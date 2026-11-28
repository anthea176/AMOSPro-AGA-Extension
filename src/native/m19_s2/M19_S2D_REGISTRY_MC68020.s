; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P3: one named v6 registry, three inline ExtSprite receipts.
; 96-byte P2d receipt followed by ID, bank, image, generation,
; stage image, opaque count and 48-byte local RGB24 palette.
; All roots pinned and exclusively borrowed. No pointers to native code.
; SCAN D0 logical ID (0 inspect), A0 root; D0 record/0, D1 free mask/-1.
; DRAIN A0 root A1 GfxBase D0 mode 0 preclose,1 closed,2 Off,3 bank,4 closed bank.
; Preclose fully retires/reclaims while Gfx and screen live; refuses Close
; on any unresolved receipt. Keeps lifetime header until real Close success.
; Postclose requires empty registry. No speculative reclaim of stale VP.
W_REC_BYTES equ 168
W_R_ID equ 96
W_R_BANK equ 100
W_R_IMAGE equ 104
W_R_GEN equ 108
W_R_STAGE equ 112
W_R_COLORS equ 116
W_R_PAL equ 120

AGSP_S2B_SCAN:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    move.l d0,d7
    cmpi.l #64,d7
    bhi.w s2d_reg_bad
    move.l a2,d0
    beq.w s2d_reg_bad
    btst #0,d0
    bne.w s2d_reg_bad
    addi.l #556,d0
    bcs.w s2d_reg_bad
    cmpi.l #3,(a2)
    bhi.w s2d_reg_bad
    moveq #0,d2       ; count
    moveq #0,d3       ; slot
    moveq #0,d4       ; free mask
    moveq #0,d5       ; matched pointer
    moveq #0,d6       ; common width
    lea 52(a2),a3
s2d_reg_slot:
    move.l W_R_ID(a3),d0
    bne.s s2d_reg_used
    movea.l a3,a0
    moveq #41,d1
s2d_reg_zero:
    tst.l (a0)+
    bne.w s2d_reg_bad
    dbra d1,s2d_reg_zero
    bset d3,d4
    bra.w s2d_reg_next
s2d_reg_used:
    cmpi.l #64,d0
    bhi.w s2d_reg_bad
    cmp.l d7,d0
    bne.s s2d_reg_id
    move.l a3,d5
s2d_reg_id:
    move.l d3,d1
    add.l d1,d1
    addq.l #2,d1
    cmp.l 20(a3),d1
    bne.w s2d_reg_bad
    move.l W_R_BANK(a3),d0
    cmpi.l #5,d0
    bcs.w s2d_reg_bad
    cmpi.l #65535,d0
    bhi.w s2d_reg_bad
    move.l W_R_IMAGE(a3),d0
    beq.w s2d_reg_bad
    cmpi.l #4096,d0
    bhi.w s2d_reg_bad
    tst.l W_R_GEN(a3)
    beq.w s2d_reg_bad
    move.l 12(a3),d0
    cmpi.l #16,d0
    beq.s s2d_reg_width
    cmpi.l #32,d0
    beq.s s2d_reg_width
    cmpi.l #64,d0
    bne.w s2d_reg_bad
s2d_reg_width:
    tst.l d6
    beq.s s2d_reg_width_first
    cmp.l d6,d0
    bne.w s2d_reg_bad
s2d_reg_width_first:
    move.l d0,d6
    move.l 16(a3),d0
    cmpi.l #2,d0
    beq.s s2d_reg_simple
    cmpi.l #4,d0
    bne.w s2d_reg_bad
    tst.l 56(a3)
    beq.w s2d_reg_bad
    cmpi.l #4,W_R_COLORS(a3)
    bcs.w s2d_reg_bad
    cmpi.l #15,W_R_COLORS(a3)
    bhi.w s2d_reg_bad
    bra.s s2d_reg_meta
s2d_reg_simple:
    tst.l 56(a3)
    bne.w s2d_reg_bad
    tst.l 76(a3)
    bne.w s2d_reg_bad
    cmpi.l #3,W_R_COLORS(a3)
    bhi.w s2d_reg_bad
s2d_reg_meta:
    tst.l (a3)
    beq.w s2d_reg_bad
    tst.l 4(a3)
    beq.w s2d_reg_bad
    tst.l 8(a3)
    beq.w s2d_reg_bad
    tst.l 52(a3)
    beq.w s2d_reg_bad
    move.l 60(a3),d0
    beq.w s2d_reg_bad
    cmpi.l #256,d0
    bhi.w s2d_reg_bad
    move.l 80(a3),d0
    cmpi.l #3,d0
    bhi.w s2d_reg_bad
    tst.l d0
    bne.s s2d_reg_staged
    move.l 72(a3),d0
    or.l 76(a3),d0
    or.l W_R_STAGE(a3),d0
    bne.w s2d_reg_bad
    bra.s s2d_reg_peers
