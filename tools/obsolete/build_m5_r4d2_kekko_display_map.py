#!/usr/bin/env python3
"""M5.2 R4D2 - temporary KEKKO displayed-plane mapping diagnostic.

Base: R4D1 plane-sum diagnostic.

Adds:
    value=Aga Plane Map(displayed_plane)

After Aga Swap, returns the matching front ScreenBuffer plane index (0..7)
for a displayed RasInfo plane, or -1 if no pointer matches.

Reuses the previously validated historical R2D11 pointer-mapping routine.
No existing runtime routine is modified.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r4d1_kekko_plane_sum import build as build_r4d1

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_R4D2_KEKKO_DISPLAY_MAP.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='9f3296d8d07aaa108081a41b9510efe265cb5606a6f9616a6db148a4fb146c43'

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

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    out=w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'
    if len(out)&1: out+=b'\0'
    return out

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

    seg[15]=seg[15]+b'GetP'
    seg[16]=routine
    seg.append(b'')

    for i in range(15):
        assert seg[i]==original[i]
    assert seg[15][:-4]==original[15]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,381,53,92,0]
    code=b''.join(seg)

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga plane map',16,'0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    title=b'AMOSPro AGA M5.2 R4D2 KEKKO display map 0.4.5d2\0$VER: AMOSPro_AGA 0.4.5d2\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    rows=[x for x in audit['tokens'] if x['name']=='aga plane map']
    assert len(rows)==1 and rows[0]['function']==16
    checks=[x for x in audit['parameter_checks'] if x['name']=='aga plane map']
    assert len(checks)==1 and checks[0]['getp'] is True

    assert len(out)==4844
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
