; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0C8BE source-verified against pinned P2d emitter.
; UNIT142+$0C8BE..$0C8D4, 22 instructions/data bytes.
UNIT142_BLOCK_0C8BE_EDIT equ 0

L_UNIT142_0C8BE:
    move.l #$00000000,d3
L_UNIT142_0C8C4:
    movea.l 12(a7),a3
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0C8BE_EDIT,d2
    rts
