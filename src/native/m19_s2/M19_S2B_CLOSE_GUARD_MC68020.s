; AGA_NATIVE_MIN_CPU: MC68020
; S2b collective Close/End guard. Same legacy wait/close paths.
; Authenticate lifetime and borrow, then retire all three records.
p2f_screen_close:
    move.l d0,-(sp)
    bsr.w p2f_gate
    tst.l d0
    beq.s p2f_close_refused
    move.l (sp)+,d0
    bsr.l L_LEGACY_CLOSE_TARGET_001EE
    bsr.l L_LEGACY_CLOSE_TARGET_00140
    tst.l d0
    beq.s p2k_close_timeout
    bsr.l L_LEGACY_CLOSE_TARGET_000D8
    bra.l L_LEGACY_CLOSE_TARGET_00010
p2k_close_timeout:
    bsr.w p2k_abort_close
    bra.l L_LEGACY_CLOSE_TARGET_000D2
p2f_close_refused:
    move.l (sp)+,d0
    bra.l L_LEGACY_CLOSE_TARGET_000D2

p2f_program_end:
    move.l d0,-(sp)
    bsr.w p2f_gate
    tst.l d0
    beq.s p2f_end_refused
    move.l (sp)+,d0
    bsr.l L_LEGACY_CLOSE_TARGET_001EE
    bsr.l L_LEGACY_CLOSE_CORE_001A6
    tst.l d0
    beq.s p2k_end_timeout
    bsr.l L_LEGACY_CLOSE_CORE_00116
    bra.l L_LEGACY_CLOSE_CORE_0000C
p2k_end_timeout:
    bsr.w p2k_abort_close
    bra.l L_LEGACY_CLOSE_CORE_00110
p2f_end_refused:
    move.l (sp)+,d0
    bra.l L_LEGACY_CLOSE_CORE_00110

p2f_gate:
    movem.l d1-d7/a0-a6,-(sp)
    movea.l p2f_root(pc),a3
    move.l a3,d0
    beq.w p2k_unlinked_close
    moveq #0,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    beq.w p2f_deny     ; never unlock a foreign or incomplete borrow
    move.l a3,d1
    movea.l d0,a3
    cmp.l d1,d0
    bne.w p2k_unlock_deny
    move.l 16(a3),d0
    cmp.l 48(a3),d0
    bne.w p2k_unlock_deny
    cmpa.l 4(a3),a5
    bne.w p2k_unlock_deny
    move.l a2,d0
    beq.w p2k_unlock_deny
    cmpa.l 8(a3),a2
    bne.w p2k_unlock_deny
    move.l (a2),d0
    beq.w p2k_unlock_deny
    cmp.l 12(a3),d0
    bne.w p2k_unlock_deny
    movea.l a3,a0
    movea.l 8(a2),a1
    moveq #0,d0        ; collective preclose ignores selector D1
    bsr.w AGSP_S2B_DRAIN
    tst.l d0
    beq.w p2k_unlock_deny
    bra.s p2f_allow
p2k_unlinked_close:
    ; No local link is NOT evidence of no Sprite after a forced reload.
    ; Inspect only a locked, named registry, never a former VP or record.
    move.l a2,d0
    beq.w p2f_allow
    tst.l (a2)
    beq.w p2f_allow
    moveq #0,d0
    bsr.w s2b_p2h_enter
    tst.l d0
    bne.s p2k_unlinked_found
    cmpi.l #1,d1          ; absent registry is the ordinary non-Sprite path
    beq.w p2f_allow
    bra.w p2f_deny       ; unknown/busy registry: fail closed
p2k_unlinked_found:
    movea.l d0,a3
    move.l (a2),d0
    cmp.l 12(a3),d0
    beq.s p2k_unlock_deny ; same Screen without a live link: quarantine
    movea.l a3,a0
    bsr.w s2b_p2h_leave
    tst.l d0
    beq.s p2f_deny
    bra.s p2f_allow
p2k_unlock_deny:
    movea.l a3,a0
    bsr.w s2b_p2h_leave
    bra.s p2f_deny
p2f_allow:
    moveq #1,d0
    bra.s p2f_return
p2f_deny:
    moveq #0,d0
p2f_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

; Called ONLY after gate success, before legacy return on failure.
p2k_abort_close:
    movem.l d0-d1/a0,-(sp)
    movea.l p2f_root(pc),a0
    move.l a0,d0
    beq.s p2k_abort_done
    bsr.w s2b_p2h_leave
p2k_abort_done:
    movem.l (sp)+,d0-d1/a0
    rts

    include "M19_S2B_RETIRE_PAIR_MC68020.s"
    include "M19_S2B_CLOSE_RECLAIM_MC68020.s"
    include "M19_S2B_REGISTRY_MC68020.s"
    include "M19_S2B_PERSIST_ROOT_MC68020.s"
p2f_root:
    dc.l 0,$41475349,$00010010,0
