#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Standalone S2f P1 arithmetic/raster checks; no public or real DMA claim."""
import argparse,random
from hashlib import sha256
from itertools import product
from pathlib import Path
from struct import pack
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

CODE,STOP,SRC,DST,STACK=0x10000,0x20000,0x30000,0x40000,0x70000
MASK=0xffffffff
D=(UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
   UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7)
A=(UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
   UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)
def signed(v):return v if v<0x80000000 else v-0x100000000
def packed(hx,hy):return (hx&65535)<<16 | (hy&65535)

def oracle(x,y,hx,hy,w,h):
    ox,oy=x-hx,y-hy
    if w not in (16,32,64) or not 1<=h<=256:
        return (0,0,0,0,0)
    if not (-2**31<=ox<2**31 and -2**31<=oy<2**31):
        return (0,0,0,0,0)
    if ox+w<=0 or oy+h<=0 or ox>=320 or oy>=256:
        return (3,0,0,0,0)
    px=max(0,min(ox,320-w));py=max(0,min(oy,256-h))
    dx,dy=ox-px,oy-py
    return (2 if dx or dy else 1,px,py,dx,dy)

def raster(raw,w,h,dx,dy):
    # Independent whole-row integer oracle (not the native byte algorithm).
    n=w//8;mask=(1<<w)-1
    rows=[int.from_bytes(raw[i:i+n],'big') for i in range(0,len(raw),n)]
    out=[]
    for y in range(h):
        sy=y-dy
        row=rows[sy] if 0<=sy<h else 0
        row=(row>>dx) if dx>=0 else (row<<(-dx))
        out.append((row&mask).to_bytes(n,'big'))
    return b''.join(out)

class Machine:
    def __init__(self,code):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x80000)
        self.u.mem_write(CODE,code)
        self.read_regions=[];self.write_regions=[]
        self.u.hook_add(UC_HOOK_MEM_READ,self.read)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
    def read(self,uc,access,address,size,value,user):
        assert any(lo<=address and address+size<=hi for lo,hi in self.read_regions),('read',hex(address),size)
    def write(self,uc,access,address,size,value,user):
        assert any(lo<=address and address+size<=hi for lo,hi in self.write_regions),('write',hex(address),size)
    def call(self,entry,args,preserved,ptrs=None,extent=0,writable=False):
        u=self.u
        for i,reg in enumerate(D+A):u.reg_write(reg,0x12340000+i)
        for reg,val in zip(D,args):u.reg_write(reg,val&MASK)
        if ptrs:
            for reg,val in zip(A,ptrs):u.reg_write(reg,val&MASK)
        keep={reg:u.reg_read(reg) for reg in preserved}
        u.reg_write(UC_M68K_REG_SR,0x2000)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        stackbytes=12 if entry==0 else 72
        self.read_regions=[(STACK-stackbytes,STACK+4)]
        self.write_regions=[(STACK-stackbytes,STACK)]
        if extent:
            self.read_regions.append((SRC,SRC+extent))
            if writable:self.write_regions.append((DST,DST+extent))
        u.emu_start(CODE+entry,STOP,count=1000000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(reg)==val for reg,val in keep.items())
        return tuple(signed(u.reg_read(reg)) for reg in D[:5])

def geometry(m):
    count=0
    def case(x,y,hx,hy,w,h):
        nonlocal count
        got=m.call(0,(x,y,packed(hx,hy),w,h),D[5:]+A)
        expected=oracle(x,y,hx,hy,w,h)
        assert got==expected,(x,y,hx,hy,w,h,got,expected)
        count+=1
    for w,h,hx,hy in product((16,32,64),(1,16,255,256),(-32768,-1,0,1,32767),(-32768,-1,0,1,32767)):
        for ox,oy in product((-w-1,-w,1-w,-1,0,320-w,321-w,319,320,321),
                             (-h-1,-h,1-h,-1,0,256-h,257-h,255,256,257)):
            case(ox+hx,oy+hy,hx,hy,w,h)
        case(-2**31,2**31-1,hx,hy,w,h)
        case(2**31-1,-2**31,hx,hy,w,h)
    for w,h in product((0,15,17,128,-1,16,32,64),(0,-1,257,65536,16)):
        case(0,0,0,0,w,h)
    rng=random.Random(0x52F)
    for _ in range(512):
        case(rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31),
             rng.randrange(-32768,32768),rng.randrange(-32768,32768),16,16)
    print('S2F_GEOMETRY_PASS',count,flush=True)

