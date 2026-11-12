#!/usr/bin/env python3
"""M6/R13 0.7.0 candidate: single back-buffer BltBitMap copy operation.

No edits to R12 runtime entries 0..17. Entry 18 gains only the 'GetP'
delimiter required by AMOS AP20 to parse the first new parameterized
entry; new entry 19 contains the stand-alone CPU 68000 routine.

R13 has passed AMOS/WinUAE for Copy and is now a frozen archived base for R14.
Running this historic builder must never replace the newer active candidate.
"""
from pathlib import Path
import hashlib

from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect, token
from m68k_emit import Code, D, A, M, POST, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib"
DEST = ROOT / "dist/AMOSPro_AGA.Lib"
ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256 = "b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec"
LAST_GOOD_SHA256="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
VERSION = "0.7.0"
ENTRY = 19
AMOS_STATE_PTR = 0x01C8
SCREEN, GFX, WIDTH, HEIGHT, DEPTH, DBSTATE = 0, 8, 12, 16, 28, 32
LVO_BLTBITMAP, LVO_WAITBLIT = -30, -228


def emit_copy():
    """AMOS function: Aga Blit Copy(sx,sy,dx,dy,w,h) -> 1 or 0.

    In: D3=h, (A3)+=w,dy,dx,sy,sx; A5=AMOS base.
    Out: D3=result, D2=0, A3 advanced by 20 bytes, SP balanced.
    Preserves D0,D1,D4-D7/A0-A2/A4-A6 (including A5).
    Modifies D2,D3,A3,CCR. Does not use WaitPort or Exec Wait.

    All coordinates and extents are checked BEFORE calling BltBitMap,
    which performs no clipping/sanity checks. Destination/source refer
    to the same validated back BitMap. BltBitMap handles overlaps,
    pixel shifts and modulos. WaitBlit makes the result synchronous.
    """
    c = Code()
    # Same proven R9 save/restore pair; A3 deliberately NOT saved.
    c.raw("48e7efee")
    c.move(D(3), D(5))          # h
    for reg in (4, 3, 2, 1, 0):
        c.move(POST(3), D(reg)) # w,dy,dx,sy,sx

    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, SCREEN), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, DBSTATE), A(2))
    c.move(A(2), D(6))
    c.tst(D(6)); c.branch(7, "bad")
    c.move(M(4, GFX), A(6))
    c.move(A(6), D(6))
    c.tst(D(6)); c.branch(7, "bad")

    # Reject negative coordinates and nonpositive rectangle dimensions.
    for reg in (0, 1, 2, 3):
        c.tst(D(reg)); c.branch(11, "bad")  # BMI
    for reg in (4, 5):
        c.tst(D(reg)); c.branch(15, "bad")  # BLE

    # Signed 16-bit geometry is an AmigaOS BltBitMap requirement.
    for off in (WIDTH, HEIGHT):
        c.move(M(4, off), D(6))
        c.tst(D(6)); c.branch(15, "bad")
        c.imm("cmp", 32767, D(6)); c.branch(14, "bad")

    # Subtract before comparing: avoids overflow of (coordinate+extent).
    c.move(M(4, WIDTH), D(6))
    c.alu("sub", D(4), 6)
    c.tst(D(6)); c.branch(11, "bad")
    for reg in (0, 2):
        c.alu("cmp", D(6), reg); c.branch(14, "bad")
    c.move(M(4, HEIGHT), D(6))
    c.alu("sub", D(5), 6)
    c.tst(D(6)); c.branch(11, "bad")
    for reg in (1, 3):
        c.alu("cmp", D(6), reg); c.branch(14, "bad")

    # DBState: front index +8, original ScreenBuffer +0, alt +4.
    c.tst(M(2, 8))
    c.branch(7, "front_zero")
    c.move(M(2, 0), A(0))
    c.branch(0, "have_sb")
    c.label("front_zero")
    c.move(M(2, 4), A(0))
    c.label("have_sb")
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")
    c.move(M(0, 0), A(0))      # ScreenBuffer.sb_BitMap
    c.move(A(0), D(6)); c.tst(D(6)); c.branch(7, "bad")

    # Guard the real BitMap geometry before any DMA. 68000 only.
    c.move(I(0), D(6))
    c.move(M(0, 0), D(6), "w") # BytesPerRow
    c.shift(6, 3, left=True)   # >= logical width in bits
    c.alu("cmp", M(4, WIDTH), 6)
    c.branch(13, "bad")       # BLT
    c.move(I(0), D(6))
    c.move(M(0, 2), D(6), "w") # Rows
    c.alu("cmp", M(4, HEIGHT), 6)
    c.branch(13, "bad")
    c.move(I(0), D(6))
    c.move(M(0, 5), D(6), "b") # Depth
    c.alu("cmp", M(4, DEPTH), 6)
    c.branch(6, "bad")
    c.tst(D(6)); c.branch(15, "bad")
    c.imm("cmp", 8, D(6)); c.branch(14, "bad")

    c.move(A(0), A(1))        # source and dest BitMap are identical
    c.move(I(0), A(2))        # TempA: graphics.library owns overlap scratch
    c.move(I(0xC0), D(6))     # copy minterm
    c.move(I(0xFF), D(7))     # all available bitplanes
    c.call_os(LVO_BLTBITMAP)
    c.tst(D(0)); c.branch(7, "bad")
    c.call_os(LVO_WAITBLIT)
    c.move(I(1), D(3))
    c.branch(0, "finish")
    c.label("bad")
    c.move(I(0), D(3))
    c.label("finish")
    c.raw("4cdf77f7")        # exact counterpart to 48e7efee; not A3
    c.raw("7400")            # AMOS integer result: D2=0
    c.raw("4e75")
    result = c.out()
    assert len(result) % 2 == 0
    return result, c.labels


