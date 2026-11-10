#!/usr/bin/env python3
"""R24 68000 CPU preflight for stateless Aga Hotspot Hit.

Tests signed 32-bit overflow, start-inclusive/end-exclusive bounds,
negative rectangle origins, invalid points/dimensions, 6-arg AP20 GetP
ABI, intact R23 code/FIFO state, and overlapping-zone priority driven
by the AMOS caller. Never claims WinUAE runtime validation.
"""
import random
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from audit_ap20 import parse, inspect
from ap20_utils import split, digest
from build_m9_hotspot_hit_r24 import (
    build, BASE, LAST_GOOD, BASE_SHA256, LAST_GOOD_SHA256,
    ENTRY, GETP, SIGNATURE,
)
from m9_hotspot_r24_emit import emit_hotspot_hit
from test_m8_mouse_position_r19 import (
    MouseMachine, ARGS, CODE, STACK, STOP, DR, AR, AMOS
)

INT_MIN = -(1<<31)
INT_MAX = (1<<31)-1

class HitMachine(MouseMachine):
    def hit(self, args):
        assert len(args) == 6
        px,py,x,y,w,h = args
        for n in args:
            assert INT_MIN <= n <= INT_MAX, args
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[3], ARGS)
        self.uc.reg_write(AR[5], AMOS)
        for i, value in enumerate((w,y,x,py,px)):
            self.put(ARGS + 4*i, value)
        self.uc.reg_write(DR[3], h & 0xFFFFFFFF)
        saved = {reg: self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY], STOP, count=10000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP, ("No RTS", args)
        assert self.uc.reg_read(AR[7]) == STACK+4, ("SP",args)
        assert self.uc.reg_read(AR[3]) == ARGS + 20, ("A3 GetP",args)
        assert self.uc.reg_read(DR[2]) == 0, ("D2 integer",args)
        for reg, before in saved.items():
            if reg in (DR[2],DR[3],AR[3]):
                continue
            assert self.uc.reg_read(reg) == before, ("ABI",reg,args)
        result = self.uc.reg_read(DR[3])
        assert result in (0,1), (args,result)
        return result

def reference(v):
    px,py,x,y,w,h = v
    return int(px >= 0 and py >= 0 and w > 0 and h > 0
               and x <= px < x+w and y <= py < y+h)

