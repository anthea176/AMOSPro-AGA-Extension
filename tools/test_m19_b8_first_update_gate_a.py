#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""First no-draw B7 bootstrap and public B8 AP20 construction Gate A.

Runs the actual B7 first-End armer in Unicorn M68020, with two distinct
relocations and mocked AmigaOS. Checks no Blitter draw prior to startup.
No real AMOS Runtime or Compiler is implied by this test.
"""
from __future__ import annotations

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from amos_link_test_support import relocate
from build_m19_b8_first_update_in_memory import build_b8_first_update
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update
from m19_b8_first_update_emit import emit_b8_b7_first_update, emit_b8_first_update
from test_m19_b8_atomic_integrated_b7_gate_a import AtomicIntegrated, SNAP0, SNAP1, PAGE
from m19_b8_page_manager_emit import R as SROOT
from test_m19_p0j_pending_close_end_gate_a import DB
from m19_p0j_swap_barrier_emit import READY, DIRTY
from test_m19_p0j_pending_close_end_gate_a import ready
from test_m5_generic import AMOS, EXEC

class FirstUpdateIntegrated(AtomicIntegrated):
    """Actual MC68020 B7 SET/End/Draw + B8 Bind/Arm/Update, mocked AmigaOS."""
    def __init__(self, source, layout):
        super().__init__(source, layout)
        from m19_b8_first_update_emit import emit_b8_b7_first_update, emit_b8_first_update
        b7, labels = emit_b8_b7_first_update()
        self.native, self.labels = b7, labels
        self.uc.mem_write(self.entry, relocate(b7, self.entry, {}, self.uc))
        self.labels['routed_paint_all_entry'] = labels['b8_b7_draw_trampoline_entry']
        self.labels['guarded_close_entry'] = labels['b8_b7_close_trampoline_entry']
        b8, b8labels = emit_b8_first_update()
        self.fifth_source, self.fifth_labels = b8, b8labels
        self.uc.mem_write(self.fifth, b8)
        self.snapshot_allocs = {}
        self.b8_alloc_index = 0

    def os_call(self, uc, address, size, user):
        if address == EXEC - 198:
            n, flags = self.d(0), self.d(1)
            assert n == PAGE and flags == 0x10001, ('snapshot AllocMem',n,flags)
            if self.b8_alloc_index >= 2:
                return self._os_return(0)
            ptr = (SNAP0, SNAP1)[self.b8_alloc_index]
            self.b8_alloc_index += 1
            self.snapshot_allocs[ptr] = n
            self.uc.mem_write(ptr, bytes(n))
            return self._os_return(ptr)
        if address == EXEC - 534:
            ptr = self.a(1)
            if any(p <= ptr < p + n for p,n in self.snapshot_allocs.items()):
                return self._os_return(1)
        return super().os_call(uc,address,size,user)


def main():
    candidate, meta = build_b8_first_update()
    assert candidate and meta['public_commands'] == 88
    assert meta['ap20_entries'] == 184
    assert meta['native_groups'] == [142,153,156,177,181]
    assert meta['pc16_max'] < 32766
    old7, _ = emit_b8_b7_hooks()
    new7, labels7 = emit_b8_b7_first_update()
    old8, _ = emit_b8_atomic_registered_update()
    new8, labels8 = emit_b8_first_update()
    assert new7.startswith(old7) and new8.startswith(old8)
    assert labels7['b8_b7_arm_end_nodraw_entry'] == len(old7)
    assert labels8['b8_service_update_first_entry'] == len(old8)
    # Fully decode new executable suffixes: no arbitrary data masquerading
    # as machine instructions (the B7 native prefix contains private data).
    for old, new in ((old7,new7),(old8,new8)):
        code = new[len(old):]
        decoded = list(Cs(CS_ARCH_M68K,
                          CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
                       .disasm(code,0x10000+len(old)))
        assert decoded and sum(x.size for x in decoded) == len(code)
        assert all(not x.mnemonic.startswith('dc.') for x in decoded)

    checks = 9
    for layout in ('interpreted','compiled'):
        m = ready(layout, cls=AtomicIntegrated, inject_failure=False)
        # Replace only the append-only source in both separately mapped
        # native units; no public install and no fake first Draw.
        m.native, m.labels = new7, labels7
        m.uc.mem_write(m.entry,relocate(new7,m.entry,{},m.uc))
        m.fifth_source, m.fifth_labels = new8,labels8
        m.uc.mem_write(m.fifth,new8)
        old = m.old_end
        m.put(AMOS+0x1cc,old)
        m.put(AMOS+0x1d0,old)
        prior = len(m.paint_blits)
        # The first B8 Update must be bootstrapped by an End hook that
        # runs ZERO graphics operations and does not depend on Draw.
        assert m.direct(m.entry+labels7['b8_b7_arm_end_nodraw_entry']) == 1
        assert len(m.paint_blits) == prior
        assert m.callbacks() == (m.end_callback(),)*2
        checks += 3
        assert m.direct(m.entry+labels7['b8_b7_arm_end_nodraw_entry']) == 1
        assert len(m.paint_blits) == prior
        checks += 2
        m.setup_b8_pool()
        assert m.arm() == 1
        assert m.b7_root()[0] == AMOS
        checks += 2
        assert m.direct(m.entry+labels7['b8_b7_arm_end_nodraw_entry']) == 1
        assert len(m.paint_blits) == prior
        checks += 2
    # FIRST public Update, starting with only the original AGA End hook.
    # Exercise the real existing public SET through its new AP20 shim.
    for layout in ('interpreted','compiled'):
        m = ready(layout, cls=FirstUpdateIntegrated, inject_failure=False)
        m.put(AMOS+0x1cc,m.old_end)
        m.put(AMOS+0x1d0,m.old_end)
        prior = len(m.paint_blits)
        m.labels['public_aga_bob_entry'] = m.labels['b8_b7_bob_set_bootstrap_entry']
        assert m.public('bob', ident=3, image=1, x=18, y=20) == 1
        assert m.callbacks() == (m.end_callback(),)*2
        assert len(m.paint_blits) == prior, 'SET bootstrap painted before capture'
        checks += 3
        assert m.invoke_guard('swap') == 1
        m.put(DB + 20, 0)
        before = m.physical_back_bytes()
        prior = len(m.paint_blits)
        assert m.direct(m.fifth + m.fifth_labels['b8_service_update_first_entry'],
                        maxcount=20000000) == 1
        assert m.status() == READY and len(m.paint_blits) > prior
        assert set(m.snapshot_allocs) == {SNAP0,SNAP1}
        backbit = 1 if m.get(DB+8) == 1 else 2
        snapshot = SNAP0 if backbit==1 else SNAP1
        assert bytes(m.uc.mem_read(snapshot,PAGE)) == before
        assert m.physical_back_bytes() != before
        checks += 5
        assert m.clear() == 1
        assert m.physical_back_bytes() == before and m.status() == 0
        m.invoke_guard('close')
        assert m.get(m.real_state) == 0
        assert not m.snapshot_allocs and m.b8post_calls == 1
        checks += 4

        # No SET and no B7 End callback: Update must fail/roll back
        # cleanly without drawing or exposing uninitialized state.
        n = ready(layout, cls=FirstUpdateIntegrated, inject_failure=False)
        n.put(AMOS+0x1cc,n.old_end)
        n.put(AMOS+0x1d0,n.old_end)
        assert n.invoke_guard('swap') == 1
        n.put(DB+20,0)
        before = n.physical_back_bytes()
        prior = len(n.paint_blits)
        assert n.direct(n.fifth+n.fifth_labels['b8_service_update_first_entry'],
                        maxcount=20000000) == 0
        assert n.physical_back_bytes() == before
        assert len(n.paint_blits) == prior
        assert not n.snapshot_allocs
        checks += 4

    print('M19 B8 FIRST UPDATE NODRAW MC68020 Gate A PASS',
          checks,'checks; two relocations, no Draw during bootstrap')
    print('SOURCE_ONLY_AP20',meta)

if __name__=='__main__':
    main()
