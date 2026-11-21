#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Execute REAL emitted private MC68020 collision bytes under Unicorn.

Prevalidated descriptor inputs from AGBO v1; compare collision results to the
independent P2a Python model across signed hotspots, masks, clipping and
2 code placements. Does not exercise AMOS bank-list/owner checks, AP20, VBL,
actual WinUAE, real Compiler or physical Amiga.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from struct import Struct, pack
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
from m19_p2a_agbo_bridge import host_image
from m19_p2a_bob_collision_model import Bob, Rect, collision, visible_footprint
from m19_p2a_collision020_emit import DESCRIPTOR_BYTES, emit_collision020

REG_D=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
       UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
REG_A=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
       UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
DESC=Struct('>iiiiiiIIII')
assert DESC.size==DESCRIPTOR_BYTES==40
ADDR_A,ADDR_B=0x40100,0x40200
MASK_A,MASK_B=0x50000,0x60000
STOP=0x18000
STACK=0x70fffc
SCREEN=Rect(0,0,320,256)
CANARY=b'\x5a'*8


def u32(n): return n&0xffffffff


def image(w,h,visibility=None,hot=(0,0)):
    pixels=bytes(w*h)
    payload=put_image(empty_bank(),1,w,h,1,pixels,
                      visibility=bytes(visibility) if visibility is not None else None)
    if hot != (0,0):
        payload=set_hotspot(payload,1,*hot)
    return parse_payload(payload).image(1)


def fixture(img, ident, x, y, bank=24):
    return Bob(ident,bank,img.image_id,x,y,host_image(img),img.hotspot_x,img.hotspot_y)


def descriptor(bob, source, mask_address, screen, global_limit, local_limits):
    clipped=visible_footprint(bob, screen, global_limit, local_limits)
    rect=(0,0,0,0) if clipped is None else (
        clipped.x,clipped.y,clipped.right,clipped.bottom)
    return DESC.pack(*rect,bob.origin_x,bob.origin_y,source.width,source.height,
                     source.stride,mask_address if source.mask is not None else 0)


