; AGA_NATIVE_MIN_CPU: MC68020
; S2b private allocation path, same named v4 borrow as registry core.
; PICK: A0 root, D0 new logical ID, D1 palette-compatible pair mask
; (bits 0..2 for 2/4/6), D2 OS reservation byte snapshot.
; Return D0 empty slot ptr, D1 even channel, or D0=0 D1=-1 invalid,
; -2 no pair, -3 pending registry. Snapshot is NOT ownership.
; INSERT: A0 root, A1 pinned detached P2a block, D0 ID, D1 bank,
; D2 image, D3 even channel, D4 ViewPort. Result record ptr or 0.
; ACQUIRE: A0 inserted private record, A1 live GfxBase. D0=1 for
; both receipts acquired (state7); 0 on refusal (D1=-141/-142/-143).
; Caller verifies bank/context and palette after acquisition, BEFORE
; publication. No ChangeSprite/MoveSprite, no FreeVec in this module.
; Preserve D2-D7/A0-A6 in all entries.
AGSP_S2B_PICK:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    move.l d1,d6
    move.l d2,d7
    cmpi.l #1,d0
    bcs.s s2b_pick_bad
    cmpi.l #7,d6
    bhi.s s2b_pick_bad
    cmpi.l #255,d7
    bhi.s s2b_pick_bad
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.s s2b_pick_bad
    tst.l d0
    bne.s s2b_pick_bad
    and.l d1,d6
    lea 52(a2),a3
    moveq #2,d5
s2b_pick_check:
    tst.l 28(a3)
    beq.s s2b_pick_check_next
    cmpi.l #15,12(a3)
    bne.s s2b_pick_pending
    tst.l 36(a3)
    beq.s s2b_pick_pending
s2b_pick_check_next:
    lea 44(a3),a3
    dbra d5,s2b_pick_check
    lea 52(a2),a3
    moveq #0,d5
    moveq #2,d4
s2b_pick_slot:
    btst d5,d6
    beq.s s2b_pick_next
    moveq #3,d0
    lsl.l d4,d0
    and.l d7,d0
    beq.s s2b_pick_ok
s2b_pick_next:
    addq.l #1,d5
    addq.l #2,d4
    lea 44(a3),a3
    cmpi.l #3,d5
    bcs.s s2b_pick_slot
    moveq #-2,d1
    bra.s s2b_pick_no
s2b_pick_bad:
    moveq #-1,d1
    bra.s s2b_pick_no
s2b_pick_pending:
    moveq #-3,d1
s2b_pick_no:
    moveq #0,d0
    bra.s s2b_pick_return
s2b_pick_ok:
    move.l a3,d0
    move.l d4,d1
s2b_pick_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

AGSP_S2B_INSERT:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    movea.l a1,a3
    move.l d0,d5
    move.l d1,d6
    move.l d3,d7
    cmpi.l #1,d5
    bcs.w s2b_insert_bad
    cmpi.l #5,d6
    bcs.w s2b_insert_bad
    cmpi.l #65535,d6
    bhi.w s2b_insert_bad
    cmpi.l #1,d2
    bcs.w s2b_insert_bad
    cmpi.l #4096,d2
    bhi.w s2b_insert_bad
    cmpi.l #2,d7
    beq.s s2b_insert_pair
    cmpi.l #4,d7
    beq.s s2b_insert_pair
    cmpi.l #6,d7
    bne.w s2b_insert_bad
s2b_insert_pair:
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.w s2b_insert_bad
    tst.l d0
    bne.w s2b_insert_bad
    move.l d7,d0
    lsr.l #1,d0
    subq.l #1,d0
    btst d0,d1
    beq.w s2b_insert_bad
    mulu.w #44,d0
    lea 52(a2,d0.l),a4
    ; Require caller's authenticated live lifetime before receipt.
    move.l 48(a2),d0
    beq.w s2b_insert_bad
    cmp.l 16(a2),d0
    bne.w s2b_insert_bad
    tst.l 4(a2)
    beq.w s2b_insert_bad
    tst.l 8(a2)
    beq.w s2b_insert_bad
    move.l 12(a2),d0
    beq.w s2b_insert_bad
    addi.l #44,d0
    bcs.w s2b_insert_bad
    cmp.l d4,d0
    bne.w s2b_insert_bad
    move.l a3,d0
    beq.w s2b_insert_bad
    btst #0,d0
    bne.w s2b_insert_bad
    ; P2a producer guarantees mapped private block and exact allocation.
    tst.l (a3)
    bne.w s2b_insert_bad
    tst.l 6(a3)
    bne.w s2b_insert_bad
    cmpi.w #-1,10(a3)
    bne.w s2b_insert_bad
    cmp.w 16(a3),d2
    bne.w s2b_insert_bad
    moveq #0,d0
    move.w 4(a3),d0
    beq.w s2b_insert_bad
    cmpi.w #256,d0
    bhi.w s2b_insert_bad
    lsl.l #2,d0
    addq.l #8,d0
    move.l d0,d1
    addi.l #48,d1
    cmpi.l #48,40(a3)
    bne.w s2b_insert_bad
    cmp.l 44(a3),d1
    bne.w s2b_insert_bad
    add.l d1,d0
    cmp.l 12(a3),d0
    bne.w s2b_insert_bad
    ; Publish the complete private receipt under the lock; no OS calls.
    ; SCAN below is a bounded read-only validation. Roll back the new
    ; receipt if its extent aliases any peer/anchor. No allocation freed.
    move.l a3,(a4)
    move.l d0,4(a4)
    move.l d4,8(a4)
    move.w 4(a3),20(a4)
    move.w #-1,26(a4)
    move.l d5,28(a4)
    move.l d6,32(a4)
    move.l d2,36(a4)
    move.l d7,40(a4)
    addq.l #1,(a2)
    movea.l a2,a0
    move.l d5,d0
    bsr.w AGSP_S2B_SCAN
    tst.l d1
    bmi.s s2b_insert_rollback
    cmp.l a4,d0
    beq.s s2b_insert_return
