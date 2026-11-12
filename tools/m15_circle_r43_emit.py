"""M15/R43: fully clipped, integer midpoint AGA circle outline.

Public AMOS API: _OK=Aga Circle(CX,CY,Radius,Pen).
Only the back buffer of the private indexed AGA screen is writable.
All eight symmetric raster points are individually checked against the logical
screen BEFORE WritePixel. A non-layered DrawEllipse is never invoked.
R42's validated state, Safe, palette index and BitMap guards are preserved.
No persistent allocation, implicit VBL, swap, image bank or WaitPort.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_INDEX = 53
STATE_PTR = 0x01C8
FRAME_SIZE = 160
Y = 128
ERROR = 132
PAINT_ATTEMPTED = 136
BACK_BITMAP = 156

LVO_GETMSG = -372
LVO_INIT_RP = -198
LVO_SET_APEN = -342
LVO_SET_DRMD = -354
LVO_WRITE_PIXEL = -324
LVO_WAIT_BLIT = -228


def emit_circle():
    c = Code()
    # D3=Pen; next numeric arguments on A3: Radius, CY, CX.
    # D7=Pen, D6=Radius, D4=CY, D2=CX, D5=current X.
    c.raw("48e7efee")                 # Preserve original R42 register set.
    c.move(D(3), D(7))
    c.move(POST(3), D(6))
    c.move(POST(3), D(4))
    c.move(POST(3), D(2))
    c.move(I(0), D(3))
    c.raw("4fefff60")                 # LEA -160(SP),SP: 128-byte RP + locals.

    # AMOS LONGs must fit the signed 16-bit public coordinate/radius contract.
    for reg in (2, 4, 6):
        c.imm("cmp", 32767, D(reg))
        c.branch(14, "bad")          # BGT
        c.imm("cmp", -32768, D(reg))
        c.branch(13, "bad")          # BLT
    c.tst(D(6))
    c.branch(11, "bad")              # Radius negative
    c.tst(D(7))
    c.branch(11, "bad")              # Pen negative

    # R42's private-screen and logical-dimension validation.
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    for off in (0, 8, 32):          # Screen*, GfxBase*, DBState*
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(7, "bad")
    for off in (12, 16):            # logical width and height
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(15, "bad")
        c.imm("cmp", 32767, D(0))
        c.branch(14, "bad")

    c.move(M(4, 28), D(0))          # Depth 1..8.
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
    c.branch(4, "bad")              # unsigned Pen >= 2^Depth

    # Only the bounding box may be used for early rejection. It must NOT
    # be clipped into a spurious screen-edge circle.
    for center, dimension, tag in ((2, 12, "x"), (4, 16, "y")):
        c.move(D(center), D(0))
        c.alu("add", D(6), 0)
        c.tst(D(0))
        c.branch(11, "bad")         # (center+radius) < 0
        c.move(D(center), D(0))
        c.alu("sub", D(6), 0)
        c.alu("cmp", M(4, dimension), 0)
        c.branch(12, "bad")         # (center-radius) >= dimension

    # Inactive back buffer; exactly the R42 structural checks.
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
    c.move(A(0), A(2))

    c.move(I(0), D(1))
    c.move(M(0, 0), D(1), "w")     # BytesPerRow * 8 >= width
    c.shift(1, 3, left=True)
    c.alu("cmp", M(4, 12), 1)
    c.branch(13, "bad")
    c.move(I(0), D(1))
    c.move(M(0, 2), D(1), "w")     # Rows >= height
    c.alu("cmp", M(4, 16), 1)
    c.branch(13, "bad")
    c.move(I(0), D(1))
    c.move(M(0, 5), D(1), "b")     # BitMap.Depth == logical Depth
    c.alu("cmp", M(4, 28), 1)
    c.branch(6, "bad")
    c.move(D(1), D(0))
    c.move(A(0), A(1))
    c.quick(8, A(1))
    c.label("plane_check")
    c.move(POST(1), D(1))
    c.tst(D(1))
    c.branch(7, "bad")
    c.imm("cmp", -1, D(1))
    c.branch(7, "bad")
    c.quick(1, D(0), sub=True)
    c.branch(6, "plane_check")
    c.move(A(2), M(7, BACK_BITMAP))

    # Non-blocking Safe guard. No WaitPort and no ReplyMsg on Safe/Disp.
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 1, D(0))
    c.branch(7, "safe")
    c.move(M(0, 12), A(0))
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.raw("2c780004")             # ExecBase
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 0xfffffffe, D(0))
    c.move(D(0), M(0, 20))
    c.label("safe")

    c.move(A(7), A(2))            # Temporary RastPort on stack
    c.move(A(2), A(1))
    c.move(M(4, 8), A(6))
    c.call_os(LVO_INIT_RP)
    c.move(M(7, BACK_BITMAP), M(2, 4))
    c.move(A(2), A(1))
    c.move(D(7), D(0))
    c.call_os(LVO_SET_APEN)
    c.move(A(2), A(1))
    c.move(I(0), D(0))            # JAM1, not XOR
    c.call_os(LVO_SET_DRMD)
    c.move(I(0), M(7, PAINT_ATTEMPTED))

    # Zero radius: exactly ONE WritePixel (no eight identical calls).
    c.tst(D(6))
    c.branch(6, "normal_circle")
    c.move(D(2), D(0))
    c.move(D(4), D(1))
    c.move(I(1), M(7, PAINT_ATTEMPTED))
    c.move(A(2), A(1))
    c.call_os(LVO_WRITE_PIXEL)
    c.tst(D(0))
    c.branch(6, "finish_circle")
    c.move(I(1), D(3))
    c.branch(0, "finish_circle")
    c.label("normal_circle")

    # Midpoint algorithm: x=Radius, y=0, error=1-Radius.
    c.move(D(6), D(5))
    c.move(I(0), M(7, Y))
    c.move(I(1), D(0))
    c.alu("sub", D(6), 0)
    c.move(D(0), M(7, ERROR))
    c.label("circle_loop")

    # Every octant is clipped BEFORE WritePixel. Graphics functions may
    # clobber D0/D1/A0/A1; CX,D2 / CY,D4 / X,D5 / Radius,D6 survive.
    octants = (
        (5, +1, Y, +1), (5, -1, Y, +1),
        (5, +1, Y, -1), (5, -1, Y, -1),
        (Y, +1, 5, +1), (Y, -1, 5, +1),
        (Y, +1, 5, -1), (Y, -1, 5, -1),
    )
    for index, (xsrc, xs, ysrc, ys) in enumerate(octants):
        skip = "point_" + str(index) + "_skip"
        c.move(D(2), D(0))
        c.alu("add" if xs > 0 else "sub",
              D(xsrc) if xsrc == 5 else M(7, Y), 0)
        c.tst(D(0))
        c.branch(11, skip)
        c.alu("cmp", M(4, 12), 0)
        c.branch(12, skip)
        c.move(D(4), D(1))
        c.alu("add" if ys > 0 else "sub",
              D(ysrc) if ysrc == 5 else M(7, Y), 1)
        c.tst(D(1))
        c.branch(11, skip)
        c.alu("cmp", M(4, 16), 1)
        c.branch(12, skip)
        c.move(I(1), M(7, PAINT_ATTEMPTED))
        c.move(A(2), A(1))
        c.call_os(LVO_WRITE_PIXEL)
        c.tst(D(0))
        c.branch(6, skip)         # OS success is exactly zero
        c.move(I(1), D(3))
        c.label(skip)

    # Increment y, update signed 32-bit midpoint error. Decrement x only
    # in the nonnegative-error branch; no implicit 16-bit arithmetic.
    c.quick(1, M(7, Y))
    c.tst(M(7, ERROR))
    c.branch(11, "error_negative") # BMI
    c.quick(1, D(5), sub=True)
    c.move(M(7, Y), D(0))
    c.alu("sub", D(5), 0)
    c.shift(0, 1, left=True)
    c.quick(1, D(0))
    c.branch(0, "adjust_error")
    c.label("error_negative")
    c.move(M(7, Y), D(0))
    c.shift(0, 1, left=True)
    c.quick(1, D(0))
    c.label("adjust_error")
    c.move(M(7, ERROR), D(1))
    c.alu("add", D(0), 1)
    c.move(D(1), M(7, ERROR))
    c.move(M(7, Y), D(0))
    c.alu("cmp", D(5), 0)
    c.branch(15, "circle_loop")   # y <= x

    c.label("finish_circle")
    c.tst(M(7, PAINT_ATTEMPTED))
    c.branch(7, "bad")           # No visible points: no WaitBlit.
    c.call_os(LVO_WAIT_BLIT)
    c.label("bad")
    c.raw("4fef00a0")            # LEA +160(SP),SP
    c.raw("4cdf77f7")            # Restore preserved registers
    c.raw("74004e75")            # D2=0 (integer result), RTS; D3=0/1
    body = c.out()
    assert len(body) % 2 == 0
    return body, c.labels
