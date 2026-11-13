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
    # OPT020/P1e has ONE interpreted-only active ASC, and keeps R68 archived.
    if files and files[0].name == "OPT020_P1E_R69_INTERPRETED_01.asc":
        source = files[0].read_bytes().decode("latin-1")
        needed = (
            "Aga Image Region(10,0,0,32,20,20,65,0)",
            "Aga Image Region(10,32,0,32,20,88,65,1)",
            "Aga Image Region(10,0,0,16,16,304,208,0)",
            "Aga Image Region(10,1,1,17,12,313,240,1)",
            "Aga Image Region(4,0,0,16,16,10,10,0)",
            "Aga Screen Close", 'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in needed), "P1e interpreted Gate B scenario incomplete"
        print("PASS: P1e active ASC covers opaque/masked, aligned/clip, reject, close (STATIC only)")
    # R71/R72 integrated Gate B: Clear -> Fill before first P2 Draw.
    if files and files[0].name in ("OPT020_P2_R71_INTERPRETED_01.asc", "OPT020_P2_R72_INTERPRETED_01.asc"):
        source = files[0].read_bytes().decode("latin-1")
        required = (
            "Aga Blit Clear(0,0,320,256)",
            "Aga Blit Fill(0,0,320,256,2)",
            "Aga Image Draw(_BASE,_LEN,18,20,0)",
            "Aga Image Draw(_BASE,_LEN,108,20,1)",
            "Aga Image Draw(_BASE,_LEN,197,22,1)",
            "Aga Image Draw(_BASE,_LEN,-15,196,1)",
            "Aga Image Draw(_BASE,_LEN,291,182,0)",
            "Aga Image Draw(_BASE,_LEN,256,-17,1)",
            "Aga Image Draw(_BASE,_LEN,105,241,1)",
            "Aga Image Draw(_BASE,_LEN,320,256,0)",
            "Aga Image Draw(0,_LEN,20,20,1)",
            "Aga Image Draw(_BASE,20,20,20,0)",
            "Aga Image Draw(_BASE,_LEN,20,20,2)",
            "Aga Image Draw(_BASE,_LEN,32768,20,0)",
            "_P2NOS=Aga Image Draw(_BASE,_LEN,25,25,0)",
            "Aga Image Region(10,0,0,32,20,20,65,0)",
            "Aga Image Region(10,32,0,32,20,88,65,1)",
            "_OLD=Aga Bank Image Draw(10,116,169,0)",
            "Aga Screen Close", "Erase 10",
            'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "P2 active test misses R69 or P2 cases"
        assert source.count('Print "CLOSE RETURNED"') == 1
        assert source.index("Aga Blit Clear(") < source.index("Aga Blit Fill(") < source.index("Aga Image Draw(")
        print("PASS: P2 active ASC exercises Clear -> Fill -> Draw, Region and legacy Bank Draw (STATIC only)")
    # Final M18 Compiler Gate C coverage: static only, never executes Compiler.
    if files and files[0].name == "M18_R68_COMPILER_FINAL_01.asc":
        source = files[0].read_text("ascii")
        required = (
            "Aga F Icon Bank Create(", "Aga F Icon Bank Put(",
            "Aga F Chip Bank Create(", "Aga F Chip Stage(",
            "Aga F Icon Capture(", "Aga F Blit(",
            "Aga C Block Capture(", "Aga C Block Draw(",
            "Aga C Block Restore(",
            "Aga C Block Draw(14,8,200,0)",
            "Aga C Block Draw(14,96,200,2)",
            "Aga C Block Draw(14,176,200,1)",
            "Aga C Block Restore(14,1)",
            "Erase 14", 'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "Final M18 test misses R64-R68 calls"
        assert "_CBLEN<>1064" in source, "Final CBlock 32x32x8 bank length mismatch"
        print("PASS: single R68 Compiler Gate C ASC covers R64-R68 (static only)")



if __name__ == "__main__":
    main()
