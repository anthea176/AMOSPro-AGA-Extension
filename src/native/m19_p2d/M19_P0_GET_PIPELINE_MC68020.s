; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/build_m19_p2c_in_memory.py::build_p2c
; Audited bytes checked against the official M19 P2d library.
; BOBS+$020CE..$03772 (5796 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0_GET_FRAME_VALID equ 1

    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -320(a7),a7
    movea.l a7,a2
    move.l d3,16(a2)
    move.l (a3)+,d7
    move.l d7,12(a2)
    move.l (a3)+,d7
    move.l d7,8(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l (a3)+,d7
    move.l d7,(a2)
    move.l #$00000000,156(a2)
    move.l #$00000000,224(a2)
    move.l #$00000000,d3
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_02AC4
    move.l (a2),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l 4(a2),d0
    tst.l d0
    bmi.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l 8(a2),d0
    tst.l d0
    bmi.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l 12(a2),d0
    tst.l d0
    bmi.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l 16(a2),d0
    tst.l d0
    bmi.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l 4(a2),d0
    move.l 12(a2),d1
    cmp.l d0,d1
    bcs.w L_BOBS_02AC4
    move.l 8(a2),d0
    move.l 16(a2),d1
    cmp.l d0,d1
    bcs.w L_BOBS_02AC4
    lea L_BOBS_020A2(pc),a0
    move.l (a0),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_02AC4
    move.l d0,20(a2)
    move.l 4(a0),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l d0,24(a2)
    move.l 8(a0),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l d0,28(a2)
    move.l 1514(a5),d0
    move.l 28(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l 20(a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    move.l 24(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l 24(a2),d0
    cmpi.l #$00000018,d0
    bls.w L_BOBS_02AC4
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_02AC4
    movea.l d0,a4
    move.l -20(a4),d0
    cmpi.l #$00000030,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$01000010,d0
    bhi.w L_BOBS_02AC4
    subi.l #$00000010,d0
    move.l d0,32(a2)
    move.l 24(a2),d0
    subi.l #$00000018,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 24(a2),d0
    move.l 32(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_02AC4
    movea.l 24(a2),a4
    move.l -16(a4),d0
    move.l 20(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l #$00000000,d0
    move.w -12(a4),d0
    tst.l d0
    beq.w L_BOBS_022A6
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_BOBS_02AC4
L_BOBS_022A6:
old_flags_good:
    move.l -8(a4),d0
    cmpi.l #$41474142,d0
    bne.w L_BOBS_02AC4
    move.l -4(a4),d0
    cmpi.l #$4F425320,d0
    bne.w L_BOBS_02AC4
    move.l (a4),d0
    cmpi.l #$4147424F,d0
    bne.w L_BOBS_02AC4
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_02AC4
    tst.w 6(a4)
    bne.w L_BOBS_02AC4
    move.l #$00000000,d0
    move.w 8(a4),d0
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,36(a2)
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000028,d0
    bne.w L_BOBS_02AC4
    move.l 12(a4),d0
    cmpi.l #$00000020,d0
    bne.w L_BOBS_02AC4
    move.l 36(a2),d0
    mulu.w #$0028,d0
    addi.l #$00000020,d0
    movea.l 24(a2),a4
    cmp.l 16(a4),d0
    bne.w L_BOBS_02AC4
    move.l 32(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_02AC4
    move.l d0,40(a2)
    move.l 20(a4),d0
    move.l 32(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l 24(a4),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    cmpi.l #$FFFFFFFF,d0
    beq.w L_BOBS_02AC4
    move.l d0,44(a2)
    tst.l 28(a4)
    bne.w L_BOBS_02AC4
    move.l #$00000000,48(a2)
    move.l #$00000000,52(a2)
    move.l 40(a2),d0
    move.l d0,56(a2)
    move.l 24(a2),d0
    addi.l #$00000020,d0
    move.l d0,60(a2)
    move.l #$00000000,172(a2)
L_BOBS_023A8:
validate_old_loop:
    move.l 172(a2),d0
    move.l 36(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_0262C
    movea.l 60(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l 52(a2),d1
    cmp.l d1,d0
    bls.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,52(a2)
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_023EA
    move.l #P0_GET_FRAME_VALID,48(a2)
L_BOBS_023EA:
not_replaced:
    move.l #$00000000,d0
    move.w 2(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,64(a2)
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,72(a2)
    move.l #$00000000,d0
    move.w 6(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_02AC4
    move.l d0,68(a2)
    move.l 64(a2),d0
    move.l 72(a2),d1
    mulu.w d1,d0
    cmpi.l #$00400000,d0
    bhi.w L_BOBS_02AC4
    move.l 64(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l #$00000000,d1
    move.w 8(a4),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l d0,64(a2)
    move.l #$00000000,d0
    move.w 10(a4),d0
    andi.l #$0000FFFE,d0
    tst.l d0
    bne.w L_BOBS_02AC4
    move.l 64(a2),d0
    move.l 72(a2),d1
    mulu.w d1,d0
    move.l d0,d6
    move.l 68(a2),d5
    move.l #$00000000,d7
L_BOBS_024B2:
old_depth_sum:
    add.l d6,d7
    bcs.w L_BOBS_02AC4
    subq.l #1,d5
    bne.w L_BOBS_024B2
    movea.l 60(a2),a4
    move.l 16(a4),d0
    cmp.l d7,d0
    bne.w L_BOBS_02AC4
    move.l d7,76(a2)
    move.l 56(a2),d0
    cmp.l 12(a4),d0
    bne.w L_BOBS_02AC4
    move.l 24(a4),d0
    tst.l d0
    beq.w L_BOBS_02522
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_02AC4
    move.l 24(a4),d0
    cmp.l d6,d0
    bne.w L_BOBS_02AC4
    move.l 56(a2),d0
    move.l 76(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    cmp.l 20(a4),d0
    bne.w L_BOBS_02AC4
    move.l d6,80(a2)
    bra.w L_BOBS_02542
L_BOBS_02522:
no_mask:
    tst.l 20(a4)
    bne.w L_BOBS_02AC4
    move.l #$00000000,d0
    move.w 10(a4),d0
    tst.l d0
    bne.w L_BOBS_02AC4
    move.l #$00000000,80(a2)
L_BOBS_02542:
mask_checked:
    move.l 56(a2),d0
    move.l 76(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    move.l 80(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    move.l 32(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_02AC4
    move.l d0,56(a2)
    movea.l 60(a2),a4
    tst.l 32(a4)
    bne.w L_BOBS_02AC4
    tst.l 36(a4)
    bne.w L_BOBS_02AC4
    movea.l 24(a2),a0
    movea.l 60(a2),a4
    move.l 12(a4),d0
    add.l a0,d0
    movea.l d0,a0
    move.l #$00000000,d0
    move.w 2(a4),d0
    move.l 64(a2),d1
    move.l 72(a2),d2
    move.l 68(a2),d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 80(a2),d0
    tst.l d0
    beq.w L_BOBS_025EA
    move.l 24(a2),d0
    movea.l 60(a2),a4
    add.l 20(a4),d0
    bcs.w L_BOBS_02AC4
    movea.l d0,a0
    move.l #$00000000,d0
    move.w 2(a4),d0
    move.l 64(a2),d1
    move.l 72(a2),d2
    move.l #$00000001,d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_02AC4
L_BOBS_025EA:
padding_ok:
    movea.l 60(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l (a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02610
    move.l 76(a2),d0
    move.l 80(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    move.l d0,84(a2)
L_BOBS_02610:
not_replaced_size:
    move.l 60(a2),d0
    addi.l #$00000028,d0
    move.l d0,60(a2)
    move.l 172(a2),d0
    addq.l #1,d0
    move.l d0,172(a2)
    bra.w L_BOBS_023A8
L_BOBS_0262C:
old_validated:
    move.l 56(a2),d0
    move.l 32(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    movea.l 456(a5),a4
    move.l a4,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l a4,124(a2)
    move.l (a4),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 8(a4),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 32(a4),d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 12(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,140(a2)
    move.l 16(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,144(a2)
    move.l 28(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_02AC4
    move.l d0,108(a2)
    move.l 12(a2),d0
    move.l 140(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_02AC4
    move.l 16(a2),d0
    move.l 144(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_02AC4
    move.l 12(a2),d0
    move.l 4(a2),d1
    sub.l d1,d0
    addq.l #1,d0
    move.l d0,100(a2)
    move.l 16(a2),d0
    move.l 8(a2),d1
    sub.l d1,d0
    addq.l #1,d0
    move.l d0,104(a2)
    move.l 100(a2),d0
    move.l 104(a2),d1
    mulu.w d1,d0
    cmpi.l #$00400000,d0
    bhi.w L_BOBS_02AC4
    move.l 100(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l d0,112(a2)
    move.l 104(a2),d1
    mulu.w d1,d0
    move.l d0,116(a2)
    move.l 108(a2),d5
    move.l d0,d6
    move.l #$00000000,d0
L_BOBS_02732:
new_depth_sum:
    add.l d6,d0
    bcs.w L_BOBS_02AC4
    subq.l #1,d5
    bne.w L_BOBS_02732
    move.l d0,120(a2)
    move.l 36(a2),d0
    move.l 48(a2),d1
    cmpi.l #$00000000,d1
    bne.w L_BOBS_02756
    addq.l #1,d0
L_BOBS_02756:
count_done:
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,88(a2)
    mulu.w #$0028,d0
    addi.l #$00000020,d0
    move.l d0,96(a2)
    move.l 32(a2),d0
    move.l 48(a2),d1
    tst.l d1
    bne.w L_BOBS_0278E
    addi.l #$00000028,d0
    bcs.w L_BOBS_02AC4
    bra.w L_BOBS_02798
L_BOBS_0278E:
subtract_old:
    move.l 84(a2),d1
    sub.l d1,d0
    bmi.w L_BOBS_02AC4
L_BOBS_02798:
add_capture:
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$01000000,d0
    bhi.w L_BOBS_02AC4
    move.l d0,92(a2)
    movea.l 124(a2),a4
    movea.l 32(a4),a0
    move.l a0,128(a2)
    move.l 8(a0),d0
    tst.l d0
    beq.w L_BOBS_027DA
    cmpi.l #$00000001,d0
    bne.w L_BOBS_02AC4
    movea.l 128(a2),a0
    movea.l (a0),a1
    bra.w L_BOBS_027E2
L_BOBS_027DA:
front_zero:
    movea.l 128(a2),a0
    movea.l 4(a0),a1
L_BOBS_027E2:
back_found:
    move.l a1,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    movea.l (a1),a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l a0,132(a2)
    move.l #$00000000,d0
    move.w (a0),d0
    cmpi.l #$00000002,d0
    bcs.w L_BOBS_02AC4
    cmpi.l #$0000FFFE,d0
    bhi.w L_BOBS_02AC4
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_02AC4
    move.l d0,136(a2)
    lsl.l #3,d0
    move.l 140(a2),d1
    cmp.l d1,d0
    bcs.w L_BOBS_02AC4
    movea.l 132(a2),a0
    move.l #$00000000,d0
    move.w 2(a0),d0
    move.l 144(a2),d1
    cmp.l d1,d0
    bcs.w L_BOBS_02AC4
    move.l #$00000000,d0
    move.b 5(a0),d0
    move.l 108(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    move.l 4(a2),d0
    lsr.l #3,d0
    move.l 8(a2),d1
    move.l 136(a2),d5
    mulu.w d5,d1
    add.l d0,d1
    bcs.w L_BOBS_02AC4
    move.l d1,148(a2)
    move.l 4(a2),d0
    andi.l #$00000007,d0
    move.l d0,152(a2)
    movea.l 132(a2),a4
    addq.l #8,a4
    move.l 108(a2),d6
L_BOBS_0288E:
check_chip_loop:
    move.l (a4)+,d7
    tst.l d7
    beq.w L_BOBS_02AC4
    cmpi.l #$FFFFFFFF,d7
    beq.w L_BOBS_02AC4
    move.l d7,d0
    andi.l #$00000001,d0
    bne.w L_BOBS_02AC4
    move.l d7,d0
    move.l 148(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l 16(a2),d0
    move.l 136(a2),d1
    mulu.w d1,d0
    move.l 12(a2),d1
    lsr.l #3,d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    add.l d7,d0
    bcs.w L_BOBS_02AC4
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    subq.l #1,d6
    bne.w L_BOBS_0288E
    movea.l 128(a2),a4
    move.l 20(a4),d0
    andi.l #$00000001,d0
    beq.w L_BOBS_02944
    movea.l 12(a4),a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    movea.l $0004.w,a6
    jsr -372(a6)
    tst.l d0
    beq.w L_BOBS_02AC4
    movea.l 128(a2),a4
    move.l 20(a4),d0
    andi.l #$FFFFFFFE,d0
    move.l d0,20(a4)
L_BOBS_02944:
safe_ready:
    movea.l 124(a2),a4
    movea.l 8(a4),a6
    jsr -228(a6)
    move.l 92(a2),d0
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_BOBS_02AC4
    move.l d0,156(a2)
    move.l d0,176(a2)
    movea.l d0,a4
    move.l #$4147424F,(a4)
    move.w #$0001,4(a4)
    move.w #$0000,6(a4)
    move.l 88(a2),d0
    move.w d0,8(a4)
    move.w #$0028,10(a4)
    move.l #$00000020,12(a4)
    move.l 96(a2),d0
    move.l d0,16(a4)
    move.l 92(a2),d0
    move.l d0,20(a4)
    move.l 44(a2),d0
    addq.l #1,d0
    move.l d0,24(a4)
    move.l #$00000000,28(a4)
    move.l 156(a2),d0
    addi.l #$00000020,d0
    move.l d0,160(a2)
    move.l 156(a2),d0
    move.l 96(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_02AC4
    move.l d0,164(a2)
    move.l #$00000000,168(a2)
    move.l 24(a2),d0
    addi.l #$00000020,d0
    move.l d0,60(a2)
    move.l #$00000000,172(a2)
L_BOBS_029FA:
build_entries:
    move.l 172(a2),d0
    move.l 36(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_02A5E
    movea.l 60(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l d0,216(a2)
    move.l (a2),d1
    cmp.l d1,d0
    bcs.w L_BOBS_02A32
    beq.w L_BOBS_02A36
    move.l 168(a2),d0
    tst.l d0
    bne.w L_BOBS_02A3E
    bsr.w L_BOBS_02BE8
L_BOBS_02A32:
maybe_insert_before:
    bra.w L_BOBS_02A3E
L_BOBS_02A36:
replace_here:
    bsr.w L_BOBS_02BE8
    bra.w L_BOBS_02A42
L_BOBS_02A3E:
copy_old_entry:
    bsr.w L_BOBS_02B56
L_BOBS_02A42:
advance_old:
    move.l 60(a2),d0
    addi.l #$00000028,d0
    move.l d0,60(a2)
    move.l 172(a2),d0
    addq.l #1,d0
    move.l d0,172(a2)
    bra.w L_BOBS_029FA
L_BOBS_02A5E:
after_old_entries:
    move.l 168(a2),d0
    tst.l d0
    bne.w L_BOBS_02A6C
    bsr.w L_BOBS_02BE8
L_BOBS_02A6C:
finished_entries:
    move.l 164(a2),d0
    move.l 156(a2),d1
    sub.l d1,d0
    move.l 92(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_02AC4
    movea.l 156(a2),a0
    move.l 92(a2),d1
    move.l 20(a2),d3
    bsr.w L_BOBS_01D38
    tst.l d3
    beq.w L_BOBS_02AC4
    move.l 20(a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_02AC4
    lea L_BOBS_020A2(pc),a0
    move.l d0,4(a0)
    move.l 28(a2),d1
    move.l d1,8(a0)
    move.l #$00000001,224(a2)
    bra.w L_BOBS_02AC4
L_BOBS_02AC4:
done:
fail:
    movea.l 156(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_BOBS_02AD8
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_02AD8:
no_scratch:
    move.l 224(a2),d3
    lea 320(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_02AE8:
check_padding:
    move.l d0,d5
    andi.l #$0000000F,d5
    tst.l d5
    beq.w L_BOBS_02B24
    move.w #$FFFF,d4
L_BOBS_02AFA:
padding_shift:
    lsr.w #1,d4
    subq.l #1,d5
    bne.w L_BOBS_02AFA
    move.l d2,d6
    mulu.w d3,d6
    movea.l a0,a1
    adda.l d1,a1
    subq.l #2,a1
L_BOBS_02B0C:
padding_loop:
    move.l #$00000000,d7
    move.w (a1),d7
    and.w d4,d7
    tst.w d7
    bne.w L_BOBS_02B2C
    adda.l d1,a1
    subq.l #1,d6
    bne.w L_BOBS_02B0C
L_BOBS_02B24:
padding_accept:
    move.l #$00000001,d0
    rts
L_BOBS_02B2C:
padding_reject:
    move.l #$00000000,d0
    rts
L_BOBS_02B34:
copy_bytes:
    move.l d0,d6
    lsr.l #2,d6
    tst.l d6
    beq.w L_BOBS_02B46
L_BOBS_02B3E:
copy_long_loop:
    move.l (a0)+,(a1)+
    subq.l #1,d6
    bne.w L_BOBS_02B3E
L_BOBS_02B46:
copy_tail:
    andi.l #$00000002,d0
    tst.l d0
    beq.w L_BOBS_02B54
    move.w (a0)+,(a1)+
L_BOBS_02B54:
copy_return:
    rts
L_BOBS_02B56:
emit_copy_old:
    movea.l 60(a2),a0
    movea.l 160(a2),a1
    move.l #$0000000A,d6
L_BOBS_02B64:
copy_entry_longs:
    move.l (a0)+,(a1)+
    subq.l #1,d6
    bne.w L_BOBS_02B64
    movea.l 160(a2),a4
    move.l 164(a2),d0
    move.l 156(a2),d1
    sub.l d1,d0
    move.l d0,12(a4)
    movea.l 60(a2),a0
    move.l 16(a0),d5
    move.l 24(a0),d7
    tst.l d7
    beq.w L_BOBS_02BA0
    move.l 164(a2),d0
    add.l d5,d0
    move.l 156(a2),d1
    sub.l d1,d0
    move.l d0,20(a4)
L_BOBS_02BA0:
copied_mask_offset:
    movea.l 60(a2),a0
    move.l 24(a2),d0
    add.l 12(a0),d0
    movea.l d0,a0
    movea.l 164(a2),a1
    movea.l 60(a2),a4
    move.l 16(a4),d0
    add.l 24(a4),d0
    bsr.w L_BOBS_02B34
    movea.l 60(a2),a4
    move.l 16(a4),d0
    add.l 24(a4),d0
    move.l 164(a2),d1
    add.l d0,d1
    move.l d1,164(a2)
    move.l 160(a2),d1
    addi.l #$00000028,d1
    move.l d1,160(a2)
    rts
L_BOBS_02BE8:
emit_new_entry:
p1b_join_disp:
    movea.l 160(a2),a4
    move.l (a2),d0
    move.w d0,(a4)
    move.l 100(a2),d0
    move.w d0,2(a4)
    move.l 104(a2),d0
    move.w d0,4(a4)
    move.l 108(a2),d0
    move.w d0,6(a4)
    move.l 112(a2),d0
    move.w d0,8(a4)
    move.w #$0000,10(a4)
    move.l 164(a2),d0
    move.l 156(a2),d1
    sub.l d1,d0
    move.l d0,12(a4)
    move.l 120(a2),d0
    move.l d0,16(a4)
    move.l #$00000000,20(a4)
    move.l #$00000000,24(a4)
    move.l #$00000000,32(a4)
    move.l #$00000000,36(a4)
    move.w #$0000,28(a4)
    move.w #$0000,30(a4)
    move.l 132(a2),d0
    addi.l #$00000008,d0
    move.l d0,180(a2)
    move.l 164(a2),d0
    move.l d0,188(a2)
    move.l 108(a2),d0
    move.l d0,200(a2)
L_BOBS_02C76:
capture_plane:
    movea.l 180(a2),a4
    move.l (a4)+,d0
    move.l d0,184(a2)
    move.l a4,180(a2)
    move.l 188(a2),d0
    move.l d0,196(a2)
    move.l 148(a2),d0
    move.l d0,192(a2)
    move.l 104(a2),d0
    move.l d0,204(a2)
L_BOBS_02C9C:
capture_row:
    move.l 184(a2),d0
    move.l 192(a2),d1
    add.l d1,d0
    movea.l d0,a0
    movea.l 196(a2),a1
    move.l 152(a2),d1
    move.l 100(a2),d7
L_BOBS_02CB4:
capture_word:
    move.l #$00000010,d3
    cmpi.l #$00000010,d7
    bcc.w L_BOBS_02CC6
    move.l d7,d3
L_BOBS_02CC6:
group_width_ready:
    bfextu (a0){d1:d3},d4
    bfins d4,(a1){0:d3}
    addq.l #2,a0
    addq.l #2,a1
    sub.l d3,d7
    bne.w L_BOBS_02CB4
    move.l 192(a2),d0
    move.l 136(a2),d1
    add.l d1,d0
    move.l d0,192(a2)
    move.l 196(a2),d0
    move.l 112(a2),d1
    add.l d1,d0
    move.l d0,196(a2)
    move.l 204(a2),d0
    subq.l #1,d0
    move.l d0,204(a2)
    bne.w L_BOBS_02C9C
    move.l 188(a2),d0
    move.l 116(a2),d1
    add.l d1,d0
    move.l d0,188(a2)
    move.l 200(a2),d0
    subq.l #1,d0
    move.l d0,200(a2)
    bne.w L_BOBS_02C76
    move.l 164(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    move.l d0,164(a2)
    move.l 160(a2),d0
    addi.l #$00000028,d0
    move.l d0,160(a2)
    move.l #$00000001,168(a2)
    rts
ENTRY_BOBS_02D44:
mask_make_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$00000001,d0
    bra.w L_BOBS_02D5C
ENTRY_BOBS_02D52:
mask_no_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    move.l #$00000000,d0
L_BOBS_02D5C:
m_start:
    lea -256(a7),a7
    movea.l a7,a2
    move.l d0,(a2)
    move.l #$00000000,88(a2)
    move.l #$00000000,140(a2)
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_02D8A
    move.l d3,8(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    bra.w L_BOBS_02D96
L_BOBS_02D8A:
m_args_no:
    move.l d3,4(a2)
    move.l #$00000000,8(a2)
L_BOBS_02D96:
m_args_done:
    move.l #$00000000,d3
    movea.l $0004.w,a0
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_03598
    move.w 296(a0),d0
    btst #1,d0
    beq.w L_BOBS_03598
    move.l 4(a2),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03598
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03598
    lea L_BOBS_020A2(pc),a0
    move.l (a0),d0
    cmpi.l #$00000005,d0
    bcs.w L_BOBS_03598
    cmpi.l #$0000FFFF,d0
    bhi.w L_BOBS_03598
    move.l d0,12(a2)
    move.l 4(a0),d0
    tst.l d0
    beq.w L_BOBS_03598
    move.l d0,16(a2)
    move.l 8(a0),d0
    tst.l d0
    beq.w L_BOBS_03598
    move.l d0,20(a2)
    move.l 1514(a5),d0
    move.l 20(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l 12(a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    move.l 16(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l 16(a2),d0
    cmpi.l #$00000018,d0
    bls.w L_BOBS_03598
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_BOBS_03598
    movea.l d0,a4
    move.l -20(a4),d0
    cmpi.l #$00000030,d0
    bcs.w L_BOBS_03598
    cmpi.l #$01000010,d0
    bhi.w L_BOBS_03598
    subi.l #$00000010,d0
    move.l d0,24(a2)
    movea.l 16(a2),a4
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_03598
    move.l 16(a2),d0
    move.l 24(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_03598
    movea.l 16(a2),a4
    move.l -16(a4),d0
    move.l 12(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l #$00000000,d0
    move.w -12(a4),d0
    tst.l d0
    beq.w L_BOBS_02ECA
    andi.w #$FFFD,d0
    cmpi.w #$0001,d0
    bne.w L_BOBS_03598
L_BOBS_02ECA:
m_flags_ok:
    move.l -8(a4),d0
    cmpi.l #$41474142,d0
    bne.w L_BOBS_03598
    move.l -4(a4),d0
    cmpi.l #$4F425320,d0
    bne.w L_BOBS_03598
    move.l (a4),d0
    cmpi.l #$4147424F,d0
    bne.w L_BOBS_03598
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_03598
    tst.w 6(a4)
    bne.w L_BOBS_03598
    move.l #$00000000,d0
    move.w 8(a4),d0
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03598
    move.l d0,28(a2)
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000028,d0
    bne.w L_BOBS_03598
    move.l 12(a4),d0
    cmpi.l #$00000020,d0
    bne.w L_BOBS_03598
    move.l 28(a2),d0
    mulu.w #$0028,d0
    addi.l #$00000020,d0
    cmp.l 16(a4),d0
    bne.w L_BOBS_03598
    move.l 24(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_03598
    move.l d0,32(a2)
    move.l 20(a4),d0
    move.l 24(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l 24(a4),d0
    tst.l d0
    beq.w L_BOBS_03598
    move.l d0,36(a2)
    tst.l 28(a4)
    bne.w L_BOBS_03598
    move.l 32(a2),d0
    move.l d0,40(a2)
    move.l 16(a2),d0
    addi.l #$00000020,d0
    move.l d0,44(a2)
    move.l #$00000000,48(a2)
    move.l #$00000000,52(a2)
    move.l #$00000000,56(a2)
    move.l #$00000000,64(a2)
L_BOBS_02FC6:
m_check_entry:
    move.l 48(a2),d0
    move.l 28(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_03270
    movea.l 44(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l 52(a2),d1
    cmp.l d1,d0
    bls.w L_BOBS_03598
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03598
    move.l d0,52(a2)
    move.l #$00000000,d0
    move.w 2(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03598
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03598
    move.l d0,100(a2)
    move.l #$00000000,d0
    move.w 4(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03598
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03598
    move.l d0,104(a2)
    move.l #$00000000,d0
    move.w 6(a4),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03598
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_03598
    move.l d0,108(a2)
    move.l 100(a2),d0
    move.l 104(a2),d1
    mulu.w d1,d0
    cmpi.l #$00400000,d0
    bhi.w L_BOBS_03598
    move.l 100(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    movea.l 44(a2),a4
    move.l #$00000000,d1
    move.w 8(a4),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l d0,112(a2)
    move.l 112(a2),d0
    move.l 104(a2),d1
    mulu.w d1,d0
    move.l d0,116(a2)
    move.l d0,d6
    move.l 108(a2),d5
    move.l #$00000000,d7
L_BOBS_030B2:
m_sum_planes:
    add.l d6,d7
    bcs.w L_BOBS_03598
    subq.l #1,d5
    bne.w L_BOBS_030B2
    movea.l 44(a2),a4
    move.l 16(a4),d0
    cmp.l d7,d0
    bne.w L_BOBS_03598
    move.l d0,120(a2)
    move.l 40(a2),d0
    cmp.l 12(a4),d0
    bne.w L_BOBS_03598
    move.l #$00000000,d0
    move.w 10(a4),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_03120
    move.l 116(a2),d1
    move.l 24(a4),d0
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l 40(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    cmp.l 20(a4),d0
    bne.w L_BOBS_03598
    move.l 116(a2),d0
    move.l d0,124(a2)
    bra.w L_BOBS_0313E
L_BOBS_03120:
m_unmasked:
    tst.l d0
    bne.w L_BOBS_03598
    tst.l 20(a4)
    bne.w L_BOBS_03598
    tst.l 24(a4)
    bne.w L_BOBS_03598
    move.l #$00000000,124(a2)
L_BOBS_0313E:
m_mask_checked:
    move.l 40(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 124(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 24(a2),d1
    cmp.l d1,d0
    bhi.w L_BOBS_03598
    move.l d0,40(a2)
    movea.l 44(a2),a4
    tst.l 32(a4)
    bne.w L_BOBS_03598
    tst.l 36(a4)
    bne.w L_BOBS_03598
    move.l 16(a2),d0
    movea.l 44(a2),a4
    add.l 12(a4),d0
    bcs.w L_BOBS_03598
    movea.l d0,a0
    move.l 100(a2),d0
    move.l 112(a2),d1
    move.l 104(a2),d2
    move.l 108(a2),d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_03598
    move.l 124(a2),d0
    tst.l d0
    beq.w L_BOBS_031DC
    move.l 16(a2),d0
    movea.l 44(a2),a4
    add.l 20(a4),d0
    bcs.w L_BOBS_03598
    movea.l d0,a0
    move.l 100(a2),d0
    move.l 112(a2),d1
    move.l 104(a2),d2
    move.l #$00000001,d3
    bsr.w L_BOBS_02AE8
    tst.l d0
    beq.w L_BOBS_03598
L_BOBS_031DC:
m_padding_ok:
    movea.l 44(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03254
    move.l #$00000001,56(a2)
    move.l 100(a2),d0
    move.l d0,68(a2)
    move.l 104(a2),d0
    move.l d0,72(a2)
    move.l 108(a2),d0
    move.l d0,76(a2)
    move.l 112(a2),d0
    move.l d0,80(a2)
    move.l 116(a2),d0
    move.l d0,60(a2)
    move.l 124(a2),d0
    move.l d0,64(a2)
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_03254
    move.l 8(a2),d7
    tst.l d7
    bmi.w L_BOBS_03598
    move.l #$00000001,d0
    move.l 108(a2),d1
L_BOBS_03246:
m_colour_shift:
    lsl.l #1,d0
    subq.l #1,d1
    bne.w L_BOBS_03246
    cmp.l d0,d7
    bcc.w L_BOBS_03598
L_BOBS_03254:
m_not_target:
    move.l 44(a2),d0
    addi.l #$00000028,d0
    move.l d0,44(a2)
    move.l 48(a2),d0
    addq.l #1,d0
    move.l d0,48(a2)
    bra.w L_BOBS_02FC6
L_BOBS_03270:
m_all_valid:
    move.l 40(a2),d0
    move.l 24(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    move.l 56(a2),d0
    tst.l d0
    beq.w L_BOBS_03598
    move.l (a2),d0
    tst.l d0
    bne.w L_BOBS_032A6
    move.l 64(a2),d0
    tst.l d0
    bne.w L_BOBS_032A6
    move.l #$00000001,140(a2)
    bra.w L_BOBS_03598
L_BOBS_032A6:
m_mutate:
    move.l 36(a2),d0
    cmpi.l #$FFFFFFFF,d0
    beq.w L_BOBS_03598
    move.l 24(a2),d0
    move.l 64(a2),d1
    move.l (a2),d2
    tst.l d2
    beq.w L_BOBS_032D8
    tst.l d1
    bne.w L_BOBS_032DE
    move.l 60(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    bra.w L_BOBS_032DE
L_BOBS_032D8:
m_remove_size:
    sub.l d1,d0
    bmi.w L_BOBS_03598
L_BOBS_032DE:
m_size_ok:
    cmpi.l #$01000000,d0
    bhi.w L_BOBS_03598
    move.l d0,84(a2)
    move.l #$00000000,d1
    move.l #$00010001,d1
    movea.l $0004.w,a6
    jsr -684(a6)
    tst.l d0
    beq.w L_BOBS_03598
    move.l d0,88(a2)
    movea.l 16(a2),a0
    movea.l 88(a2),a1
    move.l #$00000020,d0
    bsr.w L_BOBS_02B34
    movea.l 88(a2),a4
    move.l 84(a2),d0
    move.l d0,20(a4)
    move.l 36(a2),d0
    addq.l #1,d0
    move.l d0,24(a4)
    move.l 32(a2),d0
    move.l d0,40(a2)
    move.l 16(a2),d0
    addi.l #$00000020,d0
    move.l d0,44(a2)
    move.l 88(a2),d0
    addi.l #$00000020,d0
    move.l d0,92(a2)
    move.l 88(a2),d0
    move.l 32(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l d0,96(a2)
    move.l #$00000000,48(a2)
L_BOBS_03370:
m_build_loop:
    move.l 48(a2),d0
    move.l 28(a2),d1
    cmp.l d1,d0
    bge.w L_BOBS_03544
    movea.l 44(a2),a0
    movea.l 92(a2),a1
    move.l #$00000028,d0
    bsr.w L_BOBS_02B34
    movea.l 92(a2),a4
    move.l 96(a2),d0
    move.l 88(a2),d1
    sub.l d1,d0
    move.l d0,12(a4)
    movea.l 44(a2),a4
    move.l 16(a4),d0
    move.l d0,120(a2)
    move.l 24(a4),d0
    move.l d0,124(a2)
    move.l 16(a2),d0
    move.l 40(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l d0,136(a2)
    movea.l 136(a2),a0
    movea.l 96(a2),a1
    move.l 120(a2),d0
    bsr.w L_BOBS_02B34
    movea.l 44(a2),a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l 4(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03480
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_0345A
    movea.l 92(a2),a4
    move.w #$0001,10(a4)
    move.l 60(a2),d0
    move.l d0,132(a2)
    move.l d0,24(a4)
    move.l 96(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 88(a2),d1
    sub.l d1,d0
    move.l d0,20(a4)
    movea.l 96(a2),a0
    move.l 96(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    movea.l d0,a1
    move.l 68(a2),d0
    move.l 72(a2),d1
    move.l 76(a2),d2
    move.l 8(a2),d3
    move.l 80(a2),d4
    bsr.w L_BOBS_035BC
    tst.l d3
    beq.w L_BOBS_03598
    bra.w L_BOBS_034E2
L_BOBS_0345A:
m_remove_entry_mask:
    movea.l 92(a2),a4
    move.w #$0000,10(a4)
    move.l #$00000000,20(a4)
    move.l #$00000000,24(a4)
    move.l #$00000000,132(a2)
    bra.w L_BOBS_034E2
L_BOBS_03480:
m_copy_other_mask:
    move.l 124(a2),d0
    move.l d0,132(a2)
    tst.l d0
    beq.w L_BOBS_034D6
    move.l 136(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    movea.l d0,a0
    move.l 96(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    movea.l d0,a1
    move.l 124(a2),d0
    bsr.w L_BOBS_02B34
    movea.l 92(a2),a4
    move.l 96(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 88(a2),d1
    sub.l d1,d0
    move.l d0,20(a4)
    bra.w L_BOBS_034E2
L_BOBS_034D6:
m_other_opaque:
    movea.l 92(a2),a4
    move.l #$00000000,20(a4)
L_BOBS_034E2:
m_advance:
    move.l 96(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 132(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l d0,96(a2)
    move.l 40(a2),d0
    move.l 120(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l 124(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_03598
    move.l d0,40(a2)
    move.l 44(a2),d0
    addi.l #$00000028,d0
    move.l d0,44(a2)
    move.l 92(a2),d0
    addi.l #$00000028,d0
    move.l d0,92(a2)
    move.l 48(a2),d0
    addq.l #1,d0
    move.l d0,48(a2)
    bra.w L_BOBS_03370
L_BOBS_03544:
m_build_complete:
    move.l 96(a2),d0
    move.l 88(a2),d1
    sub.l d1,d0
    move.l 84(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03598
    movea.l 88(a2),a0
    move.l 84(a2),d1
    move.l 12(a2),d3
    bsr.w L_BOBS_01D38
    tst.l d3
    beq.w L_BOBS_03598
    move.l 12(a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    tst.l d0
    beq.w L_BOBS_03598
    lea L_BOBS_020A2(pc),a0
    move.l d0,4(a0)
    move.l 20(a2),d1
    move.l d1,8(a0)
    move.l #$00000001,140(a2)
L_BOBS_03598:
m_done:
m_fail:
    movea.l 88(a2),a1
    move.l a1,d0
    tst.l d0
    beq.w L_BOBS_035AC
    movea.l $0004.w,a6
    jsr -690(a6)
L_BOBS_035AC:
m_no_scratch:
    move.l 140(a2),d3
    lea 256(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_BOBS_035BC:
mask_kernel:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l a0,(a2)
    move.l a1,4(a2)
    move.l d0,8(a2)
    move.l d1,12(a2)
    move.l d2,16(a2)
    move.l d3,20(a2)
    move.l d4,24(a2)
    move.l 8(a2),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03760
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03760
    move.l 12(a2),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03760
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_03760
    move.l 16(a2),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_03760
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_03760
    move.l (a2),d0
    tst.l d0
    beq.w L_BOBS_03760
    andi.l #$00000001,d0
    bne.w L_BOBS_03760
    move.l 4(a2),d0
    tst.l d0
    beq.w L_BOBS_03760
    andi.l #$00000001,d0
    bne.w L_BOBS_03760
    move.l 8(a2),d0
    move.l 12(a2),d1
    mulu.w d1,d0
    cmpi.l #$00400000,d0
    bhi.w L_BOBS_03760
    move.l 8(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l 24(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_03760
    lsr.l #1,d0
    move.l d0,32(a2)
    move.l 24(a2),d0
    move.l 12(a2),d1
    mulu.w d1,d0
    move.l d0,28(a2)
    move.l 20(a2),d1
    tst.l d1
    bmi.w L_BOBS_03760
    move.l #$00000001,d6
    move.l 16(a2),d7
L_BOBS_036A2:
    add.l d6,d6
    subq.l #1,d7
    bne.w L_BOBS_036A2
    cmp.l d6,d1
    bcc.w L_BOBS_03760
    move.l 8(a2),d0
    andi.l #$0000000F,d0
    lsl.l #1,d0
    lea L_BOBS_03772(pc),a4
    adda.l d0,a4
    move.l #$00000000,d0
    move.w (a4),d0
    move.l d0,44(a2)
    move.l 12(a2),d0
    move.l d0,36(a2)
    movea.l (a2),a0
    movea.l 4(a2),a1
L_BOBS_036DC:
    move.l 32(a2),d0
    move.l d0,40(a2)
L_BOBS_036E4:
    movea.l a0,a4
    move.l 28(a2),d4
    move.l 16(a2),d7
    move.l 20(a2),d5
    move.l #$00000000,d6
L_BOBS_036F8:
    move.l #$00000000,d0
    move.w (a4),d0
    bfextu d5{31:1},d1
    tst.l d1
    beq.w L_BOBS_0370E
    eori.w #$FFFF,d0
L_BOBS_0370E:
    or.w d0,d6
    adda.l d4,a4
    lsr.l #1,d5
    subq.l #1,d7
    bne.w L_BOBS_036F8
    move.l 40(a2),d0
    cmpi.l #$00000001,d0
    bne.w L_BOBS_0372E
    move.l 44(a2),d0
    and.w d0,d6
L_BOBS_0372E:
    move.w d6,(a1)+
    addq.l #2,a0
    move.l 40(a2),d0
    subq.l #1,d0
    move.l d0,40(a2)
    bne.w L_BOBS_036E4
    move.l 36(a2),d0
    subq.l #1,d0
    move.l d0,36(a2)
    bne.w L_BOBS_036DC
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    move.l #$00000001,d3
    moveq #0,d2
    rts
L_BOBS_03760:
    lea 96(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    move.l #$00000000,d3
    moveq #0,d2
    rts
