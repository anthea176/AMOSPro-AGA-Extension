; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $09A6C source-verified against pinned P2d emitter.
; UNIT142+$09A6C..$09A7A, 14 instructions/data bytes.
UNIT142_BLOCK_09A6C_EDIT equ 1

    move.l #UNIT142_BLOCK_09A6C_EDIT,d3
    bra.w L_UNIT142_09A86
L_UNIT142_09A76:
    move.l 4(a2),d0
