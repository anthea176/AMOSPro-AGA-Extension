; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $07B56 source-verified against pinned P2d emitter.
; UNIT142+$07B56..$07BC2, 108 instructions/data bytes.
UNIT142_BLOCK_07B56_EDIT equ 0

ENTRY_UNIT142_07B56:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -192(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l (a3)+,d6
    move.l d6,8(a2)
    move.l (a3)+,d7
    move.l d7,12(a2)
    move.l (a3)+,d7
    move.l d7,16(a2)
    move.l (a3)+,d7
    move.l d7,20(a2)
    move.l (a3)+,d7
    move.l d7,24(a2)
    move.l (a3)+,d7
    move.l d7,28(a2)
    move.l #UNIT142_BLOCK_07B56_EDIT,d3
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_081D2
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_UNIT142_081D2
    move.l 28(a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_081D2
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_081D2
