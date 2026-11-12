#!/usr/bin/env python3
"""M15/R41 CPU 68000 Gate A — clipped Aga Draw and preserved R40.

Execute real R41 68000 code with Unicorn and mocked AmigaOS Exec/graphics.
Check exact pixels, 8 octants, all four boundaries, safe vs front buffer,
invalid pointers/geometry, ABI/AP20, deterministic binary and 68000-only opcodes.
This does NOT replace interpreted AMOS/WinUAE Gate B.
"""
from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m15_draw_r41 import (build, BASE, BASE_SHA256, LAST_GOOD,
                                LAST_GOOD_SHA256, ENTRY_INDEX, GETP, API)
from m15_draw_r41_emit import emit_draw
from test_m15_plot_r40 import PlotMachine, ARGS, SAFE_PORT
from test_m5_generic import CODE, GFX, EXEC, STATE, DB, BITMAP, STACK, STOP, AMOS, DR, AR


def raster(x1, y1, x2, y2):
    """Integer Bresenham from original endpoints: no arbitrary endpoint rounding."""
    dx, dy = abs(x2-x1), abs(y2-y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx-dy
    while True:
        yield x1, y1
        if x1 == x2 and y1 == y2:
            return
        e2 = 2*err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


class DrawMachine(PlotMachine):
    def __init__(self, binary, *, width=320, height=256, depth=8, front=0,
                 pending=0, safe_ready=False, pixel_ok=True):
        super().__init__(binary, width=width, height=height, depth=depth,
                         front=front, pending=pending, safe_ready=safe_ready,
                         pixel_ok=pixel_ok)
        self.uc.mem_write(GFX-240, bytes.fromhex("4e75"))
        self.uc.mem_write(GFX-246, bytes.fromhex("4e75"))
        self.moves = []
        self.lines = []
        self.pixels = []
        self.failed_pixels = not pixel_ok

    def paint(self, x, y, pen):
        assert 0 <= x < self.meta["width"], ("unsafe x", x)
        assert 0 <= y < self.meta["height"], ("unsafe y", y)
        offset = y*self.stride + (x>>3)
        mask = 1 << (7-(x&7))
        for plane, pointer in enumerate(self.planes):
            old = self.uc.mem_read(pointer+offset, 1)[0]
            new = (old | mask) if pen & (1<<plane) else (old & (255 ^ mask))
            self.uc.mem_write(pointer+offset, bytes([new]))

    def os_call(self, uc, address, size, user):
        if address == GFX-240:  # Move (within bounds ONLY!)
            self.calls.append(address)
            assert self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap
            x,y=self.d(0),self.d(1)
            assert 0<=x<self.meta["width"] and 0<=y<self.meta["height"]
            self.moves.append((x,y))
            self._ret()
            return
        if address == GFX-246:  # Draw (within bounds ONLY!)
            self.calls.append(address)
            assert self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap
            assert len(self.moves)==1
            x,y=self.d(0),self.d(1)
            assert 0<=x<self.meta["width"] and 0<=y<self.meta["height"]
            a,b=self.moves[-1]
            pts=list(raster(a,b,x,y))
            assert pts and all(0<=px<self.meta["width"] and 0<=py<self.meta["height"]
                               for px,py in pts)
            for px,py in pts:self.paint(px,py,self.pen)
            self.lines.append((a,b,x,y))
            self._ret()
            return
        if address == GFX-324:  # WritePixel (software clipping path)
            self.calls.append(address)
            assert self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap
            x,y=self.d(0),self.d(1)
            self.pixels.append((x,y))
            assert 0<=x<self.meta["width"] and 0<=y<self.meta["height"]
            if not self.failed_pixels:self.paint(x,y,self.pen)
            self._ret(-1 if self.failed_pixels else 0)
            return
        if address == GFX-228:
            self.calls.append(address)
            assert self.lines or self.pixels, "WaitBlit without drawing"
            self.waits+=1
            self._ret()
            return
        # R40 caller-volatility mocks for InitRastPort, SetAPen, SetDrMd, GetMsg.
        super().os_call(uc,address,size,user)

    def draw(self, x1=12,y1=15,x2=286,y2=230,pen=1,limit=5000000):
        self.pen=pen
        for i,reg in enumerate(DR): self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,v in enumerate((y2,x2,y1,x1)):
            self.put(ARGS+4*i,v)
        self.uc.reg_write(DR[3],pen & 0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX],STOP,count=limit)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP, "CPU did not return"
        assert self.a(7)==STACK+4,"stack imbalanced"
        assert self.a(3)==ARGS+16,"GetP arguments must advance 16 bytes"
        for reg,prev in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==prev,("register clobbered",reg)
        assert self.d(2)==0,"AMOS return type must be integer"
        assert self.waits in (0,1)
        return self.d(3)


