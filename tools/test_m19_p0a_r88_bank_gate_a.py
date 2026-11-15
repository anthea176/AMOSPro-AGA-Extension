#!/usr/bin/env python3
"""R88-derived M19 P0a: MC68020-only Unicorn bank-selection Gate A.

Tests private native Bank Select + embedded 365 list transaction. Main AMOS
service effects are MOCKS, both interpreter and compiled-style relocated native
layouts are exercised. This is NOT AMOS Runtime / Compiler / WinUAE validation.
"""
from __future__ import annotations

from struct import pack
from unittest.mock import patch
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR,UC_CPU_M68K_M68020
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020

from test_m5_generic import Machine,DR,AR,AMOS,EXEC,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from build_m19_p0a_r88_bank_in_memory import build
from compiler_relocation import unpack_ap20
from m19_p0a_bank_select_emit import emit_bank_select
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0a_multi_bob_abk import empty_bank,parse_payload

ENTRY=0x180000
COMPILED=0x1a0000
HEAD=0x59800
NEW_FIRST=0xb00000
NAMES=('Bnk.GetAdr','Lst.Cree','Lst.Del','Bnk.Change')

class SelectMachine(Machine):
    def __init__(self,lib,layout='interpreted',occupied=None,
                 alloc_fail=False,foreign=False):
        # The test framework defaults to M68000; this experiment must NEVER
        # run a Gate A in CPU000 mode. R88's own P2.8 tests use this patch.
        with patch('test_m5_generic.UC_CPU_M68K_M68000',UC_CPU_M68K_M68020):
            super().__init__(lib,None)
        self.uc.mem_write(EXEC+0x128,b'\x00\x02') # AFF_68020
        t,n=main_table(self.uc)
        self.targets={t[i]:name for i,name,*_ in declarations() if name in NAMES}
        assert set(self.targets.values())==set(NAMES)
        self.entry=ENTRY if layout=='interpreted' else COMPILED
        self.unit,self.labels=emit_bank_select()
        self.uc.mem_write(self.entry,relocate(self.unit,self.entry,{},self.uc))
        self.uc.hook_add(UC_HOOK_CODE,self.service,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        for address in self.targets:
            self.uc.mem_write(address,b'\x4e\x75')
        self.put(AMOS+CUR_BANKS_A5,HEAD)
        self.put(HEAD,0)
        self.heap_next=NEW_FIRST
        self.calls=[]
        self.alive=set()
        self.notifications=0
        self.allocations=0
        self.frees=0
        self.alloc_fail=alloc_fail
        self.foreign=foreign
        self.last_created=0
        if occupied is not None:
            self.install_bank(occupied,foreign=foreign)

    def install_bank(self,n,*,foreign=False):
        payload=(b'AGPC'+bytes(28)) if foreign else empty_bank()
        node=self.heap_next
        self.heap_next+=0x1000
        self.put(node,self.get(HEAD))
        self.put(node+4,16+len(payload))
        self.put(node+8,n)
        self.uc.mem_write(node+12,b'\0\x01\0\0')
        self.uc.mem_write(node+16,b'AGAPIC  ' if foreign else b'AGABOBS ')
        self.uc.mem_write(node+24,payload)
        self.put(HEAD,node)
        self.alive.add(node)
        return node

    def find(self,num):
        node=self.get(HEAD)
        seen=set()
        while node:
            assert node not in seen,'list cycle'
            seen.add(node)
            if self.get(node+8)==num:
                return node
            node=self.get(node)
        return 0

    def _rts(self):
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def service(self,uc,address,size,user):
        if address not in self.targets:
            return
        name=self.targets[address]
        self.calls.append(name)
        assert self.a(5)==AMOS,'AMOS A5 corrupted'
        if name=='Bnk.GetAdr':
            node=self.find(self.d(0))
            ptr=node+24 if node else 0
            self.uc.reg_write(AR[0],ptr)
            self.uc.reg_write(AR[1],ptr)
            self.uc.reg_write(DR[0],self.get(node+12)&0xffff if node else 0)
            self.uc.reg_write(DR[1],0xdeadbeef)
        elif name=='Lst.Cree':
            self.allocations+=1
            requested=self.d(0)
            headptr=self.a(0)
            assert requested>=16 and requested<=0x1000010
            assert self.d(1)==0x00010001
            if self.alloc_fail:
                self.uc.reg_write(DR[0],0)
                self.uc.reg_write(AR[1],0)
            else:
                node=self.heap_next
                self.heap_next+=(requested+8+15)&~15
                self.uc.mem_write(node,bytes(requested+8))
                self.put(node,self.get(headptr))
                self.put(node+4,requested)
                self.put(headptr,node)
                self.alive.add(node)
                self.last_created=node
                self.uc.reg_write(DR[0],node)
                self.uc.reg_write(AR[1],node)
        elif name=='Bnk.Change':
            self.notifications+=1
            # The selected list is already updated before callbacks begin.
            assert self.find(10)!=0 or self.find(11)!=0
            # The real Bnk.Change preserves all registers, including D3.
        elif name=='Lst.Del':
            self.frees+=1
            head=self.a(0)
            node=self.a(1)
            assert node in self.alive
            cur=head
            for _ in range(65536):
                nxt=self.get(cur)
                if nxt==node:
                    self.put(cur,self.get(node))
                    self.alive.remove(node)
                    break
                assert nxt!=0,'Lst.Del called with foreign pointer'
                cur=nxt
            else:
                raise AssertionError('Lst.Del list loop')
        self._rts()

    def run_select(self,n):
        for i,r in enumerate(DR):
            self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):
            self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],0x58000)
        self.uc.reg_write(DR[3],n&0xffffffff)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:
            self.uc.emu_start(self.entry,STOP,count=350000)
        except Exception as exc:
            raise AssertionError(('68020 Bank Select exception',str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),n,self.calls)) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,'stack leak'
        for reg,value in before.items():
            if reg not in (DR[2],DR[3]):
                assert self.uc.reg_read(reg)==value,('register ABI',reg)
        assert self.d(2)==0,'AMOS integer result type'
        assert self.d(3) in (0,1)
        return self.d(3)


