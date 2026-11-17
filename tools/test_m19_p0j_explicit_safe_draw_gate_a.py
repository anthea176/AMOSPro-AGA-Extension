#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b4 Gate A: 64 persistent Bobs from source banks, ZERO shadow writes.

Real emitted MC68020 executes on two disjoint native placements; AMOS,
Exec/graphics and Blitter are mocked, not WinUAE or real Compiler.
"""
from __future__ import annotations
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from test_m19_p0a_r88_get_gate_a import SCREEN_W
from test_m5_generic import EXEC,AMOS
from test_m19_p0j_explicit_image_resolve_gate_a import ResolverMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0j_explicit_safe_draw_in_memory import build
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw
from m19_p0a_multi_bob_abk import parse_payload
from test_m19_p0d_safe_bank_blit_native import oracle,SIZE
from amos_link_test_support import relocate

class NoShadowMachine(ResolverMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.draw_native,self.labels=emit_explicit_bob_draw()
        self.uc.mem_write(self.entry,relocate(self.draw_native,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['explicit_frame_draw_entry']

    def frame(self):
        start=self.selected_triple()
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True
        try:
            result=self.route('all')
        finally:
            self.in_explicit_lookup=False
        assert not self.explicit_shadow_writes,('SHADOW WRITE DURING FRAME',
                                               self.explicit_shadow_writes)
        assert self.selected_triple()==start
        return result

def prepare(layout,all64=False):
    src,_=build_p0c()
    m=NoShadowMachine(src,layout)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.mask(True,1,0)==1    # actual 1-bit transparency in bank10
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    m.activate_aga_state();m.configure_real_state()
    if not all64:
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=5,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=9,y=11,image=1)==1
    else:
        for ident in range(1,65):
            bank=10 if ident<=32 else 11
            assert m.run_select(bank)==1
            assert m.public('bob',ident=ident,image=1,
                            x=(ident*7)%65,y=(ident*11)%45)==1
    assert m.run_select(11)==1
    return m

def main():
    candidate,meta=build()
    assert meta['public_commands']==85 and meta['ap20_entries']==178
    assert meta['native_groups']==[142,153,156,177] and meta['pc16_max']<1000
    previous,_=emit_explicit_bank_image_resolve()
    source,labels=emit_explicit_bob_draw()
    assert source.startswith(previous)
    code=source[len(previous):]
    instructions=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
                      .disasm(code,0x120000+len(previous)))
    assert instructions and sum(i.size for i in instructions)==len(code)
    assert all(not i.mnemonic.startswith('dc.') for i in instructions)
    checks=0
    original,_=build_p0c()
    for layout in ('interpreted','compiled'):
        m=prepare(layout)
        selected=m.selected_triple()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        initial=m.read_back()
        i10=parse_payload(m.bank_payload(10)).image(1)
        i11=parse_payload(m.bank_payload(11)).image(1)
        expected=oracle(oracle(initial,i10,5,7),i11,9,11)
        assert m.frame()==1,(layout,m.route_trace[-25:],
                             m.root(),m.nodes() if m.metadata else {})
        assert m.read_back()==expected,'Pixel-exact source bank/overlap drift'
        assert m.selected_triple()==selected
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        assert m.get(0x53000+8)==0
        assert len(m.chip_live)==2
        assert sum(t[0] in ('BltOpaque','BltMask') for t in m.paint_blits)==2
        allocs=m.chip_allocs;copies=m.chip_copies;cache=dict(m.chip_live)
        checks+=7

        assert m.frame()==1
        assert m.read_back()==expected
        assert m.chip_live==cache and m.chip_allocs==allocs
        assert m.chip_copies==copies
        checks+=3

        assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
        m.invoke('bridge')
        assert not m.chip_live and not m.metadata
        checks+=2

        m=prepare(layout,all64=True)
        chosen=m.selected_triple()
        start=m.read_back()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        i10=parse_payload(m.bank_payload(10)).image(1)
        i11=parse_payload(m.bank_payload(11)).image(1)
        expected=start
        for ident in range(1,65):
            img=i10 if ident<=32 else i11
            expected=oracle(expected,img,(ident*7)%65,(ident*11)%45)
        assert m.frame()==1,(layout,m.route_trace[-20:])
        assert m.read_back()==expected
        assert m.selected_triple()==chosen and m.get(0x53000+8)==0
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        assert len(m.chip_live)==2 and m.chip_allocs==2
        assert sum(t[0] in ('BltOpaque','BltMask') for t in m.paint_blits)==64
        checks+=6

        allocs=m.chip_allocs;copies=m.chip_copies
        assert m.frame()==1
        assert m.chip_allocs==allocs and m.chip_copies==copies
        checks+=2

        # Source bank 11 becomes stale for Bob64: preflight rejects BEFORE
        # any new DMA; all buffers and selected bank remain unchanged.
        node=m.find(11);gen=m.get(node+24+24)
        m.put(node+24+24,gen+1)
        before=m.read_back();blits=len(m.paint_blits)
        assert m.frame()==0
        assert m.read_back()==before and len(m.paint_blits)==blits
        assert m.selected_triple()==chosen
        m.put(node+24+24,gen)
        checks+=3

        m=prepare(layout,all64=True)
        assert m.public('bob',ident=64,image=4096,x=5,y=5)==1
        before=m.read_back();blits=len(m.paint_blits)
        assert m.frame()==0
        assert m.read_back()==before and len(m.paint_blits)==blits
        assert not m.chip_live and not m.metadata
        assert m.get(0x53000+8)==0
        checks+=4

        m=prepare(layout)
        m.safe=False
        m.put(0x53000+20,3)
        old=m.read_back();blits=len(m.paint_blits)
        assert m.frame()==0
        assert m.read_back()==old and len(m.paint_blits)==blits
        assert m.get(0x53000+8)==0
        checks+=3

        # Regression: actual transparent mask clipped at a negative X,
        # then an opaque Bob clipped at the right screen boundary.
        m=prepare(layout)
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=-3,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=SCREEN_W-5,y=11,image=1)==1
        selected=m.selected_triple()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        before=m.read_back()
        i10=parse_payload(m.bank_payload(10)).image(1)
        i11=parse_payload(m.bank_payload(11)).image(1)
        expected=oracle(oracle(before,i10,-3,7),i11,SCREEN_W-5,11)
        assert m.frame()==1
        assert m.read_back()==expected
        assert [t[0] for t in m.paint_blits if t[0] in ('BltMask','BltOpaque')]==['BltMask','BltOpaque']
        assert m.get(0x53000+8)==0 and m.selected_triple()==selected
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        checks+=5

        # Regression: a damaged 1-bit mask length in source AGBO must
        # reject the ENTIRE 64-object frame before Chip staging or DMA.
        m=prepare(layout,all64=True)
        masked_entry=m.find(10)+24+32
        original_mask_len=m.get(masked_entry+24)
        assert original_mask_len>1
        m.put(masked_entry+24,original_mask_len-1)
        selected=m.selected_triple()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        before=m.read_back()
        assert m.frame()==0
        assert m.read_back()==before
        assert sum(t[0] in ('BltOpaque','BltMask') for t in m.paint_blits)==0, (layout, 'unexpected Blitter DMA after invalid mask', m.paint_blits)
        assert not m.chip_live and not m.metadata
        assert m.chip_allocs==0 and m.chip_copies==0
        assert m.get(0x53000+8)==0 and m.selected_triple()==selected
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        m.put(masked_entry+24,original_mask_len)
        assert m.frame()==1
        assert sum(t[0]=='BltMask' for t in m.paint_blits)==32
        assert sum(t[0]=='BltOpaque' for t in m.paint_blits)==32
        checks+=8

        # Regression: force SafePort to fail AFTER Bob 1 has already
        # Blitted. Return is failure; partial BACK exists but the FRONT
        # remains unchanged, with no implicit Swap. This is NOT atomicity.
        m=prepare(layout)
        m.safe=True
        m.put(0x53000+12,0x5b000)
        m.put(0x53000+20,0)
        selected=m.selected_triple()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        before=m.read_back()
        img=parse_payload(m.bank_payload(10)).image(1)
        first_only=oracle(before,img,5,7)
        visits=[]
        def fail_safe_on_second_bob(uc,address,size,user):
            visits.append(address)
            if len(visits)==2:
                m.safe=False
                m.put(0x53000+20,3)
        paint_entry=m.entry+m.labels['explicit_safe_blit_entry']
        hook=m.uc.hook_add(UC_HOOK_CODE,fail_safe_on_second_bob,
                           begin=paint_entry,end=paint_entry)
        try:
            assert m.frame()==0
        finally:
            m.uc.hook_del(hook)
        assert len(visits)==2 and m.read_back()==first_only
        assert sum(t[0]=='BltMask' for t in m.paint_blits)==1
        assert sum(t[0]=='BltOpaque' for t in m.paint_blits)==0
        assert sum(t[0]=='WaitBlit' for t in m.paint_blits)>=1  # includes Chip-stage sync
        assert len(m.getmsg)==1 and m.get(0x53000+20)==3
        assert m.get(0x53000+8)==0 and m.selected_triple()==selected
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        m.invoke('bridge')
        assert not m.chip_live and not m.metadata
        checks+=9

    print('M19 P0j-b4 NO-SHADOW PERSISTENT 64-BOB BLITTER GATE A PASS',
          checks,'tests, two disjoint native V2 layouts; 64 real Bobs from',
          'banks 10+11, pixel-exact masked and opaque Chip sources,',
          'Safe back buffer, no Swap, ZERO selected-state writes;',
          'NO public Draw / WinUAE / real AMOS Compiler')

if __name__=='__main__':
    main()
