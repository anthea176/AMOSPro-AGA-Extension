#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build and audit the P1d clipping candidate from exact P1c bytes in memory."""
from hashlib import sha256
from struct import pack, pack_into, unpack_from

from active_library import P1C_SHA
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token, walk_tokens
from build_m19_p1c_bob_priority_in_memory import build_p1c
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from m19_p0c_screen_close_bridge_emit import AGA_STATE_OFFSET
from m19_p1c_bob_priority_emit import emit_priority_bobs
from m19_p1d_limit_bob_emit import TABLE_BYTES, TABLE_FROM_CONTEXT, emit_limit_bobs, emit_limit_open

NAME = 'aga limit bob'
SIGNATURE = '00,0,0,0,0'
TITLE = b'AMOSPro AGA M19 P1d Limit Bob MC68020\0$VER: AMOSPro_AGA M19 P1d\0'
TITLE += bytes(len(TITLE) % 2)
CORE, BOBS = 142, 179


def build_p1d():
    old, p1c = build_p1c()
    if sha256(old).hexdigest() != P1C_SHA:
        raise ValueError('P1c source drift')
    tokens, sections, _ = unpack_ap20(old)
    rows = list(walk_tokens(tokens))
    parts = list(sections)
    open_index = next(row['function'] for row in rows if row['name'] == 'aga screen open')
    old_open = p1c['open_offset']
    assert parts[open_index][:6] == RBSR + pack('>HH', CORE, old_open)
    table_offset = len(parts[CORE]) - len(DISPATCH_V2)
    assert len(parts[CORE]) == AGA_STATE_OFFSET + p1c['context_delta'] + TABLE_FROM_CONTEXT
    open_offset = table_offset + TABLE_BYTES
    parts[CORE] += emit_limit_open(old_open, table_offset)
    parts[open_index] = RBSR + pack('>HH', CORE, open_offset) + parts[open_index][6:]
    predecessor, _ = emit_priority_bobs(p1c['context_delta'])
    native, labels = emit_limit_bobs(p1c['context_delta'])
    assert sections[BOBS].endswith(predecessor)
    prefix = len(sections[BOBS]) - len(predecessor)
    parts[BOBS] = sections[BOBS][:prefix] + native

    for i, part in enumerate(parts):
        if part.startswith(RBSR):
            group = unpack_from('>H', part, 2)[0]
            if group >= BOBS:
                parts[i] = part[:2] + pack('>H', group + 2) + part[4:]
    stub = BOBS + 1
    target = prefix - len(DISPATCH_V2) + labels['p1d_limit_entry']
    parts[BOBS:BOBS] = [GETP, RBSR + pack('>HH', BOBS + 2, target) + b'\x4e\x75']

    updated = bytearray(tokens[:-6])
    for row in rows:
        for word, role in enumerate(('instruction', 'function')):
            address = row[role]
            if address >= BOBS:
                pack_into('>H', updated, row['offset'] + word * 2, address + 2)
    updated += token(NAME, 1, stub, SIGNATURE) + tokens[-6:]
    updated = bytes(updated)
    groups = [i for i, part in enumerate(parts) if part.startswith(DISPATCH_V2)]
    assert groups == [142, 153, 156, 181, 185]
    assert all(len(parts[g]) <= MAX_UNIT_BYTES for g in groups)
    bound = max(map(abs, pc16_displacements(parts).values()))
    candidate = repack_ap20(old, updated, parts, TITLE)
    assert unpack_ap20(candidate) == (updated, parts, TITLE)
    audited = inspect(parse(candidate))
    assert not audited['issues'] and len(parts) == 192
    expected = [(row['name'], row['instruction'] + 2 * (row['instruction'] >= BOBS),
                 row['function'] + 2 * (row['function'] >= BOBS), row['signature'])
                for row in rows]
    expected.append((NAME, 1, stub, SIGNATURE))
    assert [(r['name'], r['instruction'], r['function'], r['signature'])
            for r in audited['tokens']] == expected
    return candidate, dict(sha256=sha256(candidate).hexdigest(), bytes=len(candidate),
                           public_commands=94, ap20_entries=192, native_groups=groups,
                           pc16_max=bound, old_open_offset=old_open,
                           open_offset=open_offset, limit_offset=target,
                           context_delta=p1c['context_delta'])


if __name__ == '__main__':
    binary, metadata = build_p1d()
    assert build_p1d()[0] == binary
    print('P1D_SOURCE_ONLY', metadata)
