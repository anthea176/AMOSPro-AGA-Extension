; AGA_NATIVE_MIN_CPU: MC68020
; PARTIAL_SOURCE_MIGRATION: UNIT153 public preflight native, audit remainder
; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)
; Unit: UNIT153 | SHA256: 6eda5283af42617aa13ad81e24d9130abedc4528ed05b469de2d765d20b4d700
; Proven SHA-pinned AP20 unit, including its 34-byte V2 dispatcher.
; DC.B preserves unclassified code/data, GetP and AMOS linker markers.
; Mnemonic equivalence is NOT proven without --verify-vasm.
; MC68020: assemble with vasmm68k_mot -m68020

UNIT_UNIT153:
    subq.l #4,a7                                       ; +$00000: 598F
    movem.l d0/a0,-(a7)                                ; +$00002: 48E78080
    movea.l 12(a7),a0                                  ; +$00006: 206F000C
    moveq #0,d0                                        ; +$0000A: 7000
    move.w (a0)+,d0                                    ; +$0000C: 3018
    move.l a0,12(a7)                                   ; +$0000E: 2F48000C
    lea ENTRY_UNIT153_00022(pc),a0                     ; +$00012: 41FA000E
    adda.l d0,a0                                       ; +$00016: D1C0
    move.l a0,8(a7)                                    ; +$00018: 2F480008
    movem.l (a7)+,d0/a0                                ; +$0001C: 4CDF0101
    rts                                                ; +$00020: 4E75
ENTRY_UNIT153_00022:
    include "M19_UNIT153_ENTRY_GUARD_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00108: FE11F700031D
    include "M19_UNIT153_POINTER_VALIDATE_MC68020.s"
L_UNIT153_00362:
    dc.b $63,$32,$70,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$00362: 6332702E6C69627261727900
    dc.b $47,$65,$74,$50  ; +$0036E: 47657450
ENTRY_UNIT153_00372:
    include "M19_UNIT153_PUBLIC_PREFLIGHT_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00530: FE11F700031D
    include "M19_UNIT153_SECOND_GET_MC68020.s"
    dc.b $47,$65,$74,$50  ; +$00946: 47657450
ENTRY_UNIT153_0094A:
    include "M19_UNIT153_SHORT_SERVICE_MC68020.s"
    dc.b $47,$65,$74,$50  ; +$009FE: 47657450
ENTRY_UNIT153_00A02:
    include "M19_UNIT153_BULK_PREFLIGHT_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00BD4: FE11F700031D
    include "M19_UNIT153_POINTER_RECHECK_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$00C98: FE11F700031D
    include "M19_UNIT153_MEMORY_WALK_MC68020.s"
    dc.b $53,$86,$12,$D8,$51,$CE,$FF,$FC,$20,$2A,$00,$4C  ; +$00EDA: 538612D851CEFFFC202A004C
    dc.b $2A,$08,$DA,$80,$20,$45,$20,$2A,$00,$50,$2A,$09  ; +$00EE6: 2A08DA802045202A00502A09
    dc.b $DA,$80,$22,$45,$51,$CF,$FF,$DE,$26,$3C,$00,$00  ; +$00EF2: DA80224551CFFFDE263C0000
    dc.b $00,$01,$60,$00,$00,$08  ; +$00EFE: 000160000008
L_UNIT153_00F04:
    include "M19_UNIT153_WALK_CLEANUP_MC68020.s"
    dc.b $47,$65,$74,$50  ; +$00F9C: 47657450
