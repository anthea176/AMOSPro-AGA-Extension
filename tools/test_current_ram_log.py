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
        "mode field (RUN_MODE or PRG_STATE)":r"\b(?:RUN_MODE|PRG_STATE)\b",
        "result field":r"\bRESULT\b",
    }
    for label,pattern in required.items():
        assert re.search(pattern,source,re.I),("missing AMOS RAM log",label)
    # Older benches use CLOSE_RETURNED; P0c records three Close results.
    # P0d logs its actual _CLOSED status as the explicit "CLOSE " field.
    close_markers=("CLOSE_FIRST","CLOSE_WITH_DB","CLOSE_REOPEN")
    p0d_close = re.search(
        r'(?im)^\s*Print\s*#\s*\d+\s*,\s*"CLOSE\s*"\s*;\s*_CLOSED\b',
        source,
    )
    assert ("CLOSE_RETURNED" in source.upper() or all(
        marker in source.upper() for marker in close_markers) or p0d_close), (
        "missing AMOS RAM log","close field")
    executable=[line.strip() for line in source.splitlines()
                if line.strip() and not line.lstrip().startswith("'")]
    assert has_normal_program_end(executable), (
        "ASC must END normally; GOSUB routines after END must end in RETURN")
    end_marker=max(
        [source.upper().rfind(m) for m in ("CLOSE_RETURNED",)+close_markers]
        + ([p0d_close.start()] if p0d_close else [])
    )
    after_status=source[end_marker:]
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
    if scripts[0].name == "M19_P0J_B7_END_NO_CLOSE_BC_02.asc":
        # A successful End terminates the program: its journal can only
        # demonstrate entry into End, never post-End cleanup. Do NOT
        # fabricate RESULT/PASS/CLOSE_RETURNED for this special case.
        from test_m19_p0j_b7_end_asc_static import verify as verify_end
        verify_end(scripts[0])
        print("CURRENT RAM LOG PRE-END CONTRACT PASS:",scripts[0],
              "post-End success requires WinUAE observation")
        return
    verify(scripts[0].read_bytes().decode("latin-1"))
    print("CURRENT RAM LOG STATIC PASS:",scripts[0])

if __name__=="__main__":
    main()
