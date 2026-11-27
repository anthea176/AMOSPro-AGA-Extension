#!/usr/bin/env python3
"""S2c-P0 real MC68020 capture and repack vs the existing AGSP v1 model.

No OS or DMA publication. Old S1 tests remain unchanged; S2c allows 15 opaque
RGB24 colors but preserves the exact two-plane format for 0..3.
"""
import os
from pathlib import Path
from struct import pack
import random
import unittest
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_A0, UC_M68K_REG_A7, UC_M68K_REG_D0, UC_M68K_REG_D1)
from test_m19_s1p1_native_capture import (
    planar, SEED_REGS, PC, DESC, SOURCE, CMAP, OUTPUT, PALOUT, STACK, STOP)
from test_m19_s1p1b_agsp_repack import RepackRunner, DEST
from test_m19_s1p1c_agsp_validate import Runner as Validator
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload

FILL=0x5a
GUARD=16
STAGE=2048

def cmap():
    return b''.join(bytes((i,(17*i+7)&255,(43*i+11)&255)) for i in range(256))

class Capture:
    def __init__(self):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x300000)
        code=Path(os.environ['S2C_CAPTURE_BIN']).read_bytes()
        assert 100<len(code)<20000
        self.u.mem_write(PC,code)
    def run(self,pixels,w,h,depth,palette,x,y,height,transparent,bad=None):
        u=self.u
        stride=(w+15)//16*2
        planes=planar(pixels,w,h,depth,stride)
        addresses=[SOURCE+0x10000*i for i in range(depth)]
        for addr,p in zip(addresses,planes):
            u.mem_write(addr,p)
        desc=bytearray(pack('>8I3II8H',*(addresses+[0]*(8-depth)),
              CMAP,OUTPUT,PALOUT,stride,w,h,depth,x,y,height,transparent,0))
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

class S2cCaptureRepack(unittest.TestCase):
    def setUp(self):
        self.capture=Capture()
        self.repack=RepackRunner()
        self.validator=Validator()
    def image(self,n,height=16,w=48,h=None,x=13,y=0,depth=8,palette=None,
              transparent=0,seed=None,old=None,ident=1):
        h=height+y if h is None else h
        palette=cmap() if palette is None else palette
        choices=[transparent]+[i for i in range(1,256) if i!=transparent and i<(1<<depth)][:n]
        pixels=bytearray([transparent])*(w*h)
        for row in range(height):
            for col in range(16):
                pixels[(y+row)*w+x+col]=choices[(row*16+col)%len(choices)]
        if seed is not None:
            rnd=random.Random(seed)
            # Preserve the first scanline and first-seen ordering; shuffle the rest.
            for row in range(1,height):
                for col in range(16):pixels[(y+row)*w+x+col]=rnd.choice(choices)
        params=(bytes(pixels),w,h,x,y,16,height,palette,transparent)
        model=put_capture(old if old is not None else empty_bank(),ident,*params,mode='s2')
        one=put_capture(empty_bank(),ident,*params,mode='s2')
        img=parse_payload(one).image(ident)
        rc,count,raw,colors=self.capture.run(bytes(pixels),w,h,depth,palette,x,y,height,transparent)
        self.assertEqual((rc,count),(1,img.opaque_count))
        self.assertEqual(raw[:len(img.planes)],img.planes)
        self.assertEqual(raw[len(img.planes):],bytes([FILL])*(STAGE-len(img.planes)))
        self.assertEqual(colors,img.palette)
        # RepackRunner copies the stage fixture, but the exact native capture
        # above already matched every byte of that fixture.
        size,ok=self.repack.run(old,one,ident,capacity=len(model))
        self.assertEqual((size,ok),(len(model),1))
        got=self.repack.read(DEST,size)
        self.assertEqual(got,model)
        self.assertEqual(self.repack.read(DEST+size,16),bytes([FILL])*16)
        self.assertEqual(self.validator.test(got),(1,len(parse_payload(got).images)))
        return got,one
    def test_every_color_count_and_depth_threshold(self):
        for n in range(16):
            with self.subTest(opaque=n):
                raw,_=self.image(n,seed=n)
                i=parse_payload(raw).image(1)
                self.assertEqual((i.opaque_count,i.depth),(n,2 if n<=3 else 4))
    def test_unaligned_capture_nonzero_transparency_and_max_height(self):
        for n in (3,4,15):
            with self.subTest(opaque=n):
                self.image(n,height=256,x=7,depth=8,transparent=19,seed=n)
        self.image(14,height=2,depth=4,transparent=15,x=1)
        self.image(1,height=1,depth=1,x=31)
    def test_opaque_black_and_duplicate_rgb(self):
        pal=bytearray(cmap())
        pal[3:6]=bytes(3)
        pal[6:9]=pal[9:12]
        raw,_=self.image(5,palette=bytes(pal))
        i=parse_payload(raw).image(1)
        self.assertEqual((i.opaque_count,i.depth),(4,4))
        self.assertEqual(i.palette[3:6],bytes(3))
        raw,_=self.image(4,palette=bytes(pal))
        self.assertEqual(parse_payload(raw).image(1).depth,2)
    def test_mixed_bank_insert_replace_and_depth_transitions(self):
        bank,_=self.image(15,height=19,ident=20)
        bank,_=self.image(3,height=3,ident=1,old=bank)
        bank,_=self.image(4,height=7,ident=12,old=bank)
        before=parse_payload(bank)
        bank,_=self.image(2,height=5,ident=12,old=bank)
        self.assertEqual(parse_payload(bank).image(20),before.image(20))
        self.assertEqual(parse_payload(bank).image(1),before.image(1))
        bank,_=self.image(15,height=1,ident=1,old=bank)
        self.assertEqual([i.depth for i in parse_payload(bank).images],[4,2,4])
    def test_refuse_16_distinct_colors_and_invalid_descriptors_without_write(self):
        pal=cmap()
        pix=bytes((i%17) for i in range(32*16))
        def check(result):
            self.assertEqual(result[:2],(0,0))
            self.assertEqual(result[2],bytes([FILL])*STAGE)
            self.assertEqual(result[3],bytes([FILL])*48)
        check(self.capture.run(pix,32,16,8,pal,0,0,16,0))
        good=bytes(i%4 for i in range(32*16))
        for bad in ({54:17},{52:9},{44:1},{44:5},{62:1},{36:0},
                    {40:PALOUT+1},{36:OUTPUT+1},{0:0},{58:0},{58:257},
                    {60:256},{56:1}):
            with self.subTest(bad=bad):
                check(self.capture.run(good,32,16,8,pal,0,0,16,0,bad))
    def test_repack_refusals_preserve_old_and_destination(self):
        old,_=self.image(15,ident=5,height=11)
        model,one=self.image(4,ident=1,height=5,old=old)
        for cap,changes in ((len(model)-1,None),(len(model),{28:16}),
                            (len(model),{36:1}),(len(model),{8:0}),
                            (len(model),{26:0})):
            with self.subTest(cap=cap,changes=changes):
                self.assertEqual(self.repack.run(old,one,1,capacity=cap,corrupt=changes),(0,0))
                self.assertEqual(self.repack.read(DEST,0x5000),bytes([FILL])*0x5000)

if __name__=='__main__':unittest.main(verbosity=2)
