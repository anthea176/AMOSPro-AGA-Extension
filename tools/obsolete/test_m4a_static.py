#!/usr/bin/env python3
"""M4a v0.0.5 structural checks. These do NOT replace WinUAE runtime tests."""
import hashlib
import struct
import unittest
from build_m4a_waitvbl import build, BASE, BASE_SHA, M4A_SHA, WAIT_HEX

class TestM4a(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = build()
        cls.old = BASE.read_bytes()
        cls.d = cls.b[32:-4]
        cls.off, cls.toklen, cls.liblen, cls.titlelen = struct.unpack_from(">4I", cls.d)
        cls.j = list(struct.unpack_from(">11H", cls.d, 22))
        cls.tok = cls.d[44:44 + cls.toklen]
        cls.lib = cls.d[44 + cls.toklen:44 + cls.toklen + cls.liblen]

        od = cls.old[32:-4]
        _, oldtoklen, oldliblen, _ = struct.unpack_from(">4I", od)
        cls.oldlib = od[44 + oldtoklen:44 + oldtoklen + oldliblen]

    def test_hunk(self):
        self.assertEqual(len(self.b), 1612)
        self.assertEqual(self.b[:4], bytes.fromhex("000003f3"))
        self.assertEqual(self.b[-4:], bytes.fromhex("000003f2"))

    def test_sha(self):
        self.assertEqual(hashlib.sha256(self.old).hexdigest(), BASE_SHA)
        self.assertEqual(hashlib.sha256(self.b).hexdigest(), M4A_SHA)

    def test_header(self):
        self.assertEqual((self.off, self.toklen, self.liblen, self.titlelen),
                         (22, 150, 1320, 60))
        self.assertEqual(self.d[16:22], b"\0\0AP20")

    def test_jumps(self):
        self.assertEqual(self.j, [94, 2, 8, 8, 48, 167, 193, 75, 52, 13, 0])
        self.assertEqual(sum(self.j) * 2, len(self.lib))

    def test_token(self):
        self.assertIn(b"aga wait vb\xecI\xff", self.tok)

    def test_legacy_library_preserved(self):
        self.assertEqual(self.lib[:len(self.oldlib)], self.oldlib)

    def test_getp_dispatcher(self):
        self.assertEqual(self.lib[len(self.oldlib):len(self.oldlib) + 4], b"GetP")

    def test_wait_routine(self):
        offset = sum(self.j[:9]) * 2
        self.assertEqual(self.lib[offset:offset + 26], bytes.fromhex(WAIT_HEX))

    def test_waittof_lvo(self):
        self.assertIn(bytes.fromhex("4eaefef2"), self.lib)

    def test_state_access(self):
        tail = self.lib[-40:]
        self.assertIn(bytes.fromhex("246d01c84a92"), tail)
        self.assertIn(bytes.fromhex("2c6a0008"), tail)

    def test_reproducible(self):
        self.assertEqual(build(), self.b)

if __name__ == "__main__":
    unittest.main(verbosity=2)
