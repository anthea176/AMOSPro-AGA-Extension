#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j stage 1: AP20 V2 source-only image preflight before any DMA."""
from __future__ import annotations
from hashlib import sha256
from compiler_relocation import repack_ap20,unpack_ap20
from audit_ap20 import inspect,parse
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_p0i_multibank_draw_in_memory import build as build_p0i
from m19_p0i_multibank_draw_emit import emit_multibank_paint
from m19_p0j_frame_image_preflight_emit import emit_image_preflight

P0I_SHA='004a04f9819fc2df9498ec8887e3de8a6533a7f620f04743c1fa1ae6ee872fa4'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0j PRIVATE IMAGE GATE PRE-DMA SOURCE ONLY\0'
       b'$VER: AMOSPro_AGA P0j image preflight UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build()->tuple[bytes,dict]:
    source,meta=build_p0i()
    if len(source)!=97820 or sha256(source).hexdigest()!=P0I_SHA:
        raise ValueError('P0i image provenance mismatch')
    tokens,parts,_=unpack_ap20(source)
    old,_=emit_multibank_paint()
    native,labels=emit_image_preflight()
    if len(parts)!=178 or not parts[BOBS].endswith(old):
        raise ValueError('Expected pinned P0i BOBS tail')
    suffix=native[len(old):]
    new=list(parts);new[BOBS]+=suffix
    if (not suffix or len(suffix)&1 or len(new[BOBS])>MAX_UNIT_BYTES
            or any(new[i]!=parts[i] for i in range(BOBS))):
        raise ValueError('P0j changed pre-existing AP20 native unit')
    result=repack_ap20(source,tokens,new,TITLE)
    tok2,parts2,title2=unpack_ap20(result)
    if (tok2,parts2,title2)!=(tokens,new,TITLE):
        raise ValueError('AP20 V2 roundtrip failed')
    a,b=inspect(parse(source)),inspect(parse(result))
    if (a['issues'] or b['issues'] or
            [(t['name'],t['signature']) for t in a['tokens']] !=
            [(t['name'],t['signature']) for t in b['tokens']]):
        raise ValueError('P0j public AMOS API drift')
    groups=[i for i,p in enumerate(parts2) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(parts2)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('P0j AP20 PC16 V2 island drift')
    return result,dict(sha256=sha256(result).hexdigest(),size=len(result),
        predecessor_sha=meta['sha256'],appended=len(suffix),
        public_commands=85,ap20_entries=len(parts2),native_groups=groups,
        max_pc16=max(map(abs,links.values())),
        image_gate=labels['image_frame_preflight_entry'],
        checked_draw=labels['routed_paint_prechecked_entry'],
        installed_lib='UNCHANGED',public_draw='NOT EXPOSED',
        selection_shadow='P0i TEMPORARY PROJECTION STILL PRESENT',
        gate_a='PENDING MC68020 TEST',gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    print('M19 P0j IMAGE PREFLIGHT AP20 SOURCE ONLY',build()[1])
