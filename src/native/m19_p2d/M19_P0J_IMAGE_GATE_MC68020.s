; AGA_NATIVE_MIN_CPU: MC68020
; Historical owner: tools/m19_p0j_frame_image_preflight_emit.py::emit_image_preflight
; Audited bytes checked against the official M19 P2d library.
; BOBS+$05F30..$06254 (804 bytes).
; AMOS Main symbolic pseudo-ops preserve six-byte ABI.
P0J_IMAGE_GATE_INITIAL_RESULT equ 0

image_frame_preflight_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -160(a7),a7
    movea.l a7,a2
    move.l #P0J_IMAGE_GATE_INITIAL_RESULT,4(a2)
    bsr.w L_BOBS_05BBA
    tst.l d3
    beq.w L_BOBS_06254
    move.l 456(a5),d0
    move.l d0,32(a2)
    move.l #$00000001,(a2)
L_BOBS_05F5A:
img_gate_next:
    move.l (a2),d0
    cmpi.l #$00000040,d0
    bhi.w L_BOBS_0624C
    move.l a2,d0
    addi.l #$00000060,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05A78
    tst.l d3
    beq.w L_BOBS_06242
    move.l a2,d0
    addi.l #$00000060,d0
    movea.l d0,a1
    move.l (a2),d0
    bsr.w L_BOBS_05BAC
    tst.l d3
    beq.w L_BOBS_06254
    move.l 96(a2),d0
    move.l d0,8(a2)
    move.l 100(a2),d0
    move.l d0,12(a2)
    move.l 8(a2),d0
    dc.w $FE11,$F700,AMOS_MAIN_GETADR
    move.l a0,d0
    move.l d0,16(a2)
    cmpi.l #$00000018,d0
    bls.w L_BOBS_06254
    andi.l #$00000001,d0
    bne.w L_BOBS_06254
    movea.l 16(a2),a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06254
    movea.l 16(a2),a0
    move.l #$00000000,d0
    move.w 8(a0),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_06254
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_06254
    move.l d0,20(a2)
    move.l d0,24(a2)
    mulu.w #$0028,d0
    addi.l #$00000020,d0
    move.l d0,36(a2)
    movea.l 16(a2),a0
    move.l 20(a0),d1
    move.l d1,40(a2)
    cmp.l d1,d0
    bhi.w L_BOBS_06254
    move.l 16(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_06254
    subq.l #1,d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    tst.l d0
    beq.w L_BOBS_06254
    move.l 16(a2),d0
    addi.l #$00000020,d0
    bcs.w L_BOBS_06254
    move.l d0,28(a2)
L_BOBS_06050:
img_gate_scan:
    move.l 24(a2),d0
    tst.l d0
    beq.w L_BOBS_06254
    movea.l 28(a2),a0
    move.l #$00000000,d0
    move.w (a0),d0
    move.l 12(a2),d1
    cmp.l d1,d0
    beq.w L_BOBS_06090
    move.l 28(a2),d0
    addi.l #$00000028,d0
    bcs.w L_BOBS_06254
    move.l d0,28(a2)
    move.l 24(a2),d0
    subq.l #1,d0
    move.l d0,24(a2)
    bra.w L_BOBS_06050
L_BOBS_06090:
img_gate_found:
    movea.l 28(a2),a0
    move.l #$00000000,d0
    move.w 2(a0),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_06254
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_06254
    move.l d0,44(a2)
    movea.l 28(a2),a0
    move.l #$00000000,d0
    move.w 4(a0),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_06254
    cmpi.l #$00001000,d0
    bhi.w L_BOBS_06254
    move.l d0,48(a2)
    movea.l 28(a2),a0
    move.l #$00000000,d0
    move.w 6(a0),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_06254
    cmpi.l #$00000008,d0
    bhi.w L_BOBS_06254
    move.l d0,52(a2)
    movea.l 28(a2),a0
    move.l #$00000000,d0
    move.w 8(a0),d0
    cmpi.l #$00000001,d0
    bcs.w L_BOBS_06254
    cmpi.l #$00000200,d0
    bhi.w L_BOBS_06254
    move.l d0,56(a2)
    movea.l 32(a2),a0
    move.l 28(a0),d1
    move.l 52(a2),d0
    cmp.l d1,d0
    bne.w L_BOBS_06254
    move.l 44(a2),d0
    addi.l #$0000000F,d0
    lsr.l #4,d0
    lsl.l #1,d0
    move.l 56(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06254
    move.l 56(a2),d0
    move.l 48(a2),d1
    mulu.w d1,d0
    move.l d0,60(a2)
    move.l #$00000000,84(a2)
    move.l 52(a2),d7
L_BOBS_0616C:
img_gate_depth_loop:
    move.l 84(a2),d0
    move.l 60(a2),d1
    add.l d1,d0
    bcs.w L_BOBS_06254
    move.l d0,84(a2)
    subq.l #1,d7
    bne.w L_BOBS_0616C
    movea.l 28(a2),a0
    move.l 12(a0),d0
    move.l d0,64(a2)
    move.l 16(a0),d0
    move.l d0,68(a2)
    move.l 20(a0),d0
    move.l d0,72(a2)
    move.l 24(a0),d0
    move.l d0,76(a2)
    move.l #$00000000,d0
    move.w 10(a0),d0
    cmpi.l #$00000001,d0
    bhi.w L_BOBS_06254
    move.l d0,80(a2)
    move.l 68(a2),d0
    move.l 84(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06254
    move.l 64(a2),d0
    move.l 36(a2),d1
    cmp.l d1,d0
    bcs.w L_BOBS_06254
    move.l 40(a2),d1
    move.l 68(a2),d7
    sub.l d7,d1
    bcs.w L_BOBS_06254
    cmp.l d1,d0
    bhi.w L_BOBS_06254
    move.l 80(a2),d0
    tst.l d0
    beq.w L_BOBS_0622E
    move.l 76(a2),d0
    move.l 60(a2),d1
    cmp.l d1,d0
    bne.w L_BOBS_06254
    move.l 72(a2),d0
    move.l 36(a2),d1
    cmp.l d1,d0
    bcs.w L_BOBS_06254
    move.l 40(a2),d1
    move.l 76(a2),d7
    sub.l d7,d1
    bcs.w L_BOBS_06254
    cmp.l d1,d0
    bhi.w L_BOBS_06254
    bra.w L_BOBS_06242
L_BOBS_0622E:
img_gate_no_mask:
    move.l 72(a2),d0
    tst.l d0
    bne.w L_BOBS_06254
    move.l 76(a2),d0
    tst.l d0
    bne.w L_BOBS_06254
L_BOBS_06242:
img_gate_advance:
    move.l (a2),d0
    addq.l #1,d0
    move.l d0,(a2)
    bra.w L_BOBS_05F5A
L_BOBS_0624C:
img_gate_done:
    move.l #$00000001,4(a2)
