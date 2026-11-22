; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_b8_b7_hook_emit.py::emit_b8_b7_hooks
; Audited bytes checked against the official M19 P2d library.
; BOBS+$06FA6..$071E8 (578 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
B7_B8_DRAW_FAIL_FLAG equ 1

b7_multiframe_draw_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_070BE
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_070BE
    andi.l #$00000001,d0
    bne.w L_BOBS_070BE
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_070BE
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_070BE
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_070BE
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_070BE
    movea.l 456(a5),a0
    tst.l (a0)
    beq.w L_BOBS_070BE
    move.l 456(a5),d0
    cmpi.l #$00000168,d0
    bcs.w L_BOBS_070BE
    subi.l #$00000168,d0
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_070BE
    movea.l d0,a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_070BE
    move.l a4,d0
    addi.l #$0000000B,d0
    bcs.w L_BOBS_070BE
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_070BE
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_070BE
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_070BE
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w L_BOBS_070BE
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_070BE
    move.l a4,d1
    cmp.l d1,d0
    beq.w L_BOBS_070B6
    lea L_BOBS_048FA(pc),a1
    move.l a1,d1
    cmp.l d1,d0
    beq.w L_BOBS_070B6
    lea L_BOBS_06EAC(pc),a1
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_BOBS_070BE
    lea L_BOBS_048FA(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
L_BOBS_070B6:
b7_multiframe_forward:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    bra.w L_BOBS_06D4E
L_BOBS_070BE:
b7_multiframe_refuse:
    lea L_BOBS_06D36(pc),a0
    move.l #B7_B8_DRAW_FAIL_FLAG,(a0)
    move.l #$00000000,d3
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_070D6:
b7m2_close_reset_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_070F2
    bsr.w L_BOBS_05A86
    tst.l d3
    beq.w L_BOBS_070F2
    bsr.w L_BOBS_06C9E
L_BOBS_070F2:
b7m2_close_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts
ENTRY_BOBS_070F8:
b8_b7_draw_trampoline_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    move.l #$00000000,(a7)
    lea L_BOBS_0735C(pc),a0
    move.l (a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_07140
    tst.l d0
    beq.w L_BOBS_07140
    lea L_BOBS_071EE(pc),a4
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_07140
    move.l a4,d1
    cmp.l d1,d0
    bne.w L_BOBS_07140
    lea L_BOBS_06EAC(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
L_BOBS_07140:
b8_b7_draw_call:
    bsr.w L_BOBS_06FA6
    move.l d3,(a7)
    lea L_BOBS_0735C(pc),a0
    move.l (a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_07180
    tst.l d0
    beq.w L_BOBS_07180
    lea L_BOBS_06EAC(pc),a4
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_07180
    move.l a4,d1
    cmp.l d1,d0
    bne.w L_BOBS_07180
    lea L_BOBS_071EE(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
L_BOBS_07180:
b8_b7_draw_return:
    move.l (a7),d3
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
ENTRY_BOBS_0718E:
b8_b7_close_trampoline_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w L_BOBS_070D6
    lea L_BOBS_0735C(pc),a0
    move.l (a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_071E8
    tst.l d0
    beq.w L_BOBS_071E8
    movea.l 4(a0),a4
    move.l a4,d0
    tst.l d0
    beq.w L_BOBS_071E8
    jsr (a4)
    tst.l d3
    beq.w L_BOBS_071E8
    bsr.w L_BOBS_07348
    lea L_BOBS_071EE(pc),a4
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_071E8
    move.l a4,d1
    cmp.l d1,d0
    bne.w L_BOBS_071E8
    lea L_BOBS_06EAC(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
