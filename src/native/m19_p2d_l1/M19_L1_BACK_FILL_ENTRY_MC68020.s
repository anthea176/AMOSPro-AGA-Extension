; AGA_NATIVE_MIN_CPU: MC68020
; Replace exactly the six-byte MOVE.L #128,D0 after Back Fill validates
; the selected ScreenBuffer and BitMap. All following addresses stay fixed.
    bra.l L1_BackFillGuard
L1_BackFillResume:
