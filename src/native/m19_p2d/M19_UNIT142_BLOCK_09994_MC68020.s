; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 field bridge offset source-verified against pinned P2d emitter.
; UNIT142+$09994..$099A0, 12 instructions/data bytes.
UNIT142_BLOCK_09994_EDIT equ 4

    move.l a0,d0
    tst.l d0
    bne.w L_UNIT142_09A86
    move.l UNIT142_BLOCK_09994_EDIT(a2),d0
