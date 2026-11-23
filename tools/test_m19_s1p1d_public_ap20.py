#!/usr/bin/env python3
"""S1-P1d public Aga Sprite Bank candidate AP20 HUNK structural tests.

Solely in-memory build using verified P2d sources. Nothing installed.
"""
from __future__ import annotations
import os
from hashlib import sha256
from pathlib import Path
import unittest
from active_library import P2D_SHA
from audit_ap20 import inspect,parse,walk_tokens
from build_m19_p2d_in_memory import build_p2d
from build_m19_s1p1d_sprite_bank_ap20 import build_sprite_bank_candidate
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP,RBSR,unpack_ap20


@unittest.skipUnless(os.getenv('AGSP_SELECT_BIN'),
                     'requires real VASM MC68020 public select binary')
class AGSPSpriteBankAP20GateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=Path(os.environ['AGSP_SELECT_BIN']).read_bytes()
        cls.base,cls.base_report=build_p2d()
        cls.image,cls.report=build_sprite_bank_candidate(cls.native)

    def test_source_identity_and_preservation_of_p2d(self):
        self.assertEqual(sha256(self.base).hexdigest(),P2D_SHA)
        src_tok,src_parts,src_title=unpack_ap20(self.base)
        tok,parts,title=unpack_ap20(self.image)
        self.assertNotEqual(tok,src_tok)  # exactly one new token, checked below
        self.assertEqual(len(parts),len(src_parts)+3)
        self.assertEqual(parts[:203],src_parts)
        self.assertEqual(parts[203],GETP)
        self.assertEqual(parts[204][:2],RBSR)
        self.assertEqual(parts[205],DISPATCH_V2+self.native)
        self.assertNotEqual(title,src_title)

    def test_public_instruction_and_single_argument_getp(self):
        src=list(walk_tokens(unpack_ap20(self.base)[0]))
        dst=list(walk_tokens(unpack_ap20(self.image)[0]))
        self.assertEqual(dst[:-1],src)
        new=dst[-1]
        self.assertEqual(new['name'],'aga sprite bank')
        self.assertEqual(new['signature'],'I0')
        self.assertEqual((new['instruction'],new['function']),(204,1))
        self.assertEqual(inspect(parse(self.image))['issues'],[])
        self.assertEqual(self.report['stub_index'],204)
        self.assertEqual(self.report['group_index'],205)

    def test_all_native_is_private_except_sprite_bank(self):
        self.assertEqual(self.report['candidate_public_commands'],
                         self.report['original_public_commands']+1)
        self.assertEqual(self.report['public_name'],'aga sprite bank')
        self.assertFalse(self.report['installable'])
        self.assertFalse(self.report['distributed'])
        self.assertFalse(self.report['compiler_tested'])
        self.assertEqual(self.report['native_sha256'],sha256(self.native).hexdigest())

    def test_fail_closed_invalid_binary(self):
        samples=(self.native[:99],self.native+b'\x00',
                 b'\x00\x00'+self.native[2:],
                 b'\x60\x00'+bytes(65536))
        for raw in samples:
            with self.subTest(n=len(raw)),self.assertRaises(ValueError):
                build_sprite_bank_candidate(raw)


if __name__=='__main__':
    unittest.main(verbosity=2)
