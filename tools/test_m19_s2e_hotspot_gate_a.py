#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2e hotspot arithmetic and exact public AP20 path, MC68020 + OS model.
No actual AMOS Compiler or DMA raster claim.
"""
import argparse,json,os,random
from pathlib import Path
from struct import pack
from itertools import product
from hashlib import sha256
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from m19_s1_agsp_bank import set_hotspot,parse_payload
from build_m19_s2e_in_memory import build_s2e,protected
from test_m19_s2d_public_display_gate_a import WidePublic,FAST_TABLE,CI,PAIRS

CODE,STOP,STACK=0x10000,0x20000,0x38000
MASK=0xffffffff
D=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
   UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
A=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
   UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)
PRESERVED=D[3:]+A

def packed(hx,hy):
    return (hx&65535)<<16 | (hy&65535)

def oracle(x,y,hx,hy,w,h):
    ox,oy=x-hx,y-hy
    return (1,ox,oy) if w in (16,32,64) and 1<=h<=256 and 0<=ox<=320-w and 0<=oy<=256-h else (0,0,0)

def geometry(binary):
    code=Path(binary).read_bytes()
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    u.mem_map(0,0x40000)
    u.mem_write(CODE,code)
    def writes(uc,access,address,size,value,user):
        assert STACK-12<=address and address+size<=STACK, ('unexpected write',hex(address),size)
    u.hook_add(UC_HOOK_MEM_WRITE,writes)
    count=0
    def case(x,y,hx,hy,w,h):
        nonlocal count
        for i,reg in enumerate(PRESERVED):u.reg_write(reg,0x12340000+i)
        for reg,val in zip(D[:5],(x,y,packed(hx,hy),w,h)):u.reg_write(reg,val&MASK)
        keep={reg:u.reg_read(reg) for reg in PRESERVED}
        u.reg_write(UC_M68K_REG_SR,0x2000)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE,STOP,count=200)
        assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(reg)==val for reg,val in keep.items())
        got=tuple(u.reg_read(reg) for reg in D[:3])
        assert got==oracle(x,y,hx,hy,w,h),(x,y,hx,hy,w,h,got)
        count+=1
    for w,h,hx,hy in product((16,32,64),(1,16,255,256),(-32768,-1,0,1,32767),(-32768,-1,0,1,32767)):
        for ox,oy in ((0,0),(320-w,256-h),(-1,0),(321-w,0),(0,-1),(0,257-h)):
            case(ox+hx,oy+hy,hx,hy,w,h)
        case(-2147483648,2147483647,hx,hy,w,h)
        case(2147483647,-2147483648,hx,hy,w,h)
    for w,h in product((0,15,17,128,-1,16,32,64),(0,-1,257,65536,16)):
        case(0,0,0,0,w,h)
    rng=random.Random(0x52E)
    for i in range(400):
        case(rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31),
             rng.randrange(-32768,32768),rng.randrange(-32768,32768),16,16)
    print('S2E_GEOMETRY_PASS',count,'bytes',len(code),'sha256',sha256(code).hexdigest(),flush=True)

class HotPublic(WidePublic):
    def __init__(self,image,info,layout,width,version=40):
        super().__init__(image,info,layout,width,version)
        self.erase()
        p=self.payload
        for i,hx,hy in ((1,width//2,8),(2,-3,-4),(7,width//2,8),(8,-3,-4),(9,32767,-32768)):
            p=set_hotspot(p,i,hx,hy)
        self.payload=p
        self.node=self.make_bank(29,b'AGASPRT ',p)
        assert self.select(29)==1
    def record(self,ch):
        assert self.named
        return self.named+108+172*((ch-2)//2)
    def peer(self,ch):
        return (self.read(self.record(ch),172),self.read(FAST_TABLE+4*ch,8),self.read(CI+88+8*ch,16))
    def anchored(self,ch,ident,x,y):
        im=parse_payload(self.payload).image(ident)
        self.frame(ch,ident,x-im.hotspot_x,y-im.hotspot_y)
        assert self.get(self.record(ch)+168)==packed(im.hotspot_x,im.hotspot_y)
        assert self.get(self.named+52)==0x00070270
        assert self.allocations[self.named]==624

def public(image,info,layout):
    checks=0
    for w,version,ident in product((16,32,64),(39,40),(1,7)):
        m=HotPublic(image,info,layout,w,version)
        hx=w//2;hy=8
        assert m.sprite(image=ident,x=hx-1,y=hy)==-128
        assert not m.ext_allocs
        m.empty_wide();checks+=1
        assert m.sprite(image=ident,x=hx,y=hy)==1
        m.anchored(2,ident,hx,hy);checks+=1
        # Zero-hotspot peer is unchanged by all target calls.
        assert m.sprite(n=2,image=3,x=11,y=21)==1
        m.anchored(4,3,11,21)
        peer=m.peer(4)
        assert m.sprite(image=ident,x=320-w+hx,y=240+hy)==1
        m.anchored(2,ident,320-w+hx,240+hy);checks+=1
        current=m.peer(2)
        events=list(m.ext_events);fences=m.tofs
        for x,y in ((hx-1,hy),(321-w+hx,hy),(hx,hy-1),(hx,241+hy),(-2**31,hy),(hx,2**31-1)):
            assert m.sprite(image=ident,x=x,y=y)==-128
            assert m.peer(2)==current and m.peer(4)==peer
            assert m.ext_events==events and m.tofs==fences
            checks+=1
        assert m.sprite(image=ident+1,x=-4,y=-4)==-128
        assert m.peer(2)==current and m.ext_events==events and m.tofs==fences;checks+=1
        start=len(m.ext_events);fences=m.tofs
        assert m.sprite(image=ident+1,x=-3,y=-4)==1
        m.anchored(2,ident+1,-3,-4)
        assert m.tofs-fences==2 and m.peer(4)==peer
        visible=[e[2:] for e in m.ext_events[start:] if e[0]=='move' and e[3]<=256]
        assert visible and all(xy==(0,0) for xy in visible),visible
        checks+=1
        alloc=m.ext_allocs
        assert m.sprite(image=ident,x=hx+12,y=hy+24)==1
        m.anchored(2,ident,hx+12,hy+24)
        assert m.ext_allocs==alloc and m.peer(4)==peer;checks+=1
        assert m.sprite(image=ident+1,x=17,y=16)==1
        m.anchored(2,ident+1,17,16)
        assert m.ext_allocs==alloc and m.peer(4)==peer;checks+=1
        # Third stage with extreme signed hotspot values; no new format.
        last=ident+1
        if ident==1:
            assert m.sprite(image=9,x=32767+20,y=-32768+30)==1
            m.anchored(2,9,32767+20,-32768+30)
            last=9;checks+=1
        # Preserve the cached current hotspot after source bank removal.
        im=parse_payload(m.payload).image(last)
        m.erase()
        assert m.sprite(image=last,x=im.hotspot_x+25,y=im.hotspot_y+35)==1
        m.anchored(2,last,im.hotspot_x+25,im.hotspot_y+35)
        assert m.peer(4)==peer;checks+=1
        m.close(end=(version==39))
        m.empty_wide();checks+=1
    print('S2E_HOTSPOT_PUBLIC_PASS',layout,checks,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--geometry',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('geometry','runtime','compiled'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    if a.suite=='geometry':geometry(a.geometry)
    else:
        image,info=build_s2e(a.vasm)
        print('S2E_BUILT '+json.dumps(info,sort_keys=True),flush=True)
        public(image,info,a.suite)
    assert protected()==before
if __name__=='__main__':main()
