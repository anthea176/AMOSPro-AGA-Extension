#!/usr/bin/env python3
"""M15/R42 native CPU 68000 Gate A for the inclusive, clipped Aga Box API.

Real 68000 instructions run in Unicorn. Graphics/Exec calls are simulated,
with strict rejection of ANY out-of-bounds Move/Draw/WritePixel. Checks the
exact drawn outline pixel set, all untouched bitplane bytes, 4-side clipping,
reversed corners, degenerate edges, Safe/Disp, invalid state, ABI and AP20.
This is not interpreted AMOS/WinUAE Gate B.
"""
from struct import pack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m15_box_r42 import build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256, ENTRY_INDEX, GETP, API
from m15_box_r42_emit import emit_box
from test_m15_draw_r41 import DrawMachine, raster
from test_m15_plot_r40 import ARGS, SAFE_PORT
from test_m5_generic import CODE, GFX, EXEC, STATE, DB, STACK, STOP, AMOS, DR, AR


def reference_box(x1,y1,x2,y2,width=320,height=256):
    """The four ORIGINAL inclusive outline edges, clipped independently.

    A rectangle surrounding the screen creates NO painted border when its
    original sides all lie outside. Clipping must not invent an extra border.
    """
    xa, xb = sorted((x1,x2))
    ya, yb = sorted((y1,y2))
    pixels=set()
    if xa>=width or xb<0 or ya>=height or yb<0:
        return pixels
    for x in range(max(xa,0),min(xb,width-1)+1):
        if 0<=ya<height:pixels.add((x,ya))
        if 0<=yb<height:pixels.add((x,yb))
    for y in range(max(ya,0),min(yb,height-1)+1):
        if 0<=xa<width:pixels.add((xa,y))
        if 0<=xb<width:pixels.add((xb,y))
    return pixels


class BoxMachine(DrawMachine):
    def os_call(self, uc, address, size, user):
        if address==GFX-240:
            self.calls.append(address)
            assert self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap
            x,y=self.d(0),self.d(1)
            assert 0<=x<self.meta["width"] and 0<=y<self.meta["height"],("unsafe Move",x,y)
            assert len(self.moves)==len(self.lines), "Move without paired Draw"
            self.moves.append((x,y))
            self._ret()
            return
        if address==GFX-246:
            self.calls.append(address)
            assert self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap
            assert len(self.moves)==len(self.lines)+1, "Draw lacks previous Move"
            x,y=self.d(0),self.d(1)
            assert 0<=x<self.meta["width"] and 0<=y<self.meta["height"],("unsafe Draw",x,y)
            sx,sy=self.moves[-1]
            assert (x==sx) != (y==sy), "non-degenerate horizontal/vertical only"
            pts=list(raster(sx,sy,x,y))
            assert all(0<=px<self.meta["width"] and 0<=py<self.meta["height"] for px,py in pts)
            for px,py in pts:self.paint(px,py,self.pen)
            self.lines.append((sx,sy,x,y))
            self._ret()
            return
        # WritePixel (for exactly one visible pixel), WaitBlit and Safe.
        super().os_call(uc,address,size,user)

    def box(self,x1=12,y1=15,x2=286,y2=230,pen=1,limit=160000):
        self.pen=pen
        for i,reg in enumerate(DR):self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]):self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,value in enumerate((y2,x2,y1,x1)):
            self.put(ARGS+4*i,value)
        self.uc.reg_write(DR[3],pen & 0xffffffff)
        saved={reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX],STOP,count=limit)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,"CPU did not return"
        assert self.a(7)==STACK+4,"stack imbalanced"
        assert self.a(3)==ARGS+16,"AP20 GetP must consume 4 stack LONGs"
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,("clobbered reg",reg)
        assert self.d(2)==0
        assert self.waits in (0,1)
        return self.d(3)


def verify_bitmap(before,after,expected,pen,depth,stride):
    masks={}
    for x,y in expected:
        off=y*stride+(x>>3)
        bit=1<<(7-(x&7))
        masks[off]=masks.get(off,0)|bit
        for plane in range(depth):
            assert bool(after[plane][off]&bit)==bool(pen&(1<<plane)),("wrong pixel",x,y,plane)
    for plane in range(depth):
        for off,mask in masks.items():
            assert before[plane][off] & (~mask&255) == after[plane][off] & (~mask&255),("adjacent bits changed",plane,off)
        for off in range(len(before[plane])):
            if off not in masks:
                assert before[plane][off]==after[plane][off],("bitplane modified outside outline",plane,off)


