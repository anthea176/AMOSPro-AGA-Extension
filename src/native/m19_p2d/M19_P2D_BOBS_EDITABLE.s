; AGA_NATIVE_MIN_CPU: MC68020
; Original AMOS Main rjsr indices (source tools/amos_main_abi.py).
AMOS_MAIN_GETADR     equ 797
AMOS_MAIN_CHANGE     equ 819
AMOS_MAIN_LIST_CREATE equ 91
AMOS_MAIN_LIST_DELETE equ 93
; M19 P2d BOBS native editable assembly: P2c/P2d manually authored.
; WARNING: remaining BOBS routines are still audit-restored instructions/data.
; Verified external emitter aliases (relative to native group):
route_arm_end equ UNIT_BOBS+$05E50
route_unwind equ UNIT_BOBS+$05E80
route_return equ UNIT_BOBS+$05EC8
route_all_next equ UNIT_BOBS+$05EFA
route_all_return equ UNIT_BOBS+$05F22
img_gate_draw_return equ UNIT_BOBS+$06276
b7_end_pending equ UNIT_BOBS+$06F94
b7_end_return equ UNIT_BOBS+$06FA0
b8_b7_end_pending equ UNIT_BOBS+$0724C
b8_b7_register_magic equ UNIT_BOBS+$07278
b8_b7_register_entry equ UNIT_BOBS+$0727C
b8_b7_register_check_root equ UNIT_BOBS+$072F8
b8_b7_register_commit equ UNIT_BOBS+$0731E
b8_b7_register_arm equ UNIT_BOBS+$07328
b8_b7_register_return equ UNIT_BOBS+$0733A
b8s1_bank_free_registry_empty equ UNIT_BOBS+$07728
b8s1_bank_free_registry_ok equ UNIT_BOBS+$07730
b8s1_bank_free_scan equ UNIT_BOBS+$07868
b8s1_bank_free_next_check equ UNIT_BOBS+$078A4
b8s1_bank_free_disable equ UNIT_BOBS+$078D4
b8s1_bank_free_next_off equ UNIT_BOBS+$078F6
b8s1_bank_free_release equ UNIT_BOBS+$0793A
b8s1_bank_free_return equ UNIT_BOBS+$07952
p1b_fully_clipped equ UNIT_BOBS+$07A08
p1b_hotspot_origin_entry equ UNIT_BOBS+$07A14
p2a_pair_chip_resolve_entry equ UNIT_BOBS+$08BB6
p2a_pair_chip_return equ UNIT_BOBS+$08E10
p2a_pair_hotspot_entry equ UNIT_BOBS+$08E20
p2a_h0_scan equ UNIT_BOBS+$08EEA
p2a_h0_found equ UNIT_BOBS+$08F1C
p2a_h1_scan equ UNIT_BOBS+$08FEC
p2a_h1_found equ UNIT_BOBS+$0901E
p2a_hot_refuse equ UNIT_BOBS+$0917A
p2a_pair_geometry_entry equ UNIT_BOBS+$0918A
p2a_g0_left_ok_0 equ UNIT_BOBS+$09396
p2a_g0_right_ok_0 equ UNIT_BOBS+$093A8
p2a_g0_left_ok_4 equ UNIT_BOBS+$093BA
p2a_g0_right_ok_4 equ UNIT_BOBS+$093CC
p2a_g0_global_set equ UNIT_BOBS+$093FC
p2a_g0_global_clip_4 equ UNIT_BOBS+$09434
p2a_g0_global_clip_12 equ UNIT_BOBS+$09458
p2a_g0_global_done equ UNIT_BOBS+$09458
p2a_g0_local_clip_0 equ UNIT_BOBS+$094B4
p2a_g0_local_clip_4 equ UNIT_BOBS+$094C6
p2a_g0_local_clip_8 equ UNIT_BOBS+$094D8
p2a_g0_local_clip_12 equ UNIT_BOBS+$094EA
p2a_g0_local_done equ UNIT_BOBS+$094EA
p2a_g0_complete equ UNIT_BOBS+$09526
p2a_g1_right_ok_0 equ UNIT_BOBS+$09644
p2a_g1_right_ok_4 equ UNIT_BOBS+$09668
p2a_g1_global_set equ UNIT_BOBS+$09698
p2a_g1_global_clip_0 equ UNIT_BOBS+$096BE
p2a_g1_global_clip_4 equ UNIT_BOBS+$096D0
p2a_g1_global_clip_8 equ UNIT_BOBS+$096E2
p2a_g1_global_clip_12 equ UNIT_BOBS+$096F4
p2a_g1_global_done equ UNIT_BOBS+$096F4
p2a_g1_local_set equ UNIT_BOBS+$0972C
p2a_g1_local_clip_4 equ UNIT_BOBS+$09764
p2a_g1_local_clip_12 equ UNIT_BOBS+$09788
p2a_g1_local_done equ UNIT_BOBS+$09788
p2a_g1_empty equ UNIT_BOBS+$097A4
p2a_g1_complete equ UNIT_BOBS+$097C4
p2a_geo_reject equ UNIT_BOBS+$09848
p2a_pair_entry equ UNIT_BOBS+$09858
p2a_v0_validated equ UNIT_BOBS+$09942
p2a_keep_left equ UNIT_BOBS+$099FA
p2a_keep_right equ UNIT_BOBS+$09A32
p2a_keep_bottom equ UNIT_BOBS+$09A4E
p2a_row equ UNIT_BOBS+$09A7A
p2a_opaque_0 equ UNIT_BOBS+$09AC4
p2a_next_pixel equ UNIT_BOBS+$09B0A
p2a_no_hit equ UNIT_BOBS+$09B2E
p2a_hit equ UNIT_BOBS+$09B38
p2a_return equ UNIT_BOBS+$09B48
p2a_collision_query_entry equ UNIT_BOBS+$09B54
p2a_query_return equ UNIT_BOBS+$09D26
p2a_public_col_done equ UNIT_BOBS+$09E26
p2b_mode equ UNIT_BOBS+$09E48
p2b_mode_normal equ UNIT_BOBS+$09E70
p2b_free_slot equ UNIT_BOBS+$09E74
p2b_free_slot_done equ UNIT_BOBS+$09E94
p2b_flip_read equ UNIT_BOBS+$09ED4
p2b_flip_ok equ UNIT_BOBS+$09F0C
p2b_variant_miss equ UNIT_BOBS+$09FBE
p2b_variant_prepare equ UNIT_BOBS+$09FEC
p2b_variant_ok equ UNIT_BOBS+$0A066
p2b_variant_fail equ UNIT_BOBS+$0A06C
p2b_variant_return equ UNIT_BOBS+$0A06E
p2b_adjust_anchor equ UNIT_BOBS+$0A07A
p2b_axis_done_0 equ UNIT_BOBS+$0A090
p2b_axis_done_1 equ UNIT_BOBS+$0A0A8
p2b_paint_normal equ UNIT_BOBS+$0A0F2
p2b_paint_fail equ UNIT_BOBS+$0A0FC
p2b_geometry equ UNIT_BOBS+$0A106
p2b_geo_done_0 equ UNIT_BOBS+$0A166
p2b_geo_done_1 equ UNIT_BOBS+$0A1B8
p2b_geometry_fail equ UNIT_BOBS+$0A1C4
p2b_closed equ UNIT_BOBS+$0A20A
p2b_close_restore equ UNIT_BOBS+$0A222
p2b_bank_free equ UNIT_BOBS+$0A228
p2b_bank_free_return equ UNIT_BOBS+$0A24E
p2b_purge_loop equ UNIT_BOBS+$0A264
p2b_clear_mode equ UNIT_BOBS+$0A276
p2b_purge_slot equ UNIT_BOBS+$0A27C
p2b_purge_next equ UNIT_BOBS+$0A280
p2b_materialize_chip equ UNIT_BOBS+$0A43E
p2b_slots equ UNIT_BOBS+$0A4C4
p2d_clear_mode equ UNIT_BOBS+$0B70E
p2d_close_return equ UNIT_BOBS+$0B718

; AGA_NATIVE_MIN_CPU: MC68020
; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)
; Unit: BOBS | SHA256: cc37518ac3407c7d03352c02bb3aeb88cb2b4d15ad3b9414c31cb43e404ea62d
; Proven SHA-pinned AP20 unit, including its 34-byte V2 dispatcher.
; DC.B preserves unclassified code/data, GetP and AMOS linker markers.
; Mnemonic equivalence is NOT proven without --verify-vasm.
; MC68020: assemble with vasmm68k_mot -m68020

UNIT_BOBS:
    subq.l #4,a7                                       ; +$00000: 598F
    movem.l d0/a0,-(a7)                                ; +$00002: 48E78080
    movea.l 12(a7),a0                                  ; +$00006: 206F000C
    moveq #0,d0                                        ; +$0000A: 7000
    move.w (a0)+,d0                                    ; +$0000C: 3018
    move.l a0,12(a7)                                   ; +$0000E: 2F48000C
    lea ENTRY_BOBS_00022(pc),a0                        ; +$00012: 41FA000E
    adda.l d0,a0                                       ; +$00016: D1C0
    move.l a0,8(a7)                                    ; +$00018: 2F480008
    movem.l (a7)+,d0/a0                                ; +$0001C: 4CDF0101
    rts                                                ; +$00020: 4E75
