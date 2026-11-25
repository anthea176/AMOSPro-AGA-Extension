; AGA_NATIVE_MIN_CPU: MC68020
; Source-only include in the exact UNIT142 overlay, AFTER L2b tails.
; Original saved-register frames and Close/End entry signatures unchanged.
; No public producer of the root yet. A future producer must pin its record
; and publish it last in task context, with no concurrent lifecycle calls.
; Root +0 record pointer (P2e), +4 AMOS A5 owner, +8 AGA State,
; +12 Screen identity. Root is not cleared by Close/End. The record and Chip
; allocation must live independently of the executable until safe reclaim.
; A2 = live AGA State, A5 = AMOS context, legacy MOVEM frame on stack.
; No free of exposed memory; no modifications to the existing BOB hooks.
p2f_screen_close:
    move.l d0,-(sp)
    bsr.w p2f_gate
    tst.l d0
    beq.w p2f_close_refused
    move.l (sp)+,d0
    bsr.l L_LEGACY_CLOSE_TARGET_001EE
    bra.l L_LEGACY_CLOSE_TARGET_0012A
p2f_close_refused:
    move.l (sp)+,d0
    bra.l L_LEGACY_CLOSE_TARGET_000D2

p2f_program_end:
    move.l d0,-(sp)
    bsr.w p2f_gate
    tst.l d0
    beq.w p2f_end_refused
    move.l (sp)+,d0
    bsr.l L_LEGACY_CLOSE_TARGET_001EE
    bra.l ENTRY_LEGACY_CLOSE_CORE_00190
p2f_end_refused:
    move.l (sp)+,d0
    bra.l L_LEGACY_CLOSE_CORE_00110

p2f_gate:
    movem.l d1-d7/a0-a6,-(sp)
    lea p2f_root(pc),a3
    move.l (a3),d0
    beq.w p2f_allow
    btst #0,d0
    bne.w p2f_deny
    movea.l d0,a4        ; trusted persistent internal record
    move.l 12(a4),d2
    ; No owned channels, no VP call. A quarantined previous generation
    ; must never be dereferenced through a stale Screen/ViewPort.
    tst.l d2
    beq.w p2f_allow
    cmpi.l #4,d2
    beq.w p2f_allow
    cmpi.l #5,d2
    beq.w p2f_context
    cmpi.l #7,d2
    beq.w p2f_context
    cmpi.l #13,d2
    beq.w p2f_context
    cmpi.l #15,d2
    bne.w p2f_deny
p2f_context:
    move.l a5,d0
    cmp.l 4(a3),d0
    bne.w p2f_deny
    move.l a2,d0
    beq.w p2f_deny
    cmp.l 8(a3),d0
    bne.w p2f_deny
    move.l (a2),d0
    beq.w p2f_deny
    cmp.l 12(a3),d0
    bne.w p2f_deny
    btst #3,d2
    beq.w p2f_call
    ; Screen.ViewPort = +44, source-proven screen layout (NDK V39).
    addi.l #44,d0
    bcs.w p2f_deny
    cmp.l 8(a4),d0
    bne.w p2f_deny
p2f_call:
    movea.l a4,a0
    movea.l 8(a2),a1
    bsr.w AGSP_P2E_RETIRE
    ; Allow original teardown only when ownership really cleared. A failed
    ; post-release scan may require Close itself to remove remaining refs;
    ; record stays quarantined. Never erase receipts to manufacture PASS.
    cmpi.l #4,12(a4)
    beq.w p2f_allow
    bra.w p2f_deny
p2f_allow:
    moveq #1,d0
    bra.w p2f_return
p2f_deny:
    moveq #0,d0
p2f_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

    include "M19_S1P2E_RETIRE_MC68020.s"

; Last 16 bytes of candidate UNIT142. No absolute addresses or relocations.
p2f_root:
    dcb.b 16,0
