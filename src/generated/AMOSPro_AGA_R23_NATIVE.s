; AMOS Professional 365 - AGA extension native 68000 source restoration
; Generated from the actual AP20/HUNK image, NOT the historical M1 source.
; All recognized executable instructions are real Motorola mnemonics.
; Remaining dc.b/dcb.b encode strings, state/data, AMOS Rjsr markers,
; or code that cannot be safely identified. They are never silently lost.
; A native assembler comparison is REQUIRED before treating this file
; as byte-identical or using it as the replacement build authority.
; SHA256 original: 899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23
; Build: AMOSPro AGA M8 IDCMP Mouse R23 0.8.7 | $VER: AMOSPro_AGA 0.8.7 |  |
; Syntax target: vasm mot / Genam-style source (68020-capable).

    cpu 68020

AGA_StatePtr equ $01C8
AGA_Width equ 12
AGA_Height equ 16
AGA_Window equ 36
WD_LeftEdge equ 4
WD_TopEdge equ 6
WD_MouseY equ 12
WD_MouseX equ 14
WD_Screen equ 46

; Standalone binary HUNK wrapper: -Fbin, NOT -Fhunk
HUNK_HEADER:
    dc.l $000003F3,0,1,0,0
    dc.l (HUNK_DATA_END-HUNK_DATA)/4
    dc.l $000003E9
    dc.l (HUNK_DATA_END-HUNK_DATA)/4
HUNK_DATA:
    dc.l C_Tk-C_Off,C_Lib-C_Tk,C_Title-C_Lib,C_End-C_Title
    dc.w 0
    dc.b "AP20"
C_Off:
    ; Entry sizes in WORDS (not offsets). The last marker is an end label.
    dc.w (Entry_01-Entry_00)/2
    dc.w (Entry_02-Entry_01)/2
    dc.w (Entry_03-Entry_02)/2
    dc.w (Entry_04-Entry_03)/2
    dc.w (Entry_05-Entry_04)/2
    dc.w (Entry_06-Entry_05)/2
    dc.w (Entry_07-Entry_06)/2
    dc.w (Entry_08-Entry_07)/2
    dc.w (Entry_09-Entry_08)/2
    dc.w (Entry_10-Entry_09)/2
    dc.w (Entry_11-Entry_10)/2
    dc.w (Entry_12-Entry_11)/2
    dc.w (Entry_13-Entry_12)/2
    dc.w (Entry_14-Entry_13)/2
    dc.w (Entry_15-Entry_14)/2
    dc.w (Entry_16-Entry_15)/2
    dc.w (Entry_17-Entry_16)/2
    dc.w (Entry_18-Entry_17)/2
    dc.w (Entry_19-Entry_18)/2
    dc.w (Entry_20-Entry_19)/2
    dc.w (Entry_21-Entry_20)/2
    dc.w (Entry_22-Entry_21)/2
    dc.w (Entry_23-Entry_22)/2
    dc.w (Entry_24-Entry_23)/2
    dc.w (Entry_25-Entry_24)/2
    dc.w (Entry_26-Entry_25)/2
    dc.w (Entry_27-Entry_26)/2
    dc.w (Entry_28-Entry_27)/2
    dc.w (Entry_29-Entry_28)/2
    dc.w (Entry_30-Entry_29)/2
    dc.w (Entry_31-Entry_30)/2
    dc.w (Entry_32-Entry_31)/2
    dc.w (Entry_33-Entry_32)/2
    dc.w (Entry_34-Entry_33)/2
C_Tk:
    ; AP20 token table: pointers are AP20 entry indices, not addresses
Tk_00:  ; <dummy> : 
    dc.w 1,0
    dc.b $80,$FF
Tk_01:  ; aga probe : I
    dc.w 3,1
    dc.b "aga prob","e"+$80,"I",$FF,0
Tk_02:  ; aga detect : 0
    dc.w 1,4
    dc.b "aga detec","t"+$80,"0",$FF
Tk_03:  ; aga demo : 0
    dc.w 1,5
    dc.b "aga dem","o"+$80,"0",$FF
Tk_04:  ; aga screen open : 00,0,0,0
    dc.w 1,6
    dc.b "aga screen ope","n"+$80,"00,0,0,0",$FF
Tk_05:  ; aga screen pattern : I
    dc.w 7,1
    dc.b "aga screen patter","n"+$80,"I",$FF
Tk_06:  ; aga screen close : I
    dc.w 8,1
    dc.b "aga screen clos","e"+$80,"I",$FF
Tk_07:  ; aga wait vbl : I
    dc.w 9,1
    dc.b "aga wait vb","l"+$80,"I",$FF
Tk_08:  ; aga double buffer : 0
    dc.w 1,10
    dc.b "aga double buffe","r"+$80,"0",$FF,0
Tk_09:  ; aga swap : 0
    dc.w 1,11
    dc.b "aga swa","p"+$80,"0",$FF
Tk_10:  ; aga back fill : I0
    dc.w 12,1
    dc.b "aga back fil","l"+$80,"I0",$FF
Tk_11:  ; aga iff load : 02
    dc.w 1,13
    dc.b "aga iff loa","d"+$80,"02",$FF,0
Tk_12:  ; aga pic info : 02,0
    dc.w 1,14
    dc.b "aga pic inf","o"+$80,"02,0",$FF,0
Tk_13:  ; aga key : 0
    dc.w 1,17
    dc.b "aga ke","y"+$80,"0",$FF,0
Tk_14:  ; aga wait key : 0
    dc.w 1,18
    dc.b "aga wait ke","y"+$80,"0",$FF
Tk_15:  ; aga blit copy : 00,0,0,0,0,0
    dc.w 1,19
    dc.b "aga blit cop","y"+$80,"00,0,0,0,0,0",$FF
Tk_16:  ; aga blit fill : 00,0,0,0,0
    dc.w 1,20
    dc.b "aga blit fil","l"+$80,"00,0,0,0,0",$FF
Tk_17:  ; aga blit clear : 00,0,0,0
    dc.w 1,21
    dc.b "aga blit clea","r"+$80,"00,0,0,0",$FF,0
Tk_18:  ; aga copper clear : 0
    dc.w 1,22
    dc.b "aga copper clea","r"+$80,"0",$FF
Tk_19:  ; aga copper on : 0
    dc.w 1,23
    dc.b "aga copper o","n"+$80,"0",$FF,0
Tk_20:  ; aga copper off : 0
    dc.w 1,24
    dc.b "aga copper of","f"+$80,"0",$FF
Tk_21:  ; aga copper wait : 00,0
    dc.w 1,25
    dc.b "aga copper wai","t"+$80,"00,0",$FF
Tk_22:  ; aga copper move : 00,0
    dc.w 1,26
    dc.b "aga copper mov","e"+$80,"00,0",$FF
Tk_23:  ; aga copper end : 0
    dc.w 1,27
    dc.b "aga copper en","d"+$80,"0",$FF
Tk_24:  ; aga mouse x : 0
    dc.w 1,28
    dc.b "aga mouse ","x"+$80,"0",$FF,0
Tk_25:  ; aga mouse y : 0
    dc.w 1,29
    dc.b "aga mouse ","y"+$80,"0",$FF,0
Tk_26:  ; aga mouse buttons : 0
    dc.w 1,30
    dc.b "aga mouse button","s"+$80,"0",$FF,0
Tk_27:  ; aga mouse pressed : 0
    dc.w 1,31
    dc.b "aga mouse presse","d"+$80,"0",$FF,0
Tk_28:  ; aga mouse released : 0
    dc.w 1,32
    dc.b "aga mouse release","d"+$80,"0",$FF
    dc.b $00,$00,$00,$00,$00,$00

C_Lib:

; -------- AP20 entry 00 : private/reserved --------
Entry_00:
Internal_00:
    cmp.l #$41506578,d1                               ; +$0000 : B2BC41506578
    bne.w L_00030A                                    ; +$0006 : 6600002A
    lea L_000478(pc),a0                               ; +$000A : 41FA0194
    move.l a0,456(a5)                                 ; +$000E : 2B4801C8
    lea L_000310(pc),a0                               ; +$0012 : 41FA0024
    move.l a0,460(a5)                                 ; +$0016 : 2B4801CC
    move.l a0,464(a5)                                 ; +$001A : 2B4801D0
    lea L_000478(pc),a0                               ; +$001E : 41FA0180
    moveq #9,d0                                       ; +$0022 : 7009
L_0002FC:
    clr.l (a0)+                                       ; +$0024 : 4298
    dbra d0,L_0002FC                                  ; +$0026 : 51C8FFFC
    moveq #13,d0                                      ; +$002A : 700D
    move.w #$0200,d1                                  ; +$002C : 323C0200
    rts                                               ; +$0030 : 4E75
L_00030A:
    moveq #-1,d0                                      ; +$0032 : 70FF
    suba.l a0,a0                                      ; +$0034 : 91C8
    rts                                               ; +$0036 : 4E75
L_000310:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0038 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$003C : 246D01C8
    bra.w L_0004A0                                    ; +$0040 : 60000186
L_00031C:
    move.l a4,d0                                      ; +$0044 : 200C
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_0003D2                                    ; +$0048 : 670000B0
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_000334                                    ; +$0054 : 67000006
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
L_000334:
    move.l 20(a4),d0                                  ; +$005C : 202C0014
    tst.l d0                                          ; +$0060 : 4A80
    bra.w L_000376                                    ; +$0062 : 6000003A
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    movea.l $0004.w,a6                                ; +$006A : 2C780004
    nop                                               ; +$006E : 4E71
    nop                                               ; +$0070 : 4E71
    movea.l 12(a4),a0                                 ; +$0072 : 206C000C
    jsr -372(a6)                                      ; +$0076 : 4EAEFE8C
    tst.l d0                                          ; +$007A : 4A80
    beq.w L_000376                                    ; +$007C : 67000020
    movea.l 16(a4),a0                                 ; +$0080 : 206C0010
    movea.l $0004.w,a6                                ; +$0084 : 2C780004
    nop                                               ; +$0088 : 4E71
    nop                                               ; +$008A : 4E71
    movea.l 16(a4),a0                                 ; +$008C : 206C0010
    jsr -372(a6)                                      ; +$0090 : 4EAEFE8C
    tst.l d0                                          ; +$0094 : 4A80
    beq.w L_000376                                    ; +$0096 : 67000006
    clr.l 20(a4)                                      ; +$009A : 42AC0014
L_000376:
    movea.l (a2),a0                                   ; +$009E : 2052
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_0003A4                                    ; +$00A4 : 67000026
    movea.l 4(a2),a6                                  ; +$00A8 : 2C6A0004
    movea.l 4(a4),a1                                  ; +$00AC : 226C0004
    move.l a1,d0                                      ; +$00B0 : 2009
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_000394                                    ; +$00B4 : 67000006
    jsr -774(a6)                                      ; +$00B8 : 4EAEFCFA
L_000394:
    movea.l (a4),a1                                   ; +$00BC : 2254
    move.l a1,d0                                      ; +$00BE : 2009
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_0003A4                                    ; +$00C2 : 67000008
    movea.l (a2),a0                                   ; +$00C6 : 2052
    jsr -774(a6)                                      ; +$00C8 : 4EAEFCFA
L_0003A4:
    movea.l $0004.w,a6                                ; +$00CC : 2C780004
    movea.l 16(a4),a0                                 ; +$00D0 : 206C0010
    move.l a0,d0                                      ; +$00D4 : 2008
    tst.l d0                                          ; +$00D6 : 4A80
    beq.w L_0003B8                                    ; +$00D8 : 67000006
    jsr -672(a6)                                      ; +$00DC : 4EAEFD60
L_0003B8:
    movea.l 12(a4),a0                                 ; +$00E0 : 206C000C
    move.l a0,d0                                      ; +$00E4 : 2008
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_0003C8                                    ; +$00E8 : 67000006
    jsr -672(a6)                                      ; +$00EC : 4EAEFD60
L_0003C8:
    movea.l a4,a1                                     ; +$00F0 : 224C
    jsr -690(a6)                                      ; +$00F2 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$00F6 : 42AA0020
L_0003D2:
    tst.l (a2)                                        ; +$00FA : 4A92
    beq.w L_0003E4                                    ; +$00FC : 6700000E
    movea.l (a2),a0                                   ; +$0100 : 2052
    movea.l 4(a2),a6                                  ; +$0102 : 2C6A0004
    jsr -66(a6)                                       ; +$0106 : 4EAEFFBE
    clr.l (a2)                                        ; +$010A : 4292
L_0003E4:
    movea.l 8(a2),a1                                  ; +$010C : 226A0008
    move.l a1,d0                                      ; +$0110 : 2009
    tst.l d0                                          ; +$0112 : 4A80
    beq.w L_0003FC                                    ; +$0114 : 6700000E
    movea.l $0004.w,a6                                ; +$0118 : 2C780004
    jsr -414(a6)                                      ; +$011C : 4EAEFE62
    clr.l 8(a2)                                       ; +$0120 : 42AA0008
L_0003FC:
    movea.l 4(a2),a1                                  ; +$0124 : 226A0004
    move.l a1,d0                                      ; +$0128 : 2009
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_000414                                    ; +$012C : 6700000E
    movea.l $0004.w,a6                                ; +$0130 : 2C780004
    jsr -414(a6)                                      ; +$0134 : 4EAEFE62
    clr.l 4(a2)                                       ; +$0138 : 42AA0004
L_000414:
    lea 12(a2),a0                                     ; +$013C : 41EA000C
    moveq #4,d0                                       ; +$0140 : 7004
L_00041A:
    clr.l (a0)+                                       ; +$0142 : 4298
    dbra d0,L_00041A                                  ; +$0144 : 51C8FFFC
L_000420:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$0148 : 4CDF7FFF
    rts                                               ; +$014C : 4E75
L_000426:
    movea.l 36(a2),a3                                 ; +$014E : 266A0024
    move.l a3,d0                                      ; +$0152 : 200B
    tst.l d0                                          ; +$0154 : 4A80
    beq.w L_000472                                    ; +$0156 : 67000042
    movea.l 86(a3),a4                                 ; +$015A : 286B0056
    move.l a4,d0                                      ; +$015E : 200C
    tst.l d0                                          ; +$0160 : 4A80
    beq.w L_000458                                    ; +$0162 : 6700001C
L_00043E:
    movea.l a4,a0                                     ; +$0166 : 204C
    movea.l $0004.w,a6                                ; +$0168 : 2C780004
    jsr -372(a6)                                      ; +$016C : 4EAEFE8C
    tst.l d0                                          ; +$0170 : 4A80
    beq.w L_000458                                    ; +$0172 : 6700000C
    movea.l d0,a1                                     ; +$0176 : 2240
    jsr -378(a6)                                      ; +$0178 : 4EAEFE86
    bra.w L_00043E                                    ; +$017C : 6000FFE8
L_000458:
    movea.l 4(a2),a6                                  ; +$0180 : 2C6A0004
    move.l a6,d0                                      ; +$0184 : 200E
    tst.l d0                                          ; +$0186 : 4A80
    beq.w L_00046A                                    ; +$0188 : 67000008
    movea.l a3,a0                                     ; +$018C : 204B
    jsr -72(a6)                                       ; +$018E : 4EAEFFB8
L_00046A:
    move.l #$00000000,36(a2)                          ; +$0192 : 257C000000000024
L_000472:
    movea.l 32(a2),a4                                 ; +$019A : 286A0020
    rts                                               ; +$019E : 4E75
L_000478:
    dcb.b 40,0
L_0004A0:
    bsr.w L_0004B6                                    ; +$01C8 : 61000014
    tst.l d0                                          ; +$01CC : 4A80
    beq.w L_0004B2                                    ; +$01CE : 6700000A
    bsr.w L_000426                                    ; +$01D2 : 6100FF7A
    bra.w L_00031C                                    ; +$01D6 : 6000FE6C
L_0004B2:
    bra.w L_000420                                    ; +$01DA : 6000FF6C
L_0004B6:
    movea.l 32(a2),a4                                 ; +$01DE : 286A0020
    move.l a4,d0                                      ; +$01E2 : 200C
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_0004EE                                    ; +$01E6 : 6700002E
    moveq #0,d4                                       ; +$01EA : 7800
L_0004C4:
    bsr.w L_0004F6                                    ; +$01EC : 61000030
    tst.l d0                                          ; +$01F0 : 4A80
    beq.w L_0004EE                                    ; +$01F2 : 67000022
    addq.l #1,d4                                      ; +$01F6 : 5284
    cmpi.l #$0000012D,d4                              ; +$01F8 : 0C840000012D
    bge.w L_0004F2                                    ; +$01FE : 6C00001A
    movea.l 8(a2),a6                                  ; +$0202 : 2C6A0008
    move.l a6,d0                                      ; +$0206 : 200E
    tst.l d0                                          ; +$0208 : 4A80
    beq.w L_0004F2                                    ; +$020A : 6700000E
    jsr -270(a6)                                      ; +$020E : 4EAEFEF2
    bra.w L_0004C4                                    ; +$0212 : 6000FFD8
L_0004EE:
    moveq #1,d0                                       ; +$0216 : 7001
    rts                                               ; +$0218 : 4E75
L_0004F2:
    moveq #0,d0                                       ; +$021A : 7000
    rts                                               ; +$021C : 4E75
L_0004F6:
    move.l 20(a4),d6                                  ; +$021E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0222 : 028600000003
    btst #0,d6                                        ; +$0228 : 08060000
    beq.w L_000526                                    ; +$022C : 67000020
    movea.l 12(a4),a0                                 ; +$0230 : 206C000C
    move.l a0,d0                                      ; +$0234 : 2008
    tst.l d0                                          ; +$0236 : 4A80
    beq.w L_000526                                    ; +$0238 : 67000014
    movea.l $0004.w,a6                                ; +$023C : 2C780004
    jsr -372(a6)                                      ; +$0240 : 4EAEFE8C
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_000526                                    ; +$0246 : 67000006
    bclr #0,d6                                        ; +$024A : 08860000
L_000526:
    btst #1,d6                                        ; +$024E : 08060001
    beq.w L_00054C                                    ; +$0252 : 67000020
    movea.l 16(a4),a0                                 ; +$0256 : 206C0010
    move.l a0,d0                                      ; +$025A : 2008
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_00054C                                    ; +$025E : 67000014
    movea.l $0004.w,a6                                ; +$0262 : 2C780004
    jsr -372(a6)                                      ; +$0266 : 4EAEFE8C
    tst.l d0                                          ; +$026A : 4A80
    beq.w L_00054C                                    ; +$026C : 67000006
    bclr #1,d6                                        ; +$0270 : 08860001
L_00054C:
    move.l d6,20(a4)                                  ; +$0274 : 29460014
    move.l d6,d0                                      ; +$0278 : 2006
    rts                                               ; +$027A : 4E75

; -------- AP20 entry 01 : private/reserved --------
Entry_01:
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 02 : private/reserved --------
Entry_02:
Internal_02:
    rts                                               ; +$0000 : 4E75
    movea.l -4(a5),a0                                 ; +$0002 : 206DFFFC
    jsr 400(a0)                                       ; +$0006 : 4EA80190
    rts                                               ; +$000A : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 03 : aga probe --------
Entry_03:
Aga_Probe:
    rts                                               ; +$0000 : 4E75
    movea.l -4(a5),a0                                 ; +$0002 : 206DFFFC
    jsr 400(a0)                                       ; +$0006 : 4EA80190
    rts                                               ; +$000A : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 04 : aga detect --------
Entry_04:
Aga_Detect:
    move.l d0,-(a7)                                   ; +$0000 : 2F00
    move.l d1,-(a7)                                   ; +$0002 : 2F01
    move.l a0,-(a7)                                   ; +$0004 : 2F08
    move.l a1,-(a7)                                   ; +$0006 : 2F09
    move.l a6,-(a7)                                   ; +$0008 : 2F0E
    moveq #0,d3                                       ; +$000A : 7600
    movea.l $0004.w,a6                                ; +$000C : 2C780004
    btst #1,297(a6)                                   ; +$0010 : 082E00010129
    beq.s L_0005B4                                    ; +$0016 : 6724
    lea L_0005C2(pc),a1                               ; +$0018 : 43FA0030
    moveq #39,d0                                      ; +$001C : 7027
    jsr -552(a6)                                      ; +$001E : 4EAEFDD8
    tst.l d0                                          ; +$0022 : 4A80
    beq.s L_0005B4                                    ; +$0024 : 6716
    movea.l d0,a1                                     ; +$0026 : 2240
    move.b 236(a1),d1                                 ; +$0028 : 122900EC
    andi.b #$0C,d1                                    ; +$002C : 0201000C
    cmpi.b #$0C,d1                                    ; +$0030 : 0C01000C
    bne.s L_0005B0                                    ; +$0034 : 6602
    moveq #1,d3                                       ; +$0036 : 7601
L_0005B0:
    jsr -414(a6)                                      ; +$0038 : 4EAEFE62
L_0005B4:
    movea.l (a7)+,a6                                  ; +$003C : 2C5F
    movea.l (a7)+,a1                                  ; +$003E : 225F
    movea.l (a7)+,a0                                  ; +$0040 : 205F
    move.l (a7)+,d1                                   ; +$0042 : 221F
    move.l (a7)+,d0                                   ; +$0044 : 201F
    moveq #0,d2                                       ; +$0046 : 7400
    rts                                               ; +$0048 : 4E75
L_0005C2:
    dc.b "graphics.library"
    dc.b $00,$00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 05 : aga demo --------
Entry_05:
Aga_Demo:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7CFFE
    moveq #0,d3                                       ; +$0004 : 7600
    movea.l $0004.w,a6                                ; +$0006 : 2C780004
    btst #1,297(a6)                                   ; +$000A : 082E00010129
    beq.w L_0006F6                                    ; +$0010 : 6700010C
    lea L_0006FE(pc),a1                               ; +$0014 : 43FA0110
    moveq #39,d0                                      ; +$0018 : 7027
    jsr -552(a6)                                      ; +$001A : 4EAEFDD8
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_0006F6                                    ; +$0020 : 670000FC
    movea.l d0,a4                                     ; +$0024 : 2840
    movea.l $0004.w,a6                                ; +$0026 : 2C780004
    lea L_000710(pc),a1                               ; +$002A : 43FA010C
    moveq #39,d0                                      ; +$002E : 7027
    jsr -552(a6)                                      ; +$0030 : 4EAEFDD8
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_0006EC                                    ; +$0036 : 670000DC
    movea.l d0,a5                                     ; +$003A : 2A40
    move.b 236(a5),d0                                 ; +$003C : 102D00EC
    andi.b #$0C,d0                                    ; +$0040 : 0200000C
    cmpi.b #$0C,d0                                    ; +$0044 : 0C00000C
    bne.w L_0006E2                                    ; +$0048 : 660000C0
    lea -40(a7),a7                                    ; +$004C : 4FEFFFD8
    movea.l a7,a1                                     ; +$0050 : 224F
    move.l #$80000023,(a1)+                           ; +$0052 : 22FC80000023
    move.l #$00000140,(a1)+                           ; +$0058 : 22FC00000140
    move.l #$80000024,(a1)+                           ; +$005E : 22FC80000024
    move.l #$00000100,(a1)+                           ; +$0064 : 22FC00000100
    move.l #$80000025,(a1)+                           ; +$006A : 22FC80000025
    move.l #$00000008,(a1)+                           ; +$0070 : 22FC00000008
    move.l #$80000032,(a1)+                           ; +$0076 : 22FC80000032
    move.l #$00021000,(a1)+                           ; +$007C : 22FC00021000
    moveq #0,d0                                       ; +$0082 : 7000
    move.l d0,(a1)+                                   ; +$0084 : 22C0
    move.l d0,(a1)+                                   ; +$0086 : 22C0
    suba.l a0,a0                                      ; +$0088 : 91C8
    movea.l a7,a1                                     ; +$008A : 224F
    movea.l a4,a6                                     ; +$008C : 2C4C
    jsr -612(a6)                                      ; +$008E : 4EAEFD9C
    lea 40(a7),a7                                     ; +$0092 : 4FEF0028
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_0006E2                                    ; +$0098 : 67000070
    movea.l d0,a3                                     ; +$009C : 2640
    moveq #0,d6                                       ; +$009E : 7C00
L_000678:
    move.l d6,d0                                      ; +$00A0 : 2006
    move.l d6,d1                                      ; +$00A2 : 2206
    lsl.l #8,d1                                       ; +$00A4 : E189
    swap d1                                           ; +$00A6 : 4841
    move.l #$000000FF,d2                              ; +$00A8 : 243C000000FF
    sub.l d6,d2                                       ; +$00AE : 9486
    lsl.l #8,d2                                       ; +$00B0 : E18A
    swap d2                                           ; +$00B2 : 4842
    move.l #$30000000,d3                              ; +$00B4 : 263C30000000
    lea 44(a3),a0                                     ; +$00BA : 41EB002C
    movea.l a5,a6                                     ; +$00BE : 2C4D
    jsr -852(a6)                                      ; +$00C0 : 4EAEFCAC
    move.l d6,d0                                      ; +$00C4 : 2006
    lea 84(a3),a1                                     ; +$00C6 : 43EB0054
    jsr -342(a6)                                      ; +$00CA : 4EAEFEAA
    moveq #0,d0                                       ; +$00CE : 7000
    move.l d6,d1                                      ; +$00D0 : 2206
    move.l #$0000013F,d2                              ; +$00D2 : 243C0000013F
    move.l d6,d3                                      ; +$00D8 : 2606
    lea 84(a3),a1                                     ; +$00DA : 43EB0054
    jsr -306(a6)                                      ; +$00DE : 4EAEFECE
    addq.l #1,d6                                      ; +$00E2 : 5286
    cmpi.l #$00000100,d6                              ; +$00E4 : 0C8600000100
    bne.w L_000678                                    ; +$00EA : 6600FFB4
    move.w #$0096,d7                                  ; +$00EE : 3E3C0096
