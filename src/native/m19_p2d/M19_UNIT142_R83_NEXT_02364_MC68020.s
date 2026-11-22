; AGA_NATIVE_MIN_CPU: MC68020
; R83 source-verified UNIT142 $02364..$02580; original builder byte identity.
UNIT142_R83_NEXT_A5_OFFSET equ 456

ENTRY_LEGACY_NEXT_02364_00000:
    move.l (a3)+,d5                                    ; +$00000: 2A1B
    move.l (a3)+,d4                                    ; +$00002: 281B
    move.l (a3)+,d1                                    ; +$00004: 221B
    move.l (a3)+,d0                                    ; +$00006: 201B
    movea.l UNIT142_R83_NEXT_A5_OFFSET(a5),a4                                 ; +$00008: 286D01C8
    move.l a4,d6                                       ; +$0000C: 2C0C
    tst.l d6                                           ; +$0000E: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$00010: 670001FC
    move.l (a4),d6                                     ; +$00014: 2C14
    tst.l d6                                           ; +$00016: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$00018: 670001F4
    movea.l 32(a4),a2                                  ; +$0001C: 246C0020
    move.l a2,d6                                       ; +$00020: 2C0A
    tst.l d6                                           ; +$00022: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$00024: 670001E8
    movea.l 8(a4),a6                                   ; +$00028: 2C6C0008
    move.l a6,d6                                       ; +$0002C: 2C0E
    tst.l d6                                           ; +$0002E: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$00030: 670001DC
    tst.l d0                                           ; +$00034: 4A80
    bmi.w L_LEGACY_NEXT_02364_0020E                    ; +$00036: 6B0001D6
    tst.l d1                                           ; +$0003A: 4A81
    bmi.w L_LEGACY_NEXT_02364_0020E                    ; +$0003C: 6B0001D0
    tst.l d3                                           ; +$00040: 4A83
    bmi.w L_LEGACY_NEXT_02364_0020E                    ; +$00042: 6B0001CA
    tst.l d4                                           ; +$00046: 4A84
    ble.w L_LEGACY_NEXT_02364_0020E                    ; +$00048: 6F0001C4
    tst.l d5                                           ; +$0004C: 4A85
    ble.w L_LEGACY_NEXT_02364_0020E                    ; +$0004E: 6F0001BE
    move.l 12(a4),d6                                   ; +$00052: 2C2C000C
    tst.l d6                                           ; +$00056: 4A86
    ble.w L_LEGACY_NEXT_02364_0020E                    ; +$00058: 6F0001B4
    cmpi.l #$00007FFF,d6                               ; +$0005C: 0C8600007FFF
    bgt.w L_LEGACY_NEXT_02364_0020E                    ; +$00062: 6E0001AA
    move.l 16(a4),d6                                   ; +$00066: 2C2C0010
    tst.l d6                                           ; +$0006A: 4A86
    ble.w L_LEGACY_NEXT_02364_0020E                    ; +$0006C: 6F0001A0
    cmpi.l #$00007FFF,d6                               ; +$00070: 0C8600007FFF
    bgt.w L_LEGACY_NEXT_02364_0020E                    ; +$00076: 6E000196
    move.l 12(a4),d6                                   ; +$0007A: 2C2C000C
    sub.l d4,d6                                        ; +$0007E: 9C84
    tst.l d6                                           ; +$00080: 4A86
    bmi.w L_LEGACY_NEXT_02364_0020E                    ; +$00082: 6B00018A
    cmp.l d6,d0                                        ; +$00086: B086
    bgt.w L_LEGACY_NEXT_02364_0020E                    ; +$00088: 6E000184
    move.l 16(a4),d6                                   ; +$0008C: 2C2C0010
    sub.l d5,d6                                        ; +$00090: 9C85
    tst.l d6                                           ; +$00092: 4A86
    bmi.w L_LEGACY_NEXT_02364_0020E                    ; +$00094: 6B000178
    cmp.l d6,d1                                        ; +$00098: B286
    bgt.w L_LEGACY_NEXT_02364_0020E                    ; +$0009A: 6E000172
    tst.l 8(a2)                                        ; +$0009E: 4AAA0008
    beq.w L_LEGACY_NEXT_02364_000AC                    ; +$000A2: 67000008
    movea.l (a2),a0                                    ; +$000A6: 2052
    bra.w L_LEGACY_NEXT_02364_000B0                    ; +$000A8: 60000006
