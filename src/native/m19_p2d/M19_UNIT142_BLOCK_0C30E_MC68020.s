; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0C30E source-verified against pinned P2d emitter.
; UNIT142+$0C30E..$0C340, 50 instructions/data bytes.
UNIT142_BLOCK_0C30E_EDIT equ 0

    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0C32A
    move.l a0,8(a2)
    move.l (a2),d3
    lea 8(a2),a3
    bsr.l ENTRY_UNIT142_0411A
    bra.w L_UNIT142_0C330
L_UNIT142_0C32A:
    move.l #$00000000,d3
L_UNIT142_0C330:
    movea.l 4(a2),a3
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0C30E_EDIT,d2
    rts
