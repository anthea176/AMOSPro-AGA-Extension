#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""V5 registry + actual attached lifecycle on MC68020, modeled OS.

No real DMA, no AP20 token or actual CloseScreen yet. Use one record
per pair, and both source-backed layouts under the same semaphore.
"""
import argparse
from itertools import product,permutations
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2b_registry_cpu import (
    RegistryMachine,ANCHOR,ROOT,TASK,OWNER,STATE,SCREEN,CM,VP,NAME,PAIRS,s32)
from test_m19_s2b_retire_pair_cpu import CODE,STOP,STACK,EXEC,GFX,CI,TABLE,BLANK,REGS
SIZE=324
RGB=bytes(v for i in range(1,16) for v in (i,255-i,(i*19)&255))
VIEW,LOF,SHF=0x170100,0x170200,0x170300
ENTER,LEAVE,SCAN,PICK,INSERT,ACQUIRE,DRAIN,MASK,ATT_INSERT,ATT_ACQUIRE,ATT_SHOW,ATT_MOVE,ATT_CHANGE=range(0,52,4)
def slot(n):return ROOT+52+72*((n-2)//2)

class Mixed(RegistryMachine):
    def __init__(self,code):
        super().__init__(code)
        self.w32(GFX+34,VIEW);self.w32(GFX+50,LOF);self.w32(GFX+54,SHF)
        self.w32(VIEW,VP);self.w32(VP+4,CM)
        self.w16(VP+24,320);self.w16(VP+26,256);self.w16(VP+32,0x5000)
        self.w8(CM+1,2);self.w16(CM+2,256)
        self.w32(STATE,SCREEN);self.w32(STATE+8,GFX)
        self.palette={21:RGB[12:21],25:RGB[24:33],29:RGB[36:45]}
        self.cmap=RGB
        self.current=None
        self.moves=[]
        self.gfx_freed=[]
        self.hidden=[]
        self.kinds={}
        for off in (420,426):self.u.mem_write(GFX-off,b'\x4e\x75')
    def watch(self,u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:return
        if self.root_alloc and ANCHOR<=address and address+size<=ANCHOR+SIZE:return
        for p,length in self.chips.items():
            if self.kinds.get(p)==4:
                stream=self.u32(p+88)
                if address in (p+8,p+20,p+28) and size==2:return
                if address in (p+96+stream+3,p+96+3*stream+3) and size==1:return
                if p+96<=address and address+size<=p+length and size==4:
                    # Inactive staging only; the caller owns one record.
                    active=self.u32(p)
                    if active in (p+96,p+96+2*stream):
                        spare=p+96+2*stream if active==p+96 else p+96
                        assert spare<=address and address+size<=spare+2*stream
                        assert self.waits>=2
                        return
        raise AssertionError(('native write outside v5 registry/owned attached buffer',hex(address),size))
    def os(self,u,address,size,user):
        d0=u.reg_read(UC_M68K_REG_D0);d1=u.reg_read(UC_M68K_REG_D1)
        a0=u.reg_read(UC_M68K_REG_A0);a1=u.reg_read(UC_M68K_REG_A1)
        a2=u.reg_read(UC_M68K_REG_A2)
        if address==EXEC-684:
            assert self.depth==0 and d0==SIZE and d1==0x10001
            result=0
            if not self.fail_alloc:
                assert not self.root_alloc
                self.root_alloc=True
                self.u.mem_write(ANCHOR,bytes(SIZE));result=ANCHOR
            self.volatile(result)
        elif address==EXEC-600:
            assert self.depth==1 and a1==ANCHOR and not self.named
            assert self.read(self.u32(a1+10),len(NAME))==NAME
            assert self.u32(a1+52)==0x00050144
            self.named=a1;self.w8(a1+8,15);self.w16(a1+14,0)
            self.w32(a1+40,0);self.w16(a1+44,65535);self.volatile()
        elif address==EXEC-606:
            assert self.depth==1 and a1==self.named and self.u32(a1+40)==self.task
            assert self.read(ROOT,16)==bytes(16) and self.u32(ROOT+48)==0
            assert self.read(ROOT+52,216)==bytes(216)
            self.named=0;self.volatile()
        elif address==EXEC-690:
            assert self.depth==0
            if a1==ANCHOR:
                assert self.root_alloc and not self.named and not self.u32(a1+40)
                self.root_alloc=False
            else:
                assert a1 in self.chips
                assert all(self.u32(slot(n))!=a1 for n in PAIRS)
                if a1 in self.published:
                    n=self.published.pop(a1)
                    assert self.waits-self.retired[a1]>=2
                    assert not self.u8(GFX+166)&(3<<n)
                    for ch in (n,n+1):
                        assert not self.u32(TABLE+4*ch)
                        assert self.u16(CI+90+8*ch)==BLANK>>16
                        assert self.u16(CI+94+8*ch)==BLANK&65535
                self.freed.append(a1);del self.chips[a1]
            self.volatile()
        elif address==GFX-408:
            n=d0&~1;rec=slot(n);p=self.u32(rec)
            assert self.depth==0 and self.u32(ANCHOR+72)==self.task
            assert a0==(p if not d0&1 else p+12 if self.u32(rec+44)==4 else rec+16)
            return super().os(u,address,size,user)
        elif address==GFX-414:
            n=d0&~1;rec=slot(n)
            assert self.depth==0 and self.u32(rec+12)&(1<<(d0&1))
            assert self.u8(GFX+166)&(1<<d0)
            self.gfx_freed.append(d0)
            self.w8(GFX+166,self.u8(GFX+166)&~(1<<d0))
            self.w32(TABLE+4*d0,0)
            if d0!=self.stale:self.pointer(d0,BLANK)
            if not d0&1:self.retired[self.u32(rec)]=self.waits
            self.volatile()
        elif address==GFX-900 and d0==17:
            assert a0==CM and 4<=d1<=15
            for i,v in enumerate(self.cmap[:3*d1]):self.w32(a1+4*i,v*0x01010101)
            self.volatile()
        elif address==GFX-420:
            n=self.u16(a1+10);rec=slot(n&~1);p=self.u32(rec);stream=self.u32(p+88)
            assert a0==VP and self.u32(rec+44)==4 and self.u32(rec+12)==15
            assert a1==p+12*(n&1) and self.u16(a1+8)==257
            assert a2 in (p+96+(n&1)*stream,p+96+(2+(n&1))*stream)
            self.published[p]=n&~1
            self.w32(a1,a2);self.move_model(a1,self.u16(a1+6),257)
            self.hidden.append(n);self.volatile()
        elif address==GFX-426:
            assert a0==VP and self.u16(a1+10) in PAIRS
            assert self.u32(slot(self.u16(a1+10))+12)==15
            assert self.u8(self.u32(a1+12)+3)&128
            self.move_model(a1,d0,d1);self.moves.append((d0,d1));self.volatile()
        else:return super().os(u,address,size,user)
    def move_model(self,desc,x,y):
        ch=self.u16(desc+10);p=self.u32(desc)
        self.w16(desc+6,x);self.w16(desc+8,y)
        self.w32(TABLE+4*ch,desc)
        if not ch&1:
            odd=self.u32(TABLE+4*(ch+1))
            if odd and self.u8(self.u32(odd)+3)&128:self.move_model(odd,x,y)
        h=self.u16(desc+4)
        ctl=((y+h)&255)<<8|(self.u8(p+3)&128)
        if y>=256:ctl|=4
        self.w32(p,((y&255)<<24)|((x&255)<<16)|ctl)
        self.pointer(ch,BLANK if y>256 else p)
    def call(self,off,d0=0,d1=0,d2=0,d3=0,d4=0,d5=0,a0=ROOT,a1=GFX,a2=0):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,reg in enumerate(REGS):u.reg_write(reg,0x55000000+i)
        for reg,v in ((UC_M68K_REG_D0,d0),(UC_M68K_REG_D1,d1),(UC_M68K_REG_D2,d2),
                      (UC_M68K_REG_D3,d3),(UC_M68K_REG_D4,d4),(UC_M68K_REG_D5,d5),
                      (UC_M68K_REG_A0,a0),(UC_M68K_REG_A1,a1),(UC_M68K_REG_A2,a2)):
            u.reg_write(reg,v&0xffffffff)
        saved={reg:u.reg_read(reg) for reg in REGS}
        u.reg_write(UC_M68K_REG_A7,STACK);self.w32(STACK,STOP)
        u.emu_start(CODE+off,STOP,count=1000000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(reg)==v for reg,v in saved.items())
        assert self.depth==0
        return tuple(s32(u.reg_read(reg)) for reg in (UC_M68K_REG_D0,UC_M68K_REG_D1))
    def prepare_kind(self,n,kind,ident=3,height=16):
        # Space 0x2000 between allocations even for 256-row attached block.
        p=self.next_chip;self.next_chip+=0x2000
        stream=8+4*height
        if kind==2:
            size=48+2*stream
            self.u.mem_write(p,bytes(size))
            self.w16(p+4,height);self.w16(p+10,65535)
            self.w32(p+12,size);self.w16(p+16,ident);self.w16(p+18,3)
            self.w32(p+20,2);self.u.mem_write(p+31,self.palette[17+2*n])
            self.w32(p+40,48);self.w32(p+44,48+stream)
        else:
            size=96+4*stream
            desc=pack('>I4H',0,height,0,0,65535)
            head=desc*2+pack('>I2HI2h48s2I',size,ident,15,2,0,0,bytes(3)+RGB,stream,96)
            assert len(head)==96
            data=bytes((i+ident)&255 for i in range(height*4))
            self.u.mem_write(p,head+bytes(4)+data+bytes(8)+data+bytes(4)+bytes(2*stream))
        self.chips[p]=size;self.kinds[p]=kind
        return p
    def insert_kind(self,n,kind,ident,bank=29,img=3,p=None):
        if p is None:p=self.prepare_kind(n,kind,img)
        return p,self.call(ATT_INSERT if kind==4 else INSERT,d0=ident,d1=bank,d2=img,
            d3=n,d4=VP,d5=self.chips[p],a1=p,a2=GFX)
    def show_kind(self,n,kind,ident,bank=29):
        p,result=self.insert_kind(n,kind,ident,bank)
        assert result==(slot(n),0)
        assert self.call(ATT_ACQUIRE if kind==4 else ACQUIRE,a0=slot(n))==(1,0)
        if kind==4:
            assert self.call(ATT_SHOW,d0=32+n,d1=80,a0=slot(n))==(1,0)
            assert self.u32(slot(n)+12)==31
        else:
            # Existing S2b public route will supply Change/Move; this
            # test models its already qualified publication receipt.
            self.w32(slot(n)+12,15);self.w32(p,p+48)
            self.w32(TABLE+4*n,p);self.pointer(n,p+48);self.published[p]=n
        return p
    def snapshot(self,n):
        rec=slot(n);p=self.u32(rec)
        return self.read(rec,72),self.read(p,self.chips[p]),self.slot(n),self.slot(n+1)
    def drain_kind(self,mode,arg=0):return self.call(DRAIN,d0=mode,d1=arg)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path)
    raw=p.parse_args().native.read_bytes();cases=0
    def fresh():
        m=Mixed(raw);assert m.call(ENTER,d0=1)==(ROOT,0)
        assert m.u32(ANCHOR+52)==0x00050144
        assert m.call(SCAN)==(0,7)
        m.owner()
        return m
    for kinds in product((2,4),repeat=3):
        for order in permutations(PAIRS):
            m=fresh()
            for n,kind in zip(PAIRS,kinds):
                assert m.call(PICK,d0=n+10,d1=1<<((n-2)//2),d2=m.u8(GFX+166))==(slot(n),n)
                m.show_kind(n,kind,n+10)
            assert m.call(SCAN)==(0,0)
            for n in order:
                others={k:m.snapshot(k) for k in PAIRS if k!=n and m.u32(slot(k)+28)}
                assert m.drain_kind(2,n+10)==(1,0)
                assert all(m.snapshot(k)==v for k,v in others.items())
            assert m.u32(ROOT)==0 and not m.chips and m.waits==6
            assert m.call(LEAVE)==(1,0) and not m.named and not m.root_alloc
            cases+=1
    for kinds in ((2,4,2),(4,2,4),(4,4,4)):
        m=fresh()
        for n,kind in zip(PAIRS,kinds):m.show_kind(n,kind,n+10,29 if n!=4 else 30)
        peer=m.snapshot(4)
        assert m.drain_kind(3,29)==(1,0) and m.snapshot(4)==peer
        assert m.drain_kind(0)==(1,0) and m.u32(ROOT)==1
        assert m.u32(slot(4)+12)==20 and m.chips
        m.closed()
        assert m.drain_kind(1)==(1,0) and not m.chips
        assert m.call(LEAVE)==(1,0)
        cases+=1
    for n in PAIRS:
        for kind in (2,4):
            m=fresh();m.show_kind(n,kind,n+10)
            m.stale=n+1 if kind==4 else n
            assert m.drain_kind(2,n+10)==(0,0) and m.u32(slot(n)+12)==4
            assert m.call(PICK,d0=60,d1=7,d2=m.u8(GFX+166))==(0,-3)
            # Pre-Close may preserve pending receipt; closed drain
            # refuses until the pair is corroborated neutral.
            assert m.drain_kind(0)==(1,0)
            m.closed();assert m.drain_kind(1)==(0,0)
            m.stale=None;m.neutral(n)
            assert m.drain_kind(4,29)==(1,0) and not m.chips
            assert m.gfx_freed==[n+1,n] and m.waits==2
            assert m.call(LEAVE)==(1,0)
            cases+=1
        m=fresh()
        p,result=m.insert_kind(n,4,n+10);assert result==(slot(n),0)
        m.reject=n+1;m.foreign_odd=True
        assert m.call(ATT_ACQUIRE,a0=slot(n))[0]==0
        assert m.u32(slot(n)+12)==5
        foreign=m.slot(n+1)
        assert m.drain_kind(2,n+10)==(1,0) and m.gfx_freed==[n]
        assert m.slot(n+1)==foreign and not m.chips
        assert m.call(LEAVE)==(1,0);cases+=1
        m=fresh();m.show_kind(n,4,n+10)
        m.w32(TABLE+4*(n+1),0x140000)
        assert m.drain_kind(2,n+10)==(0,0) and not m.gfx_freed
        cases+=1
        m=fresh();m.show_kind(n,4,n+10)
        scratch=m.prepare_kind(n,4,ident=9)
        assert m.call(ATT_CHANGE,a0=slot(n),a2=scratch,d0=m.chips[scratch])==(1,0)
        assert m.u32(slot(n)+36)==9
        assert m.call(ATT_MOVE,d0=100,d1=120,a0=slot(n))==(1,0)
        assert m.drain_kind(2,n+10)==(1,0)
        assert set(m.chips)=={scratch} and m.call(LEAVE)==(1,0)
        cases+=1
    for field,value in ((44,3),(48,0),(64,1),(68,1),(16,1),(40,6),(4,143)):
        m=fresh();m.show_kind(2,4,17)
        m.w32(slot(2)+field,value)
        assert m.call(SCAN)==(0,-1) and m.drain_kind(0)==(0,0)
        assert not m.gfx_freed;cases+=1
    m=fresh();m.show_kind(2,2,17);m.w32(slot(2)+48,1)
    assert m.call(SCAN)==(0,-1) and m.drain_kind(0)==(0,0);cases+=1
    # Old v4 schema is not a v5 registry. No accidental migration/free.
    m=fresh();m.call(LEAVE);assert m.named
    m.w32(ANCHOR+52,0x000400f0)
    assert m.call(ENTER,d0=1)==(0,3) and not m.gfx_freed and m.root_alloc
    cases+=1
    print('S2C_V5_MIXED_REGISTRY_PASS',cases,'scenarios; modeled OS only',flush=True)
if __name__=='__main__':main()
