#!/usr/bin/env python3
"""M5.2 R4D1 - temporary KEKKO plane checksum diagnostic.

Base: M5.2 R4 0.4.5.

Adds one temporary function:
    value=Aga Plane Sum(plane)

For this diagnostic it sums exactly 10240 bytes, i.e. one 320x256 plane
(40 bytes/row * 256 rows). Use only with 320x256 fixtures.

No existing runtime routine is modified.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_M52R4.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_R4D1_KEKKO_PLANE_SUM.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178'
OUT_SHA='95c9fd890bc2c98f257ba9efe8c5909966cc4e8f975a1f79a2d719ff6c513923'

ROUTINE_HEX=(
'48e7effe28034a846b0000520c84000000076e000048206d01c820680020'
'202800084a806700000820506000000620680004205041e800084a846700'
'000a588853846600fffa20507600323c27ff70001018d68051c9fff860000'
'00476004cdf7ff774004e75'
)

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    out=w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'
    if len(out)&1: out+=b'\0'
    return out

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]
    assert list(base.jumps)==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,0]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==102

    # Parameterized function after PicInfo: append GetP dispatcher to PicInfo.
    seg[14]=seg[14]+b'GetP'
    seg[15]=routine
    seg.append(b'')

    # All existing routines remain byte-for-byte identical.
    for i in range(14):
        assert seg[i]==original[i]
    assert seg[14][:-4]==original[14]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,381,51,0]
    code=b''.join(seg)

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga plane sum',15,'0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    title=b'AMOSPro AGA M5.2 R4D1 KEKKO plane sum 0.4.5d1\0$VER: AMOSPro_AGA 0.4.5d1\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    rows=[x for x in audit['tokens'] if x['name']=='aga plane sum']
    assert len(rows)==1 and rows[0]['function']==15
    checks=[x for x in audit['parameter_checks'] if x['name']=='aga plane sum']
    assert len(checks)==1 and checks[0]['getp'] is True

    assert len(out)==4632
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
