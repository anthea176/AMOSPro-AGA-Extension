#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f public Aga Bob selected-bank escrow MC68020 native Gate A.

Native wrappers in two unrelated V2 placements, original AGA Init, AMOS
Bnk.GetAdr and Exec OS calls mocked. No public Draw/actual Compiler proof.
"""
from __future__ import annotations
from struct import unpack
from test_m5_generic import EXEC
from test_m19_p0f_object_identity_native import IdentityMachine,CANARY
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0f_public_bound_in_memory import build,emit_bound_public
from amos_link_test_support import relocate

class BoundMachine(IdentityMachine):
    def __init__(self,lib,layout='interpreted'):
        super().__init__(lib,layout)
        self.public_native,self.labels=emit_bound_public()
        self.uc.mem_write(self.entry,relocate(
            self.public_native,self.entry,{},self.uc))

def main():
    lib,_=build_p0c()
    _,meta=build()
    assert meta['public_commands']==85 and meta['pc16_margin']==190
    count=0
    for layout in ('interpreted','compiled'):
        m=BoundMachine(lib,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
        assert m.public('bob',ident=1)==0
        assert m.table()==bytes(len(m.table()))
        m.activate_aga_state()
        assert m.public('bob',ident=1,x=12,y=33,image=1)==1
        status,rec=m.identity('check',ident=1)
        assert status==1 and unpack('>6I',rec)==(10,1,12,33,1,0)
        count+=3
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=-12,y=31,image=1)==1
        status,rec=m.identity('check',ident=2)
        assert status==1 and unpack('>6I',rec)==(
            11,1,(-12)&0xffffffff,31,1,0)
        assert m.identity('check',ident=1)[0]==1
        count+=3
        before=m.table(),m.shadows()
        for args in (dict(ident=0),dict(ident=65),
                     dict(ident=1,image=0),dict(ident=1,image=4097),
                     dict(ident=1,x=32768)):
            assert m.public('bob',**args)==0,(layout,args)
            assert (m.table(),m.shadows())==before
            count+=1
        n=m.find(10);generation=m.get(n+24+24)
        m.put(n+24+24,generation+1)
        assert m.identity('check',ident=1)==(0,CANARY)
        m.put(n+24+24,generation)
        assert m.identity('check',ident=1)[0]==1
        count+=2
        assert m.public('off',ident=1)==1
        assert m.identity('check',ident=1)==(0,CANARY)
        assert m.public('bob',ident=1,image=1,x=20,y=20)==1
        assert m.identity('check',ident=1)[0]==1
        count+=4
        m.uc.mem_write(EXEC+0x128,b'\0\0')
        before=m.table(),m.shadows()
        assert m.public('bob',ident=3)==0
        assert (m.table(),m.shadows())==before
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        count+=1
        assert m.relay_call('reset')[0]==1
        assert m.identity('check',ident=1)==(0,CANARY)
        count+=2
    print('M19 P0f PUBLIC AGA BOB STAMPED MC68020 GATE A PASS',
          count,'cases; 2 native layouts; no Draw, End or real Compiler')

if __name__=='__main__':
    main()
