#!/usr/bin/env python3
"""M3b R1 regression: checks old failure vs corrected 68k parameters."""
import hashlib
import unittest
from build_m3b_compact import build as old_build
from build_m3b_r1 import build as r1_build, M3B_SHA

class TestM3bR1(unittest.TestCase):
    def test_compact_rebuild_sha(self):
        out=r1_build()
        self.assertEqual(len(out),1564)
        self.assertEqual(hashlib.sha256(out).hexdigest(),M3B_SHA)
    def test_exactly_four_bytes_modified(self):
        old=old_build()
        new=r1_build()
        changes=[(i,a,b) for i,(a,b) in enumerate(zip(old,new)) if a!=b]
        self.assertEqual(changes,[(866,40,46),(868,42,44),(870,44,42),(872,46,40)])
    def test_amos_365_last_parameter_in_d3(self):
        new=r1_build()
        self.assertEqual(new[862:874],bytes.fromhex("48e7cfee2e032c1b2a1b281b"))

if __name__=="__main__":
    unittest.main(verbosity=2)
