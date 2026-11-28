; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P2c2: first show (+0), move (+4), exchange frame (+8).
; Source-derived P2c1, same first 72 bytes; full record 96 bytes.
; +72/+76 staged even/odd (odd=0 for simple), +80 stage.L:
; 0 absent; 1 private candidate; 2 possibly exposed (sticky);
; 3 previous frame no longer referenced by sampled OS slots after fence.
; +84 reserved zero, +88/+92 pinned LOF/SHF snapshots.
; Caller owns/pins all allocations, disjoint chip streams, source palette,
; bank generation, height, width, kind; exclusive registry borrow.
; Candidate must match width/kind/height/palette; no hot spot in this tranche.
; A0 receipt, A6 graphics.library, D0/D1 x/y for move, ignored for exchange.
; Return 1/0 success, 0/1 preflight refusal, 0/2 uncertain (state15).
; On exchange failure both sets retained; no speculative free or retry.
; State3 permits another exchange of the retained old frame. No free here.
; Two WaitTOF while BOTH current channels are hidden, then switch, verify
; all eight sampled slots no longer reference old frame, commit pointers.
; Not a guarantee of atomic raster update or universal DMA safety.
    bra.w AGSP_S2D_EXT_FIRST_SHOW
    bra.w AGSP_S2D_EXT_MOVE
    bra.w AGSP_S2D_EXT_EXCHANGE

AGSP_S2D_EXT_MOVE:
    movem.l d2-d7/a0-a6,-(sp)
    move.l d1,-(sp)
    move.l d0,-(sp)
    movea.l a0,a3
    movea.l a6,a5
    bsr.w s2d_x_base
    tst.l d0
    beq.w s2d_x_move_bad
    bsr.w s2d_x_current
    tst.l d0
    beq.w s2d_x_move_uncertain
    move.l (sp),d2
    move.l 4(sp),d3
    bsr.w s2d_x_geometry
    tst.l d0
    beq.w s2d_x_move_bad
    move.l #15,24(a3)
    bsr.w s2d_x_reveal
    tst.l d0
    beq.s s2d_x_move_uncertain
    move.l #31,24(a3)
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_x_move_return
s2d_x_move_bad:
    moveq #0,d0
    moveq #1,d1
    bra.s s2d_x_move_return
s2d_x_move_uncertain:
    move.l #15,24(a3)
    moveq #0,d0
    moveq #2,d1
s2d_x_move_return:
    addq.l #8,sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

AGSP_S2D_EXT_EXCHANGE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a6,a5
    bsr.w s2d_x_base
    tst.l d0
    beq.w s2d_x_bad
    cmpi.l #1,80(a3)
    beq.s s2d_x_stage_ok
    cmpi.l #3,80(a3)
    bne.w s2d_x_bad
s2d_x_stage_ok:
    bsr.w s2d_x_current
    tst.l d0
    beq.w s2d_x_uncertain
    ; All candidate descriptors must be distinct from blanks and current.
    move.l 72(a3),d0
    bsr.w s2d_x_distinct
    tst.l d0
    beq.w s2d_x_bad
    movea.l 72(a3),a0
    move.l d7,d0
    moveq #0,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_x_bad
    cmpi.l #4,d5
    beq.s s2d_x_stage_odd
    tst.l 76(a3)
    bne.w s2d_x_bad
    bra.s s2d_x_begin
s2d_x_stage_odd:
    move.l 76(a3),d0
    cmp.l 72(a3),d0
    beq.w s2d_x_bad
    bsr.w s2d_x_distinct
    tst.l d0
    beq.w s2d_x_bad
    movea.l 76(a3),a0
    move.l d7,d0
    moveq #1,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_x_bad
