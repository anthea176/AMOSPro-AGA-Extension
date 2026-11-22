; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 source-verified clean block $0AB96 source-verified against pinned P2d emitter.
; UNIT142+$0AB96..$0ABAE, 24 instructions/data bytes.
UNIT142_BLOCK_0AB96_EDIT equ 1

    move.l #UNIT142_BLOCK_0AB96_EDIT,d3
    bra.w L_UNIT142_0ABBA
L_UNIT142_0ABA0:
    move.l 72(a2),d0
    tst.l d0
    beq.w L_UNIT142_0ABB4
    move.l 20(a2),d0
