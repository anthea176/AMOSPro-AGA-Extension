"""Regression tests: reject malformed historical fixtures, accept in-memory repair."""
from pathlib import Path
import hashlib
import base64
import os
import runpy
import struct
import unittest
from audit_ap20 import FormatError, inspect, parse, structural_candidate, token

ROOT = Path(os.environ.get('AGA_AUDIT_ROOT', Path(__file__).resolve().parents[1]))
M4A = ROOT / 'archive/AMOSPro_AGA_M4a_v0.0.5_WinUAE_OK.Lib'
M4B = [ROOT / ('dist/experimental/AMOSPro_AGA_M4b_v0.0.6'+suffix+'.Lib')
       for suffix in ('', '_R1', '_R2')]


class LoaderAudit(unittest.TestCase):
    def test_official_requester_fixture(self):
        reference = runpy.run_path(str(ROOT / 'tools/build_probe.py'))
        raw = base64.b64decode(reference['REFERENCE_B64'])
        self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                         '0d22cf3365e008413a2d56b920294fda3931a9db')
        result = inspect(parse(raw))
        self.assertEqual(result['issues'], [])
        self.assertEqual(len(result['jumps']), 7)

    def test_baseline_hash_untouched(self):
        self.assertEqual(hashlib.sha256(M4A.read_bytes()).hexdigest(),
                         'ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e')

    def test_historical_container_and_spans_are_valid(self):
        for path in [M4A] + M4B:
            with self.subTest(path=path):
                lib = parse(path.read_bytes())
                self.assertEqual(sum(lib.jumps)*2, len(lib.code))

    def test_baseline_has_latent_detect_defect_but_no_bad_parameter_target(self):
        result = inspect(parse(M4A.read_bytes()))
        self.assertEqual([(x['offset'], x['index']) for x in result['issues']],
                         [(22, 256), (22, 1121)])
        self.assertTrue(all(x['getp'] for x in result['parameter_checks']))

    def test_all_three_m4b_fail_parameter_target_validation(self):
        for path in M4B:
            with self.subTest(path=path):
                result = inspect(parse(path.read_bytes()))
                bad = [x for x in result['parameter_checks'] if not x['getp']]
                self.assertEqual([(x['offset'], x['index'], x['parameters']) for x in bad],
                                 [(182, 3072, 1), (182, 353, 1)])

    def test_each_token_is_even(self):
        for length in range(1, 33):
            for signature in ('I', '0', 'I0', '00,0,0,0'):
                self.assertEqual(len(token('a'*length, 3, 1, signature)) % 2, 0)

    def test_in_memory_candidates_have_correct_dispatch(self):
        for path in M4B:
            with self.subTest(path=path):
                result = inspect(parse(structural_candidate(path.read_bytes())))
                self.assertEqual(result['issues'], [])
                self.assertEqual([(x['index'], x['parameters']) for x in result['parameter_checks']],
                                 [(6, 4), (12, 1)])
                self.assertTrue(all(x['getp'] for x in result['parameter_checks']))
                self.assertEqual([t['offset'] for t in result['tokens']],
                                 [0, 6, 22, 38, 52, 80, 104, 126, 144, 168, 182])

    def test_repair_does_not_change_runtime_code_or_jump_spans(self):
        for path in M4B:
            raw = path.read_bytes()
            a, b = parse(raw), parse(structural_candidate(raw))
            self.assertEqual((a.code, a.jumps, a.title), (b.code, b.jumps, b.title))
            self.assertEqual(a.lengths, b.lengths)
            differences = [i for i, (x, y) in enumerate(zip(raw, b.raw)) if x != y]
            ts = 32+22+a.lengths[0]
            self.assertTrue(differences)
            self.assertTrue(all(ts <= i < ts+a.lengths[1] for i in differences))

    def test_r2_cold_and_pc_relative_targets(self):
        a = parse(M4A.read_bytes())
        r2 = parse(M4B[2].read_bytes())
        self.assertEqual(a.code[:188], r2.code[:188])
        for path, state in [(M4A, 156), (M4B[0], 234), (M4B[1], 234), (M4B[2], 156)]:
            lib = parse(path.read_bytes())
            for field, target in [(12, state), (20, 56), (32, state)]:
                self.assertEqual(field+struct.unpack_from('>h', lib.code, field)[0], target)
            self.assertEqual(lib.code[state:state+32], b'\0'*32)

    def test_missing_getp_rejected(self):
        raw = bytearray(structural_candidate(M4B[2].read_bytes()))
        lib = parse(raw)
        p = 32+22+lib.lengths[0]+lib.lengths[1]+lib.starts[12]-4
        raw[p:p+4] = b'XXXX'
        self.assertTrue(any(x['kind'] == 'missing-GetP' for x in inspect(parse(raw))['issues']))

    def test_hunk_size_corruption_rejected(self):
        raw = bytearray(M4B[2].read_bytes())
        raw[31] ^= 1
        with self.assertRaises(FormatError):
            parse(raw)

    def test_span_corruption_rejected(self):
        raw = bytearray(M4B[2].read_bytes())
        raw[55] ^= 1
        with self.assertRaises(FormatError):
            parse(raw)

    def test_missing_token_terminator_rejected(self):
        lib = parse(structural_candidate(M4B[2].read_bytes()))
        lib.tokens = lib.tokens[:-6]
        with self.assertRaises(FormatError):
            inspect(lib)


if __name__ == '__main__':
    unittest.main(verbosity=2)
