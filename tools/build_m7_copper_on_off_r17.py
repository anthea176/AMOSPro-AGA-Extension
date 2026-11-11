#!/usr/bin/env python3
"""M7 R17 0.8.1: activate/deactivate the R16 no-op UCopList via Intuition.

Two new no-argument AMOS functions:
  Aga Copper On: MakeScreen + RethinkDisplay; keep list on error.
  Aga Copper Off: detach UCopIns; rebuild and rethink; then free own
    FirstCopList and UCopList. On failure, restore UCopIns and retain memory.

The R16 Copper Clear segment is preserved byte-for-byte except for the
mandatory AP20 trailing GetP separator. No raster instructions yet.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, D, A, M, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1"
LAST_GOOD_SHA256 = "64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe"

ENTRY_ON = 23
ENTRY_OFF = 24
STATE_PTR = 0x1C8
SC_USERDATA = 342
SC_UCOPINS = 64
UCOP_SIZE = 12
INTUI_MAKESCREEN = -378
INTUI_RETHINK = -390
GFX_WAITTOF = -270
GFX_FREECOPLIST = -546
EXEC_FREEMEM = -210
DELIMITER = b"GetP"


def common_screen(c):
    """A4 = extension's private Screen*, A5 = AMOSBase."""
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(4, 0), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")


def own_list(c, allow_empty):
    """A2 = UCopList and require Screen.UserData == ViewPort.UCopIns."""
    c.move(M(4, SC_USERDATA), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    if allow_empty:
        c.branch(7, "empty")
    else:
        c.branch(7, "bad")
    c.move(M(4, SC_UCOPINS), D(0))
    c.move(A(2), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "bad")


def load_intui(c):
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 4), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "bad")


def finish(c):
    c.label("success")
    c.move(I(1), D(3))
    c.branch(0, "done")
    c.label("bad")
    c.move(I(0), D(3))
    c.label("done")
    c.raw("4cdf77f7")  # restore saved registers except D3/A3
    c.raw("74004e75")  # MOVEQ #0,D2; RTS


def emit_on():
    c = Code()
    c.raw("48e7efee")
    common_screen(c)
    own_list(c, allow_empty=False)
    load_intui(c)
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
    c.raw("48e7efee")
    common_screen(c)
    own_list(c, allow_empty=True)
    load_intui(c)
    # Ensure the GraphicsBase is present BEFORE we detach anything.
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), D(0))
    c.tst(D(0))
    c.branch(7, "bad")

    # Deactivate first. The UCopList itself is not modified while active.
    c.move(I(0), M(4, SC_UCOPINS))
    c.move(A(4), A(0))
    c.call_os(INTUI_MAKESCREEN)
    c.tst(D(0))
    c.branch(6, "restore")
    c.call_os(INTUI_RETHINK)
    c.tst(D(0))
    c.branch(6, "rollback")

    # New display no longer references our UCopList. Synchronize one TOF
    # before disposing of its intermediate graphics.library structures.
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))
    c.call_os(GFX_WAITTOF)
    c.move(M(2, 4), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "release")
    c.call_os(GFX_FREECOPLIST)

    c.label("release")
    c.move(I(0), M(4, SC_USERDATA))
    c.raw("2c780004")  # MOVEA.L (4).W,A6 -> ExecBase
    c.move(A(2), A(1))
    c.move(I(UCOP_SIZE), D(0))
    c.call_os(EXEC_FREEMEM)
    c.branch(0, "success")

    # A zero UCopIns with zero UserData already is clean: idempotent.
    c.label("empty")
    c.move(M(4, SC_UCOPINS), D(0))
    c.tst(D(0))
    c.branch(7, "success")
    c.branch(0, "bad")

    # Rebuild failed, keep all ownership and do not free the list.
    c.label("restore")
    c.move(A(2), M(4, SC_UCOPINS))
    c.branch(0, "bad")

    # Rethink failed: restore the owned list, try rebuilding original view.
    # Regardless of rollback result retain all allocations for retry.
    c.label("rollback")
    c.move(A(2), M(4, SC_UCOPINS))
    c.move(A(4), A(0))
    c.call_os(INTUI_MAKESCREEN)
    c.call_os(INTUI_RETHINK)
    c.branch(0, "bad")

    finish(c)
    return c.out(), c.labels


def build():
    base = BASE.read_bytes()
    assert digest(base) == BASE_SHA256, "R16 archive missing or changed"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    orig_tokens, orig_parts, _ = split(base)
    assert len(orig_parts) == ENTRY_ON and orig_tokens.endswith(bytes(6))
    on, labels_on = emit_on()
    off, labels_off = emit_off()
    parts = list(orig_parts)
    parts[-1] += DELIMITER
    parts.append(on + DELIMITER)
    parts.append(off)
    tokens = (orig_tokens[:-6] +
              token("aga copper on", 1, ENTRY_ON, "0") +
              token("aga copper off", 1, ENTRY_OFF, "0") +
              bytes(6))
    title = (b"AMOSPro AGA M7 Copper On/Off R17 0.8.1\0"
             b"$VER: AMOSPro_AGA 0.8.1\0")
    if len(title) % 2:
        title += b"\0"
    code = b"".join(parts)
    data = (pack(">4I", len(parts)*2, len(tokens), len(code), len(title))
            + b"\0\0AP20"
            + b"".join(pack(">H", len(p)//2) for p in parts)
            + tokens + code + title + b"\0\0")
    data += bytes(-len(data) % 4)
    hunk_size = pack(">I", len(data)//4)
    binary = base[:20] + hunk_size + base[24:28] + hunk_size + data + base[-4:]
    assert not inspect(parse(binary))["issues"]
    t2, p2, _ = split(binary)
    assert t2 == tokens and p2 == parts
    assert p2[:ENTRY_ON-1] == orig_parts[:ENTRY_ON-1]
    assert p2[ENTRY_ON-1] == orig_parts[ENTRY_ON-1] + DELIMITER
    audit = inspect(parse(binary))
    for name, index in (("aga copper on", ENTRY_ON),
                        ("aga copper off", ENTRY_OFF)):
        hits = [r for r in audit["tokens"] if r["name"] == name]
        assert len(hits) == 1
        assert (hits[0]["instruction"], hits[0]["function"],
                hits[0]["signature"]) == (1, index, "0")
    return binary, dict(version="0.8.1", size=len(binary),
                        sha256=digest(binary), on_bytes=len(on),
                        off_bytes=len(off), on_labels=labels_on,
                        off_labels=labels_off, runtime="NOT_TESTED")


if __name__ == "__main__":
    assert len({p.resolve() for p in (BASE, DEST, ARCHIVE, LAST_GOOD)}) == 4
    binary, info = build()
    assert build()[0] == binary
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(binary)
    assert ARCHIVE.read_bytes() == binary
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M7 R17 archived checkpoint; never overwrite active R18:", info)
