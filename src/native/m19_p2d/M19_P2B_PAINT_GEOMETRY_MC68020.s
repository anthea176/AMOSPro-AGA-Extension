; AGA_NATIVE_MIN_CPU: MC68020
; P2b Flip painter and paired collision geometry (full 68020-source semantics).
; AUTHORITATIVE EMITTER: tools/m19_p2b_bob_flip_emit.py::emit_bob_flip
; Original BOBS span +$0A0AA..+$0A1D1 (296 instruction bytes).
; One original PC-relative 68020 full-format LEA uses $41FB,$0170.

; In Draw, the mirror cache and HotSpot adjustment share the collision path.
p2b_paint:
    move.l a0,-(a7)
    dc.w $41FB,$0170
    dc.l p1d_drawing_id-(*-2)    ; full-format PC32, source-pinned
    move.l (a0),d0
    bsr.w p2b_mode
    tst.l d3
    beq.w p2b_paint_normal
    move.l d3,-(a7)
    move.l 64(a4),d1
    move.l 68(a4),d4
    movea.l a4,a1
    bsr.w p2b_variant
    tst.l d3
    beq.w p2b_paint_fail
    move.l (a7)+,d3
    movea.l (a7),a0
    adda.l #28,a0
    move.l 72(a4),d1
    move.l 76(a4),d4
    bsr.w p2b_adjust_anchor
    movea.l (a7)+,a0
    bra.w p2b_paint_hotspot
p2b_paint_normal:
    movea.l (a7)+,a0
p2b_paint_hotspot:
    bsr.w p1b_hotspot_origin_entry
    bra.w p2b_paint_continue
p2b_paint_fail:
    addq.l #8,a7
    movea.l 120(a4),a3
    bra.w draw_reject

; Pair A/B use the identical cached variants and mirrored coordinates.
p2b_geometry:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    lea -20(a7),a7
    movea.l a7,a2
    move.l d0,(a2)
    move.l d1,4(a2)
    move.l a0,8(a2)
    move.l a3,12(a2)

    move.l (a2),d0
    bsr.w p2b_mode
    tst.l d3
    beq.w p2b_geo_done_0
    move.l d3,16(a2)
    movea.l 8(a2),a4
    movea.l a4,a1
    adda.l #24,a1
    move.l (a4),d1
    move.l 4(a4),d4
    bsr.w p2b_variant
    tst.l d3
    beq.w p2b_geometry_fail
    move.l 16(a2),d3
    movea.l 12(a2),a0
    move.l 8(a4),d1
    move.l 12(a4),d4
    bsr.w p2b_adjust_anchor
    move.l d1,8(a4)
    move.l d4,12(a4)
p2b_geo_done_0:
    move.l 4(a2),d0
    bsr.w p2b_mode
    tst.l d3
    beq.w p2b_geo_done_1
    move.l d3,16(a2)
    movea.l 8(a2),a4
    adda.l #60,a4
    movea.l a4,a1
    adda.l #24,a1
    move.l (a4),d1
    move.l 4(a4),d4
    bsr.w p2b_variant
    tst.l d3
    beq.w p2b_geometry_fail
    move.l 16(a2),d3
    movea.l 12(a2),a0
    addq.l #4,a0
    move.l 8(a4),d1
    move.l 12(a4),d4
    bsr.w p2b_adjust_anchor
    move.l d1,8(a4)
    move.l d4,12(a4)
p2b_geo_done_1:
    lea 20(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    bra.w p2a_pair_geometry_entry
p2b_geometry_fail:
    moveq #0,d3
    lea 20(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    moveq #0,d2
    rts
