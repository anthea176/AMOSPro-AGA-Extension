; AGA_NATIVE_MIN_CPU: MC68020
; P2l-a private read-only DMA observation. Appended to exact P2k UNIT207.
; NO public AP20 token, NO FreeVec of exposed memory, NO release certificate.
; D0=1: two sampled idle observations, NOT proof of hardware detachment.
; D0<0: refusal reason. D1 volatile; D2-D7/A0-A6 preserved.
; No writes to record, Chip, Copper, Sprite descriptor or old ViewPort.
; Existing private named P2k protocol supplies lifetime and allocation
; provenance; TypeOfMem endpoints are corroboration, not size proof.
; Task context only. Never called from an interrupt or with Forbid active.
p2l_observe:
    movem.l d2-d7/a0-a6,-(sp)
    moveq #0,d0
    bsr.w p2h_enter
    tst.l d0
    bne.s p2l_borrowed
    neg.l d1
    subi.l #130,d1
    move.l d1,d7
    bra.w p2l_return
p2l_borrowed:
    movea.l d0,a4
    move.l #-180,d7
    tst.l 12(a4)          ; actual successful CloseScreen receipt required
    bne.w p2l_leave
    tst.l 48(a4)          ; no live lifetime Task
    bne.w p2l_leave
    move.l (a4),d0
    beq.w p2l_leave
    movea.l d0,a3
    move.l #-181,d7
    movea.l a3,a0
    moveq #40,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2l_leave
    move.l #-182,d7
    cmpi.l #4,12(a3)      ; exactly retired; no active/uncertain receipt
    bne.w p2l_leave
    move.l #-183,d7
    move.l (a3),d3
    move.l 4(a3),d4
    cmpi.l #72,d4
    bcs.w p2l_leave
    cmpi.l #2112,d4
    bhi.w p2l_leave
    movea.l d3,a0
    move.l d4,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2l_leave
    add.l d3,d4           ; exclusive end of pinned private Chip block
    bcs.w p2l_leave
    move.l a3,d0
    cmp.l d3,d0
    bcs.s p2l_record_below
    cmp.l d4,d0
    bcs.w p2l_leave
    bra.s p2l_geometry
p2l_record_below:
    addi.l #40,d0
    bcs.w p2l_leave
    cmp.l d3,d0
    bhi.w p2l_leave
