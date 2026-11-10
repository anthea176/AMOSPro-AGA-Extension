#!/usr/bin/env python3
import hashlib
import struct
import unittest

from audit_ap20 import inspect, parse
from build_m4b_r6a import BASE, DEST, R6A_SHA, build

class TestM4bR6A(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=build()
        cls.lib=parse(cls.raw)
        cls.r4=parse(BASE.read_bytes())

    def segment(self,index):
        s=self.lib.starts[index]
        return self.lib.code[s:s+2*self.lib.jumps[index]]

    def r4_segment(self,index):
        s=self.r4.starts[index]
        return self.r4.code[s:s+2*self.r4.jumps[index]]

    def test_hash_and_ap20(self):
        self.assertEqual(len(self.raw),2004)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),R6A_SHA)
        self.assertEqual(inspect(self.lib)["issues"],[])
        self.assertEqual(self.lib.lengths,(28,208,1642,64))
        self.assertEqual(self.lib.jumps,(136,2,8,8,48,167,193,75,92,15,71,5,1,0))

    def test_committed_binary_matches_builder(self):
        self.assertTrue(DEST.exists(),"committed R6A binary missing")
        committed=DEST.read_bytes()
        self.assertEqual(len(committed),2004)
        self.assertEqual(hashlib.sha256(committed).hexdigest(),R6A_SHA)
        self.assertEqual(committed,self.raw)
        self.assertEqual(inspect(parse(committed))["issues"],[])

    def test_open_unchanged(self):
        self.assertEqual(self.segment(6),self.r4_segment(6))

    def test_state_is_36_bytes_and_leas_target_it(self):
        cold=self.segment(0)
        state_start=len(cold)-36
        self.assertEqual(cold[-36:],b"\0"*36)
        for field in (12,32):
            disp=struct.unpack_from(">h",cold,field)[0]
            self.assertEqual(field+disp,state_start)

    def test_depth_is_not_used_as_db_pointer(self):
        for index in (8,10,11,12):
            self.assertNotIn(bytes.fromhex("266a001c"),self.segment(index))

    def test_db_pointer_is_state_plus_32(self):
        close=self.segment(8)
        db=self.segment(10)
        self.assertIn(bytes.fromhex("286a0020"),close)
        self.assertIn(bytes.fromhex("42aa0020"),close)
        self.assertIn(bytes.fromhex("286a0020"),db)
        self.assertIn(bytes.fromhex("254c0020"),db)

    def test_a3_preserved(self):
        close=self.segment(8)
        db=self.segment(10)
        self.assertEqual(close[:4],bytes.fromhex("48e7fffe"))
        self.assertIn(bytes.fromhex("4cdf7fff4e75"),close)
        self.assertEqual(db[:4],bytes.fromhex("48e7effe"))
        self.assertIn(bytes.fromhex("4cdf7ff774004e75"),db)

    def test_db_published_only_after_two_allocations(self):
        db=self.segment(10)
        publish=db.index(bytes.fromhex("254c0020"))
        alloc=bytes.fromhex("4eaefd00")
        self.assertEqual(db[:publish].count(alloc),2)
        self.assertEqual(db[publish:].count(alloc),0)

    def test_waitblit_precedes_free_screenbuffer(self):
        close=self.segment(8)
        self.assertLess(close.index(bytes.fromhex("4eaeff1c")),
                        close.index(bytes.fromhex("4eaefcfa")))

    def test_swap_and_backfill_are_safe_stubs(self):
        self.assertEqual(self.segment(11),bytes.fromhex("760074004e7547657450"))
        self.assertEqual(self.segment(12),bytes.fromhex("4e75"))

    def test_parameter_dispatchers_remain_valid(self):
        checks=inspect(self.lib)["parameter_checks"]
        self.assertEqual([(x["index"],x["parameters"],x["getp"]) for x in checks],
                         [(6,4,True),(12,1,True)])

if __name__ == "__main__":
    unittest.main(verbosity=2)
