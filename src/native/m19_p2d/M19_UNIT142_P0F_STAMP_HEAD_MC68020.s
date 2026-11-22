; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P0f source-owned segment $00000..$000E2, emitter-exact MC68020.
; P0f whole code-and-markers SHA256 fa7d64ce347c08d0e523d5d31ac8a3e3b5175fdd38867bca76c6d7941aa9f2b4
UNIT142_P0F_STAMP_HEAD_EDIT equ 0

ENTRY_P0F_IDENTITY_CODE_00000:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00000: 48E7EFEE
    move.l #UNIT142_P0F_STAMP_HEAD_EDIT,d7                               ; +$00004: 2E3C00000000
    bra.w L_P0F_IDENTITY_CODE_0001C                    ; +$0000A: 60000010
ENTRY_P0F_IDENTITY_CODE_0000E:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$0000E: 48E7EFEE
    move.l #$00000001,d7                               ; +$00012: 2E3C00000001
    bra.w L_P0F_IDENTITY_CODE_0001C                    ; +$00018: 60000002
L_P0F_IDENTITY_CODE_0001C:
    lea -96(a7),a7                                     ; +$0001C: 4FEFFFA0
    movea.l a7,a2                                      ; +$00020: 244F
    move.l d0,(a2)                                     ; +$00022: 2480
    move.l a1,4(a2)                                    ; +$00024: 25490004
    move.l d7,8(a2)                                    ; +$00028: 25470008
    move.l a5,12(a2)                                   ; +$0002C: 254D000C
    move.l #$00000000,32(a2)                           ; +$00030: 257C000000000020
    movea.l $0004.w,a0                                 ; +$00038: 20780004
    move.l a0,d0                                       ; +$0003C: 2008
    tst.l d0                                           ; +$0003E: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$00040: 67000274
    move.w 296(a0),d0                                  ; +$00044: 30280128
    btst #1,d0                                         ; +$00048: 08000001
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$0004C: 67000268
    move.l 12(a2),d0                                   ; +$00050: 202A000C
    tst.l d0                                           ; +$00054: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$00056: 6700025E
    andi.l #$00000001,d0                               ; +$0005A: 028000000001
    bne.w L_P0F_IDENTITY_CODE_002B6                    ; +$00060: 66000254
    move.l (a2),d0                                     ; +$00064: 2012
    cmpi.l #$00000005,d0                               ; +$00066: 0C8000000005
    bcs.w L_P0F_IDENTITY_CODE_002B6                    ; +$0006C: 65000248
    cmpi.l #$0000FFFF,d0                               ; +$00070: 0C800000FFFF
    bhi.w L_P0F_IDENTITY_CODE_002B6                    ; +$00076: 6200023E
    move.l 4(a2),d0                                    ; +$0007A: 202A0004
    tst.l d0                                           ; +$0007E: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$00080: 67000234
    andi.l #$00000001,d0                               ; +$00084: 028000000001
    bne.w L_P0F_IDENTITY_CODE_002B6                    ; +$0008A: 6600022A
    movea.l 4(a2),a1                                   ; +$0008E: 226A0004
    movea.l $0004.w,a6                                 ; +$00092: 2C780004
    jsr -534(a6)                                       ; +$00096: 4EAEFDEA
    tst.l d0                                           ; +$0009A: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$0009C: 67000218
    move.l 4(a2),d0                                    ; +$000A0: 202A0004
    addi.l #$0000000F,d0                               ; +$000A4: 06800000000F
    bcs.w L_P0F_IDENTITY_CODE_002B6                    ; +$000AA: 6500020A
    move.l d0,36(a2)                                   ; +$000AE: 25400024
    movea.l 36(a2),a1                                  ; +$000B2: 226A0024
    movea.l $0004.w,a6                                 ; +$000B6: 2C780004
    jsr -534(a6)                                       ; +$000BA: 4EAEFDEA
    tst.l d0                                           ; +$000BE: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$000C0: 670001F4
    movea.l 12(a2),a0                                  ; +$000C4: 206A000C
    move.l 1514(a0),d0                                 ; +$000C8: 202805EA
    move.l d0,16(a2)                                   ; +$000CC: 25400010
    tst.l d0                                           ; +$000D0: 4A80
    beq.w L_P0F_IDENTITY_CODE_002B6                    ; +$000D2: 670001E2
    andi.l #$00000001,d0                               ; +$000D6: 028000000001
    bne.w L_P0F_IDENTITY_CODE_002B6                    ; +$000DC: 660001D8
    move.l (a2),d0                                     ; +$000E0: 2012
