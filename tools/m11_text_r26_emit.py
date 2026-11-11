"""M11/R26: 68000 AMOS function rendering one text line into the AGA back BitMap.

Aga Text(x, baselineY, pen, text$) -> 1 rendered, 0 invalid/not-Safe.
No new screen, no pointers into AMOS graphics and no wait for Safe.
Uses the existing InitRastPort->BitMap pattern of R25 Aga Back Fill.

R25 AP20 ABI: D3=AMOS string descriptor, (A3)+=pen, baselineY, x.
The descriptor is a WORD length followed by text bytes, not a C string.
D3 is result (0/1), D2=0. A3 advances by 12. Hardware SP balanced.
No allocation: a 160-byte temporary stack context holds a 128-byte
RastPort followed by a 12-byte TextExtent structure.

Warning: this new entry protects only its OWN drawing from a pending
dbi_SafeMessage. It does not retrofit that protection into the existing
R25 Blitter commands. Gate A CPU != Gate B WinUAE.
"""
from m68k_emit import Code, D, A, M, POST, I

ENTRY = 36
COUNT = 4
STACK_ARGS = (COUNT - 1) * 4
LVO_GETMSG = -372
LVO_INIT_RP = -198
LVO_TEXT_EXTENT = -690    # V36+, installed AmigaOS V39 for AGA
LVO_SET_APEN = -342
LVO_SET_DRMD = -354
LVO_MOVE = -240
LVO_TEXT = -60
LVO_WAIT_BLIT = -228
RP_STACK = 160
RP_BITMAP = 4
RP_FONT = 52
TEXT_EXTENT_OFF = 128
MAX_CHARS = 128
STATE_PTR = 0x1C8

