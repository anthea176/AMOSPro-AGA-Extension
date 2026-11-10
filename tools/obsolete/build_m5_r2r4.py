#!/usr/bin/env python3
"""M5 R2R4 - open the AGA screen with SA_FullPalette=TRUE.

Built on the runtime-stable M5-R2R2 candidate.

Why:
- decoded BODY is exact for all 8 planes;
- displayed plane order is exact 0..7;
- logical ColorMap contains the exact 256 IFF colours;
- display mode is normal PAL LORES, no HAM/EHB/DUALPF.

The remaining issue is that the screen was originally opened without
SA_FullPalette, so Intuition/graphics may not build a full AGA palette load
for the ViewPort.

This candidate changes only Aga Screen Open:
- tag-list stack grows from 40 to 52 bytes (50 used + alignment);
- inserts SA_FullPalette ($8000003B), TRUE before TAG_DONE;
- adjusts all PC-relative branches/LEAs crossing the insertion;
- leaves the validated IFF loader, double buffer, swap and close untouched.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect
from build_m5_r2r2 import build as build_r2r2

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.2.15_R2R4.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'
OUT_SHA='2571a944cd1001c1ede89c8cbafa3c02e07acd8ebedc62cc145fedfd66e17430'

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def s16(b,p):
    return struct.unpack_from('>h',b,p)[0]

def patch_open(seg):
    assert seg[-4:]==b'GetP'
    op=bytearray(seg[:-4])

    alloc=bytes.fromhex('4fefffd8')
    restore=bytes.fromhex('4fef0028')
    alloc_pos=op.find(alloc)
    restore_pos=op.find(restore)
    assert (alloc_pos,restore_pos)==(218,272)

    insert_pos=256
    delta=10

    # Record original relative control-flow references.
    refs=[]
    pos=0
    while pos+4<=len(op):
        ins=struct.unpack_from('>H',op,pos)[0]
        kind=None
        if 0x6000 <= (ins & 0xff00) <= 0x6f00 and (ins & 0x00ff)==0:
            kind='branch'
        elif (ins & 0xf0f8)==0x50c8:
            kind='dbcc'
        elif (ins & 0xf1ff)==0x41fa:
            kind='leapc'
        if kind:
            refs.append((kind,pos,pos+2+s16(op,pos+2)))
        pos+=2

    # 52 bytes keeps 4-byte stack alignment; tag list itself uses 50 bytes.
    op[alloc_pos+2:alloc_pos+4]=bytes.fromhex('ffcc')
    op[restore_pos+2:restore_pos+4]=bytes.fromhex('0034')

    # References starting before the insertion and targeting after it grow.
    for _kind,pos,target in refs:
        if pos < insert_pos and target >= insert_pos:
            old=s16(op,pos+2)
            struct.pack_into('>h',op,pos+2,old+delta)

    # SA_FullPalette ($8000003B), TRUE.
    # move.l #$8000003B,(a1)+
    # moveq  #1,d0
    # move.l d0,(a1)+
    add=bytes.fromhex('22fc8000003b700122c0')
    op[insert_pos:insert_pos]=add

    assert op.find(add)==insert_pos
    assert op.find(bytes.fromhex('4fef0034'))==restore_pos+delta

    # Verify every known relative reference still lands on the same logical
    # instruction/data, shifted only when it was after the insertion.
    for kind,pos,target in refs:
        new_pos=pos+delta if pos>=insert_pos else pos
        got=new_pos+2+s16(op,new_pos+2)
        expected=target+delta if target>=insert_pos else target
        assert got==expected,(kind,pos,got,expected)

    out=bytes(op)+b'GetP'
    assert len(out)==396
    return out

def build():
    raw=build_r2r2()
    base=parse(raw)
    assert inspect(base)['issues']==[]

    seg=[]
    p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n])
        p+=2*n
    assert p==len(base.code)

    original=[bytes(x) for x in seg]
    seg[6]=patch_open(seg[6])

    # Only Aga Screen Open changes.
    for i in range(len(seg)):
        if i!=6:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,554,0]
    code=b''.join(seg)

    title=b'AMOSPro AGA M5 R2R4 FullPalette OpenScreen 0.2.15\0$VER: AMOSPro_AGA 0.2.15\0'
    if len(title)&1:
        title+=b'\0'

    off,nt,_,_=base.lengths
    header=l(off)+l(nt)+l(len(code))+l(len(title))+b'\0\0AP20'+b''.join(w(x) for x in jumps)
    payload=bytearray(header+base.tokens+code+title+b'\0\0')
    while len(payload)&3:
        payload+=b'\0'

    count=len(payload)//4
    out=raw[:20]+l(count)+raw[24:28]+l(count)+payload+raw[-4:]
    assert len(out)==3720
    assert hashlib.sha256(out).hexdigest()==OUT_SHA
    assert inspect(parse(out))['issues']==[]
    return out

if __name__=='__main__':
    out=build()
    DEST.write_bytes(out)
    LIVE.write_bytes(out)
    print('Generated',DEST)
    print('Updated',LIVE)
    print('Size',len(out))
    print('SHA256',OUT_SHA)
