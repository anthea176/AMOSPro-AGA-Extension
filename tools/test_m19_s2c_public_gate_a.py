#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exact S2r-derived candidate, public capture 2/4-plane transaction tests."""
import argparse,json,os,unittest
from pathlib import Path
from struct import unpack_from
from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_s2c_in_memory import build_s2c,protected
from test_m19_s1p1i_contract_gate_a import ContractMachine,switch_owner,bump_generation
from test_m19_s1p1i_l2b_integration_gate_a import Integrated
from test_m19_s1p1c_pipeline import W,H,DB
from test_m19_s2b_public_gate_a import cases as sprite_cases
from test_m19_s2r_agapic_gate_a import cases as agapic_cases
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
import test_m19_s1p2m_gate_a as regress

CMAP=bytes(v for i in range(256) for v in (i,(i*17+7)&255,(i*43+11)&255))
def region(n,h=16,x=13,y=5,transparent=0):
    pal=[transparent]+[i for i in range(1,256) if i!=transparent][:n]
    pixels=bytearray([transparent])*(W*H)
    for row in range(h):
        for col in range(16):pixels[(row+y)*W+x+col]=pal[(row*16+col)%len(pal)]
    return bytes(pixels)

def capture_cases(image,layout):
    _,parts,_=unpack_ap20(image)
    native=parts[unpack_from('>H',parts[204],2)[0]][len(DISPATCH_V2):]
    checks=0
    def new(n=15,h=16,x=13,y=5,pen=0,**kw):
        m=ContractMachine(native,parts,layout,**kw)
        m.pixels=region(n,h,x,y,pen);m.cmap=CMAP
        m.load_pixels(1-m.front,m.pixels)
        assert m.select()==1
        return m
    def capture(m,old,ident=1,x=13,y=5,h=16,pen=0,success=True):
        prev=len(m.notes)
        rc=m.get_sprite(ident,x,y,x+15,y+h-1,pen)
        assert rc==int(success),(layout,ident,x,y,h,pen,rc,success,m.temp_allocs,m.calls_gfx)
        want=put_capture(old,ident,m.pixels,W,H,x,y,16,h,m.cmap,pen,mode='s2') if success else old
        assert m.bank(29)==want
        assert len(m.notes)==prev+int(success)
        assert m.unsafe_reads==0
        assert [s for p,s in m.temp_allocs[-2:]]==[6168,len(old)+96+8*h]
        m.no_temps()
        return want
    for n in range(17):
        for front in (0,1):
            m=new(n,front=front)
            raw=capture(m,empty_bank(),success=n<16)
            if n<16:
                i=parse_payload(raw).image(1)
                assert (i.opaque_count,i.depth)==(n,2 if n<4 else 4)
            checks+=1
    for h,x,y,pen in ((1,304,255,0),(256,13,0,0),(256,7,0,19)):
        m=new(15,h,x,y,pen)
        capture(m,empty_bank(),x=x,y=y,h=h,pen=pen)
        checks+=1
    m=new(3,1,304,255)
    capture(m,empty_bank(),x=304,y=255,h=1);checks+=1
    m=new(15)
    want=capture(m,empty_bank(),ident=20)
    for n,ident in ((3,1),(4,12),(2,12),(15,1),(16,20)):
        m.pixels=region(n);m.load_pixels(1-m.front,m.pixels)
        want=capture(m,want,ident,success=n<16);checks+=1
    assert [i.depth for i in parse_payload(want).images]==[4,2,4]
    for flags,ready,port,success,polls,left in ((0,False,True,True,0,0),
        (2,False,True,True,0,2),(3,True,True,True,1,2),
        (3,False,True,False,1,3),(3,False,False,False,0,3)):
        m=new(flags=flags,ready=ready,port=port)
        capture(m,empty_bank(),success=success)
        assert m.safe_polls==polls and m.get(DB+20)==left
        if not success:assert m.reads==0
        checks+=1
    for attr in ('mutate_on_alloc','mutate_on_publish'):
        for drift in (switch_owner,bump_generation):
            m=new();setattr(m,attr,drift)
            assert m.get_sprite()==0 and len(m.notes)==1 and len(m.bank(29))==32
            m.no_temps();checks+=1
    for at in (1,2):
        m=new();m.fail_temp_at=at
        assert m.get_sprite()==0 and m.bank(29)==empty_bank()
        m.no_temps();checks+=1
    m=new();m.alloc_fail=True
    assert m.get_sprite()==0 and m.bank(29)==empty_bank()
    m.no_temps();checks+=1
    m=new();m.put16(m.bynum(29)+12,3)
    capture(m,empty_bank());assert m.word(m.bynum(29)+12)==3
    assert m.list_alloc_flags[-1]==0x10003;checks+=1
    m=new();assert m.select(4)==0 and m.get_sprite()==0 and m.bank(29)==empty_bank()
    m.no_temps();checks+=1
    print('S2C_PUBLIC_CAPTURE_PASS',layout,checks,'cases',flush=True)

