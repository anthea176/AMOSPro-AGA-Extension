; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $099C6 source-verified against pinned P2d emitter.
; UNIT142+$099C6..$09A66, 160 instructions/data bytes.
UNIT142_BLOCK_099C6_EDIT equ 24

    tst.l d0
    beq.w L_UNIT142_09A86
    move.l d0,12(a2)
    cmpi.l #UNIT142_BLOCK_099C6_EDIT,d0
    bls.w L_UNIT142_09A76
    move.l d0,d1
    andi.l #$00000001,d1
    bne.w L_UNIT142_09A76
    move.l 12(a2),d0
    move.l 8(a2),d1
    add.l d1,d0
    bcs.w L_UNIT142_09A76
    subq.l #1,d0
    move.l d0,16(a2)
    move.l 12(a2),d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    beq.w L_UNIT142_09A76
    move.l 16(a2),d0
    movea.l d0,a1
    movea.l $0004.w,a6
    jsr -534(a6)
    andi.l #$00000002,d0
    beq.w L_UNIT142_09A76
    movea.l 12(a2),a1
    move.l 8(a2),d0
    move.l d0,(a1)+
    move.l (a2),d0
    move.w d0,(a1)+
    move.w #$0010,(a1)+
    move.w #$0010,(a1)+
    move.w #$0008,(a1)+
    move.l (a2),d6
    move.l #$00000048,d1
    mulu.w d1,d6
L_UNIT142_09A4E:
    move.l #$00000000,(a1)+
    subq.l #1,d6
    bne.w L_UNIT142_09A4E
    move.l (a2),d6
L_UNIT142_09A5C:
    move.b #$00,(a1)+
    subq.l #1,d6
    bne.w L_UNIT142_09A5C
