#!/usr/bin/env python3
"""R56 Gate A: native real 68000 RastPort Fill/Clear, Safe, ABI and pixels.

Mocks graphics.library; CPU tests DO NOT establish actual AmigaOS/WinUAE
rendering or real speedup. R55 and R54 artifacts remain unchanged.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack,unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC

from audit_ap20 import inspect,parse
from compiler_relocation import (
    native_from_promoted,unwrap_native_parts,unpack_ap20,is_compiler_wrapped,
)
from build_m17_r56_rastport import build,TITLE
from build_m17_blit_group_r55 import build as build_r55
from m17_r56_rastport_emit import emit_fill_r56
from test_m12_blit_safe_r27 import SafeMixin,SafeCopyMachine
from test_m6_blit_fill_r14 import FillMachine,expected_fill
from test_m6_blit_clear_r15 import ClearMachine
from test_m5_generic import (
    Machine,DR,AR,GFX,EXEC,DB,BITMAP,CODE,STATE
)


class RastMachine(SafeMixin,FillMachine):
    run_clear=ClearMachine.run_clear

    def __init__(self,*args,physical_exact=False,pending=0,safe_ready=False,
                 port_valid=True,**kwargs):
        super().__init__(*args,pending=pending,safe_ready=safe_ready,
                         port_valid=port_valid,**kwargs)
        self.pixels_calls=[]
        self.pending_pixels=None
        self.rp=None
        self.apen=None
        self.draw_mode=None
        self.physical_exact=physical_exact
        # Existing legacy test fixture deliberately has 8 extra bytes/row.
        # Test both padded geometry (RectFill) and exact geometry (SetRast).
        if physical_exact:
            rowbytes=self.meta["row_bytes"]
            self.uc.mem_write(BITMAP,pack(">H",rowbytes))
            self.uc.mem_write(BITMAP+0x100,pack(">H",rowbytes))
            self.stride=rowbytes
            self.plane_size=rowbytes*self.meta["height"]
        for off in (-198,-234,-306,-342,-354):
            self.uc.mem_write(GFX+off,b"\x4e\x75")

    def apply_pixels(self):
        assert self.pending_pixels is not None
        mode,x,y,w,h,pen=self.pending_pixels
        assert mode in ("rect","setrast")
        for plane,address in enumerate(self.planes):
            after=bytearray(self.uc.mem_read(address,self.plane_size))
            for yy in range(y,y+h):
                for xx in range(x,x+w):
                    pos=yy*self.stride+(xx>>3)
                    bit=1<<(7-(xx&7))
                    if pen&(1<<plane):
                        after[pos]|=bit
                    else:
                        after[pos]&=255^bit
            self.uc.mem_write(address,bytes(after))
        self.pending_pixels=None

    def return_os(self,uc):
        # Strict SysV/Amiga style: D0/D1/A0/A1 trashed; D2-D7 and A2-A6 kept.
        uc.reg_write(DR[0],0xdead9999)
        uc.reg_write(DR[1],0xdeadbeef)
        uc.reg_write(AR[0],0xbad000)
        uc.reg_write(AR[1],0xbad100)
        pc=self.get(self.a(7))
        uc.reg_write(AR[7],self.a(7)+4)
        uc.reg_write(UC_M68K_REG_PC,pc)

    def os_call(self,uc,address,size,user):
        if address==GFX-198:
            rp=self.a(1)
            assert rp>0xEFFE00 and rp<0xF00000
            self.rp=rp
            self.uc.mem_write(rp,bytes(128)) # InitRastPort defaults
            self.return_os(uc)
            return
        if address in (GFX-234,GFX-306,GFX-342,GFX-354):
            assert self.rp is not None and self.a(1)==self.rp
            assert self.get(self.rp+4)==self.expected_bitmap, "wrong back BitMap"
            if address==GFX-342:
                self.apen=self.d(0)&255
            elif address==GFX-354:
                self.draw_mode=self.d(0)&255
                assert self.draw_mode==0, "Only JAM1 supported"
            elif address==GFX-306:
                assert self.apen is not None and self.draw_mode==0
                x,y,xmax,ymax=(self.d(i) for i in range(4))
                assert x<=xmax and y<=ymax
                assert xmax<self.meta["width"] and ymax<self.meta["height"]
                assert self.pending_pixels is None, "async draw overlap"
                self.pending_pixels=("rect",x,y,xmax-x+1,ymax-y+1,self.apen)
                self.pixels_calls.append(self.pending_pixels)
            else:
                assert self.physical_exact,"SetRast cannot affect physical padding"
                pen=self.d(0)&255
                assert self.pending_pixels is None, "async SetRast overlap"
                self.pending_pixels=("setrast",0,0,self.stride*8,
                                     self.meta["height"],pen)
                self.pixels_calls.append(self.pending_pixels)
            self.return_os(uc)
            return
        if address==GFX-228:
            assert self.pending_pixels is not None,"WaitBlit without queued draw"
            self.waits+=1
            self.apply_pixels()
            return Machine.os_call(self,uc,address,size,user)
        if address==EXEC-372:
            return SafeMixin.os_call(self,uc,address,size,user)
        return Machine.os_call(self,uc,address,size,user)


def preflight():
    raw,meta=build()
    assert build()[0]==raw
    prev,_=build_r55()
    assert sha256(raw).hexdigest()==meta["sha256"]
    assert is_compiler_wrapped(raw)
    oldtok,old=unwrap_native_parts(prev)
    tok,parts=unwrap_native_parts(raw)
    assert tok==oldtok
    assert len(parts)==len(old)==59
    assert len(unpack_ap20(raw)[1])==60
    assert all(parts[i]==old[i] for i in range(59) if i not in (20,58))
    assert parts[20][4:]==old[20][4:]
    assert parts[21]==old[21] and parts[19]==old[19]
    assert parts[58].startswith(old[58])
    fill,labels=emit_fill_r56()
    assert parts[58]==old[58]+fill
    assert meta["labels"]==labels
    assert meta["new_code_size"]==len(fill)
    starts=[];off=0
    for p in old:
        starts.append(off);off+=len(p)
    assert starts[20]+2+unpack_from(">h",parts[20],2)[0]==off
    assert starts[21]+24+unpack_from(">h",parts[21],24)[0]==starts[20]
    assert len(unpack_ap20(raw)[1][-1])<32768
    assert unpack_ap20(raw)[1][:-1]==unpack_ap20(prev)[1][:-1]
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    inst=list(dis.disasm(fill,0))
    assert sum(x.size for x in inst)==len(fill)
    assert all(x.mnemonic not in ("dc.w","illegal","trap") for x in inst)
    boundaries={x.address for x in inst}
    assert all(x in boundaries for x in labels.values())
    for lvo in (-198,-234,-306,-342,-354,-228):
        assert bytes.fromhex("4eae")+pack(">h",lvo) in fill, lvo
    assert not (bytes.fromhex("4eaeffe2") in fill),"R56 unexpected BltBitMap"
    assert inspect(parse(raw))["issues"]==[]
    native=native_from_promoted(raw,TITLE)
    assert inspect(parse(native))["issues"]==[]
    return native,meta


def run():
    native,meta=preflight()
    cases=0
    for depth in range(1,9):
        full=(1<<depth)-1
        pens=sorted(set((0,1,full//2,full,full^(1<<(depth-1)))))
        for front in (0,1):
            for pen in pens:
                m=RastMachine(native,depth=depth,front=front)
                before=m.snapshot()
                args=(11,17,9,5,pen)
                assert m.run_fill(*args)==1, (depth,front,pen)
                assert m.pixels_calls==[("rect",*args)]
                assert m.waits==1 and m.pending_pixels is None
                for plane in range(depth):
                    assert m.snapshot()[plane]==expected_fill(
                        before[plane],*args,plane,m.stride)
                cases+=1
            m=RastMachine(native,depth=depth,front=front)
            before=m.snapshot()
            assert m.run_clear(7,13,6,4)==1
            assert m.pixels_calls==[("rect",7,13,6,4,0)]
            assert m.waits==1 and m.pending_pixels is None
            for plane in range(depth):
                assert m.snapshot()[plane]==expected_fill(
                    before[plane],7,13,6,4,0,plane,m.stride)
            cases+=1
            for pen in sorted(set((0,full,full//2))):
                m=RastMachine(native,depth=depth,front=front,physical_exact=True)
                before=m.snapshot()
                assert m.run_fill(0,0,320,256,pen)==1
                assert m.pixels_calls==[("setrast",0,0,320,256,pen)]
                assert m.waits==1 and m.pending_pixels is None
                for plane in range(depth):
                    assert m.snapshot()[plane]==expected_fill(
                        before[plane],0,0,320,256,pen,plane,m.stride)
                cases+=1
            m=RastMachine(native,depth=depth,front=front,physical_exact=True)
            assert m.run_clear(0,0,320,256)==1
            assert m.pixels_calls==[("setrast",0,0,320,256,0)]
            assert m.waits==1 and m.pending_pixels is None
            cases+=1

    # Logical full screen but larger physical Bitmap => MUST use RectFill.
    for depth in (1,5,8):
        m=RastMachine(native,depth=depth,physical_exact=False)
        before=m.snapshot()
        assert m.run_clear(0,0,320,256)==1
        assert m.pixels_calls==[("rect",0,0,320,256,0)]
        assert m.waits==1
        for plane in range(depth):
            assert m.snapshot()[plane]==expected_fill(
                before[plane],0,0,320,256,0,plane,m.stride)
        cases+=1

    # All Safe checks BEFORE InitRastPort or drawing.
    for dep in (1,5,8):
        for pending,ready,want in ((0,False,1),(1,False,0),(1,True,1),
                                   (2,False,1),(3,False,0),(3,True,1)):
            m=RastMachine(native,depth=dep,pending=pending,safe_ready=ready)
            before=m.snapshot()
            assert m.run_fill(15,23,7,9,(1<<dep)-1)==want
            assert m.safe_calls==int(bool(pending&1))
            assert m.get(DB+20)==(pending & ~1 if want else pending)
            assert len(m.pixels_calls)==(1 if want else 0)
            assert m.waits==(1 if want else 0)
            if not want:
                assert m.rp is None and m.snapshot()==before
            cases+=1
        m=RastMachine(native,depth=dep,pending=3,safe_ready=True,
                      port_valid=False)
        original=m.snapshot()
        assert m.run_clear(1,2,8,9)==0
        assert not m.pixels_calls and m.rp is None and not m.waits
        assert m.snapshot()==original
        cases+=1

    # Bounds/pen invalid never consume Safe, and never draw.
    bad=((0,0,0,10,1),(0,0,10,0,1),(-1,0,10,10,1),
         (0,-1,10,10,1),(310,0,20,10,1),
         (0,250,10,20,1),(0,0,10,10,-1),(0,0,10,10,256),
         (0x7fffffff,0,10,10,1))
    for args in bad:
        m=RastMachine(native,depth=8,pending=3,safe_ready=True)
        before=m.snapshot()
        assert m.run_fill(*args)==0,args
        assert not m.safe_calls and not m.pixels_calls and m.rp is None
        assert m.snapshot()==before and not m.waits
        cases+=1

    # Reject invalid destination plane pointers before touching Safe.
    m=RastMachine(native,depth=5,pending=3,safe_ready=True)
    from test_m5_generic import BITMAP
    m.put(BITMAP+0x100+8+2*4,0)
    before=m.snapshot()
    assert m.run_fill(13,17,19,23,7)==0
    assert not m.pixels_calls and not m.safe_calls
    assert before==m.snapshot()
    cases+=1

    # Copy remains byte-for-byte R54 and executable unchanged.
    m=SafeCopyMachine(native,depth=4,pending=0)
    assert m.run_copy((2,3,40,50,16,10))==1
    assert len(m.blits)==m.waits==1
    cases+=1
    print("R56 CPU/ABI/Safe/RastPort/SetRast/RectFill Gate A PASS",
          cases,"cases; unpromoted",meta["size"],"bytes",
          meta["sha256"],flush=True)
    print("R56 WinUAE interpreted / AMOS Compiler / real Amiga: NOT TESTED",
          flush=True)


if __name__=="__main__":
    run()
