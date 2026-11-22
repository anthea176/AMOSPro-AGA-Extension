#!/usr/bin/env python3
"""S1-P1b: execute actual Motorola MC68020 screen/ColorMap bridge code.

Gate A with simulated P2d AGA Screen/ScreenBuffer and graphics.library.
Not WinUAE, AP20, AMOS Save/Load, IFF loader or a Sprite-DMA test.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack, pack_into, unpack_from
import unittest

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2,
    UC_M68K_REG_A3, UC_M68K_REG_A4, UC_M68K_REG_A5,
    UC_M68K_REG_A6, UC_M68K_REG_A7, UC_M68K_REG_D0,
    UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6,
    UC_M68K_REG_D7,
)

from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload
from test_m19_s1p1_native_capture import planar

SOURCE = 0x40000
STATE, SCREEN, COLORMAP, DB = 0x140000, 0x141000, 0x142000, 0x143000
SB0, SB1, BITMAP0, BITMAP1 = 0x144000, 0x145000, 0x146000, 0x147000
REQUEST = 0x150000
RGB32, RGB24, DESC, PLANE_OUT, PAL_OUT = (
    0x1a0000, 0x1a1000, 0x1a2000, 0x1a3000, 0x1a4000)
GFX, CODE, KERNEL, STACK, STOP = 0x280000, 0x20000, 0x22000, 0x2c0000, 0x30000
STRIDE, WIDTH, HEIGHT, DEPTH = 40, 320, 256, 8
REGS = (UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4,
        UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
        UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4,
        UC_M68K_REG_A5, UC_M68K_REG_A6)


def make_screen(x=13, y=5, h=16, extra=False):
    pixels = bytearray(WIDTH * HEIGHT)
    choices = [0, 25, 67, 128, 180] if extra else [0, 25, 67, 128]
    for row in range(h):
        for col in range(16):
            pixels[(y+row)*WIDTH + x+col] = choices[(col+row) % len(choices)]
    return bytes(pixels)


def make_cmap():
    return b''.join(bytes((i, (i*11+3)&255, (i*17+7)&255)) for i in range(256))


class BridgeMachine:
    def __init__(self, screen=None, x=13, y=5, height=16, front=0, safe=1):
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0, 0x300000)
        self.pixels = make_screen(x, y, height) if screen is None else screen
        self.cmap = make_cmap()
        self.x, self.y, self.height = x, y, height
        self.front, self.safe = front, safe
        self.calls = []
        uc = self.uc
        uc.mem_write(CODE, Path(os.environ['AGSP_BRIDGE_BIN']).read_bytes())
        uc.mem_write(KERNEL, Path(os.environ['AGSP_NATIVE_BIN']).read_bytes())
        uc.mem_write(GFX-900, b'\x4e\x75')
        uc.mem_write(GFX-228, b'\x4e\x75')
        uc.hook_add(UC_HOOK_CODE, self.hook, begin=GFX-900, end=GFX-900)
        uc.hook_add(UC_HOOK_CODE, self.hook, begin=GFX-228, end=GFX-228)
        self.put(STATE, pack('>I', SCREEN))
        self.put(STATE+8, pack('>I', GFX))
        self.put(STATE+12, pack('>II', WIDTH, HEIGHT))
        self.put(STATE+20, pack('>I', 256))
        self.put(STATE+28, pack('>II', 8, DB))
        self.put(SCREEN+48, pack('>I', COLORMAP))
        self.put(COLORMAP+2, pack('>H',256))
        self.put(DB, pack('>III', SB0, SB1, front))
        self.put(DB+20,pack('>I',safe))
        self.put(SB0, pack('>I', BITMAP0))
        self.put(SB1, pack('>I', BITMAP1))
        for j,bm in enumerate((BITMAP0,BITMAP1)):
            raw=bytearray(40)
            pack_into('>HH',raw,0,STRIDE,HEIGHT)
            raw[5]=DEPTH
            for i in range(8):
                pack_into('>I',raw,8+4*i,SOURCE + (j*8+i)*0x10000)
            self.put(bm,raw)
        # Fill both buffers, including an independent inactive buffer.
        for j in range(2):
            for i,plane in enumerate(planar(self.pixels,WIDTH,HEIGHT,DEPTH,STRIDE)):
                self.put(SOURCE+(j*8+i)*0x10000,plane)
        self.put(RGB32,bytes([0x66])*3072)
        self.put(RGB24,bytes([0x5a])*768)
        self.put(DESC,bytes([0x5a])*64)
        self.put(PLANE_OUT,bytes([0x5a])*1024)
        self.put(PAL_OUT,bytes([0x5a])*48)
        self.put(REQUEST,pack('>6I4HI',STATE,RGB32,RGB24,DESC,PLANE_OUT,PAL_OUT,
                              x,y,height,0,0))

    def put(self,addr,raw):
        self.uc.mem_write(addr, bytes(raw))

    def read(self,addr,length):
        return bytes(self.uc.mem_read(addr,length))

    def hook(self,uc,address,size,user):
        if address == GFX-228:
            self.calls.append('WaitBlit')
        elif address == GFX-900:
            self.calls.append('GetRGB32')
            self.first=uc.reg_read(UC_M68K_REG_D0)
            self.count=uc.reg_read(UC_M68K_REG_D1)
            self.cm_addr=uc.reg_read(UC_M68K_REG_A0)
            self.rgb_dest=uc.reg_read(UC_M68K_REG_A1)
            assert self.cm_addr == COLORMAP and self.first == 0 and self.count == 256
            assert self.rgb_dest == RGB32
            data=b''.join(pack('>III',*(b*0x01010101 for b in self.cmap[pen*3:pen*3+3]))
                          for pen in range(256))
            self.put(RGB32,data)

    def run(self, at=CODE, arg=REQUEST):
        uc=self.uc
        for i,r in enumerate(REGS):
            uc.reg_write(r,0x55000000+i)
        expected={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A0,arg)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        self.put(STACK,pack('>I',STOP))
        uc.emu_start(at,STOP,count=5000000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in expected.items()),'ABI clobber'
        return uc.reg_read(UC_M68K_REG_D0),uc.reg_read(UC_M68K_REG_D1)


@unittest.skipUnless(os.environ.get('AGSP_BRIDGE_BIN') and os.environ.get('AGSP_NATIVE_BIN'),
                     'Requires real vasm MC68020 binaries')
class ScreenRGB24BridgeGateA(unittest.TestCase):
    def test_complete_screen_to_native_capture_to_agsp_model(self):
        m=BridgeMachine()
        self.assertEqual(m.run(),(1,256))
        self.assertEqual(m.calls,['WaitBlit','GetRGB32'])
        self.assertEqual(m.read(RGB24,768),m.cmap)
        pointers=[unpack_from('>I',m.read(DESC,64),4*i)[0] for i in range(8)]
        self.assertEqual(pointers,[SOURCE+(8+i)*0x10000 for i in range(8)])
        self.assertEqual(unpack_from('>IIII',m.read(DESC,64),32),
                         (RGB24,PLANE_OUT,PAL_OUT,STRIDE))
        self.assertEqual(unpack_from('>8H',m.read(DESC,64),48),
                         (WIDTH,HEIGHT,8,13,5,16,0,0))
        self.assertEqual(m.read(PLANE_OUT,64),bytes([0x5a])*64)
        self.assertEqual(m.run(KERNEL,DESC)[0],1)
        expected=parse_payload(put_capture(empty_bank(),1,m.pixels,WIDTH,HEIGHT,13,5,
                                           16,16,m.cmap,0,mode='s1')).image(1)
        self.assertEqual(m.read(PLANE_OUT,len(expected.planes)),expected.planes)
        self.assertEqual(m.read(PAL_OUT,48),expected.palette)

    def test_front_one_selects_back_zero(self):
        m=BridgeMachine(front=1)
        self.assertEqual(m.run(),(1,256))
        pointers=[unpack_from('>I',m.read(DESC,64),4*i)[0] for i in range(8)]
        self.assertEqual(pointers,[SOURCE+i*0x10000 for i in range(8)])

    def test_unsafe_refuses_without_consuming_safeport_or_writing(self):
        m=BridgeMachine(safe=0)
        self.assertEqual(m.run(),(0,0))
        self.assertEqual(m.calls,[])
        self.assertEqual(m.read(DESC,64),bytes([0x5a])*64)
        self.assertEqual(m.read(RGB24,768),bytes([0x5a])*768)

    def test_four_opaque_colors_refused_by_kernel(self):
        pixels=make_screen(extra=True)
        m=BridgeMachine(screen=pixels)
        self.assertEqual(m.run(),(1,256))
        self.assertEqual(m.run(KERNEL,DESC),(0,0))
        # The bridge does not publish or change an AMOS bank.
        self.assertEqual(m.read(PLANE_OUT,64),bytes([0x5a])*64)
        self.assertEqual(m.read(PAL_OUT,48),bytes([0x5a])*48)

    def test_invalid_screen_geometry_and_structure_fail_read_only(self):
        for address,raw in ((STATE+28,pack('>I',4)),(STATE+20,pack('>I',128)),
                            (DB+8,pack('>I',2)),(COLORMAP+2,pack('>H',4)),
                            (BITMAP1+5,b'\x04'),(BITMAP1,pack('>H',2)),
                            (REQUEST+28,pack('>H',0)),(REQUEST+24,pack('>H',320)),
                            (REQUEST+30,pack('>H',256)),(REQUEST+32,pack('>I',1)),
                            (REQUEST+8,pack('>I',0)),(SB1,pack('>I',0))):
            with self.subTest(address=hex(address)):
                m=BridgeMachine()
                m.put(address,raw)
                self.assertEqual(m.run(),(0,0))
                self.assertEqual(m.calls,[])
                self.assertEqual(m.read(DESC,64),bytes([0x5a])*64)

    def test_transparency_and_rgb_high_byte_precision(self):
        m=BridgeMachine()
        self.assertEqual(m.run(),(1,256))
        self.assertEqual(m.read(RGB24,768),m.cmap)
        self.assertEqual(m.read(RGB32,12),
                         pack('>III',0x00000000,0x03030303,0x07070707))


if __name__=='__main__':
    unittest.main(verbosity=2)
