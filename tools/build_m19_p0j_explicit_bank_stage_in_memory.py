#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b2 in-memory 4-island AP20 V2 explicit Chip staging candidate."""
from __future__ import annotations
from hashlib import sha256
from compiler_relocation import repack_ap20,unpack_ap20
from audit_ap20 import inspect,parse
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from build_m19_p0j_explicit_bank_lookup_in_memory import build as build_b1
from m19_p0j_explicit_bank_lookup_emit import emit_explicit_bank_lookup
from m19_p0j_explicit_bank_stage_emit import emit_explicit_bank_stage

BASE_SHA='757025bbcf846694d8ecc0377a28fa08344d9b82964501dfdc4a7f0c4b6c171e'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0j-b2 EXPLICIT CHIP STAGE SOURCE ONLY\0'
       b'$VER: AGA P0j-b2 private stage UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)

def build()->tuple[bytes,dict]:
    base,meta=build_b1()
    if len(base)!=99280 or sha256(base).hexdigest()!=BASE_SHA:
        raise ValueError('P0j-b1 source ancestry mismatch')
    tokens,parts,_=unpack_ap20(base)
    old,_=emit_explicit_bank_lookup()
    native,labels=emit_explicit_bank_stage()
    if len(parts)!=178 or not parts[BOBS].endswith(old):
        raise ValueError('P0j-b1 native prefix changed')
    suffix=native[len(old):]
    new=list(parts);new[BOBS]+=suffix
    if not suffix or len(suffix)&1 or len(new[BOBS])>MAX_UNIT_BYTES or new[:BOBS]!=parts[:BOBS]:
        raise ValueError('P0j-b2 invalid private native suffix')
    result=repack_ap20(base,tokens,new,TITLE)
    if unpack_ap20(result)!=(tokens,new,TITLE):
        raise ValueError('P0j-b2 AP20 HUNK roundtrip drift')
    a,b=inspect(parse(base)),inspect(parse(result))
    if a['issues'] or b['issues'] or [(x['name'],x['signature']) for x in a['tokens']]!=[(x['name'],x['signature']) for x in b['tokens']]:
        raise ValueError('P0j-b2 changed public AMOS API')
    groups=[i for i,p in enumerate(new) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(new)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('P0j-b2 native AP20 island PC16 drift')
    return result,dict(sha256=sha256(result).hexdigest(),size=len(result),
      predecessor=meta['sha256'],appended=len(suffix),public_commands=85,
      ap20_entries=178,native_groups=groups,max_pc16=max(map(abs,links.values())),
      stage_entry=labels['explicit_checked_stage_entry'],
      prepare_entry=labels['explicit_registry_prepare_entry'],
      gate_a='NATIVE TEST REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED',
      installed_lib='UNCHANGED',public_draw='NOT IMPLEMENTED')

if __name__=='__main__':
    print('M19 P0j-b2 explicit Chip AP20 SOURCE ONLY',build()[1])
