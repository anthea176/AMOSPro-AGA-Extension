#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2d-P0 isolated MC68020 capture/repack. No OS, AP20, DMA or AMOS runtime proof."""
import os
from pathlib import Path
from struct import pack,pack_into
import random
import unittest
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
from test_m19_s1p1_native_capture import planar,SEED_REGS,PC,DESC,SOURCE,CMAP,OUTPUT,PALOUT,STACK,STOP
from test_m19_s1p1b_agsp_repack import (OLD,PLANES,PALETTE,DEST,REQUEST,REGS)
from test_m19_s1p1c_agsp_validate import Runner as Validator
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
from m19_s2d_visual_fixture import fixture,FAMILIES,pixels as pattern

FILL=0x5a
GUARD=16
STAGE=8192

def cmap():
    return b''.join(bytes((i,(17*i+7)&255,(43*i+11)&255)) for i in range(256))

class Capture:
    def __init__(self):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x300000)
        code=Path(os.environ['S2D_CAPTURE_BIN']).read_bytes()
        assert 100<len(code)<20000
        self.u.mem_write(PC,code)
    def run(self,pixels,w,h,depth,palette,x,y,height,transparent,width,bad=None):
        u=self.u
        stride=(w+15)//16*2
        planes=planar(pixels,w,h,depth,stride)
        addresses=[SOURCE+0x10000*i for i in range(depth)]
        for addr,p in zip(addresses,planes):
            u.mem_write(addr,p)
        desc=bytearray(pack('>8I3II8H',*(addresses+[0]*(8-depth)),
              CMAP,OUTPUT,PALOUT,stride,w,h,depth,x,y,height,transparent,width))
        for off,value in (bad or {}).items():
            n=4 if off<=44 else 2
            desc[off:off+n]=value.to_bytes(n,'big')
        u.mem_write(DESC,bytes(desc))
        u.mem_write(CMAP,palette)
        u.mem_write(OUTPUT-GUARD,bytes([0xa5])*GUARD)
        u.mem_write(OUTPUT,bytes([FILL])*STAGE)
        u.mem_write(OUTPUT+STAGE,bytes([0xc3])*GUARD)
        u.mem_write(PALOUT-GUARD,bytes([0xa5])*GUARD)
        u.mem_write(PALOUT,bytes([FILL])*48)
        u.mem_write(PALOUT+48,bytes([0xc3])*GUARD)
        for i,r in enumerate(SEED_REGS):u.reg_write(r,0x55001000+i)
        saved={r:u.reg_read(r) for r in SEED_REGS}
        u.reg_write(UC_M68K_REG_SR,0x2000)
        u.reg_write(UC_M68K_REG_A0,DESC)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(PC,STOP,count=70_000_000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items())
        for addr,p in zip(addresses,planes):assert bytes(u.mem_read(addr,len(p)))==p
        assert bytes(u.mem_read(DESC,len(desc)))==desc
        assert bytes(u.mem_read(CMAP,768))==palette
        for addr,value in ((OUTPUT-GUARD,0xa5),(OUTPUT+STAGE,0xc3),
                           (PALOUT-GUARD,0xa5),(PALOUT+48,0xc3)):
            assert bytes(u.mem_read(addr,GUARD))==bytes([value])*GUARD
        return (u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1),
                bytes(u.mem_read(OUTPUT,STAGE)),bytes(u.mem_read(PALOUT,48)))

