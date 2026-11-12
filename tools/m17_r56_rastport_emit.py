"""M17/R56: CPU-safe RectFill / SetRast replacement for R55 Blitter Fill.

Native 68000 only. Same full argument/BitMap/Safe validation as R55,
then a temporary stack RastPort with the inactive private BitMap.

SetRast is legal ONLY when x=y=0 and the requested rectangle covers
the *physical* bitmap (BytesPerRow*8 and Rows), not just logical width.
Every other valid rectangle goes through RectFill with inclusive bounds.

Both OS routines have void results; the AMOS 1/0 contract continues to
describe input/Safe validation and successfully issued/synchronized draws,
NOT an unobservable OS internal partial-plane error. Gate B/C required.
"""
from m68k_emit import Code, D, A, M, POST, I
from m12_blit_safe_r27_emit import (
    AMOS_STATE_PTR, SCREEN, GFX, WIDTH, HEIGHT, DEPTH, DBSTATE,
    LVO_WAITBLIT, _emit_safe_guard,
)

LVO_INIT_RP=-198
LVO_SET_RAST=-234
LVO_RECT_FILL=-306
LVO_SET_APEN=-342
LVO_SET_DRMD=-354
RASTPORT_BYTES=128


def emit_fill_r56():
    """Whole Fill code, without AMOS AP20 GetP. D3=pen, A3 pops h,w,y,x."""
    c=Code()
    c.raw("48e7efee")           # original R55 preservation set
    c.move(POST(3),D(5))       # height
    c.move(POST(3),D(4))       # width
    c.move(POST(3),D(1))       # y
    c.move(POST(3),D(0))       # x

    # Untouched R55-style geometry, bitmap and per-plane validation.
    c.move(M(5,AMOS_STATE_PTR),A(4))
    c.move(A(4),D(6)); c.tst(D(6)); c.branch(7,"bad")
    c.move(M(4,SCREEN),D(6)); c.tst(D(6)); c.branch(7,"bad")
    c.move(M(4,DBSTATE),A(2))
    c.move(A(2),D(6)); c.tst(D(6)); c.branch(7,"bad")
    c.move(M(4,GFX),A(6))
    c.move(A(6),D(6)); c.tst(D(6)); c.branch(7,"bad")
    for reg in (0,1,3):
        c.tst(D(reg)); c.branch(11,"bad")
    for reg in (4,5):
        c.tst(D(reg)); c.branch(15,"bad")
    for off in (WIDTH,HEIGHT):
        c.move(M(4,off),D(6)); c.tst(D(6)); c.branch(15,"bad")
        c.imm("cmp",32767,D(6)); c.branch(14,"bad")
    c.move(M(4,WIDTH),D(6)); c.alu("sub",D(4),6)
    c.tst(D(6)); c.branch(11,"bad")
    c.alu("cmp",D(6),0); c.branch(14,"bad")
    c.move(M(4,HEIGHT),D(6)); c.alu("sub",D(5),6)
    c.tst(D(6)); c.branch(11,"bad")
    c.alu("cmp",D(6),1); c.branch(14,"bad")

    c.tst(M(2,8)); c.branch(7,"front_zero")
    c.move(M(2,0),A(0)); c.branch(0,"have_sb")
    c.label("front_zero"); c.move(M(2,4),A(0))
    c.label("have_sb")
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,"bad")
    c.move(M(0,0),A(0))
    c.move(A(0),D(6)); c.tst(D(6)); c.branch(7,"bad")
    c.move(I(0),D(6)); c.move(M(0,0),D(6),"w")
    c.shift(6,3,left=True)
    c.alu("cmp",M(4,WIDTH),6); c.branch(13,"bad")
    c.move(I(0),D(6)); c.move(M(0,2),D(6),"w")
    c.alu("cmp",M(4,HEIGHT),6); c.branch(13,"bad")
    c.move(I(0),D(6)); c.move(M(0,5),D(6),"b")
    c.alu("cmp",M(4,DEPTH),6); c.branch(6,"bad")
    c.tst(D(6)); c.branch(15,"bad")
    c.imm("cmp",8,D(6)); c.branch(14,"bad")

    c.move(D(6),D(2))
    c.move(A(0),A(1)); c.quick(8,A(1))
    c.label("check_plane")
    c.move(POST(1),D(6))
    c.tst(D(6)); c.branch(7,"bad")
    c.imm("cmp",-1,D(6)); c.branch(7,"bad")
    c.quick(1,D(2),sub=True)
    c.branch(6,"check_plane")

    c.move(I(0),D(2)); c.move(M(0,5),D(2),"b")
    c.move(I(1),D(6))
    c.label("compute_limit")
    c.shift(6,1,left=True)
    c.quick(1,D(2),sub=True)
    c.branch(6,"compute_limit")
    c.alu("cmp",D(6),3); c.branch(4,"bad")

    _emit_safe_guard(c)

    # No DMA before Safe. Save position, pen, and BitMap in preserved regs.
    c.move(D(0),D(2))        # x
    c.move(D(1),D(6))        # y
    c.move(D(3),D(7))        # pen
    c.move(A(0),A(4))       # inactive back BitMap
    c.raw("4fefff80")       # LEA -128(SP),SP
    c.move(A(7),A(2))       # stack-owned RastPort
    c.move(A(2),A(1))
    c.call_os(LVO_INIT_RP)
    c.move(A(4),M(2,4))     # RastPort.BitMap

    # Only SetRast when the *PHYSICAL* bitmap will be fully covered.
    # Physical stride may exceed logical W, and physical Rows may exceed H.
    c.tst(D(2)); c.branch(6,"rect_fill")
    c.tst(D(6)); c.branch(6,"rect_fill")
    c.move(I(0),D(0)); c.move(M(4,0),D(0),"w")
    c.shift(0,3,left=True)
    c.alu("cmp",D(4),0); c.branch(6,"rect_fill")
    c.move(I(0),D(0)); c.move(M(4,2),D(0),"w")
    c.alu("cmp",D(5),0); c.branch(6,"rect_fill")
    c.move(D(7),D(0))
    c.move(A(2),A(1))
    c.call_os(LVO_SET_RAST)
    c.branch(0,"blit_wait")

    c.label("rect_fill")
    c.move(A(2),A(1))
    c.move(D(7),D(0))
    c.call_os(LVO_SET_APEN)
    c.move(A(2),A(1))
    c.move(I(0),D(0))       # JAM1 copy (not XOR/Complement)
    c.call_os(LVO_SET_DRMD)
    c.move(D(2),D(0))       # xmin
    c.move(D(6),D(1))       # ymin
    c.alu("add",D(4),2)     # xmax = x+w-1
    c.quick(1,D(2),sub=True)
    c.move(D(6),D(3))
    c.alu("add",D(5),3)     # ymax = y+h-1
    c.quick(1,D(3),sub=True)
    c.move(A(2),A(1))
    c.call_os(LVO_RECT_FILL)

    c.label("blit_wait")
    c.call_os(LVO_WAITBLIT) # must complete before RP stack is released
    c.raw("4fef0080")       # LEA +128(SP),SP, exact stack balance
    c.move(I(1),D(3))
    c.branch(0,"finish")
    c.label("bad")
    c.move(I(0),D(3))
    c.label("finish")
    c.raw("4cdf77f7")
    c.raw("74004e75")
    code=c.out()
    assert len(code)%2==0
    assert c.labels["blit_wait"] < c.labels["finish"]
    return code,c.labels
