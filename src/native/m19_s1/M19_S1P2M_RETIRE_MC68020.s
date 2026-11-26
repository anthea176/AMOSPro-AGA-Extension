; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2m: source-backed OS-owned SimpleSprite lifetime, V39/V40.
; FreeSprite clears the owned slot and replaces copinit startup pointer.
; Check only the released pair, not ActiView/LOF/SHF/wait_forever.
; D0=2 private, 1 retired and detached by the S1 protocol, 0 pending/refused.
; Flags 4 = receipts released, fence pending; 20 = fence completed.
; GetSprite alone stores the channel number, not a descriptor in the table.
; No custom Copper writes, no hardware DMA register writes, no stale VP calls.
; Pinned private record and live graphics base are supplied by registry owner.
AGSP_P2E_RETIRE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    move.l a3,d0
    beq.w p2e_bad_record
    btst #0,d0
    bne.w p2e_bad_record
    move.l (a3),d3
    beq.w p2e_bad_record
    btst #0,d3
    bne.w p2e_bad_record
    move.l 4(a3),d4
    cmpi.l #72,d4
    bcs.w p2e_bad_record
    cmpi.l #2112,d4
    bhi.w p2e_bad_record
    add.l d3,d4
    bcs.w p2e_bad_record
    movea.l d3,a4
    moveq #0,d0
    move.w 4(a4),d0
    beq.w p2e_bad_record
    cmpi.w #256,d0
    bhi.w p2e_bad_record
    lsl.l #2,d0
    addq.l #8,d0
    move.l d0,d5
    addi.l #48,d5
    cmpi.l #48,40(a4)
    bne.w p2e_bad_record
    cmp.l 44(a4),d5
    bne.w p2e_bad_record
    add.l d5,d0
    cmp.l 4(a3),d0
    bne.w p2e_bad_record
    cmp.l 12(a4),d0
    bne.w p2e_bad_record
    move.l 12(a3),d2
    beq.w p2e_private
    cmpi.l #20,d2
    beq.w p2j_retired
    cmpi.l #4,d2
    beq.w p2e_validate_gfx
    cmpi.l #5,d2
    beq.w p2e_validate_gfx
    cmpi.l #7,d2
    beq.w p2e_validate_gfx
    cmpi.l #13,d2
    beq.w p2e_validate_gfx
    cmpi.l #15,d2
    bne.w p2e_bad_flags
p2e_validate_gfx:
    move.l a5,d0
    beq.w p2e_bad_gfx
    btst #0,d0
    bne.w p2e_bad_gfx
    cmpi.w #212,18(a5)
    bcs.w p2e_bad_gfx
    cmpi.w #39,20(a5)
    bcs.w p2e_bad_gfx
    cmpi.w #40,20(a5)
    bhi.w p2e_bad_gfx
    movea.l a5,a6
    cmpi.l #4,d2
    beq.w p2m_fence
    move.l d2,d7         ; snapshot before receipts are cleared
    ; Verify reservation bits as corroboration, never infer ownership
    ; from them. d2 has our previously recorded GetSprite receipts.
    move.l d2,d0
    andi.l #3,d0
    lsl.l #2,d0
    moveq #0,d1
    move.b 166(a5),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w p2e_bad_owner
    cmpi.w #2,10(a4)
    bne.w p2e_bad_owner
    btst #1,d2
    beq.w p2j_guard_ok
    cmpi.w #3,26(a3)
    bne.w p2e_bad_owner
p2j_guard_ok:
    ; FreeSprite is the documented OS release, and installs its own
    ; neutral data. Do not republish a private blank or touch the old VP.
p2j_release:
    btst #1,d2
    beq.w p2j_release_two
    moveq #3,d0
    jsr -414(a6)
    andi.l #$fffffffd,d2
    move.l d2,12(a3)
p2j_release_two:
    btst #0,d2
    beq.w p2j_release_done
    moveq #2,d0
    jsr -414(a6)
    andi.l #$fffffff6,d2
    move.l d2,12(a3)
p2j_release_done:
    ; Without ChangeSprite/MoveSprite, GetSprite only reserved channels.
    ; No private data was published to the DMA or SimpleSprites table.
    btst #3,d7
    beq.s p2m_confirm
p2m_fence:
    move.l 38(a5),d3
    move.l 208(a5),d4
    bsr.w p2m_neutral
    tst.l d0
    beq.w p2e_bad_owner
    jsr -270(a6)          ; two full frame boundaries, task context
    jsr -270(a6)
    bsr.w p2m_neutral
    tst.l d0
    beq.w p2e_bad_owner
p2m_confirm:
    move.l #20,12(a3)    ; no further publication allowed by this record
p2j_retired:
    moveq #1,d0
    moveq #0,d1
    bra.w p2e_return
p2e_private:
    moveq #2,d0
    moveq #0,d1
    bra.w p2e_return
p2e_bad_record:
    moveq #1,d1
    bra.w p2e_refuse
p2e_bad_gfx:
    moveq #2,d1
    bra.w p2e_refuse
p2e_bad_flags:
    moveq #3,d1
    bra.w p2e_refuse
p2e_bad_owner:
    moveq #5,d1
    bra.w p2e_refuse
p2e_refuse:
    moveq #0,d0
p2e_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; Check source-proven V39/V40 private layout, with mapped endpoints.
; D3=copinit base, D4=SimpleSprites base, A5/A6=live GfxBase.
; Only the channels we published/reserved are examined. No WAIT magic.
p2m_neutral:
    cmp.l 38(a5),d3
    bne.w p2m_bad
    cmp.l 208(a5),d4
    bne.w p2m_bad
    movea.l d4,a0
    moveq #15,d0
    bsr.w p2m_span
    tst.l d0
    beq.w p2m_bad
    tst.l 8(a0)
    bne.s p2m_bad
    tst.l 12(a0)
    bne.s p2m_bad
    move.b 166(a5),d0
    andi.b #12,d0
    bne.s p2m_bad
    movea.l d3,a0
    move.l #191,d0
    bsr.w p2m_span
    tst.l d0
    beq.s p2m_bad
    cmpi.w #$128,104(a0)
    bne.s p2m_bad
    cmpi.w #$12a,108(a0)
    bne.s p2m_bad
    cmpi.w #$12c,112(a0)
    bne.s p2m_bad
    cmpi.w #$12e,116(a0)
    bne.s p2m_bad
    lea 176(a0),a1
    move.l a1,d0
    cmp.w 110(a0),d0
    bne.s p2m_bad
    cmp.w 118(a0),d0
    bne.s p2m_bad
    swap d0
    cmp.w 106(a0),d0
    bne.s p2m_bad
    cmp.w 114(a0),d0
    bne.s p2m_bad
    cmp.l 38(a5),d3
    bne.s p2m_bad
    cmp.l 208(a5),d4
    bne.s p2m_bad
    moveq #1,d0
    rts
p2m_bad:
    moveq #0,d0
    rts
; A0 pinned OS object, D0 last-byte offset. TypeOfMem is a mapping
; corroboration, not a general-purpose allocation size certificate.
p2m_span:
    move.l a0,d1
    beq.s p2m_bad
    btst #0,d1
    bne.s p2m_bad
    add.l d0,d1
    bcs.s p2m_bad
    movem.l a0/a6,-(sp)
    movea.l $0004.w,a6
    movea.l d1,a1
    jsr -534(a6)
    tst.l d0
    beq.s p2m_span_end
    movea.l (sp),a1
    jsr -534(a6)
p2m_span_end:
    movem.l (sp)+,a0/a6
    rts
