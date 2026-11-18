#!/usr/bin/env python3
"""Source/geometry preflight for B7-m1 A/B/C Runtime benchmark.

Does not qualify WinUAE timing, pixel masks, Safe/Disp or Compiler.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys

NAME = "M19_P0J_B7_ANIM_RUNTIME_03.asc"  # only active ASC; canonical path retained
SIZE = 7555
SHA = "0f18cb608f75cda0390f86d25169bd4312561efd4d2051435a6803ceff42f689"
B7M1 = "838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"


def clipped(x: int, y: int, w: int, h: int) -> set[tuple[int, int]]:
    return {(xx, yy) for yy in range(max(0, y), min(256, y + h))
            for xx in range(max(0, x), min(320, x + w))}


def geometry_test() -> int:
    """Two-page occupied-footprint oracle, including out-of-screen sprites.

    A solid footprint conservatively over-approximates the red mask. All four
    rectangles are repainted after clearing, so overlaps cannot lose pixels.
    """
    checks = 0
    for repetition in range(2):
        pages = [set(), set()]
        previous = [{}, {}]
        page = 0
        for frame in range(1, 121):
            phase = frame if frame <= 60 else 120 - frame
            positions = ((-10 + phase * 5, 72, 17, 15),
                         (315 - phase * 5, 110, 37, 8),
                         (-5 + phase * 2, 170 - phase, 17, 15),
                         (315 - phase * 3, 200 - phase, 37, 8))
            target = set().union(*(clipped(*p) for p in positions))
            if frame <= 2:
                pages[page].clear()  # full-screen priming of each back page
            else:
                assert previous[page], "Unprimed page"
                for rect in previous[page].values():
                    pages[page].difference_update(clipped(*rect))
            for rect in positions:
                pages[page].update(clipped(*rect))
            assert pages[page] == target, (repetition, frame, page,
                                          "old Bobs not completely erased")
            previous[page] = dict(enumerate(positions))
            page = 1 - page  # toggle only after a successful Swap
            checks += 1
    return checks


def verify(path: Path) -> None:
    data = path.read_bytes()
    assert len(data) == SIZE and sha256(data).hexdigest() == SHA, "ASC source pin changed"
    src = data.decode("ascii")
    lines = src.splitlines()
    assert lines and max(map(len, lines)) <= 200
    assert B7M1 in src and "NO COMPILER TEST" in src
    for term, count in (("Aga Screen Open(", 1), ("Aga Double Buffer", 1),
                        ("Aga Screen Close", 1), ("Aga Bob Draw", 1),
                        ("Aga Swap", 1), ("Make AGA Bob Mask 1,0", 1),
                        ("No AGA Bob Mask 1", 1), ("Amos To Front", 1),
                        ("Erase _BANK1", 1), ("Erase _BANK2", 1),
                        ("Trap Open Out 1,_LOG$", 1), ("Trap Close 1", 1),
                        ("Aga Blit Fill(_EX,_EY,_EW,_EH,1)", 1)):
        assert src.count(term) == count, (term, src.count(term))
    assert len(re.findall(r"(?m)^\s*If\b", src)) == len(
        re.findall(r"(?m)^\s*End If\b", src))
    assert len(re.findall(r"(?m)^\s*For\b", src)) == len(
        re.findall(r"(?m)^\s*Next\b", src))
    assert len(re.findall(r"(?m)^\s*Repeat\b", src)) == len(
        re.findall(r"(?m)^\s*Until\b", src)) == 2
    assert not re.search(r"\bElseIf\b|\bExit\s+For\b|\bThen\b", src, re.I)
    assert "If Length(_BANK1)<>0 or Length(_BANK2)<>0" in src
    assert "Erase All" not in "\n".join(
        x.split("'", 1)[0] for x in lines)
    assert "For _RUN=1 To 6" in src and "For _FRAME=1 To 120" in src
    assert "_CASE=_RUN" in src and "_CASE=3" in src and "_CASE=2" in src
    assert "_CASE=1" in src and "_T0=Timer" in src
    assert "_TICKS(_RUN)=Timer-_T0" in src
    assert "_FPS10(_RUN)=_FRAMES(_RUN)*500/_TICKS(_RUN)" in src
    assert "If _TICKS(_RUN)>0" in src
    assert "If _CASE=3 and _FRAME>2" in src
    assert "If _ERR=0 and _CASE<>2" in src
    assert "_PAGE=1-_PAGE" in src
    for i, size in enumerate(((17, 15), (37, 8), (17, 15), (37, 8)), 1):
        assert f"_EX=_OX{i}(_PAGE) : _EY=_OY{i}(_PAGE) : _EW={size[0]} : _EH={size[1]}" in src
        assert f"_OX{i}(_PAGE)=_X{i} : _OY{i}(_PAGE)=_Y{i}" in src
        assert f"Aga Bob {i},_X{i},_Y{i},1" in src
    main = src.split("\nEnd\n", 1)[0]
    assert main.count("Gosub _ERASE_RECT") == 6  # warmup + 4 dirty + full
    assert main.count("Gosub _DO_SWAP") == 2  # warmup + measured loop
    assert "Aga Wait Vbl" not in main.split("_T0=Timer", 1)[1].split("Next _RUN", 1)[0]
    assert "Aga Wait Vbl" in src.split("_ERASE_RECT:", 1)[1]
    assert "If _CLEAR=0 and _TRY<40" in src
    assert "If _SW=0 and _TRY<40" in src
    assert "_ERR=13" in src and "_ERR=14" in src and "_ERR=15" in src
    assert "If _ERR=0 and _FR_OK=720 and _DB=1 and _CLOSE_CALLED=1" in src
    assert src.index("\n_CLEANUP:\n") < src.index("\n   Aga Screen Close\n")
    assert src.index("\n   Aga Screen Close\n") < src.index("\n   Erase _BANK1\n")
    assert src.index("\n   Erase _BANK1\n") < src.index("\n   Erase _BANK2\n")
    for field in ("RUN_FRAMES", "RUN_TICKS", "RUN_FPS_X10", "RETRY_VBL",
                  "FRAMES_OK", "CLOSE_CALLED", "VERDICT"):
        assert f'Print #1,"{field} "' in src
    assert '_VERDICT$="PATH_OK"' in src and "GATE B PASS" not in src
    assert "_ERR=1 : Goto _CLEANUP" in src  # deliberate Compiler exclusion
    assert src.rstrip().endswith("Return") and "\nEnd\n" in src
    checks = geometry_test()
    print(f"M19 B7-m1 A/B/C BENCH ASC STATIC PASS; {checks} page geometry checks; "
          "no WinUAE/Compiler timing asserted")


if __name__ == "__main__":
    verify(Path(sys.argv[1]) if len(sys.argv) > 1
           else Path("tests/current") / NAME)
