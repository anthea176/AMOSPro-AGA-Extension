; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 historical R83 Close/End source-pinned; active P2d bytes unchanged.
; UNIT142+$00066..$00088 (34 MC68020 instructions).
UNIT142_R83_CLOSE_GUARD_GFX_OFFSET equ 8

L_LEGACY_CLOSE_CORE_0000C:
    move.l a4,d0                                       ; +$0000C: 200C
    tst.l d0                                           ; +$0000E: 4A80
    beq.w L_LEGACY_CLOSE_CORE_000C2                    ; +$00010: 670000B0
    movea.l UNIT142_R83_CLOSE_GUARD_GFX_OFFSET(a2),a6                                   ; +$00014: 2C6A0008
    move.l a6,d0                                       ; +$00018: 200E
    tst.l d0                                           ; +$0001A: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00024                    ; +$0001C: 67000006
    jsr -228(a6)                                       ; +$00020: 4EAEFF1C
L_LEGACY_CLOSE_CORE_00024:
    move.l 20(a4),d0                                   ; +$00024: 202C0014
    tst.l d0                                           ; +$00028: 4A80
    bra.w L_LEGACY_CLOSE_CORE_00066                    ; +$0002A: 6000003A
