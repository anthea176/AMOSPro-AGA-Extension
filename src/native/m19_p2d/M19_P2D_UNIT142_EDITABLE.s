; AGA_NATIVE_MIN_CPU: MC68020
; PARTIAL_SOURCE_MIGRATION: UNIT142 pinned MC68020 code, audit remainder
; Selected native spans source-owned; remaining legacy mnemonics/data pinned
; Unit: UNIT142 | SHA256: 8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7
; Proven SHA-pinned AP20 unit, including its 34-byte V2 dispatcher.
; DC.B preserves unclassified code/data, GetP and AMOS linker markers.
; Mnemonic equivalence is NOT proven without --verify-vasm.
; MC68020: assemble with vasmm68k_mot -m68020

UNIT_UNIT142:
    include "M19_UNIT142_DISPATCH_V2_MC68020.s"
ENTRY_UNIT142_00022:
    include "M19_UNIT142_INIT_ENTRY_MC68020.s"
L_UNIT142_0005A:
    include "M19_UNIT142_R83_CLOSE_ENTRY_MC68020.s"
    include "M19_UNIT142_R83_MAIN_BRA_TARGET_MC68020.s"
    include "M19_UNIT142_R83_CLOSE_GUARD_MC68020.s"
    include "M19_UNIT142_R83_CLOSE_ISLAND_MC68020.s"
    include "M19_UNIT142_R83_CLOSE_CLEANUP_MC68020.s"
    include "M19_UNIT142_R83_CLOSE_CROSS_BSR_MC68020.s"
    include "M19_UNIT142_R83_CLOSE_POSTCALL_MC68020.s"
L_UNIT142_001C2:
    dcb.b 40,0
    include "M19_UNIT142_R83_CLOSE_SAFEWAIT_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_002A2_MC68020.s"
    dc.b $20,$6D,$FF,$FC,$4E,$A8,$01,$90,$4E,$75,$47,$65
    dc.b $74,$50
    include "M19_UNIT142_BLOCK_002B2_MC68020.s"
    dc.b $20,$6D,$FF,$FC,$4E,$A8,$01,$90,$4E,$75,$47,$65
    dc.b $74,$50
ENTRY_UNIT142_002C2:
    include "M19_UNIT142_GRAPHICS_GUARD_MC68020.s"
L_UNIT142_0030C:
    dc.b $67,$72,$61,$70,$68,$69,$63,$73,$2E,$6C,$69,$62
    dc.b $72,$61,$72,$79,$00,$00,$47,$65,$74,$50
ENTRY_UNIT142_00322:
    include "M19_UNIT142_GRAPHICS_SCREEN_MC68020.s"
L_UNIT142_00448:
    dc.b $69,$6E,$74,$75,$69,$74,$69,$6F,$6E,$2E,$6C,$69
    dc.b $62,$72,$61,$72,$79,$00
L_UNIT142_0045A:
    dc.b $67,$72,$61,$70,$68,$69,$63,$73,$2E,$6C,$69,$62
    dc.b $72,$61,$72,$79,$00,$00,$47,$65,$74,$50
    include "M19_UNIT142_LEGACY_OPEN_HEAD_MC68020.s"
L_LEGACY_SCREEN_OPEN_00164:
    dc.b $69,$6E,$74,$75,$69,$74,$69,$6F,$6E,$2E,$6C,$69
    dc.b $62,$72,$61,$72,$79,$00
L_LEGACY_SCREEN_OPEN_00176:
    dc.b $67,$72,$61,$70,$68,$69,$63,$73,$2E,$6C,$69,$62
    dc.b $72,$61,$72,$79,$00,$00
    include "M19_UNIT142_LEGACY_OPEN_HELPERS_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_00764_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_R83_TARGET_HEAD_MC68020.s"
    dc.b $61,$00,$4A,$42
    include "M19_UNIT142_R83_TARGET_BODY_MC68020.s"
    include "M19_UNIT142_R83_TARGET_BSR_660A_MC68020.s"
    include "M19_UNIT142_R83_TARGET_WAIT_MC68020.s"
    include "M19_UNIT142_R83_TARGET_BRA_WAIT_MC68020.s"
    include "M19_UNIT142_R83_TARGET_AUX_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_00A62_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_00A80_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_00BA2_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_00C9E_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_00D3C:
    include "M19_UNIT142_IFF_LOAD_BODY_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_01540_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_015C0_MC68020.s"
    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_015D8:
    include "M19_UNIT142_IFF_PALETTE_BODY_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_01BCA_MC68020.s"
    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00
