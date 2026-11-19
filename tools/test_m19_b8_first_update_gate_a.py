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
from test_m19_b8_atomic_integrated_b7_gate_a import AtomicIntegrated
from test_m19_p0j_pending_close_end_gate_a import ready
from test_m5_generic import AMOS

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
    print('M19 B8 FIRST UPDATE NODRAW MC68020 Gate A PASS',
          checks,'checks; two relocations, no Draw during bootstrap')
    print('SOURCE_ONLY_AP20',meta)

if __name__=='__main__':
    main()
