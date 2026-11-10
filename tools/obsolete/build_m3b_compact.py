#!/usr/bin/env python3
"""AMOSPro AGA M3b v0.0.4: deterministic AP20 HUNK generator.

Preserves all M3a validated routines except cold-init, which now registers
an extension data zone and RESET/END cleanup hooks. The M3b routines below
contain full relocatable 68k instruction streams (PC offsets are resolved).
This is not an assembled Genam build; WinUAE M3b validation remains pending.
"""
from pathlib import Path
import hashlib
import struct

ROOT = Path(__file__).resolve().parents[1]
M3A = ROOT / "archive" / "AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib"
DEST = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M3b_v0.0.4.Lib"
M3A_SHA = "ea2c3d970569e870952f843b96264a27bce79a2dc337115d738e4e6d3e6ee2aa"
M3B_SHA = "b602f90b8cd66c701f53d83014c0723cf74cbed73bdc5ecbd300dc9d40ed2af4"
COLD_HEX = """b2bc415065786600002a41fa00902b4801c841fa00242b4801cc2b4801d041fa007c7007429851c8fffc700d323c0200
4e7570ff91c84e7548e7ffee246d01c8200a4a80670000504a926700000e20522c6a00044eaeffbe4292226a00082009
4a806700000e2c7800044eaefe6242aa0008226a000420094a806700000e2c7800044eaefe6242aa000441ea000c7004
429851c8fffc4cdf77ff4e750000000000000000000000000000000000000000000000000000000000000000"""
OPEN_HEX = """48e7cfee28032a1b2c1b2e1b7600246d01c8200a4a806700013a4a92660001340c84000000a06500012a0c8400000500
62000120200402800000000f660001140c85000000a06500010a0c8500000200620001000c8600000002650000f60c86
00000100620000ec22065381c286660000e22007028000000c80660000d62c780004082e00010129670000c843fa00cc
70274eaefdd84a80670000b828402c78000443fa00c870274eaefdd84a80670000982a40102d00ec0200000c0c00000c
6600007822067000e28952800c81000000016600fff42540001c4fefffd8224f22fc8000002322c422fc8000002422c5
22fc8000002522c022fc8000003222c7700022c022c091c8224f2c4c4eaefd9c4fef00284a80670000222480254c0004
254d00082544000c25450010254600142547001876016000001a42aa001c224d2c7800044eaefe62224c2c7800044eae
fe624cdf77f374004e75696e74756974696f6e2e6c6962726172790067726170686963732e6c6962726172790000"""
PATTERN_HEX = """48e7ffee246d01c8200a4a806700007e4a926700007828522c6a0008282a00142a2a00107c002006c0c480c502800000
ffff2e002207c2fc00ff2004538082c002810000ffff243c000000ff9481e1894841e18a4842263c30000000200741ec
002c4eaefcac200743ec00544eaefeaa70002206242a000c5382260643ec00544eaefece5286bc856600ff9c4cdf77ff
4e75"""
CLOSE_HEX = """48e7ffee246d01c8200a4a80670000504a926700000e20522c6a00044eaeffbe4292226a000820094a806700000e2c78
00044eaefe6242aa0008226a000420094a806700000e2c7800044eaefe6242aa000441ea000c7004429851c8fffc4cdf
77ff4e75"""

def w(n): return struct.pack(">H", n & 0xffff)
def l(n): return struct.pack(">I", n & 0xffffffff)

def token(name, statement, index, params=""):
    name=name.encode("ascii")
    token_name=name[:-1]+bytes((name[-1]|128,))
    return ((w(index)+w(1)) if statement else (w(1)+w(index))) + token_name + (b"I" if statement else b"0") + params.encode("ascii") + b"\xff"

def build():
    old=M3A.read_bytes()
    assert hashlib.sha256(old).hexdigest()==M3A_SHA
    assert len(old)==688 and old[:4]==l(0x3f3) and old[-4:]==l(0x3f2)
    data=old[32:-4]
    assert struct.unpack_from(">4I",data)==(16,58,504,50)
    oldtok=data[38:96]
    oldlib=data[96:600]
    assert oldtok[-6:]==b"\0"*6

    cold=bytes.fromhex(COLD_HEX)
    op=bytes.fromhex(OPEN_HEX)
    pat=bytes.fromhex(PATTERN_HEX)
    close=bytes.fromhex(CLOSE_HEX)
    assert list(map(len,(cold,op,pat,close)))==[188,382,146,100]
    lib=cold+oldlib[42:]+b"GetP"+op+b"GetP"+pat+b"GetP"+close
    sizes=[len(cold),4,16,16,96,334,len(op)+4,len(pat)+4,len(close),0,0]
    assert len(lib)==sum(sizes)
    jumps=[v//2 for v in sizes]

    tok=(oldtok[:-6]
         +token("aga screen open",False,6,"0,0,0,0")
         +token("aga screen pattern",True,7)
         +token("aga screen close",True,8)
         +b"\0"*6)
    if len(tok)&1:tok+=b"\0"
    title=b"AMOSPro AGA M3b experimental 0.0.4\0$VER: AMOSPro_AGA 0.0.4\0"
    if len(title)&1:title+=b"\0"
    header=l(22)+l(len(tok))+l(len(lib))+l(len(title))+b"\0\0AP20"
    payload=bytearray(header+b"".join(w(v) for v in jumps)+tok+lib+title+b"\0\0")
    while len(payload)&3:payload+=b"\0"
    n=len(payload)//4
    result=old[:20]+l(n)+old[24:28]+l(n)+payload+old[-4:]
    assert len(result)==1564
    assert hashlib.sha256(result).hexdigest()==M3B_SHA
    return result

if __name__=="__main__":
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(build())
    print("Generated",DEST)
    print("SHA256",M3B_SHA)
    print("Native WinUAE test not yet performed.")