ENTRY_UNIT142_01BDE:
    include "M19_UNIT142_IFF_AP20_PRECALL_MC68020.s"
    dc.b $FE,$11,$F7,$00,$00,$8C
    include "M19_UNIT142_BLOCK_01E12_MC68020.s"
    dc.b $4E,$71
    include "M19_UNIT142_BLOCK_01F32_MC68020.s"
    dc.b $FE,$11,$F7,$00,$00,$8C
    include "M19_UNIT142_BLOCK_020E6_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0219C:
    include "M19_UNIT142_BLOCK_0219C_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02360_MC68020.s"
    dc.b $2A,$1B,$28,$1B,$22,$1B,$20,$1B,$28,$6D,$01,$C8
    dc.b $2C,$0C,$4A,$86,$67,$00,$01,$FC,$2C,$14,$4A,$86
    dc.b $67,$00,$01,$F4,$24,$6C,$00,$20,$2C,$0A,$4A,$86
    dc.b $67,$00,$01,$E8,$2C,$6C,$00,$08,$2C,$0E,$4A,$86
    dc.b $67,$00,$01,$DC,$4A,$80,$6B,$00,$01,$D6,$4A,$81
    dc.b $6B,$00,$01,$D0,$4A,$83,$6B,$00,$01,$CA,$4A,$84
    dc.b $6F,$00,$01,$C4,$4A,$85,$6F,$00,$01,$BE,$2C,$2C
    dc.b $00,$0C,$4A,$86,$6F,$00,$01,$B4,$0C,$86,$00,$00
    dc.b $7F,$FF,$6E,$00,$01,$AA,$2C,$2C,$00,$10,$4A,$86
    dc.b $6F,$00,$01,$A0,$0C,$86,$00,$00,$7F,$FF,$6E,$00
    dc.b $01,$96,$2C,$2C,$00,$0C,$9C,$84,$4A,$86,$6B,$00
    dc.b $01,$8A,$B0,$86,$6E,$00,$01,$84,$2C,$2C,$00,$10
    dc.b $9C,$85,$4A,$86,$6B,$00,$01,$78,$B2,$86,$6E,$00
    dc.b $01,$72,$4A,$AA,$00,$08,$67,$00,$00,$08,$20,$52
    dc.b $60,$00,$00,$06,$20,$6A,$00,$04,$2C,$08,$4A,$86
    dc.b $67,$00,$01,$58,$20,$50,$2C,$08,$4A,$86,$67,$00
    dc.b $01,$4E,$2C,$3C,$00,$00,$00,$00,$3C,$10,$E7,$8E
    dc.b $BC,$AC,$00,$0C,$6D,$00,$01,$3C,$2C,$3C,$00,$00
    dc.b $00,$00,$3C,$28,$00,$02,$BC,$AC,$00,$10,$6D,$00
    dc.b $01,$2A,$2C,$3C,$00,$00,$00,$00,$1C,$28,$00,$05
    dc.b $BC,$AC,$00,$1C,$66,$00,$01,$18,$4A,$86,$6F,$00
    dc.b $01,$12,$0C,$86,$00,$00,$00,$08,$6E,$00,$01,$08
    dc.b $24,$06,$22,$48,$50,$89,$2C,$19,$4A,$86,$67,$00
    dc.b $00,$FA,$0C,$86,$FF,$FF,$FF,$FF,$67,$00,$00,$F0
    dc.b $53,$82,$66,$00,$FF,$EA,$24,$3C,$00,$00,$00,$00
    dc.b $14,$28,$00,$05,$2C,$3C,$00,$00,$00,$01,$E3,$8E
    dc.b $53,$82,$66,$00,$FF,$FA,$B6,$86,$64,$00,$00,$CC
    dc.b $2F,$06,$2C,$2A,$00,$14,$02,$86,$00,$00,$00,$01
    dc.b $67,$00,$00,$54,$2F,$00,$2F,$01,$2F,$08,$2F,$09
    dc.b $20,$6A,$00,$0C,$2C,$08,$4A,$86,$67,$00,$00,$2E
    dc.b $2C,$78,$00,$04,$4E,$AE,$FE,$8C,$4A,$80,$67,$00
    dc.b $00,$20,$2C,$2A,$00,$14,$02,$86,$FF,$FF,$FF,$FE
    dc.b $25,$46,$00,$14,$2C,$6C,$00,$08,$22,$5F,$20,$5F
    dc.b $22,$1F,$20,$1F,$60,$00,$00,$14,$2C,$6C,$00,$08
    dc.b $22,$5F,$20,$5F,$22,$1F,$20,$1F,$2C,$1F,$60,$00
    dc.b $00,$6A,$2C,$1F,$2F,$03,$2F,$06,$28,$48,$24,$00
    dc.b $26,$01,$2E,$3C,$00,$00,$00,$01,$2C,$2F,$00,$04
    dc.b $CC,$87,$4A,$86,$67,$00,$00,$0C,$2C,$3C,$00,$00
    dc.b $00,$F0,$60,$00,$00,$08,$2C,$3C,$00,$00,$00,$00
    dc.b $20,$02,$22,$03,$20,$4C,$22,$4C,$24,$7C,$00,$00
    dc.b $00,$00,$4E,$AE,$FF,$E2,$4A,$80,$67,$00,$00,$18
    dc.b $4E,$AE,$FF,$1C,$E3,$8F,$BE,$97,$66,$00,$FF,$C2
    dc.b $26,$3C,$00,$00,$00,$01,$60,$00,$00,$08,$26,$3C
    dc.b $00,$00,$00,$00,$50,$8F,$60,$00,$00,$08,$26,$3C
    dc.b $00,$00,$00,$00,$4C,$DF,$77,$F7,$74,$00,$4E,$75
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02584_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02690_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0273C_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0282C:
    include "M19_UNIT142_BLOCK_0282C_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0299A:
    include "M19_UNIT142_COLOR_RANGE_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02BBA_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02C2A_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02C9A_MC68020.s"
    dc.b $69,$6E,$70,$75,$74,$2E,$64,$65,$76,$69,$63,$65
    dc.b $00,$00,$47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02D90_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_02DFA_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_02E64:
    include "M19_UNIT142_ENTRY_02E64_MC68020.s"
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0317C_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_031E4_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_03270:
    include "M19_UNIT142_ENTRY_03270_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_034F4:
    include "M19_UNIT142_ENTRY_034F4_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_0398C_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_03A0C_MC68020.s"
    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_03A24_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_03B52_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_03C46:
    include "M19_UNIT142_ENTRY_03C46_MC68020.s"
    dc.b $20,$3C,$00,$00,$00,$00
    include "M19_UNIT142_BLOCK_04102_MC68020.s"
    dc.b $64,$6F,$73,$2E,$6C,$69,$62,$72,$61,$72,$79,$00
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0411A_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_04256:
    include "M19_UNIT142_ENTRY_04256_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_044EA:
    include "M19_UNIT142_ENTRY_044EA_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0479E:
    include "M19_UNIT142_ENTRY_0479E_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_04B40:
    include "M19_UNIT142_ENTRY_04B40_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_04D4C:
    include "M19_UNIT142_ENTRY_04D4C_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_04F58:
    include "M19_UNIT142_ENTRY_04F58_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_05150:
    include "M19_UNIT142_BLOCK_05150_MC68020.s"
    dc.b $2F,$0E,$2F,$08,$2F,$0A,$61,$00,$FF,$DC,$4A,$80
    dc.b $67,$00,$00,$1E,$43,$FA,$00,$26,$22,$BC,$00,$00
    dc.b $00,$00,$23,$7C,$00,$00,$00,$00,$00,$04,$22,$40
    dc.b $2C,$6A,$00,$08,$61,$00,$03,$B2,$24,$5F,$20,$5F
    dc.b $2C,$5F,$4E,$AE,$FF,$BE,$4E,$75
