#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0i Gate A: actual native two-bank persistent Bob Safe painter.

Runs real source-emitted MC68020, two independent AGA/BOBS layouts.
Exec/AMOS/graphics and Blitter are mocked, NOT WinUAE/real Compiler.
"""
from __future__ import annotations
from struct import unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0h_frame_preflight_gate_a import FrameMachine
from test_m19_p0d_safe_bank_blit_native import oracle
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0i_multibank_draw_in_memory import build
from m19_p0h_frame_preflight_emit import emit_frame_preflight
from m19_p0i_multibank_draw_emit import emit_multibank_paint,MAX_BOBS
from amos_link_test_support import relocate

class MultiBankMachine(FrameMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.route_native,self.labels=emit_multibank_paint()
        self.uc.mem_write(self.entry,relocate(self.route_native,
                                            self.entry,{},self.uc))
        self.native=self.route_native

    def route(self,kind='all',ident=1,owner=AMOS,count=27000000):
        assert kind in ('one','all')
        for n,r in enumerate(DR):self.uc.reg_write(r,0x770000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x43000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(DR[0],ident)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        entry='routed_paint_all_entry' if kind=='all' else 'routed_paint_one_entry'
        try:
            self.uc.emu_start(self.entry+self.labels[entry],STOP,count=count)
        except Exception as err:
            raise AssertionError(('P0i routed native CPU020 fault',kind,ident,
                str(err),hex(self.uc.reg_read(UC_M68K_REG_PC)),
                self.paint_blits[-8:],self.nodes() if self.metadata else {})) from err
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for r,v in saved.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('P0i AMOS ABI clobber',r)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3)

    def selected_triple(self):
        ptr=self.entry+self.labels['bank_active_state']
        return bytes(self.uc.mem_read(ptr,12))

def main():
    original,_=build_p0c()
    rebuilt,meta=build()
    assert meta['public_commands']==85 and meta['ap20_entries']==178
    assert meta['native_groups']==[142,153,156,177]
    assert meta['max_pc16']<1000
    old,_=emit_frame_preflight()
    new,lab=emit_multibank_paint()
    assert new.startswith(old) and lab['routed_paint_one_entry']==len(old)
    sec=new[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(sec,0x100000+len(old)))
    assert sum(x.size for x in ins)==len(sec)
    assert all(not x.mnemonic.startswith('dc.') for x in ins)
    passed=0
    for layout in ('interpreted','compiled'):
        m=MultiBankMachine(original,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        m.activate_aga_state()
        m.configure_real_state()
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=5,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=9,y=11,image=1)==1
        selected=m.selected_triple()
        original_front=tuple(bytes(m.uc.mem_read(p,128*64))
                             for p in m.screen_planes)
        start=m.read_back()
        img10=parse_payload(m.bank_payload(10)).image(1)
        img11=parse_payload(m.bank_payload(11)).image(1)
        expected=oracle(oracle(start,img10,5,7),img11,9,11)
        assert m.route('all')==1
        assert m.selected_triple()==selected,'Aga Bob Bank changed after Draw'
        assert m.read_back()==expected,'BOBS source bank / draw order pixel drift'
        assert m.get(0x53000+8)==0,'unexpected automatic AGA Swap'
        assert tuple(bytes(m.uc.mem_read(p,128*64))
                     for p in m.screen_planes)==original_front
        assert sum(x[0] in ('BltMask','BltOpaque') for x in m.paint_blits)==2
        assert len(m.chip_live)==2,'each original source bank must own Chip'
        live=dict(m.chip_live)
        passed+=7

        assert m.route('all')==1
        assert m.selected_triple()==selected
        assert m.chip_live==live,'repeated Bobs recopied or leaked Chip'
        passed+=3

        # A destroyed/replaced last bank refuses the whole frame before DMA.
        node=m.find(11)
        oldgen=m.get(node+24+24)
        m.put(node+24+24,oldgen+1)
        before=m.read_back()
        nblit=len(m.paint_blits)
        assert m.route('all')==0
        assert m.read_back()==before and len(m.paint_blits)==nblit
        assert m.selected_triple()==selected
        m.put(node+24+24,oldgen)
        passed+=3

        # Missing Safe notification: no paint or hidden Swap, selector restored.
        m.safe=False
        m.put(0x53000+20,3)
        before=m.read_back()
        nblit=len(m.paint_blits)
        assert m.route('all')==0
        assert m.read_back()==before and len(m.paint_blits)==nblit
        assert m.selected_triple()==selected
        assert m.get(0x53000+8)==0
        m.safe=True
        m.put(0x53000+20,0)
        passed+=4

        # The original program-End callback is armed for both Chip sources.
        assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
        m.invoke('bridge')
        assert not m.chip_live and not m.metadata
        passed+=2

    print('M19 P0i PRIVATE TWO-BANK PERSISTENT BOB BLIT GATE A PASS',
          passed,'checks, source MC68020 + 2 disjoint V2 layouts',
          'pixel-exact source banks 10/11, hidden back buffer, Chip cache',
          'selector restored; NO public Draw/WinUAE/real Compiler')

if __name__=='__main__':
    main()
