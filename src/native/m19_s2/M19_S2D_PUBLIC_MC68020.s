; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P3 private source candidate. Existing three public functions,
; exact AP20 integer ABI. All sprite widths use the ExtSprite lifecycle.
; One width per lifetime with active records, three pairs, zero hotspot.
; Source snapshots never persist as pointers. Two frame allocations
; retained for fast alternating animation, third image uses guarded drop.
; Off/Bank Free/Close/End share the same v6 registry and retire/reclaim.
    bra.w p2i_sprite
    bra.w p2i_off
    bra.w p2i_bank_free

I_ID equ 0
I_X equ 4
I_Y equ 8
I_IMAGE equ 12
I_ARGS equ 16
I_RESULT equ 20
I_STATE equ 24
I_CELL equ 28
I_SCREEN equ 32
I_VP equ 36
I_GFX equ 40
I_CM equ 44
I_ROOT equ 48
I_REC equ 52
I_CHIP equ 56
I_LEN equ 60
I_BANK equ 64
I_SNAPSHOT equ 68
I_TAG equ 92
I_PHASE equ 132
I_KIND equ 136
S_SCRATCH equ 140
S_LENGTH equ 144
S_OLD equ 148
S_NEW equ 152
S_VIEW equ 156
S_CI equ 160
S_TABLE equ 164
S_LOF equ 168
S_SHF equ 172
I_TYPE equ 176
W_WIDTH equ 180
W_HEIGHT equ 184
W_COLORS equ 188
W_PAL equ 192
W_E equ 240
W_O equ 244
W_B0 equ 248
W_B1 equ 252
W_SLOT equ 256
W_CH equ 260
W_CWIDTH equ 264
W_RGB equ 268
I_FRAME equ 448


p2i_sprite:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_IMAGE(a2)
    move.l (a3)+,I_Y(a2)
    move.l (a3)+,I_X(a2)
    move.l (a3)+,I_ID(a2)
    move.l a3,I_ARGS(a2)
    bsr.w p2i_init
    move.l #1,I_KIND(a2)
    move.l #-101,I_PHASE(a2)
    tst.l d0
    beq.w p2i_end
    move.l #-102,I_PHASE(a2)
    cmpi.l #1,I_IMAGE(a2)
    bcs.w p2i_end
    cmpi.l #4096,I_IMAGE(a2)
    bhi.w p2i_end
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_display_mode
    tst.l d0
    beq.w p2i_end
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.s s2d_pub_new_root
    move.l #-139,I_PHASE(a2)
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    tst.l I_REC(a2)
    bne.w s2d_pub_active
    bra.s s2d_pub_new
s2d_pub_new_root:
    moveq #1,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s s2d_pub_borrowed
    bsr.w p2k_root_reason
    bra.w p2i_end
s2d_pub_borrowed:
    move.l d0,I_ROOT(a2)
    movea.l d0,a0
    move.l (a0),d0
    or.l 4(a0),d0
    or.l 8(a0),d0
    or.l 12(a0),d0
    or.l 48(a0),d0
    move.l #-123,I_PHASE(a2)
    tst.l d0
    bne.w p2i_end
    moveq #0,d0
    bsr.w AGSP_S2B_SCAN
    cmpi.l #7,d1
    bne.w p2i_end
s2d_pub_new:
    move.l #-120,I_PHASE(a2)
    bsr.w s2d_pub_bank
    tst.l d0
    beq.w p2i_end
    move.l #-128,I_PHASE(a2)
    bsr.w s2d_pub_geometry
    tst.l d0
    beq.w p2i_end
    move.l #-206,I_PHASE(a2)
    bsr.w s2d_pub_pick
    tst.l d0
    beq.w p2i_end
    move.l #-126,I_PHASE(a2)
    bsr.w s2d_pub_prepare
    tst.l d0
    beq.w s2d_pub_private
    movea.l I_GFX(a2),a6
    move.l W_WIDTH(a2),d0
    move.l I_TYPE(a2),d1
    bsr.w AGSP_S2D_ALLOC_BLANK_PAIR
    move.l d0,W_B0(a2)
    move.l d1,W_B1(a2)
    tst.l d0
    beq.w s2d_pub_private
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w s2d_pub_private
    bsr.w s2d_pub_context_now
    tst.l d0
    beq.w s2d_pub_private
    ; Recheck the chosen palette after OS allocations, before ownership.
    bsr.w s2d_pub_palette
    tst.l d0
    beq.w s2d_pub_private
    movea.l I_ROOT(a2),a0
    tst.l (a0)
    bne.s s2d_pub_owner
    move.l 16(a0),48(a0)
    move.l a5,4(a0)
    move.l I_STATE(a2),8(a0)
    move.l I_SCREEN(a2),12(a0)
