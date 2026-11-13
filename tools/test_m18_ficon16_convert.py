#!/usr/bin/env python3
"""M18/P1 host-only safe AGAPIC->Unity AGA Fast Icon conversion regression."""
from __future__ import annotations

from dataclasses import replace
import random

from m16_agapic import pack_image, parse_payload
from m18_icon_atlas_model import IconAtlas, IconRect
from m18_ficon16_convert import export_fast_icons
from m18_ficon16_model import draw_cpu
from test_m18_agapic_atlas_model import as_planar, reference, fails_clean


def fixture(*, masked: bool = True, depth: int = 8,
            wrong_mask: int = 0, short_icon: bool = False) -> IconAtlas:
    rng = random.Random(0xA616A)
    width, height = 64, 16
    pixels = bytearray(rng.randrange(1 << depth) for _ in range(width*height))
    for i in range(0, len(pixels), 7):
        pixels[i] = 0
    mask = bytearray(int(bool(x)) for x in pixels) if masked else None
    if wrong_mask == 1:
        assert mask is not None
        mask[0] = 1    # An opaque colour zero is not a Unity F Icon alpha.
    if wrong_mask == 2:
        assert mask is not None
        n = next(i for i,v in enumerate(pixels) if v != 0)
        mask[n] = 0    # A masked nonzero pixel cannot survive conversion.
    image = parse_payload(pack_image(
        width, height, depth, bytes(pixels), bytes(mask) if mask is not None else None))
    rects = (
        IconRect(1, 0, 0, 16, 16),
        IconRect(3, 16, 0, 16, 16),
        IconRect(7, 32, 0, 16, 16),
        IconRect(65535, 48, 0, 15 if short_icon else 16, 16),
    )
    return IconAtlas(image, rects)


def test_conversion() -> int:
    selected = (65535, 1, 7, 3)  # Sparse source IDs, ordered dense slots.
    cases = 0
    for masked in (True, False):
        atlas = fixture(masked=masked)
        exported = export_fast_icons(atlas, selected)
        assert exported.bank.count == 4
        assert exported.source_numbers == selected
        assert tuple(exported.slot_for_source(i) for i in selected) == (1, 2, 3, 4)
        assert len(exported.bank.raw) == 1164
        for number in selected:
            rect = atlas.rect(number)
            source = bytes(
                next_pixel
                for y in range(rect.y, rect.y + 16)
                for next_pixel in atlas.image_pixel_placeholder
            ) if False else None  # pixel oracle below uses an unpacked copy
            from m16_agapic import unpack_image
            pixels, _ = unpack_image(atlas.image)
            icon = bytes(pixels[y * 64 + x]
                         for y in range(rect.y, rect.y + 16)
                         for x in range(rect.x, rect.x + 16))
            # Byte-identical 256-pixel original icon and 8-plane words.
            for y in range(16):
                from struct import unpack_from
                words = unpack_from(">9H", exported.bank.icon(exported.slot_for_source(number)), y*18)
                for x in range(16):
                    got = sum((1 << plane) for plane, word in enumerate(words[1:])
                              if word & (0x8000 >> x))
                    assert got == icon[y*16+x]
            for x,y in ((-3, 5), (3, 7), (50, 36)):
                for mode in (0, 1):
                    w,h = 65,43
                    background = bytes([0x4c] * (w*h))
                    planes,stride = as_planar(background,w,h,8)
                    expected, count = reference(background,w,h,icon,
                                                bytes(int(bool(z)) for z in icon),
                                                16,(0,0,16,16),x,y,mode)
                    stats = draw_cpu(exported.bank,exported.slot_for_source(number),
                                     x,y,mode,planes,w,h,stride)
                    exp_planes,_ = as_planar(expected,w,h,8)
                    assert planes == exp_planes and stats.visible_pixels == count
                    cases += 1
    return cases


def test_refusals() -> int:
    atlas = fixture()
    source = (1,3,7,65535)
    from test_m18_agapic_atlas_model import as_planar
    planes,_ = as_planar(bytes([0] * (65*43)),65,43,8)
    invalids = (
        ("opaque colour-zero mask", lambda: export_fast_icons(fixture(wrong_mask=1), source)),
        ("hidden nonzero mask", lambda: export_fast_icons(fixture(wrong_mask=2), source)),
        ("wrong depth", lambda: export_fast_icons(fixture(depth=4), source)),
        ("non 16x16", lambda: export_fast_icons(fixture(short_icon=True), source)),
        ("less than 4 IDs", lambda: export_fast_icons(atlas, (1,3,7))),
        ("duplicate ID", lambda: export_fast_icons(atlas, (1,1,7,65535))),
        ("unknown ID", lambda: export_fast_icons(atlas, (1,3,7,8))),
        ("non tuple IDs", lambda: export_fast_icons(atlas, [1,3,7,65535])),
        ("boolean ID", lambda: export_fast_icons(atlas, (1,3,7,True))),
    )
    for name,action in invalids:
        fails_clean(action, planes, name)
    return len(invalids)


def main() -> None:
    rendered = test_conversion()
    refused = test_refusals()
    assert rendered == 48 and refused == 9, (rendered, refused)
    print("M18 AGAPIC->FICON16 HOST P1 PASS:",rendered,
          "pixel/planar renders, sparse->dense mapping,",refused,
          "semantic loss refusals")
    print("MASK POLICY: independent AGAPIC alpha must equal (colour != 0) "
          "for all selected pixels; no silent transparency loss")
    print("HOST ONLY: no native bank, Compiler V2, WinUAE or DMA proof")


if __name__ == "__main__":
    main()
