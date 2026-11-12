"""M15/R42 — protected, clipped, inclusive AGA rectangle outline.

AMOS API: _OK=Aga Box(X1,Y1,X2,Y2,Pen). Corner order is irrelevant.
The four ORIGINAL sides are independently clipped: clipping must not
invent borders on the screen edges when the rectangle encloses the screen.
Only 1-pixel JAM1 outlines; no fill, heap allocations or implicit swap/VBL.

Both endpoints of every Move/Draw are checked *inside* the target BitMap.
Degenerate (1-pixel) edges use WritePixel because Move/Draw at identical
coordinates is not guaranteed to draw a dot. Draw is never called outside.
An entirely invisible outline returns zero without consuming Safe.
R41 is the immutable, user-validated source base for AP20 and graphics ABI.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_INDEX = 52
STATE_PTR = 0x01C8
FRAME_SIZE = 160
CLIP_MINX = 128
CLIP_MAXX = 132
CLIP_MINY = 136
CLIP_MAXY = 140
VISIBLE = 152
BACK_BITMAP = 156

LVO_GETMSG = -372
LVO_INIT_RP = -198
LVO_SET_APEN = -342
LVO_SET_DRMD = -354
LVO_WRITE_PIXEL = -324
LVO_MOVE = -240
LVO_DRAW = -246
LVO_WAIT_BLIT = -228


def emit_box():
    c = Code()
    # Preserved R41 register ABI. Five numeric AP20 arguments:
    # D3=Pen, (A3)+=Y2, X2, Y1, X1. D3=result (0/1), D2=0.
    c.raw("48e7efee")
    c.move(D(3), D(7))
    c.move(POST(3), D(6))
    c.move(POST(3), D(5))
    c.move(POST(3), D(4))
    c.move(POST(3), D(2))
    c.move(I(0), D(3))
    c.raw("4fefff60")               # LEA -160(SP),SP

    # No accidental 32->16 truncation in AmigaOS graphics.libraries.
    for reg in (2, 4, 5, 6):
        c.imm("cmp", 32767, D(reg))
        c.branch(14, "bad")         # signed >32767
        c.imm("cmp", -32768, D(reg))
        c.branch(13, "bad")         # signed <-32768
    c.tst(D(7))
    c.branch(11, "bad")

    # Normalize unordered corners. D2=minX, D5=maxX, D4=minY, D6=maxY.
    c.alu("cmp", D(5), 2)
    c.branch(15, "x_ordered")
    c.move(D(2), D(0))
    c.move(D(5), D(2))
    c.move(D(0), D(5))
    c.label("x_ordered")
    c.alu("cmp", D(6), 4)
    c.branch(15, "y_ordered")
    c.move(D(4), D(0))
    c.move(D(6), D(4))
    c.move(D(0), D(6))
    c.label("y_ordered")

    # The same private R40 state and BitMap structural guards.
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    for off in (0, 8, 32):          # Screen*, GfxBase*, DBState*
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(7, "bad")
    for off in (12, 16):            # logical Width/Height in 1..32767
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(15, "bad")
        c.imm("cmp", 32767, D(0))
        c.branch(14, "bad")

    c.move(M(4, 28), D(0))           # depth 1..8
    c.tst(D(0))
    c.branch(15, "bad")
    c.imm("cmp", 8, D(0))
    c.branch(14, "bad")
    c.move(I(1), D(1))
    c.label("pen_limit")
    c.shift(1, 1, left=True)
    c.quick(1, D(0), sub=True)
    c.branch(6, "pen_limit")
    c.alu("cmp", D(1), 7)
    c.branch(4, "bad")              # pen unsigned >= (1<<depth)


    # Bounding rectangle entirely outside? Reject before Safe / graphics calls.
    for maxreg, minreg, off, axis in ((5, 2, 12, "x"), (6, 4, 16, "y")):
        c.tst(D(maxreg))
        c.branch(11, "bad")              # maximum <0
        c.alu("cmp", M(4, off), minreg)
        c.branch(12, "bad")              # minimum >= screen extent

    # Select inactive ScreenBuffer with known front index 0 or 1.
    c.move(M(4, 32), A(2))
    c.move(M(2, 8), D(0))
    c.tst(D(0))
    c.branch(7, "front_zero")
    c.imm("cmp", 1, D(0))
    c.branch(6, "bad")
    c.move(M(2, 0), A(0))
    c.branch(0, "have_sb")
    c.label("front_zero")
    c.move(M(2, 4), A(0))
    c.label("have_sb")
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(0, 0), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(A(0), A(2))              # A2 = back BitMap until RastPort created

    c.move(I(0), D(1))
    c.move(M(0, 0), D(1), "w")       # BytesPerRow
    c.shift(1, 3, left=True)
    c.alu("cmp", M(4, 12), 1)
    c.branch(13, "bad")
    c.move(I(0), D(1))
    c.move(M(0, 2), D(1), "w")       # Rows
    c.alu("cmp", M(4, 16), 1)
    c.branch(13, "bad")
    c.move(I(0), D(1))
    c.move(M(0, 5), D(1), "b")       # BitMap.Depth
    c.alu("cmp", M(4, 28), 1)
    c.branch(6, "bad")
    c.move(D(1), D(0))
    c.move(A(0), A(1))
    c.quick(8, A(1))                # BitMap.Planes[0]
    c.label("plane_check")
    c.move(POST(1), D(1))
    c.tst(D(1))
    c.branch(7, "bad")
    c.imm("cmp", -1, D(1))
    c.branch(7, "bad")
    c.quick(1, D(0), sub=True)
    c.branch(6, "plane_check")
    c.move(A(2), M(7, BACK_BITMAP))


    # Compute the pixel-perfect intersection [min,max] with the BitMap.
    # All four edge endpoints below are built solely from these bounds.
    for minreg, maxreg, off, axis, dstmin, dstmax in (
        (2, 5, 12, "x", CLIP_MINX, CLIP_MAXX),
        (4, 6, 16, "y", CLIP_MINY, CLIP_MAXY),
    ):
        c.move(D(minreg), M(7, dstmin))
        c.tst(D(minreg))
        c.branch(10, axis+"_min_ok")
        c.move(I(0), M(7, dstmin))
        c.label(axis+"_min_ok")
        c.move(D(maxreg), M(7, dstmax))
        c.alu("cmp", M(4, off), maxreg)
        c.branch(13, axis+"_max_ok")
        c.move(M(4, off), D(0))
        c.quick(1, D(0), sub=True)
        c.move(D(0), M(7, dstmax))
        c.label(axis+"_max_ok")

    # A huge rectangle can overlap the BitMap but have all four actual
    # outline edges outside. No newly invented screen-boundary edges.
    c.move(I(0), M(7, VISIBLE))
    for reg, off, side in ((2, 12, "left"), (5, 12, "right"),
                           (4, 16, "top"), (6, 16, "bottom")):
        c.tst(D(reg))
        c.branch(11, side+"_invisible")
        c.alu("cmp", M(4, off), reg)
        c.branch(12, side+"_invisible")
        c.move(I(1), M(7, VISIBLE))
        c.label(side+"_invisible")
    c.tst(M(7, VISIBLE))
    c.branch(7, "bad")

    # Nonblocking SafePort GetMsg. Preserve Disp, do not ReplyMsg or WaitPort.
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 1, D(0))
    c.branch(7, "safe")
    c.move(M(0, 12), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.raw("2c780004")              # MOVEA.L 4.w,A6 (ExecBase)
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 0xfffffffe, D(0))
    c.move(D(0), M(0, 20))
    c.label("safe")


    # Stack RastPort, indexed foreground pen and normal copy mode.
    c.move(A(7), A(2))             # A2 = &stack RastPort
    c.move(A(2), A(1))
    c.move(M(4, 8), A(6))          # graphics.library
    c.call_os(LVO_INIT_RP)
    c.move(M(7, BACK_BITMAP), M(2, 4))  # RastPort.BitMap
    c.move(A(2), A(1))
    c.move(D(7), D(0))
    c.call_os(LVO_SET_APEN)
    c.move(A(2), A(1))
    c.move(I(0), D(0))             # JAM1, no XOR
    c.call_os(LVO_SET_DRMD)


    # Four clipped original sides. Any normal Draw returns 1; a one-point
    # side uses WritePixel, whose AmigaOS success return is exactly zero.
    def horizontal_side(yreg, tag):
        skip = "skip_" + tag
        line = "line_" + tag
        c.tst(D(yreg))
        c.branch(11, skip)
        c.alu("cmp", M(4, 16), yreg)
        c.branch(12, skip)
        c.move(M(7, CLIP_MINX), D(0))
        c.alu("cmp", M(7, CLIP_MAXX), 0)
        c.branch(6, line)
        c.move(A(2), A(1))
        c.move(D(yreg), D(1))
        c.call_os(LVO_WRITE_PIXEL)
        c.tst(D(0))
        c.branch(6, skip)
        c.move(I(1), D(3))
        c.branch(0, skip)
        c.label(line)
        c.move(A(2), A(1))
        c.move(M(7, CLIP_MINX), D(0))
        c.move(D(yreg), D(1))
        c.call_os(LVO_MOVE)
        c.move(A(2), A(1))
        c.move(M(7, CLIP_MAXX), D(0))
        c.move(D(yreg), D(1))
        c.call_os(LVO_DRAW)
        c.move(I(1), D(3))
        c.label(skip)

    def vertical_side(xreg, tag):
        skip = "skip_" + tag
        line = "line_" + tag
        c.tst(D(xreg))
        c.branch(11, skip)
        c.alu("cmp", M(4, 12), xreg)
        c.branch(12, skip)
        c.move(M(7, CLIP_MINY), D(1))
        c.alu("cmp", M(7, CLIP_MAXY), 1)
        c.branch(6, line)
        c.move(A(2), A(1))
        c.move(D(xreg), D(0))
        c.call_os(LVO_WRITE_PIXEL)
        c.tst(D(0))
        c.branch(6, skip)
        c.move(I(1), D(3))
        c.branch(0, skip)
        c.label(line)
        c.move(A(2), A(1))
        c.move(D(xreg), D(0))
        c.move(M(7, CLIP_MINY), D(1))
        c.call_os(LVO_MOVE)
        c.move(A(2), A(1))
        c.move(D(xreg), D(0))
        c.move(M(7, CLIP_MAXY), D(1))
        c.call_os(LVO_DRAW)
        c.move(I(1), D(3))
        c.label(skip)

    horizontal_side(4, "top")
    c.alu("cmp", D(4), 6)
    c.branch(7, "skip_bottom_duplicate")
    horizontal_side(6, "bottom")
    c.label("skip_bottom_duplicate")

    vertical_side(2, "left")
    c.alu("cmp", D(2), 5)
    c.branch(7, "skip_right_duplicate")
    vertical_side(5, "right")
    c.label("skip_right_duplicate")

    c.call_os(LVO_WAIT_BLIT)           # RP stays alive until blitter finishes
    c.label("bad")
    c.raw("4fef00a0")                 # LEA +160(SP),SP
    c.raw("4cdf77f7")                 # R41 register restore
    c.raw("74004e75")                 # D2=0, RTS, D3=success
    raw = c.out()
    assert len(raw) % 2 == 0
    return raw, c.labels
