; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $02584 source-verified against pinned P2d emitter.
; UNIT142+$02584..$0268C, 264 instructions/data bytes.
UNIT142_BLOCK_02584_EDIT equ 0

ENTRY_UNIT142_02584:
    move.l a3,-(a7)
    move.l 8(a3),-(a7)
    move.l 4(a3),-(a7)
    move.l (a3),-(a7)
    move.l d3,-(a7)
    movea.l a7,a3
    move.l #$00000000,d3
    bsr.w ENTRY_UNIT142_02360
    addq.l #8,a7
    addq.l #8,a7
    movea.l (a7)+,a3
    addq.l #8,a3
    addq.l #4,a3
    rts
ENTRY_UNIT142_025AA:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0267E
    movea.l (a4),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0267E
    move.l 342(a4),d0
    tst.l d0
    bne.w L_UNIT142_02642
    move.l 64(a4),d0
    tst.l d0
    bne.w L_UNIT142_0267E
    movea.l 456(a5),a0
    movea.l 8(a0),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_0267E
    movea.l $0004.w,a6
    move.l #$0000000C,d0
    move.l #$00010001,d1
    jsr -198(a6)
    tst.l d0
    beq.w L_UNIT142_0267E
    movea.l d0,a2
    movea.l 456(a5),a0
    movea.l 8(a0),a6
    movea.l a2,a0
    move.l #$00000040,d0
    jsr -594(a6)
    tst.l d0
    beq.w L_UNIT142_02650
    movea.l a2,a1
    move.l #$00002710,d0
    move.l #$000000FF,d1
    jsr -378(a6)
    movea.l a2,a1
    jsr -366(a6)
    move.l a2,342(a4)
    move.l a2,64(a4)
    bra.w L_UNIT142_02674
L_UNIT142_02642:
    move.l 64(a4),d1
    cmp.l d1,d0
    beq.w L_UNIT142_02674
    bra.w L_UNIT142_0267E
L_UNIT142_02650:
    movea.l 4(a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_02660
    jsr -546(a6)
L_UNIT142_02660:
    movea.l $0004.w,a6
    movea.l a2,a1
    move.l #$0000000C,d0
    jsr -210(a6)
    bra.w L_UNIT142_0267E
L_UNIT142_02674:
    move.l #$00000001,d3
    bra.w L_UNIT142_02684
L_UNIT142_0267E:
    move.l #$00000000,d3
L_UNIT142_02684:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02584_EDIT,d2
    rts
