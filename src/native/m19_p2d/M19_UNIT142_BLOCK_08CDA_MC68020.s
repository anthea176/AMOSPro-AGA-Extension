; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $08CDA source-verified against pinned P2d emitter.
; UNIT142+$08CDA..$08D72, 152 instructions/data bytes.
UNIT142_BLOCK_08CDA_EDIT equ 0

ENTRY_UNIT142_08CDA:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l (a3)+,d7
    move.l d7,8(a2)
    move.l (a3)+,d7
    move.l d7,12(a2)
    move.l (a3)+,d7
    move.l d7,16(a2)
    move.l #UNIT142_BLOCK_08CDA_EDIT,d3
    move.l (a2),d0
    tst.l d0
    bmi.w L_UNIT142_09114
    cmpi.l #$00000001,d0
    bgt.w L_UNIT142_09114
    move.l 8(a2),d0
    cmpi.l #$FFFF8000,d0
    blt.w L_UNIT142_09114
    cmpi.l #$00007FFF,d0
    bgt.w L_UNIT142_09114
    move.l 4(a2),d0
    cmpi.l #$FFFF8000,d0
    blt.w L_UNIT142_09114
    cmpi.l #$00007FFF,d0
    bgt.w L_UNIT142_09114
    move.l 12(a2),d0
    tst.l d0
    ble.w L_UNIT142_09114
    cmpi.l #$00001000,d0
    bgt.w L_UNIT142_09114
    move.l 16(a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_09114
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_09114
