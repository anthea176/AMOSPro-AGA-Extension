#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Private observer and 16 KiB AP20 growth: CPU/OS model only, never DMA proof."""
import argparse, json, os, unittest
from pathlib import Path
from struct import pack
from unicorn.m68k_const import *
from build_m19_s1p2l_a_in_memory import build_s1p2la, expanded, protected
from compiler_relocation import unpack_ap20, repack_ap20
import test_m19_s1p2j_gate_a as p2j
from test_m19_s1p2k_gate_a import TransactionMachine, transactions
from test_m19_s1p2i_gate_a import CI, TASK, STATE
from test_m19_s1p1c_amos_bank_commit import CODE, STOP, STACK, REGS, EXEC
from test_m19_s1p1c_pipeline import GFX
from test_m19_s1p2j_gate_a import FAST_TABLE
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

class ObserveMachine(TransactionMachine):
    def __init__(self,image,info,layout,db=False):
        super().__init__(image,info,layout,db)
        self.probe_pc=CODE+info['probe_offset']
        self.fail_gfx_open=False
        self.after_tof=None
        self.opens=0
        self.closes=0
    def on_code(self,uc,address,size,user):
        if address==EXEC-552:
            self.opens+=1
            if self.fail_gfx_open:
                self.volatile(uc,0)
                return
        if address==EXEC-414 and uc.reg_read(UC_M68K_REG_A1)==GFX:
            self.closes+=1
        super().on_code(uc,address,size,user)
        if address==GFX-270 and self.after_tof is not None:
            fn,self.after_tof=self.after_tof,None
            fn()
    def observe(self):
        uc=self.uc
        regs=tuple(r for r in REGS if r not in (UC_M68K_REG_D0,UC_M68K_REG_D1))+(UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_A3)
        for i,r in enumerate(regs):uc.reg_write(r,0x55007000+i)
        saved={r:uc.reg_read(r) for r in regs}
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        before=(list(self.temp_allocs),list(self.temp_frees),list(self.sprite_calls))
        uc.emu_start(self.probe_pc,STOP,count=2000000)
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items())
        assert self.depth==0
        if not self.expect_busy:self.unlocked()
        assert before==(self.temp_allocs,self.temp_frees,self.sprite_calls)
        value=uc.reg_read(UC_M68K_REG_D0)
        return value-(1<<32) if value&0x80000000 else value

def observer_cases(image,info,idle=(-185,-185,-185)):
    count=0
    for layout in ('runtime','compiled'):
        def new():
            m=ObserveMachine(image,info,layout)
            assert m.select(29)==1
            return m
        m=new()
        assert m.observe()==-131 and m.opens==0 and not m.named;count+=1
        assert m.sprite()==1
        assert m.observe()==-180 and m.opens==0;count+=1
        m.closed()
        a=m.named;rec=m.get(a+56);chip=m.get(rec)
        assert m.get(a+68)==0 and m.get(a+104)==0
        def check(expected):
            anchor=m.read(a,112);record=m.read(rec,40);block=m.read(chip,192)
            prev_o,prev_c=m.opens,m.closes
            assert m.observe()==expected,('observer result',expected)
            assert m.read(a,112)==anchor and m.read(rec,40)==record and m.read(chip,192)==block
            assert m.opens-prev_o==m.closes-prev_c+int(m.fail_gfx_open)
        check(1);count+=1
        m.fail_gfx_open=True;check(-184);m.fail_gfx_open=False;count+=1
        cases=[
            (a+68,4,-180),(rec+12,5,-182),(rec+4,71,-183),
            (GFX+34,1,idle[0]),(GFX+50,CI+160,idle[1]),
            (CI+164,0,idle[2]),(GFX+208,0,-186),
            (FAST_TABLE+8,chip,-187),(FAST_TABLE+16,rec+8,-187),
            (FAST_TABLE+28,chip+191,-187),
        ]
        for addr,value,expected in cases:
            old=m.get(addr);m.put32(addr,value)
            check(expected);m.put32(addr,old);count+=1
        mask=m.read(GFX+166,1)
        m.uc.mem_write(GFX+166,bytes([mask[0]|4]))
        check(-187);m.uc.mem_write(GFX+166,mask);count+=1
        op=m.read(CI+88,2);m.put16(CI+88,0x124)
        check(-186);m.uc.mem_write(CI+88,op);count+=1
        m.copper(2,chip+48);check(-187);m.copper(2,CI+176);count+=1
        m.copper(5,chip+191);check(-187);m.copper(5,CI+176);count+=1
        m.after_tof=lambda: m.copper(5,chip+48)
        check(-187);m.copper(5,CI+176);count+=1
        # Valid after the transient refusal; still no freeing.
        check(1);count+=1
        m.expect_busy=True
        m.put32(a+72,TASK);m.put32(a+40,TASK)
        m.put16(a+14,1);m.put16(a+44,0)
        check(-136);count+=1
    print('S1P2LA_OBSERVATION_CPU_PASS',count,flush=True)

def reserve_cases(image,info):
    tok,parts,title=unpack_ap20(image)
    bigger=expanded(parts,info['reserve_bytes'])
    probe=repack_ap20(image,tok,bigger,title)
    assert unpack_ap20(probe)==(tok,bigger,title)
    for layout in ('runtime','compiled'):
        m=ObserveMachine(probe,info,layout)
        assert m.select(29)==1 and m.sprite()==1
        m.erase()
        for x in range(34,234,2):assert m.sprite(x=x)==1
        assert len(m.moves)==101
        m.closed()
        assert m.observe()==1
    print('S1P2LA_RESERVE_CPU_PASS',info['reserve_bytes'],2,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s1p2la(a.vasm)
    print('S1P2LA_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    p2j.ProbeMachine=TransactionMachine
    assert p2j.suite(image,info)==54
    transactions(image,info)
    observer_cases(image,info)
    reserve_cases(image,info)
    chain(image)
    prior,meta=build_l2(a.vasm)
    verify_linked_source(a.vasm,before[1])
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,info)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    assert protected()==before
    print('S1P2LA_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
