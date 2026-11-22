; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$06254..$06264 (16 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0J_IMAGE_RESULT_OFFSET equ 4

img_gate_return:
    move.l P0J_IMAGE_RESULT_OFFSET(a2),d3
    lea 160(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
