; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $00C9E source-verified against pinned P2d emitter.
; UNIT142+$00C9E..$00D38, 154 instructions/data bytes.
UNIT142_BLOCK_00C9E_EDIT equ 128

ENTRY_UNIT142_00C9E:
    movem.l d0-d7/a0-a6,-(a7)
    move.l d3,d7
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_00D32
    tst.l (a2)
    beq.w L_UNIT142_00D32
    movea.l 32(a2),a3
    move.l a3,d0
    tst.l d0
    beq.w L_UNIT142_00D32
    move.l 8(a3),d0
    tst.l d0
    beq.w L_UNIT142_00CD2
    movea.l (a3),a1
    bra.w L_UNIT142_00CD6
L_UNIT142_00CD2:
    movea.l 4(a3),a1
L_UNIT142_00CD6:
    move.l a1,d0
    tst.l d0
    beq.w L_UNIT142_00D32
    movea.l (a1),a4
    move.l a4,d0
    tst.l d0
    beq.w L_UNIT142_00D32
    move.l #UNIT142_BLOCK_00C9E_EDIT,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_UNIT142_00D32
    movea.l d0,a3
    movea.l a3,a1
    movea.l 8(a2),a6
    jsr -198(a6)
    move.l a4,4(a3)
    move.l d7,d0
    andi.l #$000000FF,d0
    movea.l a3,a1
    movea.l 8(a2),a6
    jsr -234(a6)
    jsr -228(a6)
    movea.l a3,a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_UNIT142_00D32:
    movem.l (a7)+,d0-d7/a0-a6
    rts