L_0006CA:
    movea.l a5,a6                                     ; +$00F2 : 2C4D
    jsr -270(a6)                                      ; +$00F4 : 4EAEFEF2
    dbra d7,L_0006CA                                  ; +$00F8 : 51CFFFF8
    movea.l a3,a0                                     ; +$00FC : 204B
    movea.l a4,a6                                     ; +$00FE : 2C4C
    jsr -66(a6)                                       ; +$0100 : 4EAEFFBE
    moveq #1,d3                                       ; +$0104 : 7601
    bra.w L_0006E2                                    ; +$0106 : 60000002
L_0006E2:
    movea.l a5,a1                                     ; +$010A : 224D
    movea.l $0004.w,a6                                ; +$010C : 2C780004
    jsr -414(a6)                                      ; +$0110 : 4EAEFE62
L_0006EC:
    movea.l a4,a1                                     ; +$0114 : 224C
    movea.l $0004.w,a6                                ; +$0116 : 2C780004
    jsr -414(a6)                                      ; +$011A : 4EAEFE62
L_0006F6:
    movem.l (a7)+,d0-d1/d4-d7/a0-a6                   ; +$011E : 4CDF7FF3
    moveq #0,d2                                       ; +$0122 : 7400
    rts                                               ; +$0124 : 4E75
L_0006FE:
    dc.b "intuition.library"
    dc.b $00
L_000710:
    dc.b "graphics.library"
    dc.b $00,$00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 06 : aga screen open --------
Entry_06:
Aga_Screen_Open:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7CFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l (a3)+,d4                                   ; +$000A : 281B
    moveq #0,d3                                       ; +$000C : 7600
    movea.l 456(a5),a2                                ; +$000E : 246D01C8
    move.l a2,d0                                      ; +$0012 : 200A
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_000882                                    ; +$0016 : 67000144
    tst.l (a2)                                        ; +$001A : 4A92
    bne.w L_000882                                    ; +$001C : 6600013E
    cmpi.l #$00000001,d4                              ; +$0020 : 0C8400000001
    bcs.w L_000882                                    ; +$0026 : 65000134
    cmpi.l #$00007FFF,d4                              ; +$002A : 0C8400007FFF
    bhi.w L_000882                                    ; +$0030 : 6200012A
    move.l d4,d0                                      ; +$0034 : 2004
    andi.l #$00000000,d0                              ; +$0036 : 028000000000
    nop                                               ; +$003C : 4E71
    nop                                               ; +$003E : 4E71
    cmpi.l #$00000001,d5                              ; +$0040 : 0C8500000001
    bcs.w L_000882                                    ; +$0046 : 65000114
    cmpi.l #$00007FFF,d5                              ; +$004A : 0C8500007FFF
    bhi.w L_000882                                    ; +$0050 : 6200010A
    cmpi.l #$00000002,d6                              ; +$0054 : 0C8600000002
    bcs.w L_000882                                    ; +$005A : 65000100
    cmpi.l #$00000100,d6                              ; +$005E : 0C8600000100
    bhi.w L_000882                                    ; +$0064 : 620000F6
    move.l d6,d1                                      ; +$0068 : 2206
    subq.l #1,d1                                      ; +$006A : 5381
    and.l d6,d1                                       ; +$006C : C286
    bne.w L_000882                                    ; +$006E : 660000EC
    move.l d7,d0                                      ; +$0072 : 2007
    andi.l #$00000400,d0                              ; +$0074 : 028000000400
    bne.w L_000882                                    ; +$007A : 660000E0
    movea.l $0004.w,a6                                ; +$007E : 2C780004
    btst #1,297(a6)                                   ; +$0082 : 082E00010129
    beq.w L_000882                                    ; +$0088 : 670000D2
    lea L_00088A(pc),a1                               ; +$008C : 43FA00D6
    moveq #39,d0                                      ; +$0090 : 7027
    jsr -552(a6)                                      ; +$0092 : 4EAEFDD8
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_000882                                    ; +$0098 : 670000C2
    movea.l d0,a4                                     ; +$009C : 2840
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    lea L_00089C(pc),a1                               ; +$00A2 : 43FA00D2
    moveq #39,d0                                      ; +$00A6 : 7027
    jsr -552(a6)                                      ; +$00A8 : 4EAEFDD8
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_000878                                    ; +$00AE : 670000A2
    movea.l d0,a5                                     ; +$00B2 : 2A40
    move.b 236(a5),d0                                 ; +$00B4 : 102D00EC
    andi.b #$0C,d0                                    ; +$00B8 : 0200000C
    cmpi.b #$0C,d0                                    ; +$00BC : 0C00000C
    bne.w L_00086A                                    ; +$00C0 : 66000082
    move.l d6,d1                                      ; +$00C4 : 2206
    moveq #0,d0                                       ; +$00C6 : 7000
L_0007EE:
    lsr.l #1,d1                                       ; +$00C8 : E289
    addq.l #1,d0                                      ; +$00CA : 5280
    cmpi.l #$00000001,d1                              ; +$00CC : 0C8100000001
    bne.w L_0007EE                                    ; +$00D2 : 6600FFF4
    move.l d0,28(a2)                                  ; +$00D6 : 2540001C
    lea -60(a7),a7                                    ; +$00DA : 4FEFFFC4
    movea.l a7,a1                                     ; +$00DE : 224F
    move.l #$80000023,(a1)+                           ; +$00E0 : 22FC80000023
    move.l d4,(a1)+                                   ; +$00E6 : 22C4
    move.l #$80000024,(a1)+                           ; +$00E8 : 22FC80000024
    move.l d5,(a1)+                                   ; +$00EE : 22C5
    move.l #$80000025,(a1)+                           ; +$00F0 : 22FC80000025
    move.l d0,(a1)+                                   ; +$00F6 : 22C0
    move.l #$80000032,(a1)+                           ; +$00F8 : 22FC80000032
    move.l d7,(a1)+                                   ; +$00FE : 22C7
    move.l #$8000003B,(a1)+                           ; +$0100 : 22FC8000003B
    moveq #1,d0                                       ; +$0106 : 7001
    move.l d0,(a1)+                                   ; +$0108 : 22C0
    bsr.w L_0008AE                                    ; +$010A : 6100007C
    nop                                               ; +$010E : 4E71
    suba.l a0,a0                                      ; +$0110 : 91C8
    movea.l a7,a1                                     ; +$0112 : 224F
    movea.l a4,a6                                     ; +$0114 : 2C4C
    bsr.w L_0009B2                                    ; +$0116 : 61000174
    lea 60(a7),a7                                     ; +$011A : 4FEF003C
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_00086A                                    ; +$0120 : 67000022
    move.l d0,(a2)                                    ; +$0124 : 2480
    move.l a4,4(a2)                                   ; +$0126 : 254C0004
    move.l a5,8(a2)                                   ; +$012A : 254D0008
    move.l d4,12(a2)                                  ; +$012E : 2544000C
    move.l d5,16(a2)                                  ; +$0132 : 25450010
    move.l d6,20(a2)                                  ; +$0136 : 25460014
    bsr.w L_000A04                                    ; +$013A : 610001A2
    bra.w L_000882                                    ; +$013E : 6000001C
    nop                                               ; +$0142 : 4E71
L_00086A:
    clr.l 28(a2)                                      ; +$0144 : 42AA001C
    movea.l a5,a1                                     ; +$0148 : 224D
    movea.l $0004.w,a6                                ; +$014A : 2C780004
    jsr -414(a6)                                      ; +$014E : 4EAEFE62
L_000878:
    movea.l a4,a1                                     ; +$0152 : 224C
    movea.l $0004.w,a6                                ; +$0154 : 2C780004
    jsr -414(a6)                                      ; +$0158 : 4EAEFE62
L_000882:
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6             ; +$015C : 4CDF77F3
    moveq #0,d2                                       ; +$0160 : 7400
    rts                                               ; +$0162 : 4E75
L_00088A:
    dc.b "intuition.library"
    dc.b $00
L_00089C:
    dc.b "graphics.library"
    dc.b $00,$00
L_0008AE:
    move.l #$80000039,(a1)+                           ; +$0188 : 22FC80000039
    moveq #1,d0                                       ; +$018E : 7001
    move.l d0,(a1)+                                   ; +$0190 : 22C0
    moveq #0,d0                                       ; +$0192 : 7000
    move.l d0,(a1)+                                   ; +$0194 : 22C0
    move.l d0,(a1)+                                   ; +$0196 : 22C0
    rts                                               ; +$0198 : 4E75
L_0008C0:
    move.l d7,24(a2)                                  ; +$019A : 25470018
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$019E : 48E7EFFE
    lea -48(a7),a7                                    ; +$01A2 : 4FEFFFD0
    moveq #0,d0                                       ; +$01A6 : 7000
    move.l d0,(a7)                                    ; +$01A8 : 2E80
    move.l d0,4(a7)                                   ; +$01AA : 2F400004
    move.l d0,8(a7)                                   ; +$01AE : 2F400008
    move.l d0,12(a7)                                  ; +$01B2 : 2F40000C
    move.l d0,16(a7)                                  ; +$01B6 : 2F400010
    move.l d0,20(a7)                                  ; +$01BA : 2F400014
    move.l d0,24(a7)                                  ; +$01BE : 2F400018
    move.l d0,28(a7)                                  ; +$01C2 : 2F40001C
    move.l d0,32(a7)                                  ; +$01C6 : 2F400020
    move.l d0,36(a7)                                  ; +$01CA : 2F400024
    move.l d0,40(a7)                                  ; +$01CE : 2F400028
    move.l d0,44(a7)                                  ; +$01D2 : 2F40002C
    move.l 12(a2),d0                                  ; +$01D6 : 202A000C
    move.w d0,4(a7)                                   ; +$01DA : 3F400004
    move.l 16(a2),d0                                  ; +$01DE : 202A0010
    move.w d0,6(a7)                                   ; +$01E2 : 3F400006
    move.l #$000C0408,10(a7)                          ; +$01E6 : 2F7C000C0408000A
    move.l #$00031900,14(a7)                          ; +$01EE : 2F7C00031900000E
    move.l (a2),d0                                    ; +$01F6 : 2012
    move.l d0,30(a7)                                  ; +$01F8 : 2F40001E
    move.w #$000F,46(a7)                              ; +$01FC : 3F7C000F002E
    movea.l a7,a0                                     ; +$0202 : 204F
    movea.l 4(a2),a6                                  ; +$0204 : 2C6A0004
    jsr -204(a6)                                      ; +$0208 : 4EAEFF34
    move.l d0,d1                                      ; +$020C : 2200
    lea 48(a7),a7                                     ; +$020E : 4FEF0030
    tst.l d1                                          ; +$0212 : 4A81
    beq.w L_000948                                    ; +$0214 : 6700000C
    move.l d1,36(a2)                                  ; +$0218 : 25410024
    moveq #1,d3                                       ; +$021C : 7601
    bra.w L_0009AC                                    ; +$021E : 60000066
L_000948:
    movea.l (a2),a0                                   ; +$0222 : 2052
    move.l a0,d0                                      ; +$0224 : 2008
    tst.l d0                                          ; +$0226 : 4A80
    beq.w L_00095A                                    ; +$0228 : 6700000A
    movea.l 4(a2),a6                                  ; +$022C : 2C6A0004
    jsr -66(a6)                                       ; +$0230 : 4EAEFFBE
L_00095A:
    movea.l 8(a2),a1                                  ; +$0234 : 226A0008
    move.l a1,d0                                      ; +$0238 : 2009
    tst.l d0                                          ; +$023A : 4A80
    beq.w L_00096E                                    ; +$023C : 6700000A
    movea.l $0004.w,a6                                ; +$0240 : 2C780004
    jsr -414(a6)                                      ; +$0244 : 4EAEFE62
L_00096E:
    movea.l 4(a2),a1                                  ; +$0248 : 226A0004
    move.l a1,d0                                      ; +$024C : 2009
    tst.l d0                                          ; +$024E : 4A80
    beq.w L_000982                                    ; +$0250 : 6700000A
    movea.l $0004.w,a6                                ; +$0254 : 2C780004
    jsr -414(a6)                                      ; +$0258 : 4EAEFE62
L_000982:
    moveq #0,d0                                       ; +$025C : 7000
    move.l d0,(a2)                                    ; +$025E : 2480
    move.l d0,4(a2)                                   ; +$0260 : 25400004
    move.l d0,8(a2)                                   ; +$0264 : 25400008
    move.l d0,12(a2)                                  ; +$0268 : 2540000C
    move.l d0,16(a2)                                  ; +$026C : 25400010
    move.l d0,20(a2)                                  ; +$0270 : 25400014
    move.l d0,24(a2)                                  ; +$0274 : 25400018
    move.l d0,28(a2)                                  ; +$0278 : 2540001C
    move.l d0,32(a2)                                  ; +$027C : 25400020
    move.l d0,36(a2)                                  ; +$0280 : 25400024
    moveq #0,d3                                       ; +$0284 : 7600
L_0009AC:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0286 : 4CDF7FF7
    rts                                               ; +$028A : 4E75
L_0009B2:
    move.l a1,d2                                      ; +$028C : 2409
    jsr -612(a6)                                      ; +$028E : 4EAEFD9C
    tst.l d0                                          ; +$0292 : 4A80
    bne.w L_0009FE                                    ; +$0294 : 66000042
    move.l d7,d1                                      ; +$0298 : 2207
    andi.l #$FFFF0000,d1                              ; +$029A : 0281FFFF0000
    cmpi.l #$00010000,d1                              ; +$02A0 : 0C8100010000
    bne.w L_0009FE                                    ; +$02A6 : 66000030
    move.l d7,d1                                      ; +$02AA : 2207
    addi.l #$00010000,d1                              ; +$02AC : 068100010000
    move.l a6,-(a7)                                   ; +$02B2 : 2F0E
    movea.l a5,a6                                     ; +$02B4 : 2C4D
    move.l d1,d0                                      ; +$02B6 : 2001
    jsr -798(a6)                                      ; +$02B8 : 4EAEFCE2
    movea.l (a7)+,a6                                  ; +$02BC : 2C5F
    tst.l d0                                          ; +$02BE : 4A80
    bne.w L_000A00                                    ; +$02C0 : 66000018
    move.l d7,d1                                      ; +$02C4 : 2207
    addi.l #$00010000,d1                              ; +$02C6 : 068100010000
    movea.l d2,a1                                     ; +$02CC : 2242
    move.l d1,28(a1)                                  ; +$02CE : 2341001C
    suba.l a0,a0                                      ; +$02D2 : 91C8
    jsr -612(a6)                                      ; +$02D4 : 4EAEFD9C
L_0009FE:
    rts                                               ; +$02D8 : 4E75
L_000A00:
    moveq #0,d0                                       ; +$02DA : 7000
    rts                                               ; +$02DC : 4E75
L_000A04:
    bsr.w L_0008C0                                    ; +$02DE : 6100FEBA
    lea 11732(a2),a0                                  ; +$02E2 : 41EA2DD4
    moveq #35,d0                                      ; +$02E6 : 7023
L_000A0E:
    clr.l (a0)+                                       ; +$02E8 : 4298
    dbra d0,L_000A0E                                  ; +$02EA : 51C8FFFC
    rts                                               ; +$02EE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 07 : aga screen pattern --------
Entry_07:
Aga_Screen_Pattern:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)                   ; +$0000 : 48E7FFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_000AA6                                    ; +$000C : 6700007E
    tst.l (a2)                                        ; +$0010 : 4A92
    beq.w L_000AA6                                    ; +$0012 : 67000078
    movea.l (a2),a4                                   ; +$0016 : 2852
    movea.l 8(a2),a6                                  ; +$0018 : 2C6A0008
    move.l 20(a2),d4                                  ; +$001C : 282A0014
    move.l 16(a2),d5                                  ; +$0020 : 2A2A0010
    moveq #0,d6                                       ; +$0024 : 7C00
L_000A40:
    move.l d6,d0                                      ; +$0026 : 2006
    mulu.w d4,d0                                      ; +$0028 : C0C4
    divu.w d5,d0                                      ; +$002A : 80C5
    andi.l #$0000FFFF,d0                              ; +$002C : 02800000FFFF
    move.l d0,d7                                      ; +$0032 : 2E00
    move.l d7,d1                                      ; +$0034 : 2207
    mulu.w #$00FF,d1                                  ; +$0036 : C2FC00FF
    move.l d4,d0                                      ; +$003A : 2004
    subq.l #1,d0                                      ; +$003C : 5380
    divu.w d0,d1                                      ; +$003E : 82C0
    andi.l #$0000FFFF,d1                              ; +$0040 : 02810000FFFF
    move.l #$000000FF,d2                              ; +$0046 : 243C000000FF
    sub.l d1,d2                                       ; +$004C : 9481
    lsl.l #8,d1                                       ; +$004E : E189
    swap d1                                           ; +$0050 : 4841
    lsl.l #8,d2                                       ; +$0052 : E18A
    swap d2                                           ; +$0054 : 4842
    move.l #$30000000,d3                              ; +$0056 : 263C30000000
    move.l d7,d0                                      ; +$005C : 2007
    lea 44(a4),a0                                     ; +$005E : 41EC002C
    jsr -852(a6)                                      ; +$0062 : 4EAEFCAC
    move.l d7,d0                                      ; +$0066 : 2007
    lea 84(a4),a1                                     ; +$0068 : 43EC0054
    jsr -342(a6)                                      ; +$006C : 4EAEFEAA
    moveq #0,d0                                       ; +$0070 : 7000
    move.l d6,d1                                      ; +$0072 : 2206
    move.l 12(a2),d2                                  ; +$0074 : 242A000C
    subq.l #1,d2                                      ; +$0078 : 5382
    move.l d6,d3                                      ; +$007A : 2606
    lea 84(a4),a1                                     ; +$007C : 43EC0054
    jsr -306(a6)                                      ; +$0080 : 4EAEFECE
    addq.l #1,d6                                      ; +$0084 : 5286
    cmp.l d5,d6                                       ; +$0086 : BC85
    bne.w L_000A40                                    ; +$0088 : 6600FF9C
L_000AA6:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6                   ; +$008C : 4CDF77FF
    rts                                               ; +$0090 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 08 : aga screen close --------
Entry_08:
Aga_Screen_Close:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0000 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    bra.w L_000BD6                                    ; +$0008 : 6000011C
L_000ABC:
    move.l a4,d0                                      ; +$000C : 200C
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_000B30                                    ; +$0010 : 6700006E
    movea.l 8(a2),a6                                  ; +$0014 : 2C6A0008
    move.l a6,d0                                      ; +$0018 : 200E
    tst.l d0                                          ; +$001A : 4A80
    beq.w L_000AD4                                    ; +$001C : 67000006
    jsr -228(a6)                                      ; +$0020 : 4EAEFF1C
L_000AD4:
    movea.l (a2),a0                                   ; +$0024 : 2052
    move.l a0,d0                                      ; +$0026 : 2008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_000B02                                    ; +$002A : 67000026
    movea.l 4(a2),a6                                  ; +$002E : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0032 : 226C0004
    move.l a1,d0                                      ; +$0036 : 2009
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_000AF2                                    ; +$003A : 67000006
    jsr -774(a6)                                      ; +$003E : 4EAEFCFA
L_000AF2:
    movea.l (a4),a1                                   ; +$0042 : 2254
    move.l a1,d0                                      ; +$0044 : 2009
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_000B02                                    ; +$0048 : 67000008
    movea.l (a2),a0                                   ; +$004C : 2052
    jsr -774(a6)                                      ; +$004E : 4EAEFCFA
L_000B02:
    movea.l $0004.w,a6                                ; +$0052 : 2C780004
    movea.l 16(a4),a0                                 ; +$0056 : 206C0010
    move.l a0,d0                                      ; +$005A : 2008
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_000B16                                    ; +$005E : 67000006
    jsr -672(a6)                                      ; +$0062 : 4EAEFD60
L_000B16:
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    move.l a0,d0                                      ; +$006A : 2008
    tst.l d0                                          ; +$006C : 4A80
    beq.w L_000B26                                    ; +$006E : 67000006
    jsr -672(a6)                                      ; +$0072 : 4EAEFD60
L_000B26:
    movea.l a4,a1                                     ; +$0076 : 224C
    jsr -690(a6)                                      ; +$0078 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$007C : 42AA0020
L_000B30:
    tst.l (a2)                                        ; +$0080 : 4A92
    beq.w L_000B42                                    ; +$0082 : 6700000E
    movea.l (a2),a0                                   ; +$0086 : 2052
    movea.l 4(a2),a6                                  ; +$0088 : 2C6A0004
    jsr -66(a6)                                       ; +$008C : 4EAEFFBE
    clr.l (a2)                                        ; +$0090 : 4292
L_000B42:
    movea.l 8(a2),a1                                  ; +$0092 : 226A0008
    move.l a1,d0                                      ; +$0096 : 2009
    tst.l d0                                          ; +$0098 : 4A80
    beq.w L_000B5A                                    ; +$009A : 6700000E
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    jsr -414(a6)                                      ; +$00A2 : 4EAEFE62
    clr.l 8(a2)                                       ; +$00A6 : 42AA0008
L_000B5A:
    movea.l 4(a2),a1                                  ; +$00AA : 226A0004
    move.l a1,d0                                      ; +$00AE : 2009
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_000B72                                    ; +$00B2 : 6700000E
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    jsr -414(a6)                                      ; +$00BA : 4EAEFE62
    clr.l 4(a2)                                       ; +$00BE : 42AA0004
L_000B72:
    lea 12(a2),a0                                     ; +$00C2 : 41EA000C
    moveq #4,d0                                       ; +$00C6 : 7004
L_000B78:
    clr.l (a0)+                                       ; +$00C8 : 4298
    dbra d0,L_000B78                                  ; +$00CA : 51C8FFFC
L_000B7E:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$00CE : 4CDF7FFF
    rts                                               ; +$00D2 : 4E75
L_000B84:
    movea.l 36(a2),a3                                 ; +$00D4 : 266A0024
    move.l a3,d0                                      ; +$00D8 : 200B
    tst.l d0                                          ; +$00DA : 4A80
    beq.w L_000BD0                                    ; +$00DC : 67000042
    movea.l 86(a3),a4                                 ; +$00E0 : 286B0056
    move.l a4,d0                                      ; +$00E4 : 200C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_000BB6                                    ; +$00E8 : 6700001C
L_000B9C:
    movea.l a4,a0                                     ; +$00EC : 204C
    movea.l $0004.w,a6                                ; +$00EE : 2C780004
    jsr -372(a6)                                      ; +$00F2 : 4EAEFE8C
    tst.l d0                                          ; +$00F6 : 4A80
    beq.w L_000BB6                                    ; +$00F8 : 6700000C
    movea.l d0,a1                                     ; +$00FC : 2240
    jsr -378(a6)                                      ; +$00FE : 4EAEFE86
    bra.w L_000B9C                                    ; +$0102 : 6000FFE8
L_000BB6:
    movea.l 4(a2),a6                                  ; +$0106 : 2C6A0004
    move.l a6,d0                                      ; +$010A : 200E
    tst.l d0                                          ; +$010C : 4A80
    beq.w L_000BC8                                    ; +$010E : 67000008
    movea.l a3,a0                                     ; +$0112 : 204B
    jsr -72(a6)                                       ; +$0114 : 4EAEFFB8
L_000BC8:
    move.l #$00000000,36(a2)                          ; +$0118 : 257C000000000024
L_000BD0:
    movea.l 32(a2),a4                                 ; +$0120 : 286A0020
    rts                                               ; +$0124 : 4E75
L_000BD6:
    bsr.w L_000BEC                                    ; +$0126 : 61000014
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_000BE8                                    ; +$012C : 6700000A
    bsr.w L_000B84                                    ; +$0130 : 6100FFA2
    bra.w L_000ABC                                    ; +$0134 : 6000FED6
L_000BE8:
    bra.w L_000B7E                                    ; +$0138 : 6000FF94
L_000BEC:
    movea.l 32(a2),a4                                 ; +$013C : 286A0020
    move.l a4,d0                                      ; +$0140 : 200C
    tst.l d0                                          ; +$0142 : 4A80
    beq.w L_000C24                                    ; +$0144 : 6700002E
    moveq #0,d4                                       ; +$0148 : 7800
