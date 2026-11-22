; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0A6FA source-verified against pinned P2d emitter.
; UNIT142+$0A6FA..$0A714, 26 instructions/data bytes.
UNIT142_BLOCK_0A6FA_EDIT equ 3

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0ABA0
    move.l 20(a2),d0
    move.l #UNIT142_BLOCK_0A6FA_EDIT,d1
    move.l 68(a2),d2
    lea L_UNIT142_0ABC6(pc),a0
