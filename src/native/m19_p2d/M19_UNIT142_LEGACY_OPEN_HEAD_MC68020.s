; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 R83 source-proven legacy Screen Open, $00470..$005D4 (356 code bytes).
UNIT142_LEGACY_OPEN_HEAD_EDIT equ 0

ENTRY_LEGACY_SCREEN_OPEN_00000:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00000: 48E7CFEE
    move.l d3,d7                                       ; +$00004: 2E03
    move.l (a3)+,d6                                    ; +$00006: 2C1B
    move.l (a3)+,d5                                    ; +$00008: 2A1B
    move.l (a3)+,d4                                    ; +$0000A: 281B
    moveq #UNIT142_LEGACY_OPEN_HEAD_EDIT,d3             ; +$0000C: 7600
    movea.l 456(a5),a2                                 ; +$0000E: 246D01C8
    move.l a2,d0                                       ; +$00012: 200A
    tst.l d0                                           ; +$00014: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00016: 67000144
    tst.l (a2)                                         ; +$0001A: 4A92
    bne.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$0001C: 6600013E
    cmpi.l #$00000001,d4                               ; +$00020: 0C8400000001
    bcs.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00026: 65000134
    cmpi.l #$00007FFF,d4                               ; +$0002A: 0C8400007FFF
    bhi.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00030: 6200012A
    move.l d4,d0                                       ; +$00034: 2004
    andi.l #$00000000,d0                               ; +$00036: 028000000000
    nop                                                ; +$0003C: 4E71
    nop                                                ; +$0003E: 4E71
    cmpi.l #$00000001,d5                               ; +$00040: 0C8500000001
    bcs.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00046: 65000114
    cmpi.l #$00007FFF,d5                               ; +$0004A: 0C8500007FFF
    bhi.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00050: 6200010A
    cmpi.l #$00000002,d6                               ; +$00054: 0C8600000002
    bcs.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$0005A: 65000100
    cmpi.l #$00000100,d6                               ; +$0005E: 0C8600000100
    bhi.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00064: 620000F6
    move.l d6,d1                                       ; +$00068: 2206
    subq.l #1,d1                                       ; +$0006A: 5381
    and.l d6,d1                                        ; +$0006C: C286
    bne.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$0006E: 660000EC
    move.l d7,d0                                       ; +$00072: 2007
    andi.l #$00000400,d0                               ; +$00074: 028000000400
    bne.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$0007A: 660000E0
    movea.l $0004.w,a6                                 ; +$0007E: 2C780004
    btst #1,297(a6)                                    ; +$00082: 082E00010129
    beq.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00088: 670000D2
    lea L_LEGACY_SCREEN_OPEN_00164(pc),a1              ; +$0008C: 43FA00D6
    moveq #39,d0                                       ; +$00090: 7027
    jsr -552(a6)                                       ; +$00092: 4EAEFDD8
    tst.l d0                                           ; +$00096: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$00098: 670000C2
    movea.l d0,a4                                      ; +$0009C: 2840
    movea.l $0004.w,a6                                 ; +$0009E: 2C780004
    lea L_LEGACY_SCREEN_OPEN_00176(pc),a1              ; +$000A2: 43FA00D2
    moveq #39,d0                                       ; +$000A6: 7027
    jsr -552(a6)                                       ; +$000A8: 4EAEFDD8
    tst.l d0                                           ; +$000AC: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_00152                   ; +$000AE: 670000A2
    movea.l d0,a5                                      ; +$000B2: 2A40
    move.b 236(a5),d0                                  ; +$000B4: 102D00EC
    andi.b #$0C,d0                                     ; +$000B8: 0200000C
    cmpi.b #$0C,d0                                     ; +$000BC: 0C00000C
    bne.w L_LEGACY_SCREEN_OPEN_00144                   ; +$000C0: 66000082
    move.l d6,d1                                       ; +$000C4: 2206
    moveq #0,d0                                        ; +$000C6: 7000
L_LEGACY_SCREEN_OPEN_000C8:
    lsr.l #1,d1                                        ; +$000C8: E289
    addq.l #1,d0                                       ; +$000CA: 5280
    cmpi.l #$00000001,d1                               ; +$000CC: 0C8100000001
    bne.w L_LEGACY_SCREEN_OPEN_000C8                   ; +$000D2: 6600FFF4
    move.l d0,28(a2)                                   ; +$000D6: 2540001C
    lea -60(a7),a7                                     ; +$000DA: 4FEFFFC4
    movea.l a7,a1                                      ; +$000DE: 224F
    move.l #$80000023,(a1)+                            ; +$000E0: 22FC80000023
    move.l d4,(a1)+                                    ; +$000E6: 22C4
    move.l #$80000024,(a1)+                            ; +$000E8: 22FC80000024
    move.l d5,(a1)+                                    ; +$000EE: 22C5
    move.l #$80000025,(a1)+                            ; +$000F0: 22FC80000025
    move.l d0,(a1)+                                    ; +$000F6: 22C0
    move.l #$80000032,(a1)+                            ; +$000F8: 22FC80000032
    move.l d7,(a1)+                                    ; +$000FE: 22C7
    move.l #$8000003B,(a1)+                            ; +$00100: 22FC8000003B
    moveq #1,d0                                        ; +$00106: 7001
    move.l d0,(a1)+                                    ; +$00108: 22C0
    bsr.w L_LEGACY_SCREEN_OPEN_00188                   ; +$0010A: 6100007C
    nop                                                ; +$0010E: 4E71
    suba.l a0,a0                                       ; +$00110: 91C8
    movea.l a7,a1                                      ; +$00112: 224F
    movea.l a4,a6                                      ; +$00114: 2C4C
    bsr.w L_LEGACY_SCREEN_OPEN_0028C                   ; +$00116: 61000174
    lea 60(a7),a7                                      ; +$0011A: 4FEF003C
    tst.l d0                                           ; +$0011E: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_00144                   ; +$00120: 67000022
    move.l d0,(a2)                                     ; +$00124: 2480
    move.l a4,4(a2)                                    ; +$00126: 254C0004
    move.l a5,8(a2)                                    ; +$0012A: 254D0008
    move.l d4,12(a2)                                   ; +$0012E: 2544000C
    move.l d5,16(a2)                                   ; +$00132: 25450010
    move.l d6,20(a2)                                   ; +$00136: 25460014
    bsr.w L_LEGACY_SCREEN_OPEN_002DE                   ; +$0013A: 610001A2
    bra.w L_LEGACY_SCREEN_OPEN_0015C                   ; +$0013E: 6000001C
    nop                                                ; +$00142: 4E71
L_LEGACY_SCREEN_OPEN_00144:
    clr.l 28(a2)                                       ; +$00144: 42AA001C
    movea.l a5,a1                                      ; +$00148: 224D
    movea.l $0004.w,a6                                 ; +$0014A: 2C780004
    jsr -414(a6)                                       ; +$0014E: 4EAEFE62
L_LEGACY_SCREEN_OPEN_00152:
    movea.l a4,a1                                      ; +$00152: 224C
    movea.l $0004.w,a6                                 ; +$00154: 2C780004
    jsr -414(a6)                                       ; +$00158: 4EAEFE62
L_LEGACY_SCREEN_OPEN_0015C:
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6              ; +$0015C: 4CDF77F3
    moveq #0,d2                                        ; +$00160: 7400
    rts                                                ; +$00162: 4E75
