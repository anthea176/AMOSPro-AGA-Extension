#!/usr/bin/env python3
"""R74 Open-only CPU 68k ABI + OS/SDK ownership tests (not WinUAE Gate B).

Execute the actual native R74 emitter under machine68k with trap-backed
AMOS GetAdr, Exec, c2p.library. Assert 4..8 bitplanes, failure rollback,
no screen mutations and idempotent C2P cleanup on normal/exit path.
"""
from __future__ import annotations

from struct import pack
from machine68k import Machine, CPUType, Register
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

from c2p_r74_open_emit import emit_open, emit_cleanup_hooks, BANK, MAGIC, CHUNKY
from build_c2p_r74_open import build
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74

CODE = 0x160000
STOP = 0x1800
BANK_SERVICE = 0x2800
EXEC = 0x8000
GFX = 0x9000
C2P_LIB = 0xa000
AMOS = 0x32000
STATE = 0x34000
DB = 0x34200
SB0, SB1 = 0x34400, 0x34500
BANKPTR = 0xc0000
ARGS = 0xf0000
STACK = 0xe0000
CONTEXT = 0x120000
BMP = 0x121000

SAVED = {
    Register.D0: 0x12345678, Register.D1:0x23456789,
    Register.D4:0x456789ab, Register.D5:0x56789abc,
    Register.D6:0x6789abcd, Register.D7:0x789abcde,
    Register.A0:0x30000, Register.A1:0x30200,
    Register.A2:0x30400, Register.A4:0x30600,
    Register.A5:AMOS, Register.A6:0x30800,
}

class Harness:
    def __init__(self, *,depth=8, cpu=CPUType.M68020, flags=2,
                 width=320, height=256, bank=12, banklength=CHUNKY,
                 bankflags=1, no_db=False, no_screen=False, fail=None):
        self.m = Machine(cpu,4096)
        self.mem,self.cpu = self.m.mem,self.m.cpu
        self.mem.w32(0,STACK);self.mem.w32(4,CODE)
        self.cpu.execute(self.cpu.pulse_reset())
        self.mem.w32(4,EXEC);self.mem.w16(EXEC+0x128,flags)
        self.end=self.m.create_execute_end('r74-open-done')
        self.trap(STOP,lambda _op,_pc:self.end)
        self.bank=bank;self.banklength=banklength;self.fail=fail
        self.depth=depth
        self.calls=[];self.params={}
        self.mem.w_block(CODE, emit_open()[0].replace(BANK,b'\x4e\xb9'+pack('>I',BANK_SERVICE)))
        self.mem.w32(AMOS+0x1c8,STATE)
        for off,val in ((0,0 if no_screen else 0x35000),(8,GFX),
                        (12,width),(16,height),(28,depth),(32,0 if no_db else DB)):
            self.mem.w32(STATE+off,val)
        self.mem.w_block(DB,bytes(48))
        self.mem.w32(DB,SB0);self.mem.w32(DB+4,SB1)
        self.mem.w_block(DB+48,b'DB_CANARY')
        self.mem.w_block(BANKPTR,b'Z'*max(CHUNKY,banklength))
        self.mem.w_block(BANKPTR-24,pack('>IIIHH8s',0,banklength+16,bank,bankflags,0,b'C2PRAW  '))
        self.mem.w_block(BMP,pack('>HHBBH',40,256,0,depth,0))
        self.mem.w_block(BMP+40,b'BMP_CANARY')
        self.trap(BANK_SERVICE,self.bank_lookup)
        for addr,fn in ((EXEC-534,self.type_of_mem),(EXEC-552,self.open_library),
                        (EXEC-414,self.close_library),(GFX-228,self.wait_blit),
                        (C2P_LIB-48,self.create_context),(C2P_LIB-54,self.initialize),
                        (C2P_LIB-60,self.destroy_context),(C2P_LIB-66,self.get_param),
                        (C2P_LIB-72,self.set_param)):
            self.trap(addr,fn)

    def trap(self,addr,callback):
        self.mem.w16(addr,0xa000|self.m.traps.alloc(callback))

    def ret(self,value=0,a0=None):
        sp=self.cpu.r_sp();pc=self.mem.r32(sp)
        self.cpu.w_sp(sp+4);self.cpu.w_pc(pc)
        self.cpu.w_reg(Register.D0,value&0xffffffff)
        self.cpu.w_reg(Register.A0,(0xbad000 if a0 is None else a0))
        self.cpu.w_reg(Register.D1,0xdeadbeef)

    def bank_lookup(self,_op,_pc):
        self.calls.append('getadr')
        assert self.cpu.r_reg(Register.A5)==AMOS
        ptr=BANKPTR if self.cpu.r_reg(Register.D0)==self.bank else 0
        self.ret(0,a0=ptr)

    def type_of_mem(self,_op,_pc):
        self.calls.append('type')
        ptr=self.cpu.r_reg(Register.A1)
        valid=(BANKPTR-24<=ptr<BANKPTR+self.banklength or
               BMP<=ptr<BMP+40)
        if self.fail=='bad_mem' and ptr==BANKPTR+self.banklength-1:valid=False
        self.ret(1 if valid else 0)

    def open_library(self,_op,_pc):
        self.calls.append('openlib')
        assert self.cpu.r_reg(Register.D0)==1
        assert self.mem.r_block(self.cpu.r_reg(Register.A1),12)==b'c2p.library\0'
        self.ret(0 if self.fail=='openlib' else C2P_LIB)

    def close_library(self,_op,_pc):
        self.calls.append('closelib')
        assert self.cpu.r_reg(Register.A1)==C2P_LIB
        self.ret()

    def create_context(self,_op,_pc):
        self.calls.append('create')
        self.ret(0 if self.fail=='create' else CONTEXT)

    def initialize(self,_op,_pc):
        self.calls.append('init')
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        assert self.params[1]==1 and self.params[2]==320 and self.params[3]==256
        assert self.params[9]==self.depth and self.params[4]==BANKPTR
        self.ret(1 if self.fail=='init' else 0)

    def destroy_context(self,_op,_pc):
        self.calls.append('destroy')
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        self.ret()

    def get_param(self,_op,_pc):
        self.calls.append('getbmp')
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        assert self.cpu.r_reg(Register.D0)==5
        self.ret(0 if self.fail=='getbmp' else BMP)

    def set_param(self,_op,_pc):
        self.calls.append('set')
        assert self.cpu.r_reg(Register.A0)==CONTEXT
        key=self.cpu.r_reg(Register.D0)
        val=self.cpu.r_reg(Register.D1)
        self.params[key]=val
        self.ret(1 if self.fail=='set' and key==9 else 0)

    def wait_blit(self,_op,_pc):
        self.calls.append('waitblit')
        self.ret()

    def run(self,bankarg=None, *, close=False):
        self.cpu.w_sp(STACK);self.mem.w32(STACK,STOP)
        for reg,value in SAVED.items():self.cpu.w_reg(reg,value)
        self.cpu.w_reg(Register.A3,ARGS)
        self.cpu.w_reg(Register.D3,(self.bank if bankarg is None else bankarg)&0xffffffff)
        if close:
            code,labels=emit_cleanup_hooks()
            loc=CODE+0x1000
            self.mem.w_block(loc,code)
            self.cpu.w_pc(loc+labels['cleanup_core'])
            self.cpu.w_reg(Register.A2,STATE)
        else:self.cpu.w_pc(CODE)
        saved={reg:self.cpu.r_reg(reg) for reg in SAVED}
        if close:saved[Register.A2]=STATE
        result=self.m.execute(8000000)
        assert result.result is self.end,('unexpected CPU stop',result,self.cpu.r_pc())
        assert self.cpu.r_sp()==STACK+4
        assert self.cpu.r_reg(Register.A3)==ARGS
        if not close:assert self.cpu.r_reg(Register.D2)==0
        for reg,value in saved.items():
            assert self.cpu.r_reg(reg)==value,('clobbered',reg,value,self.cpu.r_reg(reg))
        assert self.mem.r_block(DB+48,9)==b'DB_CANARY'
        assert self.mem.r_block(BMP+40,10)==b'BMP_CANARY'
        return self.cpu.r_reg(Register.D3)

    def cleanup(self):self.m.cleanup()