ENTRY_UNIT153_00FA0:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00FA0: 48E7EFEE
    lea -192(a7),a7                                    ; +$00FA4: 4FEFFF40
    movea.l a7,a2                                      ; +$00FA8: 244F
    move.l d3,(a2)                                     ; +$00FAA: 2483
    move.l (a3)+,d7                                    ; +$00FAC: 2E1B
    move.l d7,4(a2)                                    ; +$00FAE: 25470004
    move.l (a3)+,d7                                    ; +$00FB2: 2E1B
    move.l d7,8(a2)                                    ; +$00FB4: 25470008
    move.l (a3)+,d7                                    ; +$00FB8: 2E1B
    move.l d7,12(a2)                                   ; +$00FBA: 2547000C
    move.l (a3)+,d7                                    ; +$00FBE: 2E1B
    move.l d7,16(a2)                                   ; +$00FC0: 25470010
    move.l (a3)+,d7                                    ; +$00FC4: 2E1B
    move.l d7,20(a2)                                   ; +$00FC6: 25470014
    move.l (a3)+,d7                                    ; +$00FCA: 2E1B
    move.l d7,24(a2)                                   ; +$00FCC: 25470018
    move.l (a3)+,d7                                    ; +$00FD0: 2E1B
    move.l d7,28(a2)                                   ; +$00FD2: 2547001C
    move.l (a3)+,d7                                    ; +$00FD6: 2E1B
    move.l d7,32(a2)                                   ; +$00FD8: 25470020
    move.l (a3)+,d7                                    ; +$00FDC: 2E1B
    move.l d7,36(a2)                                   ; +$00FDE: 25470024
    move.l #$00000000,d3                               ; +$00FE2: 263C00000000
    movea.l $0004.w,a0                                 ; +$00FE8: 20780004
    move.l a0,d0                                       ; +$00FEC: 2008
    tst.l d0                                           ; +$00FEE: 4A80
    beq.w L_UNIT153_01540                              ; +$00FF0: 6700054E
    move.l #$00000000,d0                               ; +$00FF4: 203C00000000
    move.w 296(a0),d0                                  ; +$00FFA: 30280128
    btst #1,d0                                         ; +$00FFE: 08000001
    beq.w L_UNIT153_01540                              ; +$01002: 6700053C
    move.l 36(a2),d0                                   ; +$01006: 202A0024
    cmpi.l #$00000005,d0                               ; +$0100A: 0C8000000005
    bcs.w L_UNIT153_01540                              ; +$01010: 6500052E
    cmpi.l #$0000FFFF,d0                               ; +$01014: 0C800000FFFF
    bhi.w L_UNIT153_01540                              ; +$0101A: 62000524
    move.l 32(a2),d0                                   ; +$0101E: 202A0020
    tst.l d0                                           ; +$01022: 4A80
    blt.w L_UNIT153_01540                              ; +$01024: 6D00051A
    beq.w L_UNIT153_01540                              ; +$01028: 67000516
    move.l 28(a2),d0                                   ; +$0102C: 202A001C
    tst.l d0                                           ; +$01030: 4A80
    blt.w L_UNIT153_01540                              ; +$01032: 6D00050C
    move.l 24(a2),d0                                   ; +$01036: 202A0018
    tst.l d0                                           ; +$0103A: 4A80
    blt.w L_UNIT153_01540                              ; +$0103C: 6D000502
    move.l 20(a2),d0                                   ; +$01040: 202A0014
    tst.l d0                                           ; +$01044: 4A80
    ble.w L_UNIT153_01540                              ; +$01046: 6F0004F8
    cmpi.l #$00000140,d0                               ; +$0104A: 0C8000000140
    bhi.w L_UNIT153_01540                              ; +$01050: 620004EE
    move.l 16(a2),d0                                   ; +$01054: 202A0010
    tst.l d0                                           ; +$01058: 4A80
    ble.w L_UNIT153_01540                              ; +$0105A: 6F0004E4
    cmpi.l #$00000100,d0                               ; +$0105E: 0C8000000100
    bhi.w L_UNIT153_01540                              ; +$01064: 620004DA
    move.l 4(a2),d0                                    ; +$01068: 202A0004
    tst.l d0                                           ; +$0106C: 4A80
    ble.w L_UNIT153_01540                              ; +$0106E: 6F0004D0
    cmpi.l #$00000140,d0                               ; +$01072: 0C8000000140
    bhi.w L_UNIT153_01540                              ; +$01078: 620004C6
    move.l (a2),d0                                     ; +$0107C: 2012
    tst.l d0                                           ; +$0107E: 4A80
    ble.w L_UNIT153_01540                              ; +$01080: 6F0004BE
    cmpi.l #$00000100,d0                               ; +$01084: 0C8000000100
    bhi.w L_UNIT153_01540                              ; +$0108A: 620004B4
    move.l 12(a2),d0                                   ; +$0108E: 202A000C
    cmpi.l #$FFFFFEC1,d0                               ; +$01092: 0C80FFFFFEC1
    blt.w L_UNIT153_01540                              ; +$01098: 6D0004A6
    cmpi.l #$00000140,d0                               ; +$0109C: 0C8000000140
    bge.w L_UNIT153_01540                              ; +$010A2: 6C00049C
    move.l 8(a2),d0                                    ; +$010A6: 202A0008
    cmpi.l #$FFFFFF01,d0                               ; +$010AA: 0C80FFFFFF01
    blt.w L_UNIT153_01540                              ; +$010B0: 6D00048E
    cmpi.l #$00000100,d0                               ; +$010B4: 0C8000000100
    bge.w L_UNIT153_01540                              ; +$010BA: 6C000484
    move.l 28(a2),d0                                   ; +$010BE: 202A001C
    move.l 20(a2),d1                                   ; +$010C2: 222A0014
    add.l d1,d0                                        ; +$010C6: D081
    bcs.w L_UNIT153_01540                              ; +$010C8: 65000476
    bvs.w L_UNIT153_01540                              ; +$010CC: 69000472
    move.l 32(a2),d1                                   ; +$010D0: 222A0020
    cmp.l d1,d0                                        ; +$010D4: B081
    bhi.w L_UNIT153_01540                              ; +$010D6: 62000468
    movea.l 456(a5),a4                                 ; +$010DA: 286D01C8
    move.l a4,d0                                       ; +$010DE: 200C
    tst.l d0                                           ; +$010E0: 4A80
    beq.w L_UNIT153_01540                              ; +$010E2: 6700045C
    move.l a4,40(a2)                                   ; +$010E6: 254C0028
    movea.l 40(a2),a4                                  ; +$010EA: 286A0028
    move.l (a4),d0                                     ; +$010EE: 2014
    tst.l d0                                           ; +$010F0: 4A80
    beq.w L_UNIT153_01540                              ; +$010F2: 6700044C
    movea.l 40(a2),a4                                  ; +$010F6: 286A0028
    move.l 12(a4),d0                                   ; +$010FA: 202C000C
    cmpi.l #$00000140,d0                               ; +$010FE: 0C8000000140
    bne.w L_UNIT153_01540                              ; +$01104: 6600043A
    movea.l 40(a2),a4                                  ; +$01108: 286A0028
    move.l 16(a4),d0                                   ; +$0110C: 202C0010
    cmpi.l #$00000100,d0                               ; +$01110: 0C8000000100
    bne.w L_UNIT153_01540                              ; +$01116: 66000428
    movea.l 40(a2),a4                                  ; +$0111A: 286A0028
    move.l 28(a4),d0                                   ; +$0111E: 202C001C
    cmpi.l #$00000004,d0                               ; +$01122: 0C8000000004
    bcs.w L_UNIT153_01540                              ; +$01128: 65000416
    cmpi.l #$00000008,d0                               ; +$0112C: 0C8000000008
    bhi.w L_UNIT153_01540                              ; +$01132: 6200040C
    movea.l 40(a2),a4                                  ; +$01136: 286A0028
    movea.l 32(a4),a4                                  ; +$0113A: 286C0020
    move.l a4,d0                                       ; +$0113E: 200C
    tst.l d0                                           ; +$01140: 4A80
    beq.w L_UNIT153_01540                              ; +$01142: 670003FC
    move.l a4,44(a2)                                   ; +$01146: 254C002C
    movea.l 44(a2),a4                                  ; +$0114A: 286A002C
    move.l 40(a4),d0                                   ; +$0114E: 202C0028
    cmpi.l #$43325031,d0                               ; +$01152: 0C8043325031
    bne.w L_UNIT153_01540                              ; +$01158: 660003E6
    movea.l 44(a2),a4                                  ; +$0115C: 286A002C
    move.l 24(a4),d0                                   ; +$01160: 202C0018
    tst.l d0                                           ; +$01164: 4A80
    beq.w L_UNIT153_01540                              ; +$01166: 670003D8
    movea.l 44(a2),a4                                  ; +$0116A: 286A002C
    move.l 28(a4),d0                                   ; +$0116E: 202C001C
    tst.l d0                                           ; +$01172: 4A80
    beq.w L_UNIT153_01540                              ; +$01174: 670003CA
    movea.l 44(a2),a4                                  ; +$01178: 286A002C
    move.l 32(a4),d0                                   ; +$0117C: 202C0020
    cmpi.l #$00000005,d0                               ; +$01180: 0C8000000005
    bcs.w L_UNIT153_01540                              ; +$01186: 650003B8
    cmpi.l #$0000FFFF,d0                               ; +$0118A: 0C800000FFFF
    bhi.w L_UNIT153_01540                              ; +$01190: 620003AE
    move.l d0,48(a2)                                   ; +$01194: 25400030
    move.l 36(a2),d1                                   ; +$01198: 222A0024
    cmp.l d1,d0                                        ; +$0119C: B081
    beq.w L_UNIT153_01540                              ; +$0119E: 670003A0
    move.l 36(a2),d0                                   ; +$011A2: 202A0024
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$011A6: FE11F700031D
    move.l a0,d5                                       ; +$011AC: 2A08
    cmpi.l #$00000018,d5                               ; +$011AE: 0C8500000018
    bls.w L_UNIT153_01540                              ; +$011B4: 6300038A
    move.l d5,d0                                       ; +$011B8: 2005
    andi.l #$00000001,d0                               ; +$011BA: 028000000001
    bne.w L_UNIT153_01540                              ; +$011C0: 6600037E
    move.l d5,52(a2)                                   ; +$011C4: 25450034
    movea.l d5,a1                                      ; +$011C8: 2245
    movea.l $0004.w,a6                                 ; +$011CA: 2C780004
    jsr -534(a6)                                       ; +$011CE: 4EAEFDEA
    tst.l d0                                           ; +$011D2: 4A80
    beq.w L_UNIT153_01540                              ; +$011D4: 6700036A
    move.l 52(a2),d0                                   ; +$011D8: 202A0034
    subi.l #$00000018,d0                               ; +$011DC: 048000000018
    movea.l d0,a1                                      ; +$011E2: 2240
    movea.l $0004.w,a6                                 ; +$011E4: 2C780004
    jsr -534(a6)                                       ; +$011E8: 4EAEFDEA
    tst.l d0                                           ; +$011EC: 4A80
    beq.w L_UNIT153_01540                              ; +$011EE: 67000350
    movea.l 52(a2),a4                                  ; +$011F2: 286A0034
    move.l -16(a4),d0                                  ; +$011F6: 202CFFF0
    move.l 36(a2),d1                                   ; +$011FA: 222A0024
    cmp.l d1,d0                                        ; +$011FE: B081
    bne.w L_UNIT153_01540                              ; +$01200: 6600033E
    move.l #$00000000,d0                               ; +$01204: 203C00000000
    move.w -12(a4),d0                                  ; +$0120A: 302CFFF4
    tst.l d0                                           ; +$0120E: 4A80
    beq.w L_UNIT153_01220                              ; +$01210: 6700000E
    andi.w #$FFFD,d0                                   ; +$01214: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$01218: 0C400001
    bne.w L_UNIT153_01540                              ; +$0121C: 66000322
