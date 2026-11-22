; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P0e AGA object bridge source-backed from M19 emitter.
; UNIT142+$0E620..$0E7F6, 470 bytes of Motorola instructions.
; SHA256 ddcd43fdfd7922650076dfccc6c31a347dea0b4f5df6350a629882ecb4f3046b
UNIT142_P0E_AGA_BRIDGE_RESULT equ 0

ENTRY_P0E_AGA_BRIDGE_00000:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00000: 48E7EFEE
    move.l #$00000000,d7                               ; +$00004: 2E3C00000000
    bra.w L_P0E_AGA_BRIDGE_00038                       ; +$0000A: 6000002C
ENTRY_P0E_AGA_BRIDGE_0000E:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$0000E: 48E7EFEE
    move.l #$00000124,d7                               ; +$00012: 2E3C00000124
    bra.w L_P0E_AGA_BRIDGE_00038                       ; +$00018: 6000001E
ENTRY_P0E_AGA_BRIDGE_0001C:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$0001C: 48E7EFEE
    move.l #$000001A8,d7                               ; +$00020: 2E3C000001A8
    bra.w L_P0E_AGA_BRIDGE_00038                       ; +$00026: 60000010
ENTRY_P0E_AGA_BRIDGE_0002A:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$0002A: 48E7EFEE
    move.l #$00000272,d7                               ; +$0002E: 2E3C00000272
    bra.w L_P0E_AGA_BRIDGE_00038                       ; +$00034: 60000002
