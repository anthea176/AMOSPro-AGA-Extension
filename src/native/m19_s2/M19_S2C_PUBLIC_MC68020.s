; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P1c public Sprite routes, source-derived from qualified S2b.
; Same AP20 ABI and tokens, v5 mixed inline registry, logical IDs 1..64.
; At most three independent 16px pairs, simple or attached.
; No new Swap, no palette write. Root borrow released at every return.
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
I_FRAME equ 180

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
    cmpi.l #304,I_X(a2)
    bhi.w p2i_end
    cmpi.l #255,I_Y(a2)
    bhi.w p2i_end
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_display_mode
    tst.l d0
    beq.w p2i_end
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2i_new
    move.l #-139,I_PHASE(a2)
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    move.l I_REC(a2),d0
    beq.w p2i_new       ; existing root, new logical ID
    movea.l d0,a4
    move.l #-140,I_PHASE(a2)
    cmpi.l #4,I_TYPE(a2)
    beq.w s2c_active
    cmpi.l #15,12(a4)
    bne.w p2i_end
    tst.l 36(a4)
    beq.w p2i_end
    move.l I_IMAGE(a2),d0
    cmp.l 36(a4),d0
    bne.w s2a_change
    move.l #-128,I_PHASE(a2)
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_end
    bra.w p2i_move

p2i_new:
    move.l #-120,I_PHASE(a2)
    ; Resolve the selected live AMOS bank; do not cache its payload.
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_end
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_end
    move.l a0,I_SNAPSHOT(a2)
    move.l 4(a4),d0
    cmpi.l #5,d0
    bcs.w p2i_end
    cmpi.l #65535,d0
    bhi.w p2i_end
    move.l d0,I_BANK(a2)
    move.l d0,I_SNAPSHOT+4(a2)
    dc.w $FE11,$F700,797
    move.l a0,I_SNAPSHOT+8(a2)
    move.l #-121,I_PHASE(a2)
    move.l I_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w p2i_end
    move.l d1,I_SNAPSHOT+12(a2)
    move.l d2,I_SNAPSHOT+16(a2)
    move.l d3,I_SNAPSHOT+20(a2)
    ; Borrow once. A missing local link is never authority over a
    ; nonempty or pending durable root from an earlier execution.
    tst.l I_ROOT(a2)
    bne.s s2b_new_borrowed
    moveq #1,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s s2b_new_root
    bsr.w p2k_root_reason
    bra.w p2i_end
s2b_new_root:
    move.l d0,I_ROOT(a2)
    movea.l d0,a3
    move.l (a3),d0
    or.l 4(a3),d0
    or.l 8(a3),d0
    or.l 12(a3),d0
    or.l 48(a3),d0
    move.l #-123,I_PHASE(a2)
    tst.l d0
    bne.w p2i_end
    movea.l a3,a0
    moveq #0,d0
    bsr.w AGSP_S2B_SCAN
    cmpi.l #7,d1
    bne.w p2i_end
s2b_new_borrowed:
    ; Refuse saturation/pending/conflict before allocating a new frame.
    move.l #-206,I_PHASE(a2)
    moveq #7,d1
    bsr.w s2b_public_pick
    tst.l d0
    beq.w p2i_end
    move.l #-125,I_PHASE(a2)
    lea I_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w p2i_end
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    move.l #-126,I_PHASE(a2)
    bsr.w s2c_prepare_dispatch
    tst.l d0
    beq.w p2i_end
    move.l d0,I_CHIP(a2)
    move.l d1,I_LEN(a2)
    move.l #-127,I_PHASE(a2)
    lea I_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w p2i_private_abort
    bsr.w s2b_public_context_now
    tst.l d0
    beq.w p2i_private_abort
    move.l #-128,I_PHASE(a2)
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_private_abort
    ; Attached palette is common to all pairs; checked before GetSprite.
    moveq #7,d1
    cmpi.l #4,I_TYPE(a2)
    beq.w s2c_pick_palette
    ; Select a compatible palette without changing any ColorMap pen.
    move.l #-150,I_PHASE(a2)
    movea.l I_CHIP(a2),a0
    movea.l I_CM(a2),a1
    movea.l I_GFX(a2),a2
    bsr.w AGSP_S2B_PALETTE_MASK
    movea.l sp,a2
    tst.l d1
    beq.w p2i_private_abort
    move.l #-153,I_PHASE(a2)
    tst.l d0
    beq.w p2i_private_abort
    move.l d0,d1
