; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 historical R83 Close/End source-pinned; active P2d bytes unchanged.
; UNIT142+$001B4..$001C2 (14 MC68020 instructions).
UNIT142_R83_CLOSE_POSTCALL_ROOT_OFFSET equ 32

L_LEGACY_CLOSE_CORE_0015A:
    move.l #$00000000,36(a2)                           ; +$0015A: 257C000000000024
L_LEGACY_CLOSE_CORE_00162:
    movea.l UNIT142_R83_CLOSE_POSTCALL_ROOT_OFFSET(a2),a4                                  ; +$00162: 286A0020
    rts                                                ; +$00166: 4E75
