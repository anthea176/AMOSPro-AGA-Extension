#!/usr/bin/env python3
"""Reject blocking Exec waits in AMOS-facing M4b routines.

Policy: extension commands must always return control to AMOS.
WaitPort is forbidden in Screen Close, Aga Swap and Aga Back Fill.
Use GetMsg polling plus a bounded WaitTOF budget instead.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_ap20 import parse

TARGET=ROOT/'dist'/'AMOSPro_AGA.Lib'
WAITPORT=bytes.fromhex('4eaefe80')  # Exec WaitPort, LVO -384
WAIT_EXEC=bytes.fromhex('4eaefec2') # Exec Wait, LVO -318

def segment(lib,index):
    s=lib.starts[index]
    return lib.code[s:s+2*lib.jumps[index]]

def main():
    lib=parse(TARGET.read_bytes())
    failures=[]
    for index,name in ((8,'Aga Screen Close'),(11,'Aga Swap'),(12,'Aga Back Fill'),(30,'Aga Mouse Buttons')):
        code=segment(lib,index)
        if WAITPORT in code:
            failures.append(f'{name}: forbidden WaitPort')
        if WAIT_EXEC in code:
            failures.append(f'{name}: forbidden Exec Wait')
    if failures:
        for f in failures:
            print('FAIL:',f)
        return 1
    print('OK: no blocking WaitPort/Wait in AMOS-facing close/swap/backfill routines')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
