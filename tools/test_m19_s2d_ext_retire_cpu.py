#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2c3 exact retirement receipts and FreeSpriteData ABI, modeled OS only."""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2d_ext_frame_cpu import Machine as FrameMachine
from test_m19_s2d_ext_frame_cpu import (
    CODE,STOP,EXEC,GFX,STACK,REGS,REC,VIEW,VP,CI,TAB,LOF,SHF,
    B0,B1,F0,F1,N0,N1,P2,Q0,NEUTRAL)

class Machine(FrameMachine):
    def __init__(self,code,**kw):
        super().__init__(code,**kw)
        self.u.mem_write(GFX-414,b'\x4e\x75')
        self.u.mem_write(GFX-1032,b'\x4e\x75')
        self.u.mem_write(GFX+448,bytes([3]))
        self.held={self.ch,self.ch+1}
        self.foreign={0,1}
        self.live_alloc={B0,B1,F0,N0}|({F1,N1} if self.k==4 else set())
        self.r_fault=None
        self.releases=[]
        self.freed=[]
    def sync(self):
        self.u.mem_write(GFX+166,bytes([sum(1<<c for c in self.held|self.foreign)]))
    def partial(self,state,foreign_odd=False):
        self.put(REC+24,state)
        self.held=({self.ch} if state==5 else set())
        if foreign_odd:self.foreign.add(self.ch+1)
        self.sync()
        if foreign_odd:
            self.put(TAB+4*(self.ch+1),0x151000)
            self.copper_set(self.ch+1,0x155000)
    def on_write(self,u,access,a,n,value,user):
        assert (STACK-4096<=a and a+n<=STACK+4 or
                REC+4<=a and a+n<=REC+12 or
                REC+24<=a and a+n<=REC+28 or
                REC+52<=a and a+n<=REC+60 or
                REC+72<=a and a+n<=REC+88),('native write outside receipt/stack',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==GFX-414:
            c=self.reg(UC_M68K_REG_D0)
            assert c in self.held and not c in self.foreign
            assert not self.state()&(1<<(c-self.ch))
            assert self.get(REC+84)&0x80000000
            self.held.remove(c);self.sync()
            self.releases.append(c);self.events.append(('FreeSprite',c))
            self.put(TAB+4*c,0)
            self.copper_set(c,NEUTRAL)
            if not self.held:
                self.u.mem_write(GFX+444,pack('>H',1))
            if self.r_fault==('release',c):
                self.put(TAB+4*c,0x151000)
            self.volatile();return
        if a==GFX-270 and self.state()==4:
            assert not self.held
            self.events.append(('RetireWait',))
            if self.r_fault==('wait',self.events.count(('RetireWait',))):
                self.put(GFX+50,LOF+4)
            self.volatile();return
        if a==GFX-1032:
            p=self.reg(UC_M68K_REG_A2)
            assert self.state()==32 and not self.held
            assert p in self.live_alloc
            assert p not in (self.get(REC+i) for i in (4,8,52,56,72,76))
            for c in range(8):
                assert self.get(TAB+4*c)!=p
                start,ht,_,_=self.descs[p]
                assert not start<=self.copper(c)<start+(ht+2)*self.w//4
            self.live_alloc.remove(p);self.freed.append(p)
            self.events.append(('FreeData',p));self.volatile();return
        super().on_code(u,a,size,user)
    def call(self,entry,x=0,y=0):
        if entry<12:return super().call(entry,x,y)
        u=self.u;u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55002000+i)
        u.reg_write(UC_M68K_REG_A0,REC);u.reg_write(UC_M68K_REG_A6,GFX)
        saved={r:self.reg(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,x&0xffffffff);u.reg_write(UC_M68K_REG_D1,y&0xffffffff)
        u.reg_write(UC_M68K_REG_A7,STACK);self.put(STACK,STOP)
        before=self.read(REC,96)
        peers=[(i,self.get(TAB+4*i),self.copper(i)) for i in range(8) if i not in self.held and i not in (self.ch,self.ch+1)]
        u.emu_start(CODE+entry,STOP,count=400000)
        assert self.reg(UC_M68K_REG_PC)==STOP and self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items())
        after=self.read(REC,96)
        assert all(after[i]==before[i] for i in range(96)
                   if not (4<=i<12 or 24<=i<28 or 52<=i<60 or 72<=i<88))
        assert all(self.get(TAB+4*i)==p and self.copper(i)==c for i,p,c in peers)
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)
    def finish(self,private=False):
        assert self.call(12)==(2 if private else 1,0)
        assert self.state()==(0 if private else 20)
        assert not self.held
        assert self.events.count(('RetireWait',))==(0 if private else 2)
        before=list(self.events)
        assert self.call(12)==(2 if private else 1,0) and self.events==before
        count=len(self.live_alloc)
        assert self.call(16)==(1,0) and self.state()==32
        assert len(self.freed)==count and not self.live_alloc
        assert all(self.get(REC+i)==0 for i in (4,8,52,56,72,76,80))
        assert self.call(12)==(0,1) and self.call(16)==(0,1)
        assert len(self.freed)==count

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes();n=0
    for w in (16,32,64):
        for k in (2,4):
            for ch in (2,4,6):
                for h in (1,256):
                    for scenario in ('private','get0','get1','got','shown','exchange','uncertain','no_stage'):
                        m=Machine(code,w=w,k=k,h=h,ch=ch)
                        if scenario=='private':
                            m.partial(0)
                        elif scenario=='get0':
                            m.partial(4,True)
                        elif scenario=='get1':
                            m.partial(5,True)
                        elif scenario in ('shown','exchange','uncertain','no_stage'):
                            m.show()
                            if scenario=='no_stage':
                                for off in (72,76):
                                    ptr=m.get(REC+off)
                                    if ptr:m.live_alloc.remove(ptr)
                                    m.put(REC+off,0)
                                m.put(REC+80,0)
                            if scenario=='exchange':
                                assert m.call(8)==(1,0)
                            if scenario=='uncertain':
                                m.fault=(4,'fail')
                                assert m.call(8)==(0,2) and m.state()==15
                                m.fault=None
                            m.events.clear()
                        initial=list(sorted(m.held,reverse=True))
                        peer=(m.get(TAB+4*(ch+1)),m.copper(ch+1)) if ch+1 in m.foreign else None
                        m.finish(scenario=='private')
                        assert m.releases==initial
                        if peer:assert peer==(m.get(TAB+4*(ch+1)),m.copper(ch+1))
                        n+=1
    for w in (16,32,64):
        for ch in (2,4,6):
            m=Machine(code,w=w,k=4,ch=ch,version=39);m.show()
            assert m.call(8)==(1,0)
            m.events.clear();m.finish();assert m.releases==[ch+1,ch];n+=1
    for k in (2,4):
        for fail_odd in (False,True):
            m=Machine(code,k=k);m.show()
            ch=m.ch+int(fail_odd);m.r_fault=('release',ch)
            assert m.call(12)==(0,2) and m.state()==(5 if fail_odd else 4)
            assert m.call(16)==(0,1) and not m.freed
            m.put(TAB+4*ch,0);m.r_fault=None;m.events.clear()
            m.finish();assert m.releases==[m.ch+1,m.ch];n+=1
        for step in (1,2):
            m=Machine(code,k=k);m.show();m.r_fault=('wait',step)
            assert m.call(12)==(0,2) and m.state()==4
            assert m.call(16)==(0,1) and not m.freed
            m.put(GFX+50,LOF);m.r_fault=None;m.events.clear()
            m.finish();assert m.releases==[m.ch+1,m.ch];n+=1
        for off,val in ((24,0x80000005),(84,1),(84,0x80000002),(4,0),(8,B0),(72,F0)):
            m=Machine(code,k=k);m.show();m.put(REC+off,val)
            assert m.call(12)==(0,1) and not m.releases and not m.freed;n+=1
        m=Machine(code,k=k);m.show();m.put(TAB+4*m.ch,0x151000)
        assert m.call(12)==(0,2) and not m.releases;n+=1
        m=Machine(code,k=k);m.show();m.put(TAB+4*6,F0)
        assert m.call(12)==(0,2) and m.state()==4 and len(m.releases)==2
        m.put(TAB+4*6,0);m.events.clear();m.finish();n+=1
        m=Machine(code,k=k);m.show()
        assert m.call(12)==(1,0)
        m.copper_set(6,P2+2)
        assert m.call(16)==(0,2) and not m.freed
        m.copper_set(6,NEUTRAL);assert m.call(16)==(1,0);n+=1
        m=Machine(code,k=k);m.show();m.put(GFX+34,0)
        # Old View is not used by FreeSprite. Current list starts still mapped.
        m.finish();n+=1
    print('S2D_P2C3_EXT_RETIRE_CPU_PASS',n,'scenarios',sha256(code).hexdigest(),flush=True)
if __name__=='__main__':main()
