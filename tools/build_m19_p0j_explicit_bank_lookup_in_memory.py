#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b1: source-only AP20 V2 explicit-bank staged context lookup."""
from __future__ import annotations
from hashlib import sha256
from compiler_relocation import repack_ap20,unpack_ap20
from audit_ap20 import inspect,parse
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0j_frame_image_preflight_in_memory import build as build_p0ja
from m19_p0j_frame_image_preflight_emit import emit_image_preflight
from m19_p0j_explicit_bank_lookup_emit import emit_explicit_bank_lookup

P0JA_SHA='4d43956a5dfbc1ae9cb1baf7058f48e6748f8bf80ef948fcc6b0a1872960a4ab'
P0JB1_BYTES=99280
P0JB1_SHA256='757025bbcf846694d8ecc0377a28fa08344d9b82964501dfdc4a7f0c4b6c171e'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0j-b1 EXPLICIT PER-BANK CHIP LOOKUP SOURCE ONLY\0'
       b'$VER: AGA P0j-b1 uninstalled private bank lookup\0')
TITLE+=bytes(len(TITLE)&1)

def build() -> tuple[bytes,dict]:
    source,meta=build_p0ja()
    if len(source)!=98652 or sha256(source).hexdigest()!=P0JA_SHA:
        raise ValueError('P0j-a exact provenance mismatch')
    tokens,parts,_=unpack_ap20(source)
    old,_=emit_image_preflight()
    native,labels=emit_explicit_bank_lookup()
    if len(parts)!=178 or not parts[BOBS].endswith(old):
        raise ValueError('Expected P0j-a pinned BOBS source tail')
    suffix=native[len(old):]
    new=list(parts);new[BOBS]+=suffix
    if (not suffix or len(suffix)&1 or len(new[BOBS])>MAX_UNIT_BYTES or
            new[:BOBS]!=parts[:BOBS]):
        raise ValueError('P0j-b1 changed historical AP20 unit or ABI')
    result=repack_ap20(source,tokens,new,TITLE)
    tk,pt,ttl=unpack_ap20(result)
    if (tk,pt,ttl)!=(tokens,new,TITLE):
        raise ValueError('P0j-b1 AP20/HUNK repack not byte stable')
    a,b=inspect(parse(source)),inspect(parse(result))
    if a['issues'] or b['issues'] or [(x['name'],x['signature']) for x in a['tokens']]!=[(x['name'],x['signature']) for x in b['tokens']]:
        raise ValueError('P0j-b1 public token drift')
    groups=[i for i,p in enumerate(pt) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(pt)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('P0j-b1 V2 island PC16 overflow')
    if (len(result)!=P0JB1_BYTES or sha256(result).hexdigest()!=P0JB1_SHA256
            or len(suffix)!=626 or max(map(abs,links.values()))!=854):
        raise ValueError('P0j-b1 rebuilt AP20 source SHA/size/PC16 drift')
    return result,dict(
        sha256=sha256(result).hexdigest(),size=len(result),
        appended=len(suffix),public_commands=85,ap20_entries=178,
        native_groups=groups,max_pc16=max(map(abs,links.values())),
        explicit_lookup_entry=labels['explicit_bank_lookup_entry'],
        installed_lib='UNCHANGED',public_draw='NOT EXPOSED',
        gate_a='MC68020 NATIVE TEST REQUIRED',gate_b='NOT TESTED',
        gate_c='NOT TESTED')

if __name__=='__main__':
    print('M19 P0j-b1 AP20 SOURCE ONLY',build()[1])
