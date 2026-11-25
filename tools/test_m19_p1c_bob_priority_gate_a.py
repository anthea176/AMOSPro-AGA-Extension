#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A for the actual P1c native priority, AP20 dispatch and pixel order."""
from pathlib import Path

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from amos_link_test_support import relocate
from build_m19_p1c_bob_priority_in_memory import build_p1c
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, unpack_ap20
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p0a_multi_bob_abk import parse_payload
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p1c_bob_priority_emit import emit_priority_bobs
from test_m19_b8_s1_bank_free_gate_a import FreeMachine
from test_m19_p0d_safe_bank_blit_native import SIZE, oracle
from test_m19_p0j_pending_close_end_gate_a import DB, ready
from test_m19_p0e_v2_object_bridge_native import OTHER
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p1b_hotspot_draw_gate_a import machine
from test_m5_generic import AMOS, AR, DR, STACK, STOP

ROOT = Path(__file__).resolve().parents[1]
HOTSPOTS = {10: (0, 4), 11: (0, 0)}


def invoke(m, address, value=0, owner=AMOS):
    for index, reg in enumerate(DR):
        m.uc.reg_write(reg, 0x12300000 + index)
    for index, reg in enumerate(AR[:7]):
        m.uc.reg_write(reg, 0x31000 + 256 * index)
    m.uc.reg_write(DR[3], value & 0xffffffff)
    m.uc.reg_write(AR[5], owner)
    saved = {reg: m.uc.reg_read(reg) for reg in DR + AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR, 0x2000)
    m.uc.reg_write(AR[7], STACK)
    m.put(STACK, STOP)
    m.uc.emu_start(address, STOP, count=3_000_000)
    assert m.uc.reg_read(UC_M68K_REG_PC) == STOP
    assert m.a(7) == STACK + 4 and m.d(2) == 0
    assert all(m.uc.reg_read(reg) == original for reg, original in saved.items()
               if reg not in (DR[2], DR[3]))
    return m.d(3)


def install_native(m, parts, meta):
    native, labels = emit_priority_bobs(meta['context_delta'])
    m.labels = labels
    m.labels['routed_paint_all_entry'] = labels['p1b_frame_draw_entry']
    # The seed fixtures have already created live registry/cache state.
    # Install the two link changes and suffix without overwriting that data.
    relocated = relocate(native, m.entry, {}, m.uc)
    baseline_size = len(emit_b8_s1_bank_free()[0])
    for site, size in ((labels['p1b_source_patch_site'], 4),
                       (labels['p1b_frame_draw_entry'], 8),
                       (baseline_size, len(native) - baseline_size)):
        m.uc.mem_write(m.entry + site, relocated[site:site + size])
    m.uc.ctl_remove_cache(m.entry, m.entry + len(native))
    m.aga_native = parts[142]
    append_offset = len(DISPATCH_V2) + meta['open_offset']
    m.uc.mem_write(m.aga + append_offset, m.aga_native[append_offset:])
    context = m.real_state + meta['context_delta']
    entry = m.entry + labels['p1c_priority_entry']
    original_open = m.aga + len(DISPATCH_V2) + 1102
    wrapper = m.aga + len(DISPATCH_V2) + meta['open_offset']
    return context, entry, original_open, wrapper


def set_objects(m, objects):
    for ident, (bank, x, y) in objects.items():
        assert m.run_select(bank) == 1
        assert m.public('bob', ident=ident, x=x, y=y, image=1) == 1


def expect_frame(m, objects, mode):
    initial = m.read_back()
    front = tuple(bytes(m.uc.mem_read(ptr, SIZE)) for ptr in m.screen_planes)
    images = {bank: parse_payload(m.bank_payload(bank)).image(1) for bank in HOTSPOTS}
    expected = initial
    order = sorted(objects, key=lambda ident: (objects[ident][2], ident) if mode & 1 else ident,
                   reverse=bool(mode & 2))
    for ident in order:
        bank, x, y = objects[ident]
        dx, dy = HOTSPOTS[bank]
        expected = oracle(expected, images[bank], x - dx, y - dy)
    assert m.frame() == 1
    assert m.read_back() == expected, (mode, order, 'back buffer differs')
    assert tuple(bytes(m.uc.mem_read(ptr, SIZE)) for ptr in m.screen_planes) == front
    assert m.get(0x53000 + 8) == 0
    return expected


