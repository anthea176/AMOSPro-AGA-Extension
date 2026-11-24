#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1h exact source reconstruction plus inherited L2b regressions."""
from __future__ import annotations
import argparse
import base64
from hashlib import sha1,sha256
import json
from pathlib import Path
import unittest

from active_library import P2DL2B_SHA
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from build_m19_s1p1h_l2b_bank_fix_ap20 import build_s1p1h
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p2d_l1_safeport_gate_a import run_cases
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
import test_m19_p2d_l2_first_bind_gate_a as l2_gate


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    p.add_argument('--tested-native',type=Path,required=True)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    good=(root/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    active=(root/'dist/AMOSPro_AGA.Lib').read_bytes()
    assert sha256(good).hexdigest()==P2DL2B_SHA
    image,meta=build_s1p1h(a.vasm)
    _,parts,_=unpack_ap20(image)
    native=parts[207][len(DISPATCH_V2):]
    assert native==a.tested_native.read_bytes()
    assert parts[:203]==unpack_ap20(good)[1]
    verify_linked_source(a.vasm,good)
    prior,_=build_l2(a.vasm)
    assert dispatch_models(parts,207,0,204)==2
    assert dispatch_models(parts,207,8,206)==2
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,meta)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    assert (root/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (root/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    evidence=dict(meta,git_blob=sha1(f'blob {len(image)}'.encode()+bytes([0])+image).hexdigest())
    print('S1P1H_GATE_A_PASS '+json.dumps(evidence,sort_keys=True),flush=True)
    print('S1P1H_SOURCE_NATIVE_BASE64 '+base64.b64encode(native).decode('ascii'),flush=True)


if __name__=='__main__':
    main()
