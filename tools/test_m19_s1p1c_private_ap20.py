#!/usr/bin/env python3
"""Verify private AGSP AP20 source link against P2d source-built baseline.

No .Lib is produced or installed; this tests AP20 HUNK layout only.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import unittest

from active_library import P2D_SHA
from audit_ap20 import inspect, parse, walk_tokens
from build_m19_p2d_in_memory import build_p2d
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import unpack_ap20
from build_m19_s1p1c_private_ap20 import build_private_agsp


@unittest.skipUnless(os.environ.get('AGSP_PIPELINE_BIN'),
                     'requires real VASM private pipeline bytes')
class AGSPPrivateAP20GateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = Path(os.environ['AGSP_PIPELINE_BIN']).read_bytes()
        cls.original, cls.base = build_p2d()
        assert sha256(cls.original).hexdigest() == P2D_SHA
        cls.candidate, cls.report = build_private_agsp(cls.raw)

    def test_candidate_reversible_ap20_hunk(self):
        tokens,parts,title=unpack_ap20(self.candidate)
        src_tokens,src_parts,src_title=unpack_ap20(self.original)
        self.assertEqual(len(parts),204)
        self.assertEqual(len(src_parts),203)
        self.assertEqual(tokens,src_tokens)
        self.assertEqual(parts[:-1],src_parts)
        self.assertEqual(parts[-1],DISPATCH_V2+self.raw)
        self.assertNotEqual(title,src_title)
        self.assertEqual(self.report['group'],203)
        self.assertEqual(self.report['private_code_bytes'],len(self.raw))
        self.assertEqual(self.report['sha256'],sha256(self.candidate).hexdigest())

    def test_no_new_public_command_or_getp_impact(self):
        before=inspect(parse(self.original))
        after=inspect(parse(self.candidate))
        self.assertEqual(after['issues'],[])
        self.assertEqual(before['tokens'],after['tokens'])
        self.assertEqual(list(walk_tokens(unpack_ap20(self.original)[0])),
                         list(walk_tokens(unpack_ap20(self.candidate)[0])))
        self.assertEqual(len(after['tokens']), len(before['tokens']))
        self.assertFalse(self.report['installable'])
        self.assertFalse(self.report['api_exported'])

    def test_native_source_anchored_to_exact_p2d(self):
        self.assertEqual(sha256(self.original).hexdigest(),P2D_SHA)
        self.assertEqual(self.report['protected_entries'],203)
        self.assertEqual(self.report['protected_commands'],100)
        self.assertGreater(len(self.raw),1000)
        self.assertLessEqual(len(self.raw)+len(DISPATCH_V2),MAX_UNIT_BYTES)
        self.assertEqual(self.report['private_code_sha256'],sha256(self.raw).hexdigest())

    def test_reject_odd_overlong_or_missing_entry(self):
        bad=(self.raw[:97],self.raw+b'x',
             b'\x60\x00'+bytes(MAX_UNIT_BYTES),
             b'\x00\x00'+self.raw[2:],
             self.raw[:2]+bytes(len(self.raw)-2))
        for candidate in bad:
            with self.subTest(length=len(candidate)),self.assertRaises(ValueError):
                build_private_agsp(candidate)


if __name__=='__main__':
    unittest.main(verbosity=2)
