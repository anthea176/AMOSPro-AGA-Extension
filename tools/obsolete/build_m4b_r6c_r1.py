#!/usr/bin/env python3
"""M4b v0.0.9 R6C-R1 - safe Back Fill on top of validated R6B-R4.

Only Aga Back Fill changes.
The validated R6B-R4 Open/Close/Double Buffer/Swap path remains byte-for-byte unchanged.
Back Fill uses a temporary layerless RastPort pointing directly at sb_BitMap.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import inspect, parse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R4.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.9_R6C_R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='f6b3ef41375191d83ee533de19635879ff38fdac32e4182e8957370ae8e29a23'
R6C_R1_SHA='a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

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
            struct.pack_into('>h',self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def back_fill():
    a=A()
    a.e('48e7fffe')                    # preserve D0-D7/A0-A6
    a.e('2e03')                        # D7 = requested pen
    a.e('246d01c8')                    # A2 = extension state
    a.e('200a4a80'); a.br(0x6700,'done')
    a.e('4a92'); a.br(0x6700,'done')   # Screen*
    a.e('266a0020')                    # A3 = DBState* at state+32
    a.e('200b4a80'); a.br(0x6700,'done')

    # Select the non-displayed ScreenBuffer from current-front index.
    a.e('202b00084a80'); a.br(0x6700,'front0')
    a.e('2253'); a.br(0x6000,'target') # current=1 -> sb0
    a.label('front0')
    a.e('226b0004')                    # current=0 -> sb1
    a.label('target')
    a.e('20094a80'); a.br(0x6700,'done')
    a.e('2851')                        # A4 = ScreenBuffer.sb_BitMap
    a.e('200c4a80'); a.br(0x6700,'done')

    # Allocate a temporary RastPort. 128 bytes safely covers the V39 structure.
    a.e('203c00000080')                 # D0 = 128
    a.e('223c00010001')                 # D1 = MEMF_PUBLIC|MEMF_CLEAR
    a.e('2c780004')                     # A6 = ExecBase
    a.e('4eaefd54')                     # AllocVec
    a.e('4a80'); a.br(0x6700,'done')
    a.e('2640')                         # A3 = temp RastPort
    a.e('224b')                         # A1 = temp RastPort
    a.e('2c6a0008')                     # A6 = GfxBase
    a.e('4eaeff3a')                     # InitRastPort(A1)

    # Layer stays NULL; only BitMap is attached.
    a.e('274c0004')                     # rp->BitMap = back bitmap
    a.e('2007')                         # D0 = pen
    a.e('0280000000ff')                 # 0..255
    a.e('224b')                         # A1 = temp RastPort
    a.e('2c6a0008')                     # A6 = GfxBase
    a.e('4eaeff16')                     # SetRast(A1,D0)
    a.e('4eaeff1c')                     # WaitBlit

    a.e('224b')                         # A1 = temp RastPort
    a.e('2c780004')                     # A6 = ExecBase
    a.e('4eaefd4e')                     # FreeVec

    a.label('done')
    a.e('4cdf7fff4e75')
    return a.out()

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    original=[bytes(x) for x in seg]

    seg[12]=back_fill()

    for index in (0,6,8,10,11):
        assert seg[index]==original[index]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,77,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M4b R6C-R1 Back Fill 0.0.9\0$VER: AMOSPro_AGA 0.0.9\0'
    if len(title)&1:
        title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3:
        payload+=b'\0'

    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]
    parsed=parse(out)

    assert inspect(parsed)['issues']==[]
    assert len(out)==2564
    assert hashlib.sha256(out).hexdigest()==R6C_R1_SHA

    # Runtime safety gates.
    for index in (8,11,12):
        start=parsed.starts[index]
        code_i=parsed.code[start:start+2*parsed.jumps[index]]
        assert bytes.fromhex('4eaefe80') not in code_i  # WaitPort
        assert bytes.fromhex('4eaefec2') not in code_i  # Exec Wait

    bf_start=parsed.starts[12]
    bf=parsed.code[bf_start:bf_start+2*parsed.jumps[12]]
    assert bytes.fromhex('4eaeff3a') in bf  # InitRastPort
    assert bytes.fromhex('4eaeff16') in bf  # SetRast
    assert bytes.fromhex('4eaefd54') in bf  # AllocVec
    assert bytes.fromhex('4eaefd4e') in bf  # FreeVec

    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated archive',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',R6C_R1_SHA)
