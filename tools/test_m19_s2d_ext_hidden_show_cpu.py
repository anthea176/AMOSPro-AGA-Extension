#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2c1 first show on modeled V40 OS, not real graphics/DMA."""
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from test_m19_s2d_ext_prepare_cpu import CODE,STOP,EXEC,GFX,STACK,REGS

REC,VIEW,VP,CM,CI,TAB=0x100000,0x101000,0x102000,0x103000,0x104000,0x105000
B0,B1,F0,F1=0x110000,0x111000,0x112000,0x113000
P0,P1,P2,P3=0x120000,0x124000,0x128000,0x12c000
NEUTRAL=CI+176

class Machine:
    def __init__(self,code,w=32,k=4,h=17,ch=2,version=40,mode='ok'):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x200000)
        self.u.mem_write(CODE,code)
        self.put(4,EXEC)
        self.u.mem_write(GFX+16,pack('>HHH',1100,450,version))
        self.put(GFX+34,VIEW);self.put(GFX+38,CI);self.put(GFX+208,TAB)
        self.u.mem_write(GFX+166,bytes([(3<<ch)|3]))
        self.u.mem_write(GFX+444,pack('>H',w//16))
        self.put(VIEW,VP);self.put(VP+4,CM)
        self.u.mem_write(VP+24,pack('>HH',320,256))
        self.u.mem_write(VP+32,pack('>H',0x5000))
        self.w,self.k,self.h,self.ch,self.mode=w,k,h,ch,mode
        self.u.mem_write(REC,pack('>18I',GFX,B0,B1,w,k,ch,7,0,0,VP,VIEW,CI,TAB,F0,F1 if k==4 else 0,h,CM,0))
        self.descs={B0:(P0,1,False,ch),B1:(P1,1,k==4,ch+1),
                    F0:(P2,h,False,0xbeef),F1:(P3,h,k==4,0xbeef)}
        for a,(p,ht,att,num) in self.descs.items():
            self.u.mem_write(a,pack('>IHHHH',p,ht,0xdead,0xbeef,num))
            data=bytearray((ht+2)*w//4)
            if att:
                data[3]=0x80;data[w//8+1]=0x80
            self.u.mem_write(p,bytes(data))
        for n in range(8):
            self.u.mem_write(CI+88+8*n,pack('>HHHH',0x120+4*n,NEUTRAL>>16,0x122+4*n,NEUTRAL&65535))
        self.put(TAB,0x150000);self.put(TAB+4,0x150100)
        for a in (EXEC-534,GFX-426,GFX-1026):
            self.u.mem_write(a,b'\x4e\x75')
        self.events=[]
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def get(self,a):return unpack_from('>I',self.read(a,4))[0]
    def word(self,a):return unpack_from('>H',self.read(a,2))[0]
    def put(self,a,v):self.u.mem_write(a,pack('>I',v))
    def reg(self,r):return self.u.reg_read(r)
    def state(self):return self.get(REC+24)
    def copper(self,c):
        a=CI+88+8*c
        return self.word(a+2)*65536+self.word(a+6)
    def copper_set(self,c,p):
        a=CI+88+8*c
        self.u.mem_write(a+2,pack('>H',p>>16))
        self.u.mem_write(a+6,pack('>H',p&65535))
    def on_write(self,u,access,a,n,value,user):
        assert STACK-4096<=a and a+n<=STACK+4 or (REC+24<=a and a+n<=REC+28),('native write outside receipt/stack',hex(a),n)
    def volatile(self,result=0):
        for r,v in ((UC_M68K_REG_D0,result),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            self.u.reg_write(r,v)
    def model_move(self,ptr,x,y):
        n=self.word(ptr+10)
        assert n in (self.ch,self.ch+1)
        self.u.mem_write(ptr+6,pack('>HH',x,y))
        self.put(TAB+4*n,ptr)
        if n==self.ch:
            odd=self.get(TAB+4*(n+1))
            if odd and self.read(self.get(odd)+3,1)[0]&128:
                self.model_move(odd,x,y)
        self.copper_set(n,NEUTRAL if y>256 else self.get(ptr))
    def on_code(self,u,a,size,user):
        if a==EXEC-534:
            p=self.reg(UC_M68K_REG_A1)
            chip=CI<=p<CI+192 or any(base<=p<base+(ht+2)*self.w//4 for base,ht,_,_ in self.descs.values())
            self.volatile(2 if chip and self.mode!='no_chip' else 1 if 0x80000<=p<0x200000 else 0)
            return
        if a not in (GFX-426,GFX-1026):return
        assert self.state()==15
        assert self.reg(UC_M68K_REG_A0)==VP
        old=self.reg(UC_M68K_REG_A1)
        assert old in self.descs
        if a==GFX-426:
            x,y=self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)
            self.events.append(('Move',old,x,y))
            self.model_move(old,x,y)
            result=0
        else:
            new=self.reg(UC_M68K_REG_A2)
            assert (old,new) in ((B0,F0),(B1,F1))
            assert self.read(self.reg(UC_M68K_REG_A3),8)==bytes(8)
            assert self.word(old+6)==0 and self.word(old+8)==257
            assert self.copper(self.ch)==self.copper(self.ch+1)==NEUTRAL
            self.events.append(('Change',old,new))
            if self.mode=='fail_change':
                self.volatile(0);return
            self.u.mem_write(new+10,pack('>H',self.word(old+10)))
            self.model_move(new,0,257)
            result=0xffffffff
        if self.mode=='bad_width_after' and len(self.events)==1:
            self.u.mem_write(GFX+444,pack('>H',1 if self.w!=16 else 4))
        if self.mode=='bad_slot_after' and len(self.events)==1:
            self.put(TAB+4*(self.ch+1),0x151000)
        if self.mode=='visible_early' and len(self.events)==1:
            self.copper_set(self.ch+1,P1)
        self.volatile(result)
    def invoke(self,x=1,y=2):
        u=self.u;u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(REGS):u.reg_write(r,0x55000000+i)
        u.reg_write(UC_M68K_REG_A0,REC);u.reg_write(UC_M68K_REG_A6,GFX)
        saved={r:self.reg(r) for r in REGS}
        u.reg_write(UC_M68K_REG_D0,x&0xffffffff)
        u.reg_write(UC_M68K_REG_D1,y&0xffffffff)
        u.reg_write(UC_M68K_REG_A7,STACK)
        self.put(STACK,STOP)
        before=self.read(REC,72)
        peers=[(i,self.get(TAB+4*i),self.copper(i)) for i in range(8) if i not in (self.ch,self.ch+1)]
        u.emu_start(CODE,STOP,count=200000)
        assert self.reg(UC_M68K_REG_PC)==STOP and self.reg(UC_M68K_REG_A7)==STACK+4
        assert all(self.reg(r)==v for r,v in saved.items())
        assert self.read(REC,24)==before[:24] and self.read(REC+28,44)==before[28:]
        assert all(self.get(TAB+4*i)==p and self.copper(i)==c for i,p,c in peers)
        return self.reg(UC_M68K_REG_D0),self.reg(UC_M68K_REG_D1)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('native',type=Path)
    code=p.parse_args().native.read_bytes();n=0
    for w in (16,32,64):
        for k in (2,4):
            for h in (1,17,256):
                for ch in (2,4,6):
                    for v in (39,40):
                        for x,y in ((0,0),(320-w,256-h)):
                            m=Machine(code,w,k,h,ch,v)
                            assert m.invoke(x,y)==(1,0) and m.state()==31,(w,k,h,ch,v,m.events)
                            expect=[('Move',B1,0,257),('Move',B0,0,257)]
                            if k==4:expect.append(('Change',B1,F1))
                            expect += [('Change',B0,F0),('Move',F0,x,y)]
                            assert m.events==expect
                            assert m.copper(ch)==P2
                            assert m.copper(ch+1)==(P3 if k==4 else NEUTRAL)
                            before=list(m.events)
                            assert m.invoke(x,y)==(0,1) and m.events==before and m.state()==31
                            n+=1
    for w in (16,32,64):
        for k in (2,4):
            for mode in ('bad_width_after','bad_slot_after','visible_early','fail_change'):
                m=Machine(code,w,k,mode=mode)
                assert m.invoke()==(0,2) and m.state()==15,(w,k,mode,m.events)
                assert len(m.events)==(3 if mode=='fail_change' else 1)
                n+=1
            for x,y in ((-1,0),(0,-1),(321-w,0),(0,240)):
                m=Machine(code,w,k)
                assert m.invoke(x,y)==(0,1) and m.state()==7 and not m.events
                n+=1
    for off,val in ((0,0),(4,0),(8,B0),(12,48),(16,3),(20,1),(24,5),(32,1),(36,0),
                    (40,0),(44,0),(48,0),(52,B1),(56,F0),(60,0),(64,0),(68,1)):
        m=Machine(code);m.put(REC+off,val)
        assert m.invoke()==(0,1) and not m.events,(off,val)
        n+=1
    for addr,val,size in ((GFX+18,449,2),(GFX+444,1,2),(GFX+166,3,1),
                          (VP+24,640,2),(VP+26,200,2),(VP+32,0,2),(VP+12,1,4),
                          (B0+4,2,2),(B1+10,0,2),(F0+4,1,2),(P3+3,0,1),
                          (P3+5,0,1),(CI+88+8*2,0,2),(TAB+8,F0,4)):
        m=Machine(code);m.u.mem_write(addr,val.to_bytes(size,'big'))
        assert m.invoke()==(0,1) and m.state()==7 and not m.events,(addr,val)
        n+=1
    for opts in ({'version':38},{'version':46},{'mode':'no_chip'}):
        m=Machine(code,**opts)
        assert m.invoke()==(0,1) and m.state()==7 and not m.events
        n+=1
    print('S2D_P2C1_HIDDEN_SHOW_CPU_PASS',n,sha256(code).hexdigest(),flush=True)
if __name__=='__main__':main()
