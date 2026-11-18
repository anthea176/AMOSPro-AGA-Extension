#!/usr/bin/env python3
"""Source-only safeguards for the single B7-m1 Runtime animation program.

Does not prove correct AGA pixels, wait/Safe behavior, speed or WinUAE.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys

NAME = "M19_P0J_B7_ANIM_RUNTIME_03.asc"
SIZE = 4730
SHA = "a5a263e38faa2dfba75bf94beac4915c6ddea85e8c345f9a2f7eb0316d8190dd"
B7M1 = "838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"


def verify(path: Path) -> None:
    data = path.read_bytes()
    assert len(data) == SIZE and sha256(data).hexdigest() == SHA, "Active ASC changed"
    src = data.decode("ascii")
    lines = src.splitlines()
    assert lines and max(map(len, lines)) <= 200
    assert B7M1 in src and "NO COMPILER TEST" in src
    for term, n in (("Aga Screen Open(", 1), ("Aga Double Buffer", 1),
                    ("Aga Screen Close", 1), ("Aga Bob Draw", 1),
                    ("Aga Swap", 1), ("Make AGA Bob Mask 1,0", 1),
                    ("No AGA Bob Mask 1", 1), ("Amos To Front", 1),
                    ("Erase _BANK1", 1), ("Erase _BANK2", 1),
                    ("Trap Open Out 1,_LOG$", 1), ("Trap Close 1", 1)):
        assert src.count(term) == n, (term, src.count(term))
    assert len(re.findall(r"(?m)^If\b", src)) == len(re.findall(r"(?m)^End If\b", src))
    assert len(re.findall(r"(?m)^For\b", src)) == len(re.findall(r"(?m)^Next\b", src))
    assert not re.search(r"\bElseIf\b|\bExit\s+For\b|\bThen\b", src, re.I)
    assert "If Length(_BANK1)<>0 or Length(_BANK2)<>0" in src
    assert "Erase All" not in "\n".join(x.split("'", 1)[0] for x in lines)
    assert "_FR_OK=_FR_OK+1" in src and "_TARGET=120" in src
    assert "For _FRAME=1 To 120" in src
    loop_start = src.index("\nFor _FRAME=1 To 120\n")
    loop_end = src.index("\nNext _FRAME\n", loop_start)
    loop = src[loop_start:loop_end]
    ops = ["_CLEAR=Aga Blit Fill(0,0,320,256,1)",
           "Aga Bob Bank _BANK1", "Aga Bob 1,_X1,72,1",
           "Aga Bob 3,-5,170,1", "Aga Bob Bank _BANK2",
           "Aga Bob 2,_X2,110,1", "Aga Bob 4,315,200,1",
           "_DRAW=Aga Bob Draw", "_SW=Aga Swap", "_FR_OK=_FR_OK+1"]
    offsets = [loop.index(op) for op in ops]
    assert offsets == sorted(offsets), "Frame must clear, place, draw, swap, count"
    assert "_X1=-10+_PHASE*5" in loop and "_X2=315-_PHASE*5" in loop
    assert "If _FRAME>60" in loop and "_PHASE=120-_FRAME" in loop
    assert "If _CLEAR<>1" in loop and "_ERR=13" in loop
    assert "If _DRAW<>1" in loop and "_ERR=14" in loop
    assert "If _SW<>1" in loop and "_ERR=15" in loop
    assert "Aga Screen Close" not in loop and "Amos To Front" not in loop
    assert "Amos To Back" in loop and loop.index("Amos To Back") > loop.index("_SW=Aga Swap")
    assert src.index("\nNext _FRAME\n") < src.index("\n_CLEANUP:\n")
    assert src.index("\n_CLEANUP:\n") < src.index("\n   Aga Screen Close\n")
    assert src.index("\n   Aga Screen Close\n") < src.index("\n   Erase _BANK1\n")
    assert src.index("\n   Erase _BANK1\n") < src.index("\n   Erase _BANK2\n")
    assert 'Print #1,"FRAMES_OK ";_FR_OK' in src
    assert 'Print #1,"VERDICT ";_VERDICT$' in src
    assert 'Print #1,"CLOSE_CALLED ";_CLOSE_CALLED' in src
    assert '_VERDICT$="PATH_OK"' in src and "GATE B PASS" not in src
    assert "_ERR=1 : Goto _CLEANUP" in src  # compiled test intentionally excluded
    assert src.rstrip().endswith("End")
    print("M19 B7 120-FRAME ANIM ASC STATIC PASS (not WinUAE/Compiler validation)")


if __name__ == "__main__":
    verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/current") / NAME)
