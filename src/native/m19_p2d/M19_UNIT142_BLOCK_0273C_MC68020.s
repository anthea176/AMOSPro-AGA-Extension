; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$0273C..$02828, 236 instruction bytes.
UNIT142_BLOCK_0273C_EDIT equ 0

ENTRY_UNIT142_0273C:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0281A
    movea.l (a4),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0281A
    move.l 342(a4),d6
    move.l d6,d0
    andi.l #$FFFFFFFC,d0
    movea.l d0,a2
    tst.l d0
    beq.w L_UNIT142_027E8
    move.l 64(a4),d1
    cmp.l d1,d0
    bne.w L_UNIT142_0281A
    movea.l 456(a5),a0
    movea.l 4(a0),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_0281A
    movea.l 456(a5),a0
    move.l 8(a0),d0
    tst.l d0
    beq.w L_UNIT142_0281A
    move.l #$00000000,64(a4)
    movea.l a4,a0
    jsr -378(a6)
    tst.l d0
    bne.w L_UNIT142_027F6
    jsr -390(a6)
    tst.l d0
    bne.w L_UNIT142_027FE
    movea.l 456(a5),a0
    movea.l 8(a0),a6
    jsr -270(a6)
    movea.l 4(a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_027CC
    jsr -546(a6)
L_UNIT142_027CC:
    move.l #$00000000,342(a4)
    movea.l $0004.w,a6
    movea.l a2,a1
    move.l #$0000000C,d0
    jsr -210(a6)
    bra.w L_UNIT142_02810
L_UNIT142_027E8:
    move.l 64(a4),d0
    tst.l d0
    beq.w L_UNIT142_02810
    bra.w L_UNIT142_0281A
L_UNIT142_027F6:
    move.l a2,64(a4)
    bra.w L_UNIT142_0281A
L_UNIT142_027FE:
    move.l a2,64(a4)
    movea.l a4,a0
    jsr -378(a6)
    jsr -390(a6)
    bra.w L_UNIT142_0281A
L_UNIT142_02810:
    move.l #$00000001,d3
    bra.w L_UNIT142_02820
L_UNIT142_0281A:
    move.l #$00000000,d3
L_UNIT142_02820:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0273C_EDIT,d2
    rts
