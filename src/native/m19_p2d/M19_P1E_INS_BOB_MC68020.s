; AGA_NATIVE_MIN_CPU: MC68020
; P1e public Bob Insert argument staging from tools/m19_p1e_bank_edit_emit.py.
; BOBS+$07F2E..+$07F54 = 38 MC68020 code bytes.
P1E_INS_FRAME_BYTES equ 256
P1E_INS_DEPTH equ 32
P1E_INS_HEIGHT equ 28
P1E_INS_WIDTH equ 24
P1E_INS_FIRST equ 16
P1E_INS_BANK equ 36
P1E_INS_LAST equ 20

p1e_ins_bob:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P1E_INS_FRAME_BYTES(a7),a7
    movea.l a7,a2
    move.l d3,P1E_INS_DEPTH(a2)
    move.l (a3)+,P1E_INS_HEIGHT(a2)
    move.l (a3)+,P1E_INS_WIDTH(a2)
    move.l (a3)+,P1E_INS_FIRST(a2)
    move.l (a3)+,P1E_INS_BANK(a2)
    move.l #0,P1E_INS_LAST(a2)
