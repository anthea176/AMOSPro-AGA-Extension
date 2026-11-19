#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 full first Update + public Clear/Update AP20 candidate, memory only.

The B7-m2 and validated B8 registered Update are immutable predecessors.
Only the historical Aga Bob SET AP20 stub is rebound to B7's no-draw
End armer; new zero-argument numerical Clear and Update tokens target
verified native entries in the existing fifth group. No installed Lib.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse, token, walk_tokens
from compiler_relocation import RBSR, repack_ap20, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_atomic_registered_update_in_memory import build_b8_atomic_registered_update
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update
from m19_b8_first_update_emit import emit_b8_b7_first_update, emit_b8_first_update

BASE_SHA = '62b9d3236197d5b7340237278719d3caa17b0b3df456c4bbe300c03d801dcae2'
BOBS, B8 = 177, 181
CLEAR, UPDATE = 182, 183
TITLE = (b'AMOSPro AGA M19 B8 candidate first Clear Update MC68020\0'
         b'$VER: AMOSPro_AGA M19 B8 Clear Update CANDIDATE\0')
TITLE += bytes(len(TITLE) & 1)


def build_b8_first_update() -> tuple[bytes, dict]:
    base, meta = build_b8_atomic_registered_update()
    if (meta['sha256'] != BASE_SHA or len(base) != 115180
            or sha256(base).hexdigest() != BASE_SHA):
        raise ValueError('Unchanged B8 atomic registered source is not exact')
    tokens, parts, _ = unpack_ap20(base)
    if len(parts) != 182 or parts[B8][:len(DISPATCH_V2)] != DISPATCH_V2:
        raise ValueError('Expected five pinned B7/B8 AP20 islands')
    old7, old7lab = emit_b8_b7_hooks()
    new7, new7lab = emit_b8_b7_first_update()
    old8, _ = emit_b8_atomic_registered_update()
    new8, new8lab = emit_b8_first_update()
    if (not new7.startswith(old7) or not new8.startswith(old8)
            or not parts[BOBS].endswith(old7)
            or parts[B8] != DISPATCH_V2 + old8):
        raise ValueError('Native source ancestry or original BOBS position changed')

    old_tokens = inspect(parse(base))
    if old_tokens['issues']:
        raise ValueError('Baseline token audit issues')
    bob = [t for t in old_tokens['tokens'] if t['name'] == 'aga bob']
    if len(bob) != 1 or bob[0]['signature'] != 'I0,0,0,0':
        raise ValueError('Missing original public Aga Bob SET contract')
    setter = bob[0]['instruction']
    old_stub = parts[setter]
    origin = len(parts[BOBS]) - len(DISPATCH_V2) - len(old7)
    if (not old_stub.startswith(RBSR) or len(old_stub) not in (8, 12)
            or old_stub[6:8] != b'\x4e\x75'
            or unpack_from('>HH', old_stub, 2)
                 != (BOBS, origin + old7lab['public_aga_bob_entry'])):
        raise ValueError('Original Aga Bob setter AP20 ABI/stub not source pinned')
    if any(t['name'] in ('aga bob clear', 'aga bob update')
           for t in walk_tokens(tokens)):
        raise ValueError('Clear/Update public token already present')
    changed = list(parts)
    changed[BOBS] += new7[len(old7):]
    changed[B8] += new8[len(old8):]
    if (len(changed[BOBS]) >= MAX_UNIT_BYTES
            or len(changed[B8]) >= MAX_UNIT_BYTES):
        raise ValueError('New native group exceeds AP20 V2 copy size')

    def stub(group, offset, tail=b'\x4e\x75'):
        if not (0 <= offset < len(changed[group]) - len(DISPATCH_V2)) or offset & 1:
            raise ValueError('Source-relative AP20 entry offset invalid')
        return RBSR + pack('>HH', group, offset) + tail

    setter_target = origin + new7lab['b8_b7_bob_set_bootstrap_entry']
    changed[setter] = stub(BOBS, setter_target, old_stub[6:])
    changed.append(stub(B8, new8lab['b8_service_clear_guard_entry']))
    changed.append(stub(B8, new8lab['b8_service_update_first_entry']))
    if len(changed) != 184:
        raise ValueError('Bad new AP20 entry count')
    newtokens = (tokens[:-6]
                 + token('aga bob clear', 1, CLEAR, '0')
                 + token('aga bob update', 1, UPDATE, '0')
                 + tokens[-6:])
    candidate = repack_ap20(base, newtokens, changed, TITLE)
    if unpack_ap20(candidate) != (newtokens, changed, TITLE):
        raise ValueError('New AP20/HUNK roundtrip changed source')
    before, after = inspect(parse(base)), inspect(parse(candidate))
    if (before['issues'] or after['issues']
            or before['tokens'] != after['tokens'][:-2]):
        raise ValueError('Preexisting public AMOS signatures/indices changed')
    for index, name in ((CLEAR, 'aga bob clear'), (UPDATE, 'aga bob update')):
        values = [t for t in after['tokens'] if t['name'] == name]
        if len(values) != 1 or (
                values[0]['instruction'], values[0]['function'],
                values[0]['signature']) != (1, index, '0'):
            raise ValueError('Bad zero-argument numeric API token: ' + name)
    if any(changed[i] != parts[i] for i in range(len(parts))
           if i not in (setter, BOBS, B8)):
        raise ValueError('Protected existing AP20 code/stub altered')
    if (changed[BOBS][:len(parts[BOBS])] != parts[BOBS]
            or changed[B8][:len(parts[B8])] != parts[B8]):
        raise ValueError('B7/B8 native code prefix altered')
    groups = [i for i, p in enumerate(changed) if p.startswith(DISPATCH_V2)]
    spans = pc16_displacements(changed)
    reach = max(map(abs, spans.values()))
    if groups != [142, 153, 156, 177, 181] or reach >= 32766:
        raise ValueError('AMOS Compiler signed PC16 or native groups invalid')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), bytes=len(candidate),
        predecessor_sha=BASE_SHA, native_groups=groups, pc16_max=reach,
        public_commands=88, ap20_entries=len(changed),
        bob_setter_stub=setter, bob_setter_source_offset=setter_target,
        clear_token=CLEAR, update_token=UPDATE,
        b7_append_bytes=len(new7)-len(old7),
        b8_append_bytes=len(new8)-len(old8),
        first_draw_before_capture=False,
        b7_m2_prefix='BYTE-EXACT', b8_registered_prefix='BYTE-EXACT',
        source_only=True, installed_lib='UNCHANGED',
        active_asc='UNCHANGED', last_good='UNCHANGED',
        gate_a='CPU TEST REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED')


if __name__ == '__main__':
    from pprint import pprint
    image, info = build_b8_first_update()
    print('M19 B8 PUBLIC Clear/Update AP20 candidate IN MEMORY')
    pprint(info)
