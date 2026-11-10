#!/usr/bin/env python3
"""M6/R15: 68000 ABI and pixel-accurate tests for the Clear -> Fill adapter.

Unicorn mocks graphics.library; passing these tests does NOT mean WinUAE,
AMOS Compiler or real Amiga hardware have been tested.
"""
from struct import unpack_from, pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import *

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m6_blit_clear_r15 import (build, emit_clear, BASE, BASE_SHA256,
                                      LAST_GOOD, LAST_GOOD_SHA256, ENTRY,
                                      FILL_ENTRY, DELIMITER)
from test_m6_blit_fill_r14 import FillMachine, expected_fill
from test_m6_blit_copy_r13 import CopyMachine
from test_m5_generic import (CODE, STATE, DB, SB, BITMAP, AMOS, STACK,
                             STOP, DR, AR)


class ClearMachine(FillMachine):
    def run_clear(self, x, y, w, h):
        # Actual AMOS365 function convention: last parameter in D3,
        # others in reverse order in the A3 parameter stack.
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200 + i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000 + i * 256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x58000)
        for i, value in enumerate((w, y, x)):
            self.put(0x58000 + i * 4, value)
        self.uc.reg_write(DR[3], h & 0xffffffff)
        saved = {r: self.uc.reg_read(r) for r in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE + self.p.starts[ENTRY], STOP, count=300000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP, "No RTS to AMOS"
        assert self.a(7) == STACK + 4, "CPU SP unbalanced"
        for reg, previous in saved.items():
            if reg in (DR[2], DR[3], AR[3]):
                continue
            assert self.uc.reg_read(reg) == previous, (
                reg, previous, self.uc.reg_read(reg))
        assert self.d(2) == 0, "AMOS return type must be integer"
        assert self.a(3) == 0x58000 + 12, "AMOS A3 must consume 3 longs"
        assert self.pending is None, "Unfinished asynchronous bitmap blit"
        return self.d(3)


def run():
    candidate, report = build()
    assert build()[0] == candidate, "R15 not reproducible"
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok14, seg14, _ = split(BASE.read_bytes())
    tok15, seg15, _ = split(candidate)
    assert len(seg14) == 21 and len(seg15) == 22
    assert seg15[:20] == seg14[:20], "R13 Copy or prior code changed"
    assert seg15[FILL_ENTRY] == seg14[FILL_ENTRY] + DELIMITER
    clear, meta = emit_clear(len(seg14[FILL_ENTRY]))
    assert seg15[ENTRY] == clear

    audited = inspect(parse(candidate))
    assert not audited["issues"], audited["issues"]
    clear_tokens = [r for r in audited["tokens"] if r["name"] == "aga blit clear"]
    assert len(clear_tokens) == 1
    assert (clear_tokens[0]["function"], clear_tokens[0]["signature"]) == (
        ENTRY, "00,0,0,0")
    assert any(r["index"] == ENTRY and r["getp"]
               for r in audited["parameter_checks"])
    assert tok15 != tok14

    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    instructions = list(dis.disasm(clear, 0))
    assert sum(i.size for i in instructions) == len(clear)
    assert all(i.mnemonic not in ("dc.w", "illegal") for i in instructions)
    assert sum(i.mnemonic.startswith("bsr") for i in instructions) == 1
    call_at = meta["call_at"]
    assert clear[call_at:call_at + 2] == bytes.fromhex("6100")
    signed_disp = unpack_from(">h", clear, call_at + 2)[0]
    assert signed_disp == meta["bsr_displacement"]
    p = parse(candidate)
    assert (p.starts[ENTRY] + call_at + 2 + signed_disp
            == p.starts[FILL_ENTRY]), "BSR must call EXACT R14 Fill entry"

    positive = 0
    for depth in (1, 2, 4, 8):
        for front in (0, 1):
            for x, y, w, h in ((7, 13, 37, 19),
                               (95, 120, 91, 46),
                               (319, 255, 1, 1)):
                m = ClearMachine(candidate, depth=depth, front=front)
                previous = m.snapshot()
                assert m.run_clear(x, y, w, h) == 1, (depth, front, x, y)
                assert len(m.fill_calls) == depth and m.waits == depth
                assert [r[0] for r in m.fill_calls] == list(range(depth))
                assert all(r[-1] == 0 for r in m.fill_calls), "All planes must clear"
                after = m.snapshot()
                for plane in range(depth):
                    expected = expected_fill(previous[plane], x, y, w, h,
                                             0, plane, m.stride)
                    assert after[plane] == expected, (
                        depth, front, plane, x, y, w, h)
                positive += 1

    # Clearing must preserve a surrounding colored region and other pixels.
    for depth in (1, 4, 8):
        m = ClearMachine(candidate, depth=depth)
        pen = (1 << depth) - 1
        assert m.run_fill(10, 10, 64, 40, pen) == 1
        before = m.snapshot()
        m.fill_calls.clear()
        m.waits = 0
        assert m.run_clear(17, 18, 26, 16) == 1
        assert len(m.fill_calls) == m.waits == depth
        for plane in range(depth):
            assert m.snapshot()[plane] == expected_fill(
                before[plane], 17, 18, 26, 16, 0, plane, m.stride)
        positive += 1

    rejected = 0
    for args in ((-1, 0, 12, 14), (0, -1, 12, 14),
                 (0, 0, 0, 14), (0, 0, 12, 0),
                 (320, 0, 1, 1), (0, 256, 1, 1),
                 (315, 0, 12, 10), (0, 251, 12, 10),
                 (0, 0, -1, 10), (0, 0, 10, -1),
                 (0x7fffffff, 0, 2, 2),
                 (0, 0, 0x7fffffff, 2)):
        m = ClearMachine(candidate, depth=8)
        before = m.snapshot()
        assert m.run_clear(*args) == 0, args
        assert not m.fill_calls and m.waits == 0 and m.snapshot() == before
        rejected += 1

    for case in ("screen", "gfx", "dbstate", "width", "height", "depth",
                 "short_stride", "short_rows", "bad_plane_null",
                 "bad_plane_minus1", "no_sb", "no_bitmap"):
        m = ClearMachine(candidate, depth=4)
        bm = BITMAP + 0x100
        if case == "screen": m.put(STATE + 0, 0)
        elif case == "gfx": m.put(STATE + 8, 0)
        elif case == "dbstate": m.put(STATE + 32, 0)
        elif case == "width": m.put(STATE + 12, 0x10000)
        elif case == "height": m.put(STATE + 16, 0)
        elif case == "depth": m.put(STATE + 28, 9)
        elif case == "short_stride": m.uc.mem_write(bm, pack(">H", 2))
        elif case == "short_rows": m.uc.mem_write(bm + 2, pack(">H", 1))
        elif case == "bad_plane_null": m.put(bm + 8 + 4 * 2, 0)
        elif case == "bad_plane_minus1": m.put(bm + 8 + 4 * 2, 0xffffffff)
        elif case == "no_sb": m.put(DB + 4, 0)
        else: m.put(SB + 0x100, 0)
        before = m.snapshot()
        assert m.run_clear(10, 20, 32, 17) == 0, case
        assert not m.fill_calls and m.waits == 0 and m.snapshot() == before
        rejected += 1

    m = ClearMachine(candidate, depth=8, fail_plane=3)
    assert m.run_clear(10, 10, 19, 11) == 0
    assert len(m.fill_calls) == 4 and m.waits == 3
    rejected += 1

    # Both previously validated entrypoints remain callable in R15.
    fill = ClearMachine(candidate, depth=8)
    assert fill.run_fill(18, 24, 86, 48, 15) == 1
    assert len(fill.fill_calls) == fill.waits == 8
    copy = CopyMachine(candidate, depth=8)
    assert copy.run_copy((0, 0, 160, 128, 96, 80)) == 1
    assert len(copy.blits) == copy.waits == 1

    print("M6 R15 CPU PASS: %d valid Clear, %d rejected/error cases, "
          "R14 Fill + R13 Copy regression; A3 +12, SP balanced, "
          "exact pixels, single BSR to validated Fill" % (positive, rejected))
    print("M6 R15 candidate", report["size"], "bytes SHA256", report["sha256"])
    print("WinUAE / Compiler / physical AGA: NOT TESTED")


if __name__ == "__main__":
    run()