ENTRY_BOBS_00022:
    include "M19_P0_CORE_DISPATCH_MC68020.s"
L_BOBS_020A2:
bank_active_state:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$020A2: 000000000000000000000000
L_BOBS_020AE:
bank_canonical_empty:
    dc.b $41,$47,$42,$4F,$00,$01,$00,$00,$00,$00,$00,$28  ; +$020AE: 4147424F0001000000000028
    dc.b $00,$00,$00,$20,$00,$00,$00,$20,$00,$00,$00,$20  ; +$020BA: 000000200000002000000020
    dc.b $00,$00,$00,$01,$00,$00,$00,$00  ; +$020C6: 0000000100000000
ENTRY_BOBS_020CE:
get_entry:
    include "M19_P0_GET_PIPELINE_MC68020.s"
L_BOBS_03772:
    dc.b $FF,$FF,$80,$00,$C0,$00,$E0,$00,$F0,$00,$F8,$00  ; +$03772: FFFF8000C000E000F000F800
    dc.b $FC,$00,$FE,$00,$FF,$00,$FF,$80,$FF,$C0,$FF,$E0  ; +$0377E: FC00FE00FF00FF80FFC0FFE0
    dc.b $FF,$F0,$FF,$F8,$FF,$FC,$FF,$FE  ; +$0378A: FFF0FFF8FFFCFFFE
L_BOBS_03792:
    include "M19_P0_CHECKED_REGISTRY_MC68020.s"
L_BOBS_046CC:
registry_state:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$046CC: 0000000000000000
L_BOBS_046D4:
    include "M19_P0_SCREEN_PRECLOSE_MC68020.s"
