#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19: append a fifth AP20 V2 unit, preserving ALL existing 178 entries.

Source-only proof; reads but NEVER writes dist/, tests/current/, archives or
LAST_GOOD. Two disposable zero-argument functions call the fifth unit, one
at native unsigned offset >32768. No existing native unit is moved/rebuilt;
the old AP20 code is an exact byte prefix of the experimental candidate.

A future real WinUAE/Compiler V2 B/C run will require a separate authorized
switch of the unique canonical dist/AMOSPro_AGA.Lib and active test ASC.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack_from
from pathlib import Path

from audit_ap20 import inspect, parse, token
from active_library import P1E_SHA, P2D_SHA, P2DL2_SHA, P2DL2B_SHA, S1P1E_SHA, SPRITE_L2B_HISTORICAL_SHAS
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_ap20_islands_in_memory import build as build_islands, ISLAND_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import RBSR, GETP, repack_ap20, unpack_ap20
from m19_ap20_unit5_emit import emit_fifth_native, DATA, DATA_BYTES, EXPECTED_SUM, FAR_SIGNATURE

BASE_ENTRIES = 178
UNIT5_SUM = 178
UNIT5_TAIL = 179
UNIT5_GROUP = 180
FUNCTIONS = (('aga unit five sum', 1, UNIT5_SUM, '0'),
             ('aga unit five tail', 1, UNIT5_TAIL, '0'))
