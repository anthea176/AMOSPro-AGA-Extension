; AGA_NATIVE_MIN_CPU: MC68020
; P2b Flip cached planar variant, per-object mode, and hotspot mirroring.
; SOURCE: tools/m19_p2b_bob_flip_emit.py::emit_bob_flip (no disassembly).
; BOBS+$09F26..+$0A0A9, exactly 388 instruction bytes.
; Internal caching is private; Blitter completion precedes freeing Chip.
; Two noncanonical MULU.L extension words are preserved from source.
P2BV_FRAME_BYTES   equ 80
P2BV_CACHE_MODE    equ 4
P2BV_CACHE_BANK    equ 8
P2BV_CACHE_IMAGE   equ 12
P2BV_CACHE_PAYLOAD equ 16
P2BV_CACHE_GEN     equ 20
P2BV_CACHE_PIXELS  equ 24
P2BV_CACHE_MASK    equ 28
P2BV_CACHE_BLOCK   equ 32
P2BV_CACHE_SIZE    equ 36

; D0 bob ID, D1 bank, D4 image, A1 checked image descriptor.
p2b_variant:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    lea -P2BV_FRAME_BYTES(a7),a7
    movea.l a7,a2
    move.l d1,(a2)
    move.l d4,4(a2)
    move.l a1,8(a2)
    bsr.w p2b_mode
    tst.l d3
    beq.w p2b_variant_ok
    movea.l a0,a3
    move.l d3,12(a2)
    movea.l a2,a1
    adda.l #32,a1
    move.l (a2),d3
    bsr.w explicit_bank_lookup_entry
    tst.l d3
    beq.w p2b_variant_fail
    movea.l 8(a2),a4
    tst.l P2BV_CACHE_BLOCK(a3)
    beq.w p2b_variant_miss

    ; Same cache key is shared by paint and masked collision.
    move.l 12(a2),d0
    cmp.l P2BV_CACHE_MODE(a3),d0
    bne.w p2b_variant_miss
    move.l (a2),d0
    cmp.l P2BV_CACHE_BANK(a3),d0
    bne.w p2b_variant_miss
    move.l 4(a2),d0
    cmp.l P2BV_CACHE_IMAGE(a3),d0
    bne.w p2b_variant_miss
    move.l 32(a2),d0
    cmp.l P2BV_CACHE_PAYLOAD(a3),d0
    bne.w p2b_variant_miss
    move.l 36(a2),d0
    cmp.l P2BV_CACHE_GEN(a3),d0
    bne.w p2b_variant_miss
    move.l (a4),d0
    cmp.l P2BV_CACHE_PIXELS(a3),d0
    bne.w p2b_variant_miss
    move.l 4(a4),d0
    cmp.l P2BV_CACHE_MASK(a3),d0
    bne.w p2b_variant_miss
    bra.w p2b_variant_publish

p2b_variant_miss:
    move.l 20(a4),d4
    move.l 24(a4),d6
    dc.w $4C04,$6000     ; MULU.L D4,D6: source-emitter encoding
    move.l d6,16(a2)
    tst.l 4(a4)
    beq.w p2b_variant_prepare
    move.l (a4),d0
    add.l d6,d0
    bcs.w p2b_variant_fail
    cmp.l 4(a4),d0
    bne.w p2b_variant_fail
    add.l 24(a4),d6
    addq.l #1,d4

p2b_variant_prepare:
    movea.l (a4),a0
    move.l 8(a4),d0
    move.l 12(a4),d1
    move.l 12(a2),d5
    movea.l $0004.w,a6
    bsr.w p2b_materialize_chip
    tst.l d3
    beq.w p2b_variant_fail
    move.l a1,20(a2)
    move.l d7,24(a2)
    bsr.w p2b_free_slot

    ; Publish an all-or-nothing cache identity and DMA addresses.
    move.l 12(a2),P2BV_CACHE_MODE(a3)
    move.l (a2),P2BV_CACHE_BANK(a3)
    move.l 4(a2),P2BV_CACHE_IMAGE(a3)
    move.l 32(a2),P2BV_CACHE_PAYLOAD(a3)
    move.l 36(a2),P2BV_CACHE_GEN(a3)
    move.l (a4),P2BV_CACHE_PIXELS(a3)
    move.l 4(a4),P2BV_CACHE_MASK(a3)
    move.l 20(a2),P2BV_CACHE_BLOCK(a3)
    move.l 24(a2),P2BV_CACHE_SIZE(a3)

p2b_variant_publish:
    move.l P2BV_CACHE_BLOCK(a3),d0
    move.l d0,(a4)
    tst.l 4(a4)
    beq.w p2b_variant_ok
    move.l 20(a4),d1
    move.l 24(a4),d2
    dc.w $4C01,$2000     ; MULU.L D1,D2: source-emitter encoding
    add.l d2,d0
    move.l d0,4(a4)
p2b_variant_ok:
    moveq #1,d3
    bra.w p2b_variant_return
p2b_variant_fail:
    moveq #0,d3
p2b_variant_return:
    lea P2BV_FRAME_BYTES(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    moveq #0,d2
    rts

; A0 points to signed original HotSpot words; A1 image descriptor.
p2b_adjust_anchor:
    btst #0,d3
    beq.w p2b_axis_done_0
    move.w (a0),d2
    ext.l d2
    lsl.l #1,d2
    sub.l 8(a1),d2
    addq.l #1,d2
    add.l d2,d1
p2b_axis_done_0:
    btst #1,d3
    beq.w p2b_axis_done_1
    move.w 2(a0),d2
    ext.l d2
    lsl.l #1,d2
    sub.l 12(a1),d2
    addq.l #1,d2
    add.l d2,d4
p2b_axis_done_1:
    rts
