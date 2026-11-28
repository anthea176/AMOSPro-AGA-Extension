; AGA_NATIVE_MIN_CPU: MC68020
; S2f v8 cache receipts, shared by Sprite and the compact Close/End unit.
; A3 occupied record, previously checked width, height, depth and IDs.
; Cache ownership established at create/transfer, not by TypeOfMem.
; Current always has an original. A same-image stage shares it (stage
; cache=0); a different-image stage owns a separate immutable original.
; No access to raw cached pixel bytes on this retirement path.
s2f_reg_validate:
    movea.l W_R_CACHE(a3),a0
    move.l W_R_IMAGE(a3),d0
    bsr.w s2f_reg_cache
    tst.l d0
    beq.s s2f_reg_no
    move.l W_R_HOT(a3),d0
    cmp.l 28(a0),d0
    bne.s s2f_reg_no
    tst.l 80(a3)
    bne.s s2f_reg_has_stage
    move.l W_R_STAGECACHE(a3),d0
    or.l W_R_STAGEKEY(a3),d0
    bne.s s2f_reg_no
    bra.s s2f_reg_yes
s2f_reg_has_stage:
    move.l W_R_STAGE(a3),d0
    cmp.l W_R_IMAGE(a3),d0
    bne.s s2f_reg_other
    tst.l W_R_STAGECACHE(a3)
    bne.s s2f_reg_no
s2f_reg_yes:
    moveq #1,d0
    rts
s2f_reg_other:
    movea.l W_R_STAGECACHE(a3),a0
    cmpa.l W_R_CACHE(a3),a0
    beq.s s2f_reg_no
    bra.s s2f_reg_cache
s2f_reg_no:
    moveq #0,d0
    rts

; A0 immutable owned cache, D0 expected image ID, A3 record.
; Check size/metadata and descriptor disjointness before a caller frees.
; Preserve A0 and D2-D7/A2-A6. Span helper preserves A0.
s2f_reg_cache:
    movem.l d2-d3/a1,-(sp)
    move.l d0,d2
    move.l 12(a3),d3
    lsr.l #3,d3
    mulu.w 62(a3),d3
    mulu.w 18(a3),d3
    addi.l #84,d3
    move.l d3,d0
    subq.l #1,d0
    bsr.w s2d_c_span
    tst.l d0
    beq.s s2f_reg_cache_no
    cmpi.l #$53324643,(a0)
    bne.s s2f_reg_cache_no
    cmp.l 4(a0),d3
    bne.s s2f_reg_cache_no
    cmp.l 20(a0),d2
    bne.s s2f_reg_cache_no
    move.l W_R_GEN(a3),d0
    cmp.l 24(a0),d0
    bne.s s2f_reg_cache_no
    move.l 12(a3),d0
    cmp.l 8(a0),d0
    bne.s s2f_reg_cache_no
    move.l 60(a3),d0
    cmp.l 12(a0),d0
    bne.s s2f_reg_cache_no
    move.l 16(a3),d0
    cmp.l 16(a0),d0
    bne.s s2f_reg_cache_no
    move.l W_R_COLORS(a3),d0
    cmp.w 32(a0),d0
    bne.s s2f_reg_cache_no
    lea s2d_reg_ptrs(pc),a1
    move.l a0,d1
    moveq #5,d3 ; the six ExtSprite slots precede the two caches
s2f_reg_cache_alias:
    moveq #0,d0
    move.b (a1)+,d0
    cmp.l 0(a3,d0.w),d1
    beq.s s2f_reg_cache_no
    dbra d3,s2f_reg_cache_alias
    moveq #1,d0
    bra.s s2f_reg_cache_return
s2f_reg_cache_no:
    moveq #0,d0
s2f_reg_cache_return:
    movem.l (sp)+,d2-d3/a1
    rts

; A0 receipt or private stack, D0 cache pointer field offset.
; Only after caller proves ownership (and DMA retirement for receipt).
; Clear before void FreeVec; preserve all registers used by caller.
s2f_reg_free:
    movem.l d0-d1/a0-a1/a6,-(sp)
    move.l 0(a0,d0.w),d1
    beq.s s2f_reg_free_return
    clr.l 0(a0,d0.w)
    movea.l d1,a1
    movea.l $0004.w,a6
    jsr -690(a6)
s2f_reg_free_return:
    movem.l (sp)+,d0-d1/a0-a1/a6
    rts
