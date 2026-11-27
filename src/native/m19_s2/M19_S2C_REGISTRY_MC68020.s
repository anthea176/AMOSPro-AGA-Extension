; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P1b mixed v5 registry and collective/targeted retirement.
; 72-byte slots: S2b prefix 44, kind.L 2/4, Gfx/CM/View/CI/Table/reserved.
; Kind2 extra fields zero. Kind4 legacy odd descriptor bytes zero.
; All receipt state is the same LONG at +12, no duplicated state.
; A0 = authenticated, pinned v5 root under its named semaphore borrow.
; All chip pointers originate in the private P2a allocator. No foreign
; pointers are accepted by the producer. Span checks corroborate mapping,
; not exact allocation provenance. No allocation or wait in Forbid.
; All entries preserve D2-D7/A0-A6.
; SCAN: D0 logical ID (0 = inspect only). D0 record or 0, D1 free
; slot mask (bits 0..2), -1 structural refusal. No writes or OS calls.
AGSP_S2B_SCAN:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    move.l d0,d7
    cmpi.l #64,d7
    bhi.w s2b_scan_bad
    move.l a2,d0
    cmpi.l #56,d0
    bcs.w s2b_scan_bad
    btst #0,d0
    bne.w s2b_scan_bad
    addi.l #268,d0
    bcs.w s2b_scan_bad
    cmpi.l #3,(a2)
    bhi.w s2b_scan_bad
    moveq #0,d6          ; matching record
    moveq #0,d5          ; free slots
    moveq #0,d4          ; observed count
    moveq #0,d3          ; slot index
    lea 52(a2),a3
s2b_scan_slot:
    move.l 28(a3),d0
    bne.s s2b_scan_used
    movea.l a3,a4
    moveq #17,d2
s2b_scan_zero:
    tst.l (a4)+
    bne.w s2b_scan_bad
    dbra d2,s2b_scan_zero
    bset d3,d5
    bra.w s2b_scan_next
s2b_scan_used:
    cmpi.l #64,d0
    bhi.w s2b_scan_bad
    addq.l #1,d4
    cmp.l d7,d0
    bne.s s2b_scan_channel
    move.l a3,d6
s2b_scan_channel:
    move.l d3,d1
    add.l d1,d1
    addq.l #2,d1
    cmp.l 40(a3),d1
    bne.w s2b_scan_bad
    move.l (a3),d0
    beq.w s2b_scan_bad
    btst #0,d0
    bne.w s2b_scan_bad
    move.l 4(a3),d1
    cmpi.l #2,44(a3)
    beq.s s2c_scan_single
    cmpi.l #4,44(a3)
    bne.w s2b_scan_bad
    cmpi.l #144,d1
    bcs.w s2b_scan_bad
    cmpi.l #4224,d1
    bhi.w s2b_scan_bad
    move.l 16(a3),d2
    or.l 20(a3),d2
    or.l 24(a3),d2
    or.l 68(a3),d2
    bne.w s2b_scan_bad
    lea 48(a3),a4
    moveq #4,d2
s2c_scan_snapshots:
    move.l (a4)+,d0
    beq.w s2b_scan_bad
    btst #0,d0
    bne.w s2b_scan_bad
    dbra d2,s2c_scan_snapshots
    move.l (a3),d0
    bra.s s2c_scan_extent
s2c_scan_single:
    cmpi.l #72,d1
    bcs.w s2b_scan_bad
    cmpi.l #2112,d1
    bhi.w s2b_scan_bad
    lea 48(a3),a4
    moveq #5,d2
s2c_scan_no_extras:
    tst.l (a4)+
    bne.w s2b_scan_bad
    dbra d2,s2c_scan_no_extras
s2c_scan_extent:
    add.l d0,d1
    bcs.w s2b_scan_bad
    ; No Chip extent may overlap the semaphore allocation.
    move.l a2,d2
    addi.l #268,d2
    cmp.l d2,d0
    bcc.s s2b_scan_previous
    move.l a2,d2
    subi.l #56,d2
    cmp.l d2,d1
    bhi.w s2b_scan_bad
s2b_scan_previous:
    ; Earlier records were already validated. Reject duplicate IDs and
    ; overlapping Chip extents before a collective call can free anything.
    lea 52(a2),a4
s2b_scan_peer:
    cmpa.l a3,a4
    beq.s s2b_scan_next
    move.l 28(a4),d2
    beq.s s2b_scan_peer_next
    cmp.l 28(a3),d2
    beq.s s2b_scan_bad
    move.l (a4),d2
    cmp.l d1,d2
    bcc.s s2b_scan_peer_next
    add.l 4(a4),d2
    cmp.l d0,d2
    bhi.s s2b_scan_bad
s2b_scan_peer_next:
    lea 72(a4),a4
    bra.s s2b_scan_peer
s2b_scan_next:
    lea 72(a3),a3
    addq.l #1,d3
    cmpi.l #3,d3
    bcs.w s2b_scan_slot
    cmp.l (a2),d4
    bne.s s2b_scan_bad
    move.l d6,d0
    move.l d5,d1
    bra.s s2b_scan_return
