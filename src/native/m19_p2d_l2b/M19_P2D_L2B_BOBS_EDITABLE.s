; AGA_NATIVE_MIN_CPU: MC68020
; L2b linked view of frozen M19_P2D_BOBS_EDITABLE.s.
; Historical ranges and SHA comments below describe the P2d base.
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
    include "../m19_p2d/M19_P0_CORE_DISPATCH_MC68020.s"
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
    include "../m19_p2d/M19_P0_GET_PIPELINE_MC68020.s"
L_BOBS_03772:
    dc.b $FF,$FF,$80,$00,$C0,$00,$E0,$00,$F0,$00,$F8,$00  ; +$03772: FFFF8000C000E000F000F800
    dc.b $FC,$00,$FE,$00,$FF,$00,$FF,$80,$FF,$C0,$FF,$E0  ; +$0377E: FC00FE00FF00FF80FFC0FFE0
    dc.b $FF,$F0,$FF,$F8,$FF,$FC,$FF,$FE  ; +$0378A: FFF0FFF8FFFCFFFE
L_BOBS_03792:
    include "../m19_p2d/M19_P0_CHECKED_REGISTRY_MC68020.s"
L_BOBS_046CC:
registry_state:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$046CC: 0000000000000000
L_BOBS_046D4:
    include "../m19_p2d/M19_P0_SCREEN_PRECLOSE_MC68020.s"
L_BOBS_048FA:
program_end_bridge_entry:
    include "../m19_p2d/M19_P0C_PROGRAM_END_CALLBACK_MC68020.s"
L_BOBS_049A8:
    include "../m19_p2d/M19_P0_BANK_IMAGE_RESOLVE_MC68020.s"
relay_put_entry:
    include "../m19_p2d/M19_P0_RELAY_PUT_MC68020.s"
L_BOBS_05A6A:
    include "../m19_p2d/M19_P0_RELAY_COMMANDS_MC68020.s"
L_BOBS_05B6E:
    include "../m19_p2d/M19_P0_PUBLIC_FRAME_MC68020.s"
    include "../m19_p2d/M19_P0I_ROUTED_PAINT_MC68020.s"
L_BOBS_05F30:
    include "../m19_p2d/M19_P0J_IMAGE_GATE_MC68020.s"
L_BOBS_06254:
    include "../m19_p2d/M19_P0J_IMAGE_RETURN_MC68020.s"
routed_paint_prechecked_entry:
    include "../m19_p2d/M19_P0J_PRECHECKED_PAINT_MC68020.s"
L_BOBS_0627E:
    include "../m19_p2d/M19_P0J_EXPLICIT_BANK_MC68020.s"
L_BOBS_0685C:
    include "../m19_p2d/M19_P0J_SAFE_TAIL_MC68020.s"
L_BOBS_068FA:
    include "../m19_p2d/M19_P1B_FRAME_BRANCH_MC68020.s"
    nop                                                ; +$068FE: 4E71
    nop                                                ; +$06900: 4E71
L_BOBS_06902:
    include "../m19_p2d/M19_P1B_FRAME_GUARD_MC68020.s"
L_BOBS_06D36:
frame_guard_state:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$06D36: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$06D42: 000000000000000000000000
L_BOBS_06D4E:
    include "../m19_p2d/M19_B7_GUARDED_DRAW_MC68020.s"
L_BOBS_06EAC:
    include "../m19_p2d/M19_B7_END_MC68020.s"
L_BOBS_06FA6:
    include "../m19_p2d/M19_B7_B8_DRAW_BRIDGE_MC68020.s"
L_BOBS_071E8:
    include "../m19_p2d/M19_B8_CLOSE_BRANCH_MC68020.s"
    rts                                                ; +$071EC: 4E75
L_BOBS_071EE:
    include "../m19_p2d/M19_B8_END_REGISTER_MC68020.s"
L_BOBS_07364:
    include "../m19_p2d/M19_B8_NODRAW_PRESTAGE_MC68020.s"
L_BOBS_07698:
    include "../m19_p2d/M19_B8S1_BANK_RETURN_MC68020.s"
    include "../m19_p2d/M19_B8S1_BANK_FREE_MC68020.s"
L_BOBS_07962:
    include "../m19_p2d/M19_P1B_HOTSPOT_JOIN_MC68020.s"
p2b_paint_continue:
    include "../m19_p2d/M19_P1B_PAINT_CONTINUE_MC68020.s"
    include "../m19_p2d/M19_P1B_HOTSPOT_ORIGIN_MC68020.s"
L_BOBS_07AC2:
    include "../m19_p2d/M19_P1C_FRAME_DISPATCH_MC68020.s"
L_BOBS_07AE8:
    include "../m19_p2d/M19_P1C_CONTEXT_MC68020.s"
ENTRY_BOBS_07B84:
    include "../m19_p2d/M19_P1C_PRIORITY_MC68020.s"
L_BOBS_07BBA:
    include "../m19_p2d/M19_P1C_FRAME_PREFLIGHT_MC68020.s"
L_BOBS_07C18:
    include "../m19_p2d/M19_P1C_ORDER_COLLECT_MC68020.s"
L_BOBS_07C98:
    include "../m19_p2d/M19_P1C_FRAME_DRAW_MC68020.s"
ENTRY_BOBS_07D7E:
    include "../m19_p2d/M19_P1D_LIMIT_MC68020.s"
L_BOBS_07DFE:
    include "../m19_p2d/M19_P1D_SCOPED_PAINT_MC68020.s"
L_BOBS_07E1C:
p1d_drawing_id:
    dc.b $00,$00,$00,$00  ; +$07E1C: 00000000
L_BOBS_07E20:
    include "../m19_p2d/M19_P1D_CLIP_BRIDGE_MC68020.s"