s2d_reg_staged:
    tst.l 72(a3)
    beq.w s2d_reg_bad
    move.l W_R_STAGE(a3),d0
    beq.w s2d_reg_bad
    cmpi.l #4096,d0
    bhi.w s2d_reg_bad
    cmpi.l #4,16(a3)
    bne.s s2d_reg_peers
    tst.l 76(a3)
    beq.w s2d_reg_bad
s2d_reg_peers:
    lea 52(a2),a4
s2d_reg_peer:
    cmpa.l a3,a4
    beq.s s2d_reg_count
    move.l W_R_ID(a4),d0
    beq.s s2d_reg_peer_next
    cmp.l W_R_ID(a3),d0
    beq.w s2d_reg_bad
    ; Compare all descriptor receipts before any target may be released.
    bsr.w s2d_reg_distinct
    tst.l d0
    beq.w s2d_reg_bad
s2d_reg_peer_next:
    lea W_REC_BYTES(a4),a4
    bra.s s2d_reg_peer
s2d_reg_count:
    addq.l #1,d2
s2d_reg_next:
    lea W_REC_BYTES(a3),a3
    addq.l #1,d3
    cmpi.l #3,d3
    bcs.w s2d_reg_slot
    cmp.l (a2),d2
    bne.s s2d_reg_bad
    move.l d5,d0
    move.l d4,d1
    bra.s s2d_reg_return
s2d_reg_bad:
    moveq #0,d0
    moveq #-1,d1
s2d_reg_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; A3/A4 distinct occupied slots. No dereference of ExtSprite pointers.
s2d_reg_distinct:
    movem.l d2-d3/a0-a1,-(sp)
    lea s2d_reg_ptrs(pc),a0
    moveq #5,d2
s2d_reg_outer:
    moveq #0,d0
    move.b (a0)+,d0
    move.l 0(a3,d0.w),d0
    beq.s s2d_reg_outer_next
    lea s2d_reg_ptrs(pc),a1
    moveq #5,d3
s2d_reg_inner:
    moveq #0,d1
    move.b (a1)+,d1
    cmp.l 0(a4,d1.w),d0
    beq.s s2d_reg_alias
    dbra d3,s2d_reg_inner
s2d_reg_outer_next:
    dbra d2,s2d_reg_outer
    moveq #1,d0
    bra.s s2d_reg_distinct_return
s2d_reg_alias:
    moveq #0,d0
s2d_reg_distinct_return:
    movem.l (sp)+,d2-d3/a0-a1
    rts
s2d_reg_ptrs:
    dc.b 4,8,52,56,72,76

AGSP_S2B_DRAIN:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    movea.l a1,a6
    move.l d0,d2
    move.l d1,d3
    cmpi.l #4,d2
    bhi.w s2d_drain_bad
    moveq #0,d0
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.w s2d_drain_bad
    cmpi.l #1,d2
    beq.w s2d_drain_closed
    cmpi.l #4,d2
    beq.w s2d_drain_closed
    tst.l 12(a2)
    beq.w s2d_drain_bad
    move.l 48(a2),d0
    beq.w s2d_drain_bad
    cmp.l 16(a2),d0
    bne.w s2d_drain_bad
    moveq #1,d5
    moveq #2,d4
    lea 52(a2),a3
s2d_drain_slot:
    move.l W_R_ID(a3),d0
    beq.s s2d_drain_next
    cmpi.l #2,d2
    bne.s s2d_drain_bank
    cmp.l d3,d0
    bne.s s2d_drain_next
s2d_drain_bank:
    cmpi.l #3,d2
    bne.s s2d_drain_record
    cmp.l W_R_BANK(a3),d3
    bne.s s2d_drain_next
s2d_drain_record:
    movea.l a3,a0
    bsr.w AGSP_S2D_EXT_RETIRE
    tst.l d0
    beq.s s2d_drain_pending
    movea.l a3,a0
    bsr.w AGSP_S2D_EXT_RECLAIM
    tst.l d0
    beq.s s2d_drain_pending
    movea.l a3,a0
    moveq #41,d0
s2d_drain_clear:
    clr.l (a0)+
    dbra d0,s2d_drain_clear
    subq.l #1,(a2)
    bra.s s2d_drain_next
s2d_drain_pending:
    moveq #0,d5
s2d_drain_next:
    lea W_REC_BYTES(a3),a3
    dbra d4,s2d_drain_slot
    tst.l d2
    beq.s s2d_drain_result
    tst.l (a2)
    bne.s s2d_drain_result
    bra.s s2d_drain_empty
s2d_drain_closed:
    move.l 12(a2),d0
    or.l 48(a2),d0
    or.l (a2),d0
    bne.s s2d_drain_bad
    moveq #1,d5
s2d_drain_empty:
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 48(a2)
s2d_drain_result:
    move.l d5,d0
    bra.s s2d_drain_return
s2d_drain_bad:
    moveq #0,d0
s2d_drain_return:
    moveq #0,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts
