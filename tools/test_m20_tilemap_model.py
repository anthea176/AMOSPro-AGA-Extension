#!/usr/bin/env python3
"""M20 P0 independent full-frame oracle and two-buffer regression tests.

HOST-ONLY: not 68020, not an AMOS runtime test, not a native performance test.
"""
import unittest
from m20_tilemap_model import (
    TILE, MAX_EDITS, Bob, DoubleBufferTilemap, TileMap, planar_bytes, DIRTY
)

def fixture(cols=10, rows=9, depth=8):
    palette = 1 << depth
    tiles = tuple(bytes(
        (n * 7 + x * 3 + y * 5) % palette
        for y in range(TILE) for x in range(TILE)
    ) for n in range(5))
    indices = bytearray((x + 3 * y) % len(tiles)
                        for y in range(rows) for x in range(cols))
    return TileMap(cols, rows, tiles, indices, depth)

def oracle(world, cx, cy, width, height, bobs=()):
    """Full paint with an independent tile-array address calculation."""
    out = bytearray(width * height)
    for y in range(height):
        wy = y + cy
        ty, py = divmod(wy, TILE)
        for x in range(width):
            tx, px = divmod(x + cx, TILE)
            tile = world.ids[ty * world.cols + tx]
            out[y * width + x] = world.tileset[tile][py * TILE + px]
    for b in bobs:
        for y in range(max(0, b.y), min(height, b.y + b.h)):
            for x in range(max(0, b.x), min(width, b.x + b.w)):
                out[y * width + x] = b.pen
    return bytes(out)

def step(m, cx, cy, bobs=()):
    page = m.pages[m.back]
    if page.snapshot is not None:
        assert m.clear(), m.last_error
    stats = m.draw_map(cx, cy)
    assert stats is not None, m.last_error
    clean = oracle(m.world, cx, cy, m.width, m.height)
    assert bytes(m.pages[m.back].pixels) == clean
    assert m.update_bobs(bobs), m.last_error
    assert m.pages[m.back].snapshot == clean
    assert m.swap(), m.last_error
    assert m.front_pixels() == oracle(m.world, cx, cy, m.width, m.height, bobs)
    return stats

