#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0i: source-only multibank persistent Safe back-buffer Bob renderer.

Four AP20 V2 islands preserved, 85 public commands unchanged. The
candidate is built strictly in memory from SHA-pinned P0h. Does not
install any .Lib, add a public Draw, change tests/current or promote R84.
"""
from __future__ import annotations
from hashlib import sha256
from audit_ap20 import inspect,parse
from compiler_relocation import repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0h_frame_preflight_in_memory import build as build_p0h
from m19_p0h_frame_preflight_emit import emit_frame_preflight
from m19_p0i_multibank_draw_emit import emit_multibank_paint

BASE_SHA='2c5c371754a3b54c797c7b413769ef2536db92cdad7eba3db8185bb88dea7782'
BOBS=177
TITLE=(b'AMOSPro AGA M19 P0i PRIVATE MULTIBANK SAFE DRAW SOURCE ONLY\0'
       b'$VER: AMOSPro_AGA P0i internal back buffer Blitter UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)

def build()->tuple[bytes,dict]:
    old,meta=build_p0h()
    if sha256(old).hexdigest()!=BASE_SHA or len(old)!=97248:
        raise ValueError('P0h four-island ancestry mismatch')
    tokens,parts,_=unpack_ap20(old)
    previous,previous_labels=emit_frame_preflight()
    updated_native,labels=emit_multibank_paint()
    if len(parts)!=178 or not parts[BOBS].endswith(previous):
        raise ValueError('P0h BOBS island prefix changed')
    suffix=updated_native[len(previous):]
    updated=list(parts)
    updated[BOBS]+=suffix
    if (not suffix or len(suffix)&1 or len(updated[BOBS])>MAX_UNIT_BYTES
            or any(updated[i]!=parts[i] for i in range(BOBS))):
        raise ValueError('Native private-only appendix changed old group')
    candidate=repack_ap20(old,tokens,updated,TITLE)
    tok2,parts2,title2=unpack_ap20(candidate)
    if (tok2,parts2,title2)!=(tokens,updated,TITLE):
        raise ValueError('Unstable AP20 HUNK reconstruction')
    old_api,new_api=inspect(parse(old)),inspect(parse(candidate))
    if (old_api['issues'] or new_api['issues']
            or [(t['name'],t['signature']) for t in old_api['tokens']]
             !=[(t['name'],t['signature']) for t in new_api['tokens']]):
        raise ValueError('Unexpected new AMOS token/API changed')
    groups=[i for i,p in enumerate(parts2) if p.startswith(DISPATCH_V2)]
    links=pc16_displacements(parts2)
    if groups!=[142,153,156,177] or max(map(abs,links.values()))>=1000:
        raise ValueError('Unsafe native island PC16 layout')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),size=len(candidate),
        predecessor_sha=meta['sha256'],native_groups=groups,
        public_commands=85,ap20_entries=len(parts2),
        new_native_bytes=len(suffix),one_entry=labels['routed_paint_one_entry'],
        all_entry=labels['routed_paint_all_entry'],
        max_pc16=max(map(abs,links.values())),
        distribution='SOURCE ONLY',public_draw='NOT EXPOSED',
        gate_a='NATIVE CPU TEST REQUIRED',gate_b='NOT TESTED',
        gate_c='NOT TESTED',gate_d='NOT TESTED')

if __name__=='__main__':
    print('M19 P0i PRIVATE MULTIBANK DRAW AP20 SOURCE ONLY',build()[1])
