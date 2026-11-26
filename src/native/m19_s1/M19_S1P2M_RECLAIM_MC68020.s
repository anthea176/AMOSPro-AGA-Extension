; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2m: release the exact owned allocations only after private or
; confirmed retirement. Closed-root retry never touches the old ViewPort.
; Live entry called only under the verified owner/cell transaction.
p2g_end_close:
    jsr -66(a6)           ; Intuition CloseScreen, real BOOL in D0
    bsr.s p2g_closed
    tst.l d0
    beq.s p2g_end_pending
    clr.l (a2)
    bra.l L_LEGACY_CLOSE_CORE_000D4
p2g_end_pending:
    bra.l L_LEGACY_CLOSE_CORE_00110

p2g_public_close:
    bsr.l ENTRY_LEGACY_HELPER_052CA_00000
    ; Helper ends with CloseScreen then RTS, preserving D0 result.
    bsr.s p2g_closed
    tst.l d0
    beq.s p2g_close_pending
    clr.l (a2)
    bra.l L_LEGACY_CLOSE_TARGET_00096
p2g_close_pending:
    bra.l L_LEGACY_CLOSE_TARGET_000D2

p2g_closed:
    ; A2=State, A5=owner, (A2)=screen BEFORE legacy clear.
    ; D0=real CloseScreen result. Preserve all except decision D0.
    movem.l d1-d7/a0-a6,-(sp)
    move.l d0,d7
    tst.l d7
    beq.w p2g_close_failed
    movea.l p2f_root(pc),a3
    move.l a3,d0
    beq.w p2g_continue
    tst.l (a3)
    beq.w p2k_close_unlink
    move.l a5,d0
    cmp.l 4(a3),d0
    bne.w p2k_close_unlink
    move.l a2,d0
    cmp.l 8(a3),d0
    bne.s p2k_close_unlink
    move.l (a2),d0
    beq.s p2k_close_unlink
    cmp.l 12(a3),d0
    bne.s p2k_close_unlink
    tst.l d7
    beq.s p2g_close_failed
    clr.l 12(a3)         ; durable receipt of this successful close
    clr.l 48(a3)         ; no longer a live lifetime owner
    movea.l a3,a0
    movea.l 8(a2),a1     ; still-open graphics.library
    bsr.s AGSP_P2G_RECLAIM
    ; If pending, keep root and both allocations, but finish closed screen.
p2k_close_unlink:
    ; Successful OS close: remove local link even if receipt mismatched.
    ; A mismatched durable receipt stays quarantined; never free it.
    lea p2f_root(pc),a0
    clr.l (a0)
    movea.l a3,a0
    bsr.w p2h_leave
p2g_continue:
    moveq #1,d0
    bra.s p2g_closed_return
p2g_close_failed:
    ; Screen/graphics/intuition remain live; retry, not blind clear.
    bsr.w p2k_abort_close
    moveq #0,d0
p2g_closed_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

AGSP_P2G_RECLAIM:
    moveq #0,d0
    bra.s p2m_reclaim
AGSP_P2M_RELEASE_LIVE:
    moveq #1,d0
p2m_reclaim:
    ; A0=pinned root, A1=live GfxBase. D0=1 released, 0 pending.
    movem.l d2-d7/a0-a6,-(sp)
    move.l d0,d2
    movea.l a0,a2
    movea.l a1,a5
    move.l a2,d0
    beq.w p2g_reject
    btst #0,d0
    bne.w p2g_reject
    move.l (a2),d0
    beq.w p2g_done
    btst #0,d0
    bne.w p2g_reject
    movea.l d0,a3
    tst.l d2
    bne.s p2m_live_check
    tst.l 12(a2)
    bne.w p2g_reject
    tst.l 48(a2)
    bne.w p2g_reject
    move.l 12(a3),d7
    beq.s p2m_retire
    cmpi.l #4,d7
    beq.s p2m_retire
    cmpi.l #20,d7
    bne.w p2g_reject
    bra.s p2m_retire
p2m_live_check:
    tst.l 12(a2)
    beq.w p2g_reject
    move.l 48(a2),d1
    beq.w p2g_reject
    cmp.l 16(a2),d1
    bne.w p2g_reject
p2m_retire:
    movea.l a3,a0
    movea.l a5,a1
    bsr.w AGSP_P2E_RETIRE
    tst.l d0
    beq.w p2g_reject
    move.l 12(a3),d7
    beq.s p2g_release
    cmpi.l #20,d7
    bne.w p2g_reject
p2g_release:
    ; Pinned, separate private allocations; producer must retain provenance.
    movea.l (a3),a4
    move.l a4,d0
    cmp.l a3,d0
    beq.w p2g_reject
    move.l a3,d1
    cmp.l d0,d1
    bcs.s p2g_record_below
    add.l 4(a3),d0
    bcs.w p2g_reject
    cmp.l d0,d1
    bcs.w p2g_reject
    bra.s p2g_clear
p2g_record_below:
    addi.l #40,d1
    bcs.w p2g_reject
    cmp.l d1,d0
    bcs.s p2g_reject
p2g_clear:
    ; Clear durable owner receipt BEFORE release; no second attempt can
    ; free either allocation. No waits or future pointer publication here.
    clr.l (a2)
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    clr.l 48(a2)
    movea.l $0004.w,a6
    movea.l a4,a1
    jsr -690(a6)          ; FreeVec exact P2a AllocVec base
    movea.l a3,a1
    jsr -690(a6)          ; FreeVec separate owner record
p2g_done:
    moveq #1,d0
    bra.s p2g_return
p2g_reject:
    moveq #0,d0
p2g_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

