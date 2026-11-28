; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P2c3: P2c2 entries plus retire (+12), reclaim (+16).
; Same pinned 96-byte record. +84 becomes a sticky retirement journal:
; bit31 started, bits0/1 original confirmed ownership mask.
; Inputs A0 record, A6 pinned graphics.library V39/V40. Caller owns all
; exact detached allocations and keeps them alive until reclaim. A complete
; record is prepared before first Get; optional staged frame may be absent.
; Caller holds registry borrow and excludes asynchronous release/republication
; of our channels, and guarantees the current View/VP chain is safe for OS.
; Retire returns 2/0 private, 1/0 retired, 0/1 invalid, 0/2 pending.
; Quarantine never guesses ownership. Consume receipts before FreeSprite.
; Only confirmed owned channels released (odd then even); check original
; released channels neutral; all eight table/CopInit refs exclude all owned
; descriptor and used Chip spans; two WaitTOF with stable list snapshots.
; Current VP need not equal old VP, but CopInit/table must match snapshots.
; Reclaim only private or retired records, rechecks samples for retired,
; calls FreeSpriteData once per distinct allocation, clears receipt ptrs.
; state32 terminal: no second reclaim. No direct OS/hardware writes.
; Scope: source-derived modeled OS proof, not universal DMA retirement.
    bra.w AGSP_S2D_EXT_FIRST_SHOW
    bra.w AGSP_S2D_EXT_MOVE
    bra.w AGSP_S2D_EXT_EXCHANGE
    bra.w AGSP_S2D_EXT_RETIRE
    bra.w AGSP_S2D_EXT_RECLAIM

AGSP_S2D_EXT_RETIRE:
    movem.l d2-d7/a0-a6,-(sp)
    subq.l #8,sp
    movea.l a0,a3
    movea.l a6,a5
    bsr.w s2d_r_validate
    tst.l d0
    beq.w s2d_r_bad
    tst.l 24(a3)
    beq.w s2d_r_private
    cmpi.l #20,24(a3)
    beq.w s2d_r_done
    bsr.w s2d_r_mask
    tst.l d0
    beq.w s2d_r_bad
    move.l 50(a5),(sp)
    move.l 54(a5),4(sp)
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
    move.l d3,d0
    ori.l #$80000000,d0
    move.l d0,84(a3)
    btst #1,d2
    beq.s s2d_r_even
    bclr #1,d2
    move.l d2,d0
    ori.l #4,d0
    move.l d0,24(a3)      ; consume receipt before the OS call
    move.l d6,d0
    addq.l #1,d0
    jsr -414(a6)
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
s2d_r_even:
    btst #0,d2
    beq.s s2d_r_fence
    bclr #0,d2
    move.l #4,24(a3)
    move.l d6,d0
    jsr -414(a6)
s2d_r_fence:
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
    bsr.w s2d_r_no_refs
    tst.l d0
    beq.w s2d_r_pending
    jsr -270(a6)
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
    bsr.w s2d_r_no_refs
    tst.l d0
    beq.w s2d_r_pending
    jsr -270(a6)
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
    bsr.w s2d_r_no_refs
    tst.l d0
    beq.w s2d_r_pending
    move.l #20,24(a3)
s2d_r_done:
    moveq #1,d0
    moveq #0,d1
    bra.w s2d_r_return
s2d_r_private:
    tst.l 84(a3)
    bne.w s2d_r_bad
    moveq #2,d0
    moveq #0,d1
    bra.w s2d_r_return

AGSP_S2D_EXT_RECLAIM:
    movem.l d2-d7/a0-a6,-(sp)
    subq.l #8,sp
    movea.l a0,a3
    movea.l a6,a5
    bsr.w s2d_r_validate
    tst.l d0
    beq.w s2d_r_bad
    tst.l 24(a3)
    bne.s s2d_r_reclaim_retired
    tst.l 84(a3)
    bne.w s2d_r_bad
    cmpi.l #1,80(a3)
    bhi.w s2d_r_bad
    bra.s s2d_r_reclaim_start
