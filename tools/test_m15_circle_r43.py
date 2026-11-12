#!/usr/bin/env python3
"""M15/R43 Gate A: native 68000 midpoint circle, clipping and strict ABI.

The actual 68000 code runs in Unicorn; all OS calls are mocked with bound
checks. This is NOT AMOS interpreted, AMOS Compiler or physical AGA testing.
"""
from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m15_circle_r43 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY_INDEX, GETP, API
)
from m15_circle_r43_emit import emit_circle
from test_m15_draw_r41 import DrawMachine
from test_m15_box_r42 import verify_bitmap
from test_m15_plot_r40 import ARGS
from test_m5_generic import CODE, EXEC, STATE, DB, STACK, STOP, AMOS, DR, AR


def reference_circle(cx, cy, radius, width=320, height=256):
    """Independent reference raster point set, original contour only."""
    if not 0 <= radius <= 32767 or not -32768 <= cx <= 32767 or not -32768 <= cy <= 32767:
        return set()
    pixels = set()
    x, y, decision = radius, 0, 1-radius
    while y <= x:
        points = (
            (cx+x,cy+y), (cx-x,cy+y), (cx+x,cy-y), (cx-x,cy-y),
            (cx+y,cy+x), (cx-y,cy+x), (cx+y,cy-x), (cx-y,cy-x)
        )
        pixels.update((px,py) for px,py in points if 0<=px<width and 0<=py<height)
        y += 1
        if decision < 0:
            decision += 2*y+1
        else:
            x -= 1
            decision += 2*(y-x)+1
    return pixels


class CircleMachine(DrawMachine):
    def circle(self, cx=160, cy=128, radius=34, pen=3, limit=9000000):
        self.pen = pen
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], ARGS)
        for i, value in enumerate((radius, cy, cx)):
            self.put(ARGS+4*i, value)
        self.uc.reg_write(DR[3], pen & 0xffffffff)
        saved = {reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX], STOP, count=limit)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP, "CPU did not return"
        assert self.a(7) == STACK+4, "stack imbalanced"
        assert self.a(3) == ARGS+12, "three stacked AP20 LONG parameters"
        for reg, prev in saved.items():
            if reg not in (DR[2], DR[3], AR[3]):
                assert self.uc.reg_read(reg) == prev, ("clobbered register", reg)
        assert self.d(2) == 0, "AMOS result must be integer"
        assert self.waits in (0,1)
        return self.d(3)


