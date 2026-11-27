#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2c-P0b detached pair allocation on real MC68020 instructions.
Independent row/palette oracle, exact allocation and ABI guards.
No display, channel, Copper, real OS or WinUAE qualification.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from m19_s1_agsp_bank import parse_abk, parse_payload, empty_bank, put_capture, set_hotspot

ROOT=Path(__file__).resolve().parents[1]
CODE,STOP,EXEC,STACK,SOURCE,CHIP=0x20000,0x30000,0x80000,0xb0000,0x100000,0x140000
REGS=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
      UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
      UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)


class Machine:
    def __init__(self,code,payload,mode='ok'):
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0,0x200000)
        self.uc.mem_write(CODE,code)
        self.uc.mem_write(4,pack('>I',EXEC))
        for lvo in (534,684,690):
            self.uc.mem_write(EXEC-lvo,b'\x4e\x75')
        self.uc.mem_write(SOURCE,payload or bytes(1))
        self.uc.mem_write(CHIP-16,b'\x5a'*4352)
        self.payload=payload
        self.mode=mode
        self.live=0
        self.allocs=0
        self.frees=0
        self.polls=[]
        self.uc.hook_add(UC_HOOK_CODE,self.on_code)
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):
        return bytes(self.uc.mem_read(a,n))
    def on_write(self,uc,access,a,n,value,user):
        if STACK-4096<=a and a+n<=STACK+4:return
        assert self.live and CHIP<=a and a+n<=CHIP+self.live,('unexpected write',hex(a),n)
    def volatile(self,result):
        self.uc.reg_write(UC_M68K_REG_D0,result)
        self.uc.reg_write(UC_M68K_REG_D1,0xdead0001)
        self.uc.reg_write(UC_M68K_REG_A0,0xdead0002)
        self.uc.reg_write(UC_M68K_REG_A1,0xdead0003)
    def on_code(self,uc,addr,size,user):
        if addr==EXEC-534:
            p=uc.reg_read(UC_M68K_REG_A1)
            self.polls.append(p)
            if SOURCE<=p<SOURCE+len(self.payload):
                flags=1 if self.mode!='source_end_bad' or p==SOURCE else 0
            elif self.live and CHIP<=p<CHIP+self.live:
                flags=1 if self.mode=='fast' or (self.mode=='chip_end_bad' and p!=CHIP) else 3
            else:flags=0
            self.volatile(flags)
        elif addr==EXEC-684:
            n=uc.reg_read(UC_M68K_REG_D0)
            assert uc.reg_read(UC_M68K_REG_D1)==0x10003
            assert 144<=n<=4224 and not self.live
            self.allocs+=1
            if self.mode=='oom':
                self.volatile(0)
            else:
                self.live=n
                self.uc.mem_write(CHIP,bytes(n))
                self.volatile(CHIP)
        elif addr==EXEC-690:
            assert self.live and uc.reg_read(UC_M68K_REG_A1)==CHIP
            self.live=0
            self.frees+=1
            self.volatile(0)
    def invoke(self,ident,pointer=SOURCE,length=None):
        u=self.uc
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55001000+i)
        u.reg_write(UC_M68K_REG_A0,pointer)
        saved={r:u.reg_read(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,len(self.payload) if length is None else length)
        u.reg_write(UC_M68K_REG_D1,ident)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE,STOP,count=20_000_000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items()),'preserved registers'
        assert self.read(SOURCE,len(self.payload))==self.payload
        assert self.read(CHIP-16,16)==b'\x5a'*16
        if self.live:assert self.read(CHIP+self.live,16)==b'\x5a'*16
        return u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1)

