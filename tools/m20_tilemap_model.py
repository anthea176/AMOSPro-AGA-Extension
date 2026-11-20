#!/usr/bin/env python3
"""M20 P0 two-page tilemap scrolling oracle; host-only, NOT AGA native code.

Chunky 8-bit values here are reference pixels, NOT an AGA planar renderer.
Frame: restore old back snapshot, scroll/repaint tilemap, capture background
and overlay Bobs, then explicit Swap. Per-page camera and edit revisions.
No new AMOS API, library, runtime or Compiler claim.
"""
from __future__ import annotations
from dataclasses import dataclass, field

TILE = 16
MAX_BOBS = 64
MAX_EDITS = 128
CLEAN, DIRTY, READY = 0, 1, 2

@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self):
        return self.w * self.h

@dataclass(frozen=True)
class Bob:
    x: int
    y: int
    w: int
    h: int
    pen: int

@dataclass
class TileMap:
    cols: int
    rows: int
    tileset: tuple[bytes, ...]
    ids: bytearray
    depth: int = 8
    revision: int = 0
    edits: list[tuple[int, int, int]] = field(default_factory=list)

    def __post_init__(self):
        if not 1 <= self.depth <= 8 or not 1 <= self.cols <= 4096 or not 1 <= self.rows <= 4096:
            raise ValueError("invalid depth or geometry")
        if len(self.ids) != self.cols * self.rows:
            raise ValueError("tilemap stride mismatch")
        if not 1 <= len(self.tileset) <= 256:
            raise ValueError("tileset count")
        if any(len(t) != TILE * TILE or max(t) >= (1 << self.depth) for t in self.tileset):
            raise ValueError("invalid tile pixels")
        if any(i >= len(self.tileset) for i in self.ids):
            raise ValueError("tilemap references absent tile")

    @property
    def width(self):
        return self.cols * TILE

    @property
    def height(self):
        return self.rows * TILE

    def pixel(self, x, y):
        tx, lx = divmod(x, TILE)
        ty, ly = divmod(y, TILE)
        return self.tileset[self.ids[ty * self.cols + tx]][ly * TILE + lx]

    def edit(self, tx, ty, tile_id):
        if not (0 <= tx < self.cols and 0 <= ty < self.rows and 0 <= tile_id < len(self.tileset)):
            return False
        k = ty * self.cols + tx
        if self.ids[k] != tile_id:
            self.ids[k] = tile_id
            self.revision += 1
            self.edits.append((self.revision, tx, ty))
            if len(self.edits) > MAX_EDITS:
                del self.edits[:len(self.edits) - MAX_EDITS]
        return True

    def changes_since(self, seen_revision):
        if seen_revision == self.revision:
            return []
        if seen_revision > self.revision:
            return None
        if self.edits and seen_revision < self.edits[0][0] - 1:
            return None  # History lost: repaint all rather than reuse stale pixels.
        return [(x, y) for revision, x, y in self.edits if revision > seen_revision]

@dataclass(frozen=True)
class RenderStats:
    page: int
    full: bool
    repainted: int
    scrolled: int
    dirty_rects: tuple[Rect, ...]

@dataclass
class _Page:
    pixels: bytearray
    snapshot: bytes | None = None
    camera: tuple[int, int] | None = None
    map_revision: int = 0

