#!/usr/bin/env python3
"""P1: execute TWO physically separate AP20 V2 native units on MC68020.

This is an isolated CPU gate, NOT an actual AMOS Compiler / WinUAE gate.
The R82 binary, AP20 API, and current AMOS test are never rewritten.
"""
from __future__ import annotations

from pathlib import Path
from struct import pack, unpack_from
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from compiler_relocation import unpack_ap20 as production_parser
from ap20_v3_multiunit_probe import (
    DISPATCH_V2, MAX_UNIT, NOP, RBSR, RTS, TITLE, TOKENS,
    pack_ap20, template, unpack_ap20, wrap_multiunit, unwrap_multiunit,
)

GROUP_BASES = {4: 0x100000, 5: 0x220000}
STOP = 0x20000
STACK = 0x500000
# EXTB.L D3 is MC68020+ only (opcode 49C3).
EXTB_L_D3 = bytes.fromhex("49c3")
M68K020_OP = bytes.fromhex("760149c34e75")


def native_routine(value: int, length: int) -> bytes:
    if not (0 <= value <= 127) or length < 6 or length & 1:
        raise ValueError("Invalid synthetic MC68020 routine")
    return bytes((0x76, value)) + EXTB_L_D3 + RTS + NOP * ((length - 6) // 2)


def independent_fixture():
    bodies = [
        native_routine(17, 40000),
        native_routine(34, 6),
        native_routine(51, 42000),
        native_routine(68, 6),
    ]
    raw = pack_ap20(template(), TOKENS, bodies, TITLE)
    wrapped, layout = wrap_multiunit(raw, (2,), independent_test_only=True)
    return raw, wrapped, layout, bodies


def compiler_link_stub(stub: bytes, stub_address: int, *, absolute: bool) -> tuple[bytes, int]:
    """Model the compiler-resolved RBSR as BSR.W or a far absolute JSR.

    This exercises the native dispatcher at runtime; it DOES NOT claim
    byte-for-byte equivalence to actual +APComp.s output.
    """
    if len(stub) != 8 or stub[:2] != RBSR or stub[6:] != RTS:
        raise ValueError("Not an AP20 RBSR/RTS bridge stub")
    group, offset = unpack_from(">HH", stub, 2)
    if group not in GROUP_BASES or offset & 1:
        raise ValueError("Invalid group/offset")
    addr = GROUP_BASES[group]
    if absolute:
        return b"\x4e\xb9" + pack(">I", addr) + pack(">H", offset) + RTS, offset
    # 68k BSR.W displacement is relative to the opcode's PC+2,
    # not to the word following its 16-bit extension.
    displacement = addr - (stub_address + 2)
    if not -32768 <= displacement <= 32767:
        raise ValueError("Near BSR.W cannot reach unit")
    return b"\x61\x00" + pack(">h", displacement) + pack(">H", offset) + RTS, offset


def simulate_cpu020(wrapped: bytes, routine_index: int, *, absolute: bool) -> dict:
    try:
        from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
        from unicorn.m68k_const import (
            UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR,
            UC_M68K_REG_A7, UC_M68K_REG_A0, UC_M68K_REG_D0,
            UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_A5,
        )
    except ImportError as exc:
        raise RuntimeError("MC68020 CPU proof requires unicorn==2.1.4") from exc

    _, segments, _ = unpack_ap20(wrapped)
    assert len(segments) == 6
    stub = segments[routine_index]
    group, off = unpack_from(">HH", stub, 2)
    unit_address = GROUP_BASES[group]
    stub_address = (0x70000 if absolute else unit_address - 0x100)
    link, offset = compiler_link_stub(stub, stub_address, absolute=absolute)

    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68020)
    cpu.mem_map(0, 0x600000)
    cpu.mem_write(STOP, NOP)
    cpu.mem_write(stub_address, link)
    for i, dest in enumerate((4, 5)):
        cpu.mem_write(GROUP_BASES[dest], segments[dest])
    cpu.mem_write(STACK, pack(">I", STOP))

    sentinel = {
        UC_M68K_REG_A0: 0x12f040,
        UC_M68K_REG_A5: 0x21a050,
        UC_M68K_REG_D0: 0x33445566,
        UC_M68K_REG_D2: 0x778899aa,
    }
    for reg, val in sentinel.items():
        cpu.reg_write(reg, val)
    cpu.reg_write(UC_M68K_REG_D3, 0)
    cpu.reg_write(UC_M68K_REG_SR, 0x2000)
    cpu.reg_write(UC_M68K_REG_A7, STACK)

    expected_pc = unit_address + len(DISPATCH_V2) + offset
    visited = []
    def trace(_cpu, pc, _size, _data):
        if pc == expected_pc:
            visited.append(pc)
    cpu.hook_add(UC_HOOK_CODE, trace)
    cpu.emu_start(stub_address, STOP, count=300)

    if cpu.reg_read(UC_M68K_REG_PC) != STOP:
        raise AssertionError("Failed return to caller")
    if cpu.reg_read(UC_M68K_REG_A7) != STACK + 4:
        raise AssertionError("Invalid stack after dispatcher and target returns")
    if visited != [expected_pc]:
        raise AssertionError(("Wrong native entry executed", visited, hex(expected_pc)))
    for reg, val in sentinel.items():
        if cpu.reg_read(reg) != val:
            raise AssertionError(("ABI register modified", reg))
    if cpu.mem_read(unit_address, len(segments[group])) != bytes(segments[group]):
        raise AssertionError("Native code overwritten")
    return {"D3": cpu.reg_read(UC_M68K_REG_D3), "PC": expected_pc, "group": group}