def planes(m):
    rng=random.Random(0x52F1);count=0
    def case(w,h,dx,dy,raw):
        nonlocal count
        n=w//8*h
        assert len(raw)==n
        m.u.mem_write(SRC-8,b'\x91'*8+raw+b'\x19'*8)
        m.u.mem_write(DST-8,b'\x72'*8+b'\xff'*n+b'\x27'*8)
        got=m.call(4,(w,h,dx,dy,n,n),D[1:]+A,(SRC,DST),n,True)
        assert got[0]==1,(w,h,dx,dy,got)
        assert bytes(m.u.mem_read(SRC-8,n+16))==b'\x91'*8+raw+b'\x19'*8
        expected=b'\x72'*8+raster(raw,w,h,dx,dy)+b'\x27'*8
        assert bytes(m.u.mem_read(DST-8,n+16))==expected,(w,h,dx,dy)
        count+=1
    for w in (16,32,64):
        for dx in range(1-w,w):
            for raw in (bytes([0xff])*(w//8),rng.randbytes(w//8)):
                case(w,1,dx,0,raw)
        for h in (2,16,256):
            for dx,dy in product((1-w,-9,-1,0,1,9,w-1),(1-h,-1,0,1,h-1)):
                if abs(dx)<w and abs(dy)<h:
                    case(w,h,dx,dy,rng.randbytes(w//8*h))
        # Distinct planes and composite-pixel equivalence at each edge.
        for depth in (2,4):
            h=16;n=w//8*h
            raw=[rng.randbytes(n) for _ in range(depth)]
            for dx,dy in ((1-w,1-h),(w-1,h-1),(-3,2),(3,-2),(0,0)):
                for plane in raw:case(w,h,dx,dy,plane)
    print('S2F_PLANES_PASS',count,flush=True)
    bad=0
    def reject(w,h,dx,dy,n,mn,src=SRC,dst=DST):
        nonlocal bad
        sentinel=b'\xa5'*2064
        m.u.mem_write(DST-8,sentinel)
        got=m.call(4,(w,h,dx,dy,n,mn),D[1:]+A,(src,dst))
        assert got[0]==0,(w,h,dx,dy,n,mn,src,dst)
        assert bytes(m.u.mem_read(DST-8,len(sentinel)))==sentinel
        bad+=1
    for w,h in product((0,15,17,128,-1,16,32,64),(0,-1,257,65536)):
        reject(w,h,0,0,32,32)
    for w in (16,32,64):
        h=16;n=w//8*h
        for dx,dy in ((-w,0),(w,0),(0,-h),(0,h),(-2**31,0),(0,2**31-1)):
            reject(w,h,dx,dy,n,n)
        for a,b in ((n-1,n),(n,n-1),(n+1,n),(n,n+1)):
            reject(w,h,0,0,a,b)
        for s,d in ((0,DST),(SRC,0),(SRC,SRC),(SRC,SRC+1),(DST+1,DST),
                    (0xffffffff-n+1,DST),(SRC,0xffffffff-n+1)):
            reject(w,h,0,0,n,n,s,d)
    print('S2F_REFUSALS_PASS',bad,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',required=True,type=Path)
    a=p.parse_args()
    code=a.binary.read_bytes()
    machine=Machine(code)
    geometry(machine);planes(machine)
    print('S2F_KERNEL_GATE_A_PASS',len(code),sha256(code).hexdigest(),flush=True)