def planar_bytes(width, height, depth):
    if not (width > 0 and height > 0 and 1 <= depth <= 8):
        raise ValueError("invalid planar geometry")
    return 2 * ((width + 15) // 16) * height * depth

def _clip(x, y, w, h, screen_w, screen_h):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(screen_w, x + w), min(screen_h, y + h)
    return Rect(x0, y0, x1 - x0, y1 - y0) if x0 < x1 and y0 < y1 else None

class DoubleBufferTilemap:
    def __init__(self, world: TileMap, width: int, height: int):
        if not (1 <= width <= world.width and 1 <= height <= world.height):
            raise ValueError("viewport exceeds map")
        self.world = world
        self.width, self.height = width, height
        self.pages = [_Page(bytearray(width * height)) for _ in range(2)]
        self.front = 0
        self.status, self.stage = CLEAN, "idle"
        self.swaps = 0
        self.closed = False
        self.last_error = ""

    @property
    def back(self):
        return 1 - self.front

    def _deny(self, reason):
        self.last_error = reason
        self.status = DIRTY
        return False

    def clear(self):
        if self.closed or self.status == DIRTY or self.stage not in ("idle", "cleared"):
            return self._deny("Clear in invalid state")
        page = self.pages[self.back]
        if page.snapshot is None:
            return self._deny("no per-page snapshot yet")
        page.pixels[:] = page.snapshot
        self.stage = "cleared"
        return True

    def draw_map(self, cx: int, cy: int) -> RenderStats | None:
        if self.closed or self.status == DIRTY or self.stage not in ("idle", "cleared"):
            self._deny("map draw in invalid state")
            return None
        pindex = self.back
        page = self.pages[pindex]
        if page.snapshot is not None and self.stage != "cleared":
            self._deny("must Clear old Bobs before map drawing")
            return None
        w, h = self.width, self.height
        if not (0 <= cx <= self.world.width - w and 0 <= cy <= self.world.height - h):
            self._deny("camera outside map")
            return None
        changes = self.world.changes_since(page.map_revision)
        full = page.camera is None or changes is None
        dx = dy = 0
        if page.camera is not None:
            dx, dy = cx - page.camera[0], cy - page.camera[1]
            full = full or abs(dx) >= w or abs(dy) >= h

        dest = bytearray(w * h)
        dirty = bytearray(w * h)
        regions: list[Rect] = []
        scrolled = 0
        if full:
            dirty[:] = b"\x01" * (w * h)
            regions.append(Rect(0, 0, w, h))
        else:
            x0, y0 = max(0, -dx), max(0, -dy)
            x1, y1 = x0 + w - abs(dx), y0 + h - abs(dy)
            for y in range(y0, y1):
                start = (y + dy) * w + x0 + dx
                dest[y * w + x0:y * w + x1] = page.pixels[start:start + x1 - x0]
            scrolled = (x1 - x0) * (y1 - y0)
            if x0:
                regions.append(Rect(0, 0, x0, h))
            if x1 < w:
                regions.append(Rect(x1, 0, w - x1, h))
            if y0:
                regions.append(Rect(x0, 0, x1 - x0, y0))
            if y1 < h:
                regions.append(Rect(x0, y1, x1 - x0, h - y1))
            for tx, ty in changes:
                rect = _clip(tx * TILE - cx, ty * TILE - cy, TILE, TILE, w, h)
                if rect is not None:
                    regions.append(rect)
            for rect in regions:
                for y in range(rect.y, rect.y + rect.h):
                    pos = y * w + rect.x
                    dirty[pos:pos + rect.w] = b"\x01" * rect.w

        repainted = 0
        for y in range(h):
            for x in range(w):
                k = y * w + x
                if dirty[k]:
                    dest[k] = self.world.pixel(cx + x, cy + y)
                    repainted += 1
        page.pixels = dest
        page.camera = (cx, cy)
        page.map_revision = self.world.revision
        self.stage = "map-drawn"
        self.last_error = ""
        return RenderStats(pindex, full, repainted, scrolled, tuple(regions))

    def update_bobs(self, bobs=()):
        if self.closed or self.status == DIRTY or self.stage != "map-drawn":
            return self._deny("Update before full map preparation")
        if len(bobs) > MAX_BOBS or any(
            b.w <= 0 or b.h <= 0 or not 0 <= b.pen < (1 << self.world.depth)
            for b in bobs
        ):
            return self._deny("Bob preflight failure")
        page = self.pages[self.back]
        background = bytes(page.pixels)
        composed = bytearray(page.pixels)
        for b in bobs:
            rect = _clip(b.x, b.y, b.w, b.h, self.width, self.height)
            if rect is not None:
                for y in range(rect.y, rect.y + rect.h):
                    pos = y * self.width + rect.x
                    composed[pos:pos + rect.w] = bytes([b.pen]) * rect.w
        page.snapshot, page.pixels = background, composed
        self.status, self.stage = READY, "ready"
        return True

    def swap(self):
        if self.closed or self.status != READY or self.stage != "ready":
            return self._deny("Swap before READY")
        self.front = self.back
        self.swaps += 1
        self.status, self.stage = CLEAN, "idle"
        return True

    def front_pixels(self):
        return bytes(self.pages[self.front].pixels)

    def close(self):
        self.closed = True
        self.pages = [_Page(bytearray(self.width * self.height)) for _ in range(2)]
        self.status, self.stage = CLEAN, "idle"

    def reopen(self):
        if not self.closed:
            raise ValueError("close required")
        self.closed = False
        self.front, self.swaps = 0, 0
        self.status, self.stage = CLEAN, "idle"
