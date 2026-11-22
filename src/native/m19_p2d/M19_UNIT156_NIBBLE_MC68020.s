; AGA_NATIVE_MIN_CPU: MC68020
; Source-backed native UNIT156 nibble expansion from pinned P2d emitter.
; UNIT156+$00932..$0095E, 44 code bytes. Neighboring data unchanged.
; Read-only audit verified byte by byte before MC68020 direct assembly.
UNIT156_NIBBLE_ZERO equ 0

    lea L_UNIT156_0095E(pc),a6
L_UNIT156_00936:
    moveq #UNIT156_NIBBLE_ZERO,d0
    move.b (a3)+,d0
    move.l d0,d1
    lsr.l #4,d0
    move.l 0(a6,d0.l*4),d0
    lsl.l d6,d0
    or.l d0,(a4)+
    move.l d1,d0
    andi.l #$0000000F,d0
    move.l 0(a6,d0.l*4),d0
    lsl.l d6,d0
    or.l d0,(a4)+
    dbra d2,L_UNIT156_00936
    bra.w L_UNIT156_00850