L_UNIT153_01220:
    movea.l 52(a2),a4                                  ; +$01220: 286A0034
    move.l -20(a4),d0                                  ; +$01224: 202CFFEC
    cmpi.l #$00000011,d0                               ; +$01228: 0C8000000011
    bcs.w L_UNIT153_01540                              ; +$0122E: 65000310
    subi.l #$00000010,d0                               ; +$01232: 048000000010
    tst.l d0                                           ; +$01238: 4A80
    blt.w L_UNIT153_01540                              ; +$0123A: 6D000304
    move.l d0,56(a2)                                   ; +$0123E: 25400038
    move.l 52(a2),d0                                   ; +$01242: 202A0034
    move.l 56(a2),d1                                   ; +$01246: 222A0038
    add.l d1,d0                                        ; +$0124A: D081
    bcs.w L_UNIT153_01540                              ; +$0124C: 650002F2
    move.l d0,60(a2)                                   ; +$01250: 2540003C
    subq.l #1,d0                                       ; +$01254: 5380
    movea.l d0,a1                                      ; +$01256: 2240
    movea.l $0004.w,a6                                 ; +$01258: 2C780004
    jsr -534(a6)                                       ; +$0125C: 4EAEFDEA
    tst.l d0                                           ; +$01260: 4A80
    beq.w L_UNIT153_01540                              ; +$01262: 670002DC
    move.l 48(a2),d0                                   ; +$01266: 202A0030
    dc.b $FE,$11,$F7,$00,$03,$1D  ; +$0126A: FE11F700031D
    move.l a0,d5                                       ; +$01270: 2A08
    cmpi.l #$00000018,d5                               ; +$01272: 0C8500000018
    bls.w L_UNIT153_01540                              ; +$01278: 630002C6
    move.l d5,d0                                       ; +$0127C: 2005
    andi.l #$00000001,d0                               ; +$0127E: 028000000001
    bne.w L_UNIT153_01540                              ; +$01284: 660002BA
    move.l d5,64(a2)                                   ; +$01288: 25450040
    movea.l d5,a1                                      ; +$0128C: 2245
    movea.l $0004.w,a6                                 ; +$0128E: 2C780004
    jsr -534(a6)                                       ; +$01292: 4EAEFDEA
    tst.l d0                                           ; +$01296: 4A80
    beq.w L_UNIT153_01540                              ; +$01298: 670002A6
    move.l 64(a2),d0                                   ; +$0129C: 202A0040
    subi.l #$00000018,d0                               ; +$012A0: 048000000018
    movea.l d0,a1                                      ; +$012A6: 2240
    movea.l $0004.w,a6                                 ; +$012A8: 2C780004
    jsr -534(a6)                                       ; +$012AC: 4EAEFDEA
    tst.l d0                                           ; +$012B0: 4A80
    beq.w L_UNIT153_01540                              ; +$012B2: 6700028C
    movea.l 64(a2),a4                                  ; +$012B6: 286A0040
    move.l -16(a4),d0                                  ; +$012BA: 202CFFF0
    move.l 48(a2),d1                                   ; +$012BE: 222A0030
    cmp.l d1,d0                                        ; +$012C2: B081
    bne.w L_UNIT153_01540                              ; +$012C4: 6600027A
    move.l #$00000000,d0                               ; +$012C8: 203C00000000
    move.w -12(a4),d0                                  ; +$012CE: 302CFFF4
    tst.l d0                                           ; +$012D2: 4A80
    beq.w L_UNIT153_012E4                              ; +$012D4: 6700000E
    andi.w #$FFFD,d0                                   ; +$012D8: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$012DC: 0C400001
    bne.w L_UNIT153_01540                              ; +$012E0: 6600025E
