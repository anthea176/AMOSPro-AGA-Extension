#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Execute the actual L2b Pattern on MC68020 with modeled OS/Blitter services.

Reuse the established L1 writer fixture and AP20 relocation models.
Not WinUAE or a real AMOS Compiler test. Also replay the L1/L2 native gates.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from struct import pack, unpack_from
import unittest
import subprocess
import tempfile
from hashlib import sha256

from unicorn.m68k_const import UC_M68K_REG_PC
from audit_ap20 import walk_tokens
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from build_m19_p2d_l2b_pattern_in_memory import build_l2b
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import RBSR, unpack_ap20
from test_m19_p2d_l1_safeport_gate_a import (
    Machine, DR, AR, EXEC, GFX, AMOS, STATE, DB, SB, BM, SCREEN,
    SAFE, DISP, CODE, GROUP, WIDTH, HEIGHT, STRIDE, SIZE, run_cases,
)
import test_m19_p2d_l2_first_bind_gate_a as l2_gate


class PatternMachine(Machine):
    def __init__(self, image, layout, front, depth, flags, ready=None,
                 port=True, *, single=False, legacy=False, fail_alloc=False):
        super().__init__(image, layout, front, depth, flags, ready, port,
                         fail_alloc=1 if fail_alloc else 0)
        self.single, self.legacy = single, legacy
        self.rgb = []
        self.pens = {}
        self.draws = []
        self.drawing_pending = False
        self.screen_rp = SCREEN+84
        self.put(self.screen_rp+4, BM+front*0x100)
        self.screen_rp_before = bytes(self.u.mem_read(self.screen_rp, 128))
        if single:
            self.put(STATE+32, 0)
        tok, parts, _ = unpack_ap20(image)
        entry = next(row['instruction'] for row in walk_tokens(tok)
                     if row['name'] == 'aga screen pattern')
        assert entry == 14
        stub = parts[entry]
        assert stub.startswith(RBSR) and stub[6:8] == b'\x4e\x75'
        group, offset = unpack_from('>HH', stub, 2)
        assert (group, offset+len(DISPATCH_V2)) == (142, 0x00764)
        if layout == 'runtime':
            address = CODE + sum(map(len, parts[:entry]))
            disp = sum(map(len, parts[:group])) - (address-CODE+2)
            self.u.mem_write(address, pack('>Hh', 0x6100, disp))
        else:
            address = CODE+0x200
            self.u.mem_write(address, pack('>HIH', 0x4EB9, GROUP, offset)+b'\x4e\x75')
        self.entries['pattern'] = address
        for lvo in (-852, -342, -306):
            self.u.mem_write(GFX+lvo, b'\x4e\x75')

    def target(self, rp):
        if self.single or self.legacy:
            assert rp == self.screen_rp
            target = self.front
        else:
            assert rp in self.owned and self.safe(), 'unsafe or public RastPort'
            target = self.back
        assert self.get(rp+4) == BM+target*0x100, 'wrong bitmap'
        return target

    def os_call(self, uc, addr, size, ctx):
        if addr == GFX-228:
            self.drawing_pending = False
        if addr == EXEC-690:
            assert not self.drawing_pending, 'free before WaitBlit'
        if addr not in (GFX-852, GFX-342, GFX-306):
            return super().os_call(uc, addr, size, ctx)
        assert self.a(6) == GFX
        if not (self.single or self.legacy):
            assert self.safe(), 'write before Safe'
            assert 'waitblit' in self.events, 'write before WaitBlit'
        if addr == GFX-852:
            assert self.a(0) == SCREEN+44
            self.rgb.append(tuple(self.d(i) for i in range(4)))
            self.events.append('setrgb')
        elif addr == GFX-342:
            rp = self.a(1)
            self.target(rp)
            self.pens[rp] = self.d(0)
            self.events.append('setapen')
        else:
            rp = self.a(1)
            page = self.target(rp)
            y = self.d(1)
            assert self.d(0) == 0 and self.d(2) == WIDTH-1
            assert self.d(3) == y and 0 <= y < HEIGHT
            pen = self.pens[rp]
            for plane, start in enumerate(self.planes[page]):
                at = start+y*STRIDE
                row = bytearray(uc.mem_read(at, STRIDE))
                for x in range(WIDTH):
                    bit = 128 >> (x & 7)
                    if pen & (1 << plane):
                        row[x//8] |= bit
                    else:
                        row[x//8] &= 255 ^ bit
                uc.mem_write(at, bytes(row))
            self.draws.append((page, y, pen))
            self.drawing_pending = not (self.single or self.legacy)
            self.events.append('rectfill')
        ret = self.get(self.a(7))
        uc.reg_write(AR[7], self.a(7)+4)
        uc.reg_write(DR[0], 0)
        uc.reg_write(DR[1], 0xdeadbeef)
        uc.reg_write(AR[0], 0xbad000)
        uc.reg_write(AR[1], 0xbad100)
        uc.reg_write(UC_M68K_REG_PC, ret)


def expected_page(before, depth):
    mask = ((1 << WIDTH)-1) << (8*STRIDE-WIDTH)
    rows = []
    for p in range(depth):
        result = bytearray()
        for y in range(HEIGHT):
            pen = y*(1 << depth)//HEIGHT
            value = int.from_bytes(before[p][y*STRIDE:(y+1)*STRIDE], 'big')
            value = (value & ~mask) | (mask if pen & (1 << p) else 0)
            result.extend(value.to_bytes(STRIDE, 'big'))
        rows.append(bytes(result))
    return tuple(rows)


def check(m, flags, success, calls, waits, *, alloc_fail=False, draw_page=None):
    before = m.snapshot()
    db_page = m.get(DB+8)
    disp = m.get(DB+16)
    m.run('pattern')  # inherited register/stack/canary/allocation assertions
    target = m.back if draw_page is None else draw_page
    after = list(before)
    expected_rgb = []
    if success:
        after[target] = expected_page(before[target], m.depth)
        for y in range(HEIGHT):
            pen = y*(1 << m.depth)//HEIGHT
            red = pen*255//((1 << m.depth)-1)
            expected_rgb.append((pen, red << 24, (255-red) << 24, 0x30000000))
    assert m.snapshot() == tuple(after), ('pixels', m.front, flags, success)
    assert m.rgb == expected_rgb
    assert m.draws == ([(target, y, y*(1 << m.depth)//HEIGHT)
                        for y in range(HEIGHT)] if success else [])
    assert (m.safe_calls, m.safe_waits) == (calls, waits), m.events
    assert m.get(DB+20) == (flags & ~1 if success or alloc_fail else flags)
    assert m.get(DB+8) == db_page and m.get(DB+16) == disp
    assert bytes(m.u.mem_read(m.screen_rp, 128)) == m.screen_rp_before
    if not (m.single or m.legacy):
        assert m.alloc_calls == int(success or alloc_fail)
        assert m.screen_rp not in m.pens
        if success:
            assert m.events.count('waitblit') >= 2
            assert m.events.index('waitblit') < m.events.index('setrgb')
            assert not m.drawing_pending
            if flags & 1:
                assert m.events.index('getmsg') < m.events.index('setrgb')
    else:
        assert m.alloc_calls == 0
    return 1


def run_pattern_cases(prior, fixed):
    n = 0
    for layout in ('runtime', 'compiled'):
        for front in (0, 1):
            for depth in (2, 8):
                # The observed L2 FRONT defect is an explicit failing-contract
                # witness; the single-buffer behavior is intentionally retained.
                old = PatternMachine(prior, layout, front, depth, 0, legacy=True)
                n += check(old, 0, True, 0, 0, draw_page=front)
                for image in (prior, fixed):
                    single = PatternMachine(image, layout, front, depth, 0, single=True)
                    n += check(single, 0, True, 0, 0, draw_page=front)
                for flags, ready, port, ok, calls, waits in (
                    (0, None, True, True, 0, 0),
                    (2, None, True, True, 0, 0),
                    (1, 0, True, True, 1, 0),
                    (3, 0, True, True, 1, 0),
                    (3, 1, True, True, 2, 1),
                    (3, 2, True, True, 3, 2),
                    (3, 3, True, True, 4, 3),
                    (3, None, True, False, 4, 3),
                    (3, 0, False, False, 0, 0),
                ):
                    m = PatternMachine(fixed, layout, front, depth, flags, ready, port)
                    n += check(m, flags, ok, calls, waits)
                m = PatternMachine(fixed, layout, front, depth, 3, 0)
                m.put(DB+12, SAFE+1)
                n += check(m, 3, False, 0, 0)
                m = PatternMachine(fixed, layout, front, depth, 3, 0, fail_alloc=True)
                n += check(m, 3, False, 1, 0, alloc_fail=True)
                for address, value in (
                    (DB+8, 2), (DB+(1-front)*4, 0),
                    (SB+(1-front)*0x100, 0), (SB+(1-front)*0x100, BM+front*0x100),
                    (STATE+8, 0), (STATE+16, 0), (STATE+20, 1),
                    (AMOS+456, 0), (STATE, 0),
                ):
                    m = PatternMachine(fixed, layout, front, depth, 3, 0)
                    m.put(address, value)
                    n += check(m, 3, False, 0, 0)
    print('P2D L2B PATTERN MC68020 PASS', n,
          'cases including original FRONT witnesses, simple mode and both DB parities', flush=True)
    return n


def verify_linked_source(vasm: Path, expected: bytes) -> None:
    """Compare the checked-in direct master, without writing any distributed Lib."""
    root = Path(__file__).resolve().parents[1]
    folder = root / 'src/native/m19_p2d_l2b'
    vasm = vasm.resolve()
    with tempfile.TemporaryDirectory(prefix='aga-p2d-l2b-linked-') as temp:
        output = Path(temp) / 'source-check.bin'
        result = subprocess.run(
            [str(vasm), '-Fbin', '-m68020', '-no-opt', '-quiet',
             '-I../m19_p2d', '-o', str(output),
             'M19_P2D_L2B_LINKED_EDITABLE.s'],
            cwd=folder, capture_output=True, text=True, timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        direct = output.read_bytes()
    digest = sha256(direct).hexdigest()
    assert digest == 'a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc', 'direct L2b SHA mismatch'
    assert direct == expected, 'linked ASM and source builder differ'
    installed = (root / 'dist/AMOSPro_AGA.Lib').read_bytes()
    if sha256(installed).hexdigest() == digest:
        assert direct == installed, 'linked ASM and installed L2b differ'
    print('P2D L2B LINKED ASM BYTE-EXACT PASS', len(direct), digest, flush=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm', type=Path, required=True)
    vasm = cli.parse_args().vasm
    prior, _ = build_l2(vasm)
    image, meta = build_l2b(vasm)
    verify_linked_source(vasm, image)
    print('P2D L2B SOURCE IN MEMORY', meta, flush=True)
    assert run_pattern_cases(prior, image) == 184
    assert run_cases(image, meta) == 172
    l2_gate.IMAGE, l2_gate.META = image, meta
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert result.wasSuccessful() and result.testsRun == 10
    print('P2D L2B GATE A PASS: 184 Pattern cases, 172 writer cases, 10 Bob suites', meta)
    print('WinUAE B / real Compiler C / physical D NOT TESTED')
    # Transfer only the checked append-only source delta, not an alternate Lib.
    # The canonical image must be reconstructed and checked against these
    # digests by the authorized delivery operation; this CI never writes Git.
    import base64
    import hashlib
    import json
    from build_m19_p2d_l2b_pattern_in_memory import OFFSET, PRIOR_SIZE, UNIT
    _, parts, title = unpack_ap20(image)
    evidence = dict(size=len(image), sha256=hashlib.sha256(image).hexdigest(),
                    git_blob=hashlib.sha1(f'blob {len(image)}'.encode()+bytes([0])+image).hexdigest(),
                    branch=parts[UNIT][OFFSET:OFFSET+6].hex(),
                    tail=base64.b64encode(parts[UNIT][PRIOR_SIZE:]).decode('ascii'),
                    title=base64.b64encode(title).decode('ascii'))
    print('L2B_CHECKED_DELTA '+json.dumps(evidence, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
