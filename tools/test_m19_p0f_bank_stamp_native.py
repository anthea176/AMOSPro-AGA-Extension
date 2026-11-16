#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0f AGBO bank stamp CPU020 Gate A in two disjoint native placements.

Exec TypeOfMem and the AMOS 365 Bnk.GetAdr service are mocked, but actual
emitted 020 instructions execute under Unicorn. CaptureMachine's real Get
source creates AGBO payloads; stamps NEVER select/create/allocate a bank.
No public Draw, actual AMOS Compiler, WinUAE or physical hardware claim.
"""
from __future__ import annotations

from struct import pack,unpack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR

from test_m5_generic import DR,AR,AMOS,EXEC,STACK,STOP
from test_m19_p0a_r88_bank_gate_a import HEAD
from test_m19_p0a_r88_get_gate_a import CaptureMachine
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from m19_p0f_bank_stamp_emit import emit_bank_stamp
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from amos_link_test_support import relocate

OUTPUT=0x5c000
SENTINEL=bytes.fromhex('aabbddeeffaacc1122334566deadbeef')


class StampMachine(CaptureMachine):
    def __init__(self,source,layout='interpreted'):
        super().__init__(source,layout,depth=8)
        self.code,self.stamp_labels=emit_bank_stamp()
        self.stamp_base=0x340000 if layout=='interpreted' else 0x470000
        self.relocated=relocate(self.code,self.stamp_base,{},self.uc)
        self.uc.mem_write(self.stamp_base,self.relocated)

    def stamp(self,kind,bank=10,*,output=OUTPUT,data=None,owner=AMOS,
              limit=1000000):
        assert kind in ('capture','verify')
        self.uc.mem_write(OUTPUT,SENTINEL if data is None else data)
        for n,r in enumerate(DR):self.uc.reg_write(r,0x127000+n)
        for n,r in enumerate(AR[:7]):self.uc.reg_write(r,0x43000+n*0x100)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(AR[1],output)
        self.uc.reg_write(DR[0],bank&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(
                self.stamp_base+self.stamp_labels['stamp_'+kind+'_entry'],
                STOP,count=limit)
        except Exception as error:
            raise AssertionError(('M19 P0f native stamp CPU020 failure',
                kind,bank,hex(self.uc.reg_read(UC_M68K_REG_PC)),
                str(error),self.calls[-5:])) from error
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        for reg,old in saved.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==old,('native stamp AMOS ABI',reg)
        assert self.d(2)==0 and self.d(3) in (0,1)
        return self.d(3),bytes(self.uc.mem_read(OUTPUT,16))


def main():
    lib,_=build_p0c()
    raw,labels=emit_bank_stamp()
    assert raw==emit_bank_stamp()[0]
    cases=0
    for layout in ('interpreted','compiled'):
        m=StampMachine(lib,layout)
        instructions=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
                          disasm(m.relocated,m.stamp_base))
        assert sum(x.size for x in instructions)==len(m.relocated)
        assert all(not x.mnemonic.startswith('dc.') for x in instructions)
        # Empty AGBO is an existing bank but not a valid persistent image.
        assert m.run_select(10)==1
        status,out=m.stamp('capture')
        assert status==0 and out==SENTINEL
        cases+=1
        assert m.run_get(1,4,5,20,8)==1
        node=m.find(10)
        assert node!=0
        status,stamp=m.stamp('capture')
        assert status==1 and unpack('>4I',stamp)==(
            node+24,m.get(node+24+24),HEAD,len(m.bank_payload(10)))
        assert m.stamp('verify',data=stamp)==(1,stamp)
        cases+=2
        # Unlike the old checked_lookup, stamp validation of bank 10 is
        # independent of the CURRENTLY selected bank 11.
        assert m.run_select(11)==1
        assert m.run_get(1,7,8,16,15)==1
        assert m.stamp('verify',bank=10,data=stamp)==(1,stamp)
        assert m.stamp('verify',bank=11,data=stamp)==(0,stamp)
        assert m.stamp('verify',bank=12,data=stamp)==(0,stamp)
        cases+=3

        # A changed generation is rejected without writing to caller data.
        generation=m.get(node+24+24)
        m.put(node+24+24,generation+1)
        assert m.stamp('verify',data=stamp)==(0,stamp)
        m.put(node+24+24,generation)
        assert m.stamp('verify',data=stamp)==(1,stamp)
        cases+=2
        # A changed payload size is also a different bank identity.
        old_size=m.get(node+4)
        m.put(node+4,old_size+4)
        assert m.stamp('verify',data=stamp)==(0,stamp)
        m.put(node+4,old_size)
        cases+=1
        # Changing AMOS Cur_Banks list, even with the same data address,
        # must invalidate old objects; do not trust a selected-bank shadow.
        m.put(AMOS+CUR_BANKS_A5,HEAD+4)
        assert m.stamp('verify',data=stamp)==(0,stamp)
        m.put(AMOS+CUR_BANKS_A5,HEAD)
        cases+=1
        # The head loses bank 10 after Erase (no implicit Reserve/Load).
        old_head=m.get(HEAD)
        m.put(HEAD,0)
        assert m.stamp('verify',data=stamp)==(0,stamp)
        assert m.stamp('capture')[0]==0
        m.put(HEAD,old_head)
        cases+=2

        # A real Get on the SAME bank replaces the AMOS bank allocation.
        assert m.run_select(10)==1
        assert m.run_get(1,8,8,22,12)==1
        assert m.find(10)!=node
        assert m.stamp('verify',data=stamp)==(0,stamp)
        status,fresh=m.stamp('capture')
        assert status==1 and fresh!=stamp
        assert m.stamp('verify',data=fresh)==(1,fresh)
        cases+=3

        for bank in (0,4,65536,0xffffffff):
            assert m.stamp('capture',bank=bank)==(0,SENTINEL)
            cases+=1
        assert m.stamp('capture',output=0)==(0,SENTINEL)
        assert m.stamp('capture',output=OUTPUT+1)==(0,SENTINEL)
        cases+=2
        m.uc.mem_write(EXEC+0x128,b'\0\0')
        assert m.stamp('capture')==(0,SENTINEL)
        assert m.stamp('verify',data=fresh)==(0,fresh)
        m.uc.mem_write(EXEC+0x128,b'\0\x02')
        cases+=2
        assert m.stamp('capture',owner=0)==(0,SENTINEL)
        assert m.stamp('capture',owner=3)==(0,SENTINEL)
        cases+=2
    print('M19 P0f PRIVATE MC68020 AGBO BANK STAMP GATE A PASS',
          cases,'cases; live AMOS Bnk.GetAdr, generation, ptr/size/head;',
          '2 disjoint layouts; no bank switch, OS mocked, NO public Draw')


if __name__=='__main__':
    main()
