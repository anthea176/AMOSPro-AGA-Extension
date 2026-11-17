#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b1: actual MC68020 original-bank lookup never touches selector."""
from __future__ import annotations
from struct import unpack
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m5_generic import DR,AR,STACK,STOP
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from test_m5_generic import AMOS,EXEC
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0j_frame_image_preflight_gate_a import ImageGateMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0j_explicit_bank_lookup_in_memory import build
from m19_p0j_frame_image_preflight_emit import emit_image_preflight
from m19_p0j_explicit_bank_lookup_emit import emit_explicit_bank_lookup
from amos_link_test_support import relocate

OUT=0x43100
CANARY=b'Z'*28


class ExplicitMachine(ImageGateMachine):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.native_explicit,self.labels=emit_explicit_bank_lookup()
        self.uc.mem_write(self.entry,relocate(
            self.native_explicit,self.entry,{},self.uc))
        self.labels['routed_paint_all_entry']=self.labels['routed_paint_prechecked_entry']
        self.explicit_trace=[]
        from unicorn import UC_HOOK_CODE
        for key in ('explicit_bank_lookup_entry','explicit_lookup_node',
                    'explicit_lookup_found','explicit_lookup_return',
                    'chip_lookup_entry'):
            addr=self.entry+self.labels[key]
            def watch(uc,address,size,label):
                self.explicit_trace.append((label,self.d(0),self.d(3),
                    self.a(1),self.a(2),self.get(self.a(2)+12)
                    if 0x50000<=self.a(2)<0xe00000 else 0))
            self.uc.hook_add(UC_HOOK_CODE,watch,user_data=key,
                             begin=addr,end=addr)

    def os_call(self,uc,address,size,user):
        # OUT is mapped writable scratch. The inherited test stub only
        # marks addresses >=0x50000 as PUBLIC, but this harness passes A1
        # at 0x43100. Model that exact mapped 28-byte output as PUBLIC.
        if address==EXEC-534 and OUT<=self.a(1)<OUT+28:
            return self._os_return(1)
        return super().os_call(uc,address,size,user)

    def lookup(self,bank,owner=AMOS):
        self.uc.mem_write(OUT,CANARY)
        # Independent ABI harness: explicit-bank entry takes D3=bank,
        # NOT D0, as P0i's object-ID drawing entry does.
        for n,r in enumerate(DR):
            self.uc.reg_write(r,0x770000+n)
        for n,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x43000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[1],OUT)
        self.uc.reg_write(DR[3],bank)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(self.entry+self.labels['explicit_bank_lookup_entry'],
                          STOP,count=13000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for reg,previous in old.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==previous,('explicit-bank ABI',reg)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3),bytes(self.uc.mem_read(OUT,28))

def prepare(layout):
    original,_=build_p0c()
    m=ExplicitMachine(original,layout)
    assert m.run_select(10)==1 and m.run_get(1,4,5,20,8)==1
    assert m.run_select(11)==1 and m.run_get(1,7,8,16,15)==1
    m.activate_aga_state()
    m.configure_real_state()
    assert m.run_select(10)==1
    assert m.public('bob',ident=1,x=5,y=7,image=1)==1
    assert m.run_select(11)==1
    assert m.public('bob',ident=2,x=9,y=11,image=1)==1
    return m

def main():
    source,meta=build()
    assert meta['public_commands']==85 and meta['ap20_entries']==178
    assert meta['native_groups']==[142,153,156,177]
    old,_=emit_image_preflight()
    native,labels=emit_explicit_bank_lookup()
    assert native.startswith(old)
    raw=native[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(raw,0x100000+len(old)))
    assert ins and sum(i.size for i in ins)==len(raw)
    assert all(not i.mnemonic.startswith('dc.') for i in ins)
    checks=0
    for layout in ('interpreted','compiled'):
        m=prepare(layout)
        selection=m.selected_triple()
        # Without staging, the original source exists but no Chip cache.
        assert m.lookup(10)==(0,CANARY)
        assert m.lookup(11)==(0,CANARY)
        assert m.selected_triple()==selection
        checks+=3

        # Use existing P0i one-time staging to isolate *only* lookup.
        assert m.route('all')==1
        cache=dict(m.chip_live)
        selection=m.selected_triple()
        assert len(cache)==2
        for bank in (10,11):
            ok,out=m.lookup(bank)
            assert ok==1,(layout,bank,out,m.explicit_trace[-35:],
                           m.root(),m.nodes() if m.metadata else {},
                           m.selected_triple().hex(),m.chip_live)
            payload,generation,chip,chiplen,ctx,bnum,head=unpack('>7I',out)
            assert payload==m.find(bank)+24
            assert generation==m.get(payload+24)
            assert chip in cache and chiplen>0
            assert bnum==bank and head==HEAD,(layout,bank,head,HEAD)
            assert ctx and ctx%2==0
            assert m.selected_triple()==selection
            checks+=8

        # Drop the original bank generation, while cached Chip is unchanged.
        node=m.find(10)
        generation=m.get(node+24+24)
        m.put(node+24+24,generation+1)
        assert m.lookup(10)==(0,CANARY)
        assert m.selected_triple()==selection
        m.put(node+24+24,generation)
        assert m.lookup(10)[0]==1
        checks+=3

        old_head=m.get(HEAD)
        m.put(HEAD,0)
        assert m.lookup(10)==(0,CANARY)
        m.put(HEAD,old_head)
        assert m.lookup(10)[0]==1
        checks+=2

        for bank in (0,4,12,65536):
            assert m.lookup(bank)==(0,CANARY)
        assert m.lookup(10,owner=AMOS+0x1000)==(0,CANARY)
        checks+=5

        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.lookup(10)==(0,CANARY)
        m.uc.mem_write(EXEC+0x128,b'\x00\x02')
        assert m.lookup(10)[0]==1
        checks+=2

        assert m.selected_triple()==selection
        m.invoke('bridge')
        assert not m.chip_live and not m.metadata
        assert m.lookup(10)==(0,CANARY)
        checks+=3
    print('M19 P0j-b1 REAL MC68020 EXPLICIT-BANK CHIP LOOKUP GATE A PASS',
          checks,'cases, 2 native disjoint placements, original banks 10/11,',
          'stale Erase/generation and wrong owner refused; global selector',
          'NEVER written; NO public Draw, WinUAE or true Compiler')

if __name__=='__main__':
    main()
