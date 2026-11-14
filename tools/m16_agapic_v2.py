#!/usr/bin/env python3
"""AGAPIC v2 host codec, sharing the *unchanged* M16 AGAPIC v1 RLE core.

No new AP20 token. No native renderer. Palette selection is a read-only host
model for the later combined Bank Palette Apply / Fade native commands.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from m16_agapic import (
    ABK_HEADER, BANK_NAME, FLAG_MASK, HEADER, MAX_PAYLOAD,
    pack_image as pack_image_v1, parse_payload as parse_payload_v1,
)

EXTENSION = struct.Struct('>IHHIII3I')
VERSION_V2 = 2
FLAG_PALETTE = 2
RGB24 = 1
HEADER_V2_SIZE = HEADER.size + EXTENSION.size
AGAPAL_SLOT = struct.Struct('>IHH')


def align4(x: int) -> int:
    return (x + 3) & ~3


@dataclass(frozen=True)
class VersionedImage:
    version: int
    image: object  # Existing m16_agapic.AGAPIC, with v1-encoded RLE validation
    mode_id: int | None
    palette: bytes | None
    original: bytes

    @property
    def depth(self) -> int:
        return self.image.depth

    @property
    def masked(self) -> bool:
        return self.image.masked


def _mode_id(value: int) -> None:
    if (not isinstance(value, int) or isinstance(value, bool) or
        not 0 < value < 0xffffffff):
        raise ValueError('v2 ModeID must be a valid non-reserved U32')


def pack_image_v2(width: int, height: int, depth: int, pixels: bytes,
                  palette: bytes, mode_id: int, mask: bytes | None = None) -> bytes:
    """Wrap the byte-identical v1 planar RLE stream with mandatory v2 metadata."""
    _mode_id(mode_id)
    # Validation of dimensions/depth/pixels/mask is delegated to stable v1.
    v1 = pack_image_v1(width, height, depth, pixels, mask)
    n = 1 << depth
    if not isinstance(palette, bytes) or len(palette) != 3 * n:
        raise ValueError('v2 requires a complete 3*(2^Depth) RGB24 palette')
    old = HEADER.unpack_from(v1)
    table = align4(HEADER_V2_SIZE + len(palette))
    stream = table + 4 * (height + 1)
    old_table = old[8]
    old_stream = old[9]
    old_rows = struct.unpack_from('>' + 'I' * (height + 1), v1, old_table)
    delta = stream - old_stream
    rows = [pos + delta for pos in old_rows]
    total = rows[-1]
    if total > MAX_PAYLOAD:
        raise ValueError('v2 payload exceeds the existing limit')
    head = HEADER.pack(old[0], VERSION_V2, old[2] | FLAG_PALETTE,
                       old[3], width, height, depth, old[7], table, stream, total)
    ext = EXTENSION.pack(mode_id, n, RGB24, HEADER_V2_SIZE,
                         len(palette), HEADER_V2_SIZE, 0, 0, 0)
    result = (head + ext + palette + bytes(table - HEADER_V2_SIZE - len(palette))
              + struct.pack('>' + 'I' * (height + 1), *rows)
              + v1[old_stream:])
    assert len(result) == total
    return result


def parse_payload_any(raw: bytes) -> VersionedImage:
    """Preserve v1 strict parser; convert v2 to v1 *only for host RLE checks*."""
    if not isinstance(raw, bytes) or not HEADER.size <= len(raw) <= MAX_PAYLOAD:
        raise ValueError('invalid AGAPIC payload size')
    common = HEADER.unpack_from(raw)
    if common[1] == 1:
        return VersionedImage(1, parse_payload_v1(raw), None, None, raw)
    if common[1] != VERSION_V2 or len(raw) < HEADER_V2_SIZE:
        raise ValueError('unsupported AGAPIC version/header')
    magic, _ver, flags, codec, width, height, depth, groupbytes, table, stream, total = common
    if magic != b'AGAPIC' or flags not in (2, 3) or codec != 1:
        raise ValueError('invalid v2 magic/flags/codec')
    if not (1 <= width <= 4096 and 1 <= height <= 4096 and
            1 <= depth <= 8 and width * height <= 4 * 1024 * 1024):
        raise ValueError('invalid v2 dimensions/depth')
    masked = bool(flags & FLAG_MASK)
    if groupbytes != 2 * (depth + int(masked)) or total != len(raw):
        raise ValueError('invalid v2 group size/payload total')
    mode, count, fmt, paloff, palbytes, headbytes, r0, r1, r2 = EXTENSION.unpack_from(raw, 32)
    _mode_id(mode)
    if (fmt != RGB24 or count != (1 << depth) or
        paloff != HEADER_V2_SIZE or palbytes != count * 3 or
        headbytes != HEADER_V2_SIZE or r0 or r1 or r2):
        raise ValueError('invalid or incomplete v2 RGB24 metadata')
    wanted_table = align4(HEADER_V2_SIZE + palbytes)
    if (table != wanted_table or stream != table + 4 * (height + 1) or
        stream > total or any(raw[HEADER_V2_SIZE + palbytes:table])):
        raise ValueError('invalid palette padding or row table')
    offsets = struct.unpack_from('>' + 'I' * (height + 1), raw, table)
    if (offsets[0] != stream or offsets[-1] != total or
        any(offsets[i] >= offsets[i+1] for i in range(height))):
        raise ValueError('invalid v2 row offsets')
    delta = stream - (HEADER.size + 4 * (height + 1))
    legacy_offsets = [o - delta for o in offsets]
    legacy_stream = HEADER.size + 4 * (height + 1)
    legacy_total = legacy_offsets[-1]
    v1head = HEADER.pack(magic, 1, flags & FLAG_MASK, codec, width, height,
                         depth, groupbytes, HEADER.size, legacy_stream,
                         legacy_total)
    v1bytes = (v1head + struct.pack('>'+'I'*(height+1), *legacy_offsets)
               + raw[stream:])
    if len(v1bytes) != legacy_total:
        raise ValueError('invalid v2 RLE relocation')
    # Exact v1 strict validation for every row, RLE packet and unused bit.
    image = parse_payload_v1(v1bytes)
    return VersionedImage(VERSION_V2, image, mode,
                          raw[HEADER_V2_SIZE:HEADER_V2_SIZE+palbytes], raw)


def parse_abk_any(abk: bytes) -> tuple[int, int, VersionedImage]:
    if not isinstance(abk, bytes) or len(abk) < ABK_HEADER.size:
        raise ValueError('truncated ABK')
    magic, bank, flags, length, name = ABK_HEADER.unpack_from(abk)
    if (magic != b'AmBk' or not 5 <= bank <= 65535 or
        flags not in (1, 3) or length != len(abk) - 12 or name != BANK_NAME):
        raise ValueError('bad AmBk AGAPIC envelope')
    return bank, flags, parse_payload_any(abk[ABK_HEADER.size:])


def make_abk_v2(bank: int, payload: bytes, *, chip: bool = False) -> bytes:
    if not isinstance(bank, int) or isinstance(bank, bool) or not 5 <= bank <= 65535:
        raise ValueError('invalid AMOS bank number')
    image = parse_payload_any(payload)
    if image.version != VERSION_V2:
        raise ValueError('not AGAPIC v2')
    return ABK_HEADER.pack(b'AmBk', bank, 3 if chip else 1,
                           len(payload) + 8, BANK_NAME) + payload


def compatible_screen(v: VersionedImage, *, screen_depth: int,
                      screen_mode_id: int | None = None, indexed: bool = True) -> bool:
    if not indexed or screen_depth != v.depth:
        return False
    return v.version == 1 or screen_mode_id == v.mode_id


def select_bank_palette(payload: bytes, index: int, *, screen_depth: int,
                        screen_mode_id: int | None = None,
                        indexed: bool = True) -> bytes:
    """Read-only host selector for unified Bank Palette Apply/Fade.

    AGAPAL v1: selected palette, may be partial. AGAPIC v2: full palette at
    index 0, strict ModeID. AGAPIC v1: rejected. Actual LoadRGB32, WaitTOF,
    bank resolution, ABI and memory ownership belong to the future native API.
    """
    if not isinstance(payload, bytes) or not isinstance(index, int) or index < 0:
        raise ValueError('invalid payload/index')
    if not indexed or not 1 <= screen_depth <= 8:
        raise ValueError('unsupported AGA screen')
    if payload[:6] == b'AGAPIC':
        img = parse_payload_any(payload)
        if img.version != 2 or index != 0 or not compatible_screen(
                img, screen_depth=screen_depth,
                screen_mode_id=screen_mode_id, indexed=indexed):
            raise ValueError('AGAPIC image has no matching palette/mode')
        assert img.palette is not None
        return img.palette
    if payload[:6] != b'AGAPAL' or len(payload) < 16:
        raise ValueError('unsupported palette bank format')
    magic, version, slots, flags, reserved = struct.unpack_from('>6sHHHI', payload)
    if (magic != b'AGAPAL' or version != 1 or not 1 <= slots <= 256 or
            flags != 0 or reserved != 0 or len(payload) != 16 + 776 * slots or
            index >= slots):
        raise ValueError('bad AGAPAL layout/index')
    offset, count, descflags = AGAPAL_SLOT.unpack_from(payload, 16 + 8 * index)
    if (offset != 16 + 8 * slots + 768 * index or
            not 1 <= count <= 1 << screen_depth or descflags != 0):
        raise ValueError('invalid or incompatible AGAPAL slot')
    # Source has a full 768-byte palette slot, but only 3*count bytes matter.
    return payload[offset:offset + 3 * count]
