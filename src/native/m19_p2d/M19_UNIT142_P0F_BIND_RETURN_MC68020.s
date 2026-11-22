; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P0f source-owned segment $003FC..$004AE, emitter-exact MC68020.
; P0f whole code-and-markers SHA256 fa7d64ce347c08d0e523d5d31ac8a3e3b5175fdd38867bca76c6d7941aa9f2b4
UNIT142_P0F_BIND_RETURN_EDIT equ 0

    tst.l d3                                           ; +$003FC: 4A83
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$003FE: 6700009E
    move.l (a2),d0                                     ; +$00402: 2012
    subq.l #1,d0                                       ; +$00404: 5380
    mulu.w #$0010,d0                                   ; +$00406: C0FC0010
    lea 162(pc),a1                                     ; +$0040A: 43FA00A2
    adda.l d0,a1                                       ; +$0040E: D3C0
    move.l 64(a2),d0                                   ; +$00410: 202A0040
    bsr.w ENTRY_P0F_IDENTITY_CODE_0000E                ; +$00414: 6100FBF8
    tst.l d3                                           ; +$00418: 4A83
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$0041A: 67000082
    movea.l 20(a2),a1                                  ; +$0041E: 226A0014
    move.l 64(a2),d0                                   ; +$00422: 202A0040
    move.l d0,(a1)+                                    ; +$00426: 22C0
    move.l 68(a2),d0                                   ; +$00428: 202A0044
    move.l d0,(a1)+                                    ; +$0042C: 22C0
    move.l 72(a2),d0                                   ; +$0042E: 202A0048
    move.l d0,(a1)+                                    ; +$00432: 22C0
    move.l 76(a2),d0                                   ; +$00434: 202A004C
    move.l d0,(a1)+                                    ; +$00438: 22C0
    move.l 80(a2),d0                                   ; +$0043A: 202A0050
    move.l d0,(a1)+                                    ; +$0043E: 22C0
    move.l 84(a2),d0                                   ; +$00440: 202A0054
    move.l d0,(a1)+                                    ; +$00444: 22C0
    move.l #$00000001,24(a2)                           ; +$00446: 257C000000010018
    bra.w L_P0F_IDENTITY_CODE_0049E                    ; +$0044E: 6000004E
ENTRY_P0F_IDENTITY_CODE_00452:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00452: 48E7EFEE
    lea -160(a7),a7                                    ; +$00456: 4FEFFF60
    movea.l a7,a2                                      ; +$0045A: 244F
    move.l d0,(a2)                                     ; +$0045C: 2480
    move.l a5,28(a2)                                   ; +$0045E: 254D001C
    move.l #$00000000,24(a2)                           ; +$00462: 257C000000000018
    move.l 28(a2),d0                                   ; +$0046A: 202A001C
    tst.l d0                                           ; +$0046E: 4A80
    beq.w L_P0F_IDENTITY_CODE_0049E                    ; +$00470: 6700002C
    andi.l #$00000001,d0                               ; +$00474: 028000000001
    bne.w L_P0F_IDENTITY_CODE_0049E                    ; +$0047A: 66000022
    lea 46(pc),a0                                      ; +$0047E: 41FA002E
    move.l #$00000000,d0                               ; +$00482: 203C00000000
    move.l #$00000100,d1                               ; +$00488: 223C00000100
L_P0F_IDENTITY_CODE_0048E:
    move.l d0,(a0)+                                    ; +$0048E: 20C0
    subq.l #1,d1                                       ; +$00490: 5381
    bne.w L_P0F_IDENTITY_CODE_0048E                    ; +$00492: 6600FFFA
    move.l #$00000001,24(a2)                           ; +$00496: 257C000000010018
L_P0F_IDENTITY_CODE_0049E:
    move.l 24(a2),d3                                   ; +$0049E: 262A0018
    lea 160(a7),a7                                     ; +$004A2: 4FEF00A0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$004A6: 4CDF77F7
    moveq #UNIT142_P0F_BIND_RETURN_EDIT,d2                                        ; +$004AA: 7400
    rts                                                ; +$004AC: 4E75