L_P0E_AGA_BRIDGE_00038:
    lea -32(a7),a7                                     ; +$00038: 4FEFFFE0
    movea.l a7,a2                                      ; +$0003C: 244F
    move.l d0,(a2)                                     ; +$0003E: 2480
    move.l d1,4(a2)                                    ; +$00040: 25410004
    move.l d4,8(a2)                                    ; +$00044: 25440008
    move.l d5,12(a2)                                   ; +$00048: 2545000C
    move.l d6,16(a2)                                   ; +$0004C: 25460010
    move.l a1,20(a2)                                   ; +$00050: 25490014
    move.l d7,24(a2)                                   ; +$00054: 25470018
    move.l #$00000000,d3                               ; +$00058: 263C00000000
    movea.l $0004.w,a0                                 ; +$0005E: 20780004
    move.l a0,d0                                       ; +$00062: 2008
    tst.l d0                                           ; +$00064: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$00066: 67000162
    move.w 296(a0),d0                                  ; +$0006A: 30280128
    btst #1,d0                                         ; +$0006E: 08000001
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$00072: 67000156
    move.l a5,d0                                       ; +$00076: 200D
    tst.l d0                                           ; +$00078: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$0007A: 6700014E
    andi.l #$00000001,d0                               ; +$0007E: 028000000001
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$00084: 66000144
    move.l 24(a2),d0                                   ; +$00088: 202A0018
    cmpi.l #$FFFFFFFF,d0                               ; +$0008C: 0C80FFFFFFFF
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$00092: 67000136
    move.l 456(a5),d0                                  ; +$00096: 202D01C8
    tst.l d0                                           ; +$0009A: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$0009C: 6700012C
    andi.l #$00000001,d0                               ; +$000A0: 028000000001
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$000A6: 66000122
    movea.l 456(a5),a1                                 ; +$000AA: 226D01C8
    movea.l $0004.w,a6                                 ; +$000AE: 2C780004
    jsr -534(a6)                                       ; +$000B2: 4EAEFDEA
    tst.l d0                                           ; +$000B6: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$000B8: 67000110
    movea.l 456(a5),a0                                 ; +$000BC: 206D01C8
    tst.l (a0)                                         ; +$000C0: 4A90
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$000C2: 67000106
    move.l 456(a5),d0                                  ; +$000C6: 202D01C8
    cmpi.l #$00000168,d0                               ; +$000CA: 0C8000000168
    bcs.w L_P0E_AGA_BRIDGE_001CA                       ; +$000D0: 650000F8
    subi.l #$00000168,d0                               ; +$000D4: 048000000168
    movea.l d0,a4                                      ; +$000DA: 2840
    andi.l #$00000001,d0                               ; +$000DC: 028000000001
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$000E2: 660000E6
    movea.l a4,a1                                      ; +$000E6: 224C
    movea.l $0004.w,a6                                 ; +$000E8: 2C780004
    jsr -534(a6)                                       ; +$000EC: 4EAEFDEA
    tst.l d0                                           ; +$000F0: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$000F2: 670000D6
    move.l (a4),d0                                     ; +$000F6: 2014
    cmpi.l #$48E7FFFE,d0                               ; +$000F8: 0C8048E7FFFE
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$000FE: 660000CA
    move.l 4(a4),d0                                    ; +$00102: 202C0004
    cmpi.l #$246D01C8,d0                               ; +$00106: 0C80246D01C8
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$0010C: 660000BC
    move.l 8(a4),d0                                    ; +$00110: 202C0008
    cmpi.l #$60000978,d0                               ; +$00114: 0C8060000978
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$0011A: 660000AE
    move.l 456(a5),d0                                  ; +$0011E: 202D01C8
    addi.l #$0000DB42,d0                               ; +$00122: 06800000DB42
    bcs.w L_P0E_AGA_BRIDGE_001CA                       ; +$00128: 650000A0
    andi.l #$00000001,d0                               ; +$0012C: 028000000001
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$00132: 66000096
    move.l 456(a5),d0                                  ; +$00136: 202D01C8
    addi.l #$0000DB42,d0                               ; +$0013A: 06800000DB42
    movea.l d0,a4                                      ; +$00140: 2840
    movea.l a4,a1                                      ; +$00142: 224C
    movea.l $0004.w,a6                                 ; +$00144: 2C780004
    jsr -534(a6)                                       ; +$00148: 4EAEFDEA
    tst.l d0                                           ; +$0014C: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$0014E: 6700007A
    move.l a4,d0                                       ; +$00152: 200C
    addi.l #$0000091B,d0                               ; +$00154: 06800000091B
    bcs.w L_P0E_AGA_BRIDGE_001CA                       ; +$0015A: 6500006E
    movea.l d0,a1                                      ; +$0015E: 2240
    movea.l $0004.w,a6                                 ; +$00160: 2C780004
    jsr -534(a6)                                       ; +$00164: 4EAEFDEA
    tst.l d0                                           ; +$00168: 4A80
    beq.w L_P0E_AGA_BRIDGE_001CA                       ; +$0016A: 6700005E
    move.l (a4),d0                                     ; +$0016E: 2014
    cmpi.l #$48E7EFEE,d0                               ; +$00170: 0C8048E7EFEE
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$00176: 66000052
    move.l 4(a4),d0                                    ; +$0017A: 202C0004
    cmpi.l #$4FEFFFC0,d0                               ; +$0017E: 0C804FEFFFC0
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$00184: 66000044
    move.l 8(a4),d0                                    ; +$00188: 202C0008
    cmpi.l #$244F254D,d0                               ; +$0018C: 0C80244F254D
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$00192: 66000036
    move.l 12(a4),d0                                   ; +$00196: 202C000C
    cmpi.l #$0014257C,d0                               ; +$0019A: 0C800014257C
    bne.w L_P0E_AGA_BRIDGE_001CA                       ; +$001A0: 66000028
    move.l a4,d0                                       ; +$001A4: 200C
    move.l 24(a2),d1                                   ; +$001A6: 222A0018
    add.l d1,d0                                        ; +$001AA: D081
    bcs.w L_P0E_AGA_BRIDGE_001CA                       ; +$001AC: 6500001C
    movea.l d0,a4                                      ; +$001B0: 2840
    move.l (a2),d0                                     ; +$001B2: 2012
    move.l 4(a2),d1                                    ; +$001B4: 222A0004
    move.l 8(a2),d4                                    ; +$001B8: 282A0008
    move.l 12(a2),d5                                   ; +$001BC: 2A2A000C
    move.l 16(a2),d6                                   ; +$001C0: 2C2A0010
    movea.l 20(a2),a1                                  ; +$001C4: 226A0014
    jsr (a4)                                           ; +$001C8: 4E94
L_P0E_AGA_BRIDGE_001CA:
    lea 32(a7),a7                                      ; +$001CA: 4FEF0020
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$001CE: 4CDF77F7
    moveq #UNIT142_P0E_AGA_BRIDGE_RESULT,d2                                        ; +$001D2: 7400
    rts                                                ; +$001D4: 4E75
