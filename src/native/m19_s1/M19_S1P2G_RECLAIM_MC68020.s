; AGA_NATIVE_MIN_CPU: MC68020
; Source-only candidate: reclaim after actual successful CloseScreen.
; Uses P2f root and P2e. Included before p2f_root in disposable source.
; No public producer. Future producer MUST own two separate AllocVec
; allocations (P2e Chip and 28-byte record), with a persistent receipt.
; Only OS-managed SimpleSprite 2/3; no private pointer export, external
; ChangeSprite, custom DMA/Copper publication or concurrent owner calls.
; Closed-view predicate is deliberately restrictive, pending real gates.
; root+12 becomes zero ONLY on receipt of successful CloseScreen.
; FreeVec is not a result of FreeSprite alone or of a caller's Screen=0.

p2g_end_close:
    jsr -66(a6)           ; Intuition CloseScreen, real BOOL in D0
    bsr.w p2g_closed
    tst.l d0
    beq.w p2g_end_pending
    clr.l (a2)
    bra.l L_LEGACY_CLOSE_CORE_000D4
p2g_end_pending:
    bra.l L_LEGACY_CLOSE_CORE_00110

p2g_public_close:
    bsr.l ENTRY_LEGACY_HELPER_052CA_00000
    ; Helper ends with CloseScreen then RTS, preserving D0 result.
    bsr.w p2g_closed
    tst.l d0
    beq.w p2g_close_pending
    clr.l (a2)
    bra.l L_LEGACY_CLOSE_TARGET_00096
p2g_close_pending:
    bra.l L_LEGACY_CLOSE_TARGET_000D2

p2g_closed:
    ; A2=State, A5=owner, (A2)=screen BEFORE legacy clear.
    ; D0=real CloseScreen result. Preserve all except decision D0.
    movem.l d1-d7/a0-a6,-(sp)
    move.l d0,d7
    lea p2f_root(pc),a3
    tst.l (a3)
    beq.w p2g_continue
    move.l a5,d0
    cmp.l 4(a3),d0
    bne.w p2g_continue
    move.l a2,d0
    cmp.l 8(a3),d0
    bne.w p2g_continue
    move.l (a2),d0
    beq.w p2g_continue
    cmp.l 12(a3),d0
    bne.w p2g_continue
    tst.l d7
    beq.w p2g_close_failed
    clr.l 12(a3)         ; durable receipt of this successful close
    movea.l a3,a0
    movea.l 8(a2),a1     ; still-open graphics.library
    bsr.w AGSP_P2G_RECLAIM
    ; If pending, keep root and both allocations, but finish closed screen.
p2g_continue:
    moveq #1,d0
    bra.w p2g_closed_return
p2g_close_failed:
    ; Screen/graphics/intuition remain live; retry, not blind clear.
    moveq #0,d0
p2g_closed_return:
    movem.l (sp)+,d1-d7/a0-a6
    rts

AGSP_P2G_RECLAIM:
    ; A0=pinned root, A1=live GfxBase (independent open on later retry).
    ; D0=1 reclaimed/already empty; 0 pending. D2-D7/A0-A6 preserved.
    ; Never dereference former ViewPort after root screen receipt=0.
    movem.l d2-d7/a0-a6,-(sp)
    movea.l a0,a2
    movea.l a1,a5
    move.l a2,d0
    beq.w p2g_reject
    btst #0,d0
    bne.w p2g_reject
    move.l (a2),d0
    beq.w p2g_done
    tst.l 12(a2)
    bne.w p2g_reject
    btst #0,d0
    bne.w p2g_reject
    movea.l d0,a3
    move.l 12(a3),d7
    beq.w p2g_validate
    cmpi.l #4,d7
    bne.w p2g_reject
    bsr.w p2g_idle_view
    tst.l d0
    beq.w p2g_reject
p2g_validate:
    movea.l a3,a0
    movea.l a5,a1
    bsr.w AGSP_P2E_RETIRE ; validates private block; flags=4 waits 2 TOF + scan
    tst.l d7
    beq.w p2g_unpublished
    cmpi.l #1,d0
    bne.w p2g_reject
    bsr.w p2g_idle_view
    tst.l d0
    beq.w p2g_reject
    bra.w p2g_release
p2g_unpublished:
    cmpi.l #2,d0
    bne.w p2g_reject
p2g_release:
    ; Pinned, separate private allocations; producer must retain provenance.
    movea.l (a3),a4
    move.l a4,d0
    cmp.l a3,d0
    beq.w p2g_reject
    move.l a3,d1
    cmp.l d0,d1
    bcs.w p2g_record_below
    add.l 4(a3),d0
    bcs.w p2g_reject
    cmp.l d0,d1
    bcs.w p2g_reject
    bra.w p2g_clear
p2g_record_below:
    addi.l #28,d1
    bcs.w p2g_reject
    cmp.l d1,d0
    bcs.w p2g_reject
p2g_clear:
    ; Clear durable owner receipt BEFORE release; no second attempt can
    ; free either allocation. No waits or future pointer publication here.
    clr.l (a2)
    clr.l 4(a2)
    clr.l 8(a2)
    clr.l 12(a2)
    movea.l $0004.w,a6
    movea.l a4,a1
    jsr -690(a6)          ; FreeVec exact P2a AllocVec base
    movea.l a3,a1
    jsr -690(a6)          ; FreeVec separate owner record
p2g_done:
    moveq #1,d0
    bra.w p2g_return
p2g_reject:
    moveq #0,d0
p2g_return:
    movem.l (sp)+,d2-d7/a0-a6
    rts

p2g_idle_view:
    ; NDK copinit: sprstrtup +88, wait_forever +164, sprstop +176.
    ; P2d r2 observed LOF=SHF=copinit+164, COP2/3=copinit+176
    ; and null ActiView. Require terminal wait shape too (not yet observed).
    ; No dynamic list walk or hardware/global DMA write.
    move.l a5,d0
    beq.w p2g_view_no
    btst #0,d0
    bne.w p2g_view_no
    cmpi.w #212,18(a5)
    bcs.w p2g_view_no
    cmpi.w #39,20(a5)
    bcs.w p2g_view_no
    cmpi.w #40,20(a5)
    bhi.w p2g_view_no
    tst.l 34(a5)
    bne.w p2g_view_no
    movea.l 38(a5),a0
    move.l a0,d0
    beq.w p2g_view_no
    btst #0,d0
    bne.w p2g_view_no
    addi.l #164,d0
    bcs.w p2g_view_no
    cmp.l 50(a5),d0
    bne.w p2g_view_no
    cmp.l 54(a5),d0
    bne.w p2g_view_no
    cmpi.l #$fffffffe,164(a0)
    bne.w p2g_view_no
    addi.l #12,d0
    bcs.w p2g_view_no
    moveq #0,d1
    move.w 106(a0),d1
    swap d1
    move.w 110(a0),d1
    cmp.l d0,d1
    bne.w p2g_view_no
    moveq #0,d1
    move.w 114(a0),d1
    swap d1
    move.w 118(a0),d1
    cmp.l d0,d1
    bne.w p2g_view_no
    moveq #0,d1
    move.b 166(a5),d1
    andi.b #12,d1
    bne.w p2g_view_no
    movea.l 208(a5),a1
    move.l a1,d1
    beq.w p2g_view_no
    btst #0,d1
    bne.w p2g_view_no
    addi.l #32,d1
    bcs.w p2g_view_no
    tst.l 8(a1)
    bne.w p2g_view_no
    tst.l 12(a1)
    bne.w p2g_view_no
    moveq #1,d0
    rts
p2g_view_no:
    moveq #0,d0
    rts
