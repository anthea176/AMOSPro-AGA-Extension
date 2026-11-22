; AGA_NATIVE_MIN_CPU: MC68020
; Source-backed UNIT156 main conversion body from pinned P2d emitter.
; UNIT156+$00218..$007EE (1494 bytes), instructions only, no data.
UNIT156_MIN_POINTER_BYTES equ 24

    move.l a0,d5
    cmpi.l #UNIT156_MIN_POINTER_BYTES,d5
    bls.w L_UNIT156_00302
    move.l d5,d0
    andi.l #$00000001,d0
    bne.w L_UNIT156_00302
    move.l d5,132(a2)
    movea.l d5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT156_00302
    move.l d5,d0
    subi.l #$00000018,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT156_00302
    movea.l d5,a4
    move.l -16(a4),d0
    cmp.l 128(a2),d0
    bne.w L_UNIT156_00302
    move.l #$00000000,d0
    move.w -12(a4),d0
    tst.l d0
    beq.w L_UNIT156_00286
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_UNIT156_00302
L_UNIT156_00286:
    move.l -20(a4),d0
    cmpi.l #$00014010,d0
    bcs.w L_UNIT156_00302
    subi.l #$00000010,d0
    tst.l d0
    blt.w L_UNIT156_00302
    move.l d0,136(a2)
    add.l d5,d0
    bcs.w L_UNIT156_00302
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT156_00302
    movea.l a2,a5
    bsr.w L_UNIT156_0031A
    tst.l d0
    beq.w L_UNIT156_00304
    bsr.w L_UNIT156_00448
    tst.l d0
    beq.w L_UNIT156_00304
    bsr.w L_UNIT156_006A0
    tst.l d0
    beq.w L_UNIT156_00304
    bsr.w L_UNIT156_00714
    tst.l d0
    beq.w L_UNIT156_00304
    move.l #$00000001,100(a5)
    bsr.w L_UNIT156_00714
    tst.l d0
    beq.w L_UNIT156_00304
    move.l #$00000001,d3
    bra.w L_UNIT156_0030A
L_UNIT156_00302:
    movea.l a2,a5
L_UNIT156_00304:
    move.l #$00000000,d3
