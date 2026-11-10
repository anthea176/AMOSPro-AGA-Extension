#!/usr/bin/env python3
"""M5.2 R5R2 0.4.8 - transparent image/screen mismatch guard.

Base: M5.2 R5 0.4.6, the runtime version where KEKKO palette was correct.

R5R1 regression:
- its mismatch guard used D0 as scratch and returned with D0 modified;
- the original BMHD validation block did not modify D0;
- the chunk/palette path later reused D0, reintroducing the KEKKO palette bug.

R5R2 fix:
- preserve D0, D6 and A0 across the guard;
- return success/failure only through the CPU Z flag;
- caller branches immediately on Z, without touching D0;
- keep the public Aga Iff Load segment exactly the same size;
- keep all R5 palette/BODY/double-buffer behavior unchanged;
- no new AMOS token.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.8_M52R5R2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715'
OUT_SHA='4f447bce27fa7db1e86a8fb0d53d4e125e5bf7c6cf83474b4be61a3bf4eda377'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)
def s16(buf,p): return struct.unpack_from('>h',buf,p)[0]

def find_unique(buf,pat):
    hits=[]; p=0
    while True:
        p=buf.find(pat,p)
        if p<0: break
        hits.append(p); p+=1
    assert len(hits)==1,(pat.hex(),hits)
    return hits[0]

class A:
    def __init__(self):
        self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h):
        self.b += bytes.fromhex(h.replace(' ',''))
    def label(self,n):
        self.labels[n]=len(self.b)
    def br(self,op,label):
        p=len(self.b); self.b += w(op)+b'\0\0'; self.fix.append((p+2,label))
    def out(self):
        for ext,label in self.fix:
            disp=self.labels[label]-ext
            assert -32768 <= disp <= 32767
            struct.pack_into('>h',self.b,ext,disp)
        return bytes(self.b)

def build_guard():
    a=A()

    # Preserve every register this guard touches and that R5 may reuse later.
    # MOVEM restore does not modify CCR, so the Z flag can carry the result.
    a.e('48e78200')        # movem.l d0/d6,-(sp)
    a.e('2f08')            # move.l a0,-(sp)
    a.e('7c00')            # d6=0 => fail by default

    a.e('206d01c8')        # a0=extension state
    a.e('2008'); a.e('4a80'); a.br(0x6700,'done')
    a.e('2010'); a.e('4a80'); a.br(0x6700,'done')

    # M5.2 loader scope: 320px indexed only.
    a.e('0c560140'); a.br(0x6600,'done')

    # BMHD width == current screen width.
    a.e('7000')
    a.e('3016')
    a.e('b0a8000c')
    a.br(0x6600,'done')

    # BMHD height == current screen height.
    a.e('7000')
    a.e('302e0002')
    a.e('b0a80010')
    a.br(0x6600,'done')

    # BMHD depth 3..8 and equal to current screen depth.
    a.e('7000')
    a.e('102e0008')
    a.e('0c000003'); a.br(0x6500,'done')
    a.e('0c000008'); a.br(0x6200,'done')
    a.e('b0a8001c'); a.br(0x6600,'done')

    # No mask yet; ByteRun1 only at M5.2.
    a.e('4a2e0009'); a.br(0x6600,'done')
    a.e('0c2e0001000a'); a.br(0x6600,'done')

    a.e('7c01')            # success
    a.label('done')

    a.e('205f')            # restore a0
    a.e('4a06')            # tst.b d6 => Z=1 fail / Z=0 success
    a.e('4cdf0041')        # restore d0/d6, CCR preserved
    a.e('4e75')

    out=a.out()
    assert len(out)==122
    return out

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]
    assert list(base.jumps)==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,29,0]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(bytearray(base.code[p:p+2*n])); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    loader=seg[13]
    start=find_unique(loader,bytes.fromhex('0c5601406600'))
    tail=find_unique(loader,bytes.fromhex('7c0160000012'))
    assert tail-start==48

    # Original failure branch is BNE.W at start+4.
    fail=(start+4)+2+s16(loader,start+6)

    # BSR.W guard ; BEQ.W original failure ; NOP padding.
    # No TST in caller: guard's Z flag survives RTS.
    patch=bytearray.fromhex('6100000067000000')
    patch += bytes.fromhex('4e71')*20
    assert len(patch)==48
    loader[start:start+48]=patch

    guard=build_guard()
    guard_off=len(seg[15])
    seg[15]+=guard

    # Public routines remain fixed-size and byte-identical except the local
    # validation block inside Aga Iff Load.
    for i in range(15):
        assert len(seg[i])==len(original[i])
        if i!=13:
            assert bytes(seg[i])==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,90,0]

    starts=[]; acc=0
    for x in seg:
        starts.append(acc); acc+=len(x)

    ext=starts[13]+start+2
    target=starts[15]+guard_off
    disp=target-ext
    assert -32768 <= disp <= 32767
    struct.pack_into('>h',loader,start+2,disp)

    # BEQ.W displacement extension is at start+6.
    struct.pack_into('>h',loader,start+6,fail-(start+6))

    assert loader[tail:tail+6]==bytes.fromhex('7c0160000012')

    code=b''.join(bytes(x) for x in seg)
    title=b'AMOSPro AGA M5.2 R5R2 transparent guard 0.4.8\0$VER: AMOSPro_AGA 0.4.8\0'
    if len(title)&1: title+=b'\0'

    off=len(jumps)*2
    nt=len(base.tokens)
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    assert parsed.tokens==base.tokens
    assert len(out)==4684
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
