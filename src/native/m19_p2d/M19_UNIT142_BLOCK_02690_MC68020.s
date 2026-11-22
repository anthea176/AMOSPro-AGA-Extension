; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $02690 source-verified against pinned P2d emitter.
; UNIT142+$02690..$02738, 168 instructions/data bytes.
UNIT142_BLOCK_02690_EDIT equ 0

ENTRY_UNIT142_02690:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0272A
    movea.l (a4),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0272A
    move.l 342(a4),d6
    move.l d6,d0
    andi.l #$FFFFFFFC,d0
    movea.l d0,a2
    tst.l d0
    beq.w L_UNIT142_0272A
    move.l 64(a4),d1
    cmp.l d1,d0
    bne.w L_UNIT142_0272A
    movea.l 456(a5),a0
    movea.l 4(a0),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_0272A
    movea.l 8(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_0272A
    move.w 28(a1),d0
    cmpi.w #$0001,d0
    beq.w L_UNIT142_026FE
    move.l d6,d0
    andi.l #$00000002,d0
    tst.l d0
    beq.w L_UNIT142_0272A
L_UNIT142_026FE:
    ori.l #$00000001,342(a4)
    movea.l a4,a0
    jsr -378(a6)
    tst.l d0
    bne.w L_UNIT142_0272A
    jsr -390(a6)
    tst.l d0
    bne.w L_UNIT142_0272A
    bra.w L_UNIT142_02720
L_UNIT142_02720:
    move.l #$00000001,d3
    bra.w L_UNIT142_02730
L_UNIT142_0272A:
    move.l #$00000000,d3
L_UNIT142_02730:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02690_EDIT,d2
    rts
