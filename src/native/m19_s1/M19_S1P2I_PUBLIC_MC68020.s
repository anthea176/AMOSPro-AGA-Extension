; AGA_NATIVE_MIN_CPU: MC68020
; First integrated S1 candidate. One OS-owned Sprite pair 2/3, 16px,
; one immutable detached image per open screen. Numeric AMOS functions.
; Sprite(N,X,Y,I) repeats to move; Off(N) releases channels, same image
; can be shown again only after sampled detach, no allocation replacement.
; Bank Free(N) does not Erase AMOS bank. Palette is caller-owned:
; pens 21..23 must already match AGSP RGB24, no palette mutation here.
; No custom Copper list, PAL LowRes 320x256x256, zero hotspot, V39/V40.
; P2h anchor held by current Task across open sprite lifecycle; no code
; address is stored in persistent RAM. P2g reclaims after confirmed close.
; Generated P2I_CELL_DELTA is source-assembled offset from State in UNIT142.
    bra.w p2i_sprite
    bra.w p2i_off
    bra.w p2i_bank_free

I_ID equ 0
I_X equ 4
I_Y equ 8
I_IMAGE equ 12
I_ARGS equ 16
I_RESULT equ 20
I_STATE equ 24
I_CELL equ 28
I_SCREEN equ 32
I_VP equ 36
I_GFX equ 40
I_CM equ 44
I_ROOT equ 48
I_REC equ 52
I_CHIP equ 56
I_LEN equ 60
I_BANK equ 64
I_SNAPSHOT equ 68
I_TAG equ 92
I_FRAME equ 136

p2i_sprite:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_IMAGE(a2)
    move.l (a3)+,I_Y(a2)
    move.l (a3)+,I_X(a2)
    move.l (a3)+,I_ID(a2)
    move.l a3,I_ARGS(a2)
    bsr.w p2i_init
    tst.l d0
    beq.w p2i_end
    cmpi.l #1,I_IMAGE(a2)
    bcs.w p2i_end
    cmpi.l #4096,I_IMAGE(a2)
    bhi.w p2i_end
    cmpi.l #304,I_X(a2)
    bhi.w p2i_end
    cmpi.l #255,I_Y(a2)
    bhi.w p2i_end
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_display_mode
    tst.l d0
    beq.w p2i_end
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2i_new
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_ID(a2),d0
    cmp.l 28(a4),d0
    bne.w p2i_end
    move.l I_IMAGE(a2),d0
    cmp.l 36(a4),d0
    bne.w p2i_end
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    cmpi.l #15,12(a4)
    beq.w p2i_move
    cmpi.l #4,12(a4)
    bne.w p2i_end
    ; Re-show only the SAME immutable pixels after sampled logical detach.
    movea.l a4,a0
    movea.l I_GFX(a2),a1
    bsr.w AGSP_P2E_RETIRE
    cmpi.l #1,d0
    bne.w p2i_end
    bra.w p2i_acquire

p2i_new:
    ; Resolve the selected live AMOS bank; do not cache its payload.
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w p2i_end
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_end
    move.l a0,I_SNAPSHOT(a2)
    move.l 4(a4),d0
    cmpi.l #5,d0
    bcs.w p2i_end
    cmpi.l #65535,d0
    bhi.w p2i_end
    move.l d0,I_BANK(a2)
    move.l d0,I_SNAPSHOT+4(a2)
    dc.w $FE11,$F700,797
    move.l a0,I_SNAPSHOT+8(a2)
    move.l I_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w p2i_end
    move.l d1,I_SNAPSHOT+12(a2)
    move.l d2,I_SNAPSHOT+16(a2)
    move.l d3,I_SNAPSHOT+20(a2)
    ; A pending record from any earlier execution blocks new allocation.
    moveq #1,d0
    bsr.w p2h_enter
    tst.l d0
    beq.w p2i_end
    move.l d0,I_ROOT(a2)
    movea.l d0,a3
    move.l (a3),d0
    or.l 4(a3),d0
    or.l 8(a3),d0
    or.l 12(a3),d0
    bne.w p2i_leave_only
    movea.l $0004.w,a6
    moveq #40,d0
    move.l #$10001,d1
    jsr -684(a6)
    tst.l d0
    beq.w p2i_leave_only
    move.l d0,I_REC(a2)
    lea I_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w p2i_private_abort
    movea.l I_SNAPSHOT+8(a2),a0
    move.l I_SNAPSHOT+12(a2),d0
    move.l I_IMAGE(a2),d1
    bsr.w AGSP_P2A_PREPARE
    tst.l d0
    beq.w p2i_private_abort
    move.l d0,I_CHIP(a2)
    move.l d1,I_LEN(a2)
    lea I_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w p2i_private_abort
    move.l I_STATE(a2),d0
    cmp.l 456(a5),d0
    bne.w p2i_private_abort
    movea.l d0,a0
    move.l (a0),d0
    cmp.l I_SCREEN(a2),d0
    bne.w p2i_private_abort
    bsr.w p2i_geometry
    tst.l d0
    beq.w p2i_private_abort
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_private_abort
    movea.l I_REC(a2),a4
    move.l I_CHIP(a2),(a4)
    move.l I_LEN(a2),4(a4)
    move.l I_VP(a2),8(a4)
    move.l I_ID(a2),28(a4)
    move.l I_BANK(a2),32(a4)
    move.l I_IMAGE(a2),36(a4)
    movea.l I_ROOT(a2),a3
    move.l a5,4(a3)
    move.l I_STATE(a2),8(a3)
    move.l I_SCREEN(a2),12(a3)
    move.l a4,(a3)
    movea.l I_CELL(a2),a0
    move.l a3,(a0)           ; local live borrow link, publish LAST