class TwoNativeUnitCPU020(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.wrapped, cls.layout, cls.bodies = independent_fixture()

    def test_two_groups_over_64k_real_ap20_reader(self):
        self.assertEqual(self.layout.total_native, 82012)
        self.assertEqual(self.layout.unit_sizes, (40040, 42040))
        self.assertEqual(self.layout.bridges, (4, 4, 5, 5))
        self.assertEqual(self.layout.offsets, (0, 40000, 0, 42000))
        self.assertEqual(sum(self.layout.unit_sizes), 82080)
        self.assertTrue(all(x <= MAX_UNIT for x in self.layout.unit_sizes))
        self.assertEqual(production_parser(self.wrapped),
                         unpack_ap20(self.wrapped))
        self.assertEqual(unwrap_multiunit(self.wrapped, (2,)), self.bodies)

    def test_four_entries_near_bsr_on_mc68020(self):
        for i, expected in enumerate((17, 34, 51, 68)):
            with self.subTest(i=i):
                result = simulate_cpu020(self.wrapped, i, absolute=False)
                self.assertEqual((result["D3"], result["group"]),
                                 (expected, 4 if i < 2 else 5))

    def test_four_entries_far_jsr_on_mc68020(self):
        for i, expected in enumerate((17, 34, 51, 68)):
            with self.subTest(i=i):
                result = simulate_cpu020(self.wrapped, i, absolute=True)
                self.assertEqual((result["D3"], result["group"]),
                                 (expected, 4 if i < 2 else 5))

    def test_020_opcodes_actually_present(self):
        for b in self.bodies:
            self.assertEqual(b[2:4], EXTB_L_D3)
            self.assertEqual(b[4:6], RTS)
        from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
        dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
        insn = list(dis.disasm(self.bodies[2][:6], 0))
        self.assertEqual(sum(i.size for i in insn), 6)
        self.assertTrue(any(i.mnemonic.lower().startswith("extb") for i in insn),
                        [(i.mnemonic, i.op_str) for i in insn])

    def test_near_bsr_pc_base_is_opcode_plus_two(self):
        _, segments, _ = unpack_ap20(self.wrapped)
        stub = GROUP_BASES[4] - 0x100
        link, _ = compiler_link_stub(segments[0], stub, absolute=False)
        self.assertEqual(link[:4], bytes.fromhex("610000fe"))
        self.assertEqual(stub + 2 + unpack_from(">h", link, 2)[0],
                         GROUP_BASES[4])

    def test_far_link_must_be_explicit(self):
        _, seg, _ = unpack_ap20(self.wrapped)
        with self.assertRaises(ValueError):
            compiler_link_stub(seg[2], 0x70000, absolute=False)

    def test_refuses_caller_without_proven_independence(self):
        with self.assertRaises(ValueError):
            wrap_multiunit(self.source, (2,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
