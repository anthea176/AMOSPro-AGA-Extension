#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exact P3 AP20 Runtime/Compiler placement models, not real AmigaOS."""
import argparse,json,os
from pathlib import Path
from struct import pack,unpack_from
from itertools import product
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from build_m19_s2d_in_memory import build_s2d,protected
from test_m19_s1p2k_gate_a import TransactionMachine
from test_m19_s1p2i_gate_a import STATE,CI,TASK,GROUP,INTUI
from test_m19_s1p2j_gate_a import FAST_TABLE
from test_m19_s1p1c_amos_bank_commit import EXEC,CODE
from test_m19_s1p1c_pipeline import SCREEN,GFX,COLORMAP
from test_m19_s2a_public_gate_a import VIEW
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
from m19_s2d_visual_fixture import RGB,FAMILIES,pixels
VP=SCREEN+44
NEUTRAL=CI+176
PAIRS=(2,4,6)
REC_BYTES=168
ID,BANK,IMAGE,GEN,STAGE,COLORS,PAL=(96,100,104,108,112,116,120)

def bank(width):
    raw=empty_bank()
    for family,rgb in enumerate(FAMILIES):
        count=len(rgb)//3
        for j in (0,1):
            raw=put_capture(raw,1+family*2+j,pixels(width,16,count,j),
                width,16,0,0,width,16,bytes(3)+rgb,0,mode='s2')
    # third frame in family 0 and alternate width to exercise width refusal
    raw=put_capture(raw,9,pixels(width,16,3,0),width,16,0,0,width,16,
                    bytes(3)+FAMILIES[0],0,mode='s2')
    other=32 if width==16 else 16
    return put_capture(raw,10,pixels(other,16,3,0),other,16,0,0,other,16,
                    bytes(3)+FAMILIES[0],0,mode='s2')

