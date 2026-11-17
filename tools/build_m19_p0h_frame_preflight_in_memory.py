#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0h: source-only 64-Bob preflight with AP20 V2 island relayout.

P0g exact source first, append ONLY the BOBS private frame preflight,
then apply source-verified AP20 V2 island dispatcher. That is essential:
the pre-islands P0g PC16 reach is 32590, too near the 32766 boundary for
a new >176-byte routine. Retain all public signatures and four native
groups, no installed Lib/ASC or untested public Draw.
"""
from __future__ import annotations

from hashlib import sha256

from audit_ap20 import inspect, parse
from ap20_v2_island_dispatch import dispatch_islands, pc16_displacements
from build_m19_p0g_checked_read_in_memory import build as build_p0g
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20
from m19_p0g_checked_read_emit import emit_checked_read
from m19_p0h_frame_preflight_emit import emit_frame_preflight

BOBS, AGA = 93, 94
BASE_SHA = 'e1f8f8c04e24a38651ade50b6878cffb1dd288a766b104fb5c9fa9ae314d9536'
TITLE = (b'AMOSPro AGA M19 P0h 64 BOBS PRIVATE PREFLIGHT MC68020 SOURCE ONLY\0'
         b'$VER: M19 P0h AP20 V2 private check only UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    predecessor, meta = build_p0g()
    if meta['sha256'] != BASE_SHA or len(predecessor) != 96752:
        raise ValueError('P0g base provenance changed')
    tokens, parts, _ = unpack_ap20(predecessor)
    old_native, _ = emit_checked_read()
    new_native, labels = emit_frame_preflight()
    if (len(parts) != 95 or not parts[BOBS].endswith(old_native)
            or not new_native.startswith(old_native)):
        raise ValueError('P0g BOBS native prefix mismatch')
    suffix = new_native[len(old_native):]
    if not suffix or len(suffix)&1 or len(new_native) >= 32766:
        raise ValueError('P0h invalid native suffix')
    updated = list(parts)
    updated[BOBS] += suffix
    if (len(updated[BOBS]) > MAX_UNIT_BYTES or
            updated[AGA] != parts[AGA] or updated[:BOBS] != parts[:BOBS]):
        raise ValueError('P0h damaged historical native code/entries')
    source_only = repack_ap20(predecessor,tokens,updated,TITLE)
    if unpack_ap20(source_only) != (tokens,updated,TITLE):
        raise ValueError('Pre-islands HUNK/AP20 roundtrip failed')
    islands, layout = dispatch_islands(source_only,title=TITLE)
    actual_tokens, actual_parts, actual_title = unpack_ap20(islands)
    if actual_title != TITLE or actual_parts[layout.group_map[BOBS]] != updated[BOBS]:
        raise ValueError('P0h BOBS source bytes were altered by AP20 islands')
    for old_idx in [i for i,p in enumerate(parts) if p.startswith(DISPATCH_V2)]:
        desired = updated[old_idx] if old_idx == BOBS else parts[old_idx]
        if actual_parts[layout.group_map[old_idx]] != desired:
            raise ValueError('An unrelated native unit changed')
    old_api, new_api = inspect(parse(predecessor)), inspect(parse(islands))
    if (old_api['issues'] or new_api['issues'] or
            [(x['name'],x['signature']) for x in old_api['tokens']] !=
            [(x['name'],x['signature']) for x in new_api['tokens']]):
        raise ValueError('Public API name/signature drift')
    if len(actual_parts) != layout.entries or len(actual_parts) <= len(parts):
        raise ValueError('AP20 source islands missing')
    groups = [i for i,p in enumerate(actual_parts) if p.startswith(DISPATCH_V2)]
    links = pc16_displacements(actual_parts)
    if len(groups) != 4 or max(map(abs,links.values())) >= 1000:
        raise ValueError('AP20 island PC16 margin is not safe')
    if len([t for t in new_api['tokens'] if t['name'].startswith('aga ')]) < 60:
        raise ValueError('Incomplete AMOS public token table')
    return islands, dict(
        sha256=sha256(islands).hexdigest(),size=len(islands),
        base_sha=meta['sha256'],public_commands=85,
        ap20_entries=len(actual_parts),native_groups=groups,
        bob_native_group=layout.group_map[BOBS],
        appended_bytes=len(suffix),frame_entry=labels['frame_bank_preflight_entry'],
        interpreter_pc16=max(map(abs,links.values())),
        active_dist='UNCHANGED',public_draw='NOT IMPLEMENTED',
        draw_status='IDENTITY PREFLIGHT ONLY, NO CHIP OR BLIT',
        gate_a='SOURCE STRUCTURE; CPU TEST REQUIRED',
        gate_b='NOT TESTED',gate_c='NOT TESTED')


if __name__=='__main__':
    blob,meta=build()
    print('M19 P0h MC68020 AP20 ISLANDS PRIVATE FRAME PREFLIGHT SOURCE ONLY',meta)
