#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only regression of the 68020 M19 P2d assembler migration."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from active_library import P2D_SHA
from export_m19_p2d_native_source import generate
from decoder68k import Decoder


class P2dNativeSourceTest(unittest.TestCase):
    def test_mc68020_direct_register_bitfield_decodes_exactly(self):
        # Source emitter opcode $E9C5, extension $17C1, then TST.L D1.
        raw=bytes.fromhex('e9c517c14a81')
        dec=Decoder(raw,allow_scaled_index=True)
        first=dec.decode(0)
        self.assertIsNotNone(first)
        self.assertEqual(first.size,4)
        self.assertEqual(first.text,'bfextu d5{31:1},d1')
        self.assertEqual(dec.decode(4).text,'tst.l d1')

    def test_lossless_builder_and_real_mnemonics(self):
        with tempfile.TemporaryDirectory(prefix='p2d_asm_') as directory:
            before=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
            frozen=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
            m=generate(Path(directory))
            self.assertEqual(m['input_sha256'],P2D_SHA)
            self.assertEqual(m['input_bytes'],136020)
            self.assertEqual(m['ap20_entries'],203)
            self.assertEqual(m['commands'],100)
            self.assertTrue(m['builder_exact_match'])
            self.assertEqual(len(m['native_groups']),4)
            for report in m['native_groups']:
                print('GROUP', report['file'], 'bytes', report['bytes'], 'mnemonic', report['mnemonic_bytes'], 'data', report['raw_dc_bytes'], flush=True)
                text=(Path(directory)/report['file']).read_text()
                self.assertIn('move.',text)
                self.assertIn('rts',text)
                self.assertLessEqual(report['unresolved_instruction_encodings'],8,
                                     report['file'])
                self.assertGreater(report['mnemonic_bytes'] / report['bytes'],.72,
                                   report['file'])
            p2d=next(x for x in m['native_groups'] if 'BOBS' in x['file'])
            bobtext=(Path(directory)/p2d['file']).read_text()
            self.assertIn('p2d_public_auto_update:',bobtext)
            self.assertIn('p2d_public_swap:',bobtext)
            self.assertIn('p2d_close:',bobtext)
            self.assertIn('p2d_mode:',bobtext)
            self.assertTrue((Path(directory)/m['linked_file']).is_file())
            self.assertEqual((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes(),before)
            self.assertEqual((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes(),frozen)
            print('P2d SOURCE-BACKED ASM PASS:',
                  [(g['file'],g['mnemonic_bytes'],g['raw_dc_bytes'])
                   for g in m['native_groups']])


if __name__=='__main__':
    unittest.main(verbosity=2)