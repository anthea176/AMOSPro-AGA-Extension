; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$0652C..$0666C, 320 instruction bytes.
UNIT142_BLOCK_0652C_EDIT equ 0

ENTRY_UNIT142_0652C:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)
    move.l d3,d7
    move.l #$00000000,d3
    tst.l d7
    blt.w L_UNIT142_06602
    cmpi.l #$00000001,d7
    bgt.w L_UNIT142_06602
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_06602
    movea.l (a4),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_06602
    movea.l 4(a4),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_06602
    movea.l 36(a4),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_06602
    move.l 46(a3),d0
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_UNIT142_06602
    lea L_UNIT142_0666C(pc),a2
    move.l (a2),d0
    tst.l d0
    beq.w L_UNIT142_0659A
    move.l 4(a2),d0
    move.l a3,d1
    cmp.l d1,d0
    bne.w L_UNIT142_06602
L_UNIT142_0659A:
    tst.l d7
    beq.w L_UNIT142_065B0
    movea.l a3,a0
    jsr -60(a6)
    move.l #$00000001,d3
    bra.w L_UNIT142_06602
L_UNIT142_065B0:
    move.l (a2),d0
    tst.l d0
    bne.w L_UNIT142_065D8
    move.l #$00000048,d0
    move.l #$00010002,d1
    movea.l $0004.w,a6
    jsr -198(a6)
    tst.l d0
    beq.w L_UNIT142_06602
    move.l d0,(a2)
    move.l a3,4(a2)
L_UNIT142_065D8:
    movea.l a3,a0
    movea.l (a2),a1
    move.l #$00000010,d0
    move.l #$00000010,d1
    move.l #$00000000,d2
    move.l #$00000000,d3
    movea.l 4(a4),a6
    jsr -270(a6)
    move.l #$00000001,d3
L_UNIT142_06602:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6
    moveq #UNIT142_BLOCK_0652C_EDIT,d2
    rts
L_UNIT142_0660A:
    movem.l d0-d7/a0-a6,-(a7)
    movea.l a0,a3
    lea L_UNIT142_0666C(pc),a4
    move.l (a4),d0
    tst.l d0
    beq.w L_UNIT142_0662E
    move.l 4(a4),d0
    move.l a3,d1
    cmp.l d1,d0
    bne.w L_UNIT142_0662E
    movea.l a3,a0
    jsr -60(a6)
L_UNIT142_0662E:
    movea.l a3,a0
    jsr -72(a6)
    move.l (a4),d0
    tst.l d0
    beq.w L_UNIT142_06666
    move.l 4(a4),d0
    move.l a3,d1
    cmp.l d1,d0
    bne.w L_UNIT142_06666
    movea.l (a4),a1
    move.l #$00000048,d0
    movea.l $0004.w,a6
    jsr -210(a6)
    move.l #$00000000,(a4)
    move.l #$00000000,4(a4)
L_UNIT142_06666:
    movem.l (a7)+,d0-d7/a0-a6
    rts
L_UNIT142_0666C:
