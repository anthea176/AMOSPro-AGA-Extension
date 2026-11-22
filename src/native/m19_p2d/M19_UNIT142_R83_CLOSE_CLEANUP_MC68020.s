; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 historical R83 Close/End source-pinned; active P2d bytes unchanged.
; UNIT142+$000C0..$001B0 (240 MC68020 instructions).
UNIT142_R83_CLOSE_CLEANUP_CLEAR_COUNT equ 4

L_LEGACY_CLOSE_CORE_00066:
    movea.l (a2),a0                                    ; +$00066: 2052
    move.l a0,d0                                       ; +$00068: 2008
    tst.l d0                                           ; +$0006A: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00094                    ; +$0006C: 67000026
    movea.l 4(a2),a6                                   ; +$00070: 2C6A0004
    movea.l 4(a4),a1                                   ; +$00074: 226C0004
    move.l a1,d0                                       ; +$00078: 2009
    tst.l d0                                           ; +$0007A: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00084                    ; +$0007C: 67000006
    jsr -774(a6)                                       ; +$00080: 4EAEFCFA
L_LEGACY_CLOSE_CORE_00084:
    movea.l (a4),a1                                    ; +$00084: 2254
    move.l a1,d0                                       ; +$00086: 2009
    tst.l d0                                           ; +$00088: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00094                    ; +$0008A: 67000008
    movea.l (a2),a0                                    ; +$0008E: 2052
    jsr -774(a6)                                       ; +$00090: 4EAEFCFA
L_LEGACY_CLOSE_CORE_00094:
    movea.l $0004.w,a6                                 ; +$00094: 2C780004
    movea.l 16(a4),a0                                  ; +$00098: 206C0010
    move.l a0,d0                                       ; +$0009C: 2008
    tst.l d0                                           ; +$0009E: 4A80
    beq.w L_LEGACY_CLOSE_CORE_000A8                    ; +$000A0: 67000006
    jsr -672(a6)                                       ; +$000A4: 4EAEFD60
L_LEGACY_CLOSE_CORE_000A8:
    movea.l 12(a4),a0                                  ; +$000A8: 206C000C
    move.l a0,d0                                       ; +$000AC: 2008
    tst.l d0                                           ; +$000AE: 4A80
    beq.w L_LEGACY_CLOSE_CORE_000B8                    ; +$000B0: 67000006
    jsr -672(a6)                                       ; +$000B4: 4EAEFD60
L_LEGACY_CLOSE_CORE_000B8:
    movea.l a4,a1                                      ; +$000B8: 224C
    jsr -690(a6)                                       ; +$000BA: 4EAEFD4E
    clr.l 32(a2)                                       ; +$000BE: 42AA0020
L_LEGACY_CLOSE_CORE_000C2:
    tst.l (a2)                                         ; +$000C2: 4A92
    beq.w L_LEGACY_CLOSE_CORE_000D4                    ; +$000C4: 6700000E
    movea.l (a2),a0                                    ; +$000C8: 2052
    movea.l 4(a2),a6                                   ; +$000CA: 2C6A0004
    jsr -66(a6)                                        ; +$000CE: 4EAEFFBE
    clr.l (a2)                                         ; +$000D2: 4292
L_LEGACY_CLOSE_CORE_000D4:
    movea.l 8(a2),a1                                   ; +$000D4: 226A0008
    move.l a1,d0                                       ; +$000D8: 2009
    tst.l d0                                           ; +$000DA: 4A80
    beq.w L_LEGACY_CLOSE_CORE_000EC                    ; +$000DC: 6700000E
    movea.l $0004.w,a6                                 ; +$000E0: 2C780004
    jsr -414(a6)                                       ; +$000E4: 4EAEFE62
    clr.l 8(a2)                                        ; +$000E8: 42AA0008
L_LEGACY_CLOSE_CORE_000EC:
    movea.l 4(a2),a1                                   ; +$000EC: 226A0004
    move.l a1,d0                                       ; +$000F0: 2009
    tst.l d0                                           ; +$000F2: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00104                    ; +$000F4: 6700000E
    movea.l $0004.w,a6                                 ; +$000F8: 2C780004
    jsr -414(a6)                                       ; +$000FC: 4EAEFE62
    clr.l 4(a2)                                        ; +$00100: 42AA0004
L_LEGACY_CLOSE_CORE_00104:
    lea 12(a2),a0                                      ; +$00104: 41EA000C
    moveq #UNIT142_R83_CLOSE_CLEANUP_CLEAR_COUNT,d0                                        ; +$00108: 7004
L_LEGACY_CLOSE_CORE_0010A:
    clr.l (a0)+                                        ; +$0010A: 4298
    dbra d0,L_LEGACY_CLOSE_CORE_0010A                  ; +$0010C: 51C8FFFC
L_LEGACY_CLOSE_CORE_00110:
    movem.l (a7)+,d0-d7/a0-a6                          ; +$00110: 4CDF7FFF
    rts                                                ; +$00114: 4E75
L_LEGACY_CLOSE_CORE_00116:
    movea.l 36(a2),a3                                  ; +$00116: 266A0024
    move.l a3,d0                                       ; +$0011A: 200B
    tst.l d0                                           ; +$0011C: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00162                    ; +$0011E: 67000042
    movea.l 86(a3),a4                                  ; +$00122: 286B0056
    move.l a4,d0                                       ; +$00126: 200C
    tst.l d0                                           ; +$00128: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00148                    ; +$0012A: 6700001C
L_LEGACY_CLOSE_CORE_0012E:
    movea.l a4,a0                                      ; +$0012E: 204C
    movea.l $0004.w,a6                                 ; +$00130: 2C780004
    jsr -372(a6)                                       ; +$00134: 4EAEFE8C
    tst.l d0                                           ; +$00138: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00148                    ; +$0013A: 6700000C
    movea.l d0,a1                                      ; +$0013E: 2240
    jsr -378(a6)                                       ; +$00140: 4EAEFE86
    bra.w L_LEGACY_CLOSE_CORE_0012E                    ; +$00144: 6000FFE8
L_LEGACY_CLOSE_CORE_00148:
    movea.l 4(a2),a6                                   ; +$00148: 2C6A0004
    move.l a6,d0                                       ; +$0014C: 200E
    tst.l d0                                           ; +$0014E: 4A80
    beq.w L_LEGACY_CLOSE_CORE_0015A                    ; +$00150: 67000008
    movea.l a3,a0                                      ; +$00154: 204B
