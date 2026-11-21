#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Select destination planes in the private Bob RastPort for P2c."""

from struct import pack_into

from m68k_emit import A, D, I, M, POST, Code
from m19_p2b_bob_flip_emit import MODE, SIZE, SLOT_BYTES, RESTORE, SAVES, emit_bob_flip

# Use an unused long in the owner-scoped P2b slot. Zero encodes the
# default mask $ff, so a fresh slot needs no separate initialization.
PLANE_SELECTION = SIZE + 4
RP_MASK = 24  # graphics/rastport.h, classic 32-bit layout
assert PLANE_SELECTION + 4 <= SLOT_BYTES


def emit_bob_planes(context_delta):
    old, labels = emit_bob_flip(context_delta)
    c = Code()
    c.b.extend(old)
    c.labels.update(labels)
    B, L = c.branch, c.label

    # AGA GetP ABI: D3 mask, A3 -> one long (Bob number).
    L('p2c_public_planes')
    c.raw(SAVES + '4fefffd8')  # 40-byte private frame
    c.move(A(7), A(2))
    c.move(D(3), M(2, 0))
    c.move(POST(3), M(2, 4))
    c.move(A(3), M(2, 8))
    c.imm('cmp', 255, D(3)); B(2, 'p2c_set_fail')
    B(1, 'p1c_context')
    c.move(A(0), D(0)); B(7, 'p2c_set_fail')
    c.lea(0, 'p2b_owner')
    c.move(M(0), D(0)); B(7, 'p2c_set_check')
    c.move(A(5), D(1)); c.alu('cmp', D(1), 0); B(6, 'p2c_set_fail')
    L('p2c_set_check')
    c.raw('43ea0010')  # LEA 16(A2),A1 (24-byte checked Bob)
    c.move(M(2, 4), D(0))
    B(1, 'relay_checked_read_entry')
    c.tst(D(3)); B(7, 'p2c_set_fail')
    c.lea(0, 'p2b_owner')
    c.move(A(5), M(0))
    c.move(M(2, 4), D(0))
    B(1, 'p2b_slot')
    c.move(M(2, 0), D(3))
    c.raw('0a0300ff')  # EORI.B #$ff,D3
    c.move(D(3), M(0, PLANE_SELECTION))
    c.word(0x7601)
    B(0, 'p2c_set_return')
    L('p2c_set_fail')
    c.word(0x7600)
    L('p2c_set_return')
    c.move(M(2, 8), D(2))
    c.raw('4fef0028' + RESTORE)
    c.move(D(2), A(3))
    c.raw('74004e75')

    # Preserve the original InitRastPort call, then apply the scoped Bob's
    # mask on that same private RP before either graphics.library blit.
    L('p2c_apply_planes')
    c.raw('43ec0040')  # Original LEA 64(A4),A1.
    c.lea(0, 'p2b_owner')
    c.move(A(5), D(0)); c.alu('cmp', M(0), 0); B(6, 'p2c_apply_done')
    c.lea(0, 'p1d_drawing_id')
    c.move(M(0), D(0)); B(7, 'p2c_apply_done')
    c.imm('cmp', 64, D(0)); B(2, 'p2c_apply_done')
    B(1, 'p2b_slot')
    c.move(M(0, PLANE_SELECTION), D(3)); B(7, 'p2c_apply_done')
    c.raw('0a0300ff')
    c.move(D(3), M(1, RP_MASK), 'b')
    L('p2c_apply_done')
    c.word(0x4e75)

    # Only the all-slot purge performed after confirmed Close/End resets
    # render configuration. Per-bank eviction preserves slot settings.
    L('p2c_reset_slot')
    c.move(I(0), M(3, MODE))
    c.move(I(0), M(3, PLANE_SELECTION))
    c.word(0x4e75)
    result = bytearray(c.out())
    init_and_lea = bytes.fromhex('4eaeff3a43ec0040')
    paint = old.index(init_and_lea, labels['private_bob_blit_entry'])
    assert old.count(init_and_lea, labels['private_bob_blit_entry']) == 1
    patch = paint + 4
    pack_into('>Hh', result, patch, 0x6100, c.labels['p2c_apply_planes']-(patch+2))
    patch = labels['p2b_clear_mode']
    assert old[patch:patch+6] == bytes.fromhex('26bc00000000')
    pack_into('>HhH', result, patch, 0x6100, c.labels['p2c_reset_slot']-(patch+2), 0x4e71)
    return bytes(result), c.labels
