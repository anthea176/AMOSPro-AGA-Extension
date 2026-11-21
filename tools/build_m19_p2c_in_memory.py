#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Build P2c Bob Planes from the validated P2b baseline in memory."""

from active_library import P2B_SHA
from build_m19_p1e_bank_edit_in_memory import build_p1e
from build_m19_p2b_in_memory import build_p2b, extend_bob_api
from m19_p2b_bob_flip_emit import emit_bob_flip
from m19_p2c_bob_planes_emit import emit_bob_planes

TITLE = b'AMOSPro AGA M19 P2c Bob Planes MC68020\0$VER: AMOSPro_AGA M19 P2c\0'
TITLE += bytes(len(TITLE) % 2)


def build_p2c():
    baseline, meta = build_p2b()
    assert meta['sha256'] == P2B_SHA
    _, p1e = build_p1e()
    context = p1e['context_delta']
    old, _ = emit_bob_flip(context)
    native, labels = emit_bob_planes(context)
    return extend_bob_api(baseline, meta['bob_group'], meta['commands'], old,
                          native, labels['p2c_public_planes'], 'aga bob planes', '00,0', TITLE)


if __name__ == '__main__':
    _, meta = build_p2c()
    print('P2C_IN_MEMORY', meta)
