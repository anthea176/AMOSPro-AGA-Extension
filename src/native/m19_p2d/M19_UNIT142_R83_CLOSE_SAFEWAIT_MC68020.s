; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 historical R83 Close/End source-pinned; active P2d bytes unchanged.
; UNIT142+$001EA..$0029E (180 MC68020 instructions).
UNIT142_R83_CLOSE_SAFEWAIT_READY equ 1

ENTRY_LEGACY_CLOSE_CORE_00190:
    bsr.w L_LEGACY_CLOSE_CORE_001A6                    ; +$00190: 61000014
    tst.l d0                                           ; +$00194: 4A80
    beq.w L_LEGACY_CLOSE_CORE_001A2                    ; +$00196: 6700000A
    bsr.w L_LEGACY_CLOSE_CORE_00116                    ; +$0019A: 6100FF7A
    bra.w L_LEGACY_CLOSE_CORE_0000C                    ; +$0019E: 6000FE6C
L_LEGACY_CLOSE_CORE_001A2:
    bra.w L_LEGACY_CLOSE_CORE_00110                    ; +$001A2: 6000FF6C
L_LEGACY_CLOSE_CORE_001A6:
    movea.l 32(a2),a4                                  ; +$001A6: 286A0020
    move.l a4,d0                                       ; +$001AA: 200C
    tst.l d0                                           ; +$001AC: 4A80
    beq.w L_LEGACY_CLOSE_CORE_001DE                    ; +$001AE: 6700002E
    moveq #0,d4                                        ; +$001B2: 7800
L_LEGACY_CLOSE_CORE_001B4:
    bsr.w L_LEGACY_CLOSE_CORE_001E6                    ; +$001B4: 61000030
    tst.l d0                                           ; +$001B8: 4A80
    beq.w L_LEGACY_CLOSE_CORE_001DE                    ; +$001BA: 67000022
    addq.l #1,d4                                       ; +$001BE: 5284
    cmpi.l #$0000012D,d4                               ; +$001C0: 0C840000012D
    bge.w L_LEGACY_CLOSE_CORE_001E2                    ; +$001C6: 6C00001A
    movea.l 8(a2),a6                                   ; +$001CA: 2C6A0008
    move.l a6,d0                                       ; +$001CE: 200E
    tst.l d0                                           ; +$001D0: 4A80
    beq.w L_LEGACY_CLOSE_CORE_001E2                    ; +$001D2: 6700000E
    jsr -270(a6)                                       ; +$001D6: 4EAEFEF2
    bra.w L_LEGACY_CLOSE_CORE_001B4                    ; +$001DA: 6000FFD8
L_LEGACY_CLOSE_CORE_001DE:
    moveq #UNIT142_R83_CLOSE_SAFEWAIT_READY,d0                                        ; +$001DE: 7001
    rts                                                ; +$001E0: 4E75
L_LEGACY_CLOSE_CORE_001E2:
    moveq #0,d0                                        ; +$001E2: 7000
    rts                                                ; +$001E4: 4E75
L_LEGACY_CLOSE_CORE_001E6:
    move.l 20(a4),d6                                   ; +$001E6: 2C2C0014
    andi.l #$00000003,d6                               ; +$001EA: 028600000003
    btst #0,d6                                         ; +$001F0: 08060000
    beq.w L_LEGACY_CLOSE_CORE_00216                    ; +$001F4: 67000020
    movea.l 12(a4),a0                                  ; +$001F8: 206C000C
    move.l a0,d0                                       ; +$001FC: 2008
    tst.l d0                                           ; +$001FE: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00216                    ; +$00200: 67000014
    movea.l $0004.w,a6                                 ; +$00204: 2C780004
    jsr -372(a6)                                       ; +$00208: 4EAEFE8C
    tst.l d0                                           ; +$0020C: 4A80
    beq.w L_LEGACY_CLOSE_CORE_00216                    ; +$0020E: 67000006
    bclr #0,d6                                         ; +$00212: 08860000
L_LEGACY_CLOSE_CORE_00216:
    btst #1,d6                                         ; +$00216: 08060001
    beq.w L_LEGACY_CLOSE_CORE_0023C                    ; +$0021A: 67000020
    movea.l 16(a4),a0                                  ; +$0021E: 206C0010
    move.l a0,d0                                       ; +$00222: 2008
    tst.l d0                                           ; +$00224: 4A80
    beq.w L_LEGACY_CLOSE_CORE_0023C                    ; +$00226: 67000014
    movea.l $0004.w,a6                                 ; +$0022A: 2C780004
    jsr -372(a6)                                       ; +$0022E: 4EAEFE8C
    tst.l d0                                           ; +$00232: 4A80
    beq.w L_LEGACY_CLOSE_CORE_0023C                    ; +$00234: 67000006
    bclr #1,d6                                         ; +$00238: 08860001
L_LEGACY_CLOSE_CORE_0023C:
    move.l d6,20(a4)                                   ; +$0023C: 29460014
    move.l d6,d0                                       ; +$00240: 2006
    rts                                                ; +$00242: 4E75
