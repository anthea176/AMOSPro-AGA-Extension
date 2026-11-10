#!/usr/bin/env python3
"""M5 R2D1 - runtime BitMap layout diagnostic.

Temporary diagnostic functions:
- Aga Back Flags()  -> BitMap.bm_Flags
- Aga Back Stride() -> abs(Planes[1] - Planes[0])

Built on the current M5-R2R2 candidate. No existing routine is modified.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.3_R2D1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

FLAGS_HEX='48e7effe206d01c820680020202800084a806704205060042068000420507600162800044cdf7ff774004e75'
STRIDE_HEX='48e7effe206d01c820680020202800084a806704205060042068000420502628000c96a800084a836a0244834cdf7ff774004e75'

def w(n): return struct.pack('>H', n & 0xffff)
def l(n): return struct.pack('>I', n & 0xffffffff)

def token_function(name,index):
    n=bytearray(name.encode('ascii')); n[-1] |= 0x80
    return w(1)+w(index)+bytes(n)+b'0\xff'

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    flags=bytes.fromhex(FLAGS_HEX)
    stride=bytes.fromhex(STRIDE_HEX)
    assert len(flags)==44
    assert len(stride)==52

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga back flags',14)
    tok+=token_function('aga back stride',15)
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+flags+b'GetP'+stride
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,554,0]
    jumps[13]+=2
    jumps[14]=len(flags)//2+2
    jumps[15]=len(stride)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,24,26,0]

    title=b'AMOSPro AGA M5 R2D1 bitmap diagnostics 0.2.3\0$VER: AMOSPro_AGA 0.2.3\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3852
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
