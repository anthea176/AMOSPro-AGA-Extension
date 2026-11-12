#!/usr/bin/env python3
"""M16 AGAPIC capture reference model (HOST ONLY, no AP20 command).

Mirrors the approved future Aga Image Capture bank, X/Y/W/H and
TransparentIndex contract. Source is the private AGA back buffer represented
as planar bytes (one plane per buffer). There is NO implicit Swap, no change
to source planes or palette, and no partial capture.

The creation model uses a mapping of AMOS bank numbers to .abk bytes.
Its Fast-first/Chip-fallback capacity arguments are *simulated* capacities,
not Exec TypeOfMem evidence or a claim about Amiga memory placement.
R46 C1 is unchanged; native 68000 and Compiler Gates remain open.
"""
from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass

from m16_agapic import MAX_SIDE, MAX_PIXELS, make_abk, pack_image


@dataclass(frozen=True)
class CaptureResult:
    """Zero means refuse with no bank created; location is only a model."""
    ok: int
    location: str | None
    payload_length: int


def _integer(value: object) -> bool:
    return type(value) is int


def capture_payload_model(
    planes: Sequence[bytes | bytearray],
    screen_width: int,
    screen_height: int,
    x: int,
    y: int,
    width: int,
    height: int,
    transparent_index: int = -1,
    *,
    stride: int | None = None,
) -> bytes:
    """Compress a strictly in-bounds rectangle from AGA planar back-buffer.

    Raises ValueError on malformed parameters or buffers BEFORE generating
    any encoded output. Never modifies source planes or the palette.
    Pixel bit 7 represents the leftmost pixel within each source byte.
    Each plane uses a word-aligned BytesPerRow (as Amiga BitMap does).
    """
    vals = (screen_width, screen_height, x, y, width, height,
            transparent_index)
    if not all(_integer(v) for v in vals):
        raise ValueError("capture parameters must be integers")
    if (not (1 <= screen_width <= MAX_SIDE and
             1 <= screen_height <= MAX_SIDE and
             1 <= width <= MAX_SIDE and 1 <= height <= MAX_SIDE) or
        x < 0 or y < 0 or width > screen_width or
        height > screen_height or x > screen_width - width or
        y > screen_height - height or width * height > MAX_PIXELS):
        raise ValueError("capture rectangle exceeds back-buffer bounds")

    if not isinstance(planes, (tuple, list)) or not 1 <= len(planes) <= 8:
        raise ValueError("AGA requires 1 to 8 bitplanes")
    depth = len(planes)
    if not -1 <= transparent_index < (1 << depth):
        raise ValueError("invalid transparent colour for AGA depth")
    min_stride = ((screen_width + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if not _integer(stride) or stride < min_stride or stride & 1:
        raise ValueError("invalid source bitmap stride")
    if any(not isinstance(p, (bytes, bytearray)) or
           len(p) < stride * screen_height for p in planes):
        raise ValueError("source bitmap plane missing or too short")

    pixels = bytearray(width * height)
    mask = bytearray(len(pixels)) if transparent_index != -1 else None
    pos = 0
    for yy in range(y, y + height):
        start = yy * stride
        for xx in range(x, x + width):
            address = start + (xx >> 3)
            bit = 0x80 >> (xx & 7)
            colour = 0
            for index, plane in enumerate(planes):
                if plane[address] & bit:
                    colour |= 1 << index
            pixels[pos] = colour
            if mask is not None:
                mask[pos] = int(colour != transparent_index)
            pos += 1
    return pack_image(width, height, depth, bytes(pixels),
                      bytes(mask) if mask is not None else None)


def create_capture_bank_model(
    banks: MutableMapping[int, bytes],
    bank_number: int,
    planes: Sequence[bytes | bytearray],
    screen_width: int,
    screen_height: int,
    x: int,
    y: int,
    width: int,
    height: int,
    transparent_index: int = -1,
    *,
    stride: int | None = None,
    fast_free: int,
    chip_free: int,
) -> CaptureResult:
    """Model prospective bank creation, never overwrite any existing bank.

    Refusals return 0 with no mutations. Allocation is modeled as
    payload + 24-byte AMOS bank header; actual AMOS list allocator overhead,
    flags and physical memory placement must be verified on WinUAE.
    On success the .abk is marked DATA/Fast-preferred (flag 1), even
    when simulated placement falls back to Chip memory.
    """
    failure = CaptureResult(0, None, 0)
    if (not isinstance(banks, MutableMapping) or
        not _integer(bank_number) or not 5 <= bank_number <= 65535 or
        bank_number in banks or
        not _integer(fast_free) or not _integer(chip_free) or
        fast_free < 0 or chip_free < 0):
        return failure
    try:
        payload = capture_payload_model(
            planes, screen_width, screen_height, x, y, width, height,
            transparent_index, stride=stride)
        required = len(payload) + 24
        location = ("fast" if fast_free >= required else
                    "chip" if chip_free >= required else None)
        if location is None:
            return failure
        # Build the entire native ABK before touching the bank registry.
        abk = make_abk(bank_number, payload)
        banks[bank_number] = abk
    except (ValueError, TypeError, MemoryError, OverflowError):
        return failure
    return CaptureResult(1, location, len(payload))
