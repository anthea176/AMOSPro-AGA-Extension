; AGA_NATIVE_MIN_CPU: MC68020
; S2f P2a private owned full-frame cache and detached rendering.
; No AMOS, channel, Copper, live ExtSprite or registry mutation.
; Caller pins input allocation and bank lifetime, owns returned cache,
; and serializes use/free. TypeOfMem is endpoint corroboration only.
; Cache: 84 byte header followed by full original plane-major bytes.
S2F_C_MAGIC  equ $53324643 ; S2FC
S2F_C_LEN    equ 4
S2F_C_W      equ 8
S2F_C_H      equ 12
S2F_C_DEPTH  equ 16
S2F_C_ID     equ 20
S2F_C_GEN    equ 24
S2F_C_HOT    equ 28
S2F_C_COLORS equ 32 ; opaque count.W, source transparent pen.W
S2F_C_PAL    equ 36
S2F_C_DATA   equ 84
S2F_C_MAX    equ 8276
S2F_C_ALLOC  equ -684 ; AllocVec
S2F_C_FREE   equ -690 ; FreeVec

; A0 pinned canonical AGSP payload, D0 exact bytes, D1 image ID.
; Return D0 owned cache pointer, D1 exact logical allocation size;
; both zero on refusal. Preserve D2-D7/A0-A6.
AGSP_S2F_CACHE_CREATE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    move.l d0,d6
    move.l d1,d5
    cmpi.l #1,d5
    bcs.w s2f_c_create_bad
    cmpi.l #4096,d5
    bhi.w s2f_c_create_bad
    cmpi.l #32,d6
    bcs.w s2f_c_create_bad
    cmpi.l #$01000000,d6
    bhi.w s2f_c_create_bad
    bsr.w s2f_c_span
    tst.l d0
    beq.w s2f_c_create_bad
    movea.l a3,a0
    move.l d6,d0
    bsr.w AGSP_P1C_VALIDATE
    tst.l d0
    beq.w s2f_c_create_bad
    tst.l d1
    beq.w s2f_c_create_bad
    lea 32(a3),a2
    subq.w #1,d1
s2f_c_find:
    cmp.w (a2),d5
    beq.s s2f_c_found
    bcs.w s2f_c_create_bad
    adda.w #48,a2
    dbra d1,s2f_c_find
    bra.w s2f_c_create_bad
s2f_c_found:
    move.l 16(a2),d6
    move.l d6,d7
    addi.l #S2F_C_DATA,d7
    cmpi.l #S2F_C_MAX,d7
    bhi.w s2f_c_create_bad
    ; Same Exec allocation family as the S2e named root.
    move.l d7,d0
    moveq #1,d1 ; MEMF_PUBLIC, every byte initialized below
    movea.l $0004.w,a6
    jsr S2F_C_ALLOC(a6)
    tst.l d0
    beq.w s2f_c_create_bad
    movea.l d0,a4
    move.l #S2F_C_MAGIC,(a4)
    move.l d7,S2F_C_LEN(a4)
    moveq #0,d0
    move.w 2(a2),d0
    move.l d0,S2F_C_W(a4)
    move.w 4(a2),d0
    move.l d0,S2F_C_H(a4)
    move.w 6(a2),d0
    move.l d0,S2F_C_DEPTH(a4)
    move.l d5,S2F_C_ID(a4)
    move.l 24(a3),S2F_C_GEN(a4)
    move.l 28(a2),S2F_C_HOT(a4)
    move.l 32(a2),S2F_C_COLORS(a4)
    movea.l a3,a0
    adda.l 20(a2),a0
    lea S2F_C_PAL(a4),a1
    moveq #11,d0
s2f_c_copy_palette:
    move.l (a0)+,(a1)+
    dbra d0,s2f_c_copy_palette
    movea.l a3,a0
    adda.l 12(a2),a0
    ; a1 now points at +84. Canonical data is always even length.
    move.l d6,d0
    lsr.l #1,d0
    subq.w #1,d0
s2f_c_copy_plane:
    move.w (a0)+,(a1)+
    dbra d0,s2f_c_copy_plane
    move.l a4,d0
    move.l d7,d1
    bra.s s2f_c_create_return
s2f_c_create_bad:
    moveq #0,d0
    moveq #0,d1
