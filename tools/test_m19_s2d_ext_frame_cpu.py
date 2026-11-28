#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-built P2c2 move/exchange, modeled OS, no physical DMA proof."""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2d_ext_hidden_show_cpu import Machine as ShowMachine
from test_m19_s2d_ext_hidden_show_cpu import (
    CODE,STOP,EXEC,GFX,STACK,REGS,REC,VIEW,VP,CI,TAB,
    B0,B1,F0,F1,P2,P3,NEUTRAL)

N0,N1,Q0,Q1,LOF,SHF=0x114000,0x115000,0x130000,0x134000,0x106000,0x107000

class Machine(ShowMachine):
    def __init__(self,code,**kw):
        super().__init__(code,**kw)
        self.put(GFX+50,LOF);self.put(GFX+54,SHF)
        self.u.mem_write(GFX-270,b'\x4e\x75')
        self.u.mem_write(REC+72,pack('>6I',N0,N1 if self.k==4 else 0,1,0,LOF,SHF))
        for ptr,data,att in ((N0,Q0,False),(N1,Q1,self.k==4)):
            self.descs[ptr]=(data,self.h,att,0xbeef)
            self.u.mem_write(ptr,pack('>IHHHH',data,self.h,0xdead,0xbeef,0xbeef))
            raw=bytearray((self.h+2)*self.w//4)
            if att:raw[3]=raw[self.w//8+1]=0x80
            self.u.mem_write(data,bytes(raw))
        self.fault=None
    def on_write(self,u,access,a,n,value,user):
        assert (STACK-4096<=a and a+n<=STACK+4 or
                REC+24<=a and a+n<=REC+28 or
                REC+52<=a and a+n<=REC+60 or
                REC+72<=a and a+n<=REC+84),('unexpected write',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==EXEC-534:
            super().on_code(u,a,size,user);return
        if a not in (GFX-426,GFX-1026,GFX-270):return
        assert self.state()==15
        if a==GFX-270:
            assert self.copper(self.ch)==self.copper(self.ch+1)==NEUTRAL
            self.events.append(('Wait',))
            result=0
        else:
            assert self.reg(UC_M68K_REG_A0)==VP
            old=self.reg(UC_M68K_REG_A1)
            assert old in self.descs
            if a==GFX-426:
                x,y=self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)
                self.events.append(('Move',old,x,y))
                self.model_move(old,x,y);result=0
            else:
                new=self.reg(UC_M68K_REG_A2)
                assert new in self.descs and old!=new
                assert self.read(self.reg(UC_M68K_REG_A3),8)==bytes(8)
                assert self.word(old+6)==0 and self.word(old+8)==257
                assert self.copper(self.ch)==self.copper(self.ch+1)==NEUTRAL
                self.events.append(('Change',old,new))
                if self.fault==(len(self.events),'fail'):
                    self.volatile(0);return
                self.u.mem_write(new+10,pack('>H',self.word(old+10)))
                self.model_move(new,0,257);result=0xffffffff
        if self.fault==(len(self.events),'list'):
            self.put(GFX+50,LOF+4)
        if self.fault==(len(self.events),'slot'):
            self.put(TAB+4*self.ch,0x151000)
        if self.fault==(len(self.events),'width'):
            self.u.mem_write(GFX+444,bytes(2))
        self.volatile(result)
    def call(self,entry,x=0,y=0):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55001000+i)
        u.reg_write(UC_M68K_REG_A0,REC);u.reg_write(UC_M68K_REG_A6,GFX)
        saved={r:self.reg(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,x&0xffffffff);u.reg_write(UC_M68K_REG_D1,y&0xffffffff)
        u.reg_write(UC_M68K_REG_A7,STACK);self.put(STACK,STOP)
        before=self.read(REC,96)
        peers=[(i,self.get(TAB+4*i),self.copper(i)) for i in range(8) if i not in (self.ch,self.ch+1)]
        u.emu_start(CODE+entry,STOP,count=300000)
        assert self.reg(UC_M68K_REG_PC)==STOP and self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items())
        after=self.read(REC,96)
        assert all(after[i]==before[i] for i in range(96)
                   if not (24<=i<28 or 52<=i<60 or 72<=i<84))
        assert all(self.get(TAB+4*i)==p and self.copper(i)==c for i,p,c in peers)
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)
    def show(self,x=1,y=0):
        assert self.call(0,x,y)==(1,0)
        self.events.clear()
    def refs(self):
        return tuple(self.get(REC+i) for i in (52,56,72,76,80))
    def live(self,x,y):
        e,o,_,_,_=self.refs()
        assert self.get(TAB+4*self.ch)==e and self.copper(self.ch)==self.get(e)
        assert self.word(e+6)==x and self.word(e+8)==y
        if self.k==4:
            assert self.get(TAB+4*(self.ch+1))==o
            assert self.copper(self.ch+1)==self.get(o)
            assert self.word(o+6)==x and self.word(o+8)==y
        else:
            assert self.get(TAB+4*(self.ch+1))==B1
            assert self.copper(self.ch+1)==NEUTRAL

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('native',type=Path)
    code=ap.parse_args().native.read_bytes();moves=changes=neg=0
    for w in (16,32,64):
        for k in (2,4):
            for h in (1,17,256):
                for ch in (2,4,6):
                    m=Machine(code,w=w,k=k,h=h,ch=ch);m.show()
                    for i in range(12):
                        x=i*(320-w)//11;y=i*(256-h)//11
                        assert m.call(4,x,y)==(1,0);moves+=1
                        assert m.events==[('Move',m.refs()[0],x,y)]
                        m.live(x,y);m.events.clear()
                        old=m.refs()
                        assert m.call(8)==(1,0),(w,k,h,ch,i,m.events)
                        assert m.state()==31 and m.refs()==(old[2],old[3],old[0],old[1],3)
                        assert m.events.count(('Wait',))==2
                        assert m.events[0]==('Move',old[0],0,257)
                        assert m.events[-1]==('Move',old[2],x,y)
                        m.live(x,y);m.events.clear();changes+=1
                    for x,y in ((-1,0),(0,-1),(321-w,0),(0,257-h)):
                        assert m.call(4,x,y)==(0,1) and m.state()==31 and not m.events
                        neg+=1
    for k in (2,4):
        for step in range(1,7 if k==4 else 6):
            for fault in ('list','slot','width'):
                m=Machine(code,k=k);m.show();before=m.refs()
                m.fault=(step,fault)
                assert m.call(8)==(0,2),(k,step,fault,m.events)
                assert m.state()==15 and m.refs()[:4]==before[:4] and m.refs()[4]==2
                n=len(m.events)
                assert m.call(8)==(0,1) and m.call(4)==(0,1) and len(m.events)==n
                neg+=1
        for step in range(4,6 if k==4 else 5):
            m=Machine(code,k=k);m.show();m.fault=(step,'fail')
            assert m.call(8)==(0,2) and m.state()==15 and m.refs()[4]==2;neg+=1
        for off,val in ((72,0),(72,F0),(72,B0),(80,0),(80,2),(84,1)):
            m=Machine(code,k=k);m.show();m.put(REC+off,val)
            assert m.call(8)==(0,1) and m.state()==31 and not m.events;neg+=1
        m=Machine(code,k=k);m.show();m.put(TAB+4*6,N0)
        assert m.call(8)==(0,1) and not m.events and m.state()==31;neg+=1
        m=Machine(code,k=k);m.show();m.copper_set(6,Q0+2)
        assert m.call(8)==(0,1) and not m.events and m.state()==31;neg+=1
        m=Machine(code,k=k);m.show();m.put(TAB+4*6,F0)
        assert m.call(8)==(0,2) and m.state()==15 and m.refs()[4]==2;neg+=1
        m=Machine(code,k=k);m.show();m.fault=(1,'slot')
        assert m.call(4,9,8)==(0,2) and m.state()==15;neg+=1
    print('S2D_P2C2_EXT_FRAME_CPU_PASS',moves,'moves',changes,'changes',neg,'negative',sha256(code).hexdigest(),flush=True)
if __name__=='__main__':main()
