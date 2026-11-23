#!/usr/bin/env python3
"""Host-only AGTM format and reference pixel tests (not Gate A/B/C/D)."""

import struct
import unittest

from agtm_format_proto import (
    AGTMError, AGTMMap, HEADER_BYTES, decode_agtm, encode_agtm, render_reference,
)


class AGTMFormatTests(unittest.TestCase):
    def make_map(self, cols=32, rows=32, layers=2, tile_count=4):
        size = cols * rows
        maps = [bytes((x + 3 * y) % tile_count
                      for y in range(rows) for x in range(cols))]
        for _ in range(layers - 1):
            maps.append(bytes((x * y) % tile_count
                              for y in range(rows) for x in range(cols)))
        return AGTMMap(cols, rows, tile_count, tuple(maps))

    def test_signature_exact_fields_and_32x32_round_trip(self):
        tilemap = self.make_map()
        raw = encode_agtm(tilemap)
        self.assertEqual(raw[:4], b"AGTM")
        self.assertEqual(len(raw), HEADER_BYTES + 2 * 32 * 32)
        self.assertEqual(struct.unpack_from(">H", raw, 4)[0], 1)
        self.assertEqual(struct.unpack_from(">H", raw, 8)[0], 32)
        self.assertEqual(struct.unpack_from(">H", raw, 10)[0], 32)
        self.assertEqual(struct.unpack_from(">I", raw, 20)[0], 32)
        self.assertEqual(struct.unpack_from(">I", raw, 24)[0], 1024)
        self.assertEqual(struct.unpack_from(">I", raw, 28)[0], 64)
        self.assertEqual(struct.unpack_from(">I", raw, 32)[0], 2048)
        self.assertEqual(raw[36:64], bytes(28))
        self.assertEqual(decode_agtm(raw), tilemap)
        self.assertEqual(encode_agtm(decode_agtm(raw)), raw)

    def test_big_endian_width_and_200_by_200(self):
        tilemap = self.make_map(200, 200)
        raw = encode_agtm(tilemap)
        self.assertEqual(raw[8:10], b"\x00\xc8")
        self.assertEqual(len(raw), 80_064)
        self.assertEqual(decode_agtm(raw).cell(0, 199, 199),
                         tilemap.cell(0, 199, 199))

    def test_maximum_geometry_four_layers(self):
        raw = encode_agtm(self.make_map(256, 256, 4, 256))
        self.assertEqual(len(raw), 262_208)
        self.assertEqual(len(decode_agtm(raw).layers), 4)
        self.assertEqual(decode_agtm(raw).tile_count, 256)

    def test_cell_edit_is_immutable_and_encoded(self):
        original = self.make_map()
        old = original.cell(1, 0, 0)
        changed = original.with_cell(1, 0, 0, 3)
        self.assertEqual(original.cell(1, 0, 0), old)
        self.assertEqual(changed.cell(1, 0, 0), 3)
        self.assertEqual(decode_agtm(encode_agtm(changed)), changed)
        self.assertIs(changed.with_cell(1, 0, 0, 3), changed)

    def test_invalid_map_dimensions_indices_and_coordinates(self):
        for args in ((0, 1, 2, (b"\x00",)),
                     (1, 257, 2, (bytes(257),)),
                     (1, 1, 257, (b"\x00",)),
                     (1, 1, 2, (b"\x02",)),
                     (1, 1, 2, (b"\x00",) * 5)):
            with self.subTest(args=args), self.assertRaises(AGTMError):
                AGTMMap(*args)
        with self.assertRaises(AGTMError):
            self.make_map().cell(2, 0, 0)
        with self.assertRaises(AGTMError):
            self.make_map().with_cell(0, 0, 0, 4)

    def test_reject_corrupt_header_and_payload(self):
        raw = encode_agtm(self.make_map())
        mutations = [
            (0, b"OTM!"), (4, b"\x00\x02"), (6, b"\x00\x20"),
            (8, b"\x00\x00"), (12, b"\x08"), (14, b"\x05"),
            (15, b"\x02"), (16, b"\x00\x00"), (18, b"\x00\x01"),
            (20, b"\x00\x00\x00\x21"),
            (24, b"\x00\x00\x03\xff"),
            (28, b"\x00\x00\x00\x00"),
            (32, b"\x00\x00\x08\x01"),
            (36, b"\x80"),
            (64, b"\xff"),
        ]
        for offset, replace in mutations:
            with self.subTest(offset=offset, replacement=replace):
                broken = raw[:offset] + replace + raw[offset + len(replace):]
                with self.assertRaises(AGTMError):
                    decode_agtm(broken)
        for bad in (raw[:-1], raw + b"\x00", raw[:35], b""):
            with self.subTest(length=len(bad)), self.assertRaises(AGTMError):
                decode_agtm(bad)

    def test_palette_zero_is_opaque_on_ground_and_transparent_on_overlay(self):
        tiles = [bytes(256), bytes([5] * 256), bytearray(256)]
        tiles[2][2 * 16 + 1] = 7
        base = bytes((0, 1))
        overlay = bytes((0, 2))
        map_data = AGTMMap(2, 1, 3, (base, overlay))
        pixels = render_reference(map_data, tuple(bytes(t) for t in tiles),
                                  0, 0, 32, 16)
        self.assertEqual(pixels[0], 0)
        self.assertEqual(pixels[16], 5)
        self.assertEqual(pixels[2 * 32 + 17], 7)
        self.assertEqual(pixels[2 * 32 + 18], 5)

    def test_unaligned_camera_over_tile_boundary(self):
        tiles = tuple(bytes([i + 1] * 256) for i in range(3))
        tilemap = AGTMMap(3, 1, 3, (b"\x00\x01\x02",))
        for camera_x in (1, 8, 15, 16, 17, 31):
            pixels = render_reference(tilemap, tiles, camera_x, 0,
                                      48 - camera_x, 1)
            expected = bytes((x // 16 + 1) for x in range(camera_x, 48))
            self.assertEqual(pixels, expected)

    def test_reject_viewport_or_tileset_mismatch(self):
        tilemap = AGTMMap(1, 1, 1, (b"\x00",))
        for args in ((0, 0, 17, 1), (-1, 0, 1, 1), (0, 0, 0, 1)):
            with self.subTest(args=args), self.assertRaises(AGTMError):
                render_reference(tilemap, (bytes(256),), *args)
        with self.assertRaises(AGTMError):
            render_reference(tilemap, (), 0, 0, 16, 16)


if __name__ == "__main__":
    unittest.main()
