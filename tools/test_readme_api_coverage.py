#!/usr/bin/env python3
"""Verify English/French public README coverage against the active AP20 library.

Run: python -B tools/test_readme_api_coverage.py
No third-party dependency. Both languages must document every named token,
the exact call signatures and the active binary version.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import re

from audit_ap20 import inspect, parse

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "dist/AMOSPro_AGA.Lib"  # Active candidate, with explicit Gate limits.
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
    # A link to the active .Lib is not proof that the README describes it:
    # validate the first version summary against the *current binary bytes*.
    summary = readme.split(library_heading, 1)[1].strip().splitlines()[0]
    digest = sha256(LIB.read_bytes()).hexdigest()
    assert digest in summary, (
        f"{language}: active library SHA256 absent/stale in README summary"
    )
    count_label = "commandes" if language == "Français" else "commands"
    assert re.search(rf"\b{len(exported)}\s+{count_label}\b", summary), (
        f"{language}: README summary does not report {len(exported)} public commands"
    )
    assert release.split()[0] in summary, (
        f"{language}: active release {release!r} missing from library summary"
    )
    # Keep the README as a quick-start: historical benchmarks and checkpoints
    # belong in docs/ rather than being accumulated before the API table.
    overview = readme.split(library_heading, 1)[1].split(api_heading, 1)[0].strip()
    paragraphs = [p for p in overview.split("\n\n") if p.strip()]
    assert len(overview) <= 1800 and 1 <= len(paragraphs) <= 3, (
        f"{language}: Libraries and tests grew too long "
        f"({len(overview)} characters, {len(paragraphs)} paragraphs); "
        f"move historical detail to docs/"
    )
    active_tests = sorted((ROOT / "tests/current").glob("*.asc"))
    assert len(active_tests) == 1 and active_tests[0].name in overview, (
        f"{language}: library overview must link to the unique active ASC"
    )
    assert "LIBRARY_TEST_HISTORY" in overview and "LAST_GOOD" in overview, (
        f"{language}: historical versions and protected LAST_GOOD need links"
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
        match = re.search(r"`((?:Aga|Get AGA|Make AGA|No AGA) [^`]+)`", first)
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
        if token["name"].lower().startswith(("aga ", "get aga ", "make aga ", "no aga "))
    }
    assert exported, "No named AP20 commands found in current library"
    title = library.title.decode("latin-1")
    # M19 P0a/P0b/P0c titles have different $VER suffixes. Read the
    # actual M19 milestone, never infer the active version from an R88 base.
    m19 = re.search(
        r"\$VER:\s*AMOSPro_AGA\s+(M\d+\s+P\d+[a-z]?)\b",
        title, re.IGNORECASE,
    )
    islands = re.search(r"\$VER:\s*AGA\s+M19\s+AP20\s+islands\b", title, re.IGNORECASE)
    b7 = re.search(r"\$VER:\s*AGA\s+(M19\s+P0j-b7)\b", title, re.IGNORECASE)
    if b7:
        assert sha256(LIB.read_bytes()).hexdigest() == "f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b", "B7 release must be exact source-built canonical"
        release = "M19 P0j-b7"
    elif islands:
        assert "M19 AP20 V2 ISLAND DISPATCH" in title, "Unexpected AP20 island title"
        release = "M19 AP20 ISLANDS"
    elif m19:
        release = m19.group(1)
    else:
        # Older Rxx candidates keep their historical $VER syntax.
        revision = re.search(r"\bR(\d+)\b", title)
        version = re.search(r"\$VER:\s*AMOSPro_AGA\s+(\d+\.\d+\.\d+)", title)
        assert revision and version, "Cannot read active AP20 release from $VER"
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