def run():
    candidate, info = build()
    assert candidate == build()[0], "non-deterministic R43 build"
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok42, seg42, _ = split(BASE.read_bytes())
    tok43, seg43, _ = split(candidate)
    assert len(seg42) == ENTRY_INDEX == 53 and len(seg43) == 54
    assert seg43[:52] == seg42[:52], "historical entries changed"
    assert seg43[52] == seg42[52]+GETP
    assert seg43[53] == emit_circle()[0]
    assert tok43.startswith(tok42[:-6]) and tok43 != tok42
    audit = inspect(parse(candidate))
    assert not audit["issues"], audit["issues"]
    named = [t for t in audit["tokens"] if t["name"].startswith("aga ")]
    assert len(named) == 48
    matches = [t for t in named if t["name"] == "aga circle"]
    assert len(matches) == 1
    assert (matches[0]["instruction"], matches[0]["function"], matches[0]["signature"]) == (1,53,"00,0,0,0")
    assert any(t["index"] == 53 and t["parameters"] == 4 and t["getp"]
               for t in audit["parameter_checks"])

    body, labels = emit_circle()
    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions = list(dis.disasm(body, 0))
    assert sum(i.size for i in instructions) == len(body), "invalid 68000 disassembly"
    starts = {i.address for i in instructions}
    assert all(position in starts for position in labels.values()), labels
    assert all(i.mnemonic not in ("illegal","dc.w","trap") for i in instructions)

    cases = 0
    examples = [
        (160,128,0),(160,128,1),(160,128,2),
        (160,128,3),(160,128,4),(160,128,13),(160,128,36),
        (0,0,0),(0,0,1),(0,0,48),(319,255,0),(319,255,1),
        (319,255,48),(319,0,30),(0,255,30),
        (160,0,50),(160,255,50),(0,128,60),(319,128,60),
        (-12,128,45),(330,128,45),(160,-12,45),(160,266,45),
        (160,128,160),(160,128,260),(160,128,320),
        (160,128,1000),(25,25,35),(300,230,35),
        (20,120,119),(300,120,119),
        (-35,-35,55),(355,285,55),
        (-200,125,210),(530,125,210),
        (120,-200,210),(120,455,210),
        (-32768,128,200), (32767,128,200),
        (160,-32768,200),(160,32767,200),
        (-500,20,50), (900,20,50),
        (20,-500,50), (20,800,50),
    ]
    for depth in (1,2,4,8):
        for front in (0,1):
            for k,(cx,cy,radius) in enumerate(examples):
                pending = (k+depth+front)%4
                pen = (1<<depth)-1 if k%2 else 0
                m = CircleMachine(candidate, depth=depth, front=front,
                                  pending=pending, safe_ready=True)
                before = m.snapshot()
                expected = reference_circle(cx,cy,radius)
                got = m.circle(cx,cy,radius,pen)
                assert got == int(bool(expected)), ("return",k,depth,front,got,len(expected))
                assert set(m.pixels) == expected, ("circle pixels", k, depth, front,
                    len(m.pixels), len(expected), list(set(m.pixels)^expected)[:10])
                assert not m.lines and not m.moves, "DrawEllipse/Move not allowed"
                assert m.waits == int(bool(expected)), ("WaitBlit",k,m.waits)
                verify_bitmap(before,m.snapshot(),expected,pen,depth,m.stride)
                if not m.calls:
                    assert m.get(DB+20) == pending
                else:
                    assert m.get(DB+20) == (pending&~1)
                cases += 1

    # Different logical dimensions and minimal 1x1/2x2 screens.
    for width,height in ((1,1),(1,2),(2,1),(2,2),(13,11),(320,1),(1,256)):
        for cx,cy,radius in ((0,0,0),(0,0,1),(width-1,height-1,0),
                             (width//2,height//2,2),
                             (width//2,height//2,50),(-30,0,31)):
            m = CircleMachine(candidate,width=width,height=height,depth=2)
            before = m.snapshot()
            expected = reference_circle(cx,cy,radius,width,height)
            got = m.circle(cx,cy,radius,3)
            assert got == int(bool(expected)),(width,height,cx,cy,radius,got,len(expected))
            assert set(m.pixels) == expected
            assert m.waits == int(bool(expected))
            verify_bitmap(before,m.snapshot(),expected,3,2,m.stride)
            cases += 1

    # Very large enclosing circle: overlaps screen bounding box but
    # original ring contains no visible pixel. No fake border drawn.
    m = CircleMachine(candidate)
    before = m.snapshot()
    assert m.circle(160,128,32767,3) == 0
    assert not m.pixels and not m.lines and m.waits == 0
    assert m.snapshot() == before
    cases += 1

    # Invalid LONGs/pen must return zero without graphics or Safe calls.
    for changes in (
        dict(cx=32768),dict(cy=32768),dict(cx=-32769),dict(cy=-32769),
        dict(radius=-1),dict(radius=-32768),dict(radius=32768),
        dict(radius=0x7fffffff),dict(radius=-0x80000000),
        dict(cx=0x7fffffff),dict(cy=-0x80000000),
        dict(pen=-1),dict(pen=256),dict(pen=0x7fffffff),
    ):
        m = CircleMachine(candidate)
        before = m.snapshot()
        assert m.circle(**changes) == 0, changes
        assert m.calls == [] and m.snapshot() == before, changes
        cases += 1

    # Safe pending and not delivered: one nonblocking GetMsg, no writing.
    for pending in (1,3):
        m = CircleMachine(candidate,pending=pending,safe_ready=False)
        before = m.snapshot()
        assert m.circle(160,128,30,1) == 0
        assert m.calls == [EXEC-372] and m.waits == 0
        assert m.get(DB+20) == pending and m.snapshot() == before
        cases += 1

    # A wholly offscreen bounding box must not even consume Safe.
    m = CircleMachine(candidate,pending=1,safe_ready=False)
    assert m.circle(-500,20,50,3) == 0 and m.calls == []
    assert m.get(DB+20) == 1
    cases += 1

    for mutant in ("screen","gfx","db","width","height","depth","front",
                   "sb0","sb1","bitmap","stride","rows","bmpdepth","plane","planem1"):
        m = CircleMachine(candidate)
        if mutant=="screen":m.put(STATE,0)
        elif mutant=="gfx":m.put(STATE+8,0)
        elif mutant=="db":m.put(STATE+32,0)
        elif mutant=="width":m.put(STATE+12,0)
        elif mutant=="height":m.put(STATE+16,0)
        elif mutant=="depth":m.put(STATE+28,9)
        elif mutant=="front":m.put(DB+8,2)
        elif mutant=="sb0":m.put(DB,0);m.put(DB+8,1)
        elif mutant=="sb1":m.put(DB+4,0)
        elif mutant=="bitmap":m.put(0x54100,0)
        elif mutant=="stride":m.uc.mem_write(m.expected_bitmap,pack(">H",1))
        elif mutant=="rows":m.uc.mem_write(m.expected_bitmap+2,pack(">H",1))
        elif mutant=="bmpdepth":m.uc.mem_write(m.expected_bitmap+5,bytes([7]))
        elif mutant=="plane":m.put(m.expected_bitmap+8,0)
        elif mutant=="planem1":m.put(m.expected_bitmap+8,-1)
        before=m.snapshot()
        assert m.circle()==0,mutant
        assert m.calls==[] and m.snapshot()==before,mutant
        cases += 1

    m = CircleMachine(candidate,pixel_ok=False)
    before = m.snapshot()
    assert m.circle(160,128,0,1) == 0
    assert len(m.pixels)==1 and m.waits==1 and m.snapshot()==before
    cases += 1

    print("M15/R43 native CPU 68000 Gate A PASS:",cases,"cases")
    print("48 named AP20 commands / 54 segments; R42 frozen entries unchanged")
    print("Eight symmetric octants, zero-radius one pixel, no out-of-bounds writes")
    print("Gate B AMOS/WinUAE, C Compiler and D physical AGA: NOT TESTED")
    print("R43 in-memory SHA256:",info["sha256"],"bytes",info["size"])


if __name__ == "__main__":
    run()
