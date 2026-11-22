; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $094BE source-verified against pinned P2d emitter.
; UNIT142+$094BE..$0952C, 110 instructions/data bytes.
UNIT142_BLOCK_094BE_EDIT equ 24

    tst.l d0
    beq.w L_UNIT142_0954C
    move.l d0,12(a2)
    cmpi.l #UNIT142_BLOCK_094BE_EDIT,d0
    bls.w L_UNIT142_0953C
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_UNIT142_0953C
    move.l 12(a2),d0
    move.l 8(a2),d1
    add.l d1,d0
    bcs.w L_UNIT142_0953C
    movea.l 12(a2),a1
    move.l 8(a2),d0
    move.l d0,(a1)+
    move.l (a2),d0
    move.w d0,(a1)+
    move.w #$0010,(a1)+
    move.w #$0010,(a1)+
    move.w #$0008,(a1)+
    move.l (a2),d6
    lsl.l #4,d6
L_UNIT142_0950A:
    move.w #$FFFF,(a1)+
    move.l #$00000000,(a1)+
    move.l #$00000000,(a1)+
    move.l #$00000000,(a1)+
    move.l #$00000000,(a1)+
    subq.l #1,d6
    bne.w L_UNIT142_0950A
