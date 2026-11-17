#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b7 MC68020 Gate A: actual native End + Safe/Disp pending.

Two disjoint AP20 native placements, source-pinned R88 AGA Close/End
machine code executed. Exec/Intuition/Gfx and DMA are MOCKED. No true
AMOS Compiler, WinUAE or material hardware proof.
"""
from __future__ import annotations

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from test_m5_generic import AMOS
from test_m19_p0j_pending_close_end_gate_a import (
    PendingMachine,ready,DB,SAFE,DISP,
)
from test_m19_p0j_swap_barrier_gate_a import DIRTY,READY
from m19_p0j_swap_barrier_emit import emit_swap_barrier
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle
from build_m19_p0j_end_lifecycle_in_memory import build
from compiler_relocation import unpack_ap20
from amos_link_test_support import relocate


class LifecycleMachine(PendingMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.native,self.labels=emit_end_lifecycle()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['b7_guarded_draw_entry']

    def end_callback(self):
        return self.entry+self.labels['b7_end_entry']

    def callbacks(self):
        return self.get(AMOS+0x1cc),self.get(AMOS+0x1d0)


def main():
    candidate,meta=build()
    old,_=emit_swap_barrier()
    new,labels=emit_end_lifecycle()
    assert new.startswith(old)
    assert meta['public_commands']==86 and meta['ap20_entries']==181
    assert meta['native_groups']==[142,153,156,177]
    assert meta['pc16_max']<32766
    assert meta['guarded_draw_stub']==180 and meta['guarded_draw_group']==177
    assert len(candidate)==meta['size']
    _,parts,_=unpack_ap20(candidate)
    assert parts[177].endswith(new)
    tail=new[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(tail,0x120000+len(old)))
    assert ins and sum(i.size for i in ins)==len(tail)
    assert all(not i.mnemonic.startswith('dc.') for i in ins)
    checks=0

    for layout in ('interpreted','compiled'):
        # Normal public Draw -> native B7 End callback -> real AGA End:
        # all staged Chip freed only once, and frame guard is reset.
        m=ready(layout,cls=LifecycleMachine,inject_failure=False)
        assert m.status()==READY
        assert m.callbacks()==(m.end_callback(),m.end_callback())
        assert m.chip_live
        m.invoke_callback(0x1cc)
        assert m.get(m.real_state)==0 and m.status()==0
        assert not m.chip_live and not m.metadata
        assert m.root()==(0,0)
        assert m.callbacks()==(m.old_end,m.old_end)
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        assert not any(m.flag_at_free) and m.reply_count==0
        before=(len(m.free_screens),len(m.free_ports),len(m.events))
        m.invoke_callback(0x1d0)
        assert len(m.free_screens)==before[0] and len(m.free_ports)==before[1]
        checks+=9

        # Close before End, no double Free even with installed B7 hook.
        m=ready(layout,cls=LifecycleMachine,inject_failure=False)
        assert m.invoke_guard('close')==1
        assert m.get(m.real_state)==0 and m.status()==0
        assert m.callbacks()==(m.end_callback(),m.end_callback())
        m.invoke_callback(0x1d0)
        assert m.callbacks()==(m.old_end,m.old_end)
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        assert not m.chip_live and not m.metadata
        checks+=6

        # Missing notifications: real native End bounded cooperative
        # wait aborts without releasing SB or ports. B7 retains its hook,
        # so a later End retry can finish instead of leaving B6 stale.
        m=ready(layout,cls=LifecycleMachine,inject_failure=True)
        assert m.status()==DIRTY
        assert m.callbacks()==(m.end_callback(),m.end_callback())
        m.invoke_callback(0x1cc)
        assert m.get(m.real_state)==m.screen and m.get(DB+20)==3
        assert not m.free_screens and not m.free_ports
        assert 299<=m.waittof_count<=302
        assert m.status()==DIRTY
        assert m.callbacks()==(m.end_callback(),m.end_callback())
        assert m.reply_count==0
        checks+=7

        m.safe_after=m.safe_count+2
        m.disp_after=m.disp_count+4
        m.invoke_callback(0x1d0)
        assert m.safe_received and m.disp_received
        assert m.get(DB+20)==0 and m.get(m.real_state)==0
        assert m.status()==0
        assert m.callbacks()==(m.old_end,m.old_end)
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        assert not any(m.flag_at_free) and m.reply_count==0
        checks+=6

        # Missing notifications followed by explicit Close instead
        # of End retry. Guarded Close remains the original B5 code.
        m=ready(layout,cls=LifecycleMachine,inject_failure=True)
        m.invoke_guard('close')
        assert m.status()==DIRTY and m.get(m.real_state)==m.screen
        assert not m.free_screens and not m.free_ports
        m.safe_after=m.safe_count+1
        m.disp_after=m.disp_count+3
        m.invoke_guard('close')
        assert m.get(m.real_state)==0 and m.status()==0
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        m.invoke_callback(0x1cc)
        assert m.callbacks()==(m.old_end,m.old_end)
        checks+=6

        # Unexpected third-party End callback may never be silently
        # replaced. If drawing occurred, the final status becomes DIRTY
        # and the normal public Swap must refuse.
        m=ready(layout,cls=LifecycleMachine,inject_failure=False)
        m.put(AMOS+0x1cc,0x123450)
        m.put(AMOS+0x1d0,0x123450)
        assert m.frame()==0
        assert m.status()==DIRTY
        assert m.callbacks()==(0x123450,0x123450)
        assert m.invoke_guard('swap')==0
        assert m.swap_count==0 and m.native_swap_visits==0
        checks+=5

        # Native AGA End signature tampering blocks B7 End arming
        # despite a valid existing End callback.
        m=ready(layout,cls=LifecycleMachine,inject_failure=False)
        original=bytes(m.uc.mem_read(m.old_end,12))
        m.uc.mem_write(m.old_end,b'\x4e\x71\x4e\x71')
        assert m.frame()==0 and m.status()==DIRTY
        assert m.invoke_guard('swap')==0
        assert m.callbacks()==(m.end_callback(),m.end_callback())
        m.uc.mem_write(m.old_end,original)
        m.invoke_callback(0x1cc)
        assert m.status()==0 and m.get(m.real_state)==0
        checks+=5

    print('M19 P0j-b7 MC68020 SAFE/DISP END LIFECYCLE GATE A PASS',
          checks,'checks, two native layouts; real old AGA Close/End;',
          'missing/delayed Safe+Disp, no early frees/no ReplyMsg;',
          'End timeout retains callback, success clears DIRTY;',
          'B6 native/tokens untouched except Draw stub;',
          'OS MOCKED; NO WinUAE/real Compiler/installed Lib')


if __name__=='__main__':
    main()
