#!/usr/bin/env python3
"""HOST-only AGTM dirty-tile + scrolling timing, not a 68020/AGA result."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
import statistics

from agtm_dirty_scene_proto import MutableMap, incremental_background
from agtm_render_bench import fixture, span_frame, time_variant
from agtm_format_proto import render_reference


DEFAULT_CASES = (
    (0, 1, 0, 2), (1, 1, 0, 2), (4, 1, 0, 2),
    (16, 1, 0, 2), (64, 1, 0, 2), (128, 1, 0, 2),
    (129, 1, 0, 2), (1, 8, 8, 2), (16, 16, 0, 2),
    (64, 16, 0, 2), (16, 1, 0, 1),
)


def prepare_case(n_edits, dx, dy, layers):
    width, height = 320, 256
    old_x, old_y = 37, 41
    cam_x, cam_y = old_x + dx, old_y + dy
    base, tiles = fixture(cols=64, rows=64, layers=layers)
    world = MutableMap(base)
    old_frame = span_frame(world, tiles, old_x, old_y, width, height)
    old_revision = world.revision
    tx_first, ty_first = cam_x // 16, cam_y // 16
    tx_count = (cam_x + width - 1) // 16 - tx_first + 1
    ty_count = (cam_y + height - 1) // 16 - ty_first + 1
    if n_edits > tx_count * ty_count:
        raise ValueError("not enough visible cells for requested edits")
    for i in range(n_edits):
        tx = tx_first + (i % tx_count)
        ty = ty_first + (i // tx_count)
        index = ty * world.cols + tx
        layer = 1 if layers > 1 and i % 3 == 0 else 0
        previous = world.layers[layer][index]
        world.edit(layer, tx, ty, (previous + 3) % world.tile_count)
    baseline = lambda: span_frame(world, tiles, cam_x, cam_y, width, height)
    dirty = lambda: incremental_background(
        world, tiles, old_frame, (old_x, old_y), old_revision,
        (cam_x, cam_y), width, height)
    expected = render_reference(world, tiles, cam_x, cam_y, width, height)
    actual, stats = dirty()
    assert expected == baseline() == actual, "pixel mismatch"
    return baseline, dirty, stats, hashlib.sha256(expected).hexdigest()


def benchmark(repeats=4, passes=5, cases=DEFAULT_CASES):
    if repeats < 1 or passes < 1:
        raise ValueError("positive repeats/passes required")
    results = []
    for n_edits, dx, dy, layers in cases:
        full_op, incr_op, stats, checksum = prepare_case(n_edits, dx, dy, layers)
        operations = {
            "full_tile_spans": full_op,
            "incremental_dirty": lambda: incr_op()[0],
        }
        batches = {name: [] for name in operations}
        for i in range(passes):
            names = list(operations)
            if i % 2:
                names.reverse()
            for name in names:
                median_ms, _ = time_variant(operations[name], repeats, 1)
                batches[name].append(median_ms)
        medians = {name: round(statistics.median(vals), 6)
                   for name, vals in batches.items()}
        results.append({
            "edits": n_edits, "layers": layers,
            "camera_delta": [dx, dy], "pixel_sha256": checksum,
            "full_redraw_fallback": stats.full_redraw,
            "history_lost": stats.history_lost,
            "copied_pixels": stats.copied_pixels,
            "band_pixels": stats.bands_pixels,
            "visible_edited_cells": stats.tile_edits,
            "edited_pixels_including_overlap": stats.edit_pixels,
            "median_ms": medians, "passes_ms": batches,
            "full_over_incremental": round(
                medians["full_tile_spans"] / medians["incremental_dirty"], 4),
        })
    return {
        "kind": "HOST_PYTHON_ONLY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "machine": platform.platform(),
        "python": platform.python_version(),
        "clock": "perf_counter_ns via agtm_render_bench.time_variant",
        "view": [320, 256],
        "repeats_per_pass": repeats, "passes": passes,
        "method": "AB/BA passes; map edits and previous-frame preparation outside timing",
        "verified": "oracle pixel comparison before all timed cases",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--passes", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.repeats, args.passes), indent=2))


if __name__ == "__main__":
    main()
