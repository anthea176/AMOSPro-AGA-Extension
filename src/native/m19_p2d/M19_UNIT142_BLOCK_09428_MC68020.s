; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $09428 source-verified against pinned P2d emitter.
; UNIT142+$09428..$09486, 94 instructions/data bytes.
UNIT142_BLOCK_09428_EDIT equ 0

ENTRY_UNIT142_09428:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -48(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l #UNIT142_BLOCK_09428_EDIT,d3
    move.l (a2),d0
    cmpi.l #$00000004,d0
    bcs.w L_UNIT142_0954C
    cmpi.l #$00001000,d0
    bhi.w L_UNIT142_0954C
    move.l 4(a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_0954C
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0954C
    move.l (a2),d0
    move.l #$00000120,d1
    mulu.w d1,d0
    addi.l #$0000000C,d0
    move.l d0,8(a2)
    move.l 4(a2),d0
