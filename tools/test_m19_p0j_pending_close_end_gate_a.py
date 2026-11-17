#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b6 source-only Close/End pending Safe/Disp DIAGNOSTIC.

Execute genuine R88 AGA Close/End instructions through the B5/B6 BOBS
bridge in MC68020 Unicorn. OS libraries, GetMsg and hardware are mocked.
Expose (rather than conceal) the B6 guard-state lifecycle gap on End.
NO new native code, no active Lib/ASC and no real WinUAE/Compiler proof.
"""
from __future__ import annotations

from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from test_m5_generic import DR, AR, AMOS, EXEC, GFX, INTUI, STACK, STOP
from test_m19_p0j_swap_barrier_gate_a import BarrierMachine, prepare, DB, SAFE, DISP
from m19_p0j_swap_barrier_emit import DIRTY, READY
from build_m19_p0j_public_draw_in_memory import build

class PendingMachine(BarrierMachine):
    def __init__(self, source, layout):
        super().__init__(source,layout)
        self.safe_after = None
        self.disp_after = None
        self.safe_count = 0
        self.disp_count = 0
        self.safe_received = False
        self.disp_received = False
        self.waittof_count = 0
        self.free_ports = []
        self.free_screens = []
        self.reply_count = 0
        self.flag_at_free = []

    def os_call(self, uc, address, size, user):
        if address == EXEC-372:
            port = self.a(0)
            if port == SAFE:
                self.safe_count += 1
                deliver = (not self.safe_received and self.safe_after is not None
                           and self.safe_count >= self.safe_after)
                if deliver: self.safe_received = True
                return self._os_return(SAFE+0x100 if deliver else 0)
            if port == DISP:
                self.disp_count += 1
                deliver = (not self.disp_received and self.disp_after is not None
                           and self.disp_count >= self.disp_after)
                if deliver: self.disp_received = True
                return self._os_return(DISP+0x100 if deliver else 0)
        if address == GFX-270:
            self.waittof_count += 1
            return self._os_return(0)
        if address == EXEC-378 and self.a(1) in (SAFE+0x100, DISP+0x100):
            self.reply_count += 1
            raise AssertionError('Safe/Disp messages have already been replied by OS')
        if address == INTUI-774:
            self.flag_at_free.append(self.get(DB+20))
            assert self.get(DB+20)==0,'FreeScreenBuffer before Safe/Disp'
            self.free_screens.append(self.a(1))
        if address == EXEC-672:
            self.flag_at_free.append(self.get(DB+20))
            assert self.get(DB+20)==0,'DeleteMsgPort before Safe/Disp'
            self.free_ports.append(self.a(0))
        return super().os_call(uc,address,size,user)

    def invoke_callback(self,slot=0x1cc,limit=8000000):
        target=self.get(AMOS+slot)
        for n,r in enumerate(DR): self.uc.reg_write(r,0x1230+n)
        for n,r in enumerate(AR[:7]): self.uc.reg_write(r,0x40000+n*0x100)
        self.uc.reg_write(AR[5],AMOS)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(target,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('B6 End CPU020 fault',str(exc),
                    hex(self.uc.reg_read(UC_M68K_REG_PC)),hex(target),
                    self.events[-25:],hex(self.get(DB+20)))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for r,v in before.items():
            assert self.uc.reg_read(r)==v,('End ABI',r)
        return self.events

def ready(layout):
    # Same actual native B5 source, replace only the OS reply fixture.
    from build_m19_p0c_screen_close_in_memory import build as build_p0c
    src,_=build_p0c()
    m=PendingMachine(src,layout)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.mask(True,1,0)==1
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    m.activate_aga_state()
    m.configure_real_state()
    m.put(DB+12,SAFE)
    m.put(DB+16,DISP)
    m.put(DB+20,0)
    m.safe=True
    assert m.run_select(10)==1
    assert m.public('bob',ident=1,x=5,y=7,image=1)==1
    assert m.run_select(11)==1
    assert m.public('bob',ident=2,x=9,y=11,image=1)==1
    assert m.frame()==1
    assert m.status()==READY
    assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
    assert m.get(AMOS+0x1d0)==m.entry+m.labels['program_end_bridge_entry']
    m.put(DB+20,3)
    assert m.frame()==0
    assert m.status()==DIRTY
    return m

def main():
    _,meta=build()
    assert meta['public_commands']==86 and meta['ap20_entries']==181
    checks=0
    for layout in ('interpreted','compiled'):
        # Missing replies: bounded WaitTOF, screen+ports preserved, no
        # ReplyMsg, B5 DIRTY latch persists across failed Close.
        m=ready(layout)
        m.invoke_guard('close')
        assert m.get(m.real_state)==m.screen
        assert m.get(m.real_state+32)==DB
        assert m.get(DB+20)==3
        assert not m.free_ports and not m.free_screens
        assert m.status()==DIRTY
        assert 299<=m.waittof_count<=302
        assert m.reply_count==0
        checks+=7

        # When replies eventually arrive, a second Close may run the
        # *real native* cleanup. Every notification is consumed once.
        m.safe_after=m.safe_count+2
        m.disp_after=m.disp_count+4
        m.invoke_guard('close')
        assert m.safe_received and m.disp_received
        assert m.get(DB+20)==0
        assert m.get(m.real_state)==0
        assert m.status()==0
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        assert not any(m.flag_at_free) and m.reply_count==0
        checks+=6

        # Separate End callback with unreceived notifications. P0c must
        # not run destructive old End; after replies, End closes, but B6
        # (NOT YET fixed) has no guard reset callback for the Draw latch.
        m=ready(layout)
        m.invoke_callback(0x1cc)
        assert m.get(DB+20)==3 and m.get(m.real_state)==m.screen
        assert not m.free_ports and not m.free_screens
        assert 299<=m.waittof_count<=302
        assert m.reply_count==0
        assert m.status()==DIRTY
        checks+=5

        m.safe_after=m.safe_count+1
        m.disp_after=m.disp_count+2
        m.invoke_callback(0x1d0)
        assert m.get(DB+20)==0 and m.get(m.real_state)==0
        assert len(m.free_screens)==2 and len(m.free_ports)==2
        # Documented B6 defect: End bypasses guarded_close_entry and does
        # not reset its stale DIRTY latch, even though the screen is closed.
        assert m.status()==DIRTY,'B6 lifecycle changed: re-audit End contract'
        assert m.reply_count==0
        checks+=4

    print('M19 P0j-b6 NATIVE PENDING CLOSE/END DIAGNOSTIC PASS',
          checks,'checks; bounded WaitTOF and no premature SB/port frees;',
          'IDENTIFIED GAP: successful End leaves B5 frame latch DIRTY;',
          'actual R88 native, OS MOCKED; B7 needed before runtime gates')

if __name__=='__main__':
    main()
