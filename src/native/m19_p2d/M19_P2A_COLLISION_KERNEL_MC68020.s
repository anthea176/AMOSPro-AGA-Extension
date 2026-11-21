; AGA_NATIVE_MIN_CPU: MC68020
; P2a private collision rectangle/mask kernel.
; Source authority: tools/m19_p2a_collision020_emit.py::emit_collision020.
; BOBS+$09858..+$09B53 (764 instruction bytes), 40B validated descriptors.
; Caller provides safe source AGBO/Chip ownership, hotspot and screen clip.
p2a_pair_entry:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -64(a7),a7
    movea.l a7,a2
    move.l d0,(a2)
    move.l a0,4(a2)
    move.l a1,8(a2)
    cmpi.l #1,d0
    bhi.w p2a_invalid
    move.l 4(a2),d4
    tst.l d4
    beq.w p2a_invalid
    andi.l #1,d4
    bne.w p2a_invalid
    move.l 8(a2),d4
    tst.l d4
    beq.w p2a_invalid
    andi.l #1,d4
    bne.w p2a_invalid
    ; Revalidate first descriptor
    movea.l 4(a2),a4
    move.l (a4),d4
    cmp.l 8(a4),d4
    bge.w p2a_no_hit
    move.l 4(a4),d4
    cmp.l 12(a4),d4
    bge.w p2a_no_hit
    move.l 24(a4),d4
    cmpi.l #1,d4
    blt.w p2a_invalid
    cmpi.l #4096,d4
    bgt.w p2a_invalid
    move.l 28(a4),d4
    cmpi.l #1,d4
    blt.w p2a_invalid
    cmpi.l #4096,d4
    bgt.w p2a_invalid
    move.l 24(a4),d4
    addi.l #15,d4
    lsr.l #4,d4
    lsl.l #1,d4
    cmp.l 32(a4),d4
    bne.w p2a_invalid
    move.l 36(a4),d4
    andi.l #1,d4
    bne.w p2a_invalid
    move.l (a4),d4
    cmp.l 16(a4),d4
    blt.w p2a_invalid
    move.l 16(a4),d4
    add.l 24(a4),d4
    cmp.l 8(a4),d4
    blt.w p2a_invalid
    move.l 4(a4),d4
    cmp.l 20(a4),d4
    blt.w p2a_invalid
    move.l 20(a4),d4
    add.l 28(a4),d4
    cmp.l 12(a4),d4
    blt.w p2a_invalid
p2a_v0_validated:
    ; Revalidate second descriptor
    movea.l 8(a2),a4
    move.l (a4),d4
    cmp.l 8(a4),d4
    bge.w p2a_no_hit
    move.l 4(a4),d4
    cmp.l 12(a4),d4
    bge.w p2a_no_hit
    move.l 24(a4),d4
    cmpi.l #1,d4
    blt.w p2a_invalid
    cmpi.l #4096,d4
    bgt.w p2a_invalid
    move.l 28(a4),d4
    cmpi.l #1,d4
    blt.w p2a_invalid
    cmpi.l #4096,d4
    bgt.w p2a_invalid
    move.l 24(a4),d4
    addi.l #15,d4
    lsr.l #4,d4
    lsl.l #1,d4
    cmp.l 32(a4),d4
    bne.w p2a_invalid
    move.l 36(a4),d4
    andi.l #1,d4
    bne.w p2a_invalid
    move.l (a4),d4
    cmp.l 16(a4),d4
    blt.w p2a_invalid
    move.l 16(a4),d4
    add.l 24(a4),d4
    cmp.l 8(a4),d4
    blt.w p2a_invalid
    move.l 4(a4),d4
    cmp.l 20(a4),d4
    blt.w p2a_invalid
    move.l 20(a4),d4
    add.l 28(a4),d4
    cmp.l 12(a4),d4
    blt.w p2a_invalid
p2a_v1_validated:
    movea.l 4(a2),a0
    movea.l 8(a2),a1
    move.l (a0),d4
    move.l (a1),d5
    cmp.l d5,d4
    bge.w p2a_keep_left
    move.l d5,d4
p2a_keep_left:
    move.l d4,12(a2)
    movea.l 4(a2),a0
    movea.l 8(a2),a1
    move.l 4(a0),d4
    move.l 4(a1),d5
    cmp.l d5,d4
    bge.w p2a_keep_top
    move.l d5,d4
p2a_keep_top:
    move.l d4,16(a2)
    movea.l 4(a2),a0
    movea.l 8(a2),a1
    move.l 8(a0),d4
    move.l 8(a1),d5
    cmp.l d5,d4
    ble.w p2a_keep_right
    move.l d5,d4
p2a_keep_right:
    move.l d4,20(a2)
    movea.l 4(a2),a0
    movea.l 8(a2),a1
    move.l 12(a0),d4
    move.l 12(a1),d5
    cmp.l d5,d4
    ble.w p2a_keep_bottom
    move.l d5,d4
p2a_keep_bottom:
    move.l d4,24(a2)
    move.l 20(a2),d4
    cmp.l 12(a2),d4
    ble.w p2a_no_hit
    move.l 24(a2),d4
    cmp.l 16(a2),d4
    ble.w p2a_no_hit
    move.l (a2),d4
    tst.l d4
    beq.w p2a_hit
    move.l 16(a2),d4
    move.l d4,32(a2)
p2a_row:
    move.l 12(a2),d4
    move.l d4,28(a2)
p2a_pixel:
    movea.l 4(a2),a4
    move.l 36(a4),d4
    tst.l d4
    beq.w p2a_opaque_0
    move.l 28(a2),d5
    sub.l 16(a4),d5
    move.l 32(a2),d6
    sub.l 20(a4),d6
    move.l 32(a4),d7
    mulu.w d7,d6
    move.l d5,d7
    lsr.l #3,d7
    add.l d7,d6
    movea.l d4,a6
    adda.l d6,a6
    andi.l #7,d5
    move.l #7,d7
    sub.l d5,d7
    btst d7,(a6)
    beq.w p2a_next_pixel
p2a_opaque_0:
    movea.l 8(a2),a4
    move.l 36(a4),d4
    tst.l d4
    beq.w p2a_opaque_1
    move.l 28(a2),d5
    sub.l 16(a4),d5
    move.l 32(a2),d6
    sub.l 20(a4),d6
    move.l 32(a4),d7
    mulu.w d7,d6
    move.l d5,d7
    lsr.l #3,d7
    add.l d7,d6
    movea.l d4,a6
    adda.l d6,a6
    andi.l #7,d5
    move.l #7,d7
    sub.l d5,d7
    btst d7,(a6)
    beq.w p2a_next_pixel
p2a_opaque_1:
    bra.w p2a_hit
p2a_next_pixel:
    move.l 28(a2),d4
    addq.l #1,d4
    move.l d4,28(a2)
    cmp.l 20(a2),d4
    blt.w p2a_pixel
    move.l 32(a2),d4
    addq.l #1,d4
    move.l d4,32(a2)
    cmp.l 24(a2),d4
    blt.w p2a_row
p2a_no_hit:
    move.l #0,d3
    bra.w p2a_return
p2a_hit:
    move.l #1,d3
    bra.w p2a_return
p2a_invalid:
    move.l #-1,d3
p2a_return:
    lea 64(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
