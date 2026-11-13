"""OPT020/P1d ABI-shaped 020 worker entry, TEST-ONLY.

This probe reproduces the register-save/restore and seven (A3)+ argument
consumption used by native R60 Aga Image Region, with D3 Mode/result,
D2=0 on return, and an *early 68000-safe* ExecBase CPU capability check.

It intentionally takes a synthetic PREVALIDATED fragment descriptor in A0.
That descriptor is NOT an AMOS bank; do not export this as the public
"Aga Image Region" entry or replace R60 before bank/GetAdr, Safe,
two-pass RLE validation, real Bitmap.Planes and Compiler V2 are wired.

Test descriptor (BE LONG words) at A0:
 +0 source plane words address
 +4 source mask word address (0xffff if opaque)
 +8 destination plane POINTER TABLE address
+12 destination field bit offset [0..7]
+16 source group left bit [0..15]
+20 visible field width [1..16-left]
+24 depth [1..8]

ExecBase.AttnFlags: UWORD at ExecBase+0x128 (296), AFF_68020 bit 1.
Validated against Amiga NDK exec/execbase.h; check precedes every 020 opcode.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, I
from opt020_p1d_fragment_emit import emit_fragment_020

EXECBASE_ATTNFLAGS = 0x128
AFF_68020_BIT = 1
GETP_PARAMS = ("y", "x", "height", "width", "src_y", "src_x", "bank")


def emit_ap20_shaped_probe() -> bytes:
    c = Code()
    # EXACT R60/AMOS AP20 preservation pattern; D2/D3 results, A3 cursor.
    c.raw("48e7efee")                      # MOVEM.L preserved regs,-(SP)
    c.move(D(3), D(4))                     # original Mode 0 opaque, 1 masked
    c.word(0x7600)                        # default failure D3=0
    # Always pop the ENTIRE GetP tuple before ANY argument refusal,
    # matching R60's cursor behavior and the AMOS extension convention.
    for idx, _name in enumerate(GETP_PARAMS):
        c.move(POST(3), D(5))
        if idx == 2:
            c.move(D(5), D(6))             # height, scratch only
        elif idx == 3:
            c.move(D(5), D(7))             # width, scratch only
    c.tst(D(6))
    c.branch(15, "reject")                 # invalid height
    c.tst(D(7))
    c.branch(15, "reject")                 # invalid width
    c.imm("cmp", 5, D(5))
    c.branch(5, "reject")                  # bank number under 5
    c.imm("cmp", 1, D(4))
    c.branch(2, "reject")                  # BHI, mode outside 0..1

    # All instructions before this test are legal on a plain 68000.
    c.raw("2c780004")                     # MOVEA.L 4.W,A6 = ExecBase
    c.move(A(6), D(0))                   # TST An illegal on MC68000
    c.tst(D(0))                          # safe 68000 pointer check
    c.branch(7, "reject")
    c.move(M(6, EXECBASE_ATTNFLAGS), D(0), "w")
    c.word(0x0800)                        # BTST #1,D0
    c.word(AFF_68020_BIT)
    c.branch(7, "reject")                  # no 020 -> return 0, never BFEXTU

    # Synthetic prevalidated structure, NOT the actual AMOS bank.
    c.move(A(0), D(5))                   # avoid TST An here as well
    c.tst(D(5))
    c.branch(7, "reject")
    c.move(A(0), A(4))
    c.move(M(4, 0), A(0))
    c.move(M(4, 4), A(1))
    c.move(M(4, 8), A(2))
    c.move(M(4, 12), D(0))
    c.move(M(4, 16), D(4))
    c.move(M(4, 20), D(6))
    c.move(M(4, 24), D(7))
    for ptr in (A(0), A(1), A(2)):
        c.move(ptr, D(5))
        c.tst(D(5))
        c.branch(7, "reject")
    c.imm("cmp", 7, D(0))
    c.branch(2, "reject")                  # dest bit offset <=7 unsigned
    c.imm("cmp", 15, D(4))
    c.branch(2, "reject")                  # source left <=15
    c.tst(D(6))
    c.branch(15, "reject")                 # width <=0
    c.move(D(4), D(5))
    c.alu("add", D(6), 5)
    c.imm("cmp", 16, D(5))
    c.branch(14, "reject")                 # left+width >16
    c.imm("cmp", 1, D(7))
    c.branch(13, "reject")                 # depth <1
    c.imm("cmp", 8, D(7))
    c.branch(14, "reject")                 # depth >8

    c.branch(1, "fragment")               # BSR.W only after guard
    c.branch(0, "leave")
    c.label("reject")
    c.word(0x7600)                        # MOVEQ #0,D3
    c.label("leave")
    c.raw("4cdf77f7")                     # restore R60 prescribed set
    c.word(0x7400)                        # MOVEQ #0,D2
    c.word(0x4e75)                        # RTS
    c.label("fragment")
    c.raw(emit_fragment_020().hex())      # separate 020-only worker
    return c.out()


if __name__ == "__main__":
    from hashlib import sha256
    p = emit_ap20_shaped_probe()
    print("OPT020 ABI SHAPE",len(p),sha256(p).hexdigest())
