#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2l-c read-only idle detail via true AP20 route, both MC68020 models."""
import argparse, json, os, unittest
from pathlib import Path
from build_m19_s1p2l_c_in_memory import build_s1p2lc, protected
from build_m19_s1p2l_b_in_memory import DIAG_ARGUMENT
from test_m19_s1p2l_b_gate_a import route_cases, signed
from test_m19_s1p1c_pipeline import GFX
from test_m19_s1p2l_a_gate_a import ObserveMachine, observer_cases, reserve_cases
from test_m19_s1p2k_gate_a import TransactionMachine, transactions
from test_m19_s1p2i_gate_a import CI, TASK, STATE
import test_m19_s1p2j_gate_a as p2j
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

def idle_cases(image,info):
    count=0
    for layout in ('runtime','compiled'):
        m=ObserveMachine(image,info,layout,True)
        assert m.select(29)==1 and m.sprite()==1
        m.erase()
        m.closed()
        a=m.named;rec=m.get(a+56);chip=m.get(rec)
        baseline={p:m.get(p) for p in (GFX+34,GFX+38,GFX+50,GFX+54,CI+164)}
        assert baseline=={GFX+34:0,GFX+38:CI,GFX+50:CI+164,GFX+54:CI+164,CI+164:0xfffffffe}
        def restore():
            for addr,value in baseline.items():m.put32(addr,value)
        def check(expected):
            before=(m.read(a,112),m.read(rec,40),m.read(chip,192),
                    list(m.temp_allocs),list(m.temp_frees),list(m.sprite_calls),
                    m.get(m.cell),m.get(STATE),m.named)
            opens,closes=m.opens,m.closes
            result=signed(m.bankfree(DIAG_ARGUMENT))
            assert result==expected,(layout,expected,result)
            assert before==(m.read(a,112),m.read(rec,40),m.read(chip,192),
                            m.temp_allocs,m.temp_frees,m.sprite_calls,
                            m.get(m.cell),m.get(STATE),m.named)
            assert m.opens-opens==m.closes-closes
        # All combinations, including real View active with nonidle Copper.
        for mask in range(1,16):
            restore()
            for bit,addr,value in ((1,GFX+34,1),(2,GFX+50,CI+160),
                                   (4,GFX+54,CI+160),(8,CI+164,0)):
                if mask&bit:m.put32(addr,value)
            check(-256-mask);count+=1
        restore()
        m.put32(GFX+34,1);m.put32(GFX+38,0)
        check(-273);count+=1
        restore()
        def late():
            m.put32(GFX+34,1)
            m.put32(GFX+50,CI+160)
        m.after_tof=late
        check(-259);count+=1
        restore()
        check(-190);count+=1
        assert m.bankfree(29)==0 and m.bankfree(DIAG_ARGUMENT-1)==0
    assert count==36
    print('S1P2LC_IDLE_DETAIL_CPU_PASS',count,flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s1p2lc(a.vasm)
    print('S1P2LC_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    route_cases(image,info)
    p2j.ProbeMachine=TransactionMachine
    assert p2j.suite(image,info)==54
    transactions(image,info)
    observer_cases(image,info,idle=(-257,-258,-264))
    idle_cases(image,info)
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
    print('S1P2LC_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)

if __name__=='__main__':main()
