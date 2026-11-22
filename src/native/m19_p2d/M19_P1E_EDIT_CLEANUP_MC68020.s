; AGA_NATIVE_MIN_CPU: MC68020
; P1e safe detached cache/bank cleanup from tools/m19_p1e_bank_edit_emit.py.
; BOBS+$085E8..+$08632 = 74 bytes, including one AMOS Main Lst.Del pseudo-call.
; AMOS_MAIN_LIST_DELETE is fixed by tools/amos_main_abi.py (index 93).
P1E_NEW_CACHE equ 88
P1E_NEW_NODE equ 60
P1E_DETACHED equ 64
P1E_GFX equ 44
P1E_EDIT_STACK equ 256

edit_cleanup:
    move.l P1E_NEW_CACHE(a2),d0
    beq.w edit_cleanup_bank
    movea.l d0,a0
    lea 8(a0),a1
    movea.l P1E_GFX(a2),a4
    bsr.w checked_release_entry
    movea.l P1E_NEW_CACHE(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_0860A:
edit_cleanup_bank:
    move.l P1E_NEW_NODE(a2),d0
    beq.w edit_fail
    lea P1E_DETACHED(a2),a0
    movea.l P1E_NEW_NODE(a2),a1
    dc.w $FE11,$F700,AMOS_MAIN_LIST_DELETE  ; verified Lst.Del pseudo-opcode
L_BOBS_08620:
edit_fail:
    move.l #0,d3
L_BOBS_08626:
edit_return:
    lea P1E_EDIT_STACK(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
