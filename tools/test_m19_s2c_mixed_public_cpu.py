#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exercise exact public AP20 mixed paths with modeled Exec/Gfx/Intuition."""
from itertools import product
from struct import pack
from unicorn.m68k_const import *
from test_m19_s2b_public_gate_a import MultiMachine,PAIRS,SCREEN,GFX,COLORMAP,CI,FAST_TABLE
from m19_s1_agsp_bank import empty_bank,put_capture,parse_payload
RGB=bytes(v for i in range(1,16) for v in (i,255-i,(i*19)&255))
VP=SCREEN+44

def mixed_bank():
    raw=empty_bank()
    for k in range(3):
        pal=bytes(3)+RGB[12+12*k:21+12*k]
        for j in range(2):
            pix=bytes((x+y*(1+2*j))%4 for y in range(16) for x in range(16))
            raw=put_capture(raw,3+k*2+j,pix,16,16,0,0,16,16,pal,0)
    for j in range(2):
        pix=bytes((x+y*(1+2*j))%16 for y in range(16) for x in range(16))
        raw=put_capture(raw,9+j,pix,16,16,0,0,16,16,bytes(3)+RGB,0,mode='s2')
    return raw

class MixedPublic(MultiMachine):
    def __init__(self,image,info,layout,db):
        super().__init__(image,info,layout,db)
        self.erase()
        self.payload=mixed_bank()
        self.node=self.make_bank(29,b'AGASPRT ',self.payload)
        cmap=bytearray(768);cmap[51:96]=RGB;self.cmap=bytes(cmap)
        self.put32(VP,0);self.put32(VP+12,0);self.put32(VP+20,0)
        self.put16(VP+24,320);self.put16(VP+26,256)
        assert self.select(29)==1
    def watch_frames(self,uc,access,addr,size,value,user):
        for p,n in self.published.items():
            r=self.record(n)
            if self.get(r+44)==4:
                if p+96<=addr<p+self.allocations[p]:
                    stream=self.get(p+88)
                    active=self.get(p)
                    if size==1 and addr==self.get(p+12)+3:
                        assert self.get(r+12)==15
                        assert all(self.word(CI+90+8*c)<<16|self.word(CI+94+8*c)==CI+176 for c in (n,n+1))
                    else:
                        assert active in (p+96,p+96+2*stream)
                        spare=p+96+2*stream if active==p+96 else p+96
                        assert spare<=addr and addr+size<=spare+2*stream
                        assert self.tofs-self.last_pub[p]>=2
            elif p+48<=addr<p+self.allocations[p]:
                active=self.get(p);stream=self.get(p+44)-48
                assert active in (p+48,p+48+stream)
                spare=p+48+stream if active==p+48 else p+48
                assert spare<=addr and addr+size<=spare+stream
                assert self.tofs-self.last_pub[p]>=2
    def attached_desc(self,a):
        for p,n in self.published.items():
            if self.get(self.record(n)+44)==4 and a in (p,p+12):
                return p,n+(a!=p)
        if self.named:
            for n in PAIRS:
                r=self.record(n);p=self.get(r)
                if p and self.get(r+44)==4 and a in (p,p+12):return p,n+(a!=p)
        return None
    def model_move(self,a,x,y):
        p,n=self.attached_desc(a);ptr=self.get(a);h=self.word(a+4)
        self.put16(a+6,x);self.put16(a+8,y);self.put32(FAST_TABLE+4*n,a)
        ctl=(((y+h)&255)<<8)|(self.read(ptr+3,1)[0]&128)|(4 if y>=256 else 0)
        self.put32(ptr,((y&255)<<24)|((x&255)<<16)|ctl)
        self.copper(n,CI+176 if y>256 else ptr)
        if not n&1:
            odd=self.get(FAST_TABLE+4*(n+1))
            if odd and self.read(self.get(odd)+3,1)[0]&128:self.model_move(odd,x,y)
        self.moves.append((n,x,y))
        if y<=256:self.last_pub[p]=self.tofs
    def on_code(self,uc,address,size,user):
        d0=uc.reg_read(UC_M68K_REG_D0);d1=uc.reg_read(UC_M68K_REG_D1)
        a0=uc.reg_read(UC_M68K_REG_A0);a1=uc.reg_read(UC_M68K_REG_A1)
        if address==GFX-900 and d0==17:
            assert a0==COLORMAP and 4<=d1<=15
            uc.mem_write(a1,b''.join(pack('>I',v*0x01010101) for v in self.cmap[51:51+3*d1]))
            self.volatile(uc,0);return
        if address==GFX-408 and self.named and self.get(self.record(d0&~1)+44)==4:
            r=self.record(d0&~1);p=self.get(r)
            assert a0==p+12*(d0&1) and self.depth==0
            assert self.get(r+12)==(5 if d0&1 else 0)
            mask=self.read(GFX+166,1)[0]
            if d0==self.reject_channel or mask&(1<<d0):
                self.put16(a0+10,65535);self.volatile(uc,65535);return
            self.uc.mem_write(GFX+166,bytes([mask|1<<d0]))
            self.put16(a0+10,d0);self.sprite_calls.append('get'+str(d0))
            self.volatile(uc,d0);return
        if address in (GFX-420,GFX-426):
            desc=self.attached_desc(a1)
            if desc:
                p,n=desc;r=self.record(n&~1)
                assert a0==VP and self.get(r+12)==15
                if address==GFX-420:
                    ptr=uc.reg_read(UC_M68K_REG_A2);stream=self.get(p+88)
                    assert ptr in (p+96+(n&1)*stream,p+96+(2+(n&1))*stream)
                    assert self.word(a1+8)==257
                    self.published[p]=n&~1
                    if not self.change_noop:
                        self.put32(a1,ptr);self.model_move(a1,self.word(a1+6),257)
                else:
                    assert not n&1
                    if not self.move_noop:self.model_move(a1,d0,d1)
                self.volatile(uc,0);return
        return super().on_code(uc,address,size,user)
    def assert_attached(self,n,ident,x,y):
        r,p,ptr=self.live(n);stream=self.get(p+88)
        assert self.get(r+12)==31 and self.get(r+44)==4
        assert self.word(p+28)==self.get(r+36)==ident
        assert ptr in (p+96,p+96+2*stream) and self.get(p+12)==ptr+stream
        assert self.read(ptr+3,1)[0]&128==0 and self.read(ptr+stream+3,1)[0]&128
        for a,ch in ((p,n),(p+12,n+1)):
            assert self.word(a+6)==x and self.word(a+8)==y
            assert self.get(FAST_TABLE+4*ch)==a
            assert self.word(CI+90+8*ch)<<16|self.word(CI+94+8*ch)==self.get(a)
        j=ident-9
        for group in (0,1):
            expected=bytearray()
            for row in range(16):
                words=[]
                for bit in (group*2,group*2+1):
                    word=0
                    for col in range(16):
                        value=(col+row*(1+2*j))%16
                        word|=((value>>bit)&1)<<(15-col)
                    words.append(word)
                expected.extend(pack('>HH',*words))
            assert self.read(ptr+group*stream+4,64)==bytes(expected)
            assert self.read(ptr+group*stream+68,4)==bytes(4)
    def assert_frame(self,n,kind,img,x,y):
        if kind==4:self.assert_attached(n,img,x,y)
        else:self.assert_pixels(n,img,x,y)

