; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$05A6A..$05B6E (260 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_RELAY_OFF_SELECTOR equ 14

relay_off_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #P0_RELAY_OFF_SELECTOR,d7
    bra.w L_BOBS_05A94
L_BOBS_05A78:
relay_read_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$0000001C,d7
    bra.w L_BOBS_05A94
L_BOBS_05A86:
relay_reset_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$0000002A,d7
    bra.w L_BOBS_05A94
L_BOBS_05A94:
relay_common:
    lea -32(a7),a7
    movea.l a7,a2
    move.l d0,(a2)
    move.l d1,4(a2)
    move.l d4,8(a2)
    move.l d5,12(a2)
    move.l d6,16(a2)
    move.l a1,20(a2)
    move.l d7,24(a2)
    move.l #$00000000,d3
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_05B62
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_05B62
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_05B62
    andi.l #$00000001,d0
    bne.w L_BOBS_05B62
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_05B62
    andi.l #$00000001,d0
    bne.w L_BOBS_05B62
    movea.l 456(a5),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_05B62
    move.l 456(a5),d0
    addi.l #$0000E45E,d0
    bcs.w L_BOBS_05B62
    move.l 24(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_05B62
    movea.l d0,a4
    andi.l #$00000001,d0
    bne.w L_BOBS_05B62
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_05B62
    move.l (a4),d0
    cmpi.l #$48E7EFEE,d0
    bne.w L_BOBS_05B62
    move.l (a2),d0
    move.l 4(a2),d1
    move.l 8(a2),d4
    move.l 12(a2),d5
    move.l 16(a2),d6
    movea.l 20(a2),a1
    jsr (a4)
L_BOBS_05B62:
relay_return:
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
