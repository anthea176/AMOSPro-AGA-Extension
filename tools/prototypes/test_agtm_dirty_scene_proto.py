#!/usr/bin/env python3
"""Correctness and lifecycle regressions for the AGTM 2-page host prototype."""
import random
import unittest

from agtm_format_proto import AGTMError, render_reference
from agtm_render_bench import fixture, span_frame
from agtm_dirty_scene_proto import (
    Actor, MutableMap, TwoPageScene, incremental_background,
    MAX_EDITS, compose_actors,
)


class AGTMDirtySceneTests(unittest.TestCase):
    def scene(self, width=192, height=192, layers=2):
        base, tiles = fixture(cols=64, rows=64, layers=layers)
        world = MutableMap(base)
        return TwoPageScene(world, tiles, width, height)

    def oracle(self, scene, cx, cy, actors=()):
        background = render_reference(scene.world, scene.tiles,
                                      cx, cy, scene.width, scene.height)
        return compose_actors(background, tuple(actors), scene.width, scene.height)

    def check_step(self, scene, cx, cy, actors=()):
        old_front = scene.pages[scene.front].displayed
        stats = scene.prepare(cx, cy, tuple(actors))
        self.assertEqual(scene.pages[scene.front].displayed, old_front)
        result = scene.swap()
        self.assertEqual(result, self.oracle(scene, cx, cy, actors))
        return stats

    def test_frame_initialization_and_two_page_cameras(self):
        s = self.scene()
        self.assertTrue(self.check_step(s, 11, 12).full_redraw)
        self.assertTrue(self.check_step(s, 12, 12).full_redraw)
        self.assertFalse(self.check_step(s, 13, 12).full_redraw)
        self.assertFalse(self.check_step(s, 14, 12).full_redraw)
        self.assertEqual(s.pages[0].camera, (14, 12))
        self.assertEqual(s.pages[1].camera, (13, 12))

    def test_dirty_ground_overlay_and_pen_zero(self):
        s = self.scene(layers=2)
        self.check_step(s, 7, 8)
        self.check_step(s, 8, 8)
        self.assertTrue(s.world.edit(0, 4, 3, 5))
        self.assertTrue(s.world.edit(1, 4, 3, 7))
        self.assertEqual(s.world.revision, 2)
        st = self.check_step(s, 9, 8, (Actor(0, 0, 2, 2, 0),))
        self.assertFalse(st.full_redraw)
        self.assertEqual(st.tile_edits, 1)  # same cell, two layers
        self.assertEqual(s.pages[s.front].displayed[0], 0)
        st2 = self.check_step(s, 10, 8)
        self.assertEqual(st2.tile_edits, 1)
        self.assertFalse(s.world.edit(1, 4, 3, 7))
        self.assertEqual(s.world.revision, 2)

    def test_offscreen_edits_do_not_draw(self):
        s = self.scene()
        self.check_step(s, 3, 4)
        self.check_step(s, 4, 4)
        s.world.edit(0, 50, 50, 6)
        a = self.check_step(s, 5, 4)
        self.assertEqual(a.tile_edits, 0)
        b = self.check_step(s, 6, 4)
        self.assertEqual(b.tile_edits, 0)

    def test_edited_partially_visible_cell(self):
        s = self.scene(width=40, height=37)
        self.check_step(s, 15, 15)
        self.check_step(s, 17, 16)
        s.world.edit(1, 1, 1, 7)
        stats = self.check_step(s, 18, 17)
        self.assertEqual(stats.tile_edits, 1)
        self.assertEqual(stats.edit_pixels, 14 * 15)

    def test_edit_history_pruned_falls_back(self):
        s = self.scene()
        self.check_step(s, 17, 21)
        self.check_step(s, 18, 22)
        for i in range(MAX_EDITS + 1):
            x, y = (i % 60), ((i // 60) + 30)
            old = s.world.layers[0][y * s.world.cols + x]
            s.world.edit(0, x, y, (old + 1) % s.world.tile_count)
        self.assertEqual(len(s.world.edits), MAX_EDITS)
        stats = self.check_step(s, 19, 23)
        self.assertTrue(stats.history_lost)
        self.assertTrue(stats.full_redraw)

    def test_full_fallback_after_big_jump(self):
        s = self.scene(width=64, height=48)
        self.check_step(s, 0, 0)
        self.check_step(s, 1, 0)
        st = self.check_step(s, 300, 100)
        self.assertTrue(st.full_redraw)

    def test_preflight_failure_never_swaps(self):
        s = self.scene()
        self.check_step(s, 7, 9)
        expected = s.pages[s.front].displayed
        with self.assertRaises(AGTMError):
            s.prepare(1000, 1000)
        self.assertEqual(s.pages[s.front].displayed, expected)
        with self.assertRaises(AGTMError):
            s.swap()
        s.abort()
        self.check_step(s, 8, 9)
        with self.assertRaises(AGTMError):
            s.swap()
        with self.assertRaises(AGTMError):
            s.prepare(7, 9, (Actor(1, 1, -1, 3, 0),))
        s.abort()

    def test_actors_removed_leave_no_ghosts(self):
        s = self.scene()
        for i in range(20):
            actors = (Actor(13 + i, 24, 19, 17, 0),
                      Actor(13, 10 + i, 27, 20, 255)) if i % 2 else ()
            self.check_step(s, 13 + i, 14 + i, actors)

    def test_random_120_frames_two_pages_edits_and_actors(self):
        s = self.scene(width=192, height=192, layers=3)
        rng = random.Random(7262026)
        for i in range(120):
            for _ in range(i % 4):
                layer = rng.randrange(3)
                x, y = rng.randrange(64), rng.randrange(64)
                tile_id = rng.randrange(s.world.tile_count)
                s.world.edit(layer, x, y, tile_id)
            cx = 19 + (i * 7) % 400
            cy = 11 + (i * 9) % 400
            actors = tuple(Actor(rng.randrange(-15, 180), rng.randrange(-15, 180),
                                 17, 21, rng.randrange(256))
                           for _ in range(i % 4))
            self.check_step(s, cx, cy, actors)

    def test_no_spurious_redraw_with_stable_camera(self):
        s = self.scene()
        self.check_step(s, 7, 9)
        self.check_step(s, 7, 9)
        st = self.check_step(s, 7, 9)
        self.assertFalse(st.full_redraw)
        self.assertEqual(st.bands_pixels, 0)
        self.assertEqual(st.tile_edits, 0)

    def test_scroll_dirty_matches_full_reference(self):
        base, tiles = fixture(cols=64, rows=64, layers=2)
        m = MutableMap(base)
        cx, cy = 13, 15
        old = span_frame(m, tiles, cx, cy, 320, 256)
        for dx, dy in [(1, 0), (-8, 5), (16, -8), (0, 0)]:
            old = span_frame(m, tiles, cx, cy, 320, 256)
            changed = [(2, 2), (3, 4), (40, 40)]
            revision = m.revision
            for tx, ty in changed:
                old_id = m.layers[0][ty * m.cols + tx]
                m.edit(0, tx, ty, (old_id + 1) % m.tile_count)
            frame, _ = incremental_background(m, tiles, old, (cx, cy),
                                               revision, (cx + dx, cy + dy),
                                               320, 256)
            self.assertEqual(frame, render_reference(m, tiles, cx + dx, cy + dy, 320, 256))


if __name__ == '__main__':
    unittest.main()
