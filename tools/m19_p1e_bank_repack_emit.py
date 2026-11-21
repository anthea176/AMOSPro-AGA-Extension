#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Private P1e payload sizing and repacking for fully validated AGBO v1.

A0 points to a trusted descriptor of nine longs: original, original_size,
destination, capacity, first_or_id, last (zero for insert), width, height,
depth. The caller validates the entire original AGBO and both memory spans.
A null destination requests sizing only. No AMOS bank, cache, stamp, or
caller-owned source bytes are modified. Return D3=exact size or zero, D2=0.
"""
from m68k_emit import A, Code, D, I, M, POST
from m19_p0a_multi_bob_abk import ENTRY, HEADER, MAX_BANK_BYTES, MAX_IMAGE_ID, MAX_PIXELS, MAX_SIDE

ARGUMENTS = ('source', 'size', 'dest', 'capacity', 'first', 'last', 'width', 'height', 'depth')
F = {name: i * 4 for i, name in enumerate(ARGUMENTS + (
    'count', 'entries', 'data_size', 'plane', 'stride', 'blank_size',
    'total', 'generation', 'emit_blank', 'data_offset', 'result',
))}
FRAME = 96
assert max(F.values()) + 4 <= FRAME


def emit_bank_repack():
    c = Code()
    B, L = c.branch, c.label

    def get(name, reg):
        c.move(M(2, F[name]), reg)

    def save(reg, name):
        c.move(reg, M(2, F[name]))

    def check_range(name, high, low=1):
        get(name, D(0))
        c.imm('cmp', low, D(0)); B(5, 'repack_return')
        c.imm('cmp', high, D(0)); B(2, 'repack_return')

    def advance(reg, amount):
        c.word(0xd1fc | reg << 9)  # ADDA.L #amount,An
        c.word(0)
        c.word(amount)

    def read_id(reg):
        c.move(I(0), D(0))
        c.move(M(reg), D(0), 'w')

    L('bank_repack')
    c.raw('48e7efee')
    c.word(0x4fef); c.word(-FRAME)
    c.move(A(7), A(2))
    for i, name in enumerate(ARGUMENTS):
        save(M(0, 4 * i), name)
    save(I(0), 'result')
    get('source', A(0))
    c.move(M(0, 24), D(0))
    c.imm('cmp', -1, D(0)); B(7, 'repack_return')
    c.quick(1, D(0))
    save(D(0), 'generation')
    c.move(I(0), D(0))
    c.move(M(0, 8), D(0), 'w')
    save(D(0), 'count')
    save(I(0), 'entries'); save(I(0), 'data_size')
    check_range('first', MAX_IMAGE_ID)
    get('last', D(0))
    B(7, 'repack_insertion')
    c.alu('cmp', M(2, F['first']), 0); B(5, 'repack_return')
    c.imm('cmp', MAX_IMAGE_ID, D(0)); B(2, 'repack_return')
    save(I(0), 'emit_blank')
    B(0, 'repack_scan_init')

    L('repack_insertion')
    check_range('width', MAX_SIDE)
    check_range('height', MAX_SIDE)
    check_range('depth', 8)
    get('width', D(0)); get('height', D(1))
    c.raw('c0c1')  # MULU.W D1,D0 -> 32-bit pixel count.
    c.imm('cmp', MAX_PIXELS, D(0)); B(2, 'repack_return')
    get('width', D(0))
    c.imm('add', 15, D(0)); c.shift(0, 4); c.shift(0, 1, left=True)
    save(D(0), 'stride')
    c.raw('c0c1')  # stride * height.
    save(D(0), 'plane')
    get('depth', D(1)); c.quick(1, D(1))
    # One plane can exceed 16 bits. Sum at most nine 32-bit planes.
    c.move(I(0), D(4))
    L('repack_planes')
    c.alu('add', D(0), 4)
    c.quick(1, D(1), sub=True); B(6, 'repack_planes')
    save(D(4), 'blank_size')
    save(D(4), 'data_size')
    save(I(1), 'entries'); save(I(1), 'emit_blank')

    L('repack_scan_init')
    get('source', A(4)); advance(4, HEADER.size)
    get('count', D(7))
    L('repack_scan')
    c.tst(D(7)); B(7, 'repack_sized')
    read_id(4)
    c.tst(M(2, F['last'])); B(7, 'repack_insert_scan')
    c.alu('cmp', M(2, F['first']), 0); B(5, 'repack_keep')
    c.alu('cmp', M(2, F['last']), 0); B(3, 'repack_scan_next')
    B(0, 'repack_keep')
    L('repack_insert_scan')
    c.alu('cmp', M(2, F['first']), 0); B(7, 'repack_return')
    L('repack_keep')
    c.move(M(4, 16), D(0)); c.alu('add', M(4, 24), 0)
    c.alu('add', M(2, F['data_size']), 0)
    save(D(0), 'data_size')
    c.quick(1, M(2, F['entries']))
    L('repack_scan_next')
    advance(4, ENTRY.size)
    c.quick(1, D(7), sub=True)
    B(0, 'repack_scan')

    L('repack_sized')
    get('entries', D(0)); c.imm('cmp', MAX_IMAGE_ID, D(0)); B(2, 'repack_return')
    c.tst(M(2, F['last'])); B(7, 'repack_size')
    c.alu('cmp', M(2, F['count']), 0); B(7, 'repack_return')
    L('repack_size')
    c.word(0xc0fc); c.word(ENTRY.size)  # MULU.W #40,D0
    c.imm('add', HEADER.size, D(0))
    save(D(0), 'data_offset')
    c.alu('add', M(2, F['data_size']), 0)
    c.imm('cmp', MAX_BANK_BYTES, D(0)); B(2, 'repack_return')
    save(D(0), 'total')
    get('dest', D(1)); c.tst(D(1)); B(7, 'repack_success')
    c.alu('cmp', M(2, F['capacity']), 0); B(2, 'repack_return')
    c.alu('add', D(1), 0); B(5, 'repack_return')
    get('source', D(4))
    c.alu('cmp', D(4), 0); B(3, 'repack_disjoint')
    c.alu('add', M(2, F['size']), 4); B(5, 'repack_return')
    c.alu('cmp', D(4), 1); B(5, 'repack_return')
    L('repack_disjoint')

    get('dest', A(0)); get('source', A(4))
    for offset in range(0, HEADER.size, 4):
        c.move(M(4, offset), M(0, offset))
    get('entries', D(0)); c.move(D(0), M(0, 8), 'w')
    for name, offset in (('data_offset', 16), ('total', 20), ('generation', 24)):
        get(name, D(0)); c.move(D(0), M(0, offset))
    advance(0, HEADER.size); advance(4, HEADER.size)
    get('count', D(7))
    L('repack_write')
    c.tst(D(7)); B(7, 'repack_tail')
    read_id(4)
    c.tst(M(2, F['last'])); B(7, 'repack_insert_write')
    c.alu('cmp', M(2, F['first']), 0); B(5, 'repack_copy_image')
    c.alu('cmp', M(2, F['last']), 0); B(3, 'repack_write_next')
    B(0, 'repack_copy_image')
    L('repack_insert_write')
    c.tst(M(2, F['emit_blank'])); B(7, 'repack_copy_image')
    c.alu('cmp', M(2, F['first']), 0); B(5, 'repack_copy_image')
    B(1, 'repack_blank')
    L('repack_copy_image')
    for offset in range(0, ENTRY.size, 4):
        c.move(M(4, offset), M(0, offset))
    get('source', A(1))
    c.move(M(4, 12), D(0))
    c.raw('d3c0')  # ADDA.L D0,A1
    get('data_offset', D(0))
    c.move(D(0), M(0, 12))
    c.move(M(4, 16), D(4))
    c.alu('add', D(4), 0)
    c.move(M(4, 24), D(5)); c.tst(D(5)); B(7, 'repack_no_mask')
    c.move(D(0), M(0, 20))
    L('repack_no_mask')
    c.alu('add', D(5), 4)
    get('dest', A(6)); get('data_offset', D(0))
    c.raw('ddc0')  # ADDA.L D0,A6
    c.alu('add', D(4), 0); save(D(0), 'data_offset')
    c.shift(4, 1)
    L('repack_copy_words')
    c.move(POST(1), POST(6), 'w')
    c.quick(1, D(4), sub=True); B(6, 'repack_copy_words')
    advance(0, ENTRY.size)
    L('repack_write_next')
    advance(4, ENTRY.size)
    c.quick(1, D(7), sub=True)
    B(0, 'repack_write')
    L('repack_tail')
    c.tst(M(2, F['emit_blank'])); B(7, 'repack_success')
    B(1, 'repack_blank')
    L('repack_success')
    get('total', D(3))
    B(0, 'repack_epilogue')
    L('repack_return')
    c.move(I(0), D(3))
    L('repack_epilogue')
    c.word(0x4fef); c.word(FRAME)
    c.raw('4cdf77f774004e75')

    L('repack_blank')
    for name, offset in (('first', 0), ('width', 2), ('height', 4), ('depth', 6), ('stride', 8)):
        get(name, D(0)); c.move(D(0), M(0, offset), 'w')
    c.move(I(1, 'w'), M(0, 10), 'w')
    get('data_offset', D(0)); c.move(D(0), M(0, 12))
    get('plane', D(4)); c.move(D(4), M(0, 24))
    get('blank_size', D(5))
    c.move(D(5), D(6)); c.alu('sub', D(4), 6)
    c.move(D(6), M(0, 16)); c.alu('add', D(6), 0)
    c.move(D(0), M(0, 20))
    for offset in (28, 32, 36):
        c.move(I(0), M(0, offset))
    get('dest', A(6)); get('data_offset', D(0))
    c.raw('ddc0')  # ADDA.L D0,A6
    c.alu('add', D(5), 0); save(D(0), 'data_offset')
    c.shift(5, 1)
    L('repack_blank_words')
    c.move(I(0, 'w'), POST(6), 'w')
    c.quick(1, D(5), sub=True); B(6, 'repack_blank_words')
    advance(0, ENTRY.size)
    save(I(0), 'emit_blank')
    c.raw('4e75')
    return c.out(), c.labels
