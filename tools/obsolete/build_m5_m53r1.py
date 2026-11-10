#!/usr/bin/env python3
"""M5.3 R1 0.5.0 - RAW BODY + bounded parser guards.

Base: runtime-validated M5.2 R4 0.4.5.

Public layout contract:
- all existing public command segments keep their M5.2 sizes;
- Aga Iff Load remains exactly 1112 bytes before its trailing GetP;
- Aga Pic Info therefore keeps the same relative code address;
- one hidden helper segment is appended after PicInfo, with no AMOS token.

M5.3 delta:
- BMHD strict validation: 320 width, height 200/256, depth 3..8,
  masking=0, compression=0 or 1;
- CMAP strict validation: 24..768 bytes and divisible by 3;
- chunk scanner rejects non-zero trailing bytes shorter than a chunk header;
- compression state survives palette loading in D6;
- compression=0 reuses the existing literal-run copy path with a synthetic
  40-byte literal row (control=39);
- ByteRun1 path stays intact, including NEG.L;
- BODY must be consumed exactly;
- destination row offset is recomputed from row index, leaving D6 untouched;
- no WaitPort / Exec Wait is introduced.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_M52R4.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.0_M53R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178'
OUT_SHA='5f9b2d3fb2c40a265b5ae1b7dcc0a22bd448683d3b5d946bc68a8adbdcb54678'

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

def refs(buf):
    out=[]
    for p in range(0,len(buf)-3,2):
        ins=struct.unpack_from('>H',buf,p)[0]
        yes=False
        if 0x6000 <= (ins&0xff00) <= 0x6f00 and (ins&0xff)==0:
            yes=True
        elif (ins&0xf0f8)==0x50c8:
            yes=True
        elif (ins&0xf1ff)==0x41fa:
            yes=True
        if yes:
            target=p+2+s16(buf,p+2)
            if 0 <= target <= len(buf) and not(target&1):
                out.append((p,target))
    return out

def splice_fix(buf,pos,old_len,new_bytes):
    rs=refs(buf)
    end=pos+old_len
    delta=len(new_bytes)-old_len
    for p,target in rs:
        if pos <= p < end:
            continue
        assert not (pos < target < end),(p,target,pos,end)
    buf[pos:end]=new_bytes
    for p,target in rs:
        if pos <= p < end:
            continue
        np=p+(delta if p>=end else 0)
        nt=target+(delta if target>=end else 0)
        struct.pack_into('>h',buf,np+2,nt-(np+2))
        assert np+2+s16(buf,np+2)==nt

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

def helper_segment():
    a=A()

    # D6 result on success = $00010000 | compression.
    a.label('bmhd')
    a.e('7000')
    a.e('0c560140');       a.br(0x6600,'bmhd_fail')
    a.e('0c6e00c80002');   a.br(0x6700,'bmhd_h_ok')
    a.e('0c6e01000002');   a.br(0x6600,'bmhd_fail')
    a.label('bmhd_h_ok')
    a.e('0c2e00030008');   a.br(0x6500,'bmhd_fail')
    a.e('0c2e00080008');   a.br(0x6200,'bmhd_fail')
    a.e('0c2e00000009');   a.br(0x6600,'bmhd_fail')
    a.e('0c2e0001000a');   a.br(0x6200,'bmhd_fail')
    a.e('7c0148461c2e000a70014e75')
    a.label('bmhd_fail')
    a.e('70004e75')

    # D5 = CMAP byte size.
    a.label('cmap')
    a.e('7000')
    a.e('0c8500000018');   a.br(0x6500,'cmap_fail')
    a.e('0c8500000300');   a.br(0x6200,'cmap_fail')
    a.e('220582fc000348414a41'); a.br(0x6600,'cmap_fail')
    a.e('70014e75')
    a.label('cmap_fail')
    a.e('70004e75')

    # Return a ByteRun1 control in D0. RAW uses synthetic literal count 39.
    a.label('control')
    a.e('4a06');           a.br(0x6700,'raw')
    a.e('7000101c4e75')
    a.label('raw')
    a.e('70274e75')

    out=a.out()
    assert len(out)==146
    return out,a.labels

def patch_loader(loader):
    rt=bytearray(loader)
    assert len(rt)==1112

    # Chunk scan: exact end is valid; 1..7 trailing bytes are malformed.
    p=find_unique(rt,bytes.fromhex('2009240890820c80000000086500'))
    scan_done=branch_target(rt,p+12)
    q=find_unique(rt,bytes.fromhex('90816500'))
    fail=branch_target(rt,q+2)
    splice_fix(rt,p+6,0,bytes.fromhex('4a8067000000'))
    struct.pack_into('>h',rt,p+10,(scan_done+6)-(p+10))
    bcs=p+18
    struct.pack_into('>h',rt,bcs+2,(fail+6)-(bcs+2))

    # Replace the monolithic BMHD field checks by a hidden helper gate.
    p=find_unique(rt,bytes.fromhex('0c5601406600'))
    fail=branch_target(rt,p+6)
    found=find_unique(rt,bytes.fromhex('7c0160000012'))
    old_len=(found+2)-p
    delta=10-old_len
    block=bytearray.fromhex('610012344a0067000000')
    struct.pack_into('>h',block,8,(fail+delta)-(p+8))
    splice_fix(rt,p,old_len,block)

    # CMAP validation helper gate.
    p=find_unique(rt,bytes.fromhex('0c85000000186500'))
    fail=branch_target(rt,p+6)
    block=bytearray.fromhex('610012344a0067000000')
    struct.pack_into('>h',block,8,fail-(p+8))
    splice_fix(rt,p,10,block)

    # Palette RGB expansion uses D0 scratch instead of D6, preserving
    # compression state across SetRGB32 / WaitTOF.
    replacements=(
        ('2c01e18982862c0148418286','2001e1898280200148418280'),
        ('2c02e18a84862c0248428486','2002e18a8480200248428480'),
        ('2c03e18b86862c0348438686','2003e18b8680200348438680'),
    )
    for src,dst in replacements:
        p=find_unique(rt,bytes.fromhex(src))
        splice_fix(rt,p,len(bytes.fromhex(src)),bytes.fromhex(dst))

    # Old D6 row-offset reset becomes NOP; D6 now holds compression metadata.
    p=find_unique(rt,bytes.fromhex('7a007c0041eb0008'))
    splice_fix(rt,p+2,2,bytes.fromhex('4e71'))

    # Destination offset = row_index * 40, so D6 remains untouched.
    p=find_unique(rt,bytes.fromhex('d3c67228200a'))
    splice_fix(rt,p,2,bytes.fromhex('2005c0fc0028d3c0'))
    p=find_unique(rt,bytes.fromhex('0686000000285245'))
    splice_fix(rt,p,6,b'')

    # Hidden helper selects RAW synthetic literal or real ByteRun1 control.
    p=find_unique(rt,bytes.fromhex('7000101c488048c0'))
    splice_fix(rt,p,4,bytes.fromhex('61001234'))

    # After the final row, BODY source pointer must equal BODY end exactly.
    p=find_unique(rt,bytes.fromhex('5245ba6b00026600'))
    after_row=p+10
    splice_fix(rt,after_row,0,bytes.fromhex('240a2e0c948766000000'))
    bpr=find_unique(rt,bytes.fromhex('0c5300286600'))
    fail=branch_target(rt,bpr+4)
    struct.pack_into('>h',rt,after_row+8,fail-(after_row+8))

    # Keep public loader segment exactly fixed-size.
    dos=b'dos.library\0'
    p=rt.find(dos)
    assert p>=0
    logical_end=p+len(dos)
    rt=rt[:logical_end]
    assert len(rt)<=1112
    rt += b'\0'*(1112-len(rt))

    assert len(rt)==1112
    assert bytes.fromhex('4480') in rt       # ByteRun1 NEG.L
    assert bytes.fromhex('4eaefef2') in rt   # validated WaitTOF
    assert bytes.fromhex('4eaefe80') not in rt
    assert bytes.fromhex('4eaefec2') not in rt
    return rt

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(bytearray(base.code[p:p+2*n])); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    assert base.jumps[13:16]==(558,379,0)
    assert bytes(seg[13][-4:])==b'GetP'

    seg[13]=patch_loader(seg[13][:-4])+b'GetP'

    # Existing public routines stay same size; every non-loader public routine
    # stays byte-for-byte identical.
    for i in range(15):
        assert len(seg[i])==len(original[i])
        if i!=13:
            assert bytes(seg[i])==original[i]

    helper,labels=helper_segment()
    seg[15]=bytearray(helper)
    seg.append(bytearray())  # new empty sentinel

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,73,0]

    # Patch the 3 BSR.W placeholders from loader to hidden helper labels.
    starts=[]; acc=0
    for x in seg:
        starts.append(acc); acc+=len(x)
    loader=seg[13]
    calls=[]; pos=0
    marker=bytes.fromhex('61001234')
    while True:
        pos=loader.find(marker,pos)
        if pos<0: break
        calls.append(pos); pos+=4
    assert len(calls)==3
    targets=(starts[15]+labels['bmhd'],starts[15]+labels['cmap'],starts[15]+labels['control'])
    for call,target in zip(calls,targets):
        ext=starts[13]+call+2
        disp=target-ext
        assert -32768 <= disp <= 32767
        struct.pack_into('>h',loader,call+2,disp)

    code=b''.join(bytes(x) for x in seg)
    title=b'AMOSPro AGA M5.3 R1 raw+guards 0.5.0\0$VER: AMOSPro_AGA 0.5.0\0'
    if len(title)&1: title+=b'\0'

    # Tokens are unchanged. Jump table gains only the hidden helper + sentinel.
    nt=len(base.tokens)
    off=len(jumps)*2
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    audit=inspect(parsed)
    assert audit['issues']==[]
    assert parsed.tokens==base.tokens
    assert len(out)==4644
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
