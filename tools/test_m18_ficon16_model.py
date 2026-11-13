#!/usr/bin/env python3
"""M18 Fast Icons AGA HOST contract: bit-exact CPU vs word/Blitter oracle.

Source format from AmiDARK Unity SpecialFX, not a new native command.
These are Python tests, NEVER CPU 68k, Blitter hardware or speed benchmarks.
"""
from __future__ import annotations

from dataclasses import replace
from struct import pack
import random

from m18_ficon16_model import (
    HEADER, ROW, SIDE, SLOT_BYTES, build_bank, parse_bank,
    draw_cpu, draw_chip_words, FIconBank,
)
from test_m18_agapic_atlas_model import as_planar, reference, fails_clean, GUARD


def test_unity_bank_layout() -> int:
    # Exactly 4 icons, 12-byte header, 288 bytes per icon (16 x 9 x 2).
    a = bytearray(256)
    a[0] = 1
    bank = parse_bank(build_bank((bytes(a), bytes(256), bytes([255] * 256), bytes(range(256)))))
    assert bank.count == 4
    assert len(bank.raw) == 12 + 4 * 288
    assert HEADER.unpack_from(bank.raw) == (1164, 4, 16, 16, 8)
    # First icon: pixel 0 = bit 15 in bitplane 0; colour zero is masked.
    assert ROW.unpack_from(bank.icon(1)) == (0x7fff, 0x8000, 0, 0, 0, 0, 0, 0, 0)
    assert ROW.unpack_from(bank.icon(2)) == (0xffff, 0, 0, 0, 0, 0, 0, 0, 0)
    assert bank.icon(3)[:ROW.size] == ROW.pack(0, *([0xffff] * 8))
    assert len(bank.icon(4)) == SLOT_BYTES
    return 4


def test_cpu_vs_word_blitter() -> int:
    rng = random.Random(0xA6162026)
    width, height = 65, 43  # Includes non-word-aligned right edge.
    icons = tuple(bytes(0 if rng.randrange(5) == 0 else rng.randrange(1, 256)
                        for _ in range(256)) for _ in range(4))
    bank = parse_bank(build_bank(icons))
    placements = (
        (-32768, -32768), (-20, 0), (-16, 5), (-1, -1),
        (0, 0), (1, 1), (7, 5), (15, 16),
        (16, 2), (31, 29), (53, 36), (64, 0),
        (65, 43), (32767, 32767), (-1, 42),
    )
    cases = 0
    for number in range(1, 5):
        icon = icons[number-1]
        binary_mask = bytes(1 if pixel else 0 for pixel in icon)
        for x, y in placements:
            for mode in (0, 1):
                for align in ("pixel", "unity16"):
                    expected_x = x & ~15 if align == "unity16" else x
                    expected_y = y & ~15 if align == "unity16" else y
                    background = bytes(rng.randrange(256)
                                       for _ in range(width * height))
                    expected, count = reference(
                        background, width, height, icon, binary_mask, 16,
                        (0, 0, 16, 16), expected_x, expected_y, mode)
                    oracle_planes, _ = as_planar(expected, width, height, 8)
                    for memory in ("chip", "fast"):
                        cpu_planes, stride = as_planar(background, width, height, 8)
                        blt_planes, _ = as_planar(background, width, height, 8)
                        unused_planes, _ = as_planar(background, width, height, 8)
                        unused_before = [bytes(p) for p in unused_planes]
                        cpu_stats = draw_cpu(
                            bank, number, x, y, mode, cpu_planes,
                            width, height, stride, align)
                        word_stats = draw_chip_words(
                            bank, number, x, y, mode, blt_planes,
                            width, height, stride, align, memory,
                            allow_staging=(memory == "fast"))
                        assert cpu_planes == blt_planes == oracle_planes, (
                            number, x, y, align, mode, memory)
                        assert cpu_stats.visible_pixels == count
                        assert word_stats.visible_pixels == count
                        assert word_stats.staged_chip_bytes == (
                            SLOT_BYTES if memory == "fast" else 0)
                        assert [bytes(p) for p in unused_planes] == unused_before
                        assert all(p[-len(GUARD):] == GUARD for p in cpu_planes)
                        assert all(p[-len(GUARD):] == GUARD for p in blt_planes)
                        cases += 1
    return cases


