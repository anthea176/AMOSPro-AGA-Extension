#!/usr/bin/env python3
"""S1-P1c strict AGSP v1 validator: raw MC68020 binary vs Python oracle.

No OS services. Payload source is caller-owned memory. A CPU Gate A test
for complete AGSP bank structure/pixels/RGB24, not WinUAE or Compiler.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_A0, UC_M68K_REG_A2, UC_M68K_REG_A3,
    UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6,
    UC_M68K_REG_A7, UC_M68K_REG_D0, UC_M68K_REG_D1,
    UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4,
    UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
)
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload

PC,STOP,SOURCE,STACK=0x20000,0x30000,0x50000,0x2c0000
PRESERVED=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,
           UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
           UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,
           UC_M68K_REG_A5,UC_M68K_REG_A6)


def cmap():
    return b''.join(bytes((i, (i*13+1)&255, (i*23+5)&255)) for i in range(256))


def capture(payload=empty_bank(), ident=1, width=16, height=16,
            ncolors=3, mode='s1', blank=False):
    cmapdata=cmap()
    colors=tuple(range(1,ncolors+1))
    if blank:
        pixels=bytes(width*height)
    else:
        pixels=bytes((0,)+colors)[0:0]  # ensure no implicit smoothing
        pixels=bytes((0 if (x+y)% (ncolors+1)==0 else
                       colors[((x+y)%(ncolors+1))-1])
                      for y in range(height) for x in range(width))
    return put_capture(payload,ident,pixels,width,height,
                       0,0,width,height,cmapdata,0,mode=mode)


class Runner:
    def __init__(self):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x400000)
        bin=Path(os.environ['AGSP_VALIDATE_BIN']).read_bytes()
        assert 100<len(bin)<14000
        self.uc.mem_write(PC,bin)

    def test(self,payload,length=None):
        u=self.uc
        length=len(payload) if length is None else length
        u.mem_write(SOURCE-16,bytes([0xa5])*16)
        u.mem_write(SOURCE,payload)
        u.mem_write(SOURCE+len(payload),bytes([0xc3])*16)
        for i,r in enumerate(PRESERVED):
            u.reg_write(r,0x44001000+i)
        saved={r:u.reg_read(r) for r in PRESERVED}
        u.reg_write(UC_M68K_REG_A0,SOURCE)
        u.reg_write(UC_M68K_REG_D0,length)
        u.reg_write(UC_M68K_REG_SR,0x2000)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(PC,STOP,count=70_000_000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items()),'ABI clobber'
        assert bytes(u.mem_read(SOURCE-16,16))==bytes([0xa5])*16
        assert bytes(u.mem_read(SOURCE+len(payload),16))==bytes([0xc3])*16
        assert bytes(u.mem_read(SOURCE,len(payload)))==payload
        return u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1)


@unittest.skipUnless(os.getenv('AGSP_VALIDATE_BIN'),'requires real VASM MC68020 binary')
class AGSPStrictValidatorCPU(unittest.TestCase):
    def setUp(self):
        self.m=Runner()

    def assert_good(self,payload):
        parsed=parse_payload(payload)
        self.assertEqual(self.m.test(payload),(1,len(parsed.images)))

    def assert_bad(self,payload):
        with self.assertRaises(ValueError):
            parse_payload(payload)
        self.assertEqual(self.m.test(payload),(0,0))

    def test_empty_bank_is_canonical(self):
        self.assert_good(empty_bank())

    def test_one_s1_16x16_three_opaque(self):
        self.assert_good(capture())

    def test_many_sorted_images_and_replacement(self):
        p=capture(ident=6)
        p=capture(payload=p,ident=1,height=2)
        p=capture(payload=p,ident=40,height=8)
        p=capture(payload=p,ident=6,height=9,ncolors=2)
        self.assert_good(p)

    def test_transparent_only_and_opaque_black(self):
        self.assert_good(capture(blank=True))
        self.assert_good(capture(ncolors=1))

    def test_s2_4planes_15_colors_and_widths(self):
        for width in (16,32,64):
            for n in (3,4,15):
                with self.subTest(width=width,n=n):
                    self.assert_good(capture(width=width,mode='s2',ncolors=n))

    def test_max_height_256(self):
        self.assert_good(capture(height=256))

    def test_header_invalid_version_flags_offsets_and_generation(self):
        original=capture()
        updates=((0,b'AGBO'),(4,b'\x00\x02'),(6,b'\x00\x01'),
                 (8,b'\x00\x02'),(10,b'\x00\x28'),(12,bytes(4)),
                 (16,bytes(4)),(20,bytes(4)),(24,bytes(4)),
                 (28,b'\x00\x00\x00\x01'))
        for off,val in updates:
            with self.subTest(offset=off):
                raw=bytearray(original)
                raw[off:off+len(val)]=val
                self.assert_bad(bytes(raw))

    def test_directory_invalid_flags_stride_depth_and_lengths(self):
        base=capture()
        mutations=((32,2,0),(34,2,20),(36,2,0),(38,2,3),
                   (40,2,0),(42,2,1),(44,4,0),(48,4,0),
                   (52,4,0),(56,4,0),(64,2,4),(66,2,256),
                   (68,4,1),(72,4,1),(76,4,1))
        for off,width,val in mutations:
            with self.subTest(offset=off):
                raw=bytearray(base)
                pack_into('>H' if width==2 else '>I',raw,off,val)
                self.assert_bad(bytes(raw))

    def test_palette_zero_unused_duplicate_and_index_corruption(self):
        base=capture()
        img=parse_payload(base).image(1)
        paloff=80+len(img.planes)
        variants=[
            (paloff,1),
            (paloff+47,1)
        ]
        for off,value in variants:
            with self.subTest(offset=off):
                raw=bytearray(base);raw[off]=value
                self.assert_bad(bytes(raw))
        dup=bytearray(base)
        dup[paloff+6:paloff+9]=dup[paloff+3:paloff+6]
        self.assert_bad(bytes(dup))
        # Local pen index > opaque colors is forbidden.
        raw=bytearray(capture(ncolors=1))
        raw[80+2*16] |=0x40  # plane1 bit6, y0; introduces local pen2
        self.assert_bad(bytes(raw))
        # First appearance must be local pen1, then pen2 (not 2 first).
        raw=bytearray(base)
        raw[80] &=~0x40      # clear plane0 bit6, x1, y0
        self.assert_bad(bytes(raw))

    def test_truncated_trailing_and_unreferenced_bytes(self):
        p=capture()
        for candidate in (p[:-2],p+bytes(2)):
            self.assert_bad(candidate)


if __name__=='__main__':
    unittest.main(verbosity=2)
