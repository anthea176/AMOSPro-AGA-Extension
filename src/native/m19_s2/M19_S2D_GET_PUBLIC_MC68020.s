; AGA_NATIVE_MIN_CPU: MC68020
; M19 S2d-P1: Get AGA Sprite I,X1,Y1,X2,Y2,TransparentPen.
; All six AMOS arguments are integer LONG. D3=TransparentPen, (A3)+
; yields Y2,X2,Y1,X1,I. X2/Y2 are INCLUSIVE. 16/32/64px, 2/4bpp.
; Selection bound to both A5 and the live Cur_Banks owner cell.
;
; Entry/return: D3=1 success, 0 refusal; D2=0 AMOS integer result.
; Other caller registers preserved; A3 consumes exactly five LONGs.
; No DMA, no Sprite channel, no changes to P2d/LAST_GOOD.
; Uses AMOS Professional 365 Exec.AllocVec/FreeVec and source-verifed
; P1c pipeline, validator, Bnk.GetAdr and transactional publisher.
;
; Private allocation ownership:
; WORK (4120+128*W bytes) request, RGB32, RGB24, descriptor, 2/4bpp image,
; local palette, repack request and commit request; + STAGE AGSP bank
; payload capacity oldlen + 96 + (W/2)*H, sufficient for max 4 plans.
; All pointers belong exclusively to this invocation, are freed after
; the transaction or any refusal, and are NEVER retained by a bank.
;
AGSP_GET_F_ID       equ 0
AGSP_GET_F_X1       equ 4
AGSP_GET_F_Y1       equ 8
AGSP_GET_F_X2       equ 12
AGSP_GET_F_Y2       equ 16
AGSP_GET_F_TRANS    equ 20
AGSP_GET_F_BANK     equ 24
AGSP_GET_F_OLDPTR   equ 28
AGSP_GET_F_OLDLEN   equ 32
AGSP_GET_F_WORK     equ 36
AGSP_GET_F_STAGE    equ 40
AGSP_GET_F_CAP      equ 44
AGSP_GET_F_STATE    equ 48
AGSP_GET_F_HEIGHT   equ 52
AGSP_GET_F_RESULT   equ 56
AGSP_GET_F_WIDTH    equ 60
AGSP_GET_F_SNAPSHOT equ 64
AGSP_GET_FRAME      equ 96
AGSP_GET_WORK_FIXED equ 4120
AGSP_GET_MEM_FLAGS  equ $00010001

agsp_s1_get_body:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(sp)
    suba.l #AGSP_GET_FRAME,sp
    movea.l sp,a2
    move.l d3,AGSP_GET_F_TRANS(a2)
    move.l (a3)+,AGSP_GET_F_Y2(a2)
    move.l (a3)+,AGSP_GET_F_X2(a2)
    move.l (a3)+,AGSP_GET_F_Y1(a2)
    move.l (a3)+,AGSP_GET_F_X1(a2)
    move.l (a3)+,AGSP_GET_F_ID(a2)
    clr.l AGSP_GET_F_WORK(a2)
    clr.l AGSP_GET_F_STAGE(a2)
    clr.l AGSP_GET_F_RESULT(a2)
    moveq #0,d3
    moveq #0,d2

    ; Reject stale selection, foreign AMOS owner, or unselected bank.
    lea agsp_s1_selection_state(pc),a4
    move.l a5,d0
    cmp.l (a4),d0
    bne.w agsp_s1_get_cleanup
    movea.l 8(a4),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l a0,AGSP_GET_F_SNAPSHOT(a2)
    move.l 4(a4),d0
    cmpi.l #5,d0
    bcs.w agsp_s1_get_cleanup
    cmpi.l #65535,d0
    bhi.w agsp_s1_get_cleanup
    move.l d0,AGSP_GET_F_BANK(a2)
    move.l d0,AGSP_GET_F_SNAPSHOT+4(a2)
    move.l AGSP_GET_F_ID(a2),d0
    cmpi.l #1,d0
    bcs.w agsp_s1_get_cleanup
    cmpi.l #4096,d0
    bhi.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_TRANS(a2),d0
    cmpi.l #255,d0
    bhi.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_X1(a2),d0
    tst.l d0
    bmi.w agsp_s1_get_cleanup
    cmpi.l #65519,d0
    bhi.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_X2(a2),d1
    cmpi.l #65535,d1
    bhi.w agsp_s1_get_cleanup
    cmp.l d0,d1
    bcs.w agsp_s1_get_cleanup
    sub.l d0,d1
    cmpi.l #15,d1
    beq.s agsp_s2d_get_width_ok
    cmpi.l #31,d1
    beq.s agsp_s2d_get_width_ok
    cmpi.l #63,d1
    bne.w agsp_s1_get_cleanup
