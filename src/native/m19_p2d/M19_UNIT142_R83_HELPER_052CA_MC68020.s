; AGA_NATIVE_MIN_CPU: MC68020
; R83 source-verified UNIT142 $052CA..$05302, preserving helper zero state.
UNIT142_R83_HELPER_ZERO equ 0

ENTRY_LEGACY_HELPER_052CA_00000:
    move.l a6,-(a7)                                    ; +$00000: 2F0E
    move.l a0,-(a7)                                    ; +$00002: 2F08
    move.l a2,-(a7)                                    ; +$00004: 2F0A
    bsr.w L_UNIT142_052AE  ; +$00006: 6100FFDC
    tst.l d0                                           ; +$0000A: 4A80
    beq.w L_LEGACY_HELPER_052CA_0002C                  ; +$0000C: 6700001E
    lea L_UNIT142_05302(pc),a1             ; +$00010: 43FA0026
    move.l #$00000000,(a1)                             ; +$00014: 22BC00000000
    move.l #UNIT142_R83_HELPER_ZERO,4(a1)                            ; +$0001A: 237C000000000004
    movea.l d0,a1                                      ; +$00022: 2240
    movea.l 8(a2),a6                                   ; +$00024: 2C6A0008
    bsr.w L_UNIT142_056A6  ; +$00028: 610003B2
L_LEGACY_HELPER_052CA_0002C:
    movea.l (a7)+,a2                                   ; +$0002C: 245F
    movea.l (a7)+,a0                                   ; +$0002E: 205F
    movea.l (a7)+,a6                                   ; +$00030: 2C5F
    jsr -66(a6)                                        ; +$00032: 4EAEFFBE
    rts                                                ; +$00036: 4E75
