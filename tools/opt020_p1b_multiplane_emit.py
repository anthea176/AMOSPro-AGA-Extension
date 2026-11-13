"""OPT020 P1b: real 68020 masked eight-plane group kernel.

Inputs:
 A0 -> source plane words, depth consecutive BE WORDs (1..8)
 A1 -> destination pointer table, depth consecutive BE LONGs
 D0 = destination bit offset (0..7), D2.w = effective source mask
 D6.w = depth (1..8).
Outputs: D3=1; A3, D0, D2, D5 and stack preserved.
Scratch: A0/A1/A2, D1/D4/D6/D7; NO AP20 ABI is implied.

IMPORTANT: caller validates entire RLE bank, inactive Safe back-buffer,
source/destination boundaries, plane layout, CPU>=68EC020 and memory.
The kernel accesses a 16-bit field at each destination pointer + D0 bits.
It must never be used across an unallocated bitmap row boundary.
"""
from __future__ import annotations

from m68k_emit import A, D, POST, Code
from opt020_p1_bitfield_emit import bitfield_020


def emit_masked_multiplane_020() -> bytes:
    c = Code()
    c.label("next_plane")
    c.raw(bitfield_020(0xe9c0, 0, 1).hex())  # BFEXTU (A0){0:16},D1
    c.quick(2, A(0))                         # next BE source WORD
    c.move(POST(1), A(2))                    # MOVEA.L (A1)+,A2
    c.raw(bitfield_020(0xe9c0, 2, 4, offset_reg=0).hex())
    # D4=old destination field, D1=source field, D2.w=source/effective mask
    c.move(D(2), D(7), "w")                  # D7.w=mask
    c.word(0x4647)                          # NOT.W D7
    c.alu("and", D(2), 1, "w")               # source & mask
    c.alu("and", D(7), 4, "w")               # old & ~mask
    c.alu("or", D(4), 1, "w")                # merged 16-bit word
    c.raw(bitfield_020(0xefc0, 2, 1, offset_reg=0).hex())
    c.quick(1, D(6), sub=True, size="w")     # next plane
    c.branch(6, "next_plane")               # BNE
    c.word(0x7601)                          # MOVEQ #1,D3
    c.word(0x4e75)                          # RTS
    binary = c.out()
    assert len(binary) % 2 == 0
    return binary
