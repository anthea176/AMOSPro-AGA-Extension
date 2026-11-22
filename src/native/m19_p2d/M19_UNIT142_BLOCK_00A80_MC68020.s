; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$00A80..$00B9E, 286 instruction bytes.
UNIT142_BLOCK_00A80_EDIT equ 0

ENTRY_UNIT142_00A80:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)
    moveq #UNIT142_BLOCK_00A80_EDIT,d3
    movea.l 456(a5),a2
    tst.l (a2)
    beq.w L_UNIT142_00B96
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    bne.w L_UNIT142_00B48
    moveq #48,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_00B96
    movea.l d0,a4
    movea.l $0004.w,a6
    jsr -666(a6)
    tst.l d0
    beq.w L_UNIT142_00B8C
    move.l d0,12(a4)
    movea.l $0004.w,a6
    jsr -666(a6)
    tst.l d0
    beq.w L_UNIT142_00B68
    move.l d0,16(a4)
    movea.l (a2),a0
    suba.l a1,a1
    moveq #1,d0
    movea.l 4(a2),a6
    jsr -768(a6)
    tst.l d0
    beq.w L_UNIT142_00B68
    move.l d0,(a4)
    movea.l (a2),a0
    suba.l a1,a1
    moveq #2,d0
    movea.l 4(a2),a6
    jsr -768(a6)
    tst.l d0
    beq.w L_UNIT142_00B5C
    move.l d0,4(a4)
    movea.l (a4),a0
    movea.l 4(a0),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00B4E
    move.l 12(a4),d0
    move.l d0,22(a0)
    move.l 16(a4),d0
    move.l d0,54(a0)
    movea.l 4(a4),a0
    movea.l 4(a0),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00B4E
    move.l 12(a4),d0
    move.l d0,22(a0)
    move.l 16(a4),d0
    move.l d0,54(a0)
    move.l a4,32(a2)
L_UNIT142_00B48:
    moveq #1,d3
    bra.w L_UNIT142_00B96
L_UNIT142_00B4E:
    movea.l (a2),a0
    movea.l 4(a4),a1
    movea.l 4(a2),a6
    jsr -774(a6)
L_UNIT142_00B5C:
    movea.l (a2),a0
    movea.l (a4),a1
    movea.l 4(a2),a6
    jsr -774(a6)
L_UNIT142_00B68:
    movea.l $0004.w,a6
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00B7C
    jsr -672(a6)
L_UNIT142_00B7C:
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00B8C
    jsr -672(a6)
L_UNIT142_00B8C:
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_00B96:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6
    moveq #0,d2
    rts