L_BOBS_07E6A:
    include "../m19_p2d/M19_P1D_INTERSECT_MC68020.s"
ENTRY_BOBS_07F00:
    include "../m19_p2d/M19_P1E_DEL_BOB_MC68020.s"
ENTRY_BOBS_07F2E:
    include "../m19_p2d/M19_P1E_INS_BOB_MC68020.s"
L_BOBS_07F54:
    include "../m19_p2d/M19_P1E_EDIT_BOOTSTRAP_MC68020.s"
L_BOBS_08306:
    include "../m19_p2d/M19_P1E_EDIT_OBJECTS_MC68020.s"
L_BOBS_0840A:
    include "../m19_p2d/M19_P1E_EDIT_PREFLIGHT_MC68020.s"
L_BOBS_08498:
    include "../m19_p2d/M19_P1E_EDIT_PREFLIGHT_NEXT_MC68020.s"
L_BOBS_084C6:
    include "../m19_p2d/M19_P1E_EDIT_PUBLISH_MC68020.s"
L_BOBS_08516:
    include "../m19_p2d/M19_P1E_EDIT_STAMPS_MC68020.s"
L_BOBS_085A6:
    include "../m19_p2d/M19_P1E_EDIT_COMMIT_MC68020.s"
L_BOBS_085E8:
    include "../m19_p2d/M19_P1E_EDIT_CLEANUP_MC68020.s"
L_BOBS_08632:
    include "../m19_p2d/M19_P1E_VALIDATE_BANK_MC68020.s"
L_BOBS_0865E:
    include "../m19_p2d/M19_P1E_VALIDATE_STAGE_MC68020.s"
L_BOBS_0866C:
    include "../m19_p2d/M19_P1E_REPACK_ENTRY_MC68020.s"
L_BOBS_08722:
    include "../m19_p2d/M19_P1E_REPACK_INSERT_MC68020.s"
L_BOBS_087C2:
    include "../m19_p2d/M19_P1E_REPACK_SCAN_MC68020.s"
L_BOBS_08820:
    include "../m19_p2d/M19_P1E_REPACK_PREPARE_MC68020.s"
L_BOBS_088EE:
    include "../m19_p2d/M19_P1E_REPACK_COPY_MC68020.s"
L_BOBS_089B6:
    include "../m19_p2d/M19_P1E_REPACK_FINALIZE_MC68020.s"
    include "../m19_p2d/M19_P2A_PAIR_CHECK_MC68020.s"
    include "../m19_p2d/M19_P2A_CHIP_RESOLVE_MC68020.s"
    include "../m19_p2d/M19_P2A_HOTSPOT_MC68020.s"
    include "../m19_p2d/M19_P2A_GEOMETRY_MC68020.s"
    include "../m19_p2d/M19_P2A_COLLISION_KERNEL_MC68020.s"
    include "../m19_p2d/M19_P2A_COLLISION_QUERY_MC68020.s"
ENTRY_BOBS_09D38:
    include "../m19_p2d/M19_P2A_PUBLIC_COL_MC68020.s"
L_BOBS_09E36:
    include "../m19_p2d/M19_P2B_FLIP_PUBLIC_MC68020.s"
    include "../m19_p2d/M19_P2B_VARIANT_ANCHOR_MC68020.s"
L_BOBS_0A0AA:
    include "../m19_p2d/M19_P2B_PAINT_GEOMETRY_MC68020.s"
L_BOBS_0A1D2:
    include "../m19_p2d/M19_P2B_CLEANUP_MC68020.s"
    include "../m19_p2d/M19_P2B_PLANAR_MC68020.s"
L_BOBS_0A4C0:
    include "../m19_p2d/M19_P2B_SLOTS_DATA_MC68020.s"
ENTRY_BOBS_0B4C4:
    include "../m19_p2d/M19_P2C_PLANES_MC68020.s"
ENTRY_BOBS_0B58C:
    include "../m19_p2d/M19_P2D_CONTROLS_MC68020.s"
L_BOBS_0B72A:
    include "M19_L2B_BOBS_SUPPORT_BODY_MC68020.s"
L_BOBS_0C4FE:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0C4FE: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0C50A: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$0C516: 0000000000000000
L_BOBS_0C51E:
    include "../m19_p2d/M19_P2D_SERVICE_BODY_MC68020.s"
L_BOBS_0DA10:
p2d_service_root:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA10: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA1C: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00  ; +$0DA28: 0000000000000000
L_BOBS_0DA30:
    include "../m19_p2d/M19_P2D_SYSTEM_SERVICE_MC68020.s"
L_BOBS_0DCB4:
    include "../m19_p2d/M19_P2D_SERVICE_UPDATE_BRIDGE_MC68020.s"
L_BOBS_0DD96:
    include "../m19_p2d/M19_P2D_SERVICE_GUARDS_MC68020.s"
    include "../m19_p2d/M19_P2D_SERVICE_ROOT_RESET_MC68020.s"
L_BOBS_0E59E:
    include "../m19_p2d/M19_P2D_SERVICE_RETURN_MC68020.s"
L_BOBS_0E5B0:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5B0: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5BC: 000000000000000000000000
L_BOBS_0E5C8:
    include "../m19_p2d/M19_P2D_PUBLIC_UPDATE_MC68020.s"
ENTRY_BOBS_0EDD0:
    include "../m19_p2d/M19_P2D_PUBLIC_QUERY_HEAD_MC68020.s"
L_BOBS_0EDF4:
    include "../m19_p2d/M19_P2D_PUBLIC_QUERY_TAIL_MC68020.s"

    include "../m19_p2d_l2/M19_L2_FIRST_BIND_TAIL_MC68020.s"
