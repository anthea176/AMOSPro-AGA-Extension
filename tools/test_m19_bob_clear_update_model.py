#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Behavioural oracle for M19 Clear/Update; NO native Gate A claim."""
import unittest
from m19_bob_clear_update_model import BobFrameModel, BobImage, CLEAN, DIRTY, READY


def img(pixels, depth=4, mask=None):
    return BobImage(tuple(tuple(r) for r in pixels), depth,
                    None if mask is None else tuple(tuple(r) for r in mask))


class ClearUpdate(unittest.TestCase):
    def setUp(self):
        self.m = BobFrameModel(8, 5, 4)
        self.assertTrue(self.m.install_bank(10, {1: img([[1, 2], [3, 4]]),
                                                   2: img([[6, 7], [8, 9]], mask=[[1, 0], [1, 1]])}))

    def test_update_has_no_implicit_swap_and_preserves_backdrop(self):
        m = self.m
        self.assertTrue(m.edit_background(2, 2, 12))
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        before_front = m._copy(m.pages[m.front])
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][2][2], 1)
        self.assertEqual(m.pages[m.front], before_front)
        self.assertEqual(m.front, 0)
        self.assertEqual(m.swaps, 0)
        self.assertEqual(m.status, READY)
        self.assertFalse(m.update())
        self.assertTrue(m.swap())
        self.assertEqual(m.status, CLEAN)

    def test_clear_is_physical_page_local_and_idempotent(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        displayed = m._copy(m.pages[m.front])
        self.assertTrue(m.clear())
        self.assertTrue(m.clear())
        self.assertEqual(m.pages[m.front], displayed)
        self.assertEqual(m.pages[m.back][2][2], 0)
        self.assertEqual(m.status, CLEAN)

    def test_off_move_reactivation_two_pages_no_ghost(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 1, 1))
        for i in range(12):
            if i == 3:
                self.assertTrue(m.off(1))
            if i == 6:
                self.assertTrue(m.put(1, 10, 1, 5, 2))
            self.assertTrue(m.update())
            self.assertTrue(m.swap())
            if 4 <= i < 6:
                self.assertTrue(all(1 not in row for row in m.pages[m.front]))
            if i >= 7:
                self.assertEqual(m.pages[m.front][2][5], 1)
                self.assertEqual(m.pages[m.front][1][1], 0)
            self.assertEqual(m.backing_reserved,
                             m.backing_bytes_per_page * (2 if i else 1))

    def test_overlay_mask_and_reverse_restoration(self):
        m = self.m
        self.assertTrue(m.edit_background(3, 2, 12))
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        self.assertTrue(m.put(2, 10, 2, 2, 2))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][2][2], 6)
        self.assertEqual(m.pages[m.back][2][3], 2)
        self.assertTrue(m.swap())
        self.assertTrue(m.edit_background(3, 2, 13))
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        self.assertTrue(m.off(2))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][2][3], 2)
        self.assertEqual(m.pages[m.back][2][2], 1)
        self.assertTrue(m.swap())
        self.assertTrue(m.clear())
        self.assertEqual(m.pages[m.back][2][3], 13)

    def test_background_edit_rejected_until_clear(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        self.assertTrue(m.update()); self.assertTrue(m.swap())
        self.assertTrue(m.update()); self.assertTrue(m.swap())
        self.assertFalse(m.edit_background(2, 2, 12))
        self.assertTrue(m.clear())
        self.assertTrue(m.edit_background(2, 2, 12))
        self.assertTrue(m.update())
        self.assertEqual(m.saved[m.back][2][2], 12)
        self.assertTrue(m.swap())
        self.assertTrue(m.update()); self.assertTrue(m.swap())
        self.assertTrue(m.clear())
        self.assertEqual(m.pages[m.back][2][2], 12)

    def test_preflight_stale_bank_fail_closed(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 1, 1))
        previous = m._copy(m.pages[m.back])
        m.install_bank(10, {1: img([[5]])})
        self.assertFalse(m.update())
        self.assertEqual(m.status, DIRTY)
        self.assertFalse(m.swap())
        self.assertEqual(m.pages[m.back], previous)
        self.assertFalse(m.clear())
        m.close(); m.reopen()
        self.assertTrue(m.put(1, 10, 1, 1, 1))
        self.assertTrue(m.update())

    def test_partial_draw_fault_requires_recovery_before_swap(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        self.assertFalse(m.update(inject_fault_after_pixels=2))
        self.assertEqual(m.status, DIRTY)
        self.assertFalse(m.swap())
        self.assertTrue(m.clear())
        self.assertEqual(m.pages[m.back][2][2], 0)
        self.assertTrue(m.update()); self.assertTrue(m.swap())

    def test_out_of_memory_fail_before_first_pixel(self):
        m = BobFrameModel(8, 5, 4, backing_budget=20)
        m.install_bank(10, {1: img([[5]])})
        self.assertTrue(m.put(1, 10, 1, 1, 1))
        before = m._copy(m.pages[m.back])
        self.assertFalse(m.update())
        self.assertEqual(m.status, DIRTY)
        self.assertEqual(m.pages[m.back], before)
        self.assertEqual(m.backing_reserved, 0)
        self.assertFalse(m.swap())

    def test_clipping_and_depth_and_mask_index_zero(self):
        m = self.m
        m.install_bank(11, {1: img([[0, 5], [6, 7]], mask=None)})
        self.assertTrue(m.put(1, 11, 1, -1, 0))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][0][0], 5)
        self.assertEqual(m.pages[m.back][1][0], 7)
        self.assertTrue(m.swap())
        m.install_bank(12, {1: img([[0]])})
        self.assertTrue(m.put(2, 12, 1, 1, 1))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][1][1], 0)

    def test_sixty_four_sorted_and_repeatable(self):
        m = BobFrameModel(16, 4, 4)
        m.install_bank(10, {1: img([[3]])})
        m.install_bank(11, {1: img([[7]])})
        for n in range(64, 0, -1):
            self.assertTrue(m.put(n, 10 if n % 2 else 11, 1, n % 16, n % 4))
        for frame in range(6):
            self.assertTrue(m.update())
            self.assertTrue(m.swap())
            self.assertEqual(m.pages[m.front][0][0], 7)
            self.assertEqual(m.swaps, frame + 1)

    def test_full_405_frame_nine_stage_cycle(self):
        m = BobFrameModel(24, 8, 4)
        m.install_bank(10, {1: img([[1, 2], [3, 4]])})
        m.install_bank(11, {1: img([[6, 7], [8, 9]], mask=[[1, 0], [1, 1]])})
        phases = (2, 1, 0, 2, 4, 8, 16, 64, 16)
        previous = 0
        for stage, count in enumerate(phases):
            for n in range(1, previous + 1):
                if n > count:
                    self.assertTrue(m.off(n))
            for n in range(1, count + 1):
                self.assertTrue(m.put(n, 10 if n % 2 else 11, 1,
                                      (n * 5 + stage) % 24, (n * 3) % 8))
            for frame in range(45):
                self.assertTrue(m.update())
                self.assertTrue(m.swap())
                self.assertEqual(m.status, CLEAN)
            previous = count
        self.assertEqual(m.swaps, 405)
        self.assertEqual(m.draw_calls, 405)
        self.assertEqual(m.backing_reserved, 2 * m.backing_bytes_per_page)
        m.close()
        self.assertEqual(m.backing_reserved, 0)

    def test_planar_backing_pitch_and_page_capacity(self):
        for width, depth, expected in ((1, 1, 2), (16, 1, 2),
                                       (17, 1, 4), (320, 8, 320)):
            m = BobFrameModel(width, 256, depth)
            self.assertEqual(m.backing_bytes_per_page, expected * 256)
        full = BobFrameModel(320, 256, 8)
        self.assertEqual(full.backing_bytes_per_page, 81920)
        self.assertEqual(2 * full.backing_bytes_per_page, 163840)

    def test_no_screen_leak_after_close_and_reopen(self):
        m = self.m
        self.assertTrue(m.put(1, 10, 1, 1, 1))
        self.assertTrue(m.update()); self.assertTrue(m.swap())
        self.assertEqual(m.backing_reserved, m.backing_bytes_per_page)
        m.close()
        self.assertEqual(m.backing_reserved, 0)
        self.assertEqual(m.objects, {})
        self.assertFalse(m.update())
        m.reopen()
        self.assertTrue(m.put(1, 10, 1, 2, 2))
        self.assertTrue(m.update()); self.assertTrue(m.swap())

    def test_invalid_inputs_fail_before_paint(self):
        with self.assertRaises(ValueError):
            img([[1], [1, 2]])
        with self.assertRaises(ValueError):
            img([[1]], depth=0)
        with self.assertRaises(ValueError):
            img([[1]], depth=1, mask=[[True, False]])
        self.assertFalse(self.m.put(65, 10, 1, 0, 0))
        self.assertFalse(self.m.put(1, 10, 999, 0, 0))
        self.assertFalse(self.m.off(1))
        self.assertEqual(self.m.draw_calls, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
