#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2d-P2b blank allocation and GetExtSpriteA receipt ABI models.
No proof of real OS side effects, ownership after external mutation or DMA.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from test_m19_s2d_ext_prepare_cpu import CODE,STOP,GFX,STACK,EXT0,EXT1,REGS

REC=0x160000
class Machine:
    def __init__(self,code,width=32,kind=4,channel=2,version=40,context=0,
                 mode='ok',state=0,negsize=1100):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        self.u.mem_write(GFX+16,pack('>HHH',negsize,34,version))
        for a in (GFX-390,GFX-1020,GFX-1032,GFX-930):
            self.u.mem_write(a,b'\x4e\x75')
        self.width,self.kind,self.channel=width,kind,channel
        self.mode=mode
        self.receipt=pack('>9I',GFX,EXT0,EXT1,width&0xffffffff,kind&0xffffffff,
                          channel&0xffffffff,state&0xffffffff,context&0xffffffff,0)
        self.u.mem_write(REC,self.receipt)
        for p in (EXT0,EXT1):
            self.u.mem_write(p,bytes(10)+b'\xff\xff'+b'\xa5'*52)
        self.events=[]
        self.live=set()
        self.got=set()
        self.reserved={0,1}
        self.allocs=self.gets=0
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def reg(self,r):return self.u.reg_read(r)
    def get(self,a):return unpack_from('>I',self.read(a,4))[0]
    def state(self):return self.get(REC+24)
    def volatile(self,result):
        for r,v in ((UC_M68K_REG_D0,result&0xffffffff),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            self.u.reg_write(r,v)
    def on_write(self,u,access,a,n,value,user):
        assert (STACK-4096<=a and a+n<=STACK+4) or (REC+24<=a and a+n<=REC+28),('forbidden write',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==GFX-390:
            assert tuple(self.reg(r) for r in (UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2))==(self.kind,self.width,1)
            self.bm=self.reg(UC_M68K_REG_A0)
            assert STACK-4096<=self.bm<=STACK-96
            stride=self.width//8+(2 if self.mode=='stride' else 0)
            u.mem_write(self.bm,pack('>HHBBH',stride,1,0,self.kind,0))
            self.events.append('Init')
            self.volatile(0)
        elif a==GFX-1020:
            assert self.reg(UC_M68K_REG_A2)==self.bm
            tag=self.reg(UC_M68K_REG_A1)
            second=self.allocs==1
            attached=second and self.kind==4
            assert unpack_from('>6I',self.read(tag,24))==(
                (0x81000000,self.width,0x81000008,1,0,0) if attached
                else (0x81000000,self.width,0,0,0,0))
            stride,rows,flags,depth,pad,*ptrs=unpack_from('>HHBBH8I',self.read(self.bm,40))
            assert (stride,rows,depth)==(self.width//8,1,self.kind)
            for i,p in enumerate(ptrs[:depth]):
                assert p==self.bm+64+i*stride and self.read(p,stride)==bytes(stride)
            assert not any(ptrs[depth:])
            self.allocs+=1
            self.events.append('AllocOdd' if second else 'AllocEven')
            if self.mode==('oom2' if second else 'oom1'):
                self.volatile(0)
            else:
                p=EXT1 if second else EXT0
                self.live.add(p);self.volatile(p)
        elif a==GFX-1032:
            p=self.reg(UC_M68K_REG_A2)
            assert p in self.live and not self.got
            self.live.remove(p);self.events.append('FreeDetached');self.volatile(0)
        elif a==GFX-930:
            tag=self.reg(UC_M68K_REG_A1)
            p=self.reg(UC_M68K_REG_A2)
            second=self.gets==1
            c=self.channel+int(second)
            assert p==(EXT1 if second else EXT0)
            pair=self.kind==4
            assert not (pair and second)
            assert unpack_from('>6I',self.read(tag,24))==(
                (0x82000020,c,0x82000022,EXT1,0,0) if pair
                else (0x82000020,c,0,0,0,0))
            assert self.state()==(5 if second else 4)
            self.gets+=1
            self.events.append('GetPair' if pair else 'GetOdd' if second else 'GetEven')
            if self.mode==('getfail2' if second else 'getfail1'):
                self.volatile(-1);return
            if c in self.reserved or pair and c+1 in self.reserved:
                self.volatile(-1);return
            if self.mode==('wrong2' if second else 'wrong1'):
                self.volatile(0);return
            self.reserved.add(c);self.got.add(c)
            u.mem_write(p+10,pack('>H',c if self.mode!='badnum1' or second else 0))
            if pair:
                self.reserved.add(c+1);self.got.add(c+1)
                u.mem_write(EXT1+10,pack('>H',c+1 if self.mode!='badnum2' else 0))
            elif second and self.mode=='badnum2':
                u.mem_write(EXT1+10,bytes(2))
            self.volatile(c)
    def invoke(self,entry,gfx=GFX,rec=REC):
        u=self.u;u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,rec)
        u.reg_write(UC_M68K_REG_A6,gfx)
        saved={r:self.reg(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,self.width&0xffffffff)
        u.reg_write(UC_M68K_REG_D1,self.kind&0xffffffff)
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(CODE+entry,STOP,count=100000)
        assert self.reg(UC_M68K_REG_PC)==STOP and self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items())
        assert self.read(REC,24)==self.receipt[:24] and self.read(REC+28,8)==self.receipt[28:]
        assert self.read(EXT0+12,52)==self.read(EXT1+12,52)==b'\xa5'*52
        assert {0,1}<=self.reserved
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    n=0
    for w in (16,32,64):
        for k in (2,4):
            for v in ((39,40,46) if k==2 else (40,46)):
                m=Machine(code,w,k,version=v)
                assert m.invoke(0)==(EXT0,EXT1)
                assert m.live=={EXT0,EXT1} and m.events==['Init','AllocEven','AllocOdd'] and m.state()==0
                n+=1
                for ch in (2,4,6):
                    for ctx in (0,w):
                        m=Machine(code,w,k,channel=ch,version=v,context=ctx)
                        assert m.invoke(4)==(1,0) and m.state()==7 and m.got=={ch,ch+1}
                        assert m.events==(['GetPair'] if k==4 else ['GetEven','GetOdd'])
                        before=list(m.events)
                        assert m.invoke(4)==(0,1) and m.state()==7 and m.events==before
                        n+=1
            for mode,events in (('oom1',['Init','AllocEven']),
                                ('oom2',['Init','AllocEven','AllocOdd','FreeDetached']),
                                ('stride',['Init'])):
                m=Machine(code,w,k,mode=mode)
                assert m.invoke(0)==(0,0) and not m.live and m.events==events
                n+=1
            for mode,flags,rc in (('getfail1',4,2),('wrong1',0x80000004,3),
                                  ('badnum1',0x80000007 if k==4 else 0x80000005,3),
                                  ('badnum2',0x80000007,3)):
                m=Machine(code,w,k,mode=mode)
                assert m.invoke(4)==(0,rc) and m.state()==flags,(w,k,mode,m.state())
                assert 'FreeDetached' not in m.events;n+=1
            if k==2:
                for mode,flags,rc in (('getfail2',5,2),('wrong2',0x80000005,3)):
                    m=Machine(code,w,k,mode=mode)
                    assert m.invoke(4)==(0,rc) and m.state()==flags and m.got=={2}
                    n+=1
                m=Machine(code,w,k);m.reserved.add(3)
                assert m.invoke(4)==(0,2) and m.state()==5 and m.got=={2} and 3 in m.reserved
                n+=1
            else:
                m=Machine(code,w,k);m.reserved.add(3)
                assert m.invoke(4)==(0,2) and m.state()==4 and not m.got and 3 in m.reserved
                n+=1
    for opts in ({'width':0},{'width':17},{'width':48},{'width':128},{'kind':3},
                 {'kind':4,'version':39},{'version':38},{'negsize':1030}):
        m=Machine(code,**opts)
        assert m.invoke(0)==(0,0) and not m.events
        assert m.invoke(4)==(0,1) and not m.events and m.state()==0
        n+=2
    for opts in ({'context':16},{'channel':0},{'channel':3},{'channel':8},
                 {'state':4},{'state':0x80000004}):
        m=Machine(code,**opts);state=m.state()
        assert m.invoke(4)==(0,1) and m.state()==state and not m.events
        n+=1
    for off,value in ((4,0),(8,0),(8,EXT0),(4,EXT0+1),(8,EXT1+1),(32,1)):
        m=Machine(code);b=bytearray(m.receipt)
        b[off:off+4]=pack('>I',value);m.receipt=bytes(b);m.u.mem_write(REC,m.receipt)
        assert m.invoke(4)==(0,1) and m.state()==0 and not m.events;n+=1
    print('S2D_P2B_BLANK_RECEIPTS_CPU_PASS',n,sha256(code).hexdigest(),flush=True)
if __name__=='__main__':main()
