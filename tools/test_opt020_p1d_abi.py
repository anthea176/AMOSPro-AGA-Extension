#!/usr/bin/env python3
"""OPT020/P1d: synthetic AP20 ABI shell + CPU guard and in-memory V2 test.

NO real AMOS API or .Lib is generated. A0 points to a test-only prevalidated
descriptor, never a bank ID. The in-memory V2 round trip substitutes a dummy
entry temporarily, and is NOT a functional R69 or a Compiler Gate C.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from random import Random
from struct import pack

from capstone import CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020, Cs
from machine68k import CPUType, Machine, Register

from compiler_bridge_v2_probe import (
    unwrap_native_parts_v2, wrap_native_ap20_v2, DISPATCH_V2)
from compiler_relocation import GETP, unpack_ap20, repack_ap20
from opt020_p1d_ap20_probe_emit import (
    emit_ap20_shaped_probe, EXECBASE_ATTNFLAGS, AFF_68020_BIT)

ROOT=Path(__file__).resolve().parents[1]
R68_SHA="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
CODE=0x2000
TRAP=0x1800
SYSBASE=0x3000
SRC=0xa000
MASK=0xa100
PTRTABLE=0xb000
DEST=0xc000
STACK=0x1f000
PARAMS=0x21000
DESCRIPTOR=0x22000
BEFORE=b"\xa5"*8
AFTER=b"\x5a"*8
SAVED={
    Register.D0:0x11223344, Register.D1:0x55667788,
    Register.D4:0x11224455, Register.D5:0x33445566,
    Register.D6:0x66778899, Register.D7:0x13579bdf,
    Register.A1:0x6000, Register.A2:0x6100,
    Register.A4:0x6200, Register.A5:0x6300, Register.A6:0x6400,
}


def pixel_oracle(source,mask,left,width,shift,depth,original):
    out=[bytearray(p) for p in original]
    for bit in range(width):
        srcbit=0x8000 >> (left+bit)
        if not (mask & srcbit):
            continue
        pos=shift+bit
        byte,b=divmod(pos,8)
        bitmask=0x80 >> b
        for plane in range(depth):
            if source[plane] & srcbit:
                out[plane][byte] |= bitmask
            else:
                out[plane][byte] &= 255 ^ bitmask
    return out


def run_abi(cpu_type, *, flags, depth, left, width, shift,
            mask, mode=1, bank=11, rectw=16, recth=3):
    rng=Random(0x0a20d)
    words=[rng.randrange(65536) for _ in range(max(1,depth))]
    original=[bytearray(rng.randbytes(8)) for _ in range(max(1,depth))]
    m=Machine(cpu_type,256)
    try:
        mem,cpu=m.mem,m.cpu
        mem.w32(0,STACK)
        mem.w32(4,CODE)
        cpu.execute(cpu.pulse_reset())
        # SysBase is made available AFTER reset, not a reset vector.
        mem.w32(4,SYSBASE)
        mem.w16(SYSBASE+EXECBASE_ATTNFLAGS,flags)
        end=m.create_execute_end("opt020-p1d-return")
        trap_id=m.traps.alloc(lambda opcode,pc: end)
        mem.w16(TRAP,0xa000|trap_id)
        mem.w_block(CODE,emit_ap20_shaped_probe())
        mem.w_block(SRC,pack(">"+("H"*len(words)),*words))
        mem.w16(MASK,mask)
        for i,initial in enumerate(original):
            start=DEST+i*0x100
            mem.w_block(start,BEFORE+bytes(initial)+AFTER)
            mem.w32(PTRTABLE+4*i,start+8)
        for i,value in enumerate((0,0,recth,rectw,0,0,bank)):
            mem.w32(PARAMS+i*4,value)
        for i,v in enumerate((SRC,MASK,PTRTABLE,shift,left,width,depth)):
            mem.w32(DESCRIPTOR+i*4,v & 0xffffffff)
        mem.w32(STACK,TRAP)
        cpu.w_sp(STACK)
        cpu.w_pc(CODE)
        for reg,val in SAVED.items():
            cpu.w_reg(reg,val)
        cpu.w_reg(Register.A0,DESCRIPTOR)
        cpu.w_reg(Register.A3,PARAMS)
        cpu.w_reg(Register.D2,0xfeed1234)
        cpu.w_reg(Register.D3,mode)
        result=m.execute(30000)
        assert result.result is end, (
            cpu_type,flags,depth,left,width,shift,mode,
            cpu.r_pc(),result)
        assert cpu.r_sp()==STACK+4, (
            'SP IMBALANCE',cpu_type,flags,depth,left,width,shift,mode,
            hex(cpu.r_sp()),hex(cpu.r_pc()),hex(STACK+4),
            'D3',cpu.r_reg(Register.D3),
            'A3',hex(cpu.r_reg(Register.A3)))
        assert cpu.r_reg(Register.A3)==PARAMS+28
        assert cpu.r_reg(Register.D2)==0
        for reg,val in SAVED.items():
            assert cpu.r_reg(reg)==val,("ABI register changed",reg)
        assert cpu.r_reg(Register.A0)==DESCRIPTOR
        success=(
            (flags & (1 << AFF_68020_BIT)) != 0 and
            mode in (0,1) and bank>=5 and rectw>0 and recth>0 and
            1<=depth<=8 and 0<=left<=15 and
            1<=width<=16-left and 0<=shift<8)
        assert cpu.r_reg(Register.D3)==int(success),(
            "wrong ABI result",cpu_type,flags,depth,left,width,shift,mode,
            cpu.r_reg(Register.D3),success)
        expected=(pixel_oracle(words,mask,left,width,shift,depth,original)
                  if success else original)
        for i,initial in enumerate(expected):
            start=DEST+i*0x100
            actual=mem.r_block(start,8+len(initial)+8)
            assert actual[:8]==BEFORE and actual[-8:]==AFTER
            assert actual[8:-8]==bytes(initial),(
                "pixel/canary corruption",cpu_type,flags,depth,i)
        assert mem.r16(MASK)==mask
        return bool(success)
    finally:
        m.cleanup()


def cpu_tests():
    tests=passes=rejects=0
    # Confirm the pre-020 guard is executable on a true 68000.
    for cpu in (CPUType.M68000,CPUType.M68EC020,CPUType.M68020):
        for width,left,shift in ((1,0,0),(3,5,2),(8,4,7),(16,0,3),(1,15,7)):
            for depth in (1,2,4,8):
                for mask,mode in ((0xffff,0),(0xa55a,1)):
                    ok=run_abi(cpu,flags=0 if cpu==CPUType.M68000 else 2,
                               depth=depth,left=left,width=width,
                               shift=shift,mask=mask,mode=mode)
                    passes+=int(ok)
                    rejects+=int(not ok)
                    tests+=1
    for cpu in (CPUType.M68EC020,CPUType.M68020):
        for data in (
            dict(flags=0,depth=2,left=0,width=16,shift=0,mask=0xffff),
            dict(flags=2,depth=0,left=0,width=16,shift=0,mask=0xffff),
            dict(flags=2,depth=9,left=0,width=16,shift=0,mask=0xffff),
            dict(flags=2,depth=2,left=15,width=2,shift=0,mask=0xffff),
            dict(flags=2,depth=2,left=16,width=1,shift=0,mask=0xffff),
            dict(flags=2,depth=2,left=0,width=0,shift=0,mask=0xffff),
            dict(flags=2,depth=2,left=0,width=16,shift=8,mask=0xffff),
            dict(flags=2,depth=2,left=0,width=16,shift=0,mask=0xffff,mode=2),
            dict(flags=2,depth=2,left=0,width=16,shift=0,mask=0xffff,bank=4),
            dict(flags=2,depth=2,left=0,width=16,shift=0,mask=0xffff,rectw=0),
        ):
            assert not run_abi(cpu,**data)
            tests+=1
            rejects+=1
    return tests,passes,rejects


def ap20_v2_in_memory_probe():
    raw=(ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    current=(ROOT/"dist/AMOSPro_AGA.Lib").read_bytes()
    assert sha256(raw).hexdigest()==R68_SHA, "protected R68 LAST_GOOD changed"
    if current != raw:
        from build_opt020_p1e_r69 import build as build_r69
        from build_opt020_p2_r70 import build as build_r70
        candidate69, meta69 = build_r69()
        candidate70, meta70 = build_r70()
        assert current in (candidate69, candidate70), (
            "Current must be reproducible R69 or R70, not an unknown Lib")
        assert meta69["sha256"] == "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
        assert meta70["sha256"] == "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
    tokens, parts=unwrap_native_parts_v2(raw)
    original_tokens, segments,title=unpack_ap20(raw)
    assert tokens==original_tokens and len(parts)==len(segments)-1==70
    assert parts[59].endswith(GETP), "R60 region lacks GetP marker"
    adapter=emit_ap20_shaped_probe()
    trial=list(parts)
    trial[59]=adapter+GETP  # test-only replacement; NEVER SHIP
    source=repack_ap20(raw,tokens,trial,title)
    wrapped=wrap_native_ap20_v2(source,title)
    assert unwrap_native_parts_v2(wrapped)==(tokens,trial)
    t,new,title_again=unpack_ap20(wrapped)
    assert t==tokens and title_again==title
    assert new[-1].startswith(DISPATCH_V2)
    assert adapter in new[-1]
    assert len(new[-1])<=65534
    assert sha256((ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()).hexdigest()==R68_SHA
    return len(adapter),len(wrapped),len(new[-1]),len(parts)


def decode_check():
    code=emit_ap20_shaped_probe()
    # The last portion is native 020 (but all code BEFORE CPU guard is 000).
    dec=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
    ins=list(dec.disasm(code,CODE))
    names=[p.mnemonic.lower().split(".",1)[0] for p in ins]
    assert sum(p.size for p in ins)==len(code),names
    assert "btst" in names and "bfins" in names and "bfextu" in names
    assert names.count("rts")>=2
    assert code.startswith(bytes.fromhex("48e7efee"))
    assert bytes.fromhex("4cdf77f774004e75") in code
    # Before the first 020 opcode, ALL instructions must decode on 68000.
    from capstone import CS_MODE_M68K_000
    from opt020_p1d_fragment_emit import emit_fragment_020
    start = code.index(emit_fragment_020())
    pre_020 = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000).
                   disasm(code[:start],CODE))
    assert sum(item.size for item in pre_020)==start, (
        'CPU000-unsafe opcode before gate', [v.mnemonic for v in pre_020])
    return len(code),sha256(code).hexdigest()


def main():
    size,hashcode=decode_check()
    tests,success,rejects=cpu_tests()
    trial=ap20_v2_in_memory_probe()
    print("OPT020/P1d AP20-SHAPED 68000/EC020/020 CPU GUARD PASS:",
          tests,"calls",success,"successes",rejects,"failures",
          "preserved regs, A3+28, D2=0, D3=0/1, pixel/canaries intact")
    print("ABI SHAPE",size,"bytes SHA256",hashcode)
    print("IN-MEMORY COMPILER V2 AP20 STRUCTURAL ROUND TRIP PASS:",trial)
    print("NOT a working AMOS entry: synthetic A0 context; native R60 "
          "bank preflight, GetAdr, Safe, full API and Compiler Gate C "
          "remain to be integrated. No candidate file was created.")


if __name__=="__main__":
    main()
