; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0CED8 source-verified against pinned P2d emitter.
; UNIT142+$0CED8..$0CEEE, 22 instructions/data bytes.
UNIT142_BLOCK_0CED8_EDIT equ 0

L_UNIT142_0CED8:
    move.l #$00000000,d3
L_UNIT142_0CEDE:
    movea.l 12(a7),a3
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0CED8_EDIT,d2
    rts
