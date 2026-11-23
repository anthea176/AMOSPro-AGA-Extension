#!/usr/bin/env python3
"""Deterministic correctness tests for the host renderer benchmark."""
import unittest

from agtm_format_proto import render_reference
from agtm_render_bench import fixture, span_frame, scroll_frame, measure


class TilemapRenderBenchTests(unittest.TestCase):
    def test_span_matches_pixel_oracle_for_misaligned_camera(self):
        for layers in (1, 2, 3):
            tm, tiles = fixture(layers=layers)
            for camera in ((0, 0), (1, 8), (15, 15), (16, 32), (37, 43)):
                for viewport in ((31, 23), (192, 192)):
                    with self.subTest(layers=layers, camera=camera, view=viewport):
                        cx, cy = camera
                        w, h = viewport
                        self.assertEqual(span_frame(tm, tiles, cx, cy, w, h),
                                         render_reference(tm, tiles, cx, cy, w, h))

    def test_scroll_four_directions_diagonals_and_jumps(self):
        for layers in (1, 2):
            tm, tiles = fixture(layers=layers)
            old_x, old_y = 41, 57
            view = (43, 35)
            previous = span_frame(tm, tiles, old_x, old_y, *view)
            for dx in (-45, -16, -8, -1, 0, 1, 8, 16, 45):
                for dy in (-37, -16, -1, 0, 1, 16, 37):
                    cam_x, cam_y = old_x + dx, old_y + dy
                    if cam_x < 0 or cam_y < 0:
                        continue
                    with self.subTest(layers=layers, dx=dx, dy=dy):
                        actual = scroll_frame(tm, tiles, previous, old_x, old_y,
                                              cam_x, cam_y, *view)
                        expected = render_reference(tm, tiles, cam_x, cam_y, *view)
                        self.assertEqual(actual, expected)

    def test_alternating_two_physical_page_histories(self):
        tm, tiles = fixture(layers=2)
        view = (192, 192)
        cameras = [(13 + step * 3, 11 + step * 2) for step in range(12)]
        pages = [(None, None), (None, None)]
        for step, (cx, cy) in enumerate(cameras):
            page = step % 2
            old, old_camera = pages[page]
            if old_camera is None:
                frame = span_frame(tm, tiles, cx, cy, *view)
            else:
                frame = scroll_frame(tm, tiles, old, *old_camera,
                                     cx, cy, *view)
            self.assertEqual(frame, render_reference(tm, tiles, cx, cy, *view))
            pages[page] = (frame, (cx, cy))

    def test_invalid_previous_size_falls_back(self):
        tm, tiles = fixture(layers=2)
        result = scroll_frame(tm, tiles, b"wrong", 10, 10, 13, 15, 37, 21)
        self.assertEqual(result, render_reference(tm, tiles, 13, 15, 37, 21))

    def test_benchmark_minimal_case_contains_checksums_and_raw_passes(self):
        result = measure(1, 1, cases=[(32, 24, 2, 1, 0)])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["new_pixels"], 24)
        for value in result["results"][0]["timing"].values():
            self.assertEqual(len(value["pass_ms"]), 1)
            self.assertGreater(value["median_ms"], 0)


if __name__ == "__main__":
    unittest.main()
