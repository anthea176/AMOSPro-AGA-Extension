#!/usr/bin/env python3
"""M5 R1: validate AMOS string ABI + DOS file open + FORM/ILBM header.

This is deliberately stage 1 only. No screen or pixel data is modified.
M4b LAST_GOOD remains untouched.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.1.0_R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615'
OUT_SHA='25c1cdfa735f9716588316ce39c1d5397c154e5110e45c99b289c4dd650af141'

ROUTINE_HEX='''48e7effe2e037c002446264628467a002047780038184a44670000a420045280223c000100012c7800044eaefd544a806700008c2440204741e80002224a534412d851ccfffc421143fa00c870002c7800044eaefdd828404a8067000062220a243c000003ed2c4c4eaeffe22a004a856700004c700c223c000100012c7800044eaefd544a806700003626402205240b760c2c4c4eaeffd60c800000000c6600001e20130c80464f524d66000012202b00080c80494c424d660000047c014a856700000c2c4c22054eaeffdc7a00200b4a806700000e224b2c7800044eaefd4e2646200c4a806700000e224c2c7800044eaefe622846200a4a806700000e224a2c7800044eaefd4e244626064cdf7ff74e75646f732e6c69627261727900'''

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii'))
    n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga iff load',13,'2')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==286
    code=base.code+b'GetP'+routine

    jumps=list(base.jumps)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,77,0]
    jumps[12]+=2
    jumps[13]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,143,0]

    title=b'AMOSPro AGA M5 R1 IFF header 0.1.0\0$VER: AMOSPro_AGA 0.1.0\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==2872
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
