; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 R83 source-proven legacy Screen Open helpers, $005F8..$00760 (360 code bytes).
UNIT142_LEGACY_OPEN_HELPER_EDIT equ 1

L_LEGACY_SCREEN_OPEN_00188:
    move.l #$80000039,(a1)+                            ; +$00188: 22FC80000039
    moveq #UNIT142_LEGACY_OPEN_HELPER_EDIT,d0           ; +$0018E: 7001
    move.l d0,(a1)+                                    ; +$00190: 22C0
    moveq #0,d0                                        ; +$00192: 7000
    move.l d0,(a1)+                                    ; +$00194: 22C0
    move.l d0,(a1)+                                    ; +$00196: 22C0
    rts                                                ; +$00198: 4E75
L_LEGACY_SCREEN_OPEN_0019A:
    move.l d7,24(a2)                                   ; +$0019A: 25470018
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                    ; +$0019E: 48E7EFFE
    lea -48(a7),a7                                     ; +$001A2: 4FEFFFD0
    moveq #0,d0                                        ; +$001A6: 7000
    move.l d0,(a7)                                     ; +$001A8: 2E80
    move.l d0,4(a7)                                    ; +$001AA: 2F400004
    move.l d0,8(a7)                                    ; +$001AE: 2F400008
    move.l d0,12(a7)                                   ; +$001B2: 2F40000C
    move.l d0,16(a7)                                   ; +$001B6: 2F400010
    move.l d0,20(a7)                                   ; +$001BA: 2F400014
    move.l d0,24(a7)                                   ; +$001BE: 2F400018
    move.l d0,28(a7)                                   ; +$001C2: 2F40001C
    move.l d0,32(a7)                                   ; +$001C6: 2F400020
    move.l d0,36(a7)                                   ; +$001CA: 2F400024
    move.l d0,40(a7)                                   ; +$001CE: 2F400028
    move.l d0,44(a7)                                   ; +$001D2: 2F40002C
    move.l 12(a2),d0                                   ; +$001D6: 202A000C
    move.w d0,4(a7)                                    ; +$001DA: 3F400004
    move.l 16(a2),d0                                   ; +$001DE: 202A0010
    move.w d0,6(a7)                                    ; +$001E2: 3F400006
    move.l #$000C0408,10(a7)                           ; +$001E6: 2F7C000C0408000A
    move.l #$00031900,14(a7)                           ; +$001EE: 2F7C00031900000E
    move.l (a2),d0                                     ; +$001F6: 2012
    move.l d0,30(a7)                                   ; +$001F8: 2F40001E
    move.w #$000F,46(a7)                               ; +$001FC: 3F7C000F002E
    movea.l a7,a0                                      ; +$00202: 204F
    movea.l 4(a2),a6                                   ; +$00204: 2C6A0004
    jsr -204(a6)                                       ; +$00208: 4EAEFF34
    move.l d0,d1                                       ; +$0020C: 2200
    lea 48(a7),a7                                      ; +$0020E: 4FEF0030
    tst.l d1                                           ; +$00212: 4A81
    beq.w L_LEGACY_SCREEN_OPEN_00222                   ; +$00214: 6700000C
    move.l d1,36(a2)                                   ; +$00218: 25410024
    moveq #1,d3                                        ; +$0021C: 7601
    bra.w L_LEGACY_SCREEN_OPEN_00286                   ; +$0021E: 60000066
L_LEGACY_SCREEN_OPEN_00222:
    movea.l (a2),a0                                    ; +$00222: 2052
    move.l a0,d0                                       ; +$00224: 2008
    tst.l d0                                           ; +$00226: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_00234                   ; +$00228: 6700000A
    movea.l 4(a2),a6                                   ; +$0022C: 2C6A0004
    jsr -66(a6)                                        ; +$00230: 4EAEFFBE
L_LEGACY_SCREEN_OPEN_00234:
    movea.l 8(a2),a1                                   ; +$00234: 226A0008
    move.l a1,d0                                       ; +$00238: 2009
    tst.l d0                                           ; +$0023A: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_00248                   ; +$0023C: 6700000A
    movea.l $0004.w,a6                                 ; +$00240: 2C780004
    jsr -414(a6)                                       ; +$00244: 4EAEFE62
