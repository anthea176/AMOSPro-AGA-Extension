; AGA_NATIVE_MIN_CPU: MC68020
; P1e public Bob Delete argument staging from tools/m19_p1e_bank_edit_emit.py.
; BOBS+$07F00..+$07F2E = 46 MC68020 bytes; the final edit cleanup is shared.
P1E_EDIT_FRAME_BYTES equ 256
P1E_DEL_LAST equ 20
P1E_DEL_FIRST equ 16
P1E_DEL_BANK equ 36

p1e_del_bob:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P1E_EDIT_FRAME_BYTES(a7),a7
    movea.l a7,a2
    move.l d3,P1E_DEL_LAST(a2)
    tst.l d3
    beq.w edit_bad_del
    move.l (a3)+,P1E_DEL_FIRST(a2)
    move.l (a3)+,P1E_DEL_BANK(a2)
    bra.w edit_begin
L_BOBS_07F20:
edit_bad_del:
    move.l (a3)+,d0
    move.l (a3)+,d0
    move.l #0,d3
    bra.w edit_return
