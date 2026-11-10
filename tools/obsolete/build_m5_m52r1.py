#!/usr/bin/env python3
"""M5.2 R1 0.4.2 - indexed ILBM 320x200/256, 3..8 planes.

Base: M5.1 PicInfo 0.3.2.

Design constraints:
- preserve all existing R3R1/PicInfo command segments except Aga Iff Load;
- preserve every original Aga Iff Load byte in order and add only new paths;
- Clown 320x200x8 continues through the original 200/8 validation and loops;
- 320x256 and depths 3..7 use inserted alternate paths;
- palette loop stops at the actual screen color count;
- destination screen is expected to have been opened from Aga Pic Info;
- no EHB/HAM support in this milestone;
- ByteRun1 core and R3R1 WaitTOF stay unchanged.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.2_PICINFO.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.2_M52R1.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='32e84b42f2187440bb4a6c1f34523c8d1bd1bb61080f0f1de658f7b63f68f9ac'
OUT_SHA='5956323948e2bc341c8e7db896953a8ac80844acf70c122a0cacea1ba54c15b9'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)
def s16(buf,p): return struct.unpack_from('>h',buf,p)[0]

def find_unique(buf, pat):
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
        if 0x6000 <= (ins & 0xff00) <= 0x6f00 and (ins & 0xff)==0:
            yes=True
        elif (ins & 0xf0f8)==0x50c8:
            yes=True
        elif (ins & 0xf1ff)==0x41fa:
            yes=True
        if yes:
            target=p+2+s16(buf,p+2)
            if 0 <= target <= len(buf) and not (target&1):
                out.append((p,target))
    return out

def insert_fix(buf,pos,payload):
    rs=refs(buf)
    delta=len(payload)
    buf[pos:pos]=payload
    for p,target in rs:
        np=p+(delta if p>=pos else 0)
        nt=target+(delta if target>=pos else 0)
        struct.pack_into('>h',buf,np+2,nt-(np+2))
        assert np+2+s16(buf,np+2)==nt

def branch_target(buf,op_pos):
    return op_pos+2+s16(buf,op_pos+2)

def bcc(op,ext_pos,target):
    return w(op)+struct.pack('>h',target-ext_pos)

def patch_loader(loader):
    rt=bytearray(loader)
    assert len(rt)==1112

    # A5 is unused by the validated loader: reserve it for BMHD payload.
    p=find_unique(rt,bytes.fromhex('2446264628462043'))
    insert_fix(rt,p+6,bytes.fromhex('2a46')) # movea.l d6,a5 -> NULL

    # Height 256 is accepted before the original exact-200 test.
    p=find_unique(rt,bytes.fromhex('0c6e00c800026600'))
    insert_fix(rt,p,bytes.fromhex('0c6e010000026700000c'))

    # Depth 3..8. Valid values skip the original exact-8 test.
    p=find_unique(rt,bytes.fromhex('0c2e000800086600'))
    fail=branch_target(rt,p+6)
    delta=24
    nf=fail+delta
    block=(bytes.fromhex('0c2e00030008') + bcc(0x6500,p+8,nf)
           + bytes.fromhex('0c2e00080008') + bcc(0x6200,p+18,nf)
           + bcc(0x6000,p+22,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Keep original D6 BMHD-found flag and additionally retain BMHD payload in A5.
    p=find_unique(rt,bytes.fromhex('7c0160000012'))
    insert_fix(rt,p,bytes.fromhex('2a4e')) # movea.l a6,a5

    # CMAP 8..256 colors => 24..768 bytes.
    p=find_unique(rt,bytes.fromhex('0c85000003006500'))
    fail=branch_target(rt,p+6)
    delta=24
    nf=fail+delta
    block=(bytes.fromhex('0c8500000018') + bcc(0x6500,p+8,nf)
           + bytes.fromhex('0c8500000300') + bcc(0x6200,p+18,nf)
           + bcc(0x6000,p+22,p+delta+10))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Palette count comes from the already validated/opened screen.
    p=find_unique(rt,bytes.fromhex('41e9002c28087a00'))
    insert_fix(rt,p+6,bytes.fromhex('2f07206d01c82e280014')) # save BODY size; D7=colors

    # Stop palette at D5==D7; otherwise keep original 256-color loop.
    p=find_unique(rt,bytes.fromhex('52450c4501006600'))
    insert_fix(rt,p+2,bytes.fromhex('ba476700000a'))

    # Restore BODY size immediately after the validated R3R1 WaitTOF.
    p=find_unique(rt,bytes.fromhex('4eaefef2280b'))
    insert_fix(rt,p+4,bytes.fromhex('2e1f'))

    # Bitmap rows: 256 path checks 256; 200 keeps original validation.
    p=find_unique(rt,bytes.fromhex('0c6b00c800026500'))
    fail=branch_target(rt,p+6)
    delta=24
    nf=fail+delta
    block=(bytes.fromhex('0c6d01000002') + bcc(0x6600,p+8,p+delta)
           + bytes.fromhex('0c6b01000002') + bcc(0x6700,p+18,p+delta+10)
           + bcc(0x6000,p+22,nf))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Bitmap depth: non-8 compares destination depth with BMHD.
    p=find_unique(rt,bytes.fromhex('0c2b000800056500'))
    fail=branch_target(rt,p+6)
    delta=28
    nf=fail+delta
    block=(bytes.fromhex('0c2d00080008') + bcc(0x6700,p+8,p+delta)
           + bytes.fromhex('7000102b0005b02d0008')
           + bcc(0x6700,p+22,p+delta+10)
           + bcc(0x6000,p+26,nf))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Plane loop: depth 8 keeps original MOVEQ #7; lower depths use BMHD-1.
    p=find_unique(rt,bytes.fromhex('760722582009'))
    delta=22
    block=(bytes.fromhex('0c2d00080008') + bcc(0x6700,p+8,p+delta)
           + bytes.fromhex('7600162d00085343')
           + bcc(0x6000,p+20,p+delta+2))
    assert len(block)==delta
    insert_fix(rt,p,block)

    # Row loop: 200 keeps legacy compare; 256 uses an alternate limit.
    p=find_unique(rt,bytes.fromhex('52450c4500c86600'))
    cp=p+2
    row_loop=branch_target(rt,cp+4)
    delta=22
    new_row=row_loop+(delta if row_loop>=cp else 0)
    block=(bytes.fromhex('0c6d01000002') + bcc(0x6600,cp+8,cp+delta)
           + bytes.fromhex('0c450100') + bcc(0x6600,cp+16,new_row)
           + bcc(0x6000,cp+20,cp+delta+8))
    assert len(block)==delta
    insert_fix(rt,cp,block)

    assert len(rt)==1288
    assert bytes.fromhex('4480') in rt       # validated NEG.L ByteRun1 fix
    assert bytes.fromhex('4eaefef2') in rt   # validated R3R1 WaitTOF
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
    old_loader=seg[13][:-4]
    seg[13]=patch_loader(old_loader)+b'GetP'

    # PicInfo and every non-loader command remain byte-for-byte identical.
    for i in range(len(seg)):
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,646,379,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5.2 R1 multi320 0.4.2\0$VER: AMOSPro_AGA 0.4.2\0'
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
    assert len(out)==4668
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
