#!/usr/bin/env python3
"""M5.2 R5 0.4.6 - fix low-color IFF palette loading with LoadRGB32.

Base: runtime-validated M5.2 R4 0.4.5.

Diagnosis:
- KEKKO BODY decodes correctly: all four back-buffer plane sums exactly match
  the source ILBM BODY.
- Open/Close 16-color cycling is valid.
- graphics.library/SetRGB32 may ignore an "unused" color value.
  That makes it unsuitable as the only mechanism for loading a complete
  low-color IFF palette.

Delta:
- the public Aga Iff Load segment keeps exactly the same size;
- its SetRGB32 call is replaced by a BSR.W to a hidden helper;
- for 256 colors, the helper calls the previously validated SetRGB32 path;
- for lower color counts, the helper uses a one-record LoadRGB32 table;
- all public tokens and all non-loader public routines stay unchanged;
- no BODY/double-buffer/swap logic changes.
"""
from pathlib import Path
import hashlib, struct
from audit_ap20 import parse, inspect

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.5_M52R4.Lib'
DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib'
LIVE=ROOT/'dist/AMOSPro_AGA.Lib'

BASE_SHA='b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178'
OUT_SHA='33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715'

SET_RGB32=bytes.fromhex('4eaefcac')
HELPER=bytes.fromhex(
    '0c8700000100'      # cmpi.l #256,d7
    '6700002c'          # beq.w setrgb32
    '4fefffec'          # lea -20(sp),sp
    '2c00'              # move.l d0,d6
    '008600010000'      # ori.l #$00010000,d6 (count=1, first=d0)
    '224f'              # movea.l sp,a1
    '2286'              # move.l d6,(a1)
    '23410004'          # move.l d1,4(a1)
    '23420008'          # move.l d2,8(a1)
    '2343000c'          # move.l d3,12(a1)
    '42a90010'          # clr.l 16(a1) terminator
    '4eaefc8e'          # jsr -882(a6) LoadRGB32
    '4fef0014'          # lea 20(sp),sp
    '4e75'              # rts
    '4eaefcac'          # setrgb32: jsr -852(a6)
    '4e75'              # rts
)
assert len(HELPER)==58

def w(n): return struct.pack('>H',n&0xffff)
def l(n): return struct.pack('>I',n&0xffffffff)

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    base=parse(raw)
    assert inspect(base)['issues']==[]
    assert list(base.jumps)==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,0]

    seg=[]; p=0
    for n in base.jumps:
        seg.append(bytearray(base.code[p:p+2*n])); p+=2*n
    assert p==len(base.code)
    original=[bytes(x) for x in seg]

    loader=seg[13]
    pos=loader.find(SET_RGB32)
    assert pos>=0 and loader.find(SET_RGB32,pos+1)<0

    # Same-size replacement: public loader layout is unchanged.
    loader[pos:pos+4]=bytes.fromhex('61000000')

    # Hidden helper occupies the former empty sentinel slot.
    seg[15]=bytearray(HELPER)
    seg.append(bytearray())

    jumps=[len(x)//2 for x in seg]
    assert jumps==[185,2,8,8,48,167,198,75,108,15,141,74,79,558,379,29,0]

    # Patch BSR.W from Aga Iff Load to hidden helper.
    starts=[]; acc=0
    for x in seg:
        starts.append(acc); acc+=len(x)
    ext=starts[13]+pos+2
    target=starts[15]
    disp=target-ext
    assert -32768 <= disp <= 32767
    struct.pack_into('>h',loader,pos+2,disp)

    # All existing public routines except the one 4-byte loader call are
    # otherwise byte-for-byte identical and every public segment size is fixed.
    for i in range(15):
        assert len(seg[i])==len(original[i])
        if i!=13:
            assert bytes(seg[i])==original[i]
    check=bytearray(original[13])
    check[pos:pos+4]=loader[pos:pos+4]
    assert bytes(loader)==bytes(check)

    code=b''.join(bytes(x) for x in seg)
    title=b'AMOSPro AGA M5.2 R5 LoadRGB32 palette 0.4.6\0$VER: AMOSPro_AGA 0.4.6\0'
    if len(title)&1: title+=b'\0'

    # No token change. Only hidden helper + jump-table sentinel are appended.
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
    assert len(out)==4560
    assert hashlib.sha256(out).hexdigest()==OUT_SHA

    # Safety / intent guards.
    loader_start=parsed.starts[13]
    loader_code=parsed.code[loader_start:loader_start+2*parsed.jumps[13]]
    assert bytes.fromhex('4eaefc8e') not in loader_code
    helper_start=parsed.starts[15]
    helper_code=parsed.code[helper_start:helper_start+2*parsed.jumps[15]]
    assert bytes.fromhex('4eaefc8e') in helper_code  # LoadRGB32
    assert bytes.fromhex('4eaefcac') in helper_code  # preserved 256-color SetRGB32
    assert bytes.fromhex('4eaefe80') not in helper_code
    assert bytes.fromhex('4eaefec2') not in helper_code

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
