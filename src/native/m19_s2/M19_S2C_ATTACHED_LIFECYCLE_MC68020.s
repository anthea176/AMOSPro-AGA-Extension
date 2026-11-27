; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P0c standalone attached SimpleSprite pair, V39/V40 OS API.
; Source authority: P0b prepared layout, S2b palette/retire, V40
; simplesprites.asm (GetSprite, ChangeSprite, MoveSprite, FreeSprite).
; Caller owns/pins the exact 44-byte receipt, P0b Chip allocation,
; graphics.library, ViewPort and ColorMap, and holds the exclusive
; AMOS registry borrow for their lifetime. Never infer ownership from bits.
; Receipt LONGs: block, extent, VP, state, Gfx, CM, View, CopInit,
; SimpleSprites table, zero, even channel (2/4/6). All snapshots immutable.
; States: 0 private, 5 even, 7 both, 15 attempted publication,
; 31 shown, 13 partially released after publication, 4 pending fence,
; 20 retired; bit31 quarantine (no automatic release on ambiguous Get).
; A0 receipt, A1 Gfx, D0 X and D1 Y for Show/Move.
; D0=1 OK (Retire: 2 private, 1 retired), 0 refused; D1 reason 1..7.
; D2-D7/A0-A6 preserved. No FreeVec, new public token, direct register
; or user Copper write. Change: A2 detached P0b block, D0 exact extent.
; Change alternates E0/O0 and E1/O1, same height/generation/palette.
; All five old entry offsets preserved; Change entry at +20.
; Show failure after publication leaves a sticky state 15: retire or
; quarantine, NEVER free merely because Show returned 0.
; MoveSprite calls on even propagate to odd in source-proven V40.
; Both initial ChangeSprite calls are at Y=257 (VP height=256).
; ATTACH bit is set only in the owned odd stream while hidden.
; No proof of atomic raster update or real DMA retirement.
    bra.w AGSP_S2C_ACQUIRE
    bra.w AGSP_S2C_SHOW
    bra.w AGSP_S2C_MOVE
    bra.w AGSP_S2C_RETIRE
    bra.w AGSP_S2C_PALETTE
    bra.w AGSP_S2C_CHANGE

AGSP_S2C_ACQUIRE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_l_bad
    tst.l 12(a3)
    bne.w s2c_l_owner
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_context_bad
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_owner
    tst.l (a1)
    bne.w s2c_l_owner
    tst.l 4(a1)
    bne.w s2c_l_owner
    bsr.w s2c_l_blank
    tst.l d0
    beq.w s2c_l_owner
    moveq #3,d0
    lsl.l d6,d0
    and.b 166(a5),d0
    bne.w s2c_l_owner
    tst.l (a4)
    bne.w s2c_l_owner
    tst.l 12(a4)
    bne.w s2c_l_owner
    cmpi.w #-1,10(a4)
    bne.w s2c_l_owner
    cmpi.w #-1,22(a4)
    bne.w s2c_l_owner
    movea.l a4,a0
    move.l d6,d0
    jsr -408(a6)
    cmp.w d6,d0
    beq.s s2c_l_got_even
    cmpi.w #-1,d0
    bne.w s2c_l_quarantine
    cmpi.w #-1,10(a4)
    bne.w s2c_l_quarantine
    bra.w s2c_l_get_fail
s2c_l_got_even:
    move.l #5,12(a3)
    cmp.w 10(a4),d6
    bne.w s2c_l_quarantine
    lea 12(a4),a0
    move.l d6,d0
    addq.l #1,d0
    jsr -408(a6)
    move.l d6,d1
    addq.l #1,d1
    cmp.w d1,d0
    beq.s s2c_l_got_odd
    cmpi.w #-1,d0
    bne.w s2c_l_quarantine
    cmpi.w #-1,22(a4)
    bne.w s2c_l_quarantine
    ; Only the exact even receipt remains. Caller calls Retire (state5).
    bra.w s2c_l_get_fail
s2c_l_got_odd:
    move.l #7,12(a3)
    cmp.w 22(a4),d1
    bne.w s2c_l_quarantine
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_context_bad
    bsr.w s2c_l_ownership
    tst.l d0
    beq.w s2c_l_owner
    bra.w s2c_l_ok
s2c_l_quarantine:
    ori.l #$80000004,12(a3)
    moveq #5,d1
    bra.w s2c_l_refuse

