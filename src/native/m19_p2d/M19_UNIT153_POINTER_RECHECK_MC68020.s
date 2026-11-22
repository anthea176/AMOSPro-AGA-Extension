; AGA_NATIVE_MIN_CPU: MC68020
; Source-verified UNIT153 pointer recheck, pinned P2d emitter.
; UNIT153+$00BDA..$00C98 (190 code bytes); AMOS Main marker preserved.
UNIT153_RECHECK_MIN_POINTER_BYTES equ 24

    move.l a0,d5
    cmpi.l #UNIT153_RECHECK_MIN_POINTER_BYTES,d5
    bls.w L_UNIT153_00F04
    move.l d5,d0
    andi.l #$00000001,d0
    bne.w L_UNIT153_00F04
    move.l d5,44(a2)
    movea.l d5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT153_00F04
    move.l 44(a2),d0
    subi.l #$00000018,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT153_00F04
    movea.l 44(a2),a4
    move.l -16(a4),d0
    move.l 28(a2),d1
    cmp.l d1,d0
    bne.w L_UNIT153_00F04
    move.l #$00000000,d0
    move.w -12(a4),d0
    tst.l d0
    beq.w L_UNIT153_00C4E
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_UNIT153_00F04
L_UNIT153_00C4E:
    movea.l 44(a2),a4
    move.l -20(a4),d0
    cmpi.l #$00000011,d0
    bcs.w L_UNIT153_00F04
    subi.l #$00000010,d0
    tst.l d0
    blt.w L_UNIT153_00F04
    move.l d0,48(a2)
    move.l 44(a2),d0
    move.l 48(a2),d1
    add.l d1,d0
    bcs.w L_UNIT153_00F04
    move.l d0,52(a2)
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT153_00F04
    move.l 40(a2),d0
