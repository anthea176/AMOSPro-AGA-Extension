; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 clean source-backed region against pinned P2d emitter.
; UNIT142+$02C9A..$02D7E, 228 instruction bytes.
UNIT142_BLOCK_02C9A_EDIT equ 0

ENTRY_UNIT142_02C9A:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_02D70
    movea.l (a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_02D70
    movea.l 36(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02D70
    move.l 46(a4),d0
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_UNIT142_02D70
    lea -48(a7),a7
    movea.l a7,a4
    movea.l a4,a0
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    clr.l (a0)+
    movea.l $0004.w,a6
    lea L_UNIT142_02D7E(pc),a0
    move.l #$00000000,d0
    movea.l a4,a1
    move.l #$00000000,d1
    jsr -444(a6)
    tst.l d0
    bne.w L_UNIT142_02D62
    movea.l 20(a4),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_02D4E
    jsr -42(a6)
    andi.w #$7000,d0
    move.l #$00000000,d3
    move.l d0,d1
    andi.w #$4000,d1
    beq.w L_UNIT142_02D32
    addq.l #1,d3
L_UNIT142_02D32:
    move.l d0,d1
    andi.w #$2000,d1
    beq.w L_UNIT142_02D3E
    addq.l #2,d3
L_UNIT142_02D3E:
    move.l d0,d1
    andi.w #$1000,d1
    beq.w L_UNIT142_02D4A
    addq.l #4,d3
L_UNIT142_02D4A:
    bra.w L_UNIT142_02D54
L_UNIT142_02D4E:
    move.l #$FFFFFFFF,d3
L_UNIT142_02D54:
    movea.l $0004.w,a6
    movea.l a4,a1
    jsr -450(a6)
    bra.w L_UNIT142_02D68
L_UNIT142_02D62:
    move.l #$FFFFFFFF,d3
L_UNIT142_02D68:
    lea 48(a7),a7
    bra.w L_UNIT142_02D76
L_UNIT142_02D70:
    move.l #$FFFFFFFF,d3
L_UNIT142_02D76:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02C9A_EDIT,d2
    rts
L_UNIT142_02D7E:
