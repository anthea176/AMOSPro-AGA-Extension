#!/usr/bin/env python3
"""M3b v0.0.4 structural regression checks. NOT WinUAE runtime tests."""
import hashlib
import struct
import unittest
from build_m3b_compact import build, M3A, M3A_SHA, M3B_SHA

class StaticM3b(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=build()
        cls.d=cls.b[32:-4]
        cls.j=list(struct.unpack_from(">11H",cls.d,22))
        cls.ts=struct.unpack_from(">4I",cls.d)
        cls.lib=cls.d[22+22+cls.ts[1]:22+22+cls.ts[1]+cls.ts[2]]
        cls.old=M3A.read_bytes()[32:-4]

    def test_hunk(self):
        self.assertEqual(len(self.b),1564)
        self.assertEqual(self.b[:4],bytes.fromhex("000003f3"))
        self.assertEqual(self.b[24:28],bytes.fromhex("000003e9"))
        self.assertEqual(self.b[-4:],bytes.fromhex("000003f2"))
        self.assertEqual(struct.unpack_from(">I",self.b,20),struct.unpack_from(">I",self.b,28))

    def test_header(self):
        self.assertEqual(self.ts[0],22)
        self.assertEqual(self.d[16:22],b"\0\0AP20")
        self.assertEqual(sum(self.j)*2,len(self.lib))
        self.assertEqual(self.j[-2:],[0,0])

    def test_legacy(self):
        self.assertEqual(hashlib.sha256(M3A.read_bytes()).hexdigest(),M3A_SHA)
        oldlib=self.old[96:600]
        self.assertEqual(self.lib[188:188+462],oldlib[42:])

    def test_cold_hooks(self):
        for off in (0x1c8,0x1cc,0x1d0):
            self.assertIn(bytes.fromhex("2b48")+struct.pack(">H",off),self.lib[:188])
        self.assertEqual(self.lib[188-32:188],b"\0"*32)

    def test_tokens(self):
        tok=self.d[44:44+self.ts[1]]
        self.assertIn(b"aga screen ope\xee00,0,0,0\xff",tok)
        self.assertIn(b"aga screen patter\xeeI\xff",tok)
        self.assertIn(b"aga screen clos\xe5I\xff",tok)

    def test_getp_abi(self):
        offset=0
        for i,length in enumerate(self.j):
            if i in (2,3,4,5,6,7,8):
                self.assertEqual(self.lib[offset-4:offset],b"GetP")
            offset+=length*2

    def test_dynamic_screen(self):
        self.assertIn(bytes.fromhex("80000023"),self.lib)
        self.assertIn(bytes.fromhex("80000024"),self.lib)
        self.assertIn(bytes.fromhex("80000025"),self.lib)
        self.assertIn(bytes.fromhex("80000032"),self.lib)
        self.assertIn(bytes.fromhex("028000000c80"),self.lib)

    def test_rendering_apis(self):
        self.assertIn(bytes.fromhex("4eaefcac"),self.lib)
        self.assertIn(bytes.fromhex("4eaefeaa"),self.lib)
        self.assertIn(bytes.fromhex("4eaefece"),self.lib)

    def test_cleanup_apis(self):
        self.assertIn(bytes.fromhex("4eaeffbe"),self.lib)
        self.assertIn(bytes.fromhex("4eaefe62"),self.lib)

    def test_sha_and_repro(self):
        self.assertEqual(hashlib.sha256(self.b).hexdigest(),M3B_SHA)
        self.assertEqual(build(),self.b)

if __name__=="__main__":
    unittest.main(verbosity=2)
