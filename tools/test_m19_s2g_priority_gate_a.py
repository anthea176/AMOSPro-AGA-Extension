#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2g-P1a native MC68020, exact private stub, OS/relocation models only."""
import argparse
import json
import os
from itertools import permutations, product
from pathlib import Path
from struct import pack, unpack_from
from unittest.mock import patch
from build_m19_s2g_in_memory import build_s2g, protected
from compiler_relocation import GETP, RBSR, unpack_ap20
from test_m19_s1p1c_amos_bank_commit import CODE
from test_m19_s1p1c_pipeline import GFX
import test_m19_s2d_public_display_gate_a as display
from test_m19_s2f_public_gate_a import HotClip, ClipBase, public as old_public

class Layered(HotClip):
    def __init__(self,image,info,layout,width,version=40):
        super().__init__(image,info,layout,width,version)
        _,parts,_=unpack_ap20(image)
        index,group=info['private_entry'],info['sprite_group']
        stub=parts[index]
        assert parts[index-1]==GETP
        assert stub[:2]==RBSR and unpack_from('>HH',stub,2)==(group,info['private_offset'])
        if layout=='runtime':
            assert index<group
            pc=CODE-sum(map(len,parts[index:group]))
            raw=pack('>Hh',0x6100,CODE-(pc+2))+stub[4:]
        else:
            pc=CODE-0x400+3*0x20
            raw=pack('>HIH',0x4eb9,CODE,info['private_offset'])+b'\x4e\x75'
        self.uc.mem_write(pc,raw)
        self.layer_entry=pc

    def sprite5(self,n=1,x=30,y=40,image=7,layer=0):
        return self.invoke_any(self.layer_entry,layer,(image,y,x,n))

    def layer_frame(self,layer,n,ident,x,y):
        self.clipped(2*layer,ident,x,y)
        assert self.get(self.record(2*layer)+96)==n

def cases(image,info,layout):
    count=0
    for width,version,order,mixed in product((16,32,64),(39,40),
                                             permutations((1,2,3)),(False,True)):
        m=Layered(image,info,layout,width,version)
        ident={k:(7 if not mixed or k==2 else 2*k-1) for k in (1,2,3)}
        for k in order:
            peers={2*j:m.peer(2*j) for j in order if j!=k and m.named and
                   m.get(m.record(2*j)+96)}
            assert m.sprite5(n=20+k,image=ident[k],layer=k,x=50,y=50)==1
            m.layer_frame(k,20+k,ident[k],50,50)
            assert all(m.peer(ch)==before for ch,before in peers.items())
            count+=1
        old={ch:m.peer(ch) for ch in display.PAIRS}
        events=list(m.ext_events)
        allocs,temps,fences=m.ext_allocs,m.temp_tries,m.tofs
        for k in (1,2,3):
            wrong=k%3+1
            assert m.sprite5(n=20+k,image=ident[k],layer=wrong,x=55,y=60)==-206
            assert m.sprite5(n=40+k,image=7,layer=k)==-206
            assert all(m.peer(ch)==before for ch,before in old.items())
            assert m.ext_events==events and (m.ext_allocs,m.temp_tries,m.tofs)==(allocs,temps,fences)
            count+=2
        for k in (1,2,3):
            others={ch:m.peer(ch) for ch in display.PAIRS if ch!=2*k}
            # Four-argument Move and explicit same layer preserve allocation.
            assert m.sprite(n=20+k,image=ident[k],x=60,y=60)==1
            m.layer_frame(k,20+k,ident[k],60,60)
            assert m.sprite5(n=20+k,image=ident[k]+1,layer=k,x=-1,y=-1)==1
            m.layer_frame(k,20+k,ident[k]+1,-1,-1)
            assert m.sprite5(n=20+k,image=ident[k]+1,layer=0,x=320,y=256)==1
            m.layer_frame(k,20+k,ident[k]+1,320,256)
            assert all(m.peer(ch)==before for ch,before in others.items())
            count+=3
        m.erase()
        for k in (1,2,3):
            assert m.sprite5(n=20+k,image=ident[k]+1,layer=k,x=70,y=80)==1
            m.layer_frame(k,20+k,ident[k]+1,70,80)
            count+=1
        m.close(end=bool(mixed))
        m.empty_wide()
        count+=1
    for width,version in product((16,32,64),(39,40)):
        m=Layered(image,info,layout,width,version)
        attempts=m.temp_tries
        for invalid in (-2147483648,-1,4,2147483647):
            assert m.sprite5(layer=invalid)==-210
            assert m.temp_tries==attempts and not m.ext_events
            m.empty_wide()
            count+=1
        # Family 0 simple is compatible only with pair 2/3. No fallback.
        for layer in (2,3):
            assert m.sprite5(image=1,layer=layer)==-206
            assert not m.ext_events and m.ext_allocs==0
            m.empty_wide()
            count+=1
        # Foreign reservation in pair 4/5: do not acquire or free it.
        m.uc.mem_write(GFX+166,b'\x11')
        assert m.sprite5(layer=2)==-206
        assert m.read(GFX+166,1)==b'\x11' and not m.ext_events
        m.uc.mem_write(GFX+166,b'\x01')
        m.empty_wide()
        count+=1
        assert m.sprite5(n=64,layer=3)==1
        m.layer_frame(3,64,7,30,40)
        peer=m.peer(6)
        assert m.sprite5(n=1,image=10,layer=1)==-206
        assert m.peer(6)==peer
        # Existing four-argument creation still takes first compatible pair.
        assert m.sprite(n=2,image=1,x=40,y=40)==1
        m.layer_frame(1,2,1,40,40)
        assert m.off(64)==1
        assert m.sprite5(n=64,layer=2)==1
        m.layer_frame(2,64,7,30,40)
        assert m.bankfree()==1
        m.empty_wide()
        count+=6
    print('S2G_P1A_PRIVATE_LAYER_PASS',layout,count,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    p.add_argument('--historical',type=Path,required=True)
    p.add_argument('--suite',choices=('runtime','compiled','legacy-runtime','legacy-compiled'),required=True)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2g(a.vasm)
    print('S2G_P1A_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite.startswith('legacy-'):
        layout=a.suite[7:]
        old_public(image,info,layout)
        with patch.object(display,'WidePublic',ClipBase):
            display.cases(image,info,layout,clipping=True)
    else:
        cases(image,info,a.suite)
    assert protected()==before
    print('S2G_P1A_SUITE_PASS '+a.suite,flush=True)

if __name__=='__main__':
    main()
