; AGA_NATIVE_MIN_CPU: MC68020
; S2d-P2b private blank-pair allocation and acquisition receipts.
; Two entries: +0 ALLOC_BLANK_PAIR; +4 ACQUIRE_BLANK_PAIR.
; No Move/Change/FreeSprite, publication of actual image, direct OS structure
; writes, FMODE or AMOS API. GetExtSpriteA is treated as potential exposure.
; Caller pins live GfxBase and each detached OS allocation, holds exclusive
; registry borrow, proves screen/VP/context, width/ownership and palette.
; The caller must retire or prove no OS reference before freeing any
; descriptor passed to GetExtSpriteA, even when that call refuses.
;
; ALLOC: A6=live graphics.library; D0 width 16/32/64, D1 kind 2/4.
; Return D0 even blank ExtSprite*, D1 odd blank ExtSprite*, or 0/0.
; Always two allocated blank descriptors: odd guard for kind2, attached for
; kind4. Height=1, all planes zero. On second OOM free only detached first.
; V39 simple allowed; V39 attach deferred (documented OS bugs).
;
; ACQUIRE: A0 pinned 36-byte private receipt; A6 same pinned GfxBase.
; +0 GfxBase; +4 even blank*; +8 odd blank*; +12 width.L; +16 kind.L
; +20 expected even channel.L (2/4/6); +24 state.L initially 0;
; +28 context width.L (0 if no other live/reserved records; else same width);
; +32 reserved zero. Metadata comes from actual owned blank allocation.
; Context width is an assertion of the CALLER, not an OS width probe.
; State bit0=even confirmed return, bit1=odd confirmed return,
; bit2=Get attempted/exposure possible (sticky), bit31=quarantine.
; D0=1 and D1=0 success, state7. D0=0 and D1=1 invalid/private,
; 2 OS refusal with state4/5, 3 unexpected receipt/quarantine.
; No retry on nonzero state, no release on any error here.
; Preserve D2-D7/A0-A6 in both entries.
    bra.w AGSP_S2D_ALLOC_BLANK_PAIR
    bra.w AGSP_S2D_ACQUIRE_BLANK_PAIR

S2D_B_BM equ 0
S2D_B_TAG equ 40
S2D_B_PIX equ 64
S2D_B_FRAME equ 96
S2D_B_WIDTH_TAG equ $81000000
S2D_B_ATTACH_TAG equ $81000008
S2D_B_NUM_TAG equ $82000020
S2D_B_PAIR_TAG equ $82000022

AGSP_S2D_ALLOC_BLANK_PAIR:
    movem.l d2-d7/a0-a6,-(sp)
    suba.w #S2D_B_FRAME,sp
    movea.l sp,a3
    move.l d0,d4
    move.l d1,d5
    movea.l a6,a5
    bsr.w s2d_b_contract
    tst.l d0
    beq.w s2d_b_alloc_bad
    movea.l a3,a0
    moveq #23,d0
s2d_b_zero:
    clr.l (a0)+
    dbra d0,s2d_b_zero
    move.l d4,d6
    lsr.l #3,d6
    lea S2D_B_BM(a3),a0
    move.l d5,d0
    move.l d4,d1
    moveq #1,d2
    jsr -390(a6)
    cmp.w S2D_B_BM(a3),d6
    bne.w s2d_b_alloc_bad
    cmpi.w #1,S2D_B_BM+2(a3)
    bne.w s2d_b_alloc_bad
    cmp.b S2D_B_BM+5(a3),d5
    bne.w s2d_b_alloc_bad
    lea S2D_B_BM+8(a3),a0
    lea S2D_B_PIX(a3),a1
    move.w d5,d0
    subq.w #1,d0
s2d_b_planes:
    move.l a1,(a0)+
    adda.l d6,a1
    dbra d0,s2d_b_planes
    lea S2D_B_TAG(a3),a1
    move.l #S2D_B_WIDTH_TAG,(a1)
    move.l d4,4(a1)
    lea S2D_B_BM(a3),a2
    jsr -1020(a6)
    tst.l d0
    beq.s s2d_b_alloc_bad
    move.l d0,d7
    lea S2D_B_TAG(a3),a1
    cmpi.l #4,d5
    bne.s s2d_b_second
    move.l #S2D_B_ATTACH_TAG,8(a1)
    move.l #1,12(a1)
s2d_b_second:
    lea S2D_B_BM(a3),a2
    jsr -1020(a6)
    tst.l d0
    beq.s s2d_b_alloc_rollback
    move.l d0,d1
    move.l d7,d0
    bra.s s2d_b_alloc_return
s2d_b_alloc_rollback:
    movea.l d7,a2
    jsr -1032(a6)
s2d_b_alloc_bad:
    moveq #0,d0
    moveq #0,d1
s2d_b_alloc_return:
    adda.w #S2D_B_FRAME,sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

