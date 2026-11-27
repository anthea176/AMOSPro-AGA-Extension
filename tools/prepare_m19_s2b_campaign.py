#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Prepare S2b exact candidate and future single ASC/ABK outside repository."""
import argparse
from hashlib import sha256
from pathlib import Path
from build_m19_s2b_in_memory import build_s2b,protected
from verify_m19_s2a_delivery import verify_asc
from prepare_m19_s2a_campaign import identify,replace
from test_m19_s2b_public_gate_a import multi_bank,PALETTES
from m19_s1_agsp_bank import make_abk,parse_abk
from test_current_ram_log import verify as verify_log

def prepare(source):
    verify_asc(source)
    abk=make_abk(29,multi_bank())
    bank,flags,payload=parse_abk(abk)
    assert bank==29 and flags==1 and len(payload.images)==6
    for k,pal in enumerate(PALETTES):
        a,b=payload.image(3+2*k),payload.image(4+2*k)
        assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
        assert (a.width,a.height,a.depth,a.palette)==(16,16,2,pal)
        assert a.planes!=b.planes
    text=source.decode('ascii')
    text=replace(text,text.splitlines()[0],
                 "' M19 S2b - 3 independent sprites, 300 changes, targeted Off and 2 active closes.")
    text=text.replace('M19_S2A_','M19_S2B_').replace('AGSP_S2A_ANIMATION.ABK','AGSP_S2B_MULTI.ABK')
    text=replace(text,'Length(29)<>352','Length(29)<>'+str(len(abk)-20))
    text=replace(text,'_CHANGED=0 : _CHANGE_RC=-999 : _IMAGE=3 : _COUNT=0',
                 '_CHANGED=0 : _CHANGE_RC=-999 : _FULL_RC=-999 : _FULL_COUNT=0\n_ID2=42 : _J=0 : _FRAME=0 : _N=0 : _SX=0 : _SY=0 : _BASE=0\nDim _IDS(3),_BASES(3)\n_IDS(1)=17 : _IDS(2)=42 : _IDS(3)=64\n_BASES(1)=3 : _BASES(2)=5 : _BASES(3)=7')
    text=replace(text,'         If _P0<>1 or _P1<>1 or _P2<>1 or _P3<>1\n            _ERR=8\n         End If',
                 '''         If _P0<>1 or _P1<>1 or _P2<>1 or _P3<>1
            _ERR=8
         End If
         _P1=Aga Palette Set(25,248,216,90)
         _P2=Aga Palette Set(26,52,197,224)
         _P3=Aga Palette Set(27,104,73,187)
         If _P1<>1 or _P2<>1 or _P3<>1
            _ERR=8
         End If
         _P1=Aga Palette Set(29,255,129,201)
         _P2=Aga Palette Set(30,107,195,79)
         _P3=Aga Palette Set(31,254,254,254)
         If _P1<>1 or _P2<>1 or _P3<>1
            _ERR=8
         End If''')
    start=text.index('         _CHIP_CYCLE0=Chip Free')
    end=text.index('      If _OPEN=1\n         If _ERR<>0 and _ATTEMPT=1',start)
    text=text[:start]+'''         _ATTEMPT=1 : _ID2=42 : _IDS(2)=42
         For _J=1 To 3
            If _ERR=0
               _N=_IDS(_J) : _BASE=_BASES(_J)
               _SY=24+_J*56
               _SPRITE_RC=Aga Sprite(_N,32,_SY,_BASE)
               If _SPRITE_RC<>1
                  _ERR=10
               Else
                  _SHOWN=_SHOWN+1
               End If
            End If
         Next _J
         If _ERR=0
            _FULL_RC=Aga Sprite(1,16,24,3)
            If _FULL_RC=-206
               _FULL_COUNT=_FULL_COUNT+1
            Else
               _ERR=16
            End If
         End If
         If _ERR=0
            For _I=1 To 25
               Aga Wait Vbl
            Next _I
         End If
         _CHIP_CYCLE0=Chip Free : _FAST_CYCLE0=Fast Free
         For _CYCLE=1 To 50
            If _ERR=0
               _FRAME=_CYCLE mod 2
               For _J=1 To 3
                  If _ERR=0
                     _N=_IDS(_J) : _BASE=_BASES(_J)
                     _SX=32+_CYCLE*4 : _SY=24+_J*56
                     If _J=2
                        _SX=240-_CYCLE*4
                     End If
                     _CHANGE_RC=Aga Sprite(_N,_SX,_SY,_BASE+_FRAME)
                     If _CHANGE_RC<>1
                        _ERR=11
                     Else
                        _CHANGED=_CHANGED+1
                        _MOVE_RC=Aga Sprite(_N,_SX+2,_SY,_BASE+_FRAME)
                        If _MOVE_RC<>1
                           _ERR=12
                        Else
                           _MOVED=_MOVED+1
                        End If
                     End If
                  End If
               Next _J
               _DC=_CHIP_CYCLE0-Chip Free
               _DF=_FAST_CYCLE0-Fast Free
               If _DC>_CHIP_LOSS
                  _CHIP_LOSS=_DC
               End If
               If _DF>_FAST_LOSS
                  _FAST_LOSS=_DF
               End If
            End If
         Next _CYCLE
         If _ERR=0
            _OFF_RC=Aga Sprite Off(42)
            If _OFF_RC<>1
               _ERR=13
            Else
               _OFF_COUNT=_OFF_COUNT+1
               For _I=1 To 25
                  Aga Wait Vbl
               Next _I
               _SPRITE_RC=Aga Sprite(9,160,136,5)
               If _SPRITE_RC<>1
                  _ERR=15
               Else
                  _ID2=9 : _SHOWN=_SHOWN+1
               End If
            End If
         End If
         If _ERR=0
            _AUTO_COUNT=_AUTO_COUNT+3
            For _I=1 To 25
               Aga Wait Vbl
            Next _I
         End If
      End If
'''+text[end:]
    text=replace(text,'''            _OFF_RC=Aga Sprite Off(1)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If''','''            _OFF_RC=Aga Sprite Off(17)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If
            _OFF_RC=Aga Sprite Off(_ID2)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If
            _OFF_RC=Aga Sprite Off(64)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If
            _OFF_RC=Aga Sprite Off(1)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If''')
    text=replace(text,'_SHOWN=3 and _CHANGED=100 and _MOVED=100 and _OFF_COUNT=1 and _AUTO_COUNT=2',
                 '_SHOWN=8 and _CHANGED=300 and _MOVED=300 and _OFF_COUNT=2 and _AUTO_COUNT=6 and _FULL_COUNT=2')
    text=replace(text,'M19_S2B_FRAME_CHANGE_V1','M19_S2B_MULTI_SPRITE_V1')
    text=replace(text,'PASS_S2A_FRAME_CHANGE','PASS_S2B_MULTI_SPRITE')
    text=replace(text,'Print #1,"CHANGED ";_CHANGED;',
                 'Print #1,"SATURATION ";_FULL_COUNT;" FULL_RC ";_FULL_RC\nPrint #1,"CHANGED ";_CHANGED;')
    verify_log(text)
    assert max(map(len,text.splitlines()))<=220
    return text.encode('ascii'),abk

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--temp',required=True,type=Path)
    args=p.parse_args()
    before=protected()
    image,info=build_s2b(args.vasm)
    asc,abk=prepare(before[2])
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_S2B_MULTI.ABK',abk)):
        with (args.temp/name).open('xb') as f:f.write(data)
    assert protected()==before
    identify('S2B_LIB',image)
    identify('S2B_ASC',asc)
    identify('S2B_ABK',abk)

if __name__=='__main__':main()
