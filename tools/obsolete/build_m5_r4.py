#!/usr/bin/env python3
"""M5 R4 - multi-format 320-pixel ByteRun1 ILBM loader.

Built directly on runtime-validated M5-R3R1 0.3.1. Only command segment 13
(Aga Iff Load) changes. R3R1 screen/FullPalette/Swap/Close behaviour stays
byte-for-byte unchanged.

Scope: width 320; height 200/256; depth 3..8; mask 0; ByteRun1;
CMAP 8..256 colours; clear destination planes above source depth.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.1_R3R1.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.0_R4.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='a1b24aa0f83be86858b2ba495e94259aac211208ff5a8b0d6825a3427a09cb2e'
OUT_SHA='b6fca88d9ab4ce8da0addb0130962cd607705b2b50d882e9d5278671ec48514d'

ROUTINE_HEX=(
    '48e7effe7c007e007a0078002446264628462043780038184a446700013c20045280223c000100012c7800044eaefd544a80670001242440204341e8'
    '0002224a534412d851ccfffc12bc000043fa049470002c7800044eaefdd84a80670000fa2840220a243c000003ed2c4c4eaeffe22a004a85670000e2'
    '700c223c000100012c7800044eaefd544a80670000cc26402205240b760c2c4c4eaeffd60c800000000c660000b40c93464f524d660000aa0cab494c'
    '424d00086600009e282b000450840c840000000c6300008e0c8400200000620000842004223c000100012c7800044eaefd544a806700006e2e002040'
    '2093216b00040004216b00080008224b2c7800044eaefd4e7c0026462205204741e8000c2408260404830000000c2c4c4eaeffd6b083660000302c4c'
    '22054eaeffdc7a00224c2c7800044eaefe627c002846224a2c7800044eaefd4e7c00244626477e00600000664a856700000c2c4c22054eaeffdc7a00'
    '200b4a8067000010224b2c7800044eaefd4e7c0026464a876700000e22472c7800044eaefd4e7e00200c4a8067000010224c2c7800044eaefe627c00'
    '2846200a4a806700032c224a2c7800044eaefd4e6000031e41eb000c224bd3c47c007a007e00244628462009240890820c8000000008650000b22610'
    '24280004220252810281fffffffe50819081650002b84de800080c83424d48446700001a0c83434d41506700006c0c83424f44596700006a6000006e'
    '0c8200000014650002880c560140660002807c003c2e00020c4600c86700000a0c4601006600026a7000102e00080c0000036500025c0c0000086200'
    '02540c2e000000096600024a0c2e0001000a66000240e148e3488c4060000012244e2a026000000a284e2e0260000002d1c16000ff424a866700021a'
    '200a4a8067000212200c4a806700020a0c8500000018650002000c8500000300620001f68afc0003200548404a40660001e848454a87670001e0206d'
    '01c820084a80670001d4225020094a80670001ca2c680008200e4a80670001be41e97200121a2001e18982802001484182807400141a2002e18a8480'
    '2002484284807600161a2003e18b86802003484386802044700030054eaefcac524520054840ba406600ffbc4eaefef2280b206d01c82c680020200e'
    '4a806700016e202e00084a8067000008225660000006226e000420094a80670001522651200b4a80670001480c530028660001407000302b00022206'
    '024101ffb0416500012e0c2b0008000565000124244cd5c72a06484541eb000826054843e04be24b0c4300086700003830035340588851c8fffc7407'
    '94432e054847024701ff3207e74fd241de415347225820094a80670000de3007429951c8fffc51caffec7c0041eb000826054843e04be24b53432258'
    '20094a80670000b8d3c67228200a240c90824a80670000a86b0000a47000101c488048c04a806a0000420c80ffffff806700ffda44802e0052877400'
    '340194876500007c240a2e0c94874a82670000706b00006c7400141c12c2534151c8fffa4a416600ffa86000002a240a2e0c94872e00528794876500'
    '00467400340194876500003c12dc534151c8fffa4a416600ff7c51cbff6a068600000028524520054840024001ffba406600ff466000001e224b2c78'
    '00044eaefd4e6000002022442c7800044eaefd4e6000001222442c7800044eaefd4e76016000000476004cdf7ff774004e75646f732e6c6962726172'
    '7900'
)

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    routine=bytes.fromhex(ROUTINE_HEX)
    assert len(routine)==1262
    assert bytes.fromhex('0c560140') in routine                 # width 320
    assert bytes.fromhex('0c4600c8') in routine                 # height 200
    assert bytes.fromhex('0c460100') in routine                 # height 256
    assert bytes.fromhex('0c000003') in routine                 # depth >= 3
    assert bytes.fromhex('0c000008') in routine                 # depth <= 8
    assert bytes.fromhex('8afc0003') in routine                 # CMAP bytes / 3
    assert bytes.fromhex('4299') in routine                     # clear unused planes
    assert bytes.fromhex('4480') in routine                     # NEG.L ByteRun1 fix
    assert bytes.fromhex('4eaefef2') in routine                 # R3R1 WaitTOF
    assert bytes.fromhex('4eaefe80') not in routine             # no WaitPort
    assert bytes.fromhex('4eaefec2') not in routine             # no Exec Wait

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    original=[bytes(x) for x in seg]
    seg[13]=routine
    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,631,0]
    code=b''.join(seg)
    title=b'AMOSPro AGA M5 R4 multi-format 320 0.4.0\0$VER: AMOSPro_AGA 0.4.0\0'
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
