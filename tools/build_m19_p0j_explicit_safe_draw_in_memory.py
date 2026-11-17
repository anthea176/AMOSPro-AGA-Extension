#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b4: deterministic source-only AP20 V2 private 64-Bob no-shadow."""
from __future__ import annotations
from hashlib import sha256
from compiler_relocation import repack_ap20,unpack_ap20
from audit_ap20 import inspect,parse
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_p0j_explicit_image_resolve_in_memory import build as build_b3
from m19_p0j_explicit_image_resolve_emit import emit_explicit_bank_image_resolve
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw

P0JB3_SHA='90b5d69743bb93c5de9f97039e802e9bedd6866302e7b655efdde4c4a2f5e585'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0j-b4 PRIVATE NO-SHADOW 64 BOBS DRAW SOURCE ONLY\0'
       b'$VER: AMOSPro_AGA P0j-b4 private Safe/WaitBlit UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)

def build()->tuple[bytes,dict]:
    original,meta=build_b3()
    if len(original)!=99832 or sha256(original).hexdigest()!=P0JB3_SHA:
        raise ValueError('P0j-b3 exact source ancestry mismatch')
    tokens,parts,_=unpack_ap20(original)
    old,_=emit_explicit_bank_image_resolve()
    new,labels=emit_explicit_bob_draw()
    if len(parts)!=178 or not parts[BOBS].endswith(old):
        raise ValueError('P0j-b3 BOBS prefix mismatch')
    suffix=new[len(old):]
    parts2=list(parts);parts2[BOBS]+=suffix
    if not suffix or len(suffix)&1 or len(parts2[BOBS])>MAX_UNIT_BYTES or parts2[:BOBS]!=parts[:BOBS]:
        raise ValueError('P0j-b4 exceeds native V2 island or modifies prefix')
    result=repack_ap20(original,tokens,parts2,TITLE)
    if unpack_ap20(result)!=(tokens,parts2,TITLE):
        raise ValueError('P0j-b4 AP20/HUNK pack unstable')
    oa,na=inspect(parse(original)),inspect(parse(result))
    if oa['issues'] or na['issues'] or [(t['name'],t['signature']) for t in oa['tokens']]!=[(t['name'],t['signature']) for t in na['tokens']]:
        raise ValueError('P0j-b4 changes public commands')
    groups=[i for i,p in enumerate(parts2) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(parts2)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('P0j-b4 native island PC16 drift')
    return result,dict(
        sha256=sha256(result).hexdigest(),size=len(result),
        predecessor_sha=meta['sha256'],native_added=len(suffix),
        ap20_entries=178,public_commands=85,native_groups=groups,
        pc16_max=max(map(abs,links.values())),
        safe_entry=labels['explicit_safe_blit_entry'],
        draw_all_entry=labels['explicit_frame_draw_entry'],
        installed_lib='UNCHANGED',public_draw='NOT EXPOSED',
        gate_a='NATIVE CPU TEST REQUIRED',gate_b='NOT TESTED',
        gate_c='NOT TESTED',gate_d='NOT TESTED')

if __name__=='__main__':
    print('M19 P0j-b4 NO-SHADOW FRAME SOURCE ONLY',build()[1])