def emit_text(selected_font=False):
    c = Code()
    c.raw("48e7efee")                  # preserve D0,D1,D4..D7,A0..A2,A4..A6
    c.move(D(3), A(4))               # final string descriptor pointer
    c.move(POST(3), D(7))            # pen
    c.move(POST(3), D(6))            # baselineY
    c.move(POST(3), D(5))            # x
    c.raw("7600")                    # result D3=0 until successful render

    c.move(A(4), D(0))
    c.tst(D(0)); c.branch(7, "bad")
    c.move(I(0), D(4))
    c.move(M(4), D(4), "w")           # AMOS descriptor WORD length
    c.tst(D(4)); c.branch(7, "bad")
    c.imm("cmp", MAX_CHARS, D(4)); c.branch(14, "bad")
    c.quick(2, A(4))                 # first character, NOT zero terminated

    c.tst(D(5)); c.branch(11, "bad") # negative X
    c.tst(D(6)); c.branch(11, "bad") # negative baseline
    c.tst(D(7)); c.branch(11, "bad") # negative pen
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0)); c.tst(D(0)); c.branch(7, "bad")
    c.move(M(2, 0), D(0)); c.tst(D(0)); c.branch(7, "bad")  # screen
    c.move(M(2, 8), D(0)); c.tst(D(0)); c.branch(7, "bad")  # GfxBase
    c.move(M(2, 32), D(0)); c.tst(D(0)); c.branch(7, "bad") # DBState

    for off, reg in ((12, 5), (16, 6)):
        c.move(M(2, off), D(0))
        c.tst(D(0)); c.branch(15, "bad")
        c.imm("cmp", 32767, D(0)); c.branch(14, "bad")
        c.alu("cmp", D(0), reg); c.branch(12, "bad") # >= logical width/height

    c.move(M(2, 28), D(0))          # depth
    c.tst(D(0)); c.branch(15, "bad")
    c.imm("cmp", 8, D(0)); c.branch(14, "bad")
    c.move(I(1), D(1))
    c.label("pen_limit")
    c.shift(1, 1, left=True)
    c.quick(1, D(0), sub=True)
    c.branch(6, "pen_limit")
    c.alu("cmp", D(1), 7)
    c.branch(4, "bad")               # unsigned pen >= 2**depth

    c.move(M(2, 32), A(2))           # DBState (no new persistent state)
    c.move(M(2, 8), D(0))            # front index
    c.tst(D(0)); c.branch(7, "front_zero")
    c.imm("cmp", 1, D(0)); c.branch(6, "bad")
    c.move(M(2, 0), A(0))            # front=1 -> back=SB0
    c.branch(0, "have_sb")
    c.label("front_zero")
    c.move(M(2, 4), A(0))            # front=0 -> back=SB1
    c.label("have_sb")
    c.move(A(0), D(0)); c.tst(D(0)); c.branch(7, "bad")
    c.move(M(0, 0), A(0))            # ScreenBuffer.sb_BitMap
    c.move(A(0), D(0)); c.tst(D(0)); c.branch(7, "bad")
    c.move(A(0), D(2))               # save BitMap across all OS calls

    # Read-only BitMap geometry/planes validation before any graphics call.
    c.move(M(5, STATE_PTR), A(1))
    c.move(I(0), D(1))
    c.move(M(0, 0), D(1), "w")        # BitMap.BytesPerRow
    c.shift(1, 3, left=True)
    c.alu("cmp", M(1, 12), 1)
    c.branch(13, "bad")              # stride bits too small
    c.move(I(0), D(1))
    c.move(M(0, 2), D(1), "w")        # BitMap.Rows
    c.alu("cmp", M(1, 16), 1)
    c.branch(13, "bad")
    c.move(I(0), D(1))
    c.move(M(0, 5), D(1), "b")        # BitMap.Depth
    c.alu("cmp", M(1, 28), 1)
    c.branch(6, "bad")
    c.move(D(1), D(0))               # plane counter
    c.move(A(0), A(1))
    c.quick(8, A(1))                 # BitMap.Planes[0]
    c.label("check_plane")
    c.move(POST(1), D(1))
    c.tst(D(1)); c.branch(7, "bad")
    c.imm("cmp", -1, D(1)); c.branch(7, "bad")
    c.quick(1, D(0), sub=True)
    c.branch(6, "check_plane")

    # Temporary RastPort (+0) and TextExtent (+128), no heap allocations.
    c.raw("4fefff60")               # LEA -160(SP),SP
    c.move(A(7), A(2))              # RastPort
    c.move(A(2), A(1))
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))            # GfxBase
    c.call_os(LVO_INIT_RP)
    c.move(D(2), M(2, RP_BITMAP))   # rp->BitMap = actual back BitMap
    if selected_font:
        # R37 only: resolve the private Screen* -> TextFont* and install
        # it BEFORE TextExtent. Default R26 emission remains byte-identical.
        c.move(M(5, STATE_PTR), A(0))
        c.move(M(0), A(0))            # State.Screen*
        c.word(0x6100)               # BSR.W to R37 private font_query helper
        c.label("r37_query_operand")  # displacement WORD; linked by R37 builder
        c.word(0)
        c.tst(D(0))
        c.branch(7, "r37_default_font")
        c.move(D(0), A(0))            # selected TextFont*
        c.move(A(7), A(1))            # temporary RastPort*
        c.call_os(-66)               # graphics.library/SetFont
        c.label("r37_default_font")
    c.move(M(2, RP_FONT), D(0))
    c.tst(D(0)); c.branch(7, "drop")

    # TextExtent gives a real glyph bounding rectangle (incl. overhang).
    c.move(A(7), A(2))
    c.raw("45ef0080")               # LEA 128(SP),A2 -> TextExtent
    c.move(A(7), A(1))              # RP
    c.move(A(4), A(0))              # character data
    c.move(D(4), D(0))              # count WORD
    c.call_os(LVO_TEXT_EXTENT)
    # Re-check coordinates using relative glyph extents and 32-bit sums.
    for bound_off, position_reg, limit_off, lower in (
        (4, 5, 12, True), (6, 6, 16, True),
        (8, 5, 12, False), (10, 6, 16, False),
    ):
        c.move(M(2, bound_off), D(0), "w")
        c.raw("48c0")                # EXT.L D0 (signed WORD -> LONG)
        c.alu("add", D(position_reg), 0)
        if lower:
            c.tst(D(0)); c.branch(11, "drop")
        else:
            c.move(M(5, STATE_PTR), A(1))
            c.alu("cmp", M(1, limit_off), 0)
            c.branch(12, "drop")      # x+MaxX >= width, y+MaxY >= height
    # Defensive guard against a malformed / empty extent.
    c.move(M(2, 0), D(0), "w")
    c.tst(D(0), "w"); c.branch(7, "drop")
    c.move(M(2, 2), D(0), "w")
    c.tst(D(0), "w"); c.branch(7, "drop")

    # Poll dbi_SafeMessage once; never WaitPort/Wait and NEVER ReplyMsg.
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 1, D(0))
    c.branch(7, "safe")
    c.move(M(0, 12), A(0))           # Safe reply port
    c.move(A(0), D(0)); c.tst(D(0)); c.branch(7, "drop")
    c.raw("2c780004")               # A6=ExecBase at 4.w
    c.call_os(LVO_GETMSG)
    c.tst(D(0)); c.branch(7, "drop") # not safe yet, return 0
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 32), A(0))
    c.move(M(0, 20), D(0))
    c.imm("and", 0xfffffffe, D(0))
    c.move(D(0), M(0, 20))           # preserve Disp pending bit
    c.move(M(5, STATE_PTR), A(0))
    c.move(M(0, 8), A(6))            # restore GfxBase after Exec/GetMsg
    c.label("safe")

    c.move(A(7), A(1))              # RP; A2 currently TextExtent
    c.move(D(7), D(0))
    c.call_os(LVO_SET_APEN)
    c.move(A(7), A(1))
    c.move(I(0), D(0))              # JAM1: transparent background
    c.call_os(LVO_SET_DRMD)
    c.move(A(7), A(1))
    c.move(D(5), D(0))
    c.move(D(6), D(1))
    c.call_os(LVO_MOVE)
    c.move(A(7), A(1))
    c.move(A(4), A(0))
    c.move(D(4), D(0))
    c.call_os(LVO_TEXT)
    c.call_os(LVO_WAIT_BLIT)
    c.move(I(1), D(3))              # success after synchronous completion

    c.label("drop")
    c.raw("4fef00a0")               # LEA +160(SP),SP
    c.label("bad")
    c.raw("4cdf77f7")               # restore D0,D1,D4..D7,A0..A2,A4..A6
    c.raw("74004e75")               # D2=0; RTS, D3 retains result
    raw = c.out()
    assert raw and len(raw) % 2 == 0
    return raw, c.labels
