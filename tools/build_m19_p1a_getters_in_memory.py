#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1a: append three AMOS numeric functions to exact promoted P0, IN MEMORY.

Zero changes to the P0 code, P0 public tokens, tests/current, or LAST_GOOD.
New functions are one-argument AMOS numeric expressions, not instructions.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from

from audit_ap20 import inspect, parse, token, walk_tokens
from compiler_relocation import GETP, RBSR, unpack_ap20, repack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_b8_s1_bank_free_in_memory import build_bank_free
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters, FIELDS, INVALID

P0_SHA = 'f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d'
BOBS = 177
BASE_ENTRIES = 185
API = (('aga x bob', 'x'), ('aga y bob', 'y'), ('aga i bob', 'image'))
TITLE = (b'AMOSPro AGA M19 P1a Bob X/Y/I getters MC68020 SOURCE ONLY\0'
         b'$VER: AMOSPro_AGA M19 P1a Gate A UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build_p1a() -> tuple[bytes, dict]:
    old, previous = build_bank_free()
    if (len(old) != 117896 or sha256(old).hexdigest() != P0_SHA
            or previous['sha256'] != P0_SHA
            or previous['pc16_max'] != 31092):
        raise ValueError('Promoted P0 Bank Free source provenance drift')
    tokens, parts, _ = unpack_ap20(old)
    if len(parts) != BASE_ENTRIES or not parts[BOBS].startswith(DISPATCH_V2):
        raise ValueError('Unexpected P0 five-native-group AP20 structure')
    old_native, _ = emit_b8_s1_bank_free()
    native, labels = emit_m19_p1a_getters()
    if (not native.startswith(old_native) or
            not parts[BOBS].endswith(old_native)):
        raise ValueError('P0 BOBS source is not the exact proven native suffix')
    before = inspect(parse(old))
    if before['issues']:
        raise ValueError('P0 public ABI failed audit')
    if any(row['name'] in {name for name, _ in API}
           for row in walk_tokens(tokens)):
        raise ValueError('P1a public functions already tokenized')

    entries = list(parts)
    origin = len(parts[BOBS]) - len(DISPATCH_V2) - len(old_native)
    entries[BOBS] += native[len(old_native):]
    if (len(entries[BOBS]) >= MAX_UNIT_BYTES or
            not entries[BOBS].startswith(parts[BOBS])):
        raise ValueError('P1a native group exceeded AP20 or broke P0 prefix')

    # In AMOS, GetP precedes each parameterized entry in the merged stream.
    # Exactly three new 1-arg function entries: previous index 184 gets GetP.
    if not entries[184].endswith(b'\x4e\x75'):
        raise ValueError('P0 Bank Free entry no longer ends in RTS')
    entries[184] += GETP
    targets = {}
    new_tokens = tokens[:-6]
    for i, (name, field) in enumerate(API):
        index = BASE_ENTRIES + i
        target = origin + labels['p1a_get_' + field + '_entry']
        if (target < 0 or target & 1 or
                target >= len(entries[BOBS]) - len(DISPATCH_V2) or
                target > 65535):
            raise ValueError('P1a native target not Compiler V2 addressable')
        stub = RBSR + pack('>HH', BOBS, target) + b'\x4e\x75'
        if i < len(API) - 1:
            stub += GETP
        entries.append(stub)
        new_tokens += token(name, 1, index, '00')
        targets[name] = (BOBS, target, index)
    new_tokens += tokens[-6:]

    candidate = repack_ap20(old, new_tokens, entries, TITLE)
    if unpack_ap20(candidate) != (new_tokens, entries, TITLE):
        raise ValueError('P1a AP20 repack roundtrip mismatch')
    after = inspect(parse(candidate))
    if after['issues'] or after['tokens'][:-3] != before['tokens']:
        raise ValueError(('P1a changed original token signatures', after['issues']))
    if any((row['name'], row['instruction'], row['function'], row['signature'])
           != (name, 1, BASE_ENTRIES + i, '00')
           for i, ((name, _), row) in enumerate(zip(API, after['tokens'][-3:]))):
        raise ValueError('P1a tokens are not exact numeric 1-argument functions')
    if (len(entries) != 188 or len(after['tokens']) != len(before['tokens']) + 3 or
            entries[184] != parts[184] + GETP or
            entries[185][-4:] != GETP or entries[186][-4:] != GETP or
            entries[187][-2:] != b'\x4e\x75'):
        raise ValueError('P1a GetP/RTS placement wrong')
    if any(entries[i] != parts[i] for i in range(len(parts))
           if i not in (BOBS, 184)):
        raise ValueError('P1a modified historical AP20 stub')
    for name, (group, offset, index) in targets.items():
        if (unpack_from('>HH', entries[index], 2) != (group, offset)
                or not entries[index].startswith(RBSR)):
            raise ValueError('P1a relocatable function entry invalid: ' + name)

    groups = [i for i, segment in enumerate(entries)
              if segment.startswith(DISPATCH_V2)]
    spans = pc16_displacements(entries)
    pc16 = max(map(abs, spans.values()))
    if groups != [142, 153, 156, 177, 181] or pc16 >= 32766:
        raise ValueError('P1a interpreter/Compiler signed PC16 reach exceeded')
    named = [t for t in after['tokens']
             if t['name'].startswith(('aga ', 'get aga ', 'make aga ', 'no aga '))]
    if len(named) != 92:
        raise ValueError('P1a public command count differs from 89+3')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), bytes=len(candidate),
        p0_sha=P0_SHA, predecessor_sha=previous['sha256'],
        public_commands=len(named), ap20_entries=len(entries),
        native_groups=groups, pc16_max=pc16,
        appended_native_bytes=len(native)-len(old_native),
        source_native_sha=sha256(native).hexdigest(), targets=targets,
        refusal_sentinel=INVALID, source_only=True, installed=False,
        gate_a='TESTS REQUIRED', gate_b='NOT TESTED',
        gate_c='NOT TESTED', gate_d='NOT TESTED')


if __name__ == '__main__':
    candidate, report = build_p1a()
    repeat, _ = build_p1a()
    if candidate != repeat:
        raise ValueError('Non-deterministic P1a build')
    print('M19 P1a GETTERS AP20 IN MEMORY ONLY:', report)
