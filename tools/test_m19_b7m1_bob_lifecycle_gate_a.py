#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 B7-m1: functional persistent-Bob lifecycle on real emitted CPU020.

Execute installed B7-m1's exact source-derived native suffix in Unicorn,
on two disjoint AP20 placements ("compiled" means RELOCATION ONLY).
OS, video pages, and DMA are mocked. No WinUAE/Compiler/Amiga claim.
No benchmarking and no new AP20/Lib/ASC output.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from struct import unpack

from build_m19_p0j_end_lifecycle_in_memory import build_multiframe
from test_m19_p0j_end_lifecycle_gate_a import MultiframeMachine
from test_m19_p0j_pending_close_end_gate_a import ready, DB
from m19_p0j_swap_barrier_emit import DIRTY, READY

ROOT = Path(__file__).resolve().parents[1]
B7M1_SHA = '838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403'
B7M1_SIZE = 102360
LAYOUTS = ('interpreted', 'compiled')


def prepared(layout: str) -> MultiframeMachine:
    m = ready(layout, cls=MultiframeMachine, inject_failure=False)
    assert m.status() == READY and m.chip_live
    assert m.callbacks() == (m.end_callback(), m.end_callback())
    return m


def painted(m):
    """Only actual mock Blitter paint events, not Chip staging/WaitBlit."""
    return [event[0] for event in m.paint_blits
            if event[0] in ('BltMask', 'BltOpaque')]


def present_and_ack(m):
    """Present only a READY frame, then mock completed Safe/Disp messages."""
    assert m.status() == READY
    before = (m.swap_count, m.native_swap_visits)
    assert m.invoke_guard('swap') == 1
    assert (m.swap_count, m.native_swap_visits) == (before[0]+1, before[1]+1)
    assert m.status() == 0 and m.get(DB+20) == 3
    m.put(DB+20, 0)  # CPU harness: messages already delivered by the OS
    return before


def finish(m):
    """Original native Close/End cleanup, including one-time resource frees."""
    assert m.get(DB+20) == 0
    assert m.invoke_guard('close') == 1
    assert m.status() == 0 and not m.chip_live and not m.metadata
    assert len(m.free_screens) == 2 and len(m.free_ports) == 2
    assert m.callbacks() == (m.end_callback(), m.end_callback())
    m.invoke_callback(0x1cc)
    assert m.callbacks() == (m.old_end, m.old_end)
    m.invoke_callback(0x1d0)
    assert len(m.free_screens) == 2 and len(m.free_ports) == 2


def off_and_reactivate(layout: str):
    m = prepared(layout)
    present_and_ack(m)
    assert m.public('off', ident=1) == 1
    assert m.relay_call('read', ident=1)[0] == 0
    first = len(painted(m))
    selected = m.selected_triple()
    assert m.frame() == 1 and m.status() == READY
    assert painted(m)[first:] == ['BltOpaque']  # Bob 2 only
    assert m.selected_triple() == selected
    present_and_ack(m)

    assert m.public('off', ident=2) == 1
    assert m.relay_call('read', ident=2)[0] == 0
    first = len(painted(m))
    assert m.frame() == 1 and m.status() == READY
    assert painted(m)[first:] == []  # Empty persistent set is valid
    present_and_ack(m)

    # Reactivate both IDs, each from its own original AGBO source bank.
    assert m.run_select(10) == 1
    assert m.public('bob', ident=1, x=-3, y=21, image=1) == 1
    status, record = m.relay_call('read', ident=1)
    assert status == 1 and unpack('>6I', record) == (
        10, 1, (-3)&0xffffffff, 21, 1, 0)
    assert m.run_select(11) == 1
    assert m.public('bob', ident=2, x=320-5, y=19, image=1) == 1
    status, record = m.relay_call('read', ident=2)
    assert status == 1 and unpack('>6I', record) == (11,1,315,19,1,0)
    selected = m.selected_triple()
    first = len(painted(m))
    assert m.frame() == 1 and m.status() == READY
    assert painted(m)[first:] == ['BltMask', 'BltOpaque']
    assert m.selected_triple() == selected
    assert m.callbacks() == (m.end_callback(),m.end_callback())
    present_and_ack(m)
    finish(m)
    return 19


