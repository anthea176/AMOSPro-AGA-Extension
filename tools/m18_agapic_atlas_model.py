#!/usr/bin/env python3
"""M18/P0 host-only AGAPIC v1 atlas/subrectangle renderer model.

Uses one already validated AGAPIC v1 image as a sprite sheet: no new
bank format, public command, AP20 token or native 68000 code. Decode
one source row at a time; never allocate a full uncompressed atlas.
The destination models the private AGA back buffer, not measured Chip.
Return value is pixels written, NOT a public AMOS success return.
"""
from __future__ import annotations

from struct import unpack
from m16_agapic import AGAPIC, MAX_PIXELS, MAX_SIDE, parse_payload


def _integer(value: object) -> bool:
    return type(value) is int


def grid_frame_rect(image: AGAPIC, frame_w: int, frame_h: int,
                    index: int) -> tuple[int, int, int, int]:
    """Zero-based row-major frame selection, no partial grid cells."""
    if not isinstance(image, AGAPIC):
        raise ValueError("source must be a validated AGAPIC image")
    if (not all(_integer(v) for v in (frame_w, frame_h, index)) or
        frame_w <= 0 or frame_h <= 0 or
        frame_w > image.width or frame_h > image.height or
        image.width % frame_w or image.height % frame_h):
        raise ValueError("frame geometry does not divide the atlas exactly")
    cols = image.width // frame_w
    rows = image.height // frame_h
    if not 0 <= index < cols * rows:
        raise ValueError("frame index out of range")
    return ((index % cols) * frame_w, (index // cols) * frame_h,
            frame_w, frame_h)


def render_region_cpu_model(image: AGAPIC, src_x: int, src_y: int,
                            width: int, height: int, dst_x: int, dst_y: int,
                            planes: list[bytearray], dest_w: int, dest_h: int,
                            mode: int, stride: int | None = None) -> int:
    """Render a source rectangle into planar destination with clipping.

    Mode 0: opaque (including colour 0). Mode 1: independent mask, where
    mask bit 0 retains the destination. Invalid parameters or corrupt RLE
    refuse before any write. Valid off-screen destination clips.
    No palette, swap, VBL, Blitter or Safe operation is implied.
    """
    if not isinstance(image, AGAPIC):
        raise ValueError("source must be AGAPIC")
    values = (src_x, src_y, width, height, dst_x, dst_y, dest_w, dest_h, mode)
    if not all(_integer(v) for v in values):
        raise ValueError("coordinates, dimensions and mode must be integers")
    if (src_x < 0 or src_y < 0 or width <= 0 or height <= 0 or
        width > image.width or height > image.height or
        src_x > image.width - width or src_y > image.height - height):
        raise ValueError("source rectangle must be wholly inside the atlas")
    if not (-32768 <= dst_x <= 32767 and -32768 <= dst_y <= 32767):
        raise ValueError("destination origin outside signed 16-bit range")
    if mode not in (0, 1) or (mode == 1 and not image.masked):
        raise ValueError("masked draw requires a source mask")
    if (not 1 <= dest_w <= MAX_SIDE or not 1 <= dest_h <= MAX_SIDE or
        dest_w * dest_h > MAX_PIXELS):
        raise ValueError("destination dimensions out of range")
    min_stride = ((dest_w + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if not _integer(stride) or stride < min_stride or stride & 1:
        raise ValueError("invalid destination plane stride")
    if (not isinstance(planes, list) or len(planes) != image.depth or
        any(not isinstance(p, bytearray) or len(p) < stride * dest_h
            for p in planes)):
        raise ValueError("wrong depth or insufficient destination memory")

    # Validate every compressed row before touching the destination:
    # malformed late scanlines cannot leave partial rendering behind.
    # Validation streams groups and never expands the full image.
    if parse_payload(image.raw) != image:
        raise ValueError("inconsistent source metadata")

    count = 0
    word_format = ">" + "H" * (image.depth + int(image.masked))
    for sy in range(src_y, src_y + height):
        dy = dst_y + sy - src_y
        if dy < 0 or dy >= dest_h:
            continue
        for group_index, group in enumerate(image.row_groups(sy)):
            group_x = group_index * 16
            left = max(src_x, group_x)
            right = min(src_x + width, group_x + 16)
            if left >= right:
                continue
            words = unpack(word_format, group)
            mask_word = words[0] if mode == 1 else 0xffff
            colours = words[int(image.masked):]
            for sx in range(left, right):
                dx = dst_x + sx - src_x
                if dx < 0 or dx >= dest_w:
                    continue
                source_bit = 0x8000 >> (sx - group_x)
                if not (mask_word & source_bit):
                    continue
                off = dy * stride + (dx // 16) * 2
                dest_bit = 0x8000 >> (dx % 16)
                for plane, source_word in zip(planes, colours):
                    old = (plane[off] << 8) | plane[off + 1]
                    if source_word & source_bit:
                        new = old | dest_bit
                    else:
                        new = old & (~dest_bit & 0xffff)
                    plane[off] = new >> 8
                    plane[off + 1] = new & 255
                count += 1
    return count


def render_grid_frame_cpu_model(image: AGAPIC, frame_w: int, frame_h: int,
                                frame_index: int, dst_x: int, dst_y: int,
                                planes: list[bytearray], dest_w: int,
                                dest_h: int, mode: int,
                                stride: int | None = None) -> int:
    """Draw a grid frame from one AGAPIC v1 atlas without allocating a frame."""
    src_x, src_y, width, height = grid_frame_rect(
        image, frame_w, frame_h, frame_index)
    return render_region_cpu_model(image, src_x, src_y, width, height,
                                   dst_x, dst_y, planes, dest_w, dest_h,
                                   mode, stride)
