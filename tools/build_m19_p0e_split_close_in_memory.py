#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e source-only prototype: active Bob Set/Off plus Close reset.

Strict build from P0d->P0e source-validated split public candidate. Only
the existing public Screen Close stub #8 is redirected to a NEW BOBS
wrapper. All original native bytes remain immutable prefix. No End hook,
Draw, installed .Lib, or separate ASC.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from compiler_relocation import RBSR,GETP,unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from audit_ap20 import inspect,parse
from build_m19_p0e_split_public_in_memory import build as build_split
from m19_p0e_split_close_emit import emit_split_with_close
from m19_p0e_split_bridge_emit import emit_split_bobs_public
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

BOBS=93
CLOSE=8
TITLE=(b'AMOSPro AGA M19 P0e CPU020 SPLIT BOB SET OFF CLOSE-RESET GATE A\0'
       b'$VER: AMOSPro_AGA P0e source-only reset-before-close UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    prev,meta=build_split()
    tokens,parts,_=unpack_ap20(prev)
    original,labels=emit_split_bobs_public()
    revised,all_labels=emit_split_with_close()
    if not parts[BOBS].endswith(original) or not revised.startswith(original):
        raise ValueError('split BOBS source changed unexpectedly')
    native_suffix=revised[len(original):]
    entry=(len(parts[BOBS])-len(DISPATCH_V2)+
           all_labels['public_aga_p0e_close_entry']-len(original))
    if len(native_suffix)&1 or entry&1 or entry>=65534:
        raise ValueError('Close native offset/size invalid')
    if parts[CLOSE][:2]!=RBSR or len(parts[CLOSE])!=8:
        raise ValueError('existing public Close stub damaged')
    source_group,source_offset=unpack_from('>HH',parts[CLOSE],2)
    if source_group!=BOBS or source_offset==entry:
        raise ValueError('old Close not routed to expected P0d BOBS group')
    modified=list(parts)
    modified[CLOSE]=RBSR+pack('>HH',BOBS,entry)+bytes.fromhex('4e75')
    modified[BOBS]=parts[BOBS]+native_suffix
    if len(modified[BOBS])>65534 or any(len(x)&1 for x in modified):
        raise ValueError('Compiler V2 word-boundary error')
    new=repack_ap20(prev,tokens,modified,TITLE)
    if unpack_ap20(new)!=(tokens,modified,TITLE):
        raise ValueError('AP20/HUNK roundtrip failure')
    original_audit=inspect(parse(prev))
    audit=inspect(parse(new))
    if audit['issues'] or audit['tokens']!=original_audit['tokens']:
        raise ValueError('old public API modified')
    if (modified[91:93]!=parts[91:93] or modified[94]!=parts[94] or
            modified[BOBS][:len(parts[BOBS])]!=parts[BOBS]):
        raise ValueError('source-pinned native units mutated')
    links=interpreter_rbsr_displacements(modified)
    reach=max(map(abs,links.values()))
    if CLOSE not in links or reach>=32766 or 32766-reach<64:
        raise ValueError(f'unsafe reset-before-Close PC16 reach {reach}')
    return new,dict(
        sha256=sha256(new).hexdigest(),size=len(new),
        previous_sha=meta['sha256'],public_commands=85,ap20_entries=95,
        close_group=BOBS,close_entry=entry,
        close_suffix_bytes=len(native_suffix),
        previous_stub=source_offset,interpreter_reach=reach,
        pc16_margin=32766-reach,gate_a='PENDING',gate_b='NOT TESTED',
        gate_c='NOT TESTED',end_reset='NOT IMPLEMENTED',
        draw='NOT IMPLEMENTED')


if __name__=='__main__':
    _,meta=build()
    print('M19 P0e SOURCE ONLY RESET BEFORE ORIGINAL AGA CLOSE',meta)
