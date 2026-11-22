; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $02DFA source-verified against pinned P2d emitter.
; UNIT142+$02DFA..$02E60, 102 instructions/data bytes.
UNIT142_BLOCK_02DFA_EDIT equ 0

ENTRY_UNIT142_02DFA:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_02E56
    movea.l 36(a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02E56
    move.l 24(a4),d0
    andi.l #$00002000,d0
    beq.w L_UNIT142_02E42
    bsr.w ENTRY_UNIT142_02E64
    tst.l d0
    bne.w L_UNIT142_02E56
    movea.l 456(a5),a2
    lea 12070(a2),a2
    move.l 8(a2),d3
    clr.l 8(a2)
    bra.w L_UNIT142_02E58
L_UNIT142_02E42:
    lea 12070(a2),a2
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 28(a2)
L_UNIT142_02E56:
    moveq #-1,d3
L_UNIT142_02E58:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02DFA_EDIT,d2
    rts
