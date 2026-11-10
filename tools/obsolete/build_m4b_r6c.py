#!/usr/bin/env python3
"""M4b v0.0.9 R6C - restore Back Fill on top of validated R6B-R4.

Only Aga Back Fill changes.
The validated nonblocking Swap/Close path remains byte-for-byte unchanged.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import inspect, parse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R4.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.9_R6C.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='f6b3ef41375191d83ee533de19635879ff38fdac32e4182e8957370ae8e29a23'
R6C_SHA='ee5d92d9ab076d727c3fb31b2a4f70ee5640408cf61b89b195221acdfdeb4281'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def back_fill():
    # Port of the old R4 Back Fill with the audited DBState pointer fix:
    # state+32 instead of the obsolete state+28.
    return bytes.fromhex(
        '48e7ffee'          # movem save
        '2e03'              # D7 = requested pen from D3
        '246d01c8'          # A2 = extension state
        '200a4a806700005a'  # state required
        '4a9267000054'      # Screen* required
        '266a0020'          # A3 = DBState* at +32
        '200b4a8067000048'
        '202b00084a8067000008'
        '225360000006'      # current=1 -> sb0
        '226b0004'          # current=0 -> sb1
        '20094a806700002c'
        '2851'              # A4 = target sb_BitMap
        '2052'              # A0 = Screen*
        '2a680058'          # save Screen.RastPort.BitMap
        '214c0058'          # point RastPort at back bitmap
        '0287000000ff'      # pen &= 255
        '43e80054'          # A1 = &Screen.RastPort
        '2007'              # D0 = pen
        '2c6a0008'          # A6 = GfxBase
        '4eaeff16'          # SetRast
        '4eaeff1c'          # WaitBlit
        '2052'
        '214d0058'          # restore Screen.RastPort.BitMap
        '4cdf77ff4e75'
    )

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    original=[bytes(x) for x in seg]

    seg[12]=back_fill()

    # R6B-R4 validated path must remain untouched.
    for index in (0,6,8,10,11):
        assert seg[index]==original[index]

    jumps=[len(x)//2 for x in seg]
    assert jumps==(185,2,8,8,48,167,193,75,108,15,141,74,56,0)
    code=b''.join(seg)
    title=b'AMOSPro AGA M4b R6C Back Fill 0.0.9\0$VER: AMOSPro_AGA 0.0.9\0'
    if len(title)&1: title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==2516
    assert hashlib.sha256(out).hexdigest()==R6C_SHA

    # Blocking waits remain forbidden in AMOS-facing routines.
    for index in (8,11,12):
        start=parsed.starts[index]
        code_i=parsed.code[start:start+2*parsed.jumps[index]]
        assert bytes.fromhex('4eaefe80') not in code_i
        assert bytes.fromhex('4eaefec2') not in code_i

    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated archive',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',R6C_SHA)
