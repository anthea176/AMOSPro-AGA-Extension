; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p0j_end_lifecycle_emit.py::emit_end_lifecycle
; Audited bytes checked against the official M19 P2d library.
; BOBS+$06D4E..$06EAC (350 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
B7_GUARD_DIRTY_ON_CONFLICT equ 1

b7_guarded_draw_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    movea.l a7,a2
    bsr.w L_BOBS_06AB8
    move.l d3,(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_06E8E
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_06E8E
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06E8E
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06E8E
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_06E8E
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06E8E
    move.l d0,4(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06E8E
    movea.l 4(a2),a0
    tst.l (a0)
    beq.w L_BOBS_06E8E
    move.l 4(a2),d0
    cmpi.l #$00000168,d0
    bcs.w L_BOBS_06E8E
    subi.l #$00000168,d0
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_06E8E
    move.l d0,8(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06E8E
    move.l 8(a2),d0
    addi.l #$0000000B,d0
    bcs.w L_BOBS_06E8E
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06E8E
    movea.l 8(a2),a4
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_06E8E
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_06E8E
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w L_BOBS_06E8E
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_06E8E
    move.l d0,12(a2)
    move.l 12(a2),d0
    move.l 8(a2),d1
    cmp.l d1,d0
    beq.w L_BOBS_06E7E
    move.l 12(a2),d0
    lea L_BOBS_048FA(pc),a1
    move.l a1,d1
    cmp.l d1,d0
    beq.w L_BOBS_06E7E
    move.l 12(a2),d0
    lea L_BOBS_06EAC(pc),a1
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_BOBS_06E8E
L_BOBS_06E7E:
b7_draw_arm:
    lea L_BOBS_06EAC(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
    bra.w L_BOBS_06E9E
L_BOBS_06E8E:
b7_draw_fail:
    lea L_BOBS_06D36(pc),a0
    move.l #B7_GUARD_DIRTY_ON_CONFLICT,(a0)
    move.l #$00000000,(a2)
L_BOBS_06E9E:
b7_draw_return:
    move.l (a2),d3
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