p2i_acquire:
    movea.l I_REC(a2),a4
    movea.l I_CHIP(a2),a3
    clr.l (a3)
    clr.l 6(a3)
    move.w #$ffff,10(a3)
    clr.l 16(a4)
    move.w 4(a3),20(a4)
    clr.l 22(a4)
    move.w #$ffff,26(a4)
    movea.l I_GFX(a2),a6
    movea.l a3,a0
    moveq #2,d0
    jsr -408(a6)
    cmpi.w #2,d0
    beq.s p2i_got_two
    cmpi.w #-1,d0
    bne.w p2i_bad_receipt
    tst.l 12(a4)
    bne.w p2i_end           ; previously exposed, keep immutable block
    movea.l I_CELL(a2),a0
    clr.l (a0)
    movea.l I_ROOT(a2),a0
    clr.l (a0)
    clr.l 4(a0)
    clr.l 8(a0)
    clr.l 12(a0)
    bra.w p2i_private_abort
p2i_got_two:
    moveq #5,d0
    move.l d0,12(a4)       ; receipt and sticky exposure
    cmpi.w #2,10(a3)
    bne.w p2i_bad_receipt
    lea 16(a4),a0
    moveq #3,d0
    jsr -408(a6)
    cmpi.w #3,d0
    beq.s p2i_got_three
    cmpi.w #-1,d0
    bne.w p2i_bad_receipt
    bra.w p2i_retire_failed
p2i_got_three:
    moveq #7,d0
    move.l d0,12(a4)
    cmpi.w #3,26(a4)
    bne.w p2i_bad_receipt
    ; VideoControl after reservations, same measured contract as P2b.
    bsr.w p2i_palette
    tst.l d0
    beq.w p2i_retire_failed
    movea.l I_REC(a2),a4
    movea.l I_CHIP(a2),a3
    moveq #15,d0
    move.l d0,12(a4)       ; record publication attempted BEFORE call
    movea.l I_GFX(a2),a6
    movea.l I_VP(a2),a0
    movea.l a3,a1
    lea 48(a3),a2
    jsr -420(a6)          ; ChangeSprite
    ; A2 is nonvolatile in graphics.library ABI, but was an argument.
    ; Restore the public frame from SP, not from a volatile register.
    movea.l sp,a2
p2i_move:
    bsr.w p2i_active
    tst.l d0
    beq.w p2i_retire_failed
    movea.l I_GFX(a2),a6
    movea.l I_VP(a2),a0
    movea.l I_CHIP(a2),a1
    move.l I_X(a2),d0
    move.l I_Y(a2),d1
    jsr -426(a6)          ; MoveSprite, no implicit Swap or VBL
    moveq #1,d0
    move.l d0,I_RESULT(a2)
    bra.w p2i_end
p2i_bad_receipt:
    ; OS violated fixed-channel GetSprite contract: cannot guess owner.
    ; Never permit FreeVec or destruction of a potentially live VP.
    movea.l I_REC(a2),a4
    ori.l #$80000004,12(a4)
    bra.w p2i_end
p2i_retire_failed:
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a1
    bsr.w AGSP_P2E_RETIRE
    bra.w p2i_end
p2i_private_abort:
    ; Only unpublished allocations and no live root reach here.
    movea.l $0004.w,a6
    move.l I_CHIP(a2),d0
    beq.s p2i_free_record
    movea.l d0,a1
    jsr -690(a6)
p2i_free_record:
    move.l I_REC(a2),d0
    beq.s p2i_leave_only
    movea.l d0,a1
    jsr -690(a6)
p2i_leave_only:
    movea.l I_ROOT(a2),a0
    bsr.w p2h_leave
    bra.w p2i_end

p2i_off:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_ID(a2)
    move.l a3,I_ARGS(a2)
    bsr.w p2i_init
    tst.l d0
    beq.w p2i_end
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_end
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2i_success
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_ID(a2),d0
    cmp.l 28(a4),d0
    bne.w p2i_end
    bsr.w p2i_retire
    bra.w p2i_end

