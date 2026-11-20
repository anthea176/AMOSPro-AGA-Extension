#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0 Bank Free native/ABI Gate A, two independent MC68020 relocations.

The exact native BOBS unit runs under Unicorn MC68020 with mocked AMOS,
Exec, graphics.library, Blitter and AGA. NOT a WinUAE Runtime/Compiler test.
"""
from __future__ import annotations

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from amos_link_test_support import relocate
from test_m5_generic import AMOS
from test_m19_p0c_screen_close_real_gate_a import GFX
from test_m19_p0j_pending_close_end_gate_a import DB
from test_m19_b8_s1_bank_prestage_gate_a import Prestaged
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_b8_s1_bank_free_in_memory import build_bank_free
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_b8_s1_bank_prestage_emit import emit_b8_s1_bank_prestage
from m19_p0e_object_table_emit import emit_object_table
from m19_p0e_v2_object_bridge_emit import OBJ_RELATIVE
from m19_p0j_swap_barrier_emit import READY,DIRTY
from compiler_relocation import unpack_ap20,RBSR
from struct import unpack_from

OBJECT, OBJ=emit_object_table()

class FreeMachine(Prestaged):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.native,self.labels=emit_b8_s1_bank_free()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))

    def free(self,bank):
        # Call the native FREE AP20 target with exactly the public bank
        # instruction register context; do not rebase the fixture.
        key='b8s1_bank_prestage_entry'
        original=self.labels[key]
        self.labels[key]=self.labels['b8s1_bank_free_entry']
        try:
            return super().run_select(bank)
        finally:
            self.labels[key]=original

def prepared(layout, *, with_bobs=True):
    src,_=build_p0c()
    m=FreeMachine(src,layout)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    m.activate_aga_state()
    m.configure_real_state()
    assert m.run_select(10)==1
    assert m.run_select(11)==1
    assert set(m.nodes())=={10,11}
    if with_bobs:
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=5,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=9,y=11,image=1)==1
    return m

def main():
    image,meta=build_bank_free()
    assert image==build_bank_free()[0]
    assert meta['predecessor_sha']=='577fe698f040a13ea0a12c88fc80f31fd316eed011a305955eb5be635c8613bf'
    assert meta['public_commands']==89 and meta['ap20_entries']==185
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['pc16_max']<32766 and meta['old_bobs_prefix_byte_exact']
    toks,parts,_=unpack_ap20(image)
    assert parts[184][:2]==RBSR
    assert unpack_from('>HH',parts[184],2)==(177,meta['free_native_offset'])
    old,_=emit_b8_s1_bank_prestage()
    raw,labs=emit_b8_s1_bank_free()
    assert raw.startswith(old) and labs['b8s1_bank_free_entry']==len(old)
    dec=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(raw[len(old):],0x10000+len(old)))
    assert dec and sum(x.size for x in dec)==len(raw)-len(old)
    assert not any(x.mnemonic.startswith('dc.') for x in dec)
    checks=12

    for layout in ('interpreted','compiled'):
        m=prepared(layout)
        data10=m.bank_payload(10);data11=m.bank_payload(11)
        chosen=m.selected_triple()
        m.pending_dma=True
        assert m.free(10)==1
        assert not m.pending_dma and m.chip_frees==1
        assert set(m.nodes())=={11} and len(m.chip_live)==1
        assert m.bank_payload(10)==data10 and m.bank_payload(11)==data11
        assert m.find(10)!=0 and m.find(11)!=0
        assert m.selected_triple()==chosen
        assert m.relay_call('read',ident=1)[0]==0
        assert m.relay_call('read',ident=2)[0]==1
        assert m.free(10)==1  # idempotent, bank AMOS still present.
        assert m.chip_frees==1
        assert m.frame()==1 and m.status()==READY
        assert m.free(11)==0  # READY frame: do not invalidate display.
        assert set(m.nodes())=={11} and m.status()==READY
        assert m.relay_call('read',ident=2)[0]==1
        assert m.invoke_guard('swap')==1
        m.put(DB+20,0)
        assert m.free(11)==1 and m.chip_frees==2
        assert not m.chip_live and not m.metadata
        assert m.relay_call('read',ident=2)[0]==0
        checks+=18

        # A freed selected bank is deselected but is still an AMOS bank.
        n=prepared(layout)
        assert n.run_select(10)==1
        assert n.selected_triple()[:4] != bytes(4)
        assert n.free(10)==1 and n.selected_triple()==bytes(12)
        assert n.bank_payload(10)==data10
        assert n.public('bob',ident=3,image=1,x=12,y=14)==0
        assert n.run_select(10)==1
        assert 10 in n.nodes()
        assert n.public('bob',ident=3,image=1,x=12,y=14)==1
        checks+=7

        # A new/empty bank may be freed without Chip.
        e=prepared(layout,with_bobs=False)
        assert e.run_select(12)==1
        assert len(e.chip_live)==2
        assert e.free(12)==1
        assert len(e.chip_live)==2 and e.find(12)!=0
        assert e.selected_triple()==bytes(12)
        checks+=4

        # Invalid bank IDs and foreign A5 never change live object/cache.
        b=prepared(layout)
        prior=(b.selected_triple(),b.nodes().copy(),dict(b.chip_live))
        for bad in (0,4,65536,-1):
            assert b.free(bad)==0
            assert (b.selected_triple(),b.nodes(),b.chip_live)==prior
            checks+=2
        # Dirty/partially prepared frame must NEVER free a Chip source.
        assert b.frame()==1 and b.status()==READY
        assert b.free(10)==0 and b.chip_frees==0
        assert b.invoke_guard('swap')==1
        b.put(DB+20,0)
        assert b.free(10)==1
        checks+=4

        # Bad object root owner is checked before any Bob Off or Chip Free.
        f=prepared(layout)
        root=f.real_state+OBJ_RELATIVE+OBJ['object_root']
        f.put(root,AMOS+0x100)
        assert f.free(10)==0
        assert set(f.nodes())=={10,11} and f.chip_frees==0
        assert f.relay_call('read',ident=1)[0]==0 # foreign owner blocks reads
        f.put(root,AMOS)
        assert f.relay_call('read',ident=1)[0]==1
        assert f.free(10)==1
        checks+=5

        # A malformed object active flag cannot lead to a partial Free.
        z=prepared(layout)
        slot=z.real_state+OBJ_RELATIVE+OBJ['object_table']
        z.put(slot+16,2)
        assert z.free(10)==0 and set(z.nodes())=={10,11}
        assert z.chip_frees==0
        z.put(slot+16,1)
        assert z.free(10)==1
        checks+=3

        # Invalid graphics library/AGA State is fail closed.
        q=prepared(layout)
        q.put(q.real_state+8,0)
        assert q.free(10)==0 and set(q.nodes())=={10,11}
        q.put(q.real_state+8,GFX)
        assert q.free(10)==1
        checks+=3

    print('M19 P0 BANK FREE native MC68020 Gate A PASS',
          checks,'checks, two relocations, preserved AMOS banks')
    print('SOURCE_ONLY',meta)


if __name__=='__main__':
    main()
