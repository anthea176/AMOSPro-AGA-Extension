; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $02BBA source-verified against pinned P2d emitter.
; UNIT142+$02BBA..$02C26, 108 instructions/data bytes.
UNIT142_BLOCK_02BBA_EDIT equ 0

ENTRY_UNIT142_02BBA:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_02C18
    movea.l (a2),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_02C18
    movea.l 36(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_02C18
    move.l 46(a1),d0
    move.l a4,d1
    cmp.l d1,d0
    bne.w L_UNIT142_02C18
    move.l 12(a2),d0
    tst.l d0
    beq.w L_UNIT142_02C18
    bmi.w L_UNIT142_02C18
    move.w 14(a1),d3
    ext.l d3
    move.w 4(a1),d1
    ext.l d1
    add.l d1,d3
    tst.l d3
    bmi.w L_UNIT142_02C18
    cmp.l d0,d3
    bcc.w L_UNIT142_02C18
    bra.w L_UNIT142_02C1E
L_UNIT142_02C18:
    move.l #$FFFFFFFF,d3
L_UNIT142_02C1E:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_02BBA_EDIT,d2
    rts
