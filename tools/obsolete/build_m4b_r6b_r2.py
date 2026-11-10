#!/usr/bin/env python3
"""M4b v0.0.8 R6B-R2 - visible synchronized single swap.

The test target is always mirrored to dist/AMOSPro_AGA.Lib.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import inspect, parse

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.7_R6A.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='cce0104e1cecf6842de008b58df0533e126cf6b1402f1bedfdc1a45ee88cf784'
R6B_SHA='f7100189ccd69ec7d8d1eca774b6f89cd67c4cbd96df98adf0ccd9c96454978c'

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

def cleanup():
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

def double_buffer():
    a=A(); a.e('48e7effe7600246d01c84a92'); a.br(0x6700,'done')
    a.e('286a0020200c4a80'); a.br(0x6600,'already')
    a.e('7014223c000100012c7800044eaefd544a80'); a.br(0x6700,'done')
    a.e('2840')
    a.e('2c7800044eaefd664a80'); a.br(0x6700,'fail_vec')
    a.e('2940000c')
    a.e('2c7800044eaefd664a80'); a.br(0x6700,'fail_ports')
    a.e('29400010')
    a.e('205293c970012c6a00044eaefd004a80'); a.br(0x6700,'fail_ports')
    a.e('2880')
    a.e('205293c970022c6a00044eaefd004a80'); a.br(0x6700,'fail_sb0')
    a.e('29400004')
    a.e('205420684a80'); a.br(0x6700,'fail_both')
    a.e('202c000c21400016202c001021400036')
    a.e('206c000420684a80'); a.br(0x6700,'fail_both')
    a.e('202c000c21400016202c001021400036')
    a.e('254c0020')
    a.label('already'); a.e('7601'); a.br(0x6000,'done')
    a.label('fail_both')
    a.e('2052226c00042c6a00044eaefcfa')
    a.label('fail_sb0')
    a.e('205222542c6a00044eaefcfa')
    a.label('fail_ports')
    a.e('2c780004206c001020084a80'); a.br(0x6700,'skip_disp')
    a.e('4eaefd60')
    a.label('skip_disp')
    a.e('206c000c20084a80'); a.br(0x6700,'fail_vec')
    a.e('4eaefd60')
    a.label('fail_vec')
    a.e('224c2c7800044eaefd4e')
    a.label('done'); a.e('4cdf7ff774004e75')
    return a.out()

def swap_once():
    a=A(); a.e('48e7effe7600246d01c84a92'); a.br(0x6700,'done')
    a.e('286a0020200c4a80'); a.br(0x6700,'done')
    a.e('202c000c4a80'); a.br(0x6700,'done')
    a.e('202c00104a80'); a.br(0x6700,'done')
    a.e('202c00084a80'); a.br(0x6700,'front0')
    a.e('22547e00'); a.br(0x6000,'have_target')
    a.label('front0'); a.e('226c00047e01')
    a.label('have_target'); a.e('20094a80'); a.br(0x6700,'done')
    # The screen must actually become visible for DispMessage to be returned.
    a.e('20522c6a00044eaeff04')       # ScreenToFront(screen), LVO -252
    a.e('2c6a00084eaeff1c')           # WaitBlit
    a.e('205222492c6a00044eaefcf4')   # ChangeScreenBuffer
    a.e('4a80'); a.br(0x6700,'done')
    a.e('29470008')                   # publish current index only after success
    a.e('206c000c2c7800044eaefe80206c000c4eaefe8c4a80'); a.br(0x6700,'done')
    a.e('206c00102c7800044eaefe80206c00104eaefe8c4a80'); a.br(0x6700,'done')
    a.e('7601')
    a.label('done'); a.e('4cdf7ff774004e75')
    return a.out()

def build():
    raw=BASE.read_bytes(); assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw); seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    cl=cleanup(); init=bytearray(seg[0][:56]); state_start=56+len(cl)
    struct.pack_into('>h',init,12,state_start-12)
    struct.pack_into('>h',init,32,state_start-32)
    seg[0]=bytes(init)+cl+b'\0'*36
    seg[8]=cl+b'GetP'
    seg[10]=double_buffer()+b'GetP'
    seg[11]=swap_once()+b'GetP'
    seg[12]=b'\x4e\x75'
    jumps=[len(s)//2 for s in seg]; code=b''.join(seg)
    assert jumps==[152,2,8,8,48,167,193,75,108,15,141,93,1,0]
    title=b'AMOSPro AGA M4b R6B-R2 experimental 0.0.8\0$VER: AMOSPro_AGA 0.0.8\0'
    if len(title)&1: title+=b'\0'
    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(v) for v in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]
    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==2384
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
