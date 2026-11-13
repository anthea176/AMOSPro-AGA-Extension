#!/usr/bin/env python3
"""M18/R60 0.13.5: ADDITIVE AGAPIC v1 atlas region, Compiler V2 candidate.

Read-only deterministic builder from historical SHA-pinned R59 builder.
Independent of the CURRENT LAST_GOOD, which now points to R60. Append only
one GetP marker and native 68000 routine, preserving all R59 public stubs.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse, token
from compiler_bridge_v2_probe import (
    DISPATCH_V2, is_v2_wrapped, unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from m18_image_region_emit import ENTRY_INDEX, GETADR_MARKER, emit_image_region
from build_m17_r59_compact_v2 import build as build_r59

ROOT = Path(__file__).resolve().parents[1]
# R59 is reconstructed via build_r59; no dependency on current LAST_GOOD.
R59_SHA = "00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d"
API = ("aga image region", 1, ENTRY_INDEX, "00,0,0,0,0,0,0,0")
TITLE = (
    b"AMOSPro AGA M18 Image Region R60 0.13.5 candidate\0"
    b"$VER: AMOSPro_AGA 0.13.5\0"
)
TITLE += bytes(len(TITLE) % 2)


def build() -> tuple[bytes, dict]:
    r59, _ = build_r59()
    assert sha256(r59).hexdigest() == R59_SHA, "historical R59 builder changed"
    assert is_v2_wrapped(r59)
    old_tokens, original = unwrap_native_parts_v2(r59)
    _, old_parts, _ = unpack_ap20(r59)
    assert len(original) == ENTRY_INDEX == 59
    assert len(old_parts) == 60
    assert old_parts[-1] == DISPATCH_V2 + b"".join(original)

    native, labels = emit_image_region()
    assert native.count(GETADR_MARKER) == 1
    assert len(native) % 2 == 0
    assert native and native[:2] == bytes.fromhex("48e7")
    assert original[-1] not in (b"", GETP) and not original[-1].endswith(GETP)
    parts = list(original)
    parts[-1] += GETP      # Marker for the NEW 8-parameter entry.
    parts.append(native)   # New public entry index 59, old indexes untouched.
    tokens = old_tokens[:-6] + token(*API) + bytes(6)
    source = repack_ap20(r59, tokens, parts, TITLE)
    binary = wrap_native_ap20_v2(source, TITLE)
    new_tokens, new_entries, new_title = unpack_ap20(binary)

    assert new_tokens == tokens and new_title == TITLE
    assert len(new_entries) == 61
    assert new_entries[-1] == DISPATCH_V2 + b"".join(parts)
    assert unwrap_native_parts_v2(binary) == (tokens, parts)
    assert parts[:58] == original[:58]
    assert parts[58] == original[58] + GETP
    assert parts[59] == native
    report = inspect(parse(binary))
    assert not report["issues"], report["issues"]
    named = [x for x in report["tokens"] if x["name"].startswith("aga ")]
    old_named = [x for x in inspect(parse(r59))["tokens"]
                 if x["name"].startswith("aga ")]
    assert len(named) == 54 and named[:-1] == old_named
    assert named[-1]["name"] == API[0]
    assert (named[-1]["function"], named[-1]["signature"]) == (API[2], API[3])
    assert any(x["index"] == ENTRY_INDEX and x["parameters"] == 8
               and x["getp"] for x in report["parameter_checks"])
    assert len(new_entries[-1]) < 65534
    return binary, {
        "version": "M18/R60 0.13.5 promoted (A/B/C + full regression)",
        "bytes": len(binary),
        "sha256": sha256(binary).hexdigest(),
        "public_commands": len(named),
        "ap20_entries": len(new_entries),
        "compiler_v2_bytes": len(new_entries[-1]),
        "new_entry_index": ENTRY_INDEX,
        "region_routine_bytes": len(native),
        "region_native_offset": sum(map(len, parts[:-1])),
        "r59_legacy_bytes": sum(map(len, original)),
        "labels": labels,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print one in-memory binary in CI logs; no file writes")
    args = parser.parse_args()
    binary, meta = build()
    assert build()[0] == binary, "R60 build is not deterministic"
    print("R60 IN-MEMORY CANDIDATE", {k: v for k, v in meta.items()
                                      if k != "labels"}, flush=True)
    if args.emit_base64:
        encoded = base64.b64encode(binary).decode("ascii")
        print("R60_BASE64_BEGIN", flush=True)
        for at in range(0, len(encoded), 128):
            print("R60_BASE64 " + encoded[at:at+128], flush=True)
        print("R60_BASE64_END", flush=True)


if __name__ == "__main__":
    main()
