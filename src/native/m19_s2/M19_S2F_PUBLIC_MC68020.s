; AGA_NATIVE_MIN_CPU: MC68020
; S2f public source helpers. Included within the private AP20 Sprite island.
; W_CACHE owns only a NEW original until transferred into a receipt.
; Render key: packed signed dx/dy, $80000000 = fully transparent outside.
; Same-frame Move with unchanged key never allocates or rewrites DMA data.
s2d_pub_prepare:
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w p2i_no
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    bsr.w AGSP_S2F_CACHE_CREATE
    move.l d0,W_CACHE(a2)
    move.l d1,W_CSIZE(a2)
    tst.l d0
    beq.w p2i_no
    bsr.w s2d_pub_expect
    tst.l d0
    beq.w p2i_no
    movea.l W_CACHE(a2),a0
    move.l W_CSIZE(a2),d0
    bsr.w s2f_pub_render
    tst.l d0
    beq.w p2i_no
    bra.w s2d_pub_expect

s2f_pub_prepare_current:
    movea.l I_REC(a2),a4
    movea.l W_R_CACHE(a4),a0
    move.l 4(a0),d0
    ; The registry validated this owned original before we arrived here.
    bra.s s2f_pub_render

s2f_pub_render:
    move.l W_KEY(a2),d1
    moveq #0,d3
    cmpi.l #$80000000,d1
    bne.s s2f_pub_shift
    moveq #0,d1
    moveq #0,d2
    moveq #1,d3
    bra.s s2f_pub_convert
s2f_pub_shift:
    move.l d1,d2
    swap d1
    ext.l d1
    ext.l d2
s2f_pub_convert:
    movea.l I_GFX(a2),a6
    bsr.w AGSP_S2F_CACHE_RENDER
    move.l d0,W_E(a2)
    move.l d1,W_O(a2)
    tst.l d0
    beq.w p2i_no
    moveq #1,d0
    rts

s2d_pub_geometry:
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    move.l W_HOT(a2),d2
    move.l W_WIDTH(a2),d3
    move.l W_HEIGHT(a2),d4
    bsr.w AGSP_S2F_CLIP_GEOMETRY
    tst.l d0
    beq.w p2i_no
    move.l d1,I_X(a2)
    move.l d2,I_Y(a2)
    cmpi.l #3,d0
    bne.s s2f_pub_key
    move.l #$80000000,W_KEY(a2)
    rts
s2f_pub_key:
    swap d3
    move.w d4,d3
    move.l d3,W_KEY(a2)
    rts
