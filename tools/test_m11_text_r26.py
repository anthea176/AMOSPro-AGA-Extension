#!/usr/bin/env python3
"""M11/R26 Gate A: execute emitted 68000 code under Unicorn and mock OS ABI.

Checks AP20 mixed string/integer arguments, state/BitMap selection, real
TextExtent bounds, safe-message polling, output calls, 68000 code and immutable
R25/R10. This is NOT a WinUAE, Compiler or physical-Amiga test.
"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m11_text_r26 import (build, BASE, BASE_SHA256, LAST_GOOD,
                               LAST_GOOD_SHA256, ENTRY, GETP, TOKEN, SIGNATURE)
from m11_text_r26_emit import emit_text
from test_m6_blit_copy_r13 import CopyMachine
from test_m5_generic import DR, AR, CODE, GFX, EXEC, AMOS, STATE, DB, BITMAP, STACK, STOP

TEXT_PTR = 0x5e000
ARGS = 0x58000
SAFE_PORT = 0x59000
SAFE_MSG = 0x59100
GFX_CALLS = (-198, -690, -342, -354, -240, -60, -228)
FONT = 0x5d000


class TextMachine(CopyMachine):
    def __init__(self, binary, depth=8, front=0, pending=0, safe_ready=False,
                 font_ok=True, ext=None):
        super().__init__(binary, depth=depth, front=front)
        self.put(DB+12, SAFE_PORT)
        self.put(DB+16, SAFE_PORT+0x100)
        self.put(DB+20, pending)
        self.safe_ready = safe_ready
        self.font_ok = font_ok
        self.ext = ext
        self.calls = []
        self.drawn = False
        self.waits = 0
        self.string = b"AGA TEXT"
        for off in GFX_CALLS:
            self.uc.mem_write(GFX+off, b"\x4e\x75")
        self.uc.mem_write(EXEC-372, b"\x4e\x75")

    def _ret(self, result=0):
        u = self.uc
        u.reg_write(DR[0], result & 0xffffffff)
        u.reg_write(DR[1], 0xdeadbeef)
        u.reg_write(AR[0], 0xbad000)
        u.reg_write(AR[1], 0xbad100)
        pc = self.get(self.a(7))
        u.reg_write(AR[7], self.a(7)+4)
        u.reg_write(UC_M68K_REG_PC, pc)

    def os_call(self, uc, address, size, user):
        if address not in [GFX+v for v in GFX_CALLS] and address != EXEC-372:
            return super().os_call(uc, address, size, user)
        self.calls.append(address)
        if address == GFX-198:
            rp = self.a(1)
            assert STACK-1024 <= rp < STACK
            uc.mem_write(rp, b"\0"*128)
            self.put(rp+52, FONT if self.font_ok else 0)
            uc.mem_write(rp+58, struct.pack(">HH", 8, 8))
            uc.mem_write(rp+62, struct.pack(">H", 6))
            self._ret()
        elif address == GFX-690:
            rp, src, count, target = self.a(1), self.a(0), self.d(0)&0xffff, self.a(2)
            assert STACK-1024<=rp<STACK and target==rp+128
            assert self.get(rp+4)==self.expected_bitmap
            assert bytes(uc.mem_read(src,count))==self.string
            extent = self.ext if self.ext is not None else (count*8,8,0,-6,count*8-1,1)
            uc.mem_write(target, struct.pack(">HHhhhh", *extent))
            self._ret()
        elif address == EXEC-372:
            assert self.a(0)==SAFE_PORT
            assert self.get(DB+20)&1
            self._ret(SAFE_MSG if self.safe_ready else 0)
        elif address == GFX-342:
            assert self.a(1) < STACK and self.d(0)==self.pen
            uc.mem_write(self.a(1)+25,bytes([self.pen]))
            self._ret()
        elif address == GFX-354:
            assert self.d(0)==0                 # JAM1, transparent background
            uc.mem_write(self.a(1)+28,b"\0")
            self._ret()
        elif address == GFX-240:
            assert self.d(0)==self.x and self.d(1)==self.y
            uc.mem_write(self.a(1)+36,struct.pack(">hh",self.x,self.y))
            self._ret()
        elif address == GFX-60:
            assert self.a(0)==TEXT_PTR+2
            assert self.d(0)&0xffff==len(self.string)
            assert bytes(uc.mem_read(self.a(0),len(self.string)))==self.string
            assert self.get(self.a(1)+4)==self.expected_bitmap
            assert self.drawn is False
            self.drawn=True
            self._ret()
        elif address == GFX-228:
            assert self.drawn and self.waits==0
            self.waits+=1
            self._ret()
        else:
            raise AssertionError(hex(address))

    def text(self, x=24, y=34, pen=28, value=b"AGA TEXT"):
        self.x,self.y,self.pen,self.string=x,y,pen,value
        self.uc.mem_write(TEXT_PTR,struct.pack(">H",len(value))+value)
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg,0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS+0,pen)
        self.put(ARGS+4,y)
        self.put(ARGS+8,x)
        self.uc.reg_write(DR[3],TEXT_PTR)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY],STOP,count=100000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4,"hardware SP not balanced"
        assert self.a(3)==ARGS+12,"A3 did not advance +12"
        for reg,original in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==original,("register corrupted",reg)
        assert self.d(2)==0
        assert self.waits==int(self.drawn)
        return self.d(3)


def run():
    candidate, meta=build()
    assert candidate==build()[0]
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    oldtok,old,_=split(BASE.read_bytes())
    newtok,parts,_=split(candidate)
    assert len(old)==ENTRY==36 and len(parts)==37
    assert parts[:35]==old[:35]
    assert parts[35]==old[35]+GETP
    assert parts[36]==emit_text()[0]
    assert newtok.startswith(oldtok[:-6])
    audit=inspect(parse(candidate))
    assert audit["issues"]==[],audit["issues"]
    rows=[r for r in audit["tokens"] if r["name"]==TOKEN]
    assert len(rows)==1
    assert (rows[0]["function"],rows[0]["instruction"],rows[0]["signature"])==(ENTRY,1,SIGNATURE)
    assert any(r["index"]==ENTRY and r["parameters"]==4 and r["getp"] for r in audit["parameter_checks"])
    code, labels=emit_text()
    md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(md.disasm(code,0))
    assert sum(i.size for i in instructions)==len(code),"invalid 68000 encoding"
    boundaries={i.address for i in instructions}
    assert all(off in boundaries for off in labels.values())
    assert all(i.mnemonic not in ("illegal","dc.w","trap") for i in instructions)

    count=0
    for depth in (1,2,4,8):
        for front in (0,1):
            for pending,ready in ((0,False),(1,True),(2,False),(3,True)):
                p=(1<<depth)-1
                m=TextMachine(candidate,depth=depth,front=front,pending=pending,safe_ready=ready)
                assert m.text(pen=p)==1
                assert m.drawn and m.waits==1
                assert m.get(DB+20)==(pending & ~1),pending
                assert m.calls.count(EXEC-372)==int(bool(pending&1))
                assert m.calls[-2:]==[GFX-60,GFX-228]
                count+=1

    for pending in (1,3):
        m=TextMachine(candidate,pending=pending,safe_ready=False)
        assert m.text()==0 and not m.drawn
        assert m.get(DB+20)==pending
        assert m.calls.count(EXEC-372)==1
        count+=1

    for args in (
        dict(x=-1),dict(y=-1),dict(pen=-1),dict(pen=256),
        dict(x=320),dict(y=256),dict(x=300),dict(y=1),
        dict(value=b""),dict(value=b"x"*129),
        dict(x=0,y=0),dict(x=319),dict(y=255),
    ):
        m=TextMachine(candidate)
        assert m.text(**args)==0, args
        assert not m.drawn
        count+=1

    for mutation in ("screen","gfx","db","width","height","depth",
                     "sb0","sb1","bitmap","stride","rows","plane"):
        m=TextMachine(candidate)
        if mutation=="screen":m.put(STATE,0)
        if mutation=="gfx":m.put(STATE+8,0)
        if mutation=="db":m.put(STATE+32,0)
        if mutation=="width":m.put(STATE+12,0)
        if mutation=="height":m.put(STATE+16,0)
        if mutation=="depth":m.put(STATE+28,9)
        if mutation=="sb0":m.put(DB,0);m.put(DB+8,1)
        if mutation=="sb1":m.put(DB+4,0)
        if mutation=="bitmap":m.put(0x54100,0)
        if mutation=="stride":m.uc.mem_write(m.expected_bitmap,struct.pack(">H",1))
        if mutation=="rows":m.uc.mem_write(m.expected_bitmap+2,struct.pack(">H",1))
        if mutation=="plane":m.put(m.expected_bitmap+8,0)
        assert m.text()==0,mutation
        assert not m.drawn,mutation
        count+=1

    for extent in (
        (16,8,-30,-6,15,1),  # left of screen
        (16,8,0,-40,15,1),   # top of screen
        (16,8,0,-6,340,1),   # right of screen
        (16,8,0,-6,15,300), # bottom of screen
    ):
        m=TextMachine(candidate,ext=extent)
        assert m.text()==0,extent
        assert not m.drawn
        count+=1
    m=TextMachine(candidate,font_ok=False)
    assert m.text()==0 and not m.drawn;count+=1

    print("M11/R26 Gate A CPU PASS:",count,"native 68000 ABI/geometry/Safe cases")
    print("M11/R26 in-memory candidate:",meta)
    print("Gate B WinUAE / Compiler / real AGA: NOT TESTED")


if __name__=="__main__":
    run()
