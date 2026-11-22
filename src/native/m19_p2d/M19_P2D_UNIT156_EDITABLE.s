; AGA_NATIVE_MIN_CPU: MC68020
; PARTIAL_SOURCE_MIGRATION: native UNIT156 public + main + tail + nibble + DOS guard; audit remainder
; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)
; Unit: UNIT156 | SHA256: 4e14633eea1ed1fd906ee9f4691e3a0bfc3c6086aaea858f8d2fc1a88ea8f31b
; Proven SHA-pinned AP20 unit, including its 34-byte V2 dispatcher.
; DC.B preserves unclassified code/data, GetP and AMOS linker markers.
; Mnemonic equivalence is NOT proven without --verify-vasm.
; MC68020: assemble with vasmm68k_mot -m68020

UNIT_UNIT156:
    subq.l #4,a7                                       ; +$00000: 598F
    movem.l d0/a0,-(a7)                                ; +$00002: 48E78080
    movea.l 12(a7),a0                                  ; +$00006: 206F000C
    moveq #0,d0                                        ; +$0000A: 7000
    move.w (a0)+,d0                                    ; +$0000C: 3018
    move.l a0,12(a7)                                   ; +$0000E: 2F48000C
    lea ENTRY_UNIT156_00022(pc),a0                     ; +$00012: 41FA000E
    adda.l d0,a0                                       ; +$00016: D1C0
    move.l a0,8(a7)                                    ; +$00018: 2F480008
    movem.l (a7)+,d0/a0                                ; +$0001C: 4CDF0101
    rts                                                ; +$00020: 4E75
ENTRY_UNIT156_00022:
    include "M19_UNIT156_PUBLIC_GET_MC68020.s"
    include "M19_UNIT156_MAIN_BODY_MC68020.s"
    dc.b $00,$07,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$007EE: 0007670000040DD4528C0800
    dc.b $00,$06,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$007FA: 0006670000040DD4528C0800
    dc.b $00,$05,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$00806: 0005670000040DD4528C0800
    dc.b $00,$04,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$00812: 0004670000040DD4528C0800
    dc.b $00,$03,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$0081E: 0003670000040DD4528C0800
    dc.b $00,$02,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$0082A: 0002670000040DD4528C0800
    dc.b $00,$01,$67,$00,$00,$04,$0D,$D4,$52,$8C,$08,$00  ; +$00836: 0001670000040DD4528C0800
    dc.b $00,$00,$67,$00,$00,$04,$0D,$D4,$52,$8C,$51,$CA  ; +$00842: 0000670000040DD4528C51CA
    dc.b $FF,$9C  ; +$0084E: FF9C
L_UNIT156_00850:
    include "M19_UNIT156_CONVERT_TAIL_MC68020.s"
L_UNIT156_00926:
    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00  ; +$00926: 646F732E6C69627261727900
L_UNIT156_00932:
    include "M19_UNIT156_NIBBLE_MC68020.s"
L_UNIT156_0095E:
    dc.b $00,$00,$00,$00,$00,$00,$00,$01,$00,$00,$01,$00  ; +$0095E: 000000000000000100000100
    dc.b $00,$00,$01,$01,$00,$01,$00,$00,$00,$01,$00,$01  ; +$0096A: 000001010001000000010001
    dc.b $00,$01,$01,$00,$00,$01,$01,$01,$01,$00,$00,$00  ; +$00976: 000101000001010101000000
    dc.b $01,$00,$00,$01,$01,$00,$01,$00,$01,$00,$01,$01  ; +$00982: 010000010100010001000101
    dc.b $01,$01,$00,$00,$01,$01,$00,$01,$01,$01,$01,$00  ; +$0098E: 010100000101000101010100
    dc.b $01,$01,$01,$01  ; +$0099A: 01010101
L_UNIT156_0099E:
    include "M19_UNIT156_DOS_GUARD_MC68020.s"
    dc.b $47,$65,$74,$50  ; +$009C8: 47657450
