#!/usr/bin/env python3
"""Build and test the S2b v4 registry, allocation and drain components."""
import os
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
tmp=Path(os.environ['RUNNER_TEMP'])
vasm=tmp/'vasm/vasmm68k_mot'
src=root/'src/native/m19_s2'
binary=tmp/'s2b-registry.bin'
subprocess.run([str(vasm),'-I',str(src),'-Fbin','-m68020','-no-opt','-quiet',
                '-o',str(binary),str(src/'M19_S2B_COMPONENT_GATE_MC68020.s')],
               cwd=root,check=True)
subprocess.run([sys.executable,'-B',str(root/'tools/test_m19_s2b_registry_cpu.py'),
                str(binary)],cwd=root,check=True)
print('S2B_COMPONENT_BYTES',binary.stat().st_size,flush=True)