AGSP_S2C_SHOW:
    movem.l d2-d7/a0-a6,-(sp)
    move.l d0,d2
    move.l d1,d3
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_l_bad
    cmpi.l #7,12(a3)
    bne.w s2c_l_owner
    bsr.w s2c_l_geometry
    tst.l d0
    beq.w s2c_l_geom_bad
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_context_bad
    bsr.w s2c_l_ownership
    tst.l d0
    beq.w s2c_l_owner
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_owner
    tst.l (a1)
    bne.w s2c_l_owner
    tst.l 4(a1)
    bne.w s2c_l_owner
    bsr.w s2c_l_blank
    tst.l d0
    beq.w s2c_l_owner
    tst.l (a4)
    bne.w s2c_l_owner
    tst.l 12(a4)
    bne.w s2c_l_owner
    tst.l 6(a4)
    bne.w s2c_l_owner
    tst.l 18(a4)
    bne.w s2c_l_owner
    lea 96(a4),a2
    tst.l (a2)
    bne.w s2c_l_owner
    tst.l -4(a2,d5.l)
    bne.w s2c_l_owner
    tst.l 0(a2,d5.l)
    bne.w s2c_l_owner
    move.l d5,d0
    add.l d0,d0
    tst.l -4(a2,d0.l)
    bne.w s2c_l_owner
    ; No visible half-pair while ChangeSprite invokes MoveSprite.
    move.l #15,12(a3)
    move.w #257,8(a4)
    move.w #257,20(a4)
    movea.l 8(a3),a0
    movea.l a4,a1
    jsr -420(a6)
    lea 96(a4),a0
    cmpa.l (a4),a0
    bne.w s2c_l_publish_bad
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_l_publish_bad
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_publish_bad
    cmpa.l (a1),a4
    bne.w s2c_l_publish_bad
    tst.l 4(a1)
    bne.w s2c_l_publish_bad
    bsr.w s2c_l_blank
    tst.l d0
    beq.w s2c_l_publish_bad
    bsr.w s2c_l_ownership
    tst.l d0
    beq.w s2c_l_publish_bad
    movea.l 8(a3),a0
    lea 12(a4),a1
    lea 96(a4,d5.l),a2
    jsr -420(a6)
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_publish_bad
    bsr.w s2c_l_hidden
    tst.l d0
    beq.w s2c_l_publish_bad
    ; A source-proven hidden owned stream; do not write a custom register.
    movea.l 12(a4),a0
    bset #7,3(a0)
    bra.w s2c_l_move_now

AGSP_S2C_MOVE:
    movem.l d2-d7/a0-a6,-(sp)
    move.l d0,d2
    move.l d1,d3
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_l_bad
    cmpi.l #31,12(a3)
    bne.w s2c_l_owner
    bsr.w s2c_l_geometry
    tst.l d0
    beq.w s2c_l_geom_bad
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_context_bad
    bsr.w s2c_l_live
    tst.l d0
    beq.w s2c_l_publish_bad
    move.l #15,12(a3)       ; uncertain until both refs corroborated
s2c_l_move_now:
    movea.l 8(a3),a0
    movea.l a4,a1
    move.l d2,d0
    move.l d3,d1
    jsr -426(a6)
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_l_publish_bad
    bsr.w s2c_l_live
    tst.l d0
    beq.w s2c_l_publish_bad
    cmp.w 6(a4),d2
    bne.w s2c_l_publish_bad
    cmp.w 8(a4),d3
    bne.w s2c_l_publish_bad
    move.l #31,12(a3)
    bra.w s2c_l_ok

AGSP_S2C_PALETTE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_l_bad
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_l_context_bad
    bra.w s2c_l_ok

AGSP_S2C_RETIRE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_l_bad
    move.l 12(a3),d2
    beq.w s2c_l_private
    cmpi.l #20,d2
    beq.w s2c_l_ok
    cmpi.l #4,d2
    beq.w s2c_l_fence
    cmpi.l #5,d2
    beq.s s2c_l_retire_owned
    cmpi.l #7,d2
    beq.s s2c_l_retire_owned
    cmpi.l #13,d2
    beq.s s2c_l_retire_owned
    cmpi.l #15,d2
    beq.s s2c_l_retire_owned
    cmpi.l #31,d2
    bne.w s2c_l_owner
s2c_l_retire_owned:
    ; Only our explicit receipt bits authorize FreeSprite. A foreign
    ; odd owner after a failed second GetSprite is not examined/freed.
    move.l d2,d7
    andi.l #15,d2
    move.l d2,d0
    andi.l #3,d0
    lsl.l d6,d0
    moveq #0,d1
    move.b 166(a5),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w s2c_l_owner
    cmp.w 10(a4),d6
    bne.w s2c_l_owner
    btst #1,d2
    beq.s s2c_l_retire_slots
    move.l d6,d0
    addq.l #1,d0
    cmp.w 22(a4),d0
    bne.w s2c_l_owner
