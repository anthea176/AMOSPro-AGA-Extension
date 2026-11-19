#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A MC68020 emulator tests: never select front/pending Safe bitmap."""
from __future__ import annotations
from struct import pack,unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import (UC_CPU_M68K_M68020,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
from m19_b8_back_selector_emit import emit_b8_back_selector,STATE_OFF
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core
DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
EXEC=0x110000
STOP=0x18000
STACK=0xf0000
AMOS=0x40000
STATE=0x52000
DB=0x53000
SB0=0x54000
SB1=0x54100
BMP0=0x55000
BMP1=0x55100
SCREEN=0x70000
BUF=0x66000


class Selector:
    def __init__(self,native,labels,base):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x1000000)
        self.base=base
        self.entry=base+labels['b8_checked_back_selector_entry']
        self.uc.mem_write(base,native)
        self.uc.mem_write(4,pack('>I',EXEC))
        self.uc.mem_write(EXEC+0x128,pack('>H',2))
        self.uc.mem_write(STOP,bytes.fromhex('4e71'))
        self.regions=[(AMOS,AMOS+0x200),(STATE,STATE+40),
                      (DB,DB+24),(SB0,SB0+8),(SB1,SB1+8),
                      (BMP0,BMP0+40),(BMP1,BMP1+40)]
        self.put(AMOS+STATE_OFF,STATE)
        self.put(STATE,SCREEN)
        self.put(STATE+32,DB)
        self.put(DB,SB0);self.put(DB+4,SB1)
        self.put(DB+8,0);self.put(DB+20,0)
        self.put(SB0,BMP0);self.put(SB1,BMP1)
        self.uc.hook_add(UC_HOOK_CODE,self.os_call,begin=EXEC-534,end=EXEC-534)
        self.mem_calls=0

    def put(self,addr,num):
        self.uc.mem_write(addr,pack('>I',num&0xffffffff))

    def os_call(self,uc,addr,size,user):
        self.mem_calls+=1
        ptr=uc.reg_read(AR[1])
        ok=any(start<=ptr<end for start,end in self.regions)
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[0],int(ok))
        uc.reg_write(DR[1],0xbaad0011)
        uc.reg_write(AR[0],0xfade0000)
        uc.reg_write(AR[1],0xfade0001)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def invoke(self,*,owner=AMOS,limit=3000000):
        uc=self.uc
        for i,r in enumerate(DR):uc.reg_write(r,0x200120+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x210000+i*0x100)
        uc.reg_write(AR[5],owner)
        before={r:uc.reg_read(r) for r in DR+AR[:7]}
        frozen=bytes(uc.mem_read(AMOS,0x200))+bytes(uc.mem_read(STATE,40))
        frozen+=bytes(uc.mem_read(DB,24))+bytes(uc.mem_read(SB0,8))
        frozen+=bytes(uc.mem_read(SB1,8))+bytes(uc.mem_read(BMP0,40))
        frozen+=bytes(uc.mem_read(BMP1,40))
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK);uc.mem_write(STACK,pack('>I',STOP))
        try:uc.emu_start(self.entry,STOP,count=limit)
        except Exception as exc:raise AssertionError(('MC68020 selector fault',
            str(exc),hex(uc.reg_read(UC_M68K_REG_PC)))) from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(AR[7])==STACK+4
        for r,value in before.items():
            if r not in (DR[2],DR[3]):
                assert uc.reg_read(r)==value,('Selector ABI clobbered',r)
        after=bytes(uc.mem_read(AMOS,0x200))+bytes(uc.mem_read(STATE,40))
        after+=bytes(uc.mem_read(DB,24))+bytes(uc.mem_read(SB0,8))
        after+=bytes(uc.mem_read(SB1,8))+bytes(uc.mem_read(BMP0,40))
        after+=bytes(uc.mem_read(BMP1,40))
        assert frozen==after,'Selector modified screen or OS state'
        return uc.reg_read(DR[3]),uc.reg_read(DR[2])


def main():
    code,labels=emit_b8_back_selector()
    prefix,_=emit_planar_snapshot_core()
    assert code.startswith(prefix)
    assert labels['b8_checked_back_selector_entry']==len(prefix)
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
             disasm(code[len(prefix):],0x10000))
    assert sum(x.size for x in ins)==len(code)-len(prefix)
    assert all(not x.mnemonic.startswith('dc.') for x in ins)
    cases=0
    for base in (0x20000,0x31000):
        m=Selector(code,labels,base)
        assert m.invoke()==(1,BMP1);cases+=1
        m.put(DB+8,1)
        assert m.invoke()==(1,BMP0);cases+=1
        m.put(DB+20,1)
        assert m.invoke()==(0,0);cases+=1
        m.put(DB+20,2) # Disp pending alone is not Safe pending
        assert m.invoke()==(1,BMP0);cases+=1
        m.put(DB+20,0)
        m.put(DB+8,2);assert m.invoke()==(0,0);cases+=1
        m.put(DB+8,0)
        m.put(DB+4,SB0);assert m.invoke()==(0,0);cases+=1
        m.put(DB+4,SB1)
        m.put(SB1,BMP0);assert m.invoke()==(0,0);cases+=1
        m.put(SB1,BMP1)
        m.put(SB1,0);assert m.invoke()==(0,0);cases+=1
        m.put(SB1,BMP1)
        m.put(SB1,BMP1+1);assert m.invoke()==(0,0);cases+=1
        m.put(SB1,BMP1)
        m.put(STATE+32,0);assert m.invoke()==(0,0);cases+=1
        m.put(STATE+32,DB)
        m.put(STATE,0);assert m.invoke()==(0,0);cases+=1
        m.put(STATE,SCREEN)
        m.put(AMOS+STATE_OFF,0);assert m.invoke()==(0,0);cases+=1
        m.put(AMOS+STATE_OFF,STATE)
        m.uc.mem_write(EXEC+0x128,pack('>H',0))
        assert m.invoke()==(0,0);cases+=1
        m.uc.mem_write(EXEC+0x128,pack('>H',2))
        assert m.invoke(owner=0)==(0,0);cases+=1
        assert m.invoke(owner=AMOS+1)==(0,0);cases+=1
        assert m.invoke(owner=0x2f000)==(0,0);cases+=1
        assert m.invoke()==(1,BMP1);cases+=1
    print('M19 B8 checked back selector real MC68020 Gate A PASS',
          cases,'cases; 2 relocations; Safe fail-closed; no front writes or Swap')


if __name__=='__main__':main()
