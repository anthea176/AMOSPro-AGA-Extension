#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b3 MC68020 private resolver: original bank != currently selected."""
from __future__ import annotations
from struct import unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from test_m19_p0j_explicit_bank_stage_gate_a import StageMachine
from m19_p0j_explicit_bank_stage_emit import emit_explicit_bank_stage
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve
from build_m19_p0j_explicit_image_resolve_in_memory import build
from m19_p0a_multi_bob_abk import parse_payload
from amos_link_test_support import relocate

OUT=0x43200
CANARY=b'Z'*36

class ResolverMachine(StageMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.res_native,self.labels=emit_explicit_bank_image_resolve()
        self.uc.mem_write(self.entry,relocate(self.res_native,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['routed_paint_prechecked_entry']

    def resolve(self,bank,image,owner=AMOS):
        self.uc.mem_write(OUT,CANARY)
        for n,r in enumerate(DR):
            self.uc.reg_write(r,0x660000+n)
        for n,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x43000+n*256)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[1],OUT)
        self.uc.reg_write(DR[3],bank)
        self.uc.reg_write(DR[0],image)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True
        try:
            self.uc.emu_start(self.entry+self.labels['explicit_image_resolve_entry'],
                              STOP,count=15000000)
        finally:
            self.in_explicit_lookup=False
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert not self.explicit_shadow_writes,('selected bank shadow written',
                                               self.explicit_shadow_writes)
        for r,v in saved.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('P0j-b3 ABI register',r)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3),bytes(self.uc.mem_read(OUT,36))

def main():
    candidate,meta=build()
    assert meta['public_commands']==85 and meta['ap20_entries']==178
    assert meta['native_groups']==[142,153,156,177] and meta['pc16_max']<1000
    old,_=emit_explicit_bank_stage()
    source,labels=emit_explicit_bank_image_resolve()
    assert source.startswith(old) and labels['explicit_image_resolve_entry']==len(old)
    tail=source[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(tail,0x120000+len(old)))
    assert ins and sum(i.size for i in ins)==len(tail)
    assert not any(x.mnemonic.startswith('dc.') for x in ins)
    ntests=0
    original,_=build_p0c()
    for layout in ('interpreted','compiled'):
        m=ResolverMachine(original,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        m.activate_aga_state()
        m.configure_real_state()
        select=m.selected_triple()   # always bank 11
        assert m.stage(10)==1
        assert m.stage(11)==1
        assert m.selected_triple()==select
        ntests+=3

        for bank in (10,11):
            ok,descr=m.resolve(bank,1)
            assert ok==1,(layout,bank,m.root(),m.nodes())
            plane0,mask,w,h,stride,depth,plane_bytes,chip,alloc=unpack('>9I',descr)
            img=parse_payload(m.bank_payload(bank)).image(1)
            assert (w,h,stride,depth)==(img.width,img.height,img.stride,img.depth)
            assert plane_bytes==stride*h and mask==0
            assert chip in m.chip_live and alloc==m.chip_live[chip]
            assert chip<=plane0<chip+alloc
            assert bytes(m.uc.mem_read(plane0,len(img.planes)))==img.planes
            assert m.selected_triple()==select
            ntests+=6

        # No image: destination untouched, and no DMA/Chip mutation.
        live=dict(m.chip_live)
        assert m.resolve(11,4096)==(0,CANARY)
        assert m.resolve(10,0)==(0,CANARY)
        assert m.resolve(12,1)==(0,CANARY)
        assert m.resolve(10,1,owner=AMOS+0x1000)==(0,CANARY)
        assert m.selected_triple()==select and m.chip_live==live
        ntests+=5

        # Generation drift: never publish stale DMA pointer.
        node=m.find(10)
        generation=m.get(node+24+24)
        m.put(node+24+24,generation+1)
        assert m.resolve(10,1)==(0,CANARY)
        m.put(node+24+24,generation)
        assert m.resolve(10,1)[0]==1
        ntests+=2

        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.resolve(10,1)==(0,CANARY)
        m.uc.mem_write(EXEC+0x128,b'\x00\x02')
        assert m.resolve(10,1)[0]==1
        ntests+=2

        assert m.call('registry_close_entry')==1
        assert m.resolve(10,1)==(0,CANARY)
        ntests+=2

    print('M19 P0j-b3 MC68020 EXPLICIT SOURCE-BANK IMAGE RESOLVE GATE A PASS',
          ntests,'cases, two independent native group placements,',
          'real AGBO/Chip offsets and mask/plane checks, ZERO selector writes;',
          'no Blitter, no public Draw/WinUAE/Compiler')

if __name__=='__main__':
    main()