L_000BFA:
    bsr.w L_000C2C                                    ; +$014A : 61000030
    tst.l d0                                          ; +$014E : 4A80
    beq.w L_000C24                                    ; +$0150 : 67000022
    addq.l #1,d4                                      ; +$0154 : 5284
    cmpi.l #$0000012D,d4                              ; +$0156 : 0C840000012D
    bge.w L_000C28                                    ; +$015C : 6C00001A
    movea.l 8(a2),a6                                  ; +$0160 : 2C6A0008
    move.l a6,d0                                      ; +$0164 : 200E
    tst.l d0                                          ; +$0166 : 4A80
    beq.w L_000C28                                    ; +$0168 : 6700000E
    jsr -270(a6)                                      ; +$016C : 4EAEFEF2
    bra.w L_000BFA                                    ; +$0170 : 6000FFD8
L_000C24:
    moveq #1,d0                                       ; +$0174 : 7001
    rts                                               ; +$0176 : 4E75
L_000C28:
    moveq #0,d0                                       ; +$0178 : 7000
    rts                                               ; +$017A : 4E75
L_000C2C:
    move.l 20(a4),d6                                  ; +$017C : 2C2C0014
    andi.l #$00000003,d6                              ; +$0180 : 028600000003
    btst #0,d6                                        ; +$0186 : 08060000
    beq.w L_000C5C                                    ; +$018A : 67000020
    movea.l 12(a4),a0                                 ; +$018E : 206C000C
    move.l a0,d0                                      ; +$0192 : 2008
    tst.l d0                                          ; +$0194 : 4A80
    beq.w L_000C5C                                    ; +$0196 : 67000014
    movea.l $0004.w,a6                                ; +$019A : 2C780004
    jsr -372(a6)                                      ; +$019E : 4EAEFE8C
    tst.l d0                                          ; +$01A2 : 4A80
    beq.w L_000C5C                                    ; +$01A4 : 67000006
    bclr #0,d6                                        ; +$01A8 : 08860000
L_000C5C:
    btst #1,d6                                        ; +$01AC : 08060001
    beq.w L_000C82                                    ; +$01B0 : 67000020
    movea.l 16(a4),a0                                 ; +$01B4 : 206C0010
    move.l a0,d0                                      ; +$01B8 : 2008
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_000C82                                    ; +$01BC : 67000014
    movea.l $0004.w,a6                                ; +$01C0 : 2C780004
    jsr -372(a6)                                      ; +$01C4 : 4EAEFE8C
    tst.l d0                                          ; +$01C8 : 4A80
    beq.w L_000C82                                    ; +$01CA : 67000006
    bclr #1,d6                                        ; +$01CE : 08860001
L_000C82:
    move.l d6,20(a4)                                  ; +$01D2 : 29460014
    move.l d6,d0                                      ; +$01D6 : 2006
    rts                                               ; +$01D8 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 09 : aga wait vbl --------
Entry_09:
Aga_Wait_Vbl:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)                   ; +$0000 : 48E7FFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    tst.l (a2)                                        ; +$0008 : 4A92
    beq.s L_000CA2                                    ; +$000A : 6708
    movea.l 8(a2),a6                                  ; +$000C : 2C6A0008
    jsr -270(a6)                                      ; +$0010 : 4EAEFEF2
L_000CA2:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6                   ; +$0014 : 4CDF77FF
    rts                                               ; +$0018 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 10 : aga double buffer --------
Entry_10:
Aga_Double_Buffer:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    moveq #0,d3                                       ; +$0004 : 7600
    movea.l 456(a5),a2                                ; +$0006 : 246D01C8
    tst.l (a2)                                        ; +$000A : 4A92
    beq.w L_000DC2                                    ; +$000C : 67000108
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    bne.w L_000D74                                    ; +$0018 : 660000AE
    moveq #24,d0                                      ; +$001C : 7018
    move.l #$00010001,d1                              ; +$001E : 223C00010001
    movea.l $0004.w,a6                                ; +$0024 : 2C780004
    jsr -684(a6)                                      ; +$0028 : 4EAEFD54
    tst.l d0                                          ; +$002C : 4A80
    beq.w L_000DC2                                    ; +$002E : 670000E6
    movea.l d0,a4                                     ; +$0032 : 2840
    movea.l $0004.w,a6                                ; +$0034 : 2C780004
    jsr -666(a6)                                      ; +$0038 : 4EAEFD66
    tst.l d0                                          ; +$003C : 4A80
    beq.w L_000DB8                                    ; +$003E : 670000CC
    move.l d0,12(a4)                                  ; +$0042 : 2940000C
    movea.l $0004.w,a6                                ; +$0046 : 2C780004
    jsr -666(a6)                                      ; +$004A : 4EAEFD66
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_000D94                                    ; +$0050 : 67000096
    move.l d0,16(a4)                                  ; +$0054 : 29400010
    movea.l (a2),a0                                   ; +$0058 : 2052
    suba.l a1,a1                                      ; +$005A : 93C9
    moveq #1,d0                                       ; +$005C : 7001
    movea.l 4(a2),a6                                  ; +$005E : 2C6A0004
    jsr -768(a6)                                      ; +$0062 : 4EAEFD00
    tst.l d0                                          ; +$0066 : 4A80
    beq.w L_000D94                                    ; +$0068 : 6700007E
    move.l d0,(a4)                                    ; +$006C : 2880
    movea.l (a2),a0                                   ; +$006E : 2052
    suba.l a1,a1                                      ; +$0070 : 93C9
    moveq #2,d0                                       ; +$0072 : 7002
    movea.l 4(a2),a6                                  ; +$0074 : 2C6A0004
    jsr -768(a6)                                      ; +$0078 : 4EAEFD00
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_000D88                                    ; +$007E : 6700005C
    move.l d0,4(a4)                                   ; +$0082 : 29400004
    movea.l (a4),a0                                   ; +$0086 : 2054
    movea.l 4(a0),a0                                  ; +$0088 : 20680004
    move.l a0,d0                                      ; +$008C : 2008
    tst.l d0                                          ; +$008E : 4A80
    beq.w L_000D7A                                    ; +$0090 : 6700003C
    move.l 12(a4),d0                                  ; +$0094 : 202C000C
    move.l d0,22(a0)                                  ; +$0098 : 21400016
    move.l 16(a4),d0                                  ; +$009C : 202C0010
    move.l d0,54(a0)                                  ; +$00A0 : 21400036
    movea.l 4(a4),a0                                  ; +$00A4 : 206C0004
    movea.l 4(a0),a0                                  ; +$00A8 : 20680004
    move.l a0,d0                                      ; +$00AC : 2008
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_000D7A                                    ; +$00B0 : 6700001C
    move.l 12(a4),d0                                  ; +$00B4 : 202C000C
    move.l d0,22(a0)                                  ; +$00B8 : 21400016
    move.l 16(a4),d0                                  ; +$00BC : 202C0010
    move.l d0,54(a0)                                  ; +$00C0 : 21400036
    move.l a4,32(a2)                                  ; +$00C4 : 254C0020
L_000D74:
    moveq #1,d3                                       ; +$00C8 : 7601
    bra.w L_000DC2                                    ; +$00CA : 6000004A
L_000D7A:
    movea.l (a2),a0                                   ; +$00CE : 2052
    movea.l 4(a4),a1                                  ; +$00D0 : 226C0004
    movea.l 4(a2),a6                                  ; +$00D4 : 2C6A0004
    jsr -774(a6)                                      ; +$00D8 : 4EAEFCFA
L_000D88:
    movea.l (a2),a0                                   ; +$00DC : 2052
    movea.l (a4),a1                                   ; +$00DE : 2254
    movea.l 4(a2),a6                                  ; +$00E0 : 2C6A0004
    jsr -774(a6)                                      ; +$00E4 : 4EAEFCFA
L_000D94:
    movea.l $0004.w,a6                                ; +$00E8 : 2C780004
    movea.l 16(a4),a0                                 ; +$00EC : 206C0010
    move.l a0,d0                                      ; +$00F0 : 2008
    tst.l d0                                          ; +$00F2 : 4A80
    beq.w L_000DA8                                    ; +$00F4 : 67000006
    jsr -672(a6)                                      ; +$00F8 : 4EAEFD60
L_000DA8:
    movea.l 12(a4),a0                                 ; +$00FC : 206C000C
    move.l a0,d0                                      ; +$0100 : 2008
    tst.l d0                                          ; +$0102 : 4A80
    beq.w L_000DB8                                    ; +$0104 : 67000006
    jsr -672(a6)                                      ; +$0108 : 4EAEFD60
L_000DB8:
    movea.l a4,a1                                     ; +$010C : 224C
    movea.l $0004.w,a6                                ; +$010E : 2C780004
    jsr -690(a6)                                      ; +$0112 : 4EAEFD4E
L_000DC2:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0116 : 4CDF7FF7
    moveq #0,d2                                       ; +$011A : 7400
    rts                                               ; +$011C : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 11 : aga swap --------
Entry_11:
Aga_Swap:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    moveq #0,d3                                       ; +$0004 : 7600
    movea.l 456(a5),a2                                ; +$0006 : 246D01C8
    tst.l (a2)                                        ; +$000A : 4A92
    beq.w L_000E60                                    ; +$000C : 67000084
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_000E60                                    ; +$0018 : 67000078
    move.l 12(a4),d0                                  ; +$001C : 202C000C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_000E60                                    ; +$0022 : 6700006E
    move.l 16(a4),d0                                  ; +$0026 : 202C0010
    tst.l d0                                          ; +$002A : 4A80
    beq.w L_000E60                                    ; +$002C : 67000064
    bsr.w L_000E68                                    ; +$0030 : 61000068
    tst.l d0                                          ; +$0034 : 4A80
    bne.w L_000E60                                    ; +$0036 : 6600005A
    move.l 8(a4),d0                                   ; +$003A : 202C0008
    tst.l d0                                          ; +$003E : 4A80
    beq.w L_000E18                                    ; +$0040 : 67000008
    moveq #0,d7                                       ; +$0044 : 7E00
    bra.w L_000E1A                                    ; +$0046 : 60000004
L_000E18:
    moveq #1,d7                                       ; +$004A : 7E01
L_000E1A:
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_000E60                                    ; +$0054 : 6700003C
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
    tst.l d7                                          ; +$005C : 4A87
    beq.w L_000E38                                    ; +$005E : 6700000A
    movea.l 4(a4),a1                                  ; +$0062 : 226C0004
    bra.w L_000E3A                                    ; +$0066 : 60000004
L_000E38:
    movea.l (a4),a1                                   ; +$006A : 2254
L_000E3A:
    move.l a1,d0                                      ; +$006C : 2009
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_000E60                                    ; +$0070 : 67000020
    movea.l (a2),a0                                   ; +$0074 : 2052
    movea.l 4(a2),a6                                  ; +$0076 : 2C6A0004
    jsr -780(a6)                                      ; +$007A : 4EAEFCF4
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_000E60                                    ; +$0080 : 67000010
    move.l d7,8(a4)                                   ; +$0084 : 29470008
    move.l #$00000003,20(a4)                          ; +$0088 : 297C000000030014
    moveq #1,d3                                       ; +$0090 : 7601
L_000E60:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0092 : 4CDF7FF7
    moveq #0,d2                                       ; +$0096 : 7400
    rts                                               ; +$0098 : 4E75
L_000E68:
    move.l 20(a4),d6                                  ; +$009A : 2C2C0014
    andi.l #$00000003,d6                              ; +$009E : 028600000003
    btst #0,d6                                        ; +$00A4 : 08060000
    beq.w L_000E98                                    ; +$00A8 : 67000020
    movea.l 12(a4),a0                                 ; +$00AC : 206C000C
    move.l a0,d0                                      ; +$00B0 : 2008
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_000E98                                    ; +$00B4 : 67000014
    movea.l $0004.w,a6                                ; +$00B8 : 2C780004
    jsr -372(a6)                                      ; +$00BC : 4EAEFE8C
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_000E98                                    ; +$00C2 : 67000006
    bclr #0,d6                                        ; +$00C6 : 08860000
L_000E98:
    btst #1,d6                                        ; +$00CA : 08060001
    beq.w L_000EBE                                    ; +$00CE : 67000020
    movea.l 16(a4),a0                                 ; +$00D2 : 206C0010
    move.l a0,d0                                      ; +$00D6 : 2008
    tst.l d0                                          ; +$00D8 : 4A80
    beq.w L_000EBE                                    ; +$00DA : 67000014
    movea.l $0004.w,a6                                ; +$00DE : 2C780004
    jsr -372(a6)                                      ; +$00E2 : 4EAEFE8C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_000EBE                                    ; +$00E8 : 67000006
    bclr #1,d6                                        ; +$00EC : 08860001
L_000EBE:
    move.l d6,20(a4)                                  ; +$00F0 : 29460014
    move.l d6,d0                                      ; +$00F4 : 2006
    rts                                               ; +$00F6 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 12 : aga back fill --------
Entry_12:
Aga_Back_Fill:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0000 : 48E7FFFE
    move.l d3,d7                                      ; +$0004 : 2E03
    movea.l 456(a5),a2                                ; +$0006 : 246D01C8
    move.l a2,d0                                      ; +$000A : 200A
    tst.l d0                                          ; +$000C : 4A80
    beq.w L_000F5E                                    ; +$000E : 67000084
    tst.l (a2)                                        ; +$0012 : 4A92
    beq.w L_000F5E                                    ; +$0014 : 6700007E
    movea.l 32(a2),a3                                 ; +$0018 : 266A0020
    move.l a3,d0                                      ; +$001C : 200B
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_000F5E                                    ; +$0020 : 67000072
    move.l 8(a3),d0                                   ; +$0024 : 202B0008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_000EFE                                    ; +$002A : 67000008
    movea.l (a3),a1                                   ; +$002E : 2253
    bra.w L_000F02                                    ; +$0030 : 60000006
L_000EFE:
    movea.l 4(a3),a1                                  ; +$0034 : 226B0004
L_000F02:
    move.l a1,d0                                      ; +$0038 : 2009
    tst.l d0                                          ; +$003A : 4A80
    beq.w L_000F5E                                    ; +$003C : 67000056
    movea.l (a1),a4                                   ; +$0040 : 2851
    move.l a4,d0                                      ; +$0042 : 200C
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_000F5E                                    ; +$0046 : 6700004C
    move.l #$00000080,d0                              ; +$004A : 203C00000080
    move.l #$00010001,d1                              ; +$0050 : 223C00010001
    movea.l $0004.w,a6                                ; +$0056 : 2C780004
    jsr -684(a6)                                      ; +$005A : 4EAEFD54
    tst.l d0                                          ; +$005E : 4A80
    beq.w L_000F5E                                    ; +$0060 : 67000032
    movea.l d0,a3                                     ; +$0064 : 2640
    movea.l a3,a1                                     ; +$0066 : 224B
    movea.l 8(a2),a6                                  ; +$0068 : 2C6A0008
    jsr -198(a6)                                      ; +$006C : 4EAEFF3A
    move.l a4,4(a3)                                   ; +$0070 : 274C0004
    move.l d7,d0                                      ; +$0074 : 2007
    andi.l #$000000FF,d0                              ; +$0076 : 0280000000FF
    movea.l a3,a1                                     ; +$007C : 224B
    movea.l 8(a2),a6                                  ; +$007E : 2C6A0008
    jsr -234(a6)                                      ; +$0082 : 4EAEFF16
    jsr -228(a6)                                      ; +$0086 : 4EAEFF1C
    movea.l a3,a1                                     ; +$008A : 224B
    movea.l $0004.w,a6                                ; +$008C : 2C780004
    jsr -690(a6)                                      ; +$0090 : 4EAEFD4E
L_000F5E:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$0094 : 4CDF7FFF
    rts                                               ; +$0098 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 13 : aga iff load --------
Entry_13:
Aga_Iff_Load:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    movea.l 456(a5),a0                                ; +$0004 : 206D01C8
    move.l d3,d4                                      ; +$0008 : 2803
    movea.l d3,a1                                     ; +$000A : 2243
    lea -128(a7),a7                                   ; +$000C : 4FEFFF80
    movea.l a7,a5                                     ; +$0010 : 2A4F
    move.l #$00000000,(a5)                            ; +$0012 : 2ABC00000000
    move.l #$00000000,4(a5)                           ; +$0018 : 2B7C000000000004
    move.l #$00000000,8(a5)                           ; +$0020 : 2B7C000000000008
    move.l #$00000000,12(a5)                          ; +$0028 : 2B7C00000000000C
    move.l #$00000000,16(a5)                          ; +$0030 : 2B7C000000000010
    move.l #$00000000,20(a5)                          ; +$0038 : 2B7C000000000014
    move.l #$00000000,24(a5)                          ; +$0040 : 2B7C000000000018
    move.l #$00000000,28(a5)                          ; +$0048 : 2B7C00000000001C
    move.l #$00000000,32(a5)                          ; +$0050 : 2B7C000000000020
    move.l #$00000000,36(a5)                          ; +$0058 : 2B7C000000000024
    move.l #$00000000,40(a5)                          ; +$0060 : 2B7C000000000028
    move.l #$00000000,44(a5)                          ; +$0068 : 2B7C00000000002C
    move.l #$00000000,48(a5)                          ; +$0070 : 2B7C000000000030
    move.l #$00000000,52(a5)                          ; +$0078 : 2B7C000000000034
    move.l #$00000000,56(a5)                          ; +$0080 : 2B7C000000000038
    move.l #$00000000,60(a5)                          ; +$0088 : 2B7C00000000003C
    move.l #$00000000,64(a5)                          ; +$0090 : 2B7C000000000040
    move.l #$00000000,68(a5)                          ; +$0098 : 2B7C000000000044
    move.l #$00000000,72(a5)                          ; +$00A0 : 2B7C000000000048
    move.l #$00000000,76(a5)                          ; +$00A8 : 2B7C00000000004C
    move.l #$00000000,80(a5)                          ; +$00B0 : 2B7C000000000050
    move.l #$00000000,84(a5)                          ; +$00B8 : 2B7C000000000054
    move.l #$00000000,88(a5)                          ; +$00C0 : 2B7C000000000058
    move.l #$00000000,92(a5)                          ; +$00C8 : 2B7C00000000005C
    move.l #$00000000,96(a5)                          ; +$00D0 : 2B7C000000000060
    move.l #$00000000,100(a5)                         ; +$00D8 : 2B7C000000000064
    move.l #$00000000,104(a5)                         ; +$00E0 : 2B7C000000000068
    move.l #$00000000,108(a5)                         ; +$00E8 : 2B7C00000000006C
    move.l #$00000000,112(a5)                         ; +$00F0 : 2B7C000000000070
    move.l #$00000000,116(a5)                         ; +$00F8 : 2B7C000000000074
    move.l #$00000000,120(a5)                         ; +$0100 : 2B7C000000000078
    move.l #$00000000,124(a5)                         ; +$0108 : 2B7C00000000007C
    move.l a0,(a5)                                    ; +$0110 : 2A88
    move.l a1,4(a5)                                   ; +$0112 : 2B490004
    move.l d4,8(a5)                                   ; +$0116 : 2B440008
    bsr.w L_0010FA                                    ; +$011A : 61000076
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_0010E4                                    ; +$0120 : 6700005A
    bsr.w L_001228                                    ; +$0124 : 6100019A
    tst.l d0                                          ; +$0128 : 4A80
    beq.w L_0010E4                                    ; +$012A : 67000050
    bsr.w L_001480                                    ; +$012E : 610003E8
    tst.l d0                                          ; +$0132 : 4A80
    beq.w L_0010E4                                    ; +$0134 : 67000046
    bsr.w L_00158C                                    ; +$0138 : 610004EA
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_0010E4                                    ; +$013E : 6700003C
    bsr.w L_0016BE                                    ; +$0142 : 61000612
    tst.l d0                                          ; +$0146 : 4A80
    beq.w L_0010E4                                    ; +$0148 : 67000032
    movea.l (a5),a2                                   ; +$014C : 2455
    movea.l 8(a2),a6                                  ; +$014E : 2C6A0008
    jsr -228(a6)                                      ; +$0152 : 4EAEFF1C
    move.l #$00000001,100(a5)                         ; +$0156 : 2B7C000000010064
    bsr.w L_00158C                                    ; +$015E : 610004C4
    tst.l d0                                          ; +$0162 : 4A80
    beq.w L_0010E4                                    ; +$0164 : 67000016
    bsr.w L_00173A                                    ; +$0168 : 61000668
    tst.l d0                                          ; +$016C : 4A80
    beq.w L_0010E4                                    ; +$016E : 6700000C
    move.l #$00000001,d3                              ; +$0172 : 263C00000001
    bra.w L_0010EA                                    ; +$0178 : 60000008
L_0010E4:
    move.l #$00000000,d3                              ; +$017C : 263C00000000
L_0010EA:
    bsr.w L_001774                                    ; +$0182 : 61000688
    lea 128(a7),a7                                    ; +$0186 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$018A : 4CDF7FF7
    moveq #0,d2                                       ; +$018E : 7400
    rts                                               ; +$0190 : 4E75
L_0010FA:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0192 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$0196 : 246D0004
    move.l #$00000000,d4                              ; +$019A : 283C00000000
    move.w (a2)+,d4                                   ; +$01A0 : 381A
    tst.l d4                                          ; +$01A2 : 4A84
    beq.w L_00121A                                    ; +$01A4 : 6700010C
    move.l d4,d0                                      ; +$01A8 : 2004
    addq.l #1,d0                                      ; +$01AA : 5280
    move.l #$00010001,d1                              ; +$01AC : 223C00010001
    movea.l $0004.w,a6                                ; +$01B2 : 2C780004
    jsr -684(a6)                                      ; +$01B6 : 4EAEFD54
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_00121A                                    ; +$01BC : 670000F4
    move.l d0,12(a5)                                  ; +$01C0 : 2B40000C
    movea.l d0,a1                                     ; +$01C4 : 2240
L_00112E:
    move.b (a2)+,(a1)+                                ; +$01C6 : 12DA
    subq.l #1,d4                                      ; +$01C8 : 5384
    bne.w L_00112E                                    ; +$01CA : 6600FFFA
    lea L_0017F4(pc),a1                               ; +$01CE : 43FA06BC
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    movea.l $0004.w,a6                                ; +$01D8 : 2C780004
    jsr -552(a6)                                      ; +$01DC : 4EAEFDD8
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_00121A                                    ; +$01E2 : 670000CE
    move.l d0,16(a5)                                  ; +$01E6 : 2B400010
    movea.l d0,a6                                     ; +$01EA : 2C40
    move.l 12(a5),d1                                  ; +$01EC : 222D000C
    move.l #$000003ED,d2                              ; +$01F0 : 243C000003ED
    jsr -30(a6)                                       ; +$01F6 : 4EAEFFE2
    tst.l d0                                          ; +$01FA : 4A80
    beq.w L_00121A                                    ; +$01FC : 670000B4
    move.l d0,20(a5)                                  ; +$0200 : 2B400014
    move.l d0,d1                                      ; +$0204 : 2200
    move.l a5,d2                                      ; +$0206 : 240D
    addi.l #$00000068,d2                              ; +$0208 : 068200000068
    move.l #$0000000C,d3                              ; +$020E : 263C0000000C
    jsr -42(a6)                                       ; +$0214 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$0218 : 0C800000000C
    bne.w L_00121A                                    ; +$021E : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0222 : 0CAD464F524D0068
    bne.w L_00121A                                    ; +$022A : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$022E : 0CAD494C424D0070
    bne.w L_00121A                                    ; +$0236 : 6600007A
    move.l 108(a5),d4                                 ; +$023A : 282D006C
    cmpi.l #$00000004,d4                              ; +$023E : 0C8400000004
    bcs.w L_00121A                                    ; +$0244 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$0248 : 0C847FFFFFF7
    bhi.w L_00121A                                    ; +$024E : 62000062
    addq.l #8,d4                                      ; +$0252 : 5084
    move.l d4,28(a5)                                  ; +$0254 : 2B44001C
    move.l d4,d0                                      ; +$0258 : 2004
    move.l #$00010001,d1                              ; +$025A : 223C00010001
    movea.l $0004.w,a6                                ; +$0260 : 2C780004
    jsr -684(a6)                                      ; +$0264 : 4EAEFD54
    tst.l d0                                          ; +$0268 : 4A80
    beq.w L_00121A                                    ; +$026A : 67000046
    move.l d0,24(a5)                                  ; +$026E : 2B400018
    movea.l d0,a2                                     ; +$0272 : 2440
    move.l 104(a5),(a2)                               ; +$0274 : 24AD0068
    move.l 108(a5),4(a2)                              ; +$0278 : 256D006C0004
    move.l 112(a5),8(a2)                              ; +$027E : 256D00700008
    move.l 20(a5),d1                                  ; +$0284 : 222D0014
    move.l a2,d2                                      ; +$0288 : 240A
    addi.l #$0000000C,d2                              ; +$028A : 06820000000C
    move.l d4,d3                                      ; +$0290 : 2604
    subi.l #$0000000C,d3                              ; +$0292 : 04830000000C
    move.l d3,d4                                      ; +$0298 : 2803
    movea.l 16(a5),a6                                 ; +$029A : 2C6D0010
    jsr -42(a6)                                       ; +$029E : 4EAEFFD6
    cmp.l d4,d0                                       ; +$02A2 : B084
    bne.w L_00121A                                    ; +$02A4 : 6600000C
    move.l #$00000001,d0                              ; +$02A8 : 203C00000001
    bra.w L_001220                                    ; +$02AE : 60000008