L_UNIT153_012E4:
    movea.l 64(a2),a4                                  ; +$012E4: 286A0040
    move.l -20(a4),d0                                  ; +$012E8: 202CFFEC
    cmpi.l #$00014010,d0                               ; +$012EC: 0C8000014010
    bcs.w L_UNIT153_01540                              ; +$012F2: 6500024C
    subi.l #$00000010,d0                               ; +$012F6: 048000000010
    tst.l d0                                           ; +$012FC: 4A80
    blt.w L_UNIT153_01540                              ; +$012FE: 6D000240
    move.l d0,68(a2)                                   ; +$01302: 25400044
    move.l 64(a2),d0                                   ; +$01306: 202A0040
    move.l 68(a2),d1                                   ; +$0130A: 222A0044
    add.l d1,d0                                        ; +$0130E: D081
    bcs.w L_UNIT153_01540                              ; +$01310: 6500022E
    move.l d0,72(a2)                                   ; +$01314: 25400048
    subq.l #1,d0                                       ; +$01318: 5380
    movea.l d0,a1                                      ; +$0131A: 2240
    movea.l $0004.w,a6                                 ; +$0131C: 2C780004
    jsr -534(a6)                                       ; +$01320: 4EAEFDEA
    tst.l d0                                           ; +$01324: 4A80
    beq.w L_UNIT153_01540                              ; +$01326: 67000218
    move.l 52(a2),d0                                   ; +$0132A: 202A0034
    move.l 72(a2),d1                                   ; +$0132E: 222A0048
    cmp.l d1,d0                                        ; +$01332: B081
    bcc.w L_UNIT153_0134A                              ; +$01334: 64000014
    move.l 64(a2),d0                                   ; +$01338: 202A0040
    move.l 60(a2),d1                                   ; +$0133C: 222A003C
    cmp.l d1,d0                                        ; +$01340: B081
    bcc.w L_UNIT153_0134A                              ; +$01342: 64000006
    bra.w L_UNIT153_01540                              ; +$01346: 600001F8
