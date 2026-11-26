#!/usr/bin/env python3
"""Run the selected exact MC68020 regression without shell interpolation."""
import os
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
tmp=Path(os.environ['RUNNER_TEMP'])
vasm=tmp/'vasm/vasmm68k_mot'
historical=tmp/'p1i.bin'
suite=os.environ['S2A_SUITE']
assert suite in ('public-runtime','public-compiled','lifetime-runtime',
                 'lifetime-compiled','chain','pattern','safeport','bob')
subprocess.run([str(vasm),'-I',str(root/'src/native/m19_s1'),'-Fbin',
                '-m68020','-no-opt','-quiet','-o',str(historical),
                str(root/'src/native/m19_s1/M19_S1P1I_BANK_PUBLIC_MC68020.s')],
               cwd=root,check=True)
subprocess.run([sys.executable,'-B',str(root/'tools/test_m19_s2a_public_gate_a.py'),
                '--suite',suite,'--expected-sha',
                '1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2',
                '--vasm',str(vasm),'--historical',str(historical)],
               cwd=root,check=True)