L_LEGACY_SCREEN_OPEN_00248:
    movea.l 4(a2),a1                                   ; +$00248: 226A0004
    move.l a1,d0                                       ; +$0024C: 2009
    tst.l d0                                           ; +$0024E: 4A80
    beq.w L_LEGACY_SCREEN_OPEN_0025C                   ; +$00250: 6700000A
    movea.l $0004.w,a6                                 ; +$00254: 2C780004
    jsr -414(a6)                                       ; +$00258: 4EAEFE62
L_LEGACY_SCREEN_OPEN_0025C:
    moveq #0,d0                                        ; +$0025C: 7000
    move.l d0,(a2)                                     ; +$0025E: 2480
    move.l d0,4(a2)                                    ; +$00260: 25400004
    move.l d0,8(a2)                                    ; +$00264: 25400008
    move.l d0,12(a2)                                   ; +$00268: 2540000C
    move.l d0,16(a2)                                   ; +$0026C: 25400010
    move.l d0,20(a2)                                   ; +$00270: 25400014
    move.l d0,24(a2)                                   ; +$00274: 25400018
    move.l d0,28(a2)                                   ; +$00278: 2540001C
    move.l d0,32(a2)                                   ; +$0027C: 25400020
    move.l d0,36(a2)                                   ; +$00280: 25400024
    moveq #0,d3                                        ; +$00284: 7600
L_LEGACY_SCREEN_OPEN_00286:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                    ; +$00286: 4CDF7FF7
    rts                                                ; +$0028A: 4E75
L_LEGACY_SCREEN_OPEN_0028C:
    move.l a1,d2                                       ; +$0028C: 2409
    jsr -612(a6)                                       ; +$0028E: 4EAEFD9C
    tst.l d0                                           ; +$00292: 4A80
    bne.w L_LEGACY_SCREEN_OPEN_002D8                   ; +$00294: 66000042
    move.l d7,d1                                       ; +$00298: 2207
    andi.l #$FFFF0000,d1                               ; +$0029A: 0281FFFF0000
    cmpi.l #$00010000,d1                               ; +$002A0: 0C8100010000
    bne.w L_LEGACY_SCREEN_OPEN_002D8                   ; +$002A6: 66000030
    move.l d7,d1                                       ; +$002AA: 2207
    addi.l #$00010000,d1                               ; +$002AC: 068100010000
    move.l a6,-(a7)                                    ; +$002B2: 2F0E
    movea.l a5,a6                                      ; +$002B4: 2C4D
    move.l d1,d0                                       ; +$002B6: 2001
    jsr -798(a6)                                       ; +$002B8: 4EAEFCE2
    movea.l (a7)+,a6                                   ; +$002BC: 2C5F
    tst.l d0                                           ; +$002BE: 4A80
    bne.w L_LEGACY_SCREEN_OPEN_002DA                   ; +$002C0: 66000018
    move.l d7,d1                                       ; +$002C4: 2207
    addi.l #$00010000,d1                               ; +$002C6: 068100010000
    movea.l d2,a1                                      ; +$002CC: 2242
    move.l d1,28(a1)                                   ; +$002CE: 2341001C
    suba.l a0,a0                                       ; +$002D2: 91C8
    jsr -612(a6)                                       ; +$002D4: 4EAEFD9C
L_LEGACY_SCREEN_OPEN_002D8:
    rts                                                ; +$002D8: 4E75
L_LEGACY_SCREEN_OPEN_002DA:
    moveq #0,d0                                        ; +$002DA: 7000
    rts                                                ; +$002DC: 4E75
L_LEGACY_SCREEN_OPEN_002DE:
    bsr.w L_LEGACY_SCREEN_OPEN_0019A                   ; +$002DE: 6100FEBA
    lea 12070(a2),a0                                   ; +$002E2: 41EA2F26
    moveq #35,d0                                       ; +$002E6: 7023
L_LEGACY_SCREEN_OPEN_002E8:
    clr.l (a0)+                                        ; +$002E8: 4298
    dbra d0,L_LEGACY_SCREEN_OPEN_002E8                 ; +$002EA: 51C8FFFC
    rts                                                ; +$002EE: 4E75
