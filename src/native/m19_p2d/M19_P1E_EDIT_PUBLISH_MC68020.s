; AGA_NATIVE_MIN_CPU: MC68020
; From tools/m19_p1e_bank_edit_emit.py::emit_bank_edit
; BOBS+$084C6..+$08516, P1e Bob bank publication and registry ownership
P1E_PUBLISH_CLEAR equ 0

edit_publish:
    movea.l 56(a2),a0
    movea.l 60(a2),a1
    move.l (a0),(a1)
    movea.l 52(a2),a4
    move.l a1,(a4)
    move.l #P1E_PUBLISH_CLEAR,(a0)
    move.l a0,64(a2)
    movea.l 84(a2),a0
    move.l a0,d0
    beq.w L_BOBS_084F0
    movea.l 80(a2),a1
    move.l (a0),(a1)
L_BOBS_084F0:
edit_registry_insert:
    move.l 88(a2),d0
    beq.w L_BOBS_08502
    movea.l d0,a0
    movea.l 80(a2),a1
    move.l (a1),(a0)
    move.l a0,(a1)
L_BOBS_08502:
edit_registry_owner:
    movea.l 76(a2),a0
    move.l #$00000000,(a0)
    tst.l 4(a0)
    beq.w L_BOBS_08516
    move.l a5,(a0)
