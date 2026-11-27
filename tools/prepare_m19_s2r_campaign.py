#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Generate future S2r ASC from exact validated S2b, in CI temporary space.
No active ASC/ABK or installable library writes."""
import argparse
from hashlib import sha256
from pathlib import Path
from build_m19_s2r_in_memory import build_s2r, protected, ROOT
from verify_m19_s2b_delivery import verify_asc, verify_abk
from prepare_m19_s2a_campaign import identify, replace
from test_current_ram_log import verify as verify_log

EXPECTED='7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a'

def prepare(source):
    verify_asc(source)
    s=source.decode('ascii')
    s=replace(s,s.splitlines()[0],
        "' M19 S2r - exact S2b regression plus both relocated AGAPIC functions.")
    s=s.replace('M19_S2B_','M19_S2R_')
    s=replace(s,'M19_S2R_MULTI_SPRITE_V1','M19_S2R_REPARTITION_V1')
    s=replace(s,'PASS_S2B_MULTI_SPRITE','PASS_S2R_REPARTITION')
    s=replace(s,'_ERR=0 : _CLEAN_ERR=0 : _RESULT=0 : _BANK_OWN=0',
        '''_ERR=0 : _CLEAN_ERR=0 : _RESULT=0 : _BANK_OWN=0
_PIC_OWN=0 : _PIC_VER=0 : _PIC_RC=-999 : _PIC_DRAW_RC=-999
_PIC_CAP=0 : _PIC_META=0 : _PIC_NEG=0 : _PIC_DRAW=0 : _PIC_LEN=0
_PIC_W=0 : _PIC_H=0 : _PIC_D=0 : _PIC_COL=0 : _PIC_MODE=0
_PIC_BAD=-999 : _PIC_DUP=-999 : _PIC_EXPECT_COL=0 : _PIC_EXPECT_MODE=0''')
    s=replace(s,'If Length(29)<>0\n   _ERR=2\nEnd If',
        'If Length(29)<>0\n   _ERR=2\nEnd If\nIf Length(30)<>0\n   _ERR=17\nEnd If')
    anchor='      If _ERR=0\n         _OK=Aga Mouse Cursor(0)'
    s=replace(s,anchor,'''      If _ERR=0
         _PIC_RC=Aga Blit Fill(5,5,19,9,21)
         If _PIC_RC<>1
            _ERR=18
         End If
      End If
      For _PIC_VER=1 To 2
         If _ERR=0
            _PIC_RC=Aga Bank Image Capture(30,5,5,19,9,-1,_PIC_VER)
            _PIC_LEN=Length(30)
            If _PIC_LEN<>0
               _PIC_OWN=1
            End If
            If _PIC_RC<>1 or _PIC_OWN<>1
               _ERR=19
            Else
               _PIC_CAP=_PIC_CAP+1
            End If
         End If
         If _ERR=0
            _PIC_W=Aga Bank Image Info(30,1)
            _PIC_H=Aga Bank Image Info(30,2)
            _PIC_D=Aga Bank Image Info(30,3)
            _PIC_COL=Aga Bank Image Info(30,4)
            _PIC_MODE=Aga Bank Image Info(30,5)
            _PIC_EXPECT_COL=0 : _PIC_EXPECT_MODE=0
            If _PIC_VER=2
               _PIC_EXPECT_COL=256 : _PIC_EXPECT_MODE=$21000
            End If
            If _PIC_W<>19 or _PIC_H<>9 or _PIC_D<>8 or _PIC_COL<>_PIC_EXPECT_COL or _PIC_MODE<>_PIC_EXPECT_MODE
               _ERR=20
            Else
               _PIC_META=_PIC_META+1
            End If
         End If
         If _ERR=0
            _PIC_BAD=Aga Bank Image Info(30,6)
            _PIC_DUP=Aga Bank Image Capture(30,5,5,19,9,-1,_PIC_VER)
            If _PIC_BAD<>-1 or _PIC_DUP<>0 or Length(30)<>_PIC_LEN
               _ERR=21
            Else
               _PIC_NEG=_PIC_NEG+1
            End If
         End If
         If _ERR=0
            _PIC_DRAW_RC=Aga Bank Image Draw(30,40+_PIC_VER*40,5,0)
            If _PIC_DRAW_RC<>1
               _ERR=22
            Else
               _PIC_DRAW=_PIC_DRAW+1
            End If
         End If
         If _PIC_OWN=1
            Erase 30
            If Length(30)<>0
               _CLEAN_ERR=_CLEAN_ERR or 32
               _ERR=23
            Else
               _PIC_OWN=0
            End If
         End If
      Next _PIC_VER
      If _ERR=0 and _CLEAN_ERR=0
         _OK=Aga Swap
         If _OK<>1
            _ERR=24
         Else
            Aga Wait Vbl
         End If
      End If
'''+anchor)
    s=replace(s,'Next _SCREEN_NO\nIf _BANK_OWN=1',
        '''Next _SCREEN_NO
If _PIC_OWN=1
   Erase 30
   If Length(30)<>0
      _CLEAN_ERR=_CLEAN_ERR or 32
   Else
      _PIC_OWN=0
   End If
End If
If _BANK_OWN=1''')
    s=replace(s,'If _OPENED=2 and _CLOSED=2',
        'If _OPENED=2 and _CLOSED=2 and _PIC_CAP=4 and _PIC_META=4 and _PIC_NEG=4 and _PIC_DRAW=4 and _PIC_OWN=0')
    s=replace(s,'Print #1,"CHIP_CYCLE_LOSS ";_CHIP_LOSS;',
        '''Print #1,"AGAPIC_CAPTURE ";_PIC_CAP;" META ";_PIC_META;" NEGATIVE ";_PIC_NEG;" DRAW ";_PIC_DRAW
Print #1,"AGAPIC_W ";_PIC_W;" H ";_PIC_H;" DEPTH ";_PIC_D;" COLORS ";_PIC_COL;" MODE ";_PIC_MODE
Print #1,"AGAPIC_RC ";_PIC_RC;" INFO_BAD ";_PIC_BAD;" DUP_RC ";_PIC_DUP;" DRAW_RC ";_PIC_DRAW_RC;" OWN ";_PIC_OWN
Print #1,"CHIP_CYCLE_LOSS ";_CHIP_LOSS;''')
    assert 'AGSP_S2B_MULTI.ABK' in s and 'AGSP_S2R_MULTI.ABK' not in s
    assert max(map(len,s.splitlines()))<=220
    verify_log(s)
    return s.encode('ascii')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--temp',required=True,type=Path)
    a=p.parse_args()
    before=protected()
    bank=(ROOT/'tests/current/AGSP_S2B_MULTI.ABK').read_bytes()
    verify_abk(bank)
    image,meta=build_s2r(a.vasm)
    assert sha256(image).hexdigest()==EXPECTED and meta['sha256']==EXPECTED
    from verify_m19_s2r_delivery import pre_s2r_pair, verify_asc as verify_s2r_asc
    parent=pre_s2r_pair(before)
    asc=prepare(parent[2])
    assert asc==prepare(parent[2])
    verify_s2r_asc(asc)
    with (a.temp/'SPRITE_PUBLIC.asc').open('xb') as f:f.write(asc)
    assert protected()==before
    assert (ROOT/'tests/current/AGSP_S2B_MULTI.ABK').read_bytes()==bank
    identify('S2R_LIB',image)
    identify('S2R_ASC',asc)
    identify('S2R_ABK',bank)

if __name__=='__main__':main()
