#!/usr/bin/env python3
"""M19 P2.2 fourth AP20 group Gate A: actual MC68020 dispatcher and probe ABI.

The witness is not Aga Bob Batch and does not draw. All testing stays in
memory; only the independent build command may export a disposable .Lib.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'experiments'))

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_A3, UC_M68K_REG_A7,
    UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2,
    UC_M68K_REG_D3, UC_M68K_REG_D4, UC_M68K_REG_PC,
    UC_M68K_REG_SR,
)

from active_library import R84_SHA
from audit_ap20 import inspect, parse
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import starts, interpreter_rbsr_displacements, assert_reaches_entry_on_mc68020
from build_m19_p22_fourth_unit_probe import (
    ACTIVE, PROTECTED, PROBE_CODE, TITLE, NEW_FUNCTION,
    GROUP_C2P, GROUP_IFF, GROUP_AGA, GROUP_BOBS, BASE_PUBLIC,
    build,
)


class FourUnitProbeGateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.metadata = build()
        cls.original = PROTECTED.read_bytes()
        cls.tok, cls.parts, cls.title = unpack_ap20(cls.candidate)
        cls.old_tok, cls.old_parts, _ = unpack_ap20(cls.original)

    def test_R84_identity_and_read_only(self):
        self.assertIn(ACTIVE.read_bytes(), (self.original, self.candidate))
        self.assertEqual(len(self.original), 67904)
        self.assertEqual(sha256(self.original).hexdigest(), R84_SHA)
        self.assertNotEqual(self.candidate, self.original)
        self.assertEqual(self.title, TITLE)
        self.assertEqual(self.metadata["commands"], 77)
        self.assertEqual(self.metadata["ap20_entries"], 87)

    def test_four_independent_v2_units_and_public_abi(self):
        self.assertEqual(len(self.parts), 87)
        self.assertEqual(len(self.old_parts), 85)
        self.assertEqual(tuple(map(len, self.parts[83:])), (5558, 2508, 40, 56580))
        self.assertEqual(self.parts[83:85], self.old_parts[82:84])
        self.assertEqual(self.parts[86], self.old_parts[84])
        self.assertEqual(self.parts[85], DISPATCH_V2 + PROBE_CODE)
        self.assertTrue(all(p.startswith(DISPATCH_V2) and len(p) <= 65534
                            and len(p) % 2 == 0 for p in self.parts[83:]))
        report = inspect(parse(self.candidate))
        old_report = inspect(parse(self.original))
        self.assertEqual(report["issues"], [])
        self.assertEqual(old_report["issues"], [])
        self.assertEqual(report["tokens"][:-1], old_report["tokens"])
        self.assertEqual(report["tokens"][-1]["name"], "aga bob probe")
        self.assertEqual(report["tokens"][-1]["signature"], NEW_FUNCTION[3])
        self.assertEqual(report["tokens"][-1]["function"], BASE_PUBLIC)

    def test_old_public_entries_only_change_group_numbers_and_end_getp(self):
        for i, original in enumerate(self.old_parts[:82]):
            now = self.parts[i]
            if original in (b"", GETP):
                self.assertEqual(now, original)
                continue
            expected = RBSR + pack(">HH",
                                   {82: GROUP_C2P, 83: GROUP_IFF, 84: GROUP_AGA}[
                                       unpack_from(">H", original, 2)[0]],
                                   unpack_from(">H", original, 4)[0]) + original[6:]
            if i == 81:
                expected += GETP
            self.assertEqual(now, expected, f"historical R84 stub {i} changed")
        self.assertEqual(self.parts[82], RBSR + pack(">HH", GROUP_BOBS, 0)
                         + bytes.fromhex("4e75"))

    def test_interpreter_bsr_displacements_and_error_injection(self):
        links = interpreter_rbsr_displacements(self.parts)
        self.assertEqual(len(links), 81)
        self.assertTrue(all(abs(d) < 32766 and d % 2 == 0 for d in links.values()))
        self.assertEqual(unpack_from(">H", self.parts[82], 2)[0], GROUP_BOBS)
        broken = list(self.parts)
        broken[82] = RBSR + pack(">HH", 87, 0) + bytes.fromhex("4e75")
        with self.assertRaises(ValueError):
            interpreter_rbsr_displacements(broken)
        self.assertEqual(unpack_ap20(repack_ap20(self.candidate,
                          self.tok, self.parts, self.title))[1], self.parts)

    def test_r84_and_bobs_group_dispatch_on_real_mc68020(self):
        for entry in (0, 2, 20, 33, 41, 57, 70, 75, 79, 80, 81, 82):
            with self.subTest(entry=entry):
                assert_reaches_entry_on_mc68020(self.candidate, entry)

    def test_probe_handler_executes_and_returns_1_on_real_mc68020(self):
        base, stack, stop = 0x100000, 0x380000, 0x480000
        u = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        u.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        u.mem_map(0, 0x500000)
        pos = starts(self.parts)
        u.mem_write(base, b"".join(self.parts))
        for index, displacement in interpreter_rbsr_displacements(self.parts).items():
            u.mem_write(base + pos[index], pack(">Hh", 0x6100, displacement))
        u.mem_write(stack, pack(">I", stop))
        u.mem_write(stop, bytes.fromhex("4e71"))
        u.reg_write(UC_M68K_REG_SR, 0x2000)
        u.reg_write(UC_M68K_REG_A7, stack)
        u.reg_write(UC_M68K_REG_A3, 0x210000)
        u.reg_write(UC_M68K_REG_D0, 0x11223344)
        u.reg_write(UC_M68K_REG_D1, 0x55667788)
        u.reg_write(UC_M68K_REG_D2, 0x13572468)
        u.reg_write(UC_M68K_REG_D3, 0)  # native V2 entry-offset 0
        u.reg_write(UC_M68K_REG_D4, 0x76543210)
        hits = []
        def at_stop(machine, address, _size, _data):
            if address == stop:
                hits.append(address)
                machine.emu_stop()
        u.hook_add(UC_HOOK_CODE, at_stop)
        u.emu_start(base + pos[BASE_PUBLIC], stop + 2, count=200)
        self.assertEqual(hits, [stop])
        self.assertEqual(u.reg_read(UC_M68K_REG_D3), 1)
        self.assertEqual(u.reg_read(UC_M68K_REG_D2), 0)
        self.assertEqual(u.reg_read(UC_M68K_REG_A3), 0x210000)
        self.assertEqual(u.reg_read(UC_M68K_REG_D0), 0x11223344)
        self.assertEqual(u.reg_read(UC_M68K_REG_D1), 0x55667788)
        self.assertEqual(u.reg_read(UC_M68K_REG_D4), 0x76543210)
        self.assertEqual(u.reg_read(UC_M68K_REG_A7), stack + 4)

    def test_determinism_and_no_write_to_dist(self):
        second, meta = build()
        self.assertEqual(second, self.candidate)
        self.assertEqual(meta, self.metadata)
        self.assertIn(ACTIVE.read_bytes(), (self.original, self.candidate))
        self.assertEqual(PROTECTED.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
