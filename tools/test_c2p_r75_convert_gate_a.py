#!/usr/bin/env python3
"""R75 native Convert Gate A on real 68k bytes and mock SDK/graphics calls.

Not a substitute for running c2p.library or an interpreted AMOS ASC in WinUAE.
"""
from __future__ import annotations

from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from machine68k import CPUType,Register

from build_c2p_r75_convert import build
from c2p_r75_convert_emit import emit_convert,BANK
from test_c2p_r74_open_gate_a import (
    Harness as OpenHarness, SAVED, BANKPTR, BANK_SERVICE, CODE, STOP,
    EXEC,GFX,C2P_LIB,AMOS,STATE,DB,SB0,SB1,BMP,CONTEXT,ARGS,STACK,CHUNKY)
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74

CONVERT_CODE=CODE+0x5000
BM0,BM1=0x124000,0x124100
PLANE=CHUNKY//8
SRC=0x150000
DEST0=0x170000
DEST1=0x190000
BANKPTR2=0x1c0000

class ConvertHarness(OpenHarness):
    def __init__(self,*,depth=8,interleaved=False,**kwargs):
        self.bank_address=BANKPTR
        self.ready_safe=False
        self.fail_convert=False
        self.fail_set_convert=False
        self.partial_blit=False
        self.interleaved=interleaved
        super().__init__(depth=depth,**kwargs)
        self.convert_bytes=emit_convert()[0].replace(BANK,b'\x4e\xb9'+pack('>I',BANK_SERVICE))
        assert len(self.convert_bytes)==len(emit_convert()[0])
        self.mem.w_block(CONVERT_CODE,self.convert_bytes)
        self.trap(C2P_LIB-90,self.sdk_convert)
        self.trap(GFX-30,self.blit_bitmap)
        self.trap(EXEC-372,self.get_message)
        for bm,base in ((BM0,DEST0),(BM1,DEST1)):
            bpr=depth*40 if interleaved else 40
            self.mem.w_block(bm,pack('>HHBBH',bpr,256,1 if interleaved else 0,depth,0))
            for i in range(depth):
                address=base+i*40 if interleaved else base+i*PLANE
                self.mem.w32(bm+8+i*4,address)
            self.mem.w_block(base,bytes([0xa5])*(PLANE*depth))
        for i in range(depth):self.mem.w32(BMP+8+4*i,SRC+i*PLANE)
        self.mem.w32(SB0,BM0)
        self.mem.w32(SB1,BM1)
        self.mem.w32(SB0+4,0x33333330)  # DBufInfo, never sb_BitMap
        self.mem.w32(SB1+4,0x33333334)
        self.mem.w32(DB+12,0x34800)
        self.mem.w32(DB+16,0x34900)
        self.mem.w32(DB+20,0)

    def bank_lookup(self,op,pc):
        self.calls.append('getadr')
        assert self.cpu.r_reg(Register.A5)==AMOS
        ptr=self.bank_address if self.cpu.r_reg(Register.D0)==self.bank else 0
        self.ret(0,a0=ptr)

    def type_of_mem(self,op,pc):
        self.calls.append('type')
        ptr=self.cpu.r_reg(Register.A1)
        is_bank=(BANKPTR-24<=ptr<BANKPTR+self.banklength or
                 BANKPTR2-24<=ptr<BANKPTR2+CHUNKY)
        is_header=(BMP<=ptr<BMP+40 or BM0<=ptr<BM0+40 or BM1<=ptr<BM1+40)
        is_sb=(SB0<=ptr<SB0+8 or SB1<=ptr<SB1+8)
        is_chip=(SRC<=ptr<SRC+self.depth*PLANE or
                 DEST0<=ptr<DEST0+self.depth*PLANE or
                 DEST1<=ptr<DEST1+self.depth*PLANE)
        # Artificially mark the LAST byte of the last SOURCE plane non-Chip.
        if self.fail=='bad_src_chip' and ptr==SRC+self.depth*PLANE-1:is_chip=False
        self.ret(2 if is_chip else 1 if is_bank or is_header or is_sb else 0)

    def set_param(self,op,pc):
        self.calls.append('set')
        if self.fail_set_convert:
            self.ret(37)
            return
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        k=self.cpu.r_reg(Register.D0)
        self.params[k]=self.cpu.r_reg(Register.D1)
        self.ret(0)

    def sdk_convert(self,op,pc):
        self.calls.append('convert')
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        assert self.cpu.r_reg(Register.A6)==C2P_LIB
        if not self.fail_convert:
            for i in range(self.depth):
                self.mem.w_block(SRC+i*PLANE,bytes([i*17+3])*PLANE)
        self.ret(33 if self.fail_convert else 0)

    def get_message(self,op,pc):
        self.calls.append('getmsg')
        assert self.cpu.r_reg(Register.A0)==self.mem.r32(DB+12)
        self.ret(0x44400 if self.ready_safe else 0)

    def blit_bitmap(self,op,pc):
        self.calls.append('blit')
        assert self.cpu.r_reg(Register.A6)==GFX
        assert self.cpu.r_reg(Register.A0)==BMP
        front=self.mem.r32(DB+8)
        expected_back=BM1 if front==0 else BM0
        assert self.cpu.r_reg(Register.A1)==expected_back
        assert self.cpu.r_reg(Register.A2)==0
        assert [self.cpu.r_reg(getattr(Register,f'D{i}')) for i in range(6)]==[0,0,0,0,320,256]
        assert self.cpu.r_reg(Register.D6)==0xc0
        assert self.cpu.r_reg(Register.D7)==0xff
        # Simulate only one full row per plane: the source data belongs to
        # the SDK, the destination belongs to the inactive Intuition bitmap.
        for i in range(self.depth):
            src=self.mem.r32(BMP+8+i*4)
            dst=self.mem.r32(expected_back+8+i*4)
            self.mem.w_block(dst,self.mem.r_block(src,40))
        self.ret(self.depth-1 if self.partial_blit else self.depth)

    def run_convert(self):
        self.calls=[]
        self.cpu.w_sp(STACK);self.mem.w32(STACK,STOP)
        for reg,value in SAVED.items():self.cpu.w_reg(reg,value)
        self.cpu.w_reg(Register.A3,ARGS)
        self.cpu.w_reg(Register.D3,0xabababab)
        self.cpu.w_pc(CONVERT_CODE)
        saved=dict(SAVED)
        result=self.m.execute(8000000)
        assert result.result is self.end,('unexpected CPU stop',result,self.cpu.r_pc())
        assert self.cpu.r_sp()==STACK+4 and self.cpu.r_reg(Register.A3)==ARGS
        assert self.cpu.r_reg(Register.D2)==0
        for reg,val in saved.items():
            assert self.cpu.r_reg(reg)==val,('register corruption',reg,self.cpu.r_reg(reg),val)
        assert self.mem.r_block(DB+48,9)==b'DB_CANARY'
        assert self.mem.r_block(BMP+40,10)==b'BMP_CANARY'
        return self.cpu.r_reg(Register.D3)

    def cleanup(self):self.m.cleanup()


