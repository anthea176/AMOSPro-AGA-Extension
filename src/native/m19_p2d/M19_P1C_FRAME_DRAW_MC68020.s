; AGA_NATIVE_MIN_CPU: MC68020
; P1c ordered frame traversal, paint and restore from source emitters:
; tools/m19_p1c_bob_priority_emit.py::PriorityTraversal.next
; tools/m19_p0j_explicit_safe_draw_emit.py::emit_frame_draw.
; BOBS+$07C98..+$07D7E = 230 executable MC68020 bytes, no data.
P1C_NEXT_CURSOR equ 32
P1C_NEXT_COUNT equ 36
P1C_NEXT_SORT_MODE equ 40
P1C_NEXT_LIST equ 160
P1C_NEXT_RECORD equ 96
P1C_NEXT_FRAME_SIZE equ 416

explicit_frame_next:
    move.l P1C_NEXT_CURSOR(a2),d0
    cmp.l P1C_NEXT_COUNT(a2),d0
    bcc.w explicit_frame_done
    addq.l #1,P1C_NEXT_CURSOR(a2)
    cmpi.l #1,P1C_NEXT_SORT_MODE(a2)
    beq.w p1c_cursor_ready
    move.l P1C_NEXT_COUNT(a2),d1
    subq.l #1,d1
    sub.l d0,d1
    move.l d1,d0
L_BOBS_07CBE:
p1c_cursor_ready:
    lsl.l #2,d0
    movea.l a2,a0
    adda.l d0,a0
    move.l P1C_NEXT_LIST(a0),d0
    andi.l #127,d0
    move.l d0,(a2)
    move.l a2,d0
    addi.l #P1C_NEXT_RECORD,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w relay_read_entry
    tst.l d3
    beq.w explicit_frame_advance
    move.l a2,d0
    addi.l #P1C_NEXT_RECORD,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w relay_checked_read_entry
    tst.l d3
    beq.w explicit_frame_return
    move.l P1C_NEXT_RECORD(a2),d0
    move.l d0,8(a2)
    move.l P1C_NEXT_RECORD+4(a2),d0
    move.l d0,12(a2)
    move.l P1C_NEXT_RECORD+8(a2),d0
    move.l d0,16(a2)
    move.l P1C_NEXT_RECORD+12(a2),d0
    move.l d0,20(a2)
    move.l 8(a2),d3
    movea.l 28(a2),a4
    bsr.w explicit_registry_prepare_entry
    tst.l d3
    beq.w explicit_frame_return
    bsr.w program_end_arm_entry
    tst.l d3
    beq.w explicit_frame_unwind
    move.l 8(a2),d3
    move.l 12(a2),d0
    move.l 16(a2),d1
    move.l 20(a2),d4
explicit_frame_paint_call:
    bsr.w explicit_safe_blit_entry
    tst.l d3
    beq.w explicit_frame_return
L_BOBS_07D52:
explicit_frame_advance:
    bra.w explicit_frame_next
L_BOBS_07D56:
explicit_frame_unwind:
    move.l 8(a2),d3
    movea.l 28(a2),a4
    bsr.w registry_free_entry
    bra.w explicit_frame_return
L_BOBS_07D66:
explicit_frame_done:
    move.l #1,4(a2)
L_BOBS_07D6E:
explicit_frame_return:
    move.l 4(a2),d3
    lea P1C_NEXT_FRAME_SIZE(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
