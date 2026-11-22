#!/usr/bin/env python3
"""AGSP v1 host-only tests: no native extension, WinUAE or Compiler gate."""
from __future__ import annotations

from struct import pack_into
import unittest

from m19_s1_agsp_bank import (
    ABK, ENTRY, HEADER, MAGIC, NAME, PALETTE_BYTES, SpriteImage,
    delete_image, empty_bank, make_abk, parse_abk, parse_payload,
    put_capture, s0_interleaved_image, set_hotspot,
)


def cmap256() -> bytes:
    cmap = bytearray(256 * 3)
    for pen, rgb in ((0, (1, 2, 3)), (7, (8, 9, 10)),
                     (25, (255, 80, 56)), (67, (237, 198, 66)),
                     (128, (61, 199, 182)), (255, (0, 0, 0))):
        cmap[pen * 3:pen * 3 + 3] = bytes(rgb)
    return bytes(cmap)


def simple_screen() -> tuple[bytes, bytes]:
    screen = bytearray(32 * 16)
    screen[0:4] = bytes([0, 25, 67, 128])
    for y in range(1, 16):
        for x in range(16):
            screen[y * 32 + x] = (0, 25, 67, 128)[(x + y) % 4]
    return bytes(screen), cmap256()


def capture(screen: bytes, cmap: bytes, *, width: int = 16,
            height: int = 16, mode: str = "s1", image_id: int = 1,
            source_width: int = 32, source_height: int = 16,
            x: int = 0, y: int = 0, transparent_pen: int = 0,
            payload: bytes | None = None) -> bytes:
    return put_capture(empty_bank() if payload is None else payload,
                       image_id, screen, source_width, source_height,
                       x, y, width, height, cmap, transparent_pen,
                       mode=mode)