def test_rejections() -> int:
    zero = bytes(256)
    icons = (zero, bytes([1]*256), bytes([255]*256), bytes(range(256)))
    raw = build_bank(icons)
    bank = parse_bank(raw)
    width, height = 65, 43
    pixels = bytes([5] * (width*height))
    planes, stride = as_planar(pixels, width, height, 8)
    checks = 0

    for desc, bad in (
        ("short", raw[:6]),
        ("truncated", raw[:-1]),
        ("extra byte", raw + b"x"),
        ("bad size", b"\0\0\0\0" + raw[4:]),
        ("bad count", raw[:4] + pack(">H", 3) + raw[6:]),
        ("bad width", raw[:6] + pack(">H", 19) + raw[8:]),
        ("bad height", raw[:8] + pack(">H", 17) + raw[10:]),
        ("unsupported ECS depth", raw[:10] + pack(">H", 6) + raw[12:]),
        ("noncanonical mask", raw[:12] + b"\0\0" + raw[14:]),
    ):
        fails_clean(lambda v=bad: parse_bank(v), planes, desc)
        checks += 1

    for desc, values in (
        ("too few slots", (zero, zero, zero)),
        ("no slots", ()),
        ("not a tuple", [zero]*4),
        ("incorrect pixel count", (zero, zero, zero, b"\0"*255)),
    ):
        fails_clean(lambda items=values: build_bank(items), planes, desc)
        checks += 1

    bad_bank = replace(bank, count=5)
    for desc, action in (
        ("id zero", lambda: draw_cpu(bank, 0, 0, 0, 0, planes, width, height)),
        ("id above count", lambda: draw_cpu(bank, 5, 0, 0, 0, planes, width, height)),
        ("id boolean", lambda: draw_cpu(bank, True, 0, 0, 0, planes, width, height)),
        ("wrong bank metadata", lambda: draw_cpu(bad_bank, 1, 0, 0, 0, planes, width, height)),
        ("X outside int16", lambda: draw_cpu(bank, 1, 32768, 0, 0, planes, width, height)),
        ("Y outside int16", lambda: draw_cpu(bank, 1, 0, -32769, 0, planes, width, height)),
        ("unsupported mode", lambda: draw_cpu(bank, 1, 0, 0, 2, planes, width, height)),
        ("unsupported alignment", lambda: draw_cpu(bank, 1, 0, 0, 0, planes, width, height, alignment="unknown")),
        ("wrong planes", lambda: draw_cpu(bank, 1, 0, 0, 0, planes[:-1], width, height)),
        ("too short stride", lambda: draw_cpu(bank, 1, 0, 0, 0, planes, width, height, stride=2)),
        ("invalid width", lambda: draw_cpu(bank, 1, 0, 0, 0, planes, 0, height)),
        ("bad memory", lambda: draw_chip_words(bank, 1, 0, 0, 0, planes, width, height, source_memory="other")),
        ("Fast without staging", lambda: draw_chip_words(bank, 1, 0, 0, 0, planes, width, height, source_memory="fast")),
        ("Fast bad staging", lambda: draw_chip_words(bank, 1, 0, 0, 0, planes, width, height, source_memory="fast", allow_staging=1)),
        ("bad Blitter id", lambda: draw_chip_words(bank, 0, 0, 0, 0, planes, width, height)),
    ):
        fails_clean(action, planes, desc)
        checks += 1
    return checks


def main() -> None:
    layout = test_unity_bank_layout()
    pixels = test_cpu_vs_word_blitter()
    rejected = test_rejections()
    assert (layout, pixels, rejected) == (4, 480, 28), (
        layout, pixels, rejected)
    print("M18 F ICON 16 HOST P1 PASS: 4 binary layout checkpoints,",
          pixels, "CPU vs word/Blitter-semantic comparisons,",
          rejected, "refusals without writes")
    print("16x16, 8 bitplanes, mask=colour-zero, pixel/unity16 alignment, "
          "negative-edge clipping, immutable second back buffer: PASS")
    print("HOST ONLY: no native 68000 code, real Blitter, timing data, "
          "AP20 command or WinUAE result")


if __name__ == "__main__":
    main()
