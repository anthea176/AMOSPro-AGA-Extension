#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2f P2a: native cache/translation and detached OS ABI, not live DMA."""
import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path
from struct import pack,unpack_from
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from m19_s1_agsp_bank import parse_payload,set_hotspot,empty_bank
from test_m19_s2d_ext_prepare_cpu import (make,plane,mock_attach39,att39_type,
    att39_write,assert_attach39,BAD39,EXT0,EXT1)
from test_m19_s2f_clip_kernel_gate_a import raster
CODE,STOP,EXEC,GFX,STACK,SOURCE=0x20000,0x30000,0x80000,0x90000,0xb0000,0x100000
D=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
   UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
A=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
   UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)
MASK=0xffffffff

class Machine:
    def __init__(self,code,payload,version=40):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x800000)
        self.u.mem_write(CODE,code)
        self.u.mem_write(4,pack('>I',EXEC))
        self.u.mem_write(GFX+16,pack('>HHH',1100,34,version))
        self.u.mem_write(SOURCE,payload)
        self.payload=payload;self.source_live=True;self.version=version
        for a in (EXEC-534,EXEC-684,EXEC-690,GFX-390,GFX-1020,GFX-1032):
            self.u.mem_write(a,b'\x4e\x75')
        self.alloc={};self.sealed=set();self.live=set()
        self.cursor=0x200000;self.events=[];self.mode='ok'
        self.fail_alloc=False;self.calls=0;self.expected=None
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def reg(self,r):return self.u.reg_read(r)
    def volatile(self,v):
        for r,n in ((D[0],v),(D[1],0xdead0001),(A[0],0xdead0002),(A[1],0xdead0003)):
            self.u.reg_write(r,n)
    def span(self,p,n=1):
        return (self.source_live and SOURCE<=p and p+n<=SOURCE+len(self.payload)
                or any(q<=p and p+n<=q+size for q,size in self.alloc.items()))
    def on_write(self,u,access,a,n,value,user):
        if STACK-8192<=a and a+n<=STACK+4:return
        if any(q not in self.sealed and q<=a and a+n<=q+size for q,size in self.alloc.items()):
            return
        assert att39_write(self,a,n,value),('unexpected write',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==EXEC-534:
            p=self.reg(A[1])
            flag=att39_type(self,p)
            self.volatile(flag if flag is not None else int(self.span(p)))
        elif a==EXEC-684:
            n=self.reg(D[0]);flags=self.reg(D[1])
            assert 1<=n<=8276 and flags==1
            self.events.append(('AllocVec',n))
            if self.fail_alloc:
                self.fail_alloc=False;self.volatile(0);return
            p=self.cursor;self.cursor+=0x3000
            assert p+n<0x800000
            self.alloc[p]=n
            self.u.mem_write(p-8,b'\x91'*8+b'\xcd'*n+b'\x19'*8)
            self.volatile(p)
        elif a==EXEC-690:
            p=self.reg(A[1]);assert p in self.alloc
            n=self.alloc.pop(p)
            assert self.read(p-8,8)==b'\x91'*8 and self.read(p+n,8)==b'\x19'*8
            self.events.append(('FreeVec',n))
            self.sealed.discard(p)
            self.u.mem_write(p,b'\xde'*n)
            self.volatile(0)
        elif a==GFX-390:
            w,h,depth,_=self.expected
            assert tuple(self.reg(r) for r in D[:3])==(depth,w,h)
            self.bm=self.reg(A[0])
            assert STACK-8192<=self.bm<STACK
            self.events.append('InitBitMap')
            stride=w//8+(2 if self.mode=='bad_stride' else 0)
            self.u.mem_write(self.bm,pack('>HHBBH',stride,h,0,depth,0))
            self.volatile(0)
        elif a==GFX-1020:
            w,h,depth,planes=self.expected
            assert self.reg(A[2])==self.bm
            tag=self.reg(A[1]);assert STACK-8192<=tag<=STACK-24
            attached=self.calls==1
            assert unpack_from('>6I',self.read(tag,24))==(
                (0x81000000,w,0x81000008,1,0,0) if attached else (0x81000000,w,0,0,0,0))
            stride,rows,flags,bd,pad,*ptrs=unpack_from('>HHBBH8I',self.read(self.bm,40))
            assert (stride,rows,bd)==(w//8,h,depth)
            n=stride*rows
            assert all(p==0 for p in ptrs[depth:])
            for i,p in enumerate(ptrs[:depth]):
                assert self.span(p,n) and self.read(p,n)==planes[i],('plane',i,w,h)
                if i:assert p==ptrs[i-1]+n
            assert not attached or depth==4
            self.events.append('AllocOdd' if attached else 'AllocEven');self.calls+=1
            if self.mode==('oom2' if attached else 'oom1'):
                self.volatile(0);return
            out=EXT1 if attached else EXT0
            assert out not in self.live;self.live.add(out)
            if attached and self.version==39:mock_attach39(self,w,h)
            self.volatile(out)
        elif a==GFX-1032:
            p=self.reg(A[2]);assert p in self.live
            self.live.remove(p);self.events.append('FreeDetached');self.volatile(0)
    def call(self,entry,pointer,args,gfx=GFX):
        self.events=[];self.calls=0
        if hasattr(self,'att39_raw'):del self.att39_raw
        for i,r in enumerate(D+A):self.u.reg_write(r,0x55000000+i)
        self.u.reg_write(A[0],pointer);self.u.reg_write(A[6],gfx)
        for r,n in zip(D,args):self.u.reg_write(r,n&MASK)
        preserved=(D[1:] if entry in (8,12) else D[2:])+A
        saved={r:self.reg(r) for r in preserved}
        self.u.reg_write(UC_M68K_REG_SR,0x2000)
        self.u.reg_write(UC_M68K_REG_A7,STACK)
        self.u.mem_write(STACK,pack('>I',STOP))
        self.u.emu_start(CODE+entry,STOP,count=30_000_000)
        assert self.reg(UC_M68K_REG_PC)==STOP and self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items()),'register ABI'
        if self.source_live:assert self.read(SOURCE,len(self.payload))==self.payload
        for q,n in self.alloc.items():
            assert self.read(q-8,8)==b'\x91'*8 and self.read(q+n,8)==b'\x19'*8
        if hasattr(self,'att39_raw'):assert_attach39(self)
        return self.reg(D[0]),self.reg(D[1])
    def create(self,ident=17):
        im=parse_payload(self.payload).image(ident)
        p,n=self.call(0,SOURCE,(len(self.payload),ident))
        expected=pack('>8I2H',0x53324643,84+len(im.planes),im.width,im.height,im.depth,
            ident,parse_payload(self.payload).generation,(im.hotspot_x&65535)<<16|(im.hotspot_y&65535),
            im.opaque_count,im.source_transparent_pen)+im.palette+im.planes
        assert n==len(expected) and self.alloc=={p:n}
        assert self.read(p,n)==expected
        self.sealed.add(p);self.cached=expected;self.im=im
        return p,n
    def erase(self):
        self.u.mem_write(SOURCE,b'\xe7'*len(self.payload));self.source_live=False
    def render(self,p,n,dx,dy,blank=False,mode='ok',fail_alloc=False,success=True):
        im=self.im;self.mode=mode;self.fail_alloc=fail_alloc
        raw=[plane(im,i) for i in range(im.depth)]
        planes=[bytes(len(x)) if blank else raster(x,im.width,im.height,dx,dy) for x in raw]
        self.expected=(im.width,im.height,im.depth,planes)
        got=self.call(4,p,(n,dx,dy,int(blank)))
        expected=(EXT0,EXT1 if im.depth==4 else 0) if success else (0,0)
        assert got==expected,(dx,dy,blank,mode,got,self.events)
        assert self.alloc=={p:n} and self.read(p,n)==self.cached
        if success:
            assert self.live==({EXT0,EXT1} if im.depth==4 else {EXT0})
            # Test harness acts as detached caller, not DMA retirement.
            self.live.clear()
        else:assert not self.live
        uses_scratch=blank or dx!=0 or dy!=0
        allocs=[e for e in self.events if isinstance(e,tuple)]
        if uses_scratch:
            assert allocs==[('AllocVec',len(im.planes))]+([] if fail_alloc else [('FreeVec',len(im.planes))])
        else:assert not allocs
        self.mode='ok'

def cases(code):
    count=0
    for w,h,colors,version in product((16,32,64),(1,7,256),(0,3,15),(39,40)):
        payload=set_hotspot(make(w,h,colors),17,-3,8)
        m=Machine(code,payload,version);p,n=m.create()
        assert m.call(12,p,(n,))[0]==1
        m.erase()
        for dx,dy,blank in ((0,0,False),(1-w,0,False),(w-1,0,False),
                            (-3,1-h,False),(3,h-1,False),(0,0,True),(0,0,False)):
            m.render(p,n,dx,dy,blank);count+=1
        assert m.call(8,p,(n,))[0]==1 and not m.alloc
        assert m.call(12,p,(n,))[0]==0 and not m.alloc
    print('S2F_CACHE_RENDER_PASS',count,flush=True)
    negative=0
    for w,version in product((16,32,64),(39,40)):
        m=Machine(code,make(w,7,15),version);p,n=m.create();m.erase()
        for mode,dx,fail in (('oom1',-3,False),('oom2',3,False),('bad_stride',0,False),
                            ('ok',-1,True),('oom1',0,False)):
            m.render(p,n,dx,0,mode=mode,fail_alloc=fail,success=False);negative+=1
        if version==39:
            for mode in BAD39:
                m.render(p,n,-3,1,mode=mode,success=False);negative+=1
        for dx,dy,flag in ((-w,0,0),(w,0,0),(0,-7,0),(0,7,0),(1,0,1),(0,0,2),
                           (-2**31,0,0),(0,2**31-1,0)):
            assert m.call(4,p,(n,dx,dy,flag))==(0,0)
            assert not m.events and not m.live and m.alloc=={p:n};negative+=1
        for ptr,size in ((0,n),(p+1,n),(p,n-2),(p,n+2),(0xfffffff0,n)):
            assert m.call(4,ptr,(size,0,0,0))==(0,0)
            assert not m.events and not m.live and m.alloc=={p:n};negative+=1
        # Corrupt private header must fail closed without freeing it.
        for offset in (0,4,8,12,16,20,24,32):
            before=m.read(p,n)
            m.u.mem_write(p+offset,b'\xff'*4 if offset!=24 else bytes(4))
            assert m.call(12,p,(n,))[0]==0
            assert m.call(8,p,(n,))[0]==0
            assert m.alloc=={p:n} and not m.events
            m.u.mem_write(p,before);negative+=1
        assert m.call(8,p,(n,))[0]==1 and not m.alloc
    payload=make(32,7,15)
    for pointer,length,ident in ((SOURCE,len(payload),0),(SOURCE,len(payload),1),
        (SOURCE,len(payload),4097),(SOURCE,len(payload)-2,17),(SOURCE+1,len(payload),17),
        (0,len(payload),17),(0xfffffff0,len(payload),17),(SOURCE,30,17)):
        m=Machine(code,payload)
        assert m.call(0,pointer,(length,ident))==(0,0) and not m.alloc and not m.events
        negative+=1
    m=Machine(code,payload);m.fail_alloc=True
    assert m.call(0,SOURCE,(len(payload),17))==(0,0) and not m.alloc
    negative+=1
    for offset in (0,5,10,20,32+8,32+12):
        data=bytearray(payload);data[offset]^=1
        m=Machine(code,bytes(data))
        assert m.call(0,SOURCE,(len(data),17))==(0,0) and not m.alloc and not m.events
        negative+=1
    print('S2F_CACHE_REFUSALS_PASS',negative,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',required=True,type=Path)
    code=p.parse_args().binary.read_bytes()
    cases(code)
    print('S2F_CACHE_GATE_A_PASS',len(code),sha256(code).hexdigest(),flush=True)
