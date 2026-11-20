#!/usr/bin/env python3
"""Block accidental alternative AGA Libs, ZIP deliveries and misplaced ASC tests.

Run on the Git diff, so existing archives are preserved without retroactive edits.
A CI failure is a guardrail, not a substitute for protected-branch rules.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
import unittest


ARCHIVES = ('dist/experimental/', 'tests/passed/', 'tests/historical/', 'tests/fixtures/')
CANONICAL_LIB = 'dist/AMOSPro_AGA.Lib'
PROTECTED_LIB = 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
# Only the exact author-approved R84 -> M19 P0 binary transition is exempt.
PROMOTION_R84_BLOB = '9c6c52a1d857c89089b2540b438b76efbf80c77b'
PROMOTION_P0_BLOB = '6e23a1dc783145adb41f1a9b02fc6fc8f3b80ff2'
PUBLIC_VERSION = re.compile(r'(?:^|[/_-])(?:M\d+|R\d+)(?=[_/.]|$)', re.I)


def path_errors(path: str, *, deleted: bool = False, approved_p0: bool = False) -> list[str]:
    """Check destinations and protect histories, including removals.

    Public version-free examples/*.asc are not the single active test. Removing
    an old versioned public example is allowed to normalize its filename.
    """
    path = path.replace('\\', '/')
    errors = []
    if (path == PROTECTED_LIB and not approved_p0) or path.startswith(ARCHIVES):
        errors.append('protected historical asset: explicit separate authorization required')
    if (path.startswith('dist/') and path.lower().endswith('.lib') and
            path != CANONICAL_LIB and not (path == PROTECTED_LIB and approved_p0)):
        if not errors:
            errors.append('AGA Lib may only be delivered as dist/AMOSPro_AGA.Lib')
    if path.startswith('dist/') and path.lower().endswith('.zip'):
        if not errors:
            errors.append('ZIP is not an AGA Lib delivery destination')
    if path.lower().endswith('.asc') and not path.startswith('tests/current/'):
        if path.startswith('examples/'):
            if not deleted and PUBLIC_VERSION.search(path[len('examples/'):]):
                errors.append('public AMOS example ASC needs a version-free filename')
        elif not errors:
            errors.append('active AMOS test must live in tests/current/')
    return errors


def workflow_errors(path: str, content: str) -> list[str]:
    if not path.startswith('.github/workflows/') or not path.endswith(('.yml', '.yaml')):
        return []
    # A workflow that touches the AGA release slot must never push itself.
    release_related = any(x in content for x in ('AMOSPro_AGA', 'dist/', 'dist\/'))
    errors = []
    if release_related and (re.search(r'\bgit\s+push\b', content) or
                            re.search(r'(?m)^\s*contents:\s*write\s*$', content)):
        errors.append('AGA release workflow must be read-only (no git push / contents: write)')
    # A Gate A may verify exact binaries in RAM, but must not distribute a
    # second installable Lib/ZIP via GitHub Actions artifacts.
    for step in re.split(r'(?m)^[ \t]*-[ \t]*name:[ \t]*', content)[1:]:
        if (re.search(r'(?m)^[ \t]*uses:[ \t]*actions/upload-artifact@', step)
                and re.search(r'(?i)\.(?:lib|zip)\b', step)):
            errors.append('AGA library/ZIP artifacts forbidden; use canonical dist/AMOSPro_AGA.Lib')
    return errors


def changed_files(base: str, head: str) -> list[str]:
    proc = subprocess.run(['git', 'diff', '--name-only', '--no-renames', base, head],
                          text=True, capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError('cannot compare Git commits: ' + proc.stderr.strip())
    return sorted(set(proc.stdout.splitlines()))


def exact_p0_promotion(base: str, head: str) -> bool:
    """Fail closed: only exact R84 -> P0 blobs with unchanged active P0."""
    pins=(
        (f'{base}:{PROTECTED_LIB}',PROMOTION_R84_BLOB),
        (f'{base}:{CANONICAL_LIB}',PROMOTION_P0_BLOB),
        (f'{head}:{PROTECTED_LIB}',PROMOTION_P0_BLOB),
        (f'{head}:{CANONICAL_LIB}',PROMOTION_P0_BLOB),
    )
    for obj,expected in pins:
        proc=subprocess.run(['git','rev-parse','--verify',obj],
                            capture_output=True,text=True,check=False)
        if proc.returncode or proc.stdout.strip()!=expected:
            return False
    return True


def run_check(base: str, head: str) -> int:
    issues = []
    paths=changed_files(base, head)
    approved=PROTECTED_LIB in paths and exact_p0_promotion(base, head)
    for path in paths:
        issues.extend((path, msg) for msg in path_errors(
            path, deleted=not Path(path).exists(),
            approved_p0=(path==PROTECTED_LIB and approved)))
        if path.startswith('.github/workflows/'):
            p = Path(path)
            if p.is_file():
                issues.extend((path, msg) for msg in workflow_errors(path, p.read_text(encoding='utf-8')))
    # Ensure only a single real test ASC can be active at a time.
    current = sorted(p.name for p in Path('tests/current').glob('*.asc'))
    if len(current) != 1:
        issues.append(('tests/current/', f'exactly one active ASC required; found {current!r}'))
    for path, msg in issues:
        print(f'FAIL delivery policy: {path}: {msg}')
    if issues:
        print(f'FAIL: {len(issues)} AGA delivery violation(s)')
        return 1
    print('PASS delivery policy: canonical dist/ Lib, single tests/current ASC, protected archives; exact P0 promotion:', approved)
    return 0


class DeliveryPolicyTests(unittest.TestCase):
    def test_canonical_delivery_paths(self):
        for path in ('dist/AMOSPro_AGA.Lib', 'tests/current/NEW.asc',
                     'tools/build_m19.py', 'docs/STATUS.md'):
            self.assertEqual(path_errors(path), [], path)

    def test_reject_experimental_library(self):
        self.assertTrue(path_errors('dist/experimental/M19_NEW.Lib'))

    def test_reject_zip_substitute(self):
        self.assertTrue(path_errors('dist/experimental/M19_WINUAE.zip'))
        self.assertTrue(path_errors('dist/M19_WINUAE.zip'))

    def test_protect_last_good(self):
        self.assertTrue(path_errors(PROTECTED_LIB))
        self.assertEqual(path_errors(PROTECTED_LIB, approved_p0=True), [])
        self.assertTrue(path_errors('dist/experimental/OLD.Lib', approved_p0=True))

    def test_protect_histories(self):
        for path in ('tests/passed/OLD.asc', 'tests/fixtures/test.abk',
                     'tests/historical/OLD.asc', 'dist/experimental/OLD.Lib'):
            self.assertTrue(path_errors(path), path)

    def test_reject_test_in_examples(self):
        self.assertTrue(path_errors('examples/m19/new.asc'))
        self.assertTrue(path_errors('examples/m19_p0a_68020/M19_P0A_MC68020_BANK_GET.asc'))
        self.assertTrue(path_errors('tests/design/new.asc'))

    def test_allow_version_free_public_examples_and_old_name_cleanup(self):
        self.assertEqual(path_errors('examples/aga_bob_bank_get/BANK_GET_MULTI.asc'), [])
        self.assertEqual(path_errors('examples/m19_p0a_68020/M19_P0A_MC68020_BANK_GET.asc',
                                     deleted=True), [])
        self.assertTrue(path_errors('tests/passed/OLD.asc', deleted=True))

    def test_reject_renamed_library(self):
        self.assertTrue(path_errors('dist/AMOSPro_AGA_M20.Lib'))

    def test_read_only_workflow_accepted(self):
        self.assertEqual(workflow_errors('.github/workflows/m19-p0a-publish-github.yml',
                                         'permissions:\n  contents: read\n# dist/AMOSPro_AGA.Lib\n'), [])

    def test_self_publishing_workflow_rejected(self):
        raw = 'permissions:\n  contents: write\nrun: git push origin HEAD:main\n# dist/experimental/FILE.Lib'
        self.assertTrue(workflow_errors('.github/workflows/test.yml', raw))

    def test_reject_library_artifact(self):
        raw = ('jobs:\n  a:\n    steps:\n'
               '      - name: Bad binary publication\n'
               '        uses: actions/upload-artifact@v4\n'
               '        with:\n'
               '          path: m19_p0c_uninstalled/AMOSPro_AGA.Lib\n')
        self.assertTrue(workflow_errors('.github/workflows/test.yml', raw))

    def test_reject_zip_artifact(self):
        raw = ('      - name: Bad ZIP\n'
               '        uses: actions/upload-artifact@v4\n'
               '        with:\n'
               '          path: m19_p0c_uninstalled/install.zip\n')
        self.assertTrue(workflow_errors('.github/workflows/test.yml', raw))

    def test_allow_log_artifact(self):
        raw = ('      - name: Gate A logs\n'
               '        uses: actions/upload-artifact@v4\n'
               '        with:\n'
               '          path: results/*.txt\n')
        self.assertEqual(workflow_errors('.github/workflows/test.yml', raw), [])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base')
    parser.add_argument('--head')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryPolicyTests))
        sys.exit(0 if result.wasSuccessful() else 1)
    if not args.base or not args.head:
        parser.error('--base and --head required, or --self-test')
    try:
        sys.exit(run_check(args.base, args.head))
    except (OSError, RuntimeError, UnicodeError) as exc:
        print('FAIL delivery policy:', exc)
        sys.exit(2)
