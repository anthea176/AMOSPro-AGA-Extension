#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Historical regressions on the exact P3 candidate, not on the active Lib.
Reuse the established independent S2c regression oracles unchanged.
"""
import argparse,json,os,unittest
from pathlib import Path
from build_m19_s2d_in_memory import build_s2d,protected
from test_m19_s2r_agapic_gate_a import cases as agapic_cases
import test_m19_s1p2m_gate_a as regress

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    p.add_argument('--suite',required=True,choices=('agapic','pattern','safeport','bob'))
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    image,info=build_s2d(a.vasm)
    print('S2D_P3_LEGACY_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite=='agapic':
        for layout in ('runtime','compiled'):agapic_cases(image,layout)
    elif a.suite=='pattern':
        prior,_=regress.build_l2(a.vasm)
        regress.verify_linked_source(a.vasm,before[1])
        assert regress.run_pattern_cases(prior,image)==184
    elif a.suite=='safeport':
        assert regress.run_cases(image,info)==172
    else:
        _,meta=regress.build_l2(a.vasm)
        regress.l2_gate.IMAGE,regress.l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(regress.l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
    assert protected()==before
    print('S2D_P3_LEGACY_SUITE_PASS '+a.suite,flush=True)
if __name__=='__main__':main()
