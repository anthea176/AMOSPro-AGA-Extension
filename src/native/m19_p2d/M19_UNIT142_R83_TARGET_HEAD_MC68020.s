; AGA_NATIVE_MIN_CPU: MC68020
; Unit142 historical R83 source exact; vasm MC68020; no Lib/ASC promotion.
; Absolute offsets $007FA..$00886.
UNIT142_R83_TARGET_HEAD_A5 equ 456

ENTRY_LEGACY_CLOSE_TARGET_00004:
    movem.l d0-d7/a0-a6,-(a7)                          ; +$00004: 48E7FFFE
    movea.l UNIT142_R83_TARGET_HEAD_A5(a5),a2                                 ; +$00008: 246D01C8
    bra.w L_LEGACY_CLOSE_TARGET_001DE                  ; +$0000C: 600001D0
L_LEGACY_CLOSE_TARGET_00010:
    move.l a4,d0                                       ; +$00010: 200C
    tst.l d0                                           ; +$00012: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00084                  ; +$00014: 6700006E
    movea.l 8(a2),a6                                   ; +$00018: 2C6A0008
    move.l a6,d0                                       ; +$0001C: 200E
    tst.l d0                                           ; +$0001E: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00028                  ; +$00020: 67000006
    jsr -228(a6)                                       ; +$00024: 4EAEFF1C
L_LEGACY_CLOSE_TARGET_00028:
    movea.l (a2),a0                                    ; +$00028: 2052
    move.l a0,d0                                       ; +$0002A: 2008
    tst.l d0                                           ; +$0002C: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00056                  ; +$0002E: 67000026
    movea.l 4(a2),a6                                   ; +$00032: 2C6A0004
    movea.l 4(a4),a1                                   ; +$00036: 226C0004
    move.l a1,d0                                       ; +$0003A: 2009
    tst.l d0                                           ; +$0003C: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00046                  ; +$0003E: 67000006
    jsr -774(a6)                                       ; +$00042: 4EAEFCFA
L_LEGACY_CLOSE_TARGET_00046:
    movea.l (a4),a1                                    ; +$00046: 2254
    move.l a1,d0                                       ; +$00048: 2009
    tst.l d0                                           ; +$0004A: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_00056                  ; +$0004C: 67000008
    movea.l (a2),a0                                    ; +$00050: 2052
    jsr -774(a6)                                       ; +$00052: 4EAEFCFA
L_LEGACY_CLOSE_TARGET_00056:
    movea.l $0004.w,a6                                 ; +$00056: 2C780004
    movea.l 16(a4),a0                                  ; +$0005A: 206C0010
    move.l a0,d0                                       ; +$0005E: 2008
    tst.l d0                                           ; +$00060: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0006A                  ; +$00062: 67000006
    jsr -672(a6)                                       ; +$00066: 4EAEFD60
L_LEGACY_CLOSE_TARGET_0006A:
    movea.l 12(a4),a0                                  ; +$0006A: 206C000C
    move.l a0,d0                                       ; +$0006E: 2008
    tst.l d0                                           ; +$00070: 4A80
    beq.w L_LEGACY_CLOSE_TARGET_0007A                  ; +$00072: 67000006
    jsr -672(a6)                                       ; +$00076: 4EAEFD60
L_LEGACY_CLOSE_TARGET_0007A:
    movea.l a4,a1                                      ; +$0007A: 224C
    jsr -690(a6)                                       ; +$0007C: 4EAEFD4E
    clr.l 32(a2)                                       ; +$00080: 42AA0020
L_LEGACY_CLOSE_TARGET_00084:
    tst.l (a2)                                         ; +$00084: 4A92
    beq.w L_LEGACY_CLOSE_TARGET_00096                  ; +$00086: 6700000E
    movea.l (a2),a0                                    ; +$0008A: 2052
    movea.l 4(a2),a6                                   ; +$0008C: 2C6A0004
