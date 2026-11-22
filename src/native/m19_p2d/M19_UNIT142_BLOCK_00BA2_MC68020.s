; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $00BA2 source-verified against pinned P2d emitter.
; UNIT142+$00BA2..$00C9A, 248 instructions/data bytes.
UNIT142_BLOCK_00BA2_EDIT equ 0

ENTRY_UNIT142_00BA2:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)
    moveq #UNIT142_BLOCK_00BA2_EDIT,d3
    movea.l 456(a5),a2
    tst.l (a2)
    beq.w L_UNIT142_00C34
    movea.l 32(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_00C34
    move.l 12(a4),d0
    tst.l d0
    beq.w L_UNIT142_00C34
    move.l 16(a4),d0
    tst.l d0
    beq.w L_UNIT142_00C34
    bsr.w L_UNIT142_00C3C
    tst.l d0
    bne.w L_UNIT142_00C34
    move.l 8(a4),d0
    tst.l d0
    beq.w L_UNIT142_00BEC
    moveq #0,d7
    bra.w L_UNIT142_00BEE
L_UNIT142_00BEC:
    moveq #1,d7
L_UNIT142_00BEE:
    movea.l 8(a2),a6
    move.l a6,d0
    tst.l d0
    beq.w L_UNIT142_00C34
    jsr -228(a6)
    tst.l d7
    beq.w L_UNIT142_00C0C
    movea.l 4(a4),a1
    bra.w L_UNIT142_00C0E
L_UNIT142_00C0C:
    movea.l (a4),a1
L_UNIT142_00C0E:
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_00C34
    movea.l (a2),a0
    movea.l 4(a2),a6
    jsr -780(a6)
    tst.l d0
    beq.w L_UNIT142_00C34
    move.l d7,8(a4)
    move.l #$00000003,20(a4)
    moveq #1,d3
L_UNIT142_00C34:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6
    moveq #0,d2
    rts
L_UNIT142_00C3C:
    move.l 20(a4),d6
    andi.l #$00000003,d6
    btst #0,d6
    beq.w L_UNIT142_00C6C
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00C6C
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_00C6C
    bclr #0,d6
L_UNIT142_00C6C:
    btst #1,d6
    beq.w L_UNIT142_00C92
    movea.l 16(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_00C92
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_UNIT142_00C92
    bclr #1,d6
L_UNIT142_00C92:
    move.l d6,20(a4)
    move.l d6,d0
    rts
