#!/usr/bin/env python3
"""M18 CBlock 68000 standalone core: CPU byte/word + mocked graphics Blitter.

Executes real emitted 68000 instructions, stubs only OS graphics.library;
not a WinUAE bench, not an AP20 wrapper, no physical DMA measurement.
"""
from __future__ import annotations
from random import Random
from struct import pack,unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
)
from m18_cblock_copy_emit import emit_cblock_copy_core
from m18_cblock_copy_model import Surface,copy_pixel_oracle,copy_blitter_word_model

AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
CODE=0x10000; STOP=0x12000; SRC_BM=0x20000; DST_BM=0x30000
SRC_PLANE=0x40000; DST_PLANE=0x100000; STEP=0x10000
STACK=0x800000; GFX=0x900000
GUARD=b'CBLOCK-CANARY-8PIX'

def read_u16(uc,addr):return unpack('>H',bytes(uc.mem_read(addr,2)))[0]
def read_u32(uc,addr):return unpack('>I',bytes(uc.mem_read(addr,4)))[0]
def read_bm(uc,addr):
    stride=read_u16(uc,addr)
    rows=read_u16(uc,addr+2)
    depth=bytes(uc.mem_read(addr+5,1))[0]
    ptrs=[read_u32(uc,addr+8+4*i) for i in range(depth)]
    planes=[bytearray(uc.mem_read(p,stride*rows)) for p in ptrs]
    return Surface(stride*8, rows, depth, stride, planes),ptrs

def execute(core,src,dest,*,sx,sy,dx,dy,width,height,mode,malformed=None):
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0,0x1000000)
    uc.mem_write(CODE,core)
    uc.mem_write(STOP,bytes.fromhex('4e71'))
    uc.mem_write(STACK,pack('>I',STOP))
    src_ptrs=[SRC_PLANE+STEP*i for i in range(src.depth)]
    dst_ptrs=[DST_PLANE+STEP*i for i in range(dest.depth)]
    def bitmap(src,destptrs):
        return pack('>HHBBH',src.stride,src.height,0,src.depth,0)+b''.join(
            pack('>I',destptrs[i] if i<len(destptrs) else 0) for i in range(8))
    sb=bytearray(bitmap(src,src_ptrs));db=bytearray(bitmap(dest,dst_ptrs))
    if malformed=='src_depth':sb[5]=0
    if malformed=='dst_depth':db[5]=dest.depth-1
    if malformed=='src_plane':sb[8:12]=bytes(4)
    if malformed=='dest_plane':db[8:12]=bytes(4)
    if malformed=='src_bpr':sb[0:2]=bytes(2)
    if malformed=='dst_rows':db[2:4]=bytes(2)
    uc.mem_write(SRC_BM,bytes(sb));uc.mem_write(DST_BM,bytes(db))
    for ptr,plane in zip(src_ptrs,src.planes):uc.mem_write(ptr,bytes(plane)+GUARD)
    for ptr,plane in zip(dst_ptrs,dest.planes):uc.mem_write(ptr,bytes(plane)+GUARD)
    for disp in (198,606,228):uc.mem_write(GFX-disp,bytes.fromhex('4e75'))
    calls=[]
    def ret():
        sp=uc.reg_read(AR[7]);pc=read_u32(uc,sp)
        uc.reg_write(AR[7],sp+4);uc.reg_write(UC_M68K_REG_PC,pc)
    def hook(uc,address,size,user_data):
        if address==GFX-198:
            rp=uc.reg_read(AR[1]);uc.mem_write(rp,bytes(128))
            calls.append('InitRastPort');ret();return
        if address==GFX-606:
            abm=uc.reg_read(AR[0]);rp=uc.reg_read(AR[1]);dbm=read_u32(uc,rp+4)
            assert (abm,dbm)==(SRC_BM,DST_BM)
            vals=[uc.reg_read(r) for r in DR[:7]]
            assert vals==[sx,sy,dx,dy,width,height,0xc0],vals
            sbm,src_addr=read_bm(uc,abm)
            dbm,dst_addr=read_bm(uc,dbm)
            copy_blitter_word_model(sbm,dbm,sx,sy,dx,dy,width,height)
            for ptr,p in zip(dst_addr,dbm.planes):uc.mem_write(ptr,bytes(p))
            calls.append('BltBitMapRastPort');ret();return
        if address==GFX-228:
            assert calls and calls[-1]=='BltBitMapRastPort'
            calls.append('WaitBlit');ret();return
        raise AssertionError('Unexpected OS call: '+hex(address))
    uc.hook_add(UC_HOOK_CODE,hook,begin=GFX-700,end=GFX)
    inputs={
        AR[0]:SRC_BM,AR[1]:DST_BM,AR[2]:0x723402,AR[3]:0x723404,
        AR[4]:0x723406,AR[5]:0x723408,AR[6]:GFX,
        DR[0]:sx&0xffffffff,DR[1]:sy&0xffffffff,
        DR[2]:dx&0xffffffff,DR[3]:dy&0xffffffff,
        DR[4]:width&0xffffffff,DR[5]:height&0xffffffff,
        DR[6]:mode&0xffffffff,DR[7]:0x87654321,
    }
    for reg,val in inputs.items():uc.reg_write(reg,val)
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    uc.reg_write(AR[7],STACK)
    uc.emu_start(CODE,STOP,count=2500000)
    assert uc.reg_read(UC_M68K_REG_PC)==STOP, 'core did not return'
    assert uc.reg_read(AR[7])==STACK+4, 'unbalanced stack'
    for reg,val in inputs.items():
        if reg not in (DR[2],DR[3]):
            assert uc.reg_read(reg)==val, ('register corrupted',reg,uc.reg_read(reg),val)
    assert uc.reg_read(DR[2])==0
    status=uc.reg_read(DR[3])
    after=[bytearray(uc.mem_read(ptr,len(p))) for ptr,p in zip(dst_ptrs,dest.planes)]
    assert [bytes(uc.mem_read(ptr,len(p))) for ptr,p in zip(src_ptrs,src.planes)]==[
        bytes(p) for p in src.planes], 'source mutated'
    for ptr,p in zip(src_ptrs,src.planes):
        assert bytes(uc.mem_read(ptr+len(p),len(GUARD)))==GUARD
    for ptr,p in zip(dst_ptrs,dest.planes):
        assert bytes(uc.mem_read(ptr+len(p),len(GUARD)))==GUARD
    return status,after,calls


