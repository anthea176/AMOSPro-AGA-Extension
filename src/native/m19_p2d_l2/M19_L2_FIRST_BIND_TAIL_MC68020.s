; AGA_NATIVE_MIN_CPU: MC68020
; AGA-002: acquire an available Safe reply only for the first B8 Bind.
; Entry is after the selector's State/DBState TypeOfMem and extent checks.
; A4=DBState, A2=selector frame. This selector saves all scratch registers.
; Existing pool paths keep their original refusal and separate acquisition.
L2_FirstBindSafe:
    lea L_BOBS_0DA10(pc),a0
    tst.l (a0)
    bne.w L_BOBS_0C07A
    cmpi.l #1,8(a4)
    bhi.w L_BOBS_0C07A
    move.l 12(a4),d0
    beq.w L_BOBS_0C07A
    btst #0,d0
    bne.w L_BOBS_0C07A
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0C07A
    movea.l 12(a4),a0
    jsr -372(a6)
    tst.l d0
    beq.w L_BOBS_0C07A
    andi.l #$FFFFFFFE,20(a4)
    bra.w L2_SelectResume
