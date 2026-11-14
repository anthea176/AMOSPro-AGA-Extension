#!/usr/bin/env python3
"""R82: real MC68020 standalone Gate A for unified Bank Palette Apply/Fade.

Mocks ONLY OS/AMOS service entrypoints and the previously qualified AGAPAL
legacy core. The v2 parsing, RGB32 serialization and fade loops execute real
68020 instructions. No installed binary, Compiler or WinUAE claim.
"""
from __future__ import annotations

import struct
from machine68k import Machine, CPUType, Register

from m16_agapic_v2_palette_emit import (
    BANK_LOOKUP, LVO_GETVPMODEID, LVO_TYPEOFMEM, LVO_ALLOCVEC,
    LVO_FREEVEC, LVO_LOADRGB32, LVO_GETRGB32, LVO_WAITTOF,
    emit_bank_palette_apply, emit_bank_palette_fade)
from m16_agapic_v2 import pack_image_v2

CPU_CODE = 0x1c000
NATIVE_START = 58400
LEGACY_OFFSET = 17000
EXIT = 0x1800
BANK_SERVICE = 0x2800
EXEC = 0x8000
AMOS = 0x32000
STATE = 0x34000
SCREEN = 0x34a00
GFX = 0x34b00
COLORMAP = 0x34c00
BANK = 0xc0000
PARAMS = 0xd0000
STACK = 0xe0000
SCRATCH = 0x90000
MODE = 0x00021000


