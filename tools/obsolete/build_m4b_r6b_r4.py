#!/usr/bin/env python3
"""M4b v0.0.8 R6B-R4 - nonblocking swap candidate.

Base: R6B-R1 (launch-proven).
Policy:
- Cold/hooks remain launch-proven.
- explicit Close has no WaitPort/Exec Wait.
- Swap uses only nonblocking GetMsg polling plus one ChangeScreenBuffer attempt.
- mirror exact candidate to dist/AMOSPro_AGA.Lib.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import inspect, parse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R1.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R4.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='6c5e4dba8d91a2d80abc45630155a18e86bc663667441529acec1e47a9b9da15'
R6B_SHA='f6b3ef41375191d83ee533de19635879ff38fdac32e4182e8957370ae8e29a23'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

class A:
    def __init__(self): self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h): self.b+=bytes.fromhex(h.replace(' ',''))
    def label(self,n): self.labels[n]=len(self.b)
    def br(self,op,label):
        p=len(self.b); self.b+=w(op)+b'\0\0'; self.fix.append((p+2,label))
    def out(self):
        for ext,label in self.fix:
            struct.pack_into('>h',self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def close_nonblocking():
    a=A(); a.e('48e7fffe246d01c8286a0020200c4a80'); a.br(0x6700,'close_screen')
    a.e('2c6a0008200e4a80'); a.br(0x6700,'free_sbs')
    a.e('4eaeff1c')
    a.label('free_sbs')
    a.e('205220084a80'); a.br(0x6700,'delete_ports')
    a.e('2c6a0004226c000420094a80'); a.br(0x6700,'skip_sb1')
    a.e('4eaefcfa')
    a.label('skip_sb1')
    a.e('225420094a80'); a.br(0x6700,'delete_ports')
    a.e('20524eaefcfa')
    a.label('delete_ports')
    a.e('2c780004206c001020084a80'); a.br(0x6700,'skip_disp')
    a.e('4eaefd60')
    a.label('skip_disp')
    a.e('206c000c20084a80'); a.br(0x6700,'free_vec')
    a.e('4eaefd60')
    a.label('free_vec')
    a.e('224c4eaefd4e42aa0020')
    a.label('close_screen')
    a.e('4a92'); a.br(0x6700,'close_gfx')
    a.e('20522c6a00044eaeffbe4292')
    a.label('close_gfx')
    a.e('226a000820094a80'); a.br(0x6700,'close_intui')
    a.e('2c7800044eaefe6242aa0008')
    a.label('close_intui')
    a.e('226a000420094a80'); a.br(0x6700,'clear_tail')
    a.e('2c7800044eaefe6242aa0004')
    a.label('clear_tail')
    a.e('41ea000c7004429851c8fffc4cdf7fff4e75')
    return a.out()

def swap_nonblocking():
    a=A(); a.e('48e7effe7600246d01c84a92'); a.br(0x6700,'done')
    a.e('286a0020200c4a80'); a.br(0x6700,'done')
    a.e('202c000c4a80'); a.br(0x6700,'done')
    a.e('202c00104a80'); a.br(0x6700,'done')
    # Drain already-delivered notifications only. GetMsg never blocks.
    a.e('206c000c2c7800044eaefe8c')
    a.e('206c00102c7800044eaefe8c')
    a.e('202c00084a80'); a.br(0x6700,'front0')
    a.e('22547e00'); a.br(0x6000,'have_target')
    a.label('front0'); a.e('226c00047e01')
    a.label('have_target'); a.e('20094a80'); a.br(0x6700,'done')
    a.e('2c6a00084eaeff1c')
    a.e('205222492c6a00044eaefcf4')
    a.e('4a80'); a.br(0x6700,'done')
    a.e('294700087601')
    a.label('done'); a.e('4cdf7ff774004e75')
    return a.out()

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n

    # Keep launch-proven Cold/Open/DB allocation untouched.
    original=[bytes(x) for x in seg]
    seg[8]=close_nonblocking()+b'GetP'
    seg[11]=swap_nonblocking()+b'GetP'
    assert seg[0]==original[0]
    assert seg[6]==original[6]
    assert seg[10]==original[10]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,1,0]
    code=b''.join(seg)
    title=b'AMOSPro AGA M4b R6B-R4 nonblocking 0.0.8\0$VER: AMOSPro_AGA 0.0.8\0'
    if len(title)&1: title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==2412
    assert hashlib.sha256(out).hexdigest()==R6B_SHA

    for index in (8,11,12):
        start=parsed.starts[index]
        code_i=parsed.code[start:start+2*parsed.jumps[index]]
        assert bytes.fromhex('4eaefe80') not in code_i  # WaitPort
        assert bytes.fromhex('4eaefec2') not in code_i  # Exec Wait

    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated archive',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',R6B_SHA)
