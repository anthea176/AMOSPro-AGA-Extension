#!/usr/bin/env python3
"""Guard new AMOS tests against block syntax and obvious string type errors.

R24 initially failed under AMOS because single-line THEN was used in a
block. Check only tests/current/*.asc, not legacy archived examples.
This is a STATIC guard; it is not an AMOS Professional parser/runtime test.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "tests" / "current"


def strip_comment(line):
    quote = False
    for i, char in enumerate(line):
        if char == '"':
            quote = not quote
        elif char == "'" and not quote:
            return line[:i]
    return line


def scan(path):
    if_blocks, for_blocks = [], []
    errors = []
    for index, raw in enumerate(path.read_bytes().decode("latin-1").splitlines(), 1):
        line = strip_comment(raw).strip()
        if not line:
            continue
        # AMOS Peek$ returns a string and requires a $-typed destination.
        peek_assignment = re.match(r"(?i)^([A-Za-z_][A-Za-z0-9_]*\$?)\s*=\s*Peek\$\s*\(", line)
        if peek_assignment and not peek_assignment.group(1).endswith("$"):
            errors.append(f"{index}: Peek$ returns a string; target needs a $ suffix")
        # Direct numeric-variable vs quoted-string comparisons are invalid.
        if re.search(r'(?i)(?<![A-Za-z0-9_$])[A-Za-z_][A-Za-z0-9_]*\s*(?:<>|=)\s*"', line):
            errors.append(f"{index}: string literal compared with non-$ numeric variable")
        if re.match(r"(?i)^If\s+", line):
            if re.search(r"(?i)\bThen\b", line):
                errors.append(f"{index}: single-line THEN is not allowed in current block tests")
            if_blocks.append(index)
        elif re.fullmatch(r"(?i)Else", line):
            if not if_blocks:
                errors.append(f"{index}: ELSE without IF")
        elif re.fullmatch(r"(?i)End\s+If", line):
            if if_blocks:
                if_blocks.pop()
            else:
                errors.append(f"{index}: END IF without IF")
        elif re.match(r"(?i)^For\s+", line):
            for_blocks.append(index)
        elif re.match(r"(?i)^Next\b", line):
            if for_blocks:
                for_blocks.pop()
            else:
                errors.append(f"{index}: NEXT without FOR")
    errors.extend(f"{i}: IF without END IF" for i in if_blocks)
    errors.extend(f"{i}: FOR without NEXT" for i in for_blocks)
    return errors


def main():
    files = sorted(CURRENT.glob("*.asc"))
    assert len(files) <= 1, "Only one active AMOS test is permitted"
    for path in files:
        errors = scan(path)
        assert not errors, f"{path}:\n" + "\n".join(errors)
        print(f"PASS: {path.name} has matched IF/END IF and FOR/NEXT; no single-line THEN")
    if not files:
        print("PASS: no active AMOS test (zero is valid after archiving)")


if __name__ == "__main__":
    main()
