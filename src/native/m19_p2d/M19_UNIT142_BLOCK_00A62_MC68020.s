; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 OS graphics LVO call source-verified against pinned P2d emitter.
; UNIT142+$00A62..$00A7C, 26 instructions/data bytes.
UNIT142_BLOCK_00A62_EDIT equ -270

ENTRY_UNIT142_00A62:
    movem.l d0-d7/a0-a2/a4-a6,-(a7)
    movea.l 456(a5),a2
    tst.l (a2)
    beq.s L_UNIT142_00A76
    movea.l 8(a2),a6
    jsr UNIT142_BLOCK_00A62_EDIT(a6)
L_UNIT142_00A76:
    movem.l (a7)+,d0-d7/a0-a2/a4-a6
    rts
