; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0DA30..$0DCB4 (644 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_SYSTEM_SUCCESS_FLAG equ 1

movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a4
    move.l #$00000000,20(a4)
    move.l a5,(a4)
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_0DC14
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_0DC14
    lea L_BOBS_0DA10(pc),a2
    move.l (a2),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_0DC14
    tst.l d0
    beq.w L_BOBS_0DC14
    move.l (a4),d0
    tst.l d0
    beq.w L_BOBS_0DC14
    andi.l #$00000001,d0
    bne.w L_BOBS_0DC14
    movea.l (a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    move.l (a4),d0
    addi.l #$000001CB,d0
    bcs.w L_BOBS_0DC14
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    move.l 456(a5),d0
    move.l d0,4(a4)
    move.l 4(a4),d0
    tst.l d0
    beq.w L_BOBS_0DC14
    andi.l #$00000001,d0
    bne.w L_BOBS_0DC14
    movea.l 4(a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    move.l 4(a4),d0
    addi.l #$00000023,d0
    bcs.w L_BOBS_0DC14
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    movea.l 4(a4),a0
    move.l (a0),d0
    tst.l d0
    beq.w L_BOBS_0DC14
    lea L_BOBS_0DA10(pc),a2
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_0DC14
    movea.l 4(a4),a0
    move.l 8(a0),d0
    move.l d0,12(a4)
    tst.l d0
    beq.w L_BOBS_0DC14
    andi.l #$00000001,d0
    bne.w L_BOBS_0DC14
    movea.l 4(a4),a0
    move.l 32(a0),d0
    move.l d0,8(a4)
    move.l 8(a4),d0
    tst.l d0
    beq.w L_BOBS_0DC14
    andi.l #$00000001,d0
    bne.w L_BOBS_0DC14
    movea.l 8(a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    move.l 8(a4),d0
    addi.l #$00000017,d0
    bcs.w L_BOBS_0DC14
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    lea L_BOBS_0DA10(pc),a2
    move.l 8(a2),d0
    move.l 8(a4),d1
    cmp.l d1,d0
    bne.w L_BOBS_0DC14
    movea.l 8(a4),a0
    move.l 20(a0),d0
    andi.l #$00000001,d0
    beq.w L_BOBS_0DBFA
    movea.l 8(a4),a0
    move.l 12(a0),d0
    move.l d0,16(a4)
    move.l 16(a4),d0
    tst.l d0
    beq.w L_BOBS_0DC14
    andi.l #$00000001,d0
    bne.w L_BOBS_0DC14
    movea.l 16(a4),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    movea.l 16(a4),a0
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_BOBS_0DC14
    movea.l 8(a4),a0
    move.l 20(a0),d0
    andi.l #$FFFFFFFE,d0
    move.l d0,20(a0)
L_BOBS_0DBFA:
    movea.l 12(a4),a6
    jsr -228(a6)
    bsr.w L_BOBS_0BE32
    tst.l d3
    beq.w L_BOBS_0DC14
    move.l #P2D_SYSTEM_SUCCESS_FLAG,20(a4)
L_BOBS_0DC14:
    move.l 20(a4),d3
    move.l #$00000000,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
L_BOBS_0DC28:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a4
    move.l #$00000000,20(a4)
    bsr.w L_BOBS_0DA30
    tst.l d3
    beq.w L_BOBS_0DCA0
    bsr.w L_BOBS_0D802
    move.l d3,20(a4)
    bra.w L_BOBS_0DC50
L_BOBS_0DC50:
    move.l 20(a4),d3
    move.l #$00000000,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
L_BOBS_0DC64:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a4
    move.l #$00000000,20(a4)
    bsr.w L_BOBS_0DA30
    tst.l d3
    beq.w L_BOBS_0DCA0
    bsr.w L_BOBS_0D820
    move.l d3,20(a4)
    bra.w L_BOBS_0DC8C
L_BOBS_0DC8C:
    move.l 20(a4),d3
    move.l #$00000000,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
L_BOBS_0DCA0:
    move.l 20(a4),d3
    move.l #$00000000,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
