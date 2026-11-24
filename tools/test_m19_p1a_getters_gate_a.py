#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P1a Gate A: real fifth-group native getters and two AP20 relocation models.

Run the exact P0 Bank Free fixture with source-emitted public wrappers under
Unicorn MC68020. Exec/Gfx/AMOS/Blitter remain MOCKED: not a real WinUAE run.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack_from
from pathlib import Path

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_get_gate_a import ARGS
from test_m19_p0e_v2_object_bridge_native import OTHER
from test_m19_b8_s1_bank_free_gate_a import prepared
from test_ap20_v2_island_dispatch import cpu,trace_entry
from build_m19_b8_s1_bank_free_in_memory import build_bank_free
from build_m19_p1a_getters_in_memory import build_p1a,API,FIFTH
from m19_p1a_bob_getters_emit import emit_m19_p1a_getters,INVALID
from compiler_relocation import RBSR,GETP,unpack_ap20
from compiler_bridge_v2_probe import DISPATCH_V2

ROOT=Path(__file__).resolve().parents[1]


def setup(layout):
    m=prepared(layout,with_bobs=True)  # real B7 callback armed by public Bob
    native,labels=emit_m19_p1a_getters()
    m.fifth_source,m.fifth_labels=native,labels
    m.uc.mem_write(m.fifth,native)      # fifth physical island, PC relative
    return m


def query(m,field,ident,*,owner=AMOS,limit=3000000):
    assert field in ('x','y','image')
    for i,r in enumerate(DR):m.uc.reg_write(r,0x12340000+i)
    for i,r in enumerate(AR[:7]):m.uc.reg_write(r,0x31000+i*256)
    m.uc.reg_write(DR[3],ident&0xffffffff)
    m.uc.reg_write(AR[5],owner)
    m.uc.reg_write(AR[3],ARGS)
    before={r:m.uc.reg_read(r) for r in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK);m.put(STACK,STOP)
    try:
        m.uc.emu_start(m.fifth+m.fifth_labels['p1a_get_'+field+'_entry'],
                       STOP,count=limit)
    except Exception as exc:
        raise AssertionError(('P1a MC68020 native getter fault',field,ident,
                 owner,hex(m.uc.reg_read(UC_M68K_REG_PC)))) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4 and m.d(2)==0
    for reg,value in before.items():
        if reg not in (DR[2],DR[3]):
            assert m.uc.reg_read(reg)==value,(
                'P1a public AMOS ABI clobbered',field,reg)
    answer=m.d(3)
    return answer-0x100000000 if answer&0x80000000 else answer


def dispatch_models(parts,group,offset,stub_index):
    starts=[];pc=0
    for part in parts:
        starts.append(pc);pc+=len(part)
    stub=parts[stub_index]
    assert stub.startswith(RBSR) and stub[6:8]==b'\x4e\x75'
    target=starts[group]+len(DISPATCH_V2)+offset
    rel=starts[group]-(starts[stub_index]+2)
    assert -32766<rel<32766
    u=cpu()
    raw=bytearray(b''.join(parts))
    raw[starts[stub_index]:starts[stub_index]+4]=pack('>Hh',0x6100,rel)
    u.mem_write(0x100000,bytes(raw))
    trace_entry(u,0x100000+starts[stub_index],0x100000+target)
    u=cpu()
    dest=0x500000
    u.mem_write(dest,parts[group])
    entry=0x101000
    u.mem_write(entry,bytes.fromhex('4eb9')+pack('>I',dest)+
                pack('>H',offset)+bytes.fromhex('4e75'))
    trace_entry(u,entry,dest+len(DISPATCH_V2)+offset)
    return 2


def main():
    p0,p0meta=build_bank_free()
    candidate,info=build_p1a()
    oldtok,oldparts,_=unpack_ap20(p0)
    tok,parts,_=unpack_ap20(candidate)
    assert info['p0_sha']==p0meta['sha256']
    assert info['public_commands']==92 and info['ap20_entries']==188
    assert info['native_groups']==[142,153,156,177,181]
    assert info['pc16_max']<32766 and info['refusal_sentinel']==-32769
    assert parts[177]==oldparts[177]
    assert parts[FIFTH].startswith(oldparts[FIFTH])
    assert parts[184]==oldparts[184]+GETP
    assert all(parts[i]==oldparts[i] for i in range(185) if i not in (FIFTH,184))
    assert tok.startswith(oldtok[:-6])
    new,labels=emit_m19_p1a_getters()
    oldlen=labels['p1a_read_bridge_entry']
    code=new[oldlen:]
    instructions=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
                      disasm(code,0x100000))
    assert sum(x.size for x in instructions)==len(code)
    assert all(not i.mnemonic.startswith('dc.') for i in instructions)
    checks=12
    for name,_ in API:
        group,off,idx=info['targets'][name]
        assert group==FIFTH and unpack_from('>HH',parts[idx],2)==(group,off)
        checks+=dispatch_models(parts,group,off,idx)

    for layout in ('interpreted','compiled'):
        m=setup(layout)
        assert query(m,'x',3)==INVALID
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
            # Foreign process with otherwise valid callback must be rejected.
            for off in (0x1c8,0x1cc,0x1d0):
                m.put(OTHER+off,m.get(AMOS+off))
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
        m.put(AMOS+0x1cc,0)
        assert query(m,'x',1)==INVALID
        m.put(AMOS+0x1cc,m.get(AMOS+0x1d0))
        checks+=1
        # Bank Free disables dependent Bobs but not other-bank objects.
        if m.status()==0:
            assert m.free(10)==1
            assert query(m,'x',1)==INVALID
            assert query(m,'image',32)==INVALID
            assert query(m,'y',64)==0
            checks+=4

    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert len(p0)==117896 and sha256(p0).hexdigest()==info['p0_sha'], "Historical P0 fixture must remain unchanged"
    from active_library import P2D_SHA
    assert len(good)==136020 and sha256(good).hexdigest()==P2D_SHA, "Promoted P2d LAST_GOOD must be exact"
    assert len(candidate)==118816 and sha256(candidate).hexdigest()==info['sha256']
    from active_library import P1B_SHA, P1C_SHA, P1D_SHA, P1E_SHA, P2D_SHA, S1P1E_SHA, P2DL2_SHA, P2DL2B_SHA, verify_active
    verified, _, _ = verify_active(ROOT)
    assert active == verified and active != candidate
    assert sha256(good).hexdigest() == P2D_SHA
    assert sha256(active).hexdigest() in (P2D_SHA,S1P1E_SHA,P2DL2_SHA,P2DL2B_SHA)
    if sha256(active).hexdigest()==P2D_SHA:
        assert active==good
    print('M19 P1a BOB X/Y/I PUBLIC NUMERIC GATE A PASS',checks,'checks;',
          '188 AP20 entries, 5 native units, 2 mocked placements;',
          'candidate',info['sha256'], 'SOURCE ONLY, NO AMOS/WinUAE Compiler')


if __name__=='__main__':
    main()
