#!/usr/bin/env python3
"""Static AMOS guard: Copper, Mouse, Hotspot, Rect and AGA Text functions require an expression.

A bare "Aga Copper Off" parses as a command in AMOS, but Copper Off is
declared as an integer function in AP20. That caused the R18 test's initial
Syntax Error even though the branch wasn't executed.

Scan active/passed tests and public examples; historical diagnostics are excluded.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BARE_COPPER_FUNC = re.compile(
    r"^\s*Aga\s+(?:Copper\s+(?:Clear|Wait|Move|End|On|Off)|Mouse\s+(?:X|Y|Buttons|Pressed|Released)|Hotspot\s+Hit|Rect\s+Overlap|Text)\b",
    re.IGNORECASE,
)


def main():
    files = sorted(
        [path for folder in ("current", "passed")
         for path in (ROOT / "tests" / folder).glob("*.asc")]
        + list((ROOT / "examples").glob("*.asc"))
    )
    assert files, "No AMOS test files were found"
    violations = []
    for path in files:
        for number, line in enumerate(
            path.read_bytes().decode("latin-1").splitlines(), 1
        ):
            # A single quote begins an AMOS comment outside literal strings.
            # Only line-start command detection is needed for this guard.
            if BARE_COPPER_FUNC.match(line):
                violations.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    if violations:
        raise SystemExit("Bare Copper/Mouse/Hotspot/Rect/Text AP20 function call (use X=Aga ...):\n" +
                         "\n".join(violations))
    print(f"PASS: AMOS Copper/Mouse/Hotspot/Rect/Text functions used as expressions ({len(files)} test/example files)")


if __name__ == "__main__":
    main()
