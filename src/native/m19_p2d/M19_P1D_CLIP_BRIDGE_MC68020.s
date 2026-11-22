; AGA_NATIVE_MIN_CPU: MC68020
; M19 P1d clipped painter -> original Safe Blitter.
; From tools/m19_p1d_limit_bob_emit.py::emit_limit_bobs.
; BOBS+$07E20..+$07E6A = 74 MC68020 instruction bytes.
P1D_CLIP_RECORD_OFFSET equ 8
P1D_CLIP_STRIDE_OFFSET equ 216

p1d_clip_painter:
    lea p1d_drawing_id(pc),a0
    tst.l (a0)
    beq.w p1d_continue
    bsr.w p1c_context
    move.l a0,d0
    beq.w p1d_continue
    adda.l #P1D_CLIP_RECORD_OFFSET,a0
    movea.l a0,a1
    lea p1d_drawing_id(pc),a0
    move.l (a0),d0
    lsl.l #4,d0
    movea.l a1,a0
    adda.l d0,a0
    move.l a0,-(a7)
    movea.l a1,a0
    bsr.w p1d_intersect
    movea.l (a7)+,a0
    tst.l d0
    beq.w private_blit_clipped_ok
    bsr.w p1d_intersect
    tst.l d0
    beq.w private_blit_clipped_ok
p1d_continue:
    move.l P1D_CLIP_STRIDE_OFFSET(a4),d0
    bra.w p1d_resume_bitmap
