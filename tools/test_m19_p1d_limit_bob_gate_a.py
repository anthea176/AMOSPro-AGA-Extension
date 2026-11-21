#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1d native clipping on two placements with mocked Amiga services."""
from pathlib import Path

from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from amos_link_test_support import relocate
from build_m19_p1d_limit_bob_in_memory import build_p1d
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, unpack_ap20
from m19_p0a_multi_bob_abk import parse_payload
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p1d_limit_bob_emit import TABLE_BYTES, TABLE_FROM_CONTEXT, emit_limit_bobs
from test_m19_b8_s1_bank_free_gate_a import FreeMachine
from test_m19_p0d_safe_bank_blit_native import SIZE, STRIDE, SCREEN_W, SCREEN_H
from test_m19_p0e_v2_object_bridge_native import OTHER
from test_m19_p0j_pending_close_end_gate_a import DB, ready
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p1b_hotspot_draw_gate_a import machine
from test_m19_p1c_bob_priority_gate_a import HOTSPOTS, install_native, invoke, set_objects
from test_m5_generic import AMOS, AR, DR, STACK, STOP

ROOT = Path(__file__).resolve().parents[1]
ARGS = 0x58000


def set_limit(m, ident, rect, owner=AMOS):
    x, y, w, h = rect or (0, 0, 0, 0)
    for i, r in enumerate(DR):
        m.uc.reg_write(r, 0x12345600 + i)
    for i, r in enumerate(AR[:7]):
        m.uc.reg_write(r, 0x31000 + i * 256)
    m.uc.reg_write(AR[3], ARGS)
    m.uc.reg_write(AR[5], owner)
    m.uc.reg_write(DR[3], h & 0xffffffff)
    for i, value in enumerate((w, y, x, ident)):
        m.put(ARGS + i * 4, value & 0xffffffff)
    saved = {r: m.uc.reg_read(r) for r in DR + AR[:7] if r not in (DR[2], DR[3], AR[3])}
    m.uc.reg_write(UC_M68K_REG_SR, 0x2000)
    m.uc.reg_write(AR[7], STACK)
    m.put(STACK, STOP)
    m.uc.emu_start(m.entry + m.labels['p1d_limit_entry'], STOP, count=100000)
    assert m.uc.reg_read(UC_M68K_REG_PC) == STOP
    assert m.a(3) == ARGS + 16 and m.a(7) == STACK + 4 and m.d(2) == 0
    assert all(m.uc.reg_read(r) == value for r, value in saved.items())
    return m.d(3)


def load_native(m, parts, meta):
    p1c_setup = dict(meta, open_offset=meta['old_open_offset'])
    context, priority, original_open, _ = install_native(m, parts, p1c_setup)
    raw, labels = emit_limit_bobs(meta['context_delta'])
    old_end = labels['p1d_limit_entry']
    native = relocate(raw, m.entry, {}, m.uc)
    for key in ('private_blit_build_bitmap', 'p1b_frame_paint_call', 'explicit_frame_paint_call'):
        site = labels[key]
        m.uc.mem_write(m.entry + site, native[site:site+4])
    m.uc.mem_write(m.entry + old_end, native[old_end:])
    m.uc.ctl_remove_cache(m.entry, m.entry + len(native))
    m.labels.update(labels)
    m.labels['routed_paint_all_entry'] = labels['p1b_frame_draw_entry']
    reset = m.aga + len(DISPATCH_V2) + meta['open_offset']
    m.uc.mem_write(original_open, bytes.fromhex('760174004e75'))
    return context + TABLE_FROM_CONTEXT, priority, original_open, reset