L_UNIT142_05302:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$47,$65,$74,$50
ENTRY_UNIT142_0530E:
    include "M19_UNIT142_ENTRY_0530E_MC68020.s"
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$47,$65,$74,$50
ENTRY_UNIT142_05706:
    include "M19_UNIT142_BLOCK_05706_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_058C6:
    include "M19_UNIT142_BLOCK_058C6_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_05C7A:
    include "M19_UNIT142_BLOCK_05C7A_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0609E:
    include "M19_UNIT142_ENTRY_0609E_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0652C_MC68020.s"
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$47,$65,$74,$50
ENTRY_UNIT142_06678:
    include "M19_UNIT142_ENTRY_06678_MC68020.s"
    dc.b $47,$65,$74,$50
ENTRY_UNIT142_0700A:
    include "M19_UNIT142_ENTRY_0700A_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0725A_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_07342_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$30
    include "M19_UNIT142_BLOCK_07360_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$33
    include "M19_UNIT142_BLOCK_0746E_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$20
    include "M19_UNIT142_BLOCK_07482_MC68020.s"
L_UNIT142_077D0:
    dc.b $41,$47,$41,$50,$49,$43,$20,$20,$47,$65,$74,$50
    include "M19_UNIT142_BLOCK_077DC_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0781C_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_07878_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_078A4_MC68020.s"
    dc.b $4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71
    dc.b $4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71
    dc.b $4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71,$4E,$71
    dc.b $4E,$71,$4E,$71,$47,$65,$74,$50
    include "M19_UNIT142_BLOCK_07B56_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_07BC8_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_08568_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_08618_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_08CDA_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_08D78_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_09428_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0948C_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0949E_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$30
    include "M19_UNIT142_BLOCK_094BE_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$33
    include "M19_UNIT142_BLOCK_09532_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$20
    include "M19_UNIT142_BLOCK_09546_MC68020.s"
    dc.b $46,$49,$43,$4F,$4E,$38,$20,$20,$47,$65,$74,$50
    include "M19_UNIT142_BLOCK_09564_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_095EC_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_09790_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_09930_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_09994_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_099A6_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$30
    include "M19_UNIT142_BLOCK_099C6_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$33
    include "M19_UNIT142_BLOCK_09A6C_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$20
    include "M19_UNIT142_BLOCK_09A80_MC68020.s"
    dc.b $46,$49,$43,$48,$49,$50,$38,$20,$47,$65,$74,$50
    include "M19_UNIT142_BLOCK_09A9E_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_09B16_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_09C80_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_09F6A_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0A006_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0A476_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0A6E2_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0A6FA_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$30
    include "M19_UNIT142_BLOCK_0A71A_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$33
    include "M19_UNIT142_BLOCK_0AB96_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$20
    include "M19_UNIT142_BLOCK_0ABB4_MC68020.s"
    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20
