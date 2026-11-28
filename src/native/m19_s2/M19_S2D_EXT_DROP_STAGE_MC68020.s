; AGA_NATIVE_MIN_CPU: MC68020
; A0 owned receipt, A6 GfxBase. Only phase1 private or phase3 fenced
; previous frame may be freed. Never free current/blank/uncertain stage.
; Reuse exact P2c2 checks and all eight reference scans.
AGSP_S2D_EXT_DROP_STAGE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a6,a5
    bsr.w s2d_x_base
    tst.l d0
    beq.w s2d_drop_no
    cmpi.l #1,80(a3)
    beq.s s2d_drop_stage
    cmpi.l #3,80(a3)
    bne.w s2d_drop_no
s2d_drop_stage:
    bsr.w s2d_x_current
    tst.l d0
    beq.w s2d_drop_uncertain
    move.l 72(a3),d0
    bsr.w s2d_x_distinct
    tst.l d0
    beq.w s2d_drop_no
    movea.l 72(a3),a0
    move.l d7,d0
    moveq #0,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_drop_no
    movea.l 72(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_drop_no
    cmpi.l #4,d5
    bne.s s2d_drop_simple
    move.l 76(a3),d0
    cmp.l 72(a3),d0
    beq.w s2d_drop_no
    bsr.w s2d_x_distinct
    tst.l d0
    beq.w s2d_drop_no
    movea.l 76(a3),a0
    move.l d7,d0
    moveq #1,d1
    bsr.w s2d_c_descriptor
    tst.l d0
    beq.w s2d_drop_no
    movea.l 76(a3),a0
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_drop_no
    bra.s s2d_drop_check
s2d_drop_simple:
    tst.l 76(a3)
    bne.w s2d_drop_no
s2d_drop_check:
    bsr.w s2d_x_refs
    tst.l d0
    beq.s s2d_drop_uncertain
    movea.l 72(a3),a2
    clr.l 72(a3)
    jsr -1032(a6)
    move.l 76(a3),d0
    beq.s s2d_drop_done
    movea.l d0,a2
    clr.l 76(a3)
    jsr -1032(a6)
s2d_drop_done:
    clr.l 80(a3)
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_drop_return
s2d_drop_uncertain:
    move.l #15,24(a3)
s2d_drop_no:
    moveq #0,d0
    moveq #1,d1
s2d_drop_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts
