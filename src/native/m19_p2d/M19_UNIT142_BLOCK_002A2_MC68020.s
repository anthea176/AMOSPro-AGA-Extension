; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 return $002A2 source-verified against pinned P2d emitter.
; UNIT142+$002A2..$002A4, 2 instructions/data bytes.
UNIT142_BLOCK_002A2_EDIT equ 0

ENTRY_UNIT142_002A2:
    ifne UNIT142_BLOCK_002A2_EDIT
        nop
    else
        rts
    endif
