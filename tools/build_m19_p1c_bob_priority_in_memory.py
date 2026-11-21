#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Rebuild P1b and assemble the P1c priority candidate in memory."""
from hashlib import sha256
from struct import pack, pack_into, unpack_from

from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token, walk_tokens
from build_m19_p1b_hotspot_in_memory import BOBS, P1B_SHA, build_p1b
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from m19_p0c_screen_close_bridge_emit import AGA_STATE_OFFSET
from m19_p1b_hotspot_draw_emit import emit_p1b_hotspot_draw
from m19_p1c_bob_priority_emit import emit_priority_bobs, emit_priority_open

NAME = 'aga bob priority'
TITLE = b'AMOSPro AGA M19 P1c Bob Priority MC68020\0$VER: AMOSPro_AGA M19 P1c\0'
TITLE += bytes(len(TITLE) % 2)


def build_p1c():
    source, _ = build_p1b()
    if sha256(source).hexdigest() != P1B_SHA:
        raise ValueError('P1b build drift')
    tokens, parts, _ = unpack_ap20(source)
    rows = list(walk_tokens(tokens))
    open_index = next(row['function'] for row in rows if row['name'] == 'aga screen open')
    if not parts[open_index].startswith(RBSR):
        raise ValueError('Expected source-linked Screen Open')
    core, open_offset = unpack_from('>HH', parts[open_index], 2)
    if (core, open_offset) != (142, 1102):
        raise ValueError('P1b Screen Open layout drift')
    core_size = len(parts[core]) - len(DISPATCH_V2)
    open_code, context = emit_priority_open(open_offset, core_size)
    context_delta = len(DISPATCH_V2) + context - AGA_STATE_OFFSET
    native, labels = emit_priority_bobs(context_delta)
    original, old_labels = emit_p1b_hotspot_draw()
    prefix = len(parts[BOBS]) - len(original)
    if not parts[BOBS].endswith(original):
        raise ValueError('P1b BOBS ancestry drift')
    entry = old_labels['explicit_frame_draw_entry']
    if native[:entry] != original[:entry] or native[entry+8:len(original)] != original[entry+8:]:
        raise ValueError('Unexpected changes to P1b BOBS')
    changed = list(parts)
    changed[core] += open_code
    changed[BOBS] = parts[BOBS][:prefix] + native
    changed[open_index] = RBSR + pack('>HH', core, core_size) + parts[open_index][6:]

    # Keep the parameter marker and the new stub immediately before BOBS.
    # Update AP20 group references and token indices at or after the insertion.
    for i, part in enumerate(changed):
        if part.startswith(RBSR):
            group = unpack_from('>H', part, 2)[0]
            if group >= BOBS:
                changed[i] = part[:2] + pack('>H', group + 2) + part[4:]
    priority_offset = prefix - len(DISPATCH_V2) + labels['p1c_priority_entry']
    changed[BOBS:BOBS] = [
        GETP, RBSR + pack('>HH', BOBS + 2, priority_offset) + b'\x4e\x75',
    ]
    updated = bytearray(tokens[:-6])
    for row in rows:
        for word, role in enumerate(('instruction', 'function')):
            index = row[role]
            if index >= BOBS:
                pack_into('>H', updated, row['offset'] + 2 * word, index + 2)
    updated += token(NAME, 1, BOBS + 1, '00') + tokens[-6:]
    updated = bytes(updated)
    groups = [i for i, part in enumerate(changed) if part.startswith(DISPATCH_V2)]
    if groups != [142, 153, 156, 179, 183] or any(len(changed[g]) > MAX_UNIT_BYTES for g in groups):
        raise ValueError('P1c native-unit layout or size invalid')
    pc16 = max(map(abs, pc16_displacements(changed).values()))
    candidate = repack_ap20(source, updated, changed, TITLE)
    if unpack_ap20(candidate) != (updated, changed, TITLE):
        raise ValueError('P1c AP20 round trip failed')
    audited = inspect(parse(candidate))
    actual = audited['tokens']
    expected_tokens = [
        (row['name'], row['instruction'] + 2 * (row['instruction'] >= BOBS),
         row['function'] + 2 * (row['function'] >= BOBS), row['signature'])
        for row in rows
    ]
    expected_tokens.append((NAME, 1, BOBS + 1, '00'))
    if (audited['issues'] or len(changed) != 190
            or [(row['name'], row['instruction'], row['function'], row['signature'])
                for row in actual] != expected_tokens):
        raise ValueError('P1c AP20 API audit failed')
    return candidate, dict(bytes=len(candidate), sha256=sha256(candidate).hexdigest(),
                           pc16_max=pc16, ap20_entries=len(changed), native_groups=groups,
                           public_commands=93, context_delta=context_delta,
                           open_offset=core_size, priority_offset=priority_offset)


if __name__ == '__main__':
    binary, metadata = build_p1c()
    if build_p1c()[0] != binary:
        raise ValueError('P1c candidate is not reproducible')
    print('P1C_SOURCE_ONLY', metadata)
