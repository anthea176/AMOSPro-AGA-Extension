"""OPT020/P1: two standalone kernels for 16-pixel opaque AGAPIC groups.

Source word at A0, destination byte at A1, dest bit offset D0 (0..7).
Full group, no clipping or mask; the caller MUST acquire Safe, check
screen bounds and ensure at least 3 destination bytes are accessible.
D3=1 result; A3/D5 unchanged; A1 is a scratch in the CPU000 variant.
NOT a full AGAPIC renderer, AP20 entry, or installable library.
"""
from __future__ import annotations

from hashlib import sha256
from struct import pack
from m68k_emit import Code, D, A, M, I


def reference_68000() -> bytes:
    """68000-only: copy 16 source bits one by one into 2-3 dest bytes."""
    c = Code()
    c.move(M(0), D(1), "w")      # MOVE.W (A0),D1
    c.move(I(15), D(2))          # source bit 15..0
    c.move(I(7), D(4))
    c.alu("sub", D(0), 4)        # first dest bit = 7-offset
    c.label("pixel")
    c.word(0x0501)              # BTST D2,D1
    c.branch(7, "pixel_zero")   # BEQ
    c.word(0x09d1)              # BSET D4,(A1)
    c.branch(0, "after_pixel")
    c.label("pixel_zero")
    c.word(0x0991)              # BCLR D4,(A1)
    c.label("after_pixel")
    c.quick(1, D(4), sub=True)
    c.branch(10, "same_byte")   # BPL
    c.quick(1, A(1))
    c.move(I(7), D(4))
    c.label("same_byte")
    c.quick(1, D(2), sub=True)
    c.branch(10, "pixel")       # BPL, exactly 16 pixels
    c.word(0x7601)              # MOVEQ #1,D3
    c.word(0x4e75)              # RTS
    return c.out()


def bitfield_020(opcode: int, address_reg: int, value_reg: int,
                 *, offset_reg: int | None = None, width: int = 16) -> bytes:
    """68020 E9C0 BFEXTU / EFC0 BFINS, plus Motorola extension word.

    Register fields: bits 14-12 of extension = data register, bit 11
    = dynamic-offset selector, bits 8-6 = offset data register, bits
    4-0 = bit-field width (0 encodes width 32). EA=010rrr is (Ar).
    """
    assert opcode in (0xe9c0, 0xefc0)
    assert 0 <= address_reg <= 7 and 0 <= value_reg <= 7
    assert offset_reg is None or 0 <= offset_reg <= 7
    assert 1 <= width <= 32
    ext = (value_reg << 12) | (width & 31)
    if offset_reg is not None:
        ext |= 0x0800 | (offset_reg << 6)
    return pack(">HH", opcode | 0x10 | address_reg, ext)


def candidate_68020() -> bytes:
    """16-pixel opaque group copy with actual 020 bit-field opcodes."""
    result = (bitfield_020(0xe9c0, 0, 1)  # BFEXTU (A0){0:16},D1
              + bitfield_020(0xefc0, 1, 1, offset_reg=0)
              + bytes.fromhex("76014e75"))  # MOVEQ #1,D3 ; RTS
    assert result == bytes.fromhex("e9d01010efd1181076014e75")
    return result


if __name__ == "__main__":
    for label, blob in (("CPU000", reference_68000()),
                        ("CPU020", candidate_68020())):
        print(label, len(blob), "bytes", sha256(blob).hexdigest())
