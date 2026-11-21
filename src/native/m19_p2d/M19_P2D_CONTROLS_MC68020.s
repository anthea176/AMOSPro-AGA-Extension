; AGA_NATIVE_MIN_CPU: MC68020
; M19 P2d - hand-maintained Bob Auto Update / guarded Swap / Close.
; SOURCE OF AUTHORITY: tools/m19_p2d_bob_auto_update_emit.py (same P2d).
; Integrated at BOBS +$0B58C, immediately before B8 service at +$0B72A.
; Machine-code instructions are explicit; the 12 state bytes are DATA.
; Do not install an edited .Lib without a dedicated Runtime/Compiler gate.
;
; This is an INCLUDE file for M19_P2D_BOBS_MC68020.s.
; Externals: p1c_context, frame_guard_context_entry,
; frame_guard_state, b8_b7_arm_end_nodraw_entry,
; p2d_service_root, p2d_service_update, guarded_swap_entry.

P2D_FRAME_BYTES        equ 48
P2D_SAVED_A2           equ 24
P2D_CTX_SCREEN        equ 12
P2D_MODE_OWNER        equ 0
P2D_MODE_STATE        equ 4
P2D_MODE_SCREEN       equ 8
P2D_OBJECT_OFFSET     equ $DE5E
P2D_OBJECT_COUNT      equ 64
P2D_OBJECT_SIZE       equ 24
P2D_OBJECT_LAST       equ (P2D_OBJECT_COUNT*P2D_OBJECT_SIZE)-1
P2D_OBJECT_ACTIVE     equ 16
P2D_AMOS_STATE_A5     equ $01C8
P2D_EXEC_TYPEOFMEM    equ -534

p2d_public_auto_update:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P2D_FRAME_BYTES(a7),a7
    move.l a2,P2D_SAVED_A2(a7)
    movea.l a7,a2
    cmpi.l #1,d3
    bhi.w p2d_refused
    move.l d3,d7
    bsr.w p1c_context
    move.l a0,d0
    beq.w p2d_refused
    bsr.w frame_guard_context_entry
    tst.l d3
    beq.w p2d_refused
    lea frame_guard_state(pc),a0
    tst.l (a0)
    bne.w p2d_refused
    lea p2d_mode(pc),a0
    tst.l (a0)
    beq.w p2d_set_mode
    move.l a5,d1
    cmp.l (a0),d1
    bne.w p2d_refused

L_BOBS_0B5D6:
p2d_set_mode:
    tst.l d7
    beq.w p2d_disable
    bsr.w b8_b7_arm_end_nodraw_entry
    tst.l d3
    beq.w p2d_refused
    lea p2d_mode(pc),a0
    move.l (a2),P2D_MODE_STATE(a0)
    move.l P2D_CTX_SCREEN(a2),P2D_MODE_SCREEN(a0)
    move.l a5,(a0)
    bra.w p2d_set_done

L_BOBS_0B5FA:
p2d_disable:
    move.l #0,(a0)

L_BOBS_0B600:
p2d_set_done:
    moveq #1,d3
    bra.w p2d_return

ENTRY_BOBS_0B606:
p2d_public_swap:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -P2D_FRAME_BYTES(a7),a7
    move.l a2,P2D_SAVED_A2(a7)
    movea.l a7,a2
    lea p2d_mode(pc),a0
    tst.l (a0)
    beq.w p2d_swap
    move.l a5,d1
    cmp.l (a0),d1
    bne.w p2d_swap
    bsr.w frame_guard_context_entry
    tst.l d3
    beq.w p2d_refused
    lea p2d_mode(pc),a0
    move.l (a2),d0
    cmp.l P2D_MODE_STATE(a0),d0
    bne.w p2d_refused
    move.l P2D_CTX_SCREEN(a2),d0
    cmp.l P2D_MODE_SCREEN(a0),d0
    bne.w p2d_refused
    lea frame_guard_state(pc),a0
    tst.l (a0)
    bne.w p2d_swap
    lea p2d_service_root(pc),a0
    tst.l (a0)
    bne.w p2d_update

    ; Pool bind only when an active, validated Bob exists.
    move.l (a2),d4
    addi.l #P2D_OBJECT_OFFSET,d4
    bcs.w p2d_refused
    movea.l d4,a1
    movea.l $0004.w,a6
    jsr P2D_EXEC_TYPEOFMEM(a6)
    tst.l d0
    beq.w p2d_refused
    move.l d4,d0
    addi.l #P2D_OBJECT_LAST,d0
    bcs.w p2d_refused
    movea.l d0,a1
    jsr P2D_EXEC_TYPEOFMEM(a6)
    tst.l d0
    beq.w p2d_refused
    movea.l d4,a0
    move.l #P2D_OBJECT_COUNT,d0

L_BOBS_0B69A:
p2d_scan:
    tst.l P2D_OBJECT_ACTIVE(a0)
    bne.w p2d_update
    adda.l #P2D_OBJECT_SIZE,a0
    subq.l #1,d0
    bne.w p2d_scan
    bra.w p2d_swap

L_BOBS_0B6B2:
p2d_update:
    movea.l P2D_SAVED_A2(a7),a2
    bsr.w p2d_service_update
    tst.l d3
    beq.w p2d_refused

L_BOBS_0B6C0:
p2d_swap:
    movea.l P2D_SAVED_A2(a7),a2
    bsr.w guarded_swap_entry
    bra.w p2d_return

L_BOBS_0B6CC:
p2d_refused:
    moveq #0,d3

L_BOBS_0B6CE:
p2d_return:
    lea P2D_FRAME_BYTES(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts

; Previously entirely DC.B in the generic restored listing.
; Recovered instruction for instruction from the P2d Python emitter.
p2d_close:
    lea p2d_mode(pc),a0
    tst.l (a0)
    beq.w p2d_close_return
    move.l a5,d1
    cmp.l (a0),d1
    bne.w p2d_close_return
    move.l P2D_AMOS_STATE_A5(a5),d0
    beq.w p2d_clear_mode
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr P2D_EXEC_TYPEOFMEM(a6)
    tst.l d0
    beq.w p2d_close_return
    movea.l P2D_AMOS_STATE_A5(a5),a1
    tst.l (a1)
    bne.w p2d_close_return
p2d_clear_mode:
    lea p2d_mode(pc),a0
    move.l #0,(a0)
p2d_close_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts

L_BOBS_0B71E:
p2d_mode:
    dcb.b 12,0
