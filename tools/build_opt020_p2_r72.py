#!/usr/bin/env python3
"""OPT020/P2 R72: isolated late-rejection D3 hardening, in memory only.

R71 remains the byte-identical WinUAE Gate B PASS reference.  R70/R71
builders and their output must not change.  R72 modifies native entry 55
only via an opt-in source emitter, then relocates the three audited
inter-entry BRA/BSR links.  No library or ASC is written by this builder.
Gate B WinUAE interpreted must be repeated for R72.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from build_opt020_p2_r71 import R71_SHA, build as build_r71
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from m16_image_draw_r45_emit import ENTRY_INDEX, emit_image_draw
from native_relative_links import assert_native_links, relink_native_parts

ROOT = Path(__file__).resolve().parents[1]
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
TITLE = (b"AMOSPro AGA OPT020 P2 Image Draw R72 0.13.17 Gate A candidate\0"
         b"$VER: AMOSPro_AGA 0.13.17\0")
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    good_path = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
    good = good_path.read_bytes()
    assert sha256(good).hexdigest() == R68_SHA, "R68 LAST_GOOD changed"

    r71, previous = build_r71()
    assert sha256(r71).hexdigest() == R71_SHA and previous["size"] == 51460
    tokens, old_parts = unwrap_native_parts_v2(r71)
    old_tokens, old_entries, title = unpack_ap20(r71)
    assert tokens == old_tokens and len(old_parts) == 70 and len(old_entries) == 71
    assert len(TITLE) == len(title), "R72 changes V2 title envelope size"

    before, labels0 = emit_image_draw(accept_loaded_flags_zero=True, opt020=True)
    after, labels1 = emit_image_draw(
        accept_loaded_flags_zero=True, opt020=True, reset_failure_d3=True
    )
    assert after != before and len(after) == len(before) + 6
    assert len(before) == 2018 and old_parts[ENTRY_INDEX] == before + GETP
    assert "p2_exit" not in labels0 and "p2_exit" in labels1
    assert after.startswith(before[:14]), "P2 prologue unexpectedly changed"
    assert after.endswith(before[-12:]), "P2 epilogue unexpectedly changed"
    # Opt-in only: no legacy R46/R70/R71 source alteration.
    assert emit_image_draw(accept_loaded_flags_zero=True, opt020=True)[0] == before

    trial = list(old_parts)
    trial[ENTRY_INDEX] = after + GETP
    repaired = relink_native_parts(trial)
    assert_native_links(repaired)
    changed = {i for i, (a, b) in enumerate(zip(old_parts, repaired)) if a != b}
    assert changed == {20, 55, 57, 58}, f"Unexpected native changes: {changed}"
    assert repaired[55] == after + GETP and repaired[59] == old_parts[59], (
        "P2 emitter or validated P1e region changed beyond intended fix"
    )

    native = repack_ap20(r71, tokens, repaired, TITLE)
    output = wrap_native_ap20_v2(native, TITLE)
    assert unwrap_native_parts_v2(output) == (tokens, repaired)
    token2, entries, title2 = unpack_ap20(output)
    assert token2 == tokens and title2 == TITLE and len(entries) == 71
    assert len(entries[-1]) < 65534
    assert not inspect(parse(output))["issues"], "R72 AP20 structure failed"
    # 6 native bytes, plus 2 bytes of 4-byte-aligned AP20/HUNK padding.
    assert len(output) == len(r71) + 8, "R72 HUNK/AP20 alignment drift"
    assert good_path.read_bytes() == good, "R68 LAST_GOOD mutated"
    return output, {
        "version": "R72 v0.13.17 P2 late D3 reject hardening, Gate A only",
        "size": len(output),
        "sha256": sha256(output).hexdigest(),
        "native55_bytes": len(after),
        "native55_sha256": sha256(after).hexdigest(),
        "native_changed": sorted(changed),
        "commands": 64,
        "ap20_entries": 71,
        "gate_a": "PENDING",
        "gate_b": "NOT TESTED",
        "gate_c": "NOT TESTED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print candidate bytes for external SHA-pinned GitHub publication; never writes files")
    args = parser.parse_args()
    candidate, meta = build()
    assert candidate == build()[0], "R72 not reproducible"
    print("R72 P2 IN-MEMORY D3 REJECT CANDIDATE:", meta, flush=True)
    if args.emit_base64:
        print("R72_B64_BEGIN", flush=True)
        encoded = base64.b64encode(candidate).decode("ascii")
        for index in range(0, len(encoded), 120):
            print("R72_B64 " + encoded[index:index + 120], flush=True)
        print("R72_B64_END", flush=True)


if __name__ == "__main__":
    main()