def multi_bank_counts(layout: str):
    m = prepared(layout)
    present_and_ack(m)
    assert m.public('off', ident=2) == 1
    # Grow the same live registry: 1 -> 4 -> 8 -> 16 -> 64 real Bob IDs.
    for count in (1,4,8,16,64):
        for ident in range(1,count+1):
            bank = 10 if ident & 1 else 11
            assert m.run_select(bank) == 1
            assert m.public('bob', ident=ident, image=1,
                            x=(ident*7)%65, y=(ident*11)%45) == 1
        selected = m.selected_triple()
        first = len(painted(m))
        assert m.frame() == 1, (layout, count, 'Draw')
        actual = painted(m)[first:]
        assert len(actual) == count, (layout, count, actual)
        assert actual.count('BltMask') == (count+1)//2
        assert actual.count('BltOpaque') == count//2
        assert m.selected_triple() == selected  # no bank shadow projection
        assert m.status() == READY
        assert m.callbacks() == (m.end_callback(),m.end_callback())
        present_and_ack(m)

    # Shrink the same registry without changing the selected bank.
    for ident in range(17,65):
        assert m.public('off', ident=ident) == 1
        assert m.relay_call('read', ident=ident)[0] == 0
    first = len(painted(m))
    assert m.frame() == 1
    assert painted(m)[first:].count('BltMask') == 8
    assert painted(m)[first:].count('BltOpaque') == 8
    present_and_ack(m)
    finish(m)
    return 5+5+48+4


def source_identity_and_swap_barrier(layout: str):
    # Inactive Bob's stamp must be ignored; active bank-11 Bob remains valid.
    m = prepared(layout)
    present_and_ack(m)
    assert m.public('off', ident=1) == 1
    node = m.find(10)
    gen = m.get(node+24+24)
    m.put(node+24+24, gen+1)  # injected source identity change
    first = len(painted(m))
    assert m.frame() == 1
    assert painted(m)[first:] == ['BltOpaque']
    present_and_ack(m)
    m.put(node+24+24, gen)
    finish(m)

    # The identical mutation while Bob 1 is active must veto before DMA.
    m = prepared(layout)
    present_and_ack(m)
    node = m.find(10)
    gen = m.get(node+24+24)
    m.put(node+24+24, gen+1)
    selected = m.selected_triple()
    before_blits = len(painted(m))
    before_swaps = (m.swap_count, m.native_swap_visits)
    assert m.frame() == 0 and m.status() == DIRTY
    assert len(painted(m)) == before_blits  # image gate rejects pre-DMA
    assert m.selected_triple() == selected
    assert m.invoke_guard('swap') == 0  # absolutely no ChangeScreenBuffer
    assert (m.swap_count, m.native_swap_visits) == before_swaps
    m.put(node+24+24, gen)
    assert m.frame() == 0 and m.status() == DIRTY  # no silent recovery
    assert m.invoke_guard('swap') == 0
    assert (m.swap_count, m.native_swap_visits) == before_swaps
    finish(m)
    return 16


def main():
    candidate, meta = build_multiframe()
    installed = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
    assert len(candidate) == B7M1_SIZE == len(installed)
    assert sha256(candidate).hexdigest() == meta['sha256'] == B7M1_SHA
    assert installed == candidate  # exact installed work Lib, not older B7/B6
    assert meta['native_groups'] == [142,153,156,177]
    assert meta['public_commands'] == 86 and meta['ap20_entries'] == 181
    tests = 0
    for layout in LAYOUTS:
        tests += off_and_reactivate(layout)
        tests += multi_bank_counts(layout)
        tests += source_identity_and_swap_barrier(layout)
    print('M19 B7-m1 PERSISTENT BOB LIFECYCLE MC68020 GATE A PASS',
          tests, 'functional assertions across two relocated AP20 layouts;',
          'Off/reactivation, 1/4/8/16/64 IDs, mixed source banks,',
          'stale bank pre-DMA refusal, DIRTY Swap guard, Close/End one-time frees;',
          'AmigaOS and DMA MOCKED; no FPS bench, WinUAE, real Compiler or Lib edit')


if __name__ == '__main__':
    main()
