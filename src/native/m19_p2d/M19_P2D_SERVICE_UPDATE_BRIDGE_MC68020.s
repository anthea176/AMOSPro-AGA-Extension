; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$0DCB4..$0DD96 (226 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P2D_SERVICE_BRIDGE_INITIAL_RESULT equ 0

    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a4
    move.l #P2D_SERVICE_BRIDGE_INITIAL_RESULT,20(a4)
    move.l a5,(a4)
    lea p2d_service_root(pc),a2
    tst.l (a2)
    beq.w L_BOBS_0DD7A
    move.l (a2),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_0DD82
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
    tst.l (a0)
    bne.w L_BOBS_0DD82
    bsr.w L_BOBS_0D8D4
    tst.l d3
    beq.w L_BOBS_0DD82
L_BOBS_0DD7A:
    move.l #$00000001,20(a4)
L_BOBS_0DD82:
    move.l 20(a4),d3
    move.l #$00000000,d2
    lea 96(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
