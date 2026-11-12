"""R46 C1 native-source restoration: exact Compiler wrapper provenance only.

Run: python -m unittest discover -s tests -p 'test_native_source_c1.py' -v
No library is generated, installed or modified.
"""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_aga_native_source as export

CURRENT=ROOT/'dist/AMOSPro_AGA.Lib'
FROZEN=ROOT/'dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib'


class CompilerSafeSourceTests(unittest.TestCase):
    def test_official_c1_extract_exact_native_without_edit(self):
        official=CURRENT.read_bytes()
        native=FROZEN.read_bytes()
        self.assertEqual(export.sha(official),export.PROMOTED_R46_C1_SHA)
        self.assertEqual(export.sha(native),export.NATIVE_R46_SHA)
        recovered,meta=export.source_binary_from_input(official)
        self.assertEqual(recovered,native)
        self.assertTrue(meta['verified_extract_and_rewrap'])
        self.assertEqual(meta['official_entries'],57)
        self.assertEqual(meta['native_entries'],56)
        self.assertFalse(export.unclassified_gaps(export.parse_lib(recovered)))
        self.assertEqual(CURRENT.read_bytes(),official)
        self.assertEqual(FROZEN.read_bytes(),native)

    def test_current_strict_cli_exports_c1_native_view_only(self):
        original=CURRENT.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(export.main(['--lib',str(CURRENT),'--out',folder,
                                          '--baseline','none','--strict']),0)
            files=list(Path(folder).glob('*_NATIVE.s'))
            self.assertEqual(len(files),1)
            self.assertEqual(files[0].name,'AMOSPro_AGA_R46_C1_NATIVE.s')
            self.assertIn('NOT an installable',files[0].read_text(encoding='ascii'))
            self.assertEqual(len(list(Path(folder).glob('*_NATIVE.json'))),1)
        self.assertEqual(CURRENT.read_bytes(),original)

    def test_tampered_dispatcher_or_stub_fails_closed(self):
        original=CURRENT.read_bytes()
        parsed=export.parse_lib(original)
        for index in (0,len(parsed['section'])-1):
            corrupted=bytearray(original)
            corrupted[parsed['section'][index]['file_offset']]^=1
            with self.subTest(index=index):
                with self.assertRaises(export.ExportError):
                    export.source_binary_from_input(bytes(corrupted))

    def test_historical_native_remains_supported(self):
        original=FROZEN.read_bytes()
        restored,meta=export.source_binary_from_input(original)
        self.assertEqual(restored,original)
        self.assertIsNone(meta)


if __name__=='__main__':
    unittest.main()
