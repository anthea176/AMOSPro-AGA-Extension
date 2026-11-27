#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 pair retirement, modeled graphics.library/Exec only."""
import argparse
import itertools
from pathlib import Path
from struct import pack, unpack
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

CODE,STOP,EXEC,GFX,CI,TABLE,STACK=0x20000,0x30000,0x60000,0x70000,0x90000,0x91000,0xb0000
RECS={n:0x100000+0x100*n for n in (2,4,6)}
CHIPS={n:0x110000+0x1000*n for n in (2,4,6)}
BLANK=CI+176
REGS=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
      UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
      UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)

class Machine:
    def __init__(self,code):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        self.w32(4,EXEC)
        self.w16(GFX+18,212)
        self.w16(GFX+20,40)
        self.w32(GFX+38,CI)
        self.w32(GFX+208,TABLE)
        # A foreign cursor and another external sprite must not be touched.
        self.w8(GFX+166,3)
        for n in range(8):
            self.w16(CI+88+8*n,0x120+4*n)
            self.w16(CI+92+8*n,0x122+4*n)
            self.pointer(n,BLANK)
        self.w32(TABLE,0x130000)
        self.pointer(0,0x131000)
        self.w32(TABLE+4,0x132000)
        self.pointer(1,0x133000)
        for addr in (EXEC-534,GFX-414,GFX-270):
            self.u.mem_write(addr,b'\x4e\x75')
        self.u.hook_add(UC_HOOK_CODE,self.os)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.watch)
        self.frees=[]
        self.waits=0
        self.stale=None
        self.mutate_wait=None
        self.unmapped=set()
        self.current=None
        self.writes=[]
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def u8(self,a):return self.read(a,1)[0]
    def u16(self,a):return unpack('>H',self.read(a,2))[0]
    def u32(self,a):return unpack('>I',self.read(a,4))[0]
    def w8(self,a,v):self.u.mem_write(a,bytes([v]))
    def w16(self,a,v):self.u.mem_write(a,pack('>H',v))
    def w32(self,a,v):self.u.mem_write(a,pack('>I',v))
    def pointer(self,n,p):
        self.w16(CI+90+8*n,p>>16)
        self.w16(CI+94+8*n,p&65535)
    def slot(self,n):
        return self.read(TABLE+4*n,4),self.read(CI+88+8*n,8),bool(self.u8(GFX+166)&(1<<n))
    def record(self,n,flags=15,height=16):
        rec,chip=RECS[n],CHIPS[n]
        frame=8+4*height
        length=48+2*frame
        self.u.mem_write(rec,bytes(44))
        self.u.mem_write(chip,bytes(length))
        self.w32(rec,chip)
        self.w32(rec+4,length)
        self.w32(rec+8,0x150000)
        self.w32(rec+12,flags)
        self.w16(rec+26,n+1 if flags&2 else 65535)
        self.w32(rec+28,n+10)
        self.w32(rec+32,29)
        self.w32(rec+36,3)
        self.w32(rec+40,n)
        self.w16(chip+4,height)
        self.w16(chip+10,n if flags&1 else 65535)
        self.w32(chip+12,length)
        self.w32(chip+40,48)
        self.w32(chip+44,48+frame)
        self.w8(GFX+166,self.u8(GFX+166)|((flags&3)<<n))
        if flags&8:
            self.w32(chip,chip+48+frame) # alternate slot is live
            self.w32(TABLE+4*n,chip)
            self.pointer(n,chip+48+frame)
        return rec,chip
    def volatile(self,d0=0):
        for reg,v in ((UC_M68K_REG_D0,d0),(UC_M68K_REG_D1,0xa5a5a5a5),
                      (UC_M68K_REG_A0,0x12345678),(UC_M68K_REG_A1,0x87654320)):
            self.u.reg_write(reg,v)
    def os(self,u,address,size,user):
        if address==EXEC-534:
            p=u.reg_read(UC_M68K_REG_A1)
            self.volatile(int(0<p<0x200000 and p not in self.unmapped))
        elif address==GFX-414:
            n=u.reg_read(UC_M68K_REG_D0)&65535
            assert n in (self.current,self.current+1)
            assert self.u8(GFX+166)&(1<<n),'double/foreign FreeSprite'
            self.frees.append(n)
            self.w8(GFX+166,self.u8(GFX+166)&~(1<<n))
            self.w32(TABLE+4*n,0)
            if n!=self.stale:self.pointer(n,BLANK)
            self.volatile()
        elif address==GFX-270:
            self.waits+=1
            if self.mutate_wait:
                fn=self.mutate_wait
                self.mutate_wait=None
                fn(self)
            self.volatile()
    def watch(self,u,access,address,size,value,user):
        if STACK-4096<=address and address+size<=STACK+4:return
        assert self.current is not None
        assert address==RECS[self.current]+12 and size==4,('unexpected write',hex(address),size)
        self.writes.append(value&0xffffffff)
    def call(self,n,result,flags,frees=(),waits=0,reason=None):
        self.current=n
        rec=RECS[n]
        original=self.read(rec,44)
        before={i:self.slot(i) for i in range(8) if i not in (n,n+1)}
        peers={i:self.read(RECS[i],44) for i in RECS if i!=n}
        chip=self.read(CHIPS[n],2112)
        nf,nw=len(self.frees),self.waits
        self.writes=[]
        self.u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,reg in enumerate(REGS):self.u.reg_write(reg,0x55000000+i)
        self.u.reg_write(UC_M68K_REG_A0,rec)
        self.u.reg_write(UC_M68K_REG_A1,GFX)
        saved={reg:self.u.reg_read(reg) for reg in REGS}
        self.u.reg_write(UC_M68K_REG_A7,STACK)
        self.w32(STACK,STOP)
        self.u.emu_start(CODE,STOP,count=100000)
        assert self.u.reg_read(UC_M68K_REG_PC)==STOP
        assert self.u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(self.u.reg_read(reg)==v for reg,v in saved.items())
        assert self.u.reg_read(UC_M68K_REG_D0)==result
        if reason is not None:assert self.u.reg_read(UC_M68K_REG_D1)==reason
        assert self.u32(rec+12)==flags
        assert self.read(rec,44)==original[:12]+pack('>I',flags)+original[16:]
        assert self.read(CHIPS[n],2112)==chip
        assert self.frees[nf:]==list(frees) and self.waits-nw==waits
        assert all(self.slot(i)==s for i,s in before.items())
        assert all(self.read(RECS[i],44)==s for i,s in peers.items())
        self.current=None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    cases=0
    for n in RECS:
        for flags,result,final,frees,waits in (
            (0,2,0,(),0),(20,1,20,(),0),
            (5,1,20,(n,),0),(7,1,20,(n+1,n),0),
            (13,1,20,(n,),2),(15,1,20,(n+1,n),2),
            (4,1,20,(),2)):
            m=Machine(code);m.record(n,flags)
            if flags==5:
                # An unrelated odd-channel owner is legal after partial acquisition.
                m.w8(GFX+166,m.u8(GFX+166)|(1<<(n+1)))
                m.w32(TABLE+4*(n+1),0x140000);m.pointer(n+1,0x140100)
            odd=m.slot(n+1)
            m.call(n,result,final,frees,waits,0)
            if flags==5:assert m.slot(n+1)==odd
            cases+=1
        for h in (1,255,256):
            m=Machine(code);m.record(n,15,h);m.call(n,1,20,(n+1,n),2,0);cases+=1
        for wrong in (0,1,3,5,7,8,0xffffffff):
            m=Machine(code);rec,chip=m.record(n)
            m.w32(rec+40,wrong);m.call(n,0,15,reason=1);cases+=1
        for off,value,reason in ((12,9,3),(4,70,1),(4,2114,1)):
            m=Machine(code);rec,chip=m.record(n);m.w32(rec+off,value)
            m.call(n,0,9 if off==12 else 15,reason=reason);cases+=1
        for field in ('mask','even_num','odd_num','even_table','odd_table','table_unmapped','gfx'):
            m=Machine(code);rec,chip=m.record(n)
            if field=='mask':m.w8(GFX+166,m.u8(GFX+166)&~(1<<n))
            elif field=='even_num':m.w16(chip+10,n+1)
            elif field=='odd_num':m.w16(rec+26,n)
            elif field=='even_table':m.w32(TABLE+4*n,0x140000)
            elif field=='odd_table':m.w32(TABLE+4*(n+1),0x140000)
            elif field=='table_unmapped':m.unmapped.add(TABLE+31)
            else:m.w16(GFX+20,38)
            m.call(n,0,15,reason=2 if field=='gfx' else 5);cases+=1
        # Already released but stale reference: pending and no premature free.
        m=Machine(code);m.record(n);m.stale=n
        m.call(n,0,4,(n+1,n),0,5);cases+=1
        m.pointer(n,BLANK)
        m.call(n,1,20,(),2,0);cases+=1
        m=Machine(code);m.record(n)
        m.mutate_wait=lambda k:k.pointer(n,0x140100)
        m.call(n,0,4,(n+1,n),2,5);cases+=1
        m.pointer(n,BLANK);m.call(n,1,20,(),2,0);cases+=1
        m=Machine(code);m.record(n,4)
        m.w16(CI+88+8*n,0x1234)
        m.call(n,0,4,reason=5);cases+=1
    # All three simultaneous, retire in every order; other pairs/cursor unchanged.
    for order in itertools.permutations(RECS):
        m=Machine(code)
        for n in RECS:m.record(n)
        for n in order:
            m.call(n,1,20,(n+1,n),2,0);cases+=1
        assert m.u8(GFX+166)==3
        assert m.waits==6
    print('S2B_RETIRE_PAIR_CPU_PASS',cases,'cases; no real DMA or multi-record integration')

if __name__=='__main__':main()
