; AGA_NATIVE_MIN_CPU: MC68020
; UNIT153 P2d source-backed third-pixel loop $014F8..$0151A.
; CPU MC68020, 34 exact instruction bytes; no AMOS linker bytes.
UNIT153_THIRD_PIXEL_ADVANCE equ 1

L_UNIT153_014F8:
    move.l 100(a2),d0
    move.l a0,d1
    add.l d0,d1
    movea.l d1,a0
    move.l 104(a2),d0
    add.l d0,d4
    move.l 4(a2),d0
    cmp.l d0,d4
    bcs.w L_UNIT153_01516
    sub.l d0,d4
    addq.l #UNIT153_THIRD_PIXEL_ADVANCE,a0
L_UNIT153_01516:
    dbra d6,L_UNIT153_014F4
