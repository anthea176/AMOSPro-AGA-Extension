#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Detached AGSP -> ExtSprite OS ABI model, real MC68020 instructions.

The mock validates the documented OS entry registers and TagItem/BitMap
contracts, and independently reconstructs input planes from pixels.
It never claims to emulate real graphics.library or Sprite DMA.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from m19_s1_agsp_bank import empty_bank,parse_payload,put_capture,set_hotspot

CODE,STOP,EXEC,GFX,STACK,SOURCE,EXT0,EXT1=(
    0x20000,0x30000,0x80000,0x90000,0xb0000,0x100000,0x140000,0x150000)
REGS=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
      UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
      UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)

def make(width,height,colors,ident=17):
    pixels=bytes((x+3*y)%(colors+1) for y in range(height) for x in range(width))
    cmap=bytes(3)+bytes(v for i in range(1,16) for v in (i*11,255-i*7,i*13))
    return put_capture(empty_bank(),ident,pixels,width,height,0,0,width,height,cmap,0,mode='s2')

def plane(im,p):
    return bytes(sum(((im.index(x+i,y)>>p)&1)<<(7-i) for i in range(8))
                 for y in range(im.height) for x in range(0,im.width,8))

class Machine:
    def __init__(self,code,payload,version=40,negsize=1100,possize=34,mode='ok'):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        self.u.mem_write(4,pack('>I',EXEC))
        self.u.mem_write(GFX+16,pack('>HHH',negsize,possize,version))
        self.u.mem_write(SOURCE,payload)
        self.u.mem_write(EXT0,b'\xa5'*64)
        self.u.mem_write(EXT1,b'\x5a'*64)
        for a in (EXEC-534,GFX-390,GFX-1020,GFX-1032):
            self.u.mem_write(a,b'\x4e\x75')
        self.payload=payload
        self.mode=mode
        self.live=set()
        self.events=[]
        self.calls=0
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def reg(self,r):return self.u.reg_read(r)
    def volatile(self,result):
        for r,v in ((UC_M68K_REG_D0,result),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            self.u.reg_write(r,v)
    def on_write(self,u,access,a,n,value,user):
        assert STACK-4096<=a and a+n<=STACK+4,('write outside private stack',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==EXEC-534:
            p=self.reg(UC_M68K_REG_A1)
            ok=SOURCE<=p<SOURCE+len(self.payload)
            if self.mode=='bad_end' and p!=SOURCE:ok=False
            self.volatile(1 if ok else 0)
        elif a==GFX-390:
            im=parse_payload(self.payload).image(self.ident)
            self.bm=self.reg(UC_M68K_REG_A0)
            assert STACK-4096<=self.bm<STACK
            assert tuple(self.reg(r) for r in (UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2))==(im.depth,im.width,im.height)
            self.events.append('InitBitMap')
            stride=im.width//8+(2 if self.mode=='bad_stride' else 0)
            self.u.mem_write(self.bm,pack('>HHBBH',stride,im.height,0,im.depth,0))
            self.volatile(0)
        elif a==GFX-1020:
            im=parse_payload(self.payload).image(self.ident)
            assert self.reg(UC_M68K_REG_A2)==self.bm
            tag=self.reg(UC_M68K_REG_A1)
            assert STACK-4096<=tag<=STACK-24
            tags=unpack_from('>6I',self.read(tag,24))
            attached=self.calls==1
            assert tags==((0x81000000,im.width,0x81000008,1,0,0) if attached
                          else (0x81000000,im.width,0,0,0,0))
            stride,rows,flags,depth,pad,*ptrs=unpack_from('>HHBBH8I',self.read(self.bm,40))
            assert (stride,rows,depth)==(im.width//8,im.height,im.depth)
            assert all(p==0 for p in ptrs[depth:])
            for i,p in enumerate(ptrs[:depth]):
                n=stride*rows
                assert SOURCE<=p and p+n<=SOURCE+len(self.payload)
                assert self.read(p,n)==plane(im,i),(i,im.width,im.height)
                if i:assert p==ptrs[i-1]+n
            assert not attached or depth==4
            self.calls+=1
            self.events.append('AllocOdd' if attached else 'AllocEven')
            if self.mode==('oom2' if attached else 'oom1'):
                self.volatile(0)
            else:
                out=EXT1 if attached else EXT0
                self.live.add(out)
                self.volatile(out)
        elif a==GFX-1032:
            p=self.reg(UC_M68K_REG_A2)
            assert p in self.live
            self.live.remove(p)
            self.events.append('FreeDetached')
            self.volatile(0)
    def invoke(self,ident=17,pointer=SOURCE,length=None,gfx=GFX):
        self.ident=ident
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,pointer)
        u.reg_write(UC_M68K_REG_A6,gfx)
        saved={r:self.reg(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,len(self.payload) if length is None else length)
        u.reg_write(UC_M68K_REG_D1,ident&0xffffffff)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE,STOP,count=20_000_000)
        assert self.reg(UC_M68K_REG_PC)==STOP
        assert self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items()),'register ABI'
        assert self.read(SOURCE,len(self.payload))==self.payload
        assert self.read(EXT0,64)==b'\xa5'*64 and self.read(EXT1,64)==b'\x5a'*64
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)