class AGSPHostTests(unittest.TestCase):
    def setUp(self):
        self.screen, self.cmap = simple_screen()

    def test_canonical_empty_header_and_round_trip(self):
        empty = empty_bank()
        self.assertEqual(len(empty), 32)
        self.assertEqual(empty[:4], b"AGSP")
        self.assertEqual(parse_payload(empty).generation, 1)
        self.assertEqual(parse_payload(empty).images, ())
        for bank_num in (5, 10, 65535):
            for chip in (False, True):
                raw = make_abk(bank_num, empty, chip_preferred=chip)
                self.assertEqual(len(raw), 52)
                self.assertEqual(raw[:4], b"AmBk")
                self.assertEqual(raw[12:20], NAME)
                number, flags, parsed = parse_abk(raw)
                self.assertEqual((number, flags, parsed.raw),
                                 (bank_num, 3 if chip else 1, empty))

    def test_first_appearance_mapping_and_exact_rgb24(self):
        bank = parse_payload(capture(self.screen, self.cmap))
        image = bank.image(1)
        self.assertEqual((image.width, image.height, image.depth, image.stride),
                         (16, 16, 2, 2))
        self.assertEqual((image.opaque_count, image.source_transparent_pen), (3, 0))
        self.assertEqual([image.index(x, 0) for x in range(4)], [0, 1, 2, 3])
        self.assertEqual(image.rgb(0, 0), None)
        self.assertEqual(image.rgb(1, 0), bytes([255, 80, 56]))
        self.assertEqual(image.rgb(2, 0), bytes([237, 198, 66]))
        self.assertEqual(image.rgb(3, 0), bytes([61, 199, 182]))
        self.assertEqual(len(image.palette), 48)
        self.assertEqual(image.palette[:3], bytes(3))
        self.assertEqual(image.palette[12:], bytes(36))
        self.assertEqual(len(image.planes), 64)
        self.assertEqual(len(bank.raw), 32 + 48 + 64 + 48)

    def test_identical_rgb_from_two_source_indices_is_one_opaque_color(self):
        palette = bytearray(self.cmap)
        palette[250 * 3:250 * 3 + 3] = palette[25 * 3:25 * 3 + 3]
        src = bytearray(self.screen)
        src[2] = 250
        src[3] = 25
        src[1] = 128
        src[0] = 0
        bank = parse_payload(capture(bytes(src), bytes(palette)))
        image = bank.image(1)
        self.assertEqual(image.rgb(2, 0), image.rgb(3, 0))
        self.assertEqual(image.index(2, 0), image.index(3, 0))
        self.assertEqual(image.opaque_count, 3)

    def test_transparent_pen_explicit_not_forced_zero(self):
        src = bytearray(16 * 16)
        src[0:4] = bytes([0, 7, 25, 67])
        bank = parse_payload(capture(bytes(src), self.cmap, source_width=16,
                                     source_height=16, transparent_pen=7))
        image = bank.image(1)
        self.assertEqual([image.index(x, 0) for x in range(4)], [1, 0, 2, 3])
        self.assertEqual(image.rgb(0, 0), bytes([1, 2, 3]))
        self.assertIsNone(image.rgb(1, 0))

    def test_black_opaque_distinct_from_transparency(self):
        src = bytearray([0] * (16 * 16))
        src[0] = 255
        bank = parse_payload(capture(bytes(src), self.cmap, source_width=16,
                                     source_height=16))
        image = bank.image(1)
        self.assertEqual(image.opaque_count, 1)
        self.assertEqual(image.rgb(0, 0), bytes(3))
        self.assertEqual(image.index(0, 0), 1)
        self.assertEqual(image.index(1, 0), 0)

    def test_empty_transparent_sprite_is_legal(self):
        blank = bytes(16 * 16)
        image = parse_payload(capture(blank, self.cmap,
                                      source_width=16, source_height=16)).image(1)
        self.assertEqual(image.opaque_count, 0)
        self.assertEqual(image.palette, bytes(48))
        self.assertEqual(image.planes, bytes(64))
        self.assertTrue(all(image.index(x, y) == 0 for x in range(16) for y in range(16)))

    def test_s1_rejects_four_opaque_colors_transactionally(self):
        src = bytearray(16 * 16)
        src[0:5] = bytes([0, 1, 2, 3, 4])
        cmap = b"".join(bytes((i, i + 1, i + 2)) for i in range(16))
        original = empty_bank()
        with self.assertRaisesRegex(ValueError, "too many opaque colors"):
            put_capture(original, 1, bytes(src), 16, 16, 0, 0, 16, 16,
                        cmap, 0, mode="s1")
        self.assertEqual(original, empty_bank())

    def test_s2_four_colors_uses_four_planar_bits(self):
        src = bytearray(16 * 16)
        src[0:5] = bytes([0, 1, 2, 3, 4])
        cmap = b"".join(bytes((i, i, i)) for i in range(16))
        image = parse_payload(capture(bytes(src), cmap,
                                      source_width=16, source_height=16,
                                      mode="s2")).image(1)
        self.assertEqual((image.depth, image.opaque_count), (4, 4))
        self.assertEqual([image.index(i, 0) for i in range(5)], [0, 1, 2, 3, 4])
        self.assertEqual(len(image.planes), 128)
        with self.assertRaisesRegex(ValueError, "16px 2-plane"):
            s0_interleaved_image(image)

    def test_s2_fifteen_colors_allowed_sixteen_rejected(self):
        cmap = b"".join(bytes((i, i, i)) for i in range(32))
        src = bytes([0] + list(range(1, 16)) + [0] * (16 * 15))
        image = parse_payload(capture(src, cmap, mode="s2",
                                      source_width=16, source_height=16)).image(1)
        self.assertEqual((image.depth, image.opaque_count), (4, 15))
        src = bytes(list(range(17)) + [0] * (16 * 16 - 17))
        with self.assertRaisesRegex(ValueError, "too many opaque colors"):
            capture(src, cmap, mode="s2", source_width=16, source_height=16)

    def test_width_16_32_64_s2_and_s1_width_restriction(self):
        for width in (16, 32, 64):
            src = bytes([0, 25, 67, 128] * (width * 2 // 4))
            image = parse_payload(capture(src, self.cmap, width=width,
                                          height=2, mode="s2",
                                          source_width=width, source_height=2)).image(1)
            self.assertEqual((image.width, image.stride, image.depth), (width, width // 8, 2))
            self.assertEqual(len(image.planes), (width // 8) * 2 * 2)
            self.assertEqual([image.index(x, 0) for x in range(4)], [0, 1, 2, 3])
            if width > 16:
                with self.assertRaisesRegex(ValueError, "S1 supports 16px"):
                    capture(src, self.cmap, width=width, height=2,
                            source_width=width, source_height=2)

    def test_16px_planar_layout_and_s0_interleave(self):
        src = bytearray(16 * 16)
        src[0:4] = bytes([25, 67, 128, 0])
        image = parse_payload(capture(bytes(src), self.cmap,
                                      source_width=16, source_height=16)).image(1)
        self.assertEqual(image.planes[:2], bytes.fromhex("a000"))  # plane0 for 1 and 3
        self.assertEqual(image.planes[32:34], bytes.fromhex("6000"))  # plane1 for 2 and 3
        raw = s0_interleaved_image(image)
        self.assertEqual(len(raw), 72)
        self.assertEqual(raw[:4], bytes(4))
        self.assertEqual(raw[4:8], bytes.fromhex("a0006000"))
        self.assertEqual(raw[-4:], bytes(4))

    def test_banks_allow_multi_image_different_local_palettes(self):
        first = capture(self.screen, self.cmap)
        second_src = bytes(7 if pen == 25 else pen for pen in self.screen)
        second = capture(second_src, self.cmap, image_id=12,
                         payload=first)
        p = parse_payload(second)
        self.assertEqual([x.image_id for x in p.images], [1, 12])
        self.assertEqual(p.generation, 3)
        self.assertEqual(p.image(1).palette[:12], parse_payload(first).image(1).palette[:12])
        self.assertNotEqual(p.image(1).palette, p.image(12).palette)
        self.assertEqual(parse_payload(first).generation, 2)
        self.assertEqual(second, parse_payload(second).raw)

    def test_replacing_image_is_atomic_and_keeps_other_images(self):
        original = capture(self.screen, self.cmap)
        both = capture(self.screen, self.cmap, image_id=10, payload=original)
        replacement = bytes([0] * (16 * 16))
        changed = capture(replacement, self.cmap, image_id=1, payload=both,
                          source_width=16, source_height=16)
        self.assertEqual(parse_payload(changed).image(1).opaque_count, 0)
        self.assertEqual(parse_payload(changed).image(10), parse_payload(both).image(10))
        self.assertEqual(parse_payload(both).image(1).opaque_count, 3)
        self.assertEqual(parse_payload(changed).generation, 4)
        with self.assertRaises(ValueError):
            capture(bytes([1] * 50), self.cmap, image_id=10, payload=changed)
        self.assertEqual(parse_payload(changed).generation, 4)

    def test_delete_preserves_image_id_and_generation(self):
        first = capture(self.screen, self.cmap, image_id=3)
        both = capture(self.screen, self.cmap, image_id=12, payload=first)
        third = delete_image(both, 3)
        p = parse_payload(third)
        self.assertEqual(([x.image_id for x in p.images], p.generation), ([12], 4))
        with self.assertRaises(KeyError):
            delete_image(third, 3)

    def test_hotspot_metadata_and_idempotence(self):
        original = capture(self.screen, self.cmap)
        changed = set_hotspot(original, 1, -5, 7)
        self.assertEqual((parse_payload(changed).image(1).hotspot_x,
                          parse_payload(changed).image(1).hotspot_y), (-5, 7))
        self.assertEqual(parse_payload(changed).generation, 3)
        self.assertEqual(set_hotspot(changed, 1, -5, 7), changed)
        self.assertEqual(parse_payload(original).image(1).hotspot_x, 0)
        with self.assertRaises(ValueError):
            set_hotspot(changed, 1, 32768, 0)

    def test_native_amos_save_length_high_bit_and_bad_length(self):
        payload = capture(self.screen, self.cmap)
        original = make_abk(24, payload)
        native = bytearray(original)
        pack_into(">I", native, 8, 0x80000000 | (len(native) - 12))
        self.assertEqual(parse_abk(bytes(native))[2].raw, payload)
        for bad_len in (len(native) - 11, 0x40000000 | (len(native) - 12), 0):
            bad = bytearray(native)
            pack_into(">I", bad, 8, bad_len)
            with self.assertRaises(ValueError):
                parse_abk(bytes(bad))
        with self.assertRaises(ValueError):
            parse_abk(bytes(native) + b"x")

    def test_ocs_sprite_or_agbo_name_not_accepted(self):
        raw = bytearray(make_abk(10, capture(self.screen, self.cmap)))
        raw[12:20] = b"AGABOBS "
        with self.assertRaises(ValueError):
            parse_abk(bytes(raw))
        raw[12:20] = NAME
        raw[20:24] = b"AGBO"
        with self.assertRaises(ValueError):
            parse_abk(bytes(raw))

    def test_invalid_capture_coordinates_and_dimensions(self):
        bad_cases = ((-1, 0, 16, 16), (0, -1, 16, 16),
                     (17, 0, 16, 16), (0, 1, 16, 16),
                     (0, 0, 17, 16), (0, 0, 16, 257),
                     (0, 0, 16, 0))
        for x, y, w, h in bad_cases:
            with self.subTest(x=x, y=y, w=w, h=h), self.assertRaises(ValueError):
                capture(self.screen, self.cmap, x=x, y=y, width=w, height=h)

    def test_invalid_screen_and_cmap(self):
        for screen, cmap in ((b"", self.cmap), (self.screen, b""),
                             (self.screen, bytes(769)),
                             (self.screen, bytes(4))):
            with self.subTest(len_screen=len(screen), len_cmap=len(cmap)):
                with self.assertRaises(ValueError):
                    capture(screen, cmap)
        src = bytearray(16 * 16)
        src[1] = 23
        with self.assertRaisesRegex(ValueError, "pixel index beyond"):
            capture(bytes(src), bytes(3 * 3), source_width=16, source_height=16)

    def test_source_transparent_index_must_exist_in_cmap(self):
        with self.assertRaisesRegex(ValueError, "transparent source pen outside CMAP"):
            capture(bytes(16 * 16), bytes(4 * 3),
                    source_width=16, source_height=16, transparent_pen=6)

    def test_bad_capture_mode_and_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            capture(self.screen, self.cmap, mode="invalid")
        for image_id in (0, 4097, True):
            with self.assertRaises(ValueError):
                capture(self.screen, self.cmap, image_id=image_id)

    def test_corrupt_payload_header_rejected(self):
        valid = capture(self.screen, self.cmap)
        mutations = ((0, b"AGBO"), (4, b"\x00\x02"),
                     (6, b"\x00\x01"), (8, b"\xff\xff"),
                     (10, b"\x00\x28"), (12, bytes(4)),
                     (16, bytes(4)), (20, bytes(4)),
                     (24, bytes(4)), (28, bytes([0, 0, 0, 1])))
        for offset, val in mutations:
            damaged = bytearray(valid)
            damaged[offset:offset + len(val)] = val
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                parse_payload(bytes(damaged))
        with self.assertRaises(ValueError):
            parse_payload(valid + bytes(1))
        with self.assertRaises(ValueError):
            parse_payload(valid[:-1])

    def test_corrupt_directory_offsets_flags_and_size_rejected(self):
        valid = capture(self.screen, self.cmap)
        # entry offsets: image_id=32, depth=38, flags=42, pixel_offset=44,
        # palette_offset=52, palette_length=56, count=64, reserved=68..
        alterations = ((32, b"\x00\x00"), (38, b"\x00\x08"),
                       (40, b"\x00\x01"), (42, b"\x00\x01"),
                       (44, bytes(4)), (48, bytes(4)),
                       (52, bytes(4)), (56, bytes(4)),
                       (64, bytes(2)), (68, b"\x00\x01"),
                       (72, b"\x00\x00\x00\x01"))
        for off, val in alterations:
            damaged = bytearray(valid)
            damaged[off:off + len(val)] = val
            with self.subTest(offset=off), self.assertRaises(ValueError):
                parse_payload(bytes(damaged))

    def test_corrupt_palette_padding_duplicate_and_pixel_index(self):
        valid = capture(self.screen, self.cmap)
        _, _, _, _, _, _, start, _, _, _ = HEADER.unpack_from(valid)
        img = parse_payload(valid).image(1)
        palette_start = start + len(img.planes)
        bad = bytearray(valid)
        bad[palette_start] = 1  # index zero palette must be black placeholder
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))
        bad = bytearray(valid)
        bad[palette_start + 45] = 1  # unused slot15 must be zero
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))
        bad = bytearray(valid)
        bad[palette_start + 6:palette_start + 9] = bad[palette_start + 3:palette_start + 6]
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))
        bad = bytearray(valid)
        bad[start] = 0  # remove first local pen 1, break canonical appearance order
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))

    def test_duplicate_image_id_in_directory_is_rejected(self):
        payload = capture(self.screen, self.cmap)
        payload = capture(self.screen, self.cmap, image_id=10, payload=payload)
        bad = bytearray(payload)
        # duplicate first id by changing second id to 1
        pack_into(">H", bad, HEADER.size + ENTRY.size, 1)
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))

    def test_generation_exhaustion_is_safe(self):
        payload = bytearray(capture(self.screen, self.cmap))
        pack_into(">I", payload, 24, 0xffffffff)
        with self.assertRaisesRegex(ValueError, "generation exhausted"):
            capture(self.screen, self.cmap, payload=bytes(payload))
        with self.assertRaisesRegex(ValueError, "generation exhausted"):
            delete_image(bytes(payload), 1)

    def test_independent_storage_not_a_dma_allocation(self):
        image = parse_payload(capture(self.screen, self.cmap)).image(1)
        self.assertEqual(len(image.planes), 2 * 2 * 16)
        self.assertEqual(len(s0_interleaved_image(image)), 8 + len(image.planes))
        self.assertNotEqual(image.planes, s0_interleaved_image(image))


if __name__ == "__main__":
    unittest.main(verbosity=2)
