#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 fifth AP20 private Safe/WaitBlit and post-Close source-only.

The B7-m2 installed Lib and active ASC are unchanged. Keep all 181 legacy
AP20 entries, tokens and four native groups byte-for-byte; extend only the
private fifth group in RAM for CPU/ABI/PC16 structural validation.
NO automatic Close/End hook is installed by this candidate.
"""
from __future__ import annotations

from hashlib import sha256
from audit_ap20 import inspect, parse, walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_page_manager_in_memory import build_b8_page_manager
from m19_b8_safe_lifecycle_emit import emit_b8_safe_lifecycle
from m19_b8_page_manager_emit import emit_b8_page_manager

OLD_SHA='98166666ebe11c8c7210b3f734c5615567a9eb221c7ecf440fa1c005f97add37'
TITLE=(b'AMOSPro AGA M19 B8 SAFE/WAITBLIT private lifecycle SOURCE ONLY\0'
       b'$VER: M19 B8 Safe, post-Close/End UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_safe_lifecycle() -> tuple[bytes,dict]:
    old,meta=build_b8_page_manager()
    if meta['sha256']!=OLD_SHA or len(old)!=111396:
        raise ValueError('Previous 58-case B8 source provenance drift')
    tokens,parts,_=unpack_ap20(old)
    if len(parts)!=182:
        raise ValueError('Unexpected previous fifth AP20 unit layout')
    core,_=emit_b8_page_manager()
    extension,labels=emit_b8_safe_lifecycle()
    if not extension.startswith(core) or parts[181]!=DISPATCH_V2+core:
        raise ValueError('Private source prefix was modified')
    group=DISPATCH_V2+extension
    if len(group)>=MAX_UNIT_BYTES or len(group)&1:
        raise ValueError('Fifth AP20 group exceeds native size budget')
    sections=parts[:181]+[group]
    result=repack_ap20(old,tokens,sections,TITLE)
    if unpack_ap20(result)!=(tokens,sections,TITLE):
        raise ValueError('AP20 HUNK roundtrip failure')
    before,after=inspect(parse(old)),inspect(parse(result))
    if before['issues'] or after['issues'] or before['tokens']!=after['tokens']:
        raise ValueError('Public tokens/AP20 ABI drift')
    if sections[:181]!=parts[:181]:
        raise ValueError('Protected B7-m2 AP20 sections changed')
    old_pc16=pc16_displacements(parts)
    new_pc16=pc16_displacements(sections)
    if old_pc16!=new_pc16:
        raise ValueError('Existing PC16 displacements changed')
    groups=[n for n,p in enumerate(sections) if p.startswith(DISPATCH_V2)]
    if groups!=[142,153,156,177,181]:
        raise ValueError('Unexpected native groups')
    if any(t['name'] in ('aga bob clear','aga bob update') for t in walk_tokens(tokens)):
        raise ValueError('Unexpected public B8 token')
    return result,dict(
        sha256=sha256(result).hexdigest(),bytes=len(result),
        prev_sha=OLD_SHA,source_bytes=len(extension),
        native_group_bytes=len(group),new_suffix_bytes=len(extension)-len(core),
        ap20_entries=len(sections),public_commands=86,native_groups=groups,
        old_pc16_max=max(map(abs,old_pc16.values())),
        new_pc16_max=max(map(abs,new_pc16.values())),
        safe_capture=labels['b8_service_safe_capture_entry'],
        safe_restore=labels['b8_service_safe_restore_entry'],
        postclose=labels['b8_service_postclose_entry'],
        installed_lib='UNCHANGED',current_asc='UNCHANGED',
        close_end_hook='NOT WIRED',clear_update_tokens='ABSENT',
        gate_a='CPU020/ABI/PC16 SOURCE ONLY',
        gate_b='NOT TESTED',gate_c='NOT TESTED',gate_d='NOT TESTED')

if __name__=='__main__':
    from pprint import pprint
    _,meta=build_b8_safe_lifecycle()
    print('M19 B8 fifth AP20 Safe/Close/End source-only, UNINSTALLED')
    pprint(meta)