def run():
    raw,info=build()
    assert raw==build()[0]
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    tok40,seg40,_=split(BASE.read_bytes())
    tok41,seg41,_=split(raw)
    assert len(seg40)==ENTRY_INDEX==51 and len(seg41)==52
    assert seg41[:50]==seg40[:50]
    assert seg41[50]==seg40[50]+GETP
    assert seg41[51]==emit_draw()[0]
    assert tok41.startswith(tok40[:-6]) and tok41!=tok40
    audit=inspect(parse(raw))
    assert not audit["issues"],audit["issues"]
    named=[v for v in audit["tokens"] if v["name"].startswith("aga ")]
    assert len(named)==46
    t=[v for v in named if v["name"]==API[0][0]]
    assert len(t)==1 and (t[0]["instruction"],t[0]["function"],t[0]["signature"])==(1,51,"00,0,0,0,0")
    assert any(v["index"]==51 and v["parameters"]==5 and v["getp"]
               for v in audit["parameter_checks"])
    machine,labels=emit_draw()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(dis.disasm(machine,0))
    assert sum(i.size for i in instructions)==len(machine),"not strict 68000"
    boundaries={i.address for i in instructions}
    assert all(i in boundaries for i in labels.values()), labels
    assert all(i.mnemonic not in ("illegal","dc.w","trap") for i in instructions)

    examples=[
        (0,0,319,255),(319,255,0,0),
        (0,255,319,0),(319,0,0,255),
        (0,128,319,128),(319,128,0,128),
        (160,0,160,255),(160,255,160,0),
        (0,0,0,0),(319,255,319,255),
        (130,100,133,102),(133,102,130,100),
        (130,100,132,103),(132,103,130,100),
        (130,100,127,102),(127,102,130,100),
        (130,100,128,97),(128,97,130,100),
        (-20,128,340,128),(340,128,-20,128),
        (160,-40,160,295),(160,295,160,-40),
        (-8,-8,330,260),(330,260,-8,-8),
        (-8,260,330,-8),(330,-8,-8,260),
        (-30,100,150,250),(150,250,-30,100),
        (100,-30,250,150),(250,150,100,-30),
        (300,130,400,210),(400,210,300,130),
        (-10,1,1,-10),(-10,0,-1,10),
        (-1024,128,1024,128),(1024,128,-1024,128),
    ]
    cases=0
    for depth in (1,2,4,8):
        for front in (0,1):
            for k,(x1,y1,x2,y2) in enumerate(examples):
                pending,ready=((0,False),(1,True),(2,False),(3,True))[(k+depth+front)%4]
                pen=(1<<depth)-1 if k%2 else 0
                m=DrawMachine(raw,depth=depth,front=front,pending=pending,safe_ready=ready)
                before=m.snapshot()
                expected=[(x,y) for x,y in raster(x1,y1,x2,y2)
                          if 0<=x<m.meta["width"] and 0<=y<m.meta["height"]]
                ok=m.draw(x1,y1,x2,y2,pen)
                assert ok==int(bool(expected)),(k,depth,front,pending,ok,len(expected))
                assert m.waits==int(bool(expected))
                if expected:
                    is_fast=all(0<=x<m.meta["width"] and 0<=y<m.meta["height"]
                                for x,y in ((x1,y1),(x2,y2)))
                    if is_fast and (x1,y1)!=(x2,y2):
                        assert m.lines==[(x1,y1,x2,y2)] and not m.pixels
                    else:
                        assert m.pixels==expected and not m.lines
                    assert m.get(DB+20)==(pending & ~1)
                    assert m.calls.count(EXEC-372)==int(bool(pending&1))
                else:
                    assert not m.lines and not m.pixels and m.waits==0
                    assert m.get(DB+20)==pending
                # Byte-accurate validation for every plane, all untouched
                # pixels preserved, and selected Pen applied to every hit.
                after=m.snapshot()
                touched=set(expected)
                for x,y in touched:
                    offset=y*m.stride+(x>>3)
                    bit=1<<(7-(x&7))
                    for plane in range(depth):
                        assert bool(after[plane][offset]&bit)==bool(pen&(1<<plane))
                mask_by_offset={}
                for x,y in touched:
                    offset=y*m.stride+(x>>3)
                    mask_by_offset[offset]=mask_by_offset.get(offset,0)|(1<<(7-(x&7)))
                for plane in range(depth):
                    for off,mask in mask_by_offset.items():
                        assert (before[plane][off]&(~mask&255))==(after[plane][off]&(~mask&255))
                    assert all(before[plane][off]==after[plane][off]
                               for off in range(len(before[plane])) if off not in mask_by_offset)
                cases+=1

    # Same half-plane: rejected before RP or Safe consumption.
    for xy in [(-10,10,-1,20),(320,10,400,20),
               (10,-15,25,-1),(10,256,25,300),
               (-32768,-32768,-32767,-32767),
               (32767,32767,32766,32766)]:
        m=DrawMachine(raw)
        before=m.snapshot()
        assert m.draw(*xy,1)==0 and not m.calls and not m.lines
        assert m.snapshot()==before
        cases+=1

    # Invalid 32-bit coordinates and 8-bit indexed pen.
    for kwargs in [
        dict(x1=32768),dict(y1=32768),dict(x2=32768),dict(y2=32768),
        dict(x1=-32769),dict(y1=-32769),dict(x2=-32769),dict(y2=-32769),
        dict(x1=0x7fffffff),dict(y2=-0x80000000),
        dict(pen=-1),dict(pen=256),
    ]:
        m=DrawMachine(raw)
        before=m.snapshot()
        assert m.draw(**kwargs)==0,kwargs
        assert m.calls==[] and m.snapshot()==before,kwargs
        cases+=1

    # Unavailable Safe (including Disp set) never blocks or draws.
    for pending in (1,3):
        m=DrawMachine(raw,pending=pending,safe_ready=False)
        before=m.snapshot()
        assert m.draw(-20,20,120,80,1)==0
        assert m.calls==[EXEC-372]
        assert m.get(DB+20)==pending
        assert m.snapshot()==before
        cases+=1

    # No SafePort => no GetMsg (and no draw).
    m=DrawMachine(raw,pending=1,safe_ready=True)
    m.put(DB+12,0)
    assert m.draw()==0 and m.calls==[]
    cases+=1

    for mutant in ("screen","gfx","db","width","height","depth","front",
                   "sb0","sb1","bitmap","stride","rows","bmpdepth","plane","planem1"):
        m=DrawMachine(raw)
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
        assert m.draw()==0,mutant
        assert m.calls==[] and m.snapshot()==before,mutant
        cases+=1

    # In-bound single point, mocked OS WritePixel failure must give zero.
    m=DrawMachine(raw,pixel_ok=False)
    before=m.snapshot()
    assert m.draw(25,25,25,25,1)==0
    assert len(m.pixels)==1 and m.waits==1 and before==m.snapshot()
    cases+=1
    print("M15/R41 native 68000 Gate A PASS:",cases,"cases")
    print("AP20 46 named commands / 52 segments; R40 frozen entries intact")
    print("Strict 68000 / bounds-safe fast Move-Draw and software clipped Bresenham")
    print("Gate B WinUAE / C Compiler / D real AGA: NOT TESTED")
    print("R41 in-memory SHA256",info["sha256"],"size",info["size"])


if __name__=="__main__":
    run()