agsp_s2d_get_width_ok:
    addq.l #1,d1
    move.l d1,AGSP_GET_F_WIDTH(a2)
    move.l AGSP_GET_F_Y1(a2),d0
    tst.l d0
    bmi.w agsp_s1_get_cleanup
    cmpi.l #65535,d0
    bhi.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_Y2(a2),d1
    cmpi.l #65535,d1
    bhi.w agsp_s1_get_cleanup
    sub.l d0,d1
    bmi.w agsp_s1_get_cleanup
    cmpi.l #255,d1
    bhi.w agsp_s1_get_cleanup
    addq.l #1,d1
    move.l d1,AGSP_GET_F_HEIGHT(a2)

    ; Screen state is Main's private AGA screen; only SCREEN_PREPARE
    ; may read the guarded inactive ScreenBuffer, after Safe/WaitBlit.
    movea.l $01C8(a5),a4
    move.l a4,d0
    beq.w agsp_s1_get_cleanup
    btst #0,d0
    bne.w agsp_s1_get_cleanup
    move.l a4,AGSP_GET_F_STATE(a2)
    ; All private State fields used by the bridge must be accessible.
    movea.l a4,a0
    moveq #36,d0
    bsr.w AGSP_I_SPAN
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l 12(a4),d0          ; state.width
    cmp.l AGSP_GET_F_X2(a2),d0
    bls.w agsp_s1_get_cleanup
    move.l 16(a4),d0          ; state.height
    cmp.l AGSP_GET_F_Y2(a2),d0
    bls.w agsp_s1_get_cleanup

    ; Snapshot the selected bank BEFORE any temporary allocation.
    movea.l AGSP_GET_F_SNAPSHOT(a2),a0
    bsr.w AGSP_I_OWNER
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_BANK(a2),d0
    dc.w $FE11,$F700,797
    move.l a0,AGSP_GET_F_OLDPTR(a2)
    move.l a0,AGSP_GET_F_SNAPSHOT+8(a2)
    move.l AGSP_GET_F_BANK(a2),d0
    bsr.w AGSP_I_LIVE
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l d1,AGSP_GET_F_OLDLEN(a2)
    move.l d1,AGSP_GET_F_SNAPSHOT+12(a2)
    move.l d2,AGSP_GET_F_SNAPSHOT+16(a2)
    move.l d3,AGSP_GET_F_SNAPSHOT+20(a2)
    cmpi.l #$FFFFFFFF,d2
    beq.w agsp_s1_get_cleanup

    ; Worst-case new image: one 48-byte directory row + (W/2)*H
    ; pixels + 48-byte RGB24 palette. Replaced image can be smaller.
    move.l AGSP_GET_F_WIDTH(a2),d0
    lsr.l #1,d0
    mulu.w AGSP_GET_F_HEIGHT+2(a2),d0
    addi.l #96,d0
    bcs.w agsp_s1_get_cleanup
    add.l AGSP_GET_F_OLDLEN(a2),d0
    bcs.w agsp_s1_get_cleanup
    cmpi.l #$01000000,d0
    bhi.w agsp_s1_get_cleanup
    move.l d0,AGSP_GET_F_CAP(a2)

    ; Allocate all scratch in a single privately owned cleared block.
    movea.l $0004.w,a6
    move.l AGSP_GET_F_WIDTH(a2),d0
    lsl.l #7,d0              ; (W/8)*256*4, 2048/4096/8192
    addi.l #AGSP_GET_WORK_FIXED,d0
    move.l #AGSP_GET_MEM_FLAGS,d1
    jsr -684(a6)              ; Exec.AllocVec
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l d0,AGSP_GET_F_WORK(a2)
    move.l AGSP_GET_F_CAP(a2),d0
    move.l #AGSP_GET_MEM_FLAGS,d1
    jsr -684(a6)
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l d0,AGSP_GET_F_STAGE(a2)

    ; Re-resolve after allocations. Never read a stale bank snapshot.
    lea AGSP_GET_F_SNAPSHOT(a2),a0
    bsr.w AGSP_I_EXPECT
    tst.l d0
    beq.w agsp_s1_get_cleanup
    move.l AGSP_GET_F_STATE(a2),d0
    cmp.l $01C8(a5),d0
    bne.w agsp_s1_get_cleanup

    ; Build the 96-byte request and independent expected bank snapshot.
    movea.l AGSP_GET_F_WORK(a2),a4
    move.l AGSP_GET_F_STATE(a2),(a4)
    lea 96(a4),a0
    move.l a0,4(a4)           ; RGB32[3072]
    lea 3168(a4),a0
    move.l a0,8(a4)           ; RGB24[768]
    lea 3936(a4),a0
    move.l a0,12(a4)          ; descriptor[64]
    lea 4000(a4),a0
    move.l a0,16(a4)          ; planes[(W/8)*256*4], H<=256
    move.l AGSP_GET_F_WIDTH(a2),d0
    lsl.l #7,d0
    lea 4000(a4,d0.l),a0
    move.l a0,20(a4)          ; palette[48]
    move.w AGSP_GET_F_X1+2(a2),24(a4)
    move.w AGSP_GET_F_Y1+2(a2),26(a4)
    move.w AGSP_GET_F_HEIGHT+2(a2),28(a4)
    move.w AGSP_GET_F_TRANS+2(a2),30(a4)
    move.w AGSP_GET_F_WIDTH+2(a2),32(a4)
    clr.w 34(a4)
    move.l AGSP_GET_F_BANK(a2),36(a4)
    move.w AGSP_GET_F_ID+2(a2),40(a4)
    clr.w 42(a4)              ; hotspot x default 0
    clr.w 44(a4)              ; hotspot y default 0
    clr.w 46(a4)
    move.l AGSP_GET_F_OLDPTR(a2),48(a4)
    move.l AGSP_GET_F_OLDLEN(a2),52(a4)
    movea.l 20(a4),a0
    lea 48(a0),a0
    move.l a0,56(a4)          ; repack request[40]
    move.l AGSP_GET_F_STAGE(a2),60(a4)
    move.l AGSP_GET_F_CAP(a2),64(a4)
    lea 40(a0),a0
    move.l a0,68(a4)          ; commit request[32]
    lea AGSP_GET_F_SNAPSHOT(a2),a0
    lea 72(a4),a1
    moveq #5,d7
agsp_i_get_snapshot_copy:
    move.l (a0)+,(a1)+
    dbra d7,agsp_i_get_snapshot_copy
    movea.l a4,a0
    bsr.w AGSP_P1C_PIPELINE_ENTRY
    move.l d3,AGSP_GET_F_RESULT(a2)

agsp_s1_get_cleanup:
    ; Stage and scratch memory NEVER survive publication, even on refusal.
    movea.l $0004.w,a6
    move.l AGSP_GET_F_STAGE(a2),d0
    beq.w agsp_s1_get_work_free
    movea.l d0,a1
    jsr -690(a6)              ; Exec.FreeVec
agsp_s1_get_work_free:
    move.l AGSP_GET_F_WORK(a2),d0
    beq.w agsp_s1_get_done
    movea.l d0,a1
    jsr -690(a6)
agsp_s1_get_done:
    move.l AGSP_GET_F_RESULT(a2),d3
    adda.l #AGSP_GET_FRAME,sp
    movem.l (sp)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