def main():
    native,labels=emit_cblock_copy_core()
    assert len(native)<3000
    asm=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(native,CODE))
    assert sum(ins.size for ins in asm)==len(native),'invalid 68000 instruction'
    assert native==emit_cblock_copy_core()[0],'nondeterministic code'
    rng=Random(0xCB108)
    good=bad=0
    for depth in (1,4,8):
        for w,h in ((8,8),(16,16),(24,12),(32,8),(64,20)):
            src=Surface.make(112,47,depth,seed=rng.randrange(999999))
            dest=Surface.make(112,47,depth,seed=rng.randrange(999999))
            for sx,dx,mode in ((8,8,0),(16,24,0),(8,16,2),(16,8,2),(16,32,1)):
                if mode==1 and (sx|dx|w)&15:continue
                if max(sx,dx)+w>112:continue
                expected=dest.clone()
                copy_pixel_oracle(src,expected,sx,1,dx,3,w,h)
                status,actual,calls=execute(native,src,dest,sx=sx,sy=1,dx=dx,dy=3,
                                             width=w,height=h,mode=mode)
                assert status==1,(depth,w,sx,dx,mode,'return')
                assert tuple(bytes(x) for x in actual)==expected.signature(),(
                    depth,w,sx,dx,mode,'pixel mismatch')
                assert calls==(['InitRastPort','BltBitMapRastPort','WaitBlit']
                               if mode==2 else []),calls
                good+=1
    src=Surface.make(112,47,8,seed=345)
    dest=Surface.make(112,47,8,seed=876)
    args=dict(sx=8,sy=2,dx=8,dy=2,width=24,height=16,mode=0)
    rejects=(dict(mode=3),dict(mode=-1),dict(width=0),dict(width=15),
             dict(width=120),dict(sx=1),dict(sy=-1),dict(dx=-8),
             dict(dx=99),dict(dy=40),dict(height=0),dict(height=100),
             dict(mode=1),dict(malformed='src_depth'),
             dict(malformed='dst_depth'),dict(malformed='src_plane'),
             dict(malformed='dest_plane'),dict(malformed='src_bpr'),
             dict(malformed='dst_rows'))
    for over in rejects:
        kw=args|over
        status,actual,calls=execute(native,src,dest,**kw)
        assert status==0,(kw,status)
        assert tuple(bytes(p) for p in actual)==dest.signature(),kw
        assert calls==[],(kw,calls)
        bad+=1
    print('M18 CBlock standalone 68000 core Gate A PASS:',len(native),'bytes;',
          good,'CPU/Blitter pixel, register and stack cases;',bad,'rejections.')
    print('Blitter OS calls are mocked, not physical DMA; NO WinUAE timing or AP20 validation.')

if __name__=='__main__':main()
