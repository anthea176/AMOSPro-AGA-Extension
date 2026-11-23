#!/usr/bin/env python3
"""Gate A: source-built P2d + public Sprite Bank/Get Sprite AP20 HUNK.

Real VASM MC68020 image, no installable Lib and no WinUAE claims.
"""
from __future__ import annotations
from hashlib import sha256
import os
import tempfile
from pathlib import Path
import unittest

from active_library import P2D_SHA
from audit_ap20 import inspect,parse,walk_tokens
from build_m19_p2d_in_memory import build_p2d
from build_m19_s1p1e_get_sprite_ap20 import build_get_aga_sprite_candidate,write_test_candidate
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP,RBSR,unpack_ap20


@unittest.skipUnless(os.getenv('AGSP_GET_BIN'), 'requires native MC68020 Get AGA Sprite binary')
class AGSPGetPublicAP20GateA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=Path(os.environ['AGSP_GET_BIN']).read_bytes()
        cls.base,cls.baseinfo=build_p2d()
        cls.image,cls.info=build_get_aga_sprite_candidate(cls.raw)

    def test_exact_p2d_and_hunk_preserved(self):
        self.assertEqual(sha256(self.base).hexdigest(),P2D_SHA)
        orig_t,orig_p,_=unpack_ap20(self.base)
        tokens,parts,_=unpack_ap20(self.image)
        self.assertEqual(parts[:203],orig_p)
        self.assertEqual(parts[203],GETP)
        self.assertEqual(parts[205],GETP)
        self.assertEqual(parts[204][:2],RBSR)
        self.assertEqual(parts[206][:2],RBSR)
        self.assertEqual(parts[207],DISPATCH_V2+self.raw)
        self.assertEqual(len(parts),208)
        self.assertEqual(len(list(walk_tokens(tokens))),
                         len(list(walk_tokens(orig_t)))+2)

    def test_six_argument_api_is_exact_and_new_tokens_only(self):
        tok,parts,_=unpack_ap20(self.image)
        old=list(walk_tokens(unpack_ap20(self.base)[0]))
        new=list(walk_tokens(tok))
        self.assertEqual(new[:-2],old)
        self.assertEqual([(t['name'],t['instruction'],t['function'],t['signature'])
                          for t in new[-2:]],[
                            ('aga sprite bank',204,1,'I0'),
                            ('get aga sprite',206,1,'00,0,0,0,0,0')])
        self.assertEqual(inspect(parse(self.image))['issues'],[])

    def test_candidate_not_distributed_not_compiler_tested(self):
        self.assertEqual(self.info['P2d_sha256'],P2D_SHA)
        self.assertEqual(self.info['native_sha256'],sha256(self.raw).hexdigest())
        self.assertEqual((self.info['P2d_commands'],self.info['candidate_commands']), (100,102))
        self.assertFalse(self.info['installable'])
        self.assertFalse(self.info['runtime_tested'])
        self.assertFalse(self.info['compiler_tested'])

    def test_explicit_test_candidate_only_outside_repository_no_overwrite(self):
        # Only an opt-in CI output under RUNNER_TEMP can be written.
        # dist/ and every other path within this repository stay untouchable.
        with tempfile.TemporaryDirectory(prefix='agsp_s1p1e_') as tmp:
            output=Path(tmp)/'AMOSPro_AGA.Lib'
            self.assertEqual(write_test_candidate(self.image,output),output.resolve())
            self.assertEqual(output.read_bytes(),self.image)
            self.assertEqual(sha256(output.read_bytes()).hexdigest(),self.info['sha256'])
            with self.assertRaises(FileExistsError):
                write_test_candidate(self.image,output)
        repository=Path(__file__).resolve().parents[1]
        for path in (repository/'dist/AMOSPro_AGA.Lib',
                     repository/'dist/AMOSPro_AGA_LAST_GOOD.Lib',
                     repository/'tests/proto/agsp_capture/NEVER_WRITE.Lib'):
            with self.subTest(path=path),self.assertRaises(ValueError):
                write_test_candidate(self.image,path)
        with self.assertRaises(ValueError):
            write_test_candidate(b'',Path('/tmp/AGSP_empty.Lib'))

    def test_reject_corrupt_native_image(self):
        for raw in (self.raw[:99],self.raw+b'\x00',b'\x00\x00'+self.raw[2:],
                    self.raw[:4]+b'\x00\x00'+self.raw[6:],
                    b'\x60\x00'+bytes(65536)):
            with self.subTest(size=len(raw)),self.assertRaises(ValueError):
                build_get_aga_sprite_candidate(raw)


if __name__=='__main__':
    unittest.main(verbosity=2)