s2d_pub_owner:
    movea.l W_SLOT(a2),a4
    movea.l I_GFX(a2),a6
    move.l a6,(a4)
    move.l W_B0(a2),4(a4)
    move.l W_B1(a2),8(a4)
    move.l W_WIDTH(a2),12(a4)
    move.l I_TYPE(a2),16(a4)
    move.l W_CH(a2),20(a4)
    move.l W_CWIDTH(a2),28(a4)
    move.l I_VP(a2),36(a4)
    move.l 34(a6),40(a4)
    move.l 38(a6),44(a4)
    move.l 208(a6),48(a4)
    move.l W_E(a2),52(a4)
    move.l W_O(a2),56(a4)
    move.l W_HEIGHT(a2),60(a4)
    move.l I_CM(a2),64(a4)
    move.l 50(a6),88(a4)
    move.l 54(a6),92(a4)
    move.l I_ID(a2),W_R_ID(a4)
    move.l I_BANK(a2),W_R_BANK(a4)
    move.l I_IMAGE(a2),W_R_IMAGE(a4)
    move.l I_SNAPSHOT+16(a2),W_R_GEN(a4)
    move.l W_COLORS(a2),W_R_COLORS(a4)
    lea W_PAL(a2),a0
    lea W_R_PAL(a4),a1
    moveq #11,d0
s2d_pub_save_palette:
    move.l (a0)+,(a1)+
    dbra d0,s2d_pub_save_palette
    move.l a4,I_REC(a2)
    movea.l I_ROOT(a2),a0
    addq.l #1,(a0)
    movea.l I_CELL(a2),a1
    move.l a0,(a1)
    ; Ownership transferred into persistent receipt before any Get.
    clr.l W_E(a2)
    clr.l W_O(a2)
    clr.l W_B0(a2)
    clr.l W_B1(a2)
    move.l #-208,I_PHASE(a2)
    movea.l a4,a0
    bsr.w AGSP_S2D_ACQUIRE_BLANK_PAIR
    tst.l d0
    beq.w s2d_pub_retire_failed
    bsr.w s2d_pub_context_now
    tst.l d0
    beq.w s2d_pub_retire_failed
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w s2d_pub_retire_failed
    bsr.w s2d_pub_palette
    tst.l d0
    beq.w s2d_pub_retire_failed
    ; Width negotiation may rebuild list starts. Accept only if
    ; View, CopInit and descriptor table still match the receipt.
    movea.l I_REC(a2),a4
    movea.l I_GFX(a2),a6
    move.l 34(a6),d0
    cmp.l 40(a4),d0
    bne.w s2d_pub_retire_failed
    move.l 38(a6),d0
    cmp.l 44(a4),d0
    bne.w s2d_pub_retire_failed
    move.l 208(a6),d0
    cmp.l 48(a4),d0
    bne.w s2d_pub_retire_failed
    move.l 50(a6),88(a4)
    move.l 54(a6),92(a4)
    movea.l a4,a0
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    bsr.w AGSP_S2D_EXT_FIRST_SHOW
    tst.l d0
    beq.w s2d_pub_retire_failed
    bra.w p2i_success

s2d_pub_active:
    movea.l I_REC(a2),a4
    cmpi.l #31,24(a4)
    bne.w p2i_end
    move.l 12(a4),W_WIDTH(a2)
    move.l 16(a4),I_TYPE(a2)
    move.l 20(a4),W_CH(a2)
    move.l 60(a4),W_HEIGHT(a2)
    move.l W_R_COLORS(a4),W_COLORS(a2)
    lea W_R_PAL(a4),a0
    lea W_PAL(a2),a1
    moveq #11,d0
