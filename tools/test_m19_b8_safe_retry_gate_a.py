#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 B8 S1 bounded WaitTOF Clear regression, two relocated native units.

Runs the ORIGINAL Clear validator, Safe/GetMsg/WaitBlit, real planar CPU
copy, B7 foreign-owner guards, and NEW wrapper on Unicorn 68020.
Models graphics.library/WaitTOF and delivery of SafePort signal only.
Not a real WinUAE or AMOS Compiler Gate B/C.
"""
from __future__ import annotations
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020

from m19_b8_safe_retry_emit import emit_b8_safe_retry,MAX_SAFE_VBLS
from m19_b8_first_update_emit import emit_b8_first_update
from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
from test_m19_b8_clear_update_tx_gate_a import TxMachine,B7_A,B7_B
from test_m19_b8_safe_lifecycle_gate_a import GRAPHICS
from test_m19_b8_page_manager_gate_a import (
    OWNER,OTHER,STATE,DB,SNAP1,PAGE_SIZE,AR,DR
)
from m19_p0j_swap_barrier_emit import READY,DIRTY
from m19_b8_page_manager_emit import R as SERVICE

class LatencyMachine(TxMachine):
    def __init__(self,code,labels,base,b7base):
        self.tof_count=0
        self.deliver_at=None
        super().__init__(code,labels,base,b7base)
        self.uc.hook_add(UC_HOOK_CODE,self.wait_tof,
                         begin=GRAPHICS-270,end=GRAPHICS-270)

    def wait_tof(self,uc,addr,size,ctx):
        assert uc.reg_read(AR[6])==GRAPHICS, 'WaitTOF GfxBase ABI'
        assert self.get(DB+20)&1, 'WaitTOF without Safe pending'
        self.tof_count+=1
        if self.deliver_at is not None and self.tof_count>=self.deliver_at:
            self.safe_available=True
        sp=uc.reg_read(AR[7])
        ret=int.from_bytes(uc.mem_read(sp,4),'big')
        uc.reg_write(AR[7],sp+4)
        # Model library-clobbered scratch registers; wrapper must survive.
        uc.reg_write(DR[0],0xbaad1111)
        uc.reg_write(DR[1],0xbaad2222)
        uc.reg_write(AR[0],0xbaad3333)
        uc.reg_write(AR[1],0xbaad4444)
        uc.reg_write(UC_M68K_REG_PC,ret)


def ready_snap(code,labels,base,b7base):
    m=LatencyMachine(code,labels,base,b7base)
    assert m.call('bind')==1
    assert m.call('update_prepare')==1
    m.set_guard(READY)
    assert m.call('update_finish')==1
    assert m.root()[SERVICE['valid']//4]==2
    return m


def main():
    candidate,meta=build_b8_safe_retry()
    assert len(candidate)>115744 and meta['predecessor_sha']==(
        '00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae')
    assert meta['public_commands']==88 and meta['ap20_entries']==184
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['pc16_max']<32766 and meta['wait_tof_max']==3
    old,_=emit_b8_first_update()
    raw,labels=emit_b8_safe_retry()
    assert raw.startswith(old) and labels['b8_service_clear_wait_safe_entry']==len(old)
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(raw[len(old):],0x10000+len(old)))
    assert ins and sum(i.size for i in ins)==len(raw)-len(old)
    assert not any(i.mnemonic.startswith('dc.') for i in ins)

    checks=9
    for base,b7base in ((0x20000,B7_A),(0x31000,B7_B)):
        # A message arriving after exactly one/two/three vertical blanks.
        for latency in (1,2,3):
            m=ready_snap(raw,labels,base,b7base)
            front=m.page(0)
            oldback=m.page(1)
            initial_blits=m.waitblit_count
            m.rewrite_page(1,0xa5)
            m.put(DB+20,3)  # Pending Safe + unrelated Disp bit.
            m.deliver_at=latency
            assert m.call('clear_wait_safe')==1
            assert m.tof_count==latency
            assert m.getmsg_count==latency+1
            assert m.waitblit_count==initial_blits+1
            assert m.page(1)==oldback and m.page(0)==front
            assert m.g('status')==0 and m.get(DB+20)==2
            assert m.root()[SERVICE['valid']//4]==2
            # Subsequent Update must see decorations added AFTER Clear.
            m.rewrite_page(1,0x73)
            edited=m.page(1)
            assert m.call('update_prepare')==1
            assert bytes(m.uc.mem_read(SNAP1,PAGE_SIZE))==edited
            m.set_guard(READY)
            assert m.call('update_finish')==1
            assert m.page(0)==front
            assert m.call('close')==1 and len(m.free_calls)==2
            checks+=12

        # Permanently absent Safe: exactly three waits, zero pixel copies,
        # fail DIRTY. Later delivered Safe permits recovery through Clear.
        t=ready_snap(raw,labels,base,b7base)
        oldfront=t.page(0)
        t.rewrite_page(1,0xaa)
        dirtyback=t.page(1)
        t.put(DB+20,1)
        assert t.call('clear_wait_safe')==0
        assert t.tof_count==MAX_SAFE_VBLS and t.getmsg_count==MAX_SAFE_VBLS+1
        assert t.waitblit_count==1  # preflight's initial capture waited for Blitter
        assert t.page(0)==oldfront and t.page(1)==dirtyback
        assert t.g('status')==DIRTY and t.root()[SERVICE['valid']//4]==2
        t.safe_available=True
        assert t.call('clear_wait_safe')==1
        assert t.g('status')==0 and t.page(0)==oldfront
        checks+=7

        # No snapshot => no waiting and no copy, even if Safe pending.
        n=LatencyMachine(raw,labels,base,b7base)
        assert n.call('bind')==1
        n.put(DB+20,1)
        assert n.call('clear_wait_safe')==0 and n.tof_count==0
        assert n.getmsg_count==0 and n.waitblit_count==0
        checks+=3

        # Owner mismatch must never consume Safe or wait for VBL.
        x=ready_snap(raw,labels,base,b7base)
        x.put(DB+20,1)
        assert x.call('clear_wait_safe',owner=OTHER)==0
        assert x.tof_count==0 and x.getmsg_count==0
        checks+=2

        # Missing graphics.library: no indirect jump and no false success.
        y=ready_snap(raw,labels,base,b7base)
        y.put(DB+20,1)
        y.put(STATE+8,0)
        assert y.call('clear_wait_safe')==0
        assert y.tof_count==0 and y.getmsg_count==0
        checks+=3

        # A non-Safe failure while pending bit is already clear must not
        # be hidden by timing retries or change the front buffer.
        z=ready_snap(raw,labels,base,b7base)
        z.put(OWNER+0x1d0,0x123450) # foreign End callback
        assert z.call('clear_wait_safe')==0
        assert z.tof_count==0 and z.getmsg_count==0
        checks+=2

        # No Safe pending => no unnecessary VBL waits in normal frame loop.
        q=ready_snap(raw,labels,base,b7base)
        assert q.call('clear_wait_safe')==1
        assert q.tof_count==0 and q.getmsg_count==0
        checks+=2

    print('M19 B8 S1 SAFE WAITTOF MC68020 Gate A PASS',checks,
          'checks, 2 placements, bounded retry 1/2/3 VBL, fail closed')
    print('B8S1_IMAGE',meta)

if __name__=='__main__':
    main()
