; AGA_NATIVE_MIN_CPU: MC68020
; One existing 4-byte BNE.W changes destination. The Safe-clear fast path
; and every later instruction retain their exact P2d offsets.
    bne.w L2_FirstBindSafe
L2_SelectResume:
