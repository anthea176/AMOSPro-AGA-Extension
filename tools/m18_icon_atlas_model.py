#!/usr/bin/env python3
"""M18/F-Icon P0: numbered images over an AGAPIC v1 atlas (HOST ONLY).

A small immutable directory maps a positive icon ID to one exact source
rectangle in one validated AGAPIC v1 DATA image. Rendering deliberately
delegates to the already tested M18 region decoder, not a second raster
engine. No on-disk icon format, AP20 token, 68000 code or Blitter here.

This is a proposed functional model for fast numbered icon pasting, NOT
a reconstruction of Turbo Plus 'F Paste Icon' or the unverified name
'F 16 Icon'. The host return value is pixels written, not an AMOS ABI.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from m16_agapic import AGAPIC, parse_payload
from m18_agapic_atlas_model import render_region_cpu_model


@dataclass(frozen=True)
class IconRect:
    number: int
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class IconAtlas:
    image: AGAPIC
    icons: tuple[IconRect, ...]
    _by_id: Mapping[int, IconRect] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.image, AGAPIC):
            raise ValueError("icon source is not AGAPIC")
        if parse_payload(self.image.raw) != self.image:
            raise ValueError("icon source metadata mismatch")
        if not isinstance(self.icons, tuple) or not self.icons:
            raise ValueError("icon directory is empty")
        index: dict[int, IconRect] = {}
        for rect in self.icons:
            if not isinstance(rect, IconRect):
                raise ValueError("not an icon rectangle")
            values = (rect.number, rect.x, rect.y, rect.width, rect.height)
            if not all(type(x) is int for x in values):
                raise ValueError("icon metadata must be plain integers")
            if not 1 <= rect.number <= 65535 or rect.number in index:
                raise ValueError("duplicate or invalid icon number")
            if (rect.x < 0 or rect.y < 0 or rect.width <= 0 or rect.height <= 0
                    or rect.x + rect.width > self.image.width
                    or rect.y + rect.height > self.image.height):
                raise ValueError("icon rectangle outside atlas")
            index[rect.number] = rect
        object.__setattr__(self, "_by_id", MappingProxyType(index))

    def rect(self, number: int) -> IconRect:
        if type(number) is not int or not 1 <= number <= 65535:
            raise ValueError("invalid icon number")
        item = self._by_id.get(number)
        if item is None:
            raise ValueError("unknown icon number")
        return item


def draw_numbered_icon_cpu_model(
        atlas: IconAtlas, number: int, x: int, y: int,
        planes: list[bytearray], dest_w: int, dest_h: int, mode: int,
        stride: int | None = None) -> int:
    """Select one numbered icon and paint only its pixels, with clipping."""
    if not isinstance(atlas, IconAtlas):
        raise ValueError("source must be an icon atlas")
    rect = atlas.rect(number)  # Fail before any writes.
    return render_region_cpu_model(
        atlas.image, rect.x, rect.y, rect.width, rect.height,
        x, y, planes, dest_w, dest_h, mode, stride)
