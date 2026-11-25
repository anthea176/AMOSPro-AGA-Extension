; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2e source-only: logical retirement of S1 SimpleSprite pair 2/3.
; NOT a DMA-free certificate, NOT an AP20 command, never FreeVec.
; Task context, interrupts enabled, serialized by owner. Caller pins A0
; record (28 bytes), A1 live graphics.library V39/V40 and its system
; structures. No external FreeSprite or reuse of this record is allowed.
; A0+0 P2a private Chip block, +4 exact allocation length, +8 live VP
; (required only for published sprite), +12 flags.L, +16 guard descriptor
; (12 bytes, never published). Block is prevalidated, owned and stable.
; Flags: 1 own channel 2, 2 own channel 3, 4 ever exposed (sticky),
; 8 publication attempted on 2. Set receipt immediately on acquisition,
; bit 3 BEFORE ChangeSprite. Only this owner may release these channels.
; Supported states: 0,4,5,7,13,15. No flags invented from OS mask.
; D0=2 never exposed; 1 no owned channel / no sampled private references;
; 0 rejected or pending. D1 reason 0 success, 1 invalid record/block,
; 2 invalid gfx, 3 invalid flags, 4 invalid Copper/table layout,
; 5 ownership/publication mismatch, 6 blank not confirmed, 7 refs retained.
; D2-D7/A0-A6 preserved. Flags cleared immediately after each FreeSprite.
; Status 1 NEVER permits freeing exposed Chip by itself.
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
    add.l d3,d5
    move.l 12(a3),d2
    beq.w p2e_private
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
    bsr.w p2e_scan
    tst.l d0
    bmi.w p2e_bad_layout
    cmpi.l #4,d2
    beq.w p2e_post_release
    bsr.w p2e_owned
    tst.l d0
    beq.w p2e_bad_owner
    btst #3,d2
    beq.w p2e_release
    ; Published: only call ChangeSprite with the original live VP.
    move.l 8(a3),d0
    beq.w p2e_bad_owner
    btst #0,d0
    bne.w p2e_bad_owner
    move.l (a4),d0
    cmp.l d5,d0
    beq.w p2e_check_live
    move.l d3,d1
    addi.l #48,d1
    cmp.l d1,d0
    bne.w p2e_bad_owner
p2e_check_live:
    bsr.w p2e_cop2_equals
    tst.l d0
    beq.w p2e_bad_owner
    movea.l 8(a3),a0
    movea.l a4,a1
    movea.l d5,a2
    jsr -420(a6)          ; ChangeSprite(VP,SimpleSprite,blank)
    bsr.w p2e_wait_two
    bsr.w p2e_scan
    tst.l d0
    bmi.w p2e_bad_layout
    bsr.w p2e_owned
    tst.l d0
    beq.w p2e_bad_owner
    cmp.l (a4),d5
    bne.w p2e_blank_failed
    move.l d5,d0
    bsr.w p2e_cop2_equals
    tst.l d0
    beq.w p2e_blank_failed
p2e_release:
    ; Never free a channel merely because its OS bit is set.
    ; Guard first, then actual sprite (same order as P2d r2).
    btst #1,d2
    beq.w p2e_release_two
    moveq #3,d0
    jsr -414(a6)          ; FreeSprite(3)
    andi.l #$fffffffd,d2
    move.l d2,12(a3)
p2e_release_two:
    btst #0,d2
    beq.w p2e_post_release
    moveq #2,d0
    jsr -414(a6)          ; FreeSprite(2)
    andi.l #$fffffff6,d2  ; clear ownership 2 and published; keep exposure
    move.l d2,12(a3)
p2e_post_release:
    ; Already retired/retry: no ViewPort dereference or repeated FreeSprite.
    bsr.w p2e_wait_two
    bsr.w p2e_scan
    tst.l d0
    bmi.w p2e_bad_layout
    bne.w p2e_refs_pending
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
p2e_bad_layout:
    moveq #4,d1
    bra.w p2e_refuse
p2e_bad_owner:
    moveq #5,d1
    bra.w p2e_refuse
p2e_blank_failed:
    moveq #6,d1
    bra.w p2e_refuse
p2e_refs_pending:
    moveq #7,d1
p2e_refuse:
    moveq #0,d0
p2e_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

p2e_wait_two:
    ; WaitTOF: task context, no Forbid/Disable, bounded number of calls.
    jsr -270(a6)
    jsr -270(a6)
    rts

p2e_owned:
    move.l d2,d0
    andi.l #3,d0
    lsl.l #2,d0
    moveq #0,d1
    move.b 166(a5),d1
    and.l d0,d1
    cmp.l d0,d1
    bne.w p2e_owned_no
    ; p2e_scan checked the table and the caller pins its lifetime.
    movea.l 208(a5),a0
    cmpi.w #2,10(a4)
    bne.w p2e_owned_no
    btst #3,d2
    beq.w p2e_owned_unpublished
    cmp.l 8(a0),d3
    bne.w p2e_owned_no
    bra.w p2e_owned_guard
p2e_owned_unpublished:
    tst.l 8(a0)
    bne.w p2e_owned_no
    ; No ChangeSprite yet, the descriptor must not point at DMA data.
    tst.l (a4)
    bne.w p2e_owned_no
p2e_owned_guard:
    btst #1,d2
    beq.w p2e_owned_yes
    cmpi.w #3,26(a3)
    bne.w p2e_owned_no
    tst.l 12(a0)          ; reserved guard does not have a published desc
    bne.w p2e_owned_no
p2e_owned_yes:
    moveq #1,d0
    rts
p2e_owned_no:
    moveq #0,d0
    rts

p2e_cop2_equals:
    ; copinit.sprstrtup+2*8: two MOVE values at +106 and +110.
    ; The whole layout was checked by p2e_scan before this call.
    movea.l 38(a5),a0
    moveq #0,d1
    move.w 106(a0),d1
    swap d1
    move.w 110(a0),d1
    cmp.l d0,d1
    bne.w p2e_cop2_no
    moveq #1,d0
    rts
p2e_cop2_no:
    moveq #0,d0
    rts

p2e_scan:
    ; A5 pinned GfxBase; D3..D4 allocation range; A3 private record.
    ; NDK V39/V40: copinit +38, SimpleSprites +208, 16 MOVE pairs
    ; at copinit+88. Trust the live OS structure, not fixed low address.
    ; No walk of dynamic LOF/SHF lists or hardware reads.
    ; D0=-1 invalid, else number of sampled references. D1 volatile.
    movem.l d2-d7/a2,-(sp)
    movea.l 38(a5),a0
    move.l a0,d6
    beq.w p2e_scan_bad
    btst #0,d6
    bne.w p2e_scan_bad
    addi.l #152,d6
    bcs.w p2e_scan_bad
    movea.l 208(a5),a1
    move.l a1,d6
    beq.w p2e_scan_bad
    btst #0,d6
    bne.w p2e_scan_bad
    addi.l #32,d6
    bcs.w p2e_scan_bad
    lea 88(a0),a0
    move.l a3,d7
    addi.l #16,d7         ; guard descriptor address
    moveq #0,d0
    moveq #7,d1
    move.w #$120,d5
p2e_scan_loop:
    cmp.w (a0)+,d5
    bne.w p2e_scan_bad
    moveq #0,d6
    move.w (a0)+,d6
    swap d6
    addq.w #2,d5
    cmp.w (a0)+,d5
    bne.w p2e_scan_bad
    move.w (a0)+,d6
    addq.w #2,d5
    cmp.l d3,d6
    bcs.w p2e_scan_desc
    cmp.l d4,d6
    bcc.w p2e_scan_desc
    addq.l #1,d0
p2e_scan_desc:
    move.l (a1)+,d6
    cmp.l d7,d6
    beq.w p2e_scan_add
    cmp.l d3,d6
    bcs.w p2e_scan_next
    cmp.l d4,d6
    bcc.w p2e_scan_next
p2e_scan_add:
    addq.l #1,d0
p2e_scan_next:
    dbra d1,p2e_scan_loop
    ; Reject a changed table/list base. Not a global atomic snapshot.
    move.l a0,d6
    subi.l #152,d6
    cmp.l 38(a5),d6
    bne.w p2e_scan_bad
    move.l a1,d6
    subi.l #32,d6
    cmp.l 208(a5),d6
    bne.w p2e_scan_bad
    bra.w p2e_scan_return
p2e_scan_bad:
    moveq #-1,d0
p2e_scan_return:
    movem.l (sp)+,d2-d7/a2
    rts