class PaletteMachine:
    def __init__(self, code, payload, *, depth=4, mode_id=MODE,
                 fade=False, index=0, vbl=3, cpu=CPUType.M68020,
                 native_flags=0, bank_name=b'AGAPIC  ', bank_number=10,
                 screen_colors=None):
        self.m = Machine(cpu, 1024)
        self.cpu = self.m.cpu
        self.mem = self.m.mem
        self.payload = payload
        self.fade = fade
        self.index = index
        self.vbl = vbl
        self.bank_number = bank_number
        self.mode_id = mode_id
        self.wait_count = self.load_count = self.rgb_count = 0
        self.lookup_calls = self.type_calls = self.alloc_calls = self.free_calls = self.mode_calls = 0
        self.legacy_calls = 0
        self.owned = {}
        self.screen_palette = [(0x22000000,0x44000000,0x66000000)] * 256
        self.before = tuple(self.screen_palette)
        self.frames=[]
        self.mem.w32(0, STACK); self.mem.w32(4, CPU_CODE)
        self.cpu.execute(self.cpu.pulse_reset())
        self.mem.w32(4, EXEC)
        self.mem.w16(EXEC + 0x128, 2 if cpu == CPUType.M68020 else 0)
        self.end = self.m.create_execute_end('bank palette exit')
        self.trap(EXIT, lambda _op, _pc: self.end)
        self.trap(BANK_SERVICE, self.lookup)
        for relative, fn in ((LVO_TYPEOFMEM,self.type_mem),
                             (LVO_ALLOCVEC,self.alloc_vec),
                             (LVO_FREEVEC,self.free_vec)):
            self.trap(EXEC + relative, fn)
        for relative, fn in ((LVO_GETVPMODEID,self.get_mode),
                             (LVO_LOADRGB32,self.load_rgb),
                             (LVO_GETRGB32,self.get_rgb),
                             (LVO_WAITTOF,self.wait_tof)):
            self.trap(GFX + relative, fn)
        legacy_at = CPU_CODE + LEGACY_OFFSET - NATIVE_START
        assert legacy_at > EXEC and legacy_at < CPU_CODE - 32768
        self.trap(legacy_at, self.legacy)
        patched = code.replace(BANK_LOOKUP, b'\x4e\xb9' + struct.pack('>I', BANK_SERVICE))
        assert len(patched) == len(code) and code.count(BANK_LOOKUP)==1
        self.mem.w_block(CPU_CODE, patched)
        self.mem.w32(AMOS+0x1c8,STATE)
        self.mem.w32(STATE,SCREEN)
        self.mem.w32(STATE+8,GFX)
        self.mem.w32(STATE+20,screen_colors if screen_colors is not None else (1<<depth))
        self.mem.w32(STATE+24,0)
        self.mem.w32(STATE+28,depth)
        self.mem.w32(SCREEN+48,COLORMAP)
        self.mem.w16(COLORMAP+2,screen_colors if screen_colors is not None else (1<<depth))
        self.mem.w_block(BANK,payload)
        self.mem.w_block(BANK-24,struct.pack('>IIIHH8s',0,len(payload)+16,
                       bank_number,native_flags,0,bank_name))

    def trap(self,addr,fn):
        ident=self.m.traps.alloc(fn)
        assert 0<=ident<=4095
        self.mem.w16(addr,0xa000|ident)

    def ret(self,value=0,*,ptr=None):
        ret_pc=self.mem.r32(self.cpu.r_sp())
        self.cpu.w_sp(self.cpu.r_sp()+4)
        self.cpu.w_pc(ret_pc)
        self.cpu.w_reg(Register.D0,value & 0xffffffff)
        self.cpu.w_reg(Register.D1,0xdeadbeef)
        self.cpu.w_reg(Register.A0,0xbad000 if ptr is None else ptr)
        self.cpu.w_reg(Register.A1,0xbad100)

    def lookup(self,_op,_pc):
        self.lookup_calls+=1
        assert self.cpu.r_reg(Register.A5)==AMOS
        valid=self.cpu.r_reg(Register.D0)==10
        self.ret(int(valid),ptr=BANK if valid else 0)

    def legacy(self,_op,_pc):
        self.legacy_calls+=1
        a3=self.cpu.r_reg(Register.A3)
        if self.fade:
            assert self.mem.r32(a3)==self.index
            assert self.mem.r32(a3+4)==BANK
            assert self.cpu.r_reg(Register.D3)==self.vbl
            self.cpu.w_reg(Register.A3,a3+8)
        else:
            assert self.mem.r32(a3)==BANK
            assert self.cpu.r_reg(Register.D3)==self.index
            self.cpu.w_reg(Register.A3,a3+4)
        self.cpu.w_reg(Register.D3,1)
        self.ret(1)

    def type_mem(self,_op,_pc):
        self.type_calls+=1
        a1=self.cpu.r_reg(Register.A1)
        self.ret(1 if BANK-24<=a1<BANK+len(self.payload) else 0)

    def alloc_vec(self,_op,_pc):
        self.alloc_calls+=1
        length=self.cpu.r_reg(Register.D0)
        assert self.cpu.r_reg(Register.D1)==1 and 0<length<15000
        self.owned[SCRATCH]=length
        self.mem.w_block(SCRATCH,bytes(length))
        self.ret(SCRATCH,ptr=SCRATCH)

    def free_vec(self,_op,_pc):
        self.free_calls+=1
        ptr=self.cpu.r_reg(Register.A1)
        assert ptr in self.owned
        del self.owned[ptr]
        self.ret(0)

    def get_mode(self,_op,_pc):
        self.mode_calls += 1
        assert self.cpu.r_reg(Register.A0)==SCREEN+44
        self.ret(self.mode_id)

    def load_rgb(self,_op,_pc):
        assert self.cpu.r_reg(Register.A0)==SCREEN+44
        start=self.cpu.r_reg(Register.A1)
        count,first=divmod(self.mem.r32(start),65536)
        assert first==0 and 1<=count<=256
        assert start in self.owned and self.owned[start]>=8+count*12
        assert self.mem.r32(start+4+count*12)==0
        for i in range(count):
            rgb=tuple(self.mem.r32(start+4+i*12+4*k) for k in range(3))
            assert all(x==((x>>24)*0x01010101) for x in rgb)
            self.screen_palette[i]=rgb
        self.frames.append(tuple(self.screen_palette))
        self.load_count+=1
        self.ret()

    def get_rgb(self,_op,_pc):
        self.rgb_count+=1
        assert self.wait_count==0
        assert self.cpu.r_reg(Register.A0)==COLORMAP
        count=self.cpu.r_reg(Register.D1)
        assert self.cpu.r_reg(Register.D0)==0 and count<=256
        dest=self.cpu.r_reg(Register.A1)
        assert any(start<=dest and dest+12*count<=start+length
                   for start,length in self.owned.items())
        for i in range(count):
            for k in range(3):
                self.mem.w32(dest+i*12+k*4,self.screen_palette[i][k])
        self.ret()

    def wait_tof(self,_op,_pc):
        self.wait_count+=1
        self.ret()

    def run(self,*, expect_ok=True):
        cpu=self.cpu
        self.mem.w32(STACK,EXIT)
        self.mem.w32(PARAMS, self.index if self.fade else self.bank_number)
        if self.fade:
            self.mem.w32(PARAMS+4,self.bank_number)
        cpu.w_sp(STACK);cpu.w_pc(CPU_CODE)
        preserved={
            Register.D0:0x11223344,Register.D1:0x22334455,
            Register.D4:0x44556677,Register.D5:0x55667788,
            Register.D6:0x66778899,Register.D7:0x778899aa,
            Register.A0:0x41000,Register.A1:0x42000,
            Register.A2:0x43000,Register.A4:0x44000,
            Register.A5:AMOS,Register.A6:0x46000}
        for reg,val in preserved.items(): cpu.w_reg(reg,val)
        cpu.w_reg(Register.A3,PARAMS)
        cpu.w_reg(Register.D2,0xabcdef01)
        cpu.w_reg(Register.D3,self.vbl if self.fade else self.index)
        try:
            result=self.m.execute(5_000_000)
            assert result.result is self.end,(cpu.r_pc(),result)
            assert cpu.r_sp()==STACK+4
            assert cpu.r_reg(Register.A3)==PARAMS+(8 if self.fade else 4)
            assert cpu.r_reg(Register.D2)==0
            assert cpu.r_reg(Register.D3)==int(expect_ok), (
                'R82 palette native reject', {'fade':self.fade,'depth':self.mem.r32(STATE+28),
                  'index':self.index,'vbl':self.vbl,'bank_name':self.mem.r_block(BANK-8,8),
                  'lookup':self.lookup_calls,'type':self.type_calls,'mode':self.mode_calls,
                  'alloc':self.alloc_calls,'free':self.free_calls,
                  'load':self.load_count,'rgb':self.rgb_count,'wait':self.wait_count,
                  'D3':cpu.r_reg(Register.D3),'A0':hex(cpu.r_reg(Register.A0))})
            for reg,val in preserved.items():
                assert cpu.r_reg(reg)==val,('ABI register',reg)
            assert not self.owned, 'scratch memory leaked'
            if not expect_ok:
                assert self.screen_palette==list(self.before)
                assert self.load_count==self.wait_count==0
            return 1
        finally:
            self.m.cleanup()