p2l_geometry:
    movea.l d3,a0
    moveq #0,d0
    move.w 4(a0),d0
    beq.w p2l_leave
    cmpi.w #256,d0
    bhi.w p2l_leave
    lsl.l #2,d0
    addq.l #8,d0
    move.l d0,d1
    addi.l #48,d1
    cmpi.l #48,40(a0)
    bne.w p2l_leave
    cmp.l 44(a0),d1
    bne.w p2l_leave
    add.l d1,d0
    cmp.l 4(a3),d0
    bne.w p2l_leave
    cmp.l 12(a0),d0
    bne.w p2l_leave
    movea.l $0004.w,a6
    movea.l d3,a1
    jsr -534(a6)
    btst #1,d0            ; MEMF_CHIP at both mapped endpoints
    beq.w p2l_leave
    move.l d4,d0
    subq.l #1,d0
    movea.l d0,a1
    jsr -534(a6)
    btst #1,d0
    beq.w p2l_leave
    ; Use a new library reference, never dereference the old Screen/VP.
    move.l #-184,d7
    lea p2l_gfx_name(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.w p2l_leave
    movea.l d0,a5
    bsr.w p2l_sample
    move.l d0,d7
    cmpi.l #1,d7
    bne.w p2l_close_gfx
    move.l 38(a5),-(sp)
    move.l 208(a5),-(sp)
    movea.l a5,a6
    jsr -270(a6)          ; WaitTOF, no Forbid or Disable
    jsr -270(a6)
    bsr.w p2l_sample
    move.l d0,d7
    move.l (sp)+,d0
    cmp.l 208(a5),d0
    bne.s p2l_changed_table
    move.l (sp)+,d0
    cmp.l 38(a5),d0
    beq.s p2l_close_gfx
    bra.s p2l_changed
p2l_changed_table:
    addq.l #4,sp
p2l_changed:
    move.l #-188,d7
p2l_close_gfx:
    movea.l $0004.w,a6
    movea.l a5,a1
    jsr -414(a6)          ; CloseLibrary, only our independent reference
p2l_leave:
    movea.l a4,a0
    bsr.w p2h_leave
    tst.l d0
    bne.s p2l_return
    move.l #-189,d7
p2l_return:
    move.l d7,d0
    movem.l (sp)+,d2-d7/a0-a6
    rts

p2l_sample:
    ; A5 live GfxBase, A3 record, D3..D4 exclusive Chip span.
    ; Preserve D3/D4/D7/A3-A6. Check the observed V39/V40 idle shape.
    movea.l a5,a0
    move.l #212,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2l_bad_gfx
    cmpi.w #212,18(a5)
    bcs.w p2l_bad_gfx
    cmpi.w #39,20(a5)
    bcs.w p2l_bad_gfx
    cmpi.w #40,20(a5)
    bhi.w p2l_bad_gfx
    tst.l 34(a5)
    bne.w p2l_not_idle
    movea.l 38(a5),a2
    movea.l a2,a0
    move.l #180,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2l_bad_layout
    lea 164(a2),a0
    move.l a0,d0
    cmp.l 50(a5),d0
    bne.w p2l_not_idle
    cmp.l 54(a5),d0
    bne.w p2l_not_idle
    cmpi.l #$fffffffe,164(a2)
    bne.w p2l_not_idle
    movea.l 208(a5),a0
    moveq #32,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2l_bad_layout
    movea.l a0,a1
    move.l a1,d2          ; stable table base within this sample
    moveq #0,d0
    move.b 166(a5),d0
    andi.b #12,d0
    bne.w p2l_refs
    tst.l 8(a1)
    bne.w p2l_refs
    tst.l 12(a1)
    bne.w p2l_refs
    lea 176(a2),a0
    move.l a0,d0
    moveq #0,d1
    move.w 106(a2),d1
    swap d1
    move.w 110(a2),d1
    cmp.l d0,d1
    bne.w p2l_refs
    moveq #0,d1
    move.w 114(a2),d1
    swap d1
    move.w 118(a2),d1
    cmp.l d0,d1
    bne.w p2l_refs
    ; All eight startup MOVE pairs and all eight SimpleSprite pointers.
    ; Neither sampled list nor table proves absence from other lists
    ; or from the chipset's internal DMA address latch.
    lea 88(a2),a0
    moveq #7,d1
    move.w #$120,d5
    move.l a3,d6
    addi.l #40,d6         ; record range, not only guard descriptor
    bcs.w p2l_bad_layout
p2l_scan:
    cmp.w (a0)+,d5
    bne.w p2l_bad_layout
    moveq #0,d0
    move.w (a0)+,d0
    swap d0
    addq.w #2,d5
    cmp.w (a0)+,d5
    bne.w p2l_bad_layout
    move.w (a0)+,d0
    addq.w #2,d5
    bsr.w p2l_in_private
    tst.l d0
    bne.w p2l_refs
    move.l (a1)+,d0
    bsr.w p2l_in_private
    tst.l d0
    bne.w p2l_refs
    dbra d1,p2l_scan
    move.l a2,d0
    cmp.l 38(a5),d0
    bne.w p2l_bad_layout
    cmp.l 208(a5),d2
    bne.w p2l_bad_layout
    tst.l 34(a5)
    bne.w p2l_not_idle
    lea 164(a2),a0
    move.l a0,d0
    cmp.l 50(a5),d0
    bne.w p2l_not_idle
    cmp.l 54(a5),d0
    bne.w p2l_not_idle
    moveq #1,d0
    rts
p2l_in_private:
    cmp.l d3,d0
    bcs.s p2l_check_record
    cmp.l d4,d0
    bcs.s p2l_is_private
p2l_check_record:
    cmp.l a3,d0
    bcs.s p2l_not_private
    cmp.l d6,d0
    bcs.s p2l_is_private
p2l_not_private:
    moveq #0,d0
    rts
p2l_is_private:
    moveq #1,d0
    rts
p2l_bad_gfx:
    move.l #-184,d0
    rts
p2l_not_idle:
    move.l #-185,d0
    rts
p2l_bad_layout:
    move.l #-186,d0
    rts
p2l_refs:
    move.l #-187,d0
    rts
p2l_gfx_name:
    dc.b "graphics.library",0
    even
