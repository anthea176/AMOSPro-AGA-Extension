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
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00022: 48E7EFEE
    lea -96(a7),a7                                     ; +$00026: 4FEFFFA0
    movea.l a7,a2                                      ; +$0002A: 244F
    move.l d3,(a2)                                     ; +$0002C: 2483
    move.l (a3)+,d7                                    ; +$0002E: 2E1B
    move.l d7,4(a2)                                    ; +$00030: 25470004
    move.l a3,8(a2)                                    ; +$00034: 254B0008
    move.l #$00000000,d3                               ; +$00038: 263C00000000
    movea.l $0004.w,a0                                 ; +$0003E: 20780004
    move.l a0,d0                                       ; +$00042: 2008
    tst.l d0                                           ; +$00044: 4A80
    beq.w L_BOBS_002BA                                 ; +$00046: 67000272
    move.w 296(a0),d0                                  ; +$0004A: 30280128
    btst #1,d0                                         ; +$0004E: 08000001
    beq.w L_BOBS_002BA                                 ; +$00052: 67000266
    move.l (a2),d0                                     ; +$00056: 2012
    tst.l d0                                           ; +$00058: 4A80
    ble.w L_BOBS_002BA                                 ; +$0005A: 6F00025E
    cmpi.l #$00000100,d0                               ; +$0005E: 0C8000000100
    bgt.w L_BOBS_002BA                                 ; +$00064: 6E000254
    move.l 4(a2),d0                                    ; +$00068: 202A0004
    cmpi.l #$00000005,d0                               ; +$0006C: 0C8000000005
    bcs.w L_BOBS_002BA                                 ; +$00072: 65000246
    cmpi.l #$0000FFFF,d0                               ; +$00076: 0C800000FFFF
    bhi.w L_BOBS_002BA                                 ; +$0007C: 6200023C
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$00080: FE11F700031D
    move.l a0,d5                                       ; +$00086: 2A08
    cmpi.l #$00000018,d5                               ; +$00088: 0C8500000018
    bls.w L_BOBS_002BA                                 ; +$0008E: 6300022A
    move.l d5,d0                                       ; +$00092: 2005
    andi.l #$00000001,d0                               ; +$00094: 028000000001
    bne.w L_BOBS_002BA                                 ; +$0009A: 6600021E
    move.l d5,12(a2)                                   ; +$0009E: 2545000C
    movea.l d5,a1                                      ; +$000A2: 2245
    movea.l $0004.w,a6                                 ; +$000A4: 2C780004
    jsr -534(a6)                                       ; +$000A8: 4EAEFDEA
    tst.l d0                                           ; +$000AC: 4A80
    beq.w L_BOBS_002BA                                 ; +$000AE: 6700020A
    move.l 12(a2),d0                                   ; +$000B2: 202A000C
    subi.l #$00000018,d0                               ; +$000B6: 048000000018
    movea.l d0,a1                                      ; +$000BC: 2240
    movea.l $0004.w,a6                                 ; +$000BE: 2C780004
    jsr -534(a6)                                       ; +$000C2: 4EAEFDEA
    tst.l d0                                           ; +$000C6: 4A80
    beq.w L_BOBS_002BA                                 ; +$000C8: 670001F0
    move.l (a2),d0                                     ; +$000CC: 2012
    move.l #$00000014,d1                               ; +$000CE: 223C00000014
    mulu.w d1,d0                                       ; +$000D4: C0C1
    addi.l #$00000010,d0                               ; +$000D6: 068000000010
    move.l d0,16(a2)                                   ; +$000DC: 25400010
    movea.l 12(a2),a0                                  ; +$000E0: 206A000C
    move.l -20(a0),d0                                  ; +$000E4: 2028FFEC
    move.l 16(a2),d1                                   ; +$000E8: 222A0010
    addi.l #$00000010,d1                               ; +$000EC: 068100000010
    cmp.l d1,d0                                        ; +$000F2: B081
    bne.w L_BOBS_002BA                                 ; +$000F4: 660001C4
    move.l -16(a0),d0                                  ; +$000F8: 2028FFF0
    move.l 4(a2),d1                                    ; +$000FC: 222A0004
    cmp.l d1,d0                                        ; +$00100: B081
    bne.w L_BOBS_002BA                                 ; +$00102: 660001B6
    move.l #$00000000,d0                               ; +$00106: 203C00000000
    move.w -12(a0),d0                                  ; +$0010C: 3028FFF4
    tst.l d0                                           ; +$00110: 4A80
    beq.w L_BOBS_00124                                 ; +$00112: 67000010
    andi.w #$FFFD,d0                                   ; +$00116: 0240FFFD
    cmpi.l #$00000001,d0                               ; +$0011A: 0C8000000001
    bne.w L_BOBS_002BA                                 ; +$00120: 66000198
L_BOBS_00124:
    move.l 12(a2),d0                                   ; +$00124: 202A000C
    move.l 16(a2),d1                                   ; +$00128: 222A0010
    add.l d1,d0                                        ; +$0012C: D081
    bcs.w L_BOBS_002BA                                 ; +$0012E: 6500018A
    subq.l #1,d0                                       ; +$00132: 5380
    movea.l d0,a1                                      ; +$00134: 2240
    movea.l $0004.w,a6                                 ; +$00136: 2C780004
    jsr -534(a6)                                       ; +$0013A: 4EAEFDEA
    tst.l d0                                           ; +$0013E: 4A80
    beq.w L_BOBS_002BA                                 ; +$00140: 67000178
    movea.l 12(a2),a0                                  ; +$00144: 206A000C
    move.l (a0),d0                                     ; +$00148: 2010
    cmpi.l #$424F4231,d0                               ; +$0014A: 0C80424F4231
    bne.w L_BOBS_002BA                                 ; +$00150: 66000168
    move.l #$00000000,d0                               ; +$00154: 203C00000000
    move.w 4(a0),d0                                    ; +$0015A: 30280004
    cmpi.l #$00000001,d0                               ; +$0015E: 0C8000000001
    bne.w L_BOBS_002BA                                 ; +$00164: 66000154
    move.l #$00000000,d0                               ; +$00168: 203C00000000
    move.w 6(a0),d0                                    ; +$0016E: 30280006
    cmpi.l #$00000014,d0                               ; +$00172: 0C8000000014
    bne.w L_BOBS_002BA                                 ; +$00178: 66000140
    move.l 8(a0),d0                                    ; +$0017C: 20280008
    move.l (a2),d1                                     ; +$00180: 2212
    cmp.l d1,d0                                        ; +$00182: B081
    bne.w L_BOBS_002BA                                 ; +$00184: 66000134
    tst.l 12(a0)                                       ; +$00188: 4AA8000C
    bne.w L_BOBS_002BA                                 ; +$0018C: 6600012C
    movea.l a0,a4                                      ; +$00190: 2848
    lea 16(a4),a4                                      ; +$00192: 49EC0010
    move.l a4,20(a2)                                   ; +$00196: 254C0014
    move.l (a2),d6                                     ; +$0019A: 2C12
L_BOBS_0019C:
    move.l #$00000000,d0                               ; +$0019C: 203C00000000
    move.w 16(a4),d0                                   ; +$001A2: 302C0010
    cmpi.l #$00000001,d0                               ; +$001A6: 0C8000000001
    beq.w L_BOBS_001D2                                 ; +$001AC: 67000024
    cmpi.l #$00000002,d0                               ; +$001B0: 0C8000000002
    bne.w L_BOBS_002BA                                 ; +$001B6: 66000102
    move.l 12(a4),d0                                   ; +$001BA: 202C000C
    tst.l d0                                           ; +$001BE: 4A80
    ble.w L_BOBS_002BA                                 ; +$001C0: 6F0000F8
    cmpi.l #$00001000,d0                               ; +$001C4: 0C8000001000
    bgt.w L_BOBS_002BA                                 ; +$001CA: 6E0000EE
    bra.w L_BOBS_001DA                                 ; +$001CE: 6000000A
L_BOBS_001D2:
    tst.l 12(a4)                                       ; +$001D2: 4AAC000C
    bne.w L_BOBS_002BA                                 ; +$001D6: 660000E2
L_BOBS_001DA:
    move.l #$00000000,d0                               ; +$001DA: 203C00000000
    move.w 18(a4),d0                                   ; +$001E0: 302C0012
    cmpi.l #$00000001,d0                               ; +$001E4: 0C8000000001
    bhi.w L_BOBS_002BA                                 ; +$001EA: 620000CE
    move.l 8(a4),d0                                    ; +$001EE: 202C0008
    cmpi.l #$00000005,d0                               ; +$001F2: 0C8000000005
    bcs.w L_BOBS_002BA                                 ; +$001F8: 650000C0
    cmpi.l #$0000FFFF,d0                               ; +$001FC: 0C800000FFFF
    bhi.w L_BOBS_002BA                                 ; +$00202: 620000B6
    move.l (a4),d0                                     ; +$00206: 2014
    cmpi.l #$FFFF8000,d0                               ; +$00208: 0C80FFFF8000
    blt.w L_BOBS_002BA                                 ; +$0020E: 6D0000AA
    cmpi.l #$00007FFF,d0                               ; +$00212: 0C8000007FFF
    bgt.w L_BOBS_002BA                                 ; +$00218: 6E0000A0
    move.l 4(a4),d0                                    ; +$0021C: 202C0004
    cmpi.l #$FFFF8000,d0                               ; +$00220: 0C80FFFF8000
    blt.w L_BOBS_002BA                                 ; +$00226: 6D000092
    cmpi.l #$00007FFF,d0                               ; +$0022A: 0C8000007FFF
    bgt.w L_BOBS_002BA                                 ; +$00230: 6E000088
    lea 20(a4),a4                                      ; +$00234: 49EC0014
    subq.l #1,d6                                       ; +$00238: 5386
    bne.w L_BOBS_0019C                                 ; +$0023A: 6600FF60
    movea.l 20(a2),a4                                  ; +$0023E: 286A0014
    move.l (a2),d6                                     ; +$00242: 2C12
L_BOBS_00244:
    move.l (a4),d0                                     ; +$00244: 2014
    move.l d0,24(a2)                                   ; +$00246: 25400018
    move.l 4(a4),d0                                    ; +$0024A: 202C0004
    move.l d0,28(a2)                                   ; +$0024E: 2540001C
    move.l #$00000000,d3                               ; +$00252: 263C00000000
    move.w 18(a4),d3                                   ; +$00258: 362C0012
    move.l #$00000000,d0                               ; +$0025C: 203C00000000
    move.w 16(a4),d0                                   ; +$00262: 302C0010
    cmpi.l #$00000001,d0                               ; +$00266: 0C8000000001
    bne.w L_BOBS_00284                                 ; +$0026C: 66000016
    move.l 8(a4),d0                                    ; +$00270: 202C0008
    move.l d0,32(a2)                                   ; +$00274: 25400020
    lea 24(a2),a3                                      ; +$00278: 47EA0018
    bsr.w L_BOBS_00C5E                                 ; +$0027C: 610009E0
    bra.w L_BOBS_0029C                                 ; +$00280: 6000001A
L_BOBS_00284:
    move.l 12(a4),d0                                   ; +$00284: 202C000C
    move.l d0,32(a2)                                   ; +$00288: 25400020
    move.l 8(a4),d0                                    ; +$0028C: 202C0008
    move.l d0,36(a2)                                   ; +$00290: 25400024
    lea 24(a2),a3                                      ; +$00294: 47EA0018
    bsr.w L_BOBS_00CF6                                 ; +$00298: 61000A5C
L_BOBS_0029C:
    cmpi.l #$00000001,d3                               ; +$0029C: 0C8300000001
    bne.w L_BOBS_002BA                                 ; +$002A2: 66000016
    lea 20(a4),a4                                      ; +$002A6: 49EC0014
    subq.l #1,d6                                       ; +$002AA: 5386
    bne.w L_BOBS_00244                                 ; +$002AC: 6600FF96
    move.l #$00000001,d3                               ; +$002B0: 263C00000001
    bra.w L_BOBS_002C0                                 ; +$002B6: 60000008
L_BOBS_002BA:
    move.l #$00000000,d3                               ; +$002BA: 263C00000000
L_BOBS_002C0:
    movea.l 8(a2),a3                                   ; +$002C0: 266A0008
    lea 96(a7),a7                                      ; +$002C4: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$002C8: 4CDF77F7
    moveq #0,d2                                        ; +$002CC: 7400
    rts                                                ; +$002CE: 4E75
L_BOBS_002D0:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$002D0: 48E7EFEE
    lea -192(a7),a7                                    ; +$002D4: 4FEFFF40
    movea.l a7,a2                                      ; +$002D8: 244F
    move.l d3,(a2)                                     ; +$002DA: 2483
    move.l (a3)+,d7                                    ; +$002DC: 2E1B
    move.l d7,4(a2)                                    ; +$002DE: 25470004
    move.l (a3)+,d6                                    ; +$002E2: 2C1B
    move.l d6,8(a2)                                    ; +$002E4: 25460008
    move.l (a3)+,d4                                    ; +$002E8: 281B
    move.l d4,12(a2)                                   ; +$002EA: 2544000C
    move.l (a3)+,d5                                    ; +$002EE: 2A1B
    move.l d5,16(a2)                                   ; +$002F0: 25450010
    move.l #$00000000,d3                               ; +$002F4: 263C00000000
    movea.l $0004.w,a0                                 ; +$002FA: 20780004
    move.l a0,d0                                       ; +$002FE: 2008
    tst.l d0                                           ; +$00300: 4A80
    beq.w L_BOBS_008BE                                 ; +$00302: 670005BA
    move.w 296(a0),d0                                  ; +$00306: 30280128
    btst #1,d0                                         ; +$0030A: 08000001
    beq.w L_BOBS_008BE                                 ; +$0030E: 670005AE
    move.l (a2),d0                                     ; +$00312: 2012
    cmpi.l #$00000001,d0                               ; +$00314: 0C8000000001
    bhi.w L_BOBS_008BE                                 ; +$0031A: 620005A2
    cmpi.l #$00000020,d4                               ; +$0031E: 0C8400000020
    bcs.w L_BOBS_008BE                                 ; +$00324: 65000598
    cmpi.l #$01000000,d4                               ; +$00328: 0C8401000000
    bhi.w L_BOBS_008BE                                 ; +$0032E: 6200058E
    cmpi.l #$00000018,d5                               ; +$00332: 0C8500000018
    bls.w L_BOBS_008BE                                 ; +$00338: 63000584
    move.l d5,d0                                       ; +$0033C: 2005
    andi.l #$00000001,d0                               ; +$0033E: 028000000001
    bne.w L_BOBS_008BE                                 ; +$00344: 66000578
    cmpi.l #$FFFF8000,d6                               ; +$00348: 0C86FFFF8000
    blt.w L_BOBS_008BE                                 ; +$0034E: 6D00056E
    cmpi.l #$00007FFF,d6                               ; +$00352: 0C8600007FFF
    bgt.w L_BOBS_008BE                                 ; +$00358: 6E000564
    cmpi.l #$FFFF8000,d7                               ; +$0035C: 0C87FFFF8000
    blt.w L_BOBS_008BE                                 ; +$00362: 6D00055A
    cmpi.l #$00007FFF,d7                               ; +$00366: 0C8700007FFF
    bgt.w L_BOBS_008BE                                 ; +$0036C: 6E000550
    move.l d5,d0                                       ; +$00370: 2005
    add.l d4,d0                                        ; +$00372: D084
    bcs.w L_BOBS_008BE                                 ; +$00374: 65000548
    subq.l #1,d0                                       ; +$00378: 5380
    movea.l d0,a1                                      ; +$0037A: 2240
    movea.l $0004.w,a6                                 ; +$0037C: 2C780004
    jsr -534(a6)                                       ; +$00380: 4EAEFDEA
    tst.l d0                                           ; +$00384: 4A80
    beq.w L_BOBS_008BE                                 ; +$00386: 67000536
    move.l d5,d0                                       ; +$0038A: 2005
    subi.l #$00000018,d0                               ; +$0038C: 048000000018
    movea.l d0,a1                                      ; +$00392: 2240
    jsr -534(a6)                                       ; +$00394: 4EAEFDEA
    tst.l d0                                           ; +$00398: 4A80
    beq.w L_BOBS_008BE                                 ; +$0039A: 67000522
    movea.l d5,a0                                      ; +$0039E: 2045
    move.l -20(a0),d0                                  ; +$003A0: 2028FFEC
    move.l d4,d1                                       ; +$003A4: 2204
    addi.l #$00000010,d1                               ; +$003A6: 068100000010
    cmp.l d1,d0                                        ; +$003AC: B081
    bne.w L_BOBS_008BE                                 ; +$003AE: 6600050E
    move.l -16(a0),d0                                  ; +$003B2: 2028FFF0
    cmpi.l #$00000005,d0                               ; +$003B6: 0C8000000005
    bcs.w L_BOBS_008BE                                 ; +$003BC: 65000500
    cmpi.l #$0000FFFF,d0                               ; +$003C0: 0C800000FFFF
    bhi.w L_BOBS_008BE                                 ; +$003C6: 620004F6
    move.l #$00000000,d0                               ; +$003CA: 203C00000000
    move.w -12(a0),d0                                  ; +$003D0: 3028FFF4
    tst.l d0                                           ; +$003D4: 4A80
    beq.w L_BOBS_003E8                                 ; +$003D6: 67000010
    andi.w #$FFFD,d0                                   ; +$003DA: 0240FFFD
    cmpi.l #$00000001,d0                               ; +$003DE: 0C8000000001
    bne.w L_BOBS_008BE                                 ; +$003E4: 660004D8
L_BOBS_003E8:
    move.l -8(a0),d0                                   ; +$003E8: 2028FFF8
    cmpi.l #$41474150,d0                               ; +$003EC: 0C8041474150
    bne.w L_BOBS_008BE                                 ; +$003F2: 660004CA
    move.l -4(a0),d0                                   ; +$003F6: 2028FFFC
    cmpi.l #$49432020,d0                               ; +$003FA: 0C8049432020
    bne.w L_BOBS_008BE                                 ; +$00400: 660004BC
    move.l (a0),d0                                     ; +$00404: 2010
    cmpi.l #$41474150,d0                               ; +$00406: 0C8041474150
    bne.w L_BOBS_008BE                                 ; +$0040C: 660004B0
    move.l #$00000000,d0                               ; +$00410: 203C00000000
    move.w 4(a0),d0                                    ; +$00416: 30280004
    cmpi.l #$00004943,d0                               ; +$0041A: 0C8000004943
    bne.w L_BOBS_008BE                                 ; +$00420: 6600049C
    move.l #$00000000,d0                               ; +$00424: 203C00000000
    move.w 6(a0),d0                                    ; +$0042A: 30280006
    cmpi.l #$00000001,d0                               ; +$0042E: 0C8000000001
    beq.w L_BOBS_0044E                                 ; +$00434: 67000018
    cmpi.l #$00000002,d0                               ; +$00438: 0C8000000002
    bne.w L_BOBS_008BE                                 ; +$0043E: 6600047E
    move.l #$00000002,144(a2)                          ; +$00442: 257C000000020090
    bra.w L_BOBS_00456                                 ; +$0044A: 6000000A
L_BOBS_0044E:
    move.l #$00000001,144(a2)                          ; +$0044E: 257C000000010090
L_BOBS_00456:
    move.l #$00000000,d0                               ; +$00456: 203C00000000
    move.w 8(a0),d0                                    ; +$0045C: 30280008
    move.l d0,32(a2)                                   ; +$00460: 25400020
    move.l 144(a2),d1                                  ; +$00464: 222A0090
    cmpi.l #$00000002,d1                               ; +$00468: 0C8100000002
    bne.w L_BOBS_0048A                                 ; +$0046E: 6600001A
    cmpi.l #$00000002,d0                               ; +$00472: 0C8000000002
    bcs.w L_BOBS_008BE                                 ; +$00478: 65000444
    cmpi.l #$00000003,d0                               ; +$0047C: 0C8000000003
    bhi.w L_BOBS_008BE                                 ; +$00482: 6200043A
    bra.w L_BOBS_00494                                 ; +$00486: 6000000C
L_BOBS_0048A:
    cmpi.l #$00000001,d0                               ; +$0048A: 0C8000000001
    bhi.w L_BOBS_008BE                                 ; +$00490: 6200042C
L_BOBS_00494:
    move.l (a2),d1                                     ; +$00494: 2212
    tst.l d1                                           ; +$00496: 4A81
    beq.w L_BOBS_004A8                                 ; +$00498: 6700000E
    andi.l #$00000001,d0                               ; +$0049C: 028000000001
    tst.l d0                                           ; +$004A2: 4A80
    beq.w L_BOBS_008BE                                 ; +$004A4: 67000418
L_BOBS_004A8:
    move.l #$00000000,d0                               ; +$004A8: 203C00000000
    move.w 10(a0),d0                                   ; +$004AE: 3028000A
    cmpi.l #$00000001,d0                               ; +$004B2: 0C8000000001
    bne.w L_BOBS_008BE                                 ; +$004B8: 66000404
    move.l #$00000000,d0                               ; +$004BC: 203C00000000
    move.w 12(a0),d0                                   ; +$004C2: 3028000C
    move.l d0,20(a2)                                   ; +$004C6: 25400014
    tst.l d0                                           ; +$004CA: 4A80
    beq.w L_BOBS_008BE                                 ; +$004CC: 670003F0
    cmpi.l #$00001000,d0                               ; +$004D0: 0C8000001000
    bhi.w L_BOBS_008BE                                 ; +$004D6: 620003E6
    move.l #$00000000,d0                               ; +$004DA: 203C00000000
    move.w 14(a0),d0                                   ; +$004E0: 3028000E
    move.l d0,24(a2)                                   ; +$004E4: 25400018
    tst.l d0                                           ; +$004E8: 4A80
    beq.w L_BOBS_008BE                                 ; +$004EA: 670003D2
    cmpi.l #$00001000,d0                               ; +$004EE: 0C8000001000
    bhi.w L_BOBS_008BE                                 ; +$004F4: 620003C8
    move.l 20(a2),d1                                   ; +$004F8: 222A0014
    mulu.w d1,d0                                       ; +$004FC: C0C1
    cmpi.l #$00400000,d0                               ; +$004FE: 0C8000400000
    bhi.w L_BOBS_008BE                                 ; +$00504: 620003B8
    move.l #$00000000,d0                               ; +$00508: 203C00000000
    move.w 16(a0),d0                                   ; +$0050E: 30280010
    move.l d0,28(a2)                                   ; +$00512: 2540001C
    tst.l d0                                           ; +$00516: 4A80
    beq.w L_BOBS_008BE                                 ; +$00518: 670003A4
    cmpi.l #$00000008,d0                               ; +$0051C: 0C8000000008
    bhi.w L_BOBS_008BE                                 ; +$00522: 6200039A
    move.l d0,d1                                       ; +$00526: 2200
    move.l 32(a2),d0                                   ; +$00528: 202A0020
    andi.l #$00000001,d0                               ; +$0052C: 028000000001
    add.l d1,d0                                        ; +$00532: D081
    lsl.l #1,d0                                        ; +$00534: E388
    move.l d0,36(a2)                                   ; +$00536: 25400024
    move.l #$00000000,d1                               ; +$0053A: 223C00000000
    move.w 18(a0),d1                                   ; +$00540: 32280012
    cmp.l d1,d0                                        ; +$00544: B081
    bne.w L_BOBS_008BE                                 ; +$00546: 66000376
    move.l 28(a0),d0                                   ; +$0054A: 2028001C
    cmp.l d4,d0                                        ; +$0054E: B084
    bne.w L_BOBS_008BE                                 ; +$00550: 6600036C
    move.l 144(a2),d0                                  ; +$00554: 202A0090
    cmpi.l #$00000002,d0                               ; +$00558: 0C8000000002
    bne.w L_BOBS_00662                                 ; +$0055E: 66000102
    cmpi.l #$00000040,d4                               ; +$00562: 0C8400000040
    bcs.w L_BOBS_008BE                                 ; +$00568: 65000354
    move.l 32(a0),d0                                   ; +$0056C: 20280020
    tst.l d0                                           ; +$00570: 4A80
    beq.w L_BOBS_008BE                                 ; +$00572: 6700034A
    cmpi.l #$FFFFFFFF,d0                               ; +$00576: 0C80FFFFFFFF
    beq.w L_BOBS_008BE                                 ; +$0057C: 67000340
    move.l #$00000001,d1                               ; +$00580: 223C00000001
    move.l 28(a2),d2                                   ; +$00586: 242A001C
L_BOBS_0058A:
    lsl.l #1,d1                                        ; +$0058A: E389
    subq.l #1,d2                                       ; +$0058C: 5382
    bne.w L_BOBS_0058A                                 ; +$0058E: 6600FFFA
    move.l #$00000000,d0                               ; +$00592: 203C00000000
    move.w 36(a0),d0                                   ; +$00598: 30280024
    cmp.l d1,d0                                        ; +$0059C: B081
    bne.w L_BOBS_008BE                                 ; +$0059E: 6600031E
    move.l #$00000000,d0                               ; +$005A2: 203C00000000
    move.w 38(a0),d0                                   ; +$005A8: 30280026
    cmpi.l #$00000001,d0                               ; +$005AC: 0C8000000001
    bne.w L_BOBS_008BE                                 ; +$005B2: 6600030A
    move.l 40(a0),d0                                   ; +$005B6: 20280028
    cmpi.l #$00000040,d0                               ; +$005BA: 0C8000000040
    bne.w L_BOBS_008BE                                 ; +$005C0: 660002FC
    move.l d1,d2                                       ; +$005C4: 2401
    add.l d1,d2                                        ; +$005C6: D481
    add.l d1,d2                                        ; +$005C8: D481
    move.l 44(a0),d0                                   ; +$005CA: 2028002C
    cmp.l d2,d0                                        ; +$005CE: B082
    bne.w L_BOBS_008BE                                 ; +$005D0: 660002EC
    move.l 48(a0),d0                                   ; +$005D4: 20280030
    cmpi.l #$00000040,d0                               ; +$005D8: 0C8000000040
    bne.w L_BOBS_008BE                                 ; +$005DE: 660002DE
    tst.l 52(a0)                                       ; +$005E2: 4AA80034
    bne.w L_BOBS_008BE                                 ; +$005E6: 660002D6
    tst.l 56(a0)                                       ; +$005EA: 4AA80038
    bne.w L_BOBS_008BE                                 ; +$005EE: 660002CE
    tst.l 60(a0)                                       ; +$005F2: 4AA8003C
    bne.w L_BOBS_008BE                                 ; +$005F6: 660002C6
    move.l d2,d0                                       ; +$005FA: 2002
    addi.l #$00000043,d0                               ; +$005FC: 068000000043
    andi.l #$FFFFFFFC,d0                               ; +$00602: 0280FFFFFFFC
    cmp.l 20(a0),d0                                    ; +$00608: B0A80014
    bne.w L_BOBS_008BE                                 ; +$0060C: 660002B0
    cmp.l d4,d0                                        ; +$00610: B084
    bhi.w L_BOBS_008BE                                 ; +$00612: 620002AA
    move.l d0,188(a2)                                  ; +$00616: 254000BC
    move.l d2,d1                                       ; +$0061A: 2202
    addi.l #$00000040,d1                               ; +$0061C: 068100000040
    move.l d0,d3                                       ; +$00622: 2600
    sub.l d1,d3                                        ; +$00624: 9681
    tst.l d3                                           ; +$00626: 4A83
    beq.w L_BOBS_0063E                                 ; +$00628: 67000014
    move.l a0,d0                                       ; +$0062C: 2008
    add.l d1,d0                                        ; +$0062E: D081
    movea.l d0,a1                                      ; +$00630: 2240
L_BOBS_00632:
    tst.b (a1)+                                        ; +$00632: 4A19
    bne.w L_BOBS_008BE                                 ; +$00634: 66000288
    subq.l #1,d3                                       ; +$00638: 5383
    bne.w L_BOBS_00632                                 ; +$0063A: 6600FFF6
L_BOBS_0063E:
    move.l 188(a2),d0                                  ; +$0063E: 202A00BC
    move.l 24(a2),d1                                   ; +$00642: 222A0018
    addq.l #1,d1                                       ; +$00646: 5281
    lsl.l #2,d1                                        ; +$00648: E589
    add.l d1,d0                                        ; +$0064A: D081
    move.l d0,48(a2)                                   ; +$0064C: 25400030
    cmp.l 24(a0),d0                                    ; +$00650: B0A80018
    bne.w L_BOBS_008BE                                 ; +$00654: 66000268
    cmp.l d4,d0                                        ; +$00658: B084
    bhi.w L_BOBS_008BE                                 ; +$0065A: 62000262
    bra.w L_BOBS_00696                                 ; +$0065E: 60000036
L_BOBS_00662:
    move.l 20(a0),d0                                   ; +$00662: 20280014
    cmpi.l #$00000020,d0                               ; +$00666: 0C8000000020
    bne.w L_BOBS_008BE                                 ; +$0066C: 66000250
    move.l d0,188(a2)                                  ; +$00670: 254000BC
    move.l 24(a2),d0                                   ; +$00674: 202A0018
    addq.l #1,d0                                       ; +$00678: 5280
    lsl.l #2,d0                                        ; +$0067A: E588
    addi.l #$00000020,d0                               ; +$0067C: 068000000020
    move.l d0,48(a2)                                   ; +$00682: 25400030
    move.l 24(a0),d1                                   ; +$00686: 22280018
    cmp.l d1,d0                                        ; +$0068A: B081
    bne.w L_BOBS_008BE                                 ; +$0068C: 66000230
    cmp.l d4,d0                                        ; +$00690: B084
    bhi.w L_BOBS_008BE                                 ; +$00692: 6200022A
L_BOBS_00696:
    move.l 20(a2),d0                                   ; +$00696: 202A0014
    addi.l #$0000000F,d0                               ; +$0069A: 06800000000F
    lsr.l #4,d0                                        ; +$006A0: E888
    move.l d0,40(a2)                                   ; +$006A2: 25400028
    move.l 20(a2),d1                                   ; +$006A6: 222A0014
    andi.l #$0000000F,d1                               ; +$006AA: 02810000000F
    move.l #$00000000,d0                               ; +$006B0: 203C00000000
    tst.l d1                                           ; +$006B6: 4A81
    beq.w L_BOBS_006CA                                 ; +$006B8: 67000010
    move.l #$0000FFFF,d0                               ; +$006BC: 203C0000FFFF
L_BOBS_006C2:
    lsr.w #1,d0                                        ; +$006C2: E248
    subq.l #1,d1                                       ; +$006C4: 5381
    bne.w L_BOBS_006C2                                 ; +$006C6: 6600FFFA
L_BOBS_006CA:
    move.l d0,44(a2)                                   ; +$006CA: 2540002C
    movea.l 456(a5),a4                                 ; +$006CE: 286D01C8
    move.l a4,d0                                       ; +$006D2: 200C
    tst.l d0                                           ; +$006D4: 4A80
    beq.w L_BOBS_008BE                                 ; +$006D6: 670001E6
    move.l (a4),d0                                     ; +$006DA: 2014
    tst.l d0                                           ; +$006DC: 4A80
    beq.w L_BOBS_008BE                                 ; +$006DE: 670001DE
    move.l 8(a4),d0                                    ; +$006E2: 202C0008
    tst.l d0                                           ; +$006E6: 4A80
    beq.w L_BOBS_008BE                                 ; +$006E8: 670001D4
    move.l 32(a4),d0                                   ; +$006EC: 202C0020
    tst.l d0                                           ; +$006F0: 4A80
    beq.w L_BOBS_008BE                                 ; +$006F2: 670001CA
    move.l 12(a4),d0                                   ; +$006F6: 202C000C
    tst.l d0                                           ; +$006FA: 4A80
    ble.w L_BOBS_008BE                                 ; +$006FC: 6F0001C0
    cmpi.l #$00007FFF,d0                               ; +$00700: 0C8000007FFF
    bgt.w L_BOBS_008BE                                 ; +$00706: 6E0001B6
    move.l d0,52(a2)                                   ; +$0070A: 25400034
    move.l 16(a4),d0                                   ; +$0070E: 202C0010
    tst.l d0                                           ; +$00712: 4A80
    ble.w L_BOBS_008BE                                 ; +$00714: 6F0001A8
    cmpi.l #$00007FFF,d0                               ; +$00718: 0C8000007FFF
    bgt.w L_BOBS_008BE                                 ; +$0071E: 6E00019E
    move.l d0,56(a2)                                   ; +$00722: 25400038
    move.l 28(a4),d0                                   ; +$00726: 202C001C
    cmp.l 28(a2),d0                                    ; +$0072A: B0AA001C
    bne.w L_BOBS_008BE                                 ; +$0072E: 6600018E
    move.l 144(a2),d0                                  ; +$00732: 202A0090
    cmpi.l #$00000002,d0                               ; +$00736: 0C8000000002
    bne.w L_BOBS_0076A                                 ; +$0073C: 6600002C
    move.l (a4),d0                                     ; +$00740: 2014
    addi.l #$0000002C,d0                               ; +$00742: 06800000002C
    movea.l d0,a0                                      ; +$00748: 2040
    movea.l 8(a4),a6                                   ; +$0074A: 2C6C0008
    jsr -792(a6)                                       ; +$0074E: 4EAEFCE8
    cmpi.l #$FFFFFFFF,d0                               ; +$00752: 0C80FFFFFFFF
    beq.w L_BOBS_008BE                                 ; +$00758: 67000164
    move.l 16(a2),d1                                   ; +$0075C: 222A0010
    movea.l d1,a0                                      ; +$00760: 2041
    cmp.l 32(a0),d0                                    ; +$00762: B0A80020
    bne.w L_BOBS_008BE                                 ; +$00766: 66000156
