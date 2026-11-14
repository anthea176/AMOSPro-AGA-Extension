"""R82 P1: two native 68020 bank-number wrappers for AGAPAL Init/Capture.

Standalone, not installed. Calls the original qualified entry by BSR.L
(signed 32-bit PC relative), because R81 native body is >57 KiB and the
legacy palette routines are beyond the range of BSR.W from its end.
"""
from __future__ import annotations

from struct import pack_into, unpack_from
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr

BASIC_BANK_MIN = 5
BASIC_BANK_MAX = 65535
BANK_LOOKUP = rjsr(main_index("Bnk.GetAdr"))
assert main_index("Bnk.GetAdr") == 797
BSR_LONG = bytes.fromhex("61ff00000000")
PRESERVE = "48e7efee"
RESTORE = "4cdf77f7"
GETP = b"GetP"


def _emit_simple(native_start: int, native_target: int):
    """_OK=Aga Bank Palette {Init/Capture}(Bank, N_or_Index).

    D3 is the second argument, (A3)+ is the bank number. The old
    routine receives D3 unchanged and a synthetic Start(bank) at (A3)+.
    """
    c = Code()
    B, L = c.branch, c.label
    c.raw(PRESERVE)
    c.raw("4fefffe0")  # reserve 32-byte local stack frame
    c.move(A(7), A(2))
    c.move(D(3), M(2, 0))  # original count/index
    c.move(POST(3), D(7))  # bank number, consume exactly 1 argument
    c.move(A(3), M(2, 4))  # caller A3 after bank consumed
    c.move(D(7), D(0))
    c.imm("cmp", BASIC_BANK_MIN, D(0))
    B(5, "reject")
    c.imm("cmp", BASIC_BANK_MAX, D(0))
    B(2, "reject")
    # CPU000-safe AFF_68020 check before the first BSR.L opcode.
    c.raw("20780004")        # MOVEA.L 4.W,A0 : ExecBase
    c.move(A(0), D(0))
    c.tst(D(0))
    B(7, "reject")
    c.move(M(0, 0x128), D(0), "w")
    c.word(0x0800); c.word(1)  # BTST #AFF_68020,D0
    B(7, "reject")
    c.move(D(7),D(0))        # restore bank number for Bnk.GetAdr
    c.raw(BANK_LOOKUP.hex())
    c.move(A(0), D(0))
    c.tst(D(0))
    B(7, "reject")
    c.move(A(0), M(2, 8))
    c.move(M(2, 0), D(3))
    c.raw("47ea0008")  # LEA 8(A2),A3 : synthetic sole Start(bank)
    L("delegate")
    c.raw(BSR_LONG.hex())
    B(0, "done")
    L("reject")
    c.move(I(0), D(3))
    L("done")
    c.move(M(2, 4), A(3))
    c.raw("4fef0020")
    c.raw(RESTORE)
    c.raw("74004e75")  # D2 = integer; RTS
    code = bytearray(c.out())
    branch = c.labels["delegate"]
    assert code[branch:branch+6] == BSR_LONG
    # MC68020 BSR.L PC refers to the first extension word, at +2.
    displacement = native_target - (native_start + branch + 2)
    assert -(1 << 31) <= displacement < (1 << 31)
    pack_into(">i", code, branch + 2, displacement)
    assert native_start + branch + 2 + unpack_from(">i",code,branch+2)[0] == native_target
    assert code.count(BANK_LOOKUP) == 1
    return bytes(code), {
        **c.labels, "native_start":native_start,
        "native_target":native_target,
        "branch_displacement": displacement,
        "bank_lookup": main_index("Bnk.GetAdr")
    }


def emit_bank_palette_init(native_start: int, native_target: int):
    """Call legacy AGAPAL Init entry 41, without changing its ABI."""
    return _emit_simple(native_start, native_target)


def emit_bank_palette_capture(native_start: int, native_target: int):
    """Call legacy AGAPAL Capture entry 42, without changing its ABI."""
    return _emit_simple(native_start, native_target)