L_BOBS_048FA:
program_end_bridge_entry:
    dc.b $48,$E7,$FF,$FE,$61,$00,$FD,$94,$4A,$80,$67,$00  ; +$048FA: 48E7FFFE6100FD944A806700
    dc.b $00,$9C,$20,$0D,$4A,$80,$67,$00,$00,$94,$02,$80  ; +$04906: 009C200D4A80670000940280
    dc.b $00,$00,$00,$01,$66,$00,$00,$8A,$20,$2D,$01,$C8  ; +$04912: 000000016600008A202D01C8
    dc.b $0C,$80,$00,$00,$01,$68,$65,$00,$00,$7C,$04,$80  ; +$0491E: 0C80000001686500007C0480
    dc.b $00,$00,$01,$68,$22,$00,$02,$81,$00,$00,$00,$01  ; +$0492A: 000001682200028100000001
    dc.b $66,$00,$00,$6A,$28,$40,$22,$4C,$2C,$78,$00,$04  ; +$04936: 6600006A2840224C2C780004
    dc.b $4E,$AE,$FD,$EA,$4A,$80,$67,$00,$00,$58,$20,$14  ; +$04942: 4EAEFDEA4A80670000582014
    dc.b $0C,$80,$48,$E7,$FF,$FE,$66,$00,$00,$4C,$20,$2C  ; +$0494E: 0C8048E7FFFE6600004C202C
    dc.b $00,$04,$0C,$80,$24,$6D,$01,$C8,$66,$00,$00,$3E  ; +$0495A: 00040C80246D01C86600003E
    dc.b $20,$2C,$00,$08,$0C,$80,$60,$00,$09,$78,$66,$00  ; +$04966: 202C00080C80600009786600
    dc.b $00,$30,$41,$FA,$FF,$84,$22,$08,$20,$2D,$01,$CC  ; +$04972: 003041FAFF842208202D01CC
    dc.b $B0,$81,$66,$00,$00,$20,$20,$2D,$01,$D0,$B0,$81  ; +$0497E: B08166000020202D01D0B081
    dc.b $66,$00,$00,$16,$61,$00,$FD,$44,$4A,$83,$67,$00  ; +$0498A: 660000166100FD444A836700
    dc.b $00,$0C,$2B,$4C,$01,$CC,$2B,$4C,$01,$D0,$4E,$94  ; +$04996: 000C2B4C01CC2B4C01D04E94
end_bridge_return:
    dc.b $4C,$DF,$7F,$FF,$4E,$75  ; +$049A2: 4CDF7FFF4E75
L_BOBS_049A8:
    include "M19_P0_BANK_IMAGE_RESOLVE_MC68020.s"
relay_put_entry:
    dc.b $48,$E7,$EF,$EE,$2E,$3C,$00,$00,$00,$00,$60,$00  ; +$05A5C: 48E7EFEE2E3C000000006000
    dc.b $00,$2C  ; +$05A68: 002C
L_BOBS_05A6A:
    include "M19_P0_RELAY_COMMANDS_MC68020.s"
L_BOBS_05B6E:
    include "M19_P0_PUBLIC_FRAME_MC68020.s"
    include "M19_P0I_ROUTED_PAINT_MC68020.s"
L_BOBS_05F30:
    include "M19_P0J_IMAGE_GATE_MC68020.s"
L_BOBS_06254:
    include "M19_P0J_IMAGE_RETURN_MC68020.s"
routed_paint_prechecked_entry:
    dc.b $48,$E7,$EF,$EE,$61,$00,$FC,$C6,$4A,$83,$67,$00  ; +$06264: 48E7EFEE6100FCC64A836700
    dc.b $00,$06,$61,$00,$FC,$64,$4C,$DF,$77,$F7,$74,$00  ; +$06270: 00066100FC644CDF77F77400
    dc.b $4E,$75  ; +$0627C: 4E75
L_BOBS_0627E:
    include "M19_P0J_EXPLICIT_BANK_MC68020.s"
L_BOBS_0685C:
    include "M19_P0J_SAFE_TAIL_MC68020.s"
L_BOBS_068FA:
p1b_frame_draw_entry:
    bra.w L_BOBS_07AC2                                 ; +$068FA: 600011C6
    dc.b $4E,$71,$4E,$71  ; +$068FE: 4E714E71
L_BOBS_06902:
    include "M19_P1B_FRAME_GUARD_MC68020.s"
L_BOBS_06D36:
frame_guard_state:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$06D36: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$06D42: 000000000000000000000000
L_BOBS_06D4E:
    include "M19_B7_GUARDED_DRAW_MC68020.s"
L_BOBS_06EAC:
    include "M19_B7_END_MC68020.s"
