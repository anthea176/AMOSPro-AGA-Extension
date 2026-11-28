#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A for public overload, both layouts plus all S2f legacy suites."""
import argparse,base64,json,os,unittest
from pathlib import Path
from hashlib import sha256,sha1
from unittest.mock import patch
from build_m19_s2g_public_in_memory import build_s2g_public,grammar_tests,protected
from test_m19_s2g_priority_gate_a import cases
from test_m19_s2f_public_gate_a import public,ClipBase,agapic_cases,regress
import test_m19_s2d_public_display_gate_a as display

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    p.add_argument('--historical',type=Path,required=True)
    p.add_argument('--suite',required=True,choices=('link','runtime','compiled',
        'legacy-runtime','legacy-compiled','agapic','pattern','safeport','bob','capture','chain'))
    p.add_argument('--campaign',type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    before=protected()
    grammar_tests()
    image,info=build_s2g_public(a.vasm)
    print('S2G_PUBLIC_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    if a.suite=='link':
        other,second=build_s2g_public(a.vasm)
        assert image==other and info==second
        assert a.campaign
        from prepare_m19_s2g_campaign import prepare,ROOT
        from verify_m19_s2g_delivery import verify_library,verify_asc
        from verify_m19_s2e_delivery import verify_abk
        # protected()[3] is the S1P1e historical ABK, not the hotspot fixture.
        bank_path=ROOT/'tests/current/AGSP_HOTSPOT_TEST.ABK'
        bank=bank_path.read_bytes()
        verify_abk(bank)
        asc=prepare(before[2],bank)
        assert asc==a.campaign.read_bytes()
        verify_library(image,before[1])
        verify_asc(asc,bank)
        assert bank_path.read_bytes()==bank
        # Byte receipt for the authorized later canonical activation.
        # No artifact, alternate Lib, archive or Git write by CI.
        for tag,data in (('LIB',image),('ASC',asc),('ABK',bank)):
            digest=sha256(data).hexdigest()
            blob=sha1(f'blob {len(data)}'.encode()+b'\0'+data).hexdigest()
            print('S2G_DELIVERY_ID',tag,len(data),digest,blob,flush=True)
            for i in range(0,len(data),1536):
                print('S2G_PAYLOAD',tag,i//1536,
                      base64.b64encode(data[i:i+1536]).decode(),flush=True)
    elif a.suite in ('runtime','compiled'):
        cases(image,info,a.suite)
    elif a.suite.startswith('legacy-'):
        layout=a.suite[7:]
        public(image,info,layout)
        with patch.object(display,'WidePublic',ClipBase):
            display.cases(image,info,layout,clipping=True)
    elif a.suite=='agapic':
        for layout in ('runtime','compiled'):agapic_cases(image,layout)
    elif a.suite=='pattern':
        prior,_=regress.build_l2(a.vasm)
        regress.verify_linked_source(a.vasm,before[1])
        assert regress.run_pattern_cases(prior,image)==184
    elif a.suite=='safeport':
        assert regress.run_cases(image,info)==172
    elif a.suite=='capture':
        from test_m19_s2d_public_capture_gate_a import capture_cases,wide_cases
        for layout in ('runtime','compiled'):
            capture_cases(image,layout)
            wide_cases(image,layout)
    elif a.suite=='chain':
        from test_m19_s2c_public_gate_a import chain
        chain(image)
    else:
        _,meta=regress.build_l2(a.vasm)
        regress.l2_gate.IMAGE,regress.l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(regress.l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
    assert protected()==before
    print('S2G_PUBLIC_SUITE_PASS '+a.suite,flush=True)

if __name__=='__main__':main()
