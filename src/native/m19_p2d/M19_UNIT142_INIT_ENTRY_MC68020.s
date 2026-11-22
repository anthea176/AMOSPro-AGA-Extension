; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 AGA init/entry source-verified against pinned P2d emitter.
; UNIT142+$00022..$0005A, 56 instructions/data bytes.
UNIT142_INIT_COUNT equ 9

    cmp.l #$41506578,d1
    bne.w L_UNIT142_00054
    lea L_UNIT142_001C2(pc),a0
    move.l a0,456(a5)
    lea L_UNIT142_0005A(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
    lea L_UNIT142_001C2(pc),a0
    moveq #UNIT142_INIT_COUNT,d0
L_UNIT142_00046:
    clr.l (a0)+
    dbra d0,L_UNIT142_00046
    moveq #13,d0
    move.w #$0200,d1
    rts
L_UNIT142_00054:
    moveq #-1,d0
    suba.l a0,a0
    rts
