#!/usr/bin/env python3
"""AGAPIC v1: M16 host-side planar RLE bank format and CPU renderer model.

Design/prototype ONLY. No AP20 command is added here; WinUAE, 68000/020
timings, memory-bank placement and actual CPU writes still need validation.

All multi-byte quantities are big-endian. Each compressed scanline stores
16-pixel groups (optional 16-bit mask followed by depth plane words).
Control byte 0..127: 1..128 literal groups. Byte 128..255: 1..128 copies
of one group. Group bits run from pixel 0 at bit 15 to pixel 15 at bit 0.
Opaque mode ignores the optional mask; mask mode preserves the destination
where mask bits are zero, INCLUDING when the source colour index is zero.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = b"AGAPIC"
BANK_NAME = b"AGAPIC  "
VERSION = 1
CODEC_ROW_RLE = 1
FLAG_MASK = 1
HEADER = struct.Struct(">6s7H3I")
ABK_HEADER = struct.Struct(">4sHHI8s")
MAX_PIXELS = 4 * 1024 * 1024
MAX_PAYLOAD = 16 * 1024 * 1024
MAX_SIDE = 4096


@dataclass(frozen=True)
class AGAPIC:
    raw: bytes
    width: int
    height: int
    depth: int
    masked: bool
    group_bytes: int
    offsets: tuple[int, ...]

    @property
    def groups_per_row(self) -> int:
        return (self.width + 15) // 16

    def row_groups(self, row: int):
        if not 0 <= row < self.height:
            raise ValueError("row out of range")
        start, stop = self.offsets[row:row + 2]
        return _decode_groups(self.raw, start, stop, self.group_bytes,
                              self.groups_per_row)


def _dimensions(width: int, height: int, depth: int) -> None:
    if (not all(isinstance(v, int) and not isinstance(v, bool)
                for v in (width, height, depth)) or
        not (1 <= width <= MAX_SIDE and 1 <= height <= MAX_SIDE) or
        not 1 <= depth <= 8 or width * height > MAX_PIXELS):
        raise ValueError("dimensions or colour depth out of range")


def _encode_row(groups: list[bytes]) -> bytes:
    out = bytearray()
    pos = 0
    while pos < len(groups):
        run = 1
        while (pos + run < len(groups) and run < 128 and
               groups[pos + run] == groups[pos]):
            run += 1
        if run >= 2:
            out.append(0x80 | (run - 1))
            out.extend(groups[pos])
            pos += run
            continue
        # A literal packet ends before any upcoming repeated group.
        start = pos
        pos += 1
        while pos < len(groups) and pos - start < 128:
            if pos + 1 < len(groups) and groups[pos] == groups[pos + 1]:
                break
            pos += 1
        count = pos - start
        out.append(count - 1)
        for group in groups[start:pos]:
            out.extend(group)
    return bytes(out)


def _decode_groups(raw: bytes, start: int, stop: int, size: int, total: int):
    pos = start
    produced = 0
    while produced < total:
        if pos >= stop:
            raise ValueError("RLE row ended before all groups")
        control = raw[pos]
        pos += 1
        count = (control & 0x7f) + 1
        if produced + count > total:
            raise ValueError("RLE packet exceeds row width")
        if control & 0x80:
            if pos + size > stop:
                raise ValueError("truncated RLE repeat group")
            group = raw[pos:pos + size]
            pos += size
            for _ in range(count):
                yield group
        else:
            end = pos + count * size
            if end > stop:
                raise ValueError("truncated RLE literal groups")
            for offset in range(pos, end, size):
                yield raw[offset:offset + size]
            pos = end
        produced += count
    if pos != stop:
        raise ValueError("trailing bytes in RLE row")


def pack_image(width: int, height: int, depth: int, pixels: bytes,
               mask: bytes | None = None) -> bytes:
    """Pack indexed pixels + optional independent 0/1 mask, top-down."""
    _dimensions(width, height, depth)
    if not isinstance(pixels, bytes) or len(pixels) != width * height:
        raise ValueError("pixels must be exactly width*height bytes")
    if any(pixel >= (1 << depth) for pixel in pixels):
        raise ValueError("pixel index is outside source depth")
    if mask is not None:
        if (not isinstance(mask, bytes) or len(mask) != len(pixels) or
            any(bit not in (0, 1) for bit in mask)):
            raise ValueError("mask must contain one 0/1 byte per pixel")
    masked = mask is not None
    group_bytes = 2 * (depth + int(masked))
    groups_per_row = (width + 15) // 16
    table_offset = HEADER.size
    stream_offset = table_offset + 4 * (height + 1)
    rows: list[bytes] = []
    offsets = [stream_offset]
    for y in range(height):
        row: list[bytes] = []
        for g in range(groups_per_row):
            plane_words = [0] * depth
            mask_word = 0
            for bit in range(16):
                x = g * 16 + bit
                if x >= width:
                    break
                p = y * width + x
                pixel = pixels[p]
                if masked and mask[p]:
                    mask_word |= 0x8000 >> bit
                for plane in range(depth):
                    if pixel & (1 << plane):
                        plane_words[plane] |= 0x8000 >> bit
            words = ([mask_word] if masked else []) + plane_words
            row.append(struct.pack(">" + "H" * len(words), *words))
        packed = _encode_row(row)
        rows.append(packed)
        offsets.append(offsets[-1] + len(packed))
    total = offsets[-1]
    if total > MAX_PAYLOAD:
        raise ValueError("bank payload exceeds 16 MiB limit")
    head = HEADER.pack(MAGIC, VERSION, FLAG_MASK if masked else 0,
                       CODEC_ROW_RLE, width, height, depth, group_bytes,
                       table_offset, stream_offset, total)
    payload = head + struct.pack(">" + "I" * len(offsets), *offsets) + b"".join(rows)
    assert len(payload) == total
    return payload


def parse_payload(payload: bytes) -> AGAPIC:
    """Strict, complete validation BEFORE any simulated destination write."""
    if not isinstance(payload, bytes) or not HEADER.size <= len(payload) <= MAX_PAYLOAD:
        raise ValueError("invalid payload size")
    magic, version, flags, codec, width, height, depth, group_bytes, table, stream, size = HEADER.unpack_from(payload)
    if magic != MAGIC or version != VERSION:
        raise ValueError("not AGAPIC version 1")
    _dimensions(width, height, depth)
    if flags & ~FLAG_MASK or codec != CODEC_ROW_RLE:
        raise ValueError("unknown flags or codec")
    masked = bool(flags & FLAG_MASK)
    if group_bytes != 2 * (depth + int(masked)):
        raise ValueError("inconsistent group size")
    if (table != HEADER.size or stream != table + 4 * (height + 1) or
        size != len(payload) or stream > size):
        raise ValueError("invalid offsets or total length")
    offsets = struct.unpack_from(">" + "I" * (height + 1), payload, table)
    if offsets[0] != stream or offsets[-1] != size:
        raise ValueError("invalid row-table boundaries")
    if any(offsets[i] >= offsets[i + 1] for i in range(height)):
        raise ValueError("empty, reversed or overlapping row")
    image = AGAPIC(payload, width, height, depth, masked, group_bytes, offsets)
    rem = width % 16
    unused = (1 << (16 - rem)) - 1 if rem else 0
    for y in range(height):
        n = 0
        for group in image.row_groups(y):
            if len(group) != group_bytes:
                raise ValueError("incorrect RLE group size")
            if unused and n == image.groups_per_row - 1:
                if any(struct.unpack_from(">H", group, i)[0] & unused
                       for i in range(0, group_bytes, 2)):
                    raise ValueError("nonzero unused padding pixels")
            n += 1
        if n != image.groups_per_row:
            raise ValueError("incorrect RLE group count")
    return image


def unpack_image(image: AGAPIC) -> tuple[bytes, bytes | None]:
    pixels = bytearray(image.width * image.height)
    masks = bytearray(len(pixels)) if image.masked else None
    for y in range(image.height):
        for g, group in enumerate(image.row_groups(y)):
            words = struct.unpack(">" + "H" * (image.depth + int(image.masked)), group)
            planes = words[int(image.masked):]
            for bit in range(16):
                x = g * 16 + bit
                if x >= image.width:
                    break
                v = 0
                for plane, word in enumerate(planes):
                    if word & (0x8000 >> bit):
                        v |= 1 << plane
                pos = y * image.width + x
                pixels[pos] = v
                if masks is not None:
                    masks[pos] = int(bool(words[0] & (0x8000 >> bit)))
    return bytes(pixels), bytes(masks) if masks is not None else None


def make_abk(bank_number: int, payload: bytes, *, chip: bool = False) -> bytes:
    """Wrap AGAPIC data in native AmBk DATA envelope, as in AGAPAL tooling.

    DATA flags 1 (Fast preference) / 3 (Chip) do NOT guarantee where AMOS
    will actually allocate the loaded bank. Check List Bank in WinUAE.
    """
    if not isinstance(bank_number, int) or not 5 <= bank_number <= 65535:
        raise ValueError("AMOS bank number must be 5..65535")
    parse_payload(payload)
    return ABK_HEADER.pack(b"AmBk", bank_number, 3 if chip else 1,
                           len(payload) + 8, BANK_NAME) + payload


def parse_abk(abk: bytes) -> tuple[int, int, AGAPIC]:
    if not isinstance(abk, bytes) or len(abk) < ABK_HEADER.size:
        raise ValueError("short ABK file")
    magic, bank, flags, length, name = ABK_HEADER.unpack_from(abk)
    if (magic != b"AmBk" or not 5 <= bank <= 65535 or
        flags not in (1, 3) or length != len(abk) - 12 or
        name != BANK_NAME):
        raise ValueError("invalid native AMOS DATA ABK header")
    return bank, flags, parse_payload(abk[ABK_HEADER.size:])


def render_cpu_model(image: AGAPIC, x: int, y: int, planes: list[bytearray],
                     dest_width: int, dest_height: int, mode: int,
                     stride: int | None = None) -> int:
    """68000-oriented PLANAR-WORD reference model; not a timed native renderer.

    mode 0: opaque, including pen 0. mode 1: use 1-bit independent mask.
    Destination planes model Chip RAM; a native implementation must test
    actual Intuition ownership, BitMap pointers and Safe independently.
    """
    if (mode not in (0, 1) or (mode == 1 and not image.masked) or
        not isinstance(x, int) or not isinstance(y, int) or
        not (-32768 <= x <= 32767 and -32768 <= y <= 32767)):
        raise ValueError("invalid mode or coordinates")
    if (not 1 <= dest_width <= MAX_SIDE or not 1 <= dest_height <= MAX_SIDE or
        len(planes) != image.depth):
        raise ValueError("unsupported destination dimensions/depth")
    min_stride = ((dest_width + 15) // 16) * 2
    if stride is None:
        stride = min_stride
    if stride < min_stride or stride & 1:
        raise ValueError("invalid planar stride")
    if any(not isinstance(p, bytearray) or len(p) < stride * dest_height
           for p in planes):
        raise ValueError("insufficient destination plane memory")
    written = 0
    max_word = (dest_width + 15) // 16
    rem = image.width & 15
    valid_last = 0xffff if not rem else (0xffff << (16 - rem)) & 0xffff
    for sy in range(image.height):
        dy = sy + y
        if not 0 <= dy < dest_height:
            continue
        for g, group in enumerate(image.row_groups(sy)):
            words = struct.unpack(">" + "H" * (image.depth + int(image.masked)), group)
            src_planes = words[int(image.masked):]
            src_mask = words[0] if mode == 1 else 0xffff
            if g == image.groups_per_row - 1:
                src_mask &= valid_last
            start = x + 16 * g
            dw, shift = divmod(start, 16)
            for half in range(1 if shift == 0 else 2):
                index = dw + half
                if not 0 <= index < max_word:
                    continue
                word_mask = (src_mask >> shift) if half == 0 else (
                    (src_mask << (16 - shift)) & 0xffff)
                if index == max_word - 1 and dest_width & 15:
                    word_mask &= (0xffff << (16 - (dest_width & 15))) & 0xffff
                if not word_mask:
                    continue
                written += word_mask.bit_count()
                address = dy * stride + index * 2
                inv = ~word_mask & 0xffff
                for plane, value in zip(planes, src_planes):
                    src_word = (value >> shift) if half == 0 else (
                        (value << (16 - shift)) & 0xffff)
                    old = (plane[address] << 8) | plane[address + 1]
                    new = (old & inv) | (src_word & word_mask)
                    plane[address] = new >> 8
                    plane[address + 1] = new & 255
    return written


def stats(payload: bytes) -> dict[str, int | str]:
    image = parse_payload(payload)
    raw_groups = image.groups_per_row * image.height * image.group_bytes
    return dict(width=image.width, height=image.height, depth=image.depth,
                mode="masked" if image.masked else "opaque",
                planar_bytes=raw_groups, packed_bytes=len(payload),
                sha256=hashlib.sha256(payload).hexdigest())


def write_abk(path: Path, width: int, height: int, depth: int,
              pixels: bytes, mask: bytes | None, bank: int) -> dict[str, int | str]:
    payload = pack_image(width, height, depth, pixels, mask)
    binary = make_abk(bank, payload)
    path.write_bytes(binary)
    return stats(payload)
