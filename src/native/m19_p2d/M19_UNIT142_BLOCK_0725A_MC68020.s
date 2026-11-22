; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0725A source-verified against pinned P2d emitter.
; UNIT142+$0725A..$0733C, 226 instructions/data bytes.
UNIT142_BLOCK_0725A_EDIT equ 1

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_0748E
    movea.l 28(a2),a4
    move.l 20(a4),d0
    andi.l #UNIT142_BLOCK_0725A_EDIT,d0
    beq.w L_UNIT142_072A0
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0748E
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_0748E
    movea.l 28(a2),a4
    move.l 20(a4),d0
    andi.l #$FFFFFFFE,d0
    move.l d0,20(a4)
L_UNIT142_072A0:
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
    beq.w L_UNIT142_0748E
    move.l d0,52(a2)
    move.l 16(a2),d0
    addq.l #1,d0
    lsl.l #2,d0
    addi.l #$00000020,d0
    move.l d0,92(a2)
    move.l d0,60(a2)
    move.l #$00000000,68(a2)
L_UNIT142_072F6:
    move.l 68(a2),d0
    cmp.l 16(a2),d0
    bge.w L_UNIT142_0733A
    movea.l 52(a2),a1
    move.l 56(a2),d6
    bsr.w L_UNIT142_074B2
    tst.l d0
    beq.w L_UNIT142_0748E
    move.l 60(a2),d1
    add.l d0,d1
    bcs.w L_UNIT142_0748E
    cmpi.l #$01000000,d1
    bhi.w L_UNIT142_0748E
    move.l d1,60(a2)
    move.l 68(a2),d0
    addq.l #1,d0
    move.l d0,68(a2)
    bra.w L_UNIT142_072F6
L_UNIT142_0733A:
    move.l (a2),d0
