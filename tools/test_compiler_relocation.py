#!/usr/bin/env python3
"""Regression: promoted R46 must stay Compiler-safe, preserving future build path.

The native/unwrapped 56-segment archive is historical only and may NEVER be
published as dist/AMOSPro_AGA.Lib or LAST_GOOD after the C1 promotion.
"""
import hashlib
from pathlib import Path
from struct import pack

from audit_ap20 import parse, inspect
from build_aga_current import build, C1_ARCHIVE, LAST_GOOD, CURRENT, HISTORICAL_RAW
from active_library import verify_active
from compiler_relocation import (
    unpack_ap20, repack_ap20, is_compiler_wrapped,
    wrap_native_ap20, unwrap_native_parts, native_from_promoted, DISPATCH
)

ROOT=Path(__file__).resolve().parents[1]


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected fail-closed AP20 relocation error")


def main():
    raw = HISTORICAL_RAW.read_bytes()
    official, meta = build()
    assert official == C1_ARCHIVE.read_bytes()  # frozen C1, not moving LAST_GOOD
    verify_active(ROOT)
    assert hashlib.sha256(official).hexdigest() == "d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
    assert is_compiler_wrapped(official) and not is_compiler_wrapped(raw)
    tokens, original, old_title = unpack_ap20(raw)
    promoted_tokens, promoted_parts, promoted_title = unpack_ap20(official)
    assert len(promoted_parts) == len(original)+1 == 57
    assert promoted_parts[-1] == DISPATCH + b"".join(original)
    assert len(promoted_parts[-1]) == 27888 < 32768
    assert tokens == promoted_tokens
    assert unwrap_native_parts(official) == (tokens, original)
    assert native_from_promoted(official, old_title) == raw
    assert wrap_native_ap20(raw, promoted_title) == official
    assert inspect(parse(raw))["tokens"] == inspect(parse(official))["tokens"]
    assert not inspect(parse(official))["issues"]
    assert len([v for v in inspect(parse(official))["tokens"] if v["name"].startswith("aga ")]) == 50
    checks = inspect(parse(official))["parameter_checks"]
    assert checks and all(x["getp"] for x in checks)
    # Public example uses clean filenames, while the exact historically
    # compiled R46 C1 source stays immutable in tests/passed and the ZIP.
    historical = (ROOT/"tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc").read_bytes()
    public = (ROOT/"examples/compiler_all_in_one/COMPILER_ALL_IN_ONE.asc").read_bytes()
    assert public == historical.replace(
        b"M16_AGAPIC_SAMPLE_BANK10.abk", b"AGAPIC_SAMPLE_BANK10.abk")

    # Simulate R47: future source is derived from the *promoted* C1,
    # changed as native segments, then wrapped again. No stale bridge index.
    parts = list(original)
    parts[-1] += b"GetP"
    parts.append(b"\x4e\x75")
    native_future = repack_ap20(raw, tokens, parts, old_title)
    title_future = b"AMOSPro AGA future compiler-safe build\0$VER: AMOSPro_AGA 0.12.2\0"
    title_future += bytes(len(title_future)%2)
    future = wrap_native_ap20(native_future,title_future)
    future_tokens, future_segments, _ = unpack_ap20(future)
    assert len(future_segments) == 58 and future_segments[-1].startswith(DISPATCH)
    assert unwrap_native_parts(future) == (tokens, parts)
    assert future_tokens == tokens and future_segments[-1][32:] == b"".join(parts)

    # Never accept accidental double wrapping or silent overflow.
    rejects(lambda: wrap_native_ap20(official,promoted_title))
    rejects(lambda: unwrap_native_parts(raw))
    overflow_native = repack_ap20(raw,tokens,original+[b"\x4e\x71"*2500],old_title)
    rejects(lambda: wrap_native_ap20(overflow_native,promoted_title))
    broken = bytearray(official)
    _, stubs, _ = unpack_ap20(official)
    entry_len = sum(len(x) for x in stubs[:3])
    header = 54 + 2*len(stubs) + len(tokens)
    broken[header+entry_len+4] ^= 1  # mutate inline offset of AP20 entry 3
    rejects(lambda: unwrap_native_parts(bytes(broken)))
    print("PROMOTED R46 Compiler-safe PASS: SHA, 50 tokens, 57 AP20 entries, GetP, bytecode")
    print("FUTURE BUILD PATH PASS: unwrap current -> edit native -> wrap future (58 entries)")
    print("FAIL CLOSED PASS: double-wrap, 32-KiB overflow, unwrapped and corrupted stubs")
    print("Gate C integrated user WinUAE PASS already recorded; this is a host-only regression.")


if __name__ == "__main__":
    main()