L_00121A:
    move.l #$00000000,d0                              ; +$02B2 : 203C00000000
L_001220:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$02B8 : 4CDF5FFE
    tst.l d0                                          ; +$02BC : 4A80
    rts                                               ; +$02BE : 4E75
L_001228:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$02C0 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$02C4 : 206D0018
    move.l 28(a5),d7                                  ; +$02C8 : 2E2D001C
    subi.l #$0000000C,d7                              ; +$02CC : 04870000000C
    move.l a0,d0                                      ; +$02D2 : 2008
    addi.l #$0000000C,d0                              ; +$02D4 : 06800000000C
    movea.l d0,a0                                     ; +$02DA : 2040
L_001244:
    tst.l d7                                          ; +$02DC : 4A87
    beq.w L_001308                                    ; +$02DE : 670000C0
    cmpi.l #$00000008,d7                              ; +$02E2 : 0C8700000008
    bcs.w L_001472                                    ; +$02E8 : 65000220
    move.l (a0)+,d3                                   ; +$02EC : 2618
    move.l (a0)+,d2                                   ; +$02EE : 2418
    subq.l #8,d7                                      ; +$02F0 : 5187
    cmp.l d7,d2                                       ; +$02F2 : B487
    bhi.w L_001472                                    ; +$02F4 : 62000214
    move.l d2,d1                                      ; +$02F8 : 2202
    andi.l #$00000001,d1                              ; +$02FA : 028100000001
    add.l d2,d1                                       ; +$0300 : D282
    cmp.l d7,d1                                       ; +$0302 : B287
    bhi.w L_001472                                    ; +$0304 : 62000204
    sub.l d1,d7                                       ; +$0308 : 9E81
    cmpi.l #$424D4844,d3                              ; +$030A : 0C83424D4844
    beq.w L_00129E                                    ; +$0310 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0314 : 0C83434D4150
    beq.w L_0012B8                                    ; +$031A : 67000034
    cmpi.l #$43414D47,d3                              ; +$031E : 0C8343414D47
    beq.w L_0012E0                                    ; +$0324 : 67000052
    cmpi.l #$424F4459,d3                              ; +$0328 : 0C83424F4459
    beq.w L_0012CC                                    ; +$032E : 67000034
    bra.w L_0012FE                                    ; +$0332 : 60000062
L_00129E:
    tst.l 32(a5)                                      ; +$0336 : 4AAD0020
    bne.w L_001472                                    ; +$033A : 660001CE
    cmpi.l #$00000014,d2                              ; +$033E : 0C8200000014
    bne.w L_001472                                    ; +$0344 : 660001C4
    move.l a0,32(a5)                                  ; +$0348 : 2B480020
    bra.w L_0012FE                                    ; +$034C : 60000048
L_0012B8:
    tst.l 36(a5)                                      ; +$0350 : 4AAD0024
    bne.w L_001472                                    ; +$0354 : 660001B4
    move.l a0,36(a5)                                  ; +$0358 : 2B480024
    move.l d2,40(a5)                                  ; +$035C : 2B420028
    bra.w L_0012FE                                    ; +$0360 : 60000034
L_0012CC:
    tst.l 44(a5)                                      ; +$0364 : 4AAD002C
    bne.w L_001472                                    ; +$0368 : 660001A0
    move.l a0,44(a5)                                  ; +$036C : 2B48002C
    move.l d2,48(a5)                                  ; +$0370 : 2B420030
    bra.w L_0012FE                                    ; +$0374 : 60000020
L_0012E0:
    tst.l 52(a5)                                      ; +$0378 : 4AAD0034
    bne.w L_001472                                    ; +$037C : 6600018C
    cmpi.l #$00000004,d2                              ; +$0380 : 0C8200000004
    bne.w L_001472                                    ; +$0386 : 66000182
    move.l #$00000001,52(a5)                          ; +$038A : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$0392 : 2B50005C
L_0012FE:
    move.l a0,d0                                      ; +$0396 : 2008
    add.l d1,d0                                       ; +$0398 : D081
    movea.l d0,a0                                     ; +$039A : 2040
    bra.w L_001244                                    ; +$039C : 6000FF3E
L_001308:
    tst.l 32(a5)                                      ; +$03A0 : 4AAD0020
    beq.w L_001472                                    ; +$03A4 : 67000164
    tst.l 36(a5)                                      ; +$03A8 : 4AAD0024
    beq.w L_001472                                    ; +$03AC : 6700015C
    tst.l 44(a5)                                      ; +$03B0 : 4AAD002C
    beq.w L_001472                                    ; +$03B4 : 67000154
    tst.l 48(a5)                                      ; +$03B8 : 4AAD0030
    beq.w L_001472                                    ; +$03BC : 6700014C
    movea.l 32(a5),a0                                 ; +$03C0 : 206D0020
    move.l #$00000000,d0                              ; +$03C4 : 203C00000000
    move.w (a0),d0                                    ; +$03CA : 3010
    move.l d0,56(a5)                                  ; +$03CC : 2B400038
    move.l #$00000000,d0                              ; +$03D0 : 203C00000000
    move.w 2(a0),d0                                   ; +$03D6 : 30280002
    move.l d0,60(a5)                                  ; +$03DA : 2B40003C
    move.l #$00000000,d0                              ; +$03DE : 203C00000000
    move.b 8(a0),d0                                   ; +$03E4 : 10280008
    move.l d0,64(a5)                                  ; +$03E8 : 2B400040
    move.l #$00000000,d0                              ; +$03EC : 203C00000000
    move.b 9(a0),d0                                   ; +$03F2 : 10280009
    move.l d0,68(a5)                                  ; +$03F6 : 2B400044
    move.l #$00000000,d0                              ; +$03FA : 203C00000000
    move.b 10(a0),d0                                  ; +$0400 : 1028000A
    move.l d0,72(a5)                                  ; +$0404 : 2B400048
    tst.l 56(a5)                                      ; +$0408 : 4AAD0038
    beq.w L_001472                                    ; +$040C : 670000FC
    tst.l 60(a5)                                      ; +$0410 : 4AAD003C
    beq.w L_001472                                    ; +$0414 : 670000F4
    tst.l 64(a5)                                      ; +$0418 : 4AAD0040
    beq.w L_001472                                    ; +$041C : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0420 : 0CAD000000080040
    bhi.w L_001472                                    ; +$0428 : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$042C : 0CAD000000020044
    bhi.w L_001472                                    ; +$0434 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$0438 : 0CAD000000010048
    bhi.w L_001472                                    ; +$0440 : 620000C8
    move.l 40(a5),d0                                  ; +$0444 : 202D0028
    tst.l d0                                          ; +$0448 : 4A80
    beq.w L_001472                                    ; +$044A : 670000BE
    cmpi.l #$00000300,d0                              ; +$044E : 0C8000000300
    bhi.w L_001472                                    ; +$0454 : 620000B4
    divu.w #$0003,d0                                  ; +$0458 : 80FC0003
    move.l d0,d1                                      ; +$045C : 2200
    swap d1                                           ; +$045E : 4841
    tst.w d1                                          ; +$0460 : 4A41
    bne.w L_001472                                    ; +$0462 : 660000A6
    andi.l #$0000FFFF,d0                              ; +$0466 : 02800000FFFF
    move.l d0,40(a5)                                  ; +$046C : 2B400028
    move.l 56(a5),d0                                  ; +$0470 : 202D0038
    addi.l #$0000000F,d0                              ; +$0474 : 06800000000F
    lsr.l #4,d0                                       ; +$047A : E888
    lsl.l #1,d0                                       ; +$047C : E388
    move.l d0,76(a5)                                  ; +$047E : 2B40004C
    move.l 92(a5),d0                                  ; +$0482 : 202D005C
    move.l d0,d1                                      ; +$0486 : 2200
    andi.l #$FFFF0000,d1                              ; +$0488 : 0281FFFF0000
    bne.w L_001404                                    ; +$048E : 6600000C
    andi.l #$00008EFD,d0                              ; +$0492 : 028000008EFD
    bra.w L_001410                                    ; +$0498 : 6000000E
L_001404:
    move.l d0,d1                                      ; +$049C : 2200
    andi.l #$00001000,d1                              ; +$049E : 028100001000
    beq.w L_001472                                    ; +$04A4 : 67000064
L_001410:
    move.l d0,52(a5)                                  ; +$04A8 : 2B400034
    move.l d0,d1                                      ; +$04AC : 2200
    andi.l #$00000400,d1                              ; +$04AE : 028100000400
    bne.w L_001472                                    ; +$04B4 : 66000054
    move.l d0,d1                                      ; +$04B8 : 2200
    andi.l #$00000800,d1                              ; +$04BA : 028100000800
    beq.w L_001452                                    ; +$04C0 : 67000028
    andi.l #$00000080,d0                              ; +$04C4 : 028000000080
    bne.w L_001472                                    ; +$04CA : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$04CE : 0CAD000000060040
    beq.w L_00144E                                    ; +$04D6 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$04DA : 0CAD000000080040
    bne.w L_001472                                    ; +$04E2 : 66000026
L_00144E:
    bra.w L_001468                                    ; +$04E6 : 60000018
L_001452:
    andi.l #$00000080,d0                              ; +$04EA : 028000000080
    beq.w L_001468                                    ; +$04F0 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$04F4 : 0CAD000000060040
    bne.w L_001472                                    ; +$04FC : 6600000C
L_001468:
    move.l #$00000001,d0                              ; +$0500 : 203C00000001
    bra.w L_001478                                    ; +$0506 : 60000008
L_001472:
    move.l #$00000000,d0                              ; +$050A : 203C00000000
L_001478:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0510 : 4CDF5FFE
    tst.l d0                                          ; +$0514 : 4A80
    rts                                               ; +$0516 : 4E75
L_001480:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0518 : 48E77FFA
    movea.l (a5),a2                                   ; +$051C : 2455
    move.l a2,d0                                      ; +$051E : 200A
    tst.l d0                                          ; +$0520 : 4A80
    beq.w L_00157E                                    ; +$0522 : 670000F2
    move.l (a2),d0                                    ; +$0526 : 2012
    tst.l d0                                          ; +$0528 : 4A80
    beq.w L_00157E                                    ; +$052A : 670000EA
    move.l d0,88(a5)                                  ; +$052E : 2B400058
    tst.l 8(a2)                                       ; +$0532 : 4AAA0008
    beq.w L_00157E                                    ; +$0536 : 670000DE
    move.l 12(a2),d0                                  ; +$053A : 202A000C
    cmp.l 56(a5),d0                                   ; +$053E : B0AD0038
    bne.w L_00157E                                    ; +$0542 : 660000D2
    move.l 16(a2),d0                                  ; +$0546 : 202A0010
    cmp.l 60(a5),d0                                   ; +$054A : B0AD003C
    bne.w L_00157E                                    ; +$054E : 660000C6
    move.l 28(a2),d0                                  ; +$0552 : 202A001C
    cmp.l 64(a5),d0                                   ; +$0556 : B0AD0040
    bne.w L_00157E                                    ; +$055A : 660000BA
    move.l 24(a2),d0                                  ; +$055E : 202A0018
    move.l 52(a5),d1                                  ; +$0562 : 222D0034
    move.l d1,d2                                      ; +$0566 : 2401
    andi.l #$FFFF0000,d2                              ; +$0568 : 0282FFFF0000
    bne.w L_0014E0                                    ; +$056E : 66000008
    andi.l #$00008EFD,d0                              ; +$0572 : 028000008EFD
L_0014E0:
    cmp.l d1,d0                                       ; +$0578 : B081
    bne.w L_00157E                                    ; +$057A : 6600009A
    movea.l 32(a2),a3                                 ; +$057E : 266A0020
    move.l a3,d0                                      ; +$0582 : 200B
    tst.l d0                                          ; +$0584 : 4A80
    beq.w L_00157E                                    ; +$0586 : 6700008E
    tst.l 8(a3)                                       ; +$058A : 4AAB0008
    beq.w L_001500                                    ; +$058E : 67000008
    movea.l (a3),a0                                   ; +$0592 : 2053
    bra.w L_001504                                    ; +$0594 : 60000006
L_001500:
    movea.l 4(a3),a0                                  ; +$0598 : 206B0004
L_001504:
    move.l a0,d0                                      ; +$059C : 2008
    tst.l d0                                          ; +$059E : 4A80
    beq.w L_00157E                                    ; +$05A0 : 67000074
    movea.l (a0),a3                                   ; +$05A4 : 2650
    move.l a3,d0                                      ; +$05A6 : 200B
    tst.l d0                                          ; +$05A8 : 4A80
    beq.w L_00157E                                    ; +$05AA : 6700006A
    move.l d0,80(a5)                                  ; +$05AE : 2B400050
    move.l #$00000000,d0                              ; +$05B2 : 203C00000000
    move.w (a3),d0                                    ; +$05B8 : 3013
    cmp.l 76(a5),d0                                   ; +$05BA : B0AD004C
    bcs.w L_00157E                                    ; +$05BE : 65000056
    move.l d0,84(a5)                                  ; +$05C2 : 2B400054
    move.l #$00000000,d0                              ; +$05C6 : 203C00000000
    move.w 2(a3),d0                                   ; +$05CC : 302B0002
    cmp.l 60(a5),d0                                   ; +$05D0 : B0AD003C
    bcs.w L_00157E                                    ; +$05D4 : 65000040
    move.l #$00000000,d0                              ; +$05D8 : 203C00000000
    move.b 5(a3),d0                                   ; +$05DE : 102B0005
    cmp.l 64(a5),d0                                   ; +$05E2 : B0AD0040
    bne.w L_00157E                                    ; +$05E6 : 6600002E
    move.l a3,d0                                      ; +$05EA : 200B
    addq.l #8,d0                                      ; +$05EC : 5080
    movea.l d0,a0                                     ; +$05EE : 2040
    move.l 64(a5),d1                                  ; +$05F0 : 222D0040
L_00155C:
    move.l (a0)+,d0                                   ; +$05F4 : 2018
    tst.l d0                                          ; +$05F6 : 4A80
    beq.w L_00157E                                    ; +$05F8 : 6700001C
    cmpi.l #$FFFFFFFF,d0                              ; +$05FC : 0C80FFFFFFFF
    beq.w L_00157E                                    ; +$0602 : 67000012
    subq.l #1,d1                                      ; +$0606 : 5381
    bne.w L_00155C                                    ; +$0608 : 6600FFEA
    move.l #$00000001,d0                              ; +$060C : 203C00000001
    bra.w L_001584                                    ; +$0612 : 60000008
L_00157E:
    move.l #$00000000,d0                              ; +$0616 : 203C00000000
L_001584:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$061C : 4CDF5FFE
    tst.l d0                                          ; +$0620 : 4A80
    rts                                               ; +$0622 : 4E75
L_00158C:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0624 : 48E77FFA
    movea.l 44(a5),a0                                 ; +$0628 : 206D002C
    move.l a0,d0                                      ; +$062C : 2008
    add.l 48(a5),d0                                   ; +$062E : D0AD0030
    movea.l d0,a2                                     ; +$0632 : 2440
    move.l #$00000000,d4                              ; +$0634 : 283C00000000
    move.l #$00000000,d3                              ; +$063A : 263C00000000
L_0015A8:
    move.l #$00000000,d5                              ; +$0640 : 2A3C00000000
    movea.l 80(a5),a3                                 ; +$0646 : 266D0050
    move.l a3,d0                                      ; +$064A : 200B
    addq.l #8,d0                                      ; +$064C : 5080
    movea.l d0,a4                                     ; +$064E : 2840
L_0015B8:
    move.l 76(a5),d6                                  ; +$0650 : 2C2D004C
    movea.l #$00000000,a6                             ; +$0654 : 2C7C00000000
    cmp.l 64(a5),d5                                   ; +$065A : BAAD0040
    bcc.w L_0015D8                                    ; +$065E : 64000010
    tst.l 100(a5)                                     ; +$0662 : 4AAD0064
    beq.w L_0015D8                                    ; +$0666 : 67000008
    move.l (a4)+,d0                                   ; +$066A : 201C
    add.l d3,d0                                       ; +$066C : D083
    movea.l d0,a6                                     ; +$066E : 2C40
L_0015D8:
    tst.l 72(a5)                                      ; +$0670 : 4AAD0048
    beq.w L_001606                                    ; +$0674 : 67000028
    move.l a0,d0                                      ; +$0678 : 2008
    cmp.l a2,d0                                       ; +$067A : B08A
    bcc.w L_0016B0                                    ; +$067C : 640000CA
    move.l #$00000000,d1                              ; +$0680 : 223C00000000
    move.b (a0)+,d1                                   ; +$0686 : 1218
    cmpi.l #$00000080,d1                              ; +$0688 : 0C8100000080
    beq.w L_0015D8                                    ; +$068E : 6700FFE0
    bhi.w L_001632                                    ; +$0692 : 62000036
    addq.l #1,d1                                      ; +$0696 : 5281
    move.l d1,d2                                      ; +$0698 : 2401
    bra.w L_00160A                                    ; +$069A : 60000006
L_001606:
    move.l d6,d1                                      ; +$069E : 2206
    move.l d1,d2                                      ; +$06A0 : 2401
L_00160A:
    cmp.l d6,d1                                       ; +$06A2 : B286
    bhi.w L_0016B0                                    ; +$06A4 : 620000A2
    move.l a2,d0                                      ; +$06A8 : 200A
    sub.l a0,d0                                       ; +$06AA : 9088
    cmp.l d1,d0                                       ; +$06AC : B081
    bcs.w L_0016B0                                    ; +$06AE : 65000098
    sub.l d1,d6                                       ; +$06B2 : 9C81
L_00161C:
    move.b (a0)+,d0                                   ; +$06B4 : 1018
    move.l a6,d7                                      ; +$06B6 : 2E0E
    tst.l d7                                          ; +$06B8 : 4A87
    beq.w L_001628                                    ; +$06BA : 67000004
    move.b d0,(a6)+                                   ; +$06BE : 1CC0
L_001628:
    subq.l #1,d2                                      ; +$06C0 : 5382
    bne.w L_00161C                                    ; +$06C2 : 6600FFF0
    bra.w L_00165C                                    ; +$06C6 : 6000002C
L_001632:
    move.l #$00000101,d2                              ; +$06CA : 243C00000101
    sub.l d1,d2                                       ; +$06D0 : 9481
    cmp.l d6,d2                                       ; +$06D2 : B486
    bhi.w L_0016B0                                    ; +$06D4 : 62000072
    sub.l d2,d6                                       ; +$06D8 : 9C82
    move.l a0,d0                                      ; +$06DA : 2008
    cmp.l a2,d0                                       ; +$06DC : B08A
    bcc.w L_0016B0                                    ; +$06DE : 64000068
    move.b (a0)+,d0                                   ; +$06E2 : 1018
L_00164C:
    move.l a6,d7                                      ; +$06E4 : 2E0E
    tst.l d7                                          ; +$06E6 : 4A87
    beq.w L_001656                                    ; +$06E8 : 67000004
    move.b d0,(a6)+                                   ; +$06EC : 1CC0
L_001656:
    subq.l #1,d2                                      ; +$06EE : 5382
    bne.w L_00164C                                    ; +$06F0 : 6600FFF2
L_00165C:
    tst.l d6                                          ; +$06F4 : 4A86
    bne.w L_0015D8                                    ; +$06F6 : 6600FF78
    addq.l #1,d5                                      ; +$06FA : 5285
    move.l 64(a5),d0                                  ; +$06FC : 202D0040
    cmpi.l #$00000001,68(a5)                          ; +$0700 : 0CAD000000010044
    bne.w L_001676                                    ; +$0708 : 66000004
    addq.l #1,d0                                      ; +$070C : 5280
L_001676:
    cmp.l d0,d5                                       ; +$070E : BA80
    bcs.w L_0015B8                                    ; +$0710 : 6500FF3E
    add.l 84(a5),d3                                   ; +$0714 : D6AD0054
    addq.l #1,d4                                      ; +$0718 : 5284
    cmp.l 60(a5),d4                                   ; +$071A : B8AD003C
    bcs.w L_0015A8                                    ; +$071E : 6500FF20
L_00168A:
    move.l a0,d0                                      ; +$0722 : 2008
    cmp.l a2,d0                                       ; +$0724 : B08A
    beq.w L_0016A6                                    ; +$0726 : 67000016
    tst.l 72(a5)                                      ; +$072A : 4AAD0048
    beq.w L_0016B0                                    ; +$072E : 67000018
    cmpi.b #$80,(a0)+                                 ; +$0732 : 0C180080
    bne.w L_0016B0                                    ; +$0736 : 66000010
    bra.w L_00168A                                    ; +$073A : 6000FFE6
L_0016A6:
    move.l #$00000001,d0                              ; +$073E : 203C00000001
    bra.w L_0016B6                                    ; +$0744 : 60000008
L_0016B0:
    move.l #$00000000,d0                              ; +$0748 : 203C00000000
L_0016B6:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$074E : 4CDF5FFE
    tst.l d0                                          ; +$0752 : 4A80
    rts                                               ; +$0754 : 4E75
L_0016BE:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0756 : 48E77FFA
    move.l 40(a5),d0                                  ; +$075A : 202D0028
    move.l d0,d1                                      ; +$075E : 2200
    lsl.l #1,d0                                       ; +$0760 : E388
    add.l d1,d0                                       ; +$0762 : D081
    lsl.l #2,d0                                       ; +$0764 : E588
    addq.l #8,d0                                      ; +$0766 : 5080
    move.l #$00010001,d1                              ; +$0768 : 223C00010001
    movea.l $0004.w,a6                                ; +$076E : 2C780004
    jsr -684(a6)                                      ; +$0772 : 4EAEFD54
    tst.l d0                                          ; +$0776 : 4A80
    beq.w L_00172C                                    ; +$0778 : 6700004A
    move.l d0,96(a5)                                  ; +$077C : 2B400060
    movea.l d0,a1                                     ; +$0780 : 2240
    move.l 40(a5),d0                                  ; +$0782 : 202D0028
    swap d0                                           ; +$0786 : 4840
    move.l d0,(a1)+                                   ; +$0788 : 22C0
    movea.l 36(a5),a0                                 ; +$078A : 206D0024
    move.l 40(a5),d4                                  ; +$078E : 282D0028
    move.l d4,d0                                      ; +$0792 : 2004
    add.l d4,d0                                       ; +$0794 : D084
    add.l d0,d4                                       ; +$0796 : D880
L_001700:
    move.l #$00000000,d0                              ; +$0798 : 203C00000000
    move.b (a0)+,d0                                   ; +$079E : 1018
    move.l d0,d1                                      ; +$07A0 : 2200
    lsl.l #8,d0                                       ; +$07A2 : E188
    or.l d1,d0                                        ; +$07A4 : 8081
    move.l d0,d1                                      ; +$07A6 : 2200
    swap d0                                           ; +$07A8 : 4840
    or.l d1,d0                                        ; +$07AA : 8081
    move.l d0,(a1)+                                   ; +$07AC : 22C0
    subq.l #1,d4                                      ; +$07AE : 5384
    bne.w L_001700                                    ; +$07B0 : 6600FFE6
    move.l #$00000000,(a1)                            ; +$07B4 : 22BC00000000
    move.l #$00000001,d0                              ; +$07BA : 203C00000001
    bra.w L_001732                                    ; +$07C0 : 60000008
L_00172C:
    move.l #$00000000,d0                              ; +$07C4 : 203C00000000
L_001732:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$07CA : 4CDF5FFE
    tst.l d0                                          ; +$07CE : 4A80
    rts                                               ; +$07D0 : 4E75
L_00173A:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$07D2 : 48E77FFA
    movea.l 96(a5),a1                                 ; +$07D6 : 226D0060
    move.l 88(a5),d0                                  ; +$07DA : 202D0058
    addi.l #$0000002C,d0                              ; +$07DE : 06800000002C
    movea.l d0,a0                                     ; +$07E4 : 2040
    movea.l (a5),a2                                   ; +$07E6 : 2455
    movea.l 8(a2),a6                                  ; +$07E8 : 2C6A0008
    jsr -882(a6)                                      ; +$07EC : 4EAEFC8E
    jsr -270(a6)                                      ; +$07F0 : 4EAEFEF2
    move.l #$00000001,d0                              ; +$07F4 : 203C00000001
    bra.w L_00176C                                    ; +$07FA : 60000008
    move.l #$00000000,d0                              ; +$07FE : 203C00000000
L_00176C:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0804 : 4CDF5FFE
    tst.l d0                                          ; +$0808 : 4A80
    rts                                               ; +$080A : 4E75
L_001774:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$080C : 48E77FFA
    tst.l 20(a5)                                      ; +$0810 : 4AAD0014
    beq.w L_00178C                                    ; +$0814 : 6700000E
    movea.l 16(a5),a6                                 ; +$0818 : 2C6D0010
    move.l 20(a5),d1                                  ; +$081C : 222D0014
    jsr -36(a6)                                       ; +$0820 : 4EAEFFDC
L_00178C:
    tst.l 96(a5)                                      ; +$0824 : 4AAD0060
    beq.w L_0017A0                                    ; +$0828 : 6700000E
    movea.l 96(a5),a1                                 ; +$082C : 226D0060
    movea.l $0004.w,a6                                ; +$0830 : 2C780004
    jsr -690(a6)                                      ; +$0834 : 4EAEFD4E
