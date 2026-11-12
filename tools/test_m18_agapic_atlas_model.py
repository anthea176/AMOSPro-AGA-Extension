#!/usr/bin/env python3
"""M18/P0 host-only AGAPIC atlas contract tests; NOT a native 68k Gate A."""
from __future__ import annotations
from dataclasses import replace
import random

from m16_agapic import pack_image, parse_payload
from m18_agapic_atlas_model import (
    grid_frame_rect, render_grid_frame_cpu_model, render_region_cpu_model,
)

GUARD = bytes([0xa5] * 12)


def as_planar(pixels: bytes, width: int, height: int, depth: int):
    stride = ((width + 15) // 16) * 2
    planes = [bytearray(stride * height) + bytearray(GUARD)
              for _ in range(depth)]
    for pos, pixel in enumerate(pixels):
        x, y = pos % width, pos // width
        offset = y * stride + (x // 16) * 2
        bit = 0x8000 >> (x % 16)
        for plane in range(depth):
            if pixel & (1 << plane):
                value = (planes[plane][offset] << 8) | planes[plane][offset + 1]
                value |= bit
                planes[plane][offset] = value >> 8
                planes[plane][offset + 1] = value & 255
    return planes, stride


def reference(dst: bytes, dst_w: int, dst_h: int, src: bytes, mask: bytes | None,
              src_w: int, rect: tuple[int, int, int, int], x: int, y: int,
              mode: int) -> tuple[bytes, int]:
    out = bytearray(dst)
    sx, sy, width, height = rect
    written = 0
    for row in range(height):
        dy = y + row
        if not 0 <= dy < dst_h:
            continue
        for col in range(width):
            dx = x + col
            if not 0 <= dx < dst_w:
                continue
            source_pos = (sy + row) * src_w + sx + col
            if mode == 1 and not mask[source_pos]:
                continue
            out[dy * dst_w + dx] = src[source_pos]
            written += 1
    return bytes(out), written


def fails_clean(call, planes, reason: str):
    before = [bytes(p) for p in planes]
    try:
        call()
    except ValueError:
        assert [bytes(p) for p in planes] == before, reason + ": changed pixels"
        return
    raise AssertionError("expected refusal: " + reason)


def test_random_atlas() -> int:
    rng = random.Random(0xA6A18)
    cases = 0
    fw, fh, aw, ah = 19, 11, 57, 22
    dw, dh = 57, 37
    placements = [(-22, -15), (-1, -1), (0, 0), (1, 1),
                  (15, 6), (16, 12), (43, 29), (57, 37), (32767, -32768)]
    for depth in (1, 2, 4, 8):
        for masked in (False, True):
            pixels = bytes(rng.randrange(1 << depth) for _ in range(aw * ah))
            mask = (bytes(int((i + (i // aw)) % 4 != 0)
                          for i in range(aw * ah)) if masked else None)
            image = parse_payload(pack_image(aw, ah, depth, pixels, mask))
            for frame in range(6):
                rect = grid_frame_rect(image, fw, fh, frame)
                assert rect == ((frame % 3) * fw, (frame // 3) * fh, fw, fh)
                for x, y in placements:
                    for mode in ((0, 1) if masked else (0,)):
                        backdrop = bytes(rng.randrange(1 << depth)
                                         for _ in range(dw * dh))
                        planes, stride = as_planar(backdrop, dw, dh, depth)
                        expected, pixels_written = reference(
                            backdrop, dw, dh, pixels, mask, aw, rect, x, y, mode)
                        written = render_grid_frame_cpu_model(
                            image, fw, fh, frame, x, y,
                            planes, dw, dh, mode, stride)
                        target, _ = as_planar(expected, dw, dh, depth)
                        assert planes == target, (depth, masked, frame, x, y, mode)
                        assert written == pixels_written
                        assert all(p[-12:] == GUARD for p in planes)
                        cases += 1
            # Arbitrary non-cell rectangle spanning frame boundaries.
            for rect in ((3, 4, 37, 9), (16, 1, 21, 3), (0, 0, aw, ah)):
                backdrop = bytes(rng.randrange(1 << depth)
                                 for _ in range(dw * dh))
                planes, stride = as_planar(backdrop, dw, dh, depth)
                expected, n = reference(backdrop, dw, dh, pixels, mask, aw,
                                        rect, 7, -2, 1 if masked else 0)
                got = render_region_cpu_model(
                    image, *rect, 7, -2, planes, dw, dh,
                    1 if masked else 0, stride)
                target, _ = as_planar(expected, dw, dh, depth)
                assert got == n and planes == target
                cases += 1
    return cases


def test_rejects() -> int:
    w, h, depth = 35, 18, 4
    pixels = bytes((x * 3 + y * 5) % 16
                   for y in range(h) for x in range(w))
    img = parse_payload(pack_image(w, h, depth, pixels))
    masked_img = parse_payload(pack_image(w, h, depth, pixels,
                                          bytes(i % 3 != 0 for i in range(w*h))))
    dest, _ = as_planar(bytes([6] * (48 * 32)), 48, 32, depth)
    calls = [
        ("outside source left", lambda: render_region_cpu_model(
            img, -1, 0, 4, 5, 0, 0, dest, 48, 32, 0)),
        ("outside source right", lambda: render_region_cpu_model(
            img, 34, 0, 2, 5, 0, 0, dest, 48, 32, 0)),
        ("outside source bottom", lambda: render_region_cpu_model(
            img, 0, 17, 4, 2, 0, 0, dest, 48, 32, 0)),
        ("zero width", lambda: render_region_cpu_model(
            img, 0, 0, 0, 1, 0, 0, dest, 48, 32, 0)),
        ("bool coordinate", lambda: render_region_cpu_model(
            img, True, 0, 4, 5, 0, 0, dest, 48, 32, 0)),
        ("masked without source mask", lambda: render_region_cpu_model(
            img, 0, 0, 4, 5, 0, 0, dest, 48, 32, 1)),
        ("invalid mode", lambda: render_region_cpu_model(
            masked_img, 0, 0, 4, 5, 0, 0, dest, 48, 32, 2)),
        ("dest signed overflow", lambda: render_region_cpu_model(
            img, 0, 0, 4, 5, 32768, 0, dest, 48, 32, 0)),
        ("bad depth", lambda: render_region_cpu_model(
            img, 0, 0, 4, 5, 0, 0, dest[:-1], 48, 32, 0)),
        ("bad destination stride", lambda: render_region_cpu_model(
            img, 0, 0, 4, 5, 0, 0, dest, 48, 32, 0, 3)),
        ("grid does not divide atlas", lambda: render_grid_frame_cpu_model(
            img, 8, 9, 0, 0, 0, dest, 48, 32, 0)),
        ("negative frame", lambda: render_grid_frame_cpu_model(
            img, 35, 9, -1, 0, 0, dest, 48, 32, 0)),
        ("frame index too large", lambda: render_grid_frame_cpu_model(
            img, 35, 9, 2, 0, 0, dest, 48, 32, 0)),
        ("frame index bool", lambda: render_grid_frame_cpu_model(
            img, 35, 9, True, 0, 0, dest, 48, 32, 0)),
        ("truncated AGAPIC", lambda: render_region_cpu_model(
            replace(img, raw=img.raw[:-1]), 0, 0, 4, 5,
            0, 0, dest, 48, 32, 0)),
        ("changed metadata", lambda: render_region_cpu_model(
            replace(img, depth=3), 0, 0, 4, 5,
            0, 0, dest, 48, 32, 0)),
    ]
    for reason, call in calls:
        fails_clean(call, dest, reason)
    return len(calls)


def main() -> None:
    cases, rejected = test_random_atlas(), test_rejects()
    print(f"M18 AGAPIC ATLAS P0 HOST PASS: {cases} pixel-exact draws, "
          f"{rejected} safe refusals; 1/2/4/8 depths, opaque/masked, "
          "misaligned X, clipping and planar guards")
    print("HOST MODEL ONLY: no .Lib, AMOS command, native 68000 Gate A, "
          "WinUAE B/C, hardware D or FPS claim")


if __name__ == "__main__":
    main()