L_BOBS_0076A:
    movea.l 32(a4),a0                                  ; +$0076A: 206C0020
    move.l 8(a0),d0                                    ; +$0076E: 20280008
    tst.l d0                                           ; +$00772: 4A80
    beq.w L_BOBS_0078C                                 ; +$00774: 67000016
    cmpi.l #$00000001,d0                               ; +$00778: 0C8000000001
    bne.w L_BOBS_008BE                                 ; +$0077E: 6600013E
    movea.l 32(a4),a0                                  ; +$00782: 206C0020
    movea.l (a0),a1                                    ; +$00786: 2250
    bra.w L_BOBS_00794                                 ; +$00788: 6000000A
L_BOBS_0078C:
    movea.l 32(a4),a0                                  ; +$0078C: 206C0020
    movea.l 4(a0),a1                                   ; +$00790: 22680004
L_BOBS_00794:
    move.l a1,d0                                       ; +$00794: 2009
    tst.l d0                                           ; +$00796: 4A80
    beq.w L_BOBS_008BE                                 ; +$00798: 67000124
    movea.l (a1),a0                                    ; +$0079C: 2051
    move.l a0,d0                                       ; +$0079E: 2008
    tst.l d0                                           ; +$007A0: 4A80
    beq.w L_BOBS_008BE                                 ; +$007A2: 6700011A
    move.l a0,64(a2)                                   ; +$007A6: 25480040
    move.l #$00000000,d1                               ; +$007AA: 223C00000000
    move.w (a0),d1                                     ; +$007B0: 3210
    tst.l d1                                           ; +$007B2: 4A81
    beq.w L_BOBS_008BE                                 ; +$007B4: 67000108
    move.l d1,60(a2)                                   ; +$007B8: 2541003C
    lsl.l #3,d1                                        ; +$007BC: E789
    cmp.l 52(a2),d1                                    ; +$007BE: B2AA0034
    blt.w L_BOBS_008BE                                 ; +$007C2: 6D0000FA
    move.l #$00000000,d1                               ; +$007C6: 223C00000000
    move.w 2(a0),d1                                    ; +$007CC: 32280002
    cmp.l 56(a2),d1                                    ; +$007D0: B2AA0038
    blt.w L_BOBS_008BE                                 ; +$007D4: 6D0000E8
    move.l #$00000000,d1                               ; +$007D8: 223C00000000
    move.b 5(a0),d1                                    ; +$007DE: 12280005
    cmp.l 28(a2),d1                                    ; +$007E2: B2AA001C
    bne.w L_BOBS_008BE                                 ; +$007E6: 660000D6
    move.l d1,d0                                       ; +$007EA: 2001
    movea.l a0,a1                                      ; +$007EC: 2248
    addq.l #8,a1                                       ; +$007EE: 5089
L_BOBS_007F0:
    move.l (a1)+,d1                                    ; +$007F0: 2219
    tst.l d1                                           ; +$007F2: 4A81
    beq.w L_BOBS_008BE                                 ; +$007F4: 670000C8
    cmpi.l #$FFFFFFFF,d1                               ; +$007F8: 0C81FFFFFFFF
    beq.w L_BOBS_008BE                                 ; +$007FE: 670000BE
    subq.l #1,d0                                       ; +$00802: 5380
    bne.w L_BOBS_007F0                                 ; +$00804: 6600FFEA
    move.l #$00000000,72(a2)                           ; +$00808: 257C000000000048
    bsr.w L_BOBS_008CC                                 ; +$00810: 610000BA
    tst.l d0                                           ; +$00814: 4A80
    beq.w L_BOBS_008BE                                 ; +$00816: 670000A6
    move.l 8(a2),d0                                    ; +$0081A: 202A0008
    cmp.l 52(a2),d0                                    ; +$0081E: B0AA0034
    bge.w L_BOBS_008B4                                 ; +$00822: 6C000090
    add.l 20(a2),d0                                    ; +$00826: D0AA0014
    tst.l d0                                           ; +$0082A: 4A80
    ble.w L_BOBS_008B4                                 ; +$0082C: 6F000086
    move.l 4(a2),d0                                    ; +$00830: 202A0004
    cmp.l 56(a2),d0                                    ; +$00834: B0AA0038
    bge.w L_BOBS_008B4                                 ; +$00838: 6C00007A
    add.l 24(a2),d0                                    ; +$0083C: D0AA0018
    tst.l d0                                           ; +$00840: 4A80
    ble.w L_BOBS_008B4                                 ; +$00842: 6F000070
    movea.l 32(a4),a0                                  ; +$00846: 206C0020
    move.l 20(a0),d0                                   ; +$0084A: 20280014
    andi.l #$00000001,d0                               ; +$0084E: 028000000001
    beq.w L_BOBS_00884                                 ; +$00854: 6700002E
    movea.l 12(a0),a0                                  ; +$00858: 2068000C
    move.l a0,d0                                       ; +$0085C: 2008
    tst.l d0                                           ; +$0085E: 4A80
    beq.w L_BOBS_008BE                                 ; +$00860: 6700005C
    movea.l $0004.w,a6                                 ; +$00864: 2C780004
    jsr -372(a6)                                       ; +$00868: 4EAEFE8C
    tst.l d0                                           ; +$0086C: 4A80
    beq.w L_BOBS_008BE                                 ; +$0086E: 6700004E
    movea.l 32(a4),a0                                  ; +$00872: 206C0020
    move.l 20(a0),d0                                   ; +$00876: 20280014
    andi.l #$FFFFFFFE,d0                               ; +$0087A: 0280FFFFFFFE
    move.l d0,20(a0)                                   ; +$00880: 21400014
L_BOBS_00884:
    move.l #$00000000,d0                               ; +$00884: 203C00000000
    move.l d0,128(a2)                                  ; +$0088A: 25400080
    move.l d0,132(a2)                                  ; +$0088E: 25400084
    move.l 20(a2),d0                                   ; +$00892: 202A0014
    move.l d0,136(a2)                                  ; +$00896: 25400088
    move.l 24(a2),d0                                   ; +$0089A: 202A0018
    move.l d0,140(a2)                                  ; +$0089E: 2540008C
    move.l #$00000001,72(a2)                           ; +$008A2: 257C000000010048
    bsr.w L_BOBS_008CC                                 ; +$008AA: 61000020
    tst.l d0                                           ; +$008AE: 4A80
    beq.w L_BOBS_008BE                                 ; +$008B0: 6700000C
L_BOBS_008B4:
    move.l #$00000001,d3                               ; +$008B4: 263C00000001
    bra.w L_BOBS_008C0                                 ; +$008BA: 60000004
L_BOBS_008BE:
    moveq #0,d3                                        ; +$008BE: 7600
L_BOBS_008C0:
    lea 192(a7),a7                                     ; +$008C0: 4FEF00C0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$008C4: 4CDF77F7
    moveq #0,d2                                        ; +$008C8: 7400
    rts                                                ; +$008CA: 4E75
L_BOBS_008CC:
    move.l #$00000000,68(a2)                           ; +$008CC: 257C000000000044
L_BOBS_008D4:
    move.l 68(a2),d0                                   ; +$008D4: 202A0044
    cmp.l 24(a2),d0                                    ; +$008D8: B0AA0018
    bge.w L_BOBS_00A8A                                 ; +$008DC: 6C0001AC
    lsl.l #2,d0                                        ; +$008E0: E588
    move.l d0,d1                                       ; +$008E2: 2200
    move.l 16(a2),d0                                   ; +$008E4: 202A0010
    add.l 188(a2),d0                                   ; +$008E8: D0AA00BC
    add.l d1,d0                                        ; +$008EC: D081
    movea.l d0,a1                                      ; +$008EE: 2240
    move.l (a1)+,d0                                    ; +$008F0: 2019
    move.l (a1)+,d1                                    ; +$008F2: 2219
    cmp.l d1,d0                                        ; +$008F4: B081
    bcc.w L_BOBS_00A92                                 ; +$008F6: 6400019A
    cmp.l 48(a2),d0                                    ; +$008FA: B0AA0030
    bcs.w L_BOBS_00A92                                 ; +$008FE: 65000192
    cmp.l 12(a2),d1                                    ; +$00902: B2AA000C
    bhi.w L_BOBS_00A92                                 ; +$00906: 6200018A
    move.l 68(a2),d2                                   ; +$0090A: 242A0044
    tst.l d2                                           ; +$0090E: 4A82
    bne.w L_BOBS_0091C                                 ; +$00910: 6600000A
    cmp.l 48(a2),d0                                    ; +$00914: B0AA0030
    bne.w L_BOBS_00A92                                 ; +$00918: 66000178
L_BOBS_0091C:
    move.l 24(a2),d2                                   ; +$0091C: 242A0018
    subq.l #1,d2                                       ; +$00920: 5382
    cmp.l 68(a2),d2                                    ; +$00922: B4AA0044
    bne.w L_BOBS_00932                                 ; +$00926: 6600000A
    cmp.l 12(a2),d1                                    ; +$0092A: B2AA000C
    bne.w L_BOBS_00A92                                 ; +$0092E: 66000162
L_BOBS_00932:
    move.l 16(a2),d2                                   ; +$00932: 242A0010
    add.l d2,d0                                        ; +$00936: D082
    move.l d0,76(a2)                                   ; +$00938: 2540004C
    add.l d2,d1                                        ; +$0093C: D282
    move.l d1,80(a2)                                   ; +$0093E: 25410050
    move.l #$00000000,84(a2)                           ; +$00942: 257C000000000054
    move.l #$00000000,88(a2)                           ; +$0094A: 257C000000000058
    move.l #$00000000,92(a2)                           ; +$00952: 257C00000000005C
L_BOBS_0095A:
    move.l 84(a2),d0                                   ; +$0095A: 202A0054
    cmp.l 40(a2),d0                                    ; +$0095E: B0AA0028
    bge.w L_BOBS_00A70                                 ; +$00962: 6C00010C
    move.l 88(a2),d0                                   ; +$00966: 202A0058
    tst.l d0                                           ; +$0096A: 4A80
    bne.w L_BOBS_009E0                                 ; +$0096C: 66000072
    move.l 76(a2),d0                                   ; +$00970: 202A004C
    cmp.l 80(a2),d0                                    ; +$00974: B0AA0050
    bcc.w L_BOBS_00A92                                 ; +$00978: 64000118
    movea.l d0,a0                                      ; +$0097C: 2040
    move.l #$00000000,d0                               ; +$0097E: 203C00000000
    move.b (a0)+,d0                                    ; +$00984: 1018
    move.l d0,d1                                       ; +$00986: 2200
    andi.l #$0000007F,d1                               ; +$00988: 02810000007F
    addq.l #1,d1                                       ; +$0098E: 5281
    move.l d1,88(a2)                                   ; +$00990: 25410058
    move.l d0,d2                                       ; +$00994: 2400
    andi.l #$00000080,d2                               ; +$00996: 028200000080
    move.l d2,92(a2)                                   ; +$0099C: 2542005C
    move.l 84(a2),d2                                   ; +$009A0: 242A0054
    add.l d1,d2                                        ; +$009A4: D481
    cmp.l 40(a2),d2                                    ; +$009A6: B4AA0028
    bgt.w L_BOBS_00A92                                 ; +$009AA: 6E0000E6
    move.l a0,d2                                       ; +$009AE: 2408
    move.l d2,76(a2)                                   ; +$009B0: 2542004C
    move.l 92(a2),d2                                   ; +$009B4: 242A005C
    tst.l d2                                           ; +$009B8: 4A82
    beq.w L_BOBS_009CA                                 ; +$009BA: 6700000E
    move.l a0,96(a2)                                   ; +$009BE: 25480060
    move.l 36(a2),d2                                   ; +$009C2: 242A0024
    bra.w L_BOBS_009D0                                 ; +$009C6: 60000008
L_BOBS_009CA:
    move.l 36(a2),d2                                   ; +$009CA: 242A0024
    mulu.w d1,d2                                       ; +$009CE: C4C1
L_BOBS_009D0:
    move.l a0,d0                                       ; +$009D0: 2008
    add.l d2,d0                                        ; +$009D2: D082
    bcs.w L_BOBS_00A92                                 ; +$009D4: 650000BC
    cmp.l 80(a2),d0                                    ; +$009D8: B0AA0050
    bgt.w L_BOBS_00A92                                 ; +$009DC: 6E0000B4
L_BOBS_009E0:
    move.l 92(a2),d2                                   ; +$009E0: 242A005C
    tst.l d2                                           ; +$009E4: 4A82
    bne.w L_BOBS_009FE                                 ; +$009E6: 66000016
    move.l 76(a2),d0                                   ; +$009EA: 202A004C
    move.l d0,96(a2)                                   ; +$009EE: 25400060
    add.l 36(a2),d0                                    ; +$009F2: D0AA0024
    move.l d0,76(a2)                                   ; +$009F6: 2540004C
    bra.w L_BOBS_00A14                                 ; +$009FA: 60000018
L_BOBS_009FE:
    move.l 76(a2),d0                                   ; +$009FE: 202A004C
    move.l 96(a2),d1                                   ; +$00A02: 222A0060
    cmp.l d1,d0                                        ; +$00A06: B081
    bne.w L_BOBS_00A14                                 ; +$00A08: 6600000A
    add.l 36(a2),d0                                    ; +$00A0C: D0AA0024
    move.l d0,76(a2)                                   ; +$00A10: 2540004C
L_BOBS_00A14:
    move.l 44(a2),d0                                   ; +$00A14: 202A002C
    tst.l d0                                           ; +$00A18: 4A80
    beq.w L_BOBS_00A4A                                 ; +$00A1A: 6700002E
    move.l 84(a2),d1                                   ; +$00A1E: 222A0054
    addq.l #1,d1                                       ; +$00A22: 5281
    cmp.l 40(a2),d1                                    ; +$00A24: B2AA0028
    bne.w L_BOBS_00A4A                                 ; +$00A28: 66000020
    movea.l 96(a2),a0                                  ; +$00A2C: 206A0060
    move.l 36(a2),d1                                   ; +$00A30: 222A0024
    lsr.l #1,d1                                        ; +$00A34: E289
L_BOBS_00A36:
    move.l #$00000000,d2                               ; +$00A36: 243C00000000
    move.w (a0)+,d2                                    ; +$00A3C: 3418
    and.w d0,d2                                        ; +$00A3E: C440
    bne.w L_BOBS_00A92                                 ; +$00A40: 66000050
    subq.l #1,d1                                       ; +$00A44: 5381
    bne.w L_BOBS_00A36                                 ; +$00A46: 6600FFEE
L_BOBS_00A4A:
    move.l 72(a2),d0                                   ; +$00A4A: 202A0048
    tst.l d0                                           ; +$00A4E: 4A80
    beq.w L_BOBS_00A58                                 ; +$00A50: 67000006
    bsr.w L_BOBS_00A9A                                 ; +$00A54: 61000044
L_BOBS_00A58:
    move.l 88(a2),d0                                   ; +$00A58: 202A0058
    subq.l #1,d0                                       ; +$00A5C: 5380
    move.l d0,88(a2)                                   ; +$00A5E: 25400058
    move.l 84(a2),d0                                   ; +$00A62: 202A0054
    addq.l #1,d0                                       ; +$00A66: 5280
    move.l d0,84(a2)                                   ; +$00A68: 25400054
    bra.w L_BOBS_0095A                                 ; +$00A6C: 6000FEEC
L_BOBS_00A70:
    move.l 76(a2),d0                                   ; +$00A70: 202A004C
    cmp.l 80(a2),d0                                    ; +$00A74: B0AA0050
    bne.w L_BOBS_00A92                                 ; +$00A78: 66000018
    move.l 68(a2),d0                                   ; +$00A7C: 202A0044
    addq.l #1,d0                                       ; +$00A80: 5280
    move.l d0,68(a2)                                   ; +$00A82: 25400044
    bra.w L_BOBS_008D4                                 ; +$00A86: 6000FE4C
L_BOBS_00A8A:
    move.l #$00000001,d0                               ; +$00A8A: 203C00000001
    rts                                                ; +$00A90: 4E75
L_BOBS_00A92:
    move.l #$00000000,d0                               ; +$00A92: 203C00000000
    rts                                                ; +$00A98: 4E75
L_BOBS_00A9A:
    move.l 32(a2),d0                                   ; +$00A9A: 202A0020
    andi.l #$00000001,d0                               ; +$00A9E: 028000000001
    move.l d0,32(a2)                                   ; +$00AA4: 25400020
    move.l 68(a2),d0                                   ; +$00AA8: 202A0044
    sub.l 132(a2),d0                                   ; +$00AAC: 90AA0084
    tst.l d0                                           ; +$00AB0: 4A80
    bmi.w L_BOBS_00BC6                                 ; +$00AB2: 6B000112
    cmp.l 140(a2),d0                                   ; +$00AB6: B0AA008C
    bge.w L_BOBS_00BC6                                 ; +$00ABA: 6C00010A
    add.l 4(a2),d0                                     ; +$00ABE: D0AA0004
    tst.l d0                                           ; +$00AC2: 4A80
    bmi.w L_BOBS_00BC6                                 ; +$00AC4: 6B000100
    cmp.l 56(a2),d0                                    ; +$00AC8: B0AA0038
    bge.w L_BOBS_00BC6                                 ; +$00ACC: 6C0000F8
    move.l d0,108(a2)                                  ; +$00AD0: 2540006C
    move.l 84(a2),d0                                   ; +$00AD4: 202A0054
    lsl.l #4,d0                                        ; +$00AD8: E988
    move.l 128(a2),d1                                  ; +$00ADA: 222A0080
    move.l 136(a2),d2                                  ; +$00ADE: 242A0088
    add.l d1,d2                                        ; +$00AE2: D481
    move.l 8(a2),d3                                    ; +$00AE4: 262A0008
    move.l 52(a2),d4                                   ; +$00AE8: 282A0034
    move.l 20(a2),d5                                   ; +$00AEC: 2A2A0014
    bsr.w L_BOBS_00BC8                                 ; +$00AF0: 610000D6
    cmp.l d6,d7                                        ; +$00AF4: BE86
    ble.w L_BOBS_00BC6                                 ; +$00AF6: 6F0000CE
    move.l d6,124(a2)                                  ; +$00AFA: 2546007C
    sub.l d6,d7                                        ; +$00AFE: 9E86
    move.l d7,184(a2)                                  ; +$00B00: 254700B8
    add.l d6,d0                                        ; +$00B04: D086
    sub.l 128(a2),d0                                   ; +$00B06: 90AA0080
    add.l 8(a2),d0                                     ; +$00B0A: D0AA0008
    move.l d0,104(a2)                                  ; +$00B0E: 25400068
    move.l 108(a2),d0                                  ; +$00B12: 202A006C
    move.l 60(a2),d1                                   ; +$00B16: 222A003C
    mulu.w d1,d0                                       ; +$00B1A: C0C1
    move.l 104(a2),d1                                  ; +$00B1C: 222A0068
    lsr.l #3,d1                                        ; +$00B20: E689
    add.l d1,d0                                        ; +$00B22: D081
    move.l d0,112(a2)                                  ; +$00B24: 25400070
    movea.l 64(a2),a6                                  ; +$00B28: 2C6A0040
    addq.l #8,a6                                       ; +$00B2C: 508E
    lea 152(a2),a0                                     ; +$00B2E: 41EA0098
    move.l 28(a2),d7                                   ; +$00B32: 2E2A001C
L_BOBS_00B36:
    movea.l (a6)+,a1                                   ; +$00B36: 225E
    move.l a1,d1                                       ; +$00B38: 2209
    add.l 112(a2),d1                                   ; +$00B3A: D2AA0070
    move.l d1,(a0)+                                    ; +$00B3E: 20C1
    subq.w #1,d7                                       ; +$00B40: 5347
    bne.w L_BOBS_00B36                                 ; +$00B42: 6600FFF2
    movea.l 96(a2),a0                                  ; +$00B46: 206A0060
    move.l 32(a2),d5                                   ; +$00B4A: 2A2A0020
    tst.l d5                                           ; +$00B4E: 4A85
    beq.w L_BOBS_00B56                                 ; +$00B50: 67000004
    addq.l #2,a0                                       ; +$00B54: 5488
L_BOBS_00B56:
    move.l (a2),d2                                     ; +$00B56: 2412
    tst.l d2                                           ; +$00B58: 4A82
    bne.w L_BOBS_00B74                                 ; +$00B5A: 66000018
    move.l #$0000FFFF,d2                               ; +$00B5E: 243C0000FFFF
    move.l #$FFFFFFFF,148(a2)                          ; +$00B64: 257CFFFFFFFF0094
    lea 148(a2),a1                                     ; +$00B6C: 43EA0094
    bra.w L_BOBS_00B80                                 ; +$00B70: 6000000E
L_BOBS_00B74:
    movea.l 96(a2),a1                                  ; +$00B74: 226A0060
    move.l #$00000000,d2                               ; +$00B78: 243C00000000
    move.w (a1),d2                                     ; +$00B7E: 3411
L_BOBS_00B80:
    tst.l d2                                           ; +$00B80: 4A82
    beq.w L_BOBS_00BC6                                 ; +$00B82: 67000042
    move.l 124(a2),d4                                  ; +$00B86: 282A007C
    move.l 184(a2),d6                                  ; +$00B8A: 2C2A00B8
    move.l 104(a2),d0                                  ; +$00B8E: 202A0068
    andi.l #$00000007,d0                               ; +$00B92: 028000000007
    move.l 28(a2),d7                                   ; +$00B98: 2E2A001C
    tst.l d4                                           ; +$00B9C: 4A84
    bne.w L_BOBS_00BBA                                 ; +$00B9E: 6600001A
    cmpi.l #$00000010,d6                               ; +$00BA2: 0C8600000010
    bne.w L_BOBS_00BBA                                 ; +$00BA8: 66000010
    lea 152(a2),a1                                     ; +$00BAC: 43EA0098
    move.l d7,d6                                       ; +$00BB0: 2C07
    bsr.w L_BOBS_00C16                                 ; +$00BB2: 61000062
    bra.w L_BOBS_00BC2                                 ; +$00BB6: 6000000A
L_BOBS_00BBA:
    lea 152(a2),a2                                     ; +$00BBA: 45EA0098
    bsr.w L_BOBS_00C3A                                 ; +$00BBE: 6100007A
L_BOBS_00BC2:
    lea 8(a7),a2                                       ; +$00BC2: 45EF0008
L_BOBS_00BC6:
    rts                                                ; +$00BC6: 4E75
L_BOBS_00BC8:
    move.l d0,d6                                       ; +$00BC8: 2C00
    cmp.l d1,d6                                        ; +$00BCA: BC81
    bge.w L_BOBS_00BD2                                 ; +$00BCC: 6C000004
    move.l d1,d6                                       ; +$00BD0: 2C01
L_BOBS_00BD2:
    move.l d1,d7                                       ; +$00BD2: 2E01
    sub.l d3,d7                                        ; +$00BD4: 9E83
    cmp.l d7,d6                                        ; +$00BD6: BC87
    bge.w L_BOBS_00BDE                                 ; +$00BD8: 6C000004
    move.l d7,d6                                       ; +$00BDC: 2C07
L_BOBS_00BDE:
    move.l d0,d7                                       ; +$00BDE: 2E00
    addi.l #$00000010,d7                               ; +$00BE0: 068700000010
    cmp.l d2,d7                                        ; +$00BE6: BE82
    ble.w L_BOBS_00BEE                                 ; +$00BE8: 6F000004
    move.l d2,d7                                       ; +$00BEC: 2E02
L_BOBS_00BEE:
    cmp.l d5,d7                                        ; +$00BEE: BE85
    ble.w L_BOBS_00BF6                                 ; +$00BF0: 6F000004
    move.l d5,d7                                       ; +$00BF4: 2E05
L_BOBS_00BF6:
    move.l d1,d5                                       ; +$00BF6: 2A01
    add.l d4,d5                                        ; +$00BF8: DA84
    sub.l d3,d5                                        ; +$00BFA: 9A83
    cmp.l d5,d7                                        ; +$00BFC: BE85
    ble.w L_BOBS_00C04                                 ; +$00BFE: 6F000004
    move.l d5,d7                                       ; +$00C02: 2E05
L_BOBS_00C04:
    cmp.l d6,d7                                        ; +$00C04: BE86
    ble.w L_BOBS_00C10                                 ; +$00C06: 6F000008
    sub.l d0,d6                                        ; +$00C0A: 9C80
    sub.l d0,d7                                        ; +$00C0C: 9E80
    rts                                                ; +$00C0E: 4E75
L_BOBS_00C10:
    moveq #0,d6                                        ; +$00C10: 7C00
    moveq #0,d7                                        ; +$00C12: 7E00
    rts                                                ; +$00C14: 4E75
L_BOBS_00C16:
    bfextu (a0){0:16},d1                               ; +$00C16: E9D01010
    addq.l #2,a0                                       ; +$00C1A: 5488
    movea.l (a1)+,a2                                   ; +$00C1C: 2459
    bfextu (a2){d0:16},d4                              ; +$00C1E: E9D24810
    move.w d2,d7                                       ; +$00C22: 3E02
    not.w d7                                           ; +$00C24: 4647
    and.w d2,d1                                        ; +$00C26: C242
    and.w d7,d4                                        ; +$00C28: C847
    or.w d4,d1                                         ; +$00C2A: 8244
    bfins d1,(a2){d0:16}                               ; +$00C2C: EFD21810
    subq.w #1,d6                                       ; +$00C30: 5346
    bne.w L_BOBS_00C16                                 ; +$00C32: 6600FFE2
    moveq #1,d3                                        ; +$00C36: 7601
    rts                                                ; +$00C38: 4E75
L_BOBS_00C3A:
    bfextu (a1){d4:d6},d2                              ; +$00C3A: E9D12926
L_BOBS_00C3E:
    bfextu (a0){d4:d6},d1                              ; +$00C3E: E9D01926
    addq.l #2,a0                                       ; +$00C42: 5488
    movea.l (a2)+,a4                                   ; +$00C44: 285A
    bfextu (a4){d0:d6},d3                              ; +$00C46: E9D43826
    eor.w d3,d1                                        ; +$00C4A: B741
    and.w d2,d1                                        ; +$00C4C: C242
    eor.w d3,d1                                        ; +$00C4E: B741
    bfins d1,(a4){d0:d6}                               ; +$00C50: EFD41826
    subq.w #1,d7                                       ; +$00C54: 5347
    bne.w L_BOBS_00C3E                                 ; +$00C56: 6600FFE6
    moveq #1,d3                                        ; +$00C5A: 7601
    rts                                                ; +$00C5C: 4E75
L_BOBS_00C5E:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00C5E: 48E7EFEE
    lea -48(a7),a7                                     ; +$00C62: 4FEFFFD0
    movea.l a7,a2                                      ; +$00C66: 244F
    move.l d3,(a2)                                     ; +$00C68: 2483
    move.l (a3)+,d7                                    ; +$00C6A: 2E1B
    move.l d7,4(a2)                                    ; +$00C6C: 25470004
    move.l (a3)+,d7                                    ; +$00C70: 2E1B
    move.l d7,8(a2)                                    ; +$00C72: 25470008
    move.l (a3)+,d7                                    ; +$00C76: 2E1B
    move.l d7,12(a2)                                   ; +$00C78: 2547000C
    move.l a3,16(a2)                                   ; +$00C7C: 254B0010
    move.l 12(a2),d0                                   ; +$00C80: 202A000C
    cmpi.l #$00000005,d0                               ; +$00C84: 0C8000000005
    bcs.w L_BOBS_00CE0                                 ; +$00C8A: 65000054
    cmpi.l #$0000FFFF,d0                               ; +$00C8E: 0C800000FFFF
    bhi.w L_BOBS_00CE0                                 ; +$00C94: 6200004A
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$00C98: FE11F700031D
    move.l a0,d0                                       ; +$00C9E: 2008
    tst.l d0                                           ; +$00CA0: 4A80
    beq.w L_BOBS_00CE0                                 ; +$00CA2: 6700003C
    move.l a0,32(a2)                                   ; +$00CA6: 25480020
    move.l -20(a0),d1                                  ; +$00CAA: 2228FFEC
    cmpi.l #$00000010,d1                               ; +$00CAE: 0C8100000010
    bcs.w L_BOBS_00CE0                                 ; +$00CB4: 6500002A
    subi.l #$00000010,d1                               ; +$00CB8: 048100000010
    move.l d1,28(a2)                                   ; +$00CBE: 2541001C
    move.l 4(a2),d0                                    ; +$00CC2: 202A0004
    move.l d0,20(a2)                                   ; +$00CC6: 25400014
    move.l 8(a2),d0                                    ; +$00CCA: 202A0008
    move.l d0,24(a2)                                   ; +$00CCE: 25400018
    move.l (a2),d3                                     ; +$00CD2: 2612
    lea 20(a2),a3                                      ; +$00CD4: 47EA0014
    bsr.w L_BOBS_002D0                                 ; +$00CD8: 6100F5F6
    bra.w L_BOBS_00CE6                                 ; +$00CDC: 60000008
L_BOBS_00CE0:
    move.l #$00000000,d3                               ; +$00CE0: 263C00000000
L_BOBS_00CE6:
    movea.l 16(a2),a3                                  ; +$00CE6: 266A0010
    lea 48(a7),a7                                      ; +$00CEA: 4FEF0030
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$00CEE: 4CDF77F7
    moveq #0,d2                                        ; +$00CF2: 7400
    rts                                                ; +$00CF4: 4E75
