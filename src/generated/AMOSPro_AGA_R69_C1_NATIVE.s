; Restored from SHA-pinned Compiler-safe Rbsr wrapper, in memory only.
; Native assembler source is NOT an installable AMOS Compiler library.
; Production builds MUST apply compiler_relocation.wrap_native_ap20().

; AMOS Professional 365 - AGA extension native 68000 source restoration
; Generated from the actual AP20/HUNK image, NOT the historical M1 source.
; All recognized executable instructions are real Motorola mnemonics.
; Remaining dc.b/dcb.b encode strings, state/data, AMOS Rjsr markers,
; or code that cannot be safely identified. They are never silently lost.
; A native assembler comparison is REQUIRED before treating this file
; as byte-identical or using it as the replacement build authority.
; SHA256 original: 5c90e8f02cb82c3939c31c2615ecfd367ab5c9a70316fb50e72c067f2d9c7b9e
; Build: AMOSPro AGA OPT020 Image Region R69 0.13.14 Gate A candidate | $VER: AMOSPro_AGA 0.13.14 |  |
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
    dc.w (Entry_57-Entry_56)/2
    dc.w (Entry_58-Entry_57)/2
    dc.w (Entry_59-Entry_58)/2
    dc.w (Entry_60-Entry_59)/2
    dc.w (Entry_61-Entry_60)/2
    dc.w (Entry_62-Entry_61)/2
    dc.w (Entry_63-Entry_62)/2
    dc.w (Entry_64-Entry_63)/2
    dc.w (Entry_65-Entry_64)/2
    dc.w (Entry_66-Entry_65)/2
    dc.w (Entry_67-Entry_66)/2
    dc.w (Entry_68-Entry_67)/2
    dc.w (Entry_69-Entry_68)/2
    dc.w (Entry_70-Entry_69)/2
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
Tk_51:  ; aga image capture : 00,0,0,0,0,0
    dc.w 1,56
    dc.b "aga image captur","e"+$80,"00,0,0,0,0,0",$FF
Tk_52:  ; aga bank image draw : 00,0,0,0
    dc.w 1,57
    dc.b "aga bank image dra","w"+$80,"00,0,0,0",$FF
Tk_53:  ; aga bank font select : 00
    dc.w 1,58
    dc.b "aga bank font selec","t"+$80,"00",$FF,0
Tk_54:  ; aga image region : 00,0,0,0,0,0,0,0
    dc.w 1,59
    dc.b "aga image regio","n"+$80,"00,0,0,0,0,0,0,0",$FF,0
Tk_55:  ; aga f icon : 00,0,0,0,0
    dc.w 1,60
    dc.b "aga f ico","n"+$80,"00,0,0,0,0",$FF,0
Tk_56:  ; aga f blit : 00,0,0,0,0
    dc.w 1,61
    dc.b "aga f bli","t"+$80,"00,0,0,0,0",$FF,0
Tk_57:  ; aga f icon bank create : 00,0
    dc.w 1,62
    dc.b "aga f icon bank creat","e"+$80,"00,0",$FF,0
Tk_58:  ; aga f icon bank put : 00,0,0,0
    dc.w 1,63
    dc.b "aga f icon bank pu","t"+$80,"00,0,0,0",$FF
Tk_59:  ; aga f chip bank create : 00,0
    dc.w 1,64
    dc.b "aga f chip bank creat","e"+$80,"00,0",$FF,0
Tk_60:  ; aga f chip stage : 00,0,0
    dc.w 1,65
    dc.b "aga f chip stag","e"+$80,"00,0,0",$FF,0
Tk_61:  ; aga f icon capture : 00,0,0,0
    dc.w 1,66
    dc.b "aga f icon captur","e"+$80,"00,0,0,0",$FF,0
Tk_62:  ; aga c block capture : 00,0,0,0,0,0
    dc.w 1,67
    dc.b "aga c block captur","e"+$80,"00,0,0,0,0,0",$FF
Tk_63:  ; aga c block draw : 00,0,0,0
    dc.w 1,68
    dc.b "aga c block dra","w"+$80,"00,0,0,0",$FF,0
Tk_64:  ; aga c block restore : 00,0
    dc.w 1,69
    dc.b "aga c block restor","e"+$80,"00,0",$FF
    dc.b $00,$00,$00,$00,$00,$00

C_Lib:

; -------- AP20 entry 00 : private/reserved --------
Entry_00:
Internal_00:
    cmp.l #$41506578,d1                               ; +$0000 : B2BC41506578
    bne.w L_000750                                    ; +$0006 : 6600002A
    lea L_0008BE(pc),a0                               ; +$000A : 41FA0194
    move.l a0,456(a5)                                 ; +$000E : 2B4801C8
    lea L_000756(pc),a0                               ; +$0012 : 41FA0024
    move.l a0,460(a5)                                 ; +$0016 : 2B4801CC
    move.l a0,464(a5)                                 ; +$001A : 2B4801D0
    lea L_0008BE(pc),a0                               ; +$001E : 41FA0180
    moveq #9,d0                                       ; +$0022 : 7009
L_000742:
    clr.l (a0)+                                       ; +$0024 : 4298
    dbra d0,L_000742                                  ; +$0026 : 51C8FFFC
    moveq #13,d0                                      ; +$002A : 700D
    move.w #$0200,d1                                  ; +$002C : 323C0200
    rts                                               ; +$0030 : 4E75
L_000750:
    moveq #-1,d0                                      ; +$0032 : 70FF
    suba.l a0,a0                                      ; +$0034 : 91C8
    rts                                               ; +$0036 : 4E75
L_000756:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0038 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$003C : 246D01C8
    bra.w L_0008E6                                    ; +$0040 : 60000186
L_000762:
    move.l a4,d0                                      ; +$0044 : 200C
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_000818                                    ; +$0048 : 670000B0
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_00077A                                    ; +$0054 : 67000006
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
L_00077A:
    move.l 20(a4),d0                                  ; +$005C : 202C0014
    tst.l d0                                          ; +$0060 : 4A80
    bra.w L_0007BC                                    ; +$0062 : 6000003A
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    movea.l $0004.w,a6                                ; +$006A : 2C780004
    nop                                               ; +$006E : 4E71
    nop                                               ; +$0070 : 4E71
    movea.l 12(a4),a0                                 ; +$0072 : 206C000C
    jsr -372(a6)                                      ; +$0076 : 4EAEFE8C
    tst.l d0                                          ; +$007A : 4A80
    beq.w L_0007BC                                    ; +$007C : 67000020
    movea.l 16(a4),a0                                 ; +$0080 : 206C0010
    movea.l $0004.w,a6                                ; +$0084 : 2C780004
    nop                                               ; +$0088 : 4E71
    nop                                               ; +$008A : 4E71
    movea.l 16(a4),a0                                 ; +$008C : 206C0010
    jsr -372(a6)                                      ; +$0090 : 4EAEFE8C
    tst.l d0                                          ; +$0094 : 4A80
    beq.w L_0007BC                                    ; +$0096 : 67000006
    clr.l 20(a4)                                      ; +$009A : 42AC0014
L_0007BC:
    movea.l (a2),a0                                   ; +$009E : 2052
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_0007EA                                    ; +$00A4 : 67000026
    movea.l 4(a2),a6                                  ; +$00A8 : 2C6A0004
    movea.l 4(a4),a1                                  ; +$00AC : 226C0004
    move.l a1,d0                                      ; +$00B0 : 2009
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_0007DA                                    ; +$00B4 : 67000006
    jsr -774(a6)                                      ; +$00B8 : 4EAEFCFA
L_0007DA:
    movea.l (a4),a1                                   ; +$00BC : 2254
    move.l a1,d0                                      ; +$00BE : 2009
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_0007EA                                    ; +$00C2 : 67000008
    movea.l (a2),a0                                   ; +$00C6 : 2052
    jsr -774(a6)                                      ; +$00C8 : 4EAEFCFA
L_0007EA:
    movea.l $0004.w,a6                                ; +$00CC : 2C780004
    movea.l 16(a4),a0                                 ; +$00D0 : 206C0010
    move.l a0,d0                                      ; +$00D4 : 2008
    tst.l d0                                          ; +$00D6 : 4A80
    beq.w L_0007FE                                    ; +$00D8 : 67000006
    jsr -672(a6)                                      ; +$00DC : 4EAEFD60
L_0007FE:
    movea.l 12(a4),a0                                 ; +$00E0 : 206C000C
    move.l a0,d0                                      ; +$00E4 : 2008
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_00080E                                    ; +$00E8 : 67000006
    jsr -672(a6)                                      ; +$00EC : 4EAEFD60
L_00080E:
    movea.l a4,a1                                     ; +$00F0 : 224C
    jsr -690(a6)                                      ; +$00F2 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$00F6 : 42AA0020
L_000818:
    tst.l (a2)                                        ; +$00FA : 4A92
    beq.w L_00082A                                    ; +$00FC : 6700000E
    movea.l (a2),a0                                   ; +$0100 : 2052
    movea.l 4(a2),a6                                  ; +$0102 : 2C6A0004
    jsr -66(a6)                                       ; +$0106 : 4EAEFFBE
    clr.l (a2)                                        ; +$010A : 4292
L_00082A:
    movea.l 8(a2),a1                                  ; +$010C : 226A0008
    move.l a1,d0                                      ; +$0110 : 2009
    tst.l d0                                          ; +$0112 : 4A80
    beq.w L_000842                                    ; +$0114 : 6700000E
    movea.l $0004.w,a6                                ; +$0118 : 2C780004
    jsr -414(a6)                                      ; +$011C : 4EAEFE62
    clr.l 8(a2)                                       ; +$0120 : 42AA0008
L_000842:
    movea.l 4(a2),a1                                  ; +$0124 : 226A0004
    move.l a1,d0                                      ; +$0128 : 2009
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_00085A                                    ; +$012C : 6700000E
    movea.l $0004.w,a6                                ; +$0130 : 2C780004
    jsr -414(a6)                                      ; +$0134 : 4EAEFE62
    clr.l 4(a2)                                       ; +$0138 : 42AA0004
L_00085A:
    lea 12(a2),a0                                     ; +$013C : 41EA000C
    moveq #4,d0                                       ; +$0140 : 7004
L_000860:
    clr.l (a0)+                                       ; +$0142 : 4298
    dbra d0,L_000860                                  ; +$0144 : 51C8FFFC
L_000866:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$0148 : 4CDF7FFF
    rts                                               ; +$014C : 4E75
L_00086C:
    movea.l 36(a2),a3                                 ; +$014E : 266A0024
    move.l a3,d0                                      ; +$0152 : 200B
    tst.l d0                                          ; +$0154 : 4A80
    beq.w L_0008B8                                    ; +$0156 : 67000042
    movea.l 86(a3),a4                                 ; +$015A : 286B0056
    move.l a4,d0                                      ; +$015E : 200C
    tst.l d0                                          ; +$0160 : 4A80
    beq.w L_00089E                                    ; +$0162 : 6700001C
L_000884:
    movea.l a4,a0                                     ; +$0166 : 204C
    movea.l $0004.w,a6                                ; +$0168 : 2C780004
    jsr -372(a6)                                      ; +$016C : 4EAEFE8C
    tst.l d0                                          ; +$0170 : 4A80
    beq.w L_00089E                                    ; +$0172 : 6700000C
    movea.l d0,a1                                     ; +$0176 : 2240
    jsr -378(a6)                                      ; +$0178 : 4EAEFE86
    bra.w L_000884                                    ; +$017C : 6000FFE8
L_00089E:
    movea.l 4(a2),a6                                  ; +$0180 : 2C6A0004
    move.l a6,d0                                      ; +$0184 : 200E
    tst.l d0                                          ; +$0186 : 4A80
    beq.w L_0008B0                                    ; +$0188 : 67000008
    movea.l a3,a0                                     ; +$018C : 204B
    bsr.w L_006C7C                                    ; +$018E : 610063CE
L_0008B0:
    move.l #$00000000,36(a2)                          ; +$0192 : 257C000000000024
L_0008B8:
    movea.l 32(a2),a4                                 ; +$019A : 286A0020
    rts                                               ; +$019E : 4E75
L_0008BE:
    dcb.b 40,0
L_0008E6:
    bsr.w L_0008FC                                    ; +$01C8 : 61000014
    tst.l d0                                          ; +$01CC : 4A80
    beq.w L_0008F8                                    ; +$01CE : 6700000A
    bsr.w L_00086C                                    ; +$01D2 : 6100FF7A
    bra.w L_000762                                    ; +$01D6 : 6000FE6C
L_0008F8:
    bra.w L_000866                                    ; +$01DA : 6000FF6C
L_0008FC:
    movea.l 32(a2),a4                                 ; +$01DE : 286A0020
    move.l a4,d0                                      ; +$01E2 : 200C
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_000934                                    ; +$01E6 : 6700002E
    moveq #0,d4                                       ; +$01EA : 7800
L_00090A:
    bsr.w L_00093C                                    ; +$01EC : 61000030
    tst.l d0                                          ; +$01F0 : 4A80
    beq.w L_000934                                    ; +$01F2 : 67000022
    addq.l #1,d4                                      ; +$01F6 : 5284
    cmpi.l #$0000012D,d4                              ; +$01F8 : 0C840000012D
    bge.w L_000938                                    ; +$01FE : 6C00001A
    movea.l 8(a2),a6                                  ; +$0202 : 2C6A0008
    move.l a6,d0                                      ; +$0206 : 200E
    tst.l d0                                          ; +$0208 : 4A80
    beq.w L_000938                                    ; +$020A : 6700000E
    jsr -270(a6)                                      ; +$020E : 4EAEFEF2
    bra.w L_00090A                                    ; +$0212 : 6000FFD8
L_000934:
    moveq #1,d0                                       ; +$0216 : 7001
    rts                                               ; +$0218 : 4E75
L_000938:
    moveq #0,d0                                       ; +$021A : 7000
    rts                                               ; +$021C : 4E75
L_00093C:
    move.l 20(a4),d6                                  ; +$021E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0222 : 028600000003
    btst #0,d6                                        ; +$0228 : 08060000
    beq.w L_00096C                                    ; +$022C : 67000020
    movea.l 12(a4),a0                                 ; +$0230 : 206C000C
    move.l a0,d0                                      ; +$0234 : 2008
    tst.l d0                                          ; +$0236 : 4A80
    beq.w L_00096C                                    ; +$0238 : 67000014
    movea.l $0004.w,a6                                ; +$023C : 2C780004
    jsr -372(a6)                                      ; +$0240 : 4EAEFE8C
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_00096C                                    ; +$0246 : 67000006
    bclr #0,d6                                        ; +$024A : 08860000
L_00096C:
    btst #1,d6                                        ; +$024E : 08060001
    beq.w L_000992                                    ; +$0252 : 67000020
    movea.l 16(a4),a0                                 ; +$0256 : 206C0010
    move.l a0,d0                                      ; +$025A : 2008
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_000992                                    ; +$025E : 67000014
    movea.l $0004.w,a6                                ; +$0262 : 2C780004
    jsr -372(a6)                                      ; +$0266 : 4EAEFE8C
    tst.l d0                                          ; +$026A : 4A80
    beq.w L_000992                                    ; +$026C : 67000006
    bclr #1,d6                                        ; +$0270 : 08860001
L_000992:
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
    beq.s L_0009FA                                    ; +$0016 : 6724
    lea L_000A08(pc),a1                               ; +$0018 : 43FA0030
    moveq #39,d0                                      ; +$001C : 7027
    jsr -552(a6)                                      ; +$001E : 4EAEFDD8
    tst.l d0                                          ; +$0022 : 4A80
    beq.s L_0009FA                                    ; +$0024 : 6716
    movea.l d0,a1                                     ; +$0026 : 2240
    move.b 236(a1),d1                                 ; +$0028 : 122900EC
    andi.b #$0C,d1                                    ; +$002C : 0201000C
    cmpi.b #$0C,d1                                    ; +$0030 : 0C01000C
    bne.s L_0009F6                                    ; +$0034 : 6602
    moveq #1,d3                                       ; +$0036 : 7601
L_0009F6:
    jsr -414(a6)                                      ; +$0038 : 4EAEFE62
L_0009FA:
    movea.l (a7)+,a6                                  ; +$003C : 2C5F
    movea.l (a7)+,a1                                  ; +$003E : 225F
    movea.l (a7)+,a0                                  ; +$0040 : 205F
    move.l (a7)+,d1                                   ; +$0042 : 221F
    move.l (a7)+,d0                                   ; +$0044 : 201F
    moveq #0,d2                                       ; +$0046 : 7400
    rts                                               ; +$0048 : 4E75
L_000A08:
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
    beq.w L_000B3C                                    ; +$0010 : 6700010C
    lea L_000B44(pc),a1                               ; +$0014 : 43FA0110
    moveq #39,d0                                      ; +$0018 : 7027
    jsr -552(a6)                                      ; +$001A : 4EAEFDD8
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_000B3C                                    ; +$0020 : 670000FC
    movea.l d0,a4                                     ; +$0024 : 2840
    movea.l $0004.w,a6                                ; +$0026 : 2C780004
    lea L_000B56(pc),a1                               ; +$002A : 43FA010C
    moveq #39,d0                                      ; +$002E : 7027
    jsr -552(a6)                                      ; +$0030 : 4EAEFDD8
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_000B32                                    ; +$0036 : 670000DC
    movea.l d0,a5                                     ; +$003A : 2A40
    move.b 236(a5),d0                                 ; +$003C : 102D00EC
    andi.b #$0C,d0                                    ; +$0040 : 0200000C
    cmpi.b #$0C,d0                                    ; +$0044 : 0C00000C
    bne.w L_000B28                                    ; +$0048 : 660000C0
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
    beq.w L_000B28                                    ; +$0098 : 67000070
    movea.l d0,a3                                     ; +$009C : 2640
    moveq #0,d6                                       ; +$009E : 7C00
L_000ABE:
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
    bne.w L_000ABE                                    ; +$00EA : 6600FFB4
    move.w #$0096,d7                                  ; +$00EE : 3E3C0096
L_000B10:
    movea.l a5,a6                                     ; +$00F2 : 2C4D
    jsr -270(a6)                                      ; +$00F4 : 4EAEFEF2
    dbra d7,L_000B10                                  ; +$00F8 : 51CFFFF8
    movea.l a3,a0                                     ; +$00FC : 204B
    movea.l a4,a6                                     ; +$00FE : 2C4C
    jsr -66(a6)                                       ; +$0100 : 4EAEFFBE
    moveq #1,d3                                       ; +$0104 : 7601
    bra.w L_000B28                                    ; +$0106 : 60000002
L_000B28:
    movea.l a5,a1                                     ; +$010A : 224D
    movea.l $0004.w,a6                                ; +$010C : 2C780004
    jsr -414(a6)                                      ; +$0110 : 4EAEFE62
L_000B32:
    movea.l a4,a1                                     ; +$0114 : 224C
    movea.l $0004.w,a6                                ; +$0116 : 2C780004
    jsr -414(a6)                                      ; +$011A : 4EAEFE62
L_000B3C:
    movem.l (a7)+,d0-d1/d4-d7/a0-a6                   ; +$011E : 4CDF7FF3
    moveq #0,d2                                       ; +$0122 : 7400
    rts                                               ; +$0124 : 4E75
L_000B44:
    dc.b "intuition.library"
    dc.b $00
L_000B56:
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
    beq.w L_000CC8                                    ; +$0016 : 67000144
    tst.l (a2)                                        ; +$001A : 4A92
    bne.w L_000CC8                                    ; +$001C : 6600013E
    cmpi.l #$00000001,d4                              ; +$0020 : 0C8400000001
    bcs.w L_000CC8                                    ; +$0026 : 65000134
    cmpi.l #$00007FFF,d4                              ; +$002A : 0C8400007FFF
    bhi.w L_000CC8                                    ; +$0030 : 6200012A
    move.l d4,d0                                      ; +$0034 : 2004
    andi.l #$00000000,d0                              ; +$0036 : 028000000000
    nop                                               ; +$003C : 4E71
    nop                                               ; +$003E : 4E71
    cmpi.l #$00000001,d5                              ; +$0040 : 0C8500000001
    bcs.w L_000CC8                                    ; +$0046 : 65000114
    cmpi.l #$00007FFF,d5                              ; +$004A : 0C8500007FFF
    bhi.w L_000CC8                                    ; +$0050 : 6200010A
    cmpi.l #$00000002,d6                              ; +$0054 : 0C8600000002
    bcs.w L_000CC8                                    ; +$005A : 65000100
    cmpi.l #$00000100,d6                              ; +$005E : 0C8600000100
    bhi.w L_000CC8                                    ; +$0064 : 620000F6
    move.l d6,d1                                      ; +$0068 : 2206
    subq.l #1,d1                                      ; +$006A : 5381
    and.l d6,d1                                       ; +$006C : C286
    bne.w L_000CC8                                    ; +$006E : 660000EC
    move.l d7,d0                                      ; +$0072 : 2007
    andi.l #$00000400,d0                              ; +$0074 : 028000000400
    bne.w L_000CC8                                    ; +$007A : 660000E0
    movea.l $0004.w,a6                                ; +$007E : 2C780004
    btst #1,297(a6)                                   ; +$0082 : 082E00010129
    beq.w L_000CC8                                    ; +$0088 : 670000D2
    lea L_000CD0(pc),a1                               ; +$008C : 43FA00D6
    moveq #39,d0                                      ; +$0090 : 7027
    jsr -552(a6)                                      ; +$0092 : 4EAEFDD8
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_000CC8                                    ; +$0098 : 670000C2
    movea.l d0,a4                                     ; +$009C : 2840
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    lea L_000CE2(pc),a1                               ; +$00A2 : 43FA00D2
    moveq #39,d0                                      ; +$00A6 : 7027
    jsr -552(a6)                                      ; +$00A8 : 4EAEFDD8
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_000CBE                                    ; +$00AE : 670000A2
    movea.l d0,a5                                     ; +$00B2 : 2A40
    move.b 236(a5),d0                                 ; +$00B4 : 102D00EC
    andi.b #$0C,d0                                    ; +$00B8 : 0200000C
    cmpi.b #$0C,d0                                    ; +$00BC : 0C00000C
    bne.w L_000CB0                                    ; +$00C0 : 66000082
    move.l d6,d1                                      ; +$00C4 : 2206
    moveq #0,d0                                       ; +$00C6 : 7000
L_000C34:
    lsr.l #1,d1                                       ; +$00C8 : E289
    addq.l #1,d0                                      ; +$00CA : 5280
    cmpi.l #$00000001,d1                              ; +$00CC : 0C8100000001
    bne.w L_000C34                                    ; +$00D2 : 6600FFF4
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
    bsr.w L_000CF4                                    ; +$010A : 6100007C
    nop                                               ; +$010E : 4E71
    suba.l a0,a0                                      ; +$0110 : 91C8
    movea.l a7,a1                                     ; +$0112 : 224F
    movea.l a4,a6                                     ; +$0114 : 2C4C
    bsr.w L_000DF8                                    ; +$0116 : 61000174
    lea 60(a7),a7                                     ; +$011A : 4FEF003C
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_000CB0                                    ; +$0120 : 67000022
    move.l d0,(a2)                                    ; +$0124 : 2480
    move.l a4,4(a2)                                   ; +$0126 : 254C0004
    move.l a5,8(a2)                                   ; +$012A : 254D0008
    move.l d4,12(a2)                                  ; +$012E : 2544000C
    move.l d5,16(a2)                                  ; +$0132 : 25450010
    move.l d6,20(a2)                                  ; +$0136 : 25460014
    bsr.w L_000E4A                                    ; +$013A : 610001A2
    bra.w L_000CC8                                    ; +$013E : 6000001C
    nop                                               ; +$0142 : 4E71
L_000CB0:
    clr.l 28(a2)                                      ; +$0144 : 42AA001C
    movea.l a5,a1                                     ; +$0148 : 224D
    movea.l $0004.w,a6                                ; +$014A : 2C780004
    jsr -414(a6)                                      ; +$014E : 4EAEFE62
L_000CBE:
    movea.l a4,a1                                     ; +$0152 : 224C
    movea.l $0004.w,a6                                ; +$0154 : 2C780004
    jsr -414(a6)                                      ; +$0158 : 4EAEFE62
L_000CC8:
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6             ; +$015C : 4CDF77F3
    moveq #0,d2                                       ; +$0160 : 7400
    rts                                               ; +$0162 : 4E75
L_000CD0:
    dc.b "intuition.library"
    dc.b $00
L_000CE2:
    dc.b "graphics.library"
    dc.b $00,$00
L_000CF4:
    move.l #$80000039,(a1)+                           ; +$0188 : 22FC80000039
    moveq #1,d0                                       ; +$018E : 7001
    move.l d0,(a1)+                                   ; +$0190 : 22C0
    moveq #0,d0                                       ; +$0192 : 7000
    move.l d0,(a1)+                                   ; +$0194 : 22C0
    move.l d0,(a1)+                                   ; +$0196 : 22C0
    rts                                               ; +$0198 : 4E75
L_000D06:
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
    beq.w L_000D8E                                    ; +$0214 : 6700000C
    move.l d1,36(a2)                                  ; +$0218 : 25410024
    moveq #1,d3                                       ; +$021C : 7601
    bra.w L_000DF2                                    ; +$021E : 60000066
L_000D8E:
    movea.l (a2),a0                                   ; +$0222 : 2052
    move.l a0,d0                                      ; +$0224 : 2008
    tst.l d0                                          ; +$0226 : 4A80
    beq.w L_000DA0                                    ; +$0228 : 6700000A
    movea.l 4(a2),a6                                  ; +$022C : 2C6A0004
    jsr -66(a6)                                       ; +$0230 : 4EAEFFBE
L_000DA0:
    movea.l 8(a2),a1                                  ; +$0234 : 226A0008
    move.l a1,d0                                      ; +$0238 : 2009
    tst.l d0                                          ; +$023A : 4A80
    beq.w L_000DB4                                    ; +$023C : 6700000A
    movea.l $0004.w,a6                                ; +$0240 : 2C780004
    jsr -414(a6)                                      ; +$0244 : 4EAEFE62
L_000DB4:
    movea.l 4(a2),a1                                  ; +$0248 : 226A0004
    move.l a1,d0                                      ; +$024C : 2009
    tst.l d0                                          ; +$024E : 4A80
    beq.w L_000DC8                                    ; +$0250 : 6700000A
    movea.l $0004.w,a6                                ; +$0254 : 2C780004
    jsr -414(a6)                                      ; +$0258 : 4EAEFE62
L_000DC8:
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
L_000DF2:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0286 : 4CDF7FF7
    rts                                               ; +$028A : 4E75
L_000DF8:
    move.l a1,d2                                      ; +$028C : 2409
    jsr -612(a6)                                      ; +$028E : 4EAEFD9C
    tst.l d0                                          ; +$0292 : 4A80
    bne.w L_000E44                                    ; +$0294 : 66000042
    move.l d7,d1                                      ; +$0298 : 2207
    andi.l #$FFFF0000,d1                              ; +$029A : 0281FFFF0000
    cmpi.l #$00010000,d1                              ; +$02A0 : 0C8100010000
    bne.w L_000E44                                    ; +$02A6 : 66000030
    move.l d7,d1                                      ; +$02AA : 2207
    addi.l #$00010000,d1                              ; +$02AC : 068100010000
    move.l a6,-(a7)                                   ; +$02B2 : 2F0E
    movea.l a5,a6                                     ; +$02B4 : 2C4D
    move.l d1,d0                                      ; +$02B6 : 2001
    jsr -798(a6)                                      ; +$02B8 : 4EAEFCE2
    movea.l (a7)+,a6                                  ; +$02BC : 2C5F
    tst.l d0                                          ; +$02BE : 4A80
    bne.w L_000E46                                    ; +$02C0 : 66000018
    move.l d7,d1                                      ; +$02C4 : 2207
    addi.l #$00010000,d1                              ; +$02C6 : 068100010000
    movea.l d2,a1                                     ; +$02CC : 2242
    move.l d1,28(a1)                                  ; +$02CE : 2341001C
    suba.l a0,a0                                      ; +$02D2 : 91C8
    jsr -612(a6)                                      ; +$02D4 : 4EAEFD9C
L_000E44:
    rts                                               ; +$02D8 : 4E75
L_000E46:
    moveq #0,d0                                       ; +$02DA : 7000
    rts                                               ; +$02DC : 4E75
L_000E4A:
    bsr.w L_000D06                                    ; +$02DE : 6100FEBA
    lea 11932(a2),a0                                  ; +$02E2 : 41EA2E9C
    moveq #35,d0                                      ; +$02E6 : 7023
L_000E54:
    clr.l (a0)+                                       ; +$02E8 : 4298
    dbra d0,L_000E54                                  ; +$02EA : 51C8FFFC
    rts                                               ; +$02EE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 07 : aga screen pattern --------
Entry_07:
Aga_Screen_Pattern:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)                   ; +$0000 : 48E7FFEE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    move.l a2,d0                                      ; +$0008 : 200A
    tst.l d0                                          ; +$000A : 4A80
    beq.w L_000EEC                                    ; +$000C : 6700007E
    tst.l (a2)                                        ; +$0010 : 4A92
    beq.w L_000EEC                                    ; +$0012 : 67000078
    movea.l (a2),a4                                   ; +$0016 : 2852
    movea.l 8(a2),a6                                  ; +$0018 : 2C6A0008
    move.l 20(a2),d4                                  ; +$001C : 282A0014
    move.l 16(a2),d5                                  ; +$0020 : 2A2A0010
    moveq #0,d6                                       ; +$0024 : 7C00
L_000E86:
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
    bne.w L_000E86                                    ; +$0088 : 6600FF9C
L_000EEC:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6                   ; +$008C : 4CDF77FF
    rts                                               ; +$0090 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 08 : aga screen close --------
Entry_08:
Aga_Screen_Close:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$0000 : 48E7FFFE
    movea.l 456(a5),a2                                ; +$0004 : 246D01C8
    bra.w L_00101C                                    ; +$0008 : 6000011C
L_000F02:
    move.l a4,d0                                      ; +$000C : 200C
    tst.l d0                                          ; +$000E : 4A80
    beq.w L_000F76                                    ; +$0010 : 6700006E
    movea.l 8(a2),a6                                  ; +$0014 : 2C6A0008
    move.l a6,d0                                      ; +$0018 : 200E
    tst.l d0                                          ; +$001A : 4A80
    beq.w L_000F1A                                    ; +$001C : 67000006
    jsr -228(a6)                                      ; +$0020 : 4EAEFF1C
L_000F1A:
    movea.l (a2),a0                                   ; +$0024 : 2052
    move.l a0,d0                                      ; +$0026 : 2008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_000F48                                    ; +$002A : 67000026
    movea.l 4(a2),a6                                  ; +$002E : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0032 : 226C0004
    move.l a1,d0                                      ; +$0036 : 2009
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_000F38                                    ; +$003A : 67000006
    jsr -774(a6)                                      ; +$003E : 4EAEFCFA
L_000F38:
    movea.l (a4),a1                                   ; +$0042 : 2254
    move.l a1,d0                                      ; +$0044 : 2009
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_000F48                                    ; +$0048 : 67000008
    movea.l (a2),a0                                   ; +$004C : 2052
    jsr -774(a6)                                      ; +$004E : 4EAEFCFA
L_000F48:
    movea.l $0004.w,a6                                ; +$0052 : 2C780004
    movea.l 16(a4),a0                                 ; +$0056 : 206C0010
    move.l a0,d0                                      ; +$005A : 2008
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_000F5C                                    ; +$005E : 67000006
    jsr -672(a6)                                      ; +$0062 : 4EAEFD60
L_000F5C:
    movea.l 12(a4),a0                                 ; +$0066 : 206C000C
    move.l a0,d0                                      ; +$006A : 2008
    tst.l d0                                          ; +$006C : 4A80
    beq.w L_000F6C                                    ; +$006E : 67000006
    jsr -672(a6)                                      ; +$0072 : 4EAEFD60
L_000F6C:
    movea.l a4,a1                                     ; +$0076 : 224C
    jsr -690(a6)                                      ; +$0078 : 4EAEFD4E
    clr.l 32(a2)                                      ; +$007C : 42AA0020
L_000F76:
    tst.l (a2)                                        ; +$0080 : 4A92
    beq.w L_000F88                                    ; +$0082 : 6700000E
    movea.l (a2),a0                                   ; +$0086 : 2052
    movea.l 4(a2),a6                                  ; +$0088 : 2C6A0004
    bsr.w L_00593C                                    ; +$008C : 610049B8
    clr.l (a2)                                        ; +$0090 : 4292
L_000F88:
    movea.l 8(a2),a1                                  ; +$0092 : 226A0008
    move.l a1,d0                                      ; +$0096 : 2009
    tst.l d0                                          ; +$0098 : 4A80
    beq.w L_000FA0                                    ; +$009A : 6700000E
    movea.l $0004.w,a6                                ; +$009E : 2C780004
    jsr -414(a6)                                      ; +$00A2 : 4EAEFE62
    clr.l 8(a2)                                       ; +$00A6 : 42AA0008
L_000FA0:
    movea.l 4(a2),a1                                  ; +$00AA : 226A0004
    move.l a1,d0                                      ; +$00AE : 2009
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_000FB8                                    ; +$00B2 : 6700000E
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    jsr -414(a6)                                      ; +$00BA : 4EAEFE62
    clr.l 4(a2)                                       ; +$00BE : 42AA0004
L_000FB8:
    lea 12(a2),a0                                     ; +$00C2 : 41EA000C
    moveq #4,d0                                       ; +$00C6 : 7004
L_000FBE:
    clr.l (a0)+                                       ; +$00C8 : 4298
    dbra d0,L_000FBE                                  ; +$00CA : 51C8FFFC
L_000FC4:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$00CE : 4CDF7FFF
    rts                                               ; +$00D2 : 4E75
L_000FCA:
    movea.l 36(a2),a3                                 ; +$00D4 : 266A0024
    move.l a3,d0                                      ; +$00D8 : 200B
    tst.l d0                                          ; +$00DA : 4A80
    beq.w L_001016                                    ; +$00DC : 67000042
    movea.l 86(a3),a4                                 ; +$00E0 : 286B0056
    move.l a4,d0                                      ; +$00E4 : 200C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_000FFC                                    ; +$00E8 : 6700001C
L_000FE2:
    movea.l a4,a0                                     ; +$00EC : 204C
    movea.l $0004.w,a6                                ; +$00EE : 2C780004
    jsr -372(a6)                                      ; +$00F2 : 4EAEFE8C
    tst.l d0                                          ; +$00F6 : 4A80
    beq.w L_000FFC                                    ; +$00F8 : 6700000C
    movea.l d0,a1                                     ; +$00FC : 2240
    jsr -378(a6)                                      ; +$00FE : 4EAEFE86
    bra.w L_000FE2                                    ; +$0102 : 6000FFE8
L_000FFC:
    movea.l 4(a2),a6                                  ; +$0106 : 2C6A0004
    move.l a6,d0                                      ; +$010A : 200E
    tst.l d0                                          ; +$010C : 4A80
    beq.w L_00100E                                    ; +$010E : 67000008
    movea.l a3,a0                                     ; +$0112 : 204B
    bsr.w L_006C7C                                    ; +$0114 : 61005C70
L_00100E:
    move.l #$00000000,36(a2)                          ; +$0118 : 257C000000000024
L_001016:
    movea.l 32(a2),a4                                 ; +$0120 : 286A0020
    rts                                               ; +$0124 : 4E75
L_00101C:
    bsr.w L_001032                                    ; +$0126 : 61000014
    tst.l d0                                          ; +$012A : 4A80
    beq.w L_00102E                                    ; +$012C : 6700000A
    bsr.w L_000FCA                                    ; +$0130 : 6100FFA2
    bra.w L_000F02                                    ; +$0134 : 6000FED6
L_00102E:
    bra.w L_000FC4                                    ; +$0138 : 6000FF94
L_001032:
    movea.l 32(a2),a4                                 ; +$013C : 286A0020
    move.l a4,d0                                      ; +$0140 : 200C
    tst.l d0                                          ; +$0142 : 4A80
    beq.w L_00106A                                    ; +$0144 : 6700002E
    moveq #0,d4                                       ; +$0148 : 7800
L_001040:
    bsr.w L_001072                                    ; +$014A : 61000030
    tst.l d0                                          ; +$014E : 4A80
    beq.w L_00106A                                    ; +$0150 : 67000022
    addq.l #1,d4                                      ; +$0154 : 5284
    cmpi.l #$0000012D,d4                              ; +$0156 : 0C840000012D
    bge.w L_00106E                                    ; +$015C : 6C00001A
    movea.l 8(a2),a6                                  ; +$0160 : 2C6A0008
    move.l a6,d0                                      ; +$0164 : 200E
    tst.l d0                                          ; +$0166 : 4A80
    beq.w L_00106E                                    ; +$0168 : 6700000E
    jsr -270(a6)                                      ; +$016C : 4EAEFEF2
    bra.w L_001040                                    ; +$0170 : 6000FFD8
L_00106A:
    moveq #1,d0                                       ; +$0174 : 7001
    rts                                               ; +$0176 : 4E75
L_00106E:
    moveq #0,d0                                       ; +$0178 : 7000
    rts                                               ; +$017A : 4E75
L_001072:
    move.l 20(a4),d6                                  ; +$017C : 2C2C0014
    andi.l #$00000003,d6                              ; +$0180 : 028600000003
    btst #0,d6                                        ; +$0186 : 08060000
    beq.w L_0010A2                                    ; +$018A : 67000020
    movea.l 12(a4),a0                                 ; +$018E : 206C000C
    move.l a0,d0                                      ; +$0192 : 2008
    tst.l d0                                          ; +$0194 : 4A80
    beq.w L_0010A2                                    ; +$0196 : 67000014
    movea.l $0004.w,a6                                ; +$019A : 2C780004
    jsr -372(a6)                                      ; +$019E : 4EAEFE8C
    tst.l d0                                          ; +$01A2 : 4A80
    beq.w L_0010A2                                    ; +$01A4 : 67000006
    bclr #0,d6                                        ; +$01A8 : 08860000
L_0010A2:
    btst #1,d6                                        ; +$01AC : 08060001
    beq.w L_0010C8                                    ; +$01B0 : 67000020
    movea.l 16(a4),a0                                 ; +$01B4 : 206C0010
    move.l a0,d0                                      ; +$01B8 : 2008
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_0010C8                                    ; +$01BC : 67000014
    movea.l $0004.w,a6                                ; +$01C0 : 2C780004
    jsr -372(a6)                                      ; +$01C4 : 4EAEFE8C
    tst.l d0                                          ; +$01C8 : 4A80
    beq.w L_0010C8                                    ; +$01CA : 67000006
    bclr #1,d6                                        ; +$01CE : 08860001
L_0010C8:
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
    beq.s L_0010E8                                    ; +$000A : 6708
    movea.l 8(a2),a6                                  ; +$000C : 2C6A0008
    jsr -270(a6)                                      ; +$0010 : 4EAEFEF2
L_0010E8:
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
    beq.w L_001208                                    ; +$000C : 67000108
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    bne.w L_0011BA                                    ; +$0018 : 660000AE
    moveq #24,d0                                      ; +$001C : 7018
    move.l #$00010001,d1                              ; +$001E : 223C00010001
    movea.l $0004.w,a6                                ; +$0024 : 2C780004
    jsr -684(a6)                                      ; +$0028 : 4EAEFD54
    tst.l d0                                          ; +$002C : 4A80
    beq.w L_001208                                    ; +$002E : 670000E6
    movea.l d0,a4                                     ; +$0032 : 2840
    movea.l $0004.w,a6                                ; +$0034 : 2C780004
    jsr -666(a6)                                      ; +$0038 : 4EAEFD66
    tst.l d0                                          ; +$003C : 4A80
    beq.w L_0011FE                                    ; +$003E : 670000CC
    move.l d0,12(a4)                                  ; +$0042 : 2940000C
    movea.l $0004.w,a6                                ; +$0046 : 2C780004
    jsr -666(a6)                                      ; +$004A : 4EAEFD66
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_0011DA                                    ; +$0050 : 67000096
    move.l d0,16(a4)                                  ; +$0054 : 29400010
    movea.l (a2),a0                                   ; +$0058 : 2052
    suba.l a1,a1                                      ; +$005A : 93C9
    moveq #1,d0                                       ; +$005C : 7001
    movea.l 4(a2),a6                                  ; +$005E : 2C6A0004
    jsr -768(a6)                                      ; +$0062 : 4EAEFD00
    tst.l d0                                          ; +$0066 : 4A80
    beq.w L_0011DA                                    ; +$0068 : 6700007E
    move.l d0,(a4)                                    ; +$006C : 2880
    movea.l (a2),a0                                   ; +$006E : 2052
    suba.l a1,a1                                      ; +$0070 : 93C9
    moveq #2,d0                                       ; +$0072 : 7002
    movea.l 4(a2),a6                                  ; +$0074 : 2C6A0004
    jsr -768(a6)                                      ; +$0078 : 4EAEFD00
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_0011CE                                    ; +$007E : 6700005C
    move.l d0,4(a4)                                   ; +$0082 : 29400004
    movea.l (a4),a0                                   ; +$0086 : 2054
    movea.l 4(a0),a0                                  ; +$0088 : 20680004
    move.l a0,d0                                      ; +$008C : 2008
    tst.l d0                                          ; +$008E : 4A80
    beq.w L_0011C0                                    ; +$0090 : 6700003C
    move.l 12(a4),d0                                  ; +$0094 : 202C000C
    move.l d0,22(a0)                                  ; +$0098 : 21400016
    move.l 16(a4),d0                                  ; +$009C : 202C0010
    move.l d0,54(a0)                                  ; +$00A0 : 21400036
    movea.l 4(a4),a0                                  ; +$00A4 : 206C0004
    movea.l 4(a0),a0                                  ; +$00A8 : 20680004
    move.l a0,d0                                      ; +$00AC : 2008
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_0011C0                                    ; +$00B0 : 6700001C
    move.l 12(a4),d0                                  ; +$00B4 : 202C000C
    move.l d0,22(a0)                                  ; +$00B8 : 21400016
    move.l 16(a4),d0                                  ; +$00BC : 202C0010
    move.l d0,54(a0)                                  ; +$00C0 : 21400036
    move.l a4,32(a2)                                  ; +$00C4 : 254C0020
L_0011BA:
    moveq #1,d3                                       ; +$00C8 : 7601
    bra.w L_001208                                    ; +$00CA : 6000004A
L_0011C0:
    movea.l (a2),a0                                   ; +$00CE : 2052
    movea.l 4(a4),a1                                  ; +$00D0 : 226C0004
    movea.l 4(a2),a6                                  ; +$00D4 : 2C6A0004
    jsr -774(a6)                                      ; +$00D8 : 4EAEFCFA
L_0011CE:
    movea.l (a2),a0                                   ; +$00DC : 2052
    movea.l (a4),a1                                   ; +$00DE : 2254
    movea.l 4(a2),a6                                  ; +$00E0 : 2C6A0004
    jsr -774(a6)                                      ; +$00E4 : 4EAEFCFA
L_0011DA:
    movea.l $0004.w,a6                                ; +$00E8 : 2C780004
    movea.l 16(a4),a0                                 ; +$00EC : 206C0010
    move.l a0,d0                                      ; +$00F0 : 2008
    tst.l d0                                          ; +$00F2 : 4A80
    beq.w L_0011EE                                    ; +$00F4 : 67000006
    jsr -672(a6)                                      ; +$00F8 : 4EAEFD60
L_0011EE:
    movea.l 12(a4),a0                                 ; +$00FC : 206C000C
    move.l a0,d0                                      ; +$0100 : 2008
    tst.l d0                                          ; +$0102 : 4A80
    beq.w L_0011FE                                    ; +$0104 : 67000006
    jsr -672(a6)                                      ; +$0108 : 4EAEFD60
L_0011FE:
    movea.l a4,a1                                     ; +$010C : 224C
    movea.l $0004.w,a6                                ; +$010E : 2C780004
    jsr -690(a6)                                      ; +$0112 : 4EAEFD4E
L_001208:
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
    beq.w L_0012A6                                    ; +$000C : 67000084
    movea.l 32(a2),a4                                 ; +$0010 : 286A0020
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_0012A6                                    ; +$0018 : 67000078
    move.l 12(a4),d0                                  ; +$001C : 202C000C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0012A6                                    ; +$0022 : 6700006E
    move.l 16(a4),d0                                  ; +$0026 : 202C0010
    tst.l d0                                          ; +$002A : 4A80
    beq.w L_0012A6                                    ; +$002C : 67000064
    bsr.w L_0012AE                                    ; +$0030 : 61000068
    tst.l d0                                          ; +$0034 : 4A80
    bne.w L_0012A6                                    ; +$0036 : 6600005A
    move.l 8(a4),d0                                   ; +$003A : 202C0008
    tst.l d0                                          ; +$003E : 4A80
    beq.w L_00125E                                    ; +$0040 : 67000008
    moveq #0,d7                                       ; +$0044 : 7E00
    bra.w L_001260                                    ; +$0046 : 60000004
L_00125E:
    moveq #1,d7                                       ; +$004A : 7E01
L_001260:
    movea.l 8(a2),a6                                  ; +$004C : 2C6A0008
    move.l a6,d0                                      ; +$0050 : 200E
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0012A6                                    ; +$0054 : 6700003C
    jsr -228(a6)                                      ; +$0058 : 4EAEFF1C
    tst.l d7                                          ; +$005C : 4A87
    beq.w L_00127E                                    ; +$005E : 6700000A
    movea.l 4(a4),a1                                  ; +$0062 : 226C0004
    bra.w L_001280                                    ; +$0066 : 60000004
L_00127E:
    movea.l (a4),a1                                   ; +$006A : 2254
L_001280:
    move.l a1,d0                                      ; +$006C : 2009
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_0012A6                                    ; +$0070 : 67000020
    movea.l (a2),a0                                   ; +$0074 : 2052
    movea.l 4(a2),a6                                  ; +$0076 : 2C6A0004
    jsr -780(a6)                                      ; +$007A : 4EAEFCF4
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_0012A6                                    ; +$0080 : 67000010
    move.l d7,8(a4)                                   ; +$0084 : 29470008
    move.l #$00000003,20(a4)                          ; +$0088 : 297C000000030014
    moveq #1,d3                                       ; +$0090 : 7601
L_0012A6:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0092 : 4CDF7FF7
    moveq #0,d2                                       ; +$0096 : 7400
    rts                                               ; +$0098 : 4E75
L_0012AE:
    move.l 20(a4),d6                                  ; +$009A : 2C2C0014
    andi.l #$00000003,d6                              ; +$009E : 028600000003
    btst #0,d6                                        ; +$00A4 : 08060000
    beq.w L_0012DE                                    ; +$00A8 : 67000020
    movea.l 12(a4),a0                                 ; +$00AC : 206C000C
    move.l a0,d0                                      ; +$00B0 : 2008
    tst.l d0                                          ; +$00B2 : 4A80
    beq.w L_0012DE                                    ; +$00B4 : 67000014
    movea.l $0004.w,a6                                ; +$00B8 : 2C780004
    jsr -372(a6)                                      ; +$00BC : 4EAEFE8C
    tst.l d0                                          ; +$00C0 : 4A80
    beq.w L_0012DE                                    ; +$00C2 : 67000006
    bclr #0,d6                                        ; +$00C6 : 08860000
L_0012DE:
    btst #1,d6                                        ; +$00CA : 08060001
    beq.w L_001304                                    ; +$00CE : 67000020
    movea.l 16(a4),a0                                 ; +$00D2 : 206C0010
    move.l a0,d0                                      ; +$00D6 : 2008
    tst.l d0                                          ; +$00D8 : 4A80
    beq.w L_001304                                    ; +$00DA : 67000014
    movea.l $0004.w,a6                                ; +$00DE : 2C780004
    jsr -372(a6)                                      ; +$00E2 : 4EAEFE8C
    tst.l d0                                          ; +$00E6 : 4A80
    beq.w L_001304                                    ; +$00E8 : 67000006
    bclr #1,d6                                        ; +$00EC : 08860001
L_001304:
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
    beq.w L_0013A4                                    ; +$000E : 67000084
    tst.l (a2)                                        ; +$0012 : 4A92
    beq.w L_0013A4                                    ; +$0014 : 6700007E
    movea.l 32(a2),a3                                 ; +$0018 : 266A0020
    move.l a3,d0                                      ; +$001C : 200B
    tst.l d0                                          ; +$001E : 4A80
    beq.w L_0013A4                                    ; +$0020 : 67000072
    move.l 8(a3),d0                                   ; +$0024 : 202B0008
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_001344                                    ; +$002A : 67000008
    movea.l (a3),a1                                   ; +$002E : 2253
    bra.w L_001348                                    ; +$0030 : 60000006
L_001344:
    movea.l 4(a3),a1                                  ; +$0034 : 226B0004
L_001348:
    move.l a1,d0                                      ; +$0038 : 2009
    tst.l d0                                          ; +$003A : 4A80
    beq.w L_0013A4                                    ; +$003C : 67000056
    movea.l (a1),a4                                   ; +$0040 : 2851
    move.l a4,d0                                      ; +$0042 : 200C
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_0013A4                                    ; +$0046 : 6700004C
    move.l #$00000080,d0                              ; +$004A : 203C00000080
    move.l #$00010001,d1                              ; +$0050 : 223C00010001
    movea.l $0004.w,a6                                ; +$0056 : 2C780004
    jsr -684(a6)                                      ; +$005A : 4EAEFD54
    tst.l d0                                          ; +$005E : 4A80
    beq.w L_0013A4                                    ; +$0060 : 67000032
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
L_0013A4:
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
    bsr.w L_001540                                    ; +$011A : 61000076
    tst.l d0                                          ; +$011E : 4A80
    beq.w L_00152A                                    ; +$0120 : 6700005A
    bsr.w L_00166E                                    ; +$0124 : 6100019A
    tst.l d0                                          ; +$0128 : 4A80
    beq.w L_00152A                                    ; +$012A : 67000050
    bsr.w L_0018C6                                    ; +$012E : 610003E8
    tst.l d0                                          ; +$0132 : 4A80
    beq.w L_00152A                                    ; +$0134 : 67000046
    bsr.w L_0019D2                                    ; +$0138 : 610004EA
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_00152A                                    ; +$013E : 6700003C
    bsr.w L_001B04                                    ; +$0142 : 61000612
    tst.l d0                                          ; +$0146 : 4A80
    beq.w L_00152A                                    ; +$0148 : 67000032
    movea.l (a5),a2                                   ; +$014C : 2455
    movea.l 8(a2),a6                                  ; +$014E : 2C6A0008
    jsr -228(a6)                                      ; +$0152 : 4EAEFF1C
    move.l #$00000001,100(a5)                         ; +$0156 : 2B7C000000010064
    bsr.w L_0019D2                                    ; +$015E : 610004C4
    tst.l d0                                          ; +$0162 : 4A80
    beq.w L_00152A                                    ; +$0164 : 67000016
    bsr.w L_001B80                                    ; +$0168 : 61000668
    tst.l d0                                          ; +$016C : 4A80
    beq.w L_00152A                                    ; +$016E : 6700000C
    move.l #$00000001,d3                              ; +$0172 : 263C00000001
    bra.w L_001530                                    ; +$0178 : 60000008
L_00152A:
    move.l #$00000000,d3                              ; +$017C : 263C00000000
L_001530:
    bsr.w L_001BBA                                    ; +$0182 : 61000688
    lea 128(a7),a7                                    ; +$0186 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$018A : 4CDF7FF7
    moveq #0,d2                                       ; +$018E : 7400
    rts                                               ; +$0190 : 4E75
L_001540:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0192 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$0196 : 246D0004
    move.l #$00000000,d4                              ; +$019A : 283C00000000
    move.w (a2)+,d4                                   ; +$01A0 : 381A
    tst.l d4                                          ; +$01A2 : 4A84
    beq.w L_001660                                    ; +$01A4 : 6700010C
    move.l d4,d0                                      ; +$01A8 : 2004
    addq.l #1,d0                                      ; +$01AA : 5280
    move.l #$00010001,d1                              ; +$01AC : 223C00010001
    movea.l $0004.w,a6                                ; +$01B2 : 2C780004
    jsr -684(a6)                                      ; +$01B6 : 4EAEFD54
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_001660                                    ; +$01BC : 670000F4
    move.l d0,12(a5)                                  ; +$01C0 : 2B40000C
    movea.l d0,a1                                     ; +$01C4 : 2240
L_001574:
    move.b (a2)+,(a1)+                                ; +$01C6 : 12DA
    subq.l #1,d4                                      ; +$01C8 : 5384
    bne.w L_001574                                    ; +$01CA : 6600FFFA
    lea L_001C3A(pc),a1                               ; +$01CE : 43FA06BC
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    movea.l $0004.w,a6                                ; +$01D8 : 2C780004
    jsr -552(a6)                                      ; +$01DC : 4EAEFDD8
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_001660                                    ; +$01E2 : 670000CE
    move.l d0,16(a5)                                  ; +$01E6 : 2B400010
    movea.l d0,a6                                     ; +$01EA : 2C40
    move.l 12(a5),d1                                  ; +$01EC : 222D000C
    move.l #$000003ED,d2                              ; +$01F0 : 243C000003ED
    jsr -30(a6)                                       ; +$01F6 : 4EAEFFE2
    tst.l d0                                          ; +$01FA : 4A80
    beq.w L_001660                                    ; +$01FC : 670000B4
    move.l d0,20(a5)                                  ; +$0200 : 2B400014
    move.l d0,d1                                      ; +$0204 : 2200
    move.l a5,d2                                      ; +$0206 : 240D
    addi.l #$00000068,d2                              ; +$0208 : 068200000068
    move.l #$0000000C,d3                              ; +$020E : 263C0000000C
    jsr -42(a6)                                       ; +$0214 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$0218 : 0C800000000C
    bne.w L_001660                                    ; +$021E : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0222 : 0CAD464F524D0068
    bne.w L_001660                                    ; +$022A : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$022E : 0CAD494C424D0070
    bne.w L_001660                                    ; +$0236 : 6600007A
    move.l 108(a5),d4                                 ; +$023A : 282D006C
    cmpi.l #$00000004,d4                              ; +$023E : 0C8400000004
    bcs.w L_001660                                    ; +$0244 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$0248 : 0C847FFFFFF7
    bhi.w L_001660                                    ; +$024E : 62000062
    addq.l #8,d4                                      ; +$0252 : 5084
    move.l d4,28(a5)                                  ; +$0254 : 2B44001C
    move.l d4,d0                                      ; +$0258 : 2004
    move.l #$00010001,d1                              ; +$025A : 223C00010001
    movea.l $0004.w,a6                                ; +$0260 : 2C780004
    jsr -684(a6)                                      ; +$0264 : 4EAEFD54
    tst.l d0                                          ; +$0268 : 4A80
    beq.w L_001660                                    ; +$026A : 67000046
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
    bne.w L_001660                                    ; +$02A4 : 6600000C
    move.l #$00000001,d0                              ; +$02A8 : 203C00000001
    bra.w L_001666                                    ; +$02AE : 60000008
L_001660:
    move.l #$00000000,d0                              ; +$02B2 : 203C00000000
L_001666:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$02B8 : 4CDF5FFE
    tst.l d0                                          ; +$02BC : 4A80
    rts                                               ; +$02BE : 4E75
L_00166E:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$02C0 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$02C4 : 206D0018
    move.l 28(a5),d7                                  ; +$02C8 : 2E2D001C
    subi.l #$0000000C,d7                              ; +$02CC : 04870000000C
    move.l a0,d0                                      ; +$02D2 : 2008
    addi.l #$0000000C,d0                              ; +$02D4 : 06800000000C
    movea.l d0,a0                                     ; +$02DA : 2040
L_00168A:
    tst.l d7                                          ; +$02DC : 4A87
    beq.w L_00174E                                    ; +$02DE : 670000C0
    cmpi.l #$00000008,d7                              ; +$02E2 : 0C8700000008
    bcs.w L_0018B8                                    ; +$02E8 : 65000220
    move.l (a0)+,d3                                   ; +$02EC : 2618
    move.l (a0)+,d2                                   ; +$02EE : 2418
    subq.l #8,d7                                      ; +$02F0 : 5187
    cmp.l d7,d2                                       ; +$02F2 : B487
    bhi.w L_0018B8                                    ; +$02F4 : 62000214
    move.l d2,d1                                      ; +$02F8 : 2202
    andi.l #$00000001,d1                              ; +$02FA : 028100000001
    add.l d2,d1                                       ; +$0300 : D282
    cmp.l d7,d1                                       ; +$0302 : B287
    bhi.w L_0018B8                                    ; +$0304 : 62000204
    sub.l d1,d7                                       ; +$0308 : 9E81
    cmpi.l #$424D4844,d3                              ; +$030A : 0C83424D4844
    beq.w L_0016E4                                    ; +$0310 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0314 : 0C83434D4150
    beq.w L_0016FE                                    ; +$031A : 67000034
    cmpi.l #$43414D47,d3                              ; +$031E : 0C8343414D47
    beq.w L_001726                                    ; +$0324 : 67000052
    cmpi.l #$424F4459,d3                              ; +$0328 : 0C83424F4459
    beq.w L_001712                                    ; +$032E : 67000034
    bra.w L_001744                                    ; +$0332 : 60000062
L_0016E4:
    tst.l 32(a5)                                      ; +$0336 : 4AAD0020
    bne.w L_0018B8                                    ; +$033A : 660001CE
    cmpi.l #$00000014,d2                              ; +$033E : 0C8200000014
    bne.w L_0018B8                                    ; +$0344 : 660001C4
    move.l a0,32(a5)                                  ; +$0348 : 2B480020
    bra.w L_001744                                    ; +$034C : 60000048
L_0016FE:
    tst.l 36(a5)                                      ; +$0350 : 4AAD0024
    bne.w L_0018B8                                    ; +$0354 : 660001B4
    move.l a0,36(a5)                                  ; +$0358 : 2B480024
    move.l d2,40(a5)                                  ; +$035C : 2B420028
    bra.w L_001744                                    ; +$0360 : 60000034
L_001712:
    tst.l 44(a5)                                      ; +$0364 : 4AAD002C
    bne.w L_0018B8                                    ; +$0368 : 660001A0
    move.l a0,44(a5)                                  ; +$036C : 2B48002C
    move.l d2,48(a5)                                  ; +$0370 : 2B420030
    bra.w L_001744                                    ; +$0374 : 60000020
L_001726:
    tst.l 52(a5)                                      ; +$0378 : 4AAD0034
    bne.w L_0018B8                                    ; +$037C : 6600018C
    cmpi.l #$00000004,d2                              ; +$0380 : 0C8200000004
    bne.w L_0018B8                                    ; +$0386 : 66000182
    move.l #$00000001,52(a5)                          ; +$038A : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$0392 : 2B50005C
L_001744:
    move.l a0,d0                                      ; +$0396 : 2008
    add.l d1,d0                                       ; +$0398 : D081
    movea.l d0,a0                                     ; +$039A : 2040
    bra.w L_00168A                                    ; +$039C : 6000FF3E
L_00174E:
    tst.l 32(a5)                                      ; +$03A0 : 4AAD0020
    beq.w L_0018B8                                    ; +$03A4 : 67000164
    tst.l 36(a5)                                      ; +$03A8 : 4AAD0024
    beq.w L_0018B8                                    ; +$03AC : 6700015C
    tst.l 44(a5)                                      ; +$03B0 : 4AAD002C
    beq.w L_0018B8                                    ; +$03B4 : 67000154
    tst.l 48(a5)                                      ; +$03B8 : 4AAD0030
    beq.w L_0018B8                                    ; +$03BC : 6700014C
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
    beq.w L_0018B8                                    ; +$040C : 670000FC
    tst.l 60(a5)                                      ; +$0410 : 4AAD003C
    beq.w L_0018B8                                    ; +$0414 : 670000F4
    tst.l 64(a5)                                      ; +$0418 : 4AAD0040
    beq.w L_0018B8                                    ; +$041C : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0420 : 0CAD000000080040
    bhi.w L_0018B8                                    ; +$0428 : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$042C : 0CAD000000020044
    bhi.w L_0018B8                                    ; +$0434 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$0438 : 0CAD000000010048
    bhi.w L_0018B8                                    ; +$0440 : 620000C8
    move.l 40(a5),d0                                  ; +$0444 : 202D0028
    tst.l d0                                          ; +$0448 : 4A80
    beq.w L_0018B8                                    ; +$044A : 670000BE
    cmpi.l #$00000300,d0                              ; +$044E : 0C8000000300
    bhi.w L_0018B8                                    ; +$0454 : 620000B4
    divu.w #$0003,d0                                  ; +$0458 : 80FC0003
    move.l d0,d1                                      ; +$045C : 2200
    swap d1                                           ; +$045E : 4841
    tst.w d1                                          ; +$0460 : 4A41
    bne.w L_0018B8                                    ; +$0462 : 660000A6
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
    bne.w L_00184A                                    ; +$048E : 6600000C
    andi.l #$00008EFD,d0                              ; +$0492 : 028000008EFD
    bra.w L_001856                                    ; +$0498 : 6000000E
L_00184A:
    move.l d0,d1                                      ; +$049C : 2200
    andi.l #$00001000,d1                              ; +$049E : 028100001000
    beq.w L_0018B8                                    ; +$04A4 : 67000064
L_001856:
    move.l d0,52(a5)                                  ; +$04A8 : 2B400034
    move.l d0,d1                                      ; +$04AC : 2200
    andi.l #$00000400,d1                              ; +$04AE : 028100000400
    bne.w L_0018B8                                    ; +$04B4 : 66000054
    move.l d0,d1                                      ; +$04B8 : 2200
    andi.l #$00000800,d1                              ; +$04BA : 028100000800
    beq.w L_001898                                    ; +$04C0 : 67000028
    andi.l #$00000080,d0                              ; +$04C4 : 028000000080
    bne.w L_0018B8                                    ; +$04CA : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$04CE : 0CAD000000060040
    beq.w L_001894                                    ; +$04D6 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$04DA : 0CAD000000080040
    bne.w L_0018B8                                    ; +$04E2 : 66000026
L_001894:
    bra.w L_0018AE                                    ; +$04E6 : 60000018
L_001898:
    andi.l #$00000080,d0                              ; +$04EA : 028000000080
    beq.w L_0018AE                                    ; +$04F0 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$04F4 : 0CAD000000060040
    bne.w L_0018B8                                    ; +$04FC : 6600000C
L_0018AE:
    move.l #$00000001,d0                              ; +$0500 : 203C00000001
    bra.w L_0018BE                                    ; +$0506 : 60000008
L_0018B8:
    move.l #$00000000,d0                              ; +$050A : 203C00000000
L_0018BE:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0510 : 4CDF5FFE
    tst.l d0                                          ; +$0514 : 4A80
    rts                                               ; +$0516 : 4E75
L_0018C6:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0518 : 48E77FFA
    movea.l (a5),a2                                   ; +$051C : 2455
    move.l a2,d0                                      ; +$051E : 200A
    tst.l d0                                          ; +$0520 : 4A80
    beq.w L_0019C4                                    ; +$0522 : 670000F2
    move.l (a2),d0                                    ; +$0526 : 2012
    tst.l d0                                          ; +$0528 : 4A80
    beq.w L_0019C4                                    ; +$052A : 670000EA
    move.l d0,88(a5)                                  ; +$052E : 2B400058
    tst.l 8(a2)                                       ; +$0532 : 4AAA0008
    beq.w L_0019C4                                    ; +$0536 : 670000DE
    move.l 12(a2),d0                                  ; +$053A : 202A000C
    cmp.l 56(a5),d0                                   ; +$053E : B0AD0038
    bne.w L_0019C4                                    ; +$0542 : 660000D2
    move.l 16(a2),d0                                  ; +$0546 : 202A0010
    cmp.l 60(a5),d0                                   ; +$054A : B0AD003C
    bne.w L_0019C4                                    ; +$054E : 660000C6
    move.l 28(a2),d0                                  ; +$0552 : 202A001C
    cmp.l 64(a5),d0                                   ; +$0556 : B0AD0040
    bne.w L_0019C4                                    ; +$055A : 660000BA
    move.l 24(a2),d0                                  ; +$055E : 202A0018
    move.l 52(a5),d1                                  ; +$0562 : 222D0034
    move.l d1,d2                                      ; +$0566 : 2401
    andi.l #$FFFF0000,d2                              ; +$0568 : 0282FFFF0000
    bne.w L_001926                                    ; +$056E : 66000008
    andi.l #$00008EFD,d0                              ; +$0572 : 028000008EFD
L_001926:
    cmp.l d1,d0                                       ; +$0578 : B081
    bne.w L_0019C4                                    ; +$057A : 6600009A
    movea.l 32(a2),a3                                 ; +$057E : 266A0020
    move.l a3,d0                                      ; +$0582 : 200B
    tst.l d0                                          ; +$0584 : 4A80
    beq.w L_0019C4                                    ; +$0586 : 6700008E
    tst.l 8(a3)                                       ; +$058A : 4AAB0008
    beq.w L_001946                                    ; +$058E : 67000008
    movea.l (a3),a0                                   ; +$0592 : 2053
    bra.w L_00194A                                    ; +$0594 : 60000006
L_001946:
    movea.l 4(a3),a0                                  ; +$0598 : 206B0004
L_00194A:
    move.l a0,d0                                      ; +$059C : 2008
    tst.l d0                                          ; +$059E : 4A80
    beq.w L_0019C4                                    ; +$05A0 : 67000074
    movea.l (a0),a3                                   ; +$05A4 : 2650
    move.l a3,d0                                      ; +$05A6 : 200B
    tst.l d0                                          ; +$05A8 : 4A80
    beq.w L_0019C4                                    ; +$05AA : 6700006A
    move.l d0,80(a5)                                  ; +$05AE : 2B400050
    move.l #$00000000,d0                              ; +$05B2 : 203C00000000
    move.w (a3),d0                                    ; +$05B8 : 3013
    cmp.l 76(a5),d0                                   ; +$05BA : B0AD004C
    bcs.w L_0019C4                                    ; +$05BE : 65000056
    move.l d0,84(a5)                                  ; +$05C2 : 2B400054
    move.l #$00000000,d0                              ; +$05C6 : 203C00000000
    move.w 2(a3),d0                                   ; +$05CC : 302B0002
    cmp.l 60(a5),d0                                   ; +$05D0 : B0AD003C
    bcs.w L_0019C4                                    ; +$05D4 : 65000040
    move.l #$00000000,d0                              ; +$05D8 : 203C00000000
    move.b 5(a3),d0                                   ; +$05DE : 102B0005
    cmp.l 64(a5),d0                                   ; +$05E2 : B0AD0040
    bne.w L_0019C4                                    ; +$05E6 : 6600002E
    move.l a3,d0                                      ; +$05EA : 200B
    addq.l #8,d0                                      ; +$05EC : 5080
    movea.l d0,a0                                     ; +$05EE : 2040
    move.l 64(a5),d1                                  ; +$05F0 : 222D0040
L_0019A2:
    move.l (a0)+,d0                                   ; +$05F4 : 2018
    tst.l d0                                          ; +$05F6 : 4A80
    beq.w L_0019C4                                    ; +$05F8 : 6700001C
    cmpi.l #$FFFFFFFF,d0                              ; +$05FC : 0C80FFFFFFFF
    beq.w L_0019C4                                    ; +$0602 : 67000012
    subq.l #1,d1                                      ; +$0606 : 5381
    bne.w L_0019A2                                    ; +$0608 : 6600FFEA
    move.l #$00000001,d0                              ; +$060C : 203C00000001
    bra.w L_0019CA                                    ; +$0612 : 60000008
L_0019C4:
    move.l #$00000000,d0                              ; +$0616 : 203C00000000
L_0019CA:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$061C : 4CDF5FFE
    tst.l d0                                          ; +$0620 : 4A80
    rts                                               ; +$0622 : 4E75
L_0019D2:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0624 : 48E77FFA
    movea.l 44(a5),a0                                 ; +$0628 : 206D002C
    move.l a0,d0                                      ; +$062C : 2008
    add.l 48(a5),d0                                   ; +$062E : D0AD0030
    movea.l d0,a2                                     ; +$0632 : 2440
    move.l #$00000000,d4                              ; +$0634 : 283C00000000
    move.l #$00000000,d3                              ; +$063A : 263C00000000
L_0019EE:
    move.l #$00000000,d5                              ; +$0640 : 2A3C00000000
    movea.l 80(a5),a3                                 ; +$0646 : 266D0050
    move.l a3,d0                                      ; +$064A : 200B
    addq.l #8,d0                                      ; +$064C : 5080
    movea.l d0,a4                                     ; +$064E : 2840
L_0019FE:
    move.l 76(a5),d6                                  ; +$0650 : 2C2D004C
    movea.l #$00000000,a6                             ; +$0654 : 2C7C00000000
    cmp.l 64(a5),d5                                   ; +$065A : BAAD0040
    bcc.w L_001A1E                                    ; +$065E : 64000010
    tst.l 100(a5)                                     ; +$0662 : 4AAD0064
    beq.w L_001A1E                                    ; +$0666 : 67000008
    move.l (a4)+,d0                                   ; +$066A : 201C
    add.l d3,d0                                       ; +$066C : D083
    movea.l d0,a6                                     ; +$066E : 2C40
L_001A1E:
    tst.l 72(a5)                                      ; +$0670 : 4AAD0048
    beq.w L_001A4C                                    ; +$0674 : 67000028
    move.l a0,d0                                      ; +$0678 : 2008
    cmp.l a2,d0                                       ; +$067A : B08A
    bcc.w L_001AF6                                    ; +$067C : 640000CA
    move.l #$00000000,d1                              ; +$0680 : 223C00000000
    move.b (a0)+,d1                                   ; +$0686 : 1218
    cmpi.l #$00000080,d1                              ; +$0688 : 0C8100000080
    beq.w L_001A1E                                    ; +$068E : 6700FFE0
    bhi.w L_001A78                                    ; +$0692 : 62000036
    addq.l #1,d1                                      ; +$0696 : 5281
    move.l d1,d2                                      ; +$0698 : 2401
    bra.w L_001A50                                    ; +$069A : 60000006
L_001A4C:
    move.l d6,d1                                      ; +$069E : 2206
    move.l d1,d2                                      ; +$06A0 : 2401
L_001A50:
    cmp.l d6,d1                                       ; +$06A2 : B286
    bhi.w L_001AF6                                    ; +$06A4 : 620000A2
    move.l a2,d0                                      ; +$06A8 : 200A
    sub.l a0,d0                                       ; +$06AA : 9088
    cmp.l d1,d0                                       ; +$06AC : B081
    bcs.w L_001AF6                                    ; +$06AE : 65000098
    sub.l d1,d6                                       ; +$06B2 : 9C81
L_001A62:
    move.b (a0)+,d0                                   ; +$06B4 : 1018
    move.l a6,d7                                      ; +$06B6 : 2E0E
    tst.l d7                                          ; +$06B8 : 4A87
    beq.w L_001A6E                                    ; +$06BA : 67000004
    move.b d0,(a6)+                                   ; +$06BE : 1CC0
L_001A6E:
    subq.l #1,d2                                      ; +$06C0 : 5382
    bne.w L_001A62                                    ; +$06C2 : 6600FFF0
    bra.w L_001AA2                                    ; +$06C6 : 6000002C
L_001A78:
    move.l #$00000101,d2                              ; +$06CA : 243C00000101
    sub.l d1,d2                                       ; +$06D0 : 9481
    cmp.l d6,d2                                       ; +$06D2 : B486
    bhi.w L_001AF6                                    ; +$06D4 : 62000072
    sub.l d2,d6                                       ; +$06D8 : 9C82
    move.l a0,d0                                      ; +$06DA : 2008
    cmp.l a2,d0                                       ; +$06DC : B08A
    bcc.w L_001AF6                                    ; +$06DE : 64000068
    move.b (a0)+,d0                                   ; +$06E2 : 1018
L_001A92:
    move.l a6,d7                                      ; +$06E4 : 2E0E
    tst.l d7                                          ; +$06E6 : 4A87
    beq.w L_001A9C                                    ; +$06E8 : 67000004
    move.b d0,(a6)+                                   ; +$06EC : 1CC0
L_001A9C:
    subq.l #1,d2                                      ; +$06EE : 5382
    bne.w L_001A92                                    ; +$06F0 : 6600FFF2
L_001AA2:
    tst.l d6                                          ; +$06F4 : 4A86
    bne.w L_001A1E                                    ; +$06F6 : 6600FF78
    addq.l #1,d5                                      ; +$06FA : 5285
    move.l 64(a5),d0                                  ; +$06FC : 202D0040
    cmpi.l #$00000001,68(a5)                          ; +$0700 : 0CAD000000010044
    bne.w L_001ABC                                    ; +$0708 : 66000004
    addq.l #1,d0                                      ; +$070C : 5280
L_001ABC:
    cmp.l d0,d5                                       ; +$070E : BA80
    bcs.w L_0019FE                                    ; +$0710 : 6500FF3E
    add.l 84(a5),d3                                   ; +$0714 : D6AD0054
    addq.l #1,d4                                      ; +$0718 : 5284
    cmp.l 60(a5),d4                                   ; +$071A : B8AD003C
    bcs.w L_0019EE                                    ; +$071E : 6500FF20
L_001AD0:
    move.l a0,d0                                      ; +$0722 : 2008
    cmp.l a2,d0                                       ; +$0724 : B08A
    beq.w L_001AEC                                    ; +$0726 : 67000016
    tst.l 72(a5)                                      ; +$072A : 4AAD0048
    beq.w L_001AF6                                    ; +$072E : 67000018
    cmpi.b #$80,(a0)+                                 ; +$0732 : 0C180080
    bne.w L_001AF6                                    ; +$0736 : 66000010
    bra.w L_001AD0                                    ; +$073A : 6000FFE6
L_001AEC:
    move.l #$00000001,d0                              ; +$073E : 203C00000001
    bra.w L_001AFC                                    ; +$0744 : 60000008
L_001AF6:
    move.l #$00000000,d0                              ; +$0748 : 203C00000000
L_001AFC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$074E : 4CDF5FFE
    tst.l d0                                          ; +$0752 : 4A80
    rts                                               ; +$0754 : 4E75
L_001B04:
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
    beq.w L_001B72                                    ; +$0778 : 6700004A
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
L_001B46:
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
    bne.w L_001B46                                    ; +$07B0 : 6600FFE6
    move.l #$00000000,(a1)                            ; +$07B4 : 22BC00000000
    move.l #$00000001,d0                              ; +$07BA : 203C00000001
    bra.w L_001B78                                    ; +$07C0 : 60000008
L_001B72:
    move.l #$00000000,d0                              ; +$07C4 : 203C00000000
L_001B78:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$07CA : 4CDF5FFE
    tst.l d0                                          ; +$07CE : 4A80
    rts                                               ; +$07D0 : 4E75
L_001B80:
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
    bra.w L_001BB2                                    ; +$07FA : 60000008
    move.l #$00000000,d0                              ; +$07FE : 203C00000000
L_001BB2:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0804 : 4CDF5FFE
    tst.l d0                                          ; +$0808 : 4A80
    rts                                               ; +$080A : 4E75
L_001BBA:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$080C : 48E77FFA
    tst.l 20(a5)                                      ; +$0810 : 4AAD0014
    beq.w L_001BD2                                    ; +$0814 : 6700000E
    movea.l 16(a5),a6                                 ; +$0818 : 2C6D0010
    move.l 20(a5),d1                                  ; +$081C : 222D0014
    jsr -36(a6)                                       ; +$0820 : 4EAEFFDC
L_001BD2:
    tst.l 96(a5)                                      ; +$0824 : 4AAD0060
    beq.w L_001BE6                                    ; +$0828 : 6700000E
    movea.l 96(a5),a1                                 ; +$082C : 226D0060
    movea.l $0004.w,a6                                ; +$0830 : 2C780004
    jsr -690(a6)                                      ; +$0834 : 4EAEFD4E
L_001BE6:
    tst.l 24(a5)                                      ; +$0838 : 4AAD0018
    beq.w L_001BFA                                    ; +$083C : 6700000E
    movea.l 24(a5),a1                                 ; +$0840 : 226D0018
    movea.l $0004.w,a6                                ; +$0844 : 2C780004
    jsr -690(a6)                                      ; +$0848 : 4EAEFD4E
L_001BFA:
    tst.l 12(a5)                                      ; +$084C : 4AAD000C
    beq.w L_001C0E                                    ; +$0850 : 6700000E
    movea.l 12(a5),a1                                 ; +$0854 : 226D000C
    movea.l $0004.w,a6                                ; +$0858 : 2C780004
    jsr -690(a6)                                      ; +$085C : 4EAEFD4E
L_001C0E:
    tst.l 16(a5)                                      ; +$0860 : 4AAD0010
    beq.w L_001C22                                    ; +$0864 : 6700000E
    movea.l 16(a5),a1                                 ; +$0868 : 226D0010
    movea.l $0004.w,a6                                ; +$086C : 2C780004
    jsr -414(a6)                                      ; +$0870 : 4EAEFE62
L_001C22:
    move.l #$00000001,d0                              ; +$0874 : 203C00000001
    bra.w L_001C32                                    ; +$087A : 60000008
    move.l #$00000000,d0                              ; +$087E : 203C00000000
L_001C32:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0884 : 4CDF5FFE
    tst.l d0                                          ; +$0888 : 4A80
    rts                                               ; +$088A : 4E75
L_001C3A:
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
    bhi.w L_001E28                                    ; +$0124 : 620000B8
    bsr.w L_001E3E                                    ; +$0128 : 610000CA
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_001E28                                    ; +$012E : 670000AE
    bsr.w L_001F6C                                    ; +$0132 : 610001EE
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_001E28                                    ; +$0138 : 670000A4
    cmpi.l #$00000000,8(a5)                           ; +$013C : 0CAD000000000008
    beq.w L_001DF0                                    ; +$0144 : 67000060
    cmpi.l #$00000001,8(a5)                           ; +$0148 : 0CAD000000010008
    beq.w L_001DF8                                    ; +$0150 : 6700005C
    cmpi.l #$00000002,8(a5)                           ; +$0154 : 0CAD000000020008
    beq.w L_001E00                                    ; +$015C : 67000058
    cmpi.l #$00000003,8(a5)                           ; +$0160 : 0CAD000000030008
    beq.w L_001E08                                    ; +$0168 : 67000054
    cmpi.l #$00000004,8(a5)                           ; +$016C : 0CAD000000040008
    beq.w L_001E10                                    ; +$0174 : 67000050
    cmpi.l #$00000005,8(a5)                           ; +$0178 : 0CAD000000050008
    beq.w L_001E18                                    ; +$0180 : 6700004C
    cmpi.l #$00000006,8(a5)                           ; +$0184 : 0CAD000000060008
    beq.w L_001E20                                    ; +$018C : 67000048
    move.l #$00000001,d3                              ; +$0190 : 263C00000001
    move.l 64(a5),d0                                  ; +$0196 : 202D0040
L_001DE4:
    lsl.l #1,d3                                       ; +$019A : E38B
    subq.l #1,d0                                      ; +$019C : 5380
    bne.w L_001DE4                                    ; +$019E : 6600FFFA
    bra.w L_001E2E                                    ; +$01A2 : 60000040
L_001DF0:
    move.l 56(a5),d3                                  ; +$01A6 : 262D0038
    bra.w L_001E2E                                    ; +$01AA : 60000038
L_001DF8:
    move.l 60(a5),d3                                  ; +$01AE : 262D003C
    bra.w L_001E2E                                    ; +$01B2 : 60000030
L_001E00:
    move.l 64(a5),d3                                  ; +$01B6 : 262D0040
    bra.w L_001E2E                                    ; +$01BA : 60000028
L_001E08:
    move.l 40(a5),d3                                  ; +$01BE : 262D0028
    bra.w L_001E2E                                    ; +$01C2 : 60000020
L_001E10:
    move.l 72(a5),d3                                  ; +$01C6 : 262D0048
    bra.w L_001E2E                                    ; +$01CA : 60000018
L_001E18:
    move.l 92(a5),d3                                  ; +$01CE : 262D005C
    bra.w L_001E2E                                    ; +$01D2 : 60000010
L_001E20:
    move.l 52(a5),d3                                  ; +$01D6 : 262D0034
    bra.w L_001E2E                                    ; +$01DA : 60000008
L_001E28:
    move.l #$FFFFFFFF,d3                              ; +$01DE : 263CFFFFFFFF
L_001E2E:
    bsr.w L_0021C4                                    ; +$01E4 : 61000394
    lea 128(a7),a7                                    ; +$01E8 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01EC : 4CDF77F7
    moveq #0,d2                                       ; +$01F0 : 7400
    rts                                               ; +$01F2 : 4E75
L_001E3E:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$01F4 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$01F8 : 246D0004
    move.l #$00000000,d4                              ; +$01FC : 283C00000000
    move.w (a2)+,d4                                   ; +$0202 : 381A
    tst.l d4                                          ; +$0204 : 4A84
    beq.w L_001F5E                                    ; +$0206 : 6700010C
    move.l d4,d0                                      ; +$020A : 2004
    addq.l #1,d0                                      ; +$020C : 5280
    move.l #$00010001,d1                              ; +$020E : 223C00010001
    movea.l $0004.w,a6                                ; +$0214 : 2C780004
    jsr -684(a6)                                      ; +$0218 : 4EAEFD54
    tst.l d0                                          ; +$021C : 4A80
    beq.w L_001F5E                                    ; +$021E : 670000F4
    move.l d0,12(a5)                                  ; +$0222 : 2B40000C
    movea.l d0,a1                                     ; +$0226 : 2240
L_001E72:
    move.b (a2)+,(a1)+                                ; +$0228 : 12DA
    subq.l #1,d4                                      ; +$022A : 5384
    bne.w L_001E72                                    ; +$022C : 6600FFFA
    lea L_002244(pc),a1                               ; +$0230 : 43FA03C8
    move.l #$00000000,d0                              ; +$0234 : 203C00000000
    movea.l $0004.w,a6                                ; +$023A : 2C780004
    jsr -552(a6)                                      ; +$023E : 4EAEFDD8
    tst.l d0                                          ; +$0242 : 4A80
    beq.w L_001F5E                                    ; +$0244 : 670000CE
    move.l d0,16(a5)                                  ; +$0248 : 2B400010
    movea.l d0,a6                                     ; +$024C : 2C40
    move.l 12(a5),d1                                  ; +$024E : 222D000C
    move.l #$000003ED,d2                              ; +$0252 : 243C000003ED
    jsr -30(a6)                                       ; +$0258 : 4EAEFFE2
    tst.l d0                                          ; +$025C : 4A80
    beq.w L_001F5E                                    ; +$025E : 670000B4
    move.l d0,20(a5)                                  ; +$0262 : 2B400014
    move.l d0,d1                                      ; +$0266 : 2200
    move.l a5,d2                                      ; +$0268 : 240D
    addi.l #$00000068,d2                              ; +$026A : 068200000068
    move.l #$0000000C,d3                              ; +$0270 : 263C0000000C
    jsr -42(a6)                                       ; +$0276 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$027A : 0C800000000C
    bne.w L_001F5E                                    ; +$0280 : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$0284 : 0CAD464F524D0068
    bne.w L_001F5E                                    ; +$028C : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$0290 : 0CAD494C424D0070
    bne.w L_001F5E                                    ; +$0298 : 6600007A
    move.l 108(a5),d4                                 ; +$029C : 282D006C
    cmpi.l #$00000004,d4                              ; +$02A0 : 0C8400000004
    bcs.w L_001F5E                                    ; +$02A6 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$02AA : 0C847FFFFFF7
    bhi.w L_001F5E                                    ; +$02B0 : 62000062
    addq.l #8,d4                                      ; +$02B4 : 5084
    move.l d4,28(a5)                                  ; +$02B6 : 2B44001C
    move.l d4,d0                                      ; +$02BA : 2004
    move.l #$00010001,d1                              ; +$02BC : 223C00010001
    movea.l $0004.w,a6                                ; +$02C2 : 2C780004
    jsr -684(a6)                                      ; +$02C6 : 4EAEFD54
    tst.l d0                                          ; +$02CA : 4A80
    beq.w L_001F5E                                    ; +$02CC : 67000046
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
    bne.w L_001F5E                                    ; +$0306 : 6600000C
    move.l #$00000001,d0                              ; +$030A : 203C00000001
    bra.w L_001F64                                    ; +$0310 : 60000008
L_001F5E:
    move.l #$00000000,d0                              ; +$0314 : 203C00000000
L_001F64:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$031A : 4CDF5FFE
    tst.l d0                                          ; +$031E : 4A80
    rts                                               ; +$0320 : 4E75
L_001F6C:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0322 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$0326 : 206D0018
    move.l 28(a5),d7                                  ; +$032A : 2E2D001C
    subi.l #$0000000C,d7                              ; +$032E : 04870000000C
    move.l a0,d0                                      ; +$0334 : 2008
    addi.l #$0000000C,d0                              ; +$0336 : 06800000000C
    movea.l d0,a0                                     ; +$033C : 2040
L_001F88:
    tst.l d7                                          ; +$033E : 4A87
    beq.w L_00204C                                    ; +$0340 : 670000C0
    cmpi.l #$00000008,d7                              ; +$0344 : 0C8700000008
    bcs.w L_0021B6                                    ; +$034A : 65000220
    move.l (a0)+,d3                                   ; +$034E : 2618
    move.l (a0)+,d2                                   ; +$0350 : 2418
    subq.l #8,d7                                      ; +$0352 : 5187
    cmp.l d7,d2                                       ; +$0354 : B487
    bhi.w L_0021B6                                    ; +$0356 : 62000214
    move.l d2,d1                                      ; +$035A : 2202
    andi.l #$00000001,d1                              ; +$035C : 028100000001
    add.l d2,d1                                       ; +$0362 : D282
    cmp.l d7,d1                                       ; +$0364 : B287
    bhi.w L_0021B6                                    ; +$0366 : 62000204
    sub.l d1,d7                                       ; +$036A : 9E81
    cmpi.l #$424D4844,d3                              ; +$036C : 0C83424D4844
    beq.w L_001FE2                                    ; +$0372 : 67000024
    cmpi.l #$434D4150,d3                              ; +$0376 : 0C83434D4150
    beq.w L_001FFC                                    ; +$037C : 67000034
    cmpi.l #$43414D47,d3                              ; +$0380 : 0C8343414D47
    beq.w L_002024                                    ; +$0386 : 67000052
    cmpi.l #$424F4459,d3                              ; +$038A : 0C83424F4459
    beq.w L_002010                                    ; +$0390 : 67000034
    bra.w L_002042                                    ; +$0394 : 60000062
L_001FE2:
    tst.l 32(a5)                                      ; +$0398 : 4AAD0020
    bne.w L_0021B6                                    ; +$039C : 660001CE
    cmpi.l #$00000014,d2                              ; +$03A0 : 0C8200000014
    bne.w L_0021B6                                    ; +$03A6 : 660001C4
    move.l a0,32(a5)                                  ; +$03AA : 2B480020
    bra.w L_002042                                    ; +$03AE : 60000048
L_001FFC:
    tst.l 36(a5)                                      ; +$03B2 : 4AAD0024
    bne.w L_0021B6                                    ; +$03B6 : 660001B4
    move.l a0,36(a5)                                  ; +$03BA : 2B480024
    move.l d2,40(a5)                                  ; +$03BE : 2B420028
    bra.w L_002042                                    ; +$03C2 : 60000034
L_002010:
    tst.l 44(a5)                                      ; +$03C6 : 4AAD002C
    bne.w L_0021B6                                    ; +$03CA : 660001A0
    move.l a0,44(a5)                                  ; +$03CE : 2B48002C
    move.l d2,48(a5)                                  ; +$03D2 : 2B420030
    bra.w L_002042                                    ; +$03D6 : 60000020
L_002024:
    tst.l 52(a5)                                      ; +$03DA : 4AAD0034
    bne.w L_0021B6                                    ; +$03DE : 6600018C
    cmpi.l #$00000004,d2                              ; +$03E2 : 0C8200000004
    bne.w L_0021B6                                    ; +$03E8 : 66000182
    move.l #$00000001,52(a5)                          ; +$03EC : 2B7C000000010034
    move.l (a0),92(a5)                                ; +$03F4 : 2B50005C
L_002042:
    move.l a0,d0                                      ; +$03F8 : 2008
    add.l d1,d0                                       ; +$03FA : D081
    movea.l d0,a0                                     ; +$03FC : 2040
    bra.w L_001F88                                    ; +$03FE : 6000FF3E
L_00204C:
    tst.l 32(a5)                                      ; +$0402 : 4AAD0020
    beq.w L_0021B6                                    ; +$0406 : 67000164
    tst.l 36(a5)                                      ; +$040A : 4AAD0024
    beq.w L_0021B6                                    ; +$040E : 6700015C
    tst.l 44(a5)                                      ; +$0412 : 4AAD002C
    beq.w L_0021B6                                    ; +$0416 : 67000154
    tst.l 48(a5)                                      ; +$041A : 4AAD0030
    beq.w L_0021B6                                    ; +$041E : 6700014C
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
    beq.w L_0021B6                                    ; +$046E : 670000FC
    tst.l 60(a5)                                      ; +$0472 : 4AAD003C
    beq.w L_0021B6                                    ; +$0476 : 670000F4
    tst.l 64(a5)                                      ; +$047A : 4AAD0040
    beq.w L_0021B6                                    ; +$047E : 670000EC
    cmpi.l #$00000008,64(a5)                          ; +$0482 : 0CAD000000080040
    bhi.w L_0021B6                                    ; +$048A : 620000E0
    cmpi.l #$00000002,68(a5)                          ; +$048E : 0CAD000000020044
    bhi.w L_0021B6                                    ; +$0496 : 620000D4
    cmpi.l #$00000001,72(a5)                          ; +$049A : 0CAD000000010048
    bhi.w L_0021B6                                    ; +$04A2 : 620000C8
    move.l 40(a5),d0                                  ; +$04A6 : 202D0028
    tst.l d0                                          ; +$04AA : 4A80
    beq.w L_0021B6                                    ; +$04AC : 670000BE
    cmpi.l #$00000300,d0                              ; +$04B0 : 0C8000000300
    bhi.w L_0021B6                                    ; +$04B6 : 620000B4
    divu.w #$0003,d0                                  ; +$04BA : 80FC0003
    move.l d0,d1                                      ; +$04BE : 2200
    swap d1                                           ; +$04C0 : 4841
    tst.w d1                                          ; +$04C2 : 4A41
    bne.w L_0021B6                                    ; +$04C4 : 660000A6
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
    bne.w L_002148                                    ; +$04F0 : 6600000C
    andi.l #$00008EFD,d0                              ; +$04F4 : 028000008EFD
    bra.w L_002154                                    ; +$04FA : 6000000E
L_002148:
    move.l d0,d1                                      ; +$04FE : 2200
    andi.l #$00001000,d1                              ; +$0500 : 028100001000
    beq.w L_0021B6                                    ; +$0506 : 67000064
L_002154:
    move.l d0,52(a5)                                  ; +$050A : 2B400034
    move.l d0,d1                                      ; +$050E : 2200
    andi.l #$00000400,d1                              ; +$0510 : 028100000400
    bne.w L_0021B6                                    ; +$0516 : 66000054
    move.l d0,d1                                      ; +$051A : 2200
    andi.l #$00000800,d1                              ; +$051C : 028100000800
    beq.w L_002196                                    ; +$0522 : 67000028
    andi.l #$00000080,d0                              ; +$0526 : 028000000080
    bne.w L_0021B6                                    ; +$052C : 6600003E
    cmpi.l #$00000006,64(a5)                          ; +$0530 : 0CAD000000060040
    beq.w L_002192                                    ; +$0538 : 6700000E
    cmpi.l #$00000008,64(a5)                          ; +$053C : 0CAD000000080040
    bne.w L_0021B6                                    ; +$0544 : 66000026
L_002192:
    bra.w L_0021AC                                    ; +$0548 : 60000018
L_002196:
    andi.l #$00000080,d0                              ; +$054C : 028000000080
    beq.w L_0021AC                                    ; +$0552 : 6700000E
    cmpi.l #$00000006,64(a5)                          ; +$0556 : 0CAD000000060040
    bne.w L_0021B6                                    ; +$055E : 6600000C
L_0021AC:
    move.l #$00000001,d0                              ; +$0562 : 203C00000001
    bra.w L_0021BC                                    ; +$0568 : 60000008
L_0021B6:
    move.l #$00000000,d0                              ; +$056C : 203C00000000
L_0021BC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0572 : 4CDF5FFE
    tst.l d0                                          ; +$0576 : 4A80
    rts                                               ; +$0578 : 4E75
L_0021C4:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$057A : 48E77FFA
    tst.l 20(a5)                                      ; +$057E : 4AAD0014
    beq.w L_0021DC                                    ; +$0582 : 6700000E
    movea.l 16(a5),a6                                 ; +$0586 : 2C6D0010
    move.l 20(a5),d1                                  ; +$058A : 222D0014
    jsr -36(a6)                                       ; +$058E : 4EAEFFDC
L_0021DC:
    tst.l 96(a5)                                      ; +$0592 : 4AAD0060
    beq.w L_0021F0                                    ; +$0596 : 6700000E
    movea.l 96(a5),a1                                 ; +$059A : 226D0060
    movea.l $0004.w,a6                                ; +$059E : 2C780004
    jsr -690(a6)                                      ; +$05A2 : 4EAEFD4E
L_0021F0:
    tst.l 24(a5)                                      ; +$05A6 : 4AAD0018
    beq.w L_002204                                    ; +$05AA : 6700000E
    movea.l 24(a5),a1                                 ; +$05AE : 226D0018
    movea.l $0004.w,a6                                ; +$05B2 : 2C780004
    jsr -690(a6)                                      ; +$05B6 : 4EAEFD4E
L_002204:
    tst.l 12(a5)                                      ; +$05BA : 4AAD000C
    beq.w L_002218                                    ; +$05BE : 6700000E
    movea.l 12(a5),a1                                 ; +$05C2 : 226D000C
    movea.l $0004.w,a6                                ; +$05C6 : 2C780004
    jsr -690(a6)                                      ; +$05CA : 4EAEFD4E
L_002218:
    tst.l 16(a5)                                      ; +$05CE : 4AAD0010
    beq.w L_00222C                                    ; +$05D2 : 6700000E
    movea.l 16(a5),a1                                 ; +$05D6 : 226D0010
    movea.l $0004.w,a6                                ; +$05DA : 2C780004
    jsr -414(a6)                                      ; +$05DE : 4EAEFE62
L_00222C:
    move.l #$00000001,d0                              ; +$05E2 : 203C00000001
    bra.w L_00223C                                    ; +$05E8 : 60000008
    move.l #$00000000,d0                              ; +$05EC : 203C00000000
L_00223C:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$05F2 : 4CDF5FFE
    tst.l d0                                          ; +$05F6 : 4A80
    rts                                               ; +$05F8 : 4E75
L_002244:
    dc.b "dos.library"
    dc.b $00

; -------- AP20 entry 15 : private/reserved --------
Entry_15:
Internal_15:
    cmpi.l #$00000100,d7                              ; +$0000 : 0C8700000100
    beq.w L_002284                                    ; +$0006 : 6700002C
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
L_002284:
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
    beq.w L_002464                                    ; +$000E : 670001CA
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002464                                    ; +$001A : 670001BE
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_002464                                    ; +$0026 : 670001B2
L_0022B4:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_0036F0                                    ; +$0030 : 61001434
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_002464                                    ; +$0036 : 670001A2
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
    bne.w L_0022B4                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_0022B4                                    ; +$0064 : 6600FFC4
    cmpi.l #$00000033,d5                              ; +$0068 : 0C8500000033
    bne.w L_00245E                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_00245E                                    ; +$007A : 67000158
    bra.w L_002486                                    ; +$007E : 6000017C
L_00230C:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_00246C                                    ; +$0088 : 60000158
L_002316:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_002362                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_002348                                    ; +$00A0 : 6700001C
L_00232E:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_002348                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_00232E                                    ; +$00BA : 6000FFE8
L_002348:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_00235A                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    bsr.w L_006C7C                                    ; +$00CC : 61004924
L_00235A:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_002362:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_0023E2                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_00237E                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_00237E:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_0023AC                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_00239C                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_00239C:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_0023AC                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_0023AC:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_0023C0                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_0023C0:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_0023D0                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_0023D0:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_0023E2:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_0023FA                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_0023FA:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_002416                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_002416:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_002432                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_002432:
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
    bra.w L_00230C                                    ; +$01D0 : 6000FEB0
L_00245E:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_002464                                    ; +$01D6 : 60000002
L_002464:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01DA : 4CDF5FF3
    moveq #0,d2                                       ; +$01DE : 7400
    rts                                               ; +$01E0 : 4E75
L_00246C:
    moveq #1,d1                                       ; +$01E2 : 7201
    movea.l -8(a5),a0                                 ; +$01E4 : 206DFFF8
    jsr 288(a0)                                       ; +$01E8 : 4EA80120
    move.l d5,d3                                      ; +$01EC : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$01FA : 4E75
L_002486:
    bsr.w L_002498                                    ; +$01FC : 61000010
    tst.l d0                                          ; +$0200 : 4A80
    beq.w L_002494                                    ; +$0202 : 67000006
    bra.w L_002316                                    ; +$0206 : 6000FE84
L_002494:
    bra.w L_002464                                    ; +$020A : 6000FFCE
L_002498:
    movea.l 32(a2),a4                                 ; +$020E : 286A0020
    move.l a4,d0                                      ; +$0212 : 200C
    tst.l d0                                          ; +$0214 : 4A80
    beq.w L_0024D0                                    ; +$0216 : 6700002E
    moveq #0,d4                                       ; +$021A : 7800
L_0024A6:
    bsr.w L_0024D8                                    ; +$021C : 61000030
    tst.l d0                                          ; +$0220 : 4A80
    beq.w L_0024D0                                    ; +$0222 : 67000022
    addq.l #1,d4                                      ; +$0226 : 5284
    cmpi.l #$0000012D,d4                              ; +$0228 : 0C840000012D
    bge.w L_0024D4                                    ; +$022E : 6C00001A
    movea.l 8(a2),a6                                  ; +$0232 : 2C6A0008
    move.l a6,d0                                      ; +$0236 : 200E
    tst.l d0                                          ; +$0238 : 4A80
    beq.w L_0024D4                                    ; +$023A : 6700000E
    jsr -270(a6)                                      ; +$023E : 4EAEFEF2
    bra.w L_0024A6                                    ; +$0242 : 6000FFD8
L_0024D0:
    moveq #1,d0                                       ; +$0246 : 7001
    rts                                               ; +$0248 : 4E75
L_0024D4:
    moveq #0,d0                                       ; +$024A : 7000
    rts                                               ; +$024C : 4E75
L_0024D8:
    move.l 20(a4),d6                                  ; +$024E : 2C2C0014
    andi.l #$00000003,d6                              ; +$0252 : 028600000003
    btst #0,d6                                        ; +$0258 : 08060000
    beq.w L_002508                                    ; +$025C : 67000020
    movea.l 12(a4),a0                                 ; +$0260 : 206C000C
    move.l a0,d0                                      ; +$0264 : 2008
    tst.l d0                                          ; +$0266 : 4A80
    beq.w L_002508                                    ; +$0268 : 67000014
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -372(a6)                                      ; +$0270 : 4EAEFE8C
    tst.l d0                                          ; +$0274 : 4A80
    beq.w L_002508                                    ; +$0276 : 67000006
    bclr #0,d6                                        ; +$027A : 08860000
L_002508:
    btst #1,d6                                        ; +$027E : 08060001
    beq.w L_00252E                                    ; +$0282 : 67000020
    movea.l 16(a4),a0                                 ; +$0286 : 206C0010
    move.l a0,d0                                      ; +$028A : 2008
    tst.l d0                                          ; +$028C : 4A80
    beq.w L_00252E                                    ; +$028E : 67000014
    movea.l $0004.w,a6                                ; +$0292 : 2C780004
    jsr -372(a6)                                      ; +$0296 : 4EAEFE8C
    tst.l d0                                          ; +$029A : 4A80
    beq.w L_00252E                                    ; +$029C : 67000006
    bclr #1,d6                                        ; +$02A0 : 08860001
L_00252E:
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
    beq.w L_002724                                    ; +$000E : 670001DE
    movea.l 36(a2),a3                                 ; +$0012 : 266A0024
    move.l a3,d0                                      ; +$0016 : 200B
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002724                                    ; +$001A : 670001D2
    movea.l 86(a3),a4                                 ; +$001E : 286B0056
    move.l a4,d0                                      ; +$0022 : 200C
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_002724                                    ; +$0026 : 670001C6
L_002560:
    movea.l a4,a0                                     ; +$002A : 204C
    movea.l $0004.w,a6                                ; +$002C : 2C780004
    bsr.w L_0036F0                                    ; +$0030 : 61001188
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_002710                                    ; +$0036 : 670001A2
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
    bne.w L_002560                                    ; +$0058 : 6600FFD0
    move.l d5,d0                                      ; +$005C : 2005
    andi.l #$00000080,d0                              ; +$005E : 028000000080
    bne.w L_002560                                    ; +$0064 : 6600FFC4
    bra.w L_00272C                                    ; +$0068 : 6000018C
    nop                                               ; +$006C : 4E71
L_0025A4:
    bne.w L_00270A                                    ; +$006E : 66000164
    move.l d6,d0                                      ; +$0072 : 2006
    andi.l #$00000008,d0                              ; +$0074 : 028000000008
    beq.w L_00270A                                    ; +$007A : 67000158
    bra.w L_00275A                                    ; +$007E : 600001A4
L_0025B8:
    ori.w #$8100,-168(a5)                             ; +$0082 : 006D8100FF58
    bra.w L_002740                                    ; +$0088 : 60000180
L_0025C2:
    movea.l 36(a2),a3                                 ; +$008C : 266A0024
    move.l a3,d0                                      ; +$0090 : 200B
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_00260E                                    ; +$0094 : 67000042
    movea.l 86(a3),a4                                 ; +$0098 : 286B0056
    move.l a4,d0                                      ; +$009C : 200C
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_0025F4                                    ; +$00A0 : 6700001C
L_0025DA:
    movea.l a4,a0                                     ; +$00A4 : 204C
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -372(a6)                                      ; +$00AA : 4EAEFE8C
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_0025F4                                    ; +$00B0 : 6700000C
    movea.l d0,a1                                     ; +$00B4 : 2240
    jsr -378(a6)                                      ; +$00B6 : 4EAEFE86
    bra.w L_0025DA                                    ; +$00BA : 6000FFE8
L_0025F4:
    movea.l 4(a2),a6                                  ; +$00BE : 2C6A0004
    move.l a6,d0                                      ; +$00C2 : 200E
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_002606                                    ; +$00C6 : 67000008
    movea.l a3,a0                                     ; +$00CA : 204B
    bsr.w L_006C7C                                    ; +$00CC : 61004678
L_002606:
    move.l #$00000000,36(a2)                          ; +$00D0 : 257C000000000024
L_00260E:
    movea.l 32(a2),a4                                 ; +$00D8 : 286A0020
    move.l a4,d0                                      ; +$00DC : 200C
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_00268E                                    ; +$00E0 : 67000076
    movea.l 8(a2),a6                                  ; +$00E4 : 2C6A0008
    move.l a6,d0                                      ; +$00E8 : 200E
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_00262A                                    ; +$00EC : 67000006
    jsr -228(a6)                                      ; +$00F0 : 4EAEFF1C
L_00262A:
    movea.l (a2),a0                                   ; +$00F4 : 2052
    move.l a0,d0                                      ; +$00F6 : 2008
    tst.l d0                                          ; +$00F8 : 4A80
    beq.w L_002658                                    ; +$00FA : 67000026
    movea.l 4(a2),a6                                  ; +$00FE : 2C6A0004
    movea.l 4(a4),a1                                  ; +$0102 : 226C0004
    move.l a1,d0                                      ; +$0106 : 2009
    tst.l d0                                          ; +$0108 : 4A80
    beq.w L_002648                                    ; +$010A : 67000006
    jsr -774(a6)                                      ; +$010E : 4EAEFCFA
L_002648:
    movea.l (a4),a1                                   ; +$0112 : 2254
    move.l a1,d0                                      ; +$0114 : 2009
    tst.l d0                                          ; +$0116 : 4A80
    beq.w L_002658                                    ; +$0118 : 67000008
    movea.l (a2),a0                                   ; +$011C : 2052
    jsr -774(a6)                                      ; +$011E : 4EAEFCFA
L_002658:
    movea.l $0004.w,a6                                ; +$0122 : 2C780004
    movea.l 16(a4),a0                                 ; +$0126 : 206C0010
    move.l a0,d0                                      ; +$012A : 2008
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_00266C                                    ; +$012E : 67000006
    jsr -672(a6)                                      ; +$0132 : 4EAEFD60
L_00266C:
    movea.l 12(a4),a0                                 ; +$0136 : 206C000C
    move.l a0,d0                                      ; +$013A : 2008
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_00267C                                    ; +$013E : 67000006
    jsr -672(a6)                                      ; +$0142 : 4EAEFD60
L_00267C:
    movea.l a4,a1                                     ; +$0146 : 224C
    movea.l $0004.w,a6                                ; +$0148 : 2C780004
    jsr -690(a6)                                      ; +$014C : 4EAEFD4E
    move.l #$00000000,32(a2)                          ; +$0150 : 257C000000000020
L_00268E:
    movea.l (a2),a0                                   ; +$0158 : 2052
    move.l a0,d0                                      ; +$015A : 2008
    tst.l d0                                          ; +$015C : 4A80
    beq.w L_0026A6                                    ; +$015E : 67000010
    movea.l 4(a2),a6                                  ; +$0162 : 2C6A0004
    jsr -66(a6)                                       ; +$0166 : 4EAEFFBE
    move.l #$00000000,(a2)                            ; +$016A : 24BC00000000
L_0026A6:
    movea.l 8(a2),a1                                  ; +$0170 : 226A0008
    move.l a1,d0                                      ; +$0174 : 2009
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_0026C2                                    ; +$0178 : 67000012
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -414(a6)                                      ; +$0180 : 4EAEFE62
    move.l #$00000000,8(a2)                           ; +$0184 : 257C000000000008
L_0026C2:
    movea.l 4(a2),a1                                  ; +$018C : 226A0004
    move.l a1,d0                                      ; +$0190 : 2009
    tst.l d0                                          ; +$0192 : 4A80
    beq.w L_0026DE                                    ; +$0194 : 67000012
    movea.l $0004.w,a6                                ; +$0198 : 2C780004
    jsr -414(a6)                                      ; +$019C : 4EAEFE62
    move.l #$00000000,4(a2)                           ; +$01A0 : 257C000000000004
L_0026DE:
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
    bra.w L_0025B8                                    ; +$01D0 : 6000FEB0
L_00270A:
    move.l d5,d3                                      ; +$01D4 : 2605
    bra.w L_002724                                    ; +$01D6 : 60000016
L_002710:
    movea.l 8(a2),a6                                  ; +$01DA : 2C6A0008
    move.l a6,d0                                      ; +$01DE : 200E
    tst.l d0                                          ; +$01E0 : 4A80
    beq.w L_002724                                    ; +$01E2 : 6700000A
    jsr -270(a6)                                      ; +$01E6 : 4EAEFEF2
    bra.w L_002560                                    ; +$01EA : 6000FE3E
L_002724:
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$01EE : 4CDF5FF3
    moveq #0,d2                                       ; +$01F2 : 7400
    rts                                               ; +$01F4 : 4E75
L_00272C:
    cmpi.l #$00000063,d5                              ; +$01F6 : 0C8500000063
    beq.w L_002560                                    ; +$01FC : 6700FE2C
    cmpi.l #$00000033,d5                              ; +$0200 : 0C8500000033
    bra.w L_0025A4                                    ; +$0206 : 6000FE66
L_002740:
    moveq #1,d1                                       ; +$020A : 7201
    movea.l -8(a5),a0                                 ; +$020C : 206DFFF8
    jsr 288(a0)                                       ; +$0210 : 4EA80120
    move.l d5,d3                                      ; +$0214 : 2605
    movem.l (a7)+,d0-d1/d4-d7/a0-a4/a6                ; +$0216 : 4CDF5FF3
    moveq #0,d2                                       ; +$021A : 7400
    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut
    rts                                               ; +$0222 : 4E75
L_00275A:
    bsr.w L_00276C                                    ; +$0224 : 61000010
    tst.l d0                                          ; +$0228 : 4A80
    beq.w L_002768                                    ; +$022A : 67000006
    bra.w L_0025C2                                    ; +$022E : 6000FE5C
L_002768:
    bra.w L_002724                                    ; +$0232 : 6000FFBA
L_00276C:
    movea.l 32(a2),a4                                 ; +$0236 : 286A0020
    move.l a4,d0                                      ; +$023A : 200C
    tst.l d0                                          ; +$023C : 4A80
    beq.w L_0027A4                                    ; +$023E : 6700002E
    moveq #0,d4                                       ; +$0242 : 7800
L_00277A:
    bsr.w L_0027AC                                    ; +$0244 : 61000030
    tst.l d0                                          ; +$0248 : 4A80
    beq.w L_0027A4                                    ; +$024A : 67000022
    addq.l #1,d4                                      ; +$024E : 5284
    cmpi.l #$0000012D,d4                              ; +$0250 : 0C840000012D
    bge.w L_0027A8                                    ; +$0256 : 6C00001A
    movea.l 8(a2),a6                                  ; +$025A : 2C6A0008
    move.l a6,d0                                      ; +$025E : 200E
    tst.l d0                                          ; +$0260 : 4A80
    beq.w L_0027A8                                    ; +$0262 : 6700000E
    jsr -270(a6)                                      ; +$0266 : 4EAEFEF2
    bra.w L_00277A                                    ; +$026A : 6000FFD8
L_0027A4:
    moveq #1,d0                                       ; +$026E : 7001
    rts                                               ; +$0270 : 4E75
L_0027A8:
    moveq #0,d0                                       ; +$0272 : 7000
    rts                                               ; +$0274 : 4E75
L_0027AC:
    move.l 20(a4),d6                                  ; +$0276 : 2C2C0014
    andi.l #$00000003,d6                              ; +$027A : 028600000003
    btst #0,d6                                        ; +$0280 : 08060000
    beq.w L_0027DC                                    ; +$0284 : 67000020
    movea.l 12(a4),a0                                 ; +$0288 : 206C000C
    move.l a0,d0                                      ; +$028C : 2008
    tst.l d0                                          ; +$028E : 4A80
    beq.w L_0027DC                                    ; +$0290 : 67000014
    movea.l $0004.w,a6                                ; +$0294 : 2C780004
    jsr -372(a6)                                      ; +$0298 : 4EAEFE8C
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_0027DC                                    ; +$029E : 67000006
    bclr #0,d6                                        ; +$02A2 : 08860000
L_0027DC:
    btst #1,d6                                        ; +$02A6 : 08060001
    beq.w L_002802                                    ; +$02AA : 67000020
    movea.l 16(a4),a0                                 ; +$02AE : 206C0010
    move.l a0,d0                                      ; +$02B2 : 2008
    tst.l d0                                          ; +$02B4 : 4A80
    beq.w L_002802                                    ; +$02B6 : 67000014
    movea.l $0004.w,a6                                ; +$02BA : 2C780004
    jsr -372(a6)                                      ; +$02BE : 4EAEFE8C
    tst.l d0                                          ; +$02C2 : 4A80
    beq.w L_002802                                    ; +$02C4 : 67000006
    bclr #1,d6                                        ; +$02C8 : 08860001
L_002802:
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
    beq.w L_0029C0                                    ; +$0018 : 67000198
    move.l (a4),d6                                    ; +$001C : 2C14
    tst.l d6                                          ; +$001E : 4A86
    beq.w L_0029C0                                    ; +$0020 : 67000190
    movea.l 32(a4),a2                                 ; +$0024 : 246C0020
    move.l a2,d6                                      ; +$0028 : 2C0A
    tst.l d6                                          ; +$002A : 4A86
    beq.w L_0029C0                                    ; +$002C : 67000184
    movea.l 8(a4),a6                                  ; +$0030 : 2C6C0008
    move.l a6,d6                                      ; +$0034 : 2C0E
    tst.l d6                                          ; +$0036 : 4A86
    beq.w L_0029C0                                    ; +$0038 : 67000178
    tst.l d0                                          ; +$003C : 4A80
    bmi.w L_0029C0                                    ; +$003E : 6B000172
    tst.l d1                                          ; +$0042 : 4A81
    bmi.w L_0029C0                                    ; +$0044 : 6B00016C
    tst.l d2                                          ; +$0048 : 4A82
    bmi.w L_0029C0                                    ; +$004A : 6B000166
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_0029C0                                    ; +$0050 : 6B000160
    tst.l d4                                          ; +$0054 : 4A84
    ble.w L_0029C0                                    ; +$0056 : 6F00015A
    tst.l d5                                          ; +$005A : 4A85
    ble.w L_0029C0                                    ; +$005C : 6F000154
    move.l 12(a4),d6                                  ; +$0060 : 2C2C000C
    tst.l d6                                          ; +$0064 : 4A86
    ble.w L_0029C0                                    ; +$0066 : 6F00014A
    cmpi.l #$00007FFF,d6                              ; +$006A : 0C8600007FFF
    bgt.w L_0029C0                                    ; +$0070 : 6E000140
    move.l 16(a4),d6                                  ; +$0074 : 2C2C0010
    tst.l d6                                          ; +$0078 : 4A86
    ble.w L_0029C0                                    ; +$007A : 6F000136
    cmpi.l #$00007FFF,d6                              ; +$007E : 0C8600007FFF
    bgt.w L_0029C0                                    ; +$0084 : 6E00012C
    move.l 12(a4),d6                                  ; +$0088 : 2C2C000C
    sub.l d4,d6                                       ; +$008C : 9C84
    tst.l d6                                          ; +$008E : 4A86
    bmi.w L_0029C0                                    ; +$0090 : 6B000120
    cmp.l d6,d0                                       ; +$0094 : B086
    bgt.w L_0029C0                                    ; +$0096 : 6E00011A
    cmp.l d6,d2                                       ; +$009A : B486
    bgt.w L_0029C0                                    ; +$009C : 6E000114
    move.l 16(a4),d6                                  ; +$00A0 : 2C2C0010
    sub.l d5,d6                                       ; +$00A4 : 9C85
    tst.l d6                                          ; +$00A6 : 4A86
    bmi.w L_0029C0                                    ; +$00A8 : 6B000108
    cmp.l d6,d1                                       ; +$00AC : B286
    bgt.w L_0029C0                                    ; +$00AE : 6E000102
    cmp.l d6,d3                                       ; +$00B2 : B686
    bgt.w L_0029C0                                    ; +$00B4 : 6E0000FC
    tst.l 8(a2)                                       ; +$00B8 : 4AAA0008
    beq.w L_0028D4                                    ; +$00BC : 67000008
    movea.l (a2),a0                                   ; +$00C0 : 2052
    bra.w L_0028D8                                    ; +$00C2 : 60000006
L_0028D4:
    movea.l 4(a2),a0                                  ; +$00C6 : 206A0004
L_0028D8:
    move.l a0,d6                                      ; +$00CA : 2C08
    tst.l d6                                          ; +$00CC : 4A86
    beq.w L_0029C0                                    ; +$00CE : 670000E2
    movea.l (a0),a0                                   ; +$00D2 : 2050
    move.l a0,d6                                      ; +$00D4 : 2C08
    tst.l d6                                          ; +$00D6 : 4A86
    beq.w L_0029C0                                    ; +$00D8 : 670000D8
    move.l #$00000000,d6                              ; +$00DC : 2C3C00000000
    move.w (a0),d6                                    ; +$00E2 : 3C10
    lsl.l #3,d6                                       ; +$00E4 : E78E
    cmp.l 12(a4),d6                                   ; +$00E6 : BCAC000C
    blt.w L_0029C0                                    ; +$00EA : 6D0000C6
    move.l #$00000000,d6                              ; +$00EE : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00F4 : 3C280002
    cmp.l 16(a4),d6                                   ; +$00F8 : BCAC0010
    blt.w L_0029C0                                    ; +$00FC : 6D0000B4
    move.l #$00000000,d6                              ; +$0100 : 2C3C00000000
    move.b 5(a0),d6                                   ; +$0106 : 1C280005
    cmp.l 28(a4),d6                                   ; +$010A : BCAC001C
    bne.w L_0029C0                                    ; +$010E : 660000A2
    tst.l d6                                          ; +$0112 : 4A86
    ble.w L_0029C0                                    ; +$0114 : 6F00009C
    cmpi.l #$00000008,d6                              ; +$0118 : 0C8600000008
    bgt.w L_0029C0                                    ; +$011E : 6E000092
    move.l d6,-(a7)                                   ; +$0122 : 2F06
    move.l 20(a2),d6                                  ; +$0124 : 2C2A0014
    andi.l #$00000001,d6                              ; +$0128 : 028600000001
    beq.w L_002992                                    ; +$012E : 67000054
    move.l d0,-(a7)                                   ; +$0132 : 2F00
    move.l d1,-(a7)                                   ; +$0134 : 2F01
    move.l a0,-(a7)                                   ; +$0136 : 2F08
    move.l a1,-(a7)                                   ; +$0138 : 2F09
    movea.l 12(a2),a0                                 ; +$013A : 206A000C
    move.l a0,d6                                      ; +$013E : 2C08
    tst.l d6                                          ; +$0140 : 4A86
    beq.w L_002980                                    ; +$0142 : 6700002E
    movea.l $0004.w,a6                                ; +$0146 : 2C780004
    jsr -372(a6)                                      ; +$014A : 4EAEFE8C
    tst.l d0                                          ; +$014E : 4A80
    beq.w L_002980                                    ; +$0150 : 67000020
    move.l 20(a2),d6                                  ; +$0154 : 2C2A0014
    andi.l #$FFFFFFFE,d6                              ; +$0158 : 0286FFFFFFFE
    move.l d6,20(a2)                                  ; +$015E : 25460014
    movea.l 8(a4),a6                                  ; +$0162 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$0166 : 225F
    movea.l (a7)+,a0                                  ; +$0168 : 205F
    move.l (a7)+,d1                                   ; +$016A : 221F
    move.l (a7)+,d0                                   ; +$016C : 201F
    bra.w L_002992                                    ; +$016E : 60000014
L_002980:
    movea.l 8(a4),a6                                  ; +$0172 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$0176 : 225F
    movea.l (a7)+,a0                                  ; +$0178 : 205F
    move.l (a7)+,d1                                   ; +$017A : 221F
    move.l (a7)+,d0                                   ; +$017C : 201F
    move.l (a7)+,d6                                   ; +$017E : 2C1F
    bra.w L_0029C0                                    ; +$0180 : 60000030
L_002992:
    move.l (a7)+,d6                                   ; +$0184 : 2C1F
    movea.l a0,a1                                     ; +$0186 : 2248
    movea.l #$00000000,a2                             ; +$0188 : 247C00000000
    move.l #$000000C0,d6                              ; +$018E : 2C3C000000C0
    move.l #$000000FF,d7                              ; +$0194 : 2E3C000000FF
    jsr -30(a6)                                       ; +$019A : 4EAEFFE2
    tst.l d0                                          ; +$019E : 4A80
    beq.w L_0029C0                                    ; +$01A0 : 67000010
    jsr -228(a6)                                      ; +$01A4 : 4EAEFF1C
    move.l #$00000001,d3                              ; +$01A8 : 263C00000001
    bra.w L_0029C6                                    ; +$01AE : 60000008
L_0029C0:
    move.l #$00000000,d3                              ; +$01B2 : 263C00000000
L_0029C6:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$01B8 : 4CDF77F7
    moveq #0,d2                                       ; +$01BC : 7400
    rts                                               ; +$01BE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 20 : aga blit fill --------
Entry_20:
Aga_Blit_Fill:
    bra.w L_007CCE                                    ; +$0000 : 600052FA
    move.l (a3)+,d5                                   ; +$0004 : 2A1B
    move.l (a3)+,d4                                   ; +$0006 : 281B
    move.l (a3)+,d1                                   ; +$0008 : 221B
    move.l (a3)+,d0                                   ; +$000A : 201B
    movea.l 456(a5),a4                                ; +$000C : 286D01C8
    move.l a4,d6                                      ; +$0010 : 2C0C
    tst.l d6                                          ; +$0012 : 4A86
    beq.w L_002BE4                                    ; +$0014 : 670001FC
    move.l (a4),d6                                    ; +$0018 : 2C14
    tst.l d6                                          ; +$001A : 4A86
    beq.w L_002BE4                                    ; +$001C : 670001F4
    movea.l 32(a4),a2                                 ; +$0020 : 246C0020
    move.l a2,d6                                      ; +$0024 : 2C0A
    tst.l d6                                          ; +$0026 : 4A86
    beq.w L_002BE4                                    ; +$0028 : 670001E8
    movea.l 8(a4),a6                                  ; +$002C : 2C6C0008
    move.l a6,d6                                      ; +$0030 : 2C0E
    tst.l d6                                          ; +$0032 : 4A86
    beq.w L_002BE4                                    ; +$0034 : 670001DC
    tst.l d0                                          ; +$0038 : 4A80
    bmi.w L_002BE4                                    ; +$003A : 6B0001D6
    tst.l d1                                          ; +$003E : 4A81
    bmi.w L_002BE4                                    ; +$0040 : 6B0001D0
    tst.l d3                                          ; +$0044 : 4A83
    bmi.w L_002BE4                                    ; +$0046 : 6B0001CA
    tst.l d4                                          ; +$004A : 4A84
    ble.w L_002BE4                                    ; +$004C : 6F0001C4
    tst.l d5                                          ; +$0050 : 4A85
    ble.w L_002BE4                                    ; +$0052 : 6F0001BE
    move.l 12(a4),d6                                  ; +$0056 : 2C2C000C
    tst.l d6                                          ; +$005A : 4A86
    ble.w L_002BE4                                    ; +$005C : 6F0001B4
    cmpi.l #$00007FFF,d6                              ; +$0060 : 0C8600007FFF
    bgt.w L_002BE4                                    ; +$0066 : 6E0001AA
    move.l 16(a4),d6                                  ; +$006A : 2C2C0010
    tst.l d6                                          ; +$006E : 4A86
    ble.w L_002BE4                                    ; +$0070 : 6F0001A0
    cmpi.l #$00007FFF,d6                              ; +$0074 : 0C8600007FFF
    bgt.w L_002BE4                                    ; +$007A : 6E000196
    move.l 12(a4),d6                                  ; +$007E : 2C2C000C
    sub.l d4,d6                                       ; +$0082 : 9C84
    tst.l d6                                          ; +$0084 : 4A86
    bmi.w L_002BE4                                    ; +$0086 : 6B00018A
    cmp.l d6,d0                                       ; +$008A : B086
    bgt.w L_002BE4                                    ; +$008C : 6E000184
    move.l 16(a4),d6                                  ; +$0090 : 2C2C0010
    sub.l d5,d6                                       ; +$0094 : 9C85
    tst.l d6                                          ; +$0096 : 4A86
    bmi.w L_002BE4                                    ; +$0098 : 6B000178
    cmp.l d6,d1                                       ; +$009C : B286
    bgt.w L_002BE4                                    ; +$009E : 6E000172
    tst.l 8(a2)                                       ; +$00A2 : 4AAA0008
    beq.w L_002A82                                    ; +$00A6 : 67000008
    movea.l (a2),a0                                   ; +$00AA : 2052
    bra.w L_002A86                                    ; +$00AC : 60000006
L_002A82:
    movea.l 4(a2),a0                                  ; +$00B0 : 206A0004
L_002A86:
    move.l a0,d6                                      ; +$00B4 : 2C08
    tst.l d6                                          ; +$00B6 : 4A86
    beq.w L_002BE4                                    ; +$00B8 : 67000158
    movea.l (a0),a0                                   ; +$00BC : 2050
    move.l a0,d6                                      ; +$00BE : 2C08
    tst.l d6                                          ; +$00C0 : 4A86
    beq.w L_002BE4                                    ; +$00C2 : 6700014E
    move.l #$00000000,d6                              ; +$00C6 : 2C3C00000000
    move.w (a0),d6                                    ; +$00CC : 3C10
    lsl.l #3,d6                                       ; +$00CE : E78E
    cmp.l 12(a4),d6                                   ; +$00D0 : BCAC000C
    blt.w L_002BE4                                    ; +$00D4 : 6D00013C
    move.l #$00000000,d6                              ; +$00D8 : 2C3C00000000
    move.w 2(a0),d6                                   ; +$00DE : 3C280002
    cmp.l 16(a4),d6                                   ; +$00E2 : BCAC0010
    blt.w L_002BE4                                    ; +$00E6 : 6D00012A
    move.l #$00000000,d6                              ; +$00EA : 2C3C00000000
    move.b 5(a0),d6                                   ; +$00F0 : 1C280005
    cmp.l 28(a4),d6                                   ; +$00F4 : BCAC001C
    bne.w L_002BE4                                    ; +$00F8 : 66000118
    tst.l d6                                          ; +$00FC : 4A86
    ble.w L_002BE4                                    ; +$00FE : 6F000112
    cmpi.l #$00000008,d6                              ; +$0102 : 0C8600000008
    bgt.w L_002BE4                                    ; +$0108 : 6E000108
    move.l d6,d2                                      ; +$010C : 2406
    movea.l a0,a1                                     ; +$010E : 2248
    addq.l #8,a1                                      ; +$0110 : 5089
L_002AE4:
    move.l (a1)+,d6                                   ; +$0112 : 2C19
    tst.l d6                                          ; +$0114 : 4A86
    beq.w L_002BE4                                    ; +$0116 : 670000FA
    cmpi.l #$FFFFFFFF,d6                              ; +$011A : 0C86FFFFFFFF
    beq.w L_002BE4                                    ; +$0120 : 670000F0
    subq.l #1,d2                                      ; +$0124 : 5382
    bne.w L_002AE4                                    ; +$0126 : 6600FFEA
    move.l #$00000000,d2                              ; +$012A : 243C00000000
    move.b 5(a0),d2                                   ; +$0130 : 14280005
    move.l #$00000001,d6                              ; +$0134 : 2C3C00000001
L_002B0C:
    lsl.l #1,d6                                       ; +$013A : E38E
    subq.l #1,d2                                      ; +$013C : 5382
    bne.w L_002B0C                                    ; +$013E : 6600FFFA
    cmp.l d6,d3                                       ; +$0142 : B686
    bcc.w L_002BE4                                    ; +$0144 : 640000CC
    move.l d6,-(a7)                                   ; +$0148 : 2F06
    move.l 20(a2),d6                                  ; +$014A : 2C2A0014
    andi.l #$00000001,d6                              ; +$014E : 028600000001
    beq.w L_002B7C                                    ; +$0154 : 67000054
    move.l d0,-(a7)                                   ; +$0158 : 2F00
    move.l d1,-(a7)                                   ; +$015A : 2F01
    move.l a0,-(a7)                                   ; +$015C : 2F08
    move.l a1,-(a7)                                   ; +$015E : 2F09
    movea.l 12(a2),a0                                 ; +$0160 : 206A000C
    move.l a0,d6                                      ; +$0164 : 2C08
    tst.l d6                                          ; +$0166 : 4A86
    beq.w L_002B6A                                    ; +$0168 : 6700002E
    movea.l $0004.w,a6                                ; +$016C : 2C780004
    jsr -372(a6)                                      ; +$0170 : 4EAEFE8C
    tst.l d0                                          ; +$0174 : 4A80
    beq.w L_002B6A                                    ; +$0176 : 67000020
    move.l 20(a2),d6                                  ; +$017A : 2C2A0014
    andi.l #$FFFFFFFE,d6                              ; +$017E : 0286FFFFFFFE
    move.l d6,20(a2)                                  ; +$0184 : 25460014
    movea.l 8(a4),a6                                  ; +$0188 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$018C : 225F
    movea.l (a7)+,a0                                  ; +$018E : 205F
    move.l (a7)+,d1                                   ; +$0190 : 221F
    move.l (a7)+,d0                                   ; +$0192 : 201F
    bra.w L_002B7C                                    ; +$0194 : 60000014
L_002B6A:
    movea.l 8(a4),a6                                  ; +$0198 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$019C : 225F
    movea.l (a7)+,a0                                  ; +$019E : 205F
    move.l (a7)+,d1                                   ; +$01A0 : 221F
    move.l (a7)+,d0                                   ; +$01A2 : 201F
    move.l (a7)+,d6                                   ; +$01A4 : 2C1F
    bra.w L_002BE4                                    ; +$01A6 : 6000006A
L_002B7C:
    move.l (a7)+,d6                                   ; +$01AA : 2C1F
    move.l d3,-(a7)                                   ; +$01AC : 2F03
    move.l d6,-(a7)                                   ; +$01AE : 2F06
    movea.l a0,a4                                     ; +$01B0 : 2848
    move.l d0,d2                                      ; +$01B2 : 2400
    move.l d1,d3                                      ; +$01B4 : 2601
    move.l #$00000001,d7                              ; +$01B6 : 2E3C00000001
L_002B8E:
    move.l 4(a7),d6                                   ; +$01BC : 2C2F0004
    and.l d7,d6                                       ; +$01C0 : CC87
    tst.l d6                                          ; +$01C2 : 4A86
    beq.w L_002BA4                                    ; +$01C4 : 6700000C
    move.l #$000000F0,d6                              ; +$01C8 : 2C3C000000F0
    bra.w L_002BAA                                    ; +$01CE : 60000008
L_002BA4:
    move.l #$00000000,d6                              ; +$01D2 : 2C3C00000000
L_002BAA:
    move.l d2,d0                                      ; +$01D8 : 2002
    move.l d3,d1                                      ; +$01DA : 2203
    movea.l a4,a0                                     ; +$01DC : 204C
    movea.l a4,a1                                     ; +$01DE : 224C
    movea.l #$00000000,a2                             ; +$01E0 : 247C00000000
    jsr -30(a6)                                       ; +$01E6 : 4EAEFFE2
    tst.l d0                                          ; +$01EA : 4A80
    beq.w L_002BD8                                    ; +$01EC : 67000018
    jsr -228(a6)                                      ; +$01F0 : 4EAEFF1C
    lsl.l #1,d7                                       ; +$01F4 : E38F
    cmp.l (a7),d7                                     ; +$01F6 : BE97
    bne.w L_002B8E                                    ; +$01F8 : 6600FFC2
    move.l #$00000001,d3                              ; +$01FC : 263C00000001
    bra.w L_002BDE                                    ; +$0202 : 60000008
L_002BD8:
    move.l #$00000000,d3                              ; +$0206 : 263C00000000
L_002BDE:
    addq.l #8,a7                                      ; +$020C : 508F
    bra.w L_002BEA                                    ; +$020E : 60000008
L_002BE4:
    move.l #$00000000,d3                              ; +$0212 : 263C00000000
L_002BEA:
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
    beq.w L_002CF0                                    ; +$000C : 670000C6
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002CF0                                    ; +$0016 : 670000BC
    move.l 342(a4),d0                                 ; +$001A : 202C0156
    tst.l d0                                          ; +$001E : 4A80
    bne.w L_002CB4                                    ; +$0020 : 66000076
    move.l 64(a4),d0                                  ; +$0024 : 202C0040
    tst.l d0                                          ; +$0028 : 4A80
    bne.w L_002CF0                                    ; +$002A : 660000A8
    movea.l 456(a5),a0                                ; +$002E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0032 : 2C680008
    move.l a6,d0                                      ; +$0036 : 200E
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_002CF0                                    ; +$003A : 67000098
    movea.l $0004.w,a6                                ; +$003E : 2C780004
    move.l #$0000000C,d0                              ; +$0042 : 203C0000000C
    move.l #$00010001,d1                              ; +$0048 : 223C00010001
    jsr -198(a6)                                      ; +$004E : 4EAEFF3A
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_002CF0                                    ; +$0054 : 6700007E
    movea.l d0,a2                                     ; +$0058 : 2440
    movea.l 456(a5),a0                                ; +$005A : 206D01C8
    movea.l 8(a0),a6                                  ; +$005E : 2C680008
    movea.l a2,a0                                     ; +$0062 : 204A
    move.l #$00000040,d0                              ; +$0064 : 203C00000040
    jsr -594(a6)                                      ; +$006A : 4EAEFDAE
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_002CC2                                    ; +$0070 : 67000034
    movea.l a2,a1                                     ; +$0074 : 224A
    move.l #$00002710,d0                              ; +$0076 : 203C00002710
    move.l #$000000FF,d1                              ; +$007C : 223C000000FF
    jsr -378(a6)                                      ; +$0082 : 4EAEFE86
    movea.l a2,a1                                     ; +$0086 : 224A
    jsr -366(a6)                                      ; +$0088 : 4EAEFE92
    move.l a2,342(a4)                                 ; +$008C : 294A0156
    move.l a2,64(a4)                                  ; +$0090 : 294A0040
    bra.w L_002CE6                                    ; +$0094 : 60000034
L_002CB4:
    move.l 64(a4),d1                                  ; +$0098 : 222C0040
    cmp.l d1,d0                                       ; +$009C : B081
    beq.w L_002CE6                                    ; +$009E : 6700002A
    bra.w L_002CF0                                    ; +$00A2 : 60000030
L_002CC2:
    movea.l 4(a2),a0                                  ; +$00A6 : 206A0004
    move.l a0,d0                                      ; +$00AA : 2008
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_002CD2                                    ; +$00AE : 67000006
    jsr -546(a6)                                      ; +$00B2 : 4EAEFDDE
L_002CD2:
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    movea.l a2,a1                                     ; +$00BA : 224A
    move.l #$0000000C,d0                              ; +$00BC : 203C0000000C
    jsr -210(a6)                                      ; +$00C2 : 4EAEFF2E
    bra.w L_002CF0                                    ; +$00C6 : 6000000C
L_002CE6:
    move.l #$00000001,d3                              ; +$00CA : 263C00000001
    bra.w L_002CF6                                    ; +$00D0 : 60000008
L_002CF0:
    move.l #$00000000,d3                              ; +$00D4 : 263C00000000
L_002CF6:
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
    beq.w L_002D9C                                    ; +$000C : 6700008C
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002D9C                                    ; +$0016 : 67000082
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_002D9C                                    ; +$002A : 6700006E
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_002D9C                                    ; +$0034 : 66000064
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_002D9C                                    ; +$0044 : 67000054
    movea.l 8(a2),a1                                  ; +$0048 : 226A0008
    move.l a1,d0                                      ; +$004C : 2009
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_002D9C                                    ; +$0050 : 67000048
    move.w 28(a1),d0                                  ; +$0054 : 3029001C
    cmpi.w #$0001,d0                                  ; +$0058 : 0C400001
    beq.w L_002D70                                    ; +$005C : 67000010
    move.l d6,d0                                      ; +$0060 : 2006
    andi.l #$00000002,d0                              ; +$0062 : 028000000002
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_002D9C                                    ; +$006A : 6700002E
L_002D70:
    ori.l #$00000001,342(a4)                          ; +$006E : 00AC000000010156
    movea.l a4,a0                                     ; +$0076 : 204C
    jsr -378(a6)                                      ; +$0078 : 4EAEFE86
    tst.l d0                                          ; +$007C : 4A80
    bne.w L_002D9C                                    ; +$007E : 6600001A
    jsr -390(a6)                                      ; +$0082 : 4EAEFE7A
    tst.l d0                                          ; +$0086 : 4A80
    bne.w L_002D9C                                    ; +$0088 : 66000010
    bra.w L_002D92                                    ; +$008C : 60000002
L_002D92:
    move.l #$00000001,d3                              ; +$0090 : 263C00000001
    bra.w L_002DA2                                    ; +$0096 : 60000008
L_002D9C:
    move.l #$00000000,d3                              ; +$009A : 263C00000000
L_002DA2:
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
    beq.w L_002E8C                                    ; +$000C : 670000D0
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_002E8C                                    ; +$0016 : 670000C6
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_002E5A                                    ; +$002A : 67000080
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_002E8C                                    ; +$0034 : 660000A8
    movea.l 456(a5),a0                                ; +$0038 : 206D01C8
    movea.l 4(a0),a6                                  ; +$003C : 2C680004
    move.l a6,d0                                      ; +$0040 : 200E
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_002E8C                                    ; +$0044 : 67000098
    movea.l 456(a5),a0                                ; +$0048 : 206D01C8
    move.l 8(a0),d0                                   ; +$004C : 20280008
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_002E8C                                    ; +$0052 : 6700008A
    move.l #$00000000,64(a4)                          ; +$0056 : 297C000000000040
    movea.l a4,a0                                     ; +$005E : 204C
    jsr -378(a6)                                      ; +$0060 : 4EAEFE86
    tst.l d0                                          ; +$0064 : 4A80
    bne.w L_002E68                                    ; +$0066 : 66000052
    jsr -390(a6)                                      ; +$006A : 4EAEFE7A
    tst.l d0                                          ; +$006E : 4A80
    bne.w L_002E70                                    ; +$0070 : 66000050
    movea.l 456(a5),a0                                ; +$0074 : 206D01C8
    movea.l 8(a0),a6                                  ; +$0078 : 2C680008
    jsr -270(a6)                                      ; +$007C : 4EAEFEF2
    movea.l 4(a2),a0                                  ; +$0080 : 206A0004
    move.l a0,d0                                      ; +$0084 : 2008
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_002E3E                                    ; +$0088 : 67000006
    jsr -546(a6)                                      ; +$008C : 4EAEFDDE
L_002E3E:
    move.l #$00000000,342(a4)                         ; +$0090 : 297C000000000156
    movea.l $0004.w,a6                                ; +$0098 : 2C780004
    movea.l a2,a1                                     ; +$009C : 224A
    move.l #$0000000C,d0                              ; +$009E : 203C0000000C
    jsr -210(a6)                                      ; +$00A4 : 4EAEFF2E
    bra.w L_002E82                                    ; +$00A8 : 6000002A
L_002E5A:
    move.l 64(a4),d0                                  ; +$00AC : 202C0040
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_002E82                                    ; +$00B2 : 67000020
    bra.w L_002E8C                                    ; +$00B6 : 60000026
L_002E68:
    move.l a2,64(a4)                                  ; +$00BA : 294A0040
    bra.w L_002E8C                                    ; +$00BE : 6000001E
L_002E70:
    move.l a2,64(a4)                                  ; +$00C2 : 294A0040
    movea.l a4,a0                                     ; +$00C6 : 204C
    jsr -378(a6)                                      ; +$00C8 : 4EAEFE86
    jsr -390(a6)                                      ; +$00CC : 4EAEFE7A
    bra.w L_002E8C                                    ; +$00D0 : 6000000C
L_002E82:
    move.l #$00000001,d3                              ; +$00D4 : 263C00000001
    bra.w L_002E92                                    ; +$00DA : 60000008
L_002E8C:
    move.l #$00000000,d3                              ; +$00DE : 263C00000000
L_002E92:
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
    beq.w L_002FFA                                    ; +$0010 : 6700014A
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_002FFA                                    ; +$001A : 67000140
    cmpi.l #$000000FF,d4                              ; +$001E : 0C84000000FF
    bhi.w L_002FFA                                    ; +$0024 : 62000136
    cmpi.l #$000000DE,d5                              ; +$0028 : 0C85000000DE
    bhi.w L_002FFA                                    ; +$002E : 6200012C
    move.l 342(a4),d6                                 ; +$0032 : 2C2C0156
    move.l d6,d0                                      ; +$0036 : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0038 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$003E : 2440
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_002FFA                                    ; +$0042 : 67000118
    move.l 64(a4),d1                                  ; +$0046 : 222C0040
    cmp.l d1,d0                                       ; +$004A : B081
    bne.w L_002FFA                                    ; +$004C : 6600010E
    move.l d6,d0                                      ; +$0050 : 2006
    andi.l #$00000003,d0                              ; +$0052 : 028000000003
    tst.l d0                                          ; +$0058 : 4A80
    bne.w L_002FFA                                    ; +$005A : 66000100
    movea.l 456(a5),a0                                ; +$005E : 206D01C8
    movea.l 8(a0),a6                                  ; +$0062 : 2C680008
    move.l a6,d0                                      ; +$0066 : 200E
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_002FFA                                    ; +$006A : 670000F0
    movea.l 8(a2),a1                                  ; +$006E : 226A0008
    move.l a1,d0                                      ; +$0072 : 2009
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_002FFA                                    ; +$0076 : 670000E4
    move.l 12(a1),d0                                  ; +$007A : 2029000C
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_002FFA                                    ; +$0080 : 670000DA
    movea.l 16(a1),a0                                 ; +$0084 : 20690010
    move.l a0,d0                                      ; +$0088 : 2008
    tst.l d0                                          ; +$008A : 4A80
    beq.w L_002FFA                                    ; +$008C : 670000CE
    move.w 30(a1),d0                                  ; +$0090 : 3029001E
    cmpi.w #$0040,d0                                  ; +$0094 : 0C400040
    bne.w L_002FFA                                    ; +$0098 : 660000C2
    move.w 28(a1),d7                                  ; +$009C : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00A0 : 0C470000
    bls.w L_002FFA                                    ; +$00A4 : 630000B6
    cmpi.w #$003F,d7                                  ; +$00A8 : 0C47003F
    bcc.w L_002FFA                                    ; +$00AC : 640000AE
    movea.l 16(a1),a0                                 ; +$00B0 : 20690010
    subq.l #6,a0                                      ; +$00B4 : 5D88
    move.w (a0),d0                                    ; +$00B6 : 3010
    cmpi.w #$0001,d0                                  ; +$00B8 : 0C400001
    bne.w L_002FFA                                    ; +$00BC : 6600009E
    move.w 2(a0),d0                                   ; +$00C0 : 30280002
    cmpi.w #$2710,d0                                  ; +$00C4 : 0C402710
    bne.w L_002FFA                                    ; +$00C8 : 66000092
    move.w 4(a0),d0                                   ; +$00CC : 30280004
    cmpi.w #$00FF,d0                                  ; +$00D0 : 0C4000FF
    bne.w L_002FFA                                    ; +$00D4 : 66000086
    move.w d7,d6                                      ; +$00D8 : 3C07
    subq.w #1,d6                                      ; +$00DA : 5346
    beq.w L_002FB6                                    ; +$00DC : 6700003A
    movea.l 16(a1),a0                                 ; +$00E0 : 20690010
    subq.l #6,a0                                      ; +$00E4 : 5D88
L_002F84:
    subq.l #6,a0                                      ; +$00E6 : 5D88
    move.w (a0),d0                                    ; +$00E8 : 3010
    cmpi.w #$0001,d0                                  ; +$00EA : 0C400001
    beq.w L_002F9A                                    ; +$00EE : 6700000C
    subq.w #1,d6                                      ; +$00F2 : 5346
    bne.w L_002F84                                    ; +$00F4 : 6600FFF0
    bra.w L_002FB6                                    ; +$00F8 : 6000001E
L_002F9A:
    move.w 2(a0),d0                                   ; +$00FC : 30280002
    move.w d4,d1                                      ; +$0100 : 3204
    cmp.w d0,d1                                       ; +$0102 : B240
    bhi.w L_002FB6                                    ; +$0104 : 62000012
    bne.w L_002FFA                                    ; +$0108 : 66000052
    move.w 4(a0),d0                                   ; +$010C : 30280004
    move.w d5,d1                                      ; +$0110 : 3205
    cmp.w d0,d1                                       ; +$0112 : B240
    bls.w L_002FFA                                    ; +$0114 : 63000046
L_002FB6:
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
    bra.w L_002FF0                                    ; +$014E : 60000002
L_002FF0:
    move.l #$00000001,d3                              ; +$0152 : 263C00000001
    bra.w L_003000                                    ; +$0158 : 60000008
L_002FFA:
    move.l #$00000000,d3                              ; +$015C : 263C00000000
L_003000:
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
    beq.w L_003146                                    ; +$0010 : 67000128
    movea.l (a4),a4                                   ; +$0014 : 2854
    move.l a4,d0                                      ; +$0016 : 200C
    tst.l d0                                          ; +$0018 : 4A80
    beq.w L_003146                                    ; +$001A : 6700011E
    cmpi.l #$00000180,d4                              ; +$001E : 0C8400000180
    bcs.w L_003146                                    ; +$0024 : 65000114
    cmpi.l #$000001BE,d4                              ; +$0028 : 0C84000001BE
    bhi.w L_003146                                    ; +$002E : 6200010A
    move.l d4,d0                                      ; +$0032 : 2004
    andi.l #$00000001,d0                              ; +$0034 : 028000000001
    tst.l d0                                          ; +$003A : 4A80
    bne.w L_003146                                    ; +$003C : 660000FC
    cmpi.l #$00000FFF,d5                              ; +$0040 : 0C8500000FFF
    bhi.w L_003146                                    ; +$0046 : 620000F2
    move.l 342(a4),d6                                 ; +$004A : 2C2C0156
    move.l d6,d0                                      ; +$004E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0050 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0056 : 2440
    tst.l d0                                          ; +$0058 : 4A80
    beq.w L_003146                                    ; +$005A : 670000DE
    move.l 64(a4),d1                                  ; +$005E : 222C0040
    cmp.l d1,d0                                       ; +$0062 : B081
    bne.w L_003146                                    ; +$0064 : 660000D4
    move.l d6,d0                                      ; +$0068 : 2006
    andi.l #$00000003,d0                              ; +$006A : 028000000003
    tst.l d0                                          ; +$0070 : 4A80
    bne.w L_003146                                    ; +$0072 : 660000C6
    movea.l 456(a5),a0                                ; +$0076 : 206D01C8
    movea.l 8(a0),a6                                  ; +$007A : 2C680008
    move.l a6,d0                                      ; +$007E : 200E
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_003146                                    ; +$0082 : 670000B6
    movea.l 8(a2),a1                                  ; +$0086 : 226A0008
    move.l a1,d0                                      ; +$008A : 2009
    tst.l d0                                          ; +$008C : 4A80
    beq.w L_003146                                    ; +$008E : 670000AA
    move.l 12(a1),d0                                  ; +$0092 : 2029000C
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_003146                                    ; +$0098 : 670000A0
    movea.l 16(a1),a0                                 ; +$009C : 20690010
    move.l a0,d0                                      ; +$00A0 : 2008
    tst.l d0                                          ; +$00A2 : 4A80
    beq.w L_003146                                    ; +$00A4 : 67000094
    move.w 30(a1),d0                                  ; +$00A8 : 3029001E
    cmpi.w #$0040,d0                                  ; +$00AC : 0C400040
    bne.w L_003146                                    ; +$00B0 : 66000088
    move.w 28(a1),d7                                  ; +$00B4 : 3E29001C
    cmpi.w #$0000,d7                                  ; +$00B8 : 0C470000
    bls.w L_003146                                    ; +$00BC : 6300007C
    cmpi.w #$003F,d7                                  ; +$00C0 : 0C47003F
    bcc.w L_003146                                    ; +$00C4 : 64000074
    movea.l 16(a1),a0                                 ; +$00C8 : 20690010
    subq.l #6,a0                                      ; +$00CC : 5D88
    move.w (a0),d0                                    ; +$00CE : 3010
    cmpi.w #$0001,d0                                  ; +$00D0 : 0C400001
    bne.w L_003146                                    ; +$00D4 : 66000064
    move.w 2(a0),d0                                   ; +$00D8 : 30280002
    cmpi.w #$2710,d0                                  ; +$00DC : 0C402710
    bne.w L_003146                                    ; +$00E0 : 66000058
    move.w 4(a0),d0                                   ; +$00E4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00E8 : 0C4000FF
    bne.w L_003146                                    ; +$00EC : 6600004C
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
    bra.w L_00313C                                    ; +$012C : 60000002
L_00313C:
    move.l #$00000001,d3                              ; +$0130 : 263C00000001
    bra.w L_00314C                                    ; +$0136 : 60000008
L_003146:
    move.l #$00000000,d3                              ; +$013A : 263C00000000
L_00314C:
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
    beq.w L_00321A                                    ; +$000C : 670000B8
    movea.l (a4),a4                                   ; +$0010 : 2854
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00321A                                    ; +$0016 : 670000AE
    move.l 342(a4),d6                                 ; +$001A : 2C2C0156
    move.l d6,d0                                      ; +$001E : 2006
    andi.l #$FFFFFFFC,d0                              ; +$0020 : 0280FFFFFFFC
    movea.l d0,a2                                     ; +$0026 : 2440
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_00321A                                    ; +$002A : 6700009A
    move.l 64(a4),d1                                  ; +$002E : 222C0040
    cmp.l d1,d0                                       ; +$0032 : B081
    bne.w L_00321A                                    ; +$0034 : 66000090
    move.l d6,d0                                      ; +$0038 : 2006
    andi.l #$00000003,d0                              ; +$003A : 028000000003
    tst.l d0                                          ; +$0040 : 4A80
    bne.w L_00321A                                    ; +$0042 : 66000082
    movea.l 8(a2),a1                                  ; +$0046 : 226A0008
    move.l a1,d0                                      ; +$004A : 2009
    tst.l d0                                          ; +$004C : 4A80
    beq.w L_00321A                                    ; +$004E : 67000076
    move.l 12(a1),d0                                  ; +$0052 : 2029000C
    tst.l d0                                          ; +$0056 : 4A80
    beq.w L_00321A                                    ; +$0058 : 6700006C
    movea.l 16(a1),a0                                 ; +$005C : 20690010
    move.l a0,d0                                      ; +$0060 : 2008
    tst.l d0                                          ; +$0062 : 4A80
    beq.w L_00321A                                    ; +$0064 : 67000060
    move.w 30(a1),d0                                  ; +$0068 : 3029001E
    cmpi.w #$0040,d0                                  ; +$006C : 0C400040
    bne.w L_00321A                                    ; +$0070 : 66000054
    move.w 28(a1),d7                                  ; +$0074 : 3E29001C
    cmpi.w #$0001,d7                                  ; +$0078 : 0C470001
    bls.w L_00321A                                    ; +$007C : 63000048
    cmpi.w #$0040,d7                                  ; +$0080 : 0C470040
    bhi.w L_00321A                                    ; +$0084 : 62000040
    movea.l 16(a1),a0                                 ; +$0088 : 20690010
    subq.l #6,a0                                      ; +$008C : 5D88
    move.w (a0),d0                                    ; +$008E : 3010
    cmpi.w #$0001,d0                                  ; +$0090 : 0C400001
    bne.w L_00321A                                    ; +$0094 : 66000030
    move.w 2(a0),d0                                   ; +$0098 : 30280002
    cmpi.w #$2710,d0                                  ; +$009C : 0C402710
    bne.w L_00321A                                    ; +$00A0 : 66000024
    move.w 4(a0),d0                                   ; +$00A4 : 30280004
    cmpi.w #$00FF,d0                                  ; +$00A8 : 0C4000FF
    bne.w L_00321A                                    ; +$00AC : 66000018
    ori.l #$00000002,342(a4)                          ; +$00B0 : 00AC000000020156
    bra.w L_003210                                    ; +$00B8 : 60000002
L_003210:
    move.l #$00000001,d3                              ; +$00BC : 263C00000001
    bra.w L_003220                                    ; +$00C2 : 60000008
L_00321A:
    move.l #$00000000,d3                              ; +$00C6 : 263C00000000
L_003220:
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
    beq.w L_00328A                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_00328A                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_00328A                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_00328A                                    ; +$002E : 6600002E
    move.l 12(a2),d0                                  ; +$0032 : 202A000C
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_00328A                                    ; +$0038 : 67000024
    bmi.w L_00328A                                    ; +$003C : 6B000020
    move.w 14(a1),d3                                  ; +$0040 : 3629000E
    ext.l d3                                          ; +$0044 : 48C3
    move.w 4(a1),d1                                   ; +$0046 : 32290004
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_00328A                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_00328A                                    ; +$0056 : 64000006
    bra.w L_003290                                    ; +$005A : 60000008
L_00328A:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_003290:
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
    beq.w L_0032FA                                    ; +$000C : 67000050
    movea.l (a2),a4                                   ; +$0010 : 2852
    move.l a4,d0                                      ; +$0012 : 200C
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0032FA                                    ; +$0016 : 67000046
    movea.l 36(a2),a1                                 ; +$001A : 226A0024
    move.l a1,d0                                      ; +$001E : 2009
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0032FA                                    ; +$0022 : 6700003A
    move.l 46(a1),d0                                  ; +$0026 : 2029002E
    move.l a4,d1                                      ; +$002A : 220C
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_0032FA                                    ; +$002E : 6600002E
    move.l 16(a2),d0                                  ; +$0032 : 202A0010
    tst.l d0                                          ; +$0036 : 4A80
    beq.w L_0032FA                                    ; +$0038 : 67000024
    bmi.w L_0032FA                                    ; +$003C : 6B000020
    move.w 12(a1),d3                                  ; +$0040 : 3629000C
    ext.l d3                                          ; +$0044 : 48C3
    move.w 6(a1),d1                                   ; +$0046 : 32290006
    ext.l d1                                          ; +$004A : 48C1
    add.l d1,d3                                       ; +$004C : D681
    tst.l d3                                          ; +$004E : 4A83
    bmi.w L_0032FA                                    ; +$0050 : 6B00000C
    cmp.l d0,d3                                       ; +$0054 : B680
    bcc.w L_0032FA                                    ; +$0056 : 64000006
    bra.w L_003300                                    ; +$005A : 60000008
L_0032FA:
    move.l #$FFFFFFFF,d3                              ; +$005E : 263CFFFFFFFF
L_003300:
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
    beq.w L_0033E2                                    ; +$000C : 670000C8
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0033E2                                    ; +$0016 : 670000BE
    movea.l 36(a2),a4                                 ; +$001A : 286A0024
    move.l a4,d0                                      ; +$001E : 200C
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0033E2                                    ; +$0022 : 670000B2
    move.l 46(a4),d0                                  ; +$0026 : 202C002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_0033E2                                    ; +$002E : 660000A6
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
    lea L_0033F0(pc),a0                               ; +$0056 : 41FA008C
    move.l #$00000000,d0                              ; +$005A : 203C00000000
    movea.l a4,a1                                     ; +$0060 : 224C
    move.l #$00000000,d1                              ; +$0062 : 223C00000000
    jsr -444(a6)                                      ; +$0068 : 4EAEFE44
    tst.l d0                                          ; +$006C : 4A80
    bne.w L_0033D4                                    ; +$006E : 66000058
    movea.l 20(a4),a6                                 ; +$0072 : 2C6C0014
    move.l a6,d0                                      ; +$0076 : 200E
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0033C0                                    ; +$007A : 67000038
    jsr -42(a6)                                       ; +$007E : 4EAEFFD6
    andi.w #$7000,d0                                  ; +$0082 : 02407000
    move.l #$00000000,d3                              ; +$0086 : 263C00000000
    move.l d0,d1                                      ; +$008C : 2200
    andi.w #$4000,d1                                  ; +$008E : 02414000
    beq.w L_0033A4                                    ; +$0092 : 67000004
    addq.l #1,d3                                      ; +$0096 : 5283
L_0033A4:
    move.l d0,d1                                      ; +$0098 : 2200
    andi.w #$2000,d1                                  ; +$009A : 02412000
    beq.w L_0033B0                                    ; +$009E : 67000004
    addq.l #2,d3                                      ; +$00A2 : 5483
L_0033B0:
    move.l d0,d1                                      ; +$00A4 : 2200
    andi.w #$1000,d1                                  ; +$00A6 : 02411000
    beq.w L_0033BC                                    ; +$00AA : 67000004
    addq.l #4,d3                                      ; +$00AE : 5883
L_0033BC:
    bra.w L_0033C6                                    ; +$00B0 : 60000008
L_0033C0:
    move.l #$FFFFFFFF,d3                              ; +$00B4 : 263CFFFFFFFF
L_0033C6:
    movea.l $0004.w,a6                                ; +$00BA : 2C780004
    movea.l a4,a1                                     ; +$00BE : 224C
    jsr -450(a6)                                      ; +$00C0 : 4EAEFE3E
    bra.w L_0033DA                                    ; +$00C4 : 60000008
L_0033D4:
    move.l #$FFFFFFFF,d3                              ; +$00C8 : 263CFFFFFFFF
L_0033DA:
    lea 48(a7),a7                                     ; +$00CE : 4FEF0030
    bra.w L_0033E8                                    ; +$00D2 : 60000008
L_0033E2:
    move.l #$FFFFFFFF,d3                              ; +$00D6 : 263CFFFFFFFF
L_0033E8:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$00DC : 4CDF77F7
    moveq #0,d2                                       ; +$00E0 : 7400
    rts                                               ; +$00E2 : 4E75
L_0033F0:
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
    beq.w L_00345E                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_00345E                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_00344A                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 610000A8
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_00345E                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11932(a2),a2                                  ; +$0038 : 45EA2E9C
    move.l 4(a2),d3                                   ; +$003C : 262A0004
    clr.l 4(a2)                                       ; +$0040 : 42AA0004
    bra.w L_003460                                    ; +$0044 : 60000018
L_00344A:
    lea 11932(a2),a2                                  ; +$0048 : 45EA2E9C
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_00345E:
    moveq #-1,d3                                      ; +$005C : 76FF
L_003460:
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
    beq.w L_0034C8                                    ; +$000C : 6700004E
    movea.l 36(a2),a4                                 ; +$0010 : 286A0024
    move.l a4,d0                                      ; +$0014 : 200C
    tst.l d0                                          ; +$0016 : 4A80
    beq.w L_0034C8                                    ; +$0018 : 67000042
    move.l 24(a4),d0                                  ; +$001C : 202C0018
    andi.l #$00002000,d0                              ; +$0020 : 028000002000
    beq.w L_0034B4                                    ; +$0026 : 67000020
    bsr.w Internal_33                                 ; +$002A : 6100003E
    tst.l d0                                          ; +$002E : 4A80
    bne.w L_0034C8                                    ; +$0030 : 6600002A
    movea.l 456(a5),a2                                ; +$0034 : 246D01C8
    lea 11932(a2),a2                                  ; +$0038 : 45EA2E9C
    move.l 8(a2),d3                                   ; +$003C : 262A0008
    clr.l 8(a2)                                       ; +$0040 : 42AA0008
    bra.w L_0034CA                                    ; +$0044 : 60000018
L_0034B4:
    lea 11932(a2),a2                                  ; +$0048 : 45EA2E9C
    clr.l 4(a2)                                       ; +$004C : 42AA0004
    clr.l 8(a2)                                       ; +$0050 : 42AA0008
    clr.l 12(a2)                                      ; +$0054 : 42AA000C
    clr.l 28(a2)                                      ; +$0058 : 42AA001C
L_0034C8:
    moveq #-1,d3                                      ; +$005C : 76FF
L_0034CA:
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
    beq.w L_0036E8                                    ; +$000C : 67000204
    movea.l (a2),a1                                   ; +$0010 : 2252
    move.l a1,d0                                      ; +$0012 : 2009
    tst.l d0                                          ; +$0014 : 4A80
    beq.w L_0036E8                                    ; +$0016 : 670001FA
    movea.l 36(a2),a3                                 ; +$001A : 266A0024
    move.l a3,d0                                      ; +$001E : 200B
    tst.l d0                                          ; +$0020 : 4A80
    beq.w L_0036E8                                    ; +$0022 : 670001EE
    move.l 46(a3),d0                                  ; +$0026 : 202B002E
    move.l a1,d1                                      ; +$002A : 2209
    cmp.l d1,d0                                       ; +$002C : B081
    bne.w L_0036E8                                    ; +$002E : 660001E2
    movea.l 86(a3),a4                                 ; +$0032 : 286B0056
    move.l a4,d0                                      ; +$0036 : 200C
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_0036E8                                    ; +$003A : 670001D6
    lea 11932(a2),a2                                  ; +$003E : 45EA2E9C
    move.l (a2),d0                                    ; +$0042 : 2012
    move.l a3,d1                                      ; +$0044 : 220B
    cmp.l d1,d0                                       ; +$0046 : B081
    beq.w L_00354A                                    ; +$0048 : 6700002A
    move.l a3,(a2)                                    ; +$004C : 248B
    clr.l 4(a2)                                       ; +$004E : 42AA0004
    clr.l 8(a2)                                       ; +$0052 : 42AA0008
    clr.l 12(a2)                                      ; +$0056 : 42AA000C
    clr.l 28(a2)                                      ; +$005A : 42AA001C
    move.l 24(a3),d0                                  ; +$005E : 202B0018
    andi.l #$00002000,d0                              ; +$0062 : 028000002000
    beq.w L_00354A                                    ; +$0068 : 6700000A
    move.l #$00000001,28(a2)                          ; +$006C : 257C00000001001C
L_00354A:
    move.l 24(a3),d0                                  ; +$0074 : 202B0018
    andi.l #$00002000,d0                              ; +$0078 : 028000002000
    bne.w L_003568                                    ; +$007E : 66000012
    clr.l 4(a2)                                       ; +$0082 : 42AA0004
    clr.l 8(a2)                                       ; +$0086 : 42AA0008
    clr.l 12(a2)                                      ; +$008A : 42AA000C
    clr.l 28(a2)                                      ; +$008E : 42AA001C
L_003568:
    moveq #63,d7                                      ; +$0092 : 7E3F
L_00356A:
    move.l 24(a2),d0                                  ; +$0094 : 202A0018
    cmpi.l #$00000010,d0                              ; +$0098 : 0C8000000010
    bcc.w L_0036E2                                    ; +$009E : 6400016C
    movea.l a4,a0                                     ; +$00A2 : 204C
    movea.l $0004.w,a6                                ; +$00A4 : 2C780004
    jsr -372(a6)                                      ; +$00A8 : 4EAEFE8C
    tst.l d0                                          ; +$00AC : 4A80
    beq.w L_0036E2                                    ; +$00AE : 6700015C
    movea.l d0,a3                                     ; +$00B2 : 2640
    move.l 20(a3),d4                                  ; +$00B4 : 282B0014
    moveq #0,d5                                       ; +$00B8 : 7A00
    move.w 24(a3),d5                                  ; +$00BA : 3A2B0018
    moveq #0,d6                                       ; +$00BE : 7C00
    move.w 26(a3),d6                                  ; +$00C0 : 3C2B001A
    cmpi.l #$00000400,d4                              ; +$00C4 : 0C8400000400
    beq.w L_0035C6                                    ; +$00CA : 67000024
    cmpi.l #$00000008,d4                              ; +$00CE : 0C8400000008
    beq.w L_003606                                    ; +$00D4 : 6700005A
    cmpi.l #$00080000,d4                              ; +$00D8 : 0C8400080000
    beq.w L_003698                                    ; +$00DE : 670000E2
    cmpi.l #$00040000,d4                              ; +$00E2 : 0C8400040000
    beq.w L_0036AC                                    ; +$00E8 : 670000EC
    bra.w L_0036D4                                    ; +$00EC : 60000110
L_0035C6:
    move.l d5,d0                                      ; +$00F0 : 2005
    andi.l #$00000080,d0                              ; +$00F2 : 028000000080
    bne.w L_0036D4                                    ; +$00F8 : 66000104
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
    bra.w L_0036D4                                    ; +$012C : 600000D0
L_003606:
    move.l 28(a2),d0                                  ; +$0130 : 202A001C
    tst.l d0                                          ; +$0134 : 4A80
    beq.w L_0036D4                                    ; +$0136 : 670000C6
    move.l d5,d0                                      ; +$013A : 2005
    andi.l #$0000007F,d0                              ; +$013C : 02800000007F
    cmpi.l #$00000068,d0                              ; +$0142 : 0C8000000068
    beq.w L_00363A                                    ; +$0148 : 6700001A
    cmpi.l #$00000069,d0                              ; +$014C : 0C8000000069
    beq.w L_003640                                    ; +$0152 : 67000016
    cmpi.l #$0000006A,d0                              ; +$0156 : 0C800000006A
    beq.w L_003646                                    ; +$015C : 67000012
    bra.w L_0036D4                                    ; +$0160 : 6000009C
L_00363A:
    moveq #1,d1                                       ; +$0164 : 7201
    bra.w L_003648                                    ; +$0166 : 6000000A
L_003640:
    moveq #2,d1                                       ; +$016A : 7202
    bra.w L_003648                                    ; +$016C : 60000004
L_003646:
    moveq #4,d1                                       ; +$0170 : 7204
L_003648:
    move.l d5,d0                                      ; +$0172 : 2005
    andi.l #$00000080,d0                              ; +$0174 : 028000000080
    bne.w L_003676                                    ; +$017A : 66000024
    move.l 12(a2),d0                                  ; +$017E : 202A000C
    move.l d0,d4                                      ; +$0182 : 2800
    and.l d1,d4                                       ; +$0184 : C881
    tst.l d4                                          ; +$0186 : 4A84
    bne.w L_0036D4                                    ; +$0188 : 66000074
    or.l d1,d0                                        ; +$018C : 8081
    move.l d0,12(a2)                                  ; +$018E : 2540000C
    move.l 4(a2),d0                                   ; +$0192 : 202A0004
    or.l d1,d0                                        ; +$0196 : 8081
    move.l d0,4(a2)                                   ; +$0198 : 25400004
    bra.w L_0036D4                                    ; +$019C : 60000060
L_003676:
    move.l 12(a2),d0                                  ; +$01A0 : 202A000C
    move.l d0,d4                                      ; +$01A4 : 2800
    and.l d1,d4                                       ; +$01A6 : C881
    tst.l d4                                          ; +$01A8 : 4A84
    beq.w L_0036D4                                    ; +$01AA : 67000052
    sub.l d1,d0                                       ; +$01AE : 9081
    move.l d0,12(a2)                                  ; +$01B0 : 2540000C
    move.l 8(a2),d0                                   ; +$01B4 : 202A0008
    or.l d1,d0                                        ; +$01B8 : 8081
    move.l d0,8(a2)                                   ; +$01BA : 25400008
    bra.w L_0036D4                                    ; +$01BE : 6000003E
L_003698:
    clr.l 4(a2)                                       ; +$01C2 : 42AA0004
    clr.l 8(a2)                                       ; +$01C6 : 42AA0008
    clr.l 12(a2)                                      ; +$01CA : 42AA000C
    clr.l 28(a2)                                      ; +$01CE : 42AA001C
    bra.w L_0036D4                                    ; +$01D2 : 6000002A
L_0036AC:
    clr.l 4(a2)                                       ; +$01D6 : 42AA0004
    clr.l 8(a2)                                       ; +$01DA : 42AA0008
    clr.l 12(a2)                                      ; +$01DE : 42AA000C
    clr.l 28(a2)                                      ; +$01E2 : 42AA001C
    movea.l (a2),a0                                   ; +$01E6 : 2052
    move.l 24(a0),d0                                  ; +$01E8 : 20280018
    andi.l #$00002000,d0                              ; +$01EC : 028000002000
    beq.w L_0036D4                                    ; +$01F2 : 6700000A
    move.l #$00000001,28(a2)                          ; +$01F6 : 257C00000001001C
L_0036D4:
    movea.l a3,a1                                     ; +$01FE : 224B
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -378(a6)                                      ; +$0204 : 4EAEFE86
    dbra d7,L_00356A                                  ; +$0208 : 51CFFE8A
L_0036E2:
    moveq #0,d0                                       ; +$020C : 7000
    bra.w L_0036EA                                    ; +$020E : 60000004
L_0036E8:
    moveq #-1,d0                                      ; +$0212 : 70FF
L_0036EA:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$0214 : 4CDF7FFE
    rts                                               ; +$0218 : 4E75
L_0036F0:
    bsr.w Internal_33                                 ; +$021A : 6100FDE4
    tst.l d0                                          ; +$021E : 4A80
    bne.w L_003756                                    ; +$0220 : 6600005E
    movem.l d1-d7/a0-a6,-(a7)                         ; +$0224 : 48E77FFE
    movea.l 456(a5),a2                                ; +$0228 : 246D01C8
    lea 11932(a2),a2                                  ; +$022C : 45EA2E9C
    move.l 24(a2),d0                                  ; +$0230 : 202A0018
    tst.l d0                                          ; +$0234 : 4A80
    beq.w L_00374E                                    ; +$0236 : 67000040
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
    bra.w L_003750                                    ; +$0274 : 60000004
L_00374E:
    moveq #0,d0                                       ; +$0278 : 7000
L_003750:
    movem.l (a7)+,d1-d7/a0-a6                         ; +$027A : 4CDF7FFE
    rts                                               ; +$027E : 4E75
L_003756:
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
    bmi.w L_003844                                    ; +$0012 : 6B000042
    tst.l d1                                          ; +$0016 : 4A81
    bmi.w L_003844                                    ; +$0018 : 6B00003C
    tst.l d4                                          ; +$001C : 4A84
    ble.w L_003844                                    ; +$001E : 6F000036
    tst.l d5                                          ; +$0022 : 4A85
    ble.w L_003844                                    ; +$0024 : 6F000030
    cmp.l d2,d0                                       ; +$0028 : B082
    blt.w L_003844                                    ; +$002A : 6D00002A
    sub.l d2,d0                                       ; +$002E : 9082
    bvs.w L_003844                                    ; +$0030 : 69000024
    cmp.l d4,d0                                       ; +$0034 : B084
    bge.w L_003844                                    ; +$0036 : 6C00001E
    cmp.l d3,d1                                       ; +$003A : B283
    blt.w L_003844                                    ; +$003C : 6D000018
    sub.l d3,d1                                       ; +$0040 : 9283
    bvs.w L_003844                                    ; +$0042 : 69000012
    cmp.l d5,d1                                       ; +$0046 : B285
    bge.w L_003844                                    ; +$0048 : 6C00000C
    move.l #$00000001,d3                              ; +$004C : 263C00000001
    bra.w L_00384A                                    ; +$0052 : 60000008
L_003844:
    move.l #$00000000,d3                              ; +$0056 : 263C00000000
L_00384A:
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
    ble.w L_0038D0                                    ; +$0016 : 6F000062
    tst.l d3                                          ; +$001A : 4A83
    ble.w L_0038D0                                    ; +$001C : 6F00005C
    tst.l d6                                          ; +$0020 : 4A86
    ble.w L_0038D0                                    ; +$0022 : 6F000056
    tst.l d7                                          ; +$0026 : 4A87
    ble.w L_0038D0                                    ; +$0028 : 6F000050
    cmp.l d4,d0                                       ; +$002C : B084
    blt.w L_003898                                    ; +$002E : 6D000012
    sub.l d4,d0                                       ; +$0032 : 9084
    bvs.w L_0038D0                                    ; +$0034 : 69000044
    cmp.l d6,d0                                       ; +$0038 : B086
    bge.w L_0038D0                                    ; +$003A : 6C00003E
    bra.w L_0038A4                                    ; +$003E : 6000000E
L_003898:
    sub.l d0,d4                                       ; +$0042 : 9880
    bvs.w L_0038D0                                    ; +$0044 : 69000034
    cmp.l d2,d4                                       ; +$0048 : B882
    bge.w L_0038D0                                    ; +$004A : 6C00002E
L_0038A4:
    cmp.l d5,d1                                       ; +$004E : B285
    blt.w L_0038BA                                    ; +$0050 : 6D000012
    sub.l d5,d1                                       ; +$0054 : 9285
    bvs.w L_0038D0                                    ; +$0056 : 69000022
    cmp.l d7,d1                                       ; +$005A : B287
    bge.w L_0038D0                                    ; +$005C : 6C00001C
    bra.w L_0038C6                                    ; +$0060 : 6000000E
L_0038BA:
    sub.l d1,d5                                       ; +$0064 : 9A81
    bvs.w L_0038D0                                    ; +$0066 : 69000012
    cmp.l d3,d5                                       ; +$006A : BA83
    bge.w L_0038D0                                    ; +$006C : 6C00000C
L_0038C6:
    move.l #$00000001,d3                              ; +$0070 : 263C00000001
    bra.w L_0038D6                                    ; +$0076 : 60000008
L_0038D0:
    move.l #$00000000,d3                              ; +$007A : 263C00000000
L_0038D6:
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
    beq.w L_003B5A                                    ; +$0012 : 67000264
    move.l #$00000000,d4                              ; +$0016 : 283C00000000
    move.w (a4),d4                                    ; +$001C : 3814
    tst.l d4                                          ; +$001E : 4A84
    beq.w L_003B5A                                    ; +$0020 : 67000256
    cmpi.l #$00000080,d4                              ; +$0024 : 0C8400000080
    bgt.w L_003B5A                                    ; +$002A : 6E00024C
    addq.l #2,a4                                      ; +$002E : 548C
    tst.l d5                                          ; +$0030 : 4A85
    bmi.w L_003B5A                                    ; +$0032 : 6B000244
    tst.l d6                                          ; +$0036 : 4A86
    bmi.w L_003B5A                                    ; +$0038 : 6B00023E
    tst.l d7                                          ; +$003C : 4A87
    bmi.w L_003B5A                                    ; +$003E : 6B000238
    movea.l 456(a5),a2                                ; +$0042 : 246D01C8
    move.l a2,d0                                      ; +$0046 : 200A
    tst.l d0                                          ; +$0048 : 4A80
    beq.w L_003B5A                                    ; +$004A : 6700022C
    move.l (a2),d0                                    ; +$004E : 2012
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_003B5A                                    ; +$0052 : 67000224
    move.l 8(a2),d0                                   ; +$0056 : 202A0008
    tst.l d0                                          ; +$005A : 4A80
    beq.w L_003B5A                                    ; +$005C : 6700021A
    move.l 32(a2),d0                                  ; +$0060 : 202A0020
    tst.l d0                                          ; +$0064 : 4A80
    beq.w L_003B5A                                    ; +$0066 : 67000210
    move.l 12(a2),d0                                  ; +$006A : 202A000C
    tst.l d0                                          ; +$006E : 4A80
    ble.w L_003B5A                                    ; +$0070 : 6F000206
    cmpi.l #$00007FFF,d0                              ; +$0074 : 0C8000007FFF
    bgt.w L_003B5A                                    ; +$007A : 6E0001FC
    cmp.l d0,d5                                       ; +$007E : BA80
    bge.w L_003B5A                                    ; +$0080 : 6C0001F6
    move.l 16(a2),d0                                  ; +$0084 : 202A0010
    tst.l d0                                          ; +$0088 : 4A80
    ble.w L_003B5A                                    ; +$008A : 6F0001EC
    cmpi.l #$00007FFF,d0                              ; +$008E : 0C8000007FFF
    bgt.w L_003B5A                                    ; +$0094 : 6E0001E2
    cmp.l d0,d6                                       ; +$0098 : BC80
    bge.w L_003B5A                                    ; +$009A : 6C0001DC
    move.l 28(a2),d0                                  ; +$009E : 202A001C
    tst.l d0                                          ; +$00A2 : 4A80
    ble.w L_003B5A                                    ; +$00A4 : 6F0001D2
    cmpi.l #$00000008,d0                              ; +$00A8 : 0C8000000008
    bgt.w L_003B5A                                    ; +$00AE : 6E0001C8
    move.l #$00000001,d1                              ; +$00B2 : 223C00000001
L_00399A:
    lsl.l #1,d1                                       ; +$00B8 : E389
    subq.l #1,d0                                      ; +$00BA : 5380
    bne.w L_00399A                                    ; +$00BC : 6600FFFA
    cmp.l d1,d7                                       ; +$00C0 : BE81
    bcc.w L_003B5A                                    ; +$00C2 : 640001B4
    movea.l 32(a2),a2                                 ; +$00C6 : 246A0020
    move.l 8(a2),d0                                   ; +$00CA : 202A0008
    tst.l d0                                          ; +$00CE : 4A80
    beq.w L_0039C6                                    ; +$00D0 : 67000012
    cmpi.l #$00000001,d0                              ; +$00D4 : 0C8000000001
    bne.w L_003B5A                                    ; +$00DA : 6600019C
    movea.l (a2),a0                                   ; +$00DE : 2052
    bra.w L_0039CA                                    ; +$00E0 : 60000006
L_0039C6:
    movea.l 4(a2),a0                                  ; +$00E4 : 206A0004
L_0039CA:
    move.l a0,d0                                      ; +$00E8 : 2008
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_003B5A                                    ; +$00EC : 6700018A
    movea.l (a0),a0                                   ; +$00F0 : 2050
    move.l a0,d0                                      ; +$00F2 : 2008
    tst.l d0                                          ; +$00F4 : 4A80
    beq.w L_003B5A                                    ; +$00F6 : 67000180
    move.l a0,d2                                      ; +$00FA : 2408
    movea.l 456(a5),a1                                ; +$00FC : 226D01C8
    move.l #$00000000,d1                              ; +$0100 : 223C00000000
    move.w (a0),d1                                    ; +$0106 : 3210
    lsl.l #3,d1                                       ; +$0108 : E789
    cmp.l 12(a1),d1                                   ; +$010A : B2A9000C
    blt.w L_003B5A                                    ; +$010E : 6D000168
    move.l #$00000000,d1                              ; +$0112 : 223C00000000
    move.w 2(a0),d1                                   ; +$0118 : 32280002
    cmp.l 16(a1),d1                                   ; +$011C : B2A90010
    blt.w L_003B5A                                    ; +$0120 : 6D000156
    move.l #$00000000,d1                              ; +$0124 : 223C00000000
    move.b 5(a0),d1                                   ; +$012A : 12280005
    cmp.l 28(a1),d1                                   ; +$012E : B2A9001C
    bne.w L_003B5A                                    ; +$0132 : 66000144
    move.l d1,d0                                      ; +$0136 : 2001
    movea.l a0,a1                                     ; +$0138 : 2248
    addq.l #8,a1                                      ; +$013A : 5089
L_003A1E:
    move.l (a1)+,d1                                   ; +$013C : 2219
    tst.l d1                                          ; +$013E : 4A81
    beq.w L_003B5A                                    ; +$0140 : 67000136
    cmpi.l #$FFFFFFFF,d1                              ; +$0144 : 0C81FFFFFFFF
    beq.w L_003B5A                                    ; +$014A : 6700012C
    subq.l #1,d0                                      ; +$014E : 5380
    bne.w L_003A1E                                    ; +$0150 : 6600FFEA
    lea -160(a7),a7                                   ; +$0154 : 4FEFFF60
    movea.l a7,a2                                     ; +$0158 : 244F
    movea.l a2,a1                                     ; +$015A : 224A
    movea.l 456(a5),a0                                ; +$015C : 206D01C8
    movea.l 8(a0),a6                                  ; +$0160 : 2C680008
    jsr -198(a6)                                      ; +$0164 : 4EAEFF3A
    move.l d2,4(a2)                                   ; +$0168 : 25420004
    movea.l 456(a5),a0                                ; +$016C : 206D01C8
    movea.l (a0),a0                                   ; +$0170 : 2050
    bsr.w L_005920                                    ; +$0172 : 61001ECA
    tst.l d0                                          ; +$0176 : 4A80
    beq.w L_003A66                                    ; +$0178 : 6700000A
    movea.l d0,a0                                     ; +$017C : 2040
    movea.l a7,a1                                     ; +$017E : 224F
    jsr -66(a6)                                       ; +$0180 : 4EAEFFBE
L_003A66:
    move.l 52(a2),d0                                  ; +$0184 : 202A0034
    tst.l d0                                          ; +$0188 : 4A80
    beq.w L_003B56                                    ; +$018A : 670000E8
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
    bmi.w L_003B56                                    ; +$01A8 : 6B0000CA
    move.w 6(a2),d0                                   ; +$01AC : 302A0006
    ext.l d0                                          ; +$01B0 : 48C0
    add.l d6,d0                                       ; +$01B2 : D086
    tst.l d0                                          ; +$01B4 : 4A80
    bmi.w L_003B56                                    ; +$01B6 : 6B0000BC
    move.w 8(a2),d0                                   ; +$01BA : 302A0008
    ext.l d0                                          ; +$01BE : 48C0
    add.l d5,d0                                       ; +$01C0 : D085
    movea.l 456(a5),a1                                ; +$01C2 : 226D01C8
    cmp.l 12(a1),d0                                   ; +$01C6 : B0A9000C
    bge.w L_003B56                                    ; +$01CA : 6C0000A8
    move.w 10(a2),d0                                  ; +$01CE : 302A000A
    ext.l d0                                          ; +$01D2 : 48C0
    add.l d6,d0                                       ; +$01D4 : D086
    movea.l 456(a5),a1                                ; +$01D6 : 226D01C8
    cmp.l 16(a1),d0                                   ; +$01DA : B0A90010
    bge.w L_003B56                                    ; +$01DE : 6C000094
    move.w (a2),d0                                    ; +$01E2 : 3012
    tst.w d0                                          ; +$01E4 : 4A40
    beq.w L_003B56                                    ; +$01E6 : 6700008C
    move.w 2(a2),d0                                   ; +$01EA : 302A0002
    tst.w d0                                          ; +$01EE : 4A40
    beq.w L_003B56                                    ; +$01F0 : 67000082
    movea.l 456(a5),a0                                ; +$01F4 : 206D01C8
    movea.l 32(a0),a0                                 ; +$01F8 : 20680020
    move.l 20(a0),d0                                  ; +$01FC : 20280014
    andi.l #$00000001,d0                              ; +$0200 : 028000000001
    beq.w L_003B24                                    ; +$0206 : 6700003A
    movea.l 12(a0),a0                                 ; +$020A : 2068000C
    move.l a0,d0                                      ; +$020E : 2008
    tst.l d0                                          ; +$0210 : 4A80
    beq.w L_003B56                                    ; +$0212 : 67000060
    movea.l $0004.w,a6                                ; +$0216 : 2C780004
    jsr -372(a6)                                      ; +$021A : 4EAEFE8C
    tst.l d0                                          ; +$021E : 4A80
    beq.w L_003B56                                    ; +$0220 : 67000052
    movea.l 456(a5),a0                                ; +$0224 : 206D01C8
    movea.l 32(a0),a0                                 ; +$0228 : 20680020
    move.l 20(a0),d0                                  ; +$022C : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0230 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$0236 : 21400014
    movea.l 456(a5),a0                                ; +$023A : 206D01C8
    movea.l 8(a0),a6                                  ; +$023E : 2C680008
L_003B24:
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
L_003B56:
    lea 160(a7),a7                                    ; +$0274 : 4FEF00A0
L_003B5A:
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
    bsr.w L_003CCC                                    ; +$0114 : 61000050
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_003CB6                                    ; +$011A : 67000034
    bsr.w L_003DFA                                    ; +$011E : 61000174
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_003CB6                                    ; +$0124 : 6700002A
    bsr.w L_003EB4                                    ; +$0128 : 61000224
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_003CB6                                    ; +$012E : 67000020
    bsr.w L_003F50                                    ; +$0132 : 610002B6
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_003CB6                                    ; +$0138 : 67000016
    bsr.w L_003FCC                                    ; +$013C : 61000328
    tst.l d0                                          ; +$0140 : 4A80
    beq.w L_003CB6                                    ; +$0142 : 6700000C
    move.l #$00000001,d3                              ; +$0146 : 263C00000001
    bra.w L_003CBC                                    ; +$014C : 60000008
L_003CB6:
    move.l #$00000000,d3                              ; +$0150 : 263C00000000
L_003CBC:
    bsr.w L_004006                                    ; +$0156 : 61000348
    lea 128(a7),a7                                    ; +$015A : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$015E : 4CDF7FF7
    moveq #0,d2                                       ; +$0162 : 7400
    rts                                               ; +$0164 : 4E75
L_003CCC:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0166 : 48E77FFA
    movea.l 4(a5),a2                                  ; +$016A : 246D0004
    move.l #$00000000,d4                              ; +$016E : 283C00000000
    move.w (a2)+,d4                                   ; +$0174 : 381A
    tst.l d4                                          ; +$0176 : 4A84
    beq.w L_003DEC                                    ; +$0178 : 6700010C
    move.l d4,d0                                      ; +$017C : 2004
    addq.l #1,d0                                      ; +$017E : 5280
    move.l #$00010001,d1                              ; +$0180 : 223C00010001
    movea.l $0004.w,a6                                ; +$0186 : 2C780004
    jsr -684(a6)                                      ; +$018A : 4EAEFD54
    tst.l d0                                          ; +$018E : 4A80
    beq.w L_003DEC                                    ; +$0190 : 670000F4
    move.l d0,12(a5)                                  ; +$0194 : 2B40000C
    movea.l d0,a1                                     ; +$0198 : 2240
L_003D00:
    move.b (a2)+,(a1)+                                ; +$019A : 12DA
    subq.l #1,d4                                      ; +$019C : 5384
    bne.w L_003D00                                    ; +$019E : 6600FFFA
    lea L_004086(pc),a1                               ; +$01A2 : 43FA037C
    move.l #$00000000,d0                              ; +$01A6 : 203C00000000
    movea.l $0004.w,a6                                ; +$01AC : 2C780004
    jsr -552(a6)                                      ; +$01B0 : 4EAEFDD8
    tst.l d0                                          ; +$01B4 : 4A80
    beq.w L_003DEC                                    ; +$01B6 : 670000CE
    move.l d0,16(a5)                                  ; +$01BA : 2B400010
    movea.l d0,a6                                     ; +$01BE : 2C40
    move.l 12(a5),d1                                  ; +$01C0 : 222D000C
    move.l #$000003ED,d2                              ; +$01C4 : 243C000003ED
    jsr -30(a6)                                       ; +$01CA : 4EAEFFE2
    tst.l d0                                          ; +$01CE : 4A80
    beq.w L_003DEC                                    ; +$01D0 : 670000B4
    move.l d0,20(a5)                                  ; +$01D4 : 2B400014
    move.l d0,d1                                      ; +$01D8 : 2200
    move.l a5,d2                                      ; +$01DA : 240D
    addi.l #$00000068,d2                              ; +$01DC : 068200000068
    move.l #$0000000C,d3                              ; +$01E2 : 263C0000000C
    jsr -42(a6)                                       ; +$01E8 : 4EAEFFD6
    cmpi.l #$0000000C,d0                              ; +$01EC : 0C800000000C
    bne.w L_003DEC                                    ; +$01F2 : 66000092
    cmpi.l #$464F524D,104(a5)                         ; +$01F6 : 0CAD464F524D0068
    bne.w L_003DEC                                    ; +$01FE : 66000086
    cmpi.l #$494C424D,112(a5)                         ; +$0202 : 0CAD494C424D0070
    bne.w L_003DEC                                    ; +$020A : 6600007A
    move.l 108(a5),d4                                 ; +$020E : 282D006C
    cmpi.l #$00000004,d4                              ; +$0212 : 0C8400000004
    bcs.w L_003DEC                                    ; +$0218 : 6500006C
    cmpi.l #$7FFFFFF7,d4                              ; +$021C : 0C847FFFFFF7
    bhi.w L_003DEC                                    ; +$0222 : 62000062
    addq.l #8,d4                                      ; +$0226 : 5084
    move.l d4,28(a5)                                  ; +$0228 : 2B44001C
    move.l d4,d0                                      ; +$022C : 2004
    move.l #$00010001,d1                              ; +$022E : 223C00010001
    movea.l $0004.w,a6                                ; +$0234 : 2C780004
    jsr -684(a6)                                      ; +$0238 : 4EAEFD54
    tst.l d0                                          ; +$023C : 4A80
    beq.w L_003DEC                                    ; +$023E : 67000046
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
    bne.w L_003DEC                                    ; +$0278 : 6600000C
    move.l #$00000001,d0                              ; +$027C : 203C00000001
    bra.w L_003DF2                                    ; +$0282 : 60000008
L_003DEC:
    move.l #$00000000,d0                              ; +$0286 : 203C00000000
L_003DF2:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$028C : 4CDF5FFE
    tst.l d0                                          ; +$0290 : 4A80
    rts                                               ; +$0292 : 4E75
L_003DFA:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$0294 : 48E77FFA
    movea.l 24(a5),a0                                 ; +$0298 : 206D0018
    move.l 28(a5),d7                                  ; +$029C : 2E2D001C
    subi.l #$0000000C,d7                              ; +$02A0 : 04870000000C
    move.l a0,d0                                      ; +$02A6 : 2008
    addi.l #$0000000C,d0                              ; +$02A8 : 06800000000C
    movea.l d0,a0                                     ; +$02AE : 2040
L_003E16:
    tst.l d7                                          ; +$02B0 : 4A87
    beq.w L_003E68                                    ; +$02B2 : 6700004E
    cmpi.l #$00000008,d7                              ; +$02B6 : 0C8700000008
    bcs.w L_003EA6                                    ; +$02BC : 65000082
    move.l (a0)+,d3                                   ; +$02C0 : 2618
    move.l (a0)+,d2                                   ; +$02C2 : 2418
    subq.l #8,d7                                      ; +$02C4 : 5187
    cmp.l d7,d2                                       ; +$02C6 : B487
    bhi.w L_003EA6                                    ; +$02C8 : 62000076
    move.l d2,d1                                      ; +$02CC : 2202
    andi.l #$00000001,d1                              ; +$02CE : 028100000001
    add.l d2,d1                                       ; +$02D4 : D282
    cmp.l d7,d1                                       ; +$02D6 : B287
    bhi.w L_003EA6                                    ; +$02D8 : 62000066
    sub.l d1,d7                                       ; +$02DC : 9E81
    cmpi.l #$434D4150,d3                              ; +$02DE : 0C83434D4150
    bne.w L_003E5E                                    ; +$02E4 : 66000012
    tst.l 36(a5)                                      ; +$02E8 : 4AAD0024
    bne.w L_003EA6                                    ; +$02EC : 66000052
    move.l a0,36(a5)                                  ; +$02F0 : 2B480024
    move.l d2,40(a5)                                  ; +$02F4 : 2B420028
L_003E5E:
    move.l a0,d0                                      ; +$02F8 : 2008
    add.l d1,d0                                       ; +$02FA : D081
    movea.l d0,a0                                     ; +$02FC : 2040
    bra.w L_003E16                                    ; +$02FE : 6000FFB0
L_003E68:
    tst.l 36(a5)                                      ; +$0302 : 4AAD0024
    beq.w L_003EA6                                    ; +$0306 : 67000038
    move.l 40(a5),d0                                  ; +$030A : 202D0028
    tst.l d0                                          ; +$030E : 4A80
    beq.w L_003EA6                                    ; +$0310 : 6700002E
    cmpi.l #$00000300,d0                              ; +$0314 : 0C8000000300
    bhi.w L_003EA6                                    ; +$031A : 62000024
    divu.w #$0003,d0                                  ; +$031E : 80FC0003
    move.l d0,d1                                      ; +$0322 : 2200
    swap d1                                           ; +$0324 : 4841
    tst.w d1                                          ; +$0326 : 4A41
    bne.w L_003EA6                                    ; +$0328 : 66000016
    andi.l #$0000FFFF,d0                              ; +$032C : 02800000FFFF
    move.l d0,40(a5)                                  ; +$0332 : 2B400028
    move.l #$00000001,d0                              ; +$0336 : 203C00000001
    bra.w L_003EAC                                    ; +$033C : 60000008
L_003EA6:
    move.l #$00000000,d0                              ; +$0340 : 203C00000000
L_003EAC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0346 : 4CDF5FFE
    tst.l d0                                          ; +$034A : 4A80
    rts                                               ; +$034C : 4E75
L_003EB4:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$034E : 48E77FFA
    movea.l (a5),a2                                   ; +$0352 : 2455
    move.l a2,d0                                      ; +$0354 : 200A
    tst.l d0                                          ; +$0356 : 4A80
    beq.w L_003F42                                    ; +$0358 : 67000082
    move.l (a2),d0                                    ; +$035C : 2012
    tst.l d0                                          ; +$035E : 4A80
    beq.w L_003F42                                    ; +$0360 : 6700007A
    move.l d0,88(a5)                                  ; +$0364 : 2B400058
    move.l 8(a2),d0                                   ; +$0368 : 202A0008
    tst.l d0                                          ; +$036C : 4A80
    beq.w L_003F42                                    ; +$036E : 6700006C
    move.l 28(a2),d0                                  ; +$0372 : 202A001C
    tst.l d0                                          ; +$0376 : 4A80
    ble.w L_003F42                                    ; +$0378 : 6F000062
    cmpi.l #$00000008,d0                              ; +$037C : 0C8000000008
    bgt.w L_003F42                                    ; +$0382 : 6E000058
    move.l 24(a2),d0                                  ; +$0386 : 202A0018
    andi.l #$00000C80,d0                              ; +$038A : 028000000C80
    bne.w L_003F42                                    ; +$0390 : 6600004A
    movea.l 88(a5),a0                                 ; +$0394 : 206D0058
    movea.l 48(a0),a1                                 ; +$0398 : 22680030
    move.l a1,d0                                      ; +$039C : 2009
    tst.l d0                                          ; +$039E : 4A80
    beq.w L_003F42                                    ; +$03A0 : 6700003A
    move.l #$00000000,d0                              ; +$03A4 : 203C00000000
    move.w 2(a1),d0                                   ; +$03AA : 30290002
    tst.l d0                                          ; +$03AE : 4A80
    beq.w L_003F42                                    ; +$03B0 : 6700002A
    cmpi.l #$00000100,d0                              ; +$03B4 : 0C8000000100
    bhi.w L_003F42                                    ; +$03BA : 62000020
    cmp.l 40(a5),d0                                   ; +$03BE : B0AD0028
    bcs.w L_003F42                                    ; +$03C2 : 65000018
    move.l 20(a2),d0                                  ; +$03C6 : 202A0014
    cmp.l 40(a5),d0                                   ; +$03CA : B0AD0028
    bcs.w L_003F42                                    ; +$03CE : 6500000C
    move.l #$00000001,d0                              ; +$03D2 : 203C00000001
    bra.w L_003F48                                    ; +$03D8 : 60000008
L_003F42:
    move.l #$00000000,d0                              ; +$03DC : 203C00000000
L_003F48:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$03E2 : 4CDF5FFE
    tst.l d0                                          ; +$03E6 : 4A80
    rts                                               ; +$03E8 : 4E75
L_003F50:
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
    beq.w L_003FBE                                    ; +$040C : 6700004A
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
L_003F92:
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
    bne.w L_003F92                                    ; +$0444 : 6600FFE6
    move.l #$00000000,(a1)                            ; +$0448 : 22BC00000000
    move.l #$00000001,d0                              ; +$044E : 203C00000001
    bra.w L_003FC4                                    ; +$0454 : 60000008
L_003FBE:
    move.l #$00000000,d0                              ; +$0458 : 203C00000000
L_003FC4:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$045E : 4CDF5FFE
    tst.l d0                                          ; +$0462 : 4A80
    rts                                               ; +$0464 : 4E75
L_003FCC:
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
    bra.w L_003FFE                                    ; +$048E : 60000008
    move.l #$00000000,d0                              ; +$0492 : 203C00000000
L_003FFE:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0498 : 4CDF5FFE
    tst.l d0                                          ; +$049C : 4A80
    rts                                               ; +$049E : 4E75
L_004006:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$04A0 : 48E77FFA
    tst.l 20(a5)                                      ; +$04A4 : 4AAD0014
    beq.w L_00401E                                    ; +$04A8 : 6700000E
    movea.l 16(a5),a6                                 ; +$04AC : 2C6D0010
    move.l 20(a5),d1                                  ; +$04B0 : 222D0014
    jsr -36(a6)                                       ; +$04B4 : 4EAEFFDC
L_00401E:
    tst.l 96(a5)                                      ; +$04B8 : 4AAD0060
    beq.w L_004032                                    ; +$04BC : 6700000E
    movea.l 96(a5),a1                                 ; +$04C0 : 226D0060
    movea.l $0004.w,a6                                ; +$04C4 : 2C780004
    jsr -690(a6)                                      ; +$04C8 : 4EAEFD4E
L_004032:
    tst.l 24(a5)                                      ; +$04CC : 4AAD0018
    beq.w L_004046                                    ; +$04D0 : 6700000E
    movea.l 24(a5),a1                                 ; +$04D4 : 226D0018
    movea.l $0004.w,a6                                ; +$04D8 : 2C780004
    jsr -690(a6)                                      ; +$04DC : 4EAEFD4E
L_004046:
    tst.l 12(a5)                                      ; +$04E0 : 4AAD000C
    beq.w L_00405A                                    ; +$04E4 : 6700000E
    movea.l 12(a5),a1                                 ; +$04E8 : 226D000C
    movea.l $0004.w,a6                                ; +$04EC : 2C780004
    jsr -690(a6)                                      ; +$04F0 : 4EAEFD4E
L_00405A:
    tst.l 16(a5)                                      ; +$04F4 : 4AAD0010
    beq.w L_00406E                                    ; +$04F8 : 6700000E
    movea.l 16(a5),a1                                 ; +$04FC : 226D0010
    movea.l $0004.w,a6                                ; +$0500 : 2C780004
    jsr -414(a6)                                      ; +$0504 : 4EAEFE62
L_00406E:
    move.l #$00000001,d0                              ; +$0508 : 203C00000001
    bra.w L_00407E                                    ; +$050E : 60000008
    move.l #$00000000,d0                              ; +$0512 : 203C00000000
L_00407E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0518 : 4CDF5FFE
    tst.l d0                                          ; +$051C : 4A80
    rts                                               ; +$051E : 4E75
L_004086:
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
    bhi.w L_0041B8                                    ; +$0018 : 62000108
    cmpi.l #$000000FF,d5                              ; +$001C : 0C85000000FF
    bhi.w L_0041B8                                    ; +$0022 : 620000FE
    cmpi.l #$000000FF,d6                              ; +$0026 : 0C86000000FF
    bhi.w L_0041B8                                    ; +$002C : 620000F4
    cmpi.l #$000000FF,d7                              ; +$0030 : 0C87000000FF
    bhi.w L_0041B8                                    ; +$0036 : 620000EA
    movea.l 456(a5),a2                                ; +$003A : 246D01C8
    move.l a2,d0                                      ; +$003E : 200A
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_0041B8                                    ; +$0042 : 670000DE
    move.l (a2),d0                                    ; +$0046 : 2012
    tst.l d0                                          ; +$0048 : 4A80
    beq.w L_0041B8                                    ; +$004A : 670000D6
    move.l 8(a2),d0                                   ; +$004E : 202A0008
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0041B8                                    ; +$0054 : 670000CC
    move.l 28(a2),d0                                  ; +$0058 : 202A001C
    tst.l d0                                          ; +$005C : 4A80
    ble.w L_0041B8                                    ; +$005E : 6F0000C2
    cmpi.l #$00000008,d0                              ; +$0062 : 0C8000000008
    bgt.w L_0041B8                                    ; +$0068 : 6E0000B8
    move.l 24(a2),d0                                  ; +$006C : 202A0018
    andi.l #$00000C80,d0                              ; +$0070 : 028000000C80
    bne.w L_0041B8                                    ; +$0076 : 660000AA
    movea.l (a2),a0                                   ; +$007A : 2052
    movea.l 48(a0),a1                                 ; +$007C : 22680030
    move.l a1,d0                                      ; +$0080 : 2009
    tst.l d0                                          ; +$0082 : 4A80
    beq.w L_0041B8                                    ; +$0084 : 6700009C
    move.l #$00000000,d0                              ; +$0088 : 203C00000000
    move.w 2(a1),d0                                   ; +$008E : 30290002
    tst.l d0                                          ; +$0092 : 4A80
    beq.w L_0041B8                                    ; +$0094 : 6700008C
    cmpi.l #$00000100,d0                              ; +$0098 : 0C8000000100
    bhi.w L_0041B8                                    ; +$009E : 62000082
    tst.l d4                                          ; +$00A2 : 4A84
    bmi.w L_0041B8                                    ; +$00A4 : 6B00007C
    cmp.l d0,d4                                       ; +$00A8 : B880
    bcc.w L_0041B8                                    ; +$00AA : 64000076
    cmp.l 20(a2),d4                                   ; +$00AE : B8AA0014
    bcc.w L_0041B8                                    ; +$00B2 : 6400006E
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
L_0041B8:
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
    bhi.w L_0042AC                                    ; +$0012 : 620000D4
    movea.l 456(a5),a2                                ; +$0016 : 246D01C8
    move.l a2,d0                                      ; +$001A : 200A
    tst.l d0                                          ; +$001C : 4A80
    beq.w L_0042AC                                    ; +$001E : 670000C8
    move.l (a2),d0                                    ; +$0022 : 2012
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0042AC                                    ; +$0026 : 670000C0
    move.l 8(a2),d0                                   ; +$002A : 202A0008
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0042AC                                    ; +$0030 : 670000B6
    move.l 28(a2),d0                                  ; +$0034 : 202A001C
    tst.l d0                                          ; +$0038 : 4A80
    ble.w L_0042AC                                    ; +$003A : 6F0000AC
    cmpi.l #$00000008,d0                              ; +$003E : 0C8000000008
    bgt.w L_0042AC                                    ; +$0044 : 6E0000A2
    move.l 24(a2),d0                                  ; +$0048 : 202A0018
    andi.l #$00000C80,d0                              ; +$004C : 028000000C80
    bne.w L_0042AC                                    ; +$0052 : 66000094
    movea.l (a2),a0                                   ; +$0056 : 2052
    movea.l 48(a0),a1                                 ; +$0058 : 22680030
    move.l a1,d0                                      ; +$005C : 2009
    tst.l d0                                          ; +$005E : 4A80
    beq.w L_0042AC                                    ; +$0060 : 67000086
    move.l #$00000000,d0                              ; +$0064 : 203C00000000
    move.w 2(a1),d0                                   ; +$006A : 30290002
    tst.l d0                                          ; +$006E : 4A80
    beq.w L_0042AC                                    ; +$0070 : 67000076
    cmpi.l #$00000100,d0                              ; +$0074 : 0C8000000100
    bhi.w L_0042AC                                    ; +$007A : 6200006C
    tst.l d4                                          ; +$007E : 4A84
    bmi.w L_0042AC                                    ; +$0080 : 6B000066
    cmp.l d0,d4                                       ; +$0084 : B880
    bcc.w L_0042AC                                    ; +$0086 : 64000060
    cmp.l 20(a2),d4                                   ; +$008A : B8AA0014
    bcc.w L_0042AC                                    ; +$008E : 64000058
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
L_0042AC:
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
    bsr.w L_004414                                    ; +$0114 : 61000046
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_0043FE                                    ; +$011A : 6700002A
    bsr.w L_0044F2                                    ; +$011E : 6100011A
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_0043FE                                    ; +$0124 : 67000020
    bsr.w L_004558                                    ; +$0128 : 61000176
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_0043FE                                    ; +$012E : 67000016
    bsr.w L_004666                                    ; +$0132 : 6100027A
    tst.l d0                                          ; +$0136 : 4A80
    beq.w L_0043FE                                    ; +$0138 : 6700000C
    move.l #$00000001,d3                              ; +$013C : 263C00000001
    bra.w L_004404                                    ; +$0142 : 60000008
L_0043FE:
    move.l #$00000000,d3                              ; +$0146 : 263C00000000
L_004404:
    bsr.w L_0046F4                                    ; +$014C : 610002EE
    lea 128(a7),a7                                    ; +$0150 : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$0154 : 4CDF7FF7
    moveq #0,d2                                       ; +$0158 : 7400
    rts                                               ; +$015A : 4E75
L_004414:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$015C : 48E77FFA
    movea.l (a5),a2                                   ; +$0160 : 2455
    move.l a2,d0                                      ; +$0162 : 200A
    tst.l d0                                          ; +$0164 : 4A80
    beq.w L_0044E4                                    ; +$0166 : 670000C4
    move.l (a2),d0                                    ; +$016A : 2012
    tst.l d0                                          ; +$016C : 4A80
    beq.w L_0044E4                                    ; +$016E : 670000BC
    move.l d0,20(a5)                                  ; +$0172 : 2B400014
    tst.l 8(a2)                                       ; +$0176 : 4AAA0008
    beq.w L_0044E4                                    ; +$017A : 670000B0
    move.l 28(a2),d0                                  ; +$017E : 202A001C
    tst.l d0                                          ; +$0182 : 4A80
    beq.w L_0044E4                                    ; +$0184 : 670000A6
    cmpi.l #$00000008,d0                              ; +$0188 : 0C8000000008
    bhi.w L_0044E4                                    ; +$018E : 6200009C
    move.l d0,40(a5)                                  ; +$0192 : 2B400028
    move.l 24(a2),d0                                  ; +$0196 : 202A0018
    andi.l #$00000C80,d0                              ; +$019A : 028000000C80
    bne.w L_0044E4                                    ; +$01A0 : 6600008A
    move.l 12(a2),d0                                  ; +$01A4 : 202A000C
    tst.l d0                                          ; +$01A8 : 4A80
    ble.w L_0044E4                                    ; +$01AA : 6F000080
    cmpi.l #$00007FFF,d0                              ; +$01AE : 0C8000007FFF
    bhi.w L_0044E4                                    ; +$01B4 : 62000076
    move.l d0,32(a5)                                  ; +$01B8 : 2B400020
    move.l 16(a2),d0                                  ; +$01BC : 202A0010
    tst.l d0                                          ; +$01C0 : 4A80
    ble.w L_0044E4                                    ; +$01C2 : 6F000068
    cmpi.l #$00007FFF,d0                              ; +$01C6 : 0C8000007FFF
    bhi.w L_0044E4                                    ; +$01CC : 6200005E
    move.l d0,36(a5)                                  ; +$01D0 : 2B400024
    move.l 20(a2),d4                                  ; +$01D4 : 282A0014
    tst.l d4                                          ; +$01D8 : 4A84
    ble.w L_0044E4                                    ; +$01DA : 6F000050
    cmpi.l #$00000100,d4                              ; +$01DE : 0C8400000100
    bhi.w L_0044E4                                    ; +$01E4 : 62000046
    movea.l 20(a5),a0                                 ; +$01E8 : 206D0014
    movea.l 48(a0),a1                                 ; +$01EC : 22680030
    move.l a1,d0                                      ; +$01F0 : 2009
    tst.l d0                                          ; +$01F2 : 4A80
    beq.w L_0044E4                                    ; +$01F4 : 67000036
    move.l d0,24(a5)                                  ; +$01F8 : 2B400018
    move.l #$00000000,d0                              ; +$01FC : 203C00000000
    move.w 2(a1),d0                                   ; +$0202 : 30290002
    tst.l d0                                          ; +$0206 : 4A80
    beq.w L_0044E4                                    ; +$0208 : 67000022
    cmpi.l #$00000100,d0                              ; +$020C : 0C8000000100
    bhi.w L_0044E4                                    ; +$0212 : 62000018
    cmp.l d0,d4                                       ; +$0216 : B880
    bls.w L_0044D6                                    ; +$0218 : 63000004
    move.l d0,d4                                      ; +$021C : 2800
L_0044D6:
    move.l d4,28(a5)                                  ; +$021E : 2B44001C
    move.l #$00000001,d0                              ; +$0222 : 203C00000001
    bra.w L_0044EA                                    ; +$0228 : 60000008
L_0044E4:
    move.l #$00000000,d0                              ; +$022C : 203C00000000
L_0044EA:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0232 : 4CDF5FFE
    tst.l d0                                          ; +$0236 : 4A80
    rts                                               ; +$0238 : 4E75
L_0044F2:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$023A : 48E77FFA
    movea.l 4(a5),a2                                  ; +$023E : 246D0004
    move.l a2,d0                                      ; +$0242 : 200A
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_00454A                                    ; +$0246 : 6700004A
    move.l #$00000000,d4                              ; +$024A : 283C00000000
    move.w (a2)+,d4                                   ; +$0250 : 381A
    tst.l d4                                          ; +$0252 : 4A84
    beq.w L_00454A                                    ; +$0254 : 6700003C
    cmpi.l #$000000FF,d4                              ; +$0258 : 0C84000000FF
    bhi.w L_00454A                                    ; +$025E : 62000032
    move.l d4,d0                                      ; +$0262 : 2004
    addq.l #1,d0                                      ; +$0264 : 5280
    move.l #$00010001,d1                              ; +$0266 : 223C00010001
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -684(a6)                                      ; +$0270 : 4EAEFD54
    tst.l d0                                          ; +$0274 : 4A80
    beq.w L_00454A                                    ; +$0276 : 6700001A
    move.l d0,8(a5)                                   ; +$027A : 2B400008
    movea.l d0,a1                                     ; +$027E : 2240
L_004538:
    move.b (a2)+,(a1)+                                ; +$0280 : 12DA
    subq.l #1,d4                                      ; +$0282 : 5384
    bne.w L_004538                                    ; +$0284 : 6600FFFA
    move.l #$00000001,d0                              ; +$0288 : 203C00000001
    bra.w L_004550                                    ; +$028E : 60000008
L_00454A:
    move.l #$00000000,d0                              ; +$0292 : 203C00000000
L_004550:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0298 : 4CDF5FFE
    tst.l d0                                          ; +$029C : 4A80
    rts                                               ; +$029E : 4E75
L_004558:
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
    beq.w L_004658                                    ; +$02DE : 670000C0
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
L_00463C:
    move.b (a0),(a1)+                                 ; +$0384 : 12D0
    addq.l #4,a0                                      ; +$0386 : 5888
    move.b (a0),(a1)+                                 ; +$0388 : 12D0
    addq.l #4,a0                                      ; +$038A : 5888
    move.b (a0),(a1)+                                 ; +$038C : 12D0
    addq.l #4,a0                                      ; +$038E : 5888
    subq.l #1,d4                                      ; +$0390 : 5384
    bne.w L_00463C                                    ; +$0392 : 6600FFF0
    move.l #$00000001,d0                              ; +$0396 : 203C00000001
    bra.w L_00465E                                    ; +$039C : 60000008
L_004658:
    move.l #$00000000,d0                              ; +$03A0 : 203C00000000
L_00465E:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$03A6 : 4CDF5FFE
    tst.l d0                                          ; +$03AA : 4A80
    rts                                               ; +$03AC : 4E75
L_004666:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$03AE : 48E77FFA
    lea L_00477C(pc),a1                               ; +$03B2 : 43FA0110
    movea.l $0004.w,a6                                ; +$03B6 : 2C780004
    jsr -552(a6)                                      ; +$03BA : 4EAEFDD8
    tst.l d0                                          ; +$03BE : 4A80
    beq.w L_0046E6                                    ; +$03C0 : 6700006C
    move.l d0,12(a5)                                  ; +$03C4 : 2B40000C
    movea.l d0,a6                                     ; +$03C8 : 2C40
    move.l 8(a5),d1                                   ; +$03CA : 222D0008
    move.l #$000003EE,d2                              ; +$03CE : 243C000003EE
    jsr -30(a6)                                       ; +$03D4 : 4EAEFFE2
    tst.l d0                                          ; +$03D8 : 4A80
    beq.w L_0046E6                                    ; +$03DA : 67000052
    move.l d0,16(a5)                                  ; +$03DE : 2B400010
    move.l #$00000001,60(a5)                          ; +$03E2 : 2B7C00000001003C
    move.l d0,d1                                      ; +$03EA : 2200
    move.l 52(a5),d2                                  ; +$03EC : 242D0034
    move.l 48(a5),d3                                  ; +$03F0 : 262D0030
    jsr -48(a6)                                       ; +$03F4 : 4EAEFFD0
    cmp.l 48(a5),d0                                   ; +$03F8 : B0AD0030
    bne.w L_0046E6                                    ; +$03FC : 66000030
    move.l 16(a5),d1                                  ; +$0400 : 222D0010
    movea.l 12(a5),a6                                 ; +$0404 : 2C6D000C
    jsr -36(a6)                                       ; +$0408 : 4EAEFFDC
    move.l d0,d4                                      ; +$040C : 2800
    move.l #$00000000,16(a5)                          ; +$040E : 2B7C000000000010
    tst.l d4                                          ; +$0416 : 4A84
    beq.w L_0046E6                                    ; +$0418 : 67000014
    move.l #$00000001,64(a5)                          ; +$041C : 2B7C000000010040
    move.l #$00000001,d0                              ; +$0424 : 203C00000001
    bra.w L_0046EC                                    ; +$042A : 60000008
L_0046E6:
    move.l #$00000000,d0                              ; +$042E : 203C00000000
L_0046EC:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$0434 : 4CDF5FFE
    tst.l d0                                          ; +$0438 : 4A80
    rts                                               ; +$043A : 4E75
L_0046F4:
    movem.l d1-d7/a0-a4/a6,-(a7)                      ; +$043C : 48E77FFA
    tst.l 16(a5)                                      ; +$0440 : 4AAD0010
    beq.w L_00470C                                    ; +$0444 : 6700000E
    movea.l 12(a5),a6                                 ; +$0448 : 2C6D000C
    move.l 16(a5),d1                                  ; +$044C : 222D0010
    jsr -36(a6)                                       ; +$0450 : 4EAEFFDC
L_00470C:
    tst.l 60(a5)                                      ; +$0454 : 4AAD003C
    beq.w L_004728                                    ; +$0458 : 67000016
    tst.l 64(a5)                                      ; +$045C : 4AAD0040
    bne.w L_004728                                    ; +$0460 : 6600000E
    movea.l 12(a5),a6                                 ; +$0464 : 2C6D000C
    move.l 8(a5),d1                                   ; +$0468 : 222D0008
    jsr -72(a6)                                       ; +$046C : 4EAEFFB8
L_004728:
    tst.l 52(a5)                                      ; +$0470 : 4AAD0034
    beq.w L_00473C                                    ; +$0474 : 6700000E
    movea.l 52(a5),a1                                 ; +$0478 : 226D0034
    movea.l $0004.w,a6                                ; +$047C : 2C780004
    jsr -690(a6)                                      ; +$0480 : 4EAEFD4E
L_00473C:
    tst.l 8(a5)                                       ; +$0484 : 4AAD0008
    beq.w L_004750                                    ; +$0488 : 6700000E
    movea.l 8(a5),a1                                  ; +$048C : 226D0008
    movea.l $0004.w,a6                                ; +$0490 : 2C780004
    jsr -690(a6)                                      ; +$0494 : 4EAEFD4E
L_004750:
    tst.l 12(a5)                                      ; +$0498 : 4AAD000C
    beq.w L_004764                                    ; +$049C : 6700000E
    movea.l 12(a5),a1                                 ; +$04A0 : 226D000C
    movea.l $0004.w,a6                                ; +$04A4 : 2C780004
    jsr -414(a6)                                      ; +$04A8 : 4EAEFE62
L_004764:
    move.l #$00000001,d0                              ; +$04AC : 203C00000001
    bra.w L_004774                                    ; +$04B2 : 60000008
    move.l #$00000000,d0                              ; +$04B6 : 203C00000000
L_004774:
    movem.l (a7)+,d1-d7/a0-a4/a6                      ; +$04BC : 4CDF5FFE
    tst.l d0                                          ; +$04C0 : 4A80
    rts                                               ; +$04C2 : 4E75
L_00477C:
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
    beq.w L_0048BC                                    ; +$0010 : 6700011E
    cmpi.l #$00000100,d5                              ; +$0014 : 0C8500000100
    bhi.w L_0048BC                                    ; +$001A : 62000114
    move.l d4,d0                                      ; +$001E : 2004
    cmpi.l #$00000018,d0                              ; +$0020 : 0C8000000018
    bls.w L_0048BC                                    ; +$0026 : 63000108
    andi.l #$00000001,d0                              ; +$002A : 028000000001
    bne.w L_0048BC                                    ; +$0030 : 660000FE
    move.l d5,d6                                      ; +$0034 : 2C05
    mulu.w #$0308,d6                                  ; +$0036 : CCFC0308
    addi.l #$00000010,d6                              ; +$003A : 068600000010
    move.l d4,d0                                      ; +$0040 : 2004
    subi.l #$00000018,d0                              ; +$0042 : 048000000018
    movea.l d0,a1                                     ; +$0048 : 2240
    movea.l $0004.w,a6                                ; +$004A : 2C780004
    jsr -534(a6)                                      ; +$004E : 4EAEFDEA
    tst.l d0                                          ; +$0052 : 4A80
    beq.w L_0048BC                                    ; +$0054 : 670000DA
    move.l d4,d0                                      ; +$0058 : 2004
    add.l d6,d0                                       ; +$005A : D086
    bcs.w L_0048BC                                    ; +$005C : 650000D2
    subq.l #1,d0                                      ; +$0060 : 5380
    movea.l d0,a1                                     ; +$0062 : 2240
    jsr -534(a6)                                      ; +$0064 : 4EAEFDEA
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_0048BC                                    ; +$006A : 670000C4
    movea.l d4,a0                                     ; +$006E : 2044
    move.l -20(a0),d0                                 ; +$0070 : 2028FFEC
    move.l d6,d7                                      ; +$0074 : 2E06
    addi.l #$00000010,d7                              ; +$0076 : 068700000010
    cmp.l d7,d0                                       ; +$007C : B087
    bne.w L_0048BC                                    ; +$007E : 660000B0
    move.l #$00000000,d0                              ; +$0082 : 203C00000000
    move.w -12(a0),d0                                 ; +$0088 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$008C : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$0090 : 0C8000000001
    bne.w L_0048BC                                    ; +$0096 : 66000098
    move.l -16(a0),d0                                 ; +$009A : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$009E : 0C8000000005
    bcs.w L_0048BC                                    ; +$00A4 : 6500008A
    cmpi.l #$0000FFFF,d0                              ; +$00A8 : 0C800000FFFF
    bhi.w L_0048BC                                    ; +$00AE : 62000080
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
L_004886:
    move.l d7,(a1)+                                   ; +$00FA : 22C7
    move.w #$0000,(a1)+                               ; +$00FC : 32FC0000
    move.w #$0000,(a1)+                               ; +$0100 : 32FC0000
    addi.l #$00000300,d7                              ; +$0104 : 068700000300
    subq.l #1,d5                                      ; +$010A : 5385
    bne.w L_004886                                    ; +$010C : 6600FFEC
    move.l #$00000000,d5                              ; +$0110 : 2A3C00000000
    move.w 8(a0),d5                                   ; +$0116 : 3A280008
    mulu.w #$00C0,d5                                  ; +$011A : CAFC00C0
L_0048AA:
    move.l #$00000000,(a1)+                           ; +$011E : 22FC00000000
    subq.l #1,d5                                      ; +$0124 : 5385
    bne.w L_0048AA                                    ; +$0126 : 6600FFF6
    move.l #$00000001,d3                              ; +$012A : 263C00000001
L_0048BC:
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
    bhi.w L_004B50                                    ; +$0014 : 62000272
    move.l d4,d0                                      ; +$0018 : 2004
    cmpi.l #$00000018,d0                              ; +$001A : 0C8000000018
    bls.w L_004B50                                    ; +$0020 : 63000266
    andi.l #$00000001,d0                              ; +$0024 : 028000000001
    bne.w L_004B50                                    ; +$002A : 6600025C
    move.l d4,d0                                      ; +$002E : 2004
    subi.l #$00000018,d0                              ; +$0030 : 048000000018
    movea.l d0,a1                                     ; +$0036 : 2240
    movea.l $0004.w,a6                                ; +$0038 : 2C780004
    jsr -534(a6)                                      ; +$003C : 4EAEFDEA
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_004B50                                    ; +$0042 : 67000244
    movea.l d4,a0                                     ; +$0046 : 2044
    move.l #$00000000,d6                              ; +$0048 : 2C3C00000000
    move.w 8(a0),d6                                   ; +$004E : 3C280008
    tst.l d6                                          ; +$0052 : 4A86
    beq.w L_004B50                                    ; +$0054 : 67000232
    cmpi.l #$00000100,d6                              ; +$0058 : 0C8600000100
    bhi.w L_004B50                                    ; +$005E : 62000228
    cmp.l d6,d5                                       ; +$0062 : BA86
    bcc.w L_004B50                                    ; +$0064 : 64000222
    move.l d6,d7                                      ; +$0068 : 2E06
    mulu.w #$0308,d7                                  ; +$006A : CEFC0308
    addi.l #$00000010,d7                              ; +$006E : 068700000010
    move.l d4,d0                                      ; +$0074 : 2004
    add.l d7,d0                                       ; +$0076 : D087
    bcs.w L_004B50                                    ; +$0078 : 6500020E
    subq.l #1,d0                                      ; +$007C : 5380
    movea.l d0,a1                                     ; +$007E : 2240
    jsr -534(a6)                                      ; +$0080 : 4EAEFDEA
    tst.l d0                                          ; +$0084 : 4A80
    beq.w L_004B50                                    ; +$0086 : 67000200
    movea.l d4,a0                                     ; +$008A : 2044
    move.l -20(a0),d0                                 ; +$008C : 2028FFEC
    move.l d7,d1                                      ; +$0090 : 2207
    addi.l #$00000010,d1                              ; +$0092 : 068100000010
    cmp.l d1,d0                                       ; +$0098 : B081
    bne.w L_004B50                                    ; +$009A : 660001EC
    move.l #$00000000,d0                              ; +$009E : 203C00000000
    move.w -12(a0),d0                                 ; +$00A4 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00A8 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00AC : 0C8000000001
    bne.w L_004B50                                    ; +$00B2 : 660001D4
    move.l -16(a0),d0                                 ; +$00B6 : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00BA : 0C8000000005
    bcs.w L_004B50                                    ; +$00C0 : 650001C6
    cmpi.l #$0000FFFF,d0                              ; +$00C4 : 0C800000FFFF
    bhi.w L_004B50                                    ; +$00CA : 620001BC
    move.l -8(a0),d0                                  ; +$00CE : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00D2 : 0C8041474150
    bne.w L_004B50                                    ; +$00D8 : 660001AE
    move.l -4(a0),d0                                  ; +$00DC : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00E0 : 0C80414C2020
    bne.w L_004B50                                    ; +$00E6 : 660001A0
    move.l (a0),d0                                    ; +$00EA : 2010
    cmpi.l #$41474150,d0                              ; +$00EC : 0C8041474150
    bne.w L_004B50                                    ; +$00F2 : 66000194
    move.l #$00000000,d0                              ; +$00F6 : 203C00000000
    move.w 4(a0),d0                                   ; +$00FC : 30280004
    cmpi.l #$0000414C,d0                              ; +$0100 : 0C800000414C
    bne.w L_004B50                                    ; +$0106 : 66000180
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 6(a0),d0                                   ; +$0110 : 30280006
    cmpi.l #$00000001,d0                              ; +$0114 : 0C8000000001
    bne.w L_004B50                                    ; +$011A : 6600016C
    move.w 10(a0),d0                                  ; +$011E : 3028000A
    tst.w d0                                          ; +$0122 : 4A40
    bne.w L_004B50                                    ; +$0124 : 66000162
    tst.l 12(a0)                                      ; +$0128 : 4AA8000C
    bne.w L_004B50                                    ; +$012C : 6600015A
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
    bne.w L_004B50                                    ; +$0152 : 66000134
    move.l #$00000000,d0                              ; +$0156 : 203C00000000
    move.w 4(a1),d0                                   ; +$015C : 30290004
    cmpi.l #$00000100,d0                              ; +$0160 : 0C8000000100
    bhi.w L_004B50                                    ; +$0166 : 62000120
    tst.w 6(a1)                                       ; +$016A : 4A690006
    bne.w L_004B50                                    ; +$016E : 66000118
    movea.l 456(a5),a0                                ; +$0172 : 206D01C8
    move.l a0,d0                                      ; +$0176 : 2008
    tst.l d0                                          ; +$0178 : 4A80
    beq.w L_004B50                                    ; +$017A : 6700010C
    movea.l (a0),a1                                   ; +$017E : 2250
    move.l a1,d0                                      ; +$0180 : 2009
    tst.l d0                                          ; +$0182 : 4A80
    beq.w L_004B50                                    ; +$0184 : 67000102
    tst.l 8(a0)                                       ; +$0188 : 4AA80008
    beq.w L_004B50                                    ; +$018C : 670000FA
    move.l 28(a0),d0                                  ; +$0190 : 2028001C
    tst.l d0                                          ; +$0194 : 4A80
    ble.w L_004B50                                    ; +$0196 : 6F0000F0
    cmpi.l #$00000008,d0                              ; +$019A : 0C8000000008
    bhi.w L_004B50                                    ; +$01A0 : 620000E6
    move.l 24(a0),d0                                  ; +$01A4 : 20280018
    andi.l #$00000C80,d0                              ; +$01A8 : 028000000C80
    bne.w L_004B50                                    ; +$01AE : 660000D8
    move.l 20(a0),d7                                  ; +$01B2 : 2E280014
    tst.l d7                                          ; +$01B6 : 4A87
    beq.w L_004B50                                    ; +$01B8 : 670000CE
    cmpi.l #$00000100,d7                              ; +$01BC : 0C8700000100
    bhi.w L_004B50                                    ; +$01C2 : 620000C4
    movea.l 48(a1),a2                                 ; +$01C6 : 24690030
    move.l a2,d0                                      ; +$01CA : 200A
    tst.l d0                                          ; +$01CC : 4A80
    beq.w L_004B50                                    ; +$01CE : 670000B8
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    move.w 2(a2),d0                                   ; +$01D8 : 302A0002
    tst.l d0                                          ; +$01DC : 4A80
    beq.w L_004B50                                    ; +$01DE : 670000A8
    cmpi.l #$00000100,d0                              ; +$01E2 : 0C8000000100
    bhi.w L_004B50                                    ; +$01E8 : 6200009E
    cmp.l d0,d7                                       ; +$01EC : BE80
    bls.w L_004ABC                                    ; +$01EE : 63000004
    move.l d0,d7                                      ; +$01F2 : 2E00
L_004ABC:
    move.l d7,d0                                      ; +$01F4 : 2007
    mulu.w #$000C,d0                                  ; +$01F6 : C0FC000C
    move.l #$00000001,d1                              ; +$01FA : 223C00000001
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -684(a6)                                      ; +$0204 : 4EAEFD54
    tst.l d0                                          ; +$0208 : 4A80
    beq.w L_004B50                                    ; +$020A : 6700007C
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
L_004B0C:
    move.l #$00000000,(a1)+                           ; +$0244 : 22FC00000000
    subq.l #1,d6                                      ; +$024A : 5386
    bne.w L_004B0C                                    ; +$024C : 6600FFF6
    movea.l d0,a1                                     ; +$0250 : 2240
    movea.l a4,a2                                     ; +$0252 : 244C
    move.l d7,d6                                      ; +$0254 : 2C07
L_004B1E:
    move.b (a2),(a1)+                                 ; +$0256 : 12D2
    addq.l #4,a2                                      ; +$0258 : 588A
    move.b (a2),(a1)+                                 ; +$025A : 12D2
    addq.l #4,a2                                      ; +$025C : 588A
    move.b (a2),(a1)+                                 ; +$025E : 12D2
    addq.l #4,a2                                      ; +$0260 : 588A
    subq.l #1,d6                                      ; +$0262 : 5386
    bne.w L_004B1E                                    ; +$0264 : 6600FFF0
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
L_004B50:
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
    bhi.w L_004E04                                    ; +$0014 : 62000292
    move.l d4,d0                                      ; +$0018 : 2004
    cmpi.l #$00000018,d0                              ; +$001A : 0C8000000018
    bls.w L_004E04                                    ; +$0020 : 63000286
    andi.l #$00000001,d0                              ; +$0024 : 028000000001
    bne.w L_004E04                                    ; +$002A : 6600027C
    move.l d4,d0                                      ; +$002E : 2004
    subi.l #$00000018,d0                              ; +$0030 : 048000000018
    movea.l d0,a1                                     ; +$0036 : 2240
    movea.l $0004.w,a6                                ; +$0038 : 2C780004
    jsr -534(a6)                                      ; +$003C : 4EAEFDEA
    tst.l d0                                          ; +$0040 : 4A80
    beq.w L_004E04                                    ; +$0042 : 67000264
    movea.l d4,a0                                     ; +$0046 : 2044
    move.l #$00000000,d6                              ; +$0048 : 2C3C00000000
    move.w 8(a0),d6                                   ; +$004E : 3C280008
    tst.l d6                                          ; +$0052 : 4A86
    beq.w L_004E04                                    ; +$0054 : 67000252
    cmpi.l #$00000100,d6                              ; +$0058 : 0C8600000100
    bhi.w L_004E04                                    ; +$005E : 62000248
    cmp.l d6,d5                                       ; +$0062 : BA86
    bcc.w L_004E04                                    ; +$0064 : 64000242
    move.l d6,d7                                      ; +$0068 : 2E06
    mulu.w #$0308,d7                                  ; +$006A : CEFC0308
    addi.l #$00000010,d7                              ; +$006E : 068700000010
    move.l d4,d0                                      ; +$0074 : 2004
    add.l d7,d0                                       ; +$0076 : D087
    bcs.w L_004E04                                    ; +$0078 : 6500022E
    subq.l #1,d0                                      ; +$007C : 5380
    movea.l d0,a1                                     ; +$007E : 2240
    jsr -534(a6)                                      ; +$0080 : 4EAEFDEA
    tst.l d0                                          ; +$0084 : 4A80
    beq.w L_004E04                                    ; +$0086 : 67000220
    movea.l d4,a0                                     ; +$008A : 2044
    move.l -20(a0),d0                                 ; +$008C : 2028FFEC
    move.l d7,d1                                      ; +$0090 : 2207
    addi.l #$00000010,d1                              ; +$0092 : 068100000010
    cmp.l d1,d0                                       ; +$0098 : B081
    bne.w L_004E04                                    ; +$009A : 6600020C
    move.l #$00000000,d0                              ; +$009E : 203C00000000
    move.w -12(a0),d0                                 ; +$00A4 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00A8 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00AC : 0C8000000001
    bne.w L_004E04                                    ; +$00B2 : 660001F4
    move.l -16(a0),d0                                 ; +$00B6 : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00BA : 0C8000000005
    bcs.w L_004E04                                    ; +$00C0 : 650001E6
    cmpi.l #$0000FFFF,d0                              ; +$00C4 : 0C800000FFFF
    bhi.w L_004E04                                    ; +$00CA : 620001DC
    move.l -8(a0),d0                                  ; +$00CE : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00D2 : 0C8041474150
    bne.w L_004E04                                    ; +$00D8 : 660001CE
    move.l -4(a0),d0                                  ; +$00DC : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00E0 : 0C80414C2020
    bne.w L_004E04                                    ; +$00E6 : 660001C0
    move.l (a0),d0                                    ; +$00EA : 2010
    cmpi.l #$41474150,d0                              ; +$00EC : 0C8041474150
    bne.w L_004E04                                    ; +$00F2 : 660001B4
    move.l #$00000000,d0                              ; +$00F6 : 203C00000000
    move.w 4(a0),d0                                   ; +$00FC : 30280004
    cmpi.l #$0000414C,d0                              ; +$0100 : 0C800000414C
    bne.w L_004E04                                    ; +$0106 : 660001A0
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 6(a0),d0                                   ; +$0110 : 30280006
    cmpi.l #$00000001,d0                              ; +$0114 : 0C8000000001
    bne.w L_004E04                                    ; +$011A : 6600018C
    tst.w 10(a0)                                      ; +$011E : 4A68000A
    bne.w L_004E04                                    ; +$0122 : 66000184
    tst.l 12(a0)                                      ; +$0126 : 4AA8000C
    bne.w L_004E04                                    ; +$012A : 6600017C
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
    bne.w L_004E04                                    ; +$0150 : 66000156
    move.l #$00000000,d7                              ; +$0154 : 2E3C00000000
    move.w 4(a1),d7                                   ; +$015A : 3E290004
    tst.l d7                                          ; +$015E : 4A87
    beq.w L_004E04                                    ; +$0160 : 67000146
    cmpi.l #$00000100,d7                              ; +$0164 : 0C8700000100
    bhi.w L_004E04                                    ; +$016A : 6200013C
    tst.w 6(a1)                                       ; +$016E : 4A690006
    bne.w L_004E04                                    ; +$0172 : 66000134
    add.l d4,d0                                       ; +$0176 : D084
    movea.l d0,a2                                     ; +$0178 : 2440
    movea.l 456(a5),a0                                ; +$017A : 206D01C8
    move.l a0,d0                                      ; +$017E : 2008
    tst.l d0                                          ; +$0180 : 4A80
    beq.w L_004E04                                    ; +$0182 : 67000124
    movea.l (a0),a1                                   ; +$0186 : 2250
    move.l a1,d0                                      ; +$0188 : 2009
    tst.l d0                                          ; +$018A : 4A80
    beq.w L_004E04                                    ; +$018C : 6700011A
    tst.l 8(a0)                                       ; +$0190 : 4AA80008
    beq.w L_004E04                                    ; +$0194 : 67000112
    move.l 28(a0),d0                                  ; +$0198 : 2028001C
    tst.l d0                                          ; +$019C : 4A80
    ble.w L_004E04                                    ; +$019E : 6F000108
    cmpi.l #$00000008,d0                              ; +$01A2 : 0C8000000008
    bhi.w L_004E04                                    ; +$01A8 : 620000FE
    move.l 24(a0),d0                                  ; +$01AC : 20280018
    andi.l #$00000C80,d0                              ; +$01B0 : 028000000C80
    bne.w L_004E04                                    ; +$01B6 : 660000F0
    move.l 20(a0),d0                                  ; +$01BA : 20280014
    tst.l d0                                          ; +$01BE : 4A80
    beq.w L_004E04                                    ; +$01C0 : 670000E6
    cmpi.l #$00000100,d0                              ; +$01C4 : 0C8000000100
    bhi.w L_004E04                                    ; +$01CA : 620000DC
    cmp.l d0,d7                                       ; +$01CE : BE80
    bhi.w L_004E04                                    ; +$01D0 : 620000D6
    movea.l 48(a1),a1                                 ; +$01D4 : 22690030
    move.l a1,d0                                      ; +$01D8 : 2009
    tst.l d0                                          ; +$01DA : 4A80
    beq.w L_004E04                                    ; +$01DC : 670000CA
    move.l #$00000000,d0                              ; +$01E0 : 203C00000000
    move.w 2(a1),d0                                   ; +$01E6 : 30290002
    tst.l d0                                          ; +$01EA : 4A80
    beq.w L_004E04                                    ; +$01EC : 670000BA
    cmpi.l #$00000100,d0                              ; +$01F0 : 0C8000000100
    bhi.w L_004E04                                    ; +$01F6 : 620000B0
    cmp.l d0,d7                                       ; +$01FA : BE80
    bhi.w L_004E04                                    ; +$01FC : 620000AA
    move.l d7,d0                                      ; +$0200 : 2007
    mulu.w #$000C,d0                                  ; +$0202 : C0FC000C
    addi.l #$00000008,d0                              ; +$0206 : 068000000008
    move.l #$00000001,d1                              ; +$020C : 223C00000001
    movea.l $0004.w,a6                                ; +$0212 : 2C780004
    jsr -684(a6)                                      ; +$0216 : 4EAEFD54
    tst.l d0                                          ; +$021A : 4A80
    beq.w L_004E04                                    ; +$021C : 6700008A
    movea.l d0,a4                                     ; +$0220 : 2840
    movea.l a4,a1                                     ; +$0222 : 224C
    move.l d7,d0                                      ; +$0224 : 2007
    swap d0                                           ; +$0226 : 4840
    move.l d0,(a1)+                                   ; +$0228 : 22C0
    move.l d7,d6                                      ; +$022A : 2C07
L_004D88:
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
    bne.w L_004D88                                    ; +$0270 : 6600FFBA
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
L_004E04:
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
    beq.w L_0051A4                                    ; +$0014 : 6700037E
    cmpi.l #$000000FF,d0                              ; +$0018 : 0C80000000FF
    bhi.w L_0051A4                                    ; +$001E : 62000374
    cmpi.l #$000000FF,d5                              ; +$0022 : 0C85000000FF
    bhi.w L_0051A4                                    ; +$0028 : 6200036A
    move.l d4,d0                                      ; +$002C : 2004
    cmpi.l #$00000018,d0                              ; +$002E : 0C8000000018
    bls.w L_0051A4                                    ; +$0034 : 6300035E
    andi.l #$00000001,d0                              ; +$0038 : 028000000001
    bne.w L_0051A4                                    ; +$003E : 66000354
    move.l d4,d0                                      ; +$0042 : 2004
    subi.l #$00000018,d0                              ; +$0044 : 048000000018
    movea.l d0,a1                                     ; +$004A : 2240
    movea.l $0004.w,a6                                ; +$004C : 2C780004
    jsr -534(a6)                                      ; +$0050 : 4EAEFDEA
    tst.l d0                                          ; +$0054 : 4A80
    beq.w L_0051A4                                    ; +$0056 : 6700033C
    movea.l d4,a0                                     ; +$005A : 2044
    move.l #$00000000,d6                              ; +$005C : 2C3C00000000
    move.w 8(a0),d6                                   ; +$0062 : 3C280008
    tst.l d6                                          ; +$0066 : 4A86
    beq.w L_0051A4                                    ; +$0068 : 6700032A
    cmpi.l #$00000100,d6                              ; +$006C : 0C8600000100
    bhi.w L_0051A4                                    ; +$0072 : 62000320
    cmp.l d6,d5                                       ; +$0076 : BA86
    bcc.w L_0051A4                                    ; +$0078 : 6400031A
    move.l d6,d7                                      ; +$007C : 2E06
    mulu.w #$0308,d7                                  ; +$007E : CEFC0308
    addi.l #$00000010,d7                              ; +$0082 : 068700000010
    move.l d4,d0                                      ; +$0088 : 2004
    add.l d7,d0                                       ; +$008A : D087
    bcs.w L_0051A4                                    ; +$008C : 65000306
    subq.l #1,d0                                      ; +$0090 : 5380
    movea.l d0,a1                                     ; +$0092 : 2240
    jsr -534(a6)                                      ; +$0094 : 4EAEFDEA
    tst.l d0                                          ; +$0098 : 4A80
    beq.w L_0051A4                                    ; +$009A : 670002F8
    movea.l d4,a0                                     ; +$009E : 2044
    move.l -20(a0),d0                                 ; +$00A0 : 2028FFEC
    move.l d7,d1                                      ; +$00A4 : 2207
    addi.l #$00000010,d1                              ; +$00A6 : 068100000010
    cmp.l d1,d0                                       ; +$00AC : B081
    bne.w L_0051A4                                    ; +$00AE : 660002E4
    move.l #$00000000,d0                              ; +$00B2 : 203C00000000
    move.w -12(a0),d0                                 ; +$00B8 : 3028FFF4
    andi.w #$FFFD,d0                                  ; +$00BC : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00C0 : 0C8000000001
    bne.w L_0051A4                                    ; +$00C6 : 660002CC
    move.l -16(a0),d0                                 ; +$00CA : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00CE : 0C8000000005
    bcs.w L_0051A4                                    ; +$00D4 : 650002BE
    cmpi.l #$0000FFFF,d0                              ; +$00D8 : 0C800000FFFF
    bhi.w L_0051A4                                    ; +$00DE : 620002B4
    move.l -8(a0),d0                                  ; +$00E2 : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$00E6 : 0C8041474150
    bne.w L_0051A4                                    ; +$00EC : 660002A6
    move.l -4(a0),d0                                  ; +$00F0 : 2028FFFC
    cmpi.l #$414C2020,d0                              ; +$00F4 : 0C80414C2020
    bne.w L_0051A4                                    ; +$00FA : 66000298
    move.l (a0),d0                                    ; +$00FE : 2010
    cmpi.l #$41474150,d0                              ; +$0100 : 0C8041474150
    bne.w L_0051A4                                    ; +$0106 : 6600028C
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w 4(a0),d0                                   ; +$0110 : 30280004
    cmpi.l #$0000414C,d0                              ; +$0114 : 0C800000414C
    bne.w L_0051A4                                    ; +$011A : 66000278
    move.l #$00000000,d0                              ; +$011E : 203C00000000
    move.w 6(a0),d0                                   ; +$0124 : 30280006
    cmpi.l #$00000001,d0                              ; +$0128 : 0C8000000001
    bne.w L_0051A4                                    ; +$012E : 66000264
    tst.w 10(a0)                                      ; +$0132 : 4A68000A
    bne.w L_0051A4                                    ; +$0136 : 6600025C
    tst.l 12(a0)                                      ; +$013A : 4AA8000C
    bne.w L_0051A4                                    ; +$013E : 66000254
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
    bne.w L_0051A4                                    ; +$0164 : 6600022E
    move.l #$00000000,d7                              ; +$0168 : 2E3C00000000
    move.w 4(a1),d7                                   ; +$016E : 3E290004
    tst.l d7                                          ; +$0172 : 4A87
    beq.w L_0051A4                                    ; +$0174 : 6700021E
    cmpi.l #$00000100,d7                              ; +$0178 : 0C8700000100
    bhi.w L_0051A4                                    ; +$017E : 62000214
    tst.w 6(a1)                                       ; +$0182 : 4A690006
    bne.w L_0051A4                                    ; +$0186 : 6600020C
    add.l d4,d0                                       ; +$018A : D084
    movea.l d0,a2                                     ; +$018C : 2440
    movea.l 456(a5),a0                                ; +$018E : 206D01C8
    move.l a0,d0                                      ; +$0192 : 2008
    tst.l d0                                          ; +$0194 : 4A80
    beq.w L_0051A4                                    ; +$0196 : 670001FC
    movea.l (a0),a1                                   ; +$019A : 2250
    move.l a1,d0                                      ; +$019C : 2009
    tst.l d0                                          ; +$019E : 4A80
    beq.w L_0051A4                                    ; +$01A0 : 670001F2
    tst.l 8(a0)                                       ; +$01A4 : 4AA80008
    beq.w L_0051A4                                    ; +$01A8 : 670001EA
    move.l 28(a0),d0                                  ; +$01AC : 2028001C
    tst.l d0                                          ; +$01B0 : 4A80
    ble.w L_0051A4                                    ; +$01B2 : 6F0001E0
    cmpi.l #$00000008,d0                              ; +$01B6 : 0C8000000008
    bhi.w L_0051A4                                    ; +$01BC : 620001D6
    move.l 24(a0),d0                                  ; +$01C0 : 20280018
    andi.l #$00000C80,d0                              ; +$01C4 : 028000000C80
    bne.w L_0051A4                                    ; +$01CA : 660001C8
    move.l 20(a0),d0                                  ; +$01CE : 20280014
    tst.l d0                                          ; +$01D2 : 4A80
    beq.w L_0051A4                                    ; +$01D4 : 670001BE
    cmpi.l #$00000100,d0                              ; +$01D8 : 0C8000000100
    bhi.w L_0051A4                                    ; +$01DE : 620001B4
    cmp.l d0,d7                                       ; +$01E2 : BE80
    bhi.w L_0051A4                                    ; +$01E4 : 620001AE
    movea.l 48(a1),a1                                 ; +$01E8 : 22690030
    move.l a1,d0                                      ; +$01EC : 2009
    tst.l d0                                          ; +$01EE : 4A80
    beq.w L_0051A4                                    ; +$01F0 : 670001A2
    move.l #$00000000,d0                              ; +$01F4 : 203C00000000
    move.w 2(a1),d0                                   ; +$01FA : 30290002
    tst.l d0                                          ; +$01FE : 4A80
    beq.w L_0051A4                                    ; +$0200 : 67000192
    cmpi.l #$00000100,d0                              ; +$0204 : 0C8000000100
    bhi.w L_0051A4                                    ; +$020A : 62000188
    cmp.l d0,d7                                       ; +$020E : BE80
    bhi.w L_0051A4                                    ; +$0210 : 62000182
    move.l (a7),d6                                    ; +$0214 : 2C17
    move.l d7,d0                                      ; +$0216 : 2007
    mulu.w #$002A,d0                                  ; +$0218 : C0FC002A
    addi.l #$00000008,d0                              ; +$021C : 068000000008
    move.l #$00000001,d1                              ; +$0222 : 223C00000001
    movea.l $0004.w,a6                                ; +$0228 : 2C780004
    jsr -684(a6)                                      ; +$022C : 4EAEFD54
    tst.l d0                                          ; +$0230 : 4A80
    beq.w L_0051A4                                    ; +$0232 : 67000160
    movea.l d0,a4                                     ; +$0236 : 2840
    cmpi.l #$00000001,d6                              ; +$0238 : 0C8600000001
    beq.w L_0050DC                                    ; +$023E : 6700008C
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
L_0050AC:
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
    bne.w L_0050AC                                    ; +$02BC : 6600FFDE
    move.l d7,d0                                      ; +$02C0 : 2007
    mulu.w #$0003,d0                                  ; +$02C2 : C0FC0003
    move.l a2,d1                                      ; +$02C6 : 220A
    sub.l d0,d1                                       ; +$02C8 : 9280
    movea.l d1,a2                                     ; +$02CA : 2441
L_0050DC:
    move.l d6,d4                                      ; +$02CC : 2806
L_0050DE:
    movea.l 456(a5),a6                                ; +$02CE : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$02D2 : 2C6E0008
    jsr -270(a6)                                      ; +$02D6 : 4EAEFEF2
    movea.l a4,a1                                     ; +$02DA : 224C
    move.l d7,d0                                      ; +$02DC : 2007
    swap d0                                           ; +$02DE : 4840
    move.l d0,(a1)+                                   ; +$02E0 : 22C0
    cmpi.l #$00000001,d4                              ; +$02E2 : 0C8400000001
    beq.w L_005146                                    ; +$02E8 : 6700004C
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
L_005118:
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
    bne.w L_005118                                    ; +$032E : 6600FFD8
    bra.w L_00516A                                    ; +$0332 : 60000026
L_005146:
    movea.l a2,a0                                     ; +$0336 : 204A
    move.l d7,d5                                      ; +$0338 : 2A07
    mulu.w #$0003,d5                                  ; +$033A : CAFC0003
L_00514E:
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
    bne.w L_00514E                                    ; +$0356 : 6600FFE6
L_00516A:
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
    bne.w L_0050DE                                    ; +$0380 : 6600FF4C
    movea.l a4,a1                                     ; +$0384 : 224C
    movea.l $0004.w,a6                                ; +$0386 : 2C780004
    jsr -690(a6)                                      ; +$038A : 4EAEFD4E
    move.l #$00000001,d3                              ; +$038E : 263C00000001
L_0051A4:
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
    beq.w L_0053B0                                    ; +$0010 : 670001EC
    cmpi.l #$000000FF,d0                              ; +$0014 : 0C80000000FF
    bhi.w L_0053B0                                    ; +$001A : 620001E2
    movea.l 456(a5),a0                                ; +$001E : 206D01C8
    move.l a0,d0                                      ; +$0022 : 2008
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0053B0                                    ; +$0026 : 670001D6
    movea.l (a0),a1                                   ; +$002A : 2250
    move.l a1,d0                                      ; +$002C : 2009
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0053B0                                    ; +$0030 : 670001CC
    tst.l 8(a0)                                       ; +$0034 : 4AA80008
    beq.w L_0053B0                                    ; +$0038 : 670001C4
    move.l 28(a0),d0                                  ; +$003C : 2028001C
    tst.l d0                                          ; +$0040 : 4A80
    ble.w L_0053B0                                    ; +$0042 : 6F0001BA
    cmpi.l #$00000008,d0                              ; +$0046 : 0C8000000008
    bhi.w L_0053B0                                    ; +$004C : 620001B0
    move.l 24(a0),d0                                  ; +$0050 : 20280018
    andi.l #$00000C80,d0                              ; +$0054 : 028000000C80
    bne.w L_0053B0                                    ; +$005A : 660001A2
    move.l 20(a0),d7                                  ; +$005E : 2E280014
    tst.l d7                                          ; +$0062 : 4A87
    beq.w L_0053B0                                    ; +$0064 : 67000198
    cmpi.l #$00000100,d7                              ; +$0068 : 0C8700000100
    bhi.w L_0053B0                                    ; +$006E : 6200018E
    movea.l 48(a1),a1                                 ; +$0072 : 22690030
    move.l a1,d0                                      ; +$0076 : 2009
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0053B0                                    ; +$007A : 67000182
    move.l #$00000000,d0                              ; +$007E : 203C00000000
    move.w 2(a1),d0                                   ; +$0084 : 30290002
    tst.l d0                                          ; +$0088 : 4A80
    beq.w L_0053B0                                    ; +$008A : 67000172
    cmpi.l #$00000100,d0                              ; +$008E : 0C8000000100
    bhi.w L_0053B0                                    ; +$0094 : 62000168
    cmp.l d0,d7                                       ; +$0098 : BE80
    bhi.w L_0053B0                                    ; +$009A : 62000162
    move.l (a7),d6                                    ; +$009E : 2C17
    move.l d7,d0                                      ; +$00A0 : 2007
    mulu.w #$002A,d0                                  ; +$00A2 : C0FC002A
    addi.l #$00000008,d0                              ; +$00A6 : 068000000008
    move.l #$00000001,d1                              ; +$00AC : 223C00000001
    movea.l $0004.w,a6                                ; +$00B2 : 2C780004
    jsr -684(a6)                                      ; +$00B6 : 4EAEFD54
    tst.l d0                                          ; +$00BA : 4A80
    beq.w L_0053B0                                    ; +$00BC : 67000140
    movea.l d0,a4                                     ; +$00C0 : 2840
    cmpi.l #$00000001,d6                              ; +$00C2 : 0C8600000001
    beq.w L_0052FA                                    ; +$00C8 : 6700007E
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
L_0052D8:
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
    bne.w L_0052D8                                    ; +$0144 : 6600FFE0
L_0052FA:
    move.l d6,d4                                      ; +$0148 : 2806
L_0052FC:
    movea.l 456(a5),a6                                ; +$014A : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$014E : 2C6E0008
    jsr -270(a6)                                      ; +$0152 : 4EAEFEF2
    movea.l a4,a1                                     ; +$0156 : 224C
    move.l d7,d0                                      ; +$0158 : 2007
    swap d0                                           ; +$015A : 4840
    move.l d0,(a1)+                                   ; +$015C : 22C0
    cmpi.l #$00000001,d4                              ; +$015E : 0C8400000001
    beq.w L_005364                                    ; +$0164 : 6700004C
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
L_005336:
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
    bne.w L_005336                                    ; +$01AA : 6600FFD8
    bra.w L_005376                                    ; +$01AE : 60000014
L_005364:
    move.l d7,d5                                      ; +$01B2 : 2A07
    mulu.w #$0003,d5                                  ; +$01B4 : CAFC0003
L_00536A:
    move.l #$00000000,(a1)+                           ; +$01B8 : 22FC00000000
    subq.l #1,d5                                      ; +$01BE : 5385
    bne.w L_00536A                                    ; +$01C0 : 6600FFF6
L_005376:
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
    bne.w L_0052FC                                    ; +$01EA : 6600FF5E
    movea.l a4,a1                                     ; +$01EE : 224C
    movea.l $0004.w,a6                                ; +$01F0 : 2C780004
    jsr -690(a6)                                      ; +$01F4 : 4EAEFD4E
    move.l #$00000001,d3                              ; +$01F8 : 263C00000001
L_0053B0:
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
    beq.w L_0055BC                                    ; +$0010 : 670001EC
    cmpi.l #$000000FF,d0                              ; +$0014 : 0C80000000FF
    bhi.w L_0055BC                                    ; +$001A : 620001E2
    movea.l 456(a5),a0                                ; +$001E : 206D01C8
    move.l a0,d0                                      ; +$0022 : 2008
    tst.l d0                                          ; +$0024 : 4A80
    beq.w L_0055BC                                    ; +$0026 : 670001D6
    movea.l (a0),a1                                   ; +$002A : 2250
    move.l a1,d0                                      ; +$002C : 2009
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_0055BC                                    ; +$0030 : 670001CC
    tst.l 8(a0)                                       ; +$0034 : 4AA80008
    beq.w L_0055BC                                    ; +$0038 : 670001C4
    move.l 28(a0),d0                                  ; +$003C : 2028001C
    tst.l d0                                          ; +$0040 : 4A80
    ble.w L_0055BC                                    ; +$0042 : 6F0001BA
    cmpi.l #$00000008,d0                              ; +$0046 : 0C8000000008
    bhi.w L_0055BC                                    ; +$004C : 620001B0
    move.l 24(a0),d0                                  ; +$0050 : 20280018
    andi.l #$00000C80,d0                              ; +$0054 : 028000000C80
    bne.w L_0055BC                                    ; +$005A : 660001A2
    move.l 20(a0),d7                                  ; +$005E : 2E280014
    tst.l d7                                          ; +$0062 : 4A87
    beq.w L_0055BC                                    ; +$0064 : 67000198
    cmpi.l #$00000100,d7                              ; +$0068 : 0C8700000100
    bhi.w L_0055BC                                    ; +$006E : 6200018E
    movea.l 48(a1),a1                                 ; +$0072 : 22690030
    move.l a1,d0                                      ; +$0076 : 2009
    tst.l d0                                          ; +$0078 : 4A80
    beq.w L_0055BC                                    ; +$007A : 67000182
    move.l #$00000000,d0                              ; +$007E : 203C00000000
    move.w 2(a1),d0                                   ; +$0084 : 30290002
    tst.l d0                                          ; +$0088 : 4A80
    beq.w L_0055BC                                    ; +$008A : 67000172
    cmpi.l #$00000100,d0                              ; +$008E : 0C8000000100
    bhi.w L_0055BC                                    ; +$0094 : 62000168
    cmp.l d0,d7                                       ; +$0098 : BE80
    bhi.w L_0055BC                                    ; +$009A : 62000162
    move.l (a7),d6                                    ; +$009E : 2C17
    move.l d7,d0                                      ; +$00A0 : 2007
    mulu.w #$002A,d0                                  ; +$00A2 : C0FC002A
    addi.l #$00000008,d0                              ; +$00A6 : 068000000008
    move.l #$00000001,d1                              ; +$00AC : 223C00000001
    movea.l $0004.w,a6                                ; +$00B2 : 2C780004
    jsr -684(a6)                                      ; +$00B6 : 4EAEFD54
    tst.l d0                                          ; +$00BA : 4A80
    beq.w L_0055BC                                    ; +$00BC : 67000140
    movea.l d0,a4                                     ; +$00C0 : 2840
    cmpi.l #$00000001,d6                              ; +$00C2 : 0C8600000001
    beq.w L_005506                                    ; +$00C8 : 6700007E
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
L_0054E4:
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
    bne.w L_0054E4                                    ; +$0144 : 6600FFE0
L_005506:
    move.l d6,d4                                      ; +$0148 : 2806
L_005508:
    movea.l 456(a5),a6                                ; +$014A : 2C6D01C8
    movea.l 8(a6),a6                                  ; +$014E : 2C6E0008
    jsr -270(a6)                                      ; +$0152 : 4EAEFEF2
    movea.l a4,a1                                     ; +$0156 : 224C
    move.l d7,d0                                      ; +$0158 : 2007
    swap d0                                           ; +$015A : 4840
    move.l d0,(a1)+                                   ; +$015C : 22C0
    cmpi.l #$00000001,d4                              ; +$015E : 0C8400000001
    beq.w L_005570                                    ; +$0164 : 6700004C
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
L_005542:
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
    bne.w L_005542                                    ; +$01AA : 6600FFD8
    bra.w L_005582                                    ; +$01AE : 60000014
L_005570:
    move.l d7,d5                                      ; +$01B2 : 2A07
    mulu.w #$0003,d5                                  ; +$01B4 : CAFC0003
L_005576:
    move.l #$FFFFFFFF,(a1)+                           ; +$01B8 : 22FCFFFFFFFF
    subq.l #1,d5                                      ; +$01BE : 5385
    bne.w L_005576                                    ; +$01C0 : 6600FFF6
L_005582:
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
    bne.w L_005508                                    ; +$01EA : 6600FF5E
    movea.l a4,a1                                     ; +$01EE : 224C
    movea.l $0004.w,a6                                ; +$01F0 : 2C780004
    jsr -690(a6)                                      ; +$01F4 : 4EAEFD4E
    move.l #$00000001,d3                              ; +$01F8 : 263C00000001
L_0055BC:
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
    beq.w L_0055F0                                    ; +$0018 : 6700000C
    cmpi.l #$FFFFFFFF,d0                              ; +$001C : 0C80FFFFFFFF
    bne.w L_0057B4                                    ; +$0022 : 660001C6
L_0055F0:
    cmpi.l #$000000FF,d5                              ; +$0026 : 0C85000000FF
    bhi.w L_0057B4                                    ; +$002C : 620001BC
    cmp.l d5,d4                                       ; +$0030 : B885
    bcc.w L_0057B4                                    ; +$0032 : 640001B6
    movea.l 456(a5),a0                                ; +$0036 : 206D01C8
    move.l a0,d0                                      ; +$003A : 2008
    tst.l d0                                          ; +$003C : 4A80
    beq.w L_0057B4                                    ; +$003E : 670001AA
    movea.l (a0),a1                                   ; +$0042 : 2250
    move.l a1,d0                                      ; +$0044 : 2009
    tst.l d0                                          ; +$0046 : 4A80
    beq.w L_0057B4                                    ; +$0048 : 670001A0
    tst.l 8(a0)                                       ; +$004C : 4AA80008
    beq.w L_0057B4                                    ; +$0050 : 67000198
    move.l 28(a0),d0                                  ; +$0054 : 2028001C
    tst.l d0                                          ; +$0058 : 4A80
    ble.w L_0057B4                                    ; +$005A : 6F00018E
    cmpi.l #$00000008,d0                              ; +$005E : 0C8000000008
    bhi.w L_0057B4                                    ; +$0064 : 62000184
    move.l 24(a0),d0                                  ; +$0068 : 20280018
    andi.l #$00000C80,d0                              ; +$006C : 028000000C80
    bne.w L_0057B4                                    ; +$0072 : 66000176
    move.l 20(a0),d7                                  ; +$0076 : 2E280014
    tst.l d7                                          ; +$007A : 4A87
    beq.w L_0057B4                                    ; +$007C : 6700016C
    cmpi.l #$00000100,d7                              ; +$0080 : 0C8700000100
    bhi.w L_0057B4                                    ; +$0086 : 62000162
    cmp.l d7,d5                                       ; +$008A : BA87
    bcc.w L_0057B4                                    ; +$008C : 6400015C
    movea.l 48(a1),a1                                 ; +$0090 : 22690030
    move.l a1,d0                                      ; +$0094 : 2009
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_0057B4                                    ; +$0098 : 67000150
    move.l #$00000000,d0                              ; +$009C : 203C00000000
    move.w 2(a1),d0                                   ; +$00A2 : 30290002
    tst.l d0                                          ; +$00A6 : 4A80
    beq.w L_0057B4                                    ; +$00A8 : 67000140
    cmpi.l #$00000100,d0                              ; +$00AC : 0C8000000100
    bhi.w L_0057B4                                    ; +$00B2 : 62000136
    cmp.l d0,d7                                       ; +$00B6 : BE80
    bhi.w L_0057B4                                    ; +$00B8 : 62000130
    cmp.l d0,d5                                       ; +$00BC : BA80
    bcc.w L_0057B4                                    ; +$00BE : 6400012A
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
    beq.w L_0057B4                                    ; +$00E4 : 67000104
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
    beq.w L_005746                                    ; +$0130 : 6700004A
    movea.l a4,a0                                     ; +$0134 : 204C
    addq.l #4,a0                                      ; +$0136 : 5888
    move.l a0,d0                                      ; +$0138 : 2008
    addi.l #$0000000C,d0                              ; +$013A : 06800000000C
    movea.l d0,a1                                     ; +$0140 : 2240
    move.l (a0),d4                                    ; +$0142 : 2810
    move.l 4(a0),d5                                   ; +$0144 : 2A280004
    move.l 8(a0),d6                                   ; +$0148 : 2C280008
    subq.l #1,d7                                      ; +$014C : 5387
L_005718:
    move.l (a1),(a0)                                  ; +$014E : 2091
    move.l 4(a1),4(a0)                                ; +$0150 : 216900040004
    move.l 8(a1),8(a0)                                ; +$0156 : 216900080008
    movea.l a1,a0                                     ; +$015C : 2049
    move.l a1,d0                                      ; +$015E : 2009
    addi.l #$0000000C,d0                              ; +$0160 : 06800000000C
    movea.l d0,a1                                     ; +$0166 : 2240
    subq.l #1,d7                                      ; +$0168 : 5387
    bne.w L_005718                                    ; +$016A : 6600FFE2
    move.l d4,(a0)                                    ; +$016E : 2084
    move.l d5,4(a0)                                   ; +$0170 : 21450004
    move.l d6,8(a0)                                   ; +$0174 : 21460008
    bra.w L_005786                                    ; +$0178 : 60000042
L_005746:
    move.l a2,d0                                      ; +$017C : 200A
    subi.l #$0000000C,d0                              ; +$017E : 04800000000C
    movea.l d0,a1                                     ; +$0184 : 2240
    move.l (a1),d4                                    ; +$0186 : 2811
    move.l 4(a1),d5                                   ; +$0188 : 2A290004
    move.l 8(a1),d6                                   ; +$018C : 2C290008
    subq.l #1,d7                                      ; +$0190 : 5387
L_00575C:
    move.l a1,d0                                      ; +$0192 : 2009
    subi.l #$0000000C,d0                              ; +$0194 : 04800000000C
    movea.l d0,a0                                     ; +$019A : 2040
    move.l (a0),(a1)                                  ; +$019C : 2290
    move.l 4(a0),4(a1)                                ; +$019E : 236800040004
    move.l 8(a0),8(a1)                                ; +$01A4 : 236800080008
    movea.l a0,a1                                     ; +$01AA : 2248
    subq.l #1,d7                                      ; +$01AC : 5387
    bne.w L_00575C                                    ; +$01AE : 6600FFE2
    move.l d4,(a1)                                    ; +$01B2 : 2284
    move.l d5,4(a1)                                   ; +$01B4 : 23450004
    move.l d6,8(a1)                                   ; +$01B8 : 23460008
L_005786:
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
L_0057B4:
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
    beq.w L_005918                                    ; +$0016 : 6700013E
    move.l (a2),d6                                    ; +$001A : 2C12
    tst.l d6                                          ; +$001C : 4A86
    beq.w L_005918                                    ; +$001E : 67000136
    move.l 8(a2),d0                                   ; +$0022 : 202A0008
    tst.l d0                                          ; +$0026 : 4A80
    beq.w L_005918                                    ; +$0028 : 6700012C
    tst.l d7                                          ; +$002C : 4A87
    bne.w L_00583C                                    ; +$002E : 6600004A
    move.l a4,d0                                      ; +$0032 : 200C
    tst.l d0                                          ; +$0034 : 4A80
    beq.w L_00580A                                    ; +$0036 : 67000010
    move.l #$00000000,d0                              ; +$003A : 203C00000000
    move.w (a4),d0                                    ; +$0040 : 3014
    tst.l d0                                          ; +$0042 : 4A80
    bne.w L_005918                                    ; +$0044 : 66000110
L_00580A:
    movea.l d6,a0                                     ; +$0048 : 2046
    bsr.w L_005920                                    ; +$004A : 61000112
    tst.l d0                                          ; +$004E : 4A80
    beq.w L_005832                                    ; +$0050 : 6700001E
    lea L_005974(pc),a1                               ; +$0054 : 43FA015C
    move.l #$00000000,(a1)                            ; +$0058 : 22BC00000000
    move.l #$00000000,4(a1)                           ; +$005E : 237C000000000004
    movea.l d0,a1                                     ; +$0066 : 2240
    movea.l 8(a2),a6                                  ; +$0068 : 2C6A0008
    bsr.w L_005D18                                    ; +$006C : 610004E8
L_005832:
    move.l #$00000001,d3                              ; +$0070 : 263C00000001
    bra.w L_005918                                    ; +$0076 : 600000DE
L_00583C:
    cmpi.l #$000000FF,d7                              ; +$007A : 0C87000000FF
    bhi.w L_005918                                    ; +$0080 : 620000D4
    move.l a4,d0                                      ; +$0084 : 200C
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_005918                                    ; +$0088 : 670000CC
    move.l #$00000000,d5                              ; +$008C : 2A3C00000000
    move.w (a4),d5                                    ; +$0092 : 3A14
    tst.l d5                                          ; +$0094 : 4A85
    beq.w L_005918                                    ; +$0096 : 670000BE
    cmpi.l #$0000007F,d5                              ; +$009A : 0C850000007F
    bhi.w L_005918                                    ; +$00A0 : 620000B4
    lea -176(a7),a7                                   ; +$00A4 : 4FEFFF50
    lea 16(a7),a0                                     ; +$00A8 : 41EF0010
    movea.l a4,a1                                     ; +$00AC : 224C
    addq.l #2,a1                                      ; +$00AE : 5489
    move.l d5,d4                                      ; +$00B0 : 2805
    subq.l #1,d4                                      ; +$00B2 : 5384
L_005876:
    move.b (a1)+,d0                                   ; +$00B4 : 1019
    tst.b d0                                          ; +$00B6 : 4A00
    beq.w L_005914                                    ; +$00B8 : 67000098
    move.b d0,(a0)+                                   ; +$00BC : 10C0
    dbra d4,L_005876                                  ; +$00BE : 51CCFFF4
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
    beq.w L_005914                                    ; +$010C : 67000044
    movea.l d0,a6                                     ; +$0110 : 2C40
    movea.l a7,a0                                     ; +$0112 : 204F
    jsr -30(a6)                                       ; +$0114 : 4EAEFFE2
    move.l d0,d4                                      ; +$0118 : 2800
    movea.l a6,a1                                     ; +$011A : 224E
    movea.l $0004.w,a6                                ; +$011C : 2C780004
    jsr -414(a6)                                      ; +$0120 : 4EAEFE62
    tst.l d4                                          ; +$0124 : 4A84
    beq.w L_005914                                    ; +$0126 : 6700002A
    movea.l d6,a0                                     ; +$012A : 2046
    bsr.w L_005920                                    ; +$012C : 61000030
    move.l d0,d5                                      ; +$0130 : 2A00
    lea L_005974(pc),a1                               ; +$0132 : 43FA007E
    move.l d6,(a1)                                    ; +$0136 : 2286
    move.l d4,4(a1)                                   ; +$0138 : 23440004
    tst.l d5                                          ; +$013C : 4A85
    beq.w L_00590E                                    ; +$013E : 6700000C
    movea.l d5,a1                                     ; +$0142 : 2245
    movea.l 8(a2),a6                                  ; +$0144 : 2C6A0008
    bsr.w L_005D18                                    ; +$0148 : 6100040C
L_00590E:
    move.l #$00000001,d3                              ; +$014C : 263C00000001
L_005914:
    lea 176(a7),a7                                    ; +$0152 : 4FEF00B0
L_005918:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0156 : 4CDF77F7
    moveq #0,d2                                       ; +$015A : 7400
    rts                                               ; +$015C : 4E75
L_005920:
    lea L_005974(pc),a1                               ; +$015E : 43FA0052
    move.l (a1),d0                                    ; +$0162 : 2011
    move.l a0,d1                                      ; +$0164 : 2208
    cmp.l d1,d0                                       ; +$0166 : B081
    bne.w L_005934                                    ; +$0168 : 66000008
    move.l 4(a1),d0                                   ; +$016C : 20290004
    rts                                               ; +$0170 : 4E75
L_005934:
    move.l #$00000000,d0                              ; +$0172 : 203C00000000
    rts                                               ; +$0178 : 4E75
L_00593C:
    move.l a6,-(a7)                                   ; +$017A : 2F0E
    move.l a0,-(a7)                                   ; +$017C : 2F08
    move.l a2,-(a7)                                   ; +$017E : 2F0A
    bsr.w L_005920                                    ; +$0180 : 6100FFDC
    tst.l d0                                          ; +$0184 : 4A80
    beq.w L_005968                                    ; +$0186 : 6700001E
    lea L_005974(pc),a1                               ; +$018A : 43FA0026
    move.l #$00000000,(a1)                            ; +$018E : 22BC00000000
    move.l #$00000000,4(a1)                           ; +$0194 : 237C000000000004
    movea.l d0,a1                                     ; +$019C : 2240
    movea.l 8(a2),a6                                  ; +$019E : 2C6A0008
    bsr.w L_005D18                                    ; +$01A2 : 610003B2
L_005968:
    movea.l (a7)+,a2                                  ; +$01A6 : 245F
    movea.l (a7)+,a0                                  ; +$01A8 : 205F
    movea.l (a7)+,a6                                  ; +$01AA : 2C5F
    jsr -66(a6)                                       ; +$01AC : 4EAEFFBE
    rts                                               ; +$01B0 : 4E75
L_005974:
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
    beq.w L_005D0A                                    ; +$0016 : 67000372
    move.l (a2),d0                                    ; +$001A : 2012
    tst.l d0                                          ; +$001C : 4A80
    beq.w L_005D0A                                    ; +$001E : 6700036A
    move.l 8(a2),d0                                   ; +$0022 : 202A0008
    tst.l d0                                          ; +$0026 : 4A80
    beq.w L_005D0A                                    ; +$0028 : 67000360
    cmpi.l #$00000070,d7                              ; +$002C : 0C8700000070
    bcs.w L_005D0A                                    ; +$0032 : 65000356
    cmpi.l #$0000FFFF,d7                              ; +$0036 : 0C870000FFFF
    bhi.w L_005D0A                                    ; +$003C : 6200034C
    move.l d6,d0                                      ; +$0040 : 2006
    cmpi.l #$00000018,d0                              ; +$0042 : 0C8000000018
    bls.w L_005D0A                                    ; +$0048 : 63000340
    andi.l #$00000001,d0                              ; +$004C : 028000000001
    bne.w L_005D0A                                    ; +$0052 : 66000336
    movea.l d6,a4                                     ; +$0056 : 2846
    move.l d6,d0                                      ; +$0058 : 2006
    subi.l #$00000018,d0                              ; +$005A : 048000000018
    movea.l d0,a1                                     ; +$0060 : 2240
    movea.l $0004.w,a6                                ; +$0062 : 2C780004
    jsr -534(a6)                                      ; +$0066 : 4EAEFDEA
    tst.l d0                                          ; +$006A : 4A80
    beq.w L_005D0A                                    ; +$006C : 6700031C
    move.l d6,d0                                      ; +$0070 : 2006
    add.l d7,d0                                       ; +$0072 : D087
    bcs.w L_005D0A                                    ; +$0074 : 65000314
    subq.l #1,d0                                      ; +$0078 : 5380
    movea.l d0,a1                                     ; +$007A : 2240
    jsr -534(a6)                                      ; +$007C : 4EAEFDEA
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_005D0A                                    ; +$0082 : 67000306
    move.l -20(a4),d0                                 ; +$0086 : 202CFFEC
    move.l d7,d1                                      ; +$008A : 2207
    addi.l #$00000010,d1                              ; +$008C : 068100000010
    cmp.l d1,d0                                       ; +$0092 : B081
    bne.w L_005D0A                                    ; +$0094 : 660002F4
    move.l -16(a4),d0                                 ; +$0098 : 202CFFF0
    cmpi.l #$00000005,d0                              ; +$009C : 0C8000000005
    bcs.w L_005D0A                                    ; +$00A2 : 650002E6
    cmpi.l #$0000FFFF,d0                              ; +$00A6 : 0C800000FFFF
    bhi.w L_005D0A                                    ; +$00AC : 620002DC
    move.l #$00000000,d0                              ; +$00B0 : 203C00000000
    move.w -12(a4),d0                                 ; +$00B6 : 302CFFF4
    andi.w #$FFFC,d0                                  ; +$00BA : 0240FFFC
    tst.l d0                                          ; +$00BE : 4A80
    bne.w L_005D0A                                    ; +$00C0 : 660002C8
    move.l -8(a4),d0                                  ; +$00C4 : 202CFFF8
    cmpi.l #$42616E6B,d0                              ; +$00C8 : 0C8042616E6B
    bne.w L_005D0A                                    ; +$00CE : 660002BA
    move.l -4(a4),d0                                  ; +$00D2 : 202CFFFC
    cmpi.l #$466F6E74,d0                              ; +$00D6 : 0C80466F6E74
    bne.w L_005D0A                                    ; +$00DC : 660002AC
    move.l (a4),d0                                    ; +$00E0 : 2014
    cmpi.l #$464F4E54,d0                              ; +$00E2 : 0C80464F4E54
    bne.w L_005D0A                                    ; +$00E8 : 660002A0
    move.l #$00000000,d0                              ; +$00EC : 203C00000000
    move.b 32(a4),d0                                  ; +$00F2 : 102C0020
    cmpi.l #$0000000C,d0                              ; +$00F6 : 0C800000000C
    bne.w L_005D0A                                    ; +$00FC : 6600028C
    move.l #$00000000,d4                              ; +$0100 : 283C00000000
    move.w 10(a4),d4                                  ; +$0106 : 382C000A
    move.l #$00000000,d5                              ; +$010A : 2A3C00000000
    move.w 14(a4),d5                                  ; +$0110 : 3A2C000E
    cmpi.l #$0000004E,d4                              ; +$0114 : 0C840000004E
    bcs.w L_005D0A                                    ; +$011A : 6500026E
    cmp.l d4,d5                                       ; +$011E : BA84
    bls.w L_005D0A                                    ; +$0120 : 63000268
    cmp.l d7,d5                                       ; +$0124 : BA87
    bcc.w L_005D0A                                    ; +$0126 : 64000262
    move.l #$00000000,d0                              ; +$012A : 203C00000000
    move.w 44(a4),d0                                  ; +$0130 : 302C002C
    tst.l d0                                          ; +$0134 : 4A80
    beq.w L_005D0A                                    ; +$0136 : 67000252
    cmpi.l #$000000FF,d0                              ; +$013A : 0C80000000FF
    bhi.w L_005D0A                                    ; +$0140 : 62000248
    move.l #$00000000,d3                              ; +$0144 : 263C00000000
    move.w 48(a4),d3                                  ; +$014A : 362C0030
    tst.l d3                                          ; +$014E : 4A83
    beq.w L_005D0A                                    ; +$0150 : 67000238
    cmpi.l #$000000FF,d3                              ; +$0154 : 0C83000000FF
    bhi.w L_005D0A                                    ; +$015A : 6200022E
    move.l #$00000000,d1                              ; +$015E : 223C00000000
    move.w 50(a4),d1                                  ; +$0164 : 322C0032
    cmp.l d0,d1                                       ; +$0168 : B280
    bcc.w L_005D0A                                    ; +$016A : 6400021E
    move.l #$00000000,d1                              ; +$016E : 223C00000000
    move.b 46(a4),d1                                  ; +$0174 : 122C002E
    andi.b #$40,d1                                    ; +$0178 : 02010040
    tst.l d1                                          ; +$017C : 4A81
    bne.w L_005D0A                                    ; +$017E : 6600020A
    move.l 68(a4),d0                                  ; +$0182 : 202C0044
    tst.l d0                                          ; +$0186 : 4A80
    bne.w L_005D0A                                    ; +$0188 : 66000200
    move.l 72(a4),d0                                  ; +$018C : 202C0048
    tst.l d0                                          ; +$0190 : 4A80
    bne.w L_005D0A                                    ; +$0192 : 660001F6
    move.l #$00000000,d6                              ; +$0196 : 2C3C00000000
    move.b 57(a4),d6                                  ; +$019C : 1C2C0039
    move.l #$00000000,d0                              ; +$01A0 : 203C00000000
    move.b 56(a4),d0                                  ; +$01A6 : 102C0038
    sub.l d0,d6                                       ; +$01AA : 9C80
    bcs.w L_005D0A                                    ; +$01AC : 650001DC
    addq.l #2,d6                                      ; +$01B0 : 5486
    move.l d6,d0                                      ; +$01B2 : 2006
    lsl.l #2,d0                                       ; +$01B4 : E588
    add.l d5,d0                                       ; +$01B6 : D085
    bcs.w L_005D0A                                    ; +$01B8 : 650001D0
    move.l #$00000000,d1                              ; +$01BC : 223C00000000
    move.b 47(a4),d1                                  ; +$01C2 : 122C002F
    andi.b #$20,d1                                    ; +$01C6 : 02010020
    tst.b d1                                          ; +$01CA : 4A01
    beq.w L_005B5A                                    ; +$01CC : 6700000C
    move.l d6,d1                                      ; +$01D0 : 2206
    lsl.l #2,d1                                       ; +$01D2 : E589
    add.l d1,d0                                       ; +$01D4 : D081
    bcs.w L_005D0A                                    ; +$01D6 : 650001B2
L_005B5A:
    cmp.l d7,d0                                       ; +$01DA : B087
    bne.w L_005D0A                                    ; +$01DC : 660001AC
    move.l #$00000000,d1                              ; +$01E0 : 223C00000000
    move.w 62(a4),d1                                  ; +$01E6 : 322C003E
    tst.l d1                                          ; +$01EA : 4A81
    beq.w L_005D0A                                    ; +$01EC : 6700019C
    move.l d1,d2                                      ; +$01F0 : 2401
    andi.l #$00000001,d2                              ; +$01F2 : 028200000001
    bne.w L_005D0A                                    ; +$01F8 : 66000190
    move.l d1,d2                                      ; +$01FC : 2401
    lsl.l #3,d2                                       ; +$01FE : E78A
    move.l #$00000000,d0                              ; +$0200 : 203C00000000
    move.w 44(a4),d0                                  ; +$0206 : 302C002C
    mulu.w d1,d0                                      ; +$020A : C0C1
    move.l d5,d1                                      ; +$020C : 2205
    sub.l d4,d1                                       ; +$020E : 9284
    cmp.l d1,d0                                       ; +$0210 : B081
    bne.w L_005D0A                                    ; +$0212 : 66000176
    move.l d6,-(a7)                                   ; +$0216 : 2F06
    move.l d4,d1                                      ; +$0218 : 2204
    subi.l #$0000004C,d1                              ; +$021A : 04810000004C
    move.l a4,d0                                      ; +$0220 : 200C
    addi.l #$0000004C,d0                              ; +$0222 : 06800000004C
    movea.l d0,a1                                     ; +$0228 : 2240
    move.b (a1),d0                                    ; +$022A : 1011
    tst.b d0                                          ; +$022C : 4A00
    beq.w L_005BC6                                    ; +$022E : 67000016
L_005BB2:
    move.l #$00000000,d0                              ; +$0232 : 203C00000000
    move.b (a1)+,d0                                   ; +$0238 : 1019
    tst.b d0                                          ; +$023A : 4A00
    beq.w L_005BCC                                    ; +$023C : 6700000E
    subq.l #1,d1                                      ; +$0240 : 5381
    bne.w L_005BB2                                    ; +$0242 : 6600FFEE
L_005BC6:
    move.l (a7)+,d6                                   ; +$0246 : 2C1F
    bra.w L_005D0A                                    ; +$0248 : 60000140
L_005BCC:
    move.l (a7)+,d6                                   ; +$024C : 2C1F
    move.l a4,d0                                      ; +$024E : 200C
    add.l d5,d0                                       ; +$0250 : D085
    movea.l d0,a1                                     ; +$0252 : 2240
    move.l #$00000000,d0                              ; +$0254 : 203C00000000
    move.b 47(a4),d0                                  ; +$025A : 102C002F
    andi.b #$20,d0                                    ; +$025E : 02000020
    tst.b d0                                          ; +$0262 : 4A00
    beq.w L_005BEE                                    ; +$0264 : 67000008
    move.l #$00000100,d3                              ; +$0268 : 263C00000100
L_005BEE:
    move.l #$00000000,d0                              ; +$026E : 203C00000000
    move.w (a1)+,d0                                   ; +$0274 : 3019
    move.l #$00000000,d1                              ; +$0276 : 223C00000000
    move.w (a1)+,d1                                   ; +$027C : 3219
    cmp.l d3,d1                                       ; +$027E : B283
    bhi.w L_005D0A                                    ; +$0280 : 62000108
    add.l d1,d0                                       ; +$0284 : D081
    cmp.l d2,d0                                       ; +$0286 : B082
    bhi.w L_005D0A                                    ; +$0288 : 62000100
    subq.l #1,d6                                      ; +$028C : 5386
    bne.w L_005BEE                                    ; +$028E : 6600FFDE
    move.l a4,-(a7)                                   ; +$0292 : 2F0C
    move.l d7,d0                                      ; +$0294 : 2007
    move.l #$00010003,d1                              ; +$0296 : 223C00010003
    movea.l $0004.w,a6                                ; +$029C : 2C780004
    jsr -684(a6)                                      ; +$02A0 : 4EAEFD54
    tst.l d0                                          ; +$02A4 : 4A80
    bne.w L_005C30                                    ; +$02A6 : 66000008
    movea.l (a7)+,a0                                  ; +$02AA : 205F
    bra.w L_005D0A                                    ; +$02AC : 600000DC
L_005C30:
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
    bne.w L_005C8E                                    ; +$02F6 : 66000016
    move.l #$00000000,68(a4)                          ; +$02FA : 297C000000000044
    move.l #$00000000,72(a4)                          ; +$0302 : 297C000000000048
    bra.w L_005CBA                                    ; +$030A : 6000002E
L_005C8E:
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
L_005CBA:
    move.l #$00000000,d0                              ; +$033A : 203C00000000
    move.b 47(a4),d0                                  ; +$0340 : 102C002F
    andi.b #$FC,d0                                    ; +$0344 : 020000FC
    move.b d0,47(a4)                                  ; +$0348 : 1940002F
    lea L_005974(pc),a1                               ; +$034C : 43FAFCA6
    move.l 4(a1),d6                                   ; +$0350 : 2C290004
    tst.l d6                                          ; +$0354 : 4A86
    beq.w L_005CE4                                    ; +$0356 : 6700000C
    movea.l d6,a1                                     ; +$035A : 2246
    movea.l 8(a2),a6                                  ; +$035C : 2C6A0008
    bsr.w L_005D18                                    ; +$0360 : 61000036
L_005CE4:
    move.l a4,d0                                      ; +$0364 : 200C
    addi.l #$00000018,d0                              ; +$0366 : 068000000018
    lea L_005D6C(pc),a1                               ; +$036C : 43FA007E
    move.l d0,(a1)                                    ; +$0370 : 2280
    move.l a4,4(a1)                                   ; +$0372 : 234C0004
    lea L_005974(pc),a1                               ; +$0376 : 43FAFC7C
    move.l (a2),(a1)                                  ; +$037A : 2292
    move.l d0,4(a1)                                   ; +$037C : 23400004
    move.l #$00000001,d3                              ; +$0380 : 263C00000001
    bra.w L_005D10                                    ; +$0386 : 60000008
L_005D0A:
    move.l #$00000000,d3                              ; +$038A : 263C00000000
L_005D10:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0390 : 4CDF77F7
    moveq #0,d2                                       ; +$0394 : 7400
    rts                                               ; +$0396 : 4E75
L_005D18:
    move.l d0,-(a7)                                   ; +$0398 : 2F00
    move.l d1,-(a7)                                   ; +$039A : 2F01
    move.l a0,-(a7)                                   ; +$039C : 2F08
    move.l a2,-(a7)                                   ; +$039E : 2F0A
    move.l a6,-(a7)                                   ; +$03A0 : 2F0E
    move.l a1,d0                                      ; +$03A2 : 2009
    tst.l d0                                          ; +$03A4 : 4A80
    beq.w L_005D60                                    ; +$03A6 : 67000038
    lea L_005D6C(pc),a2                               ; +$03AA : 45FA0040
    cmp.l (a2),d0                                     ; +$03AE : B092
    bne.w L_005D5C                                    ; +$03B0 : 6600002A
    movea.l a1,a0                                     ; +$03B4 : 2049
    jsr -822(a6)                                      ; +$03B6 : 4EAEFCCA
    lea L_005D6C(pc),a2                               ; +$03BA : 45FA0030
    movea.l 4(a2),a1                                  ; +$03BE : 226A0004
    move.l #$00000000,(a2)                            ; +$03C2 : 24BC00000000
    move.l #$00000000,4(a2)                           ; +$03C8 : 257C000000000004
    movea.l $0004.w,a6                                ; +$03D0 : 2C780004
    jsr -690(a6)                                      ; +$03D4 : 4EAEFD4E
    bra.w L_005D60                                    ; +$03D8 : 60000006
L_005D5C:
    jsr -78(a6)                                       ; +$03DC : 4EAEFFB2
L_005D60:
    movea.l (a7)+,a6                                  ; +$03E0 : 2C5F
    movea.l (a7)+,a2                                  ; +$03E2 : 245F
    movea.l (a7)+,a0                                  ; +$03E4 : 205F
    move.l (a7)+,d1                                   ; +$03E6 : 221F
    move.l (a7)+,d0                                   ; +$03E8 : 201F
    rts                                               ; +$03EA : 4E75
L_005D6C:
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
    bmi.w L_005F2C                                    ; +$0012 : 6B0001A0
    tst.l d6                                          ; +$0016 : 4A86
    bmi.w L_005F2C                                    ; +$0018 : 6B00019A
    tst.l d7                                          ; +$001C : 4A87
    bmi.w L_005F2C                                    ; +$001E : 6B000194
    movea.l 456(a5),a4                                ; +$0022 : 286D01C8
    move.l a4,d0                                      ; +$0026 : 200C
    tst.l d0                                          ; +$0028 : 4A80
    beq.w L_005F2C                                    ; +$002A : 67000188
    move.l (a4),d0                                    ; +$002E : 2014
    tst.l d0                                          ; +$0030 : 4A80
    beq.w L_005F2C                                    ; +$0032 : 67000180
    move.l 8(a4),d0                                   ; +$0036 : 202C0008
    tst.l d0                                          ; +$003A : 4A80
    beq.w L_005F2C                                    ; +$003C : 67000176
    move.l 32(a4),d0                                  ; +$0040 : 202C0020
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_005F2C                                    ; +$0046 : 6700016C
    move.l 12(a4),d0                                  ; +$004A : 202C000C
    tst.l d0                                          ; +$004E : 4A80
    ble.w L_005F2C                                    ; +$0050 : 6F000162
    cmpi.l #$00007FFF,d0                              ; +$0054 : 0C8000007FFF
    bgt.w L_005F2C                                    ; +$005A : 6E000158
    cmp.l d0,d5                                       ; +$005E : BA80
    bge.w L_005F2C                                    ; +$0060 : 6C000152
    move.l 16(a4),d0                                  ; +$0064 : 202C0010
    tst.l d0                                          ; +$0068 : 4A80
    ble.w L_005F2C                                    ; +$006A : 6F000148
    cmpi.l #$00007FFF,d0                              ; +$006E : 0C8000007FFF
    bgt.w L_005F2C                                    ; +$0074 : 6E00013E
    cmp.l d0,d6                                       ; +$0078 : BC80
    bge.w L_005F2C                                    ; +$007A : 6C000138
    move.l 28(a4),d0                                  ; +$007E : 202C001C
    tst.l d0                                          ; +$0082 : 4A80
    ble.w L_005F2C                                    ; +$0084 : 6F00012E
    cmpi.l #$00000008,d0                              ; +$0088 : 0C8000000008
    bgt.w L_005F2C                                    ; +$008E : 6E000124
    move.l #$00000001,d1                              ; +$0092 : 223C00000001
L_005E10:
    lsl.l #1,d1                                       ; +$0098 : E389
    subq.l #1,d0                                      ; +$009A : 5380
    bne.w L_005E10                                    ; +$009C : 6600FFFA
    cmp.l d1,d7                                       ; +$00A0 : BE81
    bcc.w L_005F2C                                    ; +$00A2 : 64000110
    movea.l 32(a4),a2                                 ; +$00A6 : 246C0020
    move.l 8(a2),d0                                   ; +$00AA : 202A0008
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_005E3C                                    ; +$00B0 : 67000012
    cmpi.l #$00000001,d0                              ; +$00B4 : 0C8000000001
    bne.w L_005F2C                                    ; +$00BA : 660000F8
    movea.l (a2),a0                                   ; +$00BE : 2052
    bra.w L_005E40                                    ; +$00C0 : 60000006
L_005E3C:
    movea.l 4(a2),a0                                  ; +$00C4 : 206A0004
L_005E40:
    move.l a0,d0                                      ; +$00C8 : 2008
    tst.l d0                                          ; +$00CA : 4A80
    beq.w L_005F2C                                    ; +$00CC : 670000E6
    movea.l (a0),a0                                   ; +$00D0 : 2050
    move.l a0,d0                                      ; +$00D2 : 2008
    tst.l d0                                          ; +$00D4 : 4A80
    beq.w L_005F2C                                    ; +$00D6 : 670000DC
    move.l a0,d2                                      ; +$00DA : 2408
    move.l #$00000000,d1                              ; +$00DC : 223C00000000
    move.w (a0),d1                                    ; +$00E2 : 3210
    lsl.l #3,d1                                       ; +$00E4 : E789
    cmp.l 12(a4),d1                                   ; +$00E6 : B2AC000C
    blt.w L_005F2C                                    ; +$00EA : 6D0000C8
    move.l #$00000000,d1                              ; +$00EE : 223C00000000
    move.w 2(a0),d1                                   ; +$00F4 : 32280002
    cmp.l 16(a4),d1                                   ; +$00F8 : B2AC0010
    blt.w L_005F2C                                    ; +$00FC : 6D0000B6
    move.l #$00000000,d1                              ; +$0100 : 223C00000000
    move.b 5(a0),d1                                   ; +$0106 : 12280005
    cmp.l 28(a4),d1                                   ; +$010A : B2AC001C
    bne.w L_005F2C                                    ; +$010E : 660000A4
    move.l d1,d0                                      ; +$0112 : 2001
    movea.l a0,a1                                     ; +$0114 : 2248
    addq.l #8,a1                                      ; +$0116 : 5089
L_005E90:
    move.l (a1)+,d1                                   ; +$0118 : 2219
    tst.l d1                                          ; +$011A : 4A81
    beq.w L_005F2C                                    ; +$011C : 67000096
    cmpi.l #$FFFFFFFF,d1                              ; +$0120 : 0C81FFFFFFFF
    beq.w L_005F2C                                    ; +$0126 : 6700008C
    subq.l #1,d0                                      ; +$012A : 5380
    bne.w L_005E90                                    ; +$012C : 6600FFEA
    movea.l 32(a4),a0                                 ; +$0130 : 206C0020
    move.l 20(a0),d0                                  ; +$0134 : 20280014
    andi.l #$00000001,d0                              ; +$0138 : 028000000001
    beq.w L_005EE6                                    ; +$013E : 6700002E
    movea.l 12(a0),a0                                 ; +$0142 : 2068000C
    move.l a0,d0                                      ; +$0146 : 2008
    tst.l d0                                          ; +$0148 : 4A80
    beq.w L_005F2C                                    ; +$014A : 67000068
    movea.l $0004.w,a6                                ; +$014E : 2C780004
    jsr -372(a6)                                      ; +$0152 : 4EAEFE8C
    tst.l d0                                          ; +$0156 : 4A80
    beq.w L_005F2C                                    ; +$0158 : 6700005A
    movea.l 32(a4),a0                                 ; +$015C : 206C0020
    move.l 20(a0),d0                                  ; +$0160 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0164 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$016A : 21400014
L_005EE6:
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
    bne.w L_005F24                                    ; +$01A2 : 66000008
    move.l #$00000001,d3                              ; +$01A6 : 263C00000001
L_005F24:
    jsr -228(a6)                                      ; +$01AC : 4EAEFF1C
    lea 128(a7),a7                                    ; +$01B0 : 4FEF0080
L_005F2C:
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
    bgt.w L_0062DC                                    ; +$001E : 6E000384
    cmpi.l #$FFFF8000,d2                              ; +$0022 : 0C82FFFF8000
    blt.w L_0062DC                                    ; +$0028 : 6D00037A
    cmpi.l #$00007FFF,d4                              ; +$002C : 0C8400007FFF
    bgt.w L_0062DC                                    ; +$0032 : 6E000370
    cmpi.l #$FFFF8000,d4                              ; +$0036 : 0C84FFFF8000
    blt.w L_0062DC                                    ; +$003C : 6D000366
    cmpi.l #$00007FFF,d5                              ; +$0040 : 0C8500007FFF
    bgt.w L_0062DC                                    ; +$0046 : 6E00035C
    cmpi.l #$FFFF8000,d5                              ; +$004A : 0C85FFFF8000
    blt.w L_0062DC                                    ; +$0050 : 6D000352
    cmpi.l #$00007FFF,d6                              ; +$0054 : 0C8600007FFF
    bgt.w L_0062DC                                    ; +$005A : 6E000348
    cmpi.l #$FFFF8000,d6                              ; +$005E : 0C86FFFF8000
    blt.w L_0062DC                                    ; +$0064 : 6D00033E
    tst.l d7                                          ; +$0068 : 4A87
    bmi.w L_0062DC                                    ; +$006A : 6B000338
    movea.l 456(a5),a4                                ; +$006E : 286D01C8
    move.l a4,d0                                      ; +$0072 : 200C
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_0062DC                                    ; +$0076 : 6700032C
    move.l (a4),d0                                    ; +$007A : 2014
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_0062DC                                    ; +$007E : 67000324
    move.l 8(a4),d0                                   ; +$0082 : 202C0008
    tst.l d0                                          ; +$0086 : 4A80
    beq.w L_0062DC                                    ; +$0088 : 6700031A
    move.l 32(a4),d0                                  ; +$008C : 202C0020
    tst.l d0                                          ; +$0090 : 4A80
    beq.w L_0062DC                                    ; +$0092 : 67000310
    move.l 12(a4),d0                                  ; +$0096 : 202C000C
    tst.l d0                                          ; +$009A : 4A80
    ble.w L_0062DC                                    ; +$009C : 6F000306
    cmpi.l #$00007FFF,d0                              ; +$00A0 : 0C8000007FFF
    bgt.w L_0062DC                                    ; +$00A6 : 6E0002FC
    move.l 16(a4),d0                                  ; +$00AA : 202C0010
    tst.l d0                                          ; +$00AE : 4A80
    ble.w L_0062DC                                    ; +$00B0 : 6F0002F2
    cmpi.l #$00007FFF,d0                              ; +$00B4 : 0C8000007FFF
    bgt.w L_0062DC                                    ; +$00BA : 6E0002E8
    move.l 28(a4),d0                                  ; +$00BE : 202C001C
    tst.l d0                                          ; +$00C2 : 4A80
    ble.w L_0062DC                                    ; +$00C4 : 6F0002DE
    cmpi.l #$00000008,d0                              ; +$00C8 : 0C8000000008
    bgt.w L_0062DC                                    ; +$00CE : 6E0002D4
    move.l #$00000001,d1                              ; +$00D2 : 223C00000001
L_006010:
    lsl.l #1,d1                                       ; +$00D8 : E389
    subq.l #1,d0                                      ; +$00DA : 5380
    bne.w L_006010                                    ; +$00DC : 6600FFFA
    cmp.l d1,d7                                       ; +$00E0 : BE81
    bcc.w L_0062DC                                    ; +$00E2 : 640002C0
    tst.l d2                                          ; +$00E6 : 4A82
    bpl.w L_00602A                                    ; +$00E8 : 6A000008
    tst.l d5                                          ; +$00EC : 4A85
    bmi.w L_0062DC                                    ; +$00EE : 6B0002B4
L_00602A:
    cmp.l 12(a4),d2                                   ; +$00F2 : B4AC000C
    blt.w L_00603A                                    ; +$00F6 : 6D00000A
    cmp.l 12(a4),d5                                   ; +$00FA : BAAC000C
    bge.w L_0062DC                                    ; +$00FE : 6C0002A4
L_00603A:
    tst.l d4                                          ; +$0102 : 4A84
    bpl.w L_006046                                    ; +$0104 : 6A000008
    tst.l d6                                          ; +$0108 : 4A86
    bmi.w L_0062DC                                    ; +$010A : 6B000298
L_006046:
    cmp.l 16(a4),d4                                   ; +$010E : B8AC0010
    blt.w L_006056                                    ; +$0112 : 6D00000A
    cmp.l 16(a4),d6                                   ; +$0116 : BCAC0010
    bge.w L_0062DC                                    ; +$011A : 6C000288
L_006056:
    movea.l 32(a4),a2                                 ; +$011E : 246C0020
    move.l 8(a2),d0                                   ; +$0122 : 202A0008
    tst.l d0                                          ; +$0126 : 4A80
    beq.w L_006074                                    ; +$0128 : 67000012
    cmpi.l #$00000001,d0                              ; +$012C : 0C8000000001
    bne.w L_0062DC                                    ; +$0132 : 66000270
    movea.l (a2),a0                                   ; +$0136 : 2052
    bra.w L_006078                                    ; +$0138 : 60000006
L_006074:
    movea.l 4(a2),a0                                  ; +$013C : 206A0004
L_006078:
    move.l a0,d0                                      ; +$0140 : 2008
    tst.l d0                                          ; +$0142 : 4A80
    beq.w L_0062DC                                    ; +$0144 : 6700025E
    movea.l (a0),a0                                   ; +$0148 : 2050
    move.l a0,d0                                      ; +$014A : 2008
    tst.l d0                                          ; +$014C : 4A80
    beq.w L_0062DC                                    ; +$014E : 67000254
    movea.l a0,a2                                     ; +$0152 : 2448
    move.l #$00000000,d1                              ; +$0154 : 223C00000000
    move.w (a0),d1                                    ; +$015A : 3210
    lsl.l #3,d1                                       ; +$015C : E789
    cmp.l 12(a4),d1                                   ; +$015E : B2AC000C
    blt.w L_0062DC                                    ; +$0162 : 6D000240
    move.l #$00000000,d1                              ; +$0166 : 223C00000000
    move.w 2(a0),d1                                   ; +$016C : 32280002
    cmp.l 16(a4),d1                                   ; +$0170 : B2AC0010
    blt.w L_0062DC                                    ; +$0174 : 6D00022E
    move.l #$00000000,d1                              ; +$0178 : 223C00000000
    move.b 5(a0),d1                                   ; +$017E : 12280005
    cmp.l 28(a4),d1                                   ; +$0182 : B2AC001C
    bne.w L_0062DC                                    ; +$0186 : 6600021C
    move.l d1,d0                                      ; +$018A : 2001
    movea.l a0,a1                                     ; +$018C : 2248
    addq.l #8,a1                                      ; +$018E : 5089
L_0060C8:
    move.l (a1)+,d1                                   ; +$0190 : 2219
    tst.l d1                                          ; +$0192 : 4A81
    beq.w L_0062DC                                    ; +$0194 : 6700020E
    cmpi.l #$FFFFFFFF,d1                              ; +$0198 : 0C81FFFFFFFF
    beq.w L_0062DC                                    ; +$019E : 67000204
    subq.l #1,d0                                      ; +$01A2 : 5380
    bne.w L_0060C8                                    ; +$01A4 : 6600FFEA
    move.l a2,156(a7)                                 ; +$01A8 : 2F4A009C
    tst.l d2                                          ; +$01AC : 4A82
    bmi.w L_006128                                    ; +$01AE : 6B000040
    cmp.l 12(a4),d2                                   ; +$01B2 : B4AC000C
    bge.w L_006128                                    ; +$01B6 : 6C000038
    tst.l d5                                          ; +$01BA : 4A85
    bmi.w L_006128                                    ; +$01BC : 6B000032
    cmp.l 12(a4),d5                                   ; +$01C0 : BAAC000C
    bge.w L_006128                                    ; +$01C4 : 6C00002A
    tst.l d4                                          ; +$01C8 : 4A84
    bmi.w L_006128                                    ; +$01CA : 6B000024
    cmp.l 16(a4),d4                                   ; +$01CE : B8AC0010
    bge.w L_006128                                    ; +$01D2 : 6C00001C
    tst.l d6                                          ; +$01D6 : 4A86
    bmi.w L_006128                                    ; +$01D8 : 6B000016
    cmp.l 16(a4),d6                                   ; +$01DC : BCAC0010
    bge.w L_006128                                    ; +$01E0 : 6C00000E
    move.l #$00000001,152(a7)                         ; +$01E4 : 2F7C000000010098
    bra.w L_006130                                    ; +$01EC : 6000000A
L_006128:
    move.l #$00000000,152(a7)                         ; +$01F0 : 2F7C000000000098
L_006130:
    movea.l 32(a4),a0                                 ; +$01F8 : 206C0020
    move.l 20(a0),d0                                  ; +$01FC : 20280014
    andi.l #$00000001,d0                              ; +$0200 : 028000000001
    beq.w L_00616E                                    ; +$0206 : 6700002E
    movea.l 12(a0),a0                                 ; +$020A : 2068000C
    move.l a0,d0                                      ; +$020E : 2008
    tst.l d0                                          ; +$0210 : 4A80
    beq.w L_0062DC                                    ; +$0212 : 67000190
    movea.l $0004.w,a6                                ; +$0216 : 2C780004
    jsr -372(a6)                                      ; +$021A : 4EAEFE8C
    tst.l d0                                          ; +$021E : 4A80
    beq.w L_0062DC                                    ; +$0220 : 67000182
    movea.l 32(a4),a0                                 ; +$0224 : 206C0020
    move.l 20(a0),d0                                  ; +$0228 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$022C : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$0232 : 21400014
L_00616E:
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
    beq.w L_0061E0                                    ; +$0260 : 67000046
    cmp.l d5,d2                                       ; +$0264 : B485
    bne.w L_0061C2                                    ; +$0266 : 66000022
    cmp.l d6,d4                                       ; +$026A : B886
    bne.w L_0061C2                                    ; +$026C : 6600001C
    movea.l a2,a1                                     ; +$0270 : 224A
    move.l d2,d0                                      ; +$0272 : 2002
    move.l d4,d1                                      ; +$0274 : 2204
    jsr -324(a6)                                      ; +$0276 : 4EAEFEBC
    tst.l d0                                          ; +$027A : 4A80
    bne.w L_0062D0                                    ; +$027C : 6600011A
    move.l #$00000001,d3                              ; +$0280 : 263C00000001
    bra.w L_0062D0                                    ; +$0286 : 60000110
L_0061C2:
    movea.l a2,a1                                     ; +$028A : 224A
    move.l d2,d0                                      ; +$028C : 2002
    move.l d4,d1                                      ; +$028E : 2204
    jsr -240(a6)                                      ; +$0290 : 4EAEFF10
    movea.l a2,a1                                     ; +$0294 : 224A
    move.l d5,d0                                      ; +$0296 : 2005
    move.l d6,d1                                      ; +$0298 : 2206
    jsr -246(a6)                                      ; +$029A : 4EAEFF0A
    move.l #$00000001,d3                              ; +$029E : 263C00000001
    bra.w L_0062D0                                    ; +$02A4 : 600000F2
L_0061E0:
    move.l d5,d0                                      ; +$02A8 : 2005
    sub.l d2,d0                                       ; +$02AA : 9082
    move.l #$00000001,136(a7)                         ; +$02AC : 2F7C000000010088
    tst.l d0                                          ; +$02B4 : 4A80
    bpl.w L_006204                                    ; +$02B6 : 6A000014
    move.l #$FFFFFFFF,136(a7)                         ; +$02BA : 2F7CFFFFFFFF0088
    move.l #$00000000,d1                              ; +$02C2 : 223C00000000
    sub.l d0,d1                                       ; +$02C8 : 9280
    move.l d1,d0                                      ; +$02CA : 2001
L_006204:
    move.l d0,128(a7)                                 ; +$02CC : 2F400080
    move.l d6,d0                                      ; +$02D0 : 2006
    sub.l d4,d0                                       ; +$02D2 : 9084
    move.l #$00000001,140(a7)                         ; +$02D4 : 2F7C00000001008C
    tst.l d0                                          ; +$02DC : 4A80
    bpl.w L_00622C                                    ; +$02DE : 6A000014
    move.l #$FFFFFFFF,140(a7)                         ; +$02E2 : 2F7CFFFFFFFF008C
    move.l #$00000000,d1                              ; +$02EA : 223C00000000
    sub.l d0,d1                                       ; +$02F0 : 9280
    move.l d1,d0                                      ; +$02F2 : 2001
L_00622C:
    move.l d0,132(a7)                                 ; +$02F4 : 2F400084
    move.l 128(a7),d0                                 ; +$02F8 : 202F0080
    sub.l 132(a7),d0                                  ; +$02FC : 90AF0084
    move.l d0,144(a7)                                 ; +$0300 : 2F400090
L_00623C:
    tst.l d2                                          ; +$0304 : 4A82
    bmi.w L_006276                                    ; +$0306 : 6B000036
    cmp.l 12(a4),d2                                   ; +$030A : B4AC000C
    bge.w L_006276                                    ; +$030E : 6C00002E
    tst.l d4                                          ; +$0312 : 4A84
    bmi.w L_006276                                    ; +$0314 : 6B000028
    cmp.l 16(a4),d4                                   ; +$0318 : B8AC0010
    bge.w L_006276                                    ; +$031C : 6C000020
    movea.l a2,a1                                     ; +$0320 : 224A
    move.l d2,d0                                      ; +$0322 : 2002
    move.l d4,d1                                      ; +$0324 : 2204
    move.l #$00000002,152(a7)                         ; +$0326 : 2F7C000000020098
    jsr -324(a6)                                      ; +$032E : 4EAEFEBC
    tst.l d0                                          ; +$0332 : 4A80
    bne.w L_006276                                    ; +$0334 : 66000008
    move.l #$00000001,d3                              ; +$0338 : 263C00000001
L_006276:
    cmp.l d5,d2                                       ; +$033E : B485
    bne.w L_006282                                    ; +$0340 : 66000008
    cmp.l d6,d4                                       ; +$0344 : B886
    beq.w L_0062D0                                    ; +$0346 : 67000050
L_006282:
    move.l 144(a7),d0                                 ; +$034A : 202F0090
    lsl.l #1,d0                                       ; +$034E : E388
    move.l d0,148(a7)                                 ; +$0350 : 2F400094
    move.l #$00000000,d1                              ; +$0354 : 223C00000000
    sub.l 132(a7),d1                                  ; +$035A : 92AF0084
    cmp.l d1,d0                                       ; +$035E : B081
    ble.w L_0062AE                                    ; +$0360 : 6F000014
    move.l 144(a7),d0                                 ; +$0364 : 202F0090
    sub.l 132(a7),d0                                  ; +$0368 : 90AF0084
    move.l d0,144(a7)                                 ; +$036C : 2F400090
    move.l 136(a7),d0                                 ; +$0370 : 202F0088
    add.l d0,d2                                       ; +$0374 : D480
L_0062AE:
    move.l 148(a7),d0                                 ; +$0376 : 202F0094
    cmp.l 128(a7),d0                                  ; +$037A : B0AF0080
    bge.w L_0062CC                                    ; +$037E : 6C000014
    move.l 144(a7),d0                                 ; +$0382 : 202F0090
    add.l 128(a7),d0                                  ; +$0386 : D0AF0080
    move.l d0,144(a7)                                 ; +$038A : 2F400090
    move.l 140(a7),d0                                 ; +$038E : 202F008C
    add.l d0,d4                                       ; +$0392 : D880
L_0062CC:
    bra.w L_00623C                                    ; +$0394 : 6000FF6E
L_0062D0:
    tst.l 152(a7)                                     ; +$0398 : 4AAF0098
    beq.w L_0062DC                                    ; +$039C : 67000006
    jsr -228(a6)                                      ; +$03A0 : 4EAEFF1C
L_0062DC:
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
    bgt.w L_006700                                    ; +$001E : 6E0003F4
    cmpi.l #$FFFF8000,d2                              ; +$0022 : 0C82FFFF8000
    blt.w L_006700                                    ; +$0028 : 6D0003EA
    cmpi.l #$00007FFF,d4                              ; +$002C : 0C8400007FFF
    bgt.w L_006700                                    ; +$0032 : 6E0003E0
    cmpi.l #$FFFF8000,d4                              ; +$0036 : 0C84FFFF8000
    blt.w L_006700                                    ; +$003C : 6D0003D6
    cmpi.l #$00007FFF,d5                              ; +$0040 : 0C8500007FFF
    bgt.w L_006700                                    ; +$0046 : 6E0003CC
    cmpi.l #$FFFF8000,d5                              ; +$004A : 0C85FFFF8000
    blt.w L_006700                                    ; +$0050 : 6D0003C2
    cmpi.l #$00007FFF,d6                              ; +$0054 : 0C8600007FFF
    bgt.w L_006700                                    ; +$005A : 6E0003B8
    cmpi.l #$FFFF8000,d6                              ; +$005E : 0C86FFFF8000
    blt.w L_006700                                    ; +$0064 : 6D0003AE
    tst.l d7                                          ; +$0068 : 4A87
    bmi.w L_006700                                    ; +$006A : 6B0003A8
    cmp.l d5,d2                                       ; +$006E : B485
    ble.w L_006366                                    ; +$0070 : 6F000008
    move.l d2,d0                                      ; +$0074 : 2002
    move.l d5,d2                                      ; +$0076 : 2405
    move.l d0,d5                                      ; +$0078 : 2A00
L_006366:
    cmp.l d6,d4                                       ; +$007A : B886
    ble.w L_006372                                    ; +$007C : 6F000008
    move.l d4,d0                                      ; +$0080 : 2004
    move.l d6,d4                                      ; +$0082 : 2806
    move.l d0,d6                                      ; +$0084 : 2C00
L_006372:
    movea.l 456(a5),a4                                ; +$0086 : 286D01C8
    move.l a4,d0                                      ; +$008A : 200C
    tst.l d0                                          ; +$008C : 4A80
    beq.w L_006700                                    ; +$008E : 67000384
    move.l (a4),d0                                    ; +$0092 : 2014
    tst.l d0                                          ; +$0094 : 4A80
    beq.w L_006700                                    ; +$0096 : 6700037C
    move.l 8(a4),d0                                   ; +$009A : 202C0008
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_006700                                    ; +$00A0 : 67000372
    move.l 32(a4),d0                                  ; +$00A4 : 202C0020
    tst.l d0                                          ; +$00A8 : 4A80
    beq.w L_006700                                    ; +$00AA : 67000368
    move.l 12(a4),d0                                  ; +$00AE : 202C000C
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_006700                                    ; +$00B4 : 6F00035E
    cmpi.l #$00007FFF,d0                              ; +$00B8 : 0C8000007FFF
    bgt.w L_006700                                    ; +$00BE : 6E000354
    move.l 16(a4),d0                                  ; +$00C2 : 202C0010
    tst.l d0                                          ; +$00C6 : 4A80
    ble.w L_006700                                    ; +$00C8 : 6F00034A
    cmpi.l #$00007FFF,d0                              ; +$00CC : 0C8000007FFF
    bgt.w L_006700                                    ; +$00D2 : 6E000340
    move.l 28(a4),d0                                  ; +$00D6 : 202C001C
    tst.l d0                                          ; +$00DA : 4A80
    ble.w L_006700                                    ; +$00DC : 6F000336
    cmpi.l #$00000008,d0                              ; +$00E0 : 0C8000000008
    bgt.w L_006700                                    ; +$00E6 : 6E00032C
    move.l #$00000001,d1                              ; +$00EA : 223C00000001
L_0063DC:
    lsl.l #1,d1                                       ; +$00F0 : E389
    subq.l #1,d0                                      ; +$00F2 : 5380
    bne.w L_0063DC                                    ; +$00F4 : 6600FFFA
    cmp.l d1,d7                                       ; +$00F8 : BE81
    bcc.w L_006700                                    ; +$00FA : 64000318
    tst.l d5                                          ; +$00FE : 4A85
    bmi.w L_006700                                    ; +$0100 : 6B000312
    cmp.l 12(a4),d2                                   ; +$0104 : B4AC000C
    bge.w L_006700                                    ; +$0108 : 6C00030A
    tst.l d6                                          ; +$010C : 4A86
    bmi.w L_006700                                    ; +$010E : 6B000304
    cmp.l 16(a4),d4                                   ; +$0112 : B8AC0010
    bge.w L_006700                                    ; +$0116 : 6C0002FC
    movea.l 32(a4),a2                                 ; +$011A : 246C0020
    move.l 8(a2),d0                                   ; +$011E : 202A0008
    tst.l d0                                          ; +$0122 : 4A80
    beq.w L_006424                                    ; +$0124 : 67000012
    cmpi.l #$00000001,d0                              ; +$0128 : 0C8000000001
    bne.w L_006700                                    ; +$012E : 660002E4
    movea.l (a2),a0                                   ; +$0132 : 2052
    bra.w L_006428                                    ; +$0134 : 60000006
L_006424:
    movea.l 4(a2),a0                                  ; +$0138 : 206A0004
L_006428:
    move.l a0,d0                                      ; +$013C : 2008
    tst.l d0                                          ; +$013E : 4A80
    beq.w L_006700                                    ; +$0140 : 670002D2
    movea.l (a0),a0                                   ; +$0144 : 2050
    move.l a0,d0                                      ; +$0146 : 2008
    tst.l d0                                          ; +$0148 : 4A80
    beq.w L_006700                                    ; +$014A : 670002C8
    movea.l a0,a2                                     ; +$014E : 2448
    move.l #$00000000,d1                              ; +$0150 : 223C00000000
    move.w (a0),d1                                    ; +$0156 : 3210
    lsl.l #3,d1                                       ; +$0158 : E789
    cmp.l 12(a4),d1                                   ; +$015A : B2AC000C
    blt.w L_006700                                    ; +$015E : 6D0002B4
    move.l #$00000000,d1                              ; +$0162 : 223C00000000
    move.w 2(a0),d1                                   ; +$0168 : 32280002
    cmp.l 16(a4),d1                                   ; +$016C : B2AC0010
    blt.w L_006700                                    ; +$0170 : 6D0002A2
    move.l #$00000000,d1                              ; +$0174 : 223C00000000
    move.b 5(a0),d1                                   ; +$017A : 12280005
    cmp.l 28(a4),d1                                   ; +$017E : B2AC001C
    bne.w L_006700                                    ; +$0182 : 66000290
    move.l d1,d0                                      ; +$0186 : 2001
    movea.l a0,a1                                     ; +$0188 : 2248
    addq.l #8,a1                                      ; +$018A : 5089
L_006478:
    move.l (a1)+,d1                                   ; +$018C : 2219
    tst.l d1                                          ; +$018E : 4A81
    beq.w L_006700                                    ; +$0190 : 67000282
    cmpi.l #$FFFFFFFF,d1                              ; +$0194 : 0C81FFFFFFFF
    beq.w L_006700                                    ; +$019A : 67000278
    subq.l #1,d0                                      ; +$019E : 5380
    bne.w L_006478                                    ; +$01A0 : 6600FFEA
    move.l a2,156(a7)                                 ; +$01A4 : 2F4A009C
    move.l d2,128(a7)                                 ; +$01A8 : 2F420080
    tst.l d2                                          ; +$01AC : 4A82
    bpl.w L_0064A6                                    ; +$01AE : 6A00000A
    move.l #$00000000,128(a7)                         ; +$01B2 : 2F7C000000000080
L_0064A6:
    move.l d5,132(a7)                                 ; +$01BA : 2F450084
    cmp.l 12(a4),d5                                   ; +$01BE : BAAC000C
    blt.w L_0064BC                                    ; +$01C2 : 6D00000C
    move.l 12(a4),d0                                  ; +$01C6 : 202C000C
    subq.l #1,d0                                      ; +$01CA : 5380
    move.l d0,132(a7)                                 ; +$01CC : 2F400084
L_0064BC:
    move.l d4,136(a7)                                 ; +$01D0 : 2F440088
    tst.l d4                                          ; +$01D4 : 4A84
    bpl.w L_0064CE                                    ; +$01D6 : 6A00000A
    move.l #$00000000,136(a7)                         ; +$01DA : 2F7C000000000088
L_0064CE:
    move.l d6,140(a7)                                 ; +$01E2 : 2F46008C
    cmp.l 16(a4),d6                                   ; +$01E6 : BCAC0010
    blt.w L_0064E4                                    ; +$01EA : 6D00000C
    move.l 16(a4),d0                                  ; +$01EE : 202C0010
    subq.l #1,d0                                      ; +$01F2 : 5380
    move.l d0,140(a7)                                 ; +$01F4 : 2F40008C
L_0064E4:
    move.l #$00000000,152(a7)                         ; +$01F8 : 2F7C000000000098
    tst.l d2                                          ; +$0200 : 4A82
    bmi.w L_006502                                    ; +$0202 : 6B000012
    cmp.l 12(a4),d2                                   ; +$0206 : B4AC000C
    bge.w L_006502                                    ; +$020A : 6C00000A
    move.l #$00000001,152(a7)                         ; +$020E : 2F7C000000010098
L_006502:
    tst.l d5                                          ; +$0216 : 4A85
    bmi.w L_006518                                    ; +$0218 : 6B000012
    cmp.l 12(a4),d5                                   ; +$021C : BAAC000C
    bge.w L_006518                                    ; +$0220 : 6C00000A
    move.l #$00000001,152(a7)                         ; +$0224 : 2F7C000000010098
L_006518:
    tst.l d4                                          ; +$022C : 4A84
    bmi.w L_00652E                                    ; +$022E : 6B000012
    cmp.l 16(a4),d4                                   ; +$0232 : B8AC0010
    bge.w L_00652E                                    ; +$0236 : 6C00000A
    move.l #$00000001,152(a7)                         ; +$023A : 2F7C000000010098
L_00652E:
    tst.l d6                                          ; +$0242 : 4A86
    bmi.w L_006544                                    ; +$0244 : 6B000012
    cmp.l 16(a4),d6                                   ; +$0248 : BCAC0010
    bge.w L_006544                                    ; +$024C : 6C00000A
    move.l #$00000001,152(a7)                         ; +$0250 : 2F7C000000010098
L_006544:
    tst.l 152(a7)                                     ; +$0258 : 4AAF0098
    beq.w L_006700                                    ; +$025C : 670001B6
    movea.l 32(a4),a0                                 ; +$0260 : 206C0020
    move.l 20(a0),d0                                  ; +$0264 : 20280014
    andi.l #$00000001,d0                              ; +$0268 : 028000000001
    beq.w L_00658A                                    ; +$026E : 6700002E
    movea.l 12(a0),a0                                 ; +$0272 : 2068000C
    move.l a0,d0                                      ; +$0276 : 2008
    tst.l d0                                          ; +$0278 : 4A80
    beq.w L_006700                                    ; +$027A : 67000198
    movea.l $0004.w,a6                                ; +$027E : 2C780004
    jsr -372(a6)                                      ; +$0282 : 4EAEFE8C
    tst.l d0                                          ; +$0286 : 4A80
    beq.w L_006700                                    ; +$0288 : 6700018A
    movea.l 32(a4),a0                                 ; +$028C : 206C0020
    move.l 20(a0),d0                                  ; +$0290 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0294 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$029A : 21400014
L_00658A:
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
    bmi.w L_006600                                    ; +$02C6 : 6B00004C
    cmp.l 16(a4),d4                                   ; +$02CA : B8AC0010
    bge.w L_006600                                    ; +$02CE : 6C000044
    move.l 128(a7),d0                                 ; +$02D2 : 202F0080
    cmp.l 132(a7),d0                                  ; +$02D6 : B0AF0084
    bne.w L_0065E2                                    ; +$02DA : 6600001A
    movea.l a2,a1                                     ; +$02DE : 224A
    move.l d4,d1                                      ; +$02E0 : 2204
    jsr -324(a6)                                      ; +$02E2 : 4EAEFEBC
    tst.l d0                                          ; +$02E6 : 4A80
    bne.w L_006600                                    ; +$02E8 : 6600002A
    move.l #$00000001,d3                              ; +$02EC : 263C00000001
    bra.w L_006600                                    ; +$02F2 : 60000020
L_0065E2:
    movea.l a2,a1                                     ; +$02F6 : 224A
    move.l 128(a7),d0                                 ; +$02F8 : 202F0080
    move.l d4,d1                                      ; +$02FC : 2204
    jsr -240(a6)                                      ; +$02FE : 4EAEFF10
    movea.l a2,a1                                     ; +$0302 : 224A
    move.l 132(a7),d0                                 ; +$0304 : 202F0084
    move.l d4,d1                                      ; +$0308 : 2204
    jsr -246(a6)                                      ; +$030A : 4EAEFF0A
    move.l #$00000001,d3                              ; +$030E : 263C00000001
L_006600:
    cmp.l d4,d6                                       ; +$0314 : BC84
    beq.w L_006656                                    ; +$0316 : 67000052
    tst.l d6                                          ; +$031A : 4A86
    bmi.w L_006656                                    ; +$031C : 6B00004C
    cmp.l 16(a4),d6                                   ; +$0320 : BCAC0010
    bge.w L_006656                                    ; +$0324 : 6C000044
    move.l 128(a7),d0                                 ; +$0328 : 202F0080
    cmp.l 132(a7),d0                                  ; +$032C : B0AF0084
    bne.w L_006638                                    ; +$0330 : 6600001A
    movea.l a2,a1                                     ; +$0334 : 224A
    move.l d6,d1                                      ; +$0336 : 2206
    jsr -324(a6)                                      ; +$0338 : 4EAEFEBC
    tst.l d0                                          ; +$033C : 4A80
    bne.w L_006656                                    ; +$033E : 6600002A
    move.l #$00000001,d3                              ; +$0342 : 263C00000001
    bra.w L_006656                                    ; +$0348 : 60000020
L_006638:
    movea.l a2,a1                                     ; +$034C : 224A
    move.l 128(a7),d0                                 ; +$034E : 202F0080
    move.l d6,d1                                      ; +$0352 : 2206
    jsr -240(a6)                                      ; +$0354 : 4EAEFF10
    movea.l a2,a1                                     ; +$0358 : 224A
    move.l 132(a7),d0                                 ; +$035A : 202F0084
    move.l d6,d1                                      ; +$035E : 2206
    jsr -246(a6)                                      ; +$0360 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$0364 : 263C00000001
L_006656:
    tst.l d2                                          ; +$036A : 4A82
    bmi.w L_0066A6                                    ; +$036C : 6B00004C
    cmp.l 12(a4),d2                                   ; +$0370 : B4AC000C
    bge.w L_0066A6                                    ; +$0374 : 6C000044
    move.l 136(a7),d1                                 ; +$0378 : 222F0088
    cmp.l 140(a7),d1                                  ; +$037C : B2AF008C
    bne.w L_006688                                    ; +$0380 : 6600001A
    movea.l a2,a1                                     ; +$0384 : 224A
    move.l d2,d0                                      ; +$0386 : 2002
    jsr -324(a6)                                      ; +$0388 : 4EAEFEBC
    tst.l d0                                          ; +$038C : 4A80
    bne.w L_0066A6                                    ; +$038E : 6600002A
    move.l #$00000001,d3                              ; +$0392 : 263C00000001
    bra.w L_0066A6                                    ; +$0398 : 60000020
L_006688:
    movea.l a2,a1                                     ; +$039C : 224A
    move.l d2,d0                                      ; +$039E : 2002
    move.l 136(a7),d1                                 ; +$03A0 : 222F0088
    jsr -240(a6)                                      ; +$03A4 : 4EAEFF10
    movea.l a2,a1                                     ; +$03A8 : 224A
    move.l d2,d0                                      ; +$03AA : 2002
    move.l 140(a7),d1                                 ; +$03AC : 222F008C
    jsr -246(a6)                                      ; +$03B0 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$03B4 : 263C00000001
L_0066A6:
    cmp.l d2,d5                                       ; +$03BA : BA82
    beq.w L_0066FC                                    ; +$03BC : 67000052
    tst.l d5                                          ; +$03C0 : 4A85
    bmi.w L_0066FC                                    ; +$03C2 : 6B00004C
    cmp.l 12(a4),d5                                   ; +$03C6 : BAAC000C
    bge.w L_0066FC                                    ; +$03CA : 6C000044
    move.l 136(a7),d1                                 ; +$03CE : 222F0088
    cmp.l 140(a7),d1                                  ; +$03D2 : B2AF008C
    bne.w L_0066DE                                    ; +$03D6 : 6600001A
    movea.l a2,a1                                     ; +$03DA : 224A
    move.l d5,d0                                      ; +$03DC : 2005
    jsr -324(a6)                                      ; +$03DE : 4EAEFEBC
    tst.l d0                                          ; +$03E2 : 4A80
    bne.w L_0066FC                                    ; +$03E4 : 6600002A
    move.l #$00000001,d3                              ; +$03E8 : 263C00000001
    bra.w L_0066FC                                    ; +$03EE : 60000020
L_0066DE:
    movea.l a2,a1                                     ; +$03F2 : 224A
    move.l d5,d0                                      ; +$03F4 : 2005
    move.l 136(a7),d1                                 ; +$03F6 : 222F0088
    jsr -240(a6)                                      ; +$03FA : 4EAEFF10
    movea.l a2,a1                                     ; +$03FE : 224A
    move.l d5,d0                                      ; +$0400 : 2005
    move.l 140(a7),d1                                 ; +$0402 : 222F008C
    jsr -246(a6)                                      ; +$0406 : 4EAEFF0A
    move.l #$00000001,d3                              ; +$040A : 263C00000001
L_0066FC:
    jsr -228(a6)                                      ; +$0410 : 4EAEFF1C
L_006700:
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
    bgt.w L_006B8E                                    ; +$001C : 6E000460
    cmpi.l #$FFFF8000,d2                              ; +$0020 : 0C82FFFF8000
    blt.w L_006B8E                                    ; +$0026 : 6D000456
    cmpi.l #$00007FFF,d4                              ; +$002A : 0C8400007FFF
    bgt.w L_006B8E                                    ; +$0030 : 6E00044C
    cmpi.l #$FFFF8000,d4                              ; +$0034 : 0C84FFFF8000
    blt.w L_006B8E                                    ; +$003A : 6D000442
    cmpi.l #$00007FFF,d6                              ; +$003E : 0C8600007FFF
    bgt.w L_006B8E                                    ; +$0044 : 6E000438
    cmpi.l #$FFFF8000,d6                              ; +$0048 : 0C86FFFF8000
    blt.w L_006B8E                                    ; +$004E : 6D00042E
    tst.l d6                                          ; +$0052 : 4A86
    bmi.w L_006B8E                                    ; +$0054 : 6B000428
    tst.l d7                                          ; +$0058 : 4A87
    bmi.w L_006B8E                                    ; +$005A : 6B000422
    movea.l 456(a5),a4                                ; +$005E : 286D01C8
    move.l a4,d0                                      ; +$0062 : 200C
    tst.l d0                                          ; +$0064 : 4A80
    beq.w L_006B8E                                    ; +$0066 : 67000416
    move.l (a4),d0                                    ; +$006A : 2014
    tst.l d0                                          ; +$006C : 4A80
    beq.w L_006B8E                                    ; +$006E : 6700040E
    move.l 8(a4),d0                                   ; +$0072 : 202C0008
    tst.l d0                                          ; +$0076 : 4A80
    beq.w L_006B8E                                    ; +$0078 : 67000404
    move.l 32(a4),d0                                  ; +$007C : 202C0020
    tst.l d0                                          ; +$0080 : 4A80
    beq.w L_006B8E                                    ; +$0082 : 670003FA
    move.l 12(a4),d0                                  ; +$0086 : 202C000C
    tst.l d0                                          ; +$008A : 4A80
    ble.w L_006B8E                                    ; +$008C : 6F0003F0
    cmpi.l #$00007FFF,d0                              ; +$0090 : 0C8000007FFF
    bgt.w L_006B8E                                    ; +$0096 : 6E0003E6
    move.l 16(a4),d0                                  ; +$009A : 202C0010
    tst.l d0                                          ; +$009E : 4A80
    ble.w L_006B8E                                    ; +$00A0 : 6F0003DC
    cmpi.l #$00007FFF,d0                              ; +$00A4 : 0C8000007FFF
    bgt.w L_006B8E                                    ; +$00AA : 6E0003D2
    move.l 28(a4),d0                                  ; +$00AE : 202C001C
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_006B8E                                    ; +$00B4 : 6F0003C8
    cmpi.l #$00000008,d0                              ; +$00B8 : 0C8000000008
    bgt.w L_006B8E                                    ; +$00BE : 6E0003BE
    move.l #$00000001,d1                              ; +$00C2 : 223C00000001
L_0067D8:
    lsl.l #1,d1                                       ; +$00C8 : E389
    subq.l #1,d0                                      ; +$00CA : 5380
    bne.w L_0067D8                                    ; +$00CC : 6600FFFA
    cmp.l d1,d7                                       ; +$00D0 : BE81
    bcc.w L_006B8E                                    ; +$00D2 : 640003AA
    move.l d2,d0                                      ; +$00D6 : 2002
    add.l d6,d0                                       ; +$00D8 : D086
    tst.l d0                                          ; +$00DA : 4A80
    bmi.w L_006B8E                                    ; +$00DC : 6B0003A0
    move.l d2,d0                                      ; +$00E0 : 2002
    sub.l d6,d0                                       ; +$00E2 : 9086
    cmp.l 12(a4),d0                                   ; +$00E4 : B0AC000C
    bge.w L_006B8E                                    ; +$00E8 : 6C000394
    move.l d4,d0                                      ; +$00EC : 2004
    add.l d6,d0                                       ; +$00EE : D086
    tst.l d0                                          ; +$00F0 : 4A80
    bmi.w L_006B8E                                    ; +$00F2 : 6B00038A
    move.l d4,d0                                      ; +$00F6 : 2004
    sub.l d6,d0                                       ; +$00F8 : 9086
    cmp.l 16(a4),d0                                   ; +$00FA : B0AC0010
    bge.w L_006B8E                                    ; +$00FE : 6C00037E
    movea.l 32(a4),a2                                 ; +$0102 : 246C0020
    move.l 8(a2),d0                                   ; +$0106 : 202A0008
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_006830                                    ; +$010C : 67000012
    cmpi.l #$00000001,d0                              ; +$0110 : 0C8000000001
    bne.w L_006B8E                                    ; +$0116 : 66000366
    movea.l (a2),a0                                   ; +$011A : 2052
    bra.w L_006834                                    ; +$011C : 60000006
L_006830:
    movea.l 4(a2),a0                                  ; +$0120 : 206A0004
L_006834:
    move.l a0,d0                                      ; +$0124 : 2008
    tst.l d0                                          ; +$0126 : 4A80
    beq.w L_006B8E                                    ; +$0128 : 67000354
    movea.l (a0),a0                                   ; +$012C : 2050
    move.l a0,d0                                      ; +$012E : 2008
    tst.l d0                                          ; +$0130 : 4A80
    beq.w L_006B8E                                    ; +$0132 : 6700034A
    movea.l a0,a2                                     ; +$0136 : 2448
    move.l #$00000000,d1                              ; +$0138 : 223C00000000
    move.w (a0),d1                                    ; +$013E : 3210
    lsl.l #3,d1                                       ; +$0140 : E789
    cmp.l 12(a4),d1                                   ; +$0142 : B2AC000C
    blt.w L_006B8E                                    ; +$0146 : 6D000336
    move.l #$00000000,d1                              ; +$014A : 223C00000000
    move.w 2(a0),d1                                   ; +$0150 : 32280002
    cmp.l 16(a4),d1                                   ; +$0154 : B2AC0010
    blt.w L_006B8E                                    ; +$0158 : 6D000324
    move.l #$00000000,d1                              ; +$015C : 223C00000000
    move.b 5(a0),d1                                   ; +$0162 : 12280005
    cmp.l 28(a4),d1                                   ; +$0166 : B2AC001C
    bne.w L_006B8E                                    ; +$016A : 66000312
    move.l d1,d0                                      ; +$016E : 2001
    movea.l a0,a1                                     ; +$0170 : 2248
    addq.l #8,a1                                      ; +$0172 : 5089
L_006884:
    move.l (a1)+,d1                                   ; +$0174 : 2219
    tst.l d1                                          ; +$0176 : 4A81
    beq.w L_006B8E                                    ; +$0178 : 67000304
    cmpi.l #$FFFFFFFF,d1                              ; +$017C : 0C81FFFFFFFF
    beq.w L_006B8E                                    ; +$0182 : 670002FA
    subq.l #1,d0                                      ; +$0186 : 5380
    bne.w L_006884                                    ; +$0188 : 6600FFEA
    move.l a2,156(a7)                                 ; +$018C : 2F4A009C
    movea.l 32(a4),a0                                 ; +$0190 : 206C0020
    move.l 20(a0),d0                                  ; +$0194 : 20280014
    andi.l #$00000001,d0                              ; +$0198 : 028000000001
    beq.w L_0068DE                                    ; +$019E : 6700002E
    movea.l 12(a0),a0                                 ; +$01A2 : 2068000C
    move.l a0,d0                                      ; +$01A6 : 2008
    tst.l d0                                          ; +$01A8 : 4A80
    beq.w L_006B8E                                    ; +$01AA : 670002D2
    movea.l $0004.w,a6                                ; +$01AE : 2C780004
    jsr -372(a6)                                      ; +$01B2 : 4EAEFE8C
    tst.l d0                                          ; +$01B6 : 4A80
    beq.w L_006B8E                                    ; +$01B8 : 670002C4
    movea.l 32(a4),a0                                 ; +$01BC : 206C0020
    move.l 20(a0),d0                                  ; +$01C0 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$01C4 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$01CA : 21400014
L_0068DE:
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
    bne.w L_006934                                    ; +$01FE : 66000024
    move.l d2,d0                                      ; +$0202 : 2002
    move.l d4,d1                                      ; +$0204 : 2204
    move.l #$00000001,136(a7)                         ; +$0206 : 2F7C000000010088
    movea.l a2,a1                                     ; +$020E : 224A
    jsr -324(a6)                                      ; +$0210 : 4EAEFEBC
    tst.l d0                                          ; +$0214 : 4A80
    bne.w L_006B82                                    ; +$0216 : 6600025A
    move.l #$00000001,d3                              ; +$021A : 263C00000001
    bra.w L_006B82                                    ; +$0220 : 60000250
L_006934:
    move.l d6,d5                                      ; +$0224 : 2A06
    move.l #$00000000,128(a7)                         ; +$0226 : 2F7C000000000080
    move.l #$00000001,d0                              ; +$022E : 203C00000001
    sub.l d6,d0                                       ; +$0234 : 9086
    move.l d0,132(a7)                                 ; +$0236 : 2F400084
L_00694A:
    move.l d2,d0                                      ; +$023A : 2002
    add.l d5,d0                                       ; +$023C : D085
    tst.l d0                                          ; +$023E : 4A80
    bmi.w L_00698A                                    ; +$0240 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0244 : B0AC000C
    bge.w L_00698A                                    ; +$0248 : 6C000030
    move.l d4,d1                                      ; +$024C : 2204
    add.l 128(a7),d1                                  ; +$024E : D2AF0080
    tst.l d1                                          ; +$0252 : 4A81
    bmi.w L_00698A                                    ; +$0254 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0258 : B2AC0010
    bge.w L_00698A                                    ; +$025C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0260 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0268 : 224A
    jsr -324(a6)                                      ; +$026A : 4EAEFEBC
    tst.l d0                                          ; +$026E : 4A80
    bne.w L_00698A                                    ; +$0270 : 66000008
    move.l #$00000001,d3                              ; +$0274 : 263C00000001
L_00698A:
    move.l d2,d0                                      ; +$027A : 2002
    sub.l d5,d0                                       ; +$027C : 9085
    tst.l d0                                          ; +$027E : 4A80
    bmi.w L_0069CA                                    ; +$0280 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0284 : B0AC000C
    bge.w L_0069CA                                    ; +$0288 : 6C000030
    move.l d4,d1                                      ; +$028C : 2204
    add.l 128(a7),d1                                  ; +$028E : D2AF0080
    tst.l d1                                          ; +$0292 : 4A81
    bmi.w L_0069CA                                    ; +$0294 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0298 : B2AC0010
    bge.w L_0069CA                                    ; +$029C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$02A0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$02A8 : 224A
    jsr -324(a6)                                      ; +$02AA : 4EAEFEBC
    tst.l d0                                          ; +$02AE : 4A80
    bne.w L_0069CA                                    ; +$02B0 : 66000008
    move.l #$00000001,d3                              ; +$02B4 : 263C00000001
L_0069CA:
    move.l d2,d0                                      ; +$02BA : 2002
    add.l d5,d0                                       ; +$02BC : D085
    tst.l d0                                          ; +$02BE : 4A80
    bmi.w L_006A0A                                    ; +$02C0 : 6B000038
    cmp.l 12(a4),d0                                   ; +$02C4 : B0AC000C
    bge.w L_006A0A                                    ; +$02C8 : 6C000030
    move.l d4,d1                                      ; +$02CC : 2204
    sub.l 128(a7),d1                                  ; +$02CE : 92AF0080
    tst.l d1                                          ; +$02D2 : 4A81
    bmi.w L_006A0A                                    ; +$02D4 : 6B000024
    cmp.l 16(a4),d1                                   ; +$02D8 : B2AC0010
    bge.w L_006A0A                                    ; +$02DC : 6C00001C
    move.l #$00000001,136(a7)                         ; +$02E0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$02E8 : 224A
    jsr -324(a6)                                      ; +$02EA : 4EAEFEBC
    tst.l d0                                          ; +$02EE : 4A80
    bne.w L_006A0A                                    ; +$02F0 : 66000008
    move.l #$00000001,d3                              ; +$02F4 : 263C00000001
L_006A0A:
    move.l d2,d0                                      ; +$02FA : 2002
    sub.l d5,d0                                       ; +$02FC : 9085
    tst.l d0                                          ; +$02FE : 4A80
    bmi.w L_006A4A                                    ; +$0300 : 6B000038
    cmp.l 12(a4),d0                                   ; +$0304 : B0AC000C
    bge.w L_006A4A                                    ; +$0308 : 6C000030
    move.l d4,d1                                      ; +$030C : 2204
    sub.l 128(a7),d1                                  ; +$030E : 92AF0080
    tst.l d1                                          ; +$0312 : 4A81
    bmi.w L_006A4A                                    ; +$0314 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0318 : B2AC0010
    bge.w L_006A4A                                    ; +$031C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0320 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0328 : 224A
    jsr -324(a6)                                      ; +$032A : 4EAEFEBC
    tst.l d0                                          ; +$032E : 4A80
    bne.w L_006A4A                                    ; +$0330 : 66000008
    move.l #$00000001,d3                              ; +$0334 : 263C00000001
L_006A4A:
    move.l d2,d0                                      ; +$033A : 2002
    add.l 128(a7),d0                                  ; +$033C : D0AF0080
    tst.l d0                                          ; +$0340 : 4A80
    bmi.w L_006A8A                                    ; +$0342 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0346 : B0AC000C
    bge.w L_006A8A                                    ; +$034A : 6C00002E
    move.l d4,d1                                      ; +$034E : 2204
    add.l d5,d1                                       ; +$0350 : D285
    tst.l d1                                          ; +$0352 : 4A81
    bmi.w L_006A8A                                    ; +$0354 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0358 : B2AC0010
    bge.w L_006A8A                                    ; +$035C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0360 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0368 : 224A
    jsr -324(a6)                                      ; +$036A : 4EAEFEBC
    tst.l d0                                          ; +$036E : 4A80
    bne.w L_006A8A                                    ; +$0370 : 66000008
    move.l #$00000001,d3                              ; +$0374 : 263C00000001
L_006A8A:
    move.l d2,d0                                      ; +$037A : 2002
    sub.l 128(a7),d0                                  ; +$037C : 90AF0080
    tst.l d0                                          ; +$0380 : 4A80
    bmi.w L_006ACA                                    ; +$0382 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0386 : B0AC000C
    bge.w L_006ACA                                    ; +$038A : 6C00002E
    move.l d4,d1                                      ; +$038E : 2204
    add.l d5,d1                                       ; +$0390 : D285
    tst.l d1                                          ; +$0392 : 4A81
    bmi.w L_006ACA                                    ; +$0394 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0398 : B2AC0010
    bge.w L_006ACA                                    ; +$039C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$03A0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$03A8 : 224A
    jsr -324(a6)                                      ; +$03AA : 4EAEFEBC
    tst.l d0                                          ; +$03AE : 4A80
    bne.w L_006ACA                                    ; +$03B0 : 66000008
    move.l #$00000001,d3                              ; +$03B4 : 263C00000001
L_006ACA:
    move.l d2,d0                                      ; +$03BA : 2002
    add.l 128(a7),d0                                  ; +$03BC : D0AF0080
    tst.l d0                                          ; +$03C0 : 4A80
    bmi.w L_006B0A                                    ; +$03C2 : 6B000036
    cmp.l 12(a4),d0                                   ; +$03C6 : B0AC000C
    bge.w L_006B0A                                    ; +$03CA : 6C00002E
    move.l d4,d1                                      ; +$03CE : 2204
    sub.l d5,d1                                       ; +$03D0 : 9285
    tst.l d1                                          ; +$03D2 : 4A81
    bmi.w L_006B0A                                    ; +$03D4 : 6B000024
    cmp.l 16(a4),d1                                   ; +$03D8 : B2AC0010
    bge.w L_006B0A                                    ; +$03DC : 6C00001C
    move.l #$00000001,136(a7)                         ; +$03E0 : 2F7C000000010088
    movea.l a2,a1                                     ; +$03E8 : 224A
    jsr -324(a6)                                      ; +$03EA : 4EAEFEBC
    tst.l d0                                          ; +$03EE : 4A80
    bne.w L_006B0A                                    ; +$03F0 : 66000008
    move.l #$00000001,d3                              ; +$03F4 : 263C00000001
L_006B0A:
    move.l d2,d0                                      ; +$03FA : 2002
    sub.l 128(a7),d0                                  ; +$03FC : 90AF0080
    tst.l d0                                          ; +$0400 : 4A80
    bmi.w L_006B4A                                    ; +$0402 : 6B000036
    cmp.l 12(a4),d0                                   ; +$0406 : B0AC000C
    bge.w L_006B4A                                    ; +$040A : 6C00002E
    move.l d4,d1                                      ; +$040E : 2204
    sub.l d5,d1                                       ; +$0410 : 9285
    tst.l d1                                          ; +$0412 : 4A81
    bmi.w L_006B4A                                    ; +$0414 : 6B000024
    cmp.l 16(a4),d1                                   ; +$0418 : B2AC0010
    bge.w L_006B4A                                    ; +$041C : 6C00001C
    move.l #$00000001,136(a7)                         ; +$0420 : 2F7C000000010088
    movea.l a2,a1                                     ; +$0428 : 224A
    jsr -324(a6)                                      ; +$042A : 4EAEFEBC
    tst.l d0                                          ; +$042E : 4A80
    bne.w L_006B4A                                    ; +$0430 : 66000008
    move.l #$00000001,d3                              ; +$0434 : 263C00000001
L_006B4A:
    addq.l #1,128(a7)                                 ; +$043A : 52AF0080
    tst.l 132(a7)                                     ; +$043E : 4AAF0084
    bmi.w L_006B66                                    ; +$0442 : 6B000012
    subq.l #1,d5                                      ; +$0446 : 5385
    move.l 128(a7),d0                                 ; +$0448 : 202F0080
    sub.l d5,d0                                       ; +$044C : 9085
    lsl.l #1,d0                                       ; +$044E : E388
    addq.l #1,d0                                      ; +$0450 : 5280
    bra.w L_006B6E                                    ; +$0452 : 6000000A
L_006B66:
    move.l 128(a7),d0                                 ; +$0456 : 202F0080
    lsl.l #1,d0                                       ; +$045A : E388
    addq.l #1,d0                                      ; +$045C : 5280
L_006B6E:
    move.l 132(a7),d1                                 ; +$045E : 222F0084
    add.l d0,d1                                       ; +$0462 : D280
    move.l d1,132(a7)                                 ; +$0464 : 2F410084
    move.l 128(a7),d0                                 ; +$0468 : 202F0080
    cmp.l d5,d0                                       ; +$046C : B085
    ble.w L_00694A                                    ; +$046E : 6F00FDCA
L_006B82:
    tst.l 136(a7)                                     ; +$0472 : 4AAF0088
    beq.w L_006B8E                                    ; +$0476 : 67000006
    jsr -228(a6)                                      ; +$047A : 4EAEFF1C
L_006B8E:
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
    blt.w L_006C74                                    ; +$000E : 6D0000C6
    cmpi.l #$00000001,d7                              ; +$0012 : 0C8700000001
    bgt.w L_006C74                                    ; +$0018 : 6E0000BC
    movea.l 456(a5),a4                                ; +$001C : 286D01C8
    move.l a4,d0                                      ; +$0020 : 200C
    tst.l d0                                          ; +$0022 : 4A80
    beq.w L_006C74                                    ; +$0024 : 670000B0
    movea.l (a4),a1                                   ; +$0028 : 2254
    move.l a1,d0                                      ; +$002A : 2009
    tst.l d0                                          ; +$002C : 4A80
    beq.w L_006C74                                    ; +$002E : 670000A6
    movea.l 4(a4),a6                                  ; +$0032 : 2C6C0004
    move.l a6,d0                                      ; +$0036 : 200E
    tst.l d0                                          ; +$0038 : 4A80
    beq.w L_006C74                                    ; +$003A : 6700009A
    movea.l 36(a4),a3                                 ; +$003E : 266C0024
    move.l a3,d0                                      ; +$0042 : 200B
    tst.l d0                                          ; +$0044 : 4A80
    beq.w L_006C74                                    ; +$0046 : 6700008E
    move.l 46(a3),d0                                  ; +$004A : 202B002E
    move.l a1,d1                                      ; +$004E : 2209
    cmp.l d1,d0                                       ; +$0050 : B081
    bne.w L_006C74                                    ; +$0052 : 66000082
    lea L_006CDE(pc),a2                               ; +$0056 : 45FA00E8
    move.l (a2),d0                                    ; +$005A : 2012
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_006C0C                                    ; +$005E : 6700000E
    move.l 4(a2),d0                                   ; +$0062 : 202A0004
    move.l a3,d1                                      ; +$0066 : 220B
    cmp.l d1,d0                                       ; +$0068 : B081
    bne.w L_006C74                                    ; +$006A : 6600006A
L_006C0C:
    tst.l d7                                          ; +$006E : 4A87
    beq.w L_006C22                                    ; +$0070 : 67000012
    movea.l a3,a0                                     ; +$0074 : 204B
    jsr -60(a6)                                       ; +$0076 : 4EAEFFC4
    move.l #$00000001,d3                              ; +$007A : 263C00000001
    bra.w L_006C74                                    ; +$0080 : 60000054
L_006C22:
    move.l (a2),d0                                    ; +$0084 : 2012
    tst.l d0                                          ; +$0086 : 4A80
    bne.w L_006C4A                                    ; +$0088 : 66000022
    move.l #$00000048,d0                              ; +$008C : 203C00000048
    move.l #$00010002,d1                              ; +$0092 : 223C00010002
    movea.l $0004.w,a6                                ; +$0098 : 2C780004
    jsr -198(a6)                                      ; +$009C : 4EAEFF3A
    tst.l d0                                          ; +$00A0 : 4A80
    beq.w L_006C74                                    ; +$00A2 : 67000032
    move.l d0,(a2)                                    ; +$00A6 : 2480
    move.l a3,4(a2)                                   ; +$00A8 : 254B0004
L_006C4A:
    movea.l a3,a0                                     ; +$00AC : 204B
    movea.l (a2),a1                                   ; +$00AE : 2252
    move.l #$00000010,d0                              ; +$00B0 : 203C00000010
    move.l #$00000010,d1                              ; +$00B6 : 223C00000010
    move.l #$00000000,d2                              ; +$00BC : 243C00000000
    move.l #$00000000,d3                              ; +$00C2 : 263C00000000
    movea.l 4(a4),a6                                  ; +$00C8 : 2C6C0004
    jsr -270(a6)                                      ; +$00CC : 4EAEFEF2
    move.l #$00000001,d3                              ; +$00D0 : 263C00000001
L_006C74:
    movem.l (a7)+,d0-d2/d4-d7/a0-a6                   ; +$00D6 : 4CDF7FF7
    moveq #0,d2                                       ; +$00DA : 7400
    rts                                               ; +$00DC : 4E75
L_006C7C:
    movem.l d0-d7/a0-a6,-(a7)                         ; +$00DE : 48E7FFFE
    movea.l a0,a3                                     ; +$00E2 : 2648
    lea L_006CDE(pc),a4                               ; +$00E4 : 49FA005A
    move.l (a4),d0                                    ; +$00E8 : 2014
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_006CA0                                    ; +$00EC : 67000014
    move.l 4(a4),d0                                   ; +$00F0 : 202C0004
    move.l a3,d1                                      ; +$00F4 : 220B
    cmp.l d1,d0                                       ; +$00F6 : B081
    bne.w L_006CA0                                    ; +$00F8 : 66000008
    movea.l a3,a0                                     ; +$00FC : 204B
    jsr -60(a6)                                       ; +$00FE : 4EAEFFC4
L_006CA0:
    movea.l a3,a0                                     ; +$0102 : 204B
    jsr -72(a6)                                       ; +$0104 : 4EAEFFB8
    move.l (a4),d0                                    ; +$0108 : 2014
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_006CD8                                    ; +$010C : 6700002C
    move.l 4(a4),d0                                   ; +$0110 : 202C0004
    move.l a3,d1                                      ; +$0114 : 220B
    cmp.l d1,d0                                       ; +$0116 : B081
    bne.w L_006CD8                                    ; +$0118 : 66000020
    movea.l (a4),a1                                   ; +$011C : 2254
    move.l #$00000048,d0                              ; +$011E : 203C00000048
    movea.l $0004.w,a6                                ; +$0124 : 2C780004
    jsr -210(a6)                                      ; +$0128 : 4EAEFF2E
    move.l #$00000000,(a4)                            ; +$012C : 28BC00000000
    move.l #$00000000,4(a4)                           ; +$0132 : 297C000000000004
L_006CD8:
    movem.l (a7)+,d0-d7/a0-a6                         ; +$013A : 4CDF7FFF
    rts                                               ; +$013E : 4E75
L_006CDE:
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
    bhi.w L_007104                                    ; +$0032 : 620003E6
    cmpi.l #$00000020,d4                              ; +$0036 : 0C8400000020
    bcs.w L_007104                                    ; +$003C : 650003DC
    cmpi.l #$01000000,d4                              ; +$0040 : 0C8401000000
    bhi.w L_007104                                    ; +$0046 : 620003D2
    cmpi.l #$00000018,d5                              ; +$004A : 0C8500000018
    bls.w L_007104                                    ; +$0050 : 630003C8
    move.l d5,d0                                      ; +$0054 : 2005
    andi.l #$00000001,d0                              ; +$0056 : 028000000001
    bne.w L_007104                                    ; +$005C : 660003BC
    cmpi.l #$FFFF8000,d6                              ; +$0060 : 0C86FFFF8000
    blt.w L_007104                                    ; +$0066 : 6D0003B2
    cmpi.l #$00007FFF,d6                              ; +$006A : 0C8600007FFF
    bgt.w L_007104                                    ; +$0070 : 6E0003A8
    cmpi.l #$FFFF8000,d7                              ; +$0074 : 0C87FFFF8000
    blt.w L_007104                                    ; +$007A : 6D00039E
    cmpi.l #$00007FFF,d7                              ; +$007E : 0C8700007FFF
    bgt.w L_007104                                    ; +$0084 : 6E000394
    move.l d5,d0                                      ; +$0088 : 2005
    add.l d4,d0                                       ; +$008A : D084
    bcs.w L_007104                                    ; +$008C : 6500038C
    subq.l #1,d0                                      ; +$0090 : 5380
    movea.l d0,a1                                     ; +$0092 : 2240
    movea.l $0004.w,a6                                ; +$0094 : 2C780004
    jsr -534(a6)                                      ; +$0098 : 4EAEFDEA
    tst.l d0                                          ; +$009C : 4A80
    beq.w L_007104                                    ; +$009E : 6700037A
    move.l d5,d0                                      ; +$00A2 : 2005
    subi.l #$00000018,d0                              ; +$00A4 : 048000000018
    movea.l d0,a1                                     ; +$00AA : 2240
    jsr -534(a6)                                      ; +$00AC : 4EAEFDEA
    tst.l d0                                          ; +$00B0 : 4A80
    beq.w L_007104                                    ; +$00B2 : 67000366
    movea.l d5,a0                                     ; +$00B6 : 2045
    move.l -20(a0),d0                                 ; +$00B8 : 2028FFEC
    move.l d4,d1                                      ; +$00BC : 2204
    addi.l #$00000010,d1                              ; +$00BE : 068100000010
    cmp.l d1,d0                                       ; +$00C4 : B081
    bne.w L_007104                                    ; +$00C6 : 66000352
    move.l -16(a0),d0                                 ; +$00CA : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$00CE : 0C8000000005
    bcs.w L_007104                                    ; +$00D4 : 65000344
    cmpi.l #$0000FFFF,d0                              ; +$00D8 : 0C800000FFFF
    bhi.w L_007104                                    ; +$00DE : 6200033A
    move.l #$00000000,d0                              ; +$00E2 : 203C00000000
    move.w -12(a0),d0                                 ; +$00E8 : 3028FFF4
    tst.l d0                                          ; +$00EC : 4A80
    beq.w L_006DEA                                    ; +$00EE : 67000010
    andi.w #$FFFD,d0                                  ; +$00F2 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$00F6 : 0C8000000001
    bne.w L_007104                                    ; +$00FC : 6600031C
L_006DEA:
    move.l -8(a0),d0                                  ; +$0100 : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$0104 : 0C8041474150
    bne.w L_007104                                    ; +$010A : 6600030E
    move.l -4(a0),d0                                  ; +$010E : 2028FFFC
    cmpi.l #$49432020,d0                              ; +$0112 : 0C8049432020
    bne.w L_007104                                    ; +$0118 : 66000300
    move.l (a0),d0                                    ; +$011C : 2010
    cmpi.l #$41474150,d0                              ; +$011E : 0C8041474150
    bne.w L_007104                                    ; +$0124 : 660002F4
    move.l #$00000000,d0                              ; +$0128 : 203C00000000
    move.w 4(a0),d0                                   ; +$012E : 30280004
    cmpi.l #$00004943,d0                              ; +$0132 : 0C8000004943
    bne.w L_007104                                    ; +$0138 : 660002E0
    move.l #$00000000,d0                              ; +$013C : 203C00000000
    move.w 6(a0),d0                                   ; +$0142 : 30280006
    cmpi.l #$00000001,d0                              ; +$0146 : 0C8000000001
    bne.w L_007104                                    ; +$014C : 660002CC
    move.l #$00000000,d0                              ; +$0150 : 203C00000000
    move.w 8(a0),d0                                   ; +$0156 : 30280008
    move.l d0,32(a2)                                  ; +$015A : 25400020
    cmpi.l #$00000001,d0                              ; +$015E : 0C8000000001
    bhi.w L_007104                                    ; +$0164 : 620002B4
    move.l (a2),d1                                    ; +$0168 : 2212
    tst.l d1                                          ; +$016A : 4A81
    beq.w L_006E60                                    ; +$016C : 67000008
    tst.l d0                                          ; +$0170 : 4A80
    beq.w L_007104                                    ; +$0172 : 670002A6
L_006E60:
    move.l #$00000000,d0                              ; +$0176 : 203C00000000
    move.w 10(a0),d0                                  ; +$017C : 3028000A
    cmpi.l #$00000001,d0                              ; +$0180 : 0C8000000001
    bne.w L_007104                                    ; +$0186 : 66000292
    move.l #$00000000,d0                              ; +$018A : 203C00000000
    move.w 12(a0),d0                                  ; +$0190 : 3028000C
    move.l d0,20(a2)                                  ; +$0194 : 25400014
    tst.l d0                                          ; +$0198 : 4A80
    beq.w L_007104                                    ; +$019A : 6700027E
    cmpi.l #$00001000,d0                              ; +$019E : 0C8000001000
    bhi.w L_007104                                    ; +$01A4 : 62000274
    move.l #$00000000,d0                              ; +$01A8 : 203C00000000
    move.w 14(a0),d0                                  ; +$01AE : 3028000E
    move.l d0,24(a2)                                  ; +$01B2 : 25400018
    tst.l d0                                          ; +$01B6 : 4A80
    beq.w L_007104                                    ; +$01B8 : 67000260
    cmpi.l #$00001000,d0                              ; +$01BC : 0C8000001000
    bhi.w L_007104                                    ; +$01C2 : 62000256
    move.l 20(a2),d1                                  ; +$01C6 : 222A0014
    mulu.w d1,d0                                      ; +$01CA : C0C1
    cmpi.l #$00400000,d0                              ; +$01CC : 0C8000400000
    bhi.w L_007104                                    ; +$01D2 : 62000246
    move.l #$00000000,d0                              ; +$01D6 : 203C00000000
    move.w 16(a0),d0                                  ; +$01DC : 30280010
    move.l d0,28(a2)                                  ; +$01E0 : 2540001C
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_007104                                    ; +$01E6 : 67000232
    cmpi.l #$00000008,d0                              ; +$01EA : 0C8000000008
    bhi.w L_007104                                    ; +$01F0 : 62000228
    move.l d0,d1                                      ; +$01F4 : 2200
    move.l 32(a2),d0                                  ; +$01F6 : 202A0020
    add.l d1,d0                                       ; +$01FA : D081
    lsl.l #1,d0                                       ; +$01FC : E388
    move.l d0,36(a2)                                  ; +$01FE : 25400024
    move.l #$00000000,d1                              ; +$0202 : 223C00000000
    move.w 18(a0),d1                                  ; +$0208 : 32280012
    cmp.l d1,d0                                       ; +$020C : B081
    bne.w L_007104                                    ; +$020E : 6600020A
    move.l 20(a0),d0                                  ; +$0212 : 20280014
    cmpi.l #$00000020,d0                              ; +$0216 : 0C8000000020
    bne.w L_007104                                    ; +$021C : 660001FC
    move.l 24(a2),d0                                  ; +$0220 : 202A0018
    addq.l #1,d0                                      ; +$0224 : 5280
    lsl.l #2,d0                                       ; +$0226 : E588
    addi.l #$00000020,d0                              ; +$0228 : 068000000020
    move.l d0,48(a2)                                  ; +$022E : 25400030
    move.l 24(a0),d1                                  ; +$0232 : 22280018
    cmp.l d1,d0                                       ; +$0236 : B081
    bne.w L_007104                                    ; +$0238 : 660001E0
    cmp.l d4,d0                                       ; +$023C : B084
    bhi.w L_007104                                    ; +$023E : 620001DA
    move.l 28(a0),d0                                  ; +$0242 : 2028001C
    cmp.l d4,d0                                       ; +$0246 : B084
    bne.w L_007104                                    ; +$0248 : 660001D0
    move.l 20(a2),d0                                  ; +$024C : 202A0014
    addi.l #$0000000F,d0                              ; +$0250 : 06800000000F
    lsr.l #4,d0                                       ; +$0256 : E888
    move.l d0,40(a2)                                  ; +$0258 : 25400028
    move.l 20(a2),d1                                  ; +$025C : 222A0014
    andi.l #$0000000F,d1                              ; +$0260 : 02810000000F
    move.l #$00000000,d0                              ; +$0266 : 203C00000000
    tst.l d1                                          ; +$026C : 4A81
    beq.w L_006F6A                                    ; +$026E : 67000010
    move.l #$0000FFFF,d0                              ; +$0272 : 203C0000FFFF
L_006F62:
    lsr.w #1,d0                                       ; +$0278 : E248
    subq.l #1,d1                                      ; +$027A : 5381
    bne.w L_006F62                                    ; +$027C : 6600FFFA
L_006F6A:
    move.l d0,44(a2)                                  ; +$0280 : 2540002C
    movea.l 456(a5),a4                                ; +$0284 : 286D01C8
    move.l a4,d0                                      ; +$0288 : 200C
    tst.l d0                                          ; +$028A : 4A80
    beq.w L_007104                                    ; +$028C : 6700018C
    move.l (a4),d0                                    ; +$0290 : 2014
    tst.l d0                                          ; +$0292 : 4A80
    beq.w L_007104                                    ; +$0294 : 67000184
    move.l 8(a4),d0                                   ; +$0298 : 202C0008
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_007104                                    ; +$029E : 6700017A
    move.l 32(a4),d0                                  ; +$02A2 : 202C0020
    tst.l d0                                          ; +$02A6 : 4A80
    beq.w L_007104                                    ; +$02A8 : 67000170
    move.l 12(a4),d0                                  ; +$02AC : 202C000C
    tst.l d0                                          ; +$02B0 : 4A80
    ble.w L_007104                                    ; +$02B2 : 6F000166
    cmpi.l #$00007FFF,d0                              ; +$02B6 : 0C8000007FFF
    bgt.w L_007104                                    ; +$02BC : 6E00015C
    move.l d0,52(a2)                                  ; +$02C0 : 25400034
    move.l 16(a4),d0                                  ; +$02C4 : 202C0010
    tst.l d0                                          ; +$02C8 : 4A80
    ble.w L_007104                                    ; +$02CA : 6F00014E
    cmpi.l #$00007FFF,d0                              ; +$02CE : 0C8000007FFF
    bgt.w L_007104                                    ; +$02D4 : 6E000144
    move.l d0,56(a2)                                  ; +$02D8 : 25400038
    move.l 28(a4),d0                                  ; +$02DC : 202C001C
    cmp.l 28(a2),d0                                   ; +$02E0 : B0AA001C
    bne.w L_007104                                    ; +$02E4 : 66000134
    movea.l 32(a4),a0                                 ; +$02E8 : 206C0020
    move.l 8(a0),d0                                   ; +$02EC : 20280008
    tst.l d0                                          ; +$02F0 : 4A80
    beq.w L_006FF4                                    ; +$02F2 : 67000016
    cmpi.l #$00000001,d0                              ; +$02F6 : 0C8000000001
    bne.w L_007104                                    ; +$02FC : 6600011C
    movea.l 32(a4),a0                                 ; +$0300 : 206C0020
    movea.l (a0),a1                                   ; +$0304 : 2250
    bra.w L_006FFC                                    ; +$0306 : 6000000A
L_006FF4:
    movea.l 32(a4),a0                                 ; +$030A : 206C0020
    movea.l 4(a0),a1                                  ; +$030E : 22680004
L_006FFC:
    move.l a1,d0                                      ; +$0312 : 2009
    tst.l d0                                          ; +$0314 : 4A80
    beq.w L_007104                                    ; +$0316 : 67000102
    movea.l (a1),a0                                   ; +$031A : 2051
    move.l a0,d0                                      ; +$031C : 2008
    tst.l d0                                          ; +$031E : 4A80
    beq.w L_007104                                    ; +$0320 : 670000F8
    move.l a0,64(a2)                                  ; +$0324 : 25480040
    move.l #$00000000,d1                              ; +$0328 : 223C00000000
    move.w (a0),d1                                    ; +$032E : 3210
    tst.l d1                                          ; +$0330 : 4A81
    beq.w L_007104                                    ; +$0332 : 670000E6
    move.l d1,60(a2)                                  ; +$0336 : 2541003C
    lsl.l #3,d1                                       ; +$033A : E789
    cmp.l 52(a2),d1                                   ; +$033C : B2AA0034
    blt.w L_007104                                    ; +$0340 : 6D0000D8
    move.l #$00000000,d1                              ; +$0344 : 223C00000000
    move.w 2(a0),d1                                   ; +$034A : 32280002
    cmp.l 56(a2),d1                                   ; +$034E : B2AA0038
    blt.w L_007104                                    ; +$0352 : 6D0000C6
    move.l #$00000000,d1                              ; +$0356 : 223C00000000
    move.b 5(a0),d1                                   ; +$035C : 12280005
    cmp.l 28(a2),d1                                   ; +$0360 : B2AA001C
    bne.w L_007104                                    ; +$0364 : 660000B4
    move.l d1,d0                                      ; +$0368 : 2001
    movea.l a0,a1                                     ; +$036A : 2248
    addq.l #8,a1                                      ; +$036C : 5089
L_007058:
    move.l (a1)+,d1                                   ; +$036E : 2219
    tst.l d1                                          ; +$0370 : 4A81
    beq.w L_007104                                    ; +$0372 : 670000A6
    cmpi.l #$FFFFFFFF,d1                              ; +$0376 : 0C81FFFFFFFF
    beq.w L_007104                                    ; +$037C : 6700009C
    subq.l #1,d0                                      ; +$0380 : 5380
    bne.w L_007058                                    ; +$0382 : 6600FFEA
    move.l #$00000000,72(a2)                          ; +$0386 : 257C000000000048
    bsr.w L_007110                                    ; +$038E : 61000096
    tst.l d0                                          ; +$0392 : 4A80
    beq.w L_007104                                    ; +$0394 : 67000084
    move.l 8(a2),d0                                   ; +$0398 : 202A0008
    cmp.l 52(a2),d0                                   ; +$039C : B0AA0034
    bge.w L_0070FE                                    ; +$03A0 : 6C000072
    add.l 20(a2),d0                                   ; +$03A4 : D0AA0014
    tst.l d0                                          ; +$03A8 : 4A80
    ble.w L_0070FE                                    ; +$03AA : 6F000068
    move.l 4(a2),d0                                   ; +$03AE : 202A0004
    cmp.l 56(a2),d0                                   ; +$03B2 : B0AA0038
    bge.w L_0070FE                                    ; +$03B6 : 6C00005C
    add.l 24(a2),d0                                   ; +$03BA : D0AA0018
    tst.l d0                                          ; +$03BE : 4A80
    ble.w L_0070FE                                    ; +$03C0 : 6F000052
    movea.l 32(a4),a0                                 ; +$03C4 : 206C0020
    move.l 20(a0),d0                                  ; +$03C8 : 20280014
    andi.l #$00000001,d0                              ; +$03CC : 028000000001
    beq.w L_0070EC                                    ; +$03D2 : 6700002E
    movea.l 12(a0),a0                                 ; +$03D6 : 2068000C
    move.l a0,d0                                      ; +$03DA : 2008
    tst.l d0                                          ; +$03DC : 4A80
    beq.w L_007104                                    ; +$03DE : 6700003A
    movea.l $0004.w,a6                                ; +$03E2 : 2C780004
    jsr -372(a6)                                      ; +$03E6 : 4EAEFE8C
    tst.l d0                                          ; +$03EA : 4A80
    beq.w L_007104                                    ; +$03EC : 6700002C
    movea.l 32(a4),a0                                 ; +$03F0 : 206C0020
    move.l 20(a0),d0                                  ; +$03F4 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$03F8 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$03FE : 21400014
L_0070EC:
    move.l #$00000001,72(a2)                          ; +$0402 : 257C000000010048
    bsr.w L_007110                                    ; +$040A : 6100001A
    tst.l d0                                          ; +$040E : 4A80
    beq.w L_007104                                    ; +$0410 : 67000008
L_0070FE:
    move.l #$00000001,d3                              ; +$0414 : 263C00000001
L_007104:
    lea 192(a7),a7                                    ; +$041A : 4FEF00C0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$041E : 4CDF77F7
    moveq #0,d2                                       ; +$0422 : 7400
    rts                                               ; +$0424 : 4E75
L_007110:
    move.l #$00000000,68(a2)                          ; +$0426 : 257C000000000044
L_007118:
    move.l 68(a2),d0                                  ; +$042E : 202A0044
    cmp.l 24(a2),d0                                   ; +$0432 : B0AA0018
    bge.w L_0072D0                                    ; +$0436 : 6C0001AE
    lsl.l #2,d0                                       ; +$043A : E588
    move.l d0,d1                                      ; +$043C : 2200
    move.l 16(a2),d0                                  ; +$043E : 202A0010
    addi.l #$00000020,d0                              ; +$0442 : 068000000020
    add.l d1,d0                                       ; +$0448 : D081
    movea.l d0,a1                                     ; +$044A : 2240
    move.l (a1)+,d0                                   ; +$044C : 2019
    move.l (a1)+,d1                                   ; +$044E : 2219
    cmp.l d1,d0                                       ; +$0450 : B081
    bcc.w L_0072D8                                    ; +$0452 : 6400019A
    cmp.l 48(a2),d0                                   ; +$0456 : B0AA0030
    bcs.w L_0072D8                                    ; +$045A : 65000192
    cmp.l 12(a2),d1                                   ; +$045E : B2AA000C
    bhi.w L_0072D8                                    ; +$0462 : 6200018A
    move.l 68(a2),d2                                  ; +$0466 : 242A0044
    tst.l d2                                          ; +$046A : 4A82
    bne.w L_007162                                    ; +$046C : 6600000A
    cmp.l 48(a2),d0                                   ; +$0470 : B0AA0030
    bne.w L_0072D8                                    ; +$0474 : 66000178
L_007162:
    move.l 24(a2),d2                                  ; +$0478 : 242A0018
    subq.l #1,d2                                      ; +$047C : 5382
    cmp.l 68(a2),d2                                   ; +$047E : B4AA0044
    bne.w L_007178                                    ; +$0482 : 6600000A
    cmp.l 12(a2),d1                                   ; +$0486 : B2AA000C
    bne.w L_0072D8                                    ; +$048A : 66000162
L_007178:
    move.l 16(a2),d2                                  ; +$048E : 242A0010
    add.l d2,d0                                       ; +$0492 : D082
    move.l d0,76(a2)                                  ; +$0494 : 2540004C
    add.l d2,d1                                       ; +$0498 : D282
    move.l d1,80(a2)                                  ; +$049A : 25410050
    move.l #$00000000,84(a2)                          ; +$049E : 257C000000000054
    move.l #$00000000,88(a2)                          ; +$04A6 : 257C000000000058
    move.l #$00000000,92(a2)                          ; +$04AE : 257C00000000005C
L_0071A0:
    move.l 84(a2),d0                                  ; +$04B6 : 202A0054
    cmp.l 40(a2),d0                                   ; +$04BA : B0AA0028
    bge.w L_0072B6                                    ; +$04BE : 6C00010C
    move.l 88(a2),d0                                  ; +$04C2 : 202A0058
    tst.l d0                                          ; +$04C6 : 4A80
    bne.w L_007226                                    ; +$04C8 : 66000072
    move.l 76(a2),d0                                  ; +$04CC : 202A004C
    cmp.l 80(a2),d0                                   ; +$04D0 : B0AA0050
    bcc.w L_0072D8                                    ; +$04D4 : 64000118
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
    bgt.w L_0072D8                                    ; +$0506 : 6E0000E6
    move.l a0,d2                                      ; +$050A : 2408
    move.l d2,76(a2)                                  ; +$050C : 2542004C
    move.l 92(a2),d2                                  ; +$0510 : 242A005C
    tst.l d2                                          ; +$0514 : 4A82
    beq.w L_007210                                    ; +$0516 : 6700000E
    move.l a0,96(a2)                                  ; +$051A : 25480060
    move.l 36(a2),d2                                  ; +$051E : 242A0024
    bra.w L_007216                                    ; +$0522 : 60000008
L_007210:
    move.l 36(a2),d2                                  ; +$0526 : 242A0024
    mulu.w d1,d2                                      ; +$052A : C4C1
L_007216:
    move.l a0,d0                                      ; +$052C : 2008
    add.l d2,d0                                       ; +$052E : D082
    bcs.w L_0072D8                                    ; +$0530 : 650000BC
    cmp.l 80(a2),d0                                   ; +$0534 : B0AA0050
    bgt.w L_0072D8                                    ; +$0538 : 6E0000B4
L_007226:
    move.l 92(a2),d2                                  ; +$053C : 242A005C
    tst.l d2                                          ; +$0540 : 4A82
    bne.w L_007244                                    ; +$0542 : 66000016
    move.l 76(a2),d0                                  ; +$0546 : 202A004C
    move.l d0,96(a2)                                  ; +$054A : 25400060
    add.l 36(a2),d0                                   ; +$054E : D0AA0024
    move.l d0,76(a2)                                  ; +$0552 : 2540004C
    bra.w L_00725A                                    ; +$0556 : 60000018
L_007244:
    move.l 76(a2),d0                                  ; +$055A : 202A004C
    move.l 96(a2),d1                                  ; +$055E : 222A0060
    cmp.l d1,d0                                       ; +$0562 : B081
    bne.w L_00725A                                    ; +$0564 : 6600000A
    add.l 36(a2),d0                                   ; +$0568 : D0AA0024
    move.l d0,76(a2)                                  ; +$056C : 2540004C
L_00725A:
    move.l 44(a2),d0                                  ; +$0570 : 202A002C
    tst.l d0                                          ; +$0574 : 4A80
    beq.w L_007290                                    ; +$0576 : 6700002E
    move.l 84(a2),d1                                  ; +$057A : 222A0054
    addq.l #1,d1                                      ; +$057E : 5281
    cmp.l 40(a2),d1                                   ; +$0580 : B2AA0028
    bne.w L_007290                                    ; +$0584 : 66000020
    movea.l 96(a2),a0                                 ; +$0588 : 206A0060
    move.l 36(a2),d1                                  ; +$058C : 222A0024
    lsr.l #1,d1                                       ; +$0590 : E289
L_00727C:
    move.l #$00000000,d2                              ; +$0592 : 243C00000000
    move.w (a0)+,d2                                   ; +$0598 : 3418
    and.w d0,d2                                       ; +$059A : C440
    bne.w L_0072D8                                    ; +$059C : 66000050
    subq.l #1,d1                                      ; +$05A0 : 5381
    bne.w L_00727C                                    ; +$05A2 : 6600FFEE
L_007290:
    move.l 72(a2),d0                                  ; +$05A6 : 202A0048
    tst.l d0                                          ; +$05AA : 4A80
    beq.w L_00729E                                    ; +$05AC : 67000006
    bsr.w L_0072E0                                    ; +$05B0 : 61000044
L_00729E:
    move.l 88(a2),d0                                  ; +$05B4 : 202A0058
    subq.l #1,d0                                      ; +$05B8 : 5380
    move.l d0,88(a2)                                  ; +$05BA : 25400058
    move.l 84(a2),d0                                  ; +$05BE : 202A0054
    addq.l #1,d0                                      ; +$05C2 : 5280
    move.l d0,84(a2)                                  ; +$05C4 : 25400054
    bra.w L_0071A0                                    ; +$05C8 : 6000FEEC
L_0072B6:
    move.l 76(a2),d0                                  ; +$05CC : 202A004C
    cmp.l 80(a2),d0                                   ; +$05D0 : B0AA0050
    bne.w L_0072D8                                    ; +$05D4 : 66000018
    move.l 68(a2),d0                                  ; +$05D8 : 202A0044
    addq.l #1,d0                                      ; +$05DC : 5280
    move.l d0,68(a2)                                  ; +$05DE : 25400044
    bra.w L_007118                                    ; +$05E2 : 6000FE4A
L_0072D0:
    move.l #$00000001,d0                              ; +$05E6 : 203C00000001
    rts                                               ; +$05EC : 4E75
L_0072D8:
    move.l #$00000000,d0                              ; +$05EE : 203C00000000
    rts                                               ; +$05F4 : 4E75
L_0072E0:
    move.l 68(a2),d0                                  ; +$05F6 : 202A0044
    add.l 4(a2),d0                                    ; +$05FA : D0AA0004
    tst.l d0                                          ; +$05FE : 4A80
    bmi.w L_0073EC                                    ; +$0600 : 6B000100
    cmp.l 56(a2),d0                                   ; +$0604 : B0AA0038
    bge.w L_0073EC                                    ; +$0608 : 6C0000F8
    move.l d0,108(a2)                                 ; +$060C : 2540006C
    move.l #$00000000,100(a2)                         ; +$0610 : 257C000000000064
L_007302:
    move.l 100(a2),d0                                 ; +$0618 : 202A0064
    cmpi.l #$00000010,d0                              ; +$061C : 0C8000000010
    bge.w L_0073EC                                    ; +$0622 : 6C0000DE
    move.l 84(a2),d1                                  ; +$0626 : 222A0054
    lsl.l #4,d1                                       ; +$062A : E989
    add.l d0,d1                                       ; +$062C : D280
    cmp.l 20(a2),d1                                   ; +$062E : B2AA0014
    bge.w L_0073EC                                    ; +$0632 : 6C0000CE
    add.l 8(a2),d1                                    ; +$0636 : D2AA0008
    tst.l d1                                          ; +$063A : 4A81
    bmi.w L_0073DE                                    ; +$063C : 6B0000B6
    cmp.l 52(a2),d1                                   ; +$0640 : B2AA0034
    bge.w L_0073DE                                    ; +$0644 : 6C0000AE
    move.l d1,104(a2)                                 ; +$0648 : 25410068
    move.l #$0000000F,d0                              ; +$064C : 203C0000000F
    sub.l 100(a2),d0                                  ; +$0652 : 90AA0064
    move.l d0,124(a2)                                 ; +$0656 : 2540007C
    move.l (a2),d2                                    ; +$065A : 2412
    tst.l d2                                          ; +$065C : 4A82
    beq.w L_00735E                                    ; +$065E : 67000014
    movea.l 96(a2),a0                                 ; +$0662 : 206A0060
    move.l #$00000000,d2                              ; +$0666 : 243C00000000
    move.w (a0),d2                                    ; +$066C : 3410
    btst d0,d2                                        ; +$066E : 0102
    beq.w L_0073DE                                    ; +$0670 : 67000082
L_00735E:
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
    beq.w L_00739A                                    ; +$06AA : 67000004
    addq.l #2,a1                                      ; +$06AE : 5489
L_00739A:
    movea.l 64(a2),a6                                 ; +$06B0 : 2C6A0040
    addq.l #8,a6                                      ; +$06B4 : 508E
    move.l 28(a2),d0                                  ; +$06B6 : 202A001C
    move.l d0,120(a2)                                 ; +$06BA : 25400078
L_0073A8:
    move.l #$00000000,d2                              ; +$06BE : 243C00000000
    move.w (a1)+,d2                                   ; +$06C4 : 3419
    movea.l (a6)+,a0                                  ; +$06C6 : 205E
    move.l a0,d4                                      ; +$06C8 : 2808
    add.l 112(a2),d4                                  ; +$06CA : D8AA0070
    movea.l d4,a0                                     ; +$06CE : 2044
    move.l 124(a2),d0                                 ; +$06D0 : 202A007C
    move.l 116(a2),d1                                 ; +$06D4 : 222A0074
    btst d0,d2                                        ; +$06D8 : 0102
    beq.w L_0073CE                                    ; +$06DA : 67000008
    bset d1,(a0)                                      ; +$06DE : 03D0
    bra.w L_0073D0                                    ; +$06E0 : 60000004
L_0073CE:
    bclr d1,(a0)                                      ; +$06E4 : 0390
L_0073D0:
    move.l 120(a2),d0                                 ; +$06E6 : 202A0078
    subq.l #1,d0                                      ; +$06EA : 5380
    move.l d0,120(a2)                                 ; +$06EC : 25400078
    bne.w L_0073A8                                    ; +$06F0 : 6600FFCC
L_0073DE:
    move.l 100(a2),d0                                 ; +$06F4 : 202A0064
    addq.l #1,d0                                      ; +$06F8 : 5280
    move.l d0,100(a2)                                 ; +$06FA : 25400064
    bra.w L_007302                                    ; +$06FE : 6000FF18
L_0073EC:
    rts                                               ; +$0702 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 56 : aga image capture --------
Entry_56:
Aga_Image_Capture:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -224(a7),a7                                   ; +$0004 : 4FEFFF20
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,20(a2)                                  ; +$000A : 25430014
    move.l (a3)+,d7                                   ; +$000E : 2E1B
    move.l d7,16(a2)                                  ; +$0010 : 25470010
    move.l (a3)+,d7                                   ; +$0014 : 2E1B
    move.l d7,12(a2)                                  ; +$0016 : 2547000C
    move.l (a3)+,d7                                   ; +$001A : 2E1B
    move.l d7,8(a2)                                   ; +$001C : 25470008
    move.l (a3)+,d7                                   ; +$0020 : 2E1B
    move.l d7,4(a2)                                   ; +$0022 : 25470004
    move.l (a3)+,d7                                   ; +$0026 : 2E1B
    move.l d7,(a2)                                    ; +$0028 : 2487
    move.l #$00000000,52(a2)                          ; +$002A : 257C000000000034
    move.l #$00000000,64(a2)                          ; +$0032 : 257C000000000040
    move.l #$00000000,88(a2)                          ; +$003A : 257C000000000058
    move.l #$00000000,d3                              ; +$0042 : 263C00000000
    move.l (a2),d0                                    ; +$0048 : 2012
    cmpi.l #$00000005,d0                              ; +$004A : 0C8000000005
    bcs.w L_007876                                    ; +$0050 : 65000432
    cmpi.l #$0000FFFF,d0                              ; +$0054 : 0C800000FFFF
    bhi.w L_007876                                    ; +$005A : 62000428
    movea.l 456(a5),a4                                ; +$005E : 286D01C8
    move.l a4,d0                                      ; +$0062 : 200C
    tst.l d0                                          ; +$0064 : 4A80
    beq.w L_007876                                    ; +$0066 : 6700041C
    move.l a4,24(a2)                                  ; +$006A : 254C0018
    move.l (a4),d0                                    ; +$006E : 2014
    tst.l d0                                          ; +$0070 : 4A80
    beq.w L_007876                                    ; +$0072 : 67000410
    move.l 8(a4),d0                                   ; +$0076 : 202C0008
    tst.l d0                                          ; +$007A : 4A80
    beq.w L_007876                                    ; +$007C : 67000406
    move.l 32(a4),d0                                  ; +$0080 : 202C0020
    tst.l d0                                          ; +$0084 : 4A80
    beq.w L_007876                                    ; +$0086 : 670003FC
    movea.l 32(a4),a0                                 ; +$008A : 206C0020
    move.l a0,28(a2)                                  ; +$008E : 2548001C
    move.l 12(a4),d0                                  ; +$0092 : 202C000C
    tst.l d0                                          ; +$0096 : 4A80
    ble.w L_007876                                    ; +$0098 : 6F0003EA
    cmpi.l #$00001000,d0                              ; +$009C : 0C8000001000
    bhi.w L_007876                                    ; +$00A2 : 620003E0
    move.l d0,44(a2)                                  ; +$00A6 : 2540002C
    move.l 16(a4),d0                                  ; +$00AA : 202C0010
    tst.l d0                                          ; +$00AE : 4A80
    ble.w L_007876                                    ; +$00B0 : 6F0003D2
    cmpi.l #$00001000,d0                              ; +$00B4 : 0C8000001000
    bhi.w L_007876                                    ; +$00BA : 620003C8
    move.l d0,48(a2)                                  ; +$00BE : 25400030
    move.l 28(a4),d0                                  ; +$00C2 : 202C001C
    tst.l d0                                          ; +$00C6 : 4A80
    ble.w L_007876                                    ; +$00C8 : 6F0003BA
    cmpi.l #$00000008,d0                              ; +$00CC : 0C8000000008
    bhi.w L_007876                                    ; +$00D2 : 620003B0
    move.l d0,40(a2)                                  ; +$00D6 : 25400028
    move.l 4(a2),d0                                   ; +$00DA : 202A0004
    tst.l d0                                          ; +$00DE : 4A80
    bmi.w L_007876                                    ; +$00E0 : 6B0003A2
    move.l 8(a2),d0                                   ; +$00E4 : 202A0008
    tst.l d0                                          ; +$00E8 : 4A80
    bmi.w L_007876                                    ; +$00EA : 6B000398
    move.l 12(a2),d0                                  ; +$00EE : 202A000C
    tst.l d0                                          ; +$00F2 : 4A80
    ble.w L_007876                                    ; +$00F4 : 6F00038E
    cmpi.l #$00001000,d0                              ; +$00F8 : 0C8000001000
    bhi.w L_007876                                    ; +$00FE : 62000384
    move.l 16(a2),d0                                  ; +$0102 : 202A0010
    tst.l d0                                          ; +$0106 : 4A80
    ble.w L_007876                                    ; +$0108 : 6F00037A
    cmpi.l #$00001000,d0                              ; +$010C : 0C8000001000
    bhi.w L_007876                                    ; +$0112 : 62000370
    move.l 44(a2),d0                                  ; +$0116 : 202A002C
    sub.l 12(a2),d0                                   ; +$011A : 90AA000C
    bmi.w L_007876                                    ; +$011E : 6B000364
    move.l 4(a2),d1                                   ; +$0122 : 222A0004
    cmp.l d0,d1                                       ; +$0126 : B280
    bgt.w L_007876                                    ; +$0128 : 6E00035A
    move.l 48(a2),d0                                  ; +$012C : 202A0030
    sub.l 16(a2),d0                                   ; +$0130 : 90AA0010
    bmi.w L_007876                                    ; +$0134 : 6B00034E
    move.l 8(a2),d1                                   ; +$0138 : 222A0008
    cmp.l d0,d1                                       ; +$013C : B280
    bgt.w L_007876                                    ; +$013E : 6E000344
    move.l 12(a2),d0                                  ; +$0142 : 202A000C
    move.l 16(a2),d1                                  ; +$0146 : 222A0010
    mulu.w d1,d0                                      ; +$014A : C0C1
    cmpi.l #$00400000,d0                              ; +$014C : 0C8000400000
    bhi.w L_007876                                    ; +$0152 : 62000330
    move.l 20(a2),d1                                  ; +$0156 : 222A0014
    cmpi.l #$FFFFFFFF,d1                              ; +$015A : 0C81FFFFFFFF
    beq.w L_007580                                    ; +$0160 : 6700002C
    tst.l d1                                          ; +$0164 : 4A81
    bmi.w L_007876                                    ; +$0166 : 6B00031C
    move.l 40(a2),d0                                  ; +$016A : 202A0028
    move.l #$00000001,d7                              ; +$016E : 2E3C00000001
L_007566:
    lsl.l #1,d7                                       ; +$0174 : E38F
    subq.l #1,d0                                      ; +$0176 : 5380
    bne.w L_007566                                    ; +$0178 : 6600FFFA
    cmp.l d7,d1                                       ; +$017C : B287
    bcc.w L_007876                                    ; +$017E : 64000304
    move.l #$00000001,84(a2)                          ; +$0182 : 257C000000010054
    bra.w L_007588                                    ; +$018A : 6000000A
L_007580:
    move.l #$00000000,84(a2)                          ; +$018E : 257C000000000054
L_007588:
    movea.l 28(a2),a0                                 ; +$0196 : 206A001C
    move.l 8(a0),d0                                   ; +$019A : 20280008
    tst.l d0                                          ; +$019E : 4A80
    beq.w L_0075A6                                    ; +$01A0 : 67000012
    cmpi.l #$00000001,d0                              ; +$01A4 : 0C8000000001
    bne.w L_007876                                    ; +$01AA : 660002D8
    movea.l (a0),a1                                   ; +$01AE : 2250
    bra.w L_0075AA                                    ; +$01B0 : 60000006
L_0075A6:
    movea.l 4(a0),a1                                  ; +$01B4 : 22680004
L_0075AA:
    move.l a1,d0                                      ; +$01B8 : 2009
    tst.l d0                                          ; +$01BA : 4A80
    beq.w L_007876                                    ; +$01BC : 670002C6
    movea.l (a1),a0                                   ; +$01C0 : 2051
    move.l a0,d0                                      ; +$01C2 : 2008
    tst.l d0                                          ; +$01C4 : 4A80
    beq.w L_007876                                    ; +$01C6 : 670002BC
    move.l a0,32(a2)                                  ; +$01CA : 25480020
    move.l #$00000000,d0                              ; +$01CE : 203C00000000
    move.w (a0),d0                                    ; +$01D4 : 3010
    cmpi.l #$00000002,d0                              ; +$01D6 : 0C8000000002
    bcs.w L_007876                                    ; +$01DC : 650002A6
    cmpi.l #$0000FFFE,d0                              ; +$01E0 : 0C800000FFFE
    bhi.w L_007876                                    ; +$01E6 : 6200029C
    move.l d0,d1                                      ; +$01EA : 2200
    andi.l #$00000001,d1                              ; +$01EC : 028100000001
    bne.w L_007876                                    ; +$01F2 : 66000290
    move.l d0,36(a2)                                  ; +$01F6 : 25400024
    lsl.l #3,d0                                       ; +$01FA : E788
    cmp.l 44(a2),d0                                   ; +$01FC : B0AA002C
    blt.w L_007876                                    ; +$0200 : 6D000282
    move.l #$00000000,d0                              ; +$0204 : 203C00000000
    move.w 2(a0),d0                                   ; +$020A : 30280002
    cmp.l 48(a2),d0                                   ; +$020E : B0AA0030
    blt.w L_007876                                    ; +$0212 : 6D000270
    move.l #$00000000,d0                              ; +$0216 : 203C00000000
    move.b 5(a0),d0                                   ; +$021C : 10280005
    cmp.l 40(a2),d0                                   ; +$0220 : B0AA0028
    bne.w L_007876                                    ; +$0224 : 6600025E
    movea.l a0,a1                                     ; +$0228 : 2248
    addq.l #8,a1                                      ; +$022A : 5089
    move.l 40(a2),d0                                  ; +$022C : 202A0028
L_007622:
    move.l (a1)+,d1                                   ; +$0230 : 2219
    tst.l d1                                          ; +$0232 : 4A81
    beq.w L_007876                                    ; +$0234 : 6700024E
    cmpi.l #$FFFFFFFF,d1                              ; +$0238 : 0C81FFFFFFFF
    beq.w L_007876                                    ; +$023E : 67000244
    subq.l #1,d0                                      ; +$0242 : 5380
    bne.w L_007622                                    ; +$0244 : 6600FFEA
    move.l (a2),d0                                    ; +$0248 : 2012
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0250 : 2008
    tst.l d0                                          ; +$0252 : 4A80
    bne.w L_007876                                    ; +$0254 : 6600022E
    movea.l 28(a2),a4                                 ; +$0258 : 286A001C
    move.l 20(a4),d0                                  ; +$025C : 202C0014
    andi.l #$00000001,d0                              ; +$0260 : 028000000001
    beq.w L_007688                                    ; +$0266 : 6700002E
    movea.l 12(a4),a0                                 ; +$026A : 206C000C
    move.l a0,d0                                      ; +$026E : 2008
    tst.l d0                                          ; +$0270 : 4A80
    beq.w L_007876                                    ; +$0272 : 67000210
    movea.l $0004.w,a6                                ; +$0276 : 2C780004
    jsr -372(a6)                                      ; +$027A : 4EAEFE8C
    tst.l d0                                          ; +$027E : 4A80
    beq.w L_007876                                    ; +$0280 : 67000202
    movea.l 28(a2),a4                                 ; +$0284 : 286A001C
    move.l 20(a4),d0                                  ; +$0288 : 202C0014
    andi.l #$FFFFFFFE,d0                              ; +$028C : 0280FFFFFFFE
    move.l d0,20(a4)                                  ; +$0292 : 29400014
L_007688:
    move.l 12(a2),d0                                  ; +$0296 : 202A000C
    addi.l #$0000000F,d0                              ; +$029A : 06800000000F
    lsr.l #4,d0                                       ; +$02A0 : E888
    move.l 40(a2),d1                                  ; +$02A2 : 222A0028
    add.l 84(a2),d1                                   ; +$02A6 : D2AA0054
    lsl.l #1,d1                                       ; +$02AA : E389
    addq.l #1,d1                                      ; +$02AC : 5281
    mulu.w d1,d0                                      ; +$02AE : C0C1
    move.l d0,56(a2)                                  ; +$02B0 : 25400038
    move.l d0,d6                                      ; +$02B4 : 2C00
    move.l #$00000001,d1                              ; +$02B6 : 223C00000001
    movea.l $0004.w,a6                                ; +$02BC : 2C780004
    jsr -684(a6)                                      ; +$02C0 : 4EAEFD54
    tst.l d0                                          ; +$02C4 : 4A80
    beq.w L_007876                                    ; +$02C6 : 670001BC
    move.l d0,52(a2)                                  ; +$02CA : 25400034
    move.l 16(a2),d0                                  ; +$02CE : 202A0010
    addq.l #1,d0                                      ; +$02D2 : 5280
    lsl.l #2,d0                                       ; +$02D4 : E588
    addi.l #$00000020,d0                              ; +$02D6 : 068000000020
    move.l d0,92(a2)                                  ; +$02DC : 2540005C
    move.l d0,60(a2)                                  ; +$02E0 : 2540003C
    move.l #$00000000,68(a2)                          ; +$02E4 : 257C000000000044
L_0076DE:
    move.l 68(a2),d0                                  ; +$02EC : 202A0044
    cmp.l 16(a2),d0                                   ; +$02F0 : B0AA0010
    bge.w L_007722                                    ; +$02F4 : 6C00003A
    movea.l 52(a2),a1                                 ; +$02F8 : 226A0034
    move.l 56(a2),d6                                  ; +$02FC : 2C2A0038
    bsr.w L_00789A                                    ; +$0300 : 610001A6
    tst.l d0                                          ; +$0304 : 4A80
    beq.w L_007876                                    ; +$0306 : 6700017C
    move.l 60(a2),d1                                  ; +$030A : 222A003C
    add.l d0,d1                                       ; +$030E : D280
    bcs.w L_007876                                    ; +$0310 : 65000172
    cmpi.l #$01000000,d1                              ; +$0314 : 0C8101000000
    bhi.w L_007876                                    ; +$031A : 62000168
    move.l d1,60(a2)                                  ; +$031E : 2541003C
    move.l 68(a2),d0                                  ; +$0322 : 202A0044
    addq.l #1,d0                                      ; +$0326 : 5280
    move.l d0,68(a2)                                  ; +$0328 : 25400044
    bra.w L_0076DE                                    ; +$032C : 6000FFBE
L_007722:
    move.l (a2),d0                                    ; +$0330 : 2012
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0338 : 2008
    tst.l d0                                          ; +$033A : 4A80
    bne.w L_007876                                    ; +$033C : 66000146
    move.l (a2),d0                                    ; +$0340 : 2012
    move.l #$00000001,d1                              ; +$0342 : 223C00000001
    move.l 60(a2),d2                                  ; +$0348 : 242A003C
    lea L_007BB8(pc),a0                               ; +$034C : 41FA0478
    dc.b $FE,$11,$F7,$00,$03,$30
    tst.l d0                                          ; +$0356 : 4A80
    beq.w L_007876                                    ; +$0358 : 6700012A
    move.l d0,64(a2)                                  ; +$035C : 25400040
    move.l 60(a2),d1                                  ; +$0360 : 222A003C
    add.l d1,d0                                       ; +$0364 : D081
    bcs.w L_007862                                    ; +$0366 : 65000108
    move.l d0,80(a2)                                  ; +$036A : 25400050
    movea.l 64(a2),a0                                 ; +$036E : 206A0040
    move.l #$41474150,(a0)                            ; +$0372 : 20BC41474150
    move.w #$4943,4(a0)                               ; +$0378 : 317C49430004
    move.w #$0001,6(a0)                               ; +$037E : 317C00010006
    move.l 84(a2),d0                                  ; +$0384 : 202A0054
    move.w d0,8(a0)                                   ; +$0388 : 31400008
    move.w #$0001,10(a0)                              ; +$038C : 317C0001000A
    move.l 12(a2),d0                                  ; +$0392 : 202A000C
    move.w d0,12(a0)                                  ; +$0396 : 3140000C
    move.l 16(a2),d0                                  ; +$039A : 202A0010
    move.w d0,14(a0)                                  ; +$039E : 3140000E
    move.l 40(a2),d0                                  ; +$03A2 : 202A0028
    move.w d0,16(a0)                                  ; +$03A6 : 31400010
    move.l 40(a2),d0                                  ; +$03AA : 202A0028
    add.l 84(a2),d0                                   ; +$03AE : D0AA0054
    lsl.l #1,d0                                       ; +$03B2 : E388
    move.w d0,18(a0)                                  ; +$03B4 : 31400012
    move.l #$00000020,20(a0)                          ; +$03B8 : 217C000000200014
    move.l 92(a2),d0                                  ; +$03C0 : 202A005C
    move.l d0,24(a0)                                  ; +$03C4 : 21400018
    move.l 60(a2),d0                                  ; +$03C8 : 202A003C
    move.l d0,28(a0)                                  ; +$03CC : 2140001C
    move.l 64(a2),d0                                  ; +$03D0 : 202A0040
    addi.l #$00000020,d0                              ; +$03D4 : 068000000020
    move.l d0,72(a2)                                  ; +$03DA : 25400048
    move.l 64(a2),d0                                  ; +$03DE : 202A0040
    add.l 92(a2),d0                                   ; +$03E2 : D0AA005C
    move.l d0,76(a2)                                  ; +$03E6 : 2540004C
    move.l #$00000000,68(a2)                          ; +$03EA : 257C000000000044
L_0077E4:
    move.l 68(a2),d0                                  ; +$03F2 : 202A0044
    cmp.l 16(a2),d0                                   ; +$03F6 : B0AA0010
    bge.w L_00783A                                    ; +$03FA : 6C00004C
    move.l 76(a2),d0                                  ; +$03FE : 202A004C
    sub.l 64(a2),d0                                   ; +$0402 : 90AA0040
    movea.l 72(a2),a4                                 ; +$0406 : 286A0048
    move.l d0,(a4)+                                   ; +$040A : 28C0
    move.l a4,72(a2)                                  ; +$040C : 254C0048
    movea.l 76(a2),a1                                 ; +$0410 : 226A004C
    move.l 80(a2),d6                                  ; +$0414 : 2C2A0050
    sub.l a1,d6                                       ; +$0418 : 9C89
    bsr.w L_00789A                                    ; +$041A : 6100008C
    tst.l d0                                          ; +$041E : 4A80
    beq.w L_007862                                    ; +$0420 : 6700004E
    move.l 76(a2),d1                                  ; +$0424 : 222A004C
    add.l d0,d1                                       ; +$0428 : D280
    bcs.w L_007862                                    ; +$042A : 65000044
    cmp.l 80(a2),d1                                   ; +$042E : B2AA0050
    bhi.w L_007862                                    ; +$0432 : 6200003C
    move.l d1,76(a2)                                  ; +$0436 : 2541004C
    move.l 68(a2),d0                                  ; +$043A : 202A0044
    addq.l #1,d0                                      ; +$043E : 5280
    move.l d0,68(a2)                                  ; +$0440 : 25400044
    bra.w L_0077E4                                    ; +$0444 : 6000FFAC
L_00783A:
    move.l 76(a2),d0                                  ; +$0448 : 202A004C
    cmp.l 80(a2),d0                                   ; +$044C : B0AA0050
    bne.w L_007862                                    ; +$0450 : 6600001E
    movea.l 72(a2),a4                                 ; +$0454 : 286A0048
    move.l 60(a2),d0                                  ; +$0458 : 202A003C
    move.l d0,(a4)                                    ; +$045C : 2880
    dc.b $FE,$11,$F7,$00,$03,$33
    move.l #$00000001,88(a2)                          ; +$0464 : 257C000000010058
    bra.w L_007876                                    ; +$046C : 60000016
L_007862:
    move.l (a2),d0                                    ; +$0470 : 2012
    dc.b $FE,$11,$F7,$00,$03,$20
    move.l #$00000000,64(a2)                          ; +$0478 : 257C000000000040
    bra.w L_007876                                    ; +$0480 : 60000002
L_007876:
    movea.l 52(a2),a1                                 ; +$0484 : 226A0034
    move.l a1,d0                                      ; +$0488 : 2009
    tst.l d0                                          ; +$048A : 4A80
    beq.w L_00788A                                    ; +$048C : 6700000A
    movea.l $0004.w,a6                                ; +$0490 : 2C780004
    jsr -690(a6)                                      ; +$0494 : 4EAEFD4E
L_00788A:
    move.l 88(a2),d3                                  ; +$0498 : 262A0058
    lea 224(a7),a7                                    ; +$049C : 4FEF00E0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$04A0 : 4CDF77F7
    moveq #0,d2                                       ; +$04A4 : 7400
    rts                                               ; +$04A6 : 4E75
L_00789A:
    movea.l 32(a2),a0                                 ; +$04A8 : 206A0020
    addq.l #8,a0                                      ; +$04AC : 5088
    move.l 4(a2),d0                                   ; +$04AE : 202A0004
    move.l 8(a2),d1                                   ; +$04B2 : 222A0008
    add.l 68(a2),d1                                   ; +$04B6 : D2AA0044
    move.l 12(a2),d2                                  ; +$04BA : 242A000C
    move.l 40(a2),d3                                  ; +$04BE : 262A0028
    move.l 36(a2),d4                                  ; +$04C2 : 282A0024
    move.l 20(a2),d5                                  ; +$04C6 : 2A2A0014
    bsr.w L_0078C2                                    ; +$04CA : 61000004
    rts                                               ; +$04CE : 4E75
L_0078C2:
    movem.l d1-d7/a0-a6,-(a7)                         ; +$04D0 : 48E77FFE
    lea -160(a7),a7                                   ; +$04D4 : 4FEFFF60
    movea.l a7,a2                                     ; +$04D8 : 244F
    move.l a0,(a2)                                    ; +$04DA : 2488
    move.l a1,4(a2)                                   ; +$04DC : 25490004
    move.l a1,8(a2)                                   ; +$04E0 : 25490008
    move.l d0,16(a2)                                  ; +$04E4 : 25400010
    move.l d1,20(a2)                                  ; +$04E8 : 25410014
    move.l d2,24(a2)                                  ; +$04EC : 25420018
    move.l d3,28(a2)                                  ; +$04F0 : 2543001C
    move.l d4,32(a2)                                  ; +$04F4 : 25440020
    move.l d5,36(a2)                                  ; +$04F8 : 25450024
    move.l #$00000000,76(a2)                          ; +$04FC : 257C00000000004C
    move.l #$00000000,d0                              ; +$0504 : 203C00000000
    move.l 16(a2),d1                                  ; +$050A : 222A0010
    tst.l d1                                          ; +$050E : 4A81
    bmi.w L_007BA8                                    ; +$0510 : 6B0002A4
    cmpi.l #$00001000,d1                              ; +$0514 : 0C8100001000
    bhi.w L_007BA8                                    ; +$051A : 6200029A
    move.l 20(a2),d1                                  ; +$051E : 222A0014
    tst.l d1                                          ; +$0522 : 4A81
    bmi.w L_007BA8                                    ; +$0524 : 6B000290
    cmpi.l #$00001000,d1                              ; +$0528 : 0C8100001000
    bhi.w L_007BA8                                    ; +$052E : 62000286
    move.l 24(a2),d1                                  ; +$0532 : 222A0018
    tst.l d1                                          ; +$0536 : 4A81
    ble.w L_007BA8                                    ; +$0538 : 6F00027C
    cmpi.l #$00001000,d1                              ; +$053C : 0C8100001000
    bhi.w L_007BA8                                    ; +$0542 : 62000272
    add.l 16(a2),d1                                   ; +$0546 : D2AA0010
    cmpi.l #$00001000,d1                              ; +$054A : 0C8100001000
    bhi.w L_007BA8                                    ; +$0550 : 62000264
    move.l 28(a2),d1                                  ; +$0554 : 222A001C
    tst.l d1                                          ; +$0558 : 4A81
    ble.w L_007BA8                                    ; +$055A : 6F00025A
    cmpi.l #$00000008,d1                              ; +$055E : 0C8100000008
    bhi.w L_007BA8                                    ; +$0564 : 62000250
    move.l 32(a2),d1                                  ; +$0568 : 222A0020
    cmpi.l #$00000002,d1                              ; +$056C : 0C8100000002
    bcs.w L_007BA8                                    ; +$0572 : 65000242
    cmpi.l #$0000FFFE,d1                              ; +$0576 : 0C810000FFFE
    bhi.w L_007BA8                                    ; +$057C : 62000238
    move.l d1,d0                                      ; +$0580 : 2001
    andi.l #$00000001,d0                              ; +$0582 : 028000000001
    bne.w L_007BA8                                    ; +$0588 : 6600022C
    move.l 36(a2),d1                                  ; +$058C : 222A0024
    cmpi.l #$FFFFFFFF,d1                              ; +$0590 : 0C81FFFFFFFF
    beq.w L_0079B6                                    ; +$0596 : 6700002C
    tst.l d1                                          ; +$059A : 4A81
    bmi.w L_007BA8                                    ; +$059C : 6B000218
    move.l 28(a2),d0                                  ; +$05A0 : 202A001C
    move.l #$00000001,d7                              ; +$05A4 : 2E3C00000001
L_00799C:
    lsl.l #1,d7                                       ; +$05AA : E38F
    subq.l #1,d0                                      ; +$05AC : 5380
    bne.w L_00799C                                    ; +$05AE : 6600FFFA
    cmp.l d7,d1                                       ; +$05B2 : B287
    bcc.w L_007BA8                                    ; +$05B4 : 64000200
    move.l #$00000001,52(a2)                          ; +$05B8 : 257C000000010034
    bra.w L_0079BE                                    ; +$05C0 : 6000000A
L_0079B6:
    move.l #$00000000,52(a2)                          ; +$05C4 : 257C000000000034
L_0079BE:
    tst.l d6                                          ; +$05CC : 4A86
    ble.w L_007BA8                                    ; +$05CE : 6F0001E6
    move.l a1,d0                                      ; +$05D2 : 2009
    add.l d6,d0                                       ; +$05D4 : D086
    bcs.w L_007BA8                                    ; +$05D6 : 650001DE
    move.l d0,12(a2)                                  ; +$05DA : 2540000C
    move.l 20(a2),d0                                  ; +$05DE : 202A0014
    move.l 32(a2),d1                                  ; +$05E2 : 222A0020
    mulu.w d1,d0                                      ; +$05E6 : C0C1
    move.l d0,40(a2)                                  ; +$05E8 : 25400028
    move.l 24(a2),d0                                  ; +$05EC : 202A0018
    addi.l #$0000000F,d0                              ; +$05F0 : 06800000000F
    lsr.l #4,d0                                       ; +$05F6 : E888
    move.l d0,44(a2)                                  ; +$05F8 : 2540002C
    move.l 28(a2),d0                                  ; +$05FC : 202A001C
    add.l 52(a2),d0                                   ; +$0600 : D0AA0034
    lsl.l #1,d0                                       ; +$0604 : E388
    move.l d0,48(a2)                                  ; +$0606 : 25400030
    move.l #$00000000,56(a2)                          ; +$060A : 257C000000000038
L_007A04:
    move.l 56(a2),d0                                  ; +$0612 : 202A0038
    cmp.l 44(a2),d0                                   ; +$0616 : B0AA002C
    bge.w L_007B9A                                    ; +$061A : 6C00018C
    lea 96(a2),a4                                     ; +$061E : 49EA0060
    move.l 48(a2),d5                                  ; +$0622 : 2A2A0030
    lsr.l #1,d5                                       ; +$0626 : E28D
L_007A1A:
    move.w #$0000,(a4)+                               ; +$0628 : 38FC0000
    subq.l #1,d5                                      ; +$062C : 5385
    bne.w L_007A1A                                    ; +$062E : 6600FFF8
    move.l #$00000000,60(a2)                          ; +$0632 : 257C00000000003C
    move.l #$00008000,d4                              ; +$063A : 283C00008000
L_007A32:
    move.l 60(a2),d5                                  ; +$0640 : 2A2A003C
    cmpi.l #$00000010,d5                              ; +$0644 : 0C8500000010
    bge.w L_007B06                                    ; +$064A : 6C0000C8
    move.l 56(a2),d0                                  ; +$064E : 202A0038
    lsl.l #4,d0                                       ; +$0652 : E988
    add.l d5,d0                                       ; +$0654 : D085
    cmp.l 24(a2),d0                                   ; +$0656 : B0AA0018
    bge.w L_007B06                                    ; +$065A : 6C0000B8
    add.l 16(a2),d0                                   ; +$065E : D0AA0010
    move.l d0,d1                                      ; +$0662 : 2200
    lsr.l #3,d1                                       ; +$0664 : E689
    add.l 40(a2),d1                                   ; +$0666 : D2AA0028
    move.l d1,68(a2)                                  ; +$066A : 25410044
    andi.l #$00000007,d0                              ; +$066E : 028000000007
    move.l #$00000007,d3                              ; +$0674 : 263C00000007
    sub.l d0,d3                                       ; +$067A : 9680
    move.l d3,64(a2)                                  ; +$067C : 25430040
    movea.l (a2),a0                                   ; +$0680 : 2052
    lea 96(a2),a4                                     ; +$0682 : 49EA0060
    move.l 52(a2),d0                                  ; +$0686 : 202A0034
    tst.l d0                                          ; +$068A : 4A80
    beq.w L_007A84                                    ; +$068C : 67000004
    addq.l #2,a4                                      ; +$0690 : 548C
L_007A84:
    move.l 28(a2),d5                                  ; +$0692 : 2A2A001C
    move.l #$00000001,d7                              ; +$0696 : 2E3C00000001
    move.l #$00000000,d6                              ; +$069C : 2C3C00000000
L_007A94:
    movea.l (a0)+,a5                                  ; +$06A2 : 2A58
    move.l a5,d0                                      ; +$06A4 : 200D
    move.l 68(a2),d1                                  ; +$06A6 : 222A0044
    add.l d1,d0                                       ; +$06AA : D081
    movea.l d0,a5                                     ; +$06AC : 2A40
    move.l #$00000000,d0                              ; +$06AE : 203C00000000
    move.b (a5),d0                                    ; +$06B4 : 1015
    move.l 64(a2),d3                                  ; +$06B6 : 262A0040
    btst d3,d0                                        ; +$06BA : 0700
    beq.w L_007AC0                                    ; +$06BC : 67000010
    move.l #$00000000,d0                              ; +$06C0 : 203C00000000
    move.w (a4),d0                                    ; +$06C6 : 3014
    or.w d4,d0                                        ; +$06C8 : 8044
    move.w d0,(a4)                                    ; +$06CA : 3880
    or.l d7,d6                                        ; +$06CC : 8C87
L_007AC0:
    addq.l #2,a4                                      ; +$06CE : 548C
    lsl.l #1,d7                                       ; +$06D0 : E38F
    subq.l #1,d5                                      ; +$06D2 : 5385
    bne.w L_007A94                                    ; +$06D4 : 6600FFCC
    move.l d6,72(a2)                                  ; +$06D8 : 25460048
    move.l 52(a2),d0                                  ; +$06DC : 202A0034
    tst.l d0                                          ; +$06E0 : 4A80
    beq.w L_007AF6                                    ; +$06E2 : 67000020
    move.l 36(a2),d0                                  ; +$06E6 : 202A0024
    move.l 72(a2),d6                                  ; +$06EA : 2C2A0048
    cmp.l d0,d6                                       ; +$06EE : BC80
    beq.w L_007AF6                                    ; +$06F0 : 67000012
    lea 96(a2),a4                                     ; +$06F4 : 49EA0060
    move.l #$00000000,d0                              ; +$06F8 : 203C00000000
    move.w (a4),d0                                    ; +$06FE : 3014
    or.w d4,d0                                        ; +$0700 : 8044
    move.w d0,(a4)                                    ; +$0702 : 3880
L_007AF6:
    lsr.w #1,d4                                       ; +$0704 : E24C
    move.l 60(a2),d0                                  ; +$0706 : 202A003C
    addq.l #1,d0                                      ; +$070A : 5280
    move.l d0,60(a2)                                  ; +$070C : 2540003C
    bra.w L_007A32                                    ; +$0710 : 6000FF2E
L_007B06:
    movea.l 76(a2),a4                                 ; +$0714 : 286A004C
    move.l a4,d0                                      ; +$0718 : 200C
    tst.l d0                                          ; +$071A : 4A80
    beq.w L_007B54                                    ; +$071C : 67000044
    lea 96(a2),a5                                     ; +$0720 : 4BEA0060
    move.l 48(a2),d5                                  ; +$0724 : 2A2A0030
    lsr.l #1,d5                                       ; +$0728 : E28D
L_007B1C:
    move.w (a5)+,d0                                   ; +$072A : 301D
    cmp.w (a4)+,d0                                    ; +$072C : B05C
    bne.w L_007B54                                    ; +$072E : 66000032
    subq.l #1,d5                                      ; +$0732 : 5385
    bne.w L_007B1C                                    ; +$0734 : 6600FFF4
    movea.l 80(a2),a4                                 ; +$0738 : 286A0050
    move.l #$00000000,d0                              ; +$073C : 203C00000000
    move.b (a4),d0                                    ; +$0742 : 1014
    cmpi.l #$000000FF,d0                              ; +$0744 : 0C80000000FF
    beq.w L_007B54                                    ; +$074A : 67000016
    tst.l d0                                          ; +$074E : 4A80
    bne.w L_007B4E                                    ; +$0750 : 6600000A
    move.b #$81,(a4)                                  ; +$0754 : 18BC0081
    bra.w L_007B8C                                    ; +$0758 : 60000040
L_007B4E:
    addq.b #1,(a4)                                    ; +$075C : 5214
    bra.w L_007B8C                                    ; +$075E : 6000003A
L_007B54:
    move.l 12(a2),d0                                  ; +$0762 : 202A000C
    movea.l 8(a2),a4                                  ; +$0766 : 286A0008
    sub.l a4,d0                                       ; +$076A : 908C
    move.l 48(a2),d5                                  ; +$076C : 2A2A0030
    addq.l #1,d5                                      ; +$0770 : 5285
    cmp.l d5,d0                                       ; +$0772 : B085
    bcs.w L_007BA8                                    ; +$0774 : 65000040
    move.l a4,80(a2)                                  ; +$0778 : 254C0050
    move.b #$00,(a4)+                                 ; +$077C : 18FC0000
    move.l a4,76(a2)                                  ; +$0780 : 254C004C
    lea 96(a2),a5                                     ; +$0784 : 4BEA0060
    move.l 48(a2),d5                                  ; +$0788 : 2A2A0030
    lsr.l #1,d5                                       ; +$078C : E28D
L_007B80:
    move.w (a5)+,(a4)+                                ; +$078E : 38DD
    subq.l #1,d5                                      ; +$0790 : 5385
    bne.w L_007B80                                    ; +$0792 : 6600FFFA
    move.l a4,8(a2)                                   ; +$0796 : 254C0008
L_007B8C:
    move.l 56(a2),d0                                  ; +$079A : 202A0038
    addq.l #1,d0                                      ; +$079E : 5280
    move.l d0,56(a2)                                  ; +$07A0 : 25400038
    bra.w L_007A04                                    ; +$07A4 : 6000FE6C
L_007B9A:
    move.l 8(a2),d0                                   ; +$07A8 : 202A0008
    movea.l 4(a2),a5                                  ; +$07AC : 2A6A0004
    sub.l a5,d0                                       ; +$07B0 : 908D
    bra.w L_007BAE                                    ; +$07B2 : 60000008
L_007BA8:
    move.l #$00000000,d0                              ; +$07B6 : 203C00000000
L_007BAE:
    lea 160(a7),a7                                    ; +$07BC : 4FEF00A0
    movem.l (a7)+,d1-d7/a0-a6                         ; +$07C0 : 4CDF7FFE
    rts                                               ; +$07C4 : 4E75
L_007BB8:
    dc.b "AGAPIC  "
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 57 : aga bank image draw --------
Entry_57:
Aga_Bank_Image_Draw:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -48(a7),a7                                    ; +$0004 : 4FEFFFD0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l a3,16(a2)                                  ; +$001E : 254B0010
    move.l 12(a2),d0                                  ; +$0022 : 202A000C
    cmpi.l #$00000005,d0                              ; +$0026 : 0C8000000005
    bcs.w L_007C46                                    ; +$002C : 65000054
    cmpi.l #$0000FFFF,d0                              ; +$0030 : 0C800000FFFF
    bhi.w L_007C46                                    ; +$0036 : 6200004A
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0040 : 2008
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_007C46                                    ; +$0044 : 6700003C
    move.l a0,32(a2)                                  ; +$0048 : 25480020
    move.l -20(a0),d1                                 ; +$004C : 2228FFEC
    cmpi.l #$00000010,d1                              ; +$0050 : 0C8100000010
    bcs.w L_007C46                                    ; +$0056 : 6500002A
    subi.l #$00000010,d1                              ; +$005A : 048100000010
    move.l d1,28(a2)                                  ; +$0060 : 2541001C
    move.l 4(a2),d0                                   ; +$0064 : 202A0004
    move.l d0,20(a2)                                  ; +$0068 : 25400014
    move.l 8(a2),d0                                   ; +$006C : 202A0008
    move.l d0,24(a2)                                  ; +$0070 : 25400018
    move.l (a2),d3                                    ; +$0074 : 2612
    lea 20(a2),a3                                     ; +$0076 : 47EA0014
    bsr.w L_006CE8                                    ; +$007A : 6100F0A8
    bra.w L_007C4C                                    ; +$007E : 60000008
L_007C46:
    move.l #$00000000,d3                              ; +$0082 : 263C00000000
L_007C4C:
    movea.l 16(a2),a3                                 ; +$0088 : 266A0010
    lea 48(a7),a7                                     ; +$008C : 4FEF0030
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0090 : 4CDF77F7
    moveq #0,d2                                       ; +$0094 : 7400
    rts                                               ; +$0096 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 58 : aga bank font select --------
Entry_58:
Aga_Bank_Font_Select:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -32(a7),a7                                    ; +$0004 : 4FEFFFE0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l a3,4(a2)                                   ; +$000C : 254B0004
    move.l d3,d0                                      ; +$0010 : 2003
    cmpi.l #$00000005,d0                              ; +$0012 : 0C8000000005
    bcs.w L_007CB8                                    ; +$0018 : 6500003E
    cmpi.l #$0000FFFF,d0                              ; +$001C : 0C800000FFFF
    bhi.w L_007CB8                                    ; +$0022 : 62000034
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$002C : 2008
    tst.l d0                                          ; +$002E : 4A80
    beq.w L_007CB8                                    ; +$0030 : 67000026
    move.l a0,8(a2)                                   ; +$0034 : 25480008
    move.l -20(a0),d3                                 ; +$0038 : 2628FFEC
    cmpi.l #$00000010,d3                              ; +$003C : 0C8300000010
    bcs.w L_007CB8                                    ; +$0042 : 65000014
    subi.l #$00000010,d3                              ; +$0046 : 048300000010
    lea 8(a2),a3                                      ; +$004C : 47EA0008
    bsr.w L_00597E                                    ; +$0050 : 6100DCCC
    bra.w L_007CBE                                    ; +$0054 : 60000008
L_007CB8:
    move.l #$00000000,d3                              ; +$0058 : 263C00000000
L_007CBE:
    movea.l 4(a2),a3                                  ; +$005E : 266A0004
    lea 32(a7),a7                                     ; +$0062 : 4FEF0020
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0066 : 4CDF77F7
    moveq #0,d2                                       ; +$006A : 7400
    rts                                               ; +$006C : 4E75
L_007CCE:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$006E : 48E7EFEE
    move.l (a3)+,d5                                   ; +$0072 : 2A1B
    move.l (a3)+,d4                                   ; +$0074 : 281B
    move.l (a3)+,d1                                   ; +$0076 : 221B
    move.l (a3)+,d0                                   ; +$0078 : 201B
    movea.l 456(a5),a4                                ; +$007A : 286D01C8
    move.l a4,d6                                      ; +$007E : 2C0C
    tst.l d6                                          ; +$0080 : 4A86
    beq.w L_007F04                                    ; +$0082 : 67000220
    move.l (a4),d6                                    ; +$0086 : 2C14
    tst.l d6                                          ; +$0088 : 4A86
    beq.w L_007F04                                    ; +$008A : 67000218
    movea.l 32(a4),a2                                 ; +$008E : 246C0020
    move.l a2,d6                                      ; +$0092 : 2C0A
    tst.l d6                                          ; +$0094 : 4A86
    beq.w L_007F04                                    ; +$0096 : 6700020C
    movea.l 8(a4),a6                                  ; +$009A : 2C6C0008
    move.l a6,d6                                      ; +$009E : 2C0E
    tst.l d6                                          ; +$00A0 : 4A86
    beq.w L_007F04                                    ; +$00A2 : 67000200
    tst.l d0                                          ; +$00A6 : 4A80
    bmi.w L_007F04                                    ; +$00A8 : 6B0001FA
    tst.l d1                                          ; +$00AC : 4A81
    bmi.w L_007F04                                    ; +$00AE : 6B0001F4
    tst.l d3                                          ; +$00B2 : 4A83
    bmi.w L_007F04                                    ; +$00B4 : 6B0001EE
    tst.l d4                                          ; +$00B8 : 4A84
    ble.w L_007F04                                    ; +$00BA : 6F0001E8
    tst.l d5                                          ; +$00BE : 4A85
    ble.w L_007F04                                    ; +$00C0 : 6F0001E2
    move.l 12(a4),d6                                  ; +$00C4 : 2C2C000C
    tst.l d6                                          ; +$00C8 : 4A86
    ble.w L_007F04                                    ; +$00CA : 6F0001D8
    cmpi.l #$00007FFF,d6                              ; +$00CE : 0C8600007FFF
    bgt.w L_007F04                                    ; +$00D4 : 6E0001CE
    move.l 16(a4),d6                                  ; +$00D8 : 2C2C0010
    tst.l d6                                          ; +$00DC : 4A86
    ble.w L_007F04                                    ; +$00DE : 6F0001C4
    cmpi.l #$00007FFF,d6                              ; +$00E2 : 0C8600007FFF
    bgt.w L_007F04                                    ; +$00E8 : 6E0001BA
    move.l 12(a4),d6                                  ; +$00EC : 2C2C000C
    sub.l d4,d6                                       ; +$00F0 : 9C84
    tst.l d6                                          ; +$00F2 : 4A86
    bmi.w L_007F04                                    ; +$00F4 : 6B0001AE
    cmp.l d6,d0                                       ; +$00F8 : B086
    bgt.w L_007F04                                    ; +$00FA : 6E0001A8
    move.l 16(a4),d6                                  ; +$00FE : 2C2C0010
    sub.l d5,d6                                       ; +$0102 : 9C85
    tst.l d6                                          ; +$0104 : 4A86
    bmi.w L_007F04                                    ; +$0106 : 6B00019C
    cmp.l d6,d1                                       ; +$010A : B286
    bgt.w L_007F04                                    ; +$010C : 6E000196
    tst.l 8(a2)                                       ; +$0110 : 4AAA0008
    beq.w L_007D7E                                    ; +$0114 : 67000008
    movea.l (a2),a0                                   ; +$0118 : 2052
    bra.w L_007D82                                    ; +$011A : 60000006
L_007D7E:
    movea.l 4(a2),a0                                  ; +$011E : 206A0004
L_007D82:
    move.l a0,d6                                      ; +$0122 : 2C08
    tst.l d6                                          ; +$0124 : 4A86
    beq.w L_007F04                                    ; +$0126 : 6700017C
    movea.l (a0),a0                                   ; +$012A : 2050
    move.l a0,d6                                      ; +$012C : 2C08
    tst.l d6                                          ; +$012E : 4A86
    beq.w L_007F04                                    ; +$0130 : 67000172
    move.l #$00000000,d6                              ; +$0134 : 2C3C00000000
    move.w (a0),d6                                    ; +$013A : 3C10
    lsl.l #3,d6                                       ; +$013C : E78E
    cmp.l 12(a4),d6                                   ; +$013E : BCAC000C
    blt.w L_007F04                                    ; +$0142 : 6D000160
    move.l #$00000000,d6                              ; +$0146 : 2C3C00000000
    move.w 2(a0),d6                                   ; +$014C : 3C280002
    cmp.l 16(a4),d6                                   ; +$0150 : BCAC0010
    blt.w L_007F04                                    ; +$0154 : 6D00014E
    move.l #$00000000,d6                              ; +$0158 : 2C3C00000000
    move.b 5(a0),d6                                   ; +$015E : 1C280005
    cmp.l 28(a4),d6                                   ; +$0162 : BCAC001C
    bne.w L_007F04                                    ; +$0166 : 6600013C
    tst.l d6                                          ; +$016A : 4A86
    ble.w L_007F04                                    ; +$016C : 6F000136
    cmpi.l #$00000008,d6                              ; +$0170 : 0C8600000008
    bgt.w L_007F04                                    ; +$0176 : 6E00012C
    move.l d6,d2                                      ; +$017A : 2406
    movea.l a0,a1                                     ; +$017C : 2248
    addq.l #8,a1                                      ; +$017E : 5089
L_007DE0:
    move.l (a1)+,d6                                   ; +$0180 : 2C19
    tst.l d6                                          ; +$0182 : 4A86
    beq.w L_007F04                                    ; +$0184 : 6700011E
    cmpi.l #$FFFFFFFF,d6                              ; +$0188 : 0C86FFFFFFFF
    beq.w L_007F04                                    ; +$018E : 67000114
    subq.l #1,d2                                      ; +$0192 : 5382
    bne.w L_007DE0                                    ; +$0194 : 6600FFEA
    move.l #$00000000,d2                              ; +$0198 : 243C00000000
    move.b 5(a0),d2                                   ; +$019E : 14280005
    move.l #$00000001,d6                              ; +$01A2 : 2C3C00000001
L_007E08:
    lsl.l #1,d6                                       ; +$01A8 : E38E
    subq.l #1,d2                                      ; +$01AA : 5382
    bne.w L_007E08                                    ; +$01AC : 6600FFFA
    cmp.l d6,d3                                       ; +$01B0 : B686
    bcc.w L_007F04                                    ; +$01B2 : 640000F0
    move.l d6,-(a7)                                   ; +$01B6 : 2F06
    move.l 20(a2),d6                                  ; +$01B8 : 2C2A0014
    andi.l #$00000001,d6                              ; +$01BC : 028600000001
    beq.w L_007E78                                    ; +$01C2 : 67000054
    move.l d0,-(a7)                                   ; +$01C6 : 2F00
    move.l d1,-(a7)                                   ; +$01C8 : 2F01
    move.l a0,-(a7)                                   ; +$01CA : 2F08
    move.l a1,-(a7)                                   ; +$01CC : 2F09
    movea.l 12(a2),a0                                 ; +$01CE : 206A000C
    move.l a0,d6                                      ; +$01D2 : 2C08
    tst.l d6                                          ; +$01D4 : 4A86
    beq.w L_007E66                                    ; +$01D6 : 6700002E
    movea.l $0004.w,a6                                ; +$01DA : 2C780004
    jsr -372(a6)                                      ; +$01DE : 4EAEFE8C
    tst.l d0                                          ; +$01E2 : 4A80
    beq.w L_007E66                                    ; +$01E4 : 67000020
    move.l 20(a2),d6                                  ; +$01E8 : 2C2A0014
    andi.l #$FFFFFFFE,d6                              ; +$01EC : 0286FFFFFFFE
    move.l d6,20(a2)                                  ; +$01F2 : 25460014
    movea.l 8(a4),a6                                  ; +$01F6 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$01FA : 225F
    movea.l (a7)+,a0                                  ; +$01FC : 205F
    move.l (a7)+,d1                                   ; +$01FE : 221F
    move.l (a7)+,d0                                   ; +$0200 : 201F
    bra.w L_007E78                                    ; +$0202 : 60000014
L_007E66:
    movea.l 8(a4),a6                                  ; +$0206 : 2C6C0008
    movea.l (a7)+,a1                                  ; +$020A : 225F
    movea.l (a7)+,a0                                  ; +$020C : 205F
    move.l (a7)+,d1                                   ; +$020E : 221F
    move.l (a7)+,d0                                   ; +$0210 : 201F
    move.l (a7)+,d6                                   ; +$0212 : 2C1F
    bra.w L_007F04                                    ; +$0214 : 6000008E
L_007E78:
    move.l (a7)+,d6                                   ; +$0218 : 2C1F
    move.l d0,d2                                      ; +$021A : 2400
    move.l d1,d6                                      ; +$021C : 2C01
    move.l d3,d7                                      ; +$021E : 2E03
    movea.l a0,a4                                     ; +$0220 : 2848
    lea -128(a7),a7                                   ; +$0222 : 4FEFFF80
    movea.l a7,a2                                     ; +$0226 : 244F
    movea.l a2,a1                                     ; +$0228 : 224A
    jsr -198(a6)                                      ; +$022A : 4EAEFF3A
    move.l a4,4(a2)                                   ; +$022E : 254C0004
    tst.l d2                                          ; +$0232 : 4A82
    bne.w L_007ECA                                    ; +$0234 : 66000034
    tst.l d6                                          ; +$0238 : 4A86
    bne.w L_007ECA                                    ; +$023A : 6600002E
    move.l #$00000000,d0                              ; +$023E : 203C00000000
    move.w (a4),d0                                    ; +$0244 : 3014
    lsl.l #3,d0                                       ; +$0246 : E788
    cmp.l d4,d0                                       ; +$0248 : B084
    bne.w L_007ECA                                    ; +$024A : 6600001E
    move.l #$00000000,d0                              ; +$024E : 203C00000000
    move.w 2(a4),d0                                   ; +$0254 : 302C0002
    cmp.l d5,d0                                       ; +$0258 : B085
    bne.w L_007ECA                                    ; +$025A : 6600000E
    move.l d7,d0                                      ; +$025E : 2007
    movea.l a2,a1                                     ; +$0260 : 224A
    jsr -234(a6)                                      ; +$0262 : 4EAEFF16
    bra.w L_007EF2                                    ; +$0266 : 6000002A
L_007ECA:
    movea.l a2,a1                                     ; +$026A : 224A
    move.l d7,d0                                      ; +$026C : 2007
    jsr -342(a6)                                      ; +$026E : 4EAEFEAA
    movea.l a2,a1                                     ; +$0272 : 224A
    move.l #$00000000,d0                              ; +$0274 : 203C00000000
    jsr -354(a6)                                      ; +$027A : 4EAEFE9E
    move.l d2,d0                                      ; +$027E : 2002
    move.l d6,d1                                      ; +$0280 : 2206
    add.l d4,d2                                       ; +$0282 : D484
    subq.l #1,d2                                      ; +$0284 : 5382
    move.l d6,d3                                      ; +$0286 : 2606
    add.l d5,d3                                       ; +$0288 : D685
    subq.l #1,d3                                      ; +$028A : 5383
    movea.l a2,a1                                     ; +$028C : 224A
    jsr -306(a6)                                      ; +$028E : 4EAEFECE
L_007EF2:
    jsr -228(a6)                                      ; +$0292 : 4EAEFF1C
    lea 128(a7),a7                                    ; +$0296 : 4FEF0080
    move.l #$00000001,d3                              ; +$029A : 263C00000001
    bra.w L_007F0A                                    ; +$02A0 : 60000008
L_007F04:
    move.l #$00000000,d3                              ; +$02A4 : 263C00000000
L_007F0A:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$02AA : 4CDF77F7
    moveq #0,d2                                       ; +$02AE : 7400
    rts                                               ; +$02B0 : 4E75
    dc.b "NqNqNqNqNqNqNqNqNqNqNqNqNqNqNqNqNqNqNqNq"
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 59 : aga image region --------
Entry_59:
Aga_Image_Region:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -192(a7),a7                                   ; +$0004 : 4FEFFF40
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d6                                   ; +$0012 : 2C1B
    move.l d6,8(a2)                                   ; +$0014 : 25460008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l (a3)+,d7                                   ; +$001E : 2E1B
    move.l d7,16(a2)                                  ; +$0020 : 25470010
    move.l (a3)+,d7                                   ; +$0024 : 2E1B
    move.l d7,20(a2)                                  ; +$0026 : 25470014
    move.l (a3)+,d7                                   ; +$002A : 2E1B
    move.l d7,24(a2)                                  ; +$002C : 25470018
    move.l (a3)+,d7                                   ; +$0030 : 2E1B
    move.l d7,28(a2)                                  ; +$0032 : 2547001C
    move.l #$00000000,d3                              ; +$0036 : 263C00000000
    movea.l $0004.w,a0                                ; +$003C : 20780004
    move.l a0,d0                                      ; +$0040 : 2008
    tst.l d0                                          ; +$0042 : 4A80
    beq.w L_008428                                    ; +$0044 : 670004A4
    move.w 296(a0),d0                                 ; +$0048 : 30280128
    btst #1,d0                                        ; +$004C : 08000001
    beq.w L_008428                                    ; +$0050 : 67000498
    move.l 28(a2),d0                                  ; +$0054 : 202A001C
    cmpi.l #$00000005,d0                              ; +$0058 : 0C8000000005
    bcs.w L_008428                                    ; +$005E : 6500048A
    cmpi.l #$0000FFFF,d0                              ; +$0062 : 0C800000FFFF
    bhi.w L_008428                                    ; +$0068 : 62000480
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$0072 : 2A08
    tst.l d5                                          ; +$0074 : 4A85
    beq.w L_008428                                    ; +$0076 : 67000472
    move.l d5,36(a2)                                  ; +$007A : 25450024
    move.l -20(a0),d4                                 ; +$007E : 2828FFEC
    cmpi.l #$00000010,d4                              ; +$0082 : 0C8400000010
    bcs.w L_008428                                    ; +$0088 : 65000460
    subi.l #$00000010,d4                              ; +$008C : 048400000010
    move.l d4,32(a2)                                  ; +$0092 : 25440020
    move.l (a2),d0                                    ; +$0096 : 2012
    cmpi.l #$00000001,d0                              ; +$0098 : 0C8000000001
    bhi.w L_008428                                    ; +$009E : 6200044A
    cmpi.l #$00000020,d4                              ; +$00A2 : 0C8400000020
    bcs.w L_008428                                    ; +$00A8 : 65000440
    cmpi.l #$01000000,d4                              ; +$00AC : 0C8401000000
    bhi.w L_008428                                    ; +$00B2 : 62000436
    cmpi.l #$00000018,d5                              ; +$00B6 : 0C8500000018
    bls.w L_008428                                    ; +$00BC : 6300042C
    move.l d5,d0                                      ; +$00C0 : 2005
    andi.l #$00000001,d0                              ; +$00C2 : 028000000001
    bne.w L_008428                                    ; +$00C8 : 66000420
    move.l 8(a2),d0                                   ; +$00CC : 202A0008
    cmpi.l #$FFFF8000,d0                              ; +$00D0 : 0C80FFFF8000
    blt.w L_008428                                    ; +$00D6 : 6D000412
    cmpi.l #$00007FFF,d0                              ; +$00DA : 0C8000007FFF
    bgt.w L_008428                                    ; +$00E0 : 6E000408
    move.l 4(a2),d0                                   ; +$00E4 : 202A0004
    cmpi.l #$FFFF8000,d0                              ; +$00E8 : 0C80FFFF8000
    blt.w L_008428                                    ; +$00EE : 6D0003FA
    cmpi.l #$00007FFF,d0                              ; +$00F2 : 0C8000007FFF
    bgt.w L_008428                                    ; +$00F8 : 6E0003F0
    move.l d5,d0                                      ; +$00FC : 2005
    add.l d4,d0                                       ; +$00FE : D084
    bcs.w L_008428                                    ; +$0100 : 650003E8
    subq.l #1,d0                                      ; +$0104 : 5380
    movea.l d0,a1                                     ; +$0106 : 2240
    movea.l $0004.w,a6                                ; +$0108 : 2C780004
    jsr -534(a6)                                      ; +$010C : 4EAEFDEA
    tst.l d0                                          ; +$0110 : 4A80
    beq.w L_008428                                    ; +$0112 : 670003D6
    move.l d5,d0                                      ; +$0116 : 2005
    subi.l #$00000018,d0                              ; +$0118 : 048000000018
    movea.l d0,a1                                     ; +$011E : 2240
    jsr -534(a6)                                      ; +$0120 : 4EAEFDEA
    tst.l d0                                          ; +$0124 : 4A80
    beq.w L_008428                                    ; +$0126 : 670003C2
    movea.l d5,a0                                     ; +$012A : 2045
    move.l -20(a0),d0                                 ; +$012C : 2028FFEC
    move.l d4,d1                                      ; +$0130 : 2204
    addi.l #$00000010,d1                              ; +$0132 : 068100000010
    cmp.l d1,d0                                       ; +$0138 : B081
    bne.w L_008428                                    ; +$013A : 660003AE
    move.l -16(a0),d0                                 ; +$013E : 2028FFF0
    cmpi.l #$00000005,d0                              ; +$0142 : 0C8000000005
    bcs.w L_008428                                    ; +$0148 : 650003A0
    cmpi.l #$0000FFFF,d0                              ; +$014C : 0C800000FFFF
    bhi.w L_008428                                    ; +$0152 : 62000396
    move.l #$00000000,d0                              ; +$0156 : 203C00000000
    move.w -12(a0),d0                                 ; +$015C : 3028FFF4
    tst.l d0                                          ; +$0160 : 4A80
    beq.w L_0080B2                                    ; +$0162 : 67000010
    andi.w #$FFFD,d0                                  ; +$0166 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$016A : 0C8000000001
    bne.w L_008428                                    ; +$0170 : 66000378
L_0080B2:
    move.l -8(a0),d0                                  ; +$0174 : 2028FFF8
    cmpi.l #$41474150,d0                              ; +$0178 : 0C8041474150
    bne.w L_008428                                    ; +$017E : 6600036A
    move.l -4(a0),d0                                  ; +$0182 : 2028FFFC
    cmpi.l #$49432020,d0                              ; +$0186 : 0C8049432020
    bne.w L_008428                                    ; +$018C : 6600035C
    move.l (a0),d0                                    ; +$0190 : 2010
    cmpi.l #$41474150,d0                              ; +$0192 : 0C8041474150
    bne.w L_008428                                    ; +$0198 : 66000350
    move.l #$00000000,d0                              ; +$019C : 203C00000000
    move.w 4(a0),d0                                   ; +$01A2 : 30280004
    cmpi.l #$00004943,d0                              ; +$01A6 : 0C8000004943
    bne.w L_008428                                    ; +$01AC : 6600033C
    move.l #$00000000,d0                              ; +$01B0 : 203C00000000
    move.w 6(a0),d0                                   ; +$01B6 : 30280006
    cmpi.l #$00000001,d0                              ; +$01BA : 0C8000000001
    bne.w L_008428                                    ; +$01C0 : 66000328
    move.l #$00000000,d0                              ; +$01C4 : 203C00000000
    move.w 8(a0),d0                                   ; +$01CA : 30280008
    move.l d0,52(a2)                                  ; +$01CE : 25400034
    cmpi.l #$00000001,d0                              ; +$01D2 : 0C8000000001
    bhi.w L_008428                                    ; +$01D8 : 62000310
    move.l (a2),d1                                    ; +$01DC : 2212
    tst.l d1                                          ; +$01DE : 4A81
    beq.w L_008128                                    ; +$01E0 : 67000008
    tst.l d0                                          ; +$01E4 : 4A80
    beq.w L_008428                                    ; +$01E6 : 67000302
L_008128:
    move.l #$00000000,d0                              ; +$01EA : 203C00000000
    move.w 10(a0),d0                                  ; +$01F0 : 3028000A
    cmpi.l #$00000001,d0                              ; +$01F4 : 0C8000000001
    bne.w L_008428                                    ; +$01FA : 660002EE
    move.l #$00000000,d0                              ; +$01FE : 203C00000000
    move.w 12(a0),d0                                  ; +$0204 : 3028000C
    move.l d0,40(a2)                                  ; +$0208 : 25400028
    tst.l d0                                          ; +$020C : 4A80
    beq.w L_008428                                    ; +$020E : 670002DA
    cmpi.l #$00001000,d0                              ; +$0212 : 0C8000001000
    bhi.w L_008428                                    ; +$0218 : 620002D0
    move.l #$00000000,d0                              ; +$021C : 203C00000000
    move.w 14(a0),d0                                  ; +$0222 : 3028000E
    move.l d0,44(a2)                                  ; +$0226 : 2540002C
    tst.l d0                                          ; +$022A : 4A80
    beq.w L_008428                                    ; +$022C : 670002BC
    cmpi.l #$00001000,d0                              ; +$0230 : 0C8000001000
    bhi.w L_008428                                    ; +$0236 : 620002B2
    move.l 40(a2),d1                                  ; +$023A : 222A0028
    mulu.w d1,d0                                      ; +$023E : C0C1
    cmpi.l #$00400000,d0                              ; +$0240 : 0C8000400000
    bhi.w L_008428                                    ; +$0246 : 620002A2
    move.l 24(a2),d0                                  ; +$024A : 202A0018
    tst.l d0                                          ; +$024E : 4A80
    bmi.w L_008428                                    ; +$0250 : 6B000298
    move.l 20(a2),d0                                  ; +$0254 : 202A0014
    tst.l d0                                          ; +$0258 : 4A80
    bmi.w L_008428                                    ; +$025A : 6B00028E
    move.l 16(a2),d0                                  ; +$025E : 202A0010
    tst.l d0                                          ; +$0262 : 4A80
    ble.w L_008428                                    ; +$0264 : 6F000284
    cmp.l 40(a2),d0                                   ; +$0268 : B0AA0028
    bgt.w L_008428                                    ; +$026C : 6E00027C
    move.l 40(a2),d0                                  ; +$0270 : 202A0028
    sub.l 16(a2),d0                                   ; +$0274 : 90AA0010
    cmp.l 24(a2),d0                                   ; +$0278 : B0AA0018
    bmi.w L_008428                                    ; +$027C : 6B00026C
    move.l 12(a2),d0                                  ; +$0280 : 202A000C
    tst.l d0                                          ; +$0284 : 4A80
    ble.w L_008428                                    ; +$0286 : 6F000262
    cmp.l 44(a2),d0                                   ; +$028A : B0AA002C
    bgt.w L_008428                                    ; +$028E : 6E00025A
    move.l 44(a2),d0                                  ; +$0292 : 202A002C
    sub.l 12(a2),d0                                   ; +$0296 : 90AA000C
    cmp.l 20(a2),d0                                   ; +$029A : B0AA0014
    bmi.w L_008428                                    ; +$029E : 6B00024A
    move.l #$00000000,d0                              ; +$02A2 : 203C00000000
    move.w 16(a0),d0                                  ; +$02A8 : 30280010
    move.l d0,48(a2)                                  ; +$02AC : 25400030
    tst.l d0                                          ; +$02B0 : 4A80
    beq.w L_008428                                    ; +$02B2 : 67000236
    cmpi.l #$00000008,d0                              ; +$02B6 : 0C8000000008
    bhi.w L_008428                                    ; +$02BC : 6200022C
    move.l d0,d1                                      ; +$02C0 : 2200
    move.l 52(a2),d0                                  ; +$02C2 : 202A0034
    add.l d1,d0                                       ; +$02C6 : D081
    lsl.l #1,d0                                       ; +$02C8 : E388
    move.l d0,56(a2)                                  ; +$02CA : 25400038
    move.l #$00000000,d1                              ; +$02CE : 223C00000000
    move.w 18(a0),d1                                  ; +$02D4 : 32280012
    cmp.l d1,d0                                       ; +$02D8 : B081
    bne.w L_008428                                    ; +$02DA : 6600020E
    move.l 20(a0),d0                                  ; +$02DE : 20280014
    cmpi.l #$00000020,d0                              ; +$02E2 : 0C8000000020
    bne.w L_008428                                    ; +$02E8 : 66000200
    move.l 44(a2),d0                                  ; +$02EC : 202A002C
    addq.l #1,d0                                      ; +$02F0 : 5280
    lsl.l #2,d0                                       ; +$02F2 : E588
    addi.l #$00000020,d0                              ; +$02F4 : 068000000020
    move.l d0,68(a2)                                  ; +$02FA : 25400044
    move.l 24(a0),d1                                  ; +$02FE : 22280018
    cmp.l d1,d0                                       ; +$0302 : B081
    bne.w L_008428                                    ; +$0304 : 660001E4
    cmp.l d4,d0                                       ; +$0308 : B084
    bhi.w L_008428                                    ; +$030A : 620001DE
    move.l 28(a0),d0                                  ; +$030E : 2028001C
    cmp.l d4,d0                                       ; +$0312 : B084
    bne.w L_008428                                    ; +$0314 : 660001D4
    move.l 40(a2),d0                                  ; +$0318 : 202A0028
    addi.l #$0000000F,d0                              ; +$031C : 06800000000F
    lsr.l #4,d0                                       ; +$0322 : E888
    move.l d0,60(a2)                                  ; +$0324 : 2540003C
    move.l 40(a2),d1                                  ; +$0328 : 222A0028
    andi.l #$0000000F,d1                              ; +$032C : 02810000000F
    move.l #$00000000,d0                              ; +$0332 : 203C00000000
    tst.l d1                                          ; +$0338 : 4A81
    beq.w L_00828A                                    ; +$033A : 67000010
    move.l #$0000FFFF,d0                              ; +$033E : 203C0000FFFF
L_008282:
    lsr.w #1,d0                                       ; +$0344 : E248
    subq.l #1,d1                                      ; +$0346 : 5381
    bne.w L_008282                                    ; +$0348 : 6600FFFA
L_00828A:
    move.l d0,64(a2)                                  ; +$034C : 25400040
    movea.l 456(a5),a4                                ; +$0350 : 286D01C8
    move.l a4,d0                                      ; +$0354 : 200C
    tst.l d0                                          ; +$0356 : 4A80
    beq.w L_008428                                    ; +$0358 : 67000190
    move.l (a4),d0                                    ; +$035C : 2014
    tst.l d0                                          ; +$035E : 4A80
    beq.w L_008428                                    ; +$0360 : 67000188
    move.l 8(a4),d0                                   ; +$0364 : 202C0008
    tst.l d0                                          ; +$0368 : 4A80
    beq.w L_008428                                    ; +$036A : 6700017E
    move.l 32(a4),d0                                  ; +$036E : 202C0020
    tst.l d0                                          ; +$0372 : 4A80
    beq.w L_008428                                    ; +$0374 : 67000174
    move.l 12(a4),d0                                  ; +$0378 : 202C000C
    tst.l d0                                          ; +$037C : 4A80
    ble.w L_008428                                    ; +$037E : 6F00016A
    cmpi.l #$00007FFF,d0                              ; +$0382 : 0C8000007FFF
    bgt.w L_008428                                    ; +$0388 : 6E000160
    move.l d0,72(a2)                                  ; +$038C : 25400048
    move.l 16(a4),d0                                  ; +$0390 : 202C0010
    tst.l d0                                          ; +$0394 : 4A80
    ble.w L_008428                                    ; +$0396 : 6F000152
    cmpi.l #$00007FFF,d0                              ; +$039A : 0C8000007FFF
    bgt.w L_008428                                    ; +$03A0 : 6E000148
    move.l d0,76(a2)                                  ; +$03A4 : 2540004C
    move.l 28(a4),d0                                  ; +$03A8 : 202C001C
    cmp.l 48(a2),d0                                   ; +$03AC : B0AA0030
    bne.w L_008428                                    ; +$03B0 : 66000138
    movea.l 32(a4),a0                                 ; +$03B4 : 206C0020
    move.l 8(a0),d0                                   ; +$03B8 : 20280008
    tst.l d0                                          ; +$03BC : 4A80
    beq.w L_008314                                    ; +$03BE : 67000016
    cmpi.l #$00000001,d0                              ; +$03C2 : 0C8000000001
    bne.w L_008428                                    ; +$03C8 : 66000120
    movea.l 32(a4),a0                                 ; +$03CC : 206C0020
    movea.l (a0),a1                                   ; +$03D0 : 2250
    bra.w L_00831C                                    ; +$03D2 : 6000000A
L_008314:
    movea.l 32(a4),a0                                 ; +$03D6 : 206C0020
    movea.l 4(a0),a1                                  ; +$03DA : 22680004
L_00831C:
    move.l a1,d0                                      ; +$03DE : 2009
    tst.l d0                                          ; +$03E0 : 4A80
    beq.w L_008428                                    ; +$03E2 : 67000106
    movea.l (a1),a0                                   ; +$03E6 : 2051
    move.l a0,d0                                      ; +$03E8 : 2008
    tst.l d0                                          ; +$03EA : 4A80
    beq.w L_008428                                    ; +$03EC : 670000FC
    move.l a0,84(a2)                                  ; +$03F0 : 25480054
    move.l #$00000000,d1                              ; +$03F4 : 223C00000000
    move.w (a0),d1                                    ; +$03FA : 3210
    tst.l d1                                          ; +$03FC : 4A81
    beq.w L_008428                                    ; +$03FE : 670000EA
    move.l d1,80(a2)                                  ; +$0402 : 25410050
    lsl.l #3,d1                                       ; +$0406 : E789
    cmp.l 72(a2),d1                                   ; +$0408 : B2AA0048
    blt.w L_008428                                    ; +$040C : 6D0000DC
    move.l #$00000000,d1                              ; +$0410 : 223C00000000
    move.w 2(a0),d1                                   ; +$0416 : 32280002
    cmp.l 76(a2),d1                                   ; +$041A : B2AA004C
    blt.w L_008428                                    ; +$041E : 6D0000CA
    move.l #$00000000,d1                              ; +$0422 : 223C00000000
    move.b 5(a0),d1                                   ; +$0428 : 12280005
    cmp.l 48(a2),d1                                   ; +$042C : B2AA0030
    bne.w L_008428                                    ; +$0430 : 660000B8
    move.l d1,d0                                      ; +$0434 : 2001
    movea.l a0,a1                                     ; +$0436 : 2248
    addq.l #8,a1                                      ; +$0438 : 5089
L_008378:
    move.l (a1)+,d1                                   ; +$043A : 2219
    tst.l d1                                          ; +$043C : 4A81
    beq.w L_008428                                    ; +$043E : 670000AA
    cmpi.l #$FFFFFFFF,d1                              ; +$0442 : 0C81FFFFFFFF
    beq.w L_008428                                    ; +$0448 : 670000A0
    subq.l #1,d0                                      ; +$044C : 5380
    bne.w L_008378                                    ; +$044E : 6600FFEA
    move.l #$00000000,92(a2)                          ; +$0452 : 257C00000000005C
    bsr.w L_008436                                    ; +$045A : 6100009C
    tst.l d0                                          ; +$045E : 4A80
    beq.w L_008428                                    ; +$0460 : 67000088
    move.l 8(a2),d0                                   ; +$0464 : 202A0008
    cmp.l 72(a2),d0                                   ; +$0468 : B0AA0048
    bge.w L_00841E                                    ; +$046C : 6C000072
    add.l 16(a2),d0                                   ; +$0470 : D0AA0010
    tst.l d0                                          ; +$0474 : 4A80
    ble.w L_00841E                                    ; +$0476 : 6F000068
    move.l 4(a2),d0                                   ; +$047A : 202A0004
    cmp.l 76(a2),d0                                   ; +$047E : B0AA004C
    bge.w L_00841E                                    ; +$0482 : 6C00005C
    add.l 12(a2),d0                                   ; +$0486 : D0AA000C
    tst.l d0                                          ; +$048A : 4A80
    ble.w L_00841E                                    ; +$048C : 6F000052
    movea.l 32(a4),a0                                 ; +$0490 : 206C0020
    move.l 20(a0),d0                                  ; +$0494 : 20280014
    andi.l #$00000001,d0                              ; +$0498 : 028000000001
    beq.w L_00840C                                    ; +$049E : 6700002E
    movea.l 12(a0),a0                                 ; +$04A2 : 2068000C
    move.l a0,d0                                      ; +$04A6 : 2008
    tst.l d0                                          ; +$04A8 : 4A80
    beq.w L_008428                                    ; +$04AA : 6700003E
    movea.l $0004.w,a6                                ; +$04AE : 2C780004
    jsr -372(a6)                                      ; +$04B2 : 4EAEFE8C
    tst.l d0                                          ; +$04B6 : 4A80
    beq.w L_008428                                    ; +$04B8 : 67000030
    movea.l 32(a4),a0                                 ; +$04BC : 206C0020
    move.l 20(a0),d0                                  ; +$04C0 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$04C4 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$04CA : 21400014
L_00840C:
    move.l #$00000001,92(a2)                          ; +$04CE : 257C00000001005C
    bsr.w L_008436                                    ; +$04D6 : 61000020
    tst.l d0                                          ; +$04DA : 4A80
    beq.w L_008428                                    ; +$04DC : 6700000C
L_00841E:
    move.l #$00000001,d3                              ; +$04E0 : 263C00000001
    bra.w L_00842A                                    ; +$04E6 : 60000004
L_008428:
    moveq #0,d3                                       ; +$04EA : 7600
L_00842A:
    lea 192(a7),a7                                    ; +$04EC : 4FEF00C0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$04F0 : 4CDF77F7
    moveq #0,d2                                       ; +$04F4 : 7400
    rts                                               ; +$04F6 : 4E75
L_008436:
    move.l #$00000000,88(a2)                          ; +$04F8 : 257C000000000058
L_00843E:
    move.l 88(a2),d0                                  ; +$0500 : 202A0058
    cmp.l 44(a2),d0                                   ; +$0504 : B0AA002C
    bge.w L_0085F6                                    ; +$0508 : 6C0001AE
    lsl.l #2,d0                                       ; +$050C : E588
    move.l d0,d1                                      ; +$050E : 2200
    move.l 36(a2),d0                                  ; +$0510 : 202A0024
    addi.l #$00000020,d0                              ; +$0514 : 068000000020
    add.l d1,d0                                       ; +$051A : D081
    movea.l d0,a1                                     ; +$051C : 2240
    move.l (a1)+,d0                                   ; +$051E : 2019
    move.l (a1)+,d1                                   ; +$0520 : 2219
    cmp.l d1,d0                                       ; +$0522 : B081
    bcc.w L_0085FE                                    ; +$0524 : 6400019A
    cmp.l 68(a2),d0                                   ; +$0528 : B0AA0044
    bcs.w L_0085FE                                    ; +$052C : 65000192
    cmp.l 32(a2),d1                                   ; +$0530 : B2AA0020
    bhi.w L_0085FE                                    ; +$0534 : 6200018A
    move.l 88(a2),d2                                  ; +$0538 : 242A0058
    tst.l d2                                          ; +$053C : 4A82
    bne.w L_008488                                    ; +$053E : 6600000A
    cmp.l 68(a2),d0                                   ; +$0542 : B0AA0044
    bne.w L_0085FE                                    ; +$0546 : 66000178
L_008488:
    move.l 44(a2),d2                                  ; +$054A : 242A002C
    subq.l #1,d2                                      ; +$054E : 5382
    cmp.l 88(a2),d2                                   ; +$0550 : B4AA0058
    bne.w L_00849E                                    ; +$0554 : 6600000A
    cmp.l 32(a2),d1                                   ; +$0558 : B2AA0020
    bne.w L_0085FE                                    ; +$055C : 66000162
L_00849E:
    move.l 36(a2),d2                                  ; +$0560 : 242A0024
    add.l d2,d0                                       ; +$0564 : D082
    move.l d0,96(a2)                                  ; +$0566 : 25400060
    add.l d2,d1                                       ; +$056A : D282
    move.l d1,100(a2)                                 ; +$056C : 25410064
    move.l #$00000000,104(a2)                         ; +$0570 : 257C000000000068
    move.l #$00000000,108(a2)                         ; +$0578 : 257C00000000006C
    move.l #$00000000,112(a2)                         ; +$0580 : 257C000000000070
L_0084C6:
    move.l 104(a2),d0                                 ; +$0588 : 202A0068
    cmp.l 60(a2),d0                                   ; +$058C : B0AA003C
    bge.w L_0085DC                                    ; +$0590 : 6C00010C
    move.l 108(a2),d0                                 ; +$0594 : 202A006C
    tst.l d0                                          ; +$0598 : 4A80
    bne.w L_00854C                                    ; +$059A : 66000072
    move.l 96(a2),d0                                  ; +$059E : 202A0060
    cmp.l 100(a2),d0                                  ; +$05A2 : B0AA0064
    bcc.w L_0085FE                                    ; +$05A6 : 64000118
    movea.l d0,a0                                     ; +$05AA : 2040
    move.l #$00000000,d0                              ; +$05AC : 203C00000000
    move.b (a0)+,d0                                   ; +$05B2 : 1018
    move.l d0,d1                                      ; +$05B4 : 2200
    andi.l #$0000007F,d1                              ; +$05B6 : 02810000007F
    addq.l #1,d1                                      ; +$05BC : 5281
    move.l d1,108(a2)                                 ; +$05BE : 2541006C
    move.l d0,d2                                      ; +$05C2 : 2400
    andi.l #$00000080,d2                              ; +$05C4 : 028200000080
    move.l d2,112(a2)                                 ; +$05CA : 25420070
    move.l 104(a2),d2                                 ; +$05CE : 242A0068
    add.l d1,d2                                       ; +$05D2 : D481
    cmp.l 60(a2),d2                                   ; +$05D4 : B4AA003C
    bgt.w L_0085FE                                    ; +$05D8 : 6E0000E6
    move.l a0,d2                                      ; +$05DC : 2408
    move.l d2,96(a2)                                  ; +$05DE : 25420060
    move.l 112(a2),d2                                 ; +$05E2 : 242A0070
    tst.l d2                                          ; +$05E6 : 4A82
    beq.w L_008536                                    ; +$05E8 : 6700000E
    move.l a0,116(a2)                                 ; +$05EC : 25480074
    move.l 56(a2),d2                                  ; +$05F0 : 242A0038
    bra.w L_00853C                                    ; +$05F4 : 60000008
L_008536:
    move.l 56(a2),d2                                  ; +$05F8 : 242A0038
    mulu.w d1,d2                                      ; +$05FC : C4C1
L_00853C:
    move.l a0,d0                                      ; +$05FE : 2008
    add.l d2,d0                                       ; +$0600 : D082
    bcs.w L_0085FE                                    ; +$0602 : 650000BC
    cmp.l 100(a2),d0                                  ; +$0606 : B0AA0064
    bgt.w L_0085FE                                    ; +$060A : 6E0000B4
L_00854C:
    move.l 112(a2),d2                                 ; +$060E : 242A0070
    tst.l d2                                          ; +$0612 : 4A82
    bne.w L_00856A                                    ; +$0614 : 66000016
    move.l 96(a2),d0                                  ; +$0618 : 202A0060
    move.l d0,116(a2)                                 ; +$061C : 25400074
    add.l 56(a2),d0                                   ; +$0620 : D0AA0038
    move.l d0,96(a2)                                  ; +$0624 : 25400060
    bra.w L_008580                                    ; +$0628 : 60000018
L_00856A:
    move.l 96(a2),d0                                  ; +$062C : 202A0060
    move.l 116(a2),d1                                 ; +$0630 : 222A0074
    cmp.l d1,d0                                       ; +$0634 : B081
    bne.w L_008580                                    ; +$0636 : 6600000A
    add.l 56(a2),d0                                   ; +$063A : D0AA0038
    move.l d0,96(a2)                                  ; +$063E : 25400060
L_008580:
    move.l 64(a2),d0                                  ; +$0642 : 202A0040
    tst.l d0                                          ; +$0646 : 4A80
    beq.w L_0085B6                                    ; +$0648 : 6700002E
    move.l 104(a2),d1                                 ; +$064C : 222A0068
    addq.l #1,d1                                      ; +$0650 : 5281
    cmp.l 60(a2),d1                                   ; +$0652 : B2AA003C
    bne.w L_0085B6                                    ; +$0656 : 66000020
    movea.l 116(a2),a0                                ; +$065A : 206A0074
    move.l 56(a2),d1                                  ; +$065E : 222A0038
    lsr.l #1,d1                                       ; +$0662 : E289
L_0085A2:
    move.l #$00000000,d2                              ; +$0664 : 243C00000000
    move.w (a0)+,d2                                   ; +$066A : 3418
    and.w d0,d2                                       ; +$066C : C440
    bne.w L_0085FE                                    ; +$066E : 66000050
    subq.l #1,d1                                      ; +$0672 : 5381
    bne.w L_0085A2                                    ; +$0674 : 6600FFEE
L_0085B6:
    move.l 92(a2),d0                                  ; +$0678 : 202A005C
    tst.l d0                                          ; +$067C : 4A80
    beq.w L_0085C4                                    ; +$067E : 67000006
    bsr.w L_008606                                    ; +$0682 : 61000044
L_0085C4:
    move.l 108(a2),d0                                 ; +$0686 : 202A006C
    subq.l #1,d0                                      ; +$068A : 5380
    move.l d0,108(a2)                                 ; +$068C : 2540006C
    move.l 104(a2),d0                                 ; +$0690 : 202A0068
    addq.l #1,d0                                      ; +$0694 : 5280
    move.l d0,104(a2)                                 ; +$0696 : 25400068
    bra.w L_0084C6                                    ; +$069A : 6000FEEC
L_0085DC:
    move.l 96(a2),d0                                  ; +$069E : 202A0060
    cmp.l 100(a2),d0                                  ; +$06A2 : B0AA0064
    bne.w L_0085FE                                    ; +$06A6 : 66000018
    move.l 88(a2),d0                                  ; +$06AA : 202A0058
    addq.l #1,d0                                      ; +$06AE : 5280
    move.l d0,88(a2)                                  ; +$06B0 : 25400058
    bra.w L_00843E                                    ; +$06B4 : 6000FE4A
L_0085F6:
    move.l #$00000001,d0                              ; +$06B8 : 203C00000001
    rts                                               ; +$06BE : 4E75
L_0085FE:
    move.l #$00000000,d0                              ; +$06C0 : 203C00000000
    rts                                               ; +$06C6 : 4E75
L_008606:
    move.l 88(a2),d0                                  ; +$06C8 : 202A0058
    sub.l 20(a2),d0                                   ; +$06CC : 90AA0014
    tst.l d0                                          ; +$06D0 : 4A80
    bmi.w L_008724                                    ; +$06D2 : 6B000112
    cmp.l 12(a2),d0                                   ; +$06D6 : B0AA000C
    bge.w L_008724                                    ; +$06DA : 6C00010A
    add.l 4(a2),d0                                    ; +$06DE : D0AA0004
    tst.l d0                                          ; +$06E2 : 4A80
    bmi.w L_008724                                    ; +$06E4 : 6B000100
    cmp.l 76(a2),d0                                   ; +$06E8 : B0AA004C
    bge.w L_008724                                    ; +$06EC : 6C0000F8
    move.l d0,128(a2)                                 ; +$06F0 : 25400080
    move.l 104(a2),d0                                 ; +$06F4 : 202A0068
    lsl.l #4,d0                                       ; +$06F8 : E988
    move.l 24(a2),d1                                  ; +$06FA : 222A0018
    move.l 16(a2),d2                                  ; +$06FE : 242A0010
    add.l d1,d2                                       ; +$0702 : D481
    move.l 8(a2),d3                                   ; +$0704 : 262A0008
    move.l 72(a2),d4                                  ; +$0708 : 282A0048
    move.l 40(a2),d5                                  ; +$070C : 2A2A0028
    bsr.w L_008726                                    ; +$0710 : 610000D6
    cmp.l d6,d7                                       ; +$0714 : BE86
    ble.w L_008724                                    ; +$0716 : 6F0000CE
    move.l d6,144(a2)                                 ; +$071A : 25460090
    sub.l d6,d7                                       ; +$071E : 9E86
    move.l d7,184(a2)                                 ; +$0720 : 254700B8
    add.l d6,d0                                       ; +$0724 : D086
    sub.l 24(a2),d0                                   ; +$0726 : 90AA0018
    add.l 8(a2),d0                                    ; +$072A : D0AA0008
    move.l d0,124(a2)                                 ; +$072E : 2540007C
    move.l 128(a2),d0                                 ; +$0732 : 202A0080
    move.l 80(a2),d1                                  ; +$0736 : 222A0050
    mulu.w d1,d0                                      ; +$073A : C0C1
    move.l 124(a2),d1                                 ; +$073C : 222A007C
    lsr.l #3,d1                                       ; +$0740 : E689
    add.l d1,d0                                       ; +$0742 : D081
    move.l d0,132(a2)                                 ; +$0744 : 25400084
    movea.l 84(a2),a6                                 ; +$0748 : 2C6A0054
    addq.l #8,a6                                      ; +$074C : 508E
    lea 152(a2),a0                                    ; +$074E : 41EA0098
    move.l 48(a2),d7                                  ; +$0752 : 2E2A0030
L_008694:
    movea.l (a6)+,a1                                  ; +$0756 : 225E
    move.l a1,d1                                      ; +$0758 : 2209
    add.l 132(a2),d1                                  ; +$075A : D2AA0084
    move.l d1,(a0)+                                   ; +$075E : 20C1
    subq.w #1,d7                                      ; +$0760 : 5347
    bne.w L_008694                                    ; +$0762 : 6600FFF2
    movea.l 116(a2),a0                                ; +$0766 : 206A0074
    move.l 52(a2),d5                                  ; +$076A : 2A2A0034
    tst.l d5                                          ; +$076E : 4A85
    beq.w L_0086B4                                    ; +$0770 : 67000004
    addq.l #2,a0                                      ; +$0774 : 5488
L_0086B4:
    move.l (a2),d2                                    ; +$0776 : 2412
    tst.l d2                                          ; +$0778 : 4A82
    bne.w L_0086D2                                    ; +$077A : 66000018
    move.l #$0000FFFF,d2                              ; +$077E : 243C0000FFFF
    move.l #$FFFFFFFF,148(a2)                         ; +$0784 : 257CFFFFFFFF0094
    lea 148(a2),a1                                    ; +$078C : 43EA0094
    bra.w L_0086DE                                    ; +$0790 : 6000000E
L_0086D2:
    movea.l 116(a2),a1                                ; +$0794 : 226A0074
    move.l #$00000000,d2                              ; +$0798 : 243C00000000
    move.w (a1),d2                                    ; +$079E : 3411
L_0086DE:
    tst.l d2                                          ; +$07A0 : 4A82
    beq.w L_008724                                    ; +$07A2 : 67000042
    move.l 144(a2),d4                                 ; +$07A6 : 282A0090
    move.l 184(a2),d6                                 ; +$07AA : 2C2A00B8
    move.l 124(a2),d0                                 ; +$07AE : 202A007C
    andi.l #$00000007,d0                              ; +$07B2 : 028000000007
    move.l 48(a2),d7                                  ; +$07B8 : 2E2A0030
    tst.l d4                                          ; +$07BC : 4A84
    bne.w L_008718                                    ; +$07BE : 6600001A
    cmpi.l #$00000010,d6                              ; +$07C2 : 0C8600000010
    bne.w L_008718                                    ; +$07C8 : 66000010
    lea 152(a2),a1                                    ; +$07CC : 43EA0098
    move.l d7,d6                                      ; +$07D0 : 2C07
    bsr.w L_008774                                    ; +$07D2 : 61000062
    bra.w L_008720                                    ; +$07D6 : 6000000A
L_008718:
    lea 152(a2),a2                                    ; +$07DA : 45EA0098
    bsr.w L_008798                                    ; +$07DE : 6100007A
L_008720:
    lea 8(a7),a2                                      ; +$07E2 : 45EF0008
L_008724:
    rts                                               ; +$07E6 : 4E75
L_008726:
    move.l d0,d6                                      ; +$07E8 : 2C00
    cmp.l d1,d6                                       ; +$07EA : BC81
    bge.w L_008730                                    ; +$07EC : 6C000004
    move.l d1,d6                                      ; +$07F0 : 2C01
L_008730:
    move.l d1,d7                                      ; +$07F2 : 2E01
    sub.l d3,d7                                       ; +$07F4 : 9E83
    cmp.l d7,d6                                       ; +$07F6 : BC87
    bge.w L_00873C                                    ; +$07F8 : 6C000004
    move.l d7,d6                                      ; +$07FC : 2C07
L_00873C:
    move.l d0,d7                                      ; +$07FE : 2E00
    addi.l #$00000010,d7                              ; +$0800 : 068700000010
    cmp.l d2,d7                                       ; +$0806 : BE82
    ble.w L_00874C                                    ; +$0808 : 6F000004
    move.l d2,d7                                      ; +$080C : 2E02
L_00874C:
    cmp.l d5,d7                                       ; +$080E : BE85
    ble.w L_008754                                    ; +$0810 : 6F000004
    move.l d5,d7                                      ; +$0814 : 2E05
L_008754:
    move.l d1,d5                                      ; +$0816 : 2A01
    add.l d4,d5                                       ; +$0818 : DA84
    sub.l d3,d5                                       ; +$081A : 9A83
    cmp.l d5,d7                                       ; +$081C : BE85
    ble.w L_008762                                    ; +$081E : 6F000004
    move.l d5,d7                                      ; +$0822 : 2E05
L_008762:
    cmp.l d6,d7                                       ; +$0824 : BE86
    ble.w L_00876E                                    ; +$0826 : 6F000008
    sub.l d0,d6                                       ; +$082A : 9C80
    sub.l d0,d7                                       ; +$082C : 9E80
    rts                                               ; +$082E : 4E75
L_00876E:
    moveq #0,d6                                       ; +$0830 : 7C00
    moveq #0,d7                                       ; +$0832 : 7E00
    rts                                               ; +$0834 : 4E75
L_008774:
    bfextu (a0){0:16},d1                              ; +$0836 : E9D01010
    addq.l #2,a0                                      ; +$083A : 5488
    movea.l (a1)+,a2                                  ; +$083C : 2459
    bfextu (a2){d0:16},d4                             ; +$083E : E9D24810
    move.w d2,d7                                      ; +$0842 : 3E02
    not.w d7                                          ; +$0844 : 4647
    and.w d2,d1                                       ; +$0846 : C242
    and.w d7,d4                                       ; +$0848 : C847
    or.w d4,d1                                        ; +$084A : 8244
    bfins d1,(a2){d0:16}                              ; +$084C : EFD21810
    subq.w #1,d6                                      ; +$0850 : 5346
    bne.w L_008774                                    ; +$0852 : 6600FFE2
    moveq #1,d3                                       ; +$0856 : 7601
    rts                                               ; +$0858 : 4E75
L_008798:
    bfextu (a1){d4:d6},d2                             ; +$085A : E9D12926
L_00879C:
    bfextu (a0){d4:d6},d1                             ; +$085E : E9D01926
    addq.l #2,a0                                      ; +$0862 : 5488
    movea.l (a2)+,a4                                  ; +$0864 : 285A
    bfextu (a4){d0:d6},d3                             ; +$0866 : E9D43826
    eor.w d3,d1                                       ; +$086A : B741
    and.w d2,d1                                       ; +$086C : C242
    eor.w d3,d1                                       ; +$086E : B741
    bfins d1,(a4){d0:d6}                              ; +$0870 : EFD41826
    subq.w #1,d7                                      ; +$0874 : 5347
    bne.w L_00879C                                    ; +$0876 : 6600FFE6
    moveq #1,d3                                       ; +$087A : 7601
    rts                                               ; +$087C : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 60 : aga f icon --------
Entry_60:
Aga_F_Icon:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -96(a7),a7                                    ; +$0004 : 4FEFFFA0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l (a3)+,d7                                   ; +$001E : 2E1B
    move.l d7,16(a2)                                  ; +$0020 : 25470010
    move.l #$00000000,d3                              ; +$0024 : 263C00000000
    move.l (a2),d0                                    ; +$002A : 2012
    cmpi.l #$00000001,d0                              ; +$002C : 0C8000000001
    bhi.w L_008BB4                                    ; +$0032 : 620003C0
    move.l 8(a2),d0                                   ; +$0036 : 202A0008
    cmpi.l #$FFFF8000,d0                              ; +$003A : 0C80FFFF8000
    blt.w L_008BB4                                    ; +$0040 : 6D0003B2
    cmpi.l #$00007FFF,d0                              ; +$0044 : 0C8000007FFF
    bgt.w L_008BB4                                    ; +$004A : 6E0003A8
    move.l 4(a2),d0                                   ; +$004E : 202A0004
    cmpi.l #$FFFF8000,d0                              ; +$0052 : 0C80FFFF8000
    blt.w L_008BB4                                    ; +$0058 : 6D00039A
    cmpi.l #$00007FFF,d0                              ; +$005C : 0C8000007FFF
    bgt.w L_008BB4                                    ; +$0062 : 6E000390
    move.l 12(a2),d0                                  ; +$0066 : 202A000C
    tst.l d0                                          ; +$006A : 4A80
    ble.w L_008BB4                                    ; +$006C : 6F000386
    cmpi.l #$00001000,d0                              ; +$0070 : 0C8000001000
    bgt.w L_008BB4                                    ; +$0076 : 6E00037C
    move.l 16(a2),d0                                  ; +$007A : 202A0010
    cmpi.l #$00000005,d0                              ; +$007E : 0C8000000005
    bcs.w L_008BB4                                    ; +$0084 : 6500036E
    cmpi.l #$0000FFFF,d0                              ; +$0088 : 0C800000FFFF
    bhi.w L_008BB4                                    ; +$008E : 62000364
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$0098 : 2A08
    cmpi.l #$00000018,d5                              ; +$009A : 0C8500000018
    bls.w L_008BB4                                    ; +$00A0 : 63000352
    move.l d5,d0                                      ; +$00A4 : 2005
    andi.l #$00000001,d0                              ; +$00A6 : 028000000001
    bne.w L_008BB4                                    ; +$00AC : 66000346
    move.l d5,20(a2)                                  ; +$00B0 : 25450014
    movea.l d5,a1                                     ; +$00B4 : 2245
    movea.l $0004.w,a6                                ; +$00B6 : 2C780004
    jsr -534(a6)                                      ; +$00BA : 4EAEFDEA
    tst.l d0                                          ; +$00BE : 4A80
    beq.w L_008BB4                                    ; +$00C0 : 67000332
    move.l 20(a2),d5                                  ; +$00C4 : 2A2A0014
    move.l d5,d0                                      ; +$00C8 : 2005
    subi.l #$00000018,d0                              ; +$00CA : 048000000018
    movea.l d0,a1                                     ; +$00D0 : 2240
    movea.l $0004.w,a6                                ; +$00D2 : 2C780004
    jsr -534(a6)                                      ; +$00D6 : 4EAEFDEA
    tst.l d0                                          ; +$00DA : 4A80
    beq.w L_008BB4                                    ; +$00DC : 67000316
    movea.l d5,a0                                     ; +$00E0 : 2045
    move.l -20(a0),d4                                 ; +$00E2 : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$00E6 : 0C840000001C
    bcs.w L_008BB4                                    ; +$00EC : 65000306
    subi.l #$00000010,d4                              ; +$00F0 : 048400000010
    cmpi.l #$0012000C,d4                              ; +$00F6 : 0C840012000C
    bhi.w L_008BB4                                    ; +$00FC : 620002F6
    move.l d4,24(a2)                                  ; +$0100 : 25440018
    move.l d5,d0                                      ; +$0104 : 2005
    add.l d4,d0                                       ; +$0106 : D084
    bcs.w L_008BB4                                    ; +$0108 : 650002EA
    subq.l #1,d0                                      ; +$010C : 5380
    movea.l d0,a1                                     ; +$010E : 2240
    movea.l $0004.w,a6                                ; +$0110 : 2C780004
    jsr -534(a6)                                      ; +$0114 : 4EAEFDEA
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_008BB4                                    ; +$011A : 670002D8
    move.l 20(a2),d5                                  ; +$011E : 2A2A0014
    movea.l d5,a0                                     ; +$0122 : 2045
    move.l -16(a0),d0                                 ; +$0124 : 2028FFF0
    move.l 16(a2),d1                                  ; +$0128 : 222A0010
    cmp.l d1,d0                                       ; +$012C : B081
    bne.w L_008BB4                                    ; +$012E : 660002C4
    move.l #$00000000,d0                              ; +$0132 : 203C00000000
    move.w -12(a0),d0                                 ; +$0138 : 3028FFF4
    tst.l d0                                          ; +$013C : 4A80
    beq.w L_008910                                    ; +$013E : 67000010
    andi.w #$FFFD,d0                                  ; +$0142 : 0240FFFD
    cmpi.l #$00000001,d0                              ; +$0146 : 0C8000000001
    bne.w L_008BB4                                    ; +$014C : 660002A6
L_008910:
    move.l -8(a0),d0                                  ; +$0150 : 2028FFF8
    cmpi.l #$4649434F,d0                              ; +$0154 : 0C804649434F
    bne.w L_008BB4                                    ; +$015A : 66000298
    move.l -4(a0),d0                                  ; +$015E : 2028FFFC
    cmpi.l #$4E382020,d0                              ; +$0162 : 0C804E382020
    bne.w L_008BB4                                    ; +$0168 : 6600028A
    move.l (a0),d0                                    ; +$016C : 2010
    cmp.l 24(a2),d0                                   ; +$016E : B0AA0018
    bne.w L_008BB4                                    ; +$0172 : 66000280
    move.l #$00000000,d0                              ; +$0176 : 203C00000000
    move.w 4(a0),d0                                   ; +$017C : 30280004
    move.l d0,28(a2)                                  ; +$0180 : 2540001C
    cmpi.l #$00000004,d0                              ; +$0184 : 0C8000000004
    bcs.w L_008BB4                                    ; +$018A : 65000268
    cmpi.l #$00001000,d0                              ; +$018E : 0C8000001000
    bgt.w L_008BB4                                    ; +$0194 : 6E00025E
    move.l 12(a2),d1                                  ; +$0198 : 222A000C
    cmp.l d1,d0                                       ; +$019C : B081
    bcs.w L_008BB4                                    ; +$019E : 65000254
    move.l #$00000120,d1                              ; +$01A2 : 223C00000120
    mulu.w d1,d0                                      ; +$01A8 : C0C1
    addi.l #$0000000C,d0                              ; +$01AA : 06800000000C
    cmp.l 24(a2),d0                                   ; +$01B0 : B0AA0018
    bne.w L_008BB4                                    ; +$01B4 : 6600023E
    move.l #$00000000,d0                              ; +$01B8 : 203C00000000
    move.w 6(a0),d0                                   ; +$01BE : 30280006
    cmpi.l #$00000010,d0                              ; +$01C2 : 0C8000000010
    bne.w L_008BB4                                    ; +$01C8 : 6600022A
    move.l #$00000000,d0                              ; +$01CC : 203C00000000
    move.w 8(a0),d0                                   ; +$01D2 : 30280008
    cmpi.l #$00000010,d0                              ; +$01D6 : 0C8000000010
    bne.w L_008BB4                                    ; +$01DC : 66000216
    move.l #$00000000,d0                              ; +$01E0 : 203C00000000
    move.w 10(a0),d0                                  ; +$01E6 : 3028000A
    cmpi.l #$00000008,d0                              ; +$01EA : 0C8000000008
    bne.w L_008BB4                                    ; +$01F0 : 66000202
    move.l 12(a2),d0                                  ; +$01F4 : 202A000C
    subq.l #1,d0                                      ; +$01F8 : 5380
    move.l #$00000120,d1                              ; +$01FA : 223C00000120
    mulu.w d1,d0                                      ; +$0200 : C0C1
    addi.l #$0000000C,d0                              ; +$0202 : 06800000000C
    add.l d5,d0                                       ; +$0208 : D085
    bcs.w L_008BB4                                    ; +$020A : 650001E8
    move.l d0,32(a2)                                  ; +$020E : 25400020
    movea.l d0,a0                                     ; +$0212 : 2040
    move.l #$00000010,d6                              ; +$0214 : 2C3C00000010
L_0089DA:
    move.w (a0)+,d4                                   ; +$021A : 3818
    move.l #$00000000,d7                              ; +$021C : 2E3C00000000
    move.l #$00000008,d5                              ; +$0222 : 2A3C00000008
L_0089E8:
    or.w (a0)+,d7                                     ; +$0228 : 8E58
    subq.l #1,d5                                      ; +$022A : 5385
    bne.w L_0089E8                                    ; +$022C : 6600FFFA
    not.w d7                                          ; +$0230 : 4647
    cmp.w d4,d7                                       ; +$0232 : BE44
    bne.w L_008BB4                                    ; +$0234 : 660001BE
    subq.l #1,d6                                      ; +$0238 : 5386
    bne.w L_0089DA                                    ; +$023A : 6600FFDE
    movea.l 456(a5),a4                                ; +$023E : 286D01C8
    move.l a4,d0                                      ; +$0242 : 200C
    tst.l d0                                          ; +$0244 : 4A80
    beq.w L_008BB4                                    ; +$0246 : 670001AC
    move.l (a4),d0                                    ; +$024A : 2014
    tst.l d0                                          ; +$024C : 4A80
    beq.w L_008BB4                                    ; +$024E : 670001A4
    move.l 8(a4),d0                                   ; +$0252 : 202C0008
    tst.l d0                                          ; +$0256 : 4A80
    beq.w L_008BB4                                    ; +$0258 : 6700019A
    move.l 32(a4),d0                                  ; +$025C : 202C0020
    tst.l d0                                          ; +$0260 : 4A80
    beq.w L_008BB4                                    ; +$0262 : 67000190
    move.l 12(a4),d0                                  ; +$0266 : 202C000C
    tst.l d0                                          ; +$026A : 4A80
    ble.w L_008BB4                                    ; +$026C : 6F000186
    cmpi.l #$00007FFF,d0                              ; +$0270 : 0C8000007FFF
    bgt.w L_008BB4                                    ; +$0276 : 6E00017C
    move.l d0,36(a2)                                  ; +$027A : 25400024
    move.l 16(a4),d0                                  ; +$027E : 202C0010
    tst.l d0                                          ; +$0282 : 4A80
    ble.w L_008BB4                                    ; +$0284 : 6F00016E
    cmpi.l #$00007FFF,d0                              ; +$0288 : 0C8000007FFF
    bgt.w L_008BB4                                    ; +$028E : 6E000164
    move.l d0,40(a2)                                  ; +$0292 : 25400028
    move.l 28(a4),d0                                  ; +$0296 : 202C001C
    cmpi.l #$00000008,d0                              ; +$029A : 0C8000000008
    bne.w L_008BB4                                    ; +$02A0 : 66000152
    movea.l 32(a4),a0                                 ; +$02A4 : 206C0020
    move.l 8(a0),d0                                   ; +$02A8 : 20280008
    tst.l d0                                          ; +$02AC : 4A80
    beq.w L_008A86                                    ; +$02AE : 67000016
    cmpi.l #$00000001,d0                              ; +$02B2 : 0C8000000001
    bne.w L_008BB4                                    ; +$02B8 : 6600013A
    movea.l 32(a4),a0                                 ; +$02BC : 206C0020
    movea.l (a0),a1                                   ; +$02C0 : 2250
    bra.w L_008A8E                                    ; +$02C2 : 6000000A
L_008A86:
    movea.l 32(a4),a0                                 ; +$02C6 : 206C0020
    movea.l 4(a0),a1                                  ; +$02CA : 22680004
L_008A8E:
    move.l a1,d0                                      ; +$02CE : 2009
    tst.l d0                                          ; +$02D0 : 4A80
    beq.w L_008BB4                                    ; +$02D2 : 67000120
    movea.l (a1),a0                                   ; +$02D6 : 2051
    move.l a0,d0                                      ; +$02D8 : 2008
    tst.l d0                                          ; +$02DA : 4A80
    beq.w L_008BB4                                    ; +$02DC : 67000116
    move.l a0,48(a2)                                  ; +$02E0 : 25480030
    move.l #$00000000,d1                              ; +$02E4 : 223C00000000
    move.w (a0),d1                                    ; +$02EA : 3210
    tst.l d1                                          ; +$02EC : 4A81
    beq.w L_008BB4                                    ; +$02EE : 67000104
    move.l d1,44(a2)                                  ; +$02F2 : 2541002C
    lsl.l #3,d1                                       ; +$02F6 : E789
    cmp.l 36(a2),d1                                   ; +$02F8 : B2AA0024
    blt.w L_008BB4                                    ; +$02FC : 6D0000F6
    move.l #$00000000,d1                              ; +$0300 : 223C00000000
    move.w 2(a0),d1                                   ; +$0306 : 32280002
    cmp.l 40(a2),d1                                   ; +$030A : B2AA0028
    blt.w L_008BB4                                    ; +$030E : 6D0000E4
    move.l #$00000000,d1                              ; +$0312 : 223C00000000
    move.b 5(a0),d1                                   ; +$0318 : 12280005
    cmpi.l #$00000008,d1                              ; +$031C : 0C8100000008
    bne.w L_008BB4                                    ; +$0322 : 660000D0
    movea.l a0,a1                                     ; +$0326 : 2248
    addq.l #8,a1                                      ; +$0328 : 5089
    move.l #$00000008,d0                              ; +$032A : 203C00000008
L_008AF0:
    move.l (a1)+,d1                                   ; +$0330 : 2219
    tst.l d1                                          ; +$0332 : 4A81
    beq.w L_008BB4                                    ; +$0334 : 670000BE
    cmpi.l #$FFFFFFFF,d1                              ; +$0338 : 0C81FFFFFFFF
    beq.w L_008BB4                                    ; +$033E : 670000B4
    move.l d1,d5                                      ; +$0342 : 2A01
    andi.l #$00000001,d5                              ; +$0344 : 028500000001
    bne.w L_008BB4                                    ; +$034A : 660000A8
    subq.l #1,d0                                      ; +$034E : 5380
    bne.w L_008AF0                                    ; +$0350 : 6600FFDE
    move.l 8(a2),d0                                   ; +$0354 : 202A0008
    cmp.l 36(a2),d0                                   ; +$0358 : B0AA0024
    bge.w L_008BAA                                    ; +$035C : 6C00008C
    addi.l #$00000010,d0                              ; +$0360 : 068000000010
    tst.l d0                                          ; +$0366 : 4A80
    ble.w L_008BAA                                    ; +$0368 : 6F000080
    move.l 4(a2),d0                                   ; +$036C : 202A0004
    cmp.l 40(a2),d0                                   ; +$0370 : B0AA0028
    bge.w L_008BAA                                    ; +$0374 : 6C000074
    addi.l #$00000010,d0                              ; +$0378 : 068000000010
    tst.l d0                                          ; +$037E : 4A80
    ble.w L_008BAA                                    ; +$0380 : 6F000068
    movea.l 32(a4),a0                                 ; +$0384 : 206C0020
    move.l 20(a0),d0                                  ; +$0388 : 20280014
    andi.l #$00000001,d0                              ; +$038C : 028000000001
    beq.w L_008B82                                    ; +$0392 : 6700002E
    movea.l 12(a0),a0                                 ; +$0396 : 2068000C
    move.l a0,d0                                      ; +$039A : 2008
    tst.l d0                                          ; +$039C : 4A80
    beq.w L_008BB4                                    ; +$039E : 67000054
    movea.l $0004.w,a6                                ; +$03A2 : 2C780004
    jsr -372(a6)                                      ; +$03A6 : 4EAEFE8C
    tst.l d0                                          ; +$03AA : 4A80
    beq.w L_008BB4                                    ; +$03AC : 67000046
    movea.l 32(a4),a0                                 ; +$03B0 : 206C0020
    move.l 20(a0),d0                                  ; +$03B4 : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$03B8 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$03BE : 21400014
L_008B82:
    move.l 8(a2),d0                                   ; +$03C2 : 202A0008
    move.l 4(a2),d1                                   ; +$03C6 : 222A0004
    move.l 44(a2),d2                                  ; +$03CA : 242A002C
    move.l (a2),d3                                    ; +$03CE : 2612
    move.l 36(a2),d4                                  ; +$03D0 : 282A0024
    move.l 40(a2),d5                                  ; +$03D4 : 2A2A0028
    movea.l 32(a2),a0                                 ; +$03D8 : 206A0020
    movea.l 48(a2),a1                                 ; +$03DC : 226A0030
    addq.l #8,a1                                      ; +$03E0 : 5089
    bsr.w L_008BC6                                    ; +$03E2 : 61000022
    bra.w L_008BBA                                    ; +$03E6 : 60000012
L_008BAA:
    move.l #$00000001,d3                              ; +$03EA : 263C00000001
    bra.w L_008BBA                                    ; +$03F0 : 60000008
L_008BB4:
    move.l #$00000000,d3                              ; +$03F4 : 263C00000000
L_008BBA:
    lea 96(a7),a7                                     ; +$03FA : 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$03FE : 4CDF77F7
    moveq #0,d2                                       ; +$0402 : 7400
    rts                                               ; +$0404 : 4E75
L_008BC6:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0406 : 48E7EFEE
    lea -96(a7),a7                                    ; +$040A : 4FEFFFA0
    movea.l a7,a2                                     ; +$040E : 244F
    move.l d0,(a2)                                    ; +$0410 : 2480
    move.l d1,4(a2)                                   ; +$0412 : 25410004
    move.l d2,8(a2)                                   ; +$0416 : 25420008
    move.l d4,12(a2)                                  ; +$041A : 2544000C
    move.l d5,16(a2)                                  ; +$041E : 25450010
    move.l d3,20(a2)                                  ; +$0422 : 25430014
    move.l a0,d6                                      ; +$0426 : 2C08
    tst.l d6                                          ; +$0428 : 4A86
    beq.w L_008E6C                                    ; +$042A : 67000280
    andi.l #$00000001,d6                              ; +$042E : 028600000001
    bne.w L_008E6C                                    ; +$0434 : 66000276
    move.l a1,d6                                      ; +$0438 : 2C09
    tst.l d6                                          ; +$043A : 4A86
    beq.w L_008E6C                                    ; +$043C : 6700026E
    andi.l #$00000001,d6                              ; +$0440 : 028600000001
    bne.w L_008E6C                                    ; +$0446 : 66000264
    cmpi.l #$FFFF8000,d0                              ; +$044A : 0C80FFFF8000
    blt.w L_008E6C                                    ; +$0450 : 6D00025A
    cmpi.l #$00007FFF,d0                              ; +$0454 : 0C8000007FFF
    bgt.w L_008E6C                                    ; +$045A : 6E000250
    cmpi.l #$FFFF8000,d1                              ; +$045E : 0C81FFFF8000
    blt.w L_008E6C                                    ; +$0464 : 6D000246
    cmpi.l #$00007FFF,d1                              ; +$0468 : 0C8100007FFF
    bgt.w L_008E6C                                    ; +$046E : 6E00023C
    cmpi.l #$00000001,d3                              ; +$0472 : 0C8300000001
    bgt.w L_008E6C                                    ; +$0478 : 6E000232
    tst.l d3                                          ; +$047C : 4A83
    bmi.w L_008E6C                                    ; +$047E : 6B00022C
    tst.l d4                                          ; +$0482 : 4A84
    ble.w L_008E6C                                    ; +$0484 : 6F000226
    cmpi.l #$00001000,d4                              ; +$0488 : 0C8400001000
    bgt.w L_008E6C                                    ; +$048E : 6E00021C
    tst.l d5                                          ; +$0492 : 4A85
    ble.w L_008E6C                                    ; +$0494 : 6F000216
    cmpi.l #$00001000,d5                              ; +$0498 : 0C8500001000
    bgt.w L_008E6C                                    ; +$049E : 6E00020C
    tst.l d2                                          ; +$04A2 : 4A82
    ble.w L_008E6C                                    ; +$04A4 : 6F000206
    cmpi.l #$0000FFFF,d2                              ; +$04A8 : 0C820000FFFF
    bgt.w L_008E6C                                    ; +$04AE : 6E0001FC
    move.l d2,d6                                      ; +$04B2 : 2C02
    andi.l #$00000001,d6                              ; +$04B4 : 028600000001
    bne.w L_008E6C                                    ; +$04BA : 660001F0
    move.l d4,d6                                      ; +$04BE : 2C04
    addi.l #$0000000F,d6                              ; +$04C0 : 06860000000F
    lsr.l #4,d6                                       ; +$04C6 : E88E
    lsl.l #1,d6                                       ; +$04C8 : E38E
    cmp.l d6,d2                                       ; +$04CA : B486
    bcs.w L_008E6C                                    ; +$04CC : 650001DE
    movea.l a1,a4                                     ; +$04D0 : 2849
    move.l #$00000008,d6                              ; +$04D2 : 2C3C00000008
L_008C98:
    move.l (a4)+,d7                                   ; +$04D8 : 2E1C
    tst.l d7                                          ; +$04DA : 4A87
    beq.w L_008E6C                                    ; +$04DC : 670001CE
    cmpi.l #$FFFFFFFF,d7                              ; +$04E0 : 0C87FFFFFFFF
    beq.w L_008E6C                                    ; +$04E6 : 670001C4
    andi.l #$00000001,d7                              ; +$04EA : 028700000001
    bne.w L_008E6C                                    ; +$04F0 : 660001BA
    subq.l #1,d6                                      ; +$04F4 : 5386
    bne.w L_008C98                                    ; +$04F6 : 6600FFE0
    move.l d0,d6                                      ; +$04FA : 2C00
    addi.l #$00000010,d6                              ; +$04FC : 068600000010
    tst.l d6                                          ; +$0502 : 4A86
    ble.w L_008E62                                    ; +$0504 : 6F00019C
    cmp.l d4,d0                                       ; +$0508 : B084
    bge.w L_008E62                                    ; +$050A : 6C000196
    move.l d0,d6                                      ; +$050E : 2C00
    asr.l #4,d6                                       ; +$0510 : E886
    move.l d6,32(a2)                                  ; +$0512 : 25460020
    move.l d0,d6                                      ; +$0516 : 2C00
    andi.l #$0000000F,d6                              ; +$0518 : 02860000000F
    move.l d6,24(a2)                                  ; +$051E : 25460018
    move.l #$00000010,d7                              ; +$0522 : 2E3C00000010
    sub.l d6,d7                                       ; +$0528 : 9E86
    move.l d7,28(a2)                                  ; +$052A : 2547001C
    move.l d4,d6                                      ; +$052E : 2C04
    subq.l #1,d6                                      ; +$0530 : 5386
    lsr.l #4,d6                                       ; +$0532 : E88E
    move.l d6,36(a2)                                  ; +$0534 : 25460024
    move.l #$0000FFFF,d6                              ; +$0538 : 2C3C0000FFFF
    move.l d4,d7                                      ; +$053E : 2E04
    andi.l #$0000000F,d7                              ; +$0540 : 02870000000F
    tst.l d7                                          ; +$0546 : 4A87
    beq.w L_008D1C                                    ; +$0548 : 67000012
    move.l #$00000010,d0                              ; +$054C : 203C00000010
    sub.l d7,d0                                       ; +$0552 : 9087
L_008D14:
    lsl.w #1,d6                                       ; +$0554 : E34E
    subq.l #1,d0                                      ; +$0556 : 5380
    bne.w L_008D14                                    ; +$0558 : 6600FFFA
L_008D1C:
    move.w d6,40(a2)                                  ; +$055C : 35460028
    movea.l a0,a6                                     ; +$0560 : 2C48
    move.l #$00000000,d2                              ; +$0562 : 243C00000000
L_008D28:
    move.l 4(a2),d7                                   ; +$0568 : 2E2A0004
    add.l d2,d7                                       ; +$056C : DE82
    tst.l d7                                          ; +$056E : 4A87
    bmi.w L_008E52                                    ; +$0570 : 6B000120
    cmp.l 16(a2),d7                                   ; +$0574 : BEAA0010
    bge.w L_008E52                                    ; +$0578 : 6C000118
    move.l 8(a2),d6                                   ; +$057C : 2C2A0008
    mulu.w d6,d7                                      ; +$0580 : CEC6
    move.l 32(a2),d6                                  ; +$0582 : 2C2A0020
    lsl.l #1,d6                                       ; +$0586 : E38E
    add.l d6,d7                                       ; +$0588 : DE86
    move.l d7,44(a2)                                  ; +$058A : 2547002C
    addq.l #2,d7                                      ; +$058E : 5487
    move.l d7,48(a2)                                  ; +$0590 : 25470030
    move.w (a6)+,d4                                   ; +$0594 : 381E
    tst.l 20(a2)                                      ; +$0596 : 4AAA0014
    beq.w L_008D64                                    ; +$059A : 67000008
    not.w d4                                          ; +$059E : 4644
    bra.w L_008D68                                    ; +$05A0 : 60000006
L_008D64:
    move.w #$FFFF,d4                                  ; +$05A4 : 383CFFFF
L_008D68:
    move.w d4,d5                                      ; +$05A8 : 3A04
    move.l 24(a2),d7                                  ; +$05AA : 2E2A0018
    lsr.w d7,d5                                       ; +$05AE : EE6D
    move.w d5,52(a2)                                  ; +$05B0 : 35450034
    move.w d4,d5                                      ; +$05B4 : 3A04
    move.l 28(a2),d7                                  ; +$05B6 : 2E2A001C
    lsl.w d7,d5                                       ; +$05BA : EF6D
    move.w d5,56(a2)                                  ; +$05BC : 35450038
    move.l 32(a2),d6                                  ; +$05C0 : 2C2A0020
    tst.l d6                                          ; +$05C4 : 4A86
    bmi.w L_008DA6                                    ; +$05C6 : 6B00001E
    cmp.l 36(a2),d6                                   ; +$05CA : BCAA0024
    bgt.w L_008DA6                                    ; +$05CE : 6E000016
    bne.w L_008DAE                                    ; +$05D2 : 6600001A
    move.w 52(a2),d7                                  ; +$05D6 : 3E2A0034
    and.w 40(a2),d7                                   ; +$05DA : CE6A0028
    move.w d7,52(a2)                                  ; +$05DE : 35470034
    bra.w L_008DAE                                    ; +$05E2 : 6000000A
L_008DA6:
    move.l #$00000000,52(a2)                          ; +$05E6 : 257C000000000034
L_008DAE:
    addq.l #1,d6                                      ; +$05EE : 5286
    tst.l d6                                          ; +$05F0 : 4A86
    bmi.w L_008DD2                                    ; +$05F2 : 6B00001E
    cmp.l 36(a2),d6                                   ; +$05F6 : BCAA0024
    bgt.w L_008DD2                                    ; +$05FA : 6E000016
    bne.w L_008DDA                                    ; +$05FE : 6600001A
    move.w 56(a2),d7                                  ; +$0602 : 3E2A0038
    and.w 40(a2),d7                                   ; +$0606 : CE6A0028
    move.w d7,56(a2)                                  ; +$060A : 35470038
    bra.w L_008DDA                                    ; +$060E : 6000000A
L_008DD2:
    move.l #$00000000,56(a2)                          ; +$0612 : 257C000000000038
L_008DDA:
    move.w 52(a2),d6                                  ; +$061A : 3C2A0034
    or.w 56(a2),d6                                    ; +$061E : 8C6A0038
    tst.w d6                                          ; +$0622 : 4A46
    beq.w L_008E4A                                    ; +$0624 : 67000064
    movea.l a1,a5                                     ; +$0628 : 2A49
    move.l #$00000008,d1                              ; +$062A : 223C00000008
L_008DF0:
    move.w (a6)+,d5                                   ; +$0630 : 3A1E
    movea.l (a5)+,a0                                  ; +$0632 : 205D
    move.w 52(a2),d6                                  ; +$0634 : 3C2A0034
    tst.w d6                                          ; +$0638 : 4A46
    beq.w L_008E1A                                    ; +$063A : 6700001E
    move.w d5,d0                                      ; +$063E : 3005
    move.l 24(a2),d7                                  ; +$0640 : 2E2A0018
    lsr.w d7,d0                                       ; +$0644 : EE68
    and.w d6,d0                                       ; +$0646 : C046
    not.w d6                                          ; +$0648 : 4646
    movea.l a0,a4                                     ; +$064A : 2848
    move.l 44(a2),d7                                  ; +$064C : 2E2A002C
    adda.l d7,a4                                      ; +$0650 : D9C7
    move.w (a4),d4                                    ; +$0652 : 3814
    and.w d6,d4                                       ; +$0654 : C846
    or.w d0,d4                                        ; +$0656 : 8840
    move.w d4,(a4)                                    ; +$0658 : 3884
L_008E1A:
    move.w 56(a2),d6                                  ; +$065A : 3C2A0038
    tst.w d6                                          ; +$065E : 4A46
    beq.w L_008E40                                    ; +$0660 : 6700001E
    move.w d5,d0                                      ; +$0664 : 3005
    move.l 28(a2),d7                                  ; +$0666 : 2E2A001C
    lsl.w d7,d0                                       ; +$066A : EF68
    and.w d6,d0                                       ; +$066C : C046
    not.w d6                                          ; +$066E : 4646
    movea.l a0,a4                                     ; +$0670 : 2848
    move.l 48(a2),d7                                  ; +$0672 : 2E2A0030
    adda.l d7,a4                                      ; +$0676 : D9C7
    move.w (a4),d4                                    ; +$0678 : 3814
    and.w d6,d4                                       ; +$067A : C846
    or.w d0,d4                                        ; +$067C : 8840
    move.w d4,(a4)                                    ; +$067E : 3884
L_008E40:
    subq.l #1,d1                                      ; +$0680 : 5381
    bne.w L_008DF0                                    ; +$0682 : 6600FFAC
    bra.w L_008E56                                    ; +$0686 : 6000000E
L_008E4A:
    lea 16(a6),a6                                     ; +$068A : 4DEE0010
    bra.w L_008E56                                    ; +$068E : 60000006
L_008E52:
    lea 18(a6),a6                                     ; +$0692 : 4DEE0012
L_008E56:
    addq.l #1,d2                                      ; +$0696 : 5282
    cmpi.l #$00000010,d2                              ; +$0698 : 0C8200000010
    bne.w L_008D28                                    ; +$069E : 6600FEC8
L_008E62:
    move.l #$00000001,d3                              ; +$06A2 : 263C00000001
    bra.w L_008E72                                    ; +$06A8 : 60000008
L_008E6C:
    move.l #$00000000,d3                              ; +$06AC : 263C00000000
L_008E72:
    lea 96(a7),a7                                     ; +$06B2 : 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$06B6 : 4CDF77F7
    moveq #0,d2                                       ; +$06BA : 7400
    rts                                               ; +$06BC : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 61 : aga f blit --------
Entry_61:
Aga_F_Blit:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -96(a7),a7                                    ; +$0004 : 4FEFFFA0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l (a3)+,d7                                   ; +$001E : 2E1B
    move.l d7,16(a2)                                  ; +$0020 : 25470010
    move.l #$00000000,d3                              ; +$0024 : 263C00000000
    move.l (a2),d0                                    ; +$002A : 2012
    tst.l d0                                          ; +$002C : 4A80
    bmi.w L_0092BC                                    ; +$002E : 6B00040A
    cmpi.l #$00000001,d0                              ; +$0032 : 0C8000000001
    bgt.w L_0092BC                                    ; +$0038 : 6E000400
    move.l 8(a2),d0                                   ; +$003C : 202A0008
    cmpi.l #$FFFF8000,d0                              ; +$0040 : 0C80FFFF8000
    blt.w L_0092BC                                    ; +$0046 : 6D0003F2
    cmpi.l #$00007FFF,d0                              ; +$004A : 0C8000007FFF
    bgt.w L_0092BC                                    ; +$0050 : 6E0003E8
    move.l 4(a2),d0                                   ; +$0054 : 202A0004
    cmpi.l #$FFFF8000,d0                              ; +$0058 : 0C80FFFF8000
    blt.w L_0092BC                                    ; +$005E : 6D0003DA
    cmpi.l #$00007FFF,d0                              ; +$0062 : 0C8000007FFF
    bgt.w L_0092BC                                    ; +$0068 : 6E0003D0
    move.l 12(a2),d0                                  ; +$006C : 202A000C
    tst.l d0                                          ; +$0070 : 4A80
    ble.w L_0092BC                                    ; +$0072 : 6F0003C6
    cmpi.l #$00001000,d0                              ; +$0076 : 0C8000001000
    bgt.w L_0092BC                                    ; +$007C : 6E0003BC
    move.l 16(a2),d0                                  ; +$0080 : 202A0010
    cmpi.l #$00000005,d0                              ; +$0084 : 0C8000000005
    bcs.w L_0092BC                                    ; +$008A : 650003AE
    cmpi.l #$0000FFFF,d0                              ; +$008E : 0C800000FFFF
    bhi.w L_0092BC                                    ; +$0094 : 620003A4
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$009E : 2A08
    cmpi.l #$00000018,d5                              ; +$00A0 : 0C8500000018
    bls.w L_0092BC                                    ; +$00A6 : 63000392
    move.l d5,d0                                      ; +$00AA : 2005
    andi.l #$00000001,d0                              ; +$00AC : 028000000001
    bne.w L_0092BC                                    ; +$00B2 : 66000386
    move.l d5,20(a2)                                  ; +$00B6 : 25450014
    movea.l d5,a1                                     ; +$00BA : 2245
    movea.l $0004.w,a6                                ; +$00BC : 2C780004
    jsr -534(a6)                                      ; +$00C0 : 4EAEFDEA
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_0092BC                                    ; +$00C6 : 67000372
    move.l 20(a2),d5                                  ; +$00CA : 2A2A0014
    move.l d5,d0                                      ; +$00CE : 2005
    subi.l #$00000018,d0                              ; +$00D0 : 048000000018
    movea.l d0,a1                                     ; +$00D6 : 2240
    movea.l $0004.w,a6                                ; +$00D8 : 2C780004
    jsr -534(a6)                                      ; +$00DC : 4EAEFDEA
    tst.l d0                                          ; +$00E0 : 4A80
    beq.w L_0092BC                                    ; +$00E2 : 67000356
    movea.l d5,a0                                     ; +$00E6 : 2045
    move.l -20(a0),d4                                 ; +$00E8 : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$00EC : 0C840000001C
    bcs.w L_0092BC                                    ; +$00F2 : 65000346
    subi.l #$00000010,d4                              ; +$00F6 : 048400000010
    cmpi.l #$0012100C,d4                              ; +$00FC : 0C840012100C
    bhi.w L_0092BC                                    ; +$0102 : 62000336
    move.l d4,24(a2)                                  ; +$0106 : 25440018
    move.l d5,d0                                      ; +$010A : 2005
    add.l d4,d0                                       ; +$010C : D084
    bcs.w L_0092BC                                    ; +$010E : 6500032A
    subq.l #1,d0                                      ; +$0112 : 5380
    movea.l d0,a1                                     ; +$0114 : 2240
    movea.l $0004.w,a6                                ; +$0116 : 2C780004
    jsr -534(a6)                                      ; +$011A : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$011E : 028000000002
    beq.w L_0092BC                                    ; +$0124 : 67000314
    move.l 20(a2),d5                                  ; +$0128 : 2A2A0014
    movea.l d5,a0                                     ; +$012C : 2045
    move.l -16(a0),d0                                 ; +$012E : 2028FFF0
    move.l 16(a2),d1                                  ; +$0132 : 222A0010
    cmp.l d1,d0                                       ; +$0136 : B081
    bne.w L_0092BC                                    ; +$0138 : 66000300
    move.l #$00000000,d0                              ; +$013C : 203C00000000
    move.w -12(a0),d0                                 ; +$0142 : 3028FFF4
    tst.l d0                                          ; +$0146 : 4A80
    beq.w L_008FDA                                    ; +$0148 : 6700000E
    andi.w #$FFFD,d0                                  ; +$014C : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0150 : 0C400001
    bne.w L_0092BC                                    ; +$0154 : 660002E4
L_008FDA:
    move.l -8(a0),d0                                  ; +$0158 : 2028FFF8
    cmpi.l #$46494348,d0                              ; +$015C : 0C8046494348
    bne.w L_0092BC                                    ; +$0162 : 660002D6
    move.l -4(a0),d0                                  ; +$0166 : 2028FFFC
    cmpi.l #$49503820,d0                              ; +$016A : 0C8049503820
    bne.w L_0092BC                                    ; +$0170 : 660002C8
    move.l (a0),d0                                    ; +$0174 : 2010
    cmp.l 24(a2),d0                                   ; +$0176 : B0AA0018
    bne.w L_0092BC                                    ; +$017A : 660002BE
    move.l #$00000000,d0                              ; +$017E : 203C00000000
    move.w 4(a0),d0                                   ; +$0184 : 30280004
    move.l d0,28(a2)                                  ; +$0188 : 2540001C
    cmpi.l #$00000004,d0                              ; +$018C : 0C8000000004
    bcs.w L_0092BC                                    ; +$0192 : 650002A6
    cmpi.l #$00001000,d0                              ; +$0196 : 0C8000001000
    bgt.w L_0092BC                                    ; +$019C : 6E00029C
    move.l 12(a2),d1                                  ; +$01A0 : 222A000C
    cmp.l d1,d0                                       ; +$01A4 : B081
    bcs.w L_0092BC                                    ; +$01A6 : 65000292
    move.l #$00000121,d1                              ; +$01AA : 223C00000121
    mulu.w d1,d0                                      ; +$01B0 : C0C1
    addi.l #$0000000C,d0                              ; +$01B2 : 06800000000C
    cmp.l 24(a2),d0                                   ; +$01B8 : B0AA0018
    bne.w L_0092BC                                    ; +$01BC : 6600027C
    move.l #$00000000,d0                              ; +$01C0 : 203C00000000
    move.w 6(a0),d0                                   ; +$01C6 : 30280006
    cmpi.l #$00000010,d0                              ; +$01CA : 0C8000000010
    bne.w L_0092BC                                    ; +$01D0 : 66000268
    move.l #$00000000,d0                              ; +$01D4 : 203C00000000
    move.w 8(a0),d0                                   ; +$01DA : 30280008
    cmpi.l #$00000010,d0                              ; +$01DE : 0C8000000010
    bne.w L_0092BC                                    ; +$01E4 : 66000254
    move.l #$00000000,d0                              ; +$01E8 : 203C00000000
    move.w 10(a0),d0                                  ; +$01EE : 3028000A
    cmpi.l #$00000008,d0                              ; +$01F2 : 0C8000000008
    bne.w L_0092BC                                    ; +$01F8 : 66000240
    move.l 28(a2),d0                                  ; +$01FC : 202A001C
    move.l #$00000120,d1                              ; +$0200 : 223C00000120
    mulu.w d1,d0                                      ; +$0206 : C0C1
    addi.l #$0000000C,d0                              ; +$0208 : 06800000000C
    move.l 12(a2),d1                                  ; +$020E : 222A000C
    subq.l #1,d1                                      ; +$0212 : 5381
    add.l d1,d0                                       ; +$0214 : D081
    add.l d5,d0                                       ; +$0216 : D085
    bcs.w L_0092BC                                    ; +$0218 : 65000220
    move.l d0,48(a2)                                  ; +$021C : 25400030
    movea.l d0,a0                                     ; +$0220 : 2040
    move.l #$00000000,d0                              ; +$0222 : 203C00000000
    move.b (a0),d0                                    ; +$0228 : 1010
    cmpi.l #$00000001,d0                              ; +$022A : 0C8000000001
    bne.w L_0092BC                                    ; +$0230 : 66000208
    move.l 12(a2),d0                                  ; +$0234 : 202A000C
    subq.l #1,d0                                      ; +$0238 : 5380
    move.l #$00000120,d1                              ; +$023A : 223C00000120
    mulu.w d1,d0                                      ; +$0240 : C0C1
    addi.l #$0000000C,d0                              ; +$0242 : 06800000000C
    add.l d5,d0                                       ; +$0248 : D085
    bcs.w L_0092BC                                    ; +$024A : 650001EE
    move.l d0,32(a2)                                  ; +$024E : 25400020
    movea.l d0,a0                                     ; +$0252 : 2040
    movea.l d0,a1                                     ; +$0254 : 2240
    lea 32(a1),a1                                     ; +$0256 : 43E90020
    move.l #$00000010,d6                              ; +$025A : 2C3C00000010
L_0090E2:
    move.w (a0)+,d4                                   ; +$0260 : 3818
    movea.l a1,a6                                     ; +$0262 : 2C49
    move.l #$00000000,d7                              ; +$0264 : 2E3C00000000
    move.l #$00000008,d5                              ; +$026A : 2A3C00000008
L_0090F2:
    or.w (a6),d7                                      ; +$0270 : 8E56
    lea 32(a6),a6                                     ; +$0272 : 4DEE0020
    subq.l #1,d5                                      ; +$0276 : 5385
    bne.w L_0090F2                                    ; +$0278 : 6600FFF6
    cmp.w d4,d7                                       ; +$027C : BE44
    bne.w L_0092BC                                    ; +$027E : 660001BA
    addq.l #2,a1                                      ; +$0282 : 5489
    subq.l #1,d6                                      ; +$0284 : 5386
    bne.w L_0090E2                                    ; +$0286 : 6600FFD8
    movea.l 456(a5),a4                                ; +$028A : 286D01C8
    move.l a4,d0                                      ; +$028E : 200C
    tst.l d0                                          ; +$0290 : 4A80
    beq.w L_0092BC                                    ; +$0292 : 670001A6
    move.l (a4),d0                                    ; +$0296 : 2014
    tst.l d0                                          ; +$0298 : 4A80
    beq.w L_0092BC                                    ; +$029A : 6700019E
    move.l 8(a4),d0                                   ; +$029E : 202C0008
    tst.l d0                                          ; +$02A2 : 4A80
    beq.w L_0092BC                                    ; +$02A4 : 67000194
    move.l 32(a4),d0                                  ; +$02A8 : 202C0020
    tst.l d0                                          ; +$02AC : 4A80
    beq.w L_0092BC                                    ; +$02AE : 6700018A
    move.l 12(a4),d0                                  ; +$02B2 : 202C000C
    tst.l d0                                          ; +$02B6 : 4A80
    ble.w L_0092BC                                    ; +$02B8 : 6F000180
    cmpi.l #$00007FFF,d0                              ; +$02BC : 0C8000007FFF
    bgt.w L_0092BC                                    ; +$02C2 : 6E000176
    move.l d0,36(a2)                                  ; +$02C6 : 25400024
    move.l 16(a4),d0                                  ; +$02CA : 202C0010
    tst.l d0                                          ; +$02CE : 4A80
    ble.w L_0092BC                                    ; +$02D0 : 6F000168
    cmpi.l #$00007FFF,d0                              ; +$02D4 : 0C8000007FFF
    bgt.w L_0092BC                                    ; +$02DA : 6E00015E
    move.l d0,40(a2)                                  ; +$02DE : 25400028
    move.l 28(a4),d0                                  ; +$02E2 : 202C001C
    cmpi.l #$00000008,d0                              ; +$02E6 : 0C8000000008
    bne.w L_0092BC                                    ; +$02EC : 6600014C
    movea.l 32(a4),a0                                 ; +$02F0 : 206C0020
    move.l 8(a0),d0                                   ; +$02F4 : 20280008
    tst.l d0                                          ; +$02F8 : 4A80
    beq.w L_009194                                    ; +$02FA : 67000016
    cmpi.l #$00000001,d0                              ; +$02FE : 0C8000000001
    bne.w L_0092BC                                    ; +$0304 : 66000134
    movea.l 32(a4),a0                                 ; +$0308 : 206C0020
    movea.l (a0),a1                                   ; +$030C : 2250
    bra.w L_00919C                                    ; +$030E : 6000000A
L_009194:
    movea.l 32(a4),a0                                 ; +$0312 : 206C0020
    movea.l 4(a0),a1                                  ; +$0316 : 22680004
L_00919C:
    move.l a1,d0                                      ; +$031A : 2009
    tst.l d0                                          ; +$031C : 4A80
    beq.w L_0092BC                                    ; +$031E : 6700011A
    movea.l (a1),a0                                   ; +$0322 : 2051
    move.l a0,d0                                      ; +$0324 : 2008
    tst.l d0                                          ; +$0326 : 4A80
    beq.w L_0092BC                                    ; +$0328 : 67000110
    move.l a0,44(a2)                                  ; +$032C : 2548002C
    move.l #$00000000,d1                              ; +$0330 : 223C00000000
    move.w (a0),d1                                    ; +$0336 : 3210
    tst.l d1                                          ; +$0338 : 4A81
    beq.w L_0092BC                                    ; +$033A : 670000FE
    lsl.l #3,d1                                       ; +$033E : E789
    cmp.l 36(a2),d1                                   ; +$0340 : B2AA0024
    blt.w L_0092BC                                    ; +$0344 : 6D0000F4
    move.l #$00000000,d1                              ; +$0348 : 223C00000000
    move.w 2(a0),d1                                   ; +$034E : 32280002
    cmp.l 40(a2),d1                                   ; +$0352 : B2AA0028
    blt.w L_0092BC                                    ; +$0356 : 6D0000E2
    move.l #$00000000,d1                              ; +$035A : 223C00000000
    move.b 5(a0),d1                                   ; +$0360 : 12280005
    cmpi.l #$00000008,d1                              ; +$0364 : 0C8100000008
    bne.w L_0092BC                                    ; +$036A : 660000CE
    movea.l a0,a1                                     ; +$036E : 2248
    addq.l #8,a1                                      ; +$0370 : 5089
    move.l #$00000008,d0                              ; +$0372 : 203C00000008
L_0091FA:
    move.l (a1)+,d1                                   ; +$0378 : 2219
    tst.l d1                                          ; +$037A : 4A81
    beq.w L_0092BC                                    ; +$037C : 670000BC
    cmpi.l #$FFFFFFFF,d1                              ; +$0380 : 0C81FFFFFFFF
    beq.w L_0092BC                                    ; +$0386 : 670000B2
    move.l d1,d5                                      ; +$038A : 2A01
    andi.l #$00000001,d5                              ; +$038C : 028500000001
    bne.w L_0092BC                                    ; +$0392 : 660000A6
    subq.l #1,d0                                      ; +$0396 : 5380
    bne.w L_0091FA                                    ; +$0398 : 6600FFDE
    move.l 8(a2),d0                                   ; +$039C : 202A0008
    cmp.l 36(a2),d0                                   ; +$03A0 : B0AA0024
    bge.w L_0092B2                                    ; +$03A4 : 6C00008A
    addi.l #$00000010,d0                              ; +$03A8 : 068000000010
    tst.l d0                                          ; +$03AE : 4A80
    ble.w L_0092B2                                    ; +$03B0 : 6F00007E
    move.l 4(a2),d0                                   ; +$03B4 : 202A0004
    cmp.l 40(a2),d0                                   ; +$03B8 : B0AA0028
    bge.w L_0092B2                                    ; +$03BC : 6C000072
    addi.l #$00000010,d0                              ; +$03C0 : 068000000010
    tst.l d0                                          ; +$03C6 : 4A80
    ble.w L_0092B2                                    ; +$03C8 : 6F000066
    movea.l 32(a4),a0                                 ; +$03CC : 206C0020
    move.l 20(a0),d0                                  ; +$03D0 : 20280014
    andi.l #$00000001,d0                              ; +$03D4 : 028000000001
    beq.w L_00928C                                    ; +$03DA : 6700002E
    movea.l 12(a0),a0                                 ; +$03DE : 2068000C
    move.l a0,d0                                      ; +$03E2 : 2008
    tst.l d0                                          ; +$03E4 : 4A80
    beq.w L_0092BC                                    ; +$03E6 : 67000052
    movea.l $0004.w,a6                                ; +$03EA : 2C780004
    jsr -372(a6)                                      ; +$03EE : 4EAEFE8C
    tst.l d0                                          ; +$03F2 : 4A80
    beq.w L_0092BC                                    ; +$03F4 : 67000044
    movea.l 32(a4),a0                                 ; +$03F8 : 206C0020
    move.l 20(a0),d0                                  ; +$03FC : 20280014
    andi.l #$FFFFFFFE,d0                              ; +$0400 : 0280FFFFFFFE
    move.l d0,20(a0)                                  ; +$0406 : 21400014
L_00928C:
    move.l 8(a2),d0                                   ; +$040A : 202A0008
    move.l 4(a2),d1                                   ; +$040E : 222A0004
    move.l (a2),d3                                    ; +$0412 : 2612
    move.l 36(a2),d4                                  ; +$0414 : 282A0024
    move.l 40(a2),d5                                  ; +$0418 : 2A2A0028
    movea.l 32(a2),a0                                 ; +$041C : 206A0020
    movea.l 44(a2),a1                                 ; +$0420 : 226A002C
    movea.l 8(a4),a6                                  ; +$0424 : 2C6C0008
    bsr.w L_0092CE                                    ; +$0428 : 61000022
    bra.w L_0092C2                                    ; +$042C : 60000012
L_0092B2:
    move.l #$00000001,d3                              ; +$0430 : 263C00000001
    bra.w L_0092C2                                    ; +$0436 : 60000008
L_0092BC:
    move.l #$00000000,d3                              ; +$043A : 263C00000000
L_0092C2:
    lea 96(a7),a7                                     ; +$0440 : 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0444 : 4CDF77F7
    moveq #0,d2                                       ; +$0448 : 7400
    rts                                               ; +$044A : 4E75
L_0092CE:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$044C : 48E7EFEE
    lea -256(a7),a7                                   ; +$0450 : 4FEFFF00
    movea.l a7,a4                                     ; +$0454 : 284F
    move.l a0,192(a4)                                 ; +$0456 : 294800C0
    move.l a1,196(a4)                                 ; +$045A : 294900C4
    move.l a6,244(a4)                                 ; +$045E : 294E00F4
    move.l d0,200(a4)                                 ; +$0462 : 294000C8
    move.l d1,204(a4)                                 ; +$0466 : 294100CC
    move.l d3,208(a4)                                 ; +$046A : 294300D0
    move.l d4,212(a4)                                 ; +$046E : 294400D4
    move.l d5,216(a4)                                 ; +$0472 : 294500D8
    move.l 192(a4),d6                                 ; +$0476 : 2C2C00C0
    tst.l d6                                          ; +$047A : 4A86
    beq.w L_0095BA                                    ; +$047C : 670002BA
    andi.l #$00000001,d6                              ; +$0480 : 028600000001
    bne.w L_0095BA                                    ; +$0486 : 660002B0
    move.l 196(a4),d6                                 ; +$048A : 2C2C00C4
    tst.l d6                                          ; +$048E : 4A86
    beq.w L_0095BA                                    ; +$0490 : 670002A6
    andi.l #$00000001,d6                              ; +$0494 : 028600000001
    bne.w L_0095BA                                    ; +$049A : 6600029C
    move.l 244(a4),d6                                 ; +$049E : 2C2C00F4
    tst.l d6                                          ; +$04A2 : 4A86
    beq.w L_0095BA                                    ; +$04A4 : 67000292
    andi.l #$00000001,d6                              ; +$04A8 : 028600000001
    bne.w L_0095BA                                    ; +$04AE : 66000288
    move.l 200(a4),d6                                 ; +$04B2 : 2C2C00C8
    cmpi.l #$FFFF8000,d6                              ; +$04B6 : 0C86FFFF8000
    blt.w L_0095BA                                    ; +$04BC : 6D00027A
    cmpi.l #$00007FFF,d6                              ; +$04C0 : 0C8600007FFF
    bgt.w L_0095BA                                    ; +$04C6 : 6E000270
    move.l 204(a4),d6                                 ; +$04CA : 2C2C00CC
    cmpi.l #$FFFF8000,d6                              ; +$04CE : 0C86FFFF8000
    blt.w L_0095BA                                    ; +$04D4 : 6D000262
    cmpi.l #$00007FFF,d6                              ; +$04D8 : 0C8600007FFF
    bgt.w L_0095BA                                    ; +$04DE : 6E000258
    move.l 208(a4),d6                                 ; +$04E2 : 2C2C00D0
    tst.l d6                                          ; +$04E6 : 4A86
    bmi.w L_0095BA                                    ; +$04E8 : 6B00024E
    cmpi.l #$00000001,d6                              ; +$04EC : 0C8600000001
    bgt.w L_0095BA                                    ; +$04F2 : 6E000244
    move.l 212(a4),d6                                 ; +$04F6 : 2C2C00D4
    tst.l d6                                          ; +$04FA : 4A86
    ble.w L_0095BA                                    ; +$04FC : 6F00023A
    cmpi.l #$00001000,d6                              ; +$0500 : 0C8600001000
    bgt.w L_0095BA                                    ; +$0506 : 6E000230
    move.l 216(a4),d6                                 ; +$050A : 2C2C00D8
    tst.l d6                                          ; +$050E : 4A86
    ble.w L_0095BA                                    ; +$0510 : 6F000226
    cmpi.l #$00001000,d6                              ; +$0514 : 0C8600001000
    bgt.w L_0095BA                                    ; +$051A : 6E00021C
    move.l 192(a4),d6                                 ; +$051E : 2C2C00C0
    addi.l #$0000011F,d6                              ; +$0522 : 06860000011F
    bcs.w L_0095BA                                    ; +$0528 : 6500020E
    movea.l 196(a4),a0                                ; +$052C : 206C00C4
    move.l #$00000000,d6                              ; +$0530 : 2C3C00000000
    move.w (a0),d6                                    ; +$0536 : 3C10
    lsl.l #3,d6                                       ; +$0538 : E78E
    cmp.l 212(a4),d6                                  ; +$053A : BCAC00D4
    blt.w L_0095BA                                    ; +$053E : 6D0001F8
    move.l #$00000000,d6                              ; +$0542 : 2C3C00000000
    move.w 2(a0),d6                                   ; +$0548 : 3C280002
    cmp.l 216(a4),d6                                  ; +$054C : BCAC00D8
    blt.w L_0095BA                                    ; +$0550 : 6D0001E6
    move.l #$00000000,d6                              ; +$0554 : 2C3C00000000
    move.b 5(a0),d6                                   ; +$055A : 1C280005
    cmpi.l #$00000008,d6                              ; +$055E : 0C8600000008
    bne.w L_0095BA                                    ; +$0564 : 660001D2
    movea.l 196(a4),a1                                ; +$0568 : 226C00C4
    addq.l #8,a1                                      ; +$056C : 5089
    move.l #$00000008,d7                              ; +$056E : 2E3C00000008
L_0093F6:
    move.l (a1)+,d6                                   ; +$0574 : 2C19
    tst.l d6                                          ; +$0576 : 4A86
    beq.w L_0095BA                                    ; +$0578 : 670001BE
    cmpi.l #$FFFFFFFF,d6                              ; +$057C : 0C86FFFFFFFF
    beq.w L_0095BA                                    ; +$0582 : 670001B4
    andi.l #$00000001,d6                              ; +$0586 : 028600000001
    bne.w L_0095BA                                    ; +$058C : 660001AA
    subq.l #1,d7                                      ; +$0590 : 5387
    bne.w L_0093F6                                    ; +$0592 : 6600FFE0
    move.l 200(a4),d6                                 ; +$0596 : 2C2C00C8
    cmp.l 212(a4),d6                                  ; +$059A : BCAC00D4
    bge.w L_0095B0                                    ; +$059E : 6C00018E
    addi.l #$00000010,d6                              ; +$05A2 : 068600000010
    tst.l d6                                          ; +$05A8 : 4A86
    ble.w L_0095B0                                    ; +$05AA : 6F000182
    move.l 204(a4),d6                                 ; +$05AE : 2C2C00CC
    cmp.l 216(a4),d6                                  ; +$05B2 : BCAC00D8
    bge.w L_0095B0                                    ; +$05B6 : 6C000176
    addi.l #$00000010,d6                              ; +$05BA : 068600000010
    tst.l d6                                          ; +$05C0 : 4A86
    ble.w L_0095B0                                    ; +$05C2 : 6F00016A
    move.l 200(a4),d6                                 ; +$05C6 : 2C2C00C8
    tst.l d6                                          ; +$05CA : 4A86
    bmi.w L_009462                                    ; +$05CC : 6B000012
    move.l #$00000000,220(a4)                         ; +$05D0 : 297C0000000000DC
    move.l d6,228(a4)                                 ; +$05D8 : 294600E4
    bra.w L_009476                                    ; +$05DC : 60000016
L_009462:
    move.l #$00000000,228(a4)                         ; +$05E0 : 297C0000000000E4
    move.l #$00000000,d7                              ; +$05E8 : 2E3C00000000
    sub.l d6,d7                                       ; +$05EE : 9E86
    move.l d7,220(a4)                                 ; +$05F0 : 294700DC
L_009476:
    move.l #$00000010,d6                              ; +$05F4 : 2C3C00000010
    sub.l 220(a4),d6                                  ; +$05FA : 9CAC00DC
    move.l 212(a4),d7                                 ; +$05FE : 2E2C00D4
    sub.l 228(a4),d7                                  ; +$0602 : 9EAC00E4
    cmp.l d7,d6                                       ; +$0606 : BC87
    blt.w L_009490                                    ; +$0608 : 6D000004
    move.l d7,d6                                      ; +$060C : 2C07
L_009490:
    tst.l d6                                          ; +$060E : 4A86
    ble.w L_0095B0                                    ; +$0610 : 6F00011C
    move.l d6,236(a4)                                 ; +$0614 : 294600EC
    move.l 204(a4),d6                                 ; +$0618 : 2C2C00CC
    tst.l d6                                          ; +$061C : 4A86
    bmi.w L_0094B4                                    ; +$061E : 6B000012
    move.l #$00000000,224(a4)                         ; +$0622 : 297C0000000000E0
    move.l d6,232(a4)                                 ; +$062A : 294600E8
    bra.w L_0094C8                                    ; +$062E : 60000016
L_0094B4:
    move.l #$00000000,232(a4)                         ; +$0632 : 297C0000000000E8
    move.l #$00000000,d7                              ; +$063A : 2E3C00000000
    sub.l d6,d7                                       ; +$0640 : 9E86
    move.l d7,224(a4)                                 ; +$0642 : 294700E0
L_0094C8:
    move.l #$00000010,d6                              ; +$0646 : 2C3C00000010
    sub.l 224(a4),d6                                  ; +$064C : 9CAC00E0
    move.l 216(a4),d7                                 ; +$0650 : 2E2C00D8
    sub.l 232(a4),d7                                  ; +$0654 : 9EAC00E8
    cmp.l d7,d6                                       ; +$0658 : BC87
    blt.w L_0094E2                                    ; +$065A : 6D000004
    move.l d7,d6                                      ; +$065E : 2C07
L_0094E2:
    tst.l d6                                          ; +$0660 : 4A86
    ble.w L_0095B0                                    ; +$0662 : 6F0000CA
    move.l d6,240(a4)                                 ; +$0666 : 294600F0
    movea.l $0004.w,a6                                ; +$066A : 2C780004
    movea.l 192(a4),a1                                ; +$066E : 226C00C0
    jsr -534(a6)                                      ; +$0672 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0676 : 028000000002
    beq.w L_0095BA                                    ; +$067C : 670000BA
    move.l 192(a4),d6                                 ; +$0680 : 2C2C00C0
    addi.l #$0000011F,d6                              ; +$0684 : 06860000011F
    movea.l d6,a1                                     ; +$068A : 2246
    jsr -534(a6)                                      ; +$068C : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0690 : 028000000002
    beq.w L_0095BA                                    ; +$0696 : 670000A0
    move.w #$0002,(a4)                                ; +$069A : 38BC0002
    move.w #$0010,2(a4)                               ; +$069E : 397C00100002
    move.l #$00000000,4(a4)                           ; +$06A4 : 297C000000000004
    move.b #$08,5(a4)                                 ; +$06AC : 197C00080005
    movea.l 192(a4),a0                                ; +$06B2 : 206C00C0
    lea 32(a0),a0                                     ; +$06B6 : 41E80020
    lea 8(a4),a1                                      ; +$06BA : 43EC0008
    move.l #$00000008,d7                              ; +$06BE : 2E3C00000008
L_009546:
    move.l a0,(a1)+                                   ; +$06C4 : 22C8
    lea 32(a0),a0                                     ; +$06C6 : 41E80020
    subq.l #1,d7                                      ; +$06CA : 5387
    bne.w L_009546                                    ; +$06CC : 6600FFF6
    movea.l 244(a4),a6                                ; +$06D0 : 2C6C00F4
    lea 64(a4),a1                                     ; +$06D4 : 43EC0040
    jsr -198(a6)                                      ; +$06D8 : 4EAEFF3A
    lea 64(a4),a1                                     ; +$06DC : 43EC0040
    move.l 196(a4),4(a1)                              ; +$06E0 : 236C00C40004
    movea.l a4,a0                                     ; +$06E6 : 204C
    move.l 220(a4),d0                                 ; +$06E8 : 202C00DC
    move.l 224(a4),d1                                 ; +$06EC : 222C00E0
    move.l 228(a4),d2                                 ; +$06F0 : 242C00E4
    move.l 232(a4),d3                                 ; +$06F4 : 262C00E8
    move.l 236(a4),d4                                 ; +$06F8 : 282C00EC
    move.l 240(a4),d5                                 ; +$06FC : 2A2C00F0
    move.l 208(a4),d7                                 ; +$0700 : 2E2C00D0
    tst.l d7                                          ; +$0704 : 4A87
    beq.w L_00959E                                    ; +$0706 : 67000014
    move.l #$000000E0,d6                              ; +$070A : 2C3C000000E0
    movea.l 192(a4),a2                                ; +$0710 : 246C00C0
    jsr -636(a6)                                      ; +$0714 : 4EAEFD84
    bra.w L_0095A8                                    ; +$0718 : 6000000C
L_00959E:
    move.l #$000000C0,d6                              ; +$071C : 2C3C000000C0
    jsr -606(a6)                                      ; +$0722 : 4EAEFDA2
L_0095A8:
    movea.l 244(a4),a6                                ; +$0726 : 2C6C00F4
    jsr -228(a6)                                      ; +$072A : 4EAEFF1C
L_0095B0:
    move.l #$00000001,d3                              ; +$072E : 263C00000001
    bra.w L_0095C0                                    ; +$0734 : 60000008
L_0095BA:
    move.l #$00000000,d3                              ; +$0738 : 263C00000000
L_0095C0:
    lea 256(a7),a7                                    ; +$073E : 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0742 : 4CDF77F7
    moveq #0,d2                                       ; +$0746 : 7400
    rts                                               ; +$0748 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 62 : aga f icon bank create --------
Entry_62:
Aga_F_Icon_Bank_Create:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -48(a7),a7                                    ; +$0004 : 4FEFFFD0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l #$00000000,d3                              ; +$0012 : 263C00000000
    move.l (a2),d0                                    ; +$0018 : 2012
    cmpi.l #$00000004,d0                              ; +$001A : 0C8000000004
    bcs.w L_0096F4                                    ; +$0020 : 65000102
    cmpi.l #$00001000,d0                              ; +$0024 : 0C8000001000
    bhi.w L_0096F4                                    ; +$002A : 620000F8
    move.l 4(a2),d0                                   ; +$002E : 202A0004
    cmpi.l #$00000005,d0                              ; +$0032 : 0C8000000005
    bcs.w L_0096F4                                    ; +$0038 : 650000EA
    cmpi.l #$0000FFFF,d0                              ; +$003C : 0C800000FFFF
    bhi.w L_0096F4                                    ; +$0042 : 620000E0
    move.l (a2),d0                                    ; +$0046 : 2012
    move.l #$00000120,d1                              ; +$0048 : 223C00000120
    mulu.w d1,d0                                      ; +$004E : C0C1
    addi.l #$0000000C,d0                              ; +$0050 : 06800000000C
    move.l d0,8(a2)                                   ; +$0056 : 25400008
    move.l 4(a2),d0                                   ; +$005A : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0064 : 2008
    tst.l d0                                          ; +$0066 : 4A80
    bne.w L_0096F4                                    ; +$0068 : 660000BA
    move.l 4(a2),d0                                   ; +$006C : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0076 : 2008
    tst.l d0                                          ; +$0078 : 4A80
    bne.w L_0096F4                                    ; +$007A : 660000A8
    move.l 4(a2),d0                                   ; +$007E : 202A0004
    move.l #$00000001,d1                              ; +$0082 : 223C00000001
    move.l 8(a2),d2                                   ; +$0088 : 242A0008
    lea L_009700(pc),a0                               ; +$008C : 41FA00A2
    dc.b $FE,$11,$F7,$00,$03,$30
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_0096F4                                    ; +$0098 : 6700008A
    move.l d0,12(a2)                                  ; +$009C : 2540000C
    cmpi.l #$00000018,d0                              ; +$00A0 : 0C8000000018
    bls.w L_0096E4                                    ; +$00A6 : 6300006C
    move.l d0,d1                                      ; +$00AA : 2200
    andi.l #$00000001,d1                              ; +$00AC : 028100000001
    bne.w L_0096E4                                    ; +$00B2 : 66000060
    move.l 12(a2),d0                                  ; +$00B6 : 202A000C
    move.l 8(a2),d1                                   ; +$00BA : 222A0008
    add.l d1,d0                                       ; +$00BE : D081
    bcs.w L_0096E4                                    ; +$00C0 : 65000052
    movea.l 12(a2),a1                                 ; +$00C4 : 226A000C
    move.l 8(a2),d0                                   ; +$00C8 : 202A0008
    move.l d0,(a1)+                                   ; +$00CC : 22C0
    move.l (a2),d0                                    ; +$00CE : 2012
    move.w d0,(a1)+                                   ; +$00D0 : 32C0
    move.w #$0010,(a1)+                               ; +$00D2 : 32FC0010
    move.w #$0010,(a1)+                               ; +$00D6 : 32FC0010
    move.w #$0008,(a1)+                               ; +$00DA : 32FC0008
    move.l (a2),d6                                    ; +$00DE : 2C12
    lsl.l #4,d6                                       ; +$00E0 : E98E
L_0096B2:
    move.w #$FFFF,(a1)+                               ; +$00E2 : 32FCFFFF
    move.l #$00000000,(a1)+                           ; +$00E6 : 22FC00000000
    move.l #$00000000,(a1)+                           ; +$00EC : 22FC00000000
    move.l #$00000000,(a1)+                           ; +$00F2 : 22FC00000000
    move.l #$00000000,(a1)+                           ; +$00F8 : 22FC00000000
    subq.l #1,d6                                      ; +$00FE : 5386
    bne.w L_0096B2                                    ; +$0100 : 6600FFE0
    dc.b $FE,$11,$F7,$00,$03,$33
    move.l #$00000001,d3                              ; +$010A : 263C00000001
    bra.w L_0096F4                                    ; +$0110 : 60000012
L_0096E4:
    move.l 4(a2),d0                                   ; +$0114 : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$20
    move.l #$00000000,d3                              ; +$011E : 263C00000000
L_0096F4:
    lea 48(a7),a7                                     ; +$0124 : 4FEF0030
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0128 : 4CDF77F7
    moveq #0,d2                                       ; +$012C : 7400
    rts                                               ; +$012E : 4E75
L_009700:
    dc.b "FICON8  "
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 63 : aga f icon bank put --------
Entry_63:
Aga_F_Icon_Bank_Put:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -96(a7),a7                                    ; +$0004 : 4FEFFFA0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l #$00000000,d3                              ; +$001E : 263C00000000
    move.l 12(a2),d0                                  ; +$0024 : 202A000C
    cmpi.l #$00000005,d0                              ; +$0028 : 0C8000000005
    bcs.w L_009AC8                                    ; +$002E : 6500038C
    cmpi.l #$0000FFFF,d0                              ; +$0032 : 0C800000FFFF
    bhi.w L_009AC8                                    ; +$0038 : 62000382
    move.l 4(a2),d0                                   ; +$003C : 202A0004
    cmpi.l #$00000005,d0                              ; +$0040 : 0C8000000005
    bcs.w L_009AC8                                    ; +$0046 : 65000374
    cmpi.l #$0000FFFF,d0                              ; +$004A : 0C800000FFFF
    bhi.w L_009AC8                                    ; +$0050 : 6200036A
    move.l 12(a2),d0                                  ; +$0054 : 202A000C
    move.l 4(a2),d1                                   ; +$0058 : 222A0004
    cmp.l d1,d0                                       ; +$005C : B081
    beq.w L_009AC8                                    ; +$005E : 6700035C
    move.l 8(a2),d0                                   ; +$0062 : 202A0008
    tst.l d0                                          ; +$0066 : 4A80
    ble.w L_009AC8                                    ; +$0068 : 6F000352
    cmpi.l #$00001000,d0                              ; +$006C : 0C8000001000
    bgt.w L_009AC8                                    ; +$0072 : 6E000348
    move.l (a2),d0                                    ; +$0076 : 2012
    tst.l d0                                          ; +$0078 : 4A80
    bmi.w L_009AC8                                    ; +$007A : 6B000340
    move.l 12(a2),d0                                  ; +$007E : 202A000C
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$0088 : 2A08
    cmpi.l #$00000018,d5                              ; +$008A : 0C8500000018
    bls.w L_009AC8                                    ; +$0090 : 6300032A
    move.l d5,d0                                      ; +$0094 : 2005
    andi.l #$00000001,d0                              ; +$0096 : 028000000001
    bne.w L_009AC8                                    ; +$009C : 6600031E
    move.l d5,16(a2)                                  ; +$00A0 : 25450010
    movea.l d5,a1                                     ; +$00A4 : 2245
    movea.l $0004.w,a6                                ; +$00A6 : 2C780004
    jsr -534(a6)                                      ; +$00AA : 4EAEFDEA
    tst.l d0                                          ; +$00AE : 4A80
    beq.w L_009AC8                                    ; +$00B0 : 6700030A
    move.l 16(a2),d0                                  ; +$00B4 : 202A0010
    subi.l #$00000018,d0                              ; +$00B8 : 048000000018
    movea.l d0,a1                                     ; +$00BE : 2240
    movea.l $0004.w,a6                                ; +$00C0 : 2C780004
    jsr -534(a6)                                      ; +$00C4 : 4EAEFDEA
    tst.l d0                                          ; +$00C8 : 4A80
    beq.w L_009AC8                                    ; +$00CA : 670002F0
    movea.l 16(a2),a0                                 ; +$00CE : 206A0010
    move.l -20(a0),d4                                 ; +$00D2 : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$00D6 : 0C840000001C
    bcs.w L_009AC8                                    ; +$00DC : 650002DE
    subi.l #$00000010,d4                              ; +$00E0 : 048400000010
    cmpi.l #$0012000C,d4                              ; +$00E6 : 0C840012000C
    bhi.w L_009AC8                                    ; +$00EC : 620002CE
    move.l d4,20(a2)                                  ; +$00F0 : 25440014
    move.l 16(a2),d0                                  ; +$00F4 : 202A0010
    add.l d4,d0                                       ; +$00F8 : D084
    bcs.w L_009AC8                                    ; +$00FA : 650002C0
    subq.l #1,d0                                      ; +$00FE : 5380
    movea.l d0,a1                                     ; +$0100 : 2240
    movea.l $0004.w,a6                                ; +$0102 : 2C780004
    jsr -534(a6)                                      ; +$0106 : 4EAEFDEA
    tst.l d0                                          ; +$010A : 4A80
    beq.w L_009AC8                                    ; +$010C : 670002AE
    movea.l 16(a2),a0                                 ; +$0110 : 206A0010
    move.l -16(a0),d0                                 ; +$0114 : 2028FFF0
    move.l 12(a2),d1                                  ; +$0118 : 222A000C
    cmp.l d1,d0                                       ; +$011C : B081
    bne.w L_009AC8                                    ; +$011E : 6600029C
    move.l #$00000000,d0                              ; +$0122 : 203C00000000
    move.w -12(a0),d0                                 ; +$0128 : 3028FFF4
    tst.l d0                                          ; +$012C : 4A80
    beq.w L_00984A                                    ; +$012E : 6700000E
    andi.w #$FFFD,d0                                  ; +$0132 : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0136 : 0C400001
    bne.w L_009AC8                                    ; +$013A : 66000280
L_00984A:
    movea.l 16(a2),a0                                 ; +$013E : 206A0010
    move.l -8(a0),d0                                  ; +$0142 : 2028FFF8
    cmpi.l #$4649434F,d0                              ; +$0146 : 0C804649434F
    bne.w L_009AC8                                    ; +$014C : 6600026E
    move.l -4(a0),d0                                  ; +$0150 : 2028FFFC
    cmpi.l #$4E382020,d0                              ; +$0154 : 0C804E382020
    bne.w L_009AC8                                    ; +$015A : 66000260
    move.l (a0),d0                                    ; +$015E : 2010
    cmp.l 20(a2),d0                                   ; +$0160 : B0AA0014
    bne.w L_009AC8                                    ; +$0164 : 66000256
    move.l #$00000000,d0                              ; +$0168 : 203C00000000
    move.w 4(a0),d0                                   ; +$016E : 30280004
    cmpi.l #$00000004,d0                              ; +$0172 : 0C8000000004
    bcs.w L_009AC8                                    ; +$0178 : 65000242
    cmpi.l #$00001000,d0                              ; +$017C : 0C8000001000
    bgt.w L_009AC8                                    ; +$0182 : 6E000238
    move.l d0,24(a2)                                  ; +$0186 : 25400018
    move.l 8(a2),d1                                   ; +$018A : 222A0008
    cmp.l d1,d0                                       ; +$018E : B081
    bcs.w L_009AC8                                    ; +$0190 : 6500022A
    move.l #$00000120,d1                              ; +$0194 : 223C00000120
    mulu.w d1,d0                                      ; +$019A : C0C1
    addi.l #$0000000C,d0                              ; +$019C : 06800000000C
    cmp.l 20(a2),d0                                   ; +$01A2 : B0AA0014
    bne.w L_009AC8                                    ; +$01A6 : 66000214
    move.l #$00000000,d0                              ; +$01AA : 203C00000000
    move.w 6(a0),d0                                   ; +$01B0 : 30280006
    cmpi.l #$00000010,d0                              ; +$01B4 : 0C8000000010
    bne.w L_009AC8                                    ; +$01BA : 66000200
    move.l #$00000000,d0                              ; +$01BE : 203C00000000
    move.w 8(a0),d0                                   ; +$01C4 : 30280008
    cmpi.l #$00000010,d0                              ; +$01C8 : 0C8000000010
    bne.w L_009AC8                                    ; +$01CE : 660001EC
    move.l #$00000000,d0                              ; +$01D2 : 203C00000000
    move.w 10(a0),d0                                  ; +$01D8 : 3028000A
    cmpi.l #$00000008,d0                              ; +$01DC : 0C8000000008
    bne.w L_009AC8                                    ; +$01E2 : 660001D8
    move.l 8(a2),d0                                   ; +$01E6 : 202A0008
    subq.l #1,d0                                      ; +$01EA : 5380
    move.l #$00000120,d1                              ; +$01EC : 223C00000120
    mulu.w d1,d0                                      ; +$01F2 : C0C1
    addi.l #$0000000C,d0                              ; +$01F4 : 06800000000C
    move.l 16(a2),d5                                  ; +$01FA : 2A2A0010
    add.l d5,d0                                       ; +$01FE : D085
    bcs.w L_009AC8                                    ; +$0200 : 650001BA
    move.l d0,40(a2)                                  ; +$0204 : 25400028
    addi.l #$0000011F,d0                              ; +$0208 : 06800000011F
    bcs.w L_009AC8                                    ; +$020E : 650001AC
    movea.l d0,a1                                     ; +$0212 : 2240
    movea.l $0004.w,a6                                ; +$0214 : 2C780004
    jsr -534(a6)                                      ; +$0218 : 4EAEFDEA
    tst.l d0                                          ; +$021C : 4A80
    beq.w L_009AC8                                    ; +$021E : 6700019C
    move.l 4(a2),d0                                   ; +$0222 : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$022C : 2A08
    cmpi.l #$00000018,d5                              ; +$022E : 0C8500000018
    bls.w L_009AC8                                    ; +$0234 : 63000186
    move.l d5,d0                                      ; +$0238 : 2005
    andi.l #$00000001,d0                              ; +$023A : 028000000001
    bne.w L_009AC8                                    ; +$0240 : 6600017A
    move.l d5,28(a2)                                  ; +$0244 : 2545001C
    movea.l d5,a1                                     ; +$0248 : 2245
    movea.l $0004.w,a6                                ; +$024A : 2C780004
    jsr -534(a6)                                      ; +$024E : 4EAEFDEA
    tst.l d0                                          ; +$0252 : 4A80
    beq.w L_009AC8                                    ; +$0254 : 67000166
    move.l 28(a2),d0                                  ; +$0258 : 202A001C
    subi.l #$00000018,d0                              ; +$025C : 048000000018
    movea.l d0,a1                                     ; +$0262 : 2240
    movea.l $0004.w,a6                                ; +$0264 : 2C780004
    jsr -534(a6)                                      ; +$0268 : 4EAEFDEA
    tst.l d0                                          ; +$026C : 4A80
    beq.w L_009AC8                                    ; +$026E : 6700014C
    movea.l 28(a2),a0                                 ; +$0272 : 206A001C
    move.l -20(a0),d4                                 ; +$0276 : 2828FFEC
    cmpi.l #$00000110,d4                              ; +$027A : 0C8400000110
    bcs.w L_009AC8                                    ; +$0280 : 6500013A
    subi.l #$00000010,d4                              ; +$0284 : 048400000010
    move.l d4,32(a2)                                  ; +$028A : 25440020
    move.l 28(a2),d0                                  ; +$028E : 202A001C
    add.l d4,d0                                       ; +$0292 : D084
    bcs.w L_009AC8                                    ; +$0294 : 65000126
    subq.l #1,d0                                      ; +$0298 : 5380
    movea.l d0,a1                                     ; +$029A : 2240
    movea.l $0004.w,a6                                ; +$029C : 2C780004
    jsr -534(a6)                                      ; +$02A0 : 4EAEFDEA
    tst.l d0                                          ; +$02A4 : 4A80
    beq.w L_009AC8                                    ; +$02A6 : 67000114
    movea.l 28(a2),a0                                 ; +$02AA : 206A001C
    move.l -16(a0),d0                                 ; +$02AE : 2028FFF0
    move.l 4(a2),d1                                   ; +$02B2 : 222A0004
    cmp.l d1,d0                                       ; +$02B6 : B081
    bne.w L_009AC8                                    ; +$02B8 : 66000102
    move.l #$00000000,d0                              ; +$02BC : 203C00000000
    move.w -12(a0),d0                                 ; +$02C2 : 3028FFF4
    tst.l d0                                          ; +$02C6 : 4A80
    beq.w L_0099E4                                    ; +$02C8 : 6700000E
    andi.w #$FFFD,d0                                  ; +$02CC : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$02D0 : 0C400001
    bne.w L_009AC8                                    ; +$02D4 : 660000E6
L_0099E4:
    move.l 32(a2),d0                                  ; +$02D8 : 202A0020
    subi.l #$00000100,d0                              ; +$02DC : 048000000100
    move.l (a2),d1                                    ; +$02E2 : 2212
    cmp.l d1,d0                                       ; +$02E4 : B081
    bcs.w L_009AC8                                    ; +$02E6 : 650000D4
    move.l 28(a2),d0                                  ; +$02EA : 202A001C
    add.l d1,d0                                       ; +$02EE : D081
    bcs.w L_009AC8                                    ; +$02F0 : 650000CA
    move.l d0,36(a2)                                  ; +$02F4 : 25400024
    movea.l d0,a1                                     ; +$02F8 : 2240
    movea.l $0004.w,a6                                ; +$02FA : 2C780004
    jsr -534(a6)                                      ; +$02FE : 4EAEFDEA
    tst.l d0                                          ; +$0302 : 4A80
    beq.w L_009AC8                                    ; +$0304 : 670000B6
    move.l 36(a2),d0                                  ; +$0308 : 202A0024
    addi.l #$000000FF,d0                              ; +$030C : 0680000000FF
    bcs.w L_009AC8                                    ; +$0312 : 650000A8
    movea.l d0,a1                                     ; +$0316 : 2240
    movea.l $0004.w,a6                                ; +$0318 : 2C780004
    jsr -534(a6)                                      ; +$031C : 4EAEFDEA
    tst.l d0                                          ; +$0320 : 4A80
    beq.w L_009AC8                                    ; +$0322 : 67000098
    movea.l 36(a2),a0                                 ; +$0326 : 206A0024
    movea.l 40(a2),a1                                 ; +$032A : 226A0028
    move.l #$00000010,d6                              ; +$032E : 2C3C00000010
L_009A40:
    move.w #$0000,(a1)                                ; +$0334 : 32BC0000
    move.l #$00000000,2(a1)                           ; +$0338 : 237C000000000002
    move.l #$00000000,6(a1)                           ; +$0340 : 237C000000000006
    move.l #$00000000,10(a1)                          ; +$0348 : 237C00000000000A
    move.l #$00000000,14(a1)                          ; +$0350 : 237C00000000000E
    move.l #$00000000,d7                              ; +$0358 : 2E3C00000000
    move.w #$8000,d1                                  ; +$035E : 323C8000
    move.l #$00000010,d2                              ; +$0362 : 243C00000010
L_009A74:
    move.l #$00000000,d4                              ; +$0368 : 283C00000000
    move.b (a0)+,d4                                   ; +$036E : 1818
    tst.b d4                                          ; +$0370 : 4A04
    bne.w L_009A88                                    ; +$0372 : 66000008
    or.w d1,d7                                        ; +$0376 : 8E41
    bra.w L_009AAE                                    ; +$0378 : 60000028
L_009A88:
    movea.l a1,a4                                     ; +$037C : 2849
    addq.l #2,a4                                      ; +$037E : 548C
    move.l #$00000008,d5                              ; +$0380 : 2A3C00000008
L_009A92:
    move.l d4,d0                                      ; +$0386 : 2004
    andi.w #$0001,d0                                  ; +$0388 : 02400001
    tst.w d0                                          ; +$038C : 4A40
    beq.w L_009AA4                                    ; +$038E : 67000008
    move.w (a4),d0                                    ; +$0392 : 3014
    or.w d1,d0                                        ; +$0394 : 8041
    move.w d0,(a4)                                    ; +$0396 : 3880
L_009AA4:
    lsr.w #1,d4                                       ; +$0398 : E24C
    addq.l #2,a4                                      ; +$039A : 548C
    subq.l #1,d5                                      ; +$039C : 5385
    bne.w L_009A92                                    ; +$039E : 6600FFE6
L_009AAE:
    lsr.w #1,d1                                       ; +$03A2 : E249
    subq.l #1,d2                                      ; +$03A4 : 5382
    bne.w L_009A74                                    ; +$03A6 : 6600FFC0
    move.w d7,(a1)                                    ; +$03AA : 3287
    lea 18(a1),a1                                     ; +$03AC : 43E90012
    subq.l #1,d6                                      ; +$03B0 : 5386
    bne.w L_009A40                                    ; +$03B2 : 6600FF80
    move.l #$00000001,d3                              ; +$03B6 : 263C00000001
L_009AC8:
    lea 96(a7),a7                                     ; +$03BC : 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$03C0 : 4CDF77F7
    moveq #0,d2                                       ; +$03C4 : 7400
    rts                                               ; +$03C6 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 64 : aga f chip bank create --------
Entry_64:
Aga_F_Chip_Bank_Create:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -64(a7),a7                                    ; +$0004 : 4FEFFFC0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l #$00000000,d3                              ; +$0012 : 263C00000000
    move.l 4(a2),d0                                   ; +$0018 : 202A0004
    cmpi.l #$00000005,d0                              ; +$001C : 0C8000000005
    bcs.w L_009C2E                                    ; +$0022 : 65000132
    cmpi.l #$0000FFFF,d0                              ; +$0026 : 0C800000FFFF
    bhi.w L_009C2E                                    ; +$002C : 62000128
    move.l (a2),d0                                    ; +$0030 : 2012
    cmpi.l #$00000004,d0                              ; +$0032 : 0C8000000004
    bcs.w L_009C2E                                    ; +$0038 : 6500011C
    cmpi.l #$00001000,d0                              ; +$003C : 0C8000001000
    bhi.w L_009C2E                                    ; +$0042 : 62000112
    move.l (a2),d0                                    ; +$0046 : 2012
    move.l #$00000121,d1                              ; +$0048 : 223C00000121
    mulu.w d1,d0                                      ; +$004E : C0C1
    addi.l #$0000000C,d0                              ; +$0050 : 06800000000C
    move.l d0,8(a2)                                   ; +$0056 : 25400008
    move.l 4(a2),d0                                   ; +$005A : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0064 : 2008
    tst.l d0                                          ; +$0066 : 4A80
    bne.w L_009C2E                                    ; +$0068 : 660000EC
    move.l 4(a2),d0                                   ; +$006C : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0076 : 2008
    tst.l d0                                          ; +$0078 : 4A80
    bne.w L_009C2E                                    ; +$007A : 660000DA
    move.l 4(a2),d0                                   ; +$007E : 202A0004
    move.l #$00000003,d1                              ; +$0082 : 223C00000003
    move.l 8(a2),d2                                   ; +$0088 : 242A0008
    lea L_009C3A(pc),a0                               ; +$008C : 41FA00D4
    dc.b $FE,$11,$F7,$00,$03,$30
    tst.l d0                                          ; +$0096 : 4A80
    beq.w L_009C2E                                    ; +$0098 : 670000BC
    move.l d0,12(a2)                                  ; +$009C : 2540000C
    cmpi.l #$00000018,d0                              ; +$00A0 : 0C8000000018
    bls.w L_009C1E                                    ; +$00A6 : 6300009E
    move.l d0,d1                                      ; +$00AA : 2200
    andi.l #$00000001,d1                              ; +$00AC : 028100000001
    bne.w L_009C1E                                    ; +$00B2 : 66000092
    move.l 12(a2),d0                                  ; +$00B6 : 202A000C
    move.l 8(a2),d1                                   ; +$00BA : 222A0008
    add.l d1,d0                                       ; +$00BE : D081
    bcs.w L_009C1E                                    ; +$00C0 : 65000084
    subq.l #1,d0                                      ; +$00C4 : 5380
    move.l d0,16(a2)                                  ; +$00C6 : 25400010
    move.l 12(a2),d0                                  ; +$00CA : 202A000C
    movea.l d0,a1                                     ; +$00CE : 2240
    movea.l $0004.w,a6                                ; +$00D0 : 2C780004
    jsr -534(a6)                                      ; +$00D4 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$00D8 : 028000000002
    beq.w L_009C1E                                    ; +$00DE : 67000066
    move.l 16(a2),d0                                  ; +$00E2 : 202A0010
    movea.l d0,a1                                     ; +$00E6 : 2240
    movea.l $0004.w,a6                                ; +$00E8 : 2C780004
    jsr -534(a6)                                      ; +$00EC : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$00F0 : 028000000002
    beq.w L_009C1E                                    ; +$00F6 : 6700004E
    movea.l 12(a2),a1                                 ; +$00FA : 226A000C
    move.l 8(a2),d0                                   ; +$00FE : 202A0008
    move.l d0,(a1)+                                   ; +$0102 : 22C0
    move.l (a2),d0                                    ; +$0104 : 2012
    move.w d0,(a1)+                                   ; +$0106 : 32C0
    move.w #$0010,(a1)+                               ; +$0108 : 32FC0010
    move.w #$0010,(a1)+                               ; +$010C : 32FC0010
    move.w #$0008,(a1)+                               ; +$0110 : 32FC0008
    move.l (a2),d6                                    ; +$0114 : 2C12
    move.l #$00000048,d1                              ; +$0116 : 223C00000048
    mulu.w d1,d6                                      ; +$011C : CCC1
L_009BF6:
    move.l #$00000000,(a1)+                           ; +$011E : 22FC00000000
    subq.l #1,d6                                      ; +$0124 : 5386
    bne.w L_009BF6                                    ; +$0126 : 6600FFF6
    move.l (a2),d6                                    ; +$012A : 2C12
L_009C04:
    move.b #$00,(a1)+                                 ; +$012C : 12FC0000
    subq.l #1,d6                                      ; +$0130 : 5386
    bne.w L_009C04                                    ; +$0132 : 6600FFF8
    dc.b $FE,$11,$F7,$00,$03,$33
    move.l #$00000001,d3                              ; +$013C : 263C00000001
    bra.w L_009C2E                                    ; +$0142 : 60000012
L_009C1E:
    move.l 4(a2),d0                                   ; +$0146 : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$20
    move.l #$00000000,d3                              ; +$0150 : 263C00000000
L_009C2E:
    lea 64(a7),a7                                     ; +$0156 : 4FEF0040
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$015A : 4CDF77F7
    moveq #0,d2                                       ; +$015E : 7400
    rts                                               ; +$0160 : 4E75
L_009C3A:
    dc.b "FICHIP8 "
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 65 : aga f chip stage --------
Entry_65:
Aga_F_Chip_Stage:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -96(a7),a7                                    ; +$0004 : 4FEFFFA0
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l #$00000000,d3                              ; +$0018 : 263C00000000
    move.l 4(a2),d0                                   ; +$001E : 202A0004
    cmpi.l #$00000005,d0                              ; +$0022 : 0C8000000005
    bcs.w L_00A102                                    ; +$0028 : 65000492
    cmpi.l #$0000FFFF,d0                              ; +$002C : 0C800000FFFF
    bhi.w L_00A102                                    ; +$0032 : 62000488
    move.l 8(a2),d0                                   ; +$0036 : 202A0008
    cmpi.l #$00000005,d0                              ; +$003A : 0C8000000005
    bcs.w L_00A102                                    ; +$0040 : 6500047A
    cmpi.l #$0000FFFF,d0                              ; +$0044 : 0C800000FFFF
    bhi.w L_00A102                                    ; +$004A : 62000470
    move.l 8(a2),d0                                   ; +$004E : 202A0008
    move.l 4(a2),d1                                   ; +$0052 : 222A0004
    cmp.l d1,d0                                       ; +$0056 : B081
    beq.w L_00A102                                    ; +$0058 : 67000462
    move.l (a2),d0                                    ; +$005C : 2012
    tst.l d0                                          ; +$005E : 4A80
    ble.w L_00A102                                    ; +$0060 : 6F00045A
    cmpi.l #$00001000,d0                              ; +$0064 : 0C8000001000
    bhi.w L_00A102                                    ; +$006A : 62000450
    move.l 8(a2),d0                                   ; +$006E : 202A0008
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$0078 : 2A08
    cmpi.l #$00000018,d5                              ; +$007A : 0C8500000018
    bls.w L_00A102                                    ; +$0080 : 6300043A
    move.l d5,d0                                      ; +$0084 : 2005
    andi.l #$00000001,d0                              ; +$0086 : 028000000001
    bne.w L_00A102                                    ; +$008C : 6600042E
    move.l d5,12(a2)                                  ; +$0090 : 2545000C
    movea.l d5,a1                                     ; +$0094 : 2245
    movea.l $0004.w,a6                                ; +$0096 : 2C780004
    jsr -534(a6)                                      ; +$009A : 4EAEFDEA
    tst.l d0                                          ; +$009E : 4A80
    beq.w L_00A102                                    ; +$00A0 : 6700041A
    move.l 12(a2),d0                                  ; +$00A4 : 202A000C
    subi.l #$00000018,d0                              ; +$00A8 : 048000000018
    movea.l d0,a1                                     ; +$00AE : 2240
    movea.l $0004.w,a6                                ; +$00B0 : 2C780004
    jsr -534(a6)                                      ; +$00B4 : 4EAEFDEA
    tst.l d0                                          ; +$00B8 : 4A80
    beq.w L_00A102                                    ; +$00BA : 67000400
    movea.l 12(a2),a0                                 ; +$00BE : 206A000C
    move.l -20(a0),d4                                 ; +$00C2 : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$00C6 : 0C840000001C
    bcs.w L_00A102                                    ; +$00CC : 650003EE
    subi.l #$00000010,d4                              ; +$00D0 : 048400000010
    cmpi.l #$0012100C,d4                              ; +$00D6 : 0C840012100C
    bhi.w L_00A102                                    ; +$00DC : 620003DE
    move.l d4,16(a2)                                  ; +$00E0 : 25440010
    move.l 12(a2),d0                                  ; +$00E4 : 202A000C
    add.l d4,d0                                       ; +$00E8 : D084
    bcs.w L_00A102                                    ; +$00EA : 650003D0
    move.l d0,20(a2)                                  ; +$00EE : 25400014
    subq.l #1,d0                                      ; +$00F2 : 5380
    movea.l d0,a1                                     ; +$00F4 : 2240
    movea.l $0004.w,a6                                ; +$00F6 : 2C780004
    jsr -534(a6)                                      ; +$00FA : 4EAEFDEA
    tst.l d0                                          ; +$00FE : 4A80
    beq.w L_00A102                                    ; +$0100 : 670003BA
    movea.l 12(a2),a0                                 ; +$0104 : 206A000C
    move.l -16(a0),d0                                 ; +$0108 : 2028FFF0
    move.l 8(a2),d1                                   ; +$010C : 222A0008
    cmp.l d1,d0                                       ; +$0110 : B081
    bne.w L_00A102                                    ; +$0112 : 660003A8
    move.l #$00000000,d0                              ; +$0116 : 203C00000000
    move.w -12(a0),d0                                 ; +$011C : 3028FFF4
    tst.l d0                                          ; +$0120 : 4A80
    beq.w L_009D78                                    ; +$0122 : 6700000E
    andi.w #$FFFD,d0                                  ; +$0126 : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$012A : 0C400001
    bne.w L_00A102                                    ; +$012E : 6600038C
L_009D78:
    movea.l 12(a2),a0                                 ; +$0132 : 206A000C
    move.l -8(a0),d0                                  ; +$0136 : 2028FFF8
    cmpi.l #$4649434F,d0                              ; +$013A : 0C804649434F
    bne.w L_00A102                                    ; +$0140 : 6600037A
    move.l -4(a0),d0                                  ; +$0144 : 2028FFFC
    cmpi.l #$4E382020,d0                              ; +$0148 : 0C804E382020
    bne.w L_00A102                                    ; +$014E : 6600036C
    move.l (a0),d0                                    ; +$0152 : 2010
    cmp.l 16(a2),d0                                   ; +$0154 : B0AA0010
    bne.w L_00A102                                    ; +$0158 : 66000362
    move.l #$00000000,d0                              ; +$015C : 203C00000000
    move.w 4(a0),d0                                   ; +$0162 : 30280004
    cmpi.l #$00000004,d0                              ; +$0166 : 0C8000000004
    bcs.w L_00A102                                    ; +$016C : 6500034E
    cmpi.l #$00001000,d0                              ; +$0170 : 0C8000001000
    bhi.w L_00A102                                    ; +$0176 : 62000344
    move.l d0,24(a2)                                  ; +$017A : 25400018
    move.l (a2),d1                                    ; +$017E : 2212
    cmp.l d1,d0                                       ; +$0180 : B081
    bcs.w L_00A102                                    ; +$0182 : 65000338
    move.l #$00000120,d1                              ; +$0186 : 223C00000120
    mulu.w d1,d0                                      ; +$018C : C0C1
    addi.l #$0000000C,d0                              ; +$018E : 06800000000C
    cmp.l 16(a2),d0                                   ; +$0194 : B0AA0010
    bne.w L_00A102                                    ; +$0198 : 66000322
    move.l #$00000000,d0                              ; +$019C : 203C00000000
    move.w 6(a0),d0                                   ; +$01A2 : 30280006
    cmpi.l #$00000010,d0                              ; +$01A6 : 0C8000000010
    bne.w L_00A102                                    ; +$01AC : 6600030E
    move.l #$00000000,d0                              ; +$01B0 : 203C00000000
    move.w 8(a0),d0                                   ; +$01B6 : 30280008
    cmpi.l #$00000010,d0                              ; +$01BA : 0C8000000010
    bne.w L_00A102                                    ; +$01C0 : 660002FA
    move.l #$00000000,d0                              ; +$01C4 : 203C00000000
    move.w 10(a0),d0                                  ; +$01CA : 3028000A
    cmpi.l #$00000008,d0                              ; +$01CE : 0C8000000008
    bne.w L_00A102                                    ; +$01D4 : 660002E6
    move.l 4(a2),d0                                   ; +$01D8 : 202A0004
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$01E2 : 2A08
    cmpi.l #$00000018,d5                              ; +$01E4 : 0C8500000018
    bls.w L_00A102                                    ; +$01EA : 630002D0
    move.l d5,d0                                      ; +$01EE : 2005
    andi.l #$00000001,d0                              ; +$01F0 : 028000000001
    bne.w L_00A102                                    ; +$01F6 : 660002C4
    move.l d5,28(a2)                                  ; +$01FA : 2545001C
    movea.l d5,a1                                     ; +$01FE : 2245
    movea.l $0004.w,a6                                ; +$0200 : 2C780004
    jsr -534(a6)                                      ; +$0204 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0208 : 028000000002
    tst.l d0                                          ; +$020E : 4A80
    beq.w L_00A102                                    ; +$0210 : 670002AA
    move.l 28(a2),d0                                  ; +$0214 : 202A001C
    subi.l #$00000018,d0                              ; +$0218 : 048000000018
    movea.l d0,a1                                     ; +$021E : 2240
    movea.l $0004.w,a6                                ; +$0220 : 2C780004
    jsr -534(a6)                                      ; +$0224 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0228 : 028000000002
    tst.l d0                                          ; +$022E : 4A80
    beq.w L_00A102                                    ; +$0230 : 6700028A
    movea.l 28(a2),a0                                 ; +$0234 : 206A001C
    move.l -20(a0),d4                                 ; +$0238 : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$023C : 0C840000001C
    bcs.w L_00A102                                    ; +$0242 : 65000278
    subi.l #$00000010,d4                              ; +$0246 : 048400000010
    cmpi.l #$0012100C,d4                              ; +$024C : 0C840012100C
    bhi.w L_00A102                                    ; +$0252 : 62000268
    move.l d4,32(a2)                                  ; +$0256 : 25440020
    move.l 28(a2),d0                                  ; +$025A : 202A001C
    add.l d4,d0                                       ; +$025E : D084
    bcs.w L_00A102                                    ; +$0260 : 6500025A
    move.l d0,36(a2)                                  ; +$0264 : 25400024
    subq.l #1,d0                                      ; +$0268 : 5380
    movea.l d0,a1                                     ; +$026A : 2240
    movea.l $0004.w,a6                                ; +$026C : 2C780004
    jsr -534(a6)                                      ; +$0270 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0274 : 028000000002
    tst.l d0                                          ; +$027A : 4A80
    beq.w L_00A102                                    ; +$027C : 6700023E
    movea.l 28(a2),a0                                 ; +$0280 : 206A001C
    move.l -16(a0),d0                                 ; +$0284 : 2028FFF0
    move.l 4(a2),d1                                   ; +$0288 : 222A0004
    cmp.l d1,d0                                       ; +$028C : B081
    bne.w L_00A102                                    ; +$028E : 6600022C
    move.l #$00000000,d0                              ; +$0292 : 203C00000000
    move.w -12(a0),d0                                 ; +$0298 : 3028FFF4
    tst.l d0                                          ; +$029C : 4A80
    beq.w L_009EF4                                    ; +$029E : 6700000E
    andi.w #$FFFD,d0                                  ; +$02A2 : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$02A6 : 0C400001
    bne.w L_00A102                                    ; +$02AA : 66000210
L_009EF4:
    movea.l 28(a2),a0                                 ; +$02AE : 206A001C
    move.l -8(a0),d0                                  ; +$02B2 : 2028FFF8
    cmpi.l #$46494348,d0                              ; +$02B6 : 0C8046494348
    bne.w L_00A102                                    ; +$02BC : 660001FE
    move.l -4(a0),d0                                  ; +$02C0 : 2028FFFC
    cmpi.l #$49503820,d0                              ; +$02C4 : 0C8049503820
    bne.w L_00A102                                    ; +$02CA : 660001F0
    move.l (a0),d0                                    ; +$02CE : 2010
    cmp.l 32(a2),d0                                   ; +$02D0 : B0AA0020
    bne.w L_00A102                                    ; +$02D4 : 660001E6
    move.l #$00000000,d0                              ; +$02D8 : 203C00000000
    move.w 4(a0),d0                                   ; +$02DE : 30280004
    cmpi.l #$00000004,d0                              ; +$02E2 : 0C8000000004
    bcs.w L_00A102                                    ; +$02E8 : 650001D2
    cmpi.l #$00001000,d0                              ; +$02EC : 0C8000001000
    bhi.w L_00A102                                    ; +$02F2 : 620001C8
    move.l d0,40(a2)                                  ; +$02F6 : 25400028
    move.l (a2),d1                                    ; +$02FA : 2212
    cmp.l d1,d0                                       ; +$02FC : B081
    bcs.w L_00A102                                    ; +$02FE : 650001BC
    move.l #$00000121,d1                              ; +$0302 : 223C00000121
    mulu.w d1,d0                                      ; +$0308 : C0C1
    addi.l #$0000000C,d0                              ; +$030A : 06800000000C
    cmp.l 32(a2),d0                                   ; +$0310 : B0AA0020
    bne.w L_00A102                                    ; +$0314 : 660001A6
    move.l #$00000000,d0                              ; +$0318 : 203C00000000
    move.w 6(a0),d0                                   ; +$031E : 30280006
    cmpi.l #$00000010,d0                              ; +$0322 : 0C8000000010
    bne.w L_00A102                                    ; +$0328 : 66000192
    move.l #$00000000,d0                              ; +$032C : 203C00000000
    move.w 8(a0),d0                                   ; +$0332 : 30280008
    cmpi.l #$00000010,d0                              ; +$0336 : 0C8000000010
    bne.w L_00A102                                    ; +$033C : 6600017E
    move.l #$00000000,d0                              ; +$0340 : 203C00000000
    move.w 10(a0),d0                                  ; +$0346 : 3028000A
    cmpi.l #$00000008,d0                              ; +$034A : 0C8000000008
    bne.w L_00A102                                    ; +$0350 : 6600016A
    move.l 12(a2),d0                                  ; +$0354 : 202A000C
    cmp.l 36(a2),d0                                   ; +$0358 : B0AA0024
    bcc.w L_009FB6                                    ; +$035C : 64000012
    move.l 28(a2),d0                                  ; +$0360 : 202A001C
    cmp.l 20(a2),d0                                   ; +$0364 : B0AA0014
    bcc.w L_009FB6                                    ; +$0368 : 64000006
    bra.w L_00A102                                    ; +$036C : 6000014E
L_009FB6:
    move.l (a2),d0                                    ; +$0370 : 2012
    subq.l #1,d0                                      ; +$0372 : 5380
    move.l #$00000120,d1                              ; +$0374 : 223C00000120
    mulu.w d1,d0                                      ; +$037A : C0C1
    addi.l #$0000000C,d0                              ; +$037C : 06800000000C
    move.l 12(a2),d5                                  ; +$0382 : 2A2A000C
    add.l d5,d0                                       ; +$0386 : D085
    bcs.w L_00A102                                    ; +$0388 : 65000132
    move.l d0,44(a2)                                  ; +$038C : 2540002C
    addi.l #$0000011F,d0                              ; +$0390 : 06800000011F
    bcs.w L_00A102                                    ; +$0396 : 65000124
    movea.l d0,a1                                     ; +$039A : 2240
    movea.l $0004.w,a6                                ; +$039C : 2C780004
    jsr -534(a6)                                      ; +$03A0 : 4EAEFDEA
    tst.l d0                                          ; +$03A4 : 4A80
    beq.w L_00A102                                    ; +$03A6 : 67000114
    move.l (a2),d0                                    ; +$03AA : 2012
    subq.l #1,d0                                      ; +$03AC : 5380
    move.l #$00000120,d1                              ; +$03AE : 223C00000120
    mulu.w d1,d0                                      ; +$03B4 : C0C1
    addi.l #$0000000C,d0                              ; +$03B6 : 06800000000C
    move.l 28(a2),d5                                  ; +$03BC : 2A2A001C
    add.l d5,d0                                       ; +$03C0 : D085
    bcs.w L_00A102                                    ; +$03C2 : 650000F8
    move.l d0,48(a2)                                  ; +$03C6 : 25400030
    addi.l #$0000011F,d0                              ; +$03CA : 06800000011F
    bcs.w L_00A102                                    ; +$03D0 : 650000EA
    movea.l d0,a1                                     ; +$03D4 : 2240
    movea.l $0004.w,a6                                ; +$03D6 : 2C780004
    jsr -534(a6)                                      ; +$03DA : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$03DE : 028000000002
    tst.l d0                                          ; +$03E4 : 4A80
    beq.w L_00A102                                    ; +$03E6 : 670000D4
    move.l 40(a2),d0                                  ; +$03EA : 202A0028
    move.l #$00000120,d1                              ; +$03EE : 223C00000120
    mulu.w d1,d0                                      ; +$03F4 : C0C1
    addi.l #$0000000C,d0                              ; +$03F6 : 06800000000C
    move.l (a2),d1                                    ; +$03FC : 2212
    subq.l #1,d1                                      ; +$03FE : 5381
    add.l d1,d0                                       ; +$0400 : D081
    move.l 28(a2),d5                                  ; +$0402 : 2A2A001C
    add.l d5,d0                                       ; +$0406 : D085
    bcs.w L_00A102                                    ; +$0408 : 650000B2
    move.l d0,52(a2)                                  ; +$040C : 25400034
    movea.l d0,a1                                     ; +$0410 : 2240
    movea.l $0004.w,a6                                ; +$0412 : 2C780004
    jsr -534(a6)                                      ; +$0416 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$041A : 028000000002
    tst.l d0                                          ; +$0420 : 4A80
    beq.w L_00A102                                    ; +$0422 : 67000098
    movea.l 52(a2),a0                                 ; +$0426 : 206A0034
    move.l #$00000000,d0                              ; +$042A : 203C00000000
    move.b (a0),d0                                    ; +$0430 : 1010
    cmpi.l #$00000001,d0                              ; +$0432 : 0C8000000001
    bhi.w L_00A102                                    ; +$0438 : 62000082
    movea.l 44(a2),a0                                 ; +$043C : 206A002C
    move.l #$00000010,d6                              ; +$0440 : 2C3C00000010
L_00A08C:
    move.w (a0)+,d4                                   ; +$0446 : 3818
    move.l #$00000000,d7                              ; +$0448 : 2E3C00000000
    move.l #$00000008,d5                              ; +$044E : 2A3C00000008
L_00A09A:
    or.w (a0)+,d7                                     ; +$0454 : 8E58
    subq.l #1,d5                                      ; +$0456 : 5385
    bne.w L_00A09A                                    ; +$0458 : 6600FFFA
    not.w d7                                          ; +$045C : 4647
    cmp.w d4,d7                                       ; +$045E : BE44
    bne.w L_00A102                                    ; +$0460 : 6600005A
    subq.l #1,d6                                      ; +$0464 : 5386
    bne.w L_00A08C                                    ; +$0466 : 6600FFDE
    movea.l 52(a2),a4                                 ; +$046A : 286A0034
    move.b #$00,(a4)                                  ; +$046E : 18BC0000
    movea.l 44(a2),a0                                 ; +$0472 : 206A002C
    movea.l 48(a2),a1                                 ; +$0476 : 226A0030
    move.l #$00000000,d0                              ; +$047A : 203C00000000
    move.l #$00000010,d6                              ; +$0480 : 2C3C00000010
L_00A0CC:
    movea.l a1,a4                                     ; +$0486 : 2849
    adda.l d0,a4                                      ; +$0488 : D9C0
    move.w (a0)+,d7                                   ; +$048A : 3E18
    not.w d7                                          ; +$048C : 4647
    move.w d7,(a4)                                    ; +$048E : 3887
    lea 32(a4),a4                                     ; +$0490 : 49EC0020
    move.l #$00000008,d5                              ; +$0494 : 2A3C00000008
L_00A0E0:
    move.w (a0)+,(a4)                                 ; +$049A : 3898
    lea 32(a4),a4                                     ; +$049C : 49EC0020
    subq.l #1,d5                                      ; +$04A0 : 5385
    bne.w L_00A0E0                                    ; +$04A2 : 6600FFF6
    addq.l #2,d0                                      ; +$04A6 : 5480
    subq.l #1,d6                                      ; +$04A8 : 5386
    bne.w L_00A0CC                                    ; +$04AA : 6600FFDA
    movea.l 52(a2),a4                                 ; +$04AE : 286A0034
    move.b #$01,(a4)                                  ; +$04B2 : 18BC0001
    move.l #$00000001,d3                              ; +$04B6 : 263C00000001
L_00A102:
    lea 96(a7),a7                                     ; +$04BC : 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$04C0 : 4CDF77F7
    moveq #0,d2                                       ; +$04C4 : 7400
    rts                                               ; +$04C6 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 66 : aga f icon capture --------
Entry_66:
Aga_F_Icon_Capture:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -128(a7),a7                                   ; +$0004 : 4FEFFF80
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l (a3)+,d7                                   ; +$000C : 2E1B
    move.l d7,4(a2)                                   ; +$000E : 25470004
    move.l (a3)+,d7                                   ; +$0012 : 2E1B
    move.l d7,8(a2)                                   ; +$0014 : 25470008
    move.l (a3)+,d7                                   ; +$0018 : 2E1B
    move.l d7,12(a2)                                  ; +$001A : 2547000C
    move.l #$00000000,d3                              ; +$001E : 263C00000000
    move.l 12(a2),d0                                  ; +$0024 : 202A000C
    cmpi.l #$00000005,d0                              ; +$0028 : 0C8000000005
    bcs.w L_00A630                                    ; +$002E : 650004EE
    cmpi.l #$0000FFFF,d0                              ; +$0032 : 0C800000FFFF
    bhi.w L_00A630                                    ; +$0038 : 620004E4
    move.l 8(a2),d0                                   ; +$003C : 202A0008
    cmpi.l #$00000001,d0                              ; +$0040 : 0C8000000001
    bcs.w L_00A630                                    ; +$0046 : 650004D6
    cmpi.l #$00001000,d0                              ; +$004A : 0C8000001000
    bhi.w L_00A630                                    ; +$0050 : 620004CC
    move.l 4(a2),d0                                   ; +$0054 : 202A0004
    tst.l d0                                          ; +$0058 : 4A80
    bmi.w L_00A630                                    ; +$005A : 6B0004C2
    cmpi.l #$00001000,d0                              ; +$005E : 0C8000001000
    bhi.w L_00A630                                    ; +$0064 : 620004B8
    move.l (a2),d0                                    ; +$0068 : 2012
    tst.l d0                                          ; +$006A : 4A80
    bmi.w L_00A630                                    ; +$006C : 6B0004B0
    cmpi.l #$00001000,d0                              ; +$0070 : 0C8000001000
    bhi.w L_00A630                                    ; +$0076 : 620004A6
    move.l 12(a2),d0                                  ; +$007A : 202A000C
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d5                                      ; +$0084 : 2A08
    cmpi.l #$00000018,d5                              ; +$0086 : 0C8500000018
    bls.w L_00A630                                    ; +$008C : 63000490
    move.l d5,d0                                      ; +$0090 : 2005
    andi.l #$00000001,d0                              ; +$0092 : 028000000001
    bne.w L_00A630                                    ; +$0098 : 66000484
    move.l d5,16(a2)                                  ; +$009C : 25450010
    movea.l d5,a1                                     ; +$00A0 : 2245
    movea.l $0004.w,a6                                ; +$00A2 : 2C780004
    jsr -534(a6)                                      ; +$00A6 : 4EAEFDEA
    tst.l d0                                          ; +$00AA : 4A80
    beq.w L_00A630                                    ; +$00AC : 67000470
    move.l 16(a2),d0                                  ; +$00B0 : 202A0010
    subi.l #$00000018,d0                              ; +$00B4 : 048000000018
    movea.l d0,a1                                     ; +$00BA : 2240
    movea.l $0004.w,a6                                ; +$00BC : 2C780004
    jsr -534(a6)                                      ; +$00C0 : 4EAEFDEA
    tst.l d0                                          ; +$00C4 : 4A80
    beq.w L_00A630                                    ; +$00C6 : 67000456
    movea.l 16(a2),a0                                 ; +$00CA : 206A0010
    move.l -20(a0),d4                                 ; +$00CE : 2828FFEC
    cmpi.l #$0000001C,d4                              ; +$00D2 : 0C840000001C
    bcs.w L_00A630                                    ; +$00D8 : 65000444
    subi.l #$00000010,d4                              ; +$00DC : 048400000010
    cmpi.l #$0012000C,d4                              ; +$00E2 : 0C840012000C
    bhi.w L_00A630                                    ; +$00E8 : 62000434
    move.l d4,20(a2)                                  ; +$00EC : 25440014
    move.l 16(a2),d0                                  ; +$00F0 : 202A0010
    add.l d4,d0                                       ; +$00F4 : D084
    bcs.w L_00A630                                    ; +$00F6 : 65000426
    subq.l #1,d0                                      ; +$00FA : 5380
    movea.l d0,a1                                     ; +$00FC : 2240
    movea.l $0004.w,a6                                ; +$00FE : 2C780004
    jsr -534(a6)                                      ; +$0102 : 4EAEFDEA
    tst.l d0                                          ; +$0106 : 4A80
    beq.w L_00A630                                    ; +$0108 : 67000414
    movea.l 16(a2),a0                                 ; +$010C : 206A0010
    move.l -16(a0),d0                                 ; +$0110 : 2028FFF0
    move.l 12(a2),d1                                  ; +$0114 : 222A000C
    cmp.l d1,d0                                       ; +$0118 : B081
    bne.w L_00A630                                    ; +$011A : 66000402
    move.l #$00000000,d0                              ; +$011E : 203C00000000
    move.w -12(a0),d0                                 ; +$0124 : 3028FFF4
    tst.l d0                                          ; +$0128 : 4A80
    beq.w L_00A24C                                    ; +$012A : 6700000E
    andi.w #$FFFD,d0                                  ; +$012E : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0132 : 0C400001
    bne.w L_00A630                                    ; +$0136 : 660003E6
L_00A24C:
    move.l -8(a0),d0                                  ; +$013A : 2028FFF8
    cmpi.l #$4649434F,d0                              ; +$013E : 0C804649434F
    bne.w L_00A630                                    ; +$0144 : 660003D8
    move.l -4(a0),d0                                  ; +$0148 : 2028FFFC
    cmpi.l #$4E382020,d0                              ; +$014C : 0C804E382020
    bne.w L_00A630                                    ; +$0152 : 660003CA
    move.l (a0),d0                                    ; +$0156 : 2010
    cmp.l 20(a2),d0                                   ; +$0158 : B0AA0014
    bne.w L_00A630                                    ; +$015C : 660003C0
    move.l #$00000000,d0                              ; +$0160 : 203C00000000
    move.w 4(a0),d0                                   ; +$0166 : 30280004
    cmpi.l #$00000004,d0                              ; +$016A : 0C8000000004
    bcs.w L_00A630                                    ; +$0170 : 650003AC
    cmpi.l #$00001000,d0                              ; +$0174 : 0C8000001000
    bhi.w L_00A630                                    ; +$017A : 620003A2
    move.l d0,24(a2)                                  ; +$017E : 25400018
    move.l 8(a2),d1                                   ; +$0182 : 222A0008
    cmp.l d1,d0                                       ; +$0186 : B081
    bcs.w L_00A630                                    ; +$0188 : 65000394
    move.l #$00000120,d1                              ; +$018C : 223C00000120
    mulu.w d1,d0                                      ; +$0192 : C0C1
    addi.l #$0000000C,d0                              ; +$0194 : 06800000000C
    cmp.l 20(a2),d0                                   ; +$019A : B0AA0014
    bne.w L_00A630                                    ; +$019E : 6600037E
    move.l #$00000000,d0                              ; +$01A2 : 203C00000000
    move.w 6(a0),d0                                   ; +$01A8 : 30280006
    cmpi.l #$00000010,d0                              ; +$01AC : 0C8000000010
    bne.w L_00A630                                    ; +$01B2 : 6600036A
    move.l #$00000000,d0                              ; +$01B6 : 203C00000000
    move.w 8(a0),d0                                   ; +$01BC : 30280008
    cmpi.l #$00000010,d0                              ; +$01C0 : 0C8000000010
    bne.w L_00A630                                    ; +$01C6 : 66000356
    move.l #$00000000,d0                              ; +$01CA : 203C00000000
    move.w 10(a0),d0                                  ; +$01D0 : 3028000A
    cmpi.l #$00000008,d0                              ; +$01D4 : 0C8000000008
    bne.w L_00A630                                    ; +$01DA : 66000342
    move.l 8(a2),d0                                   ; +$01DE : 202A0008
    subq.l #1,d0                                      ; +$01E2 : 5380
    move.l #$00000120,d1                              ; +$01E4 : 223C00000120
    mulu.w d1,d0                                      ; +$01EA : C0C1
    addi.l #$0000000C,d0                              ; +$01EC : 06800000000C
    move.l 16(a2),d5                                  ; +$01F2 : 2A2A0010
    add.l d5,d0                                       ; +$01F6 : D085
    bcs.w L_00A630                                    ; +$01F8 : 65000324
    move.l d0,28(a2)                                  ; +$01FC : 2540001C
    addi.l #$0000011F,d0                              ; +$0200 : 06800000011F
    bcs.w L_00A630                                    ; +$0206 : 65000316
    movea.l d0,a1                                     ; +$020A : 2240
    movea.l $0004.w,a6                                ; +$020C : 2C780004
    jsr -534(a6)                                      ; +$0210 : 4EAEFDEA
    tst.l d0                                          ; +$0214 : 4A80
    beq.w L_00A630                                    ; +$0216 : 67000306
    movea.l 456(a5),a4                                ; +$021A : 286D01C8
    move.l a4,d0                                      ; +$021E : 200C
    tst.l d0                                          ; +$0220 : 4A80
    beq.w L_00A630                                    ; +$0222 : 670002FA
    move.l a4,32(a2)                                  ; +$0226 : 254C0020
    move.l (a4),d0                                    ; +$022A : 2014
    tst.l d0                                          ; +$022C : 4A80
    beq.w L_00A630                                    ; +$022E : 670002EE
    move.l 8(a4),d0                                   ; +$0232 : 202C0008
    tst.l d0                                          ; +$0236 : 4A80
    beq.w L_00A630                                    ; +$0238 : 670002E4
    move.l 32(a4),d0                                  ; +$023C : 202C0020
    tst.l d0                                          ; +$0240 : 4A80
    beq.w L_00A630                                    ; +$0242 : 670002DA
    move.l 12(a4),d0                                  ; +$0246 : 202C000C
    cmpi.l #$00000010,d0                              ; +$024A : 0C8000000010
    bcs.w L_00A630                                    ; +$0250 : 650002CC
    cmpi.l #$00001000,d0                              ; +$0254 : 0C8000001000
    bhi.w L_00A630                                    ; +$025A : 620002C2
    move.l d0,44(a2)                                  ; +$025E : 2540002C
    move.l 16(a4),d0                                  ; +$0262 : 202C0010
    cmpi.l #$00000010,d0                              ; +$0266 : 0C8000000010
    bcs.w L_00A630                                    ; +$026C : 650002B0
    cmpi.l #$00001000,d0                              ; +$0270 : 0C8000001000
    bhi.w L_00A630                                    ; +$0276 : 620002A6
    move.l d0,48(a2)                                  ; +$027A : 25400030
    move.l 28(a4),d0                                  ; +$027E : 202C001C
    cmpi.l #$00000008,d0                              ; +$0282 : 0C8000000008
    bne.w L_00A630                                    ; +$0288 : 66000294
    move.l 44(a2),d0                                  ; +$028C : 202A002C
    subi.l #$00000010,d0                              ; +$0290 : 048000000010
    move.l 4(a2),d1                                   ; +$0296 : 222A0004
    cmp.l d0,d1                                       ; +$029A : B280
    bhi.w L_00A630                                    ; +$029C : 62000280
    move.l 48(a2),d0                                  ; +$02A0 : 202A0030
    subi.l #$00000010,d0                              ; +$02A4 : 048000000010
    move.l (a2),d1                                    ; +$02AA : 2212
    cmp.l d0,d1                                       ; +$02AC : B280
    bhi.w L_00A630                                    ; +$02AE : 6200026E
    movea.l 32(a2),a4                                 ; +$02B2 : 286A0020
    movea.l 32(a4),a0                                 ; +$02B6 : 206C0020
    move.l a0,36(a2)                                  ; +$02BA : 25480024
    move.l 8(a0),d0                                   ; +$02BE : 20280008
    tst.l d0                                          ; +$02C2 : 4A80
    beq.w L_00A3EE                                    ; +$02C4 : 67000016
    cmpi.l #$00000001,d0                              ; +$02C8 : 0C8000000001
    bne.w L_00A630                                    ; +$02CE : 6600024E
    movea.l 36(a2),a0                                 ; +$02D2 : 206A0024
    movea.l (a0),a1                                   ; +$02D6 : 2250
    bra.w L_00A3F6                                    ; +$02D8 : 6000000A
L_00A3EE:
    movea.l 36(a2),a0                                 ; +$02DC : 206A0024
    movea.l 4(a0),a1                                  ; +$02E0 : 22680004
L_00A3F6:
    move.l a1,d0                                      ; +$02E4 : 2009
    tst.l d0                                          ; +$02E6 : 4A80
    beq.w L_00A630                                    ; +$02E8 : 67000234
    movea.l (a1),a0                                   ; +$02EC : 2051
    move.l a0,d0                                      ; +$02EE : 2008
    tst.l d0                                          ; +$02F0 : 4A80
    beq.w L_00A630                                    ; +$02F2 : 6700022A
    move.l a0,40(a2)                                  ; +$02F6 : 25480028
    move.l #$00000000,d0                              ; +$02FA : 203C00000000
    move.w (a0),d0                                    ; +$0300 : 3010
    cmpi.l #$00000002,d0                              ; +$0302 : 0C8000000002
    bcs.w L_00A630                                    ; +$0308 : 65000214
    cmpi.l #$0000FFFE,d0                              ; +$030C : 0C800000FFFE
    bhi.w L_00A630                                    ; +$0312 : 6200020A
    move.l d0,d1                                      ; +$0316 : 2200
    andi.l #$00000001,d1                              ; +$0318 : 028100000001
    bne.w L_00A630                                    ; +$031E : 660001FE
    move.l d0,52(a2)                                  ; +$0322 : 25400034
    lsl.l #3,d0                                       ; +$0326 : E788
    cmp.l 44(a2),d0                                   ; +$0328 : B0AA002C
    bcs.w L_00A630                                    ; +$032C : 650001F0
    movea.l 40(a2),a0                                 ; +$0330 : 206A0028
    move.l #$00000000,d0                              ; +$0334 : 203C00000000
    move.w 2(a0),d0                                   ; +$033A : 30280002
    cmp.l 48(a2),d0                                   ; +$033E : B0AA0030
    bcs.w L_00A630                                    ; +$0342 : 650001DA
    move.l #$00000000,d0                              ; +$0346 : 203C00000000
    move.b 5(a0),d0                                   ; +$034C : 10280005
    cmpi.l #$00000008,d0                              ; +$0350 : 0C8000000008
    bne.w L_00A630                                    ; +$0356 : 660001C6
    move.l 4(a2),d0                                   ; +$035A : 202A0004
    lsr.l #3,d0                                       ; +$035E : E688
    move.l d0,56(a2)                                  ; +$0360 : 25400038
    move.l 4(a2),d0                                   ; +$0364 : 202A0004
    andi.l #$00000007,d0                              ; +$0368 : 028000000007
    move.l #$00000007,d1                              ; +$036E : 223C00000007
    sub.l d0,d1                                       ; +$0374 : 9280
    move.l d1,60(a2)                                  ; +$0376 : 2541003C
    move.l (a2),d0                                    ; +$037A : 2012
    move.l 52(a2),d1                                  ; +$037C : 222A0034
    mulu.w d1,d0                                      ; +$0380 : C0C1
    move.l d0,64(a2)                                  ; +$0382 : 25400040
    move.l 56(a2),d1                                  ; +$0386 : 222A0038
    add.l d1,d0                                       ; +$038A : D081
    bcs.w L_00A630                                    ; +$038C : 65000190
    move.l d0,68(a2)                                  ; +$0390 : 25400044
    move.l (a2),d0                                    ; +$0394 : 2012
    addi.l #$0000000F,d0                              ; +$0396 : 06800000000F
    move.l 52(a2),d1                                  ; +$039C : 222A0034
    mulu.w d1,d0                                      ; +$03A0 : C0C1
    move.l 4(a2),d1                                   ; +$03A2 : 222A0004
    addi.l #$0000000F,d1                              ; +$03A6 : 06810000000F
    lsr.l #3,d1                                       ; +$03AC : E689
    add.l d1,d0                                       ; +$03AE : D081
    bcs.w L_00A630                                    ; +$03B0 : 6500016C
    move.l d0,72(a2)                                  ; +$03B4 : 25400048
    movea.l 40(a2),a4                                 ; +$03B8 : 286A0028
    addq.l #8,a4                                      ; +$03BC : 508C
    move.l #$00000008,d5                              ; +$03BE : 2A3C00000008
L_00A4D6:
    move.l (a4)+,d7                                   ; +$03C4 : 2E1C
    tst.l d7                                          ; +$03C6 : 4A87
    beq.w L_00A630                                    ; +$03C8 : 67000154
    cmpi.l #$FFFFFFFF,d7                              ; +$03CC : 0C87FFFFFFFF
    beq.w L_00A630                                    ; +$03D2 : 6700014A
    move.l d7,d0                                      ; +$03D6 : 2007
    andi.l #$00000001,d0                              ; +$03D8 : 028000000001
    bne.w L_00A630                                    ; +$03DE : 6600013E
    move.l d7,d0                                      ; +$03E2 : 2007
    move.l 68(a2),d1                                  ; +$03E4 : 222A0044
    add.l d1,d0                                       ; +$03E8 : D081
    bcs.w L_00A630                                    ; +$03EA : 65000132
    movea.l d0,a1                                     ; +$03EE : 2240
    movea.l $0004.w,a6                                ; +$03F0 : 2C780004
    jsr -534(a6)                                      ; +$03F4 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$03F8 : 028000000002
    tst.l d0                                          ; +$03FE : 4A80
    beq.w L_00A630                                    ; +$0400 : 6700011C
    move.l d7,d0                                      ; +$0404 : 2007
    move.l 72(a2),d1                                  ; +$0406 : 222A0048
    add.l d1,d0                                       ; +$040A : D081
    bcs.w L_00A630                                    ; +$040C : 65000110
    movea.l d0,a1                                     ; +$0410 : 2240
    movea.l $0004.w,a6                                ; +$0412 : 2C780004
    jsr -534(a6)                                      ; +$0416 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$041A : 028000000002
    tst.l d0                                          ; +$0420 : 4A80
    beq.w L_00A630                                    ; +$0422 : 670000FA
    subq.l #1,d5                                      ; +$0426 : 5385
    bne.w L_00A4D6                                    ; +$0428 : 6600FF9A
    movea.l 36(a2),a4                                 ; +$042C : 286A0024
    move.l 20(a4),d0                                  ; +$0430 : 202C0014
    andi.l #$00000001,d0                              ; +$0434 : 028000000001
    beq.w L_00A57C                                    ; +$043A : 6700002E
    movea.l 12(a4),a0                                 ; +$043E : 206C000C
    move.l a0,d0                                      ; +$0442 : 2008
    tst.l d0                                          ; +$0444 : 4A80
    beq.w L_00A630                                    ; +$0446 : 670000D6
    movea.l $0004.w,a6                                ; +$044A : 2C780004
    jsr -372(a6)                                      ; +$044E : 4EAEFE8C
    tst.l d0                                          ; +$0452 : 4A80
    beq.w L_00A630                                    ; +$0454 : 670000C8
    movea.l 36(a2),a4                                 ; +$0458 : 286A0024
    move.l 20(a4),d0                                  ; +$045C : 202C0014
    andi.l #$FFFFFFFE,d0                              ; +$0460 : 0280FFFFFFFE
    move.l d0,20(a4)                                  ; +$0466 : 29400014
L_00A57C:
    movea.l 32(a2),a4                                 ; +$046A : 286A0020
    movea.l 8(a4),a6                                  ; +$046E : 2C6C0008
    jsr -228(a6)                                      ; +$0472 : 4EAEFF1C
    move.l 28(a2),d0                                  ; +$0476 : 202A001C
    move.l d0,76(a2)                                  ; +$047A : 2540004C
    move.l #$00000010,d6                              ; +$047E : 2C3C00000010
L_00A596:
    movea.l 40(a2),a0                                 ; +$0484 : 206A0028
    addq.l #8,a0                                      ; +$0488 : 5088
    movea.l 76(a2),a1                                 ; +$048A : 226A004C
    addq.l #2,a1                                      ; +$048E : 5489
    move.l #$00000008,d5                              ; +$0490 : 2A3C00000008
    move.l #$00000000,d7                              ; +$0496 : 2E3C00000000
L_00A5AE:
    movea.l (a0)+,a4                                  ; +$049C : 2858
    move.l 64(a2),d0                                  ; +$049E : 202A0040
    adda.l d0,a4                                      ; +$04A2 : D9C0
    move.l 56(a2),d0                                  ; +$04A4 : 202A0038
    adda.l d0,a4                                      ; +$04A8 : D9C0
    move.l #$00000000,d4                              ; +$04AA : 283C00000000
    move.w #$8000,d2                                  ; +$04B0 : 343C8000
    move.l 60(a2),d1                                  ; +$04B4 : 222A003C
    move.l #$00000010,d0                              ; +$04B8 : 203C00000010
L_00A5D0:
    move.l #$00000000,d3                              ; +$04BE : 263C00000000
    move.b (a4),d3                                    ; +$04C4 : 1614
    btst d1,d3                                        ; +$04C6 : 0303
    beq.w L_00A5E0                                    ; +$04C8 : 67000004
    or.w d2,d4                                        ; +$04CC : 8842
L_00A5E0:
    lsr.w #1,d2                                       ; +$04CE : E24A
    subq.l #1,d1                                      ; +$04D0 : 5381
    bpl.w L_00A5F0                                    ; +$04D2 : 6A00000A
    addq.l #1,a4                                      ; +$04D6 : 528C
    move.l #$00000007,d1                              ; +$04D8 : 223C00000007
L_00A5F0:
    subq.l #1,d0                                      ; +$04DE : 5380
    bne.w L_00A5D0                                    ; +$04E0 : 6600FFDC
    move.w d4,(a1)+                                   ; +$04E4 : 32C4
    or.w d4,d7                                        ; +$04E6 : 8E44
    subq.l #1,d5                                      ; +$04E8 : 5385
    bne.w L_00A5AE                                    ; +$04EA : 6600FFB0
    not.w d7                                          ; +$04EE : 4647
    movea.l 76(a2),a1                                 ; +$04F0 : 226A004C
    move.w d7,(a1)                                    ; +$04F4 : 3287
    move.l 64(a2),d0                                  ; +$04F6 : 202A0040
    move.l 52(a2),d1                                  ; +$04FA : 222A0034
    add.l d1,d0                                       ; +$04FE : D081
    move.l d0,64(a2)                                  ; +$0500 : 25400040
    move.l 76(a2),d0                                  ; +$0504 : 202A004C
    addi.l #$00000012,d0                              ; +$0508 : 068000000012
    move.l d0,76(a2)                                  ; +$050E : 2540004C
    subq.l #1,d6                                      ; +$0512 : 5386
    bne.w L_00A596                                    ; +$0514 : 6600FF6E
    move.l #$00000001,d3                              ; +$0518 : 263C00000001
L_00A630:
    lea 128(a7),a7                                    ; +$051E : 4FEF0080
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0522 : 4CDF77F7
    moveq #0,d2                                       ; +$0526 : 7400
    rts                                               ; +$0528 : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 67 : aga c block capture --------
Entry_67:
Aga_C_Block_Capture:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -384(a7),a7                                   ; +$0004 : 4FEFFE80
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l #$00000000,72(a2)                          ; +$000C : 257C000000000048
    move.l (a3)+,d7                                   ; +$0014 : 2E1B
    move.l d7,4(a2)                                   ; +$0016 : 25470004
    move.l (a3)+,d7                                   ; +$001A : 2E1B
    move.l d7,8(a2)                                   ; +$001C : 25470008
    move.l (a3)+,d7                                   ; +$0020 : 2E1B
    move.l d7,12(a2)                                  ; +$0022 : 2547000C
    move.l (a3)+,d7                                   ; +$0026 : 2E1B
    move.l d7,16(a2)                                  ; +$0028 : 25470010
    move.l (a3)+,d7                                   ; +$002C : 2E1B
    move.l d7,20(a2)                                  ; +$002E : 25470014
    move.l #$00000000,d3                              ; +$0032 : 263C00000000
    move.l (a2),d0                                    ; +$0038 : 2012
    tst.l d0                                          ; +$003A : 4A80
    bmi.w L_00AD6A                                    ; +$003C : 6B0006EC
    cmpi.l #$00000002,d0                              ; +$0040 : 0C8000000002
    bhi.w L_00AD6A                                    ; +$0046 : 620006E2
    move.l 20(a2),d0                                  ; +$004A : 202A0014
    cmpi.l #$00000005,d0                              ; +$004E : 0C8000000005
    bcs.w L_00AD6A                                    ; +$0054 : 650006D4
    cmpi.l #$0000FFFF,d0                              ; +$0058 : 0C800000FFFF
    bhi.w L_00AD6A                                    ; +$005E : 620006CA
    movea.l 456(a5),a4                                ; +$0062 : 286D01C8
    move.l a4,d0                                      ; +$0066 : 200C
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_00AD6A                                    ; +$006A : 670006BE
    move.l a4,32(a2)                                  ; +$006E : 254C0020
    move.l (a4),d0                                    ; +$0072 : 2014
    tst.l d0                                          ; +$0074 : 4A80
    beq.w L_00AD6A                                    ; +$0076 : 670006B2
    move.l 8(a4),d0                                   ; +$007A : 202C0008
    tst.l d0                                          ; +$007E : 4A80
    beq.w L_00AD6A                                    ; +$0080 : 670006A8
    move.l 32(a4),d0                                  ; +$0084 : 202C0020
    tst.l d0                                          ; +$0088 : 4A80
    beq.w L_00AD6A                                    ; +$008A : 6700069E
    move.l 8(a4),d0                                   ; +$008E : 202C0008
    move.l d0,44(a2)                                  ; +$0092 : 2540002C
    move.l 12(a4),d0                                  ; +$0096 : 202C000C
    tst.l d0                                          ; +$009A : 4A80
    ble.w L_00AD6A                                    ; +$009C : 6F00068C
    cmpi.l #$00001000,d0                              ; +$00A0 : 0C8000001000
    bhi.w L_00AD6A                                    ; +$00A6 : 62000682
    move.l d0,48(a2)                                  ; +$00AA : 25400030
    move.l 16(a4),d0                                  ; +$00AE : 202C0010
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_00AD6A                                    ; +$00B4 : 6F000674
    cmpi.l #$00001000,d0                              ; +$00B8 : 0C8000001000
    bhi.w L_00AD6A                                    ; +$00BE : 6200066A
    move.l d0,52(a2)                                  ; +$00C2 : 25400034
    move.l 28(a4),d0                                  ; +$00C6 : 202C001C
    tst.l d0                                          ; +$00CA : 4A80
    ble.w L_00AD6A                                    ; +$00CC : 6F00065C
    cmpi.l #$00000008,d0                              ; +$00D0 : 0C8000000008
    bhi.w L_00AD6A                                    ; +$00D6 : 62000652
    move.l d0,56(a2)                                  ; +$00DA : 25400038
    movea.l 32(a4),a4                                 ; +$00DE : 286C0020
    move.l a4,36(a2)                                  ; +$00E2 : 254C0024
    move.l 8(a4),d0                                   ; +$00E6 : 202C0008
    tst.l d0                                          ; +$00EA : 4A80
    beq.w L_00A744                                    ; +$00EC : 67000016
    cmpi.l #$00000001,d0                              ; +$00F0 : 0C8000000001
    bne.w L_00AD6A                                    ; +$00F6 : 66000632
    movea.l 36(a2),a4                                 ; +$00FA : 286A0024
    movea.l (a4),a1                                   ; +$00FE : 2254
    bra.w L_00A74C                                    ; +$0100 : 6000000A
L_00A744:
    movea.l 36(a2),a4                                 ; +$0104 : 286A0024
    movea.l 4(a4),a1                                  ; +$0108 : 226C0004
L_00A74C:
    move.l a1,d0                                      ; +$010C : 2009
    tst.l d0                                          ; +$010E : 4A80
    beq.w L_00AD6A                                    ; +$0110 : 67000618
    movea.l (a1),a0                                   ; +$0114 : 2051
    move.l a0,d0                                      ; +$0116 : 2008
    tst.l d0                                          ; +$0118 : 4A80
    beq.w L_00AD6A                                    ; +$011A : 6700060E
    move.l a0,40(a2)                                  ; +$011E : 25480028
    move.l #$00000000,d0                              ; +$0122 : 203C00000000
    move.w (a0),d0                                    ; +$0128 : 3010
    tst.l d0                                          ; +$012A : 4A80
    ble.w L_00AD6A                                    ; +$012C : 6F0005FC
    move.l d0,d1                                      ; +$0130 : 2200
    andi.l #$00000001,d1                              ; +$0132 : 028100000001
    bne.w L_00AD6A                                    ; +$0138 : 660005F0
    move.l d0,76(a2)                                  ; +$013C : 2540004C
    lsl.l #3,d0                                       ; +$0140 : E788
    cmp.l 48(a2),d0                                   ; +$0142 : B0AA0030
    bcs.w L_00AD6A                                    ; +$0146 : 650005E2
    move.l #$00000000,d0                              ; +$014A : 203C00000000
    move.w 2(a0),d0                                   ; +$0150 : 30280002
    cmp.l 52(a2),d0                                   ; +$0154 : B0AA0034
    bcs.w L_00AD6A                                    ; +$0158 : 650005D0
    move.l #$00000000,d0                              ; +$015C : 203C00000000
    move.b 5(a0),d0                                   ; +$0162 : 10280005
    cmp.l 56(a2),d0                                   ; +$0166 : B0AA0038
    bne.w L_00AD6A                                    ; +$016A : 660005BE
    move.l 8(a2),d0                                   ; +$016E : 202A0008
    tst.l d0                                          ; +$0172 : 4A80
    ble.w L_00AD6A                                    ; +$0174 : 6F0005B4
    cmpi.l #$00001000,d0                              ; +$0178 : 0C8000001000
    bhi.w L_00AD6A                                    ; +$017E : 620005AA
    move.l 4(a2),d0                                   ; +$0182 : 202A0004
    tst.l d0                                          ; +$0186 : 4A80
    ble.w L_00AD6A                                    ; +$0188 : 6F0005A0
    cmpi.l #$00001000,d0                              ; +$018C : 0C8000001000
    bhi.w L_00AD6A                                    ; +$0192 : 62000596
    move.l 16(a2),d0                                  ; +$0196 : 202A0010
    tst.l d0                                          ; +$019A : 4A80
    bmi.w L_00AD6A                                    ; +$019C : 6B00058C
    cmpi.l #$00007FFF,d0                              ; +$01A0 : 0C8000007FFF
    bhi.w L_00AD6A                                    ; +$01A6 : 62000582
    move.l 12(a2),d0                                  ; +$01AA : 202A000C
    tst.l d0                                          ; +$01AE : 4A80
    bmi.w L_00AD6A                                    ; +$01B0 : 6B000578
    cmpi.l #$00007FFF,d0                              ; +$01B4 : 0C8000007FFF
    bhi.w L_00AD6A                                    ; +$01BA : 6200056E
    move.l (a2),d1                                    ; +$01BE : 2212
    cmpi.l #$00000001,d1                              ; +$01C0 : 0C8100000001
    beq.w L_00A814                                    ; +$01C6 : 6700000C
    move.l #$00000007,d1                              ; +$01CA : 223C00000007
    bra.w L_00A81A                                    ; +$01D0 : 60000008
L_00A814:
    move.l #$0000000F,d1                              ; +$01D4 : 223C0000000F
L_00A81A:
    move.l 16(a2),d0                                  ; +$01DA : 202A0010
    and.l d1,d0                                       ; +$01DE : C081
    bne.w L_00AD6A                                    ; +$01E0 : 66000548
    move.l 8(a2),d0                                   ; +$01E4 : 202A0008
    and.l d1,d0                                       ; +$01E8 : C081
    bne.w L_00AD6A                                    ; +$01EA : 6600053E
    move.l 16(a2),d0                                  ; +$01EE : 202A0010
    move.l 8(a2),d1                                   ; +$01F2 : 222A0008
    add.l d1,d0                                       ; +$01F6 : D081
    bcs.w L_00AD6A                                    ; +$01F8 : 65000530
    cmp.l 48(a2),d0                                   ; +$01FC : B0AA0030
    bhi.w L_00AD6A                                    ; +$0200 : 62000528
    move.l 12(a2),d0                                  ; +$0204 : 202A000C
    move.l 4(a2),d1                                   ; +$0208 : 222A0004
    add.l d1,d0                                       ; +$020C : D081
    bcs.w L_00AD6A                                    ; +$020E : 6500051A
    cmp.l 52(a2),d0                                   ; +$0212 : B0AA0034
    bhi.w L_00AD6A                                    ; +$0216 : 62000512
    move.l 8(a2),d0                                   ; +$021A : 202A0008
    addi.l #$0000000F,d0                              ; +$021E : 06800000000F
    bcs.w L_00AD6A                                    ; +$0224 : 65000504
    lsr.l #4,d0                                       ; +$0228 : E888
    lsl.l #1,d0                                       ; +$022A : E388
    move.l d0,60(a2)                                  ; +$022C : 2540003C
    move.l 4(a2),d1                                   ; +$0230 : 222A0004
    mulu.w d1,d0                                      ; +$0234 : C0C1
    move.l d0,64(a2)                                  ; +$0236 : 25400040
    move.l 56(a2),d5                                  ; +$023A : 2A2A0038
    move.l #$00000028,d0                              ; +$023E : 203C00000028
L_00A884:
    move.l 64(a2),d1                                  ; +$0244 : 222A0040
    add.l d1,d0                                       ; +$0248 : D081
    bcs.w L_00AD6A                                    ; +$024A : 650004DE
    subq.l #1,d5                                      ; +$024E : 5385
    bne.w L_00A884                                    ; +$0250 : 6600FFF2
    cmpi.l #$00100000,d0                              ; +$0254 : 0C8000100000
    bhi.w L_00AD6A                                    ; +$025A : 620004CE
    move.l d0,68(a2)                                  ; +$025E : 25400044
    move.l 20(a2),d0                                  ; +$0262 : 202A0014
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,24(a2)                                  ; +$026C : 25480018
    move.l 24(a2),d0                                  ; +$0270 : 202A0018
    tst.l d0                                          ; +$0274 : 4A80
    bne.w L_00A9CA                                    ; +$0276 : 66000112
    move.l 20(a2),d0                                  ; +$027A : 202A0014
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,d0                                      ; +$0284 : 2008
    tst.l d0                                          ; +$0286 : 4A80
    bne.w L_00AD6A                                    ; +$0288 : 660004A0
    move.l 20(a2),d0                                  ; +$028C : 202A0014
    move.l #$00000003,d1                              ; +$0290 : 223C00000003
    move.l 68(a2),d2                                  ; +$0296 : 242A0044
    lea L_00AD90(pc),a0                               ; +$029A : 41FA04B4
    dc.b $FE,$11,$F7,$00,$03,$30
    tst.l d0                                          ; +$02A4 : 4A80
    beq.w L_00AD6A                                    ; +$02A6 : 67000482
    move.l d0,24(a2)                                  ; +$02AA : 25400018
    move.l #$00000001,72(a2)                          ; +$02AE : 257C000000010048
    move.l 24(a2),d0                                  ; +$02B6 : 202A0018
    cmpi.l #$00000018,d0                              ; +$02BA : 0C8000000018
    bls.w L_00AD6A                                    ; +$02C0 : 63000468
    move.l d0,d1                                      ; +$02C4 : 2200
    andi.l #$00000001,d1                              ; +$02C6 : 028100000001
    bne.w L_00AD6A                                    ; +$02CC : 6600045C
    movea.l d0,a1                                     ; +$02D0 : 2240
    movea.l $0004.w,a6                                ; +$02D2 : 2C780004
    jsr -534(a6)                                      ; +$02D6 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02DA : 028000000002
    beq.w L_00AD6A                                    ; +$02E0 : 67000448
    move.l 24(a2),d0                                  ; +$02E4 : 202A0018
    subi.l #$00000018,d0                              ; +$02E8 : 048000000018
    movea.l d0,a1                                     ; +$02EE : 2240
    movea.l $0004.w,a6                                ; +$02F0 : 2C780004
    jsr -534(a6)                                      ; +$02F4 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02F8 : 028000000002
    beq.w L_00AD6A                                    ; +$02FE : 6700042A
    move.l 24(a2),d0                                  ; +$0302 : 202A0018
    move.l 68(a2),d1                                  ; +$0306 : 222A0044
    add.l d1,d0                                       ; +$030A : D081
    bcs.w L_00AD6A                                    ; +$030C : 6500041C
    subq.l #1,d0                                      ; +$0310 : 5380
    movea.l d0,a1                                     ; +$0312 : 2240
    movea.l $0004.w,a6                                ; +$0314 : 2C780004
    jsr -534(a6)                                      ; +$0318 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$031C : 028000000002
    beq.w L_00AD6A                                    ; +$0322 : 67000406
    movea.l 24(a2),a0                                 ; +$0326 : 206A0018
    move.l #$41474143,(a0)+                           ; +$032A : 20FC41474143
    move.l #$424C4B31,(a0)+                           ; +$0330 : 20FC424C4B31
    move.w #$0028,(a0)+                               ; +$0336 : 30FC0028
    move.w #$0001,(a0)+                               ; +$033A : 30FC0001
    move.l 56(a2),d0                                  ; +$033E : 202A0038
    move.w d0,(a0)+                                   ; +$0342 : 30C0
    move.w #$0000,(a0)+                               ; +$0344 : 30FC0000
    move.l 16(a2),d0                                  ; +$0348 : 202A0010
    move.l d0,(a0)+                                   ; +$034C : 20C0
    move.l 12(a2),d0                                  ; +$034E : 202A000C
    move.l d0,(a0)+                                   ; +$0352 : 20C0
    move.l 8(a2),d0                                   ; +$0354 : 202A0008
    move.l d0,(a0)+                                   ; +$0358 : 20C0
    move.l 4(a2),d0                                   ; +$035A : 202A0004
    move.l d0,(a0)+                                   ; +$035E : 20C0
    move.l 60(a2),d0                                  ; +$0360 : 202A003C
    move.l d0,(a0)+                                   ; +$0364 : 20C0
    move.l 64(a2),d0                                  ; +$0366 : 202A0040
    move.l d0,(a0)+                                   ; +$036A : 20C0
    move.l 68(a2),d6                                  ; +$036C : 2C2A0044
    subi.l #$00000028,d6                              ; +$0370 : 048600000028
    lsr.l #1,d6                                       ; +$0376 : E28E
    move.l #$00000000,d0                              ; +$0378 : 203C00000000
L_00A9BE:
    move.w d0,(a0)+                                   ; +$037E : 30C0
    subq.l #1,d6                                      ; +$0380 : 5386
    bne.w L_00A9BE                                    ; +$0382 : 6600FFFA
    bra.w L_00AB5A                                    ; +$0386 : 60000192
L_00A9CA:
    move.l 24(a2),d5                                  ; +$038A : 2A2A0018
    cmpi.l #$00000018,d5                              ; +$038E : 0C8500000018
    bls.w L_00AD6A                                    ; +$0394 : 63000394
    move.l d5,d0                                      ; +$0398 : 2005
    andi.l #$00000001,d0                              ; +$039A : 028000000001
    bne.w L_00AD6A                                    ; +$03A0 : 66000388
    movea.l d5,a1                                     ; +$03A4 : 2245
    movea.l $0004.w,a6                                ; +$03A6 : 2C780004
    jsr -534(a6)                                      ; +$03AA : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$03AE : 028000000002
    beq.w L_00AD6A                                    ; +$03B4 : 67000374
    move.l 24(a2),d0                                  ; +$03B8 : 202A0018
    subi.l #$00000018,d0                              ; +$03BC : 048000000018
    movea.l d0,a1                                     ; +$03C2 : 2240
    movea.l $0004.w,a6                                ; +$03C4 : 2C780004
    jsr -534(a6)                                      ; +$03C8 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$03CC : 028000000002
    beq.w L_00AD6A                                    ; +$03D2 : 67000356
    movea.l 24(a2),a0                                 ; +$03D6 : 206A0018
    move.l -20(a0),d4                                 ; +$03DA : 2828FFEC
    cmpi.l #$00000038,d4                              ; +$03DE : 0C8400000038
    bcs.w L_00AD6A                                    ; +$03E4 : 65000344
    subi.l #$00000010,d4                              ; +$03E8 : 048400000010
    cmpi.l #$00100000,d4                              ; +$03EE : 0C8400100000
    bhi.w L_00AD6A                                    ; +$03F4 : 62000334
    move.l d4,28(a2)                                  ; +$03F8 : 2544001C
    move.l 24(a2),d0                                  ; +$03FC : 202A0018
    add.l d4,d0                                       ; +$0400 : D084
    bcs.w L_00AD6A                                    ; +$0402 : 65000326
    subq.l #1,d0                                      ; +$0406 : 5380
    movea.l d0,a1                                     ; +$0408 : 2240
    movea.l $0004.w,a6                                ; +$040A : 2C780004
    jsr -534(a6)                                      ; +$040E : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0412 : 028000000002
    beq.w L_00AD6A                                    ; +$0418 : 67000310
    movea.l 24(a2),a0                                 ; +$041C : 206A0018
    move.l -16(a0),d0                                 ; +$0420 : 2028FFF0
    move.l 20(a2),d1                                  ; +$0424 : 222A0014
    cmp.l d1,d0                                       ; +$0428 : B081
    bne.w L_00AD6A                                    ; +$042A : 660002FE
    move.l #$00000000,d0                              ; +$042E : 203C00000000
    move.w -12(a0),d0                                 ; +$0434 : 3028FFF4
    tst.l d0                                          ; +$0438 : 4A80
    beq.w L_00AA8A                                    ; +$043A : 6700000E
    andi.w #$FFFD,d0                                  ; +$043E : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0442 : 0C400001
    bne.w L_00AD6A                                    ; +$0446 : 660002E2
L_00AA8A:
    move.l -8(a0),d0                                  ; +$044A : 2028FFF8
    cmpi.l #$41474143,d0                              ; +$044E : 0C8041474143
    bne.w L_00AD6A                                    ; +$0454 : 660002D4
    move.l -4(a0),d0                                  ; +$0458 : 2028FFFC
    cmpi.l #$424C4B20,d0                              ; +$045C : 0C80424C4B20
    bne.w L_00AD6A                                    ; +$0462 : 660002C6
    move.l (a0),d0                                    ; +$0466 : 2010
    cmpi.l #$41474143,d0                              ; +$0468 : 0C8041474143
    bne.w L_00AD6A                                    ; +$046E : 660002BA
    move.l 4(a0),d0                                   ; +$0472 : 20280004
    cmpi.l #$424C4B31,d0                              ; +$0476 : 0C80424C4B31
    bne.w L_00AD6A                                    ; +$047C : 660002AC
    move.l #$00000000,d0                              ; +$0480 : 203C00000000
    move.w 8(a0),d0                                   ; +$0486 : 30280008
    cmpi.l #$00000028,d0                              ; +$048A : 0C8000000028
    bne.w L_00AD6A                                    ; +$0490 : 66000298
    move.l #$00000000,d0                              ; +$0494 : 203C00000000
    move.w 10(a0),d0                                  ; +$049A : 3028000A
    cmpi.l #$00000001,d0                              ; +$049E : 0C8000000001
    bne.w L_00AD6A                                    ; +$04A4 : 66000284
    move.l #$00000000,d0                              ; +$04A8 : 203C00000000
    move.w 14(a0),d0                                  ; +$04AE : 3028000E
    cmpi.l #$00000000,d0                              ; +$04B2 : 0C8000000000
    bne.w L_00AD6A                                    ; +$04B8 : 66000270
    move.l #$00000000,d0                              ; +$04BC : 203C00000000
    move.w 12(a0),d0                                  ; +$04C2 : 3028000C
    cmp.l 56(a2),d0                                   ; +$04C6 : B0AA0038
    bne.w L_00AD6A                                    ; +$04CA : 6600025E
    movea.l 24(a2),a0                                 ; +$04CE : 206A0018
    move.l 24(a0),d0                                  ; +$04D2 : 20280018
    cmp.l 8(a2),d0                                    ; +$04D6 : B0AA0008
    bne.w L_00AD6A                                    ; +$04DA : 6600024E
    movea.l 24(a2),a0                                 ; +$04DE : 206A0018
    move.l 28(a0),d0                                  ; +$04E2 : 2028001C
    cmp.l 4(a2),d0                                    ; +$04E6 : B0AA0004
    bne.w L_00AD6A                                    ; +$04EA : 6600023E
    movea.l 24(a2),a0                                 ; +$04EE : 206A0018
    move.l 32(a0),d0                                  ; +$04F2 : 20280020
    cmp.l 60(a2),d0                                   ; +$04F6 : B0AA003C
    bne.w L_00AD6A                                    ; +$04FA : 6600022E
    movea.l 24(a2),a0                                 ; +$04FE : 206A0018
    move.l 36(a0),d0                                  ; +$0502 : 20280024
    cmp.l 64(a2),d0                                   ; +$0506 : B0AA0040
    bne.w L_00AD6A                                    ; +$050A : 6600021E
    move.l 28(a2),d0                                  ; +$050E : 202A001C
    cmp.l 68(a2),d0                                   ; +$0512 : B0AA0044
    bne.w L_00AD6A                                    ; +$0516 : 66000212
L_00AB5A:
    move.l 12(a2),d0                                  ; +$051A : 202A000C
    move.l 76(a2),d1                                  ; +$051E : 222A004C
    mulu.w d1,d0                                      ; +$0522 : C0C1
    move.l 16(a2),d1                                  ; +$0524 : 222A0010
    lsr.l #3,d1                                       ; +$0528 : E689
    add.l d1,d0                                       ; +$052A : D081
    bcs.w L_00AD6A                                    ; +$052C : 650001FC
    move.l d0,80(a2)                                  ; +$0530 : 25400050
    move.l 12(a2),d0                                  ; +$0534 : 202A000C
    move.l 4(a2),d1                                   ; +$0538 : 222A0004
    add.l d1,d0                                       ; +$053C : D081
    bcs.w L_00AD6A                                    ; +$053E : 650001EA
    subq.l #1,d0                                      ; +$0542 : 5380
    move.l 76(a2),d1                                  ; +$0544 : 222A004C
    mulu.w d1,d0                                      ; +$0548 : C0C1
    move.l 16(a2),d1                                  ; +$054A : 222A0010
    move.l 8(a2),d4                                   ; +$054E : 282A0008
    add.l d4,d1                                       ; +$0552 : D284
    bcs.w L_00AD6A                                    ; +$0554 : 650001D4
    subq.l #1,d1                                      ; +$0558 : 5381
    lsr.l #3,d1                                       ; +$055A : E689
    add.l d1,d0                                       ; +$055C : D081
    bcs.w L_00AD6A                                    ; +$055E : 650001CA
    move.l d0,84(a2)                                  ; +$0562 : 25400054
    movea.l 40(a2),a4                                 ; +$0566 : 286A0028
    addq.l #8,a4                                      ; +$056A : 508C
    move.l 56(a2),d5                                  ; +$056C : 2A2A0038
L_00ABB0:
    move.l (a4)+,d7                                   ; +$0570 : 2E1C
    tst.l d7                                          ; +$0572 : 4A87
    beq.w L_00AD6A                                    ; +$0574 : 670001B4
    cmpi.l #$FFFFFFFF,d7                              ; +$0578 : 0C87FFFFFFFF
    beq.w L_00AD6A                                    ; +$057E : 670001AA
    move.l d7,d0                                      ; +$0582 : 2007
    andi.l #$00000001,d0                              ; +$0584 : 028000000001
    bne.w L_00AD6A                                    ; +$058A : 6600019E
    move.l 80(a2),d0                                  ; +$058E : 202A0050
    add.l d7,d0                                       ; +$0592 : D087
    bcs.w L_00AD6A                                    ; +$0594 : 65000194
    movea.l d0,a1                                     ; +$0598 : 2240
    movea.l $0004.w,a6                                ; +$059A : 2C780004
    jsr -534(a6)                                      ; +$059E : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$05A2 : 028000000002
    beq.w L_00AD6A                                    ; +$05A8 : 67000180
    move.l 84(a2),d0                                  ; +$05AC : 202A0054
    add.l d7,d0                                       ; +$05B0 : D087
    bcs.w L_00AD6A                                    ; +$05B2 : 65000176
    movea.l d0,a1                                     ; +$05B6 : 2240
    movea.l $0004.w,a6                                ; +$05B8 : 2C780004
    jsr -534(a6)                                      ; +$05BC : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$05C0 : 028000000002
    beq.w L_00AD6A                                    ; +$05C6 : 67000162
    subq.l #1,d5                                      ; +$05CA : 5385
    bne.w L_00ABB0                                    ; +$05CC : 6600FFA2
    move.l #$00000000,260(a2)                         ; +$05D0 : 257C000000000104
    move.l #$00000000,264(a2)                         ; +$05D8 : 257C000000000108
    move.l #$00000000,268(a2)                         ; +$05E0 : 257C00000000010C
    move.l #$00000000,272(a2)                         ; +$05E8 : 257C000000000110
    move.l #$00000000,276(a2)                         ; +$05F0 : 257C000000000114
    move.l #$00000000,280(a2)                         ; +$05F8 : 257C000000000118
    move.l #$00000000,284(a2)                         ; +$0600 : 257C00000000011C
    move.l #$00000000,288(a2)                         ; +$0608 : 257C000000000120
    move.l #$00000000,292(a2)                         ; +$0610 : 257C000000000124
    move.l 60(a2),d0                                  ; +$0618 : 202A003C
    move.w d0,256(a2)                                 ; +$061C : 35400100
    move.l 4(a2),d0                                   ; +$0620 : 202A0004
    move.w d0,258(a2)                                 ; +$0624 : 35400102
    move.l 56(a2),d0                                  ; +$0628 : 202A0038
    move.b d0,261(a2)                                 ; +$062C : 15400105
    lea 264(a2),a4                                    ; +$0630 : 49EA0108
    move.l 24(a2),d6                                  ; +$0634 : 2C2A0018
    addi.l #$00000028,d6                              ; +$0638 : 068600000028
    move.l 64(a2),d7                                  ; +$063E : 2E2A0040
    move.l 56(a2),d5                                  ; +$0642 : 2A2A0038
L_00AC86:
    movea.l d6,a1                                     ; +$0646 : 2246
    movea.l $0004.w,a6                                ; +$0648 : 2C780004
    jsr -534(a6)                                      ; +$064C : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0650 : 028000000002
    beq.w L_00AD6A                                    ; +$0656 : 670000D2
    move.l d6,d0                                      ; +$065A : 2006
    add.l d7,d0                                       ; +$065C : D087
    bcs.w L_00AD6A                                    ; +$065E : 650000CA
    subq.l #1,d0                                      ; +$0662 : 5380
    movea.l d0,a1                                     ; +$0664 : 2240
    movea.l $0004.w,a6                                ; +$0666 : 2C780004
    jsr -534(a6)                                      ; +$066A : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$066E : 028000000002
    beq.w L_00AD6A                                    ; +$0674 : 670000B4
    move.l d6,(a4)+                                   ; +$0678 : 28C6
    add.l d7,d6                                       ; +$067A : DC87
    bcs.w L_00AD6A                                    ; +$067C : 650000AC
    subq.l #1,d5                                      ; +$0680 : 5385
    bne.w L_00AC86                                    ; +$0682 : 6600FFC2
    movea.l 36(a2),a4                                 ; +$0686 : 286A0024
    move.l 20(a4),d0                                  ; +$068A : 202C0014
    andi.l #$00000001,d0                              ; +$068E : 028000000001
    beq.w L_00AD08                                    ; +$0694 : 67000032
    movea.l 36(a2),a4                                 ; +$0698 : 286A0024
    movea.l 12(a4),a0                                 ; +$069C : 206C000C
    move.l a0,d0                                      ; +$06A0 : 2008
    tst.l d0                                          ; +$06A2 : 4A80
    beq.w L_00AD6A                                    ; +$06A4 : 67000084
    movea.l $0004.w,a6                                ; +$06A8 : 2C780004
    jsr -372(a6)                                      ; +$06AC : 4EAEFE8C
    tst.l d0                                          ; +$06B0 : 4A80
    beq.w L_00AD6A                                    ; +$06B2 : 67000076
    movea.l 36(a2),a4                                 ; +$06B6 : 286A0024
    move.l 20(a4),d0                                  ; +$06BA : 202C0014
    andi.l #$FFFFFFFE,d0                              ; +$06BE : 0280FFFFFFFE
    move.l d0,20(a4)                                  ; +$06C4 : 29400014
L_00AD08:
    movea.l 44(a2),a6                                 ; +$06C8 : 2C6A002C
    jsr -228(a6)                                      ; +$06CC : 4EAEFF1C
    movea.l 40(a2),a0                                 ; +$06D0 : 206A0028
    lea 256(a2),a1                                    ; +$06D4 : 43EA0100
    move.l 16(a2),d0                                  ; +$06D8 : 202A0010
    move.l 12(a2),d1                                  ; +$06DC : 222A000C
    move.l #$00000000,d2                              ; +$06E0 : 243C00000000
    move.l #$00000000,d3                              ; +$06E6 : 263C00000000
    move.l 8(a2),d4                                   ; +$06EC : 282A0008
    move.l 4(a2),d5                                   ; +$06F0 : 2A2A0004
    move.l (a2),d6                                    ; +$06F4 : 2C12
    movea.l 44(a2),a6                                 ; +$06F6 : 2C6A002C
    lea L_00AD98(pc),a4                               ; +$06FA : 49FA005C
    jsr (a4)                                          ; +$06FE : 4E94
    tst.l d3                                          ; +$0700 : 4A83
    beq.w L_00AD6A                                    ; +$0702 : 67000026
    movea.l 24(a2),a0                                 ; +$0706 : 206A0018
    move.l 16(a2),d0                                  ; +$070A : 202A0010
    move.l d0,16(a0)                                  ; +$070E : 21400010
    move.l 12(a2),d0                                  ; +$0712 : 202A000C
    move.l d0,20(a0)                                  ; +$0716 : 21400014
    dc.b $FE,$11,$F7,$00,$03,$33
    move.l #$00000001,d3                              ; +$0720 : 263C00000001
    bra.w L_00AD84                                    ; +$0726 : 6000001C
L_00AD6A:
    move.l 72(a2),d0                                  ; +$072A : 202A0048
    tst.l d0                                          ; +$072E : 4A80
    beq.w L_00AD7E                                    ; +$0730 : 6700000C
    move.l 20(a2),d0                                  ; +$0734 : 202A0014
    dc.b $FE,$11,$F7,$00,$03,$20
L_00AD7E:
    move.l #$00000000,d3                              ; +$073E : 263C00000000
L_00AD84:
    lea 384(a7),a7                                    ; +$0744 : 4FEF0180
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0748 : 4CDF77F7
    moveq #0,d2                                       ; +$074C : 7400
    rts                                               ; +$074E : 4E75
L_00AD90:
    dc.b "AGACBLK "
L_00AD98:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0758 : 48E7EFEE
    lea -256(a7),a7                                   ; +$075C : 4FEFFF00
    movea.l a7,a4                                     ; +$0760 : 284F
    move.l a0,(a4)                                    ; +$0762 : 2888
    move.l a1,4(a4)                                   ; +$0764 : 29490004
    move.l a6,36(a4)                                  ; +$0768 : 294E0024
    move.l d0,8(a4)                                   ; +$076C : 29400008
    move.l d1,12(a4)                                  ; +$0770 : 2941000C
    move.l d2,16(a4)                                  ; +$0774 : 29420010
    move.l d3,20(a4)                                  ; +$0778 : 29430014
    move.l d4,24(a4)                                  ; +$077C : 29440018
    move.l d5,28(a4)                                  ; +$0780 : 2945001C
    move.l d6,32(a4)                                  ; +$0784 : 29460020
    move.l #$00000000,d3                              ; +$0788 : 263C00000000
    move.l (a4),d0                                    ; +$078E : 2014
    tst.l d0                                          ; +$0790 : 4A80
    beq.w L_00B0EE                                    ; +$0792 : 6700031A
    andi.l #$00000001,d0                              ; +$0796 : 028000000001
    bne.w L_00B0EE                                    ; +$079C : 66000310
    move.l 4(a4),d0                                   ; +$07A0 : 202C0004
    tst.l d0                                          ; +$07A4 : 4A80
    beq.w L_00B0EE                                    ; +$07A6 : 67000306
    andi.l #$00000001,d0                              ; +$07AA : 028000000001
    bne.w L_00B0EE                                    ; +$07B0 : 660002FC
    move.l 32(a4),d0                                  ; +$07B4 : 202C0020
    cmpi.l #$00000002,d0                              ; +$07B8 : 0C8000000002
    bhi.w L_00B0EE                                    ; +$07BE : 620002EE
    tst.l d0                                          ; +$07C2 : 4A80
    bmi.w L_00B0EE                                    ; +$07C4 : 6B0002E8
    move.l 8(a4),d0                                   ; +$07C8 : 202C0008
    tst.l d0                                          ; +$07CC : 4A80
    bmi.w L_00B0EE                                    ; +$07CE : 6B0002DE
    cmpi.l #$00007FFF,d0                              ; +$07D2 : 0C8000007FFF
    bgt.w L_00B0EE                                    ; +$07D8 : 6E0002D4
    move.l 12(a4),d0                                  ; +$07DC : 202C000C
    tst.l d0                                          ; +$07E0 : 4A80
    bmi.w L_00B0EE                                    ; +$07E2 : 6B0002CA
    cmpi.l #$00007FFF,d0                              ; +$07E6 : 0C8000007FFF
    bgt.w L_00B0EE                                    ; +$07EC : 6E0002C0
    move.l 16(a4),d0                                  ; +$07F0 : 202C0010
    tst.l d0                                          ; +$07F4 : 4A80
    bmi.w L_00B0EE                                    ; +$07F6 : 6B0002B6
    cmpi.l #$00007FFF,d0                              ; +$07FA : 0C8000007FFF
    bgt.w L_00B0EE                                    ; +$0800 : 6E0002AC
    move.l 20(a4),d0                                  ; +$0804 : 202C0014
    tst.l d0                                          ; +$0808 : 4A80
    bmi.w L_00B0EE                                    ; +$080A : 6B0002A2
    cmpi.l #$00007FFF,d0                              ; +$080E : 0C8000007FFF
    bgt.w L_00B0EE                                    ; +$0814 : 6E000298
    move.l 24(a4),d0                                  ; +$0818 : 202C0018
    tst.l d0                                          ; +$081C : 4A80
    ble.w L_00B0EE                                    ; +$081E : 6F00028E
    cmpi.l #$00001000,d0                              ; +$0822 : 0C8000001000
    bgt.w L_00B0EE                                    ; +$0828 : 6E000284
    move.l 28(a4),d0                                  ; +$082C : 202C001C
    tst.l d0                                          ; +$0830 : 4A80
    ble.w L_00B0EE                                    ; +$0832 : 6F00027A
    cmpi.l #$00001000,d0                              ; +$0836 : 0C8000001000
    bgt.w L_00B0EE                                    ; +$083C : 6E000270
    move.l 32(a4),d1                                  ; +$0840 : 222C0020
    cmpi.l #$00000001,d1                              ; +$0844 : 0C8100000001
    beq.w L_00AE98                                    ; +$084A : 6700000C
    move.l #$00000007,d1                              ; +$084E : 223C00000007
    bra.w L_00AE9E                                    ; +$0854 : 60000008
L_00AE98:
    move.l #$0000000F,d1                              ; +$0858 : 223C0000000F
L_00AE9E:
    move.l 8(a4),d0                                   ; +$085E : 202C0008
    and.l d1,d0                                       ; +$0862 : C081
    bne.w L_00B0EE                                    ; +$0864 : 66000248
    move.l 16(a4),d0                                  ; +$0868 : 202C0010
    and.l d1,d0                                       ; +$086C : C081
    bne.w L_00B0EE                                    ; +$086E : 6600023E
    move.l 24(a4),d0                                  ; +$0872 : 202C0018
    and.l d1,d0                                       ; +$0876 : C081
    bne.w L_00B0EE                                    ; +$0878 : 66000234
    movea.l (a4),a0                                   ; +$087C : 2054
    move.l #$00000000,d0                              ; +$087E : 203C00000000
    move.w (a0),d0                                    ; +$0884 : 3010
    move.l d0,40(a4)                                  ; +$0886 : 29400028
    tst.l d0                                          ; +$088A : 4A80
    ble.w L_00B0EE                                    ; +$088C : 6F000220
    andi.l #$00000001,d0                              ; +$0890 : 028000000001
    bne.w L_00B0EE                                    ; +$0896 : 66000216
    move.l #$00000000,d0                              ; +$089A : 203C00000000
    move.w 2(a0),d0                                   ; +$08A0 : 30280002
    move.l d0,68(a4)                                  ; +$08A4 : 29400044
    tst.l d0                                          ; +$08A8 : 4A80
    ble.w L_00B0EE                                    ; +$08AA : 6F000202
    move.l #$00000000,d0                              ; +$08AE : 203C00000000
    move.b 5(a0),d0                                   ; +$08B4 : 10280005
    tst.l d0                                          ; +$08B8 : 4A80
    ble.w L_00B0EE                                    ; +$08BA : 6F0001F2
    cmpi.l #$00000008,d0                              ; +$08BE : 0C8000000008
    bgt.w L_00B0EE                                    ; +$08C4 : 6E0001E8
    move.l d0,48(a4)                                  ; +$08C8 : 29400030
    movea.l 4(a4),a0                                  ; +$08CC : 206C0004
    move.l #$00000000,d0                              ; +$08D0 : 203C00000000
    move.w (a0),d0                                    ; +$08D6 : 3010
    move.l d0,44(a4)                                  ; +$08D8 : 2940002C
    tst.l d0                                          ; +$08DC : 4A80
    ble.w L_00B0EE                                    ; +$08DE : 6F0001CE
    andi.l #$00000001,d0                              ; +$08E2 : 028000000001
    bne.w L_00B0EE                                    ; +$08E8 : 660001C4
    move.l #$00000000,d0                              ; +$08EC : 203C00000000
    move.w 2(a0),d0                                   ; +$08F2 : 30280002
    move.l d0,72(a4)                                  ; +$08F6 : 29400048
    tst.l d0                                          ; +$08FA : 4A80
    ble.w L_00B0EE                                    ; +$08FC : 6F0001B0
    move.l #$00000000,d0                              ; +$0900 : 203C00000000
    move.b 5(a0),d0                                   ; +$0906 : 10280005
    tst.l d0                                          ; +$090A : 4A80
    ble.w L_00B0EE                                    ; +$090C : 6F0001A0
    cmpi.l #$00000008,d0                              ; +$0910 : 0C8000000008
    bgt.w L_00B0EE                                    ; +$0916 : 6E000196
    cmp.l 48(a4),d0                                   ; +$091A : B0AC0030
    bne.w L_00B0EE                                    ; +$091E : 6600018E
    move.l 8(a4),d0                                   ; +$0922 : 202C0008
    move.l 24(a4),d1                                  ; +$0926 : 222C0018
    add.l d1,d0                                       ; +$092A : D081
    move.l 40(a4),d1                                  ; +$092C : 222C0028
    lsl.l #3,d1                                       ; +$0930 : E789
    cmp.l d1,d0                                       ; +$0932 : B081
    bhi.w L_00B0EE                                    ; +$0934 : 62000178
    move.l 12(a4),d0                                  ; +$0938 : 202C000C
    move.l 28(a4),d1                                  ; +$093C : 222C001C
    add.l d1,d0                                       ; +$0940 : D081
    cmp.l 68(a4),d0                                   ; +$0942 : B0AC0044
    bhi.w L_00B0EE                                    ; +$0946 : 62000166
    move.l 16(a4),d0                                  ; +$094A : 202C0010
    move.l 24(a4),d1                                  ; +$094E : 222C0018
    add.l d1,d0                                       ; +$0952 : D081
    move.l 44(a4),d1                                  ; +$0954 : 222C002C
    lsl.l #3,d1                                       ; +$0958 : E789
    cmp.l d1,d0                                       ; +$095A : B081
    bhi.w L_00B0EE                                    ; +$095C : 62000150
    move.l 20(a4),d0                                  ; +$0960 : 202C0014
    move.l 28(a4),d1                                  ; +$0964 : 222C001C
    add.l d1,d0                                       ; +$0968 : D081
    cmp.l 72(a4),d0                                   ; +$096A : B0AC0048
    bhi.w L_00B0EE                                    ; +$096E : 6200013E
    movea.l (a4),a5                                   ; +$0972 : 2A54
    addq.l #8,a5                                      ; +$0974 : 508D
    movea.l 4(a4),a6                                  ; +$0976 : 2C6C0004
    addq.l #8,a6                                      ; +$097A : 508E
    move.l 48(a4),d7                                  ; +$097C : 2E2C0030
L_00AFC0:
    move.l (a5)+,d0                                   ; +$0980 : 201D
    tst.l d0                                          ; +$0982 : 4A80
    beq.w L_00B0EE                                    ; +$0984 : 67000128
    andi.l #$00000001,d0                              ; +$0988 : 028000000001
    bne.w L_00B0EE                                    ; +$098E : 6600011E
    move.l (a6)+,d0                                   ; +$0992 : 201E
    tst.l d0                                          ; +$0994 : 4A80
    beq.w L_00B0EE                                    ; +$0996 : 67000116
    andi.l #$00000001,d0                              ; +$099A : 028000000001
    bne.w L_00B0EE                                    ; +$09A0 : 6600010C
    subq.l #1,d7                                      ; +$09A4 : 5387
    bne.w L_00AFC0                                    ; +$09A6 : 6600FFD8
    move.l 32(a4),d0                                  ; +$09AA : 202C0020
    cmpi.l #$00000002,d0                              ; +$09AE : 0C8000000002
    bne.w L_00B048                                    ; +$09B4 : 66000052
    move.l 36(a4),d0                                  ; +$09B8 : 202C0024
    tst.l d0                                          ; +$09BC : 4A80
    beq.w L_00B0EE                                    ; +$09BE : 670000EE
    movea.l 36(a4),a6                                 ; +$09C2 : 2C6C0024
    lea 128(a4),a1                                    ; +$09C6 : 43EC0080
    jsr -198(a6)                                      ; +$09CA : 4EAEFF3A
    lea 128(a4),a1                                    ; +$09CE : 43EC0080
    move.l 4(a4),4(a1)                                ; +$09D2 : 236C00040004
    movea.l (a4),a0                                   ; +$09D8 : 2054
    move.l 8(a4),d0                                   ; +$09DA : 202C0008
    move.l 12(a4),d1                                  ; +$09DE : 222C000C
    move.l 16(a4),d2                                  ; +$09E2 : 242C0010
    move.l 20(a4),d3                                  ; +$09E6 : 262C0014
    move.l 24(a4),d4                                  ; +$09EA : 282C0018
    move.l 28(a4),d5                                  ; +$09EE : 2A2C001C
    move.l #$000000C0,d6                              ; +$09F2 : 2C3C000000C0
    jsr -606(a6)                                      ; +$09F8 : 4EAEFDA2
    movea.l 36(a4),a6                                 ; +$09FC : 2C6C0024
    jsr -228(a6)                                      ; +$0A00 : 4EAEFF1C
    bra.w L_00B0E4                                    ; +$0A04 : 6000009E
L_00B048:
    move.l 24(a4),d0                                  ; +$0A08 : 202C0018
    lsr.l #3,d0                                       ; +$0A0C : E688
    move.l d0,52(a4)                                  ; +$0A0E : 29400034
    move.l 40(a4),d1                                  ; +$0A12 : 222C0028
    sub.l d0,d1                                       ; +$0A16 : 9280
    move.l d1,56(a4)                                  ; +$0A18 : 29410038
    move.l 44(a4),d1                                  ; +$0A1C : 222C002C
    sub.l d0,d1                                       ; +$0A20 : 9280
    move.l d1,60(a4)                                  ; +$0A22 : 2941003C
    movea.l (a4),a5                                   ; +$0A26 : 2A54
    addq.l #8,a5                                      ; +$0A28 : 508D
    movea.l 4(a4),a6                                  ; +$0A2A : 2C6C0004
    addq.l #8,a6                                      ; +$0A2E : 508E
    move.l 48(a4),d7                                  ; +$0A30 : 2E2C0030
L_00B074:
    movea.l (a5)+,a0                                  ; +$0A34 : 205D
    movea.l (a6)+,a1                                  ; +$0A36 : 225E
    move.l 12(a4),d0                                  ; +$0A38 : 202C000C
    move.l 40(a4),d1                                  ; +$0A3C : 222C0028
    mulu.w d1,d0                                      ; +$0A40 : C0C1
    move.l 8(a4),d1                                   ; +$0A42 : 222C0008
    lsr.l #3,d1                                       ; +$0A46 : E689
    add.l d1,d0                                       ; +$0A48 : D081
    adda.l d0,a0                                      ; +$0A4A : D1C0
    move.l 20(a4),d0                                  ; +$0A4C : 202C0014
    move.l 44(a4),d1                                  ; +$0A50 : 222C002C
    mulu.w d1,d0                                      ; +$0A54 : C0C1
    move.l 16(a4),d1                                  ; +$0A56 : 222C0010
    lsr.l #3,d1                                       ; +$0A5A : E689
    add.l d1,d0                                       ; +$0A5C : D081
    adda.l d0,a1                                      ; +$0A5E : D3C0
    move.l 28(a4),d4                                  ; +$0A60 : 282C001C
L_00B0A4:
    move.l 52(a4),d6                                  ; +$0A64 : 2C2C0034
    move.l 32(a4),d0                                  ; +$0A68 : 202C0020
    cmpi.l #$00000001,d0                              ; +$0A6C : 0C8000000001
    beq.w L_00B0C2                                    ; +$0A72 : 6700000E
L_00B0B6:
    move.b (a0)+,(a1)+                                ; +$0A76 : 12D8
    subq.l #1,d6                                      ; +$0A78 : 5386
    bne.w L_00B0B6                                    ; +$0A7A : 6600FFFA
    bra.w L_00B0CC                                    ; +$0A7E : 6000000C
L_00B0C2:
    lsr.l #1,d6                                       ; +$0A82 : E28E
L_00B0C4:
    move.w (a0)+,(a1)+                                ; +$0A84 : 32D8
    subq.l #1,d6                                      ; +$0A86 : 5386
    bne.w L_00B0C4                                    ; +$0A88 : 6600FFFA
L_00B0CC:
    move.l 56(a4),d0                                  ; +$0A8C : 202C0038
    adda.l d0,a0                                      ; +$0A90 : D1C0
    move.l 60(a4),d0                                  ; +$0A92 : 202C003C
    adda.l d0,a1                                      ; +$0A96 : D3C0
    subq.l #1,d4                                      ; +$0A98 : 5384
    bne.w L_00B0A4                                    ; +$0A9A : 6600FFC8
    subq.l #1,d7                                      ; +$0A9E : 5387
    bne.w L_00B074                                    ; +$0AA0 : 6600FF92
L_00B0E4:
    move.l #$00000001,d3                              ; +$0AA4 : 263C00000001
    bra.w L_00B0F4                                    ; +$0AAA : 60000008
L_00B0EE:
    move.l #$00000000,d3                              ; +$0AAE : 263C00000000
L_00B0F4:
    lea 256(a7),a7                                    ; +$0AB4 : 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0AB8 : 4CDF77F7
    moveq #0,d2                                       ; +$0ABC : 7400
    rts                                               ; +$0ABE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 68 : aga c block draw --------
Entry_68:
Aga_C_Block_Draw:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -384(a7),a7                                   ; +$0004 : 4FEFFE80
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l #$00000000,72(a2)                          ; +$000C : 257C000000000048
    move.l (a3)+,d7                                   ; +$0014 : 2E1B
    move.l d7,12(a2)                                  ; +$0016 : 2547000C
    move.l (a3)+,d7                                   ; +$001A : 2E1B
    move.l d7,16(a2)                                  ; +$001C : 25470010
    move.l (a3)+,d7                                   ; +$0020 : 2E1B
    move.l d7,20(a2)                                  ; +$0022 : 25470014
    move.l #$00000000,d3                              ; +$0026 : 263C00000000
    move.l (a2),d0                                    ; +$002C : 2012
    tst.l d0                                          ; +$002E : 4A80
    bmi.w L_00B742                                    ; +$0030 : 6B00060C
    cmpi.l #$00000002,d0                              ; +$0034 : 0C8000000002
    bhi.w L_00B742                                    ; +$003A : 62000602
    move.l 20(a2),d0                                  ; +$003E : 202A0014
    cmpi.l #$00000005,d0                              ; +$0042 : 0C8000000005
    bcs.w L_00B742                                    ; +$0048 : 650005F4
    cmpi.l #$0000FFFF,d0                              ; +$004C : 0C800000FFFF
    bhi.w L_00B742                                    ; +$0052 : 620005EA
    movea.l 456(a5),a4                                ; +$0056 : 286D01C8
    move.l a4,d0                                      ; +$005A : 200C
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_00B742                                    ; +$005E : 670005DE
    move.l a4,32(a2)                                  ; +$0062 : 254C0020
    move.l (a4),d0                                    ; +$0066 : 2014
    tst.l d0                                          ; +$0068 : 4A80
    beq.w L_00B742                                    ; +$006A : 670005D2
    move.l 8(a4),d0                                   ; +$006E : 202C0008
    tst.l d0                                          ; +$0072 : 4A80
    beq.w L_00B742                                    ; +$0074 : 670005C8
    move.l 32(a4),d0                                  ; +$0078 : 202C0020
    tst.l d0                                          ; +$007C : 4A80
    beq.w L_00B742                                    ; +$007E : 670005BE
    move.l 8(a4),d0                                   ; +$0082 : 202C0008
    move.l d0,44(a2)                                  ; +$0086 : 2540002C
    move.l 12(a4),d0                                  ; +$008A : 202C000C
    tst.l d0                                          ; +$008E : 4A80
    ble.w L_00B742                                    ; +$0090 : 6F0005AC
    cmpi.l #$00001000,d0                              ; +$0094 : 0C8000001000
    bhi.w L_00B742                                    ; +$009A : 620005A2
    move.l d0,48(a2)                                  ; +$009E : 25400030
    move.l 16(a4),d0                                  ; +$00A2 : 202C0010
    tst.l d0                                          ; +$00A6 : 4A80
    ble.w L_00B742                                    ; +$00A8 : 6F000594
    cmpi.l #$00001000,d0                              ; +$00AC : 0C8000001000
    bhi.w L_00B742                                    ; +$00B2 : 6200058A
    move.l d0,52(a2)                                  ; +$00B6 : 25400034
    move.l 28(a4),d0                                  ; +$00BA : 202C001C
    tst.l d0                                          ; +$00BE : 4A80
    ble.w L_00B742                                    ; +$00C0 : 6F00057C
    cmpi.l #$00000008,d0                              ; +$00C4 : 0C8000000008
    bhi.w L_00B742                                    ; +$00CA : 62000572
    move.l d0,56(a2)                                  ; +$00CE : 25400038
    movea.l 32(a4),a4                                 ; +$00D2 : 286C0020
    move.l a4,36(a2)                                  ; +$00D6 : 254C0024
    move.l 8(a4),d0                                   ; +$00DA : 202C0008
    tst.l d0                                          ; +$00DE : 4A80
    beq.w L_00B1FC                                    ; +$00E0 : 67000016
    cmpi.l #$00000001,d0                              ; +$00E4 : 0C8000000001
    bne.w L_00B742                                    ; +$00EA : 66000552
    movea.l 36(a2),a4                                 ; +$00EE : 286A0024
    movea.l (a4),a1                                   ; +$00F2 : 2254
    bra.w L_00B204                                    ; +$00F4 : 6000000A
L_00B1FC:
    movea.l 36(a2),a4                                 ; +$00F8 : 286A0024
    movea.l 4(a4),a1                                  ; +$00FC : 226C0004
L_00B204:
    move.l a1,d0                                      ; +$0100 : 2009
    tst.l d0                                          ; +$0102 : 4A80
    beq.w L_00B742                                    ; +$0104 : 67000538
    movea.l (a1),a0                                   ; +$0108 : 2051
    move.l a0,d0                                      ; +$010A : 2008
    tst.l d0                                          ; +$010C : 4A80
    beq.w L_00B742                                    ; +$010E : 6700052E
    move.l a0,40(a2)                                  ; +$0112 : 25480028
    move.l #$00000000,d0                              ; +$0116 : 203C00000000
    move.w (a0),d0                                    ; +$011C : 3010
    tst.l d0                                          ; +$011E : 4A80
    ble.w L_00B742                                    ; +$0120 : 6F00051C
    move.l d0,d1                                      ; +$0124 : 2200
    andi.l #$00000001,d1                              ; +$0126 : 028100000001
    bne.w L_00B742                                    ; +$012C : 66000510
    move.l d0,76(a2)                                  ; +$0130 : 2540004C
    lsl.l #3,d0                                       ; +$0134 : E788
    cmp.l 48(a2),d0                                   ; +$0136 : B0AA0030
    bcs.w L_00B742                                    ; +$013A : 65000502
    move.l #$00000000,d0                              ; +$013E : 203C00000000
    move.w 2(a0),d0                                   ; +$0144 : 30280002
    cmp.l 52(a2),d0                                   ; +$0148 : B0AA0034
    bcs.w L_00B742                                    ; +$014C : 650004F0
    move.l #$00000000,d0                              ; +$0150 : 203C00000000
    move.b 5(a0),d0                                   ; +$0156 : 10280005
    cmp.l 56(a2),d0                                   ; +$015A : B0AA0038
    bne.w L_00B742                                    ; +$015E : 660004DE
    move.l 20(a2),d0                                  ; +$0162 : 202A0014
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,24(a2)                                  ; +$016C : 25480018
    move.l 24(a2),d0                                  ; +$0170 : 202A0018
    tst.l d0                                          ; +$0174 : 4A80
    beq.w L_00B742                                    ; +$0176 : 670004C6
    movea.l d0,a1                                     ; +$017A : 2240
    movea.l $0004.w,a6                                ; +$017C : 2C780004
    jsr -534(a6)                                      ; +$0180 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0184 : 028000000002
    beq.w L_00B742                                    ; +$018A : 670004B2
    move.l 24(a2),d0                                  ; +$018E : 202A0018
    addi.l #$00000027,d0                              ; +$0192 : 068000000027
    bcs.w L_00B742                                    ; +$0198 : 650004A4
    movea.l d0,a1                                     ; +$019C : 2240
    movea.l $0004.w,a6                                ; +$019E : 2C780004
    jsr -534(a6)                                      ; +$01A2 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$01A6 : 028000000002
    beq.w L_00B742                                    ; +$01AC : 67000490
    movea.l 24(a2),a0                                 ; +$01B0 : 206A0018
    move.l 24(a0),d0                                  ; +$01B4 : 20280018
    move.l d0,8(a2)                                   ; +$01B8 : 25400008
    move.l 28(a0),d0                                  ; +$01BC : 2028001C
    move.l d0,4(a2)                                   ; +$01C0 : 25400004
    move.l 8(a2),d0                                   ; +$01C4 : 202A0008
    tst.l d0                                          ; +$01C8 : 4A80
    ble.w L_00B742                                    ; +$01CA : 6F000472
    cmpi.l #$00001000,d0                              ; +$01CE : 0C8000001000
    bhi.w L_00B742                                    ; +$01D4 : 62000468
    move.l 4(a2),d0                                   ; +$01D8 : 202A0004
    tst.l d0                                          ; +$01DC : 4A80
    ble.w L_00B742                                    ; +$01DE : 6F00045E
    cmpi.l #$00001000,d0                              ; +$01E2 : 0C8000001000
    bhi.w L_00B742                                    ; +$01E8 : 62000454
    move.l 16(a2),d0                                  ; +$01EC : 202A0010
    tst.l d0                                          ; +$01F0 : 4A80
    bmi.w L_00B742                                    ; +$01F2 : 6B00044A
    cmpi.l #$00007FFF,d0                              ; +$01F6 : 0C8000007FFF
    bhi.w L_00B742                                    ; +$01FC : 62000440
    move.l 12(a2),d0                                  ; +$0200 : 202A000C
    tst.l d0                                          ; +$0204 : 4A80
    bmi.w L_00B742                                    ; +$0206 : 6B000436
    cmpi.l #$00007FFF,d0                              ; +$020A : 0C8000007FFF
    bhi.w L_00B742                                    ; +$0210 : 6200042C
    move.l (a2),d1                                    ; +$0214 : 2212
    cmpi.l #$00000001,d1                              ; +$0216 : 0C8100000001
    beq.w L_00B32E                                    ; +$021C : 6700000C
    move.l #$00000007,d1                              ; +$0220 : 223C00000007
    bra.w L_00B334                                    ; +$0226 : 60000008
L_00B32E:
    move.l #$0000000F,d1                              ; +$022A : 223C0000000F
L_00B334:
    move.l 16(a2),d0                                  ; +$0230 : 202A0010
    and.l d1,d0                                       ; +$0234 : C081
    bne.w L_00B742                                    ; +$0236 : 66000406
    move.l 8(a2),d0                                   ; +$023A : 202A0008
    and.l d1,d0                                       ; +$023E : C081
    bne.w L_00B742                                    ; +$0240 : 660003FC
    move.l 16(a2),d0                                  ; +$0244 : 202A0010
    move.l 8(a2),d1                                   ; +$0248 : 222A0008
    add.l d1,d0                                       ; +$024C : D081
    bcs.w L_00B742                                    ; +$024E : 650003EE
    cmp.l 48(a2),d0                                   ; +$0252 : B0AA0030
    bhi.w L_00B742                                    ; +$0256 : 620003E6
    move.l 12(a2),d0                                  ; +$025A : 202A000C
    move.l 4(a2),d1                                   ; +$025E : 222A0004
    add.l d1,d0                                       ; +$0262 : D081
    bcs.w L_00B742                                    ; +$0264 : 650003D8
    cmp.l 52(a2),d0                                   ; +$0268 : B0AA0034
    bhi.w L_00B742                                    ; +$026C : 620003D0
    move.l 8(a2),d0                                   ; +$0270 : 202A0008
    addi.l #$0000000F,d0                              ; +$0274 : 06800000000F
    bcs.w L_00B742                                    ; +$027A : 650003C2
    lsr.l #4,d0                                       ; +$027E : E888
    lsl.l #1,d0                                       ; +$0280 : E388
    move.l d0,60(a2)                                  ; +$0282 : 2540003C
    move.l 4(a2),d1                                   ; +$0286 : 222A0004
    mulu.w d1,d0                                      ; +$028A : C0C1
    move.l d0,64(a2)                                  ; +$028C : 25400040
    move.l 56(a2),d5                                  ; +$0290 : 2A2A0038
    move.l #$00000028,d0                              ; +$0294 : 203C00000028
L_00B39E:
    move.l 64(a2),d1                                  ; +$029A : 222A0040
    add.l d1,d0                                       ; +$029E : D081
    bcs.w L_00B742                                    ; +$02A0 : 6500039C
    subq.l #1,d5                                      ; +$02A4 : 5385
    bne.w L_00B39E                                    ; +$02A6 : 6600FFF2
    cmpi.l #$00100000,d0                              ; +$02AA : 0C8000100000
    bhi.w L_00B742                                    ; +$02B0 : 6200038C
    move.l d0,68(a2)                                  ; +$02B4 : 25400044
    move.l 24(a2),d5                                  ; +$02B8 : 2A2A0018
    cmpi.l #$00000018,d5                              ; +$02BC : 0C8500000018
    bls.w L_00B742                                    ; +$02C2 : 6300037A
    move.l d5,d0                                      ; +$02C6 : 2005
    andi.l #$00000001,d0                              ; +$02C8 : 028000000001
    bne.w L_00B742                                    ; +$02CE : 6600036E
    movea.l d5,a1                                     ; +$02D2 : 2245
    movea.l $0004.w,a6                                ; +$02D4 : 2C780004
    jsr -534(a6)                                      ; +$02D8 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02DC : 028000000002
    beq.w L_00B742                                    ; +$02E2 : 6700035A
    move.l 24(a2),d0                                  ; +$02E6 : 202A0018
    subi.l #$00000018,d0                              ; +$02EA : 048000000018
    movea.l d0,a1                                     ; +$02F0 : 2240
    movea.l $0004.w,a6                                ; +$02F2 : 2C780004
    jsr -534(a6)                                      ; +$02F6 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02FA : 028000000002
    beq.w L_00B742                                    ; +$0300 : 6700033C
    movea.l 24(a2),a0                                 ; +$0304 : 206A0018
    move.l -20(a0),d4                                 ; +$0308 : 2828FFEC
    cmpi.l #$00000038,d4                              ; +$030C : 0C8400000038
    bcs.w L_00B742                                    ; +$0312 : 6500032A
    subi.l #$00000010,d4                              ; +$0316 : 048400000010
    cmpi.l #$00100000,d4                              ; +$031C : 0C8400100000
    bhi.w L_00B742                                    ; +$0322 : 6200031A
    move.l d4,28(a2)                                  ; +$0326 : 2544001C
    move.l 24(a2),d0                                  ; +$032A : 202A0018
    add.l d4,d0                                       ; +$032E : D084
    bcs.w L_00B742                                    ; +$0330 : 6500030C
    subq.l #1,d0                                      ; +$0334 : 5380
    movea.l d0,a1                                     ; +$0336 : 2240
    movea.l $0004.w,a6                                ; +$0338 : 2C780004
    jsr -534(a6)                                      ; +$033C : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0340 : 028000000002
    beq.w L_00B742                                    ; +$0346 : 670002F6
    movea.l 24(a2),a0                                 ; +$034A : 206A0018
    move.l -16(a0),d0                                 ; +$034E : 2028FFF0
    move.l 20(a2),d1                                  ; +$0352 : 222A0014
    cmp.l d1,d0                                       ; +$0356 : B081
    bne.w L_00B742                                    ; +$0358 : 660002E4
    move.l #$00000000,d0                              ; +$035C : 203C00000000
    move.w -12(a0),d0                                 ; +$0362 : 3028FFF4
    tst.l d0                                          ; +$0366 : 4A80
    beq.w L_00B47C                                    ; +$0368 : 6700000E
    andi.w #$FFFD,d0                                  ; +$036C : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0370 : 0C400001
    bne.w L_00B742                                    ; +$0374 : 660002C8
L_00B47C:
    move.l -8(a0),d0                                  ; +$0378 : 2028FFF8
    cmpi.l #$41474143,d0                              ; +$037C : 0C8041474143
    bne.w L_00B742                                    ; +$0382 : 660002BA
    move.l -4(a0),d0                                  ; +$0386 : 2028FFFC
    cmpi.l #$424C4B20,d0                              ; +$038A : 0C80424C4B20
    bne.w L_00B742                                    ; +$0390 : 660002AC
    move.l (a0),d0                                    ; +$0394 : 2010
    cmpi.l #$41474143,d0                              ; +$0396 : 0C8041474143
    bne.w L_00B742                                    ; +$039C : 660002A0
    move.l 4(a0),d0                                   ; +$03A0 : 20280004
    cmpi.l #$424C4B31,d0                              ; +$03A4 : 0C80424C4B31
    bne.w L_00B742                                    ; +$03AA : 66000292
    move.l #$00000000,d0                              ; +$03AE : 203C00000000
    move.w 8(a0),d0                                   ; +$03B4 : 30280008
    cmpi.l #$00000028,d0                              ; +$03B8 : 0C8000000028
    bne.w L_00B742                                    ; +$03BE : 6600027E
    move.l #$00000000,d0                              ; +$03C2 : 203C00000000
    move.w 10(a0),d0                                  ; +$03C8 : 3028000A
    cmpi.l #$00000001,d0                              ; +$03CC : 0C8000000001
    bne.w L_00B742                                    ; +$03D2 : 6600026A
    move.l #$00000000,d0                              ; +$03D6 : 203C00000000
    move.w 14(a0),d0                                  ; +$03DC : 3028000E
    cmpi.l #$00000000,d0                              ; +$03E0 : 0C8000000000
    bne.w L_00B742                                    ; +$03E6 : 66000256
    move.l #$00000000,d0                              ; +$03EA : 203C00000000
    move.w 12(a0),d0                                  ; +$03F0 : 3028000C
    cmp.l 56(a2),d0                                   ; +$03F4 : B0AA0038
    bne.w L_00B742                                    ; +$03F8 : 66000244
    movea.l 24(a2),a0                                 ; +$03FC : 206A0018
    move.l 24(a0),d0                                  ; +$0400 : 20280018
    cmp.l 8(a2),d0                                    ; +$0404 : B0AA0008
    bne.w L_00B742                                    ; +$0408 : 66000234
    movea.l 24(a2),a0                                 ; +$040C : 206A0018
    move.l 28(a0),d0                                  ; +$0410 : 2028001C
    cmp.l 4(a2),d0                                    ; +$0414 : B0AA0004
    bne.w L_00B742                                    ; +$0418 : 66000224
    movea.l 24(a2),a0                                 ; +$041C : 206A0018
    move.l 32(a0),d0                                  ; +$0420 : 20280020
    cmp.l 60(a2),d0                                   ; +$0424 : B0AA003C
    bne.w L_00B742                                    ; +$0428 : 66000214
    movea.l 24(a2),a0                                 ; +$042C : 206A0018
    move.l 36(a0),d0                                  ; +$0430 : 20280024
    cmp.l 64(a2),d0                                   ; +$0434 : B0AA0040
    bne.w L_00B742                                    ; +$0438 : 66000204
    move.l 28(a2),d0                                  ; +$043C : 202A001C
    cmp.l 68(a2),d0                                   ; +$0440 : B0AA0044
    bne.w L_00B742                                    ; +$0444 : 660001F8
    move.l 12(a2),d0                                  ; +$0448 : 202A000C
    move.l 76(a2),d1                                  ; +$044C : 222A004C
    mulu.w d1,d0                                      ; +$0450 : C0C1
    move.l 16(a2),d1                                  ; +$0452 : 222A0010
    lsr.l #3,d1                                       ; +$0456 : E689
    add.l d1,d0                                       ; +$0458 : D081
    bcs.w L_00B742                                    ; +$045A : 650001E2
    move.l d0,80(a2)                                  ; +$045E : 25400050
    move.l 12(a2),d0                                  ; +$0462 : 202A000C
    move.l 4(a2),d1                                   ; +$0466 : 222A0004
    add.l d1,d0                                       ; +$046A : D081
    bcs.w L_00B742                                    ; +$046C : 650001D0
    subq.l #1,d0                                      ; +$0470 : 5380
    move.l 76(a2),d1                                  ; +$0472 : 222A004C
    mulu.w d1,d0                                      ; +$0476 : C0C1
    move.l 16(a2),d1                                  ; +$0478 : 222A0010
    move.l 8(a2),d4                                   ; +$047C : 282A0008
    add.l d4,d1                                       ; +$0480 : D284
    bcs.w L_00B742                                    ; +$0482 : 650001BA
    subq.l #1,d1                                      ; +$0486 : 5381
    lsr.l #3,d1                                       ; +$0488 : E689
    add.l d1,d0                                       ; +$048A : D081
    bcs.w L_00B742                                    ; +$048C : 650001B0
    move.l d0,84(a2)                                  ; +$0490 : 25400054
    movea.l 40(a2),a4                                 ; +$0494 : 286A0028
    addq.l #8,a4                                      ; +$0498 : 508C
    move.l 56(a2),d5                                  ; +$049A : 2A2A0038
L_00B5A2:
    move.l (a4)+,d7                                   ; +$049E : 2E1C
    tst.l d7                                          ; +$04A0 : 4A87
    beq.w L_00B742                                    ; +$04A2 : 6700019A
    cmpi.l #$FFFFFFFF,d7                              ; +$04A6 : 0C87FFFFFFFF
    beq.w L_00B742                                    ; +$04AC : 67000190
    move.l d7,d0                                      ; +$04B0 : 2007
    andi.l #$00000001,d0                              ; +$04B2 : 028000000001
    bne.w L_00B742                                    ; +$04B8 : 66000184
    move.l 80(a2),d0                                  ; +$04BC : 202A0050
    add.l d7,d0                                       ; +$04C0 : D087
    bcs.w L_00B742                                    ; +$04C2 : 6500017A
    movea.l d0,a1                                     ; +$04C6 : 2240
    movea.l $0004.w,a6                                ; +$04C8 : 2C780004
    jsr -534(a6)                                      ; +$04CC : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$04D0 : 028000000002
    beq.w L_00B742                                    ; +$04D6 : 67000166
    move.l 84(a2),d0                                  ; +$04DA : 202A0054
    add.l d7,d0                                       ; +$04DE : D087
    bcs.w L_00B742                                    ; +$04E0 : 6500015C
    movea.l d0,a1                                     ; +$04E4 : 2240
    movea.l $0004.w,a6                                ; +$04E6 : 2C780004
    jsr -534(a6)                                      ; +$04EA : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$04EE : 028000000002
    beq.w L_00B742                                    ; +$04F4 : 67000148
    subq.l #1,d5                                      ; +$04F8 : 5385
    bne.w L_00B5A2                                    ; +$04FA : 6600FFA2
    move.l #$00000000,260(a2)                         ; +$04FE : 257C000000000104
    move.l #$00000000,264(a2)                         ; +$0506 : 257C000000000108
    move.l #$00000000,268(a2)                         ; +$050E : 257C00000000010C
    move.l #$00000000,272(a2)                         ; +$0516 : 257C000000000110
    move.l #$00000000,276(a2)                         ; +$051E : 257C000000000114
    move.l #$00000000,280(a2)                         ; +$0526 : 257C000000000118
    move.l #$00000000,284(a2)                         ; +$052E : 257C00000000011C
    move.l #$00000000,288(a2)                         ; +$0536 : 257C000000000120
    move.l #$00000000,292(a2)                         ; +$053E : 257C000000000124
    move.l 60(a2),d0                                  ; +$0546 : 202A003C
    move.w d0,256(a2)                                 ; +$054A : 35400100
    move.l 4(a2),d0                                   ; +$054E : 202A0004
    move.w d0,258(a2)                                 ; +$0552 : 35400102
    move.l 56(a2),d0                                  ; +$0556 : 202A0038
    move.b d0,261(a2)                                 ; +$055A : 15400105
    lea 264(a2),a4                                    ; +$055E : 49EA0108
    move.l 24(a2),d6                                  ; +$0562 : 2C2A0018
    addi.l #$00000028,d6                              ; +$0566 : 068600000028
    move.l 64(a2),d7                                  ; +$056C : 2E2A0040
    move.l 56(a2),d5                                  ; +$0570 : 2A2A0038
L_00B678:
    movea.l d6,a1                                     ; +$0574 : 2246
    movea.l $0004.w,a6                                ; +$0576 : 2C780004
    jsr -534(a6)                                      ; +$057A : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$057E : 028000000002
    beq.w L_00B742                                    ; +$0584 : 670000B8
    move.l d6,d0                                      ; +$0588 : 2006
    add.l d7,d0                                       ; +$058A : D087
    bcs.w L_00B742                                    ; +$058C : 650000B0
    subq.l #1,d0                                      ; +$0590 : 5380
    movea.l d0,a1                                     ; +$0592 : 2240
    movea.l $0004.w,a6                                ; +$0594 : 2C780004
    jsr -534(a6)                                      ; +$0598 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$059C : 028000000002
    beq.w L_00B742                                    ; +$05A2 : 6700009A
    move.l d6,(a4)+                                   ; +$05A6 : 28C6
    add.l d7,d6                                       ; +$05A8 : DC87
    bcs.w L_00B742                                    ; +$05AA : 65000092
    subq.l #1,d5                                      ; +$05AE : 5385
    bne.w L_00B678                                    ; +$05B0 : 6600FFC2
    movea.l 36(a2),a4                                 ; +$05B4 : 286A0024
    move.l 20(a4),d0                                  ; +$05B8 : 202C0014
    andi.l #$00000001,d0                              ; +$05BC : 028000000001
    beq.w L_00B6FA                                    ; +$05C2 : 67000032
    movea.l 36(a2),a4                                 ; +$05C6 : 286A0024
    movea.l 12(a4),a0                                 ; +$05CA : 206C000C
    move.l a0,d0                                      ; +$05CE : 2008
    tst.l d0                                          ; +$05D0 : 4A80
    beq.w L_00B742                                    ; +$05D2 : 6700006A
    movea.l $0004.w,a6                                ; +$05D6 : 2C780004
    jsr -372(a6)                                      ; +$05DA : 4EAEFE8C
    tst.l d0                                          ; +$05DE : 4A80
    beq.w L_00B742                                    ; +$05E0 : 6700005C
    movea.l 36(a2),a4                                 ; +$05E4 : 286A0024
    move.l 20(a4),d0                                  ; +$05E8 : 202C0014
    andi.l #$FFFFFFFE,d0                              ; +$05EC : 0280FFFFFFFE
    move.l d0,20(a4)                                  ; +$05F2 : 29400014
L_00B6FA:
    movea.l 44(a2),a6                                 ; +$05F6 : 2C6A002C
    jsr -228(a6)                                      ; +$05FA : 4EAEFF1C
    lea 256(a2),a0                                    ; +$05FE : 41EA0100
    movea.l 40(a2),a1                                 ; +$0602 : 226A0028
    move.l #$00000000,d0                              ; +$0606 : 203C00000000
    move.l #$00000000,d1                              ; +$060C : 223C00000000
    move.l 16(a2),d2                                  ; +$0612 : 242A0010
    move.l 12(a2),d3                                  ; +$0616 : 262A000C
    move.l 8(a2),d4                                   ; +$061A : 282A0008
    move.l 4(a2),d5                                   ; +$061E : 2A2A0004
    move.l (a2),d6                                    ; +$0622 : 2C12
    movea.l 44(a2),a6                                 ; +$0624 : 2C6A002C
    lea L_00B75C(pc),a4                               ; +$0628 : 49FA002E
    jsr (a4)                                          ; +$062C : 4E94
    tst.l d3                                          ; +$062E : 4A83
    beq.w L_00B742                                    ; +$0630 : 6700000C
    move.l #$00000001,d3                              ; +$0634 : 263C00000001
    bra.w L_00B748                                    ; +$063A : 60000008
L_00B742:
    move.l #$00000000,d3                              ; +$063E : 263C00000000
L_00B748:
    lea 384(a7),a7                                    ; +$0644 : 4FEF0180
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$0648 : 4CDF77F7
    moveq #0,d2                                       ; +$064C : 7400
    rts                                               ; +$064E : 4E75
    dc.b "AGACBLK "
L_00B75C:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0658 : 48E7EFEE
    lea -256(a7),a7                                   ; +$065C : 4FEFFF00
    movea.l a7,a4                                     ; +$0660 : 284F
    move.l a0,(a4)                                    ; +$0662 : 2888
    move.l a1,4(a4)                                   ; +$0664 : 29490004
    move.l a6,36(a4)                                  ; +$0668 : 294E0024
    move.l d0,8(a4)                                   ; +$066C : 29400008
    move.l d1,12(a4)                                  ; +$0670 : 2941000C
    move.l d2,16(a4)                                  ; +$0674 : 29420010
    move.l d3,20(a4)                                  ; +$0678 : 29430014
    move.l d4,24(a4)                                  ; +$067C : 29440018
    move.l d5,28(a4)                                  ; +$0680 : 2945001C
    move.l d6,32(a4)                                  ; +$0684 : 29460020
    move.l #$00000000,d3                              ; +$0688 : 263C00000000
    move.l (a4),d0                                    ; +$068E : 2014
    tst.l d0                                          ; +$0690 : 4A80
    beq.w L_00BAB2                                    ; +$0692 : 6700031A
    andi.l #$00000001,d0                              ; +$0696 : 028000000001
    bne.w L_00BAB2                                    ; +$069C : 66000310
    move.l 4(a4),d0                                   ; +$06A0 : 202C0004
    tst.l d0                                          ; +$06A4 : 4A80
    beq.w L_00BAB2                                    ; +$06A6 : 67000306
    andi.l #$00000001,d0                              ; +$06AA : 028000000001
    bne.w L_00BAB2                                    ; +$06B0 : 660002FC
    move.l 32(a4),d0                                  ; +$06B4 : 202C0020
    cmpi.l #$00000002,d0                              ; +$06B8 : 0C8000000002
    bhi.w L_00BAB2                                    ; +$06BE : 620002EE
    tst.l d0                                          ; +$06C2 : 4A80
    bmi.w L_00BAB2                                    ; +$06C4 : 6B0002E8
    move.l 8(a4),d0                                   ; +$06C8 : 202C0008
    tst.l d0                                          ; +$06CC : 4A80
    bmi.w L_00BAB2                                    ; +$06CE : 6B0002DE
    cmpi.l #$00007FFF,d0                              ; +$06D2 : 0C8000007FFF
    bgt.w L_00BAB2                                    ; +$06D8 : 6E0002D4
    move.l 12(a4),d0                                  ; +$06DC : 202C000C
    tst.l d0                                          ; +$06E0 : 4A80
    bmi.w L_00BAB2                                    ; +$06E2 : 6B0002CA
    cmpi.l #$00007FFF,d0                              ; +$06E6 : 0C8000007FFF
    bgt.w L_00BAB2                                    ; +$06EC : 6E0002C0
    move.l 16(a4),d0                                  ; +$06F0 : 202C0010
    tst.l d0                                          ; +$06F4 : 4A80
    bmi.w L_00BAB2                                    ; +$06F6 : 6B0002B6
    cmpi.l #$00007FFF,d0                              ; +$06FA : 0C8000007FFF
    bgt.w L_00BAB2                                    ; +$0700 : 6E0002AC
    move.l 20(a4),d0                                  ; +$0704 : 202C0014
    tst.l d0                                          ; +$0708 : 4A80
    bmi.w L_00BAB2                                    ; +$070A : 6B0002A2
    cmpi.l #$00007FFF,d0                              ; +$070E : 0C8000007FFF
    bgt.w L_00BAB2                                    ; +$0714 : 6E000298
    move.l 24(a4),d0                                  ; +$0718 : 202C0018
    tst.l d0                                          ; +$071C : 4A80
    ble.w L_00BAB2                                    ; +$071E : 6F00028E
    cmpi.l #$00001000,d0                              ; +$0722 : 0C8000001000
    bgt.w L_00BAB2                                    ; +$0728 : 6E000284
    move.l 28(a4),d0                                  ; +$072C : 202C001C
    tst.l d0                                          ; +$0730 : 4A80
    ble.w L_00BAB2                                    ; +$0732 : 6F00027A
    cmpi.l #$00001000,d0                              ; +$0736 : 0C8000001000
    bgt.w L_00BAB2                                    ; +$073C : 6E000270
    move.l 32(a4),d1                                  ; +$0740 : 222C0020
    cmpi.l #$00000001,d1                              ; +$0744 : 0C8100000001
    beq.w L_00B85C                                    ; +$074A : 6700000C
    move.l #$00000007,d1                              ; +$074E : 223C00000007
    bra.w L_00B862                                    ; +$0754 : 60000008
L_00B85C:
    move.l #$0000000F,d1                              ; +$0758 : 223C0000000F
L_00B862:
    move.l 8(a4),d0                                   ; +$075E : 202C0008
    and.l d1,d0                                       ; +$0762 : C081
    bne.w L_00BAB2                                    ; +$0764 : 66000248
    move.l 16(a4),d0                                  ; +$0768 : 202C0010
    and.l d1,d0                                       ; +$076C : C081
    bne.w L_00BAB2                                    ; +$076E : 6600023E
    move.l 24(a4),d0                                  ; +$0772 : 202C0018
    and.l d1,d0                                       ; +$0776 : C081
    bne.w L_00BAB2                                    ; +$0778 : 66000234
    movea.l (a4),a0                                   ; +$077C : 2054
    move.l #$00000000,d0                              ; +$077E : 203C00000000
    move.w (a0),d0                                    ; +$0784 : 3010
    move.l d0,40(a4)                                  ; +$0786 : 29400028
    tst.l d0                                          ; +$078A : 4A80
    ble.w L_00BAB2                                    ; +$078C : 6F000220
    andi.l #$00000001,d0                              ; +$0790 : 028000000001
    bne.w L_00BAB2                                    ; +$0796 : 66000216
    move.l #$00000000,d0                              ; +$079A : 203C00000000
    move.w 2(a0),d0                                   ; +$07A0 : 30280002
    move.l d0,68(a4)                                  ; +$07A4 : 29400044
    tst.l d0                                          ; +$07A8 : 4A80
    ble.w L_00BAB2                                    ; +$07AA : 6F000202
    move.l #$00000000,d0                              ; +$07AE : 203C00000000
    move.b 5(a0),d0                                   ; +$07B4 : 10280005
    tst.l d0                                          ; +$07B8 : 4A80
    ble.w L_00BAB2                                    ; +$07BA : 6F0001F2
    cmpi.l #$00000008,d0                              ; +$07BE : 0C8000000008
    bgt.w L_00BAB2                                    ; +$07C4 : 6E0001E8
    move.l d0,48(a4)                                  ; +$07C8 : 29400030
    movea.l 4(a4),a0                                  ; +$07CC : 206C0004
    move.l #$00000000,d0                              ; +$07D0 : 203C00000000
    move.w (a0),d0                                    ; +$07D6 : 3010
    move.l d0,44(a4)                                  ; +$07D8 : 2940002C
    tst.l d0                                          ; +$07DC : 4A80
    ble.w L_00BAB2                                    ; +$07DE : 6F0001CE
    andi.l #$00000001,d0                              ; +$07E2 : 028000000001
    bne.w L_00BAB2                                    ; +$07E8 : 660001C4
    move.l #$00000000,d0                              ; +$07EC : 203C00000000
    move.w 2(a0),d0                                   ; +$07F2 : 30280002
    move.l d0,72(a4)                                  ; +$07F6 : 29400048
    tst.l d0                                          ; +$07FA : 4A80
    ble.w L_00BAB2                                    ; +$07FC : 6F0001B0
    move.l #$00000000,d0                              ; +$0800 : 203C00000000
    move.b 5(a0),d0                                   ; +$0806 : 10280005
    tst.l d0                                          ; +$080A : 4A80
    ble.w L_00BAB2                                    ; +$080C : 6F0001A0
    cmpi.l #$00000008,d0                              ; +$0810 : 0C8000000008
    bgt.w L_00BAB2                                    ; +$0816 : 6E000196
    cmp.l 48(a4),d0                                   ; +$081A : B0AC0030
    bne.w L_00BAB2                                    ; +$081E : 6600018E
    move.l 8(a4),d0                                   ; +$0822 : 202C0008
    move.l 24(a4),d1                                  ; +$0826 : 222C0018
    add.l d1,d0                                       ; +$082A : D081
    move.l 40(a4),d1                                  ; +$082C : 222C0028
    lsl.l #3,d1                                       ; +$0830 : E789
    cmp.l d1,d0                                       ; +$0832 : B081
    bhi.w L_00BAB2                                    ; +$0834 : 62000178
    move.l 12(a4),d0                                  ; +$0838 : 202C000C
    move.l 28(a4),d1                                  ; +$083C : 222C001C
    add.l d1,d0                                       ; +$0840 : D081
    cmp.l 68(a4),d0                                   ; +$0842 : B0AC0044
    bhi.w L_00BAB2                                    ; +$0846 : 62000166
    move.l 16(a4),d0                                  ; +$084A : 202C0010
    move.l 24(a4),d1                                  ; +$084E : 222C0018
    add.l d1,d0                                       ; +$0852 : D081
    move.l 44(a4),d1                                  ; +$0854 : 222C002C
    lsl.l #3,d1                                       ; +$0858 : E789
    cmp.l d1,d0                                       ; +$085A : B081
    bhi.w L_00BAB2                                    ; +$085C : 62000150
    move.l 20(a4),d0                                  ; +$0860 : 202C0014
    move.l 28(a4),d1                                  ; +$0864 : 222C001C
    add.l d1,d0                                       ; +$0868 : D081
    cmp.l 72(a4),d0                                   ; +$086A : B0AC0048
    bhi.w L_00BAB2                                    ; +$086E : 6200013E
    movea.l (a4),a5                                   ; +$0872 : 2A54
    addq.l #8,a5                                      ; +$0874 : 508D
    movea.l 4(a4),a6                                  ; +$0876 : 2C6C0004
    addq.l #8,a6                                      ; +$087A : 508E
    move.l 48(a4),d7                                  ; +$087C : 2E2C0030
L_00B984:
    move.l (a5)+,d0                                   ; +$0880 : 201D
    tst.l d0                                          ; +$0882 : 4A80
    beq.w L_00BAB2                                    ; +$0884 : 67000128
    andi.l #$00000001,d0                              ; +$0888 : 028000000001
    bne.w L_00BAB2                                    ; +$088E : 6600011E
    move.l (a6)+,d0                                   ; +$0892 : 201E
    tst.l d0                                          ; +$0894 : 4A80
    beq.w L_00BAB2                                    ; +$0896 : 67000116
    andi.l #$00000001,d0                              ; +$089A : 028000000001
    bne.w L_00BAB2                                    ; +$08A0 : 6600010C
    subq.l #1,d7                                      ; +$08A4 : 5387
    bne.w L_00B984                                    ; +$08A6 : 6600FFD8
    move.l 32(a4),d0                                  ; +$08AA : 202C0020
    cmpi.l #$00000002,d0                              ; +$08AE : 0C8000000002
    bne.w L_00BA0C                                    ; +$08B4 : 66000052
    move.l 36(a4),d0                                  ; +$08B8 : 202C0024
    tst.l d0                                          ; +$08BC : 4A80
    beq.w L_00BAB2                                    ; +$08BE : 670000EE
    movea.l 36(a4),a6                                 ; +$08C2 : 2C6C0024
    lea 128(a4),a1                                    ; +$08C6 : 43EC0080
    jsr -198(a6)                                      ; +$08CA : 4EAEFF3A
    lea 128(a4),a1                                    ; +$08CE : 43EC0080
    move.l 4(a4),4(a1)                                ; +$08D2 : 236C00040004
    movea.l (a4),a0                                   ; +$08D8 : 2054
    move.l 8(a4),d0                                   ; +$08DA : 202C0008
    move.l 12(a4),d1                                  ; +$08DE : 222C000C
    move.l 16(a4),d2                                  ; +$08E2 : 242C0010
    move.l 20(a4),d3                                  ; +$08E6 : 262C0014
    move.l 24(a4),d4                                  ; +$08EA : 282C0018
    move.l 28(a4),d5                                  ; +$08EE : 2A2C001C
    move.l #$000000C0,d6                              ; +$08F2 : 2C3C000000C0
    jsr -606(a6)                                      ; +$08F8 : 4EAEFDA2
    movea.l 36(a4),a6                                 ; +$08FC : 2C6C0024
    jsr -228(a6)                                      ; +$0900 : 4EAEFF1C
    bra.w L_00BAA8                                    ; +$0904 : 6000009E
L_00BA0C:
    move.l 24(a4),d0                                  ; +$0908 : 202C0018
    lsr.l #3,d0                                       ; +$090C : E688
    move.l d0,52(a4)                                  ; +$090E : 29400034
    move.l 40(a4),d1                                  ; +$0912 : 222C0028
    sub.l d0,d1                                       ; +$0916 : 9280
    move.l d1,56(a4)                                  ; +$0918 : 29410038
    move.l 44(a4),d1                                  ; +$091C : 222C002C
    sub.l d0,d1                                       ; +$0920 : 9280
    move.l d1,60(a4)                                  ; +$0922 : 2941003C
    movea.l (a4),a5                                   ; +$0926 : 2A54
    addq.l #8,a5                                      ; +$0928 : 508D
    movea.l 4(a4),a6                                  ; +$092A : 2C6C0004
    addq.l #8,a6                                      ; +$092E : 508E
    move.l 48(a4),d7                                  ; +$0930 : 2E2C0030
L_00BA38:
    movea.l (a5)+,a0                                  ; +$0934 : 205D
    movea.l (a6)+,a1                                  ; +$0936 : 225E
    move.l 12(a4),d0                                  ; +$0938 : 202C000C
    move.l 40(a4),d1                                  ; +$093C : 222C0028
    mulu.w d1,d0                                      ; +$0940 : C0C1
    move.l 8(a4),d1                                   ; +$0942 : 222C0008
    lsr.l #3,d1                                       ; +$0946 : E689
    add.l d1,d0                                       ; +$0948 : D081
    adda.l d0,a0                                      ; +$094A : D1C0
    move.l 20(a4),d0                                  ; +$094C : 202C0014
    move.l 44(a4),d1                                  ; +$0950 : 222C002C
    mulu.w d1,d0                                      ; +$0954 : C0C1
    move.l 16(a4),d1                                  ; +$0956 : 222C0010
    lsr.l #3,d1                                       ; +$095A : E689
    add.l d1,d0                                       ; +$095C : D081
    adda.l d0,a1                                      ; +$095E : D3C0
    move.l 28(a4),d4                                  ; +$0960 : 282C001C
L_00BA68:
    move.l 52(a4),d6                                  ; +$0964 : 2C2C0034
    move.l 32(a4),d0                                  ; +$0968 : 202C0020
    cmpi.l #$00000001,d0                              ; +$096C : 0C8000000001
    beq.w L_00BA86                                    ; +$0972 : 6700000E
L_00BA7A:
    move.b (a0)+,(a1)+                                ; +$0976 : 12D8
    subq.l #1,d6                                      ; +$0978 : 5386
    bne.w L_00BA7A                                    ; +$097A : 6600FFFA
    bra.w L_00BA90                                    ; +$097E : 6000000C
L_00BA86:
    lsr.l #1,d6                                       ; +$0982 : E28E
L_00BA88:
    move.w (a0)+,(a1)+                                ; +$0984 : 32D8
    subq.l #1,d6                                      ; +$0986 : 5386
    bne.w L_00BA88                                    ; +$0988 : 6600FFFA
L_00BA90:
    move.l 56(a4),d0                                  ; +$098C : 202C0038
    adda.l d0,a0                                      ; +$0990 : D1C0
    move.l 60(a4),d0                                  ; +$0992 : 202C003C
    adda.l d0,a1                                      ; +$0996 : D3C0
    subq.l #1,d4                                      ; +$0998 : 5384
    bne.w L_00BA68                                    ; +$099A : 6600FFC8
    subq.l #1,d7                                      ; +$099E : 5387
    bne.w L_00BA38                                    ; +$09A0 : 6600FF92
L_00BAA8:
    move.l #$00000001,d3                              ; +$09A4 : 263C00000001
    bra.w L_00BAB8                                    ; +$09AA : 60000008
L_00BAB2:
    move.l #$00000000,d3                              ; +$09AE : 263C00000000
L_00BAB8:
    lea 256(a7),a7                                    ; +$09B4 : 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$09B8 : 4CDF77F7
    moveq #0,d2                                       ; +$09BC : 7400
    rts                                               ; +$09BE : 4E75
    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code

; -------- AP20 entry 69 : aga c block restore --------
Entry_69:
Aga_C_Block_Restore:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$0000 : 48E7EFEE
    lea -384(a7),a7                                   ; +$0004 : 4FEFFE80
    movea.l a7,a2                                     ; +$0008 : 244F
    move.l d3,(a2)                                    ; +$000A : 2483
    move.l #$00000000,72(a2)                          ; +$000C : 257C000000000048
    move.l (a3)+,d7                                   ; +$0014 : 2E1B
    move.l d7,20(a2)                                  ; +$0016 : 25470014
    move.l #$00000000,d3                              ; +$001A : 263C00000000
    move.l (a2),d0                                    ; +$0020 : 2012
    tst.l d0                                          ; +$0022 : 4A80
    bmi.w L_00C10A                                    ; +$0024 : 6B00061C
    cmpi.l #$00000002,d0                              ; +$0028 : 0C8000000002
    bhi.w L_00C10A                                    ; +$002E : 62000612
    move.l 20(a2),d0                                  ; +$0032 : 202A0014
    cmpi.l #$00000005,d0                              ; +$0036 : 0C8000000005
    bcs.w L_00C10A                                    ; +$003C : 65000604
    cmpi.l #$0000FFFF,d0                              ; +$0040 : 0C800000FFFF
    bhi.w L_00C10A                                    ; +$0046 : 620005FA
    movea.l 456(a5),a4                                ; +$004A : 286D01C8
    move.l a4,d0                                      ; +$004E : 200C
    tst.l d0                                          ; +$0050 : 4A80
    beq.w L_00C10A                                    ; +$0052 : 670005EE
    move.l a4,32(a2)                                  ; +$0056 : 254C0020
    move.l (a4),d0                                    ; +$005A : 2014
    tst.l d0                                          ; +$005C : 4A80
    beq.w L_00C10A                                    ; +$005E : 670005E2
    move.l 8(a4),d0                                   ; +$0062 : 202C0008
    tst.l d0                                          ; +$0066 : 4A80
    beq.w L_00C10A                                    ; +$0068 : 670005D8
    move.l 32(a4),d0                                  ; +$006C : 202C0020
    tst.l d0                                          ; +$0070 : 4A80
    beq.w L_00C10A                                    ; +$0072 : 670005CE
    move.l 8(a4),d0                                   ; +$0076 : 202C0008
    move.l d0,44(a2)                                  ; +$007A : 2540002C
    move.l 12(a4),d0                                  ; +$007E : 202C000C
    tst.l d0                                          ; +$0082 : 4A80
    ble.w L_00C10A                                    ; +$0084 : 6F0005BC
    cmpi.l #$00001000,d0                              ; +$0088 : 0C8000001000
    bhi.w L_00C10A                                    ; +$008E : 620005B2
    move.l d0,48(a2)                                  ; +$0092 : 25400030
    move.l 16(a4),d0                                  ; +$0096 : 202C0010
    tst.l d0                                          ; +$009A : 4A80
    ble.w L_00C10A                                    ; +$009C : 6F0005A4
    cmpi.l #$00001000,d0                              ; +$00A0 : 0C8000001000
    bhi.w L_00C10A                                    ; +$00A6 : 6200059A
    move.l d0,52(a2)                                  ; +$00AA : 25400034
    move.l 28(a4),d0                                  ; +$00AE : 202C001C
    tst.l d0                                          ; +$00B2 : 4A80
    ble.w L_00C10A                                    ; +$00B4 : 6F00058C
    cmpi.l #$00000008,d0                              ; +$00B8 : 0C8000000008
    bhi.w L_00C10A                                    ; +$00BE : 62000582
    move.l d0,56(a2)                                  ; +$00C2 : 25400038
    movea.l 32(a4),a4                                 ; +$00C6 : 286C0020
    move.l a4,36(a2)                                  ; +$00CA : 254C0024
    move.l 8(a4),d0                                   ; +$00CE : 202C0008
    tst.l d0                                          ; +$00D2 : 4A80
    beq.w L_00BBB4                                    ; +$00D4 : 67000016
    cmpi.l #$00000001,d0                              ; +$00D8 : 0C8000000001
    bne.w L_00C10A                                    ; +$00DE : 66000562
    movea.l 36(a2),a4                                 ; +$00E2 : 286A0024
    movea.l (a4),a1                                   ; +$00E6 : 2254
    bra.w L_00BBBC                                    ; +$00E8 : 6000000A
L_00BBB4:
    movea.l 36(a2),a4                                 ; +$00EC : 286A0024
    movea.l 4(a4),a1                                  ; +$00F0 : 226C0004
L_00BBBC:
    move.l a1,d0                                      ; +$00F4 : 2009
    tst.l d0                                          ; +$00F6 : 4A80
    beq.w L_00C10A                                    ; +$00F8 : 67000548
    movea.l (a1),a0                                   ; +$00FC : 2051
    move.l a0,d0                                      ; +$00FE : 2008
    tst.l d0                                          ; +$0100 : 4A80
    beq.w L_00C10A                                    ; +$0102 : 6700053E
    move.l a0,40(a2)                                  ; +$0106 : 25480028
    move.l #$00000000,d0                              ; +$010A : 203C00000000
    move.w (a0),d0                                    ; +$0110 : 3010
    tst.l d0                                          ; +$0112 : 4A80
    ble.w L_00C10A                                    ; +$0114 : 6F00052C
    move.l d0,d1                                      ; +$0118 : 2200
    andi.l #$00000001,d1                              ; +$011A : 028100000001
    bne.w L_00C10A                                    ; +$0120 : 66000520
    move.l d0,76(a2)                                  ; +$0124 : 2540004C
    lsl.l #3,d0                                       ; +$0128 : E788
    cmp.l 48(a2),d0                                   ; +$012A : B0AA0030
    bcs.w L_00C10A                                    ; +$012E : 65000512
    move.l #$00000000,d0                              ; +$0132 : 203C00000000
    move.w 2(a0),d0                                   ; +$0138 : 30280002
    cmp.l 52(a2),d0                                   ; +$013C : B0AA0034
    bcs.w L_00C10A                                    ; +$0140 : 65000500
    move.l #$00000000,d0                              ; +$0144 : 203C00000000
    move.b 5(a0),d0                                   ; +$014A : 10280005
    cmp.l 56(a2),d0                                   ; +$014E : B0AA0038
    bne.w L_00C10A                                    ; +$0152 : 660004EE
    move.l 20(a2),d0                                  ; +$0156 : 202A0014
    dc.b $FE,$11,$F7,$00,$03,$1D
    move.l a0,24(a2)                                  ; +$0160 : 25480018
    move.l 24(a2),d0                                  ; +$0164 : 202A0018
    tst.l d0                                          ; +$0168 : 4A80
    beq.w L_00C10A                                    ; +$016A : 670004D6
    movea.l d0,a1                                     ; +$016E : 2240
    movea.l $0004.w,a6                                ; +$0170 : 2C780004
    jsr -534(a6)                                      ; +$0174 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0178 : 028000000002
    beq.w L_00C10A                                    ; +$017E : 670004C2
    move.l 24(a2),d0                                  ; +$0182 : 202A0018
    addi.l #$00000027,d0                              ; +$0186 : 068000000027
    bcs.w L_00C10A                                    ; +$018C : 650004B4
    movea.l d0,a1                                     ; +$0190 : 2240
    movea.l $0004.w,a6                                ; +$0192 : 2C780004
    jsr -534(a6)                                      ; +$0196 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$019A : 028000000002
    beq.w L_00C10A                                    ; +$01A0 : 670004A0
    movea.l 24(a2),a0                                 ; +$01A4 : 206A0018
    move.l 24(a0),d0                                  ; +$01A8 : 20280018
    move.l d0,8(a2)                                   ; +$01AC : 25400008
    move.l 28(a0),d0                                  ; +$01B0 : 2028001C
    move.l d0,4(a2)                                   ; +$01B4 : 25400004
    move.l 16(a0),d0                                  ; +$01B8 : 20280010
    move.l d0,16(a2)                                  ; +$01BC : 25400010
    move.l 20(a0),d0                                  ; +$01C0 : 20280014
    move.l d0,12(a2)                                  ; +$01C4 : 2540000C
    move.l 8(a2),d0                                   ; +$01C8 : 202A0008
    tst.l d0                                          ; +$01CC : 4A80
    ble.w L_00C10A                                    ; +$01CE : 6F000472
    cmpi.l #$00001000,d0                              ; +$01D2 : 0C8000001000
    bhi.w L_00C10A                                    ; +$01D8 : 62000468
    move.l 4(a2),d0                                   ; +$01DC : 202A0004
    tst.l d0                                          ; +$01E0 : 4A80
    ble.w L_00C10A                                    ; +$01E2 : 6F00045E
    cmpi.l #$00001000,d0                              ; +$01E6 : 0C8000001000
    bhi.w L_00C10A                                    ; +$01EC : 62000454
    move.l 16(a2),d0                                  ; +$01F0 : 202A0010
    tst.l d0                                          ; +$01F4 : 4A80
    bmi.w L_00C10A                                    ; +$01F6 : 6B00044A
    cmpi.l #$00007FFF,d0                              ; +$01FA : 0C8000007FFF
    bhi.w L_00C10A                                    ; +$0200 : 62000440
    move.l 12(a2),d0                                  ; +$0204 : 202A000C
    tst.l d0                                          ; +$0208 : 4A80
    bmi.w L_00C10A                                    ; +$020A : 6B000436
    cmpi.l #$00007FFF,d0                              ; +$020E : 0C8000007FFF
    bhi.w L_00C10A                                    ; +$0214 : 6200042C
    move.l (a2),d1                                    ; +$0218 : 2212
    cmpi.l #$00000001,d1                              ; +$021A : 0C8100000001
    beq.w L_00BCF6                                    ; +$0220 : 6700000C
    move.l #$00000007,d1                              ; +$0224 : 223C00000007
    bra.w L_00BCFC                                    ; +$022A : 60000008
L_00BCF6:
    move.l #$0000000F,d1                              ; +$022E : 223C0000000F
L_00BCFC:
    move.l 16(a2),d0                                  ; +$0234 : 202A0010
    and.l d1,d0                                       ; +$0238 : C081
    bne.w L_00C10A                                    ; +$023A : 66000406
    move.l 8(a2),d0                                   ; +$023E : 202A0008
    and.l d1,d0                                       ; +$0242 : C081
    bne.w L_00C10A                                    ; +$0244 : 660003FC
    move.l 16(a2),d0                                  ; +$0248 : 202A0010
    move.l 8(a2),d1                                   ; +$024C : 222A0008
    add.l d1,d0                                       ; +$0250 : D081
    bcs.w L_00C10A                                    ; +$0252 : 650003EE
    cmp.l 48(a2),d0                                   ; +$0256 : B0AA0030
    bhi.w L_00C10A                                    ; +$025A : 620003E6
    move.l 12(a2),d0                                  ; +$025E : 202A000C
    move.l 4(a2),d1                                   ; +$0262 : 222A0004
    add.l d1,d0                                       ; +$0266 : D081
    bcs.w L_00C10A                                    ; +$0268 : 650003D8
    cmp.l 52(a2),d0                                   ; +$026C : B0AA0034
    bhi.w L_00C10A                                    ; +$0270 : 620003D0
    move.l 8(a2),d0                                   ; +$0274 : 202A0008
    addi.l #$0000000F,d0                              ; +$0278 : 06800000000F
    bcs.w L_00C10A                                    ; +$027E : 650003C2
    lsr.l #4,d0                                       ; +$0282 : E888
    lsl.l #1,d0                                       ; +$0284 : E388
    move.l d0,60(a2)                                  ; +$0286 : 2540003C
    move.l 4(a2),d1                                   ; +$028A : 222A0004
    mulu.w d1,d0                                      ; +$028E : C0C1
    move.l d0,64(a2)                                  ; +$0290 : 25400040
    move.l 56(a2),d5                                  ; +$0294 : 2A2A0038
    move.l #$00000028,d0                              ; +$0298 : 203C00000028
L_00BD66:
    move.l 64(a2),d1                                  ; +$029E : 222A0040
    add.l d1,d0                                       ; +$02A2 : D081
    bcs.w L_00C10A                                    ; +$02A4 : 6500039C
    subq.l #1,d5                                      ; +$02A8 : 5385
    bne.w L_00BD66                                    ; +$02AA : 6600FFF2
    cmpi.l #$00100000,d0                              ; +$02AE : 0C8000100000
    bhi.w L_00C10A                                    ; +$02B4 : 6200038C
    move.l d0,68(a2)                                  ; +$02B8 : 25400044
    move.l 24(a2),d5                                  ; +$02BC : 2A2A0018
    cmpi.l #$00000018,d5                              ; +$02C0 : 0C8500000018
    bls.w L_00C10A                                    ; +$02C6 : 6300037A
    move.l d5,d0                                      ; +$02CA : 2005
    andi.l #$00000001,d0                              ; +$02CC : 028000000001
    bne.w L_00C10A                                    ; +$02D2 : 6600036E
    movea.l d5,a1                                     ; +$02D6 : 2245
    movea.l $0004.w,a6                                ; +$02D8 : 2C780004
    jsr -534(a6)                                      ; +$02DC : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02E0 : 028000000002
    beq.w L_00C10A                                    ; +$02E6 : 6700035A
    move.l 24(a2),d0                                  ; +$02EA : 202A0018
    subi.l #$00000018,d0                              ; +$02EE : 048000000018
    movea.l d0,a1                                     ; +$02F4 : 2240
    movea.l $0004.w,a6                                ; +$02F6 : 2C780004
    jsr -534(a6)                                      ; +$02FA : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$02FE : 028000000002
    beq.w L_00C10A                                    ; +$0304 : 6700033C
    movea.l 24(a2),a0                                 ; +$0308 : 206A0018
    move.l -20(a0),d4                                 ; +$030C : 2828FFEC
    cmpi.l #$00000038,d4                              ; +$0310 : 0C8400000038
    bcs.w L_00C10A                                    ; +$0316 : 6500032A
    subi.l #$00000010,d4                              ; +$031A : 048400000010
    cmpi.l #$00100000,d4                              ; +$0320 : 0C8400100000
    bhi.w L_00C10A                                    ; +$0326 : 6200031A
    move.l d4,28(a2)                                  ; +$032A : 2544001C
    move.l 24(a2),d0                                  ; +$032E : 202A0018
    add.l d4,d0                                       ; +$0332 : D084
    bcs.w L_00C10A                                    ; +$0334 : 6500030C
    subq.l #1,d0                                      ; +$0338 : 5380
    movea.l d0,a1                                     ; +$033A : 2240
    movea.l $0004.w,a6                                ; +$033C : 2C780004
    jsr -534(a6)                                      ; +$0340 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0344 : 028000000002
    beq.w L_00C10A                                    ; +$034A : 670002F6
    movea.l 24(a2),a0                                 ; +$034E : 206A0018
    move.l -16(a0),d0                                 ; +$0352 : 2028FFF0
    move.l 20(a2),d1                                  ; +$0356 : 222A0014
    cmp.l d1,d0                                       ; +$035A : B081
    bne.w L_00C10A                                    ; +$035C : 660002E4
    move.l #$00000000,d0                              ; +$0360 : 203C00000000
    move.w -12(a0),d0                                 ; +$0366 : 3028FFF4
    tst.l d0                                          ; +$036A : 4A80
    beq.w L_00BE44                                    ; +$036C : 6700000E
    andi.w #$FFFD,d0                                  ; +$0370 : 0240FFFD
    cmpi.w #$0001,d0                                  ; +$0374 : 0C400001
    bne.w L_00C10A                                    ; +$0378 : 660002C8
L_00BE44:
    move.l -8(a0),d0                                  ; +$037C : 2028FFF8
    cmpi.l #$41474143,d0                              ; +$0380 : 0C8041474143
    bne.w L_00C10A                                    ; +$0386 : 660002BA
    move.l -4(a0),d0                                  ; +$038A : 2028FFFC
    cmpi.l #$424C4B20,d0                              ; +$038E : 0C80424C4B20
    bne.w L_00C10A                                    ; +$0394 : 660002AC
    move.l (a0),d0                                    ; +$0398 : 2010
    cmpi.l #$41474143,d0                              ; +$039A : 0C8041474143
    bne.w L_00C10A                                    ; +$03A0 : 660002A0
    move.l 4(a0),d0                                   ; +$03A4 : 20280004
    cmpi.l #$424C4B31,d0                              ; +$03A8 : 0C80424C4B31
    bne.w L_00C10A                                    ; +$03AE : 66000292
    move.l #$00000000,d0                              ; +$03B2 : 203C00000000
    move.w 8(a0),d0                                   ; +$03B8 : 30280008
    cmpi.l #$00000028,d0                              ; +$03BC : 0C8000000028
    bne.w L_00C10A                                    ; +$03C2 : 6600027E
    move.l #$00000000,d0                              ; +$03C6 : 203C00000000
    move.w 10(a0),d0                                  ; +$03CC : 3028000A
    cmpi.l #$00000001,d0                              ; +$03D0 : 0C8000000001
    bne.w L_00C10A                                    ; +$03D6 : 6600026A
    move.l #$00000000,d0                              ; +$03DA : 203C00000000
    move.w 14(a0),d0                                  ; +$03E0 : 3028000E
    cmpi.l #$00000000,d0                              ; +$03E4 : 0C8000000000
    bne.w L_00C10A                                    ; +$03EA : 66000256
    move.l #$00000000,d0                              ; +$03EE : 203C00000000
    move.w 12(a0),d0                                  ; +$03F4 : 3028000C
    cmp.l 56(a2),d0                                   ; +$03F8 : B0AA0038
    bne.w L_00C10A                                    ; +$03FC : 66000244
    movea.l 24(a2),a0                                 ; +$0400 : 206A0018
    move.l 24(a0),d0                                  ; +$0404 : 20280018
    cmp.l 8(a2),d0                                    ; +$0408 : B0AA0008
    bne.w L_00C10A                                    ; +$040C : 66000234
    movea.l 24(a2),a0                                 ; +$0410 : 206A0018
    move.l 28(a0),d0                                  ; +$0414 : 2028001C
    cmp.l 4(a2),d0                                    ; +$0418 : B0AA0004
    bne.w L_00C10A                                    ; +$041C : 66000224
    movea.l 24(a2),a0                                 ; +$0420 : 206A0018
    move.l 32(a0),d0                                  ; +$0424 : 20280020
    cmp.l 60(a2),d0                                   ; +$0428 : B0AA003C
    bne.w L_00C10A                                    ; +$042C : 66000214
    movea.l 24(a2),a0                                 ; +$0430 : 206A0018
    move.l 36(a0),d0                                  ; +$0434 : 20280024
    cmp.l 64(a2),d0                                   ; +$0438 : B0AA0040
    bne.w L_00C10A                                    ; +$043C : 66000204
    move.l 28(a2),d0                                  ; +$0440 : 202A001C
    cmp.l 68(a2),d0                                   ; +$0444 : B0AA0044
    bne.w L_00C10A                                    ; +$0448 : 660001F8
    move.l 12(a2),d0                                  ; +$044C : 202A000C
    move.l 76(a2),d1                                  ; +$0450 : 222A004C
    mulu.w d1,d0                                      ; +$0454 : C0C1
    move.l 16(a2),d1                                  ; +$0456 : 222A0010
    lsr.l #3,d1                                       ; +$045A : E689
    add.l d1,d0                                       ; +$045C : D081
    bcs.w L_00C10A                                    ; +$045E : 650001E2
    move.l d0,80(a2)                                  ; +$0462 : 25400050
    move.l 12(a2),d0                                  ; +$0466 : 202A000C
    move.l 4(a2),d1                                   ; +$046A : 222A0004
    add.l d1,d0                                       ; +$046E : D081
    bcs.w L_00C10A                                    ; +$0470 : 650001D0
    subq.l #1,d0                                      ; +$0474 : 5380
    move.l 76(a2),d1                                  ; +$0476 : 222A004C
    mulu.w d1,d0                                      ; +$047A : C0C1
    move.l 16(a2),d1                                  ; +$047C : 222A0010
    move.l 8(a2),d4                                   ; +$0480 : 282A0008
    add.l d4,d1                                       ; +$0484 : D284
    bcs.w L_00C10A                                    ; +$0486 : 650001BA
    subq.l #1,d1                                      ; +$048A : 5381
    lsr.l #3,d1                                       ; +$048C : E689
    add.l d1,d0                                       ; +$048E : D081
    bcs.w L_00C10A                                    ; +$0490 : 650001B0
    move.l d0,84(a2)                                  ; +$0494 : 25400054
    movea.l 40(a2),a4                                 ; +$0498 : 286A0028
    addq.l #8,a4                                      ; +$049C : 508C
    move.l 56(a2),d5                                  ; +$049E : 2A2A0038
L_00BF6A:
    move.l (a4)+,d7                                   ; +$04A2 : 2E1C
    tst.l d7                                          ; +$04A4 : 4A87
    beq.w L_00C10A                                    ; +$04A6 : 6700019A
    cmpi.l #$FFFFFFFF,d7                              ; +$04AA : 0C87FFFFFFFF
    beq.w L_00C10A                                    ; +$04B0 : 67000190
    move.l d7,d0                                      ; +$04B4 : 2007
    andi.l #$00000001,d0                              ; +$04B6 : 028000000001
    bne.w L_00C10A                                    ; +$04BC : 66000184
    move.l 80(a2),d0                                  ; +$04C0 : 202A0050
    add.l d7,d0                                       ; +$04C4 : D087
    bcs.w L_00C10A                                    ; +$04C6 : 6500017A
    movea.l d0,a1                                     ; +$04CA : 2240
    movea.l $0004.w,a6                                ; +$04CC : 2C780004
    jsr -534(a6)                                      ; +$04D0 : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$04D4 : 028000000002
    beq.w L_00C10A                                    ; +$04DA : 67000166
    move.l 84(a2),d0                                  ; +$04DE : 202A0054
    add.l d7,d0                                       ; +$04E2 : D087
    bcs.w L_00C10A                                    ; +$04E4 : 6500015C
    movea.l d0,a1                                     ; +$04E8 : 2240
    movea.l $0004.w,a6                                ; +$04EA : 2C780004
    jsr -534(a6)                                      ; +$04EE : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$04F2 : 028000000002
    beq.w L_00C10A                                    ; +$04F8 : 67000148
    subq.l #1,d5                                      ; +$04FC : 5385
    bne.w L_00BF6A                                    ; +$04FE : 6600FFA2
    move.l #$00000000,260(a2)                         ; +$0502 : 257C000000000104
    move.l #$00000000,264(a2)                         ; +$050A : 257C000000000108
    move.l #$00000000,268(a2)                         ; +$0512 : 257C00000000010C
    move.l #$00000000,272(a2)                         ; +$051A : 257C000000000110
    move.l #$00000000,276(a2)                         ; +$0522 : 257C000000000114
    move.l #$00000000,280(a2)                         ; +$052A : 257C000000000118
    move.l #$00000000,284(a2)                         ; +$0532 : 257C00000000011C
    move.l #$00000000,288(a2)                         ; +$053A : 257C000000000120
    move.l #$00000000,292(a2)                         ; +$0542 : 257C000000000124
    move.l 60(a2),d0                                  ; +$054A : 202A003C
    move.w d0,256(a2)                                 ; +$054E : 35400100
    move.l 4(a2),d0                                   ; +$0552 : 202A0004
    move.w d0,258(a2)                                 ; +$0556 : 35400102
    move.l 56(a2),d0                                  ; +$055A : 202A0038
    move.b d0,261(a2)                                 ; +$055E : 15400105
    lea 264(a2),a4                                    ; +$0562 : 49EA0108
    move.l 24(a2),d6                                  ; +$0566 : 2C2A0018
    addi.l #$00000028,d6                              ; +$056A : 068600000028
    move.l 64(a2),d7                                  ; +$0570 : 2E2A0040
    move.l 56(a2),d5                                  ; +$0574 : 2A2A0038
L_00C040:
    movea.l d6,a1                                     ; +$0578 : 2246
    movea.l $0004.w,a6                                ; +$057A : 2C780004
    jsr -534(a6)                                      ; +$057E : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$0582 : 028000000002
    beq.w L_00C10A                                    ; +$0588 : 670000B8
    move.l d6,d0                                      ; +$058C : 2006
    add.l d7,d0                                       ; +$058E : D087
    bcs.w L_00C10A                                    ; +$0590 : 650000B0
    subq.l #1,d0                                      ; +$0594 : 5380
    movea.l d0,a1                                     ; +$0596 : 2240
    movea.l $0004.w,a6                                ; +$0598 : 2C780004
    jsr -534(a6)                                      ; +$059C : 4EAEFDEA
    andi.l #$00000002,d0                              ; +$05A0 : 028000000002
    beq.w L_00C10A                                    ; +$05A6 : 6700009A
    move.l d6,(a4)+                                   ; +$05AA : 28C6
    add.l d7,d6                                       ; +$05AC : DC87
    bcs.w L_00C10A                                    ; +$05AE : 65000092
    subq.l #1,d5                                      ; +$05B2 : 5385
    bne.w L_00C040                                    ; +$05B4 : 6600FFC2
    movea.l 36(a2),a4                                 ; +$05B8 : 286A0024
    move.l 20(a4),d0                                  ; +$05BC : 202C0014
    andi.l #$00000001,d0                              ; +$05C0 : 028000000001
    beq.w L_00C0C2                                    ; +$05C6 : 67000032
    movea.l 36(a2),a4                                 ; +$05CA : 286A0024
    movea.l 12(a4),a0                                 ; +$05CE : 206C000C
    move.l a0,d0                                      ; +$05D2 : 2008
    tst.l d0                                          ; +$05D4 : 4A80
    beq.w L_00C10A                                    ; +$05D6 : 6700006A
    movea.l $0004.w,a6                                ; +$05DA : 2C780004
    jsr -372(a6)                                      ; +$05DE : 4EAEFE8C
    tst.l d0                                          ; +$05E2 : 4A80
    beq.w L_00C10A                                    ; +$05E4 : 6700005C
    movea.l 36(a2),a4                                 ; +$05E8 : 286A0024
    move.l 20(a4),d0                                  ; +$05EC : 202C0014
    andi.l #$FFFFFFFE,d0                              ; +$05F0 : 0280FFFFFFFE
    move.l d0,20(a4)                                  ; +$05F6 : 29400014
L_00C0C2:
    movea.l 44(a2),a6                                 ; +$05FA : 2C6A002C
    jsr -228(a6)                                      ; +$05FE : 4EAEFF1C
    lea 256(a2),a0                                    ; +$0602 : 41EA0100
    movea.l 40(a2),a1                                 ; +$0606 : 226A0028
    move.l #$00000000,d0                              ; +$060A : 203C00000000
    move.l #$00000000,d1                              ; +$0610 : 223C00000000
    move.l 16(a2),d2                                  ; +$0616 : 242A0010
    move.l 12(a2),d3                                  ; +$061A : 262A000C
    move.l 8(a2),d4                                   ; +$061E : 282A0008
    move.l 4(a2),d5                                   ; +$0622 : 2A2A0004
    move.l (a2),d6                                    ; +$0626 : 2C12
    movea.l 44(a2),a6                                 ; +$0628 : 2C6A002C
    lea L_00C124(pc),a4                               ; +$062C : 49FA002E
    jsr (a4)                                          ; +$0630 : 4E94
    tst.l d3                                          ; +$0632 : 4A83
    beq.w L_00C10A                                    ; +$0634 : 6700000C
    move.l #$00000001,d3                              ; +$0638 : 263C00000001
    bra.w L_00C110                                    ; +$063E : 60000008
L_00C10A:
    move.l #$00000000,d3                              ; +$0642 : 263C00000000
L_00C110:
    lea 384(a7),a7                                    ; +$0648 : 4FEF0180
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$064C : 4CDF77F7
    moveq #0,d2                                       ; +$0650 : 7400
    rts                                               ; +$0652 : 4E75
    dc.b "AGACBLK "
L_00C124:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)             ; +$065C : 48E7EFEE
    lea -256(a7),a7                                   ; +$0660 : 4FEFFF00
    movea.l a7,a4                                     ; +$0664 : 284F
    move.l a0,(a4)                                    ; +$0666 : 2888
    move.l a1,4(a4)                                   ; +$0668 : 29490004
    move.l a6,36(a4)                                  ; +$066C : 294E0024
    move.l d0,8(a4)                                   ; +$0670 : 29400008
    move.l d1,12(a4)                                  ; +$0674 : 2941000C
    move.l d2,16(a4)                                  ; +$0678 : 29420010
    move.l d3,20(a4)                                  ; +$067C : 29430014
    move.l d4,24(a4)                                  ; +$0680 : 29440018
    move.l d5,28(a4)                                  ; +$0684 : 2945001C
    move.l d6,32(a4)                                  ; +$0688 : 29460020
    move.l #$00000000,d3                              ; +$068C : 263C00000000
    move.l (a4),d0                                    ; +$0692 : 2014
    tst.l d0                                          ; +$0694 : 4A80
    beq.w L_00C47A                                    ; +$0696 : 6700031A
    andi.l #$00000001,d0                              ; +$069A : 028000000001
    bne.w L_00C47A                                    ; +$06A0 : 66000310
    move.l 4(a4),d0                                   ; +$06A4 : 202C0004
    tst.l d0                                          ; +$06A8 : 4A80
    beq.w L_00C47A                                    ; +$06AA : 67000306
    andi.l #$00000001,d0                              ; +$06AE : 028000000001
    bne.w L_00C47A                                    ; +$06B4 : 660002FC
    move.l 32(a4),d0                                  ; +$06B8 : 202C0020
    cmpi.l #$00000002,d0                              ; +$06BC : 0C8000000002
    bhi.w L_00C47A                                    ; +$06C2 : 620002EE
    tst.l d0                                          ; +$06C6 : 4A80
    bmi.w L_00C47A                                    ; +$06C8 : 6B0002E8
    move.l 8(a4),d0                                   ; +$06CC : 202C0008
    tst.l d0                                          ; +$06D0 : 4A80
    bmi.w L_00C47A                                    ; +$06D2 : 6B0002DE
    cmpi.l #$00007FFF,d0                              ; +$06D6 : 0C8000007FFF
    bgt.w L_00C47A                                    ; +$06DC : 6E0002D4
    move.l 12(a4),d0                                  ; +$06E0 : 202C000C
    tst.l d0                                          ; +$06E4 : 4A80
    bmi.w L_00C47A                                    ; +$06E6 : 6B0002CA
    cmpi.l #$00007FFF,d0                              ; +$06EA : 0C8000007FFF
    bgt.w L_00C47A                                    ; +$06F0 : 6E0002C0
    move.l 16(a4),d0                                  ; +$06F4 : 202C0010
    tst.l d0                                          ; +$06F8 : 4A80
    bmi.w L_00C47A                                    ; +$06FA : 6B0002B6
    cmpi.l #$00007FFF,d0                              ; +$06FE : 0C8000007FFF
    bgt.w L_00C47A                                    ; +$0704 : 6E0002AC
    move.l 20(a4),d0                                  ; +$0708 : 202C0014
    tst.l d0                                          ; +$070C : 4A80
    bmi.w L_00C47A                                    ; +$070E : 6B0002A2
    cmpi.l #$00007FFF,d0                              ; +$0712 : 0C8000007FFF
    bgt.w L_00C47A                                    ; +$0718 : 6E000298
    move.l 24(a4),d0                                  ; +$071C : 202C0018
    tst.l d0                                          ; +$0720 : 4A80
    ble.w L_00C47A                                    ; +$0722 : 6F00028E
    cmpi.l #$00001000,d0                              ; +$0726 : 0C8000001000
    bgt.w L_00C47A                                    ; +$072C : 6E000284
    move.l 28(a4),d0                                  ; +$0730 : 202C001C
    tst.l d0                                          ; +$0734 : 4A80
    ble.w L_00C47A                                    ; +$0736 : 6F00027A
    cmpi.l #$00001000,d0                              ; +$073A : 0C8000001000
    bgt.w L_00C47A                                    ; +$0740 : 6E000270
    move.l 32(a4),d1                                  ; +$0744 : 222C0020
    cmpi.l #$00000001,d1                              ; +$0748 : 0C8100000001
    beq.w L_00C224                                    ; +$074E : 6700000C
    move.l #$00000007,d1                              ; +$0752 : 223C00000007
    bra.w L_00C22A                                    ; +$0758 : 60000008
L_00C224:
    move.l #$0000000F,d1                              ; +$075C : 223C0000000F
L_00C22A:
    move.l 8(a4),d0                                   ; +$0762 : 202C0008
    and.l d1,d0                                       ; +$0766 : C081
    bne.w L_00C47A                                    ; +$0768 : 66000248
    move.l 16(a4),d0                                  ; +$076C : 202C0010
    and.l d1,d0                                       ; +$0770 : C081
    bne.w L_00C47A                                    ; +$0772 : 6600023E
    move.l 24(a4),d0                                  ; +$0776 : 202C0018
    and.l d1,d0                                       ; +$077A : C081
    bne.w L_00C47A                                    ; +$077C : 66000234
    movea.l (a4),a0                                   ; +$0780 : 2054
    move.l #$00000000,d0                              ; +$0782 : 203C00000000
    move.w (a0),d0                                    ; +$0788 : 3010
    move.l d0,40(a4)                                  ; +$078A : 29400028
    tst.l d0                                          ; +$078E : 4A80
    ble.w L_00C47A                                    ; +$0790 : 6F000220
    andi.l #$00000001,d0                              ; +$0794 : 028000000001
    bne.w L_00C47A                                    ; +$079A : 66000216
    move.l #$00000000,d0                              ; +$079E : 203C00000000
    move.w 2(a0),d0                                   ; +$07A4 : 30280002
    move.l d0,68(a4)                                  ; +$07A8 : 29400044
    tst.l d0                                          ; +$07AC : 4A80
    ble.w L_00C47A                                    ; +$07AE : 6F000202
    move.l #$00000000,d0                              ; +$07B2 : 203C00000000
    move.b 5(a0),d0                                   ; +$07B8 : 10280005
    tst.l d0                                          ; +$07BC : 4A80
    ble.w L_00C47A                                    ; +$07BE : 6F0001F2
    cmpi.l #$00000008,d0                              ; +$07C2 : 0C8000000008
    bgt.w L_00C47A                                    ; +$07C8 : 6E0001E8
    move.l d0,48(a4)                                  ; +$07CC : 29400030
    movea.l 4(a4),a0                                  ; +$07D0 : 206C0004
    move.l #$00000000,d0                              ; +$07D4 : 203C00000000
    move.w (a0),d0                                    ; +$07DA : 3010
    move.l d0,44(a4)                                  ; +$07DC : 2940002C
    tst.l d0                                          ; +$07E0 : 4A80
    ble.w L_00C47A                                    ; +$07E2 : 6F0001CE
    andi.l #$00000001,d0                              ; +$07E6 : 028000000001
    bne.w L_00C47A                                    ; +$07EC : 660001C4
    move.l #$00000000,d0                              ; +$07F0 : 203C00000000
    move.w 2(a0),d0                                   ; +$07F6 : 30280002
    move.l d0,72(a4)                                  ; +$07FA : 29400048
    tst.l d0                                          ; +$07FE : 4A80
    ble.w L_00C47A                                    ; +$0800 : 6F0001B0
    move.l #$00000000,d0                              ; +$0804 : 203C00000000
    move.b 5(a0),d0                                   ; +$080A : 10280005
    tst.l d0                                          ; +$080E : 4A80
    ble.w L_00C47A                                    ; +$0810 : 6F0001A0
    cmpi.l #$00000008,d0                              ; +$0814 : 0C8000000008
    bgt.w L_00C47A                                    ; +$081A : 6E000196
    cmp.l 48(a4),d0                                   ; +$081E : B0AC0030
    bne.w L_00C47A                                    ; +$0822 : 6600018E
    move.l 8(a4),d0                                   ; +$0826 : 202C0008
    move.l 24(a4),d1                                  ; +$082A : 222C0018
    add.l d1,d0                                       ; +$082E : D081
    move.l 40(a4),d1                                  ; +$0830 : 222C0028
    lsl.l #3,d1                                       ; +$0834 : E789
    cmp.l d1,d0                                       ; +$0836 : B081
    bhi.w L_00C47A                                    ; +$0838 : 62000178
    move.l 12(a4),d0                                  ; +$083C : 202C000C
    move.l 28(a4),d1                                  ; +$0840 : 222C001C
    add.l d1,d0                                       ; +$0844 : D081
    cmp.l 68(a4),d0                                   ; +$0846 : B0AC0044
    bhi.w L_00C47A                                    ; +$084A : 62000166
    move.l 16(a4),d0                                  ; +$084E : 202C0010
    move.l 24(a4),d1                                  ; +$0852 : 222C0018
    add.l d1,d0                                       ; +$0856 : D081
    move.l 44(a4),d1                                  ; +$0858 : 222C002C
    lsl.l #3,d1                                       ; +$085C : E789
    cmp.l d1,d0                                       ; +$085E : B081
    bhi.w L_00C47A                                    ; +$0860 : 62000150
    move.l 20(a4),d0                                  ; +$0864 : 202C0014
    move.l 28(a4),d1                                  ; +$0868 : 222C001C
    add.l d1,d0                                       ; +$086C : D081
    cmp.l 72(a4),d0                                   ; +$086E : B0AC0048
    bhi.w L_00C47A                                    ; +$0872 : 6200013E
    movea.l (a4),a5                                   ; +$0876 : 2A54
    addq.l #8,a5                                      ; +$0878 : 508D
    movea.l 4(a4),a6                                  ; +$087A : 2C6C0004
    addq.l #8,a6                                      ; +$087E : 508E
    move.l 48(a4),d7                                  ; +$0880 : 2E2C0030
L_00C34C:
    move.l (a5)+,d0                                   ; +$0884 : 201D
    tst.l d0                                          ; +$0886 : 4A80
    beq.w L_00C47A                                    ; +$0888 : 67000128
    andi.l #$00000001,d0                              ; +$088C : 028000000001
    bne.w L_00C47A                                    ; +$0892 : 6600011E
    move.l (a6)+,d0                                   ; +$0896 : 201E
    tst.l d0                                          ; +$0898 : 4A80
    beq.w L_00C47A                                    ; +$089A : 67000116
    andi.l #$00000001,d0                              ; +$089E : 028000000001
    bne.w L_00C47A                                    ; +$08A4 : 6600010C
    subq.l #1,d7                                      ; +$08A8 : 5387
    bne.w L_00C34C                                    ; +$08AA : 6600FFD8
    move.l 32(a4),d0                                  ; +$08AE : 202C0020
    cmpi.l #$00000002,d0                              ; +$08B2 : 0C8000000002
    bne.w L_00C3D4                                    ; +$08B8 : 66000052
    move.l 36(a4),d0                                  ; +$08BC : 202C0024
    tst.l d0                                          ; +$08C0 : 4A80
    beq.w L_00C47A                                    ; +$08C2 : 670000EE
    movea.l 36(a4),a6                                 ; +$08C6 : 2C6C0024
    lea 128(a4),a1                                    ; +$08CA : 43EC0080
    jsr -198(a6)                                      ; +$08CE : 4EAEFF3A
    lea 128(a4),a1                                    ; +$08D2 : 43EC0080
    move.l 4(a4),4(a1)                                ; +$08D6 : 236C00040004
    movea.l (a4),a0                                   ; +$08DC : 2054
    move.l 8(a4),d0                                   ; +$08DE : 202C0008
    move.l 12(a4),d1                                  ; +$08E2 : 222C000C
    move.l 16(a4),d2                                  ; +$08E6 : 242C0010
    move.l 20(a4),d3                                  ; +$08EA : 262C0014
    move.l 24(a4),d4                                  ; +$08EE : 282C0018
    move.l 28(a4),d5                                  ; +$08F2 : 2A2C001C
    move.l #$000000C0,d6                              ; +$08F6 : 2C3C000000C0
    jsr -606(a6)                                      ; +$08FC : 4EAEFDA2
    movea.l 36(a4),a6                                 ; +$0900 : 2C6C0024
    jsr -228(a6)                                      ; +$0904 : 4EAEFF1C
    bra.w L_00C470                                    ; +$0908 : 6000009E
L_00C3D4:
    move.l 24(a4),d0                                  ; +$090C : 202C0018
    lsr.l #3,d0                                       ; +$0910 : E688
    move.l d0,52(a4)                                  ; +$0912 : 29400034
    move.l 40(a4),d1                                  ; +$0916 : 222C0028
    sub.l d0,d1                                       ; +$091A : 9280
    move.l d1,56(a4)                                  ; +$091C : 29410038
    move.l 44(a4),d1                                  ; +$0920 : 222C002C
    sub.l d0,d1                                       ; +$0924 : 9280
    move.l d1,60(a4)                                  ; +$0926 : 2941003C
    movea.l (a4),a5                                   ; +$092A : 2A54
    addq.l #8,a5                                      ; +$092C : 508D
    movea.l 4(a4),a6                                  ; +$092E : 2C6C0004
    addq.l #8,a6                                      ; +$0932 : 508E
    move.l 48(a4),d7                                  ; +$0934 : 2E2C0030
L_00C400:
    movea.l (a5)+,a0                                  ; +$0938 : 205D
    movea.l (a6)+,a1                                  ; +$093A : 225E
    move.l 12(a4),d0                                  ; +$093C : 202C000C
    move.l 40(a4),d1                                  ; +$0940 : 222C0028
    mulu.w d1,d0                                      ; +$0944 : C0C1
    move.l 8(a4),d1                                   ; +$0946 : 222C0008
    lsr.l #3,d1                                       ; +$094A : E689
    add.l d1,d0                                       ; +$094C : D081
    adda.l d0,a0                                      ; +$094E : D1C0
    move.l 20(a4),d0                                  ; +$0950 : 202C0014
    move.l 44(a4),d1                                  ; +$0954 : 222C002C
    mulu.w d1,d0                                      ; +$0958 : C0C1
    move.l 16(a4),d1                                  ; +$095A : 222C0010
    lsr.l #3,d1                                       ; +$095E : E689
    add.l d1,d0                                       ; +$0960 : D081
    adda.l d0,a1                                      ; +$0962 : D3C0
    move.l 28(a4),d4                                  ; +$0964 : 282C001C
L_00C430:
    move.l 52(a4),d6                                  ; +$0968 : 2C2C0034
    move.l 32(a4),d0                                  ; +$096C : 202C0020
    cmpi.l #$00000001,d0                              ; +$0970 : 0C8000000001
    beq.w L_00C44E                                    ; +$0976 : 6700000E
L_00C442:
    move.b (a0)+,(a1)+                                ; +$097A : 12D8
    subq.l #1,d6                                      ; +$097C : 5386
    bne.w L_00C442                                    ; +$097E : 6600FFFA
    bra.w L_00C458                                    ; +$0982 : 6000000C
L_00C44E:
    lsr.l #1,d6                                       ; +$0986 : E28E
L_00C450:
    move.w (a0)+,(a1)+                                ; +$0988 : 32D8
    subq.l #1,d6                                      ; +$098A : 5386
    bne.w L_00C450                                    ; +$098C : 6600FFFA
L_00C458:
    move.l 56(a4),d0                                  ; +$0990 : 202C0038
    adda.l d0,a0                                      ; +$0994 : D1C0
    move.l 60(a4),d0                                  ; +$0996 : 202C003C
    adda.l d0,a1                                      ; +$099A : D3C0
    subq.l #1,d4                                      ; +$099C : 5384
    bne.w L_00C430                                    ; +$099E : 6600FFC8
    subq.l #1,d7                                      ; +$09A2 : 5387
    bne.w L_00C400                                    ; +$09A4 : 6600FF92
L_00C470:
    move.l #$00000001,d3                              ; +$09A8 : 263C00000001
    bra.w L_00C480                                    ; +$09AE : 60000008
L_00C47A:
    move.l #$00000000,d3                              ; +$09B2 : 263C00000000
L_00C480:
    lea 256(a7),a7                                    ; +$09B8 : 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6             ; +$09BC : 4CDF77F7
    moveq #0,d2                                       ; +$09C0 : 7400
    rts                                               ; +$09C2 : 4E75

Entry_70:
C_Title:
    dc.b "AMOSPro AGA OPT020 Image Region R69 0.13.14 Gate A candidate"
    dc.b $00,$24,$56,$45,$52,$3A,$20,$41,$4D,$4F,$53,$50
    dc.b "ro_AGA 0.13.14"
    dc.b $00,$00
C_End:
    dc.w 0
    cnop 0,4
HUNK_DATA_END:
    dc.l $000003F2
