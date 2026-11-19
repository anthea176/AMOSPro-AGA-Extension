#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8 private Safe/WaitBlit and post-Close/End snapshot lifecycle.

SOURCE ONLY. Appends MC68020 entries after a byte-exact B8 page manager;
no public token, no installed library and NO patch to the B7-m2 engine.

- b8_service_safe_capture_entry / b8_service_safe_restore_entry:
  require an already-owned pool, then consume at most ONE delivered SafePort
  message with Exec/GetMsg (never ReplyMsg/WaitPort), preserve Disp, call
  graphics.library/WaitBlit and reselect the checked non-front BitMap before
  any CPU planar copy. A missing Safe message fails without touching pixels.
- b8_service_postclose_entry:
  the *caller* MUST invoke this only AFTER the original B7-m2 Screen Close
  or AMOS End has returned. It frees snapshots ONLY IF the live native AGA
  state confirms Screen* == NULL, otherwise leaves the pool intact. An
  owner mismatch fails without FreeMem. Idempotent for a closed empty pool.

This is a private bridging primitive, NOT an automatic Close/End hook:
no public stub or End callback is redirected. A follow-up source-backed
trampoline must preserve existing B7-m2 Bob reset, DIRTY and callback chain.
AmigaOS graphics.library WaitBlit LVO -228 and Exec GetMsg -372 are taken
from the existing verified P0d painter and safe notification handler.
Service calls must be serialized in the owning AMOS task; generation/ABA
still requires a later Open/Close hook, not just TypeOfMem.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_page_manager_emit import emit_b8_page_manager, R as ROOT
from m19_b8_back_selector_emit import STATE_OFF

FRAME = 96
F = dict(owner=0, state=4, db=8, gfx=12, port=16, result=20)