s2c_l_retire_slots:
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_owner
    move.l (a1),d0
    beq.s s2c_l_retire_odd_check
    btst #3,d2
    beq.w s2c_l_owner
    cmp.l a4,d0
    bne.w s2c_l_owner
s2c_l_retire_odd_check:
    btst #1,d2
    beq.s s2c_l_release_even
    move.l 4(a1),d0
    beq.s s2c_l_release_odd
    btst #3,d2
    beq.w s2c_l_owner
    lea 12(a4),a0
    cmp.l a0,d0
    bne.w s2c_l_owner
s2c_l_release_odd:
    move.l d2,12(a3)       ; remove confirmation before OS release
    move.l d6,d0
    addq.l #1,d0
    jsr -414(a6)
    andi.l #$fffffffd,d2
    move.l d2,12(a3)
s2c_l_release_even:
    move.l d6,d0
    jsr -414(a6)
    moveq #4,d2
    move.l d2,12(a3)
    btst #3,d7
    beq.s s2c_l_retired
s2c_l_fence:
    bsr.w s2c_l_neutral
    tst.l d0
    beq.w s2c_l_owner
    jsr -270(a6)
    jsr -270(a6)
    bsr.w s2c_l_neutral
    tst.l d0
    beq.w s2c_l_owner
s2c_l_retired:
    move.l #20,12(a3)
    bra.w s2c_l_ok

; Shared entry result paths.
s2c_l_private:
    moveq #2,d0
    moveq #0,d1
    bra.s s2c_l_return
s2c_l_ok:
    moveq #1,d0
    moveq #0,d1
    bra.s s2c_l_return
s2c_l_bad:
    moveq #1,d1
    bra.s s2c_l_refuse
s2c_l_context_bad:
    moveq #2,d1
    bra.s s2c_l_refuse
s2c_l_owner:
    moveq #3,d1
    bra.s s2c_l_refuse
s2c_l_get_fail:
    moveq #4,d1
    bra.s s2c_l_refuse
s2c_l_publish_bad:
    move.l #15,12(a3)
    moveq #6,d1
    bra.s s2c_l_refuse
s2c_l_geom_bad:
    moveq #7,d1
s2c_l_refuse:
    moveq #0,d0
s2c_l_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Validate pinned receipt/block, without looking at any arbitrary stream ptr.
; Output A4=block, A6=Gfx, D5=stream size, D6=even. D2/D3/D7 preserved.
s2c_l_validate:
    movea.l a3,a0
    moveq #43,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    tst.l 36(a3)
    bne.w s2c_l_no
    cmpa.l 16(a3),a5
    bne.w s2c_l_no
    movea.l a5,a0
    move.l #211,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    cmpi.w #212,18(a5)
    bcs.w s2c_l_no
    cmpi.w #39,20(a5)
    bcs.w s2c_l_no
    cmpi.w #40,20(a5)
    bhi.w s2c_l_no
    move.l 40(a3),d6
    cmpi.l #2,d6
    beq.s s2c_l_channel_ok
    cmpi.l #4,d6
    beq.s s2c_l_channel_ok
    cmpi.l #6,d6
    bne.w s2c_l_no
s2c_l_channel_ok:
    move.l 4(a3),d0
    cmpi.l #144,d0
    bcs.w s2c_l_no
    cmpi.l #4224,d0
    bhi.w s2c_l_no
    subq.l #1,d0
    movea.l (a3),a0
    bsr.w s2c_l_span
    btst #1,d0
    beq.w s2c_l_no
    movea.l (a3),a4
    moveq #0,d5
    move.w 4(a4),d5
    beq.w s2c_l_no
    cmpi.w #256,d5
    bhi.w s2c_l_no
    cmp.w 16(a4),d5
    bne.w s2c_l_no
    lsl.l #2,d5
    addq.l #8,d5
    cmp.l 88(a4),d5
    bne.w s2c_l_no
    move.l d5,d0
    lsl.l #2,d0
    addi.l #96,d0
    cmp.l 24(a4),d0
    bne.w s2c_l_no
    cmp.l 4(a3),d0
    bne.w s2c_l_no
    cmpi.l #96,92(a4)
    bne.w s2c_l_no
    cmpi.w #1,28(a4)
    bcs.w s2c_l_no
    cmpi.w #4096,28(a4)
    bhi.w s2c_l_no
    cmpi.w #4,30(a4)
    bcs.w s2c_l_no
    cmpi.w #15,30(a4)
    bhi.w s2c_l_no
    tst.l 32(a4)
    beq.w s2c_l_no
    movea.l a5,a6
    moveq #1,d0
    rts
