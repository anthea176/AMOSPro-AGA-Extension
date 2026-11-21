#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2d foreground auto-update in a combined, relocatable BOBS/B8 unit."""

from struct import pack_into, unpack_from

from m19_b8_page_manager_emit import R as B8_ROOT
from m19_p0e_object_table_emit import MAX_OBJECTS, SLOT_BYTES
from m19_p0j_swap_barrier_emit import F, G, STATE_A5
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p1e_bank_edit_emit import OBJECT
from m19_p2c_bob_planes_emit import emit_bob_planes
from m68k_emit import A, Code, D, I, M

OWNER, STATE, SCREEN = 0, 4, 8
CALLER_A2 = 24
OBJECT_ACTIVE = 16
assert CALLER_A2 not in F.values()


def emit_bob_auto_update(context_delta):
    bobs, labels = emit_bob_planes(context_delta)
    b8, service = emit_m19_p1a_getters()
    c = Code()
    c.b.extend(bobs)
    c.labels.update(labels)
    B, L = c.branch, c.label

    def begin():
        c.raw('48e7efee4fefffd0')  # Numeric ABI and frame_guard_context frame.
        c.move(A(2), M(7, CALLER_A2))
        c.move(A(7), A(2))

    def owner_matches(label):
        c.move(A(5), D(1))
        c.alu('cmp', M(0, OWNER), 1)
        B(6, label)

    L('p2d_public_auto_update')
    begin()
    c.imm('cmp', 1, D(3))
    B(2, 'p2d_refused')
    c.move(D(3), D(7))
    B(1, 'p1c_context')
    c.move(A(0), D(0))
    B(7, 'p2d_refused')
    B(1, 'frame_guard_context_entry')
    c.tst(D(3))
    B(7, 'p2d_refused')
    c.lea(0, 'frame_guard_state')
    c.tst(M(0, G['status']))
    B(6, 'p2d_refused')
    c.lea(0, 'p2d_mode')
    c.tst(M(0, OWNER))
    B(7, 'p2d_set_mode')
    owner_matches('p2d_refused')
    L('p2d_set_mode')
    c.tst(D(7))
    B(7, 'p2d_disable')
    # Guarantee that a subsequent End resets the mode, even before a Bob SET.
    B(1, 'b8_b7_arm_end_nodraw_entry')
    c.tst(D(3))
    B(7, 'p2d_refused')
    c.lea(0, 'p2d_mode')
    c.move(M(2, F['state']), M(0, STATE))
    c.move(M(2, F['screen']), M(0, SCREEN))
    c.move(A(5), M(0, OWNER))
    B(0, 'p2d_set_done')
    L('p2d_disable')
    c.move(I(0), M(0, OWNER))
    L('p2d_set_done')
    c.word(0x7601)
    B(0, 'p2d_return')

    L('p2d_public_swap')
    begin()
    c.lea(0, 'p2d_mode')
    c.tst(M(0, OWNER))
    B(7, 'p2d_swap')
    owner_matches('p2d_swap')
    B(1, 'frame_guard_context_entry')
    c.tst(D(3))
    B(7, 'p2d_refused')
    c.lea(0, 'p2d_mode')
    for guard_field, mode_offset in (('state', STATE), ('screen', SCREEN)):
        c.move(M(2, F[guard_field]), D(0))
        c.alu('cmp', M(0, mode_offset), 0)
        B(6, 'p2d_refused')
    c.lea(0, 'frame_guard_state')
    c.tst(M(0, G['status']))
    B(6, 'p2d_swap')  # Existing guard handles READY retry and DIRTY refusal.
    c.lea(0, 'p2d_service_root')
    c.tst(M(0, B8_ROOT['owner']))
    B(6, 'p2d_update')  # Existing snapshots may need restoration with all Bobs off.

    # Before the first update, avoid binding the pool until a raw slot is
    # active. The transaction itself revalidates every active bank and image.
    c.move(M(2, F['state']), D(4))
    c.imm('add', OBJECT, D(4))
    B(5, 'p2d_refused')
    c.move(D(4), A(1))
    c.raw('2c780004')
    c.call_os(-534)
    c.tst(D(0))
    B(7, 'p2d_refused')
    c.move(D(4), D(0))
    c.imm('add', MAX_OBJECTS * SLOT_BYTES - 1, D(0))
    B(5, 'p2d_refused')
    c.move(D(0), A(1))
    c.call_os(-534)
    c.tst(D(0))
    B(7, 'p2d_refused')
    c.move(D(4), A(0))
    c.move(I(MAX_OBJECTS), D(0))
    L('p2d_scan')
    c.tst(M(0, OBJECT_ACTIVE))
    B(6, 'p2d_update')
    c.raw('d1fc00000018')  # ADDA.L #24,A0
    assert SLOT_BYTES == 24
    c.quick(1, D(0), sub=True)
    B(6, 'p2d_scan')
    B(0, 'p2d_swap')

    L('p2d_update')
    c.move(M(7, CALLER_A2), A(2))
    B(1, 'p2d_service_update')
    c.tst(D(3))
    B(7, 'p2d_refused')
    L('p2d_swap')
    c.move(M(7, CALLER_A2), A(2))
    B(1, 'guarded_swap_entry')
    B(0, 'p2d_return')
    L('p2d_refused')
    c.word(0x7600)
    L('p2d_return')
    c.raw('4fef00304cdf77f774004e75')

    # All tracked Close/End paths already share this full-register epilogue.
    L('p2d_close')
    c.lea(0, 'p2d_mode')
    c.tst(M(0, OWNER))
    B(7, 'p2d_close_return')
    owner_matches('p2d_close_return')
    c.move(M(5, STATE_A5), D(0))
    B(7, 'p2d_clear_mode')
    c.move(D(0), A(1))
    c.raw('2c780004')
    c.call_os(-534)
    c.tst(D(0))
    B(7, 'p2d_close_return')
    c.move(M(5, STATE_A5), A(1))
    c.tst(M(1))
    B(6, 'p2d_close_return')
    L('p2d_clear_mode')
    c.lea(0, 'p2d_mode')
    c.move(I(0), M(0, OWNER))
    L('p2d_close_return')
    c.raw('4cdf7fff4e75')
    L('p2d_mode')
    c.b.extend(bytes(12))

    service_offset = len(c.b)
    for alias, original in (('p2d_service_update', 'b8_service_update_first_entry'),
                            ('p2d_service_root', 'b8_service_root')):
        c.labels[alias] = service_offset + service[original]
    suffix = bytearray(c.out())
    at = labels['p2b_close_restore']
    assert bobs[at:at+6] == bytes.fromhex('4cdf7fff4e75')
    pack_into('>HhH', suffix, at, 0x6000, c.labels['p2d_close'] - at - 2, 0x4e71)
    return bytes(suffix) + b8, c.labels, service_offset
