; AGA_NATIVE_MIN_CPU: MC68020
; S1-P2k transaction root, no AP20 export, no Sprite/DMA access.
; Exec V39+, task context, not already forbidden/disabled.
; All clients must use this private protocol, never cache an unlocked root,
; use ObtainSemaphore on this name, or access it from interrupt context.
; Entry 0: D0=0 lookup only, D0=1 lookup or create.
; Return D0=locked root address or 0; D1=0 success, 1 absent, 2 busy,
; 3 incompatible/stale pointer, 4 allocation failed, 5 bad args/Exec/task.
; 6 unfinished borrow tag (never steal it); 2 OS semaphore busy.
; Entry 4: A0=locked root; D0=1 released or 0 rejected; D1 same reasons.
; D2-D7/A0-A6 preserved. One matching Leave per successful Enter.
; Anchor is independent of all executable units and has no code pointers.
; NDK SS_SIZE=46, SS_NESTCOUNT=14, SS_OWNER=40, SS_QUEUECOUNT=44.
; +48 AGSP magic, +52 schema/size, +56 P2f/P2g 16-byte root,
; +72 borrowing Task (one native transaction), +76 inline name, 112 bytes.
; +104 lifetime Task for live Screen, independent of transaction borrower.
; Schema v2 at the SAME name: old v1 is incompatible, never bypassed.
; Empty root = ALL four longs zero. Pending roots survive code unload.
; A forced task death inside a native call remains quarantined, no auto-steal.
; Never hold a borrow across a returned AMOS instruction.
    bra.w p2h_enter
    bra.w p2h_leave

p2h_enter:
    movem.l d2-d7/a0-a6,-(sp)
    move.l d0,d2
    moveq #0,d5
    moveq #5,d4
    suba.l a3,a3
    cmpi.l #1,d2
    bhi.w p2h_enter_return
    bsr.w p2h_exec_task
    tst.l d0
    beq.w p2h_enter_return
    move.l d0,d3
p2h_lookup:
    jsr -132(a6)          ; Forbid, no waits/allocations in this span
    bsr.w p2h_find
    tst.l d0
    bne.w p2h_found
    tst.l d2
    beq.w p2h_absent
    move.l a3,d0
    bne.w p2h_publish
    jsr -138(a6)          ; Permit before AllocVec
    move.l #112,d0
    move.l #$00010001,d1  ; MEMF_PUBLIC | MEMF_CLEAR
    jsr -684(a6)
    tst.l d0
    beq.w p2h_oom
    movea.l d0,a3
    move.l #$41475350,48(a3)
    move.l #$00020070,52(a3)
    lea 76(a3),a1
    move.l a1,10(a3)      ; name lives inside persistent allocation
    lea p2h_name(pc),a0
p2h_copy_name:
    move.b (a0)+,d0
    move.b d0,(a1)+
    tst.b d0
    bne.w p2h_copy_name
    bra.w p2h_lookup      ; race-safe second lookup before publication
p2h_publish:
    movea.l a3,a4
    movea.l a4,a1
    jsr -600(a6)          ; AddSemaphore initializes and publishes
    suba.l a3,a3          ; anchor now belongs to named registry
    bra.w p2h_try_lock
p2h_found:
    movea.l d0,a4
    bsr.w p2h_validate
    tst.l d0
    beq.w p2h_bad_anchor
p2h_try_lock:
    tst.l 72(a4)
    bne.w p2k_unfinished
    tst.l 40(a4)         ; no recursion even if OS owner is current Task
    bne.w p2h_busy
    movea.l a4,a0
    jsr -576(a6)          ; AttemptSemaphore: never block under Forbid
    tst.l d0
    beq.w p2h_busy
    move.l d3,72(a4)
    lea 56(a4),a0
    move.l a0,d5
    moveq #0,d4
    bra.w p2h_enter_permit
p2h_absent:
    moveq #1,d4
    bra.w p2h_enter_permit
p2h_bad_anchor:
    moveq #3,d4
    bra.w p2h_enter_permit
p2k_unfinished:
    moveq #6,d4
    bra.w p2h_enter_permit
p2h_busy:
    moveq #2,d4
p2h_enter_permit:
    jsr -138(a6)
    move.l a3,d0
    beq.w p2h_enter_return
    movea.l a3,a1        ; losing unpublished allocation, not registry
    jsr -690(a6)
    bra.w p2h_enter_return
