#!/usr/bin/env python3
"""M10 R25 CPU/Gate-A preflight: native 68000 AABB, 8-argument AP20 ABI.

Covers signed 32-bit extremes, positive-area overlap, exact edge/corner
touch, symmetry, invalid sizes, R24 preservation and deterministic HUNK.
It is NOT a substitute for AMOS interpreted/WinUAE or hardware testing.
"""
import random
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from audit_ap20 import parse, inspect
from ap20_utils import split, digest
from build_m10_rect_overlap_r25 import (
    build, BASE, LAST_GOOD, BASE_SHA256, LAST_GOOD_SHA256,
    ENTRY, SIGNATURE, TOKEN, GETP,
)
from m10_rect_overlap_r25_emit import emit_rect_overlap
from test_m8_mouse_position_r19 import (
    MouseMachine, ARGS, CODE, STACK, STOP, DR, AR, AMOS,
)

MIN = -(1 << 31)
MAX = (1 << 31) - 1


def reference(v):
    ax, ay, aw, ah, bx, by, bw, bh = v
    return int(aw > 0 and ah > 0 and bw > 0 and bh > 0 and
               max(ax, bx) < min(ax + aw, bx + bw) and
               max(ay, by) < min(ay + ah, by + bh))


class RectMachine(MouseMachine):
    def overlap(self, args):
        assert len(args) == 8, args
        assert all(MIN <= x <= MAX for x in args), args
        ax, ay, aw, ah, bx, by, bw, bh = args
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200 + i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000 + i * 256)
        self.uc.reg_write(AR[3], ARGS)
        self.uc.reg_write(AR[5], AMOS)
        for i, value in enumerate((bw, by, bx, ah, aw, ay, ax)):
            self.put(ARGS + 4 * i, value)
        self.uc.reg_write(DR[3], bh & 0xffffffff)
        saved = {reg: self.uc.reg_read(reg) for reg in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE + self.p.starts[ENTRY], STOP, count=10000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP, ("no RTS", args)
        assert self.uc.reg_read(AR[7]) == STACK + 4, ("SP", args)
        assert self.uc.reg_read(AR[3]) == ARGS + 28, ("AP20 A3+28", args)
        assert self.uc.reg_read(DR[2]) == 0, ("integer D2", args)
        for reg, initial in saved.items():
            if reg not in (DR[2], DR[3], AR[3]):
                assert self.uc.reg_read(reg) == initial, ("ABI", args, reg)
        result = self.uc.reg_read(DR[3])
        assert result in (0, 1), (args, result)
        return result


def run():
    candidate, meta = build()
    assert candidate == build()[0]
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    token0, old, _ = split(BASE.read_bytes())
    token1, new, _ = split(candidate)
    assert len(old) == ENTRY == 35 and len(new) == 36
    assert new[:ENTRY-1] == old[:ENTRY-1]
    assert new[ENTRY-1] == old[ENTRY-1] + GETP
    code, labels = emit_rect_overlap()
    assert new[ENTRY] == code
    assert token1.startswith(token0[:-6]) and token1 != token0
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    names = [x for x in audit["tokens"] if x["name"] == TOKEN]
    assert len(names) == 1
    assert (names[0]["instruction"], names[0]["function"],
            names[0]["signature"]) == (1, ENTRY, SIGNATURE)
    assert any(x["index"] == ENTRY and x["parameters"] == 8 and x["getp"]
               for x in audit["parameter_checks"])
    md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    instructions = list(md.disasm(code, 0))
    assert sum(x.size for x in instructions) == len(code), "invalid 68000"
    assert all(x.mnemonic not in ("dc.w", "illegal", "jsr", "bsr", "trap")
               for x in instructions)
    assert set(labels.values()) <= {x.address for x in instructions}

    fixed = [
        ((0,0,10,10,0,0,10,10),1),
        ((0,0,10,10,10,0,10,10),0),
        ((0,0,10,10,0,10,10,10),0),
        ((0,0,10,10,10,10,10,10),0),
        ((0,0,10,10,9,0,10,10),1),
        ((0,0,10,10,0,9,10,10),1),
        ((0,0,10,10,9,9,10,10),1),
        ((0,0,1,1,0,0,1,1),1),
        ((0,0,1,1,1,0,1,1),0),
        ((0,0,1,1,0,1,1,1),0),
        ((0,0,1,1,1,1,1,1),0),
        ((0,0,100,100,10,10,2,2),1),
        ((10,10,2,2,0,0,100,100),1),
        ((-10,-20,20,30,0,0,1,1),1),
        ((-10,-20,20,30,10,0,1,1),0),
        ((-10,-20,20,30,0,10,1,1),0),
        ((0,0,0,10,0,0,10,10),0),
        ((0,0,10,0,0,0,10,10),0),
        ((0,0,-1,10,0,0,10,10),0),
        ((0,0,10,-1,0,0,10,10),0),
        ((0,0,10,10,0,0,0,10),0),
        ((0,0,10,10,0,0,10,0),0),
        ((0,0,10,10,0,0,-1,10),0),
        ((0,0,10,10,0,0,10,-1),0),
        ((0,0,10,10,1000,1000,10,10),0),
        ((0,0,10,10,-1000,-1000,10,10),0),
        ((MIN,MIN,MAX,MAX,MIN,MIN,MAX,MAX),1),
        ((MAX,MAX,MAX,MAX,MAX,MAX,1,1),1),
        ((MIN,0,MAX,1,-1,0,1,1),0),
        ((MIN,0,MAX,1,-2,0,1,1),1),
        ((0,0,MAX,1,MAX,0,1,1),0),
        ((0,0,MAX,1,MAX-1,0,2,1),1),
        ((MIN,0,MAX,1,MAX,0,1,1),0),
        ((MAX,0,1,1,MIN,0,MAX,1),0),
        ((0,MIN,1,MAX,0,MAX,1,1),0),
        ((0,MAX,1,1,0,MIN,1,MAX),0),
        ((MIN,MIN,MAX,MAX,MIN+1,MIN+1,1,1),1),
        ((MAX,MAX,1,1,MAX-1,MAX-1,2,2),1),
        ((MIN,MIN,1,1,MIN+1,MIN,1,1),0),
        ((MIN,MIN,1,1,MIN,MIN+1,1,1),0),
        ((MAX,MAX,1,1,MAX-1,MAX,1,1),0),
        ((MAX,MAX,1,1,MAX,MAX-1,1,1),0),
    ]
    machine = RectMachine(candidate)
    count = 0
    for args, expected in fixed:
        got = machine.overlap(args)
        assert got == expected == reference(args), ("fixed", args, got, expected)
        reverse = args[4:] + args[:4]
        assert machine.overlap(reverse) == expected, ("symmetry", args)
        count += 2

    machine.put(AMOS + 456, 0)
    assert machine.overlap((10,10,20,20,15,15,20,20)) == 1
    assert machine.overlap((10,10,20,20,30,30,20,20)) == 0
    count += 2

    rng = random.Random(0xA10B25)
    edges = [MIN, MIN+1, -1000000000, -32768, -1024, -1, 0, 1, 2, 10,
             64, 127, 255, 256, 319, 320, 511, 512, 640, 1280, 32767,
             1000000000, MAX-1, MAX]
    sizes = [MIN, -200, -1, 0, 1, 2, 3, 4, 5, 10, 16, 32,
             100, 256, 640, 1024, MAX]
    for i in range(540):
        if i % 3 == 0:
            args = tuple(rng.choice(edges) for _ in range(8))
        else:
            ax, ay = rng.choice(edges), rng.choice(edges)
            aw, ah = rng.choice(sizes), rng.choice(sizes)
            bx = max(MIN, min(MAX, ax + rng.randint(-5, 513)))
            by = max(MIN, min(MAX, ay + rng.randint(-5, 513)))
            bw, bh = rng.choice(sizes), rng.choice(sizes)
            args = (ax, ay, aw, ah, bx, by, bw, bh)
        got = machine.overlap(args)
        wanted = reference(args)
        assert got == wanted, ("random", i, args, got, wanted)
        count += 1
        if i % 7 == 0:
            reverse = args[4:] + args[:4]
            assert machine.overlap(reverse) == got, ("symmetry", i, args)
            count += 1

    print("M10 R25 CPU PASS:", count,
          "68000 geometry/ABI cases, 8 args A3+28; int32 overflow safe,"
          " 1px overlap, touching edges/corners=0, symmetry; R24 intact.")
    print("R25 preview", meta)
    print("Gate B interpreted AMOS/WinUAE, Compiler, real Amiga: NOT TESTED")


if __name__ == "__main__":
    run()