def expected(payload,ident):
    bank=parse_payload(payload)
    im=bank.image(ident)
    assert im.width==16 and im.depth==4 and 4<=im.opaque_count<=15
    # Independent pixel-by-pixel reconstruction, not a copy of the
    # native plane-major transposition algorithm.
    even=bytearray(4)
    odd=bytearray(4)
    for y in range(im.height):
        words=[sum(((im.index(x,y)>>bit)&1)<<(15-x) for x in range(16))
               for bit in range(4)]
        even.extend(pack('>HH',*words[:2]))
        odd.extend(pack('>HH',*words[2:]))
    even.extend(bytes(4))
    odd.extend(bytes(4))
    stream=8+4*im.height
    total=96+4*stream
    desc=pack('>I4H',0,im.height,0,0,65535)
    head=desc*2+pack('>I2HI2h48s2I',total,ident,im.opaque_count,
                    bank.generation,im.hotspot_x,im.hotspot_y,
                    im.palette,stream,96)
    assert len(head)==96 and len(even)==len(odd)==stream
    return head+even+odd+bytes(2*stream)

def check(code,payload,ident):
    m=Machine(code,payload)
    result=m.invoke(ident)
    want=expected(payload,ident)
    assert result==(CHIP,len(want)) and m.live==len(want)
    assert m.allocs==1 and m.frees==0
    assert m.read(CHIP,len(want))==want
    # Detached result owns all bytes; erasing source cannot change it.
    m.uc.mem_write(SOURCE,bytes(len(payload)))
    assert m.read(CHIP,len(want))==want

def reject(code,payload,ident,mode='ok',pointer=SOURCE,length=None,allocs=0,frees=0):
    m=Machine(code,payload,mode)
    assert m.invoke(ident,pointer,length)==(0,0)
    assert not m.live and (m.allocs,m.frees)==(allocs,frees)
    assert m.read(CHIP,16)==b'\x5a'*16 or frees==1

def make(height,width=16,mode='s1',colors=3):
    pixels=bytes((x+y)%(colors+1) for y in range(height) for x in range(width))
    cmap=bytes(3)+b''.join(bytes((i*13,i*7,i*3)) for i in range(1,16))
    return put_capture(empty_bank(),4096,pixels,width,height,0,0,width,height,cmap,0,mode=mode)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('native',type=Path)
    args=ap.parse_args()
    code=args.native.read_bytes()
    cases=0
    for height in (1,16,255,256):
        for colors in range(4,16):
            check(code,make(height,mode='s2',colors=colors),4096)
            cases+=1
    base=make(16,mode='s2',colors=15)
    check(code,set_hotspot(base,4096,-8,7),4096);cases+=1
    # Mixed-depth, sorted IDs and arbitrary RGB24 including opaque black.
    pal=bytes(3)+bytes(3)+b''.join(bytes((i*13,i*7,i*3)) for i in range(2,16))
    mixed=put_capture(base,1,bytes([0,1,2,3]*4),16,1,0,0,16,1,pal,0)
    mixed=put_capture(mixed,8,bytes(range(16))*3,16,3,0,0,16,3,pal,0,mode='s2')
    check(code,mixed,4096);check(code,mixed,8);cases+=2
    # Existing S1 assets remain owned by the old single-stream path.
    for p,ident in ((empty_bank(),1),(base,1),(base,0),(base,4097),
                    (make(16,32,'s2',15),4096),(make(16,64,'s2',15),4096),
                    (make(16),4096),(mixed,1)):
        reject(code,p,ident);cases+=1
    for off,val in ((0,0),(5,2),(10,1),(20,0),(24,0),(28,1),(32+10,1),
                    (32+12,0),(32+6,1)):
        bad=bytearray(base);bad[off]=val
        if bytes(bad)==base:continue
        reject(code,bytes(bad),4096);cases+=1
    reject(code,base,4096,pointer=0);cases+=1
    reject(code,base,4096,pointer=SOURCE+1);cases+=1
    reject(code,base,4096,pointer=0xfffffff0);cases+=1
    reject(code,base,4096,length=30);cases+=1
    reject(code,base,4096,length=len(base)-2);cases+=1
    reject(code,base,4096,mode='source_end_bad');cases+=1
    reject(code,base,4096,mode='oom',allocs=1);cases+=1
    reject(code,base,4096,mode='fast',allocs=1,frees=1);cases+=1
    reject(code,base,4096,mode='chip_end_bad',allocs=1,frees=1);cases+=1
    print('S2C_DETACHED_CHIP_PAIR_PASS',cases,sha256(code).hexdigest(),flush=True)

if __name__=='__main__':
    main()
