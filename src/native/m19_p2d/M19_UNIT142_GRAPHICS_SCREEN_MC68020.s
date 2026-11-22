; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 graphics screen preflight source-verified against pinned P2d emitter.
; UNIT142+$00322..$00448, 294 instructions/data bytes.
UNIT142_SCREEN_INITIAL_D3 equ 0

    movem.l d0-d1/d4-d7/a0-a6,-(a7)
    moveq #UNIT142_SCREEN_INITIAL_D3,d3
    movea.l $0004.w,a6
    btst #1,297(a6)
    beq.w L_UNIT142_00440
    lea L_UNIT142_00448(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_00440
    movea.l d0,a4
    movea.l $0004.w,a6
    lea L_UNIT142_0045A(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.w L_UNIT142_00436
    movea.l d0,a5
    move.b 236(a5),d0
    andi.b #$0C,d0
    cmpi.b #$0C,d0
    bne.w L_UNIT142_0042C
    lea -40(a7),a7
    movea.l a7,a1
    move.l #$80000023,(a1)+
    move.l #$00000140,(a1)+
    move.l #$80000024,(a1)+
    move.l #$00000100,(a1)+
    move.l #$80000025,(a1)+
    move.l #$00000008,(a1)+
    move.l #$80000032,(a1)+
    move.l #$00021000,(a1)+
    moveq #0,d0
    move.l d0,(a1)+
    move.l d0,(a1)+
    suba.l a0,a0
    movea.l a7,a1
    movea.l a4,a6
    jsr -612(a6)
    lea 40(a7),a7
    tst.l d0
    beq.w L_UNIT142_0042C
    movea.l d0,a3
    moveq #0,d6
L_UNIT142_003C2:
    move.l d6,d0
    move.l d6,d1
    lsl.l #8,d1
    swap d1
    move.l #$000000FF,d2
    sub.l d6,d2
    lsl.l #8,d2
    swap d2
    move.l #$30000000,d3
    lea 44(a3),a0
    movea.l a5,a6
    jsr -852(a6)
    move.l d6,d0
    lea 84(a3),a1
    jsr -342(a6)
    moveq #0,d0
    move.l d6,d1
    move.l #$0000013F,d2
    move.l d6,d3
    lea 84(a3),a1
    jsr -306(a6)
    addq.l #1,d6
    cmpi.l #$00000100,d6
    bne.w L_UNIT142_003C2
    move.w #$0096,d7
L_UNIT142_00414:
    movea.l a5,a6
    jsr -270(a6)
    dbra d7,L_UNIT142_00414
    movea.l a3,a0
    movea.l a4,a6
    jsr -66(a6)
    moveq #1,d3
    bra.w L_UNIT142_0042C
L_UNIT142_0042C:
    movea.l a5,a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT142_00436:
    movea.l a4,a1
    movea.l $0004.w,a6
    jsr -414(a6)
L_UNIT142_00440:
    movem.l (a7)+,d0-d1/d4-d7/a0-a6
    moveq #0,d2
    rts
