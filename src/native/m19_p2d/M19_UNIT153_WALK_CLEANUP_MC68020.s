; AGA_NATIVE_MIN_CPU: MC68020
; Source-verified UNIT153 walk cleanup and result, pinned P2d.
; UNIT153+$00F04..$00F9C (152 code bytes); GetP marker preserved.
UNIT153_WALK_RESULT_ZERO equ 0

    move.l #UNIT153_WALK_RESULT_ZERO,d3
L_UNIT153_00F0A:
    lea 160(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #0,d2
    rts
L_UNIT153_00F16:
    move.l #$00000000,d0
L_UNIT153_00F1C:
    tst.l d4
    beq.w L_UNIT153_00F40
    btst #0,d4
    beq.w L_UNIT153_00F30
    add.l d5,d0
    bcs.w L_UNIT153_00F48
L_UNIT153_00F30:
    lsr.l #1,d4
    beq.w L_UNIT153_00F40
    lsl.l #1,d5
    bcs.w L_UNIT153_00F48
    bra.w L_UNIT153_00F1C
L_UNIT153_00F40:
    move.l #$00000001,d1
    rts
L_UNIT153_00F48:
    move.l #$00000000,d1
    rts
L_UNIT153_00F50:
    move.l 12(a2),d6
    move.l d6,d5
    andi.l #$00000003,d5
    lsr.l #2,d6
    tst.l d6
    beq.w L_UNIT153_00F6C
    subq.l #1,d6
L_UNIT153_00F66:
    move.l (a0)+,(a1)+
    dbra d6,L_UNIT153_00F66
L_UNIT153_00F6C:
    tst.l d5
    beq.w L_UNIT153_00F7A
    subq.l #1,d5
L_UNIT153_00F74:
    move.b (a0)+,(a1)+
    dbra d5,L_UNIT153_00F74
L_UNIT153_00F7A:
    move.l 76(a2),d0
    move.l a0,d1
    add.l d0,d1
    movea.l d1,a0
    move.l 80(a2),d0
    move.l a1,d1
    add.l d0,d1
    movea.l d1,a1
    dbra d7,L_UNIT153_00F50
    move.l #$00000001,d3
    bra.w L_UNIT153_00F0A
