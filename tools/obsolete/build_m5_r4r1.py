#!/usr/bin/env python3
"""M5 R4R1 - preserve BMHD metadata across palette loading.

R4 root cause:
- D6 packed BMHD height/depth;
- the validated SetRGB32 conversion loop also uses D6 as scratch;
- after palette load, R4 decoded BODY using destroyed metadata.

R4R1 keeps R3R1 as the binary base and changes only Aga Iff Load:
- start from the R4 proposed loader routine template;
- push D6 immediately before the palette loop;
- restore D6 immediately after the existing R3R1 WaitTOF;
- recalculate every 16-bit PC-relative branch/DBcc/LEA crossing insertions.

No change to Open / Double Buffer / Swap / Close / ByteRun1 logic.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r4 import ROUTINE_HEX as R4_ROUTINE_HEX

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.1_R3R1.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.1_R4R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='a1b24aa0f83be86858b2ba495e94259aac211208ff5a8b0d6825a3427a09cb2e'
OUT_SHA='fb1da4906b050b838fc185bfa8877ff68c59463ee12765e4dfb7d6353ac6602a'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)
def s16(b,p): return struct.unpack_from('>h',b,p)[0]

def insert_and_fix_refs(buf, pos, payload):
    rt=bytearray(buf)
    refs=[]
    for p in range(0,len(rt)-3,2):
        ins=struct.unpack_from('>H',rt,p)[0]
        if ((0x6000 <= (ins & 0xff00) <= 0x6f00 and (ins & 0x00ff)==0)
            or (ins & 0xf0f8)==0x50c8
            or (ins & 0xf1ff)==0x41fa):
            refs.append((p,p+2+s16(rt,p+2)))

    rt[pos:pos]=payload
    delta=len(payload)

    for p,target in refs:
        np=p+(delta if p>=pos else 0)
        nt=target+(delta if target>=pos else 0)
        struct.pack_into('>h',rt,np+2,nt-(np+2))
        assert np+2+s16(rt,np+2)==nt
    return bytes(rt)

def corrected_routine():
    rt=bytes.fromhex(R4_ROUTINE_HEX)
    assert len(rt)==1262

    palette=bytes.fromhex('41e97200121a')
    p=rt.find(palette)
    assert p>=0
    rt=insert_and_fix_refs(rt,p+4,bytes.fromhex('2f06'))  # move.l d6,-(sp)

    wait=bytes.fromhex('4eaefef2280b')
    p=rt.find(wait)
    assert p>=0
    rt=insert_and_fix_refs(rt,p+4,bytes.fromhex('2c1f'))  # move.l (sp)+,d6

    assert len(rt)==1266
    assert bytes.fromhex('2f06121a') in rt
    assert bytes.fromhex('4eaefef22c1f280b') in rt
    assert bytes.fromhex('4480') in rt
    assert bytes.fromhex('4eaefe80') not in rt
    assert bytes.fromhex('4eaefec2') not in rt
    return rt

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    seg[13]=corrected_routine()
    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,633,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5 R4R1 preserve D6 0.4.1\0$VER: AMOSPro_AGA 0.4.1\0'
    if len(title)&1: title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==3864
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    assert inspect(parse(out))['issues']==[]
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