L_BOBS_06FA6:
    include "M19_B7_B8_DRAW_BRIDGE_MC68020.s"
L_BOBS_071E8:
b8_b7_close_return:
    bra.w L_BOBS_0A1D2                                 ; +$071E8: 60002FE8
    dc.b $4E,$75  ; +$071EC: 4E75
L_BOBS_071EE:
    include "M19_B8_END_REGISTER_MC68020.s"
L_BOBS_07364:
    include "M19_B8_NODRAW_PRESTAGE_MC68020.s"
L_BOBS_07698:
    include "M19_B8S1_BANK_RETURN_MC68020.s"
    include "M19_B8S1_BANK_FREE_MC68020.s"
L_BOBS_07962:
    include "M19_P1B_HOTSPOT_JOIN_MC68020.s"
p2b_paint_continue:
    dc.b $26,$6C,$00,$78,$4A,$83,$67,$00,$00,$0E,$29,$41  ; +$079F2: 266C00784A836700000E2941
    dc.b $00,$48,$29,$44,$00,$4C,$60,$00,$D5,$6C,$29,$7C  ; +$079FE: 00482944004C6000D56C297C
    dc.b $00,$00,$00,$01,$00,$74,$60,$00,$D5,$FA  ; +$07A0A: 0000000100746000D5FA
    include "M19_P1B_HOTSPOT_ORIGIN_MC68020.s"
L_BOBS_07AC2:
    include "M19_P1C_FRAME_DISPATCH_MC68020.s"
L_BOBS_07AE8:
    include "M19_P1C_CONTEXT_MC68020.s"
ENTRY_BOBS_07B84:
    include "M19_P1C_PRIORITY_MC68020.s"
L_BOBS_07BBA:
    include "M19_P1C_FRAME_PREFLIGHT_MC68020.s"
L_BOBS_07C18:
    include "M19_P1C_ORDER_COLLECT_MC68020.s"
L_BOBS_07C98:
    include "M19_P1C_FRAME_DRAW_MC68020.s"
ENTRY_BOBS_07D7E:
    include "M19_P1D_LIMIT_MC68020.s"
L_BOBS_07DFE:
    include "M19_P1D_SCOPED_PAINT_MC68020.s"
L_BOBS_07E1C:
p1d_drawing_id:
    dc.b $00,$00,$00,$00  ; +$07E1C: 00000000
L_BOBS_07E20:
    include "M19_P1D_CLIP_BRIDGE_MC68020.s"
L_BOBS_07E6A:
    include "M19_P1D_INTERSECT_MC68020.s"
ENTRY_BOBS_07F00:
    include "M19_P1E_DEL_BOB_MC68020.s"
ENTRY_BOBS_07F2E:
    include "M19_P1E_INS_BOB_MC68020.s"
L_BOBS_07F54:
    include "M19_P1E_EDIT_BOOTSTRAP_MC68020.s"
L_BOBS_08306:
    include "M19_P1E_EDIT_OBJECTS_MC68020.s"
L_BOBS_0840A:
    include "M19_P1E_EDIT_PREFLIGHT_MC68020.s"
L_BOBS_08498:
    include "M19_P1E_EDIT_PREFLIGHT_NEXT_MC68020.s"
L_BOBS_084C6:
    include "M19_P1E_EDIT_PUBLISH_MC68020.s"
L_BOBS_08516:
    include "M19_P1E_EDIT_STAMPS_MC68020.s"
L_BOBS_085A6:
    include "M19_P1E_EDIT_COMMIT_MC68020.s"
L_BOBS_085E8:
    include "M19_P1E_EDIT_CLEANUP_MC68020.s"
L_BOBS_08632:
    include "M19_P1E_VALIDATE_BANK_MC68020.s"
L_BOBS_0865E:
    include "M19_P1E_VALIDATE_STAGE_MC68020.s"
L_BOBS_0866C:
    include "M19_P1E_REPACK_ENTRY_MC68020.s"
