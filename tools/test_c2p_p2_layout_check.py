#!/usr/bin/env python3
"""Synthetic host-only tests; never evidence of actual WinUAE bitmap layout."""
from __future__ import annotations

import copy
import unittest

from c2p_p2_layout_check import check_document


def snapshot() -> dict:
    def sb(name: str, base: int, bpa: int, sbaddr: int) -> dict:
        return {
            "name": name, "screen_buffer": sbaddr, "bitmap": bpa,
            "bytes_per_row": 40, "rows": 256, "depth": 8, "flags": 0,
            "planes": [base + 10240 * x for x in range(8)],
            "type_of_mem_first": [2] * 8,
            "type_of_mem_last": [2] * 8,
        }
    return {
        "mode": {"width": 320, "height": 256, "depth": 8},
        "buffers": [sb("SB0", 0x10000, 0x50000, 0x60000), sb("SB1", 0x30000, 0x50040, 0x60040)],
    }


class TestLayout(unittest.TestCase):
    def test_two_standard_buffers(self) -> None:
        report = check_document(snapshot())
        self.assertTrue(report["direct_custom_bitmap_candidate"], report)
        self.assertFalse(report["runtime_qualified"])

    def test_noncontiguous_plane(self) -> None:
        obj = snapshot()
        obj["buffers"][1]["planes"][4] += 0x100
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_missing_memory_proof(self) -> None:
        obj = snapshot()
        del obj["buffers"][0]["type_of_mem_last"]
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_missing_chip_memory(self) -> None:
        obj = snapshot()
        obj["buffers"][0]["type_of_mem_last"][7] = 0
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_screen_buffers_overlap(self) -> None:
        obj = snapshot()
        obj["buffers"][1]["planes"] = copy.copy(obj["buffers"][0]["planes"])
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_interleaved_is_diagnostic_only(self) -> None:
        obj = snapshot()
        for buf in obj["buffers"]:
            base = buf["planes"][0]
            buf["flags"] = 4
            buf["bytes_per_row"] = 320
            buf["planes"] = [base + 40 * x for x in range(8)]
        report = check_document(obj)
        self.assertFalse(report["direct_custom_bitmap_candidate"])
        self.assertEqual(report["buffers"][0]["layout"], "interleaved")

    def test_bad_depth(self) -> None:
        obj = snapshot()
        obj["buffers"][0]["depth"] = 4
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_bad_width(self) -> None:
        obj = snapshot()
        obj["mode"]["width"] = 328
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_bad_sbs(self) -> None:
        obj = snapshot()
        obj["buffers"][1]["bitmap"] = obj["buffers"][0]["bitmap"]
        self.assertFalse(check_document(obj)["direct_custom_bitmap_candidate"])

    def test_wrong_plane_count(self) -> None:
        obj = snapshot()
        obj["buffers"][1]["planes"].pop()
        with self.assertRaises(ValueError):
            check_document(obj)

    def test_boolean_is_not_a_pointer(self) -> None:
        obj = snapshot()
        obj["buffers"][0]["bitmap"] = True
        with self.assertRaises(ValueError):
            check_document(obj)


if __name__ == "__main__":
    unittest.main()
