#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Prepare a future wide visual campaign outside the checkout, never activate.
The validated S2c ASC is the immutable source. 9 screens (3 widths x 3 mixes).
Real visual/Runtime/Compiler qualification remains B/C, not this preflight.
"""
import argparse,re
from hashlib import sha1,sha256
from pathlib import Path
from m19_s2d_visual_fixture import fixture,RGB
from m19_s1_agsp_bank import make_abk,parse_abk
from test_current_ram_log import verify as verify_log

ROOT=Path(__file__).resolve().parents[1]
ASC_SHA='48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec'
ABK_SHA='f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64'

def prepare(source):
    assert sha256(source).hexdigest()==ASC_SHA
    raw=fixture()
    abk=make_abk(29,raw)
    assert sha256(abk).hexdigest()==ABK_SHA
    bank,flags,payload=parse_abk(abk)
    assert (bank,flags,len(payload.images))==(29,1,24)
    s=source.decode('ascii')
    changes=[
    [
        "' M19 S2c - simple/mixed/attached, capture and full lifecycle.",
        "' M19 S2d - 16/32/64px, three modes per width, high contrast, full lifecycle."
    ],
    [
        "_ID2=42 : _J=0 : _FRAME=0 : _N=0 : _SX=0 : _SY=0 : _BASE=0",
        "_ID2=42 : _J=0 : _FRAME=0 : _N=0 : _SX=0 : _SY=0 : _BASE=0\n_WIDTH=16 : _GROUP=0 : _MIX=0 : _OTHER=9 : _CAP_X2=25\n_CAP_LEN1=136 : _CAP_LEN2=360 : _WIDTH_REFUSED=0 : _WIDTH_RC=-999"
    ],
    [
        "Dim _CHIP_CLOSED(3),_FAST_CLOSED(3)",
        "Dim _CHIP_CLOSED(9),_FAST_CLOSED(9)"
    ],
    [
        "AGSP_S2C_MIXED.ABK",
        "AGSP_WIDE_TEST.ABK"
    ],
    [
        "Length(29)<>1440",
        "Length(29)<>6816"
    ],
    [
        "For _SCREEN_NO=1 To 3\n   If _ERR=0 and _CLEAN_ERR=0",
        "For _SCREEN_NO=1 To 9\n   _WIDTH=16 : _GROUP=0 : _OTHER=9\n   If _SCREEN_NO>3\n      _WIDTH=32 : _GROUP=1 : _OTHER=1\n   End If\n   If _SCREEN_NO>6\n      _WIDTH=64 : _GROUP=2\n   End If\n   _MIX=(_SCREEN_NO-1) mod 3\n   _CAP_X2=9+_WIDTH : _CAP_LEN1=128+_WIDTH/2 : _CAP_LEN2=224+_WIDTH*8+_WIDTH/2\n   If _ERR=0 and _CLEAN_ERR=0"
    ],
    [
        "_OK=Aga Blit Fill(10,200,16,16,0)",
        "_OK=Aga Blit Fill(10,200,_WIDTH,16,0)"
    ],
    [
        "Get Aga Sprite 1,10,200,25,200,0",
        "Get Aga Sprite 1,10,200,_CAP_X2,200,0"
    ],
    [
        "If Length(30)<>136",
        "If Length(30)<>_CAP_LEN1"
    ],
    [
        "If Deek(_CAP_PTR+8)<>1 or Leek(_CAP_PTR+24)<>2 or Deek(_CAP_PTR+38)<>4",
        "If Deek(_CAP_PTR+8)<>1 or Leek(_CAP_PTR+24)<>2 or Deek(_CAP_PTR+34)<>_WIDTH or Deek(_CAP_PTR+38)<>4"
    ],
    [
        "Get Aga Sprite 2,10,200,25,215,0",
        "Get Aga Sprite 2,10,200,_CAP_X2,215,0"
    ],
    [
        "If Deek(_CAP_PTR+8)<>2 or Leek(_CAP_PTR+24)<>3 or Deek(_CAP_PTR+86)<>4",
        "If Deek(_CAP_PTR+8)<>2 or Leek(_CAP_PTR+24)<>3 or Deek(_CAP_PTR+82)<>_WIDTH or Deek(_CAP_PTR+86)<>4"
    ],
    [
        "Get Aga Sprite 3,10,200,25,215,0",
        "Get Aga Sprite 3,10,200,_CAP_X2,215,0"
    ],
    [
        "         _BASES(1)=3 : _BASES(2)=5 : _BASES(3)=7\n         If _SCREEN_NO=2\n            _BASES(2)=9\n         End If\n         If _SCREEN_NO=3\n            _BASES(1)=9 : _BASES(2)=9 : _BASES(3)=9\n         End If",
        "         _BASES(1)=1+_GROUP*8 : _BASES(2)=3+_GROUP*8 : _BASES(3)=5+_GROUP*8\n         If _MIX=1\n            _BASES(2)=7+_GROUP*8\n         End If\n         If _MIX=2\n            _BASES(1)=7+_GROUP*8 : _BASES(2)=7+_GROUP*8 : _BASES(3)=7+_GROUP*8\n            _OTHER=_OTHER+6\n         End If"
    ],
    [
        "                  _SHOWN=_SHOWN+1\n               End If\n            End If\n         Next _J",
        "                  _SHOWN=_SHOWN+1\n                  If _J=1\n                     _WIDTH_RC=Aga Sprite(1,16,24,_OTHER)\n                     If _WIDTH_RC=-206\n                        _WIDTH_REFUSED=_WIDTH_REFUSED+1\n                     Else\n                        _ERR=30\n                     End If\n                  End If\n               End If\n            End If\n         Next _J"
    ],
    [
        "_FULL_RC=Aga Sprite(1,16,24,3)",
        "_FULL_RC=Aga Sprite(1,16,24,_BASES(1))"
    ],
    [
        "For _CYCLE=1 To 50",
        "For _CYCLE=1 To 12"
    ],
    [
        "_SX=32+_CYCLE*4 : _SY=24+_J*56",
        "_SX=20+_CYCLE*16 : _SY=24+_J*56"
    ],
    [
        "_SX=240-_CYCLE*4",
        "_SX=240-_CYCLE*16"
    ],
    [
        "               _DC=_CHIP_CYCLE0-Chip Free\n               _DF=_FAST_CYCLE0-Fast Free",
        "               If _CYCLE=1\n                  _CHIP_CYCLE0=Chip Free : _FAST_CYCLE0=Fast Free\n               End If\n               _DC=_CHIP_CYCLE0-Chip Free\n               _DF=_FAST_CYCLE0-Fast Free"
    ],
    [
        "_SHOWN=12 and _CHANGED=450 and _MOVED=450 and _OFF_COUNT=3 and _AUTO_COUNT=9 and _FULL_COUNT=3",
        "_SHOWN=36 and _CHANGED=324 and _MOVED=324 and _OFF_COUNT=9 and _AUTO_COUNT=27 and _FULL_COUNT=9 and _WIDTH_REFUSED=9"
    ],
    [
        "_OPENED=3 and _CLOSED=3 and _PIC_CAP=6 and _PIC_META=6 and _PIC_NEG=6 and _PIC_DRAW=6 and _PIC_OWN=0 and _CAP_OK=6 and _CAP_REFUSED=3 and _CAP_OWN=0",
        "_OPENED=9 and _CLOSED=9 and _PIC_CAP=18 and _PIC_META=18 and _PIC_NEG=18 and _PIC_DRAW=18 and _PIC_OWN=0 and _CAP_OK=18 and _CAP_REFUSED=9 and _CAP_OWN=0"
    ],
    [
        "If _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0 and _CHIP0=_CHIP1 and _FAST0=_FAST1",
        "If _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0 and _CHIP0=_CHIP1 and _FAST0=_FAST1 and _CHIP_LOSS=0 and _FAST_LOSS=0"
    ],
    [
        "Print #1,\"SATURATION \";_FULL_COUNT;\" FULL_RC \";_FULL_RC",
        "Print #1,\"SATURATION \";_FULL_COUNT;\" FULL_RC \";_FULL_RC\nPrint #1,\"WIDTH_REFUSED \";_WIDTH_REFUSED;\" WIDTH_RC \";_WIDTH_RC"
    ],
    [
        "For _I=1 To 3\n   Print #1,\"SCREEN \"",
        "For _I=1 To 9\n   Print #1,\"SCREEN \""
    ]
]
    for old,new in changes:
        assert s.count(old)==1,old
        s=s.replace(old,new)
    assert len(raw)==6816
    assert s.count('Length(30)<>360')==2
    s=s.replace('Length(30)<>360','Length(30)<>_CAP_LEN2')
    s=s.replace('M19_S2C_','M19_S2D_').replace('M19_S2D_MIXED_V1','M19_S2D_WIDE_V1').replace('PASS_S2C_MIXED','PASS_S2D_WIDE')
    for i in range(15):
        r,g,b=RGB[3*i:3*i+3]
        s,n=re.subn(r'_P0=Aga Palette Set\('+str(17+i)+r',\d+,\d+,\d+\)',
                    f'_P0=Aga Palette Set({17+i},{r},{g},{b})',s)
        assert n==1
    assert max(map(len,s.splitlines()))<=220
    verify_log(s)
    return s.encode('ascii'),abk

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--temp',type=Path,required=True)
    a=p.parse_args()
    target=a.temp.resolve()
    assert target.is_dir() and not target.is_relative_to(ROOT)
    src=ROOT/'tests/current/SPRITE_PUBLIC.asc'
    before=src.read_bytes()
    asc,abk=prepare(before)
    assert (asc,abk)==prepare(before)
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_WIDE_TEST.ABK',abk)):
        with (target/name).open('xb') as out:out.write(data)
        print('S2D_CAMPAIGN',name,len(data),sha256(data).hexdigest(),
              sha1(f'blob {len(data)}'.encode()+b'\0'+data).hexdigest())
    assert src.read_bytes()==before
    print('S2D_CAMPAIGN_PREPARED_NO_ACTIVATION')
if __name__=='__main__':main()
