; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P2c1: guarded first publication of OS-owned ExtSprites.
; A0 pinned private 72-byte receipt, A6 pinned V39/40 graphics.library.
; D0/D1 desired x/y. +0..35 P2b-R1 receipt, state must be 7.
; +36 VP, +40 ActiView, +44 CopInit, +48 SimpleSprites table,
; +52 detached image even, +56 detached image odd (0 for simple),
; +60 expected image height.L, +64 ColorMap snapshot, +68 reserved zero.
; All descriptor allocations and chip data are owned/pinned by caller.
; Width provenance from P2a/P2b, same width for ALL descriptors.
; Caller maintains palette qualification and registry borrow, and validates
; ownership of these exact allocations. This is not an arbitrary pointer API.
; D0=1 D1=0 state31 success; D0=0 D1=1 preflight refusal unchanged;
; D0=0 D1=2 uncertain state15. No automatic retry, release, or FreeSpriteData.
; OS-owned descriptors are read-only here. All publication via OS calls.
; V40 source snapshot simplesprites.asm 39.41: Get does not populate table,
; Alloc leaves ss_x/ss_y uninitialized, Change copies old x/y and calls Move.
; Move(0,257) first primes hidden blanks. Odd first, then even. Replace
; odd (attached) and even while hidden, verify exact slots, then Move even.
; No claim of atomic display update or DMA retirement on real hardware.
AGSP_S2D_EXT_FIRST_SHOW:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a6,a5
    move.l d0,d2
    move.l d1,d3
    movea.l a3,a0
    moveq #71,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_bad
    cmpa.l (a3),a5
    bne.w s2d_c_bad
    cmpi.l #7,24(a3)
    bne.w s2d_c_bad
    tst.l 32(a3)
    bne.w s2d_c_bad
    tst.l 68(a3)
    bne.w s2d_c_bad
    move.l 12(a3),d4
    cmpi.l #16,d4
    beq.s s2d_c_width_ok
    cmpi.l #32,d4
    beq.s s2d_c_width_ok
    cmpi.l #64,d4
    bne.w s2d_c_bad
s2d_c_width_ok:
    move.l #320,d0
    sub.l d4,d0
    cmp.l d0,d2
    bhi.w s2d_c_bad
    lsr.l #4,d4
    move.l 16(a3),d5
    cmpi.l #2,d5
    beq.s s2d_c_kind_ok
    cmpi.l #4,d5
    bne.w s2d_c_bad
s2d_c_kind_ok:
    move.l 20(a3),d6
    cmpi.l #2,d6
    beq.s s2d_c_channel_ok
    cmpi.l #4,d6
    beq.s s2d_c_channel_ok
    cmpi.l #6,d6
    bne.w s2d_c_bad
s2d_c_channel_ok:
    move.l 60(a3),d7
    beq.w s2d_c_bad
    cmpi.l #256,d7
    bhi.w s2d_c_bad
    move.l #256,d0
    sub.l d7,d0
    cmp.l d0,d3
    bhi.w s2d_c_bad
    movea.l a5,a0
    move.l #449,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_bad
    cmpi.w #450,18(a5)
    bcs.w s2d_c_bad
    cmpi.w #1026,16(a5)
    bcs.w s2d_c_bad
    cmpi.w #39,20(a5)
    bcs.w s2d_c_bad
    cmpi.w #40,20(a5)
    bhi.w s2d_c_bad
    cmpi.l #4,d5
    bne.s s2d_c_simple
    move.l 56(a3),d0
    beq.w s2d_c_bad
    cmp.l 4(a3),d0
    beq.w s2d_c_bad
    cmp.l 8(a3),d0
    beq.w s2d_c_bad
    cmp.l 52(a3),d0
    beq.w s2d_c_bad
    bra.s s2d_c_distinct
s2d_c_simple:
    tst.l 56(a3)
    bne.w s2d_c_bad
s2d_c_distinct:
    move.l 52(a3),d0
    cmp.l 4(a3),d0
    beq.w s2d_c_bad
    cmp.l 8(a3),d0
    beq.w s2d_c_bad
    move.l 4(a3),d0
    cmp.l 8(a3),d0
    beq.w s2d_c_bad
    movea.l 4(a3),a0
    moveq #1,d0
    moveq #0,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_bad
    movea.l 4(a3),a0
    cmp.w 10(a0),d6
    bne.w s2d_c_bad
    movea.l 8(a3),a0
    moveq #1,d0
    moveq #0,d1
    cmpi.l #4,d5
    bne.s s2d_c_check_odd
    moveq #1,d1
s2d_c_check_odd:
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_bad
    movea.l 8(a3),a0
    move.l d6,d0
    addq.l #1,d0
    cmp.w 10(a0),d0
    bne.w s2d_c_bad
    movea.l 52(a3),a0
    move.l d7,d0
    moveq #0,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_bad
    cmpi.l #4,d5
    bne.s s2d_c_start
    movea.l 56(a3),a0
    move.l d7,d0
    moveq #1,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_c_bad
