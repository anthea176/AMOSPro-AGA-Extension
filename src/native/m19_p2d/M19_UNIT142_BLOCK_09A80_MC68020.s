; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $09A80 source-verified against pinned P2d emitter.
; UNIT142+$09A80..$09A92, 18 instructions/data bytes.
UNIT142_BLOCK_09A80_EDIT equ 0

    move.l #$00000000,d3
L_UNIT142_09A86:
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_09A80_EDIT,d2
    rts
L_UNIT142_09A92:
