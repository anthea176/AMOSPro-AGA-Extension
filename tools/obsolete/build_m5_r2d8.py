#!/usr/bin/env python3
"""M5 R2D8 - viewport diagnostics with AMOS-safe token names.

Temporary functions:
- Aga Viewflags
- Aga Displayid
- Aga Basezero
- Aga Baseone

Built on M5-R2R2. Existing screen/IFF/double-buffer routines are unchanged.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.10_R2D8.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

VIEWFLAGS_HEX='48e7effe7600206d01c820104a8067083628004c4cdf7ff774004e75'
DISPLAYID_HEX='48e7effe7600246d01c820124a80670e41e8002c2c6a00084eaefce826004cdf7ff774004e75'
BASEZERO_HEX='48e7effe7600206d01c820104a80670e2068003020084a806706362800304cdf7ff774004e75'
BASEONE_HEX='48e7effe7600206d01c820104a80670e2068003020084a806706362800324cdf7ff774004e75'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0\xff'

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    viewflags=bytes.fromhex(VIEWFLAGS_HEX)
    displayid=bytes.fromhex(DISPLAYID_HEX)
    basezero=bytes.fromhex(BASEZERO_HEX)
    baseone=bytes.fromhex(BASEONE_HEX)

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga viewflags',14)
    tok+=token_function('aga displayid',15)
    tok+=token_function('aga basezero',16)
    tok+=token_function('aga baseone',17)
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=(base.code+b'GetP'+viewflags+b'GetP'+displayid+
          b'GetP'+basezero+b'GetP'+baseone)
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    jumps[13]+=2
    jumps[14]=len(viewflags)//2+2
    jumps[15]=len(displayid)//2+2
    jumps[16]=len(basezero)//2+2
    jumps[17]=len(baseone)//2
    jumps.append(0)

    title=b'AMOSPro AGA M5 R2D8 viewport diagnostics 0.2.10\0$VER: AMOSPro_AGA 0.2.10\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]
    assert len(out)==3948
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
