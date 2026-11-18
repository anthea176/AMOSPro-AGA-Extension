#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b7 source-only End-guard AP20 V2 candidate built IN MEMORY.

Preserve ALL public tokens and 181 entry indices from B6. Append only the
new private BOBS End lifecycle native suffix, and rebind the existing
Aga Bob Draw function stub 180 to b7_guarded_draw_entry. Original AGA
native, existing Swap/Close stubs, LAST_GOOD and dist Lib are untouched.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect,parse
from compiler_relocation import RBSR,repack_ap20,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0j_public_draw_in_memory import build as build_b6
from m19_p0j_swap_barrier_emit import emit_swap_barrier
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle, emit_end_lifecycle_multiframe

B6_SHA='3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91'
B6_NATIVE_SHA='d02eb6c89863fbb769d699296a923dc2997e2b39184c2c7d51800c28c10c1b5e'
BOBS=177
DRAW=180
TITLE=(b'AMOSPro AGA M19 P0j-b7 SAFE/DISP END LIFECYCLE SOURCE ONLY\0'
       b'$VER: AGA M19 P0j-b7 guarded Draw and End UNINSTALLED\0')
TITLE+=bytes(len(TITLE)&1)


def build()->tuple[bytes,dict]:
    base,meta=build_b6()
    if len(base)!=101476 or sha256(base).hexdigest()!=B6_SHA or meta['sha256']!=B6_SHA:
        raise ValueError('P0j-b6 source ancestry mismatch')
    tokens,parts,_=unpack_ap20(base)
    old,_=emit_swap_barrier()
    if len(old)!=20944 or sha256(old).hexdigest()!=B6_NATIVE_SHA:
        raise ValueError('P0j-b6 original native source changed')
    if len(parts)!=181 or not parts[BOBS].endswith(old):
        raise ValueError('P0j-b6 BOBS source AP20 drift')
    new,labels=emit_end_lifecycle()
    if not new.startswith(old):
        raise ValueError('P0j-b7 changed any source-native prefix')
    appended=new[len(old):]
    if not appended or len(appended)&1 or len(parts[BOBS])+len(appended)>MAX_UNIT_BYTES:
        raise ValueError('P0j-b7 BOBS native unit over compiler budget')

    old_draw_stub=parts[DRAW]
    if (not old_draw_stub.startswith(RBSR) or len(old_draw_stub)!=8
            or old_draw_stub[6:8]!=b'\x4e\x75'
            or unpack_from('>HH',old_draw_stub,2)!=(BOBS,meta['draw_native_offset'])):
        raise ValueError('Original B6 Draw stub not source-pinned')
    target=len(parts[BOBS])-len(DISPATCH_V2) + (labels['b7_guarded_draw_entry']-len(old))
    if target&1 or target<0 or target>=len(parts[BOBS])+len(appended)-len(DISPATCH_V2):
        raise ValueError('New B7 Draw target out of native unit')
    outparts=list(parts)
    outparts[BOBS]=parts[BOBS]+appended
    outparts[DRAW]=RBSR+pack('>HH',BOBS,target)+b'\x4e\x75'
    if (outparts[:BOBS]!=parts[:BOBS]
            or outparts[BOBS][:len(parts[BOBS])]!=parts[BOBS]
            or outparts[BOBS+1:DRAW]!=parts[BOBS+1:DRAW]
            or len(outparts)!=181):
        raise ValueError('B7 modified protected historical source or token stubs')

    candidate=repack_ap20(base,tokens,outparts,TITLE)
    if unpack_ap20(candidate)!=(tokens,outparts,TITLE):
        raise ValueError('B7 AP20 roundtrip failed')
    previous,audit=inspect(parse(base)),inspect(parse(candidate))
    if (previous['issues'] or audit['issues'] or previous['tokens']!=audit['tokens']):
        raise ValueError('B7 public token inventory/GetP signatures changed')
    groups=[i for i,part in enumerate(outparts) if part.startswith(DISPATCH_V2)]
    spans=pc16_displacements(outparts)
    if groups!=[142,153,156,177] or max(map(abs,spans.values()))>=32766:
        raise ValueError('B7 four-native-island PC16 budget exceeded')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),size=len(candidate),
        predecessor_sha=B6_SHA,native_sha=sha256(new).hexdigest(),
        native_bytes=len(new),appended_bytes=len(appended),
        public_commands=86,ap20_entries=181,
        native_groups=groups,pc16_max=max(map(abs,spans.values())),
        guarded_draw_stub=DRAW,guarded_draw_group=BOBS,
        guarded_draw_native_offset=target,
        guarded_draw_local_label=labels['b7_guarded_draw_entry'],
        guarded_end_local_label=labels['b7_end_entry'],
        guarded_swap_stub=meta['guarded_swap_entry'],
        guarded_close_stub=meta['guarded_close_entry'],
        public_draw='EXPERIMENTAL SOURCE ONLY',
        installed_lib='UNCHANGED',active_asc='UNCHANGED',
        gate_a='NATIVE TEST REQUIRED',gate_b='NOT TESTED',
        gate_c='NOT TESTED',gate_d='NOT TESTED')



