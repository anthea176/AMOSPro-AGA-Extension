; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $031E4 source-verified against pinned P2d emitter.
; UNIT142+$031E4..$0326C, 136 instructions/data bytes.
UNIT142_BLOCK_031E4_EDIT equ 0

ENTRY_UNIT142_031E4:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d7
    move.l (a3)+,d6
    move.l (a3)+,d5
    move.l (a3)+,d4
    move.l (a3)+,d3
    move.l (a3)+,d2
    move.l (a3)+,d1
    move.l (a3)+,d0
    tst.l d2
    ble.w L_UNIT142_0325E
    tst.l d3
    ble.w L_UNIT142_0325E
    tst.l d6
    ble.w L_UNIT142_0325E
    tst.l d7
    ble.w L_UNIT142_0325E
    cmp.l d4,d0
    blt.w L_UNIT142_03226
    sub.l d4,d0
    bvs.w L_UNIT142_0325E
    cmp.l d6,d0
    bge.w L_UNIT142_0325E
    bra.w L_UNIT142_03232
L_UNIT142_03226:
    sub.l d0,d4
    bvs.w L_UNIT142_0325E
    cmp.l d2,d4
    bge.w L_UNIT142_0325E
L_UNIT142_03232:
    cmp.l d5,d1
    blt.w L_UNIT142_03248
    sub.l d5,d1
    bvs.w L_UNIT142_0325E
    cmp.l d7,d1
    bge.w L_UNIT142_0325E
    bra.w L_UNIT142_03254
L_UNIT142_03248:
    sub.l d1,d5
    bvs.w L_UNIT142_0325E
    cmp.l d3,d5
    bge.w L_UNIT142_0325E
L_UNIT142_03254:
    move.l #$00000001,d3
    bra.w L_UNIT142_03264
L_UNIT142_0325E:
    move.l #$00000000,d3
L_UNIT142_03264:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_031E4_EDIT,d2
    rts
