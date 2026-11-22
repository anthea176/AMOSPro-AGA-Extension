; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $07878 source-verified against pinned P2d emitter.
; UNIT142+$07878..$0789E, 38 instructions/data bytes.
UNIT142_BLOCK_07878_EDIT equ 5

ENTRY_UNIT142_07878:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -32(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l a3,4(a2)
    move.l d3,d0
    cmpi.l #UNIT142_BLOCK_07878_EDIT,d0
    bcs.w L_UNIT142_078D0
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_078D0
