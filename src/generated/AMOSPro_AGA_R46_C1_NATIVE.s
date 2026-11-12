; Restored from OFFICIAL C1 Rbsr wrapper, in memory only.
; Native assembler source is NOT an installable AMOS Compiler library.
; Production builds MUST apply compiler_relocation.wrap_native_ap20().

; AMOS Professional 365 - AGA extension native 68000 source restoration
; Generated from the actual AP20/HUNK image, NOT the historical M1 source.
; All recognized executable instructions are real Motorola mnemonics.
; Remaining dc.b/dcb.b encode strings, state/data, AMOS Rjsr markers,
; or code that cannot be safely identified. They are never silently lost.
; A native assembler comparison is REQUIRED before treating this file
; as byte-identical or using it as the replacement build authority.
; SHA256 original: 5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580
; Build: AMOSPro AGA M16 Image Draw R46 0.12.1 | $VER: AMOSPro_AGA 0.12.1 |  |
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
    dc.w (Entry_35-Entry_34)/2
    dc.w (Entry_36-Entry_35)/2
    dc.w (Entry_37-Entry_36)/2
    dc.w (Entry_38-Entry_37)/2
    dc.w (Entry_39-Entry_38)/2
    dc.w (Entry_40-Entry_39)/2
    dc.w (Entry_41-Entry_40)/2
    dc.w (Entry_42-Entry_41)/2
    dc.w (Entry_43-Entry_42)/2
    dc.w (Entry_44-Entry_43)/2
    dc.w (Entry_45-Entry_44)/2
    dc.w (Entry_46-Entry_45)/2
    dc.w (Entry_47-Entry_46)/2
    dc.w (Entry_48-Entry_47)/2
    dc.w (Entry_49-Entry_48)/2
    dc.w (Entry_50-Entry_49)/2
    dc.w (Entry_51-Entry_50)/2
    dc.w (Entry_52-Entry_51)/2
    dc.w (Entry_53-Entry_52)/2
    dc.w (Entry_54-Entry_53)/2
    dc.w (Entry_55-Entry_54)/2
    dc.w (Entry_56-Entry_55)/2
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
Tk_29:  ; aga hotspot hit : 00,0,0,0,0,0
    dc.w 1,34
    dc.b "aga hotspot hi","t"+$80,"00,0,0,0,0,0",$FF
Tk_30:  ; aga rect overlap : 00,0,0,0,0,0,0,0
    dc.w 1,35
    dc.b "aga rect overla","p"+$80,"00,0,0,0,0,0,0,0",$FF,0
Tk_31:  ; aga text : 00,0,0,2
    dc.w 1,36
    dc.b "aga tex","t"+$80,"00,0,0,2",$FF,0
Tk_32:  ; aga palette load : 02
    dc.w 1,37
    dc.b "aga palette loa","d"+$80,"02",$FF,0
Tk_33:  ; aga palette set : 00,0,0,0
    dc.w 1,38
    dc.b "aga palette se","t"+$80,"00,0,0,0",$FF
Tk_34:  ; aga palette get : 00
    dc.w 1,39
    dc.b "aga palette ge","t"+$80,"00",$FF
Tk_35:  ; aga palette save : 02
    dc.w 1,40
    dc.b "aga palette sav","e"+$80,"02",$FF,0
Tk_36:  ; aga palette bank init : 00,0
    dc.w 1,41
    dc.b "aga palette bank ini","t"+$80,"00,0",$FF
Tk_37:  ; aga palette bank capture : 00,0
    dc.w 1,42
    dc.b "aga palette bank captur","e"+$80,"00,0",$FF,0
Tk_38:  ; aga palette bank apply : 00,0
    dc.w 1,43
    dc.b "aga palette bank appl","y"+$80,"00,0",$FF,0
Tk_39:  ; aga fade to bank : 00,0,0
    dc.w 1,44
    dc.b "aga fade to ban","k"+$80,"00,0,0",$FF,0
Tk_40:  ; aga fade to black : 00
    dc.w 1,45
    dc.b "aga fade to blac","k"+$80,"00",$FF
Tk_41:  ; aga fade to white : 00
    dc.w 1,46
    dc.b "aga fade to whit","e"+$80,"00",$FF
Tk_42:  ; aga palette cycle : 00,0,0
    dc.w 1,47
    dc.b "aga palette cycl","e"+$80,"00,0,0",$FF
Tk_43:  ; aga font select : 02,0
    dc.w 1,48
    dc.b "aga font selec","t"+$80,"02,0",$FF
Tk_44:  ; aga font bank select : 00,0
    dc.w 1,49
    dc.b "aga font bank selec","t"+$80,"00,0",$FF,0
Tk_45:  ; aga plot : 00,0,0
    dc.w 1,50
    dc.b "aga plo","t"+$80,"00,0,0",$FF,0
Tk_46:  ; aga draw : 00,0,0,0,0
    dc.w 1,51
    dc.b "aga dra","w"+$80,"00,0,0,0,0",$FF,0
Tk_47:  ; aga box : 00,0,0,0,0
    dc.w 1,52
    dc.b "aga bo","x"+$80,"00,0,0,0,0",$FF
Tk_48:  ; aga circle : 00,0,0,0
    dc.w 1,53
    dc.b "aga circl","e"+$80,"00,0,0,0",$FF,0
Tk_49:  ; aga mouse cursor : 00
    dc.w 1,54
    dc.b "aga mouse curso","r"+$80,"00",$FF,0
Tk_50:  ; aga image draw : 00,0,0,0,0
    dc.w 1,55
    dc.b "aga image dra","w"+$80,"00,0,0,0,0",$FF,0
    dc.b $00,$00,$00,$00,$00,$00

C_Lib:

; -------- AP20 entry 00 : private/reserved --------
Entry_00:
Internal_00:
    cmp.l #$41506578,d1                               ; +$0000 : B2BC41506578
    bne.w L_000582                                    ; +$0006 : 6600002A
    lea L_0006F0(pc),a0                               ; +$000A : 41FA0194
    move.l a0,456(a5)                                 ; +$000E : 2B4801C8
    lea L_000588(pc),a0                               ; +$0012 : 41FA0024
    move.l a0,460(a5)                                 ; +$0016 : 2B4801CC
    move.l a0,464(a5)                                 ; +$001A : 2B4801D0
    lea L_0006F0(pc),a0                               ; +$001E : 41FA0180
    moveq #9,d0                                       ; +$0022 : 7009
L_000574:
    clr.l (a0)+                                       ; +$0024 : 4298
    dbra d0,L_000574                                  ; +$0026 : 51C8FFFC
    moveq #13,d0                                      ; +$002A : 700D
    move.w #$0200,d1                                  ; +$002C : 323C0200
    rts                                               ; +$0030 : 4E75
L_000582:
    moveq #-1,d0                                      ; +$0032 : 70FF
    suba.l a0,a0                                      ; +$0034 : 91C8
    rts                                               ; +$0036 : 4E75
L_000588:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0038 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$003C : 246D01C8
    bra.w L_000718                                    ; +$0040 : 60000186
L_000594:
    move.l a4,d0                                      ; +$0044 : 200C
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_00064A                                    ; +$0048 : 670000B0
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0005AC                                    ; +$0054 : 67000006
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
L_0005AC:
    move.l 20(a4),d0                                  ; +$005C : 202C0014
    tst.l d0                                          ; +$0060 : 4A80
    bra.w L_0005EE                                    ; +$0062 : 6000003A
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    movea.l $0004.w,a6                                ; +$006A : 2C780004
    nop                                               ; +$006E : 4E71
    nop                                               ; +$0070 : 4E71
    movea.l 12(a4),a0                                 ; +$0072 : 206C000C
    jsr -372(a6)                                      ; +$0076 : 4EAEFE8C
    tst.l d0                                          ; +$007A : 4A80
    beq.w L_0005EE                                    ; +$007C : 67000020
    movea.l 16(a4),a0                                 ; +$0080 : 206C0010
    movea.l $0004.w,a6                                ; +$0084 : 2C780004
    nop                                               ; +$0088 : 4E71
    nop                                               ; +$008A : 4E71
    movea.l 16(a4),a0                                 ; +$008C : 206C0010
    jsr -372(a6)                                      ; +$0090 : 4EAEFE8C
    tst.l d0                                          ; +$0094 : 4A80
    beq.w L_0005EE                                    ; +$0096 : 67000006
    clr.l 20(a4)                                      ; +$009A : 42AC0014
L_0005EE:
    movea.l (a2),a0                                   ; +$009E : 2052
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_00061C                                    ; +$00A4 : 67000026
    movea.l 4(a2),a6                                  ; +$00A8 : 2C6A0004
    movea.l 4(a4),a1                                  ; +$00AC : 226C0004
    move.l a1,d0                                      ; +$00B0 : 2009
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_00060C                                    ; +$00B4 : 67000006
    jsr -774(a6)                                      ; +$00B8 : 4EAEFCFA
L_00060C:
    movea.l (a4),a1                                   ; +$00BC : 2254
    move.l a1,d0                                      ; +$00BE : 2009
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_00061C                                    ; +$00C2 : 67000008
    movea.l (a2),a0                                   ; +$00C6 : 2052
    jsr -774(a6)                                      ; +$00C8 : 4EAEFCFA
L_00061C:
    movea.l $0004.w,a6                                ; +$00CC : 2C780004
    movea.l 16(a4),a0                                 ; +$00D0 : 206C0010
    move.l a0,d0                                      ; +$00D4 : 2008
    tst.l d0                                          ; +$00D6 : 4A80
    beq.w L_000630                                    ; +$00D8 : 67000006
    jsr -672(a6)                                      ; +$00DC : 4EAEFD60
L_000630:
    movea.l 12(a4),a0                                 ; +$00E0 : 206C000C
    move.l a0,d0                                      ; +$00E4 : 2008
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_000640                                    ; +$00E8 : 67000006
    jsr -672(a6)                                      ; +$00EC : 4EAEFD60
L_000640:
    movea.l a4,a1                                     ; +$00F0 : 224C
    jsr -690(a6)                                      ; +$00F2 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$00F6 : 42AA0020
L_00064A:
    tst.l (a2)                                        ; +$00FA : 4A92
    beq.w L_00065C                                    ; +$00FC : 6700000E
    movea.l (a2),a0                                   ; +$0100 : 2052
    movea.l 4(a2),a6                                  ; +$0102 : 2C6A0004
    jsr -66(a6)                                       ; +$0106 : 4EAEFFBE
    clr.l (a2)                                        ; +$010A : 4292
L_00065C:
    movea.l 8(a2),a1                                  ; +$010C : 226A0008
    move.l a1,d0                                      ; +$0110 : 2009
    tst.l d0                                          ; +$0112 : 4A80
    beq.w L_000674                                    ; +$0114 : 6700000E
    movea.l $0004.w,a6                                ; +$0118 : 2C780004
    jsr -414(a6)                                      ; +$011C : 4EAEFE62
    clr.l 8(a2)                                       ; +$0120 : 42AA0008
L_000674:
    movea.l 4(a2),a1                                  ; +$0124 : 226A0004
    move.l a1,d0                                      ; +$0128 : 2009
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_00068C                                    ; +$012C : 6700000E
    movea.l $0004.w,a6                                ; +$0130 : 2C780004
    jsr -414(a6)                                      ; +$0134 : 4EAEFE62
    clr.l 4(a2)                                       ; +$0138 : 42AA0004
L_00068C:
    lea 12(a2),a0                                     ; +$013C : 41EA000C
    moveq #4,d0                                       ; +$0140 : 7004
L_000692:
    clr.l (a0)+                                       ; +$0142 : 4298
    dbra d0,L_000692                                  ; +$0144 : 51C8FFFC
L_000698:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$0148 : 4CDF7FFF
    rts                                               ; +$014C : 4E75
L_00069E:
    movea.l 36(a2),a3                                 ; +$014E : 266A0024
    move.l a3,d0                                      ; +$0152 : 200B
    tst.l d0                                          ; +$0154 : 4A80
    beq.w L_0006EA                                    ; +$0156 : 67000042
    movea.l 86(a3),a4                                 ; +$015A : 286B0056
    move.l a4,d0                                      ; +$015E : 200C
    tst.l d0                                          ; +$0160 : 4A80
    beq.w L_0006D0                                    ; +$0162 : 6700001C
L_0006B6:
    movea.l a4,a0                                     ; +$0166 : 204C
    movea.l $0004.w,a6                                ; +$0168 : 2C780004
    jsr -372(a6)                                      ; +$016C : 4EAEFE8C
    tst.l d0                                          ; +$0170 : 4A80
    beq.w L_0006D0                                    ; +$0172 : 6700000C
    movea.l d0,a1                                     ; +$0176 : 2240
    jsr -378(a6)                                      ; +$0178 : 4EAEFE86
    bra.w L_0006B6                                    ; +$017C : 6000FFE8
L_0006D0:
    movea.l 4(a2),a6                                  ; +$0180 : 2C6A0004
    move.l a6,d0                                      ; +$0184 : 200E
    tst.l d0                                          ; +$0186 : 4A80
    beq.w L_0006E2                                    ; +$0188 : 67000008
    movea.l a3,a0                                     ; +$018C : 204B
    bsr.w L_006AAE                                    ; +$018E : 610063CE
L_0006E2:
    move.l #$00000000,36(a2)                          ; +$0192 : 257C000000000024
L_0006EA:
    movea.l 32(a2),a4                                 ; +$019A : 286A0020
    rts                                               ; +$019E : 4E75
L_0006F0:
    dcb.b 40,0
L_000718:
    bsr.w L_00072E                                    ; +$01C8 : 61000014
    tst.l d0                                          ; +$01CC : 4A80
    beq.w L_00072A                                    ; +$01CE : 6700000A
    bsr.w L_00069E                                    ; +$01D2 : 6100FF7A
    bra.w L_000594                                    ; +$01D6 : 6000FE6C
L_00072A:
    bra.w L_000698                                    ; +$01DA : 6000FF6C
L_00072E:
    movea.l 32(a2),a4                                 ; +$01DE : 286A0020
    move.l a4,d0                                      ; +$01E2 : 200C
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_000766                                    ; +$01E6 : 6700002E
    moveq #0,d4                                       ; +$01EA : 7800
L_00073C:
    bsr.w L_00076E                                    ; +$01EC : 61000030
    tst.l d0                                          ; +$01F0 : 4A80
    beq.w L_000766                                    ; +$01F2 : 67000022
    addq.l #1,d4                                      ; +$01F6 : 5284
    cmpi.l #$0000012D,d4                              ; +$01F8 : 0C840000012D
    bge.w L_00076A                                    ; +$01FE : 6C00001A
    movea.l 8(a2),a6                                  ; +$0202 : 2C6A0008
    move.l a6,d0                                      ; +$0206 : 200E
    tst.l d0                                          ; +$0208 : 4A80
    beq.w L_00076A                                    ; +$020A : 6700000E
    jsr -270(a6)                                      ; +$020E : 4EAEFEF2
    bra.w L_00073C                                    ; +$0212 : 6000FFD8
L_000766:
    moveq #1,d0                                       ; +$0216 : 7001
    rts                                               ; +$0218 : 4E75
L_00076A:
    moveq #0,d0                                       ; +$021A : 7000
    rts                                               ; +$021C : 4E75
L_00076E:
    move.l 20(a4),d6                                  ; +$021E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0222 : 028600000003
    btst #0,d6                                        ; +$0228 : 08060000
    beq.w L_00079E                                    ; +$022C : 67000020
    movea.l 12(a4),a0                                 ; +$0230 : 206C000C
    move.l a0,d0                                      ; +$0234 : 2008
    tst.l d0                                          ; +$0236 : 4A80
    beq.w L_00079E                                    ; +$0238 : 67000014
    movea.l $0004.w,a6                                ; +$023C : 2C780004
    jsr -372(a6)                                      ; +$0240 : 4EAEFE8C
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_00079E                                    ; +$0246 : 67000006
    bclr #0,d6                                        ; +$024A : 08860000
L_00079E:
    btst #1,d6                                        ; +$024E : 08060001
    beq.w L_0007C4                                    ; +$0252 : 67000020
    movea.l 16(a4),a0                                 ; +$0256 : 206C0010
    move.l a0,d0                                      ; +$025A : 2008
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_0007C4                                    ; +$025E : 67000014
    movea.l $0004.w,a6                                ; +$0262 : 2C780004
    jsr -372(a6)                                      ; +$0266 : 4EAEFE8C
    tst.l d0                                          ; +$026A : 4A80
    beq.w L_0007C4                                    ; +$026C : 67000006
    bclr #1,d6                                        ; +$0270 : 08860001
L_0007C4:
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
    beq.s L_00082C                                    ; +$0016 : 6724
    lea L_00083A(pc),a1                               ; +$0018 : 43FA0030
    moveq #39,d0                                      ; +$001C : 7027
    jsr -552(a6)                                      ; +$001E : 4EAEFDD8
    tst.l d0                                          ; +$0022 : 4A80
    beq.s L_00082C                                    ; +$0024 : 6716
    movea.l d0,a1                                     ; +$0026 : 2240
    move.b 236(a1),d1                                 ; +$0028 : 122900EC
    andi.b #$0C,d1                                    ; +$002C : 0201000C
    cmpi.b #$0C,d1                                    ; +$0030 : 0C01000C
    bne.s L_000828                                    ; +$0034 : 6602
    moveq #1,d3                                       ; +$0036 : 7601
L_000828:
    jsr -414(a6)                                      ; +$0038 : 4EAEFE62
L_00082C:
    movea.l (a7)+,a6                                  ; +$003C : 2C5F
    movea.l (a7)+,a1                                  ; +$003E : 225F
    movea.l (a7)+,a0                                  ; +$0040 : 205F
    move.l (a7)+,d1                                   ; +$0042 : 221F
    move.l (a7)+,d0                                   ; +$0044 : 201F
    moveq #0,d2                                       ; +$0046 : 7400
    rts                                               ; +$0048 : 4E75
L_00083A:
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
    beq.w L_00096E                                    ; +$0010 : 6700010C
    lea L_000976(pc),a1                               ; +$0014 : 43FA0110
    moveq #39,d0                                      ; +$0018 : 7027
    jsr -552(a6)                                      ; +$001A : 4EAEFDD8
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_00096E                                    ; +$0020 : 670000FC
    movea.l d0,a4                                     ; +$0024 : 2840
    movea.l $0004.w,a6                                ; +$0026 : 2C780004
    lea L_000988(pc),a1                               ; +$002A : 43FA010C
    moveq #39,d0                                      ; +$002E : 7027
    jsr -552(a6)                                      ; +$0030 : 4EAEFDD8
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_000964                                    ; +$0036 : 670000DC
    movea.l d0,a5                                     ; +$003A : 2A40
    move.b 236(a5),d0                                 ; +$003C : 102D00EC
    andi.b #$0C,d0                                    ; +$0040 : 0200000C
    cmpi.b #$0C,d0                                    ; +$0044 : 0C00000C
    bne.w L_00095A                                    ; +$0048 : 660000C0
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
    beq.w L_00095A                                    ; +$0098 : 67000070
    movea.l d0,a3                                     ; +$009C : 2640
    moveq #0,d6                                       ; +$009E : 7C00
L_0008F0:
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
    bne.w L_0008F0                                    ; +$00EA : 6600FFB4
    move.w #$0096,d7                                  ; +$00EE : 3E3C0096
L_000942:
    movea.l a5,a6                                     ; +$00F2 : 2C4D
    jsr -270(a6)                                      ; +$00F4 : 4EAEFEF2
    dbra d7,L_000942                                  ; +$00F8 : 51CFFFF8
    movea.l a3,a0                                     ; +$00FC : 204B
    movea.l a4,a6                                     ; +$00FE : 2C4C
    jsr -66(a6)                                       ; +$0100 : 4EAEFFBE
    moveq #1,d3                                       ; +$0104 : 7601
    bra.w L_00095A                                    ; +$0106 : 60000002
L_00095A:
    movea.l a5,a1                                     ; +$010A : 224D
    movea.l $0004.w,a6                                ; +$010C : 2C780004
    jsr -414(a6)                                      ; +$0110 : 4EAEFE62
L_000964:
    movea.l a4,a1                                     ; +$0114 : 224C
    movea.l $0004.w,a6                                ; +$0116 : 2C780004
    jsr -414(a6)                                      ; +$011A : 4EAEFE62
L_00096E:
    movem.l (a7)+,d0-d1/d4-d7/a0-a6                   ; +$011E : 4CDF7FF3
    moveq #0,d2                                       ; +$0122 : 7400
    rts                                               ; +$0124 : 4E75
L_000976:
    dc.b "intuition.library"
    dc.b $00
L_000988:
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
    beq.w L_000AFA                                    ; +$0016 : 67000144
    tst.l (a2)                                        ; +$001A : 4A92
    bne.w L_000AFA                                    ; +$001C : 6600013E
    cmpi.l #$00000001,d4                              ; +$0020 : 0C8400000001
    bcs.w L_000AFA                                    ; +$0026 : 65000134
    cmpi.l #$00007FFF,d4                              ; +$002A : 0C8400007FFF
    bhi.w L_000AFA                                    ; +$0030 : 6200012A
    move.l d4,d0                                      ; +$0034 : 2004
    andi.l #$00000000,d0                              ; +$0036 : 028000000000
    nop                                               ; +$003C : 4E71
    nop                                               ; +$003E : 4E71
    cmpi.l #$00000001,d5                              ; +$0040 : 0C8500000001
    bcs.w L_000AFA                                    ; +$0046 : 65000114
    cmpi.l #$00007FFF,d5                              ; +$004A : 0C8500007FFF
    bhi.w L_000AFA                                    ; +$0050 : 6200010A
    cmpi.l #$00000002,d6                              ; +$0054 : 0C8600000002
    bcs.w L_000AFA                                    ; +$005A : 65000100
    cmpi.l #$00000100,d6                              ; +$005E : 0C8600000100
    bhi.w L_000AFA                                    ; +$0064 : 620000F6
    move.l d6,d1                                      ; +$0068 : 2206
    subq.l #1,d1                                      ; +$006A : 5381
    and.l d6,d1                                       ; +$006C : C286
    bne.w L_000AFA                                    ; +$006E : 660000EC
    move.l d7,d0                                      ; +$0072 : 2007
    andi.l #$00000400,d0                              ; +$0074 : 028000000400
    bne.w L_000AFA                                    ; +$007A : 660000E0
    movea.l $0004.w,a6                                ; +$007E : 2C780004
    btst #1,297(a6)                                   ; +$0082 : 082E00010129
    beq.w L_000AFA                                    ; +$0088 : 670000D2
    lea L_000B02(pc),a1                               ; +$008C : 43FA00D6
    moveq #39,d0                                      ; +$0090 : 7027
    jsr -552(a6)                                      ; +$0092 : 4EAEFDD8
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_000AFA                                    ; +$0098 : 670000C2
    movea.l d0,a4                                     ; +$009C : 2840
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    lea L_000B14(pc),a1                               ; +$00A2 : 43FA00D2
    moveq #39,d0                                      ; +$00A6 : 7027
    jsr -552(a6)                                      ; +$00A8 : 4EAEFDD8
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_000AF0                                    ; +$00AE : 670000A2
    movea.l d0,a5                                     ; +$00B2 : 2A40
    move.b 236(a5),d0                                 ; +$00B4 : 102D00EC
    andi.b #$0C,d0                                    ; +$00B8 : 0200000C
    cmpi.b #$0C,d0                                    ; +$00BC : 0C00000C
    bne.w L_000AE2                                    ; +$00C0 : 66000082
    move.l d6,d1                                      ; +$00C4 : 2206
    moveq #0,d0                                       ; +$00C6 : 7000
L_000A66:
    lsr.l #1,d1                                       ; +$00C8 : E289
    addq.l #1,d0                                      ; +$00CA : 5280
    cmpi.l #$00000001,d1                              ; +$00CC : 0C8100000001
    bne.w L_000A66                                    ; +$00D2 : 6600FFF4
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
    bsr.w L_000B26                                    ; +$010A : 6100007C
    nop                                               ; +$010E : 4E71
    suba.l a0,a0                                      ; +$0110 : 91C8
    movea.l a7,a1                                     ; +$0112 : 224F
    movea.l a4,a6                                     ; +$0114 : 2C4C
    bsr.w L_000C2A                                    ; +$0116 : 61000174
    lea 60(a7),a7                                     ; +$011A : 4FEF003C
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_000AE2                                    ; +$0120 : 67000022
    move.l d0,(a2)                                    ; +$0124 : 2480
    move.l a4,4(a2)                                   ; +$0126 : 254C0004
    move.l a5,8(a2)                                   ; +$012A : 254D0008
    move.l d4,12(a2)                                  ; +$012E : 2544000C
    move.l d5,16(a2)                                  ; +$0132 : 25450010
    move.l d6,20(a2)                                  ; +$0136 : 25460014
    bsr.w L_000C7C                                    ; +$013A : 610001A2
    bra.w L_000AFA                                    ; +$013E : 6000001C
    nop                                               ; +$0142 : 4E71
L_000AE2:
    clr.l 28(a2)                                      ; +$0144 : 42AA001C
    movea.l a5,a1                                     ; +$0148 : 224D
    movea.l $0004.w,a6                                ; +$014A : 2C780004
    jsr -414(a6)                                      ; +$014E : 4EAEFE62
L_000AF0:
    movea.l a4,a1                                     ; +$0152 : 224C
    movea.l $0004.w,a6                                ; +$0154 : 2C780004
    jsr -414(a6)                                      ; +$0158 : 4EAEFE62
L_000AFA:
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6             ; +$015C : 4CDF77F3
    moveq #0,d2                                       ; +$0160 : 7400
    rts                                               ; +$0162 : 4E75
L_000B02:
    dc.b "intuition.library"
    dc.b $00
L_000B14:
    dc.b "graphics.library"
    dc.b $00,$00
L_000B26:
    move.l #$80000039,(a1)+                           ; +$0188 : 22FC80000039
    moveq #1,d0                                       ; +$018E : 7001
    move.l d0,(a1)+                                   ; +$0190 : 22C0
    moveq #0,d0                                       ; +$0192 : 7000
    move.l d0,(a1)+                                   ; +$0194 : 22C0
    move.l d0,(a1)+                                   ; +$0196 : 22C0
    rts                                               ; +$0198 : 4E75
L_000B38:
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
    beq.w L_000BC0                                    ; +$0214 : 6700000C
    move.l d1,36(a2)                                  ; +$0218 : 25410024
    moveq #1,d3                                       ; +$021C : 7601
    bra.w L_000C24                                    ; +$021E : 60000066
L_000BC0:
    movea.l (a2),a0                                   ; +$0222 : 2052
    move.l a0,d0                                      ; +$0224 : 2008
    tst.l d0                                          ; +$0226 : 4A80
    beq.w L_000BD2                                    ; +$0228 : 6700000A
    movea.l 4(a2),a6                                  ; +$022C : 2C6A0004
    jsr -66(a6)                                       ; +$0230 : 4EAEFFBE
L_000BD2:
    movea.l 8(a2),a1                                  ; +$0234 : 226A0008
    move.l a1,d0                                      ; +$0238 : 2009
    tst.l d0                                          ; +$023A : 4A80
    beq.w L_000BE6                                    ; +$023C : 6700000A
    movea.l $0004.w,a6                                ; +$0240 : 2C780004
    jsr -414(a6)                                      ; +$0244 : 4EAEFE62
L_000BE6:
    movea.l 4(a2),a1                                  ; +$0248 : 226A0004
    move.l a1,d0                                      ; +$024C : 2009
    tst.l d0                                          ; +$024E : 4A80
    beq.w L_000BFA                                    ; +$0250 : 6700000A
    movea.l $0004.w,a6                                ; +$0254 : 2C780004
    jsr -414(a6)                                      ; +$0258 : 4EAEFE62
L_000BFA:
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
L_000C24:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0286 : 4CDF7FF7
    rts                                               ; +$028A : 4E75
L_000C2A:
    move.l a1,d2                                      ; +$028C : 2409
    jsr -612(a6)                                      ; +$028E : 4EAEFD9C
    tst.l d0                                          ; +$0292 : 4A80
    bne.w L_000C76                                    ; +$0294 : 66000042
    move.l d7,d1                                      ; +$0298 : 2207
    andi.l #$FFFF0000,d1                              ; +$029A : 0281FFFF0000
    cmpi.l #$00010000,d1                              ; +$02A0 : 0C8100010000
    bne.w L_000C76                                    ; +$02A6 : 66000030
    move.l d7,d1                                      ; +$02AA : 2207
    addi.l #$00010000,d1                              ; +$02AC : 068100010000
    move.l a6,-(a7)                                   ; +$02B2 : 2F0E
    movea.l a5,a6                                     ; +$02B4 : 2C4D
    move.l d1,d0                                      ; +$02B6 : 2001
    jsr -798(a6)                                      ; +$02B8 : 4EAEFCE2
    movea.l (a7)+,a6                                  ; +$02BC : 2C5F
    tst.l d0                                          ; +$02BE : 4A80
    bne.w L_000C78                                    ; +$02C0 : 66000018
    move.l d7,d1                                      ; +$02C4 : 2207
    addi.l #$00010000,d1                              ; +$02C6 : 068100010000
    movea.l d2,a1                                     ; +$02CC : 2242
    move.l d1,28(a1)                                  ; +$02CE : 2341001C
    suba.l a0,a0                                      ; +$02D2 : 91C8
    jsr -612(a6)                                      ; +$02D4 : 4EAEFD9C
L_000C76:
    rts                                               ; +$02D8 : 4E75
L_000C78:
    moveq #0,d0                                       ; +$02DA : 7000
    rts                                               ; +$02DC : 4E75
L_000C7C:
    bsr.w L_000B38                                    ; +$02DE : 6100FEBA
    lea 11932(a2),a0                                  ; +$02E2 : 41EA2E9C
    moveq #35,d0                                      ; +$02E6 : 7023
L_000C86:
    clr.l (a0)+                                       ; +$02E8 : 4298
    dbra d0,L_000C86                                  ; +$02EA : 51C8FFFC
    rts                                               ; +$02EE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 07 : aga screen pattern --------
Entry_07:
Aga_Screen_Pattern:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)                   ; +$0000 : 48E7FFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_000D1E                                    ; +$000C : 6700007E
    tst.l (a2)                                        ; +$0010 : 4A92
    beq.w L_000D1E                                    ; +$0012 : 67000078
    movea.l (a2),a4                                   ; +$0016 : 2852
    movea.l 8(a2),a6                                  ; +$0018 : 2C6A0008
    move.l 20(a2),d4                                  ; +$001C : 282A0014
    move.l 16(a2),d5                                  ; +$0020 : 2A2A0010
    moveq #0,d6                                       ; +$0024 : 7C00
L_000CB8:
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
    bne.w L_000CB8                                    ; +$0088 : 6600FF9C
L_000D1E:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6                   ; +$008C : 4CDF77FF
    rts                                               ; +$0090 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 08 : aga screen close --------
Entry_08:
Aga_Screen_Close:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0000 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    bra.w L_000E4E                                    ; +$0008 : 6000011C
L_000D34:
    move.l a4,d0                                      ; +$000C : 200C
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_000DA8                                    ; +$0010 : 6700006E
    movea.l 8(a2),a6                                  ; +$0014 : 2C6A0008
    move.l a6,d0                                      ; +$0018 : 200E
    tst.l d0                                          ; +$001A : 4A80
    beq.w L_000D4C                                    ; +$001C : 67000006
    jsr -228(a6)                                      ; +$0020 : 4EAEFF1C
L_000D4C:
    movea.l (a2),a0                                   ; +$0024 : 2052
    move.l a0,d0                                      ; +$0026 : 2008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_000D7A                                    ; +$002A : 67000026
    movea.l 4(a2),a6                                  ; +$002E : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0032 : 226C0004
    move.l a1,d0                                      ; +$0036 : 2009
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_000D6A                                    ; +$003A : 67000006
    jsr -774(a6)                                      ; +$003E : 4EAEFCFA
L_000D6A:
    movea.l (a4),a1                                   ; +$0042 : 2254
    move.l a1,d0                                      ; +$0044 : 2009
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_000D7A                                    ; +$0048 : 67000008
    movea.l (a2),a0                                   ; +$004C : 2052
    jsr -774(a6)                                      ; +$004E : 4EAEFCFA
L_000D7A:
    movea.l $0004.w,a6                                ; +$0052 : 2C780004
    movea.l 16(a4),a0                                 ; +$0056 : 206C0010
    move.l a0,d0                                      ; +$005A : 2008
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_000D8E                                    ; +$005E : 67000006
    jsr -672(a6)                                      ; +$0062 : 4EAEFD60
L_000D8E:
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    move.l a0,d0                                      ; +$006A : 2008
    tst.l d0                                          ; +$006C : 4A80
    beq.w L_000D9E                                    ; +$006E : 67000006
    jsr -672(a6)                                      ; +$0072 : 4EAEFD60
L_000D9E:
    movea.l a4,a1                                     ; +$0076 : 224C
    jsr -690(a6)                                      ; +$0078 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$007C : 42AA0020
L_000DA8:
    tst.l (a2)                                        ; +$0080 : 4A92
    beq.w L_000DBA                                    ; +$0082 : 6700000E
    movea.l (a2),a0                                   ; +$0086 : 2052
    movea.l 4(a2),a6                                  ; +$0088 : 2C6A0004
    bsr.w L_00576E                                    ; +$008C : 610049B8
    clr.l (a2)                                        ; +$0090 : 4292
L_000DBA:
    movea.l 8(a2),a1                                  ; +$0092 : 226A0008
    move.l a1,d0                                      ; +$0096 : 2009
    tst.l d0                                          ; +$0098 : 4A80
    beq.w L_000DD2                                    ; +$009A : 6700000E
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    jsr -414(a6)                                      ; +$00A2 : 4EAEFE62
    clr.l 8(a2)                                       ; +$00A6 : 42AA0008
L_000DD2:
    movea.l 4(a2),a1                                  ; +$00AA : 226A0004
    move.l a1,d0                                      ; +$00AE : 2009
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_000DEA                                    ; +$00B2 : 6700000E
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    jsr -414(a6)                                      ; +$00BA : 4EAEFE62
    clr.l 4(a2)                                       ; +$00BE : 42AA0004
L_000DEA:
    lea 12(a2),a0                                     ; +$00C2 : 41EA000C
    moveq #4,d0                                       ; +$00C6 : 7004
L_000DF0:
    clr.l (a0)+                                       ; +$00C8 : 4298
    dbra d0,L_000DF0                                  ; +$00CA : 51C8FFFC
L_000DF6:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$00CE : 4CDF7FFF
    rts                                               ; +$00D2 : 4E75
L_000DFC:
    movea.l 36(a2),a3                                 ; +$00D4 : 266A0024
    move.l a3,d0                                      ; +$00D8 : 200B
    tst.l d0                                          ; +$00DA : 4A80
    beq.w L_000E48                                    ; +$00DC : 67000042
    movea.l 86(a3),a4                                 ; +$00E0 : 286B0056
    move.l a4,d0                                      ; +$00E4 : 200C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_000E2E                                    ; +$00E8 : 6700001C
L_000E14:
    movea.l a4,a0                                     ; +$00EC : 204C
    movea.l $0004.w,a6                                ; +$00EE : 2C780004
    jsr -372(a6)                                      ; +$00F2 : 4EAEFE8C
    tst.l d0                                          ; +$00F6 : 4A80
    beq.w L_000E2E                                    ; +$00F8 : 6700000C
    movea.l d0,a1                                     ; +$00FC : 2240
    jsr -378(a6)                                      ; +$00FE : 4EAEFE86
    bra.w L_000E14                                    ; +$0102 : 6000FFE8
L_000E2E:
    movea.l 4(a2),a6                                  ; +$0106 : 2C6A0004
    move.l a6,d0                                      ; +$010A : 200E
    tst.l d0                                          ; +$010C : 4A80
    beq.w L_000E40                                    ; +$010E : 67000008
    movea.l a3,a0                                     ; +$0112 : 204B
    bsr.w L_006AAE                                    ; +$0114 : 61005C70
L_000E40:
    move.l #$00000000,36(a2)                          ; +$0118 : 257C000000000024
L_000E48:
    movea.l 32(a2),a4                                 ; +$0120 : 286A0020
    rts                                               ; +$0124 : 4E75
L_000E4E:
    bsr.w L_000E64                                    ; +$0126 : 61000014
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_000E60                                    ; +$012C : 6700000A
    bsr.w L_000DFC                                    ; +$0130 : 6100FFA2
    bra.w L_000D34                                    ; +$0134 : 6000FED6
L_000E60:
    bra.w L_000DF6                                    ; +$0138 : 6000FF94
L_000E64:
    movea.l 32(a2),a4                                 ; +$013C : 286A0020
    move.l a4,d0                                      ; +$0140 : 200C
    tst.l d0                                          ; +$0142 : 4A80
    beq.w L_000E9C                                    ; +$0144 : 6700002E
    moveq #0,d4                                       ; +$0148 : 7800
L_000E72:
    bsr.w L_000EA4                                    ; +$014A : 61000030
    tst.l d0                                          ; +$014E : 4A80
    beq.w L_000E9C                                    ; +$0150 : 67000022
    addq.l #1,d4                                      ; +$0154 : 5284
    cmpi.l #$0000012D,d4                              ; +$0156 : 0C840000012D
    bge.w L_000EA0                                    ; +$015C : 6C00001A
    movea.l 8(a2),a6                                  ; +$0160 : 2C6A0008
    move.l a6,d0                                      ; +$0164 : 200E
    tst.l d0                                          ; +$0166 : 4A80
    beq.w L_000EA0                                    ; +$0168 : 6700000E
    jsr -270(a6)                                      ; +$016C : 4EAEFEF2
    bra.w L_000E72                                    ; +$0170 : 6000FFD8
L_000E9C:
    moveq #1,d0                                       ; +$0174 : 7001
    rts                                               ; +$0176 : 4E75
L_000EA0:
    moveq #0,d0                                       ; +$0178 : 7000
    rts                                               ; +$017A : 4E75
L_000EA4:
    move.l 20(a4),d6                                  ; +$017C : 2C2C0014
    andi.l #$00000003,d6                              ; +$0180 : 028600000003
    btst #0,d6                                        ; +$0186 : 08060000
    beq.w L_000ED4                                    ; +$018A : 67000020
    movea.l 12(a4),a0                                 ; +$018E : 206C000C
    move.l a0,d0                                      ; +$0192 : 2008
    tst.l d0                                          ; +$0194 : 4A80
    beq.w L_000ED4                                    ; +$0196 : 67000014
    movea.l $0004.w,a6                                ; +$019A : 2C780004
    jsr -372(a6)                                      ; +$019E : 4EAEFE8C
    tst.l d0                                          ; +$01A2 : 4A80
    beq.w L_000ED4                                    ; +$01A4 : 67000006
    bclr #0,d6                                        ; +$01A8 : 08860000
L_000ED4:
    btst #1,d6                                        ; +$01AC : 08060001
    beq.w L_000EFA                                    ; +$01B0 : 67000020
    movea.l 16(a4),a0                                 ; +$01B4 : 206C0010
    move.l a0,d0                                      ; +$01B8 : 2008
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_000EFA                                    ; +$01BC : 67000014
    movea.l $0004.w,a6                                ; +$01C0 : 2C780004
    jsr -372(a6)                                      ; +$01C4 : 4EAEFE8C
    tst.l d0                                          ; +$01C8 : 4A80
    beq.w L_000EFA                                    ; +$01CA : 67000006
    bclr #1,d6                                        ; +$01CE : 08860001
L_000EFA:
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
    beq.s L_000F1A                                    ; +$000A : 6708
    movea.l 8(a2),a6                                  ; +$000C : 2C6A0008
    jsr -270(a6)                                      ; +$0010 : 4EAEFEF2
L_000F1A:
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
    beq.w L_00103A                                    ; +$000C : 67000108
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    bne.w L_000FEC                                    ; +$0018 : 660000AE
    moveq #24,d0                                      ; +$001C : 7018
    move.l #$00010001,d1                              ; +$001E : 223C00010001
    movea.l $0004.w,a6                                ; +$0024 : 2C780004
    jsr -684(a6)                                      ; +$0028 : 4EAEFD54
    tst.l d0                                          ; +$002C : 4A80
    beq.w L_00103A                                    ; +$002E : 670000E6
    movea.l d0,a4                                     ; +$0032 : 2840
    movea.l $0004.w,a6                                ; +$0034 : 2C780004
    jsr -666(a6)                                      ; +$0038 : 4EAEFD66
    tst.l d0                                          ; +$003C : 4A80
    beq.w L_001030                                    ; +$003E : 670000CC
    move.l d0,12(a4)                                  ; +$0042 : 2940000C
    movea.l $0004.w,a6                                ; +$0046 : 2C780004
    jsr -666(a6)                                      ; +$004A : 4EAEFD66
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_00100C                                    ; +$0050 : 67000096
    move.l d0,16(a4)                                  ; +$0054 : 29400010
    movea.l (a2),a0                                   ; +$0058 : 2052
    suba.l a1,a1                                      ; +$005A : 93C9
    moveq #1,d0                                       ; +$005C : 7001
    movea.l 4(a2),a6                                  ; +$005E : 2C6A0004
    jsr -768(a6)                                      ; +$0062 : 4EAEFD00
    tst.l d0                                          ; +$0066 : 4A80
    beq.w L_00100C                                    ; +$0068 : 6700007E
    move.l d0,(a4)                                    ; +$006C : 2880
    movea.l (a2),a0                                   ; +$006E : 2052
    suba.l a1,a1                                      ; +$0070 : 93C9
    moveq #2,d0                                       ; +$0072 : 7002
    movea.l 4(a2),a6                                  ; +$0074 : 2C6A0004
    jsr -768(a6)                                      ; +$0078 : 4EAEFD00
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_001000                                    ; +$007E : 6700005C
    move.l d0,4(a4)                                   ; +$0082 : 29400004
    movea.l (a4),a0                                   ; +$0086 : 2054
    movea.l 4(a0),a0                                  ; +$0088 : 20680004
    move.l a0,d0                                      ; +$008C : 2008
    tst.l d0                                          ; +$008E : 4A80
    beq.w L_000FF2                                    ; +$0090 : 6700003C
    move.l 12(a4),d0                                  ; +$0094 : 202C000C
    move.l d0,22(a0)                                  ; +$0098 : 21400016
    move.l 16(a4),d0                                  ; +$009C : 202C0010
    move.l d0,54(a0)                                  ; +$00A0 : 21400036
    movea.l 4(a4),a0                                  ; +$00A4 : 206C0004
    movea.l 4(a0),a0                                  ; +$00A8 : 20680004
    move.l a0,d0                                      ; +$00AC : 2008
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_000FF2                                    ; +$00B0 : 6700001C
    move.l 12(a4),d0                                  ; +$00B4 : 202C000C
    move.l d0,22(a0)                                  ; +$00B8 : 21400016
    move.l 16(a4),d0                                  ; +$00BC : 202C0010
    move.l d0,54(a0)                                  ; +$00C0 : 21400036
    move.l a4,32(a2)                                  ; +$00C4 : 254C0020
L_000FEC:
    moveq #1,d3                                       ; +$00C8 : 7601
    bra.w L_00103A                                    ; +$00CA : 6000004A
L_000FF2:
    movea.l (a2),a0                                   ; +$00CE : 2052
    movea.l 4(a4),a1                                  ; +$00D0 : 226C0004
    movea.l 4(a2),a6                                  ; +$00D4 : 2C6A0004
    jsr -774(a6)                                      ; +$00D8 : 4EAEFCFA
L_001000:
    movea.l (a2),a0                                   ; +$00DC : 2052
    movea.l (a4),a1                                   ; +$00DE : 2254
    movea.l 4(a2),a6                                  ; +$00E0 : 2C6A0004
    jsr -774(a6)                                      ; +$00E4 : 4EAEFCFA
L_00100C:
    movea.l $0004.w,a6                                ; +$00E8 : 2C780004
    movea.l 16(a4),a0                                 ; +$00EC : 206C0010
    move.l a0,d0                                      ; +$00F0 : 2008
    tst.l d0                                          ; +$00F2 : 4A80
    beq.w L_001020                                    ; +$00F4 : 67000006
    jsr -672(a6)                                      ; +$00F8 : 4EAEFD60
L_001020:
    movea.l 12(a4),a0                                 ; +$00FC : 206C000C
    move.l a0,d0                                      ; +$0100 : 2008
    tst.l d0                                          ; +$0102 : 4A80
    beq.w L_001030                                    ; +$0104 : 67000006
    jsr -672(a6)                                      ; +$0108 : 4EAEFD60
L_001030:
    movea.l a4,a1                                     ; +$010C : 224C
    movea.l $0004.w,a6                                ; +$010E : 2C780004
    jsr -690(a6)                                      ; +$0112 : 4EAEFD4E
L_00103A:
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
    beq.w L_0010D8                                    ; +$000C : 67000084
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_0010D8                                    ; +$0018 : 67000078
    move.l 12(a4),d0                                  ; +$001C : 202C000C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0010D8                                    ; +$0022 : 6700006E
    move.l 16(a4),d0                                  ; +$0026 : 202C0010
    tst.l d0                                          ; +$002A : 4A80
    beq.w L_0010D8                                    ; +$002C : 67000064
    bsr.w L_0010E0                                    ; +$0030 : 61000068
    tst.l d0                                          ; +$0034 : 4A80
    bne.w L_0010D8                                    ; +$0036 : 6600005A
    move.l 8(a4),d0                                   ; +$003A : 202C0008
    tst.l d0                                          ; +$003E : 4A80
    beq.w L_001090                                    ; +$0040 : 67000008
    moveq #0,d7                                       ; +$0044 : 7E00
    bra.w L_001092                                    ; +$0046 : 60000004
L_001090:
    moveq #1,d7                                       ; +$004A : 7E01
L_001092:
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0010D8                                    ; +$0054 : 6700003C
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
    tst.l d7                                          ; +$005C : 4A87
    beq.w L_0010B0                                    ; +$005E : 6700000A
    movea.l 4(a4),a1                                  ; +$0062 : 226C0004
    bra.w L_0010B2                                    ; +$0066 : 60000004
L_0010B0:
    movea.l (a4),a1                                   ; +$006A : 2254
L_0010B2:
    move.l a1,d0                                      ; +$006C : 2009
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_0010D8                                    ; +$0070 : 67000020
    movea.l (a2),a0                                   ; +$0074 : 2052
    movea.l 4(a2),a6                                  ; +$0076 : 2C6A0004
    jsr -780(a6)                                      ; +$007A : 4EAEFCF4
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_0010D8                                    ; +$0080 : 67000010
    move.l d7,8(a4)                                   ; +$0084 : 29470008
    move.l #$00000003,20(a4)                          ; +$0088 : 297C000000030014
    moveq #1,d3                                       ; +$0090 : 7601
L_0010D8:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0092 : 4CDF7FF7
    moveq #0,d2                                       ; +$0096 : 7400
    rts                                               ; +$0098 : 4E75
L_0010E0:
    move.l 20(a4),d6                                  ; +$009A : 2C2C0014
    andi.l #$00000003,d6                              ; +$009E : 028600000003
    btst #0,d6                                        ; +$00A4 : 08060000
    beq.w L_001110                                    ; +$00A8 : 67000020
    movea.l 12(a4),a0                                 ; +$00AC : 206C000C
    move.l a0,d0                                      ; +$00B0 : 2008
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_001110                                    ; +$00B4 : 67000014
    movea.l $0004.w,a6                                ; +$00B8 : 2C780004
    jsr -372(a6)                                      ; +$00BC : 4EAEFE8C
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_001110                                    ; +$00C2 : 67000006
    bclr #0,d6                                        ; +$00C6 : 08860000
L_001110:
    btst #1,d6                                        ; +$00CA : 08060001
    beq.w L_001136                                    ; +$00CE : 67000020
    movea.l 16(a4),a0                                 ; +$00D2 : 206C0010
    move.l a0,d0                                      ; +$00D6 : 2008
    tst.l d0                                          ; +$00D8 : 4A80
    beq.w L_001136                                    ; +$00DA : 67000014
    movea.l $0004.w,a6                                ; +$00DE : 2C780004
    jsr -372(a6)                                      ; +$00E2 : 4EAEFE8C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_001136                                    ; +$00E8 : 67000006
    bclr #1,d6                                        ; +$00EC : 08860001
L_001136:
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
    beq.w L_0011D6                                    ; +$000E : 67000084
    tst.l (a2)                                        ; +$0012 : 4A92
    beq.w L_0011D6                                    ; +$0014 : 6700007E
    movea.l 32(a2),a3                                 ; +$0018 : 266A0020
    move.l a3,d0                                      ; +$001C : 200B
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_0011D6                                    ; +$0020 : 67000072
    move.l 8(a3),d0                                   ; +$0024 : 202B0008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_001176                                    ; +$002A : 67000008
    movea.l (a3),a1                                   ; +$002E : 2253
    bra.w L_00117A                                    ; +$0030 : 60000006
L_001176:
    movea.l 4(a3),a1                                  ; +$0034 : 226B0004
L_00117A:
    move.l a1,d0                                      ; +$0038 : 2009
    tst.l d0                                          ; +$003A : 4A80
    beq.w L_0011D6                                    ; +$003C : 67000056
    movea.l (a1),a4                                   ; +$0040 : 2851
    move.l a4,d0                                      ; +$0042 : 200C
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_0011D6                                    ; +$0046 : 6700004C
    move.l #$00000080,d0                              ; +$004A : 203C00000080
    move.l #$00010001,d1                              ; +$0050 : 223C00010001
    movea.l $0004.w,a6                                ; +$0056 : 2C780004
    jsr -684(a6)                                      ; +$005A : 4EAEFD54
    tst.l d0                                          ; +$005E : 4A80
    beq.w L_0011D6                                    ; +$0060 : 67000032
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
L_0011D6:
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
    bsr.w L_001372                                    ; +$011A : 61000076
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_00135C                                    ; +$0120 : 6700005A
    bsr.w L_0014A0                                    ; +$0124 : 6100019A
    tst.l d0                                          ; +$0128 : 4A80
    beq.w L_00135C                                    ; +$012A : 67000050
    bsr.w L_0016F8                                    ; +$012E : 610003E8
    tst.l d0                                          ; +$0132 : 4A80
    beq.w L_00135C                                    ; +$0134 : 67000046
    bsr.w L_001804                                    ; +$0138 : 610004EA
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_00135C                                    ; +$013E : 6700003C
    bsr.w L_001936                                    ; +$0142 : 61000612
    tst.l d0                                          ; +$0146 : 4A80
    beq.w L_00135C                                    ; +$0148 : 67000032
    movea.l (a5),a2                                   ; +$014C : 2455
    movea.l 8(a2),a6                                  ; +$014E : 2C6A0008
    jsr -228(a6)                                      ; +$0152 : 4EAEFF1C
    move.l #$00000001,100(a5)                         ; +$0156 : 2B7C000000010064
    bsr.w L_001804                                    ; +$015E : 610004C4
    tst.l d0                                          ; +$0162 : 4A80
    beq.w L_00135C                                    ; +$0164 : 67000016
    bsr.w L_0019B2                                    ; +$0168 : 61000668
    tst.l d0                                          ; +$016C : 4A80
    beq.w L_00135C                                    ; +$016E : 6700000C
    move.l #$00000001,d3                              ; +$0172 : 263C00000001
    bra.w L_001362                                    ; +$0178 : 60000008
L_00135C:
    move.l #$00000000,d3                              ; +$017C : 263C00000000
L_001362:
    bsr.w L_0019EC                                    ; +$0182 : 61000688
    lea 128(a7),a7                                    ; +$0186 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$018A : 4CDF7FF7
    moveq #0,d2                                       ; +$018E : 7400
    rts                                               ; +$0190 : 4E75
L_001372:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0192 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$0196 : 246D0004
    move.l #$00000000,d4                              ; +$019A : 283C00000000
    move.w (a2)+,d4                                   ; +$01A0 : 381A
    tst.l d4                                          ; +$01A2 : 4A84
    beq.w L_001492                                    ; +$01A4 : 6700010C
    move.l d4,d0                                      ; +$01A8 : 2004
    addq.l #1,d0                                      ; +$01AA : 5280
    move.l #$00010001,d1                              ; +$01AC : 223C00010001
    movea.l $0004.w,a6                                ; +$01B2 : 2C780004
    jsr -684(a6)                                      ; +$01B6 : 4EAEFD54
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_001492                                    ; +$01BC : 670000F4
    move.l d0,12(a5)                                  ; +$01C0 : 2B40000C
    movea.l d0,a1                                     ; +$01C4 : 2240
L_0013A6:
    move.b (a2)+,(a1)+                                ; +$01C6 : 12DA
    subq.l #1,d4                                      ; +$01C8 : 5384
    bne.w L_0013A6                                    ; +$01CA : 6600FFFA
    lea L_001A6C(pc),a1                               ; +$01CE : 43FA06BC
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    movea.l $0004.w,a6                                ; +$01D8 : 2C780004
    jsr -552(a6)                                      ; +$01DC : 4EAEFDD8
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_001492                                    ; +$01E2 : 670000CE
    move.l d0,16(a5)                                  ; +$01E6 : 2B400010
    movea.l d0,a6                                     ; +$01EA : 2C40
    move.l 12(a5),d1                                  ; +$01EC : 222D000C
    move.l #$000003ED,d2                              ; +$01F0 : 243C000003ED
    jsr -30(a6)                                       ; +$01F6 : 4EAEFFE2
    tst.l d0                                          ; +$01FA : 4A80
    beq.w L_001492                                    ; +$01FC : 670000B4
    move.l d0,20(a5)                                  ; +$0200 : 2B400014
    move.l d0,d1                                      ; +$0204 : 2200
    move.l a5,d2                                      ; +$0206 : 240D
    addi.l #$00000068,d2                              ; +$0208 : 068200000068
    move.l #$0000000C,d3                              ; +$020E : 263C0000000C
    jsr -42(a6)                                       ; +$0214 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$0218 : 0C800000000C
    bne.w L_001492                                    ; +$021E : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0222 : 0CAD464F524D0068
    bne.w L_001492                                    ; +$022A : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$022E : 0CAD494C424D0070
    bne.w L_001492                                    ; +$0236 : 6600007A
    move.l 108(a5),d4                                 ; +$023A : 282D006C
    cmpi.l #$00000004,d4                              ; +$023E : 0C8400000004
    bcs.w L_001492                                    ; +$0244 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$0248 : 0C847FFFFFF7
    bhi.w L_001492                                    ; +$024E : 62000062
    addq.l #8,d4                                      ; +$0252 : 5084
    move.l d4,28(a5)                                  ; +$0254 : 2B44001C
    move.l d4,d0                                      ; +$0258 : 2004
    move.l #$00010001,d1                              ; +$025A : 223C00010001
    movea.l $0004.w,a6                                ; +$0260 : 2C780004
    jsr -684(a6)                                      ; +$0264 : 4EAEFD54
    tst.l d0                                          ; +$0268 : 4A80
    beq.w L_001492                                    ; +$026A : 67000046
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
    bne.w L_001492                                    ; +$02A4 : 6600000C
    move.l #$00000001,d0                              ; +$02A8 : 203C00000001
    bra.w L_001498                                    ; +$02AE : 60000008
L_001492:
    move.l #$00000000,d0                              ; +$02B2 : 203C00000000
L_001498:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$02B8 : 4CDF5FFE
    tst.l d0                                          ; +$02BC : 4A80
    rts                                               ; +$02BE : 4E75
L_0014A0:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$02C0 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$02C4 : 206D0018
    move.l 28(a5),d7                                  ; +$02C8 : 2E2D001C
    subi.l #$0000000C,d7                              ; +$02CC : 04870000000C
    move.l a0,d0                                      ; +$02D2 : 2008
    addi.l #$0000000C,d0                              ; +$02D4 : 06800000000C
    movea.l d0,a0                                     ; +$02DA : 2040
L_0014BC:
    tst.l d7                                          ; +$02DC : 4A87
    beq.w L_001580                                    ; +$02DE : 670000C0
    cmpi.l #$00000008,d7                              ; +$02E2 : 0C8700000008
    bcs.w L_0016EA                                    ; +$02E8 : 65000220
    move.l (a0)+,d3                                   ; +$02EC : 2618
    move.l (a0)+,d2                                   ; +$02EE : 2418
    subq.l #8,d7                                      ; +$02F0 : 5187
    cmp.l d7,d2                                       ; +$02F2 : B487
    bhi.w L_0016EA                                    ; +$02F4 : 62000214
    move.l d2,d1                                      ; +$02F8 : 2202
    andi.l #$00000001,d1                              ; +$02FA : 028100000001
    add.l d2,d1                                       ; +$0300 : D282
    cmp.l d7,d1                                       ; +$0302 : B287
    bhi.w L_0016EA                                    ; +$0304 : 62000204
    sub.l d1,d7                                       ; +$0308 : 9E81
    cmpi.l #$424D4844,d3                              ; +$030A : 0C83424D4844
    beq.w L_001516                                    ; +$0310 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0314 : 0C83434D4150
    beq.w L_001530                                    ; +$031A : 67000034
    cmpi.l #$43414D47,d3                              ; +$031E : 0C8343414D47
    beq.w L_001558                                    ; +$0324 : 67000052
    cmpi.l #$424F4459,d3                              ; +$0328 : 0C83424F4459
    beq.w L_001544                                    ; +$032E : 67000034
    bra.w L_001576                                    ; +$0332 : 60000062
L_001516:
    tst.l 32(a5)                                      ; +$0336 : 4AAD0020
    bne.w L_0016EA                                    ; +$033A : 660001CE
    cmpi.l #$00000014,d2                              ; +$033E : 0C8200000014
    bne.w L_0016EA                                    ; +$0344 : 660001C4
    move.l a0,32(a5)                                  ; +$0348 : 2B480020
    bra.w L_001576                                    ; +$034C : 60000048
L_001530:
    tst.l 36(a5)                                      ; +$0350 : 4AAD0024
    bne.w L_0016EA                                    ; +$0354 : 660001B4
    move.l a0,36(a5)                                  ; +$0358 : 2B480024
    move.l d2,40(a5)                                  ; +$035C : 2B420028
    bra.w L_001576                                    ; +$0360 : 60000034
L_001544:
    tst.l 44(a5)                                      ; +$0364 : 4AAD002C
    bne.w L_0016EA                                    ; +$0368 : 660001A0
    move.l a0,44(a5)                                  ; +$036C : 2B48002C
    move.l d2,48(a5)                                  ; +$0370 : 2B420030
    bra.w L_001576                                    ; +$0374 : 60000020
L_001558:
    tst.l 52(a5)                                      ; +$0378 : 4AAD0034
    bne.w L_0016EA                                    ; +$037C : 6600018C
    cmpi.l #$00000004,d2                              ; +$0380 : 0C8200000004
    bne.w L_0016EA                                    ; +$0386 : 66000182
    move.l #$00000001,52(a5)                          ; +$038A : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$0392 : 2B50005C
L_001576:
    move.l a0,d0                                      ; +$0396 : 2008
    add.l d1,d0                                       ; +$0398 : D081
    movea.l d0,a0                                     ; +$039A : 2040
    bra.w L_0014BC                                    ; +$039C : 6000FF3E
L_001580:
    tst.l 32(a5)                                      ; +$03A0 : 4AAD0020
    beq.w L_0016EA                                    ; +$03A4 : 67000164
    tst.l 36(a5)                                      ; +$03A8 : 4AAD0024
    beq.w L_0016EA                                    ; +$03AC : 6700015C
    tst.l 44(a5)                                      ; +$03B0 : 4AAD002C
    beq.w L_0016EA                                    ; +$03B4 : 67000154
    tst.l 48(a5)                                      ; +$03B8 : 4AAD0030
    beq.w L_0016EA                                    ; +$03BC : 6700014C
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
    beq.w L_0016EA                                    ; +$040C : 670000FC
    tst.l 60(a5)                                      ; +$0410 : 4AAD003C
    beq.w L_0016EA                                    ; +$0414 : 670000F4
    tst.l 64(a5)                                      ; +$0418 : 4AAD0040
    beq.w L_0016EA                                    ; +$041C : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0420 : 0CAD000000080040
    bhi.w L_0016EA                                    ; +$0428 : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$042C : 0CAD000000020044
    bhi.w L_0016EA                                    ; +$0434 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$0438 : 0CAD000000010048
    bhi.w L_0016EA                                    ; +$0440 : 620000C8
    move.l 40(a5),d0                                  ; +$0444 : 202D0028
    tst.l d0                                          ; +$0448 : 4A80
    beq.w L_0016EA                                    ; +$044A : 670000BE
    cmpi.l #$00000300,d0                              ; +$044E : 0C8000000300
    bhi.w L_0016EA                                    ; +$0454 : 620000B4
    divu.w #$0003,d0                                  ; +$0458 : 80FC0003
    move.l d0,d1                                      ; +$045C : 2200
    swap d1                                           ; +$045E : 4841
    tst.w d1                                          ; +$0460 : 4A41
    bne.w L_0016EA                                    ; +$0462 : 660000A6
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
    bne.w L_00167C                                    ; +$048E : 6600000C
    andi.l #$00008EFD,d0                              ; +$0492 : 028000008EFD
    bra.w L_001688                                    ; +$0498 : 6000000E
L_00167C:
    move.l d0,d1                                      ; +$049C : 2200
    andi.l #$00001000,d1                              ; +$049E : 028100001000
    beq.w L_0016EA                                    ; +$04A4 : 67000064
L_001688:
    move.l d0,52(a5)                                  ; +$04A8 : 2B400034
    move.l d0,d1                                      ; +$04AC : 2200
    andi.l #$00000400,d1                              ; +$04AE : 028100000400
    bne.w L_0016EA                                    ; +$04B4 : 66000054
    move.l d0,d1                                      ; +$04B8 : 2200
    andi.l #$00000800,d1                              ; +$04BA : 028100000800
    beq.w L_0016CA                                    ; +$04C0 : 67000028
    andi.l #$00000080,d0                              ; +$04C4 : 028000000080
    bne.w L_0016EA                                    ; +$04CA : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$04CE : 0CAD000000060040
    beq.w L_0016C6                                    ; +$04D6 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$04DA : 0CAD000000080040
    bne.w L_0016EA                                    ; +$04E2 : 66000026
L_0016C6:
    bra.w L_0016E0                                    ; +$04E6 : 60000018
L_0016CA:
    andi.l #$00000080,d0                              ; +$04EA : 028000000080
    beq.w L_0016E0                                    ; +$04F0 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$04F4 : 0CAD000000060040
    bne.w L_0016EA                                    ; +$04FC : 6600000C
L_0016E0:
    move.l #$00000001,d0                              ; +$0500 : 203C00000001
    bra.w L_0016F0                                    ; +$0506 : 60000008
L_0016EA:
    move.l #$00000000,d0                              ; +$050A : 203C00000000
L_0016F0:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0510 : 4CDF5FFE
    tst.l d0                                          ; +$0514 : 4A80
    rts                                               ; +$0516 : 4E75
L_0016F8:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0518 : 48E77FFA
    movea.l (a5),a2                                   ; +$051C : 2455
    move.l a2,d0                                      ; +$051E : 200A
    tst.l d0                                          ; +$0520 : 4A80
    beq.w L_0017F6                                    ; +$0522 : 670000F2
    move.l (a2),d0                                    ; +$0526 : 2012
    tst.l d0                                          ; +$0528 : 4A80
    beq.w L_0017F6                                    ; +$052A : 670000EA
    move.l d0,88(a5)                                  ; +$052E : 2B400058
    tst.l 8(a2)                                       ; +$0532 : 4AAA0008
    beq.w L_0017F6                                    ; +$0536 : 670000DE
    move.l 12(a2),d0                                  ; +$053A : 202A000C
    cmp.l 56(a5),d0                                   ; +$053E : B0AD0038
    bne.w L_0017F6                                    ; +$0542 : 660000D2
    move.l 16(a2),d0                                  ; +$0546 : 202A0010
    cmp.l 60(a5),d0                                   ; +$054A : B0AD003C
    bne.w L_0017F6                                    ; +$054E : 660000C6
    move.l 28(a2),d0                                  ; +$0552 : 202A001C
    cmp.l 64(a5),d0                                   ; +$0556 : B0AD0040
    bne.w L_0017F6                                    ; +$055A : 660000BA
    move.l 24(a2),d0                                  ; +$055E : 202A0018
    move.l 52(a5),d1                                  ; +$0562 : 222D0034
    move.l d1,d2                                      ; +$0566 : 2401
    andi.l #$FFFF0000,d2                              ; +$0568 : 0282FFFF0000
    bne.w L_001758                                    ; +$056E : 66000008
    andi.l #$00008EFD,d0                              ; +$0572 : 028000008EFD
L_001758:
    cmp.l d1,d0                                       ; +$0578 : B081
    bne.w L_0017F6                                    ; +$057A : 6600009A
    movea.l 32(a2),a3                                 ; +$057E : 266A0020
    move.l a3,d0                                      ; +$0582 : 200B
    tst.l d0                                          ; +$0584 : 4A80
    beq.w L_0017F6                                    ; +$0586 : 6700008E
    tst.l 8(a3)                                       ; +$058A : 4AAB0008
    beq.w L_001778                                    ; +$058E : 67000008
    movea.l (a3),a0                                   ; +$0592 : 2053
    bra.w L_00177C                                    ; +$0594 : 60000006
L_001778:
    movea.l 4(a3),a0                                  ; +$0598 : 206B0004
L_00177C:
    move.l a0,d0                                      ; +$059C : 2008
    tst.l d0                                          ; +$059E : 4A80
    beq.w L_0017F6                                    ; +$05A0 : 67000074
    movea.l (a0),a3                                   ; +$05A4 : 2650
    move.l a3,d0                                      ; +$05A6 : 200B
    tst.l d0                                          ; +$05A8 : 4A80
    beq.w L_0017F6                                    ; +$05AA : 6700006A
    move.l d0,80(a5)                                  ; +$05AE : 2B400050
    move.l #$00000000,d0                              ; +$05B2 : 203C00000000
    move.w (a3),d0                                    ; +$05B8 : 3013
    cmp.l 76(a5),d0                                   ; +$05BA : B0AD004C
    bcs.w L_0017F6                                    ; +$05BE : 65000056
    move.l d0,84(a5)                                  ; +$05C2 : 2B400054
    move.l #$00000000,d0                              ; +$05C6 : 203C00000000
    move.w 2(a3),d0                                   ; +$05CC : 302B0002
    cmp.l 60(a5),d0                                   ; +$05D0 : B0AD003C
    bcs.w L_0017F6                                    ; +$05D4 : 65000040
    move.l #$00000000,d0                              ; +$05D8 : 203C00000000
    move.b 5(a3),d0                                   ; +$05DE : 102B0005
    cmp.l 64(a5),d0                                   ; +$05E2 : B0AD0040
    bne.w L_0017F6                                    ; +$05E6 : 6600002E
    move.l a3,d0                                      ; +$05EA : 200B
    addq.l #8,d0                                      ; +$05EC : 5080
    movea.l d0,a0                                     ; +$05EE : 2040
    move.l 64(a5),d1                                  ; +$05F0 : 222D0040
L_0017D4:
    move.l (a0)+,d0                                   ; +$05F4 : 2018
    tst.l d0                                          ; +$05F6 : 4A80
    beq.w L_0017F6                                    ; +$05F8 : 6700001C
    cmpi.l #$FFFFFFFF,d0                              ; +$05FC : 0C80FFFFFFFF
    beq.w L_0017F6                                    ; +$0602 : 67000012
    subq.l #1,d1                                      ; +$0606 : 5381
    bne.w L_0017D4                                    ; +$0608 : 6600FFEA
    move.l #$00000001,d0                              ; +$060C : 203C00000001
    bra.w L_0017FC                                    ; +$0612 : 60000008
L_0017F6:
    move.l #$00000000,d0                              ; +$0616 : 203C00000000
L_0017FC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$061C : 4CDF5FFE
    tst.l d0                                          ; +$0620 : 4A80
    rts                                               ; +$0622 : 4E75
L_001804:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0624 : 48E77FFA
    movea.l 44(a5),a0                                 ; +$0628 : 206D002C
    move.l a0,d0                                      ; +$062C : 2008
    add.l 48(a5),d0                                   ; +$062E : D0AD0030
    movea.l d0,a2                                     ; +$0632 : 2440
    move.l #$00000000,d4                              ; +$0634 : 283C00000000
    move.l #$00000000,d3                              ; +$063A : 263C00000000
L_001820:
    move.l #$00000000,d5                              ; +$0640 : 2A3C00000000
    movea.l 80(a5),a3                                 ; +$0646 : 266D0050
    move.l a3,d0                                      ; +$064A : 200B
    addq.l #8,d0                                      ; +$064C : 5080
    movea.l d0,a4                                     ; +$064E : 2840
L_001830:
    move.l 76(a5),d6                                  ; +$0650 : 2C2D004C
    movea.l #$00000000,a6                             ; +$0654 : 2C7C00000000
    cmp.l 64(a5),d5                                   ; +$065A : BAAD0040
    bcc.w L_001850                                    ; +$065E : 64000010
    tst.l 100(a5)                                     ; +$0662 : 4AAD0064
    beq.w L_001850                                    ; +$0666 : 67000008
    move.l (a4)+,d0                                   ; +$066A : 201C
    add.l d3,d0                                       ; +$066C : D083
    movea.l d0,a6                                     ; +$066E : 2C40
L_001850:
    tst.l 72(a5)                                      ; +$0670 : 4AAD0048
    beq.w L_00187E                                    ; +$0674 : 67000028
    move.l a0,d0                                      ; +$0678 : 2008
    cmp.l a2,d0                                       ; +$067A : B08A
    bcc.w L_001928                                    ; +$067C : 640000CA
    move.l #$00000000,d1                              ; +$0680 : 223C00000000
    move.b (a0)+,d1                                   ; +$0686 : 1218
    cmpi.l #$00000080,d1                              ; +$0688 : 0C8100000080
    beq.w L_001850                                    ; +$068E : 6700FFE0
    bhi.w L_0018AA                                    ; +$0692 : 62000036
    addq.l #1,d1                                      ; +$0696 : 5281
    move.l d1,d2                                      ; +$0698 : 2401
    bra.w L_001882                                    ; +$069A : 60000006
L_00187E:
    move.l d6,d1                                      ; +$069E : 2206
    move.l d1,d2                                      ; +$06A0 : 2401
L_001882:
    cmp.l d6,d1                                       ; +$06A2 : B286
    bhi.w L_001928                                    ; +$06A4 : 620000A2
    move.l a2,d0                                      ; +$06A8 : 200A
    sub.l a0,d0                                       ; +$06AA : 9088
    cmp.l d1,d0                                       ; +$06AC : B081
    bcs.w L_001928                                    ; +$06AE : 65000098
    sub.l d1,d6                                       ; +$06B2 : 9C81
L_001894:
    move.b (a0)+,d0                                   ; +$06B4 : 1018
    move.l a6,d7                                      ; +$06B6 : 2E0E
    tst.l d7                                          ; +$06B8 : 4A87
    beq.w L_0018A0                                    ; +$06BA : 67000004
    move.b d0,(a6)+                                   ; +$06BE : 1CC0
L_0018A0:
    subq.l #1,d2                                      ; +$06C0 : 5382
    bne.w L_001894                                    ; +$06C2 : 6600FFF0
    bra.w L_0018D4                                    ; +$06C6 : 6000002C
L_0018AA:
    move.l #$00000101,d2                              ; +$06CA : 243C00000101
    sub.l d1,d2                                       ; +$06D0 : 9481
    cmp.l d6,d2                                       ; +$06D2 : B486
    bhi.w L_001928                                    ; +$06D4 : 62000072
    sub.l d2,d6                                       ; +$06D8 : 9C82
    move.l a0,d0                                      ; +$06DA : 2008
    cmp.l a2,d0                                       ; +$06DC : B08A
    bcc.w L_001928                                    ; +$06DE : 64000068
    move.b (a0)+,d0                                   ; +$06E2 : 1018
L_0018C4:
    move.l a6,d7                                      ; +$06E4 : 2E0E
    tst.l d7                                          ; +$06E6 : 4A87
    beq.w L_0018CE                                    ; +$06E8 : 67000004
    move.b d0,(a6)+                                   ; +$06EC : 1CC0
L_0018CE:
    subq.l #1,d2                                      ; +$06EE : 5382
    bne.w L_0018C4                                    ; +$06F0 : 6600FFF2
L_0018D4:
    tst.l d6                                          ; +$06F4 : 4A86
    bne.w L_001850                                    ; +$06F6 : 6600FF78
    addq.l #1,d5                                      ; +$06FA : 5285
    move.l 64(a5),d0                                  ; +$06FC : 202D0040
    cmpi.l #$00000001,68(a5)                          ; +$0700 : 0CAD000000010044
    bne.w L_0018EE                                    ; +$0708 : 66000004
    addq.l #1,d0                                      ; +$070C : 5280
L_0018EE:
    cmp.l d0,d5                                       ; +$070E : BA80
    bcs.w L_001830                                    ; +$0710 : 6500FF3E
    add.l 84(a5),d3                                   ; +$0714 : D6AD0054
    addq.l #1,d4                                      ; +$0718 : 5284
    cmp.l 60(a5),d4                                   ; +$071A : B8AD003C
    bcs.w L_001820                                    ; +$071E : 6500FF20
L_001902:
    move.l a0,d0                                      ; +$0722 : 2008
    cmp.l a2,d0                                       ; +$0724 : B08A
    beq.w L_00191E                                    ; +$0726 : 67000016
    tst.l 72(a5)                                      ; +$072A : 4AAD0048
    beq.w L_001928                                    ; +$072E : 67000018
    cmpi.b #$80,(a0)+                                 ; +$0732 : 0C180080
    bne.w L_001928                                    ; +$0736 : 66000010
    bra.w L_001902                                    ; +$073A : 6000FFE6
L_00191E:
    move.l #$00000001,d0                              ; +$073E : 203C00000001
    bra.w L_00192E                                    ; +$0744 : 60000008
L_001928:
    move.l #$00000000,d0                              ; +$0748 : 203C00000000
L_00192E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$074E : 4CDF5FFE
    tst.l d0                                          ; +$0752 : 4A80
    rts                                               ; +$0754 : 4E75
L_001936:
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
    beq.w L_0019A4                                    ; +$0778 : 6700004A
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
L_001978:
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
    bne.w L_001978                                    ; +$07B0 : 6600FFE6
    move.l #$00000000,(a1)                            ; +$07B4 : 22BC00000000
    move.l #$00000001,d0                              ; +$07BA : 203C00000001
    bra.w L_0019AA                                    ; +$07C0 : 60000008
L_0019A4:
    move.l #$00000000,d0                              ; +$07C4 : 203C00000000
L_0019AA:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$07CA : 4CDF5FFE
    tst.l d0                                          ; +$07CE : 4A80
    rts                                               ; +$07D0 : 4E75
L_0019B2:
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
    bra.w L_0019E4                                    ; +$07FA : 60000008
    move.l #$00000000,d0                              ; +$07FE : 203C00000000
L_0019E4:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0804 : 4CDF5FFE
    tst.l d0                                          ; +$0808 : 4A80
    rts                                               ; +$080A : 4E75
L_0019EC:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$080C : 48E77FFA
    tst.l 20(a5)                                      ; +$0810 : 4AAD0014
    beq.w L_001A04                                    ; +$0814 : 6700000E
    movea.l 16(a5),a6                                 ; +$0818 : 2C6D0010
    move.l 20(a5),d1                                  ; +$081C : 222D0014
    jsr -36(a6)                                       ; +$0820 : 4EAEFFDC
L_001A04:
    tst.l 96(a5)                                      ; +$0824 : 4AAD0060
    beq.w L_001A18                                    ; +$0828 : 6700000E
    movea.l 96(a5),a1                                 ; +$082C : 226D0060
    movea.l $0004.w,a6                                ; +$0830 : 2C780004
    jsr -690(a6)                                      ; +$0834 : 4EAEFD4E
L_001A18:
    tst.l 24(a5)                                      ; +$0838 : 4AAD0018
    beq.w L_001A2C                                    ; +$083C : 6700000E
    movea.l 24(a5),a1                                 ; +$0840 : 226D0018
    movea.l $0004.w,a6                                ; +$0844 : 2C780004
    jsr -690(a6)                                      ; +$0848 : 4EAEFD4E
L_001A2C:
    tst.l 12(a5)                                      ; +$084C : 4AAD000C
    beq.w L_001A40                                    ; +$0850 : 6700000E
    movea.l 12(a5),a1                                 ; +$0854 : 226D000C
    movea.l $0004.w,a6                                ; +$0858 : 2C780004
    jsr -690(a6)                                      ; +$085C : 4EAEFD4E
L_001A40:
    tst.l 16(a5)                                      ; +$0860 : 4AAD0010
    beq.w L_001A54                                    ; +$0864 : 6700000E
    movea.l 16(a5),a1                                 ; +$0868 : 226D0010
    movea.l $0004.w,a6                                ; +$086C : 2C780004
    jsr -414(a6)                                      ; +$0870 : 4EAEFE62
L_001A54:
    move.l #$00000001,d0                              ; +$0874 : 203C00000001
    bra.w L_001A64                                    ; +$087A : 60000008
    move.l #$00000000,d0                              ; +$087E : 203C00000000
L_001A64:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0884 : 4CDF5FFE
    tst.l d0                                          ; +$0888 : 4A80
    rts                                               ; +$088A : 4E75
L_001A6C:
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
    bhi.w L_001C5A                                    ; +$0124 : 620000B8
    bsr.w L_001C70                                    ; +$0128 : 610000CA
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_001C5A                                    ; +$012E : 670000AE
    bsr.w L_001D9E                                    ; +$0132 : 610001EE
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_001C5A                                    ; +$0138 : 670000A4
    cmpi.l #$00000000,8(a5)                           ; +$013C : 0CAD000000000008
    beq.w L_001C22                                    ; +$0144 : 67000060
    cmpi.l #$00000001,8(a5)                           ; +$0148 : 0CAD000000010008
    beq.w L_001C2A                                    ; +$0150 : 6700005C
    cmpi.l #$00000002,8(a5)                           ; +$0154 : 0CAD000000020008
    beq.w L_001C32                                    ; +$015C : 67000058
    cmpi.l #$00000003,8(a5)                           ; +$0160 : 0CAD000000030008
    beq.w L_001C3A                                    ; +$0168 : 67000054
    cmpi.l #$00000004,8(a5)                           ; +$016C : 0CAD000000040008
    beq.w L_001C42                                    ; +$0174 : 67000050
    cmpi.l #$00000005,8(a5)                           ; +$0178 : 0CAD000000050008
    beq.w L_001C4A                                    ; +$0180 : 6700004C
    cmpi.l #$00000006,8(a5)                           ; +$0184 : 0CAD000000060008
    beq.w L_001C52                                    ; +$018C : 67000048
    move.l #$00000001,d3                              ; +$0190 : 263C00000001
    move.l 64(a5),d0                                  ; +$0196 : 202D0040
L_001C16:
    lsl.l #1,d3                                       ; +$019A : E38B
    subq.l #1,d0                                      ; +$019C : 5380
    bne.w L_001C16                                    ; +$019E : 6600FFFA
    bra.w L_001C60                                    ; +$01A2 : 60000040
L_001C22:
    move.l 56(a5),d3                                  ; +$01A6 : 262D0038
    bra.w L_001C60                                    ; +$01AA : 60000038
L_001C2A:
    move.l 60(a5),d3                                  ; +$01AE : 262D003C
    bra.w L_001C60                                    ; +$01B2 : 60000030
L_001C32:
    move.l 64(a5),d3                                  ; +$01B6 : 262D0040
    bra.w L_001C60                                    ; +$01BA : 60000028
L_001C3A:
    move.l 40(a5),d3                                  ; +$01BE : 262D0028
    bra.w L_001C60                                    ; +$01C2 : 60000020
L_001C42:
    move.l 72(a5),d3                                  ; +$01C6 : 262D0048
    bra.w L_001C60                                    ; +$01CA : 60000018
L_001C4A:
    move.l 92(a5),d3                                  ; +$01CE : 262D005C
    bra.w L_001C60                                    ; +$01D2 : 60000010
L_001C52:
    move.l 52(a5),d3                                  ; +$01D6 : 262D0034
    bra.w L_001C60                                    ; +$01DA : 60000008
L_001C5A:
    move.l #$FFFFFFFF,d3                              ; +$01DE : 263CFFFFFFFF
L_001C60:
    bsr.w L_001FF6                                    ; +$01E4 : 61000394
    lea 128(a7),a7                                    ; +$01E8 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01EC : 4CDF77F7
    moveq #0,d2                                       ; +$01F0 : 7400
    rts                                               ; +$01F2 : 4E75
L_001C70:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$01F4 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$01F8 : 246D0004
    move.l #$00000000,d4                              ; +$01FC : 283C00000000
    move.w (a2)+,d4                                   ; +$0202 : 381A
    tst.l d4                                          ; +$0204 : 4A84
    beq.w L_001D90                                    ; +$0206 : 6700010C
    move.l d4,d0                                      ; +$020A : 2004
    addq.l #1,d0                                      ; +$020C : 5280
    move.l #$00010001,d1                              ; +$020E : 223C00010001
    movea.l $0004.w,a6                                ; +$0214 : 2C780004
    jsr -684(a6)                                      ; +$0218 : 4EAEFD54
    tst.l d0                                          ; +$021C : 4A80
    beq.w L_001D90                                    ; +$021E : 670000F4
    move.l d0,12(a5)                                  ; +$0222 : 2B40000C
    movea.l d0,a1                                     ; +$0226 : 2240
L_001CA4:
    move.b (a2)+,(a1)+                                ; +$0228 : 12DA
    subq.l #1,d4                                      ; +$022A : 5384
    bne.w L_001CA4                                    ; +$022C : 6600FFFA
    lea L_002076(pc),a1                               ; +$0230 : 43FA03C8
    move.l #$00000000,d0                              ; +$0234 : 203C00000000
    movea.l $0004.w,a6                                ; +$023A : 2C780004
    jsr -552(a6)                                      ; +$023E : 4EAEFDD8
    tst.l d0                                          ; +$0242 : 4A80
    beq.w L_001D90                                    ; +$0244 : 670000CE
    move.l d0,16(a5)                                  ; +$0248 : 2B400010
    movea.l d0,a6                                     ; +$024C : 2C40
    move.l 12(a5),d1                                  ; +$024E : 222D000C
    move.l #$000003ED,d2                              ; +$0252 : 243C000003ED
    jsr -30(a6)                                       ; +$0258 : 4EAEFFE2
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_001D90                                    ; +$025E : 670000B4
    move.l d0,20(a5)                                  ; +$0262 : 2B400014
    move.l d0,d1                                      ; +$0266 : 2200
    move.l a5,d2                                      ; +$0268 : 240D
    addi.l #$00000068,d2                              ; +$026A : 068200000068
    move.l #$0000000C,d3                              ; +$0270 : 263C0000000C
    jsr -42(a6)                                       ; +$0276 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$027A : 0C800000000C
    bne.w L_001D90                                    ; +$0280 : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0284 : 0CAD464F524D0068
    bne.w L_001D90                                    ; +$028C : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$0290 : 0CAD494C424D0070
    bne.w L_001D90                                    ; +$0298 : 6600007A
    move.l 108(a5),d4                                 ; +$029C : 282D006C
    cmpi.l #$00000004,d4                              ; +$02A0 : 0C8400000004
    bcs.w L_001D90                                    ; +$02A6 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$02AA : 0C847FFFFFF7
    bhi.w L_001D90                                    ; +$02B0 : 62000062
    addq.l #8,d4                                      ; +$02B4 : 5084
    move.l d4,28(a5)                                  ; +$02B6 : 2B44001C
    move.l d4,d0                                      ; +$02BA : 2004
    move.l #$00010001,d1                              ; +$02BC : 223C00010001
    movea.l $0004.w,a6                                ; +$02C2 : 2C780004
    jsr -684(a6)                                      ; +$02C6 : 4EAEFD54
    tst.l d0                                          ; +$02CA : 4A80
    beq.w L_001D90                                    ; +$02CC : 67000046
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
    bne.w L_001D90                                    ; +$0306 : 6600000C
    move.l #$00000001,d0                              ; +$030A : 203C00000001
    bra.w L_001D96                                    ; +$0310 : 60000008
L_001D90:
    move.l #$00000000,d0                              ; +$0314 : 203C00000000
L_001D96:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$031A : 4CDF5FFE
    tst.l d0                                          ; +$031E : 4A80
    rts                                               ; +$0320 : 4E75
L_001D9E:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0322 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$0326 : 206D0018
    move.l 28(a5),d7                                  ; +$032A : 2E2D001C
    subi.l #$0000000C,d7                              ; +$032E : 04870000000C
    move.l a0,d0                                      ; +$0334 : 2008
    addi.l #$0000000C,d0                              ; +$0336 : 06800000000C
    movea.l d0,a0                                     ; +$033C : 2040
L_001DBA:
    tst.l d7                                          ; +$033E : 4A87
    beq.w L_001E7E                                    ; +$0340 : 670000C0
    cmpi.l #$00000008,d7                              ; +$0344 : 0C8700000008
    bcs.w L_001FE8                                    ; +$034A : 65000220
    move.l (a0)+,d3                                   ; +$034E : 2618
    move.l (a0)+,d2                                   ; +$0350 : 2418
    subq.l #8,d7                                      ; +$0352 : 5187
    cmp.l d7,d2                                       ; +$0354 : B487
    bhi.w L_001FE8                                    ; +$0356 : 62000214
    move.l d2,d1                                      ; +$035A : 2202
    andi.l #$00000001,d1                              ; +$035C : 028100000001
    add.l d2,d1                                       ; +$0362 : D282
    cmp.l d7,d1                                       ; +$0364 : B287
    bhi.w L_001FE8                                    ; +$0366 : 62000204
    sub.l d1,d7                                       ; +$036A : 9E81
    cmpi.l #$424D4844,d3                              ; +$036C : 0C83424D4844
    beq.w L_001E14                                    ; +$0372 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0376 : 0C83434D4150
    beq.w L_001E2E                                    ; +$037C : 67000034
    cmpi.l #$43414D47,d3                              ; +$0380 : 0C8343414D47
    beq.w L_001E56                                    ; +$0386 : 67000052
    cmpi.l #$424F4459,d3                              ; +$038A : 0C83424F4459
    beq.w L_001E42                                    ; +$0390 : 67000034
    bra.w L_001E74                                    ; +$0394 : 60000062
L_001E14:
    tst.l 32(a5)                                      ; +$0398 : 4AAD0020
    bne.w L_001FE8                                    ; +$039C : 660001CE
    cmpi.l #$00000014,d2                              ; +$03A0 : 0C8200000014
    bne.w L_001FE8                                    ; +$03A6 : 660001C4
    move.l a0,32(a5)                                  ; +$03AA : 2B480020
    bra.w L_001E74                                    ; +$03AE : 60000048
L_001E2E:
    tst.l 36(a5)                                      ; +$03B2 : 4AAD0024
    bne.w L_001FE8                                    ; +$03B6 : 660001B4
    move.l a0,36(a5)                                  ; +$03BA : 2B480024
    move.l d2,40(a5)                                  ; +$03BE : 2B420028
    bra.w L_001E74                                    ; +$03C2 : 60000034
L_001E42:
    tst.l 44(a5)                                      ; +$03C6 : 4AAD002C
    bne.w L_001FE8                                    ; +$03CA : 660001A0
    move.l a0,44(a5)                                  ; +$03CE : 2B48002C
    move.l d2,48(a5)                                  ; +$03D2 : 2B420030
    bra.w L_001E74                                    ; +$03D6 : 60000020
L_001E56:
    tst.l 52(a5)                                      ; +$03DA : 4AAD0034
    bne.w L_001FE8                                    ; +$03DE : 6600018C
    cmpi.l #$00000004,d2                              ; +$03E2 : 0C8200000004
    bne.w L_001FE8                                    ; +$03E8 : 66000182
    move.l #$00000001,52(a5)                          ; +$03EC : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$03F4 : 2B50005C
L_001E74:
    move.l a0,d0                                      ; +$03F8 : 2008
    add.l d1,d0                                       ; +$03FA : D081
    movea.l d0,a0                                     ; +$03FC : 2040
    bra.w L_001DBA                                    ; +$03FE : 6000FF3E
L_001E7E:
    tst.l 32(a5)                                      ; +$0402 : 4AAD0020
    beq.w L_001FE8                                    ; +$0406 : 67000164
    tst.l 36(a5)                                      ; +$040A : 4AAD0024
    beq.w L_001FE8                                    ; +$040E : 6700015C
    tst.l 44(a5)                                      ; +$0412 : 4AAD002C
    beq.w L_001FE8                                    ; +$0416 : 67000154
    tst.l 48(a5)                                      ; +$041A : 4AAD0030
    beq.w L_001FE8                                    ; +$041E : 6700014C
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
    beq.w L_001FE8                                    ; +$046E : 670000FC
    tst.l 60(a5)                                      ; +$0472 : 4AAD003C
    beq.w L_001FE8                                    ; +$0476 : 670000F4
    tst.l 64(a5)                                      ; +$047A : 4AAD0040
    beq.w L_001FE8                                    ; +$047E : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0482 : 0CAD000000080040
    bhi.w L_001FE8                                    ; +$048A : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$048E : 0CAD000000020044
    bhi.w L_001FE8                                    ; +$0496 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$049A : 0CAD000000010048
    bhi.w L_001FE8                                    ; +$04A2 : 620000C8
    move.l 40(a5),d0                                  ; +$04A6 : 202D0028
    tst.l d0                                          ; +$04AA : 4A80
    beq.w L_001FE8                                    ; +$04AC : 670000BE
    cmpi.l #$00000300,d0                              ; +$04B0 : 0C8000000300
    bhi.w L_001FE8                                    ; +$04B6 : 620000B4
    divu.w #$0003,d0                                  ; +$04BA : 80FC0003
    move.l d0,d1                                      ; +$04BE : 2200
    swap d1                                           ; +$04C0 : 4841
    tst.w d1                                          ; +$04C2 : 4A41
    bne.w L_001FE8                                    ; +$04C4 : 660000A6
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
    bne.w L_001F7A                                    ; +$04F0 : 6600000C
    andi.l #$00008EFD,d0                              ; +$04F4 : 028000008EFD
    bra.w L_001F86                                    ; +$04FA : 6000000E
L_001F7A:
    move.l d0,d1                                      ; +$04FE : 2200
    andi.l #$00001000,d1                              ; +$0500 : 028100001000
    beq.w L_001FE8                                    ; +$0506 : 67000064
L_001F86:
    move.l d0,52(a5)                                  ; +$050A : 2B400034
    move.l d0,d1                                      ; +$050E : 2200
    andi.l #$00000400,d1                              ; +$0510 : 028100000400
    bne.w L_001FE8                                    ; +$0516 : 66000054
    move.l d0,d1                                      ; +$051A : 2200
    andi.l #$00000800,d1                              ; +$051C : 028100000800
    beq.w L_001FC8                                    ; +$0522 : 67000028
    andi.l #$00000080,d0                              ; +$0526 : 028000000080
    bne.w L_001FE8                                    ; +$052C : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$0530 : 0CAD000000060040
    beq.w L_001FC4                                    ; +$0538 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$053C : 0CAD000000080040
    bne.w L_001FE8                                    ; +$0544 : 66000026
L_001FC4:
    bra.w L_001FDE                                    ; +$0548 : 60000018
L_001FC8:
    andi.l #$00000080,d0                              ; +$054C : 028000000080
    beq.w L_001FDE                                    ; +$0552 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$0556 : 0CAD000000060040
    bne.w L_001FE8                                    ; +$055E : 6600000C
L_001FDE:
    move.l #$00000001,d0                              ; +$0562 : 203C00000001
    bra.w L_001FEE                                    ; +$0568 : 60000008
L_001FE8:
    move.l #$00000000,d0                              ; +$056C : 203C00000000
L_001FEE:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0572 : 4CDF5FFE
    tst.l d0                                          ; +$0576 : 4A80
    rts                                               ; +$0578 : 4E75
L_001FF6:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$057A : 48E77FFA
    tst.l 20(a5)                                      ; +$057E : 4AAD0014
    beq.w L_00200E                                    ; +$0582 : 6700000E
    movea.l 16(a5),a6                                 ; +$0586 : 2C6D0010
    move.l 20(a5),d1                                  ; +$058A : 222D0014
    jsr -36(a6)                                       ; +$058E : 4EAEFFDC
L_00200E:
    tst.l 96(a5)                                      ; +$0592 : 4AAD0060
    beq.w L_002022                                    ; +$0596 : 6700000E
    movea.l 96(a5),a1                                 ; +$059A : 226D0060
    movea.l $0004.w,a6                                ; +$059E : 2C780004
    jsr -690(a6)                                      ; +$05A2 : 4EAEFD4E
L_002022:
    tst.l 24(a5)                                      ; +$05A6 : 4AAD0018
    beq.w L_002036                                    ; +$05AA : 6700000E
    movea.l 24(a5),a1                                 ; +$05AE : 226D0018
    movea.l $0004.w,a6                                ; +$05B2 : 2C780004
    jsr -690(a6)                                      ; +$05B6 : 4EAEFD4E
L_002036:
    tst.l 12(a5)                                      ; +$05BA : 4AAD000C
    beq.w L_00204A                                    ; +$05BE : 6700000E
    movea.l 12(a5),a1                                 ; +$05C2 : 226D000C
    movea.l $0004.w,a6                                ; +$05C6 : 2C780004
    jsr -690(a6)                                      ; +$05CA : 4EAEFD4E
L_00204A:
    tst.l 16(a5)                                      ; +$05CE : 4AAD0010
    beq.w L_00205E                                    ; +$05D2 : 6700000E
    movea.l 16(a5),a1                                 ; +$05D6 : 226D0010
    movea.l $0004.w,a6                                ; +$05DA : 2C780004
    jsr -414(a6)                                      ; +$05DE : 4EAEFE62
L_00205E:
    move.l #$00000001,d0                              ; +$05E2 : 203C00000001
    bra.w L_00206E                                    ; +$05E8 : 60000008
    move.l #$00000000,d0                              ; +$05EC : 203C00000000
L_00206E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$05F2 : 4CDF5FFE
    tst.l d0                                          ; +$05F6 : 4A80
    rts                                               ; +$05F8 : 4E75
L_002076:
    dc.b "dos.library"
    dc.b $00

; -------- AP20 entry 15 : private/reserved --------
Entry_15:
Internal_15:
    cmpi.l #$00000100,d7                              ; +$0000 : 0C8700000100
    beq.w L_0020B6                                    ; +$0006 : 6700002C
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
L_0020B6:
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
    beq.w L_002296                                    ; +$000E : 670001CA
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002296                                    ; +$001A : 670001BE
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_002296                                    ; +$0026 : 670001B2
L_0020E6:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_003522                                    ; +$0030 : 61001434
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_002296                                    ; +$0036 : 670001A2
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
    bne.w L_0020E6                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_0020E6                                    ; +$0064 : 6600FFC4
    cmpi.l #$00000033,d5                              ; +$0068 : 0C8500000033
    bne.w L_002290                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_002290                                    ; +$007A : 67000158
    bra.w L_0022B8                                    ; +$007E : 6000017C
L_00213E:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_00229E                                    ; +$0088 : 60000158
L_002148:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_002194                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_00217A                                    ; +$00A0 : 6700001C
L_002160:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_00217A                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_002160                                    ; +$00BA : 6000FFE8
L_00217A:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_00218C                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    bsr.w L_006AAE                                    ; +$00CC : 61004924
L_00218C:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_002194:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_002214                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_0021B0                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_0021B0:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_0021DE                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_0021CE                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_0021CE:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_0021DE                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_0021DE:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_0021F2                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_0021F2:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_002202                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_002202:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_002214:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_00222C                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_00222C:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_002248                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_002248:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_002264                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_002264:
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
    bra.w L_00213E                                    ; +$01D0 : 6000FEB0
L_002290:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_002296                                    ; +$01D6 : 60000002
L_002296:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01DA : 4CDF5FF3
    moveq #0,d2                                       ; +$01DE : 7400
    rts                                               ; +$01E0 : 4E75
L_00229E:
    moveq #1,d1                                       ; +$01E2 : 7201
    movea.l -8(a5),a0                                 ; +$01E4 : 206DFFF8
    jsr 288(a0)                                       ; +$01E8 : 4EA80120
    move.l d5,d3                                      ; +$01EC : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$01FA : 4E75
L_0022B8:
    bsr.w L_0022CA                                    ; +$01FC : 61000010
    tst.l d0                                          ; +$0200 : 4A80
    beq.w L_0022C6                                    ; +$0202 : 67000006
    bra.w L_002148                                    ; +$0206 : 6000FE84
L_0022C6:
    bra.w L_002296                                    ; +$020A : 6000FFCE
L_0022CA:
    movea.l 32(a2),a4                                 ; +$020E : 286A0020
    move.l a4,d0                                      ; +$0212 : 200C
    tst.l d0                                          ; +$0214 : 4A80
    beq.w L_002302                                    ; +$0216 : 6700002E
    moveq #0,d4                                       ; +$021A : 7800
L_0022D8:
    bsr.w L_00230A                                    ; +$021C : 61000030
    tst.l d0                                          ; +$0220 : 4A80
    beq.w L_002302                                    ; +$0222 : 67000022
    addq.l #1,d4                                      ; +$0226 : 5284
    cmpi.l #$0000012D,d4                              ; +$0228 : 0C840000012D
    bge.w L_002306                                    ; +$022E : 6C00001A
    movea.l 8(a2),a6                                  ; +$0232 : 2C6A0008
    move.l a6,d0                                      ; +$0236 : 200E
    tst.l d0                                          ; +$0238 : 4A80
    beq.w L_002306                                    ; +$023A : 6700000E
    jsr -270(a6)                                      ; +$023E : 4EAEFEF2
    bra.w L_0022D8                                    ; +$0242 : 6000FFD8
L_002302:
    moveq #1,d0                                       ; +$0246 : 7001
    rts                                               ; +$0248 : 4E75
L_002306:
    moveq #0,d0                                       ; +$024A : 7000
    rts                                               ; +$024C : 4E75
L_00230A:
    move.l 20(a4),d6                                  ; +$024E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0252 : 028600000003
    btst #0,d6                                        ; +$0258 : 08060000
    beq.w L_00233A                                    ; +$025C : 67000020
    movea.l 12(a4),a0                                 ; +$0260 : 206C000C
    move.l a0,d0                                      ; +$0264 : 2008
    tst.l d0                                          ; +$0266 : 4A80
    beq.w L_00233A                                    ; +$0268 : 67000014
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -372(a6)                                      ; +$0270 : 4EAEFE8C
    tst.l d0                                          ; +$0274 : 4A80
    beq.w L_00233A                                    ; +$0276 : 67000006
    bclr #0,d6                                        ; +$027A : 08860000
L_00233A:
    btst #1,d6                                        ; +$027E : 08060001
    beq.w L_002360                                    ; +$0282 : 67000020
    movea.l 16(a4),a0                                 ; +$0286 : 206C0010
    move.l a0,d0                                      ; +$028A : 2008
    tst.l d0                                          ; +$028C : 4A80
    beq.w L_002360                                    ; +$028E : 67000014
    movea.l $0004.w,a6                                ; +$0292 : 2C780004
    jsr -372(a6)                                      ; +$0296 : 4EAEFE8C
    tst.l d0                                          ; +$029A : 4A80
    beq.w L_002360                                    ; +$029C : 67000006
    bclr #1,d6                                        ; +$02A0 : 08860001
L_002360:
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
    beq.w L_002556                                    ; +$000E : 670001DE
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002556                                    ; +$001A : 670001D2
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_002556                                    ; +$0026 : 670001C6
L_002392:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_003522                                    ; +$0030 : 61001188
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_002542                                    ; +$0036 : 670001A2
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
    bne.w L_002392                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_002392                                    ; +$0064 : 6600FFC4
    bra.w L_00255E                                    ; +$0068 : 6000018C
    nop                                               ; +$006C : 4E71
L_0023D6:
    bne.w L_00253C                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_00253C                                    ; +$007A : 67000158
    bra.w L_00258C                                    ; +$007E : 600001A4
L_0023EA:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_002572                                    ; +$0088 : 60000180
L_0023F4:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_002440                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_002426                                    ; +$00A0 : 6700001C
L_00240C:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_002426                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_00240C                                    ; +$00BA : 6000FFE8
L_002426:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_002438                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    bsr.w L_006AAE                                    ; +$00CC : 61004678
L_002438:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_002440:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_0024C0                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_00245C                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_00245C:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_00248A                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_00247A                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_00247A:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_00248A                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_00248A:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_00249E                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_00249E:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_0024AE                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_0024AE:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_0024C0:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_0024D8                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_0024D8:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_0024F4                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_0024F4:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_002510                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_002510:
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
    bra.w L_0023EA                                    ; +$01D0 : 6000FEB0
L_00253C:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_002556                                    ; +$01D6 : 60000016
L_002542:
    movea.l 8(a2),a6                                  ; +$01DA : 2C6A0008
    move.l a6,d0                                      ; +$01DE : 200E
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_002556                                    ; +$01E2 : 6700000A
    jsr -270(a6)                                      ; +$01E6 : 4EAEFEF2
    bra.w L_002392                                    ; +$01EA : 6000FE3E
L_002556:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    rts                                               ; +$01F4 : 4E75
L_00255E:
    cmpi.l #$00000063,d5                              ; +$01F6 : 0C8500000063
    beq.w L_002392                                    ; +$01FC : 6700FE2C
    cmpi.l #$00000033,d5                              ; +$0200 : 0C8500000033
    bra.w L_0023D6                                    ; +$0206 : 6000FE66
L_002572:
    moveq #1,d1                                       ; +$020A : 7201
    movea.l -8(a5),a0                                 ; +$020C : 206DFFF8
    jsr 288(a0)                                       ; +$0210 : 4EA80120
    move.l d5,d3                                      ; +$0214 : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$0216 : 4CDF5FF3
    moveq #0,d2                                       ; +$021A : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$0222 : 4E75
L_00258C:
    bsr.w L_00259E                                    ; +$0224 : 61000010
    tst.l d0                                          ; +$0228 : 4A80
    beq.w L_00259A                                    ; +$022A : 67000006
    bra.w L_0023F4                                    ; +$022E : 6000FE5C
L_00259A:
    bra.w L_002556                                    ; +$0232 : 6000FFBA
L_00259E:
    movea.l 32(a2),a4                                 ; +$0236 : 286A0020
    move.l a4,d0                                      ; +$023A : 200C
    tst.l d0                                          ; +$023C : 4A80
    beq.w L_0025D6                                    ; +$023E : 6700002E
    moveq #0,d4                                       ; +$0242 : 7800
L_0025AC:
    bsr.w L_0025DE                                    ; +$0244 : 61000030
    tst.l d0                                          ; +$0248 : 4A80
    beq.w L_0025D6                                    ; +$024A : 67000022
    addq.l #1,d4                                      ; +$024E : 5284
    cmpi.l #$0000012D,d4                              ; +$0250 : 0C840000012D
    bge.w L_0025DA                                    ; +$0256 : 6C00001A
    movea.l 8(a2),a6                                  ; +$025A : 2C6A0008
    move.l a6,d0                                      ; +$025E : 200E
    tst.l d0                                          ; +$0260 : 4A80
    beq.w L_0025DA                                    ; +$0262 : 6700000E
    jsr -270(a6)                                      ; +$0266 : 4EAEFEF2
    bra.w L_0025AC                                    ; +$026A : 6000FFD8
L_0025D6:
    moveq #1,d0                                       ; +$026E : 7001
    rts                                               ; +$0270 : 4E75
L_0025DA:
    moveq #0,d0                                       ; +$0272 : 7000
    rts                                               ; +$0274 : 4E75
L_0025DE:
    move.l 20(a4),d6                                  ; +$0276 : 2C2C0014
    andi.l #$00000003,d6                              ; +$027A : 028600000003
    btst #0,d6                                        ; +$0280 : 08060000
    beq.w L_00260E                                    ; +$0284 : 67000020
    movea.l 12(a4),a0                                 ; +$0288 : 206C000C
    move.l a0,d0                                      ; +$028C : 2008
    tst.l d0                                          ; +$028E : 4A80
    beq.w L_00260E                                    ; +$0290 : 67000014
    movea.l $0004.w,a6                                ; +$0294 : 2C780004
    jsr -372(a6)                                      ; +$0298 : 4EAEFE8C
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_00260E                                    ; +$029E : 67000006
    bclr #0,d6                                        ; +$02A2 : 08860000
L_00260E:
    btst #1,d6                                        ; +$02A6 : 08060001
    beq.w L_002634                                    ; +$02AA : 67000020
    movea.l 16(a4),a0                                 ; +$02AE : 206C0010
    move.l a0,d0                                      ; +$02B2 : 2008
    tst.l d0                                          ; +$02B4 : 4A80
    beq.w L_002634                                    ; +$02B6 : 67000014
    movea.l $0004.w,a6                                ; +$02BA : 2C780004
    jsr -372(a6)                                      ; +$02BE : 4EAEFE8C
    tst.l d0                                          ; +$02C2 : 4A80
    beq.w L_002634                                    ; +$02C4 : 67000006
    bclr #1,d6                                        ; +$02C8 : 08860001
L_002634:
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
    beq.w L_0027F2                                    ; +$0018 : 67000198
    move.l (a4),d6                                    ; +$001C : 2C14
    tst.l d6                                          ; +$001E : 4A86
    beq.w L_0027F2                                    ; +$0020 : 67000190
    movea.l 32(a4),a2                                 ; +$0024 : 246C0020
    move.l a2,d6                                      ; +$0028 : 2C0A
    tst.l d6                                          ; +$002A : 4A86
    beq.w L_0027F2                                    ; +$002C : 67000184
    movea.l 8(a4),a6                                  ; +$0030 : 2C6C0008
    move.l a6,d6                                      ; +$0034 : 2C0E
    tst.l d6                                          ; +$0036 : 4A86
    beq.w L_0027F2                                    ; +$0038 : 67000178
    tst.l d0                                          ; +$003C : 4A80
    bmi.w L_0027F2                                    ; +$003E : 6B000172
    tst.l d1                                          ; +$0042 : 4A81
    bmi.w L_0027F2                                    ; +$0044 : 6B00016C
    tst.l d2                                          ; +$0048 : 4A82
    bmi.w L_0027F2                                    ; +$004A : 6B000166
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_0027F2                                    ; +$0050 : 6B000160
    tst.l d4                                          ; +$0054 : 4A84
    ble.w L_0027F2                                    ; +$0056 : 6F00015A
    tst.l d5                                          ; +$005A : 4A85
    ble.w L_0027F2                                    ; +$005C : 6F000154
    move.l 12(a4),d6                                  ; +$0060 : 2C2C000C
    tst.l d6                                          ; +$0064 : 4A86
    ble.w L_0027F2                                    ; +$0066 : 6F00014A
    cmpi.l #$00007FFF,d6                              ; +$006A : 0C8600007FFF
    bgt.w L_0027F2                                    ; +$0070 : 6E000140
    move.l 16(a4),d6                                  ; +$0074 : 2C2C0010
    tst.l d6                                          ; +$0078 : 4A86
    ble.w L_0027F2                                    ; +$007A : 6F000136
    cmpi.l #$00007FFF,d6                              ; +$007E : 0C8600007FFF
    bgt.w L_0027F2                                    ; +$0084 : 6E00012C
    move.l 12(a4),d6                                  ; +$0088 : 2C2C000C
    sub.l d4,d6                                       ; +$008C : 9C84
    tst.l d6                                          ; +$008E : 4A86
    bmi.w L_0027F2                                    ; +$0090 : 6B000120
    cmp.l d6,d0                                       ; +$0094 : B086
    bgt.w L_0027F2                                    ; +$0096 : 6E00011A
    cmp.l d6,d2                                       ; +$009A : B486
    bgt.w L_0027F2                                    ; +$009C : 6E000114
    move.l 16(a4),d6                                  ; +$00A0 : 2C2C0010
    sub.l d5,d6                                       ; +$00A4 : 9C85
    tst.l d6                                          ; +$00A6 : 4A86
    bmi.w L_0027F2                                    ; +$00A8 : 6B000108
    cmp.l d6,d1                                       ; +$00AC : B286
    bgt.w L_0027F2                                    ; +$00AE : 6E000102
    cmp.l d6,d3                                       ; +$00B2 : B686
    bgt.w L_0027F2                                    ; +$00B4 : 6E0000FC
    tst.l 8(a2)                                       ; +$00B8 : 4AAA0008
    beq.w L_002706                                    ; +$00BC : 67000008
    movea.l (a2),a0                                   ; +$00C0 : 2052
    bra.w L_00270A                                    ; +$00C2 : 60000006
L_002706:
    movea.l 4(a2),a0                                  ; +$00C6 : 206A0004
L_00270A:
    move.l a0,d6                                      ; +$00CA : 2C08
    tst.l d6                                          ; +$00CC : 4A86
    beq.w L_0027F2                                    ; +$00CE : 670000E2
    movea.l (a0),a0                                   ; +$00D2 : 2050
    move.l a0,d6                                      ; +$00D4 : 2C08
    tst.l d6                                          ; +$00D6 : 4A86
    beq.w L_0027F2                                    ; +$00D8 : 670000D8
    move.l #$00000000,d6                              ; +$00DC : 2C3C00000000
    move.w (a0),d6                                    ; +$00E2 : 3C10
    lsl.l #3,d6                                       ; +$00E4 : E78E
    cmp.l 12(a4),d6                                   ; +$00E6 : BCAC000C
    blt.w L_0027F2                                    ; +$00EA : 6D0000C6
    move.l #$00000000,d6                              ; +$00EE : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00F4 : 3C280002
    cmp.l 16(a4),d6                                   ; +$00F8 : BCAC0010
    blt.w L_0027F2                                    ; +$00FC : 6D0000B4
    move.l #$00000000,d6                              ; +$0100 : 2C3C00000000
    move.b 5(a0),d6                                   ; +$0106 : 1C280005
    cmp.l 28(a4),d6                                   ; +$010A : BCAC001C
    bne.w L_0027F2                                    ; +$010E : 660000A2
    tst.l d6                                          ; +$0112 : 4A86
    ble.w L_0027F2                                    ; +$0114 : 6F00009C
    cmpi.l #$00000008,d6                              ; +$0118 : 0C8600000008
    bgt.w L_0027F2                                    ; +$011E : 6E000092
    move.l d6,-(a7)                                   ; +$0122 : 2F06
    move.l 20(a2),d6                                  ; +$0124 : 2C2A0014
    andi.l #$00000001,d6                              ; +$0128 : 028600000001
    beq.w L_0027C4                                    ; +$012E : 67000054
    move.l d0,-(a7)                                   ; +$0132 : 2F00
    move.l d1,-(a7)                                   ; +$0134 : 2F01
    move.l a0,-(a7)                                   ; +$0136 : 2F08
    move.l a1,-(a7)                                   ; +$0138 : 2F09
    movea.l 12(a2),a0                                 ; +$013A : 206A000C
    move.l a0,d6                                      ; +$013E : 2C08
    tst.l d6                                          ; +$0140 : 4A86
    beq.w L_0027B2                                    ; +$0142 : 6700002E
    movea.l $0004.w,a6                                ; +$0146 : 2C780004
    jsr -372(a6)                                      ; +$014A : 4EAEFE8C
    tst.l d0                                          ; +$014E : 4A80
    beq.w L_0027B2                                    ; +$0150 : 67000020
    move.l 20(a2),d6                                  ; +$0154 : 2C2A0014
    andi.l #$FFFFFFFE,d6                              ; +$0158 : 0286FFFFFFFE
    move.l d6,20(a2)                                  ; +$015E : 25460014
    movea.l 8(a4),a6                                  ; +$0162 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$0166 : 225F
    movea.l (a7)+,a0                                  ; +$0168 : 205F
    move.l (a7)+,d1                                   ; +$016A : 221F
    move.l (a7)+,d0                                   ; +$016C : 201F
    bra.w L_0027C4                                    ; +$016E : 60000014
L_0027B2:
    movea.l 8(a4),a6                                  ; +$0172 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$0176 : 225F
    movea.l (a7)+,a0                                  ; +$0178 : 205F
    move.l (a7)+,d1                                   ; +$017A : 221F
    move.l (a7)+,d0                                   ; +$017C : 201F
    move.l (a7)+,d6                                   ; +$017E : 2C1F
    bra.w L_0027F2                                    ; +$0180 : 60000030
L_0027C4:
    move.l (a7)+,d6                                   ; +$0184 : 2C1F
    movea.l a0,a1                                     ; +$0186 : 2248
    movea.l #$00000000,a2                             ; +$0188 : 247C00000000
    move.l #$000000C0,d6                              ; +$018E : 2C3C000000C0
    move.l #$000000FF,d7                              ; +$0194 : 2E3C000000FF
    jsr -30(a6)                                       ; +$019A : 4EAEFFE2
    tst.l d0                                          ; +$019E : 4A80
    beq.w L_0027F2                                    ; +$01A0 : 67000010
    jsr -228(a6)                                      ; +$01A4 : 4EAEFF1C
    move.l #$00000001,d3                              ; +$01A8 : 263C00000001
    bra.w L_0027F8                                    ; +$01AE : 60000008
L_0027F2:
    move.l #$00000000,d3                              ; +$01B2 : 263C00000000
L_0027F8:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01B8 : 4CDF77F7
    moveq #0,d2                                       ; +$01BC : 7400
    rts                                               ; +$01BE : 4E75
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
    beq.w L_002A16                                    ; +$0014 : 670001FC
    move.l (a4),d6                                    ; +$0018 : 2C14
    tst.l d6                                          ; +$001A : 4A86
    beq.w L_002A16                                    ; +$001C : 670001F4
    movea.l 32(a4),a2                                 ; +$0020 : 246C0020
    move.l a2,d6                                      ; +$0024 : 2C0A
    tst.l d6                                          ; +$0026 : 4A86
    beq.w L_002A16                                    ; +$0028 : 670001E8
    movea.l 8(a4),a6                                  ; +$002C : 2C6C0008
    move.l a6,d6                                      ; +$0030 : 2C0E
    tst.l d6                                          ; +$0032 : 4A86
    beq.w L_002A16                                    ; +$0034 : 670001DC
    tst.l d0                                          ; +$0038 : 4A80
    bmi.w L_002A16                                    ; +$003A : 6B0001D6
    tst.l d1                                          ; +$003E : 4A81
    bmi.w L_002A16                                    ; +$0040 : 6B0001D0
    tst.l d3                                          ; +$0044 : 4A83
    bmi.w L_002A16                                    ; +$0046 : 6B0001CA
    tst.l d4                                          ; +$004A : 4A84
    ble.w L_002A16                                    ; +$004C : 6F0001C4
    tst.l d5                                          ; +$0050 : 4A85
    ble.w L_002A16                                    ; +$0052 : 6F0001BE
    move.l 12(a4),d6                                  ; +$0056 : 2C2C000C
    tst.l d6                                          ; +$005A : 4A86
    ble.w L_002A16                                    ; +$005C : 6F0001B4
    cmpi.l #$00007FFF,d6                              ; +$0060 : 0C8600007FFF
    bgt.w L_002A16                                    ; +$0066 : 6E0001AA
    move.l 16(a4),d6                                  ; +$006A : 2C2C0010
    tst.l d6                                          ; +$006E : 4A86
    ble.w L_002A16                                    ; +$0070 : 6F0001A0
    cmpi.l #$00007FFF,d6                              ; +$0074 : 0C8600007FFF
    bgt.w L_002A16                                    ; +$007A : 6E000196
    move.l 12(a4),d6                                  ; +$007E : 2C2C000C
    sub.l d4,d6                                       ; +$0082 : 9C84
    tst.l d6                                          ; +$0084 : 4A86
    bmi.w L_002A16                                    ; +$0086 : 6B00018A
    cmp.l d6,d0                                       ; +$008A : B086
    bgt.w L_002A16                                    ; +$008C : 6E000184
    move.l 16(a4),d6                                  ; +$0090 : 2C2C0010
    sub.l d5,d6                                       ; +$0094 : 9C85
    tst.l d6                                          ; +$0096 : 4A86
    bmi.w L_002A16                                    ; +$0098 : 6B000178
    cmp.l d6,d1                                       ; +$009C : B286
    bgt.w L_002A16                                    ; +$009E : 6E000172
    tst.l 8(a2)                                       ; +$00A2 : 4AAA0008
    beq.w L_0028B4                                    ; +$00A6 : 67000008
    movea.l (a2),a0                                   ; +$00AA : 2052
    bra.w L_0028B8                                    ; +$00AC : 60000006
L_0028B4:
    movea.l 4(a2),a0                                  ; +$00B0 : 206A0004
L_0028B8:
    move.l a0,d6                                      ; +$00B4 : 2C08
    tst.l d6                                          ; +$00B6 : 4A86
    beq.w L_002A16                                    ; +$00B8 : 67000158
    movea.l (a0),a0                                   ; +$00BC : 2050
    move.l a0,d6                                      ; +$00BE : 2C08
    tst.l d6                                          ; +$00C0 : 4A86
    beq.w L_002A16                                    ; +$00C2 : 6700014E
    move.l #$00000000,d6                              ; +$00C6 : 2C3C00000000
    move.w (a0),d6                                    ; +$00CC : 3C10
    lsl.l #3,d6                                       ; +$00CE : E78E
    cmp.l 12(a4),d6                                   ; +$00D0 : BCAC000C
    blt.w L_002A16                                    ; +$00D4 : 6D00013C
    move.l #$00000000,d6                              ; +$00D8 : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00DE : 3C280002
    cmp.l 16(a4),d6                                   ; +$00E2 : BCAC0010
    blt.w L_002A16                                    ; +$00E6 : 6D00012A
    move.l #$00000000,d6                              ; +$00EA : 2C3C00000000
    move.b 5(a0),d6                                   ; +$00F0 : 1C280005
    cmp.l 28(a4),d6                                   ; +$00F4 : BCAC001C
    bne.w L_002A16                                    ; +$00F8 : 66000118
    tst.l d6                                          ; +$00FC : 4A86
    ble.w L_002A16                                    ; +$00FE : 6F000112
    cmpi.l #$00000008,d6                              ; +$0102 : 0C8600000008
    bgt.w L_002A16                                    ; +$0108 : 6E000108
    move.l d6,d2                                      ; +$010C : 2406
    movea.l a0,a1                                     ; +$010E : 2248
    addq.l #8,a1                                      ; +$0110 : 5089
L_002916:
    move.l (a1)+,d6                                   ; +$0112 : 2C19
    tst.l d6                                          ; +$0114 : 4A86
    beq.w L_002A16                                    ; +$0116 : 670000FA
    cmpi.l #$FFFFFFFF,d6                              ; +$011A : 0C86FFFFFFFF
    beq.w L_002A16                                    ; +$0120 : 670000F0
    subq.l #1,d2                                      ; +$0124 : 5382
    bne.w L_002916                                    ; +$0126 : 6600FFEA
    move.l #$00000000,d2                              ; +$012A : 243C00000000
    move.b 5(a0),d2                                   ; +$0130 : 14280005
    move.l #$00000001,d6                              ; +$0134 : 2C3C00000001
L_00293E:
    lsl.l #1,d6                                       ; +$013A : E38E
    subq.l #1,d2                                      ; +$013C : 5382
    bne.w L_00293E                                    ; +$013E : 6600FFFA
    cmp.l d6,d3                                       ; +$0142 : B686
    bcc.w L_002A16                                    ; +$0144 : 640000CC
    move.l d6,-(a7)                                   ; +$0148 : 2F06
    move.l 20(a2),d6                                  ; +$014A : 2C2A0014
    andi.l #$00000001,d6                              ; +$014E : 028600000001
    beq.w L_0029AE                                    ; +$0154 : 67000054
    move.l d0,-(a7)                                   ; +$0158 : 2F00
    move.l d1,-(a7)                                   ; +$015A : 2F01
    move.l a0,-(a7)                                   ; +$015C : 2F08
    move.l a1,-(a7)                                   ; +$015E : 2F09
    movea.l 12(a2),a0                                 ; +$0160 : 206A000C
    move.l a0,d6                                      ; +$0164 : 2C08
    tst.l d6                                          ; +$0166 : 4A86
    beq.w L_00299C                                    ; +$0168 : 6700002E
    movea.l $0004.w,a6                                ; +$016C : 2C780004
    jsr -372(a6)                                      ; +$0170 : 4EAEFE8C
    tst.l d0                                          ; +$0174 : 4A80
    beq.w L_00299C                                    ; +$0176 : 67000020
    move.l 20(a2),d6                                  ; +$017A : 2C2A0014
    andi.l #$FFFFFFFE,d6                              ; +$017E : 0286FFFFFFFE
    move.l d6,20(a2)                                  ; +$0184 : 25460014
    movea.l 8(a4),a6                                  ; +$0188 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$018C : 225F
    movea.l (a7)+,a0                                  ; +$018E : 205F
    move.l (a7)+,d1                                   ; +$0190 : 221F
    move.l (a7)+,d0                                   ; +$0192 : 201F
    bra.w L_0029AE                                    ; +$0194 : 60000014
L_00299C:
    movea.l 8(a4),a6                                  ; +$0198 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$019C : 225F
    movea.l (a7)+,a0                                  ; +$019E : 205F
    move.l (a7)+,d1                                   ; +$01A0 : 221F
    move.l (a7)+,d0                                   ; +$01A2 : 201F
    move.l (a7)+,d6                                   ; +$01A4 : 2C1F
    bra.w L_002A16                                    ; +$01A6 : 6000006A
L_0029AE:
    move.l (a7)+,d6                                   ; +$01AA : 2C1F
    move.l d3,-(a7)                                   ; +$01AC : 2F03
    move.l d6,-(a7)                                   ; +$01AE : 2F06
    movea.l a0,a4                                     ; +$01B0 : 2848
    move.l d0,d2                                      ; +$01B2 : 2400
    move.l d1,d3                                      ; +$01B4 : 2601
    move.l #$00000001,d7                              ; +$01B6 : 2E3C00000001
L_0029C0:
    move.l 4(a7),d6                                   ; +$01BC : 2C2F0004
    and.l d7,d6                                       ; +$01C0 : CC87
    tst.l d6                                          ; +$01C2 : 4A86
    beq.w L_0029D6                                    ; +$01C4 : 6700000C
    move.l #$000000F0,d6                              ; +$01C8 : 2C3C000000F0
    bra.w L_0029DC                                    ; +$01CE : 60000008
L_0029D6:
    move.l #$00000000,d6                              ; +$01D2 : 2C3C00000000
L_0029DC:
    move.l d2,d0                                      ; +$01D8 : 2002
    move.l d3,d1                                      ; +$01DA : 2203
    movea.l a4,a0                                     ; +$01DC : 204C
    movea.l a4,a1                                     ; +$01DE : 224C
    movea.l #$00000000,a2                             ; +$01E0 : 247C00000000
    jsr -30(a6)                                       ; +$01E6 : 4EAEFFE2
    tst.l d0                                          ; +$01EA : 4A80
    beq.w L_002A0A                                    ; +$01EC : 67000018
    jsr -228(a6)                                      ; +$01F0 : 4EAEFF1C
    lsl.l #1,d7                                       ; +$01F4 : E38F
    cmp.l (a7),d7                                     ; +$01F6 : BE97
    bne.w L_0029C0                                    ; +$01F8 : 6600FFC2
    move.l #$00000001,d3                              ; +$01FC : 263C00000001
    bra.w L_002A10                                    ; +$0202 : 60000008
L_002A0A:
    move.l #$00000000,d3                              ; +$0206 : 263C00000000
L_002A10:
    addq.l #8,a7                                      ; +$020C : 508F
    bra.w L_002A1C                                    ; +$020E : 60000008
L_002A16:
    move.l #$00000000,d3                              ; +$0212 : 263C00000000
L_002A1C:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0218 : 4CDF77F7
    moveq #0,d2                                       ; +$021C : 7400
    rts                                               ; +$021E : 4E75
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
    bsr.w Aga_Blit_Fill                               ; +$0016 : 6100FDC4
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
    beq.w L_002B22                                    ; +$000C : 670000C6
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002B22                                    ; +$0016 : 670000BC
    move.l 342(a4),d0                                 ; +$001A : 202C0156
    tst.l d0                                          ; +$001E : 4A80
    bne.w L_002AE6                                    ; +$0020 : 66000076
    move.l 64(a4),d0                                  ; +$0024 : 202C0040
    tst.l d0                                          ; +$0028 : 4A80
    bne.w L_002B22                                    ; +$002A : 660000A8
    movea.l 456(a5),a0                                ; +$002E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0032 : 2C680008
    move.l a6,d0                                      ; +$0036 : 200E
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_002B22                                    ; +$003A : 67000098
    movea.l $0004.w,a6                                ; +$003E : 2C780004
    move.l #$0000000C,d0                              ; +$0042 : 203C0000000C
    move.l #$00010001,d1                              ; +$0048 : 223C00010001
    jsr -198(a6)                                      ; +$004E : 4EAEFF3A
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_002B22                                    ; +$0054 : 6700007E
    movea.l d0,a2                                     ; +$0058 : 2440
    movea.l 456(a5),a0                                ; +$005A : 206D01C8
    movea.l 8(a0),a6                                  ; +$005E : 2C680008
    movea.l a2,a0                                     ; +$0062 : 204A
    move.l #$00000040,d0                              ; +$0064 : 203C00000040
    jsr -594(a6)                                      ; +$006A : 4EAEFDAE
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_002AF4                                    ; +$0070 : 67000034
    movea.l a2,a1                                     ; +$0074 : 224A
    move.l #$00002710,d0                              ; +$0076 : 203C00002710
    move.l #$000000FF,d1                              ; +$007C : 223C000000FF
    jsr -378(a6)                                      ; +$0082 : 4EAEFE86
    movea.l a2,a1                                     ; +$0086 : 224A
    jsr -366(a6)                                      ; +$0088 : 4EAEFE92
    move.l a2,342(a4)                                 ; +$008C : 294A0156
    move.l a2,64(a4)                                  ; +$0090 : 294A0040
    bra.w L_002B18                                    ; +$0094 : 60000034
L_002AE6:
    move.l 64(a4),d1                                  ; +$0098 : 222C0040
    cmp.l d1,d0                                       ; +$009C : B081
    beq.w L_002B18                                    ; +$009E : 6700002A
    bra.w L_002B22                                    ; +$00A2 : 60000030
L_002AF4:
    movea.l 4(a2),a0                                  ; +$00A6 : 206A0004
    move.l a0,d0                                      ; +$00AA : 2008
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_002B04                                    ; +$00AE : 67000006
    jsr -546(a6)                                      ; +$00B2 : 4EAEFDDE
L_002B04:
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    movea.l a2,a1                                     ; +$00BA : 224A
    move.l #$0000000C,d0                              ; +$00BC : 203C0000000C
    jsr -210(a6)                                      ; +$00C2 : 4EAEFF2E
    bra.w L_002B22                                    ; +$00C6 : 6000000C
L_002B18:
    move.l #$00000001,d3                              ; +$00CA : 263C00000001
    bra.w L_002B28                                    ; +$00D0 : 60000008
L_002B22:
    move.l #$00000000,d3                              ; +$00D4 : 263C00000000
L_002B28:
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
    beq.w L_002BCE                                    ; +$000C : 6700008C
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002BCE                                    ; +$0016 : 67000082
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_002BCE                                    ; +$002A : 6700006E
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_002BCE                                    ; +$0034 : 66000064
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_002BCE                                    ; +$0044 : 67000054
    movea.l 8(a2),a1                                  ; +$0048 : 226A0008
    move.l a1,d0                                      ; +$004C : 2009
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_002BCE                                    ; +$0050 : 67000048
    move.w 28(a1),d0                                  ; +$0054 : 3029001C
    cmpi.w #$0001,d0                                  ; +$0058 : 0C400001
    beq.w L_002BA2                                    ; +$005C : 67000010
    move.l d6,d0                                      ; +$0060 : 2006
    andi.l #$00000002,d0                              ; +$0062 : 028000000002
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_002BCE                                    ; +$006A : 6700002E
L_002BA2:
    ori.l #$00000001,342(a4)                          ; +$006E : 00AC000000010156
    movea.l a4,a0                                     ; +$0076 : 204C
    jsr -378(a6)                                      ; +$0078 : 4EAEFE86
    tst.l d0                                          ; +$007C : 4A80
    bne.w L_002BCE                                    ; +$007E : 6600001A
    jsr -390(a6)                                      ; +$0082 : 4EAEFE7A
    tst.l d0                                          ; +$0086 : 4A80
    bne.w L_002BCE                                    ; +$0088 : 66000010
    bra.w L_002BC4                                    ; +$008C : 60000002
L_002BC4:
    move.l #$00000001,d3                              ; +$0090 : 263C00000001
    bra.w L_002BD4                                    ; +$0096 : 60000008
L_002BCE:
    move.l #$00000000,d3                              ; +$009A : 263C00000000
L_002BD4:
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
    beq.w L_002CBE                                    ; +$000C : 670000D0
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002CBE                                    ; +$0016 : 670000C6
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_002C8C                                    ; +$002A : 67000080
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_002CBE                                    ; +$0034 : 660000A8
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_002CBE                                    ; +$0044 : 67000098
    movea.l 456(a5),a0                                ; +$0048 : 206D01C8
    move.l 8(a0),d0                                   ; +$004C : 20280008
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_002CBE                                    ; +$0052 : 6700008A
    move.l #$00000000,64(a4)                          ; +$0056 : 297C000000000040
    movea.l a4,a0                                     ; +$005E : 204C
    jsr -378(a6)                                      ; +$0060 : 4EAEFE86
    tst.l d0                                          ; +$0064 : 4A80
    bne.w L_002C9A                                    ; +$0066 : 66000052
    jsr -390(a6)                                      ; +$006A : 4EAEFE7A
    tst.l d0                                          ; +$006E : 4A80
    bne.w L_002CA2                                    ; +$0070 : 66000050
    movea.l 456(a5),a0                                ; +$0074 : 206D01C8
    movea.l 8(a0),a6                                  ; +$0078 : 2C680008
    jsr -270(a6)                                      ; +$007C : 4EAEFEF2
    movea.l 4(a2),a0                                  ; +$0080 : 206A0004
    move.l a0,d0                                      ; +$0084 : 2008
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_002C70                                    ; +$0088 : 67000006
    jsr -546(a6)                                      ; +$008C : 4EAEFDDE
L_002C70:
    move.l #$00000000,342(a4)                         ; +$0090 : 297C000000000156
    movea.l $0004.w,a6                                ; +$0098 : 2C780004
    movea.l a2,a1                                     ; +$009C : 224A
    move.l #$0000000C,d0                              ; +$009E : 203C0000000C
    jsr -210(a6)                                      ; +$00A4 : 4EAEFF2E
    bra.w L_002CB4                                    ; +$00A8 : 6000002A
L_002C8C:
    move.l 64(a4),d0                                  ; +$00AC : 202C0040
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_002CB4                                    ; +$00B2 : 67000020
    bra.w L_002CBE                                    ; +$00B6 : 60000026
L_002C9A:
    move.l a2,64(a4)                                  ; +$00BA : 294A0040
    bra.w L_002CBE                                    ; +$00BE : 6000001E
L_002CA2:
    move.l a2,64(a4)                                  ; +$00C2 : 294A0040
    movea.l a4,a0                                     ; +$00C6 : 204C
    jsr -378(a6)                                      ; +$00C8 : 4EAEFE86
    jsr -390(a6)                                      ; +$00CC : 4EAEFE7A
    bra.w L_002CBE                                    ; +$00D0 : 6000000C
L_002CB4:
    move.l #$00000001,d3                              ; +$00D4 : 263C00000001
    bra.w L_002CC4                                    ; +$00DA : 60000008
L_002CBE:
    move.l #$00000000,d3                              ; +$00DE : 263C00000000
L_002CC4:
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
    beq.w L_002E2C                                    ; +$0010 : 6700014A
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002E2C                                    ; +$001A : 67000140
    cmpi.l #$000000FF,d4                              ; +$001E : 0C84000000FF
    bhi.w L_002E2C                                    ; +$0024 : 62000136
    cmpi.l #$000000DE,d5                              ; +$0028 : 0C85000000DE
    bhi.w L_002E2C                                    ; +$002E : 6200012C
    move.l 342(a4),d6                                 ; +$0032 : 2C2C0156
    move.l d6,d0                                      ; +$0036 : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0038 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$003E : 2440
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_002E2C                                    ; +$0042 : 67000118
    move.l 64(a4),d1                                  ; +$0046 : 222C0040
    cmp.l d1,d0                                       ; +$004A : B081
    bne.w L_002E2C                                    ; +$004C : 6600010E
    move.l d6,d0                                      ; +$0050 : 2006
    andi.l #$00000003,d0                              ; +$0052 : 028000000003
    tst.l d0                                          ; +$0058 : 4A80
    bne.w L_002E2C                                    ; +$005A : 66000100
    movea.l 456(a5),a0                                ; +$005E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0062 : 2C680008
    move.l a6,d0                                      ; +$0066 : 200E
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_002E2C                                    ; +$006A : 670000F0
    movea.l 8(a2),a1                                  ; +$006E : 226A0008
    move.l a1,d0                                      ; +$0072 : 2009
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_002E2C                                    ; +$0076 : 670000E4
    move.l 12(a1),d0                                  ; +$007A : 2029000C
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_002E2C                                    ; +$0080 : 670000DA
    movea.l 16(a1),a0                                 ; +$0084 : 20690010
    move.l a0,d0                                      ; +$0088 : 2008
    tst.l d0                                          ; +$008A : 4A80
    beq.w L_002E2C                                    ; +$008C : 670000CE
    move.w 30(a1),d0                                  ; +$0090 : 3029001E
    cmpi.w #$0040,d0                                  ; +$0094 : 0C400040
    bne.w L_002E2C                                    ; +$0098 : 660000C2
    move.w 28(a1),d7                                  ; +$009C : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00A0 : 0C470000
    bls.w L_002E2C                                    ; +$00A4 : 630000B6
    cmpi.w #$003F,d7                                  ; +$00A8 : 0C47003F
    bcc.w L_002E2C                                    ; +$00AC : 640000AE
    movea.l 16(a1),a0                                 ; +$00B0 : 20690010
    subq.l #6,a0                                      ; +$00B4 : 5D88
    move.w (a0),d0                                    ; +$00B6 : 3010
    cmpi.w #$0001,d0                                  ; +$00B8 : 0C400001
    bne.w L_002E2C                                    ; +$00BC : 6600009E
    move.w 2(a0),d0                                   ; +$00C0 : 30280002
    cmpi.w #$2710,d0                                  ; +$00C4 : 0C402710
    bne.w L_002E2C                                    ; +$00C8 : 66000092
    move.w 4(a0),d0                                   ; +$00CC : 30280004
    cmpi.w #$00FF,d0                                  ; +$00D0 : 0C4000FF
    bne.w L_002E2C                                    ; +$00D4 : 66000086
    move.w d7,d6                                      ; +$00D8 : 3C07
    subq.w #1,d6                                      ; +$00DA : 5346
    beq.w L_002DE8                                    ; +$00DC : 6700003A
    movea.l 16(a1),a0                                 ; +$00E0 : 20690010
    subq.l #6,a0                                      ; +$00E4 : 5D88
L_002DB6:
    subq.l #6,a0                                      ; +$00E6 : 5D88
    move.w (a0),d0                                    ; +$00E8 : 3010
    cmpi.w #$0001,d0                                  ; +$00EA : 0C400001
    beq.w L_002DCC                                    ; +$00EE : 6700000C
    subq.w #1,d6                                      ; +$00F2 : 5346
    bne.w L_002DB6                                    ; +$00F4 : 6600FFF0
    bra.w L_002DE8                                    ; +$00F8 : 6000001E
L_002DCC:
    move.w 2(a0),d0                                   ; +$00FC : 30280002
    move.w d4,d1                                      ; +$0100 : 3204
    cmp.w d0,d1                                       ; +$0102 : B240
    bhi.w L_002DE8                                    ; +$0104 : 62000012
    bne.w L_002E2C                                    ; +$0108 : 66000052
    move.w 4(a0),d0                                   ; +$010C : 30280004
    move.w d5,d1                                      ; +$0110 : 3205
    cmp.w d0,d1                                       ; +$0112 : B240
    bls.w L_002E2C                                    ; +$0114 : 63000046
L_002DE8:
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
    bra.w L_002E22                                    ; +$014E : 60000002
L_002E22:
    move.l #$00000001,d3                              ; +$0152 : 263C00000001
    bra.w L_002E32                                    ; +$0158 : 60000008
L_002E2C:
    move.l #$00000000,d3                              ; +$015C : 263C00000000
L_002E32:
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
    beq.w L_002F78                                    ; +$0010 : 67000128
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002F78                                    ; +$001A : 6700011E
    cmpi.l #$00000180,d4                              ; +$001E : 0C8400000180
    bcs.w L_002F78                                    ; +$0024 : 65000114
    cmpi.l #$000001BE,d4                              ; +$0028 : 0C84000001BE
    bhi.w L_002F78                                    ; +$002E : 6200010A
    move.l d4,d0                                      ; +$0032 : 2004
    andi.l #$00000001,d0                              ; +$0034 : 028000000001
    tst.l d0                                          ; +$003A : 4A80
    bne.w L_002F78                                    ; +$003C : 660000FC
    cmpi.l #$00000FFF,d5                              ; +$0040 : 0C8500000FFF
    bhi.w L_002F78                                    ; +$0046 : 620000F2
    move.l 342(a4),d6                                 ; +$004A : 2C2C0156
    move.l d6,d0                                      ; +$004E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0050 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0056 : 2440
    tst.l d0                                          ; +$0058 : 4A80
    beq.w L_002F78                                    ; +$005A : 670000DE
    move.l 64(a4),d1                                  ; +$005E : 222C0040
    cmp.l d1,d0                                       ; +$0062 : B081
    bne.w L_002F78                                    ; +$0064 : 660000D4
    move.l d6,d0                                      ; +$0068 : 2006
    andi.l #$00000003,d0                              ; +$006A : 028000000003
    tst.l d0                                          ; +$0070 : 4A80
    bne.w L_002F78                                    ; +$0072 : 660000C6
    movea.l 456(a5),a0                                ; +$0076 : 206D01C8
    movea.l 8(a0),a6                                  ; +$007A : 2C680008
    move.l a6,d0                                      ; +$007E : 200E
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_002F78                                    ; +$0082 : 670000B6
    movea.l 8(a2),a1                                  ; +$0086 : 226A0008
    move.l a1,d0                                      ; +$008A : 2009
    tst.l d0                                          ; +$008C : 4A80
    beq.w L_002F78                                    ; +$008E : 670000AA
    move.l 12(a1),d0                                  ; +$0092 : 2029000C
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_002F78                                    ; +$0098 : 670000A0
    movea.l 16(a1),a0                                 ; +$009C : 20690010
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_002F78                                    ; +$00A4 : 67000094
    move.w 30(a1),d0                                  ; +$00A8 : 3029001E
    cmpi.w #$0040,d0                                  ; +$00AC : 0C400040
    bne.w L_002F78                                    ; +$00B0 : 66000088
    move.w 28(a1),d7                                  ; +$00B4 : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00B8 : 0C470000
    bls.w L_002F78                                    ; +$00BC : 6300007C
    cmpi.w #$003F,d7                                  ; +$00C0 : 0C47003F
    bcc.w L_002F78                                    ; +$00C4 : 64000074
    movea.l 16(a1),a0                                 ; +$00C8 : 20690010
    subq.l #6,a0                                      ; +$00CC : 5D88
    move.w (a0),d0                                    ; +$00CE : 3010
    cmpi.w #$0001,d0                                  ; +$00D0 : 0C400001
    bne.w L_002F78                                    ; +$00D4 : 66000064
    move.w 2(a0),d0                                   ; +$00D8 : 30280002
    cmpi.w #$2710,d0                                  ; +$00DC : 0C402710
    bne.w L_002F78                                    ; +$00E0 : 66000058
    move.w 4(a0),d0                                   ; +$00E4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00E8 : 0C4000FF
    bne.w L_002F78                                    ; +$00EC : 6600004C
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
    bra.w L_002F6E                                    ; +$012C : 60000002
L_002F6E:
    move.l #$00000001,d3                              ; +$0130 : 263C00000001
    bra.w L_002F7E                                    ; +$0136 : 60000008
L_002F78:
    move.l #$00000000,d3                              ; +$013A : 263C00000000
L_002F7E:
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
    beq.w L_00304C                                    ; +$000C : 670000B8
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00304C                                    ; +$0016 : 670000AE
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_00304C                                    ; +$002A : 6700009A
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_00304C                                    ; +$0034 : 66000090
    move.l d6,d0                                      ; +$0038 : 2006
    andi.l #$00000003,d0                              ; +$003A : 028000000003
    tst.l d0                                          ; +$0040 : 4A80
    bne.w L_00304C                                    ; +$0042 : 66000082
    movea.l 8(a2),a1                                  ; +$0046 : 226A0008
    move.l a1,d0                                      ; +$004A : 2009
    tst.l d0                                          ; +$004C : 4A80
    beq.w L_00304C                                    ; +$004E : 67000076
    move.l 12(a1),d0                                  ; +$0052 : 2029000C
    tst.l d0                                          ; +$0056 : 4A80
    beq.w L_00304C                                    ; +$0058 : 6700006C
    movea.l 16(a1),a0                                 ; +$005C : 20690010
    move.l a0,d0                                      ; +$0060 : 2008
    tst.l d0                                          ; +$0062 : 4A80
    beq.w L_00304C                                    ; +$0064 : 67000060
    move.w 30(a1),d0                                  ; +$0068 : 3029001E
    cmpi.w #$0040,d0                                  ; +$006C : 0C400040
    bne.w L_00304C                                    ; +$0070 : 66000054
    move.w 28(a1),d7                                  ; +$0074 : 3E29001C
    cmpi.w #$0001,d7                                  ; +$0078 : 0C470001
    bls.w L_00304C                                    ; +$007C : 63000048
    cmpi.w #$0040,d7                                  ; +$0080 : 0C470040
    bhi.w L_00304C                                    ; +$0084 : 62000040
    movea.l 16(a1),a0                                 ; +$0088 : 20690010
    subq.l #6,a0                                      ; +$008C : 5D88
    move.w (a0),d0                                    ; +$008E : 3010
    cmpi.w #$0001,d0                                  ; +$0090 : 0C400001
    bne.w L_00304C                                    ; +$0094 : 66000030
    move.w 2(a0),d0                                   ; +$0098 : 30280002
    cmpi.w #$2710,d0                                  ; +$009C : 0C402710
    bne.w L_00304C                                    ; +$00A0 : 66000024
    move.w 4(a0),d0                                   ; +$00A4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00A8 : 0C4000FF
    bne.w L_00304C                                    ; +$00AC : 66000018
    ori.l #$00000002,342(a4)                          ; +$00B0 : 00AC000000020156
    bra.w L_003042                                    ; +$00B8 : 60000002
L_003042:
    move.l #$00000001,d3                              ; +$00BC : 263C00000001
    bra.w L_003052                                    ; +$00C2 : 60000008
L_00304C:
    move.l #$00000000,d3                              ; +$00C6 : 263C00000000
L_003052:
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
    beq.w L_0030BC                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0030BC                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0030BC                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_0030BC                                    ; +$002E : 6600002E
    move.l 12(a2),d0                                  ; +$0032 : 202A000C
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_0030BC                                    ; +$0038 : 67000024
    bmi.w L_0030BC                                    ; +$003C : 6B000020
    move.w 14(a1),d3                                  ; +$0040 : 3629000E
    ext.l d3                                          ; +$0044 : 48C3
    move.w 4(a1),d1                                   ; +$0046 : 32290004
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_0030BC                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_0030BC                                    ; +$0056 : 64000006
    bra.w L_0030C2                                    ; +$005A : 60000008
L_0030BC:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_0030C2:
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
    beq.w L_00312C                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00312C                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_00312C                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_00312C                                    ; +$002E : 6600002E
    move.l 16(a2),d0                                  ; +$0032 : 202A0010
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_00312C                                    ; +$0038 : 67000024
    bmi.w L_00312C                                    ; +$003C : 6B000020
    move.w 12(a1),d3                                  ; +$0040 : 3629000C
    ext.l d3                                          ; +$0044 : 48C3
    move.w 6(a1),d1                                   ; +$0046 : 32290006
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_00312C                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_00312C                                    ; +$0056 : 64000006
    bra.w L_003132                                    ; +$005A : 60000008
L_00312C:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_003132:
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
    beq.w L_003214                                    ; +$000C : 670000C8
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_003214                                    ; +$0016 : 670000BE
    movea.l 36(a2),a4                                 ; +$001A : 286A0024
    move.l a4,d0                                      ; +$001E : 200C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_003214                                    ; +$0022 : 670000B2
    move.l 46(a4),d0                                  ; +$0026 : 202C002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_003214                                    ; +$002E : 660000A6
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
    lea L_003222(pc),a0                               ; +$0056 : 41FA008C
    move.l #$00000000,d0                              ; +$005A : 203C00000000
    movea.l a4,a1                                     ; +$0060 : 224C
    move.l #$00000000,d1                              ; +$0062 : 223C00000000
    jsr -444(a6)                                      ; +$0068 : 4EAEFE44
    tst.l d0                                          ; +$006C : 4A80
    bne.w L_003206                                    ; +$006E : 66000058
    movea.l 20(a4),a6                                 ; +$0072 : 2C6C0014
    move.l a6,d0                                      ; +$0076 : 200E
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0031F2                                    ; +$007A : 67000038
    jsr -42(a6)                                       ; +$007E : 4EAEFFD6
    andi.w #$7000,d0                                  ; +$0082 : 02407000
    move.l #$00000000,d3                              ; +$0086 : 263C00000000
    move.l d0,d1                                      ; +$008C : 2200
    andi.w #$4000,d1                                  ; +$008E : 02414000
    beq.w L_0031D6                                    ; +$0092 : 67000004
    addq.l #1,d3                                      ; +$0096 : 5283
L_0031D6:
    move.l d0,d1                                      ; +$0098 : 2200
    andi.w #$2000,d1                                  ; +$009A : 02412000
    beq.w L_0031E2                                    ; +$009E : 67000004
    addq.l #2,d3                                      ; +$00A2 : 5483
L_0031E2:
    move.l d0,d1                                      ; +$00A4 : 2200
    andi.w #$1000,d1                                  ; +$00A6 : 02411000
    beq.w L_0031EE                                    ; +$00AA : 67000004
    addq.l #4,d3                                      ; +$00AE : 5883
L_0031EE:
    bra.w L_0031F8                                    ; +$00B0 : 60000008
L_0031F2:
    move.l #$FFFFFFFF,d3                              ; +$00B4 : 263CFFFFFFFF
L_0031F8:
    movea.l $0004.w,a6                                ; +$00BA : 2C780004
    movea.l a4,a1                                     ; +$00BE : 224C
    jsr -450(a6)                                      ; +$00C0 : 4EAEFE3E
    bra.w L_00320C                                    ; +$00C4 : 60000008
L_003206:
    move.l #$FFFFFFFF,d3                              ; +$00C8 : 263CFFFFFFFF
L_00320C:
    lea 48(a7),a7                                     ; +$00CE : 4FEF0030
    bra.w L_00321A                                    ; +$00D2 : 60000008
L_003214:
    move.l #$FFFFFFFF,d3                              ; +$00D6 : 263CFFFFFFFF
L_00321A:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00DC : 4CDF77F7
    moveq #0,d2                                       ; +$00E0 : 7400
    rts                                               ; +$00E2 : 4E75
L_003222:
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
    beq.w L_003290                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_003290                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_00327C                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 610000A8
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_003290                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11932(a2),a2                                  ; +$0038 : 45EA2E9C
    move.l 4(a2),d3                                   ; +$003C : 262A0004
    clr.l 4(a2)                                       ; +$0040 : 42AA0004
    bra.w L_003292                                    ; +$0044 : 60000018
L_00327C:
    lea 11932(a2),a2                                  ; +$0048 : 45EA2E9C
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_003290:
    moveq #-1,d3                                      ; +$005C : 76FF
L_003292:
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
    beq.w L_0032FA                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_0032FA                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_0032E6                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 6100003E
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_0032FA                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11932(a2),a2                                  ; +$0038 : 45EA2E9C
    move.l 8(a2),d3                                   ; +$003C : 262A0008
    clr.l 8(a2)                                       ; +$0040 : 42AA0008
    bra.w L_0032FC                                    ; +$0044 : 60000018
L_0032E6:
    lea 11932(a2),a2                                  ; +$0048 : 45EA2E9C
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_0032FA:
    moveq #-1,d3                                      ; +$005C : 76FF
L_0032FC:
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
    beq.w L_00351A                                    ; +$000C : 67000204
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00351A                                    ; +$0016 : 670001FA
    movea.l 36(a2),a3                                 ; +$001A : 266A0024
    move.l a3,d0                                      ; +$001E : 200B
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_00351A                                    ; +$0022 : 670001EE
    move.l 46(a3),d0                                  ; +$0026 : 202B002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_00351A                                    ; +$002E : 660001E2
    movea.l 86(a3),a4                                 ; +$0032 : 286B0056
    move.l a4,d0                                      ; +$0036 : 200C
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_00351A                                    ; +$003A : 670001D6
    lea 11932(a2),a2                                  ; +$003E : 45EA2E9C
    move.l (a2),d0                                    ; +$0042 : 2012
    move.l a3,d1                                      ; +$0044 : 220B
    cmp.l d1,d0                                       ; +$0046 : B081
    beq.w L_00337C                                    ; +$0048 : 6700002A
    move.l a3,(a2)                                    ; +$004C : 248B
    clr.l 4(a2)                                       ; +$004E : 42AA0004
    clr.l 8(a2)                                       ; +$0052 : 42AA0008
    clr.l 12(a2)                                      ; +$0056 : 42AA000C
    clr.l 28(a2)                                      ; +$005A : 42AA001C
    move.l 24(a3),d0                                  ; +$005E : 202B0018
    andi.l #$00002000,d0                              ; +$0062 : 028000002000
    beq.w L_00337C                                    ; +$0068 : 6700000A
    move.l #$00000001,28(a2)                          ; +$006C : 257C00000001001C
L_00337C:
    move.l 24(a3),d0                                  ; +$0074 : 202B0018
    andi.l #$00002000,d0                              ; +$0078 : 028000002000
    bne.w L_00339A                                    ; +$007E : 66000012
    clr.l 4(a2)                                       ; +$0082 : 42AA0004
    clr.l 8(a2)                                       ; +$0086 : 42AA0008
    clr.l 12(a2)                                      ; +$008A : 42AA000C
    clr.l 28(a2)                                      ; +$008E : 42AA001C
L_00339A:
    moveq #63,d7                                      ; +$0092 : 7E3F
L_00339C:
    move.l 24(a2),d0                                  ; +$0094 : 202A0018
    cmpi.l #$00000010,d0                              ; +$0098 : 0C8000000010
    bcc.w L_003514                                    ; +$009E : 6400016C
    movea.l a4,a0                                     ; +$00A2 : 204C
    movea.l $0004.w,a6                                ; +$00A4 : 2C780004
    jsr -372(a6)                                      ; +$00A8 : 4EAEFE8C
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_003514                                    ; +$00AE : 6700015C
    movea.l d0,a3                                     ; +$00B2 : 2640
    move.l 20(a3),d4                                  ; +$00B4 : 282B0014
    moveq #0,d5                                       ; +$00B8 : 7A00
    move.w 24(a3),d5                                  ; +$00BA : 3A2B0018
    moveq #0,d6                                       ; +$00BE : 7C00
    move.w 26(a3),d6                                  ; +$00C0 : 3C2B001A
    cmpi.l #$00000400,d4                              ; +$00C4 : 0C8400000400
    beq.w L_0033F8                                    ; +$00CA : 67000024
    cmpi.l #$00000008,d4                              ; +$00CE : 0C8400000008
    beq.w L_003438                                    ; +$00D4 : 6700005A
    cmpi.l #$00080000,d4                              ; +$00D8 : 0C8400080000
    beq.w L_0034CA                                    ; +$00DE : 670000E2
    cmpi.l #$00040000,d4                              ; +$00E2 : 0C8400040000
    beq.w L_0034DE                                    ; +$00E8 : 670000EC
    bra.w L_003506                                    ; +$00EC : 60000110
L_0033F8:
    move.l d5,d0                                      ; +$00F0 : 2005
    andi.l #$00000080,d0                              ; +$00F2 : 028000000080
    bne.w L_003506                                    ; +$00F8 : 66000104
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
    bra.w L_003506                                    ; +$012C : 600000D0
L_003438:
    move.l 28(a2),d0                                  ; +$0130 : 202A001C
    tst.l d0                                          ; +$0134 : 4A80
    beq.w L_003506                                    ; +$0136 : 670000C6
    move.l d5,d0                                      ; +$013A : 2005
    andi.l #$0000007F,d0                              ; +$013C : 02800000007F
    cmpi.l #$00000068,d0                              ; +$0142 : 0C8000000068
    beq.w L_00346C                                    ; +$0148 : 6700001A
    cmpi.l #$00000069,d0                              ; +$014C : 0C8000000069
    beq.w L_003472                                    ; +$0152 : 67000016
    cmpi.l #$0000006A,d0                              ; +$0156 : 0C800000006A
    beq.w L_003478                                    ; +$015C : 67000012
    bra.w L_003506                                    ; +$0160 : 6000009C
L_00346C:
    moveq #1,d1                                       ; +$0164 : 7201
    bra.w L_00347A                                    ; +$0166 : 6000000A
L_003472:
    moveq #2,d1                                       ; +$016A : 7202
    bra.w L_00347A                                    ; +$016C : 60000004
L_003478:
    moveq #4,d1                                       ; +$0170 : 7204
L_00347A:
    move.l d5,d0                                      ; +$0172 : 2005
    andi.l #$00000080,d0                              ; +$0174 : 028000000080
    bne.w L_0034A8                                    ; +$017A : 66000024
    move.l 12(a2),d0                                  ; +$017E : 202A000C
    move.l d0,d4                                      ; +$0182 : 2800
    and.l d1,d4                                       ; +$0184 : C881
    tst.l d4                                          ; +$0186 : 4A84
    bne.w L_003506                                    ; +$0188 : 66000074
    or.l d1,d0                                        ; +$018C : 8081
    move.l d0,12(a2)                                  ; +$018E : 2540000C
    move.l 4(a2),d0                                   ; +$0192 : 202A0004
    or.l d1,d0                                        ; +$0196 : 8081
    move.l d0,4(a2)                                   ; +$0198 : 25400004
    bra.w L_003506                                    ; +$019C : 60000060
L_0034A8:
    move.l 12(a2),d0                                  ; +$01A0 : 202A000C
    move.l d0,d4                                      ; +$01A4 : 2800
    and.l d1,d4                                       ; +$01A6 : C881
    tst.l d4                                          ; +$01A8 : 4A84
    beq.w L_003506                                    ; +$01AA : 67000052
    sub.l d1,d0                                       ; +$01AE : 9081
    move.l d0,12(a2)                                  ; +$01B0 : 2540000C
    move.l 8(a2),d0                                   ; +$01B4 : 202A0008
    or.l d1,d0                                        ; +$01B8 : 8081
    move.l d0,8(a2)                                   ; +$01BA : 25400008
    bra.w L_003506                                    ; +$01BE : 6000003E
L_0034CA:
    clr.l 4(a2)                                       ; +$01C2 : 42AA0004
    clr.l 8(a2)                                       ; +$01C6 : 42AA0008
    clr.l 12(a2)                                      ; +$01CA : 42AA000C
    clr.l 28(a2)                                      ; +$01CE : 42AA001C
    bra.w L_003506                                    ; +$01D2 : 6000002A
L_0034DE:
    clr.l 4(a2)                                       ; +$01D6 : 42AA0004
    clr.l 8(a2)                                       ; +$01DA : 42AA0008
    clr.l 12(a2)                                      ; +$01DE : 42AA000C
    clr.l 28(a2)                                      ; +$01E2 : 42AA001C
    movea.l (a2),a0                                   ; +$01E6 : 2052
    move.l 24(a0),d0                                  ; +$01E8 : 20280018
    andi.l #$00002000,d0                              ; +$01EC : 028000002000
    beq.w L_003506                                    ; +$01F2 : 6700000A
    move.l #$00000001,28(a2)                          ; +$01F6 : 257C00000001001C
L_003506:
    movea.l a3,a1                                     ; +$01FE : 224B
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -378(a6)                                      ; +$0204 : 4EAEFE86
    dbra d7,L_00339C                                  ; +$0208 : 51CFFE8A
L_003514:
    moveq #0,d0                                       ; +$020C : 7000
    bra.w L_00351C                                    ; +$020E : 60000004
L_00351A:
    moveq #-1,d0                                      ; +$0212 : 70FF
L_00351C:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$0214 : 4CDF7FFE
    rts                                               ; +$0218 : 4E75
L_003522:
    bsr.w Internal_33                                 ; +$021A : 6100FDE4
    tst.l d0                                          ; +$021E : 4A80
    bne.w L_003588                                    ; +$0220 : 6600005E
    movem.l d1-d7/a0-a6,-(a7)                         ; +$0224 : 48E77FFE
    movea.l 456(a5),a2                                ; +$0228 : 246D01C8
    lea 11932(a2),a2                                  ; +$022C : 45EA2E9C
    move.l 24(a2),d0                                  ; +$0230 : 202A0018
    tst.l d0                                          ; +$0234 : 4A80
    beq.w L_003580                                    ; +$0236 : 67000040
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
    bra.w L_003582                                    ; +$0274 : 60000004
L_003580:
    moveq #0,d0                                       ; +$0278 : 7000
L_003582:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$027A : 4CDF7FFE
    rts                                               ; +$027E : 4E75
L_003588:
    moveq #0,d0                                       ; +$0280 : 7000
    rts                                               ; +$0282 : 4E75
    dcb.b 144,0
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 34 : aga hotspot hit --------
Entry_34:
Aga_Hotspot_Hit:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l (a3)+,d3                                   ; +$0008 : 261B
    move.l (a3)+,d2                                   ; +$000A : 241B
    move.l (a3)+,d1                                   ; +$000C : 221B
    move.l (a3)+,d0                                   ; +$000E : 201B
    tst.l d0                                          ; +$0010 : 4A80
    bmi.w L_003676                                    ; +$0012 : 6B000042
    tst.l d1                                          ; +$0016 : 4A81
    bmi.w L_003676                                    ; +$0018 : 6B00003C
    tst.l d4                                          ; +$001C : 4A84
    ble.w L_003676                                    ; +$001E : 6F000036
    tst.l d5                                          ; +$0022 : 4A85
    ble.w L_003676                                    ; +$0024 : 6F000030
    cmp.l d2,d0                                       ; +$0028 : B082
    blt.w L_003676                                    ; +$002A : 6D00002A
    sub.l d2,d0                                       ; +$002E : 9082
    bvs.w L_003676                                    ; +$0030 : 69000024
    cmp.l d4,d0                                       ; +$0034 : B084
    bge.w L_003676                                    ; +$0036 : 6C00001E
    cmp.l d3,d1                                       ; +$003A : B283
    blt.w L_003676                                    ; +$003C : 6D000018
    sub.l d3,d1                                       ; +$0040 : 9283
    bvs.w L_003676                                    ; +$0042 : 69000012
    cmp.l d5,d1                                       ; +$0046 : B285
    bge.w L_003676                                    ; +$0048 : 6C00000C
    move.l #$00000001,d3                              ; +$004C : 263C00000001
    bra.w L_00367C                                    ; +$0052 : 60000008
L_003676:
    move.l #$00000000,d3                              ; +$0056 : 263C00000000
L_00367C:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$005C : 4CDF77F7
    moveq #0,d2                                       ; +$0060 : 7400
    rts                                               ; +$0062 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 35 : aga rect overlap --------
Entry_35:
Aga_Rect_Overlap:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l (a3)+,d4                                   ; +$000A : 281B
    move.l (a3)+,d3                                   ; +$000C : 261B
    move.l (a3)+,d2                                   ; +$000E : 241B
    move.l (a3)+,d1                                   ; +$0010 : 221B
    move.l (a3)+,d0                                   ; +$0012 : 201B
    tst.l d2                                          ; +$0014 : 4A82
    ble.w L_003702                                    ; +$0016 : 6F000062
    tst.l d3                                          ; +$001A : 4A83
    ble.w L_003702                                    ; +$001C : 6F00005C
    tst.l d6                                          ; +$0020 : 4A86
    ble.w L_003702                                    ; +$0022 : 6F000056
    tst.l d7                                          ; +$0026 : 4A87
    ble.w L_003702                                    ; +$0028 : 6F000050
    cmp.l d4,d0                                       ; +$002C : B084
    blt.w L_0036CA                                    ; +$002E : 6D000012
    sub.l d4,d0                                       ; +$0032 : 9084
    bvs.w L_003702                                    ; +$0034 : 69000044
    cmp.l d6,d0                                       ; +$0038 : B086
    bge.w L_003702                                    ; +$003A : 6C00003E
    bra.w L_0036D6                                    ; +$003E : 6000000E
L_0036CA:
    sub.l d0,d4                                       ; +$0042 : 9880
    bvs.w L_003702                                    ; +$0044 : 69000034
    cmp.l d2,d4                                       ; +$0048 : B882
    bge.w L_003702                                    ; +$004A : 6C00002E
L_0036D6:
    cmp.l d5,d1                                       ; +$004E : B285
    blt.w L_0036EC                                    ; +$0050 : 6D000012
    sub.l d5,d1                                       ; +$0054 : 9285
    bvs.w L_003702                                    ; +$0056 : 69000022
    cmp.l d7,d1                                       ; +$005A : B287
    bge.w L_003702                                    ; +$005C : 6C00001C
    bra.w L_0036F8                                    ; +$0060 : 6000000E
L_0036EC:
    sub.l d1,d5                                       ; +$0064 : 9A81
    bvs.w L_003702                                    ; +$0066 : 69000012
    cmp.l d3,d5                                       ; +$006A : BA83
    bge.w L_003702                                    ; +$006C : 6C00000C
L_0036F8:
    move.l #$00000001,d3                              ; +$0070 : 263C00000001
    bra.w L_003708                                    ; +$0076 : 60000008
L_003702:
    move.l #$00000000,d3                              ; +$007A : 263C00000000
L_003708:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0080 : 4CDF77F7
    moveq #0,d2                                       ; +$0084 : 7400
    rts                                               ; +$0086 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 36 : aga text --------
Entry_36:
Aga_Text:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    movea.l d3,a4                                     ; +$0004 : 2843
    move.l (a3)+,d7                                   ; +$0006 : 2E1B
    move.l (a3)+,d6                                   ; +$0008 : 2C1B
    move.l (a3)+,d5                                   ; +$000A : 2A1B
    moveq #0,d3                                       ; +$000C : 7600
    move.l a4,d0                                      ; +$000E : 200C
    tst.l d0                                          ; +$0010 : 4A80
    beq.w L_00398C                                    ; +$0012 : 67000264
    move.l #$00000000,d4                              ; +$0016 : 283C00000000
    move.w (a4),d4                                    ; +$001C : 3814
    tst.l d4                                          ; +$001E : 4A84
    beq.w L_00398C                                    ; +$0020 : 67000256
    cmpi.l #$00000080,d4                              ; +$0024 : 0C8400000080
    bgt.w L_00398C                                    ; +$002A : 6E00024C
    addq.l #2,a4                                      ; +$002E : 548C
    tst.l d5                                          ; +$0030 : 4A85
    bmi.w L_00398C                                    ; +$0032 : 6B000244
    tst.l d6                                          ; +$0036 : 4A86
    bmi.w L_00398C                                    ; +$0038 : 6B00023E
    tst.l d7                                          ; +$003C : 4A87
    bmi.w L_00398C                                    ; +$003E : 6B000238
    movea.l 456(a5),a2                                ; +$0042 : 246D01C8
    move.l a2,d0                                      ; +$0046 : 200A
    tst.l d0                                          ; +$0048 : 4A80
    beq.w L_00398C                                    ; +$004A : 6700022C
    move.l (a2),d0                                    ; +$004E : 2012
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_00398C                                    ; +$0052 : 67000224
    move.l 8(a2),d0                                   ; +$0056 : 202A0008
    tst.l d0                                          ; +$005A : 4A80
    beq.w L_00398C                                    ; +$005C : 6700021A
    move.l 32(a2),d0                                  ; +$0060 : 202A0020
    tst.l d0                                          ; +$0064 : 4A80
    beq.w L_00398C                                    ; +$0066 : 67000210
    move.l 12(a2),d0                                  ; +$006A : 202A000C
    tst.l d0                                          ; +$006E : 4A80
    ble.w L_00398C                                    ; +$0070 : 6F000206
    cmpi.l #$00007FFF,d0                              ; +$0074 : 0C8000007FFF
    bgt.w L_00398C                                    ; +$007A : 6E0001FC
    cmp.l d0,d5                                       ; +$007E : BA80
    bge.w L_00398C                                    ; +$0080 : 6C0001F6
    move.l 16(a2),d0                                  ; +$0084 : 202A0010
    tst.l d0                                          ; +$0088 : 4A80
    ble.w L_00398C                                    ; +$008A : 6F0001EC
    cmpi.l #$00007FFF,d0                              ; +$008E : 0C8000007FFF
    bgt.w L_00398C                                    ; +$0094 : 6E0001E2
    cmp.l d0,d6                                       ; +$0098 : BC80
    bge.w L_00398C                                    ; +$009A : 6C0001DC
    move.l 28(a2),d0                                  ; +$009E : 202A001C
    tst.l d0                                          ; +$00A2 : 4A80
    ble.w L_00398C                                    ; +$00A4 : 6F0001D2
    cmpi.l #$00000008,d0                              ; +$00A8 : 0C8000000008
    bgt.w L_00398C                                    ; +$00AE : 6E0001C8
    move.l #$00000001,d1                              ; +$00B2 : 223C00000001
L_0037CC:
    lsl.l #1,d1                                       ; +$00B8 : E389
    subq.l #1,d0                                      ; +$00BA : 5380
    bne.w L_0037CC                                    ; +$00BC : 6600FFFA
    cmp.l d1,d7                                       ; +$00C0 : BE81
    bcc.w L_00398C                                    ; +$00C2 : 640001B4
    movea.l 32(a2),a2                                 ; +$00C6 : 246A0020
    move.l 8(a2),d0                                   ; +$00CA : 202A0008
    tst.l d0                                          ; +$00CE : 4A80
    beq.w L_0037F8                                    ; +$00D0 : 67000012
    cmpi.l #$00000001,d0                              ; +$00D4 : 0C8000000001
    bne.w L_00398C                                    ; +$00DA : 6600019C
    movea.l (a2),a0                                   ; +$00DE : 2052
    bra.w L_0037FC                                    ; +$00E0 : 60000006
L_0037F8:
    movea.l 4(a2),a0                                  ; +$00E4 : 206A0004
L_0037FC:
    move.l a0,d0                                      ; +$00E8 : 2008
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_00398C                                    ; +$00EC : 6700018A
    movea.l (a0),a0                                   ; +$00F0 : 2050
    move.l a0,d0                                      ; +$00F2 : 2008
    tst.l d0                                          ; +$00F4 : 4A80
    beq.w L_00398C                                    ; +$00F6 : 67000180
    move.l a0,d2                                      ; +$00FA : 2408
    movea.l 456(a5),a1                                ; +$00FC : 226D01C8
    move.l #$00000000,d1                              ; +$0100 : 223C00000000
    move.w (a0),d1                                    ; +$0106 : 3210
    lsl.l #3,d1                                       ; +$0108 : E789
    cmp.l 12(a1),d1                                   ; +$010A : B2A9000C
    blt.w L_00398C                                    ; +$010E : 6D000168
    move.l #$00000000,d1                              ; +$0112 : 223C00000000
    move.w 2(a0),d1                                   ; +$0118 : 32280002
    cmp.l 16(a1),d1                                   ; +$011C : B2A90010
    blt.w L_00398C                                    ; +$0120 : 6D000156
    move.l #$00000000,d1                              ; +$0124 : 223C00000000
    move.b 5(a0),d1                                   ; +$012A : 12280005
    cmp.l 28(a1),d1                                   ; +$012E : B2A9001C
    bne.w L_00398C                                    ; +$0132 : 66000144
    move.l d1,d0                                      ; +$0136 : 2001
    movea.l a0,a1                                     ; +$0138 : 2248
    addq.l #8,a1                                      ; +$013A : 5089
L_003850:
    move.l (a1)+,d1                                   ; +$013C : 2219
    tst.l d1                                          ; +$013E : 4A81
    beq.w L_00398C                                    ; +$0140 : 67000136
    cmpi.l #$FFFFFFFF,d1                              ; +$0144 : 0C81FFFFFFFF
    beq.w L_00398C                                    ; +$014A : 6700012C
    subq.l #1,d0                                      ; +$014E : 5380
    bne.w L_003850                                    ; +$0150 : 6600FFEA
    lea -160(a7),a7                                   ; +$0154 : 4FEFFF60
    movea.l a7,a2                                     ; +$0158 : 244F
    movea.l a2,a1                                     ; +$015A : 224A
    movea.l 456(a5),a0                                ; +$015C : 206D01C8
    movea.l 8(a0),a6                                  ; +$0160 : 2C680008
    jsr -198(a6)                                      ; +$0164 : 4EAEFF3A
    move.l d2,4(a2)                                   ; +$0168 : 25420004
    movea.l 456(a5),a0                                ; +$016C : 206D01C8
    movea.l (a0),a0                                   ; +$0170 : 2050
    bsr.w L_005752                                    ; +$0172 : 61001ECA
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_003898                                    ; +$0178 : 6700000A
    movea.l d0,a0                                     ; +$017C : 2040
    movea.l a7,a1                                     ; +$017E : 224F
    jsr -66(a6)                                       ; +$0180 : 4EAEFFBE
L_003898:
    move.l 52(a2),d0                                  ; +$0184 : 202A0034
    tst.l d0                                          ; +$0188 : 4A80
    beq.w L_003988                                    ; +$018A : 670000E8
    movea.l a7,a2                                     ; +$018E : 244F
    lea 128(a7),a2                                    ; +$0190 : 45EF0080
    movea.l a7,a1                                     ; +$0194 : 224F
    movea.l a4,a0                                     ; +$0196 : 204C
    move.l d4,d0                                      ; +$0198 : 2004
    jsr -690(a6)                                      ; +$019A : 4EAEFD4E
    move.w 4(a2),d0                                   ; +$019E : 302A0004
    ext.l d0                                          ; +$01A2 : 48C0
    add.l d5,d0                                       ; +$01A4 : D085
    tst.l d0                                          ; +$01A6 : 4A80
    bmi.w L_003988                                    ; +$01A8 : 6B0000CA
    move.w 6(a2),d0                                   ; +$01AC : 302A0006
    ext.l d0                                          ; +$01B0 : 48C0
    add.l d6,d0                                       ; +$01B2 : D086
    tst.l d0                                          ; +$01B4 : 4A80
    bmi.w L_003988                                    ; +$01B6 : 6B0000BC
    move.w 8(a2),d0                                   ; +$01BA : 302A0008
    ext.l d0                                          ; +$01BE : 48C0
    add.l d5,d0                                       ; +$01C0 : D085
    movea.l 456(a5),a1                                ; +$01C2 : 226D01C8
    cmp.l 12(a1),d0                                   ; +$01C6 : B0A9000C
    bge.w L_003988                                    ; +$01CA : 6C0000A8
    move.w 10(a2),d0                                  ; +$01CE : 302A000A
    ext.l d0                                          ; +$01D2 : 48C0
    add.l d6,d0                                       ; +$01D4 : D086
    movea.l 456(a5),a1                                ; +$01D6 : 226D01C8
    cmp.l 16(a1),d0                                   ; +$01DA : B0A90010
    bge.w L_003988                                    ; +$01DE : 6C000094
    move.w (a2),d0                                    ; +$01E2 : 3012
    tst.w d0                                          ; +$01E4 : 4A40
    beq.w L_003988                                    ; +$01E6 : 6700008C
    move.w 2(a2),d0                                   ; +$01EA : 302A0002
    tst.w d0                                          ; +$01EE : 4A40
    beq.w L_003988                                    ; +$01F0 : 67000082
    movea.l 456(a5),a0                                ; +$01F4 : 206D01C8
    movea.l 32(a0),a0                                 ; +$01F8 : 20680020
    move.l 20(a0),d0                                  ; +$01FC : 20280014
    andi.l #$00000001,d0                              ; +$0200 : 028000000001
    beq.w L_003956                                    ; +$0206 : 6700003A
    movea.l 12(a0),a0                                 ; +$020A : 2068000C
    move.l a0,d0                                      ; +$020E : 2008
    tst.l d0                                          ; +$0210 : 4A80
    beq.w L_003988                                    ; +$0212 : 67000060
    movea.l $0004.w,a6                                ; +$0216 : 2C780004
    jsr -372(a6)                                      ; +$021A : 4EAEFE8C
    tst.l d0                                          ; +$021E : 4A80
    beq.w L_003988                                    ; +$0220 : 67000052
    movea.l 456(a5),a0                                ; +$0224 : 206D01C8
    movea.l 32(a0),a0                                 ; +$0228 : 20680020
    move.l 20(a0),d0                                  ; +$022C : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0230 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$0236 : 21400014
    movea.l 456(a5),a0                                ; +$023A : 206D01C8
    movea.l 8(a0),a6                                  ; +$023E : 2C680008
L_003956:
    movea.l a7,a1                                     ; +$0242 : 224F
    move.l d7,d0                                      ; +$0244 : 2007
    jsr -342(a6)                                      ; +$0246 : 4EAEFEAA
    movea.l a7,a1                                     ; +$024A : 224F
    move.l #$00000000,d0                              ; +$024C : 203C00000000
    jsr -354(a6)                                      ; +$0252 : 4EAEFE9E
    movea.l a7,a1                                     ; +$0256 : 224F
    move.l d5,d0                                      ; +$0258 : 2005
    move.l d6,d1                                      ; +$025A : 2206
    jsr -240(a6)                                      ; +$025C : 4EAEFF10
    movea.l a7,a1                                     ; +$0260 : 224F
    movea.l a4,a0                                     ; +$0262 : 204C
    move.l d4,d0                                      ; +$0264 : 2004
    jsr -60(a6)                                       ; +$0266 : 4EAEFFC4
    jsr -228(a6)                                      ; +$026A : 4EAEFF1C
    move.l #$00000001,d3                              ; +$026E : 263C00000001
L_003988:
    lea 160(a7),a7                                    ; +$0274 : 4FEF00A0
L_00398C:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0278 : 4CDF77F7
    moveq #0,d2                                       ; +$027C : 7400
    rts                                               ; +$027E : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 37 : aga palette load --------
Entry_37:
Aga_Palette_Load:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    movea.l 456(a5),a0                                ; +$0004 : 206D01C8
    movea.l d3,a1                                     ; +$0008 : 2243
    lea -128(a7),a7                                   ; +$000A : 4FEFFF80
    movea.l a7,a5                                     ; +$000E : 2A4F
    move.l #$00000000,(a5)                            ; +$0010 : 2ABC00000000
    move.l #$00000000,4(a5)                           ; +$0016 : 2B7C000000000004
    move.l #$00000000,8(a5)                           ; +$001E : 2B7C000000000008
    move.l #$00000000,12(a5)                          ; +$0026 : 2B7C00000000000C
    move.l #$00000000,16(a5)                          ; +$002E : 2B7C000000000010
    move.l #$00000000,20(a5)                          ; +$0036 : 2B7C000000000014
    move.l #$00000000,24(a5)                          ; +$003E : 2B7C000000000018
    move.l #$00000000,28(a5)                          ; +$0046 : 2B7C00000000001C
    move.l #$00000000,32(a5)                          ; +$004E : 2B7C000000000020
    move.l #$00000000,36(a5)                          ; +$0056 : 2B7C000000000024
    move.l #$00000000,40(a5)                          ; +$005E : 2B7C000000000028
    move.l #$00000000,44(a5)                          ; +$0066 : 2B7C00000000002C
    move.l #$00000000,48(a5)                          ; +$006E : 2B7C000000000030
    move.l #$00000000,52(a5)                          ; +$0076 : 2B7C000000000034
    move.l #$00000000,56(a5)                          ; +$007E : 2B7C000000000038
    move.l #$00000000,60(a5)                          ; +$0086 : 2B7C00000000003C
    move.l #$00000000,64(a5)                          ; +$008E : 2B7C000000000040
    move.l #$00000000,68(a5)                          ; +$0096 : 2B7C000000000044
    move.l #$00000000,72(a5)                          ; +$009E : 2B7C000000000048
    move.l #$00000000,76(a5)                          ; +$00A6 : 2B7C00000000004C
    move.l #$00000000,80(a5)                          ; +$00AE : 2B7C000000000050
    move.l #$00000000,84(a5)                          ; +$00B6 : 2B7C000000000054
    move.l #$00000000,88(a5)                          ; +$00BE : 2B7C000000000058
    move.l #$00000000,92(a5)                          ; +$00C6 : 2B7C00000000005C
    move.l #$00000000,96(a5)                          ; +$00CE : 2B7C000000000060
    move.l #$00000000,100(a5)                         ; +$00D6 : 2B7C000000000064
    move.l #$00000000,104(a5)                         ; +$00DE : 2B7C000000000068
    move.l #$00000000,108(a5)                         ; +$00E6 : 2B7C00000000006C
    move.l #$00000000,112(a5)                         ; +$00EE : 2B7C000000000070
    move.l #$00000000,116(a5)                         ; +$00F6 : 2B7C000000000074
    move.l #$00000000,120(a5)                         ; +$00FE : 2B7C000000000078
    move.l #$00000000,124(a5)                         ; +$0106 : 2B7C00000000007C
    move.l a0,(a5)                                    ; +$010E : 2A88
    move.l a1,4(a5)                                   ; +$0110 : 2B490004
    bsr.w L_003AFE                                    ; +$0114 : 61000050
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_003AE8                                    ; +$011A : 67000034
    bsr.w L_003C2C                                    ; +$011E : 61000174
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_003AE8                                    ; +$0124 : 6700002A
    bsr.w L_003CE6                                    ; +$0128 : 61000224
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_003AE8                                    ; +$012E : 67000020
    bsr.w L_003D82                                    ; +$0132 : 610002B6
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_003AE8                                    ; +$0138 : 67000016
    bsr.w L_003DFE                                    ; +$013C : 61000328
    tst.l d0                                          ; +$0140 : 4A80
    beq.w L_003AE8                                    ; +$0142 : 6700000C
    move.l #$00000001,d3                              ; +$0146 : 263C00000001
    bra.w L_003AEE                                    ; +$014C : 60000008
L_003AE8:
    move.l #$00000000,d3                              ; +$0150 : 263C00000000
L_003AEE:
    bsr.w L_003E38                                    ; +$0156 : 61000348
    lea 128(a7),a7                                    ; +$015A : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$015E : 4CDF7FF7
    moveq #0,d2                                       ; +$0162 : 7400
    rts                                               ; +$0164 : 4E75
L_003AFE:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0166 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$016A : 246D0004
    move.l #$00000000,d4                              ; +$016E : 283C00000000
    move.w (a2)+,d4                                   ; +$0174 : 381A
    tst.l d4                                          ; +$0176 : 4A84
    beq.w L_003C1E                                    ; +$0178 : 6700010C
    move.l d4,d0                                      ; +$017C : 2004
    addq.l #1,d0                                      ; +$017E : 5280
    move.l #$00010001,d1                              ; +$0180 : 223C00010001
    movea.l $0004.w,a6                                ; +$0186 : 2C780004
    jsr -684(a6)                                      ; +$018A : 4EAEFD54
    tst.l d0                                          ; +$018E : 4A80
    beq.w L_003C1E                                    ; +$0190 : 670000F4
    move.l d0,12(a5)                                  ; +$0194 : 2B40000C
    movea.l d0,a1                                     ; +$0198 : 2240
L_003B32:
    move.b (a2)+,(a1)+                                ; +$019A : 12DA
    subq.l #1,d4                                      ; +$019C : 5384
    bne.w L_003B32                                    ; +$019E : 6600FFFA
    lea L_003EB8(pc),a1                               ; +$01A2 : 43FA037C
    move.l #$00000000,d0                              ; +$01A6 : 203C00000000
    movea.l $0004.w,a6                                ; +$01AC : 2C780004
    jsr -552(a6)                                      ; +$01B0 : 4EAEFDD8
    tst.l d0                                          ; +$01B4 : 4A80
    beq.w L_003C1E                                    ; +$01B6 : 670000CE
    move.l d0,16(a5)                                  ; +$01BA : 2B400010
    movea.l d0,a6                                     ; +$01BE : 2C40
    move.l 12(a5),d1                                  ; +$01C0 : 222D000C
    move.l #$000003ED,d2                              ; +$01C4 : 243C000003ED
    jsr -30(a6)                                       ; +$01CA : 4EAEFFE2
    tst.l d0                                          ; +$01CE : 4A80
    beq.w L_003C1E                                    ; +$01D0 : 670000B4
    move.l d0,20(a5)                                  ; +$01D4 : 2B400014
    move.l d0,d1                                      ; +$01D8 : 2200
    move.l a5,d2                                      ; +$01DA : 240D
    addi.l #$00000068,d2                              ; +$01DC : 068200000068
    move.l #$0000000C,d3                              ; +$01E2 : 263C0000000C
    jsr -42(a6)                                       ; +$01E8 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$01EC : 0C800000000C
    bne.w L_003C1E                                    ; +$01F2 : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$01F6 : 0CAD464F524D0068
    bne.w L_003C1E                                    ; +$01FE : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$0202 : 0CAD494C424D0070
    bne.w L_003C1E                                    ; +$020A : 6600007A
    move.l 108(a5),d4                                 ; +$020E : 282D006C
    cmpi.l #$00000004,d4                              ; +$0212 : 0C8400000004
    bcs.w L_003C1E                                    ; +$0218 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$021C : 0C847FFFFFF7
    bhi.w L_003C1E                                    ; +$0222 : 62000062
    addq.l #8,d4                                      ; +$0226 : 5084
    move.l d4,28(a5)                                  ; +$0228 : 2B44001C
    move.l d4,d0                                      ; +$022C : 2004
    move.l #$00010001,d1                              ; +$022E : 223C00010001
    movea.l $0004.w,a6                                ; +$0234 : 2C780004
    jsr -684(a6)                                      ; +$0238 : 4EAEFD54
    tst.l d0                                          ; +$023C : 4A80
    beq.w L_003C1E                                    ; +$023E : 67000046
    move.l d0,24(a5)                                  ; +$0242 : 2B400018
    movea.l d0,a2                                     ; +$0246 : 2440
    move.l 104(a5),(a2)                               ; +$0248 : 24AD0068
    move.l 108(a5),4(a2)                              ; +$024C : 256D006C0004
    move.l 112(a5),8(a2)                              ; +$0252 : 256D00700008
    move.l 20(a5),d1                                  ; +$0258 : 222D0014
    move.l a2,d2                                      ; +$025C : 240A
    addi.l #$0000000C,d2                              ; +$025E : 06820000000C
    move.l d4,d3                                      ; +$0264 : 2604
    subi.l #$0000000C,d3                              ; +$0266 : 04830000000C
    move.l d3,d4                                      ; +$026C : 2803
    movea.l 16(a5),a6                                 ; +$026E : 2C6D0010
    jsr -42(a6)                                       ; +$0272 : 4EAEFFD6
    cmp.l d4,d0                                       ; +$0276 : B084
    bne.w L_003C1E                                    ; +$0278 : 6600000C
    move.l #$00000001,d0                              ; +$027C : 203C00000001
    bra.w L_003C24                                    ; +$0282 : 60000008
L_003C1E:
    move.l #$00000000,d0                              ; +$0286 : 203C00000000
L_003C24:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$028C : 4CDF5FFE
    tst.l d0                                          ; +$0290 : 4A80
    rts                                               ; +$0292 : 4E75
L_003C2C:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0294 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$0298 : 206D0018
    move.l 28(a5),d7                                  ; +$029C : 2E2D001C
    subi.l #$0000000C,d7                              ; +$02A0 : 04870000000C
    move.l a0,d0                                      ; +$02A6 : 2008
    addi.l #$0000000C,d0                              ; +$02A8 : 06800000000C
    movea.l d0,a0                                     ; +$02AE : 2040
L_003C48:
    tst.l d7                                          ; +$02B0 : 4A87
    beq.w L_003C9A                                    ; +$02B2 : 6700004E
    cmpi.l #$00000008,d7                              ; +$02B6 : 0C8700000008
    bcs.w L_003CD8                                    ; +$02BC : 65000082
    move.l (a0)+,d3                                   ; +$02C0 : 2618
    move.l (a0)+,d2                                   ; +$02C2 : 2418
    subq.l #8,d7                                      ; +$02C4 : 5187
    cmp.l d7,d2                                       ; +$02C6 : B487
    bhi.w L_003CD8                                    ; +$02C8 : 62000076
    move.l d2,d1                                      ; +$02CC : 2202
    andi.l #$00000001,d1                              ; +$02CE : 028100000001
    add.l d2,d1                                       ; +$02D4 : D282
    cmp.l d7,d1                                       ; +$02D6 : B287
    bhi.w L_003CD8                                    ; +$02D8 : 62000066
    sub.l d1,d7                                       ; +$02DC : 9E81
    cmpi.l #$434D4150,d3                              ; +$02DE : 0C83434D4150
    bne.w L_003C90                                    ; +$02E4 : 66000012
    tst.l 36(a5)                                      ; +$02E8 : 4AAD0024
    bne.w L_003CD8                                    ; +$02EC : 66000052
    move.l a0,36(a5)                                  ; +$02F0 : 2B480024
    move.l d2,40(a5)                                  ; +$02F4 : 2B420028
L_003C90:
    move.l a0,d0                                      ; +$02F8 : 2008
    add.l d1,d0                                       ; +$02FA : D081
    movea.l d0,a0                                     ; +$02FC : 2040
    bra.w L_003C48                                    ; +$02FE : 6000FFB0
L_003C9A:
    tst.l 36(a5)                                      ; +$0302 : 4AAD0024
    beq.w L_003CD8                                    ; +$0306 : 67000038
    move.l 40(a5),d0                                  ; +$030A : 202D0028
    tst.l d0                                          ; +$030E : 4A80
    beq.w L_003CD8                                    ; +$0310 : 6700002E
    cmpi.l #$00000300,d0                              ; +$0314 : 0C8000000300
    bhi.w L_003CD8                                    ; +$031A : 62000024
    divu.w #$0003,d0                                  ; +$031E : 80FC0003
    move.l d0,d1                                      ; +$0322 : 2200
    swap d1                                           ; +$0324 : 4841
    tst.w d1                                          ; +$0326 : 4A41
    bne.w L_003CD8                                    ; +$0328 : 66000016
    andi.l #$0000FFFF,d0                              ; +$032C : 02800000FFFF
    move.l d0,40(a5)                                  ; +$0332 : 2B400028
    move.l #$00000001,d0                              ; +$0336 : 203C00000001
    bra.w L_003CDE                                    ; +$033C : 60000008
L_003CD8:
    move.l #$00000000,d0                              ; +$0340 : 203C00000000
L_003CDE:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0346 : 4CDF5FFE
    tst.l d0                                          ; +$034A : 4A80
    rts                                               ; +$034C : 4E75
L_003CE6:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$034E : 48E77FFA
    movea.l (a5),a2                                   ; +$0352 : 2455
    move.l a2,d0                                      ; +$0354 : 200A
    tst.l d0                                          ; +$0356 : 4A80
    beq.w L_003D74                                    ; +$0358 : 67000082
    move.l (a2),d0                                    ; +$035C : 2012
    tst.l d0                                          ; +$035E : 4A80
    beq.w L_003D74                                    ; +$0360 : 6700007A
    move.l d0,88(a5)                                  ; +$0364 : 2B400058
    move.l 8(a2),d0                                   ; +$0368 : 202A0008
    tst.l d0                                          ; +$036C : 4A80
    beq.w L_003D74                                    ; +$036E : 6700006C
    move.l 28(a2),d0                                  ; +$0372 : 202A001C
    tst.l d0                                          ; +$0376 : 4A80
    ble.w L_003D74                                    ; +$0378 : 6F000062
    cmpi.l #$00000008,d0                              ; +$037C : 0C8000000008
    bgt.w L_003D74                                    ; +$0382 : 6E000058
    move.l 24(a2),d0                                  ; +$0386 : 202A0018
    andi.l #$00000C80,d0                              ; +$038A : 028000000C80
    bne.w L_003D74                                    ; +$0390 : 6600004A
    movea.l 88(a5),a0                                 ; +$0394 : 206D0058
    movea.l 48(a0),a1                                 ; +$0398 : 22680030
    move.l a1,d0                                      ; +$039C : 2009
    tst.l d0                                          ; +$039E : 4A80
    beq.w L_003D74                                    ; +$03A0 : 6700003A
    move.l #$00000000,d0                              ; +$03A4 : 203C00000000
    move.w 2(a1),d0                                   ; +$03AA : 30290002
    tst.l d0                                          ; +$03AE : 4A80
    beq.w L_003D74                                    ; +$03B0 : 6700002A
    cmpi.l #$00000100,d0                              ; +$03B4 : 0C8000000100
    bhi.w L_003D74                                    ; +$03BA : 62000020
    cmp.l 40(a5),d0                                   ; +$03BE : B0AD0028
    bcs.w L_003D74                                    ; +$03C2 : 65000018
    move.l 20(a2),d0                                  ; +$03C6 : 202A0014
    cmp.l 40(a5),d0                                   ; +$03CA : B0AD0028
    bcs.w L_003D74                                    ; +$03CE : 6500000C
    move.l #$00000001,d0                              ; +$03D2 : 203C00000001
    bra.w L_003D7A                                    ; +$03D8 : 60000008
L_003D74:
    move.l #$00000000,d0                              ; +$03DC : 203C00000000
L_003D7A:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$03E2 : 4CDF5FFE
    tst.l d0                                          ; +$03E6 : 4A80
    rts                                               ; +$03E8 : 4E75
L_003D82:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$03EA : 48E77FFA
    move.l 40(a5),d0                                  ; +$03EE : 202D0028
    move.l d0,d1                                      ; +$03F2 : 2200
    lsl.l #1,d0                                       ; +$03F4 : E388
    add.l d1,d0                                       ; +$03F6 : D081
    lsl.l #2,d0                                       ; +$03F8 : E588
    addq.l #8,d0                                      ; +$03FA : 5080
    move.l #$00010001,d1                              ; +$03FC : 223C00010001
    movea.l $0004.w,a6                                ; +$0402 : 2C780004
    jsr -684(a6)                                      ; +$0406 : 4EAEFD54
    tst.l d0                                          ; +$040A : 4A80
    beq.w L_003DF0                                    ; +$040C : 6700004A
    move.l d0,96(a5)                                  ; +$0410 : 2B400060
    movea.l d0,a1                                     ; +$0414 : 2240
    move.l 40(a5),d0                                  ; +$0416 : 202D0028
    swap d0                                           ; +$041A : 4840
    move.l d0,(a1)+                                   ; +$041C : 22C0
    movea.l 36(a5),a0                                 ; +$041E : 206D0024
    move.l 40(a5),d4                                  ; +$0422 : 282D0028
    move.l d4,d0                                      ; +$0426 : 2004
    add.l d4,d0                                       ; +$0428 : D084
    add.l d0,d4                                       ; +$042A : D880
L_003DC4:
    move.l #$00000000,d0                              ; +$042C : 203C00000000
    move.b (a0)+,d0                                   ; +$0432 : 1018
    move.l d0,d1                                      ; +$0434 : 2200
    lsl.l #8,d0                                       ; +$0436 : E188
    or.l d1,d0                                        ; +$0438 : 8081
    move.l d0,d1                                      ; +$043A : 2200
    swap d0                                           ; +$043C : 4840
    or.l d1,d0                                        ; +$043E : 8081
    move.l d0,(a1)+                                   ; +$0440 : 22C0
    subq.l #1,d4                                      ; +$0442 : 5384
    bne.w L_003DC4                                    ; +$0444 : 6600FFE6
    move.l #$00000000,(a1)                            ; +$0448 : 22BC00000000
    move.l #$00000001,d0                              ; +$044E : 203C00000001
    bra.w L_003DF6                                    ; +$0454 : 60000008
L_003DF0:
    move.l #$00000000,d0                              ; +$0458 : 203C00000000
L_003DF6:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$045E : 4CDF5FFE
    tst.l d0                                          ; +$0462 : 4A80
    rts                                               ; +$0464 : 4E75
L_003DFE:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0466 : 48E77FFA
    movea.l 96(a5),a1                                 ; +$046A : 226D0060
    move.l 88(a5),d0                                  ; +$046E : 202D0058
    addi.l #$0000002C,d0                              ; +$0472 : 06800000002C
    movea.l d0,a0                                     ; +$0478 : 2040
    movea.l (a5),a2                                   ; +$047A : 2455
    movea.l 8(a2),a6                                  ; +$047C : 2C6A0008
    jsr -882(a6)                                      ; +$0480 : 4EAEFC8E
    jsr -270(a6)                                      ; +$0484 : 4EAEFEF2
    move.l #$00000001,d0                              ; +$0488 : 203C00000001
    bra.w L_003E30                                    ; +$048E : 60000008
    move.l #$00000000,d0                              ; +$0492 : 203C00000000
L_003E30:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0498 : 4CDF5FFE
    tst.l d0                                          ; +$049C : 4A80
    rts                                               ; +$049E : 4E75
L_003E38:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$04A0 : 48E77FFA
    tst.l 20(a5)                                      ; +$04A4 : 4AAD0014
    beq.w L_003E50                                    ; +$04A8 : 6700000E
    movea.l 16(a5),a6                                 ; +$04AC : 2C6D0010
    move.l 20(a5),d1                                  ; +$04B0 : 222D0014
    jsr -36(a6)                                       ; +$04B4 : 4EAEFFDC
L_003E50:
    tst.l 96(a5)                                      ; +$04B8 : 4AAD0060
    beq.w L_003E64                                    ; +$04BC : 6700000E
    movea.l 96(a5),a1                                 ; +$04C0 : 226D0060
    movea.l $0004.w,a6                                ; +$04C4 : 2C780004
    jsr -690(a6)                                      ; +$04C8 : 4EAEFD4E
L_003E64:
    tst.l 24(a5)                                      ; +$04CC : 4AAD0018
    beq.w L_003E78                                    ; +$04D0 : 6700000E
    movea.l 24(a5),a1                                 ; +$04D4 : 226D0018
    movea.l $0004.w,a6                                ; +$04D8 : 2C780004
    jsr -690(a6)                                      ; +$04DC : 4EAEFD4E
L_003E78:
    tst.l 12(a5)                                      ; +$04E0 : 4AAD000C
    beq.w L_003E8C                                    ; +$04E4 : 6700000E
    movea.l 12(a5),a1                                 ; +$04E8 : 226D000C
    movea.l $0004.w,a6                                ; +$04EC : 2C780004
    jsr -690(a6)                                      ; +$04F0 : 4EAEFD4E
L_003E8C:
    tst.l 16(a5)                                      ; +$04F4 : 4AAD0010
    beq.w L_003EA0                                    ; +$04F8 : 6700000E
    movea.l 16(a5),a1                                 ; +$04FC : 226D0010
    movea.l $0004.w,a6                                ; +$0500 : 2C780004
    jsr -414(a6)                                      ; +$0504 : 4EAEFE62
L_003EA0:
    move.l #$00000001,d0                              ; +$0508 : 203C00000001
    bra.w L_003EB0                                    ; +$050E : 60000008
    move.l #$00000000,d0                              ; +$0512 : 203C00000000
L_003EB0:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0518 : 4CDF5FFE
    tst.l d0                                          ; +$051C : 4A80
    rts                                               ; +$051E : 4E75
L_003EB8:
    dc.b "dos.library"
    dc.b $00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 38 : aga palette set --------
Entry_38:
Aga_Palette_Set:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l (a3)+,d4                                   ; +$000A : 281B
    move.l #$00000000,d3                              ; +$000C : 263C00000000
    cmpi.l #$000000FF,d4                              ; +$0012 : 0C84000000FF
    bhi.w L_003FEA                                    ; +$0018 : 62000108
    cmpi.l #$000000FF,d5                              ; +$001C : 0C85000000FF
    bhi.w L_003FEA                                    ; +$0022 : 620000FE
    cmpi.l #$000000FF,d6                              ; +$0026 : 0C86000000FF
    bhi.w L_003FEA                                    ; +$002C : 620000F4
    cmpi.l #$000000FF,d7                              ; +$0030 : 0C87000000FF
    bhi.w L_003FEA                                    ; +$0036 : 620000EA
    movea.l 456(a5),a2                                ; +$003A : 246D01C8
    move.l a2,d0                                      ; +$003E : 200A
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_003FEA                                    ; +$0042 : 670000DE
    move.l (a2),d0                                    ; +$0046 : 2012
    tst.l d0                                          ; +$0048 : 4A80
    beq.w L_003FEA                                    ; +$004A : 670000D6
    move.l 8(a2),d0                                   ; +$004E : 202A0008
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_003FEA                                    ; +$0054 : 670000CC
    move.l 28(a2),d0                                  ; +$0058 : 202A001C
    tst.l d0                                          ; +$005C : 4A80
    ble.w L_003FEA                                    ; +$005E : 6F0000C2
    cmpi.l #$00000008,d0                              ; +$0062 : 0C8000000008
    bgt.w L_003FEA                                    ; +$0068 : 6E0000B8
    move.l 24(a2),d0                                  ; +$006C : 202A0018
    andi.l #$00000C80,d0                              ; +$0070 : 028000000C80
    bne.w L_003FEA                                    ; +$0076 : 660000AA
    movea.l (a2),a0                                   ; +$007A : 2052
    movea.l 48(a0),a1                                 ; +$007C : 22680030
    move.l a1,d0                                      ; +$0080 : 2009
    tst.l d0                                          ; +$0082 : 4A80
    beq.w L_003FEA                                    ; +$0084 : 6700009C
    move.l #$00000000,d0                              ; +$0088 : 203C00000000
    move.w 2(a1),d0                                   ; +$008E : 30290002
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_003FEA                                    ; +$0094 : 6700008C
    cmpi.l #$00000100,d0                              ; +$0098 : 0C8000000100
    bhi.w L_003FEA                                    ; +$009E : 62000082
    tst.l d4                                          ; +$00A2 : 4A84
    bmi.w L_003FEA                                    ; +$00A4 : 6B00007C
    cmp.l d0,d4                                       ; +$00A8 : B880
    bcc.w L_003FEA                                    ; +$00AA : 64000076
    cmp.l 20(a2),d4                                   ; +$00AE : B8AA0014
    bcc.w L_003FEA                                    ; +$00B2 : 6400006E
    movea.l 8(a2),a6                                  ; +$00B6 : 2C6A0008
    move.l a0,d0                                      ; +$00BA : 2008
    addi.l #$0000002C,d0                              ; +$00BC : 06800000002C
    movea.l d0,a0                                     ; +$00C2 : 2040
    lea -20(a7),a7                                    ; +$00C4 : 4FEFFFEC
    movea.l a7,a1                                     ; +$00C8 : 224F
    move.l d4,d0                                      ; +$00CA : 2004
    addi.l #$00010000,d0                              ; +$00CC : 068000010000
    move.l d0,(a1)                                    ; +$00D2 : 2280
    move.l d5,d0                                      ; +$00D4 : 2005
    move.l d0,d1                                      ; +$00D6 : 2200
    lsl.l #8,d0                                       ; +$00D8 : E188
    or.l d1,d0                                        ; +$00DA : 8081
    move.l d0,d1                                      ; +$00DC : 2200
    swap d0                                           ; +$00DE : 4840
    or.l d1,d0                                        ; +$00E0 : 8081
    move.l d0,4(a7)                                   ; +$00E2 : 2F400004
    move.l d6,d0                                      ; +$00E6 : 2006
    move.l d0,d1                                      ; +$00E8 : 2200
    lsl.l #8,d0                                       ; +$00EA : E188
    or.l d1,d0                                        ; +$00EC : 8081
    move.l d0,d1                                      ; +$00EE : 2200
    swap d0                                           ; +$00F0 : 4840
    or.l d1,d0                                        ; +$00F2 : 8081
    move.l d0,8(a7)                                   ; +$00F4 : 2F400008
    move.l d7,d0                                      ; +$00F8 : 2007
    move.l d0,d1                                      ; +$00FA : 2200
    lsl.l #8,d0                                       ; +$00FC : E188
    or.l d1,d0                                        ; +$00FE : 8081
    move.l d0,d1                                      ; +$0100 : 2200
    swap d0                                           ; +$0102 : 4840
    or.l d1,d0                                        ; +$0104 : 8081
    move.l d0,12(a7)                                  ; +$0106 : 2F40000C
    move.l #$00000000,16(a7)                          ; +$010A : 2F7C000000000010
    movea.l a7,a1                                     ; +$0112 : 224F
    jsr -882(a6)                                      ; +$0114 : 4EAEFC8E
    lea 20(a7),a7                                     ; +$0118 : 4FEF0014
    move.l #$00000001,d3                              ; +$011C : 263C00000001
L_003FEA:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0122 : 4CDF77F7
    moveq #0,d2                                       ; +$0126 : 7400
    rts                                               ; +$0128 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 39 : aga palette get --------
Entry_39:
Aga_Palette_Get:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d4                                      ; +$0004 : 2803
    move.l #$FFFFFFFF,d3                              ; +$0006 : 263CFFFFFFFF
    cmpi.l #$000000FF,d4                              ; +$000C : 0C84000000FF
    bhi.w L_0040DE                                    ; +$0012 : 620000D4
    movea.l 456(a5),a2                                ; +$0016 : 246D01C8
    move.l a2,d0                                      ; +$001A : 200A
    tst.l d0                                          ; +$001C : 4A80
    beq.w L_0040DE                                    ; +$001E : 670000C8
    move.l (a2),d0                                    ; +$0022 : 2012
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0040DE                                    ; +$0026 : 670000C0
    move.l 8(a2),d0                                   ; +$002A : 202A0008
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0040DE                                    ; +$0030 : 670000B6
    move.l 28(a2),d0                                  ; +$0034 : 202A001C
    tst.l d0                                          ; +$0038 : 4A80
    ble.w L_0040DE                                    ; +$003A : 6F0000AC
    cmpi.l #$00000008,d0                              ; +$003E : 0C8000000008
    bgt.w L_0040DE                                    ; +$0044 : 6E0000A2
    move.l 24(a2),d0                                  ; +$0048 : 202A0018
    andi.l #$00000C80,d0                              ; +$004C : 028000000C80
    bne.w L_0040DE                                    ; +$0052 : 66000094
    movea.l (a2),a0                                   ; +$0056 : 2052
    movea.l 48(a0),a1                                 ; +$0058 : 22680030
    move.l a1,d0                                      ; +$005C : 2009
    tst.l d0                                          ; +$005E : 4A80
    beq.w L_0040DE                                    ; +$0060 : 67000086
    move.l #$00000000,d0                              ; +$0064 : 203C00000000
    move.w 2(a1),d0                                   ; +$006A : 30290002
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_0040DE                                    ; +$0070 : 67000076
    cmpi.l #$00000100,d0                              ; +$0074 : 0C8000000100
    bhi.w L_0040DE                                    ; +$007A : 6200006C
    tst.l d4                                          ; +$007E : 4A84
    bmi.w L_0040DE                                    ; +$0080 : 6B000066
    cmp.l d0,d4                                       ; +$0084 : B880
    bcc.w L_0040DE                                    ; +$0086 : 64000060
    cmp.l 20(a2),d4                                   ; +$008A : B8AA0014
    bcc.w L_0040DE                                    ; +$008E : 64000058
    movea.l 8(a2),a6                                  ; +$0092 : 2C6A0008
    move.l a0,d0                                      ; +$0096 : 2008
    addi.l #$0000002C,d0                              ; +$0098 : 06800000002C
    movea.l d0,a0                                     ; +$009E : 2040
    lea -12(a7),a7                                    ; +$00A0 : 4FEFFFF4
    move.l d4,d0                                      ; +$00A4 : 2004
    move.l #$00000001,d1                              ; +$00A6 : 223C00000001
    movea.l a7,a1                                     ; +$00AC : 224F
    movea.l 4(a0),a0                                  ; +$00AE : 20680004
    jsr -900(a6)                                      ; +$00B2 : 4EAEFC7C
    move.l (a7),d5                                    ; +$00B6 : 2A17
    move.l 4(a7),d6                                   ; +$00B8 : 2C2F0004
    move.l 8(a7),d7                                   ; +$00BC : 2E2F0008
    andi.l #$FF000000,d5                              ; +$00C0 : 0285FF000000
    andi.l #$FF000000,d6                              ; +$00C6 : 0286FF000000
    andi.l #$FF000000,d7                              ; +$00CC : 0287FF000000
    lsr.l #8,d5                                       ; +$00D2 : E08D
    lsr.l #8,d6                                       ; +$00D4 : E08E
    lsr.l #8,d6                                       ; +$00D6 : E08E
    lsr.l #8,d7                                       ; +$00D8 : E08F
    lsr.l #8,d7                                       ; +$00DA : E08F
    lsr.l #8,d7                                       ; +$00DC : E08F
    or.l d6,d5                                        ; +$00DE : 8A86
    or.l d7,d5                                        ; +$00E0 : 8A87
    move.l d5,d3                                      ; +$00E2 : 2605
    lea 12(a7),a7                                     ; +$00E4 : 4FEF000C
L_0040DE:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00E8 : 4CDF77F7
    moveq #0,d2                                       ; +$00EC : 7400
    rts                                               ; +$00EE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 40 : aga palette save --------
Entry_40:
Aga_Palette_Save:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    movea.l 456(a5),a0                                ; +$0004 : 206D01C8
    movea.l d3,a1                                     ; +$0008 : 2243
    lea -128(a7),a7                                   ; +$000A : 4FEFFF80
    movea.l a7,a5                                     ; +$000E : 2A4F
    move.l #$00000000,(a5)                            ; +$0010 : 2ABC00000000
    move.l #$00000000,4(a5)                           ; +$0016 : 2B7C000000000004
    move.l #$00000000,8(a5)                           ; +$001E : 2B7C000000000008
    move.l #$00000000,12(a5)                          ; +$0026 : 2B7C00000000000C
    move.l #$00000000,16(a5)                          ; +$002E : 2B7C000000000010
    move.l #$00000000,20(a5)                          ; +$0036 : 2B7C000000000014
    move.l #$00000000,24(a5)                          ; +$003E : 2B7C000000000018
    move.l #$00000000,28(a5)                          ; +$0046 : 2B7C00000000001C
    move.l #$00000000,32(a5)                          ; +$004E : 2B7C000000000020
    move.l #$00000000,36(a5)                          ; +$0056 : 2B7C000000000024
    move.l #$00000000,40(a5)                          ; +$005E : 2B7C000000000028
    move.l #$00000000,44(a5)                          ; +$0066 : 2B7C00000000002C
    move.l #$00000000,48(a5)                          ; +$006E : 2B7C000000000030
    move.l #$00000000,52(a5)                          ; +$0076 : 2B7C000000000034
    move.l #$00000000,56(a5)                          ; +$007E : 2B7C000000000038
    move.l #$00000000,60(a5)                          ; +$0086 : 2B7C00000000003C
    move.l #$00000000,64(a5)                          ; +$008E : 2B7C000000000040
    move.l #$00000000,68(a5)                          ; +$0096 : 2B7C000000000044
    move.l #$00000000,72(a5)                          ; +$009E : 2B7C000000000048
    move.l #$00000000,76(a5)                          ; +$00A6 : 2B7C00000000004C
    move.l #$00000000,80(a5)                          ; +$00AE : 2B7C000000000050
    move.l #$00000000,84(a5)                          ; +$00B6 : 2B7C000000000054
    move.l #$00000000,88(a5)                          ; +$00BE : 2B7C000000000058
    move.l #$00000000,92(a5)                          ; +$00C6 : 2B7C00000000005C
    move.l #$00000000,96(a5)                          ; +$00CE : 2B7C000000000060
    move.l #$00000000,100(a5)                         ; +$00D6 : 2B7C000000000064
    move.l #$00000000,104(a5)                         ; +$00DE : 2B7C000000000068
    move.l #$00000000,108(a5)                         ; +$00E6 : 2B7C00000000006C
    move.l #$00000000,112(a5)                         ; +$00EE : 2B7C000000000070
    move.l #$00000000,116(a5)                         ; +$00F6 : 2B7C000000000074
    move.l #$00000000,120(a5)                         ; +$00FE : 2B7C000000000078
    move.l #$00000000,124(a5)                         ; +$0106 : 2B7C00000000007C
    move.l a0,(a5)                                    ; +$010E : 2A88
    move.l a1,4(a5)                                   ; +$0110 : 2B490004
    bsr.w L_004246                                    ; +$0114 : 61000046
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_004230                                    ; +$011A : 6700002A
    bsr.w L_004324                                    ; +$011E : 6100011A
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_004230                                    ; +$0124 : 67000020
    bsr.w L_00438A                                    ; +$0128 : 61000176
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_004230                                    ; +$012E : 67000016
    bsr.w L_004498                                    ; +$0132 : 6100027A
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_004230                                    ; +$0138 : 6700000C
    move.l #$00000001,d3                              ; +$013C : 263C00000001
    bra.w L_004236                                    ; +$0142 : 60000008
L_004230:
    move.l #$00000000,d3                              ; +$0146 : 263C00000000
L_004236:
    bsr.w L_004526                                    ; +$014C : 610002EE
    lea 128(a7),a7                                    ; +$0150 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0154 : 4CDF7FF7
    moveq #0,d2                                       ; +$0158 : 7400
    rts                                               ; +$015A : 4E75
L_004246:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$015C : 48E77FFA
    movea.l (a5),a2                                   ; +$0160 : 2455
    move.l a2,d0                                      ; +$0162 : 200A
    tst.l d0                                          ; +$0164 : 4A80
    beq.w L_004316                                    ; +$0166 : 670000C4
    move.l (a2),d0                                    ; +$016A : 2012
    tst.l d0                                          ; +$016C : 4A80
    beq.w L_004316                                    ; +$016E : 670000BC
    move.l d0,20(a5)                                  ; +$0172 : 2B400014
    tst.l 8(a2)                                       ; +$0176 : 4AAA0008
    beq.w L_004316                                    ; +$017A : 670000B0
    move.l 28(a2),d0                                  ; +$017E : 202A001C
    tst.l d0                                          ; +$0182 : 4A80
    beq.w L_004316                                    ; +$0184 : 670000A6
    cmpi.l #$00000008,d0                              ; +$0188 : 0C8000000008
    bhi.w L_004316                                    ; +$018E : 6200009C
    move.l d0,40(a5)                                  ; +$0192 : 2B400028
    move.l 24(a2),d0                                  ; +$0196 : 202A0018
    andi.l #$00000C80,d0                              ; +$019A : 028000000C80
    bne.w L_004316                                    ; +$01A0 : 6600008A
    move.l 12(a2),d0                                  ; +$01A4 : 202A000C
    tst.l d0                                          ; +$01A8 : 4A80
    ble.w L_004316                                    ; +$01AA : 6F000080
    cmpi.l #$00007FFF,d0                              ; +$01AE : 0C8000007FFF
    bhi.w L_004316                                    ; +$01B4 : 62000076
    move.l d0,32(a5)                                  ; +$01B8 : 2B400020
    move.l 16(a2),d0                                  ; +$01BC : 202A0010
    tst.l d0                                          ; +$01C0 : 4A80
    ble.w L_004316                                    ; +$01C2 : 6F000068
    cmpi.l #$00007FFF,d0                              ; +$01C6 : 0C8000007FFF
    bhi.w L_004316                                    ; +$01CC : 6200005E
    move.l d0,36(a5)                                  ; +$01D0 : 2B400024
    move.l 20(a2),d4                                  ; +$01D4 : 282A0014
    tst.l d4                                          ; +$01D8 : 4A84
    ble.w L_004316                                    ; +$01DA : 6F000050
    cmpi.l #$00000100,d4                              ; +$01DE : 0C8400000100
    bhi.w L_004316                                    ; +$01E4 : 62000046
    movea.l 20(a5),a0                                 ; +$01E8 : 206D0014
    movea.l 48(a0),a1                                 ; +$01EC : 22680030
    move.l a1,d0                                      ; +$01F0 : 2009
    tst.l d0                                          ; +$01F2 : 4A80
    beq.w L_004316                                    ; +$01F4 : 67000036
    move.l d0,24(a5)                                  ; +$01F8 : 2B400018
    move.l #$00000000,d0                              ; +$01FC : 203C00000000
    move.w 2(a1),d0                                   ; +$0202 : 30290002
    tst.l d0                                          ; +$0206 : 4A80
    beq.w L_004316                                    ; +$0208 : 67000022
    cmpi.l #$00000100,d0                              ; +$020C : 0C8000000100
    bhi.w L_004316                                    ; +$0212 : 62000018
    cmp.l d0,d4                                       ; +$0216 : B880
    bls.w L_004308                                    ; +$0218 : 63000004
    move.l d0,d4                                      ; +$021C : 2800
L_004308:
    move.l d4,28(a5)                                  ; +$021E : 2B44001C
    move.l #$00000001,d0                              ; +$0222 : 203C00000001
    bra.w L_00431C                                    ; +$0228 : 60000008
L_004316:
    move.l #$00000000,d0                              ; +$022C : 203C00000000
L_00431C:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0232 : 4CDF5FFE
    tst.l d0                                          ; +$0236 : 4A80
    rts                                               ; +$0238 : 4E75
L_004324:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$023A : 48E77FFA
    movea.l 4(a5),a2                                  ; +$023E : 246D0004
    move.l a2,d0                                      ; +$0242 : 200A
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_00437C                                    ; +$0246 : 6700004A
    move.l #$00000000,d4                              ; +$024A : 283C00000000
    move.w (a2)+,d4                                   ; +$0250 : 381A
    tst.l d4                                          ; +$0252 : 4A84
    beq.w L_00437C                                    ; +$0254 : 6700003C
    cmpi.l #$000000FF,d4                              ; +$0258 : 0C84000000FF
    bhi.w L_00437C                                    ; +$025E : 62000032
    move.l d4,d0                                      ; +$0262 : 2004
    addq.l #1,d0                                      ; +$0264 : 5280
    move.l #$00010001,d1                              ; +$0266 : 223C00010001
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -684(a6)                                      ; +$0270 : 4EAEFD54
    tst.l d0                                          ; +$0274 : 4A80
    beq.w L_00437C                                    ; +$0276 : 6700001A
    move.l d0,8(a5)                                   ; +$027A : 2B400008
    movea.l d0,a1                                     ; +$027E : 2240
L_00436A:
    move.b (a2)+,(a1)+                                ; +$0280 : 12DA
    subq.l #1,d4                                      ; +$0282 : 5384
    bne.w L_00436A                                    ; +$0284 : 6600FFFA
    move.l #$00000001,d0                              ; +$0288 : 203C00000001
    bra.w L_004382                                    ; +$028E : 60000008
L_00437C:
    move.l #$00000000,d0                              ; +$0292 : 203C00000000
L_004382:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0298 : 4CDF5FFE
    tst.l d0                                          ; +$029C : 4A80
    rts                                               ; +$029E : 4E75
L_00438A:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$02A0 : 48E77FFA
    move.l 28(a5),d4                                  ; +$02A4 : 282D001C
    move.l d4,d0                                      ; +$02A8 : 2004
    add.l d4,d0                                       ; +$02AA : D084
    add.l d4,d0                                       ; +$02AC : D084
    move.l d0,44(a5)                                  ; +$02AE : 2B40002C
    move.l d0,d1                                      ; +$02B2 : 2200
    andi.l #$00000001,d1                              ; +$02B4 : 028100000001
    add.l d1,d0                                       ; +$02BA : D081
    addi.l #$00000030,d0                              ; +$02BC : 068000000030
    move.l d0,48(a5)                                  ; +$02C2 : 2B400030
    move.l 44(a5),d1                                  ; +$02C6 : 222D002C
    lsl.l #2,d1                                       ; +$02CA : E589
    add.l d1,d0                                       ; +$02CC : D081
    move.l #$00010001,d1                              ; +$02CE : 223C00010001
    movea.l $0004.w,a6                                ; +$02D4 : 2C780004
    jsr -684(a6)                                      ; +$02D8 : 4EAEFD54
    tst.l d0                                          ; +$02DC : 4A80
    beq.w L_00448A                                    ; +$02DE : 670000C0
    move.l d0,52(a5)                                  ; +$02E2 : 2B400034
    move.l d0,d1                                      ; +$02E6 : 2200
    add.l 48(a5),d1                                   ; +$02E8 : D2AD0030
    move.l d1,56(a5)                                  ; +$02EC : 2B410038
    movea.l 52(a5),a0                                 ; +$02F0 : 206D0034
    move.l #$464F524D,(a0)                            ; +$02F4 : 20BC464F524D
    move.l #$494C424D,8(a0)                           ; +$02FA : 217C494C424D0008
    move.l #$424D4844,12(a0)                          ; +$0302 : 217C424D4844000C
    move.l #$00000014,16(a0)                          ; +$030A : 217C000000140010
    move.l #$434D4150,40(a0)                          ; +$0312 : 217C434D41500028
    move.l 48(a5),d0                                  ; +$031A : 202D0030
    subi.l #$00000008,d0                              ; +$031E : 048000000008
    move.l d0,4(a0)                                   ; +$0324 : 21400004
    move.l 32(a5),d0                                  ; +$0328 : 202D0020
    move.w d0,20(a0)                                  ; +$032C : 31400014
    move.w d0,36(a0)                                  ; +$0330 : 31400024
    move.l 36(a5),d0                                  ; +$0334 : 202D0024
    move.w d0,22(a0)                                  ; +$0338 : 31400016
    move.w d0,38(a0)                                  ; +$033C : 31400026
    move.l 40(a5),d0                                  ; +$0340 : 202D0028
    move.b d0,28(a0)                                  ; +$0344 : 1140001C
    move.w #$0101,34(a0)                              ; +$0348 : 317C01010022
    move.l 44(a5),44(a0)                              ; +$034E : 216D002C002C
    movea.l 24(a5),a0                                 ; +$0354 : 206D0018
    move.l #$00000000,d0                              ; +$0358 : 203C00000000
    move.l 28(a5),d1                                  ; +$035E : 222D001C
    movea.l 56(a5),a1                                 ; +$0362 : 226D0038
    movea.l (a5),a2                                   ; +$0366 : 2455
    movea.l 8(a2),a6                                  ; +$0368 : 2C6A0008
    jsr -900(a6)                                      ; +$036C : 4EAEFC7C
    movea.l 56(a5),a0                                 ; +$0370 : 206D0038
    move.l 52(a5),d0                                  ; +$0374 : 202D0034
    addi.l #$00000030,d0                              ; +$0378 : 068000000030
    movea.l d0,a1                                     ; +$037E : 2240
    move.l 28(a5),d4                                  ; +$0380 : 282D001C
L_00446E:
    move.b (a0),(a1)+                                 ; +$0384 : 12D0
    addq.l #4,a0                                      ; +$0386 : 5888
    move.b (a0),(a1)+                                 ; +$0388 : 12D0
    addq.l #4,a0                                      ; +$038A : 5888
    move.b (a0),(a1)+                                 ; +$038C : 12D0
    addq.l #4,a0                                      ; +$038E : 5888
    subq.l #1,d4                                      ; +$0390 : 5384
    bne.w L_00446E                                    ; +$0392 : 6600FFF0
    move.l #$00000001,d0                              ; +$0396 : 203C00000001
    bra.w L_004490                                    ; +$039C : 60000008
L_00448A:
    move.l #$00000000,d0                              ; +$03A0 : 203C00000000
L_004490:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$03A6 : 4CDF5FFE
    tst.l d0                                          ; +$03AA : 4A80
    rts                                               ; +$03AC : 4E75
L_004498:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$03AE : 48E77FFA
    lea L_0045AE(pc),a1                               ; +$03B2 : 43FA0110
    movea.l $0004.w,a6                                ; +$03B6 : 2C780004
    jsr -552(a6)                                      ; +$03BA : 4EAEFDD8
    tst.l d0                                          ; +$03BE : 4A80
    beq.w L_004518                                    ; +$03C0 : 6700006C
    move.l d0,12(a5)                                  ; +$03C4 : 2B40000C
    movea.l d0,a6                                     ; +$03C8 : 2C40
    move.l 8(a5),d1                                   ; +$03CA : 222D0008
    move.l #$000003EE,d2                              ; +$03CE : 243C000003EE
    jsr -30(a6)                                       ; +$03D4 : 4EAEFFE2
    tst.l d0                                          ; +$03D8 : 4A80
    beq.w L_004518                                    ; +$03DA : 67000052
    move.l d0,16(a5)                                  ; +$03DE : 2B400010
    move.l #$00000001,60(a5)                          ; +$03E2 : 2B7C00000001003C
    move.l d0,d1                                      ; +$03EA : 2200
    move.l 52(a5),d2                                  ; +$03EC : 242D0034
    move.l 48(a5),d3                                  ; +$03F0 : 262D0030
    jsr -48(a6)                                       ; +$03F4 : 4EAEFFD0
    cmp.l 48(a5),d0                                   ; +$03F8 : B0AD0030
    bne.w L_004518                                    ; +$03FC : 66000030
    move.l 16(a5),d1                                  ; +$0400 : 222D0010
    movea.l 12(a5),a6                                 ; +$0404 : 2C6D000C
    jsr -36(a6)                                       ; +$0408 : 4EAEFFDC
    move.l d0,d4                                      ; +$040C : 2800
    move.l #$00000000,16(a5)                          ; +$040E : 2B7C000000000010
    tst.l d4                                          ; +$0416 : 4A84
    beq.w L_004518                                    ; +$0418 : 67000014
    move.l #$00000001,64(a5)                          ; +$041C : 2B7C000000010040
    move.l #$00000001,d0                              ; +$0424 : 203C00000001
    bra.w L_00451E                                    ; +$042A : 60000008
L_004518:
    move.l #$00000000,d0                              ; +$042E : 203C00000000
L_00451E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0434 : 4CDF5FFE
    tst.l d0                                          ; +$0438 : 4A80
    rts                                               ; +$043A : 4E75
L_004526:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$043C : 48E77FFA
    tst.l 16(a5)                                      ; +$0440 : 4AAD0010
    beq.w L_00453E                                    ; +$0444 : 6700000E
    movea.l 12(a5),a6                                 ; +$0448 : 2C6D000C
    move.l 16(a5),d1                                  ; +$044C : 222D0010
    jsr -36(a6)                                       ; +$0450 : 4EAEFFDC
L_00453E:
    tst.l 60(a5)                                      ; +$0454 : 4AAD003C
    beq.w L_00455A                                    ; +$0458 : 67000016
    tst.l 64(a5)                                      ; +$045C : 4AAD0040
    bne.w L_00455A                                    ; +$0460 : 6600000E
    movea.l 12(a5),a6                                 ; +$0464 : 2C6D000C
    move.l 8(a5),d1                                   ; +$0468 : 222D0008
    jsr -72(a6)                                       ; +$046C : 4EAEFFB8
L_00455A:
    tst.l 52(a5)                                      ; +$0470 : 4AAD0034
    beq.w L_00456E                                    ; +$0474 : 6700000E
    movea.l 52(a5),a1                                 ; +$0478 : 226D0034
    movea.l $0004.w,a6                                ; +$047C : 2C780004
    jsr -690(a6)                                      ; +$0480 : 4EAEFD4E
L_00456E:
    tst.l 8(a5)                                       ; +$0484 : 4AAD0008
    beq.w L_004582                                    ; +$0488 : 6700000E
    movea.l 8(a5),a1                                  ; +$048C : 226D0008
    movea.l $0004.w,a6                                ; +$0490 : 2C780004
    jsr -690(a6)                                      ; +$0494 : 4EAEFD4E
L_004582:
    tst.l 12(a5)                                      ; +$0498 : 4AAD000C
    beq.w L_004596                                    ; +$049C : 6700000E
    movea.l 12(a5),a1                                 ; +$04A0 : 226D000C
    movea.l $0004.w,a6                                ; +$04A4 : 2C780004
    jsr -414(a6)                                      ; +$04A8 : 4EAEFE62
L_004596:
    move.l #$00000001,d0                              ; +$04AC : 203C00000001
    bra.w L_0045A6                                    ; +$04B2 : 60000008
    move.l #$00000000,d0                              ; +$04B6 : 203C00000000
L_0045A6:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$04BC : 4CDF5FFE
    tst.l d0                                          ; +$04C0 : 4A80
    rts                                               ; +$04C2 : 4E75
L_0045AE:
    dc.b "dos.library"
    dc.b $00
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 41 : aga palette bank init --------
Entry_41:
Aga_Palette_Bank_Init:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l #$00000000,d3                              ; +$0008 : 263C00000000
    tst.l d5                                          ; +$000E : 4A85
    beq.w L_0046EE                                    ; +$0010 : 6700011E
    cmpi.l #$00000100,d5                              ; +$0014 : 0C8500000100
    bhi.w L_0046EE                                    ; +$001A : 62000114
    move.l d4,d0                                      ; +$001E : 2004
    cmpi.l #$00000018,d0                              ; +$0020 : 0C8000000018
    bls.w L_0046EE                                    ; +$0026 : 63000108
    andi.l #$00000001,d0                              ; +$002A : 028000000001
    bne.w L_0046EE                                    ; +$0030 : 660000FE
    move.l d5,d6                                      ; +$0034 : 2C05
    mulu.w #$0308,d6                                  ; +$0036 : CCFC0308
    addi.l #$00000010,d6                              ; +$003A : 068600000010
    move.l d4,d0                                      ; +$0040 : 2004
    subi.l #$00000018,d0                              ; +$0042 : 048000000018
    movea.l d0,a1                                     ; +$0048 : 2240
    movea.l $0004.w,a6                                ; +$004A : 2C780004
    jsr -534(a6)                                      ; +$004E : 4EAEFDEA
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0046EE                                    ; +$0054 : 670000DA
    move.l d4,d0                                      ; +$0058 : 2004
    add.l d6,d0                                       ; +$005A : D086
    bcs.w L_0046EE                                    ; +$005C : 650000D2
    subq.l #1,d0                                      ; +$0060 : 5380
    movea.l d0,a1                                     ; +$0062 : 2240
    jsr -534(a6)                                      ; +$0064 : 4EAEFDEA
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_0046EE                                    ; +$006A : 670000C4
    movea.l d4,a0                                     ; +$006E : 2044
    move.l -20(a0),d0                                 ; +$0070 : 2028FFEC
    move.l d6,d7                                      ; +$0074 : 2E06
    addi.l #$00000010,d7                              ; +$0076 : 068700000010
    cmp.l d7,d0                                       ; +$007C : B087
    bne.w L_0046EE                                    ; +$007E : 660000B0
    move.l #$00000000,d0                              ; +$0082 : 203C00000000
    move.w -12(a0),d0                                 ; +$0088 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$008C : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$0090 : 0C8000000001
    bne.w L_0046EE                                    ; +$0096 : 66000098
    move.l -16(a0),d0                                 ; +$009A : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$009E : 0C8000000005
    bcs.w L_0046EE                                    ; +$00A4 : 6500008A
    cmpi.l #$0000FFFF,d0                              ; +$00A8 : 0C800000FFFF
    bhi.w L_0046EE                                    ; +$00AE : 62000080
    move.l #$41474150,-8(a0)                          ; +$00B2 : 217C41474150FFF8
    move.l #$414C2020,-4(a0)                          ; +$00BA : 217C414C2020FFFC
    move.l #$41474150,(a0)                            ; +$00C2 : 20BC41474150
    move.w #$414C,4(a0)                               ; +$00C8 : 317C414C0004
    move.w #$0001,6(a0)                               ; +$00CE : 317C00010006
    move.w d5,8(a0)                                   ; +$00D4 : 31450008
    move.w #$0000,10(a0)                              ; +$00D8 : 317C0000000A
    move.l #$00000000,12(a0)                          ; +$00DE : 217C00000000000C
    move.l d5,d7                                      ; +$00E6 : 2E05
    lsl.l #3,d7                                       ; +$00E8 : E78F
    addi.l #$00000010,d7                              ; +$00EA : 068700000010
    move.l d4,d0                                      ; +$00F0 : 2004
    addi.l #$00000010,d0                              ; +$00F2 : 068000000010
    movea.l d0,a1                                     ; +$00F8 : 2240
L_0046B8:
    move.l d7,(a1)+                                   ; +$00FA : 22C7
    move.w #$0000,(a1)+                               ; +$00FC : 32FC0000
    move.w #$0000,(a1)+                               ; +$0100 : 32FC0000
    addi.l #$00000300,d7                              ; +$0104 : 068700000300
    subq.l #1,d5                                      ; +$010A : 5385
    bne.w L_0046B8                                    ; +$010C : 6600FFEC
    move.l #$00000000,d5                              ; +$0110 : 2A3C00000000
    move.w 8(a0),d5                                   ; +$0116 : 3A280008
    mulu.w #$00C0,d5                                  ; +$011A : CAFC00C0
L_0046DC:
    move.l #$00000000,(a1)+                           ; +$011E : 22FC00000000
    subq.l #1,d5                                      ; +$0124 : 5385
    bne.w L_0046DC                                    ; +$0126 : 6600FFF6
    move.l #$00000001,d3                              ; +$012A : 263C00000001
L_0046EE:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0130 : 4CDF77F7
    moveq #0,d2                                       ; +$0134 : 7400
    rts                                               ; +$0136 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 42 : aga palette bank capture --------
Entry_42:
Aga_Palette_Bank_Capture:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l #$00000000,d3                              ; +$0008 : 263C00000000
    cmpi.l #$000000FF,d5                              ; +$000E : 0C85000000FF
    bhi.w L_004982                                    ; +$0014 : 62000272
    move.l d4,d0                                      ; +$0018 : 2004
    cmpi.l #$00000018,d0                              ; +$001A : 0C8000000018
    bls.w L_004982                                    ; +$0020 : 63000266
    andi.l #$00000001,d0                              ; +$0024 : 028000000001
    bne.w L_004982                                    ; +$002A : 6600025C
    move.l d4,d0                                      ; +$002E : 2004
    subi.l #$00000018,d0                              ; +$0030 : 048000000018
    movea.l d0,a1                                     ; +$0036 : 2240
    movea.l $0004.w,a6                                ; +$0038 : 2C780004
    jsr -534(a6)                                      ; +$003C : 4EAEFDEA
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_004982                                    ; +$0042 : 67000244
    movea.l d4,a0                                     ; +$0046 : 2044
    move.l #$00000000,d6                              ; +$0048 : 2C3C00000000
    move.w 8(a0),d6                                   ; +$004E : 3C280008
    tst.l d6                                          ; +$0052 : 4A86
    beq.w L_004982                                    ; +$0054 : 67000232
    cmpi.l #$00000100,d6                              ; +$0058 : 0C8600000100
    bhi.w L_004982                                    ; +$005E : 62000228
    cmp.l d6,d5                                       ; +$0062 : BA86
    bcc.w L_004982                                    ; +$0064 : 64000222
    move.l d6,d7                                      ; +$0068 : 2E06
    mulu.w #$0308,d7                                  ; +$006A : CEFC0308
    addi.l #$00000010,d7                              ; +$006E : 068700000010
    move.l d4,d0                                      ; +$0074 : 2004
    add.l d7,d0                                       ; +$0076 : D087
    bcs.w L_004982                                    ; +$0078 : 6500020E
    subq.l #1,d0                                      ; +$007C : 5380
    movea.l d0,a1                                     ; +$007E : 2240
    jsr -534(a6)                                      ; +$0080 : 4EAEFDEA
    tst.l d0                                          ; +$0084 : 4A80
    beq.w L_004982                                    ; +$0086 : 67000200
    movea.l d4,a0                                     ; +$008A : 2044
    move.l -20(a0),d0                                 ; +$008C : 2028FFEC
    move.l d7,d1                                      ; +$0090 : 2207
    addi.l #$00000010,d1                              ; +$0092 : 068100000010
    cmp.l d1,d0                                       ; +$0098 : B081
    bne.w L_004982                                    ; +$009A : 660001EC
    move.l #$00000000,d0                              ; +$009E : 203C00000000
    move.w -12(a0),d0                                 ; +$00A4 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00A8 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00AC : 0C8000000001
    bne.w L_004982                                    ; +$00B2 : 660001D4
    move.l -16(a0),d0                                 ; +$00B6 : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00BA : 0C8000000005
    bcs.w L_004982                                    ; +$00C0 : 650001C6
    cmpi.l #$0000FFFF,d0                              ; +$00C4 : 0C800000FFFF
    bhi.w L_004982                                    ; +$00CA : 620001BC
    move.l -8(a0),d0                                  ; +$00CE : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00D2 : 0C8041474150
    bne.w L_004982                                    ; +$00D8 : 660001AE
    move.l -4(a0),d0                                  ; +$00DC : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00E0 : 0C80414C2020
    bne.w L_004982                                    ; +$00E6 : 660001A0
    move.l (a0),d0                                    ; +$00EA : 2010
    cmpi.l #$41474150,d0                              ; +$00EC : 0C8041474150
    bne.w L_004982                                    ; +$00F2 : 66000194
    move.l #$00000000,d0                              ; +$00F6 : 203C00000000
    move.w 4(a0),d0                                   ; +$00FC : 30280004
    cmpi.l #$0000414C,d0                              ; +$0100 : 0C800000414C
    bne.w L_004982                                    ; +$0106 : 66000180
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 6(a0),d0                                   ; +$0110 : 30280006
    cmpi.l #$00000001,d0                              ; +$0114 : 0C8000000001
    bne.w L_004982                                    ; +$011A : 6600016C
    move.w 10(a0),d0                                  ; +$011E : 3028000A
    tst.w d0                                          ; +$0122 : 4A40
    bne.w L_004982                                    ; +$0124 : 66000162
    tst.l 12(a0)                                      ; +$0128 : 4AA8000C
    bne.w L_004982                                    ; +$012C : 6600015A
    move.l d5,d1                                      ; +$0130 : 2205
    lsl.l #3,d1                                       ; +$0132 : E789
    addi.l #$00000010,d1                              ; +$0134 : 068100000010
    add.l d4,d1                                       ; +$013A : D284
    movea.l d1,a1                                     ; +$013C : 2241
    move.l d6,d0                                      ; +$013E : 2006
    lsl.l #3,d0                                       ; +$0140 : E788
    addi.l #$00000010,d0                              ; +$0142 : 068000000010
    move.l d5,d1                                      ; +$0148 : 2205
    mulu.w #$0300,d1                                  ; +$014A : C2FC0300
    add.l d1,d0                                       ; +$014E : D081
    cmp.l (a1),d0                                     ; +$0150 : B091
    bne.w L_004982                                    ; +$0152 : 66000134
    move.l #$00000000,d0                              ; +$0156 : 203C00000000
    move.w 4(a1),d0                                   ; +$015C : 30290004
    cmpi.l #$00000100,d0                              ; +$0160 : 0C8000000100
    bhi.w L_004982                                    ; +$0166 : 62000120
    tst.w 6(a1)                                       ; +$016A : 4A690006
    bne.w L_004982                                    ; +$016E : 66000118
    movea.l 456(a5),a0                                ; +$0172 : 206D01C8
    move.l a0,d0                                      ; +$0176 : 2008
    tst.l d0                                          ; +$0178 : 4A80
    beq.w L_004982                                    ; +$017A : 6700010C
    movea.l (a0),a1                                   ; +$017E : 2250
    move.l a1,d0                                      ; +$0180 : 2009
    tst.l d0                                          ; +$0182 : 4A80
    beq.w L_004982                                    ; +$0184 : 67000102
    tst.l 8(a0)                                       ; +$0188 : 4AA80008
    beq.w L_004982                                    ; +$018C : 670000FA
    move.l 28(a0),d0                                  ; +$0190 : 2028001C
    tst.l d0                                          ; +$0194 : 4A80
    ble.w L_004982                                    ; +$0196 : 6F0000F0
    cmpi.l #$00000008,d0                              ; +$019A : 0C8000000008
    bhi.w L_004982                                    ; +$01A0 : 620000E6
    move.l 24(a0),d0                                  ; +$01A4 : 20280018
    andi.l #$00000C80,d0                              ; +$01A8 : 028000000C80
    bne.w L_004982                                    ; +$01AE : 660000D8
    move.l 20(a0),d7                                  ; +$01B2 : 2E280014
    tst.l d7                                          ; +$01B6 : 4A87
    beq.w L_004982                                    ; +$01B8 : 670000CE
    cmpi.l #$00000100,d7                              ; +$01BC : 0C8700000100
    bhi.w L_004982                                    ; +$01C2 : 620000C4
    movea.l 48(a1),a2                                 ; +$01C6 : 24690030
    move.l a2,d0                                      ; +$01CA : 200A
    tst.l d0                                          ; +$01CC : 4A80
    beq.w L_004982                                    ; +$01CE : 670000B8
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    move.w 2(a2),d0                                   ; +$01D8 : 302A0002
    tst.l d0                                          ; +$01DC : 4A80
    beq.w L_004982                                    ; +$01DE : 670000A8
    cmpi.l #$00000100,d0                              ; +$01E2 : 0C8000000100
    bhi.w L_004982                                    ; +$01E8 : 6200009E
    cmp.l d0,d7                                       ; +$01EC : BE80
    bls.w L_0048EE                                    ; +$01EE : 63000004
    move.l d0,d7                                      ; +$01F2 : 2E00
L_0048EE:
    move.l d7,d0                                      ; +$01F4 : 2007
    mulu.w #$000C,d0                                  ; +$01F6 : C0FC000C
    move.l #$00000001,d1                              ; +$01FA : 223C00000001
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -684(a6)                                      ; +$0204 : 4EAEFD54
    tst.l d0                                          ; +$0208 : 4A80
    beq.w L_004982                                    ; +$020A : 6700007C
    movea.l d0,a4                                     ; +$020E : 2840
    movea.l a2,a0                                     ; +$0210 : 204A
    movea.l a4,a1                                     ; +$0212 : 224C
    move.l #$00000000,d0                              ; +$0214 : 203C00000000
    move.l d7,d1                                      ; +$021A : 2207
    movea.l 456(a5),a6                                ; +$021C : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$0220 : 2C6E0008
    jsr -900(a6)                                      ; +$0224 : 4EAEFC7C
    move.l d6,d0                                      ; +$0228 : 2006
    lsl.l #3,d0                                       ; +$022A : E788
    addi.l #$00000010,d0                              ; +$022C : 068000000010
    move.l d5,d1                                      ; +$0232 : 2205
    mulu.w #$0300,d1                                  ; +$0234 : C2FC0300
    add.l d1,d0                                       ; +$0238 : D081
    add.l d4,d0                                       ; +$023A : D084
    movea.l d0,a1                                     ; +$023C : 2240
    move.l #$000000C0,d6                              ; +$023E : 2C3C000000C0
L_00493E:
    move.l #$00000000,(a1)+                           ; +$0244 : 22FC00000000
    subq.l #1,d6                                      ; +$024A : 5386
    bne.w L_00493E                                    ; +$024C : 6600FFF6
    movea.l d0,a1                                     ; +$0250 : 2240
    movea.l a4,a2                                     ; +$0252 : 244C
    move.l d7,d6                                      ; +$0254 : 2C07
L_004950:
    move.b (a2),(a1)+                                 ; +$0256 : 12D2
    addq.l #4,a2                                      ; +$0258 : 588A
    move.b (a2),(a1)+                                 ; +$025A : 12D2
    addq.l #4,a2                                      ; +$025C : 588A
    move.b (a2),(a1)+                                 ; +$025E : 12D2
    addq.l #4,a2                                      ; +$0260 : 588A
    subq.l #1,d6                                      ; +$0262 : 5386
    bne.w L_004950                                    ; +$0264 : 6600FFF0
    move.l d5,d0                                      ; +$0268 : 2005
    lsl.l #3,d0                                       ; +$026A : E788
    addi.l #$00000014,d0                              ; +$026C : 068000000014
    add.l d4,d0                                       ; +$0272 : D084
    movea.l d0,a0                                     ; +$0274 : 2040
    move.w d7,(a0)                                    ; +$0276 : 3087
    movea.l a4,a1                                     ; +$0278 : 224C
    movea.l $0004.w,a6                                ; +$027A : 2C780004
    jsr -690(a6)                                      ; +$027E : 4EAEFD4E
    move.l #$00000001,d3                              ; +$0282 : 263C00000001
L_004982:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0288 : 4CDF77F7
    moveq #0,d2                                       ; +$028C : 7400
    rts                                               ; +$028E : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 43 : aga palette bank apply --------
Entry_43:
Aga_Palette_Bank_Apply:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d5                                      ; +$0004 : 2A03
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l #$00000000,d3                              ; +$0008 : 263C00000000
    cmpi.l #$000000FF,d5                              ; +$000E : 0C85000000FF
    bhi.w L_004C36                                    ; +$0014 : 62000292
    move.l d4,d0                                      ; +$0018 : 2004
    cmpi.l #$00000018,d0                              ; +$001A : 0C8000000018
    bls.w L_004C36                                    ; +$0020 : 63000286
    andi.l #$00000001,d0                              ; +$0024 : 028000000001
    bne.w L_004C36                                    ; +$002A : 6600027C
    move.l d4,d0                                      ; +$002E : 2004
    subi.l #$00000018,d0                              ; +$0030 : 048000000018
    movea.l d0,a1                                     ; +$0036 : 2240
    movea.l $0004.w,a6                                ; +$0038 : 2C780004
    jsr -534(a6)                                      ; +$003C : 4EAEFDEA
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_004C36                                    ; +$0042 : 67000264
    movea.l d4,a0                                     ; +$0046 : 2044
    move.l #$00000000,d6                              ; +$0048 : 2C3C00000000
    move.w 8(a0),d6                                   ; +$004E : 3C280008
    tst.l d6                                          ; +$0052 : 4A86
    beq.w L_004C36                                    ; +$0054 : 67000252
    cmpi.l #$00000100,d6                              ; +$0058 : 0C8600000100
    bhi.w L_004C36                                    ; +$005E : 62000248
    cmp.l d6,d5                                       ; +$0062 : BA86
    bcc.w L_004C36                                    ; +$0064 : 64000242
    move.l d6,d7                                      ; +$0068 : 2E06
    mulu.w #$0308,d7                                  ; +$006A : CEFC0308
    addi.l #$00000010,d7                              ; +$006E : 068700000010
    move.l d4,d0                                      ; +$0074 : 2004
    add.l d7,d0                                       ; +$0076 : D087
    bcs.w L_004C36                                    ; +$0078 : 6500022E
    subq.l #1,d0                                      ; +$007C : 5380
    movea.l d0,a1                                     ; +$007E : 2240
    jsr -534(a6)                                      ; +$0080 : 4EAEFDEA
    tst.l d0                                          ; +$0084 : 4A80
    beq.w L_004C36                                    ; +$0086 : 67000220
    movea.l d4,a0                                     ; +$008A : 2044
    move.l -20(a0),d0                                 ; +$008C : 2028FFEC
    move.l d7,d1                                      ; +$0090 : 2207
    addi.l #$00000010,d1                              ; +$0092 : 068100000010
    cmp.l d1,d0                                       ; +$0098 : B081
    bne.w L_004C36                                    ; +$009A : 6600020C
    move.l #$00000000,d0                              ; +$009E : 203C00000000
    move.w -12(a0),d0                                 ; +$00A4 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00A8 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00AC : 0C8000000001
    bne.w L_004C36                                    ; +$00B2 : 660001F4
    move.l -16(a0),d0                                 ; +$00B6 : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00BA : 0C8000000005
    bcs.w L_004C36                                    ; +$00C0 : 650001E6
    cmpi.l #$0000FFFF,d0                              ; +$00C4 : 0C800000FFFF
    bhi.w L_004C36                                    ; +$00CA : 620001DC
    move.l -8(a0),d0                                  ; +$00CE : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00D2 : 0C8041474150
    bne.w L_004C36                                    ; +$00D8 : 660001CE
    move.l -4(a0),d0                                  ; +$00DC : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00E0 : 0C80414C2020
    bne.w L_004C36                                    ; +$00E6 : 660001C0
    move.l (a0),d0                                    ; +$00EA : 2010
    cmpi.l #$41474150,d0                              ; +$00EC : 0C8041474150
    bne.w L_004C36                                    ; +$00F2 : 660001B4
    move.l #$00000000,d0                              ; +$00F6 : 203C00000000
    move.w 4(a0),d0                                   ; +$00FC : 30280004
    cmpi.l #$0000414C,d0                              ; +$0100 : 0C800000414C
    bne.w L_004C36                                    ; +$0106 : 660001A0
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 6(a0),d0                                   ; +$0110 : 30280006
    cmpi.l #$00000001,d0                              ; +$0114 : 0C8000000001
    bne.w L_004C36                                    ; +$011A : 6600018C
    tst.w 10(a0)                                      ; +$011E : 4A68000A
    bne.w L_004C36                                    ; +$0122 : 66000184
    tst.l 12(a0)                                      ; +$0126 : 4AA8000C
    bne.w L_004C36                                    ; +$012A : 6600017C
    move.l d5,d1                                      ; +$012E : 2205
    lsl.l #3,d1                                       ; +$0130 : E789
    addi.l #$00000010,d1                              ; +$0132 : 068100000010
    add.l d4,d1                                       ; +$0138 : D284
    movea.l d1,a1                                     ; +$013A : 2241
    move.l d6,d0                                      ; +$013C : 2006
    lsl.l #3,d0                                       ; +$013E : E788
    addi.l #$00000010,d0                              ; +$0140 : 068000000010
    move.l d5,d1                                      ; +$0146 : 2205
    mulu.w #$0300,d1                                  ; +$0148 : C2FC0300
    add.l d1,d0                                       ; +$014C : D081
    cmp.l (a1),d0                                     ; +$014E : B091
    bne.w L_004C36                                    ; +$0150 : 66000156
    move.l #$00000000,d7                              ; +$0154 : 2E3C00000000
    move.w 4(a1),d7                                   ; +$015A : 3E290004
    tst.l d7                                          ; +$015E : 4A87
    beq.w L_004C36                                    ; +$0160 : 67000146
    cmpi.l #$00000100,d7                              ; +$0164 : 0C8700000100
    bhi.w L_004C36                                    ; +$016A : 6200013C
    tst.w 6(a1)                                       ; +$016E : 4A690006
    bne.w L_004C36                                    ; +$0172 : 66000134
    add.l d4,d0                                       ; +$0176 : D084
    movea.l d0,a2                                     ; +$0178 : 2440
    movea.l 456(a5),a0                                ; +$017A : 206D01C8
    move.l a0,d0                                      ; +$017E : 2008
    tst.l d0                                          ; +$0180 : 4A80
    beq.w L_004C36                                    ; +$0182 : 67000124
    movea.l (a0),a1                                   ; +$0186 : 2250
    move.l a1,d0                                      ; +$0188 : 2009
    tst.l d0                                          ; +$018A : 4A80
    beq.w L_004C36                                    ; +$018C : 6700011A
    tst.l 8(a0)                                       ; +$0190 : 4AA80008
    beq.w L_004C36                                    ; +$0194 : 67000112
    move.l 28(a0),d0                                  ; +$0198 : 2028001C
    tst.l d0                                          ; +$019C : 4A80
    ble.w L_004C36                                    ; +$019E : 6F000108
    cmpi.l #$00000008,d0                              ; +$01A2 : 0C8000000008
    bhi.w L_004C36                                    ; +$01A8 : 620000FE
    move.l 24(a0),d0                                  ; +$01AC : 20280018
    andi.l #$00000C80,d0                              ; +$01B0 : 028000000C80
    bne.w L_004C36                                    ; +$01B6 : 660000F0
    move.l 20(a0),d0                                  ; +$01BA : 20280014
    tst.l d0                                          ; +$01BE : 4A80
    beq.w L_004C36                                    ; +$01C0 : 670000E6
    cmpi.l #$00000100,d0                              ; +$01C4 : 0C8000000100
    bhi.w L_004C36                                    ; +$01CA : 620000DC
    cmp.l d0,d7                                       ; +$01CE : BE80
    bhi.w L_004C36                                    ; +$01D0 : 620000D6
    movea.l 48(a1),a1                                 ; +$01D4 : 22690030
    move.l a1,d0                                      ; +$01D8 : 2009
    tst.l d0                                          ; +$01DA : 4A80
    beq.w L_004C36                                    ; +$01DC : 670000CA
    move.l #$00000000,d0                              ; +$01E0 : 203C00000000
    move.w 2(a1),d0                                   ; +$01E6 : 30290002
    tst.l d0                                          ; +$01EA : 4A80
    beq.w L_004C36                                    ; +$01EC : 670000BA
    cmpi.l #$00000100,d0                              ; +$01F0 : 0C8000000100
    bhi.w L_004C36                                    ; +$01F6 : 620000B0
    cmp.l d0,d7                                       ; +$01FA : BE80
    bhi.w L_004C36                                    ; +$01FC : 620000AA
    move.l d7,d0                                      ; +$0200 : 2007
    mulu.w #$000C,d0                                  ; +$0202 : C0FC000C
    addi.l #$00000008,d0                              ; +$0206 : 068000000008
    move.l #$00000001,d1                              ; +$020C : 223C00000001
    movea.l $0004.w,a6                                ; +$0212 : 2C780004
    jsr -684(a6)                                      ; +$0216 : 4EAEFD54
    tst.l d0                                          ; +$021A : 4A80
    beq.w L_004C36                                    ; +$021C : 6700008A
    movea.l d0,a4                                     ; +$0220 : 2840
    movea.l a4,a1                                     ; +$0222 : 224C
    move.l d7,d0                                      ; +$0224 : 2007
    swap d0                                           ; +$0226 : 4840
    move.l d0,(a1)+                                   ; +$0228 : 22C0
    move.l d7,d6                                      ; +$022A : 2C07
L_004BBA:
    move.l #$00000000,d0                              ; +$022C : 203C00000000
    move.b (a2)+,d0                                   ; +$0232 : 101A
    move.l d0,d1                                      ; +$0234 : 2200
    lsl.l #8,d0                                       ; +$0236 : E188
    or.l d1,d0                                        ; +$0238 : 8081
    move.l d0,d1                                      ; +$023A : 2200
    swap d0                                           ; +$023C : 4840
    or.l d1,d0                                        ; +$023E : 8081
    move.l d0,(a1)+                                   ; +$0240 : 22C0
    move.l #$00000000,d0                              ; +$0242 : 203C00000000
    move.b (a2)+,d0                                   ; +$0248 : 101A
    move.l d0,d1                                      ; +$024A : 2200
    lsl.l #8,d0                                       ; +$024C : E188
    or.l d1,d0                                        ; +$024E : 8081
    move.l d0,d1                                      ; +$0250 : 2200
    swap d0                                           ; +$0252 : 4840
    or.l d1,d0                                        ; +$0254 : 8081
    move.l d0,(a1)+                                   ; +$0256 : 22C0
    move.l #$00000000,d0                              ; +$0258 : 203C00000000
    move.b (a2)+,d0                                   ; +$025E : 101A
    move.l d0,d1                                      ; +$0260 : 2200
    lsl.l #8,d0                                       ; +$0262 : E188
    or.l d1,d0                                        ; +$0264 : 8081
    move.l d0,d1                                      ; +$0266 : 2200
    swap d0                                           ; +$0268 : 4840
    or.l d1,d0                                        ; +$026A : 8081
    move.l d0,(a1)+                                   ; +$026C : 22C0
    subq.l #1,d6                                      ; +$026E : 5386
    bne.w L_004BBA                                    ; +$0270 : 6600FFBA
    move.l #$00000000,(a1)                            ; +$0274 : 22BC00000000
    movea.l 456(a5),a0                                ; +$027A : 206D01C8
    movea.l (a0),a0                                   ; +$027E : 2050
    move.l a0,d0                                      ; +$0280 : 2008
    addi.l #$0000002C,d0                              ; +$0282 : 06800000002C
    movea.l d0,a0                                     ; +$0288 : 2040
    movea.l a4,a1                                     ; +$028A : 224C
    movea.l 456(a5),a6                                ; +$028C : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$0290 : 2C6E0008
    jsr -882(a6)                                      ; +$0294 : 4EAEFC8E
    movea.l a4,a1                                     ; +$0298 : 224C
    movea.l $0004.w,a6                                ; +$029A : 2C780004
    jsr -690(a6)                                      ; +$029E : 4EAEFD4E
    move.l #$00000001,d3                              ; +$02A2 : 263C00000001
L_004C36:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$02A8 : 4CDF77F7
    moveq #0,d2                                       ; +$02AC : 7400
    rts                                               ; +$02AE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 44 : aga fade to bank --------
Entry_44:
Aga_Fade_To_Bank:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,-(a7)                                   ; +$0004 : 2F03
    move.l (a3)+,d5                                   ; +$0006 : 2A1B
    move.l (a3)+,d4                                   ; +$0008 : 281B
    move.l #$00000000,d3                              ; +$000A : 263C00000000
    move.l (a7),d0                                    ; +$0010 : 2017
    tst.l d0                                          ; +$0012 : 4A80
    beq.w L_004FD6                                    ; +$0014 : 6700037E
    cmpi.l #$000000FF,d0                              ; +$0018 : 0C80000000FF
    bhi.w L_004FD6                                    ; +$001E : 62000374
    cmpi.l #$000000FF,d5                              ; +$0022 : 0C85000000FF
    bhi.w L_004FD6                                    ; +$0028 : 6200036A
    move.l d4,d0                                      ; +$002C : 2004
    cmpi.l #$00000018,d0                              ; +$002E : 0C8000000018
    bls.w L_004FD6                                    ; +$0034 : 6300035E
    andi.l #$00000001,d0                              ; +$0038 : 028000000001
    bne.w L_004FD6                                    ; +$003E : 66000354
    move.l d4,d0                                      ; +$0042 : 2004
    subi.l #$00000018,d0                              ; +$0044 : 048000000018
    movea.l d0,a1                                     ; +$004A : 2240
    movea.l $0004.w,a6                                ; +$004C : 2C780004
    jsr -534(a6)                                      ; +$0050 : 4EAEFDEA
    tst.l d0                                          ; +$0054 : 4A80
    beq.w L_004FD6                                    ; +$0056 : 6700033C
    movea.l d4,a0                                     ; +$005A : 2044
    move.l #$00000000,d6                              ; +$005C : 2C3C00000000
    move.w 8(a0),d6                                   ; +$0062 : 3C280008
    tst.l d6                                          ; +$0066 : 4A86
    beq.w L_004FD6                                    ; +$0068 : 6700032A
    cmpi.l #$00000100,d6                              ; +$006C : 0C8600000100
    bhi.w L_004FD6                                    ; +$0072 : 62000320
    cmp.l d6,d5                                       ; +$0076 : BA86
    bcc.w L_004FD6                                    ; +$0078 : 6400031A
    move.l d6,d7                                      ; +$007C : 2E06
    mulu.w #$0308,d7                                  ; +$007E : CEFC0308
    addi.l #$00000010,d7                              ; +$0082 : 068700000010
    move.l d4,d0                                      ; +$0088 : 2004
    add.l d7,d0                                       ; +$008A : D087
    bcs.w L_004FD6                                    ; +$008C : 65000306
    subq.l #1,d0                                      ; +$0090 : 5380
    movea.l d0,a1                                     ; +$0092 : 2240
    jsr -534(a6)                                      ; +$0094 : 4EAEFDEA
    tst.l d0                                          ; +$0098 : 4A80
    beq.w L_004FD6                                    ; +$009A : 670002F8
    movea.l d4,a0                                     ; +$009E : 2044
    move.l -20(a0),d0                                 ; +$00A0 : 2028FFEC
    move.l d7,d1                                      ; +$00A4 : 2207
    addi.l #$00000010,d1                              ; +$00A6 : 068100000010
    cmp.l d1,d0                                       ; +$00AC : B081
    bne.w L_004FD6                                    ; +$00AE : 660002E4
    move.l #$00000000,d0                              ; +$00B2 : 203C00000000
    move.w -12(a0),d0                                 ; +$00B8 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00BC : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00C0 : 0C8000000001
    bne.w L_004FD6                                    ; +$00C6 : 660002CC
    move.l -16(a0),d0                                 ; +$00CA : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00CE : 0C8000000005
    bcs.w L_004FD6                                    ; +$00D4 : 650002BE
    cmpi.l #$0000FFFF,d0                              ; +$00D8 : 0C800000FFFF
    bhi.w L_004FD6                                    ; +$00DE : 620002B4
    move.l -8(a0),d0                                  ; +$00E2 : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00E6 : 0C8041474150
    bne.w L_004FD6                                    ; +$00EC : 660002A6
    move.l -4(a0),d0                                  ; +$00F0 : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00F4 : 0C80414C2020
    bne.w L_004FD6                                    ; +$00FA : 66000298
    move.l (a0),d0                                    ; +$00FE : 2010
    cmpi.l #$41474150,d0                              ; +$0100 : 0C8041474150
    bne.w L_004FD6                                    ; +$0106 : 6600028C
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 4(a0),d0                                   ; +$0110 : 30280004
    cmpi.l #$0000414C,d0                              ; +$0114 : 0C800000414C
    bne.w L_004FD6                                    ; +$011A : 66000278
    move.l #$00000000,d0                              ; +$011E : 203C00000000
    move.w 6(a0),d0                                   ; +$0124 : 30280006
    cmpi.l #$00000001,d0                              ; +$0128 : 0C8000000001
    bne.w L_004FD6                                    ; +$012E : 66000264
    tst.w 10(a0)                                      ; +$0132 : 4A68000A
    bne.w L_004FD6                                    ; +$0136 : 6600025C
    tst.l 12(a0)                                      ; +$013A : 4AA8000C
    bne.w L_004FD6                                    ; +$013E : 66000254
    move.l d5,d1                                      ; +$0142 : 2205
    lsl.l #3,d1                                       ; +$0144 : E789
    addi.l #$00000010,d1                              ; +$0146 : 068100000010
    add.l d4,d1                                       ; +$014C : D284
    movea.l d1,a1                                     ; +$014E : 2241
    move.l d6,d0                                      ; +$0150 : 2006
    lsl.l #3,d0                                       ; +$0152 : E788
    addi.l #$00000010,d0                              ; +$0154 : 068000000010
    move.l d5,d1                                      ; +$015A : 2205
    mulu.w #$0300,d1                                  ; +$015C : C2FC0300
    add.l d1,d0                                       ; +$0160 : D081
    cmp.l (a1),d0                                     ; +$0162 : B091
    bne.w L_004FD6                                    ; +$0164 : 6600022E
    move.l #$00000000,d7                              ; +$0168 : 2E3C00000000
    move.w 4(a1),d7                                   ; +$016E : 3E290004
    tst.l d7                                          ; +$0172 : 4A87
    beq.w L_004FD6                                    ; +$0174 : 6700021E
    cmpi.l #$00000100,d7                              ; +$0178 : 0C8700000100
    bhi.w L_004FD6                                    ; +$017E : 62000214
    tst.w 6(a1)                                       ; +$0182 : 4A690006
    bne.w L_004FD6                                    ; +$0186 : 6600020C
    add.l d4,d0                                       ; +$018A : D084
    movea.l d0,a2                                     ; +$018C : 2440
    movea.l 456(a5),a0                                ; +$018E : 206D01C8
    move.l a0,d0                                      ; +$0192 : 2008
    tst.l d0                                          ; +$0194 : 4A80
    beq.w L_004FD6                                    ; +$0196 : 670001FC
    movea.l (a0),a1                                   ; +$019A : 2250
    move.l a1,d0                                      ; +$019C : 2009
    tst.l d0                                          ; +$019E : 4A80
    beq.w L_004FD6                                    ; +$01A0 : 670001F2
    tst.l 8(a0)                                       ; +$01A4 : 4AA80008
    beq.w L_004FD6                                    ; +$01A8 : 670001EA
    move.l 28(a0),d0                                  ; +$01AC : 2028001C
    tst.l d0                                          ; +$01B0 : 4A80
    ble.w L_004FD6                                    ; +$01B2 : 6F0001E0
    cmpi.l #$00000008,d0                              ; +$01B6 : 0C8000000008
    bhi.w L_004FD6                                    ; +$01BC : 620001D6
    move.l 24(a0),d0                                  ; +$01C0 : 20280018
    andi.l #$00000C80,d0                              ; +$01C4 : 028000000C80
    bne.w L_004FD6                                    ; +$01CA : 660001C8
    move.l 20(a0),d0                                  ; +$01CE : 20280014
    tst.l d0                                          ; +$01D2 : 4A80
    beq.w L_004FD6                                    ; +$01D4 : 670001BE
    cmpi.l #$00000100,d0                              ; +$01D8 : 0C8000000100
    bhi.w L_004FD6                                    ; +$01DE : 620001B4
    cmp.l d0,d7                                       ; +$01E2 : BE80
    bhi.w L_004FD6                                    ; +$01E4 : 620001AE
    movea.l 48(a1),a1                                 ; +$01E8 : 22690030
    move.l a1,d0                                      ; +$01EC : 2009
    tst.l d0                                          ; +$01EE : 4A80
    beq.w L_004FD6                                    ; +$01F0 : 670001A2
    move.l #$00000000,d0                              ; +$01F4 : 203C00000000
    move.w 2(a1),d0                                   ; +$01FA : 30290002
    tst.l d0                                          ; +$01FE : 4A80
    beq.w L_004FD6                                    ; +$0200 : 67000192
    cmpi.l #$00000100,d0                              ; +$0204 : 0C8000000100
    bhi.w L_004FD6                                    ; +$020A : 62000188
    cmp.l d0,d7                                       ; +$020E : BE80
    bhi.w L_004FD6                                    ; +$0210 : 62000182
    move.l (a7),d6                                    ; +$0214 : 2C17
    move.l d7,d0                                      ; +$0216 : 2007
    mulu.w #$002A,d0                                  ; +$0218 : C0FC002A
    addi.l #$00000008,d0                              ; +$021C : 068000000008
    move.l #$00000001,d1                              ; +$0222 : 223C00000001
    movea.l $0004.w,a6                                ; +$0228 : 2C780004
    jsr -684(a6)                                      ; +$022C : 4EAEFD54
    tst.l d0                                          ; +$0230 : 4A80
    beq.w L_004FD6                                    ; +$0232 : 67000160
    movea.l d0,a4                                     ; +$0236 : 2840
    cmpi.l #$00000001,d6                              ; +$0238 : 0C8600000001
    beq.w L_004F0E                                    ; +$023E : 6700008C
    move.l d7,d0                                      ; +$0242 : 2007
    mulu.w #$000C,d0                                  ; +$0244 : C0FC000C
    addi.l #$00000008,d0                              ; +$0248 : 068000000008
    move.l a4,d1                                      ; +$024E : 220C
    add.l d1,d0                                       ; +$0250 : D081
    movea.l d0,a1                                     ; +$0252 : 2240
    movea.l 456(a5),a0                                ; +$0254 : 206D01C8
    movea.l (a0),a0                                   ; +$0258 : 2050
    movea.l 48(a0),a0                                 ; +$025A : 20680030
    move.l #$00000000,d0                              ; +$025E : 203C00000000
    move.l d7,d1                                      ; +$0264 : 2207
    movea.l 456(a5),a6                                ; +$0266 : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$026A : 2C6E0008
    jsr -900(a6)                                      ; +$026E : 4EAEFC7C
    move.l d7,d0                                      ; +$0272 : 2007
    mulu.w #$000C,d0                                  ; +$0274 : C0FC000C
    addi.l #$00000008,d0                              ; +$0278 : 068000000008
    move.l a4,d1                                      ; +$027E : 220C
    add.l d1,d0                                       ; +$0280 : D081
    movea.l d0,a0                                     ; +$0282 : 2040
    move.l d7,d0                                      ; +$0284 : 2007
    mulu.w #$0018,d0                                  ; +$0286 : C0FC0018
    addi.l #$00000008,d0                              ; +$028A : 068000000008
    move.l a4,d1                                      ; +$0290 : 220C
    add.l d1,d0                                       ; +$0292 : D081
    movea.l d0,a1                                     ; +$0294 : 2240
    move.l d7,d5                                      ; +$0296 : 2A07
    mulu.w #$0003,d5                                  ; +$0298 : CAFC0003
L_004EDE:
    move.l #$00000000,d0                              ; +$029C : 203C00000000
    move.b (a0)+,d0                                   ; +$02A2 : 1018
    addq.l #3,a0                                      ; +$02A4 : 5688
    lsl.l #8,d0                                       ; +$02A6 : E188
    move.l d0,(a1)+                                   ; +$02A8 : 22C0
    move.l #$00000000,d1                              ; +$02AA : 223C00000000
    move.b (a2)+,d1                                   ; +$02B0 : 121A
    lsl.l #8,d1                                       ; +$02B2 : E189
    sub.l d0,d1                                       ; +$02B4 : 9280
    divus.w d6,d1                                     ; +$02B6 : 83C6
    move.w d1,(a1)+                                   ; +$02B8 : 32C1
    subq.l #1,d5                                      ; +$02BA : 5385
    bne.w L_004EDE                                    ; +$02BC : 6600FFDE
    move.l d7,d0                                      ; +$02C0 : 2007
    mulu.w #$0003,d0                                  ; +$02C2 : C0FC0003
    move.l a2,d1                                      ; +$02C6 : 220A
    sub.l d0,d1                                       ; +$02C8 : 9280
    movea.l d1,a2                                     ; +$02CA : 2441
L_004F0E:
    move.l d6,d4                                      ; +$02CC : 2806
L_004F10:
    movea.l 456(a5),a6                                ; +$02CE : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$02D2 : 2C6E0008
    jsr -270(a6)                                      ; +$02D6 : 4EAEFEF2
    movea.l a4,a1                                     ; +$02DA : 224C
    move.l d7,d0                                      ; +$02DC : 2007
    swap d0                                           ; +$02DE : 4840
    move.l d0,(a1)+                                   ; +$02E0 : 22C0
    cmpi.l #$00000001,d4                              ; +$02E2 : 0C8400000001
    beq.w L_004F78                                    ; +$02E8 : 6700004C
    move.l d7,d0                                      ; +$02EC : 2007
    mulu.w #$0018,d0                                  ; +$02EE : C0FC0018
    addi.l #$00000008,d0                              ; +$02F2 : 068000000008
    move.l a4,d1                                      ; +$02F8 : 220C
    add.l d1,d0                                       ; +$02FA : D081
    movea.l d0,a0                                     ; +$02FC : 2040
    move.l d7,d5                                      ; +$02FE : 2A07
    mulu.w #$0003,d5                                  ; +$0300 : CAFC0003
    movea.l a4,a1                                     ; +$0304 : 224C
    addq.l #4,a1                                      ; +$0306 : 5889
L_004F4A:
    move.l (a0),d0                                    ; +$0308 : 2010
    move.l #$00000000,d1                              ; +$030A : 223C00000000
    move.w 4(a0),d1                                   ; +$0310 : 32280004
    ext.l d1                                          ; +$0314 : 48C1
    add.l d1,d0                                       ; +$0316 : D081
    move.l d0,(a0)                                    ; +$0318 : 2080
    addq.l #6,a0                                      ; +$031A : 5C88
    lsr.l #8,d0                                       ; +$031C : E088
    move.l d0,d1                                      ; +$031E : 2200
    lsl.l #8,d0                                       ; +$0320 : E188
    or.l d1,d0                                        ; +$0322 : 8081
    move.l d0,d1                                      ; +$0324 : 2200
    swap d0                                           ; +$0326 : 4840
    or.l d1,d0                                        ; +$0328 : 8081
    move.l d0,(a1)+                                   ; +$032A : 22C0
    subq.l #1,d5                                      ; +$032C : 5385
    bne.w L_004F4A                                    ; +$032E : 6600FFD8
    bra.w L_004F9C                                    ; +$0332 : 60000026
L_004F78:
    movea.l a2,a0                                     ; +$0336 : 204A
    move.l d7,d5                                      ; +$0338 : 2A07
    mulu.w #$0003,d5                                  ; +$033A : CAFC0003
L_004F80:
    move.l #$00000000,d0                              ; +$033E : 203C00000000
    move.b (a0)+,d0                                   ; +$0344 : 1018
    move.l d0,d1                                      ; +$0346 : 2200
    lsl.l #8,d0                                       ; +$0348 : E188
    or.l d1,d0                                        ; +$034A : 8081
    move.l d0,d1                                      ; +$034C : 2200
    swap d0                                           ; +$034E : 4840
    or.l d1,d0                                        ; +$0350 : 8081
    move.l d0,(a1)+                                   ; +$0352 : 22C0
    subq.l #1,d5                                      ; +$0354 : 5385
    bne.w L_004F80                                    ; +$0356 : 6600FFE6
L_004F9C:
    move.l #$00000000,(a1)                            ; +$035A : 22BC00000000
    movea.l 456(a5),a0                                ; +$0360 : 206D01C8
    movea.l (a0),a0                                   ; +$0364 : 2050
    move.l a0,d0                                      ; +$0366 : 2008
    addi.l #$0000002C,d0                              ; +$0368 : 06800000002C
    movea.l d0,a0                                     ; +$036E : 2040
    movea.l a4,a1                                     ; +$0370 : 224C
    movea.l 456(a5),a6                                ; +$0372 : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$0376 : 2C6E0008
    jsr -882(a6)                                      ; +$037A : 4EAEFC8E
    subq.l #1,d4                                      ; +$037E : 5384
    bne.w L_004F10                                    ; +$0380 : 6600FF4C
    movea.l a4,a1                                     ; +$0384 : 224C
    movea.l $0004.w,a6                                ; +$0386 : 2C780004
    jsr -690(a6)                                      ; +$038A : 4EAEFD4E
    move.l #$00000001,d3                              ; +$038E : 263C00000001
L_004FD6:
    addq.l #4,a7                                      ; +$0394 : 588F
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0396 : 4CDF77F7
    moveq #0,d2                                       ; +$039A : 7400
    rts                                               ; +$039C : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 45 : aga fade to black --------
Entry_45:
Aga_Fade_To_Black:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,-(a7)                                   ; +$0004 : 2F03
    move.l #$00000000,d3                              ; +$0006 : 263C00000000
    move.l (a7),d0                                    ; +$000C : 2017
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_0051E2                                    ; +$0010 : 670001EC
    cmpi.l #$000000FF,d0                              ; +$0014 : 0C80000000FF
    bhi.w L_0051E2                                    ; +$001A : 620001E2
    movea.l 456(a5),a0                                ; +$001E : 206D01C8
    move.l a0,d0                                      ; +$0022 : 2008
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0051E2                                    ; +$0026 : 670001D6
    movea.l (a0),a1                                   ; +$002A : 2250
    move.l a1,d0                                      ; +$002C : 2009
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0051E2                                    ; +$0030 : 670001CC
    tst.l 8(a0)                                       ; +$0034 : 4AA80008
    beq.w L_0051E2                                    ; +$0038 : 670001C4
    move.l 28(a0),d0                                  ; +$003C : 2028001C
    tst.l d0                                          ; +$0040 : 4A80
    ble.w L_0051E2                                    ; +$0042 : 6F0001BA
    cmpi.l #$00000008,d0                              ; +$0046 : 0C8000000008
    bhi.w L_0051E2                                    ; +$004C : 620001B0
    move.l 24(a0),d0                                  ; +$0050 : 20280018
    andi.l #$00000C80,d0                              ; +$0054 : 028000000C80
    bne.w L_0051E2                                    ; +$005A : 660001A2
    move.l 20(a0),d7                                  ; +$005E : 2E280014
    tst.l d7                                          ; +$0062 : 4A87
    beq.w L_0051E2                                    ; +$0064 : 67000198
    cmpi.l #$00000100,d7                              ; +$0068 : 0C8700000100
    bhi.w L_0051E2                                    ; +$006E : 6200018E
    movea.l 48(a1),a1                                 ; +$0072 : 22690030
    move.l a1,d0                                      ; +$0076 : 2009
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0051E2                                    ; +$007A : 67000182
    move.l #$00000000,d0                              ; +$007E : 203C00000000
    move.w 2(a1),d0                                   ; +$0084 : 30290002
    tst.l d0                                          ; +$0088 : 4A80
    beq.w L_0051E2                                    ; +$008A : 67000172
    cmpi.l #$00000100,d0                              ; +$008E : 0C8000000100
    bhi.w L_0051E2                                    ; +$0094 : 62000168
    cmp.l d0,d7                                       ; +$0098 : BE80
    bhi.w L_0051E2                                    ; +$009A : 62000162
    move.l (a7),d6                                    ; +$009E : 2C17
    move.l d7,d0                                      ; +$00A0 : 2007
    mulu.w #$002A,d0                                  ; +$00A2 : C0FC002A
    addi.l #$00000008,d0                              ; +$00A6 : 068000000008
    move.l #$00000001,d1                              ; +$00AC : 223C00000001
    movea.l $0004.w,a6                                ; +$00B2 : 2C780004
    jsr -684(a6)                                      ; +$00B6 : 4EAEFD54
    tst.l d0                                          ; +$00BA : 4A80
    beq.w L_0051E2                                    ; +$00BC : 67000140
    movea.l d0,a4                                     ; +$00C0 : 2840
    cmpi.l #$00000001,d6                              ; +$00C2 : 0C8600000001
    beq.w L_00512C                                    ; +$00C8 : 6700007E
    move.l d7,d0                                      ; +$00CC : 2007
    mulu.w #$000C,d0                                  ; +$00CE : C0FC000C
    addi.l #$00000008,d0                              ; +$00D2 : 068000000008
    move.l a4,d1                                      ; +$00D8 : 220C
    add.l d1,d0                                       ; +$00DA : D081
    movea.l d0,a1                                     ; +$00DC : 2240
    movea.l 456(a5),a0                                ; +$00DE : 206D01C8
    movea.l (a0),a0                                   ; +$00E2 : 2050
    movea.l 48(a0),a0                                 ; +$00E4 : 20680030
    move.l #$00000000,d0                              ; +$00E8 : 203C00000000
    move.l d7,d1                                      ; +$00EE : 2207
    movea.l 456(a5),a6                                ; +$00F0 : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$00F4 : 2C6E0008
    jsr -900(a6)                                      ; +$00F8 : 4EAEFC7C
    move.l d7,d0                                      ; +$00FC : 2007
    mulu.w #$000C,d0                                  ; +$00FE : C0FC000C
    addi.l #$00000008,d0                              ; +$0102 : 068000000008
    move.l a4,d1                                      ; +$0108 : 220C
    add.l d1,d0                                       ; +$010A : D081
    movea.l d0,a0                                     ; +$010C : 2040
    move.l d7,d0                                      ; +$010E : 2007
    mulu.w #$0018,d0                                  ; +$0110 : C0FC0018
    addi.l #$00000008,d0                              ; +$0114 : 068000000008
    move.l a4,d1                                      ; +$011A : 220C
    add.l d1,d0                                       ; +$011C : D081
    movea.l d0,a1                                     ; +$011E : 2240
    move.l d7,d5                                      ; +$0120 : 2A07
    mulu.w #$0003,d5                                  ; +$0122 : CAFC0003
L_00510A:
    move.l #$00000000,d0                              ; +$0126 : 203C00000000
    move.b (a0)+,d0                                   ; +$012C : 1018
    addq.l #3,a0                                      ; +$012E : 5688
    lsl.l #8,d0                                       ; +$0130 : E188
    move.l d0,(a1)+                                   ; +$0132 : 22C0
    move.l d0,d1                                      ; +$0134 : 2200
    move.l #$00000000,d0                              ; +$0136 : 203C00000000
    sub.l d1,d0                                       ; +$013C : 9081
    divus.w d6,d0                                     ; +$013E : 81C6
    move.w d0,(a1)+                                   ; +$0140 : 32C0
    subq.l #1,d5                                      ; +$0142 : 5385
    bne.w L_00510A                                    ; +$0144 : 6600FFE0
L_00512C:
    move.l d6,d4                                      ; +$0148 : 2806
L_00512E:
    movea.l 456(a5),a6                                ; +$014A : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$014E : 2C6E0008
    jsr -270(a6)                                      ; +$0152 : 4EAEFEF2
    movea.l a4,a1                                     ; +$0156 : 224C
    move.l d7,d0                                      ; +$0158 : 2007
    swap d0                                           ; +$015A : 4840
    move.l d0,(a1)+                                   ; +$015C : 22C0
    cmpi.l #$00000001,d4                              ; +$015E : 0C8400000001
    beq.w L_005196                                    ; +$0164 : 6700004C
    move.l d7,d0                                      ; +$0168 : 2007
    mulu.w #$0018,d0                                  ; +$016A : C0FC0018
    addi.l #$00000008,d0                              ; +$016E : 068000000008
    move.l a4,d1                                      ; +$0174 : 220C
    add.l d1,d0                                       ; +$0176 : D081
    movea.l d0,a0                                     ; +$0178 : 2040
    move.l d7,d5                                      ; +$017A : 2A07
    mulu.w #$0003,d5                                  ; +$017C : CAFC0003
    movea.l a4,a1                                     ; +$0180 : 224C
    addq.l #4,a1                                      ; +$0182 : 5889
L_005168:
    move.l (a0),d0                                    ; +$0184 : 2010
    move.l #$00000000,d1                              ; +$0186 : 223C00000000
    move.w 4(a0),d1                                   ; +$018C : 32280004
    ext.l d1                                          ; +$0190 : 48C1
    add.l d1,d0                                       ; +$0192 : D081
    move.l d0,(a0)                                    ; +$0194 : 2080
    addq.l #6,a0                                      ; +$0196 : 5C88
    lsr.l #8,d0                                       ; +$0198 : E088
    move.l d0,d1                                      ; +$019A : 2200
    lsl.l #8,d0                                       ; +$019C : E188
    or.l d1,d0                                        ; +$019E : 8081
    move.l d0,d1                                      ; +$01A0 : 2200
    swap d0                                           ; +$01A2 : 4840
    or.l d1,d0                                        ; +$01A4 : 8081
    move.l d0,(a1)+                                   ; +$01A6 : 22C0
    subq.l #1,d5                                      ; +$01A8 : 5385
    bne.w L_005168                                    ; +$01AA : 6600FFD8
    bra.w L_0051A8                                    ; +$01AE : 60000014
L_005196:
    move.l d7,d5                                      ; +$01B2 : 2A07
    mulu.w #$0003,d5                                  ; +$01B4 : CAFC0003
L_00519C:
    move.l #$00000000,(a1)+                           ; +$01B8 : 22FC00000000
    subq.l #1,d5                                      ; +$01BE : 5385
    bne.w L_00519C                                    ; +$01C0 : 6600FFF6
L_0051A8:
    move.l #$00000000,(a1)                            ; +$01C4 : 22BC00000000
    movea.l 456(a5),a0                                ; +$01CA : 206D01C8
    movea.l (a0),a0                                   ; +$01CE : 2050
    move.l a0,d0                                      ; +$01D0 : 2008
    addi.l #$0000002C,d0                              ; +$01D2 : 06800000002C
    movea.l d0,a0                                     ; +$01D8 : 2040
    movea.l a4,a1                                     ; +$01DA : 224C
    movea.l 456(a5),a6                                ; +$01DC : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$01E0 : 2C6E0008
    jsr -882(a6)                                      ; +$01E4 : 4EAEFC8E
    subq.l #1,d4                                      ; +$01E8 : 5384
    bne.w L_00512E                                    ; +$01EA : 6600FF5E
    movea.l a4,a1                                     ; +$01EE : 224C
    movea.l $0004.w,a6                                ; +$01F0 : 2C780004
    jsr -690(a6)                                      ; +$01F4 : 4EAEFD4E
    move.l #$00000001,d3                              ; +$01F8 : 263C00000001
L_0051E2:
    addq.l #4,a7                                      ; +$01FE : 588F
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0200 : 4CDF77F7
    moveq #0,d2                                       ; +$0204 : 7400
    rts                                               ; +$0206 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 46 : aga fade to white --------
Entry_46:
Aga_Fade_To_White:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,-(a7)                                   ; +$0004 : 2F03
    move.l #$00000000,d3                              ; +$0006 : 263C00000000
    move.l (a7),d0                                    ; +$000C : 2017
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_0053EE                                    ; +$0010 : 670001EC
    cmpi.l #$000000FF,d0                              ; +$0014 : 0C80000000FF
    bhi.w L_0053EE                                    ; +$001A : 620001E2
    movea.l 456(a5),a0                                ; +$001E : 206D01C8
    move.l a0,d0                                      ; +$0022 : 2008
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0053EE                                    ; +$0026 : 670001D6
    movea.l (a0),a1                                   ; +$002A : 2250
    move.l a1,d0                                      ; +$002C : 2009
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0053EE                                    ; +$0030 : 670001CC
    tst.l 8(a0)                                       ; +$0034 : 4AA80008
    beq.w L_0053EE                                    ; +$0038 : 670001C4
    move.l 28(a0),d0                                  ; +$003C : 2028001C
    tst.l d0                                          ; +$0040 : 4A80
    ble.w L_0053EE                                    ; +$0042 : 6F0001BA
    cmpi.l #$00000008,d0                              ; +$0046 : 0C8000000008
    bhi.w L_0053EE                                    ; +$004C : 620001B0
    move.l 24(a0),d0                                  ; +$0050 : 20280018
    andi.l #$00000C80,d0                              ; +$0054 : 028000000C80
    bne.w L_0053EE                                    ; +$005A : 660001A2
    move.l 20(a0),d7                                  ; +$005E : 2E280014
    tst.l d7                                          ; +$0062 : 4A87
    beq.w L_0053EE                                    ; +$0064 : 67000198
    cmpi.l #$00000100,d7                              ; +$0068 : 0C8700000100
    bhi.w L_0053EE                                    ; +$006E : 6200018E
    movea.l 48(a1),a1                                 ; +$0072 : 22690030
    move.l a1,d0                                      ; +$0076 : 2009
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0053EE                                    ; +$007A : 67000182
    move.l #$00000000,d0                              ; +$007E : 203C00000000
    move.w 2(a1),d0                                   ; +$0084 : 30290002
    tst.l d0                                          ; +$0088 : 4A80
    beq.w L_0053EE                                    ; +$008A : 67000172
    cmpi.l #$00000100,d0                              ; +$008E : 0C8000000100
    bhi.w L_0053EE                                    ; +$0094 : 62000168
    cmp.l d0,d7                                       ; +$0098 : BE80
    bhi.w L_0053EE                                    ; +$009A : 62000162
    move.l (a7),d6                                    ; +$009E : 2C17
    move.l d7,d0                                      ; +$00A0 : 2007
    mulu.w #$002A,d0                                  ; +$00A2 : C0FC002A
    addi.l #$00000008,d0                              ; +$00A6 : 068000000008
    move.l #$00000001,d1                              ; +$00AC : 223C00000001
    movea.l $0004.w,a6                                ; +$00B2 : 2C780004
    jsr -684(a6)                                      ; +$00B6 : 4EAEFD54
    tst.l d0                                          ; +$00BA : 4A80
    beq.w L_0053EE                                    ; +$00BC : 67000140
    movea.l d0,a4                                     ; +$00C0 : 2840
    cmpi.l #$00000001,d6                              ; +$00C2 : 0C8600000001
    beq.w L_005338                                    ; +$00C8 : 6700007E
    move.l d7,d0                                      ; +$00CC : 2007
    mulu.w #$000C,d0                                  ; +$00CE : C0FC000C
    addi.l #$00000008,d0                              ; +$00D2 : 068000000008
    move.l a4,d1                                      ; +$00D8 : 220C
    add.l d1,d0                                       ; +$00DA : D081
    movea.l d0,a1                                     ; +$00DC : 2240
    movea.l 456(a5),a0                                ; +$00DE : 206D01C8
    movea.l (a0),a0                                   ; +$00E2 : 2050
    movea.l 48(a0),a0                                 ; +$00E4 : 20680030
    move.l #$00000000,d0                              ; +$00E8 : 203C00000000
    move.l d7,d1                                      ; +$00EE : 2207
    movea.l 456(a5),a6                                ; +$00F0 : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$00F4 : 2C6E0008
    jsr -900(a6)                                      ; +$00F8 : 4EAEFC7C
    move.l d7,d0                                      ; +$00FC : 2007
    mulu.w #$000C,d0                                  ; +$00FE : C0FC000C
    addi.l #$00000008,d0                              ; +$0102 : 068000000008
    move.l a4,d1                                      ; +$0108 : 220C
    add.l d1,d0                                       ; +$010A : D081
    movea.l d0,a0                                     ; +$010C : 2040
    move.l d7,d0                                      ; +$010E : 2007
    mulu.w #$0018,d0                                  ; +$0110 : C0FC0018
    addi.l #$00000008,d0                              ; +$0114 : 068000000008
    move.l a4,d1                                      ; +$011A : 220C
    add.l d1,d0                                       ; +$011C : D081
    movea.l d0,a1                                     ; +$011E : 2240
    move.l d7,d5                                      ; +$0120 : 2A07
    mulu.w #$0003,d5                                  ; +$0122 : CAFC0003
L_005316:
    move.l #$00000000,d0                              ; +$0126 : 203C00000000
    move.b (a0)+,d0                                   ; +$012C : 1018
    addq.l #3,a0                                      ; +$012E : 5688
    lsl.l #8,d0                                       ; +$0130 : E188
    move.l d0,(a1)+                                   ; +$0132 : 22C0
    move.l #$000000FF,d1                              ; +$0134 : 223C000000FF
    lsl.l #8,d1                                       ; +$013A : E189
    sub.l d0,d1                                       ; +$013C : 9280
    divus.w d6,d1                                     ; +$013E : 83C6
    move.w d1,(a1)+                                   ; +$0140 : 32C1
    subq.l #1,d5                                      ; +$0142 : 5385
    bne.w L_005316                                    ; +$0144 : 6600FFE0
L_005338:
    move.l d6,d4                                      ; +$0148 : 2806
L_00533A:
    movea.l 456(a5),a6                                ; +$014A : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$014E : 2C6E0008
    jsr -270(a6)                                      ; +$0152 : 4EAEFEF2
    movea.l a4,a1                                     ; +$0156 : 224C
    move.l d7,d0                                      ; +$0158 : 2007
    swap d0                                           ; +$015A : 4840
    move.l d0,(a1)+                                   ; +$015C : 22C0
    cmpi.l #$00000001,d4                              ; +$015E : 0C8400000001
    beq.w L_0053A2                                    ; +$0164 : 6700004C
    move.l d7,d0                                      ; +$0168 : 2007
    mulu.w #$0018,d0                                  ; +$016A : C0FC0018
    addi.l #$00000008,d0                              ; +$016E : 068000000008
    move.l a4,d1                                      ; +$0174 : 220C
    add.l d1,d0                                       ; +$0176 : D081
    movea.l d0,a0                                     ; +$0178 : 2040
    move.l d7,d5                                      ; +$017A : 2A07
    mulu.w #$0003,d5                                  ; +$017C : CAFC0003
    movea.l a4,a1                                     ; +$0180 : 224C
    addq.l #4,a1                                      ; +$0182 : 5889
L_005374:
    move.l (a0),d0                                    ; +$0184 : 2010
    move.l #$00000000,d1                              ; +$0186 : 223C00000000
    move.w 4(a0),d1                                   ; +$018C : 32280004
    ext.l d1                                          ; +$0190 : 48C1
    add.l d1,d0                                       ; +$0192 : D081
    move.l d0,(a0)                                    ; +$0194 : 2080
    addq.l #6,a0                                      ; +$0196 : 5C88
    lsr.l #8,d0                                       ; +$0198 : E088
    move.l d0,d1                                      ; +$019A : 2200
    lsl.l #8,d0                                       ; +$019C : E188
    or.l d1,d0                                        ; +$019E : 8081
    move.l d0,d1                                      ; +$01A0 : 2200
    swap d0                                           ; +$01A2 : 4840
    or.l d1,d0                                        ; +$01A4 : 8081
    move.l d0,(a1)+                                   ; +$01A6 : 22C0
    subq.l #1,d5                                      ; +$01A8 : 5385
    bne.w L_005374                                    ; +$01AA : 6600FFD8
    bra.w L_0053B4                                    ; +$01AE : 60000014
L_0053A2:
    move.l d7,d5                                      ; +$01B2 : 2A07
    mulu.w #$0003,d5                                  ; +$01B4 : CAFC0003
L_0053A8:
    move.l #$FFFFFFFF,(a1)+                           ; +$01B8 : 22FCFFFFFFFF
    subq.l #1,d5                                      ; +$01BE : 5385
    bne.w L_0053A8                                    ; +$01C0 : 6600FFF6
L_0053B4:
    move.l #$00000000,(a1)                            ; +$01C4 : 22BC00000000
    movea.l 456(a5),a0                                ; +$01CA : 206D01C8
    movea.l (a0),a0                                   ; +$01CE : 2050
    move.l a0,d0                                      ; +$01D0 : 2008
    addi.l #$0000002C,d0                              ; +$01D2 : 06800000002C
    movea.l d0,a0                                     ; +$01D8 : 2040
    movea.l a4,a1                                     ; +$01DA : 224C
    movea.l 456(a5),a6                                ; +$01DC : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$01E0 : 2C6E0008
    jsr -882(a6)                                      ; +$01E4 : 4EAEFC8E
    subq.l #1,d4                                      ; +$01E8 : 5384
    bne.w L_00533A                                    ; +$01EA : 6600FF5E
    movea.l a4,a1                                     ; +$01EE : 224C
    movea.l $0004.w,a6                                ; +$01F0 : 2C780004
    jsr -690(a6)                                      ; +$01F4 : 4EAEFD4E
    move.l #$00000001,d3                              ; +$01F8 : 263C00000001
L_0053EE:
    addq.l #4,a7                                      ; +$01FE : 588F
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0200 : 4CDF77F7
    moveq #0,d2                                       ; +$0204 : 7400
    rts                                               ; +$0206 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 47 : aga palette cycle --------
Entry_47:
Aga_Palette_Cycle:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,-(a7)                                   ; +$0004 : 2F03
    move.l (a3)+,d5                                   ; +$0006 : 2A1B
    move.l (a3)+,d4                                   ; +$0008 : 281B
    move.l #$00000000,d3                              ; +$000A : 263C00000000
    move.l (a7),d0                                    ; +$0010 : 2017
    cmpi.l #$00000001,d0                              ; +$0012 : 0C8000000001
    beq.w L_005422                                    ; +$0018 : 6700000C
    cmpi.l #$FFFFFFFF,d0                              ; +$001C : 0C80FFFFFFFF
    bne.w L_0055E6                                    ; +$0022 : 660001C6
L_005422:
    cmpi.l #$000000FF,d5                              ; +$0026 : 0C85000000FF
    bhi.w L_0055E6                                    ; +$002C : 620001BC
    cmp.l d5,d4                                       ; +$0030 : B885
    bcc.w L_0055E6                                    ; +$0032 : 640001B6
    movea.l 456(a5),a0                                ; +$0036 : 206D01C8
    move.l a0,d0                                      ; +$003A : 2008
    tst.l d0                                          ; +$003C : 4A80
    beq.w L_0055E6                                    ; +$003E : 670001AA
    movea.l (a0),a1                                   ; +$0042 : 2250
    move.l a1,d0                                      ; +$0044 : 2009
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_0055E6                                    ; +$0048 : 670001A0
    tst.l 8(a0)                                       ; +$004C : 4AA80008
    beq.w L_0055E6                                    ; +$0050 : 67000198
    move.l 28(a0),d0                                  ; +$0054 : 2028001C
    tst.l d0                                          ; +$0058 : 4A80
    ble.w L_0055E6                                    ; +$005A : 6F00018E
    cmpi.l #$00000008,d0                              ; +$005E : 0C8000000008
    bhi.w L_0055E6                                    ; +$0064 : 62000184
    move.l 24(a0),d0                                  ; +$0068 : 20280018
    andi.l #$00000C80,d0                              ; +$006C : 028000000C80
    bne.w L_0055E6                                    ; +$0072 : 66000176
    move.l 20(a0),d7                                  ; +$0076 : 2E280014
    tst.l d7                                          ; +$007A : 4A87
    beq.w L_0055E6                                    ; +$007C : 6700016C
    cmpi.l #$00000100,d7                              ; +$0080 : 0C8700000100
    bhi.w L_0055E6                                    ; +$0086 : 62000162
    cmp.l d7,d5                                       ; +$008A : BA87
    bcc.w L_0055E6                                    ; +$008C : 6400015C
    movea.l 48(a1),a1                                 ; +$0090 : 22690030
    move.l a1,d0                                      ; +$0094 : 2009
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_0055E6                                    ; +$0098 : 67000150
    move.l #$00000000,d0                              ; +$009C : 203C00000000
    move.w 2(a1),d0                                   ; +$00A2 : 30290002
    tst.l d0                                          ; +$00A6 : 4A80
    beq.w L_0055E6                                    ; +$00A8 : 67000140
    cmpi.l #$00000100,d0                              ; +$00AC : 0C8000000100
    bhi.w L_0055E6                                    ; +$00B2 : 62000136
    cmp.l d0,d7                                       ; +$00B6 : BE80
    bhi.w L_0055E6                                    ; +$00B8 : 62000130
    cmp.l d0,d5                                       ; +$00BC : BA80
    bcc.w L_0055E6                                    ; +$00BE : 6400012A
    move.l d5,d7                                      ; +$00C2 : 2E05
    sub.l d4,d7                                       ; +$00C4 : 9E84
    addq.l #1,d7                                      ; +$00C6 : 5287
    move.l d7,d0                                      ; +$00C8 : 2007
    mulu.w #$000C,d0                                  ; +$00CA : C0FC000C
    addi.l #$00000008,d0                              ; +$00CE : 068000000008
    move.l #$00000001,d1                              ; +$00D4 : 223C00000001
    movea.l $0004.w,a6                                ; +$00DA : 2C780004
    jsr -684(a6)                                      ; +$00DE : 4EAEFD54
    tst.l d0                                          ; +$00E2 : 4A80
    beq.w L_0055E6                                    ; +$00E4 : 67000104
    movea.l d0,a4                                     ; +$00E8 : 2840
    move.l d7,d0                                      ; +$00EA : 2007
    swap d0                                           ; +$00EC : 4840
    or.l d4,d0                                        ; +$00EE : 8084
    move.l d0,(a4)                                    ; +$00F0 : 2880
    movea.l a4,a1                                     ; +$00F2 : 224C
    addq.l #4,a1                                      ; +$00F4 : 5889
    movea.l 456(a5),a0                                ; +$00F6 : 206D01C8
    movea.l (a0),a0                                   ; +$00FA : 2050
    movea.l 48(a0),a0                                 ; +$00FC : 20680030
    move.l d4,d0                                      ; +$0100 : 2004
    move.l d7,d1                                      ; +$0102 : 2207
    movea.l 456(a5),a6                                ; +$0104 : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$0108 : 2C6E0008
    jsr -900(a6)                                      ; +$010C : 4EAEFC7C
    move.l d7,d0                                      ; +$0110 : 2007
    mulu.w #$000C,d0                                  ; +$0112 : C0FC000C
    addi.l #$00000004,d0                              ; +$0116 : 068000000004
    move.l a4,d1                                      ; +$011C : 220C
    add.l d1,d0                                       ; +$011E : D081
    movea.l d0,a2                                     ; +$0120 : 2440
    move.l #$00000000,(a2)                            ; +$0122 : 24BC00000000
    move.l (a7),d0                                    ; +$0128 : 2017
    cmpi.l #$00000001,d0                              ; +$012A : 0C8000000001
    beq.w L_005578                                    ; +$0130 : 6700004A
    movea.l a4,a0                                     ; +$0134 : 204C
    addq.l #4,a0                                      ; +$0136 : 5888
    move.l a0,d0                                      ; +$0138 : 2008
    addi.l #$0000000C,d0                              ; +$013A : 06800000000C
    movea.l d0,a1                                     ; +$0140 : 2240
    move.l (a0),d4                                    ; +$0142 : 2810
    move.l 4(a0),d5                                   ; +$0144 : 2A280004
    move.l 8(a0),d6                                   ; +$0148 : 2C280008
    subq.l #1,d7                                      ; +$014C : 5387
L_00554A:
    move.l (a1),(a0)                                  ; +$014E : 2091
    move.l 4(a1),4(a0)                                ; +$0150 : 216900040004
    move.l 8(a1),8(a0)                                ; +$0156 : 216900080008
    movea.l a1,a0                                     ; +$015C : 2049
    move.l a1,d0                                      ; +$015E : 2009
    addi.l #$0000000C,d0                              ; +$0160 : 06800000000C
    movea.l d0,a1                                     ; +$0166 : 2240
    subq.l #1,d7                                      ; +$0168 : 5387
    bne.w L_00554A                                    ; +$016A : 6600FFE2
    move.l d4,(a0)                                    ; +$016E : 2084
    move.l d5,4(a0)                                   ; +$0170 : 21450004
    move.l d6,8(a0)                                   ; +$0174 : 21460008
    bra.w L_0055B8                                    ; +$0178 : 60000042
L_005578:
    move.l a2,d0                                      ; +$017C : 200A
    subi.l #$0000000C,d0                              ; +$017E : 04800000000C
    movea.l d0,a1                                     ; +$0184 : 2240
    move.l (a1),d4                                    ; +$0186 : 2811
    move.l 4(a1),d5                                   ; +$0188 : 2A290004
    move.l 8(a1),d6                                   ; +$018C : 2C290008
    subq.l #1,d7                                      ; +$0190 : 5387
L_00558E:
    move.l a1,d0                                      ; +$0192 : 2009
    subi.l #$0000000C,d0                              ; +$0194 : 04800000000C
    movea.l d0,a0                                     ; +$019A : 2040
    move.l (a0),(a1)                                  ; +$019C : 2290
    move.l 4(a0),4(a1)                                ; +$019E : 236800040004
    move.l 8(a0),8(a1)                                ; +$01A4 : 236800080008
    movea.l a0,a1                                     ; +$01AA : 2248
    subq.l #1,d7                                      ; +$01AC : 5387
    bne.w L_00558E                                    ; +$01AE : 6600FFE2
    move.l d4,(a1)                                    ; +$01B2 : 2284
    move.l d5,4(a1)                                   ; +$01B4 : 23450004
    move.l d6,8(a1)                                   ; +$01B8 : 23460008
L_0055B8:
    movea.l 456(a5),a0                                ; +$01BC : 206D01C8
    movea.l (a0),a0                                   ; +$01C0 : 2050
    move.l a0,d0                                      ; +$01C2 : 2008
    addi.l #$0000002C,d0                              ; +$01C4 : 06800000002C
    movea.l d0,a0                                     ; +$01CA : 2040
    movea.l a4,a1                                     ; +$01CC : 224C
    movea.l 456(a5),a6                                ; +$01CE : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$01D2 : 2C6E0008
    jsr -882(a6)                                      ; +$01D6 : 4EAEFC8E
    movea.l a4,a1                                     ; +$01DA : 224C
    movea.l $0004.w,a6                                ; +$01DC : 2C780004
    jsr -690(a6)                                      ; +$01E0 : 4EAEFD4E
    move.l #$00000001,d3                              ; +$01E4 : 263C00000001
L_0055E6:
    addq.l #4,a7                                      ; +$01EA : 588F
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01EC : 4CDF77F7
    moveq #0,d2                                       ; +$01F0 : 7400
    rts                                               ; +$01F2 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 48 : aga font select --------
Entry_48:
Aga_Font_Select:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    movea.l (a3)+,a4                                  ; +$0006 : 285B
    move.l #$00000000,d3                              ; +$0008 : 263C00000000
    movea.l 456(a5),a2                                ; +$000E : 246D01C8
    move.l a2,d0                                      ; +$0012 : 200A
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00574A                                    ; +$0016 : 6700013E
    move.l (a2),d6                                    ; +$001A : 2C12
    tst.l d6                                          ; +$001C : 4A86
    beq.w L_00574A                                    ; +$001E : 67000136
    move.l 8(a2),d0                                   ; +$0022 : 202A0008
    tst.l d0                                          ; +$0026 : 4A80
    beq.w L_00574A                                    ; +$0028 : 6700012C
    tst.l d7                                          ; +$002C : 4A87
    bne.w L_00566E                                    ; +$002E : 6600004A
    move.l a4,d0                                      ; +$0032 : 200C
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_00563C                                    ; +$0036 : 67000010
    move.l #$00000000,d0                              ; +$003A : 203C00000000
    move.w (a4),d0                                    ; +$0040 : 3014
    tst.l d0                                          ; +$0042 : 4A80
    bne.w L_00574A                                    ; +$0044 : 66000110
L_00563C:
    movea.l d6,a0                                     ; +$0048 : 2046
    bsr.w L_005752                                    ; +$004A : 61000112
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_005664                                    ; +$0050 : 6700001E
    lea L_0057A6(pc),a1                               ; +$0054 : 43FA015C
    move.l #$00000000,(a1)                            ; +$0058 : 22BC00000000
    move.l #$00000000,4(a1)                           ; +$005E : 237C000000000004
    movea.l d0,a1                                     ; +$0066 : 2240
    movea.l 8(a2),a6                                  ; +$0068 : 2C6A0008
    bsr.w L_005B4A                                    ; +$006C : 610004E8
L_005664:
    move.l #$00000001,d3                              ; +$0070 : 263C00000001
    bra.w L_00574A                                    ; +$0076 : 600000DE
L_00566E:
    cmpi.l #$000000FF,d7                              ; +$007A : 0C87000000FF
    bhi.w L_00574A                                    ; +$0080 : 620000D4
    move.l a4,d0                                      ; +$0084 : 200C
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_00574A                                    ; +$0088 : 670000CC
    move.l #$00000000,d5                              ; +$008C : 2A3C00000000
    move.w (a4),d5                                    ; +$0092 : 3A14
    tst.l d5                                          ; +$0094 : 4A85
    beq.w L_00574A                                    ; +$0096 : 670000BE
    cmpi.l #$0000007F,d5                              ; +$009A : 0C850000007F
    bhi.w L_00574A                                    ; +$00A0 : 620000B4
    lea -176(a7),a7                                   ; +$00A4 : 4FEFFF50
    lea 16(a7),a0                                     ; +$00A8 : 41EF0010
    movea.l a4,a1                                     ; +$00AC : 224C
    addq.l #2,a1                                      ; +$00AE : 5489
    move.l d5,d4                                      ; +$00B0 : 2805
    subq.l #1,d4                                      ; +$00B2 : 5384
L_0056A8:
    move.b (a1)+,d0                                   ; +$00B4 : 1019
    tst.b d0                                          ; +$00B6 : 4A00
    beq.w L_005746                                    ; +$00B8 : 67000098
    move.b d0,(a0)+                                   ; +$00BC : 10C0
    dbra d4,L_0056A8                                  ; +$00BE : 51CCFFF4
    clr.b (a0)                                        ; +$00C2 : 4210
    lea 16(a7),a0                                     ; +$00C4 : 41EF0010
    move.l a0,(a7)                                    ; +$00C8 : 2E88
    move.w d7,4(a7)                                   ; +$00CA : 3F470004
    move.w #$0000,6(a7)                               ; +$00CE : 3F7C00000006
    move.l #$6469736B,144(a7)                         ; +$00D4 : 2F7C6469736B0090
    move.l #$666F6E74,148(a7)                         ; +$00DC : 2F7C666F6E740094
    move.l #$2E6C6962,152(a7)                         ; +$00E4 : 2F7C2E6C69620098
    move.l #$72617279,156(a7)                         ; +$00EC : 2F7C72617279009C
    clr.b 160(a7)                                     ; +$00F4 : 422F00A0
    lea 144(a7),a1                                    ; +$00F8 : 43EF0090
    move.l #$00000000,d0                              ; +$00FC : 203C00000000
    movea.l $0004.w,a6                                ; +$0102 : 2C780004
    jsr -552(a6)                                      ; +$0106 : 4EAEFDD8
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_005746                                    ; +$010C : 67000044
    movea.l d0,a6                                     ; +$0110 : 2C40
    movea.l a7,a0                                     ; +$0112 : 204F
    jsr -30(a6)                                       ; +$0114 : 4EAEFFE2
    move.l d0,d4                                      ; +$0118 : 2800
    movea.l a6,a1                                     ; +$011A : 224E
    movea.l $0004.w,a6                                ; +$011C : 2C780004
    jsr -414(a6)                                      ; +$0120 : 4EAEFE62
    tst.l d4                                          ; +$0124 : 4A84
    beq.w L_005746                                    ; +$0126 : 6700002A
    movea.l d6,a0                                     ; +$012A : 2046
    bsr.w L_005752                                    ; +$012C : 61000030
    move.l d0,d5                                      ; +$0130 : 2A00
    lea L_0057A6(pc),a1                               ; +$0132 : 43FA007E
    move.l d6,(a1)                                    ; +$0136 : 2286
    move.l d4,4(a1)                                   ; +$0138 : 23440004
    tst.l d5                                          ; +$013C : 4A85
    beq.w L_005740                                    ; +$013E : 6700000C
    movea.l d5,a1                                     ; +$0142 : 2245
    movea.l 8(a2),a6                                  ; +$0144 : 2C6A0008
    bsr.w L_005B4A                                    ; +$0148 : 6100040C
L_005740:
    move.l #$00000001,d3                              ; +$014C : 263C00000001
L_005746:
    lea 176(a7),a7                                    ; +$0152 : 4FEF00B0
L_00574A:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0156 : 4CDF77F7
    moveq #0,d2                                       ; +$015A : 7400
    rts                                               ; +$015C : 4E75
L_005752:
    lea L_0057A6(pc),a1                               ; +$015E : 43FA0052
    move.l (a1),d0                                    ; +$0162 : 2011
    move.l a0,d1                                      ; +$0164 : 2208
    cmp.l d1,d0                                       ; +$0166 : B081
    bne.w L_005766                                    ; +$0168 : 66000008
    move.l 4(a1),d0                                   ; +$016C : 20290004
    rts                                               ; +$0170 : 4E75
L_005766:
    move.l #$00000000,d0                              ; +$0172 : 203C00000000
    rts                                               ; +$0178 : 4E75
L_00576E:
    move.l a6,-(a7)                                   ; +$017A : 2F0E
    move.l a0,-(a7)                                   ; +$017C : 2F08
    move.l a2,-(a7)                                   ; +$017E : 2F0A
    bsr.w L_005752                                    ; +$0180 : 6100FFDC
    tst.l d0                                          ; +$0184 : 4A80
    beq.w L_00579A                                    ; +$0186 : 6700001E
    lea L_0057A6(pc),a1                               ; +$018A : 43FA0026
    move.l #$00000000,(a1)                            ; +$018E : 22BC00000000
    move.l #$00000000,4(a1)                           ; +$0194 : 237C000000000004
    movea.l d0,a1                                     ; +$019C : 2240
    movea.l 8(a2),a6                                  ; +$019E : 2C6A0008
    bsr.w L_005B4A                                    ; +$01A2 : 610003B2
L_00579A:
    movea.l (a7)+,a2                                  ; +$01A6 : 245F
    movea.l (a7)+,a0                                  ; +$01A8 : 205F
    movea.l (a7)+,a6                                  ; +$01AA : 2C5F
    jsr -66(a6)                                       ; +$01AC : 4EAEFFBE
    rts                                               ; +$01B0 : 4E75
L_0057A6:
    dcb.b 8,0
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 49 : aga font bank select --------
Entry_49:
Aga_Font_Bank_Select:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l #$00000000,d3                              ; +$0008 : 263C00000000
    movea.l 456(a5),a2                                ; +$000E : 246D01C8
    move.l a2,d0                                      ; +$0012 : 200A
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_005B3C                                    ; +$0016 : 67000372
    move.l (a2),d0                                    ; +$001A : 2012
    tst.l d0                                          ; +$001C : 4A80
    beq.w L_005B3C                                    ; +$001E : 6700036A
    move.l 8(a2),d0                                   ; +$0022 : 202A0008
    tst.l d0                                          ; +$0026 : 4A80
    beq.w L_005B3C                                    ; +$0028 : 67000360
    cmpi.l #$00000070,d7                              ; +$002C : 0C8700000070
    bcs.w L_005B3C                                    ; +$0032 : 65000356
    cmpi.l #$0000FFFF,d7                              ; +$0036 : 0C870000FFFF
    bhi.w L_005B3C                                    ; +$003C : 6200034C
    move.l d6,d0                                      ; +$0040 : 2006
    cmpi.l #$00000018,d0                              ; +$0042 : 0C8000000018
    bls.w L_005B3C                                    ; +$0048 : 63000340
    andi.l #$00000001,d0                              ; +$004C : 028000000001
    bne.w L_005B3C                                    ; +$0052 : 66000336
    movea.l d6,a4                                     ; +$0056 : 2846
    move.l d6,d0                                      ; +$0058 : 2006
    subi.l #$00000018,d0                              ; +$005A : 048000000018
    movea.l d0,a1                                     ; +$0060 : 2240
    movea.l $0004.w,a6                                ; +$0062 : 2C780004
    jsr -534(a6)                                      ; +$0066 : 4EAEFDEA
    tst.l d0                                          ; +$006A : 4A80
    beq.w L_005B3C                                    ; +$006C : 6700031C
    move.l d6,d0                                      ; +$0070 : 2006
    add.l d7,d0                                       ; +$0072 : D087
    bcs.w L_005B3C                                    ; +$0074 : 65000314
    subq.l #1,d0                                      ; +$0078 : 5380
    movea.l d0,a1                                     ; +$007A : 2240
    jsr -534(a6)                                      ; +$007C : 4EAEFDEA
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_005B3C                                    ; +$0082 : 67000306
    move.l -20(a4),d0                                 ; +$0086 : 202CFFEC
    move.l d7,d1                                      ; +$008A : 2207
    addi.l #$00000010,d1                              ; +$008C : 068100000010
    cmp.l d1,d0                                       ; +$0092 : B081
    bne.w L_005B3C                                    ; +$0094 : 660002F4
    move.l -16(a4),d0                                 ; +$0098 : 202CFFF0
    cmpi.l #$00000005,d0                              ; +$009C : 0C8000000005
    bcs.w L_005B3C                                    ; +$00A2 : 650002E6
    cmpi.l #$0000FFFF,d0                              ; +$00A6 : 0C800000FFFF
    bhi.w L_005B3C                                    ; +$00AC : 620002DC
    move.l #$00000000,d0                              ; +$00B0 : 203C00000000
    move.w -12(a4),d0                                 ; +$00B6 : 302CFFF4
    andi.w #$FFFC,d0                                  ; +$00BA : 0240FFFC
    tst.l d0                                          ; +$00BE : 4A80
    bne.w L_005B3C                                    ; +$00C0 : 660002C8
    move.l -8(a4),d0                                  ; +$00C4 : 202CFFF8
    cmpi.l #$42616E6B,d0                              ; +$00C8 : 0C8042616E6B
    bne.w L_005B3C                                    ; +$00CE : 660002BA
    move.l -4(a4),d0                                  ; +$00D2 : 202CFFFC
    cmpi.l #$466F6E74,d0                              ; +$00D6 : 0C80466F6E74
    bne.w L_005B3C                                    ; +$00DC : 660002AC
    move.l (a4),d0                                    ; +$00E0 : 2014
    cmpi.l #$464F4E54,d0                              ; +$00E2 : 0C80464F4E54
    bne.w L_005B3C                                    ; +$00E8 : 660002A0
    move.l #$00000000,d0                              ; +$00EC : 203C00000000
    move.b 32(a4),d0                                  ; +$00F2 : 102C0020
    cmpi.l #$0000000C,d0                              ; +$00F6 : 0C800000000C
    bne.w L_005B3C                                    ; +$00FC : 6600028C
    move.l #$00000000,d4                              ; +$0100 : 283C00000000
    move.w 10(a4),d4                                  ; +$0106 : 382C000A
    move.l #$00000000,d5                              ; +$010A : 2A3C00000000
    move.w 14(a4),d5                                  ; +$0110 : 3A2C000E
    cmpi.l #$0000004E,d4                              ; +$0114 : 0C840000004E
    bcs.w L_005B3C                                    ; +$011A : 6500026E
    cmp.l d4,d5                                       ; +$011E : BA84
    bls.w L_005B3C                                    ; +$0120 : 63000268
    cmp.l d7,d5                                       ; +$0124 : BA87
    bcc.w L_005B3C                                    ; +$0126 : 64000262
    move.l #$00000000,d0                              ; +$012A : 203C00000000
    move.w 44(a4),d0                                  ; +$0130 : 302C002C
    tst.l d0                                          ; +$0134 : 4A80
    beq.w L_005B3C                                    ; +$0136 : 67000252
    cmpi.l #$000000FF,d0                              ; +$013A : 0C80000000FF
    bhi.w L_005B3C                                    ; +$0140 : 62000248
    move.l #$00000000,d3                              ; +$0144 : 263C00000000
    move.w 48(a4),d3                                  ; +$014A : 362C0030
    tst.l d3                                          ; +$014E : 4A83
    beq.w L_005B3C                                    ; +$0150 : 67000238
    cmpi.l #$000000FF,d3                              ; +$0154 : 0C83000000FF
    bhi.w L_005B3C                                    ; +$015A : 6200022E
    move.l #$00000000,d1                              ; +$015E : 223C00000000
    move.w 50(a4),d1                                  ; +$0164 : 322C0032
    cmp.l d0,d1                                       ; +$0168 : B280
    bcc.w L_005B3C                                    ; +$016A : 6400021E
    move.l #$00000000,d1                              ; +$016E : 223C00000000
    move.b 46(a4),d1                                  ; +$0174 : 122C002E
    andi.b #$40,d1                                    ; +$0178 : 02010040
    tst.l d1                                          ; +$017C : 4A81
    bne.w L_005B3C                                    ; +$017E : 6600020A
    move.l 68(a4),d0                                  ; +$0182 : 202C0044
    tst.l d0                                          ; +$0186 : 4A80
    bne.w L_005B3C                                    ; +$0188 : 66000200
    move.l 72(a4),d0                                  ; +$018C : 202C0048
    tst.l d0                                          ; +$0190 : 4A80
    bne.w L_005B3C                                    ; +$0192 : 660001F6
    move.l #$00000000,d6                              ; +$0196 : 2C3C00000000
    move.b 57(a4),d6                                  ; +$019C : 1C2C0039
    move.l #$00000000,d0                              ; +$01A0 : 203C00000000
    move.b 56(a4),d0                                  ; +$01A6 : 102C0038
    sub.l d0,d6                                       ; +$01AA : 9C80
    bcs.w L_005B3C                                    ; +$01AC : 650001DC
    addq.l #2,d6                                      ; +$01B0 : 5486
    move.l d6,d0                                      ; +$01B2 : 2006
    lsl.l #2,d0                                       ; +$01B4 : E588
    add.l d5,d0                                       ; +$01B6 : D085
    bcs.w L_005B3C                                    ; +$01B8 : 650001D0
    move.l #$00000000,d1                              ; +$01BC : 223C00000000
    move.b 47(a4),d1                                  ; +$01C2 : 122C002F
    andi.b #$20,d1                                    ; +$01C6 : 02010020
    tst.b d1                                          ; +$01CA : 4A01
    beq.w L_00598C                                    ; +$01CC : 6700000C
    move.l d6,d1                                      ; +$01D0 : 2206
    lsl.l #2,d1                                       ; +$01D2 : E589
    add.l d1,d0                                       ; +$01D4 : D081
    bcs.w L_005B3C                                    ; +$01D6 : 650001B2
L_00598C:
    cmp.l d7,d0                                       ; +$01DA : B087
    bne.w L_005B3C                                    ; +$01DC : 660001AC
    move.l #$00000000,d1                              ; +$01E0 : 223C00000000
    move.w 62(a4),d1                                  ; +$01E6 : 322C003E
    tst.l d1                                          ; +$01EA : 4A81
    beq.w L_005B3C                                    ; +$01EC : 6700019C
    move.l d1,d2                                      ; +$01F0 : 2401
    andi.l #$00000001,d2                              ; +$01F2 : 028200000001
    bne.w L_005B3C                                    ; +$01F8 : 66000190
    move.l d1,d2                                      ; +$01FC : 2401
    lsl.l #3,d2                                       ; +$01FE : E78A
    move.l #$00000000,d0                              ; +$0200 : 203C00000000
    move.w 44(a4),d0                                  ; +$0206 : 302C002C
    mulu.w d1,d0                                      ; +$020A : C0C1
    move.l d5,d1                                      ; +$020C : 2205
    sub.l d4,d1                                       ; +$020E : 9284
    cmp.l d1,d0                                       ; +$0210 : B081
    bne.w L_005B3C                                    ; +$0212 : 66000176
    move.l d6,-(a7)                                   ; +$0216 : 2F06
    move.l d4,d1                                      ; +$0218 : 2204
    subi.l #$0000004C,d1                              ; +$021A : 04810000004C
    move.l a4,d0                                      ; +$0220 : 200C
    addi.l #$0000004C,d0                              ; +$0222 : 06800000004C
    movea.l d0,a1                                     ; +$0228 : 2240
    move.b (a1),d0                                    ; +$022A : 1011
    tst.b d0                                          ; +$022C : 4A00
    beq.w L_0059F8                                    ; +$022E : 67000016
L_0059E4:
    move.l #$00000000,d0                              ; +$0232 : 203C00000000
    move.b (a1)+,d0                                   ; +$0238 : 1019
    tst.b d0                                          ; +$023A : 4A00
    beq.w L_0059FE                                    ; +$023C : 6700000E
    subq.l #1,d1                                      ; +$0240 : 5381
    bne.w L_0059E4                                    ; +$0242 : 6600FFEE
L_0059F8:
    move.l (a7)+,d6                                   ; +$0246 : 2C1F
    bra.w L_005B3C                                    ; +$0248 : 60000140
L_0059FE:
    move.l (a7)+,d6                                   ; +$024C : 2C1F
    move.l a4,d0                                      ; +$024E : 200C
    add.l d5,d0                                       ; +$0250 : D085
    movea.l d0,a1                                     ; +$0252 : 2240
    move.l #$00000000,d0                              ; +$0254 : 203C00000000
    move.b 47(a4),d0                                  ; +$025A : 102C002F
    andi.b #$20,d0                                    ; +$025E : 02000020
    tst.b d0                                          ; +$0262 : 4A00
    beq.w L_005A20                                    ; +$0264 : 67000008
    move.l #$00000100,d3                              ; +$0268 : 263C00000100
L_005A20:
    move.l #$00000000,d0                              ; +$026E : 203C00000000
    move.w (a1)+,d0                                   ; +$0274 : 3019
    move.l #$00000000,d1                              ; +$0276 : 223C00000000
    move.w (a1)+,d1                                   ; +$027C : 3219
    cmp.l d3,d1                                       ; +$027E : B283
    bhi.w L_005B3C                                    ; +$0280 : 62000108
    add.l d1,d0                                       ; +$0284 : D081
    cmp.l d2,d0                                       ; +$0286 : B082
    bhi.w L_005B3C                                    ; +$0288 : 62000100
    subq.l #1,d6                                      ; +$028C : 5386
    bne.w L_005A20                                    ; +$028E : 6600FFDE
    move.l a4,-(a7)                                   ; +$0292 : 2F0C
    move.l d7,d0                                      ; +$0294 : 2007
    move.l #$00010003,d1                              ; +$0296 : 223C00010003
    movea.l $0004.w,a6                                ; +$029C : 2C780004
    jsr -684(a6)                                      ; +$02A0 : 4EAEFD54
    tst.l d0                                          ; +$02A4 : 4A80
    bne.w L_005A62                                    ; +$02A6 : 66000008
    movea.l (a7)+,a0                                  ; +$02AA : 205F
    bra.w L_005B3C                                    ; +$02AC : 600000DC
L_005A62:
    movea.l d0,a4                                     ; +$02B0 : 2840
    movea.l (a7)+,a0                                  ; +$02B2 : 205F
    movea.l a4,a1                                     ; +$02B4 : 224C
    move.l d7,d0                                      ; +$02B6 : 2007
    jsr -624(a6)                                      ; +$02B8 : 4EAEFD90
    move.l a4,d0                                      ; +$02BC : 200C
    addi.l #$0000004C,d0                              ; +$02BE : 06800000004C
    move.l d0,34(a4)                                  ; +$02C4 : 29400022
    move.l a4,d0                                      ; +$02C8 : 200C
    add.l d4,d0                                       ; +$02CA : D084
    move.l d0,58(a4)                                  ; +$02CC : 2940003A
    move.l a4,d0                                      ; +$02D0 : 200C
    add.l d5,d0                                       ; +$02D2 : D085
    move.l d0,64(a4)                                  ; +$02D4 : 29400040
    move.l #$00000000,38(a4)                          ; +$02D8 : 297C000000000026
    move.w #$0000,54(a4)                              ; +$02E0 : 397C00000036
    move.l #$00000000,d0                              ; +$02E6 : 203C00000000
    move.b 47(a4),d0                                  ; +$02EC : 102C002F
    andi.b #$20,d0                                    ; +$02F0 : 02000020
    tst.b d0                                          ; +$02F4 : 4A00
    bne.w L_005AC0                                    ; +$02F6 : 66000016
    move.l #$00000000,68(a4)                          ; +$02FA : 297C000000000044
    move.l #$00000000,72(a4)                          ; +$0302 : 297C000000000048
    bra.w L_005AEC                                    ; +$030A : 6000002E
L_005AC0:
    move.l #$00000000,d0                              ; +$030E : 203C00000000
    move.b 57(a4),d0                                  ; +$0314 : 102C0039
    move.l #$00000000,d1                              ; +$0318 : 223C00000000
    move.b 56(a4),d1                                  ; +$031E : 122C0038
    sub.l d1,d0                                       ; +$0322 : 9081
    addq.l #2,d0                                      ; +$0324 : 5480
    lsl.l #2,d0                                       ; +$0326 : E588
    move.l a4,d1                                      ; +$0328 : 220C
    add.l d5,d1                                       ; +$032A : D285
    add.l d0,d1                                       ; +$032C : D280
    move.l d1,68(a4)                                  ; +$032E : 29410044
    lsr.l #1,d0                                       ; +$0332 : E288
    add.l d0,d1                                       ; +$0334 : D280
    move.l d1,72(a4)                                  ; +$0336 : 29410048
L_005AEC:
    move.l #$00000000,d0                              ; +$033A : 203C00000000
    move.b 47(a4),d0                                  ; +$0340 : 102C002F
    andi.b #$FC,d0                                    ; +$0344 : 020000FC
    move.b d0,47(a4)                                  ; +$0348 : 1940002F
    lea L_0057A6(pc),a1                               ; +$034C : 43FAFCA6
    move.l 4(a1),d6                                   ; +$0350 : 2C290004
    tst.l d6                                          ; +$0354 : 4A86
    beq.w L_005B16                                    ; +$0356 : 6700000C
    movea.l d6,a1                                     ; +$035A : 2246
    movea.l 8(a2),a6                                  ; +$035C : 2C6A0008
    bsr.w L_005B4A                                    ; +$0360 : 61000036
L_005B16:
    move.l a4,d0                                      ; +$0364 : 200C
    addi.l #$00000018,d0                              ; +$0366 : 068000000018
    lea L_005B9E(pc),a1                               ; +$036C : 43FA007E
    move.l d0,(a1)                                    ; +$0370 : 2280
    move.l a4,4(a1)                                   ; +$0372 : 234C0004
    lea L_0057A6(pc),a1                               ; +$0376 : 43FAFC7C
    move.l (a2),(a1)                                  ; +$037A : 2292
    move.l d0,4(a1)                                   ; +$037C : 23400004
    move.l #$00000001,d3                              ; +$0380 : 263C00000001
    bra.w L_005B42                                    ; +$0386 : 60000008
L_005B3C:
    move.l #$00000000,d3                              ; +$038A : 263C00000000
L_005B42:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0390 : 4CDF77F7
    moveq #0,d2                                       ; +$0394 : 7400
    rts                                               ; +$0396 : 4E75
L_005B4A:
    move.l d0,-(a7)                                   ; +$0398 : 2F00
    move.l d1,-(a7)                                   ; +$039A : 2F01
    move.l a0,-(a7)                                   ; +$039C : 2F08
    move.l a2,-(a7)                                   ; +$039E : 2F0A
    move.l a6,-(a7)                                   ; +$03A0 : 2F0E
    move.l a1,d0                                      ; +$03A2 : 2009
    tst.l d0                                          ; +$03A4 : 4A80
    beq.w L_005B92                                    ; +$03A6 : 67000038
    lea L_005B9E(pc),a2                               ; +$03AA : 45FA0040
    cmp.l (a2),d0                                     ; +$03AE : B092
    bne.w L_005B8E                                    ; +$03B0 : 6600002A
    movea.l a1,a0                                     ; +$03B4 : 2049
    jsr -822(a6)                                      ; +$03B6 : 4EAEFCCA
    lea L_005B9E(pc),a2                               ; +$03BA : 45FA0030
    movea.l 4(a2),a1                                  ; +$03BE : 226A0004
    move.l #$00000000,(a2)                            ; +$03C2 : 24BC00000000
    move.l #$00000000,4(a2)                           ; +$03C8 : 257C000000000004
    movea.l $0004.w,a6                                ; +$03D0 : 2C780004
    jsr -690(a6)                                      ; +$03D4 : 4EAEFD4E
    bra.w L_005B92                                    ; +$03D8 : 60000006
L_005B8E:
    jsr -78(a6)                                       ; +$03DC : 4EAEFFB2
L_005B92:
    movea.l (a7)+,a6                                  ; +$03E0 : 2C5F
    movea.l (a7)+,a2                                  ; +$03E2 : 245F
    movea.l (a7)+,a0                                  ; +$03E4 : 205F
    move.l (a7)+,d1                                   ; +$03E6 : 221F
    move.l (a7)+,d0                                   ; +$03E8 : 201F
    rts                                               ; +$03EA : 4E75
L_005B9E:
    dcb.b 8,0
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 50 : aga plot --------
Entry_50:
Aga_Plot:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l #$00000000,d3                              ; +$000A : 263C00000000
    tst.l d5                                          ; +$0010 : 4A85
    bmi.w L_005D5E                                    ; +$0012 : 6B0001A0
    tst.l d6                                          ; +$0016 : 4A86
    bmi.w L_005D5E                                    ; +$0018 : 6B00019A
    tst.l d7                                          ; +$001C : 4A87
    bmi.w L_005D5E                                    ; +$001E : 6B000194
    movea.l 456(a5),a4                                ; +$0022 : 286D01C8
    move.l a4,d0                                      ; +$0026 : 200C
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_005D5E                                    ; +$002A : 67000188
    move.l (a4),d0                                    ; +$002E : 2014
    tst.l d0                                          ; +$0030 : 4A80
    beq.w L_005D5E                                    ; +$0032 : 67000180
    move.l 8(a4),d0                                   ; +$0036 : 202C0008
    tst.l d0                                          ; +$003A : 4A80
    beq.w L_005D5E                                    ; +$003C : 67000176
    move.l 32(a4),d0                                  ; +$0040 : 202C0020
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_005D5E                                    ; +$0046 : 6700016C
    move.l 12(a4),d0                                  ; +$004A : 202C000C
    tst.l d0                                          ; +$004E : 4A80
    ble.w L_005D5E                                    ; +$0050 : 6F000162
    cmpi.l #$00007FFF,d0                              ; +$0054 : 0C8000007FFF
    bgt.w L_005D5E                                    ; +$005A : 6E000158
    cmp.l d0,d5                                       ; +$005E : BA80
    bge.w L_005D5E                                    ; +$0060 : 6C000152
    move.l 16(a4),d0                                  ; +$0064 : 202C0010
    tst.l d0                                          ; +$0068 : 4A80
    ble.w L_005D5E                                    ; +$006A : 6F000148
    cmpi.l #$00007FFF,d0                              ; +$006E : 0C8000007FFF
    bgt.w L_005D5E                                    ; +$0074 : 6E00013E
    cmp.l d0,d6                                       ; +$0078 : BC80
    bge.w L_005D5E                                    ; +$007A : 6C000138
    move.l 28(a4),d0                                  ; +$007E : 202C001C
    tst.l d0                                          ; +$0082 : 4A80
    ble.w L_005D5E                                    ; +$0084 : 6F00012E
    cmpi.l #$00000008,d0                              ; +$0088 : 0C8000000008
    bgt.w L_005D5E                                    ; +$008E : 6E000124
    move.l #$00000001,d1                              ; +$0092 : 223C00000001
L_005C42:
    lsl.l #1,d1                                       ; +$0098 : E389
    subq.l #1,d0                                      ; +$009A : 5380
    bne.w L_005C42                                    ; +$009C : 6600FFFA
    cmp.l d1,d7                                       ; +$00A0 : BE81
    bcc.w L_005D5E                                    ; +$00A2 : 64000110
    movea.l 32(a4),a2                                 ; +$00A6 : 246C0020
    move.l 8(a2),d0                                   ; +$00AA : 202A0008
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_005C6E                                    ; +$00B0 : 67000012
    cmpi.l #$00000001,d0                              ; +$00B4 : 0C8000000001
    bne.w L_005D5E                                    ; +$00BA : 660000F8
    movea.l (a2),a0                                   ; +$00BE : 2052
    bra.w L_005C72                                    ; +$00C0 : 60000006
L_005C6E:
    movea.l 4(a2),a0                                  ; +$00C4 : 206A0004
L_005C72:
    move.l a0,d0                                      ; +$00C8 : 2008
    tst.l d0                                          ; +$00CA : 4A80
    beq.w L_005D5E                                    ; +$00CC : 670000E6
    movea.l (a0),a0                                   ; +$00D0 : 2050
    move.l a0,d0                                      ; +$00D2 : 2008
    tst.l d0                                          ; +$00D4 : 4A80
    beq.w L_005D5E                                    ; +$00D6 : 670000DC
    move.l a0,d2                                      ; +$00DA : 2408
    move.l #$00000000,d1                              ; +$00DC : 223C00000000
    move.w (a0),d1                                    ; +$00E2 : 3210
    lsl.l #3,d1                                       ; +$00E4 : E789
    cmp.l 12(a4),d1                                   ; +$00E6 : B2AC000C
    blt.w L_005D5E                                    ; +$00EA : 6D0000C8
    move.l #$00000000,d1                              ; +$00EE : 223C00000000
    move.w 2(a0),d1                                   ; +$00F4 : 32280002
    cmp.l 16(a4),d1                                   ; +$00F8 : B2AC0010
    blt.w L_005D5E                                    ; +$00FC : 6D0000B6
    move.l #$00000000,d1                              ; +$0100 : 223C00000000
    move.b 5(a0),d1                                   ; +$0106 : 12280005
    cmp.l 28(a4),d1                                   ; +$010A : B2AC001C
    bne.w L_005D5E                                    ; +$010E : 660000A4
    move.l d1,d0                                      ; +$0112 : 2001
    movea.l a0,a1                                     ; +$0114 : 2248
    addq.l #8,a1                                      ; +$0116 : 5089
L_005CC2:
    move.l (a1)+,d1                                   ; +$0118 : 2219
    tst.l d1                                          ; +$011A : 4A81
    beq.w L_005D5E                                    ; +$011C : 67000096
    cmpi.l #$FFFFFFFF,d1                              ; +$0120 : 0C81FFFFFFFF
    beq.w L_005D5E                                    ; +$0126 : 6700008C
    subq.l #1,d0                                      ; +$012A : 5380
    bne.w L_005CC2                                    ; +$012C : 6600FFEA
    movea.l 32(a4),a0                                 ; +$0130 : 206C0020
    move.l 20(a0),d0                                  ; +$0134 : 20280014
    andi.l #$00000001,d0                              ; +$0138 : 028000000001
    beq.w L_005D18                                    ; +$013E : 6700002E
    movea.l 12(a0),a0                                 ; +$0142 : 2068000C
    move.l a0,d0                                      ; +$0146 : 2008
    tst.l d0                                          ; +$0148 : 4A80
    beq.w L_005D5E                                    ; +$014A : 67000068
    movea.l $0004.w,a6                                ; +$014E : 2C780004
    jsr -372(a6)                                      ; +$0152 : 4EAEFE8C
    tst.l d0                                          ; +$0156 : 4A80
    beq.w L_005D5E                                    ; +$0158 : 6700005A
    movea.l 32(a4),a0                                 ; +$015C : 206C0020
    move.l 20(a0),d0                                  ; +$0160 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0164 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$016A : 21400014
L_005D18:
    lea -128(a7),a7                                   ; +$016E : 4FEFFF80
    movea.l a7,a2                                     ; +$0172 : 244F
    movea.l a2,a1                                     ; +$0174 : 224A
    movea.l 8(a4),a6                                  ; +$0176 : 2C6C0008
    jsr -198(a6)                                      ; +$017A : 4EAEFF3A
    move.l d2,4(a2)                                   ; +$017E : 25420004
    movea.l a7,a1                                     ; +$0182 : 224F
    move.l d7,d0                                      ; +$0184 : 2007
    jsr -342(a6)                                      ; +$0186 : 4EAEFEAA
    movea.l a7,a1                                     ; +$018A : 224F
    move.l #$00000000,d0                              ; +$018C : 203C00000000
    jsr -354(a6)                                      ; +$0192 : 4EAEFE9E
    movea.l a7,a1                                     ; +$0196 : 224F
    move.l d5,d0                                      ; +$0198 : 2005
    move.l d6,d1                                      ; +$019A : 2206
    jsr -324(a6)                                      ; +$019C : 4EAEFEBC
    tst.l d0                                          ; +$01A0 : 4A80
    bne.w L_005D56                                    ; +$01A2 : 66000008
    move.l #$00000001,d3                              ; +$01A6 : 263C00000001
L_005D56:
    jsr -228(a6)                                      ; +$01AC : 4EAEFF1C
    lea 128(a7),a7                                    ; +$01B0 : 4FEF0080
L_005D5E:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01B4 : 4CDF77F7
    moveq #0,d2                                       ; +$01B8 : 7400
    rts                                               ; +$01BA : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 51 : aga draw --------
Entry_51:
Aga_Draw:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l (a3)+,d4                                   ; +$000A : 281B
    move.l (a3)+,d2                                   ; +$000C : 241B
    move.l #$00000000,d3                              ; +$000E : 263C00000000
    lea -160(a7),a7                                   ; +$0014 : 4FEFFF60
    cmpi.l #$00007FFF,d2                              ; +$0018 : 0C8200007FFF
    bgt.w L_00610E                                    ; +$001E : 6E000384
    cmpi.l #$FFFF8000,d2                              ; +$0022 : 0C82FFFF8000
    blt.w L_00610E                                    ; +$0028 : 6D00037A
    cmpi.l #$00007FFF,d4                              ; +$002C : 0C8400007FFF
    bgt.w L_00610E                                    ; +$0032 : 6E000370
    cmpi.l #$FFFF8000,d4                              ; +$0036 : 0C84FFFF8000
    blt.w L_00610E                                    ; +$003C : 6D000366
    cmpi.l #$00007FFF,d5                              ; +$0040 : 0C8500007FFF
    bgt.w L_00610E                                    ; +$0046 : 6E00035C
    cmpi.l #$FFFF8000,d5                              ; +$004A : 0C85FFFF8000
    blt.w L_00610E                                    ; +$0050 : 6D000352
    cmpi.l #$00007FFF,d6                              ; +$0054 : 0C8600007FFF
    bgt.w L_00610E                                    ; +$005A : 6E000348
    cmpi.l #$FFFF8000,d6                              ; +$005E : 0C86FFFF8000
    blt.w L_00610E                                    ; +$0064 : 6D00033E
    tst.l d7                                          ; +$0068 : 4A87
    bmi.w L_00610E                                    ; +$006A : 6B000338
    movea.l 456(a5),a4                                ; +$006E : 286D01C8
    move.l a4,d0                                      ; +$0072 : 200C
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_00610E                                    ; +$0076 : 6700032C
    move.l (a4),d0                                    ; +$007A : 2014
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_00610E                                    ; +$007E : 67000324
    move.l 8(a4),d0                                   ; +$0082 : 202C0008
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_00610E                                    ; +$0088 : 6700031A
    move.l 32(a4),d0                                  ; +$008C : 202C0020
    tst.l d0                                          ; +$0090 : 4A80
    beq.w L_00610E                                    ; +$0092 : 67000310
    move.l 12(a4),d0                                  ; +$0096 : 202C000C
    tst.l d0                                          ; +$009A : 4A80
    ble.w L_00610E                                    ; +$009C : 6F000306
    cmpi.l #$00007FFF,d0                              ; +$00A0 : 0C8000007FFF
    bgt.w L_00610E                                    ; +$00A6 : 6E0002FC
    move.l 16(a4),d0                                  ; +$00AA : 202C0010
    tst.l d0                                          ; +$00AE : 4A80
    ble.w L_00610E                                    ; +$00B0 : 6F0002F2
    cmpi.l #$00007FFF,d0                              ; +$00B4 : 0C8000007FFF
    bgt.w L_00610E                                    ; +$00BA : 6E0002E8
    move.l 28(a4),d0                                  ; +$00BE : 202C001C
    tst.l d0                                          ; +$00C2 : 4A80
    ble.w L_00610E                                    ; +$00C4 : 6F0002DE
    cmpi.l #$00000008,d0                              ; +$00C8 : 0C8000000008
    bgt.w L_00610E                                    ; +$00CE : 6E0002D4
    move.l #$00000001,d1                              ; +$00D2 : 223C00000001
L_005E42:
    lsl.l #1,d1                                       ; +$00D8 : E389
    subq.l #1,d0                                      ; +$00DA : 5380
    bne.w L_005E42                                    ; +$00DC : 6600FFFA
    cmp.l d1,d7                                       ; +$00E0 : BE81
    bcc.w L_00610E                                    ; +$00E2 : 640002C0
    tst.l d2                                          ; +$00E6 : 4A82
    bpl.w L_005E5C                                    ; +$00E8 : 6A000008
    tst.l d5                                          ; +$00EC : 4A85
    bmi.w L_00610E                                    ; +$00EE : 6B0002B4
L_005E5C:
    cmp.l 12(a4),d2                                   ; +$00F2 : B4AC000C
    blt.w L_005E6C                                    ; +$00F6 : 6D00000A
    cmp.l 12(a4),d5                                   ; +$00FA : BAAC000C
    bge.w L_00610E                                    ; +$00FE : 6C0002A4
L_005E6C:
    tst.l d4                                          ; +$0102 : 4A84
    bpl.w L_005E78                                    ; +$0104 : 6A000008
    tst.l d6                                          ; +$0108 : 4A86
    bmi.w L_00610E                                    ; +$010A : 6B000298
L_005E78:
    cmp.l 16(a4),d4                                   ; +$010E : B8AC0010
    blt.w L_005E88                                    ; +$0112 : 6D00000A
    cmp.l 16(a4),d6                                   ; +$0116 : BCAC0010
    bge.w L_00610E                                    ; +$011A : 6C000288
L_005E88:
    movea.l 32(a4),a2                                 ; +$011E : 246C0020
    move.l 8(a2),d0                                   ; +$0122 : 202A0008
    tst.l d0                                          ; +$0126 : 4A80
    beq.w L_005EA6                                    ; +$0128 : 67000012
    cmpi.l #$00000001,d0                              ; +$012C : 0C8000000001
    bne.w L_00610E                                    ; +$0132 : 66000270
    movea.l (a2),a0                                   ; +$0136 : 2052
    bra.w L_005EAA                                    ; +$0138 : 60000006
L_005EA6:
    movea.l 4(a2),a0                                  ; +$013C : 206A0004
L_005EAA:
    move.l a0,d0                                      ; +$0140 : 2008
    tst.l d0                                          ; +$0142 : 4A80
    beq.w L_00610E                                    ; +$0144 : 6700025E
    movea.l (a0),a0                                   ; +$0148 : 2050
    move.l a0,d0                                      ; +$014A : 2008
    tst.l d0                                          ; +$014C : 4A80
    beq.w L_00610E                                    ; +$014E : 67000254
    movea.l a0,a2                                     ; +$0152 : 2448
    move.l #$00000000,d1                              ; +$0154 : 223C00000000
    move.w (a0),d1                                    ; +$015A : 3210
    lsl.l #3,d1                                       ; +$015C : E789
    cmp.l 12(a4),d1                                   ; +$015E : B2AC000C
    blt.w L_00610E                                    ; +$0162 : 6D000240
    move.l #$00000000,d1                              ; +$0166 : 223C00000000
    move.w 2(a0),d1                                   ; +$016C : 32280002
    cmp.l 16(a4),d1                                   ; +$0170 : B2AC0010
    blt.w L_00610E                                    ; +$0174 : 6D00022E
    move.l #$00000000,d1                              ; +$0178 : 223C00000000
    move.b 5(a0),d1                                   ; +$017E : 12280005
    cmp.l 28(a4),d1                                   ; +$0182 : B2AC001C
    bne.w L_00610E                                    ; +$0186 : 6600021C
    move.l d1,d0                                      ; +$018A : 2001
    movea.l a0,a1                                     ; +$018C : 2248
    addq.l #8,a1                                      ; +$018E : 5089
L_005EFA:
    move.l (a1)+,d1                                   ; +$0190 : 2219
    tst.l d1                                          ; +$0192 : 4A81
    beq.w L_00610E                                    ; +$0194 : 6700020E
    cmpi.l #$FFFFFFFF,d1                              ; +$0198 : 0C81FFFFFFFF
    beq.w L_00610E                                    ; +$019E : 67000204
    subq.l #1,d0                                      ; +$01A2 : 5380
    bne.w L_005EFA                                    ; +$01A4 : 6600FFEA
    move.l a2,156(a7)                                 ; +$01A8 : 2F4A009C
    tst.l d2                                          ; +$01AC : 4A82
    bmi.w L_005F5A                                    ; +$01AE : 6B000040
    cmp.l 12(a4),d2                                   ; +$01B2 : B4AC000C
    bge.w L_005F5A                                    ; +$01B6 : 6C000038
    tst.l d5                                          ; +$01BA : 4A85
    bmi.w L_005F5A                                    ; +$01BC : 6B000032
    cmp.l 12(a4),d5                                   ; +$01C0 : BAAC000C
    bge.w L_005F5A                                    ; +$01C4 : 6C00002A
    tst.l d4                                          ; +$01C8 : 4A84
    bmi.w L_005F5A                                    ; +$01CA : 6B000024
    cmp.l 16(a4),d4                                   ; +$01CE : B8AC0010
    bge.w L_005F5A                                    ; +$01D2 : 6C00001C
    tst.l d6                                          ; +$01D6 : 4A86
    bmi.w L_005F5A                                    ; +$01D8 : 6B000016
    cmp.l 16(a4),d6                                   ; +$01DC : BCAC0010
    bge.w L_005F5A                                    ; +$01E0 : 6C00000E
    move.l #$00000001,152(a7)                         ; +$01E4 : 2F7C000000010098
    bra.w L_005F62                                    ; +$01EC : 6000000A
L_005F5A:
    move.l #$00000000,152(a7)                         ; +$01F0 : 2F7C000000000098
L_005F62:
    movea.l 32(a4),a0                                 ; +$01F8 : 206C0020
    move.l 20(a0),d0                                  ; +$01FC : 20280014
    andi.l #$00000001,d0                              ; +$0200 : 028000000001
    beq.w L_005FA0                                    ; +$0206 : 6700002E
    movea.l 12(a0),a0                                 ; +$020A : 2068000C
    move.l a0,d0                                      ; +$020E : 2008
    tst.l d0                                          ; +$0210 : 4A80
    beq.w L_00610E                                    ; +$0212 : 67000190
    movea.l $0004.w,a6                                ; +$0216 : 2C780004
    jsr -372(a6)                                      ; +$021A : 4EAEFE8C
    tst.l d0                                          ; +$021E : 4A80
    beq.w L_00610E                                    ; +$0220 : 67000182
    movea.l 32(a4),a0                                 ; +$0224 : 206C0020
    move.l 20(a0),d0                                  ; +$0228 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$022C : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$0232 : 21400014
L_005FA0:
    movea.l a7,a2                                     ; +$0236 : 244F
    movea.l a2,a1                                     ; +$0238 : 224A
    movea.l 8(a4),a6                                  ; +$023A : 2C6C0008
    jsr -198(a6)                                      ; +$023E : 4EAEFF3A
    move.l 156(a7),4(a2)                              ; +$0242 : 256F009C0004
    movea.l a2,a1                                     ; +$0248 : 224A
    move.l d7,d0                                      ; +$024A : 2007
    jsr -342(a6)                                      ; +$024C : 4EAEFEAA
    movea.l a2,a1                                     ; +$0250 : 224A
    move.l #$00000000,d0                              ; +$0252 : 203C00000000
    jsr -354(a6)                                      ; +$0258 : 4EAEFE9E
    tst.l 152(a7)                                     ; +$025C : 4AAF0098
    beq.w L_006012                                    ; +$0260 : 67000046
    cmp.l d5,d2                                       ; +$0264 : B485
    bne.w L_005FF4                                    ; +$0266 : 66000022
    cmp.l d6,d4                                       ; +$026A : B886
    bne.w L_005FF4                                    ; +$026C : 6600001C
    movea.l a2,a1                                     ; +$0270 : 224A
    move.l d2,d0                                      ; +$0272 : 2002
    move.l d4,d1                                      ; +$0274 : 2204
    jsr -324(a6)                                      ; +$0276 : 4EAEFEBC
    tst.l d0                                          ; +$027A : 4A80
    bne.w L_006102                                    ; +$027C : 6600011A
    move.l #$00000001,d3                              ; +$0280 : 263C00000001
    bra.w L_006102                                    ; +$0286 : 60000110
L_005FF4:
    movea.l a2,a1                                     ; +$028A : 224A
    move.l d2,d0                                      ; +$028C : 2002
    move.l d4,d1                                      ; +$028E : 2204
    jsr -240(a6)                                      ; +$0290 : 4EAEFF10
    movea.l a2,a1                                     ; +$0294 : 224A
    move.l d5,d0                                      ; +$0296 : 2005
    move.l d6,d1                                      ; +$0298 : 2206
    jsr -246(a6)                                      ; +$029A : 4EAEFF0A
    move.l #$00000001,d3                              ; +$029E : 263C00000001
    bra.w L_006102                                    ; +$02A4 : 600000F2
L_006012:
    move.l d5,d0                                      ; +$02A8 : 2005
    sub.l d2,d0                                       ; +$02AA : 9082
    move.l #$00000001,136(a7)                         ; +$02AC : 2F7C000000010088
    tst.l d0                                          ; +$02B4 : 4A80
    bpl.w L_006036                                    ; +$02B6 : 6A000014
    move.l #$FFFFFFFF,136(a7)                         ; +$02BA : 2F7CFFFFFFFF0088
    move.l #$00000000,d1                              ; +$02C2 : 223C00000000
    sub.l d0,d1                                       ; +$02C8 : 9280
    move.l d1,d0                                      ; +$02CA : 2001
L_006036:
    move.l d0,128(a7)                                 ; +$02CC : 2F400080
    move.l d6,d0                                      ; +$02D0 : 2006
    sub.l d4,d0                                       ; +$02D2 : 9084
    move.l #$00000001,140(a7)                         ; +$02D4 : 2F7C00000001008C
    tst.l d0                                          ; +$02DC : 4A80
    bpl.w L_00605E                                    ; +$02DE : 6A000014
    move.l #$FFFFFFFF,140(a7)                         ; +$02E2 : 2F7CFFFFFFFF008C
    move.l #$00000000,d1                              ; +$02EA : 223C00000000
    sub.l d0,d1                                       ; +$02F0 : 9280
    move.l d1,d0                                      ; +$02F2 : 2001
L_00605E:
    move.l d0,132(a7)                                 ; +$02F4 : 2F400084
    move.l 128(a7),d0                                 ; +$02F8 : 202F0080
    sub.l 132(a7),d0                                  ; +$02FC : 90AF0084
    move.l d0,144(a7)                                 ; +$0300 : 2F400090
L_00606E:
    tst.l d2                                          ; +$0304 : 4A82
    bmi.w L_0060A8                                    ; +$0306 : 6B000036
    cmp.l 12(a4),d2                                   ; +$030A : B4AC000C
    bge.w L_0060A8                                    ; +$030E : 6C00002E
    tst.l d4                                          ; +$0312 : 4A84
    bmi.w L_0060A8                                    ; +$0314 : 6B000028
    cmp.l 16(a4),d4                                   ; +$0318 : B8AC0010
    bge.w L_0060A8                                    ; +$031C : 6C000020
    movea.l a2,a1                                     ; +$0320 : 224A
    move.l d2,d0                                      ; +$0322 : 2002
    move.l d4,d1                                      ; +$0324 : 2204
    move.l #$00000002,152(a7)                         ; +$0326 : 2F7C000000020098
    jsr -324(a6)                                      ; +$032E : 4EAEFEBC
    tst.l d0                                          ; +$0332 : 4A80
    bne.w L_0060A8                                    ; +$0334 : 66000008
    move.l #$00000001,d3                              ; +$0338 : 263C00000001
L_0060A8:
    cmp.l d5,d2                                       ; +$033E : B485
    bne.w L_0060B4                                    ; +$0340 : 66000008
    cmp.l d6,d4                                       ; +$0344 : B886
    beq.w L_006102                                    ; +$0346 : 67000050
L_0060B4:
    move.l 144(a7),d0                                 ; +$034A : 202F0090
    lsl.l #1,d0                                       ; +$034E : E388
    move.l d0,148(a7)                                 ; +$0350 : 2F400094
    move.l #$00000000,d1                              ; +$0354 : 223C00000000
    sub.l 132(a7),d1                                  ; +$035A : 92AF0084
    cmp.l d1,d0                                       ; +$035E : B081
    ble.w L_0060E0                                    ; +$0360 : 6F000014
    move.l 144(a7),d0                                 ; +$0364 : 202F0090
    sub.l 132(a7),d0                                  ; +$0368 : 90AF0084
    move.l d0,144(a7)                                 ; +$036C : 2F400090
    move.l 136(a7),d0                                 ; +$0370 : 202F0088
    add.l d0,d2                                       ; +$0374 : D480
L_0060E0:
    move.l 148(a7),d0                                 ; +$0376 : 202F0094
    cmp.l 128(a7),d0                                  ; +$037A : B0AF0080
    bge.w L_0060FE                                    ; +$037E : 6C000014
    move.l 144(a7),d0                                 ; +$0382 : 202F0090
    add.l 128(a7),d0                                  ; +$0386 : D0AF0080
    move.l d0,144(a7)                                 ; +$038A : 2F400090
    move.l 140(a7),d0                                 ; +$038E : 202F008C
    add.l d0,d4                                       ; +$0392 : D880
L_0060FE:
    bra.w L_00606E                                    ; +$0394 : 6000FF6E
L_006102:
    tst.l 152(a7)                                     ; +$0398 : 4AAF0098
    beq.w L_00610E                                    ; +$039C : 67000006
    jsr -228(a6)                                      ; +$03A0 : 4EAEFF1C
L_00610E:
    lea 160(a7),a7                                    ; +$03A4 : 4FEF00A0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$03A8 : 4CDF77F7
    moveq #0,d2                                       ; +$03AC : 7400
    rts                                               ; +$03AE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 52 : aga box --------
Entry_52:
Aga_Box:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d5                                   ; +$0008 : 2A1B
    move.l (a3)+,d4                                   ; +$000A : 281B
    move.l (a3)+,d2                                   ; +$000C : 241B
    move.l #$00000000,d3                              ; +$000E : 263C00000000
    lea -160(a7),a7                                   ; +$0014 : 4FEFFF60
    cmpi.l #$00007FFF,d2                              ; +$0018 : 0C8200007FFF
    bgt.w L_006532                                    ; +$001E : 6E0003F4
    cmpi.l #$FFFF8000,d2                              ; +$0022 : 0C82FFFF8000
    blt.w L_006532                                    ; +$0028 : 6D0003EA
    cmpi.l #$00007FFF,d4                              ; +$002C : 0C8400007FFF
    bgt.w L_006532                                    ; +$0032 : 6E0003E0
    cmpi.l #$FFFF8000,d4                              ; +$0036 : 0C84FFFF8000
    blt.w L_006532                                    ; +$003C : 6D0003D6
    cmpi.l #$00007FFF,d5                              ; +$0040 : 0C8500007FFF
    bgt.w L_006532                                    ; +$0046 : 6E0003CC
    cmpi.l #$FFFF8000,d5                              ; +$004A : 0C85FFFF8000
    blt.w L_006532                                    ; +$0050 : 6D0003C2
    cmpi.l #$00007FFF,d6                              ; +$0054 : 0C8600007FFF
    bgt.w L_006532                                    ; +$005A : 6E0003B8
    cmpi.l #$FFFF8000,d6                              ; +$005E : 0C86FFFF8000
    blt.w L_006532                                    ; +$0064 : 6D0003AE
    tst.l d7                                          ; +$0068 : 4A87
    bmi.w L_006532                                    ; +$006A : 6B0003A8
    cmp.l d5,d2                                       ; +$006E : B485
    ble.w L_006198                                    ; +$0070 : 6F000008
    move.l d2,d0                                      ; +$0074 : 2002
    move.l d5,d2                                      ; +$0076 : 2405
    move.l d0,d5                                      ; +$0078 : 2A00
L_006198:
    cmp.l d6,d4                                       ; +$007A : B886
    ble.w L_0061A4                                    ; +$007C : 6F000008
    move.l d4,d0                                      ; +$0080 : 2004
    move.l d6,d4                                      ; +$0082 : 2806
    move.l d0,d6                                      ; +$0084 : 2C00
L_0061A4:
    movea.l 456(a5),a4                                ; +$0086 : 286D01C8
    move.l a4,d0                                      ; +$008A : 200C
    tst.l d0                                          ; +$008C : 4A80
    beq.w L_006532                                    ; +$008E : 67000384
    move.l (a4),d0                                    ; +$0092 : 2014
    tst.l d0                                          ; +$0094 : 4A80
    beq.w L_006532                                    ; +$0096 : 6700037C
    move.l 8(a4),d0                                   ; +$009A : 202C0008
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_006532                                    ; +$00A0 : 67000372
    move.l 32(a4),d0                                  ; +$00A4 : 202C0020
    tst.l d0                                          ; +$00A8 : 4A80
    beq.w L_006532                                    ; +$00AA : 67000368
    move.l 12(a4),d0                                  ; +$00AE : 202C000C
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_006532                                    ; +$00B4 : 6F00035E
    cmpi.l #$00007FFF,d0                              ; +$00B8 : 0C8000007FFF
    bgt.w L_006532                                    ; +$00BE : 6E000354
    move.l 16(a4),d0                                  ; +$00C2 : 202C0010
    tst.l d0                                          ; +$00C6 : 4A80
    ble.w L_006532                                    ; +$00C8 : 6F00034A
    cmpi.l #$00007FFF,d0                              ; +$00CC : 0C8000007FFF
    bgt.w L_006532                                    ; +$00D2 : 6E000340
    move.l 28(a4),d0                                  ; +$00D6 : 202C001C
    tst.l d0                                          ; +$00DA : 4A80
    ble.w L_006532                                    ; +$00DC : 6F000336
    cmpi.l #$00000008,d0                              ; +$00E0 : 0C8000000008
    bgt.w L_006532                                    ; +$00E6 : 6E00032C
    move.l #$00000001,d1                              ; +$00EA : 223C00000001
L_00620E:
    lsl.l #1,d1                                       ; +$00F0 : E389
    subq.l #1,d0                                      ; +$00F2 : 5380
    bne.w L_00620E                                    ; +$00F4 : 6600FFFA
    cmp.l d1,d7                                       ; +$00F8 : BE81
    bcc.w L_006532                                    ; +$00FA : 64000318
    tst.l d5                                          ; +$00FE : 4A85
    bmi.w L_006532                                    ; +$0100 : 6B000312
    cmp.l 12(a4),d2                                   ; +$0104 : B4AC000C
    bge.w L_006532                                    ; +$0108 : 6C00030A
    tst.l d6                                          ; +$010C : 4A86
    bmi.w L_006532                                    ; +$010E : 6B000304
    cmp.l 16(a4),d4                                   ; +$0112 : B8AC0010
    bge.w L_006532                                    ; +$0116 : 6C0002FC
    movea.l 32(a4),a2                                 ; +$011A : 246C0020
    move.l 8(a2),d0                                   ; +$011E : 202A0008
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_006256                                    ; +$0124 : 67000012
    cmpi.l #$00000001,d0                              ; +$0128 : 0C8000000001
    bne.w L_006532                                    ; +$012E : 660002E4
    movea.l (a2),a0                                   ; +$0132 : 2052
    bra.w L_00625A                                    ; +$0134 : 60000006
L_006256:
    movea.l 4(a2),a0                                  ; +$0138 : 206A0004
L_00625A:
    move.l a0,d0                                      ; +$013C : 2008
    tst.l d0                                          ; +$013E : 4A80
    beq.w L_006532                                    ; +$0140 : 670002D2
    movea.l (a0),a0                                   ; +$0144 : 2050
    move.l a0,d0                                      ; +$0146 : 2008
    tst.l d0                                          ; +$0148 : 4A80
    beq.w L_006532                                    ; +$014A : 670002C8
    movea.l a0,a2                                     ; +$014E : 2448
    move.l #$00000000,d1                              ; +$0150 : 223C00000000
    move.w (a0),d1                                    ; +$0156 : 3210
    lsl.l #3,d1                                       ; +$0158 : E789
    cmp.l 12(a4),d1                                   ; +$015A : B2AC000C
    blt.w L_006532                                    ; +$015E : 6D0002B4
    move.l #$00000000,d1                              ; +$0162 : 223C00000000
    move.w 2(a0),d1                                   ; +$0168 : 32280002
    cmp.l 16(a4),d1                                   ; +$016C : B2AC0010
    blt.w L_006532                                    ; +$0170 : 6D0002A2
    move.l #$00000000,d1                              ; +$0174 : 223C00000000
    move.b 5(a0),d1                                   ; +$017A : 12280005
    cmp.l 28(a4),d1                                   ; +$017E : B2AC001C
    bne.w L_006532                                    ; +$0182 : 66000290
    move.l d1,d0                                      ; +$0186 : 2001
    movea.l a0,a1                                     ; +$0188 : 2248
    addq.l #8,a1                                      ; +$018A : 5089
L_0062AA:
    move.l (a1)+,d1                                   ; +$018C : 2219
    tst.l d1                                          ; +$018E : 4A81
    beq.w L_006532                                    ; +$0190 : 67000282
    cmpi.l #$FFFFFFFF,d1                              ; +$0194 : 0C81FFFFFFFF
    beq.w L_006532                                    ; +$019A : 67000278
    subq.l #1,d0                                      ; +$019E : 5380
    bne.w L_0062AA                                    ; +$01A0 : 6600FFEA
    move.l a2,156(a7)                                 ; +$01A4 : 2F4A009C
    move.l d2,128(a7)                                 ; +$01A8 : 2F420080
    tst.l d2                                          ; +$01AC : 4A82
    bpl.w L_0062D8                                    ; +$01AE : 6A00000A
    move.l #$00000000,128(a7)                         ; +$01B2 : 2F7C000000000080
L_0062D8:
    move.l d5,132(a7)                                 ; +$01BA : 2F450084
    cmp.l 12(a4),d5                                   ; +$01BE : BAAC000C
    blt.w L_0062EE                                    ; +$01C2 : 6D00000C
    move.l 12(a4),d0                                  ; +$01C6 : 202C000C
    subq.l #1,d0                                      ; +$01CA : 5380
    move.l d0,132(a7)                                 ; +$01CC : 2F400084
L_0062EE:
    move.l d4,136(a7)                                 ; +$01D0 : 2F440088
    tst.l d4                                          ; +$01D4 : 4A84
    bpl.w L_006300                                    ; +$01D6 : 6A00000A
    move.l #$00000000,136(a7)                         ; +$01DA : 2F7C000000000088
L_006300:
    move.l d6,140(a7)                                 ; +$01E2 : 2F46008C
    cmp.l 16(a4),d6                                   ; +$01E6 : BCAC0010
    blt.w L_006316                                    ; +$01EA : 6D00000C
    move.l 16(a4),d0                                  ; +$01EE : 202C0010
    subq.l #1,d0                                      ; +$01F2 : 5380
    move.l d0,140(a7)                                 ; +$01F4 : 2F40008C
L_006316:
    move.l #$00000000,152(a7)                         ; +$01F8 : 2F7C000000000098
    tst.l d2                                          ; +$0200 : 4A82
    bmi.w L_006334                                    ; +$0202 : 6B000012
    cmp.l 12(a4),d2                                   ; +$0206 : B4AC000C
    bge.w L_006334                                    ; +$020A : 6C00000A
    move.l #$00000001,152(a7)                         ; +$020E : 2F7C000000010098
L_006334:
    tst.l d5                                          ; +$0216 : 4A85
    bmi.w L_00634A                                    ; +$0218 : 6B000012
    cmp.l 12(a4),d5                                   ; +$021C : BAAC000C
    bge.w L_00634A                                    ; +$0220 : 6C00000A
    move.l #$00000001,152(a7)                         ; +$0224 : 2F7C000000010098
L_00634A:
    tst.l d4                                          ; +$022C : 4A84
    bmi.w L_006360                                    ; +$022E : 6B000012
    cmp.l 16(a4),d4                                   ; +$0232 : B8AC0010
    bge.w L_006360                                    ; +$0236 : 6C00000A
    move.l #$00000001,152(a7)                         ; +$023A : 2F7C000000010098
L_006360:
    tst.l d6                                          ; +$0242 : 4A86
    bmi.w L_006376                                    ; +$0244 : 6B000012
    cmp.l 16(a4),d6                                   ; +$0248 : BCAC0010
    bge.w L_006376                                    ; +$024C : 6C00000A
    move.l #$00000001,152(a7)                         ; +$0250 : 2F7C000000010098
L_006376:
    tst.l 152(a7)                                     ; +$0258 : 4AAF0098
    beq.w L_006532                                    ; +$025C : 670001B6
    movea.l 32(a4),a0                                 ; +$0260 : 206C0020
    move.l 20(a0),d0                                  ; +$0264 : 20280014
    andi.l #$00000001,d0                              ; +$0268 : 028000000001
    beq.w L_0063BC                                    ; +$026E : 6700002E
    movea.l 12(a0),a0                                 ; +$0272 : 2068000C
    move.l a0,d0                                      ; +$0276 : 2008
    tst.l d0                                          ; +$0278 : 4A80
    beq.w L_006532                                    ; +$027A : 67000198
    movea.l $0004.w,a6                                ; +$027E : 2C780004
    jsr -372(a6)                                      ; +$0282 : 4EAEFE8C
    tst.l d0                                          ; +$0286 : 4A80
    beq.w L_006532                                    ; +$0288 : 6700018A
    movea.l 32(a4),a0                                 ; +$028C : 206C0020
    move.l 20(a0),d0                                  ; +$0290 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0294 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$029A : 21400014
L_0063BC:
    movea.l a7,a2                                     ; +$029E : 244F
    movea.l a2,a1                                     ; +$02A0 : 224A
    movea.l 8(a4),a6                                  ; +$02A2 : 2C6C0008
    jsr -198(a6)                                      ; +$02A6 : 4EAEFF3A
    move.l 156(a7),4(a2)                              ; +$02AA : 256F009C0004
    movea.l a2,a1                                     ; +$02B0 : 224A
    move.l d7,d0                                      ; +$02B2 : 2007
    jsr -342(a6)                                      ; +$02B4 : 4EAEFEAA
    movea.l a2,a1                                     ; +$02B8 : 224A
    move.l #$00000000,d0                              ; +$02BA : 203C00000000
    jsr -354(a6)                                      ; +$02C0 : 4EAEFE9E
    tst.l d4                                          ; +$02C4 : 4A84
    bmi.w L_006432                                    ; +$02C6 : 6B00004C
    cmp.l 16(a4),d4                                   ; +$02CA : B8AC0010
    bge.w L_006432                                    ; +$02CE : 6C000044
    move.l 128(a7),d0                                 ; +$02D2 : 202F0080
    cmp.l 132(a7),d0                                  ; +$02D6 : B0AF0084
    bne.w L_006414                                    ; +$02DA : 6600001A
    movea.l a2,a1                                     ; +$02DE : 224A
    move.l d4,d1                                      ; +$02E0 : 2204
    jsr -324(a6)                                      ; +$02E2 : 4EAEFEBC
    tst.l d0                                          ; +$02E6 : 4A80
    bne.w L_006432                                    ; +$02E8 : 6600002A
    move.l #$00000001,d3                              ; +$02EC : 263C00000001
    bra.w L_006432                                    ; +$02F2 : 60000020
L_006414:
    movea.l a2,a1                                     ; +$02F6 : 224A
    move.l 128(a7),d0                                 ; +$02F8 : 202F0080
    move.l d4,d1                                      ; +$02FC : 2204
    jsr -240(a6)                                      ; +$02FE : 4EAEFF10
    movea.l a2,a1                                     ; +$0302 : 224A
    move.l 132(a7),d0                                 ; +$0304 : 202F0084
    move.l d4,d1                                      ; +$0308 : 2204
    jsr -246(a6)                                      ; +$030A : 4EAEFF0A
    move.l #$00000001,d3                              ; +$030E : 263C00000001
L_006432:
    cmp.l d4,d6                                       ; +$0314 : BC84
    beq.w L_006488                                    ; +$0316 : 67000052
    tst.l d6                                          ; +$031A : 4A86
    bmi.w L_006488                                    ; +$031C : 6B00004C
    cmp.l 16(a4),d6                                   ; +$0320 : BCAC0010
    bge.w L_006488                                    ; +$0324 : 6C000044
    move.l 128(a7),d0                                 ; +$0328 : 202F0080
    cmp.l 132(a7),d0                                  ; +$032C : B0AF0084
    bne.w L_00646A                                    ; +$0330 : 6600001A
    movea.l a2,a1                                     ; +$0334 : 224A
    move.l d6,d1                                      ; +$0336 : 2206
    jsr -324(a6)                                      ; +$0338 : 4EAEFEBC
    tst.l d0                                          ; +$033C : 4A80
    bne.w L_006488                                    ; +$033E : 6600002A
    move.l #$00000001,d3                              ; +$0342 : 263C00000001
    bra.w L_006488                                    ; +$0348 : 60000020
L_00646A:
    movea.l a2,a1                                     ; +$034C : 224A
    move.l 128(a7),d0                                 ; +$034E : 202F0080
    move.l d6,d1                                      ; +$0352 : 2206
    jsr -240(a6)                                      ; +$0354 : 4EAEFF10
    movea.l a2,a1                                     ; +$0358 : 224A
    move.l 132(a7),d0                                 ; +$035A : 202F0084
    move.l d6,d1                                      ; +$035E : 2206
    jsr -246(a6)                                      ; +$0360 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$0364 : 263C00000001
L_006488:
    tst.l d2                                          ; +$036A : 4A82
    bmi.w L_0064D8                                    ; +$036C : 6B00004C
    cmp.l 12(a4),d2                                   ; +$0370 : B4AC000C
    bge.w L_0064D8                                    ; +$0374 : 6C000044
    move.l 136(a7),d1                                 ; +$0378 : 222F0088
    cmp.l 140(a7),d1                                  ; +$037C : B2AF008C
    bne.w L_0064BA                                    ; +$0380 : 6600001A
    movea.l a2,a1                                     ; +$0384 : 224A
    move.l d2,d0                                      ; +$0386 : 2002
    jsr -324(a6)                                      ; +$0388 : 4EAEFEBC
    tst.l d0                                          ; +$038C : 4A80
    bne.w L_0064D8                                    ; +$038E : 6600002A
    move.l #$00000001,d3                              ; +$0392 : 263C00000001
    bra.w L_0064D8                                    ; +$0398 : 60000020
L_0064BA:
    movea.l a2,a1                                     ; +$039C : 224A
    move.l d2,d0                                      ; +$039E : 2002
    move.l 136(a7),d1                                 ; +$03A0 : 222F0088
    jsr -240(a6)                                      ; +$03A4 : 4EAEFF10
    movea.l a2,a1                                     ; +$03A8 : 224A
    move.l d2,d0                                      ; +$03AA : 2002
    move.l 140(a7),d1                                 ; +$03AC : 222F008C
    jsr -246(a6)                                      ; +$03B0 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$03B4 : 263C00000001
L_0064D8:
    cmp.l d2,d5                                       ; +$03BA : BA82
    beq.w L_00652E                                    ; +$03BC : 67000052
    tst.l d5                                          ; +$03C0 : 4A85
    bmi.w L_00652E                                    ; +$03C2 : 6B00004C
    cmp.l 12(a4),d5                                   ; +$03C6 : BAAC000C
    bge.w L_00652E                                    ; +$03CA : 6C000044
    move.l 136(a7),d1                                 ; +$03CE : 222F0088
    cmp.l 140(a7),d1                                  ; +$03D2 : B2AF008C
    bne.w L_006510                                    ; +$03D6 : 6600001A
    movea.l a2,a1                                     ; +$03DA : 224A
    move.l d5,d0                                      ; +$03DC : 2005
    jsr -324(a6)                                      ; +$03DE : 4EAEFEBC
    tst.l d0                                          ; +$03E2 : 4A80
    bne.w L_00652E                                    ; +$03E4 : 6600002A
    move.l #$00000001,d3                              ; +$03E8 : 263C00000001
    bra.w L_00652E                                    ; +$03EE : 60000020
L_006510:
    movea.l a2,a1                                     ; +$03F2 : 224A
    move.l d5,d0                                      ; +$03F4 : 2005
    move.l 136(a7),d1                                 ; +$03F6 : 222F0088
    jsr -240(a6)                                      ; +$03FA : 4EAEFF10
    movea.l a2,a1                                     ; +$03FE : 224A
    move.l d5,d0                                      ; +$0400 : 2005
    move.l 140(a7),d1                                 ; +$0402 : 222F008C
    jsr -246(a6)                                      ; +$0406 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$040A : 263C00000001
L_00652E:
    jsr -228(a6)                                      ; +$0410 : 4EAEFF1C
L_006532:
    lea 160(a7),a7                                    ; +$0414 : 4FEF00A0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0418 : 4CDF77F7
    moveq #0,d2                                       ; +$041C : 7400
    rts                                               ; +$041E : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 53 : aga circle --------
Entry_53:
Aga_Circle:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l (a3)+,d6                                   ; +$0006 : 2C1B
    move.l (a3)+,d4                                   ; +$0008 : 281B
    move.l (a3)+,d2                                   ; +$000A : 241B
    move.l #$00000000,d3                              ; +$000C : 263C00000000
    lea -160(a7),a7                                   ; +$0012 : 4FEFFF60
    cmpi.l #$00007FFF,d2                              ; +$0016 : 0C8200007FFF
    bgt.w L_0069C0                                    ; +$001C : 6E000460
    cmpi.l #$FFFF8000,d2                              ; +$0020 : 0C82FFFF8000
    blt.w L_0069C0                                    ; +$0026 : 6D000456
    cmpi.l #$00007FFF,d4                              ; +$002A : 0C8400007FFF
    bgt.w L_0069C0                                    ; +$0030 : 6E00044C
    cmpi.l #$FFFF8000,d4                              ; +$0034 : 0C84FFFF8000
    blt.w L_0069C0                                    ; +$003A : 6D000442
    cmpi.l #$00007FFF,d6                              ; +$003E : 0C8600007FFF
    bgt.w L_0069C0                                    ; +$0044 : 6E000438
    cmpi.l #$FFFF8000,d6                              ; +$0048 : 0C86FFFF8000
    blt.w L_0069C0                                    ; +$004E : 6D00042E
    tst.l d6                                          ; +$0052 : 4A86
    bmi.w L_0069C0                                    ; +$0054 : 6B000428
    tst.l d7                                          ; +$0058 : 4A87
    bmi.w L_0069C0                                    ; +$005A : 6B000422
    movea.l 456(a5),a4                                ; +$005E : 286D01C8
    move.l a4,d0                                      ; +$0062 : 200C
    tst.l d0                                          ; +$0064 : 4A80
    beq.w L_0069C0                                    ; +$0066 : 67000416
    move.l (a4),d0                                    ; +$006A : 2014
    tst.l d0                                          ; +$006C : 4A80
    beq.w L_0069C0                                    ; +$006E : 6700040E
    move.l 8(a4),d0                                   ; +$0072 : 202C0008
    tst.l d0                                          ; +$0076 : 4A80
    beq.w L_0069C0                                    ; +$0078 : 67000404
    move.l 32(a4),d0                                  ; +$007C : 202C0020
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_0069C0                                    ; +$0082 : 670003FA
    move.l 12(a4),d0                                  ; +$0086 : 202C000C
    tst.l d0                                          ; +$008A : 4A80
    ble.w L_0069C0                                    ; +$008C : 6F0003F0
    cmpi.l #$00007FFF,d0                              ; +$0090 : 0C8000007FFF
    bgt.w L_0069C0                                    ; +$0096 : 6E0003E6
    move.l 16(a4),d0                                  ; +$009A : 202C0010
    tst.l d0                                          ; +$009E : 4A80
    ble.w L_0069C0                                    ; +$00A0 : 6F0003DC
    cmpi.l #$00007FFF,d0                              ; +$00A4 : 0C8000007FFF
    bgt.w L_0069C0                                    ; +$00AA : 6E0003D2
    move.l 28(a4),d0                                  ; +$00AE : 202C001C
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_0069C0                                    ; +$00B4 : 6F0003C8
    cmpi.l #$00000008,d0                              ; +$00B8 : 0C8000000008
    bgt.w L_0069C0                                    ; +$00BE : 6E0003BE
    move.l #$00000001,d1                              ; +$00C2 : 223C00000001
L_00660A:
    lsl.l #1,d1                                       ; +$00C8 : E389
    subq.l #1,d0                                      ; +$00CA : 5380
    bne.w L_00660A                                    ; +$00CC : 6600FFFA
    cmp.l d1,d7                                       ; +$00D0 : BE81
    bcc.w L_0069C0                                    ; +$00D2 : 640003AA
    move.l d2,d0                                      ; +$00D6 : 2002
    add.l d6,d0                                       ; +$00D8 : D086
    tst.l d0                                          ; +$00DA : 4A80
    bmi.w L_0069C0                                    ; +$00DC : 6B0003A0
    move.l d2,d0                                      ; +$00E0 : 2002
    sub.l d6,d0                                       ; +$00E2 : 9086
    cmp.l 12(a4),d0                                   ; +$00E4 : B0AC000C
    bge.w L_0069C0                                    ; +$00E8 : 6C000394
    move.l d4,d0                                      ; +$00EC : 2004
    add.l d6,d0                                       ; +$00EE : D086
    tst.l d0                                          ; +$00F0 : 4A80
    bmi.w L_0069C0                                    ; +$00F2 : 6B00038A
    move.l d4,d0                                      ; +$00F6 : 2004
    sub.l d6,d0                                       ; +$00F8 : 9086
    cmp.l 16(a4),d0                                   ; +$00FA : B0AC0010
    bge.w L_0069C0                                    ; +$00FE : 6C00037E
    movea.l 32(a4),a2                                 ; +$0102 : 246C0020
    move.l 8(a2),d0                                   ; +$0106 : 202A0008
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_006662                                    ; +$010C : 67000012
    cmpi.l #$00000001,d0                              ; +$0110 : 0C8000000001
    bne.w L_0069C0                                    ; +$0116 : 66000366
    movea.l (a2),a0                                   ; +$011A : 2052
    bra.w L_006666                                    ; +$011C : 60000006
L_006662:
    movea.l 4(a2),a0                                  ; +$0120 : 206A0004
L_006666:
    move.l a0,d0                                      ; +$0124 : 2008
    tst.l d0                                          ; +$0126 : 4A80
    beq.w L_0069C0                                    ; +$0128 : 67000354
    movea.l (a0),a0                                   ; +$012C : 2050
    move.l a0,d0                                      ; +$012E : 2008
    tst.l d0                                          ; +$0130 : 4A80
    beq.w L_0069C0                                    ; +$0132 : 6700034A
    movea.l a0,a2                                     ; +$0136 : 2448
    move.l #$00000000,d1                              ; +$0138 : 223C00000000
    move.w (a0),d1                                    ; +$013E : 3210
    lsl.l #3,d1                                       ; +$0140 : E789
    cmp.l 12(a4),d1                                   ; +$0142 : B2AC000C
    blt.w L_0069C0                                    ; +$0146 : 6D000336
    move.l #$00000000,d1                              ; +$014A : 223C00000000
    move.w 2(a0),d1                                   ; +$0150 : 32280002
    cmp.l 16(a4),d1                                   ; +$0154 : B2AC0010
    blt.w L_0069C0                                    ; +$0158 : 6D000324
    move.l #$00000000,d1                              ; +$015C : 223C00000000
    move.b 5(a0),d1                                   ; +$0162 : 12280005
    cmp.l 28(a4),d1                                   ; +$0166 : B2AC001C
    bne.w L_0069C0                                    ; +$016A : 66000312
    move.l d1,d0                                      ; +$016E : 2001
    movea.l a0,a1                                     ; +$0170 : 2248
    addq.l #8,a1                                      ; +$0172 : 5089
L_0066B6:
    move.l (a1)+,d1                                   ; +$0174 : 2219
    tst.l d1                                          ; +$0176 : 4A81
    beq.w L_0069C0                                    ; +$0178 : 67000304
    cmpi.l #$FFFFFFFF,d1                              ; +$017C : 0C81FFFFFFFF
    beq.w L_0069C0                                    ; +$0182 : 670002FA
    subq.l #1,d0                                      ; +$0186 : 5380
    bne.w L_0066B6                                    ; +$0188 : 6600FFEA
    move.l a2,156(a7)                                 ; +$018C : 2F4A009C
    movea.l 32(a4),a0                                 ; +$0190 : 206C0020
    move.l 20(a0),d0                                  ; +$0194 : 20280014
    andi.l #$00000001,d0                              ; +$0198 : 028000000001
    beq.w L_006710                                    ; +$019E : 6700002E
    movea.l 12(a0),a0                                 ; +$01A2 : 2068000C
    move.l a0,d0                                      ; +$01A6 : 2008
    tst.l d0                                          ; +$01A8 : 4A80
    beq.w L_0069C0                                    ; +$01AA : 670002D2
    movea.l $0004.w,a6                                ; +$01AE : 2C780004
    jsr -372(a6)                                      ; +$01B2 : 4EAEFE8C
    tst.l d0                                          ; +$01B6 : 4A80
    beq.w L_0069C0                                    ; +$01B8 : 670002C4
    movea.l 32(a4),a0                                 ; +$01BC : 206C0020
    move.l 20(a0),d0                                  ; +$01C0 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$01C4 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$01CA : 21400014
L_006710:
    movea.l a7,a2                                     ; +$01CE : 244F
    movea.l a2,a1                                     ; +$01D0 : 224A
    movea.l 8(a4),a6                                  ; +$01D2 : 2C6C0008
    jsr -198(a6)                                      ; +$01D6 : 4EAEFF3A
    move.l 156(a7),4(a2)                              ; +$01DA : 256F009C0004
    movea.l a2,a1                                     ; +$01E0 : 224A
    move.l d7,d0                                      ; +$01E2 : 2007
    jsr -342(a6)                                      ; +$01E4 : 4EAEFEAA
    movea.l a2,a1                                     ; +$01E8 : 224A
    move.l #$00000000,d0                              ; +$01EA : 203C00000000
    jsr -354(a6)                                      ; +$01F0 : 4EAEFE9E
    move.l #$00000000,136(a7)                         ; +$01F4 : 2F7C000000000088
    tst.l d6                                          ; +$01FC : 4A86
    bne.w L_006766                                    ; +$01FE : 66000024
    move.l d2,d0                                      ; +$0202 : 2002
    move.l d4,d1                                      ; +$0204 : 2204
    move.l #$00000001,136(a7)                         ; +$0206 : 2F7C000000010088
    movea.l a2,a1                                     ; +$020E : 224A
    jsr -324(a6)                                      ; +$0210 : 4EAEFEBC
    tst.l d0                                          ; +$0214 : 4A80
    bne.w L_0069B4                                    ; +$0216 : 6600025A
    move.l #$00000001,d3                              ; +$021A : 263C00000001
    bra.w L_0069B4                                    ; +$0220 : 60000250
L_006766:
    move.l d6,d5                                      ; +$0224 : 2A06
    move.l #$00000000,128(a7)                         ; +$0226 : 2F7C000000000080
    move.l #$00000001,d0                              ; +$022E : 203C00000001
    sub.l d6,d0                                       ; +$0234 : 9086
    move.l d0,132(a7)                                 ; +$0236 : 2F400084
L_00677C:
    move.l d2,d0                                      ; +$023A : 2002
    add.l d5,d0                                       ; +$023C : D085
    tst.l d0                                          ; +$023E : 4A80
    bmi.w L_0067BC                                    ; +$0240 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0244 : B0AC000C
    bge.w L_0067BC                                    ; +$0248 : 6C000030
    move.l d4,d1                                      ; +$024C : 2204
    add.l 128(a7),d1                                  ; +$024E : D2AF0080
    tst.l d1                                          ; +$0252 : 4A81
    bmi.w L_0067BC                                    ; +$0254 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0258 : B2AC0010
    bge.w L_0067BC                                    ; +$025C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0260 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0268 : 224A
    jsr -324(a6)                                      ; +$026A : 4EAEFEBC
    tst.l d0                                          ; +$026E : 4A80
    bne.w L_0067BC                                    ; +$0270 : 66000008
    move.l #$00000001,d3                              ; +$0274 : 263C00000001
L_0067BC:
    move.l d2,d0                                      ; +$027A : 2002
    sub.l d5,d0                                       ; +$027C : 9085
    tst.l d0                                          ; +$027E : 4A80
    bmi.w L_0067FC                                    ; +$0280 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0284 : B0AC000C
    bge.w L_0067FC                                    ; +$0288 : 6C000030
    move.l d4,d1                                      ; +$028C : 2204
    add.l 128(a7),d1                                  ; +$028E : D2AF0080
    tst.l d1                                          ; +$0292 : 4A81
    bmi.w L_0067FC                                    ; +$0294 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0298 : B2AC0010
    bge.w L_0067FC                                    ; +$029C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$02A0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$02A8 : 224A
    jsr -324(a6)                                      ; +$02AA : 4EAEFEBC
    tst.l d0                                          ; +$02AE : 4A80
    bne.w L_0067FC                                    ; +$02B0 : 66000008
    move.l #$00000001,d3                              ; +$02B4 : 263C00000001
L_0067FC:
    move.l d2,d0                                      ; +$02BA : 2002
    add.l d5,d0                                       ; +$02BC : D085
    tst.l d0                                          ; +$02BE : 4A80
    bmi.w L_00683C                                    ; +$02C0 : 6B000038
    cmp.l 12(a4),d0                                   ; +$02C4 : B0AC000C
    bge.w L_00683C                                    ; +$02C8 : 6C000030
    move.l d4,d1                                      ; +$02CC : 2204
    sub.l 128(a7),d1                                  ; +$02CE : 92AF0080
    tst.l d1                                          ; +$02D2 : 4A81
    bmi.w L_00683C                                    ; +$02D4 : 6B000024
    cmp.l 16(a4),d1                                   ; +$02D8 : B2AC0010
    bge.w L_00683C                                    ; +$02DC : 6C00001C
    move.l #$00000001,136(a7)                         ; +$02E0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$02E8 : 224A
    jsr -324(a6)                                      ; +$02EA : 4EAEFEBC
    tst.l d0                                          ; +$02EE : 4A80
    bne.w L_00683C                                    ; +$02F0 : 66000008
    move.l #$00000001,d3                              ; +$02F4 : 263C00000001
L_00683C:
    move.l d2,d0                                      ; +$02FA : 2002
    sub.l d5,d0                                       ; +$02FC : 9085
    tst.l d0                                          ; +$02FE : 4A80
    bmi.w L_00687C                                    ; +$0300 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0304 : B0AC000C
    bge.w L_00687C                                    ; +$0308 : 6C000030
    move.l d4,d1                                      ; +$030C : 2204
    sub.l 128(a7),d1                                  ; +$030E : 92AF0080
    tst.l d1                                          ; +$0312 : 4A81
    bmi.w L_00687C                                    ; +$0314 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0318 : B2AC0010
    bge.w L_00687C                                    ; +$031C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0320 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0328 : 224A
    jsr -324(a6)                                      ; +$032A : 4EAEFEBC
    tst.l d0                                          ; +$032E : 4A80
    bne.w L_00687C                                    ; +$0330 : 66000008
    move.l #$00000001,d3                              ; +$0334 : 263C00000001
L_00687C:
    move.l d2,d0                                      ; +$033A : 2002
    add.l 128(a7),d0                                  ; +$033C : D0AF0080
    tst.l d0                                          ; +$0340 : 4A80
    bmi.w L_0068BC                                    ; +$0342 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0346 : B0AC000C
    bge.w L_0068BC                                    ; +$034A : 6C00002E
    move.l d4,d1                                      ; +$034E : 2204
    add.l d5,d1                                       ; +$0350 : D285
    tst.l d1                                          ; +$0352 : 4A81
    bmi.w L_0068BC                                    ; +$0354 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0358 : B2AC0010
    bge.w L_0068BC                                    ; +$035C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0360 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0368 : 224A
    jsr -324(a6)                                      ; +$036A : 4EAEFEBC
    tst.l d0                                          ; +$036E : 4A80
    bne.w L_0068BC                                    ; +$0370 : 66000008
    move.l #$00000001,d3                              ; +$0374 : 263C00000001
L_0068BC:
    move.l d2,d0                                      ; +$037A : 2002
    sub.l 128(a7),d0                                  ; +$037C : 90AF0080
    tst.l d0                                          ; +$0380 : 4A80
    bmi.w L_0068FC                                    ; +$0382 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0386 : B0AC000C
    bge.w L_0068FC                                    ; +$038A : 6C00002E
    move.l d4,d1                                      ; +$038E : 2204
    add.l d5,d1                                       ; +$0390 : D285
    tst.l d1                                          ; +$0392 : 4A81
    bmi.w L_0068FC                                    ; +$0394 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0398 : B2AC0010
    bge.w L_0068FC                                    ; +$039C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$03A0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$03A8 : 224A
    jsr -324(a6)                                      ; +$03AA : 4EAEFEBC
    tst.l d0                                          ; +$03AE : 4A80
    bne.w L_0068FC                                    ; +$03B0 : 66000008
    move.l #$00000001,d3                              ; +$03B4 : 263C00000001
L_0068FC:
    move.l d2,d0                                      ; +$03BA : 2002
    add.l 128(a7),d0                                  ; +$03BC : D0AF0080
    tst.l d0                                          ; +$03C0 : 4A80
    bmi.w L_00693C                                    ; +$03C2 : 6B000036
    cmp.l 12(a4),d0                                   ; +$03C6 : B0AC000C
    bge.w L_00693C                                    ; +$03CA : 6C00002E
    move.l d4,d1                                      ; +$03CE : 2204
    sub.l d5,d1                                       ; +$03D0 : 9285
    tst.l d1                                          ; +$03D2 : 4A81
    bmi.w L_00693C                                    ; +$03D4 : 6B000024
    cmp.l 16(a4),d1                                   ; +$03D8 : B2AC0010
    bge.w L_00693C                                    ; +$03DC : 6C00001C
    move.l #$00000001,136(a7)                         ; +$03E0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$03E8 : 224A
    jsr -324(a6)                                      ; +$03EA : 4EAEFEBC
    tst.l d0                                          ; +$03EE : 4A80
    bne.w L_00693C                                    ; +$03F0 : 66000008
    move.l #$00000001,d3                              ; +$03F4 : 263C00000001
L_00693C:
    move.l d2,d0                                      ; +$03FA : 2002
    sub.l 128(a7),d0                                  ; +$03FC : 90AF0080
    tst.l d0                                          ; +$0400 : 4A80
    bmi.w L_00697C                                    ; +$0402 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0406 : B0AC000C
    bge.w L_00697C                                    ; +$040A : 6C00002E
    move.l d4,d1                                      ; +$040E : 2204
    sub.l d5,d1                                       ; +$0410 : 9285
    tst.l d1                                          ; +$0412 : 4A81
    bmi.w L_00697C                                    ; +$0414 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0418 : B2AC0010
    bge.w L_00697C                                    ; +$041C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0420 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0428 : 224A
    jsr -324(a6)                                      ; +$042A : 4EAEFEBC
    tst.l d0                                          ; +$042E : 4A80
    bne.w L_00697C                                    ; +$0430 : 66000008
    move.l #$00000001,d3                              ; +$0434 : 263C00000001
L_00697C:
    addq.l #1,128(a7)                                 ; +$043A : 52AF0080
    tst.l 132(a7)                                     ; +$043E : 4AAF0084
    bmi.w L_006998                                    ; +$0442 : 6B000012
    subq.l #1,d5                                      ; +$0446 : 5385
    move.l 128(a7),d0                                 ; +$0448 : 202F0080
    sub.l d5,d0                                       ; +$044C : 9085
    lsl.l #1,d0                                       ; +$044E : E388
    addq.l #1,d0                                      ; +$0450 : 5280
    bra.w L_0069A0                                    ; +$0452 : 6000000A
L_006998:
    move.l 128(a7),d0                                 ; +$0456 : 202F0080
    lsl.l #1,d0                                       ; +$045A : E388
    addq.l #1,d0                                      ; +$045C : 5280
L_0069A0:
    move.l 132(a7),d1                                 ; +$045E : 222F0084
    add.l d0,d1                                       ; +$0462 : D280
    move.l d1,132(a7)                                 ; +$0464 : 2F410084
    move.l 128(a7),d0                                 ; +$0468 : 202F0080
    cmp.l d5,d0                                       ; +$046C : B085
    ble.w L_00677C                                    ; +$046E : 6F00FDCA
L_0069B4:
    tst.l 136(a7)                                     ; +$0472 : 4AAF0088
    beq.w L_0069C0                                    ; +$0476 : 67000006
    jsr -228(a6)                                      ; +$047A : 4EAEFF1C
L_0069C0:
    lea 160(a7),a7                                    ; +$047E : 4FEF00A0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0482 : 4CDF77F7
    moveq #0,d2                                       ; +$0486 : 7400
    rts                                               ; +$0488 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 54 : aga mouse cursor --------
Entry_54:
Aga_Mouse_Cursor:
    movem.l d0-d2/d4-d7/a0-a6,-(a7)                   ; +$0000 : 48E7EFFE
    move.l d3,d7                                      ; +$0004 : 2E03
    move.l #$00000000,d3                              ; +$0006 : 263C00000000
    tst.l d7                                          ; +$000C : 4A87
    blt.w L_006AA6                                    ; +$000E : 6D0000C6
    cmpi.l #$00000001,d7                              ; +$0012 : 0C8700000001
    bgt.w L_006AA6                                    ; +$0018 : 6E0000BC
    movea.l 456(a5),a4                                ; +$001C : 286D01C8
    move.l a4,d0                                      ; +$0020 : 200C
    tst.l d0                                          ; +$0022 : 4A80
    beq.w L_006AA6                                    ; +$0024 : 670000B0
    movea.l (a4),a1                                   ; +$0028 : 2254
    move.l a1,d0                                      ; +$002A : 2009
    tst.l d0                                          ; +$002C : 4A80
    beq.w L_006AA6                                    ; +$002E : 670000A6
    movea.l 4(a4),a6                                  ; +$0032 : 2C6C0004
    move.l a6,d0                                      ; +$0036 : 200E
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_006AA6                                    ; +$003A : 6700009A
    movea.l 36(a4),a3                                 ; +$003E : 266C0024
    move.l a3,d0                                      ; +$0042 : 200B
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_006AA6                                    ; +$0046 : 6700008E
    move.l 46(a3),d0                                  ; +$004A : 202B002E
    move.l a1,d1                                      ; +$004E : 2209
    cmp.l d1,d0                                       ; +$0050 : B081
    bne.w L_006AA6                                    ; +$0052 : 66000082
    lea L_006B10(pc),a2                               ; +$0056 : 45FA00E8
    move.l (a2),d0                                    ; +$005A : 2012
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_006A3E                                    ; +$005E : 6700000E
    move.l 4(a2),d0                                   ; +$0062 : 202A0004
    move.l a3,d1                                      ; +$0066 : 220B
    cmp.l d1,d0                                       ; +$0068 : B081
    bne.w L_006AA6                                    ; +$006A : 6600006A
L_006A3E:
    tst.l d7                                          ; +$006E : 4A87
    beq.w L_006A54                                    ; +$0070 : 67000012
    movea.l a3,a0                                     ; +$0074 : 204B
    jsr -60(a6)                                       ; +$0076 : 4EAEFFC4
    move.l #$00000001,d3                              ; +$007A : 263C00000001
    bra.w L_006AA6                                    ; +$0080 : 60000054
L_006A54:
    move.l (a2),d0                                    ; +$0084 : 2012
    tst.l d0                                          ; +$0086 : 4A80
    bne.w L_006A7C                                    ; +$0088 : 66000022
    move.l #$00000048,d0                              ; +$008C : 203C00000048
    move.l #$00010002,d1                              ; +$0092 : 223C00010002
    movea.l $0004.w,a6                                ; +$0098 : 2C780004
    jsr -198(a6)                                      ; +$009C : 4EAEFF3A
    tst.l d0                                          ; +$00A0 : 4A80
    beq.w L_006AA6                                    ; +$00A2 : 67000032
    move.l d0,(a2)                                    ; +$00A6 : 2480
    move.l a3,4(a2)                                   ; +$00A8 : 254B0004
L_006A7C:
    movea.l a3,a0                                     ; +$00AC : 204B
    movea.l (a2),a1                                   ; +$00AE : 2252
    move.l #$00000010,d0                              ; +$00B0 : 203C00000010
    move.l #$00000010,d1                              ; +$00B6 : 223C00000010
    move.l #$00000000,d2                              ; +$00BC : 243C00000000
    move.l #$00000000,d3                              ; +$00C2 : 263C00000000
    movea.l 4(a4),a6                                  ; +$00C8 : 2C6C0004
    jsr -270(a6)                                      ; +$00CC : 4EAEFEF2
    move.l #$00000001,d3                              ; +$00D0 : 263C00000001
L_006AA6:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$00D6 : 4CDF7FF7
    moveq #0,d2                                       ; +$00DA : 7400
    rts                                               ; +$00DC : 4E75
L_006AAE:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$00DE : 48E7FFFE
    movea.l a0,a3                                     ; +$00E2 : 2648
    lea L_006B10(pc),a4                               ; +$00E4 : 49FA005A
    move.l (a4),d0                                    ; +$00E8 : 2014
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_006AD2                                    ; +$00EC : 67000014
    move.l 4(a4),d0                                   ; +$00F0 : 202C0004
    move.l a3,d1                                      ; +$00F4 : 220B
    cmp.l d1,d0                                       ; +$00F6 : B081
    bne.w L_006AD2                                    ; +$00F8 : 66000008
    movea.l a3,a0                                     ; +$00FC : 204B
    jsr -60(a6)                                       ; +$00FE : 4EAEFFC4
L_006AD2:
    movea.l a3,a0                                     ; +$0102 : 204B
    jsr -72(a6)                                       ; +$0104 : 4EAEFFB8
    move.l (a4),d0                                    ; +$0108 : 2014
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_006B0A                                    ; +$010C : 6700002C
    move.l 4(a4),d0                                   ; +$0110 : 202C0004
    move.l a3,d1                                      ; +$0114 : 220B
    cmp.l d1,d0                                       ; +$0116 : B081
    bne.w L_006B0A                                    ; +$0118 : 66000020
    movea.l (a4),a1                                   ; +$011C : 2254
    move.l #$00000048,d0                              ; +$011E : 203C00000048
    movea.l $0004.w,a6                                ; +$0124 : 2C780004
    jsr -210(a6)                                      ; +$0128 : 4EAEFF2E
    move.l #$00000000,(a4)                            ; +$012C : 28BC00000000
    move.l #$00000000,4(a4)                           ; +$0132 : 297C000000000004
L_006B0A:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$013A : 4CDF7FFF
    rts                                               ; +$013E : 4E75
L_006B10:
    dcb.b 8,0
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 55 : aga image draw --------
Entry_55:
Aga_Image_Draw:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -192(a7),a7                                   ; +$0004 : 4FEFFF40
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d6                                   ; +$0012 : 2C1B
    move.l d6,8(a2)                                   ; +$0014 : 25460008
    move.l (a3)+,d4                                   ; +$0018 : 281B
    move.l d4,12(a2)                                  ; +$001A : 2544000C
    move.l (a3)+,d5                                   ; +$001E : 2A1B
    move.l d5,16(a2)                                  ; +$0020 : 25450010
    move.l #$00000000,d3                              ; +$0024 : 263C00000000
    move.l (a2),d0                                    ; +$002A : 2012
    cmpi.l #$00000001,d0                              ; +$002C : 0C8000000001
    bhi.w L_006F36                                    ; +$0032 : 620003E6
    cmpi.l #$00000020,d4                              ; +$0036 : 0C8400000020
    bcs.w L_006F36                                    ; +$003C : 650003DC
    cmpi.l #$01000000,d4                              ; +$0040 : 0C8401000000
    bhi.w L_006F36                                    ; +$0046 : 620003D2
    cmpi.l #$00000018,d5                              ; +$004A : 0C8500000018
    bls.w L_006F36                                    ; +$0050 : 630003C8
    move.l d5,d0                                      ; +$0054 : 2005
    andi.l #$00000001,d0                              ; +$0056 : 028000000001
    bne.w L_006F36                                    ; +$005C : 660003BC
    cmpi.l #$FFFF8000,d6                              ; +$0060 : 0C86FFFF8000
    blt.w L_006F36                                    ; +$0066 : 6D0003B2
    cmpi.l #$00007FFF,d6                              ; +$006A : 0C8600007FFF
    bgt.w L_006F36                                    ; +$0070 : 6E0003A8
    cmpi.l #$FFFF8000,d7                              ; +$0074 : 0C87FFFF8000
    blt.w L_006F36                                    ; +$007A : 6D00039E
    cmpi.l #$00007FFF,d7                              ; +$007E : 0C8700007FFF
    bgt.w L_006F36                                    ; +$0084 : 6E000394
    move.l d5,d0                                      ; +$0088 : 2005
    add.l d4,d0                                       ; +$008A : D084
    bcs.w L_006F36                                    ; +$008C : 6500038C
    subq.l #1,d0                                      ; +$0090 : 5380
    movea.l d0,a1                                     ; +$0092 : 2240
    movea.l $0004.w,a6                                ; +$0094 : 2C780004
    jsr -534(a6)                                      ; +$0098 : 4EAEFDEA
    tst.l d0                                          ; +$009C : 4A80
    beq.w L_006F36                                    ; +$009E : 6700037A
    move.l d5,d0                                      ; +$00A2 : 2005
    subi.l #$00000018,d0                              ; +$00A4 : 048000000018
    movea.l d0,a1                                     ; +$00AA : 2240
    jsr -534(a6)                                      ; +$00AC : 4EAEFDEA
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_006F36                                    ; +$00B2 : 67000366
    movea.l d5,a0                                     ; +$00B6 : 2045
    move.l -20(a0),d0                                 ; +$00B8 : 2028FFEC
    move.l d4,d1                                      ; +$00BC : 2204
    addi.l #$00000010,d1                              ; +$00BE : 068100000010
    cmp.l d1,d0                                       ; +$00C4 : B081
    bne.w L_006F36                                    ; +$00C6 : 66000352
    move.l -16(a0),d0                                 ; +$00CA : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00CE : 0C8000000005
    bcs.w L_006F36                                    ; +$00D4 : 65000344
    cmpi.l #$0000FFFF,d0                              ; +$00D8 : 0C800000FFFF
    bhi.w L_006F36                                    ; +$00DE : 6200033A
    move.l #$00000000,d0                              ; +$00E2 : 203C00000000
    move.w -12(a0),d0                                 ; +$00E8 : 3028FFF4
    tst.l d0                                          ; +$00EC : 4A80
    beq.w L_006C1C                                    ; +$00EE : 67000010
    andi.w #$FFFD,d0                                  ; +$00F2 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00F6 : 0C8000000001
    bne.w L_006F36                                    ; +$00FC : 6600031C
L_006C1C:
    move.l -8(a0),d0                                  ; +$0100 : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$0104 : 0C8041474150
    bne.w L_006F36                                    ; +$010A : 6600030E
    move.l -4(a0),d0                                  ; +$010E : 2028FFFC
    cmpi.l #$49432020,d0                              ; +$0112 : 0C8049432020
    bne.w L_006F36                                    ; +$0118 : 66000300
    move.l (a0),d0                                    ; +$011C : 2010
    cmpi.l #$41474150,d0                              ; +$011E : 0C8041474150
    bne.w L_006F36                                    ; +$0124 : 660002F4
    move.l #$00000000,d0                              ; +$0128 : 203C00000000
    move.w 4(a0),d0                                   ; +$012E : 30280004
    cmpi.l #$00004943,d0                              ; +$0132 : 0C8000004943
    bne.w L_006F36                                    ; +$0138 : 660002E0
    move.l #$00000000,d0                              ; +$013C : 203C00000000
    move.w 6(a0),d0                                   ; +$0142 : 30280006
    cmpi.l #$00000001,d0                              ; +$0146 : 0C8000000001
    bne.w L_006F36                                    ; +$014C : 660002CC
    move.l #$00000000,d0                              ; +$0150 : 203C00000000
    move.w 8(a0),d0                                   ; +$0156 : 30280008
    move.l d0,32(a2)                                  ; +$015A : 25400020
    cmpi.l #$00000001,d0                              ; +$015E : 0C8000000001
    bhi.w L_006F36                                    ; +$0164 : 620002B4
    move.l (a2),d1                                    ; +$0168 : 2212
    tst.l d1                                          ; +$016A : 4A81
    beq.w L_006C92                                    ; +$016C : 67000008
    tst.l d0                                          ; +$0170 : 4A80
    beq.w L_006F36                                    ; +$0172 : 670002A6
L_006C92:
    move.l #$00000000,d0                              ; +$0176 : 203C00000000
    move.w 10(a0),d0                                  ; +$017C : 3028000A
    cmpi.l #$00000001,d0                              ; +$0180 : 0C8000000001
    bne.w L_006F36                                    ; +$0186 : 66000292
    move.l #$00000000,d0                              ; +$018A : 203C00000000
    move.w 12(a0),d0                                  ; +$0190 : 3028000C
    move.l d0,20(a2)                                  ; +$0194 : 25400014
    tst.l d0                                          ; +$0198 : 4A80
    beq.w L_006F36                                    ; +$019A : 6700027E
    cmpi.l #$00001000,d0                              ; +$019E : 0C8000001000
    bhi.w L_006F36                                    ; +$01A4 : 62000274
    move.l #$00000000,d0                              ; +$01A8 : 203C00000000
    move.w 14(a0),d0                                  ; +$01AE : 3028000E
    move.l d0,24(a2)                                  ; +$01B2 : 25400018
    tst.l d0                                          ; +$01B6 : 4A80
    beq.w L_006F36                                    ; +$01B8 : 67000260
    cmpi.l #$00001000,d0                              ; +$01BC : 0C8000001000
    bhi.w L_006F36                                    ; +$01C2 : 62000256
    move.l 20(a2),d1                                  ; +$01C6 : 222A0014
    mulu.w d1,d0                                      ; +$01CA : C0C1
    cmpi.l #$00400000,d0                              ; +$01CC : 0C8000400000
    bhi.w L_006F36                                    ; +$01D2 : 62000246
    move.l #$00000000,d0                              ; +$01D6 : 203C00000000
    move.w 16(a0),d0                                  ; +$01DC : 30280010
    move.l d0,28(a2)                                  ; +$01E0 : 2540001C
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_006F36                                    ; +$01E6 : 67000232
    cmpi.l #$00000008,d0                              ; +$01EA : 0C8000000008
    bhi.w L_006F36                                    ; +$01F0 : 62000228
    move.l d0,d1                                      ; +$01F4 : 2200
    move.l 32(a2),d0                                  ; +$01F6 : 202A0020
    add.l d1,d0                                       ; +$01FA : D081
    lsl.l #1,d0                                       ; +$01FC : E388
    move.l d0,36(a2)                                  ; +$01FE : 25400024
    move.l #$00000000,d1                              ; +$0202 : 223C00000000
    move.w 18(a0),d1                                  ; +$0208 : 32280012
    cmp.l d1,d0                                       ; +$020C : B081
    bne.w L_006F36                                    ; +$020E : 6600020A
    move.l 20(a0),d0                                  ; +$0212 : 20280014
    cmpi.l #$00000020,d0                              ; +$0216 : 0C8000000020
    bne.w L_006F36                                    ; +$021C : 660001FC
    move.l 24(a2),d0                                  ; +$0220 : 202A0018
    addq.l #1,d0                                      ; +$0224 : 5280
    lsl.l #2,d0                                       ; +$0226 : E588
    addi.l #$00000020,d0                              ; +$0228 : 068000000020
    move.l d0,48(a2)                                  ; +$022E : 25400030
    move.l 24(a0),d1                                  ; +$0232 : 22280018
    cmp.l d1,d0                                       ; +$0236 : B081
    bne.w L_006F36                                    ; +$0238 : 660001E0
    cmp.l d4,d0                                       ; +$023C : B084
    bhi.w L_006F36                                    ; +$023E : 620001DA
    move.l 28(a0),d0                                  ; +$0242 : 2028001C
    cmp.l d4,d0                                       ; +$0246 : B084
    bne.w L_006F36                                    ; +$0248 : 660001D0
    move.l 20(a2),d0                                  ; +$024C : 202A0014
    addi.l #$0000000F,d0                              ; +$0250 : 06800000000F
    lsr.l #4,d0                                       ; +$0256 : E888
    move.l d0,40(a2)                                  ; +$0258 : 25400028
    move.l 20(a2),d1                                  ; +$025C : 222A0014
    andi.l #$0000000F,d1                              ; +$0260 : 02810000000F
    move.l #$00000000,d0                              ; +$0266 : 203C00000000
    tst.l d1                                          ; +$026C : 4A81
    beq.w L_006D9C                                    ; +$026E : 67000010
    move.l #$0000FFFF,d0                              ; +$0272 : 203C0000FFFF
L_006D94:
    lsr.w #1,d0                                       ; +$0278 : E248
    subq.l #1,d1                                      ; +$027A : 5381
    bne.w L_006D94                                    ; +$027C : 6600FFFA
L_006D9C:
    move.l d0,44(a2)                                  ; +$0280 : 2540002C
    movea.l 456(a5),a4                                ; +$0284 : 286D01C8
    move.l a4,d0                                      ; +$0288 : 200C
    tst.l d0                                          ; +$028A : 4A80
    beq.w L_006F36                                    ; +$028C : 6700018C
    move.l (a4),d0                                    ; +$0290 : 2014
    tst.l d0                                          ; +$0292 : 4A80
    beq.w L_006F36                                    ; +$0294 : 67000184
    move.l 8(a4),d0                                   ; +$0298 : 202C0008
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_006F36                                    ; +$029E : 6700017A
    move.l 32(a4),d0                                  ; +$02A2 : 202C0020
    tst.l d0                                          ; +$02A6 : 4A80
    beq.w L_006F36                                    ; +$02A8 : 67000170
    move.l 12(a4),d0                                  ; +$02AC : 202C000C
    tst.l d0                                          ; +$02B0 : 4A80
    ble.w L_006F36                                    ; +$02B2 : 6F000166
    cmpi.l #$00007FFF,d0                              ; +$02B6 : 0C8000007FFF
    bgt.w L_006F36                                    ; +$02BC : 6E00015C
    move.l d0,52(a2)                                  ; +$02C0 : 25400034
    move.l 16(a4),d0                                  ; +$02C4 : 202C0010
    tst.l d0                                          ; +$02C8 : 4A80
    ble.w L_006F36                                    ; +$02CA : 6F00014E
    cmpi.l #$00007FFF,d0                              ; +$02CE : 0C8000007FFF
    bgt.w L_006F36                                    ; +$02D4 : 6E000144
    move.l d0,56(a2)                                  ; +$02D8 : 25400038
    move.l 28(a4),d0                                  ; +$02DC : 202C001C
    cmp.l 28(a2),d0                                   ; +$02E0 : B0AA001C
    bne.w L_006F36                                    ; +$02E4 : 66000134
    movea.l 32(a4),a0                                 ; +$02E8 : 206C0020
    move.l 8(a0),d0                                   ; +$02EC : 20280008
    tst.l d0                                          ; +$02F0 : 4A80
    beq.w L_006E26                                    ; +$02F2 : 67000016
    cmpi.l #$00000001,d0                              ; +$02F6 : 0C8000000001
    bne.w L_006F36                                    ; +$02FC : 6600011C
    movea.l 32(a4),a0                                 ; +$0300 : 206C0020
    movea.l (a0),a1                                   ; +$0304 : 2250
    bra.w L_006E2E                                    ; +$0306 : 6000000A
L_006E26:
    movea.l 32(a4),a0                                 ; +$030A : 206C0020
    movea.l 4(a0),a1                                  ; +$030E : 22680004
L_006E2E:
    move.l a1,d0                                      ; +$0312 : 2009
    tst.l d0                                          ; +$0314 : 4A80
    beq.w L_006F36                                    ; +$0316 : 67000102
    movea.l (a1),a0                                   ; +$031A : 2051
    move.l a0,d0                                      ; +$031C : 2008
    tst.l d0                                          ; +$031E : 4A80
    beq.w L_006F36                                    ; +$0320 : 670000F8
    move.l a0,64(a2)                                  ; +$0324 : 25480040
    move.l #$00000000,d1                              ; +$0328 : 223C00000000
    move.w (a0),d1                                    ; +$032E : 3210
    tst.l d1                                          ; +$0330 : 4A81
    beq.w L_006F36                                    ; +$0332 : 670000E6
    move.l d1,60(a2)                                  ; +$0336 : 2541003C
    lsl.l #3,d1                                       ; +$033A : E789
    cmp.l 52(a2),d1                                   ; +$033C : B2AA0034
    blt.w L_006F36                                    ; +$0340 : 6D0000D8
    move.l #$00000000,d1                              ; +$0344 : 223C00000000
    move.w 2(a0),d1                                   ; +$034A : 32280002
    cmp.l 56(a2),d1                                   ; +$034E : B2AA0038
    blt.w L_006F36                                    ; +$0352 : 6D0000C6
    move.l #$00000000,d1                              ; +$0356 : 223C00000000
    move.b 5(a0),d1                                   ; +$035C : 12280005
    cmp.l 28(a2),d1                                   ; +$0360 : B2AA001C
    bne.w L_006F36                                    ; +$0364 : 660000B4
    move.l d1,d0                                      ; +$0368 : 2001
    movea.l a0,a1                                     ; +$036A : 2248
    addq.l #8,a1                                      ; +$036C : 5089
L_006E8A:
    move.l (a1)+,d1                                   ; +$036E : 2219
    tst.l d1                                          ; +$0370 : 4A81
    beq.w L_006F36                                    ; +$0372 : 670000A6
    cmpi.l #$FFFFFFFF,d1                              ; +$0376 : 0C81FFFFFFFF
    beq.w L_006F36                                    ; +$037C : 6700009C
    subq.l #1,d0                                      ; +$0380 : 5380
    bne.w L_006E8A                                    ; +$0382 : 6600FFEA
    move.l #$00000000,72(a2)                          ; +$0386 : 257C000000000048
    bsr.w L_006F42                                    ; +$038E : 61000096
    tst.l d0                                          ; +$0392 : 4A80
    beq.w L_006F36                                    ; +$0394 : 67000084
    move.l 8(a2),d0                                   ; +$0398 : 202A0008
    cmp.l 52(a2),d0                                   ; +$039C : B0AA0034
    bge.w L_006F30                                    ; +$03A0 : 6C000072
    add.l 20(a2),d0                                   ; +$03A4 : D0AA0014
    tst.l d0                                          ; +$03A8 : 4A80
    ble.w L_006F30                                    ; +$03AA : 6F000068
    move.l 4(a2),d0                                   ; +$03AE : 202A0004
    cmp.l 56(a2),d0                                   ; +$03B2 : B0AA0038
    bge.w L_006F30                                    ; +$03B6 : 6C00005C
    add.l 24(a2),d0                                   ; +$03BA : D0AA0018
    tst.l d0                                          ; +$03BE : 4A80
    ble.w L_006F30                                    ; +$03C0 : 6F000052
    movea.l 32(a4),a0                                 ; +$03C4 : 206C0020
    move.l 20(a0),d0                                  ; +$03C8 : 20280014
    andi.l #$00000001,d0                              ; +$03CC : 028000000001
    beq.w L_006F1E                                    ; +$03D2 : 6700002E
    movea.l 12(a0),a0                                 ; +$03D6 : 2068000C
    move.l a0,d0                                      ; +$03DA : 2008
    tst.l d0                                          ; +$03DC : 4A80
    beq.w L_006F36                                    ; +$03DE : 6700003A
    movea.l $0004.w,a6                                ; +$03E2 : 2C780004
    jsr -372(a6)                                      ; +$03E6 : 4EAEFE8C
    tst.l d0                                          ; +$03EA : 4A80
    beq.w L_006F36                                    ; +$03EC : 6700002C
    movea.l 32(a4),a0                                 ; +$03F0 : 206C0020
    move.l 20(a0),d0                                  ; +$03F4 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$03F8 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$03FE : 21400014
L_006F1E:
    move.l #$00000001,72(a2)                          ; +$0402 : 257C000000010048
    bsr.w L_006F42                                    ; +$040A : 6100001A
    tst.l d0                                          ; +$040E : 4A80
    beq.w L_006F36                                    ; +$0410 : 67000008
L_006F30:
    move.l #$00000001,d3                              ; +$0414 : 263C00000001
L_006F36:
    lea 192(a7),a7                                    ; +$041A : 4FEF00C0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$041E : 4CDF77F7
    moveq #0,d2                                       ; +$0422 : 7400
    rts                                               ; +$0424 : 4E75
L_006F42:
    move.l #$00000000,68(a2)                          ; +$0426 : 257C000000000044
L_006F4A:
    move.l 68(a2),d0                                  ; +$042E : 202A0044
    cmp.l 24(a2),d0                                   ; +$0432 : B0AA0018
    bge.w L_007102                                    ; +$0436 : 6C0001AE
    lsl.l #2,d0                                       ; +$043A : E588
    move.l d0,d1                                      ; +$043C : 2200
    move.l 16(a2),d0                                  ; +$043E : 202A0010
    addi.l #$00000020,d0                              ; +$0442 : 068000000020
    add.l d1,d0                                       ; +$0448 : D081
    movea.l d0,a1                                     ; +$044A : 2240
    move.l (a1)+,d0                                   ; +$044C : 2019
    move.l (a1)+,d1                                   ; +$044E : 2219
    cmp.l d1,d0                                       ; +$0450 : B081
    bcc.w L_00710A                                    ; +$0452 : 6400019A
    cmp.l 48(a2),d0                                   ; +$0456 : B0AA0030
    bcs.w L_00710A                                    ; +$045A : 65000192
    cmp.l 12(a2),d1                                   ; +$045E : B2AA000C
    bhi.w L_00710A                                    ; +$0462 : 6200018A
    move.l 68(a2),d2                                  ; +$0466 : 242A0044
    tst.l d2                                          ; +$046A : 4A82
    bne.w L_006F94                                    ; +$046C : 6600000A
    cmp.l 48(a2),d0                                   ; +$0470 : B0AA0030
    bne.w L_00710A                                    ; +$0474 : 66000178
L_006F94:
    move.l 24(a2),d2                                  ; +$0478 : 242A0018
    subq.l #1,d2                                      ; +$047C : 5382
    cmp.l 68(a2),d2                                   ; +$047E : B4AA0044
    bne.w L_006FAA                                    ; +$0482 : 6600000A
    cmp.l 12(a2),d1                                   ; +$0486 : B2AA000C
    bne.w L_00710A                                    ; +$048A : 66000162
L_006FAA:
    move.l 16(a2),d2                                  ; +$048E : 242A0010
    add.l d2,d0                                       ; +$0492 : D082
    move.l d0,76(a2)                                  ; +$0494 : 2540004C
    add.l d2,d1                                       ; +$0498 : D282
    move.l d1,80(a2)                                  ; +$049A : 25410050
    move.l #$00000000,84(a2)                          ; +$049E : 257C000000000054
    move.l #$00000000,88(a2)                          ; +$04A6 : 257C000000000058
    move.l #$00000000,92(a2)                          ; +$04AE : 257C00000000005C
L_006FD2:
    move.l 84(a2),d0                                  ; +$04B6 : 202A0054
    cmp.l 40(a2),d0                                   ; +$04BA : B0AA0028
    bge.w L_0070E8                                    ; +$04BE : 6C00010C
    move.l 88(a2),d0                                  ; +$04C2 : 202A0058
    tst.l d0                                          ; +$04C6 : 4A80
    bne.w L_007058                                    ; +$04C8 : 66000072
    move.l 76(a2),d0                                  ; +$04CC : 202A004C
    cmp.l 80(a2),d0                                   ; +$04D0 : B0AA0050
    bcc.w L_00710A                                    ; +$04D4 : 64000118
    movea.l d0,a0                                     ; +$04D8 : 2040
    move.l #$00000000,d0                              ; +$04DA : 203C00000000
    move.b (a0)+,d0                                   ; +$04E0 : 1018
    move.l d0,d1                                      ; +$04E2 : 2200
    andi.l #$0000007F,d1                              ; +$04E4 : 02810000007F
    addq.l #1,d1                                      ; +$04EA : 5281
    move.l d1,88(a2)                                  ; +$04EC : 25410058
    move.l d0,d2                                      ; +$04F0 : 2400
    andi.l #$00000080,d2                              ; +$04F2 : 028200000080
    move.l d2,92(a2)                                  ; +$04F8 : 2542005C
    move.l 84(a2),d2                                  ; +$04FC : 242A0054
    add.l d1,d2                                       ; +$0500 : D481
    cmp.l 40(a2),d2                                   ; +$0502 : B4AA0028
    bgt.w L_00710A                                    ; +$0506 : 6E0000E6
    move.l a0,d2                                      ; +$050A : 2408
    move.l d2,76(a2)                                  ; +$050C : 2542004C
    move.l 92(a2),d2                                  ; +$0510 : 242A005C
    tst.l d2                                          ; +$0514 : 4A82
    beq.w L_007042                                    ; +$0516 : 6700000E
    move.l a0,96(a2)                                  ; +$051A : 25480060
    move.l 36(a2),d2                                  ; +$051E : 242A0024
    bra.w L_007048                                    ; +$0522 : 60000008
L_007042:
    move.l 36(a2),d2                                  ; +$0526 : 242A0024
    mulu.w d1,d2                                      ; +$052A : C4C1
L_007048:
    move.l a0,d0                                      ; +$052C : 2008
    add.l d2,d0                                       ; +$052E : D082
    bcs.w L_00710A                                    ; +$0530 : 650000BC
    cmp.l 80(a2),d0                                   ; +$0534 : B0AA0050
    bgt.w L_00710A                                    ; +$0538 : 6E0000B4
L_007058:
    move.l 92(a2),d2                                  ; +$053C : 242A005C
    tst.l d2                                          ; +$0540 : 4A82
    bne.w L_007076                                    ; +$0542 : 66000016
    move.l 76(a2),d0                                  ; +$0546 : 202A004C
    move.l d0,96(a2)                                  ; +$054A : 25400060
    add.l 36(a2),d0                                   ; +$054E : D0AA0024
    move.l d0,76(a2)                                  ; +$0552 : 2540004C
    bra.w L_00708C                                    ; +$0556 : 60000018
L_007076:
    move.l 76(a2),d0                                  ; +$055A : 202A004C
    move.l 96(a2),d1                                  ; +$055E : 222A0060
    cmp.l d1,d0                                       ; +$0562 : B081
    bne.w L_00708C                                    ; +$0564 : 6600000A
    add.l 36(a2),d0                                   ; +$0568 : D0AA0024
    move.l d0,76(a2)                                  ; +$056C : 2540004C
L_00708C:
    move.l 44(a2),d0                                  ; +$0570 : 202A002C
    tst.l d0                                          ; +$0574 : 4A80
    beq.w L_0070C2                                    ; +$0576 : 6700002E
    move.l 84(a2),d1                                  ; +$057A : 222A0054
    addq.l #1,d1                                      ; +$057E : 5281
    cmp.l 40(a2),d1                                   ; +$0580 : B2AA0028
    bne.w L_0070C2                                    ; +$0584 : 66000020
    movea.l 96(a2),a0                                 ; +$0588 : 206A0060
    move.l 36(a2),d1                                  ; +$058C : 222A0024
    lsr.l #1,d1                                       ; +$0590 : E289
L_0070AE:
    move.l #$00000000,d2                              ; +$0592 : 243C00000000
    move.w (a0)+,d2                                   ; +$0598 : 3418
    and.w d0,d2                                       ; +$059A : C440
    bne.w L_00710A                                    ; +$059C : 66000050
    subq.l #1,d1                                      ; +$05A0 : 5381
    bne.w L_0070AE                                    ; +$05A2 : 6600FFEE
L_0070C2:
    move.l 72(a2),d0                                  ; +$05A6 : 202A0048
    tst.l d0                                          ; +$05AA : 4A80
    beq.w L_0070D0                                    ; +$05AC : 67000006
    bsr.w L_007112                                    ; +$05B0 : 61000044
L_0070D0:
    move.l 88(a2),d0                                  ; +$05B4 : 202A0058
    subq.l #1,d0                                      ; +$05B8 : 5380
    move.l d0,88(a2)                                  ; +$05BA : 25400058
    move.l 84(a2),d0                                  ; +$05BE : 202A0054
    addq.l #1,d0                                      ; +$05C2 : 5280
    move.l d0,84(a2)                                  ; +$05C4 : 25400054
    bra.w L_006FD2                                    ; +$05C8 : 6000FEEC
L_0070E8:
    move.l 76(a2),d0                                  ; +$05CC : 202A004C
    cmp.l 80(a2),d0                                   ; +$05D0 : B0AA0050
    bne.w L_00710A                                    ; +$05D4 : 66000018
    move.l 68(a2),d0                                  ; +$05D8 : 202A0044
    addq.l #1,d0                                      ; +$05DC : 5280
    move.l d0,68(a2)                                  ; +$05DE : 25400044
    bra.w L_006F4A                                    ; +$05E2 : 6000FE4A
L_007102:
    move.l #$00000001,d0                              ; +$05E6 : 203C00000001
    rts                                               ; +$05EC : 4E75
L_00710A:
    move.l #$00000000,d0                              ; +$05EE : 203C00000000
    rts                                               ; +$05F4 : 4E75
L_007112:
    move.l 68(a2),d0                                  ; +$05F6 : 202A0044
    add.l 4(a2),d0                                    ; +$05FA : D0AA0004
    tst.l d0                                          ; +$05FE : 4A80
    bmi.w L_00721E                                    ; +$0600 : 6B000100
    cmp.l 56(a2),d0                                   ; +$0604 : B0AA0038
    bge.w L_00721E                                    ; +$0608 : 6C0000F8
    move.l d0,108(a2)                                 ; +$060C : 2540006C
    move.l #$00000000,100(a2)                         ; +$0610 : 257C000000000064
L_007134:
    move.l 100(a2),d0                                 ; +$0618 : 202A0064
    cmpi.l #$00000010,d0                              ; +$061C : 0C8000000010
    bge.w L_00721E                                    ; +$0622 : 6C0000DE
    move.l 84(a2),d1                                  ; +$0626 : 222A0054
    lsl.l #4,d1                                       ; +$062A : E989
    add.l d0,d1                                       ; +$062C : D280
    cmp.l 20(a2),d1                                   ; +$062E : B2AA0014
    bge.w L_00721E                                    ; +$0632 : 6C0000CE
    add.l 8(a2),d1                                    ; +$0636 : D2AA0008
    tst.l d1                                          ; +$063A : 4A81
    bmi.w L_007210                                    ; +$063C : 6B0000B6
    cmp.l 52(a2),d1                                   ; +$0640 : B2AA0034
    bge.w L_007210                                    ; +$0644 : 6C0000AE
    move.l d1,104(a2)                                 ; +$0648 : 25410068
    move.l #$0000000F,d0                              ; +$064C : 203C0000000F
    sub.l 100(a2),d0                                  ; +$0652 : 90AA0064
    move.l d0,124(a2)                                 ; +$0656 : 2540007C
    move.l (a2),d2                                    ; +$065A : 2412
    tst.l d2                                          ; +$065C : 4A82
    beq.w L_007190                                    ; +$065E : 67000014
    movea.l 96(a2),a0                                 ; +$0662 : 206A0060
    move.l #$00000000,d2                              ; +$0666 : 243C00000000
    move.w (a0),d2                                    ; +$066C : 3410
    btst d0,d2                                        ; +$066E : 0102
    beq.w L_007210                                    ; +$0670 : 67000082
L_007190:
    move.l 108(a2),d0                                 ; +$0674 : 202A006C
    move.l 60(a2),d1                                  ; +$0678 : 222A003C
    mulu.w d1,d0                                      ; +$067C : C0C1
    move.l 104(a2),d1                                 ; +$067E : 222A0068
    lsr.l #3,d1                                       ; +$0682 : E689
    add.l d1,d0                                       ; +$0684 : D081
    move.l d0,112(a2)                                 ; +$0686 : 25400070
    move.l 104(a2),d1                                 ; +$068A : 222A0068
    andi.l #$00000007,d1                              ; +$068E : 028100000007
    move.l #$00000007,d0                              ; +$0694 : 203C00000007
    sub.l d1,d0                                       ; +$069A : 9081
    move.l d0,116(a2)                                 ; +$069C : 25400074
    movea.l 96(a2),a1                                 ; +$06A0 : 226A0060
    move.l 32(a2),d0                                  ; +$06A4 : 202A0020
    tst.l d0                                          ; +$06A8 : 4A80
    beq.w L_0071CC                                    ; +$06AA : 67000004
    addq.l #2,a1                                      ; +$06AE : 5489
L_0071CC:
    movea.l 64(a2),a6                                 ; +$06B0 : 2C6A0040
    addq.l #8,a6                                      ; +$06B4 : 508E
    move.l 28(a2),d0                                  ; +$06B6 : 202A001C
    move.l d0,120(a2)                                 ; +$06BA : 25400078
L_0071DA:
    move.l #$00000000,d2                              ; +$06BE : 243C00000000
    move.w (a1)+,d2                                   ; +$06C4 : 3419
    movea.l (a6)+,a0                                  ; +$06C6 : 205E
    move.l a0,d4                                      ; +$06C8 : 2808
    add.l 112(a2),d4                                  ; +$06CA : D8AA0070
    movea.l d4,a0                                     ; +$06CE : 2044
    move.l 124(a2),d0                                 ; +$06D0 : 202A007C
    move.l 116(a2),d1                                 ; +$06D4 : 222A0074
    btst d0,d2                                        ; +$06D8 : 0102
    beq.w L_007200                                    ; +$06DA : 67000008
    bset d1,(a0)                                      ; +$06DE : 03D0
    bra.w L_007202                                    ; +$06E0 : 60000004
L_007200:
    bclr d1,(a0)                                      ; +$06E4 : 0390
L_007202:
    move.l 120(a2),d0                                 ; +$06E6 : 202A0078
    subq.l #1,d0                                      ; +$06EA : 5380
    move.l d0,120(a2)                                 ; +$06EC : 25400078
    bne.w L_0071DA                                    ; +$06F0 : 6600FFCC
L_007210:
    move.l 100(a2),d0                                 ; +$06F4 : 202A0064
    addq.l #1,d0                                      ; +$06F8 : 5280
    move.l d0,100(a2)                                 ; +$06FA : 25400064
    bra.w L_007134                                    ; +$06FE : 6000FF18
L_00721E:
    rts                                               ; +$0702 : 4E75

Entry_56:
C_Title:
    dc.b "AMOSPro AGA M16 Image Draw R46 0.12.1"
    dc.b $00,$24,$56,$45,$52,$3A,$20,$41,$4D,$4F,$53,$50
    dc.b "ro_AGA 0.12.1"
    dc.b $00,$00
C_End:
    dc.w 0
    cnop 0,4
HUNK_DATA_END:
    dc.l $000003F2
