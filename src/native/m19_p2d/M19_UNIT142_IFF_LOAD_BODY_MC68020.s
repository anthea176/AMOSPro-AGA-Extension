; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 IFF load preflight body source-verified against pinned P2d emitter.
; UNIT142+$00D3C..$0153A, 2046 instructions/data bytes.
UNIT142_IFF_LOAD_ZERO equ 0

    movem.l d0-d2/d4-d7/a0-a6,-(a7)
    movea.l 456(a5),a0
    move.l d3,d4
    movea.l d3,a1
    lea -128(a7),a7
    movea.l a7,a5
    move.l #$00000000,(a5)
    move.l #$00000000,4(a5)
    move.l #$00000000,8(a5)
    move.l #$00000000,12(a5)
    move.l #$00000000,16(a5)
    move.l #$00000000,20(a5)
    move.l #$00000000,24(a5)
    move.l #$00000000,28(a5)
    move.l #$00000000,32(a5)
    move.l #$00000000,36(a5)
    move.l #$00000000,40(a5)
    move.l #$00000000,44(a5)
    move.l #$00000000,48(a5)
    move.l #$00000000,52(a5)
    move.l #$00000000,56(a5)
    move.l #$00000000,60(a5)
    move.l #$00000000,64(a5)
    move.l #$00000000,68(a5)
    move.l #$00000000,72(a5)
    move.l #$00000000,76(a5)
    move.l #$00000000,80(a5)
    move.l #$00000000,84(a5)
    move.l #$00000000,88(a5)
    move.l #$00000000,92(a5)
    move.l #$00000000,96(a5)
    move.l #$00000000,100(a5)
    move.l #$00000000,104(a5)
    move.l #$00000000,108(a5)
    move.l #$00000000,112(a5)
    move.l #$00000000,116(a5)
    move.l #$00000000,120(a5)
    move.l #$00000000,124(a5)
    move.l a0,(a5)
    move.l a1,4(a5)
    move.l d4,8(a5)
    bsr.w L_UNIT142_00ECE
    tst.l d0
    beq.w L_UNIT142_00EB8
    bsr.w L_UNIT142_00FFC
    tst.l d0
    beq.w L_UNIT142_00EB8
    bsr.w L_UNIT142_01254
    tst.l d0
    beq.w L_UNIT142_00EB8
    bsr.w L_UNIT142_01360
    tst.l d0
    beq.w L_UNIT142_00EB8
    bsr.w L_UNIT142_01492
    tst.l d0
    beq.w L_UNIT142_00EB8
    movea.l (a5),a2
    movea.l 8(a2),a6
    jsr -228(a6)
    move.l #$00000001,100(a5)
    bsr.w L_UNIT142_01360
    tst.l d0
    beq.w L_UNIT142_00EB8
    bsr.w L_UNIT142_0150E
    tst.l d0
    beq.w L_UNIT142_00EB8
    move.l #$00000001,d3
    bra.w L_UNIT142_00EBE
L_UNIT142_00EB8:
    move.l #$00000000,d3