L_LEGACY_NEXT_02364_000AC:
    movea.l 4(a2),a0                                   ; +$000AC: 206A0004
L_LEGACY_NEXT_02364_000B0:
    move.l a0,d6                                       ; +$000B0: 2C08
    tst.l d6                                           ; +$000B2: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$000B4: 67000158
    movea.l (a0),a0                                    ; +$000B8: 2050
    move.l a0,d6                                       ; +$000BA: 2C08
    tst.l d6                                           ; +$000BC: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$000BE: 6700014E
    move.l #$00000000,d6                               ; +$000C2: 2C3C00000000
    move.w (a0),d6                                     ; +$000C8: 3C10
    lsl.l #3,d6                                        ; +$000CA: E78E
    cmp.l 12(a4),d6                                    ; +$000CC: BCAC000C
    blt.w L_LEGACY_NEXT_02364_0020E                    ; +$000D0: 6D00013C
    move.l #$00000000,d6                               ; +$000D4: 2C3C00000000
    move.w 2(a0),d6                                    ; +$000DA: 3C280002
    cmp.l 16(a4),d6                                    ; +$000DE: BCAC0010
    blt.w L_LEGACY_NEXT_02364_0020E                    ; +$000E2: 6D00012A
    move.l #$00000000,d6                               ; +$000E6: 2C3C00000000
    move.b 5(a0),d6                                    ; +$000EC: 1C280005
    cmp.l 28(a4),d6                                    ; +$000F0: BCAC001C
    bne.w L_LEGACY_NEXT_02364_0020E                    ; +$000F4: 66000118
    tst.l d6                                           ; +$000F8: 4A86
    ble.w L_LEGACY_NEXT_02364_0020E                    ; +$000FA: 6F000112
    cmpi.l #$00000008,d6                               ; +$000FE: 0C8600000008
    bgt.w L_LEGACY_NEXT_02364_0020E                    ; +$00104: 6E000108
    move.l d6,d2                                       ; +$00108: 2406
    movea.l a0,a1                                      ; +$0010A: 2248
    addq.l #8,a1                                       ; +$0010C: 5089
L_LEGACY_NEXT_02364_0010E:
    move.l (a1)+,d6                                    ; +$0010E: 2C19
    tst.l d6                                           ; +$00110: 4A86
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$00112: 670000FA
    cmpi.l #$FFFFFFFF,d6                               ; +$00116: 0C86FFFFFFFF
    beq.w L_LEGACY_NEXT_02364_0020E                    ; +$0011C: 670000F0
    subq.l #1,d2                                       ; +$00120: 5382
    bne.w L_LEGACY_NEXT_02364_0010E                    ; +$00122: 6600FFEA
    move.l #$00000000,d2                               ; +$00126: 243C00000000
    move.b 5(a0),d2                                    ; +$0012C: 14280005
    move.l #$00000001,d6                               ; +$00130: 2C3C00000001
L_LEGACY_NEXT_02364_00136:
    lsl.l #1,d6                                        ; +$00136: E38E
    subq.l #1,d2                                       ; +$00138: 5382
    bne.w L_LEGACY_NEXT_02364_00136                    ; +$0013A: 6600FFFA
    cmp.l d6,d3                                        ; +$0013E: B686
    bcc.w L_LEGACY_NEXT_02364_0020E                    ; +$00140: 640000CC
    move.l d6,-(a7)                                    ; +$00144: 2F06
    move.l 20(a2),d6                                   ; +$00146: 2C2A0014
    andi.l #$00000001,d6                               ; +$0014A: 028600000001
    beq.w L_LEGACY_NEXT_02364_001A6                    ; +$00150: 67000054
    move.l d0,-(a7)                                    ; +$00154: 2F00
    move.l d1,-(a7)                                    ; +$00156: 2F01
    move.l a0,-(a7)                                    ; +$00158: 2F08
    move.l a1,-(a7)                                    ; +$0015A: 2F09
    movea.l 12(a2),a0                                  ; +$0015C: 206A000C
    move.l a0,d6                                       ; +$00160: 2C08
    tst.l d6                                           ; +$00162: 4A86
    beq.w L_LEGACY_NEXT_02364_00194                    ; +$00164: 6700002E
    movea.l $0004.w,a6                                 ; +$00168: 2C780004
    jsr -372(a6)                                       ; +$0016C: 4EAEFE8C
    tst.l d0                                           ; +$00170: 4A80
    beq.w L_LEGACY_NEXT_02364_00194                    ; +$00172: 67000020
    move.l 20(a2),d6                                   ; +$00176: 2C2A0014
    andi.l #$FFFFFFFE,d6                               ; +$0017A: 0286FFFFFFFE
    move.l d6,20(a2)                                   ; +$00180: 25460014
    movea.l 8(a4),a6                                   ; +$00184: 2C6C0008
    movea.l (a7)+,a1                                   ; +$00188: 225F
    movea.l (a7)+,a0                                   ; +$0018A: 205F
    move.l (a7)+,d1                                    ; +$0018C: 221F
    move.l (a7)+,d0                                    ; +$0018E: 201F
    bra.w L_LEGACY_NEXT_02364_001A6                    ; +$00190: 60000014
