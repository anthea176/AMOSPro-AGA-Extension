#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 complete PRIVATE page services CPU regression, no installed API.

Runs actual emitted MC68020 instructions under Unicorn, on two placements.
Exec TypeOfMem, AllocMem, FreeMem and graphics state are deterministic mocks.
Never equate this with real AmigaOS, WinUAE Runtime or AMOS Compiler.
"""
from __future__ import annotations

from struct import pack, unpack
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
    UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
    UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7,
)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from m19_b8_page_manager_emit import emit_b8_page_manager, R as SROOT, ROOT_SIZE

DR = (UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
      UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7)
AR = (UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
      UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7)
EXEC = 0x110000
STOP = 0x18000
STACK = 0xf0000
OWNER = 0x40000
OTHER = 0x42000
STATE = 0x50000
DB = 0x51000
SCREEN = 0x52000
SB0 = 0x53000
SB1 = 0x53100
BMP0 = 0x54000
BMP1 = 0x54100
PLANE00 = 0x60000
PLANE01 = 0x61000
PLANE10 = 0x62000
PLANE11 = 0x63000
SNAP0 = 0x80000
SNAP1 = 0xb0000
BPR, ROWS, DEPTH = 4, 2, 2
PAGE_SIZE = BPR * ROWS * DEPTH

class Machine:
    def __init__(self, code, labels, base):
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0, 0x1000000)
        self.base, self.labels = base, labels
        self.uc.mem_write(base, code)
        self.uc.mem_write(4, pack('>I', EXEC))
        self.uc.mem_write(EXEC + 0x128, pack('>H', 2))
        self.uc.mem_write(STOP, bytes.fromhex('4e71'))
        self.regions = [
            (OWNER, OWNER + 0x200), (OTHER, OTHER + 0x200),
            (STATE, STATE + 40), (DB, DB + 24),
            (SCREEN, SCREEN + 32),
            (SB0, SB0 + 4), (SB1, SB1 + 4),
            (BMP0, BMP0 + 40), (BMP1, BMP1 + 40),
            (PLANE00, PLANE00 + BPR * ROWS),
            (PLANE01, PLANE01 + BPR * ROWS),
            (PLANE10, PLANE10 + BPR * ROWS),
            (PLANE11, PLANE11 + BPR * ROWS),
        ]
        self.allocations = {}
        self.alloc_calls, self.free_calls = [], []
        self.next_alloc, self.fail_alloc = 0, 0
        self.put(OWNER + 0x1c8, STATE)
        self.put(STATE, SCREEN)
        self.put(STATE + 32, DB)
        self.put(DB, SB0)
        self.put(DB + 4, SB1)
        self.put(DB + 8, 0)
        self.put(DB + 20, 0)
        self.put(SB0, BMP0)
        self.put(SB1, BMP1)
        self.set_geometry(BMP0, (PLANE00, PLANE01))
        self.set_geometry(BMP1, (PLANE10, PLANE11))
        for n,p in enumerate((PLANE00, PLANE01, PLANE10, PLANE11)):
            self.uc.mem_write(p, bytes([0x20 + 15*n + i for i in range(8)]))
        self.uc.hook_add(UC_HOOK_CODE, self.os_call,
                         begin=EXEC-534, end=EXEC-198)

    def put(self, addr, value):
        self.uc.mem_write(addr, pack('>I', value & 0xffffffff))

    def set_geometry(self, bitmap, planes, *, depth=DEPTH, bpr=BPR, rows=ROWS):
        data = pack('>HHBBH', bpr, rows, 0, depth, 0)
        data += b''.join(pack('>I', p) for p in (list(planes) + [0]*8)[:8])
        self.uc.mem_write(bitmap, data)

    def os_call(self, uc, addr, size, ctx):
        sp = uc.reg_read(AR[7])
        ret = int.from_bytes(uc.mem_read(sp, 4), 'big')
        d0, d1 = uc.reg_read(DR[0]), uc.reg_read(DR[1])
        a1 = uc.reg_read(AR[1])
        if addr == EXEC-534:
            result = int(any(a<=a1<b for a,b in self.regions)
                         or any(p<=a1<p+n for p,n in self.allocations.items()))
        elif addr == EXEC-198:
            self.alloc_calls.append((d0, d1))
            assert d1 == 0x10001, ('invalid Exec allocation flags', d1)
            if len(self.alloc_calls) == self.fail_alloc or self.next_alloc == 2:
                result = 0
            else:
                result = (SNAP0, SNAP1)[self.next_alloc]
                self.next_alloc += 1
                self.allocations[result] = d0
                self.uc.mem_write(result, bytes(d0))
        elif addr == EXEC-210:
            self.free_calls.append((a1, d0))
            assert self.allocations[a1] == d0, ('invalid FreeMem', a1, d0)
            del self.allocations[a1]
            result = 0
        else:
            raise AssertionError(('unexpected OS call',hex(addr)))
        uc.reg_write(AR[7], sp+4)
        uc.reg_write(DR[0], result)
        uc.reg_write(DR[1], 0x1234beef)
        uc.reg_write(AR[0], 0xfade0000)
        uc.reg_write(AR[1], 0xfade0001)
        uc.reg_write(UC_M68K_REG_PC, ret)

    def call(self, op, owner=OWNER):
        uc = self.uc
        for i,reg in enumerate(DR): uc.reg_write(reg, 0x200120+i)
        for i,reg in enumerate(AR[:7]): uc.reg_write(reg, 0x210000+i*0x100)
        uc.reg_write(AR[5], owner)
        previous = {r:uc.reg_read(r) for r in DR+AR[:7]}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(AR[7],STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        try:
            uc.emu_start(self.base+self.labels['b8_service_'+op+'_entry'],
                         STOP, count=5_000_000)
        except Exception as exc:
            raise AssertionError(('MC68020 CPU fault',op,
                str(exc),hex(uc.reg_read(UC_M68K_REG_PC)))) from exc
        assert uc.reg_read(UC_M68K_REG_PC) == STOP
        assert uc.reg_read(AR[7]) == STACK+4, ('stack',op)
        for r,v in previous.items():
            if r not in (DR[2],DR[3]):
                assert uc.reg_read(r) == v, ('AMOS ABI clobbered',op,r)
        assert uc.reg_read(DR[2]) == 0
        result = uc.reg_read(DR[3])
        assert result in (0,1)
        return result

    def page(self, n):
        ps = (PLANE00,PLANE01) if n==0 else (PLANE10,PLANE11)
        return b''.join(bytes(self.uc.mem_read(p,BPR*ROWS)) for p in ps)

    def rewrite_page(self,n,value):
        ps = (PLANE00,PLANE01) if n==0 else (PLANE10,PLANE11)
        for p in ps:self.uc.mem_write(p,bytes([value])*(BPR*ROWS))

    def root(self):
        p = self.base + self.labels['b8_service_root']
        return unpack('>8I', self.uc.mem_read(p,ROOT_SIZE))


def main():
    raw,labels=emit_b8_page_manager()
    assert raw==emit_b8_page_manager()[0]
    assert len(raw)%2==0 and len(raw)<32766
    for symbol in ('b8_service_bind_entry','b8_service_capture_entry',
                   'b8_service_restore_entry','b8_service_close_entry'):
        assert 0<=labels[symbol]<len(raw)
    cases=0
    for base in (0x20000,0x31000):
        m=Machine(raw,labels,base)
        front0=m.page(0); back1=m.page(1)
        assert m.call('restore')==0; cases+=1
        assert m.call('bind')==1; cases+=1
        assert m.root()[SROOT['bytes']//4]==PAGE_SIZE
        assert m.alloc_calls==[(PAGE_SIZE,0x10001)]*2
        assert m.call('restore')==0; cases+=1
        assert m.call('capture')==1; cases+=1
        assert m.root()[SROOT['valid']//4]==2
        assert bytes(m.uc.mem_read(SNAP1,PAGE_SIZE))==back1
        m.rewrite_page(1,0xee)
        assert m.call('restore')==1; cases+=1
        assert m.page(1)==back1 and m.page(0)==front0
        assert m.call('bind')==1 and len(m.alloc_calls)==2;cases+=1
        # Now page 1 is front, page 0 is back; only page 0 is saved.
        m.put(DB+8,1)
        assert m.call('restore')==0;cases+=1
        assert m.call('capture')==1;cases+=1
        assert m.root()[SROOT['valid']//4]==3
        assert bytes(m.uc.mem_read(SNAP0,PAGE_SIZE))==front0
        m.rewrite_page(0,0xfd)
        assert m.call('restore')==1;cases+=1
        assert m.page(0)==front0 and m.page(1)==back1
        # A page that is no longer back cannot be touched.
        m.put(DB+20,1)
        m.rewrite_page(0,0x55)
        assert m.call('capture')==0;cases+=1
        assert m.call('restore')==0;cases+=1
        assert m.page(0)==bytes([0x55])*PAGE_SIZE
        m.put(DB+20,0)
        assert m.call('restore')==1;cases+=1
        assert m.page(0)==front0
        assert m.call('close',owner=OTHER)==0;cases+=1
        assert not m.free_calls
        assert m.call('close')==1 and len(m.free_calls)==2;cases+=1
        assert not m.allocations
        assert m.call('close')==1 and len(m.free_calls)==2;cases+=1
        assert m.call('restore')==0;cases+=1

        t=Machine(raw,labels,base);t.fail_alloc=2
        assert t.call('bind')==0 and len(t.free_calls)==1;cases+=1
        assert t.root()[:7]==(0,)*7
        assert not t.allocations
        t=Machine(raw,labels,base);t.fail_alloc=1
        assert t.call('bind')==0 and t.root()[:7]==(0,)*7;cases+=1
        assert not t.allocations
        t=Machine(raw,labels,base)
        t.put(DB+20,1)
        assert t.call('bind')==0 and t.alloc_calls==[];cases+=1
        t=Machine(raw,labels,base)
        t.set_geometry(BMP1,(PLANE10,PLANE11),bpr=6)
        assert t.call('bind')==0 and t.alloc_calls==[];cases+=1
        t=Machine(raw,labels,base)
        t.set_geometry(BMP1,(PLANE10,PLANE11),depth=3)
        assert t.call('bind')==0 and t.alloc_calls==[];cases+=1
        # Different BitMap objects must not share even ONE physical plane.
        t=Machine(raw,labels,base)
        t.set_geometry(BMP1,(PLANE00,PLANE11))
        before=(t.page(0),t.page(1))
        assert t.call('bind')==0 and not t.alloc_calls;cases+=1
        assert (t.page(0),t.page(1))==before
        # Also reject PARTIALLY overlapping, not just identical pointers.
        t=Machine(raw,labels,base)
        t.set_geometry(BMP1,(PLANE00+2,PLANE11))
        assert t.call('bind')==0 and not t.alloc_calls;cases+=1
        # A failed capture makes an older snapshot unusable.
        t=Machine(raw,labels,base)
        assert t.call('bind')==1
        assert t.call('capture')==1
        assert t.root()[SROOT['valid']//4]==2
        t.set_geometry(BMP1,(PLANE10+1,PLANE11))
        assert t.call('capture')==0;cases+=1
        assert t.root()[SROOT['valid']//4]==0
        assert t.call('restore')==0;cases+=1
        assert t.call('close')==1
        t=Machine(raw,labels,base)
        assert t.call('bind')==1
        t.set_geometry(BMP1,(PLANE10,PLANE11),rows=3)
        assert t.call('capture')==0;cases+=1
        assert t.call('restore')==0;cases+=1
        assert t.call('close')==1
        t=Machine(raw,labels,base)
        assert t.call('bind')==1
        assert t.call('capture')==1
        t.put(DB+4,SB0)
        assert t.call('restore')==0;cases+=1
        assert t.call('close')==1
        t=Machine(raw,labels,base)
        t.uc.mem_write(EXEC+0x128,pack('>H',0))
        assert t.call('bind')==0 and not t.alloc_calls;cases+=1
    print('M19 B8 PRIVATE page manager MC68020 Gate A PASS',cases,
          'cases, 2 relocations, mocks; NO new Lib, AMOS token or WinUAE Gate')


if __name__=='__main__':main()
