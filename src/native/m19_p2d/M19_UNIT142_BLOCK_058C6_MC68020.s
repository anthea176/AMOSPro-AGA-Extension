; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 public entry $058C6 source-verified against pinned P2d emitter.
; UNIT142+$058C6..$05C76, 944 instructions/data bytes.
UNIT142_BLOCK_058C6_RESULT equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d7
    move.l (a3)+,d6
    move.l (a3)+,d5
    move.l (a3)+,d4
    move.l (a3)+,d2
    move.l #$00000000,d3
    lea -160(a7),a7
    cmpi.l #$00007FFF,d2
    bgt.w L_UNIT142_05C6A
    cmpi.l #$FFFF8000,d2
    blt.w L_UNIT142_05C6A
    cmpi.l #$00007FFF,d4
    bgt.w L_UNIT142_05C6A
    cmpi.l #$FFFF8000,d4
    blt.w L_UNIT142_05C6A
    cmpi.l #$00007FFF,d5
    bgt.w L_UNIT142_05C6A
    cmpi.l #$FFFF8000,d5
    blt.w L_UNIT142_05C6A
    cmpi.l #$00007FFF,d6
    bgt.w L_UNIT142_05C6A
    cmpi.l #$FFFF8000,d6
    blt.w L_UNIT142_05C6A
    tst.l d7
    bmi.w L_UNIT142_05C6A
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    move.l (a4),d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    move.l 8(a4),d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    move.l 32(a4),d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    move.l 12(a4),d0
    tst.l d0
    ble.w L_UNIT142_05C6A
    cmpi.l #$00007FFF,d0
    bgt.w L_UNIT142_05C6A
    move.l 16(a4),d0
    tst.l d0
    ble.w L_UNIT142_05C6A
    cmpi.l #$00007FFF,d0
    bgt.w L_UNIT142_05C6A
    move.l 28(a4),d0
    tst.l d0
    ble.w L_UNIT142_05C6A
    cmpi.l #$00000008,d0
    bgt.w L_UNIT142_05C6A
    move.l #$00000001,d1
L_UNIT142_0599E:
    lsl.l #1,d1
    subq.l #1,d0
    bne.w L_UNIT142_0599E
    cmp.l d1,d7
    bcc.w L_UNIT142_05C6A
    tst.l d2
    bpl.w L_UNIT142_059B8
    tst.l d5
    bmi.w L_UNIT142_05C6A
L_UNIT142_059B8:
    cmp.l 12(a4),d2
    blt.w L_UNIT142_059C8
    cmp.l 12(a4),d5
    bge.w L_UNIT142_05C6A
L_UNIT142_059C8:
    tst.l d4
    bpl.w L_UNIT142_059D4
    tst.l d6
    bmi.w L_UNIT142_05C6A
L_UNIT142_059D4:
    cmp.l 16(a4),d4
    blt.w L_UNIT142_059E4
    cmp.l 16(a4),d6
    bge.w L_UNIT142_05C6A
L_UNIT142_059E4:
    movea.l 32(a4),a2
    move.l 8(a2),d0
    tst.l d0
    beq.w L_UNIT142_05A02
    cmpi.l #$00000001,d0
    bne.w L_UNIT142_05C6A
    movea.l (a2),a0
    bra.w L_UNIT142_05A06
L_UNIT142_05A02:
    movea.l 4(a2),a0
L_UNIT142_05A06:
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    movea.l (a0),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    movea.l a0,a2
    move.l #$00000000,d1
    move.w (a0),d1
    lsl.l #3,d1
    cmp.l 12(a4),d1
    blt.w L_UNIT142_05C6A
    move.l #$00000000,d1
    move.w 2(a0),d1
    cmp.l 16(a4),d1
    blt.w L_UNIT142_05C6A
    move.l #$00000000,d1
    move.b 5(a0),d1
    cmp.l 28(a4),d1
    bne.w L_UNIT142_05C6A
    move.l d1,d0
    movea.l a0,a1
    addq.l #8,a1
L_UNIT142_05A56:
    move.l (a1)+,d1
    tst.l d1
    beq.w L_UNIT142_05C6A
    cmpi.l #$FFFFFFFF,d1
    beq.w L_UNIT142_05C6A
    subq.l #1,d0
    bne.w L_UNIT142_05A56
    move.l a2,156(a7)
    tst.l d2
    bmi.w L_UNIT142_05AB6
    cmp.l 12(a4),d2
    bge.w L_UNIT142_05AB6
    tst.l d5
    bmi.w L_UNIT142_05AB6
    cmp.l 12(a4),d5
    bge.w L_UNIT142_05AB6
    tst.l d4
    bmi.w L_UNIT142_05AB6
    cmp.l 16(a4),d4
    bge.w L_UNIT142_05AB6
    tst.l d6
    bmi.w L_UNIT142_05AB6
    cmp.l 16(a4),d6
    bge.w L_UNIT142_05AB6
    move.l #$00000001,152(a7)
    bra.w L_UNIT142_05ABE
