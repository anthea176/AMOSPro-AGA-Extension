#!/usr/bin/env python3
"""P2c planar write selection, transparency and the two-page contract."""

import unittest

from m19_bob_clear_update_model import BobImage
from m19_p2c_bob_planes_model import BobPlanesModel, compose_planes


class BobPlanesTests(unittest.TestCase):
    def frame(self, depth=8):
        model = BobPlanesModel(3, 1, depth)
        self.assertTrue(model.install_bank(10, {1: BobImage(((0, 0, 1),), depth,
                                                           ((True, False, True),))}))
        self.assertTrue(model.put(1, 10, 1, 0, 0))
        return model

    def test_all_plane_masks_against_independent_bit_selection(self):
        for mask in range(256):
            for source, background in ((0, 255), (255, 0), (0xA5, 0x3C), (0x12, 0xC1)):
                expected = sum(((source if mask & (1 << plane) else background)
                                & (1 << plane)) for plane in range(8))
                self.assertEqual(compose_planes(source, background, mask), expected)

    def test_opaque_zero_and_transparent_zero_are_distinct(self):
        model = self.frame()
        model.pages[1][0] = [255, 255, 255]
        self.assertTrue(model.set_planes(1, 0x81))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[1][0], [126, 255, 127])
        self.assertEqual(model.pages[0][0], [0, 0, 0])

    def test_default_zero_and_high_bits_on_shallow_screen(self):
        for depth in (1, 4, 8):
            for setting in (None, 0, 0x80, 255):
                with self.subTest(depth=depth, setting=setting):
                    model = self.frame(depth)
                    background = (1 << depth) - 1
                    model.pages[1][0] = [background] * 3
                    if setting is not None:
                        self.assertTrue(model.set_planes(1, setting))
                    self.assertTrue(model.update())
                    effective = (255 if setting is None else setting) & background
                    self.assertEqual(model.pages[1][0],
                                     [background ^ effective, background,
                                      (background ^ effective) | 1])

    def test_overlapping_slots_keep_their_own_selection_and_clip(self):
        model = self.frame()
        self.assertTrue(model.install_bank(11, {1: BobImage(((0x81, 0x80),), 8)}))
        self.assertTrue(model.put(1, 11, 1, 0, 0))
        self.assertTrue(model.put(2, 11, 1, -1, 0))
        self.assertTrue(model.set_planes(1, 0x01))
        self.assertTrue(model.set_planes(2, 0x80))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[1][0], [0x81, 0, 0])

    def test_mask_change_and_clear_restore_each_physical_page(self):
        model = self.frame()
        model.pages[0][0] = [0x28, 0x39, 0x4A]
        model.pages[1][0] = [0x85, 0x96, 0xA7]
        self.assertTrue(model.set_planes(1, 0x80))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[1][0], [0x05, 0x96, 0x27])
        self.assertTrue(model.swap())
        self.assertTrue(model.set_planes(1, 0x01))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[0][0], [0x28, 0x39, 0x4B])
        self.assertTrue(model.swap())
        self.assertTrue(model.clear())
        self.assertEqual(model.pages[1][0], [0x85, 0x96, 0xA7])
        self.assertTrue(model.swap())
        self.assertTrue(model.clear())
        self.assertEqual(model.pages[0][0], [0x28, 0x39, 0x4A])

    def test_invalid_mask_leaves_mode_and_failed_frame_cannot_swap(self):
        model = self.frame()
        model.pages[1][0] = [255] * 3
        self.assertTrue(model.set_planes(1, 0x80))
        for slot, mask in ((0, 1), (2, 1), (1, -1), (1, 256), (1, True)):
            self.assertFalse(model.set_planes(slot, mask))
        self.assertFalse(model.update(inject_fault_after_pixels=1))
        self.assertEqual(model.pages[1][0], [127, 255, 255])
        self.assertFalse(model.swap())
        self.assertTrue(model.clear())
        self.assertEqual(model.pages[1][0], [255, 255, 255])

    def test_selection_persists_for_slot_and_resets_after_close(self):
        model = self.frame()
        self.assertTrue(model.set_planes(1, 0))
        self.assertTrue(model.off(1))
        self.assertFalse(model.set_planes(1, 255))
        self.assertTrue(model.put(1, 10, 1, 0, 0))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[1][0], [0, 0, 0])
        model.close()
        model.reopen()
        self.assertTrue(model.put(1, 10, 1, 0, 0))
        self.assertTrue(model.update())
        self.assertEqual(model.pages[1][0], [0, 0, 1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
