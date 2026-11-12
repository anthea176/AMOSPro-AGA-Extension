#!/usr/bin/env python3
"""Deterministic 64x40x4 AGAPIC sample: independent mask and visible pen 0.

Host-format preview ONLY; it cannot yet be drawn through R44 AP20.
With --emit-base64 the CI log can supply the exact binary Git blob.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path

from m16_agapic import make_abk, pack_image, parse_abk, stats, unpack_image

WIDTH = 64
HEIGHT = 40
DEPTH = 4
BANK_NO = 10


def sample() -> tuple[bytes, bytes, bytes]:
    pixels = bytes(((x // 4 + 3 * (y // 5)) % 16)
                   for y in range(HEIGHT) for x in range(WIDTH))
    mask = bytes(int((x - 32) ** 2 + (y - 20) ** 2 <= 18 ** 2 and
                     ((x + 2 * y) % 13 != 0))
                 for y in range(HEIGHT) for x in range(WIDTH))
    assert any(p == 0 and m == 1 for p, m in zip(pixels, mask))
    assert any(p == 0 and m == 0 for p, m in zip(pixels, mask))
    payload = pack_image(WIDTH, HEIGHT, DEPTH, pixels, mask)
    abk = make_abk(BANK_NO, payload)
    _, _, image = parse_abk(abk)
    assert unpack_image(image) == (pixels, mask)
    return payload, pixels, mask


def binary() -> bytes:
    payload, _, _ = sample()
    return make_abk(BANK_NO, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="optional generated ABK target")
    parser.add_argument("--emit-base64", action="store_true",
                        help="print exact ABK bytes for source-controlled publication")
    args = parser.parse_args()
    payload, _, _ = sample()
    abk = make_abk(BANK_NO, payload)
    s = stats(payload)
    print(f"M16 P0 sample bank={BANK_NO} {WIDTH}x{HEIGHT}x{DEPTH} "
          f"{s['mode']} inner_bytes={len(payload)} "
          f"ABK_bytes={len(abk)} SHA256={hashlib.sha256(abk).hexdigest()}")
    if args.write is not None:
        args.write.write_bytes(abk)
        print("Wrote", args.write)
    if args.emit_base64:
        text = base64.b64encode(abk).decode("ascii")
        print("M16_SAMPLE_BASE64_BEGIN")
        for i in range(0, len(text), 76):
            print(text[i:i + 76])
        print("M16_SAMPLE_BASE64_END")
    print("Host-format checks only, WinUAE/AMOS Load NOT TESTED.")


if __name__ == "__main__":
    main()
