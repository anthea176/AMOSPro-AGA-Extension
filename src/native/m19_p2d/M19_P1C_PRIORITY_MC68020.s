; AGA_NATIVE_MIN_CPU: MC68020
; P1c source priority setter (tools/m19_p1c_bob_priority_emit.py).
; BOBS+$07B84..+$07BBA = 54 bytes, MC68020 only, no data.
p1c_priority_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    cmpi.l #3,d3
    bhi.w p1c_priority_fail
    move.l d3,d7
    bsr.w p1c_context
    move.l a0,d0
    beq.w p1c_priority_fail
    move.l d7,4(a0)
    move.l #1,d3
    bra.w p1c_priority_return
p1c_priority_fail:
    move.l #0,d3
p1c_priority_return:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
