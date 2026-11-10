"""Issue #2: structural regression and known unsafe runtime fixtures.

Passing these tests does NOT approve R4/R5 for execution: rejection of their
runtime defects is the expected result. Uses only the Python standard library.
"""
import os
import re
import struct
import unittest
from pathlib import Path
from audit_ap20 import parse, inspect
from audit_m4b_runtime import segment, compare, open_contract, findings, trace_db_already

ROOT = Path(os.environ.get('AGA_AUDIT_ROOT', Path(__file__).resolve().parents[1]))


class R5Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = {v: (ROOT / ('dist/experimental/AMOSPro_AGA_M4b_v0.0.6_'+v+'.Lib')).read_bytes()
                   for v in ('R4', 'R5')}
        cls.libs = {v: parse(b) for v, b in cls.raw.items()}

    def test_open_and_cold_contract(self):
        open_contract(self.libs['R4'], self.libs['R5'])
        m4a = parse((ROOT/'archive/AMOSPro_AGA_M4a_v0.0.5_WinUAE_OK.Lib').read_bytes())
        open_contract(m4a, self.libs['R5'])

    def test_exact_structural_delta(self):
        a, b = self.libs['R4'], self.libs['R5']
        self.assertEqual([x['index'] for x in compare(a, b)['segments'] if not x['equal']], [8,10,11])
        self.assertEqual([y-x for x,y in zip(a.starts,b.starts)],
                         [0,0,0,0,0,0,0,0,0,20,20,50,114,114])
        self.assertEqual(b.lengths, (28,208,1892,60))
        self.assertEqual(a.tokens, b.tokens)
        self.assertEqual(inspect(b)['issues'], [])
        self.assertEqual([(x['index'],x['parameters'],x['getp']) for x in inspect(b)['parameter_checks']],
                         [(6,4,True),(12,1,True)])

    def test_balanced_span_corruption_detected(self):
        raw = bytearray(self.raw['R5'])
        # Keep total code length valid while moving Open by two bytes.
        for index, delta in [(5,1),(6,-1)]:
            p=32+22+2*index
            struct.pack_into('>H',raw,p,struct.unpack_from('>H',raw,p)[0]+delta)
        with self.assertRaises(ValueError):
            open_contract(self.libs['R4'],parse(raw))

    def test_wrong_but_in_range_open_token_detected(self):
        raw=bytearray(self.raw['R5'])
        struct.pack_into('>H',raw,32+22+28+52+2,7)
        with self.assertRaises(ValueError):
            open_contract(self.libs['R4'],parse(raw))

    def test_open_code_mutation_detected(self):
        raw=bytearray(self.raw['R5'])
        raw[32+22+28+208+654+4] ^= 2
        with self.assertRaises(ValueError):
            open_contract(self.libs['R4'],parse(raw))

    def test_both_versions_are_rejected_for_known_runtime_defects(self):
        for lib in self.libs.values():
            result=findings(lib)
            self.assertEqual([x['entry'] for x in result if x['id']=='a3-not-preserved'],[8,10,11,12])
            self.assertEqual([x['entry'] for x in result if x['id']=='depth-as-db-pointer'],[6])

    def test_false_success_with_depth_in_db_pointer(self):
        for lib in self.libs.values():
            for depth in range(1,9):
                result=trace_db_already(segment(lib,10),depth)
                self.assertEqual((result['d3'],result['a3'],result['os_calls']),(1,depth,0))
                self.assertNotEqual(result['a3'],result['original_a3'])

    def test_ndk_safe_message_offset(self):
        # NDK include_i: Node=14, Message=Node+4+2=20.
        # DBufInfo has APTR+ULONG before SafeMessage; ReplyPort is +14.
        node_size=4+4+1+1+4
        message_size=node_size+4+2
        safe=4+4
        disp=safe+message_size+4+4+4
        self.assertEqual((safe+node_size,disp+node_size),(0x16,0x36))
        self.assertIn(bytes.fromhex('21400016'),segment(self.libs['R5'],11))

    def test_new_smoke_test_is_only_open_close_and_structured_if(self):
        path=ROOT/'tests/M4B_AUDIT_01_OPEN_CLOSE.asc'
        code='\n'.join(x for x in path.read_text().splitlines() if not x.lstrip().startswith("'"))
        code=re.sub(r'"[^"]*"','""',code)
        self.assertNotRegex(code.lower(),r'\bthen\b|aga swap|aga double buffer|aga back fill')
        self.assertEqual(len(re.findall(r'^\s*If\b',code,re.M)),1)
        self.assertEqual(len(re.findall(r'^\s*End If\b',code,re.M)),1)
        self.assertEqual(code.count('Aga Screen Open('),1)
        self.assertEqual(code.count('Aga Screen Close'),1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
