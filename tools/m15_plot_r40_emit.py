"""M15/R40: native 68000 Aga Plot(X,Y,Pen) on the private AGA back buffer.

AMOS AP20: D3=Pen, (A3)+ gives Y then X, D3=result (1/0), D2=0.
Never draw to the front or AMOS screen, never wait for a pending Safe message.
Uses an InitRastPort stack temporary; no heap allocation or implicit swap/VBL.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY_INDEX = 50
STATE_PTR = 0x01C8
RP_SIZE = 128
LVO_GETMSG = -372
LVO_INIT_RP = -198
LVO_SET_APEN = -342
LVO_SET_DRMD = -354
LVO_WRITE_PIXEL = -324
LVO_WAIT_BLIT = -228


def emit_plot():
    c = Code()
    # Preserve exactly the already verified R26 register set; A3/GetP advances.
    c.raw("48e7efee")
    c.move(D(3), D(7))               # Pen
    c.move(POST(3), D(6))            # Y
    c.move(POST(3), D(5))            # X
    c.move(I(0), D(3))               # default result = 0

    for reg in (5, 6, 7):
        c.tst(D(reg))
        c.branch(11, "bad")         # no negative coords / pen

    # Read the independent extension State, not AMOS's display RastPort.
    c.move(M(5, STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    for off in (0, 8, 32):          # Screen*, GfxBase*, DBState*
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(7, "bad")

    # Inclusive last pixel, exclusive Width/Height; no clipping needed.
    for off, reg in ((12, 5), (16, 6)):
        c.move(M(4, off), D(0))
        c.tst(D(0))
        c.branch(15, "bad")         # width / height must be positive
        c.imm("cmp", 32767, D(0))
        c.branch(14, "bad")
        c.alu("cmp", D(0), reg)
        c.branch(12, "bad")         # x >= width / y >= height

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
    c.branch(4, "bad")              # unsigned Pen >= 2^depth

    # ScreenBuffer.sb_BitMap of the *inactive* Intuition screen buffer.
    c.move(M(4, 32), A(2))
    c.move(M(2, 8), D(0))            # front index
    c.tst(D(0))
    c.branch(7, "front_zero")
    c.imm("cmp", 1, D(0))
    c.branch(6, "bad")
    c.move(M(2, 0), A(0))            # front 1 -> back buffer 0
    c.branch(0, "have_screenbuffer")
    c.label("front_zero")
    c.move(M(2, 4), A(0))            # front 0 -> back buffer 1
    c.label("have_screenbuffer")
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(M(0, 0), A(0))            # sb_BitMap*
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.move(A(0), D(2))               # preserve the BitMap across OS calls

    # Physical BitMap dimensions must cover all logical pixels.
    c.move(I(0), D(1))
    c.move(M(0, 0), D(1), "w")        # BytesPerRow
    c.shift(1, 3, left=True)
    c.alu("cmp", M(4, 12), 1)
    c.branch(13, "bad")             # physical stride too narrow
    c.move(I(0), D(1))
    c.move(M(0, 2), D(1), "w")        # Rows
    c.alu("cmp", M(4, 16), 1)
    c.branch(13, "bad")             # insufficient physical rows
    c.move(I(0), D(1))
    c.move(M(0, 5), D(1), "b")        # BitMap.Depth
    c.alu("cmp", M(4, 28), 1)
    c.branch(6, "bad")
    c.move(D(1), D(0))
    c.move(A(0), A(1))
    c.quick(8, A(1))                 # BitMap.Planes[0]
    c.label("plane_check")
    c.move(POST(1), D(1))
    c.tst(D(1))
    c.branch(7, "bad")
    c.imm("cmp", -1, D(1))
    c.branch(7, "bad")
    c.quick(1, D(0), sub=True)
    c.branch(6, "plane_check")

    # Nonblocking R27 Safe guard: never draw to the old front before Safe.
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 1, D(0))
    c.branch(7, "safe")
    c.move(M(0, 12), A(0))           # SafePort, NOT DispPort
    c.move(A(0), D(0))
    c.tst(D(0))
    c.branch(7, "bad")
    c.raw("2c780004")               # MOVEA.L 4.w,A6 (ExecBase)
    c.call_os(LVO_GETMSG)
    c.tst(D(0))
    c.branch(7, "bad")              # no Safe message -> result 0
    c.move(M(4, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 0xfffffffe, D(0))
    c.move(D(0), M(0, 20))           # clear Safe only, preserve Disp
    c.label("safe")

    # Stack-owned RastPort as in the already WinUAE-tested Aga Text.
    c.raw("4fefff80")               # LEA -128(SP),SP
    c.move(A(7), A(2))
    c.move(A(2), A(1))
    c.move(M(4, 8), A(6))            # graphics.library base
    c.call_os(LVO_INIT_RP)
    c.move(D(2), M(2, 4))            # RastPort.BitMap = inactive BitMap
    c.move(A(7), A(1))
    c.move(D(7), D(0))
    c.call_os(LVO_SET_APEN)
    c.move(A(7), A(1))
    c.move(I(0), D(0))               # JAM1 / copy, not complement/XOR
    c.call_os(LVO_SET_DRMD)
    c.move(A(7), A(1))
    c.move(D(5), D(0))
    c.move(D(6), D(1))
    c.call_os(LVO_WRITE_PIXEL)
    c.tst(D(0))
    c.branch(6, "pixel_failed")     # WritePixel=0 means success!
    c.move(I(1), D(3))
    c.label("pixel_failed")
    c.call_os(LVO_WAIT_BLIT)        # wait before releasing stack RastPort
    c.raw("4fef0080")               # LEA +128(SP),SP

    c.label("bad")
    c.raw("4cdf77f7")               # restore volatile/preserved set
    c.raw("74004e75")               # D2=0; RTS (D3=0/1)
    raw = c.out()
    assert len(raw) % 2 == 0
    return raw, c.labels
