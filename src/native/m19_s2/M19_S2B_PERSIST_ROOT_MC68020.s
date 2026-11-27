; AGA_NATIVE_MIN_CPU: MC68020
; S2b private named transaction, source-derived from P2m.
; Same registry name; incompatible older schemas must be refused.
; 240-byte allocation, root at +56, count +0, owner +4, State +8,
; Screen +12, borrow Task +16, lifetime Task +48.
; Three 44-byte inline records at root+52/+96/+140 (pairs 2/4/6).
; All clients hold exactly one validated semaphore borrow, no code ptrs.
; Enter/Leave ABI and reasons identical to P2m.
    bra.w s2b_p2h_enter
    bra.w s2b_p2h_leave

s2b_p2h_enter:
    movem.l d2-d7/a0-a6,-(sp)
    move.l d0,d2
    moveq #0,d5
    moveq #5,d4
    suba.l a3,a3
    cmpi.l #1,d2
    bhi.w s2b_p2h_enter_return
    bsr.w s2b_p2h_exec_task
    tst.l d0
    beq.w s2b_p2h_enter_return
    move.l d0,d3
s2b_p2h_lookup:
    jsr -132(a6)          ; Forbid, no waits/allocations in this span
    bsr.w s2b_p2h_find
    tst.l d0
    bne.w s2b_p2h_found
    tst.l d2
    beq.w s2b_p2h_absent
    move.l a3,d0
    bne.w s2b_p2h_publish
    jsr -138(a6)          ; Permit before AllocVec
    move.l #240,d0
    move.l #$00010001,d1  ; MEMF_PUBLIC | MEMF_CLEAR
    jsr -684(a6)
    tst.l d0
    beq.w s2b_p2h_oom
    movea.l d0,a3
    move.l #$41475350,48(a3)
    move.l #$000400f0,52(a3)
    lea 76(a3),a1
    move.l a1,10(a3)      ; name lives inside persistent allocation
    lea s2b_p2h_name(pc),a0
s2b_p2h_copy_name:
    move.b (a0)+,d0
    move.b d0,(a1)+
    tst.b d0
    bne.s s2b_p2h_copy_name
    bra.w s2b_p2h_lookup      ; race-safe second lookup before publication
s2b_p2h_publish:
    movea.l a3,a4
    movea.l a4,a1
    jsr -600(a6)          ; AddSemaphore initializes and publishes
    suba.l a3,a3          ; anchor now belongs to named registry
    bra.s s2b_p2h_try_lock
s2b_p2h_found:
    movea.l d0,a4
    bsr.w s2b_p2h_validate
    tst.l d0
    beq.w s2b_p2h_bad_anchor
s2b_p2h_try_lock:
    tst.l 72(a4)
    bne.w s2b_p2k_unfinished
    tst.l 40(a4)         ; no recursion even if OS owner is current Task
    bne.w s2b_p2h_busy
    movea.l a4,a0
    jsr -576(a6)          ; AttemptSemaphore: never block under Forbid
    tst.l d0
    beq.s s2b_p2h_busy
    move.l d3,72(a4)
    lea 56(a4),a0
    move.l a0,d5
    moveq #0,d4
    bra.s s2b_p2h_enter_permit
s2b_p2h_absent:
    moveq #1,d4
    bra.s s2b_p2h_enter_permit
s2b_p2h_bad_anchor:
    moveq #3,d4
    bra.s s2b_p2h_enter_permit
s2b_p2k_unfinished:
    moveq #6,d4
    bra.s s2b_p2h_enter_permit
s2b_p2h_busy:
    moveq #2,d4
s2b_p2h_enter_permit:
    jsr -138(a6)
    move.l a3,d0
    beq.s s2b_p2h_enter_return
    movea.l a3,a1        ; losing unpublished allocation, not registry
    jsr -690(a6)
    bra.s s2b_p2h_enter_return
s2b_p2h_oom:
    moveq #4,d4
s2b_p2h_enter_return:
    move.l d5,d0
    move.l d4,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts

