#!/usr/bin/env python3
"""Execute R16 Copper Clear native 68000 entry against OS-call mocks.

Gate A CPU/ABI/ownership only; no assertion about real Intuition memory
management or WinUAE is made without an actual AMOS runtime observation.
"""
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import *
from unicorn import UC_HOOK_CODE

from audit_ap20 import inspect, parse
from ap20_utils import digest, split
from build_m7_copper_clear_r16 import (
    BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY, SC_UCOPINS, SC_USERDATA, UCOP_SIZE, build, emit_clear,
)
from test_m5_generic import (
    Machine, EXEC, GFX, STATE, SCREEN, AMOS, CODE, STACK, STOP, DR, AR
)


class CopperMachine(Machine):
    def __init__(self, raw, *, depth=8, fail_alloc=False,
                 fail_cinit=False, partial_cinit=False):
        self.fail_alloc = fail_alloc
        self.fail_cinit = fail_cinit
        self.partial_cinit = partial_cinit
        self.call_counts = dict(alloc=0, free=0, cinit=0, cwait=0,
                                cbump=0, freecop=0)
        meta = dict(width=320, height=256, depth=depth,
                    row_bytes=40, camg=0x00021000)
        super().__init__(raw, data=None, meta=meta)
        for base, offsets in (
            (EXEC, (-198, -210)),
            (GFX, (-594, -378, -366, -546))
        ):
            for offset in offsets:
                self.uc.mem_write(base+offset, b"\x4e\x75")
        self.cop_ptr = 0
        self.coplist = 0
        self.alloc_failure = False

    def os_call(self, uc, address, size, user):
        result = 0
        if address == EXEC-198:
            self.call_counts["alloc"] += 1
            assert self.d(0) == UCOP_SIZE
            assert self.d(1) == 0x10001, "MEMF_PUBLIC | MEMF_CLEAR"
            if not self.fail_alloc:
                result = 0x360000
                self.cop_ptr = result
                self.uc.mem_write(result, b"\0"*UCOP_SIZE)
        elif address == GFX-594:
            self.call_counts["cinit"] += 1
            assert self.a(0) == self.cop_ptr
            assert self.d(0) == 2
            if not self.fail_cinit or self.partial_cinit:
                self.coplist = 0x360100
                self.put(self.cop_ptr + 4, self.coplist)
                self.put(self.cop_ptr + 8, self.coplist)
            result = 0 if self.fail_cinit else self.coplist
        elif address == GFX-378:
            self.call_counts["cwait"] += 1
            assert self.a(1) == self.cop_ptr
            assert self.d(0) == 10000 and self.d(1) == 255
            assert self.coplist
        elif address == GFX-366:
            self.call_counts["cbump"] += 1
            assert self.a(1) == self.cop_ptr
            assert self.call_counts["cwait"] == self.call_counts["cbump"]
        elif address == GFX-546:
            self.call_counts["freecop"] += 1
            assert self.a(0) == self.coplist
            self.coplist = 0
        elif address == EXEC-210:
            self.call_counts["free"] += 1
            assert self.a(1) == self.cop_ptr
            assert self.d(0) == UCOP_SIZE
            self.cop_ptr = 0
        else:
            raise AssertionError("Unexpected call in Copper Clear: " + hex(address))

        uc.reg_write(DR[0], result)
        uc.reg_write(DR[1], 0xDEADBEEF)
        uc.reg_write(AR[0], 0xBAD000)
        uc.reg_write(AR[1], 0xBAD100)
        pc = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC, pc)

    def run_clear(self):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x58000)
        saved = {r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY], STOP, count=250000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4
        for reg, value in saved.items():
            if reg in (DR[2], DR[3]):
                continue
            assert self.uc.reg_read(reg) == value, (
                reg, value, self.uc.reg_read(reg))
        assert self.d(2) == 0
        assert self.a(3) == 0x58000, "No-parameter command must leave A3 alone"
        return self.d(3)

    def fake_intuition_close(self):
        """Model the system's documented Intuition CloseScreen cleanup."""
        if (ucl:=self.get(SCREEN+SC_UCOPINS)):
            assert self.get(SCREEN+SC_USERDATA) == ucl
            assert ucl == self.cop_ptr
            assert self.coplist != 0
            self.coplist = 0
            self.cop_ptr = 0
        self.put(SCREEN+SC_UCOPINS, 0)
        self.put(SCREEN+SC_USERDATA, 0)


