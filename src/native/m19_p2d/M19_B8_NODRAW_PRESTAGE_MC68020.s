; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_b8_s1_bank_prestage_emit.py::emit_b8_s1_bank_prestage
; Audited bytes checked against the official M19 P2d library.
; BOBS+$07364..$07698 (820 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
B8_PRESTAGE_INITIAL_RESULT equ 0

b8_b7_arm_end_nodraw_entry:
    movem.l d0-d1/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l #B8_PRESTAGE_INITIAL_RESULT,(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_074B4
    move.l a5,d0
    tst.l d0
    beq.w L_BOBS_074B4
    andi.l #$00000001,d0
    bne.w L_BOBS_074B4
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_074B4
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_074B4
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_074B4
    move.l d0,4(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_074B4
    movea.l 4(a2),a0
    tst.l (a0)
    beq.w L_BOBS_074B4
    move.l 4(a2),d0
    cmpi.l #$00000168,d0
    bcs.w L_BOBS_074B4
    subi.l #$00000168,d0
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_074B4
    move.l d0,12(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_074B4
    move.l 12(a2),d0
    addi.l #$0000000B,d0
    bcs.w L_BOBS_074B4
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_074B4
    movea.l 12(a2),a4
    move.l (a4),d0
    cmpi.l #$48E7FFFE,d0
    bne.w L_BOBS_074B4
    move.l 4(a4),d0
    cmpi.l #$246D01C8,d0
    bne.w L_BOBS_074B4
    move.l 8(a4),d0
    cmpi.l #$60000978,d0
    bne.w L_BOBS_074B4
    move.l 460(a5),d0
    move.l 464(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_074B4
    move.l d0,8(a2)
    move.l 12(a2),d1
    cmp.l d1,d0
    beq.w L_BOBS_074A2
    lea L_BOBS_048FA(pc),a1
    move.l 8(a2),d0
    move.l a1,d1
    cmp.l d1,d0
    beq.w L_BOBS_074A2
    lea L_BOBS_06EAC(pc),a1
    move.l 8(a2),d0
    move.l a1,d1
    cmp.l d1,d0
    beq.w L_BOBS_074A2
    lea L_BOBS_071EE(pc),a1
    move.l 8(a2),d0
    move.l a1,d1
    cmp.l d1,d0
    bne.w L_BOBS_074B4
    bra.w L_BOBS_074AE
L_BOBS_074A2:
b8_nodraw_arm:
    lea L_BOBS_06EAC(pc),a0
    move.l a0,460(a5)
    move.l a0,464(a5)
L_BOBS_074AE:
b8_nodraw_success:
    move.l #$00000001,(a2)
L_BOBS_074B4:
b8_nodraw_return:
    move.l (a2),d3
    move.l #$00000000,d2
    lea 64(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a2/a4-a6
    rts
ENTRY_BOBS_074C6:
b8_b7_bob_set_bootstrap_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    move.l #$00000000,(a7)
    bsr.w L_BOBS_05B6E
    tst.l d3
    beq.w L_BOBS_074E4
    bsr.w L_BOBS_07364
    move.l d3,(a7)
L_BOBS_074E4:
b8_set_return:
    move.l (a7),d3
    move.l #$00000000,d2
    lea 32(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
ENTRY_BOBS_074F8:
b8s1_bank_prestage_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l #$00000000,28(a2)
    move.l #$00000000,32(a2)
    move.l #$00000000,36(a2)
    lea L_BOBS_020A2(pc),a0
    move.l (a0),4(a2)
    move.l 4(a0),8(a2)
    move.l 8(a0),12(a2)
    move.l (a2),d3
    bsr.w L_BOBS_01B7E
    tst.l d3
    beq.w L_BOBS_07698
    lea L_BOBS_020A2(pc),a0
    move.l (a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_07672
    move.l 4(a0),d0
    cmpi.l #$00000018,d0
    bls.w L_BOBS_07672
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_07672
    move.l d0,16(a2)
    move.l 8(a0),d0
    move.l 1514(a5),d1
    cmp.l d1,d0
    bne.w L_BOBS_07672
    move.l 16(a2),d0
    addi.l #$00000009,d0
    bcs.w L_BOBS_07672
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_07672
    movea.l 16(a2),a0
    move.l #$00000000,d0
    move.w 8(a0),d0
    tst.l d0
    beq.w L_BOBS_07690
    move.l 456(a5),d0
    tst.l d0
    beq.w L_BOBS_07672
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_07672
    move.l d0,20(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_07672
    move.l 20(a2),d0
    addi.l #$00000020,d0
    bcs.w L_BOBS_07672
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_07672
    movea.l 20(a2),a0
    tst.l (a0)
    beq.w L_BOBS_07672
    move.l 8(a0),d0
    tst.l d0
    beq.w L_BOBS_07672
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_07672
    move.l d0,24(a2)
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_07672
    move.l (a2),d3
    movea.l 24(a2),a4
    bsr.w L_BOBS_043D4
    tst.l d3
    beq.w L_BOBS_0763C
    move.l #$00000001,28(a2)
L_BOBS_0763C:
b8s1_bank_cache_miss:
    move.l (a2),d3
    movea.l 24(a2),a4
    bsr.w L_BOBS_06596
    tst.l d3
    beq.w L_BOBS_07672
    move.l #$00000001,32(a2)
    bsr.w L_BOBS_07364
    tst.l d3
    bne.w L_BOBS_07690
    move.l 28(a2),d0
    tst.l d0
    bne.w L_BOBS_07672
    move.l (a2),d3
    movea.l 24(a2),a4
    bsr.w L_BOBS_04470
L_BOBS_07672:
b8s1_bank_rollback:
    lea L_BOBS_020A2(pc),a0
    move.l 4(a2),d0
    move.l d0,(a0)
    move.l 8(a2),d0
    move.l d0,4(a0)
    move.l 12(a2),d0
    move.l d0,8(a0)
    bra.w L_BOBS_07698
L_BOBS_07690:
b8s1_bank_success:
    move.l #$00000001,36(a2)
