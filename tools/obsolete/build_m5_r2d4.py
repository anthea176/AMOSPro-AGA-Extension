#!/usr/bin/env python3
"""M5 R2D4 - checksum all eight back-buffer planes.

Temporary function:
    Aga Plane Sum(N)

Returns the sum of 8000 bytes from back-buffer plane N, where N=0..7.
Built on M5-R2R2. Existing loader/palette/double-buffer routines are unchanged.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.6_R2D4.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

ROUTINE_HEX='48e7effe28034a846b0000520c84000000076e000048206d01c820680020202800084a806700000820506000000620680004205041e800084a846700000a588853846600fffa20507600323c1f3f70001018d68051c9fff86000000476004cdf7ff774004e75'

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
    assert len(routine)==102

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga plane sum',14,'0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,554,0]
    jumps[13]+=2
    jumps[14]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,51,0]

    title=b'AMOSPro AGA M5 R2D4 all-plane checksum 0.2.6\0$VER: AMOSPro_AGA 0.2.6\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3832
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
