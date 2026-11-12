#!/usr/bin/env python3
"""Verify English/French public README coverage against the active AP20 library.

Run: python -B tools/test_readme_api_coverage.py
No third-party dependency. Both languages must document every named token,
the exact call signatures and the active binary version.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from audit_ap20 import inspect, parse

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "dist/AMOSPro_AGA.Lib"
READMES = (
    (
        "English",
        ROOT / "README.md",
        "## Libraries and tests",
        "## Main AMOS commands",
        "### AGA mouse details",
        "| Command | Exact syntax | Parameters and behaviour |",
        "Current library API",
    ),
    (
        "Français",
        ROOT / "README.fr.md",
        "## Bibliothèques et tests",
        "## Commandes AMOS principales",
        "### Détail : Souris AGA",
        "| Commande | Syntaxe exacte | Paramètres et comportement |",
        "API de la bibliothèque courante",
    ),
)


def check_readme(
    language: str,
    path: Path,
    library_heading: str,
    api_heading: str,
    api_end: str,
    table_header: str,
    version_heading: str,
    exported: dict,
    release: str,
) -> dict[str, str]:
    readme = path.read_text(encoding="utf-8")
    assert readme.startswith("# AMOSPro AGA Extension\n\n"), (
        f"{language}: missing main heading"
    )
    assert readme.count(library_heading) == 1, (
        f"{language}: missing/duplicated library heading"
    )
    intro = readme.split(library_heading, 1)[0]
    assert len(intro) <= 1400 and intro.endswith("\n\n"), (
        f"{language}: keep the introduction short"
    )
    assert not re.search(r"(?m)^#{2,6}\s", intro), (
        f"{language}: no extra sections before library documentation"
    )
    assert not re.search(r"(?im)^\s*(?:[-*]\s|\d+\.\s)", intro), (
        f"{language}: no lists or release history before library documentation"
    )
    assert not re.search(
        r"(?i)\b(?:R\d{1,3}\s+\d+\.\d+\.\d+|checkpoint|gate [a-d])\b",
        intro,
    ), f"{language}: move historical checkpoints to docs/"

    assert readme.count(api_heading) == 1, (
        f"{language}: missing/duplicated API heading"
    )
    assert readme.count(api_end) == 1, (
        f"{language}: missing/duplicated mouse API detail heading"
    )
    table = readme.split(api_heading, 1)[1].split(api_end, 1)[0]
    assert table_header in table, f"{language}: malformed API table header"
    marker = f"**{version_heading} {release}**"
    assert marker in table, (
        f"{language}: wrong README API version, expected {marker!r}"
    )

    documented: dict[str, str] = {}
    names: list[str] = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 5:
            raise AssertionError(f"{language}: malformed API row: {line}")
        first, syntax, description = (x.strip() for x in cells[1:4])
        match = re.search(r"`(Aga [^`]+)`", first)
        if not match:
            continue
        name = match.group(1).casefold()
        names.append(name)
        if not syntax or "`" not in syntax or len(description) < 20:
            raise AssertionError(f"{language}: incomplete API description: {name}")
        documented[name] = syntax

    duplicates = sorted(
        name for name, count in Counter(names).items() if count > 1
    )
    missing = sorted(set(exported) - set(documented))
    stale = sorted(set(documented) - set(exported))
    assert not duplicates and not missing and not stale, (
        f"{language}: README/AP20 mismatch: "
        f"missing={missing}, stale={stale}, duplicates={duplicates}"
    )
    for name, token in exported.items():
        example = documented[name]
        if token["function"] > 1 and token["instruction"] == 1:
            assert "=" in example, (
                f"{language}: missing result assignment for function {name}"
            )
        elif token["instruction"] > 1 and token["function"] == 1:
            assert "=" not in example, (
                f"{language}: instruction shown as function: {name}"
            )
    return documented


def main() -> None:
    library = parse(LIB.read_bytes())
    audit = inspect(library)
    assert not audit["issues"], f"AP20 invalid: {audit['issues']}"
    exported = {
        token["name"].casefold(): token
        for token in audit["tokens"]
        if token["name"].lower().startswith("aga ")
    }
    assert exported, "No named AP20 commands found in current library"
    title = library.title.decode("latin-1")
    # Compiler-safe R46 C1 retains the exact user-tested title
    # "R46 Compiler Gate C candidate 0.12.1-C1".
    revision = re.search(r"\bR(\d+)\b", title)
    version = re.search(r"\$VER:\s*AMOSPro_AGA\s+(\d+\.\d+\.\d+)", title)
    assert revision and version, "Cannot read Rxx and $VER from current AP20 title"
    release = f"R{revision.group(1)} {version.group(1)}"

    english = check_readme(*READMES[0], exported, release)
    french = check_readme(*READMES[1], exported, release)
    assert english == french, (
        "English/French README command signatures differ: "
        + repr({
            name: (english.get(name), french.get(name))
            for name in exported if english.get(name) != french.get(name)
        })
    )
    print(
        f"Bilingual README API PASS: {len(exported)} named AP20 commands "
        f"documented in English and French with identical exact syntax; "
        f"active library {release} matched."
    )


if __name__ == "__main__":
    main()
