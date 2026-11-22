; AGA_NATIVE_MIN_CPU: MC68020
; Source-pinned R83 public AGA callback stub $002B4..$002BE.
UNIT142_R83_STUB_002B4_OFFSET equ 400

ENTRY_UNIT142_R83_STUB_002B4:
    movea.l -4(a5),a0                                  ; +$00000: 206DFFFC
    jsr UNIT142_R83_STUB_002B4_OFFSET(a0)                                        ; +$00004: 4EA80190
    rts                                                ; +$00008: 4E75