L_BOBS_00CF6:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$00CF6: 48E7EFEE
    lea -96(a7),a7                                     ; +$00CFA: 4FEFFFA0
    movea.l a7,a2                                      ; +$00CFE: 244F
    move.l d3,(a2)                                     ; +$00D00: 2483
    move.l (a3)+,d7                                    ; +$00D02: 2E1B
    move.l d7,4(a2)                                    ; +$00D04: 25470004
    move.l (a3)+,d7                                    ; +$00D08: 2E1B
    move.l d7,8(a2)                                    ; +$00D0A: 25470008
    move.l (a3)+,d7                                    ; +$00D0E: 2E1B
    move.l d7,12(a2)                                   ; +$00D10: 2547000C
    move.l (a3)+,d7                                    ; +$00D14: 2E1B
    move.l d7,16(a2)                                   ; +$00D16: 25470010
    move.l #$00000000,d3                               ; +$00D1A: 263C00000000
    movea.l $0004.w,a0                                 ; +$00D20: 20780004
    move.l a0,d0                                       ; +$00D24: 2008
    tst.l d0                                           ; +$00D26: 4A80
    beq.w L_BOBS_01102                                 ; +$00D28: 670003D8
    move.w 296(a0),d0                                  ; +$00D2C: 30280128
    btst #1,d0                                         ; +$00D30: 08000001
    beq.w L_BOBS_01102                                 ; +$00D34: 670003CC
    move.l (a2),d0                                     ; +$00D38: 2012
    cmpi.l #$00000001,d0                               ; +$00D3A: 0C8000000001
    bhi.w L_BOBS_01102                                 ; +$00D40: 620003C0
    move.l 8(a2),d0                                    ; +$00D44: 202A0008
    cmpi.l #$FFFF8000,d0                               ; +$00D48: 0C80FFFF8000
    blt.w L_BOBS_01102                                 ; +$00D4E: 6D0003B2
    cmpi.l #$00007FFF,d0                               ; +$00D52: 0C8000007FFF
    bgt.w L_BOBS_01102                                 ; +$00D58: 6E0003A8
    move.l 4(a2),d0                                    ; +$00D5C: 202A0004
    cmpi.l #$FFFF8000,d0                               ; +$00D60: 0C80FFFF8000
    blt.w L_BOBS_01102                                 ; +$00D66: 6D00039A
    cmpi.l #$00007FFF,d0                               ; +$00D6A: 0C8000007FFF
    bgt.w L_BOBS_01102                                 ; +$00D70: 6E000390
    move.l 12(a2),d0                                   ; +$00D74: 202A000C
    tst.l d0                                           ; +$00D78: 4A80
    ble.w L_BOBS_01102                                 ; +$00D7A: 6F000386
    cmpi.l #$00001000,d0                               ; +$00D7E: 0C8000001000
    bgt.w L_BOBS_01102                                 ; +$00D84: 6E00037C
    move.l 16(a2),d0                                   ; +$00D88: 202A0010
    cmpi.l #$00000005,d0                               ; +$00D8C: 0C8000000005
    bcs.w L_BOBS_01102                                 ; +$00D92: 6500036E
    cmpi.l #$0000FFFF,d0                               ; +$00D96: 0C800000FFFF
    bhi.w L_BOBS_01102                                 ; +$00D9C: 62000364
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$00DA0: FE11F700031D
    move.l a0,d5                                       ; +$00DA6: 2A08
    cmpi.l #$00000018,d5                               ; +$00DA8: 0C8500000018
    bls.w L_BOBS_01102                                 ; +$00DAE: 63000352
    move.l d5,d0                                       ; +$00DB2: 2005
    andi.l #$00000001,d0                               ; +$00DB4: 028000000001
    bne.w L_BOBS_01102                                 ; +$00DBA: 66000346
    move.l d5,20(a2)                                   ; +$00DBE: 25450014
    movea.l d5,a1                                      ; +$00DC2: 2245
    movea.l $0004.w,a6                                 ; +$00DC4: 2C780004
    jsr -534(a6)                                       ; +$00DC8: 4EAEFDEA
    tst.l d0                                           ; +$00DCC: 4A80
    beq.w L_BOBS_01102                                 ; +$00DCE: 67000332
    move.l 20(a2),d5                                   ; +$00DD2: 2A2A0014
    move.l d5,d0                                       ; +$00DD6: 2005
    subi.l #$00000018,d0                               ; +$00DD8: 048000000018
    movea.l d0,a1                                      ; +$00DDE: 2240
    movea.l $0004.w,a6                                 ; +$00DE0: 2C780004
    jsr -534(a6)                                       ; +$00DE4: 4EAEFDEA
    tst.l d0                                           ; +$00DE8: 4A80
    beq.w L_BOBS_01102                                 ; +$00DEA: 67000316
    movea.l d5,a0                                      ; +$00DEE: 2045
    move.l -20(a0),d4                                  ; +$00DF0: 2828FFEC
    cmpi.l #$0000001C,d4                               ; +$00DF4: 0C840000001C
    bcs.w L_BOBS_01102                                 ; +$00DFA: 65000306
    subi.l #$00000010,d4                               ; +$00DFE: 048400000010
    cmpi.l #$0012000C,d4                               ; +$00E04: 0C840012000C
    bhi.w L_BOBS_01102                                 ; +$00E0A: 620002F6
    move.l d4,24(a2)                                   ; +$00E0E: 25440018
    move.l d5,d0                                       ; +$00E12: 2005
    add.l d4,d0                                        ; +$00E14: D084
    bcs.w L_BOBS_01102                                 ; +$00E16: 650002EA
    subq.l #1,d0                                       ; +$00E1A: 5380
    movea.l d0,a1                                      ; +$00E1C: 2240
    movea.l $0004.w,a6                                 ; +$00E1E: 2C780004
    jsr -534(a6)                                       ; +$00E22: 4EAEFDEA
    tst.l d0                                           ; +$00E26: 4A80
    beq.w L_BOBS_01102                                 ; +$00E28: 670002D8
    move.l 20(a2),d5                                   ; +$00E2C: 2A2A0014
    movea.l d5,a0                                      ; +$00E30: 2045
    move.l -16(a0),d0                                  ; +$00E32: 2028FFF0
    move.l 16(a2),d1                                   ; +$00E36: 222A0010
    cmp.l d1,d0                                        ; +$00E3A: B081
    bne.w L_BOBS_01102                                 ; +$00E3C: 660002C4
    move.l #$00000000,d0                               ; +$00E40: 203C00000000
    move.w -12(a0),d0                                  ; +$00E46: 3028FFF4
    tst.l d0                                           ; +$00E4A: 4A80
    beq.w L_BOBS_00E5E                                 ; +$00E4C: 67000010
    andi.w #$FFFD,d0                                   ; +$00E50: 0240FFFD
    cmpi.l #$00000001,d0                               ; +$00E54: 0C8000000001
    bne.w L_BOBS_01102                                 ; +$00E5A: 660002A6
L_BOBS_00E5E:
    move.l -8(a0),d0                                   ; +$00E5E: 2028FFF8
    cmpi.l #$4649434F,d0                               ; +$00E62: 0C804649434F
    bne.w L_BOBS_01102                                 ; +$00E68: 66000298
    move.l -4(a0),d0                                   ; +$00E6C: 2028FFFC
    cmpi.l #$4E382020,d0                               ; +$00E70: 0C804E382020
    bne.w L_BOBS_01102                                 ; +$00E76: 6600028A
    move.l (a0),d0                                     ; +$00E7A: 2010
    cmp.l 24(a2),d0                                    ; +$00E7C: B0AA0018
    bne.w L_BOBS_01102                                 ; +$00E80: 66000280
    move.l #$00000000,d0                               ; +$00E84: 203C00000000
    move.w 4(a0),d0                                    ; +$00E8A: 30280004
    move.l d0,28(a2)                                   ; +$00E8E: 2540001C
    cmpi.l #$00000004,d0                               ; +$00E92: 0C8000000004
    bcs.w L_BOBS_01102                                 ; +$00E98: 65000268
    cmpi.l #$00001000,d0                               ; +$00E9C: 0C8000001000
    bgt.w L_BOBS_01102                                 ; +$00EA2: 6E00025E
    move.l 12(a2),d1                                   ; +$00EA6: 222A000C
    cmp.l d1,d0                                        ; +$00EAA: B081
    bcs.w L_BOBS_01102                                 ; +$00EAC: 65000254
    move.l #$00000120,d1                               ; +$00EB0: 223C00000120
    mulu.w d1,d0                                       ; +$00EB6: C0C1
    addi.l #$0000000C,d0                               ; +$00EB8: 06800000000C
    cmp.l 24(a2),d0                                    ; +$00EBE: B0AA0018
    bne.w L_BOBS_01102                                 ; +$00EC2: 6600023E
    move.l #$00000000,d0                               ; +$00EC6: 203C00000000
    move.w 6(a0),d0                                    ; +$00ECC: 30280006
    cmpi.l #$00000010,d0                               ; +$00ED0: 0C8000000010
    bne.w L_BOBS_01102                                 ; +$00ED6: 6600022A
    move.l #$00000000,d0                               ; +$00EDA: 203C00000000
    move.w 8(a0),d0                                    ; +$00EE0: 30280008
    cmpi.l #$00000010,d0                               ; +$00EE4: 0C8000000010
    bne.w L_BOBS_01102                                 ; +$00EEA: 66000216
    move.l #$00000000,d0                               ; +$00EEE: 203C00000000
    move.w 10(a0),d0                                   ; +$00EF4: 3028000A
    cmpi.l #$00000008,d0                               ; +$00EF8: 0C8000000008
    bne.w L_BOBS_01102                                 ; +$00EFE: 66000202
    move.l 12(a2),d0                                   ; +$00F02: 202A000C
    subq.l #1,d0                                       ; +$00F06: 5380
    move.l #$00000120,d1                               ; +$00F08: 223C00000120
    mulu.w d1,d0                                       ; +$00F0E: C0C1
    addi.l #$0000000C,d0                               ; +$00F10: 06800000000C
    add.l d5,d0                                        ; +$00F16: D085
    bcs.w L_BOBS_01102                                 ; +$00F18: 650001E8
    move.l d0,32(a2)                                   ; +$00F1C: 25400020
    movea.l d0,a0                                      ; +$00F20: 2040
    move.l #$00000010,d6                               ; +$00F22: 2C3C00000010
L_BOBS_00F28:
    move.w (a0)+,d4                                    ; +$00F28: 3818
    move.l #$00000000,d7                               ; +$00F2A: 2E3C00000000
    move.l #$00000008,d5                               ; +$00F30: 2A3C00000008
L_BOBS_00F36:
    or.w (a0)+,d7                                      ; +$00F36: 8E58
    subq.l #1,d5                                       ; +$00F38: 5385
    bne.w L_BOBS_00F36                                 ; +$00F3A: 6600FFFA
    not.w d7                                           ; +$00F3E: 4647
    cmp.w d4,d7                                        ; +$00F40: BE44
    bne.w L_BOBS_01102                                 ; +$00F42: 660001BE
    subq.l #1,d6                                       ; +$00F46: 5386
    bne.w L_BOBS_00F28                                 ; +$00F48: 6600FFDE
    movea.l 456(a5),a4                                 ; +$00F4C: 286D01C8
    move.l a4,d0                                       ; +$00F50: 200C
    tst.l d0                                           ; +$00F52: 4A80
    beq.w L_BOBS_01102                                 ; +$00F54: 670001AC
    move.l (a4),d0                                     ; +$00F58: 2014
    tst.l d0                                           ; +$00F5A: 4A80
    beq.w L_BOBS_01102                                 ; +$00F5C: 670001A4
    move.l 8(a4),d0                                    ; +$00F60: 202C0008
    tst.l d0                                           ; +$00F64: 4A80
    beq.w L_BOBS_01102                                 ; +$00F66: 6700019A
    move.l 32(a4),d0                                   ; +$00F6A: 202C0020
    tst.l d0                                           ; +$00F6E: 4A80
    beq.w L_BOBS_01102                                 ; +$00F70: 67000190
    move.l 12(a4),d0                                   ; +$00F74: 202C000C
    tst.l d0                                           ; +$00F78: 4A80
    ble.w L_BOBS_01102                                 ; +$00F7A: 6F000186
    cmpi.l #$00007FFF,d0                               ; +$00F7E: 0C8000007FFF
    bgt.w L_BOBS_01102                                 ; +$00F84: 6E00017C
    move.l d0,36(a2)                                   ; +$00F88: 25400024
    move.l 16(a4),d0                                   ; +$00F8C: 202C0010
    tst.l d0                                           ; +$00F90: 4A80
    ble.w L_BOBS_01102                                 ; +$00F92: 6F00016E
    cmpi.l #$00007FFF,d0                               ; +$00F96: 0C8000007FFF
    bgt.w L_BOBS_01102                                 ; +$00F9C: 6E000164
    move.l d0,40(a2)                                   ; +$00FA0: 25400028
    move.l 28(a4),d0                                   ; +$00FA4: 202C001C
    cmpi.l #$00000008,d0                               ; +$00FA8: 0C8000000008
    bne.w L_BOBS_01102                                 ; +$00FAE: 66000152
    movea.l 32(a4),a0                                  ; +$00FB2: 206C0020
    move.l 8(a0),d0                                    ; +$00FB6: 20280008
    tst.l d0                                           ; +$00FBA: 4A80
    beq.w L_BOBS_00FD4                                 ; +$00FBC: 67000016
    cmpi.l #$00000001,d0                               ; +$00FC0: 0C8000000001
    bne.w L_BOBS_01102                                 ; +$00FC6: 6600013A
    movea.l 32(a4),a0                                  ; +$00FCA: 206C0020
    movea.l (a0),a1                                    ; +$00FCE: 2250
    bra.w L_BOBS_00FDC                                 ; +$00FD0: 6000000A
L_BOBS_00FD4:
    movea.l 32(a4),a0                                  ; +$00FD4: 206C0020
    movea.l 4(a0),a1                                   ; +$00FD8: 22680004
L_BOBS_00FDC:
    move.l a1,d0                                       ; +$00FDC: 2009
    tst.l d0                                           ; +$00FDE: 4A80
    beq.w L_BOBS_01102                                 ; +$00FE0: 67000120
    movea.l (a1),a0                                    ; +$00FE4: 2051
    move.l a0,d0                                       ; +$00FE6: 2008
    tst.l d0                                           ; +$00FE8: 4A80
    beq.w L_BOBS_01102                                 ; +$00FEA: 67000116
    move.l a0,48(a2)                                   ; +$00FEE: 25480030
    move.l #$00000000,d1                               ; +$00FF2: 223C00000000
    move.w (a0),d1                                     ; +$00FF8: 3210
    tst.l d1                                           ; +$00FFA: 4A81
    beq.w L_BOBS_01102                                 ; +$00FFC: 67000104
    move.l d1,44(a2)                                   ; +$01000: 2541002C
    lsl.l #3,d1                                        ; +$01004: E789
    cmp.l 36(a2),d1                                    ; +$01006: B2AA0024
    blt.w L_BOBS_01102                                 ; +$0100A: 6D0000F6
    move.l #$00000000,d1                               ; +$0100E: 223C00000000
    move.w 2(a0),d1                                    ; +$01014: 32280002
    cmp.l 40(a2),d1                                    ; +$01018: B2AA0028
    blt.w L_BOBS_01102                                 ; +$0101C: 6D0000E4
    move.l #$00000000,d1                               ; +$01020: 223C00000000
    move.b 5(a0),d1                                    ; +$01026: 12280005
    cmpi.l #$00000008,d1                               ; +$0102A: 0C8100000008
    bne.w L_BOBS_01102                                 ; +$01030: 660000D0
    movea.l a0,a1                                      ; +$01034: 2248
    addq.l #8,a1                                       ; +$01036: 5089
    move.l #$00000008,d0                               ; +$01038: 203C00000008
L_BOBS_0103E:
    move.l (a1)+,d1                                    ; +$0103E: 2219
    tst.l d1                                           ; +$01040: 4A81
    beq.w L_BOBS_01102                                 ; +$01042: 670000BE
    cmpi.l #$FFFFFFFF,d1                               ; +$01046: 0C81FFFFFFFF
    beq.w L_BOBS_01102                                 ; +$0104C: 670000B4
    move.l d1,d5                                       ; +$01050: 2A01
    andi.l #$00000001,d5                               ; +$01052: 028500000001
    bne.w L_BOBS_01102                                 ; +$01058: 660000A8
    subq.l #1,d0                                       ; +$0105C: 5380
    bne.w L_BOBS_0103E                                 ; +$0105E: 6600FFDE
    move.l 8(a2),d0                                    ; +$01062: 202A0008
    cmp.l 36(a2),d0                                    ; +$01066: B0AA0024
    bge.w L_BOBS_010F8                                 ; +$0106A: 6C00008C
    addi.l #$00000010,d0                               ; +$0106E: 068000000010
    tst.l d0                                           ; +$01074: 4A80
    ble.w L_BOBS_010F8                                 ; +$01076: 6F000080
    move.l 4(a2),d0                                    ; +$0107A: 202A0004
    cmp.l 40(a2),d0                                    ; +$0107E: B0AA0028
    bge.w L_BOBS_010F8                                 ; +$01082: 6C000074
    addi.l #$00000010,d0                               ; +$01086: 068000000010
    tst.l d0                                           ; +$0108C: 4A80
    ble.w L_BOBS_010F8                                 ; +$0108E: 6F000068
    movea.l 32(a4),a0                                  ; +$01092: 206C0020
    move.l 20(a0),d0                                   ; +$01096: 20280014
    andi.l #$00000001,d0                               ; +$0109A: 028000000001
    beq.w L_BOBS_010D0                                 ; +$010A0: 6700002E
    movea.l 12(a0),a0                                  ; +$010A4: 2068000C
    move.l a0,d0                                       ; +$010A8: 2008
    tst.l d0                                           ; +$010AA: 4A80
    beq.w L_BOBS_01102                                 ; +$010AC: 67000054
    movea.l $0004.w,a6                                 ; +$010B0: 2C780004
    jsr -372(a6)                                       ; +$010B4: 4EAEFE8C
    tst.l d0                                           ; +$010B8: 4A80
    beq.w L_BOBS_01102                                 ; +$010BA: 67000046
    movea.l 32(a4),a0                                  ; +$010BE: 206C0020
    move.l 20(a0),d0                                   ; +$010C2: 20280014
    andi.l #$FFFFFFFE,d0                               ; +$010C6: 0280FFFFFFFE
    move.l d0,20(a0)                                   ; +$010CC: 21400014
L_BOBS_010D0:
    move.l 8(a2),d0                                    ; +$010D0: 202A0008
    move.l 4(a2),d1                                    ; +$010D4: 222A0004
    move.l 44(a2),d2                                   ; +$010D8: 242A002C
    move.l (a2),d3                                     ; +$010DC: 2612
    move.l 36(a2),d4                                   ; +$010DE: 282A0024
    move.l 40(a2),d5                                   ; +$010E2: 2A2A0028
    movea.l 32(a2),a0                                  ; +$010E6: 206A0020
    movea.l 48(a2),a1                                  ; +$010EA: 226A0030
    addq.l #8,a1                                       ; +$010EE: 5089
    bsr.w L_BOBS_01114                                 ; +$010F0: 61000022
    bra.w L_BOBS_01108                                 ; +$010F4: 60000012
L_BOBS_010F8:
    move.l #$00000001,d3                               ; +$010F8: 263C00000001
    bra.w L_BOBS_01108                                 ; +$010FE: 60000008
L_BOBS_01102:
    move.l #$00000000,d3                               ; +$01102: 263C00000000
L_BOBS_01108:
    lea 96(a7),a7                                      ; +$01108: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0110C: 4CDF77F7
    moveq #0,d2                                        ; +$01110: 7400
    rts                                                ; +$01112: 4E75
L_BOBS_01114:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$01114: 48E7EFEE
    lea -96(a7),a7                                     ; +$01118: 4FEFFFA0
    movea.l a7,a2                                      ; +$0111C: 244F
    movea.l $0004.w,a4                                 ; +$0111E: 28780004
    move.l a4,d6                                       ; +$01122: 2C0C
    tst.l d6                                           ; +$01124: 4A86
    beq.w L_BOBS_01452                                 ; +$01126: 6700032A
    move.w 296(a4),d6                                  ; +$0112A: 3C2C0128
    btst #1,d6                                         ; +$0112E: 08060001
    beq.w L_BOBS_01452                                 ; +$01132: 6700031E
    move.l d0,(a2)                                     ; +$01136: 2480
    move.l d1,4(a2)                                    ; +$01138: 25410004
    move.l d2,8(a2)                                    ; +$0113C: 25420008
    move.l d4,12(a2)                                   ; +$01140: 2544000C
    move.l d5,16(a2)                                   ; +$01144: 25450010
    move.l d3,20(a2)                                   ; +$01148: 25430014
    move.l a0,d6                                       ; +$0114C: 2C08
    tst.l d6                                           ; +$0114E: 4A86
    beq.w L_BOBS_01452                                 ; +$01150: 67000300
    andi.l #$00000001,d6                               ; +$01154: 028600000001
    bne.w L_BOBS_01452                                 ; +$0115A: 660002F6
    move.l a1,d6                                       ; +$0115E: 2C09
    tst.l d6                                           ; +$01160: 4A86
    beq.w L_BOBS_01452                                 ; +$01162: 670002EE
    andi.l #$00000001,d6                               ; +$01166: 028600000001
    bne.w L_BOBS_01452                                 ; +$0116C: 660002E4
    cmpi.l #$FFFF8000,d0                               ; +$01170: 0C80FFFF8000
    blt.w L_BOBS_01452                                 ; +$01176: 6D0002DA
    cmpi.l #$00007FFF,d0                               ; +$0117A: 0C8000007FFF
    bgt.w L_BOBS_01452                                 ; +$01180: 6E0002D0
    cmpi.l #$FFFF8000,d1                               ; +$01184: 0C81FFFF8000
    blt.w L_BOBS_01452                                 ; +$0118A: 6D0002C6
    cmpi.l #$00007FFF,d1                               ; +$0118E: 0C8100007FFF
    bgt.w L_BOBS_01452                                 ; +$01194: 6E0002BC
    cmpi.l #$00000001,d3                               ; +$01198: 0C8300000001
    bgt.w L_BOBS_01452                                 ; +$0119E: 6E0002B2
    tst.l d3                                           ; +$011A2: 4A83
    bmi.w L_BOBS_01452                                 ; +$011A4: 6B0002AC
    tst.l d4                                           ; +$011A8: 4A84
    ble.w L_BOBS_01452                                 ; +$011AA: 6F0002A6
    cmpi.l #$00001000,d4                               ; +$011AE: 0C8400001000
    bgt.w L_BOBS_01452                                 ; +$011B4: 6E00029C
    tst.l d5                                           ; +$011B8: 4A85
    ble.w L_BOBS_01452                                 ; +$011BA: 6F000296
    cmpi.l #$00001000,d5                               ; +$011BE: 0C8500001000
    bgt.w L_BOBS_01452                                 ; +$011C4: 6E00028C
    tst.l d2                                           ; +$011C8: 4A82
    ble.w L_BOBS_01452                                 ; +$011CA: 6F000286
    cmpi.l #$0000FFFF,d2                               ; +$011CE: 0C820000FFFF
    bgt.w L_BOBS_01452                                 ; +$011D4: 6E00027C
    move.l d2,d6                                       ; +$011D8: 2C02
    andi.l #$00000001,d6                               ; +$011DA: 028600000001
    bne.w L_BOBS_01452                                 ; +$011E0: 66000270
    move.l d4,d6                                       ; +$011E4: 2C04
    addi.l #$0000000F,d6                               ; +$011E6: 06860000000F
    lsr.l #4,d6                                        ; +$011EC: E88E
    lsl.l #1,d6                                        ; +$011EE: E38E
    cmp.l d6,d2                                        ; +$011F0: B486
    bcs.w L_BOBS_01452                                 ; +$011F2: 6500025E
    movea.l a1,a4                                      ; +$011F6: 2849
    move.l #$00000008,d6                               ; +$011F8: 2C3C00000008
L_BOBS_011FE:
    move.l (a4)+,d7                                    ; +$011FE: 2E1C
    tst.l d7                                           ; +$01200: 4A87
    beq.w L_BOBS_01452                                 ; +$01202: 6700024E
    cmpi.l #$FFFFFFFF,d7                               ; +$01206: 0C87FFFFFFFF
    beq.w L_BOBS_01452                                 ; +$0120C: 67000244
    andi.l #$00000001,d7                               ; +$01210: 028700000001
    bne.w L_BOBS_01452                                 ; +$01216: 6600023A
    subq.l #1,d6                                       ; +$0121A: 5386
    bne.w L_BOBS_011FE                                 ; +$0121C: 6600FFE0
    move.l d0,d6                                       ; +$01220: 2C00
    addi.l #$00000010,d6                               ; +$01222: 068600000010
    tst.l d6                                           ; +$01228: 4A86
    ble.w L_BOBS_01448                                 ; +$0122A: 6F00021C
    cmp.l d4,d0                                        ; +$0122E: B084
    bge.w L_BOBS_01448                                 ; +$01230: 6C000216
    move.l d0,d6                                       ; +$01234: 2C00
    asr.l #4,d6                                        ; +$01236: E886
    move.l d6,32(a2)                                   ; +$01238: 25460020
    move.l d0,d6                                       ; +$0123C: 2C00
    andi.l #$0000000F,d6                               ; +$0123E: 02860000000F
    move.l d6,24(a2)                                   ; +$01244: 25460018
    move.l #$00000010,d7                               ; +$01248: 2E3C00000010
    sub.l d6,d7                                        ; +$0124E: 9E86
    move.l d7,28(a2)                                   ; +$01250: 2547001C
    move.l d4,d6                                       ; +$01254: 2C04
    subq.l #1,d6                                       ; +$01256: 5386
    lsr.l #4,d6                                        ; +$01258: E88E
    move.l d6,36(a2)                                   ; +$0125A: 25460024
    move.l #$0000FFFF,d6                               ; +$0125E: 2C3C0000FFFF
    move.l d4,d7                                       ; +$01264: 2E04
    andi.l #$0000000F,d7                               ; +$01266: 02870000000F
    tst.l d7                                           ; +$0126C: 4A87
    beq.w L_BOBS_01282                                 ; +$0126E: 67000012
    move.l #$00000010,d0                               ; +$01272: 203C00000010
    sub.l d7,d0                                        ; +$01278: 9087
L_BOBS_0127A:
    lsl.w #1,d6                                        ; +$0127A: E34E
    subq.l #1,d0                                       ; +$0127C: 5380
    bne.w L_BOBS_0127A                                 ; +$0127E: 6600FFFA
L_BOBS_01282:
    move.w d6,40(a2)                                   ; +$01282: 35460028
    movea.l a0,a6                                      ; +$01286: 2C48
    move.l #$00000000,d2                               ; +$01288: 243C00000000
L_BOBS_0128E:
    move.l 4(a2),d7                                    ; +$0128E: 2E2A0004
    add.l d2,d7                                        ; +$01292: DE82
    tst.l d7                                           ; +$01294: 4A87
    bmi.w L_BOBS_01438                                 ; +$01296: 6B0001A0
    cmp.l 16(a2),d7                                    ; +$0129A: BEAA0010
    bge.w L_BOBS_01438                                 ; +$0129E: 6C000198
    move.l 8(a2),d6                                    ; +$012A2: 2C2A0008
    mulu.w d6,d7                                       ; +$012A6: CEC6
    move.l 32(a2),d6                                   ; +$012A8: 2C2A0020
    lsl.l #1,d6                                        ; +$012AC: E38E
    add.l d6,d7                                        ; +$012AE: DE86
    move.l d7,44(a2)                                   ; +$012B0: 2547002C
    addq.l #2,d7                                       ; +$012B4: 5487
    move.l d7,48(a2)                                   ; +$012B6: 25470030
    move.w (a6)+,d4                                    ; +$012BA: 381E
    tst.l 20(a2)                                       ; +$012BC: 4AAA0014
    beq.w L_BOBS_012CA                                 ; +$012C0: 67000008
    not.w d4                                           ; +$012C4: 4644
    bra.w L_BOBS_012CE                                 ; +$012C6: 60000006
L_BOBS_012CA:
    move.w #$FFFF,d4                                   ; +$012CA: 383CFFFF
L_BOBS_012CE:
    move.l (a2),d6                                     ; +$012CE: 2C12
    tst.l d6                                           ; +$012D0: 4A86
    bmi.w L_BOBS_0134E                                 ; +$012D2: 6B00007A
    addi.l #$00000010,d6                               ; +$012D6: 068600000010
    cmp.l 12(a2),d6                                    ; +$012DC: BCAA000C
    bgt.w L_BOBS_0134E                                 ; +$012E0: 6E00006C
    tst.w d4                                           ; +$012E4: 4A44
    beq.w L_BOBS_01430                                 ; +$012E6: 67000148
    move.l (a2),d6                                     ; +$012EA: 2C12
    andi.l #$0000000F,d6                               ; +$012EC: 02860000000F
    lsr.l #3,d6                                        ; +$012F2: E68E
    move.l d6,60(a2)                                   ; +$012F4: 2546003C
    move.l (a2),d6                                     ; +$012F8: 2C12
    andi.l #$00000007,d6                               ; +$012FA: 028600000007
    move.l d6,64(a2)                                   ; +$01300: 25460040
    movea.l a1,a5                                      ; +$01304: 2A49
    move.l #$00000008,d1                               ; +$01306: 223C00000008
L_BOBS_0130C:
    move.w (a6)+,d5                                    ; +$0130C: 3A1E
    movea.l (a5)+,a0                                   ; +$0130E: 205D
    movea.l a0,a4                                      ; +$01310: 2848
    move.l 44(a2),d7                                   ; +$01312: 2E2A002C
    adda.l d7,a4                                       ; +$01316: D9C7
    move.l 60(a2),d7                                   ; +$01318: 2E2A003C
    adda.l d7,a4                                       ; +$0131C: D9C7
    move.l 64(a2),d7                                   ; +$0131E: 2E2A0040
    tst.l 20(a2)                                       ; +$01322: 4AAA0014
    beq.w L_BOBS_01340                                 ; +$01326: 67000018
    bfextu (a4){d7:16},d0                              ; +$0132A: E9D409D0
    move.w d4,d6                                       ; +$0132E: 3C04
    not.w d6                                           ; +$01330: 4646
    and.w d6,d0                                        ; +$01332: C046
    and.w d4,d5                                        ; +$01334: CA44
    or.w d5,d0                                         ; +$01336: 8045
    bfins d0,(a4){d7:16}                               ; +$01338: EFD409D0
    bra.w L_BOBS_01344                                 ; +$0133C: 60000006
L_BOBS_01340:
    bfins d5,(a4){d7:16}                               ; +$01340: EFD459D0
L_BOBS_01344:
    subq.l #1,d1                                       ; +$01344: 5381
    bne.w L_BOBS_0130C                                 ; +$01346: 6600FFC4
    bra.w L_BOBS_0143C                                 ; +$0134A: 600000F0
L_BOBS_0134E:
    move.w d4,d5                                       ; +$0134E: 3A04
    move.l 24(a2),d7                                   ; +$01350: 2E2A0018
    lsr.w d7,d5                                        ; +$01354: EE6D
    move.w d5,52(a2)                                   ; +$01356: 35450034
    move.w d4,d5                                       ; +$0135A: 3A04
    move.l 28(a2),d7                                   ; +$0135C: 2E2A001C
    lsl.w d7,d5                                        ; +$01360: EF6D
    move.w d5,56(a2)                                   ; +$01362: 35450038
    move.l 32(a2),d6                                   ; +$01366: 2C2A0020
    tst.l d6                                           ; +$0136A: 4A86
    bmi.w L_BOBS_0138C                                 ; +$0136C: 6B00001E
    cmp.l 36(a2),d6                                    ; +$01370: BCAA0024
    bgt.w L_BOBS_0138C                                 ; +$01374: 6E000016
    bne.w L_BOBS_01394                                 ; +$01378: 6600001A
    move.w 52(a2),d7                                   ; +$0137C: 3E2A0034
    and.w 40(a2),d7                                    ; +$01380: CE6A0028
    move.w d7,52(a2)                                   ; +$01384: 35470034
    bra.w L_BOBS_01394                                 ; +$01388: 6000000A
L_BOBS_0138C:
    move.l #$00000000,52(a2)                           ; +$0138C: 257C000000000034
L_BOBS_01394:
    addq.l #1,d6                                       ; +$01394: 5286
    tst.l d6                                           ; +$01396: 4A86
    bmi.w L_BOBS_013B8                                 ; +$01398: 6B00001E
    cmp.l 36(a2),d6                                    ; +$0139C: BCAA0024
    bgt.w L_BOBS_013B8                                 ; +$013A0: 6E000016
    bne.w L_BOBS_013C0                                 ; +$013A4: 6600001A
    move.w 56(a2),d7                                   ; +$013A8: 3E2A0038
    and.w 40(a2),d7                                    ; +$013AC: CE6A0028
    move.w d7,56(a2)                                   ; +$013B0: 35470038
    bra.w L_BOBS_013C0                                 ; +$013B4: 6000000A
L_BOBS_013B8:
    move.l #$00000000,56(a2)                           ; +$013B8: 257C000000000038
L_BOBS_013C0:
    move.w 52(a2),d6                                   ; +$013C0: 3C2A0034
    or.w 56(a2),d6                                     ; +$013C4: 8C6A0038
    tst.w d6                                           ; +$013C8: 4A46
    beq.w L_BOBS_01430                                 ; +$013CA: 67000064
    movea.l a1,a5                                      ; +$013CE: 2A49
    move.l #$00000008,d1                               ; +$013D0: 223C00000008
L_BOBS_013D6:
    move.w (a6)+,d5                                    ; +$013D6: 3A1E
    movea.l (a5)+,a0                                   ; +$013D8: 205D
    move.w 52(a2),d6                                   ; +$013DA: 3C2A0034
    tst.w d6                                           ; +$013DE: 4A46
    beq.w L_BOBS_01400                                 ; +$013E0: 6700001E
    move.w d5,d0                                       ; +$013E4: 3005
    move.l 24(a2),d7                                   ; +$013E6: 2E2A0018
    lsr.w d7,d0                                        ; +$013EA: EE68
    and.w d6,d0                                        ; +$013EC: C046
    not.w d6                                           ; +$013EE: 4646
    movea.l a0,a4                                      ; +$013F0: 2848
    move.l 44(a2),d7                                   ; +$013F2: 2E2A002C
    adda.l d7,a4                                       ; +$013F6: D9C7
    move.w (a4),d4                                     ; +$013F8: 3814
    and.w d6,d4                                        ; +$013FA: C846
    or.w d0,d4                                         ; +$013FC: 8840
    move.w d4,(a4)                                     ; +$013FE: 3884
L_BOBS_01400:
    move.w 56(a2),d6                                   ; +$01400: 3C2A0038
    tst.w d6                                           ; +$01404: 4A46
    beq.w L_BOBS_01426                                 ; +$01406: 6700001E
    move.w d5,d0                                       ; +$0140A: 3005
    move.l 28(a2),d7                                   ; +$0140C: 2E2A001C
    lsl.w d7,d0                                        ; +$01410: EF68
    and.w d6,d0                                        ; +$01412: C046
    not.w d6                                           ; +$01414: 4646
    movea.l a0,a4                                      ; +$01416: 2848
    move.l 48(a2),d7                                   ; +$01418: 2E2A0030
    adda.l d7,a4                                       ; +$0141C: D9C7
    move.w (a4),d4                                     ; +$0141E: 3814
    and.w d6,d4                                        ; +$01420: C846
    or.w d0,d4                                         ; +$01422: 8840
    move.w d4,(a4)                                     ; +$01424: 3884
L_BOBS_01426:
    subq.l #1,d1                                       ; +$01426: 5381
    bne.w L_BOBS_013D6                                 ; +$01428: 6600FFAC
    bra.w L_BOBS_0143C                                 ; +$0142C: 6000000E
L_BOBS_01430:
    lea 16(a6),a6                                      ; +$01430: 4DEE0010
    bra.w L_BOBS_0143C                                 ; +$01434: 60000006
L_BOBS_01438:
    lea 18(a6),a6                                      ; +$01438: 4DEE0012
L_BOBS_0143C:
    addq.l #1,d2                                       ; +$0143C: 5282
    cmpi.l #$00000010,d2                               ; +$0143E: 0C8200000010
    bne.w L_BOBS_0128E                                 ; +$01444: 6600FE48
