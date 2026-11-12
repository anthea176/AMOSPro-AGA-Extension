#!/usr/bin/env python3
"""R40 native 68000 Gate A: AP20, bounds, chipset BitMap, Safe and pixels.

Uses real Unicorn m68k-000 instructions and mocked Exec/graphics.library calls.
Not a WinUAE, AMOS Compiler or physical Amiga test.
"""
from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m15_plot_r40 import (build, BASE, BASE_SHA256, LAST_GOOD,
                               LAST_GOOD_SHA256, ENTRY_INDEX, GETP, API)
from m15_plot_r40_emit import emit_plot
from test_m6_blit_copy_r13 import CopyMachine
from test_m5_generic import CODE, GFX, EXEC, STATE, DB, BITMAP, STACK, STOP, AMOS, DR, AR

ARGS = 0x58000
SAFE_PORT = 0x59000
SAFE_MSG = 0x59100
LVOs = (GFX-198, GFX-342, GFX-354, GFX-324, GFX-228, EXEC-372)


class PlotMachine(CopyMachine):
    def __init__(self, binary, *, width=320, height=256, depth=8, front=0,
                 pending=0, safe_ready=False, pixel_ok=True):
        super().__init__(binary, width=width, height=height, depth=depth,
                         front=front)
        self.put(DB+12, SAFE_PORT)
        self.put(DB+16, SAFE_PORT+0x100)
        self.put(DB+20, pending)
        self.safe_ready = safe_ready
        self.pixel_ok = pixel_ok
        self.calls = []
        self.draws = []
        self.rp = None
        self.waits = 0
        for addr in LVOs:
            self.uc.mem_write(addr, bytes.fromhex("4e75"))

    def _ret(self, result=0):
        uc = self.uc
        uc.reg_write(DR[0], result & 0xffffffff)
        uc.reg_write(DR[1], 0xdeadbeef)
        uc.reg_write(AR[0], 0xbad000)
        uc.reg_write(AR[1], 0xbad100)
        pc = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC, pc)

    def os_call(self, uc, address, size, user):
        if address not in LVOs:
            raise AssertionError("unexpected OS LVO: "+hex(address))
        self.calls.append(address)
        if address == EXEC-372:
            assert self.a(0) == SAFE_PORT
            assert self.get(DB+20) & 1
            self._ret(SAFE_MSG if self.safe_ready else 0)
        elif address == GFX-198:
            assert STACK-512 <= self.a(1) < STACK-128
            self.rp = self.a(1)
            uc.mem_write(self.rp, bytes(128))
            self._ret()
        elif address == GFX-342:
            assert self.a(1) == self.rp
            assert self.get(self.a(1)+4) == self.expected_bitmap
            assert self.d(0) == self.pen
            self._ret()
        elif address == GFX-354:
            assert self.a(1) == self.rp
            assert self.d(0) == 0, "JAM1/copy expected"
            self._ret()
        elif address == GFX-324:
            assert self.calls[-4:] == [GFX-198, GFX-342, GFX-354, GFX-324] or (
                self.calls[-5:] == [EXEC-372, GFX-198, GFX-342, GFX-354, GFX-324])
            assert self.a(1) == self.rp
            assert self.get(self.a(1)+4) == self.expected_bitmap
            assert (self.d(0), self.d(1)) == (self.x, self.y)
            assert 0 <= self.x < self.meta["width"]
            assert 0 <= self.y < self.meta["height"]
            self.draws.append((self.x, self.y, self.pen))
            if self.pixel_ok:
                offset = self.y*self.stride + (self.x>>3)
                mask = 1 << (7-(self.x & 7))
                for plane, pointer in enumerate(self.planes):
                    previous = uc.mem_read(pointer+offset, 1)[0]
                    value = (previous | mask) if self.pen & (1<<plane) else (previous & (255 ^ mask))
                    uc.mem_write(pointer+offset, bytes([value]))
            self._ret(0 if self.pixel_ok else -1)
        elif address == GFX-228:
            assert len(self.draws) == 1
            self.waits += 1
            self._ret()

    def plot(self, x=24, y=32, pen=1):
        self.x, self.y, self.pen = x, y, pen
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], ARGS)
        self.put(ARGS, y)
        self.put(ARGS+4, x)
        self.uc.reg_write(DR[3], pen & 0xffffffff)
        saved = {reg: self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX], STOP, count=100000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4, "SP changed"
        assert self.a(3) == ARGS+8, "A3 GetP consumption wrong"
        for reg, old in saved.items():
            if reg not in (DR[2], DR[3], AR[3]):
                assert self.uc.reg_read(reg) == old, ("register clobbered", reg)
        assert self.d(2) == 0
        assert self.waits == len(self.draws)
        return self.d(3)


def run():
    raw, info = build()
    assert build()[0] == raw
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok0, seg0, _ = split(BASE.read_bytes())
    tok1, seg1, _ = split(raw)
    assert len(seg0) == ENTRY_INDEX == 50 and len(seg1) == 51
    assert seg1[:49] == seg0[:49]
    assert seg1[49] == seg0[49]+GETP
    assert seg1[50] == emit_plot()[0]
    assert tok1.startswith(tok0[:-6]) and tok1 != tok0
    audited = inspect(parse(raw))
    assert not audited["issues"], audited["issues"]
    named = [x for x in audited["tokens"] if x["name"].startswith("aga ")]
    assert len(named) == 45
    matches = [x for x in named if x["name"] == API[0][0]]
    assert len(matches) == 1
    assert (matches[0]["instruction"],matches[0]["function"],
            matches[0]["signature"]) == (1,ENTRY_INDEX,"00,0,0")
    assert any(x["index"]==50 and x["parameters"]==3 and x["getp"]
               for x in audited["parameter_checks"])
    code, labels = emit_plot()
    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    instructions = list(dis.disasm(code, 0))
    assert sum(x.size for x in instructions) == len(code), "68000 disassembly invalid"
    boundaries = {x.address for x in instructions}
    assert all(v in boundaries for v in labels.values()), labels
    assert all(x.mnemonic not in ("illegal","dc.w","trap") for x in instructions)

    cases = 0
    for depth in (1, 2, 4, 8):
        for front in (0, 1):
            for pending, ready in ((0,False),(1,True),(2,False),(3,True)):
                for x, y in ((0,0),(319,255),(24,32)):
                    for pen in (0,(1<<depth)-1):
                        m = PlotMachine(raw, depth=depth, front=front,
                                        pending=pending, safe_ready=ready)
                        before = m.snapshot()
                        assert m.plot(x,y,pen)==1
                        assert m.draws == [(x,y,pen)]
                        assert m.waits == 1
                        assert m.get(DB+20) == (pending & ~1)
                        assert m.calls.count(EXEC-372)==int(bool(pending&1))
                        assert m.calls[-2:] == [GFX-324, GFX-228]
                        after = m.snapshot()
                        off = y*m.stride + (x>>3)
                        mask = 1 << (7-(x&7))
                        for n in range(depth):
                            assert all(before[n][j] == after[n][j]
                                       for j in range(len(before[n])) if j != off)
                            assert ((after[n][off] & mask)!=0) == bool(pen & (1<<n))
                        cases += 1

    for args in (
        dict(x=-1),dict(y=-1),dict(x=320),dict(y=256),
        dict(pen=-1),dict(pen=256),dict(x=-2147483648),
        dict(y=2147483647),dict(x=2147483647),dict(pen=2147483647),
    ):
        m=PlotMachine(raw)
        snapshot=m.snapshot()
        assert m.plot(**args)==0,args
        assert not m.draws and m.snapshot()==snapshot,args
        cases+=1

    for pending in (1,3):
        m=PlotMachine(raw,pending=pending,safe_ready=False)
        snapshot=m.snapshot()
        assert m.plot()==0
        assert m.calls==[EXEC-372]
        assert m.get(DB+20)==pending
        assert m.snapshot()==snapshot
        cases+=1
    m=PlotMachine(raw,pending=1,safe_ready=True)
    m.put(DB+12,0)
    assert m.plot()==0 and not m.calls
    assert m.get(DB+20)==1
    cases+=1

    for mutant in ("screen","gfx","db","width","height","depth","front",
                   "sb0","sb1","bitmap","stride","rows","bmpdepth","plane","planem1"):
        m=PlotMachine(raw)
        if mutant=="screen":m.put(STATE,0)
        if mutant=="gfx":m.put(STATE+8,0)
        if mutant=="db":m.put(STATE+32,0)
        if mutant=="width":m.put(STATE+12,0)
        if mutant=="height":m.put(STATE+16,0)
        if mutant=="depth":m.put(STATE+28,9)
        if mutant=="front":m.put(DB+8,2)
        if mutant=="sb0":m.put(DB,0);m.put(DB+8,1)
        if mutant=="sb1":m.put(DB+4,0)
        if mutant=="bitmap":m.put(0x54100,0)
        if mutant=="stride":m.uc.mem_write(m.expected_bitmap,pack(">H",1))
        if mutant=="rows":m.uc.mem_write(m.expected_bitmap+2,pack(">H",1))
        if mutant=="bmpdepth":m.uc.mem_write(m.expected_bitmap+5,bytes([7]))
        if mutant=="plane":m.put(m.expected_bitmap+8,0)
        if mutant=="planem1":m.put(m.expected_bitmap+8,-1)
        snapshot=m.snapshot()
        assert m.plot()==0,mutant
        assert not m.draws and m.snapshot()==snapshot,mutant
        cases+=1

    m=PlotMachine(raw,pixel_ok=False)
    before=m.snapshot()
    assert m.plot()==0
    assert len(m.draws)==1 and m.waits==1
    assert m.snapshot()==before
    cases+=1
    print("M15/R40 native CPU 68000 Gate A PASS:",cases,"cases")
    print("AP20 45 commands / 51 segments; R38 original entries unchanged")
    print("Gate B WinUAE / C Compiler / D real Amiga: NOT TESTED")
    print("in-memory candidate SHA256:",info["sha256"],"bytes:",info["size"])


if __name__=="__main__":
    run()
