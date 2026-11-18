#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""B7-m2 Gate A: real MC68020 native Close resets persistent Bob slots.

Runs in two disjoint AP20-style layouts. Models a second open and Draw
without Erase All, and tests CPU/ABI/Close/End safety. Exec, Intuition,
graphics.library, Safe/Disp and Blitter/DMA are mocked. This is NOT
WinUAE or AMOS Compiler validation. No installed library is modified.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC

from amos_link_test_support import relocate
from build_m19_p0j_end_lifecycle_in_memory import build_multiframe
from build_m19_b7m2_close_reset_in_memory import build_close_reset
from compiler_relocation import RBSR, unpack_ap20
from m19_b7m2_close_reset_emit import emit_close_reset
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle_multiframe
from test_m19_p0j_end_lifecycle_gate_a import MultiframeMachine
from test_m19_p0j_pending_close_end_gate_a import ready, DB, SAFE, DISP
from test_m5_generic import AMOS, EXEC

ROOT = Path(__file__).resolve().parents[1]


class CloseResetMachine(MultiframeMachine):
    """Redirect the mock's public Close entry as the candidate AP20 stub does."""
    def __init__(self, source, layout):
        super().__init__(source, layout)
        self.native, self.labels = emit_close_reset()
        self.uc.mem_write(self.entry, relocate(self.native, self.entry, {}, self.uc))
        self.labels['routed_paint_all_entry'] = self.labels['b7_multiframe_draw_entry']
        self.legacy_close_offset = self.labels['guarded_close_entry']
        self.labels['guarded_close_entry'] = self.labels['b7m2_close_reset_entry']
        self.table_at_legacy_close = None
        self.legacy_close_visits = 0
        self.uc.hook_add(UC_HOOK_CODE, self._on_legacy_close,
                         begin=self.old_close, end=self.old_close)

    def _on_legacy_close(self, uc, address, size, user):
        self.legacy_close_visits += 1
        self.table_at_legacy_close = self.table()


def active_ids(table):
    return [i for i in range(1, 65) if
            unpack_from('>I', table, 8 + (i - 1) * 24 + 16)[0] == 1]


def stage_sixty_four_then_sixteen(m):
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)  # model delivered Safe/Disp after initial two-Bob frame
    for ident in range(3, 65):
        assert m.run_select(10 if ident & 1 else 11) == 1
        assert m.public('bob', ident=ident, image=1,
                        x=(ident * 7) % 65, y=(ident * 11) % 45) == 1
    assert m.frame() == 1
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)
    for ident in range(17, 65):
        assert m.public('off', ident=ident) == 1
    assert m.frame() == 1
    assert m.invoke_guard('swap') == 1
    m.put(DB + 20, 0)
    before = m.table()
    assert active_ids(before) == list(range(1, 17))
    return before


