; AGA_NATIVE_MIN_CPU: MC68020
; P2d L1: append-only inside UNIT142. No moved legacy data or internal labels.
; A3 = DBState. D0 = 1 safe, 0 refusal; D1/A0/A1/A6 preserved.
; Same SafePort protocol as source-owned Blit Fill:
; GetMsg(Exec -372) consumes only Safe; Disp and all other bits retained.
L1_AcquireSafe:
    movem.l d1/a0-a1/a6,-(a7)
    move.l 20(a3),d0
    andi.l #1,d0
    beq.w L1_SafeYes
    movea.l 12(a3),a0
    move.l a0,d0
    beq.w L1_SafeNo
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L1_SafeNo
    andi.l #$FFFFFFFE,20(a3)
L1_SafeYes:
    moveq #1,d0
    bra.w L1_SafeReturn
L1_SafeNo:
    moveq #0,d0
L1_SafeReturn:
    movem.l (a7)+,d1/a0-a1/a6
    rts

; Back Fill is a legacy instruction, not a function. Preserve its complete
; register ABI, entire physical bitmap/padding and 8-bit pen truncation.
; One immediate poll and at most three WaitTOF/re-polls, like B8 Clear.
; On timeout or missing SafePort, return without touching bitmap/allocating.
; This is a bounded best effort, NOT a guarantee that a fill took place.
L1_BackFillGuard:
    tst.l 8(a2)
    beq.w L1_BackFillRefuse
    moveq #3,d6
L1_BackFillRetry:
    bsr.w L1_AcquireSafe
    tst.l d0
    bne.w L1_BackFillReady
    tst.l 12(a3)
    beq.w L1_BackFillRefuse
    tst.l d6
    beq.w L1_BackFillRefuse
    subq.l #1,d6
    movea.l 8(a2),a6
    jsr -270(a6)
    bra.w L1_BackFillRetry
L1_BackFillReady:
    move.l #UNIT142_BLOCK_00C9E_EDIT,d0
    bra.l L1_BackFillResume
L1_BackFillRefuse:
    bra.l L_UNIT142_00D32

; IFF Load has an existing 0/1 result and cleanup. Refuse immediately if
; pending Safe is not available. Preflight has already selected a BitMap;
; check that it is still the back before acquiring. No palette or plan
; write before this gate. Resume exactly at original WaitBlit.
L1_IffGuard:
    move.l a3,-(a7)
    movea.l (a5),a2
    movea.l 32(a2),a3
    move.l a3,d0
    beq.w L1_IffRefuse
    tst.l 8(a3)
    beq.w L1_IffBack1
    movea.l (a3),a0
    bra.w L1_IffCheckBack
L1_IffBack1:
    movea.l 4(a3),a0
L1_IffCheckBack:
    move.l a0,d0
    beq.w L1_IffRefuse
    move.l (a0),d0
    beq.w L1_IffRefuse
    cmp.l 80(a5),d0
    bne.w L1_IffRefuse
    tst.l 8(a2)
    beq.w L1_IffRefuse
    bsr.w L1_AcquireSafe
    tst.l d0
    beq.w L1_IffRefuse
    movea.l (a7)+,a3
    movea.l 8(a2),a6
    bra.l L1_IffResume
L1_IffRefuse:
    movea.l (a7)+,a3
    bra.l L_UNIT142_00EB8
