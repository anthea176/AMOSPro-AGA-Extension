#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b5 PRIVATE fail-closed BOBS frame presentation guard.

Source-only candidate, no public Aga Bob Draw. The existing Aga Swap
token may be rebound IN MEMORY to guarded_swap_entry; this wrapper calls
the EXACT original AGA native Swap, derived from live A5+0x1c8 State.

A protected draw arms DIRTY conservatively BEFORE calling P0j-b4.
Success changes DIRTY to READY; any failure remains DIRTY and blocks both
further draws and public Swap, even if no DMA was attempted. Only an
actual successful AGA Screen Close clears this latch. A successful Swap
after READY clears state, and a refused legacy Swap leaves READY intact.

This is intentionally fail-closed, not a background reconstruction API.
There is no implicit Swap, no BOBS bank_active_state projection, no new
public token, and no claim of WinUAE or real AMOS Compiler validation.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw

STATE_A5 = 0x1c8
AGA_STATE_OFFSET = 0x1c2
AGA_SWAP_OFFSET = 0x0ba2
SWAP_STATE_DELTA = AGA_SWAP_OFFSET - AGA_STATE_OFFSET
SWAP_SIGNATURE = (0x48e7effe, 0x7600, 0x246d01c8)
assert SWAP_STATE_DELTA == 0x9e0

FRAME = 48
F = dict(state=0, db=4, front=8, screen=12, target=16, result=20)
G = dict(status=0, owner=4, state=8, db=12, front=16, screen=20)
GUARD_BYTES = 24
DIRTY, READY = 1, 2