s2d_c_start:
    suba.l a4,a4
    suba.l a2,a2
    bsr.w s2d_c_hidden_refs
    tst.l d0
    beq.w s2d_c_bad
    move.l #15,24(a3)
    ; Get alone does not initialize old coordinates or populate the table.
    movea.l 8(a3),a1
    bsr.w s2d_c_hide
    movea.l 8(a3),a2
    bsr.w s2d_c_hidden_refs
    tst.l d0
    beq.w s2d_c_uncertain
    movea.l 4(a3),a1
    bsr.w s2d_c_hide
    movea.l 4(a3),a4
    bsr.w s2d_c_hidden_refs
    tst.l d0
    beq.w s2d_c_uncertain
    cmpi.l #4,d5
    bne.s s2d_c_switch_even
    movea.l 8(a3),a1
    movea.l 56(a3),a2
    bsr.w s2d_c_change
    tst.l d0
    beq.w s2d_c_uncertain
    movea.l 56(a3),a2
    bsr.w s2d_c_hidden_refs
    tst.l d0
    beq.w s2d_c_uncertain
s2d_c_switch_even:
    movea.l 4(a3),a1
    movea.l 52(a3),a2
    bsr.w s2d_c_change
    tst.l d0
    beq.w s2d_c_uncertain
    movea.l 52(a3),a4
    movea.l 8(a3),a2
    cmpi.l #4,d5
    bne.s s2d_c_before_reveal
    movea.l 56(a3),a2
s2d_c_before_reveal:
    bsr.w s2d_c_hidden_refs
    tst.l d0
    beq.w s2d_c_uncertain
    movea.l 36(a3),a0
    movea.l a4,a1
    move.l d2,d0
    move.l d3,d1
    jsr -426(a6)
    bsr.w s2d_c_context
    tst.l d0
    beq.w s2d_c_uncertain
    cmpa.l (a1),a4
    bne.w s2d_c_uncertain
    cmpa.l 4(a1),a2
    bne.w s2d_c_uncertain
    cmp.w 10(a4),d6
    bne.w s2d_c_uncertain
    move.l d6,d0
    addq.l #1,d0
    cmp.w 10(a2),d0
    bne.w s2d_c_uncertain
    cmp.w 6(a4),d2
    bne.w s2d_c_uncertain
    cmp.w 8(a4),d3
    bne.w s2d_c_uncertain
    move.l (a4),d0
    cmp.w 6(a0),d0
    bne.w s2d_c_uncertain
    swap d0
    cmp.w 2(a0),d0
    bne.w s2d_c_uncertain
    cmpi.l #4,d5
    bne.s s2d_c_visible_simple
    cmp.w 6(a2),d2
    bne.w s2d_c_uncertain
    cmp.w 8(a2),d3
    bne.w s2d_c_uncertain
    move.l (a2),d0
    bra.s s2d_c_visible_odd
s2d_c_visible_simple:
    cmpi.w #0,6(a2)
    bne.w s2d_c_uncertain
    cmpi.w #257,8(a2)
    bne.w s2d_c_uncertain
    move.l 44(a3),d0
    addi.l #176,d0
s2d_c_visible_odd:
    cmp.w 14(a0),d0
    bne.w s2d_c_uncertain
    swap d0
    cmp.w 10(a0),d0
    bne.w s2d_c_uncertain
    move.l #31,24(a3)
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_c_return
s2d_c_bad:
    moveq #0,d0
    moveq #1,d1
    bra.s s2d_c_return
s2d_c_uncertain:
    moveq #0,d0
    moveq #2,d1
s2d_c_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts
s2d_c_hide:
    movea.l 36(a3),a0
    moveq #0,d0
    move.l #257,d1
    jsr -426(a6)
    rts
s2d_c_change:
    ; Explicit empty TagItem list, do not pass receipt as tags.
    move.l a3,-(sp)
    clr.l -(sp)
    clr.l -(sp)
    movea.l sp,a3
    movea.l 8(sp),a0
    movea.l 36(a0),a0
    jsr -1026(a6)
    adda.w #8,sp
    movea.l (sp)+,a3
    rts

; Check pinned descriptor, exact height, CHIP span and required ATTACH bits.
; A0 descriptor D0 height D1 expected attach (0/1), D4 width in words.
s2d_c_descriptor:
    movem.l d2-d3/a2,-(sp)
    move.l d0,d2
    move.l d1,d3
    movea.l a0,a2
    moveq #11,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_desc_no
    cmp.w 4(a2),d2
    bne.w s2d_c_desc_no
    movea.l (a2),a0
    move.l d4,d0
    add.l d0,d0
    subq.l #1,d0
    move.l a0,d1
    and.l d0,d1
    bne.s s2d_c_desc_no
    move.l d2,d0
    addq.l #2,d0
    mulu.w d4,d0
    lsl.l #2,d0
    subq.l #1,d0
    bsr.w s2d_c_span
    btst #1,d0
    beq.s s2d_c_desc_no
    moveq #0,d0
    move.b 3(a0),d0
    lsr.b #7,d0
    cmp.b d3,d0
    bne.s s2d_c_desc_no
    move.l d4,d1
    add.l d1,d1
    moveq #0,d0
    move.b 1(a0,d1.l),d0
    lsr.b #7,d0
    cmp.b d3,d0
    bne.s s2d_c_desc_no
    moveq #1,d0
    bra.s s2d_c_desc_return
