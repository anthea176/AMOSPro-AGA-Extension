#!/usr/bin/env python3
"""Five host-side static checks. Does NOT execute 68k code or WinUAE."""
import hashlib
import struct
import unittest
from build_m3_compact import build, SHA_M2, SHA_M3, M2_PATH

class TestM3a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=build()
        cls.p=cls.out[32:-4]
        cls.header=struct.unpack_from('>4I',cls.p)
        cls.entries=struct.unpack_from('>8H',cls.p,22)
        cls.old=M2_PATH.read_bytes()[32:-4]

    def test_hunk(self):
        self.assertEqual(len(self.out),688)
        self.assertEqual(self.out[:4],bytes.fromhex('000003f3'))
        self.assertEqual(self.out[24:28],bytes.fromhex('000003e9'))
        self.assertEqual(self.out[-4:],bytes.fromhex('000003f2'))
        n=struct.unpack_from('>I',self.out,20)[0]
        self.assertEqual(n*4,len(self.out)-36)
        self.assertEqual(n,struct.unpack_from('>I',self.out,28)[0])

    def test_tokens_and_entries(self):
        self.assertEqual(self.header,(16,58,504,50))
        self.assertEqual(self.entries,(21,2,8,8,48,165,0,0))
        self.assertEqual(sum(self.entries)*2,self.header[2])
        tokens=self.p[38:96]
        self.assertIn(b'\x00\x01\x00\x05aga dem\xef0\xff',tokens)
        self.assertTrue(tokens.startswith(self.old[36:80][:-6]))

    def test_m2_preservation(self):
        lib=self.p[96:96+504]
        self.assertEqual(lib[:170],self.old[80:250])
        self.assertEqual(lib[170:174],b'GetP')
        self.assertEqual(hashlib.sha256(M2_PATH.read_bytes()).hexdigest(),SHA_M2)

    def test_m3_pc_and_apis(self):
        demo=self.p[96+174:96+504]
        self.assertEqual(len(demo),330)
        self.assertTrue(demo.startswith(bytes.fromhex('48e7cffe')))
        self.assertIn(bytes.fromhex('4cdf7ff3'),demo)
        for vector in [-552,-414,-612,-66,-852,-342,-306,-270]:
            self.assertIn(b'\x4e\xae'+struct.pack('>h',vector),demo)
        self.assertIn(b'intuition.library\0',demo)
        self.assertIn(b'graphics.library\0',demo)

    def test_reproducible_sha(self):
        self.assertEqual(hashlib.sha256(self.out).hexdigest(),SHA_M3)
        self.assertEqual(self.out,build())

if __name__=='__main__': unittest.main(verbosity=2)
