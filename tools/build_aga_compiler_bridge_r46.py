#!/usr/bin/env python3
"""R46 v0.12.1-C1: reproduce the user-validated AMOS Compiler-safe library.

Historical R46 native 56-segment archive is immutable. Wrap it with the
approved AP20 Rbsr dispatcher before installing/publishing any library.
Gate C all-in-one was confirmed PASS under WinUAE (12 Nov 2026).
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from compiler_relocation import wrap_native_ap20, unpack_ap20, DISPATCH

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib"
SHA = "5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580"
CANDIDATE_SHA = "d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
CANDIDATE = ROOT / "dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
TITLE = b"AMOSPro AGA M16 R46 Compiler Gate C candidate 0.12.1-C1\0$VER: AMOSPro_AGA 0.12.1-C1\0"
assert not len(TITLE) % 2


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_ap20(data: bytes):
    if len(data) != 29288 or digest(data) != SHA:
        raise ValueError("R46 native archive has changed")
    tok, parts, _ = unpack_ap20(data)
    assert len(parts) == 56 and sum(map(len, parts)) == 27856
    assert parts[1] == b"GetP" and parts[16] == b""
    return tok, parts


def build(source: bytes) -> bytes:
    read_ap20(source)
    result = wrap_native_ap20(source, TITLE)
    if len(result) != 29964 or digest(result) != CANDIDATE_SHA:
        raise ValueError("R46 C1 promoted bytecode does not match tested candidate")
    return result


def verify_installable() -> bytes:
    native = SOURCE.read_bytes()
    data = build(native)
    assert CANDIDATE.read_bytes() == data, "immutable C1 evidence changed"
    assert (ROOT / "dist/AMOSPro_AGA.Lib").read_bytes() == data, "current is not compiler-safe C1"
    assert (ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes() == data, "LAST_GOOD is not compiler-safe C1"
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="check official copies (default)")
    args = parser.parse_args()
    data = verify_installable()
    print("R46 C1 PROMOTED Compiler-safe / Gate C integrated WinUAE PASS", len(data), digest(data))
    print("Source R46 56 segments preserved; official R46 57 entries; 50 AMOS commands")
    print("DO NOT use the historical native R46 .Lib as future official output.")


if __name__ == "__main__":
    main()