class RepackRunner:
    def __init__(self):
        self.uc=Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x400000)
        binary=Path(os.environ['S2D_REPACK_BIN']).read_bytes()
        assert 300 < len(binary) < 16000
        self.uc.mem_write(PC,binary)

    def put(self,addr,data): self.uc.mem_write(addr,bytes(data))
    def read(self,addr,n): return bytes(self.uc.mem_read(addr,n))

    def run(self,old,new_payload,new_id,capacity=0x100000,corrupt=None):
        uc=self.uc
        new=parse_payload(new_payload).image(new_id)
        self.put(PLANES,new.planes)
        self.put(PALETTE,new.palette)
        self.put(OLD,old if old is not None else bytes(32))
        self.put(DEST-16,bytes([0xa5])*16)
        self.put(DEST,bytes([0x5a])*max(0x5000,len(old or b'')+len(new.planes)+1024))
        self.put(DEST+0x5000,bytes([0xc3])*16)
        params=bytearray(pack('>6I4H2h2H',OLD if old is not None else 0,
                              len(old) if old is not None else 0,
                              PLANES,PALETTE,DEST,capacity,
                              new_id,new.height,new.opaque_count,
                              new.source_transparent_pen,
                              new.hotspot_x,new.hotspot_y,new.width,0))
        assert len(params)==40
        for offset,value in (corrupt or {}).items():
            if offset in (0,4,8,12,16,20):pack_into('>I',params,offset,value)
            else:pack_into('>H',params,offset,value)
        self.put(REQUEST,params)
        request_before=bytes(params)
        source=old if old is not None else bytes(32)
        planes=new.planes
        palette=new.palette
        for i,r in enumerate(REGS):uc.reg_write(r,0x45001100+i)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A0,REQUEST)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        self.put(STACK,pack('>I',STOP))
        uc.emu_start(PC,STOP,count=5000000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'ABI register clobber'
        assert self.read(REQUEST,len(params))==request_before
        assert self.read(OLD,len(source))==source
        assert self.read(PLANES,len(planes))==planes
        assert self.read(PALETTE,len(palette))==palette
        assert self.read(DEST-16,16)==bytes([0xa5])*16
        assert self.read(DEST+0x5000,16)==bytes([0xc3])*16
        return uc.reg_read(UC_M68K_REG_D0),uc.reg_read(UC_M68K_REG_D1)



class WideCaptureRepack(unittest.TestCase):
    def setUp(self):
        self.capture=Capture()
        self.repack=RepackRunner()
        self.validator=Validator()

    def verify(self,width,height,n,x=7,y=1,depth=8,transparent=0,old=None,ident=1,seed=0):
        w=x+width+3
        h=y+height
        pal=cmap()
        choices=[transparent]+[p for p in range(1,1<<depth) if p!=transparent][:n]
        assert len(choices)==n+1
        rnd=random.Random(seed)
        pix=bytearray([transparent])*(w*h)
        for row in range(height):
            for col in range(width):
                pix[(row+y)*w+x+col]=choices[col%len(choices)] if row==0 else rnd.choice(choices)
        params=(bytes(pix),w,h,x,y,width,height,pal,transparent)
        one=put_capture(empty_bank(),ident,*params,mode='s2')
        expected=put_capture(old if old is not None else empty_bank(),ident,*params,mode='s2')
        img=parse_payload(one).image(ident)
        rc,count,raw,colors=self.capture.run(bytes(pix),w,h,depth,pal,x,y,height,transparent,width)
        self.assertEqual((rc,count),(1,n))
        self.assertEqual(raw[:len(img.planes)],img.planes)
        self.assertEqual(raw[len(img.planes):],bytes([FILL])*(STAGE-len(img.planes)))
        self.assertEqual(colors,img.palette)
        size,ok=self.repack.run(old,one,ident,capacity=len(expected))
        self.assertEqual((size,ok),(len(expected),1))
        self.assertEqual(self.repack.read(DEST,size),expected)
        self.assertEqual(self.repack.read(DEST+size,16),bytes([FILL])*16)
        self.assertEqual(self.validator.test(expected),(1,len(parse_payload(expected).images)))
        return expected,one

    def test_every_width_and_color_count(self):
        for width in (16,32,64):
            for n in range(16):
                with self.subTest(width=width,n=n):
                    self.verify(width,1 if n%2 else 7,n,x=13,seed=n)

    def test_large_heights_alignment_and_depth(self):
        for width in (16,32,64):
            for n in (3,15):
                with self.subTest(width=width,n=n):
                    self.verify(width,256,n,x=1,y=2,transparent=19,seed=width+n)
            self.verify(width,9,3,x=15,depth=2)
            self.verify(width,7,1,x=31,depth=1)
            self.verify(width,3,4,x=0,depth=4,transparent=15)
        self.verify(64,256,0,x=7)

    def test_replacement_across_width_and_depth(self):
        raw,_=self.verify(16,7,3,ident=8)
        raw,_=self.verify(64,19,15,old=raw,ident=1)
        raw,_=self.verify(32,15,4,old=raw,ident=4)
        prior=parse_payload(raw)
        raw,_=self.verify(16,1,1,old=raw,ident=1)
        new=parse_payload(raw)
        self.assertEqual(new.image(4),prior.image(4))
        self.assertEqual(new.image(8),prior.image(8))
        self.assertEqual(new.generation,prior.generation+1)
        self.assertEqual(new.image(1).width,16)
        raw,_=self.verify(64,19,15,old=raw,ident=8)
        self.assertEqual(parse_payload(raw).image(8).width,64)

    def test_invalid_width_bounds_and_palette_before_writes(self):
        pal=cmap()
        pix=bytes(i%4 for i in range(96*2))
        for width,bad in ((0,None),(8,None),(17,None),(48,None),(128,None),
                          (65535,None),(64,{54:33}),(32,{54:65}),
                          (64,{58:0}),(64,{58:257}),(64,{56:2}),
                          (64,{44:1}),(64,{44:10}),(64,{52:9}),
                          (64,{36:0}),(64,{60:256})):
            with self.subTest(width=width,bad=bad):
                self.assertEqual(self.capture.run(pix,96,2,8,pal,0,0,2,0,width,bad),
                                 (0,0,bytes([FILL])*STAGE,bytes([FILL])*48))
        pix=bytes(i%17 for i in range(96*2))
        for width in (16,32,64):
            self.assertEqual(self.capture.run(pix,96,2,8,pal,0,0,2,0,width),
                             (0,0,bytes([FILL])*STAGE,bytes([FILL])*48))

    def test_repack_refusals(self):
        old,_=self.verify(32,7,4,ident=9)
        expected,one=self.verify(64,16,15,old=old,ident=1)
        for capacity,bad in ((len(expected)-1,None),(len(expected),{36:48}),
                             (len(expected),{36:0}),(len(expected),{38:1}),
                             (len(expected),{28:16}),(len(expected),{26:0}),
                             (len(expected),{8:0})):
            with self.subTest(capacity=capacity,bad=bad):
                self.assertEqual(self.repack.run(old,one,1,capacity,corrupt=bad),(0,0))
                self.assertEqual(self.repack.read(DEST,0x5000),bytes([FILL])*0x5000)

    def test_contrasting_visual_fixture(self):
        bank=fixture()
        self.assertEqual(bank,fixture())
        parsed=parse_payload(bank)
        self.assertEqual(self.validator.test(bank),(1,24))
        for img in parsed.images:
            n=img.opaque_count
            frame=(img.image_id-1)%2
            family=((img.image_id-1)%8)//2
            rgb=FAMILIES[family]
            pix=pattern(img.width,img.height,n,frame)
            result=self.capture.run(pix,img.width,img.height,4,bytes(3)+rgb+bytes(765-len(rgb)),
                                    0,0,img.height,0,img.width)
            self.assertEqual(result[:2],(1,n))
            self.assertEqual(result[2][:len(img.planes)],img.planes)
            self.assertEqual(result[3],img.palette)
        print('S2D_CONTRAST_FIXTURE_24_PASS',flush=True)

if __name__=='__main__':
    unittest.main(verbosity=2)
