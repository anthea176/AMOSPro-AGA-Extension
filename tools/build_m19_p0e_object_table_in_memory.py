#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e source-only candidate: PRIVATE Bob object table appended in AGA group.

Base P0d stays EXACT; append 2332-byte MC68020 object table to the existing
AGA V2 native group without moving any public RBSR dispatcher address.
The public 83-command AP20 table is unchanged. This validates a legal route
around P0d's nearly exhausted interpreter PC16 relative-call span. This is
NOT yet a usable Aga Bob N,X,Y,I token or a rendered object, and produces NO
installable Lib, ASC, artifact, or secondary candidate file.
"""
from __future__ import annotations

from hashlib import sha256
from compiler_relocation import unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from audit_ap20 import inspect,parse
from build_m19_p0d_bob_blit_in_memory import build as build_p0d
from m19_p0e_object_table_emit import emit_object_table
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

P0D_SHA='bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be'
AGA_GROUP=92
TITLE=(b'AMOSPro AGA M19 P0e MC68020 PRIVATE OBJECTS SOURCE-ONLY Gate A\0'
       b'$VER: AMOSPro_AGA M19 P0e object metadata NO PUBLIC TOKEN\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    original,old_meta=build_p0d()
    if len(original)!=91300 or sha256(original).hexdigest()!=P0D_SHA:
        raise ValueError('P0d canonical base/source drift')
    tokens,parts,_=unpack_ap20(original)
    if len(parts)!=93 or len(parts[AGA_GROUP])!=56580:
        raise ValueError('P0d native AGA group layout drift')
    if not parts[AGA_GROUP].startswith(DISPATCH_V2):
        raise ValueError('old AGA group has no audited Compiler V2 dispatcher')
    objects,labels=emit_object_table()
    if len(objects)!=2332 or len(objects)&1:
        raise ValueError('private P0e table size/word alignment drift')
    changed=list(parts)
    changed[AGA_GROUP]=parts[AGA_GROUP]+objects
    if len(changed[AGA_GROUP])>65534:
        raise ValueError('AGA Compiler V2 per-unit word size exceeded')
    candidate=repack_ap20(original,tokens,changed,TITLE)
    if unpack_ap20(candidate)!=(tokens,changed,TITLE):
        raise ValueError('HUNK/AP20 roundtrip failed')
    if changed[:AGA_GROUP]!=parts[:AGA_GROUP]:
        raise ValueError('P0d public/BOBS/C2P/IFF bytes unexpectedly altered')
    assert changed[AGA_GROUP].startswith(parts[AGA_GROUP])
    before=interpreter_rbsr_displacements(parts)
    after=interpreter_rbsr_displacements(changed)
    if before!=after or max(map(abs,after.values()))!=old_meta['max_rbsr']:
        raise ValueError('P0e changed an existing signed 16-bit interpreter branch')
    old_audit=inspect(parse(original))
    new_audit=inspect(parse(candidate))
    if new_audit['issues'] or old_audit['tokens']!=new_audit['tokens']:
        raise ValueError('P0d public token signature corrupted')
    native_offset=len(parts[AGA_GROUP])-len(DISPATCH_V2)
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        previous_sha=P0D_SHA,public_commands=83,ap20_entries=93,
        group=AGA_GROUP,private_offset=native_offset,
        appended_bytes=len(objects),group_bytes=len(changed[AGA_GROUP]),
        rbsr_max=max(map(abs,after.values())),labels=labels,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED',
    )


if __name__=='__main__':
    data,meta=build()
    print('M19 P0e IN-MEMORY PRIVATE V2 OBJECTS AP20 SOURCE PROVENANCE PASS',
          {k:v for k,v in meta.items() if k!='labels'})
