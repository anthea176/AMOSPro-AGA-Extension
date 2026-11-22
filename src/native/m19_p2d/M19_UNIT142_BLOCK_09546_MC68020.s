; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $09546 source-verified against pinned P2d emitter.
; UNIT142+$09546..$09558, 18 instructions/data bytes.
UNIT142_BLOCK_09546_EDIT equ 0

    move.l #$00000000,d3
L_UNIT142_0954C:
    lea 48(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_09546_EDIT,d2
    rts
L_UNIT142_09558:
