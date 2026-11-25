#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Execute P2h MC68020 root registry with explicit mocked Exec semantics.
No OS, DMA, AMOS Runtime or Compiler qualification claimed.
"""
from pathlib import Path
from struct import pack,unpack
from hashlib import sha256
import argparse
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

CODE,CODE2,STOP,EXEC,STACK=0x20000,0x28000,0x30000,0x80000,0xa0000
TASK1,TASK2=0x90000,0x91000
NAME=b'AMOSPro.AGA.AGSP.S1.root.v1\0'
SIZE=112
PRESERVED=(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
           UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,
           UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6)

class Machine:
    def __init__(self,code):
        self.u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.u.mem_map(0,0x400000)
        self.code=code
        self.code_addr=CODE
        self.u.mem_write(CODE,code)
        self.u.mem_write(CODE2,code)
        self.w32(4,EXEC)
        self.w16(EXEC+16,702)
        self.w16(EXEC+20,40)
        for n in (132,138,294,534,570,576,594,600,606,684,690):
            self.u.mem_write(EXEC-n,b'\x4e\x75')
        self.depth=0
        self.task=TASK1
        self.named=0
        self.pool=set()
        self.next_addr=0x100000
        self.allocs=self.frees=0
        self.events=[]
        self.oom=False
        self.race=False
        self.u.hook_add(UC_HOOK_CODE,self.on_code)
        self.u.hook_add(UC_HOOK_MEM_WRITE,self.on_write)
    def read(self,a,n):return bytes(self.u.mem_read(a,n))
    def r32(self,a):return unpack('>I',self.read(a,4))[0]
    def r16(self,a):return unpack('>H',self.read(a,2))[0]
    def w32(self,a,v):self.u.mem_write(a,pack('>I',v))
    def w16(self,a,v):self.u.mem_write(a,pack('>H',v&65535))
    def w8(self,a,v):self.u.mem_write(a,bytes([v]))
    def allocation(self):
        p=self.next_addr
        self.next_addr+=0x100
        assert self.next_addr<0x400000
        self.pool.add(p)
        self.allocs+=1
        self.u.mem_write(p-16,b'\x5a'*16)
        self.u.mem_write(p,bytes(SIZE))
        self.u.mem_write(p+SIZE,b'\x5a'*16)
        return p
    def init_named(self,p):
        assert p in self.pool
        assert self.r32(p+10)==p+76 and self.read(p+76,len(NAME))==NAME
        self.w8(p+8,15)
        self.w16(p+14,0)
        self.w32(p+40,0)
        self.w16(p+44,-1)
        self.named=p
    def other_root(self):
        p=self.allocation()
        self.w32(p+10,p+76)
        self.w32(p+48,0x41475350)
        self.w32(p+52,0x00010070)
        self.u.mem_write(p+76,NAME)
        self.init_named(p)
        self.u.mem_write(p+56,pack('>4I',0x350000,0x351000,0x352000,0))
        return p
    def on_write(self,uc,access,a,n,value,user):
        if STACK-4096<=a and a+n<=STACK+4:return
        assert any(p<=a and a+n<=p+SIZE for p in self.pool),('unexpected CPU write',hex(a),n)
        assert any((p+10<=a and a+n<=p+14) or (p+48<=a and a+n<=p+SIZE)
                   for p in self.pool),('CPU wrote OS semaphore internals',hex(a))
    def on_code(self,uc,addr,size,user):
        n=EXEC-addr
        a0=uc.reg_read(UC_M68K_REG_A0)
        a1=uc.reg_read(UC_M68K_REG_A1)
        d0=uc.reg_read(UC_M68K_REG_D0)
        d1=uc.reg_read(UC_M68K_REG_D1)
        result=0xdead0000
        if n==132:
            self.depth+=1;assert self.depth==1
            self.events.append('forbid')
        elif n==138:
            assert self.depth==1;self.depth=0
            self.events.append('permit')
        elif n==294:
            assert a1==0 and self.depth==0
            result=self.task
        elif n==594:
            assert self.depth==1 and self.read(a1,len(NAME))==NAME
            self.events.append('find')
            result=self.named
        elif n==534:
            assert self.depth==1
            result=int(any(p<=a1<p+SIZE for p in self.pool))
        elif n==684:
            assert self.depth==0 and d0==SIZE and d1==0x10001
            self.events.append('alloc')
            if self.race:
                assert not self.named
                self.other_root();self.race=False
            result=0 if self.oom else self.allocation()
        elif n==600:
            assert self.depth==1 and not self.named
            self.events.append('add')
            self.init_named(a1)
        elif n==576:
            assert self.depth==1 and a0==self.named and a0 in self.pool
            self.events.append('attempt')
            owner=self.r32(a0+40)
            result=int(owner in (0,self.task))
            if result:
                self.w32(a0+40,self.task)
                self.w16(a0+14,self.r16(a0+14)+1)
                self.w16(a0+44,(self.r16(a0+44)+1)&65535)
        elif n==606:
            assert self.depth==1 and a1==self.named
            assert self.r32(a1+40)==self.task and self.r16(a1+14)==1
            assert self.r16(a1+44)==0 and self.read(a1+56,16)==bytes(16)
            self.events.append('remove')
            self.named=0
        elif n==570:
            assert self.depth==1 and a0 in self.pool and self.r32(a0+40)==self.task
            assert self.r32(a0+72)==0 and self.r16(a0+14)>0
            self.events.append('release')
            nest=self.r16(a0+14)-1
            self.w16(a0+14,nest)
            self.w16(a0+44,self.r16(a0+44)-1)
            if not nest:self.w32(a0+40,0)
        elif n==690:
            assert self.depth==0 and a1 in self.pool and a1!=self.named
            assert self.r32(a1+40)==0
            assert self.read(a1-16,16)==self.read(a1+SIZE,16)==b'\x5a'*16
            self.events.append('free')
            self.pool.remove(a1);self.frees+=1
            self.u.mem_write(a1,b'\xa5'*SIZE)
        else:return
        for r,v in ((UC_M68K_REG_D0,result),(UC_M68K_REG_D1,0xdead0001),
                    (UC_M68K_REG_A0,0xdead0002),(UC_M68K_REG_A1,0xdead0003)):
            uc.reg_write(r,v)
    def invoke(self,entry,d0=0,a0=0):
        u=self.u
        u.reg_write(UC_M68K_REG_SR,0x2000)
        for i,r in enumerate(PRESERVED):u.reg_write(r,0x55001000+i)
        u.reg_write(UC_M68K_REG_A0,a0)
        u.reg_write(UC_M68K_REG_D0,d0)
        saved={r:u.reg_read(r) for r in PRESERVED}
        u.reg_write(UC_M68K_REG_A7,STACK)
        u.mem_write(STACK,pack('>I',STOP))
        u.emu_start(self.code_addr+entry,STOP,count=100000)
        assert u.reg_read(UC_M68K_REG_PC)==STOP
        assert u.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(u.reg_read(r)==v for r,v in saved.items())
        assert self.depth==0,'unbalanced Forbid'
        for p in self.pool:
            assert self.read(p-16,16)==self.read(p+SIZE,16)==b'\x5a'*16
        return u.reg_read(UC_M68K_REG_D0),u.reg_read(UC_M68K_REG_D1)
    def enter(self,create=1):return self.invoke(0,d0=create)
    def leave(self,p):return self.invoke(4,a0=p)
    def empty(self):
        assert not self.named and not self.pool and self.allocs==self.frees
    def new(self):
        p,why=self.enter()
        assert p==self.named+56 and why==0
        return p

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('native',type=Path)
    code=cli.parse_args().native.read_bytes()
    cases=0
    m=Machine(code)
    assert m.enter(0)==(0,1);m.empty();cases+=1
    for _ in range(100):
        p=m.new()
        assert m.leave(p)==(1,0);m.empty();cases+=1
    assert m.allocs==100
    # A pending record survives relocation/unload; the name is in owned
    # RAM, not in either executable copy. New owner sees identical receipt.
    m=Machine(code);p=m.new()
    pending=pack('>4I',0x350000,0x351000,0x352000,0)
    m.u.mem_write(p,pending)
    assert m.leave(p)==(1,0) and len(m.pool)==1
    m.u.mem_write(CODE,b'\x4a\xfc'*(len(code)//2))
    m.code_addr=CODE2;m.task=TASK2
    assert m.enter(0)==(p,0) and m.read(p,16)==pending and m.allocs==1
    m.u.mem_write(p,bytes(16))
    assert m.leave(p)==(1,0);m.empty();cases+=1
    # Same task recursion, another task, and forged leave are denied.
    m=Machine(code);p=m.new()
    assert m.enter()==(0,2);cases+=1
    m.task=TASK2
    assert m.enter(0)==(0,2);assert m.leave(p)==(0,2);cases+=1
    m.task=TASK1
    assert m.leave(p+4)==(0,3)
    assert m.leave(p)==(1,0);m.empty();cases+=1
    assert m.leave(p)==(0,3);cases+=1
    # Allocation outside Forbid; competing task publishes during allocation.
    m=Machine(code);m.race=True;p=m.new()
    assert len(m.pool)==1 and m.allocs==2 and m.frees==1
    assert m.r32(p)==0x350000
    m.u.mem_write(p,bytes(16))
    assert m.leave(p)==(1,0);m.empty();cases+=1
    m=Machine(code);m.oom=True
    assert m.enter()==(0,4);m.empty();cases+=1
    assert m.enter(2)==(0,5);cases+=1
    assert m.leave(0)==(0,5);cases+=1
    m=Machine(code);m.w16(EXEC+20,38)
    assert m.enter()==(0,5);m.empty();cases+=1
    m=Machine(code);m.w16(EXEC+16,684)
    assert m.enter()==(0,5);m.empty();cases+=1
    for off,value in ((48,0),(52,0x00020070),(10,0x350000)):
        m=Machine(code);a=m.other_root();m.w32(a+off,value)
        assert m.enter()==(0,3) and len(m.pool)==1
        assert 'attempt' not in m.events;cases+=1
    # Incomplete clearing of the root is not an empty receipt.
    m=Machine(code);p=m.new();m.w32(p+4,0x351000)
    assert m.leave(p)==(1,0) and len(m.pool)==1
    assert m.enter(0)==(p,0)
    m.u.mem_write(p,bytes(16));assert m.leave(p)==(1,0);m.empty();cases+=1
    # Foreign nested lock: release only our own Attempt, do not remove.
    m=Machine(code);p=m.new();a=p-56
    m.w16(a+14,2);m.w16(a+44,1)
    assert m.leave(p)==(1,0) and m.named==a and m.r16(a+14)==1
    assert m.frees==0 and m.r32(a+72)==0;cases+=1
    # A foreign owner without a borrow tag makes Attempt refuse.
    m=Machine(code);a=m.other_root()
    m.w32(a+40,TASK2);m.w16(a+14,1);m.w16(a+44,0)
    assert m.enter(0)==(0,2) and m.frees==0;cases+=1
    print('S1P2H_PERSISTENT_ROOT_CPU_PASS',cases,sha256(code).hexdigest(),flush=True)

if __name__=='__main__':main()
