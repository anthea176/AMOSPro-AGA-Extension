; AGA_NATIVE_MIN_CPU: MC68020
; UNIT153 P2d source-backed walk/copy completion $00EDA..$00F04.
; CPU MC68020, 42 exact instruction bytes; no AMOS linker bytes.
UNIT153_WALK_COPY_RESULT equ 1

L_UNIT153_00EDA:
    subq.l #1,d6
L_UNIT153_00EDC:
    move.b (a0)+,(a1)+
    dbra d6,L_UNIT153_00EDC
    move.l 76(a2),d0
    move.l a0,d5
    add.l d0,d5
    movea.l d5,a0
    move.l 80(a2),d0
    move.l a1,d5
    add.l d0,d5
    movea.l d5,a1
    dbra d7,L_UNIT153_00ED6
    move.l #UNIT153_WALK_COPY_RESULT,d3
    bra.w L_UNIT153_00F0A