def main():
    binary,meta=build()
    assert build()[0]==binary,'nondeterministic AP20'
    assert meta['commands']==79 and meta['ap20_entries']==89
    tokens,entries,title=unpack_ap20(binary)
    raw,labels=emit_bank_select()
    assert entries[87].endswith(raw),'public stub not routed into BOBS native unit'
    assert len(raw)==len(emit_bank_select()[0])
    # capstone must consume the executable region before the state/dataset.
    m=SelectMachine(binary)
    patched=relocate(raw,ENTRY,{},m.uc)
    executable=patched[:labels['active_state']]
    diss=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
              .disasm(executable,ENTRY))
    assert sum(i.size for i in diss)==len(executable),'invalid native 68020 instruction'
    count=0
    for layout in ('interpreted','compiled'):
        m=SelectMachine(binary,layout=layout)
        assert m.run_select(10)==1
        node=m.find(10)
        assert node!=0
        payload=bytes(m.uc.mem_read(node+24,32))
        assert payload==empty_bank()
        assert parse_payload(payload).images==()
        assert m.get(m.entry+labels['active_state'])==10
        assert m.get(m.entry+labels['active_state']+4)==node+24
        assert m.get(m.entry+labels['active_state']+8)==HEAD
        assert m.allocations==1 and m.notifications==1
        assert m.run_select(10)==1
        assert m.find(10)==node and m.allocations==1
        count+=2
        for n in (0,1,4,65536,-1):
            m=SelectMachine(binary,layout=layout)
            assert m.run_select(n)==0
            assert m.allocations==m.notifications==0
            count+=1
        m=SelectMachine(binary,layout=layout,alloc_fail=True)
        assert m.run_select(10)==0
        assert m.find(10)==0
        assert m.notifications==0
        count+=1
        m=SelectMachine(binary,layout=layout,occupied=11,foreign=True)
        old=m.find(11)
        assert m.run_select(11)==0
        assert m.find(11)==old and m.allocations==0
        count+=1
        m=SelectMachine(binary,layout=layout,occupied=11,foreign=False)
        old=m.find(11)
        assert m.run_select(11)==1
        assert m.find(11)==old and m.allocations==0
        count+=1
        m=SelectMachine(binary,layout=layout)
        m.uc.mem_write(EXEC+0x128,b'\x00\x00')
        assert m.run_select(10)==0 # simulated pre-020 feature flag
        assert m.allocations==m.notifications==0
        count+=1
    print('M19 P0a R88 native 68020 Gate A:',count,
          'CPU cases, two separately relocated layouts,',
          '79 AP20 commands, no dist writes, SHA256',meta['sha256'])


if __name__=='__main__':
    main()