s2b_p2h_leave:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    suba.l a2,a2
    moveq #0,d5
    moveq #5,d4
    move.l a3,d0
    beq.w s2b_p2h_leave_return
    btst #0,d0
    bne.w s2b_p2h_leave_return
    bsr.w s2b_p2h_exec_task
    tst.l d0
    beq.w s2b_p2h_leave_return
    move.l d0,d3
    jsr -132(a6)
    bsr.w s2b_p2h_find
    tst.l d0
    beq.w s2b_p2h_leave_bad
    movea.l d0,a4
    bsr.w s2b_p2h_validate
    tst.l d0
    beq.w s2b_p2h_leave_bad
    lea 56(a4),a0
    cmpa.l a0,a3
    bne.w s2b_p2h_leave_bad
    cmp.l 72(a4),d3
    bne.w s2b_p2h_leave_busy
    cmp.l 40(a4),d3
    bne.w s2b_p2h_leave_busy
    cmpi.w #1,14(a4)      ; one exact private borrow, never claim nested release
    bne.w s2b_p2h_leave_busy
    tst.w 44(a4)           ; no foreign waiter in the private protocol
    bne.w s2b_p2h_leave_busy
    ; Only remove a truly empty and exclusively held registry. Never
    ; free a semaphore with waiters or an extra recursive OS lock.
    tst.l 56(a4)
    bne.s s2b_p2h_unlock
    tst.l 60(a4)
    bne.s s2b_p2h_unlock
    tst.l 64(a4)
    bne.s s2b_p2h_unlock
    tst.l 68(a4)
    bne.s s2b_p2h_unlock
    tst.l 104(a4)
    bne.s s2b_p2h_unlock
    ; A corrupted count may not hide a record from the removal guard.
    lea 108(a4),a0
    moveq #32,d0
s2b_empty_slots:
    tst.l (a0)+
    bne.s s2b_p2h_unlock
    dbra d0,s2b_empty_slots
    movea.l a4,a1
    jsr -606(a6)          ; RemSemaphore while exclusively locked
    movea.l a4,a2        ; no client can find it after Permit
s2b_p2h_unlock:
    clr.l 72(a4)
    movea.l a4,a0
    jsr -570(a6)          ; ReleaseSemaphore, matching successful Attempt
    moveq #1,d5
    moveq #0,d4
    bra.s s2b_p2h_leave_permit
s2b_p2h_leave_bad:
    moveq #3,d4
    bra.s s2b_p2h_leave_permit
s2b_p2h_leave_busy:
    moveq #2,d4
s2b_p2h_leave_permit:
    jsr -138(a6)
    move.l a2,d0
    beq.s s2b_p2h_leave_return
    movea.l a2,a1
    jsr -690(a6)          ; removed, unlocked, no registered borrower
s2b_p2h_leave_return:
    move.l d5,d0
    move.l d4,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts

s2b_p2h_exec_task:
    movea.l $0004.w,a6
    move.l a6,d0
    beq.s s2b_p2h_exec_bad
    btst #0,d0
    bne.s s2b_p2h_exec_bad
    cmpi.w #39,20(a6)
    bcs.s s2b_p2h_exec_bad
    cmpi.w #690,16(a6)
    bcs.s s2b_p2h_exec_bad
    suba.l a1,a1
    jsr -294(a6)          ; FindTask(NULL)
    rts
s2b_p2h_exec_bad:
    moveq #0,d0
    rts

s2b_p2h_find:
    lea s2b_p2h_name(pc),a1
    jsr -594(a6)
    rts

s2b_p2h_validate:
    ; FindSemaphore gives a live named node under Forbid. Check inline
    ; name and ABI before touching root fields. TypeOfMem is not proof
    ; of an allocation's exact size; the private namespace is a contract.
    move.l a4,d0
    beq.w s2b_p2h_invalid
    btst #0,d0
    bne.w s2b_p2h_invalid
    addi.l #239,d0
    bcs.w s2b_p2h_invalid
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w s2b_p2h_invalid
    movea.l a4,a1
    jsr -534(a6)
    tst.l d0
    beq.s s2b_p2h_invalid
    cmpi.b #15,8(a4)     ; NT_SIGNALSEM
    bne.s s2b_p2h_invalid
    lea 76(a4),a0
    move.l a0,d0
    cmp.l 10(a4),d0
    bne.s s2b_p2h_invalid
    cmpi.l #$41475350,48(a4)
    bne.s s2b_p2h_invalid
    cmpi.l #$000400f0,52(a4)
    bne.s s2b_p2h_invalid
    moveq #1,d0
    rts
s2b_p2h_invalid:
    moveq #0,d0
    rts

s2b_p2h_name:
    dc.b "AMOSPro.AGA.AGSP.S1.root.v1",0
    even
