#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build the P2b candidate from the committed P2a native emitters."""
from hashlib import sha256
from struct import pack, pack_into, unpack_from

from active_library import P2A_SHA
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token, walk_tokens
from build_m19_p1e_bank_edit_in_memory import build_p1e
from build_m19_p2a_public_in_memory import build_p2a
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from m19_p2a_public_bob_col_emit import emit_p2a_public_col
from m19_p2b_bob_flip_emit import emit_bob_flip

TITLE = b'AMOSPro AGA M19 P2b Bob Flip MC68020\0$VER: AMOSPro_AGA M19 P2b\0'
TITLE += bytes(len(TITLE) % 2)
NAME, SIGNATURE = 'aga bob flip', '00,0'


def build_p2b():
    baseline, meta = build_p2a()
    assert meta['sha256'] == P2A_SHA and sha256(baseline).hexdigest() == P2A_SHA
    _, p1e = build_p1e()
    tokens, original, _ = unpack_ap20(baseline)
    group = meta['bob_group']
    old, _ = emit_p2a_public_col(p1e['context_delta'])
    native, labels = emit_bob_flip(p1e['context_delta'])
    assert original[group].endswith(old) and original[group].startswith(DISPATCH_V2)
    prefix = len(original[group]) - len(old)
    expanded = original[group][:prefix] + native
    assert len(expanded) <= MAX_UNIT_BYTES
    function = group+1
    new_group = group+2
    offset = prefix - len(DISPATCH_V2) + labels['p2b_public_flip']
    parts = []
    for index, part in enumerate(original):
        if index == group:
            parts.extend((GETP, RBSR+pack('>HH', new_group, offset)+b'\x4e\x75'))
            part = expanded
        if part.startswith(RBSR):
            target = unpack_from('>H', part, 2)[0]
            part = part[:2]+pack('>H', target+2*(target>=group))+part[4:]
        parts.append(part)
    updated = bytearray(tokens[:-6])
    expected = []
    for row in walk_tokens(tokens):
        a, b = (row[role]+2*(row[role]>=group) for role in ('instruction', 'function'))
        pack_into('>HH', updated, row['offset'], a, b)
        expected.append((row['name'], a, b, row['signature']))
    updated.extend(token(NAME, 1, function, SIGNATURE))
    updated.extend(tokens[-6:])
    expected.append((NAME, 1, function, SIGNATURE))
    result = repack_ap20(baseline, bytes(updated), parts, TITLE)
    assert unpack_ap20(result) == (bytes(updated), parts, TITLE)
    checked = inspect(parse(result))
    assert not checked['issues'], checked['issues']
    assert [(r['name'],r['instruction'],r['function'],r['signature'])
            for r in checked['tokens']] == expected
    return result, dict(sha256=sha256(result).hexdigest(), bytes=len(result),
                        entries=len(parts), commands=meta['public_commands']+1, bob_group=new_group,
                        group_bytes=len(expanded), function=function,
                        pc16_max=max(map(abs, pc16_displacements(parts).values())))


if __name__ == '__main__':
    _, metadata = build_p2b()
    print('P2B_IN_MEMORY', metadata)
