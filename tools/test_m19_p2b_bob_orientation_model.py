#!/usr/bin/env python3
"""Verify per-Bob views against asymmetric AGBO pixels and the P2a oracle."""

from dataclasses import replace
import unittest

from m19_p0a_multi_bob_abk import empty_bank, pack_pixels, parse_payload, put_image, set_hotspot
from m19_p2a_bob_collision_model import Bob, Image, Rect, collision, visible_footprint
from m19_p2b_bob_orientation_model import OrientedImage


class BobOrientationTests(unittest.TestCase):
    def test_all_orientations_share_one_agbo_image(self):
        payload = put_image(empty_bank(), 1, 3, 2, 8, bytes((0, 2, 4, 8, 16, 128)),
                            visibility=bytes((1, 0, 1, 0, 1, 1)))
        payload = set_hotspot(payload, 1, -1, 2)
        bank = parse_payload(payload)
        image = bank.image(1)
        expected = (
            (False, False, (0, 2, 4, 8, 16, 128), (1, 0, 1, 0, 1, 1), (-1, 2)),
            (True, False, (4, 2, 0, 128, 16, 8), (1, 0, 1, 1, 1, 0), (3, 2)),
            (False, True, (8, 16, 128, 0, 2, 4), (0, 1, 1, 1, 0, 1), (-1, -1)),
            (True, True, (128, 16, 8, 4, 2, 0), (1, 1, 0, 1, 0, 1), (3, -1)),
        )
        for bob_id, (horizontal, vertical, colours, mask, hotspot) in enumerate(expected, 1):
            with self.subTest(horizontal=horizontal, vertical=vertical):
                view = OrientedImage(image, horizontal, vertical)
                self.assertIs(view.source, image)
                pixels = [(x, y) for y in range(2) for x in range(3)]
                self.assertEqual(tuple(view.colour(x, y) for x, y in pixels), colours)
                self.assertEqual(tuple(view.visible(x, y) for x, y in pixels), mask)
                bob = view.collision_bob(bob_id, 26, 10, 10)
                self.assertEqual((bob.hotspot_x, bob.hotspot_y), hotspot)
                self.assertEqual((bob.x, bob.y, bob.bank_id, bob.image_id), (10, 10, 26, 1))
        self.assertEqual(parse_payload(payload), bank)

    def test_reflected_hotspot_keeps_zero_pixel_opaque(self):
        image = replace(pack_pixels(1, 4, 2, 4, bytes((1, 2, 3, 4, 5, 0, 7, 8))),
                        hotspot_x=1, hotspot_y=1)
        view = OrientedImage(image, True, True)
        bob = view.collision_bob(1, 26, 5, 6)
        self.assertEqual((bob.origin_x, bob.origin_y), (3, 6))
        self.assertEqual(view.colour(2, 0), 0)
        self.assertTrue(view.visible(2, 0))
        self.assertIsNone(bob.image.mask)
        self.assertTrue(collision(bob, Bob(2, 26, 2, 5, 6, Image(1, 1)),
                                  screen=Rect(0, 0, 16, 16), mode="mask"))

    def test_mask_reflection_respects_agbo_row_padding(self):
        for width in (1, 15, 16, 17, 31, 32, 37):
            with self.subTest(width=width):
                image = pack_pixels(1, width, 2, 8, bytes([128] + [0] * (2 * width - 1)),
                                    visibility=bytes([1] + [0] * (2 * width - 1)))
                view = OrientedImage(image, True, True)
                bob = view.collision_bob(1, 26, 0, 0)
                self.assertEqual(view.colour(width - 1, 1), 128)
                self.assertEqual([sum(bob.image.opaque(x, y) for x in range(width))
                                  for y in range(2)], [0, 1])
                self.assertTrue(bob.image.opaque(width - 1, 1))
                self.assertFalse(bob.image.opaque(width, 1))

    def test_collision_uses_same_orientation_and_clipping_as_pixels(self):
        image = replace(pack_pixels(1, 3, 1, 1, b"\x01\x00\x00",
                                    visibility=b"\x01\x00\x00"), hotspot_x=1)
        normal = OrientedImage(image).collision_bob(1, 26, 1, 0)
        flipped = OrientedImage(image, horizontal=True).collision_bob(1, 26, 1, 0)
        target = Bob(2, 26, 2, 2, 0, Image(1, 1))
        screen = Rect(0, 0, 4, 2)
        self.assertEqual(normal.footprint, flipped.footprint)
        self.assertTrue(collision(normal, target, screen=screen, mode="rect"))
        self.assertFalse(collision(normal, target, screen=screen, mode="mask"))
        self.assertTrue(collision(flipped, target, screen=screen, mode="mask"))
        self.assertFalse(collision(flipped, target, screen=screen, mode="mask",
                                   local_limits={1: Rect(0, 0, 2, 1)}))
        self.assertFalse(collision(flipped, target, screen=screen, mode="rect",
                                   global_limit=Rect(0, 0, 2, 1)))

    def test_signed_hotspot_reflection_never_wraps_to_visible_origin(self):
        image = replace(pack_pixels(1, 2, 1, 1, b"\x00\x00"), hotspot_x=-32768)
        bob = OrientedImage(image, horizontal=True).collision_bob(1, 26, -32767, 0)
        self.assertEqual((bob.hotspot_x, bob.origin_x), (32769, -65536))
        self.assertIsNone(visible_footprint(bob, Rect(0, 0, 320, 256)))

    def test_outside_pixel_is_rejected_in_either_orientation(self):
        image = pack_pixels(1, 1, 1, 1, b"\x00")
        view = OrientedImage(image, horizontal=True, vertical=True)
        with self.assertRaises(IndexError):
            view.colour(-1, 0)
        with self.assertRaises(IndexError):
            view.visible(0, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