s2c_pick_palette:
    move.l #-206,I_PHASE(a2)
    bsr.w s2b_public_pick
    tst.l d0
    beq.w p2i_private_abort
    move.l d1,d3         ; chosen even channel, not yet owned
    movea.l I_ROOT(a2),a0
    tst.l (a0)
    bne.s s2b_insert_record
    move.l 16(a0),48(a0)
    move.l a5,4(a0)
    move.l I_STATE(a2),8(a0)
    move.l I_SCREEN(a2),12(a0)
s2b_insert_record:
    move.l #-207,I_PHASE(a2)
    movea.l I_CHIP(a2),a1
    move.l I_ID(a2),d0
    move.l I_BANK(a2),d1
    move.l I_IMAGE(a2),d2
    move.l I_VP(a2),d4
    cmpi.l #4,I_TYPE(a2)
    bne.s s2c_insert_simple
    move.l I_LEN(a2),d5
    movea.l I_GFX(a2),a2
    bsr.w AGSP_S2C_INSERT_ATTACHED
    movea.l sp,a2
    bra.s s2c_inserted
s2c_insert_simple:
    bsr.w AGSP_S2B_INSERT
s2c_inserted:
    tst.l d0
    beq.w p2i_private_abort
    move.l d0,I_REC(a2)
    movea.l I_CELL(a2),a0
    move.l I_ROOT(a2),(a0) ; publish registry link before OS acquisition
    movea.l d0,a0
    movea.l I_GFX(a2),a1
    cmpi.l #4,I_TYPE(a2)
    beq.w s2c_acquire_public
    bsr.w AGSP_S2B_ACQUIRE
    tst.l d0
    bne.s s2b_acquired
    move.l d1,I_PHASE(a2)
    bra.w p2i_retire_failed
s2b_acquired:
    ; GetSprite can change global sprite width. Re-check the context,
    ; bank snapshot and this pair's actual palette before ChangeSprite.
    move.l #-127,I_PHASE(a2)
    lea I_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w p2i_retire_failed
    bsr.w s2b_public_context_now
    tst.l d0
    beq.w p2i_retire_failed
    cmpi.l #4,I_TYPE(a2)
    beq.w s2c_show_public
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_retire_failed
    movea.l I_REC(a2),a4
    movea.l I_CHIP(a2),a3
    moveq #15,d0
    move.l d0,12(a4)       ; sticky publication attempt BEFORE call
    movea.l I_GFX(a2),a6
    movea.l I_VP(a2),a0
    movea.l a3,a1
    lea 48(a3),a2
    jsr -420(a6)
    movea.l sp,a2
    move.l #-160,I_PHASE(a2)
    movea.l I_CHIP(a2),a1
    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    bne.w p2i_retire_failed
p2i_move:
    move.l #-160,I_PHASE(a2)
    bsr.w p2i_active
    tst.l d0
    beq.w p2i_retire_failed
    movea.l I_GFX(a2),a6
    movea.l I_VP(a2),a0
    movea.l I_CHIP(a2),a1
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    jsr -426(a6)          ; MoveSprite, no implicit Swap or VBL
    moveq #1,d0
    move.l d0,I_RESULT(a2)
    bra.w p2i_end
s2b_public_pick:
    movea.l I_GFX(a2),a0
    moveq #0,d2
    move.b 166(a0),d2
    movea.l I_ROOT(a2),a0
    move.l I_ID(a2),d0
    bra.w AGSP_S2B_PICK
s2b_public_context_now:
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
p2i_retire_failed:
    bsr.w p2m_release_record
    bra.w p2i_end
p2i_private_abort:
    ; The prepared block has never entered a published record.
    movea.l $0004.w,a6
    move.l I_CHIP(a2),d0
    beq.s s2b_abort_context
    movea.l d0,a1
    jsr -690(a6)
