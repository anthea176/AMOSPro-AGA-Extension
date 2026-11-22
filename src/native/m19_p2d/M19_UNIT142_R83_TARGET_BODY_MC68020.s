; AGA_NATIVE_MIN_CPU: MC68020
; Unit142 historical R83 source exact; vasm MC68020; no Lib/ASC promotion.
; Absolute offsets $0088A..$0090E.
UNIT142_R83_TARGET_BODY_COUNT equ 4

    clr.l (a2)                                         ; +$00094: 4292
L_LEGACY_CLOSE_TARGET_00096:
    movea.l 8(a2),a1                                   ; +$00096: 226A0008
    move.l a1,d0                                       ; +$0009A: 2009
    tst.l d0                                           ; +$0009C: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_000AE                  ; +$0009E: 6700000E
    movea.l $0004.w,a6                                 ; +$000A2: 2C780004
    jsr -414(a6)                                       ; +$000A6: 4EAEFE62
    clr.l 8(a2)                                        ; +$000AA: 42AA0008
L_LEGACY_CLOSE_TARGET_000AE:
    movea.l 4(a2),a1                                   ; +$000AE: 226A0004
    move.l a1,d0                                       ; +$000B2: 2009
    tst.l d0                                           ; +$000B4: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_000C6                  ; +$000B6: 6700000E
    movea.l $0004.w,a6                                 ; +$000BA: 2C780004
    jsr -414(a6)                                       ; +$000BE: 4EAEFE62
    clr.l 4(a2)                                        ; +$000C2: 42AA0004
L_LEGACY_CLOSE_TARGET_000C6:
    lea 12(a2),a0                                      ; +$000C6: 41EA000C
    moveq #UNIT142_R83_TARGET_BODY_COUNT,d0                                        ; +$000CA: 7004
L_LEGACY_CLOSE_TARGET_000CC:
    clr.l (a0)+                                        ; +$000CC: 4298
    dbra d0,L_LEGACY_CLOSE_TARGET_000CC                ; +$000CE: 51C8FFFC
L_LEGACY_CLOSE_TARGET_000D2:
    movem.l (a7)+,d0-d7/a0-a6                          ; +$000D2: 4CDF7FFF
    rts                                                ; +$000D6: 4E75
L_LEGACY_CLOSE_TARGET_000D8:
    movea.l 36(a2),a3                                  ; +$000D8: 266A0024
    move.l a3,d0                                       ; +$000DC: 200B
    tst.l d0                                           ; +$000DE: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00124                  ; +$000E0: 67000042
    movea.l 86(a3),a4                                  ; +$000E4: 286B0056
    move.l a4,d0                                       ; +$000E8: 200C
    tst.l d0                                           ; +$000EA: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0010A                  ; +$000EC: 6700001C
L_LEGACY_CLOSE_TARGET_000F0:
    movea.l a4,a0                                      ; +$000F0: 204C
    movea.l $0004.w,a6                                 ; +$000F2: 2C780004
    jsr -372(a6)                                       ; +$000F6: 4EAEFE8C
    tst.l d0                                           ; +$000FA: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0010A                  ; +$000FC: 6700000C
    movea.l d0,a1                                      ; +$00100: 2240
    jsr -378(a6)                                       ; +$00102: 4EAEFE86
    bra.w L_LEGACY_CLOSE_TARGET_000F0                  ; +$00106: 6000FFE8
L_LEGACY_CLOSE_TARGET_0010A:
    movea.l 4(a2),a6                                   ; +$0010A: 2C6A0004
    move.l a6,d0                                       ; +$0010E: 200E
    tst.l d0                                           ; +$00110: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0011C                  ; +$00112: 67000008
    movea.l a3,a0                                      ; +$00116: 204B
