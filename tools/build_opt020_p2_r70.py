#!/usr/bin/env python3
"""OPT020/P2 R70 v0.13.15 in-memory-only AP20 V2 candidate builder.

Reconstruct audited R69 P1e from R68 LAST_GOOD, replace *only* index 55
(Aga Image Draw) with the R46 prevalidation + P1e native CPU020 painter.
Every other AP20 unit and the public 64-command ABI are unchanged.
No file is written; this is NOT a WinUAE/Compiler Gate B/C.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from build_opt020_p1e_r69 import build as build_r69, R68_SHA
from m16_image_draw_r45_emit import emit_image_draw, ENTRY_INDEX as DRAW_INDEX
from m18_image_region_emit import emit_image_region, ENTRY_INDEX as REGION_INDEX

ROOT = Path(__file__).resolve().parents[1]
R69_SHA = "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
DRAW_NATIVE_SHA = "22de5190666ce2dce79a54da20ac0abe7e0148ff971f2551035d67f8db645a5e"
TITLE = (b"AMOSPro AGA OPT020 P2 Image Draw R70 0.13.15 Gate A candidate\0"
         b"$VER: AMOSPro_AGA 0.13.15\0")
if len(TITLE) % 2:
    TITLE += b"\0"


def build():
    from build_m18_r68_cblock import build as build_r68
    protected, _ = build_r68()  # Immutable historical source, never the moving LAST_GOOD.
    assert sha256(protected).hexdigest() == R68_SHA, "Historical R68 builder changed"
    r69, prev_meta = build_r69()
    assert sha256(r69).hexdigest() == R69_SHA and prev_meta["size"] == 51240
    old_tokens, old_parts = unwrap_native_parts_v2(r69)
    assert len(old_parts) == 70 and len(old_tokens) > 500
    legacy, _ = emit_image_draw(accept_loaded_flags_zero=True)
    newer, labels = emit_image_draw(accept_loaded_flags_zero=True, opt020=True)
    region, _ = emit_image_region(opt020=True)
    assert old_parts[DRAW_INDEX] == legacy + GETP, "R46 source changed"
    assert old_parts[REGION_INDEX] == region + GETP, "R69 P1e Region changed"
    assert len(newer) == 2018 and sha256(newer).hexdigest() == DRAW_NATIVE_SHA
    assert {"p1e_clip_x", "p1e_full_16", "p1e_fragment",
            "decode_rows", "paint_group", "safe"} <= set(labels)
    trial = list(old_parts)
    trial[DRAW_INDEX] = newer + GETP
    unwrapped = repack_ap20(r69, old_tokens, trial, TITLE)
    final = wrap_native_ap20_v2(unwrapped, TITLE)
    tt, entries, title = unpack_ap20(final)
    assert title == TITLE and tt == old_tokens and len(entries) == 71
    assert unwrap_native_parts_v2(final) == (old_tokens, trial)
    assert all(a == b for i, (a, b) in enumerate(zip(old_parts, trial))
               if i != DRAW_INDEX), "Unexpected non-P2 native changes"
    assert len(entries[-1]) < 65534
    report = inspect(parse(final))
    before = inspect(parse(r69))
    assert not report["issues"], report["issues"]
    assert report["tokens"] == before["tokens"], "Public API changed"
    assert len([t for t in report["tokens"] if t["name"].startswith("aga ")]) == 64
    assert any(p["index"] == DRAW_INDEX and p["parameters"] == 5 and p["getp"]
               for p in report["parameter_checks"])
    assert any(p["index"] == REGION_INDEX and p["parameters"] == 8 and p["getp"]
               for p in report["parameter_checks"])
    assert build_r68()[0] == protected, "Historical R68 source changed in build"
    return final, {
        "version": "R70 v0.13.15 OPT020/P1e+P2 Gate A candidate only",
        "size": len(final),
        "sha256": sha256(final).hexdigest(),
        "image_draw_native_bytes": len(newer),
        "image_draw_native_sha256": sha256(newer).hexdigest(),
        "changed_native_entry": DRAW_INDEX,
        "retained_region_native_entry": REGION_INDEX,
        "ap20_entries": len(entries),
        "compiler_v2_bytes": len(entries[-1]),
        "commands": 64,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-base64", action="store_true",
                    help="Emit exact candidate bytes only for separately audited promotion")
    args = ap.parse_args()
    candidate, info = build()
    assert build()[0] == candidate, "Non deterministic R70"
    print("OPT020/P2 R70 DETERMINISTIC IN-MEMORY V2 CANDIDATE", info, flush=True)
    if args.emit_base64:
        s = base64.b64encode(candidate).decode("ascii")
        print("OPT020_P2_R70_B64_BEGIN", flush=True)
        for i in range(0, len(s), 120):
            print("OPT020_P2_R70_B64 " + s[i:i+120], flush=True)
        print("OPT020_P2_R70_B64_END", flush=True)