class WidePublic(TransactionMachine):
    def __init__(self,image,info,layout,width,version=40,db=False):
        super().__init__(image,info,layout,db)
        self.unit142=info['unit142']
        self.erase()
        self.payload=bank(width)
        self.node=self.make_bank(29,b'AGASPRT ',self.payload)
        self.cmap=bytes(51)+RGB+bytes(768-96)
        self.put32(VIEW,VP)
        self.put32(VP,0);self.put32(VP+12,0);self.put32(VP+20,0)
        self.put16(VP+24,320);self.put16(VP+26,256)
        self.put16(GFX+16,1100);self.put16(GFX+20,version)
        self.put16(GFX+444,1)
        self.uc.mem_write(GFX+237,b'\x03')
        self.uc.mem_write(GFX+448,b'\x01')
        for off in (390,930,1020,1026,1032):
            self.uc.mem_write(GFX-off,b'\x4e\x75')
        self.ext={}
        self.version=version
        self.width=width
        self.ext_allocs=0
        self.ext_frees=0
        self.fail_ext_at=0
        self.change_fail=False
        self.stale_free=0
        self.preget_ref=False
        self.ext_events=[]
        self.pseudo_sites={CODE+i for i in range(0,len(self.code)-1,2)
                           if self.code[i:i+2]==b'\xfe\x11'}
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.watch)
        assert self.select(29)==1

    def record(self,ch):
        assert self.named
        return self.named+108+REC_BYTES*((ch-2)//2)
    def pointer(self,ch):
        return self.word(CI+90+8*ch)*65536+self.word(CI+94+8*ch)
    def watch(self,uc,access,a,n,v,user):
        # Only V39 detached ATTACH control bytes may be natively written.
        for p,(data,w,h,att) in self.ext.items():
            if p<=a<p+32:
                raise AssertionError(('native ExtSprite write',hex(a)))
            if data<=a<data+(h+2)*w//4:
                assert self.version==39 and att and n==1
                assert a-data in (3,w//8+1)
                assert v&128 and not any(self.get(FAST_TABLE+4*c)==p for c in range(8))
    def model_move(self,p,x,y):
        assert p in self.ext
        c=self.word(p+10);data,w,h,att=self.ext[p]
        assert c in range(2,8)
        self.put16(p+6,x);self.put16(p+8,y)
        self.put32(FAST_TABLE+4*c,p)
        self.copper(c,NEUTRAL if y>256 else data)
        if not c&1:
            odd=self.get(FAST_TABLE+4*(c+1))
            if odd in self.ext and self.ext[odd][3]:
                self.model_move(odd,x,y)
    def on_code(self,uc,address,size,user):
        if not hasattr(self,'ext'):
            return super().on_code(uc,address,size,user)
        if CODE<=address<CODE+len(self.code) and address not in self.pseudo_sites:return
        if GROUP<=address<GROUP+self.unit142:return
        a0=uc.reg_read(UC_M68K_REG_A0);a1=uc.reg_read(UC_M68K_REG_A1)
        a2=uc.reg_read(UC_M68K_REG_A2)
        d0=uc.reg_read(UC_M68K_REG_D0);d1=uc.reg_read(UC_M68K_REG_D1)
        result=0
        if address==EXEC-534 and CI<=a1<CI+192:
            result=3
        elif address==GFX-390:
            h=uc.reg_read(UC_M68K_REG_D2)
            assert d0 in (2,4) and d1 in (16,32,64) and 1<=h<=256
            self.uc.mem_write(a0,pack('>HHBBH',d1//8,h,0,d0,0))
        elif address==GFX-1020:
            assert self.depth==0
            stride,h,flags,depth,pad,*planes=unpack_from('>HHBBH8I',self.read(a2,40))
            width=stride*8
            tags=unpack_from('>6I',self.read(a1,24))
            att=tags[2]==0x81000008
            assert tags==((0x81000000,width,0x81000008,1,0,0) if att
                          else (0x81000000,width,0,0,0,0))
            assert width in (16,32,64) and 1<=h<=256 and depth in (2,4)
            assert not att or depth==4
            self.ext_allocs+=1
            if self.fail_ext_at==self.ext_allocs:
                self.volatile(uc,0);return
            p=self.allocate(32);data=self.allocate((h+2)*stride*2)
            self.chip.add(data)
            self.ext[p]=(data,width,h,att)
            self.uc.mem_write(p,pack('>IHHHH',data,h,0xdead,0xbeef,0xffff))
            raw=bytearray((h+2)*stride*2)
            if att and self.version!=39:
                raw[3]=raw[stride+1]=128
            for y in range(h):
                for b in range(2):
                    src=planes[b+2*att]+stride*y
                    dst=(y+1)*stride*2+b*stride
                    raw[dst:dst+stride]=self.read(src,stride)
            self.uc.mem_write(data,bytes(raw))
            self.ext_events.append(('alloc',p))
            if self.preget_ref and self.ext_allocs==4:
                # Simulate a reference from a foreign slot without a Get.
                self.put32(FAST_TABLE,p)
            result=p
        elif address==GFX-930:
            tags=unpack_from('>6I',self.read(a1,24))
            c=tags[1];assert tags==(0x82000020,c,0,0,0,0)
            assert 2<=c<=7 and a2 in self.ext
            r=self.record(c&~1)
            assert self.get(r+24)==(5 if c&1 else 4)
            assert self.get(r+4+4*(c&1))==a2
            mask=self.read(GFX+166,1)[0]
            if c==self.reject_channel or mask&(1<<c):
                result=0xffffffff
            else:
                _,w,_,_=self.ext[a2]
                assert self.word(GFX+444)==w//16 or mask==1
                self.put16(GFX+444,w//16)
                self.put16(a2+10,c)
                self.uc.mem_write(GFX+166,bytes([mask|1<<c]))
                self.ext_events.append(('get',c));result=c
        elif address==GFX-426:
            assert a0==VP and a1 in self.ext and self.depth==0
            c=self.word(a1+10)
            assert self.get(self.record(c&~1)+24)==15
            self.model_move(a1,d0,d1)
            self.ext_events.append(('move',c,d0,d1))
        elif address==GFX-1026:
            assert a0==VP and a1 in self.ext and a2 in self.ext and a1!=a2
            c=self.word(a1+10);r=self.record(c&~1)
            assert self.get(r+24)==15 and self.depth==0
            assert self.read(uc.reg_read(UC_M68K_REG_A3),8)==bytes(8)
            assert self.pointer(c&~1)==self.pointer((c&~1)+1)==NEUTRAL
            assert self.word(a1+6)==0 and self.word(a1+8)==257
            if not self.change_fail:
                self.put16(a2+10,c);self.model_move(a2,0,257)
                self.ext_events.append(('change',c));result=0xffffffff
        elif address==GFX-414:
            c=d0;assert c in range(2,8) and self.depth==0
            r=self.record(c&~1)
            assert not self.get(r+24)&(1<<(c&1))
            assert self.get(r+84)&0x80000000
            mask=self.read(GFX+166,1)[0];assert mask&(1<<c)
            mask&=~(1<<c)
            self.uc.mem_write(GFX+166,bytes([mask]))
            if c!=self.stale_free:
                self.put32(FAST_TABLE+4*c,0);self.copper(c,NEUTRAL)
            if mask==1:self.put16(GFX+444,1)
            self.ext_events.append(('release',c))
        elif address==GFX-1032:
            p=a2
            assert p in self.ext and self.depth==0
            data,w,h,att=self.ext[p]
            for c in range(8):
                assert self.get(FAST_TABLE+4*c)!=p
                assert not data<=self.pointer(c)<data+(h+2)*w//4
            if self.named:
                for c in PAIRS:
                    r=self.record(c)
                    assert p not in tuple(self.get(r+off) for off in (4,8,52,56,72,76))
            self.ext.pop(p)
            self.chip.remove(data)
            for ptr in (p,data):
                self.uc.mem_write(ptr,b'\xa5'*self.allocations.pop(ptr))
            self.ext_frees+=1;self.ext_events.append(('free',p))
        elif address==GFX-270:
            assert self.depth==0
            self.tofs+=1
        elif address==GFX-708:
            # Bypass old P2j ordering assertion: P3 probes before Get.
            from test_m19_s1p2i_gate_a import SpriteMachine
            return SpriteMachine.on_code(self,uc,address,size,user)
        elif address==GFX-900:
            assert a0==COLORMAP and 0<=d0<=255 and 1<=d1<=256-d0
            self.uc.mem_write(a1,b''.join(pack('>I',v*0x01010101)
                for v in self.cmap[3*d0:3*(d0+d1)]))
        elif address==INTUI-66:
            assert not self.ext and self.read(GFX+166,1)[0]==1
            return super().on_code(uc,address,size,user)
        else:
            return super().on_code(uc,address,size,user)
        self.volatile(uc,result)

    def frame(self,ch,ident,x,y):
        r=self.record(ch);im=parse_payload(self.payload).image(ident)
        assert self.get(r+24)==31 and self.get(r+IMAGE)==ident
        assert self.get(r+12)==im.width and self.get(r+16)==im.depth
        for part,offset in enumerate((52,56) if im.depth==4 else (52,)):
            p=self.get(r+offset);data,w,h,att=self.ext[p]
            assert (w,h,att)==(im.width,im.height,bool(part))
            assert self.get(FAST_TABLE+4*(ch+part))==p
            assert self.pointer(ch+part)==data
            assert self.word(p+6)==x and self.word(p+8)==y
            stride=w//8
            want=bytearray()
            for row in range(h):
                for bit in (2*part,2*part+1):
                    want.extend(bytes(sum(((im.index(col+i,row)>>bit)&1)<<(7-i)
                                      for i in range(8)) for col in range(0,w,8)))
            assert self.read(data+2*stride,len(want))==want
            assert self.read(data+3,1)[0]>>7==int(att)
            assert self.read(data+stride+1,1)[0]>>7==int(att)
            assert self.read(data+(h+1)*stride*2,stride*2)==bytes(stride*2)
        if im.depth==2:
            assert self.pointer(ch+1)==NEUTRAL
    def peer(self,ch):
        r=self.record(ch)
        return (self.read(r,REC_BYTES),self.read(FAST_TABLE+4*ch,8),self.read(CI+88+8*ch,16))
    def empty_wide(self):
        assert not self.temp_live and not self.chip and not self.named and not self.get(self.cell), (
            'leak',self.temp_live,self.chip,self.named,self.get(self.cell),self.ext)
        assert not self.ext and self.read(GFX+166,1)[0]==1
        assert all(self.get(FAST_TABLE+4*c)==0 and self.pointer(c)==NEUTRAL for c in range(2,8))

def cases(image,info,layout,*,clipping=False):
    moves=changes=neg=cycles=0
    for w in (16,32,64):
        for version in (39,40):
            for kinds in product((2,4),repeat=3):
                m=WidePublic(image,info,layout,w,version,db=(kinds==(4,4,4)))
                ids=[7 if k==4 else 1+2*i for i,k in enumerate(kinds)]
                for i,(ch,ident) in enumerate(zip(PAIRS,ids)):
                    rc=m.sprite(n=17+i,image=ident,x=12+ch,y=40+ch)
                    assert rc==1,('first show',layout,w,version,kinds,ch,rc)
                    m.frame(ch,ident,12+ch,40+ch)
                assert m.get(m.root())==3
                assert m.sprite(n=64,image=7)==-206;neg+=1
                for j in range(4):
                    for i,(ch,ident) in enumerate(zip(PAIRS,ids)):
                        peer={p:m.peer(p) for p in PAIRS if p!=ch}
                        f=ident+1-j%2
                        before=m.tofs
                        rc=m.sprite(n=17+i,image=f,x=50+j,y=70+ch)
                        assert rc==1,('exchange',layout,w,version,kinds,ch,j,rc)
                        assert m.tofs-before==2
                        m.frame(ch,f,50+j,70+ch)
                        changes+=1
                        if j:assert m.ext_allocs==warm[i]
                        rc=m.sprite(n=17+i,image=f,x=65+j,y=90+ch)
                        assert rc==1,('move',layout,w,version,kinds,ch,j,rc)
                        m.frame(ch,f,65+j,90+ch)
                        moves+=1
                        assert all(m.peer(p)==v for p,v in peer.items())
                    warm=[m.ext_allocs]*3
                m.close(end=(kinds==(4,4,4)))
                assert not m.get(STATE)
                m.empty_wide();cycles+=1
                print('S2D_P3_CLOSE_PASS',layout,w,version,kinds,flush=True)
        m=WidePublic(image,info,layout,w)
        assert m.sprite(n=42,image=1)==1
        assert m.sprite(n=42,image=2)==1
        assert m.sprite(n=42,image=9)==1
        m.frame(2,9,32,112)
        assert m.sprite(n=42,image=1)==1
        m.frame(2,1,32,112)
        old=m.peer(2)
        # S2f accepts partially visible rectangles. The positive clip
        # oracle is separate; keep every historical negative by default.
        edge_refusals=() if clipping else ({'n':42,'image':1,'x':321-w},{'n':42,'image':1,'y':241})
        for kw in ({'n':9,'image':10},{'n':42,'image':10},{'n':42,'image':7})+edge_refusals:
            assert m.sprite(**kw)<0 and m.peer(2)==old;neg+=1
        assert m.off(64)==1 and m.peer(2)==old
        assert m.off(42)==1 and m.off(42)==1;m.empty_wide()
        assert m.sprite(n=42,image=10)==1
        assert m.bankfree()==1;m.empty_wide();cycles+=1
        for at in (1,2,3,4):
            m=WidePublic(image,info,layout,w);m.fail_ext_at=at
            assert m.sprite(image=7)<0;m.empty_wide();neg+=1
        for ch in (2,3):
            m=WidePublic(image,info,layout,w);m.reject_channel=ch
            assert m.sprite(image=7)<0;m.empty_wide();neg+=1
        m=WidePublic(image,info,layout,w)
        assert m.sprite(image=7)==1
        m.change_fail=True
        assert m.sprite(image=8)<0;m.empty_wide();neg+=1
        m=WidePublic(image,info,layout,w)
        assert m.sprite(image=7)==1
        m.close_ok=False;m.close()
        assert m.get(STATE)==SCREEN and m.named and not m.ext
        assert m.get(m.root())==0
        m.close_ok=True;m.close();m.empty_wide();neg+=1
        m=WidePublic(image,info,layout,w)
        m.preget_ref=True
        assert m.sprite(image=7)==-208 and m.named and len(m.ext)==4
        assert m.get(m.record(2)+24)==4 and not m.ext_frees
        assert not any(e[0] in ('get','release') for e in m.ext_events)
        assert m.off(1)==0 and len(m.ext)==4 and not m.ext_frees
        m.put32(FAST_TABLE,0x40002700)
        before=m.tofs
        assert m.off(1)==1 and m.tofs-before==2
        m.empty_wide();neg+=1
        m=WidePublic(image,info,layout,w)
        assert m.sprite(image=7)==1
        m.stale_free=2;m.close()
        assert m.get(STATE)==SCREEN and m.named and m.ext
        assert m.get(m.record(2)+24)==4 and not m.ext_frees
        m.put32(FAST_TABLE+8,0);m.copper(2,NEUTRAL)
        m.stale_free=0;m.close();m.empty_wide();neg+=1
    print('S2D_P3_PUBLIC_DISPLAY_PASS',layout,'moves',moves,'changes',changes,
          'negative',neg,'cycles',cycles,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('runtime','compiled','capture','chain'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2d(a.vasm)
    print('S2D_P3_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite in ('runtime','compiled'):cases(image,info,a.suite)
    elif a.suite=='capture':
        from test_m19_s2d_public_capture_gate_a import capture_cases,wide_cases
        for layout in ('runtime','compiled'):capture_cases(image,layout);wide_cases(image,layout)
    else:
        from test_m19_s2c_public_gate_a import chain
        chain(image)
    assert protected()==before
    print('S2D_P3_SUITE_PASS '+a.suite,flush=True)
if __name__=='__main__':main()