s2b_abort_context:
    movea.l I_ROOT(a2),a0
    tst.l (a0)
    bne.s p2i_leave_only
    clr.l 4(a0)
    clr.l 8(a0)
    clr.l 12(a0)
    clr.l 48(a0)
p2i_leave_only:
    bra.w p2i_end

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
    move.l #212,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.w #212,18(a0)
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
    move.l (a4),I_CHIP(a2)
    move.l 4(a4),I_LEN(a2)
    move.l 44(a4),I_TYPE(a2)
s2b_live_absent:
    moveq #1,d0
    rts
p2i_geometry:
    movea.l I_CHIP(a2),a0
    cmpi.l #4,I_TYPE(a2)
    beq.s s2c_geometry_attached
    tst.l 24(a0)             ; zero hotspot only, proven capture path
    bne.w p2i_no
    bra.s s2c_geometry_height
s2c_geometry_attached:
    tst.l 36(a0)
    bne.w p2i_no
s2c_geometry_height:
    moveq #0,d0
    move.w 4(a0),d0
    beq.w p2i_no
    add.l I_Y(a2),d0
    cmpi.l #256,d0
    bhi.w p2i_no
    moveq #1,d0
    rts
p2i_palette:
    ; Probe the same VideoControl GET tags as P2b; no SET call.
    move.l #-150,I_PHASE(a2)
    lea I_TAG(a2),a1
    move.l #$80000028,(a1)
    move.l #$6a5a5a5a,4(a1)
    move.l #$80000029,8(a1)
    move.l #$6a5a5a5a,12(a1)
    move.l #$80000032,16(a1)
    move.l #$6a5a5a5a,20(a1)
    move.l #$80000034,24(a1)
    move.l #$6a5a5a5a,28(a1)
    clr.l 32(a1)
    clr.l 36(a1)
    movea.l I_CM(a2),a0
    movea.l I_GFX(a2),a6
    jsr -708(a6)
    tst.l d0
    bne.w p2i_no
    move.l #-151,I_PHASE(a2)
    cmpi.l #16,I_TAG+4(a2)
    bne.w p2i_no
    cmpi.l #16,I_TAG+12(a2)
    bne.w p2i_no
    cmpi.l #255,I_TAG+20(a2)
    bne.w p2i_no
    cmpi.l #4,I_TAG+28(a2)
    bne.w p2i_no
    move.l #-152,I_PHASE(a2)
    movea.l I_CM(a2),a0
    cmpi.b #1,18(a0)
    bne.w p2i_no
    move.l #-153,I_PHASE(a2)
    lea I_TAG(a2),a1
    movea.l I_REC(a2),a4
    move.l 40(a4),d0
    add.l d0,d0
    addi.l #17,d0       ; pair 2/4/6 -> 21/25/29
    moveq #3,d1
    jsr -900(a6)
    lea I_TAG(a2),a0
    movea.l I_CHIP(a2),a1
    adda.w #31,a1
    moveq #8,d0
p2i_rgb:
    move.b (a0),d1
    cmp.b (a1)+,d1
    bne.w p2i_no
    adda.w #4,a0
    dbra d0,p2i_rgb
    moveq #1,d0
    rts
p2i_active:
    ; Documented SimpleSprite fields and our exact GetSprite receipts.
    ; Do NOT assume the private table/Copper has been populated before
    ; the first MoveSprite. No new DMA publication through private fields.
    movea.l I_REC(a2),a0
    cmpi.l #15,12(a0)
    bne.w p2i_no
    movea.l I_CHIP(a2),a1
    move.l 40(a0),d0
    cmp.w 10(a1),d0
    bne.w p2i_no
    addq.l #1,d0
    cmp.w 26(a0),d0
    bne.w p2i_no
    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    beq.s s2a_active_ok
    move.l a1,d0
    add.l 44(a1),d0
    bcs.w p2i_no
    cmp.l (a1),d0
    bne.w p2i_no
s2a_active_ok:
    moveq #1,d0
    rts
