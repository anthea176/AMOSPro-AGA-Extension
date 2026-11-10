#!/usr/bin/env python3
"""M5.2 R3 0.4.4 - fixed-layout indexed 320px loader.

Base: M5.1 PicInfo 0.3.2.

Key rule:
- Aga Iff Load segment stays EXACTLY 1112 bytes, identical in size to the
  validated PicInfo/R3R1 layout. Therefore Aga Pic Info and every later entry
  keep the same code address as in PicInfo 0.3.2.

Changes inside Aga Iff Load only:
- BMHD height: accept >=200 (M5.2 tested cases are 200/256);
- BMHD depth: accept >=3;
- CMAP: minimum 24 bytes (8 colours);
- palette loop count = CMAP_size/3;
- BODY size D7 preserved around palette work;
- plane loop count = destination BitMap.Depth;
- row loop count = destination BitMap.Rows;
- fixed destination 200/8 checks removed because the screen is opened from
  Aga Pic Info before loading;
- validated ByteRun1 NEG.L and R3R1 WaitTOF are retained.

No EHB/HAM/640+ support in this milestone.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.3.2_PICINFO.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.4_M52R3.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='32e84b42f2187440bb4a6c1f34523c8d1bd1bb61080f0f1de658f7b63f68f9ac'
OUT_SHA='3b6d60dc10812db12b8477bc2b5c87013b075681ebcbb5bc6aa5cce6963bc230'

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
        if target>=end:
            nt=target+delta
        elif target==end:
            nt=end+delta
        else:
            nt=target
        struct.pack_into('>h',buf,np+2,nt-(np+2))
        assert np+2+s16(buf,np+2)==nt

def patch_loader(loader):
    rt=bytearray(loader)
    assert len(rt)==1112

    # Height: known M5.2 cases are 200 or 256. CMP #200 + BCS rejects <200.
    p=find_unique(rt,bytes.fromhex('0c6e00c800026600'))
    rt[p+6]=0x65

    # Depth: require >=3. Destination BitMap.Depth controls actual decode planes.
    p=find_unique(rt,bytes.fromhex('0c2e000800086600'))
    rt[p+3]=0x03
    rt[p+6]=0x65

    # CMAP minimum = 8 colours = 24 bytes.
    p=find_unique(rt,bytes.fromhex('0c85000003006500'))
    rt[p+2:p+6]=bytes.fromhex('00000018')

    # Palette count = CMAP_size / 3. Preserve BODY size D7 on stack.
    p=find_unique(rt,bytes.fromhex('41e9002c28087a00'))
    splice_fix(rt,p+6,0,bytes.fromhex('2f072e0586fc0003'))

    # Replace fixed CMP.W #256,D5 with CMP.W D7,D5.
    p=find_unique(rt,bytes.fromhex('52450c4501006600'))
    splice_fix(rt,p+2,4,bytes.fromhex('ba47'))

    # Restore BODY size just after the validated R3R1 WaitTOF.
    p=find_unique(rt,bytes.fromhex('4eaefef2280b'))
    splice_fix(rt,p+4,0,bytes.fromhex('2e1f'))

    # Destination dimensions are those already opened from PicInfo.
    p=find_unique(rt,bytes.fromhex('0c6b00c80002'))
    splice_fix(rt,p,10,b'')
    p=find_unique(rt,bytes.fromhex('0c2b00080005'))
    splice_fix(rt,p,10,b'')

    # Plane count = BitMap.Depth - 1.
    p=find_unique(rt,bytes.fromhex('760722582009'))
    splice_fix(rt,p,2,bytes.fromhex('7600162b00055343'))

    # Row count = BitMap.Rows.
    p=find_unique(rt,bytes.fromhex('52450c4500c86600'))
    splice_fix(rt,p+2,4,bytes.fromhex('ba6b0002'))

    # Keep public code layout unchanged. Padding is after the NUL-terminated
    # dos.library string and is never executed or addressed.
    assert len(rt)<=1112
    dos=bytes.fromhex('646f732e6c69627261727900')
    pos=rt.find(dos)
    assert pos>=0 and pos+len(dos)==len(rt)
    rt += b'\0'*(1112-len(rt))

    assert len(rt)==1112
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

    old_loader=seg[13][:-4]
    seg[13]=patch_loader(old_loader)+b'GetP'

    # Every segment keeps the exact same size and every non-loader segment
    # remains byte-for-byte identical.
    for i in range(len(seg)):
        assert len(seg[i])==len(original[i])
        if i!=13:
            assert seg[i]==original[i]

    jumps=[len(x)//2 for x in seg]
    assert jumps==list(base.jumps)
    code=b''.join(seg)

    title=b'AMOSPro AGA M5.2 R3 fixed-layout 0.4.4\0$VER: AMOSPro_AGA 0.4.4\0'
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
    assert parsed.jumps==base.jumps
    assert len(out)==4496
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
