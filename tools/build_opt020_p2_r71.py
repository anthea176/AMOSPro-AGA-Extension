#!/usr/bin/env python3
"""R71 v0.13.16: in-memory repair of the three R70 AP20 relative links.

Historical R70 remains byte-for-byte reproducible and banned as an active
library. Rebuild R70 from pinned R69/R68 sources, repair only native entries
20/57/58, rewrap as one Compiler-safe V2 monolith. No file is written.
R71 is Gate A candidate ONLY; real WinUAE interpreted Gate B is pending.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from build_opt020_p2_r70 import build as build_r70
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import repack_ap20, unpack_ap20
from native_relative_links import LINKS, assert_native_links, relink_native_parts

ROOT = Path(__file__).resolve().parents[1]
R70_SHA = "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
R71_SHA = "1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0"
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
ALLOWED_CHANGED = {20, 57, 58}
TITLE = (b"AMOSPro AGA OPT020 P2 Image Draw R71 0.13.16 Gate A candidate\0"
         b"$VER: AMOSPro_AGA 0.13.16\0")
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    from build_m18_r68_cblock import build as build_r68
    protected, _ = build_r68()
    assert sha256(protected).hexdigest() == R68_SHA, "Historical R68 builder changed"
    defective, old_meta = build_r70()
    assert sha256(defective).hexdigest() == R70_SHA
    tokens, old_parts = unwrap_native_parts_v2(defective)
    _t, _entries, old_title = unpack_ap20(defective)
    assert old_meta["size"] == 51460 and len(old_parts) == 70
    assert len(TITLE) == len(old_title), "R71 title must retain R70 envelope length"

    # R70 must actually contain the three documented broken branches.
    for link in LINKS:
        try:
            assert_native_links(old_parts)
        except AssertionError:
            break
    else:
        raise AssertionError("Historical R70 unexpectedly passes relocation gate")

    parts = relink_native_parts(old_parts)
    assert {i for i, (a, b) in enumerate(zip(old_parts, parts)) if a != b} == ALLOWED_CHANGED
    assert parts[55] == old_parts[55] and parts[59] == old_parts[59], (
        "P2 image painter or P1e region was changed by the relocation repair"
    )
    for link in LINKS:
        src = link.source_entry
        before, after = old_parts[src], parts[src]
        assert before[:link.source_offset + 2] == after[:link.source_offset + 2]
        assert before[link.source_offset + 4:] == after[link.source_offset + 4:]

    native = repack_ap20(defective, tokens, parts, TITLE)
    candidate = wrap_native_ap20_v2(native, TITLE)
    assert len(candidate) == len(defective) == 51460
    assert sha256(candidate).hexdigest() == R71_SHA, "R71 deterministic SHA drift"
    assert unwrap_native_parts_v2(candidate) == (tokens, parts)
    tt, entries, title = unpack_ap20(candidate)
    assert title == TITLE and tt == tokens and len(entries) == 71
    assert len(entries[-1]) == old_meta["compiler_v2_bytes"]
    assert not inspect(parse(candidate))["issues"]
    assert build_r68()[0] == protected, "Historical R68 builder changed during R71 build"
    return candidate, {
        "version": "R71 v0.13.16 OPT020/P2 relocation repair Gate A only",
        "size": len(candidate), "sha256": R71_SHA,
        "ap20_entries": len(entries), "commands": 64,
        "native_patches": [link.name for link in LINKS],
        "gate_a": "STRUCTURAL CANDIDATE", "gate_b": "NOT TESTED",
        "gate_c": "NOT TESTED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true")
    args = parser.parse_args()
    candidate, meta = build()
    assert build()[0] == candidate, "R71 not deterministic"
    print("R71 P2 BRANCH RELOCATION CANDIDATE IN MEMORY:", meta, flush=True)
    if args.emit_base64:
        print("R71_BASE64_BEGIN")
        print(base64.b64encode(candidate).decode("ascii"))
        print("R71_BASE64_END")
