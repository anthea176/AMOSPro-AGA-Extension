#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1a: three public numeric Bob getters, source-only MC68020.

Exact P0 Bank Free code is preserved as a binary prefix. The only new
execution path calls the P0e checked/relocatable object_bridge_read_entry.
A Bob's source bank remains stored in the existing 24-byte object slot.
No graphics, DMA, bank mutation or Swap; no new installed .Lib.

AMOS argument: D3=N. Result: D2=0, D3=signed X/Y or image ID.
Failure: D3=-32769 (strictly outside both X/Y and image domains).
Preserve all other AMOS registers and A3; use 32 stack-local output bytes
so the private bridge never receives a shared or stale output pointer.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free

INVALID = -32769
FIELDS = dict(x=8, y=12, image=4)
assert INVALID < -32768

def emit_m19_p1a_getters() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_b8_s1_bank_free()
    if 'object_bridge_read_entry' not in labels:
        raise ValueError('P0 checked Bob read bridge missing')
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label
    for name, offset in FIELDS.items():
        prefix = 'p1a_get_' + name
        L(prefix + '_entry')
        c.raw('48e7efee')           # MOVEM.L original AMOS caller registers
        c.raw('4fefffe0')           # 32-byte local read record on stack
        c.move(D(3), D(0))          # D3 is the sole numeric argument, Bob N
        c.move(A(7), A(1))          # 24-byte private output, aligned stack
        B(1, 'object_bridge_read_entry')
        c.tst(D(3))                 # bridge status 1=active, 0=invalid/off
        B(7, prefix + '_fail')
        c.move(M(7, offset), D(3))  # original 32-bit X/Y or image
        B(0, prefix + '_return')
        L(prefix + '_fail')
        c.move(I(INVALID), D(3))
        L(prefix + '_return')
        c.raw('4fef0020')          # discard local record
        c.raw('4cdf77f7')          # restore all AMOS regs except D2,D3
        c.raw('74004e75')          # D2=0; numeric result D3; RTS
    native = c.out()
    if (not native.startswith(old) or len(native) & 1
            or len(native) >= 32766
            or c.labels['p1a_get_x_entry'] != len(old)):
        raise ValueError('P1a native prefix, alignment, or PC16 guard')
    if len(native) - len(old) > 256:
        raise ValueError('P1a getter wrappers unexpectedly large')
    return native, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    source, labels = emit_m19_p1a_getters()
    print('M19 P1a BOB X/Y/IMAGE MC68020 SOURCE ONLY',
          len(source), sha256(source).hexdigest(),
          {name: labels['p1a_get_' + name + '_entry']
           for name in FIELDS}, 'NO installed Lib or WinUAE validation')
