#!/usr/bin/env python3
"""M17/R59 v0.13.4: compact Compiler V2 candidate; R58's 40K test padding removed.

Build exclusively from byte-verified R57 native code, preserving 59 native
parts and all 53 public tokens. Only the V2 dispatcher differs; never modify
LAST_GOOD. By default read-only; --emit-base64 prints the single candidate.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
from audit_ap20 import inspect, parse
from build_m17_r57_rastport import build as build_r57
from compiler_bridge_v2_probe import (
    DISPATCH_V2, is_v2_wrapped, unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import repack_ap20, unpack_ap20, unwrap_native_parts

R57_SHA = "aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0"
R59_TITLE = (
    b"AMOSPro AGA M17 Compact V2 R59 0.13.4 candidate\0"
    b"$VER: AMOSPro_AGA 0.13.4\0"
)
R59_TITLE += bytes(len(R59_TITLE) & 1)


def build() -> tuple[bytes, dict]:
    r57, _ = build_r57()
    assert sha256(r57).hexdigest() == R57_SHA, "R57 native provenance changed"
    tokens, native_parts = unwrap_native_parts(r57)
    old_tokens, old_entries, _ = unpack_ap20(r57)
    assert tokens == old_tokens and len(native_parts) == 59
    assert sum(map(len, native_parts)) == 30748
    native = repack_ap20(r57, tokens, native_parts, R59_TITLE)
    candidate = wrap_native_ap20_v2(native, R59_TITLE)
    assert is_v2_wrapped(candidate), "Candidate must use V2 Compiler bridge"
    new_tokens, entries, title = unpack_ap20(candidate)
    assert new_tokens == tokens and title == R59_TITLE, "Public token ABI changed"
    assert len(entries) == len(old_entries) == 60
    assert entries[:-1] == old_entries[:-1], "R57 public Compiler stubs changed"
    assert entries[-1] == DISPATCH_V2 + b"".join(native_parts)
    assert entries[-1][34:] == old_entries[-1][32:], "Native R57 code changed"
    assert len(entries[-1]) == 30782, "Unexpected padding or code added"
    assert unwrap_native_parts_v2(candidate) == (tokens, native_parts)
    report = inspect(parse(candidate))
    assert not report["issues"], report["issues"]
    names = [x["name"] for x in report["tokens"] if x["name"].startswith("aga ")]
    assert len(names) == 53 and "aga probe" in names
    return candidate, {
        "version": "M17/R59 0.13.4 compact V2 (Gate A only; B/C not tested)",
        "size": len(candidate),
        "sha256": sha256(candidate).hexdigest(),
        "native_bytes": sum(map(len, native_parts)),
        "compiler_unit_bytes": len(entries[-1]),
        "public_commands": len(names),
        "ap20_entries": len(entries),
        "padding_bytes": 0,
        "dispatcher_bytes": len(DISPATCH_V2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true",
                        help="Print one candidate in CI logs; no file writes")
    args = parser.parse_args()
    binary, details = build()
    assert build()[0] == binary, "Non-deterministic R59 build"
    print("R59 COMPACT V2 DETERMINISTIC CANDIDATE", details, flush=True)
    if args.emit_base64:
        payload = base64.b64encode(binary).decode("ascii")
        print("R59_BASE64_BEGIN", flush=True)
        for offset in range(0, len(payload), 128):
            print("R59_BASE64 " + payload[offset:offset + 128], flush=True)
        print("R59_BASE64_END", flush=True)


if __name__ == "__main__":
    main()
