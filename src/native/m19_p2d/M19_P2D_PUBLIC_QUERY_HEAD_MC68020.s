; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0EDD0..$0EDF4 (36 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_PUBLIC_VALUE_OFFSET equ 4

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    move.l d3,d0
    movea.l a7,a1
    bsr.w L_BOBS_0EABA
    tst.l d3
    beq.w L_BOBS_0EDEE
    move.l P2D_PUBLIC_VALUE_OFFSET(a7),d3
    bra.w L_BOBS_0EDF4
L_BOBS_0EDEE:
    move.l #$FFFF7FFF,d3
