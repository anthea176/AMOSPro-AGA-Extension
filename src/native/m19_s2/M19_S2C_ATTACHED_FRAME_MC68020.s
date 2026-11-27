; AGA_NATIVE_MIN_CPU: MC68020
; S2c-P0d, included by the source-built attached lifecycle component.
; A0 pinned receipt, A1 Gfx, A2 detached P0b allocation, D0 exact extent.
; Caller owns both disjoint, stable allocations and the registry borrow.
; Same bank generation, height, opaque count and all 48 RGB24 bytes.
; Return 1,0 or 0,reason; reason8=detached frame incompatible.
; No allocator, direct hardware/Copper write or source bank mutation.
; No native writes to live pixel data; OS changes control words only.
; Wait twice while old pair visible, corroborate refs before/after.
; Stage only inactive streams; then hide both, ChangeSprite twice,
; ATTACH odd, reveal pair, commit image ID. Not atomic raster timing.
; After any uncertain publication, state15 disallows Move/Change.
; Refusal before hide for incompatible scratch leaves state31 intact.
CF_SOURCE equ 0
CF_LEN    equ 4
CF_OLD    equ 8
CF_NEW    equ 12
CF_LOF    equ 16
CF_SHF    equ 20
CF_ID     equ 24
CF_BYTES  equ 28

AGSP_S2C_CHANGE:
    movem.l d2-d7/a0-a6,-(sp)
    lea -CF_BYTES(sp),sp
    move.l a2,CF_SOURCE(sp)
    move.l d0,CF_LEN(sp)
    movea.l a0,a3
    movea.l a1,a5
    bsr.w s2c_l_validate
    tst.l d0
    beq.w s2c_f_bad
    cmpi.l #31,12(a3)
    bne.w s2c_f_owner
    moveq #0,d2
    move.w 6(a4),d2
    moveq #0,d3
    move.w 8(a4),d3
    bsr.w s2c_l_geometry
    tst.l d0
    beq.w s2c_f_owner
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_f_context_bad
    bsr.w s2c_l_live
    tst.l d0
    beq.w s2c_f_uncertain
    move.l (a4),CF_OLD(sp)
    lea 96(a4),a0
    cmpa.l (a4),a0
    bne.s s2c_f_new_slot
    adda.l d5,a0
    adda.l d5,a0
s2c_f_new_slot:
    move.l a0,CF_NEW(sp)
    move.l 50(a5),CF_LOF(sp)
    move.l 54(a5),CF_SHF(sp)
    bsr.w s2c_f_source
    tst.l d0
    beq.w s2c_f_source_bad
    move.l d1,CF_ID(sp)
    bsr.w s2c_f_refs
    tst.l d0
    beq.w s2c_f_uncertain
    ; Same two frame fences as the S2a inactive-slot contract.
    ; Old pair remains visible through both boundaries.
    jsr -270(a6)
    bsr.w s2c_f_refs
    tst.l d0
    beq.w s2c_f_uncertain
    jsr -270(a6)
    bsr.w s2c_f_refs
    tst.l d0
    beq.w s2c_f_uncertain
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_f_context_bad
    bsr.w s2c_f_source
    tst.l d0
    beq.w s2c_f_source_bad
    cmp.l CF_ID(sp),d1
    bne.w s2c_f_source_bad
    bsr.w s2c_f_refs
    tst.l d0
    beq.w s2c_f_uncertain
    ; Copy exactly two streams, including zero POS/CTL and terminators.
    ; The inactive slot is not a visible descriptor or CopInit pointer.
    movea.l CF_SOURCE(sp),a0
    lea 96(a0),a0
    movea.l CF_NEW(sp),a1
    move.l d5,d0
    lsr.l #1,d0
    subq.w #1,d0
