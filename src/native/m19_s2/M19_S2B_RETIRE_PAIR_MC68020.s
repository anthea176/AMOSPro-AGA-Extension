; AGA_NATIVE_MIN_CPU: MC68020
; S2b component: retire one independently owned SimpleSprite pair.
; Source-derived from S1-P2m RETIRE; preserve the proven receipt states.
; A0=pinned 44-byte record (P2m prefix + immutable even channel LONG at 40)
; A1=live graphics.library V39/V40; caller holds exclusive owner borrow.
; D0=2 private, 1 detached, 0 refused/pending; D1=reason (P2m codes).
; D2-D7/A0-A6 preserved. No allocation or FreeVec, no user Copper writes.
; Only even 2/4/6 allowed. Odd is a reservation guard, never displayed.
; For published records, only that pair must be neutral before/after 2 WaitTOF.
; Root, lookup, acquisition, and Close/End multi-record iteration are not here.
AGSP_S2B_RETIRE_PAIR:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    move.l a3,d0
    beq.w s2b_p2e_bad_record
    btst #0,d0
    bne.w s2b_p2e_bad_record
    move.l 40(a3),d6
    cmpi.l #2,d6
    beq.s s2b_pair_ok
    cmpi.l #4,d6
    beq.s s2b_pair_ok
    cmpi.l #6,d6
    bne.w s2b_p2e_bad_record
s2b_pair_ok:
    move.l (a3),d3
    beq.w s2b_p2e_bad_record
    btst #0,d3
    bne.w s2b_p2e_bad_record
    move.l 4(a3),d4
    cmpi.l #72,d4
    bcs.w s2b_p2e_bad_record
    cmpi.l #2112,d4
    bhi.w s2b_p2e_bad_record
    add.l d3,d4
    bcs.w s2b_p2e_bad_record
    movea.l d3,a4
    moveq #0,d0
    move.w 4(a4),d0
    beq.w s2b_p2e_bad_record
    cmpi.w #256,d0
    bhi.w s2b_p2e_bad_record
    lsl.l #2,d0
    addq.l #8,d0
    move.l d0,d5
    addi.l #48,d5
    cmpi.l #48,40(a4)
    bne.w s2b_p2e_bad_record
    cmp.l 44(a4),d5
    bne.w s2b_p2e_bad_record
    add.l d5,d0
    cmp.l 4(a3),d0
    bne.w s2b_p2e_bad_record
    cmp.l 12(a4),d0
    bne.w s2b_p2e_bad_record
    move.l 12(a3),d2
    beq.w s2b_p2e_private
    cmpi.l #20,d2
    beq.w s2b_p2j_retired
    cmpi.l #4,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #5,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #7,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #13,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #15,d2
    bne.w s2b_p2e_bad_flags
s2b_p2e_validate_gfx:
    move.l a5,d0
    beq.w s2b_p2e_bad_gfx
    btst #0,d0
    bne.w s2b_p2e_bad_gfx
    cmpi.w #212,18(a5)
    bcs.w s2b_p2e_bad_gfx
    cmpi.w #39,20(a5)
    bcs.w s2b_p2e_bad_gfx
    cmpi.w #40,20(a5)
    bhi.w s2b_p2e_bad_gfx
    movea.l a5,a6
    cmpi.l #4,d2
    beq.w s2b_p2m_fence
    move.l d2,d7         ; snapshot before receipts are cleared
    ; Verify reservation bits as corroboration, never infer ownership
    ; from them. d2 has our previously recorded GetSprite receipts.
    move.l d2,d0
    andi.l #3,d0
    lsl.l d6,d0
    moveq #0,d1
    move.b 166(a5),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w s2b_p2e_bad_owner
    cmp.w 10(a4),d6
    bne.w s2b_p2e_bad_owner
    btst #1,d2
    beq.s s2b_guard_number_ok
    move.l d6,d0
    addq.l #1,d0
    cmp.w 26(a3),d0
    bne.w s2b_p2e_bad_owner
s2b_guard_number_ok:
    ; Corroborate exact SimpleSprite entries before freeing any receipt.
    ; Zero is permitted for an unpublished or not-yet-moved even slot.
    ; Never free another descriptor, even if the reservation bit is set.
    movea.l 208(a5),a0
    moveq #31,d0
    bsr.w s2b_p2m_span
    tst.l d0
    beq.w s2b_p2e_bad_owner
    move.l d6,d0
    lsl.l #2,d0
    adda.l d0,a0
    move.l (a0),d0
    beq.s s2b_even_entry_ok
    btst #3,d2
    beq.w s2b_p2e_bad_owner
    cmp.l a4,d0
    bne.w s2b_p2e_bad_owner
s2b_even_entry_ok:
    btst #1,d2
    beq.s s2b_p2j_guard_ok
    tst.l 4(a0)
    bne.w s2b_p2e_bad_owner
