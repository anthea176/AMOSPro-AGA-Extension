#!/usr/bin/env python3
"""M18/P2 real M68000 288-byte Fast->Chip staging, Unicorn Gate A only."""
from struct import pack
from random import Random
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,
    UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,
    UC_M68K_REG_A6,UC_M68K_REG_A7,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,
    UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,
    UC_M68K_REG_D6,UC_M68K_REG_D7,
)
from m18_ficon16_model import build_bank,parse_bank
from m18_ficon16_native_stage_emit import emit_ficon16_stage_cpu

CODE=0x10000
FAST=0x20000
CHIP=0x30000
STACK=0xf0000
STOP=0x12000
GUARD=bytes([0xa5])*32

def expected_layout(slot):
    assert len(slot)==288
    staged=bytearray(288)
    for row in range(16):
        for plane in range(9):
            src=(row*9+plane)*2
            dst=plane*32+row*2
            staged[dst:dst+2]=slot[src:src+2]
    return bytes(staged)

def execute(code,slot,src=FAST,dst=CHIP):
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0,0x1000000)
    uc.mem_write(CODE,code)
    uc.mem_write(STOP,bytes.fromhex('4e71'))
    uc.mem_write(STACK,pack('>I',STOP))
    uc.mem_write(FAST,slot)
    uc.mem_write(CHIP,bytes([0x33])*288+GUARD)
    data={
        UC_M68K_REG_A0:src,UC_M68K_REG_A1:dst,
        UC_M68K_REG_A2:0x93002,UC_M68K_REG_A3:0x93004,
        UC_M68K_REG_A4:0x93006,UC_M68K_REG_A5:0x93008,
        UC_M68K_REG_A6:0x9300a,
        UC_M68K_REG_D0:0x213405,UC_M68K_REG_D1:0x888432,
        UC_M68K_REG_D2:0x344566,UC_M68K_REG_D3:0x2345f0,
        UC_M68K_REG_D4:0x202545,UC_M68K_REG_D5:0x344423,
        UC_M68K_REG_D6:0x777888,UC_M68K_REG_D7:0x133777,
    }
    for reg,value in data.items():
        uc.reg_write(reg,value)
    # SR supervisor mode selects ISP; set SR BEFORE A7, as in the frozen Gate A fixtures.
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    uc.reg_write(UC_M68K_REG_A7,STACK)
    try:
        uc.emu_start(CODE,STOP,count=100000)
    except Exception as exc:
        regs={name:hex(uc.reg_read(reg)) for name,reg in (
            ('PC',UC_M68K_REG_PC),('A0',UC_M68K_REG_A0),
            ('A1',UC_M68K_REG_A1),('A4',UC_M68K_REG_A4),
            ('SP',UC_M68K_REG_A7),('D0',UC_M68K_REG_D0),
            ('D1',UC_M68K_REG_D1),('D2',UC_M68K_REG_D2),
            ('D3',UC_M68K_REG_D3),('D4',UC_M68K_REG_D4),
            ('D5',UC_M68K_REG_D5))}
        raise AssertionError(('M18 P2 stage native CPU exception',
                              repr(exc),regs)) from exc
    assert uc.reg_read(UC_M68K_REG_PC)==STOP
    assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
    assert uc.reg_read(UC_M68K_REG_D2)==0
    for reg,value in data.items():
        if reg not in (UC_M68K_REG_D2,UC_M68K_REG_D3):
            assert uc.reg_read(reg)==value,('saved register changed',reg)
    assert bytes(uc.mem_read(CHIP+288,32))==GUARD
    assert bytes(uc.mem_read(FAST,288))==slot
    return uc.reg_read(UC_M68K_REG_D3),bytes(uc.mem_read(CHIP,288))

def main():
    code,labels=emit_ficon16_stage_cpu()
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(code,CODE))
    assert sum(x.size for x in ins)==len(code)
    assert code==emit_ficon16_stage_cpu()[0] and len(labels)>=5
    rng=Random(0xA6F01C02)
    icons=(bytes(256),bytes([255]*256),bytes(range(256)),
           bytes(rng.randrange(256) for _ in range(256)))
    bank=parse_bank(build_bank(icons))
    for num in range(1,5):
        slot=bank.icon(num)
        status,actual=execute(code,slot)
        assert status==1 and actual==expected_layout(slot),num
    source=bank.icon(4)
    bad=((0,CHIP),(FAST+1,CHIP),(FAST,0),(FAST,CHIP+1),
         (CHIP,CHIP),(CHIP-100,CHIP),(CHIP+16,CHIP),
         (CHIP,CHIP+272),(0xfffffffe,CHIP),(FAST,0xfffffffe))
    for src,dst in bad:
        status,actual=execute(code,source,src,dst)
        assert status==0 and actual==bytes([0x33])*288,(src,dst)
    print('M18/P2 NATIVE STAGING 68000 Gate A PASS:',
          len(code),'bytes; 4 formats,',len(bad),'refusals')
    print('No AP20, no Chip allocation, no Blitter or WinUAE proof.')

if __name__=='__main__':
    main()
