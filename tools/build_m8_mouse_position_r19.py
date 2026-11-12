#!/usr/bin/env python3
"""M8 R19 0.8.3: read logical mouse coordinates from owned Intuition Window.

First independent mouse step: Aga Mouse X / Aga Mouse Y, functions with no
parameters, result pixel coordinate or -1. No IDCMP/keyboard event changes,
no allocation and no new state. Position = window-relative signed MouseX/Y
plus the Window LeftEdge/TopEdge, checked against extension logical W/H.

Build EXCLUSIVELY from the frozen R18 WinUAE PASS archive.
R18 AP20 entries 0..26 stay byte-for-byte identical; final entry 27 is
unchanged except for the mandatory trailing GetP delimiter. Do not promote
LAST_GOOD. Runtime AMOS/WinUAE, Compiler and real Amiga are NOT TESTED.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, D, A, M, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"
BASE_SHA256 = "600b8c2c38486004adef8c0e7924df877f7dd7829e1c622a89bbdc0db9f9808a"
LAST_GOOD_SHA256="0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc"

ENTRY_X, ENTRY_Y = 28, 29
AMOS_STATE_PTR = 0x1C8
STATE_SCREEN, STATE_WIDTH, STATE_HEIGHT, STATE_WINDOW = 0, 12, 16, 36
WD_LEFT, WD_TOP, WD_WIDTH, WD_HEIGHT = 4, 6, 8, 10
WD_MOUSE_Y, WD_MOUSE_X, WD_SCREEN = 12, 14, 46
GETP = b"GetP"


def mouse_routine(axis):
    """Public integer function. A5 AMOSBase, D3 result, D2=0, A3 intact."""
    assert axis in ("x", "y")
    c = Code()
    c.raw("48e7efee")  # R16/R18 ABI: preserve ordinary regs; D3 result.
    c.move(M(5, AMOS_STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(2, STATE_SCREEN), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(2, STATE_WINDOW), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    # Never consume another screen's Window; R19 does not own the pointer.
    c.move(M(1, WD_SCREEN), D(0))
    c.move(A(4), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "bad")

    max_off, mouse_off, edge_off = (
        (STATE_WIDTH, WD_MOUSE_X, WD_LEFT) if axis == "x"
        else (STATE_HEIGHT, WD_MOUSE_Y, WD_TOP)
    )
    c.move(M(2, max_off), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.branch(11, "bad")        # reject nonpositive logical dimension

    # MouseX/MouseY and Window edges are SIGNED 16-bit. Extend both.
    c.move(M(1, mouse_off), D(3), size="w")
    c.raw("48c3")             # EXT.L D3
    c.move(M(1, edge_off), D(1), size="w")
    c.raw("48c1")             # EXT.L D1
    c.alu("add", D(1), 3)      # screen-relative logical pixel
    c.tst(D(3))
    c.branch(11, "bad")
    c.alu("cmp", D(0), 3)      # D3 - dimension
    c.branch(4, "bad")        # reject >= width/height (exclusive upper bound)
    c.branch(0, "done")

    c.label("bad")
    c.move(I(-1), D(3))       # closed/unowned/out of screen sentinel
    c.label("done")
    c.raw("4cdf77f7")        # restore ordinary registers excluding D3/A3
    c.raw("74004e75")        # MOVEQ #0,D2; RTS
    return c.out(), c.labels


def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256, "R18 checkpoint changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    old_tok, old_parts, _ = split(raw)
    assert len(old_parts) == ENTRY_X and old_tok.endswith(bytes(6))
    x, xlabels = mouse_routine("x")
    y, ylabels = mouse_routine("y")
    parts = list(old_parts)
    parts[-1] += GETP
    parts += [x + GETP, y]
    tokens = (old_tok[:-6] +
              token("aga mouse x", 1, ENTRY_X, "0") +
              token("aga mouse y", 1, ENTRY_Y, "0") +
              bytes(6))
    title = b"AMOSPro AGA M8 Mouse Position R19 0.8.3\0$VER: AMOSPro_AGA 0.8.3\0"
    if len(title) % 2:
        title += b"\0"
    code = b"".join(parts)
    payload = (pack(">4I", len(parts)*2, len(tokens), len(code), len(title)) +
               b"\0\0AP20" +
               b"".join(pack(">H", len(p)//2) for p in parts) +
               tokens + code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    nwords = pack(">I", len(payload)//4)
    lib = raw[:20] + nwords + raw[24:28] + nwords + payload + raw[-4:]
    audit = inspect(parse(lib))
    assert not audit["issues"], audit["issues"]
    actual_tokens, actual_parts, _ = split(lib)
    assert actual_tokens == tokens and actual_parts == parts
    assert parts[:ENTRY_X-1] == old_parts[:ENTRY_X-1]
    assert parts[ENTRY_X-1] == old_parts[ENTRY_X-1] + GETP
    for name, idx in (("aga mouse x", ENTRY_X),
                      ("aga mouse y", ENTRY_Y)):
        found = [r for r in audit["tokens"] if r["name"] == name]
        assert len(found) == 1, name
        assert (found[0]["instruction"], found[0]["function"],
                found[0]["signature"]) == (1, idx, "0")
    return lib, dict(version="0.8.3", sha256=digest(lib), size=len(lib),
                     mouse_x_bytes=len(x), mouse_y_bytes=len(y),
                     labels=(xlabels, ylabels), runtime="NOT_TESTED")


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, ARCHIVE, DEST, LAST_GOOD)}) == 4
    lib, report = build()
    assert build()[0] == lib, "Builder not deterministic"
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(lib)
    # R19 is frozen: do not overwrite the active R20 candidate.
    assert ARCHIVE.read_bytes() == lib
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M8 R19 candidate, WinUAE NOT TESTED:", report)
