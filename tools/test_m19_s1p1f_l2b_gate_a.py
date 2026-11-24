#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A for the exact S1-P1f AP20 image; no WinUAE/Compiler claims."""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import unittest

from active_library import P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, S1P1I_SHA, SPRITE_L2B_HISTORICAL_SHAS
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from build_m19_s1p1f_l2b_get_sprite_ap20 import build_s1p1f
from compiler_relocation import unpack_ap20
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm', type=Path, required=True)
    p.add_argument('--native', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    active = (root / 'dist/AMOSPro_AGA.Lib').read_bytes()
    good = (root / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(good).hexdigest() == P2DL2B_SHA
    assert active == good or sha256(active).hexdigest() in (*SPRITE_L2B_HISTORICAL_SHAS)
    prior, _ = build_l2(a.vasm)
    image, meta = build_s1p1f(a.vasm, a.native.read_bytes())
    if sha256(active).hexdigest() == S1P1F_SHA:
        assert image == active
    verify_linked_source(a.vasm, good)
    _, parts, _ = unpack_ap20(image)
    assert parts[:203] == unpack_ap20(good)[1]
    assert dispatch_models(parts, 207, 0, 204) == 2
    assert dispatch_models(parts, 207, 8, 206) == 2
    assert run_pattern_cases(prior, image) == 184
    assert run_cases(image, meta) == 172
    l2_gate.IMAGE, l2_gate.META = image, meta
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun == 10
    assert (root / 'dist/AMOSPro_AGA.Lib').read_bytes() == active
    assert (root / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == good
    evidence = dict(meta, git_blob=sha1(
        f'blob {len(image)}'.encode() + bytes([0]) + image).hexdigest())
    print('S1P1F_GATE_A_PASS ' + json.dumps(evidence, sort_keys=True), flush=True)
    print('Both Sprite AP20 relocations; 184 Pattern, 172 writers, 10 Bob suites; '
          'real MC68020 modeled OS, B/C/D NOT TESTED; no Lib written.', flush=True)


if __name__ == '__main__':
    main()