L_BOBS_01448:
    move.l #$00000001,d3                               ; +$01448: 263C00000001
    bra.w L_BOBS_01458                                 ; +$0144E: 60000008
L_BOBS_01452:
    move.l #$00000000,d3                               ; +$01452: 263C00000000
L_BOBS_01458:
    lea 96(a7),a7                                      ; +$01458: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0145C: 4CDF77F7
    moveq #0,d2                                        ; +$01460: 7400
    rts                                                ; +$01462: 4E75
ENTRY_BOBS_01464:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$01464: 48E7EFEE
    lea -96(a7),a7                                     ; +$01468: 4FEFFFA0
    movea.l a7,a2                                      ; +$0146C: 244F
    move.l d3,(a2)                                     ; +$0146E: 2483
    move.l (a3)+,d7                                    ; +$01470: 2E1B
    move.l d7,4(a2)                                    ; +$01472: 25470004
    move.l (a3)+,d7                                    ; +$01476: 2E1B
    move.l d7,8(a2)                                    ; +$01478: 25470008
    move.l (a3)+,d7                                    ; +$0147C: 2E1B
    move.l d7,12(a2)                                   ; +$0147E: 2547000C
    move.l #$00000000,d3                               ; +$01482: 263C00000000
    move.l (a2),d0                                     ; +$01488: 2012
    tst.l d0                                           ; +$0148A: 4A80
    bmi.w L_BOBS_0186E                                 ; +$0148C: 6B0003E0
    cmpi.l #$00000001,d0                               ; +$01490: 0C8000000001
    bgt.w L_BOBS_0186E                                 ; +$01496: 6E0003D6
    move.l 8(a2),d0                                    ; +$0149A: 202A0008
    cmpi.l #$FFFF8000,d0                               ; +$0149E: 0C80FFFF8000
    blt.w L_BOBS_0186E                                 ; +$014A4: 6D0003C8
    cmpi.l #$00007FFF,d0                               ; +$014A8: 0C8000007FFF
    bgt.w L_BOBS_0186E                                 ; +$014AE: 6E0003BE
    move.l 4(a2),d0                                    ; +$014B2: 202A0004
    cmpi.l #$FFFF8000,d0                               ; +$014B6: 0C80FFFF8000
    blt.w L_BOBS_0186E                                 ; +$014BC: 6D0003B0
    cmpi.l #$00007FFF,d0                               ; +$014C0: 0C8000007FFF
    bgt.w L_BOBS_0186E                                 ; +$014C6: 6E0003A6
    move.l 12(a2),d0                                   ; +$014CA: 202A000C
    cmpi.l #$00000005,d0                               ; +$014CE: 0C8000000005
    bcs.w L_BOBS_0186E                                 ; +$014D4: 65000398
    cmpi.l #$0000FFFF,d0                               ; +$014D8: 0C800000FFFF
    bhi.w L_BOBS_0186E                                 ; +$014DE: 6200038E
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$014E2: FE11F700031D
    move.l a0,d5                                       ; +$014E8: 2A08
    cmpi.l #$00000018,d5                               ; +$014EA: 0C8500000018
    bls.w L_BOBS_0186E                                 ; +$014F0: 6300037C
    move.l d5,d0                                       ; +$014F4: 2005
    andi.l #$00000001,d0                               ; +$014F6: 028000000001
    bne.w L_BOBS_0186E                                 ; +$014FC: 66000370
    move.l d5,16(a2)                                   ; +$01500: 25450010
    movea.l d5,a1                                      ; +$01504: 2245
    movea.l $0004.w,a6                                 ; +$01506: 2C780004
    jsr -534(a6)                                       ; +$0150A: 4EAEFDEA
    tst.l d0                                           ; +$0150E: 4A80
    beq.w L_BOBS_0186E                                 ; +$01510: 6700035C
    move.l 16(a2),d5                                   ; +$01514: 2A2A0010
    move.l d5,d0                                       ; +$01518: 2005
    subi.l #$00000018,d0                               ; +$0151A: 048000000018
    movea.l d0,a1                                      ; +$01520: 2240
    movea.l $0004.w,a6                                 ; +$01522: 2C780004
    jsr -534(a6)                                       ; +$01526: 4EAEFDEA
    tst.l d0                                           ; +$0152A: 4A80
    beq.w L_BOBS_0186E                                 ; +$0152C: 67000340
    movea.l d5,a0                                      ; +$01530: 2045
    move.l -20(a0),d4                                  ; +$01532: 2828FFEC
    cmpi.l #$00000178,d4                               ; +$01536: 0C8400000178
    bne.w L_BOBS_0186E                                 ; +$0153C: 66000330
    subi.l #$00000010,d4                               ; +$01540: 048400000010
    move.l d4,20(a2)                                   ; +$01546: 25440014
    move.l d5,d0                                       ; +$0154A: 2005
    add.l d4,d0                                        ; +$0154C: D084
    bcs.w L_BOBS_0186E                                 ; +$0154E: 6500031E
    subq.l #1,d0                                       ; +$01552: 5380
    movea.l d0,a1                                      ; +$01554: 2240
    movea.l $0004.w,a6                                 ; +$01556: 2C780004
    jsr -534(a6)                                       ; +$0155A: 4EAEFDEA
    tst.l d0                                           ; +$0155E: 4A80
    beq.w L_BOBS_0186E                                 ; +$01560: 6700030C
    move.l 16(a2),d5                                   ; +$01564: 2A2A0010
    movea.l d5,a0                                      ; +$01568: 2045
    move.l -16(a0),d0                                  ; +$0156A: 2028FFF0
    move.l 12(a2),d1                                   ; +$0156E: 222A000C
    cmp.l d1,d0                                        ; +$01572: B081
    bne.w L_BOBS_0186E                                 ; +$01574: 660002F8
    move.l #$00000000,d0                               ; +$01578: 203C00000000
    move.w -12(a0),d0                                  ; +$0157E: 3028FFF4
    tst.l d0                                           ; +$01582: 4A80
    beq.w L_BOBS_01594                                 ; +$01584: 6700000E
    andi.w #$FFFD,d0                                   ; +$01588: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$0158C: 0C400001
    bne.w L_BOBS_0186E                                 ; +$01590: 660002DC
L_BOBS_01594:
    move.l -8(a0),d0                                   ; +$01594: 2028FFF8
    cmpi.l #$41475043,d0                               ; +$01598: 0C8041475043
    bne.w L_BOBS_0186E                                 ; +$0159E: 660002CE
    move.l -4(a0),d0                                   ; +$015A2: 2028FFFC
    cmpi.l #$41434845,d0                               ; +$015A6: 0C8041434845
    bne.w L_BOBS_0186E                                 ; +$015AC: 660002C0
    move.l (a0),d0                                     ; +$015B0: 2010
    cmpi.l #$41475043,d0                               ; +$015B2: 0C8041475043
    bne.w L_BOBS_0186E                                 ; +$015B8: 660002B4
    move.l #$00000000,d0                               ; +$015BC: 203C00000000
    move.w 4(a0),d0                                    ; +$015C2: 30280004
    cmpi.l #$00000001,d0                               ; +$015C6: 0C8000000001
    bne.w L_BOBS_0186E                                 ; +$015CC: 660002A0
    move.l #$00000000,d0                               ; +$015D0: 203C00000000
    move.w 6(a0),d0                                    ; +$015D6: 30280006
    cmpi.l #$00000003,d0                               ; +$015DA: 0C8000000003
    bne.w L_BOBS_0186E                                 ; +$015E0: 6600028C
    move.l #$00000000,d0                               ; +$015E4: 203C00000000
    move.w 8(a0),d0                                    ; +$015EA: 30280008
    cmpi.l #$00000010,d0                               ; +$015EE: 0C8000000010
    bne.w L_BOBS_0186E                                 ; +$015F4: 66000278
    move.l #$00000000,d0                               ; +$015F8: 203C00000000
    move.w 10(a0),d0                                   ; +$015FE: 3028000A
    cmpi.l #$00000010,d0                               ; +$01602: 0C8000000010
    bne.w L_BOBS_0186E                                 ; +$01608: 66000264
    move.l #$00000000,d0                               ; +$0160C: 203C00000000
    move.w 12(a0),d0                                   ; +$01612: 3028000C
    cmpi.l #$00000008,d0                               ; +$01616: 0C8000000008
    bne.w L_BOBS_0186E                                 ; +$0161C: 66000250
    move.l #$00000000,d0                               ; +$01620: 203C00000000
    move.w 14(a0),d0                                   ; +$01626: 3028000E
    cmpi.l #$00000002,d0                               ; +$0162A: 0C8000000002
    bne.w L_BOBS_0186E                                 ; +$01630: 6600023C
    move.l 20(a0),d0                                   ; +$01634: 20280014
    cmpi.l #$00000048,d0                               ; +$01638: 0C8000000048
    bne.w L_BOBS_0186E                                 ; +$0163E: 6600022E
    move.l 24(a0),d0                                   ; +$01642: 20280018
    cmpi.l #$00000068,d0                               ; +$01646: 0C8000000068
    bne.w L_BOBS_0186E                                 ; +$0164C: 66000220
    move.l 28(a0),d0                                   ; +$01650: 2028001C
    cmpi.l #$00000168,d0                               ; +$01654: 0C8000000168
    bne.w L_BOBS_0186E                                 ; +$0165A: 66000212
    move.l 32(a0),d0                                   ; +$0165E: 20280020
    tst.l d0                                           ; +$01662: 4A80
    beq.w L_BOBS_0186E                                 ; +$01664: 67000208
    tst.l 36(a0)                                       ; +$01668: 4AA80024
    bne.w L_BOBS_0186E                                 ; +$0166C: 66000200
    move.l d5,d0                                       ; +$01670: 2005
    addi.l #$00000048,d0                               ; +$01672: 068000000048
    bcs.w L_BOBS_0186E                                 ; +$01678: 650001F4
    move.l d0,24(a2)                                   ; +$0167C: 25400018
    movea.l 456(a5),a4                                 ; +$01680: 286D01C8
    move.l a4,d0                                       ; +$01684: 200C
    tst.l d0                                           ; +$01686: 4A80
    beq.w L_BOBS_0186E                                 ; +$01688: 670001E4
    move.l (a4),d0                                     ; +$0168C: 2014
    tst.l d0                                           ; +$0168E: 4A80
    beq.w L_BOBS_0186E                                 ; +$01690: 670001DC
    move.l 8(a4),d0                                    ; +$01694: 202C0008
    tst.l d0                                           ; +$01698: 4A80
    beq.w L_BOBS_0186E                                 ; +$0169A: 670001D2
    move.l 32(a4),d0                                   ; +$0169E: 202C0020
    tst.l d0                                           ; +$016A2: 4A80
    beq.w L_BOBS_0186E                                 ; +$016A4: 670001C8
    move.l 12(a4),d0                                   ; +$016A8: 202C000C
    tst.l d0                                           ; +$016AC: 4A80
    ble.w L_BOBS_0186E                                 ; +$016AE: 6F0001BE
    cmpi.l #$00007FFF,d0                               ; +$016B2: 0C8000007FFF
    bgt.w L_BOBS_0186E                                 ; +$016B8: 6E0001B4
    move.l d0,28(a2)                                   ; +$016BC: 2540001C
    move.l 16(a4),d0                                   ; +$016C0: 202C0010
    tst.l d0                                           ; +$016C4: 4A80
    ble.w L_BOBS_0186E                                 ; +$016C6: 6F0001A6
    cmpi.l #$00007FFF,d0                               ; +$016CA: 0C8000007FFF
    bgt.w L_BOBS_0186E                                 ; +$016D0: 6E00019C
    move.l d0,32(a2)                                   ; +$016D4: 25400020
    move.l 28(a4),d0                                   ; +$016D8: 202C001C
    cmpi.l #$00000008,d0                               ; +$016DC: 0C8000000008
    bne.w L_BOBS_0186E                                 ; +$016E2: 6600018A
    movea.l 16(a2),a0                                  ; +$016E6: 206A0010
    move.l 16(a0),d6                                   ; +$016EA: 2C280010
    cmpi.l #$FFFFFFFF,d6                               ; +$016EE: 0C86FFFFFFFF
    bne.w L_BOBS_016FC                                 ; +$016F4: 66000006
    bra.w L_BOBS_01724                                 ; +$016F8: 6000002A
L_BOBS_016FC:
    move.l (a4),d0                                     ; +$016FC: 2014
    addi.l #$0000002C,d0                               ; +$016FE: 06800000002C
    movea.l d0,a0                                      ; +$01704: 2040
    movea.l 8(a4),a6                                   ; +$01706: 2C6C0008
    jsr -792(a6)                                       ; +$0170A: 4EAEFCE8
    cmpi.l #$FFFFFFFF,d0                               ; +$0170E: 0C80FFFFFFFF
    beq.w L_BOBS_0186E                                 ; +$01714: 67000158
    movea.l 16(a2),a0                                  ; +$01718: 206A0010
    cmp.l 16(a0),d0                                    ; +$0171C: B0A80010
    bne.w L_BOBS_0186E                                 ; +$01720: 6600014C
L_BOBS_01724:
    movea.l 32(a4),a0                                  ; +$01724: 206C0020
    move.l 8(a0),d0                                    ; +$01728: 20280008
    tst.l d0                                           ; +$0172C: 4A80
    beq.w L_BOBS_01746                                 ; +$0172E: 67000016
    cmpi.l #$00000001,d0                               ; +$01732: 0C8000000001
    bne.w L_BOBS_0186E                                 ; +$01738: 66000134
    movea.l 32(a4),a0                                  ; +$0173C: 206C0020
    movea.l (a0),a1                                    ; +$01740: 2250
    bra.w L_BOBS_0174E                                 ; +$01742: 6000000A
L_BOBS_01746:
    movea.l 32(a4),a0                                  ; +$01746: 206C0020
    movea.l 4(a0),a1                                   ; +$0174A: 22680004
L_BOBS_0174E:
    move.l a1,d0                                       ; +$0174E: 2009
    tst.l d0                                           ; +$01750: 4A80
    beq.w L_BOBS_0186E                                 ; +$01752: 6700011A
    movea.l (a1),a0                                    ; +$01756: 2051
    move.l a0,d0                                       ; +$01758: 2008
    tst.l d0                                           ; +$0175A: 4A80
    beq.w L_BOBS_0186E                                 ; +$0175C: 67000110
    move.l a0,36(a2)                                   ; +$01760: 25480024
    move.l #$00000000,d1                               ; +$01764: 223C00000000
    move.w (a0),d1                                     ; +$0176A: 3210
    tst.l d1                                           ; +$0176C: 4A81
    beq.w L_BOBS_0186E                                 ; +$0176E: 670000FE
    lsl.l #3,d1                                        ; +$01772: E789
    cmp.l 28(a2),d1                                    ; +$01774: B2AA001C
    blt.w L_BOBS_0186E                                 ; +$01778: 6D0000F4
    move.l #$00000000,d1                               ; +$0177C: 223C00000000
    move.w 2(a0),d1                                    ; +$01782: 32280002
    cmp.l 32(a2),d1                                    ; +$01786: B2AA0020
    blt.w L_BOBS_0186E                                 ; +$0178A: 6D0000E2
    move.l #$00000000,d1                               ; +$0178E: 223C00000000
    move.b 5(a0),d1                                    ; +$01794: 12280005
    cmpi.l #$00000008,d1                               ; +$01798: 0C8100000008
    bne.w L_BOBS_0186E                                 ; +$0179E: 660000CE
    movea.l a0,a1                                      ; +$017A2: 2248
    addq.l #8,a1                                       ; +$017A4: 5089
    move.l #$00000008,d0                               ; +$017A6: 203C00000008
L_BOBS_017AC:
    move.l (a1)+,d1                                    ; +$017AC: 2219
    tst.l d1                                           ; +$017AE: 4A81
    beq.w L_BOBS_0186E                                 ; +$017B0: 670000BC
    cmpi.l #$FFFFFFFF,d1                               ; +$017B4: 0C81FFFFFFFF
    beq.w L_BOBS_0186E                                 ; +$017BA: 670000B2
    move.l d1,d5                                       ; +$017BE: 2A01
    andi.l #$00000001,d5                               ; +$017C0: 028500000001
    bne.w L_BOBS_0186E                                 ; +$017C6: 660000A6
    subq.l #1,d0                                       ; +$017CA: 5380
    bne.w L_BOBS_017AC                                 ; +$017CC: 6600FFDE
    move.l 8(a2),d0                                    ; +$017D0: 202A0008
    cmp.l 28(a2),d0                                    ; +$017D4: B0AA001C
    bge.w L_BOBS_01864                                 ; +$017D8: 6C00008A
    addi.l #$00000010,d0                               ; +$017DC: 068000000010
    tst.l d0                                           ; +$017E2: 4A80
    ble.w L_BOBS_01864                                 ; +$017E4: 6F00007E
    move.l 4(a2),d0                                    ; +$017E8: 202A0004
    cmp.l 32(a2),d0                                    ; +$017EC: B0AA0020
    bge.w L_BOBS_01864                                 ; +$017F0: 6C000072
    addi.l #$00000010,d0                               ; +$017F4: 068000000010
    tst.l d0                                           ; +$017FA: 4A80
    ble.w L_BOBS_01864                                 ; +$017FC: 6F000066
    movea.l 32(a4),a0                                  ; +$01800: 206C0020
    move.l 20(a0),d0                                   ; +$01804: 20280014
    andi.l #$00000001,d0                               ; +$01808: 028000000001
    beq.w L_BOBS_0183E                                 ; +$0180E: 6700002E
    movea.l 12(a0),a0                                  ; +$01812: 2068000C
    move.l a0,d0                                       ; +$01816: 2008
    tst.l d0                                           ; +$01818: 4A80
    beq.w L_BOBS_0186E                                 ; +$0181A: 67000052
    movea.l $0004.w,a6                                 ; +$0181E: 2C780004
    jsr -372(a6)                                       ; +$01822: 4EAEFE8C
    tst.l d0                                           ; +$01826: 4A80
    beq.w L_BOBS_0186E                                 ; +$01828: 67000044
    movea.l 32(a4),a0                                  ; +$0182C: 206C0020
    move.l 20(a0),d0                                   ; +$01830: 20280014
    andi.l #$FFFFFFFE,d0                               ; +$01834: 0280FFFFFFFE
    move.l d0,20(a0)                                   ; +$0183A: 21400014
L_BOBS_0183E:
    move.l 8(a2),d0                                    ; +$0183E: 202A0008
    move.l 4(a2),d1                                    ; +$01842: 222A0004
    move.l (a2),d3                                     ; +$01846: 2612
    move.l 28(a2),d4                                   ; +$01848: 282A001C
    move.l 32(a2),d5                                   ; +$0184C: 2A2A0020
    movea.l 24(a2),a0                                  ; +$01850: 206A0018
    movea.l 36(a2),a1                                  ; +$01854: 226A0024
    movea.l 8(a4),a6                                   ; +$01858: 2C6C0008
    bsr.w L_BOBS_01880                                 ; +$0185C: 61000022
    bra.w L_BOBS_01874                                 ; +$01860: 60000012
L_BOBS_01864:
    move.l #$00000001,d3                               ; +$01864: 263C00000001
    bra.w L_BOBS_01874                                 ; +$0186A: 60000008
L_BOBS_0186E:
    move.l #$00000000,d3                               ; +$0186E: 263C00000000
L_BOBS_01874:
    lea 96(a7),a7                                      ; +$01874: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$01878: 4CDF77F7
    moveq #0,d2                                        ; +$0187C: 7400
    rts                                                ; +$0187E: 4E75
L_BOBS_01880:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$01880: 48E7EFEE
    lea -256(a7),a7                                    ; +$01884: 4FEFFF00
    movea.l a7,a4                                      ; +$01888: 284F
    move.l a0,192(a4)                                  ; +$0188A: 294800C0
    move.l a1,196(a4)                                  ; +$0188E: 294900C4
    move.l a6,244(a4)                                  ; +$01892: 294E00F4
    move.l d0,200(a4)                                  ; +$01896: 294000C8
    move.l d1,204(a4)                                  ; +$0189A: 294100CC
    move.l d3,208(a4)                                  ; +$0189E: 294300D0
    move.l d4,212(a4)                                  ; +$018A2: 294400D4
    move.l d5,216(a4)                                  ; +$018A6: 294500D8
    move.l 192(a4),d6                                  ; +$018AA: 2C2C00C0
    tst.l d6                                           ; +$018AE: 4A86
    beq.w L_BOBS_01B6C                                 ; +$018B0: 670002BA
    andi.l #$00000001,d6                               ; +$018B4: 028600000001
    bne.w L_BOBS_01B6C                                 ; +$018BA: 660002B0
    move.l 196(a4),d6                                  ; +$018BE: 2C2C00C4
    tst.l d6                                           ; +$018C2: 4A86
    beq.w L_BOBS_01B6C                                 ; +$018C4: 670002A6
    andi.l #$00000001,d6                               ; +$018C8: 028600000001
    bne.w L_BOBS_01B6C                                 ; +$018CE: 6600029C
    move.l 244(a4),d6                                  ; +$018D2: 2C2C00F4
    tst.l d6                                           ; +$018D6: 4A86
    beq.w L_BOBS_01B6C                                 ; +$018D8: 67000292
    andi.l #$00000001,d6                               ; +$018DC: 028600000001
    bne.w L_BOBS_01B6C                                 ; +$018E2: 66000288
    move.l 200(a4),d6                                  ; +$018E6: 2C2C00C8
    cmpi.l #$FFFF8000,d6                               ; +$018EA: 0C86FFFF8000
    blt.w L_BOBS_01B6C                                 ; +$018F0: 6D00027A
    cmpi.l #$00007FFF,d6                               ; +$018F4: 0C8600007FFF
    bgt.w L_BOBS_01B6C                                 ; +$018FA: 6E000270
    move.l 204(a4),d6                                  ; +$018FE: 2C2C00CC
    cmpi.l #$FFFF8000,d6                               ; +$01902: 0C86FFFF8000
    blt.w L_BOBS_01B6C                                 ; +$01908: 6D000262
    cmpi.l #$00007FFF,d6                               ; +$0190C: 0C8600007FFF
    bgt.w L_BOBS_01B6C                                 ; +$01912: 6E000258
    move.l 208(a4),d6                                  ; +$01916: 2C2C00D0
    tst.l d6                                           ; +$0191A: 4A86
    bmi.w L_BOBS_01B6C                                 ; +$0191C: 6B00024E
    cmpi.l #$00000001,d6                               ; +$01920: 0C8600000001
    bgt.w L_BOBS_01B6C                                 ; +$01926: 6E000244
    move.l 212(a4),d6                                  ; +$0192A: 2C2C00D4
    tst.l d6                                           ; +$0192E: 4A86
    ble.w L_BOBS_01B6C                                 ; +$01930: 6F00023A
    cmpi.l #$00001000,d6                               ; +$01934: 0C8600001000
    bgt.w L_BOBS_01B6C                                 ; +$0193A: 6E000230
    move.l 216(a4),d6                                  ; +$0193E: 2C2C00D8
    tst.l d6                                           ; +$01942: 4A86
    ble.w L_BOBS_01B6C                                 ; +$01944: 6F000226
    cmpi.l #$00001000,d6                               ; +$01948: 0C8600001000
    bgt.w L_BOBS_01B6C                                 ; +$0194E: 6E00021C
    move.l 192(a4),d6                                  ; +$01952: 2C2C00C0
    addi.l #$0000011F,d6                               ; +$01956: 06860000011F
    bcs.w L_BOBS_01B6C                                 ; +$0195C: 6500020E
    movea.l 196(a4),a0                                 ; +$01960: 206C00C4
    move.l #$00000000,d6                               ; +$01964: 2C3C00000000
    move.w (a0),d6                                     ; +$0196A: 3C10
    lsl.l #3,d6                                        ; +$0196C: E78E
    cmp.l 212(a4),d6                                   ; +$0196E: BCAC00D4
    blt.w L_BOBS_01B6C                                 ; +$01972: 6D0001F8
    move.l #$00000000,d6                               ; +$01976: 2C3C00000000
    move.w 2(a0),d6                                    ; +$0197C: 3C280002
    cmp.l 216(a4),d6                                   ; +$01980: BCAC00D8
    blt.w L_BOBS_01B6C                                 ; +$01984: 6D0001E6
    move.l #$00000000,d6                               ; +$01988: 2C3C00000000
    move.b 5(a0),d6                                    ; +$0198E: 1C280005
    cmpi.l #$00000008,d6                               ; +$01992: 0C8600000008
    bne.w L_BOBS_01B6C                                 ; +$01998: 660001D2
    movea.l 196(a4),a1                                 ; +$0199C: 226C00C4
    addq.l #8,a1                                       ; +$019A0: 5089
    move.l #$00000008,d7                               ; +$019A2: 2E3C00000008
L_BOBS_019A8:
    move.l (a1)+,d6                                    ; +$019A8: 2C19
    tst.l d6                                           ; +$019AA: 4A86
    beq.w L_BOBS_01B6C                                 ; +$019AC: 670001BE
    cmpi.l #$FFFFFFFF,d6                               ; +$019B0: 0C86FFFFFFFF
    beq.w L_BOBS_01B6C                                 ; +$019B6: 670001B4
    andi.l #$00000001,d6                               ; +$019BA: 028600000001
    bne.w L_BOBS_01B6C                                 ; +$019C0: 660001AA
    subq.l #1,d7                                       ; +$019C4: 5387
    bne.w L_BOBS_019A8                                 ; +$019C6: 6600FFE0
    move.l 200(a4),d6                                  ; +$019CA: 2C2C00C8
    cmp.l 212(a4),d6                                   ; +$019CE: BCAC00D4
    bge.w L_BOBS_01B62                                 ; +$019D2: 6C00018E
    addi.l #$00000010,d6                               ; +$019D6: 068600000010
    tst.l d6                                           ; +$019DC: 4A86
    ble.w L_BOBS_01B62                                 ; +$019DE: 6F000182
    move.l 204(a4),d6                                  ; +$019E2: 2C2C00CC
    cmp.l 216(a4),d6                                   ; +$019E6: BCAC00D8
    bge.w L_BOBS_01B62                                 ; +$019EA: 6C000176
    addi.l #$00000010,d6                               ; +$019EE: 068600000010
    tst.l d6                                           ; +$019F4: 4A86
    ble.w L_BOBS_01B62                                 ; +$019F6: 6F00016A
    move.l 200(a4),d6                                  ; +$019FA: 2C2C00C8
    tst.l d6                                           ; +$019FE: 4A86
    bmi.w L_BOBS_01A14                                 ; +$01A00: 6B000012
    move.l #$00000000,220(a4)                          ; +$01A04: 297C0000000000DC
    move.l d6,228(a4)                                  ; +$01A0C: 294600E4
    bra.w L_BOBS_01A28                                 ; +$01A10: 60000016
L_BOBS_01A14:
    move.l #$00000000,228(a4)                          ; +$01A14: 297C0000000000E4
    move.l #$00000000,d7                               ; +$01A1C: 2E3C00000000
    sub.l d6,d7                                        ; +$01A22: 9E86
    move.l d7,220(a4)                                  ; +$01A24: 294700DC
L_BOBS_01A28:
    move.l #$00000010,d6                               ; +$01A28: 2C3C00000010
    sub.l 220(a4),d6                                   ; +$01A2E: 9CAC00DC
    move.l 212(a4),d7                                  ; +$01A32: 2E2C00D4
    sub.l 228(a4),d7                                   ; +$01A36: 9EAC00E4
    cmp.l d7,d6                                        ; +$01A3A: BC87
    blt.w L_BOBS_01A42                                 ; +$01A3C: 6D000004
    move.l d7,d6                                       ; +$01A40: 2C07
L_BOBS_01A42:
    tst.l d6                                           ; +$01A42: 4A86
    ble.w L_BOBS_01B62                                 ; +$01A44: 6F00011C
    move.l d6,236(a4)                                  ; +$01A48: 294600EC
    move.l 204(a4),d6                                  ; +$01A4C: 2C2C00CC
    tst.l d6                                           ; +$01A50: 4A86
    bmi.w L_BOBS_01A66                                 ; +$01A52: 6B000012
    move.l #$00000000,224(a4)                          ; +$01A56: 297C0000000000E0
    move.l d6,232(a4)                                  ; +$01A5E: 294600E8
    bra.w L_BOBS_01A7A                                 ; +$01A62: 60000016
L_BOBS_01A66:
    move.l #$00000000,232(a4)                          ; +$01A66: 297C0000000000E8
    move.l #$00000000,d7                               ; +$01A6E: 2E3C00000000
    sub.l d6,d7                                        ; +$01A74: 9E86
    move.l d7,224(a4)                                  ; +$01A76: 294700E0
L_BOBS_01A7A:
    move.l #$00000010,d6                               ; +$01A7A: 2C3C00000010
    sub.l 224(a4),d6                                   ; +$01A80: 9CAC00E0
    move.l 216(a4),d7                                  ; +$01A84: 2E2C00D8
    sub.l 232(a4),d7                                   ; +$01A88: 9EAC00E8
    cmp.l d7,d6                                        ; +$01A8C: BC87
    blt.w L_BOBS_01A94                                 ; +$01A8E: 6D000004
    move.l d7,d6                                       ; +$01A92: 2C07
L_BOBS_01A94:
    tst.l d6                                           ; +$01A94: 4A86
    ble.w L_BOBS_01B62                                 ; +$01A96: 6F0000CA
    move.l d6,240(a4)                                  ; +$01A9A: 294600F0
    movea.l $0004.w,a6                                 ; +$01A9E: 2C780004
    movea.l 192(a4),a1                                 ; +$01AA2: 226C00C0
    jsr -534(a6)                                       ; +$01AA6: 4EAEFDEA
    andi.l #$00000002,d0                               ; +$01AAA: 028000000002
    beq.w L_BOBS_01B6C                                 ; +$01AB0: 670000BA
    move.l 192(a4),d6                                  ; +$01AB4: 2C2C00C0
    addi.l #$0000011F,d6                               ; +$01AB8: 06860000011F
    movea.l d6,a1                                      ; +$01ABE: 2246
    jsr -534(a6)                                       ; +$01AC0: 4EAEFDEA
    andi.l #$00000002,d0                               ; +$01AC4: 028000000002
    beq.w L_BOBS_01B6C                                 ; +$01ACA: 670000A0
    move.w #$0002,(a4)                                 ; +$01ACE: 38BC0002
    move.w #$0010,2(a4)                                ; +$01AD2: 397C00100002
    move.l #$00000000,4(a4)                            ; +$01AD8: 297C000000000004
    move.b #$08,5(a4)                                  ; +$01AE0: 197C00080005
    movea.l 192(a4),a0                                 ; +$01AE6: 206C00C0
    lea 32(a0),a0                                      ; +$01AEA: 41E80020
    lea 8(a4),a1                                       ; +$01AEE: 43EC0008
    move.l #$00000008,d7                               ; +$01AF2: 2E3C00000008
L_BOBS_01AF8:
    move.l a0,(a1)+                                    ; +$01AF8: 22C8
    lea 32(a0),a0                                      ; +$01AFA: 41E80020
    subq.l #1,d7                                       ; +$01AFE: 5387
    bne.w L_BOBS_01AF8                                 ; +$01B00: 6600FFF6
    movea.l 244(a4),a6                                 ; +$01B04: 2C6C00F4
    lea 64(a4),a1                                      ; +$01B08: 43EC0040
    jsr -198(a6)                                       ; +$01B0C: 4EAEFF3A
    lea 64(a4),a1                                      ; +$01B10: 43EC0040
    move.l 196(a4),4(a1)                               ; +$01B14: 236C00C40004
    movea.l a4,a0                                      ; +$01B1A: 204C
    move.l 220(a4),d0                                  ; +$01B1C: 202C00DC
    move.l 224(a4),d1                                  ; +$01B20: 222C00E0
    move.l 228(a4),d2                                  ; +$01B24: 242C00E4
    move.l 232(a4),d3                                  ; +$01B28: 262C00E8
    move.l 236(a4),d4                                  ; +$01B2C: 282C00EC
    move.l 240(a4),d5                                  ; +$01B30: 2A2C00F0
    move.l 208(a4),d7                                  ; +$01B34: 2E2C00D0
    tst.l d7                                           ; +$01B38: 4A87
    beq.w L_BOBS_01B50                                 ; +$01B3A: 67000014
    move.l #$000000E0,d6                               ; +$01B3E: 2C3C000000E0
    movea.l 192(a4),a2                                 ; +$01B44: 246C00C0
    jsr -636(a6)                                       ; +$01B48: 4EAEFD84
    bra.w L_BOBS_01B5A                                 ; +$01B4C: 6000000C
L_BOBS_01B50:
    move.l #$000000C0,d6                               ; +$01B50: 2C3C000000C0
    jsr -606(a6)                                       ; +$01B56: 4EAEFDA2
L_BOBS_01B5A:
    movea.l 244(a4),a6                                 ; +$01B5A: 2C6C00F4
    jsr -228(a6)                                       ; +$01B5E: 4EAEFF1C
