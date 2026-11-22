; AGA_NATIVE_MIN_CPU: MC68020
; Unit142 historical R83 source exact; vasm MC68020; no Lib/ASC promotion.
; Absolute offsets $00912..$009E0.
UNIT142_R83_TARGET_WAIT_LIMIT equ 301

L_LEGACY_CLOSE_TARGET_0011C:
    move.l #$00000000,36(a2)                           ; +$0011C: 257C000000000024
L_LEGACY_CLOSE_TARGET_00124:
    movea.l 32(a2),a4                                  ; +$00124: 286A0020
    rts                                                ; +$00128: 4E75
L_LEGACY_CLOSE_TARGET_0012A:
    bsr.w L_LEGACY_CLOSE_TARGET_00140                  ; +$0012A: 61000014
    tst.l d0                                           ; +$0012E: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0013C                  ; +$00130: 6700000A
    bsr.w L_LEGACY_CLOSE_TARGET_000D8                  ; +$00134: 6100FFA2
    bra.w L_LEGACY_CLOSE_TARGET_00010                  ; +$00138: 6000FED6
L_LEGACY_CLOSE_TARGET_0013C:
    bra.w L_LEGACY_CLOSE_TARGET_000D2                  ; +$0013C: 6000FF94
L_LEGACY_CLOSE_TARGET_00140:
    movea.l 32(a2),a4                                  ; +$00140: 286A0020
    move.l a4,d0                                       ; +$00144: 200C
    tst.l d0                                           ; +$00146: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00178                  ; +$00148: 6700002E
    moveq #0,d4                                        ; +$0014C: 7800
L_LEGACY_CLOSE_TARGET_0014E:
    bsr.w L_LEGACY_CLOSE_TARGET_00180                  ; +$0014E: 61000030
    tst.l d0                                           ; +$00152: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00178                  ; +$00154: 67000022
    addq.l #1,d4                                       ; +$00158: 5284
    cmpi.l #UNIT142_R83_TARGET_WAIT_LIMIT,d4                               ; +$0015A: 0C840000012D
    bge.w L_LEGACY_CLOSE_TARGET_0017C                  ; +$00160: 6C00001A
    movea.l 8(a2),a6                                   ; +$00164: 2C6A0008
    move.l a6,d0                                       ; +$00168: 200E
    tst.l d0                                           ; +$0016A: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0017C                  ; +$0016C: 6700000E
    jsr -270(a6)                                       ; +$00170: 4EAEFEF2
    bra.w L_LEGACY_CLOSE_TARGET_0014E                  ; +$00174: 6000FFD8
L_LEGACY_CLOSE_TARGET_00178:
    moveq #1,d0                                        ; +$00178: 7001
    rts                                                ; +$0017A: 4E75
L_LEGACY_CLOSE_TARGET_0017C:
    moveq #0,d0                                        ; +$0017C: 7000
    rts                                                ; +$0017E: 4E75
L_LEGACY_CLOSE_TARGET_00180:
    move.l 20(a4),d6                                   ; +$00180: 2C2C0014
    andi.l #$00000003,d6                               ; +$00184: 028600000003
    btst #0,d6                                         ; +$0018A: 08060000
    beq.w L_LEGACY_CLOSE_TARGET_001B0                  ; +$0018E: 67000020
    movea.l 12(a4),a0                                  ; +$00192: 206C000C
    move.l a0,d0                                       ; +$00196: 2008
    tst.l d0                                           ; +$00198: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_001B0                  ; +$0019A: 67000014
    movea.l $0004.w,a6                                 ; +$0019E: 2C780004
    jsr -372(a6)                                       ; +$001A2: 4EAEFE8C
    tst.l d0                                           ; +$001A6: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_001B0                  ; +$001A8: 67000006
    bclr #0,d6                                         ; +$001AC: 08860000
L_LEGACY_CLOSE_TARGET_001B0:
    btst #1,d6                                         ; +$001B0: 08060001
    beq.w L_LEGACY_CLOSE_TARGET_001D6                  ; +$001B4: 67000020
    movea.l 16(a4),a0                                  ; +$001B8: 206C0010
    move.l a0,d0                                       ; +$001BC: 2008
    tst.l d0                                           ; +$001BE: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_001D6                  ; +$001C0: 67000014
    movea.l $0004.w,a6                                 ; +$001C4: 2C780004
    jsr -372(a6)                                       ; +$001C8: 4EAEFE8C
    tst.l d0                                           ; +$001CC: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_001D6                  ; +$001CE: 67000006
    bclr #1,d6                                         ; +$001D2: 08860001
L_LEGACY_CLOSE_TARGET_001D6:
    move.l d6,20(a4)                                   ; +$001D6: 29460014
    move.l d6,d0                                       ; +$001DA: 2006
    rts                                                ; +$001DC: 4E75
L_LEGACY_CLOSE_TARGET_001DE:
    bsr.w L_LEGACY_CLOSE_TARGET_001EE                  ; +$001DE: 6100000E
    bra.w L_LEGACY_CLOSE_TARGET_0012A                  ; +$001E2: 6000FF46
ENTRY_LEGACY_CLOSE_TARGET_001E6:
    bsr.w L_LEGACY_CLOSE_TARGET_001EE                  ; +$001E6: 61000006
