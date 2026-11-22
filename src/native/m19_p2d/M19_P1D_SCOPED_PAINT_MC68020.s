; AGA_NATIVE_MIN_CPU: MC68020
; M19 P1d scoped Bob paint relay. Original source:
; tools/m19_p1d_limit_bob_emit.py::emit_limit_bobs.
; BOBS+$07DFE..+$07E1C, 30 instruction bytes, no data.
; p1d_drawing_id at $07E1C is zeroed data and stays outside this module.

p1d_scoped_paint:
    move.l a0,-(a7)
    lea p1d_drawing_id(pc),a0
    move.l (a2),(a0)
    movea.l (a7)+,a0
    bsr.w explicit_safe_blit_entry
    move.l a0,-(a7)
    lea p1d_drawing_id(pc),a0
    move.l #0,(a0)
    movea.l (a7)+,a0
    rts
