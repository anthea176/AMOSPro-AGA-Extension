#!/usr/bin/env python3
"""Run one S2b public/inherited MC68020 shard."""
import os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
tmp=Path(os.environ['RUNNER_TEMP'])
vasm=tmp/'vasm/vasmm68k_mot'
historical=tmp/'p1i.bin'
suite=os.environ['S2B_SUITE']
assert suite in ('runtime','compiled','chain','pattern','safeport','bob')
subprocess.run([str(vasm),'-I',str(root/'src/native/m19_s1'),'-Fbin','-m68020',
                '-no-opt','-quiet','-o',str(historical),
                str(root/'src/native/m19_s1/M19_S1P1I_BANK_PUBLIC_MC68020.s')],cwd=root,check=True)
subprocess.run([sys.executable,'-B',str(root/'tools/test_m19_s2b_public_gate_a.py'),
                '--suite',suite,'--vasm',str(vasm),'--historical',str(historical)],cwd=root,check=True)