def case(fade, depth, *, masked=False, index=0, mode_id=MODE,
         correct_mode=MODE, corrupt=None, cpu=CPUType.M68020,
         bank_name=b'AGAPIC  ', bank_number=10, vbl=3, expect_ok=True):
    px=bytes((i*3)% (1<<depth) for i in range(17*3))
    colors=bytes((i*13+7)&255 for i in range(3*(1<<depth)))
    mask=bytes((i&1)!=0 for i in range(len(px))) if masked else None
    bank=bytearray(pack_image_v2(17,3,depth,px,colors,correct_mode,mask))
    if corrupt:
        at,length,v=corrupt
        bank[at:at+length]=int(v).to_bytes(length,'big')
    fn=emit_bank_palette_fade if fade else emit_bank_palette_apply
    code,meta=fn(NATIVE_START,LEGACY_OFFSET)
    assert code==fn(NATIVE_START,LEGACY_OFFSET)[0]
    assert meta['legacy_branch_long_displacement']< -32768
    m=PaletteMachine(code,bytes(bank),depth=depth,mode_id=mode_id,
                     fade=fade,index=index,vbl=vbl,cpu=cpu,
                     bank_name=bank_name,bank_number=bank_number)
    if bank_name==b'AGAPAL  ':
        assert m.run(expect_ok=expect_ok)
        assert m.legacy_calls==int(expect_ok)
    else:
        assert m.run(expect_ok=expect_ok)
        assert m.legacy_calls==0
        if expect_ok:
            assert m.load_count==(vbl if fade else 1)
            assert m.wait_count==(vbl if fade else 0)
            assert m.rgb_count==(int(vbl>1) if fade else 0)
            assert m.alloc_calls==m.free_calls==1
            target=[tuple(int(x)*0x01010101 for x in colors[3*i:3*i+3])
                    for i in range(1<<depth)]
            assert m.screen_palette[:len(target)]==target
            assert m.screen_palette[len(target):]==list(m.before)[len(target):]
    return 1


def main():
    count=0
    for fade in (False,True):
        for depth in (1,4,8):
            for masked in (False,True):
                for frames in ((1,2,4) if fade else (1,)):
                    count += case(fade,depth,masked=masked,vbl=frames)
        count += case(fade,4,index=1,expect_ok=False)
        count += case(fade,4,mode_id=MODE+1,expect_ok=False)
        count += case(fade,4,bank_number=4,expect_ok=False)
        count += case(fade,4,bank_name=b'INVALID ',expect_ok=False)
        count += case(fade,4,cpu=CPUType.M68000,expect_ok=False)
        for corrupt in ((6,2,1),(8,2,0),(32,4,0),(32,4,0xffffffff),
                        (36,2,4),(38,2,2),(40,4,12),(44,4,0),
                        (48,4,0),(52,4,1),(20,4,32),(28,4,1)):
            count+=case(fade,4,corrupt=corrupt,expect_ok=False)
        # AGAPAL v1 delegates to the exact legacy Apply/Fade path.
        count += case(fade,4,bank_name=b'AGAPAL  ',expect_ok=True)
    for duration in (0,256,0xffffffff):
        count += case(True,4,vbl=duration,expect_ok=False)
    print('AGAPIC v2 unified Bank Apply/Fade MC68020 Gate A PASS:',count,
          'cases, exact RGB32, fades, indexes, ModeID, ABI, CPU000, legacy')


if __name__=='__main__': main()