def paint_model(surface, m, objects, mode, bounds, hotspots):
    expected = [bytearray(p) for p in surface]
    images = {bank: parse_payload(m.bank_payload(bank)).image(1) for bank in (10, 11)}
    order = sorted(objects, key=lambda i: (objects[i][2], i) if mode & 1 else i,
                   reverse=bool(mode & 2))
    for ident in order:
        bank, ax, ay = objects[ident]
        img = images[bank]
        hx, hy = hotspots.get(bank, (0, 0))
        zones = [(0, 0, SCREEN_W, SCREEN_H)]
        zones.extend(bounds[k] for k in (0, ident) if bounds.get(k) is not None)
        for sy in range(img.height):
            for sx in range(img.width):
                x, y = ax - hx + sx, ay - hy + sy
                if not all(l <= x < l + w and t <= y < t + h for l, t, w, h in zones):
                    continue
                if img.visible(sx, sy):
                    off, bit = y * STRIDE + x // 8, 128 >> (x & 7)
                    value = img.colour(sx, sy)
                    for i, plane in enumerate(expected):
                        if value & (1 << i):
                            plane[off] |= bit
                        else:
                            plane[off] &= 255 ^ bit
    return expected


def check_native(layout, parts, meta):
    m = machine(layout, *HOTSPOTS.values())
    table, priority, original_open, reset = load_native(m, parts, meta)
    assert set_limit(m, 0, (0, 0, 1, 1)) == 0
    assert invoke(m, reset) == 1
    assert set_limit(m, 64, (-3, -5, 9, 7)) == 1  # Before first Bob SET.
    initial_limit = bytes(m.uc.mem_read(table, TABLE_BYTES))
    m.put(OTHER + 0x1c8, m.real_state)
    assert set_limit(m, 64, (1, 1, 5, 5), owner=OTHER) == 0
    for ident, rect in ((-1, None), (65, None), (0, (0, 0, 0, 1)),
                        (0, (0, 0, 1, -1)), (0, (1, 0, 0, 0)),
                        (64, (2147483647, 0, 1, 1)),
                        (64, (0, 2147483647, 1, 1))):
        assert set_limit(m, ident, rect) == 0
        assert m.uc.mem_read(table, TABLE_BYTES) == initial_limit
    assert set_limit(m, 0, (-2147483648, -2147483648, 1, 1)) == 1
    assert set_limit(m, 0, None) == 1

    objects = {1: (10, 20, 13), 2: (11, 20, 11)}
    set_objects(m, objects)
    cases = (
        (None, None),                            # P1c default.
        ((23, 12, 5, 2), None),                  # Four edges, unaligned.
        ((23, 12, 1, 1), (23, 12, 1, 1)),        # Single pixel.
        ((23, 12, 6, 3), (25, 11, 9, 3)),        # Overlap of local/global.
        (None, (29, 9, 2, 3)),                   # Local on masked Bob only.
        ((-7, -5, 11, 9), (0, 0, 2, 2)),        # Negative origin + screen.
        ((0, 0, 90, 3), (0, 8, 90, 12)),        # Neither Bob visible.
    )
    for mode in range(4):
        assert invoke(m, priority, mode) == 1
        for global_limit, local_limit in cases:
            assert set_limit(m, 0, global_limit) == set_limit(m, 1, local_limit) == 1
            for plane, ptr in enumerate(m.back_planes):
                m.uc.mem_write(ptr, bytes((i * 7 + plane * 3) & 255 for i in range(SIZE)))
            before = m.read_back()
            front = tuple(bytes(m.uc.mem_read(p, SIZE)) for p in m.screen_planes)
            expected = paint_model(before, m, objects, mode, {0: global_limit, 1: local_limit}, HOTSPOTS)
            blits = len(m.paint_blits)
            assert m.frame() == 1
            assert m.read_back() == expected, (layout, mode, global_limit, local_limit)
            assert tuple(bytes(m.uc.mem_read(p, SIZE)) for p in m.screen_planes) == front
            assert m.get(DB + 8) == 0
            if expected == before and global_limit is not None and global_limit[1] <= 0:
                assert len(m.paint_blits) == blits
    assert set_limit(m, 0, None) == 1
    assert set_limit(m, 1, (23, 12, 4, 2)) == 1
    assert m.public('off', ident=1) == 1
    set_objects(m, {1: objects[1]})
    expected = paint_model(m.read_back(), m, objects, 3, {1: (23, 12, 4, 2)}, HOTSPOTS)
    assert m.frame() == 1 and m.read_back() == expected
    # Exercise the last programmable slot and signed screen clipping.
    assert m.public('off', ident=1) == 1
    assert m.public('off', ident=2) == 1
    edge = {64: (11, -3, -2)}
    set_objects(m, edge)
    bound = (-1, -1, 4, 3)
    assert set_limit(m, 64, bound) == 1
    before = m.read_back()
    expected = paint_model(before, m, edge, 3, {64: bound}, HOTSPOTS)
    assert expected != before
    assert m.frame() == 1 and m.read_back() == expected
    # A fully clipped Bob remains subject to source prevalidation.
    assert set_limit(m, 64, (-2147483648, -2147483648, 1, 1)) == 1
    assert m.public('bob', ident=64, x=-3, y=-2, image=4096) == 1
    before, blits = m.read_back(), len(m.paint_blits)
    assert m.frame() == 0
    assert m.read_back() == before and len(m.paint_blits) == blits
    m.uc.mem_write(original_open, bytes.fromhex('760074004e75'))
    m.uc.ctl_remove_cache(original_open, original_open + 6)
    retained = bytes(m.uc.mem_read(table, TABLE_BYTES))
    assert invoke(m, reset) == 0 and m.uc.mem_read(table, TABLE_BYTES) == retained
    m.put(m.real_state, 0)
    assert set_limit(m, 1, None) == 0
    m.put(m.real_state, m.screen)
    m.uc.mem_write(original_open, bytes.fromhex('760174004e75'))
    m.uc.ctl_remove_cache(original_open, original_open + 6)
    assert invoke(m, reset) == 1 and m.uc.mem_read(table, TABLE_BYTES) == bytes(TABLE_BYTES)
    return len(cases) * 4 + 6


