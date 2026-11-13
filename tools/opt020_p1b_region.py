"""OPT020/P1b host dispatcher for real 020 masked 1..8 plane native groups.

Uses the exact AGAPIC v1 row RLE reader, after full preflight.
The group writer callback executes the separate 68EC020/68020 kernel in
a CPU emulator. Boundary/crop fragments use a bounded scalar fallback.
This is deliberately NOT a live AP20 extension, nor a timed Amiga renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack

from m16_agapic import AGAPIC, MAX_SIDE, MAX_PIXELS, parse_payload


@dataclass(frozen=True)
class RenderResult:
    pixels: int
    native_groups: int
    fallback_pixels: int
    literal_packets: int
    repeat_packets: int


def _packet_counts(image: AGAPIC) -> tuple[int, int]:
    literal = repeat = 0
    for row in range(image.height):
        pos, end = image.offsets[row:row + 2]
        while pos < end:
            control = image.raw[pos]
            pos += 1
            count = (control & 127) + 1
            if control & 128:
                repeat += 1
                pos += image.group_bytes
            else:
                literal += 1
                pos += count * image.group_bytes
        assert pos == end  # parse_payload already validated the RLE
    return literal, repeat


def draw_region_020(image: AGAPIC, sx: int, sy: int, width: int,
                    height: int, x: int, y: int,
                    planes: list[bytearray], dst_w: int, dst_h: int,
                    mode: int, native_write, stride: int | None = None
                    ) -> RenderResult:
    """Draw clipped AGAPIC region while invoking a real 020 group writer.

    native_write(words, effective_mask, bit_offset, planes, byte_offset)
    is called only if the WHOLE source group and 16 destination pixels
    are visible and the bitfield fits within the physical planar row.
    Scalar fallback handles partial crop, left/right clipping, final
    source group padding and the final bytes of short destination rows.
    """
    if not isinstance(image, AGAPIC):
        raise ValueError("source must be AGAPIC")
    vals = (sx, sy, width, height, x, y, dst_w, dst_h, mode)
    if any(type(v) is not int for v in vals):
        raise ValueError("parameters must be integers, not bools")
    if (sx < 0 or sy < 0 or width <= 0 or height <= 0 or
        width > image.width or height > image.height or
        sx > image.width - width or sy > image.height - height):
        raise ValueError("invalid source crop")
    if not (-32768 <= x <= 32767 and -32768 <= y <= 32767):
        raise ValueError("destination origin exceeds signed 16-bit")
    if mode not in (0, 1) or (mode == 1 and not image.masked):
        raise ValueError("invalid draw mode or absent mask")
    if not (1 <= dst_w <= MAX_SIDE and 1 <= dst_h <= MAX_SIDE and
            dst_w * dst_h <= MAX_PIXELS):
        raise ValueError("invalid target dimensions")
    min_stride = ((dst_w + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if type(stride) is not int or stride < min_stride or stride & 1:
        raise ValueError("invalid bitmap stride")
    if (not isinstance(planes, list) or len(planes) != image.depth or
        any(not isinstance(p, bytearray) or len(p) < stride * dst_h
            for p in planes)):
        raise ValueError("wrong plane count or insufficient destination")
    if not callable(native_write):
        raise ValueError("native writer missing")
    # Full bank-wide verification precedes *every* destination write.
    if parse_payload(image.raw) != image:
        raise ValueError("AGAPIC metadata differs from payload")

    literal, repeat = _packet_counts(image)
    pixels = native_groups = fallback_pixels = 0
    for source_y in range(sy, sy + height):
        dest_y = y + source_y - sy
        if not 0 <= dest_y < dst_h:
            continue
        for gi, group in enumerate(image.row_groups(source_y)):
            group_x = gi * 16
            left = max(sx, group_x)
            right = min(sx + width, group_x + 16, image.width)
            if left >= right:
                continue
            words = unpack(">" + "H" * (image.depth + int(image.masked)), group)
            mask = words[0] if mode == 1 else 0xffff
            colours = words[int(image.masked):]
            dest_start = x + group_x - sx
            whole_source = left == group_x and right == group_x + 16
            whole_target = 0 <= dest_start and dest_start + 16 <= dst_w
            if whole_source and whole_target:
                bit_offset = dest_start & 7
                byte_offset = dest_y * stride + dest_start // 8
                access = 2 if bit_offset == 0 else 3
                # Check the physical *row* end, not only plane allocation!
                if byte_offset + access <= (dest_y + 1) * stride:
                    if mask:
                        native_write(colours, mask, bit_offset, planes,
                                     byte_offset)
                        native_groups += 1
                        pixels += mask.bit_count()
                    continue
            for source_x in range(left, right):
                dx = x + source_x - sx
                if not 0 <= dx < dst_w:
                    continue
                bit = 0x8000 >> (source_x - group_x)
                if not (mask & bit):
                    continue
                address = dest_y * stride + dx // 8
                dest_bit = 0x80 >> (dx & 7)
                for plane, word in zip(planes, colours):
                    if word & bit:
                        plane[address] |= dest_bit
                    else:
                        plane[address] &= 255 ^ dest_bit
                fallback_pixels += 1
                pixels += 1
    return RenderResult(pixels, native_groups, fallback_pixels,
                        literal, repeat)
