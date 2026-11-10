#!/usr/bin/env python3
"""M5.2 R5R1 0.4.7 - reject image/screen mismatch safely.

Base: M5.2 R5 0.4.6.

Safety contract:
- before palette or BODY processing, validate the BMHD against the current
  AGA screen state;
- require width 320, height equal to current screen, depth equal to current
  screen, depth 3..8, masking=0 and compression=1;
- on any mismatch, follow the existing loader failure path and return 0;
- no palette/BODY write is attempted on mismatch;
- public Aga Iff Load segment keeps exactly the same size;
- no new AMOS token is introduced.

This prevents cases such as loading Clown.iff (320x200x8) into a
320x256x4 screen from reaching the decoder and crashing.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.7_M52R5R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715'
OUT_SHA='ec18e5d4fdb02a7e2ab312c09ae23fcefd87acfe4768e7402d5d3d0e66318e25'

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

def branch_target(buf,op):
    return op+2+s16(buf,op+2)

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
    a.e('2f08')            # move.l a0,-(sp)
    a.e('206d01c8')        # movea.l $1C8(a5),a0 : extension state
    a.e('2008')            # move.l a0,d0
    a.e('4a80')            # tst.l d0
    a.br(0x6700,'fail')
    a.e('2010')            # move.l (a0),d0 : Screen*
    a.e('4a80')
    a.br(0x6700,'fail')

    # Loader M5.2 remains 320px only.
    a.e('0c560140')        # cmpi.w #320,(a6)
    a.br(0x6600,'fail')

    # BMHD width == state width (state +$0C, long).
    a.e('7000')
    a.e('3016')            # move.w (a6),d0
    a.e('b0a8000c')        # cmp.l $0C(a0),d0
    a.br(0x6600,'fail')

    # BMHD height == state height (state +$10, long).
    a.e('7000')
    a.e('302e0002')
    a.e('b0a80010')
    a.br(0x6600,'fail')

    # BMHD depth 3..8 and equal to state depth (+$1C, long).
    a.e('7000')
    a.e('102e0008')
    a.e('0c000003')
    a.br(0x6500,'fail')    # <3
    a.e('0c000008')
    a.br(0x6200,'fail')    # >8
    a.e('b0a8001c')
    a.br(0x6600,'fail')

    # No mask yet; ByteRun1 only in M5.2.
    a.e('4a2e0009')
    a.br(0x6600,'fail')
    a.e('0c2e0001000a')
    a.br(0x6600,'fail')

    a.e('7001')
    a.br(0x6000,'done')
    a.label('fail')
    a.e('7000')
    a.label('done')
    a.e('205f')            # restore a0
    a.e('4e75')
    out=a.out()
    assert len(out)==116
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

    # Original R5 validation block is 48 bytes, ending just before:
    # moveq #1,d6 / bra.w found-BMHD.
    start=find_unique(loader,bytes.fromhex('0c5601406600'))
    tail=find_unique(loader,bytes.fromhex('7c0160000012'))
    assert tail-start==48

    # Existing mismatch/failure target from the original width check.
    fail=branch_target(loader,start+4)

    # Same-size public patch: call hidden guard, test D0, branch to existing
    # failure cleanup, then NOP the rest. Existing moveq/bra tail stays intact.
    patch=bytearray.fromhex('610000004a0067000000')
    patch += bytes.fromhex('4e71')*19
    assert len(patch)==48
    loader[start:start+48]=patch

    guard=build_guard()
    guard_off=len(seg[15])
    seg[15] += guard

    # Existing public segment sizes stay fixed; helper segment may grow.
    for i in range(15):
        assert len(seg[i])==len(original[i])
        if i!=13:
            assert bytes(seg[i])==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,87,0]

    starts=[]; acc=0
    for x in seg:
        starts.append(acc); acc+=len(x)

    # Patch BSR.W to appended guard inside hidden helper segment.
    ext=starts[13]+start+2
    target=starts[15]+guard_off
    disp=target-ext
    assert -32768 <= disp <= 32767
    struct.pack_into('>h',loader,start+2,disp)

    # Patch BEQ.W to existing loader failure cleanup.
    struct.pack_into('>h',loader,start+8,fail-(start+8))

    # Original success tail must remain at same offset.
    assert loader[tail:tail+6]==bytes.fromhex('7c0160000012')

    code=b''.join(bytes(x) for x in seg)
    title=b'AMOSPro AGA M5.2 R5R1 safe mismatch 0.4.7\0$VER: AMOSPro_AGA 0.4.7\0'
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
    assert len(out)==4676
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
