; AGA_NATIVE_MIN_CPU: MC68020
; P0i Bobs' original bank -> checked Chip -> Safe Blitter shadow route.
; Authority tools/m19_p0i_multibank_draw_emit.py::emit_multibank_paint.
; Exact BOBS+$05CF8..+$05F30, 568 bytes, 2 private routines.
; Bank selection shadow restored on both success and all failure paths.
routed_paint_one_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -160(a7),a7
    movea.l a7,a2
    move.l d0,(a2)
    move.l #0,4(a2)
    move.l #0,36(a2)
    bsr.w registry_cpu_guard
    tst.l d0
    beq.w route_return
    move.l (a2),d0
    cmpi.l #1,d0
    bcs.w route_return
    cmpi.l #64,d0
    bhi.w route_return
    move.l a2,d0
    addi.l #96,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w relay_read_entry
    tst.l d3
    beq.w route_inactive
    move.l a2,d0
    addi.l #96,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w relay_checked_read_entry
    tst.l d3
    beq.w route_return
    move.l 96(a2),d0
    move.l d0,8(a2)
    move.l 100(a2),d0
    move.l d0,12(a2)
    move.l 104(a2),d0
    move.l d0,16(a2)
    move.l 108(a2),d0
    move.l d0,20(a2)
    move.l $01C8(a5),d0
    move.l d0,40(a2)
    tst.l d0
    beq.w route_return
    movea.l 40(a2),a0
    move.l 8(a0),d0
    move.l d0,44(a2)
    tst.l d0
    beq.w route_return
    andi.l #1,d0
    bne.w route_return
    move.l 8(a2),d0
    dc.w $FE11,$F700,$031D   ; AMOS Main: Bnk.GetAdr (index 797)
    move.l a0,d0
    move.l d0,48(a2)
    cmpi.l #24,d0
    bls.w route_return
    andi.l #1,d0
    bne.w route_return
    movea.l 48(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w route_return
    move.l $05EA(a5),d0  ; Cur_Banks_A5, AMOS source +Equ.s
    move.l d0,52(a2)
    tst.l d0
    beq.w route_return
    andi.l #1,d0
    bne.w route_return
    lea bank_active_state(pc),a0
    move.l (a0),d1
    move.l d1,24(a2)
    move.l 4(a0),d1
    move.l d1,28(a2)
    move.l 8(a0),d1
    move.l d1,32(a2)
    move.l 8(a2),d1
    move.l d1,(a0)
    move.l 48(a2),d1
    move.l d1,4(a0)
    move.l 52(a2),d1
    move.l d1,8(a0)
    move.l #1,36(a2)
    move.l 8(a2),d3
    bsr.w registry_lookup_entry
    tst.l d3
    bne.w route_arm_end
    move.l 8(a2),d3
    movea.l 44(a2),a4
    bsr.w registry_prepare_entry
    tst.l d3
    beq.w route_restore
route_arm_end:
    bsr.w program_end_arm_entry
    tst.l d3
    beq.w route_unwind
    move.l 8(a2),d3
    move.l 12(a2),d0
    move.l 16(a2),d1
    move.l 20(a2),d4
    bsr.w safe_bank_blit_entry
    tst.l d3
    beq.w route_restore
    move.l #1,4(a2)
    bra.w route_restore
route_unwind:
    move.l 8(a2),d3
    movea.l 44(a2),a4
    bsr.w registry_free_entry
    bra.w route_restore
route_inactive:
    move.l #1,4(a2)
    bra.w route_return
route_restore:
    move.l 36(a2),d0
    tst.l d0
    beq.w route_return
    lea bank_active_state(pc),a0
    move.l 24(a2),d1
    move.l d1,(a0)
    move.l 28(a2),d1
    move.l d1,4(a0)
    move.l 32(a2),d1
    move.l d1,8(a0)
    move.l #0,36(a2)
route_return:
    move.l 4(a2),d3
    lea 160(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
routed_paint_all_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    movea.l a7,a2
    move.l #0,(a2)
    bsr.w frame_bank_preflight_entry
    tst.l d3
    beq.w route_all_return
    move.l #1,4(a2)
route_all_next:
    move.l 4(a2),d0
    bsr.w routed_paint_one_entry
    tst.l d3
    beq.w route_all_return
    move.l 4(a2),d0
    addq.l #1,d0
    move.l d0,4(a2)
    cmpi.l #64,d0
    bls.w route_all_next
    move.l #1,(a2)
route_all_return:
    move.l (a2),d3
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
