; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0949E source-verified against pinned P2d emitter.
; UNIT142+$0949E..$094B8, 26 instructions/data bytes.
UNIT142_BLOCK_0949E_EDIT equ 1

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0954C
    move.l 4(a2),d0
    move.l #UNIT142_BLOCK_0949E_EDIT,d1
    move.l 8(a2),d2
    lea L_UNIT142_09558(pc),a0
