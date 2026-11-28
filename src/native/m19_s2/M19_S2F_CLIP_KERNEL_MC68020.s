; AGA_NATIVE_MIN_CPU: MC68020
; S2f P1: private clipping geometry and single-plane raster kernel.
; Standalone test entry table. Not linked to public AP20 in P1.
    bra.w AGSP_S2F_CLIP_GEOMETRY
    bra.w AGSP_S2F_CLIP_PLANE

; D0/D1 signed logical anchor; D2 packed signed WORD hotspot X/Y;
; D3/D4 unsigned width/height (16/32/64, 1..256).
; D0=0 invalid/overflow, 1 full, 2 partial, 3 wholly outside.
; For 1/2, D1/D2 = bounded fixed-size display origin,
; D3/D4 = signed translation of original pixels inside that rectangle.
; For 0/3, D1-D4=0. Preserve D5-D7/A0-A6. No memory except stack.
AGSP_S2F_CLIP_GEOMETRY:
    movem.l d5-d7,-(sp)
    cmpi.l #16,d3
    beq.s s2f_g_width
    cmpi.l #32,d3
    beq.s s2f_g_width
    cmpi.l #64,d3
    bne.w s2f_g_bad
s2f_g_width:
    tst.l d4
    beq.w s2f_g_bad
    cmpi.l #256,d4
    bhi.w s2f_g_bad
    move.l d2,d5
    swap d5
    ext.l d5
    sub.l d5,d0
    bvs.w s2f_g_bad
    move.w d2,d5
    ext.l d5
    sub.l d5,d1
    bvs.w s2f_g_bad
    ; Classify disjoint rectangles before computing any extent/shift.
    move.l d3,d5
    neg.l d5
    cmp.l d5,d0
    ble.w s2f_g_outside
    cmpi.l #320,d0
    bge.w s2f_g_outside
    move.l d4,d5
    neg.l d5
    cmp.l d5,d1
    ble.w s2f_g_outside
    cmpi.l #256,d1
    bge.w s2f_g_outside
    move.l d0,d2
    move.l d1,d7
    move.l #320,d5
    sub.l d3,d5
    tst.l d0
    bpl.s s2f_g_x_high
    moveq #0,d0
s2f_g_x_high:
    cmp.l d5,d0
    ble.s s2f_g_x_ok
    move.l d5,d0
s2f_g_x_ok:
    move.l #256,d6
    sub.l d4,d6
    tst.l d1
    bpl.s s2f_g_y_high
    moveq #0,d1
s2f_g_y_high:
    cmp.l d6,d1
    ble.s s2f_g_y_ok
    move.l d6,d1
s2f_g_y_ok:
    move.l d2,d3
    sub.l d0,d3
    move.l d7,d4
    sub.l d1,d4
    move.l d1,d2
    move.l d0,d1
    move.l d3,d0
    or.l d4,d0
    beq.s s2f_g_full
    moveq #2,d0
    bra.s s2f_g_return
s2f_g_full:
    moveq #1,d0
    bra.s s2f_g_return
s2f_g_bad:
    moveq #0,d0
    bra.s s2f_g_clear
s2f_g_outside:
    moveq #3,d0
s2f_g_clear:
    moveq #0,d1
    moveq #0,d2
    moveq #0,d3
    moveq #0,d4
s2f_g_return:
    movem.l (sp)+,d5-d7
    rts

; Clip/translate ONE planar bitplane into a separate, same-size buffer.
; A0 immutable source, A1 detached writable destination, both caller-pinned.
; D0 width, D1 height, D2 signed dx, D3 signed dy,
; D4 source extent, D5 destination extent: exact width/8*height bytes.
; Pixel at destination(x,y) = source(x-dx,y-dy), or zero if outside.
; Only overlapping full/partial rectangles: |dx|<width, |dy|<height.
; D0=1 success, 0 refusal with destination untouched. Preserve all other regs.
; Validate arithmetic and disjoint spans, not OS allocation ownership.
; Never call on live DMA data. One byte per iteration, MSB-first.
S2F_ROWBYTES equ 0
S2F_HEIGHT   equ 4
S2F_DX       equ 8
S2F_DY       equ 12
S2F_PLANE_FRAME equ 16

