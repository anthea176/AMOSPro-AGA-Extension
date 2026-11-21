; AGA_NATIVE_MIN_CPU: MC68020
; M19 P2b Flip: slot lookup, owner/mode, Chip cache release and public setter.
; Source authority: tools/m19_p2b_bob_flip_emit.py::emit_bob_flip.
; BOBS offsets +$09E36..+$09F25, exactly 240 instruction bytes.
; The later variant/paint/geometry/cleanup routines remain audit-backed.
; Four PC-index full-extension forms are explicitly encoded to preserve
; emitter word $0170 (32-bit base displacement, suppressed index).
; At the DC.L site, the architectural PC base is current location minus 2.
; Offset-zero frame/slot fields use (An), not 0(An), to preserve 2-byte EA.

P2B_FLIP_SLOT_BYTES   equ 64
P2B_FLIP_MAX_OBJECTS  equ 64
P2B_FLIP_SLOT_MODE    equ 0
P2B_FLIP_SLOT_BLOCK   equ 32
P2B_FLIP_SLOT_SIZE    equ 36
P2B_FLIP_FRAME_SIZE   equ 40
P2B_FLIP_FRAME_MODE   equ 0
P2B_FLIP_FRAME_ID     equ 4
P2B_FLIP_FRAME_NEXT   equ 8
P2B_FLIP_CHECKED      equ 16
P2B_FLIP_FREE_MEM     equ -210

; D0=Bob ID (1..64), A0=slot.
p2b_slot:
    dc.w $41FB,$0170
    dc.l p2b_slots-(*-2)
    move.l d0,d2
    subq.l #1,d2
    lsl.l #6,d2
    adda.l d2,a0
    rts

; D0=Bob ID, D3=mode or zero for wrong owner/invalid ID.
p2b_mode:
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l a5,d2
    cmp.l (a0),d2
    bne.w p2b_mode_normal
    tst.l d0
    beq.w p2b_mode_normal
    cmpi.l #P2B_FLIP_MAX_OBJECTS,d0
    bhi.w p2b_mode_normal
    bsr.w p2b_slot
    move.l (a0),d3
    rts
p2b_mode_normal:
    moveq #0,d3
    rts

; A3=slot. The painter's synchronous Blitter completion precedes this.
p2b_free_slot:
    move.l P2B_FLIP_SLOT_BLOCK(a3),d0
    tst.l d0
    beq.w p2b_free_slot_done
    movea.l d0,a1
    move.l P2B_FLIP_SLOT_SIZE(a3),d0
    move.l #0,P2B_FLIP_SLOT_BLOCK(a3)
    movea.l $0004.w,a6
    jsr P2B_FLIP_FREE_MEM(a6)
p2b_free_slot_done:
    rts

; GetP parameter has advanced A3: preserve it across the full register save.
ENTRY_BOBS_09E96:
p2b_public_flip:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    lea -P2B_FLIP_FRAME_SIZE(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,P2B_FLIP_FRAME_ID(a2)
    move.l a3,P2B_FLIP_FRAME_NEXT(a2)
    cmpi.l #3,d3
    bhi.w p2b_flip_fail
    bsr.w p1c_context
    move.l a0,d0
    beq.w p2b_flip_fail
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l (a0),d0
    beq.w p2b_flip_read
    move.l a5,d1
    cmp.l d1,d0
    bne.w p2b_flip_fail

p2b_flip_read:
    movea.l a2,a1
    adda.l #P2B_FLIP_CHECKED,a1
    move.l P2B_FLIP_FRAME_ID(a2),d0
    bsr.w relay_checked_read_entry
    tst.l d3
    beq.w p2b_flip_fail
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l a5,(a0)
    move.l P2B_FLIP_FRAME_ID(a2),d0
    bsr.w p2b_slot
    move.l (a2),d3
    move.l d3,(a0)
    tst.l d3
    bne.w p2b_flip_ok
    movea.l a0,a3
    bsr.w p2b_free_slot
p2b_flip_ok:
    moveq #1,d3
    bra.w p2b_flip_return

L_BOBS_09F12:
p2b_flip_fail:
    moveq #0,d3
p2b_flip_return:
    move.l P2B_FLIP_FRAME_NEXT(a2),d2
    lea P2B_FLIP_FRAME_SIZE(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    movea.l d2,a3
    moveq #0,d2
    rts
