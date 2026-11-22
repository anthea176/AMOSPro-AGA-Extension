; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $03B52 source-verified against pinned P2d emitter.
; UNIT142+$03B52..$03C42, 240 instructions/data bytes.
UNIT142_BLOCK_03B52_EDIT equ 0

ENTRY_UNIT142_03B52:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d4
    move.l #$FFFFFFFF,d3
    cmpi.l #$000000FF,d4
    bhi.w L_UNIT142_03C3A
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_03C3A
    move.l (a2),d0
    tst.l d0
    beq.w L_UNIT142_03C3A
    move.l 8(a2),d0
    tst.l d0
    beq.w L_UNIT142_03C3A
    move.l 28(a2),d0
    tst.l d0
    ble.w L_UNIT142_03C3A
    cmpi.l #$00000008,d0
    bgt.w L_UNIT142_03C3A
    move.l 24(a2),d0
    andi.l #$00000C80,d0
    bne.w L_UNIT142_03C3A
    movea.l (a2),a0
    movea.l 48(a0),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_03C3A
    move.l #$00000000,d0
    move.w 2(a1),d0
    tst.l d0
    beq.w L_UNIT142_03C3A
    cmpi.l #$00000100,d0
    bhi.w L_UNIT142_03C3A
    tst.l d4
    bmi.w L_UNIT142_03C3A
    cmp.l d0,d4
    bcc.w L_UNIT142_03C3A
    cmp.l 20(a2),d4
    bcc.w L_UNIT142_03C3A
    movea.l 8(a2),a6
    move.l a0,d0
    addi.l #$0000002C,d0
    movea.l d0,a0
    lea -12(a7),a7
    move.l d4,d0
    move.l #$00000001,d1
    movea.l a7,a1
    movea.l 4(a0),a0
    jsr -900(a6)
    move.l (a7),d5
    move.l 4(a7),d6
    move.l 8(a7),d7
    andi.l #$FF000000,d5
    andi.l #$FF000000,d6
    andi.l #$FF000000,d7
    lsr.l #8,d5
    lsr.l #8,d6
    lsr.l #8,d6
    lsr.l #8,d7
    lsr.l #8,d7
    lsr.l #8,d7
    or.l d6,d5
    or.l d7,d5
    move.l d5,d3
    lea 12(a7),a7
L_UNIT142_03C3A:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_03B52_EDIT,d2
    rts