L_UNIT142_0ABCE:
    include "M19_UNIT142_CBLOCK_CORE_0ABCE_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0AF3A_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0B0A6_MC68020.s"
    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20
L_UNIT142_0B592:
    include "M19_UNIT142_CBLOCK_CORE_0B592_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0B8FE_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0BA5E_MC68020.s"
    dc.b $41,$47,$41,$43,$42,$4C,$4B,$20
L_UNIT142_0BF5A:
    include "M19_UNIT142_CBLOCK_CORE_0BF5A_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0C2C6_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0C30E_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0C344_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0C38C_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0C3C2_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0C41C_MC68020.s"
    dc.b $60,$00,$00,$08
    include "M19_UNIT142_BLOCK_0C8BE_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0C8D8_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0C946_MC68020.s"
    dc.b $60,$00,$00,$08
    include "M19_UNIT142_BLOCK_0CED8_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0CEF2_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0CF3E_MC68020.s"
    dc.b $47,$65,$74,$50
    include "M19_UNIT142_BLOCK_0D336_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0D694_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_BLOCK_0D7AA_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$30
    include "M19_UNIT142_BLOCK_0D7C8_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$33
    include "M19_UNIT142_BLOCK_0D986_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$20
    include "M19_UNIT142_BLOCK_0D99A_MC68020.s"
    dc.b $41,$47,$41,$50,$49,$43,$20,$20
    include "M19_UNIT142_P0E_OBJECT_CORE_MC68020.s"
UNIT142_P0E_OBJECT_ROOT:
    dcb.b 8,0
UNIT142_P0E_OBJECT_TABLE:
    dcb.b 1536,0
    include "M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s"
    include "M19_UNIT142_P0F_STAMP_HEAD_MC68020.s"
    dc.b $FE,$11,$F7,$00,$03,$1D
    include "M19_UNIT142_P0F_STAMP_BODY_MC68020.s"
    include "M19_UNIT142_P0F_BSR_PUT_MC68020.s"
    include "M19_UNIT142_P0F_BIND_CHECK_MC68020.s"
    include "M19_UNIT142_P0F_BSR_READ_MC68020.s"
    include "M19_UNIT142_P0F_BIND_RETURN_MC68020.s"
UNIT142_P0F_STAMP_TABLE:
    dcb.b 1024,0
UNIT142_P1C_OPEN_ENTRY:
    include "M19_UNIT142_P1C_PRIORITY_OPEN_MC68020.s"
UNIT142_P1C_CONTEXT:
    dcb.b 8,0
UNIT142_P1D_LIMIT_TABLE:
    dcb.b 1040,0
ENTRY_UNIT142_0F4E2:
    include "M19_UNIT142_P1D_LIMIT_OPEN_MC68020.s"
