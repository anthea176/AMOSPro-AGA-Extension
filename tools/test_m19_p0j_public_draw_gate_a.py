#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P0j-b6 Gate A: new zero-argument numeric Draw function token and 68020 ABI.

Checks two AP20 relocation models (interpreter Rbsr, Compiler-style JSR)
and runs exact source-emitted B5 guarded Bob/Swap code on two native
placements with mocked AmigaOS/graphics/Blitter. Not real Compiler/WinUAE.
"""
from __future__ import annotations

from struct import pack, unpack_from

from unicorn import UC_HOOK_CODE
from audit_ap20 import inspect, parse, walk_tokens
from compiler_relocation import RBSR, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p0j_swap_barrier_in_memory import build as build_b5
from build_m19_p0j_public_draw_in_memory import build
from m19_p0j_swap_barrier_emit import DIRTY, READY
from test_m19_p0j_swap_barrier_gate_a import prepare, DB
from test_m19_p0d_safe_bank_blit_native import oracle, SIZE
from m19_p0a_multi_bob_abk import parse_payload
from test_ap20_v2_island_dispatch import cpu, trace_entry


def dispatch_models(parts, group, offset, stub):
    """Execute actual AP20 dispatcher entry path on a MC68020 CPU."""
    starts = []
    pc = 0
    for part in parts:
        starts.append(pc)
        pc += len(part)
    assert parts[stub][:2] == RBSR
    assert parts[stub][6:] == b'\x4e\x75'
    target = starts[group] + len(DISPATCH_V2) + offset

    # AMOS interpreter: Rbsr reassembled as 16-bit relative BSR.W.
    signed = starts[group] - (starts[stub] + 2)
    assert -32766 < signed < 32766
    u = cpu()
    raw = bytearray(b''.join(parts))
    raw[starts[stub]:starts[stub]+4] = pack('>Hh',0x6100,signed)
    u.mem_write(0x100000, bytes(raw))
    trace_entry(u,0x100000+starts[stub],0x100000+target)

    # Compiler relocation MODEL: detached group, JSR.L dispatcher,
    # unsigned entry offset after return-address marker.
    u = cpu()
    dst = 0x500000
    u.mem_write(dst,parts[group])
    entry = 0x101000
    u.mem_write(entry,bytes.fromhex('4eb9') + pack('>I',dst) +
                pack('>H',offset) + bytes.fromhex('4e75'))
    trace_entry(u,entry,dst+len(DISPATCH_V2)+offset)
    return 2


def main():
    candidate, meta = build()
    prior,_ = build_b5()
    tok,parts,_ = unpack_ap20(candidate)
    oldtok,oldparts,_ = unpack_ap20(prior)
    assert len(parts)==181 and parts[:180]==oldparts
    assert meta['public_commands']==86 and meta['ap20_entries']==181
    assert meta['native_groups']==[142,153,156,177]
    assert meta['pc16_max']<32766
    assert meta['draw_function_entry']==180
    assert meta['draw_signature']=='0'
    assert meta['guarded_swap_entry']==178
    assert meta['guarded_close_entry']==179
    assert tok.startswith(oldtok[:-6])
    old_api=inspect(parse(prior))
    api=inspect(parse(candidate))
    assert not old_api['issues'] and not api['issues']
    assert api['tokens'][:-1]==old_api['tokens']
    draw=[t for t in walk_tokens(tok) if t['name']=='aga bob draw']
    assert len(draw)==1
    assert (draw[0]['instruction'],draw[0]['function'],draw[0]['signature'])==(1,180,'0')
    assert unpack_from('>HH',parts[180],2)==(
        meta['draw_native_group'],meta['draw_native_offset'])
    assert pc16_displacements(parts)[180]<0
    checks=8
    checks+=dispatch_models(parts,meta['draw_native_group'],
                            meta['draw_native_offset'],180)

    for layout in ('interpreted','compiled'):
        # Public zero-argument numeric return is exactly D3 (D2=0) from
        # the pre-existing guarded_frame_draw_entry, with full AMOS ABI.
        m=prepare(layout)
        assert m.status()==0
        selected=m.selected_triple()
        initial=m.read_back()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        img10=parse_payload(m.bank_payload(10)).image(1)
        img11=parse_payload(m.bank_payload(11)).image(1)
        expected=oracle(oracle(initial,img10,5,7),img11,9,11)
        assert m.frame()==1
        assert m.d(2)==0 and m.d(3)==1
        assert m.status()==READY and m.read_back()==expected
        assert m.selected_triple()==selected and m.get(DB+8)==0
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        assert m.invoke_guard('swap')==1
        assert m.status()==0 and m.get(DB+8)==1 and m.swap_count==1
        checks+=7

        # Completely invalid AGBO mask -> return 0 without any pixel DMA,
        # but latch DIRTY so even an unrelated future Swap cannot show it.
        m=prepare(layout,all64=True)
        idx=m.find(10)+24+32+24
        length=m.get(idx)
        assert length>1
        m.put(idx,length-1)
        before=m.read_back()
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        assert m.frame()==0
        assert m.d(2)==0 and m.d(3)==0
        assert m.read_back()==before and m.status()==DIRTY
        assert sum(t[0] in ('BltMask','BltOpaque') for t in m.paint_blits)==0
        assert m.invoke_guard('swap')==0
        assert m.swap_count==0 and m.get(DB+8)==0
        m.put(idx,length)
        assert m.frame()==0 and m.status()==DIRTY
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        checks+=7

        # First Bob paints with real mask; second fails SafePort. A public
        # numeric 0 MUST NOT cause a partial-buffer presentation.
        m=prepare(layout)
        front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
        original=m.read_back()
        first=oracle(original,parse_payload(m.bank_payload(10)).image(1),5,7)
        calls=[]
        def fail_second(uc,address,size,unused):
            calls.append(address)
            if len(calls)==2:
                m.safe=False
                m.put(DB+20,3)
        addr=m.entry+m.labels['explicit_safe_blit_entry']
        hook=m.uc.hook_add(UC_HOOK_CODE,fail_second,begin=addr,end=addr)
        try:
            assert m.frame()==0
        finally:
            m.uc.hook_del(hook)
        assert m.d(2)==0 and m.d(3)==0
        assert len(calls)==2 and m.read_back()==first
        assert sum(t[0]=='BltMask' for t in m.paint_blits)==1
        assert sum(t[0]=='BltOpaque' for t in m.paint_blits)==0
        assert m.status()==DIRTY and m.invoke_guard('swap')==0
        assert m.native_swap_visits==0 and m.swap_count==0
        assert m.get(DB+8)==0
        assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
        checks+=7

    print('M19 P0j-b6 PUBLIC AGA BOB DRAW NUMERIC AP20/MC68020 GATE A PASS',
          checks,'checks; 86 commands, 181 AP20 entries, 4 native islands,',
          'interpreter+Compiler dispatch models, 2 exact native placements;',
          '0/1 AMOS numeric ABI and guarded Swap,',
          'NO installed Lib/ASC, NO true AMOS Compiler/WinUAE')


if __name__=='__main__':
    main()
