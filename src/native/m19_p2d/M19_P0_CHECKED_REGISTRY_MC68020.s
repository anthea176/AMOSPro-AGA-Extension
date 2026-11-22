; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update
; Audited bytes checked against the official M19 P2d library.
; BOBS+$03792..$046CC (3898 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_REGISTRY_INITIAL_STATUS equ 0

checked_stage_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -176(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a1,4(a2)
    move.l a4,8(a2)
    move.l #$00000000,84(a2)
    move.l #P0_REGISTRY_INITIAL_STATUS,d3
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_03C7E
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_03C7E
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_03C7E
    andi.l #$00000001,d0
    bne.w L_BOBS_03C7E
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_03C7E
    lea L_BOBS_020A2(pc),a0
    move.l (a0),d1
    move.l (a2),d0
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l 4(a0),d0
    move.l d0,12(a2)
    tst.l d0
    beq.w L_BOBS_03C7E
    move.l 8(a0),d0
    move.l d0,16(a2)
    tst.l d0
    beq.w L_BOBS_03C7E
    move.l 1514(a5),d0
    move.l 16(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l (a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    cmpi.l #$00000018,d0
    bls.w L_BOBS_03C7E
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_03C7E
L_BOBS_03858:
checked_stage_live_bank_valid:
    move.l 12(a2),d0
    subi.l #$00000018,d0
    move.l d0,88(a2)
    movea.l 88(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_03C7E
    movea.l 12(a2),a4
    move.l -20(a4),d0
    cmpi.l #$00000030,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$01000010,d0
    bhi.w L_BOBS_03C7E
    subi.l #$00000010,d0
    move.l d0,20(a2)
    move.l 12(a2),d0
    move.l 20(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03C7E
    subq.l #1,d0
    move.l d0,88(a2)
    movea.l 88(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_03C7E
    movea.l 12(a2),a4
    move.l -16(a4),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l #$00000000,d0
    move.w -12(a4),d0
    tst.l d0
    beq.w L_BOBS_038F0
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_BOBS_03C7E
L_BOBS_038F0:
checked_flags_ok:
    move.l -8(a4),d0
    cmpi.l #$41474142,d0
    bne.w L_BOBS_03C7E
    move.l -4(a4),d0
    cmpi.l #$4F425320,d0
    bne.w L_BOBS_03C7E
    move.l (a4),d0
    cmpi.l #$4147424F,d0
    bne.w L_BOBS_03C7E
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_03C7E
    tst.w 6(a4)
    bne.w L_BOBS_03C7E
    move.l #$00000000,d0
    move.w 8(a4),d0
checked_stage_min_count:
    cmpi.l #$00000000,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03C7E
    move.l d0,24(a2)
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000028,d0
    bne.w L_BOBS_03C7E
    move.l 12(a4),d0
    cmpi.l #$00000020,d0
    bne.w L_BOBS_03C7E
    move.l 24(a2),d0
    mulu.w #$0028,d0
    addi.l #$00000020,d0
    move.l d0,28(a2)
    movea.l 12(a2),a4
    cmp.l 16(a4),d0
    bne.w L_BOBS_03C7E
    move.l 20(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_03C7E
    move.l 20(a4),d0
    move.l 20(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l 24(a4),d0
    tst.l d0
    beq.w L_BOBS_03C7E
    move.l d0,32(a2)
    tst.l 28(a4)
    bne.w L_BOBS_03C7E
    move.l 28(a2),d0
    move.l d0,36(a2)
    move.l 12(a2),d0
    addi.l #$00000020,d0
    move.l d0,40(a2)
    move.l #$00000000,44(a2)
    move.l #$00000000,48(a2)
L_BOBS_039EA:
checked_loop:
    move.l 44(a2),d0
    move.l 24(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_03C2C
    movea.l 40(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l 48(a2),d1
    cmp.l d1,d0
    bls.w L_BOBS_03C7E
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03C7E
    move.l d0,48(a2)
    move.l #$00000000,d0
    move.w 2(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03C7E
    move.l d0,52(a2)
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03C7E
    move.l d0,56(a2)
    move.l #$00000000,d0
    move.w 6(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03C7E
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_03C7E
    move.l d0,60(a2)
    move.l 52(a2),d0
    move.l 56(a2),d1
    mulu.w d1,d0
    cmpi.l #$00400000,d0
    bhi.w L_BOBS_03C7E
    move.l 52(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    movea.l 40(a2),a4
    move.l #$00000000,d1
    move.w 8(a4),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l d0,64(a2)
    move.l 64(a2),d0
    move.l 56(a2),d1
    mulu.w d1,d0
    move.l d0,68(a2)
    move.l d0,d6
    move.l 60(a2),d5
    move.l #$00000000,d7
L_BOBS_03AD6:
checked_sum_planes:
    add.l d6,d7
    bcs.w L_BOBS_03C7E
    subq.l #1,d5
    bne.w L_BOBS_03AD6
    movea.l 40(a2),a4
    move.l 16(a4),d0
    cmp.l d7,d0
    bne.w L_BOBS_03C7E
    move.l d0,72(a2)
    move.l 36(a2),d0
    cmp.l 12(a4),d0
    bne.w L_BOBS_03C7E
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000001,d0
    bhi.w L_BOBS_03C7E
    move.l d0,80(a2)
    move.l 80(a2),d0
    tst.l d0
    beq.w L_BOBS_03B56
    move.l 68(a2),d1
    movea.l 40(a2),a4
    move.l 24(a4),d0
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l 36(a2),d0
    move.l 72(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03C7E
    cmp.l 20(a4),d0
    bne.w L_BOBS_03C7E
    move.l 68(a2),d0
    move.l d0,76(a2)
    bra.w L_BOBS_03B72
L_BOBS_03B56:
checked_no_mask:
    movea.l 40(a2),a4
    tst.l 20(a4)
    bne.w L_BOBS_03C7E
    tst.l 24(a4)
    bne.w L_BOBS_03C7E
    move.l #$00000000,76(a2)
L_BOBS_03B72:
checked_mask_done:
    move.l 36(a2),d0
    move.l 72(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03C7E
    move.l 76(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03C7E
    move.l 20(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_03C7E
    move.l d0,36(a2)
    movea.l 40(a2),a4
    tst.l 32(a4)
    bne.w L_BOBS_03C7E
    tst.l 36(a4)
    bne.w L_BOBS_03C7E
    move.l 12(a2),d0
    movea.l 40(a2),a4
    add.l 12(a4),d0
    bcs.w L_BOBS_03C7E
    movea.l d0,a0
    move.l 52(a2),d0
    move.l 64(a2),d1
    move.l 56(a2),d2
    move.l 60(a2),d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_03C7E
    move.l 76(a2),d0
    tst.l d0
    beq.w L_BOBS_03C10
    move.l 12(a2),d0
    movea.l 40(a2),a4
    add.l 20(a4),d0
    bcs.w L_BOBS_03C7E
    movea.l d0,a0
    move.l 52(a2),d0
    move.l 64(a2),d1
    move.l 56(a2),d2
    move.l #$00000001,d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_03C7E
L_BOBS_03C10:
checked_padding_ok:
    move.l 40(a2),d0
    addi.l #$00000028,d0
    move.l d0,40(a2)
    move.l 44(a2),d0
    addq.l #1,d0
    move.l d0,44(a2)
    bra.w L_BOBS_039EA
L_BOBS_03C2C:
checked_all_entries:
    move.l 36(a2),d0
    move.l 20(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03C7E
    move.l 20(a2),d0
    move.l 28(a2),d1
    sub.l d1,d0
    move.l d0,92(a2)
    move.l 12(a2),d0
    move.l 28(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03C7E
    movea.l d0,a0
    move.l 92(a2),d0
    movea.l 4(a2),a1
    move.l 12(a2),d1
    move.l 32(a2),d4
    movea.l 8(a2),a4
checked_stage_copy_call:
    bsr.w L_BOBS_0865E
    tst.l d3
    beq.w L_BOBS_03C7E
    move.l #$00000001,84(a2)
L_BOBS_03C7E:
checked_fail:
    move.l 84(a2),d3
    lea 176(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_03C8E:
checked_lookup_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -176(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a1,4(a2)
    move.l #$00000000,84(a2)
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_03D8E
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_03D8E
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_03D8E
    andi.l #$00000001,d0
    bne.w L_BOBS_03D8E
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_03D8E
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_03D8E
    lea L_BOBS_020A2(pc),a0
    move.l (a0),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03D8E
    lea L_BOBS_020A2(pc),a0
    move.l 4(a0),d0
    move.l d0,12(a2)
    tst.l d0
    beq.w L_BOBS_03D8E
    move.l 8(a0),d0
    move.l d0,16(a2)
    move.l 1514(a5),d0
    move.l 16(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03D8E
    move.l (a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03D8E
    cmpi.l #$00000018,d0
    bls.w L_BOBS_03D8E
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_03D8E
    movea.l 12(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_03D8E
    movea.l 12(a2),a4
    move.l (a4),d0
    cmpi.l #$4147424F,d0
    bne.w L_BOBS_03D8E
    move.l 24(a4),d1
    tst.l d1
    beq.w L_BOBS_03D8E
    move.l 12(a2),d0
    movea.l 4(a2),a1
    bsr.w L_BOBS_04204
    tst.l d3
    beq.w L_BOBS_03D8E
    move.l #$00000001,84(a2)
L_BOBS_03D8E:
checked_lookup_fail:
    move.l 84(a2),d3
    lea 176(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_03D9E:
checked_release_entry:
    bra.w L_BOBS_04076
L_BOBS_03DA2:
checked_chip_stage:
chip_stage_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l #$00000000,52(a2)
    move.l a0,(a2)
    move.l d0,4(a2)
    move.l a1,8(a2)
    move.l d1,12(a2)
    move.l d4,16(a2)
    move.l a4,20(a2)
    move.l #$00000000,24(a2)
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_04066
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_04066
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 8(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 12(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    cmpi.l #$01000000,d0
    bhi.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 16(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    move.l (a2),d0
    move.l 4(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_04066
    subq.l #1,d0
    move.l d0,40(a2)
    movea.l (a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_04066
    movea.l 40(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_04066
    movea.l 8(a2),a0
    move.l (a0),d0
    move.l d0,28(a2)
    move.l 4(a0),d0
    move.l d0,32(a2)
    move.l 16(a0),d0
    move.l d0,36(a2)
    move.l 28(a2),d0
    tst.l d0
    bne.w L_BOBS_03ED8
    movea.l 8(a2),a0
    tst.l 4(a0)
    bne.w L_BOBS_04066
    movea.l 8(a2),a0
    tst.l 8(a0)
    bne.w L_BOBS_04066
    movea.l 8(a2),a0
    tst.l 12(a0)
    bne.w L_BOBS_04066
    movea.l 8(a2),a0
    tst.l 16(a0)
    bne.w L_BOBS_04066
    bra.w L_BOBS_03F6E
L_BOBS_03ED8:
chip_stage_has_old:
    move.l 28(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 32(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    cmpi.l #$01000000,d0
    bhi.w L_BOBS_04066
    andi.l #$00000001,d0
    bne.w L_BOBS_04066
    move.l 36(a2),d0
    cmpi.l #$43484950,d0
    bne.w L_BOBS_04066
    move.l 20(a2),d0
    tst.l d0
    beq.w L_BOBS_04066
    move.l 28(a2),d0
    move.l 32(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_04066
    subq.l #1,d0
    move.l d0,48(a2)
    movea.l 28(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_04066
    movea.l 48(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_04066
L_BOBS_03F6E:
chip_stage_allocate:
    move.l 4(a2),d0
    move.l #$00000003,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_BOBS_04066
    move.l d0,24(a2)
    move.l 24(a2),d0
    tst.l d0
    beq.w L_BOBS_0405A
    andi.l #$00000001,d0
    bne.w L_BOBS_0405A
    move.l 24(a2),d0
    move.l 4(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_0405A
    subq.l #1,d0
    move.l d0,44(a2)
    movea.l 24(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_0405A
    movea.l 44(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_0405A
    movea.l (a2),a0
    movea.l 24(a2),a1
    move.l 4(a2),d0
    movea.l $0004.w,a6
    jsr -624(a6)
    move.l 28(a2),d0
    tst.l d0
    beq.w L_BOBS_0400E
    movea.l 20(a2),a6
    jsr -228(a6)
L_BOBS_0400E:
chip_stage_commit:
    movea.l 8(a2),a0
    move.l 24(a2),d0
    move.l d0,(a0)
    move.l 4(a2),d0
    move.l d0,4(a0)
    move.l 12(a2),d0
    move.l d0,8(a0)
    move.l 16(a2),d0
    move.l d0,12(a0)
    move.l #$43484950,16(a0)
    move.l 28(a2),d0
    tst.l d0
    beq.w L_BOBS_0404E
    movea.l 28(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_0404E:
chip_stage_ok:
    move.l #$00000001,52(a2)
    bra.w L_BOBS_04066
L_BOBS_0405A:
chip_stage_cleanup:
    movea.l 24(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_04066:
chip_stage_fail:
chip_stage_return:
    move.l 52(a2),d3
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_04076:
chip_release_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l #$00000000,52(a2)
    move.l a1,8(a2)
    move.l a4,20(a2)
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_041F4
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_041F4
    move.l 8(a2),d0
    tst.l d0
    beq.w L_BOBS_041F4
    andi.l #$00000001,d0
    bne.w L_BOBS_041F4
    movea.l 8(a2),a0
    move.l (a0),d0
    move.l d0,28(a2)
    move.l 4(a0),d0
    move.l d0,32(a2)
    move.l 28(a2),d0
    tst.l d0
    bne.w L_BOBS_04114
    movea.l 8(a2),a0
    tst.l 4(a0)
    bne.w L_BOBS_041F4
    movea.l 8(a2),a0
    tst.l 8(a0)
    bne.w L_BOBS_041F4
    movea.l 8(a2),a0
    tst.l 12(a0)
    bne.w L_BOBS_041F4
    movea.l 8(a2),a0
    tst.l 16(a0)
    bne.w L_BOBS_041F4
    move.l #$00000001,52(a2)
    bra.w L_BOBS_041F4
L_BOBS_04114:
chip_release_has_old:
    move.l 28(a2),d0
    tst.l d0
    beq.w L_BOBS_041F4
    andi.l #$00000001,d0
    bne.w L_BOBS_041F4
    move.l 32(a2),d0
    tst.l d0
    beq.w L_BOBS_041F4
    cmpi.l #$01000000,d0
    bhi.w L_BOBS_041F4
    andi.l #$00000001,d0
    bne.w L_BOBS_041F4
    movea.l 8(a2),a0
    move.l 16(a0),d0
    cmpi.l #$43484950,d0
    bne.w L_BOBS_041F4
    move.l 20(a2),d0
    tst.l d0
    beq.w L_BOBS_041F4
    move.l 28(a2),d0
    move.l 32(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_041F4
    subq.l #1,d0
    move.l d0,48(a2)
    movea.l 28(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_041F4
    movea.l 48(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    cmpi.l #$00000002,d0
    bne.w L_BOBS_041F4
    movea.l 20(a2),a6
    jsr -228(a6)
    movea.l 28(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
    movea.l 8(a2),a0
    move.l #$00000000,(a0)
    move.l #$00000000,4(a0)
    move.l #$00000000,8(a0)
    move.l #$00000000,12(a0)
    move.l #$00000000,16(a0)
    move.l #$00000001,52(a2)
L_BOBS_041F4:
chip_release_return:
    move.l 52(a2),d3
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_04204:
chip_lookup_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l #$00000000,52(a2)
    move.l a1,8(a2)
    move.l d0,12(a2)
    move.l d1,16(a2)
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_042AA
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_042AA
    move.l 8(a2),d0
    tst.l d0
    beq.w L_BOBS_042AA
    andi.l #$00000001,d0
    bne.w L_BOBS_042AA
    move.l 12(a2),d0
    tst.l d0
    beq.w L_BOBS_042AA
    andi.l #$00000001,d0
    bne.w L_BOBS_042AA
    move.l 16(a2),d0
    tst.l d0
    beq.w L_BOBS_042AA
    movea.l 8(a2),a0
    move.l 16(a0),d0
    cmpi.l #$43484950,d0
    bne.w L_BOBS_042AA
    move.l (a0),d0
    tst.l d0
    beq.w L_BOBS_042AA
    move.l 8(a0),d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_042AA
    move.l 12(a0),d0
    move.l 16(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_042AA
    move.l #$00000001,52(a2)
L_BOBS_042AA:
chip_lookup_return:
    move.l 52(a2),d3
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_042BA:
registry_prepare_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a5,4(a2)
    move.l a4,8(a2)
    move.l #$00000000,28(a2)
    move.l #$00000000,24(a2)
    lea L_BOBS_046CC(pc),a0
    move.l a0,12(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_046BC
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_0465E
    tst.l d0
    beq.w L_BOBS_046BC
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_046BC
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_046BC
    bsr.w L_BOBS_045CE
    move.l 36(a2),d0
    tst.l d0
    bne.w L_BOBS_046BC
    move.l 20(a2),d0
    tst.l d0
    bne.w L_BOBS_04368
    move.l #$00000020,d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_BOBS_046BC
    move.l d0,24(a2)
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_043BA
    movea.l d0,a0
    move.l (a2),d1
    move.l d1,4(a0)
    move.l d0,20(a2)
L_BOBS_04368:
registry_prepare_checked:
    move.l 20(a2),d0
    addi.l #$00000008,d0
    movea.l d0,a1
    move.l (a2),d3
    movea.l 8(a2),a4
    bsr.w L_BOBS_03792
    tst.l d3
    beq.w L_BOBS_043BA
L_BOBS_04384:
registry_prepare_after_stage:
    move.l 24(a2),d0
    tst.l d0
    beq.w L_BOBS_043AE
    movea.l 12(a2),a0
    move.l 4(a0),d1
    movea.l 24(a2),a0
    move.l d1,(a0)
    movea.l 12(a2),a0
    move.l 24(a2),d0
    move.l d0,4(a0)
    move.l 4(a2),d0
    move.l d0,(a0)
L_BOBS_043AE:
registry_prepare_success:
    move.l #$00000001,28(a2)
    bra.w L_BOBS_046BC
L_BOBS_043BA:
registry_prepare_free_new:
    move.l 24(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    movea.l 24(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
    bra.w L_BOBS_046BC
L_BOBS_043D4:
registry_lookup_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a5,4(a2)
    move.l a4,8(a2)
    move.l #$00000000,28(a2)
    move.l #$00000000,24(a2)
    lea L_BOBS_046CC(pc),a0
    move.l a0,12(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_046BC
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_0465E
    tst.l d0
    beq.w L_BOBS_046BC
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_046BC
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_046BC
    bsr.w L_BOBS_045CE
    move.l 36(a2),d0
    tst.l d0
    bne.w L_BOBS_046BC
    move.l 20(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    move.l 20(a2),d0
    addi.l #$00000008,d0
    movea.l d0,a1
    move.l (a2),d3
    bsr.w L_BOBS_03C8E
    tst.l d3
    beq.w L_BOBS_046BC
    move.l #$00000001,28(a2)
    bra.w L_BOBS_046BC
L_BOBS_04470:
registry_free_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a5,4(a2)
    move.l a4,8(a2)
    move.l #$00000000,28(a2)
    move.l #$00000000,24(a2)
    lea L_BOBS_046CC(pc),a0
    move.l a0,12(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_046BC
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_0465E
    tst.l d0
    beq.w L_BOBS_046BC
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_046BC
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_046BC
    bsr.w L_BOBS_045CE
    move.l 36(a2),d0
    tst.l d0
    bne.w L_BOBS_046BC
    move.l 20(a2),d0
    tst.l d0
    beq.w L_BOBS_04506
    move.l 20(a2),d0
    addi.l #$00000008,d0
    movea.l d0,a1
    movea.l 8(a2),a4
    bsr.w L_BOBS_03D9E
    tst.l d3
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_04632
L_BOBS_04506:
registry_free_no_node:
    move.l #$00000001,28(a2)
    bra.w L_BOBS_046BC
L_BOBS_04512:
registry_close_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a5,4(a2)
    move.l a4,8(a2)
    move.l #$00000000,28(a2)
    move.l #$00000000,24(a2)
    lea L_BOBS_046CC(pc),a0
    move.l a0,12(a2)
    bsr.w L_BOBS_04694
    tst.l d0
    beq.w L_BOBS_046BC
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_0465E
    tst.l d0
    beq.w L_BOBS_046BC
    move.l #$00000100,32(a2)
L_BOBS_04564:
registry_close_next:
    movea.l 12(a2),a0
    move.l 4(a0),d0
    move.l d0,20(a2)
    tst.l d0
    beq.w L_BOBS_045B8
    move.l 32(a2),d0
    tst.l d0
    beq.w L_BOBS_046BC
    subq.l #1,d0
    move.l d0,32(a2)
    move.l 12(a2),d0
    addi.l #$00000004,d0
    movea.l d0,a0
    move.l a0,16(a2)
    move.l 20(a2),d0
    addi.l #$00000008,d0
    movea.l d0,a1
    movea.l 8(a2),a4
    bsr.w L_BOBS_03D9E
    tst.l d3
    beq.w L_BOBS_046BC
    bsr.w L_BOBS_04632
    bra.w L_BOBS_04564
L_BOBS_045B8:
registry_close_finished:
    movea.l 12(a2),a0
    move.l #$00000000,(a0)
    move.l #$00000001,28(a2)
    bra.w L_BOBS_046BC
L_BOBS_045CE:
registry_find:
    move.l 12(a2),d0
    addi.l #$00000004,d0
    movea.l d0,a0
    move.l a0,16(a2)
    move.l #$00000000,36(a2)
    move.l #$00000100,32(a2)
L_BOBS_045EE:
registry_find_next:
    movea.l 16(a2),a0
    move.l (a0),d0
    move.l d0,20(a2)
    tst.l d0
    beq.w L_BOBS_04630
    move.l 32(a2),d1
    tst.l d1
    beq.w L_BOBS_04628
    subq.l #1,d1
    move.l d1,32(a2)
    movea.l d0,a0
    move.l 4(a0),d1
    move.l (a2),d0
    cmp.l d1,d0
    beq.w L_BOBS_04630
    movea.l 20(a2),a0
    move.l a0,16(a2)
    bra.w L_BOBS_045EE
L_BOBS_04628:
registry_find_broken:
    move.l #$00000001,36(a2)
L_BOBS_04630:
registry_find_exit:
    rts
L_BOBS_04632:
registry_unlink_and_free:
    movea.l 20(a2),a0
    move.l (a0),d1
    movea.l 16(a2),a0
    move.l d1,(a0)
    movea.l 20(a2),a1
    movea.l $0004.w,a6
    jsr -690(a6)
    movea.l 12(a2),a0
    tst.l 4(a0)
    bne.w L_BOBS_0465C
    move.l #$00000000,(a0)
L_BOBS_0465C:
registry_keep_owner:
    rts
L_BOBS_0465E:
registry_owner_guard:
    movea.l 12(a2),a0
    move.l (a0),d0
    tst.l d0
    beq.w L_BOBS_0467C
    move.l 4(a2),d1
    cmp.l d1,d0
    beq.w L_BOBS_04684
    move.l #$00000000,d0
    rts
L_BOBS_0467C:
registry_owner_unbound:
    tst.l 4(a0)
    bne.w L_BOBS_0468C
L_BOBS_04684:
registry_owner_allowed:
    move.l #$00000001,d0
    rts
L_BOBS_0468C:
registry_owner_denied:
    move.l #$00000000,d0
    rts
L_BOBS_04694:
registry_cpu_guard:
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_046B4
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_046B4
    move.l #$00000001,d0
    rts
L_BOBS_046B4:
registry_cpu_absent:
    move.l #$00000000,d0
    rts
L_BOBS_046BC:
registry_return:
    move.l 28(a2),d3
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