L_0017A0:
    tst.l 24(a5)                                      ; +$0838 : 4AAD0018
    beq.w L_0017B4                                    ; +$083C : 6700000E
    movea.l 24(a5),a1                                 ; +$0840 : 226D0018
    movea.l $0004.w,a6                                ; +$0844 : 2C780004
    jsr -690(a6)                                      ; +$0848 : 4EAEFD4E
L_0017B4:
    tst.l 12(a5)                                      ; +$084C : 4AAD000C
    beq.w L_0017C8                                    ; +$0850 : 6700000E
    movea.l 12(a5),a1                                 ; +$0854 : 226D000C
    movea.l $0004.w,a6                                ; +$0858 : 2C780004
    jsr -690(a6)                                      ; +$085C : 4EAEFD4E
L_0017C8:
    tst.l 16(a5)                                      ; +$0860 : 4AAD0010
    beq.w L_0017DC                                    ; +$0864 : 6700000E
    movea.l 16(a5),a1                                 ; +$0868 : 226D0010
    movea.l $0004.w,a6                                ; +$086C : 2C780004
    jsr -414(a6)                                      ; +$0870 : 4EAEFE62
L_0017DC:
    move.l #$00000001,d0                              ; +$0874 : 203C00000001
    bra.w L_0017EC                                    ; +$087A : 60000008
    move.l #$00000000,d0                              ; +$087E : 203C00000000
L_0017EC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0884 : 4CDF5FFE
    tst.l d0                                          ; +$0888 : 4A80
    rts                                               ; +$088A : 4E75
L_0017F4:
    dc.b "dos.library"
    dc.b $00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 14 : aga pic info --------
Entry_14:
Aga_Pic_Info:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a0                                ; +$0004 : 206D01C8
    move.l d3,d4                                      ; +$0008 : 2803
    move.l (a3)+,d3                                   ; +$000A : 261B
    movea.l d3,a1                                     ; +$000C : 2243
    lea -128(a7),a7                                   ; +$000E : 4FEFFF80
    movea.l a7,a5                                     ; +$0012 : 2A4F
    move.l #$00000000,(a5)                            ; +$0014 : 2ABC00000000
    move.l #$00000000,4(a5)                           ; +$001A : 2B7C000000000004
    move.l #$00000000,8(a5)                           ; +$0022 : 2B7C000000000008
    move.l #$00000000,12(a5)                          ; +$002A : 2B7C00000000000C
    move.l #$00000000,16(a5)                          ; +$0032 : 2B7C000000000010
    move.l #$00000000,20(a5)                          ; +$003A : 2B7C000000000014
    move.l #$00000000,24(a5)                          ; +$0042 : 2B7C000000000018
    move.l #$00000000,28(a5)                          ; +$004A : 2B7C00000000001C
    move.l #$00000000,32(a5)                          ; +$0052 : 2B7C000000000020
    move.l #$00000000,36(a5)                          ; +$005A : 2B7C000000000024
    move.l #$00000000,40(a5)                          ; +$0062 : 2B7C000000000028
    move.l #$00000000,44(a5)                          ; +$006A : 2B7C00000000002C
    move.l #$00000000,48(a5)                          ; +$0072 : 2B7C000000000030
    move.l #$00000000,52(a5)                          ; +$007A : 2B7C000000000034
    move.l #$00000000,56(a5)                          ; +$0082 : 2B7C000000000038
    move.l #$00000000,60(a5)                          ; +$008A : 2B7C00000000003C
    move.l #$00000000,64(a5)                          ; +$0092 : 2B7C000000000040
    move.l #$00000000,68(a5)                          ; +$009A : 2B7C000000000044
    move.l #$00000000,72(a5)                          ; +$00A2 : 2B7C000000000048
    move.l #$00000000,76(a5)                          ; +$00AA : 2B7C00000000004C
    move.l #$00000000,80(a5)                          ; +$00B2 : 2B7C000000000050
    move.l #$00000000,84(a5)                          ; +$00BA : 2B7C000000000054
    move.l #$00000000,88(a5)                          ; +$00C2 : 2B7C000000000058
    move.l #$00000000,92(a5)                          ; +$00CA : 2B7C00000000005C
    move.l #$00000000,96(a5)                          ; +$00D2 : 2B7C000000000060
    move.l #$00000000,100(a5)                         ; +$00DA : 2B7C000000000064
    move.l #$00000000,104(a5)                         ; +$00E2 : 2B7C000000000068
    move.l #$00000000,108(a5)                         ; +$00EA : 2B7C00000000006C
    move.l #$00000000,112(a5)                         ; +$00F2 : 2B7C000000000070
    move.l #$00000000,116(a5)                         ; +$00FA : 2B7C000000000074
    move.l #$00000000,120(a5)                         ; +$0102 : 2B7C000000000078
    move.l #$00000000,124(a5)                         ; +$010A : 2B7C00000000007C
    move.l a0,(a5)                                    ; +$0112 : 2A88
    move.l a1,4(a5)                                   ; +$0114 : 2B490004
    move.l d4,8(a5)                                   ; +$0118 : 2B440008
    cmpi.l #$00000007,8(a5)                           ; +$011C : 0CAD000000070008
    bhi.w L_0019E2                                    ; +$0124 : 620000B8
    bsr.w L_0019F8                                    ; +$0128 : 610000CA
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_0019E2                                    ; +$012E : 670000AE
    bsr.w L_001B26                                    ; +$0132 : 610001EE
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_0019E2                                    ; +$0138 : 670000A4
    cmpi.l #$00000000,8(a5)                           ; +$013C : 0CAD000000000008
    beq.w L_0019AA                                    ; +$0144 : 67000060
    cmpi.l #$00000001,8(a5)                           ; +$0148 : 0CAD000000010008
    beq.w L_0019B2                                    ; +$0150 : 6700005C
    cmpi.l #$00000002,8(a5)                           ; +$0154 : 0CAD000000020008
    beq.w L_0019BA                                    ; +$015C : 67000058
    cmpi.l #$00000003,8(a5)                           ; +$0160 : 0CAD000000030008
    beq.w L_0019C2                                    ; +$0168 : 67000054
    cmpi.l #$00000004,8(a5)                           ; +$016C : 0CAD000000040008
    beq.w L_0019CA                                    ; +$0174 : 67000050
    cmpi.l #$00000005,8(a5)                           ; +$0178 : 0CAD000000050008
    beq.w L_0019D2                                    ; +$0180 : 6700004C
    cmpi.l #$00000006,8(a5)                           ; +$0184 : 0CAD000000060008
    beq.w L_0019DA                                    ; +$018C : 67000048
    move.l #$00000001,d3                              ; +$0190 : 263C00000001
    move.l 64(a5),d0                                  ; +$0196 : 202D0040
L_00199E:
    lsl.l #1,d3                                       ; +$019A : E38B
    subq.l #1,d0                                      ; +$019C : 5380
    bne.w L_00199E                                    ; +$019E : 6600FFFA
    bra.w L_0019E8                                    ; +$01A2 : 60000040
L_0019AA:
    move.l 56(a5),d3                                  ; +$01A6 : 262D0038
    bra.w L_0019E8                                    ; +$01AA : 60000038
L_0019B2:
    move.l 60(a5),d3                                  ; +$01AE : 262D003C
    bra.w L_0019E8                                    ; +$01B2 : 60000030
L_0019BA:
    move.l 64(a5),d3                                  ; +$01B6 : 262D0040
    bra.w L_0019E8                                    ; +$01BA : 60000028
L_0019C2:
    move.l 40(a5),d3                                  ; +$01BE : 262D0028
    bra.w L_0019E8                                    ; +$01C2 : 60000020
L_0019CA:
    move.l 72(a5),d3                                  ; +$01C6 : 262D0048
    bra.w L_0019E8                                    ; +$01CA : 60000018
L_0019D2:
    move.l 92(a5),d3                                  ; +$01CE : 262D005C
    bra.w L_0019E8                                    ; +$01D2 : 60000010
L_0019DA:
    move.l 52(a5),d3                                  ; +$01D6 : 262D0034
    bra.w L_0019E8                                    ; +$01DA : 60000008
L_0019E2:
    move.l #$FFFFFFFF,d3                              ; +$01DE : 263CFFFFFFFF
L_0019E8:
    bsr.w L_001D7E                                    ; +$01E4 : 61000394
    lea 128(a7),a7                                    ; +$01E8 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01EC : 4CDF77F7
    moveq #0,d2                                       ; +$01F0 : 7400
    rts                                               ; +$01F2 : 4E75
L_0019F8:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$01F4 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$01F8 : 246D0004
    move.l #$00000000,d4                              ; +$01FC : 283C00000000
    move.w (a2)+,d4                                   ; +$0202 : 381A
    tst.l d4                                          ; +$0204 : 4A84
    beq.w L_001B18                                    ; +$0206 : 6700010C
    move.l d4,d0                                      ; +$020A : 2004
    addq.l #1,d0                                      ; +$020C : 5280
    move.l #$00010001,d1                              ; +$020E : 223C00010001
    movea.l $0004.w,a6                                ; +$0214 : 2C780004
    jsr -684(a6)                                      ; +$0218 : 4EAEFD54
    tst.l d0                                          ; +$021C : 4A80
    beq.w L_001B18                                    ; +$021E : 670000F4
    move.l d0,12(a5)                                  ; +$0222 : 2B40000C
    movea.l d0,a1                                     ; +$0226 : 2240
L_001A2C:
    move.b (a2)+,(a1)+                                ; +$0228 : 12DA
    subq.l #1,d4                                      ; +$022A : 5384
    bne.w L_001A2C                                    ; +$022C : 6600FFFA
    lea L_001DFE(pc),a1                               ; +$0230 : 43FA03C8
    move.l #$00000000,d0                              ; +$0234 : 203C00000000
    movea.l $0004.w,a6                                ; +$023A : 2C780004
    jsr -552(a6)                                      ; +$023E : 4EAEFDD8
    tst.l d0                                          ; +$0242 : 4A80
    beq.w L_001B18                                    ; +$0244 : 670000CE
    move.l d0,16(a5)                                  ; +$0248 : 2B400010
    movea.l d0,a6                                     ; +$024C : 2C40
    move.l 12(a5),d1                                  ; +$024E : 222D000C
    move.l #$000003ED,d2                              ; +$0252 : 243C000003ED
    jsr -30(a6)                                       ; +$0258 : 4EAEFFE2
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_001B18                                    ; +$025E : 670000B4
    move.l d0,20(a5)                                  ; +$0262 : 2B400014
    move.l d0,d1                                      ; +$0266 : 2200
    move.l a5,d2                                      ; +$0268 : 240D
    addi.l #$00000068,d2                              ; +$026A : 068200000068
    move.l #$0000000C,d3                              ; +$0270 : 263C0000000C
    jsr -42(a6)                                       ; +$0276 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$027A : 0C800000000C
    bne.w L_001B18                                    ; +$0280 : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0284 : 0CAD464F524D0068
    bne.w L_001B18                                    ; +$028C : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$0290 : 0CAD494C424D0070
    bne.w L_001B18                                    ; +$0298 : 6600007A
    move.l 108(a5),d4                                 ; +$029C : 282D006C
    cmpi.l #$00000004,d4                              ; +$02A0 : 0C8400000004
    bcs.w L_001B18                                    ; +$02A6 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$02AA : 0C847FFFFFF7
    bhi.w L_001B18                                    ; +$02B0 : 62000062
    addq.l #8,d4                                      ; +$02B4 : 5084
    move.l d4,28(a5)                                  ; +$02B6 : 2B44001C
    move.l d4,d0                                      ; +$02BA : 2004
    move.l #$00010001,d1                              ; +$02BC : 223C00010001
    movea.l $0004.w,a6                                ; +$02C2 : 2C780004
    jsr -684(a6)                                      ; +$02C6 : 4EAEFD54
    tst.l d0                                          ; +$02CA : 4A80
    beq.w L_001B18                                    ; +$02CC : 67000046
    move.l d0,24(a5)                                  ; +$02D0 : 2B400018
    movea.l d0,a2                                     ; +$02D4 : 2440
    move.l 104(a5),(a2)                               ; +$02D6 : 24AD0068
    move.l 108(a5),4(a2)                              ; +$02DA : 256D006C0004
    move.l 112(a5),8(a2)                              ; +$02E0 : 256D00700008
    move.l 20(a5),d1                                  ; +$02E6 : 222D0014
    move.l a2,d2                                      ; +$02EA : 240A
    addi.l #$0000000C,d2                              ; +$02EC : 06820000000C
    move.l d4,d3                                      ; +$02F2 : 2604
    subi.l #$0000000C,d3                              ; +$02F4 : 04830000000C
    move.l d3,d4                                      ; +$02FA : 2803
    movea.l 16(a5),a6                                 ; +$02FC : 2C6D0010
    jsr -42(a6)                                       ; +$0300 : 4EAEFFD6
    cmp.l d4,d0                                       ; +$0304 : B084
    bne.w L_001B18                                    ; +$0306 : 6600000C
    move.l #$00000001,d0                              ; +$030A : 203C00000001
    bra.w L_001B1E                                    ; +$0310 : 60000008
L_001B18:
    move.l #$00000000,d0                              ; +$0314 : 203C00000000
L_001B1E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$031A : 4CDF5FFE
    tst.l d0                                          ; +$031E : 4A80
    rts                                               ; +$0320 : 4E75
L_001B26:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0322 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$0326 : 206D0018
    move.l 28(a5),d7                                  ; +$032A : 2E2D001C
    subi.l #$0000000C,d7                              ; +$032E : 04870000000C
    move.l a0,d0                                      ; +$0334 : 2008
    addi.l #$0000000C,d0                              ; +$0336 : 06800000000C
    movea.l d0,a0                                     ; +$033C : 2040
L_001B42:
    tst.l d7                                          ; +$033E : 4A87
    beq.w L_001C06                                    ; +$0340 : 670000C0
    cmpi.l #$00000008,d7                              ; +$0344 : 0C8700000008
    bcs.w L_001D70                                    ; +$034A : 65000220
    move.l (a0)+,d3                                   ; +$034E : 2618
    move.l (a0)+,d2                                   ; +$0350 : 2418
    subq.l #8,d7                                      ; +$0352 : 5187
    cmp.l d7,d2                                       ; +$0354 : B487
    bhi.w L_001D70                                    ; +$0356 : 62000214
    move.l d2,d1                                      ; +$035A : 2202
    andi.l #$00000001,d1                              ; +$035C : 028100000001
    add.l d2,d1                                       ; +$0362 : D282
    cmp.l d7,d1                                       ; +$0364 : B287
    bhi.w L_001D70                                    ; +$0366 : 62000204
    sub.l d1,d7                                       ; +$036A : 9E81
    cmpi.l #$424D4844,d3                              ; +$036C : 0C83424D4844
    beq.w L_001B9C                                    ; +$0372 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0376 : 0C83434D4150
    beq.w L_001BB6                                    ; +$037C : 67000034
    cmpi.l #$43414D47,d3                              ; +$0380 : 0C8343414D47
    beq.w L_001BDE                                    ; +$0386 : 67000052
    cmpi.l #$424F4459,d3                              ; +$038A : 0C83424F4459
    beq.w L_001BCA                                    ; +$0390 : 67000034
    bra.w L_001BFC                                    ; +$0394 : 60000062
L_001B9C:
    tst.l 32(a5)                                      ; +$0398 : 4AAD0020
    bne.w L_001D70                                    ; +$039C : 660001CE
    cmpi.l #$00000014,d2                              ; +$03A0 : 0C8200000014
    bne.w L_001D70                                    ; +$03A6 : 660001C4
    move.l a0,32(a5)                                  ; +$03AA : 2B480020
    bra.w L_001BFC                                    ; +$03AE : 60000048
L_001BB6:
    tst.l 36(a5)                                      ; +$03B2 : 4AAD0024
    bne.w L_001D70                                    ; +$03B6 : 660001B4
    move.l a0,36(a5)                                  ; +$03BA : 2B480024
    move.l d2,40(a5)                                  ; +$03BE : 2B420028
    bra.w L_001BFC                                    ; +$03C2 : 60000034
L_001BCA:
    tst.l 44(a5)                                      ; +$03C6 : 4AAD002C
    bne.w L_001D70                                    ; +$03CA : 660001A0
    move.l a0,44(a5)                                  ; +$03CE : 2B48002C
    move.l d2,48(a5)                                  ; +$03D2 : 2B420030
    bra.w L_001BFC                                    ; +$03D6 : 60000020
L_001BDE:
    tst.l 52(a5)                                      ; +$03DA : 4AAD0034
    bne.w L_001D70                                    ; +$03DE : 6600018C
    cmpi.l #$00000004,d2                              ; +$03E2 : 0C8200000004
    bne.w L_001D70                                    ; +$03E8 : 66000182
    move.l #$00000001,52(a5)                          ; +$03EC : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$03F4 : 2B50005C
L_001BFC:
    move.l a0,d0                                      ; +$03F8 : 2008
    add.l d1,d0                                       ; +$03FA : D081
    movea.l d0,a0                                     ; +$03FC : 2040
    bra.w L_001B42                                    ; +$03FE : 6000FF3E
L_001C06:
    tst.l 32(a5)                                      ; +$0402 : 4AAD0020
    beq.w L_001D70                                    ; +$0406 : 67000164
    tst.l 36(a5)                                      ; +$040A : 4AAD0024
    beq.w L_001D70                                    ; +$040E : 6700015C
    tst.l 44(a5)                                      ; +$0412 : 4AAD002C
    beq.w L_001D70                                    ; +$0416 : 67000154
    tst.l 48(a5)                                      ; +$041A : 4AAD0030
    beq.w L_001D70                                    ; +$041E : 6700014C
    movea.l 32(a5),a0                                 ; +$0422 : 206D0020
    move.l #$00000000,d0                              ; +$0426 : 203C00000000
    move.w (a0),d0                                    ; +$042C : 3010
    move.l d0,56(a5)                                  ; +$042E : 2B400038
    move.l #$00000000,d0                              ; +$0432 : 203C00000000
    move.w 2(a0),d0                                   ; +$0438 : 30280002
    move.l d0,60(a5)                                  ; +$043C : 2B40003C
    move.l #$00000000,d0                              ; +$0440 : 203C00000000
    move.b 8(a0),d0                                   ; +$0446 : 10280008
    move.l d0,64(a5)                                  ; +$044A : 2B400040
    move.l #$00000000,d0                              ; +$044E : 203C00000000
    move.b 9(a0),d0                                   ; +$0454 : 10280009
    move.l d0,68(a5)                                  ; +$0458 : 2B400044
    move.l #$00000000,d0                              ; +$045C : 203C00000000
    move.b 10(a0),d0                                  ; +$0462 : 1028000A
    move.l d0,72(a5)                                  ; +$0466 : 2B400048
    tst.l 56(a5)                                      ; +$046A : 4AAD0038
    beq.w L_001D70                                    ; +$046E : 670000FC
    tst.l 60(a5)                                      ; +$0472 : 4AAD003C
    beq.w L_001D70                                    ; +$0476 : 670000F4
    tst.l 64(a5)                                      ; +$047A : 4AAD0040
    beq.w L_001D70                                    ; +$047E : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0482 : 0CAD000000080040
    bhi.w L_001D70                                    ; +$048A : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$048E : 0CAD000000020044
    bhi.w L_001D70                                    ; +$0496 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$049A : 0CAD000000010048
    bhi.w L_001D70                                    ; +$04A2 : 620000C8
    move.l 40(a5),d0                                  ; +$04A6 : 202D0028
    tst.l d0                                          ; +$04AA : 4A80
    beq.w L_001D70                                    ; +$04AC : 670000BE
    cmpi.l #$00000300,d0                              ; +$04B0 : 0C8000000300
    bhi.w L_001D70                                    ; +$04B6 : 620000B4
    divu.w #$0003,d0                                  ; +$04BA : 80FC0003
    move.l d0,d1                                      ; +$04BE : 2200
    swap d1                                           ; +$04C0 : 4841
    tst.w d1                                          ; +$04C2 : 4A41
    bne.w L_001D70                                    ; +$04C4 : 660000A6
    andi.l #$0000FFFF,d0                              ; +$04C8 : 02800000FFFF
    move.l d0,40(a5)                                  ; +$04CE : 2B400028
    move.l 56(a5),d0                                  ; +$04D2 : 202D0038
    addi.l #$0000000F,d0                              ; +$04D6 : 06800000000F
    lsr.l #4,d0                                       ; +$04DC : E888
    lsl.l #1,d0                                       ; +$04DE : E388
    move.l d0,76(a5)                                  ; +$04E0 : 2B40004C
    move.l 92(a5),d0                                  ; +$04E4 : 202D005C
    move.l d0,d1                                      ; +$04E8 : 2200
    andi.l #$FFFF0000,d1                              ; +$04EA : 0281FFFF0000
    bne.w L_001D02                                    ; +$04F0 : 6600000C
    andi.l #$00008EFD,d0                              ; +$04F4 : 028000008EFD
    bra.w L_001D0E                                    ; +$04FA : 6000000E
L_001D02:
    move.l d0,d1                                      ; +$04FE : 2200
    andi.l #$00001000,d1                              ; +$0500 : 028100001000
    beq.w L_001D70                                    ; +$0506 : 67000064
L_001D0E:
    move.l d0,52(a5)                                  ; +$050A : 2B400034
    move.l d0,d1                                      ; +$050E : 2200
    andi.l #$00000400,d1                              ; +$0510 : 028100000400
    bne.w L_001D70                                    ; +$0516 : 66000054
    move.l d0,d1                                      ; +$051A : 2200
    andi.l #$00000800,d1                              ; +$051C : 028100000800
    beq.w L_001D50                                    ; +$0522 : 67000028
    andi.l #$00000080,d0                              ; +$0526 : 028000000080
    bne.w L_001D70                                    ; +$052C : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$0530 : 0CAD000000060040
    beq.w L_001D4C                                    ; +$0538 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$053C : 0CAD000000080040
    bne.w L_001D70                                    ; +$0544 : 66000026
L_001D4C:
    bra.w L_001D66                                    ; +$0548 : 60000018
L_001D50:
    andi.l #$00000080,d0                              ; +$054C : 028000000080
    beq.w L_001D66                                    ; +$0552 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$0556 : 0CAD000000060040
    bne.w L_001D70                                    ; +$055E : 6600000C
L_001D66:
    move.l #$00000001,d0                              ; +$0562 : 203C00000001
    bra.w L_001D76                                    ; +$0568 : 60000008
L_001D70:
    move.l #$00000000,d0                              ; +$056C : 203C00000000
L_001D76:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0572 : 4CDF5FFE
    tst.l d0                                          ; +$0576 : 4A80
    rts                                               ; +$0578 : 4E75
L_001D7E:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$057A : 48E77FFA
    tst.l 20(a5)                                      ; +$057E : 4AAD0014
    beq.w L_001D96                                    ; +$0582 : 6700000E
    movea.l 16(a5),a6                                 ; +$0586 : 2C6D0010
    move.l 20(a5),d1                                  ; +$058A : 222D0014
    jsr -36(a6)                                       ; +$058E : 4EAEFFDC
L_001D96:
    tst.l 96(a5)                                      ; +$0592 : 4AAD0060
    beq.w L_001DAA                                    ; +$0596 : 6700000E
    movea.l 96(a5),a1                                 ; +$059A : 226D0060
    movea.l $0004.w,a6                                ; +$059E : 2C780004
    jsr -690(a6)                                      ; +$05A2 : 4EAEFD4E
L_001DAA:
    tst.l 24(a5)                                      ; +$05A6 : 4AAD0018
    beq.w L_001DBE                                    ; +$05AA : 6700000E
    movea.l 24(a5),a1                                 ; +$05AE : 226D0018
    movea.l $0004.w,a6                                ; +$05B2 : 2C780004
    jsr -690(a6)                                      ; +$05B6 : 4EAEFD4E
L_001DBE:
    tst.l 12(a5)                                      ; +$05BA : 4AAD000C
    beq.w L_001DD2                                    ; +$05BE : 6700000E
    movea.l 12(a5),a1                                 ; +$05C2 : 226D000C
    movea.l $0004.w,a6                                ; +$05C6 : 2C780004
    jsr -690(a6)                                      ; +$05CA : 4EAEFD4E
L_001DD2:
    tst.l 16(a5)                                      ; +$05CE : 4AAD0010
    beq.w L_001DE6                                    ; +$05D2 : 6700000E
    movea.l 16(a5),a1                                 ; +$05D6 : 226D0010
    movea.l $0004.w,a6                                ; +$05DA : 2C780004
    jsr -414(a6)                                      ; +$05DE : 4EAEFE62
L_001DE6:
    move.l #$00000001,d0                              ; +$05E2 : 203C00000001
    bra.w L_001DF6                                    ; +$05E8 : 60000008
    move.l #$00000000,d0                              ; +$05EC : 203C00000000
L_001DF6:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$05F2 : 4CDF5FFE
    tst.l d0                                          ; +$05F6 : 4A80
    rts                                               ; +$05F8 : 4E75