L_UNIT156_0030A:
    bsr.w L_UNIT156_008A6
    lea 224(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_UNIT156_0031A:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 4(a5),a2
    move.l #$00000000,d4
    move.w (a2)+,d4
    tst.l d4
    beq.w L_UNIT156_0043A
    move.l d4,d0
    addq.l #1,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT156_0043A
    move.l d0,12(a5)
    movea.l d0,a1
L_UNIT156_0034E:
    move.b (a2)+,(a1)+
    subq.l #1,d4
    bne.w L_UNIT156_0034E
    lea L_UNIT156_00926(pc),a1
    move.l #$00000000,d0
    movea.l $0004.w,a6
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT156_0043A
    move.l d0,16(a5)
    movea.l d0,a6
    move.l 12(a5),d1
    move.l #$000003ED,d2
    jsr -30(a6)
    tst.l d0
    beq.w L_UNIT156_0043A
    move.l d0,20(a5)
    move.l d0,d1
    move.l a5,d2
    addi.l #$00000068,d2
    move.l #$0000000C,d3
    jsr -42(a6)
    cmpi.l #$0000000C,d0
    bne.w L_UNIT156_0043A
    cmpi.l #$464F524D,104(a5)
    bne.w L_UNIT156_0043A
    cmpi.l #$494C424D,112(a5)
    bne.w L_UNIT156_0043A
    move.l 108(a5),d4
    cmpi.l #$00000004,d4
    bcs.w L_UNIT156_0043A
    cmpi.l #$7FFFFFF7,d4
    bhi.w L_UNIT156_0043A
    addq.l #8,d4
    move.l d4,28(a5)
    move.l d4,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT156_0043A
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
    bne.w L_UNIT156_0043A
    move.l #$00000001,d0
    bra.w L_UNIT156_00440
L_UNIT156_0043A:
    move.l #$00000000,d0
L_UNIT156_00440:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT156_00448:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 24(a5),a0
    move.l 28(a5),d7
    subi.l #$0000000C,d7
    move.l a0,d0
    addi.l #$0000000C,d0
    movea.l d0,a0
L_UNIT156_00464:
    tst.l d7
    beq.w L_UNIT156_00528
    cmpi.l #$00000008,d7
    bcs.w L_UNIT156_00692
    move.l (a0)+,d3
    move.l (a0)+,d2
    subq.l #8,d7
    cmp.l d7,d2
    bhi.w L_UNIT156_00692
    move.l d2,d1
    andi.l #$00000001,d1
    add.l d2,d1
    cmp.l d7,d1
    bhi.w L_UNIT156_00692
    sub.l d1,d7
    cmpi.l #$424D4844,d3
    beq.w L_UNIT156_004BE
    cmpi.l #$434D4150,d3
    beq.w L_UNIT156_004D8
    cmpi.l #$43414D47,d3
    beq.w L_UNIT156_00500
    cmpi.l #$424F4459,d3
    beq.w L_UNIT156_004EC
    bra.w L_UNIT156_0051E
L_UNIT156_004BE:
    tst.l 32(a5)
    bne.w L_UNIT156_00692
    cmpi.l #$00000014,d2
    bne.w L_UNIT156_00692
    move.l a0,32(a5)
    bra.w L_UNIT156_0051E
L_UNIT156_004D8:
    tst.l 36(a5)
    bne.w L_UNIT156_00692
    move.l a0,36(a5)
    move.l d2,40(a5)
    bra.w L_UNIT156_0051E
L_UNIT156_004EC:
    tst.l 44(a5)
    bne.w L_UNIT156_00692
    move.l a0,44(a5)
    move.l d2,48(a5)
    bra.w L_UNIT156_0051E
L_UNIT156_00500:
    tst.l 52(a5)
    bne.w L_UNIT156_00692
    cmpi.l #$00000004,d2
    bne.w L_UNIT156_00692
    move.l #$00000001,52(a5)
    move.l (a0),92(a5)
L_UNIT156_0051E:
    move.l a0,d0
    add.l d1,d0
    movea.l d0,a0
    bra.w L_UNIT156_00464
L_UNIT156_00528:
    tst.l 32(a5)
    beq.w L_UNIT156_00692
    tst.l 36(a5)
    beq.w L_UNIT156_00692
    tst.l 44(a5)
    beq.w L_UNIT156_00692
    tst.l 48(a5)
    beq.w L_UNIT156_00692
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
    beq.w L_UNIT156_00692
    tst.l 60(a5)
    beq.w L_UNIT156_00692
    tst.l 64(a5)
    beq.w L_UNIT156_00692
    cmpi.l #$00000008,64(a5)
    bhi.w L_UNIT156_00692
    cmpi.l #$00000002,68(a5)
    bhi.w L_UNIT156_00692
    cmpi.l #$00000001,72(a5)
    bhi.w L_UNIT156_00692
    move.l 40(a5),d0
    tst.l d0
    beq.w L_UNIT156_00692
    cmpi.l #$00000300,d0
    bhi.w L_UNIT156_00692
    divu.w #$0003,d0
    move.l d0,d1
    swap d1
    tst.w d1
    bne.w L_UNIT156_00692
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
    bne.w L_UNIT156_00624
    andi.l #$00008EFD,d0
    bra.w L_UNIT156_00630
L_UNIT156_00624:
    move.l d0,d1
    andi.l #$00001000,d1
    beq.w L_UNIT156_00692
L_UNIT156_00630:
    move.l d0,52(a5)
    move.l d0,d1
    andi.l #$00000400,d1
    bne.w L_UNIT156_00692
    move.l d0,d1
    andi.l #$00000800,d1
    beq.w L_UNIT156_00672
    andi.l #$00000080,d0
    bne.w L_UNIT156_00692
    cmpi.l #$00000006,64(a5)
    beq.w L_UNIT156_0066E
    cmpi.l #$00000008,64(a5)
    bne.w L_UNIT156_00692
L_UNIT156_0066E:
    bra.w L_UNIT156_00688
L_UNIT156_00672:
    andi.l #$00000080,d0
    beq.w L_UNIT156_00688
    cmpi.l #$00000006,64(a5)
    bne.w L_UNIT156_00692
L_UNIT156_00688:
    move.l #$00000001,d0
    bra.w L_UNIT156_00698
L_UNIT156_00692:
    move.l #$00000000,d0
L_UNIT156_00698:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT156_006A0:
    movem.l d1-d7/a0-a4/a6,-(a7)
    cmpi.l #$00000140,56(a5)
    bne.w L_UNIT156_00706
    cmpi.l #$00000100,60(a5)
    bne.w L_UNIT156_00706
    cmpi.l #$00000000,68(a5)
    bne.w L_UNIT156_00706
    move.l 64(a5),d0
    cmpi.l #$00000004,d0
    blt.w L_UNIT156_00706
    cmpi.l #$00000008,d0
    bgt.w L_UNIT156_00706
    move.l 92(a5),d0
    andi.l #$00000C80,d0
    bne.w L_UNIT156_00706
    move.l 28(a5),d0
    cmpi.l #$00100000,d0
    bgt.w L_UNIT156_00706
    move.l #$00000001,d0
    bra.w L_UNIT156_0070C
L_UNIT156_00706:
    move.l #$00000000,d0
L_UNIT156_0070C:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT156_00714:
    movem.l d1-d7/a0-a4/a6,-(a7)
    bra.w L_UNIT156_0099E
L_UNIT156_0071C:
    move.l a0,d0
    add.l 48(a5),d0
    movea.l d0,a2
    movea.l 132(a5),a1
    tst.l 100(a5)
    beq.w L_UNIT156_0073E
    movea.l a1,a4
    move.l #$00004FFF,d0
L_UNIT156_00738:
    clr.l (a4)+
    dbra d0,L_UNIT156_00738
L_UNIT156_0073E:
    move.l #$000000FF,d4
L_UNIT156_00744:
    move.l #$00000000,d6
L_UNIT156_0074A:
    move.l #$00000028,d7
    move.l a5,d0
    addi.l #$000000A0,d0
    movea.l d0,a3
L_UNIT156_0075A:
    tst.l 72(a5)
    beq.w L_UNIT156_00788
    move.l a0,d0
    cmp.l a2,d0
    bcc.w L_UNIT156_00898
    move.l #$00000000,d1
    move.b (a0)+,d1
    cmpi.l #$00000080,d1
    beq.w L_UNIT156_0075A
    bhi.w L_UNIT156_007A8
    addq.l #1,d1
    move.l d1,d2
    bra.w L_UNIT156_0078A
L_UNIT156_00788:
    move.l d7,d2
L_UNIT156_0078A:
    cmp.l d7,d2
    bhi.w L_UNIT156_00898
    move.l a2,d0
    sub.l a0,d0
    cmp.l d2,d0
    bcs.w L_UNIT156_00898
    sub.l d2,d7
L_UNIT156_0079C:
    move.b (a0)+,(a3)+
    subq.l #1,d2
    bne.w L_UNIT156_0079C
    bra.w L_UNIT156_007CA
L_UNIT156_007A8:
    move.l #$00000101,d2
    sub.l d1,d2
    cmp.l d7,d2
    bhi.w L_UNIT156_00898
    move.l a0,d0
    cmp.l a2,d0
    bcc.w L_UNIT156_00898
    sub.l d2,d7
    move.b (a0)+,d0
L_UNIT156_007C2:
    move.b d0,(a3)+
    subq.l #1,d2
    bne.w L_UNIT156_007C2
L_UNIT156_007CA:
    tst.l d7
    bne.w L_UNIT156_0075A
    tst.l 100(a5)
    beq.w L_UNIT156_00850
    move.l a5,d0
    addi.l #$000000A0,d0
    movea.l d0,a3
    movea.l a1,a4
    move.l #$00000027,d2
    bra.w L_UNIT156_00932
