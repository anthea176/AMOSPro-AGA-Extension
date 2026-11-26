#!/usr/bin/env python3
"""Prepare the future single functional ASC in a temporary path, never install."""
import argparse
from hashlib import sha256
from pathlib import Path

PARENT='25a50fd84962dcdd0a52a45d496ad3413676d37aa4b3df4c2d74391d18c4a89e'

def prepare(source):
    assert sha256(source).hexdigest()==PARENT
    text=source.decode('ascii')
    header=text[text.index('Set Buffer 20'):text.index('Print "1 = DISPLAY AFTER RESET"')]
    header=header.replace('M19_P2LC','M19_P2M')
    setup=text[text.index('If _ERR=0\n   _OPEN=Aga Screen Open'):text.index('If _ERR=0\n   Aga Sprite Bank 29')]
    setup=''.join('      '+line+'\n' for line in setup.splitlines())
    s="' M19 S1-P2m - functional lifecycle: 100 Off/re-show and 10 active Close.\n"+header+'''_ERR=0 : _CLEAN_ERR=0 : _RESULT=0 : _BANK_OWN=0
_OPENED=0 : _CLOSED=0 : _SHOWN=0 : _MOVED=0 : _OFF_COUNT=0 : _AUTO_COUNT=0
_SPRITE_RC=-999 : _MOVE_RC=-999 : _OFF_RC=-999 : _FREE_RC=-999 : _CURSOR_RC=-999
_CPU=Deek(Leek(4)+296) and $FFFF
_SCREEN_NO=0 : _CYCLE=0 : _OPEN=0 : _HIDDEN=0 : _ATTEMPT=0
_CHIP_CYCLE0=0 : _FAST_CYCLE0=0 : _CHIP_LOSS=0 : _FAST_LOSS=0
_CHIP_SCREEN_LOSS=0 : _FAST_SCREEN_LOSS=0 : _FIRST_CHIP=0 : _FIRST_FAST=0
_DC=0 : _DF=0 : _OK=0 : _I=0 : _P0=0 : _P1=0 : _P2=0 : _P3=0
Dim _CHIP_CLOSED(10),_FAST_CLOSED(10)
_CHIP0=Chip Free : _FAST0=Fast Free
If Aga Detect=0
   _ERR=1
End If
If Length(29)<>0
   _ERR=2
End If
If _ERR=0
   Trap Load "AGSP_S1P1E_FINAL.ABK",29
   _IO=Errtrap
   If Length(29)<>0
      _BANK_OWN=1
   End If
   If _IO<>0 or Length(29)<>512
      _ERR=3
   End If
End If
For _SCREEN_NO=1 To 10
   If _ERR=0 and _CLEAN_ERR=0
      _OPEN=0 : _HIDDEN=0 : _ATTEMPT=0
'''+setup+'''      If _OPEN=1
         _OPENED=_OPENED+1
      End If
      If _ERR=0
         Aga Sprite Bank 29
         Amos To Back
         Aga Wait Vbl
         _CHIP_CYCLE0=Chip Free : _FAST_CYCLE0=Fast Free
         For _CYCLE=1 To 10
            If _ERR=0
               _ATTEMPT=1
               _SPRITE_RC=Aga Sprite(1,32,112,3)
               If _SPRITE_RC<>1
                  _ERR=10
               Else
                  _SHOWN=_SHOWN+1
                  Aga Wait Vbl
                  _MOVE_RC=Aga Sprite(1,32+_CYCLE*10,112,3)
                  If _MOVE_RC<>1
                     _ERR=11
                  Else
                     _MOVED=_MOVED+1
                     Aga Wait Vbl
                  End If
               End If
               _OFF_RC=Aga Sprite Off(1)
               If _OFF_RC=1
                  _ATTEMPT=0
                  _OFF_COUNT=_OFF_COUNT+1
               Else
                  If _ERR=0
                     _ERR=12
                  End If
                  _CLEAN_ERR=_CLEAN_ERR or 1
               End If
               Aga Wait Vbl
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
      End If
      If _ERR=0
         _ATTEMPT=1
         _SPRITE_RC=Aga Sprite(1,64,112,3)
         If _SPRITE_RC<>1
            _ERR=13
         Else
            _AUTO_COUNT=_AUTO_COUNT+1
            Aga Wait Vbl
         End If
      End If
      If _OPEN=1
         If _ERR<>0 and _ATTEMPT=1
            _OFF_RC=Aga Sprite Off(1)
            If _OFF_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 1
            End If
         End If
         If _HIDDEN=1
            _CURSOR_RC=Aga Mouse Cursor(1)
            If _CURSOR_RC<>1
               _CLEAN_ERR=_CLEAN_ERR or 2
            End If
         End If
         Aga Screen Close
         Amos To Front
         For _I=1 To 4
            Wait Vbl
         Next _I
         If Aga Mouse X=-1
            _CLOSED=_CLOSED+1
         Else
            _CLEAN_ERR=_CLEAN_ERR or 4
         End If
         _FREE_RC=Aga Sprite Bank Free(29)
         If _FREE_RC<>1
            _CLEAN_ERR=_CLEAN_ERR or 8
         End If
         _CHIP_CLOSED(_SCREEN_NO)=Chip Free
         _FAST_CLOSED(_SCREEN_NO)=Fast Free
         If _SCREEN_NO=1
            _FIRST_CHIP=_CHIP_CLOSED(1)
            _FIRST_FAST=_FAST_CLOSED(1)
         Else
            _DC=_FIRST_CHIP-_CHIP_CLOSED(_SCREEN_NO)
            _DF=_FIRST_FAST-_FAST_CLOSED(_SCREEN_NO)
            If _DC>_CHIP_SCREEN_LOSS
               _CHIP_SCREEN_LOSS=_DC
            End If
            If _DF>_FAST_SCREEN_LOSS
               _FAST_SCREEN_LOSS=_DF
            End If
         End If
      End If
   End If
Next _SCREEN_NO
If _BANK_OWN=1
   Erase 29
   If Length(29)<>0
      _CLEAN_ERR=_CLEAN_ERR or 16
   End If
End If
Amos To Front
_CHIP1=Chip Free : _FAST1=Fast Free
_VERDICT$="FAIL"
If _ERR=0 and _CLEAN_ERR=0
   If _SHOWN=100 and _MOVED=100 and _OFF_COUNT=100 and _AUTO_COUNT=10
      If _OPENED=10 and _CLOSED=10
         If _CHIP_LOSS=0 and _FAST_LOSS=0 and _CHIP_SCREEN_LOSS=0 and _FAST_SCREEN_LOSS=0
            _RESULT=1
            _VERDICT$="PASS_FUNCTIONAL_LIFECYCLE"
         Else
            _ERR=14
         End If
      End If
   End If
End If
Trap Open Out 1,_LOG$
_IO=Errtrap
If _IO<>0
   Print "LOG OPEN FAILED ";_IO
   End
End If
Print #1,"SOURCE_TAG M19_S1P2M_FUNCTIONAL_V1"
Print #1,"PRG_STATE ";_PRG
Print #1,"RUN_MODE ";_MODE$
Print #1,"CPU_ATTNFLAGS ";_CPU
Print #1,"OPENED ";_OPENED;" CLOSED ";_CLOSED
Print #1,"SHOWN ";_SHOWN;" MOVED ";_MOVED;" OFF_COUNT ";_OFF_COUNT;" AUTO_CLOSE ";_AUTO_COUNT
Print #1,"SPRITE_RC ";_SPRITE_RC;" MOVE_RC ";_MOVE_RC;" OFF_RC ";_OFF_RC;" FREE_RC ";_FREE_RC
Print #1,"CHIP_CYCLE_LOSS ";_CHIP_LOSS;" FAST_CYCLE_LOSS ";_FAST_LOSS
Print #1,"CHIP_SCREEN_LOSS ";_CHIP_SCREEN_LOSS;" FAST_SCREEN_LOSS ";_FAST_SCREEN_LOSS
Print #1,"CHIP_BEFORE ";_CHIP0;" CHIP_AFTER ";_CHIP1
Print #1,"FAST_BEFORE ";_FAST0;" FAST_AFTER ";_FAST1
For _I=1 To 10
   Print #1,"SCREEN ";_I;" CHIP ";_CHIP_CLOSED(_I);" FAST ";_FAST_CLOSED(_I)
Next _I
Print #1,"RESULT ";_RESULT;" ERR ";_ERR;" CLEAN_ERR ";_CLEAN_ERR
Print #1,"VERDICT ";_VERDICT$
Trap Close 1
Print _VERDICT$;" ERR ";_ERR;" CLEAN_ERR ";_CLEAN_ERR
Print "RAM LOG ";_LOG$
End
'''
    return s.encode('ascii')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    assert a.source.resolve()!=a.output.resolve()
    assert not a.output.exists(), 'refuse overwrite'
    out=prepare(a.source.read_bytes())
    a.output.write_bytes(out)
    print('S1P2M_ASC',len(out),sha256(out).hexdigest(),flush=True)