p2h_oom:
    moveq #4,d4
p2h_enter_return:
    move.l d5,d0
    move.l d4,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts

p2h_leave:
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a3
    suba.l a2,a2
    moveq #0,d5
    moveq #5,d4
    move.l a3,d0
    beq.w p2h_leave_return
    btst #0,d0
    bne.w p2h_leave_return
    bsr.w p2h_exec_task
    tst.l d0
    beq.w p2h_leave_return
    move.l d0,d3
    jsr -132(a6)
    bsr.w p2h_find
    tst.l d0
    beq.w p2h_leave_bad
    movea.l d0,a4
    bsr.w p2h_validate
    tst.l d0
    beq.w p2h_leave_bad
    lea 56(a4),a0
    cmpa.l a0,a3
    bne.w p2h_leave_bad
    cmp.l 72(a4),d3
    bne.w p2h_leave_busy
    cmp.l 40(a4),d3
    bne.w p2h_leave_busy
    cmpi.w #1,14(a4)      ; one exact private borrow, never claim nested release
    bne.w p2h_leave_busy
    tst.w 44(a4)           ; no foreign waiter in the private protocol
    bne.w p2h_leave_busy
    ; Only remove a truly empty and exclusively held registry. Never
    ; free a semaphore with waiters or an extra recursive OS lock.
    tst.l 56(a4)
    bne.w p2h_unlock
    tst.l 60(a4)
    bne.w p2h_unlock
    tst.l 64(a4)
    bne.w p2h_unlock
    tst.l 68(a4)
    bne.w p2h_unlock
    tst.l 104(a4)
    bne.w p2h_unlock
    movea.l a4,a1
    jsr -606(a6)          ; RemSemaphore while exclusively locked
    movea.l a4,a2        ; no client can find it after Permit
p2h_unlock:
    clr.l 72(a4)
    movea.l a4,a0
    jsr -570(a6)          ; ReleaseSemaphore, matching successful Attempt
    moveq #1,d5
    moveq #0,d4
    bra.w p2h_leave_permit
p2h_leave_bad:
    moveq #3,d4
    bra.w p2h_leave_permit
p2h_leave_busy:
    moveq #2,d4
p2h_leave_permit:
    jsr -138(a6)
    move.l a2,d0
    beq.w p2h_leave_return
    movea.l a2,a1
    jsr -690(a6)          ; removed, unlocked, no registered borrower
p2h_leave_return:
    move.l d5,d0
    move.l d4,d1
    movem.l (sp)+,d2-d7/a0-a6
    rts

p2h_exec_task:
    movea.l $0004.w,a6
    move.l a6,d0
    beq.w p2h_exec_bad
    btst #0,d0
    bne.w p2h_exec_bad
    cmpi.w #39,20(a6)
    bcs.w p2h_exec_bad
    cmpi.w #690,16(a6)
    bcs.w p2h_exec_bad
    suba.l a1,a1
    jsr -294(a6)          ; FindTask(NULL)
    rts
p2h_exec_bad:
    moveq #0,d0
    rts

p2h_find:
    lea p2h_name(pc),a1
    jsr -594(a6)
    rts

p2h_validate:
    ; FindSemaphore gives a live named node under Forbid. Check inline
    ; name and ABI before touching root fields. TypeOfMem is not proof
    ; of an allocation's exact size; the private namespace is a contract.
    move.l a4,d0
    beq.w p2h_invalid
    btst #0,d0
    bne.w p2h_invalid
    addi.l #111,d0
    bcs.w p2h_invalid
    movea.l d0,a1
    jsr -534(a6)
    tst.l d0
    beq.w p2h_invalid
    movea.l a4,a1
    jsr -534(a6)
    tst.l d0
    beq.w p2h_invalid
    cmpi.b #15,8(a4)     ; NT_SIGNALSEM
    bne.w p2h_invalid
    lea 76(a4),a0
    move.l a0,d0
    cmp.l 10(a4),d0
    bne.w p2h_invalid
    cmpi.l #$41475350,48(a4)
    bne.w p2h_invalid
    cmpi.l #$00020070,52(a4)
    bne.w p2h_invalid
    moveq #1,d0
    rts
p2h_invalid:
    moveq #0,d0
    rts

p2h_name:
    dc.b "AMOSPro.AGA.AGSP.S1.root.v1",0
    even
