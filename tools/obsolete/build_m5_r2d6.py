#!/usr/bin/env python3
"""M5 R2D6 - hash the actual 256-entry viewport palette via GetRGB32.

Temporary function:
    Aga Palette Hash

Hash is h = h*33 + byte over the 3072 bytes returned by
graphics.library/GetRGB32(ColorMap,0,256,table).

Built on M5-R2R2; existing loader/palette/double-buffer code is unchanged.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.8_R2D6.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

ROUTINE_HEX='48e7effe7600246d01c8200a4a806700007a205220084a806700007028680030200c4a8067000064203c00000c00223c000100012c7800044eaefd544a806700004a2640204c7000223c00000100224b2c6a00084eaefc7c204b263c00001505323c0bff700010182403d683d683d683d683d683d682d68051c9ffea2f03224b2c7800044eaefd4e261f4cdf7ff774004e75'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0\xff'

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==146

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga palette hash',14)
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    jumps[13]+=2
    jumps[14]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,73,0]

    title=b'AMOSPro AGA M5 R2D6 palette hash 0.2.8\0$VER: AMOSPro_AGA 0.2.8\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]
    assert len(out)==3872
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
