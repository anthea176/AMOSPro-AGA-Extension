#!/usr/bin/env python3
"""Host-only M19 AGBO staging tests: not native CPU Gate A or WinUAE."""
import unittest
from dataclasses import replace
from m19_p0a_multi_bob_abk import (
    empty_bank, put_image, make_mask, no_mask, parse_payload,
)
from m19_p0b_chip_dma_model import StageRegistry, stage_agbo


def fixture():
    raw = empty_bank()
    for ident, width, height, depth, value in (
            (1, 17, 15, 8, 1), (2, 31, 3, 4, 4), (3, 37, 8, 1, 0)):
        raw = put_image(raw, ident, width, height, depth,
                        bytes([value]) * (width * height))
    raw = make_mask(raw, 1, 0)
    raw = make_mask(raw, 2, 4)
    raw = no_mask(raw, 3)
    return raw


class TestDMAStage(unittest.TestCase):
    def test_exact_planes_and_masks(self):
        raw = fixture()
        expected = parse_payload(raw)
        result = stage_agbo(24, 0x1000, raw)
        self.assertEqual([e.width for e in result.images], [17, 31, 37])
        self.assertEqual([e.depth for e in result.images], [8, 4, 1])
        self.assertEqual([e.mask_offset is not None for e in result.images],
                         [True, True, False])
        self.assertEqual(result.data, b"".join(
            img.planes + (img.mask or b"") for img in expected.images))
        result.validate()
        self.assertEqual(parse_payload(raw).raw, raw)

    def test_alignment_and_ranges(self):
        result = stage_agbo(24, 0x1000, fixture())
        for image in result.images:
            for begin, count in image.dma_ranges():
                self.assertEqual(begin % 2, 0)
                self.assertEqual(count % 2, 0)
                self.assertLessEqual(begin + count, len(result.data))

    def test_reject_budget_without_publishing(self):
        raw = fixture()
        registry = StageRegistry()
        first = registry.prepare(24, 0x1000, raw)
        with self.assertRaises(MemoryError):
            registry.prepare(24, 0x2000, raw, budget=len(first.data) - 1)
        self.assertIs(registry.resolve(24, 0x1000, raw), first)

    def test_stale_pointer_and_payload_and_free(self):
        raw = fixture()
        registry = StageRegistry()
        registry.prepare(24, 0x1000, raw)
        self.assertIsNone(registry.resolve(24, 0x1002, raw))
        changed = put_image(raw, 2, 1, 1, 4, b"\x00")
        self.assertIsNone(registry.resolve(24, 0x1000, changed))
        registry.prepare(24, 0x1004, changed)
        self.assertIsNotNone(registry.resolve(24, 0x1004, changed))
        registry.free(24)
        self.assertIsNone(registry.resolve(24, 0x1004, changed))

    def test_corrupt_payload_rejected_atomically(self):
        raw = fixture()
        registry = StageRegistry()
        old = registry.prepare(24, 0x1000, raw)
        bad = b"BAD!" + raw[4:]
        with self.assertRaises(ValueError):
            registry.prepare(24, 0x1002, bad)
        self.assertIs(registry.resolve(24, 0x1000, raw), old)

    def test_bad_bank_and_synthetic_budget(self):
        raw = fixture()
        for bank, identity in ((4, 0x1000), (24, 0), (24, 3)):
            with self.assertRaises(ValueError):
                stage_agbo(bank, identity, raw)
        for budget in (-1, 1 << 25):
            with self.assertRaises(ValueError):
                stage_agbo(24, 0x1000, raw, budget=budget)

    def test_corrupt_span_detected(self):
        result = stage_agbo(24, 0x1000, fixture())
        wrong = replace(result, images=(
            replace(result.images[0], pixel_offset=0x100000),)
            + result.images[1:])
        with self.assertRaises(ValueError):
            wrong.validate()

    def test_empty_bank(self):
        result = stage_agbo(24, 0x1000, empty_bank(), budget=0)
        self.assertEqual(result.data, b"")
        self.assertEqual(result.images, ())

    def test_host_data_not_chip(self):
        result = stage_agbo(24, 0x1000, fixture())
        self.assertIsInstance(result.data, bytes)
        self.assertFalse(hasattr(result, "chip_address"))


if __name__ == "__main__":
    unittest.main()
