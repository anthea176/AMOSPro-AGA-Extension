#!/usr/bin/env python3
"""OPT020/P3 R73 v0.13.18 deterministic Fast Icon 68020 candidate.

Pure in-memory builder: pinned R72 0.13.17 is the only base, R68 LAST_GOOD
is read-only, and public tokens/AP20 ABI remain unchanged. Native entry 60
Aga F Icon and 66 Aga F Icon Capture are replaced by the separately
Musashi-tested 020 opt-in emitters. 68000 guard before any BFxxx.
Every audited native inter-entry relative branch is relinked and verified.
Do NOT install or promote until targeted Gate A passes; WinUAE Gate B
is a separate user-observed test. No AMOS Compiler before OPT020 is final.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from build_opt020_p2_r72 import build as build_r72
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from m18_ficon_ap20_emit import emit_ficon_ap20
from m18_ficon_capture_emit import emit_ficon_capture
from native_relative_links import (
    LINKS, assert_native_links, link_positions, relink_native_parts
)

ROOT = Path(__file__).resolve().parents[1]
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
R72_SHA = "fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
DRAW = 60
CAPTURE = 66
TITLE = (b"AMOSPro AGA OPT020 P3 Fast Icons R73 0.13.18 Gate A candidate\0"
         b"$VER: AMOSPro_AGA 0.13.18\0")
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    last_good_path = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
    last_good = last_good_path.read_bytes()
    assert sha256(last_good).hexdigest() == R68_SHA, "R68 protected binary modified"

    r72, meta72 = build_r72()
    assert sha256(r72).hexdigest() == R72_SHA
    assert meta72["size"] == 51468 and meta72["ap20_entries"] == 71
    tokens, parts = unwrap_native_parts_v2(r72)
    assert len(parts) == 70 and len(tokens) > 0
    old_tokens, old_entries, old_title = unpack_ap20(r72)
    assert tokens == old_tokens and len(old_entries) == 71
    assert_native_links(parts)

    old_draw, _ = emit_ficon_ap20()
    old_capture, _ = emit_ficon_capture()
    assert parts[DRAW] == old_draw + GETP, "R72 F Icon source identity changed"
    assert parts[CAPTURE] == old_capture + GETP, "R72 Capture source identity changed"

    new_draw, draw_labels = emit_ficon_ap20(opt020=True)
    new_capture, capture_labels = emit_ficon_capture(opt020=True)
    assert new_draw != old_draw and new_capture != old_capture
    assert "core" in draw_labels and "safe" in draw_labels
    assert "check_plane" in capture_labels and "row" in capture_labels
    assert len(new_draw) % 2 == len(new_capture) % 2 == 0
    assert new_draw[:4] == old_draw[:4] == bytes.fromhex("48e7efee")
    assert new_capture[:4] == old_capture[:4] == bytes.fromhex("48e7efee")
    # Every public entry keeps its standard Compiler V2 GetP suffix.
    updated = list(parts)
    updated[DRAW] = new_draw + GETP
    updated[CAPTURE] = new_capture + GETP
    repaired = relink_native_parts(updated)
    assert_native_links(repaired)
    assert relink_native_parts(repaired) == repaired, "Links not idempotent"

    changed = {i for i,(a,b) in enumerate(zip(parts,repaired)) if a != b}
    assert changed == {DRAW,CAPTURE}, f"Unexpected native entries: {sorted(changed)}"
    assert all(parts[i] == repaired[i] for i in (20,49,55,57,58,59,67,68,69))
    for edge in LINKS:
        actual,target,_ = link_positions(repaired,edge)
        assert actual == target, f"R70 regression: {edge.name}"

    native = repack_ap20(r72,tokens,repaired,TITLE)
    candidate = wrap_native_ap20_v2(native,TITLE)
    assert unwrap_native_parts_v2(candidate) == (tokens,repaired)
    tokens2, entries2, title2 = unpack_ap20(candidate)
    assert tokens2 == tokens and title2 == TITLE
    assert len(entries2) == 71 and len(entries2[-1]) < 65534
    report = inspect(parse(candidate))
    assert not report["issues"], report["issues"]
    assert len([t for t in report["tokens"] if t["name"].startswith("aga ")]) == 64
    assert_native_links(unwrap_native_parts_v2(candidate)[1])
    assert last_good_path.read_bytes() == last_good

    return candidate, dict(
        version="R73 v0.13.18 Fast Icon capture+draw 020, Gate A candidate",
        size=len(candidate),sha256=sha256(candidate).hexdigest(),
        commands=64,ap20_entries=71,changed_native=sorted(changed),
        draw_60_size=len(new_draw),capture_66_size=len(new_capture),
        gate_a="PENDING targeted CPU/ABI run",
        gate_b="NOT TESTED WinUAE",gate_c="NOT TESTED Compiler"
    )


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true",
                        help="For externally hash-verified publication after Gate A")
    args=parser.parse_args()
    candidate,info=build()
    assert candidate==build()[0],"R73 non-deterministic builder"
    print("OPT020 R73 IN-MEMORY GATE A CANDIDATE",info,flush=True)
    if args.emit_base64:
        print("R73_B64_BEGIN",flush=True)
        b64=base64.b64encode(candidate).decode("ascii")
        for at in range(0,len(b64),120):
            print("R73_B64 "+b64[at:at+120],flush=True)
        print("R73_B64_END",flush=True)

if __name__=="__main__":
    main()
