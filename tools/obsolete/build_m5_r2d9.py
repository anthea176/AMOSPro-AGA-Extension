#!/usr/bin/env python3
"""M5 R2D9 - single AMOS-safe viewport probe.

Temporary function:
    Aga Probe(N)

Selectors:
0 = ViewPort.Modes
1 = GetVPModeID()
2 = ColorMap.cm_Bp_0_base
3 = ColorMap.cm_Bp_1_base

Built on M5-R2R2. Existing screen/IFF/double-buffer routines are unchanged.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.11_R2D9.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

ROUTINE_HEX='48e7effe280376000c84000000006700002e0c84000000016700003c0c8400000002670000440c8400000003670000526000006c206d01c820104a8067000062204076003628004c60000054246d01c820124a8067000048204041e8002c2c6a00084eaefce8260060000034206d01c820104a806700002a20402068003020084a806700001e76003628003060000016206d01c820104a806700000c20402068003020084a80670000027600362800324cdf7ff774004e75'

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
    tok+=token_function('aga probe',14,'0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    jumps[13]+=2
    jumps[14]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,556,92,0]

    title=b'AMOSPro AGA M5 R2D9 viewport probe 0.2.11\0$VER: AMOSPro_AGA 0.2.11\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3908
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
