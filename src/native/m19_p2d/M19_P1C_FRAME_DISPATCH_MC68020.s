; AGA_NATIVE_MIN_CPU: MC68020
; P1c priority-aware Bob frame dispatch (tools/m19_p1c_bob_priority_emit.py).
; BOBS+$07AC2..+$07AE8 = 38 instruction bytes, no data.
p1c_frame_dispatch:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    bsr.w p1c_read_mode
    tst.l d0
    beq.w p1c_frame_default
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    bra.w explicit_frame_draw_entry
p1c_frame_default:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -160(a7),a7
    bra.w p1b_frame_body
