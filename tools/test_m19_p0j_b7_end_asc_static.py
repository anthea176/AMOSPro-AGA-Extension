#!/usr/bin/env python3
"""Static guard for B7's single active no-Close End regression ASC.

Does not execute AMOS, prove End completed, or prove memory cleanup.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys

NAME = "M19_P0J_B7_END_NO_CLOSE_BC_02.asc"
SHA = "35b2cfbfc7e2661bd5c7736811619547ca32127dc7e9d97794bc3403780118ae"
B7 = "f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b"


def verify(path: Path) -> None:
    data = path.read_bytes()
    assert len(data) == 3785 and sha256(data).hexdigest() == SHA, "ASC changed"
    src = data.decode("ascii")
    lines = src.splitlines()
    assert max(map(len, lines)) <= 200
    assert B7 in src and src.count("Aga Bob Draw") == 1
    assert src.count("Aga Swap") == 1
    assert src.count("Aga Screen Open(") == 1
    assert src.count("Aga Double Buffer") == 1
    assert "_PRG=Prg State" in src
    for needle in (
        "RAM:M19_B7_END_RUNTIME.TXT",
        "RAM:M19_B7_END_COMPILED.TXT",
        "RAM:M19_B7_END_INTERPRETED.TXT",
        'Print #1,"PRE_END_OK 1"',
        'Print #1,"POST_END_STATUS UNOBSERVABLE_IN_PROGRAM"',
        'Print #1,"EXPLICIT_SCREEN_CLOSE 0"',
    ):
        assert needle in src, needle
    assert src.count("Trap Open Out 1,_LOG$") == 1
    assert src.count("Trap Close 1") == 1
    assert src.count("Aga Screen Close") == 1
    assert src.count("Amos To Front") == 1
    assert src.count("Erase _BANK1") == 1 and src.count("Erase _BANK2") == 1
    assert src.count("Aga Bob Bank _BANK1") == 2
    assert src.count("Aga Bob Bank _BANK2") == 2
    assert src.count("Aga Bob 1,") == 1 and src.count("Aga Bob 2,") == 1
    assert src.count("Aga Bob 3,") == 1 and src.count("Aga Bob 4,") == 1
    assert src.count("Make AGA Bob Mask 1,0") == 1
    assert src.count("No AGA Bob Mask 1") == 1
    assert src.count("_LOGERR=Errtrap") == 1
    assert src.count("_CLOSEERR=Errtrap") == 1
    assert "_ERR=15 : Goto _FAIL" in src and "_ERR=16 : Goto _FAIL" in src
    assert len(re.findall(r"(?m)^If\b", src)) == len(re.findall(r"(?m)^End If\b", src))
    assert len(re.findall(r"(?m)^For\b", src)) == len(re.findall(r"(?m)^Next\b", src))
    assert not re.search(r"\bElseIf\b|\bExit\s+For\b", src, re.I)

    # An explicitly called Close would invalidate this test even if it returned 1.
    positive, sep, failure = src.partition("\n_FAIL:\n")
    assert sep, "missing dedicated error-only cleanup"
    assert positive.rstrip().endswith("\nEnd"), "success must exit by End"
    assert positive.index("Trap Open Out 1,_LOG$") < positive.index("Trap Close 1")
    assert positive.index("Trap Close 1") < positive.rindex("\nEnd")
    assert "Aga Screen Close" not in "\n".join(
        line.split("'", 1)[0] for line in positive.splitlines()
    )
    assert "Amos To Front" not in "\n".join(
        line.split("'", 1)[0] for line in positive.splitlines()
    )
    assert "Erase _BANK1" not in positive and "Erase _BANK2" not in positive
    assert "Aga Screen Close" in failure and "Amos To Front" in failure
    assert failure.rstrip().endswith("End")
    assert "RESULT 1" not in src and "VERDICT PASS" not in src
    print("M19 B7 END WITHOUT CLOSE ASC STATIC PASS: one explicit error-only Close; before-End log; true End on success")


if __name__ == "__main__":
    verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/current") / NAME)
