#!/usr/bin/env python3
"""Deterministic R82 WinUAE R82 comparison banks (AGAPIC v1 and v2).

Use --write to create exact .abk fixtures. Default mode verifies on-disk
assets without modifying them. RGB24 is stored only in AGAPIC v2. Bank10
has v2 and Bank12 has an equivalent v1 planar RLE to exercise the fallback.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from m16_agapic import pack_image, make_abk
from m16_agapic_v2 import pack_image_v2,make_abk_v2,parse_abk_any

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests/design'
MODE_ID=0x00021000
W,H,D=96,64,8
F_V2='R82_AGAPIC_V2_BANK10.abk'
F_V1='R82_AGAPIC_V1_BANK12.abk'


def samples():
    pixels=bytearray()
    mask=bytearray()
    for y in range(H):
        for x in range(W):
            base=((x//3)+((y//4)*13))&255
            if 18<=x<78 and 14<=y<50:
                base=(40+(x-18)//2 + (y-14)*4)&255
            pixels.append(base)
            mask.append(int((x-48)**2//4+(y-32)**2<=650))
    pal=bytearray()
    special={0:(0,0,0),1:(255,255,255),2:(255,0,0),3:(0,255,0),
             4:(0,0,255),5:(255,255,0),6:(255,0,255),7:(0,255,255)}
    for i in range(256):
        pal.extend(special.get(i,((i*17+7)&255,(i*11+31)&255,(i*7+63)&255)))
    v1=pack_image(W,H,D,bytes(pixels),bytes(mask))
    v2=pack_image_v2(W,H,D,bytes(pixels),bytes(pal),MODE_ID,bytes(mask))
    x=make_abk(12,v1)
    y=make_abk_v2(10,v2)
    assert parse_abk_any(x)[2].version==1
    assert parse_abk_any(y)[2].version==2
    assert parse_abk_any(y)[2].palette==bytes(pal)
    return {F_V2:y,F_V1:x}


def run(write:bool, out:Path)->None:
    produced=samples()
    if write: out.mkdir(parents=True,exist_ok=True)
    for name,data in produced.items():
        path=out/name
        if write:
            path.write_bytes(data)
        elif not path.is_file() or path.read_bytes()!=data:
            raise SystemExit('R82 sample bank missing/mismatch: '+str(path))
        print('R82 FIXTURE',name,'bytes=',len(data),'sha256=',sha256(data).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--out',type=Path,default=OUT)
    p=parser.parse_args()
    run(p.write,p.out)
