"""M18 CBlock copy prototype: independent CPU byte/word and Blitter-word models.

Only independent host functional evidence. No WinUAE speed, native ABI or DMA proof.
All surfaces are prevalidated Chip-resident planar bitmaps.
"""
from __future__ import annotations
from dataclasses import dataclass
from random import Random


@dataclass
class Surface:
    width: int
    height: int
    depth: int
    stride: int
    planes: list[bytearray]
    chip: bool = True

    @classmethod
    def make(cls, width: int, height: int, depth: int, *, chip: bool = True, seed: int = 0):
        if not (1 <= width <= 4096 and 1 <= height <= 4096 and 1 <= depth <= 8):
            raise ValueError("invalid geometry")
        stride = ((width + 15) // 16) * 2
        rng = Random(seed)
        return cls(width, height, depth, stride,
                   [bytearray(rng.randrange(256) for _ in range(stride * height))
                    for _ in range(depth)], chip)

    def clone(self):
        return Surface(self.width, self.height, self.depth, self.stride,
                       [bytearray(p) for p in self.planes], self.chip)

    def signature(self):
        return tuple(bytes(p) for p in self.planes)


def validate(src: Surface, dest: Surface, sx: int, sy: int, dx: int, dy: int,
             width: int, height: int, *, word_only: bool = False):
    if src is dest or any(p is q for p in src.planes for q in dest.planes):
        raise ValueError("overlapping source/destination not supported")
    if not src.chip or not dest.chip:
        raise ValueError("source and destination must both be real Chip")
    if src.depth != dest.depth or not (1 <= src.depth <= 8):
        raise ValueError("mismatched depth")
    for v in (sx, sy, dx, dy, width, height):
        if type(v) is not int or v < 0:
            raise ValueError("negative or non-integral geometry")
    if width <= 0 or height <= 0:
        raise ValueError("empty rectangle")
    step = 16 if word_only else 8
    if sx % step or dx % step or width % step:
        raise ValueError(f"horizontal coordinates must align on {step} pixels")
    if sx + width > src.width or sy + height > src.height:
        raise ValueError("source rectangle outside logical bitmap")
    if dx + width > dest.width or dy + height > dest.height:
        raise ValueError("destination rectangle outside logical bitmap")
    for s in (src, dest):
        if s.stride % 2 or s.stride < ((s.width + 15) // 16) * 2:
            raise ValueError("invalid bitmap stride")
        if len(s.planes) != s.depth or any(len(p) != s.height * s.stride for p in s.planes):
            raise ValueError("truncated plane")


def copy_cpu_bytes(src, dest, sx, sy, dx, dy, width, height):
    """True memory byte-copy pattern on uncompressed 8-pixel-aligned planar rows."""
    validate(src, dest, sx, sy, dx, dy, width, height)
    n = width // 8
    for source_plane, dest_plane in zip(src.planes, dest.planes):
        for y in range(height):
            source = (sy + y) * src.stride + sx // 8
            target = (dy + y) * dest.stride + dx // 8
            for j in range(n):
                dest_plane[target + j] = source_plane[source + j]
    return 1


def copy_cpu_words(src, dest, sx, sy, dx, dy, width, height):
    """True memory word-copy pattern for 16-pixel-aligned planar rows."""
    validate(src, dest, sx, sy, dx, dy, width, height, word_only=True)
    n = width // 16
    for source_plane, dest_plane in zip(src.planes, dest.planes):
        for y in range(height):
            source = (sy + y) * src.stride + sx // 8
            target = (dy + y) * dest.stride + dx // 8
            for j in range(n):
                k = 2*j
                dest_plane[target + k:target + k + 2] = source_plane[source + k:source + k + 2]
    return 1


def copy_blitter_word_model(src, dest, sx, sy, dx, dy, width, height):
    """Independent row-as-bits word-mask/shift model, not real Amiga DMA.

    Emulates the result of graphics.library BitMap->RastPort.
    Uses one packed integer per bitplane scanline, not the CPU path loops.
    """
    validate(src, dest, sx, sy, dx, dy, width, height)
    src_bits = src.stride * 8
    dest_bits = dest.stride * 8
    keep = (1 << width) - 1
    src_shift = src_bits - sx - width
    dest_shift = dest_bits - dx - width
    region_mask = keep << dest_shift
    for source_plane, dest_plane in zip(src.planes, dest.planes):
        for y in range(height):
            start = (sy + y)*src.stride
            src_row = int.from_bytes(source_plane[start:start+src.stride], 'big')
            insert = ((src_row >> src_shift) & keep) << dest_shift
            start_dest = (dy + y)*dest.stride
            dest_row = int.from_bytes(dest_plane[start_dest:start_dest+dest.stride], 'big')
            dest_plane[start_dest:start_dest+dest.stride] = (
                (dest_row & ~region_mask) | insert
            ).to_bytes(dest.stride, 'big')
    return 1


def copy_pixel_oracle(src, dest, sx, sy, dx, dy, width, height):
    """Slow unrelated per-pixel reference, preserves every untouched pixel."""
    validate(src, dest, sx, sy, dx, dy, width, height)
    for s_plane, d_plane in zip(src.planes, dest.planes):
        for y in range(height):
            for x in range(width):
                sidx = (sy+y)*src.stride + (sx+x)//8
                didx = (dy+y)*dest.stride + (dx+x)//8
                source_mask = 0x80 >> ((sx+x) % 8)
                dest_mask = 0x80 >> ((dx+x) % 8)
                if s_plane[sidx] & source_mask:
                    d_plane[didx] |= dest_mask
                else:
                    d_plane[didx] &= 0xff ^ dest_mask
    return 1


def scan_equivalence(src, initial, sx, sy, dx, dy, width, height):
    """Compare actual byte & word copies and DMA-like shifts to independent pixels."""
    expected = initial.clone()
    copy_pixel_oracle(src, expected, sx, sy, dx, dy, width, height)
    cpu8 = initial.clone()
    copy_cpu_bytes(src, cpu8, sx, sy, dx, dy, width, height)
    blit = initial.clone()
    copy_blitter_word_model(src, blit, sx, sy, dx, dy, width, height)
    if cpu8.signature() != expected.signature():
        raise AssertionError("CPU 8px differs from pixel oracle")
    if blit.signature() != expected.signature():
        raise AssertionError("Blitter word model differs from pixel oracle")
    if (sx | dx | width) & 15 == 0:
        cpu16 = initial.clone()
        copy_cpu_words(src, cpu16, sx, sy, dx, dy, width, height)
        if cpu16.signature() != expected.signature():
            raise AssertionError("CPU 16px differs from pixel oracle")
    return True
