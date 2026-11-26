#!/usr/bin/env python3
"""Derive the P2k two-launch Runtime ASC from the exact P2j source."""
import argparse
from hashlib import sha256
from pathlib import Path

OLD = "7c6cd1fdca86323271810d37f484b2bad33b70fe02c968a4d7bb306511c56084"

def once(s,a,b):
    assert s.count(a)==1, a
    return s.replace(a,b,1)

def prepare(raw):
    assert sha256(raw).hexdigest()==OLD
    crlf=b"\r\n" in raw
    s=raw.decode("ascii").replace("\r\n","\n")
    s=once(s,"' M19 S1-P2j - one-shot native display, no exposed Chip free.\n' Snapshot required. Exact AGSP fixture, image 3. Runtime first.", "' M19 S1-P2k r4 - two launches, transaction quarantine.\n' Reset once before phase 1; never reset between phases.")
    s=s.replace("M19_S1P2J_","M19_S1P2K_")
    s=once(s,"_ERR=0 : _CLEAN_ERR=0 : _RESULT=0 : _OPEN=0 : _BANK_OWN=0",'''Print "1 = DISPLAY AFTER RESET"
Print "2 = QUARANTINE WITHOUT RESET"
Input "PHASE (1 OR 2)";_PHASE
If _PHASE<>1 and _PHASE<>2
   Print "INVALID PHASE"
   End
End If
If _PHASE=1
   _LOG$="RAM:M19_S1P2K_PHASE1.TXT"
Else
   _LOG$="RAM:M19_S1P2K_PHASE2.TXT"
End If
_ERR=0 : _CLEAN_ERR=0 : _RESULT=0 : _OPEN=0 : _BANK_OWN=0''')
    s=once(s,"   If _SPRITE_RC<>1\n      _ERR=10\n   End If",'''   If _PHASE=1
      If _SPRITE_RC<>1
         _ERR=10
      End If
   Else
      If _SPRITE_RC<>-123
         _ERR=13
      End If
   End If''')
    s=once(s,"If _ERR=0\n   For _FRAME=1 To 100","If _ERR=0 and _PHASE=1\n   For _FRAME=1 To 100")
    s=once(s,"   If _SPRITE_RC=1 and _BANK_FREE_RC<>0","   If _ATTEMPT=1 and _BANK_FREE_RC<>0")
    s=once(s,'''If _ERR=0 and _CLEAN_ERR=0 and _MOVES=100 and _ERASED=1 and _CLOSED=1
   _RESULT=1
End If
_VERDICT$="FAIL"
If _RESULT=1
   _VERDICT$="PASS_DISPLAY_CLOSE_RETAINED_ONLY"
End If''','''_VERDICT$="FAIL"
If _ERR=0 and _CLEAN_ERR=0 and _ERASED=1 and _CLOSED=1
   If _OFF_RC=1 and _CURSOR_RC=1 and _BANK_FREE_RC=0
      If _PHASE=1
         If _SPRITE_RC=1 and _MOVE_RC=1 and _MOVES=100
            _RESULT=1
            _VERDICT$="PASS_DISPLAY_CLOSE_RETAINED_ONLY"
         End If
      Else
         If _SPRITE_RC=-123 and _MOVE_RC=-999 and _MOVES=0
            _RESULT=1
            _VERDICT$="PASS_QUARANTINE_NO_NEW_DISPLAY"
         End If
      End If
   End If
End If''')
    s=once(s,'Print #1,"SOURCE_TAG M19_S1P2K_PUBLIC_V1"','Print #1,"SOURCE_TAG M19_S1P2K_R4_TRANSACTION_V1"\nPrint #1,"PHASE ";_PHASE')
    assert all(len(line)<=220 for line in s.splitlines())
    return (s.replace("\n","\r\n") if crlf else s).encode("ascii")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    out=prepare(args.source.read_bytes())
    args.output.write_bytes(out)
    print("P2K_ASC",len(out),sha256(out).hexdigest())
