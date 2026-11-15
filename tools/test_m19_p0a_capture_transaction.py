#!/usr/bin/env python3
"""R88-host-only capture/transaction tests; NOT a native 68k or WinUAE Gate."""
from __future__ import annotations

import unittest
from struct import unpack_from

from m19_p0a_multi_bob_abk import empty_bank, parse_payload
from m19_p0a_capture_transaction import BackBitmap, HostBobBanks, read_back_rectangle


def make_bitmap(w: int, h: int, depth: int, *, stride_extra=0, safe=True) -> tuple[BackBitmap, bytes]:
    stride = 2 * ((w + 15) // 16) + stride_extra
    pixels = bytes((0 if (x + y) % 9 == 0 else (x * 7 + y * 13) & ((1 << depth) - 1))
                   for y in range(h) for x in range(w))
    planes = [bytearray(stride * h) for _ in range(depth)]
    for y in range(h):
        for x in range(w):
            color = pixels[y * w + x]
            byte = y * stride + (x >> 3)
            for p in range(depth):
                if color & (1 << p):
                    planes[p][byte] |= 0x80 >> (x & 7)
    return BackBitmap(w, h, depth, stride, tuple(bytes(p) for p in planes), safe), pixels


class CaptureAndAtomicBank(unittest.TestCase):
    def test_inclusive_coordinates_and_unaligned_offsets(self):
        for depth in (1, 4, 8):
            for w in (1, 17, 31, 32, 37):
                bmp, pixels = make_bitmap(w + 3, 5, depth, stride_extra=6)
                for x1 in (0, 3):
                    x2 = x1 + w - 1
                    width, height, got = read_back_rectangle(bmp, x1, 2, x2, 3)
                    expected = bytes(pixels[y * bmp.width + x] for y in (2, 3)
                                     for x in range(x1, x2 + 1))
                    self.assertEqual((width, height, got), (w, 2, expected))

    def test_single_pixel_and_full_edges(self):
        bmp, px = make_bitmap(37, 9, 8, stride_extra=2)
        self.assertEqual(read_back_rectangle(bmp, 36, 8, 36, 8), (1, 1, px[-1:]))
        self.assertEqual(read_back_rectangle(bmp, 0, 0, 36, 8), (37, 9, px))

    def test_safe_missing_refuses_before_reading(self):
        bmp, _ = make_bitmap(37, 5, 8, safe=False)
        with self.assertRaisesRegex(ValueError, "Safe"):
            read_back_rectangle(bmp, 0, 0, 31, 1)

    def test_reject_invalid_geometry_and_bad_physical_stride(self):
        bmp, _ = make_bitmap(32, 4, 8)
        for args in ((-1, 0, 1, 1), (1, 2, 0, 2), (0, 0, 32, 1),
                     (0, 0, 1, 4), (0, -1, 1, 1), (1, 1, 1.0, 1)):
            with self.assertRaises(ValueError):
                read_back_rectangle(bmp, *args)
        bad = BackBitmap(32, 4, 8, 2, bmp.planes, True)
        with self.assertRaises(ValueError):
            bad.validate()
        bad = BackBitmap(32, 4, 8, 4, bmp.planes[:-1], True)
        with self.assertRaises(ValueError):
            bad.validate()
        bad = BackBitmap(32, 4, 8, 4, bmp.planes[:-1] + (b"\0",), True)
        with self.assertRaises(ValueError):
            bad.validate()

    def test_create_empty_and_two_images_same_bank(self):
        bank = HostBobBanks()
        bank.select(10)
        self.assertEqual(bank.payload(10), empty_bank())
        bmp, pixels = make_bitmap(47, 5, 8, stride_extra=4)
        bank.capture(5, bmp, 3, 1, 39, 3)
        bank.capture(1, bmp, 0, 0, 16, 1)
        data = parse_payload(bank.payload(10))
        self.assertEqual((data.generation, [x.image_id for x in data.images]), (3, [1, 5]))
        self.assertEqual((data.image(5).width, data.image(5).height), (37, 3))
        for y in range(3):
            for x in range(37):
                self.assertEqual(data.image(5).colour(x, y), pixels[(y + 1) * 47 + (x + 3)])
        self.assertEqual(data.image(5).mask, None)

    def test_replace_one_image_preserves_other(self):
        store = HostBobBanks()
        bmp, _ = make_bitmap(41, 3, 4, stride_extra=2)
        store.select(11)
        store.capture(1, bmp, 0, 0, 16, 2)
        store.capture(2, bmp, 1, 0, 31, 2)
        old = parse_payload(store.payload(11))
        store.capture(1, bmp, 2, 1, 38, 2)
        new = parse_payload(store.payload(11))
        self.assertEqual(new.image(2), old.image(2))
        self.assertEqual((new.image(1).width, new.image(1).height), (37, 2))
        self.assertEqual(new.generation, old.generation + 1)

    def test_mask_explicit_index_zero_remains_opaque_when_unmasked(self):
        store = HostBobBanks()
        bmp, pixels = make_bitmap(17, 2, 8)
        store.select(12)
        store.capture(1, bmp, 0, 0, 16, 1)
        store.mask(1, 0)
        obj = parse_payload(store.payload(12)).image(1)
        self.assertFalse(obj.visible(0, 0))
        self.assertTrue(obj.visible(1, 0))
        store.unmask(1)
        self.assertTrue(parse_payload(store.payload(12)).image(1).visible(0, 0))
        self.assertEqual(store.payload(12), store.payload(12))

    def test_two_banks_independent_and_roundtrip(self):
        store = HostBobBanks()
        bmp, _ = make_bitmap(37, 5, 8)
        store.select(10)
        store.capture(1, bmp, 0, 0, 36, 2)
        first = store.save(10)
        store.select(20)
        store.capture(1, bmp, 1, 1, 17, 3)
        second = store.save(20)
        self.assertNotEqual(first, second)
        other = HostBobBanks()
        other.load(first)
        other.load(second)
        self.assertEqual(other.save(10), first)
        self.assertEqual(other.save(20), second)
        other.select(10)
        self.assertEqual(other.current_number(), 10)

    def test_load_or_erase_requires_explicit_reselection(self):
        store = HostBobBanks()
        bmp, _ = make_bitmap(17, 2, 8)
        store.select(10)
        store.capture(1, bmp, 0, 0, 16, 1)
        before = store.save(10)
        store.load(before, into=10)
        with self.assertRaisesRegex(ValueError, "reselect"):
            store.capture(2, bmp, 0, 0, 0, 0)
        store.select(10)
        store.capture(2, bmp, 0, 0, 0, 0)
        store.erase(10)
        with self.assertRaisesRegex(ValueError, "reselect"):
            store.capture(3, bmp, 0, 0, 0, 0)
        store.select(10)
        self.assertEqual(store.payload(10), empty_bank())

    def test_allocator_failure_is_non_destructive(self):
        allocations = []
        def allocator(size):
            allocations.append(size)
            return len(allocations) != 2
        store = HostBobBanks(allocator)
        store.select(10)
        old = store.payload(10)
        bmp, _ = make_bitmap(17, 2, 8)
        with self.assertRaises(MemoryError):
            store.capture(1, bmp, 0, 0, 16, 1)
        self.assertEqual(store.payload(10), old)
        # Subsequent allocation succeeds, preserving original bank identity.
        store.capture(1, bmp, 0, 0, 16, 1)
        self.assertEqual(len(parse_payload(store.payload(10)).images), 1)

    def test_foreign_bank_never_overwritten(self):
        store = HostBobBanks()
        store.inject_foreign_bank_for_test(10, b"AGAPIC  " + b"\0" * 100)
        with self.assertRaises(ValueError):
            store.select(10)
        self.assertEqual(store.payload(10), b"AGAPIC  " + b"\0" * 100)

    def test_invalid_capture_never_mutates_source(self):
        store = HostBobBanks()
        bmp, _ = make_bitmap(32, 2, 8)
        store.select(10)
        store.capture(1, bmp, 0, 0, 31, 1)
        old = store.payload(10)
        for args in ((2, bmp, 1, 1, 0, 1), (2, bmp, 0, 0, 32, 1),
                     (0, bmp, 0, 0, 0, 0)):
            with self.assertRaises(ValueError):
                store.capture(*args)
        self.assertEqual(store.payload(10), old)

    def test_unaligned_plane_storage_is_pixel_exact(self):
        bmp, px = make_bitmap(19, 3, 4, stride_extra=6)
        _, _, captured = read_back_rectangle(bmp, 1, 1, 17, 2)
        self.assertEqual(captured, bytes(px[y * 19 + x] for y in (1,2)
                                         for x in range(1,18)))

    def test_bool_invalid_image_id(self):
        store = HostBobBanks()
        store.select(10)
        bmp, _ = make_bitmap(2, 2, 1)
        with self.assertRaises(ValueError):
            store.capture(True, bmp, 0, 0, 1, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)