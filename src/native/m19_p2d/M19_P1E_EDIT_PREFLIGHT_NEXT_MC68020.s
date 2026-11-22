; AGA_NATIVE_MIN_CPU: MC68020
; From tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; BOBS+$08498..+$084C6 = 46 bytes, object iteration + Chip release
P1E_NEXT_OBJECT_STRIDE equ 24

edit_preflight_next:
    adda.l #P1E_NEXT_OBJECT_STRIDE,a4
    adda.l #$00000010,a6
    subq.l #1,d7
    bne.w L_BOBS_0840A
    move.l 84(a2),d0
    beq.w L_BOBS_084C6
    movea.l d0,a0
    lea 8(a0),a1
    movea.l 44(a2),a4
    bsr.w L_BOBS_03D9E
    tst.l d3
    beq.w L_BOBS_085E8
