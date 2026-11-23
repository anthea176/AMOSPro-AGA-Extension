; AGA_NATIVE_MIN_CPU: MC68020
; S1-P1c: strict AGSP v1 payload validator (native MC68020).
; A0 -> payload, D0 -> exact length (validated allocated span, 2-aligned)
; Returns D0=1 success, D0=0 refusal; D1=number of images if valid.
; D2-D7/A2-A6 preserved. Does NOT mutate input or any AMOS bank.
; Caller must prove allocation extent and no concurrent memory invalidation.
; Matches tools/m19_s1_agsp_bank.py canonical pixel/palette validation.
;
AGSP_V_BASE       equ 0
AGSP_V_SIZE       equ 4
AGSP_V_LEFT       equ 8
AGSP_V_LASTID     equ 12
AGSP_V_CURSOR     equ 16
AGSP_V_WIDTH      equ 20
AGSP_V_HEIGHT     equ 24
AGSP_V_STRIDE     equ 28
AGSP_V_DEPTH      equ 32
AGSP_V_PLANE_SIZE equ 36
AGSP_V_COLORS     equ 40
AGSP_V_SEEN       equ 44
AGSP_V_NEXT       equ 48
AGSP_V_PIXEL      equ 52
AGSP_V_COUNT      equ 56
AGSP_V_FRAME      equ 80

AGSP_P1C_VALIDATE:
    movem.l d2-d7/a2-a6,-(sp)
    suba.l #AGSP_V_FRAME,sp
    movea.l sp,a2
    move.l a0,AGSP_V_BASE(a2)
    move.l d0,AGSP_V_SIZE(a2)
    moveq #0,d0
    moveq #0,d1
    move.l AGSP_V_BASE(a2),d2
    beq.w agsp_v_fail
    btst #0,d2
    bne.w agsp_v_fail
    move.l AGSP_V_SIZE(a2),d2
    cmpi.l #32,d2
    bcs.w agsp_v_fail
    cmpi.l #$01000000,d2
    bhi.w agsp_v_fail
    btst #0,d2
    bne.w agsp_v_fail
    movea.l AGSP_V_BASE(a2),a3
    cmpi.l #$41475350,(a3)
    bne.w agsp_v_fail
    cmpi.w #1,4(a3)
    bne.w agsp_v_fail
    tst.w 6(a3)
    bne.w agsp_v_fail
    moveq #0,d7
    move.w 8(a3),d7
    cmpi.l #4096,d7
    bhi.w agsp_v_fail
    move.l d7,AGSP_V_COUNT(a2)
    move.l d7,AGSP_V_LEFT(a2)
    cmpi.w #48,10(a3)
    bne.w agsp_v_fail
    cmpi.l #32,12(a3)
    bne.w agsp_v_fail
    mulu.w #48,d7
    addi.l #32,d7
    cmp.l d2,d7
    bhi.w agsp_v_fail
    cmp.l 16(a3),d7
    bne.w agsp_v_fail
    move.l d7,AGSP_V_CURSOR(a2)
    cmp.l 20(a3),d2
    bne.w agsp_v_fail
    tst.l 24(a3)
    beq.w agsp_v_fail
    tst.l 28(a3)
    bne.w agsp_v_fail
    clr.l AGSP_V_LASTID(a2)
    lea 32(a3),a4

agsp_v_next_image:
    tst.l AGSP_V_LEFT(a2)
    beq.w agsp_v_complete
    moveq #0,d5
    move.w (a4),d5
    cmp.l AGSP_V_LASTID(a2),d5
    bls.w agsp_v_fail
    cmpi.l #4096,d5
    bhi.w agsp_v_fail
    move.l d5,AGSP_V_LASTID(a2)
    moveq #0,d5
    move.w 2(a4),d5
    cmpi.w #16,d5
    beq.w agsp_v_width_ok
    cmpi.w #32,d5
    beq.w agsp_v_width_ok
    cmpi.w #64,d5
    bne.w agsp_v_fail
agsp_v_width_ok:
    move.l d5,AGSP_V_WIDTH(a2)
    lsr.l #3,d5
    move.l d5,AGSP_V_STRIDE(a2)
    cmp.w 8(a4),d5
    bne.w agsp_v_fail
    moveq #0,d5
    move.w 4(a4),d5
    beq.w agsp_v_fail
    cmpi.w #256,d5
    bhi.w agsp_v_fail
    move.l d5,AGSP_V_HEIGHT(a2)
    moveq #0,d6
    move.w 6(a4),d6
    cmpi.w #2,d6
    beq.w agsp_v_depth_ok
    cmpi.w #4,d6
    bne.w agsp_v_fail
agsp_v_depth_ok:
    move.l d6,AGSP_V_DEPTH(a2)
    move.l AGSP_V_STRIDE(a2),d5
    mulu.w AGSP_V_HEIGHT+2(a2),d5
    move.l d5,AGSP_V_PLANE_SIZE(a2)
    mulu.w d6,d5
    tst.w 10(a4)
    bne.w agsp_v_fail
    cmp.l 16(a4),d5
    bne.w agsp_v_fail
    move.l AGSP_V_CURSOR(a2),d6
    cmp.l 12(a4),d6
    bne.w agsp_v_fail
    add.l d5,d6
    bcs.w agsp_v_fail
    cmp.l 20(a4),d6
    bne.w agsp_v_fail
    cmpi.l #48,24(a4)
    bne.w agsp_v_fail
    movea.l AGSP_V_BASE(a2),a5
    adda.l AGSP_V_CURSOR(a2),a5
    movea.l AGSP_V_BASE(a2),a6
    adda.l d6,a6
    addi.l #48,d6
    bcs.w agsp_v_fail
    cmp.l AGSP_V_SIZE(a2),d6
    bhi.w agsp_v_fail
    move.l d6,AGSP_V_CURSOR(a2)
    moveq #0,d6
    move.w 32(a4),d6
    move.l d6,AGSP_V_COLORS(a2)
    moveq #3,d5
    cmpi.w #2,6(a4)
    beq.w agsp_v_max_colors
    moveq #15,d5
agsp_v_max_colors:
    cmp.l d5,d6
    bhi.w agsp_v_fail
    cmpi.w #255,34(a4)
    bhi.w agsp_v_fail
    tst.l 36(a4)
    bne.w agsp_v_fail
    tst.l 40(a4)
    bne.w agsp_v_fail
    tst.l 44(a4)
    bne.w agsp_v_fail
    tst.w (a6)
    bne.w agsp_v_fail
    tst.b 2(a6)
    bne.w agsp_v_fail

    ; All palette entries after last declared opaque pen MUST be zero.
    move.l AGSP_V_COLORS(a2),d5
    addq.l #1,d5
    mulu.w #3,d5
agsp_v_palette_padding:
    cmpi.l #48,d5
    bcc.w agsp_v_palette_unique
    tst.b 0(a6,d5.l)
    bne.w agsp_v_fail
    addq.l #1,d5
    bra.w agsp_v_palette_padding

    ; No two opaque local colors may have identical 24-bit RGB.
agsp_v_palette_unique:
    moveq #1,d4
agsp_v_unique_outer:
    cmp.l AGSP_V_COLORS(a2),d4
    bhi.w agsp_v_pixel_start
    move.l d4,d5
    mulu.w #3,d5
    movea.l a6,a0
    adda.l d5,a0
    bsr.w agsp_v_read_rgb
    move.l d0,d2
    move.l d4,d5
    addq.l #1,d5
agsp_v_unique_inner:
    cmp.l AGSP_V_COLORS(a2),d5
    bhi.w agsp_v_unique_next
    move.l d5,d6
    mulu.w #3,d6
    movea.l a6,a0
    adda.l d6,a0
    bsr.w agsp_v_read_rgb
    cmp.l d2,d0
    beq.w agsp_v_fail
    addq.l #1,d5
    bra.w agsp_v_unique_inner
agsp_v_unique_next:
    addq.l #1,d4
    bra.w agsp_v_unique_outer

    ; Scan every planar pixel and require first appearance order 1..count.
agsp_v_pixel_start:
    clr.l AGSP_V_SEEN(a2)
    move.l #1,AGSP_V_NEXT(a2)
    moveq #0,d4            ; Y
agsp_v_pixel_row:
    moveq #0,d5            ; X
agsp_v_pixel_col:
    clr.l AGSP_V_PIXEL(a2)
    move.l d4,d7
    mulu.w AGSP_V_STRIDE+2(a2),d7
    move.l d5,d0
    lsr.l #3,d0
    add.l d0,d7
    moveq #7,d1
    move.l d5,d0
    andi.w #7,d0
    sub.w d0,d1
    moveq #0,d6            ; plane index
    moveq #1,d3            ; plane bit
agsp_v_pixel_plane:
    move.l AGSP_V_PLANE_SIZE(a2),d0
    mulu.w d6,d0
    add.l d7,d0
    btst d1,0(a5,d0.l)
    beq.w agsp_v_pixel_no_bit
    or.l d3,AGSP_V_PIXEL(a2)
agsp_v_pixel_no_bit:
    lsl.l #1,d3
    addq.l #1,d6
    cmp.l AGSP_V_DEPTH(a2),d6
    bcs.w agsp_v_pixel_plane
    move.l AGSP_V_PIXEL(a2),d0
    beq.w agsp_v_pixel_next
    cmp.l AGSP_V_COLORS(a2),d0
    bhi.w agsp_v_fail
    move.l AGSP_V_SEEN(a2),d2
    btst d0,d2
    bne.w agsp_v_pixel_next
    cmp.l AGSP_V_NEXT(a2),d0
    bne.w agsp_v_fail
    bset d0,d2
    move.l d2,AGSP_V_SEEN(a2)
    addq.l #1,AGSP_V_NEXT(a2)
agsp_v_pixel_next:
    addq.l #1,d5
    cmp.l AGSP_V_WIDTH(a2),d5
    bcs.w agsp_v_pixel_col
    addq.l #1,d4
    cmp.l AGSP_V_HEIGHT(a2),d4
    bcs.w agsp_v_pixel_row
    move.l AGSP_V_COLORS(a2),d0
    addq.l #1,d0
    cmp.l AGSP_V_NEXT(a2),d0
    bne.w agsp_v_fail
    adda.l #48,a4
    subq.l #1,AGSP_V_LEFT(a2)
    bra.w agsp_v_next_image

agsp_v_complete:
    move.l AGSP_V_CURSOR(a2),d0
    cmp.l AGSP_V_SIZE(a2),d0
    bne.w agsp_v_fail
    moveq #1,d0
    move.l AGSP_V_COUNT(a2),d1
    bra.w agsp_v_return
agsp_v_fail:
    moveq #0,d0
    moveq #0,d1
agsp_v_return:
    adda.l #AGSP_V_FRAME,sp
    movem.l (sp)+,d2-d7/a2-a6
    rts

; Read RGB8 triple at A0 into D0=$00RRGGBB; A0 increments by 3.
agsp_v_read_rgb:
    moveq #0,d0
    move.b (a0)+,d0
    lsl.l #8,d0
    move.b (a0)+,d0
    lsl.l #8,d0
    move.b (a0)+,d0
    rts
