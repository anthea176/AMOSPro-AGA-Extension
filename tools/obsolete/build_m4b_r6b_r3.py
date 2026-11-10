#!/usr/bin/env python3
"""M4b v0.0.8 R6B-R3 - preserve launch-proven R1 cold/close/db, replace Swap only.

Build policy: archive candidate and mirror exact bytes to dist/AMOSPro_AGA.Lib.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import inspect, parse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R1.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R3.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='6c5e4dba8d91a2d80abc45630155a18e86bc663667441529acec1e47a9b9da15'
R6B_SHA='0565c40049573a719465892dafcfd87647e01ac7f4a9ca06eae2dafbcbe7978d'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

class A:
    def __init__(self): self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h): self.b += bytes.fromhex(h.replace(' ',''))
    def label(self,n): self.labels[n]=len(self.b)
    def br(self,op,label):
        p=len(self.b); self.b += w(op)+b'\0\0'; self.fix.append((p+2,label))
    def out(self):
        for ext,label in self.fix:
            struct.pack_into('>h',self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def swap_once():
    a=A(); a.e('48e7effe7600246d01c84a92'); a.br(0x6700,'done')
    a.e('286a0020200c4a80'); a.br(0x6700,'done')
    a.e('202c000c4a80'); a.br(0x6700,'done')
    a.e('202c00104a80'); a.br(0x6700,'done')
    a.e('202c00084a80'); a.br(0x6700,'front0')
    a.e('22547e00'); a.br(0x6000,'have_target')
    a.label('front0'); a.e('226c00047e01')
    a.label('have_target'); a.e('20094a80'); a.br(0x6700,'done')
    a.e('20522c6a00044eaeff04')       # ScreenToFront(screen)
    a.e('2c6a00084eaeff1c')           # WaitBlit
    a.e('205222492c6a00044eaefcf4')   # ChangeScreenBuffer
    a.e('4a80'); a.br(0x6700,'done')
    a.e('29470008')                   # current index
    a.e('206c000c2c7800044eaefe80206c000c4eaefe8c4a80'); a.br(0x6700,'done')
    a.e('206c00102c7800044eaefe80206c00104eaefe8c4a80'); a.br(0x6700,'done')
    a.e('42ac0014')                   # keep R1 Close from waiting again
    a.e('7601')
    a.label('done'); a.e('4cdf7ff774004e75')
    return a.out()

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    original=[bytes(x) for x in seg]
    seg[11]=swap_once()+b'GetP'
    # Launch-critical entries remain byte-for-byte R1.
    assert seg[0]==original[0]
    assert seg[8]==original[8]
    assert seg[10]==original[10]
    assert seg[6]==original[6]
    jumps=[len(s)//2 for s in seg]
    assert jumps==[185,2,8,8,48,167,193,75,141,15,141,95,1,0]
    code=b''.join(seg)
    title=b'AMOSPro AGA M4b R6B-R3 experimental 0.0.8\0$VER: AMOSPro_AGA 0.0.8\0'
    if len(title)&1: title+=b'\0'
    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]
    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==2520
    assert hashlib.sha256(out).hexdigest()==R6B_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated archive',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',R6B_SHA)