RTS = bytes.fromhex('4e75')
UNIT5_CANDIDATE_SHA256 = '967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1'
UNIT5_CANDIDATE_BYTES = 138044
TITLE = (b'AMOSPro AGA M19 AP20 V2 FIVE UNITS MC68020 SOURCE ONLY\0'
         b'$VER: M19 AP20 V2 five unit diagnostic EXPERIMENT UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build() -> tuple[bytes, dict]:
    active_path=Path(__file__).resolve().parents[1]/'dist/AMOSPro_AGA.Lib'
    active_before=active_path.read_bytes()
    old_raw, old_meta = build_islands()
    assert len(old_raw) == 96908 and sha256(old_raw).hexdigest() == ISLAND_SHA
    old_tokens, old_parts, _ = unpack_ap20(old_raw)
    if len(old_parts) != BASE_ENTRIES or old_tokens[-6:] != bytes(6):
        raise ValueError('Active four-unit AP20 base has unexpected structure')
    original = inspect(parse(old_raw))
    if original['issues'] or len(original['tokens']) != 86:
        raise ValueError('Four-unit token ABI drift')
    groups = [i for i, p in enumerate(old_parts) if p.startswith(DISPATCH_V2)]
    if groups != [142, 153, 156, 177]:
        raise ValueError(f'Expected four frozen islands, got {groups}')
    for i in groups:
        if len(old_parts[i]) > MAX_UNIT_BYTES:
            raise ValueError('Existing Compiler V2 unit over 65534')

    code, labels = emit_fifth_native()
    near_offset, tail_offset = labels['unit5_sum'], labels['unit5_tail']
    if near_offset != 0 or tail_offset != 41012 or tail_offset <= 32768:
        raise ValueError('Fifth unit must exercise unsigned V2 deep offset')
    unit = DISPATCH_V2 + code
    if len(unit) != 41060 or len(unit) & 1 or len(unit) > MAX_UNIT_BYTES:
        raise ValueError('Fifth unit beyond Compiler V2 65534-byte bound')

    new_parts = old_parts + [
        RBSR + pack('>HH', UNIT5_GROUP, near_offset) + RTS,
        RBSR + pack('>HH', UNIT5_GROUP, tail_offset) + RTS,
        unit
    ]
    if new_parts[:BASE_ENTRIES] != old_parts:
        raise ValueError('Attempt to shift an existing AP20 entry')
    if any(new_parts[i] != old_parts[i] for i in groups):
        raise ValueError('Existing native group changed')
    if new_parts[UNIT5_SUM].endswith(GETP) or new_parts[UNIT5_TAIL].endswith(GETP):
        raise ValueError('Zero-argument diagnostics must not request GetP')

    new_tokens = old_tokens[:-6] + b''.join(token(*fn) for fn in FUNCTIONS) + bytes(6)
    image = repack_ap20(old_raw, new_tokens, new_parts, TITLE)
    if len(image) != UNIT5_CANDIDATE_BYTES or sha256(image).hexdigest() != UNIT5_CANDIDATE_SHA256:
        raise ValueError('Fifth-unit in-memory candidate SHA256/size drift')
    actual_tokens, actual_parts, actual_title = unpack_ap20(image)
    if actual_parts != new_parts or actual_tokens != new_tokens or actual_title != TITLE:
        raise ValueError('AP20 HUNK re-pack not byte-identical')
    report = inspect(parse(image))
    if report['issues'] or report['tokens'][:86] != original['tokens']:
        raise ValueError('Old public token ABI/indices modified')
    for spec, row in zip(FUNCTIONS, report['tokens'][-2:]):
        name, ins, fun, sig = spec
        if (row['name'], row['instruction'], row['function'], row['signature']) != spec:
            raise ValueError('New public function token incorrectly installed')
    # Structural interpretation has all historical links exactly unchanged.
    before = pc16_displacements(old_parts)
    after = pc16_displacements(actual_parts)
    if {i:after[i] for i in before} != before or max(map(abs,after.values())) != 854:
        raise ValueError('Changed an existing PC16 link or exceeded budget')
    if after[UNIT5_SUM] != 14 or after[UNIT5_TAIL] != 6:
        raise ValueError('Fifth-unit relay is not immediately local')
    if unpack_from('>HH', actual_parts[UNIT5_TAIL], 2) != (UNIT5_GROUP, tail_offset):
        raise ValueError('Deep native entry was truncated/signed')
    if actual_parts[UNIT5_GROUP][len(DISPATCH_V2)+labels['unit5_data']:
                                 len(DISPATCH_V2)+tail_offset] != DATA:
        raise ValueError('Table payload mutated')
    if b''.join(actual_parts[:BASE_ENTRIES]) != b''.join(old_parts):
        raise ValueError('Existing native code position shifted')
    if len(report['tokens']) != 88 or sum(p.startswith(DISPATCH_V2) for p in actual_parts)!=5:
        raise ValueError('Unexpected fifth-group layout')
    if (active_path.read_bytes()!=active_before or
        sha256(active_before).hexdigest() not in (ISLAND_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA,P2DL2_SHA,P2DL2B_SHA,S1P1E_SHA,*SPRITE_L2B_HISTORICAL_SHAS)):
        raise ValueError('Active installable Lib was changed during source-only build')
    return image, dict(
        sha256=sha256(image).hexdigest(), size=len(image),
        base_sha=ISLAND_SHA, base_size=len(old_raw),
        ap20_entries=len(actual_parts), public_commands=87,
        native_groups=groups+[UNIT5_GROUP], unit5_bytes=len(unit),
        table_bytes=DATA_BYTES, sum_expected=EXPECTED_SUM,
        far_expected=FAR_SIGNATURE, far_unsigned_offset=tail_offset,
        old_pc16=max(map(abs,before.values())),
        new_pc16=max(map(abs,after.values())),
        new_pc16_near=after[UNIT5_SUM], new_pc16_far=after[UNIT5_TAIL],
        gate_a='SOURCE STRUCTURE ONLY UNTIL TESTS PASS',
        gate_b='NOT TESTED', gate_c='NOT TESTED',
        distribution='IN MEMORY; NO ACTIVE LIB/ASC CHANGE',
        labels=labels)


if __name__ == '__main__':
    _raw, _meta=build()
    print('M19 AP20 V2 FIFTH NATIVE UNIT SOURCE-ONLY',
          {k:v for k,v in _meta.items() if k!='labels'})
