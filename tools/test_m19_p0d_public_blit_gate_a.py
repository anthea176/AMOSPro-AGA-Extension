#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d PUBLIC Bob Blit(I,X,Y) Gate A: AP20 V2 and REAL CPU020 bytes.

Execute the exact source-appended PUBLIC wrapper and P0c/P0d private path
in MC68020 Unicorn, two relocated placements, real P0c AGA Init/Close/End
native bytes but mocked Exec/graphics/Intuition/AMOS calls and DMA.

No AMOS Compiler executable, actual WinUAE DMA or installed library proof.
"""
from __future__ import annotations

from struct import pack,unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import DR,AR,AMOS,EXEC,STOP,STACK
from test_m19_p0a_r88_get_gate_a import ARGS
from test_m19_p0d_safe_bank_blit_native import DrawMachine,oracle
from m19_p0d_public_blit_emit import emit_public_blit
from m19_p0d_safe_bank_blit_emit import emit_safe_bank_blit
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0d_bob_blit_in_memory import (
    build as build_p0d, P0C_SHA,FIRST_NEW_STUB,NEW_BOBS,
)
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from compiler_relocation import unpack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from amos_link_test_support import relocate


class PublicBobMachine(DrawMachine):
    def __init__(self,binary,layout='interpreted',depth=8):
        super().__init__(binary,layout=layout,depth=depth)
        self.native,self.labels=emit_public_blit()
        self.uc.mem_write(self.entry,relocate(self.native,self.entry,{},self.uc))

    def blit(self,image=1,x=1,y=1,*,owner=AMOS,limit=12000000):
        for n,r in enumerate(DR):
            self.uc.reg_write(r,0x1210+n)
        for n,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+n*256)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[3],ARGS)
        self.uc.reg_write(DR[3],y&0xffffffff)
        self.put(ARGS,x)
        self.put(ARGS+4,image)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry+self.labels['public_bob_blit_entry'],
                              STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('M19 P0d PUBLIC Bob Blit CPU020 fault',
                str(exc),hex(self.uc.reg_read(UC_M68K_REG_PC)),
                image,x,y,owner,self.paint_blits[-5:],
                self.root(),self.nodes() if self.metadata else {})) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'AMOS stack imbalance'
        for r,v in old.items():
            if r in (DR[2],DR[3]):
                continue
            if r==AR[3]:
                assert self.uc.reg_read(r)==v+8,'GetP 3-arg consumption'
            else:
                assert self.uc.reg_read(r)==v,('public ABI clobbered',r)
        assert self.d(2)==0,'AMOS numeric result type'
        assert self.d(3) in (0,1)
        return self.d(3)


def ready(binary,layout,depth,*,two_banks=True):
    m=PublicBobMachine(binary,layout=layout,depth=depth)
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.run_get(2,20,6,56,9)==1
    assert m.run_get(3,6,3,36,10)==1
    assert m.mask(True,1,0)==1
    assert m.mask(True,2,(1<<depth)-1)==1
    if two_banks:
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.run_select(10)==1
    m.activate_aga_state()
    m.configure_real_state()
    assert m.root()==(0,0) and not m.chip_live,'no implicit stage in P0c'
    return m


def main():
    p0c,oldreport=build_p0c()
    new,report=build_p0d()
    tokens,parts,title=unpack_ap20(new)
    assert report['previous_sha']==P0C_SHA
    assert report['commands']==83 and len(parts)==93
    assert parts[NEW_BOBS].startswith(DISPATCH_V2)
    assert parts[92]==unpack_ap20(p0c)[1][91],'AGA unit modified'
    stub=parts[FIRST_NEW_STUB]
    assert stub[:2]==RBSR and len(stub)==8 and stub[6:8]==bytes.fromhex('4e75')
    assert unpack_from('>HH',stub,2)==(NEW_BOBS,report['entry'])
    assert parts[87].endswith(GETP),'new three-argument GetP missing'
    old_native,_=emit_safe_bank_blit()
    native,labels=emit_public_blit()
    assert native.startswith(old_native)
    suffix=native[labels['public_bob_blit_entry']:]
    assert suffix
    decode=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
                disasm(suffix,0x10000))
    assert sum(i.size for i in decode)==len(suffix),'CPU020 decode incomplete'
    assert parts[NEW_BOBS].endswith(native)
    assert report['entry']==len(parts[NEW_BOBS])-len(DISPATCH_V2)-len(suffix)
    assert all(len(p)<=65534 for p in parts)
    cases=0

    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m=ready(p0c,layout,depth)
            bank=parse_payload(m.bank_payload(10))
            assert m.chip_allocs==0 and not m.metadata
            first=bank.image(1)
            before=m.read_back()
            assert m.blit(1,7,8)==1
            assert m.read_back()==oracle(before,first,7,8)
            assert m.chip_allocs==1 and m.metadata_allocs==1
            assert len(m.nodes())==1
            assert m.get(AMOS+0x1cc)==m.entry+m.labels['program_end_bridge_entry']
            assert m.get(AMOS+0x1d0)==m.entry+m.labels['program_end_bridge_entry']
            cases+=1

            for image,x,y in ((1,5,4),(2,40,6),(3,-4,8),
                              (1,64,3),(3,9,-4)):
                before=m.read_back()
                count=m.chip_allocs
                assert m.blit(image,x,y)==1
                assert m.read_back()==oracle(before,bank.image(image),x,y)
                assert m.chip_allocs==count,'staging repeated per-frame'
                assert m.get(0x53000+8)==0,'implicit screen swap'
                cases+=1

            # Non-selected bank must be rejected until Aga Bob Bank chooses it.
            assert m.blit(0,1,2)==0
            assert m.blit(4097,1,2)==0
            assert m.blit(1,32768,2)==0
            assert m.blit(1,1,-32769)==0
            cases+=4

            assert m.run_select(11)==1
            before=m.read_back()
            assert m.blit(1,10,11)==1
            bank11=parse_payload(m.bank_payload(11))
            assert m.read_back()==oracle(before,bank11.image(1),10,11)
            assert set(m.nodes())=={10,11}
            cases+=1

            # A change to the official bank (e.g. a new independent mask)
            # invalidates the old staged identity and forces ONE restage.
            assert m.run_select(10)==1
            m.mask(True,1,(1<<depth)-1)
            newbank=parse_payload(m.bank_payload(10))
            copies=m.chip_copies
            oldptr=m.nodes()[10][1][0]
            before=m.read_back()
            assert m.blit(1,2,8)==1
            assert m.chip_copies==copies+1
            assert m.nodes()[10][1][0]!=oldptr
            assert m.read_back()==oracle(before,newbank.image(1),2,8)
            cases+=1

            # Safe pending without GetMsg refuses before any DMA or Swap.
            m.safe=False
            m.put(0x53000+12,0x5b000)
            m.put(0x53000+20,3)
            before=m.read_back()
            old_events=list(m.paint_blits)
            assert m.blit(1,1,1)==0
            assert m.read_back()==before and m.paint_blits==old_events
            assert m.get(0x53000+20)==3
            cases+=1
            m.safe=True
            m.put(0x53000+20,0)

            # Close cleans ALL Chip contexts, no malloc leaks or stale pointers.
            m.invoke('bridge')
            assert not m.chip_live and not m.metadata and m.root()==(0,0)
            assert m.get(m.real_state)==0
            cases+=1

            # Third-party End callback cannot be silently overwritten.
            m=ready(p0c,layout,depth,two_banks=False)
            m.put(AMOS+0x1cc,0x123456)
            m.put(AMOS+0x1d0,0x123456)
            before=m.read_back()
            assert m.blit(1,7,8)==0
            assert not m.chip_live and not m.metadata
            assert m.read_back()==before
            assert (m.get(AMOS+0x1cc),m.get(AMOS+0x1d0))==(0x123456,0x123456)
            cases+=1

            # A selected but still empty bank is valid: do not allocate
            # or access absent images; first actual capture enables staging.
            m=PublicBobMachine(p0c,layout,depth)
            assert m.run_select(10)==1
            m.activate_aga_state()
            m.configure_real_state()
            assert m.blit(1,1,1)==0
            assert not m.chip_live and not m.metadata
            cases+=1

            # Reject before any bank mutation when CPU lacks AFF_68020.
            m=ready(p0c,layout,depth,two_banks=False)
            m.uc.mem_write(EXEC+0x128,bytes.fromhex('0000'))
            assert m.blit(1,1,1)==0
            assert not m.chip_live and not m.metadata
            cases+=1

    print('M19 P0d PUBLIC Bob Blit MC68020 AP20/ABI GATE A PASS:',
          len(new),'candidate bytes, SHA256',report['sha256'],
          'public native bytes',len(suffix),'cases',cases,
          'AMOS/Exec/Gfx/Intuition mocked; NOT WinUAE/real Compiler')


if __name__=='__main__':
    main()
