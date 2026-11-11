#!/usr/bin/env python3
"""M7 R18 0.8.2: native Copper Wait(v,h), Move(reg,rgb4), End and raster.

From frozen R17. R16 Clear CINIT capacity changes ONLY 2 -> 64, R17
On/Off are deliberately adapted for Screen.UserData pointer flags:
bit0 = armed, bit1 = sealed. UCopList ptr remains in ViewPort.UCopIns.
All M5/M6 routines and archived R16/R17 .Lib files remain unchanged.

The user copper list is ALWAYS CEND terminated, even while being built:
each Wait/Move atomically rewinds the last CEND in the intermediate
CopList, emits one instruction and re-appends CEND. Gate inputs before
writing, refuse after End/On, and refuse to activate an unfinished list.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, A, D, M, POST, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "cfd73961d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a"
LAST_GOOD_SHA256="89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033"

ENTRY_CLEAR, ENTRY_ON, ENTRY_OFF = 22, 23, 24
ENTRY_WAIT, ENTRY_MOVE, ENTRY_END = 25, 26, 27
STATE_PTR, SC_USERDATA, SC_UCOPINS = 0x1C8, 342, 64
UCOP_SIZE = 12
COP_FIRST, COP_CURR = 4, 8
CL_COPINS, CL_COPPTR, CL_COUNT, CL_MAX = 12, 16, 28, 30
GFX_WAIT, GFX_MOVE, GFX_BUMP = -378, -372, -366
GFX_WAITTOF, GFX_FREECOPLIST = -270, -546
INTUI_MAKESCREEN, INTUI_RETHINK = -378, -390
EXEC_FREEMEM = -210
COUNT_MAX = 64
FLAG_ACTIVE, FLAG_SEALED = 1, 2
PTR_MASK = 0xFFFFFFFC
# R16's unique CINIT(capacity=2) opcode, before LVO UCopperListInit.
CINIT_2 = bytes.fromhex("203c000000024eaefdae")
CINIT_64 = bytes.fromhex("203c000000404eaefdae")


def start(c, pop_first=None):
    c.raw("48e7efee")  # all ordinary registers preserved except D3/A3
    if pop_first is not None:
        c.move(D(3), D(5))            # second argument
        c.move(POST(3), D(4))        # first argument, A3 advanced +4
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(4), A(4))              # Screen*
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")


def owned(c, require_unsealed=False, allow_empty=False):
    """A2 owned raw UCopList*; A4 Screen*. Never trust tagged UserData."""
    c.move(M(4, SC_USERDATA), D(6))
    c.move(D(6), D(0))
    c.imm("and", PTR_MASK, D(0))
    c.move(D(0), A(2))
    c.tst(D(0))
    if allow_empty:
        c.branch(7, "empty")
    else:
        c.branch(7, "bad")
    c.move(M(4, SC_UCOPINS), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "bad")
    if require_unsealed:
        c.move(D(6), D(0))
        c.imm("and", FLAG_ACTIVE | FLAG_SEALED, D(0))
        c.tst(D(0))
        c.branch(6, "bad")


def gfx_base(c):
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "bad")


def intui_base(c):
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 4), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "bad")


def cop_structure(c, count_min=1, require_space=False):
    """A1 CopList, D7 count. Validate limited, terminated 64-slot buffer."""
    c.move(M(2, COP_CURR), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(1, CL_COPINS), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(1, CL_COPPTR), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(1, CL_MAX), D(0), size="w")
    c.imm("cmp", COUNT_MAX, D(0), size="w")
    c.branch(6, "bad")
    c.move(M(1, CL_COUNT), D(7), size="w")
    c.imm("cmp", count_min - 1, D(7), size="w")
    c.branch(3, "bad")                # BLS: Count <= min - 1
    c.imm("cmp", COUNT_MAX - (1 if require_space else 0), D(7), size="w")
    if require_space:
        c.branch(4, "bad")            # BCC: Count >= 64 (no spare slot)
    else:
        c.branch(2, "bad")            # BHI: Count > 64
    # The last CopIns entry must still be CEND, never a partial list.
    c.move(M(1, CL_COPPTR), A(0))
    c.quick(6, A(0), sub=True)
    c.move(M(0), D(0), size="w")
    c.imm("cmp", 1, D(0), size="w")
    c.branch(6, "bad")
    c.move(M(0, 2), D(0), size="w")
    c.imm("cmp", 10000, D(0), size="w")
    c.branch(6, "bad")
    c.move(M(0, 4), D(0), size="w")
    c.imm("cmp", 255, D(0), size="w")
    c.branch(6, "bad")


def finish(c):
    c.label("success")
    c.move(I(1), D(3))
    c.branch(0, "done")
    c.label("bad")
    c.move(I(0), D(3))
    c.label("done")
    c.raw("4cdf77f7")
    c.raw("74004e75")               # D2=0; RTS


def emit_on():
    c = Code()
    start(c)
    owned(c)
    intui_base(c)
    # Count=1 is R16 legacy CEND-only. Any nonempty raster must be End-sealed.
    c.move(M(2, COP_CURR), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(1, CL_COUNT), D(0), size="w")
    c.imm("cmp", 1, D(0), size="w")
    c.branch(7, "arm")
    c.move(D(6), D(0))
    c.imm("and", FLAG_SEALED, D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.label("arm")
    # Conservative: mark active before OS calls. If MakeScreen/Rethink
    # fail, Off must detach; appending must remain blocked.
    c.imm("or", FLAG_ACTIVE, M(4, SC_USERDATA))
    c.move(A(4), A(0))
    c.call_os(INTUI_MAKESCREEN)
    c.tst(D(0))
    c.branch(6, "bad")
    c.call_os(INTUI_RETHINK)
    c.tst(D(0))
    c.branch(6, "bad")
    c.branch(0, "success")
    finish(c)
    return c.out(), c.labels


def emit_off():
    c = Code()
    start(c)
    owned(c, allow_empty=True)
    intui_base(c)
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(I(0), M(4, SC_UCOPINS))
    c.move(A(4), A(0))
    c.call_os(INTUI_MAKESCREEN)
    c.tst(D(0))
    c.branch(6, "restore")
    c.call_os(INTUI_RETHINK)
    c.tst(D(0))
    c.branch(6, "rollback")
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))
    c.call_os(GFX_WAITTOF)
    c.move(M(2, COP_FIRST), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "release")
    c.call_os(GFX_FREECOPLIST)
    c.label("release")
    c.move(I(0), M(4, SC_USERDATA))
    c.raw("2c780004")               # ExecBase
    c.move(A(2), A(1))
    c.move(I(UCOP_SIZE), D(0))
    c.call_os(EXEC_FREEMEM)
    c.branch(0, "success")
    c.label("empty")
    c.move(M(4, SC_UCOPINS), D(0))
    c.tst(D(0))
    c.branch(7, "success")
    c.branch(0, "bad")
    c.label("restore")
    c.move(A(2), M(4, SC_UCOPINS))
    c.branch(0, "bad")
    c.label("rollback")
    c.move(A(2), M(4, SC_UCOPINS))
    c.move(A(4), A(0))
    c.call_os(INTUI_MAKESCREEN)
    c.call_os(INTUI_RETHINK)
    c.branch(0, "bad")
    finish(c)
    return c.out(), c.labels


def emit_append(mode):
    """Append one CWait or CMove, keeping a CEND at every return."""
    assert mode in ("wait", "move")
    c = Code()
    start(c, pop_first=True)
    # D4 first, D5 last parameter. AMOS consumes A3 even on rejection.
    if mode == "wait":
        for reg, maximum in ((D(4), 255), (D(5), 222)):
            c.imm("cmp", maximum, reg)
            c.branch(2, "bad")        # unsigned > limit (also negatives)
    else:
        c.imm("cmp", 0x180, D(4))
        c.branch(5, "bad")            # BCS: register < COLOR00
        c.imm("cmp", 0x1BE, D(4))
        c.branch(2, "bad")            # BHI: register > COLOR31
        c.move(D(4), D(0))
        c.imm("and", 1, D(0))
        c.tst(D(0))
        c.branch(6, "bad")            # odd register offset
        c.imm("cmp", 0x0FFF, D(5))
        c.branch(2, "bad")

    owned(c, require_unsealed=True)
    gfx_base(c)
    cop_structure(c, require_space=True)

    if mode == "wait":
        # Scan backwards through preceding CopIns entries, ignoring CMOVEs.
        # All WAITs must be strictly increasing (v,h).
        c.move(D(7), D(6), size="w")
        c.quick(1, D(6), sub=True, size="w")
        c.branch(7, "append")        # Count 1 = CEND only
        c.move(M(1, CL_COPPTR), A(0))
        c.quick(6, A(0), sub=True)   # current CEND
        c.label("scan")
        c.quick(6, A(0), sub=True)   # prior real instruction
        c.move(M(0), D(0), size="w")
        c.imm("cmp", 1, D(0), size="w")
        c.branch(7, "compare")
        c.quick(1, D(6), sub=True, size="w")
        c.branch(6, "scan")
        c.branch(0, "append")
        c.label("compare")
        c.move(M(0, 2), D(0), size="w")
        c.move(D(4), D(1), size="w")
        c.alu("cmp", D(0), 1, size="w")
        c.branch(2, "append")        # new V higher
        c.branch(6, "bad")           # new V lower
        c.move(M(0, 4), D(0), size="w")
        c.move(D(5), D(1), size="w")
        c.alu("cmp", D(0), 1, size="w")
        c.branch(3, "bad")           # new H <= prior H

    c.label("append")
    # Rewind one intermediate instruction: remove trailing CEND.
    c.move(M(1, CL_COPPTR), A(0))
    c.quick(6, A(0), sub=True)
    c.move(A(0), M(1, CL_COPPTR))
    c.quick(1, M(1, CL_COUNT), sub=True, size="w")
    c.move(A(2), A(1))
    c.move(D(4), D(0))
    if mode == "move":
        # CMOVE takes a pointer to the register, not its $0180 offset.
        c.imm("add", 0xDFF000, D(0))
    c.move(D(5), D(1))
    c.call_os(GFX_WAIT if mode == "wait" else GFX_MOVE)
    c.move(A(2), A(1))
    c.call_os(GFX_BUMP)
    # Restore CEND before returning, so later On/CloseScreen is safe.
    c.move(A(2), A(1))
    c.move(I(10000), D(0))
    c.move(I(255), D(1))
    c.call_os(GFX_WAIT)
    c.move(A(2), A(1))
    c.call_os(GFX_BUMP)
    c.branch(0, "success")
    finish(c)
    return c.out(), c.labels


def emit_end():
    c = Code()
    start(c)
    owned(c, require_unsealed=True)
    cop_structure(c, count_min=2)  # do not seal empty list
    c.imm("or", FLAG_SEALED, M(4, SC_USERDATA))
    c.branch(0, "success")
    finish(c)
    return c.out(), c.labels


def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256, "Frozen R17 changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok, old, _ = split(raw)
    assert len(old) == ENTRY_WAIT and tok.endswith(bytes(6))
    parts = list(old)
    clear = parts[ENTRY_CLEAR]
    assert clear.count(CINIT_2) == 1
    parts[ENTRY_CLEAR] = clear.replace(CINIT_2, CINIT_64)
    on, l_on = emit_on()
    off, l_off = emit_off()
    wait, l_wait = emit_append("wait")
    move, l_move = emit_append("move")
    end, l_end = emit_end()
    parts[ENTRY_ON] = on + b"GetP"
    parts[ENTRY_OFF] = off + b"GetP"
    parts += [wait + b"GetP", move, end]
    tokens = (tok[:-6] +
              token("aga copper wait", 1, ENTRY_WAIT, "00,0") +
              token("aga copper move", 1, ENTRY_MOVE, "00,0") +
              token("aga copper end", 1, ENTRY_END, "0") +
              bytes(6))
    title = b"AMOSPro AGA M7 Copper Raster R18 0.8.2\0$VER: AMOSPro_AGA 0.8.2\0"
    if len(title) % 2:
        title += b"\0"
    code = b"".join(parts)
    data = (pack(">4I", len(parts)*2, len(tokens), len(code), len(title)) +
            b"\0\0AP20" +
            b"".join(pack(">H", len(p)//2) for p in parts) +
            tokens + code + title + b"\0\0")
    data += bytes(-len(data) % 4)
    size = pack(">I", len(data)//4)
    lib = raw[:20] + size + raw[24:28] + size + data + raw[-4:]
    audit = inspect(parse(lib))
    assert not audit["issues"], audit["issues"]
    tok2, segments, _ = split(lib)
    assert tok2 == tokens and segments == parts
    assert parts[:ENTRY_CLEAR] == old[:ENTRY_CLEAR]
    assert parts[ENTRY_CLEAR] != old[ENTRY_CLEAR]
    for name, idx, sig in (("aga copper wait", ENTRY_WAIT, "00,0"),
                           ("aga copper move", ENTRY_MOVE, "00,0"),
                           ("aga copper end", ENTRY_END, "0")):
        found = [t for t in audit["tokens"] if t["name"] == name]
        assert len(found) == 1
        assert (found[0]["instruction"], found[0]["function"],
                found[0]["signature"]) == (1, idx, sig)
    return lib, dict(version="0.8.2", size=len(lib), sha256=digest(lib),
                     on=len(on), off=len(off), wait=len(wait),
                     move=len(move), end=len(end),
                     labels=(l_on, l_off, l_wait, l_move, l_end),
                     runtime="NOT_TESTED")


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, ARCHIVE, DEST, LAST_GOOD)}) == 4
    lib, info = build()
    assert build()[0] == lib
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(lib)
    assert ARCHIVE.read_bytes() == lib
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M7 R18 archived checkpoint ONLY; active R19 untouched:", info)
