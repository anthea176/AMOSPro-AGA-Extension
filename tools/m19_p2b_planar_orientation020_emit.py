#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Private P2b planar materializer for prevalidated, disjoint buffers.

A0 source, A1 destination, D0 width, D1 height, D4 number of planes (1..9),
D5 orientation (0 normal, 1 H, 2 V, 3 HV), D6/D7 source/destination capacity.
AGBO layout: word-aligned rows, whole colour planes, optional mask plane last.
The caller validates the AGBO image, ownership, lifetimes and mapped spans.
The destination may be prepared Chip memory. This routine does CPU stores only.
Returns D3=1 on success, 0 on refusal, D2=0. Other registers are preserved.

The Chip entry uses the same source and geometry inputs plus trusted ExecBase
in A6. It allocates one exact MEMF_CHIP block, verifies both ends and prepares
the planes. On success A1/D7 return its address/size and ownership transfers to
the caller. On failure A1/D7 are zero and any acquired block has been freed.
"""

from hashlib import sha256

from m19_p0a_multi_bob_abk import MAX_PIXELS, MAX_SIDE
from m68k_emit import A, D, I, M, POST, PRE, Code

HEIGHT, PLANES, PLANE_BYTES, ROW_STEP, PADDING = range(0, 20, 4)
FRAME_BYTES = 20

BRA, BSR, BHI, BLS, BCS, BNE, BEQ = 0, 1, 2, 3, 5, 6, 7


def emit_planar_orientation020():
    code = Code()
    branch, label = code.branch, code.label

    label("p2b_planar_orientation_entry")
    code.raw("48e7cffe")  # MOVEM.L D0-D1/D4-D7/A0-A6,-(SP)
    code.word(0x4fef)  # LEA -FRAME_BYTES(SP),SP
    code.word(-FRAME_BYTES)
    code.move(D(1), M(7, HEIGHT))
    code.move(D(4), M(7, PLANES))

    branch(BSR, "measure")
    code.tst(D(3))
    branch(BEQ, "invalid")
    for capacity in (6, 7):
        code.alu("cmp", D(capacity), 3)
        branch(BHI, "invalid")

    # Stride is rounded to complete words. Padding is measured in bits.
    code.move(D(2), D(4))
    code.shift(4, 3, left=True)
    code.alu("sub", D(0), 4)
    code.move(D(4), M(7, PADDING))
    code.move(D(2), D(4))
    code.word(0xc8c1)  # MULU.W D1,D4 => bytes per plane
    code.move(D(4), M(7, PLANE_BYTES))

    # Validate even, nonzero starts and both ends before touching the output.
    for address, register in ((0, 0), (1, 1)):
        code.move(A(address), D(register))
        code.tst(D(register))
        branch(BEQ, "invalid")
        code.word(0x0800 | register)  # BTST #0,Dn
        code.word(0)
        branch(BNE, "invalid")
    code.move(D(0), D(6))
    code.alu("add", D(3), 6)
    branch(BCS, "invalid")
    code.move(D(1), D(7))
    code.alu("add", D(3), 7)
    branch(BCS, "invalid")
    code.alu("cmp", D(1), 6)
    branch(BLS, "disjoint")
    code.alu("cmp", D(0), 7)
    branch(BHI, "invalid")

    label("disjoint")
    code.move(D(2), D(6))  # D6 holds the row stride.
    code.move(D(2), D(0))
    code.raw("08050001")  # BTST #1,D5 (vertical)
    branch(BEQ, "save_row_step")
    code.word(0x4480)  # NEG.L D0
    label("save_row_step")
    code.move(D(0), M(7, ROW_STEP))
    code.move(M(7, PADDING), D(4))

    label("plane")
    code.move(M(7, HEIGHT), D(7))
    code.move(A(0), A(2))  # Current source row base.
    code.raw("08050001")  # BTST #1,D5 (vertical)
    branch(BEQ, "row")
    code.move(M(7, PLANE_BYTES), D(0))
    code.alu("sub", D(6), 0)
    code.word(0xd5c0)  # ADDA.L D0,A2 (start at last row)

    label("row")
    code.move(A(2), A(3))
    code.move(D(6), D(2))
    code.shift(2, 1)  # Words remaining in this row.
    code.raw("08050000")  # BTST #0,D5 (horizontal)
    branch(BNE, "reverse_row")

    label("copy_word")
    code.move(POST(3), POST(1), "w")
    code.quick(1, D(2), sub=True)
    branch(BNE, "copy_word")
    branch(BRA, "next_row")

    label("reverse_row")
    code.word(0xd7c6)  # ADDA.L D6,A3 (exclusive source-row end)
    branch(BSR, "reverse_source_word")
    code.move(D(0), D(3))

    # Adjacent reversed words form a 32-bit window. Shift out the leading
    # padding from the original last word without reading across row bounds.
    label("reverse_word")
    code.quick(1, D(2), sub=True)
    branch(BEQ, "zero_tail")
    branch(BSR, "reverse_source_word")
    branch(BRA, "store_reversed")
    label("zero_tail")
    code.move(I(0, "w"), D(0), "w")
    label("store_reversed")
    code.move(D(3), D(1))
    code.word(0x4841)  # SWAP D1
    code.alu("or", D(0), 1, "w")
    code.word(0xe9a9)  # LSL.L D4,D1 (0..15 bits)
    code.word(0x4841)  # SWAP D1
    code.move(D(1), POST(1), "w")
    code.move(D(0), D(3))
    code.tst(D(2))
    branch(BNE, "reverse_word")

    label("next_row")
    code.quick(1, D(7), sub=True)
    branch(BEQ, "next_plane")
    code.move(M(7, ROW_STEP), D(0))
    code.word(0xd5c0)  # ADDA.L D0,A2
    branch(BRA, "row")
    label("next_plane")
    code.move(M(7, PLANE_BYTES), D(0))
    code.word(0xd1c0)  # ADDA.L D0,A0
    code.quick(1, M(7, PLANES), sub=True)
    branch(BNE, "plane")

    code.word(0x7601)  # MOVEQ #1,D3
    branch(BRA, "return")
    label("invalid")
    code.word(0x7600)  # MOVEQ #0,D3
    label("return")
    code.word(0x4fef)  # LEA FRAME_BYTES(SP),SP
    code.word(FRAME_BYTES)
    code.raw("4cdf7ff374004e75")  # MOVEM restore, MOVEQ #0,D2, RTS.

    label("reverse_source_word")
    code.word(0x7000)  # MOVEQ #0,D0, keep upper word clear.
    code.move(PRE(3), D(0), "w")
    for shift, mask in ((1, 0x5555), (2, 0x3333), (4, 0x0f0f)):
        code.move(D(0), D(1))
        code.shift(1, shift)
        code.imm("and", mask, D(1), "w")
        code.imm("and", mask, D(0), "w")
        code.shift(0, shift, left=True)
        code.alu("or", D(1), 0, "w")
    code.word(0xe158)  # ROL.W #8,D0
    code.word(0x4e75)  # RTS
    # Shared pure size preflight, all input registers unchanged.
    label("measure")
    for register, maximum in ((0, MAX_SIDE), (1, MAX_SIDE), (4, 9)):
        code.tst(D(register))
        branch(BEQ, "measure_invalid")
        code.imm("cmp", maximum, D(register))
        branch(BHI, "measure_invalid")
    code.imm("cmp", 3, D(5))
    branch(BHI, "measure_invalid")
    code.move(D(0), D(2))
    code.word(0xc4c1)  # MULU.W D1,D2 => width * height
    code.imm("cmp", MAX_PIXELS, D(2))
    branch(BHI, "measure_invalid")

    code.move(D(0), D(2))
    code.imm("add", 15, D(2))
    code.shift(2, 4)
    code.shift(2, 1, left=True)
    code.move(D(2), D(3))
    code.word(0xc6c1)  # MULU.W D1,D3 => bytes per plane
    code.raw("4c043000")  # MULU.L D4,D3 => total size (fits in 32 bits)
    code.word(0x4e75)
    label("measure_invalid")
    code.word(0x7600)  # MOVEQ #0,D3
    code.word(0x4e75)

    label("p2b_planar_chip_prepare_entry")
    code.raw("48e7cebe")  # MOVEM.L D0-D1/D4-D6/A0/A2-A6,-(SP)
    branch(BSR, "measure")
    code.tst(D(3))
    branch(BEQ, "chip_fail")
    code.alu("cmp", D(6), 3)
    branch(BHI, "chip_fail")
    code.move(A(0), A(2))
    code.move(D(0), A(3))
    code.move(D(1), A(4))
    code.move(D(3), D(7))
    code.move(D(7), D(0))
    code.move(I(2), D(1))  # MEMF_CHIP
    code.call_os(-198)  # AllocMem(D0=size,D1=flags)
    code.tst(D(0))
    branch(BEQ, "chip_fail")
    code.move(D(0), A(5))

    # A fresh Exec allocation is contiguous. Check both endpoints and wrap.
    code.move(A(5), A(1))
    code.call_os(-534)  # TypeOfMem(A1)
    code.raw("08000001")  # BTST #1,D0 (MEMF_CHIP)
    branch(BEQ, "chip_free")
    code.move(A(5), D(0))
    code.alu("add", D(7), 0)
    branch(BCS, "chip_free")
    code.quick(1, D(0), sub=True)
    code.move(D(0), A(1))
    code.call_os(-534)
    code.raw("08000001")  # BTST #1,D0 (MEMF_CHIP)
    branch(BEQ, "chip_free")

    code.move(A(2), A(0))
    code.move(A(5), A(1))
    code.move(A(3), D(0))
    code.move(A(4), D(1))
    branch(BSR, "p2b_planar_orientation_entry")
    code.tst(D(3))
    branch(BNE, "chip_return")
    label("chip_free")
    code.move(D(7), D(0))
    code.move(A(5), A(1))
    code.call_os(-210)  # FreeMem(D0=size,A1=block)
    label("chip_fail")
    code.move(I(0), A(1))
    code.raw("7e007600")  # MOVEQ #0,D7 / MOVEQ #0,D3
    label("chip_return")
    code.raw("4cdf7d7374004e75")  # MOVEM restore, MOVEQ #0,D2, RTS.
    return code.out(), code.labels


if __name__ == "__main__":
    native, _ = emit_planar_orientation020()
    print("P2B_PLANAR_ORIENTATION020", len(native), sha256(native).hexdigest())
