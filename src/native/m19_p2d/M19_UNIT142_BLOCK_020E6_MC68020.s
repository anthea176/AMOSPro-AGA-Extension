; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $020E6 source-verified against pinned P2d emitter.
; UNIT142+$020E6..$02198, 178 instructions/data bytes.
UNIT142_BLOCK_020E6_EDIT equ 0

    rts
L_UNIT142_020E8:
    bsr.w L_UNIT142_020FA
    tst.l d0
    beq.w L_UNIT142_020F6
    bra.w L_UNIT142_01F50
L_UNIT142_020F6:
    bra.w L_UNIT142_020B2
L_UNIT142_020FA:
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02132
    moveq #UNIT142_BLOCK_020E6_EDIT,d4
L_UNIT142_02108:
    bsr.w L_UNIT142_0213A
    tst.l d0
    beq.w L_UNIT142_02132
    addq.l #1,d4
    cmpi.l #$0000012D,d4
    bge.w L_UNIT142_02136
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_02136
    jsr -270(a6)
    bra.w L_UNIT142_02108
L_UNIT142_02132:
    moveq #1,d0
    rts
L_UNIT142_02136:
    moveq #0,d0
    rts
L_UNIT142_0213A:
    move.l 20(a4),d6
    andi.l #$00000003,d6
    btst #0,d6
    beq.w L_UNIT142_0216A
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0216A
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_0216A
    bclr #0,d6
L_UNIT142_0216A:
    btst #1,d6
    beq.w L_UNIT142_02190
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_02190
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_02190
    bclr #1,d6
L_UNIT142_02190:
    move.l d6,20(a4)
    move.l d6,d0
    rts
