; AGA_NATIVE_MIN_CPU: MC68020
; Unit142 historical R83 source exact; vasm MC68020; no Lib/ASC promotion.
; Absolute offsets $009E4..$00A5E.
UNIT142_R83_TARGET_AUX_OFFSET equ 32

L_LEGACY_CLOSE_TARGET_001EE:
    movem.l d0-d7/a0-a6,-(a7)                          ; +$001EE: 48E7FFFE
    move.l a2,d0                                       ; +$001F2: 200A
    tst.l d0                                           ; +$001F4: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00262                  ; +$001F6: 6700006A
    movea.l UNIT142_R83_TARGET_AUX_OFFSET(a2),a4                                  ; +$001FA: 286A0020
    move.l a4,d0                                       ; +$001FE: 200C
    tst.l d0                                           ; +$00200: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00262                  ; +$00202: 6700005E
    move.l 40(a4),d0                                   ; +$00206: 202C0028
    cmpi.l #$43325031,d0                               ; +$0020A: 0C8043325031
    bne.w L_LEGACY_CLOSE_TARGET_00262                  ; +$00210: 66000050
    move.l 28(a4),d5                                   ; +$00214: 2A2C001C
    move.l 24(a4),d6                                   ; +$00218: 2C2C0018
    clr.l 24(a4)                                       ; +$0021C: 42AC0018
    clr.l 28(a4)                                       ; +$00220: 42AC001C
    clr.l 32(a4)                                       ; +$00224: 42AC0020
    clr.l 36(a4)                                       ; +$00228: 42AC0024
    clr.l 40(a4)                                       ; +$0022C: 42AC0028
    move.l d6,d0                                       ; +$00230: 2006
    tst.l d0                                           ; +$00232: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00262                  ; +$00234: 6700002C
    movea.l 8(a2),a6                                   ; +$00238: 2C6A0008
    move.l a6,d0                                       ; +$0023C: 200E
    tst.l d0                                           ; +$0023E: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00248                  ; +$00240: 67000006
    jsr -228(a6)                                       ; +$00244: 4EAEFF1C
L_LEGACY_CLOSE_TARGET_00248:
    move.l d5,d0                                       ; +$00248: 2005
    tst.l d0                                           ; +$0024A: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00258                  ; +$0024C: 6700000A
    movea.l d5,a0                                      ; +$00250: 2045
    movea.l d6,a6                                      ; +$00252: 2C46
    jsr -60(a6)                                        ; +$00254: 4EAEFFC4
L_LEGACY_CLOSE_TARGET_00258:
    movea.l d6,a1                                      ; +$00258: 2246
    movea.l $0004.w,a6                                 ; +$0025A: 2C780004
    jsr -414(a6)                                       ; +$0025E: 4EAEFE62
L_LEGACY_CLOSE_TARGET_00262:
    movem.l (a7)+,d0-d7/a0-a6                          ; +$00262: 4CDF7FFF
    rts                                                ; +$00266: 4E75