s2d_pub_load_palette:
    move.l (a0)+,(a1)+
    dbra d0,s2d_pub_load_palette
    move.l #-128,I_PHASE(a2)
    bsr.w s2d_pub_geometry
    tst.l d0
    beq.w p2i_end
    move.l #-153,I_PHASE(a2)
    bsr.w s2d_pub_palette
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_IMAGE(a2),d0
    cmp.l W_R_IMAGE(a4),d0
    beq.w s2d_pub_move
    move.l #-201,I_PHASE(a2)
    bsr.w s2d_pub_bank
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_BANK(a2),d0
    cmp.l W_R_BANK(a4),d0
    bne.w p2i_end
    move.l I_SNAPSHOT+16(a2),d0
    cmp.l W_R_GEN(a4),d0
    bne.w p2i_end
    move.l W_WIDTH(a2),d0
    cmp.l 12(a4),d0
    bne.w p2i_end
    move.l W_HEIGHT(a2),d0
    cmp.l 60(a4),d0
    bne.w p2i_end
    move.l I_TYPE(a2),d0
    cmp.l 16(a4),d0
    bne.w p2i_end
    move.l W_COLORS(a2),d0
    cmp.l W_R_COLORS(a4),d0
    bne.w p2i_end
    lea W_PAL(a2),a0
    lea W_R_PAL(a4),a1
    moveq #11,d0
s2d_pub_same_palette:
    cmpm.l (a0)+,(a1)+
    bne.w p2i_end
    dbra d0,s2d_pub_same_palette
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    tst.l 80(a4)
    beq.s s2d_pub_stage_new
    move.l W_R_STAGE(a4),d0
    cmp.l I_IMAGE(a2),d0
    beq.s s2d_pub_exchange
    movea.l a4,a0
    movea.l I_GFX(a2),a6
    bsr.w AGSP_S2D_EXT_DROP_STAGE
    tst.l d0
    beq.w s2d_pub_active_failed
    clr.l W_R_STAGE(a4)
s2d_pub_stage_new:
    move.l #-202,I_PHASE(a2)
    bsr.w s2d_pub_prepare
    tst.l d0
    beq.w s2d_pub_private
    bsr.w s2d_pub_context_now
    tst.l d0
    beq.w s2d_pub_private
    bsr.w s2d_pub_palette
    tst.l d0
    beq.w s2d_pub_private
    movea.l I_REC(a2),a4
    move.l W_E(a2),72(a4)
    move.l W_O(a2),76(a4)
    move.l I_IMAGE(a2),W_R_STAGE(a4)
    move.l #1,80(a4)
    clr.l W_E(a2)
    clr.l W_O(a2)
s2d_pub_exchange:
    move.l #-209,I_PHASE(a2)
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a6
    bsr.w AGSP_S2D_EXT_EXCHANGE
    tst.l d0
    beq.w s2d_pub_active_failed
    movea.l I_REC(a2),a4
    move.l W_R_IMAGE(a4),d0
    move.l W_R_STAGE(a4),W_R_IMAGE(a4)
    move.l d0,W_R_STAGE(a4)
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w s2d_pub_retire_failed
s2d_pub_move:
    move.l #-209,I_PHASE(a2)
    bsr.w s2d_pub_palette
    tst.l d0
    beq.w s2d_pub_retire_failed
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a6
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    bsr.w AGSP_S2D_EXT_MOVE
    tst.l d0
    beq.w s2d_pub_active_failed
    bra.w p2i_success
s2d_pub_active_failed:
    movea.l I_REC(a2),a4
    cmpi.l #31,24(a4)
    beq.w p2i_end
s2d_pub_retire_failed:
    bsr.w p2m_release_record
    bra.w p2i_end

s2d_pub_private:
    ; Only pointers never transferred into a published receipt.
    movea.l I_GFX(a2),a6
    lea W_E(a2),a4
    moveq #3,d7
s2d_pub_private_loop:
    move.l (a4),d0
    beq.s s2d_pub_private_next
    movea.l d0,a2
    clr.l (a4)
    jsr -1032(a6)
    movea.l sp,a2
