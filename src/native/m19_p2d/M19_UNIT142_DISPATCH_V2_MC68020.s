; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 AP20 V2 dispatcher source-verified against pinned P2d emitter.
; UNIT142+$00000..$00022, 34 instructions/data bytes.
UNIT142_DISPATCH_STACK equ 4

    subq.l #UNIT142_DISPATCH_STACK,a7
    movem.l d0/a0,-(a7)
    movea.l 12(a7),a0
    moveq #0,d0
    move.w (a0)+,d0
    move.l a0,12(a7)
    lea ENTRY_UNIT142_00022(pc),a0
    adda.l d0,a0
    move.l a0,8(a7)
    movem.l (a7)+,d0/a0
    rts
