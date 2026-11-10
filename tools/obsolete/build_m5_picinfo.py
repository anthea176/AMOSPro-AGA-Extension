#!/usr/bin/env python3
"""M5.1 PicInfo 0.3.2 — inspect ILBM metadata without display or BODY decode.

Built directly on runtime-validated M5-R3R1 0.3.1.

Public API:
    value=Aga Pic Info("image.iff",field)

Fields:
    0 width
    1 height
    2 bitplanes
    3 CMAP colour count
    4 compression
    5 CAMG/ModeID (0 if absent)
   -1 error / invalid field / malformed file

R3R1 runtime routines remain byte-for-byte unchanged. The only addition to
Aga Iff Load's AP20 segment is the four-byte GetP dispatcher required by the
new parameterized entry that follows it.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.1_R3R1.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.2_PICINFO.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
BASE_SHA='a1b24aa0f83be86858b2ba495e94259aac211208ff5a8b0d6825a3427a09cb2e'
OUT_SHA='32e84b42f2187440bb4a6c1f34523c8d1bd1bb61080f0f1de658f7b63f68f9ac'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

class A:
    def __init__(self):
        self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h):
        self.b += bytes.fromhex(h.replace(' ',''))
    def label(self,n):
        assert n not in self.labels
        self.labels[n]=len(self.b)
    def br(self,op,label):
        p=len(self.b); self.b += w(op)+b'\0\0'; self.fix.append((p+2,label))
    def dbra(self,reg,label):
        p=len(self.b); self.b += w(0x51c8+reg)+b'\0\0'; self.fix.append((p+2,label))
    def leapc(self,an,label):
        p=len(self.b); self.b += w(0x41fa+(an<<9))+b'\0\0'; self.fix.append((p+2,label))
    def out(self):
        for ext,label in self.fix:
            disp=self.labels[label]-ext
            assert -32768 <= disp <= 32767
            struct.pack_into('>h',self.b,ext,disp)
        return bytes(self.b)

def token_function(name,index,params):
    n=bytearray(name.encode('ascii')); n[-1]|=0x80
    out=w(1)+w(index)+bytes(n)+b'0'+params.encode('ascii')+b'\xff'
    if len(out)&1: out+=b'\0'
    return out

def pic_info_routine():
    a=A()
    # Two-parameter function ABI: last argument in D3, previous at (A3)+.
    a.e('48e7effe')
    a.e('2a43')                         # A5=field
    a.e('261b')                         # D3=AMOS string pointer
    a.e('7c007e007a007800244626462846') # resources/scratch = 0
    a.e('200d0c8000000005')             # field 0..5
    a.br(0x6200,'invalid')

    # Validated R3R1 AMOS-string -> C-string path.
    a.e('2043780038184a44')
    a.br(0x6700,'invalid')
    a.e('20045280223c000100012c7800044eaefd544a80')
    a.br(0x6700,'invalid')
    a.e('2440')
    a.e('204341e80002224a5344')
    a.label('copy_name')
    a.e('12d8')
    a.dbra(4,'copy_name')
    a.e('12bc0000')

    # dos.library + Open(MODE_OLDFILE).
    a.leapc(1,'dosname')
    a.e('70002c7800044eaefdd828404a80')
    a.br(0x6700,'invalid')
    a.e('220a243c000003ed2c4c4eaeffe22a004a85')
    a.br(0x6700,'invalid')

    # Read and validate FORM/ILBM header.
    a.e('700c223c000100012c7800044eaefd544a80')
    a.br(0x6700,'invalid')
    a.e('2640')
    a.e('2205240b760c2c4c4eaeffd6')
    a.e('0c800000000c')
    a.br(0x6600,'invalid')
    a.e('20130c80464f524d')
    a.br(0x6600,'invalid')
    a.e('202b00080c80494c424d')
    a.br(0x6600,'invalid')

    # Read complete FORM into RAM, using the validated loader I/O pattern.
    a.e('282b00045084')
    a.e('0c840000000c')
    a.br(0x6300,'invalid')
    a.e('0c8400200000')
    a.br(0x6200,'invalid')
    a.e('2004223c000100012c7800044eaefd544a80')
    a.br(0x6700,'invalid')
    a.e('2e00')
    a.e('20402093216b00040004216b00080008')
    a.e('2205204741e8000c2408260404830000000c2c4c4eaeffd6b083')
    a.br(0x6600,'invalid')

    # Free the 12-byte temporary header, full FORM becomes A3.
    a.e('224b2c7800044eaefd4e7c00264626477e00')

    # Bounded IFF chunk scanner. Unknown chunks (including BODY) are skipped.
    a.e('41eb000c224bd3c4')
    a.label('scan')
    a.e('2009240890820c8000000008')
    a.br(0x6500,'scan_done')
    a.e('261024280004220252810281fffffffe50819081')
    a.br(0x6500,'invalid')
    a.e('4de80008')

    a.e('0c83424d4844')
    a.br(0x6700,'bmhd')
    a.e('0c83434d4150')
    a.br(0x6700,'cmap')
    a.e('0c8343414d47')
    a.br(0x6700,'camg')
    a.br(0x6000,'advance')

    a.label('bmhd')
    a.e('0c8200000014')
    a.br(0x6500,'invalid')
    a.e('200d4a80')
    a.br(0x6700,'ret_width')
    a.e('0c8000000001')
    a.br(0x6700,'ret_height')
    a.e('0c8000000002')
    a.br(0x6700,'ret_depth')
    a.e('0c8000000004')
    a.br(0x6700,'ret_compression')
    a.br(0x6000,'advance')

    a.label('ret_width')
    a.e('76003616')
    a.br(0x6000,'success')
    a.label('ret_height')
    a.e('7600362e0002')
    a.br(0x6000,'success')
    a.label('ret_depth')
    a.e('7600162e0008')
    a.br(0x6000,'success')
    a.label('ret_compression')
    a.e('7600162e000a')
    a.br(0x6000,'success')

    a.label('cmap')
    a.e('200d0c8000000003')
    a.br(0x6600,'advance')
    a.e('4a82')
    a.br(0x6700,'invalid')
    a.e('0c8200000300')
    a.br(0x6200,'invalid')
    a.e('260286fc0003200348404a40')
    a.br(0x6600,'invalid')
    a.e('02830000ffff')
    a.br(0x6000,'success')

    a.label('camg')
    a.e('200d0c8000000005')
    a.br(0x6600,'advance')
    a.e('0c8200000004')
    a.br(0x6500,'invalid')
    a.e('2616')
    a.br(0x6000,'success')

    a.label('advance')
    a.e('2228000452810281fffffffe5081d1c1')
    a.br(0x6000,'scan')

    a.label('scan_done')
    a.e('200d0c8000000005')
    a.br(0x6600,'invalid')
    a.e('7600')                         # CAMG absent -> 0
    a.br(0x6000,'success')

    a.label('invalid')
    a.e('76ff')                         # -1
    a.br(0x6000,'cleanup')
    a.label('success')

    # One cleanup path. Preserve D3 result over DOS/Exec calls.
    a.label('cleanup')
    a.e('2f03')
    a.e('4a85')
    a.br(0x6700,'free_a3')
    a.e('200c4a80')
    a.br(0x6700,'free_a3')
    a.e('2c4c22054eaeffdc7a00')

    a.label('free_a3')
    a.e('200b4a80')
    a.br(0x6700,'free_d7')
    a.e('224b2c7800044eaefd4e7c002646')

    a.label('free_d7')
    a.e('20074a80')
    a.br(0x6700,'close_dos')
    a.e('22472c7800044eaefd4e7e00')

    a.label('close_dos')
    a.e('200c4a80')
    a.br(0x6700,'free_cstr')
    a.e('224c2c7800044eaefe627c002846')

    a.label('free_cstr')
    a.e('200a4a80')
    a.br(0x6700,'done')
    a.e('224a2c7800044eaefd4e7c002446')

    a.label('done')
    a.e('261f4cdf7ff774004e75')

    a.label('dosname')
    a.e('646f732e6c69627261727900')
    if len(a.b)&1: a.e('00')
    return a.out()

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n]); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    routine=pic_info_routine()
    assert len(routine)==758
    assert b'BMHD' in routine and b'CMAP' in routine and b'CAMG' in routine
    assert b'BODY' not in routine
    assert bytes.fromhex('246d01c8') not in routine # no extension screen state
    assert bytes.fromhex('4eaefe80') not in routine # no WaitPort
    assert bytes.fromhex('4eaefec2') not in routine # no Exec Wait

    # Existing R3R1 loader bytes remain exact; only next-entry GetP is appended.
    seg[13]=seg[13]+b'GetP'
    assert seg[13][:-4]==original[13]
    seg[14]=routine
    seg.append(b'')

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,0]
    code=b''.join(seg)

    tok=bytearray(base.tokens[:-6])
    tok+=token_function('aga pic info',14,'2,0')
    tok+=b'\0'*6
    if len(tok)&1: tok+=b'\0'

    title=b'AMOSPro AGA M5 PicInfo 0.3.2\0$VER: AMOSPro_AGA 0.3.2\0'
    if len(title)&1: title+=b'\0'

    header=l(len(jumps)*2)+l(len(tok))+l(len(code))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(x) for x in jumps)+tok+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'
    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    pic=[x for x in audit['tokens'] if x['name']=='aga pic info']
    assert len(pic)==1 and pic[0]['function']==14 and pic[0]['signature']=='02,0'
    checks=[x for x in audit['parameter_checks'] if x['name']=='aga pic info']
    assert len(checks)==1 and checks[0]['getp'] is True

    assert len(out)==4488
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
