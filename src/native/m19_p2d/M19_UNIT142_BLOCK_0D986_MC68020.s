; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0D986 source-verified against pinned P2d emitter.
; UNIT142+$0D986..$0D994, 14 instructions/data bytes.
UNIT142_BLOCK_0D986_EDIT equ 1

    move.l #UNIT142_BLOCK_0D986_EDIT,88(a2)
    bra.w L_UNIT142_0D9A6
L_UNIT142_0D992:
    move.l (a2),d0