s2d_r_reclaim_retired:
    cmpi.l #20,24(a3)
    bne.w s2d_r_bad
    bsr.w s2d_r_mask
    tst.l d0
    beq.w s2d_r_bad
    move.l 50(a5),(sp)
    move.l 54(a5),4(sp)
    movea.l sp,a0
    bsr.w s2d_r_verify
    tst.l d0
    beq.w s2d_r_pending
    bsr.w s2d_r_no_refs
    tst.l d0
    beq.w s2d_r_pending
s2d_r_reclaim_start:
    move.l #32,24(a3)       ; terminal before any void OS free
    move.l 4(a3),d0
    beq.s s2d_r_free_skip_4
    movea.l d0,a2
    clr.l 4(a3)
    jsr -1032(a6)
s2d_r_free_skip_4:
    move.l 8(a3),d0
    beq.s s2d_r_free_skip_8
    movea.l d0,a2
    clr.l 8(a3)
    jsr -1032(a6)
s2d_r_free_skip_8:
    move.l 52(a3),d0
    beq.s s2d_r_free_skip_52
    movea.l d0,a2
    clr.l 52(a3)
    jsr -1032(a6)
s2d_r_free_skip_52:
    move.l 56(a3),d0
    beq.s s2d_r_free_skip_56
    movea.l d0,a2
    clr.l 56(a3)
    jsr -1032(a6)
s2d_r_free_skip_56:
    move.l 72(a3),d0
    beq.s s2d_r_free_skip_72
    movea.l d0,a2
    clr.l 72(a3)
    jsr -1032(a6)
s2d_r_free_skip_72:
    move.l 76(a3),d0
    beq.s s2d_r_free_skip_76
    movea.l d0,a2
    clr.l 76(a3)
    jsr -1032(a6)
s2d_r_free_skip_76:
    clr.l 80(a3)
    bra.w s2d_r_done
s2d_r_bad:
    moveq #1,d1
    bra.s s2d_r_fail
s2d_r_pending:
    moveq #2,d1
s2d_r_fail:
    moveq #0,d0
s2d_r_return:
    addq.l #8,sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Structural validation without assuming a live or uncorrupted ATTACH bit.
; Exact allocation provenance/disjointness remains a caller obligation.
s2d_r_validate:
    movea.l a3,a0
    moveq #95,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    cmpa.l (a3),a5
    bne.w s2d_c_no
    tst.l 32(a3)
    bne.w s2d_c_no
    tst.l 68(a3)
    bne.w s2d_c_no
    move.l 24(a3),d0
    beq.s s2d_r_state_ok
    cmpi.l #4,d0
    beq.s s2d_r_state_ok
    cmpi.l #5,d0
    beq.s s2d_r_state_ok
    cmpi.l #7,d0
    beq.s s2d_r_state_ok
    cmpi.l #15,d0
    beq.s s2d_r_state_ok
    cmpi.l #20,d0
    beq.s s2d_r_state_ok
    cmpi.l #31,d0
    bne.w s2d_c_no
s2d_r_state_ok:
    move.l 12(a3),d4
    cmpi.l #16,d4
    beq.s s2d_r_width
    cmpi.l #32,d4
    beq.s s2d_r_width
    cmpi.l #64,d4
    bne.w s2d_c_no
s2d_r_width:
    lsr.l #4,d4
    move.l 16(a3),d5
    cmpi.l #2,d5
    beq.s s2d_r_kind
    cmpi.l #4,d5
    bne.w s2d_c_no
s2d_r_kind:
    move.l 20(a3),d6
    cmpi.l #2,d6
    beq.s s2d_r_channel
    cmpi.l #4,d6
    beq.s s2d_r_channel
    cmpi.l #6,d6
    bne.w s2d_c_no
s2d_r_channel:
    move.l 60(a3),d7
    beq.w s2d_c_no
    cmpi.l #256,d7
    bhi.w s2d_c_no
    movea.l a5,a0
    move.l #449,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    cmpi.w #450,18(a5)
    bcs.w s2d_c_no
    cmpi.w #1032,16(a5)
    bcs.w s2d_c_no
    cmpi.w #39,20(a5)
    bcs.w s2d_c_no
    cmpi.w #40,20(a5)
    bhi.w s2d_c_no
    cmpi.l #4,d5
    bne.s s2d_r_required
    cmpi.w #40,20(a5)
    bcs.w s2d_c_no