s2b_insert_rollback:
    movea.l a4,a0
    moveq #10,d0
s2b_insert_zero:
    clr.l (a0)+
    dbra d0,s2b_insert_zero
    subq.l #1,(a2)
s2b_insert_bad:
    moveq #0,d0
s2b_insert_return:
    moveq #0,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts

AGSP_S2B_ACQUIRE:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    movea.l a1,a5
    move.l #-143,d7
    tst.l 12(a3)
    bne.w s2b_acquire_no
    move.l 40(a3),d6
    cmpi.l #2,d6
    beq.s s2b_acquire_pair
    cmpi.l #4,d6
    beq.s s2b_acquire_pair
    cmpi.l #6,d6
    bne.w s2b_acquire_no
s2b_acquire_pair:
    movea.l (a3),a4
    move.l a4,d0
    beq.w s2b_acquire_no
    tst.l (a4)
    bne.w s2b_acquire_no
    cmpi.w #-1,10(a4)
    bne.w s2b_acquire_no
    tst.l 16(a3)
    bne.w s2b_acquire_no
    cmpi.w #-1,26(a3)
    bne.w s2b_acquire_no
    move.l a5,d0
    beq.w s2b_acquire_no
    btst #0,d0
    bne.w s2b_acquire_no
    cmpi.w #212,18(a5)
    bcs.w s2b_acquire_no
    cmpi.w #39,20(a5)
    bcs.w s2b_acquire_no
    cmpi.w #40,20(a5)
    bhi.w s2b_acquire_no
    movea.l a5,a6
    movea.l a4,a0
    move.l d6,d0
    jsr -408(a6)
    cmp.w d6,d0
    beq.s s2b_acquire_even
    cmpi.w #-1,d0
    bne.s s2b_acquire_quarantine
    move.l #-141,d7
    bra.s s2b_acquire_no
s2b_acquire_even:
    moveq #5,d0
    move.l d0,12(a3)
    cmp.w 10(a4),d6
    bne.s s2b_acquire_quarantine
    lea 16(a3),a0
    move.l d6,d0
    addq.l #1,d0
    jsr -408(a6)
    move.l d6,d1
    addq.l #1,d1
    cmp.w d1,d0
    beq.s s2b_acquire_odd
    cmpi.w #-1,d0
    bne.s s2b_acquire_quarantine
    ; Only the exact even receipt is ours. Pair retire handles rollback.
    movea.l a3,a0
    movea.l a5,a1
    bsr.w AGSP_S2B_RETIRE_PAIR
    move.l #-142,d7
    bra.s s2b_acquire_no
s2b_acquire_odd:
    moveq #7,d0
    move.l d0,12(a3)
    cmp.w 26(a3),d1
    bne.s s2b_acquire_quarantine
    moveq #1,d0
    moveq #0,d1
    bra.s s2b_acquire_return
s2b_acquire_quarantine:
    ori.l #$80000004,12(a3)
s2b_acquire_no:
    moveq #0,d0
    move.l d7,d1
s2b_acquire_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

; A0 prepared/live Chip block, A1 verified ColorMap, A2 verified GfxBase.
; Return D0 bits 0..2 for exact RGB match in groups 21..23,25..27,29..31.
; D1=1 mode/tags valid; 0 refusal. No SET tags or palette writes.
; Same V39/V40 VideoControl GET contract as p2i_palette.
AGSP_S2B_PALETTE_MASK:
    movem.l d2-d7/a0-a6,-(sp)
    lea -40(sp),sp
    movea.l a0,a3
    movea.l a1,a5
    movea.l a2,a6
    movea.l sp,a4
    moveq #0,d6
    moveq #0,d7
    move.l #$80000028,(a4)
    move.l #$6a5a5a5a,4(a4)
    move.l #$80000029,8(a4)
    move.l #$6a5a5a5a,12(a4)
    move.l #$80000032,16(a4)
    move.l #$6a5a5a5a,20(a4)
    move.l #$80000034,24(a4)
    move.l #$6a5a5a5a,28(a4)
    clr.l 32(a4)
    clr.l 36(a4)
    movea.l a5,a0
    movea.l a4,a1
    jsr -708(a6)
    tst.l d0
    bne.s s2b_palette_return
    cmpi.l #16,4(a4)
    bne.s s2b_palette_return
    cmpi.l #16,12(a4)
    bne.s s2b_palette_return
    cmpi.l #255,20(a4)
    bne.s s2b_palette_return
    cmpi.l #4,28(a4)
    bne.s s2b_palette_return
    cmpi.b #1,18(a5)
    bne.s s2b_palette_return
    moveq #1,d7
    moveq #21,d5
    moveq #0,d4
s2b_palette_group:
    movea.l a5,a0
    movea.l a4,a1
    move.l d5,d0
    moveq #3,d1
    jsr -900(a6)
    movea.l a4,a0
    lea 31(a3),a1
    moveq #8,d2
s2b_palette_rgb:
    move.b (a0),d0
    cmp.b (a1)+,d0
    bne.s s2b_palette_next
    adda.w #4,a0
    dbra d2,s2b_palette_rgb
    bset d4,d6
s2b_palette_next:
    addq.l #4,d5
    addq.l #1,d4
    cmpi.l #3,d4
    bcs.s s2b_palette_group
s2b_palette_return:
    move.l d6,d0
    move.l d7,d1
    lea 40(sp),sp
    movem.l (sp)+,d2-d7/a0-a6
    rts
