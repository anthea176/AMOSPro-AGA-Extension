; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 return $002B2 source-verified against pinned P2d emitter.
; UNIT142+$002B2..$002B4, 2 instructions/data bytes.
UNIT142_BLOCK_002B2_EDIT equ 0

ENTRY_UNIT142_002B2:
    ifne UNIT142_BLOCK_002B2_EDIT
        nop
    else
        rts
    endif