s2c_f_copy:
    move.l (a0)+,(a1)+
    dbra d0,s2c_f_copy
    bsr.w s2c_f_refs
    tst.l d0
    beq.w s2c_f_uncertain
    ; Hide using documented even MoveSprite recursion. Never set the
    ; ATTACH bit on a stream visible to the OS/Copper at this point.
    move.l #15,12(a3)
    movea.l 8(a3),a0
    movea.l a4,a1
    move.l d2,d0
    move.l #257,d1
    jsr -426(a6)
    bsr.w s2c_f_hidden_refs
    tst.l d0
    beq.w s2c_f_uncertain
    move.l CF_OLD(sp),d0
    cmp.l (a4),d0
    bne.w s2c_f_uncertain
    add.l d5,d0
    cmp.l 12(a4),d0
    bne.w s2c_f_uncertain
    ; With both pointers neutral, update descriptors separately.
    movea.l 8(a3),a0
    movea.l a4,a1
    movea.l CF_NEW(sp),a2
    jsr -420(a6)
    bsr.w s2c_f_hidden_refs
    tst.l d0
    beq.w s2c_f_uncertain
    move.l CF_NEW(sp),d0
    cmp.l (a4),d0
    bne.w s2c_f_uncertain
    move.l CF_OLD(sp),d0
    add.l d5,d0
    cmp.l 12(a4),d0
    bne.w s2c_f_uncertain
    movea.l 8(a3),a0
    lea 12(a4),a1
    movea.l CF_NEW(sp),a2
    adda.l d5,a2
    jsr -420(a6)
    bsr.w s2c_l_context_palette
    tst.l d0
    beq.w s2c_f_uncertain
    bsr.w s2c_f_hidden_refs
    tst.l d0
    beq.w s2c_f_uncertain
    bsr.w s2c_l_hidden
    tst.l d0
    beq.w s2c_f_uncertain
    move.l CF_NEW(sp),d0
    cmp.l (a4),d0
    bne.w s2c_f_uncertain
    movea.l 12(a4),a0
    bset #7,3(a0)
    movea.l 8(a3),a0
    movea.l a4,a1
    move.l d2,d0
    move.l d3,d1
    jsr -426(a6)
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_f_uncertain
    bsr.w s2c_l_live
    tst.l d0
    beq.w s2c_f_uncertain
    move.l CF_NEW(sp),d0
    cmp.l (a4),d0
    bne.w s2c_f_uncertain
    cmp.w 6(a4),d2
    bne.w s2c_f_uncertain
    cmp.w 8(a4),d3
    bne.w s2c_f_uncertain
    move.l CF_LOF(sp),d4
    move.l CF_SHF(sp),d7
    bsr.w s2c_f_lists
    tst.l d0
    beq.w s2c_f_uncertain
    move.l CF_ID(sp),d0
    move.w d0,28(a4)
    move.l #31,12(a3)
    moveq #1,d0
    moveq #0,d1
    bra.s s2c_f_return
s2c_f_bad:
    moveq #1,d1
    bra.s s2c_f_fail
s2c_f_context_bad:
    moveq #2,d1
    bra.s s2c_f_fail
s2c_f_owner:
    moveq #3,d1
    bra.s s2c_f_fail
s2c_f_source_bad:
    moveq #8,d1
    bra.s s2c_f_fail
s2c_f_uncertain:
    move.l #15,12(a3)
    moveq #6,d1
s2c_f_fail:
    moveq #0,d0
s2c_f_return:
    lea CF_BYTES(sp),sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Called directly from CHANGE; +4 accounts for BSR return address.
; Verify the old pair, coordinates and both dynamic list snapshots.
s2c_f_refs:
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_l_no
    bsr.w s2c_l_live
    tst.l d0
    beq.w s2c_l_no
    move.l CF_OLD+4(sp),d0
    cmp.l (a4),d0
    bne.w s2c_l_no
    cmp.w 6(a4),d2
    bne.w s2c_l_no
    cmp.w 8(a4),d3
    bne.w s2c_l_no
    move.l CF_LOF+4(sp),d4
    move.l CF_SHF+4(sp),d7
    bra.w s2c_f_lists