class NativePair:
    def __init__(self, base, code):
        self.base=base
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x800000)
        self.uc.mem_write(base,code)
        self.uc.mem_write(STOP,bytes.fromhex('4e71'))

    def run(self, desc_a,desc_b,mask_a,mask_b,mode,*,expect=None,ptr_a=ADDR_A):
        uc=self.uc
        # Guards detect illegal writes to descriptors, bitplanes and frame.
        for where,raw in ((ADDR_A,desc_a),(ADDR_B,desc_b),
                          (MASK_A,mask_a or b'\x00\x00'),
                          (MASK_B,mask_b or b'\x00\x00')):
            uc.mem_write(where-8,CANARY)
            uc.mem_write(where,raw)
            uc.mem_write(where+len(raw),CANARY)
        uc.mem_write(STACK,pack('>I',STOP))
        for i,reg in enumerate(REG_D):
            uc.reg_write(reg,0x12340000+i)
        for i,reg in enumerate(REG_A[:7]):
            uc.reg_write(reg,0x710000+i*0x100)
        uc.reg_write(UC_M68K_REG_D0,u32(mode))
        uc.reg_write(UC_M68K_REG_A0,ptr_a)
        uc.reg_write(UC_M68K_REG_A1,ADDR_B)
        uc.reg_write(UC_M68K_REG_SR,0x2000)  # supervisor stack model
        uc.reg_write(UC_M68K_REG_A7,STACK)
        before={r:uc.reg_read(r) for r in REG_D+REG_A[:7]
                if r not in (UC_M68K_REG_D2, UC_M68K_REG_D3)}
        uc.emu_start(self.base,STOP,count=650000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP,hex(uc.reg_read(UC_M68K_REG_PC))
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4,('SP',hex(uc.reg_read(UC_M68K_REG_A7)))
        assert uc.reg_read(UC_M68K_REG_D2)==0
        for r,value in before.items():
            assert uc.reg_read(r)==value,('clobbered',r,hex(uc.reg_read(r)),hex(value))
        for where,raw in ((ADDR_A,desc_a),(ADDR_B,desc_b),
                          (MASK_A,mask_a or b'\x00\x00'),
                          (MASK_B,mask_b or b'\x00\x00')):
            assert bytes(uc.mem_read(where-8,8))==CANARY
            assert bytes(uc.mem_read(where,len(raw)))==raw
            assert bytes(uc.mem_read(where+len(raw),8))==CANARY
        result=uc.reg_read(UC_M68K_REG_D3)
        result=result-0x100000000 if result&0x80000000 else result
        if expect is not None:
            assert result==expect,(result,expect,mode,desc_a.hex(),desc_b.hex())
        return result


def run_pair(machine, a,ia,b,ib, mode, *, screen=SCREEN,
             global_limit=None, local_limits=None, expect=None):
    if local_limits is None: local_limits={}
    desc_a=descriptor(a,ia,MASK_A,screen,global_limit,local_limits)
    desc_b=descriptor(b,ib,MASK_B,screen,global_limit,local_limits)
    reference=int(collision(a,b,screen=screen,mode=('rect' if mode==0 else 'mask'),
                            global_limit=global_limit,local_limits=local_limits))
    if expect is not None: assert reference==expect,('oracle error',reference,expect)
    return machine.run(desc_a,desc_b,ia.mask,ib.mask,mode,expect=reference)


class CollisionNativeMC68020(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code,cls.labels=emit_collision020()
        cls.machines=[NativePair(base,cls.code) for base in (0x10000,0x25000)]

    def test_01_deterministic_emission_and_m68k_disassembly(self):
        source,labels=emit_collision020()
        self.assertEqual(source,self.code)
        self.assertEqual(labels,self.labels)
        self.assertEqual(labels['p2a_pair_entry'],0)
        self.assertLess(len(source),32766)
        self.assertEqual(len(source)%2,0)
        decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        disassembled=list(decoder.disasm(source,0x10000))
        self.assertEqual(sum(i.size for i in disassembled),len(source))
        self.assertFalse(any(i.mnemonic.startswith('dc.') for i in disassembled))
        self.assertTrue(any(i.mnemonic.startswith('mulu') for i in disassembled))
        print('P2A_NATIVE_SHA',sha256(source).hexdigest(),'BYTES',len(source),flush=True)

    def test_02_rectangle_hit_and_touching_edges(self):
        i=image(8,8)
        for m in self.machines:
            a=fixture(i,1,10,10)
            for x,y,hit in ((10,10,1),(17,10,1),(18,10,0),(10,18,0),
                            (18,18,0),(-30,-30,0)):
                b=fixture(i,2,x,y)
                run_pair(m,a,i,b,i,0,expect=hit)

    def test_03_mask_pixel_intersection_and_opaque_zero(self):
        one=image(8,1,[1,0,0,0,0,0,0,0])
        last=image(8,1,[0,0,0,0,0,0,0,1])
        opaque=image(8,1)
        for m in self.machines:
            run_pair(m,fixture(one,1,10,10),one,fixture(last,2,10,10),last,0,expect=1)
            run_pair(m,fixture(one,1,10,10),one,fixture(last,2,10,10),last,1,expect=0)
            run_pair(m,fixture(one,1,10,10),one,fixture(opaque,2,10,10),opaque,1,expect=1)
            run_pair(m,fixture(opaque,1,10,10),opaque,fixture(opaque,2,10,10),opaque,1,expect=1)

    def test_04_signed_hotspots_and_screen_clipping(self):
        a=image(8,6,[1]*48,hot=(4,3))
        b=image(9,7,[int(j%4==0) for j in range(63)],hot=(-3,-2))
        cases=((2,1,7,2),(0,0,4,3),(-5,0,0,0),(318,250,319,250),
               (32767,32767,-32768,-32768),(-32768,-32768,0,0))
        for m in self.machines:
            for x,y,xx,yy in cases:
                for mode in (0,1):
                    run_pair(m,fixture(a,1,x,y),a,fixture(b,2,xx,yy),b,mode)

    def test_05_limits_global_local_and_fully_offscreen(self):
        a=image(8,6,[1]*48)
        b=image(8,6,[1]*48)
        for m in self.machines:
            for mode in (0,1):
                A=fixture(a,1,0,0)
                B=fixture(b,2,4,0)
                run_pair(m,A,a,B,b,mode,expect=1)
                run_pair(m,A,a,B,b,mode,global_limit=Rect(0,0,4,6),expect=0)
                run_pair(m,A,a,B,b,mode,global_limit=Rect(4,0,1,6),expect=1)
                run_pair(m,A,a,B,b,mode,local_limits={1:Rect(0,0,4,6)},expect=0)
                run_pair(m,A,a,B,b,mode,local_limits={1:Rect(4,0,1,6)},expect=1)
                run_pair(m,fixture(a,1,-20,-20),a,B,b,mode,expect=0)

    def test_06_real_agbo_masks_many_unaligned_widths(self):
        random=Random(0xA6A020)
        cases=0
        for w in (1,2,7,8,9,15,16,17,23,31,32,33):
            h=random.choice((1,2,3,6))
            vis1=[random.randint(0,1) for _ in range(w*h)]
            vis2=[random.randint(0,1) for _ in range(w*h)]
            a=image(w,h,vis1)
            b=image(w,h,vis2)
            for m in self.machines:
                for shift in (-3,-1,0,1,3):
                    for mode in (0,1):
                        run_pair(m,fixture(a,1,18,25),a,
                                 fixture(b,2,18+shift,25),b,mode)
                        cases+=1
        self.assertEqual(cases,240)

    def test_07_randomized_native_vs_independent_model(self):
        random=Random(0x20A0C0)
        cases=0
        for _ in range(180):
            w1,h1=random.randint(1,22),random.randint(1,7)
            w2,h2=random.randint(1,22),random.randint(1,7)
            src=[]
            for w,h in ((w1,h1),(w2,h2)):
                vis=None if random.randrange(4)==0 else [random.randrange(2) for _ in range(w*h)]
                src.append(image(w,h,vis,hot=(random.randint(-6,6),random.randint(-6,6))))
            a,b=src
            x,y=random.randint(-20,330),random.randint(-12,264)
            xx=x+random.randint(-25,25)
            yy=y+random.randint(-12,12)
            A,B=fixture(a,1,x,y),fixture(b,2,xx,yy)
            zone=None if random.randrange(3) else Rect(random.randint(0,30),0,random.randint(1,200),256)
            local={}
            if random.randrange(4)==0: local={1:Rect(0,random.randint(0,20),320,random.randint(1,100))}
            for m in self.machines:
                for mode in (0,1):
                    run_pair(m,A,a,B,b,mode,global_limit=zone,local_limits=local)
                    cases+=1
        self.assertEqual(cases,720)

    def test_08_refuse_bad_mode_and_descriptor_pointers(self):
        a=image(8,1,[1]*8)
        b=fixture(a,2,0,0)
        first=fixture(a,1,0,0)
        da=descriptor(first,a,MASK_A,SCREEN,None,{})
        db=descriptor(b,a,MASK_B,SCREEN,None,{})
        for machine in self.machines:
            for mode in (-1,2,42):
                self.assertEqual(machine.run(da,db,a.mask,a.mask,mode),-1)
            self.assertEqual(machine.run(da,db,a.mask,a.mask,1,ptr_a=0),-1)
            self.assertEqual(machine.run(da,db,a.mask,a.mask,1,ptr_a=ADDR_A+1),-1)

    def test_09_reject_bad_stride_extent_and_unaligned_mask(self):
        a=image(8,1,[1]*8)
        first=fixture(a,1,0,0)
        d=bytearray(descriptor(first,a,MASK_A,SCREEN,None,{}))
        base=bytes(d)
        from struct import pack_into
        for m in self.machines:
            for off,value in ((24,0),(24,4097),(28,0),(32,4),(36,MASK_A+1),
                              (16,20),(8,17),(12,2)):
                d[:]=base
                if off in (16,8,12):
                    pack_into('>i',d,off,value)
                else:
                    pack_into('>I',d,off,value)
                self.assertEqual(m.run(bytes(d),base,a.mask,a.mask,1),-1,(off,value))


if __name__=='__main__':
    unittest.main(verbosity=2)
