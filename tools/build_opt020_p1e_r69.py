#!/usr/bin/env python3
"""OPT020/P1e R69 0.13.14 deterministic *in-memory* AP20 V2 builder.

Replace ONLY the already-public Aga Image Region R60 entry in SHA-pinned
R68 LAST_GOOD. The API/tokens, all other native entries, and Compiler V2
relocation contract are unchanged. No file is written by this builder.
Release gates B/C and physical speed are NOT claimed.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from compiler_bridge_v2_probe import (
    DISPATCH_V2, unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from m18_image_region_emit import GETADR_MARKER, emit_image_region

ROOT = Path(__file__).resolve().parents[1]
R68_SHA = "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
IMAGE_REGION_INDEX = 59
TITLE = (b"AMOSPro AGA OPT020 Image Region R69 0.13.14 Gate A candidate\0"
         b"$VER: AMOSPro_AGA 0.13.14\0")
TITLE += bytes(len(TITLE) % 2)


def build():
    protected = (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(protected).hexdigest() == R68_SHA, "R68 LAST_GOOD changed"
    old_tokens, old = unwrap_native_parts_v2(protected)
    old_table, installed, _title = unpack_ap20(protected)
    assert old_tokens == old_table
    assert len(old) == 70 and len(installed) == 71
    old_region, _ = emit_image_region()
    native, labels = emit_image_region(opt020=True)
    assert old[IMAGE_REGION_INDEX] == old_region + GETP
    assert len(old_region) == 2012 and len(native) % 2 == 0
    assert native.count(GETADR_MARKER) == 1
    assert {"safe", "decode_rows", "paint_group", "p1e_full_16",
            "p1e_fragment", "p1e_clip_x", "reject", "success"} <= set(labels)

    parts = list(old)
    parts[IMAGE_REGION_INDEX] = native + GETP
    source = repack_ap20(protected, old_tokens, parts, TITLE)
    binary = wrap_native_ap20_v2(source, TITLE)
    tokens, wrapped, title = unpack_ap20(binary)
    assert title == TITLE and tokens == old_tokens
    assert len(wrapped) == len(installed) == 71
    assert wrapped[-1] == DISPATCH_V2 + b"".join(parts)
    assert len(wrapped[-1]) <= 65534
    assert unwrap_native_parts_v2(binary) == (tokens, parts)
    assert all(x == y for i, (x, y) in enumerate(zip(parts, old))
               if i != IMAGE_REGION_INDEX), "unrelated native entry changed"
    assert len(parts[IMAGE_REGION_INDEX]) == len(native) + len(GETP)

    report = inspect(parse(binary))
    old_report = inspect(parse(protected))
    assert not report["issues"], report["issues"]
    assert report["tokens"] == old_report["tokens"], "public API changed"
    assert len([t for t in report["tokens"] if t["name"].startswith("aga ")]) == 64
    assert any(p["index"] == IMAGE_REGION_INDEX and p["parameters"] == 8
               and p["getp"] for p in report["parameter_checks"])
    assert sha256((ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()).hexdigest() == R68_SHA
    return binary, {
        "version": "R69 0.13.14 OPT020/P1e Gate A candidate only",
        "size": len(binary),
        "sha256": sha256(binary).hexdigest(),
        "native_region_bytes": len(native),
        "native_region_sha256": sha256(native).hexdigest(),
        "native_region_index": IMAGE_REGION_INDEX,
        "ap20_entries": len(wrapped),
        "compiler_v2_bytes": len(wrapped[-1]),
        "commands": 64,
    }


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--emit-base64", action="store_true",
                      help="Print memory-only bytes for checked promotion to the ONE dist path")
    parsed = args.parse_args()
    candidate, info = build()
    assert build()[0] == candidate, "nondeterministic P1e builder"
    print("OPT020/P1e R69 DETERMINISTIC IN-MEMORY CANDIDATE", info, flush=True)
    if parsed.emit_base64:
        encoded = base64.b64encode(candidate).decode("ascii")
        print("OPT020_P1E_CANDIDATE_B64_BEGIN", flush=True)
        for i in range(0, len(encoded), 120):
            print("OPT020_P1E_CANDIDATE_B64 " + encoded[i:i+120], flush=True)
        print("OPT020_P1E_CANDIDATE_B64_END", flush=True)
