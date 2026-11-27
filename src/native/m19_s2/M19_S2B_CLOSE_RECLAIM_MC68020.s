; AGA_NATIVE_MIN_CPU: MC68020
; S2b CloseScreen result handling, source-derived from P2m.
; Successful close invalidates the lifetime, then drains all records.
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
    moveq #1,d0
    moveq #0,d1
    bsr.w AGSP_S2B_DRAIN
    ; Pending records remain pinned; finish the real closed screen.
p2k_close_unlink:
    ; Successful OS close: remove local link even if receipt mismatched.
    ; A mismatched durable receipt stays quarantined; never free it.
    lea p2f_root(pc),a0
    clr.l (a0)
    movea.l a3,a0
    bsr.w s2b_p2h_leave
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
