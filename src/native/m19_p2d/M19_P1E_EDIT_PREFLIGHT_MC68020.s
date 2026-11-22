; AGA_NATIVE_MIN_CPU: MC68020
; Original source: tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; BOBS+$0840A..+$08498: 142 bytes of P1e Bob image preflight checks
P1E_PREFLIGHT_ZERO equ 0

edit_preflight_slot:
    move.l 16(a4),d0
    cmpi.l #$00000001,d0
    bhi.w L_BOBS_085E8
    tst.l d0
    beq.w L_BOBS_08498
    movea.l 100(a2),a0
    tst.l (a0)
    beq.w L_BOBS_085E8
    move.l 36(a2),d0
    cmp.l (a4),d0
    bne.w L_BOBS_08498
    move.l (a2),d0
    cmp.l (a6),d0
    bne.w L_BOBS_085E8
    move.l 72(a2),d0
    cmp.l 4(a6),d0
    bne.w L_BOBS_085E8
    move.l 48(a2),d0
    cmp.l 8(a6),d0
    bne.w L_BOBS_085E8
    move.l 4(a2),d0
    cmp.l 12(a6),d0
    bne.w L_BOBS_085E8
    movea.l (a2),a0
    move.l #P1E_PREFLIGHT_ZERO,d1
    move.w 8(a0),d1
    adda.l #$00000020,a0
    move.l 4(a4),d4
L_BOBS_08474:
edit_preflight_image:
    tst.l d1
    beq.w L_BOBS_085E8
    move.l #$00000000,d0
    move.w (a0),d0
    cmp.l d4,d0
    beq.w L_BOBS_08498
    bhi.w L_BOBS_085E8
    adda.l #$00000028,a0
    subq.l #1,d1
    bra.w L_BOBS_08474
