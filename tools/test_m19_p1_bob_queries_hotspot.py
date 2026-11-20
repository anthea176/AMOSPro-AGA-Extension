#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1 source-only readiness: existing real MC68020 object_read and AGBO hotspots.

No public AP20 token, new native P1 emitter, Lib build, WinUAE or Compiler claim.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack_into, unpack
import unittest

from m19_p0a_multi_bob_abk import (
    empty_bank, make_abk, make_mask, no_mask, parse_abk, parse_payload,
    put_image, set_hotspot,
)
from m19_p0e_object_table_emit import emit_object_table
from test_m19_p0e_object_table_native import (
    CANARY, OTHER, native_machine, invoke,
)

ROOT = Path(__file__).resolve().parents[1]
P0_SHA = 'f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d'
P1_SHA = '2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4'


class P1Readiness(unittest.TestCase):
    def test_p0_binary_protection(self):
        current = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
        good = (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
        self.assertEqual(len(good), 117896)
        self.assertEqual(sha256(good).hexdigest(), P0_SHA)
        self.assertEqual(len(current), 119176)
        self.assertEqual(sha256(current).hexdigest(), P1_SHA)
        self.assertNotEqual(good, current)

    def test_native_private_bob_read_fields_and_guards(self):
        native, labels = emit_object_table()
        self.assertEqual(len(native), 2332)
        for base in (0x10000, 0x21000):
            uc, root, table = native_machine(native, labels, base)
            self.assertEqual(invoke(uc, base, labels, 'read', ident=1), (0, CANARY))
            self.assertEqual(invoke(uc, base, labels, 'reset')[0], 1)
            for ident, bank, image, x, y in (
                (1, 24, 1, -32768, 32767),
                (32, 25, 4096, -1, -17),
                (64, 65535, 2, 32767, -32768),
            ):
                self.assertEqual(invoke(uc, base, labels, 'put', ident=ident,
                                        bank=bank, image=image, x=x, y=y)[0], 1)
                status, raw = invoke(uc, base, labels, 'read', ident=ident)
                self.assertEqual(status, 1)
                self.assertEqual(unpack('>IIiiII', raw), (bank, image, x, y, 1, 0))
                self.assertEqual(invoke(uc, base, labels, 'read', ident=ident,
                                        owner=OTHER), (0, CANARY))
                self.assertEqual(invoke(uc, base, labels, 'off', ident=ident)[0], 1)
                self.assertEqual(invoke(uc, base, labels, 'read', ident=ident),
                                 (0, CANARY))
                self.assertEqual(invoke(uc, base, labels, 'put', ident=ident,
                                        bank=bank, image=image, x=0, y=0)[0], 1)
                status, raw = invoke(uc, base, labels, 'read', ident=ident)
                self.assertEqual((status, unpack('>IIiiII', raw)),
                                 (1, (bank, image, 0, 0, 1, 0)))
            for bad in (0, 65):
                self.assertEqual(invoke(uc, base, labels, 'read', ident=bad),
                                 (0, CANARY))

    def test_hotspot_roundtrip_mask_and_unrelated_image(self):
        payload = put_image(empty_bank(), 1, 17, 5, 8, bytes(range(85)))
        payload = put_image(payload, 2, 31, 3, 8, bytes([0, 1, 2] * 31))
        payload = make_mask(payload, 2, 0)
        previous = parse_payload(payload)
        self.assertEqual((previous.image(2).hotspot_x, previous.image(2).hotspot_y),
                         (0, 0))
        changed = set_hotspot(payload, 2, -3, 5)
        result = parse_payload(changed)
        self.assertEqual(result.generation, previous.generation + 1)
        self.assertEqual(result.image(1), previous.image(1))
        self.assertEqual(result.image(2).mask, previous.image(2).mask)
        self.assertEqual(result.image(2).planes, previous.image(2).planes)
        self.assertEqual((result.image(2).hotspot_x, result.image(2).hotspot_y),
                         (-3, 5))
        self.assertEqual(len(changed), len(payload))
        self.assertEqual(parse_payload(payload), previous)
        self.assertIs(set_hotspot(changed, 2, -3, 5), changed)
        number, flags, loaded = parse_abk(make_abk(24, changed))
        self.assertEqual((number, flags, loaded), (24, 1, result))
        self.assertEqual((parse_payload(no_mask(changed, 2)).image(2).hotspot_x,
                          parse_payload(make_mask(changed, 2, 0)).image(2).hotspot_y),
                         (-3, 5))

    def test_hotspot_range_and_transaction_failure(self):
        original = put_image(empty_bank(), 1, 1, 1, 8, b'\xff')
        for args in ((1, -32769, 0), (1, 32768, 0), (1, 0, -32769),
                     (1, 0, 32768), (1, True, 0), (1, 0, False)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                set_hotspot(original, *args)
            self.assertEqual(parse_payload(original).image(1).hotspot_x, 0)
        with self.assertRaises(KeyError):
            set_hotspot(original, 2, 0, 0)
        maximum = bytearray(original)
        pack_into('>I', maximum, 24, 0xffffffff)
        maximum = bytes(maximum)
        self.assertIs(set_hotspot(maximum, 1, 0, 0), maximum)
        with self.assertRaises(ValueError):
            set_hotspot(maximum, 1, 1, 1)
        changed = set_hotspot(original, 1, -32768, 32767)
        self.assertEqual((parse_payload(changed).image(1).hotspot_x,
                          parse_payload(changed).image(1).hotspot_y),
                         (-32768, 32767))


if __name__ == '__main__':
    unittest.main(verbosity=2)