L_BOBS_01B62:
    move.l #$00000001,d3                               ; +$01B62: 263C00000001
    bra.w L_BOBS_01B72                                 ; +$01B68: 60000008
L_BOBS_01B6C:
    move.l #$00000000,d3                               ; +$01B6C: 263C00000000
L_BOBS_01B72:
    lea 256(a7),a7                                     ; +$01B72: 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$01B76: 4CDF77F7
    moveq #0,d2                                        ; +$01B7A: 7400
    rts                                                ; +$01B7C: 4E75
L_BOBS_01B7E:
bank_bank_select:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$01B7E: 48E7EFEE
    lea -64(a7),a7                                     ; +$01B82: 4FEFFFC0
    movea.l a7,a2                                      ; +$01B86: 244F
    move.l d3,(a2)                                     ; +$01B88: 2483
    move.l #$00000000,d3                               ; +$01B8A: 263C00000000
    movea.l $0004.w,a0                                 ; +$01B90: 20780004
    move.l a0,d0                                       ; +$01B94: 2008
    tst.l d0                                           ; +$01B96: 4A80
    beq.w L_BOBS_01D2C                                 ; +$01B98: 67000192
    move.w 296(a0),d0                                  ; +$01B9C: 30280128
    btst #1,d0                                         ; +$01BA0: 08000001
    beq.w L_BOBS_01D2C                                 ; +$01BA4: 67000186
    move.l (a2),d0                                     ; +$01BA8: 2012
    cmpi.l #$00000005,d0                               ; +$01BAA: 0C8000000005
    bcs.w L_BOBS_01D2C                                 ; +$01BB0: 6500017A
    cmpi.l #$0000FFFF,d0                               ; +$01BB4: 0C800000FFFF
    bhi.w L_BOBS_01D2C                                 ; +$01BBA: 62000170
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$01BBE: FE11F700031D
    move.l a0,d0                                       ; +$01BC4: 2008
    tst.l d0                                           ; +$01BC6: 4A80
    bne.w L_BOBS_01BF2                                 ; +$01BC8: 66000028
    lea L_BOBS_020AE(pc),a0                            ; +$01BCC: 41FA04E0
    move.l #$00000020,d1                               ; +$01BD0: 223C00000020
    move.l (a2),d3                                     ; +$01BD6: 2612
    bsr.w L_BOBS_01D38                                 ; +$01BD8: 6100015E
    tst.l d3                                           ; +$01BDC: 4A83
    beq.w L_BOBS_01D2C                                 ; +$01BDE: 6700014C
    move.l (a2),d0                                     ; +$01BE2: 2012
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$01BE4: FE11F700031D
    move.l a0,d0                                       ; +$01BEA: 2008
    tst.l d0                                           ; +$01BEC: 4A80
    beq.w L_BOBS_01D2C                                 ; +$01BEE: 6700013C
L_BOBS_01BF2:
bank_existing:
    cmpi.l #$00000018,d0                               ; +$01BF2: 0C8000000018
    bls.w L_BOBS_01D2C                                 ; +$01BF8: 63000132
    move.l d0,d1                                       ; +$01BFC: 2200
    andi.l #$00000001,d1                               ; +$01BFE: 028100000001
    bne.w L_BOBS_01D2C                                 ; +$01C04: 66000126
    move.l d0,4(a2)                                    ; +$01C08: 25400004
    movea.l d0,a4                                      ; +$01C0C: 2840
    move.l -20(a4),d0                                  ; +$01C0E: 202CFFEC
    cmpi.l #$00000030,d0                               ; +$01C12: 0C8000000030
    bcs.w L_BOBS_01D2C                                 ; +$01C18: 65000112
    cmpi.l #$01000010,d0                               ; +$01C1C: 0C8001000010
    bhi.w L_BOBS_01D2C                                 ; +$01C22: 62000108
    subi.l #$00000010,d0                               ; +$01C26: 048000000010
    move.l d0,8(a2)                                    ; +$01C2C: 25400008
    move.l -16(a4),d0                                  ; +$01C30: 202CFFF0
    move.l (a2),d1                                     ; +$01C34: 2212
    cmp.l d1,d0                                        ; +$01C36: B081
    bne.w L_BOBS_01D2C                                 ; +$01C38: 660000F2
    move.l #$00000000,d0                               ; +$01C3C: 203C00000000
    move.w -12(a4),d0                                  ; +$01C42: 302CFFF4
    tst.l d0                                           ; +$01C46: 4A80
    beq.w L_BOBS_01C58                                 ; +$01C48: 6700000E
    andi.w #$FFFD,d0                                   ; +$01C4C: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$01C50: 0C400001
    bne.w L_BOBS_01D2C                                 ; +$01C54: 660000D6
L_BOBS_01C58:
bank_flags_ok:
    move.l -8(a4),d0                                   ; +$01C58: 202CFFF8
    cmpi.l #$41474142,d0                               ; +$01C5C: 0C8041474142
    bne.w L_BOBS_01D2C                                 ; +$01C62: 660000C8
    move.l -4(a4),d0                                   ; +$01C66: 202CFFFC
    cmpi.l #$4F425320,d0                               ; +$01C6A: 0C804F425320
    bne.w L_BOBS_01D2C                                 ; +$01C70: 660000BA
    move.l (a4),d0                                     ; +$01C74: 2014
    cmpi.l #$4147424F,d0                               ; +$01C76: 0C804147424F
    bne.w L_BOBS_01D2C                                 ; +$01C7C: 660000AE
    move.l #$00000000,d0                               ; +$01C80: 203C00000000
    move.w 4(a4),d0                                    ; +$01C86: 302C0004
    cmpi.l #$00000001,d0                               ; +$01C8A: 0C8000000001
    bne.w L_BOBS_01D2C                                 ; +$01C90: 6600009A
    tst.w 6(a4)                                        ; +$01C94: 4A6C0006
    bne.w L_BOBS_01D2C                                 ; +$01C98: 66000092
    move.l #$00000000,d0                               ; +$01C9C: 203C00000000
    move.w 8(a4),d0                                    ; +$01CA2: 302C0008
    cmpi.l #$00001000,d0                               ; +$01CA6: 0C8000001000
    bhi.w L_BOBS_01D2C                                 ; +$01CAC: 6200007E
    move.l d0,d1                                       ; +$01CB0: 2200
    mulu.w #$0028,d1                                   ; +$01CB2: C2FC0028
    addi.l #$00000020,d1                               ; +$01CB6: 068100000020
    move.l 16(a4),d0                                   ; +$01CBC: 202C0010
    cmp.l d1,d0                                        ; +$01CC0: B081
    bne.w L_BOBS_01D2C                                 ; +$01CC2: 66000068
    move.l #$00000000,d0                               ; +$01CC6: 203C00000000
    move.w 10(a4),d0                                   ; +$01CCC: 302C000A
    cmpi.l #$00000028,d0                               ; +$01CD0: 0C8000000028
    bne.w L_BOBS_01D2C                                 ; +$01CD6: 66000054
    move.l 12(a4),d0                                   ; +$01CDA: 202C000C
    cmpi.l #$00000020,d0                               ; +$01CDE: 0C8000000020
    bne.w L_BOBS_01D2C                                 ; +$01CE4: 66000046
    move.l 20(a4),d0                                   ; +$01CE8: 202C0014
    move.l 8(a2),d1                                    ; +$01CEC: 222A0008
    cmp.l d1,d0                                        ; +$01CF0: B081
    bne.w L_BOBS_01D2C                                 ; +$01CF2: 66000038
    move.l 24(a4),d0                                   ; +$01CF6: 202C0018
    tst.l d0                                           ; +$01CFA: 4A80
    beq.w L_BOBS_01D2C                                 ; +$01CFC: 6700002E
    tst.l 28(a4)                                       ; +$01D00: 4AAC001C
    bne.w L_BOBS_01D2C                                 ; +$01D04: 66000026
    move.l 1514(a5),d0                                 ; +$01D08: 202D05EA
    tst.l d0                                           ; +$01D0C: 4A80
    beq.w L_BOBS_01D2C                                 ; +$01D0E: 6700001C
    lea L_BOBS_020A2(pc),a0                            ; +$01D12: 41FA038E
    move.l (a2),d1                                     ; +$01D16: 2212
    move.l d1,(a0)                                     ; +$01D18: 2081
    move.l 4(a2),d1                                    ; +$01D1A: 222A0004
    move.l d1,4(a0)                                    ; +$01D1E: 21410004
    move.l d0,8(a0)                                    ; +$01D22: 21400008
    move.l #$00000001,d3                               ; +$01D26: 263C00000001
L_BOBS_01D2C:
bank_done:
    lea 64(a7),a7                                      ; +$01D2C: 4FEF0040
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$01D30: 4CDF77F7
    moveq #0,d2                                        ; +$01D34: 7400
    rts                                                ; +$01D36: 4E75
L_BOBS_01D38:
bank_commit:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$01D38: 48E7EFEE
    lea -80(a7),a7                                     ; +$01D3C: 4FEFFFB0
    movea.l a7,a2                                      ; +$01D40: 244F
    move.l d3,(a2)                                     ; +$01D42: 2483
    move.l a0,4(a2)                                    ; +$01D44: 25480004
    move.l d1,8(a2)                                    ; +$01D48: 25410008
    move.l #$00000000,12(a2)                           ; +$01D4C: 257C00000000000C
    move.l #$00000000,16(a2)                           ; +$01D54: 257C000000000010
    move.l #$00000000,20(a2)                           ; +$01D5C: 257C000000000014
    move.l #$00000000,24(a2)                           ; +$01D64: 257C000000000018
    move.l #$00000000,28(a2)                           ; +$01D6C: 257C00000000001C
    move.l #$00000000,32(a2)                           ; +$01D74: 257C000000000020
    move.l #$00000000,d3                               ; +$01D7C: 263C00000000
    move.l (a2),d0                                     ; +$01D82: 2012
    cmpi.l #$00000005,d0                               ; +$01D84: 0C8000000005
    bcs.w L_BOBS_0207E                                 ; +$01D8A: 650002F2
    cmpi.l #$0000FFFF,d0                               ; +$01D8E: 0C800000FFFF
    bhi.w L_BOBS_0207E                                 ; +$01D94: 620002E8
    move.l 8(a2),d0                                    ; +$01D98: 202A0008
    cmpi.l #$00000020,d0                               ; +$01D9C: 0C8000000020
    bcs.w L_BOBS_0207E                                 ; +$01DA2: 650002DA
    cmpi.l #$01000000,d0                               ; +$01DA6: 0C8001000000
    bhi.w L_BOBS_0207E                                 ; +$01DAC: 620002D0
    move.l d0,d1                                       ; +$01DB0: 2200
    andi.l #$00000001,d1                               ; +$01DB2: 028100000001
    bne.w L_BOBS_0207E                                 ; +$01DB8: 660002C4
    move.l 4(a2),d0                                    ; +$01DBC: 202A0004
    cmpi.l #$00000018,d0                               ; +$01DC0: 0C8000000018
    bls.w L_BOBS_0207E                                 ; +$01DC6: 630002B6
    move.l d0,d0                                       ; +$01DCA: 2000
    andi.l #$00000001,d0                               ; +$01DCC: 028000000001
    bne.w L_BOBS_0207E                                 ; +$01DD2: 660002AA
    movea.l 4(a2),a0                                   ; +$01DD6: 206A0004
    move.l (a0),d0                                     ; +$01DDA: 2010
    cmpi.l #$4147424F,d0                               ; +$01DDC: 0C804147424F
    bne.w L_BOBS_0207E                                 ; +$01DE2: 6600029A
    move.l #$00000000,d0                               ; +$01DE6: 203C00000000
    move.w 4(a0),d0                                    ; +$01DEC: 30280004
    cmpi.l #$00000001,d0                               ; +$01DF0: 0C8000000001
    bne.w L_BOBS_0207E                                 ; +$01DF6: 66000286
    tst.w 6(a0)                                        ; +$01DFA: 4A680006
    bne.w L_BOBS_0207E                                 ; +$01DFE: 6600027E
    move.l #$00000000,d0                               ; +$01E02: 203C00000000
    move.w 10(a0),d0                                   ; +$01E08: 3028000A
    cmpi.l #$00000028,d0                               ; +$01E0C: 0C8000000028
    bne.w L_BOBS_0207E                                 ; +$01E12: 6600026A
    move.l 12(a0),d0                                   ; +$01E16: 2028000C
    cmpi.l #$00000020,d0                               ; +$01E1A: 0C8000000020
    bne.w L_BOBS_0207E                                 ; +$01E20: 6600025C
    move.l 20(a0),d0                                   ; +$01E24: 20280014
    cmp.l 8(a2),d0                                     ; +$01E28: B0AA0008
    bne.w L_BOBS_0207E                                 ; +$01E2C: 66000250
    move.l 24(a0),d0                                   ; +$01E30: 20280018
    tst.l d0                                           ; +$01E34: 4A80
    beq.w L_BOBS_0207E                                 ; +$01E36: 67000246
    tst.l 28(a0)                                       ; +$01E3A: 4AA8001C
    bne.w L_BOBS_0207E                                 ; +$01E3E: 6600023E
    move.l #$00000000,d0                               ; +$01E42: 203C00000000
    move.w 8(a0),d0                                    ; +$01E48: 30280008
    cmpi.l #$00001000,d0                               ; +$01E4C: 0C8000001000
    bhi.w L_BOBS_0207E                                 ; +$01E52: 6200022A
    mulu.w #$0028,d0                                   ; +$01E56: C0FC0028
    addi.l #$00000020,d0                               ; +$01E5A: 068000000020
    movea.l 4(a2),a0                                   ; +$01E60: 206A0004
    cmp.l 16(a0),d0                                    ; +$01E64: B0A80010
    bne.w L_BOBS_0207E                                 ; +$01E68: 66000214
    move.l 8(a2),d0                                    ; +$01E6C: 202A0008
    addi.l #$0000000F,d0                               ; +$01E70: 06800000000F
    move.l 4(a2),d1                                    ; +$01E76: 222A0004
    add.l d0,d1                                        ; +$01E7A: D280
    bcs.w L_BOBS_0207E                                 ; +$01E7C: 65000200
    movea.l 1514(a5),a0                                ; +$01E80: 206D05EA
    move.l a0,d0                                       ; +$01E84: 2008
    tst.l d0                                           ; +$01E86: 4A80
    beq.w L_BOBS_0207E                                 ; +$01E88: 670001F4
    move.l a0,28(a2)                                   ; +$01E8C: 2548001C
    move.l d0,d0                                       ; +$01E90: 2000
    andi.l #$00000001,d0                               ; +$01E92: 028000000001
    bne.w L_BOBS_0207E                                 ; +$01E98: 660001E4
    move.l (a2),d0                                     ; +$01E9C: 2012
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$01E9E: FE11F700031D
    move.l a0,d4                                       ; +$01EA4: 2808
    tst.l d4                                           ; +$01EA6: 4A84
    beq.w L_BOBS_01F50                                 ; +$01EA8: 670000A6
    cmpi.l #$00000018,d4                               ; +$01EAC: 0C8400000018
    bls.w L_BOBS_0207E                                 ; +$01EB2: 630001CA
    move.l d4,d0                                       ; +$01EB6: 2004
    andi.l #$00000001,d0                               ; +$01EB8: 028000000001
    bne.w L_BOBS_0207E                                 ; +$01EBE: 660001BE
    move.l d4,12(a2)                                   ; +$01EC2: 2544000C
    subi.l #$00000018,d4                               ; +$01EC6: 048400000018
    move.l d4,16(a2)                                   ; +$01ECC: 25440010
    movea.l d4,a4                                      ; +$01ED0: 2844
    move.l 8(a4),d0                                    ; +$01ED2: 202C0008
    move.l (a2),d1                                     ; +$01ED6: 2212
    cmp.l d1,d0                                        ; +$01ED8: B081
    bne.w L_BOBS_0207E                                 ; +$01EDA: 660001A2
    move.l #$00000000,d0                               ; +$01EDE: 203C00000000
    move.w 12(a4),d0                                   ; +$01EE4: 302C000C
    tst.l d0                                           ; +$01EE8: 4A80
    beq.w L_BOBS_01EFA                                 ; +$01EEA: 6700000E
    andi.w #$FFFD,d0                                   ; +$01EEE: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$01EF2: 0C400001
    bne.w L_BOBS_0207E                                 ; +$01EF6: 66000186
L_BOBS_01EFA:
    move.l 16(a4),d0                                   ; +$01EFA: 202C0010
    cmpi.l #$41474142,d0                               ; +$01EFE: 0C8041474142
    bne.w L_BOBS_0207E                                 ; +$01F04: 66000178
    move.l 20(a4),d0                                   ; +$01F08: 202C0014
    cmpi.l #$4F425320,d0                               ; +$01F0C: 0C804F425320
    bne.w L_BOBS_0207E                                 ; +$01F12: 6600016A
    move.l 4(a4),d0                                    ; +$01F16: 202C0004
    cmpi.l #$00000030,d0                               ; +$01F1A: 0C8000000030
    bcs.w L_BOBS_0207E                                 ; +$01F20: 6500015C
    cmpi.l #$01000010,d0                               ; +$01F24: 0C8001000010
    bhi.w L_BOBS_0207E                                 ; +$01F2A: 62000152
    subi.l #$00000010,d0                               ; +$01F2E: 048000000010
    movea.l 12(a2),a0                                  ; +$01F34: 206A000C
    move.l (a0),d1                                     ; +$01F38: 2210
    cmpi.l #$4147424F,d1                               ; +$01F3A: 0C814147424F
    bne.w L_BOBS_0207E                                 ; +$01F40: 6600013C
    cmp.l 20(a0),d0                                    ; +$01F44: B0A80014
    bne.w L_BOBS_0207E                                 ; +$01F48: 66000134
    bra.w L_BOBS_01F50                                 ; +$01F4C: 60000002
L_BOBS_01F50:
    lea 24(a2),a0                                      ; +$01F50: 41EA0018
    move.l 8(a2),d0                                    ; +$01F54: 202A0008
    addi.l #$00000010,d0                               ; +$01F58: 068000000010
    move.l #$00010001,d1                               ; +$01F5E: 223C00010001
    dc.w $FE11,$F700,AMOS_MAIN_LIST_CREATE  ; +$01F64: FE11F700005B
    move.l a1,d4                                       ; +$01F6A: 2809
    tst.l d0                                           ; +$01F6C: 4A80
    beq.w L_BOBS_0207E                                 ; +$01F6E: 6700010E
    tst.l d4                                           ; +$01F72: 4A84
    beq.w L_BOBS_0207E                                 ; +$01F74: 67000108
    move.l d4,20(a2)                                   ; +$01F78: 25440014
    movea.l d4,a4                                      ; +$01F7C: 2844
    move.l (a2),d0                                     ; +$01F7E: 2012
    move.l d0,8(a4)                                    ; +$01F80: 29400008
    move.w #$0001,12(a4)                               ; +$01F84: 397C0001000C
    move.w #$0000,14(a4)                               ; +$01F8A: 397C0000000E
    move.l #$41474142,16(a4)                           ; +$01F90: 297C414741420010
    move.l #$4F425320,20(a4)                           ; +$01F98: 297C4F4253200014
    movea.l 4(a2),a0                                   ; +$01FA0: 206A0004
    lea 24(a4),a1                                      ; +$01FA4: 43EC0018
    move.l 8(a2),d6                                    ; +$01FA8: 2C2A0008
    move.l d6,d7                                       ; +$01FAC: 2E06
    lsr.l #2,d6                                        ; +$01FAE: E48E
L_BOBS_01FB0:
    move.l (a0)+,(a1)+                                 ; +$01FB0: 22D8
    subq.l #1,d6                                       ; +$01FB2: 5386
    bne.w L_BOBS_01FB0                                 ; +$01FB4: 6600FFFA
    andi.l #$00000002,d7                               ; +$01FB8: 028700000002
    tst.l d7                                           ; +$01FBE: 4A87
    beq.w L_BOBS_01FC6                                 ; +$01FC0: 67000004
    move.w (a0)+,(a1)+                                 ; +$01FC4: 32D8
L_BOBS_01FC6:
    move.l (a2),d0                                     ; +$01FC6: 2012
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$01FC8: FE11F700031D
    move.l a0,d0                                       ; +$01FCE: 2008
    cmp.l 12(a2),d0                                    ; +$01FD0: B0AA000C
    bne.w L_BOBS_0207E                                 ; +$01FD4: 660000A8
    move.l 1514(a5),d0                                 ; +$01FD8: 202D05EA
    cmp.l 28(a2),d0                                    ; +$01FDC: B0AA001C
    bne.w L_BOBS_0207E                                 ; +$01FE0: 6600009C
    movea.l 28(a2),a0                                  ; +$01FE4: 206A001C
    move.l a0,32(a2)                                   ; +$01FE8: 25480020
    move.l 16(a2),d5                                   ; +$01FEC: 2A2A0010
    tst.l d5                                           ; +$01FF0: 4A85
    beq.w L_BOBS_02040                                 ; +$01FF2: 6700004C
    move.l #$0000FFFF,d6                               ; +$01FF6: 2C3C0000FFFF
L_BOBS_01FFC:
    movea.l 32(a2),a0                                  ; +$01FFC: 206A0020
    move.l (a0),d0                                     ; +$02000: 2010
    cmp.l d5,d0                                        ; +$02002: B085
    beq.w L_BOBS_0201C                                 ; +$02004: 67000016
    tst.l d0                                           ; +$02008: 4A80
    beq.w L_BOBS_0207E                                 ; +$0200A: 67000072
    move.l d0,32(a2)                                   ; +$0200E: 25400020
    subq.l #1,d6                                       ; +$02012: 5386
    bne.w L_BOBS_01FFC                                 ; +$02014: 6600FFE6
    bra.w L_BOBS_0207E                                 ; +$02018: 60000064
L_BOBS_0201C:
    movea.l 16(a2),a0                                  ; +$0201C: 206A0010
    move.l (a0),d0                                     ; +$02020: 2010
    movea.l 20(a2),a1                                  ; +$02022: 226A0014
    move.l d0,(a1)                                     ; +$02026: 2280
    movea.l 32(a2),a0                                  ; +$02028: 206A0020
    move.l a1,(a0)                                     ; +$0202C: 2089
    movea.l 16(a2),a0                                  ; +$0202E: 206A0010
    move.l #$00000000,(a0)                             ; +$02032: 20BC00000000
    move.l a0,24(a2)                                   ; +$02038: 25480018
    bra.w L_BOBS_02056                                 ; +$0203C: 60000018
L_BOBS_02040:
    movea.l 28(a2),a0                                  ; +$02040: 206A001C
    move.l (a0),d0                                     ; +$02044: 2010
    movea.l 20(a2),a1                                  ; +$02046: 226A0014
    move.l d0,(a1)                                     ; +$0204A: 2280
    move.l a1,(a0)                                     ; +$0204C: 2089
    move.l #$00000000,24(a2)                           ; +$0204E: 257C000000000018
L_BOBS_02056:
    dc.w $FE11,$F700,AMOS_MAIN_CHANGE  ; +$02056: FE11F7000333
    move.l 16(a2),d0                                   ; +$0205C: 202A0010
    tst.l d0                                           ; +$02060: 4A80
    beq.w L_BOBS_02074                                 ; +$02062: 67000010
    lea 24(a2),a0                                      ; +$02066: 41EA0018
    movea.l 16(a2),a1                                  ; +$0206A: 226A0010
    dc.w $FE11,$F700,AMOS_MAIN_LIST_DELETE  ; +$0206E: FE11F700005D
L_BOBS_02074:
    move.l #$00000001,d3                               ; +$02074: 263C00000001
    bra.w L_BOBS_02096                                 ; +$0207A: 6000001A
L_BOBS_0207E:
    move.l 20(a2),d0                                   ; +$0207E: 202A0014
    tst.l d0                                           ; +$02082: 4A80
    beq.w L_BOBS_02096                                 ; +$02084: 67000010
    lea 24(a2),a0                                      ; +$02088: 41EA0018
    movea.l 20(a2),a1                                  ; +$0208C: 226A0014
    dc.w $FE11,$F700,AMOS_MAIN_LIST_DELETE  ; +$02090: FE11F700005D
L_BOBS_02096:
    lea 80(a7),a7                                      ; +$02096: 4FEF0050
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0209A: 4CDF77F7
    moveq #0,d2                                        ; +$0209E: 7400
    rts                                                ; +$020A0: 4E75
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
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$020CE: 48E7EFEE
    lea -320(a7),a7                                    ; +$020D2: 4FEFFEC0
    movea.l a7,a2                                      ; +$020D6: 244F
    move.l d3,16(a2)                                   ; +$020D8: 25430010
    move.l (a3)+,d7                                    ; +$020DC: 2E1B
    move.l d7,12(a2)                                   ; +$020DE: 2547000C
    move.l (a3)+,d7                                    ; +$020E2: 2E1B
    move.l d7,8(a2)                                    ; +$020E4: 25470008
    move.l (a3)+,d7                                    ; +$020E8: 2E1B
    move.l d7,4(a2)                                    ; +$020EA: 25470004
    move.l (a3)+,d7                                    ; +$020EE: 2E1B
    move.l d7,(a2)                                     ; +$020F0: 2487
    move.l #$00000000,156(a2)                          ; +$020F2: 257C00000000009C
    move.l #$00000000,224(a2)                          ; +$020FA: 257C0000000000E0
    move.l #$00000000,d3                               ; +$02102: 263C00000000
    movea.l $0004.w,a0                                 ; +$02108: 20780004
    move.l a0,d0                                       ; +$0210C: 2008
    tst.l d0                                           ; +$0210E: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02110: 670009B2
    move.w 296(a0),d0                                  ; +$02114: 30280128
    btst #1,d0                                         ; +$02118: 08000001
    beq.w L_BOBS_02AC4                                 ; +$0211C: 670009A6
    move.l (a2),d0                                     ; +$02120: 2012
    cmpi.l #$00000001,d0                               ; +$02122: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$02128: 6500099A
    cmpi.l #$00001000,d0                               ; +$0212C: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02132: 62000990
    move.l 4(a2),d0                                    ; +$02136: 202A0004
    tst.l d0                                           ; +$0213A: 4A80
    bmi.w L_BOBS_02AC4                                 ; +$0213C: 6B000986
    cmpi.l #$00001000,d0                               ; +$02140: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02146: 6200097C
    move.l 8(a2),d0                                    ; +$0214A: 202A0008
    tst.l d0                                           ; +$0214E: 4A80
    bmi.w L_BOBS_02AC4                                 ; +$02150: 6B000972
    cmpi.l #$00001000,d0                               ; +$02154: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$0215A: 62000968
    move.l 12(a2),d0                                   ; +$0215E: 202A000C
    tst.l d0                                           ; +$02162: 4A80
    bmi.w L_BOBS_02AC4                                 ; +$02164: 6B00095E
    cmpi.l #$00001000,d0                               ; +$02168: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$0216E: 62000954
    move.l 16(a2),d0                                   ; +$02172: 202A0010
    tst.l d0                                           ; +$02176: 4A80
    bmi.w L_BOBS_02AC4                                 ; +$02178: 6B00094A
    cmpi.l #$00001000,d0                               ; +$0217C: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02182: 62000940
    move.l 4(a2),d0                                    ; +$02186: 202A0004
    move.l 12(a2),d1                                   ; +$0218A: 222A000C
    cmp.l d0,d1                                        ; +$0218E: B280
    bcs.w L_BOBS_02AC4                                 ; +$02190: 65000932
    move.l 8(a2),d0                                    ; +$02194: 202A0008
    move.l 16(a2),d1                                   ; +$02198: 222A0010
    cmp.l d0,d1                                        ; +$0219C: B280
    bcs.w L_BOBS_02AC4                                 ; +$0219E: 65000924
    lea L_BOBS_020A2(pc),a0                            ; +$021A2: 41FAFEFE
    move.l (a0),d0                                     ; +$021A6: 2010
    cmpi.l #$00000005,d0                               ; +$021A8: 0C8000000005
    bcs.w L_BOBS_02AC4                                 ; +$021AE: 65000914
    cmpi.l #$0000FFFF,d0                               ; +$021B2: 0C800000FFFF
    bhi.w L_BOBS_02AC4                                 ; +$021B8: 6200090A
    move.l d0,20(a2)                                   ; +$021BC: 25400014
    move.l 4(a0),d0                                    ; +$021C0: 20280004
    tst.l d0                                           ; +$021C4: 4A80
    beq.w L_BOBS_02AC4                                 ; +$021C6: 670008FC
    move.l d0,24(a2)                                   ; +$021CA: 25400018
    move.l 8(a0),d0                                    ; +$021CE: 20280008
    tst.l d0                                           ; +$021D2: 4A80
    beq.w L_BOBS_02AC4                                 ; +$021D4: 670008EE
    move.l d0,28(a2)                                   ; +$021D8: 2540001C
    move.l 1514(a5),d0                                 ; +$021DC: 202D05EA
    move.l 28(a2),d1                                   ; +$021E0: 222A001C
    cmp.l d1,d0                                        ; +$021E4: B081
    bne.w L_BOBS_02AC4                                 ; +$021E6: 660008DC
    move.l 20(a2),d0                                   ; +$021EA: 202A0014
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$021EE: FE11F700031D
    move.l a0,d0                                       ; +$021F4: 2008
    move.l 24(a2),d1                                   ; +$021F6: 222A0018
    cmp.l d1,d0                                        ; +$021FA: B081
    bne.w L_BOBS_02AC4                                 ; +$021FC: 660008C6
    move.l 24(a2),d0                                   ; +$02200: 202A0018
    cmpi.l #$00000018,d0                               ; +$02204: 0C8000000018
    bls.w L_BOBS_02AC4                                 ; +$0220A: 630008B8
    move.l d0,d1                                       ; +$0220E: 2200
    andi.l #$00000001,d1                               ; +$02210: 028100000001
    bne.w L_BOBS_02AC4                                 ; +$02216: 660008AC
    movea.l d0,a4                                      ; +$0221A: 2840
    move.l -20(a4),d0                                  ; +$0221C: 202CFFEC
    cmpi.l #$00000030,d0                               ; +$02220: 0C8000000030
    bcs.w L_BOBS_02AC4                                 ; +$02226: 6500089C
    cmpi.l #$01000010,d0                               ; +$0222A: 0C8001000010
    bhi.w L_BOBS_02AC4                                 ; +$02230: 62000892
    subi.l #$00000010,d0                               ; +$02234: 048000000010
    move.l d0,32(a2)                                   ; +$0223A: 25400020
    move.l 24(a2),d0                                   ; +$0223E: 202A0018
    subi.l #$00000018,d0                               ; +$02242: 048000000018
    movea.l d0,a1                                      ; +$02248: 2240
    movea.l $0004.w,a6                                 ; +$0224A: 2C780004
    jsr -534(a6)                                       ; +$0224E: 4EAEFDEA
    tst.l d0                                           ; +$02252: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02254: 6700086E
    move.l 24(a2),d0                                   ; +$02258: 202A0018
    move.l 32(a2),d1                                   ; +$0225C: 222A0020
    add.l d1,d0                                        ; +$02260: D081
    bcs.w L_BOBS_02AC4                                 ; +$02262: 65000860
    subq.l #1,d0                                       ; +$02266: 5380
    movea.l d0,a1                                      ; +$02268: 2240
    movea.l $0004.w,a6                                 ; +$0226A: 2C780004
    jsr -534(a6)                                       ; +$0226E: 4EAEFDEA
    tst.l d0                                           ; +$02272: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02274: 6700084E
    movea.l 24(a2),a4                                  ; +$02278: 286A0018
    move.l -16(a4),d0                                  ; +$0227C: 202CFFF0
    move.l 20(a2),d1                                   ; +$02280: 222A0014
    cmp.l d1,d0                                        ; +$02284: B081
    bne.w L_BOBS_02AC4                                 ; +$02286: 6600083C
    move.l #$00000000,d0                               ; +$0228A: 203C00000000
    move.w -12(a4),d0                                  ; +$02290: 302CFFF4
    tst.l d0                                           ; +$02294: 4A80
    beq.w L_BOBS_022A6                                 ; +$02296: 6700000E
    andi.w #$FFFD,d0                                   ; +$0229A: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$0229E: 0C400001
    bne.w L_BOBS_02AC4                                 ; +$022A2: 66000820