L_LEGACY_NEXT_02364_00194:
    movea.l 8(a4),a6                                   ; +$00194: 2C6C0008
    movea.l (a7)+,a1                                   ; +$00198: 225F
    movea.l (a7)+,a0                                   ; +$0019A: 205F
    move.l (a7)+,d1                                    ; +$0019C: 221F
    move.l (a7)+,d0                                    ; +$0019E: 201F
    move.l (a7)+,d6                                    ; +$001A0: 2C1F
    bra.w L_LEGACY_NEXT_02364_0020E                    ; +$001A2: 6000006A
L_LEGACY_NEXT_02364_001A6:
    move.l (a7)+,d6                                    ; +$001A6: 2C1F
    move.l d3,-(a7)                                    ; +$001A8: 2F03
    move.l d6,-(a7)                                    ; +$001AA: 2F06
    movea.l a0,a4                                      ; +$001AC: 2848
    move.l d0,d2                                       ; +$001AE: 2400
    move.l d1,d3                                       ; +$001B0: 2601
    move.l #$00000001,d7                               ; +$001B2: 2E3C00000001
L_LEGACY_NEXT_02364_001B8:
    move.l 4(a7),d6                                    ; +$001B8: 2C2F0004
    and.l d7,d6                                        ; +$001BC: CC87
    tst.l d6                                           ; +$001BE: 4A86
    beq.w L_LEGACY_NEXT_02364_001CE                    ; +$001C0: 6700000C
    move.l #$000000F0,d6                               ; +$001C4: 2C3C000000F0
    bra.w L_LEGACY_NEXT_02364_001D4                    ; +$001CA: 60000008
L_LEGACY_NEXT_02364_001CE:
    move.l #$00000000,d6                               ; +$001CE: 2C3C00000000
L_LEGACY_NEXT_02364_001D4:
    move.l d2,d0                                       ; +$001D4: 2002
    move.l d3,d1                                       ; +$001D6: 2203
    movea.l a4,a0                                      ; +$001D8: 204C
    movea.l a4,a1                                      ; +$001DA: 224C
    movea.l #$00000000,a2                              ; +$001DC: 247C00000000
    jsr -30(a6)                                        ; +$001E2: 4EAEFFE2
    tst.l d0                                           ; +$001E6: 4A80
    beq.w L_LEGACY_NEXT_02364_00202                    ; +$001E8: 67000018
    jsr -228(a6)                                       ; +$001EC: 4EAEFF1C
    lsl.l #1,d7                                        ; +$001F0: E38F
    cmp.l (a7),d7                                      ; +$001F2: BE97
    bne.w L_LEGACY_NEXT_02364_001B8                    ; +$001F4: 6600FFC2
    move.l #$00000001,d3                               ; +$001F8: 263C00000001
    bra.w L_LEGACY_NEXT_02364_00208                    ; +$001FE: 60000008
L_LEGACY_NEXT_02364_00202:
    move.l #$00000000,d3                               ; +$00202: 263C00000000
L_LEGACY_NEXT_02364_00208:
    addq.l #8,a7                                       ; +$00208: 508F
    bra.w L_LEGACY_NEXT_02364_00214                    ; +$0020A: 60000008
L_LEGACY_NEXT_02364_0020E:
    move.l #$00000000,d3                               ; +$0020E: 263C00000000
L_LEGACY_NEXT_02364_00214:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$00214: 4CDF77F7
    moveq #0,d2                                        ; +$00218: 7400
    rts                                                ; +$0021A: 4E75
