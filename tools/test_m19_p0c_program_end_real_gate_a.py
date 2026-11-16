#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c actual legacy AMOS End callback from private BOBS exit hook.

Exec/Intuition/graphics services are MOCKED; original compiled V2 native AGA
code bytes are executed unchanged under Unicorn MC68020. Explicit PRIVATE
program_end_arm is required after a private stage. Current public P0b Bob
commands do NOT yet arm the callback or stage Chip themselves.
No WinUAE/real Compiler claim.
"""
from __future__ import annotations
from struct import unpack_from

from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020

from test_m5_generic import DR,AR,AMOS,STACK,STOP,EXEC
from test_m19_p0c_screen_close_real_gate_a import RealCloseMachine
from m19_p0c_program_end_bridge_emit import emit_program_end_bridge
from m19_p0c_screen_close_bridge_emit import emit_screen_close_bridge
from amos_link_test_support import relocate
from build_m19_p0c_screen_close_in_memory import build


class EndMachine(RealCloseMachine):
    def __init__(self,lib,layout='interpreted',depth=8,with_db=False):
        super().__init__(lib,layout,depth,with_db=with_db)
        self.native,self.labels=emit_program_end_bridge()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.registry_entries={name:self.entry+self.labels[name] for name in (
            'registry_prepare_entry','registry_lookup_entry',
            'registry_free_entry','registry_close_entry',
            'screen_preclose_entry','screen_close_bridge_entry',
            'program_end_arm_entry')}
        self.registry_addr=self.entry+self.labels['registry_state']
        self.uc.hook_add(UC_HOOK_CODE,self.end_enter_hook,
            begin=self.entry+self.labels['program_end_bridge_entry'],
            end=self.entry+self.labels['program_end_bridge_entry'])

    def end_enter_hook(self,uc,addr,size,user):
        self.events.append('p0c_end_bridge_entry')

    def invoke_callback(self,slot=0x1cc,limit=5000000):
        assert slot in (0x1cc,0x1d0)
        target=self.get(AMOS+slot)
        for n,r in enumerate(DR):self.uc.reg_write(r,0x1230+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+n*0x100)
        self.uc.reg_write(AR[5],AMOS)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(target,STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('AMOS REAL End CPU020 fault',str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),hex(target),
                self.events[-25:],self.root(),
                list(self.chip_live),list(self.metadata))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for reg,value in before.items():
            assert self.uc.reg_read(reg)==value,('End callback ABI clobber',reg)
        return self.events


def ready(lib,layout,*,with_db=False):
    m=EndMachine(lib,layout,8,with_db=with_db)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.mask(True,1,0)==1
    m.activate_aga_state()
    return m


def main():
    lib,report=build()
    source,labels=emit_program_end_bridge()
    previous,_=emit_screen_close_bridge()
    assert source[:len(previous)]==previous
    assert source==emit_program_end_bridge()[0]
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).disasm(
        source[len(previous):],0x100000+len(previous)))
    assert sum(x.size for x in dis)==len(source)-len(previous)
    assert not any(x.mnemonic.startswith('dc.') for x in dis)
    assert report['program_end_hook'].startswith('PRIVATE ARM+END')
    assert report['end_arm_offset']<report['end_callback_offset']

    tests=0
    for layout in ('interpreted','compiled'):
        for with_db in (False,True):
            m=ready(lib,layout,with_db=with_db)
            assert m.call('program_end_arm_entry')==0  # no staged Chip
            assert m.call('registry_prepare_entry')==1
            assert m.call('program_end_arm_entry')==1
            assert m.call('program_end_arm_entry')==1  # idempotent re-arm
            end_target=m.entry+m.labels['program_end_bridge_entry']
            assert (m.get(AMOS+0x1cc),m.get(AMOS+0x1d0))==(end_target,end_target)
            m.pending_dma=True
            events=m.invoke_callback(0x1cc)
            assert 'p0c_end_bridge_entry' in events
            assert 'real_aga_end_entry' in events
            assert 'CloseScreen' in events
            assert events.index('WaitBlit')<events.index('FreeChip')
            assert events.index('FreeChip')<events.index('real_aga_end_entry')
            assert events.index('FreeRegistryNode')<events.index('real_aga_end_entry')
            assert events.index('real_aga_end_entry')<events.index('CloseScreen')
            assert not m.chip_live and not m.metadata and m.root()==(0,0)
            assert not m.pending_dma
            assert m.get(m.real_state)==0 and m.get(m.real_state+8)==0
            assert (m.get(AMOS+0x1cc),m.get(AMOS+0x1d0))==(m.old_end,m.old_end)
            tests+=7

            before=len(events)
            m.invoke_callback(0x1d0)
            assert events[before:]==['real_aga_end_entry']
            tests+=1

        # AMOS Screen Close first then End callback: real legacy End idempotent.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        assert m.call('program_end_arm_entry')==1
        m.invoke('bridge')
        assert not m.chip_live and not m.metadata
        assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
        m.invoke_callback(0x1d0)
        assert m.get(AMOS+0x1cc)==m.old_end and m.get(AMOS+0x1d0)==m.old_end
        assert m.events.count('CloseScreen')==1
        tests+=3

        # Third-party callback: never overwrite registered foreign handler.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        m.put(AMOS+0x1cc,0x123456)
        assert m.call('program_end_arm_entry')==0
        assert m.get(AMOS+0x1cc)==0x123456
        assert m.get(AMOS+0x1d0)==m.old_end
        assert m.chip_live
        tests+=2

        # Corrupt actual AGA End native prologue; reject before arming.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        m.uc.mem_write(m.old_end,b'\x4e\x71')
        assert m.call('program_end_arm_entry')==0
        assert m.get(AMOS+0x1cc)==m.old_end
        tests+=2

        # Missing graphics base: DO NOT chain to destructive old End.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        assert m.call('program_end_arm_entry')==1
        m.put(m.real_state+8,0)
        m.invoke_callback(0x1d0)
        assert m.chip_live and m.metadata
        assert 'real_aga_end_entry' not in m.events
        assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
        tests+=2

        # Ownership guard blocks a foreign program. CPU000 is rejected.
        m=ready(lib,layout)
        assert m.call('registry_prepare_entry')==1
        assert m.call('program_end_arm_entry',owner=AMOS+0x100)==0
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.call('program_end_arm_entry')==0
        tests+=2

    print('M19 P0c PRIVATE real AMOS End callback CPU020 Gate A PASS',
          tests,'cases,',len(source),'BOBS native bytes;',
          'old AGA code UNMODIFIED, services mocked,'
          ' explicit post-stage arming required, no WinUAE/Compiler proof')

if __name__=='__main__':main()
