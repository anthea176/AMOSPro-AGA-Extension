#!/usr/bin/env python3
"""AMOSPro AGA M4a v0.0.5: add Aga Wait Vbl to validated M3b R1.

The binary keeps the validated M3b R1 library byte-for-byte and appends one
new AP20 entry. Aga Wait Vbl uses the graphics.library base already stored
in the extension state and calls WaitTOF() only while an AGA screen is open.

This remains a deterministic HUNK build, not a native Genam assembly.
"""
from pathlib import Path
import hashlib
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "archive" / "AMOSPro_AGA_M3b_v0.0.4_R1_WinUAE_OK.Lib"
DEST = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4a_v0.0.5.Lib"

BASE_SHA = "206da625c7bd96eda6a4f024026ca3ae1f2d73ea52500c2aef580db34ef6e1a9"
M4A_SHA = "ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e"

# movem.l <same preserved registers as Pattern/Close>,-(sp)
# movea.l $01c8(a5),a2       ; slot-14 extension state
# tst.l (a2)                 ; screen pointer
# beq.s .done
# movea.l 8(a2),a6           ; stored graphics.library base
# jsr -270(a6)               ; graphics.library/WaitTOF
# .done: restore registers / rts
WAIT_HEX = "48e7ffee246d01c84a9267082c6a00084eaefef24cdf77ff4e75"

def w(n):
    return struct.pack(">H", n & 0xffff)

def l(n):
    return struct.pack(">I", n & 0xffffffff)

def token(name, statement, index, params=""):
    name = name.encode("ascii")
    token_name = name[:-1] + bytes((name[-1] | 128,))
    return (((w(index) + w(1)) if statement else (w(1) + w(index)))
            + token_name
            + (b"I" if statement else b"0")
            + params.encode("ascii") + b"\xff")

def build():
    old = BASE.read_bytes()
    assert len(old) == 1564
    assert hashlib.sha256(old).hexdigest() == BASE_SHA
    assert old[:4] == l(0x3f3) and old[-4:] == l(0x3f2)

    data = old[32:-4]
    off, toklen, liblen, titlelen = struct.unpack_from(">4I", data)
    assert (off, toklen, liblen, titlelen) == (22, 132, 1290, 60)
    assert data[16:22] == b"\0\0AP20"

    jumps = list(struct.unpack_from(">11H", data, 22))
    assert jumps == [94, 2, 8, 8, 48, 167, 193, 75, 50, 0, 0]

    tok = data[44:44 + toklen]
    lib = data[44 + toklen:44 + toklen + liblen]
    assert tok[-6:] == b"\0" * 6

    wait = bytes.fromhex(WAIT_HEX)
    assert len(wait) == 26

    # The four-byte GetP dispatcher belongs to the previous jump span.
    newlib = lib + b"GetP" + wait
    jumps[8] += 2
    jumps[9] = len(wait) // 2
    assert jumps == [94, 2, 8, 8, 48, 167, 193, 75, 52, 13, 0]
    assert sum(jumps) * 2 == len(newlib) == 1320

    newtok = tok[:-6] + token("aga wait vbl", True, 9) + b"\0" * 6
    if len(newtok) & 1:
        newtok += b"\0"

    title = b"AMOSPro AGA M4a experimental 0.0.5\0$VER: AMOSPro_AGA 0.0.5\0"
    if len(title) & 1:
        title += b"\0"

    header = l(22) + l(len(newtok)) + l(len(newlib)) + l(len(title)) + b"\0\0AP20"
    payload = bytearray(header + b"".join(w(v) for v in jumps)
                        + newtok + newlib + title + b"\0\0")
    while len(payload) & 3:
        payload += b"\0"

    n = len(payload) // 4
    result = old[:20] + l(n) + old[24:28] + l(n) + payload + old[-4:]
    assert len(result) == 1612
    assert hashlib.sha256(result).hexdigest() == M4A_SHA
    return result

if __name__ == "__main__":
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(build())
    print("Generated", DEST)
    print("SHA256", M4A_SHA)
    print("Runtime validation required: WinUAE interpreted, then compiled.")
