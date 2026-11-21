#!/usr/bin/env python3
"""P2a HOST model checks, not a native, Runtime or Compiler Gate."""
from __future__ import annotations
import unittest
from m19_p2a_bob_collision_model import Bob, Image, Rect, collision, collision_pairs, visible_footprint

SCREEN=Rect(0,0,320,256)

def bob(num, x, y, image=None, **kwargs):
    return Bob(num, 24, 1, x, y, image or Image(8,8), **kwargs)


class P2aCollisionHostModel(unittest.TestCase):
    def test_rectangle_interior(self):
        self.assertTrue(collision(bob(1,10,10),bob(2,17,17),screen=SCREEN))
        self.assertFalse(collision(bob(1,10,10),bob(2,18,18),screen=SCREEN))

    def test_touching_edges(self):
        self.assertFalse(collision(bob(1,10,10),bob(2,18,10),screen=SCREEN))
        self.assertFalse(collision(bob(1,10,10),bob(2,10,18),screen=SCREEN))

    def test_hotspot_coordinates(self):
        a=bob(1,20,20,hotspot_x=4,hotspot_y=3)
        self.assertEqual(a.footprint,Rect(16,17,8,8))
        self.assertTrue(collision(a,bob(2,16,17),screen=SCREEN))
        self.assertFalse(collision(a,bob(2,24,17),screen=SCREEN))

    def test_negative_and_screen_clip(self):
        a=bob(1,-7,-7)
        self.assertEqual(visible_footprint(a,SCREEN),Rect(0,0,1,1))
        self.assertTrue(collision(a,bob(2,0,0),screen=SCREEN))
        self.assertFalse(collision(a,bob(2,1,0),screen=SCREEN))
        self.assertIsNone(visible_footprint(bob(3,-20,-20),SCREEN))

    def test_global_limit(self):
        a,b=bob(1,0,0),bob(2,4,0)
        self.assertTrue(collision(a,b,screen=SCREEN))
        self.assertFalse(collision(a,b,screen=SCREEN,global_limit=Rect(0,0,4,8)))
        self.assertTrue(collision(a,b,screen=SCREEN,global_limit=Rect(4,0,1,8)))

    def test_local_limit(self):
        a,b=bob(1,0,0),bob(2,4,0)
        self.assertFalse(collision(a,b,screen=SCREEN,local_limits={1:Rect(0,0,4,8)}))
        self.assertTrue(collision(a,b,screen=SCREEN,local_limits={1:Rect(4,0,1,8)}))

    def test_off_bob(self):
        self.assertFalse(collision(bob(1,0,0,active=False),bob(2,0,0),screen=SCREEN))
        self.assertEqual(collision_pairs([bob(1,0,0,active=False),bob(2,0,0)],screen=SCREEN),[])

    def test_mask_and_rectangle_are_distinct(self):
        a=bob(1,0,0,Image(8,1,b'\x80'))
        b=bob(2,0,0,Image(8,1,b'\x01'))
        self.assertTrue(collision(a,b,screen=SCREEN,mode="rect"))
        self.assertFalse(collision(a,b,screen=SCREEN,mode="mask"))
        self.assertTrue(collision(a,bob(3,0,0,Image(8,1,b'\x80')),screen=SCREEN,mode="mask"))

    def test_unaligned_mask_width(self):
        image=Image(9,2,bytes([0,128,0,128]))
        self.assertEqual(image.stride,2)
        self.assertTrue(image.opaque(8,0))
        self.assertTrue(image.opaque(8,1))
        self.assertFalse(image.opaque(7,0))
        self.assertFalse(image.opaque(9,0))
        self.assertTrue(collision(bob(1,0,0,image),bob(2,8,1,Image(1,1)),screen=SCREEN,mode="mask"))

    def test_clipped_mask(self):
        a=bob(1,-7,0,Image(8,1,b'\x01'))
        self.assertTrue(collision(a,bob(2,0,0,Image(8,1,b'\x80')),screen=SCREEN,mode="mask"))
        self.assertFalse(collision(a,bob(3,1,0,Image(8,1,b'\x80')),screen=SCREEN,mode="mask"))

    def test_shared_image_not_mutated(self):
        image=Image(8,1,b'\x80')
        a,b=bob(1,0,0,image),bob(2,0,0,image)
        self.assertTrue(collision(a,b,screen=SCREEN,mode="mask"))
        self.assertIs(a.image,b.image)
        self.assertEqual(image.mask,b'\x80')

    def test_missing_mask_is_opaque(self):
        self.assertTrue(collision(bob(1,0,0,Image(1,1)),bob(2,0,0,Image(1,1)),screen=SCREEN,mode="mask"))
        self.assertFalse(collision(bob(1,0,0,Image(1,1,b'\x00')),bob(2,0,0,Image(1,1)),screen=SCREEN,mode="mask"))

    def test_stable_pairs_sorted(self):
        bs=[bob(3,0,0),bob(1,0,0),bob(2,0,0)]
        self.assertEqual(collision_pairs(bs,screen=SCREEN),[(1,2),(1,3),(2,3)])
        self.assertEqual(collision_pairs(reversed(bs),screen=SCREEN),[(1,2),(1,3),(2,3)])

    def test_pairs_exclude_off_and_nonoverlap(self):
        bs=[bob(4,15,0),bob(2,0,0),bob(1,0,0),bob(3,0,0,active=False)]
        self.assertEqual(collision_pairs(bs,screen=SCREEN,mode="mask"),[(1,2)])

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError): Rect(0,0,0,1)
        with self.assertRaises(ValueError): Image(9,1,b'\x80')
        with self.assertRaises(ValueError): bob(65,0,0)
        with self.assertRaises(ValueError): Bob(1,3,1,0,0,Image(1,1))

    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError): collision_pairs([bob(1,0,0),bob(1,0,0)],screen=SCREEN)
        with self.assertRaises(ValueError): collision(bob(1,0,0),bob(1,1,1),screen=SCREEN)

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError): collision(bob(1,0,0),bob(2,0,0),screen=SCREEN,mode="unsupported")


if __name__=="__main__":
    unittest.main(verbosity=2)
