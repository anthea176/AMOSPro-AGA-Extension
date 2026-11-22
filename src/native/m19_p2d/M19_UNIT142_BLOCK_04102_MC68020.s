; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 stack epilogue tst $04102 source-verified against pinned P2d emitter.
; UNIT142+$04102..$0410A, 8 instructions/data bytes.
UNIT142_BLOCK_04102_EDIT equ 0

L_UNIT142_04102:
    movem.l (a7)+,d1-d7/a0-a4/a6
    ifne UNIT142_BLOCK_04102_EDIT
        tst.w d0
    else
        tst.l d0
    endif
    rts
L_UNIT142_0410A:
