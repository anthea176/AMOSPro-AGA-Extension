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
from test_m19_s2d_ext_prepare_cpu import (CODE,STOP,EXEC,GFX,STACK,EXT0,EXT1,REGS,
    mock_attach39,att39_type,att39_write,assert_attach39,BAD39)

REC=0x160000
class Machine:
    def __init__(self,code,width=32,kind=4,channel=2,version=40,context=0,
                 mode='ok',state=0,negsize=1100,possize=450,memtype=3,oldwidth=None,soft=3,reserved=3):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        self.u.mem_write(4,pack('>I',EXEC))
        self.u.mem_write(GFX+16,pack('>HHH',negsize,possize,version))
        self.u.mem_write(GFX+237,bytes([memtype]))
        self.u.mem_write(GFX+444,pack('>H',(oldwidth if oldwidth is not None else (context or 16)//16)))
        self.u.mem_write(GFX+448,bytes([soft]))
        for a in (EXEC-534,GFX-390,GFX-1020,GFX-1032,GFX-930):
            self.u.mem_write(a,b'\x4e\x75')
        self.width,self.kind,self.channel=width,kind,channel
        self.mode=mode;self.version=version
        self.receipt=pack('>9I',GFX,EXT0,EXT1,width&0xffffffff,kind&0xffffffff,
                          channel&0xffffffff,state&0xffffffff,context&0xffffffff,0)
        self.u.mem_write(REC,self.receipt)
        for p in (EXT0,EXT1):
            self.u.mem_write(p,bytes(10)+b'\xff\xff'+b'\xa5'*52)
        self.events=[]
        self.live=set()
        self.got=set()
        self.reserved={i for i in range(8) if reserved & (1<<i)}
        self.sync_reserved()
        self.allocs=self.gets=0
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def sync_reserved(self):
        self.u.mem_write(GFX+166,bytes([sum(1<<i for i in self.reserved)]))
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def reg(self,r):return self.u.reg_read(r)
    def get(self,a):return unpack_from('>I',self.read(a,4))[0]
    def state(self):return self.get(REC+24)
    def volatile(self,result):
        for r,v in ((UC_M68K_REG_D0,result&0xffffffff),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            self.u.reg_write(r,v)
    def on_write(self,u,access,a,n,value,user):
        if (STACK-4096<=a and a+n<=STACK+4) or (REC+24<=a and a+n<=REC+28):return
        assert att39_write(self,a,n,value),('forbidden write',hex(a),n)
    def on_code(self,u,a,size,user):
        if a==EXEC-534:
            flag=att39_type(self,self.reg(UC_M68K_REG_A1))
            self.volatile(flag or 0);return
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
                self.live.add(p)
                if attached and self.version==39:mock_attach39(self,self.width,1)
                self.volatile(p)
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
            # Archived V40 GetExtSpriteA rejects GSTAG_ATTACHED. Require
            # exactly one explicit channel per call, including attached.
            assert unpack_from('>6I',self.read(tag,24))==(0x82000020,c,0,0,0,0)
            assert self.state()==(5 if second else 4)
            self.gets+=1
            self.events.append('GetOdd' if second else 'GetEven')
            if self.mode==('getfail2' if second else 'getfail1'):
                self.volatile(-1);return
            if c in self.reserved:
                self.volatile(-1);return
            if self.mode==('wrong2' if second else 'wrong1'):
                self.volatile(0);return
            self.reserved.add(c);self.got.add(c)
            self.sync_reserved()
            u.mem_write(GFX+444,pack('>H',self.width//16))
            u.mem_write(p+10,pack('>H',c if self.mode!='badnum1' or second else 0))
            if second and self.mode=='badnum2':
                u.mem_write(EXT1+10,bytes(2))
            if self.mode==('badwidth2' if second else 'badwidth1'):
                u.mem_write(GFX+444,pack('>H',0))
            if self.mode==('badmask2' if second else 'badmask1'):
                self.reserved.remove(c);self.sync_reserved()
            if not second and self.mode=='foreign_odd':
                self.reserved.add(c+1);self.sync_reserved()
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
        if hasattr(self,'att39_raw'):assert_attach39(self)
        # Guard never writes GfxBase; mutations occur only in our OS hook.
        assert self.read(GFX+166,1)==bytes([sum(1<<i for i in self.reserved)])
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes()
    n=0
    for w in (16,32,64):
        for k in (2,4):
            for v in (39,40,46):
                m=Machine(code,w,k,version=v)
                assert m.invoke(0)==(EXT0,EXT1)
                assert m.live=={EXT0,EXT1} and m.events==['Init','AllocEven','AllocOdd'] and m.state()==0
                n+=1
                if v>40:
                    m=Machine(code,w,k,version=v)
                    assert m.invoke(4)==(0,1) and not m.events and m.state()==0
                    n+=1
                    continue
                for ch in (2,4,6):
                    for ctx in (0,w):
                        m=Machine(code,w,k,channel=ch,version=v,context=ctx)
                        assert m.invoke(4)==(1,0) and m.state()==7 and m.got=={ch,ch+1}
                        assert m.events==['GetEven','GetOdd']
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
                                  ('badnum1',0x80000005,3),
                                  ('badnum2',0x80000007,3),
                                  ('badwidth1',0x80000005,3),('badwidth2',0x80000007,3),
                                  ('badmask1',0x80000005,3),('badmask2',0x80000007,3)):
                m=Machine(code,w,k,mode=mode)
                assert m.invoke(4)==(0,rc) and m.state()==flags,(w,k,mode,m.state())
                assert 'FreeDetached' not in m.events;n+=1
            for mode,flags,rc in (('getfail2',5,2),('wrong2',0x80000005,3)):
                m=Machine(code,w,k,mode=mode)
                assert m.invoke(4)==(0,rc) and m.state()==flags and m.got=={2}
                n+=1
            m=Machine(code,w,k,reserved=11)
            assert m.invoke(4)==(0,1) and m.state()==0 and not m.events and 3 in m.reserved
            n+=1
            m=Machine(code,w,k,mode='foreign_odd')
            assert m.invoke(4)==(0,2) and m.state()==5 and m.got=={2} and 3 in m.reserved
            assert m.events==['GetEven'];n+=1
    for w in (16,32,64):
        for mode in BAD39:
            m=Machine(code,w,4,version=39,mode=mode)
            assert m.invoke(0)==(0,0) and not m.live
            assert m.events==['Init','AllocEven','AllocOdd','FreeDetached','FreeDetached'];n+=1
    for opts in ({'width':0},{'width':17},{'width':48},{'width':128},{'kind':3},
                 {'version':38},{'negsize':1030}):
        m=Machine(code,**opts)
        assert m.invoke(0)==(0,0) and not m.events
        assert m.invoke(4)==(0,1) and not m.events and m.state()==0
        n+=2
    for opts in ({'context':16},{'channel':0},{'channel':3},{'channel':8},
                 {'state':4},{'state':0x80000004}):
        m=Machine(code,**opts);state=m.state()
        assert m.invoke(4)==(0,1) and m.state()==state and not m.events
        n+=1
    # Source-derived bandwidth and global width arbitration.
    for width in (16,32,64):
        for bw in range(4):
            for old in (1,2,4):
                for reserved,soft in ((3,3),(19,3),(0,0)):
                    m=Machine(code,width=width,kind=2,memtype=bw,oldwidth=old,
                              reserved=reserved,soft=soft)
                    supported=width==16 or (width==32 and bw!=0) or (width==64 and bw==3)
                    expect=supported and (old==width//16 or reserved==soft)
                    assert m.invoke(4)==((1,0) if expect else (0,1)),(width,bw,old,reserved,soft)
                    assert m.state()==(7 if expect else 0)
                    if not expect:assert not m.events
                    n+=1
    for opts in ({'possize':449},{'oldwidth':0},{'oldwidth':3},{'oldwidth':5},
                 {'memtype':4},{'context':32,'oldwidth':1}):
        m=Machine(code,**opts)
        assert m.invoke(4)==(0,1) and m.state()==0 and not m.events
        n+=1
    for off,value in ((4,0),(8,0),(8,EXT0),(4,EXT0+1),(8,EXT1+1),(32,1)):
        m=Machine(code);b=bytearray(m.receipt)
        b[off:off+4]=pack('>I',value);m.receipt=bytes(b);m.u.mem_write(REC,m.receipt)
        assert m.invoke(4)==(0,1) and m.state()==0 and not m.events;n+=1
    print('S2D_P2B_BLANK_RECEIPTS_CPU_PASS',n,sha256(code).hexdigest(),flush=True)
if __name__=='__main__':main()
