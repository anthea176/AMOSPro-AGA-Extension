#!/usr/bin/env python3
"""Static format-only checks for the R30 AGAPAL bank proposal.

No AP20 binary, bank search in A5, or AMOS/WinUAE run is tested here.
"""
from pathlib import Path
from struct import pack
import unittest

from agapal_r30_layout import (
    ABK_HEADER, HEADER, INDEX_SIZE, NAME, RGB_SIZE, SLOT_SIZE,
    VERSION, SIGNATURE, payload_size, init_payload, parse_payload,
    abk_model, parse_abk,
)

class TestAGAPALFormat(unittest.TestCase):
    def test_exact_eight_palettes_and_header(self):
        raw = init_payload(8)
        self.assertEqual(len(raw), 6224)
        self.assertEqual(raw[:6], SIGNATURE)
        self.assertEqual(raw[6:16], pack(">HHHI",VERSION,8,0,0))
        self.assertEqual(raw[16:24],pack(">IHH",80,0,0))
        self.assertEqual(raw[72:80],pack(">IHH",80+7*768,0,0))
        self.assertEqual(raw[80:],bytes(8*768))
        self.assertEqual(parse_payload(raw).palettes,8)

    def test_multiple_counts_and_offsets(self):
        for n in (1,2,3,8,16,32,64,256):
            with self.subTest(n=n):
                p=init_payload(n)
                self.assertEqual(len(p), 16+n*776)
                parsed=parse_payload(p)
                self.assertEqual(len(parsed.entries),n)
                for i,(off,colors,flags) in enumerate(parsed.entries):
                    self.assertEqual(off,16+8*n+i*768)
                    self.assertEqual((colors,flags),(0,0))
                    self.assertEqual(p[off:off+768],bytes(768))

    def test_native_abk_reference_envelope(self):
        for chip in (False,True):
            with self.subTest(chip=chip):
                payload=init_payload(8)
                file=abk_model(10,payload,chip)
                self.assertEqual(len(file),ABK_HEADER+6224)
                self.assertEqual(file[:4],b"AmBk")
                self.assertEqual(file[4:8],pack(">HH",10,3 if chip else 1))
                self.assertEqual(file[8:12],pack(">I",6224+8))
                self.assertEqual(file[12:20],NAME)
                self.assertEqual(file[20:],payload)
                bank,flags,parsed=parse_abk(file)
                self.assertEqual((bank,flags,parsed.palettes),(10,3 if chip else 1,8))

    def test_reject_wrong_formats(self):
        good=init_payload(8)
        for invalid in (b"",b"AGAPAL",b"AGAPAx"+good[6:],
                        good[:6]+pack(">H",2)+good[8:],
                        good[:8]+pack(">H",0)+good[10:],
                        good[:10]+pack(">H",1)+good[12:],
                        good[:12]+pack(">I",1)+good[16:],
                        good[:-1],good+b"\x00",
                        good[:16]+pack(">I",9999)+good[20:],
                        good[:20]+pack(">H",257)+good[22:],
                        good[:22]+pack(">H",2)+good[24:]):
            with self.subTest(length=len(invalid), start=invalid[:16]):
                with self.assertRaises(ValueError):
                    parse_payload(invalid)
        for invalid in (0,-1,65536,"8",1.2):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    payload_size(invalid)

    def test_reject_corrupt_abk(self):
        orig=abk_model(10,init_payload(8))
        for modified in (b"",b"AmBk",
            b"NoBk"+orig[4:],
            orig[:4]+pack(">H",0)+orig[6:],
            orig[:6]+pack(">H",4)+orig[8:],
            orig[:8]+pack(">I",6231)+orig[12:],
            orig[:12]+b"Palette!"+orig[20:],
            orig[:-4],orig+b"\0"):
            with self.subTest(length=len(modified),start=modified[:20]):
                with self.assertRaises(ValueError):
                    parse_abk(modified)

if __name__=="__main__":
    unittest.main(verbosity=2)
