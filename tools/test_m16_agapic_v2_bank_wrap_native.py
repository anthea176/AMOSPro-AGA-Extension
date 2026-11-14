#!/usr/bin/env python3
"""R82 standalone MC68020 Gate A: AGAPAL Bank Init/Capture forwarding.

Runs the native wrapper and a trap-mocked *legacy entry*, with an actual
BSR.L spanning >32 KiB. This is NOT a new AP20 command or a WinUAE result.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

from machine68k import CPUType, Machine, Register

from m16_agapic_v2_bank_wrap_emit import (
    BANK_LOOKUP, emit_bank_palette_init, emit_bank_palette_capture
)

ROOT = Path(__file__).resolve().parents[1]
R81_SHA = '9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
CODE = 0x180000
EXEC = 0x8000
BANK_LOOKUP_TRAP = 0x2800
BANK = 0xc0000
PARAMS = 0xd0000
STACK = 0xe0000
EXIT = 0x1800
REL_WRAPPER = 57000
REL_TARGET = 17000


def once(emit, label, bank, arg, *, compiled=False, cpu_type=CPUType.M68020):
    native_offset = REL_WRAPPER + (32 if compiled else 0)
    legacy_offset = REL_TARGET + (32 if compiled else 0)
    native, labels = emit(native_offset, legacy_offset)
    assert native == emit(native_offset, legacy_offset)[0]
    assert native.count(BANK_LOOKUP) == 1
    pos = labels['delegate']
    assert native[pos:pos+2] == bytes.fromhex('61ff')
    signed = unpack_from('>i',native,pos+2)[0]
    assert signed < -32768, (label,'test does not exercise BSR.L')
    assert native_offset + pos + 2 + signed == legacy_offset

    m = Machine(cpu_type, 2048)
    mem,cpu = m.mem,m.cpu
    mem.w32(0,STACK)
    mem.w32(4,CODE)
    cpu.execute(cpu.pulse_reset())
    mem.w32(4, EXEC)
    mem.w16(EXEC + 0x128, 2 if cpu_type == CPUType.M68020 else 0)
    end = m.create_execute_end('wrapper-return')
    def trap(address, callback):
        ident = m.traps.alloc(callback)
        mem.w16(address,0xA000 | ident)
    trap(EXIT, lambda _op,_pc: end)

    target = CODE + legacy_offset - native_offset
    history = []
    def return_from_call(value, a0=None):
        pc = mem.r32(cpu.r_sp())
        cpu.w_sp(cpu.r_sp()+4)
        cpu.w_pc(pc)
        cpu.w_reg(Register.D0,value)
        cpu.w_reg(Register.D1,0xdeadbeef)
        cpu.w_reg(Register.A0, a0 if a0 is not None else 0xbad000)
        cpu.w_reg(Register.A1,0xbad100)
    def lookup(_op,_pc):
        supplied=cpu.r_reg(Register.D0)
        history.append(('lookup',supplied))
        assert supplied == bank
        return_from_call(1 if bank==10 else 0, BANK if bank==10 else 0)
    trap(BANK_LOOKUP_TRAP,lookup)
    def legacy(_op,_pc):
        pointer=cpu.r_reg(Register.A3)
        assert cpu.r_reg(Register.D3)==arg
        assert mem.r32(pointer)==BANK
        history.append(('delegate',label,arg))
        cpu.w_reg(Register.A3,pointer+4)
        cpu.w_reg(Register.D3,1)
        cpu.w_reg(Register.D2,0)
        return_from_call(1)
    trap(target,legacy)

    # A genuine Rjsr assembler/linker will resolve this at runtime. The
    # CPU harness replaces only the audited 6-byte Bnk.GetAdr relocation.
    patched=native.replace(BANK_LOOKUP,b'\x4e\xb9'+pack('>I',BANK_LOOKUP_TRAP))
    assert len(patched)==len(native) and BANK_LOOKUP not in patched
    mem.w_block(CODE,patched)
    mem.w32(PARAMS,bank)
    mem.w32(STACK,EXIT)
    cpu.w_sp(STACK)
    cpu.w_pc(CODE)
    cpu.w_reg(Register.A3,PARAMS)
    cpu.w_reg(Register.D3,arg)
    cpu.w_reg(Register.D2,0x12345678)
    preserved={
        Register.D0:0x11223344,
        Register.D1:0x22334455,
        Register.D4:0x44556677,
        Register.D5:0x55667788,
        Register.D6:0x66778899,
        Register.D7:0x778899aa,
        Register.A0:0x41000,
        Register.A1:0x42000,
        Register.A2:0x43000,
        Register.A4:0x44000,
        Register.A5:0x45000,
        Register.A6:0x46000,
    }
    for reg,val in preserved.items():
        cpu.w_reg(reg,val)
    try:
        result=m.execute(150000)
        assert result.result is end, (label, bank, cpu.r_pc(), result)
        assert cpu.r_sp()==STACK+4
        assert cpu.r_reg(Register.A3)==PARAMS+4
        assert cpu.r_reg(Register.D2)==0
        assert cpu.r_reg(Register.D3)==int(bank==10 and cpu_type == CPUType.M68020)
        for reg,val in preserved.items():
            assert cpu.r_reg(reg)==val, ('modified caller register',label,reg)
        if bank in (4,65536) or cpu_type == CPUType.M68000:
            assert history==[],history
        elif bank==11:
            assert history==[('lookup',11)],history
        else:
            assert history==[('lookup',10),('delegate',label,arg)],history
    finally:
        m.cleanup()
    return 1


def main():
    expected=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(expected).hexdigest()==R81_SHA
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==expected
    count=0
    for compiled in (False,True):
        for emitter,name,args in (
            (emit_bank_palette_init,'INIT',(1,8,256)),
            (emit_bank_palette_capture,'CAPTURE',(0,7,255))
        ):
            for bank in (4,10,11,65536):
                for arg in args:
                    count += once(emitter,name,bank,arg,compiled=compiled)
            count += once(emitter,name,10,args[0],compiled=compiled,cpu_type=CPUType.M68000)
    print('R82 simple bank wrappers real MC68020 Gate A PASS:',
          count,'native executions, BSR.L beyond 32KiB, ABI, bank failures, CPU000 refusal')
    print('R81 last good unchanged; AGAPIC v2 Apply/Fade not implemented.')


if __name__=='__main__':
    main()
