; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$09790..$0992C, 412 instruction bytes.
UNIT142_BLOCK_09790_EDIT equ 0

    move.l a0,d5
    cmpi.l #$00000018,d5
    bls.w L_UNIT142_09920
    move.l d5,d0
    andi.l #$00000001,d0
    bne.w L_UNIT142_09920
    move.l d5,28(a2)
    movea.l d5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_09920
    move.l 28(a2),d0
    subi.l #$00000018,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_09920
    movea.l 28(a2),a0
    move.l -20(a0),d4
    cmpi.l #$00000110,d4
    bcs.w L_UNIT142_09920
    subi.l #$00000010,d4
    move.l d4,32(a2)
    move.l 28(a2),d0
    add.l d4,d0
    bcs.w L_UNIT142_09920
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_09920
    movea.l 28(a2),a0
    move.l -16(a0),d0
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_UNIT142_09920
    move.l #$00000000,d0
    move.w -12(a0),d0
    tst.l d0
    beq.w L_UNIT142_0983C
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_UNIT142_09920
L_UNIT142_0983C:
    move.l 32(a2),d0
    subi.l #$00000100,d0
    move.l (a2),d1
    cmp.l d1,d0
    bcs.w L_UNIT142_09920
    move.l 28(a2),d0
    add.l d1,d0
    bcs.w L_UNIT142_09920
    move.l d0,36(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_09920
    move.l 36(a2),d0
    addi.l #$000000FF,d0
    bcs.w L_UNIT142_09920
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_09920
    movea.l 36(a2),a0
    movea.l 40(a2),a1
    move.l #$00000010,d6
L_UNIT142_09898:
    move.w #$0000,(a1)
    move.l #$00000000,2(a1)
    move.l #$00000000,6(a1)
    move.l #$00000000,10(a1)
    move.l #$00000000,14(a1)
    move.l #$00000000,d7
    move.w #$8000,d1
    move.l #$00000010,d2
L_UNIT142_098CC:
    move.l #$00000000,d4
    move.b (a0)+,d4
    tst.b d4
    bne.w L_UNIT142_098E0
    or.w d1,d7
    bra.w L_UNIT142_09906
L_UNIT142_098E0:
    movea.l a1,a4
    addq.l #2,a4
    move.l #$00000008,d5
L_UNIT142_098EA:
    move.l d4,d0
    andi.w #$0001,d0
    tst.w d0
    beq.w L_UNIT142_098FC
    move.w (a4),d0
    or.w d1,d0
    move.w d0,(a4)
L_UNIT142_098FC:
    lsr.w #1,d4
    addq.l #2,a4
    subq.l #1,d5
    bne.w L_UNIT142_098EA
L_UNIT142_09906:
    lsr.w #1,d1
    subq.l #1,d2
    bne.w L_UNIT142_098CC
    move.w d7,(a1)
    lea 18(a1),a1
    subq.l #1,d6
    bne.w L_UNIT142_09898
    move.l #$00000001,d3
L_UNIT142_09920:
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_09790_EDIT,d2
    rts
