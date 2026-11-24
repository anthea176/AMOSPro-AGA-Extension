; AGA_NATIVE_MIN_CPU: MC68020
; L2b linked view of frozen M19_UNIT142_BLOCK_00764_MC68020.s.
; Historical ranges and SHA comments below describe the P2d base.
; UNIT142 source-verified clean block $00764 source-verified against pinned P2d emitter.
; UNIT142+$00764..$007F6, 146 instructions/data bytes.
UNIT142_BLOCK_00764_EDIT equ 0

ENTRY_UNIT142_00764:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    move.l a2,d0
    tst.l d0
    beq.w L_UNIT142_007F0
    tst.l (a2)
    beq.w L_UNIT142_007F0
    include "M19_L2B_PATTERN_ENTRY_MC68020.s"
    move.l 20(a2),d4
    move.l 16(a2),d5
    moveq #UNIT142_BLOCK_00764_EDIT,d6
L_UNIT142_0078A:
    move.l d6,d0
    mulu.w d4,d0
    divu.w d5,d0
    andi.l #$0000FFFF,d0
    move.l d0,d7
    move.l d7,d1
    mulu.w #$00FF,d1
    move.l d4,d0
    subq.l #1,d0
    divu.w d0,d1
    andi.l #$0000FFFF,d1
    move.l #$000000FF,d2
    sub.l d1,d2
    lsl.l #8,d1
    swap d1
    lsl.l #8,d2
    swap d2
    move.l #$30000000,d3
    move.l d7,d0
    lea 44(a4),a0
    jsr -852(a6)
    move.l d7,d0
    lea 84(a4),a1
    jsr -342(a6)
    moveq #0,d0
    move.l d6,d1
    move.l 12(a2),d2
    subq.l #1,d2
    move.l d6,d3
    lea 84(a4),a1
    jsr -306(a6)
    addq.l #1,d6
    cmp.l d5,d6
    bne.w L_UNIT142_0078A
L_UNIT142_007F0:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6
    rts
