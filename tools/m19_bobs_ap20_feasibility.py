#!/usr/bin/env python3
"""Structural-only AP20 token feasibility for M19 Bank and Get AGA Bob.

Rebuilds the exact R88 archive IN MEMORY with two inert CPU placeholders.
DO NOT install the produced bytes. This proves neither WinUAE nor Compiler.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tools' / 'experiments')]
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from active_library import R84_SHA, R88_SHA

PROTECTED = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
EXPERIMENT = ROOT / 'dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib'
BANK = 84
CAPTURE = 85
GROUP_BOBS = 88
COMMANDS = (
    ('aga bob bank', BANK, 1, 'I0'),
    ('get aga bob', CAPTURE, 1, 'I0,0,0,0,0'),
)
# Deliberately inert: MOVEQ #0,D3 / MOVEQ #0,D2 / RTS.
# This is NOT a native implementation of either new command.
INERT = bytes.fromhex('760074004e75')
TITLE = b'M19 AP20 STRUCTURAL FEASIBILITY ONLY - NEVER INSTALL\0'
TITLE += bytes(len(TITLE) & 1)


def probe() -> dict:
    protected = PROTECTED.read_bytes()
    old = EXPERIMENT.read_bytes()
    if sha256(protected).hexdigest() != R84_SHA:
        raise ValueError('R84 LAST_GOOD differs')
    if sha256(old).hexdigest() != R88_SHA:
        raise ValueError('R88 candidate differs')
    source = inspect(parse(old))
    if source['issues'] or len(source['tokens']) != 79:
        raise ValueError('original AP20 contract differs')
    original_tokens, original_parts, _ = unpack_ap20(old)
    if len(original_parts) != 88 or original_parts[83].endswith(GETP):
        raise ValueError('R88 public entry mismatch')
    if not original_parts[86].startswith(DISPATCH_V2):
        raise ValueError('not a R88 Compiler V2 Bob unit')

    stubs = []
    for i, old_stub in enumerate(original_parts[:84]):
        if old_stub in (b'', GETP):
            stubs.append(old_stub)
            continue
        if not (old_stub[:2] == RBSR and len(old_stub) in (8, 12)
                and old_stub[6:8] == bytes.fromhex('4e75')):
            raise ValueError(f'unsupported original AP20 stub {i}')
        group, offset = unpack_from('>HH', old_stub, 2)
        if group not in (84, 85, 86, 87):
            raise ValueError(f'unknown native group {group}')
        stubs.append(RBSR + pack('>HH', group + 2, offset) + old_stub[6:])
    stubs[-1] += GETP
    bank_offset = len(original_parts[86]) - len(DISPATCH_V2)
    cap_offset = bank_offset + len(INERT)
    stubs.append(RBSR + pack('>HH', GROUP_BOBS, bank_offset)
                 + bytes.fromhex('4e75') + GETP)
    stubs.append(RBSR + pack('>HH', GROUP_BOBS, cap_offset)
                 + bytes.fromhex('4e75'))
    groups = [original_parts[84], original_parts[85],
              original_parts[86] + INERT + INERT, original_parts[87]]
    packed = repack_ap20(
        old,
        original_tokens[:-6] + b''.join(token(*item) for item in COMMANDS)
        + bytes(6), stubs + groups, TITLE)
    report = inspect(parse(packed))
    if report['issues'] or report['tokens'][:-2] != source['tokens']:
        raise ValueError(('token or prior ABI regression', report['issues']))
    observed = [(r['name'], r['instruction'], r['function'], r['signature'])
                for r in report['tokens'][-2:]]
    if observed != list(COMMANDS):
        raise ValueError('new AP20 tokens differ')
    for index, count in ((BANK, 1), (CAPTURE, 5)):
        if not any(p['index'] == index and p['parameters'] == count and
                   p['getp'] for p in report['parameter_checks']):
            raise ValueError(f'GetP missing for entry {index}')
    if any(len(group) > 65534 for group in groups):
        raise ValueError('AP20 V2 unit overflow')
    links = interpreter_rbsr_displacements(stubs + groups)
    if max(map(abs, links.values())) >= 32766:
        raise ValueError('Interpreter BSR.W out of range')
    return {
        'tokens': [v[0] for v in COMMANDS],
        'public_commands': len(report['tokens']) - 1,
        'ap20_entries': len(stubs) + len(groups),
        'bob_unit_bytes': len(groups[2]),
        'bob_unit_margin': 65534 - len(groups[2]),
        'max_interpreter_displacement': max(map(abs, links.values())),
        'verdict': 'STRUCTURAL AP20 FEASIBILITY ONLY; NO NATIVE GATE'
    }


if __name__ == '__main__':
    print('M19 AP20 FEASIBILITY:', probe())