p2i_bank_free:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    lea -I_FRAME(sp),sp
    movea.l sp,a2
    move.l d3,I_BANK(a2)
    move.l a3,I_ARGS(a2)
    clr.l I_ID(a2)
    bsr.w p2i_zero
    cmpi.l #5,I_BANK(a2)
    bcs.w p2i_end
    cmpi.l #65535,I_BANK(a2)
    bhi.w p2i_end
    ; Clear only this owner's matching selection; never Erase DATA.
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.s p2i_bf_context
    move.l I_BANK(a2),d0
    cmp.l 4(a4),d0
    bne.s p2i_bf_context
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w p2i_end
    clr.l (a4)
    clr.l 4(a4)
    clr.l 8(a4)
p2i_bf_context:
    bsr.w p2i_context
    tst.l d0
    beq.w p2i_bf_pending
    movea.l I_CELL(a2),a4
    tst.l (a4)
    beq.w p2i_bf_pending
    bsr.w p2i_live
    tst.l d0
    beq.w p2i_end
    movea.l I_REC(a2),a4
    move.l I_BANK(a2),d0
    cmp.l 32(a4),d0
    bne.w p2i_success
    bsr.w p2i_retire
    bra.w p2i_end
p2i_bf_pending:
    ; Recovery after successful CloseScreen whose idle predicate was pending.
    ; No screen/VP dereference and no new Chip allocation.
    moveq #0,d0
    bsr.w p2h_enter
    tst.l d0
    bne.s p2i_bf_have
    cmpi.l #1,d1
    beq.w p2i_success
    bra.w p2i_end
