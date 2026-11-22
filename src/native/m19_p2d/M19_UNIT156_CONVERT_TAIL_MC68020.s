; AGA_NATIVE_MIN_CPU: MC68020
; Native UNIT156 conversion/cleanup tail from SHA-pinned P2d source.
; UNIT156+$00850..$00926, 214 code bytes. One original raw MOVE classified.
UNIT156_TAIL_ZERO equ 0

    addq.l #1,d6
    cmp.l 64(a5),d6
    bcs.w L_UNIT156_0074A
    move.l a1,d0
    addi.l #$00000140,d0
    movea.l d0,a1
    dbra d4,L_UNIT156_00744
L_UNIT156_00868:
    move.l a0,d0
    cmp.l a2,d0
    beq.w L_UNIT156_0088E
    tst.l 72(a5)
    beq.w L_UNIT156_00898
    move.l #$00000000,d0
    move.b (a0)+,d0
    cmpi.l #$00000080,d0
    bne.w L_UNIT156_00898
    bra.w L_UNIT156_00868
L_UNIT156_0088E:
    move.l #$00000001,d0
    bra.w L_UNIT156_0089E
L_UNIT156_00898:
    move.l #$00000000,d0
L_UNIT156_0089E:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT156_008A6:
    movem.l d1-d7/a0-a4/a6,-(a7)
    tst.l 20(a5)
    beq.w L_UNIT156_008BE
    movea.l 16(a5),a6
    move.l 20(a5),d1
    jsr -36(a6)
L_UNIT156_008BE:
    tst.l 96(a5)
    beq.w L_UNIT156_008D2
    movea.l 96(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT156_008D2:
    tst.l 24(a5)
    beq.w L_UNIT156_008E6
    movea.l 24(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT156_008E6:
    tst.l 12(a5)
    beq.w L_UNIT156_008FA
    movea.l 12(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT156_008FA:
    tst.l 16(a5)
    beq.w L_UNIT156_0090E
    movea.l 16(a5),a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT156_0090E:
    move.l #$00000001,d0
    bra.w L_UNIT156_0091E
    move.l #UNIT156_TAIL_ZERO,d0
L_UNIT156_0091E:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
