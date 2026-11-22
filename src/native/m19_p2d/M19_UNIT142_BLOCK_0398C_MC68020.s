; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0398C source-verified against pinned P2d emitter.
; UNIT142+$0398C..$03A06, 122 instructions/data bytes.
UNIT142_BLOCK_0398C_EDIT equ 1

L_UNIT142_0398C:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_03994:
    movem.l d1-d7/a0-a4/a6,-(a7)
    tst.l 20(a5)
    beq.w L_UNIT142_039AC
    movea.l 16(a5),a6
    move.l 20(a5),d1
    jsr -36(a6)
L_UNIT142_039AC:
    tst.l 96(a5)
    beq.w L_UNIT142_039C0
    movea.l 96(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_039C0:
    tst.l 24(a5)
    beq.w L_UNIT142_039D4
    movea.l 24(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_039D4:
    tst.l 12(a5)
    beq.w L_UNIT142_039E8
    movea.l 12(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_039E8:
    tst.l 16(a5)
    beq.w L_UNIT142_039FC
    movea.l 16(a5),a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT142_039FC:
    move.l #UNIT142_BLOCK_0398C_EDIT,d0
    bra.w L_UNIT142_03A0C