def chain(image):
    for layout in ('runtime','compiled'):
        m=Integrated(image,layout);m.double();m.iff()
        assert m.select()==1 and m.get_sprite()==1
        want=m.expected()
        assert m.bank(29)==want
        want=put_capture(want,2,m.fixture_pixels,W,H,48,5,16,16,m.cmap,0,mode='s2')
        assert parse_payload(want).image(2).depth==4
        assert m.get_sprite(2,48,5,63,20)==1 and m.bank(29)==want
        m.swap();before=m.reads
        assert m.get_sprite(3)==0 and m.bank(29)==want and m.reads==before
        m.ready=True
        assert m.get_sprite(3)==1 and m.get(DB+20)==2
        want=put_capture(want,3,bytes(W*H),W,H,13,5,16,16,m.cmap,0,mode='s2')
        assert m.bank(29)==want
        m.iff();m.disp_ready=True;m.swap();m.ready=True
        assert m.get_sprite(4,48,5,63,20)==1 and m.get(DB+20)==2
        want=put_capture(want,4,m.fixture_pixels,W,H,48,5,16,16,m.cmap,0,mode='s2')
        assert m.bank(29)==want
        assert m.unsafe_reads==0 and m.swap_calls==2 and m.palette_calls==2 and m.writes>0
        m.no_temps();print('S2C_DB_IFF_SWAP_CAPTURE_PASS',layout,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('capture','runtime','compiled','chain','pattern','safeport','bob','agapic','mixed-runtime','mixed-compiled'))
    p.add_argument('--diagnostic',action='store_true')
    p.add_argument('--viewport-chain',action='store_true')
    a=p.parse_args()
    if a.viewport_chain:a.diagnostic=True
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2c(a.vasm,diagnostic=a.diagnostic,viewport_chain=a.viewport_chain)
    print('S2C_P1C_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite=='capture':
        for layout in ('runtime','compiled'):capture_cases(image,layout)
        rebuilt,other=build_s2c(a.vasm,diagnostic=a.diagnostic,viewport_chain=a.viewport_chain)
        assert rebuilt==image and other==info
        if a.diagnostic:
            from prepare_m19_s2a_campaign import identify
            identify('S2CE_LIB' if a.viewport_chain else 'S2CD_LIB',image)
    elif a.suite in ('runtime','compiled'):sprite_cases(image,info,a.suite)
    elif a.suite.startswith('mixed-'):
        from test_m19_s2c_mixed_public_cpu import mixed_cases
        mixed_cases(image,info,a.suite[6:])
        if a.diagnostic:
            from test_m19_s2c_diagnostic_cpu import cases
            cases(image,info,a.suite[6:])
        if a.viewport_chain:
            from test_m19_s2c_viewport_chain_cpu import cases as viewport_cases
            viewport_cases(image,info,a.suite[6:])
    elif a.suite=='chain':chain(image)
    elif a.suite=='pattern':
        prior,_=regress.build_l2(a.vasm)
        regress.verify_linked_source(a.vasm,before[1])
        assert regress.run_pattern_cases(prior,image)==184
    elif a.suite=='safeport':assert regress.run_cases(image,info)==172
    elif a.suite=='bob':
        _,meta=regress.build_l2(a.vasm)
        regress.l2_gate.IMAGE,regress.l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(regress.l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
    elif a.suite=='agapic':
        for layout in ('runtime','compiled'):agapic_cases(image,layout)
    assert protected()==before
    print('S2C_P1C_SUITE_PASS '+a.suite,flush=True)

if __name__=='__main__':main()
