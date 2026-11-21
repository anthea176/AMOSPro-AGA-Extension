#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Screen-owned rectangles for the P1c renderer and its checked Blitter."""
from struct import pack, unpack_from

from m19_p0d_private_blit_emit import F as PAINTER
from m19_p0j_explicit_safe_draw_emit import F as DRAW
from m19_p1c_bob_priority_emit import emit_priority_bobs
from m68k_emit import A, D, I, M, POST, PRE, Code

SLOT_BYTES = 16
SLOTS = 65
TABLE_BYTES = SLOTS * SLOT_BYTES
TABLE_FROM_CONTEXT = 8  # Immediately after the existing P1c owner/mode.


def emit_limit_open(previous_open, table_offset):
    """Append the zeroed rectangle table and the successful-Open reset."""
    c = Code()
    c.label('limit_table')
    c.b.extend(bytes(TABLE_BYTES))
    c.label('limit_open')
    c.raw('4ebb0170')  # MC68020 JSR (d32,PC), preserving AMOS Open arguments.
    c.b.extend(pack('>i', previous_open - (table_offset + TABLE_BYTES + 2)))
    c.imm('cmp', 1, D(3))
    c.branch(6, 'limit_open_return')
    c.move(D(0), PRE(7))
    c.move(A(0), PRE(7))
    c.lea(0, 'limit_table')
    c.move(I(TABLE_BYTES // 4), D(0))
    c.label('limit_open_clear')
    c.move(I(0), POST(0))
    c.quick(1, D(0), sub=True)
    c.branch(6, 'limit_open_clear')
    c.move(POST(7), A(0))
    c.move(POST(7), D(0))
    c.label('limit_open_return')
    c.raw('4e75')
    return c.out()


def emit_limit_bobs(context_delta):
    baseline, labels = emit_priority_bobs(context_delta)
    c = Code()
    c.b.extend(baseline)
    c.labels.update(labels)
    B, L = c.branch, c.label

    L('p1d_limit_entry')
    c.raw('48e7efee')
    # H arrives in D3, followed on A3 by W, Y, X and N, as in AMOS GetP.
    c.move(D(3), D(7))
    for reg in (6, 5, 4):
        c.move(POST(3), D(reg))
    c.move(POST(3), D(3))
    c.imm('cmp', SLOTS - 1, D(3))
    B(2, 'p1d_refuse')
    B(1, 'p1c_context')
    c.move(A(0), D(0))
    B(7, 'p1d_refuse')
    c.word(0xd1fc); c.b.extend(pack('>I', TABLE_FROM_CONTEXT))  # ADDA.L #8,A0
    c.shift(3, 4, left=True)
    c.raw('d1c3')  # ADDA.L D3,A0 => slot
    c.tst(D(6))
    B(15, 'p1d_reset_request')
    c.tst(D(7))
    B(15, 'p1d_refuse')
    c.alu('add', D(4), 6)
    B(9, 'p1d_refuse')  # BVS: signed right bound overflow.
    c.alu('add', D(5), 7)
    B(9, 'p1d_refuse')
    B(0, 'p1d_commit')
    L('p1d_reset_request')
    for reg in (4, 5, 6, 7):
        c.tst(D(reg))
        B(6, 'p1d_refuse')
    L('p1d_commit')
    for reg in (4, 5, 6, 7):
        c.move(D(reg), POST(0))
    c.move(I(1), D(3))
    B(0, 'p1d_set_return')
    L('p1d_refuse')
    c.move(I(0), D(3))
    L('p1d_set_return')
    c.raw('4cdf77f774004e75')

    # Only the two actual frame loops supply a Bob ID. A synchronous paint
    # finishes before the caller can run another AMOS command or change it.
    L('p1d_scoped_paint')
    c.move(A(0), PRE(7))
    c.lea(0, 'p1d_drawing_id')
    c.move(M(2, DRAW['ident']), M(0))
    c.move(POST(7), A(0))
    B(1, 'explicit_safe_blit_entry')
    c.move(A(0), PRE(7))
    c.lea(0, 'p1d_drawing_id')
    c.move(I(0), M(0))
    c.move(POST(7), A(0))
    c.raw('4e75')
    L('p1d_drawing_id')
    c.raw('00000000')

    L('p1d_clip_painter')
    c.lea(0, 'p1d_drawing_id')
    c.tst(M(0))
    B(7, 'p1d_continue')
    B(1, 'p1c_context')
    c.move(A(0), D(0))
    B(7, 'p1d_continue')
    c.word(0xd1fc); c.b.extend(pack('>I', TABLE_FROM_CONTEXT))
    c.move(A(0), A(1))  # Global rectangle and local rectangle.
    c.lea(0, 'p1d_drawing_id')
    c.move(M(0), D(0))
    c.shift(0, 4, left=True)
    c.move(A(1), A(0))
    c.raw('d1c0')  # ADDA.L D0,A0
    c.move(A(0), PRE(7))
    c.move(A(1), A(0))
    B(1, 'p1d_intersect')
    c.move(POST(7), A(0))
    c.tst(D(0))
    B(7, 'private_blit_clipped_ok')
    B(1, 'p1d_intersect')
    c.tst(D(0))
    B(7, 'private_blit_clipped_ok')
    L('p1d_continue')
    c.move(M(4, PAINTER['stride']), D(0))  # Instruction replaced by BRA.W.
    B(0, 'p1d_resume_bitmap')

    L('p1d_intersect')
    # Empty stored slot means no configured rectangle. A configured zone
    # can itself yield an empty intersection with the current draw.
    c.move(M(0), D(0))
    c.alu('cmp', M(0, 8), 0)
    B(7, 'p1d_visible')
    for axis, start, end in (('x', 0, 8), ('y', 4, 12)):
        dst = M(4, PAINTER['d' + axis])
        src = M(4, PAINTER['s' + axis])
        extent = M(4, PAINTER['c' + ('w' if axis == 'x' else 'h')])
        c.move(dst, D(0))
        c.move(D(0), D(1))
        c.alu('add', extent, 1)  # Original exclusive end (screen-bounded).
        c.alu('cmp', M(0, start), 0)
        B(12, 'p1d_start_' + axis)
        c.move(M(0, start), D(0))
        L('p1d_start_' + axis)
        c.alu('cmp', M(0, end), 1)
        B(15, 'p1d_end_' + axis)
        c.move(M(0, end), D(1))
        L('p1d_end_' + axis)
        c.alu('cmp', D(0), 1)
        B(15, 'p1d_invisible')  # Compare before subtract to avoid overflow.
        c.alu('sub', D(0), 1)
        c.move(D(1), extent)
        c.move(D(0), D(1))
        c.alu('sub', dst, 1)
        c.alu('add', src, 1)
        c.move(D(1), src)
        c.move(D(0), dst)
    L('p1d_visible')
    c.move(I(1), D(0))
    c.raw('4e75')
    L('p1d_invisible')
    c.move(I(0), D(0))
    c.raw('4e75')

    def redirect(site, opcode, dest):
        offset = c.labels[site]
        c.b[offset:offset + 4] = pack('>Hh', opcode, c.labels[dest] - offset - 2)

    for site in ('p1b_frame_paint_call', 'explicit_frame_paint_call'):
        at = labels[site]
        assert unpack_from('>Hh', baseline, at) == (
            0x6100, labels['explicit_safe_blit_entry'] - at - 2)
        redirect(site, 0x6100, 'p1d_scoped_paint')

    at = labels['private_blit_build_bitmap']
    original = Code()
    original.move(M(4, PAINTER['stride']), D(0))
    assert bytes(original.b) == baseline[at:at + 4]
    c.labels['p1d_resume_bitmap'] = at + 4
    redirect('private_blit_build_bitmap', 0x6000, 'p1d_clip_painter')
    return c.out(), c.labels