L_UNIT153_0134A:
    move.l 24(a2),d4                                   ; +$0134A: 282A0018
    move.l 16(a2),d0                                   ; +$0134E: 202A0010
    subq.l #1,d0                                       ; +$01352: 5380
    add.l d0,d4                                        ; +$01354: D880
    bcs.w L_UNIT153_01540                              ; +$01356: 650001E8
    bvs.w L_UNIT153_01540                              ; +$0135A: 690001E4
    move.l 32(a2),d5                                   ; +$0135E: 2A2A0020
    bsr.w L_UNIT153_01552                              ; +$01362: 610001EE
    tst.l d1                                           ; +$01366: 4A81
    beq.w L_UNIT153_01540                              ; +$01368: 670001D6
    move.l 28(a2),d1                                   ; +$0136C: 222A001C
    add.l d1,d0                                        ; +$01370: D081
    bcs.w L_UNIT153_01540                              ; +$01372: 650001CC
    move.l 20(a2),d1                                   ; +$01376: 222A0014
    add.l d1,d0                                        ; +$0137A: D081
    bcs.w L_UNIT153_01540                              ; +$0137C: 650001C2
    move.l 56(a2),d1                                   ; +$01380: 222A0038
    cmp.l d1,d0                                        ; +$01384: B081
    bhi.w L_UNIT153_01540                              ; +$01386: 620001B8
    move.l 12(a2),d0                                   ; +$0138A: 202A000C
    move.l 4(a2),d1                                    ; +$0138E: 222A0004
    add.l d0,d1                                        ; +$01392: D280
    tst.l d1                                           ; +$01394: 4A81
    ble.w L_UNIT153_01540                              ; +$01396: 6F0001A8
    cmpi.l #$00000140,d1                               ; +$0139A: 0C8100000140
    ble.w L_UNIT153_013AA                              ; +$013A0: 6F000008
    move.l #$00000140,d1                               ; +$013A4: 223C00000140
