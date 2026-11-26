; AGA_NATIVE_MIN_CPU: MC68020
; S2a component: stage one detached prepared frame in the inactive slot
; of the existing P2m allocation. Not a DMA/publication entry.
; A0=live P2a/P2m block, D0=exact extent;
; A1=detached P2a block, D1=exact extent;
; D2=inactive slot address, independently established safe by the caller.
; Both extents must be pinned, nonaliased, actual Chip allocations; the
; caller owns the live registry transaction and an OS retirement/fence
; receipt for the inactive slot. This helper cannot prove DMA safety.
; D0=staged pointer, D1=slot bytes, or D0/D1=0 on refusal.
; D2-D7/A0-A6 preserved. No OS, allocation, free, VBL, publication or
; metadata change. The active slot and source are never written.
; First S2a contract: 16px, 2bpp, equal height, zero hotspots, exact
; same bank generation and RGB24 local palette. P2a validates source.
AGSP_S2A_STAGE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    movea.l a1,a3
    move.l d0,d4
    move.l d1,d5
    move.l d2,d6
    cmp.l d4,d5
    bne.w s2a_stage_no
    cmpi.l #72,d4
    bcs.w s2a_stage_no
    cmpi.l #2112,d4
    bhi.w s2a_stage_no
    move.l a2,d0
    beq.w s2a_stage_no
    btst #0,d0
    bne.w s2a_stage_no
    move.l a3,d1
    beq.w s2a_stage_no
    btst #0,d1
    bne.w s2a_stage_no
    move.l d0,d2
    add.l d4,d2
    bcs.w s2a_stage_no
    move.l d1,d3
    add.l d5,d3
    bcs.w s2a_stage_no
    cmp.l d3,d0
    bcc.s s2a_stage_disjoint
    cmp.l d2,d1
    bcs.w s2a_stage_no
s2a_stage_disjoint:
    ; Both proven allocations have the exact P2a layout.
    cmp.l 12(a2),d4
    bne.w s2a_stage_no
    cmp.l 12(a3),d5
    bne.w s2a_stage_no
    cmpi.l #48,40(a2)
    bne.w s2a_stage_no
    cmpi.l #48,40(a3)
    bne.w s2a_stage_no
    moveq #0,d7
    move.w 4(a2),d7
    beq.w s2a_stage_no
    cmpi.w #256,d7
    bhi.w s2a_stage_no
    cmp.w 4(a3),d7
    bne.w s2a_stage_no
    lsl.l #2,d7
    addq.l #8,d7
    move.l d7,d0
    addi.l #48,d0
    cmp.l 44(a2),d0
    bne.w s2a_stage_no
    cmp.l 44(a3),d0
    bne.w s2a_stage_no
    add.l d7,d0
    cmp.l d4,d0
    bne.w s2a_stage_no
    ; Detached source has never been published by graphics.library.
    cmpi.w #2,10(a2)
    bne.w s2a_stage_no
    cmpi.w #-1,10(a3)
    bne.w s2a_stage_no
    tst.l (a3)
    bne.w s2a_stage_no
    tst.l 6(a3)
    bne.w s2a_stage_no
    tst.l 24(a2)
    bne.w s2a_stage_no
    tst.l 24(a3)
    bne.w s2a_stage_no
    move.l 20(a2),d0
    beq.w s2a_stage_no
    cmp.l 20(a3),d0
    bne.w s2a_stage_no
    moveq #0,d0
    move.w 16(a3),d0
    beq.w s2a_stage_no
    cmpi.l #4096,d0
    bhi.w s2a_stage_no
    moveq #0,d0
    move.w 18(a2),d0
    cmpi.w #3,d0
    bhi.w s2a_stage_no
    cmp.w 18(a3),d0
    bne.w s2a_stage_no
    move.l 28(a2),d0
    cmp.l 28(a3),d0
    bne.w s2a_stage_no
    move.l 32(a2),d0
    cmp.l 32(a3),d0
    bne.w s2a_stage_no
    move.l 36(a2),d0
    cmp.l 36(a3),d0
    bne.w s2a_stage_no
    ; Resolve the opposite slot from the stable live descriptor.
    lea 48(a2),a4
    movea.l a4,a5
    adda.l d7,a5
    move.l (a2),d0
    cmp.l a4,d0
    beq.s s2a_stage_first
    cmp.l a5,d0
    bne.w s2a_stage_no
    movea.l a4,a6
    bra.s s2a_stage_slot
s2a_stage_first:
    movea.l a5,a6
s2a_stage_slot:
    move.l a6,d0
    cmp.l d6,d0
    bne.w s2a_stage_no
    lea 48(a3),a0
    tst.l (a0)
    bne.w s2a_stage_no
    movea.l a0,a1
    adda.l d7,a1
    tst.l -4(a1)
    bne.w s2a_stage_no
    ; Only now write the entire inactive frame, including control/footer.
    ; No fallible operation after this first store.
    movea.l a6,a1
    move.l d7,d0
    lsr.l #2,d0
    subq.w #1,d0
s2a_stage_copy:
    move.l (a0)+,(a1)+
    dbra d0,s2a_stage_copy
    move.l a6,d0
    move.l d7,d1
    bra.s s2a_stage_return
s2a_stage_no:
    moveq #0,d0
    moveq #0,d1
s2a_stage_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts
