#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Prepare S2g P1b campaign from exact S2f ASC/ABK, never activate."""
import argparse
from pathlib import Path
from hashlib import sha1,sha256
from verify_m19_s2f_delivery import verify_asc,ROOT
from verify_m19_s2e_delivery import verify_abk
from test_current_ram_log import verify as verify_log
from m19_s1_agsp_bank import parse_abk

def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)

def prepare(source,bank):
    verify_asc(source)
    verify_abk(bank)
    _,_,payload=parse_abk(bank)
    for group,width in enumerate((16,32,64)):
        for k in range(4):
            im=payload.image(1+group*8+2*k)
            assert (im.width,im.height,im.hotspot_x,im.hotspot_y)==(width,16,width//2,8)
            assert im.depth==(4 if k==3 else 2)
    text=source.decode('ascii')
    text=once(text,"' M19 S2f - fixed-width clipping, signed hotspots, 16/32/64px.",
        "' M19 S2g P1 - explicit pair order plus S2f regression.")
    text=once(text,"_EDGE=0 : _OX=0 : _OY=0 : _HOLD=0",
        "_EDGE=0 : _OX=0 : _OY=0 : _HOLD=0\n"
        "_L=0 : _LAYER_RC=-999 : _LAYER_SHOW=0 : _LAYER_MOVE=0\n"
        "_LAYER_BAD=0 : _LAYER_PALETTE=0 : _LAYER_MIGRATE=0 : _LAYER_BUSY=0")
    start="         For _J=1 To 3\n            If _ERR=0\n               _N=_IDS(_J) : _BASE=_BASES(_J)\n               _SY=24+_J*56\n               _SPRITE_RC=Aga Sprite(_N,32,_SY,_BASE)\n"
    replacement="""         ' Refuse invalid layers and palette mismatch before any Show.
         If _ERR=0
            _LAYER_RC=Aga Sprite(1,80,24,_BASES(1),-1)
            If _LAYER_RC=-210
               _LAYER_BAD=_LAYER_BAD+1
            Else
               _ERR=38
            End If
         End If
         If _ERR=0
            _LAYER_RC=Aga Sprite(1,80,24,_BASES(1),4)
            If _LAYER_RC=-210
               _LAYER_BAD=_LAYER_BAD+1
            Else
               _ERR=38
            End If
         End If
         If _ERR=0
            _LAYER_RC=Aga Sprite(1,80,24,1+_GROUP*8,2)
            If _LAYER_RC=-206
               _LAYER_PALETTE=_LAYER_PALETTE+1
            Else
               _ERR=39
            End If
         End If
         ' Reverse creation order: 6/7, 4/5, then 2/3.
         For _L=1 To 3
            If _ERR=0
               _J=4-_L
               _N=_IDS(_J) : _BASE=_BASES(_J)
               _SY=24+_J*56
               _SPRITE_RC=Aga Sprite(_N,32,_SY,_BASE,_J)
"""
    text=once(text,start,replacement)
    text=once(text,"                  _SHOWN=_SHOWN+1\n                  If _J=1",
        "                  _SHOWN=_SHOWN+1 : _LAYER_SHOW=_LAYER_SHOW+1\n                  If _L=1")
    text=once(text,"         Next _J\n         If _ERR=0\n            _FULL_RC=Aga Sprite(1,80,24,_BASES(1))",
        "         Next _L\n         If _ERR=0\n            _FULL_RC=Aga Sprite(1,80,24,_BASES(1))")
    marker="         _CHIP_CYCLE0=Chip Free : _FAST_CYCLE0=Fast Free\n         For _CYCLE=1 To 12"
    extra="""         ' Overlap the three pairs for visual priority verification.
         For _J=1 To 3
            If _ERR=0
               _N=_IDS(_J) : _BASE=_BASES(_J)
               _LAYER_RC=Aga Sprite(_N,144+_J*5,112+_J*3,_BASE,_J)
               If _LAYER_RC=1
                  _LAYER_MOVE=_LAYER_MOVE+1
               Else
                  _ERR=40
               End If
            End If
            If _ERR=0
               _L=(_J mod 3)+1
               _LAYER_RC=Aga Sprite(_N,20,20,_BASE,_L)
               If _LAYER_RC=-206
                  _LAYER_MIGRATE=_LAYER_MIGRATE+1
               Else
                  _ERR=41
               End If
            End If
            If _ERR=0
               _LAYER_RC=Aga Sprite(1,20,20,_BASE,_J)
               If _LAYER_RC=-206
                  _LAYER_BUSY=_LAYER_BUSY+1
               Else
                  _ERR=42
               End If
            End If
         Next _J
         If _ERR=0
            For _I=1 To 100
               Aga Wait Vbl
            Next _I
         End If
"""
    text=once(text,marker,extra+marker)
    text=once(text,"_SPRITE_RC=Aga Sprite(9,319+_WIDTH/2,136,_BASES(2))",
        "_SPRITE_RC=Aga Sprite(9,319+_WIDTH/2,136,_BASES(2),2)")
    text=once(text,"_ERASE_RC=Aga Sprite(_N,_OX+_WIDTH/2,_OY+8,_BASE)",
        "_ERASE_RC=Aga Sprite(_N,_OX+_WIDTH/2,_OY+8,_BASE,_J)")
    text=once(text,'               _RESULT=1\n               _VERDICT$="PASS_S2F_CLIPPING"',
        '               If _LAYER_SHOW=27 and _LAYER_MOVE=27 and _LAYER_BAD=18 and _LAYER_PALETTE=9 and _LAYER_MIGRATE=27 and _LAYER_BUSY=27\n'
        '                  _RESULT=1\n                  _VERDICT$="PASS_S2G_PRIORITY"\n'
        '               Else\n                  _ERR=43\n               End If')
    text=once(text,'Print #1,"SOURCE_TAG M19_S2F_CLIPPING_V1"',
        'Print #1,"SOURCE_TAG M19_S2G_PRIORITY_V1"\n'
        'Print #1,"LAYER_SHOW ";_LAYER_SHOW;" LAYER_MOVE ";_LAYER_MOVE;" BAD ";_LAYER_BAD\n'
        'Print #1,"LAYER_PALETTE ";_LAYER_PALETTE;" MIGRATION ";_LAYER_MIGRATE;" BUSY ";_LAYER_BUSY;" RC ";_LAYER_RC')
    text=text.replace("RAM:M19_S2F_","RAM:M19_S2G_")
    assert max(map(len,text.splitlines()))<=220
    verify_log(text)
    return text.encode('ascii')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--temp',type=Path,required=True)
    a=p.parse_args()
    dst=a.temp.resolve()
    assert not dst.is_relative_to(ROOT)
    from verify_m19_s2g_delivery import pre_s2g_pair
    from build_m19_s2g_in_memory import protected
    before=protected()
    source=pre_s2g_pair(before)[2]
    bank=(ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK').read_bytes()
    asc=prepare(source,bank)
    assert asc==prepare(source,bank)
    dst.mkdir(parents=True,exist_ok=True)
    with (dst/'SPRITE_PUBLIC.asc').open('xb') as f:f.write(asc)
    print('S2G_ASC_PREPARED',len(asc),sha256(asc).hexdigest(),
          sha1(f'blob {len(asc)}'.encode()+b'\0'+asc).hexdigest(),flush=True)

if __name__=='__main__':main()
