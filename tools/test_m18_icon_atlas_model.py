#!/usr/bin/env python3
"""M18 numbered-icon host tests: independent pixel oracle, no 68k Gate A."""
from __future__ import annotations

from dataclasses import replace
import random

from m16_agapic import pack_image, parse_payload
from m18_icon_atlas_model import IconAtlas, IconRect, draw_numbered_icon_cpu_model
from test_m18_agapic_atlas_model import as_planar, reference, fails_clean, GUARD


def test_pixels() -> int:
    rng = random.Random(0xF16C0A)
    w, h, dest_w, dest_h = 57, 32, 65, 43
    rectangles = (
        IconRect(1, 0, 0, 16, 16),
        IconRect(3, 16, 0, 19, 11),
        IconRect(7, 35, 2, 22, 25),
        IconRect(65535, 2, 17, 11, 15),
    )
    placements = ((0, 0), (1, 1), (15, 16), (55, 40),
                  (-7, -4), (65, 43), (32767, -32768))
    cases = 0
    for depth in (1, 2, 4, 8):
        source = bytes(rng.randrange(1 << depth) for _ in range(w*h))
        for masked in (False, True):
            mask = (bytes(int(((i // w) + (i % w)) % 3 != 0)
                          for i in range(w*h)) if masked else None)
            image = parse_payload(pack_image(w, h, depth, source, mask))
            atlas = IconAtlas(image, rectangles)
            assert tuple(atlas.rect(r.number) for r in rectangles) == rectangles
            # Two independent back buffers. Drawing one must not touch the other.
            for rect in rectangles:
                for x, y in placements:
                    for mode in (0, 1) if masked else (0,):
                        base = bytes(rng.randrange(1 << depth)
                                     for _ in range(dest_w * dest_h))
                        planes, stride = as_planar(base, dest_w, dest_h, depth)
                        other, _ = as_planar(base, dest_w, dest_h, depth)
                        before_other = [bytes(p) for p in other]
                        expected, count = reference(
                            base, dest_w, dest_h, source, mask, w,
                            (rect.x, rect.y, rect.width, rect.height),
                            x, y, mode)
                        actual = draw_numbered_icon_cpu_model(
                            atlas, rect.number, x, y, planes,
                            dest_w, dest_h, mode, stride)
                        expect_planes, _ = as_planar(expected, dest_w, dest_h, depth)
                        assert actual == count
                        assert planes == expect_planes, (
                            depth, masked, rect.number, x, y, mode)
                        assert [bytes(p) for p in other] == before_other
                        assert all(p[-len(GUARD):] == GUARD for p in planes)
                        cases += 1
    return cases


def test_rejections() -> int:
    w, h, depth = 57, 32, 4
    pixels = bytes((x + 7*y) % 16 for y in range(h) for x in range(w))
    image = parse_payload(pack_image(w, h, depth, pixels))
    original = (IconRect(1, 0, 0, 16, 16), IconRect(9, 16, 0, 19, 11))
    atlas = IconAtlas(image, original)
    planes, _ = as_planar(bytes([4] * (65*43)), 65, 43, depth)
    cases = 0

    for title, icons in (
        ("empty directory", ()),
        ("duplicate ID", original + (original[0],)),
        ("zero ID", (IconRect(0, 0, 0, 16, 16),)),
        ("negative ID", (IconRect(-1, 0, 0, 16, 16),)),
        ("overflow ID", (IconRect(65536, 0, 0, 16, 16),)),
        ("bad source left", (IconRect(1, -1, 0, 16, 16),)),
        ("bad source right", (IconRect(1, 56, 0, 2, 4),)),
        ("bad source bottom", (IconRect(1, 0, 31, 3, 2),)),
        ("zero dimension", (IconRect(1, 0, 0, 0, 16),)),
        ("bool coordinate", (IconRect(1, True, 0, 16, 16),)),
        ("bool icon ID", (IconRect(True, 0, 0, 16, 16),)),
        ("bad row type", ((1, 0, 0, 16, 16),)),
    ):
        fails_clean(lambda icons=icons: IconAtlas(image, icons), planes, title)
        cases += 1

    for number in (-1, 0, 2, 65536, True, 1.0, "1"):
        fails_clean(lambda n=number: draw_numbered_icon_cpu_model(
            atlas, n, 1, 1, planes, 65, 43, 0), planes, f"icon ID {number}")
        cases += 1
    fails_clean(lambda: draw_numbered_icon_cpu_model(
        atlas, 1, 1, 1, planes, 65, 43, 1), planes, "no mask")
    cases += 1
    fails_clean(lambda: draw_numbered_icon_cpu_model(
        atlas, 1, 32768, 0, planes, 65, 43, 0), planes, "bad X")
    cases += 1
    fails_clean(lambda: draw_numbered_icon_cpu_model(
        atlas, 1, 0, 0, planes[:-1], 65, 43, 0), planes, "wrong depth")
    cases += 1
    fails_clean(lambda: IconAtlas(replace(image, raw=image.raw[:-1]), original),
                planes, "truncated image")
    cases += 1
    return cases


def main() -> None:
    pixel_cases = test_pixels()
    rejection_cases = test_rejections()
    assert pixel_cases == 336 and rejection_cases == 23, (pixel_cases, rejection_cases)
    print(f"M18 ICON ATLAS HOST P0 PASS: {pixel_cases} pixel-exact "
          f"numbered-image renders, {rejection_cases} no-write refusals")
    print("AGAPIC v1 reused, index 1..65535, 1/2/4/8 planes, "
          "opaque/masked, clipping and guard bytes PASS")
    print("HOST ONLY: no AMOS icon-bank format, no Turbo command equivalence, "
          "no Blitter, native CPU Gate A or WinUAE B/C")


if __name__ == "__main__":
    main()
