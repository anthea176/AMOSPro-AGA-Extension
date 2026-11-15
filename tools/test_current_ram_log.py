#!/usr/bin/env python3
"""Static minimum RAM: logging contract for a single current AMOS test."""
from pathlib import Path
import re


def has_normal_program_end(executable):
    """Accept END as final command or as terminator before GOSUB routines.

    An AMOS source with GOSUB subroutines after END is valid: the program
    reaches END normally, while routine bodies end with RETURN.
    """
    if not executable:
        return False
    if executable[-1].lower() == "end":
        return True
    end_positions = [
        i for i, line in enumerate(executable) if line.lower() == "end"
    ]
    if not end_positions:
        return False
    tail = executable[end_positions[-1] + 1:]
    if not tail or tail[-1].lower() != "return":
        return False
    label_positions = [
        i for i, line in enumerate(tail)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*:", line)
    ]
    return bool(label_positions) and label_positions[0] == 0 and all(
        i == 0 or tail[i - 1].lower() == "return"
        for i in label_positions
    )


def verify(source):
    required={
        "run mode":r"\bPrg\s+State\b",
        "RAM filename":r"RAM:",
        "trapped open":r"\bTrap\s+Open\s+Out\b",
        "file print":r"\bPrint\s*#\s*\d+",
        "trapped close":r"\bTrap\s+Close\b",
        "I/O result":r"\bErrtrap\b",
        "mode field":r"RUN_MODE",
        "result field":r"\bRESULT\b",
        "close field":r"CLOSE_RETURNED",
    }
    for label,pattern in required.items():
        assert re.search(pattern,source,re.I),("missing AMOS RAM log",label)
    executable=[line.strip() for line in source.splitlines()
                if line.strip() and not line.lstrip().startswith("'")]
    assert has_normal_program_end(executable), (
        "ASC must END normally; GOSUB routines after END must end in RETURN")
    after_status=source[source.upper().rfind("CLOSE_RETURNED"):]
    assert not re.search(r"(?im)^\s*Do\s*\r?\n\s*(?:Aga\s+)?Wait\s+Vbl\s*\r?\n\s*Loop\s*$",after_status), (
        "terminal result holding VBL loop forbidden")

def main():
    # Regression: last line RETURN is legitimate if END protects main.
    assert has_normal_program_end(["Print 1", "End"])
    assert has_normal_program_end(["Print 1", "End", "_SORT_OBJECTS:", "Return"])
    assert has_normal_program_end([
        "Print 1", "End", "_CREATE_OBJ:", "Return",
        "_SORT_OBJECTS:", "Return"
    ])
    assert not has_normal_program_end(["Do", "Wait Vbl", "Loop"])
    assert not has_normal_program_end(["End", "_SORT_OBJECTS:", "Do", "Loop"])
    assert not has_normal_program_end(["End", "_SORT_OBJECTS:", "Return", "Print 1"])
    scripts=sorted(Path("tests/current").glob("*.asc"))
    assert len(scripts)<=1,"Only one ASC is allowed in tests/current"
    if not scripts:
        print("CURRENT RAM LOG PASS (no active ASC)")
        return
    verify(scripts[0].read_bytes().decode("latin-1"))
    print("CURRENT RAM LOG STATIC PASS:",scripts[0])

if __name__=="__main__":
    main()
