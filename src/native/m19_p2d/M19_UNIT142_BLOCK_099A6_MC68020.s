; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $099A6 source-verified against pinned P2d emitter.
; UNIT142+$099A6..$099C0, 26 instructions/data bytes.
UNIT142_BLOCK_099A6_EDIT equ 3

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_09A86
    move.l 4(a2),d0
    move.l #UNIT142_BLOCK_099A6_EDIT,d1
    move.l 8(a2),d2
    lea L_UNIT142_09A92(pc),a0
