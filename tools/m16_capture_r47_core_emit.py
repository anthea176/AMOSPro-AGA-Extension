"""M16/R47 experimental 68000 AGAPIC scanline encoder.

This is a genuine CPU/planar/RLE building block, NOT yet the public bank-
creating Aga Image Capture command. No main-library bank management, no AP20
token, no production library patch, no claim of WinUAE/Compiler qualification.

Calling contract (private to prospective capture wrapper):
  A0 = pointer to table of 1..8 planar bitmap addresses (Chip RAM)
  A1 = bounded destination work buffer (Fast or Chip RAM)
  D0 = source X (0..4096)
  D1 = source Y (0..4096)
  D2 = capture width (1..4096), sourceX + width <= 4096
  D3 = bitplane depth (1..8)
  D4 = source BytesPerRow (even 2..65534)
  D5 = transparent index (-1 opaque or 0..(1<<depth)-1)
  D6 = output capacity in bytes (nonnegative)
Return D0 = compressed bytes (>0) or 0 on rejection. Other registers
preserved. On failure output scratch may be partially changed; wrapper
MUST never publish it to a bank. Valid output is a single AGAPIC v1
row RLE stream: repeated 16px groups use repeat packets and distinct
groups use one-group literal packets. Every packet is valid AGAPIC RLE;
the host codec's multi-group literal packing is a separate optimization.
"""
from m68k_emit import Code, D, A, M, POST, I

F = {
    "planes": 0, "start": 4, "out": 8, "limit": 12,
    "x": 16, "y": 20, "width": 24, "depth": 28,
    "stride": 32, "transparent": 36, "rowoff": 40,
    "groups": 44, "groupbytes": 48, "masked": 52,
    "group_index": 56, "pixel": 60, "srcbit": 64,
    "srcoff": 68, "colour": 72, "prev": 76,
    "control": 80, "scratch": 96,
}
FRAME = 160


