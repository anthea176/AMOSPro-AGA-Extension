; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0CEF2 source-verified against pinned P2d emitter.
; UNIT142+$0CEF2..$0CF38, 70 instructions/data bytes.
UNIT142_BLOCK_0CEF2_EDIT equ 1

ENTRY_UNIT142_0CEF2:
    movem.l d0-d2/d4-d7/a0-a2/a4-a6,-(a7)
    lea -96(a7),a7
    movea.l a7,a2
    move.l d3,4(a2)
    move.l (a3)+,d7
    move.l d7,(a2)
    move.l #$FFFFFFFF,d3
    move.l 4(a2),d0
    cmpi.l #UNIT142_BLOCK_0CEF2_EDIT,d0
    bcs.w L_UNIT142_0D320
    cmpi.l #$00000005,d0
    bhi.w L_UNIT142_0D320
    move.l (a2),d0
    cmpi.l #$00000005,d0
    bcs.w L_UNIT142_0D320
    cmpi.l #$0000FFFF,d0
    bhi.w L_UNIT142_0D320
