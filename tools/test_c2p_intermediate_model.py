"""Deterministic host-only checks; not Gate A/B/C of the native extension."""
from __future__ import annotations

import unittest
from c2p_intermediate_model import (
    Bitmap, BYTES_PER_ROW, CHUNKY_BYTES, DEPTH, DoubleBuffer,
    HEIGHT, PLANE_BYTES, WIDTH, bitmap_to_chunky, blit_bitmaps, chunky_to_owned_bitmap,
)


class TestIntermediate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Entire range of 256 palette entries, along each x and y.
        cls.gradient = bytes((x + 3 * y) & 255 for y in range(HEIGHT) for x in range(WIDTH))
        cls.black = bytes(CHUNKY_BYTES)

    def test_geometry(self):
        self.assertEqual((CHUNKY_BYTES, PLANE_BYTES, BYTES_PER_ROW), (81920, 10240, 40))

    def test_round_trip_gradient(self):
        self.assertEqual(bitmap_to_chunky(chunky_to_owned_bitmap(self.gradient)), self.gradient)

    def test_round_trip_black(self):
        self.assertEqual(bitmap_to_chunky(chunky_to_owned_bitmap(self.black)), self.black)

    def test_round_trip_all_white(self):
        white = bytes([255]) * CHUNKY_BYTES
        self.assertEqual(bitmap_to_chunky(chunky_to_owned_bitmap(white)), white)

    def test_ends_and_nonbyte_aligned_pixels(self):
        pixels = bytearray(CHUNKY_BYTES)
        for x, y, color in ((0, 0, 1), (1, 0, 2), (7, 0, 8), (8, 0, 16),
                            (319, 0, 128), (0, 255, 255), (319, 255, 127),
                            (173, 81, 137)):
            pixels[y * WIDTH + x] = color
        self.assertEqual(bitmap_to_chunky(chunky_to_owned_bitmap(pixels)), pixels)

    def test_noninterleaved_copy(self):
        dst = Bitmap()
        blit_bitmaps(chunky_to_owned_bitmap(self.gradient), dst)
        self.assertEqual(bitmap_to_chunky(dst), self.gradient)

    def test_interleaved_copy(self):
        dst = Bitmap(interleaved=True)
        blit_bitmaps(chunky_to_owned_bitmap(self.gradient), dst)
        self.assertEqual(bitmap_to_chunky(dst), self.gradient)

    def test_padded_row_copy(self):
        dst = Bitmap(padding=4)
        blit_bitmaps(chunky_to_owned_bitmap(self.gradient), dst)
        self.assertEqual(bitmap_to_chunky(dst), self.gradient)

    def test_interleaved_padded_row_copy(self):
        dst = Bitmap(interleaved=True, padding=4)
        blit_bitmaps(chunky_to_owned_bitmap(self.gradient), dst)
        self.assertEqual(bitmap_to_chunky(dst), self.gradient)

    def test_bad_length_rejected_without_write(self):
        db = DoubleBuffer()
        self.assertFalse(db.convert_and_blit(self.gradient[:-1]))
        self.assertFalse(db.convert_and_blit(self.gradient + b'x'))
        self.assertEqual(db.blit_count, 0)
        self.assertEqual(bitmap_to_chunky(db.buffers[1]), self.black)

    def test_not_safe_does_not_modify_back(self):
        db = DoubleBuffer()
        db.set_safe(False)
        self.assertFalse(db.convert_and_blit(self.gradient))
        self.assertEqual(bitmap_to_chunky(db.buffers[1]), self.black)
        self.assertEqual(db.blit_count, 0)

    def test_front_is_immutable_during_conversion(self):
        db = DoubleBuffer()
        front_snapshot = db.buffers[db.front].packed_bytes()
        self.assertTrue(db.convert_and_blit(self.gradient))
        self.assertEqual(db.buffers[db.front].packed_bytes(), front_snapshot)
        self.assertEqual(bitmap_to_chunky(db.buffers[1]), self.gradient)

    def test_swap_blocks_writes_until_safe(self):
        db = DoubleBuffer()
        self.assertTrue(db.convert_and_blit(self.gradient))
        self.assertTrue(db.swap())
        self.assertFalse(db.convert_and_blit(self.black))
        self.assertFalse(db.swap())
        db.set_safe(True)
        self.assertTrue(db.convert_and_blit(self.black))
        self.assertEqual(bitmap_to_chunky(db.buffers[db.front]), self.gradient)
        self.assertEqual(bitmap_to_chunky(db.buffers[1-db.front]), self.black)

    def test_interleaved_double_buffer(self):
        db = DoubleBuffer(interleaved_back=True)
        self.assertTrue(db.convert_and_blit(self.gradient))
        self.assertTrue(db.swap())
        self.assertEqual(bitmap_to_chunky(db.buffers[db.front]), self.gradient)

    def test_closed_refuses_operations(self):
        db = DoubleBuffer()
        db.close()
        self.assertFalse(db.convert_and_blit(self.gradient))
        self.assertFalse(db.swap())
        db.set_safe(True)
        self.assertFalse(db.safe)

    def test_bad_row_input(self):
        bmp = Bitmap()
        with self.assertRaises(ValueError):
            bmp.write(0, 0, b'x')
        with self.assertRaises(ValueError):
            bmp.read(8, 0)
        with self.assertRaises(ValueError):
            Bitmap(padding=-1)


if __name__ == '__main__':
    unittest.main()
