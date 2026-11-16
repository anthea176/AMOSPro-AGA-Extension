#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0e source-only reset objects BEFORE original P0d AGA Screen Close.

Exec/graphics/Intuition mocked; REAL source native Screen Close is reached
and the AGA object table is zero before old Close runs. No End callback
test, WinUAE or real AMOS Compiler claim.
"""
from __future__ import annotations

from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from build_m19_p0e_split_close_in_memory import build as build_close
from m19_p0e_split_close_emit import emit_split_with_close
from m19_p0e_split_bridge_emit import emit_split_bobs_public
from test_m19_p0e_split_bridge_gate_a import SplitMachine
from compiler_relocation import unpack_ap20,RBSR
from amos_link_test_support import relocate


class CloseSplitMachine(SplitMachine):
    def __init__(self,p0c,layout='interpreted'):
        super().__init__(p0c,layout)
        self.public_native,self.labels=emit_split_with_close()
        self.uc.mem_write(self.entry,relocate(self.public_native,self.entry,{},self.uc))
        self.table_at_old_close=None
        self.close_calls=0
        from unicorn import UC_HOOK_CODE
        self.uc.hook_add(UC_HOOK_CODE,self._at_native_close,
                         begin=self.old_close,end=self.old_close)

    def _at_native_close(self,uc,address,size,user):
        self.close_calls+=1
        self.table_at_old_close=self.table()

    def close(self,limit=5000000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x12340000+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x41000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry+self.labels['public_aga_p0e_close_entry'],
                              STOP,count=limit)
        except Exception as exc:
            raise AssertionError(('M19 P0e actual original native Close fault',
                hex(self.uc.reg_read(UC_M68K_REG_PC)),exc,self.close_calls,
                self.events[-16:])) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for r,v in before.items():
            assert self.uc.reg_read(r)==v,('AMOS instruction Close ABI clobber',r)
        return self.close_calls


def main():
    lib,_=build_p0c()
    candidate,report=build_close()
    _,segments,_=unpack_ap20(candidate)
    assert len(segments)==95 and segments[8][:2]==RBSR
    assert report['close_entry']>report['previous_stub']
    assert report['pc16_margin']>=64
    old,_=emit_split_bobs_public()
    code,labels=emit_split_with_close()
    assert code.startswith(old)
    asm=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
             .disasm(code[len(old):],0x10000))
    assert sum(x.size for x in asm)==len(code)-len(old)
    cases=0
    for layout in ('interpreted','compiled'):
        m=CloseSplitMachine(lib,layout)
        assert m.run_select(10)==1
        assert m.run_get(1,4,5,20,8)==1
        m.activate_aga_state() # true source-verified AGA initialization
        assert m.public('bob',ident=1,image=1)==1
        assert m.public('bob',ident=2,image=1,x=15,y=29)==1
        assert m.table()!=bytes(len(m.table()))
        assert m.close()==1
        assert m.table_at_old_close==(
            m.table_at_old_close[:4]+bytes(len(m.table_at_old_close)-4))
        assert m.get(m.real_state)==0,'legacy AGA Close screen pointer not cleared'
        assert m.table()==m.table_at_old_close
        assert 'real_aga_close_entry' in m.events
        cases+=5

        # Bad CPU and invalid native AGA anchor do NOT delete objects or
        # invoke the destructive old Close. Reset must be atomic.
        e=CloseSplitMachine(lib,layout)
        assert e.run_select(10)==1
        assert e.run_get(1,4,5,20,8)==1
        e.activate_aga_state()
        assert e.public('bob',ident=1)==1
        snapshot=e.table()
        e.uc.mem_write(EXEC+0x128,b'\0\0')
        assert e.close()==0 and e.table()==snapshot
        e.uc.mem_write(EXEC+0x128,b'\0\x02')
        e.reject_type=e.real_state
        assert e.close()==0 and e.table()==snapshot
        e.reject_type=None
        assert e.close()==1
        assert e.table()!=snapshot
        cases+=3
    print('M19 P0e SPLIT PUBLIC CLOSE OBJECT RESET CPU020 GATE A PASS',
          cases,'cases in two disjoint native layouts; real AGA Close called;',
          'OS mocked; End callback and WinUAE gates not tested')


if __name__=='__main__':
    main()
