#!/usr/bin/env python3
"""PNG -> AMOS DATA .abk / inner .agpic for M16 AGAPIC v1.

Uses Pillow only for indexed PNG import; core codec/tests use stdlib.
No palette is embedded in AGAPIC: install a compatible AGA palette separately.
Use --mask for an independent greyscale 1-bit transparency mask (threshold 128).
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from m16_agapic import pack_image, make_abk, parse_abk, stats


def indexed_png(path: Path) -> tuple[int, int, bytes, object]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("PNG conversion requires Pillow (pip install Pillow)") from exc
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != "P":
            raise ValueError("use indexed PNG, Pillow mode P; RGBA quantization is not implicit")
        return image.width, image.height, image.tobytes(), image.info.get("transparency")


def image_mask(path: Path, expected_w: int, expected_h: int) -> bytes:
    from PIL import Image
    with Image.open(path) as image:
        if image.size != (expected_w, expected_h):
            raise ValueError("mask size must match indexed PNG exactly")
        if image.mode not in ("1", "L"):
            raise ValueError("mask PNG must be monochrome (mode 1 or L)")
        img = image.convert("L")
        return bytes(int(value >= 128) for value in img.tobytes())


def palette_alpha_mask(pixels: bytes, transparent: object) -> bytes:
    if transparent is None:
        raise ValueError("PNG has no transparency; use --mask or --transparent-index")
    if isinstance(transparent, int) and 0 <= transparent <= 255:
        return bytes(int(p != transparent) for p in pixels)
    if isinstance(transparent, bytes):
        return bytes(int(p >= len(transparent) or transparent[p] >= 128)
                     for p in pixels)
    raise ValueError("unsupported PNG palette tRNS descriptor")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="indexed PNG in P mode")
    parser.add_argument("output", type=Path, help="native AMOS DATA .abk file")
    parser.add_argument("--bank", type=int, default=10, help="AMOS bank 5..65535 (default 10)")
    parser.add_argument("--depth", type=int, required=True, help="indexed bitplane depth 1..8")
    transparency = parser.add_mutually_exclusive_group()
    transparency.add_argument("--mask", type=Path, help="independent L/1-mode mask PNG; white = opaque")
    transparency.add_argument("--transparent-index", type=int, help="one palette index used as transparent")
    transparency.add_argument("--png-alpha", action="store_true", help="derive mask from indexed PNG tRNS")
    parser.add_argument("--chip", action="store_true", help="set external DATA/Chip flag (default Fast preference)")
    parser.add_argument("--payload", type=Path, help="also write raw AGAPIC payload for inspection")
    args = parser.parse_args()
    width, height, pixels, transparency_info = indexed_png(args.input)
    mask = None
    if args.mask is not None:
        mask = image_mask(args.mask, width, height)
    elif args.transparent_index is not None:
        if not 0 <= args.transparent_index < (1 << args.depth):
            raise ValueError("transparent index outside chosen bit depth")
        mask = bytes(int(px != args.transparent_index) for px in pixels)
    elif args.png_alpha:
        mask = palette_alpha_mask(pixels, transparency_info)
    payload = pack_image(width, height, args.depth, pixels, mask)
    abk = make_abk(args.bank, payload, chip=args.chip)
    assert parse_abk(abk)[2].raw == payload
    args.output.write_bytes(abk)
    if args.payload is not None:
        args.payload.write_bytes(payload)
    summary = stats(payload)
    print("AGAPIC v1 bank", args.bank, "DATA/Chip" if args.chip else
          "DATA/Fast-preference (location not guaranteed)")
    print(f"{width}x{height}x{args.depth}, {summary['mode']}, "
          f"{summary['planar_bytes']} planar B -> {summary['packed_bytes']} payload B "
          f"(+20 AmBk header)")
    print("ABK SHA256:", hashlib.sha256(abk).hexdigest())
    print("AMOS: Load the ABK into a DATA bank, then check List Bank F/C in WinUAE.")
    print("No native AGAPIC drawing API exists yet in R44 LAST_GOOD.")


if __name__ == "__main__":
    main()
