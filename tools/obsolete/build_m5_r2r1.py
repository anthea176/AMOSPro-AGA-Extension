#!/usr/bin/env python3
"""M5 R2R1 - fixture-specific Clown.iff loader candidate.

R2's generic chunk scanner had a register bug: BMHD fields were checked
through A6 without first pointing A6 at the chunk payload. R2R1 temporarily
bypasses the scanner using the verified offsets of Clown.iff so palette,
ByteRun1 decode and planar writes can be validated independently.

M4b LAST_GOOD routines remain byte-for-byte unchanged.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.1_R2R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615'
OUT_SHA='fa45b26a814b0e6b3e60eeb40cd47b9c036bdbf29e5f35173aa4f6e1609d0f08'

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

    # Start from R2 routine then patch only its chunk-scan window.
    from build_m5_r2 import ROUTINE_HEX
    rt=ROUTINE_HEX.lower()

    start_pat='41eb000c224bd3c47c007a007e0024462846'
    post_pat='4a8667'
    start=rt.index(start_pat)
    post=rt.index(post_pat,start)

    replacement=(
        '7c01'          # D6 = BMHD present/valid
        '45eb0030'      # A2 = FORM buffer + 48 = CMAP payload
        '2a3c00000300'  # D5 = 768 bytes CMAP
        '49eb0344'      # A4 = FORM buffer + 836 = BODY payload
        '2e3c0000dc40'  # D7 = 56384 BODY bytes
    )

    replace_bytes=(post-start)//2
    core_bytes=len(replacement)//2
    remain=replace_bytes-core_bytes
    assert remain>=0 and (remain&1)==0

    patched=rt[:start]+replacement+('4e71'*(remain//2))+rt[post:]
    assert len(patched)==len(rt)

    routine=bytes.fromhex(patched)
    assert len(routine)==1108
    assert bytes.fromhex('4eaefe80') not in routine
    assert bytes.fromhex('4eaefec2') not in routine

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

    title=b'AMOSPro AGA M5 R2R1 IFF Clown fixed offsets 0.2.1\0$VER: AMOSPro_AGA 0.2.1\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==3708
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
