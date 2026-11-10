#!/usr/bin/env python3
import hashlib, unittest
from build_m4b_r4 import build, BASE, R4_SHA
from audit_ap20 import parse, inspect

class TestM4bR4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = BASE.read_bytes()
        cls.new = build()
        cls.a = parse(cls.old)
        cls.b = parse(cls.new)

    def test_sha(self):
        self.assertEqual(hashlib.sha256(self.new).hexdigest(), R4_SHA)

    def test_structure_unchanged(self):
        self.assertEqual((self.a.lengths,self.a.jumps,self.a.tokens,self.a.title),
                         (self.b.lengths,self.b.jumps,self.b.tokens,self.b.title))
        self.assertEqual(inspect(self.b)["issues"], [])

    def test_only_four_mask_bytes_changed(self):
        changes=[i for i,(x,y) in enumerate(zip(self.old,self.new)) if x!=y]
        self.assertEqual(len(changes), 4)

    def test_d3_not_restored_in_functions(self):
        for index in (10,11):
            s=self.b.starts[index]
            e=s+self.b.jumps[index]*2
            code=self.b.code[s:e]
            self.assertEqual(code[:4], bytes.fromhex("48e7efee"))
            self.assertEqual(code[-12:-8], bytes.fromhex("4cdf77f7"))
            self.assertEqual(code[-4:], b"GetP")
            self.assertIn(bytes.fromhex("7601"), code)

if __name__ == "__main__":
    unittest.main(verbosity=2)
