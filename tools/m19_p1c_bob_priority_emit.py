#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1c screen-local priority and stable frame order for the P1b renderer."""
from struct import pack

from m68k_emit import A, Code, D, I, M, POST, PRE
from m19_p0j_explicit_safe_draw_emit import F, FRAME, MAX_BOBS, RECORD, emit_frame_draw
from m19_p1b_hotspot_draw_emit import emit_p1b_hotspot_draw

STATE_A5 = 0x1c8
OPEN_OK = 1
OWNER = 0
MODE = 4
LIST = FRAME
CURSOR = 32
COUNT = 36
SORT_MODE = 40
SCAN_ID = 44
FRAME_BYTES = FRAME + MAX_BOBS * 4


def emit_priority_open(original_offset, suffix_offset):
    """Return a wrapper and two zeroed longs appended to the AGA core unit."""
    c = Code()
    # MC68020 full-extension PC-relative JSR. Preserve every incoming
    # register and leave AMOS parameter consumption to the original Open.
    c.raw('4ebb0170')
    c.b.extend(pack('>i', original_offset - suffix_offset - 2))
    c.imm('cmp', OPEN_OK, D(3))
    c.branch(6, 'priority_open_return')
    c.move(A(0), PRE(7))
    c.lea(0, 'priority_context')
    c.move(A(5), M(0, OWNER))
    c.move(I(0), M(0, MODE))
    c.move(POST(7), A(0))
    c.label('priority_open_return')
    c.raw('4e75')
    c.label('priority_context')
    c.raw('0000000000000000')
    context = suffix_offset + c.labels['priority_context']
    return c.out(), context


class PriorityTraversal:
    """Build an ordered list of packed (signed Y, ID) keys on the stack."""

    def begin(self, c):
        B, L = c.branch, c.label
        c.move(I(1), M(2, SCAN_ID))
        c.move(I(0), M(2, COUNT))
        B(1, 'p1c_read_mode')
        c.move(D(0), M(2, SORT_MODE))
        L('p1c_collect')
        c.move(M(2, SCAN_ID), D(0))
        c.imm('cmp', MAX_BOBS, D(0))
        B(2, 'p1c_collect_done')
        c.move(A(2), D(1))
        c.imm('add', RECORD, D(1))
        c.move(D(1), A(1))
        B(1, 'relay_read_entry')
        c.tst(D(3))
        B(7, 'p1c_collect_next')
        c.move(M(2, SCAN_ID), D(7))
        c.imm('cmp', 2, M(2, SORT_MODE))
        B(7, 'p1c_insert')
        c.move(M(2, RECORD + 12), D(0))
        c.imm('add', 32768, D(0))
        c.shift(0, 7, left=True)
        c.alu('or', D(0), 7)
        L('p1c_insert')
        c.move(M(2, COUNT), D(0))
        c.shift(0, 2, left=True)
        c.move(A(2), A(0))
        c.word(0xd1fc); c.raw(f'{LIST:08x}')  # ADDA.L #LIST,A0
        c.move(A(0), A(1))
        c.raw('d1c0')  # ADDA.L D0,A0
        # A0 points at the vacant slot and A1 at the lower bound of the list.
        L('p1c_insert_scan')
        c.raw('b1c9')  # CMPA.L A1,A0
        B(7, 'p1c_store_key')
        c.move(M(0, -4), D(0))
        c.alu('cmp', D(7), 0)
        B(3, 'p1c_store_key')  # previous key <= inserted key
        c.move(D(0), M(0))
        c.quick(4, A(0), sub=True)
        B(0, 'p1c_insert_scan')
        L('p1c_store_key')
        c.move(D(7), M(0))
        c.quick(1, M(2, COUNT))
        L('p1c_collect_next')
        c.quick(1, M(2, SCAN_ID))
        B(0, 'p1c_collect')
        L('p1c_collect_done')
        c.move(I(0), M(2, CURSOR))

    def next(self, c):
        B, L = c.branch, c.label
        c.move(M(2, CURSOR), D(0))
        c.alu('cmp', M(2, COUNT), 0)
        B(4, 'explicit_frame_done')
        c.quick(1, M(2, CURSOR))
        c.imm('cmp', 1, M(2, SORT_MODE))
        B(7, 'p1c_cursor_ready')
        c.move(M(2, COUNT), D(1))
        c.quick(1, D(1), sub=True)
        c.alu('sub', D(0), 1)
        c.move(D(1), D(0))
        L('p1c_cursor_ready')
        c.shift(0, 2, left=True)
        c.move(A(2), A(0))
        c.raw('d1c0')  # ADDA.L D0,A0
        c.move(M(0, LIST), D(0))
        c.imm('and', 127, D(0))
        c.move(D(0), M(2, F['ident']))


