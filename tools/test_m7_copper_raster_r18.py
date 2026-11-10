#!/usr/bin/env python3
"""R18 strict CPU Gate A: real emitted 68000 code + mocked AmigaOS calls.

This does NOT simulate the copper raster output, real Intuition ownership,
chip timing, AMOS Compiler or WinUAE. No runtime PASS before user screenshots.
"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import *

from audit_ap20 import inspect, parse
from ap20_utils import split, digest
from build_m7_copper_raster_r18 import (
    BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256, build,
    ENTRY_CLEAR, ENTRY_ON, ENTRY_OFF, ENTRY_WAIT, ENTRY_MOVE, ENTRY_END,
    SC_UCOPINS, SC_USERDATA, CL_COUNT, CL_MAX, CL_COPPTR,
    emit_on, emit_off, emit_append, emit_end, CINIT_2, CINIT_64,
)
from test_m7_copper_on_off_r17 import OnOffMachine
from test_m5_generic import (
    GFX, SCREEN, AMOS, STATE, CODE, STACK, STOP, DR, AR
)

COPINS = 0x360200
COPLIST = 0x360100


class RasterMachine(OnOffMachine):
    def __init__(self, raw, *, depth=8, fail_make=False, fail_rethink=False):
        super().__init__(raw, depth=depth, fail_make=fail_make,
                         fail_rethink=fail_rethink)
        self.uc.mem_write(GFX-372, b"\x4e\x75")  # CMove
        self.written = []
        self.cinit_capacity = []

    def putw(self, addr, value):
        self.uc.mem_write(addr, struct.pack(">H", value & 0xffff))

    def getw(self, addr):
        return struct.unpack(">H", self.uc.mem_read(addr, 2))[0]

    def os_call(self, uc, address, size, user):
        if address == GFX-594:
            self.call_counts["cinit"] += 1
            assert self.a(0) == self.cop_ptr
            self.cinit_capacity.append(self.d(0))
            assert self.d(0) == 64, "R18 Clear must reserve 64 instructions"
            self.coplist = COPLIST
            self.put(self.cop_ptr+4, COPLIST)
            self.put(self.cop_ptr+8, COPLIST)
            self.put(COPLIST+12, COPINS)
            self.put(COPLIST+16, COPINS)
            self.putw(COPLIST+28, 0)
            self.putw(COPLIST+30, 64)
            uc.mem_write(COPINS, bytes(64 * 6))
            result = COPLIST
        elif address == GFX-378 or address == GFX-372:
            if address == GFX-378:
                self.call_counts["cwait"] += 1
                op, arg1, arg2 = 1, self.d(0), self.d(1)
                assert (0 <= arg1 <= 255 and 0 <= arg2 <= 222) or (
                    arg1 == 10000 and arg2 == 255)
            else:
                op, arg1, arg2 = 0, self.d(0), self.d(1)
                assert 0xDFF180 <= arg1 <= 0xDFF1BE
                assert (arg1 & 1) == 0 and 0 <= arg2 <= 0xFFF
            assert self.a(1) == self.cop_ptr
            ptr = self.get(COPLIST+16)
            assert COPINS <= ptr < COPINS+64*6
            # graphics.library CMove accepts the absolute custom
            # register pointer, but records its $0180..$01BE Copper
            # register offset in CopIns.DestAddr.
            encoded = (arg1 & 0x1fe) if op == 0 else (arg1 & 0xffff)
            uc.mem_write(ptr, struct.pack(">HHH", op, encoded,
                                           arg2 & 0xffff))
            self.written.append((op, arg1, arg2))
            result = 0
        elif address == GFX-366:
            self.call_counts["cbump"] += 1
            assert self.a(1) == self.cop_ptr
            pos = self.get(COPLIST+16)
            count = self.getw(COPLIST+28)
            assert count < self.getw(COPLIST+30)
            assert COPINS <= pos < COPINS+64*6
            self.put(COPLIST+16, pos+6)
            self.putw(COPLIST+28, count+1)
            result = 0
        else:
            return super().os_call(uc, address, size, user)

        uc.reg_write(DR[0], result)
        uc.reg_write(DR[1], 0xDEADBEEF)
        uc.reg_write(AR[0], 0xBAD000)
        uc.reg_write(AR[1], 0xBAD100)
        pc = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC, pc)

    def call_api(self, entry, first=None, last=None):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x58000)
        if first is not None:
            self.put(0x58000, first)
            self.uc.reg_write(DR[3], last)
        saved = {r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[entry], STOP, count=250000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4
        for reg, value in saved.items():
            if reg in (DR[2], DR[3]):
                continue
            if reg == AR[3] and first is not None:
                assert self.uc.reg_read(reg) == value+4, (
                    "A3 must consume first arg on valid AND rejected calls")
                continue
            assert self.uc.reg_read(reg) == value, (
                "ABI", reg, hex(value), hex(self.uc.reg_read(reg)))
        assert self.d(2) == 0
        return self.d(3)

    def wait(self, v, h=0):
        return self.call_api(ENTRY_WAIT, v, h)

    def move(self, reg, color):
        return self.call_api(ENTRY_MOVE, reg, color)

    def end(self):
        return self.call_api(ENTRY_END)

    def on(self):
        return self.call_api(ENTRY_ON)

    def off(self):
        return self.call_api(ENTRY_OFF)

    def clear(self):
        return self.call_api(ENTRY_CLEAR)

    def logical_list(self):
        n = self.getw(COPLIST+28)
        items=[]
        for i in range(n):
            items.append(struct.unpack(">HHH",self.uc.mem_read(COPINS+i*6,6)))
        if n:
            assert items[-1] == (1,10000,255), "CEND missing"
        return items

    def count(self):
        return self.getw(COPLIST+28)


def run():
    lib, info = build()
    assert build()[0] == lib
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    _, old, _ = split(BASE.read_bytes())
    _, parts, _ = split(lib)
    assert len(old) == 25 and len(parts) == 28
    assert parts[:22] == old[:22], "M5/M6 unexpectedly modified"
    assert old[22].count(CINIT_2) == 1
    assert parts[22] == old[22].replace(CINIT_2, CINIT_64)
    assert parts[23] == emit_on()[0]+b"GetP"
    assert parts[24] == emit_off()[0]+b"GetP"
    assert parts[25] == emit_append("wait")[0]+b"GetP"
    assert parts[26] == emit_append("move")[0]
    assert parts[27] == emit_end()[0]
    audit = inspect(parse(lib))
    assert not audit["issues"], audit["issues"]
    for i,name,sig in ((25,"aga copper wait","00,0"),
                       (26,"aga copper move","00,0"),
                       (27,"aga copper end","0")):
        found=[x for x in audit["tokens"] if x["name"]==name]
        assert len(found)==1
        assert (found[0]["function"], found[0]["signature"])==(i,sig)
    dec = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    for i in (22,23,24,25,26,27):
        b=parts[i][:-4] if i in (22,23,24,25) else parts[i]
        # Clear already has the trailing GetP; remove only when present.
        inst=list(dec.disasm(b,0))
        assert sum(z.size for z in inst)==len(b), (i,len(b),inst[-3:])
        assert not any(z.mnemonic in ("illegal","dc.w") for z in inst)
    cases=0
    for depth in (1,2,4,8):
        m=RasterMachine(lib,depth=depth)
        assert m.wait(40,0)==0 and m.move(0x180,0xF00)==0
        assert m.end()==0 and m.on()==0
        assert m.clear()==1
        assert m.cinit_capacity==[64]
        assert m.count()==1 and m.logical_list()==[(1,10000,255)]
        assert m.wait(40,0)==1
        assert m.count()==2
        assert m.logical_list()==[(1,40,0),(1,10000,255)]
        assert m.move(0x180,0xF00)==1
        assert m.count()==3
        assert m.logical_list() == [(1,40,0),(0,0x180,0xF00),
                                    (1,10000,255)]
        assert m.wait(90,0)==1
        assert m.move(0x180,0x00F)==1
        assert m.wait(150,0)==1
        assert m.move(0x180,0x0F0)==1
        assert m.count()==7
        assert m.end()==1 and m.end()==0
        assert (m.get(SCREEN+SC_USERDATA)&3)==2
        assert m.wait(200,0)==0 and m.move(0x180,0xF00)==0
        assert m.on()==1 and m.on()==1
        assert (m.get(SCREEN+SC_USERDATA)&3)==3
        assert m.wait(220,0)==0 and m.move(0x180,0)==0
        assert m.off()==1 and m.off()==1
        assert m.get(SCREEN+SC_USERDATA)==0
        assert m.get(SCREEN+SC_UCOPINS)==0
        assert m.call_counts["free"]==1 and m.call_counts["freecop"]==1
        # R17's legacy Clear + On/Off without End remains supported.
        assert m.clear()==1 and m.on()==1 and m.off()==1
        assert m.call_counts["free"]==2
        cases+=1

    # Bounds, sequence order, invalid register and value: no mutations.
    m=RasterMachine(lib)
    assert m.clear()==1
    for v,h in ((-1,0),(256,0),(30,-1),(30,223),(65536,0)):
        assert m.wait(v,h)==0, (v,h)
        assert m.count()==1
        cases+=1
    for reg,val in ((0x17E,0xF00),(0x181,1),(0x1C0,0),
                    (0x096,1),(-1,2),(0x180,-1),(0x180,0x1000)):
        assert m.move(reg,val)==0,(reg,val)
        assert m.count()==1
        cases+=1
    assert m.wait(44,0)==1
    for v,h in ((44,0),(43,222),(44,-1)):
        assert m.wait(v,h)==0
        assert m.count()==2
        cases+=1
    assert m.move(0x182,0xF0F)==1
    assert m.wait(44,1)==1
    assert m.wait(45,0)==1
    assert m.on()==0, "unfinished raster must not be armed"
    assert m.end()==1
    assert m.on()==1 and m.off()==1
    cases+=1

    # Capacity: maximum 63 total user steps reserved with CEND at end.
    m=RasterMachine(lib)
    assert m.clear()==1
    for v in range(62):
        assert m.wait(v,0)==1,v
    assert m.wait(62,0)==0,"must reject overflow before any memory write"
    assert m.count()==63 and m.logical_list()[-1]==(1,10000,255)
    assert m.end()==1 and m.on()==1 and m.off()==1
    cases+=1

    # No writes on mismatched owner or post activation.
    for mode in ("foreign_ucop","foreign_userdata","mismatch"):
        m=RasterMachine(lib)
        assert m.clear()==1
        if mode=="foreign_ucop":m.put(SCREEN+SC_UCOPINS,0x99000)
        elif mode=="foreign_userdata":m.put(SCREEN+SC_USERDATA,0x98000)
        else:
            m.put(SCREEN+SC_USERDATA,0x98000)
            m.put(SCREEN+SC_UCOPINS,0x99000)
        before=m.get(SCREEN+SC_USERDATA),m.get(SCREEN+SC_UCOPINS)
        assert m.wait(30,0)==0 and m.move(0x180,0xF0)==0
        assert m.end()==0 and m.on()==0 and m.off()==0
        assert before==(m.get(SCREEN+SC_USERDATA),
                        m.get(SCREEN+SC_UCOPINS))
        cases+=1

    # An On failure conservatively keeps active mark until Off; no mutation.
    for kind in ("make","rethink"):
        m=RasterMachine(lib)
        assert m.clear()==1 and m.wait(50,0)==1 and m.end()==1
        if kind=="make":m.fail_make=True
        else:m.fail_rethink=True
        assert m.on()==0
        assert m.get(SCREEN+SC_USERDATA)&1
        assert m.move(0x180,0xF00)==0
        m.fail_make=m.fail_rethink=False
        assert m.off()==1 and m.call_counts["free"]==1
        cases+=1
    print("M7 R18 CPU PASS:",cases,"scenarios; 68000 ABI, A3+4,"
          " 64-slot CEND tail, no mutation while armed/sealed, strict"
          " WAIT/CMOVE whitelist, failure handling, intact M5/M6 segments")
    print("R18 candidate",info["size"],"SHA256",info["sha256"])
    print("Gates B/C/D: NOT TESTED (visual WinUAE/Compiler/Amiga)")
if __name__=="__main__":
    run()