s2c_l_geometry:
    tst.l 36(a4)            ; only zero hotspots in this tranche
    bne.w s2c_l_no
    cmpi.l #304,d2          ; width 16 fully within 320
    bhi.w s2c_l_no
    cmpi.l #255,d3
    bhi.w s2c_l_no
    moveq #0,d0
    move.w 4(a4),d0
    add.l d3,d0
    cmpi.l #256,d0
    bhi.w s2c_l_no
    moveq #1,d0
    rts

; No dereference of unverified ViewPort/ColorMap or foreign sprite data.
s2c_l_context:
    move.l 24(a3),d0
    cmp.l 34(a5),d0
    bne.w s2c_l_no
    movea.l d0,a0
    moveq #18,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    move.l 8(a3),d0
    cmp.l (a0),d0
    bne.w s2c_l_no
    movea.l d0,a0
    moveq #40,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    tst.l (a0)              ; single active ViewPort
    bne.w s2c_l_no
    cmpi.w #$5000,32(a0)
    bne.w s2c_l_no
    cmpi.w #320,24(a0)
    bne.w s2c_l_no
    cmpi.w #256,26(a0)
    bne.w s2c_l_no
    tst.l 12(a0)
    bne.w s2c_l_no
    tst.l 20(a0)
    bne.w s2c_l_no
    move.l 20(a3),d0
    cmp.l 4(a0),d0
    bne.w s2c_l_no
    movea.l d0,a0
    moveq #51,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    cmpi.b #2,1(a0)
    bne.w s2c_l_no
    cmpi.w #256,2(a0)
    bne.w s2c_l_no
    cmpi.b #1,18(a0)
    bne.w s2c_l_no
    bsr.w s2c_l_slots
    rts

s2c_l_context_palette:
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_l_no
    ; Same V39/40 read-only VideoControl GET contract as S2b.
    ; 180-byte buffer holds up to 15 GetRGB32 triplets.
    movem.l d4/d7/a2,-(sp)
    lea -180(sp),sp
    movea.l sp,a2
    move.l #$80000028,(a2)
    move.l #$6a5a5a5a,4(a2)
    move.l #$80000029,8(a2)
    move.l #$6a5a5a5a,12(a2)
    move.l #$80000032,16(a2)
    move.l #$6a5a5a5a,20(a2)
    move.l #$80000034,24(a2)
    move.l #$6a5a5a5a,28(a2)
    clr.l 32(a2)
    clr.l 36(a2)
    movea.l 20(a3),a0
    movea.l a2,a1
    jsr -708(a6)
    tst.l d0
    bne.s s2c_l_pal_no
    cmpi.l #16,4(a2)
    bne.s s2c_l_pal_no
    cmpi.l #16,12(a2)
    bne.s s2c_l_pal_no
    cmpi.l #255,20(a2)
    bne.s s2c_l_pal_no
    cmpi.l #4,28(a2)
    bne.s s2c_l_pal_no
    moveq #0,d7
    move.w 30(a4),d7
    move.l d7,d1
    moveq #17,d0
    movea.l 20(a3),a0
    movea.l a2,a1
    jsr -900(a6)
    mulu.w #3,d7
    subq.w #1,d7
    lea 43(a4),a1
s2c_l_pal_rgb:
    move.b (a2),d0
    cmp.b (a1)+,d0
    bne.s s2c_l_pal_no
    adda.w #4,a2
    dbra d7,s2c_l_pal_rgb
    moveq #1,d4
    bra.s s2c_l_pal_return
s2c_l_pal_no:
    moveq #0,d4
s2c_l_pal_return:
    lea 180(sp),sp
    move.l d4,d0
    movem.l (sp)+,d4/d7/a2
    rts

; A0=pair's CopInit pointer instruction base, A1=table pair.
; Validate register words and stable mapped snapshots; no writes.
s2c_l_slots:
    move.l 28(a3),d0
    cmp.l 38(a5),d0
    bne.w s2c_l_no
    movea.l d0,a0
    move.l #191,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    move.l d6,d0
    lsl.l #3,d0
    lea 88(a0,d0.l),a0
    move.l d6,d1
    lsl.l #2,d1
    addi.w #$120,d1
    cmp.w (a0),d1
    bne.w s2c_l_no
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.w s2c_l_no
    addq.w #2,d1
    cmp.w 8(a0),d1
    bne.w s2c_l_no
    addq.w #2,d1
    cmp.w 12(a0),d1
    bne.w s2c_l_no
    move.l a0,-(sp)
    move.l 32(a3),d0
    cmp.l 208(a5),d0
    bne.s s2c_l_slots_bad
    movea.l d0,a0
    moveq #31,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.s s2c_l_slots_bad
    move.l d6,d0
    lsl.l #2,d0
    lea 0(a0,d0.l),a1
    movea.l (sp)+,a0
    moveq #1,d0
    rts
