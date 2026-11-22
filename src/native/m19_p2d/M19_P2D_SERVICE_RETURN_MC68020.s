; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0E59E..$0E5B0 (18 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_SERVICE_RETURN_D2 equ 0

    move.l (a4),d3
    move.l #P2D_SERVICE_RETURN_D2,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
