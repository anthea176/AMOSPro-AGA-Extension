#!/usr/bin/env python3
"""Byte-pinned static and deterministic two-page pixel tests for public AGA Bob demo.

This source audit is not AMOS/WinUAE Runtime validation of the new example.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re
import sys

ASC_NAME = "BOB_LOCAL_RESTORE.asc"
EXPECTED_SIZE = 8001
EXPECTED_SHA = "08edb560c4ca5c409c7d6e7f74110d05018d4f522160ea799ff43b9f3a7d470e"
LIB_SHA = "838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"
W, H = 320, 256
BOBS = ((17,15,4), (37,8,5), (17,15,4), (37,8,5))


def check_source(path: Path) -> None:
    raw = path.read_bytes()
    assert len(raw) == EXPECTED_SIZE and sha256(raw).hexdigest() == EXPECTED_SHA, "Public source version drift"
    src = raw.decode('ascii')
    assert '\r' not in src and src.endswith('Return\n')
    assert max(map(len, src.splitlines())) <= 200
    assert LIB_SHA not in src or "Requires B7-m1" in src
    assert "Prg State" in src and "If _PRG=-1" in src  # no untested Compiler claim
    assert "Aga Text(12,15,7,\"AGA BOBS - LOCAL RESTORE\")" in src
    assert "Aga Text(12,27,5,\"4 BOBS / KEY OR CLICK TO EXIT\")" in src
    assert "If _TX1=0 and _TRY<40" in src and "If _TX2=0 and _TRY<40" in src
    assert "_KEY=Aga Key : _CLICK=Aga Mouse Pressed" in src
    assert "If _KEY>0 or _CLICK>0" in src
    assert "For _PASS=1 To 20" in src and "For _FRAME=1 To 120" in src
    assert "_PAGE=1-_PAGE" in src and "If _FRAMES<2" in src
    assert "For _ROW=2 To 7" in src and "_DY=_ROW*32" in src
    assert "_SY=_SY-32" in src and "Until _SY<64" in src and "_SLICE=64-_SY" in src
    assert "Aga Blit Copy(_DX,_SY,_DX,_DY,_DW,_SLICE)" in src
    assert src.count('Aga Bob Draw') == 1 and src.count('Aga Swap') == 1
    for i in range(1, 5):
        assert f'Aga Bob {i},_X{i},_Y{i},1' in src
        assert f'_OX{i}(_PAGE)=_X{i} : _OY{i}(_PAGE)=_Y{i}' in src
        assert f'_DX=_OX{i}(_PAGE) : _DY=_OY{i}(_PAGE)' in src
    for t in ('Aga Screen Open', 'Aga Double Buffer', 'Aga Screen Close', 'Amos To Front',
              'Erase _BANK1', 'Erase _BANK2', '_ERR=13', '_ERR=14', '_ERR=15',
              'Get AGA Bob', 'Make AGA Bob Mask 1,0', 'No AGA Bob Mask 1',
              '_RESTORE_ALL:', '_BUILD_SCENE:'):
        assert t in src, t
    code = '\n'.join(l.split("'",1)[0] for l in src.splitlines())
    assert 'Timer' not in code and 'RUN_TICKS' not in code and 'RAM:' not in code
    assert src.index('If _ERR=0\n            Gosub _DO_SWAP') < src.index('_PAGE=1-_PAGE')
    assert len(re.findall(r'(?m)^\s*If\b',src)) == len(re.findall(r'(?m)^\s*End If\b',src))
    assert len(re.findall(r'(?m)^\s*For\b',src)) == len(re.findall(r'(?m)^\s*Next\b',src))
    assert len(re.findall(r'(?m)^\s*Repeat\b',src)) == len(re.findall(r'(?m)^\s*Until\b',src))
    assert not re.search(r'\bThen\b|\bElseIf\b|\bExit For\b',src)
    assert "Erase All" not in '\n'.join(l.split("'",1)[0] for l in src.splitlines())


def painted(rows: bytearray,x:int,y:int,w:int,h:int,c:int):
    for yy in range(y,y+h):
        rows[yy*W+x:yy*W+x+w]=bytes([c])*w


def baseline() -> bytearray:
    """Represent header as immutable pens; exact system font pixels are out-of-scope."""
    base=bytearray(W*H)
    painted(base,0,0,W,64,1)
    painted(base,0,0,W,3,7)
    painted(base,0,30,W,2,7)
    # Non-white mock glyphs (opaque within the header, outside master source).
    painted(base,12,10,160,3,7)
    painted(base,12,23,215,3,5)
    for t in range(10):
        x=t*32
        painted(base,x+2,35,28,25,3)
        painted(base,x+4,38,20,5,7)
        painted(base,x+8,48,15,3,6)
        painted(base,x+4,54,22,4,8)
        painted(base,x+23,55,4,4,9)
    # Replicate master source Y 32..63 to six rows 64..255.
    for y in range(64,256,32):
        base[y*W:(y+32)*W]=base[32*W:64*W]
    return base


def positions(frame:int):
    p=frame if frame<=60 else 120-frame
    return ((-10+p*5,72),(315-p*5,110),(-5+p*2,170-p),(315-p*3,200-p))


def draw(page:bytearray,pos:tuple[tuple[int,int],...] ):
    for i,((x,y),(width,height,color)) in enumerate(zip(pos,BOBS)):
        for dy in range(height):
            yy=y+dy
            if yy < 64 or yy >= H: continue
            for dx in range(width):
                xx=x+dx
                if not (0<=xx<W): continue
                if i in (0,2) and 5<=dx<10 and 5<=dy<10: continue
                page[yy*W+xx]=color


def copy_rect(page:bytearray,x:int,y:int,width:int,height:int)->tuple[int,int]:
    if x<0:
        width+=x; x=0
    if y<64:
        height+=y-64; y=64
    width=min(width,W-x)
    height=min(height,H-y)
    if width<=0 or height<=0: return 0,0
    copies=0; split=0
    if (y-64)%32+height>32: split=1
    while height:
        sy=32+((y-64)%32)
        n=min(height,64-sy)
        assert 32<=sy<64 and sy+n<=64
        for row in range(n):
            page[(y+row)*W+x:(y+row)*W+x+width]=page[(sy+row)*W+x:(sy+row)*W+x+width]
        copies+=1
        y+=n
        height-=n
    return copies,split


def pixel_oracle():
    clean=baseline()
    page_buffers=[bytearray(clean),bytearray(clean)]
    previous=[None,None]
    page=0
    frames=0; copy_calls=0; boundary_splits=0
    for cycle in range(3):
        for frame in range(1,121):
            pos=positions(frame)
            hidden=page_buffers[page]
            if frames<2:
                for row in range(2,8):
                    c,s=copy_rect(hidden,0,row*32,320,32)
                    assert (c,s)==(1,0)
                    copy_calls+=c
            else:
                assert previous[page] is not None
                for ((px,py),(w,h,color)) in zip(previous[page],BOBS):
                    c,s=copy_rect(hidden,px,py,w,h)
                    copy_calls+=c;boundary_splits+=s
            draw(hidden,pos)
            expected=bytearray(clean)
            draw(expected,pos)
            assert hidden==expected, (cycle,frame,page,'corrupted background or stale Bob')
            assert hidden[:64*W]==clean[:64*W], 'header or clean tile source altered'
            previous[page]=pos
            page^=1
            frames+=1
    assert frames==360 and boundary_splits>0 and copy_calls>1300
    return frames,copy_calls,boundary_splits


def run(path: Path | None=None)->None:
    path=path or (Path(__file__).resolve().parents[1]/'examples/bob_local_restore/BOB_LOCAL_RESTORE.asc')
    check_source(path)
    frames,copy_calls,boundary_splits=pixel_oracle()
    print('BOB LOCAL RESTORE EXAMPLE STATIC PASS:',frames,'pixel-checked frame compositions',copy_calls,'Copy slices',boundary_splits,'boundary splits; Runtime pending')


if __name__=='__main__':
    run(Path(sys.argv[1]) if len(sys.argv)>1 else None)