L_BOBS_08722:
    include "M19_P1E_REPACK_INSERT_MC68020.s"
L_BOBS_087C2:
    include "M19_P1E_REPACK_SCAN_MC68020.s"
L_BOBS_08820:
    include "M19_P1E_REPACK_PREPARE_MC68020.s"
L_BOBS_088EE:
    include "M19_P1E_REPACK_COPY_MC68020.s"
L_BOBS_089B6:
    include "M19_P1E_REPACK_FINALIZE_MC68020.s"
    include "M19_P2A_PAIR_CHECK_MC68020.s"
    include "M19_P2A_CHIP_RESOLVE_MC68020.s"
    include "M19_P2A_HOTSPOT_MC68020.s"
    include "M19_P2A_GEOMETRY_MC68020.s"
    include "M19_P2A_COLLISION_KERNEL_MC68020.s"
    include "M19_P2A_COLLISION_QUERY_MC68020.s"
ENTRY_BOBS_09D38:
    include "M19_P2A_PUBLIC_COL_MC68020.s"
L_BOBS_09E36:
    include "M19_P2B_FLIP_PUBLIC_MC68020.s"
    include "M19_P2B_VARIANT_ANCHOR_MC68020.s"
L_BOBS_0A0AA:
    include "M19_P2B_PAINT_GEOMETRY_MC68020.s"
L_BOBS_0A1D2:
    include "M19_P2B_CLEANUP_MC68020.s"
    include "M19_P2B_PLANAR_MC68020.s"
L_BOBS_0A4C0:
    include "M19_P2B_SLOTS_DATA_MC68020.s"
ENTRY_BOBS_0B4C4:
    include "M19_P2C_PLANES_MC68020.s"
ENTRY_BOBS_0B58C:
    include "M19_P2D_CONTROLS_MC68020.s"
L_BOBS_0B72A:
    include "M19_P2D_SUPPORT_TAIL_MC68020.s"
L_BOBS_0C4FE:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0C4FE: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0C50A: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$0C516: 0000000000000000
L_BOBS_0C51E:
    include "M19_P2D_SERVICE_BODY_MC68020.s"
L_BOBS_0DA10:
p2d_service_root:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA10: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA1C: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA28: 0000000000000000
L_BOBS_0DA30:
    include "M19_P2D_SYSTEM_SERVICE_MC68020.s"
