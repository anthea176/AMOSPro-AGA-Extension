; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 verified block $0D99A source-verified against pinned P2d emitter.
; UNIT142+$0D99A..$0DCFC, 866 instructions/data bytes.
UNIT142_BLOCK_0D99A_VALUE equ 8

    move.l #$00000000,64(a2)
    bra.w L_UNIT142_0D9A6
L_UNIT142_0D9A6:
    movea.l 52(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_0D9BA
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_0D9BA:
    movea.l 100(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_0D9CE
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_0D9CE:
    move.l 88(a2),d3
    lea 224(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_UNIT142_0D9DE:
    movea.l 32(a2),a0
    addq.l #8,a0
    move.l 4(a2),d0
    move.l 8(a2),d1
    add.l 68(a2),d1
    move.l 12(a2),d2
    move.l 40(a2),d3
    move.l 36(a2),d4
    move.l 20(a2),d5
    bsr.w L_UNIT142_0DA06
    rts
L_UNIT142_0DA06:
    movem.l d1-d7/a0-a6,-(a7)
    lea -160(a7),a7
    movea.l a7,a2
    move.l a0,(a2)
    move.l a1,4(a2)
    move.l a1,8(a2)
    move.l d0,16(a2)
    move.l d1,20(a2)
    move.l d2,24(a2)
    move.l d3,28(a2)
    move.l d4,32(a2)
    move.l d5,36(a2)
    move.l #$00000000,76(a2)
    move.l #$00000000,d0
    move.l 16(a2),d1
    tst.l d1
    bmi.w L_UNIT142_0DCEC
    cmpi.l #$00001000,d1
    bhi.w L_UNIT142_0DCEC
    move.l 20(a2),d1
    tst.l d1
    bmi.w L_UNIT142_0DCEC
    cmpi.l #$00001000,d1
    bhi.w L_UNIT142_0DCEC
    move.l 24(a2),d1
    tst.l d1
    ble.w L_UNIT142_0DCEC
    cmpi.l #$00001000,d1
    bhi.w L_UNIT142_0DCEC
    add.l 16(a2),d1
    cmpi.l #$00001000,d1
    bhi.w L_UNIT142_0DCEC
    move.l 28(a2),d1
    tst.l d1
    ble.w L_UNIT142_0DCEC
    cmpi.l #UNIT142_BLOCK_0D99A_VALUE,d1
    bhi.w L_UNIT142_0DCEC
    move.l 32(a2),d1
    cmpi.l #$00000002,d1
    bcs.w L_UNIT142_0DCEC
    cmpi.l #$0000FFFE,d1
    bhi.w L_UNIT142_0DCEC
    move.l d1,d0
    andi.l #$00000001,d0
    bne.w L_UNIT142_0DCEC
    move.l 36(a2),d1
    cmpi.l #$FFFFFFFF,d1
    beq.w L_UNIT142_0DAFA
    tst.l d1
    bmi.w L_UNIT142_0DCEC
    move.l 28(a2),d0
    move.l #$00000001,d7
L_UNIT142_0DAE0:
    lsl.l #1,d7
    subq.l #1,d0
    bne.w L_UNIT142_0DAE0
    cmp.l d7,d1
    bcc.w L_UNIT142_0DCEC
    move.l #$00000001,52(a2)
    bra.w L_UNIT142_0DB02
L_UNIT142_0DAFA:
    move.l #$00000000,52(a2)
L_UNIT142_0DB02:
    tst.l d6
    ble.w L_UNIT142_0DCEC
    move.l a1,d0
    add.l d6,d0
    bcs.w L_UNIT142_0DCEC
    move.l d0,12(a2)
    move.l 20(a2),d0
    move.l 32(a2),d1
    mulu.w d1,d0
    move.l d0,40(a2)
    move.l 24(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    move.l d0,44(a2)
    move.l 28(a2),d0
    add.l 52(a2),d0
    lsl.l #1,d0
    move.l d0,48(a2)
    move.l #$00000000,56(a2)
L_UNIT142_0DB48:
    move.l 56(a2),d0
    cmp.l 44(a2),d0
    bge.w L_UNIT142_0DCDE
    lea 96(a2),a4
    move.l 48(a2),d5
    lsr.l #1,d5
L_UNIT142_0DB5E:
    move.w #$0000,(a4)+
    subq.l #1,d5
    bne.w L_UNIT142_0DB5E
    move.l #$00000000,60(a2)
    move.l #$00008000,d4
L_UNIT142_0DB76:
    move.l 60(a2),d5
    cmpi.l #$00000010,d5
    bge.w L_UNIT142_0DC4A
    move.l 56(a2),d0
    lsl.l #4,d0
    add.l d5,d0
    cmp.l 24(a2),d0
    bge.w L_UNIT142_0DC4A
    add.l 16(a2),d0
    move.l d0,d1
    lsr.l #3,d1
    add.l 40(a2),d1
    move.l d1,68(a2)
    andi.l #$00000007,d0
    move.l #$00000007,d3
    sub.l d0,d3
    move.l d3,64(a2)
    movea.l (a2),a0
    lea 96(a2),a4
    move.l 52(a2),d0
    tst.l d0
    beq.w L_UNIT142_0DBC8
    addq.l #2,a4
L_UNIT142_0DBC8:
    move.l 28(a2),d5
    move.l #$00000001,d7
    move.l #$00000000,d6
L_UNIT142_0DBD8:
    movea.l (a0)+,a5
    move.l a5,d0
    move.l 68(a2),d1
    add.l d1,d0
    movea.l d0,a5
    move.l #$00000000,d0
    move.b (a5),d0
    move.l 64(a2),d3
    btst d3,d0
    beq.w L_UNIT142_0DC04
    move.l #$00000000,d0
    move.w (a4),d0
    or.w d4,d0
    move.w d0,(a4)
    or.l d7,d6
L_UNIT142_0DC04:
    addq.l #2,a4
    lsl.l #1,d7
    subq.l #1,d5
    bne.w L_UNIT142_0DBD8
    move.l d6,72(a2)
    move.l 52(a2),d0
    tst.l d0
    beq.w L_UNIT142_0DC3A
    move.l 36(a2),d0
    move.l 72(a2),d6
    cmp.l d0,d6
    beq.w L_UNIT142_0DC3A
    lea 96(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    or.w d4,d0
    move.w d0,(a4)
L_UNIT142_0DC3A:
    lsr.w #1,d4
    move.l 60(a2),d0
    addq.l #1,d0
    move.l d0,60(a2)
    bra.w L_UNIT142_0DB76
L_UNIT142_0DC4A:
    movea.l 76(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_0DC98
    lea 96(a2),a5
    move.l 48(a2),d5
    lsr.l #1,d5
L_UNIT142_0DC60:
    move.w (a5)+,d0
    cmp.w (a4)+,d0
    bne.w L_UNIT142_0DC98
    subq.l #1,d5
    bne.w L_UNIT142_0DC60
    movea.l 80(a2),a4
    move.l #$00000000,d0
    move.b (a4),d0
    cmpi.l #$000000FF,d0
    beq.w L_UNIT142_0DC98
    tst.l d0
    bne.w L_UNIT142_0DC92
    move.b #$81,(a4)
    bra.w L_UNIT142_0DCD0
L_UNIT142_0DC92:
    addq.b #1,(a4)
    bra.w L_UNIT142_0DCD0
L_UNIT142_0DC98:
    move.l 12(a2),d0
    movea.l 8(a2),a4
    sub.l a4,d0
    move.l 48(a2),d5
    addq.l #1,d5
    cmp.l d5,d0
    bcs.w L_UNIT142_0DCEC
    move.l a4,80(a2)
    move.b #$00,(a4)+
    move.l a4,76(a2)
    lea 96(a2),a5
    move.l 48(a2),d5
    lsr.l #1,d5
L_UNIT142_0DCC4:
    move.w (a5)+,(a4)+
    subq.l #1,d5
    bne.w L_UNIT142_0DCC4
    move.l a4,8(a2)
L_UNIT142_0DCD0:
    move.l 56(a2),d0
    addq.l #1,d0
    move.l d0,56(a2)
    bra.w L_UNIT142_0DB48
L_UNIT142_0DCDE:
    move.l 8(a2),d0
    movea.l 4(a2),a5
    sub.l a5,d0
    bra.w L_UNIT142_0DCF2
L_UNIT142_0DCEC:
    move.l #$00000000,d0
L_UNIT142_0DCF2:
    lea 160(a7),a7
    movem.l (a7)+,d1-d7/a0-a6
    rts
L_UNIT142_0DCFC:
