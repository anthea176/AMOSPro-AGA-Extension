; AGA_NATIVE_MIN_CPU: MC68020
; Private P2d workaround for AllocSpriteDataA V39 BUGS.
; A0 = freshly allocated, detached odd ExtSprite; D0 = width px,
; D1 = height; A6 = pinned live graphics.library V39.
; Caller proves ownership and allocation extent; TypeOfMem is only
; endpoint corroboration. No acquisition, publication or OS-field writes.
; D0=1 success, 0 refusal; preserve D1-D7/A0-A6.
AGSP_S2D_ATTACH39:
    movem.l d1-d7/a0-a6,-(sp)
    cmpi.w #39,20(a6)
    bne.w s2d_v39_no
    move.l d0,d3
    cmpi.l #16,d3
    beq.s s2d_v39_width
    cmpi.l #32,d3
    beq.s s2d_v39_width
    cmpi.l #64,d3
    bne.w s2d_v39_no
s2d_v39_width:
    move.l d1,d4
    beq.w s2d_v39_no
    cmpi.l #256,d4
    bhi.w s2d_v39_no
    moveq #11,d0
    bsr.w s2d_v39_span
    tst.l d0
    beq.w s2d_v39_no
    cmp.w 4(a0),d4
    bne.w s2d_v39_no
    movea.l (a0),a0
    move.l d3,d6
    lsr.l #3,d6
    move.l d6,d0
    subq.l #1,d0
    move.l a0,d1
    and.l d0,d1
    bne.w s2d_v39_no
    addq.l #2,d4
    move.l d6,d0
    add.l d0,d0
    mulu.w d4,d0
    subq.l #1,d0
    bsr.w s2d_v39_span
    btst #1,d0
    beq.w s2d_v39_no
    ; Autodoc: bit7 of second word; additionally third (32px)
    ; or fifth (64px). Only modify owned, detached Chip data.
    bset #7,3(a0)
    cmpi.l #16,d3
    beq.s s2d_v39_yes
    bset #7,1(a0,d6.l)
s2d_v39_yes:
    moveq #1,d0
    bra.s s2d_v39_return
s2d_v39_no:
    moveq #0,d0
s2d_v39_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts
s2d_v39_span:
    movem.l d2/a0-a1/a6,-(sp)
    move.l a0,d1
    beq.s s2d_v39_span_no
    btst #0,d1
    bne.s s2d_v39_span_no
    add.l d0,d1
    bcs.s s2d_v39_span_no
    movea.l d1,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    move.l d0,d2
    beq.s s2d_v39_span_no
    movea.l 4(sp),a1
    jsr -534(a6)
    and.l d2,d0
    bra.s s2d_v39_span_return
s2d_v39_span_no:
    moveq #0,d0
s2d_v39_span_return:
    movem.l (sp)+,d2/a0-a1/a6
    rts
