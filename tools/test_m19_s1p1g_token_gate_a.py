#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Targeted AP20 regression for the AMOS Syntax error reported on S1-P1f."""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
from pathlib import Path
import subprocess

from active_library import P2DL2B_SHA, S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, S1P1I_SHA, verify_s1p1g, verify_s1p1h, verify_s1p1i, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, S1P2LC_SHA, S1P2M_SHA, S2A_SHA, S2B_SHA, S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA, S2D_SHA, S2E_SHA, S2F_SHA, S2G_SHA, frozen_s1p1i
from audit_ap20 import inspect, parse, token_role_issues, walk_tokens
from build_m19_s1p1g_l2b_get_sprite_ap20 import correct_s1p1f
from compiler_relocation import unpack_ap20

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm', type=Path)
    p.add_argument('--native', type=Path)
    a = p.parse_args()
    active = (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes()
    good = (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(good).hexdigest() == P2DL2B_SHA
    installed=active
    if sha256(active).hexdigest() in (S1P2I_SHA,S1P2J_SHA,S1P2K_SHA,S1P2LB_SHA,S1P2LC_SHA,S1P2M_SHA,S2A_SHA,S2B_SHA,S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA,S2D_SHA, S2E_SHA, S2F_SHA, S2G_SHA):
        active=frozen_s1p1i(active,good)
    digest = sha256(active).hexdigest()
    if digest == S1P1F_SHA:
        parent = active
    elif digest == S1P1G_SHA:
        parent = verify_s1p1g(active, good)
    elif digest in (S1P1H_SHA,S1P1I_SHA):
        (verify_s1p1h if digest==S1P1H_SHA else verify_s1p1i)(active, good)
        # Historical AP20-only oracle, not a new production source or distribution.
        historical = subprocess.check_output(
            ['git', 'show', 'eb2b22119420196f44184a4b36035de18989fe44:dist/AMOSPro_AGA.Lib'],
            cwd=ROOT)
        parent = verify_s1p1g(historical, good)
        assert unpack_ap20(active)[0] == unpack_ap20(historical)[0]
        assert unpack_ap20(active)[1][:207] == unpack_ap20(historical)[1][:207]
    else:
        raise AssertionError('Expected exact P1f, P1g or P1h candidate')
    assert sha256(parent).hexdigest() == S1P1F_SHA
    oldtok, oldparts, oldtitle = unpack_ap20(parent)
    bad = token_role_issues(list(walk_tokens(oldtok)))
    assert [(x['name'], x['signature']) for x in bad] == [
        ('get aga sprite', '00,0,0,0,0,0')]
    image = correct_s1p1f(parent, good)
    tok, parts, title = unpack_ap20(image)
    rows = [row for row in walk_tokens(tok) if row['signature']]
    assert len(rows) == 102 and len(parts) == 208
    assert not token_role_issues(rows)
    assert rows[-1]['signature'] == 'I0,0,0,0,0,0'
    assert parts == oldparts
    assert title == oldtitle.replace(b'S1-P1f', b'S1-P1g')
    assert len(tok) == len(oldtok)
    assert [(x, y) for x, y in zip(oldtok, tok) if x != y] == [(ord('0'), ord('I'))]
    assert len(image) == len(parent) == 142684
    assert sum(x != y for x, y in zip(image, parent)) == 3
    assert not inspect(parse(image))['issues']
    assert sha256(image).hexdigest() == S1P1G_SHA
    blob = sha1(f'blob {len(image)}'.encode() + bytes([0]) + image).hexdigest()
    assert blob == 'b45ea91d9d2133ed90704305a8da34cbee339507'
    if digest == S1P1G_SHA:
        assert image == active
    assert (ROOT / 'dist/AMOSPro_AGA.Lib').read_bytes() == installed
    assert (ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes() == good
    print('S1P1G_TOKEN_GATE_A_PASS', len(rows), len(parts), len(image),
          sha256(image).hexdigest(), blob, flush=True)
    print('P1f negative oracle PASS; all 102 roles consistent; all 208 native '
          'units identical; exactly 3 bytes changed; B/C/D NOT TESTED.', flush=True)
    if a.vasm or a.native:
        assert a.vasm and a.native
        from build_m19_s1p1g_l2b_get_sprite_ap20 import build_s1p1g
        from build_m19_p2d_l2_first_bind_in_memory import build_l2
        from test_m19_p1a_getters_gate_a import dispatch_models
        from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases, verify_linked_source
        from test_m19_p2d_l1_safeport_gate_a import run_cases
        import test_m19_p2d_l2_first_bind_gate_a as l2_gate
        import unittest
        rebuilt, meta = build_s1p1g(a.vasm, a.native.read_bytes())
        assert rebuilt == image
        prior, _ = build_l2(a.vasm)
        verify_linked_source(a.vasm, good)
        assert dispatch_models(parts, 207, 0, 204) == 2
        assert dispatch_models(parts, 207, 8, 206) == 2
        assert run_pattern_cases(prior, image) == 184
        assert run_cases(image, meta) == 172
        l2_gate.IMAGE, l2_gate.META = image, meta
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun == 10
        print('S1P1G_SOURCE_NATIVE_GATE_A_PASS', S1P1G_SHA, blob, flush=True)


if __name__ == '__main__':
    main()