def check_public_update(layout, parts, meta):
    m = ready(layout, cls=FreeMachine, inject_failure=False)
    _, entry, original_open, wrapper = install_native(m, parts, meta)
    m.labels['routed_paint_all_entry'] = m.labels['b8_b7_draw_trampoline_entry']
    m.labels['guarded_close_entry'] = m.labels['b8_b7_close_trampoline_entry']
    m.labels['public_aga_bob_entry'] = m.labels['b8_b7_bob_set_bootstrap_entry']
    m.fifth_source, m.fifth_labels = emit_m19_p1a_getters()
    m.uc.mem_write(m.fifth, m.fifth_source)
    m.uc.mem_write(original_open, bytes.fromhex('760174004e75'))
    assert invoke(m, wrapper) == 1
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)
    # For both display pages use the real fifth-island B8 Update and Clear.
    objects = {1: (10, 20, 13), 2: (11, 20, 11)}
    set_objects(m, objects)
    images = {bank: parse_payload(m.bank_payload(bank)).image(1) for bank in (10, 11)}
    target = m.fifth + m.fifth_labels['b8_service_update_first_entry']
    physical_pages = set()
    for mode, order in ((1, (2, 1)), (3, (1, 2))):
        page = m.get(DB + 8)
        physical_pages.add(page)
        for plane, ptr in enumerate(m.active_back_planes()):
            m.uc.mem_write(ptr, bytes((i * 7 + plane * 3 + page) & 255 for i in range(SIZE)))
        before = m.read_back()
        expected = before
        for ident in order:
            bank, x, y = objects[ident]
            expected = oracle(expected, images[bank], x, y)
        assert invoke(m, entry, mode) == 1
        assert m.direct(target, maxcount=20_000_000) == 1
        assert m.get(DB + 8) == page and m.read_back() == expected, (
            mode, page, m.get(DB + 8), m.paint_blits[-10:],
            [(plane, p, a, b) for plane, (got, want) in enumerate(zip(m.read_back(), expected))
             for p, (a, b) in enumerate(zip(got, want)) if a != b][:12],
        )
        assert m.clear() == 1 and m.read_back() == before
        assert m.invoke_guard('swap') == 1
        m.put(DB + 20, 0)
    assert physical_pages == {0, 1}
    assert m.free(10) == m.free(11) == 1
    assert not m.chip_live and not m.metadata, (m.chip_live, m.metadata, m.root(), m.nodes())
    m.invoke_guard('close')
    assert m.get(m.real_state) == 0 and not m.snapshot_allocs
    assert invoke(m, entry, 1) == 0
    return len(physical_pages)


