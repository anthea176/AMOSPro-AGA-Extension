; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$07698..$076A8 (16 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
B8S1_BANK_RESULT_OFFSET equ 36

b8s1_bank_return:
    move.l B8S1_BANK_RESULT_OFFSET(a2),d3
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
