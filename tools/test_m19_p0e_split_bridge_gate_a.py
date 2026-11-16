#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e split AGA/BOBS relay: REAL CPU020 two-layout native Gate A.

Uses the P0d source-pinned native AGA Init and P0e object table, with
actual emitted CPU020 instructions in disjoint V2 locations. Exec/graphics,
AMOS bank dispatch, and Compiler placements are mocked, NOT WinUAE/actual
AMOS Compiler. P0d canonical .Lib and sole ASC are NOT modified.
"""
from __future__ import annotations

from struct import unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_get_gate_a import ARGS
from test_m19_p0e_public_object_ops_gate_a import PublicObjectMachine
from test_m19_p0e_v2_object_bridge_native import CANARY,OUTPUT,OTHER
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0d_bob_blit_in_memory import build as build_p0d
from build_m19_p0e_split_public_in_memory import build as build_split
from m19_p0e_split_bridge_emit import (
    P0D,OBJ,AGA_CORE,AGA_CORE_LABELS,AGA_CORE_BASE,AGA_OFFSETS,
    AGA_OLD_GROUP,AGA_BRIDGE_DELTA,emit_split_bobs_public,
)
from compiler_relocation import unpack_ap20
from amos_link_test_support import relocate


class SplitMachine(PublicObjectMachine):
    def __init__(self,p0c,layout='interpreted',depth=8):
        super().__init__(p0c,layout,depth)
        self.public_native,self.labels=emit_split_bobs_public()
        self.uc.mem_write(self.entry,relocate(self.public_native,self.entry,{},self.uc))
        self.agabridge=self.aga+AGA_OLD_GROUP+len(OBJ)
        self.uc.mem_write(self.agabridge,AGA_CORE)
        self.core_calls=[]
        from unicorn import UC_HOOK_CODE
        for kind,relative in AGA_OFFSETS.items():
            target=self.agabridge+relative
            self.uc.hook_add(UC_HOOK_CODE,self._on_core,user_data=kind,
                             begin=target,end=target)

    def _on_core(self,uc,address,size,kind):
        self.core_calls.append(kind)

    def relay_call(self,kind,ident=1,bank=10,image=1,x=0,y=0,
                   *,owner=AMOS,output=OUTPUT,count=3000000):
        assert kind in ('put_selected','put','off','read','reset')
        self.uc.mem_write(OUTPUT,CANARY)
        for n,r in enumerate(DR):
            self.uc.reg_write(r,0x12340000+n)
        for n,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x30000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(DR[0],ident&0xffffffff)
        self.uc.reg_write(DR[1],bank&0xffffffff)
        self.uc.reg_write(DR[4],image&0xffffffff)
        self.uc.reg_write(DR[5],x&0xffffffff)
        self.uc.reg_write(DR[6],y&0xffffffff)
        self.uc.reg_write(AR[1],output)
        initial={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(
                self.entry+self.labels['relay_'+kind+'_entry'],STOP,count=count)
        except Exception as err:
            raise AssertionError(('split BOBS relay CPU020 fault',kind,
                hex(self.uc.reg_read(UC_M68K_REG_PC)),ident,bank,err,
                self.core_calls[-8:])) from err
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0
        for r,v in initial.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('split relay AMOS register clobber',kind,r)
        assert self.d(3) in (0,1)
        return self.d(3),bytes(self.uc.mem_read(OUTPUT,24))


def main():
    old,_=build_p0c()
    p0d,_=build_p0d()
    split,meta=build_split()
    _,oldparts,_=unpack_ap20(p0d)
    _,parts,_=unpack_ap20(split)
    assert meta['public_commands']==85 and meta['ap20_entries']==95
    assert parts[91:93]==oldparts[89:91]
    assert parts[93].startswith(oldparts[91])
    assert parts[94].startswith(oldparts[92])
    assert parts[94][len(oldparts[92]):]==OBJ+AGA_CORE
    assert meta['pc16_margin']>=80 and meta['interpreter_reach']<32766
    data,lab=emit_split_bobs_public()
    assert data.startswith(P0D)
    insn=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
             disasm(data[len(P0D):],0x110000))
    assert sum(i.size for i in insn)==len(data)-len(P0D)
    assert all(not x.mnemonic.startswith('dc.') for x in insn)
    aga_insn=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
                 disasm(AGA_CORE,0x500000))
    assert sum(i.size for i in aga_insn)==len(AGA_CORE)

    tests=0
    for layout in ('interpreted','compiled'):
        m=SplitMachine(old,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
        # Old fake capture State is not an actual native AGA anchor.
        assert m.public('bob',ident=1,image=1)==0
        assert m.table()==bytes(len(m.table()))
        tests+=1
        m.activate_aga_state()  # executes ORIGINAL AGA Init from P0d ancestry
        assert m.real_state+AGA_BRIDGE_DELTA==m.agabridge
        assert m.public('bob',ident=1,x=103,y=72,image=1)==1
        s,rec=m.relay_call('read',ident=1)
        assert s==1 and unpack('>6I',rec)==(10,1,103,72,1,0)
        assert m.core_calls[-2:]==['put','read']
        tests+=2

        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=-12,y=31,image=1)==1
        s,rec=m.relay_call('read',ident=2)
        assert s==1 and unpack('>6I',rec)==(11,1,(-12)&0xffffffff,31,1,0)
        assert m.run_select(10)==1
        s,rec=m.relay_call('read',ident=2)
        assert s==1 and unpack('>6I',rec)[0]==11
        tests+=3

        assert m.public('off',ident=1)==1
        s,rec=m.relay_call('read',ident=1)
        assert s==0 and rec==CANARY
        assert m.public('off',ident=1)==1
        assert m.public('bob',ident=1,x=10,y=20,image=1)==1
        s,rec=m.relay_call('read',ident=1)
        assert s==1 and unpack('>6I',rec)==(10,1,10,20,1,0)
        tests+=5

        snapshot=m.table()
        for args in (
            ('bob',dict(ident=0)),('bob',dict(ident=65)),
            ('bob',dict(ident=1,image=0)),('bob',dict(ident=1,image=4097)),
            ('bob',dict(ident=1,x=32768)),('bob',dict(ident=1,y=-32769)),
            ('off',dict(ident=0)),('off',dict(ident=65)),
            ('bob',dict(ident=1,owner=OTHER)),
            ('off',dict(ident=1,owner=OTHER)),
        ):
            kind,kwargs=args
            assert m.public(kind,**kwargs)==0,(layout,args)
            assert m.table()==snapshot
            tests+=1

        m.uc.mem_write(EXEC+0x128,b'\0\0')
        assert m.public('bob',ident=1)==0
        assert m.table()==snapshot
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        tests+=1
        m.reject_type=m.real_state
        assert m.public('bob',ident=1)==0
        assert m.table()==snapshot
        m.reject_type=None
        tests+=1
        m.reject_type=m.agabridge
        assert m.public('bob',ident=1)==0
        assert m.table()==snapshot
        m.reject_type=None
        tests+=1
        # Target must retain the native entry MOVEM signature.
        orig=bytes(m.uc.mem_read(m.agabridge,4))
        m.uc.mem_write(m.agabridge,b'\x4e\x71\x4e\x71')
        assert m.public('bob',ident=1)==0
        assert m.table()==snapshot
        m.uc.mem_write(m.agabridge,orig)
        tests+=1
        m.put(m.real_state,0)
        assert m.public('bob',ident=1)==0
        assert m.table()==snapshot
        m.put(m.real_state,m.screen)
        tests+=1
        assert m.relay_call('reset')[0]==1
        assert m.table()==(m.table()[:4]+bytes(len(m.table())-4))
        assert m.relay_call('read',ident=1)[0]==0
        tests+=2
    print('M19 P0e SPLIT BOBS/AGA NATIVE MC68020 SET/OFF GATE A PASS',
          tests,'cases; 2 real-Init layouts; source-verified relocated AGA core;',
          'OS mocked, no Draw / Close-reset / installed Lib / actual Compiler')


if __name__=='__main__':
    main()
