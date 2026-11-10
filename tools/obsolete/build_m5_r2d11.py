#!/usr/bin/env python3
"""M5 R2D11 - map displayed RasInfo bitplanes to front ScreenBuffer planes.

No new AMOS token is introduced. The already parser-safe:
    Aga Plane Hash(N)
is temporarily repurposed.

After Aga Swap:
- input N = displayed plane number 0..7
- return = matching front ScreenBuffer plane index 0..7
- return -1 if no pointer matches

Built on stable M5-R2R2. No viewport mutation.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.14_R2D11.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

ROUTINE_HEX='48e7effe280376ff4a846b0000a40c84000000076e00009a246d01c8200a4a806700008e205220084a8067000084266a0020200b4a8067000078202b00084a806700000a226b000460000004225320094a806700005c2851200c4a80670000522068005020084a80670000462068000420084a806700003a41e800082a044a856700000a588853856600fffa265049ec00087a002014220bb28067000012588c52450c4500086600ffec6000000426054cdf7ff774004e75'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==184

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga plane hash',14,'0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    jumps[13]+=2
    jumps[14]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,92,0]

    title=b'AMOSPro AGA M5 R2D11 displayed plane map 0.2.14\0$VER: AMOSPro_AGA 0.2.14\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3920
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