s2d_r_required:
    tst.l 4(a3)
    beq.w s2d_c_no
    tst.l 8(a3)
    beq.w s2d_c_no
    tst.l 52(a3)
    beq.w s2d_c_no
    cmpi.l #4,d5
    beq.s s2d_r_require_att
    tst.l 56(a3)
    bne.w s2d_c_no
    tst.l 76(a3)
    bne.w s2d_c_no
    bra.s s2d_r_stage
s2d_r_require_att:
    tst.l 56(a3)
    beq.w s2d_c_no
s2d_r_stage:
    move.l 80(a3),d0
    cmpi.l #3,d0
    bhi.w s2d_c_no
    tst.l d0
    bne.s s2d_r_stage_present
    tst.l 72(a3)
    bne.w s2d_c_no
    tst.l 76(a3)
    bne.w s2d_c_no
    bra.s s2d_r_check_allocs
s2d_r_stage_present:
    tst.l 72(a3)
    beq.w s2d_c_no
    cmpi.l #4,d5
    bne.s s2d_r_check_allocs
    tst.l 76(a3)
    beq.w s2d_c_no
s2d_r_check_allocs:
    move.l 4(a3),d0
    beq.s s2d_r_skip_alloc_4
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_4:
    move.l 8(a3),d0
    beq.s s2d_r_skip_alloc_8
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_8:
    move.l 52(a3),d0
    beq.s s2d_r_skip_alloc_52
    movea.l d0,a0
    move.l d7,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_52:
    move.l 56(a3),d0
    beq.s s2d_r_skip_alloc_56
    movea.l d0,a0
    move.l d7,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_56:
    move.l 72(a3),d0
    beq.s s2d_r_skip_alloc_72
    movea.l d0,a0
    move.l d7,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_72:
    move.l 76(a3),d0
    beq.s s2d_r_skip_alloc_76
    movea.l d0,a0
    move.l d7,d0
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_76:
    ; No aliased ExtSprite or identical stream base across any pair.
    move.l 8(a3),d0
    beq.w s2d_r_alias_done_8
    movea.l d0,a0
    move.l 4(a3),d1
    beq.s s2d_r_alias_skip_8_4
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_8_4:
s2d_r_alias_done_8:
    move.l 52(a3),d0
    beq.w s2d_r_alias_done_52
    movea.l d0,a0
    move.l 4(a3),d1
    beq.s s2d_r_alias_skip_52_4
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_52_4:
    move.l 8(a3),d1
    beq.s s2d_r_alias_skip_52_8
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_52_8:
s2d_r_alias_done_52:
    move.l 56(a3),d0
    beq.w s2d_r_alias_done_56
    movea.l d0,a0
    move.l 4(a3),d1
    beq.s s2d_r_alias_skip_56_4
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_56_4:
    move.l 8(a3),d1
    beq.s s2d_r_alias_skip_56_8
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_56_8:
    move.l 52(a3),d1
    beq.s s2d_r_alias_skip_56_52
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_56_52:
s2d_r_alias_done_56:
    move.l 72(a3),d0
    beq.w s2d_r_alias_done_72
    movea.l d0,a0
    move.l 4(a3),d1
    beq.s s2d_r_alias_skip_72_4
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_72_4:
    move.l 8(a3),d1
    beq.s s2d_r_alias_skip_72_8
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_72_8:
    move.l 52(a3),d1
    beq.s s2d_r_alias_skip_72_52
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_72_52:
    move.l 56(a3),d1
    beq.s s2d_r_alias_skip_72_56
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_72_56:
s2d_r_alias_done_72:
    move.l 76(a3),d0
    beq.w s2d_r_alias_done_76
    movea.l d0,a0
    move.l 4(a3),d1
    beq.s s2d_r_alias_skip_76_4
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_76_4:
    move.l 8(a3),d1
    beq.s s2d_r_alias_skip_76_8
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_76_8:
    move.l 52(a3),d1
    beq.s s2d_r_alias_skip_76_52
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_76_52:
    move.l 56(a3),d1
    beq.s s2d_r_alias_skip_76_56
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_76_56:
    move.l 72(a3),d1
    beq.s s2d_r_alias_skip_76_72
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_76_72:
s2d_r_alias_done_76:
    moveq #1,d0
    rts

