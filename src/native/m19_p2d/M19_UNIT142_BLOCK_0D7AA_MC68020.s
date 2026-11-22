; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0D7AA source-verified against pinned P2d emitter.
; UNIT142+$0D7AA..$0D7C2, 24 instructions/data bytes.
UNIT142_BLOCK_0D7AA_EDIT equ 1

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0D9A6
    move.l (a2),d0
    move.l #UNIT142_BLOCK_0D7AA_EDIT,d1
    move.l 60(a2),d2
    lea L_UNIT142_0DCFC(pc),a0
