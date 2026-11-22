; AGA_NATIVE_MIN_CPU: MC68020
; Source-backed UNIT156 DOS readiness guard from pinned P2d emitter.
; UNIT156+$0099E..$009C8, 42 code bytes; GetP marker preserved.
UNIT156_DOS_ZERO equ 0

    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_UNIT156_009C4
    move.l #UNIT156_DOS_ZERO,d0
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_UNIT156_009C4
    movea.l 44(a5),a0
    bra.w L_UNIT156_0071C
L_UNIT156_009C4:
    bra.w L_UNIT156_00898
