#!/usr/bin/env python3
"""M18 CBlock host Gate A *model only*: exact pixels, 8- and 16-pixel cases.

No claim of CPU 68000 execution, physical Chip residency, actual Blitter or speed.
"""
from m18_cblock_copy_model import (
    Surface, scan_equivalence, validate, copy_cpu_bytes,
    copy_cpu_words, copy_blitter_word_model,
)
from random import Random


def main():
    rng = Random(0xCB10813)
    count = 0
    for depth in (1, 2, 4, 5, 8):
        for w, h in ((8, 8), (16, 16), (24, 16), (32, 3), (64, 48),
                     (80, 48), (128, 40), (168, 27)):
            width = 192
            height = 65
            source = Surface.make(width, height, depth, seed=depth*1000+w*13+h)
            target = Surface.make(width, height, depth, seed=depth*304+w*27+h*7)
            for sx, dx in ((0, 0), (8, 8), (8, 16), (16, 8), (16, 16),
                           (24, 32), (0, 8), (32, 24)):
                if max(sx, dx)+w > width:
                    continue
                for sy, dy in ((0, 0), (1, 5), (4, 0), (height-h, height-h)):
                    assert scan_equivalence(source, target, sx, sy, dx, dy, w, h)
                    count += 1
    # Capture/reuse/restore: source private screen -> zeroed Chip bank -> screen.
    for width in (8, 16, 24, 32, 80):
        src = Surface.make(192, 65, 8, seed=111+width)
        bank = Surface.make(width, 24, 8, seed=0)
        bank.planes = [bytearray(len(p)) for p in bank.planes]
        temp = Surface.make(192, 65, 8, seed=112+width)
        copy_blitter_word_model(src, bank, 8, 10, 0, 0, width, 24)
        for copy in (copy_cpu_bytes, copy_blitter_word_model):
            restored = temp.clone()
            copy(bank, restored, 0, 0, 16, 24, width, 24)
            oracle = temp.clone()
            from m18_cblock_copy_model import copy_pixel_oracle
            copy_pixel_oracle(src, oracle, 8, 10, 16, 24, width, 24)
            assert restored.signature() == oracle.signature()
            count += 1
    # All invalid arguments fail BEFORE any output modification.
    b = Surface.make(64, 48, 8, seed=3)
    before = b.signature()
    s = Surface.make(64, 48, 8, seed=7)
    invalid = (
        (1, 0, 0, 0, 16, 16), (0, 0, 1, 0, 16, 16),
        (0, 0, 0, 0, 15, 16), (0, 0, 0, 0, 0, 16),
        (0, 0, 0, 0, 16, 0), (0, 0, 56, 0, 16, 16),
        (0, 0, 0, 40, 16, 16), (0, -1, 0, 0, 16, 16),
        (-8, 0, 0, 0, 16, 16), (0, 0, 0, 0, 16, -1)
    )
    for vals in invalid:
        for copy in (copy_cpu_bytes,copy_blitter_word_model):
            try:copy(s, b, *vals)
            except ValueError:pass
            else:raise AssertionError((copy.__name__,vals))
            assert b.signature()==before
    for copy in (copy_cpu_bytes,copy_blitter_word_model):
        bad = s.clone();bad.chip=False
        try:copy(bad,b,0,0,0,0,16,16)
        except ValueError:pass
        else:raise AssertionError("Accepted Fast RAM")
    bad = s.clone();bad.depth=2
    try:copy_cpu_bytes(bad,b,0,0,0,0,16,16)
    except ValueError:pass
    else:raise AssertionError("Accepted depth mismatch")
    print(f"M18 CBlock host pixel model PASS: {count} copy/capture/restore comparisons; "
          f"{len(invalid)*2+3} malformed/Chip rejections. "
          "No real 68000/Blitter speed measured.")


if __name__ == '__main__':main()
