#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 source-only FIFTH AP20 native unit, no new public token or active Lib.

Keep exact B7-m2 four native groups and all 181 historic AP20 entries.
Append one isolated DISPATCH_V2 group at 181: source-only MC68020 planar
snapshot, Safe back selector, transactionally managed per-page snapshots.

The fifth native unit has no public stub yet. The future Clear/Update
public stubs must be local to the fifth group, with new AP20 tests and
separate authority to switch the canonical dist/AMOSPro_AGA.Lib.
"""
from __future__ import annotations

from hashlib import sha256
from audit_ap20 import inspect,parse,walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import repack_ap20,unpack_ap20
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from m19_b8_back_selector_emit import emit_b8_back_selector
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool

B7M2_SHA='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
FIFTH_GROUP=181
TITLE=(b'AMOSPro AGA M19 B8 new fifth native BACKING unit SOURCE ONLY\0'
       b'$VER: M19 B8 private page core/selector/pool UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_fifth_group() -> tuple[bytes,dict]:
    original,meta=build_close_reset()
    if len(original)!=102400 or meta['sha256']!=B7M2_SHA:
        raise ValueError('B7-m2 working source ancestry not pinned')
    tokens,parts,_=unpack_ap20(original)
    if len(parts)!=FIFTH_GROUP:
        raise ValueError('Unexpected B7-m2 AP20 entry count')
    code,labels=emit_b8_back_selector()
    pool,plabels=emit_b8_snapshot_pool()
    if (len(code)!=2400 or labels['b8_checked_back_selector_entry']!=1800
            or len(pool)!=1172 or plabels['b8_pool_bind_entry']!=0):
        raise ValueError('B8 private core/selector/pool bytes changed')
    group=DISPATCH_V2+code+pool
    if len(group)>=MAX_UNIT_BYTES or len(group)&1:
        raise ValueError('B8 fifth native group invalid')
    newer=parts+[group]
    newtokens=tokens  # absolutely no public API until integration is tested
    candidate=repack_ap20(original,newtokens,newer,TITLE)
    if unpack_ap20(candidate)!=(newtokens,newer,TITLE):
        raise ValueError('AP20 HUNK format roundtrip failed')
    before,after=inspect(parse(original)),inspect(parse(candidate))
    if before['issues'] or after['issues'] or before['tokens']!=after['tokens']:
        raise ValueError('B8 unexpectedly changed the published ABI')
    if newer[:FIFTH_GROUP]!=parts:
        raise ValueError('Existing B7-m2 AP20 code and stubs are not frozen')
    groups=[i for i,p in enumerate(newer) if p.startswith(DISPATCH_V2)]
    old_pc16=pc16_displacements(parts)
    new_pc16=pc16_displacements(newer)
    if groups!=[142,153,156,177,181] or old_pc16!=new_pc16:
        raise ValueError('Fifth group disturbed an existing Compiler link')
    if any(t['name'] in ('aga bob clear','aga bob update')
           for t in walk_tokens(newtokens)):
        raise ValueError('Public Clear/Update tokens must NOT exist yet')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        base_sha=B7M2_SHA,base_entries=len(parts),ap20_entries=len(newer),
        public_commands=86,native_groups=groups,
        fifth_group=FIFTH_GROUP,fifth_unit_bytes=len(group),
        source_core_selector_bytes=len(code),source_pool_bytes=len(pool),
        old_pc16_max=max(map(abs,old_pc16.values())),
        new_pc16_max=max(map(abs,new_pc16.values())),
        existing_stubs='BYTE-EXACT',installed_lib='UNCHANGED',
        clear_update_tokens='ABSENT',gate_a='AP20 SOURCE STRUCTURE ONLY',
        gate_b='NOT TESTED',gate_c='NOT TESTED',gate_d='NOT TESTED')


if __name__=='__main__':
    from pprint import pprint
    _,m=build_b8_fifth_group()
    print('M19 B8 5-unit source-only AP20 candidate, UNINSTALLED')
    pprint(m)
