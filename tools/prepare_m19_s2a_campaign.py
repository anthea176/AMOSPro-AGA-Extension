#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Prepare the exact S2a functional ASC and bank; no active file writes."""
import argparse
import base64
from hashlib import sha1, sha256
from pathlib import Path
from build_m19_s2a_in_memory import build_s2a, protected
from verify_m19_s1p2m_delivery import verify_asc
from test_m19_s2a_public_gate_a import animation_bank
from m19_s1_agsp_bank import make_abk, parse_abk, s0_interleaved_image
from test_current_ram_log import verify as verify_log

EXPECTED='1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2'
def replace(s,old,new):
    assert s.count(old)==1,old
    return s.replace(old,new)

def prepare(source):
    verify_asc(source)
    abk=make_abk(29,animation_bank())
    bank,flags,parsed=parse_abk(abk)
    assert bank==29 and flags==1
    a,b=parsed.image(3),parsed.image(4)
    assert (a.width,a.height,a.depth,a.palette)==(b.width,b.height,b.depth,b.palette)
    assert a.planes!=b.planes and a.palette[3:12]==bytes.fromhex('ff462824dc751a73ff')
    text=source.decode('ascii')
    text=replace(text,text.splitlines()[0],
                 "' M19 S2a-P1 - 100 hot frame changes, 2 active closes, no Off between frames.")
    text=text.replace('M19_P2M_','M19_S2A_').replace('AGSP_S1P1E_FINAL.ABK','AGSP_S2A_ANIMATION.ABK')
    text=replace(text,'Length(29)<>512','Length(29)<>'+str(len(abk)-20))
    text=replace(text,'Dim _CHIP_CLOSED(10),_FAST_CLOSED(10)',
                 '_CHANGED=0 : _CHANGE_RC=-999 : _IMAGE=3 : _COUNT=0\nDim _CHIP_CLOSED(2),_FAST_CLOSED(2)')
    text=replace(text,'For _SCREEN_NO=1 To 10','For _SCREEN_NO=1 To 2')
    start=text.index('         _CHIP_CYCLE0=Chip Free')
    end=text.index('      If _OPEN=1\n         If _ERR<>0 and _ATTEMPT=1',start)
    text=text[:start]+'''         _CHIP_CYCLE0=Chip Free : _FAST_CYCLE0=Fast Free
         _ATTEMPT=1 : _IMAGE=3
         _SPRITE_RC=Aga Sprite(1,32,112,_IMAGE)
         If _SPRITE_RC<>1
            _ERR=10
         Else
            _SHOWN=_SHOWN+1
            For _I=1 To 25
               Aga Wait Vbl
            Next _I
         End If
         _COUNT=47+_SCREEN_NO*2
         For _CYCLE=1 To _COUNT
            If _ERR=0
               _IMAGE=7-_IMAGE
               _CHANGE_RC=Aga Sprite(1,32+_CYCLE*4,112,_IMAGE)
               If _CHANGE_RC<>1
                  _ERR=11
               Else
                  _CHANGED=_CHANGED+1
                  _MOVE_RC=Aga Sprite(1,34+_CYCLE*4,112,_IMAGE)
                  If _MOVE_RC<>1
                     _ERR=12
                  Else
                     _MOVED=_MOVED+1
                     For _I=1 To 3
                        Aga Wait Vbl
                     Next _I
                  End If
               End If
            End If
         Next _CYCLE
         If _ERR=0
            If _SCREEN_NO=1
               _OFF_RC=Aga Sprite Off(1)
               If _OFF_RC<>1
                  _ERR=13
               Else
                  _OFF_COUNT=_OFF_COUNT+1 : _ATTEMPT=0
                  _DC=_CHIP_CYCLE0-Chip Free
                  _DF=_FAST_CYCLE0-Fast Free
                  If _DC>_CHIP_LOSS
                     _CHIP_LOSS=_DC
                  End If
                  If _DF>_FAST_LOSS
                     _FAST_LOSS=_DF
                  End If
                  _SPRITE_RC=Aga Sprite(1,64,112,3)
                  If _SPRITE_RC<>1
                     _ERR=15
                  Else
                     _ATTEMPT=1 : _SHOWN=_SHOWN+1
                  End If
               End If
            End If
         End If
         If _ERR=0
            _AUTO_COUNT=_AUTO_COUNT+1
            For _I=1 To 25
               Aga Wait Vbl
            Next _I
         End If
      End If
'''+text[end:]
    text=replace(text,'_SHOWN=100 and _MOVED=100 and _OFF_COUNT=100 and _AUTO_COUNT=10',
                 '_SHOWN=3 and _CHANGED=100 and _MOVED=100 and _OFF_COUNT=1 and _AUTO_COUNT=2')
    text=replace(text,'_OPENED=10 and _CLOSED=10','_OPENED=2 and _CLOSED=2')
    text=replace(text,'_CHIP_LOSS=0 and _FAST_LOSS=0 and _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0',
                 '_CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0 and _CHIP0=_CHIP1 and _FAST0=_FAST1')
    text=replace(text,'PASS_FUNCTIONAL_LIFECYCLE','PASS_S2A_FRAME_CHANGE')
    text=replace(text,'M19_S1P2M_FUNCTIONAL_V1','M19_S2A_FRAME_CHANGE_V1')
    text=replace(text,'Print #1,"SHOWN ";_SHOWN;', 'Print #1,"CHANGED ";_CHANGED;" CHANGE_RC ";_CHANGE_RC\nPrint #1,"SHOWN ";_SHOWN;')
    text=replace(text,'For _I=1 To 10\n   Print #1,"SCREEN "','For _I=1 To 2\n   Print #1,"SCREEN "')
    text=replace(text,'_P1=Aga Palette Set(21,255,70,40)','_P1=Aga Palette Set(21,255,70,40)')
    # The exact model palette is ff4628 24dc75 1a73ff.
    assert 'Aga Palette Set(21,255,70,40)' in text
    assert 'Aga Palette Set(22,36,220,117)' in text
    assert 'Aga Palette Set(23,26,115,255)' in text
    verify_log(text)
    assert max(map(len,text.splitlines()))<=220
    assert text.count('Aga Sprite Off(1)')==2
    return text.encode('ascii'),abk

def identify(label,data):
    digest=sha256(data).hexdigest()
    blob=sha1(f'blob {len(data)}'.encode()+b'\0'+data).hexdigest()
    print(label+'_IDENTITY',len(data),digest,blob,flush=True)
    encoded=base64.b64encode(data).decode('ascii')
    for i,at in enumerate(range(0,len(encoded),2048)):
        print(label+'_CHUNK',i,encoded[at:at+2048],flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--temp',required=True,type=Path)
    a=p.parse_args()
    before=protected()
    image,info=build_s2a(a.vasm)
    assert info['sha256']==EXPECTED
    asc,abk=prepare(before[2])
    for name,data in (('SPRITE_PUBLIC.asc',asc),('AGSP_S2A_ANIMATION.ABK',abk)):
        with (a.temp/name).open('xb') as f:f.write(data)
    assert protected()==before
    identify('S2A_LIB',image)
    identify('S2A_ASC',asc)
    identify('S2A_ABK',abk)

if __name__=='__main__':main()
