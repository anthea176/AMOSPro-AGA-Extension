#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Fifth AP20 group atomic REGISTERED Clear/Update candidate: SOURCE ONLY.

Preserves all public tokens, 181 old B7-m2 AP20 sections, B7 Draw/Close
trampoline section 177, and 60-case B7-end callback registration.
DOES NOT expose new AMOS tokens and DOES NOT install any library.
"""
from __future__ import annotations

from hashlib import sha256
from audit_ap20 import inspect,parse,walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import unpack_ap20,repack_ap20
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_clear_update_tx_in_memory import build_b8_clear_update_tx
from m19_b8_clear_update_tx_emit import emit_b8_clear_update_tx
from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update

PREV='cbfec5d871d746391e806acde78b15d8f2526f84f42ad64f954140e76d23c60c'
TITLE=(b'AMOSPro AGA M19 B8 private atomic registered Update SOURCE ONLY\0'
       b'$VER: B8 registered Update UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)
FIFTH=181


def build_b8_atomic_registered_update() -> tuple[bytes,dict]:
    prev,meta=build_b8_clear_update_tx()
    if meta['sha256']!=PREV or len(prev)!=114988:
        raise ValueError('Verified B8 72-case transaction source drift')
    tokens,parts,_=unpack_ap20(prev)
    old,_=emit_b8_clear_update_tx()
    new,labels=emit_b8_atomic_registered_update()
    if len(parts)!=182 or parts[FIFTH]!=DISPATCH_V2+old or not new.startswith(old):
        raise ValueError('Byte-exact fifth AP20 ancestry is broken')
    if len(new)+len(DISPATCH_V2)>=MAX_UNIT_BYTES:
        raise ValueError('Native fifth unit overflow')
    sections=list(parts)
    sections[FIFTH]=DISPATCH_V2+new
    candidate=repack_ap20(prev,tokens,sections,TITLE)
    if unpack_ap20(candidate)!=(tokens,sections,TITLE):
        raise ValueError('AP20 HUNK roundtrip changed')
    before,after=inspect(parse(prev)),inspect(parse(candidate))
    if before['issues'] or after['issues'] or before['tokens']!=after['tokens']:
        raise ValueError('AMOS public token/ABI changed')
    if sections[:FIFTH]!=parts[:FIFTH]:
        raise ValueError('Existing B7/Close/Draw sections mutated')
    groups=[i for i,p in enumerate(sections) if p.startswith(DISPATCH_V2)]
    if groups!=[142,153,156,177,181]:
        raise ValueError('Unexpected native group layout')
    spans=pc16_displacements(sections)
    if max(map(abs,spans.values()))>=32766:
        raise ValueError('AMOS Compiler PC16 overflow')
    if any(t['name'] in ('aga bob clear','aga bob update') for t in walk_tokens(tokens)):
        raise ValueError('Public Update token introduced prematurely')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        previous_sha=PREV,appended_bytes=len(new)-len(old),
        native_group_bytes=len(sections[FIFTH]),ap20_entries=len(sections),
        public_commands=86,native_groups=groups,
        old_pc16_max=max(map(abs,pc16_displacements(parts).values())),
        new_pc16_max=max(map(abs,spans.values())),
        atomic_registered_offset=labels['b8_service_update_atomic_registered_entry'],
        requires_b7_end_registration=True,
        bootstrap_first_update='NOT IMPLEMENTED',
        new_tokens=False,source_only=True,installed_lib='UNCHANGED',
        active_asc='UNCHANGED',last_good='UNCHANGED',
        gate_a='NATIVE TEST REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    from pprint import pprint
    _,meta=build_b8_atomic_registered_update()
    print('M19 B8 atomic registered Update fifth AP20 group SOURCE ONLY')
    pprint(meta)