L_BOBS_022A6:
old_flags_good:
    move.l -8(a4),d0                                   ; +$022A6: 202CFFF8
    cmpi.l #$41474142,d0                               ; +$022AA: 0C8041474142
    bne.w L_BOBS_02AC4                                 ; +$022B0: 66000812
    move.l -4(a4),d0                                   ; +$022B4: 202CFFFC
    cmpi.l #$4F425320,d0                               ; +$022B8: 0C804F425320
    bne.w L_BOBS_02AC4                                 ; +$022BE: 66000804
    move.l (a4),d0                                     ; +$022C2: 2014
    cmpi.l #$4147424F,d0                               ; +$022C4: 0C804147424F
    bne.w L_BOBS_02AC4                                 ; +$022CA: 660007F8
    move.l #$00000000,d0                               ; +$022CE: 203C00000000
    move.w 4(a4),d0                                    ; +$022D4: 302C0004
    cmpi.l #$00000001,d0                               ; +$022D8: 0C8000000001
    bne.w L_BOBS_02AC4                                 ; +$022DE: 660007E4
    tst.w 6(a4)                                        ; +$022E2: 4A6C0006
    bne.w L_BOBS_02AC4                                 ; +$022E6: 660007DC
    move.l #$00000000,d0                               ; +$022EA: 203C00000000
    move.w 8(a4),d0                                    ; +$022F0: 302C0008
    cmpi.l #$00001000,d0                               ; +$022F4: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$022FA: 620007C8
    move.l d0,36(a2)                                   ; +$022FE: 25400024
    move.l #$00000000,d0                               ; +$02302: 203C00000000
    move.w 10(a4),d0                                   ; +$02308: 302C000A
    cmpi.l #$00000028,d0                               ; +$0230C: 0C8000000028
    bne.w L_BOBS_02AC4                                 ; +$02312: 660007B0
    move.l 12(a4),d0                                   ; +$02316: 202C000C
    cmpi.l #$00000020,d0                               ; +$0231A: 0C8000000020
    bne.w L_BOBS_02AC4                                 ; +$02320: 660007A2
    move.l 36(a2),d0                                   ; +$02324: 202A0024
    mulu.w #$0028,d0                                   ; +$02328: C0FC0028
    addi.l #$00000020,d0                               ; +$0232C: 068000000020
    movea.l 24(a2),a4                                  ; +$02332: 286A0018
    cmp.l 16(a4),d0                                    ; +$02336: B0AC0010
    bne.w L_BOBS_02AC4                                 ; +$0233A: 66000788
    move.l 32(a2),d1                                   ; +$0233E: 222A0020
    cmp.l d1,d0                                        ; +$02342: B081
    bhi.w L_BOBS_02AC4                                 ; +$02344: 6200077E
    move.l d0,40(a2)                                   ; +$02348: 25400028
    move.l 20(a4),d0                                   ; +$0234C: 202C0014
    move.l 32(a2),d1                                   ; +$02350: 222A0020
    cmp.l d1,d0                                        ; +$02354: B081
    bne.w L_BOBS_02AC4                                 ; +$02356: 6600076C
    move.l 24(a4),d0                                   ; +$0235A: 202C0018
    tst.l d0                                           ; +$0235E: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02360: 67000762
    cmpi.l #$FFFFFFFF,d0                               ; +$02364: 0C80FFFFFFFF
    beq.w L_BOBS_02AC4                                 ; +$0236A: 67000758
    move.l d0,44(a2)                                   ; +$0236E: 2540002C
    tst.l 28(a4)                                       ; +$02372: 4AAC001C
    bne.w L_BOBS_02AC4                                 ; +$02376: 6600074C
    move.l #$00000000,48(a2)                           ; +$0237A: 257C000000000030
    move.l #$00000000,52(a2)                           ; +$02382: 257C000000000034
    move.l 40(a2),d0                                   ; +$0238A: 202A0028
    move.l d0,56(a2)                                   ; +$0238E: 25400038
    move.l 24(a2),d0                                   ; +$02392: 202A0018
    addi.l #$00000020,d0                               ; +$02396: 068000000020
    move.l d0,60(a2)                                   ; +$0239C: 2540003C
    move.l #$00000000,172(a2)                          ; +$023A0: 257C0000000000AC
L_BOBS_023A8:
validate_old_loop:
    move.l 172(a2),d0                                  ; +$023A8: 202A00AC
    move.l 36(a2),d1                                   ; +$023AC: 222A0024
    cmp.l d1,d0                                        ; +$023B0: B081
    bge.w L_BOBS_0262C                                 ; +$023B2: 6C000278
    movea.l 60(a2),a4                                  ; +$023B6: 286A003C
    move.l #$00000000,d0                               ; +$023BA: 203C00000000
    move.w (a4),d0                                     ; +$023C0: 3014
    move.l 52(a2),d1                                   ; +$023C2: 222A0034
    cmp.l d1,d0                                        ; +$023C6: B081
    bls.w L_BOBS_02AC4                                 ; +$023C8: 630006FA
    cmpi.l #$00001000,d0                               ; +$023CC: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$023D2: 620006F0
    move.l d0,52(a2)                                   ; +$023D6: 25400034
    move.l (a2),d1                                     ; +$023DA: 2212
    cmp.l d1,d0                                        ; +$023DC: B081
    bne.w L_BOBS_023EA                                 ; +$023DE: 6600000A
    move.l #$00000001,48(a2)                           ; +$023E2: 257C000000010030
L_BOBS_023EA:
not_replaced:
    move.l #$00000000,d0                               ; +$023EA: 203C00000000
    move.w 2(a4),d0                                    ; +$023F0: 302C0002
    cmpi.l #$00000001,d0                               ; +$023F4: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$023FA: 650006C8
    cmpi.l #$00001000,d0                               ; +$023FE: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02404: 620006BE
    move.l d0,64(a2)                                   ; +$02408: 25400040
    move.l #$00000000,d0                               ; +$0240C: 203C00000000
    move.w 4(a4),d0                                    ; +$02412: 302C0004
    cmpi.l #$00000001,d0                               ; +$02416: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$0241C: 650006A6
    cmpi.l #$00001000,d0                               ; +$02420: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02426: 6200069C
    move.l d0,72(a2)                                   ; +$0242A: 25400048
    move.l #$00000000,d0                               ; +$0242E: 203C00000000
    move.w 6(a4),d0                                    ; +$02434: 302C0006
    cmpi.l #$00000001,d0                               ; +$02438: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$0243E: 65000684
    cmpi.l #$00000008,d0                               ; +$02442: 0C8000000008
    bhi.w L_BOBS_02AC4                                 ; +$02448: 6200067A
    move.l d0,68(a2)                                   ; +$0244C: 25400044
    move.l 64(a2),d0                                   ; +$02450: 202A0040
    move.l 72(a2),d1                                   ; +$02454: 222A0048
    mulu.w d1,d0                                       ; +$02458: C0C1
    cmpi.l #$00400000,d0                               ; +$0245A: 0C8000400000
    bhi.w L_BOBS_02AC4                                 ; +$02460: 62000662
    move.l 64(a2),d0                                   ; +$02464: 202A0040
    addi.l #$0000000F,d0                               ; +$02468: 06800000000F
    lsr.l #4,d0                                        ; +$0246E: E888
    lsl.l #1,d0                                        ; +$02470: E388
    move.l #$00000000,d1                               ; +$02472: 223C00000000
    move.w 8(a4),d1                                    ; +$02478: 322C0008
    cmp.l d1,d0                                        ; +$0247C: B081
    bne.w L_BOBS_02AC4                                 ; +$0247E: 66000644
    move.l d0,64(a2)                                   ; +$02482: 25400040
    move.l #$00000000,d0                               ; +$02486: 203C00000000
    move.w 10(a4),d0                                   ; +$0248C: 302C000A
    andi.l #$0000FFFE,d0                               ; +$02490: 02800000FFFE
    tst.l d0                                           ; +$02496: 4A80
    bne.w L_BOBS_02AC4                                 ; +$02498: 6600062A
    move.l 64(a2),d0                                   ; +$0249C: 202A0040
    move.l 72(a2),d1                                   ; +$024A0: 222A0048
    mulu.w d1,d0                                       ; +$024A4: C0C1
    move.l d0,d6                                       ; +$024A6: 2C00
    move.l 68(a2),d5                                   ; +$024A8: 2A2A0044
    move.l #$00000000,d7                               ; +$024AC: 2E3C00000000
L_BOBS_024B2:
old_depth_sum:
    add.l d6,d7                                        ; +$024B2: DE86
    bcs.w L_BOBS_02AC4                                 ; +$024B4: 6500060E
    subq.l #1,d5                                       ; +$024B8: 5385
    bne.w L_BOBS_024B2                                 ; +$024BA: 6600FFF6
    movea.l 60(a2),a4                                  ; +$024BE: 286A003C
    move.l 16(a4),d0                                   ; +$024C2: 202C0010
    cmp.l d7,d0                                        ; +$024C6: B087
    bne.w L_BOBS_02AC4                                 ; +$024C8: 660005FA
    move.l d7,76(a2)                                   ; +$024CC: 2547004C
    move.l 56(a2),d0                                   ; +$024D0: 202A0038
    cmp.l 12(a4),d0                                    ; +$024D4: B0AC000C
    bne.w L_BOBS_02AC4                                 ; +$024D8: 660005EA
    move.l 24(a4),d0                                   ; +$024DC: 202C0018
    tst.l d0                                           ; +$024E0: 4A80
    beq.w L_BOBS_02522                                 ; +$024E2: 6700003E
    move.l #$00000000,d0                               ; +$024E6: 203C00000000
    move.w 10(a4),d0                                   ; +$024EC: 302C000A
    cmpi.l #$00000001,d0                               ; +$024F0: 0C8000000001
    bne.w L_BOBS_02AC4                                 ; +$024F6: 660005CC
    move.l 24(a4),d0                                   ; +$024FA: 202C0018
    cmp.l d6,d0                                        ; +$024FE: B086
    bne.w L_BOBS_02AC4                                 ; +$02500: 660005C2
    move.l 56(a2),d0                                   ; +$02504: 202A0038
    move.l 76(a2),d1                                   ; +$02508: 222A004C
    add.l d1,d0                                        ; +$0250C: D081
    bcs.w L_BOBS_02AC4                                 ; +$0250E: 650005B4
    cmp.l 20(a4),d0                                    ; +$02512: B0AC0014
    bne.w L_BOBS_02AC4                                 ; +$02516: 660005AC
    move.l d6,80(a2)                                   ; +$0251A: 25460050
    bra.w L_BOBS_02542                                 ; +$0251E: 60000022
L_BOBS_02522:
no_mask:
    tst.l 20(a4)                                       ; +$02522: 4AAC0014
    bne.w L_BOBS_02AC4                                 ; +$02526: 6600059C
    move.l #$00000000,d0                               ; +$0252A: 203C00000000
    move.w 10(a4),d0                                   ; +$02530: 302C000A
    tst.l d0                                           ; +$02534: 4A80
    bne.w L_BOBS_02AC4                                 ; +$02536: 6600058C
    move.l #$00000000,80(a2)                           ; +$0253A: 257C000000000050
L_BOBS_02542:
mask_checked:
    move.l 56(a2),d0                                   ; +$02542: 202A0038
    move.l 76(a2),d1                                   ; +$02546: 222A004C
    add.l d1,d0                                        ; +$0254A: D081
    bcs.w L_BOBS_02AC4                                 ; +$0254C: 65000576
    move.l 80(a2),d1                                   ; +$02550: 222A0050
    add.l d1,d0                                        ; +$02554: D081
    bcs.w L_BOBS_02AC4                                 ; +$02556: 6500056C
    move.l 32(a2),d1                                   ; +$0255A: 222A0020
    cmp.l d1,d0                                        ; +$0255E: B081
    bhi.w L_BOBS_02AC4                                 ; +$02560: 62000562
    move.l d0,56(a2)                                   ; +$02564: 25400038
    movea.l 60(a2),a4                                  ; +$02568: 286A003C
    tst.l 32(a4)                                       ; +$0256C: 4AAC0020
    bne.w L_BOBS_02AC4                                 ; +$02570: 66000552
    tst.l 36(a4)                                       ; +$02574: 4AAC0024
    bne.w L_BOBS_02AC4                                 ; +$02578: 6600054A
    movea.l 24(a2),a0                                  ; +$0257C: 206A0018
    movea.l 60(a2),a4                                  ; +$02580: 286A003C
    move.l 12(a4),d0                                   ; +$02584: 202C000C
    add.l a0,d0                                        ; +$02588: D088
    movea.l d0,a0                                      ; +$0258A: 2040
    move.l #$00000000,d0                               ; +$0258C: 203C00000000
    move.w 2(a4),d0                                    ; +$02592: 302C0002
    move.l 64(a2),d1                                   ; +$02596: 222A0040
    move.l 72(a2),d2                                   ; +$0259A: 242A0048
    move.l 68(a2),d3                                   ; +$0259E: 262A0044
    bsr.w L_BOBS_02AE8                                 ; +$025A2: 61000544
    tst.l d0                                           ; +$025A6: 4A80
    beq.w L_BOBS_02AC4                                 ; +$025A8: 6700051A
    move.l 80(a2),d0                                   ; +$025AC: 202A0050
    tst.l d0                                           ; +$025B0: 4A80
    beq.w L_BOBS_025EA                                 ; +$025B2: 67000036
    move.l 24(a2),d0                                   ; +$025B6: 202A0018
    movea.l 60(a2),a4                                  ; +$025BA: 286A003C
    add.l 20(a4),d0                                    ; +$025BE: D0AC0014
    bcs.w L_BOBS_02AC4                                 ; +$025C2: 65000500
    movea.l d0,a0                                      ; +$025C6: 2040
    move.l #$00000000,d0                               ; +$025C8: 203C00000000
    move.w 2(a4),d0                                    ; +$025CE: 302C0002
    move.l 64(a2),d1                                   ; +$025D2: 222A0040
    move.l 72(a2),d2                                   ; +$025D6: 242A0048
    move.l #$00000001,d3                               ; +$025DA: 263C00000001
    bsr.w L_BOBS_02AE8                                 ; +$025E0: 61000506
    tst.l d0                                           ; +$025E4: 4A80
    beq.w L_BOBS_02AC4                                 ; +$025E6: 670004DC
L_BOBS_025EA:
padding_ok:
    movea.l 60(a2),a4                                  ; +$025EA: 286A003C
    move.l #$00000000,d0                               ; +$025EE: 203C00000000
    move.w (a4),d0                                     ; +$025F4: 3014
    move.l (a2),d1                                     ; +$025F6: 2212
    cmp.l d1,d0                                        ; +$025F8: B081
    bne.w L_BOBS_02610                                 ; +$025FA: 66000014
    move.l 76(a2),d0                                   ; +$025FE: 202A004C
    move.l 80(a2),d1                                   ; +$02602: 222A0050
    add.l d1,d0                                        ; +$02606: D081
    bcs.w L_BOBS_02AC4                                 ; +$02608: 650004BA
    move.l d0,84(a2)                                   ; +$0260C: 25400054
L_BOBS_02610:
not_replaced_size:
    move.l 60(a2),d0                                   ; +$02610: 202A003C
    addi.l #$00000028,d0                               ; +$02614: 068000000028
    move.l d0,60(a2)                                   ; +$0261A: 2540003C
    move.l 172(a2),d0                                  ; +$0261E: 202A00AC
    addq.l #1,d0                                       ; +$02622: 5280
    move.l d0,172(a2)                                  ; +$02624: 254000AC
    bra.w L_BOBS_023A8                                 ; +$02628: 6000FD7E
L_BOBS_0262C:
old_validated:
    move.l 56(a2),d0                                   ; +$0262C: 202A0038
    move.l 32(a2),d1                                   ; +$02630: 222A0020
    cmp.l d1,d0                                        ; +$02634: B081
    bne.w L_BOBS_02AC4                                 ; +$02636: 6600048C
    movea.l 456(a5),a4                                 ; +$0263A: 286D01C8
    move.l a4,d0                                       ; +$0263E: 200C
    tst.l d0                                           ; +$02640: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02642: 67000480
    move.l a4,124(a2)                                  ; +$02646: 254C007C
    move.l (a4),d0                                     ; +$0264A: 2014
    tst.l d0                                           ; +$0264C: 4A80
    beq.w L_BOBS_02AC4                                 ; +$0264E: 67000474
    move.l 8(a4),d0                                    ; +$02652: 202C0008
    tst.l d0                                           ; +$02656: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02658: 6700046A
    move.l 32(a4),d0                                   ; +$0265C: 202C0020
    tst.l d0                                           ; +$02660: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02662: 67000460
    move.l 12(a4),d0                                   ; +$02666: 202C000C
    cmpi.l #$00000001,d0                               ; +$0266A: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$02670: 65000452
    cmpi.l #$00001000,d0                               ; +$02674: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$0267A: 62000448
    move.l d0,140(a2)                                  ; +$0267E: 2540008C
    move.l 16(a4),d0                                   ; +$02682: 202C0010
    cmpi.l #$00000001,d0                               ; +$02686: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$0268C: 65000436
    cmpi.l #$00001000,d0                               ; +$02690: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$02696: 6200042C
    move.l d0,144(a2)                                  ; +$0269A: 25400090
    move.l 28(a4),d0                                   ; +$0269E: 202C001C
    cmpi.l #$00000001,d0                               ; +$026A2: 0C8000000001
    bcs.w L_BOBS_02AC4                                 ; +$026A8: 6500041A
    cmpi.l #$00000008,d0                               ; +$026AC: 0C8000000008
    bhi.w L_BOBS_02AC4                                 ; +$026B2: 62000410
    move.l d0,108(a2)                                  ; +$026B6: 2540006C
    move.l 12(a2),d0                                   ; +$026BA: 202A000C
    move.l 140(a2),d1                                  ; +$026BE: 222A008C
    cmp.l d1,d0                                        ; +$026C2: B081
    bge.w L_BOBS_02AC4                                 ; +$026C4: 6C0003FE
    move.l 16(a2),d0                                   ; +$026C8: 202A0010
    move.l 144(a2),d1                                  ; +$026CC: 222A0090
    cmp.l d1,d0                                        ; +$026D0: B081
    bge.w L_BOBS_02AC4                                 ; +$026D2: 6C0003F0
    move.l 12(a2),d0                                   ; +$026D6: 202A000C
    move.l 4(a2),d1                                    ; +$026DA: 222A0004
    sub.l d1,d0                                        ; +$026DE: 9081
    addq.l #1,d0                                       ; +$026E0: 5280
    move.l d0,100(a2)                                  ; +$026E2: 25400064
    move.l 16(a2),d0                                   ; +$026E6: 202A0010
    move.l 8(a2),d1                                    ; +$026EA: 222A0008
    sub.l d1,d0                                        ; +$026EE: 9081
    addq.l #1,d0                                       ; +$026F0: 5280
    move.l d0,104(a2)                                  ; +$026F2: 25400068
    move.l 100(a2),d0                                  ; +$026F6: 202A0064
    move.l 104(a2),d1                                  ; +$026FA: 222A0068
    mulu.w d1,d0                                       ; +$026FE: C0C1
    cmpi.l #$00400000,d0                               ; +$02700: 0C8000400000
    bhi.w L_BOBS_02AC4                                 ; +$02706: 620003BC
    move.l 100(a2),d0                                  ; +$0270A: 202A0064
    addi.l #$0000000F,d0                               ; +$0270E: 06800000000F
    lsr.l #4,d0                                        ; +$02714: E888
    lsl.l #1,d0                                        ; +$02716: E388
    move.l d0,112(a2)                                  ; +$02718: 25400070
    move.l 104(a2),d1                                  ; +$0271C: 222A0068
    mulu.w d1,d0                                       ; +$02720: C0C1
    move.l d0,116(a2)                                  ; +$02722: 25400074
    move.l 108(a2),d5                                  ; +$02726: 2A2A006C
    move.l d0,d6                                       ; +$0272A: 2C00
    move.l #$00000000,d0                               ; +$0272C: 203C00000000
L_BOBS_02732:
new_depth_sum:
    add.l d6,d0                                        ; +$02732: D086
    bcs.w L_BOBS_02AC4                                 ; +$02734: 6500038E
    subq.l #1,d5                                       ; +$02738: 5385
    bne.w L_BOBS_02732                                 ; +$0273A: 6600FFF6
    move.l d0,120(a2)                                  ; +$0273E: 25400078
    move.l 36(a2),d0                                   ; +$02742: 202A0024
    move.l 48(a2),d1                                   ; +$02746: 222A0030
    cmpi.l #$00000000,d1                               ; +$0274A: 0C8100000000
    bne.w L_BOBS_02756                                 ; +$02750: 66000004
    addq.l #1,d0                                       ; +$02754: 5280
L_BOBS_02756:
count_done:
    cmpi.l #$00001000,d0                               ; +$02756: 0C8000001000
    bhi.w L_BOBS_02AC4                                 ; +$0275C: 62000366
    move.l d0,88(a2)                                   ; +$02760: 25400058
    mulu.w #$0028,d0                                   ; +$02764: C0FC0028
    addi.l #$00000020,d0                               ; +$02768: 068000000020
    move.l d0,96(a2)                                   ; +$0276E: 25400060
    move.l 32(a2),d0                                   ; +$02772: 202A0020
    move.l 48(a2),d1                                   ; +$02776: 222A0030
    tst.l d1                                           ; +$0277A: 4A81
    bne.w L_BOBS_0278E                                 ; +$0277C: 66000010
    addi.l #$00000028,d0                               ; +$02780: 068000000028
    bcs.w L_BOBS_02AC4                                 ; +$02786: 6500033C
    bra.w L_BOBS_02798                                 ; +$0278A: 6000000C
L_BOBS_0278E:
subtract_old:
    move.l 84(a2),d1                                   ; +$0278E: 222A0054
    sub.l d1,d0                                        ; +$02792: 9081
    bmi.w L_BOBS_02AC4                                 ; +$02794: 6B00032E
L_BOBS_02798:
add_capture:
    move.l 120(a2),d1                                  ; +$02798: 222A0078
    add.l d1,d0                                        ; +$0279C: D081
    bcs.w L_BOBS_02AC4                                 ; +$0279E: 65000324
    cmpi.l #$01000000,d0                               ; +$027A2: 0C8001000000
    bhi.w L_BOBS_02AC4                                 ; +$027A8: 6200031A
    move.l d0,92(a2)                                   ; +$027AC: 2540005C
    movea.l 124(a2),a4                                 ; +$027B0: 286A007C
    movea.l 32(a4),a0                                  ; +$027B4: 206C0020
    move.l a0,128(a2)                                  ; +$027B8: 25480080
    move.l 8(a0),d0                                    ; +$027BC: 20280008
    tst.l d0                                           ; +$027C0: 4A80
    beq.w L_BOBS_027DA                                 ; +$027C2: 67000016
    cmpi.l #$00000001,d0                               ; +$027C6: 0C8000000001
    bne.w L_BOBS_02AC4                                 ; +$027CC: 660002F6
    movea.l 128(a2),a0                                 ; +$027D0: 206A0080
    movea.l (a0),a1                                    ; +$027D4: 2250
    bra.w L_BOBS_027E2                                 ; +$027D6: 6000000A
L_BOBS_027DA:
front_zero:
    movea.l 128(a2),a0                                 ; +$027DA: 206A0080
    movea.l 4(a0),a1                                   ; +$027DE: 22680004
L_BOBS_027E2:
back_found:
    move.l a1,d0                                       ; +$027E2: 2009
    tst.l d0                                           ; +$027E4: 4A80
    beq.w L_BOBS_02AC4                                 ; +$027E6: 670002DC
    movea.l (a1),a0                                    ; +$027EA: 2051
    move.l a0,d0                                       ; +$027EC: 2008
    tst.l d0                                           ; +$027EE: 4A80
    beq.w L_BOBS_02AC4                                 ; +$027F0: 670002D2
    move.l a0,132(a2)                                  ; +$027F4: 25480084
    move.l #$00000000,d0                               ; +$027F8: 203C00000000
    move.w (a0),d0                                     ; +$027FE: 3010
    cmpi.l #$00000002,d0                               ; +$02800: 0C8000000002
    bcs.w L_BOBS_02AC4                                 ; +$02806: 650002BC
    cmpi.l #$0000FFFE,d0                               ; +$0280A: 0C800000FFFE
    bhi.w L_BOBS_02AC4                                 ; +$02810: 620002B2
    move.l d0,d1                                       ; +$02814: 2200
    andi.l #$00000001,d1                               ; +$02816: 028100000001
    bne.w L_BOBS_02AC4                                 ; +$0281C: 660002A6
    move.l d0,136(a2)                                  ; +$02820: 25400088
    lsl.l #3,d0                                        ; +$02824: E788
    move.l 140(a2),d1                                  ; +$02826: 222A008C
    cmp.l d1,d0                                        ; +$0282A: B081
    bcs.w L_BOBS_02AC4                                 ; +$0282C: 65000296
    movea.l 132(a2),a0                                 ; +$02830: 206A0084
    move.l #$00000000,d0                               ; +$02834: 203C00000000
    move.w 2(a0),d0                                    ; +$0283A: 30280002
    move.l 144(a2),d1                                  ; +$0283E: 222A0090
    cmp.l d1,d0                                        ; +$02842: B081
    bcs.w L_BOBS_02AC4                                 ; +$02844: 6500027E
    move.l #$00000000,d0                               ; +$02848: 203C00000000
    move.b 5(a0),d0                                    ; +$0284E: 10280005
    move.l 108(a2),d1                                  ; +$02852: 222A006C
    cmp.l d1,d0                                        ; +$02856: B081
    bne.w L_BOBS_02AC4                                 ; +$02858: 6600026A
    move.l 4(a2),d0                                    ; +$0285C: 202A0004
    lsr.l #3,d0                                        ; +$02860: E688
    move.l 8(a2),d1                                    ; +$02862: 222A0008
    move.l 136(a2),d5                                  ; +$02866: 2A2A0088
    mulu.w d5,d1                                       ; +$0286A: C2C5
    add.l d0,d1                                        ; +$0286C: D280
    bcs.w L_BOBS_02AC4                                 ; +$0286E: 65000254
    move.l d1,148(a2)                                  ; +$02872: 25410094
    move.l 4(a2),d0                                    ; +$02876: 202A0004
    andi.l #$00000007,d0                               ; +$0287A: 028000000007
    move.l d0,152(a2)                                  ; +$02880: 25400098
    movea.l 132(a2),a4                                 ; +$02884: 286A0084
    addq.l #8,a4                                       ; +$02888: 508C
    move.l 108(a2),d6                                  ; +$0288A: 2C2A006C
L_BOBS_0288E:
check_chip_loop:
    move.l (a4)+,d7                                    ; +$0288E: 2E1C
    tst.l d7                                           ; +$02890: 4A87
    beq.w L_BOBS_02AC4                                 ; +$02892: 67000230
    cmpi.l #$FFFFFFFF,d7                               ; +$02896: 0C87FFFFFFFF
    beq.w L_BOBS_02AC4                                 ; +$0289C: 67000226
    move.l d7,d0                                       ; +$028A0: 2007
    andi.l #$00000001,d0                               ; +$028A2: 028000000001
    bne.w L_BOBS_02AC4                                 ; +$028A8: 6600021A
    move.l d7,d0                                       ; +$028AC: 2007
    move.l 148(a2),d1                                  ; +$028AE: 222A0094
    add.l d1,d0                                        ; +$028B2: D081
    bcs.w L_BOBS_02AC4                                 ; +$028B4: 6500020E
    movea.l d0,a1                                      ; +$028B8: 2240
    movea.l $0004.w,a6                                 ; +$028BA: 2C780004
    jsr -534(a6)                                       ; +$028BE: 4EAEFDEA
    andi.l #$00000002,d0                               ; +$028C2: 028000000002
    tst.l d0                                           ; +$028C8: 4A80
    beq.w L_BOBS_02AC4                                 ; +$028CA: 670001F8
    move.l 16(a2),d0                                   ; +$028CE: 202A0010
    move.l 136(a2),d1                                  ; +$028D2: 222A0088
    mulu.w d1,d0                                       ; +$028D6: C0C1
    move.l 12(a2),d1                                   ; +$028D8: 222A000C
    lsr.l #3,d1                                        ; +$028DC: E689
    add.l d1,d0                                        ; +$028DE: D081
    bcs.w L_BOBS_02AC4                                 ; +$028E0: 650001E2
    add.l d7,d0                                        ; +$028E4: D087
    bcs.w L_BOBS_02AC4                                 ; +$028E6: 650001DC
    movea.l d0,a1                                      ; +$028EA: 2240
    movea.l $0004.w,a6                                 ; +$028EC: 2C780004
    jsr -534(a6)                                       ; +$028F0: 4EAEFDEA
    andi.l #$00000002,d0                               ; +$028F4: 028000000002
    tst.l d0                                           ; +$028FA: 4A80
    beq.w L_BOBS_02AC4                                 ; +$028FC: 670001C6
    subq.l #1,d6                                       ; +$02900: 5386
    bne.w L_BOBS_0288E                                 ; +$02902: 6600FF8A
    movea.l 128(a2),a4                                 ; +$02906: 286A0080
    move.l 20(a4),d0                                   ; +$0290A: 202C0014
    andi.l #$00000001,d0                               ; +$0290E: 028000000001
    beq.w L_BOBS_02944                                 ; +$02914: 6700002E
    movea.l 12(a4),a0                                  ; +$02918: 206C000C
    move.l a0,d0                                       ; +$0291C: 2008
    tst.l d0                                           ; +$0291E: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02920: 670001A2
    movea.l $0004.w,a6                                 ; +$02924: 2C780004
    jsr -372(a6)                                       ; +$02928: 4EAEFE8C
    tst.l d0                                           ; +$0292C: 4A80
    beq.w L_BOBS_02AC4                                 ; +$0292E: 67000194
    movea.l 128(a2),a4                                 ; +$02932: 286A0080
    move.l 20(a4),d0                                   ; +$02936: 202C0014
    andi.l #$FFFFFFFE,d0                               ; +$0293A: 0280FFFFFFFE
    move.l d0,20(a4)                                   ; +$02940: 29400014
L_BOBS_02944:
safe_ready:
    movea.l 124(a2),a4                                 ; +$02944: 286A007C
    movea.l 8(a4),a6                                   ; +$02948: 2C6C0008
    jsr -228(a6)                                       ; +$0294C: 4EAEFF1C
    move.l 92(a2),d0                                   ; +$02950: 202A005C
    move.l #$00010001,d1                               ; +$02954: 223C00010001
    movea.l $0004.w,a6                                 ; +$0295A: 2C780004
    jsr -684(a6)                                       ; +$0295E: 4EAEFD54
    tst.l d0                                           ; +$02962: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02964: 6700015E
    move.l d0,156(a2)                                  ; +$02968: 2540009C
    move.l d0,176(a2)                                  ; +$0296C: 254000B0
    movea.l d0,a4                                      ; +$02970: 2840
    move.l #$4147424F,(a4)                             ; +$02972: 28BC4147424F
    move.w #$0001,4(a4)                                ; +$02978: 397C00010004
    move.w #$0000,6(a4)                                ; +$0297E: 397C00000006
    move.l 88(a2),d0                                   ; +$02984: 202A0058
    move.w d0,8(a4)                                    ; +$02988: 39400008
    move.w #$0028,10(a4)                               ; +$0298C: 397C0028000A
    move.l #$00000020,12(a4)                           ; +$02992: 297C00000020000C
    move.l 96(a2),d0                                   ; +$0299A: 202A0060
    move.l d0,16(a4)                                   ; +$0299E: 29400010
    move.l 92(a2),d0                                   ; +$029A2: 202A005C
    move.l d0,20(a4)                                   ; +$029A6: 29400014
    move.l 44(a2),d0                                   ; +$029AA: 202A002C
    addq.l #1,d0                                       ; +$029AE: 5280
    move.l d0,24(a4)                                   ; +$029B0: 29400018
    move.l #$00000000,28(a4)                           ; +$029B4: 297C00000000001C
    move.l 156(a2),d0                                  ; +$029BC: 202A009C
    addi.l #$00000020,d0                               ; +$029C0: 068000000020
    move.l d0,160(a2)                                  ; +$029C6: 254000A0
    move.l 156(a2),d0                                  ; +$029CA: 202A009C
    move.l 96(a2),d1                                   ; +$029CE: 222A0060
    add.l d1,d0                                        ; +$029D2: D081
    bcs.w L_BOBS_02AC4                                 ; +$029D4: 650000EE
    move.l d0,164(a2)                                  ; +$029D8: 254000A4
    move.l #$00000000,168(a2)                          ; +$029DC: 257C0000000000A8
    move.l 24(a2),d0                                   ; +$029E4: 202A0018
    addi.l #$00000020,d0                               ; +$029E8: 068000000020
    move.l d0,60(a2)                                   ; +$029EE: 2540003C
    move.l #$00000000,172(a2)                          ; +$029F2: 257C0000000000AC
L_BOBS_029FA:
build_entries:
    move.l 172(a2),d0                                  ; +$029FA: 202A00AC
    move.l 36(a2),d1                                   ; +$029FE: 222A0024
    cmp.l d1,d0                                        ; +$02A02: B081
    bge.w L_BOBS_02A5E                                 ; +$02A04: 6C000058
    movea.l 60(a2),a4                                  ; +$02A08: 286A003C
    move.l #$00000000,d0                               ; +$02A0C: 203C00000000
    move.w (a4),d0                                     ; +$02A12: 3014
    move.l d0,216(a2)                                  ; +$02A14: 254000D8
    move.l (a2),d1                                     ; +$02A18: 2212
    cmp.l d1,d0                                        ; +$02A1A: B081
    bcs.w L_BOBS_02A32                                 ; +$02A1C: 65000014
    beq.w L_BOBS_02A36                                 ; +$02A20: 67000014
    move.l 168(a2),d0                                  ; +$02A24: 202A00A8
    tst.l d0                                           ; +$02A28: 4A80
    bne.w L_BOBS_02A3E                                 ; +$02A2A: 66000012
    bsr.w L_BOBS_02BE8                                 ; +$02A2E: 610001B8