def emit_scanline_rle():
    c = Code()
    def L(n): c.label(n)
    def B(cc, n): c.branch(cc, n)
    def S(reg, name): c.move(reg, M(2, F[name]))
    def G(name, reg): c.move(M(2, F[name]), reg)
    def SCR(reg):  # LEA scratch(A2),An, valid Motorola 68000
        c.word(0x41ea | (reg << 9))
        c.word(F['scratch'])

    c.raw("48e77ffe")                 # MOVEM.L D1-D7/A0-A6,-(SP)
    c.raw("4fefff60")                 # LEA -160(SP),SP
    c.move(A(7), A(2))                # A2 = frame
    S(A(0), "planes"); S(A(1), "start"); S(A(1), "out")
    S(D(0), "x"); S(D(1), "y"); S(D(2), "width")
    S(D(3), "depth"); S(D(4), "stride"); S(D(5), "transparent")
    c.move(I(0), M(2, F["prev"]))     # no previous RLE packet
    c.move(I(0), D(0))                # fail by default

    G("x", D(1)); c.tst(D(1)); B(11, "fail")
    c.imm("cmp", 4096, D(1)); B(2, "fail")
    G("y", D(1)); c.tst(D(1)); B(11, "fail")
    c.imm("cmp", 4096, D(1)); B(2, "fail")
    G("width", D(1)); c.tst(D(1)); B(15, "fail")
    c.imm("cmp", 4096, D(1)); B(2, "fail")
    c.alu("add", M(2, F["x"]), 1)
    c.imm("cmp", 4096, D(1)); B(2, "fail")
    G("depth", D(1)); c.tst(D(1)); B(15, "fail")
    c.imm("cmp", 8, D(1)); B(2, "fail")
    G("stride", D(1)); c.imm("cmp", 2, D(1)); B(5, "fail")
    c.imm("cmp", 65534, D(1)); B(2, "fail")
    c.move(D(1), D(0)); c.imm("and", 1, D(0)); B(6, "fail")
    G("transparent", D(1))
    c.imm("cmp", -1, D(1)); B(7, "opaque")
    c.tst(D(1)); B(11, "fail")
    G("depth", D(0)); c.move(I(1), D(7))
    L("max_colour")
    c.shift(7, 1, left=True)
    c.quick(1, D(0), sub=True); B(6, "max_colour")
    c.alu("cmp", D(7), 1); B(4, "fail") # D1 >= (1<<depth)
    c.move(I(1), M(2, F["masked"]))
    B(0, "mask_done")
    L("opaque")
    c.move(I(0), M(2, F["masked"]))
    L("mask_done")
    # No zero capacity and no wrapped destination address.
    c.tst(D(6)); B(15, "fail")
    c.move(A(1), D(0))
    c.alu("add", D(6), 0); B(5, "fail")
    S(D(0), "limit")
    # Row offset (no 68020 addressing; MULU.W 68000 generates LONG).
    G("y", D(0)); G("stride", D(1))
    c.word(0xc0c1)                    # MULU.W D1,D0
    S(D(0), "rowoff")
    G("width", D(0)); c.imm("add", 15, D(0))
    c.shift(0, 4, left=False); S(D(0), "groups")
    G("depth", D(0)); c.alu("add", M(2, F["masked"]), 0)
    c.shift(0, 1, left=True); S(D(0), "groupbytes")
    c.move(I(0), M(2, F["group_index"]))

    L("group_loop")
    G("group_index", D(0)); c.alu("cmp", M(2, F["groups"]), 0)
    B(12, "success")
    # Clear scratch (mask WORD when enabled; then depth planar WORDs).
    SCR(4)
    G("groupbytes", D(5)); c.shift(5, 1, left=False)
    L("clear_scratch")
    c.move(I(0, "w"), POST(4), "w")
    c.quick(1, D(5), sub=True); B(6, "clear_scratch")
    c.move(I(0), M(2, F["pixel"]))
    c.move(I(0x8000), D(4))           # current bit in 16px group

    L("pixel_loop")
    G("pixel", D(5)); c.imm("cmp", 16, D(5)); B(12, "rle_group")
    G("group_index", D(0)); c.shift(0, 4, left=True)
    c.alu("add", D(5), 0)             # logical X offset
    c.alu("cmp", M(2, F["width"]), 0); B(12, "rle_group")
    c.alu("add", M(2, F["x"]), 0)
    c.move(D(0), D(1))
    c.shift(1, 3, left=False)
    c.alu("add", M(2, F["rowoff"]), 1); S(D(1), "srcoff")
    c.imm("and", 7, D(0))
    c.move(I(7), D(3)); c.alu("sub", D(0), 3); S(D(3), "srcbit")
    G("planes", A(0))
    SCR(4)
    G("masked", D(0)); c.tst(D(0)); B(7, "no_mask_skip")
    c.quick(2, A(4))
    L("no_mask_skip")
    G("depth", D(5))
    c.move(I(1), D(7))                 # plane weight
    c.move(I(0), D(6))                 # pixel colour

    L("plane_loop")
    c.move(POST(0), A(5))              # plane base address
    c.move(A(5), D(0)); G("srcoff", D(1))
    c.alu("add", D(1), 0)
    c.move(D(0), A(5))
    c.move(I(0), D(0)); c.move(M(5), D(0), "b")
    G("srcbit", D(3))
    c.word(0x0700)                     # BTST D3,D0
    B(7, "plane_off")
    c.move(I(0), D(0)); c.move(M(4), D(0), "w")
    c.alu("or", D(4), 0, "w")
    c.move(D(0), M(4), "w")
    c.alu("or", D(7), 6)
    L("plane_off")
    c.quick(2, A(4))
    c.shift(7, 1, left=True)
    c.quick(1, D(5), sub=True); B(6, "plane_loop")
    S(D(6), "colour")
    G("masked", D(0)); c.tst(D(0)); B(7, "pixel_done")
    G("transparent", D(0))
    G("colour", D(6)); c.alu("cmp", D(0), 6); B(7, "pixel_done")
    SCR(4)
    c.move(I(0), D(0)); c.move(M(4), D(0), "w")
    c.alu("or", D(4), 0, "w")
    c.move(D(0), M(4), "w")
    L("pixel_done")
    c.raw("e24c")                     # LSR.W #1,D4
    G("pixel", D(0)); c.quick(1, D(0)); S(D(0), "pixel")
    B(0, "pixel_loop")

    L("rle_group")
    G("prev", A(4))
    c.move(A(4), D(0)); c.tst(D(0)); B(7, "new_packet")
    SCR(5)
    G("groupbytes", D(5)); c.shift(5, 1, left=False)
    L("compare_group")
    c.move(POST(5), D(0), "w")
    c.alu("cmp", POST(4), 0, "w")
    B(6, "new_packet")
    c.quick(1, D(5), sub=True); B(6, "compare_group")
    G("control", A(4))
    c.move(I(0), D(0)); c.move(M(4), D(0), "b")
    c.imm("cmp", 255, D(0)); B(7, "new_packet")
    c.tst(D(0)); B(6, "inc_repeat")
    c.move(I(0x81, "w"), M(4), "b")    # 2 repeated groups
    B(0, "group_done")
    L("inc_repeat")
    c.quick(1, M(4), size="b")       # counts up to 128 = 0xFF
    B(0, "group_done")

    L("new_packet")
    G("limit", D(0)); G("out", A(4))
    c.alu("sub", A(4), 0)            # remaining bytes
    G("groupbytes", D(5)); c.quick(1, D(5))
    c.alu("cmp", D(5), 0); B(5, "fail")
    S(A(4), "control")
    c.move(I(0, "w"), POST(4), "b")  # 1 literal group
    S(A(4), "prev")
    SCR(5)
    G("groupbytes", D(5)); c.shift(5, 1, left=False)
    L("copy_words")
    c.move(POST(5), POST(4), "w")
    c.quick(1, D(5), sub=True); B(6, "copy_words")
    S(A(4), "out")
    L("group_done")
    G("group_index", D(0)); c.quick(1, D(0))
    S(D(0), "group_index")
    B(0, "group_loop")

    L("success")
    G("out", D(0)); G("start", A(5)); c.alu("sub", A(5), 0)
    B(0, "return")
    L("fail")
    c.move(I(0), D(0))
    L("return")
    c.raw("4fef00a0")                # LEA +160(SP),SP
    c.raw("4cdf7ffe")                # MOVEM.L (SP)+,D1-D7/A0-A6
    c.raw("4e75")                    # RTS
    raw = c.out()
    assert len(raw) % 2 == 0
    return raw, c.labels
