; AGA_NATIVE_MIN_CPU: MC68020
; P2i live borrow bridge. A3 points at the persistent 16-byte root.
; Called only after the exact matching CloseScreen succeeded; P2f checked
; owner Task before teardown. The owner holds one AttemptSemaphore from
; publication until successful close (or pre-publication rollback).
; The local cell NEVER owns the allocations. Clear before releasing lock.
p2i_close_leave:
    lea p2f_root(pc),a0
    clr.l (a0)
    lea -56(a3),a4
    movea.l $0004.w,a6
    jsr -132(a6)
    moveq #0,d6
    move.l (a3),d0
    or.l 4(a3),d0
    or.l 8(a3),d0
    or.l 12(a3),d0
    bne.s p2i_close_unlock
    cmpi.w #1,14(a4)
    bne.s p2i_close_unlock
    tst.w 44(a4)
    bne.s p2i_close_unlock
    movea.l a4,a1
    jsr -606(a6)
    moveq #1,d6
p2i_close_unlock:
    clr.l 72(a4)
    movea.l a4,a0
    jsr -570(a6)
    jsr -138(a6)
    tst.l d6
    beq.s p2i_close_leave_done
    movea.l a4,a1
    jsr -690(a6)
p2i_close_leave_done:
    rts
