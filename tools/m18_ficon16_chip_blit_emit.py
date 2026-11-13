"""M18/P5 native M68000 Chip-cache -> masked/opaque Blitter experiment.

INTERNAL ONLY, no AP20 token yet and NO change to the R61 .Lib.
A0: validated CHIP 288-byte staged slot (32-byte visibility mask + 8 planes).
A1: validated inactive private ScreenBuffer BitMap (8 planes).
A6: valid graphics.library base. D0=X, D1=Y (signed int16),
D3=mode 0 opaque/1 colour-zero mask, D4=logical width, D5=height.
D3 returns 1 for success/no-op, 0 for rejection, D2=0.
A3 untouched, other caller regs preserved, balanced stack.
Requires AP20 wrapper to validate DATA bank/header, ready marker, Safe
and real allocation size BEFORE this core is called.
The core checks MEMF_CHIP on both ends of source slot, 8 dest pointers,
the BitMap geometry and clipping. It does not allocate/release memory,
never refers to front, never calls Swap/WaitVbl, and always WaitBlit
after real DMA. InitRastPort supplies a complete OS RastPort.
"""
from m68k_emit import Code,D,A,M,POST,I

LVO_TYPEOFMEM=-534
LVO_INITRASTPORT=-198
LVO_BLTBITMAPRASTPORT=-606
LVO_BLTMASKBITMAPRASTPORT=-636
LVO_WAITBLIT=-228
MEMF_CHIP=2

# Stack scratch, first 40 bytes source BitMap, 64..191 complete RastPort
F=dict(src=192,dst=196,x=200,y=204,mode=208,width=212,height=216,
       sx=220,sy=224,dx=228,dy=232,w=236,h=240,gfx=244)
FRAME=256

