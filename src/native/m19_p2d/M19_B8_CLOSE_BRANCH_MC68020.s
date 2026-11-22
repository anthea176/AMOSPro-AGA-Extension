; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$071E8..$071EC (4 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
B8_CLOSE_BRANCH_LOW_BYTE equ 232

b8_b7_close_return:
    bra.w L_BOBS_0A1D2+B8_CLOSE_BRANCH_LOW_BYTE-232
