#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0h Gate A: native 64-object raw+checked read, fail before DMA.

Executes source-emitted MC68020 BOBS/AGA code in two disjoint layouts.
AMOS and Exec are mocked. Does not test Chip staging, Blitter or compiler.
"""
from __future__ import annotations

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from test_m5_generic import DR, AR, AMOS, EXEC, STACK, STOP
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0g_checked_read_gate_a import CheckedMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0h_frame_preflight_in_memory import build
from m19_p0g_checked_read_emit import emit_checked_read
from m19_p0h_frame_preflight_emit import emit_frame_preflight, MAX_BOBS
from amos_link_test_support import relocate


class FrameMachine(CheckedMachine):
    def __init__(self, source, layout):
        super().__init__(source, layout)
        self.frame_native,self.labels = emit_frame_preflight()
        self.uc.mem_write(self.entry,relocate(
            self.frame_native,self.entry,{},self.uc))
        self.raw_reads=0
        self.secure_reads=0
        def on_read(uc,address,size,kind):
            if kind=='raw':
                self.raw_reads+=1
            else:
                self.secure_reads+=1
        for kind,key in [('raw','relay_read_entry'),
                         ('checked','relay_checked_read_entry')]:
            address=self.entry+self.labels[key]
            self.uc.hook_add(UC_HOOK_CODE,on_read,user_data=kind,
                             begin=address,end=address)

    def preflight(self, owner=AMOS, limit=15000000):
        for n,r in enumerate(DR):
            self.uc.reg_write(r,0x510000+n)
        for n,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40100+n*0x100)
        self.uc.reg_write(AR[5],owner)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(
                self.entry+self.labels['frame_bank_preflight_entry'],
                STOP,count=limit)
        except Exception as error:
            raise AssertionError(('P0h native frame preflight CPU020 fault',
                str(error),hex(self.uc.reg_read(UC_M68K_REG_PC)),
                self.raw_reads,self.secure_reads)) from error
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for reg,v in old.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==v,('AMOS ABI register changed',reg)
        return self.d(3)


def main():
    p0c,_=build_p0c()
    image,meta=build()
    assert meta['public_commands']==85 and meta['native_groups'].__len__()==4
    assert meta['interpreter_pc16'] < 1000
    assert meta['appended_bytes'] > 176
    old,_=emit_checked_read()
    new,labels=emit_frame_preflight()
    assert new.startswith(old) and labels['frame_bank_preflight_entry']==len(old)
    code=new[len(old):]
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        .disasm(code,0x120000))
    assert sum(x.size for x in ins)==len(code)
    assert all(not x.mnemonic.startswith('dc.') for x in ins)
    cases=0
    for layout in ('interpreted','compiled'):
        m=FrameMachine(p0c,layout)
        # An unopened AGA State cannot make an empty frame look successful.
        assert m.preflight()==0
        assert m.raw_reads==0
        m.activate_aga_state()
        assert m.preflight()==1
        assert m.raw_reads==64 and m.secure_reads==0
        cases+=3

        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=103,y=72,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=-5,y=31,image=1)==1
        before_raw, before_checked=m.raw_reads,m.secure_reads
        unchanged=(m.table(),m.shadows())
        assert m.preflight()==1
        assert m.raw_reads-before_raw==64
        assert m.secure_reads-before_checked==2
        assert (m.table(),m.shadows())==unchanged
        cases+=4

        # An active stale object aborts before any future drawing;
        # raw object 1 remains readable but its stamp no longer matches.
        node=m.find(10)
        generation=m.get(node+24+24)
        m.put(node+24+24,generation+1)
        before_raw, before_checked=m.raw_reads,m.secure_reads
        assert m.preflight()==0
        assert m.raw_reads-before_raw==1
        assert m.secure_reads-before_checked==1
        assert (m.table(),m.shadows())==unchanged
        m.put(node+24+24,generation)
        assert m.preflight()==1
        cases+=5

        saved=m.get(HEAD)
        m.put(HEAD,0)
        assert m.preflight()==0
        m.put(HEAD,saved)
        assert m.preflight()==1
        cases+=2

        assert m.public('off',ident=1)==1
        assert m.preflight()==1
        assert m.public('off',ident=2)==1
        assert m.preflight()==1
        cases+=2

        m.uc.mem_write(EXEC+0x128,b'\0\0')
        previous=m.raw_reads
        assert m.preflight()==0 and m.raw_reads==previous
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        assert m.preflight()==1
        cases+=2

        assert m.preflight(owner=AMOS+0x1000)==0
        oldscreen=m.get(m.real_state)
        m.put(m.real_state,0)
        assert m.preflight()==0
        m.put(m.real_state,oldscreen)
        assert m.preflight()==1
        cases+=3

        # Exercise the top boundary (ID=64), always in ascending order.
        assert m.run_select(10)==1
        assert m.public('bob',ident=64,x=0,y=0,image=1)==1
        start_raw,start_checked=m.raw_reads,m.secure_reads
        assert m.preflight()==1
        assert m.raw_reads-start_raw==64 and m.secure_reads-start_checked==1
        cases+=2

        # Off+reset: zero objects is valid; no stale shadow authorization.
        assert m.relay_call('reset')[0]==1
        assert m.preflight()==1
        cases+=2

    print('M19 P0h MC68020 64-OBJECT BANK PREFLIGHT GATE A PASS',
          cases,'checks; two disjoint native V2 placements, full ID 1..64,',
          'active stale bank fails BEFORE DMA; NO Draw/Chip/WinUAE claims')


if __name__=='__main__':
    main()
