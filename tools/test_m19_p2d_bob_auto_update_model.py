#!/usr/bin/env python3
"""P2d behaviour at the presentation boundary, including recovery and retries."""

import unittest

from m19_bob_clear_update_model import CLEAN, DIRTY, READY, BobImage
from m19_p2d_bob_auto_update_model import BobAutoUpdateModel


class BobAutoUpdateTests(unittest.TestCase):
    def setUp(self):
        self.model = BobAutoUpdateModel(4, 1, 4)
        self.model.pages[0][0] = [9, 9, 9, 9]
        self.model.pages[1][0] = [12, 12, 12, 12]
        self.assertTrue(self.model.install_bank(5, {1: BobImage(((3, 2),), 4, ((True, False),))}))
        self.assertTrue(self.model.put(1, 5, 1, 0, 0))

    def test_default_preserves_explicit_update(self):
        m = self.model
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [12, 12, 12, 12])
        self.assertEqual(m.draw_calls, 0)
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [3, 9, 9, 9])

    def test_auto_update_restores_each_page_with_mask_and_background_edit(self):
        m = self.model
        self.assertTrue(m.set_auto_update(True))
        self.assertTrue(m.set_planes(1, 1))
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [13, 12, 12, 12])
        self.assertTrue(m.put(1, 5, 1, 2, 0))
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [9, 9, 9, 9])
        self.assertTrue(m.clear())
        self.assertTrue(m.edit_background(0, 0, 4))
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [4, 12, 13, 12])
        self.assertTrue(m.off(1))
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [9, 9, 9, 9])
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [4, 12, 12, 12])

    def test_display_refusal_keeps_ready_and_retries_without_repaint(self):
        m = self.model
        self.assertTrue(m.set_auto_update(True))
        self.assertFalse(m.swap(display_ready=False))
        self.assertEqual((m.status, m.front, m.swaps, m.draw_calls), (READY, 0, 0, 1))
        self.assertFalse(m.set_auto_update(False))
        self.assertFalse(m.swap(display_ready=False))
        self.assertTrue(m.swap())
        self.assertEqual((m.status, m.front, m.swaps, m.draw_calls), (CLEAN, 1, 1, 1))
        self.assertEqual(m.pages[m.front][0], [3, 12, 12, 12])

    def test_explicit_update_is_not_repeated(self):
        m = self.model
        self.assertTrue(m.set_auto_update(True))
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        self.assertEqual(m.draw_calls, 1)

    def test_auto_swap_before_first_bob_does_not_allocate(self):
        m = BobAutoUpdateModel(4, 1, 4, backing_budget=0)
        self.assertTrue(m.set_auto_update(True))
        self.assertTrue(m.swap())
        self.assertEqual((m.front, m.swaps, m.draw_calls, m.backing_reserved), (1, 1, 0, 0))

    def test_partial_paint_cannot_present_and_clear_recovers(self):
        m = self.model
        self.assertTrue(m.put(2, 5, 1, 2, 0))
        self.assertTrue(m.set_auto_update(True))
        self.assertFalse(m.swap(inject_fault_after_pixels=1))
        self.assertEqual(m.pages[m.back][0], [3, 12, 12, 12])
        self.assertEqual((m.status, m.front, m.swaps), (DIRTY, 0, 0))
        self.assertFalse(m.swap())
        self.assertTrue(m.clear())
        self.assertEqual(m.pages[m.back][0], [12, 12, 12, 12])
        self.assertTrue(m.swap())
        self.assertEqual(m.pages[m.front][0], [3, 12, 3, 12])

    def assert_refused_before_paint(self):
        m = self.model
        self.assertTrue(m.set_auto_update(True))
        self.assertFalse(m.swap())
        self.assertEqual((m.status, m.front, m.swaps, m.draw_calls), (DIRTY, 0, 0, 0))
        self.assertEqual(m.pages[m.back][0], [12, 12, 12, 12])

    def test_invalid_bank_fails_before_presentation(self):
        self.model.erase_bank(5)
        self.assert_refused_before_paint()

    def test_missing_backing_memory_fails_before_presentation(self):
        self.model.backing_budget = 0
        self.assert_refused_before_paint()

    def test_valid_mode_changes_and_close_reset(self):
        m = self.model
        self.assertFalse(m.set_auto_update(1))
        self.assertTrue(m.set_auto_update(True))
        self.assertTrue(m.set_auto_update(False))
        self.assertTrue(m.swap())
        self.assertEqual(m.draw_calls, 0)
        self.assertTrue(m.set_auto_update(True))
        m.close()
        self.assertFalse(m.set_auto_update(True))
        self.assertFalse(m.swap())
        m.reopen()
        self.assertTrue(m.swap())
        self.assertEqual(m.draw_calls, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
