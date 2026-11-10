#!/usr/bin/env python3
"""M5.2 R2 0.4.3 - indexed ILBM 320x200/256, 3..8 planes.

Fixes R1 regression:
- R1 reused A5 for BMHD metadata, but A5 is the AMOS base used to reach
  extension state at +$1C8. This made Aga Iff Load return 0 even on Clown.
- R2 NEVER modifies A5.
- BMHD height/depth are validated immediately against the already-open screen.
- Later BODY loops use the validated screen state for height/depth.
- Clown 320x200x8 keeps the original R3R1 validation/loop path.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.2_PICINFO.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.3_M52R2.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='32e84b42f2187440bb4a6c1f34523c8d1bd1bb61080f0f1de658f7b63f68f9ac'
OUT_SHA='e5fcb918620d4d7a247120468e22b84bce360b9da49c432a36414ac0bda69bc7'

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

def insert_fix(buf,pos,payload):
    rs=refs(buf); delta=len(payload)
    buf[pos:pos]=payload
    for p,target in rs:
        np=p+(delta if p>=pos else 0)
        nt=target+(delta if target>=pos else 0)
        struct.pack_into('>h',buf,np+2,nt-(np+2))
        assert np+2+s16(buf,np+2)==nt

def branch_target(buf,op):
    return op+2+s16(buf,op+2)

def bcc(op,ext,target):
    return w(op)+struct.pack('>h',target-ext)

def patch_loader(loader):
    rt=bytearray(loader)
    assert len(rt)==1112

    # Height 256 skips legacy exact-200 check. 200 follows legacy path.
    p=find_unique(rt,bytes.fromhex('0c6e00c800026600'))
    insert_fix(rt,p,bytes.fromhex('0c6e010000026700000c'))

    # Depth 8 follows legacy exact-8 check. Depth 3..7 skips that one check.
    p=find_unique(rt,bytes.fromhex('0c2e000800086600'))
    fail=branch_target(rt,p+6); delta=34; nf=fail+delta
    block=(bytes.fromhex('0c2e00080008') + bcc(0x6700,p+8,p+delta)
           + bytes.fromhex('0c2e00030008') + bcc(0x6500,p+18,nf)
           + bytes.fromhex('0c2e00070008') + bcc(0x6200,p+28,nf)
           + bcc(0x6000,p+32,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Validate BMHD height/depth against current extension screen state.
    cp=find_unique(rt,bytes.fromhex('0c2e0001000a6600'))
    pos=cp+10
    fail=branch_target(rt,cp+6); delta=30
    nf=fail+(delta if fail>=pos else 0)
    block=(bytes.fromhex('206d01c8302e0002b0680010')
           + bcc(0x6600,pos+14,nf)
           + bytes.fromhex('7000102e0008b028001c')
           + bcc(0x6600,pos+28,nf))
    assert len(block)==delta
    insert_fix(rt,pos,block)

    # CMAP: 768 bytes follows legacy path; 24..767 uses alternate valid path.
    p=find_unique(rt,bytes.fromhex('0c85000003006500'))
    fail=branch_target(rt,p+6); delta=28; nf=fail+delta
    block=(bytes.fromhex('0c8500000300') + bcc(0x6700,p+8,p+delta)
           + bcc(0x6200,p+12,nf)
           + bytes.fromhex('0c8500000018') + bcc(0x6500,p+22,nf)
           + bcc(0x6000,p+26,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Palette: preserve BODY size D7, use current screen color count.
    p=find_unique(rt,bytes.fromhex('41e9002c28087a00'))
    insert_fix(rt,p+6,bytes.fromhex('2f07206d01c82e280014'))

    p=find_unique(rt,bytes.fromhex('52450c4501006600'))
    insert_fix(rt,p+2,bytes.fromhex('ba476700000a'))

    # Restore BODY size just after validated R3R1 WaitTOF.
    p=find_unique(rt,bytes.fromhex('4eaefef2280b'))
    insert_fix(rt,p+4,bytes.fromhex('2e1f'))

    # Bitmap rows: state=200 follows legacy; state=256 validates Rows dynamically.
    p=find_unique(rt,bytes.fromhex('0c6b00c800026500'))
    fail=branch_target(rt,p+6); delta=36; nf=fail+delta
    block=(bytes.fromhex('206d01c8302800100c4000c8')
           + bcc(0x6700,p+14,p+delta)
           + bytes.fromhex('0c400100') + bcc(0x6600,p+22,nf)
           + bytes.fromhex('b06b0002') + bcc(0x6600,p+30,nf)
           + bcc(0x6000,p+34,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Bitmap depth: state=8 follows legacy; state=3..7 must equal Bitmap.Depth.
    p=find_unique(rt,bytes.fromhex('0c2b000800056500'))
    fail=branch_target(rt,p+6); delta=46; nf=fail+delta
    block=(bytes.fromhex('206d01c870001028001c0c000008')
           + bcc(0x6700,p+16,p+delta)
           + bytes.fromhex('0c000003') + bcc(0x6500,p+24,nf)
           + bytes.fromhex('0c000007') + bcc(0x6200,p+32,nf)
           + bytes.fromhex('b02b0005') + bcc(0x6600,p+40,nf)
           + bcc(0x6000,p+44,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Plane loop: depth 8 keeps original MOVEQ #7; lower depths use state-1.
    p=find_unique(rt,bytes.fromhex('760722582009'))
    delta=28
    block=(bytes.fromhex('206d01c870001028001c0c000008')
           + bcc(0x6700,p+16,p+delta)
           + bytes.fromhex('760016005343')
           + bcc(0x6000,p+26,p+delta+2))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Row loop: height 200 keeps legacy compare; otherwise compare to state height.
    p=find_unique(rt,bytes.fromhex('52450c4500c86600'))
    cp=p+2
    old_branch=cp+4
    row_loop=branch_target(rt,old_branch)
    delta=26
    new_row=row_loop+(delta if row_loop>=cp else 0)
    block=(bytes.fromhex('206d01c8302800100c4000c8')
           + bcc(0x6700,cp+14,cp+delta)
           + bytes.fromhex('ba40') + bcc(0x6600,cp+20,new_row)
           + bcc(0x6000,cp+24,cp+delta+8))
    assert len(block)==delta
    insert_fix(rt,cp,block)

    assert len(rt)==1368
    assert bytes.fromhex('4480') in rt       # ByteRun1 NEG.L
    assert bytes.fromhex('4eaefef2') in rt   # R3R1 WaitTOF
    assert bytes.fromhex('4eaefe80') not in rt
    assert bytes.fromhex('4eaefec2') not in rt
    return bytes(rt)

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

    assert base.jumps[13:16]==(558,379,0)
    assert seg[13][-4:]==b'GetP'
    seg[13]=patch_loader(seg[13][:-4])+b'GetP'

    # Every non-loader command remains byte-for-byte identical.
    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,686,379,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5.2 R2 multi320 0.4.3\0$VER: AMOSPro_AGA 0.4.3\0'
    if len(title)&1: title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3: payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)['issues']==[]
    assert parsed.tokens==base.tokens
    assert len(out)==4748
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
