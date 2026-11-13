#!/usr/bin/env python3
"""M18/P1 HOST conversion: AGAPIC v1 atlas -> fixed AGA Fast Icon slots.

This is an explicit semantic conversion, NOT a native AMOS bank writer.
Each requested sparse AGAPIC icon ID becomes a dense Unity-style 16x16
slot and a separate mapping. AGAPIC independent alpha must exactly equal
"colour != 0" for the selected pixels; otherwise conversion is refused
without producing an incorrect transparency result.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from m16_agapic import unpack_image
from m18_icon_atlas_model import IconAtlas
from m18_ficon16_model import FIconBank, build_bank, parse_bank


@dataclass(frozen=True)
class FastIconExport:
    bank: FIconBank
    source_numbers: tuple[int, ...]
    _by_id: Mapping[int, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.bank, FIconBank):
            raise ValueError("invalid Fast Icon export bank")
        if (len(self.source_numbers) != self.bank.count or
                len(set(self.source_numbers)) != self.bank.count):
            raise ValueError("export number table must match Fast Icon slots")
        object.__setattr__(self, "_by_id", MappingProxyType(
            {number: slot for slot, number in enumerate(self.source_numbers, start=1)}))

    def slot_for_source(self, number: int) -> int:
        if type(number) is not int:
            raise ValueError("invalid source icon ID")
        slot = self._by_id.get(number)
        if slot is None:
            raise ValueError("icon ID not exported")
        return slot


def export_fast_icons(atlas: IconAtlas, selected_ids: tuple[int, ...]
                      ) -> FastIconExport:
    """Convert validated 8-plane 16x16 atlas entries to Unity-style slots.

    If AGAPIC has a mask, refuse EVERY independently opaque colour-zero
    pixel and EVERY transparent nonzero pixel. This preserves both
    opaque output and colour-zero transparent output in the conversion.
    A no-mask AGAPIC source is allowed, but masked Fast Icon rendering is
    an explicitly new colour-zero transparency mode.
    """
    if not isinstance(atlas, IconAtlas) or atlas.image.depth != 8:
        raise ValueError("AGA Fast Icon conversion needs an 8-plane atlas")
    if (not isinstance(selected_ids, tuple) or
            not 4 <= len(selected_ids) <= 4096 or
            any(type(x) is not int for x in selected_ids) or
            len(set(selected_ids)) != len(selected_ids)):
        raise ValueError("selected icon IDs must be four or more distinct integers")
    pixels, mask = unpack_image(atlas.image)
    slots: list[bytes] = []
    for source_id in selected_ids:
        rect = atlas.rect(source_id)
        if (rect.width, rect.height) != (16, 16):
            raise ValueError("Fast Icon slot must be exactly 16x16")
        icon = bytearray()
        for y in range(rect.y, rect.y + 16):
            for x in range(rect.x, rect.x + 16):
                pos = y * atlas.image.width + x
                index = pixels[pos]
                if mask is not None and bool(mask[pos]) != bool(index):
                    raise ValueError("AGAPIC independent alpha not representable")
                icon.append(index)
        slots.append(bytes(icon))
    return FastIconExport(parse_bank(build_bank(tuple(slots))), selected_ids)
