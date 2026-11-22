; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $077DC source-verified against pinned P2d emitter.
; UNIT142+$077DC..$07816, 58 instructions/data bytes.
UNIT142_BLOCK_077DC_EDIT equ 5

ENTRY_UNIT142_077DC:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -48(a7),a7
    movea.l a7,a2
    move.l d3,(a2)
    move.l (a3)+,d7
    move.l d7,4(a2)
    move.l (a3)+,d7
    move.l d7,8(a2)
    move.l (a3)+,d7
    move.l d7,12(a2)
    move.l a3,16(a2)
    move.l 12(a2),d0
    cmpi.l #UNIT142_BLOCK_077DC_EDIT,d0
    bcs.w L_UNIT142_0785E
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0785E
