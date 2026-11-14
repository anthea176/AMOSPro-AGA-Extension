#!/usr/bin/env python3
"""R84 MC68020 real instruction tests for read-only AGAPIC Bank Image Info.

Mocks only AMOS Bnk.GetAdr and Exec TypeOfMem entrypoints. All header,
v1/v2 format and row table validation is executed by the emitted native code.
No WinUAE or AMOS Compiler claim.
"""
from __future__ import annotations
import struct
from machine68k import Machine,CPUType,Register
from m16_agapic import pack_image
from m16_agapic_v2 import pack_image_v2
from m16_agapic_info_emit import emit_bank_image_info,BANK_LOOKUP,LVO_TYPEOFMEM

CODE=0x1c000
EXIT=0x1800
BANK_SERVICE=0x2800
EXEC=0x8000
BANK=0xc0000
PARAMS=0xd0000
STACK=0xe0000
AMOS=0x32000
MODE=0x00021000

def run_case(payload,field,expected,*,bank=10,bank_number=10,flags=0):
    m=Machine(CPUType.M68020,1024)
    mem,cpu=m.mem,m.cpu
    mem.w32(0,STACK);mem.w32(4,CODE)
    cpu.execute(cpu.pulse_reset())
    mem.w32(4,EXEC)
    end=m.create_execute_end('image-info-done')
    def trap(at,fn):
        ident=m.traps.alloc(fn)
        mem.w16(at,0xa000|ident)
    trap(EXIT,lambda _op,_pc:end)
    def ret(value=0,*,ptr=None):
        pc=mem.r32(cpu.r_sp())
        cpu.w_sp(cpu.r_sp()+4)
        cpu.w_pc(pc)
        cpu.w_reg(Register.D0,value&0xffffffff)
        if ptr is not None:
            cpu.w_reg(Register.A0,ptr)
    calls=[]
    def lookup(_op,_pc):
        supplied=cpu.r_reg(Register.D0)
        calls.append(('lookup',supplied))
        ret(1 if supplied==bank_number else 0,
            ptr=BANK if supplied==bank_number else 0)
    def type_mem(_op,_pc):
        supplied=cpu.r_reg(Register.A1)
        calls.append(('type',supplied))
        ret(1 if BANK-24<=supplied<BANK+len(payload) else 0)
    trap(BANK_SERVICE,lookup)
    trap(EXEC+LVO_TYPEOFMEM,type_mem)
    emitted,labels=emit_bank_image_info()
    assert emitted.count(BANK_LOOKUP)==1
    patched=emitted.replace(BANK_LOOKUP,b'\x4e\xb9'+struct.pack('>I',BANK_SERVICE))
    assert len(patched)==len(emitted)
    mem.w_block(CODE,patched)
    mem.w_block(BANK,payload)
    mem.w_block(BANK-24,struct.pack('>IIIHH8s',0,len(payload)+16,bank_number,flags,0,b'AGAPIC  '))
    mem.w32(PARAMS,bank)
    mem.w32(STACK,EXIT)
    cpu.w_sp(STACK);cpu.w_pc(CODE)
    cpu.w_reg(Register.A3,PARAMS)
    cpu.w_reg(Register.A5,AMOS)
    cpu.w_reg(Register.D3,field&0xffffffff)
    try:
        result=m.execute(500000)
        assert result.result is end,('entry did not return',field,hex(cpu.r_pc()),result)
        assert cpu.r_reg(Register.A3)==PARAMS+4,('A3 ABI',field)
        assert cpu.r_reg(Register.D2)==0,('D2 type',field)
        actual=cpu.r_reg(Register.D3)
        assert actual==(expected&0xffffffff),('image info mismatch',field,actual,expected,calls)
        assert bytes(mem.r_block(BANK,len(payload)))==payload,('bank was modified',field)
        return calls
    finally:
        m.cleanup()

def main():
    w,h,depth=17,3,4
    pixels=bytes((n*7)&15 for n in range(w*h))
    palette=bytes((i*11+7)&255 for i in range(3*(1<<depth)))
    v1=pack_image(w,h,depth,pixels)
    v2=pack_image_v2(w,h,depth,pixels,palette,MODE)
    count=0
    for version,blob,want in ((1,v1,(w,h,depth,0,0)),
                              (2,v2,(w,h,depth,16,MODE))):
        for field,result in enumerate(want,1):
            calls=run_case(blob,field,result)
            assert calls[0]==('lookup',10) and len(calls)>=3
            count+=1
        for field in (0,6,-1):
            run_case(blob,field,-1);count+=1
        run_case(blob,1,-1,bank=11);count+=1
        run_case(blob,1,-1,bank_number=9);count+=1
        for corrupt in (0,6,10,16,20,24,28):
            raw=bytearray(blob)
            raw[corrupt]^=1
            run_case(bytes(raw),1,-1);count+=1
    for off,size in ((32,4),(36,2),(38,2),(40,4),(44,4),
                     (48,4),(52,4),(56,4),(60,4)):
        bad=bytearray(v2)
        bad[off:off+size]=bytes(size)
        run_case(bytes(bad),1,-1)
        count+=1
    # Valid signed AMOS bit pattern for U32 mode must round-trip exactly.
    high=pack_image_v2(w,h,depth,pixels,palette,0x80021000)
    run_case(high,5,0x80021000);count+=1
    print('R84 AGAPIC BANK IMAGE INFO REAL MC68020 PASS:',count,'cases')

if __name__=='__main__':
    main()