def main():
    binary, meta = build_p1c()
    _, parts, _ = unpack_ap20(binary)
    assert binary == build_p1c()[0]
    from active_library import P1C_SHA, P1D_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, SPRITE_L2B_HISTORICAL_SHAS, verify_active
    from hashlib import sha256
    active, _, _ = verify_active(ROOT)
    assert sha256(active).hexdigest() in (P1C_SHA, P1D_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, *SPRITE_L2B_HISTORICAL_SHAS)
    assert sha256(binary).hexdigest() == P1C_SHA
    assert parts[177] == GETP
    dispatch_models(parts, 179, meta['priority_offset'], 178)
    dispatch_models(parts, 142, meta['open_offset'], 12)
    native, labels = emit_priority_bobs(meta['context_delta'])
    section = native[labels['p1c_frame_dispatch']:]
    decoder = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
    decoded = list(decoder.disasm(section, 0x120000))
    assert sum(op.size for op in decoded) == len(section)
    assert all(not op.mnemonic.startswith('dc.') for op in decoded)

    cases = 0
    for layout in ('interpreted', 'compiled'):
        m = machine(layout, *HOTSPOTS.values())
        context, entry, original_open, wrapper = install_native(m, parts, meta)
        # Isolate the wrapper completion contract from legacy OpenScreenTagList.
        # Its JSR must reach the original routine at the computed relocation.
        saved = bytes(m.uc.mem_read(original_open, 6))
        m.uc.mem_write(original_open, bytes.fromhex('760174004e75'))
        assert invoke(m, entry, 1) == 0  # no ownership before a successful Open
        assert invoke(m, wrapper) == 1
        assert (m.get(context), m.get(context + 4)) == (AMOS, 0)
        m.put(OTHER + 0x1c8, m.real_state)
        assert invoke(m, entry, 1, OTHER) == 0

        objects = {1: (10, 20, 13), 2: (11, 20, 11)}
        set_objects(m, objects)
        results = []
        for mode in range(4):
            # Reset the back buffer to the same nonuniform scenery every time.
            for ptr in m.back_planes:
                m.uc.mem_write(ptr, bytes((i * 7) & 255 for i in range(SIZE)))
            assert invoke(m, entry, mode) == 1
            assert invoke(m, entry, -1) == invoke(m, entry, 4) == 0
            assert m.get(context + 4) == mode
            results.append(expect_frame(m, objects, mode))
            cases += 1
        assert results[0] == results[3] and results[1] == results[2]
        assert results[0] != results[1], 'fixture must distinguish overlap order'

        for objects in ({1: (10, 20, 15), 2: (11, 20, 15)},
                        {1: (10, -2, -1), 2: (11, -2, 1)}):
            set_objects(m, objects)
            for mode in (1, 3):
                assert invoke(m, entry, mode) == 1
                expect_frame(m, objects, mode)
                cases += 1

        all_bobs = {ident: (10 if ident % 2 else 11, ident % 6, (64 - ident) % 13)
                    for ident in range(1, 65)}
        set_objects(m, all_bobs)
        expect_frame(m, all_bobs, 3)
        assert m.public('off', ident=2) == 1
        inactive = all_bobs.pop(2)
        expect_frame(m, all_bobs, 3)
        all_bobs[2] = inactive
        set_objects(m, {2: inactive})
        expect_frame(m, all_bobs, 3)
        cases += 3

        assert m.run_select(11) == 1
        assert m.public('bob', ident=64, x=10, y=10, image=4096) == 1
        before, paints = m.read_back(), len(m.paint_blits)
        assert m.frame() == 0  # invalid image ID
        assert m.read_back() == before and len(m.paint_blits) == paints
        set_objects(m, {64: all_bobs[64]})
        mask_length = m.find(10) + 24 + 32 + 24
        old_length = m.get(mask_length)
        assert old_length > 1
        m.put(mask_length, old_length - 1)
        assert m.frame() == 0  # invalid live AGBO mask span
        assert m.read_back() == before and len(m.paint_blits) == paints
        m.put(mask_length, old_length)
        cases += 2

        m.uc.mem_write(original_open, bytes.fromhex('760074004e75'))
        m.uc.ctl_remove_cache(original_open, original_open + 6)
        assert invoke(m, wrapper) == 0 and m.get(context + 4) == 3
        screen = m.get(m.real_state)
        m.put(m.real_state, 0)
        assert invoke(m, entry, 1) == 0
        m.uc.mem_write(original_open, bytes.fromhex('760174004e75'))
        m.uc.ctl_remove_cache(original_open, original_open + 6)
        m.put(m.real_state, screen)
        assert invoke(m, wrapper) == 1 and m.get(context + 4) == 0
        m.uc.mem_write(original_open, saved)
        cases += 3
        cases += check_public_update(layout, parts, meta)

    print('M19 P1c Gate A PASS', cases, 'native scenarios across two placements')
    print('P1C_SOURCE_ONLY', meta)


if __name__ == '__main__':
    main()
