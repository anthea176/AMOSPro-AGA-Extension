#!/usr/bin/env python3
"""S1-P1 separate MC68020 native RGB24/planar capture kernel vs AGSP v1.

Only runs when AGSP_NATIVE_BIN points to an assembled raw MC68020 binary.
This is Gate A CPU emulation, NOT an AP20 token, real WinUAE, or Compiler.
"""
from __future__ import annotations

import os
import random
from pathlib import Path
from struct import pack
import unittest

from m19_s1_agsp_bank import empty_bank, parse_payload, put_capture

try:
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
    from unicorn.m68k_const import (
        UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
        UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2,
        UC_M68K_REG_A3, UC_M68K_REG_A4, UC_M68K_REG_A5,
        UC_M68K_REG_A6, UC_M68K_REG_A7, UC_M68K_REG_D0,
        UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
        UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6,
        UC_M68K_REG_D7,
    )
except ImportError:
    Uc = None

PC = 0x20000
DESC = 0x10000
SOURCE = 0x40000
CMAP = 0x110000
OUTPUT = 0x120000
PALOUT = 0x124000
STACK = 0x2c0000
STOP = 0x30000
SEED_REGS = [UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4,
             UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
             UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4,
             UC_M68K_REG_A5, UC_M68K_REG_A6] if Uc else []


def planar(pixels: bytes, w: int, h: int, depth: int, stride: int) -> list[bytes]:
    planes = [bytearray(stride * h) for _ in range(depth)]
    for y in range(h):
        for x in range(w):
            v = pixels[y * w + x]
            assert v < 1 << depth
            for p in range(depth):
                if v & (1 << p):
                    planes[p][y * stride + x // 8] |= 1 << (7 - (x % 8))
    return [bytes(p) for p in planes]


class Runner:
    def __init__(self):
        if Uc is None:
            raise RuntimeError('Unicorn dependency missing')
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0, 0x300000)
        binary = Path(os.environ['AGSP_NATIVE_BIN']).read_bytes()
        assert 100 < len(binary) < 20000
        self.uc.mem_write(PC, binary)

    def invoke(self, pixels: bytes, w: int, h: int, depth: int, cmap: bytes,
               *, x: int = 0, y: int = 0, capheight: int = 16,
               transparent: int = 0, stride: int | None = None,
               corrupt: dict[int, int] | None = None):
        assert len(pixels) == w*h and len(cmap) == 768
        stride = (w+15)//16*2 if stride is None else stride
        uc = self.uc
        p = planar(pixels, w, h, depth, stride)
        address = []
        for i, plane in enumerate(p):
            addr = SOURCE + i*0x10000
            uc.mem_write(addr, plane)
            address.append(addr)
        address += [0]*(8-len(address))
        desc = bytearray(pack('>8I3II8H', *address, CMAP, OUTPUT, PALOUT,
                              stride, w, h, depth, x, y, capheight, transparent, 0))
        assert len(desc) == 64
        for k,v in (corrupt or {}).items():
            if k in (0,4,8,12,16,20,24,28,32,36,40,44):
                desc[k:k+4] = pack('>I',v)
            else:
                desc[k:k+2] = pack('>H',v)
        uc.mem_write(DESC, bytes(desc))
        uc.mem_write(CMAP, cmap)
        size=4*max(capheight,1)
        uc.mem_write(OUTPUT - 16, bytes([0xa5])*16)
        uc.mem_write(OUTPUT, bytes([0x5a])*max(size,1024))
        uc.mem_write(OUTPUT + 1024, bytes([0xc3])*16)
        uc.mem_write(PALOUT - 16, bytes([0xa5])*16)
        uc.mem_write(PALOUT, bytes([0x5a])*48)
        uc.mem_write(PALOUT + 48, bytes([0xc3])*16)
        for i, reg in enumerate(SEED_REGS):
            uc.reg_write(reg, 0x55001000 + i)
        expect = {reg:uc.reg_read(reg) for reg in SEED_REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A0,DESC)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK, pack('>I',STOP))
        uc.emu_start(PC,STOP,count=30_000_000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in expect.items())
        assert bytes(uc.mem_read(OUTPUT-16,16))==bytes([0xa5])*16
        assert bytes(uc.mem_read(OUTPUT+1024,16))==bytes([0xc3])*16
        assert bytes(uc.mem_read(PALOUT-16,16))==bytes([0xa5])*16
        assert bytes(uc.mem_read(PALOUT+48,16))==bytes([0xc3])*16
        return (uc.reg_read(UC_M68K_REG_D0), uc.reg_read(UC_M68K_REG_D1),
                bytes(uc.mem_read(OUTPUT,size)),bytes(uc.mem_read(PALOUT,48)))


