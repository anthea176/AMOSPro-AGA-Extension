#!/usr/bin/env python3
"""M16 P0 host-only AGAPIC v1 format / planar CPU-model tests (no AP20)."""
import random
import struct
import hashlib
from pathlib import Path

from m16_agapic_sample import binary as sample_binary
from m16_agapic import (ABK_HEADER, BANK_NAME, CODEC_ROW_RLE, FLAG_MASK,
                       HEADER, AGAPIC, make_abk, pack_image, parse_abk,
                       parse_payload, render_cpu_model, stats, unpack_image)


def must_fail(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(f"Expected rejection: {label}")


def as_planar(pixels, width, height, depth):
    stride = ((width + 15) // 16) * 2
    planes = [bytearray(stride * height + 8) for _ in range(depth)]
    for i, val in enumerate(pixels):
        x, y = i % width, i // width
        addr = y * stride + (x // 16) * 2
        bit = 0x8000 >> (x % 16)
        for plane in range(depth):
            if val & (1 << plane):
                v = (planes[plane][addr] << 8) | planes[plane][addr + 1]
                v |= bit
                planes[plane][addr] = v >> 8
                planes[plane][addr + 1] = v & 255
    for p in planes:
        p[-8:] = bytes([0xa5]) * 8
    return planes, stride


def from_planar(planes, width, height, stride):
    out = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            bit = 0x8000 >> (x % 16)
            address = y * stride + (x // 16) * 2
            val = 0
            for depth, plane in enumerate(planes):
                v = (plane[address] << 8) | plane[address + 1]
                if v & bit:
                    val |= 1 << depth
            out[y * width + x] = val
    return bytes(out)


def reference(dst, dst_w, dst_h, src, src_w, src_h, mask, x, y, mode):
    out = bytearray(dst)
    visible = 0
    for yy in range(src_h):
        dy = yy + y
        if not 0 <= dy < dst_h:
            continue
        for xx in range(src_w):
            dx = xx + x
            if not 0 <= dx < dst_w:
                continue
            pos = yy * src_w + xx
            if mode == 1 and mask[pos] == 0:
                continue
            visible += 1
            out[dy * dst_w + dx] = src[pos]
    return bytes(out), visible


def test_roundtrip(rng):
    cases = 0
    for depth in (1, 2, 4, 8):
        for width, height in ((1, 1), (7, 5), (15, 1), (16, 8), (17, 11),
                              (31, 13), (32, 2), (63, 23), (127, 19)):
            n = width * height
            src = bytes(rng.randrange(1 << depth) for _ in range(n))
            mask = bytes((i + (i // width) * 3) % 5 != 0 for i in range(n))
            for input_mask in (None, mask):
                raw = pack_image(width, height, depth, src, input_mask)
                assert raw == pack_image(width, height, depth, src, input_mask)
                parsed = parse_payload(raw)
                assert (parsed.width, parsed.height, parsed.depth, parsed.masked) == (
                    width, height, depth, input_mask is not None)
                assert unpack_image(parsed) == (src, input_mask)
                assert len(parsed.offsets) == height + 1
                assert parsed.offsets[0] == 32 + 4 * (height + 1)
                assert parsed.offsets[-1] == len(raw)
                assert all(len(list(parsed.row_groups(y))) == (width + 15) // 16
                           for y in range(height))
                for bank in (5, 10, 65535):
                    for chip in (False, True):
                        abk = make_abk(bank, raw, chip=chip)
                        bb, flags, reread = parse_abk(abk)
                        assert (bb, flags) == (bank, 3 if chip else 1)
                        assert reread == parsed
                        assert len(abk) == len(raw) + 20
                        assert abk[12:20] == BANK_NAME
                        cases += 1
    return cases


def test_render(rng):
    cases = 0
    dst_w, dst_h = 69, 43  # odd last word to exercise right-edge mask
    for depth in (1, 2, 4, 8):
        for src_w, src_h in ((1, 1), (15, 7), (16, 8), (17, 9), (33, 17),
                             (55, 47), (89, 31)):
            source = bytes(rng.randrange(1 << depth) for _ in range(src_w * src_h))
            # Independent mask: colour 0 can be either visible or transparent.
            mask = bytes(rng.randrange(2) for _ in source)
            for masked in (False, True):
                raw = pack_image(src_w, src_h, depth, source,
                                 mask if masked else None)
                img = parse_payload(raw)
                for mode in ((0, 1) if masked else (0,)):
                    positions = ((-src_w, -src_h), (-src_w + 1, -3), (-17, -1),
                                 (-1, 0), (0, -1), (0, 0), (1, 1), (7, 9),
                                 (15, 17), (16, -8), (31, 13),
                                 (dst_w - 1, dst_h - 1), (dst_w, dst_h),
                                 (dst_w + 1, 0), (0, dst_h + 1),
                                 (dst_w - src_w, dst_h - src_h))
                    for x, y in positions:
                        bg = bytes(rng.randrange(1 << depth)
                                   for _ in range(dst_w * dst_h))
                        planes, stride = as_planar(bg, dst_w, dst_h, depth)
                        expected, count = reference(bg, dst_w, dst_h,
                                                    source, src_w, src_h,
                                                    mask, x, y, mode)
                        actual_count = render_cpu_model(img, x, y, planes,
                                                        dst_w, dst_h, mode, stride)
                        result = from_planar(planes, dst_w, dst_h, stride)
                        assert result == expected, (
                            "wrong planar pixels", depth, src_w, src_h,
                            masked, mode, x, y)
                        assert actual_count == count
                        assert all(bytes(p[-8:]) == bytes([0xa5]) * 8
                                   for p in planes), "plane canary changed"
                        cases += 1
    return cases


def test_opaque_zero_and_mask():
    # Both pixels are pen 0. A mask can distinguish them; pen 0 is not alpha.
    src = bytes((0, 0, 5, 0, 0))
    mask = bytes((1, 0, 1, 1, 0))
    img = parse_payload(pack_image(5, 1, 4, src, mask))
    bg = bytes((7, 7, 7, 7, 7))
    planes, stride = as_planar(bg, 5, 1, 4)
    assert render_cpu_model(img, 0, 0, planes, 5, 1, 1) == 3
    assert from_planar(planes, 5, 1, stride) == bytes((0, 7, 5, 0, 7))
    planes, stride = as_planar(bg, 5, 1, 4)
    assert render_cpu_model(img, 0, 0, planes, 5, 1, 0) == 5
    assert from_planar(planes, 5, 1, stride) == src
    return 2


def test_invalid():
    src = bytes(range(17))
    img = parse_payload(pack_image(17, 1, 8, src, bytes([1]) * 17))
    raw = img.raw
    must_fail(lambda: pack_image(0, 1, 8, b""), "zero width")
    must_fail(lambda: pack_image(1, 1, 9, b"\x00"), "depth 9")
    must_fail(lambda: pack_image(1, 1, 1, b"\x02"), "invalid colour index")
    must_fail(lambda: pack_image(1, 1, 1, b"\x00", b"\x02"), "invalid mask bit")
    must_fail(lambda: pack_image(2, 1, 1, b"\x00"), "short pixels")
    must_fail(lambda: pack_image(1, 1, 1, b"\x00", b""), "short mask")
    must_fail(lambda: make_abk(4, raw), "bank 4")
    must_fail(lambda: make_abk(65536, raw), "bank too large")
    must_fail(lambda: parse_abk(b"AmBk"), "truncated ABK")
    abk = make_abk(10, raw)
    mutated = bytearray(abk)
    mutated[0:4] = b"AmBK"
    must_fail(lambda: parse_abk(bytes(mutated)), "wrong external magic")
    mutated = bytearray(abk)
    mutated[6:8] = b"\x00\x07"
    must_fail(lambda: parse_abk(bytes(mutated)), "wrong external flags")
    mutated = bytearray(abk)
    mutated[8:12] = b"\x00\x00\x00\x00"
    must_fail(lambda: parse_abk(bytes(mutated)), "wrong external length")
    mutated = bytearray(abk)
    mutated[12:20] = b"BADPIC  "
    must_fail(lambda: parse_abk(bytes(mutated)), "wrong bank name")

    def bad_byte(offset, new):
        buf = bytearray(raw)
        buf[offset] = new
        must_fail(lambda: parse_payload(bytes(buf)), ("header byte", offset))
    bad_byte(0, 0)
    bad_byte(7, 2)  # version
    bad_byte(9, 2)  # illegal flag
    bad_byte(11, 2)  # unknown codec
    bad_byte(17, 9)  # depth 9
    bad_byte(19, 2)  # inconsistent group size

    def patch_long(offset, value):
        buf = bytearray(raw)
        struct.pack_into(">I", buf, offset, value)
        must_fail(lambda: parse_payload(bytes(buf)), ("header long", offset))
    patch_long(20, 0)
    patch_long(24, 0)
    patch_long(28, len(raw) + 1)
    must_fail(lambda: parse_payload(raw[:-1]), "truncated last RLE group")
    must_fail(lambda: parse_payload(raw + b"\x00"), "trailing row data")
    # Row start inside the header / row offsets not matching exact boundaries.
    buf = bytearray(raw)
    struct.pack_into(">I", buf, HEADER.size, HEADER.size)
    must_fail(lambda: parse_payload(bytes(buf)), "row starts in header")
    # Force repeat packet to overrun row width.
    buf = bytearray(raw)
    buf[img.offsets[0]] = 0xff
    must_fail(lambda: parse_payload(bytes(buf)), "repeat overrun")
    # Flip a padded bit in the last 16-pixel group (width 17).
    single = pack_image(17, 1, 8, bytes([0] * 16 + [1]))
    decoded = parse_payload(single)
    buf = bytearray(single)
    # second literal group starts after first group (16 bytes)
    second_word = decoded.offsets[0] + 1 + 16
    buf[second_word + 1] |= 1
    must_fail(lambda: parse_payload(bytes(buf)), "nonzero pad bits")
    must_fail(lambda: render_cpu_model(img, 0, 0,
              [bytearray(4)] * 8, 17, 1, 2), "bad draw mode")
    must_fail(lambda: render_cpu_model(img, 0, 0,
              [bytearray(4)] * 4, 17, 1, 0), "depth mismatch")
    must_fail(lambda: render_cpu_model(img, 0, 0,
              [bytearray(4)] * 8, 17, 1, 1, stride=3), "odd stride")
    must_fail(lambda: render_cpu_model(img, 32768, 0,
              [bytearray(4)] * 8, 17, 1, 1), "coordinate overflow")
    return 31


def test_compression():
    flat = pack_image(320, 256, 8, bytes(320 * 256))
    raw_planar = 320 * 256
    assert len(flat) < raw_planar // 10, len(flat)
    alternating = bytes((x ^ (x >> 1)) & 255 for x in range(320 * 256))
    busy = pack_image(320, 256, 8, alternating)
    assert len(busy) >= len(flat)
    assert stats(flat)["planar_bytes"] == 81920
    assert stats(flat)["packed_bytes"] == len(flat)
    return len(flat), len(busy)


def test_committed_fixture():
    """The ABK Git artifact must equal the host builder byte-for-byte."""
    fixture = Path(__file__).resolve().parents[1] / "tests/design/M16_AGAPIC_SAMPLE_BANK10.abk"
    disk = fixture.read_bytes()
    expected = sample_binary()
    assert disk == expected, "sample ABK does not match exact generator bytes"
    assert len(disk) == 1856, "AGAPIC sample ABK length changed"
    assert hashlib.sha256(disk).hexdigest() == (
        "56443d5ed29527a21d043b845e70c545402648ef35fa590943cd62818499edaf"
    ), "AGAPIC sample SHA changed"
    bank, flags, image = parse_abk(disk)
    assert (bank, flags, image.width, image.height, image.depth, image.masked) == (
        10, 1, 64, 40, 4, True)
    assert image.offsets[0] == 196 and image.offsets[-1] == len(image.raw)
    return "12f19cb352252d771b058395f8b6f654aed45764"


def main():
    rng = random.Random(0xA6A160)
    a = test_roundtrip(rng)
    b = test_render(rng)
    c = test_opaque_zero_and_mask()
    d = test_invalid()
    flat, busy = test_compression()
    fixture_blob = test_committed_fixture()
    print(f"M16 P0 host format/model PASS: {a} ABK/roundtrips, "
          f"{b} clipped planar renders, {c} index-0/mask cases, "
          f"{d} malformed/invalid cases")
    print(f"AGAPIC RLE example 320x256x8: flat {flat} B vs "
          f"raw planar 81920 B; complex sample {busy} B")
    print("Pinned ABK fixture 1856 B, Git blob", fixture_blob)
    print("No new AP20 command, no WinUAE render or measured 68000 speed.")
    print("R44 LAST_GOOD remains untouched; CPU model is not a Gate A.")


if __name__ == "__main__":
    main()
