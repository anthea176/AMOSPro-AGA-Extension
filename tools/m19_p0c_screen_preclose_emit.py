#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c: PRIVATE screen-preclose guard, NOT an installed Screen Close hook.

Append source-only code to the verified per-bank BOBS native registry. Entry
screen_preclose_entry reads the REAL AGA state pointer from A5+0x1c8, obtains
graphics.library base from State+8, then calls registry_close_entry BEFORE
the caller performs any destructive CloseWindow/Screen/Library operation.

AMOS A5 is the current owner. A4 is ignored (not a trusted GfxBase input).
Returns D2=0, D3=1 when Chip+registry cleanup is finished, otherwise D3=0
without touching legacy screen/window or calling Aga Swap. A failed close
MUST NOT proceed to the legacy destructive Screen Close call.

The screen-close API stub still points to the original AGA native unit.
This is a source-backed prerequisite for a future verified cross-unit hook.
The original AGA R88 .s partial restoration is AUDIT-ONLY, NOT a patch base.
No AP20 edit, no new installed library, no WinUAE/Compiler proof.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0c_bank_registry_emit import emit_bank_registry

STATE_PTR_A5 = 0x1c8       # R74/R88 AGA state pointer in AMOS A5
GFX_BASE_OFF = 8          # State+8; still valid before legacy Close
FRAME = 64
F = dict(state=0,gfx=4,result=8,state_end=12)


def emit_screen_preclose() -> tuple[bytes, dict[str, int]]:
    prefix, old_labels = emit_bank_registry()
    c = Code()
    c.raw(prefix.hex())
    c.labels.update(old_labels)
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(2, F[name]))

    def G(name, dst):
        c.move(M(2, F[name]), dst)

    L('screen_preclose_entry')
    c.raw('48e7efee')      # Preserve caller's D0-D1,D4-D7,A0-A2,A4-A6
    c.raw('4fefffc0')      # LEA -64(SP),SP
    c.move(A(7), A(2))
    S(I(0), 'state')
    S(I(0), 'gfx')
    S(I(0), 'result')

    # No state access before the MC68020 guard; 68000/68010 refusal.
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'screen_preclose_return')
    c.move(A(5), D(0))
    c.tst(D(0)); B(7, 'screen_preclose_return')
    c.imm('and', 1, D(0)); B(6, 'screen_preclose_return')

    c.move(M(5, STATE_PTR_A5), D(0))
    c.tst(D(0)); B(7, 'screen_preclose_registry')
    c.move(D(0), D(1))
    c.imm('and', 1, D(1)); B(6, 'screen_preclose_return')
    S(D(0), 'state')

    # State+8 must be non-overflowing and readable before the dereference.
    c.move(D(0), D(1))
    c.imm('add', GFX_BASE_OFF, D(1))
    B(5, 'screen_preclose_return')
    S(D(1), 'state_end')    # Keep endpoint SEPARATE from GfxBase
    c.move(D(0), A(1))
    c.raw('2c780004')   # MOVEA.L (4).W,A6 = ExecBase
    c.call_os(-534)   # Exec TypeOfMem(State)
    c.tst(D(0)); B(7, 'screen_preclose_return')
    G('state_end', A(1))
    c.raw('2c780004')
    c.call_os(-534)   # Exec TypeOfMem(State+8), not GfxBase itself
    c.tst(D(0)); B(7, 'screen_preclose_return')

    G('state', A(0))
    c.move(M(0, GFX_BASE_OFF), D(0))
    c.tst(D(0)); B(7, 'screen_preclose_registry')
    c.move(D(0), D(1))
    c.imm('and', 1, D(1)); B(6, 'screen_preclose_return')
    S(D(0), 'gfx')

    L('screen_preclose_registry')
    G('gfx', A(4))
    B(1, 'registry_close_entry')
    c.tst(D(3)); B(7, 'screen_preclose_return')
    S(I(1), 'result')

    L('screen_preclose_return')
    G('result', D(3))
    c.raw('4fef0040')    # Restore local frame
    c.raw('4cdf77f7')    # Restore caller registers; preserves D3
    c.raw('74004e75')    # MOVEQ #0,D2; RTS

    code = c.out()
    assert code[:len(prefix)] == prefix
    assert code[old_labels['registry_state']:len(prefix)] == bytes(8)
    assert len(code) < 32766 and len(code)%2 == 0
    assert c.labels['screen_preclose_entry'] == len(prefix)
    return code, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    code, labels = emit_screen_preclose()
    print('M19 P0c PRIVATE screen preclose guard MC68020',
          len(code), sha256(code).hexdigest(),
          'offset',labels['screen_preclose_entry'],
          'NO Screen Close hook or Lib build, NO WinUAE/Compiler test')
