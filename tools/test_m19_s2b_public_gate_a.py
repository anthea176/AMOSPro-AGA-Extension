#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2b exact AP20 public entry tests; MC68020, modeled Exec/Gfx/Intuition."""
import argparse,json,os,unittest
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from unicorn import UC_HOOK_MEM_WRITE
from build_m19_s2b_in_memory import build_s2b,protected
from test_m19_s1p2i_gate_a import SpriteMachine,STATE,CI,TASK,GROUP,INTUI
from test_m19_s1p2k_gate_a import TransactionMachine
from test_m19_s1p2j_gate_a import FAST_TABLE
from test_m19_s1p1c_amos_bank_commit import EXEC,CODE
from test_m19_s1p1c_pipeline import SCREEN,GFX,COLORMAP
from test_m19_s2a_public_gate_a import VIEW
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload,s0_interleaved_image
import test_m19_s1p2m_gate_a as regress

PALETTES=(bytes.fromhex('000000ff462824dc751a73ff'),
          bytes.fromhex('000000f8d85a34c5e06849bb'),
          bytes.fromhex('000000ff81c96bc34ffefefe'))
PAIRS=(2,4,6)
def multi_bank():
    raw=empty_bank()
    for k,pal in enumerate(PALETTES):
        for j in range(2):
            pixels=bytes((x+y*(1+2*j)+k*(y//4))%4 for y in range(16) for x in range(16))
            raw=put_capture(raw,3+2*k+j,pixels,16,16,0,0,16,16,pal,0)
    return raw

class MultiMachine(TransactionMachine):
    def __init__(self,image,info,layout,db=False):
        super().__init__(image,info,layout,db)
        self.unit142=info['unit142']
        self.put32(VIEW,SCREEN+44)
        self.erase()
        self.payload=multi_bank()
        self.node=self.make_bank(29,b'AGASPRT ',self.payload)
        cmap=bytearray(768)
        for i,pal in enumerate(PALETTES):cmap[3*(21+4*i):3*(24+4*i)]=pal[3:12]
        self.cmap=bytes(cmap)
        self.newptr=0x220000
        self.pseudo_sites={CODE+i for i in range(0,len(self.code)-1,2)
                           if self.code[i:i+2]==bytes.fromhex('fe11')}
        self.published={}
        self.last_pub={}
        self.retired={}
        self.freed=[]
        self.switches=0
        self.wait_mutation=None
        self.alloc_mutation=None
        self.stale_pair=None
        self.image_noop=False
        self.change_noop=False
        self.move_noop=False
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.watch_frames)
    def record(self,n):
        return self.named+108+44*((n-2)//2)
    def live(self,n):
        r=self.record(n)
        return r,self.get(r),self.get(self.get(r))
    def snapshot(self,n):
        r,p,ptr=self.live(n)
        return (self.read(r,44),self.read(p,self.allocations[p]),
                self.read(FAST_TABLE+4*n,8),self.read(CI+88+8*n,16))
    def watch_frames(self,uc,access,addr,size,value,user):
        for p,n in self.published.items():
            if p+48<=addr<p+self.allocations[p]:
                active=self.get(p)
                f=self.get(p+44)-48
                assert active in (p+48,p+48+f)
                spare=p+48+f if active==p+48 else p+48
                assert spare<=addr and addr+size<=spare+f
                assert self.tofs-self.last_pub[p]>=2
    def on_code(self,uc,address,size,user):
        if CODE<=address<CODE+len(self.code) and address not in self.pseudo_sites:return
        if GROUP<=address<GROUP+self.unit142:return
        d0=uc.reg_read(UC_M68K_REG_D0);d1=uc.reg_read(UC_M68K_REG_D1)
        a0=uc.reg_read(UC_M68K_REG_A0);a1=uc.reg_read(UC_M68K_REG_A1)
        result=0
        if address==GFX-408:
            assert d0 in (2,3,4,5,6,7) and self.depth==0
            n=d0&~1;r=self.record(n)
            assert a0==(r+16 if d0&1 else self.get(r))
            assert self.get(r+12)==(5 if d0&1 else 0)
            mask=self.read(GFX+166,1)[0]
            if d0==self.reject_channel or mask&(1<<d0):
                self.put16(a0+10,65535);result=65535
            else:
                self.uc.mem_write(GFX+166,bytes([mask|1<<d0]))
                self.put16(a0+10,d0)
                self.sprite_calls.append('get'+str(d0));result=d0
        elif address==GFX-708:
            return SpriteMachine.on_code(self,uc,address,size,user)
        elif address==GFX-900:
            assert a0==COLORMAP and d0 in (21,25,29) and d1==3
            uc.mem_write(a1,b''.join(pack('>I',v*0x01010101) for v in self.cmap[3*d0:3*d0+9]))
        elif address==GFX-420:
            assert a0==SCREEN+44 and a1 in self.chip
            n=self.word(a1+10);r=self.record(n)
            assert n in PAIRS and self.get(r)==a1 and self.get(r+12)==15
            ptr=uc.reg_read(UC_M68K_REG_A2)
            assert ptr in (a1+48,a1+self.get(a1+44))
            if a1 in self.published:
                assert self.published[a1]==n and ptr!=self.get(a1)
                assert self.tofs-self.last_pub[a1]>=2
                self.switches+=1
                if not self.change_noop:
                    self.put32(a1,ptr);self.copper(n,ptr)
                    self.last_pub[a1]=self.tofs
            else:
                assert ptr==a1+48 and self.get(FAST_TABLE+4*n)==0
                self.published[a1]=n
                self.last_pub[a1]=self.tofs
                if not self.image_noop:self.put32(a1,ptr)
        elif address==GFX-426:
            assert a0==SCREEN+44 and a1 in self.published
            n=self.published[a1];ptr=self.get(a1)
            assert self.word(a1+10)==n and ptr in (a1+48,a1+self.get(a1+44))
            self.put32(FAST_TABLE+4*n,a1);self.copper(n,ptr)
            if not self.move_noop:
                self.put16(a1+6,d0);self.put16(a1+8,d1)
            self.moves.append((n,d0,d1))
        elif address==GFX-414:
            assert d0 in (2,3,4,5,6,7)
            n=d0&~1;r=self.record(n);mask=self.read(GFX+166,1)[0]
            assert mask&(1<<d0) and self.get(r+12)&(1<<(d0&1))
            self.uc.mem_write(GFX+166,bytes([mask&~(1<<d0)]))
            if n!=self.stale_pair:
                self.put32(FAST_TABLE+4*d0,0);self.copper(d0,CI+176)
            if not d0&1:self.retired[self.get(r)]=self.tofs
            self.sprite_calls.append('free'+str(d0))
        elif address==EXEC-690 and a1 in self.published:
            n=self.published[a1]
            assert self.tofs-self.retired[a1]>=2
            assert not self.read(GFX+166,1)[0]&(3<<n)
            for ch in (n,n+1):
                assert not self.get(FAST_TABLE+4*ch)
                assert self.word(CI+90+8*ch)<<16|self.word(CI+94+8*ch)==CI+176
            assert self.get(self.record(n))!=a1
            del self.published[a1];self.freed.append(a1)
            return SpriteMachine.on_code(self,uc,address,size,user)
        elif address==GFX-270:
            assert self.depth==0
            self.tofs+=1
            if self.wait_mutation:
                f=self.wait_mutation;self.wait_mutation=None;f(self)
        elif address==INTUI-66:
            assert not self.read(GFX+166,1)[0]&0xfc
            return super().on_code(uc,address,size,user)
        else:
            res=super().on_code(uc,address,size,user)
            if address==EXEC-684 and d1==0x10003 and self.alloc_mutation:
                f=self.alloc_mutation;self.alloc_mutation=None;f(self)
            return res
        self.volatile(uc,result)
    def assert_pixels(self,n,ident,x=None,y=None):
        r,p,ptr=self.live(n)
        im=parse_payload(self.payload).image(ident)
        raw=s0_interleaved_image(im)
        assert self.read(ptr+4,len(raw)-4)==raw[4:]
        assert self.word(p+16)==self.get(r+36)==ident
        if x is not None:assert self.word(p+6)==x and self.word(p+8)==y
    def empty_sprites(self):
        self.empty()
        assert not self.published
        assert self.read(GFX+166,1)[0]==1
        assert all(self.get(FAST_TABLE+4*n)==0 for n in range(2,8))
    def neutral(self,n):
        for ch in (n,n+1):
            self.put32(FAST_TABLE+4*ch,0);self.copper(ch,CI+176)
    def reopen(self):
        assert self.get(STATE)==0 and not self.named
        for off,v in ((0,SCREEN),(4,INTUI),(8,GFX),(12,320),(16,256),(20,256),(28,8),(32,0),(36,0)):
            self.put32(STATE+off,v)
        self.put32(GFX+34,VIEW);self.put32(GFX+50,0x97000);self.put32(GFX+54,0x98000)
        self.put32(VIEW,SCREEN+44)
        assert self.select(29)==1

def cases(image,info,layout):
    def new(db=False):
        m=MultiMachine(image,info,layout,db)
        assert m.select(29)==1
        return m
    def show_all(m):
        for n,ident,img in ((2,17,3),(4,42,5),(6,64,7)):
            rc=m.sprite(n=ident,image=img,x=32+n*8,y=112)
            assert rc==1,('show',n,rc)
            m.assert_pixels(n,img,32+n*8,112)
        assert m.get(m.root())==3 and len(m.temp_live)==4
    changes=0
    for db in (False,True):
        m=new(db);show_all(m)
        baseline=dict(m.allocations)
        for i in range(100):
            for n,ident,img in ((2,17,3),(4,42,5),(6,64,7)):
                peers={ch:m.snapshot(ch) for ch in PAIRS if ch!=n}
                f=img+1-i%2
                t=m.tofs
                rc=m.sprite(n=ident,image=f,x=40+i,y=80+n*8)
                assert rc==1,('change',n,i,rc)
                assert m.tofs-t==2
                m.assert_pixels(n,f,40+i,80+n*8)
                rc=m.sprite(n=ident,image=f,x=41+i,y=80+n*8)
                assert rc==1,('move',n,i,rc)
                m.assert_pixels(n,f,41+i,80+n*8)
                assert m.allocations==baseline
                assert all(m.snapshot(ch)==snap for ch,snap in peers.items())
                changes+=1
        assert m.switches==300
        snap={n:m.snapshot(n) for n in PAIRS}
        assert m.sprite(n=1,image=3)==-206
        assert all(m.snapshot(n)==s for n,s in snap.items())
        assert m.off(1)==1 and m.off(42)==1
        assert m.snapshot(2)==snap[2] and m.snapshot(6)==snap[6]
        assert m.sprite(n=9,image=5)==1
        m.assert_pixels(4,5)
        m.close(end=db);assert m.get(STATE)==0;m.empty_sprites()
        assert m.bank(29)==m.payload
    # Ten lifetimes, ten complete three-object show/off cycles each.
    m=new()
    baseline=dict(m.allocations)
    for i in range(10):
        if i:m.reopen()
        for j in range(10):
            show_all(m)
            for n in (42,17,64):assert m.off(n)==1
            m.empty_sprites()
            assert m.allocations==baseline
        show_all(m)
        m.close(end=bool(i&1));assert m.get(STATE)==0;m.empty_sprites()
        assert m.bankfree()==1 and m.allocations==baseline
    # Palette group selection must not overwrite an unrelated pair.
    m=new()
    assert m.sprite(n=42,image=5)==1
    m.assert_pixels(4,5)
    assert m.sprite(n=17,image=3)==1
    peer=m.snapshot(4)
    assert m.sprite(n=9,image=5)==-206
    assert m.snapshot(4)==peer
    assert m.bankfree()==1;m.empty_sprites()
    # Different banks: Off and Bank Free affect only the intended record.
    m=new();assert m.sprite(n=17,image=3)==1
    m.make_bank(30,b'AGASPRT ',m.payload)
    assert m.select(30)==1 and m.sprite(n=42,image=5)==1
    peer=m.snapshot(4)
    assert m.bankfree(29)==1 and m.snapshot(4)==peer
    assert m.bankfree(30)==1;m.empty_sprites()
    for n in (2,4,6):
        for fail in (n,n+1):
            m=new();m.reject_channel=fail
            rc=m.sprite(n=17,image=n+1)
            assert rc==(-141 if fail==n else -142),('acquire rollback',n,rc)
            m.empty_sprites()
    m=new();show_all(m);m.stale_pair=4
    assert m.off(42)==0
    assert m.get(m.record(4)+12)==4
    assert m.sprite(n=9,image=5)==-206
    m.close();assert m.get(STATE)==0 and not m.get(m.cell)
    assert len(m.published)==1 and m.get(m.named+56)==1
    assert m.bankfree()==0
    m.stale_pair=None;m.neutral(4)
    assert m.bankfree()==1;m.empty_sprites()
    m=new(True);show_all(m);m.block_replies=True
    m.close();assert m.get(STATE)==SCREEN
    assert m.get(m.root())==3 and len(m.published)==3
    m.block_replies=False
    m.close();assert m.get(STATE)==0;m.empty_sprites()
    m=new();show_all(m);m.close_ok=False
    m.close();assert m.get(STATE)==SCREEN and m.get(m.root())==3
    m.close_ok=True;m.close();assert m.get(STATE)==0;m.empty_sprites()
    m=new();show_all(m);m.task=TASK+4
    assert m.off(42)==0 and m.sprite(n=17,image=3)==-139
    m.close();assert m.get(STATE)==SCREEN
    m.task=TASK
    m.close();assert m.get(STATE)==0;m.empty_sprites()
    m=new();show_all(m);m.change_noop=True
    peer=m.snapshot(2)
    assert m.sprite(n=42,image=6)==-205
    assert m.snapshot(2)==peer and m.get(m.root())==2
    m.close();assert m.get(STATE)==0;m.empty_sprites()
    m=new();show_all(m)
    old=m.snapshot(4)
    m.wait_mutation=lambda k:k.copper(4,k.get(k.get(k.record(4)))+72)
    assert m.sprite(n=42,image=6)==-203
    m.copper(4,m.live(4)[2])
    assert m.snapshot(4)==old
    m.close();assert m.get(STATE)==0;m.empty_sprites()
    assert changes==600
    print('S2B_PUBLIC_PASS',layout,changes,'frame changes; 300 show/off cycles and 10 active closes plus negatives',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('runtime','compiled','chain','pattern','safeport','bob'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2b(a.vasm)
    print('S2B_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite in ('runtime','compiled'):cases(image,info,a.suite)
    elif a.suite=='chain':regress.chain(image)
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
    assert protected()==before
    print('S2B_SUITE_PASS '+a.suite+' '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