s2f_c_create_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; A0 caller-owned cache, D0 exact size. D0=1 structurally consistent.
; No use as a general arbitrary-pointer or allocation-ownership oracle.
; Original pixel/palette canonicality was established at creation.
AGSP_S2F_CACHE_CHECK:
    movem.l d1-d7/a0-a6,-(sp)
    movea.l a0,a3
    move.l d0,d7
    cmpi.l #88,d7
    bcs.w s2f_c_check_bad
    cmpi.l #S2F_C_MAX,d7
    bhi.w s2f_c_check_bad
    bsr.w s2f_c_span
    tst.l d0
    beq.w s2f_c_check_bad
    cmpi.l #S2F_C_MAGIC,(a3)
    bne.w s2f_c_check_bad
    cmp.l S2F_C_LEN(a3),d7
    bne.w s2f_c_check_bad
    move.l S2F_C_W(a3),d4
    cmpi.l #16,d4
    beq.s s2f_c_check_width
    cmpi.l #32,d4
    beq.s s2f_c_check_width
    cmpi.l #64,d4
    bne.w s2f_c_check_bad
s2f_c_check_width:
    move.l S2F_C_H(a3),d5
    beq.w s2f_c_check_bad
    cmpi.l #256,d5
    bhi.w s2f_c_check_bad
    move.l S2F_C_DEPTH(a3),d6
    cmpi.l #2,d6
    beq.s s2f_c_check_simple
    cmpi.l #4,d6
    bne.w s2f_c_check_bad
    cmpi.w #15,S2F_C_COLORS(a3)
    bhi.w s2f_c_check_bad
    ; The canonical validator allows a 4-plane image with fewer used pens.
    ; Public Sprite display applies its stricter opaque-count contract.
    bra.s s2f_c_check_colors
s2f_c_check_simple:
    cmpi.w #3,S2F_C_COLORS(a3)
    bhi.w s2f_c_check_bad
s2f_c_check_colors:
    cmpi.w #255,S2F_C_COLORS+2(a3)
    bhi.w s2f_c_check_bad
    move.l S2F_C_ID(a3),d0
    beq.w s2f_c_check_bad
    cmpi.l #4096,d0
    bhi.w s2f_c_check_bad
    tst.l S2F_C_GEN(a3)
    beq.w s2f_c_check_bad
    lsr.l #3,d4
    mulu.w d5,d4
    mulu.w d6,d4
    addi.l #S2F_C_DATA,d4
    cmp.l d7,d4
    bne.w s2f_c_check_bad
    moveq #1,d0
    bra.s s2f_c_check_return
s2f_c_check_bad:
    moveq #0,d0
s2f_c_check_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

; A0 cache, D0 exact size. Only its exclusive owner may call.
; On success caller must clear its receipt; do not retry a freed pointer.
AGSP_S2F_CACHE_FREE:
    movem.l d1-d7/a0-a6,-(sp)
    bsr.w AGSP_S2F_CACHE_CHECK
    tst.l d0
    beq.s s2f_c_free_return
    movea.l a0,a1
    movea.l $0004.w,a6
    jsr S2F_C_FREE(a6)
    moveq #1,d0
s2f_c_free_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

; A0 cache, D0 exact size, D1/D2 signed dx/dy, D3=0 translate,
; D3=1 all-transparent (requires dx=dy=0); A6 pinned graphics.library.
; D0/D1 detached even/odd ExtSprite pointers, 0/0 on refusal.
; All source bytes immutable; scratch never retained by OS after conversion.
; No mutation of a current/staged/live DMA descriptor. Caller owns results.
AGSP_S2F_CACHE_RENDER:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a4
    movea.l a6,a5
    move.l d1,d6
    move.l d2,d7
    move.l d3,d5
    bsr.w AGSP_S2F_CACHE_CHECK
    tst.l d0
    beq.w s2f_c_render_bad
    cmpi.l #1,d5
    bhi.w s2f_c_render_bad
    move.l d6,d0
    or.l d7,d0
    tst.l d5
    beq.s s2f_c_translate
    tst.l d0
    bne.w s2f_c_render_bad
    bra.s s2f_c_scratch
