#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2c-P0c source-assembled pair lifecycle, V40 OS model only.

Emulate relevant V40 SimpleSprite side effects: Change calls Move,
even Move recurses into attached odd, hidden VP uses neutral CopInit,
FreeSprite clears reservation/table and installs neutral pointer.
No native DMA, beam timing, OS scheduling or WinUAE assertion.
"""
import argparse
import itertools
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2b_retire_pair_cpu import Machine, CODE, STOP, EXEC, GFX, CI, TABLE, STACK, RECS, CHIPS, BLANK, REGS

VP, CM, VIEW = 0x150000, 0x160000, 0x170000
PAIRS=(2,4,6)
RGB=bytes(v for i in range(1,16) for v in (i,255-i,(i*19)&255))
SIZE=16
ACQUIRE,SHOW,MOVE,RETIRE,PALETTE=0,4,8,12,16

class AttachedMachine(Machine):
    def __init__(self,code):
        super().__init__(code)
        self.w32(GFX+34,VIEW)
        self.w32(VIEW,VP)
        self.w32(VP+4,CM)
        self.w16(VP+24,320)
        self.w16(VP+26,256)
        self.w16(VP+32,0x5000)
        self.w8(CM+1,2)
        self.w16(CM+2,256)
        self.w8(CM+18,1)
        self.rgb=RGB
        self.tags=(16,16,255,4)
        self.gets=[]
        self.moves=[]
        self.changes=[]
        self.rgb_calls=[]
        self.fail_get=None
        self.bad_get=None
        self.bad_num=None
        self.fail_change=None
        self.fail_move=None
        self.foreign_odd=False
        self.bad_palette_after_get=False
        self.mutate_after_change=None
        self.heights={}
        self.lengths={}
        for off in (408,420,426,708,900):
            self.u.mem_write(GFX-off,b'\x4e\x75')
    def record(self,n,flags=0,height=16,colors=15):
        assert flags==0
        rec,chip=RECS[n],CHIPS[n]
        stream=8+4*height
        length=96+4*stream
        self.heights[n]=height
        self.lengths[n]=length
        self.u.mem_write(rec,pack('>11I',chip,length,VP,0,GFX,CM,VIEW,CI,TABLE,0,n))
        desc=pack('>I4H',0,height,0,0,65535)
        header=desc*2+pack('>I2HI2h48s2I',length,1,colors,2,0,0,
                           bytes(3)+RGB[:3*colors]+bytes(45-3*colors),stream,96)
        assert len(header)==96
        # Mark every data row distinct; OS may only change control words.
        data0=bytes((i*7+3)&255 for i in range(4*height))
        data1=bytes((i*13+9)&255 for i in range(4*height))
        raw=header+bytes(4)+data0+bytes(8)+data1+bytes(4)+bytes(2*stream)
        assert len(raw)==length
        self.u.mem_write(chip-16,bytes([0xa5])*16)
        self.u.mem_write(chip,raw)
        self.u.mem_write(chip+length,bytes([0xc3])*16)
        return rec,chip
    def stream(self,n,odd=False):
        return CHIPS[n]+96+(8+4*self.heights[n] if odd else 0)
    def move_model(self,desc,x,y):
        ch=self.u16(desc+10)
        assert ch in (self.current,self.current+1)
        self.w16(desc+6,x)
        self.w16(desc+8,y)
        self.w32(TABLE+4*ch,desc)
        p=self.u32(desc)
        assert p==self.stream(self.current,bool(ch&1))
        # V40 calls itself on the odd descriptor only if attached.
        if not ch&1:
            odd=self.u32(TABLE+4*(ch+1))
            if odd:
                assert odd==CHIPS[self.current]+12
                op=self.u32(odd)
                if self.u8(op+3)&0x80:self.move_model(odd,x,y)
        ctl=((y+self.heights[self.current])&255)<<8 | (self.u8(p+3)&0x80)
        if y>=256:ctl|=4
        self.w32(p,((y&255)<<24)|((x&255)<<16)|ctl)
        self.pointer(ch,BLANK if y>256 else p)
    def os(self,u,address,size,user):
        d0=u.reg_read(UC_M68K_REG_D0)
        d1=u.reg_read(UC_M68K_REG_D1)
        a0=u.reg_read(UC_M68K_REG_A0)
        a1=u.reg_read(UC_M68K_REG_A1)
        a2=u.reg_read(UC_M68K_REG_A2)
        n=self.current
        if address==EXEC-534:
            result=int(0<a1<0x200000 and a1 not in self.unmapped)
            if result and any(p<=a1<p+self.lengths.get(ch,0) for ch,p in CHIPS.items()):
                result=3
            self.volatile(result)
        elif address==GFX-708:
            assert a0==CM
            for i,(tag,value) in enumerate(zip((0x80000028,0x80000029,0x80000032,0x80000034),self.tags)):
                assert self.u32(a1+8*i)==tag
                self.w32(a1+8*i+4,value)
            assert self.read(a1+32,8)==bytes(8)
            self.volatile()
        elif address==GFX-900:
            assert a0==CM and d0==17 and 4<=d1<=15
            self.rgb_calls.append((d0,d1))
            for i,v in enumerate(self.rgb[:3*d1]):self.w32(a1+4*i,v*0x01010101)
            self.volatile()
        elif address==GFX-408:
            assert d0 in (n,n+1)
            assert a0==CHIPS[n]+12*(d0&1)
            self.gets.append(d0)
            if self.fail_get==d0:
                if self.foreign_odd and d0&1:
                    self.w8(GFX+166,self.u8(GFX+166)|(1<<d0))
                    self.w32(TABLE+4*d0,0x140000)
                    self.pointer(d0,0x140100)
                self.w16(a0+10,65535)
                self.volatile(0xffffffff)
            elif self.bad_get==d0:
                self.w16(a0+10,1)
                self.volatile(1)
            else:
                assert not self.u8(GFX+166)&(1<<d0)
                self.w8(GFX+166,self.u8(GFX+166)|(1<<d0))
                self.w16(a0+10,1 if self.bad_num==d0 else d0)
                if d0&1 and self.bad_palette_after_get:self.rgb=bytes(45)
                self.volatile(d0)
        elif address==GFX-420:
            assert a0==VP
            ch=self.u16(a1+10)
            assert ch in (n,n+1)
            assert a1==CHIPS[n]+12*(ch&1)
            assert a2==self.stream(n,bool(ch&1))
            assert self.u32(RECS[n]+12)==15
            assert self.u16(a1+8)==257
            self.changes.append(ch)
            if self.fail_change!=ch:
                self.w32(a1,a2)
                self.move_model(a1,self.u16(a1+6),self.u16(a1+8))
                assert self.u16(CI+94+8*ch)==BLANK&65535
            if self.mutate_after_change==ch:
                self.rgb=bytes(45)
            self.volatile()
        elif address==GFX-426:
            assert a0==VP and a1==CHIPS[n]
            assert self.u32(RECS[n]+12)==15
            assert self.u8(self.stream(n,True)+3)&128
            self.moves.append((d0,d1))
            if not self.fail_move:self.move_model(a1,d0,d1)
            else:
                self.move_model(a1,d0,d1)
                self.pointer(n+1,BLANK)
            self.volatile()
        else:
            super().os(u,address,size,user)
    def watch(self,u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:return
        assert self.current in PAIRS
        n=self.current
        # No native writes to OS tables/Copper, palette, peers or image data.
        assert (address==RECS[n]+12 and size==4
             or address in (CHIPS[n]+8,CHIPS[n]+20) and size==2
             or address==self.stream(n,True)+3 and size==1),(
                 'unexpected native write',hex(address),size)
    def invoke(self,n,entry,x=0,y=0):
        self.current=n
        rec,chip=RECS[n],CHIPS[n]
        length=self.lengths[n]
        before={i:self.slot(i) for i in range(8) if i not in (n,n+1)}
        peers={i:(self.read(RECS[i],44),self.read(CHIPS[i],self.lengths[i]))
               for i in self.lengths if i!=n}
        orig=self.read(rec,44)
        orig_data=self.read(chip,length)
        stream=8+4*self.heights[n]
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,reg in enumerate(REGS):u.reg_write(reg,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,rec)
        u.reg_write(UC_M68K_REG_A1,GFX)
        u.reg_write(UC_M68K_REG_D0,x&0xffffffff)
        u.reg_write(UC_M68K_REG_D1,y&0xffffffff)
        saved={reg:u.reg_read(reg) for reg in REGS}
        u.reg_write(UC_M68K_REG_A7,STACK)
        self.w32(STACK,STOP)
        u.emu_start(CODE+entry,STOP,count=500000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items())
        assert self.read(rec,12)==orig[:12] and self.read(rec+16,28)==orig[16:]
        assert self.read(chip-16,16)==bytes([0xa5])*16
        assert self.read(chip+length,16)==bytes([0xc3])*16
        now=self.read(chip,length)
        assert now[24:96]==orig_data[24:96]
        assert now[100:96+stream]==orig_data[100:96+stream]
        assert now[100+stream:]==orig_data[100+stream:]
        assert all(self.slot(i)==s for i,s in before.items())
        assert all(self.read(RECS[i],44)==r and self.read(CHIPS[i],self.lengths[i])==p
                   for i,(r,p) in peers.items())
        self.current=None
        return (u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1))
    def state(self,n):return self.u32(RECS[n]+12)
    def visible(self,n,x,y):
        p=CHIPS[n]
        assert self.state(n)==31
        assert self.u16(p+6)==self.u16(p+18)==x
        assert self.u16(p+8)==self.u16(p+20)==y
        assert self.u32(p)==self.stream(n)
        assert self.u32(p+12)==self.stream(n,True)
        assert self.u32(TABLE+4*n)==p and self.u32(TABLE+4*(n+1))==p+12
        assert self.u32(self.stream(n))^self.u32(self.stream(n,True))==128
        for ch in (n,n+1):
            addr=self.stream(n,bool(ch&1))
            assert self.u16(CI+90+8*ch)==addr>>16
            assert self.u16(CI+94+8*ch)==addr&65535

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    cases=0
    def new(n=2,colors=15,height=16):
        m=AttachedMachine(code);m.record(n,height=height,colors=colors);return m
    for n in PAIRS:
        for colors in range(4,16):
            m=new(n,colors)
            assert m.invoke(n,PALETTE)==(1,0)
            assert m.rgb_calls==[(17,colors)]
            assert m.invoke(n,ACQUIRE)==(1,0) and m.state(n)==7
            assert m.invoke(n,SHOW,16,32)==(1,0)
            assert m.changes==[n,n+1];m.visible(n,16,32)
            assert m.invoke(n,MOVE,304,240)==(1,0);m.visible(n,304,240)
            assert m.invoke(n,RETIRE)==(1,0) and m.state(n)==20
            assert m.frees==[n+1,n] and m.waits==2
            assert m.invoke(n,RETIRE)==(1,0) and m.waits==2
            cases+=6
        for height in (1,255,256):
            m=new(n,height=height)
            assert m.invoke(n,ACQUIRE)==(1,0)
            assert m.invoke(n,SHOW,0,256-height)==(1,0)
            m.visible(n,0,256-height)
            assert m.invoke(n,RETIRE)==(1,0)
            cases+=3
        for tags in ((32,16,255,4),(16,32,255,4),(16,16,63,4),(16,16,255,8)):
            m=new(n);m.tags=tags
            assert m.invoke(n,ACQUIRE)==(0,2) and m.state(n)==0 and not m.gets
            cases+=1
        for k in (0,11,44):
            m=new(n);rgb=bytearray(m.rgb);rgb[k]^=1;m.rgb=bytes(rgb)
            assert m.invoke(n,ACQUIRE)==(0,2) and not m.gets
            cases+=1
        m=new(n,4);rgb=bytearray(m.rgb);rgb[44]^=1;m.rgb=bytes(rgb)
        assert m.invoke(n,PALETTE)==(1,0) # unused pen doesn't constrain attachment
        cases+=1
        m=new(n);m.bad_palette_after_get=True
        assert m.invoke(n,ACQUIRE)==(0,2) and m.state(n)==7
        assert m.invoke(n,RETIRE)==(1,0) and m.frees==[n+1,n] and m.waits==0
        cases+=2
        m=new(n);m.fail_get=n
        assert m.invoke(n,ACQUIRE)==(0,4) and m.state(n)==0
        assert m.invoke(n,RETIRE)==(2,0) and not m.frees
        cases+=2
        m=new(n);m.fail_get=n+1;m.foreign_odd=True
        assert m.invoke(n,ACQUIRE)==(0,4) and m.state(n)==5
        foreign=m.slot(n+1)
        assert m.invoke(n,RETIRE)==(1,0) and m.frees==[n] and m.waits==0
        assert m.slot(n+1)==foreign
        cases+=2
        for ch in (n,n+1):
            for kind in ('bad_get','bad_num'):
                m=new(n);setattr(m,kind,ch)
                assert m.invoke(n,ACQUIRE)==(0,5) and m.state(n)&0x80000000
                assert m.invoke(n,RETIRE)==(0,3) and not m.frees
                cases+=2
        for ch in (n,n+1):
            m=new(n);m.fail_change=ch
            assert m.invoke(n,ACQUIRE)==(1,0)
            assert m.invoke(n,SHOW,10,10)==(0,6) and m.state(n)==15
            assert m.invoke(n,MOVE,10,10)==(0,3)
            assert m.invoke(n,RETIRE)==(1,0) and m.frees==[n+1,n] and m.waits==2
            cases+=4
        m=new(n);m.mutate_after_change=n+1
        assert m.invoke(n,ACQUIRE)==(1,0)
        assert m.invoke(n,SHOW,10,10)==(0,6) and m.state(n)==15
        assert not m.moves and m.invoke(n,RETIRE)==(1,0)
        cases+=3
        m=new(n)
        assert m.invoke(n,ACQUIRE)==(1,0)
        for x,y in ((-1,0),(305,0),(0,-1),(0,241)):
            assert m.invoke(n,SHOW,x,y)==(0,7) and m.state(n)==7 and not m.changes
            cases+=1
        assert m.invoke(n,SHOW,10,10)==(1,0)
        m.fail_move=True
        assert m.invoke(n,MOVE,20,20)==(0,6) and m.state(n)==15
        m.stale=n
        assert m.invoke(n,RETIRE)==(0,3) and m.state(n)==4 and m.waits==0
        m.pointer(n,BLANK)
        m.mutate_wait=lambda k:k.pointer(n+1,0x140100)
        assert m.invoke(n,RETIRE)==(0,3) and m.state(n)==4 and m.waits==2
        m.pointer(n+1,BLANK)
        assert m.invoke(n,RETIRE)==(1,0) and m.waits==4 and m.frees==[n+1,n]
        cases+=5
        for ch in (n,n+1):
            m=new(n);m.w8(GFX+166,m.u8(GFX+166)|(1<<ch))
            assert m.invoke(n,ACQUIRE)==(0,3) and not m.gets
            cases+=1
        for addr,value,width in ((VP+32,0x4000,2),(VP+20,1,4),(VP+12,1,4),
                                  (VP+26,255,2),(CM+18,0,1),(GFX+20,38,2)):
            m=new(n);{1:m.w8,2:m.w16,4:m.w32}[width](addr,value)
            assert m.invoke(n,ACQUIRE)[0]==0 and not m.gets
            cases+=1
        m=new(n);assert m.invoke(n,ACQUIRE)==(1,0)
        assert m.invoke(n,SHOW,10,10)==(1,0)
        m.w32(TABLE+4*(n+1),0x140000)
        assert m.invoke(n,RETIRE)==(0,3) and not m.frees
        cases+=3
    for order in itertools.permutations(PAIRS):
        m=AttachedMachine(code)
        for n in PAIRS:
            # Distinct physical pairs; shared RGB slice.
            m.record(n,colors=15)
            assert m.invoke(n,ACQUIRE)==(1,0)
            assert m.invoke(n,SHOW,n*16,n*16)==(1,0)
        for n in order:
            assert m.invoke(n,RETIRE)==(1,0)
            cases+=1
        assert m.u8(GFX+166)==3 and m.waits==6
    print('S2C_ATTACHED_LIFECYCLE_CPU_PASS',cases,'checks; modeled OS only',flush=True)

if __name__=='__main__':main()
