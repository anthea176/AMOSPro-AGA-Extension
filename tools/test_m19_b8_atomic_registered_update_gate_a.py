#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""B8 atomic REGISTERED Update MC68020 stage plus B7 Draw call Gate A.

Real emitted fifth-unit source is executed under Unicorn M68020 on two
independent placements. The original B7 Draw wrapper bytes and the
checked B7 End marker are in memory and verified by the MC68020 code.
A code hook MODELS the B7 Draw return/pixels so the B8 atomic control
flow, register ABI, snapshot order, and fail/abort can be discriminated.

This does NOT model first registration/bootstrap, AMOS Compiler, actual
B7 painting inside this particular test, or real WinUAE. The existing
60-case B7 native Gate A runs separately for actual B7 Close/Draw/End.
"""
from __future__ import annotations

from struct import pack
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020

from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update
from m19_b8_clear_update_tx_emit import emit_b8_clear_update_tx
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_b8_page_manager_emit import R as SROOT
from m19_p0j_swap_barrier_emit import DIRTY,READY
from build_m19_b8_atomic_registered_update_in_memory import build_b8_atomic_registered_update
from test_m19_b8_clear_update_tx_gate_a import TxMachine,B7_A,B7_B
from test_m19_b8_page_manager_gate_a import DR,AR,DB,OWNER,OTHER,SNAP0,SNAP1,PAGE_SIZE


class AtomicMachine(TxMachine):
    def __init__(self,raw,labels,base,b7base):
        super().__init__(raw,labels,base,b7base)
        _, b7=emit_b8_b7_hooks()
        self.draw_address=b7base+b7['b8_b7_draw_trampoline_entry']
        self.draw_result=1
        self.draw_calls=0
        self.draw_snapshot=[]
        self.uc.hook_add(UC_HOOK_CODE,self.b7_draw_mock,
                         begin=self.draw_address,end=self.draw_address)

    def b7_draw_mock(self,uc,address,size,ctx):
        # B8 Prepare must finish preflight and background capture BEFORE
        # B7 first obtains the CPU to modify a single destination plane.
        back=1 if self.get(DB+8)==0 else 0
        assert self.uc.reg_read(AR[2])==0x210200, (
            'B7 Draw received mutated AMOS A2 input',
            hex(self.uc.reg_read(AR[2])))
        assert self.g('status')==0,'B7 Draw called while DIRTY'
        valid=self.root()[SROOT['valid']//4]
        bit=1 if back==0 else 2
        assert valid&bit and self.tx('pending')==bit,('Draw before capture',valid,bit)
        assert self.preflight_calls==self.draw_calls+1
        snapshot=bytes(self.uc.mem_read(SNAP1 if back else SNAP0,PAGE_SIZE))
        self.draw_snapshot.append((back,snapshot,self.page(back)))
        assert snapshot==self.page(back)
        self.draw_calls+=1
        self.rewrite_page(back,0x80+self.draw_calls)
        self.set_guard(READY if self.draw_result else DIRTY)
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[2],0)
        uc.reg_write(DR[3],self.draw_result)
        uc.reg_write(UC_M68K_REG_PC,ret)


def main():
    candidate,meta=build_b8_atomic_registered_update()
    assert candidate and meta['public_commands']==86
    assert meta['ap20_entries']==182 and meta['native_groups']==[142,153,156,177,181]
    assert meta['new_pc16_max']<32766 and meta['requires_b7_end_registration']
    raw,labels=emit_b8_atomic_registered_update()
    old,_=emit_b8_clear_update_tx()
    assert raw.startswith(old)
    code=raw[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(code,0x10000+len(old)))
    assert ins and sum(x.size for x in ins)==len(code)
    cases=0
    for base,b7base in ((0x20000,B7_A),(0x31000,B7_B)):
        m=AtomicMachine(raw,labels,base,b7base)
        front=m.page(0); old_back=m.page(1)
        assert m.call('update_atomic_registered')==0;cases+=1
        assert not m.draw_calls and m.page(0)==front
        assert m.call('bind')==1;cases+=1
        assert m.call('update_atomic_registered',owner=OTHER)==0;cases+=1
        assert m.call('update_atomic_registered')==1;cases+=1
        assert m.draw_calls==1 and m.preflight_calls==1;cases+=1
        assert m.draw_snapshot[0]==(1,old_back,old_back)
        assert m.g('status')==READY and m.tx('pending')==0
        assert m.page(0)==front and m.page(1)!=old_back;cases+=1
        # Physical back becomes a front; Clear must never touch it.
        m.put(DB+8,1)
        m.set_guard(0) # the existing guarded Swap executed in earlier B7 Gate A
        assert m.call('update_atomic_registered')==1;cases+=1
        assert m.draw_calls==2 and m.preflight_calls==2
        assert m.draw_snapshot[1]==(0,front,front)
        assert m.root()[SROOT['valid']//4]==3;cases+=1
        assert m.g('status')==READY
        # Clear back AFTER returning to original front: the exact
        # snapshot, not a default fill, restores the prior background.
        m.put(DB+8,0)
        m.set_guard(0)
        assert m.call('clear_guard')==1;cases+=1
        assert m.page(1)==old_back;cases+=1
        # Explicit dynamic decoration after Clear is captured without
        # being overwritten by a stale auto-restore.
        m.rewrite_page(1,0x47)
        dynamic=m.page(1)
        assert m.call('update_atomic_registered')==1;cases+=1
        assert m.draw_snapshot[-1]==(1,dynamic,dynamic)
        assert m.g('status')==READY;cases+=1
        assert m.call('close')==1 and len(m.free_calls)==2;cases+=1

        # B7 Draw failure AFTER saving background must call Abort and
        # keep persistent B7 DIRTY, preserving a recoverable snapshot.
        n=AtomicMachine(raw,labels,base,b7base)
        assert n.call('bind')==1
        old=n.page(1)
        n.draw_result=0
        assert n.call('update_atomic_registered')==0;cases+=1
        assert n.draw_calls==1 and n.preflight_calls==1
        assert n.g('status')==DIRTY and n.tx('pending')==0;cases+=1
        assert n.root()[SROOT['valid']//4]==2
        assert n.page(0)==front and n.page(1)!=old
        assert n.call('clear_guard')==1;cases+=1
        assert n.g('status')==0 and n.page(1)==old;cases+=1
        assert n.call('close')==1

        # AGBO preflight failure must abort BEFORE any snapshot DMA.
        p=AtomicMachine(raw,labels,base,b7base)
        assert p.call('bind')==1
        p.preflight_result=0
        back=p.page(1)
        assert p.call('update_atomic_registered')==0;cases+=1
        assert p.preflight_calls==1 and p.draw_calls==0;cases+=1
        assert p.root()[SROOT['valid']//4]==0 and p.page(1)==back
        assert p.g('status')==DIRTY;cases+=1
        assert p.call('close')==1

        # A changed B7 Draw prologue must be denied before any B8 copy.
        t=AtomicMachine(raw,labels,base,b7base)
        assert t.call('bind')==1
        t.uc.mem_write(t.draw_address,b'\x4e\x71\x4e\x71')
        assert t.call('update_atomic_registered')==0;cases+=1
        assert t.preflight_calls==0 and t.draw_calls==0
        assert t.root()[SROOT['valid']//4]==0;cases+=1
        assert t.call('close')==1

        # Foreign End callback cannot be used to derive native B7 Draw.
        t=AtomicMachine(raw,labels,base,b7base)
        assert t.call('bind')==1
        t.put(OWNER+0x1d0,0x123450)
        assert t.call('update_atomic_registered')==0;cases+=1
        assert not t.draw_calls and t.g('status')==0;cases+=1
        assert t.call('close')==1
    print('M19 B8 ATOMIC REGISTERED UPDATE MC68020 Gate A PASS',
          cases,'cases, 2 relocations; B7 Draw CPU HOOK MODELED, no first bootstrap')
    print('AP20_SOURCE_ONLY',meta)


if __name__=='__main__':main()