def emit_chip_cache_blit():
    c=Code()
    B,L=c.branch,c.label
    c.raw("48e7efee")            # saved AMOS D0/D1/D4-D7, A0-A2/A4-A6
    c.raw("4fefff00")            # LEA -256(SP),SP
    c.move(A(7),A(4))
    for src,dst in ((A(0),"src"),(A(1),"dst"),(A(6),"gfx"),
                    (D(0),"x"),(D(1),"y"),(D(3),"mode"),
                    (D(4),"width"),(D(5),"height")):
        c.move(src,M(4,F[dst]))
    # Strict pre-validation; don't access invalid pointers or call graphics.
    for key in ("src","dst","gfx"):
        c.move(M(4,F[key]),D(6))
        c.tst(D(6));B(7,"bad")
        c.imm("and",1,D(6));B(6,"bad")
    for key in ("x","y"):
        c.move(M(4,F[key]),D(6))
        c.imm("cmp",-32768,D(6));B(13,"bad")
        c.imm("cmp",32767,D(6));B(14,"bad")
    c.move(M(4,F["mode"]),D(6))
    c.tst(D(6));B(11,"bad")
    c.imm("cmp",1,D(6));B(14,"bad")
    for key in ("width","height"):
        c.move(M(4,F[key]),D(6))
        c.tst(D(6));B(15,"bad")
        c.imm("cmp",4096,D(6));B(14,"bad")
    c.move(M(4,F["src"]),D(6))
    c.imm("add",287,D(6));B(5,"bad")

    # Check screen BitMap: 8 bitplanes, physical size covers logical screen.
    c.move(M(4,F["dst"]),A(0))
    c.move(I(0),D(6))
    c.move(M(0),D(6),"w")
    c.shift(6,3,left=True)
    c.alu("cmp",M(4,F["width"]),6);B(13,"bad")
    c.move(I(0),D(6));c.move(M(0,2),D(6),"w")
    c.alu("cmp",M(4,F["height"]),6);B(13,"bad")
    c.move(I(0),D(6));c.move(M(0,5),D(6),"b")
    c.imm("cmp",8,D(6));B(6,"bad")
    c.move(M(4,F["dst"]),A(1));c.quick(8,A(1))
    c.move(I(8),D(7))
    L("check_dest_planes")
    c.move(POST(1),D(6))
    c.tst(D(6));B(7,"bad")
    c.imm("cmp",-1,D(6));B(7,"bad")
    c.imm("and",1,D(6));B(6,"bad")
    c.quick(1,D(7),sub=True);B(6,"check_dest_planes")

    # Fully offscreen means no DMA, no RastPort Init, no Safe consumption.
    for coord,extent in (("x","width"),("y","height")):
        c.move(M(4,F[coord]),D(6))
        c.alu("cmp",M(4,F[extent]),6);B(12,"ok")
        c.imm("add",16,D(6))
        c.tst(D(6));B(15,"ok")

    # Calculate clipped source/dest rectangle (WORD-safe coordinates).
    for axis in ("x","y"):
        src="s"+axis;dst="d"+axis;sz="w" if axis=="x" else "h"
        limit="width" if axis=="x" else "height"
        c.move(M(4,F[axis]),D(6))
        c.tst(D(6));B(11,"neg_"+axis)
        c.move(I(0),M(4,F[src]))
        c.move(D(6),M(4,F[dst]))
        B(0,"have_"+axis)
        L("neg_"+axis)
        c.move(I(0),M(4,F[dst]))
        c.move(I(0),D(7));c.alu("sub",D(6),7)
        c.move(D(7),M(4,F[src]))
        L("have_"+axis)
        c.move(I(16),D(6))
        c.alu("sub",M(4,F[src]),6)
        c.move(M(4,F[limit]),D(7))
        c.alu("sub",M(4,F[dst]),7)
        c.alu("cmp",D(7),6)
        B(13,"size_"+axis+"_ready")  # BLT, 16-src < remaining dest
        c.move(D(7),D(6))
        L("size_"+axis+"_ready")
        c.tst(D(6));B(15,"ok")
        c.move(D(6),M(4,F[sz]))

    # Reject Fast RAM for any part of the contiguous cache icon.
    # TypeOfMem(address) -> D0, bit1 proves custom-chip DMA reachability.
    c.raw("2c780004")            # MOVEA.L 4.w,A6 : ExecBase
    c.move(M(4,F["src"]),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.imm("and",MEMF_CHIP,D(0));B(7,"bad")
    c.move(M(4,F["src"]),D(6));c.imm("add",287,D(6))
    c.move(D(6),A(1))
    c.call_os(LVO_TYPEOFMEM)
    c.imm("and",MEMF_CHIP,D(0));B(7,"bad")

    # Private source BitMap in stack frame. BytePerRow=2, Rows=16,
    # Flags=0, Depth=8, pad=0, Planes[8] from source+32.
    c.move(I(2,"w"),M(4,0),"w")
    c.move(I(16,"w"),M(4,2),"w")
    c.move(I(0),M(4,4))
    c.move(I(8,"w"),M(4,5),"b")
    c.move(M(4,F["src"]),A(0))
    c.raw("41e80020")           # LEA 32(A0),A0 : first plane
    c.raw("43ec0008")           # LEA 8(A4),A1 : Plane table
    c.move(I(8),D(7))
    L("fill_planes")
    c.move(A(0),POST(1))
    c.raw("41e80020")           # LEA 32(A0),A0
    c.quick(1,D(7),sub=True);B(6,"fill_planes")

    # A real local RastPort, initialized by graphics.library.
    c.move(M(4,F["gfx"]),A(6))
    c.raw("43ec0040")           # LEA 64(A4),A1 : RastPort
    c.call_os(LVO_INITRASTPORT)
    c.raw("43ec0040")
    c.move(M(4,F["dst"]),M(1,4))  # rp_BitMap = inactive private BitMap

    c.move(A(4),A(0))           # source BitMap at frame start
    c.move(M(4,F["sx"]),D(0))
    c.move(M(4,F["sy"]),D(1))
    c.move(M(4,F["dx"]),D(2))
    c.move(M(4,F["dy"]),D(3))
    c.move(M(4,F["w"]),D(4))
    c.move(M(4,F["h"]),D(5))
    c.move(M(4,F["mode"]),D(7))
    c.tst(D(7));B(7,"opaque")
    c.move(I(0xe0),D(6))
    c.move(M(4,F["src"]),A(2)) # chip visibility mask, 32 bytes
    c.call_os(LVO_BLTMASKBITMAPRASTPORT)
    B(0,"wait_blit")
    L("opaque")
    c.move(I(0xc0),D(6))
    c.call_os(LVO_BLTBITMAPRASTPORT)
    L("wait_blit")
    c.move(M(4,F["gfx"]),A(6))
    c.call_os(LVO_WAITBLIT)     # DMA complete before return/Erase Bank
    L("ok")
    c.move(I(1),D(3));B(0,"leave")
    L("bad")
    c.move(I(0),D(3))
    L("leave")
    c.raw("4fef0100")           # LEA +256(SP),SP
    c.raw("4cdf77f7")
    c.raw("74004e75")           # D2=0 ; RTS
    binary=c.out()
    assert binary[:2]==bytes.fromhex("48e7") and binary[-2:]==bytes.fromhex("4e75")
    assert len(binary)%2==0
    return binary,c.labels

if __name__=="__main__":
    from hashlib import sha256
    raw,labels=emit_chip_cache_blit()
    print("M18/P5 CHIP BLITTER CORE UNINSTALLED",len(raw),
          "bytes",sha256(raw).hexdigest(),len(labels),"labels")