@unittest.skipUnless(Uc is not None and os.environ.get('AGSP_NATIVE_BIN'),
                     'requires assembled native kernel and Unicorn')
class NativeS1CaptureCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=Runner()

    def check_model(self, screen: bytes, w: int, h: int, depth: int,
                    cmap: bytes, x=0, y=0, capheight=16, transparent=0):
        res=self.m.invoke(screen,w,h,depth,cmap,x=x,y=y,
                          capheight=capheight,transparent=transparent)
        payload=put_capture(empty_bank(),1,screen,w,h,x,y,16,
                            capheight,cmap,transparent,mode='s1')
        img=parse_payload(payload).image(1)
        self.assertEqual(res[0:2],(1,img.opaque_count))
        self.assertEqual(res[2],img.planes)
        self.assertEqual(res[3],img.palette)

    @staticmethod
    def cmap():
        r=random.Random(0xA65)
        return b''.join(bytes((r.randrange(256),r.randrange(256),r.randrange(256)))
                        for _ in range(256))

    def test_16x16_exact_index_remap_rgb24(self):
        w,h=32,16
        screen=bytes([0,25,67,128][(x+y)%4] for y in range(h) for x in range(w))
        self.check_model(screen,w,h,8,self.cmap())

    def test_unaligned_aga_capture_x13_y5(self):
        w,h=64,32
        screen=bytes([0,25,67,128][(x+3*y)%4] for y in range(h) for x in range(w))
        self.check_model(screen,w,h,8,self.cmap(),x=13,y=5)

    def test_shallow_4planes_and_nonzero_transparency(self):
        w,h=32,16
        screen=bytes([1,2,3,4][(x+y)%4] for y in range(h) for x in range(w))
        self.check_model(screen,w,h,4,self.cmap(),transparent=1)

    def test_identical_rgb_colors_fold_to_same_index(self):
        w,h=16,16
        screen=bytes([0,25,67,128,180][x%5] for y in range(h) for x in range(w))
        cmap=bytearray(self.cmap())
        cmap[180*3:180*3+3]=cmap[67*3:67*3+3]
        self.check_model(screen,w,h,8,bytes(cmap))

    def test_opaque_black_not_transparent(self):
        w,h=16,16
        screen=bytes([0,25,67,128][x%4] for y in range(h) for x in range(w))
        cmap=bytearray(self.cmap())
        cmap[25*3:25*3+3]=bytes(3)
        self.check_model(screen,w,h,8,bytes(cmap))

    def test_four_opaque_colors_fail_without_writing_output(self):
        w,h=16,16
        screen=bytes([0,1,2,3,4][x%5] for y in range(h) for x in range(w))
        status,count,output,palette=self.m.invoke(screen,w,h,8,self.cmap())
        self.assertEqual((status,count),(0,0))
        self.assertEqual(output,bytes([0x5a])*(4*16))
        self.assertEqual(palette,bytes([0x5a])*48)

    def test_full_height_256_with_only_three_colors(self):
        w,h=16,256
        screen=bytes([0,25,67,128][(x+y)%4] for y in range(h) for x in range(w))
        self.check_model(screen,w,h,8,self.cmap(),capheight=256)

    def test_bad_descriptor_no_write(self):
        w,h=32,16
        screen=bytes([0,25,67,128][x%4] for y in range(h) for x in range(w))
        for bad in ({54:20},{52:9},{44:1},{62:1},{36:0},{0:0},{58:0}):
            with self.subTest(bad=bad):
                status,count,output,palette=self.m.invoke(
                    screen,w,h,8,self.cmap(),corrupt=bad)
                self.assertEqual((status,count),(0,0))
                self.assertEqual(output,bytes([0x5a])*(4*16))
                self.assertEqual(palette,bytes([0x5a])*48)

if __name__=='__main__':
    unittest.main(verbosity=2)
