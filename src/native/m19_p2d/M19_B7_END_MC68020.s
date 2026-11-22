; AGA_NATIVE_MIN_CPU: MC68020
; M19 P0j B7 real AMOS End callback with guarded screen teardown.
; Source: tools/m19_p0j_end_lifecycle_emit.py::emit_end_lifecycle.
; BOBS+$06EAC..+$06FA6 = 250 instruction bytes; no DATA.
; Original B7 epilogue is source-patched by P2b to owner cache cleanup.
B7_END_STATE_A5 equ $01C8
B7_END1_A5 equ $01CC
B7_END2_A5 equ $01D0

b7_end_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w b7_end_return
    move.l a5,d0
    tst.l d0
    beq.w b7_end_return
    move.l d0,d1
    andi.l #1,d1
    bne.w b7_end_return
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b7_end_return
    move.l B7_END_STATE_A5(a5),d0
    tst.l d0
    beq.w b7_end_return
    move.l d0,d1
    andi.l #1,d1
    bne.w b7_end_return
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b7_end_return
    lea b7_end_entry(pc),a0
    move.l a0,d1
    move.l B7_END1_A5(a5),d0
    cmp.l d1,d0
    bne.w b7_end_return
    move.l B7_END2_A5(a5),d0
    cmp.l d1,d0
    bne.w b7_end_return
    lea program_end_bridge_entry(pc),a0
    move.l a0,B7_END1_A5(a5)
    move.l a0,B7_END2_A5(a5)
    bsr.w program_end_bridge_entry
    move.l B7_END_STATE_A5(a5),d0
    tst.l d0
    beq.w b7_end_return
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w b7_end_return
    movea.l B7_END_STATE_A5(a5),a0
    tst.l (a0)
    bne.w b7_end_pending
    lea frame_guard_state(pc),a0
    move.l 4(a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w b7_end_return
    move.l #0,(a0)
    move.l #0,4(a0)
    move.l #0,8(a0)
    move.l #0,12(a0)
    move.l #0,16(a0)
    move.l #0,20(a0)
    bra.w b7_end_return
; BOBS equ b7_end_pending = UNIT_BOBS+$06F94.
    lea b7_end_entry(pc),a0
    move.l a0,B7_END1_A5(a5)
    move.l a0,B7_END2_A5(a5)
; BOBS equ b7_end_return = UNIT_BOBS+$06FA0.
    bra.w p2b_close_return
    rts