L_BOBS_02A32:
maybe_insert_before:
    bra.w L_BOBS_02A3E                                 ; +$02A32: 6000000A
L_BOBS_02A36:
replace_here:
    bsr.w L_BOBS_02BE8                                 ; +$02A36: 610001B0
    bra.w L_BOBS_02A42                                 ; +$02A3A: 60000006
L_BOBS_02A3E:
copy_old_entry:
    bsr.w L_BOBS_02B56                                 ; +$02A3E: 61000116
L_BOBS_02A42:
advance_old:
    move.l 60(a2),d0                                   ; +$02A42: 202A003C
    addi.l #$00000028,d0                               ; +$02A46: 068000000028
    move.l d0,60(a2)                                   ; +$02A4C: 2540003C
    move.l 172(a2),d0                                  ; +$02A50: 202A00AC
    addq.l #1,d0                                       ; +$02A54: 5280
    move.l d0,172(a2)                                  ; +$02A56: 254000AC
    bra.w L_BOBS_029FA                                 ; +$02A5A: 6000FF9E
L_BOBS_02A5E:
after_old_entries:
    move.l 168(a2),d0                                  ; +$02A5E: 202A00A8
    tst.l d0                                           ; +$02A62: 4A80
    bne.w L_BOBS_02A6C                                 ; +$02A64: 66000006
    bsr.w L_BOBS_02BE8                                 ; +$02A68: 6100017E
L_BOBS_02A6C:
finished_entries:
    move.l 164(a2),d0                                  ; +$02A6C: 202A00A4
    move.l 156(a2),d1                                  ; +$02A70: 222A009C
    sub.l d1,d0                                        ; +$02A74: 9081
    move.l 92(a2),d1                                   ; +$02A76: 222A005C
    cmp.l d1,d0                                        ; +$02A7A: B081
    bne.w L_BOBS_02AC4                                 ; +$02A7C: 66000046
    movea.l 156(a2),a0                                 ; +$02A80: 206A009C
    move.l 92(a2),d1                                   ; +$02A84: 222A005C
    move.l 20(a2),d3                                   ; +$02A88: 262A0014
    bsr.w L_BOBS_01D38                                 ; +$02A8C: 6100F2AA
    tst.l d3                                           ; +$02A90: 4A83
    beq.w L_BOBS_02AC4                                 ; +$02A92: 67000030
    move.l 20(a2),d0                                   ; +$02A96: 202A0014
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$02A9A: FE11F700031D
    move.l a0,d0                                       ; +$02AA0: 2008
    tst.l d0                                           ; +$02AA2: 4A80
    beq.w L_BOBS_02AC4                                 ; +$02AA4: 6700001E
    lea L_BOBS_020A2(pc),a0                            ; +$02AA8: 41FAF5F8
    move.l d0,4(a0)                                    ; +$02AAC: 21400004
    move.l 28(a2),d1                                   ; +$02AB0: 222A001C
    move.l d1,8(a0)                                    ; +$02AB4: 21410008
    move.l #$00000001,224(a2)                          ; +$02AB8: 257C0000000100E0
    bra.w L_BOBS_02AC4                                 ; +$02AC0: 60000002
L_BOBS_02AC4:
done:
fail:
    movea.l 156(a2),a1                                 ; +$02AC4: 226A009C
    move.l a1,d0                                       ; +$02AC8: 2009
    tst.l d0                                           ; +$02ACA: 4A80
    beq.w L_BOBS_02AD8                                 ; +$02ACC: 6700000A
    movea.l $0004.w,a6                                 ; +$02AD0: 2C780004
    jsr -690(a6)                                       ; +$02AD4: 4EAEFD4E
L_BOBS_02AD8:
no_scratch:
    move.l 224(a2),d3                                  ; +$02AD8: 262A00E0
    lea 320(a7),a7                                     ; +$02ADC: 4FEF0140
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$02AE0: 4CDF77F7
    moveq #0,d2                                        ; +$02AE4: 7400
    rts                                                ; +$02AE6: 4E75
L_BOBS_02AE8:
check_padding:
    move.l d0,d5                                       ; +$02AE8: 2A00
    andi.l #$0000000F,d5                               ; +$02AEA: 02850000000F
    tst.l d5                                           ; +$02AF0: 4A85
    beq.w L_BOBS_02B24                                 ; +$02AF2: 67000030
    move.w #$FFFF,d4                                   ; +$02AF6: 383CFFFF
L_BOBS_02AFA:
padding_shift:
    lsr.w #1,d4                                        ; +$02AFA: E24C
    subq.l #1,d5                                       ; +$02AFC: 5385
    bne.w L_BOBS_02AFA                                 ; +$02AFE: 6600FFFA
    move.l d2,d6                                       ; +$02B02: 2C02
    mulu.w d3,d6                                       ; +$02B04: CCC3
    movea.l a0,a1                                      ; +$02B06: 2248
    adda.l d1,a1                                       ; +$02B08: D3C1
    subq.l #2,a1                                       ; +$02B0A: 5589
L_BOBS_02B0C:
padding_loop:
    move.l #$00000000,d7                               ; +$02B0C: 2E3C00000000
    move.w (a1),d7                                     ; +$02B12: 3E11
    and.w d4,d7                                        ; +$02B14: CE44
    tst.w d7                                           ; +$02B16: 4A47
    bne.w L_BOBS_02B2C                                 ; +$02B18: 66000012
    adda.l d1,a1                                       ; +$02B1C: D3C1
    subq.l #1,d6                                       ; +$02B1E: 5386
    bne.w L_BOBS_02B0C                                 ; +$02B20: 6600FFEA
L_BOBS_02B24:
padding_accept:
    move.l #$00000001,d0                               ; +$02B24: 203C00000001
    rts                                                ; +$02B2A: 4E75
L_BOBS_02B2C:
padding_reject:
    move.l #$00000000,d0                               ; +$02B2C: 203C00000000
    rts                                                ; +$02B32: 4E75
L_BOBS_02B34:
copy_bytes:
    move.l d0,d6                                       ; +$02B34: 2C00
    lsr.l #2,d6                                        ; +$02B36: E48E
    tst.l d6                                           ; +$02B38: 4A86
    beq.w L_BOBS_02B46                                 ; +$02B3A: 6700000A
L_BOBS_02B3E:
copy_long_loop:
    move.l (a0)+,(a1)+                                 ; +$02B3E: 22D8
    subq.l #1,d6                                       ; +$02B40: 5386
    bne.w L_BOBS_02B3E                                 ; +$02B42: 6600FFFA
L_BOBS_02B46:
copy_tail:
    andi.l #$00000002,d0                               ; +$02B46: 028000000002
    tst.l d0                                           ; +$02B4C: 4A80
    beq.w L_BOBS_02B54                                 ; +$02B4E: 67000004
    move.w (a0)+,(a1)+                                 ; +$02B52: 32D8
L_BOBS_02B54:
copy_return:
    rts                                                ; +$02B54: 4E75
L_BOBS_02B56:
emit_copy_old:
    movea.l 60(a2),a0                                  ; +$02B56: 206A003C
    movea.l 160(a2),a1                                 ; +$02B5A: 226A00A0
    move.l #$0000000A,d6                               ; +$02B5E: 2C3C0000000A
L_BOBS_02B64:
copy_entry_longs:
    move.l (a0)+,(a1)+                                 ; +$02B64: 22D8
    subq.l #1,d6                                       ; +$02B66: 5386
    bne.w L_BOBS_02B64                                 ; +$02B68: 6600FFFA
    movea.l 160(a2),a4                                 ; +$02B6C: 286A00A0
    move.l 164(a2),d0                                  ; +$02B70: 202A00A4
    move.l 156(a2),d1                                  ; +$02B74: 222A009C
    sub.l d1,d0                                        ; +$02B78: 9081
    move.l d0,12(a4)                                   ; +$02B7A: 2940000C
    movea.l 60(a2),a0                                  ; +$02B7E: 206A003C
    move.l 16(a0),d5                                   ; +$02B82: 2A280010
    move.l 24(a0),d7                                   ; +$02B86: 2E280018
    tst.l d7                                           ; +$02B8A: 4A87
    beq.w L_BOBS_02BA0                                 ; +$02B8C: 67000012
    move.l 164(a2),d0                                  ; +$02B90: 202A00A4
    add.l d5,d0                                        ; +$02B94: D085
    move.l 156(a2),d1                                  ; +$02B96: 222A009C
    sub.l d1,d0                                        ; +$02B9A: 9081
    move.l d0,20(a4)                                   ; +$02B9C: 29400014
L_BOBS_02BA0:
copied_mask_offset:
    movea.l 60(a2),a0                                  ; +$02BA0: 206A003C
    move.l 24(a2),d0                                   ; +$02BA4: 202A0018
    add.l 12(a0),d0                                    ; +$02BA8: D0A8000C
    movea.l d0,a0                                      ; +$02BAC: 2040
    movea.l 164(a2),a1                                 ; +$02BAE: 226A00A4
    movea.l 60(a2),a4                                  ; +$02BB2: 286A003C
    move.l 16(a4),d0                                   ; +$02BB6: 202C0010
    add.l 24(a4),d0                                    ; +$02BBA: D0AC0018
    bsr.w L_BOBS_02B34                                 ; +$02BBE: 6100FF74
    movea.l 60(a2),a4                                  ; +$02BC2: 286A003C
    move.l 16(a4),d0                                   ; +$02BC6: 202C0010
    add.l 24(a4),d0                                    ; +$02BCA: D0AC0018
    move.l 164(a2),d1                                  ; +$02BCE: 222A00A4
    add.l d0,d1                                        ; +$02BD2: D280
    move.l d1,164(a2)                                  ; +$02BD4: 254100A4
    move.l 160(a2),d1                                  ; +$02BD8: 222A00A0
    addi.l #$00000028,d1                               ; +$02BDC: 068100000028
    move.l d1,160(a2)                                  ; +$02BE2: 254100A0
    rts                                                ; +$02BE6: 4E75
L_BOBS_02BE8:
emit_new_entry:
p1b_join_disp:
    movea.l 160(a2),a4                                 ; +$02BE8: 286A00A0
    move.l (a2),d0                                     ; +$02BEC: 2012
    move.w d0,(a4)                                     ; +$02BEE: 3880
    move.l 100(a2),d0                                  ; +$02BF0: 202A0064
    move.w d0,2(a4)                                    ; +$02BF4: 39400002
    move.l 104(a2),d0                                  ; +$02BF8: 202A0068
    move.w d0,4(a4)                                    ; +$02BFC: 39400004
    move.l 108(a2),d0                                  ; +$02C00: 202A006C
    move.w d0,6(a4)                                    ; +$02C04: 39400006
    move.l 112(a2),d0                                  ; +$02C08: 202A0070
    move.w d0,8(a4)                                    ; +$02C0C: 39400008
    move.w #$0000,10(a4)                               ; +$02C10: 397C0000000A
    move.l 164(a2),d0                                  ; +$02C16: 202A00A4
    move.l 156(a2),d1                                  ; +$02C1A: 222A009C
    sub.l d1,d0                                        ; +$02C1E: 9081
    move.l d0,12(a4)                                   ; +$02C20: 2940000C
    move.l 120(a2),d0                                  ; +$02C24: 202A0078
    move.l d0,16(a4)                                   ; +$02C28: 29400010
    move.l #$00000000,20(a4)                           ; +$02C2C: 297C000000000014
    move.l #$00000000,24(a4)                           ; +$02C34: 297C000000000018
    move.l #$00000000,32(a4)                           ; +$02C3C: 297C000000000020
    move.l #$00000000,36(a4)                           ; +$02C44: 297C000000000024
    move.w #$0000,28(a4)                               ; +$02C4C: 397C0000001C
    move.w #$0000,30(a4)                               ; +$02C52: 397C0000001E
    move.l 132(a2),d0                                  ; +$02C58: 202A0084
    addi.l #$00000008,d0                               ; +$02C5C: 068000000008
    move.l d0,180(a2)                                  ; +$02C62: 254000B4
    move.l 164(a2),d0                                  ; +$02C66: 202A00A4
    move.l d0,188(a2)                                  ; +$02C6A: 254000BC
    move.l 108(a2),d0                                  ; +$02C6E: 202A006C
    move.l d0,200(a2)                                  ; +$02C72: 254000C8
L_BOBS_02C76:
capture_plane:
    movea.l 180(a2),a4                                 ; +$02C76: 286A00B4
    move.l (a4)+,d0                                    ; +$02C7A: 201C
    move.l d0,184(a2)                                  ; +$02C7C: 254000B8
    move.l a4,180(a2)                                  ; +$02C80: 254C00B4
    move.l 188(a2),d0                                  ; +$02C84: 202A00BC
    move.l d0,196(a2)                                  ; +$02C88: 254000C4
    move.l 148(a2),d0                                  ; +$02C8C: 202A0094
    move.l d0,192(a2)                                  ; +$02C90: 254000C0
    move.l 104(a2),d0                                  ; +$02C94: 202A0068
    move.l d0,204(a2)                                  ; +$02C98: 254000CC
L_BOBS_02C9C:
capture_row:
    move.l 184(a2),d0                                  ; +$02C9C: 202A00B8
    move.l 192(a2),d1                                  ; +$02CA0: 222A00C0
    add.l d1,d0                                        ; +$02CA4: D081
    movea.l d0,a0                                      ; +$02CA6: 2040
    movea.l 196(a2),a1                                 ; +$02CA8: 226A00C4
    move.l 152(a2),d1                                  ; +$02CAC: 222A0098
    move.l 100(a2),d7                                  ; +$02CB0: 2E2A0064
L_BOBS_02CB4:
capture_word:
    move.l #$00000010,d3                               ; +$02CB4: 263C00000010
    cmpi.l #$00000010,d7                               ; +$02CBA: 0C8700000010
    bcc.w L_BOBS_02CC6                                 ; +$02CC0: 64000004
    move.l d7,d3                                       ; +$02CC4: 2607
L_BOBS_02CC6:
group_width_ready:
    bfextu (a0){d1:d3},d4                              ; +$02CC6: E9D04863
    bfins d4,(a1){0:d3}                                ; +$02CCA: EFD14023
    addq.l #2,a0                                       ; +$02CCE: 5488
    addq.l #2,a1                                       ; +$02CD0: 5489
    sub.l d3,d7                                        ; +$02CD2: 9E83
    bne.w L_BOBS_02CB4                                 ; +$02CD4: 6600FFDE
    move.l 192(a2),d0                                  ; +$02CD8: 202A00C0
    move.l 136(a2),d1                                  ; +$02CDC: 222A0088
    add.l d1,d0                                        ; +$02CE0: D081
    move.l d0,192(a2)                                  ; +$02CE2: 254000C0
    move.l 196(a2),d0                                  ; +$02CE6: 202A00C4
    move.l 112(a2),d1                                  ; +$02CEA: 222A0070
    add.l d1,d0                                        ; +$02CEE: D081
    move.l d0,196(a2)                                  ; +$02CF0: 254000C4
    move.l 204(a2),d0                                  ; +$02CF4: 202A00CC
    subq.l #1,d0                                       ; +$02CF8: 5380
    move.l d0,204(a2)                                  ; +$02CFA: 254000CC
    bne.w L_BOBS_02C9C                                 ; +$02CFE: 6600FF9C
    move.l 188(a2),d0                                  ; +$02D02: 202A00BC
    move.l 116(a2),d1                                  ; +$02D06: 222A0074
    add.l d1,d0                                        ; +$02D0A: D081
    move.l d0,188(a2)                                  ; +$02D0C: 254000BC
    move.l 200(a2),d0                                  ; +$02D10: 202A00C8
    subq.l #1,d0                                       ; +$02D14: 5380
    move.l d0,200(a2)                                  ; +$02D16: 254000C8
    bne.w L_BOBS_02C76                                 ; +$02D1A: 6600FF5A
    move.l 164(a2),d0                                  ; +$02D1E: 202A00A4
    move.l 120(a2),d1                                  ; +$02D22: 222A0078
    add.l d1,d0                                        ; +$02D26: D081
    move.l d0,164(a2)                                  ; +$02D28: 254000A4
    move.l 160(a2),d0                                  ; +$02D2C: 202A00A0
    addi.l #$00000028,d0                               ; +$02D30: 068000000028
    move.l d0,160(a2)                                  ; +$02D36: 254000A0
    move.l #$00000001,168(a2)                          ; +$02D3A: 257C0000000100A8
    rts                                                ; +$02D42: 4E75
ENTRY_BOBS_02D44:
mask_make_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$02D44: 48E7EFEE
    move.l #$00000001,d0                               ; +$02D48: 203C00000001
    bra.w L_BOBS_02D5C                                 ; +$02D4E: 6000000C
ENTRY_BOBS_02D52:
mask_no_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$02D52: 48E7EFEE
    move.l #$00000000,d0                               ; +$02D56: 203C00000000
L_BOBS_02D5C:
m_start:
    lea -256(a7),a7                                    ; +$02D5C: 4FEFFF00
    movea.l a7,a2                                      ; +$02D60: 244F
    move.l d0,(a2)                                     ; +$02D62: 2480
    move.l #$00000000,88(a2)                           ; +$02D64: 257C000000000058
    move.l #$00000000,140(a2)                          ; +$02D6C: 257C00000000008C
    move.l (a2),d0                                     ; +$02D74: 2012
    tst.l d0                                           ; +$02D76: 4A80
    beq.w L_BOBS_02D8A                                 ; +$02D78: 67000010
    move.l d3,8(a2)                                    ; +$02D7C: 25430008
    move.l (a3)+,d7                                    ; +$02D80: 2E1B
    move.l d7,4(a2)                                    ; +$02D82: 25470004
    bra.w L_BOBS_02D96                                 ; +$02D86: 6000000E
L_BOBS_02D8A:
m_args_no:
    move.l d3,4(a2)                                    ; +$02D8A: 25430004
    move.l #$00000000,8(a2)                            ; +$02D8E: 257C000000000008
L_BOBS_02D96:
m_args_done:
    move.l #$00000000,d3                               ; +$02D96: 263C00000000
    movea.l $0004.w,a0                                 ; +$02D9C: 20780004
    move.l a0,d0                                       ; +$02DA0: 2008
    tst.l d0                                           ; +$02DA2: 4A80
    beq.w L_BOBS_03598                                 ; +$02DA4: 670007F2
    move.w 296(a0),d0                                  ; +$02DA8: 30280128
    btst #1,d0                                         ; +$02DAC: 08000001
    beq.w L_BOBS_03598                                 ; +$02DB0: 670007E6
    move.l 4(a2),d0                                    ; +$02DB4: 202A0004
    cmpi.l #$00000001,d0                               ; +$02DB8: 0C8000000001
    bcs.w L_BOBS_03598                                 ; +$02DBE: 650007D8
    cmpi.l #$00001000,d0                               ; +$02DC2: 0C8000001000
    bhi.w L_BOBS_03598                                 ; +$02DC8: 620007CE
    lea L_BOBS_020A2(pc),a0                            ; +$02DCC: 41FAF2D4
    move.l (a0),d0                                     ; +$02DD0: 2010
    cmpi.l #$00000005,d0                               ; +$02DD2: 0C8000000005
    bcs.w L_BOBS_03598                                 ; +$02DD8: 650007BE
    cmpi.l #$0000FFFF,d0                               ; +$02DDC: 0C800000FFFF
    bhi.w L_BOBS_03598                                 ; +$02DE2: 620007B4
    move.l d0,12(a2)                                   ; +$02DE6: 2540000C
    move.l 4(a0),d0                                    ; +$02DEA: 20280004
    tst.l d0                                           ; +$02DEE: 4A80
    beq.w L_BOBS_03598                                 ; +$02DF0: 670007A6
    move.l d0,16(a2)                                   ; +$02DF4: 25400010
    move.l 8(a0),d0                                    ; +$02DF8: 20280008
    tst.l d0                                           ; +$02DFC: 4A80
    beq.w L_BOBS_03598                                 ; +$02DFE: 67000798
    move.l d0,20(a2)                                   ; +$02E02: 25400014
    move.l 1514(a5),d0                                 ; +$02E06: 202D05EA
    move.l 20(a2),d1                                   ; +$02E0A: 222A0014
    cmp.l d1,d0                                        ; +$02E0E: B081
    bne.w L_BOBS_03598                                 ; +$02E10: 66000786
    move.l 12(a2),d0                                   ; +$02E14: 202A000C
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$02E18: FE11F700031D
    move.l a0,d0                                       ; +$02E1E: 2008
    move.l 16(a2),d1                                   ; +$02E20: 222A0010
    cmp.l d1,d0                                        ; +$02E24: B081
    bne.w L_BOBS_03598                                 ; +$02E26: 66000770
    move.l 16(a2),d0                                   ; +$02E2A: 202A0010
    cmpi.l #$00000018,d0                               ; +$02E2E: 0C8000000018
    bls.w L_BOBS_03598                                 ; +$02E34: 63000762
    move.l d0,d1                                       ; +$02E38: 2200
    andi.l #$00000001,d1                               ; +$02E3A: 028100000001
    bne.w L_BOBS_03598                                 ; +$02E40: 66000756
    movea.l d0,a4                                      ; +$02E44: 2840
    move.l -20(a4),d0                                  ; +$02E46: 202CFFEC
    cmpi.l #$00000030,d0                               ; +$02E4A: 0C8000000030
    bcs.w L_BOBS_03598                                 ; +$02E50: 65000746
    cmpi.l #$01000010,d0                               ; +$02E54: 0C8001000010
    bhi.w L_BOBS_03598                                 ; +$02E5A: 6200073C
    subi.l #$00000010,d0                               ; +$02E5E: 048000000010
    move.l d0,24(a2)                                   ; +$02E64: 25400018
    movea.l 16(a2),a4                                  ; +$02E68: 286A0010
    movea.l a4,a1                                      ; +$02E6C: 224C
    movea.l $0004.w,a6                                 ; +$02E6E: 2C780004
    jsr -534(a6)                                       ; +$02E72: 4EAEFDEA
    tst.l d0                                           ; +$02E76: 4A80
    beq.w L_BOBS_03598                                 ; +$02E78: 6700071E
    move.l 16(a2),d0                                   ; +$02E7C: 202A0010
    move.l 24(a2),d1                                   ; +$02E80: 222A0018
    add.l d1,d0                                        ; +$02E84: D081
    bcs.w L_BOBS_03598                                 ; +$02E86: 65000710
    subq.l #1,d0                                       ; +$02E8A: 5380
    movea.l d0,a1                                      ; +$02E8C: 2240
    movea.l $0004.w,a6                                 ; +$02E8E: 2C780004
    jsr -534(a6)                                       ; +$02E92: 4EAEFDEA
    tst.l d0                                           ; +$02E96: 4A80
    beq.w L_BOBS_03598                                 ; +$02E98: 670006FE
    movea.l 16(a2),a4                                  ; +$02E9C: 286A0010
    move.l -16(a4),d0                                  ; +$02EA0: 202CFFF0
    move.l 12(a2),d1                                   ; +$02EA4: 222A000C
    cmp.l d1,d0                                        ; +$02EA8: B081
    bne.w L_BOBS_03598                                 ; +$02EAA: 660006EC
    move.l #$00000000,d0                               ; +$02EAE: 203C00000000
    move.w -12(a4),d0                                  ; +$02EB4: 302CFFF4
    tst.l d0                                           ; +$02EB8: 4A80
    beq.w L_BOBS_02ECA                                 ; +$02EBA: 6700000E
    andi.w #$FFFD,d0                                   ; +$02EBE: 0240FFFD
    cmpi.w #$0001,d0                                   ; +$02EC2: 0C400001
    bne.w L_BOBS_03598                                 ; +$02EC6: 660006D0
L_BOBS_02ECA:
m_flags_ok:
    move.l -8(a4),d0                                   ; +$02ECA: 202CFFF8
    cmpi.l #$41474142,d0                               ; +$02ECE: 0C8041474142
    bne.w L_BOBS_03598                                 ; +$02ED4: 660006C2
    move.l -4(a4),d0                                   ; +$02ED8: 202CFFFC
    cmpi.l #$4F425320,d0                               ; +$02EDC: 0C804F425320
    bne.w L_BOBS_03598                                 ; +$02EE2: 660006B4
    move.l (a4),d0                                     ; +$02EE6: 2014
    cmpi.l #$4147424F,d0                               ; +$02EE8: 0C804147424F
    bne.w L_BOBS_03598                                 ; +$02EEE: 660006A8
    move.l #$00000000,d0                               ; +$02EF2: 203C00000000
    move.w 4(a4),d0                                    ; +$02EF8: 302C0004
    cmpi.l #$00000001,d0                               ; +$02EFC: 0C8000000001
    bne.w L_BOBS_03598                                 ; +$02F02: 66000694
    tst.w 6(a4)                                        ; +$02F06: 4A6C0006
    bne.w L_BOBS_03598                                 ; +$02F0A: 6600068C
    move.l #$00000000,d0                               ; +$02F0E: 203C00000000
    move.w 8(a4),d0                                    ; +$02F14: 302C0008
    cmpi.l #$00001000,d0                               ; +$02F18: 0C8000001000
    bhi.w L_BOBS_03598                                 ; +$02F1E: 62000678
    move.l d0,28(a2)                                   ; +$02F22: 2540001C
    move.l #$00000000,d0                               ; +$02F26: 203C00000000
    move.w 10(a4),d0                                   ; +$02F2C: 302C000A
    cmpi.l #$00000028,d0                               ; +$02F30: 0C8000000028
    bne.w L_BOBS_03598                                 ; +$02F36: 66000660
    move.l 12(a4),d0                                   ; +$02F3A: 202C000C
    cmpi.l #$00000020,d0                               ; +$02F3E: 0C8000000020
    bne.w L_BOBS_03598                                 ; +$02F44: 66000652
    move.l 28(a2),d0                                   ; +$02F48: 202A001C
    mulu.w #$0028,d0                                   ; +$02F4C: C0FC0028
    addi.l #$00000020,d0                               ; +$02F50: 068000000020
    cmp.l 16(a4),d0                                    ; +$02F56: B0AC0010
    bne.w L_BOBS_03598                                 ; +$02F5A: 6600063C
    move.l 24(a2),d1                                   ; +$02F5E: 222A0018
    cmp.l d1,d0                                        ; +$02F62: B081
    bhi.w L_BOBS_03598                                 ; +$02F64: 62000632
    move.l d0,32(a2)                                   ; +$02F68: 25400020
    move.l 20(a4),d0                                   ; +$02F6C: 202C0014
    move.l 24(a2),d1                                   ; +$02F70: 222A0018
    cmp.l d1,d0                                        ; +$02F74: B081
    bne.w L_BOBS_03598                                 ; +$02F76: 66000620
    move.l 24(a4),d0                                   ; +$02F7A: 202C0018
    tst.l d0                                           ; +$02F7E: 4A80
    beq.w L_BOBS_03598                                 ; +$02F80: 67000616
    move.l d0,36(a2)                                   ; +$02F84: 25400024
    tst.l 28(a4)                                       ; +$02F88: 4AAC001C
    bne.w L_BOBS_03598                                 ; +$02F8C: 6600060A
    move.l 32(a2),d0                                   ; +$02F90: 202A0020
    move.l d0,40(a2)                                   ; +$02F94: 25400028
    move.l 16(a2),d0                                   ; +$02F98: 202A0010
    addi.l #$00000020,d0                               ; +$02F9C: 068000000020
    move.l d0,44(a2)                                   ; +$02FA2: 2540002C
    move.l #$00000000,48(a2)                           ; +$02FA6: 257C000000000030
    move.l #$00000000,52(a2)                           ; +$02FAE: 257C000000000034
    move.l #$00000000,56(a2)                           ; +$02FB6: 257C000000000038
    move.l #$00000000,64(a2)                           ; +$02FBE: 257C000000000040
L_BOBS_02FC6:
m_check_entry:
    move.l 48(a2),d0                                   ; +$02FC6: 202A0030
    move.l 28(a2),d1                                   ; +$02FCA: 222A001C
    cmp.l d1,d0                                        ; +$02FCE: B081
    bge.w L_BOBS_03270                                 ; +$02FD0: 6C00029E
    movea.l 44(a2),a4                                  ; +$02FD4: 286A002C
    move.l #$00000000,d0                               ; +$02FD8: 203C00000000
    move.w (a4),d0                                     ; +$02FDE: 3014
    move.l 52(a2),d1                                   ; +$02FE0: 222A0034
    cmp.l d1,d0                                        ; +$02FE4: B081
    bls.w L_BOBS_03598                                 ; +$02FE6: 630005B0
    cmpi.l #$00001000,d0                               ; +$02FEA: 0C8000001000
    bhi.w L_BOBS_03598                                 ; +$02FF0: 620005A6
    move.l d0,52(a2)                                   ; +$02FF4: 25400034
    move.l #$00000000,d0                               ; +$02FF8: 203C00000000
    move.w 2(a4),d0                                    ; +$02FFE: 302C0002
    cmpi.l #$00000001,d0                               ; +$03002: 0C8000000001
    bcs.w L_BOBS_03598                                 ; +$03008: 6500058E
    cmpi.l #$00001000,d0                               ; +$0300C: 0C8000001000
    bhi.w L_BOBS_03598                                 ; +$03012: 62000584
    move.l d0,100(a2)                                  ; +$03016: 25400064
    move.l #$00000000,d0                               ; +$0301A: 203C00000000
    move.w 4(a4),d0                                    ; +$03020: 302C0004
    cmpi.l #$00000001,d0                               ; +$03024: 0C8000000001
    bcs.w L_BOBS_03598                                 ; +$0302A: 6500056C
    cmpi.l #$00001000,d0                               ; +$0302E: 0C8000001000
    bhi.w L_BOBS_03598                                 ; +$03034: 62000562
    move.l d0,104(a2)                                  ; +$03038: 25400068
    move.l #$00000000,d0                               ; +$0303C: 203C00000000
    move.w 6(a4),d0                                    ; +$03042: 302C0006
    cmpi.l #$00000001,d0                               ; +$03046: 0C8000000001
    bcs.w L_BOBS_03598                                 ; +$0304C: 6500054A
    cmpi.l #$00000008,d0                               ; +$03050: 0C8000000008
    bhi.w L_BOBS_03598                                 ; +$03056: 62000540
    move.l d0,108(a2)                                  ; +$0305A: 2540006C
    move.l 100(a2),d0                                  ; +$0305E: 202A0064
    move.l 104(a2),d1                                  ; +$03062: 222A0068
    mulu.w d1,d0                                       ; +$03066: C0C1
    cmpi.l #$00400000,d0                               ; +$03068: 0C8000400000
    bhi.w L_BOBS_03598                                 ; +$0306E: 62000528
    move.l 100(a2),d0                                  ; +$03072: 202A0064
    addi.l #$0000000F,d0                               ; +$03076: 06800000000F
    lsr.l #4,d0                                        ; +$0307C: E888
    lsl.l #1,d0                                        ; +$0307E: E388
    movea.l 44(a2),a4                                  ; +$03080: 286A002C
    move.l #$00000000,d1                               ; +$03084: 223C00000000
    move.w 8(a4),d1                                    ; +$0308A: 322C0008
    cmp.l d1,d0                                        ; +$0308E: B081
    bne.w L_BOBS_03598                                 ; +$03090: 66000506
    move.l d0,112(a2)                                  ; +$03094: 25400070
    move.l 112(a2),d0                                  ; +$03098: 202A0070
    move.l 104(a2),d1                                  ; +$0309C: 222A0068
    mulu.w d1,d0                                       ; +$030A0: C0C1
    move.l d0,116(a2)                                  ; +$030A2: 25400074
    move.l d0,d6                                       ; +$030A6: 2C00
    move.l 108(a2),d5                                  ; +$030A8: 2A2A006C
    move.l #$00000000,d7                               ; +$030AC: 2E3C00000000
L_BOBS_030B2:
m_sum_planes:
    add.l d6,d7                                        ; +$030B2: DE86
    bcs.w L_BOBS_03598                                 ; +$030B4: 650004E2
    subq.l #1,d5                                       ; +$030B8: 5385
    bne.w L_BOBS_030B2                                 ; +$030BA: 6600FFF6
    movea.l 44(a2),a4                                  ; +$030BE: 286A002C
    move.l 16(a4),d0                                   ; +$030C2: 202C0010
    cmp.l d7,d0                                        ; +$030C6: B087
    bne.w L_BOBS_03598                                 ; +$030C8: 660004CE
    move.l d0,120(a2)                                  ; +$030CC: 25400078
    move.l 40(a2),d0                                   ; +$030D0: 202A0028
    cmp.l 12(a4),d0                                    ; +$030D4: B0AC000C
    bne.w L_BOBS_03598                                 ; +$030D8: 660004BE
    move.l #$00000000,d0                               ; +$030DC: 203C00000000
    move.w 10(a4),d0                                   ; +$030E2: 302C000A
    cmpi.l #$00000001,d0                               ; +$030E6: 0C8000000001
    bne.w L_BOBS_03120                                 ; +$030EC: 66000032
    move.l 116(a2),d1                                  ; +$030F0: 222A0074
    move.l 24(a4),d0                                   ; +$030F4: 202C0018
    cmp.l d1,d0                                        ; +$030F8: B081
    bne.w L_BOBS_03598                                 ; +$030FA: 6600049C
    move.l 40(a2),d0                                   ; +$030FE: 202A0028
    move.l 120(a2),d1                                  ; +$03102: 222A0078
    add.l d1,d0                                        ; +$03106: D081
    bcs.w L_BOBS_03598                                 ; +$03108: 6500048E
    cmp.l 20(a4),d0                                    ; +$0310C: B0AC0014
    bne.w L_BOBS_03598                                 ; +$03110: 66000486
    move.l 116(a2),d0                                  ; +$03114: 202A0074
    move.l d0,124(a2)                                  ; +$03118: 2540007C
    bra.w L_BOBS_0313E                                 ; +$0311C: 60000020
