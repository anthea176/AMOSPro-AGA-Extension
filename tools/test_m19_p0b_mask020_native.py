#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Real MC68020 Unicorn Gate A for the private M19 P0b mask kernel.

Runs exact emitted machine code, comparing every mask bit to the AGBO host
oracle. This tests a PRIVATE kernel only, not a new AMOS AP20 command, not
WinUAE and not Compiler. Caller allocation/AMOS bank transaction is separate.
"""
from __future__ import annotations
from struct import pack

from unicorn import UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, Uc
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_A0, UC_M68K_REG_A1,
    UC_M68K_REG_A7, UC_M68K_REG_D0, UC_M68K_REG_D1,
    UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4,
    UC_M68K_REG_PC, UC_M68K_REG_SR,
)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from m19_p0b_mask020_emit import emit_mask020
from m19_p0a_multi_bob_abk import pack_pixels

SOURCE = 0x400100
OUTPUT = 0x500200
STACK = 0x60fffc
STOP = 0x12000
SENTINEL = bytes.fromhex('a55a33cc')


def run_case(raw, *, base=0x10000, width=17, height=3, depth=8,
             transparent=0, bad_stride=None, source=SOURCE,
             output=OUTPUT, pixels=None):
    valid_geom = (1 <= width <= 4096 and 1 <= height <= 4096 and
                  width * height <= 0x400000 and 1 <= depth <= 8)
    if pixels is None and valid_geom:
        pixels=bytes((((x*19+y*31+x//3*7)^0x5a)&((1<<depth)-1))
                     for y in range(height) for x in range(width))
    stride=2*((max(width,1)+15)//16)
    if valid_geom:
        img=pack_pixels(1,width,height,depth,pixels)
        planes=img.planes
        size=len(img.planes)//depth
    else:
        planes=b'\x8a\xaa'*512
        size=stride*max(height,1)
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    uc.mem_map(0x10000,0x20000)
    uc.mem_map(0x400000,0x200000)
    uc.mem_map(0x600000,0x10000)
    uc.mem_write(base,raw)
    uc.mem_write(source,planes)
    outsize=max(size,2)
    uc.mem_write(output-4,SENTINEL)
    uc.mem_write(output,bytes([0xcc])*(outsize+4))
    uc.mem_write(output+outsize,SENTINEL)
    uc.mem_write(STACK,pack('>I',STOP))
    regvals=[(UC_M68K_REG_A0,source),(UC_M68K_REG_A1,output),
             (UC_M68K_REG_D0,width&0xffffffff),
             (UC_M68K_REG_D1,height&0xffffffff),
             (UC_M68K_REG_D2,depth&0xffffffff),
             (UC_M68K_REG_D3,transparent&0xffffffff),
             (UC_M68K_REG_D4,stride if bad_stride is None else bad_stride),
             (UC_M68K_REG_A7,STACK),(UC_M68K_REG_SR,0x2000)]
    for reg,val in regvals:uc.reg_write(reg,val)
    uc.emu_start(base,STOP,count=4000000)
    assert uc.reg_read(UC_M68K_REG_PC)==STOP
    assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
    assert uc.reg_read(UC_M68K_REG_D2)==0
    assert bytes(uc.mem_read(output-4,4))==SENTINEL
    assert bytes(uc.mem_read(output+outsize,4))==SENTINEL
    result=uc.reg_read(UC_M68K_REG_D3)
    mask=bytes(uc.mem_read(output,outsize))
    if result==1:
        assert width>0 and height>0 and 1<=depth<=8
        assert source%2==0 and output%2==0
        assert bad_stride is None
        expected=bytearray(size)
        for y in range(height):
            for x in range(width):
                if pixels[y*width+x]!=transparent:
                    off=y*stride+2*(x//16)+(1 if x%16>=8 else 0)
                    expected[off]|=0x80>>(x%8)
        assert mask[:size]==bytes(expected), (width,height,depth,transparent,
                   mask[:size].hex(),bytes(expected).hex())
        assert bytes(uc.mem_read(source,len(planes)))==planes,'source changed'
        return 1
    assert mask==bytes([0xcc])*outsize, 'rejected input wrote to destination'
    assert result==0
    return 0


def main():
    raw,labels=emit_mask020()
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(raw[:labels['tail_table']],0x10000))
    assert sum(i.size for i in dis)==labels['tail_table']
    assert any(i.mnemonic.lower().startswith('bfextu') for i in dis), 'no 68020 bitfield'
    assert not any(i.mnemonic.startswith('dc.') for i in dis)
    cases=0
    for base in (0x10000,0x18000):
        for depth in (1,4,8):
            for width,height in ((1,1),(7,2),(17,3),(31,5),(32,2),(37,4),(65,3)):
                pixels=bytes((((x*19+y*31+x//3*7)^0x5a)&((1<<depth)-1))
                             for y in range(height) for x in range(width))
                for transparent in (0,(1<<depth)-1):
                    assert run_case(raw,base=base,width=width,height=height,
                                    depth=depth,transparent=transparent,pixels=pixels)==1
                    cases+=1
        for params in ({'width':0},{'width':4097},{'height':0},
                       {'depth':0},{'depth':9},{'transparent':256},
                       {'depth':1,'transparent':2},{'bad_stride':9},
                       {'source':SOURCE+1},{'output':OUTPUT+1}):
            # Invalid width/depth never use the image generator.
            assert run_case(raw,base=base,**params)==0,params
            cases+=1
    print('M19 P0b MC68020 private mask CPU Gate A PASS',cases,
          'pixel/guard scenarios; kernel bytes',len(raw),
          '; NO AP20, NO WinUAE, NO Compiler')


if __name__=='__main__':main()
