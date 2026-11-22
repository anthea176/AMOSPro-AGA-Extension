; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$05A5C..$05A6A (14 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_RELAY_PUT_OFFSET equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #P0_RELAY_PUT_OFFSET,d7
    bra.w relay_common