L_BOBS_0DCB4:
    dc.b $48,$E7,$CF,$EE,$4F,$EF,$FF,$A0,$28,$4F,$29,$7C  ; +$0DCB4: 48E7CFEE4FEFFFA0284F297C
    dc.b $00,$00,$00,$00,$00,$14,$28,$8D,$45,$FA,$FD,$46  ; +$0DCC0: 000000000014288D45FAFD46
    dc.b $4A,$92,$67,$00,$00,$AA,$20,$12,$22,$0D,$B0,$81  ; +$0DCCC: 4A92670000AA2012220DB081
    dc.b $66,$00,$00,$A8,$20,$14,$4A,$80,$67,$00,$FF,$32  ; +$0DCD8: 660000A820144A806700FF32
    dc.b $02,$80,$00,$00,$00,$01,$66,$00,$FF,$28,$22,$54  ; +$0DCE4: 0280000000016600FF282254
    dc.b $2C,$78,$00,$04,$4E,$AE,$FD,$EA,$4A,$80,$67,$00  ; +$0DCF0: 2C7800044EAEFDEA4A806700
    dc.b $FF,$18,$20,$14,$06,$80,$00,$00,$01,$CB,$65,$00  ; +$0DCFC: FF1820140680000001CB6500
    dc.b $FF,$0C,$22,$40,$2C,$78,$00,$04,$4E,$AE,$FD,$EA  ; +$0DD08: FF0C22402C7800044EAEFDEA
    dc.b $4A,$80,$67,$00,$FE,$FC,$20,$2D,$01,$C8,$29,$40  ; +$0DD14: 4A806700FEFC202D01C82940
    dc.b $00,$04,$20,$2C,$00,$04,$4A,$80,$67,$00,$FE,$EA  ; +$0DD20: 0004202C00044A806700FEEA
    dc.b $02,$80,$00,$00,$00,$01,$66,$00,$FE,$E0,$22,$6C  ; +$0DD2C: 0280000000016600FEE0226C
    dc.b $00,$04,$2C,$78,$00,$04,$4E,$AE,$FD,$EA,$4A,$80  ; +$0DD38: 00042C7800044EAEFDEA4A80
    dc.b $67,$00,$FE,$CE,$20,$2C,$00,$04,$06,$80,$00,$00  ; +$0DD44: 6700FECE202C000406800000
    dc.b $00,$23,$65,$00,$FE,$C0,$22,$40,$2C,$78,$00,$04  ; +$0DD50: 00236500FEC022402C780004
    dc.b $4E,$AE,$FD,$EA,$4A,$80,$67,$00,$FE,$B0,$20,$6C  ; +$0DD5C: 4EAEFDEA4A806700FEB0206C
    dc.b $00,$04,$4A,$90,$66,$00,$00,$14,$61,$00,$FB,$62  ; +$0DD68: 00044A90660000146100FB62
    dc.b $4A,$83,$67,$00,$00,$0A,$29,$7C,$00,$00,$00,$01  ; +$0DD74: 4A836700000A297C00000001
    dc.b $00,$14,$26,$2C,$00,$14,$24,$3C,$00,$00,$00,$00  ; +$0DD80: 0014262C0014243C00000000
    dc.b $4F,$EF,$00,$60,$4C,$DF,$77,$F3,$4E,$75  ; +$0DD8C: 4FEF00604CDF77F34E75
L_BOBS_0DD96:
    include "M19_P2D_SERVICE_GUARDS_MC68020.s"
    dc.b $48,$E7,$CF,$EE,$4F,$EF,$FF,$A0,$28,$4F,$28,$BC  ; +$0E538: 48E7CFEE4FEFFFA0284F28BC
    dc.b $00,$00,$00,$00,$41,$FA,$F4,$C6,$4A,$90,$66,$00  ; +$0E544: 0000000041FAF4C64A906600
    dc.b $00,$4E,$45,$FA,$00,$5C,$20,$12,$4A,$80,$67,$00  ; +$0E550: 004E45FA005C20124A806700
    dc.b $00,$0A,$22,$0D,$B0,$81,$66,$00,$00,$3A,$24,$BC  ; +$0E55C: 000A220DB0816600003A24BC
    dc.b $00,$00,$00,$00,$25,$7C,$00,$00,$00,$00,$00,$04  ; +$0E568: 00000000257C000000000004
    dc.b $25,$7C,$00,$00,$00,$00,$00,$08,$25,$7C,$00,$00  ; +$0E574: 257C000000000008257C0000
    dc.b $00,$00,$00,$0C,$25,$7C,$00,$00,$00,$00,$00,$10  ; +$0E580: 0000000C257C000000000010
    dc.b $25,$7C,$00,$00,$00,$00,$00,$14,$28,$BC,$00,$00  ; +$0E58C: 257C00000000001428BC0000
    dc.b $00,$01,$60,$00,$00,$02  ; +$0E598: 000160000002
L_BOBS_0E59E:
    include "M19_P2D_SERVICE_RETURN_MC68020.s"
L_BOBS_0E5B0:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5B0: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5BC: 000000000000000000000000
L_BOBS_0E5C8:
    include "M19_P2D_PUBLIC_UPDATE_MC68020.s"
ENTRY_BOBS_0EDD0:
    include "M19_P2D_PUBLIC_QUERY_HEAD_MC68020.s"
L_BOBS_0EDF4:
    lea 32(a7),a7                                      ; +$0EDF4: 4FEF0020
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0EDF8: 4CDF77F7
    moveq #0,d2                                        ; +$0EDFC: 7400
    rts                                                ; +$0EDFE: 4E75
