#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2b private v4 registry, exact MC68020 code and modeled Exec/Gfx."""
import argparse
from itertools import permutations
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2b_retire_pair_cpu import Machine, CODE, STOP, STACK, EXEC, GFX, CI, TABLE, BLANK, REGS

ANCHOR=0x180000
ROOT=ANCHOR+56
TASK=0x170000
OWNER,STATE,SCREEN,CM=0x150000,0x150100,0x150200,0x160000
VP=SCREEN+44
NAME=b'AMOSPro.AGA.AGSP.S1.root.v1\0'
RGB=bytes.fromhex('ff462824dc751a73ff')
PAIRS=(2,4,6)

def slot(n):return ROOT+52+44*((n-2)//2)
def s32(x):return x if x<0x80000000 else x-0x100000000

class RegistryMachine(Machine):
    def __init__(self,code):
        super().__init__(code)
        self.named=0
        self.root_alloc=False
        self.depth=0
        self.task=TASK
        self.fail_alloc=False
        self.fail_lock=False
        self.chips={}
        self.next_chip=0x110000
        self.published={}
        self.retired={}
        self.gets=[]
        self.freed=[]
        self.reject=None
        self.bad_return=None
        self.bad_num=None
        self.foreign_odd=False
        self.palette={21:RGB,25:RGB,29:RGB}
        self.mode=True
        self.w8(CM+18,1)
        for base,offsets in ((EXEC,(132,138,294,594,576,570,600,606,684,690)),
                             (GFX,(408,708,900))):
            for off in offsets:self.u.mem_write(base-off,b'\x4e\x75')
    def watch(self,u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:return
        assert self.root_alloc and ANCHOR<=address and address+size<=ANCHOR+240,(
            'native write outside registry/stack',hex(address),size)
    def os(self,u,address,size,user):
        d0=u.reg_read(UC_M68K_REG_D0)
        d1=u.reg_read(UC_M68K_REG_D1)
        a0=u.reg_read(UC_M68K_REG_A0)
        a1=u.reg_read(UC_M68K_REG_A1)
        result=0
        if address==EXEC-534:
            result=int(0<a1<0x200000 and a1 not in self.unmapped)
            if result and any(p<=a1<p+n for p,n in self.chips.items()):result=3
        elif address==EXEC-132:
            assert self.depth==0
            self.depth=1
        elif address==EXEC-138:
            assert self.depth==1
            self.depth=0
        elif address==EXEC-294:
            assert a1==0
            result=self.task
        elif address==EXEC-594:
            assert self.depth==1 and self.read(a1,len(NAME))==NAME
            result=self.named
        elif address==EXEC-684:
            assert self.depth==0 and d0==240 and d1==0x10001
            if not self.fail_alloc:
                assert not self.root_alloc
                self.root_alloc=True
                self.u.mem_write(ANCHOR,bytes(240))
                result=ANCHOR
        elif address==EXEC-600:
            assert self.depth==1 and a1==ANCHOR and not self.named
            assert self.read(self.u32(a1+10),len(NAME))==NAME
            assert self.u32(a1+52)==0x000400f0
            self.named=a1
            self.w8(a1+8,15);self.w16(a1+14,0);self.w32(a1+40,0);self.w16(a1+44,65535)
        elif address==EXEC-576:
            assert self.depth==1 and a0==self.named and not self.u32(a0+40)
            if not self.fail_lock:
                self.w32(a0+40,self.task);self.w16(a0+14,1);self.w16(a0+44,0)
                result=1
        elif address==EXEC-606:
            assert self.depth==1 and a1==self.named and self.u32(a1+40)==self.task
            assert self.read(ROOT,16)==bytes(16) and self.u32(ROOT+48)==0
            assert self.read(ROOT+52,132)==bytes(132)
            self.named=0
        elif address==EXEC-570:
            assert self.depth==1 and self.u32(a0+40)==self.task and not self.u32(a0+72)
            self.w32(a0+40,0);self.w16(a0+14,0);self.w16(a0+44,65535)
        elif address==EXEC-690:
            assert self.depth==0
            if a1==ANCHOR:
                assert self.root_alloc and not self.named and not self.u32(a1+40)
                self.root_alloc=False
            else:
                assert a1 in self.chips,'nonowned or duplicate FreeVec'
                assert all(self.u32(slot(n))!=a1 for n in PAIRS),'receipt not cleared before free'
                if a1 in self.published:
                    n=self.published[a1]
                    assert self.waits-self.retired[a1]>=2
                    for ch in (n,n+1):
                        assert self.u32(TABLE+4*ch)==0
                        assert self.u32(CI+88+8*ch)&65535==BLANK>>16
                        assert self.u16(CI+94+8*ch)==BLANK&65535
                    assert not self.u8(GFX+166)&(3<<n)
                    del self.published[a1]
                self.freed.append(a1)
                del self.chips[a1]
        elif address==GFX-408:
            assert self.depth==0 and d0 in (2,3,4,5,6,7)
            assert self.u32(ANCHOR+72)==self.task
            self.gets.append(d0)
            if self.foreign_odd and d0==self.reject:
                self.w8(GFX+166,self.u8(GFX+166)|(1<<d0))
                self.w32(TABLE+4*d0,0x140000)
                self.pointer(d0,0x140100)
            if self.reject==d0 or self.u8(GFX+166)&(1<<d0):
                result=0xffffffff
                self.w16(a0+10,65535)
            elif self.bad_return==d0:
                result=1
                self.w16(a0+10,1)
            else:
                result=d0
                self.w8(GFX+166,self.u8(GFX+166)|(1<<d0))
                self.w16(a0+10,1 if self.bad_num==d0 else d0)
        elif address==GFX-414:
            n=d0&65535
            assert self.depth==0 and n in (2,3,4,5,6,7)
            rec=slot(n&~1)
            flags=self.u32(rec+12)
            assert self.u32(rec+28) and flags&(1<<(n&1))
            assert self.u8(GFX+166)&(1<<n),'duplicate/foreign release'
            self.frees.append(n)
            self.w8(GFX+166,self.u8(GFX+166)&~(1<<n))
            self.w32(TABLE+4*n,0)
            if n!=self.stale:self.pointer(n,BLANK)
            if not n&1:
                chip=self.u32(rec)
                self.retired[chip]=self.waits
        elif address==GFX-270:
            assert self.depth==0
            self.waits+=1
            if self.mutate_wait:
                fn=self.mutate_wait
                self.mutate_wait=None
                fn(self)
        elif address==GFX-708:
            assert a0==CM
            tags=(0x80000028,0x80000029,0x80000032,0x80000034)
            for i,(tag,val) in enumerate(zip(tags,(16,16,255,4 if self.mode else 8))):
                assert self.u32(a1+8*i)==tag
                self.w32(a1+8*i+4,val)
            assert self.read(a1+32,8)==bytes(8)
        elif address==GFX-900:
            assert a0==CM and d0 in (21,25,29) and d1==3
            for i,v in enumerate(self.palette[d0]):
                self.w32(a1+4*i,v*0x01010101)
        else:
            return
        self.volatile(result)

    def invoke(self,off,d0=0,d1=0,d2=0,d3=0,d4=0,a0=ROOT,a1=GFX,a2=0):
        self.u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,reg in enumerate(REGS):self.u.reg_write(reg,0x55000000+i)
        for reg,v in ((UC_M68K_REG_D0,d0),(UC_M68K_REG_D1,d1),(UC_M68K_REG_D2,d2),
                      (UC_M68K_REG_D3,d3),(UC_M68K_REG_D4,d4),
                      (UC_M68K_REG_A0,a0),(UC_M68K_REG_A1,a1),(UC_M68K_REG_A2,a2)):
            self.u.reg_write(reg,v&0xffffffff)
        saved={reg:self.u.reg_read(reg) for reg in REGS}
        self.u.reg_write(UC_M68K_REG_A7,STACK)
        self.w32(STACK,STOP)
        self.u.emu_start(CODE+off,STOP,count=200000)
        assert self.u.reg_read(UC_M68K_REG_PC)==STOP
        assert self.u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(self.u.reg_read(reg)==v for reg,v in saved.items())
        assert self.depth==0
        return tuple(s32(self.u.reg_read(reg)) for reg in (UC_M68K_REG_D0,UC_M68K_REG_D1))
    def enter(self,create=1):return self.invoke(0,d0=create)
    def leave(self):return self.invoke(4)
    def scan(self,ident=0):return self.invoke(8,d0=ident)
    def pick(self,ident,mask=7,reserved=None):
        return self.invoke(12,d0=ident,d1=mask,d2=self.u8(GFX+166) if reserved is None else reserved)
    def insert(self,n,ident,bank=29,chip=None,img=3):
        if chip is None:chip=self.prepare(img)
        return self.invoke(16,d0=ident,d1=bank,d2=img,d3=n,d4=VP,a1=chip)
    def acquire(self,n):return self.invoke(20,a0=slot(n))
    def drain(self,mode,arg=0):return self.invoke(24,d0=mode,d1=arg)
    def mask(self,chip):return self.invoke(28,a0=chip,a1=CM,a2=GFX)
    def owner(self):
        assert self.u32(ROOT)==0
        for off,value in ((4,OWNER),(8,STATE),(12,SCREEN),(48,self.task)):
            self.w32(ROOT+off,value)
    def prepare(self,img=3,height=16):
        p=self.next_chip
        self.next_chip+=0x1000
        frame=8+4*height
        n=48+2*frame
        self.chips[p]=n
        self.u.mem_write(p,bytes(n))
        self.w16(p+4,height);self.w16(p+10,65535)
        self.w32(p+12,n);self.w16(p+16,img);self.w16(p+18,3)
        self.w32(p+20,1)
        self.u.mem_write(p+31,RGB)
        self.w32(p+40,48);self.w32(p+44,48+frame)
        return p
    def publish(self,n,alternate=False):
        rec=slot(n)
        assert self.u32(rec+12)==7
        chip=self.u32(rec)
        assert self.u16(chip+10)==n
        self.w32(rec+12,15)
        ptr=chip+(self.u32(chip+44) if alternate else 48)
        self.w32(chip,ptr)
        self.w32(TABLE+4*n,chip)
        self.pointer(n,ptr)
        self.published[chip]=n
        return chip
    def add(self,n,ident,bank=29,alternate=False):
        assert self.insert(n,ident,bank)==(slot(n),0)
        assert self.acquire(n)==(1,0)
        return self.publish(n,alternate)
    def closed(self):
        self.w32(ROOT+12,0)
        self.w32(ROOT+48,0)
    def neutral(self,n):
        for ch in (n,n+1):
            self.pointer(ch,BLANK)
            self.w32(TABLE+4*ch,0)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    cases=0
    def fresh(owner=True):
        m=RegistryMachine(code)
        assert m.enter()==(ROOT,0)
        assert m.u32(ANCHOR+52)==0x000400f0 and m.scan()==(0,7)
        if owner:m.owner()
        return m
    m=RegistryMachine(code)
    assert m.enter(0)==(0,1)
    m.fail_alloc=True;assert m.enter()==(0,4);m.fail_alloc=False
    assert m.enter()==(ROOT,0);assert m.enter()==(0,6)
    assert m.leave()==(1,0) and not m.root_alloc
    cases+=5
    m=fresh(False)
    # Same name, old or unknown schema remains locked out after release.
    m.owner()
    assert m.leave()==(1,0) and m.named==ANCHOR
    m.w32(ANCHOR+52,0x00030070)
    assert m.enter()==(0,3);m.w32(ANCHOR+52,0x000400f0)
    m.fail_lock=True;assert m.enter()==(0,2);m.fail_lock=False
    assert m.enter()==(ROOT,0)
    m.task=TASK+4;assert m.leave()==(0,2);m.task=TASK
    assert m.leave()==(1,0)
    cases+=5
    m=fresh()
    for mask in range(8):
        for reserved in range(256):
            chosen=next((n for i,n in enumerate(PAIRS)
                         if mask&(1<<i) and not reserved&(3<<n)),None)
            assert m.pick(1,mask,reserved)==((slot(chosen),chosen) if chosen else (0,-2))
            cases+=1
    assert m.pick(0)==(0,-1) and m.pick(65)==(0,-1)
    chip=m.prepare()
    for mask in range(8):
        m.palette={pen:RGB if mask&(1<<i) else bytes(9) for i,pen in enumerate((21,25,29))}
        assert m.mask(chip)==(mask,1);cases+=1
    m.mode=False;assert m.mask(chip)==(0,0);m.mode=True
    m.w8(CM+18,0);assert m.mask(chip)==(0,0);m.w8(CM+18,1);cases+=2
    for order in permutations(PAIRS):
        m=fresh()
        for n in order:
            assert m.pick(n,1<<((n-2)//2))==(slot(n),n)
            m.add(n,n,29 if n!=4 else 30,alternate=bool(n&4))
        assert m.scan()==(0,0) and m.pick(64)==(0,-2)
        for n in PAIRS:assert m.scan(n)==(slot(n),0)
        assert m.pick(2)==(0,-1)
        # All receipts stay pinned during the preclose pass.
        assert m.drain(0)==(1,0)
        assert m.u32(ROOT)==3 and not m.freed
        assert all(m.u32(slot(n)+12)==20 for n in PAIRS)
        assert m.leave()==(1,0) # simulated CloseScreen refusal
        assert m.enter()==(ROOT,0)
        assert m.drain(0)==(1,0)
        m.closed()
        assert m.drain(1)==(1,0) and len(m.freed)==3
        assert m.scan()==(0,7) and m.leave()==(1,0) and not m.root_alloc
        assert m.u8(GFX+166)==3 and not m.chips
        cases+=12
    # Off middle, reuse its logical ID or pair, then free only one bank.
    m=fresh();p2=m.add(2,11);p4=m.add(4,22,30);p6=m.add(6,33)
    peers=[(n,m.read(slot(n),44),m.slot(n),m.slot(n+1)) for n in (2,6)]
    assert m.drain(2,22)==(1,0) and m.freed==[p4]
    assert all(m.read(slot(n),44)==r and m.slot(n)==e and m.slot(n+1)==o for n,r,e,o in peers)
    assert m.drain(2,22)==(1,0)
    assert m.pick(64)==(slot(4),4)
    p4b=m.add(4,64,30,True)
    assert m.drain(3,29)==(1,0)
    assert set(m.freed)=={p2,p4,p6}
    assert m.u32(slot(4))==p4b and m.u32(ROOT)==1
    assert m.drain(3,30)==(1,0) and m.leave()==(1,0) and not m.root_alloc
    cases+=7
    for n in PAIRS:
        for reject in (n,n+1):
            m=fresh();m.insert(n,n)
            m.reject=reject;m.foreign_odd=reject==n+1
            assert m.acquire(n)==(0,-141 if reject==n else -142)
            assert m.u32(slot(n)+12)==(0 if reject==n else 20)
            assert m.frees==([] if reject==n else [n])
            odd=m.slot(n+1)
            assert m.drain(2,n)==(1,0)
            assert m.slot(n+1)==odd and m.leave()==(1,0)
            cases+=1
        for bad in ('return','num'):
            m=fresh();m.insert(n,n)
            if bad=='return':m.bad_return=n
            else:m.bad_num=n+1
            assert m.acquire(n)==(0,-143)
            assert m.u32(slot(n)+12)&0x80000000
            assert m.pick(64)==(0,-3)
            assert m.drain(0)==(0,0) and not m.freed
            assert m.leave()==(1,0) and m.root_alloc
            cases+=1
    # Pending late reference after retiring one pair must not lose other receipts.
    m=fresh();a=m.add(2,11);b=m.add(4,22,30);c=m.add(6,33)
    m.stale=4
    assert m.drain(0)==(1,0)
    assert [m.u32(slot(n)+12) for n in PAIRS]==[20,4,20]
    assert not m.freed
    m.closed()
    assert m.drain(1)==(0,0)
    assert set(m.freed)=={a,c} and m.u32(ROOT)==1 and m.u32(slot(4))==b
    assert m.leave()==(1,0) and m.named
    assert m.enter()==(ROOT,0)
    assert m.drain(4,29)==(1,0) and m.u32(ROOT)==1
    m.stale=None;m.neutral(4)
    assert m.drain(4,30)==(1,0) and m.freed[-1]==b
    assert m.leave()==(1,0) and not m.root_alloc
    cases+=6
    # One wrong VP prevents Close but preserves previously retired peers.
    m=fresh()
    for n in PAIRS:m.add(n,n)
    m.w32(slot(4)+8,VP+2)
    assert m.drain(0)==(0,0)
    assert [m.u32(slot(n)+12) for n in PAIRS]==[20,15,20] and not m.freed
    m.w32(slot(4)+8,VP)
    assert m.drain(0)==(1,0);m.closed()
    assert m.drain(1)==(1,0) and m.leave()==(1,0)
    cases+=3
    # Reject inconsistent structure before the first OS free.
    for where,value in ((ROOT,0),(ROOT,4),(slot(4)+28,2),
                        (slot(4)+40,2),(slot(4),0),
                        (slot(4),ANCHOR+8),(slot(4)+4,70),
                        (slot(4)+28,0)):
        m=fresh();m.add(2,2);m.add(4,4)
        m.w32(where,value)
        assert m.scan()==(0,-1)
        assert m.drain(0)==(0,0) and not m.frees and not m.freed
        cases+=1
    m=fresh();a=m.add(2,2);m.add(4,4)
    m.w32(slot(4),a+16)
    assert m.scan()==(0,-1) and m.drain(0)==(0,0) and not m.frees
    cases+=1
    # A stale count must not let Leave remove a nonempty semaphore.
    m=fresh(False);m.w32(slot(6)+12,4)
    assert m.scan()==(0,-1)
    assert m.leave()==(1,0) and m.root_alloc
    assert m.enter()==(ROOT,0);m.w32(slot(6)+12,0)
    assert m.leave()==(1,0) and not m.root_alloc
    cases+=2
    print('S2B_REGISTRY_CPU_PASS',cases,'cases; private registry/OS model, not AP20 or DMA')

if __name__=='__main__':main()
