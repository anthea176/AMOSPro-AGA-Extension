; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 public entry $02E64 source-verified against pinned P2d emitter.
; UNIT142+$02E64..$030E8, 644 instructions/data bytes.
UNIT142_ENTRY_02E64_COUNT equ 63

    movem.l d1-d7/a0-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_03076
    movea.l (a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_03076
    movea.l 36(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_03076
    move.l 46(a3),d0
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_UNIT142_03076
    movea.l 86(a3),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_03076
    lea 12070(a2),a2
    move.l (a2),d0
    move.l a3,d1
    cmp.l d1,d0
    beq.w L_UNIT142_02ED8
    move.l a3,(a2)
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
    move.l 24(a3),d0
    andi.l #$00002000,d0
    beq.w L_UNIT142_02ED8
    move.l #$00000001,28(a2)
L_UNIT142_02ED8:
    move.l 24(a3),d0
    andi.l #$00002000,d0
    bne.w L_UNIT142_02EF6
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
L_UNIT142_02EF6:
    moveq #UNIT142_ENTRY_02E64_COUNT,d7
L_UNIT142_02EF8:
    move.l 24(a2),d0
    cmpi.l #$00000010,d0
    bcc.w L_UNIT142_03070
    movea.l a4,a0
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_03070
    movea.l d0,a3
    move.l 20(a3),d4
    moveq #0,d5
    move.w 24(a3),d5
    moveq #0,d6
    move.w 26(a3),d6
    cmpi.l #$00000400,d4
    beq.w L_UNIT142_02F54
    cmpi.l #$00000008,d4
    beq.w L_UNIT142_02F94
    cmpi.l #$00080000,d4
    beq.w L_UNIT142_03026
    cmpi.l #$00040000,d4
    beq.w L_UNIT142_0303A
    bra.w L_UNIT142_03062
L_UNIT142_02F54:
    move.l d5,d0
    andi.l #$00000080,d0
    bne.w L_UNIT142_03062
    move.l d5,d0
    swap d0
    move.w d6,d0
    move.l d0,d4
    move.l 20(a2),d1
    add.l d1,d1
    add.l d1,d1
    lea 80(a2),a0
    move.l a0,d0
    add.l d1,d0
    movea.l d0,a0
    move.l d4,(a0)
    move.l 20(a2),d0
    addq.l #1,d0
    andi.l #$0000000F,d0
    move.l d0,20(a2)
    addq.l #1,24(a2)
    bra.w L_UNIT142_03062
L_UNIT142_02F94:
    move.l 28(a2),d0
    tst.l d0
    beq.w L_UNIT142_03062
    move.l d5,d0
    andi.l #$0000007F,d0
    cmpi.l #$00000068,d0
    beq.w L_UNIT142_02FC8
    cmpi.l #$00000069,d0
    beq.w L_UNIT142_02FCE
    cmpi.l #$0000006A,d0
    beq.w L_UNIT142_02FD4
    bra.w L_UNIT142_03062
L_UNIT142_02FC8:
    moveq #1,d1
    bra.w L_UNIT142_02FD6
L_UNIT142_02FCE:
    moveq #2,d1
    bra.w L_UNIT142_02FD6
L_UNIT142_02FD4:
    moveq #4,d1
L_UNIT142_02FD6:
    move.l d5,d0
    andi.l #$00000080,d0
    bne.w L_UNIT142_03004
    move.l 12(a2),d0
    move.l d0,d4
    and.l d1,d4
    tst.l d4
    bne.w L_UNIT142_03062
    or.l d1,d0
    move.l d0,12(a2)
    move.l 4(a2),d0
    or.l d1,d0
    move.l d0,4(a2)
    bra.w L_UNIT142_03062
L_UNIT142_03004:
    move.l 12(a2),d0
    move.l d0,d4
    and.l d1,d4
    tst.l d4
    beq.w L_UNIT142_03062
    sub.l d1,d0
    move.l d0,12(a2)
    move.l 8(a2),d0
    or.l d1,d0
    move.l d0,8(a2)
    bra.w L_UNIT142_03062
L_UNIT142_03026:
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
    bra.w L_UNIT142_03062
L_UNIT142_0303A:
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
    movea.l (a2),a0
    move.l 24(a0),d0
    andi.l #$00002000,d0
    beq.w L_UNIT142_03062
    move.l #$00000001,28(a2)
L_UNIT142_03062:
    movea.l a3,a1
    movea.l $0004.w,a6
    jsr -378(a6)
    dbra d7,L_UNIT142_02EF8
L_UNIT142_03070:
    moveq #0,d0
    bra.w L_UNIT142_03078
L_UNIT142_03076:
    moveq #-1,d0
L_UNIT142_03078:
    movem.l (a7)+,d1-d7/a0-a6
    rts
L_UNIT142_0307E:
    bsr.w ENTRY_UNIT142_02E64
    tst.l d0
    bne.w L_UNIT142_030E4
    movem.l d1-d7/a0-a6,-(a7)
    movea.l 456(a5),a2
    lea 12070(a2),a2
    move.l 24(a2),d0
    tst.l d0
    beq.w L_UNIT142_030DC
    move.l 16(a2),d1
    add.l d1,d1
    add.l d1,d1
    lea 80(a2),a0
    move.l a0,d0
    add.l d1,d0
    movea.l d0,a0
    move.l (a0),d4
    lea 32(a2),a0
    move.l #$00000400,20(a0)
    move.l d4,24(a0)
    move.l 16(a2),d1
    addq.l #1,d1
    andi.l #$0000000F,d1
    move.l d1,16(a2)
    subq.l #1,24(a2)
    move.l a0,d0
    bra.w L_UNIT142_030DE
L_UNIT142_030DC:
    moveq #0,d0
L_UNIT142_030DE:
    movem.l (a7)+,d1-d7/a0-a6
    rts
L_UNIT142_030E4:
    moveq #0,d0
    rts
