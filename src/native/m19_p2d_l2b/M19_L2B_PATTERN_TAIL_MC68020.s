; AGA_NATIVE_MIN_CPU: MC68020
; AGA-011: preserve the original single-buffer path and instruction ABI.
; Double buffer: use a private RastPort, never retarget Screen.RastPort.
; A2 is the validated Screen state, A3 is not saved by the legacy prologue.
L2B_PatternDispatch:
    move.l a3,-(a7)
    movea.l (a2),a4
    movea.l 8(a2),a6
    movea.l 32(a2),a3
    move.l a3,d0
    bne.w L2B_PatternDB
    movea.l (a7)+,a3
    bra.l L2B_PatternResume

L2B_PatternDB:
    tst.l 8(a2)
    beq.w L2B_PatternExit
    move.l 20(a2),d4
    cmpi.l #2,d4
    blo.w L2B_PatternExit
    cmpi.l #256,d4
    bhi.w L2B_PatternExit
    move.l 16(a2),d5
    beq.w L2B_PatternExit
    cmpi.l #65535,d5
    bhi.w L2B_PatternExit
    tst.l 12(a2)
    ble.w L2B_PatternExit
    ; DB+8 is the front index. Select the other ScreenBuffer.
    move.l 8(a3),d0
    beq.w L2B_PatternFront0
    cmpi.l #1,d0
    bne.w L2B_PatternExit
    movea.l (a3),a0
    movea.l 4(a3),a1
    bra.w L2B_PatternCheck
L2B_PatternFront0:
    movea.l 4(a3),a0
    movea.l (a3),a1
L2B_PatternCheck:
    move.l a0,d0
    beq.w L2B_PatternExit
    move.l a1,d0
    beq.w L2B_PatternExit
    move.l (a0),d7
    beq.w L2B_PatternExit
    tst.l (a1)
    beq.w L2B_PatternExit
    cmp.l (a1),d7
    beq.w L2B_PatternExit
    ; Same bounded Safe protocol as L1 Back Fill. Check null/odd port
    ; before GetMsg. D7 retains the selected physical back BitMap.
    moveq #3,d6
L2B_PatternRetry:
    btst #0,23(a3)
    beq.w L2B_PatternAcquire
    move.l 12(a3),d0
    beq.w L2B_PatternExit
    btst #0,d0
    bne.w L2B_PatternExit
L2B_PatternAcquire:
    bsr.w L1_AcquireSafe
    tst.l d0
    bne.w L2B_PatternReady
    tst.l d6
    beq.w L2B_PatternExit
    subq.l #1,d6
    movea.l 8(a2),a6
    jsr -270(a6)
    bra.w L2B_PatternRetry
L2B_PatternReady:
    ; Reuse Back Fill's AllocVec MEMF_CLEAR / InitRastPort convention.
    ; No palette or pixels are changed before successful allocation.
    move.l #128,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L2B_PatternExit
    movea.l d0,a3
    movea.l a3,a1
    movea.l 8(a2),a6
    jsr -198(a6)
    move.l d7,4(a3)
    jsr -228(a6)
    moveq #0,d6
    ; Exact legacy row/pen/RGB calculation; only the drawing RP changes.
L2B_PatternRow:
    move.l d6,d0
    mulu.w d4,d0
    divu.w d5,d0
    andi.l #$0000FFFF,d0
    move.l d0,d7
    move.l d7,d1
    mulu.w #$00FF,d1
    move.l d4,d0
    subq.l #1,d0
    divu.w d0,d1
    andi.l #$0000FFFF,d1
    move.l #$000000FF,d2
    sub.l d1,d2
    lsl.l #8,d1
    swap d1
    lsl.l #8,d2
    swap d2
    move.l #$30000000,d3
    move.l d7,d0
    lea 44(a4),a0
    jsr -852(a6)
    move.l d7,d0
    movea.l a3,a1
    jsr -342(a6)
    moveq #0,d0
    move.l d6,d1
    move.l 12(a2),d2
    subq.l #1,d2
    move.l d6,d3
    movea.l a3,a1
    jsr -306(a6)
    addq.l #1,d6
    cmp.l d5,d6
    bne.w L2B_PatternRow
    jsr -228(a6)
    movea.l a3,a1
    movea.l $0004.w,a6
    jsr -690(a6)
L2B_PatternExit:
    movea.l (a7)+,a3
    bra.l L_UNIT142_007F0
