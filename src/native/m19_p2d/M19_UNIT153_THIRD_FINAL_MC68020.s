; AGA_NATIVE_MIN_CPU: MC68020
; P2d UNIT153 third result/loop tail source-verified against emitter.
; UNIT153+$0151A..$015B2 (152 code bytes), trailing GetP preserved.
UNIT153_THIRD_FINAL_ZERO equ 0

    move.l 120(a2),d0
    addq.l #1,d0
    move.l d0,120(a2)
    move.l 116(a2),d0
    addi.l #$00000140,d0
    move.l d0,116(a2)
    dbra d7,L_UNIT153_014B0
    move.l #$00000001,d3
    bra.w L_UNIT153_01546
L_UNIT153_01540:
    move.l #UNIT153_THIRD_FINAL_ZERO,d3
L_UNIT153_01546:
    lea 192(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_UNIT153_01552:
    move.l #$00000000,d0
L_UNIT153_01558:
    tst.l d4
    beq.w L_UNIT153_0157C
    btst #0,d4
    beq.w L_UNIT153_0156C
    add.l d5,d0
    bcs.w L_UNIT153_01584
L_UNIT153_0156C:
    lsr.l #1,d4
    beq.w L_UNIT153_0157C
    lsl.l #1,d5
    bcs.w L_UNIT153_01584
    bra.w L_UNIT153_01558
L_UNIT153_0157C:
    move.l #$00000001,d1
    rts
L_UNIT153_01584:
    move.l #$00000000,d1
    rts
L_UNIT153_0158C:
    move.l 100(a2),d5
    move.l 104(a2),d2
    move.l 4(a2),d1
L_UNIT153_01598:
    move.b (a0),(a1)
    addq.l #1,a1
    adda.l d5,a0
    add.l d2,d4
    cmp.l d1,d4
    bcs.w L_UNIT153_015AA
    sub.l d1,d4
    addq.l #1,a0
L_UNIT153_015AA:
    dbra d6,L_UNIT153_01598
    bra.w L_UNIT153_0151A
