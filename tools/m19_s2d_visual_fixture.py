#!/usr/bin/env python3
"""Deterministic, high-contrast AGSP v1 visual source for the future wide campaign.
No Lib or active campaign write. Each width uses the same shared AGA palette.
"""
from m19_s1_agsp_bank import empty_bank, put_capture, parse_payload, make_abk
from pathlib import Path
import argparse
from hashlib import sha256

# Pens 17..31. The three simple pairs use 21..23, 25..27 and 29..31.
RGB=bytes.fromhex('D02050 8040FF 004080 FFC080 FF2020 FF9020 FFFF00 '
                  '804000 0040FF 00DFFF FFFFFF 808080 00B000 80FF00 FF00FF')
CMAP=bytes(51)+RGB+bytes(768-96)
FAMILIES=(RGB[12:21],RGB[24:33],RGB[36:45],RGB)

def pixels(width,height,colors,frame):
    assert width in (16,32,64) and 1<=height<=256
    assert colors in (3,15) and frame in (0,1)
    # Canonical first-seen order (including at height=1).
    out=bytearray(width*height)
    for y in range(height):
        for x in range(width):
            if y==0:
                pen=(x+1)%(colors+1)
            elif x==0:
                pen=1
            elif x==width-1:
                pen=colors
            elif x%16==0:
                pen=colors if (y+frame)%2==0 else 1
            elif x%16==15:
                pen=0 if (y+frame)%2==0 else colors
            elif y==height-1:
                pen=(x//4+frame)%(colors+1)
            elif (x+2*y+frame*3)%11<2:
                pen=0
            elif x<width//2:
                pen=1+(x//3+y*(1+frame))%colors
            else:
                pen=1+(x//8+2*y+frame*(1+x//16))%colors
            out[y*width+x]=pen
    return bytes(out)

def fixture():
    raw=empty_bank()
    for group,width in enumerate((16,32,64)):
        for family,rgb in enumerate(FAMILIES):
            n=len(rgb)//3
            for frame in range(2):
                ident=1+group*8+family*2+frame
                raw=put_capture(raw,ident,pixels(width,16,n,frame),
                                width,16,0,0,width,16,bytes(3)+rgb,0,mode='s2')
    bank=parse_payload(raw)
    assert len(bank.images)==24
    for group,width in enumerate((16,32,64)):
        for family,rgb in enumerate(FAMILIES):
            n=len(rgb)//3
            a,b=(bank.image(1+group*8+family*2+frame) for frame in range(2))
            assert (a.width,a.height,a.depth,a.opaque_count)==(width,16,2 if n==3 else 4,n)
            assert a.palette==b.palette==bytes(3)+rgb+bytes(45-len(rgb))
            assert a.planes!=b.planes
            for j,img in enumerate((a,b)):
                assert bytes(img.index(x,y) for y in range(16) for x in range(width))==pixels(width,16,n,j)
    return raw

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    assert a.output.name=='AGSP_WIDE_TEST.ABK'
    root=Path(__file__).resolve().parents[1]
    assert not a.output.resolve().is_relative_to(root)
    abk=make_abk(29,fixture())
    assert abk==make_abk(29,fixture())
    with a.output.open('xb') as dest:dest.write(abk)
    print('S2D_VISUAL_FIXTURE',len(abk),sha256(abk).hexdigest())
