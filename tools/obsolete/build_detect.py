#!/usr/bin/env python3
"""Deterministic M1 AGA HUNK generator based on validated M0/Request ABI.
The original AMOS 365 +Request.s is public domain. Not a Genam build.
"""
import hashlib
import struct
from pathlib import Path
from build_probe import build as build_m0

# Machine code for Aga Detect, returning d3 0/1, d2=0.
# ExecBase.AttnFlags UWORD $128 (low byte $129), GfxBase.ChipRevBits0 $EC (bits Alice/Lisa).
CODE_HEX = """
2f00 2f01 2f08 2f09 2f0e 7600 2c780004 082e00010129 6724
43fa0030 7027 4eaefdd8 4a80 6716 2240 122900ec 0201000c
0c01000c 6602 7601 4eaefe62 2c5f 225f 205f 221f 201f
7400 4e75 67726170686963732e6c6962726172790000
"""
SHA256 = "69ace1d90a39a19cf47105fce8ef14fa44f7c6cca98d0a068f0d9f80abb21cfc"

def token(name, statement, number):
    name = name.encode("ascii")
    encoded = name[:-1] + bytes((name[-1] | 0x80,))
    if statement:
        return struct.pack(">HH", number, 1) + encoded + b"I\xff"
    return struct.pack(">HH", 1, number) + encoded + b"0\xff"

def build():
    src = build_m0()
    assert hashlib.sha256(src).hexdigest() == "5cbb8937b377d39314fafae98eb1030b0ada4bd1b05b828eb0e87ee6cffc28c5"
    body = src[32:-4]
    assert struct.unpack_from(">4I", body) == (14, 28, 90, 38)
    code = bytes.fromhex(CODE_HEX)
    assert len(code) == 92
    assert code[24:28] == bytes.fromhex("43fa0030")
    assert code[56:60] == bytes.fromhex("4eaefe62")
    assert code[60:62] == bytes.fromhex("2c5f")
    assert code[-18:] == b"graphics.library\x00\x00"
    toks = (b"\x00\x01\x00\x00\x80\xff"
            + token("aga probe", True, 3)
            + token("aga detect", False, 4)
            + b"\x00"*6)
    if len(toks) & 1: toks += b"\x00"
    lib = body[36+28:36+28+74] + b"GetP" + code
    assert lib[58:64] == b"GetP\x4e\x75" and len(lib) == 170
    prefix = bytearray(body[:36])
    struct.pack_into(">7H", prefix, 22, 21, 2, 8, 8, len(code)//2, 0, 0)
    title = b"AMOSPro AGA detect V 0.0.2\x00$VER: AMOSPro_AGA 0.0.2\x00"
    if len(title) & 1: title += b"\x00"
    payload = bytearray(prefix + toks + lib + title + b"\x00\x00")
    struct.pack_into(">4I", payload, 0, 14, len(toks), len(lib), len(title))
    while len(payload) & 3: payload += b"\x00"
    n = len(payload)//4
    res = (src[:20] + struct.pack(">I", n) + src[24:28]
           + struct.pack(">I", n) + bytes(payload) + src[-4:])
    assert len(res) == 340
    assert res[:4] == struct.pack(">I", 0x3f3)
    assert res[-4:] == struct.pack(">I", 0x3f2)
    assert hashlib.sha256(res).hexdigest() == SHA256
    return res

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "dist" / "AMOSPro_AGA.Lib"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build())
    print("Generated", out, SHA256)
    print("Native WinUAE validation still required.")
