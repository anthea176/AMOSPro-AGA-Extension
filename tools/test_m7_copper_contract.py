#!/usr/bin/env python3
"""Static M7 Copper contract tests — no .Lib/68k/runtime validation implied."""
import unittest

from m7_copper_contract import (
    COLOR_FIRST, COLOR_LAST, MAX_USER_INSTRUCTIONS,
    CopperInputError, CopperProgram, Move, Wait,
)


class CopperContractTests(unittest.TestCase):
    def test_legal_raster_plan(self):
        p = CopperProgram()
        self.assertEqual(p.wait(24, 0), 1)
        self.assertEqual(p.move(COLOR_FIRST, 0x0F00), 1)
        self.assertEqual(p.wait(128, 0), 1)
        self.assertEqual(p.move(COLOR_LAST, 0x000F), 1)
        self.assertEqual(p.end(), 1)
        self.assertEqual(p.on(), 1)
        self.assertEqual(p.off(), 1)
        self.assertEqual(p.instructions, (
            Wait(24, 0), Move(0x180, 0x0F00),
            Wait(128, 0), Move(0x1BE, 0x000F),
        ))

    def test_valid_boundaries(self):
        p = CopperProgram()
        p.wait(0, 0)
        p.move(0x180, 0)
        p.wait(255, 222)
        p.move(0x1BE, 0xFFF)
        self.assertEqual(p.end(), 1)

    def test_wait_bounds_and_order(self):
        for v, h in ((-1, 0), (256, 0), (0, -1), (0, 223),
                     (0x10000, 0), (0, 0x10000)):
            with self.subTest(v=v, h=h):
                with self.assertRaises(CopperInputError):
                    CopperProgram().wait(v, h)
        p = CopperProgram()
        p.wait(70, 10)
        for v, h in ((70, 10), (69, 20), (70, 9)):
            with self.subTest(v=v, h=h):
                with self.assertRaises(CopperInputError):
                    p.wait(v, h)

    def test_only_safe_color_registers(self):
        for reg in (-2, 0, 0x17E, 0x181, 0x1BF, 0x1C0,
                    0x0106, 0x08E, 0x0E0, 0x096, 0x088):
            with self.subTest(register=reg):
                with self.assertRaises(CopperInputError):
                    CopperProgram().move(reg, 0xF0F)

    def test_palette_subset(self):
        for value in (-1, 0x1000, 0xFFFF, 0x10000):
            with self.subTest(value=value):
                with self.assertRaises(CopperInputError):
                    CopperProgram().move(0x180, value)

    def test_no_implicit_bool_or_string_values(self):
        p = CopperProgram()
        for value in (True, False, None, "24", 24.0):
            with self.subTest(value=value):
                with self.assertRaises(CopperInputError):
                    p.wait(value, 0)
                with self.assertRaises(CopperInputError):
                    p.move(value, 0)

    def test_requires_end_before_on(self):
        p = CopperProgram()
        with self.assertRaises(CopperInputError):
            p.on()
        with self.assertRaises(CopperInputError):
            p.end()
        p.wait(0, 0)
        p.move(0x180, 0xA00)
        p.end()
        with self.assertRaises(CopperInputError):
            p.wait(2, 0)
        with self.assertRaises(CopperInputError):
            p.move(0x180, 0xF00)
        with self.assertRaises(CopperInputError):
            p.end()
        p.on()
        with self.assertRaises(CopperInputError):
            p.on()
        with self.assertRaises(CopperInputError):
            p.clear()
        p.off()
        self.assertEqual(p.clear(), 1)

    def test_instruction_budget_and_reset(self):
        p = CopperProgram()
        for v in range(MAX_USER_INSTRUCTIONS - 1):
            p.wait(v, 0)
        with self.assertRaises(CopperInputError):
            p.move(0x180, 0xF00)
        p.end()
        p.on()
        p.off()
        self.assertEqual(p.clear(), 1)
        self.assertFalse(p.instructions)
        p.wait(10, 0)
        p.move(0x180, 0x0F0)
        p.end()
        self.assertEqual(p.on(), 1)

    def test_no_failed_append_corrupts_plan(self):
        p = CopperProgram()
        p.wait(44, 0)
        before = p.instructions
        with self.assertRaises(CopperInputError):
            p.move(0x96, 0x8000)
        self.assertEqual(p.instructions, before)
        with self.assertRaises(CopperInputError):
            p.wait(44, 0)
        self.assertEqual(p.instructions, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
