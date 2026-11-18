#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B7-m2 SOURCE ONLY: restore Bob-slot reset before guarded Screen Close.

Append a small MC68020 entry after the byte-exact installed B7-m1 native
source. This does not change the old BOBS object table, bridge, End hook,
Draw/Swap, public tokens, or the working library. The AP20 builder redirects
ONLY the existing public Aga Screen Close instruction stub to this entry.

P0e used relay_reset_entry before Screen Close. The B5 guarded Close wrapper
skipped that reset; after B7-m1 closes, objects 3..16 remain active and a
second run's frame preflight can reject their obsolete source-bank stamps.
"""
from __future__ import annotations

from m68k_emit import Code, D
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle_multiframe


def emit_close_reset() -> tuple[bytes, dict[str, int]]:
    previous, labels = emit_end_lifecycle_multiframe()
    required = ('relay_reset_entry', 'registry_cpu_guard',
                'guarded_close_entry', 'b7_multiframe_draw_entry')
    if any(name not in labels for name in required):
        raise ValueError('B7-m1 prerequisite native entry missing')

    c = Code()
    c.raw(previous.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    L('b7m2_close_reset_entry')
    c.raw('48e7fffe')  # AMOS instruction ABI: preserve D0-D7/A0-A6.
    B(1, 'registry_cpu_guard')  # MC68020+ before cross-unit access.
    c.tst(D(0)); B(7, 'b7m2_close_return')
    B(1, 'relay_reset_entry')  # Clear ALL 64 P0e slots while Screen is live.
    c.tst(D(3)); B(7, 'b7m2_close_return')
    B(1, 'guarded_close_entry')  # Keep B5's checked preclose/Safe/Disp/guard.
    L('b7m2_close_return')
    c.raw('4cdf7fff4e75')  # Restore entire instruction ABI, RTS.

    native = c.out()
    assert native.startswith(previous)
    assert c.labels['b7m2_close_reset_entry'] == len(previous)
    assert len(native) % 2 == 0 and len(native) < 32766
    return native, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    binary, labels = emit_close_reset()
    print('M19 B7-m2 RESET BEFORE GUARDED CLOSE SOURCE ONLY',
          len(binary), sha256(binary).hexdigest(),
          labels['b7m2_close_reset_entry'],
          'NO library switch, NO WinUAE/Compiler claim')