L_001DFE:
    dc.b "dos.library"
    dc.b $00

; -------- AP20 entry 15 : private/reserved --------
Entry_15:
Internal_15:
    cmpi.l #$00000100,d7                              ; +$0000 : 0C8700000100
    beq.w L_001E3E                                    ; +$0006 : 6700002C
    lea -20(a7),a7                                    ; +$000A : 4FEFFFEC
    move.l d0,d6                                      ; +$000E : 2C00
    ori.l #$00010000,d6                               ; +$0010 : 008600010000
    movea.l a7,a1                                     ; +$0016 : 224F
    move.l d6,(a1)                                    ; +$0018 : 2286
    move.l d1,4(a1)                                   ; +$001A : 23410004
    move.l d2,8(a1)                                   ; +$001E : 23420008
    move.l d3,12(a1)                                  ; +$0022 : 2343000C
    clr.l 16(a1)                                      ; +$0026 : 42A90010
    jsr -882(a6)                                      ; +$002A : 4EAEFC8E
    lea 20(a7),a7                                     ; +$002E : 4FEF0014
    rts                                               ; +$0032 : 4E75
L_001E3E:
    jsr -852(a6)                                      ; +$0034 : 4EAEFCAC
    rts                                               ; +$0038 : 4E75

; -------- AP20 entry 16 : private/reserved --------
Entry_16:

; -------- AP20 entry 17 : aga key --------
Entry_17:
Aga_Key:
    movem.l d0-d1/d4-d7/a0-a4/a6,-(a7)                ; +$0000 : 48E7CFFA
    moveq #-1,d3                                      ; +$0004 : 76FF
    movea.l 456(a5),a2                                ; +$0006 : 246D01C8
    move.l a2,d0                                      ; +$000A : 200A
    tst.l d0                                          ; +$000C : 4A80
    beq.w L_00201E                                    ; +$000E : 670001CA
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_00201E                                    ; +$001A : 670001BE
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_00201E                                    ; +$0026 : 670001B2
L_001E6E:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_0031E2                                    ; +$0030 : 6100136C
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_00201E                                    ; +$0036 : 670001A2
    movea.l d0,a3                                     ; +$003A : 2640
    move.l 20(a3),d4                                  ; +$003C : 282B0014
    moveq #0,d5                                       ; +$0040 : 7A00
    move.w 24(a3),d5                                  ; +$0042 : 3A2B0018
    moveq #0,d6                                       ; +$0046 : 7C00
    move.w 26(a3),d6                                  ; +$0048 : 3C2B001A
    movea.l a3,a1                                     ; +$004C : 224B
    nop                                               ; +$004E : 4E71
    nop                                               ; +$0050 : 4E71
    cmpi.l #$00000400,d4                              ; +$0052 : 0C8400000400
    bne.w L_001E6E                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_001E6E                                    ; +$0064 : 6600FFC4
    cmpi.l #$00000033,d5                              ; +$0068 : 0C8500000033
    bne.w L_002018                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_002018                                    ; +$007A : 67000158
    bra.w L_002040                                    ; +$007E : 6000017C
L_001EC6:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_002026                                    ; +$0088 : 60000158
L_001ED0:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_001F1C                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_001F02                                    ; +$00A0 : 6700001C
L_001EE8:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_001F02                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_001EE8                                    ; +$00BA : 6000FFE8
L_001F02:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_001F14                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    jsr -72(a6)                                       ; +$00CC : 4EAEFFB8
L_001F14:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_001F1C:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_001F9C                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_001F38                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_001F38:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_001F66                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_001F56                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_001F56:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_001F66                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_001F66:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_001F7A                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_001F7A:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_001F8A                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_001F8A:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_001F9C:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_001FB4                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_001FB4:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_001FD0                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_001FD0:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_001FEC                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_001FEC:
    moveq #0,d0                                       ; +$01A8 : 7000
    move.l d0,(a2)                                    ; +$01AA : 2480
    move.l d0,4(a2)                                   ; +$01AC : 25400004
    move.l d0,8(a2)                                   ; +$01B0 : 25400008
    move.l d0,12(a2)                                  ; +$01B4 : 2540000C
    move.l d0,16(a2)                                  ; +$01B8 : 25400010
    move.l d0,20(a2)                                  ; +$01BC : 25400014
    move.l d0,24(a2)                                  ; +$01C0 : 25400018
    move.l d0,28(a2)                                  ; +$01C4 : 2540001C
    move.l d0,32(a2)                                  ; +$01C8 : 25400020
    move.l d0,36(a2)                                  ; +$01CC : 25400024
    bra.w L_001EC6                                    ; +$01D0 : 6000FEB0
L_002018:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_00201E                                    ; +$01D6 : 60000002
L_00201E:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01DA : 4CDF5FF3
    moveq #0,d2                                       ; +$01DE : 7400
    rts                                               ; +$01E0 : 4E75
L_002026:
    moveq #1,d1                                       ; +$01E2 : 7201
    movea.l -8(a5),a0                                 ; +$01E4 : 206DFFF8
    jsr 288(a0)                                       ; +$01E8 : 4EA80120
    move.l d5,d3                                      ; +$01EC : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$01FA : 4E75
L_002040:
    bsr.w L_002052                                    ; +$01FC : 61000010
    tst.l d0                                          ; +$0200 : 4A80
    beq.w L_00204E                                    ; +$0202 : 67000006
    bra.w L_001ED0                                    ; +$0206 : 6000FE84
L_00204E:
    bra.w L_00201E                                    ; +$020A : 6000FFCE
L_002052:
    movea.l 32(a2),a4                                 ; +$020E : 286A0020
    move.l a4,d0                                      ; +$0212 : 200C
    tst.l d0                                          ; +$0214 : 4A80
    beq.w L_00208A                                    ; +$0216 : 6700002E
    moveq #0,d4                                       ; +$021A : 7800
L_002060:
    bsr.w L_002092                                    ; +$021C : 61000030
    tst.l d0                                          ; +$0220 : 4A80
    beq.w L_00208A                                    ; +$0222 : 67000022
    addq.l #1,d4                                      ; +$0226 : 5284
    cmpi.l #$0000012D,d4                              ; +$0228 : 0C840000012D
    bge.w L_00208E                                    ; +$022E : 6C00001A
    movea.l 8(a2),a6                                  ; +$0232 : 2C6A0008
    move.l a6,d0                                      ; +$0236 : 200E
    tst.l d0                                          ; +$0238 : 4A80
    beq.w L_00208E                                    ; +$023A : 6700000E
    jsr -270(a6)                                      ; +$023E : 4EAEFEF2
    bra.w L_002060                                    ; +$0242 : 6000FFD8
L_00208A:
    moveq #1,d0                                       ; +$0246 : 7001
    rts                                               ; +$0248 : 4E75
L_00208E:
    moveq #0,d0                                       ; +$024A : 7000
    rts                                               ; +$024C : 4E75
L_002092:
    move.l 20(a4),d6                                  ; +$024E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0252 : 028600000003
    btst #0,d6                                        ; +$0258 : 08060000
    beq.w L_0020C2                                    ; +$025C : 67000020
    movea.l 12(a4),a0                                 ; +$0260 : 206C000C
    move.l a0,d0                                      ; +$0264 : 2008
    tst.l d0                                          ; +$0266 : 4A80
    beq.w L_0020C2                                    ; +$0268 : 67000014
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -372(a6)                                      ; +$0270 : 4EAEFE8C
    tst.l d0                                          ; +$0274 : 4A80
    beq.w L_0020C2                                    ; +$0276 : 67000006
    bclr #0,d6                                        ; +$027A : 08860000
L_0020C2:
    btst #1,d6                                        ; +$027E : 08060001
    beq.w L_0020E8                                    ; +$0282 : 67000020
    movea.l 16(a4),a0                                 ; +$0286 : 206C0010
    move.l a0,d0                                      ; +$028A : 2008
    tst.l d0                                          ; +$028C : 4A80
    beq.w L_0020E8                                    ; +$028E : 67000014
    movea.l $0004.w,a6                                ; +$0292 : 2C780004
    jsr -372(a6)                                      ; +$0296 : 4EAEFE8C
    tst.l d0                                          ; +$029A : 4A80
    beq.w L_0020E8                                    ; +$029C : 67000006
    bclr #1,d6                                        ; +$02A0 : 08860001
L_0020E8:
    move.l d6,20(a4)                                  ; +$02A4 : 29460014
    move.l d6,d0                                      ; +$02A8 : 2006
    rts                                               ; +$02AA : 4E75

; -------- AP20 entry 18 : aga wait key --------
Entry_18:
Aga_Wait_Key:
    movem.l d0-d1/d4-d7/a0-a4/a6,-(a7)                ; +$0000 : 48E7CFFA
    moveq #-1,d3                                      ; +$0004 : 76FF
    movea.l 456(a5),a2                                ; +$0006 : 246D01C8
    move.l a2,d0                                      ; +$000A : 200A
    tst.l d0                                          ; +$000C : 4A80
    beq.w L_0022DE                                    ; +$000E : 670001DE
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_0022DE                                    ; +$001A : 670001D2
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0022DE                                    ; +$0026 : 670001C6
L_00211A:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_0031E2                                    ; +$0030 : 610010C0
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_0022CA                                    ; +$0036 : 670001A2
    movea.l d0,a3                                     ; +$003A : 2640
    move.l 20(a3),d4                                  ; +$003C : 282B0014
    moveq #0,d5                                       ; +$0040 : 7A00
    move.w 24(a3),d5                                  ; +$0042 : 3A2B0018
    moveq #0,d6                                       ; +$0046 : 7C00
    move.w 26(a3),d6                                  ; +$0048 : 3C2B001A
    movea.l a3,a1                                     ; +$004C : 224B
    nop                                               ; +$004E : 4E71
    nop                                               ; +$0050 : 4E71
    cmpi.l #$00000400,d4                              ; +$0052 : 0C8400000400
    bne.w L_00211A                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_00211A                                    ; +$0064 : 6600FFC4
    bra.w L_0022E6                                    ; +$0068 : 6000018C
    nop                                               ; +$006C : 4E71
L_00215E:
    bne.w L_0022C4                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_0022C4                                    ; +$007A : 67000158
    bra.w L_002314                                    ; +$007E : 600001A4
L_002172:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_0022FA                                    ; +$0088 : 60000180
L_00217C:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_0021C8                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_0021AE                                    ; +$00A0 : 6700001C
L_002194:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_0021AE                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_002194                                    ; +$00BA : 6000FFE8
L_0021AE:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_0021C0                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    jsr -72(a6)                                       ; +$00CC : 4EAEFFB8
L_0021C0:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_0021C8:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_002248                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_0021E4                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_0021E4:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_002212                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_002202                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_002202:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_002212                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_002212:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_002226                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_002226:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_002236                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_002236:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_002248:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_002260                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_002260:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_00227C                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_00227C:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_002298                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_002298:
    moveq #0,d0                                       ; +$01A8 : 7000
    move.l d0,(a2)                                    ; +$01AA : 2480
    move.l d0,4(a2)                                   ; +$01AC : 25400004
    move.l d0,8(a2)                                   ; +$01B0 : 25400008
    move.l d0,12(a2)                                  ; +$01B4 : 2540000C
    move.l d0,16(a2)                                  ; +$01B8 : 25400010
    move.l d0,20(a2)                                  ; +$01BC : 25400014
    move.l d0,24(a2)                                  ; +$01C0 : 25400018
    move.l d0,28(a2)                                  ; +$01C4 : 2540001C
    move.l d0,32(a2)                                  ; +$01C8 : 25400020
    move.l d0,36(a2)                                  ; +$01CC : 25400024
    bra.w L_002172                                    ; +$01D0 : 6000FEB0
L_0022C4:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_0022DE                                    ; +$01D6 : 60000016
L_0022CA:
    movea.l 8(a2),a6                                  ; +$01DA : 2C6A0008
    move.l a6,d0                                      ; +$01DE : 200E
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_0022DE                                    ; +$01E2 : 6700000A
    jsr -270(a6)                                      ; +$01E6 : 4EAEFEF2
    bra.w L_00211A                                    ; +$01EA : 6000FE3E
L_0022DE:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    rts                                               ; +$01F4 : 4E75
L_0022E6:
    cmpi.l #$00000063,d5                              ; +$01F6 : 0C8500000063
    beq.w L_00211A                                    ; +$01FC : 6700FE2C
    cmpi.l #$00000033,d5                              ; +$0200 : 0C8500000033
    bra.w L_00215E                                    ; +$0206 : 6000FE66
L_0022FA:
    moveq #1,d1                                       ; +$020A : 7201
    movea.l -8(a5),a0                                 ; +$020C : 206DFFF8
    jsr 288(a0)                                       ; +$0210 : 4EA80120
    move.l d5,d3                                      ; +$0214 : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$0216 : 4CDF5FF3
    moveq #0,d2                                       ; +$021A : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$0222 : 4E75
L_002314:
    bsr.w L_002326                                    ; +$0224 : 61000010
    tst.l d0                                          ; +$0228 : 4A80
    beq.w L_002322                                    ; +$022A : 67000006
    bra.w L_00217C                                    ; +$022E : 6000FE5C
L_002322:
    bra.w L_0022DE                                    ; +$0232 : 6000FFBA
L_002326:
    movea.l 32(a2),a4                                 ; +$0236 : 286A0020
    move.l a4,d0                                      ; +$023A : 200C
    tst.l d0                                          ; +$023C : 4A80
    beq.w L_00235E                                    ; +$023E : 6700002E
    moveq #0,d4                                       ; +$0242 : 7800
L_002334:
    bsr.w L_002366                                    ; +$0244 : 61000030
    tst.l d0                                          ; +$0248 : 4A80
    beq.w L_00235E                                    ; +$024A : 67000022
    addq.l #1,d4                                      ; +$024E : 5284
    cmpi.l #$0000012D,d4                              ; +$0250 : 0C840000012D
    bge.w L_002362                                    ; +$0256 : 6C00001A
    movea.l 8(a2),a6                                  ; +$025A : 2C6A0008
    move.l a6,d0                                      ; +$025E : 200E
    tst.l d0                                          ; +$0260 : 4A80
    beq.w L_002362                                    ; +$0262 : 6700000E
    jsr -270(a6)                                      ; +$0266 : 4EAEFEF2
    bra.w L_002334                                    ; +$026A : 6000FFD8
L_00235E:
    moveq #1,d0                                       ; +$026E : 7001
    rts                                               ; +$0270 : 4E75
L_002362:
    moveq #0,d0                                       ; +$0272 : 7000
    rts                                               ; +$0274 : 4E75
L_002366:
    move.l 20(a4),d6                                  ; +$0276 : 2C2C0014
    andi.l #$00000003,d6                              ; +$027A : 028600000003
    btst #0,d6                                        ; +$0280 : 08060000
    beq.w L_002396                                    ; +$0284 : 67000020
    movea.l 12(a4),a0                                 ; +$0288 : 206C000C
    move.l a0,d0                                      ; +$028C : 2008
    tst.l d0                                          ; +$028E : 4A80
    beq.w L_002396                                    ; +$0290 : 67000014
    movea.l $0004.w,a6                                ; +$0294 : 2C780004
    jsr -372(a6)                                      ; +$0298 : 4EAEFE8C
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_002396                                    ; +$029E : 67000006
    bclr #0,d6                                        ; +$02A2 : 08860000
L_002396:
    btst #1,d6                                        ; +$02A6 : 08060001
    beq.w L_0023BC                                    ; +$02AA : 67000020
    movea.l 16(a4),a0                                 ; +$02AE : 206C0010
    move.l a0,d0                                      ; +$02B2 : 2008
    tst.l d0                                          ; +$02B4 : 4A80
    beq.w L_0023BC                                    ; +$02B6 : 67000014
    movea.l $0004.w,a6                                ; +$02BA : 2C780004
    jsr -372(a6)                                      ; +$02BE : 4EAEFE8C
    tst.l d0                                          ; +$02C2 : 4A80
    beq.w L_0023BC                                    ; +$02C4 : 67000006
    bclr #1,d6                                        ; +$02C8 : 08860001
L_0023BC:
    move.l d6,20(a4)                                  ; +$02CC : 29460014
    move.l d6,d0                                      ; +$02D0 : 2006
    rts                                               ; +$02D2 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 19 : aga blit copy --------
Entry_19:
Aga_Blit_Copy:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l (a3)+,d3                                   ; +$0008 : 261B
    move.l (a3)+,d2                                   ; +$000A : 241B
    move.l (a3)+,d1                                   ; +$000C : 221B
    move.l (a3)+,d0                                   ; +$000E : 201B
    movea.l 456(a5),a4                                ; +$0010 : 286D01C8
    move.l a4,d6                                      ; +$0014 : 2C0C
    tst.l d6                                          ; +$0016 : 4A86
    beq.w L_002516                                    ; +$0018 : 67000134
    move.l (a4),d6                                    ; +$001C : 2C14
    tst.l d6                                          ; +$001E : 4A86
    beq.w L_002516                                    ; +$0020 : 6700012C
    movea.l 32(a4),a2                                 ; +$0024 : 246C0020
    move.l a2,d6                                      ; +$0028 : 2C0A
    tst.l d6                                          ; +$002A : 4A86
    beq.w L_002516                                    ; +$002C : 67000120
    movea.l 8(a4),a6                                  ; +$0030 : 2C6C0008
    move.l a6,d6                                      ; +$0034 : 2C0E
    tst.l d6                                          ; +$0036 : 4A86
    beq.w L_002516                                    ; +$0038 : 67000114
    tst.l d0                                          ; +$003C : 4A80
    bmi.w L_002516                                    ; +$003E : 6B00010E
    tst.l d1                                          ; +$0042 : 4A81
    bmi.w L_002516                                    ; +$0044 : 6B000108
    tst.l d2                                          ; +$0048 : 4A82
    bmi.w L_002516                                    ; +$004A : 6B000102
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_002516                                    ; +$0050 : 6B0000FC
    tst.l d4                                          ; +$0054 : 4A84
    ble.w L_002516                                    ; +$0056 : 6F0000F6
    tst.l d5                                          ; +$005A : 4A85
    ble.w L_002516                                    ; +$005C : 6F0000F0
    move.l 12(a4),d6                                  ; +$0060 : 2C2C000C
    tst.l d6                                          ; +$0064 : 4A86
    ble.w L_002516                                    ; +$0066 : 6F0000E6
    cmpi.l #$00007FFF,d6                              ; +$006A : 0C8600007FFF
    bgt.w L_002516                                    ; +$0070 : 6E0000DC
    move.l 16(a4),d6                                  ; +$0074 : 2C2C0010
    tst.l d6                                          ; +$0078 : 4A86
    ble.w L_002516                                    ; +$007A : 6F0000D2
    cmpi.l #$00007FFF,d6                              ; +$007E : 0C8600007FFF
    bgt.w L_002516                                    ; +$0084 : 6E0000C8
    move.l 12(a4),d6                                  ; +$0088 : 2C2C000C
    sub.l d4,d6                                       ; +$008C : 9C84
    tst.l d6                                          ; +$008E : 4A86
    bmi.w L_002516                                    ; +$0090 : 6B0000BC
    cmp.l d6,d0                                       ; +$0094 : B086
    bgt.w L_002516                                    ; +$0096 : 6E0000B6
    cmp.l d6,d2                                       ; +$009A : B486
    bgt.w L_002516                                    ; +$009C : 6E0000B0
    move.l 16(a4),d6                                  ; +$00A0 : 2C2C0010
    sub.l d5,d6                                       ; +$00A4 : 9C85
    tst.l d6                                          ; +$00A6 : 4A86
    bmi.w L_002516                                    ; +$00A8 : 6B0000A4
    cmp.l d6,d1                                       ; +$00AC : B286
    bgt.w L_002516                                    ; +$00AE : 6E00009E
    cmp.l d6,d3                                       ; +$00B2 : B686
    bgt.w L_002516                                    ; +$00B4 : 6E000098
    tst.l 8(a2)                                       ; +$00B8 : 4AAA0008
    beq.w L_00248E                                    ; +$00BC : 67000008
    movea.l (a2),a0                                   ; +$00C0 : 2052
    bra.w L_002492                                    ; +$00C2 : 60000006
L_00248E:
    movea.l 4(a2),a0                                  ; +$00C6 : 206A0004
L_002492:
    move.l a0,d6                                      ; +$00CA : 2C08
    tst.l d6                                          ; +$00CC : 4A86
    beq.w L_002516                                    ; +$00CE : 6700007E
    movea.l (a0),a0                                   ; +$00D2 : 2050
    move.l a0,d6                                      ; +$00D4 : 2C08
    tst.l d6                                          ; +$00D6 : 4A86
    beq.w L_002516                                    ; +$00D8 : 67000074
    move.l #$00000000,d6                              ; +$00DC : 2C3C00000000
    move.w (a0),d6                                    ; +$00E2 : 3C10
    lsl.l #3,d6                                       ; +$00E4 : E78E
    cmp.l 12(a4),d6                                   ; +$00E6 : BCAC000C
    blt.w L_002516                                    ; +$00EA : 6D000062
    move.l #$00000000,d6                              ; +$00EE : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00F4 : 3C280002
    cmp.l 16(a4),d6                                   ; +$00F8 : BCAC0010
    blt.w L_002516                                    ; +$00FC : 6D000050
    move.l #$00000000,d6                              ; +$0100 : 2C3C00000000
    move.b 5(a0),d6                                   ; +$0106 : 1C280005
    cmp.l 28(a4),d6                                   ; +$010A : BCAC001C
    bne.w L_002516                                    ; +$010E : 6600003E
    tst.l d6                                          ; +$0112 : 4A86
    ble.w L_002516                                    ; +$0114 : 6F000038
    cmpi.l #$00000008,d6                              ; +$0118 : 0C8600000008
    bgt.w L_002516                                    ; +$011E : 6E00002E
    movea.l a0,a1                                     ; +$0122 : 2248
    movea.l #$00000000,a2                             ; +$0124 : 247C00000000
    move.l #$000000C0,d6                              ; +$012A : 2C3C000000C0
    move.l #$000000FF,d7                              ; +$0130 : 2E3C000000FF
    jsr -30(a6)                                       ; +$0136 : 4EAEFFE2
    tst.l d0                                          ; +$013A : 4A80
    beq.w L_002516                                    ; +$013C : 67000010
    jsr -228(a6)                                      ; +$0140 : 4EAEFF1C
    move.l #$00000001,d3                              ; +$0144 : 263C00000001
    bra.w L_00251C                                    ; +$014A : 60000008
L_002516:
    move.l #$00000000,d3                              ; +$014E : 263C00000000
L_00251C:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0154 : 4CDF77F7
    moveq #0,d2                                       ; +$0158 : 7400
    rts                                               ; +$015A : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 20 : aga blit fill --------
Entry_20:
Aga_Blit_Fill:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l (a3)+,d5                                   ; +$0004 : 2A1B
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l (a3)+,d1                                   ; +$0008 : 221B
    move.l (a3)+,d0                                   ; +$000A : 201B
    movea.l 456(a5),a4                                ; +$000C : 286D01C8
    move.l a4,d6                                      ; +$0010 : 2C0C
    tst.l d6                                          ; +$0012 : 4A86
    beq.w L_0026D6                                    ; +$0014 : 67000198
    move.l (a4),d6                                    ; +$0018 : 2C14
    tst.l d6                                          ; +$001A : 4A86
    beq.w L_0026D6                                    ; +$001C : 67000190
    movea.l 32(a4),a2                                 ; +$0020 : 246C0020
    move.l a2,d6                                      ; +$0024 : 2C0A
    tst.l d6                                          ; +$0026 : 4A86
    beq.w L_0026D6                                    ; +$0028 : 67000184
    movea.l 8(a4),a6                                  ; +$002C : 2C6C0008
    move.l a6,d6                                      ; +$0030 : 2C0E
    tst.l d6                                          ; +$0032 : 4A86
    beq.w L_0026D6                                    ; +$0034 : 67000178
    tst.l d0                                          ; +$0038 : 4A80
    bmi.w L_0026D6                                    ; +$003A : 6B000172
    tst.l d1                                          ; +$003E : 4A81
    bmi.w L_0026D6                                    ; +$0040 : 6B00016C
    tst.l d3                                          ; +$0044 : 4A83
    bmi.w L_0026D6                                    ; +$0046 : 6B000166
    tst.l d4                                          ; +$004A : 4A84
    ble.w L_0026D6                                    ; +$004C : 6F000160
    tst.l d5                                          ; +$0050 : 4A85
    ble.w L_0026D6                                    ; +$0052 : 6F00015A
    move.l 12(a4),d6                                  ; +$0056 : 2C2C000C
    tst.l d6                                          ; +$005A : 4A86
    ble.w L_0026D6                                    ; +$005C : 6F000150
    cmpi.l #$00007FFF,d6                              ; +$0060 : 0C8600007FFF
    bgt.w L_0026D6                                    ; +$0066 : 6E000146
    move.l 16(a4),d6                                  ; +$006A : 2C2C0010
    tst.l d6                                          ; +$006E : 4A86
    ble.w L_0026D6                                    ; +$0070 : 6F00013C
    cmpi.l #$00007FFF,d6                              ; +$0074 : 0C8600007FFF
    bgt.w L_0026D6                                    ; +$007A : 6E000132
    move.l 12(a4),d6                                  ; +$007E : 2C2C000C
    sub.l d4,d6                                       ; +$0082 : 9C84
    tst.l d6                                          ; +$0084 : 4A86
    bmi.w L_0026D6                                    ; +$0086 : 6B000126
    cmp.l d6,d0                                       ; +$008A : B086
    bgt.w L_0026D6                                    ; +$008C : 6E000120
    move.l 16(a4),d6                                  ; +$0090 : 2C2C0010
    sub.l d5,d6                                       ; +$0094 : 9C85
    tst.l d6                                          ; +$0096 : 4A86
    bmi.w L_0026D6                                    ; +$0098 : 6B000114
    cmp.l d6,d1                                       ; +$009C : B286
    bgt.w L_0026D6                                    ; +$009E : 6E00010E
    tst.l 8(a2)                                       ; +$00A2 : 4AAA0008
    beq.w L_0025D8                                    ; +$00A6 : 67000008
    movea.l (a2),a0                                   ; +$00AA : 2052
    bra.w L_0025DC                                    ; +$00AC : 60000006
