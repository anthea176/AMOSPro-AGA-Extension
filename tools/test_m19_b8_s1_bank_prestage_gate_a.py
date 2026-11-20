#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Bank Select pre-stage: real emitted 68020 vs mocked AmigaOS.

Two independent native placements. Exercises the actual original P0a bank
selector, checked P0c Chip AllocVec/CopyMem, P0j explicit registry, B7 End
armer, Bob image capture and failure rollback. NO native WinUAE/Compiler.
"""
from __future__ import annotations

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from amos_link_test_support import relocate
from build_m19_b8_s1_bank_prestage_in_memory import build_bank_prestage
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from m19_b8_first_update_emit import emit_b8_b7_first_update
from m19_b8_s1_bank_prestage_emit import emit_b8_s1_bank_prestage
from test_m19_b8_first_update_gate_a import FirstUpdateIntegrated
from test_m19_p0j_swap_barrier_gate_a import READY
from test_m5_generic import AMOS


class Prestaged(FirstUpdateIntegrated):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.native,self.labels=emit_b8_s1_bank_prestage()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['b8_b7_draw_trampoline_entry']
        self.labels['guarded_close_entry']=self.labels['b8_b7_close_trampoline_entry']

    def run_select(self,bank):
        # Invoke the new AP20 native target without ever rebasing the object
        # mapping: OS mocks, stage state and source labels use self.entry.
        from unicorn.m68k_const import UC_M68K_REG_SR, UC_M68K_REG_PC
        from test_m5_generic import DR, AR, STACK, STOP
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],0x58000)
        self.uc.reg_write(DR[3],bank & 0xffffffff)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        target=self.entry+self.labels['b8s1_bank_prestage_entry']
        try:
            self.uc.emu_start(target,STOP,count=9000000)
        except Exception as exc:
            raise AssertionError(('M19 P0 Bank Chip MC68020 native fault',
                str(exc),hex(self.uc.reg_read(UC_M68K_REG_PC)),bank)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4, 'AMOS stack mismatch'
        for reg,value in before.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==value,('AMOS ABI',reg)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3)


def fresh(layout):
    source,_=build_p0c()
    m=Prestaged(source,layout)
    assert m.run_select(10)==1 # Missing bank -> canonical EMPTY.
    assert not m.chip_live and not m.metadata
    assert m.run_get(1,4,5,20,8)==1 # Now bank 10 is populated.
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    assert not m.chip_live and not m.metadata
    # An AGBO with images requires an open AGA screen to be pre-staged.
    before=m.selected_triple()
    assert m.run_select(10)==0
    assert m.selected_triple()==before
    assert not m.chip_live
    m.activate_aga_state()
    m.configure_real_state()
    return m


def main():
    image,meta=build_bank_prestage()
    assert image==build_bank_prestage()[0]
    assert meta['predecessor_sha']=='3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a'
    assert meta['public_commands']==88 and meta['ap20_entries']==184
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['old_bobs_prefix_byte_exact'] and meta['b8_fifth_byte_exact']
    assert meta['pc16_max']<32766
    old,_=emit_b8_b7_first_update()
    new,labels=emit_b8_s1_bank_prestage()
    assert new.startswith(old) and labels['b8s1_bank_prestage_entry']==len(old)
    dec=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(new[len(old):],0x10000+len(old)))
    assert dec and sum(x.size for x in dec)==len(new)-len(old)
    assert all(not x.mnemonic.startswith('dc.') for x in dec)

    checks=10
    for layout in ('interpreted','compiled'): # relocated 68020, NOT Compiler
        m=fresh(layout)
        assert not any(e[0] in ('BltMask','BltOpaque') for e in m.paint_blits)
        assert len(m.chip_live)==0 and len(m.metadata)==0
        assert m.run_select(10)==1
        assert len(m.chip_live)==1 and len(m.metadata)==1
        assert m.chip_allocs==1 and m.chip_copies==1
        assert not any(e[0] in ('BltMask','BltOpaque') for e in m.paint_blits) # PREPARE occurred before any Bob DRAW.
        assert m.callbacks()==(m.end_callback(),)*2
        allocs=m.chip_allocs
        assert m.run_select(10)==1 # identical bank + gen = reuse.
        assert m.chip_allocs==allocs and m.chip_copies==1
        assert m.run_select(11)==1
        assert len(m.chip_live)==2 and len(m.metadata)==2
        assert m.chip_allocs==2 and m.chip_copies==2
        assert not any(e[0] in ('BltMask','BltOpaque') for e in m.paint_blits)
        assert m.run_select(10)==1
        assert m.chip_allocs==2
        assert m.public('bob',ident=1,x=5,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=9,y=11,image=1)==1
        before=m.chip_allocs
        assert m.frame()==1 and m.status()==READY
        assert m.chip_allocs==before and len(m.chip_live)==2
        assert sum(event[0] in ('BltOpaque','BltMask')
                   for event in m.paint_blits)==2
        checks+=20

        # First stage fails: selection rollback and no partial registry.
        n=fresh(layout)
        prior=n.selected_triple()
        n.chip_fail=True
        assert n.run_select(10)==0
        assert n.selected_triple()==prior
        assert not n.chip_live and not n.metadata
        assert n.chip_allocs>=1
        n.chip_fail=False
        assert n.run_select(10)==1 and len(n.chip_live)==1
        checks+=5

        # Metadata failure never touches Chip or original AGBO bank.
        f=fresh(layout)
        old=f.bank_payload(10)
        prior=f.selected_triple()
        f.meta_fail=True
        assert f.run_select(10)==0
        assert f.selected_triple()==prior
        assert not f.chip_live and not f.metadata
        assert f.bank_payload(10)==old
        checks+=4

        # Foreign End callback: stage, checked rollback with WaitBlit/free,
        # no selection change and no callback replacement.
        q=fresh(layout)
        prev=q.selected_triple()
        q.put(AMOS+0x1cc,0x123450)
        q.put(AMOS+0x1d0,0x123450)
        assert q.run_select(10)==0
        assert q.selected_triple()==prev
        assert q.callbacks()==(0x123450,0x123450)
        assert not q.chip_live and not q.metadata
        assert q.chip_allocs==q.chip_frees
        checks+=5

        # Empty canonical bank can be selected after Open without Chip.
        z=fresh(layout)
        assert z.run_select(12)==1
        assert not z.chip_live and not z.metadata
        checks+=2

    print('M19 P0 BANK SELECT PRESTAGE MC68020 Gate A PASS',
          checks,'checks; 2 relocations; no Bob Draw before Chip preparation')
    print('M19 P0 SOURCE ONLY',meta)


if __name__=='__main__':
    main()
