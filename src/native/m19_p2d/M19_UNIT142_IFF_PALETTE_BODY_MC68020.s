; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 IFF screen and palette validation source-verified against pinned P2d emitter.
; UNIT142+$015D8..$01BC4, 1516 instructions/data bytes.
UNIT142_IFF_PALETTE_CAP equ 7

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a0
    move.l d3,d4
    move.l (a3)+,d3
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
    cmpi.l #UNIT142_IFF_PALETTE_CAP,8(a5)
    bhi.w L_UNIT142_017B6
    bsr.w L_UNIT142_017CC
    tst.l d0
    beq.w L_UNIT142_017B6
    bsr.w L_UNIT142_018FA
    tst.l d0
    beq.w L_UNIT142_017B6
    cmpi.l #$00000000,8(a5)
    beq.w L_UNIT142_0177E
    cmpi.l #$00000001,8(a5)
    beq.w L_UNIT142_01786
    cmpi.l #$00000002,8(a5)
    beq.w L_UNIT142_0178E
    cmpi.l #$00000003,8(a5)
    beq.w L_UNIT142_01796
    cmpi.l #$00000004,8(a5)
    beq.w L_UNIT142_0179E
    cmpi.l #$00000005,8(a5)
    beq.w L_UNIT142_017A6
    cmpi.l #$00000006,8(a5)
    beq.w L_UNIT142_017AE
    move.l #$00000001,d3
    move.l 64(a5),d0
L_UNIT142_01772:
    lsl.l #1,d3
    subq.l #1,d0
    bne.w L_UNIT142_01772
    bra.w L_UNIT142_017BC