s2b_p2j_guard_ok:
    ; FreeSprite is the documented OS release, and installs its own
    ; neutral data. Do not republish a private blank or touch the old VP.
s2b_p2j_release:
    btst #1,d2
    beq.s s2b_p2j_release_two
    move.l d6,d0
    addq.l #1,d0
    jsr -414(a6)
    andi.l #$fffffffd,d2
    move.l d2,12(a3)
s2b_p2j_release_two:
    btst #0,d2
    beq.s s2b_p2j_release_done
    move.l d6,d0
    jsr -414(a6)
    andi.l #$fffffff6,d2
    move.l d2,12(a3)
s2b_p2j_release_done:
    ; Without ChangeSprite/MoveSprite, GetSprite only reserved channels.
    ; No private data was published to the DMA or SimpleSprites table.
    btst #3,d7
    beq.s s2b_p2m_confirm
s2b_p2m_fence:
    move.l 38(a5),d3
    move.l 208(a5),d4
    bsr.w s2b_p2m_neutral
    tst.l d0
    beq.w s2b_p2e_bad_owner
    jsr -270(a6)          ; two full frame boundaries, task context
    jsr -270(a6)
    bsr.w s2b_p2m_neutral
    tst.l d0
    beq.w s2b_p2e_bad_owner
s2b_p2m_confirm:
    move.l #20,12(a3)    ; no further publication allowed by this record
s2b_p2j_retired:
    moveq #1,d0
    moveq #0,d1
    bra.s s2b_p2e_return
s2b_p2e_private:
    moveq #2,d0
    moveq #0,d1
    bra.s s2b_p2e_return
s2b_p2e_bad_record:
    moveq #1,d1
    bra.s s2b_p2e_refuse
s2b_p2e_bad_gfx:
    moveq #2,d1
    bra.s s2b_p2e_refuse
s2b_p2e_bad_flags:
    moveq #3,d1
    bra.s s2b_p2e_refuse
s2b_p2e_bad_owner:
    moveq #5,d1
    bra.w s2b_p2e_refuse
s2b_p2e_refuse:
    moveq #0,d0
s2b_p2e_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Check source-proven V39/V40 private layout for the recorded pair.
; D3=copinit base, D4=SimpleSprites base, A5/A6=live GfxBase.
; Only the channels we published/reserved are examined. No WAIT magic.
s2b_p2m_neutral:
    cmp.l 38(a5),d3
    bne.w s2b_p2m_bad
    cmp.l 208(a5),d4
    bne.w s2b_p2m_bad
    movea.l d4,a0
    moveq #31,d0
    bsr.w s2b_p2m_span
    tst.l d0
    beq.w s2b_p2m_bad
    move.l d6,d0
    lsl.l #2,d0
    adda.l d0,a0
    tst.l (a0)
    bne.w s2b_p2m_bad
    tst.l 4(a0)
    bne.w s2b_p2m_bad
    moveq #3,d0
    lsl.l d6,d0
    and.b 166(a5),d0
    bne.w s2b_p2m_bad
    movea.l d3,a0
    move.l #191,d0
    bsr.w s2b_p2m_span
    tst.l d0
    beq.w s2b_p2m_bad
    ; V40 copinit_sprstrtup starts at +88, 8 bytes per channel.
    ; Each pair is 16 bytes: SPRxPTH/PTL then SPR(x+1)PTH/PTL.
    lea 176(a0),a1
    move.l d6,d0
    lsl.l #3,d0
    lea 88(a0,d0.l),a0
    move.l d6,d1
    lsl.l #2,d1
    addi.w #$120,d1
    cmp.w (a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 8(a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 12(a0),d1
    bne.s s2b_p2m_bad
    move.l a1,d0
    cmp.w 6(a0),d0
    bne.s s2b_p2m_bad
    cmp.w 14(a0),d0
    bne.s s2b_p2m_bad
    swap d0
    cmp.w 2(a0),d0
    bne.s s2b_p2m_bad
    cmp.w 10(a0),d0
    bne.s s2b_p2m_bad
    cmp.l 38(a5),d3
    bne.s s2b_p2m_bad
    cmp.l 208(a5),d4
    bne.s s2b_p2m_bad
    moveq #1,d0
    rts
s2b_p2m_bad:
    moveq #0,d0
    rts
; A0 pinned OS object, D0 last-byte offset. TypeOfMem is a mapping
; corroboration, not a general-purpose allocation size certificate.
s2b_p2m_span:
    move.l a0,d1
    beq.s s2b_p2m_bad
    btst #0,d1
    bne.s s2b_p2m_bad
    add.l d0,d1
    bcs.s s2b_p2m_bad
    movem.l a0/a6,-(sp)
    movea.l $0004.w,a6
    movea.l d1,a1
    jsr -534(a6)
    tst.l d0
    beq.s s2b_p2m_span_end
    movea.l (sp),a1
    jsr -534(a6)
s2b_p2m_span_end:
    movem.l (sp)+,a0/a6
    rts
