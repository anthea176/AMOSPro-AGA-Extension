; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $02D90 source-verified against pinned P2d emitter.
; UNIT142+$02D90..$02DF6, 102 instructions/data bytes.
UNIT142_BLOCK_02D90_EDIT equ 0

ENTRY_UNIT142_02D90:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_02DEC
    movea.l 36(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02DEC
    move.l 24(a4),d0
    andi.l #$00002000,d0
    beq.w L_UNIT142_02DD8
    bsr.w ENTRY_UNIT142_02E64
    tst.l d0
    bne.w L_UNIT142_02DEC
    movea.l 456(a5),a2
    lea 12070(a2),a2
    move.l 4(a2),d3
    clr.l 4(a2)
    bra.w L_UNIT142_02DEE
L_UNIT142_02DD8:
    lea 12070(a2),a2
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
L_UNIT142_02DEC:
    moveq #-1,d3
L_UNIT142_02DEE:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02D90_EDIT,d2
    rts
