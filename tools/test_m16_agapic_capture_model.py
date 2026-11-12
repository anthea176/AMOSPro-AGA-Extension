#!/usr/bin/env python3
"""M16 capture HOST reference regressions; NOT a native CPU/WinUAE PASS."""
from __future__ import annotations

from m16_agapic import (parse_payload, unpack_image, pack_image, parse_abk,
                        render_cpu_model)
from m16_agapic_capture_model import (
    CaptureResult, capture_payload_model, create_capture_bank_model)


def make_screen(width: int, height: int, depth: int):
    stride = ((width + 15) // 16) * 2
    planes = [bytearray(stride * height) for _ in range(depth)]
    pixels = bytearray(width * height)
    for yy in range(height):
        for xx in range(width):
            c = (xx * 5 + (yy * 7) ^ (xx >> 2)) % (1 << depth)
            pixels[yy * width + xx] = c
            for d in range(depth):
                if c & (1 << d):
                    planes[d][yy * stride + (xx >> 3)] |= 0x80 >> (xx & 7)
    return planes, bytes(pixels), stride


def selection(pixels: bytes, screen_w: int,
              x: int, y: int, width: int, height: int):
    return bytes(pixels[(y + yy) * screen_w + x + xx]
                 for yy in range(height) for xx in range(width))


def run():
    count = 0
    # Various word alignments, odd widths and colour depths.
    for depth in (1, 2, 4, 5, 8):
        sw, sh = 43, 23
        planes, original, stride = make_screen(sw, sh, depth)
        before = [bytes(p) for p in planes]
        for x, y, w, h in ((0, 0, 1, 1), (1, 2, 15, 4),
                           (15, 3, 17, 11), (0, 0, 43, 23),
                           (25, 12, 18, 11), (42, 22, 1, 1)):
            expected = selection(original, sw, x, y, w, h)
            for idx in (-1, 0, (1 << depth) - 1):
                packed = capture_payload_model(
                    planes, sw, sh, x, y, w, h, idx, stride=stride)
                image = parse_payload(packed)
                pixels, mask = unpack_image(image)
                assert (image.width, image.height, image.depth) == (w, h, depth)
                assert pixels == expected
                assert mask == (None if idx == -1 else
                                bytes(int(p != idx) for p in expected))
                assert image.masked == (idx != -1)
                assert packed == pack_image(w, h, depth, expected, mask)
                assert packed == capture_payload_model(
                    planes, sw, sh, x, y, w, h, idx, stride=stride)
                count += 1
        assert [bytes(p) for p in planes] == before

    # An empty screen and malformed geometry must never create a bank.
    planes, source, stride = make_screen(43, 23, 4)
    for args in ((-1, 0, 1, 1, -1), (0, -1, 1, 1, -1),
                 (0, 0, 0, 1, -1), (0, 0, 1, 0, -1),
                 (43, 0, 1, 1, -1), (0, 23, 1, 1, -1),
                 (42, 2, 2, 1, -1), (1, 22, 1, 2, -1),
                 (0, 0, 44, 1, -1), (0, 0, 1, 24, -1),
                 (2**32, 0, 1, 1, -1),
                 (0, 0, 1, 1, -2), (0, 0, 1, 1, 16),
                 (0, 0, 1, 1, True)):
        banks = {25: b"EXISTING AMCAF FONT", 10: b"EXISTING AGAPIC"}
        snapshot = dict(banks)
        result = create_capture_bank_model(
            banks, 11, planes, 43, 23, *args,
            stride=stride, fast_free=100000, chip_free=100000)
        assert result == CaptureResult(0, None, 0), args
        assert banks == snapshot
        count += 1

    # Bad bitmap shape, invalid depths, stride errors and malformed types.
    for bad in ([], planes[:1] * 9, planes + [bytearray()],
                [bytearray(2)] * 4, [b"\0"] * 4):
        banks = {}
        assert create_capture_bank_model(
            banks, 20, bad, 43, 23, 0, 0, 16, 8, -1,
            fast_free=100000, chip_free=100000).ok == 0
        assert not banks
        count += 1
    for badstride in (-2, 0, 1, 5, True):
        banks = {}
        assert create_capture_bank_model(
            banks, 20, planes, 43, 23, 0, 0, 16, 8, -1,
            stride=badstride, fast_free=100000, chip_free=100000).ok == 0
        assert not banks
        count += 1

    # Existing banks are NEVER replaced: font/data/any content counts.
    for bank in (5, 10, 25, 65535):
        banks = {bank: b"ORIGINAL BANK", 8: b"NEIGHBOUR"}
        original_banks = dict(banks)
        result = create_capture_bank_model(
            banks, bank, planes, 43, 23, 0, 0, 16, 8, 0,
            fast_free=100000, chip_free=100000)
        assert result.ok == 0 and banks == original_banks
        count += 1
    for bank in (0, 1, 4, -1, 65536, True):
        banks = {}
        result = create_capture_bank_model(
            banks, bank, planes, 43, 23, 0, 0, 16, 8, -1,
            fast_free=100000, chip_free=100000)
        assert result.ok == 0 and not banks
        count += 1

    # Fast preferred, Chip fallback, and out-of-memory are distinct.
    payload = capture_payload_model(
        planes, 43, 23, 15, 1, 17, 8, 0)
    needed = len(payload) + 24
    for fast, chip, status, location in (
        (needed, 0, 1, "fast"),
        (needed - 1, needed, 1, "chip"),
        (0, needed, 1, "chip"),
        (needed - 1, needed - 1, 0, None),
        (0, 0, 0, None),
    ):
        banks = {25: b"EXISTING AMCAF FONT"}
        before = dict(banks)
        result = create_capture_bank_model(
            banks, 10, planes, 43, 23, 15, 1, 17, 8, 0,
            fast_free=fast, chip_free=chip)
        assert (result.ok, result.location) == (status, location)
        assert banks[25] == before[25]
        if status:
            bank, flags, image = parse_abk(banks[10])
            assert (bank, flags, image.raw) == (10, 1, payload)
            assert result.payload_length == len(payload)
        else:
            assert banks == before
        count += 1

    # Simple round-trip from captured bank back to another planar surface.
    banks = {}
    result = create_capture_bank_model(
        banks, 11, planes, 43, 23, 13, 5, 18, 7, 0,
        fast_free=100000, chip_free=0)
    assert result.ok == 1
    _, _, image = parse_abk(banks[11])
    dst = [bytearray(stride * 23) for _ in range(4)]
    written = render_cpu_model(image, 7, 4, dst, 43, 23, 1, stride)
    assert written == sum(p != 0 for p in selection(source, 43, 13, 5, 18, 7))
    count += 1
    print(f"M16 CAPTURE HOST MODEL PASS: {count} deterministic cases")
    print("NOT native 68000 Gate A; NOT AMOS/WinUAE Gate B/C")


if __name__ == "__main__":
    run()