s2d_x_begin:
    ; Reject stage references anywhere in the sampled tables before use.
    movea.l 72(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_x_bad
    cmpi.l #4,d5
    bne.s s2d_x_stage_clear
    movea.l 76(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_x_bad
s2d_x_stage_clear:
    bsr.w s2d_x_refs
    tst.l d0
    beq.w s2d_x_uncertain
    move.l #15,24(a3)
    move.l #2,80(a3)
    movea.l a4,a1
    bsr.w s2d_c_hide
    bsr.w s2d_x_hidden
    tst.l d0
    beq.w s2d_x_uncertain
    jsr -270(a6)
    bsr.w s2d_x_hidden
    tst.l d0
    beq.w s2d_x_uncertain
    jsr -270(a6)
    bsr.w s2d_x_hidden
    tst.l d0
    beq.w s2d_x_uncertain
    cmpi.l #4,d5
    bne.s s2d_x_even
    movea.l a2,a1
    movea.l 76(a3),a2
    bsr.w s2d_c_change
    tst.l d0
    beq.w s2d_x_uncertain
    movea.l 76(a3),a2
    bsr.w s2d_x_hidden
    tst.l d0
    beq.w s2d_x_uncertain
s2d_x_even:
    movea.l a4,a1
    movea.l 72(a3),a2
    bsr.w s2d_c_change
    tst.l d0
    beq.w s2d_x_uncertain
    movea.l 72(a3),a4
    movea.l 8(a3),a2
    cmpi.l #4,d5
    bne.s s2d_x_ready
    movea.l 76(a3),a2
s2d_x_ready:
    bsr.w s2d_x_hidden
    tst.l d0
    beq.w s2d_x_uncertain
    bsr.w s2d_x_reveal
    tst.l d0
    beq.w s2d_x_uncertain
    ; Old streams have been hidden through both fences; verify there is
    ; no old descriptor or pointer into its used extent in any of 8 slots.
    movea.l 52(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_x_uncertain
    cmpi.l #4,d5
    bne.s s2d_x_commit
    movea.l 56(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_x_uncertain
s2d_x_commit:
    bsr.w s2d_x_refs
    tst.l d0
    beq.w s2d_x_uncertain
    move.l 52(a3),d0
    move.l 72(a3),52(a3)
    move.l d0,72(a3)
    move.l 56(a3),d0
    move.l 76(a3),56(a3)
    move.l d0,76(a3)
    move.l #3,80(a3)
    move.l #31,24(a3)
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_x_return
s2d_x_bad:
    moveq #0,d0
    moveq #1,d1
    bra.s s2d_x_return
s2d_x_uncertain:
    move.l #15,24(a3)
    moveq #0,d0
    moveq #2,d1
s2d_x_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Structural validation. D4 width words, D5 kind, D6 channel, D7 height.
s2d_x_base:
    movea.l a3,a0
    moveq #95,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    cmpa.l (a3),a5
    bne.w s2d_c_no
    cmpi.l #31,24(a3)
    bne.w s2d_c_no
    tst.l 32(a3)
    bne.w s2d_c_no
    tst.l 68(a3)
    bne.w s2d_c_no
    tst.l 84(a3)
    bne.w s2d_c_no
    move.l 80(a3),d0
    cmpi.l #3,d0
    bhi.w s2d_c_no
    cmpi.l #2,d0
    beq.w s2d_c_no
    move.l 12(a3),d4
    cmpi.l #16,d4
    beq.s s2d_x_width
    cmpi.l #32,d4
    beq.s s2d_x_width
    cmpi.l #64,d4
    bne.w s2d_c_no
s2d_x_width:
    lsr.l #4,d4
    move.l 16(a3),d5
    cmpi.l #2,d5
    beq.s s2d_x_kind
    cmpi.l #4,d5
    bne.w s2d_c_no
s2d_x_kind:
    move.l 20(a3),d6
    cmpi.l #2,d6
    beq.s s2d_x_channel
    cmpi.l #4,d6
    beq.s s2d_x_channel
    cmpi.l #6,d6
    bne.w s2d_c_no
s2d_x_channel:
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
    cmpi.w #1026,16(a5)
    bcs.w s2d_c_no
    cmpi.w #39,20(a5)
    bcs.w s2d_c_no
    cmpi.w #40,20(a5)
    bhi.w s2d_c_no
    moveq #1,d0
    rts

s2d_x_distinct:
    tst.l d0
    beq.w s2d_c_no
    cmp.l 4(a3),d0
    beq.w s2d_c_no
    cmp.l 8(a3),d0
    beq.w s2d_c_no
    cmp.l 52(a3),d0
    beq.w s2d_c_no
    cmp.l 56(a3),d0
    beq.w s2d_c_no
    moveq #1,d0
    rts

; Current pair, read-only validation of descriptors before reading positions.
s2d_x_current:
    movea.l 52(a3),a4
    movea.l a4,a0
    move.l d7,d0
    moveq #0,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_no
    cmpi.l #4,d5
    beq.s s2d_x_current_att
    tst.l 56(a3)
    bne.w s2d_c_no
    movea.l 8(a3),a2
    movea.l a2,a0
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_x_current_odd
s2d_x_current_att:
    movea.l 56(a3),a2
    movea.l a2,a0
    move.l d7,d0
    moveq #1,d1
s2d_x_current_odd:
    cmpa.l a2,a4
    beq.w s2d_c_no
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_no
    moveq #0,d2
    move.w 6(a4),d2
    moveq #0,d3
    move.w 8(a4),d3
    bsr.w s2d_x_geometry
    tst.l d0
    beq.w s2d_c_no
    bra.w s2d_x_refs

s2d_x_geometry:
    move.l d4,d0
    lsl.l #4,d0
    neg.l d0
    addi.l #320,d0
    cmp.l d0,d2
    bhi.w s2d_c_no
    move.l #256,d0
    sub.l d7,d0
    cmp.l d0,d3
    bhi.w s2d_c_no
    moveq #1,d0
    rts

; Stable mapped list starts as in S2c. No traversal or universal DMA proof.
s2d_x_lists:
    move.l 88(a3),d0
    cmp.l 50(a5),d0
    bne.w s2d_c_no
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    move.l 92(a3),d0
    cmp.l 54(a5),d0
    bne.w s2d_c_no
    movea.l d0,a0
    moveq #1,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    move.l 88(a3),d0
    cmp.l 50(a5),d0
    bne.w s2d_c_no
    move.l 92(a3),d0
    cmp.l 54(a5),d0
    bne.w s2d_c_no
    moveq #1,d0
    rts

s2d_x_hidden:
    bsr.w s2d_x_lists
    tst.l d0
    beq.w s2d_c_no
    bra.w s2d_c_hidden_refs
s2d_x_reveal:
    movea.l 36(a3),a0
    movea.l a4,a1
    move.l d2,d0
    move.l d3,d1
    jsr -426(a6)
s2d_x_refs:
    bsr.w s2d_x_lists
    tst.l d0
    beq.w s2d_c_no
    bsr.w s2d_c_context
    tst.l d0
    beq.w s2d_c_no
    cmpa.l (a1),a4
    bne.w s2d_c_no
    cmpa.l 4(a1),a2
    bne.w s2d_c_no
    cmp.w 10(a4),d6
    bne.w s2d_c_no
    move.l d6,d0
    addq.l #1,d0
    cmp.w 10(a2),d0
    bne.w s2d_c_no
    cmp.w 6(a4),d2
    bne.w s2d_c_no
    cmp.w 8(a4),d3
    bne.w s2d_c_no
    move.l (a4),d0
    cmp.w 6(a0),d0
    bne.w s2d_c_no
    swap d0
    cmp.w 2(a0),d0
    bne.w s2d_c_no
    cmpi.l #4,d5
    bne.s s2d_x_simple
    cmp.w 6(a2),d2
    bne.w s2d_c_no
    cmp.w 8(a2),d3
    bne.w s2d_c_no
    move.l (a2),d0
    bra.s s2d_x_odd
s2d_x_simple:
    cmpi.w #0,6(a2)
    bne.w s2d_c_no
    cmpi.w #257,8(a2)
    bne.w s2d_c_no
    move.l 44(a3),d0
    addi.l #176,d0
s2d_x_odd:
    cmp.w 14(a0),d0
    bne.w s2d_c_no
    swap d0
    cmp.w 10(a0),d0
    bne.w s2d_c_no
    moveq #1,d0
    rts

; A0 pinned frame descriptor (validated), D7 height, D4 width words.
; Inspect all eight sampled table entries and Copper pointer ranges.
; No dereference of foreign descriptors; no arbitrary list traversal.
s2d_x_unreferenced:
    movem.l d2-d4/a2/a4,-(sp)
    move.l a0,d2
    move.l (a0),d3
    move.l d7,d0
    addq.l #2,d0
    mulu.w d4,d0
    lsl.l #2,d0
    add.l d3,d0
    bcs.s s2d_x_ref_no
    move.l d0,d4
    movea.l 48(a3),a2
    movea.l 44(a3),a4
    lea 88(a4),a4
    moveq #7,d0
    move.w #$120,d1
s2d_x_scan:
    cmp.l (a2)+,d2
    beq.s s2d_x_ref_no
    cmp.w (a4),d1
    bne.s s2d_x_ref_no
    addq.w #2,d1
    cmp.w 4(a4),d1
    bne.s s2d_x_ref_no
    addq.w #2,d1
    move.w 2(a4),-(sp)
    move.w 6(a4),-(sp)
    move.l (sp)+,d1
    swap d1
    cmp.l d3,d1
    bcs.s s2d_x_ref_next
    cmp.l d4,d1
    bcs.s s2d_x_ref_no
s2d_x_ref_next:
    ; Recompute next register word from remaining channel count.
    lea 8(a4),a4
    moveq #8,d1
    sub.w d0,d1
    lsl.w #2,d1
    addi.w #$120,d1
    dbra d0,s2d_x_scan
    moveq #1,d0
    bra.s s2d_x_ref_return
s2d_x_ref_no:
    moveq #0,d0
s2d_x_ref_return:
    movem.l (sp)+,d2-d4/a2/a4
    rts

    include "M19_S2D_EXT_HIDDEN_SHOW_MC68020.s"
