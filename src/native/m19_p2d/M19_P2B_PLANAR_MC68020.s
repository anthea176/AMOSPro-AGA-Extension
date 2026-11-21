; AGA_NATIVE_MIN_CPU: MC68020
; P2b planar H/V/HV 16-bit word-orientation engine and Chip allocation.
; Authoritative original: tools/m19_p2b_planar_orientation020_emit.py.
; This is hand-maintained source, NOT machine-code extraction.
; Relative block in P2d BOBS: $0A28E..$0A4BF, exactly 562 bytes.
; Included inside the sole BOBS unit. ABI: D3=1/0, D2=0.
; All public Bob ownership/source checks belong to the parent P2b bridge.

P2B_FRAME_HEIGHT       equ 0
P2B_FRAME_PLANES       equ 4
P2B_FRAME_PLANE_BYTES  equ 8
P2B_FRAME_ROW_STEP     equ 12
P2B_FRAME_PADDING      equ 16
P2B_FRAME_BYTES        equ 20
P2B_MAX_SIDE           equ 4096
P2B_MAX_PIXELS         equ 4194304
P2B_MAX_PLANES         equ 9
P2B_EXEC_ALLOC_MEM     equ -198
P2B_EXEC_FREE_MEM      equ -210
P2B_EXEC_TYPE_OF_MEM   equ -534
P2B_MEMF_CHIP          equ 2

p2b_planar_orientation_entry:
    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    lea -P2B_FRAME_BYTES(a7),a7
    move.l d1,(a7)  ; HEIGHT offset 0, avoid 16-bit displacement
    move.l d4,P2B_FRAME_PLANES(a7)
    bsr.w p2b_planar_measure
    tst.l d3
    beq.w p2b_planar_invalid
    cmp.l d6,d3
    bhi.w p2b_planar_invalid
    cmp.l d7,d3
    bhi.w p2b_planar_invalid

    move.l d2,d4
    lsl.l #3,d4
    sub.l d0,d4
    move.l d4,P2B_FRAME_PADDING(a7)
    move.l d2,d4
    mulu.w d1,d4
    move.l d4,P2B_FRAME_PLANE_BYTES(a7)

    move.l a0,d0
    tst.l d0
    beq.w p2b_planar_invalid
    btst #0,d0
    bne.w p2b_planar_invalid
    move.l a1,d1
    tst.l d1
    beq.w p2b_planar_invalid
    btst #0,d1
    bne.w p2b_planar_invalid
    move.l d0,d6
    add.l d3,d6
    bcs.w p2b_planar_invalid
    move.l d1,d7
    add.l d3,d7
    bcs.w p2b_planar_invalid
    cmp.l d1,d6
    bls.w p2b_planar_disjoint
    cmp.l d0,d7
    bhi.w p2b_planar_invalid

p2b_planar_disjoint:
    move.l d2,d6
    move.l d2,d0
    btst #1,d5
    beq.w p2b_planar_save_step
    neg.l d0
p2b_planar_save_step:
    move.l d0,P2B_FRAME_ROW_STEP(a7)
    move.l P2B_FRAME_PADDING(a7),d4

p2b_planar_plane:
    move.l (a7),d7  ; HEIGHT offset 0, 2-byte addressing mode
    movea.l a0,a2
    btst #1,d5
    beq.w p2b_planar_row
    move.l P2B_FRAME_PLANE_BYTES(a7),d0
    sub.l d6,d0
    adda.l d0,a2
p2b_planar_row:
    movea.l a2,a3
    move.l d6,d2
    lsr.l #1,d2
    btst #0,d5
    bne.w p2b_planar_reverse_row
p2b_planar_copy_word:
    move.w (a3)+,(a1)+
    subq.l #1,d2
    bne.w p2b_planar_copy_word
    bra.w p2b_planar_next_row

p2b_planar_reverse_row:
    adda.l d6,a3
    bsr.w p2b_planar_reverse_source_word
    move.l d0,d3
p2b_planar_reverse_word:
    subq.l #1,d2
    beq.w p2b_planar_zero_tail
    bsr.w p2b_planar_reverse_source_word
    bra.w p2b_planar_store_reversed
p2b_planar_zero_tail:
    move.w #0,d0
p2b_planar_store_reversed:
    move.l d3,d1
    swap d1
    or.w d0,d1
    lsl.l d4,d1
    swap d1
    move.w d1,(a1)+
    move.l d0,d3
    tst.l d2
    bne.w p2b_planar_reverse_word

p2b_planar_next_row:
    subq.l #1,d7
    beq.w p2b_planar_next_plane
    move.l P2B_FRAME_ROW_STEP(a7),d0
    adda.l d0,a2
    bra.w p2b_planar_row
p2b_planar_next_plane:
    move.l P2B_FRAME_PLANE_BYTES(a7),d0
    adda.l d0,a0
    subq.l #1,P2B_FRAME_PLANES(a7)
    bne.w p2b_planar_plane

    moveq #1,d3
    bra.w p2b_planar_return
p2b_planar_invalid:
    moveq #0,d3
p2b_planar_return:
    lea P2B_FRAME_BYTES(a7),a7
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    moveq #0,d2
    rts

p2b_planar_reverse_source_word:
    moveq #0,d0
    move.w -(a3),d0
    move.l d0,d1
    lsr.l #1,d1
    andi.w #$5555,d1
    andi.w #$5555,d0
    lsl.l #1,d0
    or.w d1,d0
    move.l d0,d1
    lsr.l #2,d1
    andi.w #$3333,d1
    andi.w #$3333,d0
    lsl.l #2,d0
    or.w d1,d0
    move.l d0,d1
    lsr.l #4,d1
    andi.w #$0F0F,d1
    andi.w #$0F0F,d0
    lsl.l #4,d0
    or.w d1,d0
    rol.w #8,d0
    rts

p2b_planar_measure:
    tst.l d0
    beq.w p2b_planar_measure_invalid
    cmpi.l #P2B_MAX_SIDE,d0
    bhi.w p2b_planar_measure_invalid
    tst.l d1
    beq.w p2b_planar_measure_invalid
    cmpi.l #P2B_MAX_SIDE,d1
    bhi.w p2b_planar_measure_invalid
    tst.l d4
    beq.w p2b_planar_measure_invalid
    cmpi.l #P2B_MAX_PLANES,d4
    bhi.w p2b_planar_measure_invalid
    cmpi.l #3,d5
    bhi.w p2b_planar_measure_invalid
    move.l d0,d2
    mulu.w d1,d2
    cmpi.l #P2B_MAX_PIXELS,d2
    bhi.w p2b_planar_measure_invalid

    move.l d0,d2
    addi.l #15,d2
    lsr.l #4,d2
    lsl.l #1,d2
    move.l d2,d3
    mulu.w d1,d3
    mulu.l d4,d3
    rts
p2b_planar_measure_invalid:
    moveq #0,d3
    rts

p2b_planar_chip_prepare_entry:
    movem.l d0-d1/d4-d6/a0/a2-a6,-(a7)
    bsr.w p2b_planar_measure
    tst.l d3
    beq.w p2b_planar_chip_fail
    cmp.l d6,d3
    bhi.w p2b_planar_chip_fail
    movea.l a0,a2
    movea.l d0,a3
    movea.l d1,a4
    move.l d3,d7
    move.l d7,d0
    move.l #P2B_MEMF_CHIP,d1
    jsr P2B_EXEC_ALLOC_MEM(a6)
    tst.l d0
    beq.w p2b_planar_chip_fail
    movea.l d0,a5

    movea.l a5,a1
    jsr P2B_EXEC_TYPE_OF_MEM(a6)
    btst #1,d0
    beq.w p2b_planar_chip_free
    move.l a5,d0
    add.l d7,d0
    bcs.w p2b_planar_chip_free
    subq.l #1,d0
    movea.l d0,a1
    jsr P2B_EXEC_TYPE_OF_MEM(a6)
    btst #1,d0
    beq.w p2b_planar_chip_free

    movea.l a2,a0
    movea.l a5,a1
    move.l a3,d0
    move.l a4,d1
    bsr.w p2b_planar_orientation_entry
    tst.l d3
    bne.w p2b_planar_chip_return
p2b_planar_chip_free:
    move.l d7,d0
    movea.l a5,a1
    jsr P2B_EXEC_FREE_MEM(a6)
p2b_planar_chip_fail:
    movea.l #0,a1
    moveq #0,d7
    moveq #0,d3
p2b_planar_chip_return:
    movem.l (a7)+,d0-d1/d4-d6/a0/a2-a6
    moveq #0,d2
    rts