L_0025D8:
    movea.l 4(a2),a0                                  ; +$00B0 : 206A0004
L_0025DC:
    move.l a0,d6                                      ; +$00B4 : 2C08
    tst.l d6                                          ; +$00B6 : 4A86
    beq.w L_0026D6                                    ; +$00B8 : 670000F4
    movea.l (a0),a0                                   ; +$00BC : 2050
    move.l a0,d6                                      ; +$00BE : 2C08
    tst.l d6                                          ; +$00C0 : 4A86
    beq.w L_0026D6                                    ; +$00C2 : 670000EA
    move.l #$00000000,d6                              ; +$00C6 : 2C3C00000000
    move.w (a0),d6                                    ; +$00CC : 3C10
    lsl.l #3,d6                                       ; +$00CE : E78E
    cmp.l 12(a4),d6                                   ; +$00D0 : BCAC000C
    blt.w L_0026D6                                    ; +$00D4 : 6D0000D8
    move.l #$00000000,d6                              ; +$00D8 : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00DE : 3C280002
    cmp.l 16(a4),d6                                   ; +$00E2 : BCAC0010
    blt.w L_0026D6                                    ; +$00E6 : 6D0000C6
    move.l #$00000000,d6                              ; +$00EA : 2C3C00000000
    move.b 5(a0),d6                                   ; +$00F0 : 1C280005
    cmp.l 28(a4),d6                                   ; +$00F4 : BCAC001C
    bne.w L_0026D6                                    ; +$00F8 : 660000B4
    tst.l d6                                          ; +$00FC : 4A86
    ble.w L_0026D6                                    ; +$00FE : 6F0000AE
    cmpi.l #$00000008,d6                              ; +$0102 : 0C8600000008
    bgt.w L_0026D6                                    ; +$0108 : 6E0000A4
    move.l d6,d2                                      ; +$010C : 2406
    movea.l a0,a1                                     ; +$010E : 2248
    addq.l #8,a1                                      ; +$0110 : 5089
L_00263A:
    move.l (a1)+,d6                                   ; +$0112 : 2C19
    tst.l d6                                          ; +$0114 : 4A86
    beq.w L_0026D6                                    ; +$0116 : 67000096
    cmpi.l #$FFFFFFFF,d6                              ; +$011A : 0C86FFFFFFFF
    beq.w L_0026D6                                    ; +$0120 : 6700008C
    subq.l #1,d2                                      ; +$0124 : 5382
    bne.w L_00263A                                    ; +$0126 : 6600FFEA
    move.l #$00000000,d2                              ; +$012A : 243C00000000
    move.b 5(a0),d2                                   ; +$0130 : 14280005
    move.l #$00000001,d6                              ; +$0134 : 2C3C00000001
L_002662:
    lsl.l #1,d6                                       ; +$013A : E38E
    subq.l #1,d2                                      ; +$013C : 5382
    bne.w L_002662                                    ; +$013E : 6600FFFA
    cmp.l d6,d3                                       ; +$0142 : B686
    bcc.w L_0026D6                                    ; +$0144 : 64000068
    move.l d3,-(a7)                                   ; +$0148 : 2F03
    move.l d6,-(a7)                                   ; +$014A : 2F06
    movea.l a0,a4                                     ; +$014C : 2848
    move.l d0,d2                                      ; +$014E : 2400
    move.l d1,d3                                      ; +$0150 : 2601
    move.l #$00000001,d7                              ; +$0152 : 2E3C00000001
L_002680:
    move.l 4(a7),d6                                   ; +$0158 : 2C2F0004
    and.l d7,d6                                       ; +$015C : CC87
    tst.l d6                                          ; +$015E : 4A86
    beq.w L_002696                                    ; +$0160 : 6700000C
    move.l #$000000F0,d6                              ; +$0164 : 2C3C000000F0
    bra.w L_00269C                                    ; +$016A : 60000008
L_002696:
    move.l #$00000000,d6                              ; +$016E : 2C3C00000000
L_00269C:
    move.l d2,d0                                      ; +$0174 : 2002
    move.l d3,d1                                      ; +$0176 : 2203
    movea.l a4,a0                                     ; +$0178 : 204C
    movea.l a4,a1                                     ; +$017A : 224C
    movea.l #$00000000,a2                             ; +$017C : 247C00000000
    jsr -30(a6)                                       ; +$0182 : 4EAEFFE2
    tst.l d0                                          ; +$0186 : 4A80
    beq.w L_0026CA                                    ; +$0188 : 67000018
    jsr -228(a6)                                      ; +$018C : 4EAEFF1C
    lsl.l #1,d7                                       ; +$0190 : E38F
    cmp.l (a7),d7                                     ; +$0192 : BE97
    bne.w L_002680                                    ; +$0194 : 6600FFC2
    move.l #$00000001,d3                              ; +$0198 : 263C00000001
    bra.w L_0026D0                                    ; +$019E : 60000008
L_0026CA:
    move.l #$00000000,d3                              ; +$01A2 : 263C00000000
L_0026D0:
    addq.l #8,a7                                      ; +$01A8 : 508F
    bra.w L_0026DC                                    ; +$01AA : 60000008
L_0026D6:
    move.l #$00000000,d3                              ; +$01AE : 263C00000000
L_0026DC:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01B4 : 4CDF77F7
    moveq #0,d2                                       ; +$01B8 : 7400
    rts                                               ; +$01BA : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 21 : aga blit clear --------
Entry_21:
Aga_Blit_Clear:
    move.l a3,-(a7)                                   ; +$0000 : 2F0B
    move.l 8(a3),-(a7)                                ; +$0002 : 2F2B0008
    move.l 4(a3),-(a7)                                ; +$0006 : 2F2B0004
    move.l (a3),-(a7)                                 ; +$000A : 2F13
    move.l d3,-(a7)                                   ; +$000C : 2F03
    movea.l a7,a3                                     ; +$000E : 264F
    move.l #$00000000,d3                              ; +$0010 : 263C00000000
    bsr.w Aga_Blit_Fill                               ; +$0016 : 6100FE28
    addq.l #8,a7                                      ; +$001A : 508F
    addq.l #8,a7                                      ; +$001C : 508F
    movea.l (a7)+,a3                                  ; +$001E : 265F
    addq.l #8,a3                                      ; +$0020 : 508B
    addq.l #4,a3                                      ; +$0022 : 588B
    rts                                               ; +$0024 : 4E75

; -------- AP20 entry 22 : aga copper clear --------
Entry_22:
Aga_Copper_Clear:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a4                                ; +$0004 : 286D01C8
    move.l a4,d0                                      ; +$0008 : 200C
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_0027E2                                    ; +$000C : 670000C6
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0027E2                                    ; +$0016 : 670000BC
    move.l 342(a4),d0                                 ; +$001A : 202C0156
    tst.l d0                                          ; +$001E : 4A80
    bne.w L_0027A6                                    ; +$0020 : 66000076
    move.l 64(a4),d0                                  ; +$0024 : 202C0040
    tst.l d0                                          ; +$0028 : 4A80
    bne.w L_0027E2                                    ; +$002A : 660000A8
    movea.l 456(a5),a0                                ; +$002E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0032 : 2C680008
    move.l a6,d0                                      ; +$0036 : 200E
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_0027E2                                    ; +$003A : 67000098
    movea.l $0004.w,a6                                ; +$003E : 2C780004
    move.l #$0000000C,d0                              ; +$0042 : 203C0000000C
    move.l #$00010001,d1                              ; +$0048 : 223C00010001
    jsr -198(a6)                                      ; +$004E : 4EAEFF3A
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0027E2                                    ; +$0054 : 6700007E
    movea.l d0,a2                                     ; +$0058 : 2440
    movea.l 456(a5),a0                                ; +$005A : 206D01C8
    movea.l 8(a0),a6                                  ; +$005E : 2C680008
    movea.l a2,a0                                     ; +$0062 : 204A
    move.l #$00000040,d0                              ; +$0064 : 203C00000040
    jsr -594(a6)                                      ; +$006A : 4EAEFDAE
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_0027B4                                    ; +$0070 : 67000034
    movea.l a2,a1                                     ; +$0074 : 224A
    move.l #$00002710,d0                              ; +$0076 : 203C00002710
    move.l #$000000FF,d1                              ; +$007C : 223C000000FF
    jsr -378(a6)                                      ; +$0082 : 4EAEFE86
    movea.l a2,a1                                     ; +$0086 : 224A
    jsr -366(a6)                                      ; +$0088 : 4EAEFE92
    move.l a2,342(a4)                                 ; +$008C : 294A0156
    move.l a2,64(a4)                                  ; +$0090 : 294A0040
    bra.w L_0027D8                                    ; +$0094 : 60000034
L_0027A6:
    move.l 64(a4),d1                                  ; +$0098 : 222C0040
    cmp.l d1,d0                                       ; +$009C : B081
    beq.w L_0027D8                                    ; +$009E : 6700002A
    bra.w L_0027E2                                    ; +$00A2 : 60000030
L_0027B4:
    movea.l 4(a2),a0                                  ; +$00A6 : 206A0004
    move.l a0,d0                                      ; +$00AA : 2008
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_0027C4                                    ; +$00AE : 67000006
    jsr -546(a6)                                      ; +$00B2 : 4EAEFDDE
L_0027C4:
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    movea.l a2,a1                                     ; +$00BA : 224A
    move.l #$0000000C,d0                              ; +$00BC : 203C0000000C
    jsr -210(a6)                                      ; +$00C2 : 4EAEFF2E
    bra.w L_0027E2                                    ; +$00C6 : 6000000C
L_0027D8:
    move.l #$00000001,d3                              ; +$00CA : 263C00000001
    bra.w L_0027E8                                    ; +$00D0 : 60000008
L_0027E2:
    move.l #$00000000,d3                              ; +$00D4 : 263C00000000
L_0027E8:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00DA : 4CDF77F7
    moveq #0,d2                                       ; +$00DE : 7400
    rts                                               ; +$00E0 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 23 : aga copper on --------
Entry_23:
Aga_Copper_On:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a4                                ; +$0004 : 286D01C8
    move.l a4,d0                                      ; +$0008 : 200C
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_00288E                                    ; +$000C : 6700008C
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00288E                                    ; +$0016 : 67000082
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_00288E                                    ; +$002A : 6700006E
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_00288E                                    ; +$0034 : 66000064
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_00288E                                    ; +$0044 : 67000054
    movea.l 8(a2),a1                                  ; +$0048 : 226A0008
    move.l a1,d0                                      ; +$004C : 2009
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_00288E                                    ; +$0050 : 67000048
    move.w 28(a1),d0                                  ; +$0054 : 3029001C
    cmpi.w #$0001,d0                                  ; +$0058 : 0C400001
    beq.w L_002862                                    ; +$005C : 67000010
    move.l d6,d0                                      ; +$0060 : 2006
    andi.l #$00000002,d0                              ; +$0062 : 028000000002
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_00288E                                    ; +$006A : 6700002E
L_002862:
    ori.l #$00000001,342(a4)                          ; +$006E : 00AC000000010156
    movea.l a4,a0                                     ; +$0076 : 204C
    jsr -378(a6)                                      ; +$0078 : 4EAEFE86
    tst.l d0                                          ; +$007C : 4A80
    bne.w L_00288E                                    ; +$007E : 6600001A
    jsr -390(a6)                                      ; +$0082 : 4EAEFE7A
    tst.l d0                                          ; +$0086 : 4A80
    bne.w L_00288E                                    ; +$0088 : 66000010
    bra.w L_002884                                    ; +$008C : 60000002
L_002884:
    move.l #$00000001,d3                              ; +$0090 : 263C00000001
    bra.w L_002894                                    ; +$0096 : 60000008
L_00288E:
    move.l #$00000000,d3                              ; +$009A : 263C00000000
L_002894:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00A0 : 4CDF77F7
    moveq #0,d2                                       ; +$00A4 : 7400
    rts                                               ; +$00A6 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 24 : aga copper off --------
Entry_24:
Aga_Copper_Off:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a4                                ; +$0004 : 286D01C8
    move.l a4,d0                                      ; +$0008 : 200C
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_00297E                                    ; +$000C : 670000D0
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00297E                                    ; +$0016 : 670000C6
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_00294C                                    ; +$002A : 67000080
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_00297E                                    ; +$0034 : 660000A8
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_00297E                                    ; +$0044 : 67000098
    movea.l 456(a5),a0                                ; +$0048 : 206D01C8
    move.l 8(a0),d0                                   ; +$004C : 20280008
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_00297E                                    ; +$0052 : 6700008A
    move.l #$00000000,64(a4)                          ; +$0056 : 297C000000000040
    movea.l a4,a0                                     ; +$005E : 204C
    jsr -378(a6)                                      ; +$0060 : 4EAEFE86
    tst.l d0                                          ; +$0064 : 4A80
    bne.w L_00295A                                    ; +$0066 : 66000052
    jsr -390(a6)                                      ; +$006A : 4EAEFE7A
    tst.l d0                                          ; +$006E : 4A80
    bne.w L_002962                                    ; +$0070 : 66000050
    movea.l 456(a5),a0                                ; +$0074 : 206D01C8
    movea.l 8(a0),a6                                  ; +$0078 : 2C680008
    jsr -270(a6)                                      ; +$007C : 4EAEFEF2
    movea.l 4(a2),a0                                  ; +$0080 : 206A0004
    move.l a0,d0                                      ; +$0084 : 2008
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_002930                                    ; +$0088 : 67000006
    jsr -546(a6)                                      ; +$008C : 4EAEFDDE
L_002930:
    move.l #$00000000,342(a4)                         ; +$0090 : 297C000000000156
    movea.l $0004.w,a6                                ; +$0098 : 2C780004
    movea.l a2,a1                                     ; +$009C : 224A
    move.l #$0000000C,d0                              ; +$009E : 203C0000000C
    jsr -210(a6)                                      ; +$00A4 : 4EAEFF2E
    bra.w L_002974                                    ; +$00A8 : 6000002A
L_00294C:
    move.l 64(a4),d0                                  ; +$00AC : 202C0040
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_002974                                    ; +$00B2 : 67000020
    bra.w L_00297E                                    ; +$00B6 : 60000026
L_00295A:
    move.l a2,64(a4)                                  ; +$00BA : 294A0040
    bra.w L_00297E                                    ; +$00BE : 6000001E
L_002962:
    move.l a2,64(a4)                                  ; +$00C2 : 294A0040
    movea.l a4,a0                                     ; +$00C6 : 204C
    jsr -378(a6)                                      ; +$00C8 : 4EAEFE86
    jsr -390(a6)                                      ; +$00CC : 4EAEFE7A
    bra.w L_00297E                                    ; +$00D0 : 6000000C
L_002974:
    move.l #$00000001,d3                              ; +$00D4 : 263C00000001
    bra.w L_002984                                    ; +$00DA : 60000008
L_00297E:
    move.l #$00000000,d3                              ; +$00DE : 263C00000000
L_002984:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00E4 : 4CDF77F7
    moveq #0,d2                                       ; +$00E8 : 7400
    rts                                               ; +$00EA : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 25 : aga copper wait --------
Entry_25:
Aga_Copper_Wait:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    movea.l 456(a5),a4                                ; +$0008 : 286D01C8
    move.l a4,d0                                      ; +$000C : 200C
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_002AEC                                    ; +$0010 : 6700014A
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002AEC                                    ; +$001A : 67000140
    cmpi.l #$000000FF,d4                              ; +$001E : 0C84000000FF
    bhi.w L_002AEC                                    ; +$0024 : 62000136
    cmpi.l #$000000DE,d5                              ; +$0028 : 0C85000000DE
    bhi.w L_002AEC                                    ; +$002E : 6200012C
    move.l 342(a4),d6                                 ; +$0032 : 2C2C0156
    move.l d6,d0                                      ; +$0036 : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0038 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$003E : 2440
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_002AEC                                    ; +$0042 : 67000118
    move.l 64(a4),d1                                  ; +$0046 : 222C0040
    cmp.l d1,d0                                       ; +$004A : B081
    bne.w L_002AEC                                    ; +$004C : 6600010E
    move.l d6,d0                                      ; +$0050 : 2006
    andi.l #$00000003,d0                              ; +$0052 : 028000000003
    tst.l d0                                          ; +$0058 : 4A80
    bne.w L_002AEC                                    ; +$005A : 66000100
    movea.l 456(a5),a0                                ; +$005E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0062 : 2C680008
    move.l a6,d0                                      ; +$0066 : 200E
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_002AEC                                    ; +$006A : 670000F0
    movea.l 8(a2),a1                                  ; +$006E : 226A0008
    move.l a1,d0                                      ; +$0072 : 2009
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_002AEC                                    ; +$0076 : 670000E4
    move.l 12(a1),d0                                  ; +$007A : 2029000C
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_002AEC                                    ; +$0080 : 670000DA
    movea.l 16(a1),a0                                 ; +$0084 : 20690010
    move.l a0,d0                                      ; +$0088 : 2008
    tst.l d0                                          ; +$008A : 4A80
    beq.w L_002AEC                                    ; +$008C : 670000CE
    move.w 30(a1),d0                                  ; +$0090 : 3029001E
    cmpi.w #$0040,d0                                  ; +$0094 : 0C400040
    bne.w L_002AEC                                    ; +$0098 : 660000C2
    move.w 28(a1),d7                                  ; +$009C : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00A0 : 0C470000
    bls.w L_002AEC                                    ; +$00A4 : 630000B6
    cmpi.w #$003F,d7                                  ; +$00A8 : 0C47003F
    bcc.w L_002AEC                                    ; +$00AC : 640000AE
    movea.l 16(a1),a0                                 ; +$00B0 : 20690010
    subq.l #6,a0                                      ; +$00B4 : 5D88
    move.w (a0),d0                                    ; +$00B6 : 3010
    cmpi.w #$0001,d0                                  ; +$00B8 : 0C400001
    bne.w L_002AEC                                    ; +$00BC : 6600009E
    move.w 2(a0),d0                                   ; +$00C0 : 30280002
    cmpi.w #$2710,d0                                  ; +$00C4 : 0C402710
    bne.w L_002AEC                                    ; +$00C8 : 66000092
    move.w 4(a0),d0                                   ; +$00CC : 30280004
    cmpi.w #$00FF,d0                                  ; +$00D0 : 0C4000FF
    bne.w L_002AEC                                    ; +$00D4 : 66000086
    move.w d7,d6                                      ; +$00D8 : 3C07
    subq.w #1,d6                                      ; +$00DA : 5346
    beq.w L_002AA8                                    ; +$00DC : 6700003A
    movea.l 16(a1),a0                                 ; +$00E0 : 20690010
    subq.l #6,a0                                      ; +$00E4 : 5D88
L_002A76:
    subq.l #6,a0                                      ; +$00E6 : 5D88
    move.w (a0),d0                                    ; +$00E8 : 3010
    cmpi.w #$0001,d0                                  ; +$00EA : 0C400001
    beq.w L_002A8C                                    ; +$00EE : 6700000C
    subq.w #1,d6                                      ; +$00F2 : 5346
    bne.w L_002A76                                    ; +$00F4 : 6600FFF0
    bra.w L_002AA8                                    ; +$00F8 : 6000001E
L_002A8C:
    move.w 2(a0),d0                                   ; +$00FC : 30280002
    move.w d4,d1                                      ; +$0100 : 3204
    cmp.w d0,d1                                       ; +$0102 : B240
    bhi.w L_002AA8                                    ; +$0104 : 62000012
    bne.w L_002AEC                                    ; +$0108 : 66000052
    move.w 4(a0),d0                                   ; +$010C : 30280004
    move.w d5,d1                                      ; +$0110 : 3205
    cmp.w d0,d1                                       ; +$0112 : B240
    bls.w L_002AEC                                    ; +$0114 : 63000046
L_002AA8:
    movea.l 16(a1),a0                                 ; +$0118 : 20690010
    subq.l #6,a0                                      ; +$011C : 5D88
    move.l a0,16(a1)                                  ; +$011E : 23480010
    subq.w #1,28(a1)                                  ; +$0122 : 5369001C
    movea.l a2,a1                                     ; +$0126 : 224A
    move.l d4,d0                                      ; +$0128 : 2004
    move.l d5,d1                                      ; +$012A : 2205
    jsr -378(a6)                                      ; +$012C : 4EAEFE86
    movea.l a2,a1                                     ; +$0130 : 224A
    jsr -366(a6)                                      ; +$0132 : 4EAEFE92
    movea.l a2,a1                                     ; +$0136 : 224A
    move.l #$00002710,d0                              ; +$0138 : 203C00002710
    move.l #$000000FF,d1                              ; +$013E : 223C000000FF
    jsr -378(a6)                                      ; +$0144 : 4EAEFE86
    movea.l a2,a1                                     ; +$0148 : 224A
    jsr -366(a6)                                      ; +$014A : 4EAEFE92
    bra.w L_002AE2                                    ; +$014E : 60000002
L_002AE2:
    move.l #$00000001,d3                              ; +$0152 : 263C00000001
    bra.w L_002AF2                                    ; +$0158 : 60000008
L_002AEC:
    move.l #$00000000,d3                              ; +$015C : 263C00000000
L_002AF2:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0162 : 4CDF77F7
    moveq #0,d2                                       ; +$0166 : 7400
    rts                                               ; +$0168 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 26 : aga copper move --------
Entry_26:
Aga_Copper_Move:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    movea.l 456(a5),a4                                ; +$0008 : 286D01C8
    move.l a4,d0                                      ; +$000C : 200C
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_002C38                                    ; +$0010 : 67000128
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002C38                                    ; +$001A : 6700011E
    cmpi.l #$00000180,d4                              ; +$001E : 0C8400000180
    bcs.w L_002C38                                    ; +$0024 : 65000114
    cmpi.l #$000001BE,d4                              ; +$0028 : 0C84000001BE
    bhi.w L_002C38                                    ; +$002E : 6200010A
    move.l d4,d0                                      ; +$0032 : 2004
    andi.l #$00000001,d0                              ; +$0034 : 028000000001
    tst.l d0                                          ; +$003A : 4A80
    bne.w L_002C38                                    ; +$003C : 660000FC
    cmpi.l #$00000FFF,d5                              ; +$0040 : 0C8500000FFF
    bhi.w L_002C38                                    ; +$0046 : 620000F2
    move.l 342(a4),d6                                 ; +$004A : 2C2C0156
    move.l d6,d0                                      ; +$004E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0050 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0056 : 2440
    tst.l d0                                          ; +$0058 : 4A80
    beq.w L_002C38                                    ; +$005A : 670000DE
    move.l 64(a4),d1                                  ; +$005E : 222C0040
    cmp.l d1,d0                                       ; +$0062 : B081
    bne.w L_002C38                                    ; +$0064 : 660000D4
    move.l d6,d0                                      ; +$0068 : 2006
    andi.l #$00000003,d0                              ; +$006A : 028000000003
    tst.l d0                                          ; +$0070 : 4A80
    bne.w L_002C38                                    ; +$0072 : 660000C6
    movea.l 456(a5),a0                                ; +$0076 : 206D01C8
    movea.l 8(a0),a6                                  ; +$007A : 2C680008
    move.l a6,d0                                      ; +$007E : 200E
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_002C38                                    ; +$0082 : 670000B6
    movea.l 8(a2),a1                                  ; +$0086 : 226A0008
    move.l a1,d0                                      ; +$008A : 2009
    tst.l d0                                          ; +$008C : 4A80
    beq.w L_002C38                                    ; +$008E : 670000AA
    move.l 12(a1),d0                                  ; +$0092 : 2029000C
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_002C38                                    ; +$0098 : 670000A0
    movea.l 16(a1),a0                                 ; +$009C : 20690010
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_002C38                                    ; +$00A4 : 67000094
    move.w 30(a1),d0                                  ; +$00A8 : 3029001E
    cmpi.w #$0040,d0                                  ; +$00AC : 0C400040
    bne.w L_002C38                                    ; +$00B0 : 66000088
    move.w 28(a1),d7                                  ; +$00B4 : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00B8 : 0C470000
    bls.w L_002C38                                    ; +$00BC : 6300007C
    cmpi.w #$003F,d7                                  ; +$00C0 : 0C47003F
    bcc.w L_002C38                                    ; +$00C4 : 64000074
    movea.l 16(a1),a0                                 ; +$00C8 : 20690010
    subq.l #6,a0                                      ; +$00CC : 5D88
    move.w (a0),d0                                    ; +$00CE : 3010
    cmpi.w #$0001,d0                                  ; +$00D0 : 0C400001
    bne.w L_002C38                                    ; +$00D4 : 66000064
    move.w 2(a0),d0                                   ; +$00D8 : 30280002
    cmpi.w #$2710,d0                                  ; +$00DC : 0C402710
    bne.w L_002C38                                    ; +$00E0 : 66000058
    move.w 4(a0),d0                                   ; +$00E4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00E8 : 0C4000FF
    bne.w L_002C38                                    ; +$00EC : 6600004C
    movea.l 16(a1),a0                                 ; +$00F0 : 20690010
    subq.l #6,a0                                      ; +$00F4 : 5D88
    move.l a0,16(a1)                                  ; +$00F6 : 23480010
    subq.w #1,28(a1)                                  ; +$00FA : 5369001C
    movea.l a2,a1                                     ; +$00FE : 224A
    move.l d4,d0                                      ; +$0100 : 2004
    addi.l #$00DFF000,d0                              ; +$0102 : 068000DFF000
    move.l d5,d1                                      ; +$0108 : 2205
    jsr -372(a6)                                      ; +$010A : 4EAEFE8C
    movea.l a2,a1                                     ; +$010E : 224A
    jsr -366(a6)                                      ; +$0110 : 4EAEFE92
    movea.l a2,a1                                     ; +$0114 : 224A
    move.l #$00002710,d0                              ; +$0116 : 203C00002710
    move.l #$000000FF,d1                              ; +$011C : 223C000000FF
    jsr -378(a6)                                      ; +$0122 : 4EAEFE86
    movea.l a2,a1                                     ; +$0126 : 224A
    jsr -366(a6)                                      ; +$0128 : 4EAEFE92
    bra.w L_002C2E                                    ; +$012C : 60000002
