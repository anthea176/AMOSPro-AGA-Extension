"""M15/R41: Aga Draw(X1,Y1,X2,Y2,Pen) — protected AGA line drawing.

Only one new 68000 AP20 command (entry 51). Raster target is the private
unshown AGA ScreenBuffer; Safe is handled without blocking exactly as R40.

Two safe paths:
* ALL FOUR endpoint coordinates inside: graphics.library Move/Draw (fast blitter).
* At least one endpoint outside: integer Bresenham with a bounds check before
  EVERY WritePixel. It preserves original raster-phase while clipping pixels,
  and NEVER calls non-layered Draw/Move with an out-of-bounds coordinate.

Endpoints must be signed 16-bit (Amiga Move/Draw ABI); out-of-range 32-bit
arguments are safely rejected before drawing. Long arithmetic for delta/err
handles the full signed-16 range, with <=65536 Bresenham steps. There is no
implicit swap, wait-VBL, heap allocation or access to ordinary AMOS screens.

AMOS AP20: D3=Pen, (A3)+=Y2,X2,Y1,X1. Result D3 (1 if drawn; 0 otherwise),
D2=0. See R40 for the exact preserved register set.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_INDEX = 51
STATE_PTR = 0x01C8
RP_SIZE = 128
FRAME_SIZE = 160
DX = 128
DY = 132
SX = 136
SY = 140
ERR = 144
E2 = 148
MODE = 152
BACK_BITMAP = 156

LVO_GETMSG = -372
LVO_INIT_RP = -198
LVO_SET_APEN = -342
LVO_SET_DRMD = -354
LVO_WRITE_PIXEL = -324
LVO_MOVE = -240
LVO_DRAW = -246
LVO_WAIT_BLIT = -228


def emit_draw():
    c = Code()
    # Save exactly the R40-tested registers; A3 holds the AMOS param cursor.
    c.raw("48e7efee")
    c.move(D(3), D(7))               # Pen
    c.move(POST(3), D(6))            # Y2
    c.move(POST(3), D(5))            # X2
    c.move(POST(3), D(4))            # Y1
    c.move(POST(3), D(2))            # X1
    c.move(I(0), D(3))               # _OK=0 unless drawing succeeds
    c.raw("4fefff60")               # LEA -160(SP),SP: 128-byte RP + locals

    # Graphics Move/Draw has 16-bit signed coordinates. No implicit
    # 32->16 truncation and no unbounded loops for arbitrary AMOS LONGs.
    for reg in (2, 4, 5, 6):
        c.imm("cmp", 32767, D(reg))
        c.branch(14, "bad")         # > 32767
        c.imm("cmp", -32768, D(reg))
        c.branch(13, "bad")         # < -32768
    c.tst(D(7))
    c.branch(11, "bad")             # negative Pen

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

    # Trivial reject if endpoints both lie on the SAME outside half-plane.
    c.tst(D(2))
    c.branch(10, "x_not_both_neg")
    c.tst(D(5))
    c.branch(11, "bad")
    c.label("x_not_both_neg")
    c.alu("cmp", M(4, 12), 2)
    c.branch(13, "x_not_both_right")
    c.alu("cmp", M(4, 12), 5)
    c.branch(12, "bad")
    c.label("x_not_both_right")
    c.tst(D(4))
    c.branch(10, "y_not_both_neg")
    c.tst(D(6))
    c.branch(11, "bad")
    c.label("y_not_both_neg")
    c.alu("cmp", M(4, 16), 4)
    c.branch(13, "y_not_both_bottom")
    c.alu("cmp", M(4, 16), 6)
    c.branch(12, "bad")
    c.label("y_not_both_bottom")

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

    # Endpoints in bounds => hardware Draw; else pixel-by-pixel safe clipping.
    for reg, off in ((2,12), (5,12), (4,16), (6,16)):
        c.tst(D(reg))
        c.branch(11, "soft_mode")
        c.alu("cmp", M(4, off), reg)
        c.branch(12, "soft_mode")
    c.move(I(1), M(7, MODE))
    c.branch(0, "mode_ready")
    c.label("soft_mode")
    c.move(I(0), M(7, MODE))
    c.label("mode_ready")

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

    c.tst(M(7, MODE))
    c.branch(7, "soft_draw")
    # Fast path: all coordinates inside rectangular BitMap; Draw is safe.
    c.alu("cmp", D(5), 2)
    c.branch(6, "line_move")
    c.alu("cmp", D(6), 4)
    c.branch(6, "line_move")
    # One-point line explicitly uses WritePixel (Draw(x,y)->(x,y) is ambiguous).
    c.move(A(2), A(1))
    c.move(D(2), D(0))
    c.move(D(4), D(1))
    c.call_os(LVO_WRITE_PIXEL)
    c.tst(D(0))
    c.branch(6, "draw_finished")
    c.move(I(1), D(3))
    c.branch(0, "draw_finished")

    c.label("line_move")
    c.move(A(2), A(1))
    c.move(D(2), D(0))
    c.move(D(4), D(1))
    c.call_os(LVO_MOVE)
    c.move(A(2), A(1))
    c.move(D(5), D(0))
    c.move(D(6), D(1))
    c.call_os(LVO_DRAW)
    c.move(I(1), D(3))            # no error code from graphics.library/Draw
    c.branch(0, "draw_finished")

    # Software Bresenham, full signed-16 endpoints, LONG dx/dy/error.
    # Maximum 65536 steps even if both endpoints start far offscreen.
    c.label("soft_draw")
    c.move(D(5), D(0))
    c.alu("sub", D(2), 0)          # raw dx (LONG, no signed16 overflow)
    c.move(I(1), M(7, SX))
    c.tst(D(0))
    c.branch(10, "dx_positive")
    c.move(I(-1), M(7, SX))
    c.move(I(0), D(1))
    c.alu("sub", D(0), 1)
    c.move(D(1), D(0))
    c.label("dx_positive")
    c.move(D(0), M(7, DX))
    c.move(D(6), D(0))
    c.alu("sub", D(4), 0)          # raw dy
    c.move(I(1), M(7, SY))
    c.tst(D(0))
    c.branch(10, "dy_positive")
    c.move(I(-1), M(7, SY))
    c.move(I(0), D(1))
    c.alu("sub", D(0), 1)
    c.move(D(1), D(0))
    c.label("dy_positive")
    c.move(D(0), M(7, DY))
    c.move(M(7, DX), D(0))
    c.alu("sub", M(7, DY), 0)
    c.move(D(0), M(7, ERR))

    c.label("raster_loop")
    c.tst(D(2))
    c.branch(11, "skip_pixel")
    c.alu("cmp", M(4,12), 2)
    c.branch(12, "skip_pixel")
    c.tst(D(4))
    c.branch(11, "skip_pixel")
    c.alu("cmp", M(4,16), 4)
    c.branch(12, "skip_pixel")
    # Only in-bound coordinates ever reach WritePixel!
    c.move(A(2), A(1))
    c.move(D(2), D(0))
    c.move(D(4), D(1))
    c.move(I(2), M(7, MODE))      # mark any attempted pixel, even on OS error
    c.call_os(LVO_WRITE_PIXEL)
    c.tst(D(0))
    c.branch(6, "skip_pixel")
    c.move(I(1), D(3))            # any successfully painted pixel => 1

    c.label("skip_pixel")
    c.alu("cmp", D(5), 2)
    c.branch(6, "advance")
    c.alu("cmp", D(6), 4)
    c.branch(7, "draw_finished")  # last endpoint processed
    c.label("advance")
    c.move(M(7, ERR), D(0))
    c.shift(0, 1, left=True)
    c.move(D(0), M(7, E2))        # 2*err based on OLD err
    c.move(I(0), D(1))
    c.alu("sub", M(7, DY), 1)     # -dy
    c.alu("cmp", D(1), 0)
    c.branch(15, "dont_step_x") # e2 <= -dy
    c.move(M(7, ERR), D(0))
    c.alu("sub", M(7, DY), 0)
    c.move(D(0), M(7, ERR))
    c.move(M(7, SX), D(0))
    c.alu("add", D(0), 2)
    c.label("dont_step_x")
    c.move(M(7, E2), D(0))
    c.alu("cmp", M(7, DX), 0)
    c.branch(12, "dont_step_y") # e2 >= dx
    c.move(M(7, ERR), D(0))
    c.alu("add", M(7, DX), 0)
    c.move(D(0), M(7, ERR))
    c.move(M(7, SY), D(0))
    c.alu("add", D(0), 4)
    c.label("dont_step_y")
    c.branch(0, "raster_loop")

    c.label("draw_finished")
    c.tst(M(7, MODE))
    c.branch(7, "bad")           # invisible line: no blit, no needless wait
    c.call_os(LVO_WAIT_BLIT)      # never release a temp RP during a blit
    c.label("bad")
    c.raw("4fef00a0")             # LEA +160(SP),SP
    c.raw("4cdf77f7")             # restore same registers as R40
    c.raw("74004e75")             # D2=0, RTS; D3 carries _OK
    raw = c.out()
    assert len(raw) % 2 == 0
    return raw, c.labels