# This experiment intentionally does NOT change build() or the canonical
# B7 bytes present in dist/AMOSPro_AGA.Lib.
MULTIFRAME_TITLE = (
    b'AMOSPro AGA M19 P0j-b7-m1 multiframe callback handoff SOURCE ONLY\0'
    b'$VER: AGA M19 P0j-b7-m1 MC68020 GATE A ONLY UNINSTALLED\0'
)
MULTIFRAME_TITLE += bytes(len(MULTIFRAME_TITLE) & 1)


def build_multiframe() -> tuple[bytes, dict]:
    """Make a transient AP20 candidate from immutable installed B7 source."""
    canonical, oldmeta = build()
    if (len(canonical) != 102072
            or oldmeta['sha256'] !=
            'f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b'):
        raise ValueError('Original B7 base is no longer source-pinned')
    tokens, parts, _ = unpack_ap20(canonical)
    old, _ = emit_end_lifecycle()
    if len(old) != 21544 or not parts[BOBS].endswith(old):
        raise ValueError('B7 native suffix changed unexpectedly')
    extended, labels = emit_end_lifecycle_multiframe()
    if not extended.startswith(old):
        raise ValueError('Multiframe implementation changed original B7 bytes')
    suffix = extended[len(old):]
    if not suffix or len(suffix) & 1 or len(parts[BOBS]) + len(suffix) > MAX_UNIT_BYTES:
        raise ValueError('Multiframe source exceeds BOBS unit capacity')
    if parts[DRAW] != (RBSR + pack('>HH', BOBS, oldmeta['guarded_draw_native_offset'])
                       + b'\x4e\x75'):
        raise ValueError('B7 Draw stub is no longer source-pinned')
    target = (len(parts[BOBS]) - len(DISPATCH_V2)
              + labels['b7_multiframe_draw_entry'] - len(old))
    if target & 1 or not 0 <= target < MAX_UNIT_BYTES:
        raise ValueError('Invalid multiframe Draw target')
    outparts = list(parts)
    outparts[BOBS] += suffix
    outparts[DRAW] = RBSR + pack('>HH', BOBS, target) + b'\x4e\x75'
    if outparts[:BOBS] != parts[:BOBS] or outparts[BOBS][:len(parts[BOBS])] != parts[BOBS]:
        raise ValueError('Multiframe modified protected prefix')
    candidate = repack_ap20(canonical, tokens, outparts, MULTIFRAME_TITLE)
    if unpack_ap20(candidate) != (tokens, outparts, MULTIFRAME_TITLE):
        raise ValueError('Multiframe AP20 roundtrip failed')
    audit = inspect(parse(candidate))
    reference = inspect(parse(canonical))
    if audit['issues'] or reference['issues'] or audit['tokens'] != reference['tokens']:
        raise ValueError('Multiframe AP20 token or ABI mismatch')
    groups = [i for i, part in enumerate(outparts) if part.startswith(DISPATCH_V2)]
    spans = pc16_displacements(outparts)
    if groups != [142, 153, 156, 177] or max(map(abs, spans.values())) >= 32766:
        raise ValueError('Multiframe PC16 or native group constraint failed')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), size=len(candidate),
        predecessor_sha=oldmeta['sha256'],
        native_sha=sha256(extended).hexdigest(),
        native_bytes=len(extended), appended_bytes=len(suffix),
        public_commands=86, ap20_entries=181, native_groups=groups,
        pc16_max=max(map(abs, spans.values())),
        guarded_draw_stub=DRAW, guarded_draw_group=BOBS,
        guarded_draw_native_offset=target,
        guarded_draw_local_label=labels['b7_multiframe_draw_entry'],
        guarded_end_local_label=labels['b7_end_entry'],
        installed_lib='UNCHANGED', active_asc='UNCHANGED',
        gate_a='NATIVE TEST REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED', gate_d='NOT TESTED')

if __name__=='__main__':
    _,meta=build()
    print('M19 P0j-b7 PRIVATE END LIFECYCLE SOURCE-ONLY AP20',meta)
