#!/usr/bin/env python3
"""M5 R2D2 - runtime checksum of loaded back-buffer planes.

Temporary diagnostic functions:
- Aga Back P0 Sum() -> sum of 8000 bytes from back-buffer plane 0
- Aga Back P7 Sum() -> sum of 8000 bytes from back-buffer plane 7

Built on M5-R2R2. Existing loader/palette/double-buffer routines are unchanged.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.4_R2D2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

P0_HEX='48e7effe206d01c820680020202800084a8067000008205060000006206800042050206800087600323c1f3f70001018d68051c9fff84cdf7ff774004e75'
P7_HEX='48e7effe206d01c820680020202800084a8067000008205060000006206800042050206800247600323c1f3f70001018d68051c9fff84cdf7ff774004e75'

def w(n): return struct.pack('>H', n & 0xffff)
def l(n): return struct.pack('>I', n & 0xffffffff)

def token_function(name,index):
    n=bytearray(name.encode('ascii')); n[-1] |= 0x80
    return w(1)+w(index)+bytes(n)+b'0\xff'

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    p0=bytes.fromhex(P0_HEX)
    p7=bytes.fromhex(P7_HEX)
    assert len(p0)==62 and len(p7)==62

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga back p0 sum',14)
    tok+=token_function('aga back p7 sum',15)
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+p0+b'GetP'+p7
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,554,0]
    jumps[13]+=2
    jumps[14]=len(p0)//2+2
    jumps[15]=len(p7)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,33,31,0]

    title=b'AMOSPro AGA M5 R2D2 plane checksum diagnostic 0.2.4\0$VER: AMOSPro_AGA 0.2.4\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3888
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
