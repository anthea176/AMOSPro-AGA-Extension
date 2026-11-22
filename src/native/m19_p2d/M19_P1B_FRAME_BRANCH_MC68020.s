; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$068FA..$068FE (4 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P1B_BRANCH_LOW_BYTE equ 198

p1b_frame_draw_entry:
    bra.w L_BOBS_07AC2+P1B_BRANCH_LOW_BYTE-198