L_UNIT142_0177E:
    move.l 56(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_01786:
    move.l 60(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_0178E:
    move.l 64(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_01796:
    move.l 40(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_0179E:
    move.l 72(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_017A6:
    move.l 92(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_017AE:
    move.l 52(a5),d3
    bra.w L_UNIT142_017BC
L_UNIT142_017B6:
    move.l #$FFFFFFFF,d3
L_UNIT142_017BC:
    bsr.w L_UNIT142_01B52
    lea 128(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_UNIT142_017CC:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 4(a5),a2
    move.l #$00000000,d4
    move.w (a2)+,d4
    tst.l d4
    beq.w L_UNIT142_018EC
    move.l d4,d0
    addq.l #1,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_018EC
    move.l d0,12(a5)
    movea.l d0,a1
L_UNIT142_01800:
    move.b (a2)+,(a1)+
    subq.l #1,d4
    bne.w L_UNIT142_01800
    lea L_UNIT142_01BD2(pc),a1
    move.l #$00000000,d0
    movea.l $0004.w,a6
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_018EC
    move.l d0,16(a5)
    movea.l d0,a6
    move.l 12(a5),d1
    move.l #$000003ED,d2
    jsr -30(a6)
    tst.l d0
    beq.w L_UNIT142_018EC
    move.l d0,20(a5)
    move.l d0,d1
    move.l a5,d2
    addi.l #$00000068,d2
    move.l #$0000000C,d3
    jsr -42(a6)
    cmpi.l #$0000000C,d0
    bne.w L_UNIT142_018EC
    cmpi.l #$464F524D,104(a5)
    bne.w L_UNIT142_018EC
    cmpi.l #$494C424D,112(a5)
    bne.w L_UNIT142_018EC
    move.l 108(a5),d4
    cmpi.l #$00000004,d4
    bcs.w L_UNIT142_018EC
    cmpi.l #$7FFFFFF7,d4
    bhi.w L_UNIT142_018EC
    addq.l #8,d4
    move.l d4,28(a5)
    move.l d4,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_018EC
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
    bne.w L_UNIT142_018EC
    move.l #$00000001,d0
    bra.w L_UNIT142_018F2
L_UNIT142_018EC:
    move.l #$00000000,d0
L_UNIT142_018F2:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_018FA:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 24(a5),a0
    move.l 28(a5),d7
    subi.l #$0000000C,d7
    move.l a0,d0
    addi.l #$0000000C,d0
    movea.l d0,a0
L_UNIT142_01916:
    tst.l d7
    beq.w L_UNIT142_019DA
    cmpi.l #$00000008,d7
    bcs.w L_UNIT142_01B44
    move.l (a0)+,d3
    move.l (a0)+,d2
    subq.l #8,d7
    cmp.l d7,d2
    bhi.w L_UNIT142_01B44
    move.l d2,d1
    andi.l #$00000001,d1
    add.l d2,d1
    cmp.l d7,d1
    bhi.w L_UNIT142_01B44
    sub.l d1,d7
    cmpi.l #$424D4844,d3
    beq.w L_UNIT142_01970
    cmpi.l #$434D4150,d3
    beq.w L_UNIT142_0198A
    cmpi.l #$43414D47,d3
    beq.w L_UNIT142_019B2
    cmpi.l #$424F4459,d3
    beq.w L_UNIT142_0199E
    bra.w L_UNIT142_019D0
L_UNIT142_01970:
    tst.l 32(a5)
    bne.w L_UNIT142_01B44
    cmpi.l #$00000014,d2
    bne.w L_UNIT142_01B44
    move.l a0,32(a5)
    bra.w L_UNIT142_019D0
L_UNIT142_0198A:
    tst.l 36(a5)
    bne.w L_UNIT142_01B44
    move.l a0,36(a5)
    move.l d2,40(a5)
    bra.w L_UNIT142_019D0
L_UNIT142_0199E:
    tst.l 44(a5)
    bne.w L_UNIT142_01B44
    move.l a0,44(a5)
    move.l d2,48(a5)
    bra.w L_UNIT142_019D0
L_UNIT142_019B2:
    tst.l 52(a5)
    bne.w L_UNIT142_01B44
    cmpi.l #$00000004,d2
    bne.w L_UNIT142_01B44
    move.l #$00000001,52(a5)
    move.l (a0),92(a5)
L_UNIT142_019D0:
    move.l a0,d0
    add.l d1,d0
    movea.l d0,a0
    bra.w L_UNIT142_01916
L_UNIT142_019DA:
    tst.l 32(a5)
    beq.w L_UNIT142_01B44
    tst.l 36(a5)
    beq.w L_UNIT142_01B44
    tst.l 44(a5)
    beq.w L_UNIT142_01B44
    tst.l 48(a5)
    beq.w L_UNIT142_01B44
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
    beq.w L_UNIT142_01B44
    tst.l 60(a5)
    beq.w L_UNIT142_01B44
    tst.l 64(a5)
    beq.w L_UNIT142_01B44
    cmpi.l #$00000008,64(a5)
    bhi.w L_UNIT142_01B44
    cmpi.l #$00000002,68(a5)
    bhi.w L_UNIT142_01B44
    cmpi.l #$00000001,72(a5)
    bhi.w L_UNIT142_01B44
    move.l 40(a5),d0
    tst.l d0
    beq.w L_UNIT142_01B44
    cmpi.l #$00000300,d0
    bhi.w L_UNIT142_01B44
    divu.w #$0003,d0
    move.l d0,d1
    swap d1
    tst.w d1
    bne.w L_UNIT142_01B44
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
    bne.w L_UNIT142_01AD6
    andi.l #$00008EFD,d0
    bra.w L_UNIT142_01AE2
L_UNIT142_01AD6:
    move.l d0,d1
    andi.l #$00001000,d1
    beq.w L_UNIT142_01B44
L_UNIT142_01AE2:
    move.l d0,52(a5)
    move.l d0,d1
    andi.l #$00000400,d1
    bne.w L_UNIT142_01B44
    move.l d0,d1
    andi.l #$00000800,d1
    beq.w L_UNIT142_01B24
    andi.l #$00000080,d0
    bne.w L_UNIT142_01B44
    cmpi.l #$00000006,64(a5)
    beq.w L_UNIT142_01B20
    cmpi.l #$00000008,64(a5)
    bne.w L_UNIT142_01B44
L_UNIT142_01B20:
    bra.w L_UNIT142_01B3A
L_UNIT142_01B24:
    andi.l #$00000080,d0
    beq.w L_UNIT142_01B3A
    cmpi.l #$00000006,64(a5)
    bne.w L_UNIT142_01B44
L_UNIT142_01B3A:
    move.l #$00000001,d0
    bra.w L_UNIT142_01B4A
L_UNIT142_01B44:
    move.l #$00000000,d0
L_UNIT142_01B4A:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_01B52:
    movem.l d1-d7/a0-a4/a6,-(a7)
    tst.l 20(a5)
    beq.w L_UNIT142_01B6A
    movea.l 16(a5),a6
    move.l 20(a5),d1
    jsr -36(a6)
L_UNIT142_01B6A:
    tst.l 96(a5)
    beq.w L_UNIT142_01B7E
    movea.l 96(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_01B7E:
    tst.l 24(a5)
    beq.w L_UNIT142_01B92
    movea.l 24(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_01B92:
    tst.l 12(a5)
    beq.w L_UNIT142_01BA6
    movea.l 12(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_01BA6:
    tst.l 16(a5)
    beq.w L_UNIT142_01BBA
    movea.l 16(a5),a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT142_01BBA:
    move.l #$00000001,d0
    bra.w L_UNIT142_01BCA
