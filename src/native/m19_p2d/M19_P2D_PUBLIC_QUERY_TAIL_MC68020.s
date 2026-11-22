; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0EDF4..$0EE00 (12 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_QUERY_RETURN_ZERO equ 0

    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #P2D_QUERY_RETURN_ZERO,d2
    rts
