; AGA_NATIVE_MIN_CPU: MC68020
; S2a public frame transition, included in source-built UNIT207.
; A2 = public stack frame, A5 = AMOS Main, live owner borrow held.
; Use the S2b 44-byte inline record, one descriptor and both Chip slots.
; Never rewrite the displayed slot; never free an exposed allocation.
; OS references are corroboration under the private owner contract,
; not proof of arbitrary hardware DMA safety or foreign Copper writes.
; Before publication failure: preserve current image. After attempted
; publication failure: invalidate image ID, use P2m retirement, quarantine
; if retirement refuses. Off/Close/End keep all other registry records.
s2a_change:
    clr.l S_SCRATCH(a2)
    move.l #-200,I_PHASE(a2)
    bsr.w p2i_active
    tst.l d0
    beq.w p2i_end
    move.l #-128,I_PHASE(a2)
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_end
    move.l #-201,I_PHASE(a2)
    bsr.w s2a_bank
    tst.l d0
    beq.w p2i_end
    movea.l I_CHIP(a2),a0
    move.l I_SNAPSHOT+16(a2),d0
    cmp.l 20(a0),d0
    bne.w p2i_end
    bsr.w s2a_expect
    tst.l d0
    beq.w p2i_end
    move.l #-202,I_PHASE(a2)
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    bsr.w AGSP_P2A_PREPARE
    tst.l d0
    beq.w p2i_end
    move.l d0,S_SCRATCH(a2)
    move.l d1,S_LENGTH(a2)
    move.l #-201,I_PHASE(a2)
    bsr.w s2a_expect
    tst.l d0
    beq.w s2a_abort
    move.l #-203,I_PHASE(a2)
    bsr.w s2a_slots
    tst.l d0
    beq.w s2a_abort
    move.l #-204,I_PHASE(a2)
    move.l S_OLD(a2),d0
    move.l S_NEW(a2),d1
    eor.l d1,d0
    andi.l #$ffff0000,d0
    bne.w s2a_abort       ; no hybrid 32-bit pointer across the OS word writes
    move.l #-203,I_PHASE(a2)
    movea.l I_GFX(a2),a6
    move.l 34(a6),S_VIEW(a2)
    move.l 38(a6),S_CI(a2)
    move.l 50(a6),S_LOF(a2)
    move.l 54(a6),S_SHF(a2)
    move.l 208(a6),S_TABLE(a2)
    move.l S_OLD(a2),d7
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_abort
    ; Two complete frame boundaries after the last active reference.
    ; The locked owner never changes a frame or releases channels here.
    jsr -270(a6)
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_abort
    jsr -270(a6)
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_abort
    move.l #-201,I_PHASE(a2)
    bsr.w s2a_expect
    tst.l d0
    beq.w s2a_abort
    move.l #-203,I_PHASE(a2)
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_abort
    move.l #-202,I_PHASE(a2)
    movea.l I_CHIP(a2),a0
    move.l I_LEN(a2),d0
    movea.l S_SCRATCH(a2),a1
    move.l S_LENGTH(a2),d1
    move.l S_NEW(a2),d2
    bsr.w AGSP_S2A_STAGE
    cmp.l S_NEW(a2),d0
    bne.w s2a_abort
    bsr.w s2a_free_scratch
    move.l #-203,I_PHASE(a2)
    move.l S_OLD(a2),d7
    bsr.w s2a_refs
    tst.l d0
    beq.w p2i_end
    ; All fallible preparation is complete. ChangeSprite has no BOOL.
    ; V40 writes ss_posctldata then calls MoveSprite at current X/Y.
    move.l #-205,I_PHASE(a2)
    movea.l I_GFX(a2),a6
    movea.l I_VP(a2),a0
    movea.l I_CHIP(a2),a1
    movea.l S_NEW(a2),a2
    jsr -420(a6)
    movea.l sp,a2        ; A2 was an argument, not the public frame
    move.l S_NEW(a2),d7
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_publish_failed
    movea.l I_VP(a2),a0
    movea.l I_CHIP(a2),a1
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    jsr -426(a6)
    bsr.w s2a_refs
    tst.l d0
    beq.w s2a_publish_failed
    movea.l I_CHIP(a2),a0
    move.l I_X(a2),d0
    cmp.w 6(a0),d0
    bne.w s2a_publish_failed
    move.l I_Y(a2),d0
    cmp.w 8(a0),d0
    bne.w s2a_publish_failed
    ; Commit metadata only after publication and move corroboration.
    move.l I_IMAGE(a2),d0
    move.w d0,16(a0)
    movea.l I_REC(a2),a4
    move.l d0,36(a4)
    bra.w p2i_success
