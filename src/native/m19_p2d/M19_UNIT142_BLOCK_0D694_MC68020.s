; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0D694 source-verified against pinned P2d emitter.
; UNIT142+$0D694..$0D7A4, 272 instructions/data bytes.
UNIT142_BLOCK_0D694_EDIT equ 1

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0D9A6
    movea.l 28(a2),a4
    move.l 20(a4),d0
    andi.l #UNIT142_BLOCK_0D694_EDIT,d0
    beq.w L_UNIT142_0D6DA
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0D9A6
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_0D9A6
    movea.l 28(a2),a4
    move.l 20(a4),d0
    andi.l #$FFFFFFFE,d0
    move.l d0,20(a4)
L_UNIT142_0D6DA:
    move.l 12(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    move.l 40(a2),d1
    add.l 84(a2),d1
    lsl.l #1,d1
    addq.l #1,d1
    mulu.w d1,d0
    move.l d0,56(a2)
    move.l d0,d6
    move.l #$00000001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_0D9A6
    move.l d0,52(a2)
    move.l #$00000020,d7
    move.l 96(a2),d0
    cmpi.l #$00000002,d0
    bne.w L_UNIT142_0D740
    move.l 108(a2),d0
    mulu.w #$0003,d0
    move.l d0,112(a2)
    addi.l #$00000043,d0
    andi.l #$FFFFFFFC,d0
    move.l d0,d7
L_UNIT142_0D740:
    move.l d7,116(a2)
    move.l 16(a2),d0
    addq.l #1,d0
    lsl.l #2,d0
    add.l d7,d0
    move.l d0,92(a2)
    move.l d0,60(a2)
    move.l #$00000000,68(a2)
L_UNIT142_0D75E:
    move.l 68(a2),d0
    cmp.l 16(a2),d0
    bge.w L_UNIT142_0D7A2
    movea.l 52(a2),a1
    move.l 56(a2),d6
    bsr.w L_UNIT142_0D9DE
    tst.l d0
    beq.w L_UNIT142_0D9A6
    move.l 60(a2),d1
    add.l d0,d1
    bcs.w L_UNIT142_0D9A6
    cmpi.l #$01000000,d1
    bhi.w L_UNIT142_0D9A6
    move.l d1,60(a2)
    move.l 68(a2),d0
    addq.l #1,d0
    move.l d0,68(a2)
    bra.w L_UNIT142_0D75E
L_UNIT142_0D7A2:
    move.l (a2),d0
