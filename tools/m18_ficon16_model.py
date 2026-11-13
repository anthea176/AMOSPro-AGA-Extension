#!/usr/bin/env python3
"""M18/P1 HOST model of Unity 16x16 Fast Icons, CPU and Chip-word renderer.

Historical evidence: AmiDARK/AmosProfessionalUnity-SourceCode,
src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s, especially lines 53-63,
159-170, 1155-1196, 1225-1229, 1295-1304, 1382-1398, 1432-1587.

No AP20 token, native AGA command, real Blitter, timing or AMOS bank
installation is implemented by this Python module.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import Struct, unpack_from, pack

HEADER = Struct(">IHHHH")  # total_size, count, width, height, depth
ROW = Struct(">9H")        # inverted colour-zero mask, then 8 planar words
SIDE = 16
DEPTH = 8
SLOT_BYTES = SIDE * ROW.size  # 288 bytes/icon
MIN_COUNT = 4  # Unity's ReserveFIcons rejects fewer than four
MAX_COUNT = 4096  # conservative HOST model limit; not the original maximum


@dataclass(frozen=True)
class FIconBank:
    raw: bytes
    count: int

    def icon(self, number: int) -> bytes:
        if type(number) is not int or not (1 <= number <= self.count):
            raise ValueError("invalid 1-based Fast Icon ID")
        offset = HEADER.size + (number - 1) * SLOT_BYTES
        return self.raw[offset:offset + SLOT_BYTES]


@dataclass(frozen=True)
class DrawStats:
    visible_pixels: int
    changed_words: int
    staged_chip_bytes: int


def build_bank(icons: tuple[bytes, ...]) -> bytes:
    """Pack AGA 8-plane Unity-compatible 16x16 slots from colour indices.

    Zero means transparent *in masked mode*. No independent AGAPIC alpha.
    """
    if (not isinstance(icons, tuple) or
            not MIN_COUNT <= len(icons) <= MAX_COUNT):
        raise ValueError("invalid Fast Icon count")
    payload = bytearray()
    for icon in icons:
        if not isinstance(icon, bytes) or len(icon) != SIDE * SIDE:
            raise ValueError("each icon must contain exactly 256 byte indices")
        for y in range(SIDE):
            words = [0] * DEPTH
            preserve = 0
            for x in range(SIDE):
                colour = icon[y * SIDE + x]
                bit = 0x8000 >> x
                if not colour:
                    preserve |= bit
                else:
                    for plane in range(DEPTH):
                        if colour & (1 << plane):
                            words[plane] |= bit
            payload.extend(ROW.pack(preserve, *words))
    total = HEADER.size + len(payload)
    return HEADER.pack(total, len(icons), SIDE, SIDE, DEPTH) + payload


def parse_bank(raw: bytes) -> FIconBank:
    """Reject malformed sizes and noncanonical zero-colour masks."""
    if not isinstance(raw, bytes) or len(raw) < HEADER.size:
        raise ValueError("invalid Fast Icon bank")
    size, count, width, height, depth = HEADER.unpack_from(raw)
    if (width != SIDE or height != SIDE or depth != DEPTH or
            not MIN_COUNT <= count <= MAX_COUNT or
            size != len(raw) or size != HEADER.size + count * SLOT_BYTES):
        raise ValueError("invalid header or payload size")
    for offset in range(HEADER.size, len(raw), ROW.size):
        preserve, *planes = ROW.unpack_from(raw, offset)
        covered = 0
        for word in planes:
            covered |= word
        if preserve != (covered ^ 0xffff):
            raise ValueError("noncanonical F Icon colour-zero mask")
    return FIconBank(raw, count)


def _target(bank: FIconBank, number: int, x: int, y: int, mode: int,
            planes: list[bytearray], width: int, height: int,
            stride: int | None, alignment: str) -> tuple[bytes, int, int, int]:
    """Validate before writing a single destination pixel."""
    if not isinstance(bank, FIconBank) or parse_bank(bank.raw) != bank:
        raise ValueError("invalid source bank object")
    if not all(type(z) is int for z in (number, x, y, mode, width, height)):
        raise ValueError("integer parameters required")
    if mode not in (0, 1) or alignment not in ("pixel", "unity16"):
        raise ValueError("unsupported transparency or alignment mode")
    if not (-32768 <= x <= 32767 and -32768 <= y <= 32767):
        raise ValueError("destination coordinates outside signed 16-bit range")
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise ValueError("destination dimensions outside model limits")
    min_stride = ((width + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if (type(stride) is not int or stride < min_stride or stride % 2 or
            not isinstance(planes, list) or len(planes) != DEPTH or
            any(not isinstance(p, bytearray) or len(p) < stride * height
                for p in planes)):
        raise ValueError("invalid destination bitplanes/stride")
    icon = bank.icon(number)
    if alignment == "unity16":
        x &= ~15
        y &= ~15
    return icon, x, y, stride


def draw_cpu(bank: FIconBank, number: int, x: int, y: int, mode: int,
             planes: list[bytearray], width: int, height: int,
             stride: int | None = None, alignment: str = "pixel") -> DrawStats:
    """Independent CPU pixel model: Fast/Chip source, Chip destination."""
    icon, x, y, stride = _target(
        bank, number, x, y, mode, planes, width, height, stride, alignment)
    changed = 0
    visible = 0
    for iy in range(SIDE):
        dy = y + iy
        if not 0 <= dy < height:
            continue
        preserve, *colour_planes = ROW.unpack_from(icon, iy * ROW.size)
        for ix in range(SIDE):
            dx = x + ix
            if not 0 <= dx < width:
                continue
            bit = 0x8000 >> ix
            if mode == 1 and preserve & bit:
                continue
            off = dy * stride + (dx // 16) * 2
            dst_bit = 0x8000 >> (dx % 16)
            for plane, source_word in zip(planes, colour_planes):
                old = (plane[off] << 8) | plane[off + 1]
                updated = old | dst_bit if source_word & bit else old & (~dst_bit & 0xffff)
                plane[off:off + 2] = pack(">H", updated)
                changed += 1
            visible += 1
    return DrawStats(visible, changed, 0)


def draw_chip_words(bank: FIconBank, number: int, x: int, y: int, mode: int,
                    planes: list[bytearray], width: int, height: int,
                    stride: int | None = None, alignment: str = "pixel",
                    source_memory: str = "chip", allow_staging: bool = False
                    ) -> DrawStats:
    """Word-level *Blitter semantics* oracle, not actual hardware execution.

    A Fast source is rejected unless the caller explicitly models a
    Fast-to-Chip copy of one 288-byte slot; no speeds are inferred.
    """
    if source_memory not in ("chip", "fast") or type(allow_staging) is not bool:
        raise ValueError("unknown memory kind or staging mode")
    if source_memory == "fast" and not allow_staging:
        raise ValueError("Amiga Blitter cannot access Fast RAM directly")
    icon, x, y, stride = _target(
        bank, number, x, y, mode, planes, width, height, stride, alignment)
    source_word_index = x // 16
    shift = x % 16
    max_word = (width + 15) // 16
    last_mask = (0xffff << (16 - (width % 16))) & 0xffff if width % 16 else 0xffff
    writes = 0
    visible = 0
    for iy in range(SIDE):
        dy = y + iy
        if not 0 <= dy < height:
            continue
        preserve, *plane_words = ROW.unpack_from(icon, iy * ROW.size)
        draw_bits = 0xffff if mode == 0 else (~preserve & 0xffff)
        for ix in range(SIDE):
            if 0 <= x + ix < width and draw_bits & (0x8000 >> ix):
                visible += 1
        for plane, source in zip(planes, plane_words):
            for k in (0, 1):
                target_word = source_word_index + k
                if not 0 <= target_word < max_word:
                    continue
                shifted_data = (source >> shift) if k == 0 else ((source << (16-shift)) & 0xffff)
                shifted_mask = (draw_bits >> shift) if k == 0 else ((draw_bits << (16-shift)) & 0xffff)
                changed_mask = shifted_mask & (last_mask if target_word == max_word - 1 else 0xffff)
                if not changed_mask:
                    continue
                off = dy * stride + target_word * 2
                old = (plane[off] << 8) | plane[off + 1]
                new = (old & (~changed_mask & 0xffff)) | (shifted_data & changed_mask)
                plane[off:off + 2] = pack(">H", new)
                writes += 1
    staged = SLOT_BYTES if source_memory == "fast" and allow_staging else 0
    return DrawStats(visible, writes, staged)
