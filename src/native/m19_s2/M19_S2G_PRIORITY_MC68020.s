; AGA_NATIVE_MIN_CPU: MC68020
; S2g-P1a private five-integer entry: same transactional S2f body.
; D3 = layer, (A3)+ = image, y, x, id (four LONGs in reverse order).
; Existing four-argument entry initializes W_LAYER to zero.
; The shared body consumes parameters before any rejection and restores
; A3 to the consumed position, D2=0, D3=result. No extra persistent state.
; No public token in P1a: this entry is reached by a private AP20 test stub.
s2g_pub_sprite5:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,W_LAYER(a2)
    move.l (a3)+,d3
    bra.w s2g_pub_args

; D6 = free registry mask (bits 0..2); D0/D1 scratch.
; Caller validated layer as unsigned 0..3. Preserve auto order and
; all downstream width, OS reservation, palette and receipt checks.
s2g_pub_layer_mask:
    move.l W_LAYER(a2),d0
    beq.s s2g_pub_layer_done
    subq.l #1,d0
    moveq #1,d1
    lsl.l d0,d1
    and.l d1,d6
s2g_pub_layer_done:
    tst.l d6
    rts

; A4 = verified active record. Auto or exact pair only, no migration.
; Return D0=1 allowed, 0 refusal. No memory/OS effects.
s2g_pub_same_layer:
    move.l W_LAYER(a2),d0
    beq.s s2g_pub_layer_ok
    add.l d0,d0
    cmp.l 20(a4),d0
    bne.s s2g_pub_layer_no
s2g_pub_layer_ok:
    moveq #1,d0
    rts
s2g_pub_layer_no:
    moveq #0,d0
    rts
