#!/usr/bin/env python3
"""Real MC68020 CPU/ABI Gate A for R89 Bob Bank + Get AGA Bob.

Runs emitted machine code in Unicorn in two relocation layouts, with
AMOS bank calls and Exec/graphics services mocked. Checks independent
pixel oracle, not WinUAE AMOS Runtime or Compiler.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from
from unittest.mock import patch

from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import (UC_CPU_M68K_M68020,UC_M68K_REG_PC,
                                 UC_M68K_REG_SR)
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_relocation import unpack_ap20
from m19_bobs_ap20_feasibility import emit_bank_select,CAPACITY,NAME,DATA_OFFSET
from m19_bobs_capture_emit import emit_get_bob,GETADR
from build_m19_bobs_native_r89 import build, R88,GROUP_BOBS
from test_m5_generic import Machine,DR,AR,AMOS,EXEC,GFX,DB,SB,BITMAP,STACK,STOP

NEWBANK=0xc00000
OTHER=0xd00000
ARGS=0x58000
W,H,DEPTH=65,43,8
ROW_BYTES=10
NAMES=('Bnk.GetAdr','Bnk.Reserve','Bnk.Change','Bnk.Eff')


def pixel(x,y):
    return ((x*11+y*17+(x>>2)) ^ (0x80 if (x+y)%9==0 else 0))&255


class NativeBobMachine(Machine):
    def __init__(self, candidate, layout='interpreter', depth=DEPTH,
                 occupied=False, no_screen=False):
        with patch('test_m5_generic.UC_CPU_M68K_M68000',UC_CPU_M68K_M68020):
            super().__init__(candidate,None,meta=dict(
                width=W,height=H,depth=depth,row_bytes=ROW_BYTES,camg=0x21000))
        self.depth=depth
        self.banks={11:OTHER}
        self.uc.mem_write(OTHER,b'UNTOUCHED-OTHER-BANK')
        self.original_other=bytes(self.uc.mem_read(OTHER,20))
        self.calls=[]
        self.oscalls=[]
        self.main_table,_=main_table(self.uc)
        self.targets={self.main_table[idx]:name for idx,name,*_ in declarations()
                      if name in NAMES}
        assert set(self.targets.values())==set(NAMES)
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,
                         begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        for addr in self.targets:
            self.uc.mem_write(addr,b'\x4e\x75')
        for addr in (EXEC-534,EXEC-372,GFX-228):
            self.uc.mem_write(addr,b'\x4e\x75')
        _, parts,_ = unpack_ap20(candidate)
        _, base_parts,_ = unpack_ap20(R88.read_bytes())
        native = parts[GROUP_BOBS][len(base_parts[86]):]
        bank, _ = emit_bank_select()
        cap, _ = emit_get_bob()
        assert len(native)==len(bank)+len(cap)
        self.bank_bytes=len(bank)
        self.entry = 0x180000 if layout=='interpreter' else 0x1a0000
        relocated=relocate(native,self.entry,{},self.uc)
        self.uc.mem_write(self.entry,relocated)
        self.get_entry=self.entry+len(bank)
        self.uc.mem_write(NEWBANK+CAPACITY,b'R89-SENTINEL')
        self.uc.mem_write(DB+12,pack('>I',0x5b000))
        for plane in range(depth):
            raw=bytearray(self.stride*H)
            for y in range(H):
                for x in range(W):
                    if pixel(x,y)&(1<<plane):
                        raw[y*self.stride+(x>>3)]|=1<<(7-(x&7))
            self.uc.mem_write(self.planes[plane],bytes(raw))
        self.plane_before=[bytes(self.uc.mem_read(p,self.stride*H))
                           for p in self.planes]
        if no_screen:
            self.put(AMOS+0x1c8,0)

    def ret(self,result=0,ptr=None):
        self.uc.reg_write(DR[0],result&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000 if ptr is None else ptr)
        self.uc.reg_write(AR[1],0xbad100 if ptr is None else ptr)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def main_call(self,uc,address,size,user):
        assert address in self.targets,(hex(address),'not an AMOS bank symbol')
        name=self.targets[address]
        self.calls.append(name)
        assert self.a(5)==AMOS
        if name=='Bnk.GetAdr':
            ptr=self.banks.get(self.d(0),0)
            self.ret(0,ptr)
        elif name=='Bnk.Reserve':
            num=self.d(0)
            assert num not in self.banks,'overwrote user bank'
            assert self.d(1)==1 and self.d(2)==CAPACITY
            assert bytes(uc.mem_read(self.a(0),8))==NAME
            self.banks[num]=NEWBANK
            self.uc.mem_write(NEWBANK,bytes(CAPACITY))
            self.uc.mem_write(NEWBANK-24,pack('>IIIHH8s',
                              0,CAPACITY+16,num,1,0,NAME))
            self.ret(NEWBANK,NEWBANK)
        elif name=='Bnk.Change':
            self.ret()
        elif name=='Bnk.Eff':
            self.banks.pop(self.d(0))
            self.ret()
        else:
            raise AssertionError(name)

    def os_call(self,uc,address,size,user):
        self.oscalls.append(address)
        if address==EXEC-534:
            ptr=self.a(1)
            in_bank=NEWBANK-24<=ptr<NEWBANK+CAPACITY
            in_plane=any(p<=ptr<p+self.stride*H for p in self.planes)
            self.ret(1 if in_bank else 3 if in_plane else 0)
        elif address==EXEC-372:
            self.ret(0x5b100)
        elif address==GFX-228:
            self.ret(0)
        else:
            raise AssertionError(('unexpected native OS service',hex(address)))

    def call(self,command,values):
        if command=='bank':
            args=[]
            entry=self.entry
            d3=values[0]
        elif command=='get':
            # Public syntax Get AGA Bob I,X1,Y1,X2,Y2, D3=Y2.
            args=[values[3],values[2],values[1],values[0]]
            entry=self.get_entry
            d3=values[4]
        else:
            raise ValueError(command)
        for n,reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+n)
        for n,reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+n*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for idx,val in enumerate(args):
            self.put(ARGS+4*idx,val)
        self.uc.reg_write(DR[3],d3&0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(entry,STOP,count=10000000)
        except Exception as e:
            pc=self.uc.reg_read(UC_M68K_REG_PC)
            raise AssertionError((command,values,hex(pc),str(e),
                                  self.calls[-8:],self.oscalls[-8:])) from e
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.a(3)==ARGS+len(args)*4
        assert self.d(2)==0
        for reg, val in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==val,('ABI',reg,val,self.uc.reg_read(reg))
        assert bytes(self.uc.mem_read(OTHER,20))==self.original_other
        assert bytes(self.uc.mem_read(NEWBANK+CAPACITY,12))==b'R89-SENTINEL'
        for pointer, raw in zip(self.planes,self.plane_before):
            assert bytes(self.uc.mem_read(pointer,len(raw)))==raw,'front screen mutated'
        return self.d(3)

    def contents(self):
        return bytes(self.uc.mem_read(NEWBANK,CAPACITY))

    def check_image(self,i,x1,y1,x2,y2):
        raw=self.contents()
        assert raw[:8]==b'AGABOB01'
        count=unpack_from('>H',raw,12)[0]
        assert 1<=count<=128
        d=40+(i-1)*24
        valid,w,h,depth,stride,offset,mask,nbytes=unpack_from('>IHHHHIII',raw,d)
        assert valid==1 and (w,h,depth)==(x2-x1+1,y2-y1+1,self.depth)
        assert stride==((w+15)//16)*2
        assert mask==0 and nbytes==stride*h*depth
        assert DATA_OFFSET<=offset<=CAPACITY-nbytes
        for dy in range(h):
            for dx in range(w):
                actual=0
                for plane in range(depth):
                    byte=raw[offset+(dy*depth+plane)*stride+(dx>>3)]
                    actual|=((byte>>(7-(dx&7)))&1)<<plane
                expected=pixel(x1+dx,y1+dy)&((1<<depth)-1)
                assert actual==expected,('PIXEL',i,x1+dx,y1+dy,actual,expected)
        return count


def main():
    candidate,report=build()
    cases=0
    for layout in ('interpreter','compiler_v2_copy'):
        for depth in (1,4,8):
            m=NativeBobMachine(candidate,layout,depth)
            assert m.call('get',(1,3,2,19,8))==0  # no bank selected
            assert m.call('bank',(10,))==1
            assert m.call('bank',(10,))==1   # reselect existing
            assert m.call('get',(1,3,2,19,8))==1
            assert m.check_image(1,3,2,19,8)==1
            assert m.call('get',(2,17,1,47,7))==1
            assert m.check_image(2,17,1,47,7)==2
            assert m.check_image(1,3,2,19,8)==2
            assert m.call('get',(3,64,42,64,42))==1
            assert m.check_image(3,64,42,64,42)==3
            assert m.call('get',(1,5,5,41,11))==1
            assert m.check_image(1,5,5,41,11)==3
            assert m.check_image(2,17,1,47,7)==3
            before=sha256(m.contents()).digest()
            for bad in ((0,0,0,1,1),(129,0,0,1,1),
                        (2,-1,0,1,1),(2,0,0,65,1),
                        (2,5,5,4,6),(2,5,5,6,4)):
                assert m.call('get',bad)==0,bad
                assert sha256(m.contents()).digest()==before,'modified on reject'
            assert m.call('bank',(11,))==0,'occupied foreign bank'
            assert m.call('bank',(10,))==1
            assert m.check_image(1,5,5,41,11)==3
            cases+=16
    print('R89 GATE A NATIVE PASS:',cases,
          'image/ABI/error cases across 1/4/8 planes and 2 relocated layouts')
    print('Experimental R89 SHA256',report['sha256'],
          'bytes',report['bytes'],'WinUAE and real Compiler NOT RUN')


if __name__=='__main__':
    main()
