; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0781C source-verified against pinned P2d emitter.
; UNIT142+$0781C..$07874, 88 instructions/data bytes.
UNIT142_BLOCK_0781C_EDIT equ 0

    move.l a0,d0
    tst.l d0
    beq.w L_UNIT142_0785E
    move.l a0,32(a2)
    move.l -20(a0),d1
    cmpi.l #$00000010,d1
    bcs.w L_UNIT142_0785E
    subi.l #$00000010,d1
    move.l d1,28(a2)
    move.l 4(a2),d0
    move.l d0,20(a2)
    move.l 8(a2),d0
    move.l d0,24(a2)
    move.l (a2),d3
    lea 20(a2),a3
    bsr.w ENTRY_UNIT142_06678
    bra.w L_UNIT142_07864
L_UNIT142_0785E:
    move.l #$00000000,d3
L_UNIT142_07864:
    movea.l 16(a2),a3
    lea 48(a7),a7
    movem.l (a7)+,d0-d2/d4-d7/a0-a2/a4-a6
    moveq #UNIT142_BLOCK_0781C_EDIT,d2
    rts
