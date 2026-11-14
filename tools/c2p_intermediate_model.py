"""Host-only model of the safe chunky -> C2P-owned Chip -> AGA back workflow.

This does not execute c2p.library, an OS BltBitMap, or AMOS.  It models the
expected pixel, memory-layout and front/back invariants before native work.
"""
from __future__ import annotations

WIDTH = 320
HEIGHT = 256
DEPTH = 8
CHUNKY_BYTES = WIDTH * HEIGHT
PLANE_BYTES = CHUNKY_BYTES // 8
BYTES_PER_ROW = WIDTH // 8


class Bitmap:
    """A virtual 8-plane bitmap, with either planar or interleaved rows.

    Its planes are independently addressable even when the byte storage is
    interleaved, as graphics.library APIs expect from a struct BitMap.
    """

    def __init__(self, *, interleaved: bool = False, padding: int = 0):
        if padding < 0 or padding % 2:
            raise ValueError("invalid row padding")
        self.interleaved = interleaved
        if interleaved:
            self.row_stride = BYTES_PER_ROW * DEPTH + padding
            self.memory = bytearray(self.row_stride * HEIGHT)
            self.plane_memories = None
        else:
            self.row_stride = BYTES_PER_ROW + padding
            self.memory = None
            self.plane_memories = [bytearray(self.row_stride * HEIGHT) for _ in range(DEPTH)]

    def write(self, plane: int, row: int, data: bytes | bytearray) -> None:
        if not 0 <= plane < DEPTH or not 0 <= row < HEIGHT or len(data) != BYTES_PER_ROW:
            raise ValueError("invalid plane row")
        if self.interleaved:
            start = row * self.row_stride + plane * BYTES_PER_ROW
            self.memory[start:start + BYTES_PER_ROW] = data
        else:
            start = row * self.row_stride
            self.plane_memories[plane][start:start + BYTES_PER_ROW] = data

    def read(self, plane: int, row: int) -> bytes:
        if not 0 <= plane < DEPTH or not 0 <= row < HEIGHT:
            raise ValueError("invalid plane row")
        if self.interleaved:
            start = row * self.row_stride + plane * BYTES_PER_ROW
            return bytes(self.memory[start:start + BYTES_PER_ROW])
        start = row * self.row_stride
        return bytes(self.plane_memories[plane][start:start + BYTES_PER_ROW])

    def packed_bytes(self) -> bytes:
        return b"".join(self.read(p, y) for p in range(DEPTH) for y in range(HEIGHT))


def chunky_to_owned_bitmap(chunky: bytes | bytearray) -> Bitmap:
    """8-bit planar reference packing, not the actual SDK implementation."""
    if len(chunky) != CHUNKY_BYTES:
        raise ValueError("chunky source must contain exactly 81920 bytes")
    result = Bitmap()
    for y in range(HEIGHT):
        src = memoryview(chunky)[y * WIDTH:(y + 1) * WIDTH]
        for bitplane in range(DEPTH):
            row = bytearray(BYTES_PER_ROW)
            for x in range(WIDTH):
                if src[x] & (1 << bitplane):
                    row[x >> 3] |= 0x80 >> (x & 7)
            result.write(bitplane, y, row)
    return result


def bitmap_to_chunky(bitmap: Bitmap) -> bytes:
    """Independent planar decoder for full-256-color content comparisons."""
    result = bytearray(CHUNKY_BYTES)
    for y in range(HEIGHT):
        rows = [bitmap.read(p, y) for p in range(DEPTH)]
        for x in range(WIDTH):
            mask = 0x80 >> (x & 7)
            idx = x >> 3
            result[y * WIDTH + x] = sum((1 << p) for p in range(DEPTH) if rows[p][idx] & mask)
    return bytes(result)


def blit_bitmaps(source: Bitmap, back: Bitmap) -> None:
    """Pixel-exact virtual equivalent of whole-area, all-plane BltBitMap."""
    for plane in range(DEPTH):
        for row in range(HEIGHT):
            back.write(plane, row, source.read(plane, row))


class DoubleBuffer:
    """Fail-closed state machine: never blit to front or to a back not Safe."""
    def __init__(self, *, interleaved_back: bool = False):
        self.buffers = [Bitmap(interleaved=interleaved_back), Bitmap(interleaved=interleaved_back)]
        self.front = 0
        self.safe = True
        self.closed = False
        self.blit_count = 0

    def convert_and_blit(self, chunky: bytes | bytearray) -> bool:
        if self.closed or not self.safe or len(chunky) != CHUNKY_BYTES:
            return False
        source = chunky_to_owned_bitmap(chunky)
        back = self.buffers[1 - self.front]
        blit_bitmaps(source, back)
        self.blit_count += 1
        return True

    def swap(self) -> bool:
        if self.closed or not self.safe:
            return False
        self.front = 1 - self.front
        self.safe = False  # do not write again until an external Safe acknowledgement
        return True

    def set_safe(self, ready: bool) -> None:
        self.safe = ready and not self.closed

    def close(self) -> None:
        self.closed = True
        self.safe = False

