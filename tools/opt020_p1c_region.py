"""OPT020 P1c AGAPIC v1 renderer orchestration (Python host, native 020 subcalls).

All packet decoding and clipping decisions in this prototype are
actually executed by Motorola CPU emulation via RealNativeRLEClip.
Only high-level row/group dispatch, bitmap metadata validation, and
bounded partial-group pixel fallback are in Python. Opaque and masked
full 16-pixel groups use the real P1b native 8-plane BFINS routine.
NO AMOS/AP20/WinUAE claim: the optimized path has no safe live wrapper.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack

from m16_agapic import AGAPIC, MAX_SIDE, MAX_PIXELS, parse_payload


@dataclass(frozen=True)
class RenderStats:
    pixels: int
    native_groups: int
    fallback_pixels: int
    decoded_rows: int
    groups_clipped: int


def draw_native_plan(image: AGAPIC, sx: int, sy: int, width: int, height: int,
                     x: int, y: int, planes: list[bytearray],
                     dst_w: int, dst_h: int, mode: int, writer, native,
                     stride: int | None = None) -> RenderStats:
    """Full validation before paint; native RLE and clipping on every row/group."""
    if not isinstance(image, AGAPIC):
        raise ValueError("source must be AGAPIC")
    vals = (sx, sy, width, height, x, y, dst_w, dst_h, mode)
    if any(type(v) is not int for v in vals):
        raise ValueError("coordinates/geometry must be integers")
    if (sx < 0 or sy < 0 or width <= 0 or height <= 0 or
            width > image.width or height > image.height or
            sx > image.width - width or sy > image.height - height):
        raise ValueError("invalid source crop")
    if not (-32768 <= x <= 32767 and -32768 <= y <= 32767):
        raise ValueError("destination coordinate outside signed 16-bit")
    if mode not in (0, 1) or (mode == 1 and not image.masked):
        raise ValueError("mask mode unavailable")
    if not (1 <= dst_w <= MAX_SIDE and 1 <= dst_h <= MAX_SIDE and
            dst_w * dst_h <= MAX_PIXELS):
        raise ValueError("invalid destination geometry")
    min_stride = ((dst_w + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if type(stride) is not int or stride < min_stride or (stride & 1):
        raise ValueError("invalid plane byte stride")
    if (not isinstance(planes, list) or len(planes) != image.depth or
            any(not isinstance(p, bytearray) or len(p) < stride * dst_h
                for p in planes)):
        raise ValueError("wrong destination plane count or allocation")
    if not callable(writer) or not callable(getattr(native, "decode_row", None)):
        raise ValueError("native execution backend missing")
    # Validate all rows, padding and flags before ANY destination mutation.
    if parse_payload(image.raw) != image:
        raise ValueError("AGAPIC source is corrupt or metadata changed")

    pixels = natives = fallback = rows = clipped = 0
    for source_y in range(sy, sy + height):
        visible, dest_y = native.clip_y(source_y, sy, y, dst_h)
        if not visible:
            continue
        start, stop = image.offsets[source_y:source_y + 2]
        groups = native.decode_row(image.raw[start:stop], image.group_bytes,
                                   image.groups_per_row)
        rows += 1
        for group_i, group in enumerate(groups):
            gx = group_i * 16
            left, right = native.clip_x(gx, sx, sx + width, x, dst_w,
                                        image.width)
            if left == right:
                clipped += 1
                continue
            words = unpack(">" + "H" * (image.depth + int(image.masked)), group)
            mask = words[0] if mode == 1 else 0xffff
            colours = words[int(image.masked):]
            x0 = x + gx - sx
            whole = left == 0 and right == 16
            if whole and 0 <= x0 and x0 + 16 <= dst_w:
                bit_offset = x0 & 7
                byte_offset = dest_y * stride + (x0 // 8)
                needed = 2 if bit_offset == 0 else 3
                if byte_offset + needed <= (dest_y + 1) * stride:
                    if mask:
                        writer(colours, mask, bit_offset, planes, byte_offset)
                        natives += 1
                        pixels += mask.bit_count()
                    continue
            for bit_index in range(left, right):
                bit = 0x8000 >> bit_index
                if not (mask & bit):
                    continue
                dest_x = x0 + bit_index
                assert 0 <= dest_x < dst_w
                offset = dest_y * stride + dest_x // 8
                dest_mask = 0x80 >> (dest_x & 7)
                for plane, src_word in zip(planes, colours):
                    if src_word & bit:
                        plane[offset] |= dest_mask
                    else:
                        plane[offset] &= 255 ^ dest_mask
                pixels += 1
                fallback += 1
    return RenderStats(pixels, natives, fallback, rows, clipped)
