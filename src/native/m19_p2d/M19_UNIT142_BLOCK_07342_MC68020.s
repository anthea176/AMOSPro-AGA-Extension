; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $07342 source-verified against pinned P2d emitter.
; UNIT142+$07342..$0735A, 24 instructions/data bytes.
UNIT142_BLOCK_07342_EDIT equ 1

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0748E
    move.l (a2),d0
    move.l #UNIT142_BLOCK_07342_EDIT,d1
    move.l 60(a2),d2
    lea L_UNIT142_077D0(pc),a0
