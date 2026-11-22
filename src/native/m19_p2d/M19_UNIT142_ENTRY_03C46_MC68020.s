; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 public entry $03C46 source-verified against pinned P2d emitter.
; UNIT142+$03C46..$040FC, 1206 instructions/data bytes.
UNIT142_ENTRY_03C46_ZERO equ 0

    movem.l d0-d2/d4-d7/a0-a6,-(a7)
    movea.l 456(a5),a0
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
    bsr.w L_UNIT142_03DA2
    tst.l d0
    beq.w L_UNIT142_03D8C
    bsr.w L_UNIT142_03E80
    tst.l d0
    beq.w L_UNIT142_03D8C
    bsr.w L_UNIT142_03EE6
    tst.l d0
    beq.w L_UNIT142_03D8C
    bsr.w L_UNIT142_03FF4
    tst.l d0
    beq.w L_UNIT142_03D8C
    move.l #$00000001,d3
    bra.w L_UNIT142_03D92
L_UNIT142_03D8C:
    move.l #$00000000,d3
L_UNIT142_03D92:
    bsr.w L_UNIT142_04082
    lea 128(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a6
    moveq #UNIT142_ENTRY_03C46_ZERO,d2
    rts
L_UNIT142_03DA2:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l (a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_03E72
    move.l (a2),d0
    tst.l d0
    beq.w L_UNIT142_03E72
    move.l d0,20(a5)
    tst.l 8(a2)
    beq.w L_UNIT142_03E72
    move.l 28(a2),d0
    tst.l d0
    beq.w L_UNIT142_03E72
    cmpi.l #$00000008,d0
    bhi.w L_UNIT142_03E72
    move.l d0,40(a5)
    move.l 24(a2),d0
    andi.l #$00000C80,d0
    bne.w L_UNIT142_03E72
    move.l 12(a2),d0
    tst.l d0
    ble.w L_UNIT142_03E72
    cmpi.l #$00007FFF,d0
    bhi.w L_UNIT142_03E72
    move.l d0,32(a5)
    move.l 16(a2),d0
    tst.l d0
    ble.w L_UNIT142_03E72
    cmpi.l #$00007FFF,d0
    bhi.w L_UNIT142_03E72
    move.l d0,36(a5)
    move.l 20(a2),d4
    tst.l d4
    ble.w L_UNIT142_03E72
    cmpi.l #$00000100,d4
    bhi.w L_UNIT142_03E72
    movea.l 20(a5),a0
    movea.l 48(a0),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_03E72
    move.l d0,24(a5)
    move.l #$00000000,d0
    move.w 2(a1),d0
    tst.l d0
    beq.w L_UNIT142_03E72
    cmpi.l #$00000100,d0
    bhi.w L_UNIT142_03E72
    cmp.l d0,d4
    bls.w L_UNIT142_03E64
    move.l d0,d4
L_UNIT142_03E64:
    move.l d4,28(a5)
    move.l #$00000001,d0
    bra.w L_UNIT142_03E78
L_UNIT142_03E72:
    move.l #$00000000,d0
L_UNIT142_03E78:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_03E80:
    movem.l d1-d7/a0-a4/a6,-(a7)
    movea.l 4(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_03ED8
    move.l #$00000000,d4
    move.w (a2)+,d4
    tst.l d4
    beq.w L_UNIT142_03ED8
    cmpi.l #$000000FF,d4
    bhi.w L_UNIT142_03ED8
    move.l d4,d0
    addq.l #1,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_03ED8
    move.l d0,8(a5)
    movea.l d0,a1
L_UNIT142_03EC6:
    move.b (a2)+,(a1)+
    subq.l #1,d4
    bne.w L_UNIT142_03EC6
    move.l #$00000001,d0
    bra.w L_UNIT142_03EDE
L_UNIT142_03ED8:
    move.l #$00000000,d0
L_UNIT142_03EDE:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_03EE6:
    movem.l d1-d7/a0-a4/a6,-(a7)
    move.l 28(a5),d4
    move.l d4,d0
    add.l d4,d0
    add.l d4,d0
    move.l d0,44(a5)
    move.l d0,d1
    andi.l #$00000001,d1
    add.l d1,d0
    addi.l #$00000030,d0
    move.l d0,48(a5)
    move.l 44(a5),d1
    lsl.l #2,d1
    add.l d1,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_03FE6
    move.l d0,52(a5)
    move.l d0,d1
    add.l 48(a5),d1
    move.l d1,56(a5)
    movea.l 52(a5),a0
    move.l #$464F524D,(a0)
    move.l #$494C424D,8(a0)
    move.l #$424D4844,12(a0)
    move.l #$00000014,16(a0)
    move.l #$434D4150,40(a0)
    move.l 48(a5),d0
    subi.l #$00000008,d0
    move.l d0,4(a0)
    move.l 32(a5),d0
    move.w d0,20(a0)
    move.w d0,36(a0)
    move.l 36(a5),d0
    move.w d0,22(a0)
    move.w d0,38(a0)
    move.l 40(a5),d0
    move.b d0,28(a0)
    move.w #$0101,34(a0)
    move.l 44(a5),44(a0)
    movea.l 24(a5),a0
    move.l #$00000000,d0
    move.l 28(a5),d1
    movea.l 56(a5),a1
    movea.l (a5),a2
    movea.l 8(a2),a6
    jsr -900(a6)
    movea.l 56(a5),a0
    move.l 52(a5),d0
    addi.l #$00000030,d0
    movea.l d0,a1
    move.l 28(a5),d4
L_UNIT142_03FCA:
    move.b (a0),(a1)+
    addq.l #4,a0
    move.b (a0),(a1)+
    addq.l #4,a0
    move.b (a0),(a1)+
    addq.l #4,a0
    subq.l #1,d4
    bne.w L_UNIT142_03FCA
    move.l #$00000001,d0
    bra.w L_UNIT142_03FEC
L_UNIT142_03FE6:
    move.l #$00000000,d0
L_UNIT142_03FEC:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_03FF4:
    movem.l d1-d7/a0-a4/a6,-(a7)
    lea L_UNIT142_0410A(pc),a1
    movea.l $0004.w,a6
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_04074
    move.l d0,12(a5)
    movea.l d0,a6
    move.l 8(a5),d1
    move.l #$000003EE,d2
    jsr -30(a6)
    tst.l d0
    beq.w L_UNIT142_04074
    move.l d0,16(a5)
    move.l #$00000001,60(a5)
    move.l d0,d1
    move.l 52(a5),d2
    move.l 48(a5),d3
    jsr -48(a6)
    cmp.l 48(a5),d0
    bne.w L_UNIT142_04074
    move.l 16(a5),d1
    movea.l 12(a5),a6
    jsr -36(a6)
    move.l d0,d4
    move.l #$00000000,16(a5)
    tst.l d4
    beq.w L_UNIT142_04074
    move.l #$00000001,64(a5)
    move.l #$00000001,d0
    bra.w L_UNIT142_0407A
L_UNIT142_04074:
    move.l #$00000000,d0
L_UNIT142_0407A:
    movem.l (a7)+,d1-d7/a0-a4/a6
    tst.l d0
    rts
L_UNIT142_04082:
    movem.l d1-d7/a0-a4/a6,-(a7)
    tst.l 16(a5)
    beq.w L_UNIT142_0409A
    movea.l 12(a5),a6
    move.l 16(a5),d1
    jsr -36(a6)
L_UNIT142_0409A:
    tst.l 60(a5)
    beq.w L_UNIT142_040B6
    tst.l 64(a5)
    bne.w L_UNIT142_040B6
    movea.l 12(a5),a6
    move.l 8(a5),d1
    jsr -72(a6)
L_UNIT142_040B6:
    tst.l 52(a5)
    beq.w L_UNIT142_040CA
    movea.l 52(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_040CA:
    tst.l 8(a5)
    beq.w L_UNIT142_040DE
    movea.l 8(a5),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_040DE:
    tst.l 12(a5)
    beq.w L_UNIT142_040F2
    movea.l 12(a5),a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT142_040F2:
    move.l #$00000001,d0
    bra.w L_UNIT142_04102
