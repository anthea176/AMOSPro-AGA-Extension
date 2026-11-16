#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e first two public Bob instructions: true CPU020 AMOS ABI Gate A.

Execute the NEW public argument shims and real P0e cross-unit object calls
in two disjoint native-group placements. The original AGA Init bytes are
executed. Exec/Intuition/graphics services and Compiler placement are mocked,
so this does NOT prove actual Runtime, Compiler, or physical hardware.
"""
from __future__ import annotations

from struct import unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_get_gate_a import ARGS
from test_m19_p0e_v2_object_bridge_native import BridgeMachine,CANARY
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0e_public_object_ops_in_memory import build as build_public
from m19_p0e_public_object_ops_emit import emit_public_object_ops
from m19_p0e_v2_object_bridge_emit import emit_v2_object_bridge
from compiler_relocation import unpack_ap20,RBSR,GETP
from amos_link_test_support import relocate


class PublicObjectMachine(BridgeMachine):
    def __init__(self,binary,layout='interpreted',depth=8):
        super().__init__(binary,layout,depth)
        self.public_native,self.labels=emit_public_object_ops()
        self.uc.mem_write(self.entry,relocate(self.public_native,self.entry,{},self.uc))

    def public(self,kind,ident=1,x=30,y=45,image=1,*,owner=AMOS,
               instruction_limit=2500000):
        assert kind in ('bob','off')
        for i,reg in enumerate(DR):
            self.uc.reg_write(reg,0x12340000+i)
        for i,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x31000+i*256)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[3],ARGS)
        if kind=='bob':
            self.uc.reg_write(DR[3],image&0xffffffff)
            self.put(ARGS,y)
            self.put(ARGS+4,x)
            self.put(ARGS+8,ident)
            expect_a3=12
        else:
            self.uc.reg_write(DR[3],ident&0xffffffff)
            expect_a3=0
        snapshot={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        which='public_aga_bob_entry' if kind=='bob' else 'public_aga_bob_off_entry'
        try:
            self.uc.emu_start(self.entry+self.labels[which],STOP,count=instruction_limit)
        except Exception as exc:
            raise AssertionError(('PUBLIC P0e CPU020 fault',kind,
                                  hex(self.uc.reg_read(UC_M68K_REG_PC)),
                                  ident,x,y,image,exc)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0
        for reg,val in snapshot.items():
            if reg in (DR[2],DR[3]):
                continue
            if reg==AR[3]:
                assert self.uc.reg_read(reg)==val+expect_a3,(
                    'AMOS GetP stack consumption',kind)
            else:
                assert self.uc.reg_read(reg)==val,(
                    'PUBLIC P0e ABI clobbered',kind,reg)
        assert self.d(3) in (0,1)
        return self.d(3)


def main():
    p0c,_=build_p0c()
    public,meta=build_public()
    _,parts,_=unpack_ap20(public)
    assert meta['public_commands']==85 and len(parts)==95
    assert meta['pc16_margin']>0
    assert parts[89][-4:]==GETP and parts[90][-4:]!=GETP
    for id_,name in ((89,'aga bob'),(90,'aga bob off')):
        assert parts[id_][:2]==RBSR
        assert meta['compiled_offsets'][name]<len(parts[93])
    old_native,_=emit_v2_object_bridge()
    native,labels=emit_public_object_ops()
    assert native.startswith(old_native)
    src=native[labels['public_aga_bob_entry']:]
    insn=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
              disasm(src,0x10000))
    assert sum(i.size for i in insn)==len(src)
    assert all(not x.mnemonic.startswith('dc.') for x in insn)
    tests=0
    for layout in ('interpreted','compiled'):
        m=PublicObjectMachine(p0c,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
        # Before actual AGA Init no new object is published, even though
        # the old capture fixture pre-populates an artificial screen state.
        assert m.public('bob',ident=1,image=1)==0
        tests+=1
        m.activate_aga_state()   # actual original/native AGA initializer
        assert m.get(AMOS+0x1c8)==m.real_state
        assert m.public('bob',ident=1,x=101,y=73,image=1)==1
        s,data=m.bridge_call('read',ident=1)
        assert s==1 and unpack('>6I',data)==(10,1,101,73,1,0)
        tests+=2
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=22,y=44,image=1)==1
        s,data=m.bridge_call('read',ident=2)
        assert s==1 and unpack('>6I',data)==(11,1,22,44,1,0)
        assert m.run_select(10)==1
        s,data=m.bridge_call('read',ident=2)
        assert s==1 and unpack('>6I',data)[0]==11
        tests+=3
        # Off preserves original bank/image/position but clears activity.
        assert m.public('off',ident=1)==1
        s,data=m.bridge_call('read',ident=1)
        assert s==0 and data==CANARY
        assert m.public('off',ident=1)==1
        assert m.public('bob',ident=1,x=-5,y=32767,image=1)==1
        s,data=m.bridge_call('read',ident=1)
        assert s==1 and unpack('>6I',data)==(10,1,(-5)&0xffffffff,32767,1,0)
        tests+=5
        # Invalid IDs or coordinates must not mutate the table.
        before=m.table()
        for kw in (dict(ident=0),dict(ident=65),
                   dict(ident=1,image=0),dict(ident=1,image=4097),
                   dict(ident=1,x=32768),dict(ident=1,y=-32769)):
            assert m.public('bob',**kw)==0
            assert m.table()==before
            tests+=1
        assert m.public('off',ident=0)==0
        assert m.public('off',ident=65)==0
        assert m.table()==before
        tests+=2
        assert m.public('bob',ident=3,image=1,owner=AMOS+0x1000)==0
        assert m.public('off',ident=1,owner=AMOS+0x1000)==0
        assert m.table()==before
        tests+=2
        m.uc.mem_write(EXEC+0x128,b'\0\0')
        assert m.public('bob',ident=3)==0
        assert m.public('off',ident=1)==0
        assert m.table()==before
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        tests+=2
        m.put(m.real_state,0)
        assert m.public('bob',ident=3)==0
        assert m.table()==before
        m.put(m.real_state,m.screen)
        tests+=1

    print('M19 P0e PUBLIC BOB/BOB OFF MC68020 AP20 Gate A PASS',
          tests,'cases; 2 simulated interpreter/Compiler placements;',
          'original AGA Init executed, OS mocked, no public Draw/Close reset')


if __name__=='__main__':
    main()
