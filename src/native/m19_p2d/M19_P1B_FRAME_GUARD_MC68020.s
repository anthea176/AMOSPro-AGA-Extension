; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$06902..$06D36 (1076 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P1B_FRAME_GATE_INITIAL_RESULT equ 0

p1b_frame_body:
    movea.l a7,a2
    move.l #P1B_FRAME_GATE_INITIAL_RESULT,4(a2)
    bsr.w L_BOBS_05F30
    tst.l d3
    beq.w L_BOBS_069F6
    move.l 456(a5),d0
    move.l d0,24(a2)
    tst.l d0
    beq.w L_BOBS_069F6
    movea.l 24(a2),a0
    move.l 8(a0),d0
    move.l d0,28(a2)
    tst.l d0
    beq.w L_BOBS_069F6
    andi.l #$00000001,d0
    bne.w L_BOBS_069F6
    move.l #$00000001,(a2)
L_BOBS_06946:
p1b_frame_next:
    move.l (a2),d0
    cmpi.l #$00000040,d0
    bhi.w L_BOBS_069EE
    move.l a2,d0
    addi.l #$00000060,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05A78
    tst.l d3
    beq.w L_BOBS_069D4
    move.l a2,d0
    addi.l #$00000060,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05BAC
    tst.l d3
    beq.w L_BOBS_069F6
    move.l 96(a2),d0
    move.l d0,8(a2)
    move.l 100(a2),d0
    move.l d0,12(a2)
    move.l 104(a2),d0
    move.l d0,16(a2)
    move.l 108(a2),d0
    move.l d0,20(a2)
    move.l 8(a2),d3
    movea.l 28(a2),a4
    bsr.w L_BOBS_06596
    tst.l d3
    beq.w L_BOBS_069F6
    bsr.w L_BOBS_04828
    tst.l d3
    beq.w L_BOBS_069DE
    move.l 8(a2),d3
    move.l 12(a2),d0
    move.l 16(a2),d1
    move.l 20(a2),d4
p1b_frame_paint_call:
    bsr.w L_BOBS_07DFE
    tst.l d3
    beq.w L_BOBS_069F6
L_BOBS_069D4:
p1b_frame_advance:
    move.l (a2),d0
    addq.l #1,d0
    move.l d0,(a2)
    bra.w L_BOBS_06946
L_BOBS_069DE:
p1b_frame_unwind:
    move.l 8(a2),d3
    movea.l 28(a2),a4
    bsr.w L_BOBS_04470
    bra.w L_BOBS_069F6
L_BOBS_069EE:
p1b_frame_done:
    move.l #$00000001,4(a2)
L_BOBS_069F6:
p1b_frame_return:
    move.l 4(a2),d3
    lea 160(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_06A06:
frame_guard_context_entry:
    move.l #$00000000,d3
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_06AB6
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_06AB6
    andi.l #$00000001,d0
    bne.w L_BOBS_06AB6
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_06AB6
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06AB6
    move.l d0,(a2)
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06AB6
    movea.l (a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06AB6
    movea.l (a2),a0
    move.l (a0),d0
    tst.l d0
    beq.w L_BOBS_06AB6
    move.l d0,12(a2)
    move.l 32(a0),d0
    tst.l d0
    beq.w L_BOBS_06AB6
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06AB6
    move.l d0,4(a2)
    movea.l 4(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06AB6
    movea.l 4(a2),a0
    move.l 8(a0),d0
    cmpi.l #$00000001,d0
    bhi.w L_BOBS_06AB6
    move.l d0,8(a2)
    move.l #$00000001,d3
L_BOBS_06AB6:
guard_context_return:
    rts
L_BOBS_06AB8:
guarded_frame_draw_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -48(a7),a7
    movea.l a7,a2
    bsr.w L_BOBS_06A06
    tst.l d3
    beq.w L_BOBS_06B6E
    lea L_BOBS_06D36(pc),a0
    move.l (a0),d0
    tst.l d0
    beq.w L_BOBS_06B24
    cmpi.l #$00000002,d0
    bne.w L_BOBS_06B68
    move.l 4(a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_06B68
    move.l 8(a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06B68
    move.l 12(a0),d0
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06B68
    move.l 16(a0),d0
    move.l 8(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06B68
    move.l 20(a0),d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06B68
L_BOBS_06B24:
guard_draw_arm:
    lea L_BOBS_06D36(pc),a0
    move.l #$00000001,(a0)
    move.l a5,4(a0)
    move.l (a2),d0
    move.l d0,8(a0)
    move.l 4(a2),d0
    move.l d0,12(a0)
    move.l 8(a2),d0
    move.l d0,16(a0)
    move.l 12(a2),d0
    move.l d0,20(a0)
    bsr.w L_BOBS_068FA
    tst.l d3
    beq.w L_BOBS_06B6E
    lea L_BOBS_06D36(pc),a0
    move.l #$00000002,(a0)
    bra.w L_BOBS_06B6E
L_BOBS_06B68:
guard_draw_reject:
    move.l #$00000000,d3
L_BOBS_06B6E:
guard_draw_return:
    lea 48(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_06B7A:
guarded_swap_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -48(a7),a7
    movea.l a7,a2
    bsr.w L_BOBS_06A06
    tst.l d3
    beq.w L_BOBS_06C92
    lea L_BOBS_06D36(pc),a0
    move.l (a0),d0
    cmpi.l #$00000001,d0
    beq.w L_BOBS_06C86
    tst.l d0
    beq.w L_BOBS_06BF0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_06C86
    move.l 4(a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_06C86
    move.l 8(a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06C86
    move.l 12(a0),d0
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06C86
    move.l 16(a0),d0
    move.l 8(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06C86
    move.l 20(a0),d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06C86
L_BOBS_06BF0:
guard_swap_target:
    move.l (a2),d0
    addi.l #$000009E0,d0
    bcs.w L_BOBS_06C86
    andi.l #$00000001,d0
    bne.w L_BOBS_06C86
    move.l (a2),d0
    addi.l #$000009E0,d0
    movea.l d0,a4
    move.l d0,16(a2)
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06C86
    move.l 16(a2),d0
    addi.l #$00000009,d0
    bcs.w L_BOBS_06C86
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06C86
    movea.l 16(a2),a4
    move.l (a4),d0
    cmpi.l #$48E7EFFE,d0
    bne.w L_BOBS_06C86
    move.w 4(a4),d0
    cmpi.w #$7600,d0
    bne.w L_BOBS_06C86
    move.l 6(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_06C86
    jsr (a4)
    move.l d3,20(a2)
    tst.l d3
    beq.w L_BOBS_06C8E
    lea L_BOBS_06D36(pc),a0
    move.l #$00000000,(a0)
    bra.w L_BOBS_06C8E
L_BOBS_06C86:
guard_swap_refuse:
    move.l #$00000000,20(a2)
L_BOBS_06C8E:
guard_swap_restore:
    move.l 20(a2),d3
L_BOBS_06C92:
guard_swap_return:
    lea 48(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_06C9E:
guarded_close_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_06D30
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_06D30
    andi.l #$00000001,d0
    bne.w L_BOBS_06D30
    bsr.w L_BOBS_0479C
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_06D30
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06D30
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06D30
    movea.l 456(a5),a1
    tst.l (a1)
    bne.w L_BOBS_06D30
    lea L_BOBS_06D36(pc),a0
    move.l 4(a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_06D30
    move.l #$00000000,(a0)
    move.l #$00000000,4(a0)
    move.l #$00000000,8(a0)
    move.l #$00000000,12(a0)
    move.l #$00000000,16(a0)
    move.l #$00000000,20(a0)
L_BOBS_06D30:
guard_close_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts
