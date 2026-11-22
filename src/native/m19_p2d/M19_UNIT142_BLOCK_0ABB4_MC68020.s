; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0ABB4 source-verified against pinned P2d emitter.
; UNIT142+$0ABB4..$0ABC6, 18 instructions/data bytes.
UNIT142_BLOCK_0ABB4_EDIT equ 0

L_UNIT142_0ABB4:
    move.l #$00000000,d3
L_UNIT142_0ABBA:
    lea 384(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0ABB4_EDIT,d2
    rts
L_UNIT142_0ABC6:
