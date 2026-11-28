; AGA_NATIVE_MIN_CPU: MC68020
; S2f private raw plane entry into unchanged S2d detached conversion tail.
; Included AFTER the S2D_E_* equates, BEFORE AGSP_S2D_PREPARE_EXT.
; A0 pinned raw plane-major bytes, D0 exact extent, D1 width, D2 height,
; D3 depth. A6 pinned graphics.library V39/40.
; Not an AGSP parser: clipping may remove used pens or reorder first use.
; D0/D1 detached ExtSprite pointers, both zero on refusal.
AGSP_S2F_PREPARE_PLANES:
    movem.l d2-d7/a0-a6,-(sp)
    suba.w #S2D_E_FRAME,sp
    movea.l sp,a3
    movea.l a0,a4
    movea.l a6,a5
    move.l d3,d5
    move.l d0,d3
    move.l d1,d6
    move.l d2,d7
    move.l a5,d0
    beq.w s2d_ext_bad
    btst #0,d0
    bne.w s2d_ext_bad
    cmpi.w #34,18(a5)
    bcs.w s2d_ext_bad
    cmpi.w #1032,16(a5)
    bcs.w s2d_ext_bad
    cmpi.w #39,20(a5)
    bcs.w s2d_ext_bad
    cmpi.w #40,20(a5)
    bhi.w s2d_ext_bad
    cmpi.l #2,d5
    beq.s s2f_raw_depth
    cmpi.l #4,d5
    bne.w s2d_ext_bad
s2f_raw_depth:
    cmpi.l #16,d6
    beq.s s2f_raw_width
    cmpi.l #32,d6
    beq.s s2f_raw_width
    cmpi.l #64,d6
    bne.w s2d_ext_bad
s2f_raw_width:
    tst.l d7
    beq.w s2d_ext_bad
    cmpi.l #256,d7
    bhi.w s2d_ext_bad
    move.l d6,d4
    lsr.l #3,d4
    move.l d4,d2
    mulu.w d7,d2
    move.l d2,d0
    mulu.w d5,d0
    cmp.l d3,d0
    bne.w s2d_ext_bad
    movea.l a4,a0
    bsr.w s2f_c_span
    tst.l d0
    beq.w s2d_ext_bad
    movea.l a5,a6
    bra.w s2d_ext_planes_ready
