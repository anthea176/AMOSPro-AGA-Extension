; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0317C source-verified against pinned P2d emitter.
; UNIT142+$0317C..$031E0, 100 instructions/data bytes.
UNIT142_BLOCK_0317C_EDIT equ 0

ENTRY_UNIT142_0317C:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l d3,d5
    move.l (a3)+,d4
    move.l (a3)+,d3
    move.l (a3)+,d2
    move.l (a3)+,d1
    move.l (a3)+,d0
    tst.l d0
    bmi.w L_UNIT142_031D2
    tst.l d1
    bmi.w L_UNIT142_031D2
    tst.l d4
    ble.w L_UNIT142_031D2
    tst.l d5
    ble.w L_UNIT142_031D2
    cmp.l d2,d0
    blt.w L_UNIT142_031D2
    sub.l d2,d0
    bvs.w L_UNIT142_031D2
    cmp.l d4,d0
    bge.w L_UNIT142_031D2
    cmp.l d3,d1
    blt.w L_UNIT142_031D2
    sub.l d3,d1
    bvs.w L_UNIT142_031D2
    cmp.l d5,d1
    bge.w L_UNIT142_031D2
    move.l #$00000001,d3
    bra.w L_UNIT142_031D8
L_UNIT142_031D2:
    move.l #$00000000,d3
L_UNIT142_031D8:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0317C_EDIT,d2
    rts