p2i_bf_have:
    move.l d0,I_ROOT(a2)
    movea.l d0,a3
    tst.l (a3)
    beq.s p2i_bf_empty
    tst.l 12(a3)
    bne.w p2i_leave_only
    movea.l (a3),a4
    move.l I_BANK(a2),d0
    cmp.l 32(a4),d0
    bne.w p2i_leave_only
    movea.l $0004.w,a6
    lea p2i_gfx_name(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.w p2i_leave_only
    move.l d0,I_GFX(a2)
    movea.l I_ROOT(a2),a0
    movea.l d0,a1
    bsr.w AGSP_P2G_RECLAIM
    move.l d0,I_RESULT(a2)
    movea.l $0004.w,a6
    movea.l I_GFX(a2),a1
    jsr -414(a6)
    bra.w p2i_leave_only
p2i_bf_empty:
    moveq #1,d0
    move.l d0,I_RESULT(a2)
    bra.w p2i_leave_only

p2i_success:
    moveq #1,d0
    move.l d0,I_RESULT(a2)
p2i_end:
    move.l I_RESULT(a2),d3
    movea.l I_ARGS(a2),a3
    lea I_FRAME(sp),sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

p2i_retire:
    movea.l I_REC(a2),a0
    movea.l I_GFX(a2),a1
    bsr.w AGSP_P2E_RETIRE
    cmpi.l #1,d0
    bne.s p2i_retire_return
    move.l d0,I_RESULT(a2)
p2i_retire_return:
    rts
p2i_init:
    bsr.w p2i_zero
    cmpi.l #1,I_ID(a2)
    bcs.w p2i_no
    cmpi.l #64,I_ID(a2)
    bhi.w p2i_no
    moveq #1,d0
    rts
p2i_zero:
    clr.l I_RESULT(a2)
    clr.l I_ROOT(a2)
    clr.l I_REC(a2)
    clr.l I_CHIP(a2)
    rts

p2i_context:
    ; Same relocated AGA State anchor as P0e cross-unit bridge.
    movea.l 456(a5),a0
    moveq #40,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l a0,I_STATE(a2)
    move.l a0,d0
    addi.l #P2I_CELL_DELTA,d0
    bcs.w p2i_no
    movea.l d0,a0
    moveq #16,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.l #$41475349,4(a0)
    bne.w p2i_no
    cmpi.l #$00010010,8(a0)
    bne.w p2i_no
    move.l a0,I_CELL(a2)
    movea.l I_STATE(a2),a4
    movea.l (a4),a0
    moveq #84,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    move.l a0,I_SCREEN(a2)
    lea 44(a0),a0
    move.l a0,I_VP(a2)
    movea.l 8(a4),a0
    move.l #212,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.w #212,18(a0)
    bcs.w p2i_no
    cmpi.w #39,20(a0)
    bcs.w p2i_no
    cmpi.w #40,20(a0)
    bhi.w p2i_no
    move.l a0,I_GFX(a2)
    moveq #1,d0
    rts
p2i_display_mode:
    movea.l I_STATE(a2),a0
    cmpi.l #320,12(a0)
    bne.w p2i_no
    cmpi.l #256,16(a0)
    bne.w p2i_no
    cmpi.l #256,20(a0)
    bne.w p2i_no
    movea.l I_VP(a2),a0
    cmpi.w #$5000,32(a0)
    bne.w p2i_no
    tst.l 20(a0)             ; no user Copper list in S1
    bne.w p2i_no
    movea.l 4(a0),a0
    moveq #52,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.b #2,1(a0)
    bne.w p2i_no
    cmpi.w #256,2(a0)
    bne.w p2i_no
    move.l a0,I_CM(a2)
    moveq #1,d0
    rts
p2i_live:
    ; The link was installed by this candidate while holding the anchor.
    movea.l I_CELL(a2),a0
    movea.l (a0),a3
    lea -56(a3),a0
    moveq #112,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    cmpi.l #$41475350,-8(a3)
    bne.w p2i_no
    cmpi.l #$00010070,-4(a3)
    bne.w p2i_no
    movea.l $0004.w,a6
    suba.l a1,a1
    jsr -294(a6)
    tst.l d0
    beq.w p2i_no
    cmp.l 16(a3),d0
    bne.w p2i_no
    cmp.l -16(a3),d0
    bne.w p2i_no
    move.l a5,d0
    cmp.l 4(a3),d0
    bne.w p2i_no
    move.l I_STATE(a2),d0
    cmp.l 8(a3),d0
    bne.w p2i_no
    move.l I_SCREEN(a2),d0
    cmp.l 12(a3),d0
    bne.w p2i_no
    movea.l (a3),a4
    move.l a3,I_ROOT(a2)
    move.l a4,I_REC(a2)
    move.l a4,d0
    beq.w p2i_no
    move.l (a4),I_CHIP(a2)
    move.l 4(a4),I_LEN(a2)
    move.l I_CHIP(a2),d0
    beq.w p2i_no
    moveq #1,d0
    rts
p2i_geometry:
    movea.l I_CHIP(a2),a0
    tst.l 24(a0)             ; zero hotspot only, proven capture path
    bne.w p2i_no
    moveq #0,d0
    move.w 4(a0),d0
    beq.w p2i_no
    add.l I_Y(a2),d0
    cmpi.l #256,d0
    bhi.w p2i_no
    moveq #1,d0
    rts
p2i_palette:
    ; Probe the same VideoControl GET tags as P2b; no SET call.
    lea I_TAG(a2),a1
    move.l #$80000028,(a1)
    move.l #$6a5a5a5a,4(a1)
    move.l #$80000029,8(a1)
    move.l #$6a5a5a5a,12(a1)
    move.l #$80000032,16(a1)
    move.l #$6a5a5a5a,20(a1)
    move.l #$80000034,24(a1)
    move.l #$6a5a5a5a,28(a1)
    clr.l 32(a1)
    clr.l 36(a1)
    movea.l I_CM(a2),a0
    movea.l I_GFX(a2),a6
    jsr -708(a6)
    tst.l d0
    bne.w p2i_no
    cmpi.l #16,I_TAG+4(a2)
    bne.w p2i_no
    cmpi.l #16,I_TAG+12(a2)
    bne.w p2i_no
    cmpi.l #255,I_TAG+20(a2)
    bne.w p2i_no
    cmpi.l #4,I_TAG+28(a2)
    bne.w p2i_no
    movea.l I_CM(a2),a0
    cmpi.b #1,18(a0)
    bne.w p2i_no
    lea I_TAG(a2),a1
    moveq #21,d0
    moveq #3,d1
    jsr -900(a6)
    lea I_TAG(a2),a0
    movea.l I_CHIP(a2),a1
    adda.w #31,a1
    moveq #8,d0
p2i_rgb:
    move.b (a0),d1
    cmp.b (a1)+,d1
    bne.w p2i_no
    adda.w #4,a0
    dbra d0,p2i_rgb
    moveq #1,d0
    rts
p2i_active:
    movea.l I_GFX(a2),a0
    moveq #0,d0
    move.b 166(a0),d0
    andi.b #12,d0
    cmpi.b #12,d0
    bne.w p2i_no
    movea.l 208(a0),a0
    moveq #32,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w p2i_no
    movea.l I_CHIP(a2),a1
    move.l a1,d0
    cmp.l 8(a0),d0
    bne.w p2i_no
    tst.l 12(a0)
    bne.w p2i_no
    cmpi.w #2,10(a1)
    bne.w p2i_no
    lea 48(a1),a0
    move.l a0,d0
    cmp.l (a1),d0
    bne.w p2i_no
    moveq #1,d0
    rts
p2i_no:
    moveq #0,d0
    rts
p2i_gfx_name:
    dc.b "graphics.library",0
    even
