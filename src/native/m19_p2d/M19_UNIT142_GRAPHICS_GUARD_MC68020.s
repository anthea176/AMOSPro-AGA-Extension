; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 graphics library guard source-verified against pinned P2d emitter.
; UNIT142+$002C2..$0030C, 74 instructions/data bytes.
UNIT142_GRAPHICS_INITIAL_D3 equ 0

    move.l d0,-(a7)
    move.l d1,-(a7)
    move.l a0,-(a7)
    move.l a1,-(a7)
    move.l a6,-(a7)
    moveq #UNIT142_GRAPHICS_INITIAL_D3,d3
    movea.l $0004.w,a6
    btst #1,297(a6)
    beq.s L_UNIT142_002FE
    lea L_UNIT142_0030C(pc),a1
    moveq #39,d0
    jsr -552(a6)
    tst.l d0
    beq.s L_UNIT142_002FE
    movea.l d0,a1
    move.b 236(a1),d1
    andi.b #$0C,d1
    cmpi.b #$0C,d1
    bne.s L_UNIT142_002FA
    moveq #1,d3
L_UNIT142_002FA:
    jsr -414(a6)
L_UNIT142_002FE:
    movea.l (a7)+,a6
    movea.l (a7)+,a1
    movea.l (a7)+,a0
    move.l (a7)+,d1
    move.l (a7)+,d0
    moveq #0,d2
    rts
