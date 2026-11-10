#!/usr/bin/env python3
import unittest
from build_m4b_r5 import build, BASE
from audit_ap20 import inspect, parse

class TestM4bR5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=build()
        cls.lib=parse(cls.out)

    def test_loader_structure(self):
        self.assertEqual(inspect(self.lib)["issues"], [])
        self.assertEqual(self.lib.jumps,(94,2,8,8,48,167,193,75,101,15,90,89,56,0))

    def test_size(self):
        self.assertEqual(len(self.out),2248)

    def test_safe_protocol_vectors(self):
        code=self.lib.code
        for op in ("4eaefd66","4eaefd60","4eaefcf4","4eaefef2","4eaefe80","4eaefe8c"):
            self.assertIn(bytes.fromhex(op),code)

    def test_safe_reply_port_offset(self):
        self.assertIn(bytes.fromhex("21400016"),self.lib.code)

    def test_r4_tokens_unchanged(self):
        self.assertEqual(parse(BASE.read_bytes()).tokens,self.lib.tokens)

    def test_reproducible_committed_binary(self):
        dest=BASE.parent/"AMOSPro_AGA_M4b_v0.0.6_R5.Lib"
        if dest.exists():
            self.assertEqual(dest.read_bytes(),self.out)

if __name__=="__main__":
    unittest.main(verbosity=2)