def emit_priority_bobs(context_delta):
    original, labels = emit_p1b_hotspot_draw()
    c = Code()
    c.b.extend(original)
    # Reuse the original source generator for the checked drawing loop.
    for name, offset in labels.items():
        c.labels[name.replace('explicit_frame_', 'p1b_frame_', 1)
                 if name.startswith('explicit_frame_') else name] = offset

    entry = labels['explicit_frame_draw_entry']
    prologue = bytes.fromhex('48e7efee4fefff60')
    if original[entry:entry + len(prologue)] != prologue:
        raise ValueError('P1b frame prologue changed')

    B, L = c.branch, c.label
    c.labels['p1b_frame_body'] = entry + len(prologue)
    L('p1c_frame_dispatch')
    c.raw('48e7efee')
    B(1, 'p1c_read_mode')
    c.tst(D(0))
    B(7, 'p1c_frame_default')
    c.raw('4cdf77f7')
    B(0, 'explicit_frame_draw_entry')
    L('p1c_frame_default')
    c.raw('4cdf77f7')
    c.b.extend(prologue)
    B(0, 'p1b_frame_body')

    # Mode/owner live next to AGA State in the core AP20 island.
    # The BOBS island uses the runtime State address, never a static
    # cross-island PC-relative displacement.
    L('p1c_context')
    B(1, 'registry_cpu_guard')
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.move(A(5), D(0))
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.imm('and', 1, D(0))
    B(6, 'p1c_no_context')
    c.move(A(5), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.move(M(5, STATE_A5), D(0))
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.move(D(0), D(1))
    c.imm('and', 1, D(1))
    B(6, 'p1c_no_context')
    c.move(D(0), A(1))
    c.call_os(-534)
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.move(M(5, STATE_A5), A(0))
    c.tst(M(0))
    B(7, 'p1c_no_context')
    c.move(A(0), D(0))
    c.imm('add', context_delta + 7, D(0))
    B(5, 'p1c_no_context')
    c.move(D(0), A(1))
    c.call_os(-534)
    c.tst(D(0))
    B(7, 'p1c_no_context')
    c.move(M(5, STATE_A5), A(0))
    c.word(0xd1fc); c.raw(f'{context_delta:08x}')  # ADDA.L #delta,A0
    c.move(A(5), D(0))
    c.alu('cmp', M(0, OWNER), 0)
    B(6, 'p1c_no_context')
    c.raw('4e75')
    L('p1c_no_context')
    c.move(I(0), A(0))
    c.raw('4e75')

    L('p1c_read_mode')
    B(1, 'p1c_context')
    c.move(A(0), D(0))
    B(7, 'p1c_read_return')
    c.move(M(0, MODE), D(0))
    L('p1c_read_return')
    c.raw('4e75')

    L('p1c_priority_entry')
    c.raw('48e7efee')
    c.imm('cmp', 3, D(3))
    B(2, 'p1c_priority_fail')  # unsigned range excludes negatives
    c.move(D(3), D(7))
    B(1, 'p1c_context')
    c.move(A(0), D(0))
    B(7, 'p1c_priority_fail')
    c.move(D(7), M(0, MODE))
    c.move(I(1), D(3))
    B(0, 'p1c_priority_return')
    L('p1c_priority_fail')
    c.move(I(0), D(3))
    L('p1c_priority_return')
    c.raw('4cdf77f774004e75')

    emit_frame_draw(c, traversal=PriorityTraversal(), frame_bytes=FRAME_BYTES)
    displacement = c.labels['p1c_frame_dispatch'] - entry - 2
    c.b[entry:entry + len(prologue)] = pack('>HhHH', 0x6000, displacement, 0x4e71, 0x4e71)
    return c.out(), c.labels
