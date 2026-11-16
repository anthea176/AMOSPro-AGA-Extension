#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c CPU020: real P0b legacy AGA Screen Close called after BOBS Chip.

Exec/Intuition/graphics are deliberately mocked. The native AGA Screen
Close instructions are the immutable source-pinned P0b group 91 bytes,
NOT a model. The public AP20 stub-8 patch is checked as exact candidate
data, but real AMOS loader and AMOS Compiler B/C are NOT exercised.

AMOS End callback is tested from original AGA code after public Close.
Direct End without Close and live Chip still lacks an installed cleanup hook.
"""
from __future__ import annotations
from struct import unpack_from

from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from test_m5_generic import DR, AR, AMOS, EXEC, GFX, INTUI, STATE, DB, STACK, STOP
from test_m19_p0a_r88_get_gate_a import HEAD
from test_m19_p0c_screen_preclose_native import PreCloseMachine,ready as base_ready
from compiler_relocation import RBSR, unpack_ap20
from build_m19_p0c_screen_close_in_memory import (
    build,verify_aga_legacy,OLD_AGA,OLD_BOBS,
)
from m19_p0c_screen_close_bridge_emit import (
    emit_screen_close_bridge,AGA_STATE_OFFSET,AGA_CLOSE_ENTRY_OFFSET,
    CLOSE_STATE_DELTA,
)
from amos_link_test_support import relocate

# Physically disjoint units; Compiler may place them arbitrarily far apart.
AGABASE={'interpreted':0x300000, 'compiled':0x400000} # outside fixture's 0x600000..0xa00000 screen write guard


class RealCloseMachine(PreCloseMachine):
    def __init__(self,binary,layout='interpreted',depth=8,with_db=False):
        super().__init__(binary,layout,depth)
        self.native,self.labels=emit_screen_close_bridge()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.registry_entries={name:self.entry+self.labels[name] for name in (
            'registry_prepare_entry','registry_lookup_entry',
            'registry_free_entry','registry_close_entry',
            'screen_preclose_entry','screen_close_bridge_entry')}
        self.registry_addr=self.entry+self.labels['registry_state']

        _tok,parts,_title=unpack_ap20(binary)
        # build() already audited the OLD P0b public stub before redirect;
        # the candidate's stub 8 now intentionally points to BOBS group 90.
        self.aga=AGABASE[layout]
        self.aga_native=parts[OLD_AGA]
        # Exact original compiler V2 native group, no rewritten legacy source.
        self.uc.mem_write(self.aga,self.aga_native)
        self.real_state=self.aga+AGA_STATE_OFFSET
        self.old_close=self.aga+AGA_CLOSE_ENTRY_OFFSET
        self.old_end=self.aga+0x5a
        self.with_db=with_db
        self.events=[]
        self.uc.hook_add(UC_HOOK_CODE,self.on_native,
                         begin=self.aga,end=self.aga+len(self.aga_native))
        for vector in (INTUI-66, INTUI-774, INTUI-72,
                       EXEC-414, EXEC-672, EXEC-372):
            self.uc.mem_write(vector,b'\x4e\x75')

    def activate_aga_state(self):
        """Execute the ACTUAL original AGA V2 Init, after Get Bob capture."""
        # Source-pinned native initializer: D1='APex' handshake, A5=AMOS.
        # This must write State, End and Break callback pointers itself;
        # unlike the former fixture, none are host-supplied shortcuts.
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(DR[1],0x41506578)
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(self.aga+0x22,STOP,count=5000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.get(AMOS+0x1c8)==self.real_state
        assert self.get(AMOS+0x1cc)==self.old_end
        assert self.get(AMOS+0x1d0)==self.old_end
        assert bytes(self.uc.mem_read(self.real_state,40))==bytes(40)
        self.screen=0x5a000
        self.put(self.real_state, self.screen)
        self.put(self.real_state+4, INTUI)
        self.put(self.real_state+8, GFX)
        if self.with_db:
            self.put(self.real_state+32,DB)
            self.put(DB,0x54000)    # ScreenBuffer A
            self.put(DB+4,0x54100)  # ScreenBuffer B
            self.put(DB+12,0)       # no outstanding Safe/Disp msgport
            self.put(DB+16,0)
            self.put(DB+20,0)       # both pages are safe


    def on_native(self,uc,address,size,user):
        if address==self.old_close:
            self.events.append('real_aga_close_entry')
        if address==self.old_end:
            self.events.append('real_aga_end_entry')

    def os_call(self,uc,address,size,user):
        if address==INTUI-66:
            assert self.a(0)==self.screen, 'real AGA CloseScreen wrong screen'
            assert not self.chip_live and not self.metadata
            self.events.append('CloseScreen')
            return self._os_return(1)
        if address==INTUI-774:
            assert self.a(0)==self.screen
            assert not self.chip_live and not self.metadata
            self.events.append('FreeScreenBuffer')
            return self._os_return(0)
        if address==INTUI-72:
            self.events.append('CloseWindow')
            assert not self.chip_live
            return self._os_return(0)
        if address==EXEC-414:
            assert not self.chip_live and not self.metadata
            self.events.append('CloseLibrary')
            return self._os_return(0)
        if address==EXEC-672:
            assert not self.chip_live and not self.metadata
            self.events.append('DeleteMsgPort')
            return self._os_return(0)
        if address==EXEC-372:
            # Safe/Disp queue drained: no messages outstanding.
            return self._os_return(0)
        if address==EXEC-690:
            if self.a(1)==DB and self.with_db:
                assert not self.chip_live and not self.metadata
                self.events.append('FreeDBState')
                self.with_db=False
                return self._os_return(0)
            if self.a(1) in self.chip_live:
                self.events.append('FreeChip')
            elif self.a(1) in self.metadata:
                self.events.append('FreeRegistryNode')
        if address==GFX-228:
            self.events.append('WaitBlit')
        return super().os_call(uc,address,size,user)

    def invoke(self,which,*,limit=5000000):
        addr={'bridge':self.entry+self.labels['screen_close_bridge_entry'],
              'native_end':self.old_end}[which]
        for n,r in enumerate(DR): self.uc.reg_write(r,0x12305670+n)
        for n,r in enumerate(AR[:7]): self.uc.reg_write(r,0x40000+n*0x100)
        self.uc.reg_write(AR[5],AMOS)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(addr,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('REAL AGA CLOSE CPU020 fault',which,str(exc),
                  hex(self.uc.reg_read(UC_M68K_REG_PC)),self.events[-20:],
                  self.root(),self.get(self.real_state),self.get(self.real_state+8),
                  list(self.chip_live),list(self.metadata))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4, 'legacy/wrapper stack leak'
        for r,value in before.items():
            assert self.uc.reg_read(r)==value,('legacy Close ABI clobber',which,r)
        return self.events


def ready(lib,layout='interpreted',depth=8,with_db=False):
    m=RealCloseMachine(lib,layout,depth,with_db=with_db)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_get(2,6,5,36,8)==1
    assert m.mask(True,1,0)==1
    m.activate_aga_state()
    return m


def main():
    lib,report=build()
    _,parts,_=unpack_ap20(lib)
    source,labels=emit_screen_close_bridge()
    assert source==emit_screen_close_bridge()[0]
    code=source[labels['screen_close_bridge_entry']:]
    decoder=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
                 .disasm(code,0x100000+labels['screen_close_bridge_entry']))
    assert sum(x.size for x in decoder)==len(code), 'new public shim decode invalid'
    assert not any(x.mnemonic.startswith('dc.') for x in decoder)
    assert report['old_aga_group']==91 and report['bridge_group']==90
    assert parts[8][:2]==RBSR and unpack_from('>HH',parts[8],2)==(
        90,report['bridge_offset'])
    assert report['rel_aga_close']==CLOSE_STATE_DELTA

    cases=0
    for layout in ('interpreted','compiled'):
        for with_db in (False, True):
            m=ready(lib,layout,8,with_db=with_db)
            assert m.call('registry_prepare_entry')==1
            assert m.chip_live and m.metadata
            m.pending_dma=True
            # Real entry must NOT run until private Chip has been released.
            events=m.invoke('bridge')
            assert 'real_aga_close_entry' in events,events
            assert 'CloseScreen' in events,events
            assert events.index('FreeChip')<events.index('real_aga_close_entry')
            assert events.index('FreeRegistryNode')<events.index('real_aga_close_entry')
            assert events.index('WaitBlit')<events.index('FreeChip')
            assert events.index('real_aga_close_entry')<events.index('CloseScreen')
            assert m.root()==(0,0)
            assert not m.chip_live and not m.metadata
            assert m.get(m.real_state)==0 and m.get(m.real_state+8)==0
            assert not m.pending_dma
            if with_db:
                assert 'FreeDBState' in events and events.count('FreeScreenBuffer')==2
            cases+=5

            # Actual legacy End callback in the original AGA unit, after
            # Close, must not repeat a Chip free/ScreenClose.
            events_before=len(events)
            m.invoke('native_end')
            assert events[events_before:]==['real_aga_end_entry']
            assert not m.chip_live and not m.metadata
            cases+=2

        # Corrupt pinned legacy prologue -> refuse and preserve all resources.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        before=m.nodes()
        m.uc.mem_write(m.old_close,b'\x4e\x71')  # test-only corruption
        m.invoke('bridge')
        assert m.root()[1]!=0 and m.nodes()==before
        assert 'real_aga_close_entry' not in m.events
        assert m.get(m.real_state)!=0
        cases+=2

        # Missing GfxBase with Chip active: fail without touching old Close.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        m.put(m.real_state+8,0)
        m.invoke('bridge')
        assert m.root()[1]!=0 and m.chip_live
        assert 'real_aga_close_entry' not in m.events
        cases+=2

        # A direct End with live Chip would now DESTROY the AGA graphics
        # base before P0c cleanup (unsafe). Verify it remains UNHOOKED, but
        # deliberately never execute this dangerous legacy path on live DMA.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        assert m.get(AMOS+0x1cc)==m.old_end
        assert m.get(AMOS+0x1d0)==m.old_end
        assert m.chip_live and m.metadata
        cases+=1

    print('M19 P0c REAL legacy AGA Screen Close CPU020 Gate A',
          cases,'scenarios, bridge redirects public token 8,',
          'AGA group bytes UNCHANGED; Exec/Intuition mocked;',
          'AMOS End hook NOT YET installed; WinUAE/Compiler B/C NOT TESTED')
if __name__=='__main__':
    main()
