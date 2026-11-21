#!/usr/bin/env python3
"""M19 P2a HOST MODEL ONLY: Bob collision geometry; no native AGA or AMOS API.

Mask bytes are host-only fixtures (row-major MSB first, 1=opaque, 0=clear),
NOT the AGBO disk/RAM layout. No graphics, bank operations or Swap.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def __post_init__(self) -> None:
        if self.w <= 0 or self.h <= 0:
            raise ValueError("rectangle width and height must be positive")

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def intersect(self, other: Rect) -> Rect | None:
        x, y = max(self.x, other.x), max(self.y, other.y)
        right, bottom = min(self.right, other.right), min(self.bottom, other.bottom)
        return Rect(x, y, right-x, bottom-y) if right > x and bottom > y else None


@dataclass(frozen=True)
class Image:
    width: int
    height: int
    mask: bytes | None = None

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("image width and height must be positive")
        if self.mask is not None and len(self.mask) != self.stride * self.height:
            raise ValueError("host mask size mismatch")

    @property
    def stride(self) -> int:
        return (self.width+7)//8

    def opaque(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.mask is None or bool(self.mask[y*self.stride+x//8] & (128 >> (x%8)))


@dataclass(frozen=True)
class Bob:
    bob_id: int
    bank_id: int
    image_id: int
    x: int
    y: int
    image: Image
    hotspot_x: int = 0
    hotspot_y: int = 0
    active: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.bob_id <= 64:
            raise ValueError("Bob ID out of range")
        if not 5 <= self.bank_id <= 65535:
            raise ValueError("bank ID out of range")
        if not 1 <= self.image_id <= 4096:
            raise ValueError("image ID out of range")

    @property
    def origin_x(self) -> int:
        return self.x-self.hotspot_x

    @property
    def origin_y(self) -> int:
        return self.y-self.hotspot_y

    @property
    def footprint(self) -> Rect:
        return Rect(self.origin_x, self.origin_y, self.image.width, self.image.height)


def visible_footprint(bob: Bob, screen: Rect, global_limit: Rect | None = None,
                      local_limits: Mapping[int, Rect] | None = None) -> Rect | None:
    """Candidate footprint: screen intersection global intersection local."""
    if not bob.active:
        return None
    rect = bob.footprint.intersect(screen)
    if rect is not None and global_limit is not None:
        rect = rect.intersect(global_limit)
    if rect is not None and local_limits is not None and bob.bob_id in local_limits:
        rect = rect.intersect(local_limits[bob.bob_id])
    return rect


def collision(a: Bob, b: Bob, *, screen: Rect, mode: str = "rect",
              global_limit: Rect | None = None,
              local_limits: Mapping[int, Rect] | None = None) -> bool:
    """Proposed rectangle or masked collision; no side effects or Swap."""
    if mode not in ("rect", "mask"):
        raise ValueError("unknown collision mode")
    if a.bob_id == b.bob_id:
        raise ValueError("same Bob ID")
    ar = visible_footprint(a, screen, global_limit, local_limits)
    br = visible_footprint(b, screen, global_limit, local_limits)
    overlap = ar.intersect(br) if ar is not None and br is not None else None
    if overlap is None:
        return False
    if mode == "rect":
        return True
    for y in range(overlap.y, overlap.bottom):
        for x in range(overlap.x, overlap.right):
            if (a.image.opaque(x-a.origin_x, y-a.origin_y) and
                    b.image.opaque(x-b.origin_x, y-b.origin_y)):
                return True
    return False


def collision_pairs(bobs: Iterable[Bob], *, screen: Rect, mode: str = "rect",
                    global_limit: Rect | None = None,
                    local_limits: Mapping[int, Rect] | None = None) -> list[tuple[int, int]]:
    """Stable sorted unique ID pairs, regardless of drawing priority."""
    ordered = sorted(bobs, key=lambda b: b.bob_id)
    if len({b.bob_id for b in ordered}) != len(ordered):
        raise ValueError("duplicate Bob ID")
    return [(a.bob_id, b.bob_id)
            for i, a in enumerate(ordered)
            for b in ordered[i+1:]
            if collision(a, b, screen=screen, mode=mode,
                         global_limit=global_limit, local_limits=local_limits)]
