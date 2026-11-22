; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 historical R83 Close/End source-pinned; active P2d bytes unchanged.
; UNIT142+$0005A..$00062 (8 MC68020 instructions).
UNIT142_R83_CLOSE_ENTRY_A5_OFFSET equ 456

ENTRY_LEGACY_CLOSE_CORE_00000:
    movem.l d0-d7/a0-a6,-(a7)                          ; +$00000: 48E7FFFE
    movea.l UNIT142_R83_CLOSE_ENTRY_A5_OFFSET(a5),a2                                 ; +$00004: 246D01C8
