#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only 4-unit AP20 V2 image resolver using explicit AGBO bank."""
from __future__ import annotations
from hashlib import sha256
from compiler_relocation import repack_ap20,unpack_ap20
from audit_ap20 import inspect,parse
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_p0j_explicit_bank_stage_in_memory import build as build_b2
from m19_p0j_explicit_bank_stage_emit import emit_explicit_bank_stage
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve

P0JB2_SHA='8e1ef5daccde882aa78adb93c13108ee0d085063540920cbecfa80b4dddaad8d'
P0JB3_BYTES=99832
P0JB3_SHA256='90b5d69743bb93c5de9f97039e802e9bedd6866302e7b655efdde4c4a2f5e585'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0j-b3 EXPLICIT BANK IMAGE RESOLVER SOURCE ONLY\0'
       b'$VER: AMOSPro_AGA P0j-b3 native private descriptor UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)

def build() -> tuple[bytes,dict]:
    original,meta=build_b2()
    if len(original)!=99672 or sha256(original).hexdigest()!=P0JB2_SHA:
        raise ValueError('P0j-b2 exact AP20 source provenance lost')
    tokens,parts,_=unpack_ap20(original)
    old,_=emit_explicit_bank_stage()
    new_native,labels=emit_explicit_bank_image_resolve()
    if len(parts)!=178 or not parts[BOBS].endswith(old):
        raise ValueError('Expected P0j-b2 BOBS unit prefix not found')
    suffix=new_native[len(old):]
    new=list(parts);new[BOBS]+=suffix
    if not suffix or len(suffix)&1 or len(new[BOBS])>MAX_UNIT_BYTES or new[:BOBS]!=parts[:BOBS]:
        raise ValueError('P0j-b3 native island code changed')
    result=repack_ap20(original,tokens,new,TITLE)
    if unpack_ap20(result)!=(tokens,new,TITLE):
        raise ValueError('P0j-b3 AP20/HUNK repack not byte exact')
    original_api,new_api=inspect(parse(original)),inspect(parse(result))
    if original_api['issues'] or new_api['issues'] or [(t['name'],t['signature']) for t in original_api['tokens']]!=[(t['name'],t['signature']) for t in new_api['tokens']]:
        raise ValueError('P0j-b3 public API change')
    groups=[i for i,p in enumerate(new) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(new)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('P0j-b3 PC16/dispatch island budget exceeded')
    if (len(result)!=P0JB3_BYTES or sha256(result).hexdigest()!=P0JB3_SHA256
            or len(suffix)!=130 or max(map(abs,links.values()))!=854):
        raise ValueError('P0j-b3 AP20 canonical source SHA/size drift')
    return result,dict(
        sha256=sha256(result).hexdigest(),size=len(result),
        previous_sha=meta['sha256'],appended=len(suffix),
        ap20_entries=178,public_commands=85,native_groups=groups,
        pc16_max=max(map(abs,links.values())),
        resolver_entry=labels['explicit_image_resolve_entry'],
        installable='UNCHANGED',public_draw='NOT EXPOSED',
        gate_a='NATIVE TEST REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED')

if __name__=='__main__':
    print('M19 P0j-b3 AP20 SOURCE-ONLY IMAGE RESOLVER',build()[1])
