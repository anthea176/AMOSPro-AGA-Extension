; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P0f source-owned segment $00332..$003F8, emitter-exact MC68020.
; P0f whole code-and-markers SHA256 fa7d64ce347c08d0e523d5d31ac8a3e3b5175fdd38867bca76c6d7941aa9f2b4
UNIT142_P0F_BIND_CHECK_EDIT equ 0

    tst.l d3                                           ; +$00332: 4A83
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$00334: 67000168
    move.l (a2),d0                                     ; +$00338: 2012
    subq.l #1,d0                                       ; +$0033A: 5380
    mulu.w #$0010,d0                                   ; +$0033C: C0FC0010
    lea 364(pc),a0                                     ; +$00340: 41FA016C
    adda.l d0,a0                                       ; +$00344: D1C0
    move.l 96(a2),d1                                   ; +$00346: 222A0060
    move.l d1,(a0)                                     ; +$0034A: 2081
    move.l 100(a2),d1                                  ; +$0034C: 222A0064
    move.l d1,4(a0)                                    ; +$00350: 21410004
    move.l 104(a2),d1                                  ; +$00354: 222A0068
    move.l d1,8(a0)                                    ; +$00358: 21410008
    move.l 108(a2),d1                                  ; +$0035C: 222A006C
    move.l d1,12(a0)                                   ; +$00360: 2141000C
    move.l #$00000001,24(a2)                           ; +$00364: 257C000000010018
    bra.w L_P0F_IDENTITY_CODE_0049E                    ; +$0036C: 60000130
ENTRY_P0F_IDENTITY_CODE_00370:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00370: 48E7EFEE
    lea -160(a7),a7                                    ; +$00374: 4FEFFF60
    movea.l a7,a2                                      ; +$00378: 244F
    move.l d0,(a2)                                     ; +$0037A: 2480
    move.l a5,28(a2)                                   ; +$0037C: 254D001C
    move.l #UNIT142_P0F_BIND_CHECK_EDIT,24(a2)                           ; +$00380: 257C000000000018
    move.l a1,20(a2)                                   ; +$00388: 25490014
    move.l (a2),d0                                     ; +$0038C: 2012
    cmpi.l #$00000001,d0                               ; +$0038E: 0C8000000001
    bcs.w L_P0F_IDENTITY_CODE_0049E                    ; +$00394: 65000108
    cmpi.l #$00000040,d0                               ; +$00398: 0C8000000040
    bhi.w L_P0F_IDENTITY_CODE_0049E                    ; +$0039E: 620000FE
    move.l 20(a2),d0                                   ; +$003A2: 202A0014
    tst.l d0                                           ; +$003A6: 4A80
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$003A8: 670000F4
    andi.l #$00000001,d0                               ; +$003AC: 028000000001
    bne.w L_P0F_IDENTITY_CODE_0049E                    ; +$003B2: 660000EA
    move.l 20(a2),d0                                   ; +$003B6: 202A0014
    addi.l #$00000017,d0                               ; +$003BA: 068000000017
    bcs.w L_P0F_IDENTITY_CODE_0049E                    ; +$003C0: 650000DC
    move.l d0,12(a2)                                   ; +$003C4: 2540000C
    movea.l 20(a2),a1                                  ; +$003C8: 226A0014
    movea.l $0004.w,a6                                 ; +$003CC: 2C780004
    jsr -534(a6)                                       ; +$003D0: 4EAEFDEA
    tst.l d0                                           ; +$003D4: 4A80
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$003D6: 670000C6
    movea.l 12(a2),a1                                  ; +$003DA: 226A000C
    movea.l $0004.w,a6                                 ; +$003DE: 2C780004
    jsr -534(a6)                                       ; +$003E2: 4EAEFDEA
    tst.l d0                                           ; +$003E6: 4A80
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$003E8: 670000B4
    move.l a2,d0                                       ; +$003EC: 200A
    addi.l #$00000040,d0                               ; +$003EE: 068000000040
    movea.l d0,a1                                      ; +$003F4: 2240
    move.l (a2),d0                                     ; +$003F6: 2012
