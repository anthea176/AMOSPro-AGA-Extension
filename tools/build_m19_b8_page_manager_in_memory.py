#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""B8 private page manager, fifth native AP20 group, SOURCE ONLY.

Builds an IN-MEMORY candidate from exact B7-m2 source. Does not modify
the installed Lib, public tokens, existing 181 AP20 entries or test ASC.
No WinUAE / AMOS Compiler Gate is implied by source-only validation.
"""
from __future__ import annotations

from hashlib import sha256

from audit_ap20 import inspect, parse, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import unpack_ap20, repack_ap20
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from m19_b8_page_manager_emit import emit_b8_page_manager
from m19_b8_back_selector_emit import emit_b8_back_selector
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool

TITLE=(b'AMOSPro AGA M19 B8 private page manager MC68020 SOURCE ONLY\0'
       b'$VER: M19 B8 page manager UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_page_manager() -> tuple[bytes,dict]:
    base,origin=build_close_reset()
    if (len(base)!=102400
            or origin['sha256']!='242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'):
        raise ValueError('B7-m2 base no longer matches approved source')
    tokens,parts,_=unpack_ap20(base)
    if len(parts)!=181:
        raise ValueError('B7-m2 AP20 entry layout changed')
    service,labels=emit_b8_page_manager()
    old,_=emit_b8_back_selector()
    pool,_=emit_b8_snapshot_pool()
    if not service.startswith(old+pool):
        raise ValueError('Private B8 original native units were modified')
    group=DISPATCH_V2+service
    if len(group)&1 or len(group)>=MAX_UNIT_BYTES:
        raise ValueError('B8 fifth AP20 group cannot fit the native limit')
    sections=parts+[group]
    candidate=repack_ap20(base,tokens,sections,TITLE)
    if unpack_ap20(candidate)!=(tokens,sections,TITLE):
        raise ValueError('AP20 HUNK round trip failed')
    before,after=inspect(parse(base)),inspect(parse(candidate))
    if before['issues'] or after['issues'] or before['tokens']!=after['tokens']:
        raise ValueError('Existing public API was altered')
    if sections[:181]!=parts:
        raise ValueError('B7-m2 source sections were changed')
    groups=[i for i,part in enumerate(sections) if part.startswith(DISPATCH_V2)]
    if groups!=[142,153,156,177,181]:
        raise ValueError('Unexpected native group indices')
    old_pc16=pc16_displacements(parts)
    new_pc16=pc16_displacements(sections)
    if old_pc16!=new_pc16:
        raise ValueError('Existing Compiler PC16 displacements changed')
    if any(x['name'] in ('aga bob clear','aga bob update') for x in walk_tokens(tokens)):
        raise ValueError('Public B8 tokens appeared unexpectedly')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),
        size=len(candidate),
        base_sha=origin['sha256'],
        native_group_bytes=len(group),
        fifth_group=181,
        public_commands=86,
        ap20_entries=182,
        native_groups=groups,
        old_pc16_max=max(map(abs,old_pc16.values())),
        new_pc16_max=max(map(abs,new_pc16.values())),
        service_bind_offset=labels['b8_service_bind_entry'],
        source_prefix_bytes=len(old)+len(pool),
        gate_a='CPU020 + AP20 SOURCE ONLY',
        gate_b='NOT TESTED',gate_c='NOT TESTED',gate_d='NOT TESTED',
        installed_lib='UNCHANGED', current_asc='UNCHANGED',
        clear_update_tokens='ABSENT',
    )

if __name__=='__main__':
    from pprint import pprint
    _,meta=build_b8_page_manager()
    print('M19 B8 page manager, fifth AP20 group, UNINSTALLED')
    pprint(meta)
