; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $07360 source-verified against pinned P2d emitter.
; UNIT142+$07360..$07468, 264 instructions/data bytes.
UNIT142_BLOCK_07360_EDIT equ 1095188816

    tst.l d0
    beq.w L_UNIT142_0748E
    move.l d0,64(a2)
    move.l 60(a2),d1
    add.l d1,d0
    bcs.w L_UNIT142_0747A
    move.l d0,80(a2)
    movea.l 64(a2),a0
    move.l #UNIT142_BLOCK_07360_EDIT,(a0)
    move.w #$4943,4(a0)
    move.w #$0001,6(a0)
    move.l 84(a2),d0
    move.w d0,8(a0)
    move.w #$0001,10(a0)
    move.l 12(a2),d0
    move.w d0,12(a0)
    move.l 16(a2),d0
    move.w d0,14(a0)
    move.l 40(a2),d0
    move.w d0,16(a0)
    move.l 40(a2),d0
    add.l 84(a2),d0
    lsl.l #1,d0
    move.w d0,18(a0)
    move.l #$00000020,20(a0)
    move.l 92(a2),d0
    move.l d0,24(a0)
    move.l 60(a2),d0
    move.l d0,28(a0)
    move.l 64(a2),d0
    addi.l #$00000020,d0
    move.l d0,72(a2)
    move.l 64(a2),d0
    add.l 92(a2),d0
    move.l d0,76(a2)
    move.l #$00000000,68(a2)
L_UNIT142_073FC:
    move.l 68(a2),d0
    cmp.l 16(a2),d0
    bge.w L_UNIT142_07452
    move.l 76(a2),d0
    sub.l 64(a2),d0
    movea.l 72(a2),a4
    move.l d0,(a4)+
    move.l a4,72(a2)
    movea.l 76(a2),a1
    move.l 80(a2),d6
    sub.l a1,d6
    bsr.w L_UNIT142_074B2
    tst.l d0
    beq.w L_UNIT142_0747A
    move.l 76(a2),d1
    add.l d0,d1
    bcs.w L_UNIT142_0747A
    cmp.l 80(a2),d1
    bhi.w L_UNIT142_0747A
    move.l d1,76(a2)
    move.l 68(a2),d0
    addq.l #1,d0
    move.l d0,68(a2)
    bra.w L_UNIT142_073FC
L_UNIT142_07452:
    move.l 76(a2),d0
    cmp.l 80(a2),d0
    bne.w L_UNIT142_0747A
    movea.l 72(a2),a4
    move.l 60(a2),d0
    move.l d0,(a4)