L_UNIT153_013AA:
    move.l 12(a2),d0                                   ; +$013AA: 202A000C
    tst.l d0                                           ; +$013AE: 4A80
    bpl.w L_UNIT153_013CA                              ; +$013B0: 6A000018
    move.l #$00000000,d4                               ; +$013B4: 283C00000000
    sub.l d0,d4                                        ; +$013BA: 9880
    move.l d4,92(a2)                                   ; +$013BC: 2544005C
    move.l #$00000000,d0                               ; +$013C0: 203C00000000
    bra.w L_UNIT153_013D4                              ; +$013C6: 6000000C
L_UNIT153_013CA:
    move.l #$00000000,d4                               ; +$013CA: 283C00000000
    move.l d4,92(a2)                                   ; +$013D0: 2544005C
L_UNIT153_013D4:
    move.l d0,76(a2)                                   ; +$013D4: 2540004C
    sub.l d0,d1                                        ; +$013D8: 9280
    tst.l d1                                           ; +$013DA: 4A81
    ble.w L_UNIT153_01540                              ; +$013DC: 6F000162
    move.l d1,84(a2)                                   ; +$013E0: 25410054
    move.l 8(a2),d0                                    ; +$013E4: 202A0008
    move.l (a2),d1                                     ; +$013E8: 2212
    add.l d0,d1                                        ; +$013EA: D280
    tst.l d1                                           ; +$013EC: 4A81
    ble.w L_UNIT153_01540                              ; +$013EE: 6F000150
    cmpi.l #$00000100,d1                               ; +$013F2: 0C8100000100
    ble.w L_UNIT153_01402                              ; +$013F8: 6F000008
    move.l #$00000100,d1                               ; +$013FC: 223C00000100
