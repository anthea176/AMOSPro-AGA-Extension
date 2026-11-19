#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 emulation: all-or-nothing private snapshot pool and owner guards."""
from __future__ import annotations
from struct import pack,unpack
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool,R,ROOT_BYTES,MEMF_PUBLIC_CLEAR
DR=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
AR=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7)
EXEC=0x110000
STOP=0x18000
STACK=0xf0000
OWNER=0x40000
OTHER=0x43000
SCREEN=0x50000
FOREIGN_SCREEN=0x51000
BMP0=0x55000
BMP1=0x55100
BMP2=0x55200
ALLOCATIONS=[0x80000,0xb0000]


class PoolMachine:
    def __init__(self,base,raw,labels):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x1000000)
        self.base=base
        self.labels=labels
        self.uc.mem_write(base,raw)
        self.uc.mem_write(4,pack('>I',EXEC))
        self.uc.mem_write(EXEC+0x128,pack('>H',2))
        self.uc.mem_write(STOP,bytes.fromhex('4e71'))
        self.regions=[(OWNER,OWNER+256),(OTHER,OTHER+256),
                      (SCREEN,SCREEN+256),(FOREIGN_SCREEN,FOREIGN_SCREEN+256),
                      (BMP0,BMP0+64),(BMP1,BMP1+64),(BMP2,BMP2+64)]
        self.next_alloc=0
        self.allocations={}
        self.alloc_calls=[]
        self.free_calls=[]
        self.fail_on_alloc=0
        self.uc.hook_add(UC_HOOK_CODE,self.os_call,begin=EXEC-534,end=EXEC-198)

    def os_call(self,uc,addr,size,user):
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        d0=uc.reg_read(DR[0])
        d1=uc.reg_read(DR[1])
        a1=uc.reg_read(AR[1])
        if addr==EXEC-534:
            out=int(any(lo<=a1<hi for lo,hi in self.regions)
                    or any(p<=a1<p+n for p,n in self.allocations.items()))
        elif addr==EXEC-198:
            self.alloc_calls.append((d0,d1))
            assert d1==MEMF_PUBLIC_CLEAR
            if self.fail_on_alloc==len(self.alloc_calls) or self.next_alloc>=2:
                out=0
            else:
                out=ALLOCATIONS[self.next_alloc]
                self.next_alloc+=1
                self.allocations[out]=d0
                self.uc.mem_write(out,bytes(d0))
        elif addr==EXEC-210:
            self.free_calls.append((a1,d0))
            assert a1 in self.allocations and self.allocations[a1]==d0
            del self.allocations[a1]
            out=0
        else:
            raise AssertionError(('unexpected Exec call',hex(addr)))
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[0],out)
        uc.reg_write(DR[1],0xdecacafe)
        uc.reg_write(AR[0],0xfade0000)
        uc.reg_write(AR[1],0xfade0001)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def read_root(self):
        return unpack('>8I',self.uc.mem_read(self.base+self.labels['b8_pool_root'],ROOT_BYTES))

    def call(self,which,*,owner=OWNER,screen=SCREEN,bitmap0=BMP0,
             bitmap1=BMP1,bytes_per_page=81920):
        uc=self.uc
        for i,r in enumerate(DR):uc.reg_write(r,0x123000+i)
        for i,r in enumerate(AR[:7]):uc.reg_write(r,0x340000+i*0x100)
        uc.reg_write(DR[0],bytes_per_page)
        uc.reg_write(AR[0],screen)
        uc.reg_write(AR[1],bitmap0)
        uc.reg_write(AR[2],bitmap1)
        uc.reg_write(AR[5],owner)
        before={r:uc.reg_read(r) for r in DR+AR[:7]}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        try:uc.emu_start(self.base+self.labels['b8_pool_'+which+'_entry'],
                         STOP,count=4000000)
        except Exception as exc:raise AssertionError(('native pool CPU fault',which,
            str(exc),hex(uc.reg_read(UC_M68K_REG_PC)))) from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(AR[7])==STACK+4
        for r,v in before.items():
            if r not in (DR[2],DR[3]):assert uc.reg_read(r)==v,('ABI',which,r)
        return uc.reg_read(DR[3]),uc.reg_read(DR[2])


def main():
    raw,labels=emit_b8_snapshot_pool()
    assert raw==emit_b8_snapshot_pool()[0]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
             disasm(raw[:labels['b8_pool_root']],0x10000))
    assert sum(x.size for x in ins)==labels['b8_pool_root']
    cases=0
    for base in (0x20000,0x30000):
        m=PoolMachine(base,raw,labels)
        assert m.call('get')==(0,0);cases+=1
        assert m.call('close')==(1,0);cases+=1
        assert m.call('bind')==(1,0);cases+=1
        assert m.alloc_calls==[(81920,MEMF_PUBLIC_CLEAR)]*2
        assert m.read_root()==(OWNER,SCREEN,BMP0,ALLOCATIONS[0],81920,
                               BMP1,ALLOCATIONS[1],81920)
        assert m.call('bind')==(1,0) and len(m.alloc_calls)==2;cases+=1
        assert m.call('get',bitmap0=BMP0)==(1,ALLOCATIONS[0]);cases+=1
        assert m.call('get',bitmap0=BMP1)==(1,ALLOCATIONS[1]);cases+=1
        assert m.call('get',bitmap0=BMP2)==(0,0);cases+=1
        assert m.call('get',owner=OTHER)==(0,0);cases+=1
        assert m.call('close',owner=OTHER)==(0,0);cases+=1
        assert m.call('close',screen=FOREIGN_SCREEN)==(0,0);cases+=1
        assert len(m.free_calls)==0
        assert m.call('bind',screen=FOREIGN_SCREEN)==(0,0);cases+=1
        assert m.call('bind',bytes_per_page=64)==(0,0);cases+=1
        assert m.call('close')==(1,0);cases+=1
        assert m.read_root()==(0,)*8 and len(m.free_calls)==2
        assert not m.allocations
        assert m.call('close')==(1,0) and len(m.free_calls)==2;cases+=1
        assert m.call('get')==(0,0);cases+=1
        # No allocations if a validation fails; empty root always.
        for changed in (dict(owner=0),dict(screen=0),dict(bitmap0=0),
                        dict(bitmap1=0),dict(bitmap0=BMP1),dict(bytes_per_page=1),
                        dict(bytes_per_page=81921),dict(bytes_per_page=2097154)):
            t=PoolMachine(base,raw,labels)
            assert t.call('bind',**changed)==(0,0),changed
            assert t.alloc_calls==[] and t.read_root()==(0,)*8
            cases+=1
        # No leak when the second AllocMem fails.
        t=PoolMachine(base,raw,labels);t.fail_on_alloc=2
        assert t.call('bind')==(0,0)
        assert len(t.alloc_calls)==2 and len(t.free_calls)==1
        assert t.read_root()==(0,)*8 and not t.allocations;cases+=1
        t=PoolMachine(base,raw,labels);t.fail_on_alloc=1
        assert t.call('bind')==(0,0)
        assert len(t.alloc_calls)==1 and not t.free_calls
        assert t.read_root()==(0,)*8;cases+=1
        t=PoolMachine(base,raw,labels)
        t.uc.mem_write(EXEC+0x128,pack('>H',0))
        assert t.call('bind')==(0,0) and not t.alloc_calls;cases+=1
    print('M19 B8 MC68020 two-page snapshot pool Gate A PASS',cases,
          'cases, two placements; transactional AllocMem/FreeMem; no Lib/token changes')


if __name__=='__main__':main()
