; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$046D4..$048FA (550 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_PRE_CLOSE_STATE_ZERO equ 0

screen_preclose_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l #$00000000,(a2)
    move.l #$00000000,4(a2)
    move.l #P0_PRE_CLOSE_STATE_ZERO,8(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_0478C
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_0478C
    andi.l #$00000001,d0
    bne.w L_BOBS_0478C
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_04776
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_0478C
    move.l d0,(a2)
    move.l d0,d1
    addi.l #$00000008,d1
    bcs.w L_BOBS_0478C
    move.l d1,12(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0478C
    movea.l 12(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_0478C
    movea.l (a2),a0
    move.l 8(a0),d0
    tst.l d0
    beq.w L_BOBS_04776
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_0478C
    move.l d0,4(a2)
L_BOBS_04776:
screen_preclose_registry:
    movea.l 4(a2),a4
    bsr.w L_BOBS_04512
    tst.l d3
    beq.w L_BOBS_0478C
    move.l #$00000001,8(a2)
L_BOBS_0478C:
screen_preclose_return:
    move.l 8(a2),d3
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_0479C:
screen_close_bridge_entry:
    movem.l d0-d7/a0-a6,-(a7)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_04822
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_04822
    andi.l #$00000001,d0
    bne.w L_BOBS_04822
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_04822
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_04822
    addi.l #$00000638,d0
    bcs.w L_BOBS_04822
    movea.l d0,a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_04822
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_04822
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_04822
    move.l 8(a4),d0
    cmpi.l #$600001D0,d0
    bne.w L_BOBS_04822
    bsr.w L_BOBS_046D4
    tst.l d3
    beq.w L_BOBS_04822
    jsr (a4)
L_BOBS_04822:
bridge_return:
    movem.l (a7)+,d0-d7/a0-a6
    rts
L_BOBS_04828:
program_end_arm_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$00000000,d3
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_048F2
    lea L_BOBS_046CC(pc),a0
    move.l (a0),d0
    move.l a5,d1
    cmp.l d1,d0
    bne.w L_BOBS_048F2
    tst.l 4(a0)
    beq.w L_BOBS_048F2
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_048F2
    andi.l #$00000001,d0
    bne.w L_BOBS_048F2
    move.l 456(a5),d0
    cmpi.l #$00000168,d0
    bcs.w L_BOBS_048F2
    subi.l #$00000168,d0
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_048F2
    movea.l d0,a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_048F2
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_048F2
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_048F2
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w L_BOBS_048F2
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_048F2
    move.l a4,d1
    cmp.l d1,d0
    beq.w L_BOBS_048E0
    lea L_BOBS_048FA(pc),a1
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_BOBS_048F2
L_BOBS_048E0:
end_arm_install:
    lea L_BOBS_048FA(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
    move.l #$00000001,d3
L_BOBS_048F2:
end_arm_return:
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
