"""OPT020/P1d: native 68020 clipped planar fragment writer, 1..16 pixels.

Inputs (already *fully* validated by caller):
 A0 = consecutive source bitplane BE WORDs (depth 1..8)
 A1 = address of source mask BE WORD (0xffff for opaque)
 A2 = array of depth destination plane byte addresses (BE LONGs)
 D0 = destination bit offset 0..7 within first dest byte
 D4 = source bit offset 0..15 inside 16-pixel group
 D6 = visible width 1..16-D4
 D7 = number of bitplanes 1..8

The caller MUST ensure destination bitfield is contained in the bitmap row,
source word is readable and all plane addresses are valid/inactive/Safe.
D3=1 on return; A3/D5/D0/D4/D6 preserved; D7/A0/A2 advanced.
This is not an AMOS entry and does NOT replace R60's double preflight.
"""
from __future__ import annotations

from struct import pack
from m68k_emit import A, D, POST, Code


def bitfield_dynamic(opcode: int, an: int, dn: int, offset_dn: int,
                     width_dn: int) -> bytes:
    """68020 memory BFEXTU/BFINS with register offset and dynamic width.

    Motorola extension format: data register = 14..12, DO bit 11,
    offset reg bits 8..6, DW bit 5, width reg bits 2..0.
    """
    assert opcode in (0xe9c0, 0xefc0)
    assert all(0 <= n <= 7 for n in (an, dn, offset_dn, width_dn))
    extension = (dn << 12) | 0x0800 | (offset_dn << 6) | 0x0020 | width_dn
    return pack(">HH", opcode | 0x10 | an, extension)


def emit_fragment_020() -> bytes:
    c = Code()
    # Read only the visible source-mask field once (same for all planes).
    c.raw(bitfield_dynamic(0xe9c0, 1, 2, 4, 6).hex())   # BFEXTU (A1){D4:D6},D2
    c.label("plane")
    c.raw(bitfield_dynamic(0xe9c0, 0, 1, 4, 6).hex())   # BFEXTU (A0){D4:D6},D1
    c.quick(2, A(0))                                   # next source plane
    c.move(POST(2), A(4))                              # next dest plane pointer
    c.raw(bitfield_dynamic(0xe9c0, 4, 3, 0, 6).hex())   # BFEXTU (A4){D0:D6},D3
    # old XOR ((old XOR source) & mask) is a bit-exact masked assignment.
    c.word(0xb741)                                     # EOR.W D3,D1
    c.alu("and", D(2), 1, "w")                         # AND.W D2,D1
    c.word(0xb741)                                     # EOR.W D3,D1
    c.raw(bitfield_dynamic(0xefc0, 4, 1, 0, 6).hex())   # BFINS D1,(A4){D0:D6}
    c.quick(1, D(7), sub=True, size="w")
    c.branch(6, "plane")                               # BNE
    c.word(0x7601)                                     # MOVEQ #1,D3
    c.word(0x4e75)                                     # RTS
    return c.out()


if __name__ == "__main__":
    import hashlib
    p = emit_fragment_020()
    print("OPT020 FRAGMENT CPU020", len(p), hashlib.sha256(p).hexdigest())
