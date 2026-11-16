#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e MC68020 cross-unit BOBS -> AGA object-table Gate A.

The *real source-pinned* native AGA Init is executed and publishes its State
pointer in the live A5 context before calling the private bridge. BOBS and
AGA native groups are physically disjoint in both simulated interpreter
and Compiler V2 placements. Tests execute actual source-emitted MC68020
instructions; Exec/Intuition/graphics services remain MOCKED.
No public token, actual AMOS Compiler, WinUAE or DMA claim.
"""
from __future__ import annotations

from struct import pack,unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0d_bob_blit_in_memory import build as build_p0d
from build_m19_p0e_v2_bridge_in_memory import build as build_linked
from compiler_relocation import unpack_ap20
from m19_p0e_object_table_emit import emit_object_table,MAX_OBJECTS,SLOT_BYTES
from m19_p0e_v2_object_bridge_emit import (
    emit_v2_object_bridge,AGA_P0D_GROUP_BYTES,OBJ_RELATIVE,
)
from test_m19_p0d_public_blit_gate_a import PublicBobMachine
from amos_link_test_support import relocate

OUTPUT=0x59000
OTHER=AMOS+0x1000
CANARY=bytes.fromhex('b0b5c0dec001cafe11ee22ff')*2


class BridgeMachine(PublicBobMachine):
    def __init__(self,source,layout='interpreted',depth=8):
        super().__init__(source,layout,depth)
        assert len(self.aga_native)==AGA_P0D_GROUP_BYTES
        self.objects,self.object_labels=emit_object_table()
        self.bridge,self.labels=emit_v2_object_bridge()
        self.uc.mem_write(self.aga+AGA_P0D_GROUP_BYTES,self.objects)
        self.uc.mem_write(self.entry,relocate(self.bridge,self.entry,{},self.uc))
        self.objbase=self.aga+AGA_P0D_GROUP_BYTES
        self.objroot=self.objbase+self.object_labels['object_root']
        self.objtable=self.objbase+self.object_labels['object_table']
        self.objcalls=[]
        self.reject_type=None
        for name in ('put','off','read','reset'):
            addr=self.objbase+self.object_labels['object_'+name+'_entry']
            self.uc.hook_add(UC_HOOK_CODE,self._on_object,user_data=name,
                             begin=addr,end=addr)

    def _on_object(self,uc,address,size,name):
        self.objcalls.append(name)

    def os_call(self,uc,address,size,user):
        if address==EXEC-534 and self.reject_type is not None:
            if self.a(1)==self.reject_type:
                return self._os_return(0)
        return super().os_call(uc,address,size,user)

    def bridge_call(self,kind,ident=1,bank=10,image=1,x=0,y=0,
                    *,owner=AMOS,output=OUTPUT,count=3000000):
        self.uc.mem_write(OUTPUT,CANARY)
        for n,r in enumerate(DR):self.uc.reg_write(r,0x12340000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x30000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(DR[0],ident&0xffffffff)
        self.uc.reg_write(DR[1],bank&0xffffffff)
        self.uc.reg_write(DR[4],image&0xffffffff)
        self.uc.reg_write(DR[5],x&0xffffffff)
        self.uc.reg_write(DR[6],y&0xffffffff)
        self.uc.reg_write(AR[1],output)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(
                self.entry+self.labels['object_bridge_'+kind+'_entry'],STOP,
                count=count)
        except Exception as error:
            raise AssertionError(('cross-unit CPU020 fault',str(error),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),kind,ident,bank,
                self.objcalls[-8:])) from error
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.d(2)==0
        for r,v in old.items():
            if r not in (DR[2],DR[3]):
                assert self.uc.reg_read(r)==v,('cross-unit AMOS ABI clobbered',kind,r)
        assert self.d(3) in (0,1)
        return self.d(3),bytes(self.uc.mem_read(OUTPUT,SLOT_BYTES))

    def table(self):
        return bytes(self.uc.mem_read(self.objroot,8+MAX_OBJECTS*SLOT_BYTES))


def main():
    p0c,_=build_p0c()
    p0d,meta=build_p0d()
    linked,bridge_meta=build_linked()
    assert meta['sha256']=='bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be'
    _,p0d_parts,_=unpack_ap20(p0d)
    _,p0c_parts,_=unpack_ap20(p0c)
    _,parts,_=unpack_ap20(linked)
    assert p0d_parts[92]==p0c_parts[91]
    assert parts[92].startswith(p0d_parts[92])
    assert bridge_meta['public_commands']==83 and bridge_meta['ap20_entries']==93
    assert bridge_meta['rbsr_max']<32766
    raw,labels=emit_v2_object_bridge()
    code=raw[labels['object_bridge_put_selected_entry']:]
    inst=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        .disasm(code,0x100000))
    assert sum(i.size for i in inst)==len(code)
    assert all(not ins.mnemonic.startswith('dc.') for ins in inst)

    total=0
    for layout in ('interpreted','compiled'):
        m=BridgeMachine(p0c,layout,8)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_get(2,6,5,36,8)==1
        # The synthetic CaptureMachine screen is deliberately replaced by
        # the real AGA State at Init; capture both banks BEFORE Init so a
        # later bank switch tests object metadata, not fake screen geometry.
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1  # known-good P0d bank-11 capture
        assert m.run_select(10)==1

        # Before ACTUAL AGA Init, the legacy fake Stage pointer must be
        # rejected, never treated as an AGA native-unit relocation anchor.
        assert m.bridge_call('put')[0]==0
        assert m.table()==bytes(8+MAX_OBJECTS*SLOT_BYTES)
        total+=1

        m.activate_aga_state()       # really executes old AGA Init MC68020
        assert m.get(AMOS+0x1c8)==m.aga+0x1c2
        assert m.real_state+OBJ_RELATIVE==m.objbase
        assert m.get(AMOS+0x1cc)==m.old_end
        assert m.get(AMOS+0x1d0)==m.old_end

        assert m.bridge_call('reset')[0]==1
        assert m.get(m.objroot)==AMOS
        assert m.bridge_call('put_selected',ident=1,bank=9999,image=1,x=-5,y=23)[0]==1
        st,rec=m.bridge_call('read',ident=1)
        assert st==1 and unpack('>6I',rec)==(
            10,1,(-5)&0xffffffff,23,1,0)
        assert m.objcalls[-3:]==['reset','put','read']
        total+=3

        # Each new object captures its BOBS selection AT DEFINITION.
        assert m.run_select(11)==1
        assert m.bridge_call('put_selected',ident=2,bank=9999,image=1,x=20,y=26)[0]==1
        assert m.run_select(10)==1
        st,rec=m.bridge_call('read',ident=2)
        assert st==1 and unpack('>6I',rec)==(11,1,20,26,1,0)
        st,rec=m.bridge_call('read',ident=1)
        assert st==1 and unpack('>6I',rec)[0]==10
        total+=3

        assert m.bridge_call('off',ident=1)[0]==1
        st,rec=m.bridge_call('read',ident=1)
        assert st==0 and rec==CANARY
        assert m.bridge_call('put',ident=1,bank=10,image=2,x=100,y=90)[0]==1
        st,rec=m.bridge_call('read',ident=1)
        assert st==1 and unpack('>6I',rec)==(10,2,100,90,1,0)
        total+=4

        snapshot=m.table()
        tests=[
            ('put',dict(ident=0)),('put',dict(ident=65)),
            ('put',dict(ident=1,bank=4)),
            ('put',dict(ident=1,image=4097)),
            ('put',dict(ident=1,x=32768)),
            ('put',dict(ident=1,owner=OTHER)),
            ('put_selected',dict(ident=1,bank=9999,owner=OTHER)),
            ('off',dict(ident=1,owner=OTHER)),
            ('read',dict(ident=0)),
            ('read',dict(ident=1,output=0)),
        ]
        # The foreign A5 also has a valid state anchor; the private table
        # itself must refuse cross-owner access rather than relying on 0.
        m.put(OTHER+0x1c8,m.real_state)
        for kind,kwargs in tests:
            st,_=m.bridge_call(kind,**kwargs)
            assert st==0 and m.table()==snapshot,(kind,kwargs)
            total+=1

        # The bridge must read the ACTUAL bank selection inside BOBS,
        # not accept the caller's stale/hardcoded bank argument.
        selection=m.entry+m.labels['bank_active_state']
        previous=m.get(selection)
        m.put(selection,0)
        assert m.bridge_call('put_selected',ident=3,bank=10)[0]==0
        assert m.table()==snapshot
        m.put(selection,previous)
        total+=1

        # No CPU020 -> refusal before reading A5/State or native AGA bytes.
        m.uc.mem_write(EXEC+0x128,b'\0\0')
        assert m.bridge_call('reset')[0]==0
        assert m.table()==snapshot
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        total+=1

        # Pin original AGA legacy End signature independently of object code.
        old_end=bytes(m.uc.mem_read(m.old_end,12))
        m.uc.mem_write(m.old_end,b'\x4e\x71')
        assert m.bridge_call('put',ident=3)[0]==0
        assert m.table()==snapshot
        m.uc.mem_write(m.old_end,old_end)
        total+=1

        # AGA object-table entry has its own independent exact source
        # signature. Reject tampering and a failed TypeOfMem endpoint probe.
        orig=bytes(m.uc.mem_read(m.objbase,16))
        m.uc.mem_write(m.objbase,b'\x4e\x71')
        assert m.bridge_call('put',ident=3)[0]==0
        assert m.table()==snapshot
        m.uc.mem_write(m.objbase,orig)
        total+=1
        m.reject_type=m.objbase+len(m.objects)-1
        assert m.bridge_call('put',ident=3)[0]==0
        assert m.table()==snapshot
        m.reject_type=None
        total+=1
        # The State pointer must be checked with TypeOfMem BEFORE loading
        # its Screen field (avoids an invalid/stale native State address).
        m.reject_type=m.real_state
        assert m.bridge_call('put',ident=3)[0]==0
        assert m.table()==snapshot
        m.reject_type=None
        total+=1
        # Lost A5->State anchor must also refuse, without side effects.
        m.put(AMOS+0x1c8,0)
        assert m.bridge_call('put',ident=3)[0]==0
        assert m.table()==snapshot
        m.put(AMOS+0x1c8,m.real_state)
        total+=1

        # No AGA screen: close/End may no longer use object table API;
        # explicit reset must happen BEFORE the old AGA screen is closed.
        m.put(m.real_state,0)
        assert m.bridge_call('reset')[0]==0
        assert m.table()==snapshot
        m.put(m.real_state,m.screen)
        assert m.bridge_call('reset')[0]==1
        assert m.table()==pack('>I',AMOS)+bytes(4+MAX_OBJECTS*SLOT_BYTES)
        total+=2

    print('M19 P0e NATIVE MC68020 BOBS->AGA RELOCATION BRIDGE GATE A PASS',
          total,'cases; layouts interpreter/compiled simulated; native group',
          len(code),'bytes; original AGA Init executed, OS services mocked;'
          ' NO public token / WinUAE / actual Compiler')


if __name__=='__main__':
    main()
