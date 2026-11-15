#!/usr/bin/env python3
"""Regression tests for the conservative AMOS Professional preflight checker."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from amos_preflight import analyze_source, read_asc, remove_strings_comments


# Exact code pattern established by AMOSPro-AGA-Extension examples/screen.asc.
KNOWN_GOOD_SCREEN = '''Cls
Print "AGA SCREEN - 320 X 256"
If Aga Detect=0
   Print "AGA CHIPSET NOT DETECTED"
   End
End If
_OK=Aga Screen Open(320,256,256,$00021000)
If _OK<>1
   Print "SCREEN OPEN FAILED"
   End
End If
Aga Screen Pattern
Amos To Back
For _I=1 To 150
   Aga Wait Vbl
Next _I
Aga Screen Close
Amos To Front
End
'''


class PreflightTests(unittest.TestCase):
    def lint(self, text: str, *, strict: bool = False, encoding: str = "utf-8"):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "program.asc"
            path.write_bytes(text.encode(encoding))
            return analyze_source(path, strict_target=strict)

    def codes(self, text: str) -> set[str]:
        return {item.code for item in self.lint(text)}

    def test_reference_screen_clean(self):
        self.assertEqual(self.lint(KNOWN_GOOD_SCREEN), [])

    def test_structured_if_nested_then_rejected(self):
        self.assertIn("THEN_IN_STRUCTURED_IF", self.codes(
            "If _A<>0\n If _B<>0 Then _OK=1\nEnd If\n"))

    def test_structured_if_nested_without_then_accepted(self):
        self.assertEqual(self.lint(
            "If _A<>0\n If _B<>0\n  _OK=1\n End If\nEnd If\n"), [])

    def test_inline_if_independent_allowed(self):
        self.assertEqual(self.lint("If _A<>0 Then _B=1\n"), [])

    def test_colon_structured_if_allowed(self):
        self.assertEqual(self.lint("If _A<>0 : _B=1 : End If\n"), [])

    def test_else_if_and_else(self):
        self.assertEqual(self.lint("If _A=0\n _B=0\nElse If _A=1\n _B=1\nElse\n _B=2\nEnd If\n"), [])

    def test_unclosed_if_rejected(self):
        self.assertIn("IF_UNCLOSED", self.codes("If _A=1\n Print 1\n"))

    def test_global_before_dim_rejected(self):
        self.assertIn("GLOBAL_BEFORE_DIM", self.codes("Global _A()\nDim _A(5)\n"))

    def test_dim_before_global_accepted(self):
        self.assertEqual(self.lint("Dim _A(5),_B(2)\nGlobal _A(),_B()\n"), [])

    def test_pop_proc_return_rejected(self):
        self.assertIn("POP_PROC_RETURN", self.codes(
            "Procedure _Check[_X]\n _R=0\n If _X=0 : Pop Proc : End If\nEnd Proc[_R]\n"))

    def test_pop_proc_without_return_allowed(self):
        self.assertEqual(self.lint("Procedure _Check[_X]\nPop Proc\nEnd Proc\n"), [])

    def test_restore_local_scope_warning(self):
        self.assertIn("RESTORE_SCOPE", self.codes(
            "Procedure _Test\nRestore _Data\nEnd Proc\n"))

    def test_physical_line_hard_limit(self):
        self.assertIn("LINE_255", self.codes("'" + "x" * 256 + "\n"))

    def test_physical_line_target_warning_and_strict_failure(self):
        line = "'" + "x" * 230 + "\n"
        self.assertEqual(self.lint(line)[0].level, "AVERTISSEMENT")
        self.assertEqual(self.lint(line, strict=True)[0].level, "ERREUR")

    def test_zero_count_loop_review(self):
        self.assertIn("ZERO_COUNT_LOOP", self.codes("For _I=0 To _COUNT-1\nNext _I\n"))

    def test_set_zone_zero_warning(self):
        self.assertIn("ZONE_ZERO", self.codes("Set Zone _ZONE,0,0 To 0,0\n"))

    def test_aga_detect_minus_one_issue(self):
        self.assertIn("AGA_DETECT_BOOLEAN", self.codes("If Aga Detect=1\nEnd If\n"))

    def test_aga_missing_cleanup(self):
        codes = self.codes("_OK=Aga Screen Open(320,256,256,$00021000)\n")
        self.assertIn("AGA_MISSING_CLOSE", codes)
        self.assertIn("AGA_MISSING_FRONT", codes)

    def test_aga_bob_probe_not_r87(self):
        self.assertIn("AGA_BOB_PROBE", self.codes("_N=Aga Bob Probe(0)\n"))

    def test_strings_and_comments_do_not_trigger(self):
        self.assertEqual(self.lint("Print \"If _X=1 Then _Y=2: Aga Bob Probe\"\n' If _X=1\n"), [])
        self.assertEqual(remove_strings_comments('Print "L\'a:Then" : _A=1'),
                         'Print            : _A=1')

    def test_cp1252_roundtrip_readonly(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "cp1252.asc"
            data = "' exemple e accentue: é\r\n".encode("cp1252")
            path.write_bytes(data)
            source, encoding = read_asc(path)
            self.assertEqual(encoding, "cp1252")
            self.assertIn("é", source)
            self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
