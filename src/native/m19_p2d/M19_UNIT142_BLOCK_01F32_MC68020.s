; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$01F32..$020E0, 430 instruction bytes.
UNIT142_BLOCK_01F32_EDIT equ 0

L_UNIT142_01F32:
    bne.w L_UNIT142_02098
    move.l d6,d0
    andi.l #$00000008,d0
    beq.w L_UNIT142_02098
    bra.w L_UNIT142_020E8
L_UNIT142_01F46:
    ori.w #$8100,-168(a5)
    bra.w L_UNIT142_020CE
L_UNIT142_01F50:
    movea.l 36(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_01F9C
    movea.l 86(a3),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_01F82
L_UNIT142_01F68:
    movea.l a4,a0
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_01F82
    movea.l d0,a1
    jsr -378(a6)
    bra.w L_UNIT142_01F68
L_UNIT142_01F82:
    movea.l 4(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_01F94
    movea.l a3,a0
    bsr.w L_UNIT142_0660A
L_UNIT142_01F94:
    move.l #$00000000,36(a2)
L_UNIT142_01F9C:
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0201C
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_01FB8
    jsr -228(a6)
L_UNIT142_01FB8:
    movea.l (a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01FE6
    movea.l 4(a2),a6
    movea.l 4(a4),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01FD6
    jsr -774(a6)
L_UNIT142_01FD6:
    movea.l (a4),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01FE6
    movea.l (a2),a0
    jsr -774(a6)
L_UNIT142_01FE6:
    movea.l $0004.w,a6
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01FFA
    jsr -672(a6)
L_UNIT142_01FFA:
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0200A
    jsr -672(a6)
L_UNIT142_0200A:
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -690(a6)
    move.l #$00000000,32(a2)
L_UNIT142_0201C:
    movea.l (a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_02034
    movea.l 4(a2),a6
    jsr -66(a6)
    move.l #$00000000,(a2)
L_UNIT142_02034:
    movea.l 8(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_02050
    movea.l $0004.w,a6
    jsr -414(a6)
    move.l #$00000000,8(a2)
L_UNIT142_02050:
    movea.l 4(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_0206C
    movea.l $0004.w,a6
    jsr -414(a6)
    move.l #$00000000,4(a2)
L_UNIT142_0206C:
    moveq #UNIT142_BLOCK_01F32_EDIT,d0
    move.l d0,(a2)
    move.l d0,4(a2)
    move.l d0,8(a2)
    move.l d0,12(a2)
    move.l d0,16(a2)
    move.l d0,20(a2)
    move.l d0,24(a2)
    move.l d0,28(a2)
    move.l d0,32(a2)
    move.l d0,36(a2)
    bra.w L_UNIT142_01F46
L_UNIT142_02098:
    move.l d5,d3
    bra.w L_UNIT142_020B2
L_UNIT142_0209E:
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_020B2
    jsr -270(a6)
    bra.w L_UNIT142_01EEE
L_UNIT142_020B2:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6
    moveq #0,d2
    rts
L_UNIT142_020BA:
    cmpi.l #$00000063,d5
    beq.w L_UNIT142_01EEE
    cmpi.l #$00000033,d5
    bra.w L_UNIT142_01F32
L_UNIT142_020CE:
    moveq #1,d1
    movea.l -8(a5),a0
    jsr 288(a0)
    move.l d5,d3
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6
    moveq #0,d2
