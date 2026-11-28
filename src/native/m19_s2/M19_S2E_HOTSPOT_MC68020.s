; AGA_NATIVE_MIN_CPU: MC68020
; S2e: logical anchor -> fully visible 320x256 sprite rectangle.
; D0/D1 signed LONG anchor X/Y. D2 packed signed WORD hotspot X/Y.
; D3/D4 unsigned LONG width/height. D0=1 D1/D2 top-left on success,
; D0/D1/D2=0 on refusal. Preserve D3-D7/A0-A6, A7. No OS or memory I/O.
; No clipping, no unsigned wrap, no narrowing of anchors to WORD.
AGSP_S2E_ANCHOR_TO_ORIGIN:
    movem.l d3-d5,-(sp)
    cmpi.l #16,d3
    beq.s s2e_width_ok
    cmpi.l #32,d3
    beq.s s2e_width_ok
    cmpi.l #64,d3
    bne.w s2e_geometry_bad
s2e_width_ok:
    tst.l d4
    beq.w s2e_geometry_bad
    cmpi.l #256,d4
    bhi.w s2e_geometry_bad
    move.l d2,d5
    swap d5
    ext.l d5
    sub.l d5,d0
    bvs.w s2e_geometry_bad
    move.w d2,d5
    ext.l d5
    sub.l d5,d1
    bvs.w s2e_geometry_bad
    neg.l d3
    addi.l #320,d3
    cmp.l d3,d0
    bhi.w s2e_geometry_bad
    neg.l d4
    addi.l #256,d4
    cmp.l d4,d1
    bhi.w s2e_geometry_bad
    move.l d1,d2
    move.l d0,d1
    moveq #1,d0
    bra.s s2e_geometry_return
s2e_geometry_bad:
    moveq #0,d0
    moveq #0,d1
    moveq #0,d2
s2e_geometry_return:
    movem.l (sp)+,d3-d5
    rts
