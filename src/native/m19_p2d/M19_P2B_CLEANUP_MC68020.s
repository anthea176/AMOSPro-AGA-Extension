; AGA_NATIVE_MIN_CPU: MC68020
; P2b end/close and bank-cache retirement - source-proven 188 instruction bytes.
; SOURCE: tools/m19_p2b_bob_flip_emit.py::emit_bob_flip.
; BOBS [$0A1D2,$0A28E). Four PC32 68020 LEAs preserve emitter encodings.
p2b_close_return:
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l (a0),d0
    beq.w p2b_close_restore
    move.l a5,d1
    cmp.l d1,d0
    bne.w p2b_close_restore
    move.l $01C8(a5),d0
    beq.w p2b_closed
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w p2b_close_restore
    movea.l $01C8(a5),a0
    tst.l (a0)
    bne.w p2b_close_restore
p2b_closed:
    move.l #0,d4
    bsr.w p2b_purge
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l #0,(a0)
p2b_close_restore:
    bra.w p2d_close       ; P2d source emitter hook; exact 6 bytes incl NOP
    nop

p2b_bank_free:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    move.l d3,d4
    bsr.w registry_free_entry
    tst.l d3
    beq.w p2b_bank_free_return
    dc.w $41FB,$0170
    dc.l p2b_owner-(*-2)
    move.l a5,d0
    cmp.l (a0),d0
    bne.w p2b_bank_free_return
    bsr.w p2b_purge
    moveq #1,d3
p2b_bank_free_return:
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    moveq #0,d2
    rts

; D4=0 frees all, otherwise frees only the matching bank's variants.
p2b_purge:
    dc.w $47FB,$0170
    dc.l p2b_slots-(*-2)
    move.l #64,d5
p2b_purge_loop:
    tst.l d4
    beq.w p2b_clear_mode
    cmp.l 8(a3),d4
    bne.w p2b_purge_next
    bra.w p2b_purge_slot
p2b_clear_mode:
    bsr.w p2c_reset_slot    ; P2c patch resets mode + plane mask
    nop
p2b_purge_slot:
    bsr.w p2b_free_slot
p2b_purge_next:
    adda.l #64,a3
    subq.l #1,d5
    bne.w p2b_purge_loop
    rts
