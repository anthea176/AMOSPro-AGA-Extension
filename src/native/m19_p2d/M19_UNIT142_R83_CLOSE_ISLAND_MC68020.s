; AGA_NATIVE_MIN_CPU: MC68020
; R83 historical Close 56-byte instruction island, entry not proven reachable.
; Two BEQ.W targets source-owned cleanup at UNIT142+$000C0.
UNIT142_R83_ISLAND_CLEAR_OFFSET equ 20

ENTRY_LEGACY_CLOSE_ISLAND_00000:
    movea.l 12(a4),a0                                  ; +$00000: 206C000C
    movea.l $0004.w,a6                                 ; +$00004: 2C780004
    nop                                                ; +$00008: 4E71
    nop                                                ; +$0000A: 4E71
    movea.l 12(a4),a0                                  ; +$0000C: 206C000C
    jsr -372(a6)                                       ; +$00010: 4EAEFE8C
    tst.l d0                                           ; +$00014: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00066  ; +$00016: 67000020
    movea.l 16(a4),a0                                  ; +$0001A: 206C0010
    movea.l $0004.w,a6                                 ; +$0001E: 2C780004
    nop                                                ; +$00022: 4E71
    nop                                                ; +$00024: 4E71
    movea.l 16(a4),a0                                  ; +$00026: 206C0010
    jsr -372(a6)                                       ; +$0002A: 4EAEFE8C
    tst.l d0                                           ; +$0002E: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00066  ; +$00030: 67000006
    clr.l UNIT142_R83_ISLAND_CLEAR_OFFSET(a4)                                       ; +$00034: 42AC0014
