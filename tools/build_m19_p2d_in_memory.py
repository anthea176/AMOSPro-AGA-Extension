#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build a P2d auto-update candidate in memory from the exact P2c source."""

from hashlib import sha256
from struct import pack, pack_into, unpack_from

from active_library import P2C_SHA
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token, walk_tokens
from build_m19_p1e_bank_edit_in_memory import build_p1e
from build_m19_p2c_in_memory import build_p2c
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p2c_bob_planes_emit import emit_bob_planes
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update

TITLE = b'AMOSPro AGA M19 P2d Bob Auto Update MC68020\0$VER: AMOSPro_AGA M19 P2d\0'
TITLE += bytes(len(TITLE) % 2)
NAME, SIGNATURE = 'aga bob auto update', '00'


def build_p2d():
    baseline, meta = build_p2c()
    assert sha256(baseline).hexdigest() == meta['sha256'] == P2C_SHA
    _, p1e = build_p1e()
    context = p1e['context_delta']
    tokens, old, _ = unpack_ap20(baseline)
    bobs = meta['bob_group']
    service = bobs + 1
    old_bobs, old_labels = emit_bob_planes(context)
    old_service, _ = emit_m19_p1a_getters()
    assert old[bobs].startswith(DISPATCH_V2) and old[bobs].endswith(old_bobs)
    assert old[service] == DISPATCH_V2 + old_service
    prefix = len(old[bobs]) - len(old_bobs)
    native, labels, service_offset = emit_bob_auto_update(context)
    expanded = old[bobs][:prefix] + native
    assert len(expanded) <= MAX_UNIT_BYTES
    bobs_offset = prefix - len(DISPATCH_V2)

    token_rows = list(walk_tokens(tokens))
    (swap,) = (row['function'] for row in token_rows if row['name'] == 'aga swap')
    assert unpack_from('>HH', old[swap], 2) == (
        bobs, bobs_offset + old_labels['guarded_swap_entry'])
    public_mode = bobs + 1
    service_stubs = list(range(service + 1, len(old)))
    assert all(old[i].startswith(RBSR) and unpack_from('>H', old[i], 2)[0] == service
               for i in service_stubs)
    group = bobs + 2 + len(service_stubs)

    def stub(offset, tail=b'\x4e\x75'):
        return RBSR + pack('>HH', group, offset) + tail

    parts = list(old[:bobs])
    for i, part in enumerate(parts):
        if part.startswith(RBSR) and unpack_from('>H', part, 2)[0] == bobs:
            offset = (bobs_offset + labels['p2d_public_swap'] if i == swap
                      else unpack_from('>H', part, 4)[0])
            parts[i] = stub(offset, part[6:])
    parts.extend((GETP, stub(bobs_offset + labels['p2d_public_auto_update'])))
    remap = {}
    for i in service_stubs:
        remap[i] = len(parts)
        offset = unpack_from('>H', old[i], 4)[0]
        parts.append(stub(bobs_offset + service_offset + offset, old[i][6:]))
    assert len(parts) == group
    parts.append(expanded)

    updated = bytearray(tokens[:-6])
    expected = []
    for row in token_rows:
        entries = tuple(remap.get(row[role], row[role]) for role in ('instruction', 'function'))
        assert all(entry < group for entry in entries)
        pack_into('>HH', updated, row['offset'], *entries)
        expected.append((row['name'], *entries, row['signature']))
    updated.extend(token(NAME, 1, public_mode, SIGNATURE))
    updated.extend(tokens[-6:])
    expected.append((NAME, 1, public_mode, SIGNATURE))
    binary = repack_ap20(baseline, bytes(updated), parts, TITLE)
    assert unpack_ap20(binary) == (bytes(updated), parts, TITLE)
    report = inspect(parse(binary))
    assert not report['issues'], report['issues']
    assert [(r['name'], r['instruction'], r['function'], r['signature'])
            for r in report['tokens']] == expected
    return binary, dict(sha256=sha256(binary).hexdigest(), bytes=len(binary),
                        entries=len(parts), commands=meta['commands']+1,
                        group=group, group_bytes=len(expanded), swap=swap,
                        function=public_mode, pc16_max=max(map(abs, pc16_displacements(parts).values())))


if __name__ == '__main__':
    _, metadata = build_p2d()
    print('P2D_IN_MEMORY', metadata)