s2d_c_desc_no:
    moveq #0,d0
s2d_c_desc_return:
    movem.l (sp)+,d2-d3/a2
    rts

; Recheck exact context and paired slots, no dereferencing foreign pointers.
; Returns A0=pair copper words, A1=pair table, D0=1.
s2d_c_context:
    cmp.w 444(a5),d4
    bne.w s2d_c_no
    moveq #3,d0
    lsl.l d6,d0
    move.l d0,d1
    and.b 166(a5),d1
    cmp.b d0,d1
    bne.w s2d_c_no
    move.l 40(a3),d0
    cmp.l 34(a5),d0
    bne.w s2d_c_no
    movea.l d0,a0
    moveq #18,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    move.l 36(a3),d0
    cmp.l (a0),d0
    bne.w s2d_c_no
    movea.l d0,a0
    moveq #40,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.w s2d_c_no
    cmpi.w #320,24(a0)
    bne.w s2d_c_no
    cmpi.w #256,26(a0)
    bne.w s2d_c_no
    cmpi.w #$5000,32(a0)
    bne.w s2d_c_no
    tst.l 12(a0)
    bne.w s2d_c_no
    tst.l 20(a0)
    bne.w s2d_c_no
    move.l 64(a3),d0
    beq.w s2d_c_no
    cmp.l 4(a0),d0
    bne.w s2d_c_no
    move.l 44(a3),d0
    cmp.l 38(a5),d0
    bne.w s2d_c_no
    movea.l d0,a0
    move.l #191,d0
    bsr.w s2d_c_span
    btst #1,d0
    beq.w s2d_c_no
    move.l d6,d0
    lsl.l #3,d0
    lea 88(a0,d0.l),a0
    move.l d6,d1
    lsl.l #2,d1
    addi.w #$120,d1
    cmp.w (a0),d1
    bne.w s2d_c_no
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.w s2d_c_no
    addq.w #2,d1
    cmp.w 8(a0),d1
    bne.w s2d_c_no
    addq.w #2,d1
    cmp.w 12(a0),d1
    bne.w s2d_c_no
    move.l a0,-(sp)
    move.l 48(a3),d0
    cmp.l 208(a5),d0
    bne.s s2d_c_slot_no
    movea.l d0,a0
    moveq #31,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.s s2d_c_slot_no
    move.l d6,d0
    lsl.l #2,d0
    lea 0(a0,d0.l),a1
    movea.l (sp)+,a0
    moveq #1,d0
    rts
s2d_c_slot_no:
    addq.l #4,sp
s2d_c_no:
    moveq #0,d0
    rts
s2d_c_hidden_refs:
    bsr.w s2d_c_context
    tst.l d0
    beq.w s2d_c_no
    cmpa.l (a1),a4
    bne.w s2d_c_no
    cmpa.l 4(a1),a2
    bne.w s2d_c_no
    move.l a4,d0
    beq.s s2d_c_hidden_odd
    cmp.w 10(a4),d6
    bne.w s2d_c_no
    cmpi.w #0,6(a4)
    bne.w s2d_c_no
    cmpi.w #257,8(a4)
    bne.w s2d_c_no
s2d_c_hidden_odd:
    move.l a2,d0
    beq.s s2d_c_hidden_copper
    move.l d6,d0
    addq.l #1,d0
    cmp.w 10(a2),d0
    bne.w s2d_c_no
    cmpi.w #0,6(a2)
    bne.w s2d_c_no
    cmpi.w #257,8(a2)
    bne.w s2d_c_no
s2d_c_hidden_copper:
    move.l 44(a3),d0
    addi.l #176,d0
    cmp.w 6(a0),d0
    bne.w s2d_c_no
    cmp.w 14(a0),d0
    bne.w s2d_c_no
    swap d0
    cmp.w 2(a0),d0
    bne.w s2d_c_no
    cmp.w 10(a0),d0
    bne.w s2d_c_no
    moveq #1,d0
    rts
; Pinned pointer A0, inclusive last byte D0. Common TypeOfMem flags.
; Endpoint corroboration only, not an extent/ownership proof.
s2d_c_span:
    movem.l d2/a0-a1/a6,-(sp)
    move.l a0,d1
    beq.s s2d_c_span_no
    btst #0,d1
    bne.s s2d_c_span_no
    add.l d0,d1
    bcs.s s2d_c_span_no
    movea.l d1,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    move.l d0,d2
    beq.s s2d_c_span_no
    movea.l 4(sp),a1
    jsr -534(a6)
    and.l d2,d0
    bra.s s2d_c_span_return
s2d_c_span_no:
    moveq #0,d0
s2d_c_span_return:
    movem.l (sp)+,d2/a0-a1/a6
    rts
