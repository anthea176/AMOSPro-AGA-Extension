#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Generate S2e visual qualification inputs outside the repository, never install.
The S2d Runtime-tested ASC and ABK remain immutable.
"""
import argparse
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from m19_s1_agsp_bank import parse_abk,make_abk,set_hotspot
from test_current_ram_log import verify as verify_log

ROOT=Path(__file__).resolve().parents[1]
ASC_SHA='520c1a8a4c964b288fc76a337b5a6389e33d28340a98a8b21b342abaddaa1a29'
ABK_SHA='f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64'
PATCHES=[
  [
    "' M19 S2d - 16/32/64px, three modes per width, high contrast, full lifecycle.",
    "' M19 S2e - signed hotspots, 16/32/64px, full S2d lifecycle."
  ],
  [
    "_WIDTH_REFUSED=0 : _WIDTH_RC=-999",
    "_WIDTH_REFUSED=0 : _WIDTH_RC=-999\n_HOT_REFUSED=0 : _HOT_RC=-999 : _HOT_CHANGE_RC=-999"
  ],
  [
    "AGSP_WIDE_TEST.ABK",
    "AGSP_HOTSPOT_TEST.ABK"
  ],
  [
    "If _J=1\n                     _WIDTH_RC=Aga Sprite(1,16,24,_OTHER)\n                     If _WIDTH_RC=-206\n                        _WIDTH_REFUSED=_WIDTH_REFUSED+1\n                     Else\n                        _ERR=30\n                     End If\n                  End If",
    "If _J=1\n                     _HOT_RC=Aga Sprite(_N,_WIDTH/2-1,8,_BASE)\n                     If _HOT_RC=-128\n                        _HOT_REFUSED=_HOT_REFUSED+1\n                     Else\n                        _ERR=31\n                     End If\n                     If _ERR=0\n                        _HOT_CHANGE_RC=Aga Sprite(_N,-4,-4,_BASE+1)\n                        If _HOT_CHANGE_RC=-128\n                           _HOT_REFUSED=_HOT_REFUSED+1\n                        Else\n                           _ERR=32\n                        End If\n                     End If\n                     If _ERR=0\n                        _WIDTH_RC=Aga Sprite(1,80,24,_OTHER)\n                        If _WIDTH_RC=-206\n                           _WIDTH_REFUSED=_WIDTH_REFUSED+1\n                        Else\n                           _ERR=30\n                        End If\n                     End If\n                  End If"
  ],
  [
    "_FULL_RC=Aga Sprite(1,16,24,_BASES(1))",
    "_FULL_RC=Aga Sprite(1,80,24,_BASES(1))"
  ],
  [
    "                     _CHANGE_RC=Aga Sprite(_N,_SX,_SY,_BASE+_FRAME)",
    "                     If _CYCLE<=2\n                        _SX=32\n                     End If\n                     _CHANGE_RC=Aga Sprite(_N,_SX,_SY,_BASE+_FRAME)"
  ],
  [
    "               If _CYCLE=1\n                  _CHIP_CYCLE0",
    "               If _CYCLE<=2\n                  For _I=1 To 10\n                     Aga Wait Vbl\n                  Next _I\n               End If\n               If _CYCLE=1\n                  _CHIP_CYCLE0"
  ],
  [
    "_FULL_COUNT=9 and _WIDTH_REFUSED=9",
    "_FULL_COUNT=9 and _WIDTH_REFUSED=9 and _HOT_REFUSED=18"
  ],
  [
    "Print #1,\"WIDTH_REFUSED \";_WIDTH_REFUSED;\" WIDTH_RC \";_WIDTH_RC",
    "Print #1,\"WIDTH_REFUSED \";_WIDTH_REFUSED;\" WIDTH_RC \";_WIDTH_RC\nPrint #1,\"HOT_REFUSED \";_HOT_REFUSED;\" HOT_RC \";_HOT_RC;\" HOT_CHANGE_RC \";_HOT_CHANGE_RC"
  ],
  [
    "PASS_S2D_WIDE",
    "PASS_S2E_HOTSPOT"
  ],
  [
    "M19_S2D_WIDE_V1",
    "M19_S2E_HOTSPOT_V1"
  ]
]

def prepare(source,bank):
    assert sha256(source).hexdigest()==ASC_SHA
    assert sha256(bank).hexdigest()==ABK_SHA
    n,flags,original=parse_abk(bank)
    assert (n,flags,len(original.images))==(29,1,24)
    raw=original.raw
    expected=[]
    for im in original.images:
        assert im.hotspot_x==im.hotspot_y==0
        hx,hy=(im.width//2,8) if im.image_id%2 else (-3,-4)
        raw=set_hotspot(raw,im.image_id,hx,hy)
        expected.append(replace(im,hotspot_x=hx,hotspot_y=hy))
    new=make_abk(n,raw)
    bn,bf,parsed=parse_abk(new)
    assert (bn,bf,len(new))==(n,flags,len(bank))
    assert parsed.generation==original.generation+24
    assert parsed.images==tuple(expected)
    def valid(x,y,i):
        im=parsed.image(i)
        return 0<=x-im.hotspot_x<=320-im.width and 0<=y-im.hotspot_y<=256-im.height
    # Check all future Show/Change/Move coordinates and expected refusals.
    for group,width in enumerate((16,32,64)):
        for mix in range(3):
            ids=[1+group*8,3+group*8,5+group*8]
            other=9 if group==0 else 1
            if mix==1:ids[1]=7+group*8
            if mix==2:ids=[7+group*8]*3;other+=6
            assert parsed.image(other).width!=width
            assert valid(80,24,other) and valid(80,24,ids[0])
            assert not valid(width//2-1,8,ids[0])
            assert not valid(-4,-4,ids[0]+1)
            for j,i in enumerate(ids,1):
                y=24+j*56
                assert valid(32,y,i)
                for cycle in range(1,13):
                    x=32 if cycle<=2 else (240-cycle*16 if j==2 else 20+cycle*16)
                    assert valid(x,y,i+cycle%2) and valid(x+2,y,i+cycle%2)
            assert valid(160,136,ids[1])
    text=source.decode('ascii')
    for old,replacement in PATCHES:
        assert text.count(old)==1,old
        text=text.replace(old,replacement,1)
    text=text.replace('RAM:M19_S2D_','RAM:M19_S2E_')
    verify_log(text)
    return text.encode('ascii'),new

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--temp',type=Path,required=True)
    a=p.parse_args()
    temp=a.temp.resolve()
    assert not temp.is_relative_to(ROOT)
    from verify_m19_s2e_delivery import S2E_SHA,pre_s2e_pair
    from build_m19_s2e_in_memory import protected
    from verify_m19_s2f_delivery import pre_s2f_pair
    canon=protected()
    before=canon[2]
    parent=pre_s2f_pair(canon)
    source=pre_s2e_pair(parent)[2]
    bank=(ROOT/'tests/current/AGSP_WIDE_TEST.ABK').read_bytes()
    asc,abk=prepare(source,bank)
    assert (asc,abk)==prepare(source,bank)
    if sha256(parent[0]).hexdigest()==S2E_SHA:
        assert asc==parent[2] and abk==(ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes()
    temp.mkdir(parents=True,exist_ok=True)
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_HOTSPOT_TEST.ABK',abk)):
        with (temp/name).open('xb') as f:f.write(data)
        print('S2E_CAMPAIGN',name,len(data),sha256(data).hexdigest(),flush=True)
    assert (ROOT/'tests/current/SPRITE_PUBLIC.asc').read_bytes()==before
    assert protected()==canon
    assert (ROOT/'tests/current/AGSP_WIDE_TEST.ABK').read_bytes()==bank
    print('S2E_CAMPAIGN_PREPARED_NOT_ACTIVATED',flush=True)
if __name__=='__main__':main()
