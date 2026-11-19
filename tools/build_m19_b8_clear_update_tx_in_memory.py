#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""B8 private Clear/Update transaction stages, fifth AP20 group SOURCE ONLY.

Builds upon exact 60-case B7/B8 cross-unit trampoline; does not change
any public token, B7 native group, Close/Draw stub or installed Lib.
"""
from __future__ import annotations

from hashlib import sha256
from audit_ap20 import inspect,parse,walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import unpack_ap20,repack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_b7_trampoline_in_memory import build_b8_b7_trampoline
from m19_b8_cross_unit_arm_emit import emit_b8_cross_unit_arm
from m19_b8_clear_update_tx_emit import emit_b8_clear_update_tx

PREV_SHA='40de1b32206de8d784249b60a43d7f5f047828a2657c6651d4cb73bfeef09750'
TITLE=(b'AMOSPro AGA M19 B8 private Clear Update stages SOURCE ONLY\0'
       b'$VER: B8 private Clear Update UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)
FIFTH=181

def build_b8_clear_update_tx() -> tuple[bytes,dict]:
    previous,meta=build_b8_b7_trampoline()
    if meta['sha256']!=PREV_SHA or len(previous)!=113192:
        raise ValueError('Verified B7/B8 trampoline provenance drift')
    tokens,parts,_=unpack_ap20(previous)
    old,_=emit_b8_cross_unit_arm()
    new,labels=emit_b8_clear_update_tx()
    if len(parts)!=182 or parts[FIFTH]!=DISPATCH_V2+old or not new.startswith(old):
        raise ValueError('B8 native stage ancestry changed')
    if len(new)+len(DISPATCH_V2)>=MAX_UNIT_BYTES:
        raise ValueError('Fifth unit AP20 native limit exceeded')
    parts2=list(parts);parts2[FIFTH]=DISPATCH_V2+new
    image=repack_ap20(previous,tokens,parts2,TITLE)
    if unpack_ap20(image)!=(tokens,parts2,TITLE):
        raise ValueError('AP20 HUNK roundtrip changed')
    prior,after=inspect(parse(previous)),inspect(parse(image))
    if prior['issues'] or after['issues'] or prior['tokens']!=after['tokens']:
        raise ValueError('Public AMOS token/ABI changed')
    if parts2[:FIFTH]!=parts[:FIFTH]:
        raise ValueError('Protected B7-m2, Draw/Close stubs altered')
    groups=[i for i,p in enumerate(parts2) if p.startswith(DISPATCH_V2)]
    if groups!=[142,153,156,177,181]:
        raise ValueError('Native group index changed')
    pc16=pc16_displacements(parts2)
    if max(map(abs,pc16.values()))>=32766:
        raise ValueError('AP20 Compiler PC16 overflow')
    if any(t['name'] in ('aga bob clear','aga bob update')
           for t in walk_tokens(tokens)):
        raise ValueError('Stage names leaked into public tokens')
    return image,dict(
        sha256=sha256(image).hexdigest(),bytes=len(image),
        previous_sha=PREV_SHA,native_group_bytes=len(parts2[FIFTH]),
        appended_stage_bytes=len(new)-len(old),commands=86,
        ap20_entries=len(parts2),native_groups=groups,
        old_pc16_max=max(map(abs,pc16_displacements(parts).values())),
        new_pc16_max=max(map(abs,pc16.values())),
        clear=labels['b8_service_clear_guard_entry'],
        prepare=labels['b8_service_update_prepare_entry'],
        finish=labels['b8_service_update_finish_entry'],
        abort=labels['b8_service_update_abort_entry'],
        reset=labels['b8_service_tx_reset_entry'],
        no_amos_tokens=True,source_only=True,
        installed_lib='UNCHANGED',validated_ASC='UNCHANGED',
        LAST_GOOD='UNCHANGED',gate_a='CPU TEST REQUIRED',
        gate_b='NOT TESTED',gate_c='NOT TESTED',
        PUBLIC_UPDATE_ATOMICITY='NOT IMPLEMENTED')

if __name__=='__main__':
    from pprint import pprint
    _,meta=build_b8_clear_update_tx()
    print('M19 B8 private Clear/Update stages AP20 source-only')
    pprint(meta)