def emit_b8_safe_lifecycle() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_b8_page_manager()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    def S(src, key):
        c.move(src, M(4, F[key]))

    def G(key, dst):
        c.move(M(4, F[key]), dst)

    def mapped(key, size):
        # TypeOfMem at both endpoints is best-effort; object lifetime is
        # guaranteed by the calling AGA/AMOS task, not by TypeOfMem.
        G(key, D(0))
        c.tst(D(0)); B(7, 'b8_safe_fail')
        c.imm('and', 1, D(0)); B(6, 'b8_safe_fail')
        G(key, A(1))
        c.raw('2c780004'); c.call_os(-534)
        c.tst(D(0)); B(7, 'b8_safe_fail')
        if size > 1:
            G(key, D(0))
            c.imm('add', size-1, D(0)); B(5, 'b8_safe_fail')
            c.move(D(0), A(1))
            c.raw('2c780004'); c.call_os(-534)
            c.tst(D(0)); B(7, 'b8_safe_fail')

    def prologue(name):
        L(name)
        c.raw('48e7cfee4fefffa0')  # Save AMOS regs and local 96B frame.
        c.move(A(7), A(4))
        S(I(0), 'result')

    # Synchronous SAFE lease: no busy loop, no ReplyMsg, no Swap.
    prologue('b8_service_safe_acquire_entry')
    S(A(5), 'owner')
    c.raw('20780004')
    c.move(A(0), D(0)); c.tst(D(0)); B(7, 'b8_safe_fail')
    c.move(M(0, 0x128), D(0), 'w')
    c.word(0x0800); c.word(1)  # BTST AFF_68020
    B(7, 'b8_safe_fail')
    c.lea(2, 'b8_service_root')
    c.move(M(2, ROOT['owner']), D(0))
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_safe_fail')
    c.tst(D(0)); B(7, 'b8_safe_fail')
    mapped('owner', STATE_OFF + 4)
    c.move(M(5, STATE_OFF), D(0))
    S(D(0), 'state')
    mapped('state', 36)
    G('state', A(0))
    c.move(M(0, 0), D(0)); c.tst(D(0)); B(7, 'b8_safe_fail')
    c.lea(2, 'b8_service_root')
    c.move(M(2, ROOT['screen']), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_safe_fail')
    G('state', A(0))
    c.move(M(0, 8), D(0))
    S(D(0), 'gfx')
    c.tst(D(0)); B(7, 'b8_safe_fail')
    c.imm('and', 1, D(0)); B(6, 'b8_safe_fail')
    G('state', A(0))
    c.move(M(0, 32), D(0))
    S(D(0), 'db')
    mapped('db', 24)
    c.lea(2, 'b8_service_root')
    c.move(M(2, ROOT['db']), D(0))
    G('db', D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_safe_fail')
    G('db', A(0))
    c.move(M(0, 20), D(0))
    c.imm('and', 1, D(0))
    B(7, 'b8_safe_ready')
    G('db', A(0))
    c.move(M(0, 12), D(0))
    S(D(0), 'port')
    mapped('port', 1)
    G('port', A(0))
    c.raw('2c780004'); c.call_os(-372)  # Exec GetMsg once.
    c.tst(D(0)); B(7, 'b8_safe_fail')
    G('db', A(0))
    c.move(M(0, 20), D(0))
    c.imm('and', 0xfffffffe, D(0))  # Keep Disp bit unchanged.
    c.move(D(0), M(0, 20))
    L('b8_safe_ready')
    G('gfx', A(6))
    c.call_os(-228)  # graphics.library WaitBlit before CPU planar copying.
    B(1, 'b8_checked_back_selector_entry')
    c.tst(D(3)); B(7, 'b8_safe_fail')
    S(I(1), 'result')
    L('b8_safe_fail')
    G('result', D(3))
    c.move(I(0), D(2))
    c.raw('4fef00604cdf77f34e75')

    # Route through exactly the same validated B8 capture/restore entries.
    for name, target in (
            ('b8_service_safe_capture_entry', 'b8_service_capture_entry'),
            ('b8_service_safe_restore_entry', 'b8_service_restore_entry')):
        prologue(name)
        B(1, 'b8_service_safe_acquire_entry')
        c.tst(D(3)); B(7, 'b8_safe_wrapper_return')
        B(1, target)
        S(D(3), 'result')
        # Each wrapper has its own return to avoid cross-entry fallthrough.
        local_return = name + '_return'
        B(0, local_return)
        L(local_return)
        G('result', D(3))
        c.move(I(0), D(2))
        c.raw('4fef00604cdf77f34e75')
    # Both wrappers branch directly here on failure. Their result frame
    # is initialized at the same offsets; this common epilogue is safe.
    L('b8_safe_wrapper_return')
    G('result', D(3))
    c.move(I(0), D(2))
    c.raw('4fef00604cdf77f34e75')

    # POST-Close/End only: original B7 code must already have returned.
    prologue('b8_service_postclose_entry')
    S(A(5), 'owner')
    c.lea(2, 'b8_service_root')
    c.tst(M(2, ROOT['owner']))
    B(7, 'b8_postclose_ok')  # No allocations: idempotent.
    c.move(M(2, ROOT['owner']), D(0))
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_postclose_return')
    mapped('owner', STATE_OFF + 4)  # mapped failure returns zero safely.
    c.move(M(5, STATE_OFF), D(0))
    S(D(0), 'state')
    mapped('state', 36)
    G('state', A(0))
    c.tst(M(0, 0)); B(6, 'b8_postclose_return')  # Still open: never free.
    B(1, 'b8_service_close_entry')
    c.tst(D(3)); B(7, 'b8_postclose_return')
    L('b8_postclose_ok')
    S(I(1), 'result')
    L('b8_postclose_return')
    G('result', D(3))
    c.move(I(0), D(2))
    c.raw('4fef00604cdf77f34e75')

    data = c.out()
    assert data.startswith(old) and len(data) < 32766 and not len(data) & 1
    assert labels['b8_service_root'] < labels['b8_service_safe_acquire_entry']
    return data, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    raw, labels = emit_b8_safe_lifecycle()
    print('M19 B8 MC68020 PRIVATE SAFE/LIFECYCLE SOURCE ONLY',
          len(raw), sha256(raw).hexdigest(),
          labels['b8_service_safe_acquire_entry'])