def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256, "R12 changed or not selected"
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tokens, old, _ = split(raw)
    assert len(old) == 19 and tokens.endswith(bytes(6))
    assert old[18][-2:] == bytes.fromhex("4e75")
    code, labels = emit_copy()
    new = list(old)
    new[18] += b"GetP"        # required boundary for the next GetP entry
    new.append(code)
    assert new[:18] == old[:18]
    assert new[18] == old[18] + b"GetP"
    command = token("aga blit copy", 1, ENTRY, "00,0,0,0,0,0")
    new_tokens = tokens[:-6] + command + bytes(6)
    title = (b"AMOSPro AGA M6 Blit Copy R13 0.7.0\0"
             b"$VER: AMOSPro_AGA 0.7.0\0")
    if len(title) & 1:
        title += b"\0"
    # ap20_utils.rebuild keeps the original token table; rebuild explicitly
    # with a token-table replacement while preserving the original HUNK header.
    from struct import pack
    segment_code = b"".join(new)
    payload = (pack(">4I", len(new) * 2, len(new_tokens),
                    len(segment_code), len(title))
               + b"\0\0AP20" + b"".join(pack(">H", len(x)//2) for x in new)
               + new_tokens + segment_code + title + b"\0\0")
    payload += bytes(-len(payload) % 4)
    words = len(payload)//4
    result = (raw[:20] + pack(">I", words) + raw[24:28]
              + pack(">I", words) + payload + raw[-4:])
    parsed = parse(result)
    audit = inspect(parsed)
    assert audit["issues"] == [], audit["issues"]
    actual_tokens, actual_parts, _ = split(result)
    assert actual_tokens == new_tokens and actual_parts == new
    rows = [x for x in audit["tokens"] if x["name"] == "aga blit copy"]
    assert len(rows) == 1
    assert (rows[0]["function"], rows[0]["signature"]) == (ENTRY, "00,0,0,0,0,0")
    assert any(x["index"] == ENTRY and x["getp"]
               for x in audit["parameter_checks"])
    assert build_sha(raw) == BASE_SHA256
    return result, {"version": VERSION, "sha256": digest(result),
                    "size": len(result), "entry": ENTRY,
                    "changed_existing_segments": [18],
                    "unchanged_existing_segments": list(range(18)),
                    "labels": labels, "new_command": "Aga Blit Copy",
                    "runtime_validation": "NOT_TESTED"}


def build_sha(raw):
    return hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    assert len({BASE.resolve(), DEST.resolve(), ARCHIVE.resolve(), LAST_GOOD.resolve()}) == 4
    binary, info = build()
    assert build()[0] == binary
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(binary)
    assert ARCHIVE.read_bytes() == binary
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print("M6 R13 historical archive only; current candidate is not modified:", info)
