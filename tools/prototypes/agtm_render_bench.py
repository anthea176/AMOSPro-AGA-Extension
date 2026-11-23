#!/usr/bin/env python3
"""AGTM explorative HOST-only render benchmark (Python, not MC68020/AGA).

Methods: independent pixel oracle, tile-row span copy, byte-buffer scroll +
repaint exposed bands. Every timing case first verifies pixel equivalence.
No hardware Blitter/Chip RAM, DMA, VBL, OS Safe/Disp, or AMOS APIs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import json
import platform
import statistics
import time

from agtm_format_proto import AGTMMap, TILE_EDGE, render_reference


def fixture(cols=64, rows=64, layers=2, tile_count=64):
    """Original deterministic test assets; no Fer & Flamme content."""
    tiles = tuple(bytes(
        0 if (index + x * 3 + y * 7) % 17 == 0
        else (index * 11 + x * 7 + y * 13) & 255
        for y in range(TILE_EDGE) for x in range(TILE_EDGE)
    ) for index in range(tile_count))
    ground = bytes((x * 3 + y * 7) % tile_count
                   for y in range(rows) for x in range(cols))
    all_layers = [ground]
    for layer in range(1, layers):
        all_layers.append(bytes(
            ((x * 11 + y * 17 + layer * 5) % (tile_count - 1) + 1)
            if (x * 13 + y * 7 + layer * 3) % 11 == 0 else 0
            for y in range(rows) for x in range(cols)
        ))
    return AGTMMap(cols, rows, tile_count, tuple(all_layers)), tiles


def paint_rect(tilemap, tiles, output, cam_x, cam_y, width, x0, y0, rw, rh):
    """Copy tile scanline spans, overlay transparent pixels when needed.

    Trusted internal operation: caller validates camera and regions up front.
    This prototype deliberately uses Python bytearray slices rather than DMA.
    """
    cols = tilemap.cols
    layers = tilemap.layers
    x_end = x0 + rw
    for dy in range(y0, y0 + rh):
        world_y = cam_y + dy
        cell_y = world_y >> 4
        tile_line = (world_y & 15) << 4
        out_row = dy * width
        dx = x0
        while dx < x_end:
            world_x = cam_x + dx
            cell_x = world_x >> 4
            inner_x = world_x & 15
            run = min(TILE_EDGE - inner_x, x_end - dx)
            cell = cell_y * cols + cell_x
            tile_row_start = tile_line + inner_x
            target = out_row + dx
            base = tiles[layers[0][cell]]
            output[target:target + run] = base[tile_row_start:tile_row_start + run]
            for top in layers[1:]:
                tile_id = top[cell]
                if tile_id == 0:
                    continue
                overlay = tiles[tile_id][tile_row_start:tile_row_start + run]
                if 0 not in overlay:
                    output[target:target + run] = overlay
                else:
                    for k, pen in enumerate(overlay):
                        if pen:
                            output[target + k] = pen
            dx += run


def span_frame(tilemap, tiles, cam_x, cam_y, width, height):
    if (width <= 0 or height <= 0 or cam_x < 0 or cam_y < 0 or
            cam_x + width > tilemap.cols * TILE_EDGE or
            cam_y + height > tilemap.rows * TILE_EDGE):
        raise ValueError("invalid viewport")
    out = bytearray(width * height)
    paint_rect(tilemap, tiles, out, cam_x, cam_y, width, 0, 0, width, height)
    return bytes(out)


def scroll_frame(tilemap, tiles, old_frame, old_x, old_y,
                 cam_x, cam_y, width, height):
    """Byte-buffer copy plus exposed tile bands; not hardware scrolling.

    Full repaint if the saved image is invalid or the cameras do not overlap.
    """
    if (width <= 0 or height <= 0 or cam_x < 0 or cam_y < 0 or
            cam_x + width > tilemap.cols * TILE_EDGE or
            cam_y + height > tilemap.rows * TILE_EDGE):
        raise ValueError("invalid viewport")
    if len(old_frame) != width * height:
        return span_frame(tilemap, tiles, cam_x, cam_y, width, height)
    dx = cam_x - old_x
    dy = cam_y - old_y
    if abs(dx) >= width or abs(dy) >= height:
        return span_frame(tilemap, tiles, cam_x, cam_y, width, height)
    # New(x,y) corresponds to old(x+dx,y+dy).
    x0, x1 = max(0, -dx), min(width, width - dx)
    y0, y1 = max(0, -dy), min(height, height - dy)
    out = bytearray(width * height)
    for y in range(y0, y1):
        dst_offset = y * width + x0
        src_offset = (y + dy) * width + x0 + dx
        out[dst_offset:dst_offset + (x1 - x0)] = old_frame[
            src_offset:src_offset + (x1 - x0)]
    # Disjoint exposed regions: top/bottom, and left/right inside middle.
    if y0:
        paint_rect(tilemap, tiles, out, cam_x, cam_y, width, 0, 0, width, y0)
    if y1 < height:
        paint_rect(tilemap, tiles, out, cam_x, cam_y, width,
                   0, y1, width, height - y1)
    if x0 and y1 > y0:
        paint_rect(tilemap, tiles, out, cam_x, cam_y, width,
                   0, y0, x0, y1 - y0)
    if x1 < width and y1 > y0:
        paint_rect(tilemap, tiles, out, cam_x, cam_y, width,
                   x1, y0, width - x1, y1 - y0)
    return bytes(out)


def time_variant(operation, repeats, passes):
    """Return a median of medians, and all observed per-frame pass durations."""
    operation()  # warm up; excluded
    batches = []
    for _ in range(passes):
        gc_enabled = gc.isenabled()
        gc.disable()
        try:
            start = time.perf_counter_ns()
            checksum = 0
            for _ in range(repeats):
                output = operation()
                checksum ^= output[(len(output) // 2)]
            elapsed = time.perf_counter_ns() - start
        finally:
            if gc_enabled:
                gc.enable()
        assert isinstance(checksum, int)
        batches.append(round(elapsed / repeats / 1_000_000, 6))
    return round(statistics.median(batches), 6), batches


def measure(repeats=3, passes=3, cases=None):
    if repeats < 1 or passes < 1:
        raise ValueError("repeats and passes must be positive")
    if cases is None:
        cases = [(192, 192, 1, 1, 0), (192, 192, 2, 8, 8),
                 (320, 256, 1, 16, 0), (320, 256, 2, 1, 0),
                 (320, 256, 2, 8, 8), (320, 256, 2, 16, 0)]
    results = []
    for width, height, layers, dx, dy in cases:
        tm, tiles = fixture(layers=layers)
        old_x, old_y = 17, 21
        cx, cy = old_x + dx, old_y + dy
        before = span_frame(tm, tiles, old_x, old_y, width, height)
        oracle = render_reference(tm, tiles, cx, cy, width, height)
        a = span_frame(tm, tiles, cx, cy, width, height)
        b = scroll_frame(tm, tiles, before, old_x, old_y,
                         cx, cy, width, height)
        assert oracle == a == b, "pixel comparison failed BEFORE benchmark"
        methods = {
            "pixel_reference": lambda: render_reference(tm, tiles, cx, cy,
                                                         width, height),
            "tile_spans": lambda: span_frame(tm, tiles, cx, cy, width, height),
            "scroll_copy_bands": lambda: scroll_frame(
                tm, tiles, before, old_x, old_y, cx, cy, width, height),
        }
        # Alternate method order across passes in future hardware benchmark.
        timing = {}
        for name, operation in methods.items():
            median_ms, passes_ms = time_variant(operation, repeats, passes)
            timing[name] = {"median_ms": median_ms, "pass_ms": passes_ms}
        overlap = max(0, width - abs(dx)) * max(0, height - abs(dy))
        results.append({
            "viewport": [width, height], "layers": layers, "delta": [dx, dy],
            "pixel_sha256": hashlib.sha256(oracle).hexdigest(),
            "overlap_pixels": overlap,
            "new_pixels": width * height - overlap,
            "timing": timing,
            "span_vs_pixel": round(
                timing["pixel_reference"]["median_ms"] /
                timing["tile_spans"]["median_ms"], 4),
            "scroll_vs_span": round(
                timing["tile_spans"]["median_ms"] /
                timing["scroll_copy_bands"]["median_ms"], 4),
        })
    return {
        "kind": "host_python_only",
        "warning": "Not a MC68020/AGA/Blitter/WinUAE performance claim",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
        "clock": "time.perf_counter_ns monotonic host elapsed",
        "units": "wall-time milliseconds per frame; median of pass averages",
        "repeats_per_pass": repeats, "passes": passes,
        "pretest": "pixel identical for all three methods before timing",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--passes", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(measure(args.repeats, args.passes), indent=2))


if __name__ == "__main__":
    main()