s2d_pub_private_next:
    addq.l #4,a4
    dbra d7,s2d_pub_private_loop
    bra.w p2i_end

; Resolve selection as in S2c, then copy exact validated image metadata.
s2d_pub_bank:
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_no
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_no
    move.l a0,I_SNAPSHOT(a2)
    move.l 4(a4),d0
    cmpi.l #5,d0
    bcs.w p2i_no
    cmpi.l #65535,d0
    bhi.w p2i_no
    move.l d0,I_BANK(a2)
    move.l d0,I_SNAPSHOT+4(a2)
    dc.w $FE11,$F700,797
    move.l a0,I_SNAPSHOT+8(a2)
    move.l I_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w p2i_no
    move.l d1,I_SNAPSHOT+12(a2)
    move.l d2,I_SNAPSHOT+16(a2)
    move.l d3,I_SNAPSHOT+20(a2)
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w p2i_no
    movea.l I_SNAPSHOT+8(a2),a0
    moveq #0,d0
    move.w 8(a0),d0
    beq.w p2i_no
    subq.w #1,d0
    lea 32(a0),a4
    move.l I_IMAGE(a2),d1
s2d_pub_find:
    cmp.w (a4),d1
    beq.s s2d_pub_found
    bcs.w p2i_no
    adda.w #48,a4
    dbra d0,s2d_pub_find
    bra.w p2i_no
s2d_pub_found:
    tst.l 28(a4)
    bne.w p2i_no
    moveq #0,d0
    move.w 2(a4),d0
    move.l d0,W_WIDTH(a2)
    moveq #0,d0
    move.w 4(a4),d0
    move.l d0,W_HEIGHT(a2)
    moveq #0,d0
    move.w 6(a4),d0
    move.l d0,I_TYPE(a2)
    moveq #0,d0
    move.w 32(a4),d0
    move.l d0,W_COLORS(a2)
    adda.l 20(a4),a0
    lea W_PAL(a2),a1
    moveq #11,d0
s2d_pub_copy_pal:
    move.l (a0)+,(a1)+
    dbra d0,s2d_pub_copy_pal
    moveq #1,d0
    rts
s2d_pub_expect:
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_no
    move.l I_BANK(a2),d0
    cmp.l 4(a4),d0
    bne.w p2i_no
    move.l I_SNAPSHOT(a2),d0
    cmp.l 8(a4),d0
    bne.w p2i_no
    lea I_SNAPSHOT(a2),a0
    bra.w AGSP_I_EXPECT
s2d_pub_prepare:
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w p2i_no
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    movea.l I_GFX(a2),a6
    bsr.w AGSP_S2D_PREPARE_EXT
    move.l d0,W_E(a2)
    move.l d1,W_O(a2)
    tst.l d0
    beq.w p2i_no
    bra.w s2d_pub_expect

s2d_pub_geometry:
    move.l #320,d0
    sub.l W_WIDTH(a2),d0
    cmp.l I_X(a2),d0
    bcs.w p2i_no
    move.l #256,d0
    sub.l W_HEIGHT(a2),d0
    cmp.l I_Y(a2),d0
    bcs.w p2i_no
    moveq #1,d0
    rts

s2d_pub_pick:
    movea.l I_ROOT(a2),a0
    move.l I_ID(a2),d0
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.w p2i_no
    tst.l d0
    bne.w p2i_no
    move.l d1,d6
    beq.w p2i_no
    clr.l W_CWIDTH(a2)
    lea 52(a0),a4
    moveq #2,d7
s2d_pub_check_peer:
    tst.l W_R_ID(a4)
    beq.s s2d_pub_peer_next
    cmpi.l #31,24(a4)
    bne.w p2i_no
    move.l W_WIDTH(a2),d0
    cmp.l 12(a4),d0
    bne.w p2i_no
    move.l d0,W_CWIDTH(a2)
s2d_pub_peer_next:
    lea W_REC_BYTES(a4),a4
    dbra d7,s2d_pub_check_peer
    movea.l I_ROOT(a2),a0
    lea 52(a0),a4
    moveq #0,d7
