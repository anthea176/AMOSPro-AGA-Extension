; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; Audited bytes checked against the official M19 P2d library.
; BOBS+$085A6..$085E8 (66 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P1E_BATCH_COMMIT_DONE equ 1

edit_commit_next:
    adda.l #$00000018,a4
    adda.l #$00000010,a6
    subq.l #1,d7
    bne.w L_BOBS_08550
    dc.w $FE11,$F700,AMOS_MAIN_CHANGE
    move.l 84(a2),d0
    beq.w L_BOBS_085D0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_085D0:
edit_drop_old_bank:
    lea 64(a2),a0
    movea.l 56(a2),a1
    dc.w $FE11,$F700,AMOS_MAIN_LIST_DELETE
    move.l #P1E_BATCH_COMMIT_DONE,d3
    bra.w L_BOBS_08626