def run():
    candidate, info=build()
    assert candidate==build()[0], "R42 non-deterministic"
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    tok41,seg41,_=split(BASE.read_bytes())
    tok42,seg42,_=split(candidate)
    assert len(seg41)==ENTRY_INDEX==52 and len(seg42)==53
    assert seg42[:51]==seg41[:51], "historical R41 entries modified"
    assert seg42[51]==seg41[51]+GETP
    assert seg42[52]==emit_box()[0]
    assert tok42.startswith(tok41[:-6]) and tok42!=tok41
    a=inspect(parse(candidate))
    assert not a["issues"],a["issues"]
    named=[t for t in a["tokens"] if t["name"].startswith("aga ")]
    assert len(named)==47
    matches=[t for t in named if t["name"]=="aga box"]
    assert len(matches)==1
    assert (matches[0]["instruction"],matches[0]["function"],matches[0]["signature"])==(1,52,"00,0,0,0,0")
    assert any(x["index"]==52 and x["parameters"]==5 and x["getp"] for x in a["parameter_checks"])
    body,labels=emit_box()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    ins=list(dis.disasm(body,0))
    assert sum(i.size for i in ins)==len(body),"invalid 68000 disassembly"
    starts={i.address for i in ins}
    assert all(v in starts for v in labels.values()),labels
    assert all(i.mnemonic not in ("illegal","dc.w","trap") for i in ins)

    cases=0
    examples=[
      (10,10,200,190),(200,190,10,10),
      (0,0,319,255),(319,255,0,0),
      (319,0,0,255),(0,255,319,0),
      (0,0,0,0),(319,255,319,255),
      (50,60,50,180),(50,180,50,60),
      (50,60,180,60),(180,60,50,60),
      (319,0,319,255),(0,0,319,0),
      (-20,-20,340,280),(-32768,-32768,32767,32767),
      (-20,30,340,230),(340,230,-20,30),
      (30,-20,280,300),(280,300,30,-20),
      (-20,-20,200,200),(200,200,-20,-20),
      (140,120,350,300),(350,300,140,120),
      (319,0,320,255),(-1,0,0,255),
      (0,255,319,256),(0,-1,319,0),
      (-32768,128,32767,128),(160,-32768,160,32767),
      (320,5,400,210),(-100,10,-1,245),
      (10,256,290,320),(10,-50,290,-1),
      (-32768,-32768,-1,-1),(32767,32767,32766,32766),
      (0,0,32767,32767),(-32768,0,319,255),
    ]
    for depth in (1,2,4,8):
      for front in (0,1):
        for k,(x1,y1,x2,y2) in enumerate(examples):
            pending,ready=((0,False),(1,True),(2,False),(3,True))[(k+depth+front)%4]
            pen=0 if k%3==0 else (1<<depth)-1
            m=BoxMachine(candidate,depth=depth,front=front,pending=pending,safe_ready=ready)
            before=m.snapshot()
            expected=reference_box(x1,y1,x2,y2)
            got=m.box(x1,y1,x2,y2,pen)
            assert got==int(bool(expected)),(depth,front,k,got,len(expected))
            assert m.waits==int(bool(expected))
            touched=set(m.pixels)
            for a,b,x,y in m.lines:
                touched.update(raster(a,b,x,y))
            assert touched==expected,("incorrect rectangle geometry",depth,front,k,len(touched),len(expected),list(touched^expected)[:10])
            assert len(m.lines)<=4 and len(m.moves)==len(m.lines)
            if expected:
                assert m.get(DB+20)==(pending & ~1)
                assert m.calls.count(EXEC-372)==int(bool(pending&1))
            else:
                assert m.calls==[],"invisible rectangle must avoid Safe and graphics"
                assert m.get(DB+20)==pending
            verify_bitmap(before,m.snapshot(),expected,pen,depth,m.stride)
            cases+=1

    # Small screens and single-pixel rectangles, including reversed corners.
    for w,h in ((1,1),(2,1),(1,2),(2,2),(320,1),(1,256)):
      for shape in ((0,0,w-1,h-1),(w-1,h-1,0,0),(-5,-5,5,5),(w,h,w+3,h+3)):
        m=BoxMachine(candidate,width=w,height=h,depth=2)
        before=m.snapshot()
        exp=reference_box(*shape,w,h)
        assert m.box(*shape,3)==int(bool(exp))
        touched=set(m.pixels)
        for x,y,xx,yy in m.lines:touched.update(raster(x,y,xx,yy))
        assert touched==exp
        verify_bitmap(before,m.snapshot(),exp,3,2,m.stride)
        cases+=1

    # Signed 16-bit reject (no truncation), invalid colors and geometry.
    for args in (
       dict(x1=32768),dict(y1=32768),dict(x2=32768),dict(y2=32768),
       dict(x1=-32769),dict(y1=-32769),dict(x2=-32769),dict(y2=-32769),
       dict(x1=0x7fffffff),dict(y2=-0x80000000),
       dict(pen=-1),dict(pen=256),dict(pen=2147483647),
    ):
        m=BoxMachine(candidate)
        before=m.snapshot()
        assert m.box(**args)==0,args
        assert m.calls==[] and m.snapshot()==before,args
        cases+=1

    # Nonblocking Safe: one GetMsg, no rasterization, bit Disp unchanged.
    for pending in (1,3):
        m=BoxMachine(candidate,pending=pending,safe_ready=False)
        before=m.snapshot()
        assert m.box(-20,-20,100,100,1)==0
        assert m.calls==[EXEC-372] and m.waits==0
        assert m.get(DB+20)==pending and m.snapshot()==before
        cases+=1
    m=BoxMachine(candidate,pending=1,safe_ready=True)
    m.put(DB+12,0)
    assert m.box()==0 and m.calls==[] and m.get(DB+20)==1
    cases+=1

    for mutant in ("screen","gfx","db","width","height","depth","front",
                   "sb0","sb1","bitmap","stride","rows","bmpdepth","plane","planem1"):
        m=BoxMachine(candidate)
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
        assert m.box()==0,mutant
        assert m.calls==[] and m.snapshot()==before,mutant
        cases+=1

    # WritePixel failure for a degenerate point cannot mean success.
    m=BoxMachine(candidate,pixel_ok=False)
    before=m.snapshot()
    assert m.box(25,25,25,25,1)==0
    assert len(m.pixels)>=1 and m.waits==1 and m.snapshot()==before
    cases+=1
    print("M15/R42 native CPU 68000 Gate A PASS:",cases,"cases")
    print("47 named AP20 commands / 53 segments, R41 frozen entries unchanged")
    print("Four original sides clipped, no invented screen border, reversed and degenerate corners safe")
    print("Gate B AMOS/WinUAE, C Compiler, D physical AGA: NOT TESTED")
    print("R42 candidate SHA256:",info["sha256"],"bytes",info["size"])


if __name__=="__main__":
    run()