def run():
    binary, details = build()
    assert build()[0] == binary
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    _, old, _ = split(BASE.read_bytes())
    _, new, _ = split(binary)
    assert len(old) == ENTRY and len(new) == ENTRY+1
    assert new[:ENTRY] == old
    assert new[ENTRY] == emit_clear()[0]
    audit = inspect(parse(binary))
    assert not audit["issues"], audit["issues"]
    matches = [x for x in audit["tokens"] if x["name"] == "aga copper clear"]
    assert len(matches) == 1
    assert (matches[0]["instruction"], matches[0]["function"],
            matches[0]["signature"]) == (1, ENTRY, "0")

    disasm = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN |
                     CS_MODE_M68K_000).disasm(new[ENTRY], 0))
    assert sum(x.size for x in disasm) == len(new[ENTRY])
    assert not any(x.mnemonic in ("dc.w", "illegal") for x in disasm)
    assert not any(x.mnemonic == "move" and "dff" in x.op_str.lower()
                   for x in disasm), "No direct chipset writes"

    cases = 0
    for depth in (1, 2, 4, 8):
        m = CopperMachine(binary, depth=depth)
        assert m.run_clear() == 1
        assert m.get(SCREEN+SC_UCOPINS) == m.get(SCREEN+SC_USERDATA) == m.cop_ptr
        assert m.call_counts == dict(alloc=1, free=0, cinit=1,
                                    cwait=1, cbump=1, freecop=0)
        assert m.run_clear() == 1  # explicitly idempotent on already empty list
        assert m.call_counts["alloc"] == m.call_counts["cinit"] == 1
        m.fake_intuition_close()
        assert m.get(SCREEN+SC_UCOPINS) == 0
        assert m.get(SCREEN+SC_USERDATA) == 0
        cases += 1

    for mode in ("state", "screen", "gfx", "foreign_ucop",
                 "foreign_userdata", "mismatch"):
        m = CopperMachine(binary)
        if mode == "state": m.put(AMOS+456, 0)
        elif mode == "screen": m.put(STATE, 0)
        elif mode == "gfx": m.put(STATE+8, 0)
        elif mode == "foreign_ucop": m.put(SCREEN+SC_UCOPINS, 0x9A000)
        elif mode == "foreign_userdata": m.put(SCREEN+SC_USERDATA, 0x9B000)
        else:
            m.put(SCREEN+SC_UCOPINS, 0x9A000)
            m.put(SCREEN+SC_USERDATA, 0x9B000)
        uc_before = m.get(SCREEN+SC_UCOPINS)
        ud_before = m.get(SCREEN+SC_USERDATA)
        assert m.run_clear() == 0, mode
        assert m.get(SCREEN+SC_UCOPINS) == uc_before
        assert m.get(SCREEN+SC_USERDATA) == ud_before
        assert not m.call_counts["alloc"]
        cases += 1

    for alloc, cinit, partial in ((True, False, False),
                                 (False, True, False),
                                 (False, True, True)):
        m = CopperMachine(binary, fail_alloc=alloc,
                          fail_cinit=cinit, partial_cinit=partial)
        assert m.run_clear() == 0
        assert not m.get(SCREEN+SC_UCOPINS)
        assert not m.get(SCREEN+SC_USERDATA)
        if alloc:
            assert m.call_counts["alloc"] == 1
            assert m.call_counts["free"] == 0
        else:
            assert m.call_counts["free"] == 1
            assert m.call_counts["freecop"] == (1 if partial else 0)
        assert m.cop_ptr == 0
        assert m.coplist == 0
        cases += 1

    print("M7 R16 CPU PASS: %d lifecycle/invalid/low-memory scenarios; "
          "registers, stack, no A3 consumption, allocation, ownership, "
          "no foreign list overwrite, no DMA, prior 22 entries unchanged"
          % cases)
    print("R16 candidate", details["size"], "SHA256", details["sha256"])
    print("Intuition real cleanup / AMOS WinUAE / Compiler / hardware: NOT TESTED")


if __name__ == "__main__":
    run()
