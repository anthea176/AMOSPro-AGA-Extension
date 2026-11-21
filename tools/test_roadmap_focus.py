#!/usr/bin/env python3
"""Keep docs/ROADMAP.md focused on current state and future work.

Historical checkpoints are stored in docs/ROADMAP_HISTORY_2026-11-17.md.
No third-party dependencies. This guard never modifies project files.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs/ROADMAP.md"
ARCHIVE = ROOT / "docs/ROADMAP_HISTORY_2026-11-17.md"
LIB = ROOT / "dist/AMOSPro_AGA.Lib"
ASC_DIR = ROOT / "tests/current"
MAX_CHARS = 9000
MAX_LINES = 110


def check_roadmap(text: str, lib_digest: str, active_asc: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# Roadmap"):
        errors.append("missing roadmap title")
    if len(text) > MAX_CHARS or len(text.splitlines()) > MAX_LINES:
        errors.append(
            f"roadmap too long ({len(text)} chars, "
            f"{len(text.splitlines())} lines); move dated evidence to docs/"
        )
    headings = re.findall(r"(?m)^## (.+)$", text)
    if not (3 <= len(headings) <= 6):
        errors.append(f"expected 3-6 planning headings, found {len(headings)}")
    historical_heading = re.compile(
        r"^(?:M\d+\s+P\d+|R\d+|HISTORIQUE\b|Historique\b|"
        r"ACTIF\b|CANDIDATE\b|ÉTAT\b|Checkpoint\b)",
        re.IGNORECASE,
    )
    if any(historical_heading.search(h) for h in headings):
        errors.append("historical checkpoint heading in active roadmap")
    if lib_digest not in text:
        errors.append("active library SHA256 missing or stale")
    if active_asc not in text:
        errors.append("unique active ASC missing or stale")
    for required in ("LAST_GOOD", "NEXT_SESSION.md", "ROADMAP_HISTORY_2026-11-17.md"):
        if required not in text:
            errors.append(f"missing link or protection: {required}")
    return errors


class RoadmapPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.digest = "a" * 64
        self.asc = "M19_EXAMPLE.asc"
        self.valid = (
            "# Roadmap — AMOSPro AGA Extension\n\n"
            "## 1. État actuel\n"
            f"SHA256 {self.digest}; ASC {self.asc}; LAST_GOOD\n\n"
            "## 2. Priorité\nUn objectif\n\n"
            "## 3. Après M19\nDes pistes\n\n"
            "## 4. Historique séparé\n"
            "Voir NEXT_SESSION.md et ROADMAP_HISTORY_2026-11-17.md.\n"
        )

    def test_compact_valid(self) -> None:
        self.assertEqual(check_roadmap(self.valid, self.digest, self.asc), [])

    def test_history_heading_rejected(self) -> None:
        bad = self.valid + "\n## M19 P0a — ancien checkpoint\n"
        self.assertIn(
            "historical checkpoint heading in active roadmap",
            check_roadmap(bad, self.digest, self.asc),
        )

    def test_bloat_rejected(self) -> None:
        self.assertTrue(any("too long" in error for error in
                            check_roadmap(self.valid + "x" * 10000, self.digest, self.asc)))

    def test_stale_identity_rejected(self) -> None:
        self.assertTrue(any("SHA256" in error for error in
                            check_roadmap(self.valid, "b" * 64, self.asc)))
        self.assertTrue(any("ASC" in error for error in
                            check_roadmap(self.valid, self.digest, "OLD.asc")))


def main() -> int:
    archive = ARCHIVE.read_text(encoding="utf-8")
    if not archive.startswith("> **ARCHIVE NON NORMATIVE"):
        print("FAIL: historical roadmap not marked non-normative")
        return 1
    asc = sorted(ASC_DIR.glob("*.asc"))
    if len(asc) != 1:
        print(f"FAIL: exactly one ASC must be active, found {[p.name for p in asc]}")
        return 1
    text = ROADMAP.read_text(encoding="utf-8")
    errors = check_roadmap(text, sha256(LIB.read_bytes()).hexdigest(), asc[0].name)
    if errors:
        for error in errors:
            print("FAIL roadmap:", error)
        return 1
    print(
        f"PASS: {ROADMAP.relative_to(ROOT)} is focused "
        f"({len(text)} chars, {len(text.splitlines())} lines), "
        f"active ASC {asc[0].name}, current Lib SHA256."
    )
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(RoadmapPolicyTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    sys.exit(main())