L_UNIT142_00EBE:
    bsr.w L_UNIT142_01548
    lea 128(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a6
    moveq #UNIT142_IFF_LOAD_ZERO,d2
    rts
L_UNIT142_00ECE:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 4(a5),a2
    move.l #$00000000,d4
    move.w (a2)+,d4
    tst.l d4
    beq.w L_UNIT142_00FEE
    move.l d4,d0
    addq.l #1,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_00FEE
    move.l d0,12(a5)
    movea.l d0,a1
L_UNIT142_00F02:
    move.b (a2)+,(a1)+
    subq.l #1,d4
    bne.w L_UNIT142_00F02
    lea L_UNIT142_015C8(pc),a1
    move.l #$00000000,d0
    movea.l $0004.w,a6
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_00FEE
    move.l d0,16(a5)
    movea.l d0,a6
    move.l 12(a5),d1
    move.l #$000003ED,d2
    jsr -30(a6)
    tst.l d0
    beq.w L_UNIT142_00FEE
    move.l d0,20(a5)
    move.l d0,d1
    move.l a5,d2
    addi.l #$00000068,d2
    move.l #$0000000C,d3
    jsr -42(a6)
    cmpi.l #$0000000C,d0
    bne.w L_UNIT142_00FEE
    cmpi.l #$464F524D,104(a5)
    bne.w L_UNIT142_00FEE
    cmpi.l #$494C424D,112(a5)
    bne.w L_UNIT142_00FEE
    move.l 108(a5),d4
    cmpi.l #$00000004,d4
    bcs.w L_UNIT142_00FEE
    cmpi.l #$7FFFFFF7,d4
    bhi.w L_UNIT142_00FEE
    addq.l #8,d4
    move.l d4,28(a5)
    move.l d4,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_00FEE
    move.l d0,24(a5)
    movea.l d0,a2
    move.l 104(a5),(a2)
    move.l 108(a5),4(a2)
    move.l 112(a5),8(a2)
    move.l 20(a5),d1
    move.l a2,d2
    addi.l #$0000000C,d2
    move.l d4,d3
    subi.l #$0000000C,d3
    move.l d3,d4
    movea.l 16(a5),a6
    jsr -42(a6)
    cmp.l d4,d0
    bne.w L_UNIT142_00FEE
    move.l #$00000001,d0
    bra.w L_UNIT142_00FF4
L_UNIT142_00FEE:
    move.l #$00000000,d0
L_UNIT142_00FF4:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_00FFC:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 24(a5),a0
    move.l 28(a5),d7
    subi.l #$0000000C,d7
    move.l a0,d0
    addi.l #$0000000C,d0
    movea.l d0,a0
L_UNIT142_01018:
    tst.l d7
    beq.w L_UNIT142_010DC
    cmpi.l #$00000008,d7
    bcs.w L_UNIT142_01246
    move.l (a0)+,d3
    move.l (a0)+,d2
    subq.l #8,d7
    cmp.l d7,d2
    bhi.w L_UNIT142_01246
    move.l d2,d1
    andi.l #$00000001,d1
    add.l d2,d1
    cmp.l d7,d1
    bhi.w L_UNIT142_01246
    sub.l d1,d7
    cmpi.l #$424D4844,d3
    beq.w L_UNIT142_01072
    cmpi.l #$434D4150,d3
    beq.w L_UNIT142_0108C
    cmpi.l #$43414D47,d3
    beq.w L_UNIT142_010B4
    cmpi.l #$424F4459,d3
    beq.w L_UNIT142_010A0
    bra.w L_UNIT142_010D2
L_UNIT142_01072:
    tst.l 32(a5)
    bne.w L_UNIT142_01246
    cmpi.l #$00000014,d2
    bne.w L_UNIT142_01246
    move.l a0,32(a5)
    bra.w L_UNIT142_010D2
L_UNIT142_0108C:
    tst.l 36(a5)
    bne.w L_UNIT142_01246
    move.l a0,36(a5)
    move.l d2,40(a5)
    bra.w L_UNIT142_010D2
L_UNIT142_010A0:
    tst.l 44(a5)
    bne.w L_UNIT142_01246
    move.l a0,44(a5)
    move.l d2,48(a5)
    bra.w L_UNIT142_010D2
L_UNIT142_010B4:
    tst.l 52(a5)
    bne.w L_UNIT142_01246
    cmpi.l #$00000004,d2
    bne.w L_UNIT142_01246
    move.l #$00000001,52(a5)
    move.l (a0),92(a5)
L_UNIT142_010D2:
    move.l a0,d0
    add.l d1,d0
    movea.l d0,a0
    bra.w L_UNIT142_01018
L_UNIT142_010DC:
    tst.l 32(a5)
    beq.w L_UNIT142_01246
    tst.l 36(a5)
    beq.w L_UNIT142_01246
    tst.l 44(a5)
    beq.w L_UNIT142_01246
    tst.l 48(a5)
    beq.w L_UNIT142_01246
    movea.l 32(a5),a0
    move.l #$00000000,d0
    move.w (a0),d0
    move.l d0,56(a5)
    move.l #$00000000,d0
    move.w 2(a0),d0
    move.l d0,60(a5)
    move.l #$00000000,d0
    move.b 8(a0),d0
    move.l d0,64(a5)
    move.l #$00000000,d0
    move.b 9(a0),d0
    move.l d0,68(a5)
    move.l #$00000000,d0
    move.b 10(a0),d0
    move.l d0,72(a5)
    tst.l 56(a5)
    beq.w L_UNIT142_01246
    tst.l 60(a5)
    beq.w L_UNIT142_01246
    tst.l 64(a5)
    beq.w L_UNIT142_01246
    cmpi.l #$00000008,64(a5)
    bhi.w L_UNIT142_01246
    cmpi.l #$00000002,68(a5)
    bhi.w L_UNIT142_01246
    cmpi.l #$00000001,72(a5)
    bhi.w L_UNIT142_01246
    move.l 40(a5),d0
    tst.l d0
    beq.w L_UNIT142_01246
    cmpi.l #$00000300,d0
    bhi.w L_UNIT142_01246
    divu.w #$0003,d0
    move.l d0,d1
    swap d1
    tst.w d1
    bne.w L_UNIT142_01246
    andi.l #$0000FFFF,d0
    move.l d0,40(a5)
    move.l 56(a5),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l d0,76(a5)
    move.l 92(a5),d0
    move.l d0,d1
    andi.l #$FFFF0000,d1
    bne.w L_UNIT142_011D8
    andi.l #$00008EFD,d0
    bra.w L_UNIT142_011E4
L_UNIT142_011D8:
    move.l d0,d1
    andi.l #$00001000,d1
    beq.w L_UNIT142_01246
L_UNIT142_011E4:
    move.l d0,52(a5)
    move.l d0,d1
    andi.l #$00000400,d1
    bne.w L_UNIT142_01246
    move.l d0,d1
    andi.l #$00000800,d1
    beq.w L_UNIT142_01226
    andi.l #$00000080,d0
    bne.w L_UNIT142_01246
    cmpi.l #$00000006,64(a5)
    beq.w L_UNIT142_01222
    cmpi.l #$00000008,64(a5)
    bne.w L_UNIT142_01246
L_UNIT142_01222:
    bra.w L_UNIT142_0123C
L_UNIT142_01226:
    andi.l #$00000080,d0
    beq.w L_UNIT142_0123C
    cmpi.l #$00000006,64(a5)
    bne.w L_UNIT142_01246
L_UNIT142_0123C:
    move.l #$00000001,d0
    bra.w L_UNIT142_0124C
L_UNIT142_01246:
    move.l #$00000000,d0
L_UNIT142_0124C:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_01254:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l (a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_01352
    move.l (a2),d0
    tst.l d0
    beq.w L_UNIT142_01352
    move.l d0,88(a5)
    tst.l 8(a2)
    beq.w L_UNIT142_01352
    move.l 12(a2),d0
    cmp.l 56(a5),d0
    bne.w L_UNIT142_01352
    move.l 16(a2),d0
    cmp.l 60(a5),d0
    bne.w L_UNIT142_01352
    move.l 28(a2),d0
    cmp.l 64(a5),d0
    bne.w L_UNIT142_01352
    move.l 24(a2),d0
    move.l 52(a5),d1
    move.l d1,d2
    andi.l #$FFFF0000,d2
    bne.w L_UNIT142_012B4
    andi.l #$00008EFD,d0
L_UNIT142_012B4:
    cmp.l d1,d0
    bne.w L_UNIT142_01352
    movea.l 32(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_01352
    tst.l 8(a3)
    beq.w L_UNIT142_012D4
    movea.l (a3),a0
    bra.w L_UNIT142_012D8
L_UNIT142_012D4:
    movea.l 4(a3),a0
L_UNIT142_012D8:
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01352
    movea.l (a0),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_01352
    move.l d0,80(a5)
    move.l #$00000000,d0
    move.w (a3),d0
    cmp.l 76(a5),d0
    bcs.w L_UNIT142_01352
    move.l d0,84(a5)
    move.l #$00000000,d0
    move.w 2(a3),d0
    cmp.l 60(a5),d0
    bcs.w L_UNIT142_01352
    move.l #$00000000,d0
    move.b 5(a3),d0
    cmp.l 64(a5),d0
    bne.w L_UNIT142_01352
    move.l a3,d0
    addq.l #8,d0
    movea.l d0,a0
    move.l 64(a5),d1
L_UNIT142_01330:
    move.l (a0)+,d0
    tst.l d0
    beq.w L_UNIT142_01352
    cmpi.l #$FFFFFFFF,d0
    beq.w L_UNIT142_01352
    subq.l #1,d1
    bne.w L_UNIT142_01330
    move.l #$00000001,d0
    bra.w L_UNIT142_01358
L_UNIT142_01352:
    move.l #$00000000,d0
L_UNIT142_01358:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_01360:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 44(a5),a0
    move.l a0,d0
    add.l 48(a5),d0
    movea.l d0,a2
    move.l #$00000000,d4
    move.l #$00000000,d3
L_UNIT142_0137C:
    move.l #$00000000,d5
    movea.l 80(a5),a3
    move.l a3,d0
    addq.l #8,d0
    movea.l d0,a4
L_UNIT142_0138C:
    move.l 76(a5),d6
    movea.l #$00000000,a6
    cmp.l 64(a5),d5
    bcc.w L_UNIT142_013AC
    tst.l 100(a5)
    beq.w L_UNIT142_013AC
    move.l (a4)+,d0
    add.l d3,d0
    movea.l d0,a6
L_UNIT142_013AC:
    tst.l 72(a5)
    beq.w L_UNIT142_013DA
    move.l a0,d0
    cmp.l a2,d0
    bcc.w L_UNIT142_01484
    move.l #$00000000,d1
    move.b (a0)+,d1
    cmpi.l #$00000080,d1
    beq.w L_UNIT142_013AC
    bhi.w L_UNIT142_01406
    addq.l #1,d1
    move.l d1,d2
    bra.w L_UNIT142_013DE
L_UNIT142_013DA:
    move.l d6,d1
    move.l d1,d2
L_UNIT142_013DE:
    cmp.l d6,d1
    bhi.w L_UNIT142_01484
    move.l a2,d0
    sub.l a0,d0
    cmp.l d1,d0
    bcs.w L_UNIT142_01484
    sub.l d1,d6
L_UNIT142_013F0:
    move.b (a0)+,d0
    move.l a6,d7
    tst.l d7
    beq.w L_UNIT142_013FC
    move.b d0,(a6)+
L_UNIT142_013FC:
    subq.l #1,d2
    bne.w L_UNIT142_013F0
    bra.w L_UNIT142_01430
L_UNIT142_01406:
    move.l #$00000101,d2
    sub.l d1,d2
    cmp.l d6,d2
    bhi.w L_UNIT142_01484
    sub.l d2,d6
    move.l a0,d0
    cmp.l a2,d0
    bcc.w L_UNIT142_01484
    move.b (a0)+,d0
L_UNIT142_01420:
    move.l a6,d7
    tst.l d7
    beq.w L_UNIT142_0142A
    move.b d0,(a6)+
L_UNIT142_0142A:
    subq.l #1,d2
    bne.w L_UNIT142_01420
L_UNIT142_01430:
    tst.l d6
    bne.w L_UNIT142_013AC
    addq.l #1,d5
    move.l 64(a5),d0
    cmpi.l #$00000001,68(a5)
    bne.w L_UNIT142_0144A
    addq.l #1,d0
L_UNIT142_0144A:
    cmp.l d0,d5
    bcs.w L_UNIT142_0138C
    add.l 84(a5),d3
    addq.l #1,d4
    cmp.l 60(a5),d4
    bcs.w L_UNIT142_0137C
L_UNIT142_0145E:
    move.l a0,d0
    cmp.l a2,d0
    beq.w L_UNIT142_0147A
    tst.l 72(a5)
    beq.w L_UNIT142_01484
    cmpi.b #$80,(a0)+
    bne.w L_UNIT142_01484
    bra.w L_UNIT142_0145E
L_UNIT142_0147A:
    move.l #$00000001,d0
    bra.w L_UNIT142_0148A
L_UNIT142_01484:
    move.l #$00000000,d0
L_UNIT142_0148A:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_01492:
    movem.l d1-d7/a0-a4/a6,-(a7)
    move.l 40(a5),d0
    move.l d0,d1
    lsl.l #1,d0
    add.l d1,d0
    lsl.l #2,d0
    addq.l #8,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_01500
    move.l d0,96(a5)
    movea.l d0,a1
    move.l 40(a5),d0
    swap d0
    move.l d0,(a1)+
    movea.l 36(a5),a0
    move.l 40(a5),d4
    move.l d4,d0
    add.l d4,d0
    add.l d0,d4
L_UNIT142_014D4:
    move.l #$00000000,d0
    move.b (a0)+,d0
    move.l d0,d1
    lsl.l #8,d0
    or.l d1,d0
    move.l d0,d1
    swap d0
    or.l d1,d0
    move.l d0,(a1)+
    subq.l #1,d4
    bne.w L_UNIT142_014D4
    move.l #$00000000,(a1)
    move.l #$00000001,d0
    bra.w L_UNIT142_01506
L_UNIT142_01500:
    move.l #$00000000,d0
L_UNIT142_01506:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_0150E:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 96(a5),a1
    move.l 88(a5),d0
    addi.l #$0000002C,d0
    movea.l d0,a0
    movea.l (a5),a2
    movea.l 8(a2),a6
    jsr -882(a6)
    jsr -270(a6)
    move.l #$00000001,d0
    bra.w L_UNIT142_01540