p2i_no:
    moveq #0,d0
    rts
p2i_gfx_name:
    dc.b "graphics.library",0
    even

; The snapshot was validated by AGSP_I_EXPECT; no OS call until the
; selected depth's own full validator. Never retry as a different type.
s2c_prepare_dispatch:
    movem.l d4/a4,-(sp)
    moveq #0,d4
    move.w 8(a0),d4
    beq.s s2c_prepare_no
    subq.w #1,d4
    lea 32(a0),a4
s2c_prepare_find:
    cmp.w (a4),d1
    beq.s s2c_prepare_found
    bcs.s s2c_prepare_no
    adda.w #48,a4
    dbra d4,s2c_prepare_find
    bra.s s2c_prepare_no
s2c_prepare_found:
    cmpi.w #2,6(a4)
    bne.s s2c_prepare_attached
    move.l #2,I_TYPE(a2)
    movem.l (sp)+,d4/a4
    bra.w AGSP_P2A_PREPARE
s2c_prepare_attached:
    cmpi.w #4,6(a4)
    bne.s s2c_prepare_no
    move.l #4,I_TYPE(a2)
    movem.l (sp)+,d4/a4
    bra.w AGSP_S2C_PREPARE_PAIR
s2c_prepare_no:
    movem.l (sp)+,d4/a4
    moveq #0,d0
    moveq #0,d1
    rts

s2c_acquire_public:
    bsr.w AGSP_S2C_ACQUIRE
    tst.l d0
    bne.w s2b_acquired
    move.l #-208,I_PHASE(a2)
    cmpi.l #2,d1
    bne.w p2i_retire_failed
    move.l #-153,I_PHASE(a2)
    bra.w p2i_retire_failed
s2c_show_public:
    move.l #-208,I_PHASE(a2)
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a1
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    bsr.w AGSP_S2C_SHOW
    tst.l d0
    beq.w p2i_retire_failed
    bra.w p2i_success
s2c_active:
    cmpi.l #31,12(a4)
    bne.w p2i_end
    tst.l 36(a4)
    beq.w p2i_end
    move.l #-128,I_PHASE(a2)
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_IMAGE(a2),d0
    cmp.l 36(a4),d0
    bne.s s2c_change_public
    move.l #-209,I_PHASE(a2)
    movea.l a4,a0
    movea.l I_GFX(a2),a1
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    bsr.w AGSP_S2C_MOVE
    tst.l d0
    bne.w p2i_success
    bra.w s2c_active_failed
s2c_change_public:
    clr.l S_SCRATCH(a2)
    move.l #-201,I_PHASE(a2)
    bsr.w s2a_bank
    tst.l d0
    beq.w p2i_end
    movea.l I_CHIP(a2),a0
    move.l I_SNAPSHOT+16(a2),d0
    cmp.l 32(a0),d0
    bne.w p2i_end
    bsr.w s2a_expect
    tst.l d0
    beq.w p2i_end
    move.l #-202,I_PHASE(a2)
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    bsr.w AGSP_S2C_PREPARE_PAIR
    tst.l d0
    beq.w p2i_end
    move.l d0,S_SCRATCH(a2)
    move.l d1,S_LENGTH(a2)
    move.l #-201,I_PHASE(a2)
    bsr.w s2a_expect
    tst.l d0
    beq.w s2a_abort
    bsr.w s2b_public_context_now
    tst.l d0
    beq.w s2a_abort
    move.l #-209,I_PHASE(a2)
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a1
    movea.l a2,a3
    move.l S_LENGTH(a2),d0
    movea.l S_SCRATCH(a2),a2
    bsr.w AGSP_S2C_CHANGE
    movea.l sp,a2
    move.l d0,d7
    bsr.w s2a_free_scratch
    tst.l d7
    bne.w p2i_success
s2c_active_failed:
    ; Refused before publication: keep old visible frame. Uncertain
    ; OS publication: use common retirement, never private FreeVec.
    movea.l I_REC(a2),a4
    cmpi.l #31,12(a4)
    beq.w p2i_end
    bra.w p2i_retire_failed
