; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$06264..$0627E (26 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0J_PRECHECK_RETURN_D2 equ 0

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    bsr.w image_frame_preflight_entry
    tst.l d3
    beq.w L_BOBS_06276
    bsr.w routed_paint_all_entry
L_BOBS_06276:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #P0J_PRECHECK_RETURN_D2,d2
    rts
