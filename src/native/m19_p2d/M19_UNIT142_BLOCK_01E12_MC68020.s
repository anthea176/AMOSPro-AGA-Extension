; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$01E12..$01F30, 286 instruction bytes.
UNIT142_BLOCK_01E12_EDIT equ 0

    rts
L_UNIT142_01E14:
    bsr.w L_UNIT142_01E26
    tst.l d0
    beq.w L_UNIT142_01E22
    bra.w L_UNIT142_01CA4
L_UNIT142_01E22:
    bra.w L_UNIT142_01DF2
L_UNIT142_01E26:
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_01E5E
    moveq #UNIT142_BLOCK_01E12_EDIT,d4
L_UNIT142_01E34:
    bsr.w L_UNIT142_01E66
    tst.l d0
    beq.w L_UNIT142_01E5E
    addq.l #1,d4
    cmpi.l #$0000012D,d4
    bge.w L_UNIT142_01E62
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_01E62
    jsr -270(a6)
    bra.w L_UNIT142_01E34
L_UNIT142_01E5E:
    moveq #1,d0
    rts
L_UNIT142_01E62:
    moveq #0,d0
    rts
L_UNIT142_01E66:
    move.l 20(a4),d6
    andi.l #$00000003,d6
    btst #0,d6
    beq.w L_UNIT142_01E96
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01E96
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_01E96
    bclr #0,d6
L_UNIT142_01E96:
    btst #1,d6
    beq.w L_UNIT142_01EBC
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01EBC
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_01EBC
    bclr #1,d6
L_UNIT142_01EBC:
    move.l d6,20(a4)
    move.l d6,d0
    rts
ENTRY_UNIT142_01EC4:
    movem.l d0-d1/d4-d7/a0-a4/a6,-(a7)
    moveq #-1,d3
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_020B2
    movea.l 36(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_020B2
    movea.l 86(a3),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_020B2
L_UNIT142_01EEE:
    movea.l a4,a0
    movea.l $0004.w,a6
    bsr.w L_UNIT142_0307E
    tst.l d0
    beq.w L_UNIT142_0209E
    movea.l d0,a3
    move.l 20(a3),d4
    moveq #0,d5
    move.w 24(a3),d5
    moveq #0,d6
    move.w 26(a3),d6
    movea.l a3,a1
    nop
    nop
    cmpi.l #$00000400,d4
    bne.w L_UNIT142_01EEE
    move.l d5,d0
    andi.l #$00000080,d0
    bne.w L_UNIT142_01EEE
    bra.w L_UNIT142_020BA
