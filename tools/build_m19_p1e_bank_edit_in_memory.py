#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build the transactional P1e public API without replacing the active Lib."""
from hashlib import sha256
from struct import pack, pack_into, unpack_from

from active_library import P1D_SHA
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token, walk_tokens
from build_m19_p1d_limit_bob_in_memory import build_p1d
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP, RBSR, repack_ap20, unpack_ap20
from m19_p0c_screen_close_bridge_emit import AGA_STATE_OFFSET
from m19_p1d_limit_bob_emit import emit_limit_bobs
from m19_p1e_bank_edit_emit import OBJECT, ROOT, STAMP, emit_bank_edit

BOBS = 181
API = (('aga del bob', '00,0,0', 'p1e_del_bob'),
       ('aga ins bob', '00,0,0,0,0', 'p1e_ins_bob'))
TITLE = b'AMOSPro AGA M19 P1e Bob Bank Edit MC68020\0$VER: AMOSPro_AGA M19 P1e\0'
TITLE += bytes(len(TITLE) % 2)


def build_p1e():
    base, p1d = build_p1d()
    assert p1d['sha256'] == P1D_SHA
    tokens, old, _ = unpack_ap20(base)
    original, _ = emit_limit_bobs(p1d['context_delta'])
    native, labels = emit_bank_edit(p1d['context_delta'])
    assert old[BOBS].endswith(original)
    core = old[142]
    assert all(0 <= AGA_STATE_OFFSET + n <= len(core) for n in (ROOT, OBJECT, STAMP + 64*16))
    assert core[AGA_STATE_OFFSET + ROOT:AGA_STATE_OFFSET + OBJECT + 64*24] == bytes(8 + 64*24)
    assert core[AGA_STATE_OFFSET + STAMP:AGA_STATE_OFFSET + STAMP + 64*16] == bytes(64*16)
    prefix = len(old[BOBS]) - len(original)
    extended = old[BOBS][:prefix] + native
    assert len(extended) < MAX_UNIT_BYTES

    # Keep the three trailing BOBS stubs before the enlarged group.
    # Their original negative PC16 displacements would exceed the limit.
    order = [*range(181), 182, 183, 184, None, None, None, None, 181, *range(185, len(old))]
    remap = {previous: index for index, previous in enumerate(order) if previous is not None}
    parts = []
    for index in order:
        if index is None:
            j = len(parts) - 184
            if j % 2 == 0:
                parts.append(GETP)
            else:
                entry = API[j // 2][2]
                offset = prefix - len(DISPATCH_V2) + labels[entry]
                parts.append(RBSR + pack('>HH', remap[BOBS], offset) + b'\x4e\x75')
            continue
        item = extended if index == BOBS else old[index]
        if item.startswith(RBSR):
            group = unpack_from('>H', item, 2)[0]
            item = item[:2] + pack('>H', remap[group]) + item[4:]
        parts.append(item)
    updated = bytearray(tokens[:-6])
    expected_tokens = []
    for row in walk_tokens(tokens):
        addresses = tuple(remap[row[role]] for role in ('instruction', 'function'))
        pack_into('>HH', updated, row['offset'], *addresses)
        expected_tokens.append((row['name'], *addresses, row['signature']))
    for index, (name, signature, _) in enumerate(API):
        function = 185 + 2 * index
        updated.extend(token(name, 1, function, signature))
        expected_tokens.append((name, 1, function, signature))
    updated = bytes(updated) + tokens[-6:]
    image = repack_ap20(base, updated, parts, TITLE)
    assert unpack_ap20(image) == (updated, parts, TITLE)
    report = inspect(parse(image))
    assert not report['issues']
    assert [(r['name'], r['instruction'], r['function'], r['signature'])
            for r in report['tokens']] == expected_tokens
    bound = max(map(abs, pc16_displacements(parts).values()))
    return image, dict(sha256=sha256(image).hexdigest(), bytes=len(image),
                       entries=len(parts), commands=p1d['public_commands'] + 2, pc16_max=bound,
                       group=remap[BOBS], context_delta=p1d['context_delta'],
                       open_offset=p1d['open_offset'], old_open_offset=p1d['old_open_offset'])


if __name__ == '__main__':
    binary, meta = build_p1e()
    assert build_p1e()[0] == binary
    print('P1E_IN_MEMORY', meta)
