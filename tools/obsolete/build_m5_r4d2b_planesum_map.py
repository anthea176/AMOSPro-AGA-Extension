#!/usr/bin/env python3
"""M5.2 R4D2b - reuse existing Aga Plane Sum token as displayed-plane mapper.

Base: R4D1 plane-sum diagnostic, whose temporary token Aga Plane Sum(N)
was already runtime-validated by the user.

No new AMOS keyword is introduced.

Temporary behavior of Aga Plane Sum(N) in this diagnostic:
- after Aga Swap,
- N = displayed RasInfo plane 0..7,
- return = matching front ScreenBuffer plane index 0..7,
- return -1 if no pointer matches.

The mapping routine is the previously validated historical R2D11 routine.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r4d1_kekko_plane_sum import build as build_r4d1

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_R4D2B_PLANESUM_MAP.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='b987bc9c6b03b686def4e17e5c515b9683f05e76574cf2b5cb2b4b590893f826'

MAP_HEX=(
'48e7effe280376ff4a846b0000a40c84000000076e00009a246d01c8200a'
'4a806700008e205220084a8067000084266a0020200b4a8067000078202b'
'00084a806700000a226b000460000004225320094a806700005c2851200c'
'4a80670000522068005020084a80670000462068000420084a806700003a'
'41e800082a044a856700000a588853856600fffa265049ec00087a002014'
'220bb28067000012588c52450c4500086600ffec6000000426054cdf7ff7'
'74004e75'
)

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def build():
    raw=build_r4d1()
    base=parse(raw)
    assert inspect(base)['issues']==[]
    assert list(base.jumps)==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,381,51,0]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    routine=bytes.fromhex(MAP_HEX)
    assert len(routine)==184
    seg[15]=routine

    # Everything except the already-existing temporary diagnostic routine
    # stays byte-for-byte identical. Token table is untouched.
    for i in range(len(seg)):
        if i!=15:
            assert seg[i]==original[i]

    jumps=list(base.jumps)
    jumps[15]=len(routine)//2
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,381,92,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5.2 R4D2b PlaneSum-as-map 0.4.5d2b\0$VER: AMOSPro_AGA 0.4.5d2b\0'
    if len(title)&1: title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    assert parsed.tokens==base.tokens

    rows=[x for x in audit['tokens'] if x['name']=='aga plane sum']
    assert len(rows)==1 and rows[0]['function']==15
    checks=[x for x in audit['parameter_checks'] if x['name']=='aga plane sum']
    assert len(checks)==1 and checks[0]['getp'] is True

    assert len(out)==4720
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
