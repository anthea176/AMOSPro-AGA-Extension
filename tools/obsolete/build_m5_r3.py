#!/usr/bin/env python3
"""M5 R3 - generic 320x200x8 ByteRun1 ILBM scanner.

Built on the user-validated R2R4 baseline:
- keeps Aga Screen Open / SA_FullPalette from R2R4 unchanged;
- restores the original generic R2 BMHD/CMAP/BODY chunk scanner;
- keeps the validated ByteRun1 fix NEG.W D0 -> NEG.L D0;
- removes all Clown.iff-specific CMAP/BODY offsets.

Current R3 scope:
- FORM ILBM
- 320x200
- 8 planes
- masking = 0
- compression = ByteRun1 (1)
- CMAP >= 256 RGB entries
- unknown chunks and odd-size chunk padding are skipped generically

Uncompressed BODY (compression=0) is deliberately deferred until this generic
ByteRun1 path is validated at runtime.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r2 import ROUTINE_HEX
from build_m5_r2r4 import build as build_r2r4

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.0_R3.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='f48ec52b793b77e3e64d61cc88ec1028845ce7a40d9c5480e659a02f5c7ac9dc'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def build():
    raw=build_r2r4()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    # Split AP20 code into command segments.
    seg=[]
    p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n])
        p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    # Restore the original generic R2 loader routine.
    routine=bytearray.fromhex(ROUTINE_HEX)
    assert len(routine)==1108

    # Keep the ByteRun1 negative-run fix proven by R2R2.
    hits=[i for i in range(len(routine)-1) if routine[i:i+2]==b'\x44\x40']
    assert hits==[924],hits
    routine[924:926]=b'\x44\x80'

    # Static guards for the generic chunk scanner.
    assert b'BMHD' in routine
    assert b'CMAP' in routine
    assert b'BODY' in routine
    assert bytes.fromhex('4de80008') in routine   # lea 8(a0),a6: chunk payload
    assert bytes.fromhex('0281fffffffe') in routine  # even chunk padding
    assert bytes.fromhex('0c2e0001000a') in routine  # BMHD compression=1

    # Only Aga Iff Load changes versus R2R4.
    seg[13]=bytes(routine)
    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,554,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5 R3 generic ILBM ByteRun1 0.3.0\0$VER: AMOSPro_AGA 0.3.0\0'
    if len(title)&1:
        title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3:
        payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]
    assert len(out)==3712
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
