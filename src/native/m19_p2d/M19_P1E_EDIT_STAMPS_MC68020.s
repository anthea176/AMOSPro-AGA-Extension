; AGA_NATIVE_MIN_CPU: MC68020
; Original: tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; BOBS+$08516..+$085A6 (144 bytes) selected bank refs / Bob stamps
P1E_STAMP_OBJECT_COUNT equ 64

edit_selection:
    lea L_BOBS_020A2(pc),a0
    move.l 36(a2),d0
    cmp.l (a0),d0
    bne.w L_BOBS_08542
    move.l (a2),d0
    cmp.l 4(a0),d0
    bne.w L_BOBS_08542
    move.l 48(a2),d0
    cmp.l 8(a0),d0
    bne.w L_BOBS_08542
    move.l 8(a2),d0
    move.l d0,4(a0)
L_BOBS_08542:
edit_update_refs:
    movea.l 92(a2),a4
    movea.l 96(a2),a6
    move.l #P1E_STAMP_OBJECT_COUNT,d7
L_BOBS_08550:
edit_commit_slot:
    tst.l 16(a4)
    beq.w L_BOBS_085A6
    move.l 36(a2),d0
    cmp.l (a4),d0
    bne.w L_BOBS_085A6
    move.l 4(a4),d0
    move.l 20(a2),d1
    beq.w L_BOBS_08588
    cmp.l 16(a2),d0
    bcs.w L_BOBS_08588
    cmp.l d1,d0
    bhi.w L_BOBS_08588
    move.l #$00000000,16(a4)
    bra.w L_BOBS_085A6
L_BOBS_08588:
edit_refresh_stamp:
    move.l 8(a2),d0
    move.l d0,(a6)
    move.l 68(a2),d0
    move.l d0,4(a6)
    move.l 48(a2),d0
    move.l d0,8(a6)
    move.l 12(a2),d0
    move.l d0,12(a6)
