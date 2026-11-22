; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$079F2..$07A14 (34 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P1B_PAINT_CLIPPED_FLAG equ 1

    movea.l 120(a4),a3
    tst.l d3
    beq.w L_BOBS_07A08
    move.l d1,72(a4)
    move.l d4,76(a4)
    bra.w UNIT_BOBS+$04F72
L_BOBS_07A08:
    move.l #P1B_PAINT_CLIPPED_FLAG,116(a4)
    bra.w L_BOBS_0500C