s2c_l_slots_bad:
    addq.l #4,sp
    bra.w s2c_l_no
s2c_l_blank:
    move.l 28(a3),d0
    addi.l #176,d0
    cmp.w 6(a0),d0
    bne.w s2c_l_no
    cmp.w 14(a0),d0
    bne.w s2c_l_no
    swap d0
    cmp.w 2(a0),d0
    bne.w s2c_l_no
    cmp.w 10(a0),d0
    bne.w s2c_l_no
    moveq #1,d0
    rts
s2c_l_neutral:
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_no
    tst.l (a1)
    bne.w s2c_l_no
    tst.l 4(a1)
    bne.w s2c_l_no
    moveq #3,d0
    lsl.l d6,d0
    and.b 166(a5),d0
    bne.w s2c_l_no
    bra.w s2c_l_blank
s2c_l_ownership:
    cmp.w 10(a4),d6
    bne.w s2c_l_no
    move.l d6,d0
    addq.l #1,d0
    cmp.w 22(a4),d0
    bne.w s2c_l_no
    moveq #3,d0
    lsl.l d6,d0
    moveq #0,d1
    move.b 166(a5),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w s2c_l_no
    moveq #1,d0
    rts

; Both exact stream/descriptor references, no read through foreign pointers.
s2c_l_streams:
    bsr.w s2c_l_ownership
    tst.l d0
    beq.w s2c_l_no
    lea 96(a4),a2
    cmpa.l (a4),a2
    beq.s s2c_l_stream_pair
    adda.l d5,a2
    adda.l d5,a2
    cmpa.l (a4),a2
    bne.w s2c_l_no
s2c_l_stream_pair:
    adda.l d5,a2
    cmpa.l 12(a4),a2
    bne.w s2c_l_no
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_no
    cmpa.l (a1),a4
    bne.w s2c_l_no
    lea 12(a4),a2
    cmpa.l 4(a1),a2
    bne.w s2c_l_no
    move.l 6(a4),d0
    cmp.l 18(a4),d0
    bne.w s2c_l_no
    moveq #1,d0
    rts
s2c_l_hidden:
    bsr.w s2c_l_streams
    tst.l d0
    beq.w s2c_l_no
    cmpi.w #257,8(a4)
    bne.w s2c_l_no
    movea.l (a4),a2
    btst #7,3(a2)
    bne.w s2c_l_no
    movea.l 12(a4),a2
    btst #7,3(a2)
    bne.w s2c_l_no
    bra.w s2c_l_blank
s2c_l_live:
    bsr.w s2c_l_streams
    tst.l d0
    beq.w s2c_l_no
    move.l (a4),d0
    cmp.w 6(a0),d0
    bne.w s2c_l_no
    swap d0
    cmp.w 2(a0),d0
    bne.w s2c_l_no
    move.l 12(a4),d0
    cmp.w 14(a0),d0
    bne.w s2c_l_no
    swap d0
    cmp.w 10(a0),d0
    bne.w s2c_l_no
    movea.l (a4),a0
    movea.l 12(a4),a1
    btst #7,3(a0)
    bne.s s2c_l_no
    btst #7,3(a1)
    beq.s s2c_l_no
    move.l (a0),d0
    eori.l #$80,d0
    cmp.l (a1),d0
    bne.s s2c_l_no
    moveq #1,d0
    rts
s2c_l_no:
    moveq #0,d0
    rts

; A0 pinned pointer, D0 inclusive final byte offset. Return common
; TypeOfMem flags (CHIP callers test bit1). Endpoint corroboration only.
s2c_l_span:
    movem.l d2/a0-a1/a6,-(sp)
    move.l a0,d1
    beq.s s2c_l_span_no
    btst #0,d1
    bne.s s2c_l_span_no
    add.l d0,d1
    bcs.s s2c_l_span_no
    movea.l d1,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    move.l d0,d2
    beq.s s2c_l_span_no
    movea.l 4(sp),a1
    jsr -534(a6)
    and.l d2,d0
    bra.s s2c_l_span_end
s2c_l_span_no:
    moveq #0,d0
s2c_l_span_end:
    movem.l (sp)+,d2/a0-a1/a6
    rts

    include "M19_S2C_ATTACHED_FRAME_MC68020.s"
