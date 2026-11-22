; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0C3C2 source-verified against pinned P2d emitter.
; UNIT142+$0C3C2..$0C416, 84 instructions/data bytes.
UNIT142_BLOCK_0C3C2_EDIT equ 0

ENTRY_UNIT142_0C3C2:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l d3,8(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l a3,12(a2)
    move.l #UNIT142_BLOCK_0C3C2_EDIT,d3
    move.l 4(a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_0C8BE
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0C8BE
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0C8BE
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_UNIT142_0C8BE
    move.l 4(a2),d0