s2d_pub_pick_loop:
    btst d7,d6
    beq.s s2d_pub_pick_next
    move.l d7,d0
    add.l d0,d0
    addq.l #2,d0
    move.l d0,W_CH(a2)
    movea.l I_GFX(a2),a6
    moveq #3,d1
    lsl.l d0,d1
    and.b 166(a6),d1
    bne.s s2d_pub_pick_next
    move.l a4,W_SLOT(a2)
    bsr.w s2d_pub_palette
    tst.l d0
    bne.s s2d_pub_pick_ok
s2d_pub_pick_next:
    lea W_REC_BYTES(a4),a4
    addq.l #1,d7
    cmpi.l #3,d7
    bcs.s s2d_pub_pick_loop
    bra.w p2i_no
s2d_pub_pick_ok:
    moveq #1,d0
    rts

; Palette contract: exact RGB for used attached colors, all three
; simple colors (canonical zero padding included), no SET tags.
s2d_pub_palette:
    movem.l d2-d7/a0-a1/a4/a6,-(sp)
    lea W_RGB(a2),a4
    move.l #$80000028,(a4)
    move.l #$6a5a5a5a,4(a4)
    move.l #$80000029,8(a4)
    move.l #$6a5a5a5a,12(a4)
    move.l #$80000032,16(a4)
    move.l #$6a5a5a5a,20(a4)
    move.l #$80000034,24(a4)
    move.l #$6a5a5a5a,28(a4)
    clr.l 32(a4)
    clr.l 36(a4)
    movea.l I_CM(a2),a0
    movea.l a4,a1
    movea.l I_GFX(a2),a6
    jsr -708(a6)
    tst.l d0
    bne.s s2d_pub_pal_no
    cmpi.l #16,4(a4)
    bne.s s2d_pub_pal_no
    cmpi.l #16,12(a4)
    bne.s s2d_pub_pal_no
    cmpi.l #255,20(a4)
    bne.s s2d_pub_pal_no
    cmpi.l #4,28(a4)
    bne.s s2d_pub_pal_no
    movea.l I_CM(a2),a0
    cmpi.b #1,18(a0)
    bne.s s2d_pub_pal_no
    moveq #17,d0
    move.l W_COLORS(a2),d7
    cmpi.l #4,I_TYPE(a2)
    beq.s s2d_pub_pal_rgb
    move.l W_CH(a2),d0
    add.l d0,d0
    addi.l #17,d0
    moveq #3,d7
s2d_pub_pal_rgb:
    move.l d7,d1
    movea.l a4,a1
    jsr -900(a6)
    mulu.w #3,d7
    subq.w #1,d7
    lea W_PAL+3(a2),a1
s2d_pub_pal_loop:
    move.b (a4),d0
    cmp.b (a1)+,d0
    bne.s s2d_pub_pal_no
    adda.w #4,a4
    dbra d7,s2d_pub_pal_loop
    moveq #1,d0
    bra.s s2d_pub_pal_return
s2d_pub_pal_no:
    moveq #0,d0
s2d_pub_pal_return:
    movem.l (sp)+,d2-d7/a0-a1/a4/a6
    rts
s2d_pub_context_now:
    move.l 456(a5),d0
    cmp.l I_STATE(a2),d0
    bne.w p2i_no
    movea.l d0,a0
    move.l (a0),d0
    cmp.l I_SCREEN(a2),d0
    bne.w p2i_no
    move.l 8(a0),d0
    cmp.l I_GFX(a2),d0
    bne.w p2i_no
    movea.l I_VP(a2),a0
    cmpi.w #$5000,32(a0)
    bne.w p2i_no
    tst.l 12(a0)
    bne.w p2i_no
    tst.l 20(a0)
    bne.w p2i_no
    move.l I_CM(a2),d0
    cmp.l 4(a0),d0
    bne.w p2i_no
    moveq #1,d0
    rts

p2i_off:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_ID(a2)
    move.l a3,I_ARGS(a2)
    bsr.w p2i_init
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_end
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2k_off_unlinked
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    ; Lookup of an absent ID is a valid idempotent Off.
    bsr.w p2i_retire
    bra.w p2i_end

p2k_off_unlinked:
    ; A missing link must not turn an active orphan into a false Off PASS.
    moveq #0,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s p2k_off_found
    cmpi.l #1,d1
    beq.w p2i_success
    bra.w p2i_end
