#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""MC68020 CPU Gate A for PRIVATE per-bank Chip stage registry.

Exec, graphics and AMOS calls are mocked, never real DMA or actual Compiler.
The full compiled source prefix remains byte-identical to P0b/P0c.
"""
from __future__ import annotations

from struct import pack
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from test_m5_generic import DR,AR,AMOS,EXEC,GFX,STACK,STOP
from amos_link_test_support import relocate
from build_m19_p0b_masks_in_memory import build
from m19_p0c_bank_registry_emit import emit_bank_registry,NODE_SIZE,META_FLAGS
from m19_p0c_checked_bank_stage_emit import emit_checked_bank_stage
from m19_p0c_chip_stage_emit import COOKIE
from test_m19_p0c_checked_bank_stage_native import BankChipMachine,CHIP_START
from m19_p0a_multi_bob_abk import parse_payload

META_BASE=0xc00000


class RegistryMachine(BankChipMachine):
    def __init__(self, binary, layout='interpreted', depth=8,
                 *, chip_fail=False, meta_fail=False, bad_type=None):
        super().__init__(binary, layout=layout, depth=depth,
                         chip_fail=chip_fail, bad_type=bad_type)
        self.native,self.labels=emit_bank_registry()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))
        self.metadata={}
        self.next_metadata=META_BASE
        self.metadata_allocs=0
        self.metadata_frees=0
        self.meta_fail=meta_fail
        self.registry_addr=self.entry+self.labels['registry_state']
        self.registry_entries={
            name:self.entry+self.labels[name] for name in
            ('registry_prepare_entry','registry_lookup_entry',
             'registry_free_entry','registry_close_entry')
        }

    def root(self):
        return self.get(self.registry_addr),self.get(self.registry_addr+4)

    def nodes(self):
        owner,cur=self.root()
        found={}
        visited=set()
        for _ in range(257):
            if not cur:
                return found
            assert cur not in visited,'registry cycle'
            assert cur in self.metadata,('foreign node',hex(cur))
            visited.add(cur)
            ident=self.get(cur+4)
            assert ident not in found,'duplicate bank context'
            found[ident]=(cur,tuple(self.get(cur+8+4*i) for i in range(5)))
            cur=self.get(cur)
        raise AssertionError('unbounded registry list')

    def os_call(self, uc, address, size, user):
        if address==EXEC-684 and self.d(1)==META_FLAGS and self.d(0)==NODE_SIZE:
            self.metadata_allocs+=1
            if self.meta_fail:
                return self._os_return(0)
            ptr=self.next_metadata
            self.next_metadata+=(NODE_SIZE+16+15)&~15  # leave gap for test canary
            assert self.next_metadata<CHIP_START
            self.metadata[ptr]=NODE_SIZE
            self.uc.mem_write(ptr,bytes(NODE_SIZE))
            self.uc.mem_write(ptr+NODE_SIZE,b'\xa5\x5a\xab\xcd')
            return self._os_return(ptr)
        if address==EXEC-690 and self.a(1) in self.metadata:
            ptr=self.a(1)
            assert not self.pending_dma, 'metadata freed during pending DMA'
            assert bytes(self.uc.mem_read(ptr+NODE_SIZE,4))==b'\xa5\x5a\xab\xcd'
            self.metadata_frees+=1
            del self.metadata[ptr]
            return self._os_return(0)
        return super().os_call(uc,address,size,user)

    def call(self,name,bank=10,*,gfx=GFX,owner=AMOS,limit=12000000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1230+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[4],gfx)
        self.uc.reg_write(DR[3],bank)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.registry_entries[name],STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('registry CPU fault',name,str(exc),
                                  hex(self.uc.reg_read(UC_M68K_REG_PC)),
                                  self.root(),self.nodes() if self.metadata else {},
                                  sorted(self.chip_live))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'registry stack not restored'
        for reg,val in old.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==val,('registry ABI',name,reg)
        assert self.d(2)==0
        assert self.d(3) in (0,1)
        assert self.plane_writes==0,'registry scribbled screen DMA'
        return self.d(3)


def ready(binary, layout='interpreted', depth=8, **kw):
    m=RegistryMachine(binary,layout,depth,**kw)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_get(2,6,5,36,8)==1
    assert m.mask(True,1,0)==1
    return m


def pix(m,n):
    bank=parse_payload(m.bank_payload(n))
    return b''.join(im.planes+(im.mask or b'') for im in bank.images)


def main():
    binary,meta=build()
    assert meta['sha256']=='f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9'
    raw,labels=emit_bank_registry()
    prev,_=emit_checked_bank_stage()
    assert raw[:len(prev)]==prev,'previous native unit changed'
    assert raw==emit_bank_registry()[0],'nonreproducible emitter'
    assert raw[labels['registry_state']:]==bytes(8),'persistent root not zero'
    dis=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).disasm(
        raw[labels['registry_prepare_entry']:labels['registry_state']],
        0x100000+labels['registry_prepare_entry']))
    assert sum(i.size for i in dis)==labels['registry_state']-labels['registry_prepare_entry']
    assert not any(i.mnemonic.startswith('dc.') for i in dis)

    cases=0
    for layout in ('interpreted','compiled'):
        # First capture, second capture: one metadata node, two Chip allocations,
        # old source must be freed only after WaitBlit.
        m=ready(binary,layout)
        assert m.root()==(0,0)
        assert m.call('registry_lookup_entry')==0
        assert m.call('registry_prepare_entry')==1
        assert m.root()[0]==AMOS
        first=m.nodes()[10]
        assert first[1][4]==COOKIE
        assert bytes(m.uc.mem_read(first[1][0],first[1][1]))==pix(m,10)
        assert len(m.metadata)==1 and len(m.chip_live)==1
        assert (m.metadata_allocs,m.metadata_frees,m.chip_allocs,m.chip_frees)==(1,0,1,0)
        assert m.call('registry_lookup_entry')==1
        cases+=3

        m.pending_dma=True
        assert m.call('registry_prepare_entry')==1
        second=m.nodes()[10]
        assert second[0]==first[0] and second[1][0]!=first[1][0]
        assert not m.pending_dma and m.chip_frees==1
        assert m.metadata_allocs==1 and m.chip_allocs==2
        cases+=1

        # A failed refresh preserves the previous source and node without leak.
        m.chip_fail=True
        saved=m.nodes()[10]
        assert m.call('registry_prepare_entry')==0
        assert m.nodes()[10]==saved and len(m.chip_live)==1
        assert m.metadata_allocs==1
        m.chip_fail=False
        cases+=1

        # A replacement capture invalidates lookup until a new stage succeeds.
        assert m.run_get(1,4,5,20,9)==1
        assert m.call('registry_lookup_entry')==0
        assert m.call('registry_prepare_entry')==1
        assert m.call('registry_lookup_entry')==1
        cases+=3

        # Second bank is a distinct CHIP buffer and metadata node.
        assert m.run_select(11)==1
        assert m.run_get(1,0,0,10,2)==1
        assert m.call('registry_prepare_entry',bank=11)==1
        two=m.nodes()
        assert set(two)=={10,11}
        assert two[10][0]!=two[11][0]
        assert two[10][1][0]!=two[11][1][0]
        assert bytes(m.uc.mem_read(two[11][1][0],two[11][1][1]))==pix(m,11)
        assert m.call('registry_lookup_entry',bank=11)==1
        assert m.call('registry_lookup_entry',bank=10)==0,'not selected bank'
        assert m.run_select(10)==1
        assert m.call('registry_lookup_entry',bank=10)==1
        cases+=3

        # A5 program identity protects the registry from foreign programs.
        n_chips=len(m.chip_live)
        assert m.call('registry_prepare_entry',owner=AMOS+0x100)==0
        assert m.call('registry_close_entry',owner=AMOS+0x100)==0
        assert len(m.chip_live)==n_chips and len(m.nodes())==2
        cases+=2

        # Free one bank; keep another. An empty duplicate free is a no-op.
        m.pending_dma=True
        assert m.call('registry_free_entry',bank=10)==1
        assert not m.pending_dma
        assert set(m.nodes())=={11} and len(m.chip_live)==1
        assert m.call('registry_free_entry',bank=10)==1
        assert m.call('registry_lookup_entry',bank=10)==0
        cases+=3

        # A false GfxBase must preserve the node rather than leak or FreeVec.
        m.pending_dma=True
        assert m.call('registry_close_entry',gfx=0)==0
        assert 11 in m.nodes() and len(m.chip_live)==1
        assert m.pending_dma
        assert m.call('registry_close_entry')==1
        assert not m.pending_dma and not m.chip_live and not m.metadata
        assert m.root()==(0,0)
        assert m.call('registry_close_entry')==1
        cases+=3

        # Failed first allocation never publishes a metadata node or owner.
        for failures in ({'meta_fail':True},{'chip_fail':True},
                         {'bad_type':'first'},{'bad_type':'last'}):
            m=ready(binary,layout,**failures)
            assert m.call('registry_prepare_entry')==0
            assert m.root()==(0,0)
            assert not m.metadata and not m.chip_live
            assert m.metadata_allocs==m.metadata_frees or m.meta_fail
            cases+=1

        # Calling before any Bob capture on an empty AGBO must not leak.
        m=RegistryMachine(binary,layout)
        assert m.run_select(10)==1
        assert m.call('registry_prepare_entry')==0
        assert m.root()==(0,0) and not m.metadata and not m.chip_live
        cases+=1

        # Wrong selected bank / out-of-range numbers / CPU guard.
        for args in ((4,AMOS),(65536,AMOS),(11,AMOS),(10,0)):
            m=ready(binary,layout)
            assert m.call('registry_prepare_entry',bank=args[0],owner=args[1])==0
            assert m.root()==(0,0) and not m.metadata
            cases+=1
        m=ready(binary,layout)
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.call('registry_prepare_entry')==0
        assert m.call('registry_close_entry')==0
        cases+=2

        # Multiple buffers free on one close, including when the old AMOS
        # bank disappears; cleanup does NOT re-read removed bank pointers.
        m=ready(binary,layout)
        assert m.call('registry_prepare_entry')==1
        assert m.run_select(11)==1
        assert m.run_get(1,0,0,10,3)==1
        assert m.call('registry_prepare_entry',bank=11)==1
        assert len(m.nodes())==2
        m.pending_dma=True
        m.put(0x59800,0)   # AMOS bank-list HEAD removed (test fixture)
        assert m.call('registry_close_entry')==1
        assert m.root()==(0,0) and not m.metadata and not m.chip_live
        assert not m.pending_dma
        assert m.metadata_allocs==m.metadata_frees
        assert m.chip_allocs==m.chip_frees
        cases+=2

    print('M19 P0c PRIVATE MC68020 bank REGISTRY Gate A PASS',cases,
          'scenarios; compiled-style/interpreted-style relocations,',
          'unit bytes',len(raw),'node bytes',NODE_SIZE,
          'no installed .Lib, no screen-close hook, no WinUAE/Compiler')


if __name__=='__main__':main()
