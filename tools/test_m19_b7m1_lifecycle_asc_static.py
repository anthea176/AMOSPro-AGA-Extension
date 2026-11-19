#!/usr/bin/env python3
"""Strict source pin + two-page pixel oracle for M19 B7-m2 Off/On Gate B/C ASC.

Model reproduces local-copy geometry and Bob footprints only; it cannot
verify real AGA DMA, OS callbacks, text glyphs or actual AMOS Runtime.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import sys

NAME='M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc'
LIB='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
SIZE=10911
SHA='a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec'
W,H=320,256
STAGE_COUNTS=(2,1,0,2,4,8,16,64,16)


def tile_master()->bytearray:
    """Byte-valued, intentionally non-flat 32-pixel pattern at y 32..63."""
    tile=bytearray(W*32)
    for y in range(32):
        for x in range(W):
            # Unique multicolour pattern, not an actual rasterized system font.
            tile[y*W+x]=(x//4+y//3+((x//32)&3))%8+1
    return tile


def baseline(tile:bytearray)->bytearray:
    image=bytearray(W*H)
    for y in range(32,64):
        image[y*W:(y+1)*W]=tile[(y-32)*W:(y-31)*W]
    for y in range(64,256):
        image[y*W:(y+1)*W]=tile[((y-64)%32)*W:(((y-64)%32)+1)*W]
    return image


def restore_rect(page:bytearray, x:int,y:int,w:int,h:int)->int:
    """Native sample copies source x,Y modulo32 from clean master y=32..63."""
    if x<0:
        w+=x; x=0
    if y<64:
        h+=y-64; y=64
    if x+w>W: w=W-x
    if y+h>H: h=H-y
    if w<=0 or h<=0: return 0
    copies=0
    remaining=h
    while remaining:
        sy=32+((y-64)%32)
        step=min(remaining,64-sy)
        assert sy>=32 and sy+step<=64
        for offset in range(step):
            s=(sy+offset)*W+x
            d=(y+offset)*W+x
            page[d:d+w]=page[s:s+w]
        y+=step; remaining-=step
        copies+=1
    return copies


def positions(ident:int,step:int)->tuple[int,int]:
    return ((ident-1)%8*40+step%7-3,66+(ident-1)//8*22)


def draw(page:bytearray,ident:int,x:int,y:int)->None:
    width,height,pen=(17,15,4) if ident%2 else (37,8,5)
    for dy in range(height):
        yy=y+dy
        if yy<64 or yy>=H: continue
        for dx in range(width):
            xx=x+dx
            if not 0<=xx<W: continue
            if ident%2 and 5<=dx<10 and 5<=dy<10: continue
            page[yy*W+xx]=pen


def oracle()->tuple[int,int,int]:
    backdrop=baseline(tile_master())
    pages=[bytearray(backdrop),bytearray(backdrop)]
    last=[{},{}]
    frame_count=0; copy_calls=0; off_transitions=0
    page=0
    for stage,count in enumerate(STAGE_COUNTS,1):
        before=1 if stage in (2,3) else 48 if stage==9 else 0
        off_transitions+=before
        ids=(range(2,3) if stage==2 else range(1,count+1))
        for step in range(1,46):
            hidden=pages[page]
            for ident,(x,y) in last[page].items():
                width,height=(17,15) if ident%2 else (37,8)
                copy_calls+=restore_rect(hidden,x,y,width,height)
            next_locs={ident:positions(ident,step) for ident in ids}
            for ident,(x,y) in next_locs.items():
                draw(hidden,ident,x,y)
            expected=bytearray(backdrop)
            for ident,(x,y) in next_locs.items():
                draw(expected,ident,x,y)
            assert hidden[64*W:]==expected[64*W:], (stage,step,page,'ghost/trail/mask')
            assert hidden[32*W:64*W]==backdrop[32*W:64*W], (stage,step,'source altered')
            last[page]=next_locs
            page=1-page
            frame_count+=1
    assert frame_count==405 and off_transitions==50
    assert last[0] and last[1] and len(last[0])==len(last[1])==16
    return frame_count,copy_calls,off_transitions


def verify(path:Path)->None:
    data=path.read_bytes()
    assert len(data)==SIZE and sha256(data).hexdigest()==SHA,'current ASC source drift'
    src=data.decode('ascii');lines=src.splitlines()
    assert max(map(len,lines))<=200 and src.endswith('Return\n')
    assert LIB in src and 'NO TIMER OR BENCHMARK' in src
    # -1 is the compiled mode and must NOT trigger the error 1 shortcut.
    mode = r'If _PRG=-1\n\s*_MODE\$="COMPILED"\nEnd If\nIf _MODE\$="UNKNOWN"\n\s*_ERR=1 : Goto _CLEANUP\nEnd If'
    assert re.search(mode,src), 'Compiler -1 branch must not abort the test'
    assert '_MODE$="RUNTIME"' in src and '_MODE$="INTERPRETED"' in src
    assert 'Print #1,"TEST M19 B7-M2 BOB LIFECYCLE ";_MODE$' in src
    assert 'Print #1,"RUN_MODE ";_MODE$' in src
    assert 'Print #1,"PRG_STATE ";_PRG' in src
    assert src.count('Aga Bob Draw')==1 and src.count('Aga Swap')==1
    assert src.count('Aga Bob Off 1')==1 and src.count('Aga Bob Off 2')==1
    assert src.count('Aga Bob Off _ID')==1
    for n in (2,3,9):
        assert f'If _ERR=0 and _STAGE={n}' in src
    assert src.count('Aga Blit Copy(_DX,_SY,_DX,_DY,_DW,_SLICE)')==1
    assert 'Dim _OLDON(128),_OLDX(128),_OLDY(128)' in src
    assert 'Dim _NEWX(64),_NEWY(64)' in src
    assert 'If _ERR=0 and _EXPECT>0' in src
    assert '_IDX=_PAGE*64+_ID' in src and '_PAGE=1-_PAGE' in src
    assert src.index('Gosub _DO_SWAP',src.index('For _STAGE=1 To 9'))<src.index('_PAGE=1-_PAGE')
    assert src.index('For _STAGE=1 To 9') < src.index('For _STEP=1 To 45')
    assert 'Aga Text(12,15,7,"M19 B7M2 - BOB LIFECYCLE")' in src
    assert src.count('Aga Text(12,27,5,"')==10
    assert '_TXT=Aga Text(' in src
    assert 'For _ID=17 To 64' in src and '_OFF_SENT=_OFF_SENT+1' in src
    assert 'If _ERR=0 and _FR_OK=405 and _STAGES_OK=9 and _OFF_SENT=50' in src
    assert 'If _CLOSE_CALLED=1 and _BANKS_ERASED=2 and _DB=1' in src
    assert 'CLOSE_RETURNED' in src and 'OFF_COMMANDS_ISSUED' in src
    assert 'FRAMES_OK' in src and 'STAGE_FRAMES_OK' in src and 'STAGE' in src
    assert 'Trap Open Out 1,_LOG$' in src and 'Trap Close 1' in src
    assert 'RAM:M19_B7M1_BOB_LIFECYCLE.TXT' in src
    assert src.index('_CLEANUP:')<src.index('Aga Screen Close',src.index('_CLEANUP:'))
    assert src.index('Aga Screen Close',src.index('_CLEANUP:'))<src.index('Erase _BANK1',src.index('_CLEANUP:'))
    assert 'Aga Bob Bank _BANK1' in src and 'Aga Bob Bank _BANK2' in src
    assert 'Make AGA Bob Mask 1,0' in src and 'No AGA Bob Mask 1' in src
    executable='\n'.join(x.split("'",1)[0] for x in lines)
    assert not re.search(r'\bTimer\b|\bFPS\b|\bRUN_TICKS\b|Erase All|\bThen\b|\bElseIf\b',executable,re.I)
    assert src.count('For _STAGE=1 To 9')==1
    assert len(re.findall(r'(?m)^\s*If\b',src))==len(re.findall(r'(?m)^\s*End If\b',src))
    assert len(re.findall(r'(?m)^\s*For\b',src))==len(re.findall(r'(?m)^\s*Next\b',src))
    assert len(re.findall(r'(?m)^\s*Repeat\b',src))==len(re.findall(r'(?m)^\s*Until\b',src))
    frames,copies,offs=oracle()
    print(f'M19 B7-m2 BOB LIFECYCLE ASC STATIC PASS: {frames} dual-page scenes, '
          f'{copies} local Copy slices, {offs} Off commands modelled; compiled WinUAE Gate C pending')


if __name__=='__main__':
    verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path('tests/current')/NAME)
