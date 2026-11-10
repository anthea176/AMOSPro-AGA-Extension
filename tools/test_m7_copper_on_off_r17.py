#!/usr/bin/env python3
"""M7 R17 CPU gate: native Copper On / Off with Intuition OS-call mocks.

Tests preserve R16 0.8.0 byte-for-byte (except AP20 separator). Real
Intuition, DMA, AMOS interpreter/compiler and WinUAE are NOT simulated.
"""
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import *

from audit_ap20 import inspect, parse
from ap20_utils import digest, split
from build_m7_copper_on_off_r17 import (
    BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY_ON, ENTRY_OFF, SC_UCOPINS, SC_USERDATA,
    INTUI_MAKESCREEN, INTUI_RETHINK, GFX_FREECOPLIST,
    GFX_WAITTOF, EXEC_FREEMEM, emit_on, emit_off, build,
)
from test_m7_copper_clear_r16 import CopperMachine
from test_m5_generic import (
    EXEC, GFX, INTUI, SCREEN, AMOS, STATE, CODE, STACK, STOP, DR, AR
)


class OnOffMachine(CopperMachine):
    def __init__(self, raw, *, depth=8, fail_make=False, fail_rethink=False):
        super().__init__(raw, depth=depth)
        self.fail_make = fail_make
        self.fail_rethink = fail_rethink
        self.make_calls = 0
        self.rethink_calls = 0
        self.wait_tof = 0
        for offset in (INTUI_MAKESCREEN, INTUI_RETHINK):
            self.uc.mem_write(INTUI+offset, b"\x4e\x75")
        self.uc.mem_write(GFX+GFX_WAITTOF, b"\x4e\x75")

    def os_call(self, uc, address, size, user):
        if address not in (INTUI+INTUI_MAKESCREEN,
                           INTUI+INTUI_RETHINK, GFX+GFX_WAITTOF):
            return super().os_call(uc, address, size, user)
        result = 0
        if address == INTUI+INTUI_MAKESCREEN:
            self.make_calls += 1
            assert self.a(0) == SCREEN, "Must rebuild owned Screen only"
            result = 1 if self.fail_make else 0
        elif address == INTUI+INTUI_RETHINK:
            self.rethink_calls += 1
            result = 1 if self.fail_rethink else 0
        else:
            self.wait_tof += 1
            assert self.get(SCREEN+SC_UCOPINS) == 0, (
                "WaitTOF must occur after detach & display rebuild")
        uc.reg_write(DR[0], result)
        uc.reg_write(DR[1], 0xDEADBEEF)
        uc.reg_write(AR[0], 0xBAD000)
        uc.reg_write(AR[1], 0xBAD100)
        pc = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC, pc)

    def run_api(self, entry):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x58000)
        saved = {reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[entry], STOP, count=300000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4, "SP imbalance"
        for reg, value in saved.items():
            if reg in (DR[2], DR[3]):
                continue
            assert self.uc.reg_read(reg) == value, (
                "register changed", reg, value, self.uc.reg_read(reg))
        assert self.d(2) == 0 and self.a(3) == 0x58000
        return self.d(3)

    def on(self):
        return self.run_api(ENTRY_ON)

    def off(self):
        return self.run_api(ENTRY_OFF)


def run():
    lib, report = build()
    assert lib == build()[0]
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    _, original, _ = split(BASE.read_bytes())
    _, new, _ = split(lib)
    assert len(original) == ENTRY_ON and len(new) == ENTRY_OFF+1
    assert new[:ENTRY_ON-1] == original[:ENTRY_ON-1]
    assert new[ENTRY_ON-1] == original[ENTRY_ON-1]+b"GetP"
    assert new[ENTRY_ON] == emit_on()[0]+b"GetP"
    assert new[ENTRY_OFF] == emit_off()[0]
    audit = inspect(parse(lib))
    assert not audit["issues"], audit["issues"]
    for name, index in (("aga copper on", ENTRY_ON),
                        ("aga copper off", ENTRY_OFF)):
        tok = [t for t in audit["tokens"] if t["name"] == name]
        assert len(tok) == 1
        assert (tok[0]["instruction"], tok[0]["function"],
                tok[0]["signature"]) == (1, index, "0")

    decoder = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    for body in (emit_on()[0], emit_off()[0]):
        decoded = list(decoder.disasm(body, 0))
        assert sum(i.size for i in decoded) == len(body)
        assert not any(i.mnemonic in ("illegal", "dc.w") for i in decoded)

    cases = 0
    for depth in (1, 2, 4, 8):
        m = OnOffMachine(lib, depth=depth)
        assert m.on() == 0 and m.off() == 1, "Uninitialized calls"
        assert m.make_calls == m.rethink_calls == 0
        assert m.run_clear() == 1
        ptr = m.cop_ptr
        assert ptr == m.get(SCREEN+SC_UCOPINS) == m.get(SCREEN+SC_USERDATA)
        assert m.on() == 1
        assert m.make_calls == m.rethink_calls == 1
        assert m.on() == 1, "Reapplying On is allowed, without new alloc"
        assert m.make_calls == m.rethink_calls == 2
        assert m.off() == 1
        assert m.get(SCREEN+SC_UCOPINS) == 0
        assert m.get(SCREEN+SC_USERDATA) == 0
        assert m.call_counts["freecop"] == 1
        assert m.call_counts["free"] == 1
        assert m.cop_ptr == m.coplist == 0
        assert m.wait_tof == 1
        assert m.on() == 0 and m.off() == 1
        assert m.call_counts["free"] == 1, "No double-free"
        assert m.run_clear() == 1, "Reinitialize on the SAME screen"
        assert m.on() == 1 and m.off() == 1
        assert m.call_counts["free"] == 2
        cases += 1

    # Foreign list or UserData, mismatches and missing runtime dependencies
    # must not change pointer ownership or free anything.
    for case in ("state", "screen", "intuition", "graphics",
                 "foreign_ucop", "foreign_userdata", "mismatch"):
        m = OnOffMachine(lib)
        if case == "state": m.put(AMOS+456, 0)
        elif case == "screen": m.put(STATE, 0)
        elif case == "intuition": m.put(STATE+4, 0)
        elif case == "graphics": m.put(STATE+8, 0)
        elif case == "foreign_ucop": m.put(SCREEN+SC_UCOPINS, 0x99000)
        elif case == "foreign_userdata": m.put(SCREEN+SC_USERDATA, 0x98000)
        elif case == "mismatch":
            m.put(SCREEN+SC_UCOPINS, 0x99000)
            m.put(SCREEN+SC_USERDATA, 0x98000)
        a = m.get(SCREEN+SC_UCOPINS)
        b = m.get(SCREEN+SC_USERDATA)
        assert m.on() == 0, case
        # Off with no existing lists and missing graphics/intuition can
        # legitimately return 1: no OS calls are needed for empty state.
        off = m.off()
        if case in ("foreign_ucop", "foreign_userdata", "mismatch",
                    "state", "screen"):
            assert off == 0, case
        assert m.get(SCREEN+SC_UCOPINS) == a
        assert m.get(SCREEN+SC_USERDATA) == b
        assert m.make_calls == m.rethink_calls == 0
        assert m.call_counts["free"] == m.call_counts["freecop"] == 0
        cases += 1

    for failure in ("on_make", "on_rethink", "off_make", "off_rethink"):
        m = OnOffMachine(lib)
        assert m.run_clear() == 1
        ptr = m.cop_ptr
        if failure.startswith("off"):
            assert m.on() == 1
        if failure.endswith("make"):
            m.fail_make = True
        else:
            m.fail_rethink = True
        assert (m.on() if failure.startswith("on") else m.off()) == 0
        assert m.get(SCREEN+SC_UCOPINS) == ptr
        assert m.get(SCREEN+SC_USERDATA) == ptr
        assert m.cop_ptr == ptr and m.coplist != 0
        assert m.call_counts["free"] == m.call_counts["freecop"] == 0
        m.fail_make = m.fail_rethink = False
        assert m.off() == 1
        assert m.call_counts["free"] == m.call_counts["freecop"] == 1
        cases += 1

    print("M7 R17 CPU PASS: %d cases; On/Off 68000 registers/SP/A3,"
          " Intuition MakeScreen/RethinkDisplay, owner-only free,"
          " repeated calls, failure rollback, R16 entries unchanged"
          % cases)
    print("R17 candidate", report["size"], "SHA256", report["sha256"])
    print("AMOS interpreted WinUAE, Compiler and real Amiga: NOT TESTED")


if __name__ == "__main__":
    run()
