#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P3a source-only sizing probe; no AP20 or active artifact writes.

Extract the exact P2d Retire/Reclaim implementation and its three shared
helpers, omitting Show/Move/Exchange and their dependencies. The five-entry
test shim keeps the existing CPU harness's +12/+16 ABI. Its first three
entries refuse without touching a receipt. This is NOT yet UNIT142 code.
"""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
S2=ROOT/'src/native/m19_s2'

def section(source,start,end=None):
    assert source.count(start)==1,(start,source.count(start))
    i=source.index(start)
    if end is None:return source[i:]
    assert source.count(end)==1,(end,source.count(end))
    j=source.index(end)
    assert i<j
    return source[i:j]

def emit():
    read=lambda n:(S2/('M19_S2D_EXT_'+n+'_MC68020.s')).read_text(encoding='ascii')
    retire=section(read('RETIRE'),'AGSP_S2D_EXT_RETIRE:\n',
                   '    include "M19_S2D_EXT_FRAME_MC68020.s"')
    refs=section(read('FRAME'),'s2d_x_unreferenced:\n',
                 '    include "M19_S2D_EXT_HIDDEN_SHOW_MC68020.s"')
    show=read('HIDDEN_SHOW')
    no=section(show,'s2d_c_no:\n','s2d_c_hidden_refs:\n')
    span=section(show,'s2d_c_span:\n')
    return ('; AGA_NATIVE_MIN_CPU: MC68020\n'
            '    bra.w s2d_c_no\n'*3+
            '    bra.w AGSP_S2D_EXT_RETIRE\n'
            '    bra.w AGSP_S2D_EXT_RECLAIM\n'+retire+refs+no+span)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    out=p.parse_args().output.resolve()
    assert not out.is_relative_to(ROOT),'probe must be outside repository'
    out.write_text(emit(),encoding='ascii')
if __name__=='__main__':main()