def emit_swap_barrier() -> tuple[bytes, dict[str, int]]:
    previous, labels = emit_explicit_bob_draw()
    c = Code()
    c.raw(previous.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    def fs(src, key):
        c.move(src, M(2, F[key]))

    def fg(key, dst):
        c.move(M(2, F[key]), dst)

    def state_addr():
        c.lea(0, 'frame_guard_state')

    def match_guard(reject):
        """A0 points at guard; A2 contains checked live context."""
        for key, reg in (('owner', A(5)), ('state', M(2, F['state'])),
                         ('db', M(2, F['db'])), ('front', M(2, F['front'])),
                         ('screen', M(2, F['screen']))):
            c.move(M(0, G[key]), D(0))
            c.move(reg, D(1))
            c.alu('cmp', D(1), 0)
            B(6, reject)

    def mapped(ptr, reject):
        c.move(ptr, A(1))
        c.raw('2c780004')  # MOVEA.L (4).W,A6 = ExecBase
        c.call_os(-534)    # TypeOfMem; no access before this check
        c.tst(D(0))
        B(7, reject)

    # Internal checked shared context: A2 points to each wrapper's frame.
    L('frame_guard_context_entry')
    c.move(I(0), D(3))
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'guard_context_return')
    c.move(A(5), D(0)); c.tst(D(0)); B(7, 'guard_context_return')
    c.imm('and', 1, D(0)); B(6, 'guard_context_return')
    c.move(M(5, STATE_A5), D(0))
    c.tst(D(0)); B(7, 'guard_context_return')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'guard_context_return')
    fs(D(0), 'state')
    mapped(A(5), 'guard_context_return')  # owner must be mapped, too
    fg('state', A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'guard_context_return')
    fg('state', A(0))
    c.move(M(0, 0), D(0)); c.tst(D(0)); B(7, 'guard_context_return')
    fs(D(0), 'screen')
    c.move(M(0, 32), D(0))
    c.tst(D(0)); B(7, 'guard_context_return')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'guard_context_return')
    fs(D(0), 'db')
    fg('db', A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'guard_context_return')
    fg('db', A(0))
    c.move(M(0, 8), D(0))
    c.imm('cmp', 1, D(0)); B(2, 'guard_context_return')
    fs(D(0), 'front')
    c.move(I(1), D(3))
    L('guard_context_return')
    c.raw('4e75')

    # Native private all-object draw; sets a persistent dirty latch BEFORE
    # any possible pixel DMA. No "success" after a previous failed frame.
    L('guarded_frame_draw_entry')
    c.raw('48e7efee4fefffd0')
    c.move(A(7), A(2))
    B(1, 'frame_guard_context_entry')
    c.tst(D(3)); B(7, 'guard_draw_return')
    state_addr()
    c.move(M(0, G['status']), D(0))
    c.tst(D(0)); B(7, 'guard_draw_arm')
    c.imm('cmp', READY, D(0)); B(6, 'guard_draw_reject')
    match_guard('guard_draw_reject')
    L('guard_draw_arm')
    state_addr()
    c.move(I(DIRTY), M(0, G['status']))
    c.move(A(5), M(0, G['owner']))
    for key in ('state', 'db', 'front', 'screen'):
        fg(key, D(0))
        c.move(D(0), M(0, G[key]))
    B(1, 'explicit_frame_draw_entry')
    c.tst(D(3)); B(7, 'guard_draw_return')
    state_addr()
    c.move(I(READY), M(0, G['status']))
    B(0, 'guard_draw_return')
    L('guard_draw_reject')
    c.move(I(0), D(3))
    L('guard_draw_return')
    c.raw('4fef00304cdf77f774004e75')  # frame, AMOS ABI, D2=0, RTS

    # Public Aga Swap function shim in the source-only candidate. Original
    # Swap has no Bob-dependent flag and cannot be called while DIRTY.
    L('guarded_swap_entry')
    c.raw('48e7efee4fefffd0')
    c.move(A(7), A(2))
    B(1, 'frame_guard_context_entry')
    c.tst(D(3)); B(7, 'guard_swap_return')
    state_addr()
    c.move(M(0, G['status']), D(0))
    c.imm('cmp', DIRTY, D(0)); B(7, 'guard_swap_refuse')
    c.tst(D(0)); B(7, 'guard_swap_target')
    c.imm('cmp', READY, D(0)); B(6, 'guard_swap_refuse')
    match_guard('guard_swap_refuse')
    L('guard_swap_target')
    fg('state', D(0))
    c.imm('add', SWAP_STATE_DELTA, D(0))
    B(5, 'guard_swap_refuse')  # overflow
    c.imm('and', 1, D(0)); B(6, 'guard_swap_refuse')
    fg('state', D(0))
    c.imm('add', SWAP_STATE_DELTA, D(0))
    c.move(D(0), A(4))
    fs(D(0), 'target')
    mapped(A(4), 'guard_swap_refuse')
    fg('target', D(0))
    c.imm('add', 9, D(0)); B(5, 'guard_swap_refuse')
    mapped(D(0), 'guard_swap_refuse')
    fg('target', A(4))
    c.move(M(4, 0), D(0)); c.imm('cmp', SWAP_SIGNATURE[0], D(0))
    B(6, 'guard_swap_refuse')
    c.move(M(4, 4), D(0), 'w'); c.imm('cmp', SWAP_SIGNATURE[1], D(0), 'w')
    B(6, 'guard_swap_refuse')
    c.move(M(4, 6), D(0)); c.imm('cmp', SWAP_SIGNATURE[2], D(0))
    B(6, 'guard_swap_refuse')
    c.raw('4e94')  # JSR (A4) -> checked, ORIGINAL relocated AGA Swap
    fs(D(3), 'result')
    c.tst(D(3)); B(7, 'guard_swap_restore')
    state_addr()
    c.move(I(0), M(0, G['status']))  # only a successful swap commits
    B(0, 'guard_swap_restore')
    L('guard_swap_refuse')
    fs(I(0), 'result')
    L('guard_swap_restore')
    fg('result', D(3))
    L('guard_swap_return')
    c.raw('4fef00304cdf77f774004e75')

    # Screen Close is an AMOS INSTRUCTION: preserve D2/D3. Only clear
    # the dirty latch if the original checked Close actually closed Screen.
    L('guarded_close_entry')
    c.raw('48e7fffe')  # save D0-D7/A0-A6, including caller's D2/D3
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'guard_close_return')
    c.move(A(5), D(0)); c.tst(D(0)); B(7, 'guard_close_return')
    c.imm('and', 1, D(0)); B(6, 'guard_close_return')
    B(1, 'screen_close_bridge_entry')
    c.move(M(5, STATE_A5), D(0))
    c.tst(D(0)); B(7, 'guard_close_return')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'guard_close_return')
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'guard_close_return')
    c.move(M(5, STATE_A5), A(1))
    c.tst(M(1, 0)); B(6, 'guard_close_return')  # still open
    state_addr()
    c.move(M(0, G['owner']), D(0))
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'guard_close_return')
    for off in range(0, GUARD_BYTES, 4):
        c.move(I(0), M(0, off))
    L('guard_close_return')
    c.raw('4cdf7fff4e75')   # preserve instruction ABI, RTS

    L('frame_guard_state')
    c.raw('00' * GUARD_BYTES)
    native = c.out()
    assert native.startswith(previous)
    assert c.labels['frame_guard_context_entry'] == len(previous)
    assert c.labels['guarded_swap_entry'] < c.labels['guarded_close_entry']
    assert c.labels['guarded_close_entry'] < c.labels['frame_guard_state']
    assert len(native) % 2 == 0 and len(native) < 32766
    return native, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    source, labels = emit_swap_barrier()
    print('M19 P0j-b5 guarded Swap, native source-only',
          len(source), sha256(source).hexdigest(),
          'guard_draw', labels['guarded_frame_draw_entry'],
          'guard_swap', labels['guarded_swap_entry'],
          'guard_close', labels['guarded_close_entry'],
          'NO installed Lib or public Draw')
