#!/usr/bin/env python3
"""M19 ABK host-only regression tests. Not a native Gate A/B/C."""
import unittest
from struct import pack_into
from m19_agabob_abk import (BobBank, BobImage, BobFormatError, ABK, HEADER,
                            ENTRY, DATA_OFFSET, MASK_FLAG,
                            planar_from_indices, indices_from_planar, stride_for)


class TestM19BobAbk(unittest.TestCase):
    @staticmethod
    def pattern(w, h, depth):
        return bytes((x * 11 + y * 7 + (x ^ y)) % (1 << depth)
                     for y in range(h) for x in range(w))

    def test_geometry_and_planar_roundtrip(self):
        for depth in (1, 4, 8):
            for w in (1, 17, 31, 32, 37):
                for h in (1, 2, 19):
                    data = self.pattern(w, h, depth)
                    raw = planar_from_indices(w, h, depth, data)
                    self.assertEqual(len(raw), stride_for(w) * h * depth)
                    self.assertEqual(indices_from_planar(w, h, depth, raw), data)

    def test_three_images_save_load(self):
        from m19_agabob_fixture import build_fixture
        raw = build_fixture()
        bank = BobBank.from_abk(raw, expected_bank=10)
        self.assertEqual(bank.to_abk(), raw)
        self.assertEqual(len(bank.images), 3)
        self.assertEqual([x.depth for x in bank.images.values()], [4, 8, 1])
        self.assertIsNone(bank.images[3].mask)
        self.assertEqual(bank.images[3].colours(), b'\0')

    def test_inclusive_capture_and_independent_replacement(self):
        w, h, depth = 96, 48, 8
        source = self.pattern(w, h, depth)
        bank = BobBank(10)
        bounds = ((1, 0, 0, 0, 0), (2, 3, 4, 19, 15),
                  (3, 33, 8, 63, 10), (4, 59, 20, 95, 38))
        for ident, x1, y1, x2, y2 in bounds:
            bank.capture(ident, w, h, depth, source, x1, y1, x2, y2)
            expected = bytes(source[y * w + x]
                             for y in range(y1, y2 + 1)
                             for x in range(x1, x2 + 1))
            self.assertEqual(bank.images[ident].colours(), expected)
        original = dict(bank.images)
        bank.capture(2, w, h, depth, source, 5, 8, 41, 32)
        self.assertNotEqual(bank.images[2], original[2])
        for ident in (1, 3, 4):
            self.assertEqual(bank.images[ident], original[ident])
        self.assertEqual(BobBank.from_abk(bank.to_abk()).images, bank.images)

    def test_native_planar_source_oracle(self):
        for depth in (1, 4, 8):
            w, h = 96, 48
            source = self.pattern(w, h, depth)
            stride = stride_for(w)
            raw = planar_from_indices(w, h, depth, source)
            planes = [raw[p * stride * h:(p + 1) * stride * h]
                      for p in range(depth)]
            for width, x1, y1 in ((1, 3, 2), (17, 5, 17),
                                  (31, 65, 0), (32, 0, 16),
                                  (37, 59, 43)):
                height = min(5, h - y1)
                chunky, planar = BobBank(10), BobBank(10)
                coords = (x1, y1, x1 + width - 1, y1 + height - 1)
                chunky.capture(1, w, h, depth, source, *coords)
                planar.capture_planar(1, w, h, depth, planes, stride, *coords)
                self.assertEqual(chunky.to_abk(), planar.to_abk())
            with self.assertRaises(BobFormatError):
                BobBank(11).capture_planar(1, w, h, depth, planes, stride - 1,
                                           0, 0, 15, 15)
            with self.assertRaises(BobFormatError):
                BobBank(11).capture_planar(1, w, h, depth, planes[:-1], stride,
                                           0, 0, 15, 15)

    def test_independent_alpha_zero_opaque(self):
        bank = BobBank(10)
        bank.put(1, BobImage.from_pixels(17, 1, 8,
                 bytes([0, 1, 5, 0] + [7] * 13)))
        self.assertIsNone(bank.images[1].mask)
        bank.make_mask(1, 5)
        self.assertEqual(bank.images[1].mask[0], 0xdf)
        self.assertEqual(bank.images[1].mask[2], 0x80)
        self.assertEqual(bank.images[1].colours()[0], 0)
        bank.make_mask(1, 0)
        self.assertEqual(bank.images[1].mask[0] & 0x80, 0)
        bank.no_mask(1)
        self.assertIsNone(bank.images[1].mask)

    def test_transactional_capacity_and_bounds(self):
        bank = BobBank(10)
        bank.put(1, BobImage.from_pixels(31, 10, 8, self.pattern(31, 10, 8)))
        original = bank.to_abk()
        with self.assertRaises(BobFormatError):
            bank.put(2, BobImage.from_pixels(512, 512, 8, bytes(512 * 512)))
        with self.assertRaises(BobFormatError):
            bank.capture(2, 64, 64, 8, bytes(64 * 64), 20, 20, 19, 40)
        with self.assertRaises(BobFormatError):
            bank.make_mask(3, 0)
        self.assertEqual(bank.to_abk(), original)

    def test_wrong_abk_rejected(self):
        raw = BobBank(10).to_abk()
        candidates = []
        for offset, value in ((0, ord('X')), (12, ord('X')),
                              (ABK.size, 0xff), (len(raw) - 1, 1)):
            data = bytearray(raw)
            data[offset] = value
            candidates.append(bytes(data))
        data = bytearray(raw)
        pack_into('>I', data, 8, 27)
        candidates.append(bytes(data))
        for candidate in candidates:
            with self.assertRaises(BobFormatError):
                BobBank.from_abk(candidate)
        with self.assertRaises(BobFormatError):
            BobBank.from_abk(raw, expected_bank=11)

    def test_directory_offsets_and_corruption(self):
        bank = BobBank(10)
        bank.put(1, BobImage.from_pixels(17, 9, 8, self.pattern(17, 9, 8)))
        bank.make_mask(1, 0)
        raw = bank.to_abk()
        payload = raw[ABK.size:]
        self.assertEqual(HEADER.unpack_from(payload)[6], DATA_OFFSET + 9 * 4 * 9)
        self.assertEqual(ENTRY.unpack_from(payload, HEADER.size)[:6],
                         (1, 17, 9, 8, 4, MASK_FLAG))
        for offset in (HEADER.size + 12, HEADER.size + 20):
            data = bytearray(raw)
            data[ABK.size + offset] ^= 1
            with self.assertRaises(BobFormatError):
                BobBank.from_abk(bytes(data))


if __name__ == '__main__':
    unittest.main(verbosity=2)