L_UNIT153_01402:
    move.l 8(a2),d0                                    ; +$01402: 202A0008
    tst.l d0                                           ; +$01406: 4A80
    bpl.w L_UNIT153_01422                              ; +$01408: 6A000018
    move.l #$00000000,d4                               ; +$0140C: 283C00000000
    sub.l d0,d4                                        ; +$01412: 9880
    move.l d4,96(a2)                                   ; +$01414: 25440060
    move.l #$00000000,d0                               ; +$01418: 203C00000000
    bra.w L_UNIT153_0142C                              ; +$0141E: 6000000C
L_UNIT153_01422:
    move.l #$00000000,d4                               ; +$01422: 283C00000000
    move.l d4,96(a2)                                   ; +$01428: 25440060
L_UNIT153_0142C:
    move.l d0,80(a2)                                   ; +$0142C: 25400050
    sub.l d0,d1                                        ; +$01430: 9280
    tst.l d1                                           ; +$01432: 4A81
    ble.w L_UNIT153_01540                              ; +$01434: 6F00010A
    move.l d1,88(a2)                                   ; +$01438: 25410058
    move.l 80(a2),d0                                   ; +$0143C: 202A0050
    move.l #$00000140,d1                               ; +$01440: 223C00000140
    mulu.w d1,d0                                       ; +$01446: C0C1
    move.l 76(a2),d1                                   ; +$01448: 222A004C
    add.l d1,d0                                        ; +$0144C: D081
    move.l 64(a2),d1                                   ; +$0144E: 222A0040
    add.l d1,d0                                        ; +$01452: D081
    move.l d0,116(a2)                                  ; +$01454: 25400074
    move.l 20(a2),d0                                   ; +$01458: 202A0014
    move.l 4(a2),d1                                    ; +$0145C: 222A0004
    divu.w d1,d0                                       ; +$01460: 80C1
    move.l d0,d4                                       ; +$01462: 2800
    andi.l #$0000FFFF,d0                               ; +$01464: 02800000FFFF
    move.l d0,100(a2)                                  ; +$0146A: 25400064
    swap d4                                            ; +$0146E: 4844
    andi.l #$0000FFFF,d4                               ; +$01470: 02840000FFFF
    move.l d4,104(a2)                                  ; +$01476: 25440068
    move.l 92(a2),d0                                   ; +$0147A: 202A005C
    move.l 20(a2),d1                                   ; +$0147E: 222A0014
    mulu.w d1,d0                                       ; +$01482: C0C1
    move.l 4(a2),d1                                    ; +$01484: 222A0004
    divu.w d1,d0                                       ; +$01488: 80C1
    move.l d0,d4                                       ; +$0148A: 2800
    andi.l #$0000FFFF,d0                               ; +$0148C: 02800000FFFF
    move.l d0,108(a2)                                  ; +$01492: 2540006C
    swap d4                                            ; +$01496: 4844
    andi.l #$0000FFFF,d4                               ; +$01498: 02840000FFFF
    move.l d4,112(a2)                                  ; +$0149E: 25440070
    move.l 96(a2),d0                                   ; +$014A2: 202A0060
    move.l d0,120(a2)                                  ; +$014A6: 25400078
    move.l 88(a2),d7                                   ; +$014AA: 2E2A0058
    subq.l #1,d7                                       ; +$014AE: 5387
L_UNIT153_014B0:
    move.l 120(a2),d0                                  ; +$014B0: 202A0078
    move.l 16(a2),d1                                   ; +$014B4: 222A0010
    mulu.w d1,d0                                       ; +$014B8: C0C1
    move.l (a2),d1                                     ; +$014BA: 2212
    divu.w d1,d0                                       ; +$014BC: 80C1
    andi.l #$0000FFFF,d0                               ; +$014BE: 02800000FFFF
    move.l 24(a2),d4                                   ; +$014C4: 282A0018
    add.l d0,d4                                        ; +$014C8: D880
    move.l 32(a2),d5                                   ; +$014CA: 2A2A0020
    bsr.w L_UNIT153_01552                              ; +$014CE: 61000082
    move.l 28(a2),d1                                   ; +$014D2: 222A001C
    add.l d1,d0                                        ; +$014D6: D081
    move.l 108(a2),d1                                  ; +$014D8: 222A006C
    add.l d1,d0                                        ; +$014DC: D081
    move.l 52(a2),d1                                   ; +$014DE: 222A0034
    add.l d1,d0                                        ; +$014E2: D081
    movea.l d0,a0                                      ; +$014E4: 2040
    movea.l 116(a2),a1                                 ; +$014E6: 226A0074
    move.l 112(a2),d4                                  ; +$014EA: 282A0070
    move.l 84(a2),d6                                   ; +$014EE: 2C2A0054
    subq.l #1,d6                                       ; +$014F2: 5386
    bra.w L_UNIT153_0158C                              ; +$014F4: 60000096
    dc.b $20,$2A,$00,$64,$22,$08,$D2,$80,$20,$41,$20,$2A  ; +$014F8: 202A00642208D2802041202A
    dc.b $00,$68,$D8,$80,$20,$2A,$00,$04,$B8,$80,$65,$00  ; +$01504: 0068D880202A0004B8806500
    dc.b $00,$06,$98,$80,$52,$88,$51,$CE,$FF,$DC  ; +$01510: 00069880528851CEFFDC
