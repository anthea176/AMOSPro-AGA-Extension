#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Native MC68020 hotspot-origin Gate A and independent two-page host oracle.

Exercises real emitted M68K machine code under Unicorn for two placements,
signed extrema, clipping, masks and unchanged logical X/Y. No actual P1b
AP20 token, no hooked draw path and no WinUAE/Compiler assertion.
"""
from __future__ import annotations

from random import Random
from struct import pack, unpack_from
from hashlib import sha256
from pathlib import Path
import unittest

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
    UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7,
)
from m19_p0a_multi_bob_abk import empty_bank, put_image, set_hotspot, parse_payload
from m19_p1b_hotspot_origin_emit import emit_hotspot_origin
from m19_p1b_hotspot_draw_model import clipped_origin, HotspotFrameModel
from m19_bob_clear_update_model import READY, CLEAN, DIRTY, BobFrameModel, BobImage

REG_D=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
       UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
REG_A=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
       UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
STACK=0x70fffc
STOP=0x18000
SRC=0x40100
DIMS=0x60100
ROOT=Path(__file__).resolve().parents[1]


def native_case(raw,base,image_payload,x,y,sw,sh,*,image_id=1):
    src=parse_payload(image_payload)
    pos=next(i for i,img in enumerate(src.images) if img.image_id==image_id)
    entry=SRC+32+40*pos
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    uc.mem_map(0,0x800000)
    uc.mem_write(base,raw)
    uc.mem_write(STOP,bytes.fromhex('4e71'))
    uc.mem_write(SRC,image_payload)
    uc.mem_write(DIMS,pack('>II',sw,sh))
    uc.mem_write(STACK,pack('>I',STOP))
    for i,reg in enumerate(REG_D):
        uc.reg_write(reg,(0x13570000+i)&0xffffffff)
    for i,reg in enumerate(REG_A[:7]):
        uc.reg_write(reg,0x70000+i*0x100)
    uc.reg_write(UC_M68K_REG_D0,0x12785634)
    uc.reg_write(UC_M68K_REG_D1,x&0xffffffff)
    uc.reg_write(UC_M68K_REG_D4,y&0xffffffff)
    uc.reg_write(UC_M68K_REG_A0,entry)
    uc.reg_write(UC_M68K_REG_A3,DIMS)
    uc.reg_write(UC_M68K_REG_A7,STACK)
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    before={reg:uc.reg_read(reg) for reg in REG_D+REG_A[:7]}
    try:
        uc.emu_start(base,STOP,count=4000)
    except Exception as exc:
        raise AssertionError(('P1b MC68020 origin fault',hex(base),x,y,
                  hex(uc.reg_read(UC_M68K_REG_PC)))) from exc
    assert uc.reg_read(UC_M68K_REG_PC)==STOP
    assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
    assert uc.reg_read(UC_M68K_REG_D2)==0
    for reg in (UC_M68K_REG_D0,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)+REG_A[:7]:
        assert uc.reg_read(reg)==before[reg],('ABI clobbered',reg)
    assert bytes(uc.mem_read(SRC,len(image_payload)))==image_payload
    assert bytes(uc.mem_read(DIMS,8))==pack('>II',sw,sh)
    result=uc.reg_read(UC_M68K_REG_D3)
    assert result in (0,1)
    rx=uc.reg_read(UC_M68K_REG_D1)
    ry=uc.reg_read(UC_M68K_REG_D4)
    rx=rx-0x100000000 if rx&0x80000000 else rx
    ry=ry-0x100000000 if ry&0x80000000 else ry
    image=src.image(image_id)
    expected=clipped_origin(x,y,image.hotspot_x,image.hotspot_y,
                            image.width,image.height,sw,sh)
    if expected is None:
        assert (result,rx,ry)==(0,x,y), (result,rx,ry,x,y,expected)
    else:
        assert (result,rx,ry)==(1,*expected), (result,rx,ry,expected)
    return 1


class HotspotNativeAndFrames(unittest.TestCase):
    def test_mc68020_source_and_positioning(self):
        raw,labels=emit_hotspot_origin()
        self.assertEqual(labels['p1b_hotspot_origin_entry'],0)
        self.assertEqual(raw,emit_hotspot_origin()[0])
        ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
                 disasm(raw,0x10000))
        self.assertEqual(sum(i.size for i in ins),len(raw))
        self.assertFalse(any(i.mnemonic.startswith('dc.') for i in ins))
        rng=Random(1901)
        cases=[(0,0,0,0,1,1,16,16),(8,5,3,2,17,5,16,16),
               (0,0,-3,-4,5,4,16,16),(0,0,3,4,5,4,16,16),
               (-32768,32767,32767,-32768,2,2,16,16),
               (32767,-32768,-32768,32767,2,2,16,16),
               (-1,-1,0,0,2,2,16,16),(15,15,0,0,2,2,16,16),
               (16,16,0,0,2,2,16,16)]
        for _ in range(120):
            cases.append((rng.randint(-32768,32767),rng.randint(-32768,32767),
                          rng.randint(-32768,32767),rng.randint(-32768,32767),
                          rng.randint(1,31),rng.randint(1,12),
                          rng.randint(1,100),rng.randint(1,70)))
        checks=0
        for x,y,hx,hy,w,h,sw,sh in cases:
            payload=put_image(empty_bank(),1,w,h,4,bytes([1])*(w*h))
            payload=set_hotspot(payload,1,hx,hy)
            for base in (0x10000,0x22000):
                checks+=native_case(raw,base,payload,x,y,sw,sh)
        self.assertEqual(checks,258)

    def test_model_mask_and_logical_anchor(self):
        m=HotspotFrameModel(9,7,4)
        payload=put_image(empty_bank(),1,3,2,4,
                          bytes([1,2,3,4,5,6]),
                          visibility=bytes([1,0,1,1,1,1]))
        payload=set_hotspot(payload,1,2,1)
        self.assertTrue(m.install_agbo_bank(24,payload))
        self.assertTrue(m.edit_background(3,2,12))
        self.assertTrue(m.put(1,24,1,4,3))
        self.assertEqual((m.objects[1].x,m.objects[1].y),(4,3))
        self.assertTrue(m.update())
        self.assertEqual(m.status,READY)
        self.assertEqual(m.pages[m.back][2][2],1)
        self.assertEqual(m.pages[m.back][2][3],12)  # masked pixel keeps decor
        self.assertEqual(m.pages[m.back][2][4],3)
        self.assertEqual(m.pages[m.back][3][2:5],[4,5,6])
        self.assertTrue(m.swap())
        self.assertTrue(m.update())
        self.assertTrue(m.swap())
        self.assertTrue(m.off(1))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][2][2],0)
        self.assertTrue(m.swap())
        self.assertTrue(m.put(1,24,1,7,5))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][4][5],1)
        self.assertTrue(m.swap())
        self.assertEqual((m.objects[1].x,m.objects[1].y),(7,5))

    def test_zero_hotspot_matches_p0_model(self):
        p0=BobFrameModel(8,6,4)
        p1=HotspotFrameModel(8,6,4)
        img=BobImage(((1,2,3),(4,5,6)),4)
        for m in (p0,p1):
            self.assertTrue(m.install_bank(10,{1:img}))
            self.assertTrue(m.put(1,10,1,-1,2))
            for n in range(5):
                self.assertTrue(m.update())
                self.assertTrue(m.swap())
        self.assertEqual(p0.pages,p1.pages)
        self.assertEqual((p0.front,p0.swaps,p0.status),
                         (p1.front,p1.swaps,p1.status))

    def test_generation_and_mask_preservation(self):
        p0=put_image(empty_bank(),1,17,3,4,bytes([2])*51,
                     visibility=bytes([1]*51))
        p1=set_hotspot(p0,1,-3,2)
        self.assertEqual(parse_payload(p1).generation,
                         parse_payload(p0).generation+1)
        self.assertEqual(parse_payload(p1).image(1).planes,
                         parse_payload(p0).image(1).planes)
        self.assertEqual(parse_payload(p1).image(1).mask,
                         parse_payload(p0).image(1).mask)
        m=HotspotFrameModel(32,20,4)
        self.assertTrue(m.install_agbo_bank(24,p0))
        self.assertTrue(m.put(1,24,1,3,3))
        self.assertTrue(m.install_agbo_bank(24,p1))
        self.assertFalse(m.update())
        self.assertEqual(m.status,DIRTY)
        self.assertEqual((m.objects[1].x,m.objects[1].y),(3,3))

    def test_offscreen_and_partial_clip(self):
        m=HotspotFrameModel(8,6,4)
        payload=put_image(empty_bank(),1,17,2,4,bytes([9])*34)
        payload=set_hotspot(payload,1,5,1)
        self.assertTrue(m.install_agbo_bank(24,payload))
        self.assertTrue(m.put(1,24,1,0,1))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back][0][0],9)  # clipped left, y=0
        self.assertEqual(m.pages[m.back][0][7],9)
        self.assertTrue(m.swap())
        self.assertTrue(m.put(1,24,1,-32768,32767))
        self.assertTrue(m.update())
        self.assertEqual(m.pages[m.back],[[0]*8 for _ in range(6)])


if __name__=='__main__':
    unittest.main(verbosity=2)
