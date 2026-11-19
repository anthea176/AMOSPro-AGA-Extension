#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A format/provenance check for B8 SOURCE-ONLY AP20 native suffix."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect, parse, walk_tokens
from compiler_relocation import unpack_ap20
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from build_m19_b8_planar_snapshot_in_memory import build_b8_private_snapshot
from m19_b8_planar_snapshot_emit import emit_planar_snapshot_core

ROOT = Path(__file__).resolve().parents[1]


def main():
    active = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
    current = (ROOT / 'tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc').read_bytes()
    assert len(active) == 102400
    assert sha256(active).hexdigest() == '242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
    assert len(current) == 10911
    assert sha256(current).hexdigest() == 'a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec'
    base, _ = build_close_reset()
    assert base == active
    candidate, meta = build_b8_private_snapshot()
    assert candidate != active and meta['base_sha256'] == sha256(active).hexdigest()
    assert meta['appended_native_bytes'] == 1800
    assert meta['public_commands'] == 86 and meta['ap20_entries'] == 181
    assert meta['groups'] == [142,153,156,177] and meta['pc16_max'] < 32766
    core, _ = emit_planar_snapshot_core()
    assert sha256(core).hexdigest() == meta['core_sha256']
    tok_old, oldparts, _ = unpack_ap20(base)
    tok_new, newparts, _ = unpack_ap20(candidate)
    assert tok_old == tok_new and len(newparts) == len(oldparts) == 181
    assert newparts[177] == oldparts[177] + core
    assert all(newparts[i] == oldparts[i] for i in range(181) if i != 177)
    assert inspect(parse(candidate))['tokens'] == inspect(parse(active))['tokens']
    assert len([t for t in walk_tokens(tok_new)
                if t['name'] in ('aga bob clear','aga bob update')]) == 0
    print('M19 B8 PRIVATE candidate AP20 Gate A PASS, no token/Lib/ASC change;',meta)


if __name__ == '__main__':
    main()
