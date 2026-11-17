#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0g native 020 Gate A: distinct raw and bank-checked Bob reads.

Execute the REAL source-emitted relay in two unrelated V2 placements.
Exec/AMOS Bnk.GetAdr and screen services are mocked. No WinUAE B/C claim.
"""
from __future__ import annotations

from struct import unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE

from amos_link_test_support import relocate
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0g_checked_read_in_memory import build
from m19_p0g_checked_read_emit import emit_checked_read, checked_read_offset
from m19_p0f_public_bound_in_memory import emit_bound_public
from test_m19_p0f_public_bound_native import BoundMachine
from test_m19_p0e_v2_object_bridge_native import CANARY
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m5_generic import EXEC, AMOS


class CheckedMachine(BoundMachine):
    def __init__(self, source, layout):
        super().__init__(source, layout)
        self.public_native, self.labels = emit_checked_read()
        self.uc.mem_write(self.entry, relocate(
            self.public_native, self.entry, {}, self.uc))
        self.checked_calls = 0
        target = self.agabridge + checked_read_offset()
        def count_check(uc, address, size, extra):
            self.checked_calls += 1
        self.uc.hook_add(UC_HOOK_CODE, count_check, begin=target, end=target)

    def checked(self, ident=1, **kwargs):
        # Exercise the appended private entry through the existing relay ABI.
        # The original raw-read entry remains available and unmodified.
        previous = self.labels['relay_read_entry']
        try:
            self.labels['relay_read_entry'] = self.labels['relay_checked_read_entry']
            return self.relay_call('read', ident=ident, **kwargs)
        finally:
            self.labels['relay_read_entry'] = previous


def main():
    baseline, _ = build_p0c()
    candidate, meta = build()
    assert meta['public_commands'] == 85 and meta['ap20_entries'] == 95
    assert meta['native_groups'] == 4 and meta['pc16_margin'] >= 64
    old, old_labels = emit_bound_public()
    new, labels = emit_checked_read()
    assert new.startswith(old)
    assert labels['relay_read_entry'] == old_labels['relay_read_entry']
    assert labels['relay_checked_read_entry'] == len(old)
    code = new[len(old):]
    ins = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
               .disasm(code, 0x100000 + len(old)))
    assert ins and sum(i.size for i in ins) == len(code)
    assert all(not i.mnemonic.startswith('dc.') for i in ins)
    checks = 0
    for layout in ('interpreted', 'compiled'):
        m = CheckedMachine(baseline, layout)
        assert m.run_select(10) == 1
        assert m.run_get(1, 4, 5, 20, 8) == 1
        assert m.run_select(11) == 1
        assert m.run_get(1, 7, 8, 16, 15) == 1
        assert m.run_select(10) == 1
        m.activate_aga_state()

        # A real persistent binding, not a fabricated descriptor.
        assert m.public('bob', ident=1, x=103, y=72, image=1) == 1
        raw, rec = m.relay_call('read', ident=1)
        assert raw == 1 and unpack('>6I', rec) == (10, 1, 103, 72, 1, 0)
        status, valid = m.checked(ident=1)
        assert status == 1 and valid == rec
        checks += 2

        assert m.run_select(11) == 1
        assert m.public('bob', ident=2, x=-12, y=31, image=1) == 1
        assert m.checked(ident=1)[0] == 1
        status, valid = m.checked(ident=2)
        assert status == 1
        assert unpack('>6I', valid) == (
            11, 1, (-12) & 0xffffffff, 31, 1, 0)
        checks += 3

        immutable = (m.table(), m.shadows())
        node = m.find(10)
        generation = m.get(node + 24 + 24)
        m.put(node + 24 + 24, generation + 1)
        assert m.relay_call('read', ident=1)[0] == 1
        assert m.checked(ident=1) == (0, CANARY)
        assert (m.table(), m.shadows()) == immutable
        m.put(node + 24 + 24, generation)
        assert m.checked(ident=1)[0] == 1
        checks += 3

        old_head = m.get(HEAD)
        m.put(HEAD, 0)
        assert m.relay_call('read', ident=1)[0] == 1
        assert m.checked(ident=1) == (0, CANARY)
        m.put(HEAD, old_head)
        assert m.checked(ident=1)[0] == 1
        checks += 3

        for ident in (0, 65, 3):
            assert m.checked(ident=ident) == (0, CANARY)
            checks += 1
        assert m.checked(ident=1, output=0)[0] == 0
        assert m.checked(ident=1, output=0x5c101)[0] == 0
        assert m.checked(ident=1, owner=AMOS + 0x1000) == (0, CANARY)
        checks += 3

        m.uc.mem_write(EXEC + 0x128, b'\0\0')
        assert m.checked(ident=1) == (0, CANARY)
        m.uc.mem_write(EXEC + 0x128, b'\0\x02')
        assert m.checked(ident=1)[0] == 1
        checks += 2

        assert m.public('off', ident=1) == 1
        assert m.relay_call('read', ident=1) == (0, CANARY)
        assert m.checked(ident=1) == (0, CANARY)
        assert m.public('bob', ident=1, x=20, y=20, image=1) == 1
        assert m.checked(ident=1)[0] == 1
        checks += 4

        assert m.relay_call('reset')[0] == 1
        assert m.checked(ident=1) == (0, CANARY)
        assert m.checked(ident=2) == (0, CANARY)
        assert m.checked_calls >= 9
        checks += 3
    print('M19 P0g SOURCE-PINNED MC68020 CHECKED READ GATE A PASS',
          checks, 'cases, 2 source-disjoint V2 placements; ABI protected;',
          'bank generation and erasure rejected without buffer writes;',
          'no public Draw, no WinUAE Runtime/Compiler test')


if __name__ == '__main__':
    main()
