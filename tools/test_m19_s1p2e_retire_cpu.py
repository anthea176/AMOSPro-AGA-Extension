#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Execute P2e on Unicorn MC68020 with explicit mocked graphics.library.
This proves the routine's ABI and state transitions, not real OS or DMA.
"""
import argparse
from pathlib import Path
from hashlib import sha256
from struct import pack, unpack
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

CODE,STOP,GFX,CI,TABLE,VP,STACK,REC,CHIP=(0x20000,0x30000,0x80000,0x468,0x90000,0xa0000,0xb0000,0x100000,0x140000)
SIZE,IMAGE,BLANK,NEUTRAL=192,CHIP+48,CHIP+120,0x518
PRESERVED=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
           UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
           UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)

class Machine:
    def __init__(self,code,flags=15,mode='ok'):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        for n in (270,414,420):
            self.u.mem_write(GFX-n,b'\x4e\x75')
        self.mode=mode
        self.calls=[]
        self.w16(GFX+18,512)
        self.w16(GFX+20,40)
        self.w32(GFX+38,CI)
        self.w32(GFX+208,TABLE)
        self.w8(GFX+166,1|((flags&3)<<2))
        for i in range(8):
            self.w16(CI+88+i*8,0x120+i*4)
            self.w16(CI+92+i*8,0x122+i*4)
            self.copper(i,NEUTRAL)
        self.u.mem_write(REC-16,b'\x5a'*16)
        self.u.mem_write(REC,pack('>4I',CHIP,SIZE,VP,flags)+pack('>I4H',0,16,0,0,3 if flags&2 else 65535))
        self.u.mem_write(REC+28,b'\x5a'*16)
        self.u.mem_write(CHIP-16,b'\x5a'*16)
        self.u.mem_write(CHIP,bytes(SIZE))
        self.u.mem_write(CHIP+SIZE,b'\x5a'*16)
        self.w16(CHIP+4,16)
        self.w16(CHIP+10,2 if flags&1 else 65535)
        self.w32(CHIP+12,SIZE)
        self.w32(CHIP+40,48)
        self.w32(CHIP+44,120)
        if flags&8:
            self.w32(CHIP,IMAGE)
            self.w32(TABLE+8,CHIP)
            self.copper(2,IMAGE)
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def r32(self,a):return unpack('>I',self.read(a,4))[0]
    def w32(self,a,v):self.u.mem_write(a,pack('>I',v))
    def w16(self,a,v):self.u.mem_write(a,pack('>H',v))
    def w8(self,a,v):self.u.mem_write(a,bytes([v]))
    def copper(self,i,p):
        self.w16(CI+90+i*8,p>>16)
        self.w16(CI+94+i*8,p&65535)
    def on_write(self,uc,access,a,n,value,user):
        if STACK-4096<=a and a+n<=STACK+4:return
        assert REC+12<=a and a+n<=REC+16,('unexpected CPU write',hex(a),n)
    def on_code(self,uc,addr,size,user):
        if addr==GFX-420:
            self.calls.append('blank')
            assert (uc.reg_read(UC_M68K_REG_A0),uc.reg_read(UC_M68K_REG_A1),
                    uc.reg_read(UC_M68K_REG_A2))==(VP,CHIP,BLANK)
            if self.mode!='blank_noop':
                self.w32(CHIP,BLANK)
                if self.mode!='blank_copper_stale':self.copper(2,BLANK)
        elif addr==GFX-414:
            ch=uc.reg_read(UC_M68K_REG_D0)
            assert ch in (2,3) and self.read(GFX+166,1)[0]&(1<<ch)
            assert self.r32(REC+12)&(1<<(ch-2))
            self.calls.append('free'+str(ch))
            self.w8(GFX+166,self.read(GFX+166,1)[0]&~(1<<ch))
            self.w32(TABLE+ch*4,0)
            if not(ch==2 and self.mode=='retain'):self.copper(ch,NEUTRAL)
        elif addr==GFX-270:
            self.calls.append('tof')
            if self.mode=='lost_owner' and self.calls.count('tof')==1:
                self.w8(GFX+166,1)
        else:return
        for r,v in ((UC_M68K_REG_D0,0xdead0000),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            uc.reg_write(r,v)
    def invoke(self):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(PRESERVED):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,REC)
        u.reg_write(UC_M68K_REG_A1,GFX)
        saved={r:u.reg_read(r) for r in PRESERVED}
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE,STOP,count=100000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items())
        for p in (CHIP-16,CHIP+SIZE,REC-16,REC+28):
            assert self.read(p,16)==b'\x5a'*16
        return u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1)
    def check(self,want,flags,calls):
        assert self.invoke()==want,(want,self.calls,self.r32(REC+12))
        assert self.r32(REC+12)==flags
        assert self.calls==calls,(self.calls,calls)

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('native',type=Path)
    code=cli.parse_args().native.read_bytes()
    full=['blank','tof','tof','free3','free2','tof','tof']
    Machine(code).check((1,0),4,full)
    m=Machine(code);m.w32(CHIP,BLANK);m.copper(2,BLANK)
    m.check((1,0),4,full)
    for flags,expect in ((5,['free2','tof','tof']),(7,['free3','free2','tof','tof']),
                         (13,['blank','tof','tof','free2','tof','tof'])):
        Machine(code,flags).check((1,0),4,expect)
    Machine(code,0).check((2,0),0,[])
    m=Machine(code,4);m.w32(REC+8,0xdead0000)
    m.check((1,0),4,['tof','tof'])
    # Do not free a reallocated OS channel on repeated Off/Close.
    m.calls=[];m.w8(GFX+166,13);m.w32(TABLE+8,0x120000)
    m.check((1,0),4,['tof','tof'])
    m=Machine(code,mode='retain')
    m.check((0,7),4,full)
    m.calls=[];m.copper(2,NEUTRAL);m.w32(REC+8,0)
    m.check((1,0),4,['tof','tof'])
    for mode,reason in (('blank_noop',6),('blank_copper_stale',6),('lost_owner',5)):
        Machine(code,mode=mode).check((0,reason),15,['blank','tof','tof'])
    for addr,value,reason,width in ((GFX+20,41,2,2),(GFX+18,200,2,2),
             (CI+88,0x180,4,2),(GFX+208,0,4,4),(GFX+38,1,4,4),
             (TABLE+8,0x120000,5,4),(TABLE+12,REC+16,5,4),
             (CHIP+10,1,5,2),(REC+26,2,5,2),(REC+8,0,5,4),
             (CHIP,NEUTRAL,5,4),(REC+4,191,1,4),(CHIP+44,121,1,4),
             (CHIP+4,257,1,2),(GFX+166,1,5,1)):
        m=Machine(code)
        {1:m.w8,2:m.w16,4:m.w32}[width](addr,value)
        m.check((0,reason),15,[])
    m=Machine(code,4);m.copper(5,CHIP+8)
    m.check((0,7),4,['tof','tof'])
    m=Machine(code,4);m.w32(TABLE+12,REC+16)
    m.check((0,7),4,['tof','tof'])
    Machine(code,3).check((0,3),3,[])
    print('S1P2E_LOGICAL_RETIRE_CPU_PASS',32,sha256(code).hexdigest(),flush=True)

if __name__=='__main__':main()