def run_case(*, expected=1, bankarg=None, close=False, **opts):
    h=Harness(**opts)
    try:
        before=h.mem.r_block(STATE,40)
        result=h.run(bankarg)
        assert result==expected,(opts,result,h.calls)
        assert h.mem.r_block(STATE,40)==before,'screen state changed by Open'
        if expected:
            assert h.calls.count('openlib')==h.calls.count('create')==h.calls.count('init')==h.calls.count('getbmp')==1
            assert h.calls.count('set')==5
            assert h.mem.r32(DB+24)==C2P_LIB
            assert h.mem.r32(DB+28)==CONTEXT
            assert h.mem.r32(DB+32)==h.bank
            assert h.mem.r32(DB+36)==h.depth
            assert h.mem.r32(DB+40)==MAGIC
            assert h.run()==0 and h.calls.count('create')==1,'duplicate Open created context'
            if close:
                h.run(close=True)
                assert h.calls.count('destroy')==1 and h.calls.count('closelib')==1
                assert h.mem.r_block(DB+24,20)==bytes(20)
                h.run(close=True)
                assert h.calls.count('destroy')==1 and h.calls.count('closelib')==1
                assert h.run()==1,'Open after Close should succeed'
        else:
            assert h.mem.r_block(DB+24,20)==bytes(20),'failed Open committed context'
            assert h.calls.count('destroy')<=1 and h.calls.count('closelib')<=1
            if 'create' in h.calls and opts.get('fail') not in ('create',):
                assert 'destroy' in h.calls and 'closelib' in h.calls
        return 1
    finally:h.cleanup()


def main():
    payload,info=build()
    tokens,parts=unwrap_native_parts_v2(payload)
    assert len(parts)==71 and info['commands']==65 and info['ap20_entries']==72
    assert_native_links(parts[:70]);check_cross_r74(parts)
    open_code,labels=emit_open()
    assert parts[70]==open_code and 'c2p_library_name' in labels
    code=open_code.replace(BANK,b'\x4e\xb9'+pack('>I',BANK_SERVICE))[:labels['c2p_library_name']]
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(code,0))
    assert sum(i.size for i in decoded)==len(code),'bad 68000 opcode in Open'
    tested=0
    for depth in range(4,9):
        tested+=run_case(depth=depth,close=True)
    for opts in (
        dict(cpu=CPUType.M68000,flags=0),
        dict(cpu=CPUType.M68020,flags=0),
        dict(bank=12,no_screen=True),
        dict(depth=3),dict(depth=9),dict(width=319),dict(height=255),
        dict(banklength=81919),dict(bankflags=2),dict(no_db=True),
        dict(fail='bad_mem'),dict(fail='openlib'),dict(fail='create'),
        dict(fail='set'),dict(fail='init'),dict(fail='getbmp'),
    ):
        tested+=run_case(expected=0,**opts)
    for bad_bank in (0,4,-1,65536):
        tested+=run_case(bankarg=bad_bank,expected=0)
    print('R74 OPEN NATIVE GATE A PASS',tested,'68000/020 cases; no WinUAE/Compiler gate',info['sha256'])


if __name__=='__main__':main()
