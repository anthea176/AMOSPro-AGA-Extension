#!/usr/bin/env python3
"""Build and execute the isolated S2b component with pinned CI tools."""
import os
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
tmp=Path(os.environ['RUNNER_TEMP'])
vasm=tmp/'vasm/vasmm68k_mot'
binary=tmp/'s2b-retire.bin'
subprocess.run([str(vasm),'-Fbin','-m68020','-no-opt','-quiet','-o',str(binary),
                str(root/'src/native/m19_s2/M19_S2B_RETIRE_PAIR_MC68020.s')],
               cwd=root,check=True)
subprocess.run([sys.executable,'-B',str(root/'tools/test_m19_s2b_retire_pair_cpu.py'),
                str(binary)],cwd=root,check=True)
