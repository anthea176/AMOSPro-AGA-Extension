#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2d-P1 public capture and inherited 16px regression, MC68020 models."""
import argparse,json,os
from pathlib import Path
from struct import unpack_from
from compiler_relocation import unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from build_m19_s2d_capture_in_memory import build_s2d_capture,protected
from test_m19_s2c_public_gate_a import capture_cases,chain,CMAP,W,H
from test_m19_s1p1i_contract_gate_a import ContractMachine,switch_owner,bump_generation
from test_m19_s2c_mixed_public_cpu import mixed_cases,MixedPublic
from test_m19_s2c_diagnostic_cpu import cases as diagnostic_cases
from test_m19_s2c_viewport_chain_cpu import cases as viewport_cases,fence_case
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload

class WideMachine(ContractMachine):
    def allocate(self,size):
        ptr=super().allocate(size)
        self.uc.mem_write(ptr+size,bytes([0xa5])*32)
        return ptr
    def no_temps(self):
        super().no_temps()
        for ptr,size in self.temp_allocs:
            assert self.read(ptr+size,32)==bytes([0xa5])*32,(ptr,size)

def region(width,n,h,x,y,pen):
    colors=[pen]+[i for i in range(256) if i!=pen][:n]
    pix=bytearray([pen])*(W*H)
    for row in range(h):
        for col in range(width):
            pix[(row+y)*W+x+col]=colors[(row*width+col)%len(colors)]
    return bytes(pix)

def wide_cases(image,layout):
    _,parts,_=unpack_ap20(image)
    native=parts[unpack_from('>H',parts[204],2)[0]][len(DISPATCH_V2):]
    checks=0
    def new(width=64,n=15,h=9,x=13,y=5,pen=0,**kwargs):
        m=WideMachine(native,parts,layout,**kwargs)
        load(m,width,n,h,x,y,pen)
        assert m.select()==1
        return m
    def load(m,width,n,h,x,y,pen):
        m.pixels=region(width,n,h,x,y,pen)
        m.cmap=CMAP
        m.load_pixels(1-m.front,m.pixels)
    def capture(m,old,width,h=9,x=13,y=5,pen=0,ident=1,success=True):
        notes=len(m.notes)
        rc=m.get_sprite(ident,x,y,x+width-1,y+h-1,pen)
        assert rc==int(success),(layout,width,h,x,y,pen,rc)
        want=put_capture(old,ident,m.pixels,W,H,x,y,width,h,m.cmap,pen,mode='s2') if success else old
        assert m.bank(29)==want and len(m.notes)==notes+int(success)
        assert m.unsafe_reads==0
        assert [s for _,s in m.temp_allocs[-2:]]==[4120+128*width,len(old)+96+(width//2)*h]
        m.no_temps()
        return want
    for width in (32,64):
        for n in range(17):
            for front in (0,1):
                m=new(width,n,front=front)
                want=capture(m,empty_bank(),width,success=n<16)
                if n<16:
                    i=parse_payload(want).image(1)
                    assert (i.width,i.height,i.opaque_count,i.depth)==(width,9,n,2 if n<4 else 4)
                checks+=1
        for h,x,y,pen in ((1,W-width,H-1,0),(256,1,0,19),(256,13,0,0)):
            m=new(width,15,h,x,y,pen)
            capture(m,empty_bank(),width,h,x,y,pen)
            checks+=1
        for flags,ready,port,success,polls,left in ((0,False,True,True,0,0),
            (2,False,True,True,0,2),(3,True,True,True,1,2),
            (3,False,True,False,1,3),(3,False,False,False,0,3)):
            m=new(width,flags=flags,ready=ready,port=port)
            capture(m,empty_bank(),width,success=success)
            from test_m19_s1p1c_pipeline import DB
            assert m.safe_polls==polls and m.get(DB+20)==left
            if not success:assert m.reads==0
            checks+=1
        for at in (1,2):
            m=new(width);m.fail_temp_at=at
            assert m.get_sprite(1,13,5,13+width-1,13)==0
            assert m.bank(29)==empty_bank();m.no_temps();checks+=1
        m=new(width);m.alloc_fail=True
        assert m.get_sprite(1,13,5,13+width-1,13)==0
        assert m.bank(29)==empty_bank();m.no_temps();checks+=1
        for attr in ('mutate_on_alloc','mutate_on_publish'):
            for drift in (switch_owner,bump_generation):
                m=new(width);setattr(m,attr,drift)
                assert m.get_sprite(1,13,5,13+width-1,13)==0
                assert len(m.notes)==1 and len(m.bank(29))==32
                m.no_temps();checks+=1
    m=new(64)
    old=empty_bank()
    for width,n,ident in ((64,15,20),(32,3,1),(16,15,12),(16,2,20),
                          (64,4,12),(32,15,1),(64,16,12),(64,3,20)):
        load(m,width,n,9,13,5,0)
        old=capture(m,old,width,ident=ident,success=n<16);checks+=1
    assert [(i.image_id,i.width,i.depth) for i in parse_payload(old).images]==[(1,32,4),(12,64,4),(20,64,2)]
    for x1,y1,x2,y2 in ((13,5,12,13),(13,5,20,13),(13,5,29,13),
                         (13,5,60,13),(13,5,77,13),(W-63,5,W,13),
                         (-1,0,62,8),(0,0,0xffffffff,8),
                         (0,255,63,256),(0,0,63,0xffffffff)):
        before=(m.bank(29),len(m.notes),len(m.temp_allocs),m.reads)
        assert m.get_sprite(1,x1,y1,x2,y2)==0
        assert (m.bank(29),len(m.notes),len(m.temp_allocs),m.reads)==before
        m.no_temps();checks+=1
    print('S2D_P1_WIDE_PUBLIC_CAPTURE_PASS',layout,checks,'cases',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('capture','chain','mixed-runtime','mixed-compiled'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2d_capture(a.vasm)
    print('S2D_P1_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite=='capture':
        for layout in ('runtime','compiled'):
            capture_cases(image,layout)
            wide_cases(image,layout)
        other,meta=build_s2d_capture(a.vasm)
        assert other==image and meta==info
    elif a.suite=='chain':
        chain(image)
    else:
        layout=a.suite[6:]
        mixed_cases(image,info,layout)
        diagnostic_cases(image,info,layout)
        viewport_cases(image,info,layout)
        fence_case(image,info,layout)
    assert protected()==before
    print('S2D_P1_SUITE_PASS '+a.suite,flush=True)

if __name__=='__main__':main()
