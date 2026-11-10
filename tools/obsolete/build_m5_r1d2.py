#!/usr/bin/env python3
"""M5 R1D2 - diagnostic IFF open path with correct AMOS integer return ABI.

Return codes:
10 entered / empty string
11 filename buffer allocation
12 dos.library open
13 DOS Open()
14 header buffer allocation / Read pending
15 12-byte header read OK
16 FORM OK
17 ILBM OK
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.1.2_R1D2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

ROUTINE_HEX='''48e7effe2e037c0a2446264628467a002047780038184a44670000ac7c0b20045280223c000100012c7800044eaefd544a80670000922440204741e80002224a534412d851ccfffc42117c0c43fa00ce70002c7800044eaefdd828404a80670000667c0d220a243c000003ed2c4c4eaeffe22a004a856700004e7c0e700c223c000100012c7800044eaefd544a806700003826402205240b760c2c4c4eaeffd60c800000000c660000207c0f20130c80464f524d660000147c10202b00080c80494c424d660000067c114a856700000c2c4c22054eaeffdc7a00200b4a806700000e224b2c7800044eaefd4e2646200c4a806700000e224c2c7800044eaefe622846200a4a806700000e224a2c7800044eaefd4e244626064cdf7ff774004e75646f732e6c69627261727900'''

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii'))
    n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=BASE.read_bytes()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga iff load',13,'2')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==300
    code=base.code+b'GetP'+routine

    jumps=list(base.jumps)
    jumps[12]+=2
    jumps[13]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,150,0]

    title=b'AMOSPro AGA M5 R1D2 IFF diagnostic 0.1.2\0$VER: AMOSPro_AGA 0.1.2\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==2892
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
