; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 IFF AP20 pre-call controls source-verified against pinned P2d emitter.
; UNIT142+$01BDE..$01E0C, 558 instructions/data bytes.
UNIT142_IFF_FAILURE equ -1

    cmpi.l #$00000100,d7
    beq.w L_UNIT142_01C12
    lea -20(a7),a7
    move.l d0,d6
    ori.l #$00010000,d6
    movea.l a7,a1
    move.l d6,(a1)
    move.l d1,4(a1)
    move.l d2,8(a1)
    move.l d3,12(a1)
    clr.l 16(a1)
    jsr -882(a6)
    lea 20(a7),a7
    rts
L_UNIT142_01C12:
    jsr -852(a6)
    rts
ENTRY_UNIT142_01C18:
    movem.l d0-d1/d4-d7/a0-a4/a6,-(a7)
    moveq #UNIT142_IFF_FAILURE,d3
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_01DF2
    movea.l 36(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_01DF2
    movea.l 86(a3),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_01DF2
L_UNIT142_01C42:
    movea.l a4,a0
    movea.l $0004.w,a6
    bsr.w L_UNIT142_0307E
    tst.l d0
    beq.w L_UNIT142_01DF2
    movea.l d0,a3
    move.l 20(a3),d4
    moveq #0,d5
    move.w 24(a3),d5
    moveq #0,d6
    move.w 26(a3),d6
    movea.l a3,a1
    nop
    nop
    cmpi.l #$00000400,d4
    bne.w L_UNIT142_01C42
    move.l d5,d0
    andi.l #$00000080,d0
    bne.w L_UNIT142_01C42
    cmpi.l #$00000033,d5
    bne.w L_UNIT142_01DEC
    move.l d6,d0
    andi.l #$00000008,d0
    beq.w L_UNIT142_01DEC
    bra.w L_UNIT142_01E14
L_UNIT142_01C9A:
    ori.w #$8100,-168(a5)
    bra.w L_UNIT142_01DFA
L_UNIT142_01CA4:
    movea.l 36(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_01CF0
    movea.l 86(a3),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_01CD6
L_UNIT142_01CBC:
    movea.l a4,a0
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_01CD6
    movea.l d0,a1
    jsr -378(a6)
    bra.w L_UNIT142_01CBC
L_UNIT142_01CD6:
    movea.l 4(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_01CE8
    movea.l a3,a0
    bsr.w L_UNIT142_0660A
L_UNIT142_01CE8:
    move.l #$00000000,36(a2)
L_UNIT142_01CF0:
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_01D70
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_01D0C
    jsr -228(a6)
L_UNIT142_01D0C:
    movea.l (a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01D3A
    movea.l 4(a2),a6
    movea.l 4(a4),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01D2A
    jsr -774(a6)
L_UNIT142_01D2A:
    movea.l (a4),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01D3A
    movea.l (a2),a0
    jsr -774(a6)
L_UNIT142_01D3A:
    movea.l $0004.w,a6
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01D4E
    jsr -672(a6)
L_UNIT142_01D4E:
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01D5E
    jsr -672(a6)
L_UNIT142_01D5E:
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -690(a6)
    move.l #$00000000,32(a2)
L_UNIT142_01D70:
    movea.l (a2),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_01D88
    movea.l 4(a2),a6
    jsr -66(a6)
    move.l #$00000000,(a2)
L_UNIT142_01D88:
    movea.l 8(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01DA4
    movea.l $0004.w,a6
    jsr -414(a6)
    move.l #$00000000,8(a2)
L_UNIT142_01DA4:
    movea.l 4(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_01DC0
    movea.l $0004.w,a6
    jsr -414(a6)
    move.l #$00000000,4(a2)
L_UNIT142_01DC0:
    moveq #0,d0
    move.l d0,(a2)
    move.l d0,4(a2)
    move.l d0,8(a2)
    move.l d0,12(a2)
    move.l d0,16(a2)
    move.l d0,20(a2)
    move.l d0,24(a2)
    move.l d0,28(a2)
    move.l d0,32(a2)
    move.l d0,36(a2)
    bra.w L_UNIT142_01C9A
L_UNIT142_01DEC:
    move.l d5,d3
    bra.w L_UNIT142_01DF2
L_UNIT142_01DF2:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6
    moveq #0,d2
    rts
L_UNIT142_01DFA:
    moveq #1,d1
    movea.l -8(a5),a0
    jsr 288(a0)
    move.l d5,d3
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6
    moveq #0,d2
