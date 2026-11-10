#!/usr/bin/env python3
"""M5 R3R1 - palette synchronization after generic ILBM load.

Built on validated M5-R3 0.3.0.

Observed runtime difference:
- literal path DH6:Clown.iff could sometimes show wrong colours;
- selecting the same file through Fsel$ produced correct colours.

The filename ABI itself was already validated by R1D3. R3R1 therefore keeps
the loader, scanner and ByteRun1 logic unchanged and adds exactly one
graphics.library/WaitTOF after the complete palette loop.

Goal: make palette/copper state deterministic before BODY display/swap,
independent of requester timing.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r3 import build as build_r3

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.1_R3R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='a1b24aa0f83be86858b2ba495e94259aac211208ff5a8b0d6825a3427a09cb2e'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)
def s16(b,p): return struct.unpack_from('>h',b,p)[0]

def patch_palette_sync(seg):
    rt=bytearray(seg)
    pat=bytes.fromhex('4eaefcac52450c4501006600ffc0280b')
    pos=rt.find(pat)
    assert pos>=0
    insert_pos=pos+14
    delta=4

    refs=[]
    for p in range(0,len(rt)-3,2):
        ins=struct.unpack_from('>H',rt,p)[0]
        kind=None
        if 0x6000 <= (ins & 0xff00) <= 0x6f00 and (ins & 0x00ff)==0:
            kind='branch'
        elif (ins & 0xf0f8)==0x50c8:
            kind='dbcc'
        elif (ins & 0xf1ff)==0x41fa:
            kind='leapc'
        if kind:
            refs.append((kind,p,p+2+s16(rt,p+2)))

    for _kind,p,target in refs:
        if p<insert_pos and target>=insert_pos:
            struct.pack_into('>h',rt,p+2,s16(rt,p+2)+delta)

    rt[insert_pos:insert_pos]=bytes.fromhex('4eaefef2')  # WaitTOF

    for kind,p,target in refs:
        np=p+delta if p>=insert_pos else p
        got=np+2+s16(rt,np+2)
        expected=target+delta if target>=insert_pos else target
        assert got==expected,(kind,p,got,expected)

    assert rt[insert_pos:insert_pos+4]==bytes.fromhex('4eaefef2')
    return bytes(rt)

def build():
    raw=build_r3()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    seg=[]
    p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n])
        p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    seg[13]=patch_palette_sync(seg[13])

    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,556,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5 R3R1 palette sync 0.3.1\0$VER: AMOSPro_AGA 0.3.1\0'
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