s2a_publish_failed:
    ; ID 0 is internal only: no subsequent Move or Change on an
    ; uncertain active record. P2m retirement does not use image ID.
    movea.l I_REC(a2),a4
    clr.l 36(a4)
    bsr.w p2m_release_record
    bra.w p2i_end
s2a_abort:
    bsr.w s2a_free_scratch
    bra.w p2i_end
s2a_free_scratch:
    move.l S_SCRATCH(a2),d0
    beq.s s2a_scratch_done
    clr.l S_SCRATCH(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -690(a6)         ; only the separate, unpublished P2a scratch
s2a_scratch_done:
    rts

; Resolve exact live selected bank, not the old bank payload address.
s2a_bank:
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_no
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_no
    move.l a0,I_SNAPSHOT(a2)
    move.l 4(a4),d0
    movea.l I_REC(a2),a0
    cmp.l 32(a0),d0
    bne.w p2i_no
    cmpi.l #5,d0
    bcs.w p2i_no
    cmpi.l #65535,d0
    bhi.w p2i_no
    move.l d0,I_BANK(a2)
    move.l d0,I_SNAPSHOT+4(a2)
    dc.w $FE11,$F700,797
    move.l a0,I_SNAPSHOT+8(a2)
    move.l I_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w p2i_no
    move.l d1,I_SNAPSHOT+12(a2)
    move.l d2,I_SNAPSHOT+16(a2)
    move.l d3,I_SNAPSHOT+20(a2)
    moveq #1,d0
    rts
s2a_expect:
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_no
    move.l I_BANK(a2),d0
    cmp.l 4(a4),d0
    bne.w p2i_no
    move.l I_SNAPSHOT(a2),d0
    cmp.l 8(a4),d0
    bne.w p2i_no
    lea I_SNAPSHOT(a2),a0
    bra.w AGSP_I_EXPECT

; Trusted live allocation from pinned owner record, exact P2a extents.
s2a_slots:
    movea.l I_CHIP(a2),a0
    move.l I_LEN(a2),d0
    cmp.l 12(a0),d0
    bne.w p2i_no
    cmpi.l #48,40(a0)
    bne.w p2i_no
    moveq #0,d0
    move.w 4(a0),d0
    beq.w p2i_no
    cmpi.w #256,d0
    bhi.w p2i_no
    lsl.l #2,d0
    addq.l #8,d0
    move.l d0,d1
    addi.l #48,d1
    cmp.l 44(a0),d1
    bne.w p2i_no
    add.l d0,d1
    cmp.l I_LEN(a2),d1
    bne.w p2i_no
    lea 48(a0),a1
    move.l a1,d1
    add.l d0,d1
    bcs.w p2i_no
    move.l (a0),d0
    cmp.l a1,d0
    beq.s s2a_first
    cmp.l d1,d0
    bne.w p2i_no
    move.l d0,S_OLD(a2)
    move.l a1,S_NEW(a2)
    moveq #1,d0
    rts
s2a_first:
    move.l d0,S_OLD(a2)
    move.l d1,S_NEW(a2)
    moveq #1,d0
    rts

; Check the same OS snapshot before/after each WaitTOF and publication.
; D7 expected published data pointer. Read-only, no private pointer
; writes. No assumptions about the contents of dynamic LOF/SHF lists.
; V39/V40 GfxBase offsets and copinit layout already proved by P2m.
; Require the private viewport to be first in the current View; no
; user or Gels Sprite copper list on this viewport. NDK view.i layout.
s2a_refs:
    bsr.w s2a_context_now
    tst.l d0
    beq.w p2i_no
    ; Corroborate mapped Copper list starts without traversing them.
    ; A stable but invalid pointer is not an acceptable snapshot.
    movea.l S_LOF(a2),a0
    moveq #2,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    movea.l S_SHF(a2),a0
    moveq #2,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    movea.l S_VIEW(a2),a0
    moveq #18,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l I_VP(a2),d0
    cmp.l (a0),d0
    bne.w p2i_no
    movea.l I_VP(a2),a0
    moveq #40,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.w #$5000,32(a0)
    bne.w p2i_no
    tst.l 12(a0)          ; vp_SprIns (Gels sprite copper)
    bne.w p2i_no
    tst.l 20(a0)          ; vp_UCopIns
    bne.w p2i_no
    move.l I_CM(a2),d0
    cmp.l 4(a0),d0
    bne.w p2i_no
    movea.l I_REC(a2),a4
    cmpi.l #15,12(a4)
    bne.w p2i_no
    move.l I_VP(a2),d0
    cmp.l 8(a4),d0
    bne.w p2i_no
    move.l 40(a4),d6
    move.l d6,d0
    addq.l #1,d0
    cmp.w 26(a4),d0
    bne.w p2i_no
    tst.l 16(a4)
    bne.w p2i_no
    movea.l I_CHIP(a2),a1
    cmp.w 10(a1),d6
    bne.w p2i_no
    cmp.l (a1),d7
    bne.w p2i_no
    moveq #3,d0
    lsl.l d6,d0
    moveq #0,d1
    move.b 166(a6),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w p2i_no
    movea.l S_TABLE(a2),a0
    moveq #32,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l d6,d0
    lsl.l #2,d0
    adda.l d0,a0
    move.l I_CHIP(a2),d0
    cmp.l (a0),d0
    bne.w p2i_no
    tst.l 4(a0)
    bne.w p2i_no
    movea.l S_CI(a2),a0
    move.l #192,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    lea 176(a0),a1
    move.l d6,d0
    lsl.l #3,d0
    lea 88(a0,d0.l),a0
    move.l d6,d1
    lsl.l #2,d1
    addi.w #$120,d1
    cmp.w (a0),d1
    bne.w p2i_no
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.w p2i_no
    addq.w #2,d1
    cmp.w 8(a0),d1
    bne.w p2i_no
    addq.w #2,d1
    cmp.w 12(a0),d1
    bne.w p2i_no
    move.l d7,d0
    cmp.w 6(a0),d0
    bne.w p2i_no
    swap d0
    cmp.w 2(a0),d0
    bne.w p2i_no
    move.l a1,d0
    cmp.w 14(a0),d0
    bne.w p2i_no
    swap d0
    cmp.w 10(a0),d0
    bne.w p2i_no
    bra.w s2a_context_now

s2a_context_now:
    move.l 456(a5),d0
    cmp.l I_STATE(a2),d0
    bne.w p2i_no
    movea.l d0,a0
    move.l (a0),d0
    cmp.l I_SCREEN(a2),d0
    bne.w p2i_no
    move.l 8(a0),d0
    cmp.l I_GFX(a2),d0
    bne.w p2i_no
    movea.l d0,a6
    move.l S_VIEW(a2),d0
    beq.w p2i_no
    cmp.l 34(a6),d0
    bne.w p2i_no
    move.l S_CI(a2),d0
    cmp.l 38(a6),d0
    bne.w p2i_no
    move.l S_LOF(a2),d0
    beq.w p2i_no
    cmp.l 50(a6),d0
    bne.w p2i_no
    move.l S_SHF(a2),d0
    cmp.l 54(a6),d0
    bne.w p2i_no
    move.l S_TABLE(a2),d0
    cmp.l 208(a6),d0
    bne.w p2i_no
    moveq #1,d0
    rts
