; AGA_NATIVE_MIN_CPU: MC68020
; Source-verified UNIT153 short service, pinned P2d.
; UNIT153+$0094A..$009FE (180 code bytes), GetP marker preserved.
UNIT153_SHORT_INITIAL_D3 equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -48(a7),a7
    movea.l a7,a2
    move.l #UNIT153_SHORT_INITIAL_D3,d3
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT153_009F2
    move.l a4,(a2)
    movea.l 32(a4),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT153_009F2
    move.l a4,4(a2)
    move.l 40(a4),d0
    cmpi.l #$43325031,d0
    bne.w L_UNIT153_009F2
    move.l 24(a4),d0
    tst.l d0
    beq.w L_UNIT153_009F2
    move.l d0,8(a2)
    move.l 28(a4),d0
    tst.l d0
    beq.w L_UNIT153_009F2
    move.l d0,12(a2)
    movea.l (a2),a4
    move.l 8(a4),d0
    move.l d0,16(a2)
    movea.l 4(a2),a4
    clr.l 24(a4)
    clr.l 28(a4)
    clr.l 32(a4)
    clr.l 36(a4)
    clr.l 40(a4)
    movea.l 16(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT153_009D4
    jsr -228(a6)
L_UNIT153_009D4:
    movea.l 12(a2),a0
    movea.l 8(a2),a6
    jsr -60(a6)
    movea.l 8(a2),a1
    movea.l $0004.w,a6
    jsr -414(a6)
    move.l #$00000001,d3
L_UNIT153_009F2:
    lea 48(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