AGSP_S2F_CLIP_PLANE:
    movem.l d1-d7/a0-a6,-(sp)
    suba.w #S2F_PLANE_FRAME,sp
    movea.l sp,a2
    cmpi.l #16,d0
    beq.s s2f_p_width
    cmpi.l #32,d0
    beq.s s2f_p_width
    cmpi.l #64,d0
    bne.w s2f_p_bad
s2f_p_width:
    tst.l d1
    beq.w s2f_p_bad
    cmpi.l #256,d1
    bhi.w s2f_p_bad
    move.l d0,d6
    neg.l d6
    cmp.l d6,d2
    ble.w s2f_p_bad
    cmp.l d0,d2
    bge.w s2f_p_bad
    move.l d1,d6
    neg.l d6
    cmp.l d6,d3
    ble.w s2f_p_bad
    cmp.l d1,d3
    bge.w s2f_p_bad
    lsr.l #3,d0
    move.l d0,S2F_ROWBYTES(a2)
    move.l d1,S2F_HEIGHT(a2)
    move.l d2,S2F_DX(a2)
    move.l d3,S2F_DY(a2)
    mulu.w d1,d0
    cmp.l d0,d4
    bne.w s2f_p_bad
    cmp.l d0,d5
    bne.w s2f_p_bad
    move.l a0,d6
    beq.w s2f_p_bad
    move.l a1,d7
    beq.w s2f_p_bad
    add.l d0,d6
    bcs.w s2f_p_bad
    add.l d0,d7
    bcs.w s2f_p_bad
    cmpa.l d6,a1
    bcc.s s2f_p_disjoint
    cmpa.l d7,a0
    bcs.w s2f_p_bad
s2f_p_disjoint:
    moveq #0,d7
s2f_p_row:
    move.l d7,d6
    sub.l S2F_DY(a2),d6
    cmp.l S2F_HEIGHT(a2),d6
    bcc.s s2f_p_zero_row
    mulu.w S2F_ROWBYTES+2(a2),d6
    lea 0(a0,d6.l),a3
    moveq #0,d5
s2f_p_byte:
    move.l d5,d4
    lsl.l #3,d4
    sub.l S2F_DX(a2),d4
    move.l d4,d3
    asr.l #3,d3
    andi.l #7,d4
    moveq #0,d0
    cmp.l S2F_ROWBYTES(a2),d3
    bcc.s s2f_p_high_zero
    move.b 0(a3,d3.l),d0
s2f_p_high_zero:
    lsl.w #8,d0
    addq.l #1,d3
    cmp.l S2F_ROWBYTES(a2),d3
    bcc.s s2f_p_low_zero
    move.b 0(a3,d3.l),d0
s2f_p_low_zero:
    lsl.w d4,d0
    lsr.w #8,d0
    move.b d0,(a1)+
    addq.l #1,d5
    cmp.l S2F_ROWBYTES(a2),d5
    bcs.s s2f_p_byte
    bra.s s2f_p_next
s2f_p_zero_row:
    move.l S2F_ROWBYTES(a2),d5
    subq.w #1,d5
s2f_p_zero_byte:
    clr.b (a1)+
    dbra d5,s2f_p_zero_byte
s2f_p_next:
    addq.l #1,d7
    cmp.l S2F_HEIGHT(a2),d7
    bcs.s s2f_p_row
    moveq #1,d0
    bra.s s2f_p_return
s2f_p_bad:
    moveq #0,d0
s2f_p_return:
    adda.w #S2F_PLANE_FRAME,sp
    movem.l (sp)+,d1-d7/a0-a6
    rts
