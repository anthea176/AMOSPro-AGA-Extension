#!/usr/bin/env python3
"""M5 R2 - first visible IFF/ILBM loader candidate.

Scope deliberately limited to the real fixture Clown.iff:
- FORM ILBM
- BMHD 320x200, 8 planes, no mask, ByteRun1 compression
- CMAP 256 colours
- BODY decoded line/plane order into the validated AGA back-buffer
- palette loaded with SetRGB32
- caller performs Aga Swap

All M4b LAST_GOOD routines remain byte-for-byte unchanged.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.0_R2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615'
OUT_SHA='51ae184fcf2279b2a8c2f0d3f60a0498e171871a9956b34d17dccac2c213c919'
ROUTINE_HEX='''48e7effe7c007e007a0078002446264628462043780038184a446700013c20045280223c000100012c7800044eaefd544a80670001242440204341e80002224a534412d851ccfffc12bc000043fa03fa70002c7800044eaefdd84a80670000fa2840220a243c000003ed2c4c4eaeffe22a004a85670000e2700c223c000100012c7800044eaefd544a80670000cc26402205240b760c2c4c4eaeffd60c800000000c660000b40c93464f524d660000aa0cab494c424d00086600009e282b000450840c840000000c6300008e0c8400200000620000842004223c000100012c7800044eaefd544a806700006e2e0020402093216b00040004216b00080008224b2c7800044eaefd4e7c0026462205204741e8000c2408260404830000000c2c4c4eaeffd6b083660000302c4c22054eaeffdc7a00224c2c7800044eaefe627c002846224a2c7800044eaefd4e7c00244626477e00600000664a856700000c2c4c22054eaeffdc7a00200b4a8067000010224b2c7800044eaefd4e7c0026464a876700000e22472c7800044eaefd4e7e00200c4a8067000010224c2c7800044eaefe627c002846200a4a8067000292224a2c7800044eaefd4e6000028441eb000c224bd3c47c007a007e00244628462009240890820c800000000865000096261024280004220252810281fffffffe508190816500021e4de800080c83424d48446700001a0c83434d4150670000500c83424f44596700004e600000520c8200000014650001ee0c560140660001e60c6e00c80002660001dc0c2e00080008660001d20c2e00000009660001c80c2e0001000a660001be7c0160000012244e2a026000000a284e2e0260000002d1c16000ff5e4a866700019c200a4a8067000194200c4a806700018c0c8500000300650001824a876700017c206d01c820084a8067000170225020094a80670001662c680008200e4a806700015a41e9002c28087a007200121a2c01e18982862c01484182867400141a2c02e18a84862c02484284867600161a2c03e18b86862c0348438686204420054eaefcac52450c4501006600ffc0280b206d01c82c680020200e4a806700010c202e00084a8067000008225660000006226e000420094a80670000f02651200b4a80670000e60c530028660000de0c6b00c80002650000d40c2b00080005650000ca244cd5c77a007c0041eb00087607225820094a80670000b2d3c67228200a240c90824a80670000a26b00009e7000101c488048c04a806a0000420c80ffffff806700ffda44402e00528774003401948765000076240a2e0c94874a826700006a6b0000667400141c12c2534151c8fffa4a416600ffa86000002a240a2e0c94872e0052879487650000407400340194876500003612dc534151c8fffa4a416600ff7c51cbff6a06860000002852450c4500c86600ff546000001e224b2c7800044eaefd4e6000002022442c7800044eaefd4e6000001222442c7800044eaefd4e76016000000476004cdf7ff774004e75646f732e6c69627261727900'''

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    return w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==1108
    assert bytes.fromhex('4eaefe80') not in routine  # WaitPort forbidden
    assert bytes.fromhex('4eaefec2') not in routine  # Exec Wait forbidden

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga iff load',13,'2')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    # Do not modify the validated M4b code. Append only dispatcher + M5 routine.
    code=base.code+b'GetP'+routine
    assert code[:len(base.code)]==base.code

    jumps=list(base.jumps)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,77,0]
    jumps[12]+=2
    jumps[13]=len(routine)//2
    jumps.append(0)
    assert jumps==[185,2,8,8,48,167,193,75,108,15,141,74,79,554,0]

    title=b'AMOSPro AGA M5 R2 IFF ByteRun1 0.2.0\0$VER: AMOSPro_AGA 0.2.0\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert len(out)==3696
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated test target',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
