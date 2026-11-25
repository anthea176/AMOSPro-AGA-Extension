#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2k exact candidate; actual MC68020 instructions, OS is mocked."""
import argparse, os, json, unittest
from pathlib import Path
from unicorn.m68k_const import *
from build_m19_s1p2k_in_memory import build_s1p2k
import test_m19_s1p2j_gate_a as p2j
from test_m19_s1p2j_gate_a import ProbeMachine, STATE, SAFE, DISP, WINPORT, EXEC
from test_m19_s1p2i_gate_a import TASK
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases,verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

class TransactionMachine(ProbeMachine):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.expect_busy=False
        self.block_replies=False
        self.fail_attempt=False
    def unlocked(self):
        if self.named:
            assert self.get(self.named+72)==0,'transaction borrower leaked'
            assert self.get(self.named+40)==0,'Exec owner leaked'
    def invoke_any(self,*args,**kwargs):
        result=super().invoke_any(*args,**kwargs)
        if not self.expect_busy:
            self.unlocked()
        return result
    def on_code(self,uc,address,size,user):
        a0=uc.reg_read(UC_M68K_REG_A0)
        if address==EXEC-576 and self.fail_attempt:
            assert self.depth==1
            self.volatile(uc,0)
            return
        if address==EXEC-372 and self.block_replies and a0 in (SAFE,DISP,WINPORT):
            self.volatile(uc,0)
            return
        return super().on_code(uc,address,size,user)

def transactions(image,info):
    count=0
    for layout in ('runtime','compiled'):
        def new(db=True):
            m=TransactionMachine(image,info,layout,db)
            assert m.select(29)==1
            return m
        for end in (False,True):
            m=new()
            assert m.sprite()==1
            assert m.get(m.named+104)==TASK
            m.block_replies=True
            m.close(end)
            assert m.get(STATE)!=0 and m.get(m.cell)!=0
            m.held()
            m.unlocked()
            m.block_replies=False
            m.closed(end)
            assert m.get(m.named+104)==0
            count+=1
        # An unfinished transaction is never stolen (same or other Task).
        m=new(False);assert m.sprite()==1
        a=m.named;m.expect_busy=True
        m.put32(a+72,TASK);m.put32(a+40,TASK)
        m.put16(a+14,1);m.put16(a+44,0)
        assert m.sprite(x=34)==-136
        assert m.off()==0
        m.close();assert m.get(STATE)!=0
        assert m.get(a+72)==TASK and m.get(a+40)==TASK
        # Simulator explicitly restores an abandoned transaction only
        # to exercise subsequent branches; production never clears it.
        m.put32(a+72,0);m.put32(a+40,0)
        m.put16(a+14,0);m.put16(a+44,65535)
        m.expect_busy=False
        m.fail_attempt=True
        assert m.sprite(x=34)==-132
        m.close();assert m.get(STATE)!=0
        m.fail_attempt=False
        assert m.sprite(x=34)==1
        # A different Task cannot operate on the lifetime-owned record.
        m.task=TASK+0x100
        assert m.sprite(x=36)==-139 and m.off()==0
        m.close();assert m.get(STATE)!=0
        m.task=TASK;m.closed();count+=1
        # Recreated code-local cell must not create a second DMA block.
        m=new(False);assert m.sprite()==1;m.closed()
        a=m.named;before=len(m.temp_allocs)
        m.put32(STATE,0x0)  # closed state remains closed
        assert m.get(m.cell)==0 and m.get(a+104)==0
        # The inherited suite checks reopening after a successful close.
        # Legacy schema remains incompatible at the same registry name.
        m.put32(a+52,0x00010070)
        assert m.bankfree()==0 and m.named==a
        assert len(m.temp_allocs)==before
        count+=1
    print('S1P2K_TRANSACTION_CPU_PASS',count,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    image,info=build_s1p2k(a.vasm)
    print('S1P2K_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    p2j.ProbeMachine=TransactionMachine
    assert p2j.suite(image,info)==54
    transactions(image,info)
    chain(image)
    prior,meta=build_l2(a.vasm)
    good=(p2j.ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    verify_linked_source(a.vasm,good)
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,info)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    print('S1P2K_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
