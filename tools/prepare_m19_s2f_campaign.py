#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Derive a future S2f campaign from the exact S2e Runtime-tested source.
No replacement of active files; the original AGSP bank is reused verbatim."""
import argparse
from hashlib import sha256,sha1
from pathlib import Path
from shutil import copyfile
from build_m19_s2e_in_memory import protected
from verify_m19_s2e_delivery import verify_asc,verify_abk
from m19_s1_agsp_bank import parse_abk
from test_current_ram_log import verify as verify_log
from test_m19_s2f_clip_kernel_gate_a import oracle
ROOT=Path(__file__).resolve().parents[1]
PATCHES=[
  [
    "' M19 S2e - signed hotspots, 16/32/64px, full S2d lifecycle.",
    "' M19 S2f - fixed-width clipping, signed hotspots, 16/32/64px."
  ],
  [
    "_HOT_REFUSED=0 : _HOT_RC=-999 : _HOT_CHANGE_RC=-999",
    "_CLIP_COUNT=0 : _OUT_COUNT=0 : _RESTORE_COUNT=0 : _CLIP_CHANGE=0\n_CLIP_RC=-999 : _OUT_RC=-999 : _OVERFLOW=0 : _OVERFLOW_RC=-999\n_CLIP_SHOW=0 : _ERASE_MOVES=0 : _ERASE_RC=-999\n_EDGE=0 : _OX=0 : _OY=0 : _HOLD=0"
  ],
  [
    "                     _HOT_RC=Aga Sprite(_N,_WIDTH/2-1,8,_BASE)\n                     If _HOT_RC=-128\n                        _HOT_REFUSED=_HOT_REFUSED+1\n                     Else\n                        _ERR=31\n                     End If\n                     If _ERR=0\n                        _HOT_CHANGE_RC=Aga Sprite(_N,-4,-4,_BASE+1)\n                        If _HOT_CHANGE_RC=-128\n                           _HOT_REFUSED=_HOT_REFUSED+1\n                        Else\n                           _ERR=32\n                        End If\n                     End If\n                     If _ERR=0\n                        _WIDTH_RC=Aga Sprite(1,80,24,_OTHER)\n                        If _WIDTH_RC=-206\n                           _WIDTH_REFUSED=_WIDTH_REFUSED+1\n                        Else\n                           _ERR=30\n                        End If\n                     End If",
    "                     _WIDTH_RC=Aga Sprite(1,80,24,_OTHER)\n                     If _WIDTH_RC=-206\n                        _WIDTH_REFUSED=_WIDTH_REFUSED+1\n                     Else\n                        _ERR=30\n                     End If"
  ],
  [
    "         If _ERR=0\n            _OFF_RC=Aga Sprite Off(42)",
    "         ' Keep the measured, fully visible animation above unchanged.\n         ' Now test every edge/corner and disjoint edge for all three IDs.\n         For _J=1 To 3\n            If _ERR=0\n               _N=_IDS(_J) : _BASE=_BASES(_J)\n               _SY=24+_J*56\n               _HOLD=2\n               If _J=1\n                  _HOLD=8\n               End If\n               For _EDGE=1 To 13\n                  If _ERR=0\n                     If _EDGE=1\n                        _OX=-_WIDTH/2 : _OY=_SY-8\n                     End If\n                     If _EDGE=2\n                        _OX=320-_WIDTH/2 : _OY=_SY-8\n                     End If\n                     If _EDGE=3\n                        _OX=32+_J*60 : _OY=-8\n                     End If\n                     If _EDGE=4\n                        _OX=32+_J*60 : _OY=248\n                     End If\n                     If _EDGE=5\n                        _OX=-_WIDTH/2 : _OY=-8\n                     End If\n                     If _EDGE=6\n                        _OX=320-_WIDTH/2 : _OY=-8\n                     End If\n                     If _EDGE=7\n                        _OX=-_WIDTH/2 : _OY=248\n                     End If\n                     If _EDGE=8\n                        _OX=320-_WIDTH/2 : _OY=248\n                     End If\n                     If _EDGE=9\n                        _OX=-_WIDTH : _OY=_SY-8\n                     End If\n                     If _EDGE=10\n                        _OX=320 : _OY=_SY-8\n                     End If\n                     If _EDGE=11\n                        _OX=32+_J*60 : _OY=-16\n                     End If\n                     If _EDGE=12\n                        _OX=32+_J*60 : _OY=256\n                     End If\n                     If _EDGE=13\n                        _OX=32-_WIDTH/2 : _OY=_SY-8\n                     End If\n                     _CLIP_RC=Aga Sprite(_N,_OX+_WIDTH/2,_OY+8,_BASE)\n                     If _CLIP_RC<>1\n                        _ERR=31\n                     Else\n                        If _EDGE<=8\n                           _CLIP_COUNT=_CLIP_COUNT+1\n                        Else\n                           If _EDGE<=12\n                              _OUT_COUNT=_OUT_COUNT+1\n                              _OUT_RC=_CLIP_RC\n                           Else\n                              _RESTORE_COUNT=_RESTORE_COUNT+1\n                           End If\n                        End If\n                        For _I=1 To _HOLD\n                           Aga Wait Vbl\n                        Next _I\n                     End If\n                  End If\n               Next _EDGE\n               If _ERR=0\n                  ' Even frame has a signed hotspot (-3,-4).\n                  _CLIP_RC=Aga Sprite(_N,-6,244,_BASE+1)\n                  If _CLIP_RC<>1\n                     _ERR=32\n                  Else\n                     _CLIP_CHANGE=_CLIP_CHANGE+1\n                     For _I=1 To _HOLD\n                        Aga Wait Vbl\n                     Next _I\n                  End If\n               End If\n               If _ERR=0\n                  _CLIP_RC=Aga Sprite(_N,32,_SY,_BASE)\n                  If _CLIP_RC<>1\n                     _ERR=32\n                  Else\n                     _CLIP_CHANGE=_CLIP_CHANGE+1\n                  End If\n               End If\n            End If\n         Next _J\n         If _ERR=0\n            ' Subtraction of a positive hotspot must overflow signed LONG.\n            _OVERFLOW_RC=Aga Sprite(17,-2147483647,8,_BASES(1))\n            If _OVERFLOW_RC=-128\n               _OVERFLOW=_OVERFLOW+1\n            Else\n               _ERR=33\n            End If\n         End If\n         If _ERR=0\n            _OFF_RC=Aga Sprite Off(42)"
  ],
  [
    "               _SPRITE_RC=Aga Sprite(9,160,136,_BASES(2))",
    "               _SPRITE_RC=Aga Sprite(9,319+_WIDTH/2,136,_BASES(2))"
  ],
  [
    "                  _ID2=9 : _SHOWN=_SHOWN+1",
    "                  _ID2=9 : _SHOWN=_SHOWN+1\n                  _CLIP_SHOW=_CLIP_SHOW+1\n                  For _I=1 To 16\n                     Aga Wait Vbl\n                  Next _I\n                  _CLIP_RC=Aga Sprite(9,160,136,_BASES(2))\n                  If _CLIP_RC<>1\n                     _ERR=34\n                  End If"
  ],
  [
    "         If _ERR=0\n            _AUTO_COUNT=_AUTO_COUNT+3",
    "         ' Last screen: delete the source while all three sprites are live.\n         ' Only same-image calls may use the retained original.\n         If _ERR=0 and _SCREEN_NO=9 and _BANK_OWN=1\n            Erase 29\n            If Length(29)<>0\n               _ERR=35\n            Else\n               _BANK_OWN=0\n               For _J=1 To 3\n                  If _ERR=0\n                     _N=_IDS(_J) : _BASE=_BASES(_J)\n                     If _J=2\n                        _N=_ID2\n                     End If\n                     _SY=24+_J*56\n                     For _EDGE=1 To 3\n                        If _ERR=0\n                           _OX=-1 : _OY=-1\n                           If _EDGE=2\n                              _OX=320 : _OY=256\n                           End If\n                           If _EDGE=3\n                              _OX=32 : _OY=_SY-8\n                           End If\n                           _ERASE_RC=Aga Sprite(_N,_OX+_WIDTH/2,_OY+8,_BASE)\n                           If _ERASE_RC<>1\n                              _ERR=36\n                           Else\n                              _ERASE_MOVES=_ERASE_MOVES+1\n                              For _I=1 To 8\n                                 Aga Wait Vbl\n                              Next _I\n                           End If\n                        End If\n                     Next _EDGE\n                  End If\n               Next _J\n            End If\n         End If\n         If _ERR=0\n            _AUTO_COUNT=_AUTO_COUNT+3"
  ],
  [
    " and _HOT_REFUSED=18",
    " and _OVERFLOW=9"
  ],
  [
    "         If _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0 and _CHIP0=_CHIP1 and _FAST0=_FAST1 and _CHIP_LOSS=0 and _FAST_LOSS=0",
    "         If _CLIP_COUNT=216 and _OUT_COUNT=108 and _RESTORE_COUNT=27 and _CLIP_CHANGE=54 and _CLIP_SHOW=9 and _ERASE_MOVES=9 and _BANK_OWN=0\n            If _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0 and _CHIP0=_CHIP1 and _FAST0=_FAST1 and _CHIP_LOSS=0 and _FAST_LOSS=0"
  ],
  [
    "            _RESULT=1\n            _VERDICT$=\"PASS_S2E_HOTSPOT\"\n         Else\n            _ERR=14\n         End If",
    "               _RESULT=1\n               _VERDICT$=\"PASS_S2F_CLIPPING\"\n            Else\n               _ERR=14\n            End If\n         Else\n            _ERR=37\n         End If"
  ],
  [
    "Print #1,\"HOT_REFUSED \";_HOT_REFUSED;\" HOT_RC \";_HOT_RC;\" HOT_CHANGE_RC \";_HOT_CHANGE_RC",
    "Print #1,\"CLIPPED \";_CLIP_COUNT;\" OUTSIDE \";_OUT_COUNT;\" RESTORED \";_RESTORE_COUNT;\" CLIP_CHANGE \";_CLIP_CHANGE\nPrint #1,\"CLIP_RC \";_CLIP_RC;\" OUT_RC \";_OUT_RC;\" OVERFLOW \";_OVERFLOW;\" OVERFLOW_RC \";_OVERFLOW_RC\nPrint #1,\"CLIP_SHOW \";_CLIP_SHOW;\" ERASE_MOVES \";_ERASE_MOVES;\" ERASE_RC \";_ERASE_RC;\" BANK_OWN \";_BANK_OWN"
  ],
  [
    "SOURCE_TAG M19_S2E_HOTSPOT_V1",
    "SOURCE_TAG M19_S2F_CLIPPING_V1"
  ]
]

def prepare(source,bank):
    verify_asc(source)
    verify_abk(bank)
    _,_,payload=parse_abk(bank)
    for w in (16,32,64):
        group=(16,32,64).index(w)
        for family in range(4):
            im=payload.image(1+group*8+family*2)
            even=payload.image(im.image_id+1)
            assert (im.width,im.height,im.hotspot_x,im.hotspot_y)==(w,16,w//2,8)
            assert (even.hotspot_x,even.hotspot_y)==(-3,-4)
            for j in (1,2,3):
                sy=24+j*56
                points=[(-w//2,sy-8),(320-w//2,sy-8),(32+j*60,-8),(32+j*60,248),
                        (-w//2,-8),(320-w//2,-8),(-w//2,248),(320-w//2,248),
                        (-w,sy-8),(320,sy-8),(32+j*60,-16),(32+j*60,256),(32-w//2,sy-8)]
                assert [oracle(x+w//2,y+8,w//2,8,w,16)[0] for x,y in points]==[2]*8+[3]*4+[1]
            assert oracle(-6,244,-3,-4,w,16)[0]==2
            assert oracle(-2147483647,8,w//2,8,w,16)[0]==0
            assert oracle(319+w//2,136,w//2,8,w,16)[0]==2
            assert [oracle(x+w//2,y+8,w//2,8,w,16)[0] for x,y in ((-1,-1),(320,256),(32,72))]==[2,3,1]
    text=source.decode('ascii')
    for old,new in PATCHES:
        assert text.count(old)==1,old
        text=text.replace(old,new,1)
    text=text.replace('RAM:M19_S2E_','RAM:M19_S2F_')
    assert max(map(len,text.splitlines()))<=220
    verify_log(text)
    return text.encode('ascii')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--temp',required=True,type=Path)
    a=p.parse_args()
    temp=a.temp.resolve()
    assert not temp.is_relative_to(ROOT)
    before=protected()
    bank=(ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes()
    from verify_m19_s2f_delivery import S2F_SHA,pre_s2f_pair,verify_asc as verify_s2f_asc
    source=pre_s2f_pair(before)[2]
    asc=prepare(source,bank)
    assert asc==prepare(source,bank)
    if sha256(before[0]).hexdigest()==S2F_SHA:
        verify_s2f_asc(asc)
        assert asc==before[2]
    temp.mkdir(parents=True,exist_ok=True)
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_HOTSPOT_TEST.ABK',bank)):
        with (temp/name).open('xb') as out:out.write(data)
        blob=sha1(f'blob {len(data)}'.encode()+b'\0'+data).hexdigest()
        print('S2F_CAMPAIGN',name,len(data),sha256(data).hexdigest(),blob,flush=True)
    assert protected()==before
    assert (ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes()==bank
    print('S2F_CAMPAIGN_PREPARED_NOT_ACTIVATED',flush=True)
if __name__=='__main__':main()