p2k_off_found:
    move.l d0,I_ROOT(a2)
    movea.l d0,a0
    move.l I_SCREEN(a2),d0
    cmp.l 12(a0),d0
    beq.w p2i_end
    bra.w p2i_success

p2i_bank_free:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_BANK(a2)
    move.l a3,I_ARGS(a2)
    clr.l I_ID(a2)
    bsr.w p2i_zero
    cmpi.l #5,I_BANK(a2)
    bcs.w p2i_end
    cmpi.l #65535,I_BANK(a2)
    bhi.w p2i_end
    ; Clear only this owner's matching selection; never Erase DATA.
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.s p2i_bf_context
    move.l I_BANK(a2),d0
    cmp.l 4(a4),d0
    bne.s p2i_bf_context
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_end
    clr.l (a4)
    clr.l 4(a4)
    clr.l 8(a4)
p2i_bf_context:
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_bf_pending
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2i_bf_pending
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    movea.l I_ROOT(a2),a0
    movea.l I_GFX(a2),a1
    moveq #3,d0
    move.l I_BANK(a2),d1
    bsr.w AGSP_S2B_DRAIN
    bsr.w s2b_unlink_empty
    move.l d0,I_RESULT(a2)
    bra.w p2i_end
p2i_bf_pending:
    ; Recovery after successful CloseScreen whose channel retirement fence was pending.
    ; No screen/VP dereference and no new Chip allocation.
    moveq #0,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s p2i_bf_have
    cmpi.l #1,d1
    beq.w p2i_success
    bra.w p2i_end