def check_public_pages(layout, parts, meta):
    m = ready(layout, cls=FreeMachine, inject_failure=False)
    _, priority, _, reset = load_native(m, parts, meta)
    m.labels['guarded_close_entry'] = m.labels['b8_b7_close_trampoline_entry']
    m.labels['public_aga_bob_entry'] = m.labels['b8_b7_bob_set_bootstrap_entry']
    m.fifth_source, m.fifth_labels = emit_m19_p1a_getters()
    m.uc.mem_write(m.fifth, m.fifth_source)
    assert invoke(m, reset) == 1
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)
    objects = {1: (10, 20, 13), 2: (11, 20, 11)}
    set_objects(m, objects)
    target = m.fifth + m.fifth_labels['b8_service_update_first_entry']
    pages = set()
    for mode, bounds in ((1, {0: (23, 12, 4, 3), 1: (24, 13, 6, 6)}),
                         (3, {0: None, 1: None}),
                         (3, {0: (30, 13, 3, 2), 1: None}),
                         (0, {0: None, 1: (23, 12, 5, 3)})):
        page = m.get(DB + 8)
        pages.add(page)
        for plane, ptr in enumerate(m.active_back_planes()):
            m.uc.mem_write(ptr, bytes((i * 7 + plane * 3 + page) & 255 for i in range(SIZE)))
        before = m.read_back()
        expected = paint_model(before, m, objects, mode, bounds, {})
        assert invoke(m, priority, mode) == 1
        for scope, rect in bounds.items():
            assert set_limit(m, scope, rect) == 1
        assert m.direct(target, maxcount=20_000_000) == 1
        assert m.get(DB + 8) == page and m.read_back() == expected
        assert m.clear() == 1 and m.read_back() == before
        assert m.invoke_guard('swap') == 1
        m.put(DB + 20, 0)
    assert pages == {0, 1}
    assert m.free(10) == m.free(11) == 1
    m.invoke_guard('close')
    assert m.get(m.real_state) == 0 and not m.snapshot_allocs
    return 4


def main():
    binary, meta = build_p1d()
    assert binary == build_p1d()[0]
    assert (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes() == binary
    _, parts, _ = unpack_ap20(binary)
    assert parts[179] == GETP
    dispatch_models(parts, 181, meta['limit_offset'], 180)
    dispatch_models(parts, 142, meta['open_offset'], 12)
    scenarios = sum(check_native(layout, parts, meta) + check_public_pages(layout, parts, meta)
                    for layout in ('interpreted', 'compiled'))
    print('M19 P1d Gate A PASS', scenarios, 'scenarios across two native placements', flush=True)
    print('P1D_SOURCE_ONLY', meta)


if __name__ == '__main__':
    main()
