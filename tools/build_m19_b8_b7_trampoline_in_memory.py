#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 SOURCE-ONLY B7/B8 intra-unit trampoline AP20 builder.

The existing 86 AMOS tokens and 182 AP20 entries are preserved.
The old B7-m2 native source is a byte-exact PREFIX of the updated BOBS
unit, as is the private B8 Safe source of the fifth unit. Only Close(179)
and Draw(180) RBSR stubs get redirected to verified same-unit wrappers.
A B8-to-B7 registration may occur ONLY after B7 End was armed by Draw,
and uses source-verified B7 End pointer + relative offset (never PC16
between relocated native units). No installed Lib, no ASC mutation.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from audit_ap20 import inspect,parse,walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import RBSR,repack_ap20,unpack_ap20
from build_m19_b8_safe_lifecycle_in_memory import build_b8_safe_lifecycle
from m19_b7m2_close_reset_emit import emit_close_reset
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_b8_safe_lifecycle_emit import emit_b8_safe_lifecycle
from m19_b8_cross_unit_arm_emit import emit_b8_cross_unit_arm

PREV_SHA='8800e55f0ea0865a3b8042cb8457f27bfbf7684b84ca7d90874baec472c6a744'
BOBS,CLOSE,DRAW,B8=177,179,180,181
TITLE=(b'AMOSPro AGA M19 B8 PRIVATE B7/B8 callback trampoline SOURCE ONLY\0'
       b'$VER: B8 B7 Close/Draw/End trampoline UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_b7_trampoline() -> tuple[bytes,dict]:
    base,base_meta=build_b8_safe_lifecycle()
    if base_meta['sha256']!=PREV_SHA or len(base)!=112276:
        raise ValueError('B8 native Safe/Close provenance mismatch')
    tokens,parts,_=unpack_ap20(base)
    b7old,b7old_labels=emit_close_reset()
    b7new,b7new_labels=emit_b8_b7_hooks()
    b8old,_=emit_b8_safe_lifecycle()
    b8new,b8new_labels=emit_b8_cross_unit_arm()
    if (not b7new.startswith(b7old) or not b8new.startswith(b8old)
            or not parts[BOBS].endswith(b7old)
            or parts[B8]!=DISPATCH_V2+b8old):
        raise ValueError('Frozen B7/B8 native ancestry mismatch')
    if (len(parts)!=182 or len(b7new)>=32766 or len(b8new)>=32766):
        raise ValueError('Native section count or intra-unit size error')

    origin=len(parts[BOBS])-len(DISPATCH_V2)-len(b7old)
    for index,label in ((CLOSE,'b7m2_close_reset_entry'),
                        (DRAW,'b7_multiframe_draw_entry')):
        old=parts[index]
        if (not old.startswith(RBSR) or len(old) not in (8,12)
                or old[6:8]!=b'\x4e\x75'
                or unpack_from('>HH',old,2)
                   !=(BOBS,origin+b7old_labels[label])):
            raise ValueError('B7-m2 public stub origin or ABI changed')

    updated=list(parts)
    updated[BOBS]+=b7new[len(b7old):]
    for index,name in ((CLOSE,'b8_b7_close_trampoline_entry'),
                       (DRAW,'b8_b7_draw_trampoline_entry')):
        old=parts[index]
        offset=origin+b7new_labels[name]
        if offset>=len(updated[BOBS])-len(DISPATCH_V2) or offset&1:
            raise ValueError('New BOBS trampoline target invalid')
        updated[index]=RBSR+pack('>HH',BOBS,offset)+old[6:]
    updated[B8]=DISPATCH_V2+b8new
    if (len(updated[BOBS])>=MAX_UNIT_BYTES
            or len(updated[B8])>=MAX_UNIT_BYTES
            or updated[BOBS][:len(parts[BOBS])]!=parts[BOBS]
            or updated[B8][:len(parts[B8])]!=parts[B8]):
        raise ValueError('Native groups size or frozen prefixes changed')
    for i in range(182):
        if i not in (BOBS,CLOSE,DRAW,B8) and updated[i]!=parts[i]:
            raise ValueError('Protected AP20 section mutated')

    candidate=repack_ap20(base,tokens,updated,TITLE)
    if unpack_ap20(candidate)!=(tokens,updated,TITLE):
        raise ValueError('AP20 binary roundtrip failed')
    old_api,new_api=inspect(parse(base)),inspect(parse(candidate))
    if old_api['issues'] or new_api['issues'] or old_api['tokens']!=new_api['tokens']:
        raise ValueError('Public commands/signatures changed')
    groups=[i for i,p in enumerate(updated) if p.startswith(DISPATCH_V2)]
    if groups!=[142,153,156,177,181]:
        raise ValueError('Native groups changed')
    oldpc=pc16_displacements(parts)
    pc16=pc16_displacements(updated)
    if max(map(abs,pc16.values()))>=32766:
        raise ValueError('Compiler GRouB signed PC16 exceeded')
    if any(t['name'] in ('aga bob clear','aga bob update') for t in walk_tokens(tokens)):
        raise ValueError('Premature public B8 API token')
    return candidate,dict(
        size=len(candidate),sha256=sha256(candidate).hexdigest(),
        previous_sha=PREV_SHA,public_commands=86,ap20_entries=182,
        native_groups=groups,old_pc16_max=max(map(abs,oldpc.values())),
        pc16_max=max(map(abs,pc16.values())),
        bobs_group_bytes=len(updated[BOBS]),fifth_group_bytes=len(updated[B8]),
        bobs_suffix_bytes=len(b7new)-len(b7old),
        fifth_suffix_bytes=len(b8new)-len(b8old),
        close_stub_index=CLOSE,draw_stub_index=DRAW,
        close_offset=origin+b7new_labels['b8_b7_close_trampoline_entry'],
        draw_offset=origin+b7new_labels['b8_b7_draw_trampoline_entry'],
        end_offset=origin+b7new_labels['b8_b7_end_trampoline_entry'],
        register_delta=b7new_labels['b8_b7_register_entry']-
                       b7new_labels['b7_end_entry'],
        arm_offset=b8new_labels['b8_service_arm_b7_entry'],
        no_new_tokens=True,source_only=True,installed_lib='UNCHANGED',
        active_asc='UNCHANGED',last_good='UNCHANGED',
        gate_a='CPU TEST REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED')

if __name__=='__main__':
    from pprint import pprint
    _,report=build_b8_b7_trampoline()
    print('M19 B8 callback-derived B7 Close/Draw/End AP20 SOURCE ONLY')
    pprint(report)
