; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$0411A..$04252, 312 instruction bytes.
UNIT142_BLOCK_0411A_EDIT equ 0

ENTRY_UNIT142_0411A:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d5
    move.l (a3)+,d4
    move.l #$00000000,d3
    tst.l d5
    beq.w L_UNIT142_0424A
    cmpi.l #$00000100,d5
    bhi.w L_UNIT142_0424A
    move.l d4,d0
    cmpi.l #$00000018,d0
    bls.w L_UNIT142_0424A
    andi.l #$00000001,d0
    bne.w L_UNIT142_0424A
    move.l d5,d6
    mulu.w #$0308,d6
    addi.l #$00000010,d6
    move.l d4,d0
    subi.l #$00000018,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_0424A
    move.l d4,d0
    add.l d6,d0
    bcs.w L_UNIT142_0424A
    subq.l #1,d0
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w L_UNIT142_0424A
    movea.l d4,a0
    move.l -20(a0),d0
    move.l d6,d7
    addi.l #$00000010,d7
    cmp.l d7,d0
    bne.w L_UNIT142_0424A
    move.l #$00000000,d0
    move.w -12(a0),d0
    andi.w #$FFFD,d0
    cmpi.l #$00000001,d0
    bne.w L_UNIT142_0424A
    move.l -16(a0),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_0424A
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0424A
    move.l #$41474150,-8(a0)
    move.l #$414C2020,-4(a0)
    move.l #$41474150,(a0)
    move.w #$414C,4(a0)
    move.w #$0001,6(a0)
    move.w d5,8(a0)
    move.w #$0000,10(a0)
    move.l #$00000000,12(a0)
    move.l d5,d7
    lsl.l #3,d7
    addi.l #$00000010,d7
    move.l d4,d0
    addi.l #$00000010,d0
    movea.l d0,a1
L_UNIT142_04214:
    move.l d7,(a1)+
    move.w #$0000,(a1)+
    move.w #$0000,(a1)+
    addi.l #$00000300,d7
    subq.l #1,d5
    bne.w L_UNIT142_04214
    move.l #$00000000,d5
    move.w 8(a0),d5
    mulu.w #$00C0,d5
L_UNIT142_04238:
    move.l #$00000000,(a1)+
    subq.l #1,d5
    bne.w L_UNIT142_04238
    move.l #$00000001,d3
L_UNIT142_0424A:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0411A_EDIT,d2
    rts