class M20P0(unittest.TestCase):
    def test_planar_sizes(self):
        self.assertEqual(planar_bytes(320, 256, 8), 81920)
        self.assertEqual(2 * planar_bytes(320, 256, 8), 163840)
        self.assertEqual(planar_bytes(16, 16, 8), 256)
        self.assertEqual(256 * planar_bytes(16, 16, 8), 65536)
        self.assertEqual(len(fixture(64, 64).ids), 4096)
        self.assertEqual(planar_bytes(321, 257, 1), 10794)
        for args in ((0, 256, 8), (320, 0, 8), (320, 256, 9)):
            with self.assertRaises(ValueError):
                planar_bytes(*args)

    def test_two_pages_have_independent_camera(self):
        m = DoubleBufferTilemap(fixture(), 48, 32)
        a, b, c, d = [step(m, x, 0) for x in range(4)]
        self.assertTrue(a.full and b.full)
        self.assertFalse(c.full or d.full)
        self.assertEqual([a.page, b.page, c.page, d.page], [1, 0, 1, 0])
        self.assertEqual(c.repainted, 64)
        self.assertEqual(c.scrolled, 46 * 32)
        self.assertEqual(d.repainted, 64)

    def test_diagonal_scroll_dirty_strips(self):
        m = DoubleBufferTilemap(fixture(), 50, 35)
        step(m, 10, 10)
        step(m, 15, 13)
        t = step(m, 17, 18)
        self.assertFalse(t.full)
        self.assertEqual(t.repainted, 50 * 35 - 43 * 27)
        self.assertEqual(t.scrolled, 43 * 27)
        self.assertEqual(sum(r.area for r in t.dirty_rects), t.repainted)
        self.assertLessEqual(len(t.dirty_rects), 4)

    def test_big_jump_forces_full_redraw(self):
        m = DoubleBufferTilemap(fixture(20, 20), 48, 32)
        step(m, 0, 0)
        step(m, 1, 0)
        t = step(m, 48, 32)
        self.assertTrue(t.full)
        self.assertEqual((t.repainted, t.scrolled), (48 * 32, 0))

    def test_edit_reaches_both_physical_pages(self):
        world = fixture()
        m = DoubleBufferTilemap(world, 48, 32)
        step(m, 0, 0)
        step(m, 0, 0)
        self.assertTrue(world.edit(0, 0, (world.ids[0] + 1) % 5))
        a, b, c = (step(m, 0, 0) for _ in range(3))
        self.assertFalse(a.full or b.full or c.full)
        self.assertEqual((a.repainted, b.repainted, c.repainted), (256, 256, 0))

    def test_outside_view_edit_needs_no_visible_redraw(self):
        world = fixture()
        m = DoubleBufferTilemap(world, 48, 32)
        step(m, 0, 0)
        step(m, 0, 0)
        pos = 7 * world.cols + 7
        world.edit(7, 7, (world.ids[pos] + 1) % 5)
        t = step(m, 0, 0)
        self.assertEqual((t.repainted, t.scrolled), (0, 48 * 32))

    def test_pruned_edit_history_falls_back_to_full(self):
        world = fixture()
        m = DoubleBufferTilemap(world, 48, 32)
        step(m, 0, 0)
        step(m, 0, 0)
        for _ in range(MAX_EDITS + 1):
            world.edit(0, 0, (world.ids[0] + 1) % 5)
        t = step(m, 0, 0)
        self.assertTrue(t.full)
        self.assertEqual(t.repainted, 48 * 32)

    def test_opaque_palette_zero_and_removed_bob(self):
        world = TileMap(4, 4, (bytes(256), bytes([15]) * 256),
                        bytearray([1] * 16), depth=4)
        m = DoubleBufferTilemap(world, 32, 32)
        step(m, 0, 0, (Bob(0, 0, 6, 6, 8),))
        step(m, 0, 0, (Bob(0, 0, 6, 6, 8),))
        world.edit(0, 0, 0)
        step(m, 0, 0)
        step(m, 0, 0)
        self.assertEqual(m.front_pixels()[0], 0)
        self.assertEqual(m.front_pixels()[20], 15)

    def test_moving_bob_leaves_no_ghost_on_scrolling_pages(self):
        m = DoubleBufferTilemap(fixture(), 64, 40)
        for n in range(20):
            bob = Bob((n * 5) % 60 - 3, (n * 4) % 35 - 2, 7, 6, 255)
            step(m, n % 13, n % 8, (bob,))
        self.assertEqual(m.swaps, 20)

    def test_dirty_never_swaps_and_closed_screen_resets(self):
        m = DoubleBufferTilemap(fixture(), 48, 32)
        self.assertFalse(m.swap())
        self.assertEqual((m.status, m.swaps), (DIRTY, 0))
        m.close()
        m.reopen()
        self.assertIsNotNone(m.draw_map(0, 0))
        self.assertFalse(m.update_bobs((Bob(1, 1, 1, 1, 256),)))
        self.assertEqual(m.status, DIRTY)
        self.assertFalse(m.swap())
        m.close()
        m.reopen()
        self.assertIsNone(m.draw_map(-1, 0))

    def test_cannot_redraw_over_uncleared_bobs(self):
        m = DoubleBufferTilemap(fixture(), 48, 32)
        self.assertFalse(m.clear())
        m.close()
        m.reopen()
        step(m, 0, 0)
        step(m, 0, 0)
        self.assertIsNone(m.draw_map(1, 0))
        self.assertEqual(m.status, DIRTY)
        self.assertFalse(m.swap())

    def test_full_320x256_geometry_pixel_oracle(self):
        m = DoubleBufferTilemap(fixture(64, 64), 320, 256)
        a = step(m, 3, 4, (Bob(4, 8, 32, 24, 255),))
        b = step(m, 7, 6, (Bob(8, 10, 32, 24, 255),))
        c = step(m, 8, 7, (Bob(6, 12, 32, 24, 255),))
        self.assertTrue(a.full and b.full)
        self.assertFalse(c.full)
        self.assertEqual((c.repainted, c.scrolled),
                         (320 * 256 - 315 * 253, 315 * 253))

    def test_405_frames_moving_camera_dynamic_tiles_and_bobs(self):
        world = fixture(12, 12)
        m = DoubleBufferTilemap(world, 48, 32)
        for n in range(405):
            if n % 19 == 0:
                p = ((n // 19) * 7) % len(world.ids)
                world.edit(p % world.cols, p // world.cols,
                           (world.ids[p] + 1) % len(world.tileset))
            cx = (n * 3) % (world.width - 48 + 1)
            cy = (n * 2) % (world.height - 32 + 1)
            b = Bob((n * 7) % 51 - 3, (n * 5) % 35 - 2, 8, 6, 201)
            step(m, cx, cy, (b,))
        self.assertEqual(m.swaps, 405)

if __name__ == "__main__":
    unittest.main(verbosity=2)
