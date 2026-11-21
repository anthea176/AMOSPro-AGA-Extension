#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1e commands, real emitted bank edit/Update code and mocked Amiga services."""
from struct import unpack_from

from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from amos_link_test_support import relocate
from build_m19_p1e_bank_edit_in_memory import build_p1e
from compiler_relocation import unpack_ap20
from m19_p0a_multi_bob_abk import delete_images, insert_blank_image, parse_payload
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters
from m19_p1d_limit_bob_emit import emit_limit_bobs
from m19_p1e_bank_edit_emit import OBJECT, STAMP, emit_bank_edit
from test_m19_b8_s1_bank_free_gate_a import FreeMachine
from test_m19_p0d_safe_bank_blit_native import oracle
from test_m19_p0j_pending_close_end_gate_a import DB, ready
from test_m19_p0j_swap_barrier_gate_a import DIRTY
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p1c_bob_priority_gate_a import invoke
from test_m19_p1d_limit_bob_gate_a import load_native
from test_m5_generic import AMOS, AR, DR, EXEC, STACK, STOP

ARGS = 0x58000


class EditMachine(FreeMachine):
    fail_size_class = None
    expect_notification = None

    def service(self, uc, address, size, user):
        if self.targets.get(address) == 'Bnk.Change' and self.expect_notification:
            bank, data, survivors, deleted = self.expect_notification
            assert self.bank_payload(bank) == data
            new = parse_payload(data)
            assert (bank in self.nodes()) == bool(new.images)
            for slot in survivors:
                stamp = self.real_state + STAMP + (slot - 1) * 16
                assert self.get(stamp) == self.find(bank) + 24
                assert self.get(stamp + 4) == new.generation
                assert self.get(stamp + 12) == len(data)
            for slot in deleted:
                assert self.get(self.real_state + OBJECT + (slot - 1) * 24 + 16) == 0
        return super().service(uc, address, size, user)

    def os_call(self, uc, address, size, user):
        if address == EXEC - 684 and self.fail_size_class == self.d(1):
            return self._os_return(0)
        return super().os_call(uc, address, size, user)

    def call_edit(self, command, args, owner=AMOS):
        for i, r in enumerate(DR + AR[:7]):
            self.uc.reg_write(r, 0x321000 + i)
        self.uc.reg_write(AR[3], ARGS)
        self.uc.reg_write(AR[5], owner)
        self.uc.reg_write(DR[3], args[-1] & 0xffffffff)
        for i, arg in enumerate(reversed(args[:-1])):
            self.put(ARGS + 4*i, arg & 0xffffffff)
        saved = {r: self.uc.reg_read(r) for r in DR + AR[:7] if r not in (DR[2], DR[3], AR[3])}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(self.entry + self.labels['p1e_' + command + '_bob'], STOP, count=10_000_000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4 and self.a(3) == ARGS + 4*(len(args)-1) and self.d(2) == 0
        assert all(self.uc.reg_read(r) == value for r, value in saved.items())
        return self.d(3)


def snapshot(m):
    slots = bytes(m.uc.mem_read(m.real_state + OBJECT, 64*24))
    stamps = bytes(m.uc.mem_read(m.real_state + STAMP, 64*16))
    return (m.bank_payload(10), m.bank_payload(11), set(m.alive), dict(m.chip_live),
            dict(m.metadata), slots, stamps, m.selected_triple(), m.notifications)


def verify_layout(layout, parts, meta):
    m = ready(layout, cls=EditMachine, inject_failure=False)
    _, _, _, reset = load_native(m, parts, meta)
    old, _ = emit_limit_bobs(meta['context_delta'])
    native, labels = emit_bank_edit(meta['context_delta'])
    data = relocate(native, m.entry, {}, m.uc)
    for site, width in ((labels['checked_stage_copy_call'], 4),
                        (labels['checked_stage_min_count'], 6), (len(old), len(native)-len(old))):
        m.uc.mem_write(m.entry + site, data[site:site+width])
    m.uc.ctl_remove_cache(m.entry, m.entry + len(native))
    m.labels.update(labels)
    m.labels['routed_paint_all_entry'] = labels['b8_b7_draw_trampoline_entry']
    m.labels['guarded_close_entry'] = labels['b8_b7_close_trampoline_entry']
    m.labels['public_aga_bob_entry'] = labels['b8_b7_bob_set_bootstrap_entry']
    m.fifth_source, m.fifth_labels = emit_m19_p1a_getters()
    m.uc.mem_write(m.fifth, m.fifth_source)
    assert invoke(m, reset) == 1
    initial = snapshot(m)
    assert m.call_edit('del', (10, 1, 1)) == 0 and snapshot(m) == initial
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)
    guard = m.entry + labels['frame_guard_state']
    m.put(guard, DIRTY)
    assert m.call_edit('del', (10, 1, 1)) == 0 and snapshot(m) == initial
    m.put(guard, 0)
    args = (10, 3, 8, 6, 8)
    for failure in ('bank', 'metadata', 'chip'):
        m.bank_alloc_fail = failure == 'bank'
        m.alloc_fail = False
        m.fail_size_class = {'bank': None, 'metadata': 0x10001, 'chip': 3}[failure]
        assert m.call_edit('ins', args) == 0
        assert snapshot(m) == initial
    m.bank_alloc_fail = m.alloc_fail = False
    m.fail_size_class = None
    for command, bad in (('del', (10, 1, 0)), ('del', (10, 3, 5)), ('ins', (10, 1, 8, 6, 8)),
                         ('ins', (30, 3, 8, 6, 8)), ('ins', (10, 3, 8, 6, 9))):
        assert m.call_edit(command, bad) == 0 and snapshot(m) == initial
    stamp_size = m.real_state + STAMP + 12
    size = m.get(stamp_size)
    m.put(stamp_size, size + 2)
    stale = snapshot(m)
    assert m.call_edit('ins', args) == 0 and snapshot(m) == stale
    m.put(stamp_size, size)
    assert snapshot(m) == initial
    target = insert_blank_image(initial[0], *args[1:])
    m.expect_notification = (10, target, (1,), ())
    assert m.call_edit('ins', args) == 1
    m.expect_notification = None
    assert m.bank_payload(10) == target and m.bank_payload(11) == initial[1]
    assert m.selected_triple() == initial[-2]  # bank 11 remained selected
    assert m.relay_call('read', ident=1)[0] == 1
    assert m.run_select(10) == 1
    assert m.public('bob', ident=3, x=15, y=16, image=3) == 1
    assert m.public('bob', ident=4, x=16, y=17, image=1) == 1
    compact = delete_images(target, 1, 2)
    m.expect_notification = (10, compact, (3,), (1, 4))
    assert m.call_edit('del', (10, 1, 2)) == 1
    m.expect_notification = None
    model = parse_payload(m.bank_payload(11)).image(1)
    target_update = m.fifth + m.fifth_labels['b8_service_update_first_entry']
    pages = set()
    for _ in range(2):
        page = m.get(DB + 8)
        pages.add(page)
        before = m.read_back()
        assert m.direct(target_update, maxcount=20_000_000) == 1
        assert m.get(DB + 8) == page and m.read_back() == oracle(before, model, 9, 11)
        assert m.clear() == 1 and m.read_back() == before
        assert m.invoke_guard('swap') == 1
        m.put(DB + 20, 0)
    assert len(pages) == 2
    empty = delete_images(compact, 3, 3)
    m.expect_notification = (10, empty, (), (3,))
    assert m.call_edit('del', (10, 3, 3)) == 1
    m.expect_notification = None
    assert len(m.bank_payload(10)) == 32 and 10 not in m.nodes()
    assert m.call_edit('ins', args) == 1
    assert parse_payload(m.bank_payload(10)).image(3).mask == bytes(12)
    assert not m.relay_call('read', ident=3)[0]
    assert m.relay_call('read', ident=2)[0] == 1
    assert m.free(10) == m.free(11) == 1
    m.invoke_guard('close')
    assert not m.chip_live and not m.metadata and not m.snapshot_allocs


def main():
    binary, meta = build_p1e()
    assert build_p1e()[0] == binary
    _, parts, _ = unpack_ap20(binary)
    for stub in (185, 187):
        group, offset = unpack_from('>HH', parts[stub], 2)
        assert group == meta['group']
        dispatch_models(parts, group, offset, stub)
    for layout in ('interpreted', 'compiled'):
        verify_layout(layout, parts, meta)
    print('P1e EDIT Gate A PASS on two MC68020 layouts: transactional refusals, callback state, first Update, Clear and Swap')
    print('P1E_IN_MEMORY', meta)


if __name__ == '__main__':
    main()
