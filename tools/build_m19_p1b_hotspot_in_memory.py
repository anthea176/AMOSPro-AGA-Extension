#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b source-built AP20 Hot Spot renderer, candidate IN MEMORY ONLY.

Never consume or patch the binary from dist/. Rebuild exact P1a from its
verified source. Change one source-labelled Safe join BRA displacement in
BOBS group177 and append a private checked hotspot bridge. Zero public
tokens, zero AP20 entry/ABI changes; other 187 entries byte-identical.
No active Lib / LAST_GOOD / ASC is written by this builder.
"""
from __future__ import annotations
from hashlib import sha256
from audit_ap20 import inspect,parse
from compiler_relocation import unpack_ap20,repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p1a_getters_in_memory import build_p1a,P1A_SHA
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p1b_hotspot_draw_emit import emit_p1b_hotspot_draw

BOBS=177
P1B_SHA='2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4'
P1B_BYTES=119176
P1B_NATIVE_SHA='dde935fec04682989c90ea60fd12d40c75b77e8c1e307a93746f078123c1c7ab'
TITLE=(b'AMOSPro AGA M19 P1b Bob Hot Spot Safe Blitter MC68020 CANDIDATE\0'
       b'$VER: AMOSPro_AGA M19 P1b HOTSPOT MC68020 GATE A\0')
TITLE+=bytes(len(TITLE)&1)

def build_p1b()->tuple[bytes,dict]:
    previous,p1a=build_p1a()
    if sha256(previous).hexdigest()!=P1A_SHA or len(previous)!=118816:
        raise ValueError('P1b predecessor P1a builder SHA/length drift')
    toks,parts,_=unpack_ap20(previous)
    if len(parts)!=188 or not parts[BOBS].startswith(DISPATCH_V2):
        raise ValueError('P1b expected exactly five P1a AP20 islands')
    old,_=emit_b8_s1_bank_free()
    native,labels=emit_p1b_hotspot_draw()
    prefix_len=len(parts[BOBS])-len(old)
    if prefix_len<=len(DISPATCH_V2) or not parts[BOBS].endswith(old):
        raise ValueError('P1b exact P1a BOBS native prefix missing')
    new_parts=list(parts)
    new_parts[BOBS]=parts[BOBS][:prefix_len]+native
    if len(new_parts[BOBS])>=MAX_UNIT_BYTES:
        raise ValueError('P1b AP20 BOBS unit overflow')
    if any(new_parts[i]!=parts[i] for i in range(len(parts)) if i!=BOBS):
        raise ValueError('P1b touched unrelated AP20 sections')
    image=repack_ap20(previous,toks,new_parts,TITLE)
    rt,rec,_title=unpack_ap20(image)
    if rt!=toks or rec!=new_parts or _title!=TITLE:
        raise ValueError('P1b AP20 pack/unpack non-reproducible')
    audit1,audit2=inspect(parse(previous)),inspect(parse(image))
    if audit1['issues'] or audit2['issues'] or audit1['tokens']!=audit2['tokens']:
        raise ValueError('P1b damaged 92 public AMOS commands or signatures')
    commands=[x for x in audit2['tokens']
              if x['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
    groups=[i for i,p in enumerate(new_parts) if p.startswith(DISPATCH_V2)]
    spans=pc16_displacements(new_parts)
    bound=max(map(abs,spans.values()))
    if len(commands)!=92 or groups!=[142,153,156,177,181] or bound>=32766:
        raise ValueError('P1b wrong API group or Compiler PC16 overflow')
    if (len(image)!=P1B_BYTES or sha256(image).hexdigest()!=P1B_SHA
            or sha256(native).hexdigest()!=P1B_NATIVE_SHA or bound!=31444):
        raise ValueError('Pinned P1b MC68020 full Safe-Blitter native/AP20 SHA drift')
    return image,dict(bytes=len(image),sha256=sha256(image).hexdigest(),
       predecessor_sha=P1A_SHA,public_commands=len(commands),
       ap20_entries=len(new_parts),native_groups=groups,pc16_max=bound,
       bobs_group_bytes=len(new_parts[BOBS]),old_bobs_native_bytes=len(old),
       new_bobs_native_bytes=len(native),native_offset=prefix_len,
       source_patch_site=labels['p1b_source_patch_site'],
       join_offset=prefix_len+labels['p1b_image_hotspot_join'],
       origin_offset=prefix_len+labels['p1b_hotspot_origin_entry'],
       native_sha256=sha256(native).hexdigest(),
       last_good='UNCHANGED',installed=False,
       gate_a='TESTS REQUIRED',gate_b='NOT TESTED',gate_c='NOT TESTED',
       gate_d='NOT TESTED')

if __name__=='__main__':
    image,meta=build_p1b()
    if build_p1b()[0]!=image:
        raise ValueError('P1b in-memory rebuild mismatch')
    print('P1B_BUILDER_META',meta,flush=True)