; Mixed slots allowed ONLY between the two hidden ChangeSprite calls.
; Both OS table entries must be ours, neither CopInit pointer live.
s2c_f_hidden_refs:
    bsr.w s2c_l_context
    tst.l d0
    beq.w s2c_l_no
    bsr.w s2c_l_ownership
    tst.l d0
    beq.w s2c_l_no
    bsr.w s2c_l_slots
    tst.l d0
    beq.w s2c_l_no
    cmpa.l (a1),a4
    bne.w s2c_l_no
    lea 12(a4),a2
    cmpa.l 4(a1),a2
    bne.w s2c_l_no
    bsr.w s2c_l_blank
    tst.l d0
    beq.w s2c_l_no
    cmp.w 6(a4),d2
    bne.w s2c_l_no
    cmp.w 18(a4),d2
    bne.w s2c_l_no
    cmpi.w #257,8(a4)
    bne.w s2c_l_no
    cmpi.w #257,20(a4)
    bne.w s2c_l_no
    move.l CF_LOF+4(sp),d4
    move.l CF_SHF+4(sp),d7
    bra.w s2c_f_lists

; Mapped/stable list starts, not a general traversal or DMA proof.
s2c_f_lists:
    cmp.l 50(a5),d4
    bne.w s2c_l_no
    cmp.l 54(a5),d7
    bne.w s2c_l_no
    movea.l d4,a0
    moveq #1,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    movea.l d7,a0
    moveq #1,d0
    bsr.w s2c_l_span
    tst.l d0
    beq.w s2c_l_no
    cmp.l 50(a5),d4
    bne.w s2c_l_no
    cmp.l 54(a5),d7
    bne.w s2c_l_no
    moveq #1,d0
    rts

; Exact detached block from P0b, stable and disjoint by caller contract.
; Return D0 boolean, D1 new image ID. No stage writes here.
s2c_f_source:
    move.l CF_SOURCE+4(sp),d4
    move.l CF_LEN+4(sp),d7
    cmp.l 4(a3),d7
    bne.w s2c_l_no
    move.l d4,d0
    add.l d7,d0
    bcs.w s2c_l_no
    move.l a4,d1
    add.l 4(a3),d1
    bcs.w s2c_l_no
    cmp.l a4,d0
    bls.s s2c_f_disjoint
    cmp.l d1,d4
    bcs.w s2c_l_no
s2c_f_disjoint:
    movea.l d4,a0
    move.l d7,d0
    subq.l #1,d0
    bsr.w s2c_l_span
    btst #1,d0
    beq.w s2c_l_no
    movea.l d4,a2
    cmp.l 24(a2),d7
    bne.w s2c_l_no
    cmpi.l #96,92(a2)
    bne.w s2c_l_no
    cmp.l 88(a2),d5
    bne.w s2c_l_no
    move.w 4(a4),d0
    cmp.w 4(a2),d0
    bne.w s2c_l_no
    cmp.w 16(a2),d0
    bne.w s2c_l_no
    tst.l (a2)
    bne.w s2c_l_no
    tst.l 12(a2)
    bne.w s2c_l_no
    tst.l 6(a2)
    bne.w s2c_l_no
    tst.l 18(a2)
    bne.w s2c_l_no
    cmpi.w #-1,10(a2)
    bne.w s2c_l_no
    cmpi.w #-1,22(a2)
    bne.w s2c_l_no
    tst.l 36(a2)
    bne.w s2c_l_no
    move.l 32(a4),d0
    cmp.l 32(a2),d0
    bne.w s2c_l_no
    move.w 30(a4),d0
    cmp.w 30(a2),d0
    bne.w s2c_l_no
    lea 40(a4),a0
    lea 40(a2),a1
    moveq #11,d0
s2c_f_palette_loop:
    move.l (a0)+,d1
    cmp.l (a1)+,d1
    bne.w s2c_l_no
    dbra d0,s2c_f_palette_loop
    lea 96(a2),a0
    tst.l (a0)
    bne.w s2c_l_no
    tst.l -4(a0,d5.l)
    bne.w s2c_l_no
    adda.l d5,a0
    tst.l (a0)
    bne.w s2c_l_no
    tst.l -4(a0,d5.l)
    bne.w s2c_l_no
    moveq #0,d1
    move.w 28(a2),d1
    beq.w s2c_l_no
    cmpi.w #4096,d1
    bhi.w s2c_l_no
    moveq #1,d0
    rts
