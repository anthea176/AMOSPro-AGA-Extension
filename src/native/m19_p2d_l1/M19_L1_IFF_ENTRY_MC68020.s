; AGA_NATIVE_MIN_CPU: MC68020
; Replace exactly the six bytes loading State and graphics.library
; after IFF's read-only BODY pass and RGB table allocation.
    bra.l L1_IffGuard
L1_IffResume:
