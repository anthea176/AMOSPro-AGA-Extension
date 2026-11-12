#!/usr/bin/env python3
"""M17/R58 0.13.3: single installable AP20 candidate, V2 long-range Compiler probe.

Source is rebuilt deterministically from the verified R57 builder (and R54
LAST_GOOD). All 59 R57 native entries and 52 ordinary public commands stay
byte-for-byte identical. Existing 'Aga Probe' is redirected to a private
diagnostic implementation at native offset 40000, solely to prove the V2
unsigned dispatch path in AMOS interpreted and Compiler/WinUAE.

No file output by default; --emit-base64 only prints the one candidate so it
can replace dist/AMOSPro_AGA.Lib. Never alter LAST_GOOD or historical libs.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse
from build_m17_r57_rastport import build as build_r57
from compiler_bridge_v2_probe import (
    DISPATCH_V2, is_v2_wrapped, unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import repack_ap20, unpack_ap20, unwrap_native_parts

R57_SHA = "aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0"
FAR_NATIVE_OFFSET = 40000
FAR_ENTRY_INDEX = 60
BRIDGE_ENTRY_INDEX = 61
R58_TITLE = (
    b"AMOSPro AGA M17 Compiler Bridge R58 0.13.3 candidate\0"
    b"$VER: AMOSPro_AGA 0.13.3\0"
)
R58_TITLE += bytes(len(R58_TITLE) & 1)
# Diagnostic 'Aga Probe' remains an instruction, not a new public API.
# The marker is checked by native CPU/ABI tests (AMOS ignores D3 here).
FAR_PROBE = bytes.fromhex("766374004e75")  # D3=99, D2=0, RTS.
assert FAR_ENTRY_INDEX == 60 and len(FAR_PROBE) == 6


def build() -> tuple[bytes, dict]:
    r57, _meta = build_r57()
    if sha256(r57).hexdigest() != R57_SHA:
        raise AssertionError("R57 source not SHA-pinned")
    old_tokens, old_parts = unwrap_native_parts(r57)
    if len(old_parts) != 59 or sum(map(len, old_parts)) != 30748:
        raise AssertionError("R57 native shape changed")
    original_rows = inspect(parse(r57))["tokens"]
    probes = [t for t in original_rows if t["name"] == "aga probe"]
    if len(probes) != 1 or probes[0]["instruction"] != 3 or probes[0]["function"] != 1:
        raise AssertionError("Original Aga Probe ABI changed")
    if probes[0]["signature"] != "I":
        raise AssertionError("Original Aga Probe must remain an instruction")
    patched_tokens = bytearray(old_tokens)
    patched_tokens[probes[0]["offset"]:probes[0]["offset"]+2] = pack(">H", FAR_ENTRY_INDEX)
    tokens = bytes(patched_tokens)
    padding_size = FAR_NATIVE_OFFSET - sum(map(len, old_parts))
    if padding_size <= 0 or padding_size & 1:
        raise AssertionError("invalid 40K alignment/padding")
    padding = bytes(padding_size)  # unreachable dead data, not NOP execution
    parts = old_parts + [padding, FAR_PROBE]
    if len(parts) != BRIDGE_ENTRY_INDEX:
        raise AssertionError("bridge position drift")
    native = repack_ap20(r57, tokens, parts, R58_TITLE)
    candidate = wrap_native_ap20_v2(native, R58_TITLE)
    if not is_v2_wrapped(candidate):
        raise AssertionError("wrong Compiler bridge")
    wrapped_tokens, wrapped_entries, title = unpack_ap20(candidate)
    if wrapped_tokens != tokens or title != R58_TITLE or len(wrapped_entries) != 62:
        raise AssertionError("R58 AP20 mismatch")
    if wrapped_entries[-1] != DISPATCH_V2 + b"".join(parts):
        raise AssertionError("R58 native code unexpectedly altered")
    if unpack_from(">H", wrapped_entries[FAR_ENTRY_INDEX], 2)[0] != BRIDGE_ENTRY_INDEX:
        raise AssertionError("far probe points to wrong dispatcher")
    if unpack_from(">H", wrapped_entries[FAR_ENTRY_INDEX], 4)[0] != FAR_NATIVE_OFFSET:
        raise AssertionError("far probe offset is not 40000")
    for idx, part in enumerate(old_parts):
        if wrapped_entries[-1][len(DISPATCH_V2)+sum(map(len, old_parts[:idx])):
                               len(DISPATCH_V2)+sum(map(len, old_parts[:idx+1]))] != part:
            raise AssertionError(f"R57 native code changed at {idx}")
    if unwrap_native_parts_v2(candidate) != (tokens, parts):
        raise AssertionError("V2 reverse link not byte-exact")
    report = inspect(parse(candidate))
    if report["issues"]:
        raise AssertionError(f"AP20 errors: {report['issues']}")
    names = [t["name"] for t in report["tokens"] if t["name"].startswith("aga ")]
    if len(names) != 53 or "aga probe" not in names:
        raise AssertionError("R58 must preserve all 53 public token names")
    info = {
        "version": "M17/R58 0.13.3 (V2 compiler candidate, B/C pending)",
        "sha256": sha256(candidate).hexdigest(),
        "size": len(candidate),
        "native_bytes": sum(map(len, parts)),
        "compiler_unit_bytes": len(wrapped_entries[-1]),
        "public_commands": len(names),
        "ap20_entries": len(wrapped_entries),
        "far_probe_offset": FAR_NATIVE_OFFSET,
        "far_probe_index": FAR_ENTRY_INDEX,
        "dispatcher_index": BRIDGE_ENTRY_INDEX,
        "zero_padding_bytes": padding_size,
    }
    return candidate, info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64", action="store_true", help="one single installable candidate as CI log data")
    args = parser.parse_args()
    binary, details = build()
    assert build()[0] == binary, "non-deterministic R58"
    print("R58 DETERMINISTIC V2 CANDIDATE", details, flush=True)
    if args.emit_base64:
        payload = base64.b64encode(binary).decode("ascii")
        print("R58_BASE64_BEGIN", flush=True)
        for offset in range(0, len(payload), 128):
            print("R58_BASE64 "+payload[offset:offset+128], flush=True)
        print("R58_BASE64_END", flush=True)


if __name__ == "__main__":
    main()