s2b_scan_bad:
    moveq #0,d0
    moveq #-1,d1
s2b_scan_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; DRAIN: A0 root, A1 live GfxBase, D0 mode, D1 filter.
; 0 = pre-Close/End all (retire only; allow state 4 pending, never free)
; 1 = after successful Close all; 2 = live Off(ID)
; 3 = live Bank Free(bank); 4 = closed Bank Free(bank).
; D0=1 all targeted safe/handled, 0 refusal or pending; D1=0.
; A failure leaves its record intact (possibly state 4); never discard
; other receipts. Continue independent safe retirements. Before Close
; succeeds keep owner/State/Screen/Task and records even when retired.
AGSP_S2B_DRAIN:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    movea.l a1,a5
    move.l d0,d2
    move.l d1,d3
    cmpi.l #4,d2
    bhi.w s2b_drain_bad
    moveq #0,d0
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.w s2b_drain_bad
    cmpi.l #2,d2
    bne.s s2b_drain_bank_arg
    cmpi.l #1,d3
    bcs.w s2b_drain_bad
    cmpi.l #64,d3
    bhi.w s2b_drain_bad
s2b_drain_bank_arg:
    cmpi.l #3,d2
    bcs.s s2b_drain_owner
    cmpi.l #5,d3
    bcs.w s2b_drain_bad
    cmpi.l #65535,d3
    bhi.w s2b_drain_bad
s2b_drain_owner:
    cmpi.l #1,d2
    beq.s s2b_drain_closed
    cmpi.l #4,d2
    beq.s s2b_drain_closed
    tst.l 12(a2)
    beq.w s2b_drain_bad
    move.l 48(a2),d0
    beq.w s2b_drain_bad
    cmp.l 16(a2),d0
    bne.w s2b_drain_bad
    bra.s s2b_drain_start
s2b_drain_closed:
    move.l 12(a2),d0
    or.l 48(a2),d0
    bne.w s2b_drain_bad
s2b_drain_start:
    moveq #1,d5
    moveq #2,d4
    lea 52(a2),a3
s2b_drain_slot:
    move.l 28(a3),d0
    beq.w s2b_drain_next
    cmpi.l #2,d2
    bne.s s2b_drain_bank
    cmp.l d3,d0
    bne.w s2b_drain_next
s2b_drain_bank:
    cmpi.l #3,d2
    bcs.s s2b_drain_check
    cmp.l 32(a3),d3
    bne.w s2b_drain_next
s2b_drain_check:
    move.l 12(a3),d0
    cmpi.l #1,d2
    beq.s s2b_drain_closed_flags
    cmpi.l #4,d2
    beq.s s2b_drain_closed_flags
    btst #3,d0
    beq.s s2b_drain_chip
    move.l 12(a2),d0
    addi.l #44,d0
    bcs.s s2b_drain_pending
    cmp.l 8(a3),d0
    bne.s s2b_drain_pending
    bra.s s2b_drain_chip
s2b_drain_closed_flags:
    tst.l d0
    beq.s s2b_drain_chip
    cmpi.l #4,d0
    beq.s s2b_drain_chip
    cmpi.l #20,d0
    bne.s s2b_drain_pending
s2b_drain_chip:
    movea.l (a3),a0
    move.l 4(a3),d0
    subq.l #1,d0
    bsr.w s2b_p2m_span
    btst #1,d0            ; MEMF_CHIP at the pinned allocation base
    beq.s s2b_drain_pending
    movea.l a3,a0
    movea.l a5,a1
    bsr.w AGSP_S2C_RETIRE_MIXED
    tst.l d2
    bne.s s2b_drain_release
    ; Preclose may allow released but fence-pending (state 4).
    tst.l d0
    bne.s s2b_drain_next
    cmpi.l #4,12(a3)
    beq.s s2b_drain_next
    bra.s s2b_drain_pending
s2b_drain_release:
    tst.l d0
    beq.s s2b_drain_pending
    ; Clear the inline receipt before FreeVec. Only the exact private
    ; Chip allocation is freed; record storage belongs to the semaphore.
    movea.l (a3),a1
    movea.l a3,a0
    moveq #17,d0
s2b_drain_clear:
    clr.l (a0)+
    dbra d0,s2b_drain_clear
    subq.l #1,(a2)
    movea.l $0004.w,a6
    jsr -690(a6)
    bra.s s2b_drain_next
s2b_drain_pending:
    moveq #0,d5
s2b_drain_next:
    lea 72(a3),a3
    dbra d4,s2b_drain_slot
    tst.l d2
    beq.s s2b_drain_result
    tst.l (a2)
    bne.s s2b_drain_result
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 48(a2)
s2b_drain_result:
    move.l d5,d0
    bra.s s2b_drain_return
s2b_drain_bad:
    moveq #0,d0
s2b_drain_return:
    moveq #0,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts
