#!/usr/bin/env python3
"""M5 R1D3 - exact IFF diagnostic with result preserved across cleanup.

The diagnostic code is pushed on the stack before DOS/Exec cleanup calls,
then restored into D3 immediately before returning to AMOS.
"""
from pathlib import Path
import struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.1.3_R1D3.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

def w(n): return struct.pack('>H',n & 0xffff)
def l(n): return struct.pack('>I',n & 0xffffffff)

class A:
    def __init__(self):
        self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h):
        self.b += bytes.fromhex(h.replace(' ',''))
    def label(self,n):
        self.labels[n]=len(self.b)
    def br(self,op,label):
        p=len(self.b); self.b += w(op)+b'\0\0'; self.fix.append((p+2,label))
    def dbra(self,reg,label):
        p=len(self.b); self.b += w(0x51c8+reg)+b'\0\0'; self.fix.append((p+2,label))
    def leapc(self,an,label):
        p=len(self.b); self.b += w(0x41fa+(an<<9))+b'\0\0'; self.fix.append((p+2,label))
    def out(self):
        for ext,label in self.fix:
            struct.pack_into('>h',self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def diag_routine():
    a=A()
    a.e('48e7effe')              # preserve all ordinary regs except D3/A7
    a.e('2e03')                  # D7 = AMOS string ptr
    a.e('7c0a')                  # diag 10
    a.e('2446264628467a00')      # A2/A3/A4=0, D5=0

    a.e('2047780038184a44')      # A0=D7, D4=string length
    a.br(0x6700,'cleanup')

    a.e('7c0b')                  # diag 11
    a.e('20045280223c000100012c7800044eaefd544a80')
    a.br(0x6700,'cleanup')
    a.e('2440')                  # A2=C string

    a.e('204741e80002224a5344')  # src string+2, dst A2, count-1
    a.label('copy')
    a.e('12d8')
    a.dbra(4,'copy')
    a.e('4211')                  # NUL

    a.e('7c0c')                  # diag 12
    a.leapc(1,'dosname')
    a.e('70002c7800044eaefdd828404a80')
    a.br(0x6700,'cleanup')

    a.e('7c0d')                  # diag 13
    a.e('220a243c000003ed2c4c4eaeffe22a004a85')
    a.br(0x6700,'cleanup')

    a.e('7c0e')                  # diag 14
    a.e('700c223c000100012c7800044eaefd544a80')
    a.br(0x6700,'cleanup')
    a.e('2640')                  # A3=12-byte header
    a.e('2205240b760c2c4c4eaeffd60c800000000c')
    a.br(0x6600,'cleanup')

    a.e('7c0f')                  # diag 15
    a.e('20130c80464f524d')
    a.br(0x6600,'cleanup')

    a.e('7c10')                  # diag 16
    a.e('202b00080c80494c424d')
    a.br(0x6600,'cleanup')

    a.e('7c11')                  # diag 17

    a.label('cleanup')
    a.e('2f06')                  # PUSH diagnostic result before library calls

    a.e('4a85')
    a.br(0x6700,'freebuf')
    a.e('2c4c22054eaeffdc7a00')

    a.label('freebuf')
    a.e('200b4a80')
    a.br(0x6700,'closedos')
    a.e('224b2c7800044eaefd4e2646')

    a.label('closedos')
    a.e('200c4a80')
    a.br(0x6700,'freecstr')
    a.e('224c2c7800044eaefe622846')

    a.label('freecstr')
    a.e('200a4a80')
    a.br(0x6700,'done')
    a.e('224a2c7800044eaefd4e2446')

    a.label('done')
    a.e('261f')                  # POP preserved diagnostic into D3
    a.e('4cdf7ff7')              # restore regs except D3
    a.e('7400')                  # AMOS integer result type
    a.e('4e75')

    a.label('dosname')
    a.e('646f732e6c69627261727900')
    if len(a.b)&1: a.e('00')
    return a.out()

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1] |= 0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=BASE.read_bytes()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    tok=bytearray(base.tokens[:-6])
    tok += token_function('aga iff load',13,'2')
    tok += b'\0'*6
    if len(tok)&1: tok += b'\0'

    routine=diag_routine()
    assert len(routine)==302
    code=base.code+b'GetP'+routine

    jumps=list(base.jumps)
    jumps[12]+=2
    jumps[13]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,151,0]

    title=b'AMOSPro AGA M5 R1D3 IFF diagnostic 0.1.3\0$VER: AMOSPro_AGA 0.1.3\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    assert len(out)==2892
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
