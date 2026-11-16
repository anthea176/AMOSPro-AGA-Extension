#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A for the PRIVATE M19 P0d Bob painter.

Executes the emitted native bytes under two actual Unicorn MC68020 placements.
graphics.library/Exec calls are MOCKED: this is not a WinUAE or Compiler test.
Pixel results are independently compared with a CPU oracle.
"""
from __future__ import annotations

from random import Random
from struct import pack, unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
    UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7,
)
from m19_p0d_private_blit_emit import emit_private_bob_blit

DR = (UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
      UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7)
AR = (UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
      UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7)
EXEC, GFX, STOP, STACK = 0x110000, 0x100000, 0x18000, 0xf0000
SRC, MASK, FAST, BITMAP = 0x220000, 0x260000, 0xb00000, 0x300000
PLANES = [0x400000 + 0x10000 * i for i in range(8)]
FRONT = [0x500000 + 0x10000 * i for i in range(8)]
W, H, DS = 64, 48, 8
DPS = DS * H
GUARD = bytes.fromhex('d15ea55ad15ea55a')


def planar(pixels, width, height, depth):
    stride = 2 * ((width + 15) // 16)
    one = stride * height
    raw = bytearray(one * depth)
    for y in range(height):
        for x in range(width):
            v = pixels[y * width + x]
            for p in range(depth):
                if v & (1 << p):
                    raw[p * one + y * stride + x // 8] |= 0x80 >> (x & 7)
    return bytes(raw), stride, one


def mask_bits(pixels, width, height, stride, transparent):
    raw = bytearray(stride * height)
    for y in range(height):
        for x in range(width):
            if pixels[y * width + x] != transparent:
                raw[y * stride + x // 8] |= 0x80 >> (x & 7)
    return bytes(raw)


def reference(bg, img, width, height, x, y, transparent):
    out = list(bg)
    for sy in range(height):
        for sx in range(width):
            dx, dy = x + sx, y + sy
            if 0 <= dx < W and 0 <= dy < H:
                v = img[sy * width + sx]
                if transparent is None or transparent != v:
                    out[dy * W + dx] = v
    return planar(out, W, H, max(1, max(out).bit_length()))[0]


def u16(uc, at):
    return unpack('>H', bytes(uc.mem_read(at, 2)))[0]


def u32(uc, at):
    return unpack('>I', bytes(uc.mem_read(at, 4)))[0]


def run(binary, base, img, bg, width, height, depth, x, y, transparent,
        *, fast=False, bad_depth=False, bad_stride=False, no_cpu=False):
    pixels, stride, one = planar(img, width, height, depth)
    initial, _, _ = planar(bg, W, H, depth)
    mask = None if transparent is None else mask_bits(img, width, height, stride, transparent)
    source = FAST if fast else SRC
    uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    uc.mem_map(0, 0x1000000)
    uc.mem_write(base, binary)
    uc.mem_write(STOP, bytes.fromhex('4e71'))
    uc.mem_write(4, pack('>I', EXEC))
    uc.mem_write(EXEC + 0x128, pack('>H', 0 if no_cpu else 2))
    uc.mem_write(EXEC - 534, bytes.fromhex('4e75'))
    for off in (198, 606, 636, 228):
        uc.mem_write(GFX - off, bytes.fromhex('4e75'))
    uc.mem_write(source, pixels + GUARD)
    if mask is not None:
        uc.mem_write(MASK, mask + GUARD)
    dp = depth + 1 if bad_depth and depth < 8 else depth - 1 if bad_depth else depth
    bm = pack('>HHBBH', DS, H, 0, dp, 0)
    bm += b''.join(pack('>I', v) for v in PLANES)
    uc.mem_write(BITMAP, bm + GUARD)
    for p in range(depth):
        uc.mem_write(PLANES[p], initial[p * DPS:(p + 1) * DPS] + GUARD)
        uc.mem_write(FRONT[p], bytes([0x33]) * DPS + GUARD)

    calls = []

    def ret(value=0):
        sp = uc.reg_read(AR[7])
        uc.reg_write(DR[0], value & 0xffffffff)
        uc.reg_write(UC_M68K_REG_PC, u32(uc, sp))
        uc.reg_write(AR[7], sp + 4)
        uc.reg_write(DR[1], 0xdeadbabe)
        uc.reg_write(AR[0], 0xfeedbeee)
        uc.reg_write(AR[1], 0xfeedbef0)

    def chip(p):
        if source == SRC and SRC <= p < SRC + len(pixels):
            return True
        if mask is not None and MASK <= p < MASK + len(mask):
            return True
        return any(v <= p < v + DPS for v in PLANES[:depth])

    def hook(uc, at, size, user):
        if at == EXEC - 534:
            p = uc.reg_read(AR[1])
            ret(3 if chip(p) else 1 if p == BITMAP else 4)
            return
        if at == GFX - 198:
            rp = uc.reg_read(AR[1])
            uc.mem_write(rp, bytes(128))
            calls.append('InitRastPort')
            ret()
            return
        if at in (GFX - 606, GFX - 636):
            masked = at == GFX - 636
            src = uc.reg_read(AR[0])
            rp = uc.reg_read(AR[1])
            assert u32(uc, rp + 4) == BITMAP
            assert u16(uc, src) == stride and u16(uc, src + 2) == height
            assert bytes(uc.mem_read(src + 5, 1)) == bytes([depth])
            assert [u32(uc, src + 8 + 4 * p) for p in range(depth)] == [
                source + p * one for p in range(depth)]
            sx, sy, dx, dy, cw, ch, minterm = (uc.reg_read(v) for v in DR[:7])
            assert 0 <= sx < width and 0 <= sy < height
            assert 0 <= dx < W and 0 <= dy < H
            assert 0 < cw <= width - sx and 0 < ch <= height - sy
            assert dx + cw <= W and dy + ch <= H
            assert minterm == (0xe0 if masked else 0xc0)
            if masked:
                assert mask is not None and uc.reg_read(AR[2]) == MASK
            else:
                assert mask is None
            calls.append('BltMask' if masked else 'BltOpaque')
            for row in range(ch):
                for col in range(cw):
                    px, py, tx, ty = sx + col, sy + row, dx + col, dy + row
                    if masked and not (bytes(uc.mem_read(
                            MASK + py * stride + px // 8, 1))[0] & (0x80 >> (px & 7))):
                        continue
                    for p in range(depth):
                        v = bytes(uc.mem_read(source + p * one + py * stride + px // 8, 1))[0]
                        at_dest = PLANES[p] + ty * DS + tx // 8
                        old = bytes(uc.mem_read(at_dest, 1))[0]
                        bit = 0x80 >> (tx & 7)
                        new = (old | bit) if (v & (0x80 >> (px & 7))) else (old & (255 ^ bit))
                        uc.mem_write(at_dest, bytes([new]))
            ret()
            return
        if at == GFX - 228:
            assert calls and calls[-1] in ('BltMask', 'BltOpaque')
            calls.append('WaitBlit')
            ret()
            return
        raise AssertionError(('unexpected OS call', hex(at)))

    uc.hook_add(UC_HOOK_CODE, hook, begin=GFX - 1024, end=EXEC)
    before = {
        AR[0]: source, AR[1]: MASK if mask is not None else 0,
        AR[2]: BITMAP, AR[3]: 0x90304, AR[4]: 0x90306,
        AR[5]: 0x90308, AR[6]: GFX,
        DR[0]: x & 0xffffffff, DR[1]: y & 0xffffffff, DR[2]: 0x7788,
        DR[3]: stride + 2 if bad_stride else stride,
        DR[4]: width, DR[5]: height, DR[6]: depth, DR[7]: one,
    }
    for r, value in before.items():
        uc.reg_write(r, value)
    uc.reg_write(UC_M68K_REG_SR, 0x2000)
    uc.reg_write(AR[7], STACK)
    uc.mem_write(STACK, pack('>I', STOP))
    try:
        uc.emu_start(base, STOP, count=200000)
    except Exception as error:
        raise AssertionError(('P0d CPU020 fault', str(error),
                              hex(uc.reg_read(UC_M68K_REG_PC)),
                              width, height, depth, x, y, transparent, calls)) from error
    assert uc.reg_read(UC_M68K_REG_PC) == STOP
    assert uc.reg_read(AR[7]) == STACK + 4
    assert uc.reg_read(DR[2]) == 0
    for r, value in before.items():
        if r not in (DR[2], DR[3]):
            assert uc.reg_read(r) == value, ('register clobbered', r)
    assert bytes(uc.mem_read(source, len(pixels) + len(GUARD))) == pixels + GUARD
    if mask is not None:
        assert bytes(uc.mem_read(MASK, len(mask) + len(GUARD))) == mask + GUARD
    assert bytes(uc.mem_read(BITMAP + 40, len(GUARD))) == GUARD
    for p in range(depth):
        assert bytes(uc.mem_read(PLANES[p] + DPS, len(GUARD))) == GUARD
        assert bytes(uc.mem_read(FRONT[p], DPS)) == bytes([0x33]) * DPS
    after = b''.join(bytes(uc.mem_read(PLANES[p], DPS)) for p in range(depth))
    return uc.reg_read(DR[3]), after, calls


def main():
    raw, labels = emit_private_bob_blit()
    assert raw == emit_private_bob_blit()[0] and labels['private_bob_blit_entry'] == 0
    dis = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020).disasm(raw, 0x10000))
    assert sum(i.size for i in dis) == len(raw), 'MC68020 decode incomplete'
    rand = Random(0xA6A2026)
    cases = 0
    for base in (0x10000, 0x21000):
        for width in (1, 17, 31, 32, 37):
            height = 1 if width == 1 else 11
            for depth in (1, 4, 8):
                maximum = (1 << depth) - 1
                img = [rand.randrange(maximum + 1) for _ in range(width * height)]
                bg = [rand.randrange(maximum + 1) for _ in range(W * H)]
                if len(img) > 1:
                    img[0], img[1] = 0, maximum
                for x, y in ((0, 0), (1, 1), (-1, 4), (-16, 6),
                             (60, 1), (64, 1), (3, -4), (3, 44)):
                    for transparent in (None, 0, maximum):
                        expected = list(bg)
                        for sy in range(height):
                            for sx in range(width):
                                tx, ty = sx + x, sy + y
                                v = img[sy * width + sx]
                                if (0 <= tx < W and 0 <= ty < H and
                                        (transparent is None or v != transparent)):
                                    expected[ty * W + tx] = v
                        wanted = planar(expected, W, H, depth)[0]
                        status, got, calls = run(raw, base, img, bg, width, height,
                                                 depth, x, y, transparent)
                        assert status == 1 and got == wanted, (
                            width, height, depth, x, y, transparent, status, calls)
                        visible = -width < x < W and -height < y < H
                        assert calls.count('WaitBlit') == int(visible), calls
                        assert calls.count('InitRastPort') == int(visible), calls
                        cases += 1
    depth, width, height = 8, 37, 11
    img = [(i * 3) & 255 for i in range(width * height)]
    bg = [(i * 7) & 255 for i in range(W * H)]
    old = planar(bg, W, H, depth)[0]
    rejects = ({'fast': True}, {'bad_depth': True}, {'bad_stride': True},
               {'no_cpu': True})
    for args in rejects:
        status, got, calls = run(raw, 0x10000, img, bg, width, height,
                                 depth, 1, 2, None, **args)
        assert status == 0 and got == old
        assert 'BltOpaque' not in calls and 'BltMask' not in calls
    print('M19 P0d PRIVATE MC68020 GATE A PASS', len(raw),
          'bytes', cases, 'pixel-exact cases', len(rejects),
          'rejects; Exec/graphics mocked; NOT WinUAE or AMOS Compiler')


if __name__ == '__main__':
    main()
