#!/usr/bin/env python3
"""Static gate for the P2.8 AMOS WinUAE benchmark and its exact fixtures.

This does not execute WinUAE or AMOS Compiler, nor certify real DMA.
"""
from hashlib import sha1,sha256
from pathlib import Path

from m19_p28_winuae_bundle import assets,PIXELS,ALPHA

ROOT=Path(__file__).resolve().parents[1]
SOURCE='M19_P28_R88_CACHE_BLIT_FPS_01.asc'
BLOB='001396551cad6fed57903b714bc374e0988f63ea'
P27_BLOB='e1062818abdfeb2d7e699d8c1dc9e9696250af65'
R87_SHA='02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302'
R84_SHA='46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d'

def gitblob(data:bytes)->str:
    return sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main()->None:
    g=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    a=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    assert len(g)==67904 and sha256(g).hexdigest()==R84_SHA
    assert len(a)==75040 and sha256(a).hexdigest()=='69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc'
    prior=(ROOT/'dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib').read_bytes()
    assert len(prior)==73184 and sha256(prior).hexdigest()==R87_SHA
    active=sorted((ROOT/'tests/current').glob('*.asc'))
    assert len(active)==1 and active[0].name==SOURCE
    raw=active[0].read_bytes()
    assert gitblob(raw)==BLOB and len(raw)==10375
    assert gitblob((ROOT/'tests/passed/M19_P27_R87_CACHE_CPU_BLITTER_01.asc').read_bytes())==P27_BLOB
    s=raw.decode('latin-1')
    assert s.startswith("' M19 P2.8 R88")
    assert 'Aga Bob Probe' not in s and 'ElseIf' not in s and 'Then ' not in s
    assert 'Aga Cache Blit(_CACHE,_X,_Y,_DMODE)' in s
    assert 'Aga Bank Image Draw(_RLE,_X,_Y,_DMODE)' in s
    assert 'Aga Bank Image Capture(14,_RX,_RY,32,32,-1,1)' in s
    assert 'Aga Bank Image Capture(15,_RX,_RY,32,32,-1,1)' in s
    for name,n in [('AGAPIC_P28_V1_BANK10.abk',10),('AGPC_P28_V1_BANK11.abk',20),
                   ('AGAPIC_P28_V2_BANK12.abk',12),('AGPC_P28_V2_BANK13.abk',20)]:
        assert f'Load "{name}",{n}' in s
    for bank in (11,13):
        assert f'Reserve As Chip Data {bank},360' in s
    assert '_CACHE_STAGED=_CACHE_STAGED+1' in s
    assert 'Poke _DST-8+_I,Peek(_SRC-8+_I)' in s
    assert 'CHIP_STAGE_DELTA' in s
    assert 'If _BANKS_SAFE=1\n   For _B=10 To 15' in s and 'If Length(20)<>0\n      Erase 20' in s
    assert 'PARITY_OK ' in s and 'PARITY_BAD ' in s
    assert 'For _CASE=1 To 8' in s and 'If _PARITY_OK<>8' in s
    assert 'For _PASS=0 To 1' in s and '_METHOD=1-_ORDER' in s
    assert 'For _CASE=0 To 2' in s and 'For _REP=1 To _REPS' in s
    assert '_MICRO_RUNS<>12 or _RLE_CALLS<>3584 or _CACHE_CALLS<>3584' in s
    assert '_FRAMES=24' in s and '_FRAME_RUNS<>12 or _FRAME_COUNT<>288 or _SWAPS<>288' in s
    assert '_SW=Aga Swap' in s and 'Aga Wait Vbl' in s
    assert 'RAM:M19_P28_RUNTIME.TXT' in s and 'RAM:M19_P28_COMPILED.TXT' in s
    assert 'Trap Open Out 1,_LOG$' in s and 'Trap Close 1' in s and s.rstrip().endswith('End')
    assert 'Aga Screen Close' in s and 'Amos To Front' in s
    assert max(map(len,s.splitlines()))<=200
    assert len(PIXELS)==len(ALPHA)==256 and any(p==0 and a for p,a in zip(PIXELS,ALPHA))
    files=assets()
    assert len(files)==4
    assert len(files['AGPC_P28_V1_BANK11.abk'])==len(files['AGPC_P28_V2_BANK13.abk'])==380
    print('M19 P2.8 STATIC WINUAE BUNDLE PASS: one ASC, four exact matching AGAPIC/AGPC banks,')
    print('Chip-staged AGPC v1/v2, 8 pixel comparisons before 12 draw-only and 12 full-frame A/B measures;')
    print('R88 active candidate, R87 historical and R84 LAST_GOOD byte-exact; R88 B/C NOT TESTED.')
    print('WinUAE P2.8 Runtime and Compiled NOT TESTED.')

if __name__=='__main__':
    main()
