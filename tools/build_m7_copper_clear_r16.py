#!/usr/bin/env python3
"""M7 R16 0.8.0: first native Copper lifecycle gate, Aga Copper Clear.

This candidate ALLOCATES and initializes a harmless, CEND-terminated
UCopList for the extension-owned Intuition Screen but DOES NOT call
MakeScreen/RethinkDisplay or produce a visible raster effect.
No direct chipset register writes, no Copper On/Wait/Move yet.

Ownership: Screen.UserData (+342) mirrors Screen.ViewPort.UCopIns (+64).
The extension owns the custom screen; preexisting foreign pointers are
never overwritten. CloseScreen is the OS owner of final UCopIns cleanup.
R15 segments 0..21 are strictly byte-identical to the archived base.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import inspect, parse, token
from m68k_emit import Code, A, D, M, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e"
LAST_GOOD_SHA256="6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc"
ENTRY = 22
STATE_PTR = 0x1C8
SC_USERDATA = 342  # NDK39 intuition/screens.h, private application pointer
SC_UCOPINS = 44 + 20  # Screen.ViewPort at +44, ViewPort.UCopIns +20
UCOP_SIZE = 12  # NDK39 graphics/copper.h: Next, FirstCopList, CopList
MEMF_PUBLIC_CLEAR = 0x00010001
GFX_CINIT, GFX_CWAIT, GFX_CBUMP, GFX_FREECOPLIST = -594, -378, -366, -546
EXEC_ALLOCMEM, EXEC_FREEMEM = -198, -210


def emit_clear():
    """Aga Copper Clear -> 1/0; only one CEND-terminated UCL per screen.

    First call: alloc UCopList, CINIT capacity 2, CWAIT(10000,255), CBump,
    attach harmless list to UCopIns and record same ptr in Screen.UserData.
    Second call is idempotent if BOTH fields match; foreign pointers fail.
    Closing the Intuition Screen releases its attached UCopList per RKRM.

    All OS calls may destroy D0,D1,A0,A1; D3 result and D2=0; A3 unchanged.
    """
    c = Code()
    c.raw("48e7efee")  # R14 ABI-validated: all ordinary regs except D3/A3
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(4, 0), A(4))  # extension-owned Screen*
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")

    c.move(M(4, SC_USERDATA), D(0))
    c.tst(D(0))
    c.branch(6, "already")
    c.move(M(4, SC_UCOPINS), D(0))
    c.tst(D(0))
    c.branch(6, "bad")  # do not replace a foreign Copper list

    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))  # graphics.library base
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.raw("2c780004")  # MOVEA.L (4).W,A6 -> ExecBase
    c.move(I(UCOP_SIZE), D(0))
    c.move(I(MEMF_PUBLIC_CLEAR), D(1))
    c.call_os(EXEC_ALLOCMEM)
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(D(0), A(2))    # allocated UCopList* preserved by OS calls

    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))  # GfxBase
    c.move(A(2), A(0))
    c.move(I(2), D(0))    # one CEND + safe capacity
    c.call_os(GFX_CINIT)
    c.tst(D(0))
    c.branch(7, "cleanup")

    c.move(A(2), A(1))
    c.move(I(10000), D(0))  # the CEND macro's documented magic CWAIT
    c.move(I(255), D(1))
    c.call_os(GFX_CWAIT)
    c.move(A(2), A(1))
    c.call_os(GFX_CBUMP)

    # No MakeScreen/RethinkDisplay: install a terminated NO-OP candidate.
    # Intuition CloseScreen owns its UCopIns cleanup when the screen dies.
    c.move(A(2), M(4, SC_USERDATA))
    c.move(A(2), M(4, SC_UCOPINS))
    c.branch(0, "success")

    c.label("already")
    c.move(M(4, SC_UCOPINS), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(7, "success")  # initialised by this extension already
    c.branch(0, "bad")      # other Screen.UserData or ownership mismatch

    c.label("cleanup")
    c.move(M(2, 4), A(0))   # FirstCopList from failed CINIT
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "free_ucl")
    c.call_os(GFX_FREECOPLIST)
    c.label("free_ucl")
    c.raw("2c780004")       # ExecBase
    c.move(A(2), A(1))
    c.move(I(UCOP_SIZE), D(0))
    c.call_os(EXEC_FREEMEM)
    c.branch(0, "bad")

    c.label("success")
    c.move(I(1), D(3))
    c.branch(0, "done")
    c.label("bad")
    c.move(I(0), D(3))
    c.label("done")
    c.raw("4cdf77f7")  # restore (no D3 / no A3)
    c.raw("74004e75")  # MOVEQ #0,D2 ; RTS
    result = c.out()
    assert len(result) % 2 == 0
    return result, c.labels


def build():
    base = BASE.read_bytes()
    assert digest(base) == BASE_SHA256, "R15 archive has changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    original_tokens, parts, _ = split(base)
    assert len(parts) == ENTRY and original_tokens.endswith(bytes(6))
    code, labels = emit_clear()
    updated = list(parts) + [code]
    new_tokens = (original_tokens[:-6] +
                  token("aga copper clear", 1, ENTRY, "0") + bytes(6))
    title = b"AMOSPro AGA M7 Copper Clear R16 0.8.0\0$VER: AMOSPro_AGA 0.8.0\0"
    if len(title) & 1:
        title += b"\0"
    merged = b"".join(updated)
    payload = (pack(">4I", len(updated) * 2, len(new_tokens),
                    len(merged), len(title)) + b"\0\0AP20"
               + b"".join(pack(">H", len(part)//2) for part in updated)
               + new_tokens + merged + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    size = pack(">I", len(payload)//4)
    result = base[:20] + size + base[24:28] + size + payload + base[-4:]
    audit = inspect(parse(result))
    assert not audit["issues"], audit["issues"]
    hits = [t for t in audit["tokens"] if t["name"] == "aga copper clear"]
    assert len(hits) == 1
    assert (hits[0]["instruction"], hits[0]["function"], hits[0]["signature"]) == (
        1, ENTRY, "0")
    tokens, segments, _ = split(result)
    assert tokens == new_tokens and segments == updated
    assert segments[:ENTRY] == parts, "M5/M6 byte identity violated"
    return result, dict(version="0.8.0", entry=ENTRY, code_size=len(code),
                        labels=labels, size=len(result), sha256=digest(result),
                        runtime="NOT_TESTED", hardware_effect="NONE")


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, ARCHIVE, DEST, LAST_GOOD)}) == 4
    result, info = build()
    assert build()[0] == result
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(result)
    assert ARCHIVE.read_bytes() == result
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M7 R16 historical archive ONLY; current candidate not overwritten:", info)
