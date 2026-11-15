#!/usr/bin/env python3
"""Generate the deterministic M19 P0 AMOS DATA ABK example (no native API)."""
from __future__ import annotations
from pathlib import Path
from m19_agabob_abk import BobBank, BobImage


def build_fixture() -> bytes:
    def pattern(w: int, h: int, d: int) -> bytes:
        return bytes((x * 11 + y * 7 + (x ^ y)) % (1 << d)
                     for y in range(h) for x in range(w))
    bank = BobBank(10)
    bank.put(1, BobImage.from_pixels(31, 19, 4, pattern(31, 19, 4)))
    bank.put(2, BobImage.from_pixels(37, 20, 8, pattern(37, 20, 8)))
    bank.put(3, BobImage.from_pixels(1, 1, 1, b'\0'))
    bank.make_mask(1, 0)
    bank.make_mask(2, 27)
    return bank.to_abk()


if __name__ == '__main__':
    output = Path('M19_BOBS_HERO_BANK10.abk')
    output.write_bytes(build_fixture())
    print(f'M19 P0 fixture: {output} ({output.stat().st_size} bytes)')
