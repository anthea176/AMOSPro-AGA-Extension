#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b5 MC68020 Gate A: actual legacy AGA Swap denied after failed Bob.

Two independent AP20-style placements; real emitted BOBS/AGA 68020 runs
under Unicorn with AMOS/Exec/graphics/Intuition and DMA mocked.
No real AMOS Compiler, WinUAE or distributed library claim.
"""
from __future__ import annotations

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from test_m5_generic import DR, AR, AMOS, EXEC, INTUI, STACK, STOP
from test_m19_p0j_explicit_safe_draw_gate_a import NoShadowMachine
from test_m19_p0d_safe_bank_blit_native import oracle, SIZE
from test_m19_p0a_r88_get_gate_a import SCREEN_W
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0j_swap_barrier_in_memory import build
from m19_p0j_swap_barrier_emit import (
    emit_swap_barrier, AGA_SWAP_OFFSET, DIRTY, READY, G,
)
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw
from amos_link_test_support import relocate

DB = 0x53000
SAFE = 0x5b000
DISP = 0x5b200


class BarrierMachine(NoShadowMachine):
    def __init__(self, source, layout):
        super().__init__(source, layout)
        self.native, self.labels = emit_swap_barrier()
        self.uc.mem_write(self.entry, relocate(self.native, self.entry, {}, self.uc))
        self.labels['routed_paint_all_entry'] = self.labels['guarded_frame_draw_entry']
        self.swap_count = 0
        self.swap_accept = True
        self.old_swap = self.aga + AGA_SWAP_OFFSET
        self.native_swap_visits = 0
        self.uc.hook_add(UC_HOOK_CODE, self._swap_hook,
                         begin=self.old_swap, end=self.old_swap)

    def _swap_hook(self, uc, address, size, unused):
        self.native_swap_visits += 1

    def os_call(self, uc, address, size, user):
        if address == INTUI - 780:
            assert self.a(0) == self.screen, 'Swap screen is not AGA State screen'
            assert self.a(1) in (0x54000, 0x54100), 'Swap ScreenBuffer invalid'
            self.swap_count += 1
            return self._os_return(1 if self.swap_accept else 0)
        if address == EXEC - 372 and self.a(0) == DISP:
            return self._os_return(DISP + 0x100)
        return super().os_call(uc, address, size, user)

    def invoke_guard(self, kind, *, owner=AMOS, count=7000000):
        label = {'swap':'guarded_swap_entry', 'close':'guarded_close_entry'}[kind]
        for n, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x542000 + n)
        for n, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x43000 + n*0x100)
        self.uc.reg_write(AR[5], owner)
        saved = {r:self.uc.reg_read(r) for r in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        try:
            self.uc.emu_start(self.entry+self.labels[label], STOP, count=count)
        except Exception as exc:
            raise AssertionError(('P0j-b5 private '+kind+' fault', str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)), self.paint_blits[-10:],
                self.get(self.entry+self.labels['frame_guard_state']),
                self.swap_count)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK + 4
        for r, val in saved.items():
            if kind == 'swap' and r in (DR[2],DR[3]):
                continue
            assert self.uc.reg_read(r) == val, ('guard ABI',kind,r)
        if kind == 'swap':
            assert self.d(2) == 0 and self.d(3) in (0,1)
            return self.d(3)
        return 1

    def status(self):
        return self.get(self.entry + self.labels['frame_guard_state'] + G['status'])


def prepare(layout, *, all64=False):
    lib, _ = build_p0c()
    m = BarrierMachine(lib, layout)
    assert m.run_select(10) == 1
    assert m.run_get(1,4,5,20,8) == 1
    assert m.mask(True,1,0) == 1
    assert m.run_select(11) == 1
    assert m.run_get(1,7,8,16,15) == 1
    m.activate_aga_state()
    m.configure_real_state()
    m.put(DB+12, SAFE)
    m.put(DB+16, DISP)
    m.put(DB+20, 0)
    m.safe = True
    if all64:
        for ident in range(1,65):
            bank = 10 if ident <= 32 else 11
            assert m.run_select(bank) == 1
            assert m.public('bob',ident=ident,image=1,
                            x=(ident*7)%65,y=(ident*11)%45) == 1
    else:
        assert m.run_select(10) == 1
        assert m.public('bob',ident=1,x=5,y=7,image=1) == 1
        assert m.run_select(11) == 1
        assert m.public('bob',ident=2,x=9,y=11,image=1) == 1
    assert m.run_select(11) == 1
    return m


def main():
    candidate, meta = build()
    assert meta['public_commands'] == 85 and meta['ap20_entries'] == 180
    assert meta['native_groups'] == [142,153,156,177]
    assert meta['pc16_max'] < 32766
    old, _ = emit_explicit_bob_draw()
    source, labels = emit_swap_barrier()
    assert source.startswith(old)
    code = source[len(old):labels['frame_guard_state']]
    ins = list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
               .disasm(code,0x100000+len(old)))
    assert ins and sum(i.size for i in ins) == len(code)
    assert all(not i.mnemonic.startswith('dc.') for i in ins)
    checks = 0

    for layout in ('interpreted', 'compiled'):
        # Unprotected legacy Swap remains usable before using Bob Draw.
        m = prepare(layout)
        assert m.status() == 0
        assert m.invoke_guard('swap') == 1
        assert m.swap_count == m.native_swap_visits == 1
        assert m.get(DB+8) == 1
        assert m.status() == 0
        checks += 4

        # Successful guarded Draw -> original native Swap; state consumed.
        m = prepare(layout)
        front = tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        start = m.read_back()
        i10 = parse_payload(m.bank_payload(10)).image(1)
        i11 = parse_payload(m.bank_payload(11)).image(1)
        expected = oracle(oracle(start,i10,5,7),i11,9,11)
        assert m.frame() == 1
        assert m.status() == READY and m.read_back() == expected
        assert m.invoke_guard('swap') == 1
        assert m.swap_count == m.native_swap_visits == 1
        assert m.status() == 0 and m.get(DB+8) == 1
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes) == front
        checks += 6

        # Failed legacy ChangeScreenBuffer is retryable; do not discard READY.
        m = prepare(layout)
        assert m.frame() == 1
        m.swap_accept = False
        assert m.invoke_guard('swap') == 0
        assert m.status() == READY and m.get(DB+8) == 0
        m.swap_accept = True
        assert m.invoke_guard('swap') == 1
        assert m.get(DB+8) == 1 and m.status() == 0
        assert m.swap_count == m.native_swap_visits == 2
        checks += 5

        # Unexpected old AGA Swap source bytes: refuse without invoking it.
        m = prepare(layout)
        assert m.frame() == 1
        native = bytes(m.uc.mem_read(m.old_swap,4))
        m.uc.mem_write(m.old_swap,b'\x4e\x71\x4e\x71')
        assert m.invoke_guard('swap') == 0
        assert m.native_swap_visits == 0 and m.swap_count == 0
        assert m.status() == READY and m.get(DB+8) == 0
        m.uc.mem_write(m.old_swap,native)
        assert m.invoke_guard('swap') == 1
        checks += 4

        # Preflight refusal with a damaged source mask is conservatively
        # latched even when no pixel DMA occurred; only Close can reset.
        m = prepare(layout,all64=True)
        entry = m.find(10)+24+32
        mask_len = m.get(entry+24)
        assert mask_len > 1
        m.put(entry+24,mask_len-1)
        front = tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        before = m.read_back()
        assert m.frame() == 0
        assert m.status() == DIRTY
        assert m.read_back() == before
        assert sum(t[0] in ('BltOpaque','BltMask') for t in m.paint_blits) == 0
        assert m.invoke_guard('swap') == 0
        assert m.native_swap_visits == 0 and m.swap_count == 0
        assert m.get(DB+8) == 0
        m.put(entry+24,mask_len)
        assert m.frame() == 0 and m.status() == DIRTY
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes) == front
        checks += 9

        # Fail SafePort at the second Bob, AFTER real masked pixels were
        # painted. The PUBLIC guarded Swap cannot present this partial page.
        m = prepare(layout)
        start = m.read_back()
        front = tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        img = parse_payload(m.bank_payload(10)).image(1)
        first_only = oracle(start,img,5,7)
        visits = []
        def sabotage_safe(uc, address, size, unused):
            visits.append(address)
            if len(visits) == 2:
                m.safe = False
                m.put(DB+20,3)
        where = m.entry + m.labels['explicit_safe_blit_entry']
        hook = m.uc.hook_add(UC_HOOK_CODE,sabotage_safe,
                             begin=where,end=where)
        try:
            assert m.frame() == 0
        finally:
            m.uc.hook_del(hook)
        assert len(visits) == 2 and m.read_back() == first_only
        assert m.status() == DIRTY
        assert sum(t[0] == 'BltMask' for t in m.paint_blits) == 1
        assert sum(t[0] == 'BltOpaque' for t in m.paint_blits) == 0
        assert m.invoke_guard('swap') == 0
        assert m.swap_count == 0 and m.native_swap_visits == 0
        assert m.get(DB+8) == 0 and m.read_back() == first_only
        assert m.frame() == 0
        assert m.get(DB+8) == 0 and m.status() == DIRTY
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes) == front
        checks += 11

        # Close is the only recovery path in this prototype. The fixture
        # must first acknowledge Safe/Disp: its pending-Close OS behavior
        # is NOT a WinUAE/AmigaOS validation.
        m.safe = True
        m.put(DB+20,0)
        assert m.invoke_guard('close') == 1
        assert m.status() == 0
        assert m.root() == (0,0) and not m.chip_live and not m.metadata
        assert m.get(m.real_state) == 0
        checks += 4

    print('M19 P0j-b5 GUARDED AGA SWAP MC68020 GATE A PASS',
          checks, 'checks; two independent native placements,',
          'real original native AGA Swap invoked only on safe frames,',
          'dirty frame refused without ChangeScreenBuffer,',
          'mask corruption and late SafePort failure; source-only,',
          'NO public Draw, NO WinUAE/real Compiler, no distributed Lib')


if __name__ == '__main__':
    main()