def main():
    base, previous = build_multiframe()
    installed = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
    assert len(installed) == len(base) == 102360 and installed == base
    assert previous['sha256'] == sha256(base).hexdigest()

    candidate, report = build_close_reset()
    assert candidate != base and report['predecessor_sha'] == previous['sha256']
    assert report['public_commands'] == 86 and report['ap20_entries'] == 181
    assert report['native_groups'] == [142, 153, 156, 177]
    assert report['pc16_max'] < 32766
    assert report['close_stub'] == 179 and report['close_group'] == 177
    a, oldlab = emit_end_lifecycle_multiframe()
    b, labels = emit_close_reset()
    assert b.startswith(a) and labels['b7m2_close_reset_entry'] == len(a)
    assert b[len(a):]
    ins = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
               .disasm(b[len(a):], 0x120000 + len(a)))
    assert ins and sum(inst.size for inst in ins) == len(b) - len(a)
    assert all(not inst.mnemonic.startswith('dc.') for inst in ins)
    old_tokens, old_parts, _ = unpack_ap20(base)
    new_tokens, new_parts, _ = unpack_ap20(candidate)
    assert old_tokens == new_tokens and len(new_parts) == len(old_parts) == 181
    assert new_parts[177].startswith(old_parts[177])
    assert all(new_parts[i] == old_parts[i] for i in range(181)
               if i not in (177, 179))
    assert new_parts[179].startswith(RBSR)
    assertions = 15

    for layout in ('interpreted', 'compiled'):
        # Reproduce the exact structural defect in installed B7-m1.
        old = ready(layout, cls=MultiframeMachine, inject_failure=False)
        expected = stage_sixty_four_then_sixteen(old)
        old.invoke_guard('close')
        assert old.get(old.real_state) == 0
        assert old.table() == expected, 'B7-m1 unexpectedly reset Bob slots'
        assert active_ids(old.table()) == list(range(1, 17))
        assertions += 3

        # Candidate must clear all 64 IDs BEFORE the real native AGA Close.
        m = ready(layout, cls=CloseResetMachine, inject_failure=False)
        stage_sixty_four_then_sixteen(m)
        m.invoke_guard('close')
        assert m.legacy_close_visits == 1
        assert m.get(m.real_state) == 0 and m.status() == 0
        assert m.table() == pack('>I', AMOS) + bytes(len(m.table()) - 4)
        assert m.table_at_legacy_close == m.table()
        assert len(m.free_screens) == 2 and len(m.free_ports) == 2
        assert not m.chip_live and not m.metadata
        assertions += 6

        # A second Close must not free screen buffers / ports twice.
        m.invoke_guard('close')
        assert m.legacy_close_visits == 1
        assert len(m.free_screens) == 2 and len(m.free_ports) == 2
        assertions += 2

        # New run, same AMOS program context. Reopen original AGA State.
        m.activate_aga_state()
        m.configure_real_state()
        m.put(DB + 12, SAFE)
        m.put(DB + 16, DISP)
        m.put(DB + 20, 0)
        m.safe = True
        assert m.run_select(10) == 1
        assert m.public('bob', ident=1, x=5, y=7, image=1) == 1
        assert m.run_select(11) == 1
        assert m.public('bob', ident=2, x=9, y=11, image=1) == 1
        assert active_ids(m.table()) == [1, 2]
        before = len(m.paint_blits)
        assert m.frame() == 1, (layout, 'second run Draw', m.status(),
                                active_ids(m.table()))
        painted = [p[0] for p in m.paint_blits[before:]
                   if p[0] in ('BltMask', 'BltOpaque')]
        assert painted == ['BltMask', 'BltOpaque'], (layout, painted)
        assert m.invoke_guard('swap') == 1
        # The OS fixture does not reallocate distinct ScreenBuffers/ports
        # for a second Screen Open; testing a second Close here would
        # double-free MOCK addresses and falsely report a native fault.
        # Second Draw/Swap is valid; a second actual Close needs an
        # independent rebuilt OS resource fixture or real WinUAE.
        assert m.get(m.real_state) == m.screen
        assert active_ids(m.table()) == [1, 2]
        assert len(m.free_screens) == 2 and len(m.free_ports) == 2
        assertions += 8

        # Invalid CPU refuses before touching the table or the screen.
        n = ready(layout, cls=CloseResetMachine, inject_failure=False)
        snapshot = n.table()
        n.uc.mem_write(EXEC + 0x128, b'\x00\x00')
        n.invoke_guard('close')
        assert n.get(n.real_state) == n.screen and n.table() == snapshot
        assert n.legacy_close_visits == 0 and not n.free_screens
        n.uc.mem_write(EXEC + 0x128, b'\x00\x02')
        n.reject_type = n.real_state
        n.invoke_guard('close')
        assert n.get(n.real_state) == n.screen and n.table() == snapshot
        assert n.legacy_close_visits == 0
        n.reject_type = None
        n.invoke_guard('close')
        assert n.get(n.real_state) == 0
        assert n.legacy_close_visits == 1
        assertions += 6

        # Pending Safe/Disp may keep the Screen live; no premature free.
        p = ready(layout, cls=CloseResetMachine, inject_failure=True)
        p.invoke_guard('close')
        assert p.get(p.real_state) == p.screen
        assert not p.free_screens and not p.free_ports
        assert p.status() != 0  # DIRTY remains on failed Close
        p.safe_after = p.safe_count + 1
        p.disp_after = p.disp_count + 2
        p.invoke_guard('close')
        assert p.get(p.real_state) == 0
        assert len(p.free_screens) == 2 and len(p.free_ports) == 2
        assertions += 5

    print('M19 B7-m2 CLOSE RESET MC68020 GATE A PASS', assertions,
          'assertion groups, two relocated placements; first/second run,',
          '64->16->0 Bobs, old B7-m1 failure reproduced,',
          'original Close, ABI, CPU reject, Safe/Disp pending, End; OS MOCKED')
    print('B7M2_SOURCE_ONLY', report)


if __name__ == '__main__':
    main()
