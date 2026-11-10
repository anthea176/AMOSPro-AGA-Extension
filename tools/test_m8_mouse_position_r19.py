#!/usr/bin/env python3
"""M8 R19 native 68000 Gate A: logical mouse position, ABI and immutability.

Only Window.MouseX/Y, Window.LeftEdge/TopEdge, Window.WScreen and the
extension's 40-byte state are read. No OS/IDCMP calls in the new routines.
CPU emulator is not a visual/WinUAE/Compiler/real-hardware validation.
"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *

from audit_ap20 import parse, inspect
from ap20_utils import split, digest
from build_m8_mouse_position_r19 import (
    build, mouse_routine, BASE, BASE_SHA256, LAST_GOOD,
    LAST_GOOD_SHA256, ENTRY_X, ENTRY_Y, GETP
)
from test_m5_generic import DR, AR

CODE = 0x100000
AMOS = 0x51000
STATE = 0x50000
SCREEN = 0x56000
WINDOW = 0x58000
ARGS = 0x5a000
STACK = 0xf00000
STOP = 0x10000


class MouseMachine:
    def __init__(self, binary):
        self.p = parse(binary)
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        self.uc.mem_map(0, 0x1000000)
        self.uc.mem_write(CODE, self.p.code)
        self.uc.mem_write(STOP, b"\x4e\x71")
        self.put(AMOS+456, STATE)
        self.put(STATE+0, SCREEN)
        self.put(STATE+12, 320)
        self.put(STATE+16, 256)
        self.put(STATE+36, WINDOW)
        self.put(WINDOW+46, SCREEN)
        self.word(WINDOW+4, 0)
        self.word(WINDOW+6, 0)
        self.word(WINDOW+14, 20)
        self.word(WINDOW+12, 30)

    def put(self, off, val):
        self.uc.mem_write(off, struct.pack(">I", val & 0xFFFFFFFF))

    def get(self, off):
        return struct.unpack(">I", self.uc.mem_read(off, 4))[0]

    def word(self, off, val):
        assert -32768 <= val <= 32767
        self.uc.mem_write(off, struct.pack(">h", val))

    def sample(self, entry):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200 + i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000 + i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], ARGS)
        before={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[entry], STOP, count=5000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP, "No normal RTS"
        assert self.uc.reg_read(AR[7])==STACK+4, "Unbalanced stack"
        for reg, initial in before.items():
            if reg in (DR[2], DR[3]): continue
            assert self.uc.reg_read(reg)==initial, (
                "ABI",reg,initial,self.uc.reg_read(reg))
        assert self.uc.reg_read(DR[2])==0
        value=self.uc.reg_read(DR[3])
        return value-0x100000000 if value&0x80000000 else value

    def x(self): return self.sample(ENTRY_X)
    def y(self): return self.sample(ENTRY_Y)

    def geometry(self,w,h,left=0,top=0):
        self.put(STATE+12,w)
        self.put(STATE+16,h)
        self.word(WINDOW+4,left)
        self.word(WINDOW+6,top)

    def position(self,x,y):
        self.word(WINDOW+14,x)
        self.word(WINDOW+12,y)


def run():
    lib, data=build()
    assert lib==build()[0], "Nondeterministic builder"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    old_tok, old, _ = split(BASE.read_bytes())
    new_tok, new, _ = split(lib)
    assert len(old)==ENTRY_X and len(new)==ENTRY_Y+1
    assert new[:ENTRY_X-1]==old[:ENTRY_X-1]
    assert new[ENTRY_X-1]==old[ENTRY_X-1]+GETP
    assert new[ENTRY_X]==mouse_routine("x")[0]+GETP
    assert new[ENTRY_Y]==mouse_routine("y")[0]
    check=inspect(parse(lib))
    assert check["issues"]==[], check
    for i,name in ((ENTRY_X,"aga mouse x"),(ENTRY_Y,"aga mouse y")):
        found=[x for x in check["tokens"] if x["name"]==name]
        assert len(found)==1
        assert (found[0]["instruction"],found[0]["function"],found[0]["signature"])==(1,i,"0")
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    for raw in (mouse_routine("x")[0],mouse_routine("y")[0]):
        instructions=list(dis.disasm(raw,0))
        assert sum(x.size for x in instructions)==len(raw)
        assert all(x.mnemonic not in ("dc.w","illegal") for x in instructions)
        assert not any(x.mnemonic in ("jsr","bsr") for x in instructions), (
            "R19 getters should not call OS or external helpers")
    cases=0
    for w,h in ((320,256),(640,512),(1280,512),(736,482)):
        m=MouseMachine(lib);m.geometry(w,h)
        for x,y in ((0,0),(1,1),(w-1,h-1),(w//2,h//2),
                    (w-1,0),(0,h-1)):
            m.position(x,y)
            assert m.x()==x and m.y()==y,(w,h,x,y,m.x(),m.y())
            cases+=1
        for x,y,expected_x,expected_y in (
            (-1,0,-1,0),(0,-1,0,-1),
            (w,20,-1,20),(20,h,20,-1),
            (-100,-200,-1,-1),(w+10,h+1,-1,-1),
        ):
            m.position(x,y)
            assert (m.x(),m.y())==(expected_x,expected_y)
            cases+=1
        # Window offset: coordinates are screen-logical, not window-local.
        m.geometry(w,h,12,18)
        m.position(20,30)
        assert (m.x(),m.y())==(32,48)
        cases+=1
        m.position(-12,-18)
        assert (m.x(),m.y())==(0,0)
        cases+=1
        m.position(w-12,h-18)
        assert (m.x(),m.y())==(-1,-1)
        cases+=1
        m.geometry(w,h,-12,-18)
        m.position(20,30)
        assert (m.x(),m.y())==(8,12)
        cases+=1

    for field in ("state","screen","window","wrong_screen","width_zero",
                  "height_zero","width_negative","height_negative"):
        m=MouseMachine(lib)
        if field=="state":m.put(AMOS+456,0)
        elif field=="screen":m.put(STATE,0)
        elif field=="window":m.put(STATE+36,0)
        elif field=="wrong_screen":m.put(WINDOW+46,0x57000)
        elif field=="width_zero":m.put(STATE+12,0)
        elif field=="height_zero":m.put(STATE+16,0)
        elif field=="width_negative":m.put(STATE+12,-1)
        else:m.put(STATE+16,-1)
        x,y=m.x(),m.y()
        if field in ("height_zero","height_negative"):
            assert x==20 and y==-1,field
        elif field in ("width_zero","width_negative"):
            assert x==-1 and y==30,field
        else:
            assert (x,y)==(-1,-1),field
        cases+=1

    # Clipped upper bound is exclusive; no clamping or wrap.
    m=MouseMachine(lib)
    for x,y,ex,ey in ((319,255,319,255),(320,256,-1,-1),
                      (-32768,32767,-1,-1),(32767,-32768,-1,-1)):
        m.position(x,y)
        assert (m.x(),m.y())==(ex,ey)
        cases+=1

    print("M8 R19 CPU PASS:",cases,"cases; signed 16-bit, 320/640/1280,"
          " clipped logical coordinates, shifted Window origin, closed/wrong"
          " screen, ABI D3/D2/A3/SP, original R18 entries unchanged")
    print("R19 candidate",data["size"],"SHA256",data["sha256"])
    print("AMOS interpreted / WinUAE, Compiler and real Amiga: NOT TESTED")


if __name__=="__main__":
    run()
