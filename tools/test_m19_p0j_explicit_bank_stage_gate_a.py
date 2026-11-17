#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 Gate A: original P0c full validator but bank choice explicit."""
from __future__ import annotations
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,GFX,EXEC,STACK,STOP
from test_m19_p0j_explicit_bank_lookup_gate_a import ExplicitMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0j_explicit_bank_stage_in_memory import build
from m19_p0j_explicit_bank_lookup_emit import emit_explicit_bank_lookup
from m19_p0j_explicit_bank_stage_emit import emit_explicit_bank_stage
from m19_p0a_multi_bob_abk import parse_payload
from amos_link_test_support import relocate

class StageMachine(ExplicitMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.stage_source,self.labels=emit_explicit_bank_stage()
        self.uc.mem_write(self.entry,relocate(self.stage_source,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['routed_paint_prechecked_entry']

    def stage(self,bank,owner=AMOS):
        for n,r in enumerate(DR):self.uc.reg_write(r,0x660000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x43000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[4],GFX)
        self.uc.reg_write(DR[3],bank)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.explicit_shadow_writes=[]
        self.in_explicit_lookup=True # existing native selector write hook
        try:
            self.uc.emu_start(self.entry+self.labels['explicit_registry_prepare_entry'],
                              STOP,count=14000000)
        finally:
            self.in_explicit_lookup=False
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert not self.explicit_shadow_writes,('P0j-b2 selector was written',
                                                self.explicit_shadow_writes)
        for r,v in before.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('P0j-b2 ABI',r)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3)

def main():
    lib,meta=build()
    assert meta['public_commands']==85 and meta['ap20_entries']==178
    assert meta['native_groups']==[142,153,156,177] and meta['max_pc16']<1000
    old,_=emit_explicit_bank_lookup()
    native,labels=emit_explicit_bank_stage()
    assert native.startswith(old)
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(native[len(old):],0x100000+len(old)))
    assert dis and sum(x.size for x in dis)==len(native)-len(old)
    assert all(not x.mnemonic.startswith('dc.') for x in dis)
    tests=0
    original,_=build_p0c()
    for layout in ('interpreted','compiled'):
        m=StageMachine(original,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        m.activate_aga_state();m.configure_real_state()
        selected=m.selected_triple() # bank 11
        assert m.stage(10)==1,(layout,'source10',m.root(),m.metadata)
        assert m.selected_triple()==selected
        assert len(m.chip_live)==1 and len(m.metadata)==1
        assert m.stage(11)==1,(layout,'source11',m.root(),m.metadata)
        assert m.selected_triple()==selected
        assert len(m.chip_live)==2 and len(m.metadata)==2
        tests+=6
        for bank in (10,11):
            status,out=m.lookup(bank)
            assert status==1,(layout,bank,m.root(),m.nodes())
            chip=int.from_bytes(out[8:12],'big')
            count=int.from_bytes(out[12:16],'big')
            images=parse_payload(m.bank_payload(bank)).images
            expected=b''.join(img.planes+(img.mask or b'')
                              for img in images)
            assert bytes(m.uc.mem_read(chip,count))==expected
            assert m.selected_triple()==selected
            tests+=4
        allocated=m.chip_allocs
        assert m.stage(10)==1 and m.stage(11)==1
        assert len(m.chip_live)==2 and m.chip_allocs==allocated
        tests+=2
        before=(m.root(),m.nodes(),dict(m.chip_live),m.selected_triple())
        assert m.stage(12)==0
        assert (m.root(),m.nodes(),dict(m.chip_live),m.selected_triple())==before
        assert m.stage(10,owner=AMOS+0x1000)==0
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.stage(10)==0
        m.uc.mem_write(EXEC+0x128,b'\x00\x02')
        assert m.stage(10)==1
        tests+=5
        assert m.call('registry_close_entry')==1
        assert not m.chip_live and not m.metadata
        tests+=2
    print('M19 P0j-b2 MC68020 EXPLICIT AGBO CHIP STAGE GATE A PASS',
          tests,'tests, two unrelated V2 placements, real P0c full validator,',
          'original banks 10+11 staged while bank11 selected, ZERO selector writes;',
          'NO public Draw/WinUAE/real Compiler')

if __name__=='__main__':
    main()