L_BOBS_03120:
m_unmasked:
    tst.l d0                                           ; +$03120: 4A80
    bne.w L_BOBS_03598                                 ; +$03122: 66000474
    tst.l 20(a4)                                       ; +$03126: 4AAC0014
    bne.w L_BOBS_03598                                 ; +$0312A: 6600046C
    tst.l 24(a4)                                       ; +$0312E: 4AAC0018
    bne.w L_BOBS_03598                                 ; +$03132: 66000464
    move.l #$00000000,124(a2)                          ; +$03136: 257C00000000007C
L_BOBS_0313E:
m_mask_checked:
    move.l 40(a2),d0                                   ; +$0313E: 202A0028
    move.l 120(a2),d1                                  ; +$03142: 222A0078
    add.l d1,d0                                        ; +$03146: D081
    bcs.w L_BOBS_03598                                 ; +$03148: 6500044E
    move.l 124(a2),d1                                  ; +$0314C: 222A007C
    add.l d1,d0                                        ; +$03150: D081
    bcs.w L_BOBS_03598                                 ; +$03152: 65000444
    move.l 24(a2),d1                                   ; +$03156: 222A0018
    cmp.l d1,d0                                        ; +$0315A: B081
    bhi.w L_BOBS_03598                                 ; +$0315C: 6200043A
    move.l d0,40(a2)                                   ; +$03160: 25400028
    movea.l 44(a2),a4                                  ; +$03164: 286A002C
    tst.l 32(a4)                                       ; +$03168: 4AAC0020
    bne.w L_BOBS_03598                                 ; +$0316C: 6600042A
    tst.l 36(a4)                                       ; +$03170: 4AAC0024
    bne.w L_BOBS_03598                                 ; +$03174: 66000422
    move.l 16(a2),d0                                   ; +$03178: 202A0010
    movea.l 44(a2),a4                                  ; +$0317C: 286A002C
    add.l 12(a4),d0                                    ; +$03180: D0AC000C
    bcs.w L_BOBS_03598                                 ; +$03184: 65000412
    movea.l d0,a0                                      ; +$03188: 2040
    move.l 100(a2),d0                                  ; +$0318A: 202A0064
    move.l 112(a2),d1                                  ; +$0318E: 222A0070
    move.l 104(a2),d2                                  ; +$03192: 242A0068
    move.l 108(a2),d3                                  ; +$03196: 262A006C
    bsr.w L_BOBS_02AE8                                 ; +$0319A: 6100F94C
    tst.l d0                                           ; +$0319E: 4A80
    beq.w L_BOBS_03598                                 ; +$031A0: 670003F6
    move.l 124(a2),d0                                  ; +$031A4: 202A007C
    tst.l d0                                           ; +$031A8: 4A80
    beq.w L_BOBS_031DC                                 ; +$031AA: 67000030
    move.l 16(a2),d0                                   ; +$031AE: 202A0010
    movea.l 44(a2),a4                                  ; +$031B2: 286A002C
    add.l 20(a4),d0                                    ; +$031B6: D0AC0014
    bcs.w L_BOBS_03598                                 ; +$031BA: 650003DC
    movea.l d0,a0                                      ; +$031BE: 2040
    move.l 100(a2),d0                                  ; +$031C0: 202A0064
    move.l 112(a2),d1                                  ; +$031C4: 222A0070
    move.l 104(a2),d2                                  ; +$031C8: 242A0068
    move.l #$00000001,d3                               ; +$031CC: 263C00000001
    bsr.w L_BOBS_02AE8                                 ; +$031D2: 6100F914
    tst.l d0                                           ; +$031D6: 4A80
    beq.w L_BOBS_03598                                 ; +$031D8: 670003BE
L_BOBS_031DC:
m_padding_ok:
    movea.l 44(a2),a4                                  ; +$031DC: 286A002C
    move.l #$00000000,d0                               ; +$031E0: 203C00000000
    move.w (a4),d0                                     ; +$031E6: 3014
    move.l 4(a2),d1                                    ; +$031E8: 222A0004
    cmp.l d1,d0                                        ; +$031EC: B081
    bne.w L_BOBS_03254                                 ; +$031EE: 66000064
    move.l #$00000001,56(a2)                           ; +$031F2: 257C000000010038
    move.l 100(a2),d0                                  ; +$031FA: 202A0064
    move.l d0,68(a2)                                   ; +$031FE: 25400044
    move.l 104(a2),d0                                  ; +$03202: 202A0068
    move.l d0,72(a2)                                   ; +$03206: 25400048
    move.l 108(a2),d0                                  ; +$0320A: 202A006C
    move.l d0,76(a2)                                   ; +$0320E: 2540004C
    move.l 112(a2),d0                                  ; +$03212: 202A0070
    move.l d0,80(a2)                                   ; +$03216: 25400050
    move.l 116(a2),d0                                  ; +$0321A: 202A0074
    move.l d0,60(a2)                                   ; +$0321E: 2540003C
    move.l 124(a2),d0                                  ; +$03222: 202A007C
    move.l d0,64(a2)                                   ; +$03226: 25400040
    move.l (a2),d0                                     ; +$0322A: 2012
    tst.l d0                                           ; +$0322C: 4A80
    beq.w L_BOBS_03254                                 ; +$0322E: 67000024
    move.l 8(a2),d7                                    ; +$03232: 2E2A0008
    tst.l d7                                           ; +$03236: 4A87
    bmi.w L_BOBS_03598                                 ; +$03238: 6B00035E
    move.l #$00000001,d0                               ; +$0323C: 203C00000001
    move.l 108(a2),d1                                  ; +$03242: 222A006C
L_BOBS_03246:
m_colour_shift:
    lsl.l #1,d0                                        ; +$03246: E388
    subq.l #1,d1                                       ; +$03248: 5381
    bne.w L_BOBS_03246                                 ; +$0324A: 6600FFFA
    cmp.l d0,d7                                        ; +$0324E: BE80
    bcc.w L_BOBS_03598                                 ; +$03250: 64000346
L_BOBS_03254:
m_not_target:
    move.l 44(a2),d0                                   ; +$03254: 202A002C
    addi.l #$00000028,d0                               ; +$03258: 068000000028
    move.l d0,44(a2)                                   ; +$0325E: 2540002C
    move.l 48(a2),d0                                   ; +$03262: 202A0030
    addq.l #1,d0                                       ; +$03266: 5280
    move.l d0,48(a2)                                   ; +$03268: 25400030
    bra.w L_BOBS_02FC6                                 ; +$0326C: 6000FD58
L_BOBS_03270:
m_all_valid:
    move.l 40(a2),d0                                   ; +$03270: 202A0028
    move.l 24(a2),d1                                   ; +$03274: 222A0018
    cmp.l d1,d0                                        ; +$03278: B081
    bne.w L_BOBS_03598                                 ; +$0327A: 6600031C
    move.l 56(a2),d0                                   ; +$0327E: 202A0038
    tst.l d0                                           ; +$03282: 4A80
    beq.w L_BOBS_03598                                 ; +$03284: 67000312
    move.l (a2),d0                                     ; +$03288: 2012
    tst.l d0                                           ; +$0328A: 4A80
    bne.w L_BOBS_032A6                                 ; +$0328C: 66000018
    move.l 64(a2),d0                                   ; +$03290: 202A0040
    tst.l d0                                           ; +$03294: 4A80
    bne.w L_BOBS_032A6                                 ; +$03296: 6600000E
    move.l #$00000001,140(a2)                          ; +$0329A: 257C00000001008C
    bra.w L_BOBS_03598                                 ; +$032A2: 600002F4
L_BOBS_032A6:
m_mutate:
    move.l 36(a2),d0                                   ; +$032A6: 202A0024
    cmpi.l #$FFFFFFFF,d0                               ; +$032AA: 0C80FFFFFFFF
    beq.w L_BOBS_03598                                 ; +$032B0: 670002E6
    move.l 24(a2),d0                                   ; +$032B4: 202A0018
    move.l 64(a2),d1                                   ; +$032B8: 222A0040
    move.l (a2),d2                                     ; +$032BC: 2412
    tst.l d2                                           ; +$032BE: 4A82
    beq.w L_BOBS_032D8                                 ; +$032C0: 67000016
    tst.l d1                                           ; +$032C4: 4A81
    bne.w L_BOBS_032DE                                 ; +$032C6: 66000016
    move.l 60(a2),d1                                   ; +$032CA: 222A003C
    add.l d1,d0                                        ; +$032CE: D081
    bcs.w L_BOBS_03598                                 ; +$032D0: 650002C6
    bra.w L_BOBS_032DE                                 ; +$032D4: 60000008
L_BOBS_032D8:
m_remove_size:
    sub.l d1,d0                                        ; +$032D8: 9081
    bmi.w L_BOBS_03598                                 ; +$032DA: 6B0002BC
L_BOBS_032DE:
m_size_ok:
    cmpi.l #$01000000,d0                               ; +$032DE: 0C8001000000
    bhi.w L_BOBS_03598                                 ; +$032E4: 620002B2
    move.l d0,84(a2)                                   ; +$032E8: 25400054
    move.l #$00000000,d1                               ; +$032EC: 223C00000000
    move.l #$00010001,d1                               ; +$032F2: 223C00010001
    movea.l $0004.w,a6                                 ; +$032F8: 2C780004
    jsr -684(a6)                                       ; +$032FC: 4EAEFD54
    tst.l d0                                           ; +$03300: 4A80
    beq.w L_BOBS_03598                                 ; +$03302: 67000294
    move.l d0,88(a2)                                   ; +$03306: 25400058
    movea.l 16(a2),a0                                  ; +$0330A: 206A0010
    movea.l 88(a2),a1                                  ; +$0330E: 226A0058
    move.l #$00000020,d0                               ; +$03312: 203C00000020
    bsr.w L_BOBS_02B34                                 ; +$03318: 6100F81A
    movea.l 88(a2),a4                                  ; +$0331C: 286A0058
    move.l 84(a2),d0                                   ; +$03320: 202A0054
    move.l d0,20(a4)                                   ; +$03324: 29400014
    move.l 36(a2),d0                                   ; +$03328: 202A0024
    addq.l #1,d0                                       ; +$0332C: 5280
    move.l d0,24(a4)                                   ; +$0332E: 29400018
    move.l 32(a2),d0                                   ; +$03332: 202A0020
    move.l d0,40(a2)                                   ; +$03336: 25400028
    move.l 16(a2),d0                                   ; +$0333A: 202A0010
    addi.l #$00000020,d0                               ; +$0333E: 068000000020
    move.l d0,44(a2)                                   ; +$03344: 2540002C
    move.l 88(a2),d0                                   ; +$03348: 202A0058
    addi.l #$00000020,d0                               ; +$0334C: 068000000020
    move.l d0,92(a2)                                   ; +$03352: 2540005C
    move.l 88(a2),d0                                   ; +$03356: 202A0058
    move.l 32(a2),d1                                   ; +$0335A: 222A0020
    add.l d1,d0                                        ; +$0335E: D081
    bcs.w L_BOBS_03598                                 ; +$03360: 65000236
    move.l d0,96(a2)                                   ; +$03364: 25400060
    move.l #$00000000,48(a2)                           ; +$03368: 257C000000000030
L_BOBS_03370:
m_build_loop:
    move.l 48(a2),d0                                   ; +$03370: 202A0030
    move.l 28(a2),d1                                   ; +$03374: 222A001C
    cmp.l d1,d0                                        ; +$03378: B081
    bge.w L_BOBS_03544                                 ; +$0337A: 6C0001C8
    movea.l 44(a2),a0                                  ; +$0337E: 206A002C
    movea.l 92(a2),a1                                  ; +$03382: 226A005C
    move.l #$00000028,d0                               ; +$03386: 203C00000028
    bsr.w L_BOBS_02B34                                 ; +$0338C: 6100F7A6
    movea.l 92(a2),a4                                  ; +$03390: 286A005C
    move.l 96(a2),d0                                   ; +$03394: 202A0060
    move.l 88(a2),d1                                   ; +$03398: 222A0058
    sub.l d1,d0                                        ; +$0339C: 9081
    move.l d0,12(a4)                                   ; +$0339E: 2940000C
    movea.l 44(a2),a4                                  ; +$033A2: 286A002C
    move.l 16(a4),d0                                   ; +$033A6: 202C0010
    move.l d0,120(a2)                                  ; +$033AA: 25400078
    move.l 24(a4),d0                                   ; +$033AE: 202C0018
    move.l d0,124(a2)                                  ; +$033B2: 2540007C
    move.l 16(a2),d0                                   ; +$033B6: 202A0010
    move.l 40(a2),d1                                   ; +$033BA: 222A0028
    add.l d1,d0                                        ; +$033BE: D081
    bcs.w L_BOBS_03598                                 ; +$033C0: 650001D6
    move.l d0,136(a2)                                  ; +$033C4: 25400088
    movea.l 136(a2),a0                                 ; +$033C8: 206A0088
    movea.l 96(a2),a1                                  ; +$033CC: 226A0060
    move.l 120(a2),d0                                  ; +$033D0: 202A0078
    bsr.w L_BOBS_02B34                                 ; +$033D4: 6100F75E
    movea.l 44(a2),a4                                  ; +$033D8: 286A002C
    move.l #$00000000,d0                               ; +$033DC: 203C00000000
    move.w (a4),d0                                     ; +$033E2: 3014
    move.l 4(a2),d1                                    ; +$033E4: 222A0004
    cmp.l d1,d0                                        ; +$033E8: B081
    bne.w L_BOBS_03480                                 ; +$033EA: 66000094
    move.l (a2),d0                                     ; +$033EE: 2012
    tst.l d0                                           ; +$033F0: 4A80
    beq.w L_BOBS_0345A                                 ; +$033F2: 67000066
    movea.l 92(a2),a4                                  ; +$033F6: 286A005C
    move.w #$0001,10(a4)                               ; +$033FA: 397C0001000A
    move.l 60(a2),d0                                   ; +$03400: 202A003C
    move.l d0,132(a2)                                  ; +$03404: 25400084
    move.l d0,24(a4)                                   ; +$03408: 29400018
    move.l 96(a2),d0                                   ; +$0340C: 202A0060
    move.l 120(a2),d1                                  ; +$03410: 222A0078
    add.l d1,d0                                        ; +$03414: D081
    bcs.w L_BOBS_03598                                 ; +$03416: 65000180
    move.l 88(a2),d1                                   ; +$0341A: 222A0058
    sub.l d1,d0                                        ; +$0341E: 9081
    move.l d0,20(a4)                                   ; +$03420: 29400014
    movea.l 96(a2),a0                                  ; +$03424: 206A0060
    move.l 96(a2),d0                                   ; +$03428: 202A0060
    move.l 120(a2),d1                                  ; +$0342C: 222A0078
    add.l d1,d0                                        ; +$03430: D081
    bcs.w L_BOBS_03598                                 ; +$03432: 65000164
    movea.l d0,a1                                      ; +$03436: 2240
    move.l 68(a2),d0                                   ; +$03438: 202A0044
    move.l 72(a2),d1                                   ; +$0343C: 222A0048
    move.l 76(a2),d2                                   ; +$03440: 242A004C
    move.l 8(a2),d3                                    ; +$03444: 262A0008
    move.l 80(a2),d4                                   ; +$03448: 282A0050
    bsr.w L_BOBS_035BC                                 ; +$0344C: 6100016E
    tst.l d3                                           ; +$03450: 4A83
    beq.w L_BOBS_03598                                 ; +$03452: 67000144
    bra.w L_BOBS_034E2                                 ; +$03456: 6000008A
L_BOBS_0345A:
m_remove_entry_mask:
    movea.l 92(a2),a4                                  ; +$0345A: 286A005C
    move.w #$0000,10(a4)                               ; +$0345E: 397C0000000A
    move.l #$00000000,20(a4)                           ; +$03464: 297C000000000014
    move.l #$00000000,24(a4)                           ; +$0346C: 297C000000000018
    move.l #$00000000,132(a2)                          ; +$03474: 257C000000000084
    bra.w L_BOBS_034E2                                 ; +$0347C: 60000064
L_BOBS_03480:
m_copy_other_mask:
    move.l 124(a2),d0                                  ; +$03480: 202A007C
    move.l d0,132(a2)                                  ; +$03484: 25400084
    tst.l d0                                           ; +$03488: 4A80
    beq.w L_BOBS_034D6                                 ; +$0348A: 6700004A
    move.l 136(a2),d0                                  ; +$0348E: 202A0088
    move.l 120(a2),d1                                  ; +$03492: 222A0078
    add.l d1,d0                                        ; +$03496: D081
    bcs.w L_BOBS_03598                                 ; +$03498: 650000FE
    movea.l d0,a0                                      ; +$0349C: 2040
    move.l 96(a2),d0                                   ; +$0349E: 202A0060
    move.l 120(a2),d1                                  ; +$034A2: 222A0078
    add.l d1,d0                                        ; +$034A6: D081
    bcs.w L_BOBS_03598                                 ; +$034A8: 650000EE
    movea.l d0,a1                                      ; +$034AC: 2240
    move.l 124(a2),d0                                  ; +$034AE: 202A007C
    bsr.w L_BOBS_02B34                                 ; +$034B2: 6100F680
    movea.l 92(a2),a4                                  ; +$034B6: 286A005C
    move.l 96(a2),d0                                   ; +$034BA: 202A0060
    move.l 120(a2),d1                                  ; +$034BE: 222A0078
    add.l d1,d0                                        ; +$034C2: D081
    bcs.w L_BOBS_03598                                 ; +$034C4: 650000D2
    move.l 88(a2),d1                                   ; +$034C8: 222A0058
    sub.l d1,d0                                        ; +$034CC: 9081
    move.l d0,20(a4)                                   ; +$034CE: 29400014
    bra.w L_BOBS_034E2                                 ; +$034D2: 6000000E
L_BOBS_034D6:
m_other_opaque:
    movea.l 92(a2),a4                                  ; +$034D6: 286A005C
    move.l #$00000000,20(a4)                           ; +$034DA: 297C000000000014
L_BOBS_034E2:
m_advance:
    move.l 96(a2),d0                                   ; +$034E2: 202A0060
    move.l 120(a2),d1                                  ; +$034E6: 222A0078
    add.l d1,d0                                        ; +$034EA: D081
    bcs.w L_BOBS_03598                                 ; +$034EC: 650000AA
    move.l 132(a2),d1                                  ; +$034F0: 222A0084
    add.l d1,d0                                        ; +$034F4: D081
    bcs.w L_BOBS_03598                                 ; +$034F6: 650000A0
    move.l d0,96(a2)                                   ; +$034FA: 25400060
    move.l 40(a2),d0                                   ; +$034FE: 202A0028
    move.l 120(a2),d1                                  ; +$03502: 222A0078
    add.l d1,d0                                        ; +$03506: D081
    bcs.w L_BOBS_03598                                 ; +$03508: 6500008E
    move.l 124(a2),d1                                  ; +$0350C: 222A007C
    add.l d1,d0                                        ; +$03510: D081
    bcs.w L_BOBS_03598                                 ; +$03512: 65000084
    move.l d0,40(a2)                                   ; +$03516: 25400028
    move.l 44(a2),d0                                   ; +$0351A: 202A002C
    addi.l #$00000028,d0                               ; +$0351E: 068000000028
    move.l d0,44(a2)                                   ; +$03524: 2540002C
    move.l 92(a2),d0                                   ; +$03528: 202A005C
    addi.l #$00000028,d0                               ; +$0352C: 068000000028
    move.l d0,92(a2)                                   ; +$03532: 2540005C
    move.l 48(a2),d0                                   ; +$03536: 202A0030
    addq.l #1,d0                                       ; +$0353A: 5280
    move.l d0,48(a2)                                   ; +$0353C: 25400030
    bra.w L_BOBS_03370                                 ; +$03540: 6000FE2E
L_BOBS_03544:
m_build_complete:
    move.l 96(a2),d0                                   ; +$03544: 202A0060
    move.l 88(a2),d1                                   ; +$03548: 222A0058
    sub.l d1,d0                                        ; +$0354C: 9081
    move.l 84(a2),d1                                   ; +$0354E: 222A0054
    cmp.l d1,d0                                        ; +$03552: B081
    bne.w L_BOBS_03598                                 ; +$03554: 66000042
    movea.l 88(a2),a0                                  ; +$03558: 206A0058
    move.l 84(a2),d1                                   ; +$0355C: 222A0054
    move.l 12(a2),d3                                   ; +$03560: 262A000C
    bsr.w L_BOBS_01D38                                 ; +$03564: 6100E7D2
    tst.l d3                                           ; +$03568: 4A83
    beq.w L_BOBS_03598                                 ; +$0356A: 6700002C
    move.l 12(a2),d0                                   ; +$0356E: 202A000C
    dc.w $FE11,$F700,AMOS_MAIN_GETADR  ; +$03572: FE11F700031D
    move.l a0,d0                                       ; +$03578: 2008
    tst.l d0                                           ; +$0357A: 4A80
    beq.w L_BOBS_03598                                 ; +$0357C: 6700001A
    lea L_BOBS_020A2(pc),a0                            ; +$03580: 41FAEB20
    move.l d0,4(a0)                                    ; +$03584: 21400004
    move.l 20(a2),d1                                   ; +$03588: 222A0014
    move.l d1,8(a0)                                    ; +$0358C: 21410008
    move.l #$00000001,140(a2)                          ; +$03590: 257C00000001008C
L_BOBS_03598:
m_done:
m_fail:
    movea.l 88(a2),a1                                  ; +$03598: 226A0058
    move.l a1,d0                                       ; +$0359C: 2009
    tst.l d0                                           ; +$0359E: 4A80
    beq.w L_BOBS_035AC                                 ; +$035A0: 6700000A
    movea.l $0004.w,a6                                 ; +$035A4: 2C780004
    jsr -690(a6)                                       ; +$035A8: 4EAEFD4E
L_BOBS_035AC:
m_no_scratch:
    move.l 140(a2),d3                                  ; +$035AC: 262A008C
    lea 256(a7),a7                                     ; +$035B0: 4FEF0100
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$035B4: 4CDF77F7
    moveq #0,d2                                        ; +$035B8: 7400
    rts                                                ; +$035BA: 4E75
L_BOBS_035BC:
mask_kernel:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$035BC: 48E7EFEE
    lea -96(a7),a7                                     ; +$035C0: 4FEFFFA0
    movea.l a7,a2                                      ; +$035C4: 244F
    move.l a0,(a2)                                     ; +$035C6: 2488
    move.l a1,4(a2)                                    ; +$035C8: 25490004
    move.l d0,8(a2)                                    ; +$035CC: 25400008
    move.l d1,12(a2)                                   ; +$035D0: 2541000C
    move.l d2,16(a2)                                   ; +$035D4: 25420010
    move.l d3,20(a2)                                   ; +$035D8: 25430014
    move.l d4,24(a2)                                   ; +$035DC: 25440018
    move.l 8(a2),d0                                    ; +$035E0: 202A0008
    cmpi.l #$00000001,d0                               ; +$035E4: 0C8000000001
    bcs.w L_BOBS_03760                                 ; +$035EA: 65000174
    cmpi.l #$00001000,d0                               ; +$035EE: 0C8000001000
    bhi.w L_BOBS_03760                                 ; +$035F4: 6200016A
    move.l 12(a2),d0                                   ; +$035F8: 202A000C
    cmpi.l #$00000001,d0                               ; +$035FC: 0C8000000001
    bcs.w L_BOBS_03760                                 ; +$03602: 6500015C
    cmpi.l #$00001000,d0                               ; +$03606: 0C8000001000
    bhi.w L_BOBS_03760                                 ; +$0360C: 62000152
    move.l 16(a2),d0                                   ; +$03610: 202A0010
    cmpi.l #$00000001,d0                               ; +$03614: 0C8000000001
    bcs.w L_BOBS_03760                                 ; +$0361A: 65000144
    cmpi.l #$00000008,d0                               ; +$0361E: 0C8000000008
    bhi.w L_BOBS_03760                                 ; +$03624: 6200013A
    move.l (a2),d0                                     ; +$03628: 2012
    tst.l d0                                           ; +$0362A: 4A80
    beq.w L_BOBS_03760                                 ; +$0362C: 67000132
    andi.l #$00000001,d0                               ; +$03630: 028000000001
    bne.w L_BOBS_03760                                 ; +$03636: 66000128
    move.l 4(a2),d0                                    ; +$0363A: 202A0004
    tst.l d0                                           ; +$0363E: 4A80
    beq.w L_BOBS_03760                                 ; +$03640: 6700011E
    andi.l #$00000001,d0                               ; +$03644: 028000000001
    bne.w L_BOBS_03760                                 ; +$0364A: 66000114
    move.l 8(a2),d0                                    ; +$0364E: 202A0008
    move.l 12(a2),d1                                   ; +$03652: 222A000C
    mulu.w d1,d0                                       ; +$03656: C0C1
    cmpi.l #$00400000,d0                               ; +$03658: 0C8000400000
    bhi.w L_BOBS_03760                                 ; +$0365E: 62000100
    move.l 8(a2),d0                                    ; +$03662: 202A0008
    addi.l #$0000000F,d0                               ; +$03666: 06800000000F
    lsr.l #4,d0                                        ; +$0366C: E888
    lsl.l #1,d0                                        ; +$0366E: E388
    move.l 24(a2),d1                                   ; +$03670: 222A0018
    cmp.l d1,d0                                        ; +$03674: B081
    bne.w L_BOBS_03760                                 ; +$03676: 660000E8
    lsr.l #1,d0                                        ; +$0367A: E288
    move.l d0,32(a2)                                   ; +$0367C: 25400020
    move.l 24(a2),d0                                   ; +$03680: 202A0018
    move.l 12(a2),d1                                   ; +$03684: 222A000C
    mulu.w d1,d0                                       ; +$03688: C0C1
    move.l d0,28(a2)                                   ; +$0368A: 2540001C
    move.l 20(a2),d1                                   ; +$0368E: 222A0014
    tst.l d1                                           ; +$03692: 4A81
    bmi.w L_BOBS_03760                                 ; +$03694: 6B0000CA
    move.l #$00000001,d6                               ; +$03698: 2C3C00000001
    move.l 16(a2),d7                                   ; +$0369E: 2E2A0010
L_BOBS_036A2:
    add.l d6,d6                                        ; +$036A2: DC86
    subq.l #1,d7                                       ; +$036A4: 5387
    bne.w L_BOBS_036A2                                 ; +$036A6: 6600FFFA
    cmp.l d6,d1                                        ; +$036AA: B286
    bcc.w L_BOBS_03760                                 ; +$036AC: 640000B2
    move.l 8(a2),d0                                    ; +$036B0: 202A0008
    andi.l #$0000000F,d0                               ; +$036B4: 02800000000F
    lsl.l #1,d0                                        ; +$036BA: E388
    lea L_BOBS_03772(pc),a4                            ; +$036BC: 49FA00B4
    adda.l d0,a4                                       ; +$036C0: D9C0
    move.l #$00000000,d0                               ; +$036C2: 203C00000000
    move.w (a4),d0                                     ; +$036C8: 3014
    move.l d0,44(a2)                                   ; +$036CA: 2540002C
    move.l 12(a2),d0                                   ; +$036CE: 202A000C
    move.l d0,36(a2)                                   ; +$036D2: 25400024
    movea.l (a2),a0                                    ; +$036D6: 2052
    movea.l 4(a2),a1                                   ; +$036D8: 226A0004
L_BOBS_036DC:
    move.l 32(a2),d0                                   ; +$036DC: 202A0020
    move.l d0,40(a2)                                   ; +$036E0: 25400028
L_BOBS_036E4:
    movea.l a0,a4                                      ; +$036E4: 2848
    move.l 28(a2),d4                                   ; +$036E6: 282A001C
    move.l 16(a2),d7                                   ; +$036EA: 2E2A0010
    move.l 20(a2),d5                                   ; +$036EE: 2A2A0014
    move.l #$00000000,d6                               ; +$036F2: 2C3C00000000
L_BOBS_036F8:
    move.l #$00000000,d0                               ; +$036F8: 203C00000000
    move.w (a4),d0                                     ; +$036FE: 3014
    bfextu d5{31:1},d1                                 ; +$03700: E9C517C1
    tst.l d1                                           ; +$03704: 4A81
    beq.w L_BOBS_0370E                                 ; +$03706: 67000006
    eori.w #$FFFF,d0                                   ; +$0370A: 0A40FFFF
L_BOBS_0370E:
    or.w d0,d6                                         ; +$0370E: 8C40
    adda.l d4,a4                                       ; +$03710: D9C4
    lsr.l #1,d5                                        ; +$03712: E28D
    subq.l #1,d7                                       ; +$03714: 5387
    bne.w L_BOBS_036F8                                 ; +$03716: 6600FFE0
    move.l 40(a2),d0                                   ; +$0371A: 202A0028
    cmpi.l #$00000001,d0                               ; +$0371E: 0C8000000001
    bne.w L_BOBS_0372E                                 ; +$03724: 66000008
    move.l 44(a2),d0                                   ; +$03728: 202A002C
    and.w d0,d6                                        ; +$0372C: CC40
L_BOBS_0372E:
    move.w d6,(a1)+                                    ; +$0372E: 32C6
    addq.l #2,a0                                       ; +$03730: 5488
    move.l 40(a2),d0                                   ; +$03732: 202A0028
    subq.l #1,d0                                       ; +$03736: 5380
    move.l d0,40(a2)                                   ; +$03738: 25400028
    bne.w L_BOBS_036E4                                 ; +$0373C: 6600FFA6
    move.l 36(a2),d0                                   ; +$03740: 202A0024
    subq.l #1,d0                                       ; +$03744: 5380
    move.l d0,36(a2)                                   ; +$03746: 25400024
    bne.w L_BOBS_036DC                                 ; +$0374A: 6600FF90
    lea 96(a7),a7                                      ; +$0374E: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$03752: 4CDF77F7
    move.l #$00000001,d3                               ; +$03756: 263C00000001
    moveq #0,d2                                        ; +$0375C: 7400
    rts                                                ; +$0375E: 4E75
L_BOBS_03760:
    lea 96(a7),a7                                      ; +$03760: 4FEF0060
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$03764: 4CDF77F7
    move.l #$00000000,d3                               ; +$03768: 263C00000000
    moveq #0,d2                                        ; +$0376E: 7400
    rts                                                ; +$03770: 4E75
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
img_gate_return:
    move.l 4(a2),d3                                    ; +$06254: 262A0004
    lea 160(a7),a7                                     ; +$06258: 4FEF00A0
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0625C: 4CDF77F7
    moveq #0,d2                                        ; +$06260: 7400
    rts                                                ; +$06262: 4E75
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
b8s1_bank_return:
    move.l 36(a2),d3                                   ; +$07698: 262A0024
    lea 64(a7),a7                                      ; +$0769C: 4FEF0040
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$076A0: 4CDF77F7
    moveq #0,d2                                        ; +$076A4: 7400
    rts                                                ; +$076A6: 4E75
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
    move.l (a4),d3                                     ; +$0E59E: 2614
    move.l #$00000000,d2                               ; +$0E5A0: 243C00000000
    lea 96(a7),a7                                      ; +$0E5A6: 4FEF0060
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6              ; +$0E5AA: 4CDF77F3
    rts                                                ; +$0E5AE: 4E75
L_BOBS_0E5B0:
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5B0: 000000000000000000000000
    dc.b $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00  ; +$0E5BC: 000000000000000000000000
L_BOBS_0E5C8:
    include "M19_P2D_PUBLIC_UPDATE_MC68020.s"
ENTRY_BOBS_0EDD0:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)              ; +$0EDD0: 48E7EFEE
    lea -32(a7),a7                                     ; +$0EDD4: 4FEFFFE0
    move.l d3,d0                                       ; +$0EDD8: 2003
    movea.l a7,a1                                      ; +$0EDDA: 224F
    bsr.w L_BOBS_0EABA                                 ; +$0EDDC: 6100FCDC
    tst.l d3                                           ; +$0EDE0: 4A83
    beq.w L_BOBS_0EDEE                                 ; +$0EDE2: 6700000A
    move.l 4(a7),d3                                    ; +$0EDE6: 262F0004
    bra.w L_BOBS_0EDF4                                 ; +$0EDEA: 60000008
L_BOBS_0EDEE:
    move.l #$FFFF7FFF,d3                               ; +$0EDEE: 263CFFFF7FFF
L_BOBS_0EDF4:
    lea 32(a7),a7                                      ; +$0EDF4: 4FEF0020
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6              ; +$0EDF8: 4CDF77F7
    moveq #0,d2                                        ; +$0EDFC: 7400
    rts                                                ; +$0EDFE: 4E75
