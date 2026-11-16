#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e BOBS->AGA cross-unit bridge, rebuilt from pinned sources IN MEMORY.

Appends a small MC68020 BOBS thunk after immutable P0d public Bob Blit.
The P0e object-table code is appended in the existing AGA V2 unit as
already verified. No new AP20 token or Lib/ASC write. Proves PC16 distances
and every original public group/stub stay valid.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from audit_ap20 import inspect,parse
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20,repack_ap20
from build_m19_p0d_bob_blit_in_memory import build as build_p0d
from build_m19_p0e_object_table_in_memory import build as build_p0e
from m19_p0d_public_blit_emit import emit_public_blit
from m19_p0e_v2_object_bridge_emit import (
    emit_v2_object_bridge, AGA_P0D_GROUP_BYTES, OBJ_RELATIVE,
)
from m19_p0e_object_table_emit import emit_object_table
sys.path.insert(0,str(Path(__file__).resolve().parent/'experiments'))
from ap20_v3_r82_split import interpreter_rbsr_displacements

P0D_SHA='bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be'
P0E_SHA='588345837105bdade12f8ab289b8a46f22cd1be5f9a14c8f88ca9f2220e28790'
BOBS_GROUP=91
AGA_GROUP=92
TITLE=(b'AMOSPro AGA M19 P0e 020 PRIVATE VERIFIED BOBS-AGA LINK Gate A\0'
       b'$VER: AMOSPro_AGA P0e private cross-unit native bridge UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build():
    prev,base=build_p0d()
    if len(prev)!=91300 or base['sha256']!=P0D_SHA or sha256(prev).hexdigest()!=P0D_SHA:
        raise ValueError('active P0d source provenance changed')
    candidate,meta=build_p0e()
    if meta['sha256']!=P0E_SHA or sha256(candidate).hexdigest()!=P0E_SHA:
        raise ValueError('P0e frozen object-table source changed')
    tokens,parts,_=unpack_ap20(candidate)
    old_tokens,old_parts,_=unpack_ap20(prev)
    if tokens!=old_tokens or len(parts)!=93:
        raise ValueError('public API changed')
    if len(old_parts[AGA_GROUP])!=AGA_P0D_GROUP_BYTES or (
            meta['private_offset']!=OBJ_RELATIVE+0x1c2-len(DISPATCH_V2)):
        raise ValueError('AGA State/object-table group anchor changed')
    original_native,p0d_labels=emit_public_blit()
    linked_native,linked_labels=emit_v2_object_bridge()
    table,table_labels=emit_object_table()
    if not linked_native.startswith(original_native) or not parts[BOBS_GROUP].endswith(original_native):
        raise ValueError('P0d BOBS native prefix changed')
    if not parts[AGA_GROUP].endswith(table):
        raise ValueError('P0e AGA object table bytes changed')
    suffix=linked_native[len(original_native):]
    if not suffix or len(suffix)&1:
        raise ValueError('missing even BOBS link suffix')
    revised=list(parts)
    revised[BOBS_GROUP]+=suffix
    if len(revised[BOBS_GROUP])>65534:
        raise ValueError('BOBS V2 Compiler unit too large')
    if revised[AGA_GROUP]!=parts[AGA_GROUP] or revised[:BOBS_GROUP]!=parts[:BOBS_GROUP]:
        raise ValueError('old token/native unit modified')
    before=interpreter_rbsr_displacements(parts)
    after=interpreter_rbsr_displacements(revised)
    maxreach=max(map(abs,after.values()))
    if maxreach>=32766:
        raise ValueError(f'new cross bridge exceeds signed PC16: {maxreach} (suffix {len(suffix)})')
    raw=repack_ap20(candidate,tokens,revised,TITLE)
    if unpack_ap20(raw)!=(tokens,revised,TITLE):
        raise ValueError('HUNK / Compiler V2 roundtrip mismatch')
    if inspect(parse(raw))['issues']:
        raise ValueError('AP20 token/parameter audit failed')
    if len(revised[AGA_GROUP])!=58912 or not revised[AGA_GROUP].startswith(DISPATCH_V2):
        raise ValueError('P0e AGA source changed')
    # Caller gets all four labels relative to the compiled BOBS native start.
    offsets={key:len(parts[BOBS_GROUP])-len(DISPATCH_V2)+
             linked_labels['object_bridge_'+key+'_entry']-len(original_native)
             for key in ('put_selected','put','off','read','reset')}
    assert all(0<=value<65534 and value%2==0 for value in offsets.values())
    return raw,dict(
        sha256=sha256(raw).hexdigest(),bytes=len(raw),previous_sha=P0E_SHA,
        native_suffix_bytes=len(suffix),bobs_bytes=len(revised[BOBS_GROUP]),
        aga_bytes=len(revised[AGA_GROUP]),public_commands=83,ap20_entries=93,
        rbsr_max=maxreach,previous_rbsr=max(map(abs,before.values())),
        state_offset=0x1c2,object_state_delta=OBJ_RELATIVE,
        entry_offsets=offsets,object_labels=table_labels,
        bridge_labels=linked_labels,
        gate_a='PENDING',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    _,report=build()
    print('M19 P0e V2 BOBS->AGA BRIDGE IN-MEMORY SOURCE ONLY',
          {k:v for k,v in report.items()
           if k not in ('bridge_labels','object_labels')})
