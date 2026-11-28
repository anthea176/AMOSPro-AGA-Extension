#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Prepare future S2c mixed public campaign, never activate it."""
import argparse
from hashlib import sha256
from pathlib import Path
from build_m19_s2c_in_memory import build_s2c,protected
from verify_m19_s2r_delivery import verify_asc
from prepare_m19_s2a_campaign import identify,replace
from test_m19_s2c_mixed_public_cpu import mixed_bank,RGB
from m19_s1_agsp_bank import make_abk,parse_abk
from test_current_ram_log import verify as verify_log

def prepare(source):
    verify_asc(source)
    raw=mixed_bank()
    abk=make_abk(29,raw)
    bank,flags,payload=parse_abk(abk)
    assert bank==29 and flags==1 and len(payload.images)==8
    for k in range(4):
        a,b=payload.image(3+2*k),payload.image(4+2*k)
        assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
        assert (a.width,a.height,a.depth)==(16,16,2 if k<3 else 4)
        assert a.planes!=b.planes
    s=source.decode('ascii')
    s=replace(s,s.splitlines()[0],"' M19 S2c - simple/mixed/attached, capture and full lifecycle.")
    s=s.replace('M19_S2R_','M19_S2C_').replace('PASS_S2R_REPARTITION','PASS_S2C_MIXED').replace('M19_S2C_REPARTITION_V1','M19_S2C_MIXED_V1')
    s=replace(s,'AGSP_S2B_MULTI.ABK','AGSP_S2C_MIXED.ABK')
    s=replace(s,'Length(29)<>992','Length(29)<>'+str(len(raw)))
    s=replace(s,'_PIC_OWN=0 : _PIC_VER=0','_CAP_OWN=0 : _CAP_OK=0 : _CAP_REFUSED=0 : _CAP_FREE=-999 : _CAP_PTR=0\n_PIC_OWN=0 : _PIC_VER=0')
    s=replace(s,'Dim _CHIP_CLOSED(2),_FAST_CLOSED(2)','Dim _CHIP_CLOSED(3),_FAST_CLOSED(3)')
    s=replace(s,'For _SCREEN_NO=1 To 2','For _SCREEN_NO=1 To 3')
    a=s.index('         _P0=Aga Palette Set(0,12,20,30)')
    b=s.index('      End If\n      If _ERR=0\n         _PIC_RC=',a)
    palette=['         _P0=Aga Palette Set(0,12,20,30)',
             '         If _P0<>1','            _ERR=8','         End If',
             '         _P0=Aga Palette Set(16,200,100,51)',
             '         If _P0<>1','            _ERR=8','         End If']
    for i in range(15):
        r,g,bv=RGB[3*i:3*i+3]
        palette.extend([f'         _P0=Aga Palette Set({17+i},{r},{g},{bv})',
                        '         If _P0<>1','            _ERR=8','         End If'])
    s=s[:a]+'\n'.join(palette)+'\n'+s[b:]
    anchor='      If _ERR=0\n         _OK=Aga Mouse Cursor(0)'
    s=replace(s,anchor,'''      If _ERR=0
         _OK=Aga Blit Fill(10,200,16,16,0)
         If _OK<>1
            _ERR=25
         End If
         For _I=1 To 15
            If _ERR=0
               _OK=Aga Blit Fill(10+_I,200,1,16,16+_I)
               If _OK<>1
                  _ERR=25
               End If
            End If
         Next _I
      End If
      If _ERR=0
         Aga Sprite Bank 30
         If Length(30)<>0
            _CAP_OWN=1
         End If
         If Length(30)<>32
            _ERR=26
         End If
      End If
      If _ERR=0
         Get Aga Sprite 1,10,200,25,200,0
         If Length(30)<>136
            _ERR=27
         Else
            _CAP_PTR=Start(30)
            If Deek(_CAP_PTR+8)<>1 or Leek(_CAP_PTR+24)<>2 or Deek(_CAP_PTR+38)<>4
               _ERR=27
            Else
               _CAP_OK=_CAP_OK+1
            End If
         End If
      End If
      If _ERR=0
         Get Aga Sprite 2,10,200,25,215,0
         If Length(30)<>360
            _ERR=28
         Else
            _CAP_PTR=Start(30)
            If Deek(_CAP_PTR+8)<>2 or Leek(_CAP_PTR+24)<>3 or Deek(_CAP_PTR+86)<>4
               _ERR=28
            Else
               _CAP_OK=_CAP_OK+1
            End If
         End If
      End If
      If _ERR=0
         _OK=Aga Blit Fill(10,200,1,16,16)
         If _OK<>1
            _ERR=29
         Else
            Get Aga Sprite 3,10,200,25,215,0
            If Length(30)<>360
               _ERR=29
            Else
               _CAP_PTR=Start(30)
               If Deek(_CAP_PTR+8)<>2 or Leek(_CAP_PTR+24)<>3
                  _ERR=29
               Else
                  _CAP_REFUSED=_CAP_REFUSED+1
               End If
            End If
         End If
      End If
      If _CAP_OWN=1
         _CAP_FREE=Aga Sprite Bank Free(30)
         If _CAP_FREE<>1
            _CLEAN_ERR=_CLEAN_ERR or 64
         Else
            Erase 30
            If Length(30)<>0
               _CLEAN_ERR=_CLEAN_ERR or 64
            Else
               _CAP_OWN=0
            End If
         End If
      End If
'''+anchor)
    s=replace(s,'         _ATTEMPT=1 : _ID2=42 : _IDS(2)=42','''         _ATTEMPT=1 : _ID2=42 : _IDS(2)=42
         _BASES(1)=3 : _BASES(2)=5 : _BASES(3)=7
         If _SCREEN_NO=2
            _BASES(2)=9
         End If
         If _SCREEN_NO=3
            _BASES(1)=9 : _BASES(2)=9 : _BASES(3)=9
         End If''')
    s=replace(s,'_SPRITE_RC=Aga Sprite(9,160,136,5)','_SPRITE_RC=Aga Sprite(9,160,136,_BASES(2))')
    s=replace(s,'Next _SCREEN_NO\nIf _PIC_OWN=1','''Next _SCREEN_NO
If _CAP_OWN=1
   _CAP_FREE=Aga Sprite Bank Free(30)
   If _CAP_FREE=1
      Erase 30
      If Length(30)=0
         _CAP_OWN=0
      End If
   End If
   If _CAP_OWN=1
      _CLEAN_ERR=_CLEAN_ERR or 64
   End If
End If
If _PIC_OWN=1''')
    s=replace(s,'_SHOWN=8 and _CHANGED=300 and _MOVED=300 and _OFF_COUNT=2 and _AUTO_COUNT=6 and _FULL_COUNT=2','_SHOWN=12 and _CHANGED=450 and _MOVED=450 and _OFF_COUNT=3 and _AUTO_COUNT=9 and _FULL_COUNT=3')
    s=replace(s,'_OPENED=2 and _CLOSED=2 and _PIC_CAP=4 and _PIC_META=4 and _PIC_NEG=4 and _PIC_DRAW=4 and _PIC_OWN=0','_OPENED=3 and _CLOSED=3 and _PIC_CAP=6 and _PIC_META=6 and _PIC_NEG=6 and _PIC_DRAW=6 and _PIC_OWN=0 and _CAP_OK=6 and _CAP_REFUSED=3 and _CAP_OWN=0')
    s=replace(s,'For _I=1 To 2\n   Print #1,"SCREEN "','For _I=1 To 3\n   Print #1,"SCREEN "')
    s=replace(s,'Print #1,"CHIP_CYCLE_LOSS "', 'Print #1,"AGSP_CAPTURED ";_CAP_OK;" REFUSED ";_CAP_REFUSED;" FREE_RC ";_CAP_FREE;" OWN ";_CAP_OWN\nPrint #1,"CHIP_CYCLE_LOSS "')
    assert max(map(len,s.splitlines()))<=220
    verify_log(s)
    return s.encode('ascii'),abk

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--temp',required=True,type=Path)
    args=p.parse_args()
    before=protected()
    from verify_m19_s2c_delivery import pre_s2c_pair, S2C_SHA, S2CD_SHA, verify_asc as verify_s2c_asc, verify_abk as verify_s2c_abk
    parent=pre_s2c_pair(before)
    asc,abk=prepare(parent[2])
    assert (asc,abk)==prepare(parent[2])
    verify_s2c_asc(asc)
    verify_s2c_abk(abk)
    if sha256(before[0]).hexdigest() in (S2C_SHA,S2CD_SHA):
        assert asc==before[2] and abk==(Path(__file__).resolve().parents[1]/'tests/current/AGSP_S2C_MIXED.ABK').read_bytes()
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_S2C_MIXED.ABK',abk)):
        with (args.temp/name).open('xb') as out:out.write(data)
    # Emit generated campaign identity before building, but never install.
    identify('S2C_ASC',asc);identify('S2C_ABK',abk)
    image,info=build_s2c(args.vasm,diagnostic=sha256(before[0]).hexdigest()==S2CD_SHA)
    assert sha256(image).hexdigest()==info['sha256']
    identify('S2C_LIB',image)
    assert protected()==before
if __name__=='__main__':main()
