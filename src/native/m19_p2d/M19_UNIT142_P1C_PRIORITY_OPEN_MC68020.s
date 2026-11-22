; AGA_NATIVE_MIN_CPU: MC68020
; UNIT142 P1c Screen Open priority setup, from source-pinned M19 emitter.
; UNIT142+$0F0A4..$0F0CA, 38 bytes of MC68020 instructions.
UNIT142_P1C_OPEN_OK equ 1

    jsr (UNIT_UNIT142+$470,pc)
    cmpi.l #UNIT142_P1C_OPEN_OK,d3
    bne.w UNIT142_P1C_OPEN_RETURN
    move.l a0,-(a7)
    lea UNIT142_P1C_CONTEXT(pc),a0
    move.l a5,(a0)
    move.l #0,4(a0)
    movea.l (a7)+,a0
UNIT142_P1C_OPEN_RETURN:
    rts
