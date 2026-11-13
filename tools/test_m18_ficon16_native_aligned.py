#!/usr/bin/env python3
"""M18/P2: real 68000 aligned icon core vs independent P1 pixel/planar oracle.
CPU emulator Gate A ONLY; no AP20, WinUAE, Fast→Chip staging or Blitter.
"""
from random import Random
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68000,UC_M68K_REG_PC,UC_M68K_REG_SR,
    UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,
    UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7,
    UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,
    UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,
)
from m18_ficon16_model import build_bank,parse_bank,draw_cpu
from m18_ficon16_native_aligned_emit import emit_ficon16_aligned_cpu

CODE=0x10000
ICON=0x20000
POINTERS=0x30000
PLANE_BASE=0x40000
STACK=0xf0000
STOP=0x12000
WIDTH=65
HEIGHT=43
STRIDE=((WIDTH+15)//16)*2
GUARD=b'\x5a'*32

def as_planar(pixels):
    planes=[bytearray(STRIDE*HEIGHT) for _ in range(8)]
    for pos,value in enumerate(pixels):
        y,x=divmod(pos,WIDTH)
        at=y*STRIDE+(x>>3)
        bit=0x80>>(x&7)
        for p in range(8):
            if value&(1<<p):
                planes[p][at]|=bit
    return planes

def execute(core,icon,planes,*,x=16,y=1,mode=0,width=WIDTH,
            height=HEIGHT,stride=STRIDE,source=ICON,ptrs=POINTERS,
            bad_plane=-1,debug_hook=None):
    assert len(icon)==288 and len(planes)==8
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0,0x1000000)
    uc.mem_write(CODE,core)
    uc.mem_write(STOP,bytes.fromhex('4e71'))
    uc.mem_write(STACK,pack('>I',STOP))
    uc.mem_write(ICON,icon)
    bases=[PLANE_BASE+i*0x1000 for i in range(8)]
    pointers=bases[:]
    if bad_plane>=0:pointers[bad_plane]=0
    uc.mem_write(POINTERS,b''.join(pack('>I',a) for a in pointers))
    for addr,p in zip(bases,planes):
        uc.mem_write(addr,bytes(p)+GUARD)
    inputs={
        UC_M68K_REG_A0:source, UC_M68K_REG_A1:ptrs,
        UC_M68K_REG_A2:0x73002,UC_M68K_REG_A3:0x73004,
        UC_M68K_REG_A4:0x73006,UC_M68K_REG_A5:0x73008,
        UC_M68K_REG_A6:0x7300a,
        UC_M68K_REG_D0:x&0xffffffff,UC_M68K_REG_D1:y&0xffffffff,
        UC_M68K_REG_D2:stride,UC_M68K_REG_D3:mode&0xffffffff,
        UC_M68K_REG_D4:width,UC_M68K_REG_D5:height,
        UC_M68K_REG_D6:0x12344321,UC_M68K_REG_D7:0x98badcfe,
    }
    for reg,value in inputs.items():
        uc.reg_write(reg,value)
    uc.reg_write(UC_M68K_REG_SR,0x2000)
    uc.reg_write(UC_M68K_REG_A7,STACK)
    if debug_hook is not None:
        uc.hook_add(UC_HOOK_CODE,debug_hook)
    uc.emu_start(CODE,STOP,count=100000)
    assert uc.reg_read(UC_M68K_REG_PC)==STOP,'native did not return'
    assert uc.reg_read(UC_M68K_REG_A7)==STACK+4,'unbalanced stack'
    assert uc.reg_read(UC_M68K_REG_D2)==0,'result D2 not zero'
    for reg,value in inputs.items():
        if reg not in (UC_M68K_REG_D2,UC_M68K_REG_D3):
            assert uc.reg_read(reg)==value,('preserved register changed',reg)
    after=[bytearray(uc.mem_read(addr,len(p))) for addr,p in zip(bases,planes)]
    for addr,p in zip(bases,planes):
        assert bytes(uc.mem_read(addr+len(p),len(GUARD)))==GUARD
    assert bytes(uc.mem_read(ICON,288))==icon
    return uc.reg_read(UC_M68K_REG_D3),after

def main():
    core,labels=emit_ficon16_aligned_cpu()
    instr=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(core,CODE))
    assert sum(i.size for i in instr)==len(core),'invalid Motorola 68000 opcode'
    assert core==emit_ficon16_aligned_cpu()[0],'emitter not deterministic'
    assert len(core)<1500 and len(labels)>8
    assert not any(i.mnemonic.lower() in ('jsr','jmp','trap','stop') for i in instr)
    rng=Random(0xF0162026)
    fixtures=(
        bytes([0]*256),bytes([255]*256),
        bytes(((x*19+y*13)&255) for y in range(16) for x in range(16)),
        bytes((rng.randrange(256) if (x+y)%5 else 0)
              for y in range(16) for x in range(16)),
    )
    bank=parse_bank(build_bank(fixtures))
    cases=0
    placements=((-16,0),(0,0),(16,1),(32,7),(48,27),
                (64,42),(64,41),(0,-15),(16,-1),(32,43),
                (80,0),(32752,32767),(-32768,-32768))
    for icon_id in (1,2,3,4):
        icon=bank.icon(icon_id)
        for x,y in placements:
            for mode in (0,1):
                pixels=bytes(rng.randrange(256) for _ in range(WIDTH*HEIGHT))
                before=as_planar(pixels)
                expected=[bytearray(p) for p in before]
                draw_cpu(bank,icon_id,x,y,mode,expected,WIDTH,HEIGHT,STRIDE)
                status,actual=execute(core,icon,before,x=x,y=y,mode=mode)
                assert status==1,(icon_id,x,y,mode,'return')
                assert actual==expected,(icon_id,x,y,mode,'pixels')
                cases+=1
    icon=bank.icon(3)
    before=as_planar(bytes([0x42]*(WIDTH*HEIGHT)))
    rejected=(
        dict(x=1),dict(x=-1),dict(x=17),dict(x=32768),
        dict(y=32768),dict(y=-32769),dict(mode=-1),dict(mode=2),
        dict(width=0),dict(width=4097),dict(height=0),dict(height=4097),
        dict(stride=1),dict(stride=STRIDE-2),dict(stride=65536),
        dict(source=0),dict(source=ICON+1),dict(ptrs=0),
        dict(ptrs=POINTERS+1),dict(bad_plane=7),
    )
    for params in rejected:
        status,actual=execute(core,icon,before,**params)
        assert status==0 and actual==before,('bad accepted or drew',params)
    print('M18/P2 ALIGNED NATIVE CORE GATE A PASS:',
          len(core),'bytes;',cases,'pixel/ABI cases;',len(rejected),'refusals')
    print('ONLY ALIGNED X; trusted source and private back. '
          'No AP20, no WinUAE, no Blitter or staging.')

if __name__=='__main__':
    main()
