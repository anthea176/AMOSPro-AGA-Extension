#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j gate: full frame image preflight before the FIRST Chip/Blit."""
from __future__ import annotations

from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from test_m5_generic import EXEC,AMOS
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0i_multibank_draw_gate_a import MultiBankMachine
from test_m19_p0d_safe_bank_blit_native import oracle,SIZE
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0j_frame_image_preflight_in_memory import build
from m19_p0j_frame_image_preflight_emit import emit_image_preflight
from m19_p0i_multibank_draw_emit import emit_multibank_paint
from amos_link_test_support import relocate


class ImageGateMachine(MultiBankMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.j_source,self.j_labels=emit_image_preflight()
        self.uc.mem_write(self.entry,relocate(self.j_source,
                                             self.entry,{},self.uc))
        # Reuse the exact P0i call harness but address the stricter,
        # private full-frame entry instead of P0i's old paint_all.
        self.labels=self.j_labels.copy()
        self.labels['routed_paint_all_entry']=self.j_labels['routed_paint_prechecked_entry']


def prepare(layout,count=64):
    src,_=build_p0c()
    m=ImageGateMachine(src,layout)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    m.activate_aga_state()
    m.configure_real_state()
    for n in range(1,count+1):
        bank=10 if n<=32 else 11
        assert m.run_select(bank)==1
        assert m.public('bob',ident=n,image=1,x=(n*7)%65,y=(n*11)%45)==1
    return m


def main():
    lib,report=build()
    assert report['public_commands']==85 and report['ap20_entries']==178
    assert report['native_groups']==[142,153,156,177] and report['max_pc16']<1000
    previous,_=emit_multibank_paint()
    native,labels=emit_image_preflight()
    assert native.startswith(previous)
    section=native[len(previous):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(section,0x130000))
    assert sum(i.size for i in ins)==len(section)
    assert all(not x.mnemonic.startswith('dc.') for x in ins)
    passed=0
    old,_=build_p0c()
    for layout in ('interpreted','compiled'):
        # Missing last image: P0i painted 63 objects before refusing.
        # P0j must preserve the entire back buffer and NEVER call Blitter.
        m=prepare(layout)
        assert m.public('bob',ident=64,image=4096,x=8,y=9)==1
        before=m.read_back()
        selected=m.selected_triple()
        paints=len(m.paint_blits)
        allocs=m.chip_allocs
        assert m.route('all')==0
        assert m.read_back()==before
        assert len(m.paint_blits)==paints and m.chip_allocs==allocs
        assert m.selected_triple()==selected
        assert m.get(0x53000+8)==0 and not m.chip_live
        passed+=6

        # Bnk.GetAdr payload begins node+24, image directory is payload+32.
        # The bank generation field instead resides at payload+24.
        for off,bad in ((6,b'\x00\x04'),        # bad depth
                        (8,b'\x00\x01'),        # bad stride
                        (10,b'\x00\x02'),       # unsupported mask flag
                        (16,b'\x00\x00\x00\x00')): # wrong pixel length
            n=prepare(layout)
            entry=n.find(11)+24+32
            original=bytes(n.uc.mem_read(entry,40))
            n.uc.mem_write(entry+off,bad)
            before=n.read_back();p=len(n.paint_blits)
            allocs=n.chip_allocs
            assert n.route('all')==0,(layout,off)
            assert n.read_back()==before and len(n.paint_blits)==p
            assert n.chip_allocs==allocs and not n.chip_live
            n.uc.mem_write(entry,original)
            passed+=4

        # All 64 valid images: paint exactly all objects, pixel by pixel.
        n=prepare(layout)
        chosen=n.selected_triple()
        front=tuple(bytes(n.uc.mem_read(p,SIZE)) for p in n.screen_planes)
        first=n.read_back()
        img10=parse_payload(n.bank_payload(10)).image(1)
        img11=parse_payload(n.bank_payload(11)).image(1)
        expected=first
        for ident in range(1,65):
            img=img10 if ident<=32 else img11
            expected=oracle(expected,img,(ident*7)%65,(ident*11)%45)
        assert n.route('all')==1,(layout,n.route_trace[-30:])
        assert n.read_back()==expected
        assert n.selected_triple()==chosen
        assert tuple(bytes(n.uc.mem_read(p,SIZE)) for p in n.screen_planes)==front
        assert sum(x[0] in ('BltMask','BltOpaque') for x in n.paint_blits)==64
        assert len(n.chip_live)==2
        passed+=6

        # A later deleted bank must refuse the frame before any paint.
        n=prepare(layout)
        node=n.find(11);g=n.get(node+24+24)
        n.put(node+24+24,g+1)
        before=n.read_back();paint=len(n.paint_blits)
        assert n.route('all')==0
        assert n.read_back()==before and len(n.paint_blits)==paint
        passed+=2

        # CPU000 never gets to image scan or Chip staging.
        n=prepare(layout)
        n.uc.mem_write(EXEC+0x128,b'\x00\x00')
        before=n.read_back();p=len(n.paint_blits)
        assert n.route('all')==0
        assert n.read_back()==before and len(n.paint_blits)==p
        passed+=2

        # Memory stage/release still owns all allocations.
        n=prepare(layout)
        assert n.route('all')==1
        n.invoke('bridge')
        assert not n.chip_live and not n.metadata
        passed+=2

    print('M19 P0j MC68020 PRE-DMA IMAGE FRAME PREFLIGHT GATE A PASS',
          passed,'checks; two distinct AGA/BOBS native placements,',
          '64 Bobs from banks 10/11, missing last image no DMA/Chip; ',
          'P0i shadow projection remains; NO WinUAE/Compiler claims')


if __name__=='__main__':
    main()