L_UNIT153_0151A:
    move.l 120(a2),d0                                  ; +$0151A: 202A0078
    addq.l #1,d0                                       ; +$0151E: 5280
    move.l d0,120(a2)                                  ; +$01520: 25400078
    move.l 116(a2),d0                                  ; +$01524: 202A0074
    addi.l #$00000140,d0                               ; +$01528: 068000000140
    move.l d0,116(a2)                                  ; +$0152E: 25400074
    dbra d7,L_UNIT153_014B0                            ; +$01532: 51CFFF7C
    move.l #$00000001,d3                               ; +$01536: 263C00000001
    bra.w L_UNIT153_01546                              ; +$0153C: 60000008
L_UNIT153_01540:
    move.l #$00000000,d3                               ; +$01540: 263C00000000
L_UNIT153_01546:
    lea 192(a7),a7                                     ; +$01546: 4FEF00C0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0154A: 4CDF77F7
    moveq #0,d2                                        ; +$0154E: 7400
    rts                                                ; +$01550: 4E75
L_UNIT153_01552:
    move.l #$00000000,d0                               ; +$01552: 203C00000000
L_UNIT153_01558:
    tst.l d4                                           ; +$01558: 4A84
    beq.w L_UNIT153_0157C                              ; +$0155A: 67000020
    btst #0,d4                                         ; +$0155E: 08040000
    beq.w L_UNIT153_0156C                              ; +$01562: 67000008
    add.l d5,d0                                        ; +$01566: D085
    bcs.w L_UNIT153_01584                              ; +$01568: 6500001A
L_UNIT153_0156C:
    lsr.l #1,d4                                        ; +$0156C: E28C
    beq.w L_UNIT153_0157C                              ; +$0156E: 6700000C
    lsl.l #1,d5                                        ; +$01572: E38D
    bcs.w L_UNIT153_01584                              ; +$01574: 6500000E
    bra.w L_UNIT153_01558                              ; +$01578: 6000FFDE
L_UNIT153_0157C:
    move.l #$00000001,d1                               ; +$0157C: 223C00000001
    rts                                                ; +$01582: 4E75
L_UNIT153_01584:
    move.l #$00000000,d1                               ; +$01584: 223C00000000
    rts                                                ; +$0158A: 4E75
L_UNIT153_0158C:
    move.l 100(a2),d5                                  ; +$0158C: 2A2A0064
    move.l 104(a2),d2                                  ; +$01590: 242A0068
    move.l 4(a2),d1                                    ; +$01594: 222A0004
L_UNIT153_01598:
    move.b (a0),(a1)                                   ; +$01598: 1290
    addq.l #1,a1                                       ; +$0159A: 5289
    adda.l d5,a0                                       ; +$0159C: D1C5
    add.l d2,d4                                        ; +$0159E: D882
    cmp.l d1,d4                                        ; +$015A0: B881
    bcs.w L_UNIT153_015AA                              ; +$015A2: 65000006
    sub.l d1,d4                                        ; +$015A6: 9881
    addq.l #1,a0                                       ; +$015A8: 5288
L_UNIT153_015AA:
    dbra d6,L_UNIT153_01598                            ; +$015AA: 51CEFFEC
    bra.w L_UNIT153_0151A                              ; +$015AE: 6000FF6A
    dc.b $47,$65,$74,$50  ; +$015B2: 47657450
