#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 source-only AP20 candidate: append the proven private snapshot core.

NO Aga Bob Clear/Update tokens or complete frame lifecycle yet. This is
the byte-exact B7-m2 working Lib, extended in memory ONLY with a private
self-contained MC68020 planar copy routine. Never install this candidate.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse
from ap20_v2_island_dispatch import pc16_displacements
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from m19_b7m2_close_reset_emit import emit_close_reset
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core

BASE_SHA = '242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
CORE_SHA = '4ff797beb194e40e3c296510b6c893baaeb35cfb051d621b301ebc14d27bab06'
BOBS = 177
TITLE = (b'AMOSPro AGA M19 B8 PRIVATE snapshot core SOURCE ONLY\0'
         b'$VER: AGA M19 B8 internal snapshot UNINSTALLED\0')
TITLE += bytes(len(TITLE) & 1)


def build_b8_private_snapshot() -> tuple[bytes, dict]:
    base, meta = build_close_reset()
    if (len(base) != 102400 or meta['sha256'] != BASE_SHA
            or sha256(base).hexdigest() != BASE_SHA):
        raise ValueError('B7-m2 exact binary ancestry drift')
    tokens, parts, _ = unpack_ap20(base)
    installed, _ = emit_close_reset()
    core, labels = emit_planar_snapshot_core()
    if (len(parts) != 181 or not parts[BOBS].endswith(installed)
            or len(core) != 1800 or sha256(core).hexdigest() != CORE_SHA
            or labels['b8_planar_snapshot_core_entry'] != 0):
        raise ValueError('Installed native prefix or B8 core is not source-pinned')
    if len(parts[BOBS]) + len(core) >= MAX_UNIT_BYTES:
        raise ValueError('B8 BOBS native unit exceeds PC16 budget')
    revised = list(parts)
    revised[BOBS] = parts[BOBS] + core
    if any(revised[i] != parts[i] for i in range(len(parts)) if i != BOBS):
        raise ValueError('B8 changed a public AP20 stub')
    candidate = repack_ap20(base, tokens, revised, TITLE)
    if unpack_ap20(candidate) != (tokens, revised, TITLE):
        raise ValueError('AP20 roundtrip failed')
    a, b = inspect(parse(base)), inspect(parse(candidate))
    if a['issues'] or b['issues'] or a['tokens'] != b['tokens']:
        raise ValueError('Public tokens or signatures modified')
    groups = [i for i, part in enumerate(revised) if part.startswith(DISPATCH_V2)]
    spans = pc16_displacements(revised)
    max_pc16 = max(map(abs, spans.values()))
    if groups != [142, 153, 156, 177] or max_pc16 >= 32766:
        raise ValueError('Compiler AP20 island PC16 bounds violated')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), bytes=len(candidate),
        base_sha256=BASE_SHA, core_sha256=CORE_SHA, appended_native_bytes=len(core),
        bobs_native_entry_offset=len(parts[BOBS])-len(DISPATCH_V2),
        bobs_group_total_bytes=len(revised[BOBS]), groups=groups,
        pc16_max=max_pc16, public_commands=86, ap20_entries=181,
        installed_lib='B7-m2 UNCHANGED', active_asc='UNCHANGED',
        gate_a='PRIVATE MC68020 CORE PASS; AP20 FORMAT TESTED',
        gate_b='NOT TESTED', gate_c='NOT TESTED', gate_d='NOT TESTED')


if __name__ == '__main__':
    from pprint import pprint
    _, report = build_b8_private_snapshot()
    print('M19 B8 internal-only AP20 candidate SOURCE ONLY, NO new tokens')
    pprint(report)