def check(*,depth=8,**opts):
    h=ConvertHarness(depth=depth,**opts)
    try:
        assert h.run()==1
        assert h.run_convert()==1,('convert failed',depth,h.calls)
        assert h.calls.count('set')==h.calls.count('convert')==h.calls.count('blit')==1
        assert h.calls.count('waitblit')==2
        assert h.mem.r_block(DEST1,40)==bytes([3])*40
        assert h.mem.r_block(DEST0,40)==bytes([0xa5])*40,'front changed'
        assert h.mem.r32(DB+8)==0,'implicit Swap'
    finally:h.cleanup()


def main():
    candidate,info=build()
    _,parts=unwrap_native_parts_v2(candidate)
    assert len(parts)==72 and info['commands']==66 and info['ap20_entries']==73
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    code,_=emit_convert()
    assert parts[71]==code and info['code_bytes']==len(code)
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(
        code.replace(BANK,b'\x4e\xb9'+pack('>I',BANK_SERVICE)),0))
    assert sum(x.size for x in decoded)==len(code),'unsupported 68000 opcode'
    cases=0
    for depth in range(4,9):
        check(depth=depth);cases+=1
    check(depth=8,interleaved=True);cases+=1
    h=ConvertHarness()
    try:
        assert h.run()==1
        h.mem.w32(DB+20,3)
        assert h.run_convert()==0
        assert h.calls.count('getmsg')==1 and 'convert' not in h.calls and 'blit' not in h.calls
        assert h.mem.r32(DB+20)==3
        h.ready_safe=True
        assert h.run_convert()==1
        assert h.calls.count('getmsg')==1 and h.mem.r32(DB+20)==2
        h.mem.w32(DB+8,1)
        assert h.run_convert()==1 and h.mem.r_block(DEST0,40)==bytes([3])*40
        assert h.mem.r32(DB+8)==1
        cases+=3
    finally:h.cleanup()
    for kind in ('fail_convert','fail_set_convert','partial_blit','removed_bank',
                 'short_bank','bad_src_chip','bad_back_plane','closed','bad_depth',
                 'no_context','bad_cpu','bad_front_index','bad_back_bpr','front_alias'):
        h=ConvertHarness()
        try:
            assert h.run()==1
            if kind=='fail_convert':h.fail_convert=True
            if kind=='fail_set_convert':h.fail_set_convert=True
            if kind=='partial_blit':h.partial_blit=True
            if kind=='removed_bank':h.bank_address=0
            if kind=='short_bank':h.mem.w32(BANKPTR-20,CHUNKY+15)
            if kind=='bad_src_chip':h.fail='bad_src_chip'
            if kind=='bad_back_plane':h.mem.w32(BM1+8,0)
            if kind=='closed':h.run(close=True)
            if kind=='bad_depth':h.mem.w32(STATE+28,3)
            if kind=='no_context':h.mem.w32(DB+28,0)
            if kind=='bad_cpu':h.mem.w16(EXEC+0x128,0)
            if kind=='bad_front_index':h.mem.w32(DB+8,2)
            if kind=='bad_back_bpr':h.mem.w16(BM1,38)
            if kind=='front_alias':h.mem.w32(SB0,BM1)
            result=h.run_convert()
            assert result==0,(kind,result,h.calls)
            if kind not in ('partial_blit',):
                assert 'blit' not in h.calls,(kind,h.calls)
            if kind=='partial_blit':assert h.calls.count('waitblit')==2
            cases+=1
        finally:h.cleanup()
    h=ConvertHarness()
    try:
        assert h.run()==1
        # Reallocating the AMOS bank with the same bank id must NOT leave
        # an inherited stale chunky pointer inside the c2p context.
        h.mem.w_block(BANKPTR2-24,pack('>IIIHH8s',0,CHUNKY+16,h.bank,1,0,b'C2PRAW  '))
        h.mem.w_block(BANKPTR2,b'Q'*CHUNKY)
        h.bank_address=BANKPTR2
        assert h.run_convert()==1
        assert h.params[4]==BANKPTR2
        cases+=1
    finally:h.cleanup()
    print('R75 CONVERT NATIVE GATE A PASS',cases,'emulated 68000/020 cases',info['sha256'])

if __name__=='__main__':main()
