#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 private Clear/Update stages: real emitted MC68020 CPU Gate A.

The actual stage/copy/pool/Safe machine code is executed under Unicorn
in two relocated fifth-unit placements, with a byte-exact B7-m2 native
shim and frame-guard DATA loaded at a disjoint mock address. The B7
64-image preflight, Draw and public Swap are modeled as caller actions
here; their native implementation is separately tested by B7 Gate A.
These tests DO NOT validate public AMOS tokens, DMA or real Compiler.
"""
from __future__ import annotations

from struct import pack
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from m19_b8_clear_update_tx_emit import emit_b8_clear_update_tx,R as TX
from m19_b8_cross_unit_arm_emit import emit_b8_cross_unit_arm
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_p0j_swap_barrier_emit import G as GUARD,DIRTY,READY
from m19_b8_page_manager_emit import R as SERVICE
from build_m19_b8_clear_update_tx_in_memory import build_b8_clear_update_tx
from test_m19_b8_safe_lifecycle_gate_a import SafeMachine
from test_m19_b8_page_manager_gate_a import (
    OWNER,OTHER,STATE,DB,SCREEN,SNAP0,SNAP1,PAGE_SIZE,AR,DR,
)

B7_A=0x300000
B7_B=0x350000

class TxMachine(SafeMachine):
    def __init__(self,code,labels,base,b7base):
        super().__init__(code,labels,base)
        b7,b7labels=emit_b8_b7_hooks()
        self.uc.mem_write(b7base,b7)
        self.regions.append((b7base,b7base+len(b7)))
        self.b7base=b7base
        self.b7guard=b7base+b7labels['frame_guard_state']
        self.b7shim=b7base+b7labels['b8_b7_end_trampoline_entry']
        self.b7preflight=b7base+b7labels['image_frame_preflight_entry']
        self.preflight_result=1
        self.preflight_calls=0
        self.preflight_states=[]
        # Keep the EXACT compiled B7 native code/signature in memory.
        # The B7 bank fixture is deliberately stubbed in this B8 test;
        # the independently validated B7 native preflight tests supply
        # its full AGBO/64-ID CPU coverage.
        self.uc.hook_add(UC_HOOK_CODE,self.mock_b7_preflight,
                         begin=self.b7preflight,end=self.b7preflight)
        self.put(OWNER+0x1cc,self.b7shim)
        self.put(OWNER+0x1d0,self.b7shim)
        self.uc.mem_write(self.b7guard,bytes(24))

    def mock_b7_preflight(self,uc,addr,size,ctx):
        self.preflight_calls+=1
        self.preflight_states.append((
            self.root()[SERVICE['valid']//4],self.g('status'),self.page(1)))
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        uc.reg_write(DR[2],0)
        uc.reg_write(DR[3],self.preflight_result)
        uc.reg_write(UC_M68K_REG_PC,ret)

    def g(self,field):
        return self.get(self.b7guard+GUARD[field])

    def set_guard(self,status,*,front=None):
        self.put(self.b7guard+GUARD['status'],status)
        if status:
            self.put(self.b7guard+GUARD['owner'],OWNER)
            self.put(self.b7guard+GUARD['state'],STATE)
            self.put(self.b7guard+GUARD['db'],DB)
            self.put(self.b7guard+GUARD['front'],self.get(DB+8) if front is None else front)
            self.put(self.b7guard+GUARD['screen'],SCREEN)
        else:
            self.uc.mem_write(self.b7guard,bytes(24))

    def tx(self,field):
        return self.get(self.base+self.labels['b8_tx_root']+TX[field])


def main():
    image,meta=build_b8_clear_update_tx()
    assert image and meta['commands']==86 and meta['ap20_entries']==182
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['new_pc16_max']<32766 and meta['no_amos_tokens']
    raw,labels=emit_b8_clear_update_tx()
    prev,_=emit_b8_cross_unit_arm()
    assert raw.startswith(prev) and len(raw)>len(prev)
    section=raw[len(prev):labels['b8_tx_root']]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(section,0x10000+len(prev)))
    assert ins and sum(x.size for x in ins)==len(section)
    cases=0
    for base,b7base in ((0x20000,B7_A),(0x31000,B7_B)):
        m=TxMachine(raw,labels,base,b7base)
        front=m.page(0); old_back=m.page(1)
        # Unallocated or unregistered private service must do nothing.
        assert m.call('clear_guard')==0;cases+=1
        assert m.call('bind')==1;cases+=1
        assert m.call('clear_guard',owner=OTHER)==0;cases+=1
        assert m.page(1)==old_back and m.g('status')==0
        # No first-snapshot Clear: latch DIRTY, refuse Swap, require Close
        # or a new previously valid capture on a clean screen.
        assert m.call('clear_guard')==0;cases+=1
        assert m.g('status')==DIRTY
        m.set_guard(0)  # model fresh screen initialization before first Update
        assert m.call('update_prepare')==1;cases+=1
        assert m.preflight_calls==1
        assert m.preflight_states[0][:2]==(0,0)
        assert m.g('status')==0 and m.tx('pending')==2
        assert bytes(m.uc.mem_read(SNAP1,PAGE_SIZE))==old_back
        assert m.call('update_prepare')==0;cases+=1
        assert m.g('status')==DIRTY
        # Transaction failure before Draw: Clear can recover using exact page.
        assert m.call('clear_guard')==1;cases+=1
        assert m.g('status')==0 and m.tx('cleared')==2
        assert m.call('update_prepare')==1;cases+=1
        assert m.tx('pending')==2
        # Simulate the already-source-proven B7 Draw setting READY atomically.
        m.set_guard(READY)
        assert m.call('update_finish')==1;cases+=1
        assert m.g('status')==READY and m.tx('pending')==0
        assert m.tx('cleared')==0
        assert m.call('update_finish')==0;cases+=1
        assert m.g('status')==DIRTY
        # Exactly the page's own snapshot is restored, never the front.
        m.rewrite_page(1,0xee)
        assert m.call('clear_guard')==1;cases+=1
        assert m.page(1)==old_back and m.page(0)==front
        assert m.tx('cleared')==2 and m.g('status')==0
        # Background explicitly edited after Clear must not be wiped
        # by Update's implicit old-background restoration.
        m.rewrite_page(1,0x42)
        new_background=m.page(1)
        assert m.call('update_prepare')==1;cases+=1
        assert m.page(1)==new_background
        assert bytes(m.uc.mem_read(SNAP1,PAGE_SIZE))==new_background
        m.set_guard(READY)
        assert m.call('update_finish')==1;cases+=1
        assert m.page(0)==front
        assert m.tx('cleared')==0 and m.tx('pending')==0
        # Safe pending: no pixel writes and DIRTY stays latched.
        m.put(DB+20,3)
        assert m.call('update_prepare')==0;cases+=1
        assert m.g('status')==DIRTY
        assert m.page(1)==new_background and m.page(0)==front
        assert m.get(DB+20)==3
        m.put(DB+20,0)
        assert m.call('clear_guard')==1;cases+=1
        assert m.g('status')==0
        # Verify guard identity before *any* copy on a stale page.
        m.set_guard(READY)
        m.put(DB+8,1)
        assert m.call('clear_guard')==0;cases+=1
        assert m.g('status')==READY
        m.set_guard(0) # models a successful guarded Swap
        assert m.call('update_prepare')==1;cases+=1
        assert bytes(m.uc.mem_read(SNAP0,PAGE_SIZE))==front
        assert m.tx('pending')==1
        # A swap between prepare and finish must not create READY.
        m.put(DB+8,0)
        m.set_guard(READY)
        assert m.call('update_finish')==0;cases+=1
        assert m.g('status')==DIRTY
        assert m.call('update_abort')==0;cases+=1 # Abort intentionally never reports frame success
        assert m.g('status')==DIRTY and m.tx('pending')==0
        assert m.call('clear_guard')==1;cases+=1
        assert m.g('status')==0
        # Restore to the wrong physical page is never permitted.
        m.put(OWNER+0x1d0,0x123450)
        assert m.call('clear_guard')==0;cases+=1
        assert m.page(0)==front
        m.put(OWNER+0x1d0,m.b7shim)
        # Real post-Close does not call a separate transaction reset
        # (B7/5th hooks own only the CPU pool). Rebind to the SAME screen
        # addresses MUST invalidate the old transaction epoch implicitly.
        old_epoch=m.tx('epoch')
        assert m.call('close')==1;cases+=1
        assert len(m.free_calls)==2
        assert m.tx('owner')==OWNER and m.tx('epoch')==old_epoch
        m.set_guard(0)  # already-validated B7 Close reset, then fresh Open
        m.next_alloc=0
        assert m.call('bind')==1;cases+=1
        assert m.root()[SERVICE['valid']//4]==0
        assert m.root()[SERVICE['epoch']//4]!=old_epoch
        assert m.call('update_prepare')==1;cases+=1
        assert m.tx('epoch')==m.root()[SERVICE['epoch']//4]
        assert m.tx('cleared')==0 and m.tx('pending')==2;cases+=1
        # A forged/changing epoch is NEVER allowed to discard a LIVE
        # snapshot, even when the prior owner and Screen still match.
        fake=TxMachine(raw,labels,base,b7base)
        assert fake.call('bind')==1
        assert fake.call('update_prepare')==1
        old_tx_epoch=fake.tx('epoch')
        root_addr=fake.base+fake.labels['b8_service_root']
        fake.put(root_addr+SERVICE['epoch'],old_tx_epoch+1)
        assert fake.call('update_prepare')==0;cases+=1
        assert fake.tx('epoch')==old_tx_epoch
        assert fake.tx('pending')==2 and fake.root()[SERVICE['valid']//4]==2
        assert fake.call('close')==1
        # A stale/missing AGBO image is refused by B7 preflight BEFORE
        # the first snapshot/copy. Here B7's preflight result is mocked;
        # its actual 64-object native implementation has an independent Gate A.
        bad=TxMachine(raw,labels,base,b7base)
        assert bad.call('bind')==1
        unchanged=bad.page(1)
        bad.preflight_result=0
        assert bad.call('update_prepare')==0;cases+=1
        assert bad.preflight_calls==1;cases+=1
        assert bad.root()[SERVICE['valid']//4]==0;cases+=1
        assert bad.page(1)==unchanged and bad.g('status')==DIRTY;cases+=1
        assert bad.call('close')==1
        assert bad.call('tx_reset')==1

        # Unexpected owner cannot mutate state or release snapshots.
        before=m.tx('pending')
        assert m.call('update_abort',owner=OTHER)==0;cases+=1
        assert m.tx('pending')==before
        assert m.call('close')==1;cases+=1
        assert m.call('tx_reset')==1;cases+=1
    print('M19 B8 Clear/Update PRIVATE STAGES MC68020 Gate A PASS',
          cases,'checks, 2 relocations; B7 Draw/Swap MODELED, OS MOCKED')
    print('AP20_SOURCE_ONLY',meta)

if __name__=='__main__': main()