L_UNIT142_05AB6:
    move.l #$00000000,152(a7)
L_UNIT142_05ABE:
    movea.l 32(a4),a0
    move.l 20(a0),d0
    andi.l #$00000001,d0
    beq.w L_UNIT142_05AFC
    movea.l 12(a0),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_05C6A
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_05C6A
    movea.l 32(a4),a0
    move.l 20(a0),d0
    andi.l #$FFFFFFFE,d0
    move.l d0,20(a0)
L_UNIT142_05AFC:
    movea.l a7,a2
    movea.l a2,a1
    movea.l 8(a4),a6
    jsr -198(a6)
    move.l 156(a7),4(a2)
    movea.l a2,a1
    move.l d7,d0
    jsr -342(a6)
    movea.l a2,a1
    move.l #$00000000,d0
    jsr -354(a6)
    tst.l 152(a7)
    beq.w L_UNIT142_05B6E
    cmp.l d5,d2
    bne.w L_UNIT142_05B50
    cmp.l d6,d4
    bne.w L_UNIT142_05B50
    movea.l a2,a1
    move.l d2,d0
    move.l d4,d1
    jsr -324(a6)
    tst.l d0
    bne.w L_UNIT142_05C5E
    move.l #$00000001,d3
    bra.w L_UNIT142_05C5E
L_UNIT142_05B50:
    movea.l a2,a1
    move.l d2,d0
    move.l d4,d1
    jsr -240(a6)
    movea.l a2,a1
    move.l d5,d0
    move.l d6,d1
    jsr -246(a6)
    move.l #$00000001,d3
    bra.w L_UNIT142_05C5E
L_UNIT142_05B6E:
    move.l d5,d0
    sub.l d2,d0
    move.l #$00000001,136(a7)
    tst.l d0
    bpl.w L_UNIT142_05B92
    move.l #$FFFFFFFF,136(a7)
    move.l #$00000000,d1
    sub.l d0,d1
    move.l d1,d0
L_UNIT142_05B92:
    move.l d0,128(a7)
    move.l d6,d0
    sub.l d4,d0
    move.l #$00000001,140(a7)
    tst.l d0
    bpl.w L_UNIT142_05BBA
    move.l #$FFFFFFFF,140(a7)
    move.l #$00000000,d1
    sub.l d0,d1
    move.l d1,d0
L_UNIT142_05BBA:
    move.l d0,132(a7)
    move.l 128(a7),d0
    sub.l 132(a7),d0
    move.l d0,144(a7)
L_UNIT142_05BCA:
    tst.l d2
    bmi.w L_UNIT142_05C04
    cmp.l 12(a4),d2
    bge.w L_UNIT142_05C04
    tst.l d4
    bmi.w L_UNIT142_05C04
    cmp.l 16(a4),d4
    bge.w L_UNIT142_05C04
    movea.l a2,a1
    move.l d2,d0
    move.l d4,d1
    move.l #$00000002,152(a7)
    jsr -324(a6)
    tst.l d0
    bne.w L_UNIT142_05C04
    move.l #$00000001,d3
L_UNIT142_05C04:
    cmp.l d5,d2
    bne.w L_UNIT142_05C10
    cmp.l d6,d4
    beq.w L_UNIT142_05C5E
L_UNIT142_05C10:
    move.l 144(a7),d0
    lsl.l #1,d0
    move.l d0,148(a7)
    move.l #$00000000,d1
    sub.l 132(a7),d1
    cmp.l d1,d0
    ble.w L_UNIT142_05C3C
    move.l 144(a7),d0
    sub.l 132(a7),d0
    move.l d0,144(a7)
    move.l 136(a7),d0
    add.l d0,d2
L_UNIT142_05C3C:
    move.l 148(a7),d0
    cmp.l 128(a7),d0
    bge.w L_UNIT142_05C5A
    move.l 144(a7),d0
    add.l 128(a7),d0
    move.l d0,144(a7)
    move.l 140(a7),d0
    add.l d0,d4
L_UNIT142_05C5A:
    bra.w L_UNIT142_05BCA
L_UNIT142_05C5E:
    tst.l 152(a7)
    beq.w L_UNIT142_05C6A
    jsr -228(a6)
L_UNIT142_05C6A:
    lea 160(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_058C6_RESULT,d2
    rts
