; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 public entry $0282C source-verified against pinned P2d emitter.
; UNIT142+$0282C..$02996, 362 instructions/data bytes.
UNIT142_BLOCK_0282C_RESULT equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d5
    move.l (a3)+,d4
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02988
    movea.l (a4),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02988
    cmpi.l #$000000FF,d4
    bhi.w L_UNIT142_02988
    cmpi.l #$000000DE,d5
    bhi.w L_UNIT142_02988
    move.l 342(a4),d6
    move.l d6,d0
    andi.l #$FFFFFFFC,d0
    movea.l d0,a2
    tst.l d0
    beq.w L_UNIT142_02988
    move.l 64(a4),d1
    cmp.l d1,d0
    bne.w L_UNIT142_02988
    move.l d6,d0
    andi.l #$00000003,d0
    tst.l d0
    bne.w L_UNIT142_02988
    movea.l 456(a5),a0
    movea.l 8(a0),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_02988
    movea.l 8(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_02988
    move.l 12(a1),d0
    tst.l d0
    beq.w L_UNIT142_02988
    movea.l 16(a1),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_02988
    move.w 30(a1),d0
    cmpi.w #$0040,d0
    bne.w L_UNIT142_02988
    move.w 28(a1),d7
    cmpi.w #$0000,d7
    bls.w L_UNIT142_02988
    cmpi.w #$003F,d7
    bcc.w L_UNIT142_02988
    movea.l 16(a1),a0
    subq.l #6,a0
    move.w (a0),d0
    cmpi.w #$0001,d0
    bne.w L_UNIT142_02988
    move.w 2(a0),d0
    cmpi.w #$2710,d0
    bne.w L_UNIT142_02988
    move.w 4(a0),d0
    cmpi.w #$00FF,d0
    bne.w L_UNIT142_02988
    move.w d7,d6
    subq.w #1,d6
    beq.w L_UNIT142_02944
    movea.l 16(a1),a0
    subq.l #6,a0
L_UNIT142_02912:
    subq.l #6,a0
    move.w (a0),d0
    cmpi.w #$0001,d0
    beq.w L_UNIT142_02928
    subq.w #1,d6
    bne.w L_UNIT142_02912
    bra.w L_UNIT142_02944
L_UNIT142_02928:
    move.w 2(a0),d0
    move.w d4,d1
    cmp.w d0,d1
    bhi.w L_UNIT142_02944
    bne.w L_UNIT142_02988
    move.w 4(a0),d0
    move.w d5,d1
    cmp.w d0,d1
    bls.w L_UNIT142_02988
L_UNIT142_02944:
    movea.l 16(a1),a0
    subq.l #6,a0
    move.l a0,16(a1)
    subq.w #1,28(a1)
    movea.l a2,a1
    move.l d4,d0
    move.l d5,d1
    jsr -378(a6)
    movea.l a2,a1
    jsr -366(a6)
    movea.l a2,a1
    move.l #$00002710,d0
    move.l #$000000FF,d1
    jsr -378(a6)
    movea.l a2,a1
    jsr -366(a6)
    bra.w L_UNIT142_0297E
L_UNIT142_0297E:
    move.l #$00000001,d3
    bra.w L_UNIT142_0298E
L_UNIT142_02988:
    move.l #$00000000,d3
L_UNIT142_0298E:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0282C_RESULT,d2
    rts