def check(code,payload,ident=17,version=40):
    im=parse_payload(payload).image(ident)
    m=Machine(code,payload,version=version)
    odd=im.depth==4
    assert m.invoke(ident)==(EXT0,EXT1 if odd else 0)
    assert m.live==({EXT0,EXT1} if odd else {EXT0})
    assert m.events==['InitBitMap','AllocEven']+(['AllocOdd'] if odd else [])
def reject(code,payload,ident=17,events=(),invoke=None,**kwargs):
    m=Machine(code,payload,**kwargs)
    assert m.invoke(ident,**(invoke or {}))==(0,0)
    assert not m.live and m.events==list(events),(kwargs,m.events)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    n=0
    for width in (16,32,64):
        for height in (1,7,256):
            for colors in (0,3,4,15):
                raw=make(width,height,colors)
                for v in ((39,40,46) if colors<=3 else (40,46)):
                    check(code,raw,version=v);n+=1
                if colors>=4:
                    reject(code,raw,version=39);n+=1
        for colors in (3,15):
            raw=make(width,9,colors)
            reject(code,raw,mode='oom1',events=('InitBitMap','AllocEven'));n+=1
            reject(code,raw,mode='bad_stride',events=('InitBitMap',));n+=1
            if colors==15:
                reject(code,raw,mode='oom2',events=('InitBitMap','AllocEven','AllocOdd','FreeDetached'));n+=1
    raw=make(64,5,15)
    mixed=put_capture(raw,2,bytes([0,1,2,3]*8),32,1,0,0,32,1,
                      bytes(3)+bytes.fromhex('ff000000ff000000ff'),0,mode='s2')
    check(code,mixed,2);check(code,set_hotspot(mixed,17,-3,5));n+=2
    for v in (0,38):
        reject(code,raw,version=v);n+=1
    reject(code,raw,negsize=1030);n+=1
    reject(code,raw,possize=22);n+=1
    reject(code,raw,mode='bad_end');n+=1
    for ident in (0,1,4097,-1):
        reject(code,raw,ident=ident);n+=1
    for opts in ({'pointer':0},{'pointer':SOURCE+1},{'pointer':0xfffffff0},
                 {'length':30},{'length':len(raw)-2},{'gfx':0},{'gfx':GFX+1}):
        reject(code,raw,invoke=opts);n+=1
    reject(code,empty_bank());n+=1
    # Generation is an unsigned nonzero counter: flipping a high bit
    # is still canonical. Require zero explicitly for the negative case.
    changed=bytearray(raw)
    changed[24:28]=pack('>I',0x01000002)
    check(code,bytes(changed));n+=1
    corrupt=[]
    for off in (0,5,10,20,32+8,32+12):
        bad=bytearray(raw);bad[off]^=1
        corrupt.append((off,bytes(bad)))
    bad=bytearray(raw);bad[24:28]=bytes(4)
    corrupt.append((24,bytes(bad)))
    for off,bad in corrupt:
        try:
            parse_payload(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(('noncanonical fixture expected',off))
        reject(code,bad);n+=1
    print('S2D_P2A_DETACHED_EXT_ABI_PASS',n,sha256(code).hexdigest(),flush=True)

if __name__=='__main__':main()
