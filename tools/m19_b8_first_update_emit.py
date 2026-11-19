#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B8: append-only, no-draw first Update bootstrap for B7/B8.

First valid public Aga Bob SET executes the original setter, then arms the
verified B7 End callback WITHOUT Blitter/Draw. The fifth AP20 unit can then
Bind/Arm/Update atomically on its first public Update. No fixed addresses,
no inter-unit BSR, no implicit Swap and no installed library here.
Existing B7-m2 and B8 native sources are byte-exact prefixes.
"""
from __future__ import annotations

from m68k_emit import Code, A, D, I, M
from m19_b8_b7_hook_emit import emit_b8_b7_hooks, END1, END2
from m19_p0j_end_lifecycle_emit import STATE_A5, OLD_END_DELTA, END_SIGNATURE
from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update
from m19_b8_page_manager_emit import R as B8ROOT

F = dict(result=0, state=4, callbacks=8, old_end=12)
FRAME = 64
B8_FRAME = 96
B8_RESULT = 0
B8_A2 = 52


def emit_b8_b7_first_update() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_b8_b7_hooks()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    # Called exclusively from the same BOBS relocated AP20 unit.
    # No Bob drawing or Gfx library invocation can occur on this path.
    L('b8_b7_arm_end_nodraw_entry')
    c.raw('48e7cfee4fefffc0')  # AMOS numeric preserved regs + 64-byte frame
    c.move(A(7), A(2))
    c.move(I(0), M(2, F['result']))
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(A(5), D(0)); c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.imm('and', 1, D(0)); B(6, 'b8_nodraw_return')
    c.move(A(5), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(M(5, STATE_A5), D(0))
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'b8_nodraw_return')
    c.move(D(0), M(2, F['state']))
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(M(2, F['state']), A(0))
    c.tst(M(0, 0)); B(7, 'b8_nodraw_return')  # actual Screen must exist

    # The original relocated AGA End comes from State-$168, NOT from
    # a fabricated absolute address. Require all immutable code words.
    c.move(M(2, F['state']), D(0))
    c.imm('cmp', OLD_END_DELTA, D(0)); B(5, 'b8_nodraw_return')
    c.imm('sub', OLD_END_DELTA, D(0))
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'b8_nodraw_return')
    c.move(D(0), M(2, F['old_end']))
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(M(2, F['old_end']), D(0))
    c.imm('add', len(END_SIGNATURE)*4-1, D(0))
    B(5, 'b8_nodraw_return')
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'b8_nodraw_return')
    c.move(M(2, F['old_end']), A(4))
    for off, signature in enumerate(END_SIGNATURE):
        c.move(M(4, 4*off), D(0))
        c.imm('cmp', signature, D(0))
        B(6, 'b8_nodraw_return')

    # Reject third-party and half-updated AMOS callbacks. If B8 has
    # already registered its shim, do not disturb that callback.
    c.move(M(5, END1), D(0))
    c.move(M(5, END2), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_nodraw_return')
    c.move(D(0), M(2, F['callbacks']))
    c.move(M(2, F['old_end']), D(1))
    c.alu('cmp', D(1), 0); B(7, 'b8_nodraw_arm')
    c.lea(1, 'program_end_bridge_entry')
    c.move(M(2, F['callbacks']), D(0))
    c.move(A(1), D(1)); c.alu('cmp', D(1), 0)
    B(7, 'b8_nodraw_arm')
    c.lea(1, 'b7_end_entry')
    c.move(M(2, F['callbacks']), D(0))
    c.move(A(1), D(1)); c.alu('cmp', D(1), 0)
    B(7, 'b8_nodraw_arm')
    c.lea(1, 'b8_b7_end_trampoline_entry')
    c.move(M(2, F['callbacks']), D(0))
    c.move(A(1), D(1)); c.alu('cmp', D(1), 0)
    B(6, 'b8_nodraw_return')
    B(0, 'b8_nodraw_success')
    L('b8_nodraw_arm')
    c.lea(0, 'b7_end_entry')
    c.move(A(0), M(5, END1))
    c.move(A(0), M(5, END2))
    L('b8_nodraw_success')
    c.move(I(1), M(2, F['result']))
    L('b8_nodraw_return')
    c.move(M(2, F['result']), D(3))
    c.move(I(0), D(2))
    c.raw('4fef00404cdf77f34e75')

    # Redirect ONLY the existing public Aga Bob SET stub to this wrapper.
    # The original public setter still consumes Y/X/N via A3 as before.
    L('b8_b7_bob_set_bootstrap_entry')
    c.raw('48e7efee4fefffe0')
    c.move(I(0), M(7, 0))
    B(1, 'public_aga_bob_entry')
    c.tst(D(3)); B(7, 'b8_set_return')
    B(1, 'b8_b7_arm_end_nodraw_entry')
    c.move(D(3), M(7, 0))
    L('b8_set_return')
    c.move(M(7, 0), D(3))
    c.move(I(0), D(2))
    c.raw('4fef00204cdf77f774004e75')  # D2=0 AFTER MOVEM restore

    data = c.out()
    assert data.startswith(old)
    assert c.labels['b8_b7_arm_end_nodraw_entry'] == len(old)
    assert len(data) < 32766 and not len(data) & 1
    return data, c.labels


def emit_b8_first_update() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_b8_atomic_registered_update()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    # Single public numerical function 1/0: Bind -> Arm -> atomic Update.
    # Only the initial Bind can allocate two pages. On Arm failure, release
    # those allocations immediately, since no End callback owns them yet.
    L('b8_service_update_first_entry')
    c.raw('48e7cfee4fefffa0')
    c.move(A(7), A(4))
    c.move(I(0), M(4, B8_RESULT))
    c.move(A(2), M(4, B8_A2))
    c.lea(2, 'b8_service_root')
    c.move(M(2, B8ROOT['owner']), D(0))
    c.tst(D(0)); B(7, 'b8_first_bind')
    c.move(A(5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b8_first_return')
    B(0, 'b8_first_registered')

    L('b8_first_bind')
    B(1, 'b8_service_bind_entry')
    c.tst(D(3)); B(7, 'b8_first_return')
    B(1, 'b8_service_arm_b7_entry')
    c.tst(D(3)); B(6, 'b8_first_registered')
    # On a failed registrar, no B8 End callback exists; roll back pool.
    B(1, 'b8_service_close_entry')
    B(0, 'b8_first_return')
    L('b8_first_registered')
    c.move(M(4, B8_A2), A(2))
    B(1, 'b8_service_update_atomic_registered_entry')
    c.move(D(3), M(4, B8_RESULT))
    L('b8_first_return')
    c.move(M(4, B8_RESULT), D(3))
    c.move(I(0), D(2))
    c.raw('4fef00604cdf77f34e75')

    data = c.out()
    assert data.startswith(old)
    assert c.labels['b8_service_update_first_entry'] == len(old)
    assert not len(data) & 1 and len(data) < 32766
    return data, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    b7, lab7 = emit_b8_b7_first_update()
    b8, lab8 = emit_b8_first_update()
    print('M19 B8 FIRST UPDATE NODRAW MC68020 source-only',
          len(b7), sha256(b7).hexdigest(),
          len(b8), sha256(b8).hexdigest(),
          lab7['b8_b7_bob_set_bootstrap_entry'],
          lab8['b8_service_update_first_entry'])
