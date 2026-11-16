#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A CPU020 for PRIVATE AGA preclose guard, NOT installed Screen Close.

Tests full source-native chain P0b -> P0c registry -> preclose. Exec/graphics
are MOCKED. A model callback checks legacy-close ordering; the actual R88
Aga Screen Close and AMOS Compiler are NOT exercised by this test.
"""
from __future__ import annotations

from struct import pack, unpack_from

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from test_m5_generic import AMOS,EXEC,GFX
from amos_link_test_support import relocate
from test_m19_p0c_bank_registry_native import RegistryMachine, ready as base_ready
from test_m19_p0a_r88_get_gate_a import STATE,HEAD
from m19_p0c_bank_registry_emit import emit_bank_registry
from m19_p0c_screen_preclose_emit import emit_screen_preclose
from build_m19_p0b_masks_in_memory import build
from compiler_relocation import RBSR,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2

class PreCloseMachine(RegistryMachine):
    def __init__(self,lib,layout='interpreted',depth=8,**kw):
        super().__init__(lib,layout,depth,**kw)
        self.native,self.labels=emit_screen_preclose()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.registry_entries={name:self.entry+self.labels[name]
            for name in ('registry_prepare_entry','registry_lookup_entry',
                         'registry_free_entry','registry_close_entry',
                         'screen_preclose_entry')}
        self.registry_addr=self.entry+self.labels['registry_state']
        self.legacy_closes=0

    def legacy_close_mock(self):
        """MODEL, not the real AGA Close: must be called ONLY after preclose."""
        assert self.root()==(0,0), 'registry still active'
        assert not self.metadata and not self.chip_live, 'leaked Chip allocation'
        assert self.get(STATE+8)==GFX, 'GfxBase destroyed too early'
        self.legacy_closes+=1
        self.put(STATE+8,0)
        self.put(STATE+0,0)   # simplified screen cleanup event

def ready(lib,layout='interpreted',depth=8):
    m=PreCloseMachine(lib,layout,depth)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_get(2,6,5,36,8)==1
    assert m.mask(True,1,0)==1
    return m

def main():
    prefix,_=emit_bank_registry()
    source,labels=emit_screen_preclose()
    assert source[:len(prefix)]==prefix,'previous verified prefix changed'
    assert source==emit_screen_preclose()[0],'source not deterministic'
    assert labels['screen_preclose_entry']==len(prefix)
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).disasm(
        source[len(prefix):],0x100000+len(prefix)))
    assert sum(i.size for i in dis)==len(source)-len(prefix)
    assert not any(i.mnemonic.startswith('dc.') for i in dis)
    lib,meta=build()
    assert meta['sha256']=='f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9'

    # Prove current public Aga Screen Close is STILL in the legacy AGA native
    # group. The new BOBS preclose has no cross-unit 16-bit branch to it.
    _tokens,parts,_title=unpack_ap20(lib)
    close_stub=parts[8]
    assert close_stub[:2]==RBSR and close_stub[6:8]==b'\x4e\x75'
    group,close_offset=unpack_from('>HH',close_stub,2)
    assert group==88,('legacy public entry 8 group',group,'offset',close_offset,'stub',close_stub.hex())
    assert parts[group].startswith(DISPATCH_V2)
    assert 0<=close_offset<len(parts[group])-len(DISPATCH_V2)
    assert len(parts[group])>32766,'AGA native unit unexpectedly shrank'
    assert parts[90].startswith(DISPATCH_V2),'BOBS native unit moved'

    cases=0
    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m=ready(lib,layout,depth)
            assert m.call('registry_prepare_entry')==1
            assert 10 in m.nodes()
            m.pending_dma=True
            assert m.call('screen_preclose_entry',gfx=0)==1,                'preclose must read GfxBase from State+8, NOT caller A4'
            assert m.root()==(0,0)
            assert not m.metadata and not m.chip_live
            assert not m.pending_dma
            assert m.get(STATE+8)==GFX,'preclose closed GfxBase'
            assert m.get(STATE+0)!=0,'preclose changed screen pointer'
            m.legacy_close_mock()
            assert m.legacy_closes==1
            assert m.call('screen_preclose_entry',gfx=0)==1
            cases+=3

        # Two bank contexts are cleaned before the screen is destroyed.
        m=ready(lib,layout,8)
        assert m.call('registry_prepare_entry')==1
        assert m.run_select(11)==1
        assert m.run_get(1,0,0,10,3)==1
        assert m.call('registry_prepare_entry',bank=11)==1
        assert len(m.nodes())==2
        m.pending_dma=True
        assert m.call('screen_preclose_entry',gfx=0)==1
        assert not m.pending_dma and not m.metadata and not m.chip_live
        assert m.metadata_allocs==m.metadata_frees
        assert m.chip_allocs==m.chip_frees
        assert m.get(STATE+8)==GFX
        m.legacy_close_mock()
        cases+=2

        # Disappeared AMOS bank must not prevent ownership cleanup.
        m=ready(lib,layout,8)
        assert m.call('registry_prepare_entry')==1
        m.put(HEAD,0)
        assert m.call('screen_preclose_entry',gfx=0)==1
        assert not m.metadata and not m.chip_live
        cases+=1

        # No active resources: missing screen and graphics base is idempotent.
        m=ready(lib,layout,8)
        m.put(AMOS+0x1c8,0)
        assert m.call('screen_preclose_entry',gfx=0)==1
        assert m.call('screen_preclose_entry',gfx=0)==1
        assert m.root()==(0,0)
        cases+=2

        # Missing GfxBase with ACTIVE DMA resources: FAIL and preserve owner.
        m=ready(lib,layout,8)
        assert m.call('registry_prepare_entry')==1
        old=m.nodes()
        m.pending_dma=True
        m.put(STATE+8,0)
        assert m.call('screen_preclose_entry')==0
        assert m.nodes()==old and m.pending_dma
        assert m.get(STATE+0)!=0
        assert m.legacy_closes==0
        m.put(STATE+8,GFX)
        assert m.call('screen_preclose_entry')==1
        assert not m.pending_dma and not m.chip_live
        cases+=2

        # Missing or invalid screen state must not close a dirty context.
        for state in (0,0x1000,0xffffffff):
            m=ready(lib,layout,8)
            assert m.call('registry_prepare_entry')==1
            before=m.nodes()
            m.put(AMOS+0x1c8,state)
            assert m.call('screen_preclose_entry')==0
            assert m.nodes()==before
            assert len(m.chip_live)==1 and m.legacy_closes==0
            cases+=1

        # Foreign A5 must not close the original program's resource list.
        m=ready(lib,layout,8)
        assert m.call('registry_prepare_entry')==1
        before=m.nodes()
        assert m.call('screen_preclose_entry',owner=AMOS+0x100)==0
        assert m.nodes()==before and len(m.chip_live)==1
        cases+=1

        # CPU preflight must be before all AGA state dereferences.
        m=ready(lib,layout,8)
        assert m.call('registry_prepare_entry')==1
        before=m.nodes()
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.call('screen_preclose_entry')==0
        assert m.nodes()==before
        cases+=1

    print('M19 P0c PRIVATE MC68020 preclose Gate A PASS',
          cases,'scenarios; native unit',len(source),
          'bytes; legacy screen close ORDER MODEL ONLY, not an installed hook',
          'or AMOS Compiler/WinUAE test')

if __name__=='__main__':
    main()
