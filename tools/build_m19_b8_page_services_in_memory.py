#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 SOURCE ONLY: append private snapshot, Safe selector and two-page pool.

The old B7-m2 active library is reconstructed EXACTLY from native sources.
No public Clear/Update tokens, no entry redirect, no installation.
This tests the existing fourth AP20 island's remaining signed-PC16 budget.
"""
from __future__ import annotations

from hashlib import sha256

from audit_ap20 import inspect,parse
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from compiler_relocation import repack_ap20,unpack_ap20
from build_m19_b8_planar_snapshot_in_memory import build_b8_private_snapshot
from m19_b8_back_selector_emit import emit_b8_back_selector
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core
from m19_b8_snapshot_pool_emit import emit_b8_snapshot_pool

B8_COPY_SHA='849f4890608ab58529dcb452132d69ceb64118c24a4225c9f7b08afd0ac74de6'
SELECT_SHA='20be8cbd14a8cc1ae915e98afefb0f3ab6484945c79c2462b5d248b1ddd344bf'
POOL_SHA='45cc6021fd348f3723bf021cac4e3f63a5000285d9c26a07707411e8060d5213'
GROUP=177
TITLE=(b'AMOSPro AGA M19 B8 private back-page services SOURCE ONLY\0'
       b'$VER: AGA M19 B8 snapshot selector/pool UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build_b8_page_services() -> tuple[bytes,dict]:
    old,meta=build_b8_private_snapshot()
    if sha256(old).hexdigest()!=B8_COPY_SHA or meta['sha256']!=B8_COPY_SHA:
        raise ValueError('B8 planar snapshot ancestor has changed')
    tokens,parts,_=unpack_ap20(old)
    original, _=emit_planar_snapshot_core()
    combined,labels=emit_b8_back_selector()
    pool,plabels=emit_b8_snapshot_pool()
    if (not parts[GROUP].endswith(original)
            or len(combined)!=2400 or sha256(combined).hexdigest()!=SELECT_SHA
            or labels['b8_checked_back_selector_entry']!=len(original)
            or len(pool)!=1172 or sha256(pool).hexdigest()!=POOL_SHA
            or plabels['b8_pool_bind_entry']!=0):
        raise ValueError('B8 source ancestry/selector/pool changed')
    suffix=combined[len(original):]+pool
    revised=list(parts)
    revised[GROUP]=parts[GROUP]+suffix
    if (len(revised[GROUP])>=MAX_UNIT_BYTES
            or any(revised[i]!=parts[i] for i in range(len(parts)) if i!=GROUP)):
        raise ValueError('B8 private page services do not fit protected 4-island layout')
    candidate=repack_ap20(old,tokens,revised,TITLE)
    assert unpack_ap20(candidate)==(tokens,revised,TITLE)
    before,after=inspect(parse(old)),inspect(parse(candidate))
    if before['issues'] or after['issues'] or before['tokens']!=after['tokens']:
        raise ValueError('B8 changed public token/GetP signatures')
    groups=[i for i,p in enumerate(revised) if p.startswith(DISPATCH_V2)]
    spans=pc16_displacements(revised)
    pc16=max(map(abs,spans.values()))
    if groups!=[142,153,156,177] or pc16>=32766:
        raise ValueError('B8 AP20 Compiler signed-PC16 budget exceeded')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),size=len(candidate),
        predecessor_sha=B8_COPY_SHA,base_b7m2_sha=meta['base_sha256'],
        appended_bytes=len(suffix),selector_bytes=len(combined)-len(original),
        pool_bytes=len(pool),bobs_bytes=len(revised[GROUP]),pc16_max=pc16,
        headroom=32766-pc16,public_commands=86,ap20_entries=181,
        native_groups=groups,installed='NO',last_good='UNCHANGED',
        tokens_clear_update='ABSENT',
        gate_a='PRIVATE COMPONENTS AND AP20 FORMAT PASS ONLY',
        gate_b='NOT TESTED',gate_c='NOT TESTED',gate_d='NOT TESTED')


if __name__=='__main__':
    from pprint import pprint
    _,res=build_b8_page_services()
    print('M19 B8 private snapshot selector/pool 4-island candidate')
    pprint(res)
