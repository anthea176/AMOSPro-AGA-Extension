#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2f integrated AP20 candidate, native CPU and OS model, not real AMOS."""
import argparse,json,os,unittest
from itertools import product
from pathlib import Path
from struct import pack
from unittest.mock import patch
from unicorn.m68k_const import *
from build_m19_s2f_in_memory import build_s2f,protected
import test_m19_s2d_public_display_gate_a as display
from test_m19_s1p2i_gate_a import STATE,EXEC,CI
from test_m19_s2d_ext_prepare_cpu import plane
from test_m19_s2f_clip_kernel_gate_a import oracle,raster
from m19_s1_agsp_bank import parse_payload,set_hotspot
from test_m19_s2r_agapic_gate_a import cases as agapic_cases
import test_m19_s1p2m_gate_a as regress

REC=188
CACHE,KEY,STAGECACHE,STAGEKEY=172,176,180,184
def packed(x,y):return (x&65535)<<16 | (y&65535)

class ClipBase(display.WidePublic):
    def record(self,ch):
        assert self.named
        return self.named+108+REC*((ch-2)//2)
    def peer(self,ch):
        r=self.record(ch)
        return (self.read(r,REC),self.read(display.FAST_TABLE+4*ch,8),
                self.read(CI+88+8*ch,16))
    def on_code(self,uc,address,size,user):
        if address==EXEC-684 and uc.reg_read(UC_M68K_REG_D1)==1:
            assert self.depth==0 and self.named
            n=uc.reg_read(UC_M68K_REG_D0)
            assert 1<=n<=8276
            self.temp_tries+=1
            result=0
            if self.temp_tries!=self.fail_temp_at:
                result=self.allocate(n)
                self.uc.mem_write(result,b'\xcd'*n)
                self.temp_live.add(result);self.temp_allocs.append((result,n))
            self.volatile(uc,result)
            return
        return super().on_code(uc,address,size,user)
    def original(self,ch,ident):
        r=self.record(ch);im=parse_payload(self.payload).image(ident)
        ptr=self.get(r+CACHE)
        expected=pack('>8I2H',0x53324643,84+len(im.planes),im.width,im.height,im.depth,
            ident,parse_payload(self.payload).generation,packed(im.hotspot_x,im.hotspot_y),
            im.opaque_count,im.source_transparent_pen)+im.palette+im.planes
        assert ptr in self.temp_live and self.allocations[ptr]==len(expected)
        assert self.read(ptr,len(expected))==expected
        assert self.get(r+168)==packed(im.hotspot_x,im.hotspot_y)
        assert self.get(self.named+52)==0x000802a0 and self.allocations[self.named]==672
        return im
    def owned(self):
        expected={self.named} if self.named else set()
        if self.named:
            for ch in display.PAIRS:
                r=self.record(ch)
                if not self.get(r+96):continue
                cur=self.get(r+CACHE);stage=self.get(r+STAGECACHE)
                assert cur and cur not in expected
                expected.add(cur)
                if stage:
                    assert self.get(r+80) and self.get(r+112)!=self.get(r+104)
                    assert stage not in expected
                    expected.add(stage)
        assert self.temp_live==expected,('CPU allocations',self.temp_live,expected)
    def clipped(self,ch,ident,x,y):
        r=self.record(ch);im=self.original(ch,ident)
        k,px,py,dx,dy=oracle(x,y,im.hotspot_x,im.hotspot_y,im.width,im.height)
        assert k in (1,2,3)
        assert self.get(r+KEY)==(0x80000000 if k==3 else packed(dx,dy))
        assert self.get(r+24)==31 and self.get(r+104)==ident
        assert self.get(r+12)==im.width and self.get(r+16)==im.depth
        stride=im.width//8
        planes=[bytes(stride*im.height) if k==3 else raster(plane(im,i),im.width,im.height,dx,dy)
                for i in range(im.depth)]
        for part,offset in enumerate((52,56) if im.depth==4 else (52,)):
            p=self.get(r+offset);data,w,h,att=self.ext[p]
            assert (w,h,att)==(im.width,im.height,bool(part))
            assert self.get(display.FAST_TABLE+4*(ch+part))==p
            assert self.pointer(ch+part)==data and self.word(p+6)==px and self.word(p+8)==py
            want=b''.join(planes[2*part][row*stride:(row+1)*stride]+
                          planes[2*part+1][row*stride:(row+1)*stride] for row in range(h))
            assert self.read(data+2*stride,len(want))==want,('clipped stream',ch,x,y,ident)
            assert self.read(data+3,1)[0]>>7==int(att)
            assert self.read(data+stride+1,1)[0]>>7==int(att)
            assert self.read(data+(h+1)*stride*2,stride*2)==bytes(stride*2)
        if im.depth==2:assert self.pointer(ch+1)==display.NEUTRAL
        self.owned()

class HotClip(ClipBase):
    def __init__(self,image,info,layout,width,version=40):
        super().__init__(image,info,layout,width,version)
        self.erase()
        p=self.payload
        for i,hx,hy in ((1,width//2,8),(2,-3,-4),(7,width//2,8),(8,-3,-4),(9,32767,-32768)):
            p=set_hotspot(p,i,hx,hy)
        self.payload=p;self.node=self.make_bank(29,b'AGASPRT ',p)
        assert self.select(29)==1
    def origin(self,ident,ox,oy,n=1,ch=2):
        im=parse_payload(self.payload).image(ident)
        x=ox+im.hotspot_x;y=oy+im.hotspot_y
        rc=self.sprite(n=n,image=ident,x=x,y=y)
        assert rc==1,('origin',ident,ox,oy,rc)
        self.clipped(ch,ident,x,y)

def public(image,info,layout):
    count=0
    for w,version,ident in product((16,32,64),(39,40),(1,7)):
        m=HotClip(image,info,layout,w,version)
        m.origin(ident,1-w,3);count+=1
        m.origin(3,17,21,n=2,ch=4)
        peer=m.peer(4)
        for ox,oy in ((-w-1,0),(-w,0),(1-w,0),(-1,0),(0,0),
            (320-w,240),(321-w,240),(319,255),(320,256),
            (0,-16),(0,-15),(0,-1),(0,241),(-3,-4),
            (319,-1),(-1,255),(321-w,241),(40,50)):
            m.origin(ident,ox,oy)
            assert m.peer(4)==peer;count+=1
        m.origin(ident,-3,10)
        allocs=m.ext_allocs;temps=m.temp_tries;fences=m.tofs
        m.origin(ident,-3,20)
        assert (m.ext_allocs,m.temp_tries,m.tofs)==(allocs,temps,fences);count+=1
        m.origin(ident,-w,1);allocs=m.ext_allocs;temps=m.temp_tries;fences=m.tofs
        m.origin(ident,320,255)
        assert (m.ext_allocs,m.temp_tries,m.tofs)==(allocs,temps,fences);count+=1
        m.origin(ident,40,50);m.origin(ident+1,45,55)
        allocs=m.ext_allocs;temps=m.temp_tries
        for i in range(4):
            f=ident+i%2;before=m.tofs
            m.origin(f,50+i,70+i)
            assert m.tofs-before==2
            assert (m.ext_allocs,m.temp_tries)==(allocs,temps)
            assert m.peer(4)==peer;count+=1
        m.origin(ident,-3,241);m.origin(ident+1,319,-1);count+=2
        m.origin(ident+1,35,40)
        last=ident+1
        if ident==1:
            m.origin(9,-1,240);last=9;count+=1
        im=parse_payload(m.payload).image(last)
        old=m.peer(2);events=list(m.ext_events);fences=m.tofs;temps=m.temp_tries
        x=-2**31 if im.hotspot_x>0 else 2**31-1
        assert m.sprite(image=last,x=x,y=im.hotspot_y)==-128
        assert m.peer(2)==old and m.peer(4)==peer and m.ext_events==events
        assert m.tofs==fences and m.temp_tries==temps;count+=1
        m.erase()
        for ox,oy in ((-1,-1),(320,256),(40,60),(319,255),(40,60)):
            m.origin(last,ox,oy);assert m.peer(4)==peer;count+=1
        assert m.sprite(image=ident,x=30,y=40)<0
        m.owned();count+=1
        if version==39:m.close(end=True)
        else:assert m.bankfree()==1
        m.empty_wide();count+=1
    print('S2F_CLIP_PUBLIC_PASS',layout,count,flush=True)
    negative=0
    for w,version in product((16,32,64),(39,40)):
        for at in (1,2,3):
            m=HotClip(image,info,layout,w,version)
            m.fail_temp_at=m.temp_tries+at
            assert m.sprite(image=7,x=w//2-1,y=8)<0
            m.empty_wide();negative+=1
        for at in (1,2,3,4):
            m=HotClip(image,info,layout,w,version);m.fail_ext_at=at
            assert m.sprite(image=7,x=w//2-1,y=8)<0
            m.empty_wide();negative+=1
        for failure in ('scratch','even','odd'):
            m=HotClip(image,info,layout,w,version);m.origin(7,40,50)
            peer=m.peer(2);owned=set(m.temp_live)
            if failure=='scratch':m.fail_temp_at=m.temp_tries+1
            else:m.fail_ext_at=m.ext_allocs+(1 if failure=='even' else 2)
            assert m.sprite(image=7,x=w//2-1,y=8)<0
            assert m.peer(2)==peer and m.temp_live==owned
            m.clipped(2,7,40+w//2,58)
            assert m.off()==1;m.empty_wide();negative+=1
        m=HotClip(image,info,layout,w,version);m.origin(7,20,30)
        m.change_fail=True
        assert m.sprite(image=8,x=-4,y=-4)<0
        m.empty_wide();negative+=1
        m=HotClip(image,info,layout,w,version);m.origin(7,-1,10);m.origin(8,319,255)
        m.stale_free=2;m.close()
        assert m.get(STATE) and m.named and m.ext
        m.owned()
        m.put32(display.FAST_TABLE+8,0);m.copper(2,display.NEUTRAL)
        m.stale_free=0;m.close();m.empty_wide();negative+=1
        m=HotClip(image,info,layout,w,version)
        m.origin(1,10,20);m.origin(2,25,40)
        m.origin(3,20,30,n=2,ch=4)
        r=m.record(2);save=m.get(r+STAGECACHE);live=set(m.temp_live)
        m.put32(r+STAGECACHE,m.get(r+CACHE))
        assert m.off()==0 and m.temp_live==live
        m.put32(r+STAGECACHE,save)
        m.put32(m.named+52,0x00070270)
        assert m.off()==0 and m.temp_live==live
        m.put32(m.named+52,0x000802a0)
        p=m.get(r+CACHE);magic=m.get(p)
        m.put32(p,0)
        assert m.off()==0 and m.temp_live==live
        m.put32(p,magic)
        m.close();m.empty_wide();negative+=3
    print('S2F_CLIP_PUBLIC_NEGATIVE_PASS',layout,negative,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('runtime','compiled','zero-runtime','zero-compiled',
                    'agapic','pattern','safeport','bob','capture','chain'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2f(a.vasm)
    print('S2F_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite in ('runtime','compiled'):public(image,info,a.suite)
    elif a.suite.startswith('zero-'):
        with patch.object(display,'WidePublic',ClipBase):
            display.cases(image,info,a.suite[5:],clipping=True)
    elif a.suite=='agapic':
        for layout in ('runtime','compiled'):agapic_cases(image,layout)
    elif a.suite=='pattern':
        prior,_=regress.build_l2(a.vasm)
        regress.verify_linked_source(a.vasm,before[1])
        assert regress.run_pattern_cases(prior,image)==184
    elif a.suite=='safeport':assert regress.run_cases(image,info)==172
    elif a.suite=='capture':
        from test_m19_s2d_public_capture_gate_a import capture_cases,wide_cases
        for layout in ('runtime','compiled'):capture_cases(image,layout);wide_cases(image,layout)
    elif a.suite=='chain':
        from test_m19_s2c_public_gate_a import chain
        chain(image)
    else:
        _,meta=regress.build_l2(a.vasm)
        regress.l2_gate.IMAGE,regress.l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(regress.l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
    assert protected()==before
    print('S2F_PUBLIC_SUITE_PASS '+a.suite,flush=True)
if __name__=='__main__':main()
