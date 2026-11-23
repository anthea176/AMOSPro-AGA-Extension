#!/usr/bin/env python3
"""AGTM host-only mutable map, dirty scrolling, and two-page scene oracle.

No AGA bitmap, chipset, DMA, AP20 command or real hardware timing.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from agtm_format_proto import AGTMError, AGTMMap, TILE_EDGE
from agtm_render_bench import paint_rect, span_frame

MAX_EDITS = 128


class MutableMap:
    """Fixed-size contiguous cell arrays, O(1) edits; no full-map copying."""

    def __init__(self, source: AGTMMap):
        self.cols = source.cols
        self.rows = source.rows
        self.tile_count = source.tile_count
        self.layers = tuple(bytearray(layer) for layer in source.layers)
        self.revision = 0
        self.edits = deque(maxlen=MAX_EDITS)

    def edit(self, layer: int, x: int, y: int, tile_id: int) -> bool:
        if not (0 <= layer < len(self.layers) and 0 <= x < self.cols and
                0 <= y < self.rows and 0 <= tile_id < self.tile_count):
            raise AGTMError("INVALID_EDIT")
        offset = y * self.cols + x
        if self.layers[layer][offset] == tile_id:
            return False
        self.layers[layer][offset] = tile_id
        self.revision += 1
        self.edits.append((self.revision, x, y))
        return True

    def changes_since(self, revision: int) -> set[tuple[int, int]] | None:
        """None means the bounded history was lost: full redraw required."""
        if revision == self.revision:
            return set()
        if revision > self.revision or not self.edits:
            return None
        if revision < self.edits[0][0] - 1:
            return None
        return {(x, y) for number, x, y in self.edits if number > revision}


@dataclass(frozen=True)
class Actor:
    x: int
    y: int
    w: int
    h: int
    pen: int


@dataclass
class Page:
    background: bytes | None = None
    displayed: bytes | None = None
    camera: tuple[int, int] | None = None
    map_revision: int = 0


@dataclass(frozen=True)
class FrameStats:
    full_redraw: bool
    copied_pixels: int
    bands_pixels: int
    tile_edits: int
    edit_pixels: int
    history_lost: bool


def incremental_background(world: MutableMap, tiles: tuple[bytes, ...],
                           previous: bytes | None, previous_camera: tuple[int, int] | None,
                           previous_revision: int, camera: tuple[int, int],
                           width: int, height: int):
    """Return the clean background and work statistics; never paints actors."""
    cx, cy = camera
    if (width <= 0 or height <= 0 or cx < 0 or cy < 0 or
            cx + width > world.cols * TILE_EDGE or
            cy + height > world.rows * TILE_EDGE):
        raise AGTMError("CAMERA_RANGE")
    if len(tiles) < world.tile_count or any(len(tile) != 256 for tile in tiles):
        raise AGTMError("TILESET")

    changes = world.changes_since(previous_revision)
    lost = changes is None
    full = (previous is None or previous_camera is None or
            len(previous) != width * height or lost)
    if previous_camera is not None:
        dx, dy = cx - previous_camera[0], cy - previous_camera[1]
        full = full or abs(dx) >= width or abs(dy) >= height
    else:
        dx = dy = 0
    if full:
        return (span_frame(world, tiles, cx, cy, width, height),
                FrameStats(True, 0, width * height, 0, 0, lost))

    # A single allocation, one copy of the retained scene and direct patches.
    x0, x1 = max(0, -dx), min(width, width - dx)
    y0, y1 = max(0, -dy), min(height, height - dy)
    overlap = (x1 - x0) * (y1 - y0)
    out = bytearray(width * height)
    for y in range(y0, y1):
        dest = y * width + x0
        source = (y + dy) * width + x0 + dx
        out[dest:dest + x1 - x0] = previous[source:source + x1 - x0]
    if y0:
        paint_rect(world, tiles, out, cx, cy, width, 0, 0, width, y0)
    if y1 < height:
        paint_rect(world, tiles, out, cx, cy, width,
                   0, y1, width, height - y1)
    if x0 and y1 > y0:
        paint_rect(world, tiles, out, cx, cy, width,
                   0, y0, x0, y1 - y0)
    if x1 < width and y1 > y0:
        paint_rect(world, tiles, out, cx, cy, width,
                   x1, y0, width - x1, y1 - y0)

    edit_pixels = 0
    edit_count = 0
    for tx, ty in sorted(changes):
        left = max(0, tx * TILE_EDGE - cx)
        top = max(0, ty * TILE_EDGE - cy)
        right = min(width, (tx + 1) * TILE_EDGE - cx)
        bottom = min(height, (ty + 1) * TILE_EDGE - cy)
        if left < right and top < bottom:
            rw, rh = right - left, bottom - top
            paint_rect(world, tiles, out, cx, cy, width, left, top, rw, rh)
            edit_pixels += rw * rh
            edit_count += 1
    return (bytes(out), FrameStats(False, overlap, width * height - overlap,
                                  edit_count, edit_pixels, False))


def compose_actors(background: bytes, actors: tuple[Actor, ...],
                   width: int, height: int) -> bytes:
    if len(actors) > 64:
        raise AGTMError("TOO_MANY_ACTORS")
    result = bytearray(background)
    for a in actors:
        if a.w < 1 or a.h < 1 or not 0 <= a.pen <= 255:
            raise AGTMError("INVALID_ACTOR")
        x0, x1 = max(0, a.x), min(width, a.x + a.w)
        y0, y1 = max(0, a.y), min(height, a.y + a.h)
        if x0 >= x1 or y0 >= y1:
            continue
        fill = bytes([a.pen]) * (x1 - x0)
        for y in range(y0, y1):
            result[y * width + x0:y * width + x1] = fill
    return bytes(result)


class TwoPageScene:
    """Reference state machine, not a behavioral replacement for AGA Bobs."""

    def __init__(self, world: MutableMap, tiles: tuple[bytes, ...],
                 width: int, height: int):
        self.world, self.tiles = world, tiles
        self.width, self.height = width, height
        self.pages = [Page(), Page()]
        self.front = 0
        self.state = "CLEAN"
        self.last_stats: FrameStats | None = None

    def prepare(self, cx: int, cy: int, actors: tuple[Actor, ...] = ()): 
        if self.state != "CLEAN":
            raise AGTMError("SCENE_NOT_CLEAN")
        p = self.pages[1 - self.front]
        try:
            background, stats = incremental_background(
                self.world, self.tiles, p.background, p.camera,
                p.map_revision, (cx, cy), self.width, self.height)
            display = compose_actors(background, actors, self.width, self.height)
        except (AGTMError, ValueError, TypeError):
            self.state = "DIRTY"  # Refuse swap until explicit abort.
            raise
        # Commit only after all validation and paint stages passed.
        self.pages[1 - self.front] = Page(background, display, (cx, cy),
                                          self.world.revision)
        self.last_stats = stats
        self.state = "READY"
        return stats

    def swap(self):
        if self.state != "READY":
            raise AGTMError("SWAP_NOT_READY")
        self.front = 1 - self.front
        self.state = "CLEAN"
        return self.pages[self.front].displayed

    def abort(self):
        """Discard an unpresented preparation; never modify the front page."""
        if self.state == "DIRTY":
            self.state = "CLEAN"
            return
        raise AGTMError("ABORT_NOT_DIRTY")