p2i_bf_have:
    move.l d0,I_ROOT(a2)
    movea.l d0,a3
    tst.l (a3)
    beq.s p2i_bf_empty
    tst.l 12(a3)
    bne.w p2i_leave_only
    movea.l $0004.w,a6
    lea p2i_gfx_name(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.w p2i_leave_only
    move.l d0,I_GFX(a2)
    movea.l I_ROOT(a2),a0
    movea.l d0,a1
    moveq #4,d0
    move.l I_BANK(a2),d1
    bsr.w AGSP_S2B_DRAIN
    move.l d0,I_RESULT(a2)
    movea.l $0004.w,a6
    movea.l I_GFX(a2),a1
    jsr -414(a6)
    bra.w p2i_leave_only
p2i_bf_empty:
    moveq #1,d0
    move.l d0,I_RESULT(a2)
    bra.w p2i_leave_only

p2i_success:
    moveq #1,d0
    move.l d0,I_RESULT(a2)
p2i_end:
    movea.l I_ROOT(a2),a0
    move.l a0,d0
    beq.s p2k_no_borrow
    bsr.w s2b_p2h_leave
    tst.l d0
    bne.s p2k_no_borrow
    clr.l I_RESULT(a2)
    move.l #-137,I_PHASE(a2) ; release refused: never report success
p2k_no_borrow:
    move.l I_RESULT(a2),d3
    bne.w p2j_result_ready
    tst.l I_KIND(a2)
    beq.w p2j_result_ready
    move.l I_PHASE(a2),d3
p2j_result_ready:
    movea.l I_ARGS(a2),a3
    lea I_FRAME(sp),sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

p2i_retire:
    bsr.w p2m_release_record
    move.l d0,I_RESULT(a2)
    rts
p2m_release_record:
    movea.l I_ROOT(a2),a0
    movea.l I_GFX(a2),a1
    moveq #2,d0
    move.l I_ID(a2),d1
    bsr.w AGSP_S2B_DRAIN
s2b_unlink_empty:
    ; Keep every remaining receipt linked. Empty root may be removed by Leave.
    tst.l d0
    beq.s p2m_release_return
    movea.l I_ROOT(a2),a0
    tst.l (a0)
    bne.s p2m_release_return
    movea.l I_CELL(a2),a0
    clr.l (a0)
p2m_release_return:
    rts
p2i_init:
    bsr.w p2i_zero
    cmpi.l #1,I_ID(a2)
    bcs.w p2i_no
    cmpi.l #64,I_ID(a2)
    bhi.w p2i_no
    moveq #1,d0
    rts
p2i_zero:
    clr.l I_TYPE(a2)
    clr.l I_KIND(a2)
    clr.l I_PHASE(a2)
    clr.l I_RESULT(a2)
    clr.l I_ROOT(a2)
    clr.l I_REC(a2)
    clr.l I_CHIP(a2)
    clr.l W_E(a2)
    clr.l W_O(a2)
    clr.l W_B0(a2)
    clr.l W_B1(a2)
    rts

p2i_context:
    ; Same relocated AGA State anchor as P0e cross-unit bridge.
    move.l #-110,I_PHASE(a2)
    movea.l 456(a5),a0
    moveq #40,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l a0,I_STATE(a2)
    move.l #-111,I_PHASE(a2)
    move.l a0,d0
    addi.l #P2I_CELL_DELTA,d0
    bcs.w p2i_no
    movea.l d0,a0
    moveq #16,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.l #$41475349,4(a0)
    bne.w p2i_no
    cmpi.l #$00010010,8(a0)
    bne.w p2i_no
    move.l a0,I_CELL(a2)
    move.l #-112,I_PHASE(a2)
    movea.l I_STATE(a2),a4
    movea.l (a4),a0
    moveq #84,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l a0,I_SCREEN(a2)
    lea 44(a0),a0
    move.l a0,I_VP(a2)
    move.l #-113,I_PHASE(a2)
    movea.l 8(a4),a0
    move.l #450,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.w #450,18(a0)
    bcs.w p2i_no
    cmpi.w #1032,16(a0)
    bcs.w p2i_no
    cmpi.w #39,20(a0)
    bcs.w p2i_no
    cmpi.w #40,20(a0)
    bhi.w p2i_no
    move.l a0,I_GFX(a2)
    moveq #1,d0
    rts
p2i_display_mode:
    move.l #-114,I_PHASE(a2)
    movea.l I_STATE(a2),a0
    cmpi.l #320,12(a0)
    bne.w p2i_no
    cmpi.l #256,16(a0)
    bne.w p2i_no
    cmpi.l #256,20(a0)
    bne.w p2i_no
    move.l #-115,I_PHASE(a2)
    movea.l I_VP(a2),a0
    cmpi.w #$5000,32(a0)
    bne.w p2i_no
    tst.l 20(a0)             ; no user Copper list in S1
    bne.w p2i_no
    move.l #-116,I_PHASE(a2)
    movea.l 4(a0),a0
    moveq #52,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.b #2,1(a0)
    bne.w p2i_no
    cmpi.w #256,2(a0)
    bne.w p2i_no
    move.l a0,I_CM(a2)
    moveq #1,d0
    rts
p2k_root_reason:
    neg.l d1
    subi.l #130,d1
    move.l d1,I_PHASE(a2) ; -131..-136; -137 is leave failure
    rts
p2i_live:
    ; Validate the registry by name BEFORE dereferencing an unlocked link.
    movea.l I_CELL(a2),a0
    movea.l (a0),a3
    moveq #0,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s p2k_live_borrowed
    bsr.w p2k_root_reason
    bra.w p2i_no
p2k_live_borrowed:
    move.l d0,I_ROOT(a2) ; even mismatched links must release this borrow
    cmp.l a3,d0
    bne.w p2i_no
    movea.l d0,a3
    move.l 16(a3),d0
    cmp.l 48(a3),d0     ; lifetime owner, not merely semaphore owner
    bne.w p2i_no
    move.l a5,d0
    cmp.l 4(a3),d0
    bne.w p2i_no
    move.l I_STATE(a2),d0
    cmp.l 8(a3),d0
    bne.w p2i_no
    move.l I_SCREEN(a2),d0
    cmp.l 12(a3),d0
    bne.w p2i_no
    movea.l a3,a0
    move.l I_ID(a2),d0
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.w p2i_no
    move.l d0,I_REC(a2)
    beq.s s2b_live_absent
    movea.l d0,a4
s2b_live_absent:
    moveq #1,d0
    rts
p2i_no:
    moveq #0,d0
    rts
p2i_gfx_name:
    dc.b "graphics.library",0
    even
