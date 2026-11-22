; AGA_NATIVE_MIN_CPU: MC68020
; Source-owned UNIT153 AP20 V2 dispatcher from pinned P2d emitter.
; UNIT153+$00000..$00022, 34 executable bytes, ABI unchanged.
UNIT153_DISPATCH_STACK_BYTES equ 4

    subq.l #UNIT153_DISPATCH_STACK_BYTES,a7
    movem.l d0/a0,-(a7)
    movea.l 12(a7),a0
    moveq #0,d0
    move.w (a0)+,d0
    move.l a0,12(a7)
    lea ENTRY_UNIT153_00022(pc),a0
    adda.l d0,a0
    move.l a0,8(a7)
    movem.l (a7)+,d0/a0
    rts
