; AGA_NATIVE_MIN_CPU: MC68020
; P2l-c read-only detail of the already-rejected P2l-b idle guard.
; Only reachable from p2l_not_idle inside the existing borrowed observer.
; A5 validated live GfxBase V39/V40. D3/D4/D7/A3-A6 preserved.
; No View/LOF/SHF pointer dereference. No new write, wait or free.
; -256-mask: 1 View, 2 LOF, 4 SHF, 8 terminal WAIT,
; 16 copinit unavailable, 32 copinit changed during detail.
; Zero mask still returns -185 (transient or unresolved), never success.
p2lc_idle_detail:
    moveq #0,d5
    tst.l 34(a5)
    beq.s p2lc_copinit
    ori.b #1,d5
p2lc_copinit:
    movea.l 38(a5),a0
    move.l #180,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.s p2lc_unmapped
    cmpa.l 38(a5),a0
    bne.s p2lc_changed
    lea 164(a0),a1
    move.l a1,d0
    cmp.l 50(a5),d0
    beq.s p2lc_shf
    ori.b #2,d5
p2lc_shf:
    cmp.l 54(a5),d0
    beq.s p2lc_wait
    ori.b #4,d5
p2lc_wait:
    cmpi.l #$fffffffe,164(a0)
    beq.s p2lc_recheck
    ori.b #8,d5
p2lc_recheck:
    cmpa.l 38(a5),a0
    beq.s p2lc_result
p2lc_changed:
    ori.b #32,d5
    bra.s p2lc_result
p2lc_unmapped:
    ori.b #16,d5
p2lc_result:
    tst.l d5
    beq.s p2lc_unresolved
    move.l #-256,d0
    sub.l d5,d0
    rts
p2lc_unresolved:
    move.l #-185,d0
    rts
