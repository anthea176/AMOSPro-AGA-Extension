; AGA_NATIVE_MIN_CPU: MC68020
; P2j conservative retirement, derived from P2e's validated record ABI.
; ONLY release channels with our successful GetSprite receipts.
; Match P2b: blank through ChangeSprite, wait, release guard then image.
; Never free exposed memory, never require instantaneous private Copper
; or SimpleSprites table updates. No dynamic Copper writes or reads.
; Same P2e input/output ABI, D0=2 private, 1 retired, 0 refused/blank
; not confirmed. D1=reason. Flags=4 after release even if blank check
; failed; Close/End can then continue, with persistent quarantine.
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
    cmpi.l #4,d2
    beq.w p2j_retired
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
    moveq #1,d6
    btst #3,d2
    beq.w p2j_release
    move.l 8(a3),d0
    beq.w p2e_bad_owner
    btst #0,d0
    bne.w p2e_bad_owner
    movea.l d0,a0
    movea.l a4,a1
    movea.l d5,a2
    jsr -420(a6)
    jsr -270(a6)
    jsr -270(a6)
    jsr -270(a6)
    cmp.l (a4),d5
    beq.w p2j_release
    ; A failed observation is not permission to retain a channel forever
    ; or to free DMA data. Release our receipts and retain the block.
    moveq #0,d6
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
    jsr -270(a6)
    jsr -270(a6)
    tst.l d6
    beq.w p2j_blank_failed
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
p2j_blank_failed:
    moveq #6,d1
p2e_refuse:
    moveq #0,d0
p2e_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts
