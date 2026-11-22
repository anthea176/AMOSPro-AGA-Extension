; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 bank bridge offset source-verified against pinned P2d emitter.
; UNIT142+$0A6E2..$0A6F4, 18 instructions/data bytes.
UNIT142_BLOCK_0A6E2_EDIT equ 24

    move.l a0,24(a2)
    move.l UNIT142_BLOCK_0A6E2_EDIT(a2),d0
    tst.l d0
    bne.w L_UNIT142_0A800
    move.l 20(a2),d0
