#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Exercise the temporary diagnostic through the real AP20 public stub."""
import argparse, json, os, unittest
from pathlib import Path
from build_m19_s1p2l_b_in_memory import build_s1p2lb, DIAG_ARGUMENT, protected
from test_m19_s1p2l_a_gate_a import ObserveMachine, observer_cases, reserve_cases
from test_m19_s1p2k_gate_a import TransactionMachine, transactions
from test_m19_s1p2i_gate_a import CI, TASK, STATE
import test_m19_s1p2j_gate_a as p2j
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

def signed(value):
    return value-(1<<32) if value&0x80000000 else value

def route_cases(image,info):
    count=0
    for layout in ('runtime','compiled'):
        def new(db=True):
            m=ObserveMachine(image,info,layout,db)
            assert m.select(29)==1
            return m
        def diagnostic(m,expected):
            before=(list(m.temp_allocs),list(m.temp_frees),list(m.sprite_calls),
                    m.get(m.cell),m.get(STATE),m.named)
            result=signed(m.bankfree(DIAG_ARGUMENT))
            assert result==expected,(layout,expected,result)
            assert before==(m.temp_allocs,m.temp_frees,m.sprite_calls,
                            m.get(m.cell),m.get(STATE),m.named)
        m=new()
        # A normal invalid argument remains a normal failure.
        assert m.bankfree(DIAG_ARGUMENT-1)==0
        diagnostic(m,-131);count+=1
        assert not m.named and m.opens==0
        assert m.sprite()==1
        diagnostic(m,-180);count+=1
        # Diagnostic before Off/Close must not alter the active image or channels.
        assert m.sprite(x=34)==1
        m.erase()
        m.closed()
        a=m.named;rec=m.get(a+56);chip=m.get(rec)
        def retained(expected):
            prev=(m.read(a,112),m.read(rec,40),m.read(chip,192))
            opens,closes=m.opens,m.closes
            diagnostic(m,expected)
            assert prev==(m.read(a,112),m.read(rec,40),m.read(chip,192))
            assert m.opens-opens==m.closes-closes+int(m.fail_gfx_open)
        retained(-190);count+=1
        retained(-190);count+=1
        m.fail_gfx_open=True
        retained(-184);count+=1
        m.fail_gfx_open=False
        m.copper(2,chip+48)
        retained(-187);count+=1
        m.copper(2,CI+176)
        m.after_tof=lambda: m.copper(5,chip+48)
        retained(-187);count+=1
        m.copper(5,CI+176)
        retained(-190);count+=1
        # Positive Bank Free retains its exact boolean behavior and never
        # silently converts observation into a DMA-free result.
        assert m.bankfree(29)==0 and m.bankfree(28)==0
        assert m.bankfree(DIAG_ARGUMENT-1)==0
        m.held();count+=1
        m.expect_busy=True
        m.put32(a+72,TASK);m.put32(a+40,TASK)
        m.put16(a+14,1);m.put16(a+44,0)
        retained(-136);count+=1
    print('S1P2LB_PUBLIC_DIAG_CPU_PASS',count,flush=True)
    assert count==20

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s1p2lb(a.vasm)
    print('S1P2LB_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    route_cases(image,info)
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
    print('S1P2LB_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
