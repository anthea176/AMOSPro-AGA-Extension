#!/usr/bin/env python3
"""M8 R21 0.8.5: stop Intuition menu-bar activation on right-click.

R20 provided correct button snapshots, but WinUAE showed a lingering
Intuition menu bar when the right button was pressed. AmigaOS prescribes
WFLG_RMBTRAP ($00010000) on the application's NewWindow.Flags.

R21 changes exactly one immediate byte in AP20 entry 6 (Aga Screen Open):
  MOVE.L #$00021900,14(SP)  ->  MOVE.L #$00031900,14(SP)
The new value retains BACKDROP/BORDERLESS/ACTIVATE/NOCAREREFRESH and
adds RMBTRAP. All other machine instructions, jump sizes, AP20 tokens,
and 30 remaining segments remain byte-identical to the frozen R20 lib.

WinUAE runtime, AMOS Compiler and real Amiga are NOT TESTED for R21.
"""
from pathlib import Path
from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"

BASE_SHA256 = "9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe"
LAST_GOOD_SHA256="0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc"
R21_SHA256 = "a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644"

ENTRY_SCREEN_OPEN = 6
SCREEN_OPEN_FLAGS_OFFSET = 0x01EE
OLD_OPCODE = bytes.fromhex("2f7c00021900000e")
NEW_OPCODE = bytes.fromhex("2f7c00031900000e")
RMBTRAP_FLAG = 0x00010000
OLD_FLAGS = 0x00021900
NEW_FLAGS = OLD_FLAGS | RMBTRAP_FLAG


def build():
    original = BASE.read_bytes()
    assert digest(original) == BASE_SHA256, "R20 archive modified"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256, "LAST_GOOD mismatch (latest WinUAE-PASS R38)"
    tokens, parts, old_title = split(original)
    assert len(parts) == 31, "R20 AP20 entries changed"
    before = parts[ENTRY_SCREEN_OPEN]
    assert before.count(OLD_OPCODE) == 1, "NewWindow.Flags signature not unique"
    assert before[SCREEN_OPEN_FLAGS_OFFSET:SCREEN_OPEN_FLAGS_OFFSET+len(OLD_OPCODE)] == OLD_OPCODE
    assert NEW_FLAGS == 0x00031900 and (OLD_FLAGS & RMBTRAP_FLAG) == 0

    after = (before[:SCREEN_OPEN_FLAGS_OFFSET] + NEW_OPCODE +
             before[SCREEN_OPEN_FLAGS_OFFSET+len(OLD_OPCODE):])
    assert len(after) == len(before), "No code insertion or branch relocation"
    assert sum(a != b for a, b in zip(before, after)) == 1, "Exactly one code byte"

    updated = list(parts)
    updated[ENTRY_SCREEN_OPEN] = after
    title = b"AMOSPro AGA M8 Mouse RMBTrap R21 0.8.5\0$VER: AMOSPro_AGA 0.8.5\0"
    assert len(title) <= len(old_title)
    title = title.ljust(len(old_title), b"\0")
    candidate = rebuild(original, updated, title)
    assert len(candidate) == len(original) == 12016
    assert digest(candidate) == R21_SHA256, "R21 checkpoint mismatch"
    tk2, p2, t2 = split(candidate)
    assert tk2 == tokens and p2 == updated and t2 == title
    assert [i for i in range(len(parts)) if parts[i] != p2[i]] == [ENTRY_SCREEN_OPEN]
    assert inspect(parse(candidate))["issues"] == []
    return candidate, dict(version="0.8.5", size=len(candidate),
                           sha256=digest(candidate),
                           changed_entry=ENTRY_SCREEN_OPEN,
                           new_window_flags=hex(NEW_FLAGS),
                           runtime="NOT_TESTED")


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, ARCHIVE, DEST, LAST_GOOD)}) == 4
    lib, report = build()
    assert build()[0] == lib, "Builder nondeterministic"
    # Frozen R21 archive: do not overwrite the active R22 candidate.
    assert ARCHIVE.read_bytes() == lib
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M8 R21 frozen, WinUAE validated on its scenario:", report)
