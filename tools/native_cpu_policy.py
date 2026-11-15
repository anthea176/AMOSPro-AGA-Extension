#!/usr/bin/env python3
"""Fail-closed review gate for changed native AGA sources (not a CPU emulator).

Only newly added or modified files are checked. Pre-existing emitters are
historical evidence, not automatic approval to reuse them in a new build.

Usage: python tools/native_cpu_policy.py --base <old-git-sha> --head <new-git-sha>
       python tools/native_cpu_policy.py --self-test
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
import unittest

NATIVE_MARKER = "AGA_NATIVE_MIN_CPU: MC68020"
AUDIT_MARKER = "AGA_NATIVE_PURPOSE: AUDIT_ONLY"
ASM_SUFFIXES = (".s", ".asm", ".inc")
TARGET_000 = re.compile(
    r"(?i)(?:-m68000\b|-m68010\b|\b(?:CPU_TARGET|MIN_CPU|AGA_NATIVE_MIN_CPU)"
    r"\s*[:=]\s*['\" ]*(?:m|mc)?680(?:00|10)\b)"
)
DUAL_000 = re.compile(r"(?i)\b(?:68000|68010)\s*/\s*(?:68020|020)\b")
EMITTER_IMPORT = re.compile(r"(?m)^\s*(?:from\s+m68k_emit\s+import|import\s+m68k_emit\b)")
AUDIT_IMPORT = re.compile(r"(?m)^\s*(?:from\s+decoder68k\s+import|import\s+decoder68k\b)")


def policy_errors(path: str, content: str) -> list[str]:
    """Return diagnostics for a changed source, no repository access needed."""
    p = Path(path)
    if not p.parts or p.parts[0] not in ("tools", "src"):
        return []
    if p.name.startswith("test_") or p.name.endswith("_test.py"):
        return []
    suffix = p.suffix.lower()
    is_native = suffix in ASM_SUFFIXES or (
        suffix == ".py" and
        (p.name.endswith("_emit.py") or EMITTER_IMPORT.search(content) is not None)
    )
    is_binary_audit = suffix == ".py" and not is_native and (
        AUDIT_IMPORT.search(content) is not None or
        "def source_binary_from_input(" in content
    )
    errors = []
    # Exported disassembly is evidence, not development source. It must be
    # marked AUDIT_ONLY and must never carry the development CPU declaration.
    header = content[:1500]
    audit_only = re.search(r"(?m)^\s*(?:#|;)\s*" + re.escape(AUDIT_MARKER) + r"\s*$", header) is not None
    native_target = re.search(r"(?m)^\s*(?:#|;)\s*" + re.escape(NATIVE_MARKER) + r"\s*$", header) is not None
    if is_native and audit_only:
        if native_target:
            errors.append("source AUDIT_ONLY et cible de developpement simultanees")
        return errors
    if is_native:
        # Require marker in the file itself, not in a cited historical report.
        if not native_target:
            errors.append("nouveau code natif sans declaration " + NATIVE_MARKER)
        if TARGET_000.search(content):
            errors.append("nouvelle cible 68000/68010 interdite")
        if DUAL_000.search(content[:1500]):
            errors.append("description ambiguë de cible 68000/020 interdite")
    elif is_binary_audit:
        if not audit_only:
            errors.append("decodeur/exporteur binaire sans declaration " + AUDIT_MARKER)
    return errors


def changed_paths(base: str, head: str) -> list[str]:
    # Fetch depth 0 in CI. If base is missing, do not silently report PASS.
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", base, head, "--", "tools", "src"],
        text=True, capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError("git diff impossible: " + result.stderr.strip())
    return sorted(set(result.stdout.splitlines()))


def run_policy(base: str, head: str) -> int:
    paths = changed_paths(base, head)
    problems = 0
    examined = 0
    for path in paths:
        p = Path(path)
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as exc:
            print(f"FAIL {path}: source impossible a lire: {exc}")
            problems += 1
            continue
        examined += 1
        for error in policy_errors(path, content):
            print(f"FAIL {path}: {error}")
            problems += 1
    if problems:
        print(f"FAIL CPU policy: {problems} violation(s) sur {examined} fichier(s) changes")
        return 1
    print(f"PASS CPU policy: {examined} fichier(s) changes controles; historique non requalifie")
    return 0


class NativePolicyTests(unittest.TestCase):
    def test_reject_unmarked_68000_emitter(self):
        raw = '"""native 68000/020 emitter"""\nfrom m68k_emit import Code\n'
        self.assertTrue(policy_errors('tools/m20_new_emit.py', raw))

    def test_reject_68000_even_if_marker_is_020(self):
        raw = '# '+NATIVE_MARKER+'\nfrom m68k_emit import Code\nCPU_TARGET="m68000"\n'
        self.assertTrue(policy_errors('tools/m20_new_emit.py', raw))

    def test_reject_double_target_in_header(self):
        raw = '# '+NATIVE_MARKER+'\n"""native 68000/020 emitter"""\n'
        self.assertTrue(policy_errors('tools/m20_new_emit.py', raw))

    def test_accept_020_emitter_with_68000_compatible_instructions(self):
        raw = '# '+NATIVE_MARKER+'\nfrom m68k_emit import Code\n# MOVE.L is also 68000 compatible.\n'
        self.assertEqual(policy_errors('tools/m20_new_emit.py', raw), [])

    def test_accept_020_asm(self):
        self.assertEqual(policy_errors('src/m20/new.s', '; '+NATIVE_MARKER+'\n move.l d0,d1\n'), [])

    def test_allow_explicitly_audit_only_disassembly(self):
        self.assertEqual(policy_errors('src/generated/reconstruction.s',
                                       '; '+AUDIT_MARKER+'\n dc.b $01,$02\n'), [])
        self.assertTrue(policy_errors('src/generated/reconstruction.s',
                                      '; '+AUDIT_MARKER+'\n; '+NATIVE_MARKER+'\n'))

    def test_require_audit_marker_for_decoder(self):
        raw = 'from decoder68k import Decoder\n'
        self.assertTrue(policy_errors('tools/generate_other_source.py',raw))
        self.assertEqual(policy_errors('tools/generate_other_source.py','# '+AUDIT_MARKER+'\n'+raw), [])

    def test_do_not_retroactively_block_historical_tests(self):
        raw = 'from m68k_emit import Code\nCPU_TARGET="m68000"\n'
        self.assertEqual(policy_errors('tools/test_old_emit.py', raw), [])
        self.assertEqual(policy_errors('docs/OLD.md', raw), [])

    def test_require_marker_for_new_raw_asm(self):
        self.assertTrue(policy_errors('src/module.asm',' moveq #0,d0\n'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base')
    parser.add_argument('--head')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(NativePolicyTests)
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        sys.exit(0 if result.wasSuccessful() else 1)
    if not args.base or not args.head:
        parser.error('--base et --head obligatoires, ou --self-test')
    try:
        sys.exit(run_policy(args.base, args.head))
    except RuntimeError as exc:
        print('FAIL CPU policy:',exc)
        sys.exit(2)
