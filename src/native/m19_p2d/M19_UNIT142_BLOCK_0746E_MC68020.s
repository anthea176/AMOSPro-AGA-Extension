; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0746E source-verified against pinned P2d emitter.
; UNIT142+$0746E..$0747C, 14 instructions/data bytes.
UNIT142_BLOCK_0746E_EDIT equ 1

    move.l #UNIT142_BLOCK_0746E_EDIT,88(a2)
    bra.w L_UNIT142_0748E
L_UNIT142_0747A:
    move.l (a2),d0