s2f_c_translate:
    ; Geometry preflight before any scratch allocation.
    move.l S2F_C_W(a4),d0
    neg.l d0
    cmp.l d0,d6
    ble.w s2f_c_render_bad
    cmp.l S2F_C_W(a4),d6
    bge.w s2f_c_render_bad
    move.l S2F_C_H(a4),d0
    neg.l d0
    cmp.l d0,d7
    ble.w s2f_c_render_bad
    cmp.l S2F_C_H(a4),d7
    bge.w s2f_c_render_bad
    move.l d6,d0
    or.l d7,d0
    bne.s s2f_c_scratch
    suba.l a3,a3
    lea S2F_C_DATA(a4),a2
    bra.w s2f_c_convert
s2f_c_scratch:
    move.l S2F_C_LEN(a4),d0
    subi.l #S2F_C_DATA,d0
    moveq #1,d1
    movea.l $0004.w,a6
    jsr S2F_C_ALLOC(a6)
    tst.l d0
    beq.w s2f_c_render_bad
    movea.l d0,a3
    tst.l d5
    bne.s s2f_c_blank
    lea S2F_C_DATA(a4),a0
    movea.l a3,a1
    move.l d6,d2
    move.l d7,d3
    move.l S2F_C_W(a4),d4
    lsr.l #3,d4
    mulu.w S2F_C_H+2(a4),d4
    move.l d4,d5
    move.l S2F_C_DEPTH(a4),d7
    subq.w #1,d7
s2f_c_clip_all:
    move.l S2F_C_W(a4),d0
    move.l S2F_C_H(a4),d1
    bsr.w AGSP_S2F_CLIP_PLANE
    tst.l d0
    beq.s s2f_c_scratch_bad
    adda.l d4,a0
    adda.l d4,a1
    dbra d7,s2f_c_clip_all
    bra.s s2f_c_scratch_ready
s2f_c_blank:
    movea.l a3,a1
    move.l S2F_C_LEN(a4),d0
    subi.l #S2F_C_DATA,d0
    lsr.l #1,d0
    subq.w #1,d0
s2f_c_blank_loop:
    clr.w (a1)+
    dbra d0,s2f_c_blank_loop
s2f_c_scratch_ready:
    movea.l a3,a2
s2f_c_convert:
    movea.l a2,a0
    move.l S2F_C_LEN(a4),d0
    subi.l #S2F_C_DATA,d0
    move.l S2F_C_W(a4),d1
    move.l S2F_C_H(a4),d2
    move.l S2F_C_DEPTH(a4),d3
    movea.l a5,a6
    bsr.w AGSP_S2F_PREPARE_PLANES
    move.l d0,d6
    move.l d1,d7
    move.l a3,d0
    beq.s s2f_c_render_result
    bra.s s2f_c_scratch_free
s2f_c_scratch_bad:
    moveq #0,d6
    moveq #0,d7
s2f_c_scratch_free:
    movea.l a3,a1
    movea.l $0004.w,a6
    jsr S2F_C_FREE(a6)
s2f_c_render_result:
    move.l d6,d0
    move.l d7,d1
    bra.s s2f_c_render_return
s2f_c_render_bad:
    moveq #0,d0
    moveq #0,d1
s2f_c_render_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; A0 caller-pinned even pointer, D0 exact positive extent.
; D0=1 both endpoints mapped, 0 otherwise; preserve A0 and D2-D7.
s2f_c_span:
    movem.l d2-d3/a0-a2/a6,-(sp)
    tst.l d0
    beq.s s2f_c_span_bad
    move.l a0,d2
    beq.s s2f_c_span_bad
    btst #0,d2
    bne.s s2f_c_span_bad
    move.l d2,d3
    subq.l #1,d0
    add.l d0,d3
    bcs.s s2f_c_span_bad
    movea.l $0004.w,a6
    movea.l d2,a1
    jsr -534(a6)
    tst.l d0
    beq.s s2f_c_span_bad
    movea.l d3,a1
    jsr -534(a6)
    tst.l d0
    beq.s s2f_c_span_bad
    moveq #1,d0
    bra.s s2f_c_span_return
s2f_c_span_bad:
    moveq #0,d0
s2f_c_span_return:
    movem.l (sp)+,d2-d3/a0-a2/a6
    rts