def mixed_cases(image,info,layout):
    nchanges=0
    for kinds in product((2,4),repeat=3):
        for db in (False,True):
            m=MixedPublic(image,info,layout,db)
            images={n:(9 if kind==4 else 3+2*i) for i,(n,kind) in enumerate(zip(PAIRS,kinds))}
            for n,kind in zip(PAIRS,kinds):
                img=images[n];rc=m.sprite(n=n,image=img,x=20+n,y=48+n)
                assert rc==1,('show',layout,kinds,n,rc)
                m.assert_frame(n,kind,img,20+n,48+n)
            base=dict(m.allocations)
            for j in range(6):
                for n,kind in zip(PAIRS,kinds):
                    peers={ch:m.snapshot(ch) for ch in PAIRS if ch!=n}
                    img=images[n]+1-j%2;t=m.tofs
                    rc=m.sprite(n=n,image=img,x=50+j,y=90+n)
                    assert rc==1,('change',layout,kinds,n,j,rc)
                    assert m.tofs-t==2
                    m.assert_frame(n,kind,img,50+j,90+n)
                    assert m.sprite(n=n,image=img,x=70+j,y=96+n)==1
                    m.assert_frame(n,kind,img,70+j,96+n)
                    assert m.allocations==base and all(m.snapshot(ch)==snap for ch,snap in peers.items())
                    nchanges+=1
            assert m.sprite(n=60,image=9)<0
            m.close(end=db)
            m.empty_sprites()
    m=MixedPublic(image,info,layout,False)
    assert m.sprite(n=2,image=9)==1
    before=m.snapshot(2)
    assert m.sprite(n=2,image=3)<0 and m.snapshot(2)==before
    assert m.sprite(n=2,image=10,x=305)<0 and m.snapshot(2)==before
    m.reject_channel=5
    assert m.sprite(n=4,image=9)<0 and m.snapshot(2)==before
    m.reject_channel=0
    assert m.sprite(n=4,image=9)==1
    assert m.off(n=4)==1 and m.snapshot(2)==before
    assert m.bankfree(29)==1
    m.empty_sprites()
    print('S2C_P1C_MIXED_PASS',layout,nchanges,'changes',flush=True)