s2d_r_alloc:
    movem.l d2/a2,-(sp)
    move.l d0,d2
    movea.l a0,a2
    moveq #11,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.s s2d_r_alloc_no
    cmp.w 4(a2),d2
    bne.s s2d_r_alloc_no
    movea.l (a2),a0
    move.l d4,d0
    add.l d0,d0
    subq.l #1,d0
    move.l a0,d1
    and.l d0,d1
    bne.s s2d_r_alloc_no
    move.l d2,d0
    addq.l #2,d0
    mulu.w d4,d0
    lsl.l #2,d0
    subq.l #1,d0
    bsr.w s2d_c_span
    btst #1,d0
    beq.s s2d_r_alloc_no
    moveq #1,d0
    bra.s s2d_r_alloc_return
s2d_r_alloc_no:
    moveq #0,d0
s2d_r_alloc_return:
    movem.l (sp)+,d2/a2
    rts

; Derive current receipts (D2) and original confirmed mask (D3).
s2d_r_mask:
    move.l 24(a3),d2
    andi.l #3,d2
    move.l 84(a3),d3
    bne.s s2d_r_mask_journal
    cmpi.l #20,24(a3)
    beq.w s2d_c_no
    move.l d2,d3
    bra.s s2d_r_mask_yes
s2d_r_mask_journal:
    move.l d3,d0
    andi.l #$fffffffc,d0
    cmpi.l #$80000000,d0
    bne.w s2d_c_no
    andi.l #3,d3
    cmpi.l #2,d3
    beq.w s2d_c_no
    move.l d2,d0
    and.l d3,d0
    cmp.l d2,d0
    bne.w s2d_c_no
s2d_r_mask_yes:
    moveq #1,d0
    rts

; A0 = stack snapshot of current LOF/SHF. No use of stale old VP.
s2d_r_verify:
    move.l a2,-(sp)
    movea.l a0,a2
    move.l (a2),d0
    cmp.l 50(a5),d0
    bne.w s2d_r_verify_no
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_r_verify_no
    move.l 4(a2),d0
    cmp.l 54(a5),d0
    bne.w s2d_r_verify_no
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_r_verify_no
    move.l (a2),d0
    cmp.l 50(a5),d0
    bne.w s2d_r_verify_no
    move.l 4(a2),d0
    cmp.l 54(a5),d0
    bne.w s2d_r_verify_no
    bsr.w s2d_r_slots
    tst.l d0
    beq.w s2d_r_verify_no
    moveq #0,d0
    bsr.w s2d_r_one
    tst.l d0
    beq.s s2d_r_verify_no
    moveq #1,d0
    bsr.w s2d_r_one
    bra.s s2d_r_verify_return
s2d_r_verify_no:
    moveq #0,d0
s2d_r_verify_return:
    movea.l (sp)+,a2
    rts

; Exact snapshot bases and all eight Copper register pairs.
; Output A0=first slot, A1=first descriptor table entry.
s2d_r_slots:
    move.l 44(a3),d0
    cmp.l 38(a5),d0
    bne.w s2d_c_no
    movea.l d0,a0
    move.l #191,d0
    bsr.w s2d_c_span
    btst #1,d0
    beq.w s2d_c_no
    lea 88(a0),a0
    move.l a0,-(sp)
    moveq #7,d0
    move.w #$120,d1
s2d_r_slot_loop:
    cmp.w (a0),d1
    bne.s s2d_r_slot_bad
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.s s2d_r_slot_bad
    addq.w #2,d1
    addq.l #8,a0
    dbra d0,s2d_r_slot_loop
    move.l 48(a3),d0
    cmp.l 208(a5),d0
    bne.s s2d_r_slot_bad
    movea.l d0,a0
    moveq #31,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.s s2d_r_slot_bad
    movea.l a0,a1
    movea.l (sp)+,a0
    moveq #1,d0
    rts
s2d_r_slot_bad:
    addq.l #4,sp
    bra.w s2d_c_no

