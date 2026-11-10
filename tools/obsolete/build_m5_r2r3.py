#!/usr/bin/env python3
"""M5 R2R3 - direct AGA palette/playfield configuration trial.

Validated facts before this candidate:
- ByteRun1/body decode exact for all 8 planes
- full 256-entry ColorMap exact
- PAL LORES mode ID exact
- no HAM/EHB/dual-playfield flag

R2R3 keeps the validated loader and changes only the AGA display palette setup:
- PF1 color base = 0
- PF2 color base = 0
- FULLPALETTE enabled
- MakeScreen + RethinkDisplay before SetRGB32

No new AMOS token is added.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r2 import ROUTINE_HEX

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.13_R2R3.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615'
OUT_SHA='45bed9873c05e83df641a047e39a3b712a0cf6e631b02ac3696f86c2de78ac9b'
REPLACEMENT_HEX='7c0145eb00302a3c0000030049eb03442e3c0000dc4048e7effe206d01c8264020532068003043fa00202c6b00084eaefd3c20532c6b00044eaefe864eaefe7a4cdf7ff7600000228000002a000000008000002b00000000800000380000000100000000000000004e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e714e71'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    rt=ROUTINE_HEX.lower()
    start_pat='41eb000c224bd3c47c007a007e0024462846'
    post_pat='4a8667'
    start=rt.index(start_pat)
    post=rt.index(post_pat,start)
    assert (post-start)//2==182
    assert len(bytes.fromhex(REPLACEMENT_HEX))==182

    patched=rt[:start]+REPLACEMENT_HEX+rt[post:]
    assert len(patched)==len(rt)

    # Validated ByteRun1 fix from R2R2.
    hits=[i for i in range(0,len(patched)-3,2) if patched[i:i+4]=='4440']
    assert hits==[1848], hits
    patched=patched[:hits[0]]+'4480'+patched[hits[0]+4:]

    routine=bytes.fromhex(patched)
    assert len(routine)==1108

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga iff load',13,'2')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    jumps[12]+=2
    jumps[13]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,554,0]

    title=b'AMOSPro AGA M5 R2R3 direct AGA palette 0.2.13\0$VER: AMOSPro_AGA 0.2.13\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3704
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
