; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p0j_explicit_safe_draw_emit.py::emit_explicit_safe_draw
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0685C..$068FA (158 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0J_SAFE_ARG_OFFSET equ 68

explicit_safe_front_zero:
    move.l 4(a0),d1
    move.l d1,92(a4)
    move.l (a0),d1
    move.l d1,96(a4)
L_BOBS_0686A:
explicit_safe_buffers_ready:
    move.l 92(a4),d0
    tst.l d0
    beq.w L_BOBS_0500C
    andi.l #$00000001,d0
    bne.w L_BOBS_0500C
    move.l 96(a4),d0
    tst.l d0
    beq.w L_BOBS_0500C
    andi.l #$00000001,d0
    bne.w L_BOBS_0500C
    move.l 92(a4),d0
    move.l 96(a4),d1
    cmp.l d1,d0
    beq.w L_BOBS_0500C
    movea.l 92(a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0500C
    movea.l 92(a4),a0
    move.l (a0),d0
    move.l d0,100(a4)
    move.l 100(a4),d0
    tst.l d0
    beq.w L_BOBS_0500C
    andi.l #$00000001,d0
    bne.w L_BOBS_0500C
    movea.l 100(a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0500C
    move.l 64(a4),d3
    move.l P0J_SAFE_ARG_OFFSET(a4),d0
    movea.l a4,a1
    bsr.w L_BOBS_06686
    tst.l d3
    beq.w L_BOBS_0500C
p1b_source_patch_site:
    bra.w L_BOBS_07962
