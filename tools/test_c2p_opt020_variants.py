"""Structural and pixel-model checks for *unintegrated* C2P OPT020 code.

Run explicitly: python -B tools/test_c2p_opt020_variants.py
Not a native 68020 emulator and not a Gate A/B/C/D qualification.
"""
from __future__ import annotations

import unittest
from struct import unpack_from

from c2p_r78_blit_emit import emit_blit
from c2p_r79_zoom_emit import emit_zoom
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky
from c2p_opt020_variants import (
    emit_blit_opt020, emit_zoom_opt020, emit_iff_chunky_opt020,
    _nibble_lut,
)


def branch_target(code: bytes, branch_at: int) -> int:
    assert code[branch_at:branch_at + 2] == b"\x60\x00"
    return branch_at + 2 + unpack_from(">h", code, branch_at + 2)[0]


class Opt020PreparedTests(unittest.TestCase):
    def check_patched_entry(self, historical, optimized, name):
        old, old_labels = historical()
        fresh, new_labels = optimized()
        self.assertGreater(len(fresh), len(old))
        at = old_labels[name]
        self.assertEqual(fresh[:at], old[:at])
        self.assertEqual(branch_target(fresh, at), len(old))
        self.assertEqual(new_labels[name + "_opt020"], len(old))
        self.assertEqual(fresh[at + 4:len(old)], old[at + 4:])
        self.assertEqual(historical()[0], old, "historical emitter mutated")
        self.assertEqual(optimized()[0], fresh, "variant is nondeterministic")
        return old, fresh, old_labels, new_labels

    def test_blit_longword_loop_and_historical_integrity(self):
        old, new, labels, _ = self.check_patched_entry(
            emit_blit, emit_blit_opt020, "copy_row")
        tail = new[len(old):]
        self.assertIn(bytes.fromhex("22d8"), tail)  # MOVE.L (A0)+,(A1)+
        self.assertIn(bytes.fromhex("12d8"), tail)  # MOVE.B (A0)+,(A1)+
        self.assertIn(bytes.fromhex("51ce"), tail)  # DBRA D6
        self.assertIn(bytes.fromhex("51cf"), tail)  # DBRA D7
        for width in range(1, 321):
            count, remainder = divmod(width, 4)
            self.assertEqual(4 * count + remainder, width)
            self.assertTrue(0 <= remainder <= 3)

    def test_zoom_dda_fast_loop_and_historical_integrity(self):
        old, new, labels, _ = self.check_patched_entry(
            emit_zoom, emit_zoom_opt020, "pixel")
        tail = new[len(old):]
        self.assertIn(bytes.fromhex("d1c5"), tail)  # ADDA.L D5,A0
        self.assertIn(bytes.fromhex("51ce"), tail)
        # Quotient/remainder progression retains exact nearest-neighbour
        # positions even when left clipping changes the first visible X.
        for source_width in range(1, 321):
            for target_width in (1, 2, 3, 7, 16, 32, 64, 127, 320):
                quotient, remainder = divmod(source_width, target_width)
                for clipped in (0, min(8, target_width - 1)):
                    source, error = divmod(clipped * source_width,
                                           target_width)
                    for x in range(clipped, target_width):
                        self.assertEqual(source,
                                         (x * source_width) // target_width)
                        source += quotient
                        error += remainder
                        if error >= target_width:
                            source += 1
                            error -= target_width

    def test_iff_lut_cpu_guard_and_historical_integrity(self):
        old, labels = emit_iff_to_chunky()
        new, changed = emit_iff_chunky_opt020()
        byte_start = labels["byte_start"]
        guard_site = labels["chunky_decode"] + 4
        guard_start = changed["chunky_decode_cpu_guard_opt020"]
        self.assertEqual(branch_target(new, byte_start), len(old))
        self.assertEqual(branch_target(new, guard_site), guard_start)
        for i in range(0, len(old)):
            if byte_start <= i < byte_start + 4:
                continue
            if guard_site <= i < guard_site + 4:
                continue
            self.assertEqual(new[i], old[i], f"unexpected R80 change @{i}")
        loop = new[len(old):guard_start]
        self.assertEqual(loop.count(bytes.fromhex("20360c00")), 2)
        self.assertEqual(loop.count(bytes.fromhex("eda8")), 2)
        self.assertEqual(loop.count(bytes.fromhex("819c")), 2)
        self.assertEqual(loop[-64:], _nibble_lut())
        guard = new[guard_start:]
        self.assertIn(bytes.fromhex("20780004"), guard)
        self.assertIn(bytes.fromhex("08000001"), guard)
        self.assertEqual(emit_iff_to_chunky()[0], old)
        self.assertEqual(emit_iff_chunky_opt020()[0], new)

    def test_nibble_table_all_8_planes_all_source_bytes(self):
        table = _nibble_lut()
        self.assertEqual(len(table), 64)
        for plane in range(8):
            for value in range(256):
                upper = table[4 * (value >> 4):4 * (value >> 4) + 4]
                lower = table[4 * (value & 15):4 * (value & 15) + 4]
                got = [index << plane for index in upper + lower]
                expected = [((value >> (7 - i)) & 1) << plane
                            for i in range(8)]
                self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
