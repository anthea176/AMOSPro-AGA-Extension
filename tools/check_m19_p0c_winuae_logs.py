#!/usr/bin/env python3
"""Check M19 P0c WinUAE log evidence; does not run or certify WinUAE."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

CANDIDATE_SHA256 = '277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a'
CANDIDATE_SIZE = 87020
P0B_SHA256 = 'f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9'
P0B_SIZE = 82376
TEST_ID = 'M19_P0C_SCREEN_CLOSE_BRIDGE_01'
KEYS = ('CANDIDATE SHA256', 'TEST', 'RUN_MODE', 'PRG_STATE', 'RESULT',
        'ERR', 'VERDICT', 'CLOSE_FIRST', 'CLOSE_WITH_DB', 'CLOSE_REOPEN')


def check_log(contents: str, mode: str) -> list[str]:
    """Validate final test log fields, not runtime/Compiler execution itself."""
    found: dict[str, str] = {}
    errors: list[str] = []
    for raw in contents.splitlines():
        line = raw.strip()
        for key in KEYS:
            if line.startswith(key + ' '):
                if key in found:
                    errors.append('duplicate field: ' + key)
                found[key] = line[len(key):].strip()
                break
    expected = {
        'TEST': TEST_ID,
        'CANDIDATE SHA256': CANDIDATE_SHA256,
        'RUN_MODE': mode,
        'PRG_STATE': '1' if mode == 'RUNTIME' else '-1',
        'RESULT': '1', 'ERR': '0', 'VERDICT': 'PASS',
        'CLOSE_FIRST': '1', 'CLOSE_WITH_DB': '1', 'CLOSE_REOPEN': '1',
    }
    for key, value in expected.items():
        if found.get(key) != value:
            errors.append(f'{key}: expected {value!r}, got {found.get(key)!r}')
    return errors


def check_binary(path: Path, size: int, sha256: str) -> list[str]:
    data = path.read_bytes()
    errors = []
    if len(data) != size:
        errors.append(f'size: expected {size}, got {len(data)}')
    digest = hashlib.sha256(data).hexdigest()
    if digest != sha256:
        errors.append(f'SHA256: expected {sha256}, got {digest}')
    return errors


def check_path(label: str, path: Path, check) -> bool:
    try:
        errors = check(path)
    except OSError as exc:
        errors = [str(exc)]
    for error in errors:
        print(f'FAIL {label}: {error}')
    if not errors:
        print(f'PASS {label}: file and expected fields verified')
    return not errors


class SelfTests(unittest.TestCase):
    @staticmethod
    def example(mode: str) -> str:
        vals = {
            'TEST': TEST_ID, 'CANDIDATE SHA256': CANDIDATE_SHA256,
            'RUN_MODE': mode, 'PRG_STATE': '1' if mode == 'RUNTIME' else '-1',
            'RESULT': '1', 'ERR': '0', 'VERDICT': 'PASS',
            'CLOSE_FIRST': '1', 'CLOSE_WITH_DB': '1', 'CLOSE_REOPEN': '1',
        }
        return '\n'.join(f'{key}  {value}' for key, value in vals.items()) + '\n'

    def test_expected_modes(self):
        self.assertEqual(check_log(self.example('RUNTIME'), 'RUNTIME'), [])
        self.assertEqual(check_log(self.example('COMPILED'), 'COMPILED'), [])

    def test_runtime_not_compiled(self):
        self.assertTrue(check_log(self.example('RUNTIME'), 'COMPILED'))

    def test_reject_missing_duplicate_and_fail(self):
        good = self.example('RUNTIME')
        self.assertTrue(check_log(good.replace('ERR  0\n', ''), 'RUNTIME'))
        self.assertTrue(check_log(good + 'RESULT 1\n', 'RUNTIME'))
        self.assertTrue(check_log(good.replace('VERDICT  PASS', 'VERDICT  FAIL'), 'RUNTIME'))

    def test_binary_hash_and_size(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'candidate.Lib'
            path.write_bytes(b'example')
            digest = hashlib.sha256(b'example').hexdigest()
            self.assertEqual(check_binary(path, 7, digest), [])
            self.assertTrue(check_binary(path, 87020, digest))
            self.assertTrue(check_binary(path, 7, '0' * 64))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--installed-lib', type=Path,
                        help='exact AMOSPro_AGA.Lib installed in the WinUAE APSystem slot')
    parser.add_argument('--runtime', type=Path, help='copied RAM:M19_P0C_RUNTIME.TXT')
    parser.add_argument('--compiled', type=Path, help='copied RAM:M19_P0C_COMPILED.TXT')
    parser.add_argument('--restored-p0b', type=Path,
                        help='optional restored P0b AMOSPro_AGA.Lib, checked separately')
    args = parser.parse_args(argv)
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(SelfTests))
        return 0 if result.wasSuccessful() else 1
    if not args.installed_lib or (not args.runtime and not args.compiled):
        parser.error('supply --installed-lib and at least --runtime or --compiled')
    checks = [check_path('INSTALLED P0c LIB', args.installed_lib,
                         lambda p: check_binary(p, CANDIDATE_SIZE, CANDIDATE_SHA256))]
    if args.restored_p0b:
        checks.append(check_path('RESTORED P0b LIB', args.restored_p0b,
                                 lambda p: check_binary(p, P0B_SIZE, P0B_SHA256)))
    for mode, path in (('RUNTIME', args.runtime), ('COMPILED', args.compiled)):
        if path is None:
            print(f'NON TESTE {mode}: no log supplied')
            continue
        checks.append(check_path(mode + ' LOG', path,
                                 lambda p, m=mode: check_log(p.read_text(encoding='latin-1'), m)))
    if not all(checks):
        return 1
    print('LOG PREFLIGHT PASS ONLY: confirm WinUAE return to AMOS, no freeze/Guru,')
    print('actual installed Lib, screenshots, compiler executable and RAM logs manually.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