def run():
    binary, meta = build()
    assert binary == build()[0], "non-reproducible candidate"
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    tok_old, old, _ = split(BASE.read_bytes())
    tok_new, new, _ = split(binary)
    assert len(old) == ENTRY and len(new) == ENTRY+1 == 35
    assert new[:ENTRY-1] == old[:ENTRY-1]
    assert new[ENTRY-1] == old[ENTRY-1]+GETP
    assert new[ENTRY-1][-148:-4] == bytes(144), "R23 state/dispatcher moved"
    code, labels = emit_hotspot_hit()
    assert new[ENTRY] == code
    assert tok_old != tok_new and tok_new.startswith(tok_old[:-6])
    audit = inspect(parse(binary))
    assert audit["issues"] == [], audit["issues"]
    rows = [r for r in audit["tokens"] if r["name"] == "aga hotspot hit"]
    assert len(rows) == 1
    assert (rows[0]["instruction"],rows[0]["function"],rows[0]["signature"]) == (
        1, ENTRY, SIGNATURE)
    assert any(x["index"] == ENTRY and x["getp"] and x["parameters"] == 6
               for x in audit["parameter_checks"])
    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    inst = list(dis.disasm(code, 0))
    assert sum(i.size for i in inst) == len(code), "Illegal/unparsed 68000 instructions"
    assert all(x.mnemonic not in ("dc.w","illegal","jsr","bsr","trap") for x in inst)
    boundaries = {i.address for i in inst}
    assert set(labels.values()) <= boundaries, ("branch into extension",labels)

    cases = [
        ((0,0,0,0,320,256),1), ((319,255,0,0,320,256),1),
        ((320,255,0,0,320,256),0), ((319,256,0,0,320,256),0),
        ((0,0,0,0,1,1),1), ((1,0,0,0,1,1),0),
        ((0,1,0,0,1,1),0),
        ((10,20,10,20,50,30),1), ((59,49,10,20,50,30),1),
        ((60,49,10,20,50,30),0), ((59,50,10,20,50,30),0),
        ((9,20,10,20,50,30),0), ((10,19,10,20,50,30),0),
        ((0,0,-10,-20,11,21),1), ((0,0,-10,-20,10,21),0),
        ((0,0,-10,-20,11,20),0), ((0,0,-100,-100,0,100),0),
        ((0,0,-100,-100,101,101),1),
        ((-1,0,-10,-10,100,100),0),
        ((0,-1,-10,-10,100,100),0),
        ((0,0,0,0,0,100),0), ((0,0,0,0,100,0),0),
        ((0,0,0,0,-1,1),0), ((0,0,0,0,1,-1),0),
        ((INT_MAX,INT_MAX,INT_MAX,INT_MAX,1,1),1),
        ((INT_MAX,INT_MAX,INT_MAX,INT_MAX,2,2),1),
        ((INT_MAX,0,INT_MIN,0,INT_MAX,1),0),
        ((0,INT_MAX,0,INT_MIN,1,INT_MAX),0),
        ((0,0,INT_MIN,INT_MIN,INT_MAX,INT_MAX),0),
        ((INT_MAX,INT_MAX,0,0,INT_MAX,INT_MAX),0),
        ((INT_MAX-1,INT_MAX-1,0,0,INT_MAX,INT_MAX),1),
        ((0,0,INT_MAX,INT_MAX,1,1),0),
    ]
    machine = HitMachine(binary)
    for args, want in cases:
        got = machine.hit(args)
        assert got == want == reference(args), ("fixed",args,got,want)
    # A stateless operation works even with no screen/Window, unlike Aga Mouse X.
    machine.put(AMOS+456, 0)
    assert machine.hit((15,25,10,20,20,20)) == 1
    assert machine.hit((-1,-1,10,20,20,20)) == 0

    rnd = random.Random(0xA6A)
    edges = [INT_MIN, INT_MIN+1, -1000000,-32768,-1024,-1,0,1,2,10,
             100,255,256,319,320,639,640,1279,1280,32767,
             1000000,INT_MAX-1,INT_MAX]
    # Exact 68000 execution vs full signed-integer Python model.
    for i in range(360):
        if i%3 == 0:
            args = tuple(rnd.choice(edges) for _ in range(6))
        else:
            x,y = rnd.choice(edges), rnd.choice(edges)
            w,h = (rnd.choice([INT_MIN,0,1,2,32,100,256,INT_MAX]),
                   rnd.choice([INT_MIN,0,1,2,32,100,256,INT_MAX]))
            dx,dy = rnd.randint(-2,257),rnd.randint(-2,257)
            px = max(INT_MIN,min(INT_MAX,x+dx))
            py = max(INT_MIN,min(INT_MAX,y+dy))
            args = (px,py,x,y,w,h)
        got = machine.hit(args)
        want = reference(args)
        assert got == want, ("random",i,args,got,want)
    # Three rectangles, two overlapping: caller controls priority/order.
    zones = [(10,20,20,150,120),(20,100,70,160,110),(30,275,15,25,25)]
    def top_zone(px,py):
        for ident,x,y,w,h in reversed(zones):
            if machine.hit((px,py,x,y,w,h)):
                return ident
        return 0
    for px,py,want in ((25,25,10),(120,90,20),(250,100,20),
                       (275,15,30),(299,39,30),(300,40,0),
                       (0,0,0),(300,100,0)):
        assert top_zone(px,py) == want, (px,py,want)
    count = len(cases) + 2 + 360 + 8
    print("M9 R24 CPU PASS:",count,"geometry/ABI cases; 68000 6-arg GetP +20,"
          " signed32 overflow safe, exclusive edges, 3 overlapping hotspots,"
          " R23 preserved, deterministic HUNK/AP20")
    print("R24 preview",meta)
    print("AMOS interpreted/WinUAE, Compiler, real Amiga: NOT TESTED")

if __name__ == "__main__":
    run()
