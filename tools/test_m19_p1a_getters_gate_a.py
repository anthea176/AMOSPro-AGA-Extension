#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A: real MC68020 P1a public getter wrappers + AP20 relocation models.

Exec/TypeOfMem/AGA screen are emulated. The tests are NOT real AMOS Runtime,
AMOS Compiler, WinUAE or hardware. Do not install this candidate.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack, unpack, unpack_from
from pathlib import Path

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from test_m5_generic import DR, AR, AMOS, EXEC, STACK, STOP
from test_m19_p0a_r88_get_gate_a import ARGS
from test_m19_b8_s1_bank_free_gate_a import prepared
from test_m19_p0e_v2_object_bridge_native import OTHER
from test_ap20_v2_island_dispatch import cpu, trace_entry
from amos_link_test_support import relocate
from build_m19_b8_s1_bank_free_in_memory import build_bank_free
from build_m19_p1a_getters_in_memory import build_p1a, API, BOBS
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters, INVALID
from compiler_relocation import RBSR, GETP, unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2

ROOT = Path(__file__).resolve().parents[1]
INVALID_WORD = INVALID & 0xffffffff



def prepare_with_getters(layout):
    """Use exactly the current P0 Bank Free gate's native AGA fixture."""
    m=prepared(layout,with_bobs=False)
    native,labels=emit_m19_p1a_getters()
    m.native,m.labels=native,labels
    # Preserve the B8 routed Draw/Close guards that FreeMachine installed.
    m.labels['routed_paint_all_entry']=m.labels['b8_b7_draw_trampoline_entry']
    m.labels['guarded_close_entry']=m.labels['b8_b7_close_trampoline_entry']
    m.uc.mem_write(m.entry,relocate(native,m.entry,{},m.uc))
    return m


def query(m, field, ident, *, owner=AMOS, limit=3000000):
    assert field in ('x','y','image')
    for i,reg in enumerate(DR):
        m.uc.reg_write(reg,0x12340000+i)
    for i,reg in enumerate(AR[:7]):
        m.uc.reg_write(reg,0x31000+i*256)
    m.uc.reg_write(DR[3],ident&0xffffffff)
    m.uc.reg_write(AR[5],owner)
    m.uc.reg_write(AR[3],ARGS)
    initial={reg:m.uc.reg_read(reg) for reg in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:
        m.uc.emu_start(m.entry+m.labels['p1a_get_'+field+'_entry'],
                       STOP,count=limit)
    except Exception as exc:
        raise AssertionError(('MC68020 getter fault',field,ident,owner,
                              hex(m.uc.reg_read(UC_M68K_REG_PC)))) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4 and m.d(2)==0
    for reg,value in initial.items():
        if reg not in (DR[2],DR[3]):
            assert m.uc.reg_read(reg)==value,(
                'AMOS ABI register modified',field,reg)
    value=m.d(3)
    return value-0x100000000 if value&0x80000000 else value


def dispatch_models(parts, group, offset, stub_index):
    """Run actual AP20 dispatcher in interpreter and separated Compiler models."""
    starts = []
    at = 0
    for part in parts:
        starts.append(at)
        at += len(part)
    stub=parts[stub_index]
    assert stub.startswith(RBSR) and stub[6:8]==b'\x4e\x75'
    target = starts[group]+len(DISPATCH_V2)+offset
    signed = starts[group]-(starts[stub_index]+2)
    assert -32766 < signed < 32766
    u = cpu()
    raw = bytearray(b''.join(parts))
    raw[starts[stub_index]:starts[stub_index]+4]=pack('>Hh',0x6100,signed)
    u.mem_write(0x100000, bytes(raw))
    trace_entry(u,0x100000+starts[stub_index],0x100000+target)
    u = cpu()
    dest=0x500000
    u.mem_write(dest,parts[group])
    entry=0x101000
    u.mem_write(entry,bytes.fromhex('4eb9')+pack('>I',dest)+
                pack('>H',offset)+bytes.fromhex('4e75'))
    trace_entry(u,entry,dest+len(DISPATCH_V2)+offset)
    return 2


def main():
    p0, p0_meta = build_bank_free()
    candidate, info = build_p1a()
    original_toks, original_parts, _ = unpack_ap20(p0)
    toks,parts,_=unpack_ap20(candidate)
    assert info['p0_sha']==p0_meta['sha256']
    assert info['public_commands']==92 and info['ap20_entries']==188
    assert info['native_groups']==[142,153,156,177,181]
    assert info['pc16_max']<32766 and info['refusal_sentinel']==-32769
    assert parts[BOBS].startswith(original_parts[BOBS])
    assert parts[184]==original_parts[184]+GETP
    assert all(parts[i]==original_parts[i] for i in range(185) if i not in (BOBS,184))
    assert toks.startswith(original_toks[:-6])
    native,labels=emit_m19_p1a_getters()
    offset=labels['p1a_get_x_entry']
    code=native[offset:]
    insn=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
              disasm(code,0x100000))
    assert sum(x.size for x in insn)==len(code)
    assert all(not x.mnemonic.startswith('dc.') for x in insn)
    checks=10
    for name, _ in API:
        group,at,entry=info['targets'][name]
        assert unpack_from('>HH',parts[entry],2)==(group,at)
        assert parts[entry][6:8]==b'\x4e\x75'
        checks+=dispatch_models(parts,group,at,entry)

    for layout in ('interpreted','compiled'):
        m=prepare_with_getters(layout)
        assert query(m,'x',1)==INVALID    # never-created Bob
        checks+=1
        assert m.relay_call('reset')[0]==1
        for ident,bank,image,x,y in (
            (1,10,1,-32768,32767),
            (32,10,2,-1,0),
            (64,11,4096,32767,-32768),
        ):
            assert m.relay_call('put',ident=ident,bank=bank,
                                image=image,x=x,y=y)[0]==1
            snapshot=m.table()
            for field,value in (('x',x),('y',y),('image',image)):
                assert query(m,field,ident)==value
                assert m.table()==snapshot
                checks+=1
            m.put(OTHER+0x1c8,m.real_state)
            for field in ('x','y','image'):
                assert query(m,field,ident,owner=OTHER)==INVALID
                assert m.table()==snapshot
                checks+=1
            assert m.relay_call('off',ident=ident)[0]==1
            for field in ('x','y','image'):
                assert query(m,field,ident)==INVALID
                checks+=1
            assert m.relay_call('put',ident=ident,bank=bank,
                                image=image,x=0,y=0)[0]==1
            assert query(m,'x',ident)==0
            checks+=1
        for ident in (0,65,0xffffffff):
            for field in ('x','y','image'):
                assert query(m,field,ident)==INVALID
                checks+=1
        m.uc.mem_write(EXEC+0x128,pack('>H',0))
        assert query(m,'x',1)==INVALID
        m.uc.mem_write(EXEC+0x128,pack('>H',2))
        checks+=1
        m.put(AMOS+0x1c8,0)
        assert query(m,'x',1)==INVALID
        checks+=1

    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert len(active)==117896 and active==good==p0
    assert sha256(active).hexdigest()==info['p0_sha']
    assert candidate!=active
    print('M19 P1a PUBLIC X/Y/I BOB MC68020/AP20 GATE A PASS:',
          checks,'checks, two simulated native placements, three tokens,',
          'new source compiled into memory only, SHA',info['sha256'],
          'no actual AMOS Compiler/Runtime or physical validation')


if __name__ == '__main__':
    main()