AGSP_S2D_ACQUIRE_BLANK_PAIR:
    movem.l d2-d7/a0-a6,-(sp)
    suba.w #24,sp
    movea.l a0,a3
    movea.l a6,a5
    move.l a3,d0
    beq.w s2d_b_acquire_bad
    btst #0,d0
    bne.w s2d_b_acquire_bad
    cmpa.l (a3),a5
    bne.w s2d_b_acquire_bad
    tst.l 24(a3)
    bne.w s2d_b_acquire_bad
    tst.l 32(a3)
    bne.w s2d_b_acquire_bad
    move.l 12(a3),d4
    move.l 16(a3),d5
    bsr.w s2d_b_contract
    tst.l d0
    beq.w s2d_b_acquire_bad
    move.l 28(a3),d0
    beq.s s2d_b_context_ok
    cmp.l d4,d0
    bne.w s2d_b_acquire_bad
s2d_b_context_ok:
    move.l 20(a3),d6
    cmpi.l #2,d6
    beq.s s2d_b_channel_ok
    cmpi.l #4,d6
    beq.s s2d_b_channel_ok
    cmpi.l #6,d6
    bne.w s2d_b_acquire_bad
s2d_b_channel_ok:
    move.l 4(a3),d0
    beq.w s2d_b_acquire_bad
    btst #0,d0
    bne.w s2d_b_acquire_bad
    move.l 8(a3),d1
    beq.w s2d_b_acquire_bad
    btst #0,d1
    bne.w s2d_b_acquire_bad
    cmp.l d0,d1
    beq.w s2d_b_acquire_bad
    movea.l sp,a1
    move.l #S2D_B_NUM_TAG,(a1)
    move.l d6,4(a1)
    clr.l 8(a1)
    clr.l 12(a1)
    clr.l 16(a1)
    clr.l 20(a1)
    cmpi.l #4,d5
    bne.s s2d_b_acquire_even
    move.l #S2D_B_PAIR_TAG,8(a1)
    move.l 8(a3),12(a1)
s2d_b_acquire_even:
    movea.l 4(a3),a2
    moveq #4,d7
    move.l d7,24(a3)         ; sticky BEFORE any OS attempt
    jsr -930(a6)
    cmpi.l #-1,d0
    beq.w s2d_b_os_refusal
    cmp.l d6,d0
    bne.w s2d_b_quarantine
    ori.l #1,d7
    cmpi.l #4,d5
    bne.s s2d_b_check_even
    ori.l #2,d7             ; documented pair receipt on success
s2d_b_check_even:
    move.l d7,24(a3)
    movea.l 4(a3),a2
    cmp.w 10(a2),d6          ; public SimpleSprite.num, read only
    bne.w s2d_b_quarantine
    cmpi.l #4,d5
    beq.s s2d_b_check_both
    ; Simple object reserves its second channel as a transparent guard.
    movea.l sp,a1
    move.l d6,d0
    addq.l #1,d0
    move.l d0,4(a1)
    movea.l 8(a3),a2
    jsr -930(a6)
    cmpi.l #-1,d0
    beq.s s2d_b_os_refusal
    move.l d6,d1
    addq.l #1,d1
    cmp.l d1,d0
    bne.s s2d_b_quarantine
    ori.l #2,d7
    move.l d7,24(a3)
s2d_b_check_both:
    movea.l 4(a3),a2
    cmp.w 10(a2),d6
    bne.s s2d_b_quarantine
    movea.l 8(a3),a2
    move.l d6,d0
    addq.l #1,d0
    cmp.w 10(a2),d0
    bne.s s2d_b_quarantine
    moveq #1,d0
    moveq #0,d1
    bra.s s2d_b_acquire_return
s2d_b_quarantine:
    ori.l #$80000000,d7
    move.l d7,24(a3)
    moveq #3,d1
    bra.s s2d_b_acquire_no
s2d_b_os_refusal:
    moveq #2,d1
    bra.s s2d_b_acquire_no
s2d_b_acquire_bad:
    moveq #1,d1
s2d_b_acquire_no:
    moveq #0,d0
s2d_b_acquire_return:
    adda.w #24,sp
    movem.l (sp)+,d2-d7/a0-a6
    rts

; D4 width, D5 kind, A5/A6 caller-owned live library. No OS calls.
s2d_b_contract:
    move.l a5,d0
    beq.s s2d_b_contract_no
    btst #0,d0
    bne.s s2d_b_contract_no
    cmpi.w #34,18(a5)
    bcs.s s2d_b_contract_no
    cmpi.w #1032,16(a5)
    bcs.s s2d_b_contract_no
    cmpi.w #39,20(a5)
    bcs.s s2d_b_contract_no
    cmpi.l #16,d4
    beq.s s2d_b_width_ok
    cmpi.l #32,d4
    beq.s s2d_b_width_ok
    cmpi.l #64,d4
    bne.s s2d_b_contract_no
s2d_b_width_ok:
    cmpi.l #2,d5
    beq.s s2d_b_contract_yes
    cmpi.l #4,d5
    bne.s s2d_b_contract_no
    cmpi.w #40,20(a5)
    bcs.s s2d_b_contract_no
s2d_b_contract_yes:
    moveq #1,d0
    rts
s2d_b_contract_no:
    moveq #0,d0
    rts