L_002C2E:
    move.l #$00000001,d3                              ; +$0130 : 263C00000001
    bra.w L_002C3E                                    ; +$0136 : 60000008
L_002C38:
    move.l #$00000000,d3                              ; +$013A : 263C00000000
L_002C3E:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0140 : 4CDF77F7
    moveq #0,d2                                       ; +$0144 : 7400
    rts                                               ; +$0146 : 4E75

; -------- AP20 entry 27 : aga copper end --------
Entry_27:
Aga_Copper_End:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a4                                ; +$0004 : 286D01C8
    move.l a4,d0                                      ; +$0008 : 200C
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002D0C                                    ; +$000C : 670000B8
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002D0C                                    ; +$0016 : 670000AE
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_002D0C                                    ; +$002A : 6700009A
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_002D0C                                    ; +$0034 : 66000090
    move.l d6,d0                                      ; +$0038 : 2006
    andi.l #$00000003,d0                              ; +$003A : 028000000003
    tst.l d0                                          ; +$0040 : 4A80
    bne.w L_002D0C                                    ; +$0042 : 66000082
    movea.l 8(a2),a1                                  ; +$0046 : 226A0008
    move.l a1,d0                                      ; +$004A : 2009
    tst.l d0                                          ; +$004C : 4A80
    beq.w L_002D0C                                    ; +$004E : 67000076
    move.l 12(a1),d0                                  ; +$0052 : 2029000C
    tst.l d0                                          ; +$0056 : 4A80
    beq.w L_002D0C                                    ; +$0058 : 6700006C
    movea.l 16(a1),a0                                 ; +$005C : 20690010
    move.l a0,d0                                      ; +$0060 : 2008
    tst.l d0                                          ; +$0062 : 4A80
    beq.w L_002D0C                                    ; +$0064 : 67000060
    move.w 30(a1),d0                                  ; +$0068 : 3029001E
    cmpi.w #$0040,d0                                  ; +$006C : 0C400040
    bne.w L_002D0C                                    ; +$0070 : 66000054
    move.w 28(a1),d7                                  ; +$0074 : 3E29001C
    cmpi.w #$0001,d7                                  ; +$0078 : 0C470001
    bls.w L_002D0C                                    ; +$007C : 63000048
    cmpi.w #$0040,d7                                  ; +$0080 : 0C470040
    bhi.w L_002D0C                                    ; +$0084 : 62000040
    movea.l 16(a1),a0                                 ; +$0088 : 20690010
    subq.l #6,a0                                      ; +$008C : 5D88
    move.w (a0),d0                                    ; +$008E : 3010
    cmpi.w #$0001,d0                                  ; +$0090 : 0C400001
    bne.w L_002D0C                                    ; +$0094 : 66000030
    move.w 2(a0),d0                                   ; +$0098 : 30280002
    cmpi.w #$2710,d0                                  ; +$009C : 0C402710
    bne.w L_002D0C                                    ; +$00A0 : 66000024
    move.w 4(a0),d0                                   ; +$00A4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00A8 : 0C4000FF
    bne.w L_002D0C                                    ; +$00AC : 66000018
    ori.l #$00000002,342(a4)                          ; +$00B0 : 00AC000000020156
    bra.w L_002D02                                    ; +$00B8 : 60000002
L_002D02:
    move.l #$00000001,d3                              ; +$00BC : 263C00000001
    bra.w L_002D12                                    ; +$00C2 : 60000008
L_002D0C:
    move.l #$00000000,d3                              ; +$00C6 : 263C00000000
L_002D12:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00CC : 4CDF77F7
    moveq #0,d2                                       ; +$00D0 : 7400
    rts                                               ; +$00D2 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 28 : aga mouse x --------
Entry_28:
Aga_Mouse_X:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002D7C                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002D7C                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_002D7C                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_002D7C                                    ; +$002E : 6600002E
    move.l 12(a2),d0                                  ; +$0032 : 202A000C
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_002D7C                                    ; +$0038 : 67000024
    bmi.w L_002D7C                                    ; +$003C : 6B000020
    move.w 14(a1),d3                                  ; +$0040 : 3629000E
    ext.l d3                                          ; +$0044 : 48C3
    move.w 4(a1),d1                                   ; +$0046 : 32290004
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_002D7C                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_002D7C                                    ; +$0056 : 64000006
    bra.w L_002D82                                    ; +$005A : 60000008
L_002D7C:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_002D82:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0064 : 4CDF77F7
    moveq #0,d2                                       ; +$0068 : 7400
    rts                                               ; +$006A : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 29 : aga mouse y --------
Entry_29:
Aga_Mouse_Y:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002DEC                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002DEC                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_002DEC                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_002DEC                                    ; +$002E : 6600002E
    move.l 16(a2),d0                                  ; +$0032 : 202A0010
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_002DEC                                    ; +$0038 : 67000024
    bmi.w L_002DEC                                    ; +$003C : 6B000020
    move.w 12(a1),d3                                  ; +$0040 : 3629000C
    ext.l d3                                          ; +$0044 : 48C3
    move.w 6(a1),d1                                   ; +$0046 : 32290006
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_002DEC                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_002DEC                                    ; +$0056 : 64000006
    bra.w L_002DF2                                    ; +$005A : 60000008
L_002DEC:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_002DF2:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0064 : 4CDF77F7
    moveq #0,d2                                       ; +$0068 : 7400
    rts                                               ; +$006A : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 30 : aga mouse buttons --------
Entry_30:
Aga_Mouse_Buttons:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002ED4                                    ; +$000C : 670000C8
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002ED4                                    ; +$0016 : 670000BE
    movea.l 36(a2),a4                                 ; +$001A : 286A0024
    move.l a4,d0                                      ; +$001E : 200C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_002ED4                                    ; +$0022 : 670000B2
    move.l 46(a4),d0                                  ; +$0026 : 202C002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_002ED4                                    ; +$002E : 660000A6
    lea -48(a7),a7                                    ; +$0032 : 4FEFFFD0
    movea.l a7,a4                                     ; +$0036 : 284F
    movea.l a4,a0                                     ; +$0038 : 204C
    clr.l (a0)+                                       ; +$003A : 4298
    clr.l (a0)+                                       ; +$003C : 4298
    clr.l (a0)+                                       ; +$003E : 4298
    clr.l (a0)+                                       ; +$0040 : 4298
    clr.l (a0)+                                       ; +$0042 : 4298
    clr.l (a0)+                                       ; +$0044 : 4298
    clr.l (a0)+                                       ; +$0046 : 4298
    clr.l (a0)+                                       ; +$0048 : 4298
    clr.l (a0)+                                       ; +$004A : 4298
    clr.l (a0)+                                       ; +$004C : 4298
    clr.l (a0)+                                       ; +$004E : 4298
    clr.l (a0)+                                       ; +$0050 : 4298
    movea.l $0004.w,a6                                ; +$0052 : 2C780004
    lea L_002EE2(pc),a0                               ; +$0056 : 41FA008C
    move.l #$00000000,d0                              ; +$005A : 203C00000000
    movea.l a4,a1                                     ; +$0060 : 224C
    move.l #$00000000,d1                              ; +$0062 : 223C00000000
    jsr -444(a6)                                      ; +$0068 : 4EAEFE44
    tst.l d0                                          ; +$006C : 4A80
    bne.w L_002EC6                                    ; +$006E : 66000058
    movea.l 20(a4),a6                                 ; +$0072 : 2C6C0014
    move.l a6,d0                                      ; +$0076 : 200E
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_002EB2                                    ; +$007A : 67000038
    jsr -42(a6)                                       ; +$007E : 4EAEFFD6
    andi.w #$7000,d0                                  ; +$0082 : 02407000
    move.l #$00000000,d3                              ; +$0086 : 263C00000000
    move.l d0,d1                                      ; +$008C : 2200
    andi.w #$4000,d1                                  ; +$008E : 02414000
    beq.w L_002E96                                    ; +$0092 : 67000004
    addq.l #1,d3                                      ; +$0096 : 5283
L_002E96:
    move.l d0,d1                                      ; +$0098 : 2200
    andi.w #$2000,d1                                  ; +$009A : 02412000
    beq.w L_002EA2                                    ; +$009E : 67000004
    addq.l #2,d3                                      ; +$00A2 : 5483
L_002EA2:
    move.l d0,d1                                      ; +$00A4 : 2200
    andi.w #$1000,d1                                  ; +$00A6 : 02411000
    beq.w L_002EAE                                    ; +$00AA : 67000004
    addq.l #4,d3                                      ; +$00AE : 5883
L_002EAE:
    bra.w L_002EB8                                    ; +$00B0 : 60000008
L_002EB2:
    move.l #$FFFFFFFF,d3                              ; +$00B4 : 263CFFFFFFFF
L_002EB8:
    movea.l $0004.w,a6                                ; +$00BA : 2C780004
    movea.l a4,a1                                     ; +$00BE : 224C
    jsr -450(a6)                                      ; +$00C0 : 4EAEFE3E
    bra.w L_002ECC                                    ; +$00C4 : 60000008
L_002EC6:
    move.l #$FFFFFFFF,d3                              ; +$00C8 : 263CFFFFFFFF
L_002ECC:
    lea 48(a7),a7                                     ; +$00CE : 4FEF0030
    bra.w L_002EDA                                    ; +$00D2 : 60000008
L_002ED4:
    move.l #$FFFFFFFF,d3                              ; +$00D6 : 263CFFFFFFFF
L_002EDA:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00DC : 4CDF77F7
    moveq #0,d2                                       ; +$00E0 : 7400
    rts                                               ; +$00E2 : 4E75
L_002EE2:
    dc.b "input.device"
    dc.b $00,$00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 31 : aga mouse pressed --------
Entry_31:
Aga_Mouse_Pressed:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002F50                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_002F50                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_002F3C                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 610000A8
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_002F50                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11732(a2),a2                                  ; +$0038 : 45EA2DD4
    move.l 4(a2),d3                                   ; +$003C : 262A0004
    clr.l 4(a2)                                       ; +$0040 : 42AA0004
    bra.w L_002F52                                    ; +$0044 : 60000018
L_002F3C:
    lea 11732(a2),a2                                  ; +$0048 : 45EA2DD4
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_002F50:
    moveq #-1,d3                                      ; +$005C : 76FF
L_002F52:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$005E : 4CDF77F7
    moveq #0,d2                                       ; +$0062 : 7400
    rts                                               ; +$0064 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 32 : aga mouse released --------
Entry_32:
Aga_Mouse_Released:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_002FBA                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_002FBA                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_002FA6                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 6100003E
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_002FBA                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11732(a2),a2                                  ; +$0038 : 45EA2DD4
    move.l 8(a2),d3                                   ; +$003C : 262A0008
    clr.l 8(a2)                                       ; +$0040 : 42AA0008
    bra.w L_002FBC                                    ; +$0044 : 60000018
L_002FA6:
    lea 11732(a2),a2                                  ; +$0048 : 45EA2DD4
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_002FBA:
    moveq #-1,d3                                      ; +$005C : 76FF
L_002FBC:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$005E : 4CDF77F7
    moveq #0,d2                                       ; +$0062 : 7400
    rts                                               ; +$0064 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 33 : private/reserved --------
Entry_33:
Internal_33:
    movem.l d1-d7/a0-a6,-(a7)                         ; +$0000 : 48E77FFE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_0031DA                                    ; +$000C : 67000204
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0031DA                                    ; +$0016 : 670001FA
    movea.l 36(a2),a3                                 ; +$001A : 266A0024
    move.l a3,d0                                      ; +$001E : 200B
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0031DA                                    ; +$0022 : 670001EE
    move.l 46(a3),d0                                  ; +$0026 : 202B002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_0031DA                                    ; +$002E : 660001E2
    movea.l 86(a3),a4                                 ; +$0032 : 286B0056
    move.l a4,d0                                      ; +$0036 : 200C
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_0031DA                                    ; +$003A : 670001D6
    lea 11732(a2),a2                                  ; +$003E : 45EA2DD4
    move.l (a2),d0                                    ; +$0042 : 2012
    move.l a3,d1                                      ; +$0044 : 220B
    cmp.l d1,d0                                       ; +$0046 : B081
    beq.w L_00303C                                    ; +$0048 : 6700002A
    move.l a3,(a2)                                    ; +$004C : 248B
    clr.l 4(a2)                                       ; +$004E : 42AA0004
    clr.l 8(a2)                                       ; +$0052 : 42AA0008
    clr.l 12(a2)                                      ; +$0056 : 42AA000C
    clr.l 28(a2)                                      ; +$005A : 42AA001C
    move.l 24(a3),d0                                  ; +$005E : 202B0018
    andi.l #$00002000,d0                              ; +$0062 : 028000002000
    beq.w L_00303C                                    ; +$0068 : 6700000A
    move.l #$00000001,28(a2)                          ; +$006C : 257C00000001001C
L_00303C:
    move.l 24(a3),d0                                  ; +$0074 : 202B0018
    andi.l #$00002000,d0                              ; +$0078 : 028000002000
    bne.w L_00305A                                    ; +$007E : 66000012
    clr.l 4(a2)                                       ; +$0082 : 42AA0004
    clr.l 8(a2)                                       ; +$0086 : 42AA0008
    clr.l 12(a2)                                      ; +$008A : 42AA000C
    clr.l 28(a2)                                      ; +$008E : 42AA001C
L_00305A:
    moveq #63,d7                                      ; +$0092 : 7E3F
L_00305C:
    move.l 24(a2),d0                                  ; +$0094 : 202A0018
    cmpi.l #$00000010,d0                              ; +$0098 : 0C8000000010
    bcc.w L_0031D4                                    ; +$009E : 6400016C
    movea.l a4,a0                                     ; +$00A2 : 204C
    movea.l $0004.w,a6                                ; +$00A4 : 2C780004
    jsr -372(a6)                                      ; +$00A8 : 4EAEFE8C
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_0031D4                                    ; +$00AE : 6700015C
    movea.l d0,a3                                     ; +$00B2 : 2640
    move.l 20(a3),d4                                  ; +$00B4 : 282B0014
    moveq #0,d5                                       ; +$00B8 : 7A00
    move.w 24(a3),d5                                  ; +$00BA : 3A2B0018
    moveq #0,d6                                       ; +$00BE : 7C00
    move.w 26(a3),d6                                  ; +$00C0 : 3C2B001A
    cmpi.l #$00000400,d4                              ; +$00C4 : 0C8400000400
    beq.w L_0030B8                                    ; +$00CA : 67000024
    cmpi.l #$00000008,d4                              ; +$00CE : 0C8400000008
    beq.w L_0030F8                                    ; +$00D4 : 6700005A
    cmpi.l #$00080000,d4                              ; +$00D8 : 0C8400080000
    beq.w L_00318A                                    ; +$00DE : 670000E2
    cmpi.l #$00040000,d4                              ; +$00E2 : 0C8400040000
    beq.w L_00319E                                    ; +$00E8 : 670000EC
    bra.w L_0031C6                                    ; +$00EC : 60000110
L_0030B8:
    move.l d5,d0                                      ; +$00F0 : 2005
    andi.l #$00000080,d0                              ; +$00F2 : 028000000080
    bne.w L_0031C6                                    ; +$00F8 : 66000104
    move.l d5,d0                                      ; +$00FC : 2005
    swap d0                                           ; +$00FE : 4840
    move.w d6,d0                                      ; +$0100 : 3006
    move.l d0,d4                                      ; +$0102 : 2800
    move.l 20(a2),d1                                  ; +$0104 : 222A0014
    add.l d1,d1                                       ; +$0108 : D281
    add.l d1,d1                                       ; +$010A : D281
    lea 80(a2),a0                                     ; +$010C : 41EA0050
    move.l a0,d0                                      ; +$0110 : 2008
    add.l d1,d0                                       ; +$0112 : D081
    movea.l d0,a0                                     ; +$0114 : 2040
    move.l d4,(a0)                                    ; +$0116 : 2084
    move.l 20(a2),d0                                  ; +$0118 : 202A0014
    addq.l #1,d0                                      ; +$011C : 5280
    andi.l #$0000000F,d0                              ; +$011E : 02800000000F
    move.l d0,20(a2)                                  ; +$0124 : 25400014
    addq.l #1,24(a2)                                  ; +$0128 : 52AA0018
    bra.w L_0031C6                                    ; +$012C : 600000D0
L_0030F8:
    move.l 28(a2),d0                                  ; +$0130 : 202A001C
    tst.l d0                                          ; +$0134 : 4A80
    beq.w L_0031C6                                    ; +$0136 : 670000C6
    move.l d5,d0                                      ; +$013A : 2005
    andi.l #$0000007F,d0                              ; +$013C : 02800000007F
    cmpi.l #$00000068,d0                              ; +$0142 : 0C8000000068
    beq.w L_00312C                                    ; +$0148 : 6700001A
    cmpi.l #$00000069,d0                              ; +$014C : 0C8000000069
    beq.w L_003132                                    ; +$0152 : 67000016
    cmpi.l #$0000006A,d0                              ; +$0156 : 0C800000006A
    beq.w L_003138                                    ; +$015C : 67000012
    bra.w L_0031C6                                    ; +$0160 : 6000009C
L_00312C:
    moveq #1,d1                                       ; +$0164 : 7201
    bra.w L_00313A                                    ; +$0166 : 6000000A
L_003132:
    moveq #2,d1                                       ; +$016A : 7202
    bra.w L_00313A                                    ; +$016C : 60000004
L_003138:
    moveq #4,d1                                       ; +$0170 : 7204
L_00313A:
    move.l d5,d0                                      ; +$0172 : 2005
    andi.l #$00000080,d0                              ; +$0174 : 028000000080
    bne.w L_003168                                    ; +$017A : 66000024
    move.l 12(a2),d0                                  ; +$017E : 202A000C
    move.l d0,d4                                      ; +$0182 : 2800
    and.l d1,d4                                       ; +$0184 : C881
    tst.l d4                                          ; +$0186 : 4A84
    bne.w L_0031C6                                    ; +$0188 : 66000074
    or.l d1,d0                                        ; +$018C : 8081
    move.l d0,12(a2)                                  ; +$018E : 2540000C
    move.l 4(a2),d0                                   ; +$0192 : 202A0004
    or.l d1,d0                                        ; +$0196 : 8081
    move.l d0,4(a2)                                   ; +$0198 : 25400004
    bra.w L_0031C6                                    ; +$019C : 60000060
L_003168:
    move.l 12(a2),d0                                  ; +$01A0 : 202A000C
    move.l d0,d4                                      ; +$01A4 : 2800
    and.l d1,d4                                       ; +$01A6 : C881
    tst.l d4                                          ; +$01A8 : 4A84
    beq.w L_0031C6                                    ; +$01AA : 67000052
    sub.l d1,d0                                       ; +$01AE : 9081
    move.l d0,12(a2)                                  ; +$01B0 : 2540000C
    move.l 8(a2),d0                                   ; +$01B4 : 202A0008
    or.l d1,d0                                        ; +$01B8 : 8081
    move.l d0,8(a2)                                   ; +$01BA : 25400008
    bra.w L_0031C6                                    ; +$01BE : 6000003E
L_00318A:
    clr.l 4(a2)                                       ; +$01C2 : 42AA0004
    clr.l 8(a2)                                       ; +$01C6 : 42AA0008
    clr.l 12(a2)                                      ; +$01CA : 42AA000C
    clr.l 28(a2)                                      ; +$01CE : 42AA001C
    bra.w L_0031C6                                    ; +$01D2 : 6000002A
L_00319E:
    clr.l 4(a2)                                       ; +$01D6 : 42AA0004
    clr.l 8(a2)                                       ; +$01DA : 42AA0008
    clr.l 12(a2)                                      ; +$01DE : 42AA000C
    clr.l 28(a2)                                      ; +$01E2 : 42AA001C
    movea.l (a2),a0                                   ; +$01E6 : 2052
    move.l 24(a0),d0                                  ; +$01E8 : 20280018
    andi.l #$00002000,d0                              ; +$01EC : 028000002000
    beq.w L_0031C6                                    ; +$01F2 : 6700000A
    move.l #$00000001,28(a2)                          ; +$01F6 : 257C00000001001C
L_0031C6:
    movea.l a3,a1                                     ; +$01FE : 224B
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -378(a6)                                      ; +$0204 : 4EAEFE86
    dbra d7,L_00305C                                  ; +$0208 : 51CFFE8A
L_0031D4:
    moveq #0,d0                                       ; +$020C : 7000
    bra.w L_0031DC                                    ; +$020E : 60000004
L_0031DA:
    moveq #-1,d0                                      ; +$0212 : 70FF
L_0031DC:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$0214 : 4CDF7FFE
    rts                                               ; +$0218 : 4E75
L_0031E2:
    bsr.w Internal_33                                 ; +$021A : 6100FDE4
    tst.l d0                                          ; +$021E : 4A80
    bne.w L_003248                                    ; +$0220 : 6600005E
    movem.l d1-d7/a0-a6,-(a7)                         ; +$0224 : 48E77FFE
    movea.l 456(a5),a2                                ; +$0228 : 246D01C8
    lea 11732(a2),a2                                  ; +$022C : 45EA2DD4
    move.l 24(a2),d0                                  ; +$0230 : 202A0018
    tst.l d0                                          ; +$0234 : 4A80
    beq.w L_003240                                    ; +$0236 : 67000040
    move.l 16(a2),d1                                  ; +$023A : 222A0010
    add.l d1,d1                                       ; +$023E : D281
    add.l d1,d1                                       ; +$0240 : D281
    lea 80(a2),a0                                     ; +$0242 : 41EA0050
    move.l a0,d0                                      ; +$0246 : 2008
    add.l d1,d0                                       ; +$0248 : D081
    movea.l d0,a0                                     ; +$024A : 2040
    move.l (a0),d4                                    ; +$024C : 2810
    lea 32(a2),a0                                     ; +$024E : 41EA0020
    move.l #$00000400,20(a0)                          ; +$0252 : 217C000004000014
    move.l d4,24(a0)                                  ; +$025A : 21440018
    move.l 16(a2),d1                                  ; +$025E : 222A0010
    addq.l #1,d1                                      ; +$0262 : 5281
    andi.l #$0000000F,d1                              ; +$0264 : 02810000000F
    move.l d1,16(a2)                                  ; +$026A : 25410010
    subq.l #1,24(a2)                                  ; +$026E : 53AA0018
    move.l a0,d0                                      ; +$0272 : 2008
    bra.w L_003242                                    ; +$0274 : 60000004
L_003240:
    moveq #0,d0                                       ; +$0278 : 7000
L_003242:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$027A : 4CDF7FFE
    rts                                               ; +$027E : 4E75
L_003248:
    moveq #0,d0                                       ; +$0280 : 7000
    rts                                               ; +$0282 : 4E75
    dcb.b 144,0

Entry_34:
C_Title:
    dc.b "AMOSPro AGA M8 IDCMP Mouse R23 0.8.7"
    dc.b $00,$24,$56,$45,$52,$3A,$20,$41,$4D,$4F,$53,$50
    dc.b "ro_AGA 0.8.7"
    dc.b $00,$00
C_End:
    dc.w 0
    cnop 0,4
HUNK_DATA_END:
    dc.l $000003F2
