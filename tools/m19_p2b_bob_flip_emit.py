#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2b Bob Flip, shared draw/collision transform and bounded per-object Chip cache."""
from struct import pack, pack_into, unpack_from

from m68k_emit import A, D, I, M, PRE, POST, Code
from m19_p0d_safe_bank_blit_emit import F as SAFE
from m19_p2a_public_bob_col_emit import emit_p2a_public_col
from m19_p2b_planar_orientation020_emit import emit_planar_orientation020

SLOT_BYTES = 64
MODE, CACHE_MODE, BANK, IMAGE, PAYLOAD, GENERATION, PIXELS, MASK, BLOCK, SIZE = range(0, 40, 4)
SAVES = '48e7cffe'
RESTORE = '4cdf7ff3'


def emit_bob_flip(context_delta):
    old, labels = emit_p2a_public_col(context_delta)
    c = Code()
    c.b.extend(old)
    c.labels.update(labels)
    B, L = c.branch, c.label
    hooks = {}
    pc32 = []

    def pc(reg, target):
        c.word(0x41fb | reg << 9)
        c.word(0x0170)
        pc32.append((len(c.b), target))
        c.b.extend(bytes(4))

    def bsr_sites(start, end, target):
        return [off for off in range(start, end, 2)
                if old[off:off+2] == b'\x61\x00'
                and off+2+unpack_from('>h', old, off+2)[0] == labels[target]]

    def one_call(start, end, target):
        site, = bsr_sites(start, end, target)
        return site

    def frame(size):
        c.raw(SAVES)
        c.word(0x4fef); c.word(-size)
        c.move(A(7), A(2))

    def out(size):
        c.word(0x4fef); c.word(size)
        c.raw(RESTORE)

    def at(offset, address_reg):
        c.move(A(2), A(address_reg))
        c.word(0xd1fc | address_reg << 9)
        c.b.extend(pack('>I', offset))

    def numeric_return(size):
        out(size)
        c.raw('74004e75')

    def bit(register, number):
        c.word(0x0800 | register); c.word(number)

    # D0 ID -> A0 slot; table is local to this relocated BOBS group.
    L('p2b_slot')
    pc(0, 'p2b_slots')
    c.move(D(0), D(2))
    c.quick(1, D(2), sub=True)
    c.shift(2, 6, left=True)
    c.word(0xd1c2)  # ADDA.L D2,A0
    c.word(0x4e75)

    # D0 ID -> D3 mode, validates scope and range without OS calls.
    L('p2b_mode')
    pc(0, 'p2b_owner')
    c.move(A(5), D(2)); c.alu('cmp', M(0), 2)
    B(6, 'p2b_mode_normal')
    c.tst(D(0)); B(7, 'p2b_mode_normal')
    c.imm('cmp', 64, D(0)); B(2, 'p2b_mode_normal')
    B(1, 'p2b_slot')
    c.move(M(0, MODE), D(3))
    c.word(0x4e75)
    L('p2b_mode_normal')
    c.raw('76004e75')

    # A3 slot -> free cached variant. Every existing paint is synchronous
    # (the original private painter waits for the Blitter before returning).
    L('p2b_free_slot')
    c.move(M(3, BLOCK), D(0)); c.tst(D(0)); B(7, 'p2b_free_slot_done')
    c.move(D(0), A(1))
    c.move(M(3, SIZE), D(0))
    c.move(I(0), M(3, BLOCK))
    c.raw('2c780004')
    c.call_os(-210)
    L('p2b_free_slot_done')
    c.word(0x4e75)

    # Set orientation for an active checked Bob, consuming a single GetP long.
    L('p2b_public_flip')
    frame(40)
    c.move(D(3), M(2, 0))
    c.move(POST(3), M(2, 4))
    c.move(A(3), M(2, 8))  # GetP must retain the advanced A3 across MOVEM restore.
    c.imm('cmp', 3, D(3)); B(2, 'p2b_flip_fail')
    B(1, 'p1c_context')
    c.move(A(0), D(0)); B(7, 'p2b_flip_fail')
    pc(0, 'p2b_owner')
    c.move(M(0), D(0)); B(7, 'p2b_flip_read')
    c.move(A(5), D(1)); c.alu('cmp', D(1), 0); B(6, 'p2b_flip_fail')
    L('p2b_flip_read')
    at(16, 1)
    c.move(M(2, 4), D(0))
    B(1, 'relay_checked_read_entry')
    c.tst(D(3)); B(7, 'p2b_flip_fail')
    pc(0, 'p2b_owner')
    c.move(A(5), M(0))
    c.move(M(2, 4), D(0)); B(1, 'p2b_slot')
    c.move(M(2, 0), D(3)); c.move(D(3), M(0, MODE))
    c.tst(D(3)); B(6, 'p2b_flip_ok')
    c.move(A(0), A(3)); B(1, 'p2b_free_slot')
    L('p2b_flip_ok')
    c.word(0x7601)
    B(0, 'p2b_flip_return')
    L('p2b_flip_fail')
    c.word(0x7600)
    L('p2b_flip_return')
    c.move(M(2, 8), D(2))
    out(40)
    c.move(D(2), A(3))
    c.raw('74004e75')

    # D0 Bob ID, D1 bank, D4 image, A1 -> checked 36-byte descriptor.
    # Replace the two data pointers on success. Source identity comes from
    # the exact live P0j checked lookup, never inferred from an address alone.
    L('p2b_variant')
    frame(80)
    c.move(D(1), M(2, 0)); c.move(D(4), M(2, 4)); c.move(A(1), M(2, 8))
    B(1, 'p2b_mode')
    c.tst(D(3)); B(7, 'p2b_variant_ok')
    c.move(A(0), A(3))
    c.move(D(3), M(2, 12))
    at(32, 1)
    c.move(M(2, 0), D(3))
    B(1, 'explicit_bank_lookup_entry')
    c.tst(D(3)); B(7, 'p2b_variant_fail')
    c.move(M(2, 8), A(4))
    c.tst(M(3, BLOCK)); B(7, 'p2b_variant_miss')
    keys = ((M(2, 12), CACHE_MODE), (M(2, 0), BANK), (M(2, 4), IMAGE),
            (M(2, 32), PAYLOAD), (M(2, 36), GENERATION), (M(4), PIXELS), (M(4, 4), MASK))
    for source, key in keys:
        c.move(source, D(0)); c.alu('cmp', M(3, key), 0); B(6, 'p2b_variant_miss')
    B(0, 'p2b_variant_publish')

    L('p2b_variant_miss')
    c.move(M(4, 20), D(4))
    c.move(M(4, 24), D(6))
    c.raw('4c046000')  # MULU.L D4,D6: bytes in the colour planes.
    c.move(D(6), M(2, 16))
    c.tst(M(4, 4)); B(7, 'p2b_variant_prepare')
    c.move(M(4), D(0)); c.alu('add', D(6), 0); B(5, 'p2b_variant_fail')
    c.alu('cmp', M(4, 4), 0); B(6, 'p2b_variant_fail')  # AGBO canonical adjacency
    c.alu('add', M(4, 24), 6)
    c.quick(1, D(4))
    L('p2b_variant_prepare')
    c.move(M(4), A(0))
    c.move(M(4, 8), D(0)); c.move(M(4, 12), D(1)); c.move(M(2, 12), D(5))
    c.raw('2c780004')
    B(1, 'p2b_materialize_chip')
    c.tst(D(3)); B(7, 'p2b_variant_fail')
    c.move(A(1), M(2, 20)); c.move(D(7), M(2, 24))
    B(1, 'p2b_free_slot')
    for source, key in (*keys, (M(2, 20), BLOCK), (M(2, 24), SIZE)):
        c.move(source, M(3, key))

    L('p2b_variant_publish')
    c.move(M(3, BLOCK), D(0)); c.move(D(0), M(4))
    c.tst(M(4, 4)); B(7, 'p2b_variant_ok')
    c.move(M(4, 20), D(1))
    c.move(M(4, 24), D(2))
    c.raw('4c012000')  # MULU.L D1,D2
    c.alu('add', D(2), 0); c.move(D(0), M(4, 4))
    L('p2b_variant_ok')
    c.word(0x7601)
    B(0, 'p2b_variant_return')
    L('p2b_variant_fail')
    c.word(0x7600)
    L('p2b_variant_return')
    numeric_return(80)

    # Change the logical coordinates passed to the old origin helper by
    # old hotspot - mirrored hotspot, in signed long arithmetic.
    # A0 points to signed original hotspot words; A1 to the image descriptor.
    L('p2b_adjust_anchor')
    for mode_bit, hot, extent, coordinate in ((0, 0, 8, 1), (1, 2, 12, 4)):
        bit(3, mode_bit); B(7, f'p2b_axis_done_{mode_bit}')
        c.move(M(0, hot), D(2), 'w')
        c.word(0x48c2)  # EXT.L D2
        c.shift(2, 1, left=True)
        c.alu('sub', M(1, extent), 2)
        c.quick(1, D(2))
        c.alu('add', D(2), coordinate)
        L(f'p2b_axis_done_{mode_bit}')
    c.word(0x4e75)

    # P1b source-identified hotspot BSR is diverted through the checked
    # painter's own frame. Mode zero retains the original hotspot path.
    draw_site = one_call(labels['p1b_image_found'], labels['p1b_hotspot_origin_entry'],
                         'p1b_hotspot_origin_entry')
    hooks[draw_site] = (0x6000, 'p2b_paint')
    c.labels['p2b_paint_continue'] = draw_site+4
    L('p2b_paint')
    c.move(A(0), PRE(7))
    pc(0, 'p1d_drawing_id'); c.move(M(0), D(0))
    B(1, 'p2b_mode')
    c.tst(D(3)); B(7, 'p2b_paint_normal')
    c.move(D(3), PRE(7))
    c.move(M(4, SAFE['bank']), D(1)); c.move(M(4, SAFE['image']), D(4))
    c.move(A(4), A(1))
    B(1, 'p2b_variant')
    c.tst(D(3)); B(7, 'p2b_paint_fail')
    c.move(POST(7), D(3))
    c.move(M(7), A(0))
    c.word(0xd1fc); c.b.extend(pack('>I', 28))  # A0 -> original hot words
    c.move(M(4, SAFE['x']), D(1)); c.move(M(4, SAFE['y']), D(4))
    B(1, 'p2b_adjust_anchor')
    c.move(POST(7), A(0))
    B(0, 'p2b_paint_hotspot')
    L('p2b_paint_normal')
    c.move(POST(7), A(0))
    L('p2b_paint_hotspot')
    B(1, 'p1b_hotspot_origin_entry')
    B(0, 'p2b_paint_continue')
    L('p2b_paint_fail')
    c.quick(8, A(7))
    c.move(M(4, SAFE['saved_a3']), A(3))
    B(0, 'draw_reject')

    # The query's pair snapshot belongs to its own stack. Apply the very
    # same variant and anchor rules before the original P1d geometry build.
    L('p2b_geometry')
    frame(20)
    for source, off in ((D(0), 0), (D(1), 4), (A(0), 8), (A(3), 12)):
        c.move(source, M(2, off))
    for idx in range(2):
        done = f'p2b_geo_done_{idx}'
        c.move(M(2, idx*4), D(0))
        B(1, 'p2b_mode'); c.tst(D(3)); B(7, done)
        c.move(D(3), M(2, 16))
        c.move(M(2, 8), A(4))
        if idx:
            c.word(0xd9fc); c.b.extend(pack('>I', 60))
        c.move(A(4), A(1))
        c.word(0xd3fc); c.b.extend(pack('>I', 24))
        c.move(M(4), D(1)); c.move(M(4, 4), D(4))
        B(1, 'p2b_variant')
        c.tst(D(3)); B(7, 'p2b_geometry_fail')
        c.move(M(2, 16), D(3))
        c.move(M(2, 12), A(0))
        if idx:
            c.quick(4, A(0))
        c.move(M(4, 8), D(1)); c.move(M(4, 12), D(4))
        B(1, 'p2b_adjust_anchor')
        c.move(D(1), M(4, 8)); c.move(D(4), M(4, 12))
        L(done)
    out(20)
    B(0, 'p2a_pair_geometry_entry')
    L('p2b_geometry_fail')
    c.word(0x7600)
    numeric_return(20)

    # Close and both End routes reach the original full-register epilogue.
    # Release only a matching owner's resources and only after actual close.
    for label in ('b8_b7_close_return', 'b8_b7_end_return', 'b7_end_return'):
        off = labels[label]
        assert old[off:off+6] == bytes.fromhex('4cdf7fff4e75'), label
        hooks[off] = (0x6000, 'p2b_close_return')
    L('p2b_close_return')
    pc(0, 'p2b_owner')
    c.move(M(0), D(0)); B(7, 'p2b_close_restore')
    c.move(A(5), D(1)); c.alu('cmp', D(1), 0); B(6, 'p2b_close_restore')
    c.move(M(5, 0x1c8), D(0)); B(7, 'p2b_closed')
    c.move(D(0), A(1))
    c.raw('2c780004'); c.call_os(-534)
    c.tst(D(0)); B(7, 'p2b_close_restore')
    c.move(M(5, 0x1c8), A(0)); c.tst(M(0)); B(6, 'p2b_close_restore')
    L('p2b_closed')
    c.move(I(0), D(4)); B(1, 'p2b_purge')
    pc(0, 'p2b_owner'); c.move(I(0), M(0))
    L('p2b_close_restore')
    c.raw('4cdf7fff4e75')

    # After a successful Bank Free, retire that bank's variants as well.
    bank_site = one_call(labels['b8s1_bank_free_release'], labels['b8s1_bank_free_return'],
                         'registry_free_entry')
    hooks[bank_site] = (0x6100, 'p2b_bank_free')
    L('p2b_bank_free')
    c.raw(SAVES)
    c.move(D(3), D(4))
    B(1, 'registry_free_entry')
    c.tst(D(3)); B(7, 'p2b_bank_free_return')
    pc(0, 'p2b_owner')
    c.move(A(5), D(0)); c.alu('cmp', M(0), 0); B(6, 'p2b_bank_free_return')
    B(1, 'p2b_purge')
    c.word(0x7601)
    L('p2b_bank_free_return')
    c.raw(RESTORE + '74004e75')

    # D4 selects bank or zero for all. D4/D5/A3 are Exec callee-saved.
    L('p2b_purge')
    pc(3, 'p2b_slots')
    c.move(I(64), D(5))
    L('p2b_purge_loop')
    c.tst(D(4)); B(7, 'p2b_clear_mode')
    c.alu('cmp', M(3, BANK), 4); B(6, 'p2b_purge_next')
    B(0, 'p2b_purge_slot')
    L('p2b_clear_mode')
    c.move(I(0), M(3, MODE))
    L('p2b_purge_slot')
    B(1, 'p2b_free_slot')
    L('p2b_purge_next')
    c.word(0xd7fc); c.b.extend(pack('>I', SLOT_BYTES))
    c.quick(1, D(5), sub=True); B(6, 'p2b_purge_loop')
    c.word(0x4e75)

    native, native_labels = emit_planar_orientation020()
    c.labels['p2b_materialize_chip'] = len(c.b)+native_labels['p2b_planar_chip_prepare_entry']
    c.b.extend(native)
    L('p2b_owner'); c.b.extend(bytes(4))
    L('p2b_slots'); c.b.extend(bytes(64*SLOT_BYTES))

    # Redirect only the one existing PC32 callback reference.
    geometry_sites = [off for off in range(labels['p2a_public_bob_col'], len(old)-7, 2)
                      if old[off:off+4] == bytes.fromhex('41fb0170')
                      and off+2+unpack_from('>i', old, off+4)[0] == labels['p2a_pair_geometry_entry']]
    geo_site, = geometry_sites
    pack_into('>i', c.b, geo_site+4, c.labels['p2b_geometry']-(geo_site+2))
    for off, (op, name) in hooks.items():
        pack_into('>Hh', c.b, off, op, c.labels[name]-(off+2))
    for off, label in pc32:
        pack_into('>i', c.b, off, c.labels[label]-(off-2))
    return c.out(), c.labels
