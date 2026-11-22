; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0C2C6 source-verified against pinned P2d emitter.
; UNIT142+$0C2C6..$0C308, 66 instructions/data bytes.
UNIT142_BLOCK_0C2C6_EDIT equ 5

ENTRY_UNIT142_0C2C6:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,d7
    move.l a3,4(a2)
    move.l d7,d0
    cmpi.l #UNIT142_BLOCK_0C2C6_EDIT,d0
    bcs.w L_UNIT142_0C32A
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0C32A
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0C32A
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_UNIT142_0C32A
    move.l d7,d0