; D0=0 even or 1 odd relative to record. Ignore never-acquired slot;
; released slot must remain neutral; owned slot must have exact receipt.
s2d_r_one:
    movem.l d2-d7/a0-a2/a4,-(sp)
    move.l d0,d7
    btst d7,d3
    beq.w s2d_r_one_yes
    add.l d7,d6
    move.l d6,d0
    lsl.l #3,d0
    adda.l d0,a0
    move.l d6,d0
    lsl.l #2,d0
    adda.l d0,a1
    moveq #0,d0
    move.w 2(a0),d0
    swap d0
    move.w 6(a0),d0
    move.l d0,d3          ; observed copper data pointer
    move.l (a1),d1
    move.l d1,d5          ; observed descriptor
    btst d7,d2
    bne.s s2d_r_one_owned
    btst d6,166(a5)
    bne.w s2d_r_one_no
    tst.l d5
    bne.w s2d_r_one_no
    move.l 44(a3),d0
    addi.l #176,d0
    cmp.l d3,d0
    bne.w s2d_r_one_no
    bra.w s2d_r_one_yes
s2d_r_one_owned:
    btst d6,166(a5)
    beq.w s2d_r_one_no
    btst d6,448(a5)
    bne.w s2d_r_one_no
    cmp.w 444(a5),d4
    bne.w s2d_r_one_no
    tst.l d7
    bne.s s2d_r_one_odd
    movea.l 4(a3),a2
    move.l 52(a3),d2
    move.l 72(a3),d4
    bra.s s2d_r_one_receipt
s2d_r_one_odd:
    movea.l 8(a3),a2
    move.l 56(a3),d2
    move.l 76(a3),d4
s2d_r_one_receipt:
    cmp.w 10(a2),d6
    bne.w s2d_r_one_no
    tst.l d5
    beq.s s2d_r_one_copper
    cmp.l a2,d5
    beq.s s2d_r_one_table_num
    cmp.l d2,d5
    beq.s s2d_r_one_table_num
    cmp.l d4,d5
    bne.s s2d_r_one_no
s2d_r_one_table_num:
    movea.l d5,a4
    cmp.w 10(a4),d6
    bne.s s2d_r_one_no
s2d_r_one_copper:
    move.l 44(a3),d0
    addi.l #176,d0
    cmp.l d3,d0
    beq.s s2d_r_one_yes
    cmp.l (a2),d3
    beq.s s2d_r_one_yes
    tst.l d2
    beq.s s2d_r_one_stage
    movea.l d2,a4
    cmp.l (a4),d3
    beq.s s2d_r_one_yes
s2d_r_one_stage:
    tst.l d4
    beq.s s2d_r_one_no
    movea.l d4,a4
    cmp.l (a4),d3
    bne.s s2d_r_one_no
s2d_r_one_yes:
    moveq #1,d0
    bra.s s2d_r_one_return
s2d_r_one_no:
    moveq #0,d0
s2d_r_one_return:
    movem.l (sp)+,d2-d7/a0-a2/a4
    rts

; All descriptors were validated before any release; never deref peers.
s2d_r_no_refs:
    move.l d7,-(sp)
    move.l 4(a3),d0
    beq.s s2d_r_scan_skip_4
    movea.l d0,a0
    moveq #1,d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_4:
    move.l 8(a3),d0
    beq.s s2d_r_scan_skip_8
    movea.l d0,a0
    moveq #1,d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_8:
    move.l 52(a3),d0
    beq.s s2d_r_scan_skip_52
    movea.l d0,a0
    move.l (sp),d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_52:
    move.l 56(a3),d0
    beq.s s2d_r_scan_skip_56
    movea.l d0,a0
    move.l (sp),d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_56:
    move.l 72(a3),d0
    beq.s s2d_r_scan_skip_72
    movea.l d0,a0
    move.l (sp),d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_72:
    move.l 76(a3),d0
    beq.s s2d_r_scan_skip_76
    movea.l d0,a0
    move.l (sp),d7
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_76:
    moveq #1,d0
    bra.s s2d_r_scan_return
s2d_r_scan_no:
    moveq #0,d0
s2d_r_scan_return:
    move.l (sp)+,d7
    rts

    include "M19_S2D_EXT_FRAME_MC68020.s"
