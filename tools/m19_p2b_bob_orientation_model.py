#!/usr/bin/env python3
"""Host oracle for a per-Bob orientation of an immutable AGBO image."""

from dataclasses import dataclass

from m19_p0a_multi_bob_abk import BobImage
from m19_p2a_bob_collision_model import Bob, Image


@dataclass(frozen=True)
class OrientedImage:
    source: BobImage
    horizontal: bool = False
    vertical: bool = False

    @property
    def hotspot_x(self) -> int:
        hotspot = self.source.hotspot_x
        return self.source.width - 1 - hotspot if self.horizontal else hotspot

    @property
    def hotspot_y(self) -> int:
        hotspot = self.source.hotspot_y
        return self.source.height - 1 - hotspot if self.vertical else hotspot

    def source_pixel(self, x: int, y: int) -> tuple[int, int]:
        if self.horizontal:
            x = self.source.width - 1 - x
        if self.vertical:
            y = self.source.height - 1 - y
        return x, y

    def colour(self, x: int, y: int) -> int:
        return self.source.colour(*self.source_pixel(x, y))

    def visible(self, x: int, y: int) -> bool:
        return self.source.visible(*self.source_pixel(x, y))

    def collision_bob(self, bob_id: int, bank_id: int, x: int, y: int) -> Bob:
        """Project this orientation into the existing P2a collision oracle."""
        source = self.source
        mask = None
        if source.mask is not None:
            stride = (source.width + 7) // 8
            rows = bytearray(stride * source.height)
            for row in range(source.height):
                for column in range(source.width):
                    if self.visible(column, row):
                        rows[row * stride + column // 8] |= 0x80 >> (column % 8)
            mask = bytes(rows)
        return Bob(bob_id, bank_id, source.image_id, x, y,
                   Image(source.width, source.height, mask),
                   self.hotspot_x, self.hotspot_y)
