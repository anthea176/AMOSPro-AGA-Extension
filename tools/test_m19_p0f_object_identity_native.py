#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f private per-object identity capture/validate real CPU020 Gate A.

The source-verifiable OLD P0e object table stays byte-for-byte unchanged.
New per-object native stamps are transactional and checked through actual
Bnk.GetAdr; Compiler/WinUAE/physical execution and public Draw are untested.
"""
from __future__ import annotations

from struct import unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0e_split_bridge_gate_a import SplitMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0f_object_identity_in_memory import build as build_identity
from m19_p0f_object_identity_emit import emit_object_identity,FRAME
from m19_p0e_split_bridge_emit import AGA_CORE
from amos_link_test_support import relocate

OUTPUT=0x5c100
CANARY=bytes.fromhex('d0a5face')*6


class IdentityMachine(SplitMachine):
    def __init__(self,lib,layout='interpreted'):
        super().__init__(lib,layout)
        self.identity_source,self.identity_labels=emit_object_identity()
        self.identity_base=self.agabridge+len(AGA_CORE)
        self.uc.mem_write(self.identity_base,relocate(
            self.identity_source,self.identity_base,{},self.uc))
        self.shadow_base=self.identity_base+self.identity_labels['identity_stamp_table']

    def shadows(self):
        return bytes(self.uc.mem_read(self.shadow_base,64*16))

    def identity(self,kind,ident=1,bank=10,image=1,x=0,y=0,
                 *,owner=AMOS,output=OUTPUT,count=5000000):
        assert kind in ('bind','check','clear')
        self.uc.mem_write(OUTPUT,CANARY)
        for n,r in enumerate(DR):self.uc.reg_write(r,0x15730000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x43200+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(DR[0],ident&0xffffffff)
        self.uc.reg_write(DR[1],bank&0xffffffff)
        self.uc.reg_write(DR[4],image&0xffffffff)
        self.uc.reg_write(DR[5],x&0xffffffff)
        self.uc.reg_write(DR[6],y&0xffffffff)
        self.uc.reg_write(AR[1],output)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(
                self.identity_base+self.identity_labels['identity_'+kind+'_entry'],
                STOP,count=count)
        except Exception as exc:
            raise AssertionError(('M19 P0f per-object CPU020 fault',kind,
                ident,bank,hex(self.uc.reg_read(UC_M68K_REG_PC)),
                str(exc),self.calls[-8:])) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0 and self.d(3) in (0,1)
        for r,v in saved.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('P0f per-object AMOS ABI',kind,r)
        return self.d(3),bytes(self.uc.mem_read(OUTPUT,24))


def main():
    lib,_=build_p0c()
    candidate,meta=build_identity()
    assert meta['public_commands']==85 and meta['ap20_entries']==95
    assert meta['pc16_max']==32576 and meta['aga_bytes']<65534
    ncases=0
    for layout in ('interpreted','compiled'):
        m=IdentityMachine(lib,layout)
        native=m.identity_source
        end=m.identity_labels['identity_stamp_table']
        rel=relocate(native,m.identity_base,{},m.uc)
        insn=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
                  .disasm(rel[:end],m.identity_base))
        assert sum(x.size for x in insn)==end
        assert all(not x.mnemonic.startswith('dc.') for x in insn)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
        m.activate_aga_state()
        assert m.identity('bind',ident=1,bank=10,image=1,x=40,y=30)[0]==1
        status,data=m.identity('check',ident=1)
        assert status==1 and unpack('>6I',data)==(10,1,40,30,1,0)
        assert m.shadows()[:16]!=bytes(16)
        ncases+=2
        # Persistent objects are independent of current BOBS selection.
        assert m.run_select(11)==1
        assert m.identity('bind',ident=2,bank=11,image=1,x=-5,y=15)[0]==1
        status,data=m.identity('check',ident=2)
        assert status==1 and unpack('>6I',data)==(
            11,1,(-5)&0xffffffff,15,1,0)
        assert m.identity('check',ident=1)[0]==1
        ncases+=3
        snapshot=m.table(),m.shadows()
        for kind,kwargs in (
            ('bind',dict(ident=0)),('bind',dict(ident=65)),
            ('bind',dict(ident=1,image=0)),
            ('bind',dict(ident=1,image=4097)),
            ('bind',dict(ident=1,x=-32769)),
            ('bind',dict(ident=1,bank=12)),
            ('bind',dict(ident=1,owner=AMOS+0x1000)),
        ):
            assert m.identity(kind,**kwargs)[0]==0,(layout,kind,kwargs)
            assert (m.table(),m.shadows())==snapshot
            ncases+=1
        # Mutating AGBO generation after registration must fail closed;
        # no BOBS selection change and no output record touched.
        node=m.find(10)
        assert node!=0
        oldgen=m.get(node+24+24)
        m.put(node+24+24,oldgen+1)
        assert m.identity('check',ident=1)==(0,CANARY)
        assert (m.table(),m.shadows())==snapshot
        m.put(node+24+24,oldgen)
        assert m.identity('check',ident=1)[0]==1
        ncases+=2
        # AMOS bank is removed/replaced: old object's source is rejected.
        oldhead=m.get(HEAD)
        m.put(HEAD,0)
        assert m.identity('check',ident=1)==(0,CANARY)
        m.put(HEAD,oldhead)
        assert m.identity('check',ident=1)[0]==1
        ncases+=2
        m.uc.mem_write(EXEC+0x128,b'\0\0')
        assert m.identity('bind',ident=1,bank=10)[0]==0
        assert m.identity('check',ident=1)==(0,CANARY)
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        ncases+=2
        # Active object is wiped on original P0e Close/Reset; stale shadow
        # cannot authorize an inactive object, even though it still exists.
        assert m.relay_call('reset')[0]==1
        assert m.identity('check',ident=1)==(0,CANARY)
        assert m.identity('check',ident=2)==(0,CANARY)
        assert m.identity('clear')[0]==1
        assert m.shadows()==bytes(64*16)
        ncases+=4
    print('M19 P0f PER-OBJECT IDENTITY NATIVE MC68020 GATE A PASS',
          ncases,'cases; source exact P0e table, two AGA/BOBS placements;',
          'mocked AMOS/Exec; no public Draw/End/WinUAE Compiler')


if __name__=='__main__':
    main()
